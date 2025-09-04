import asyncio
import csv
import glob
import os
import shutil
import subprocess
import zipfile
from collections import defaultdict
from contextlib import asynccontextmanager
from math import log2

import aiohttp
import aiosu
import numpy as np
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel
from pymilvus import Collection, connections
from scipy.stats import norm, zscore

SKILL_COLUMNS = [
    "Stamina",
    "Streams",
    "Aim",
    "Accuracy",
    "Precision",
    "Reaction",
    "Flashlight",
]
COLUMNS_TO_USE = [
    "BeatmapID",
    "BeatmapsetID",
    "Mods",
    "Title",
    "Version",
] + SKILL_COLUMNS
MOD_PRESETS = {
    "nm": 0,
    "ez": 2,
    "hd": 8,
    "fl": 8,
    "bl": 8,
    "hr": 16,
    "dt": 64,
    "nc": 64,
    "ht": 256,
    "dc": 256,
}
OSU_SKILLS_RS = "./osu_skills_rs_0.0.3_linux-x64"
MOD_PRESETS_SKILLS = {
    "nm": 0,
    "ez": 2,
    "hd": 8,
    "hr": 16,
    "dt": 64,
    "ht": 256,
    "ezhd": 2 + 8,
    "hdhr": 8 + 16,
    "ezdt": 2 + 64,
    "hddt": 8 + 64,
    "hrdt": 16 + 64,
    "ezhddt": 2 + 8 + 64,
    "hdhrdt": 8 + 16 + 64,
    "ezht": 2 + 256,
    "hdht": 8 + 256,
    "hrht": 16 + 256,
    "ezhdht": 2 + 8 + 256,
    "hdhrht": 8 + 16 + 256,
}
ROOT_DIR = "beatmap_downloads"
OUTPUT_DIR = "skills_outputs"
os.makedirs(ROOT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


class BeatmapQuery(BaseModel):
    beatmap_id: int
    mods: int
    top_n: int = 10


class UserRequest(BaseModel):
    user_id: int
    top_n_neighbors: int = 50


search_params = {"metric_type": "L2", "params": {"ef": 64}}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to Milvus
    connections.connect(
        "default",
        host=os.environ.get("MILVUS_HOST", "localhost"),
        port=os.environ.get("MILVUS_PORT", "19530"),
    )
    collection = Collection("osu_beatmap_collection")
    collection.load()

    # Create aiosu client
    aiosu_client = aiosu.v2.Client(
        client_id=int(os.getenv("OSU_CLIENT_ID")),
        client_secret=os.getenv("OSU_CLIENT_SECRET"),
    )

    app.state.collection = collection
    app.state.aiosu_client = aiosu_client

    ingest_task = asyncio.create_task(background_beatmap_ingest(app))

    yield

    # Cleanup
    await aiosu_client.aclose()
    ingest_task.cancel()


app = FastAPI(lifespan=lifespan)


async def background_beatmap_ingest(app):
    while True:
        collection = app.state.collection
        aiosu_client = app.state.aiosu_client
        print("processing new beatmaps")
        await process_new_ranked_maps(collection, aiosu_client)
        await asyncio.sleep(1800)  # 30 minutes


async def download_file(url: str, target_path: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                with open(target_path, "wb") as f:
                    f.write(await resp.read())
                return True
    return False


def extract_osz_files(pack_dir):
    # Extract each .osz file in pack_dir into its own folder (named without .osz)
    for filename in os.listdir(pack_dir):
        if filename.endswith(".osz"):
            osz_path = os.path.join(pack_dir, filename)
            extract_folder = os.path.join(pack_dir, filename[:-4])
            os.makedirs(extract_folder, exist_ok=True)
            with zipfile.ZipFile(osz_path, "r") as zf:
                zf.extractall(extract_folder)


def beatmapset_exists_in_milvus(collection, beatmapsetid):
    results = collection.query(
        expr=f"BeatmapsetID == {beatmapsetid}", output_fields=["BeatmapsetID"]
    )
    return len(results) > 0


def insert_beatmaps_into_milvus(collection):
    csv_files = glob.glob(os.path.join(OUTPUT_DIR, "*.csv"))
    dtype_dict = {
        "BeatmapID": "Int64",  # nullable integer type, preserves NA
        "BeatmapsetID": "Int64",
        "Mods": "Int64",  # use Int64 instead of Int8 for safety
        "Title": "string",
        "Version": "string",
        "Stamina": "float64",
        "Streams": "float64",
        "Aim": "float64",
        "Accuracy": "float64",
        "Precision": "float64",
        "Reaction": "float64",
        "Flashlight": "float64",
    }
    df_list = []
    for file in csv_files:
        df = pd.read_csv(
            file,
            usecols=COLUMNS_TO_USE,
            dtype=dtype_dict,
            engine="python",
            quoting=csv.QUOTE_MINIMAL,
            on_bad_lines="skip",
            escapechar="\\",
        )
        available_cols = [col for col in COLUMNS_TO_USE if col in df.columns]
        df_list.append(df[available_cols])

    combined_df = pd.concat(df_list, ignore_index=True)

    # Create "embedding" column from skill_columns as list of floats for vector
    combined_df["embedding"] = combined_df[SKILL_COLUMNS].values.tolist()

    # Define a dictionary of fixup rules for each column (fillna + convert type)
    fixup_rules = {
        "BeatmapID": ("int64", -1),
        "BeatmapsetID": ("int64", -1),
        "Mods": ("int64", -1),
        "Title": ("string", "Unknown Title"),
        "Version": ("string", "Unknown Version"),
    }

    # Apply fixup all at once
    for col, (dtype, fill_value) in fixup_rules.items():
        combined_df[col] = combined_df[col].fillna(fill_value).astype(dtype)

    # After conversions, filter relevant integer columns for invalid values (e.g. negative)
    for col in ["BeatmapID", "BeatmapsetID", "Mods"]:
        combined_df = combined_df[combined_df[col] >= (0 if col == "Mods" else 1)]

    # 1. Replace NaN/inf/-inf in all relevant float columns
    for col in SKILL_COLUMNS:
        # You may want to choose a default value (here, 0.0)
        combined_df[col] = combined_df[col].replace([np.nan, np.inf, -np.inf], 0.0)

    # 2. Replace NaN/inf/-inf inside the "embedding" column (since it's a list)
    def clean_embedding(vec):
        # Replace any NaN/inf/-inf within the vector with 0.0
        return [float(x) if (pd.notnull(x) and np.isfinite(x)) else 0.0 for x in vec]

    combined_df["embedding"] = combined_df["embedding"].apply(clean_embedding)

    print(combined_df.head())

    # Insert data into Milvus from pandas DataFrame
    collection.insert(combined_df)

    # Flush to make sure data is persisted
    collection.flush()

    # Create HNSW_SQ index on embedding vector field for nearest neighbor search
    index_params = {
        "index_type": "HNSW_SQ",
        "metric_type": "L2",
        "params": {"M": 8, "efConstruction": 32}
    }
    collection.create_index(field_name="embedding", index_params=index_params)

    print(f"Inserted {len(combined_df)} records into Milvus collection collection.")


async def process_new_ranked_maps(collection, aiosu_client):
    packs = await aiosu_client.get_beatmap_packs(
        type=aiosu.models.beatmap.BeatmapPackType.STANDARD
    )

    downloaded = 0

    for pack in packs.beatmap_packs:
        tag = pack.tag

        # Get beatmap pack details
        beatmap_pack = await aiosu_client.get_beatmap_pack(tag)

        print(beatmap_pack.mode)

        if not beatmap_pack.mode == None:
            continue

        # Check if any beatmapset is missing in Milvus
        any_missing = False
        for bmset in beatmap_pack.beatmapsets:
            if not beatmapset_exists_in_milvus(collection, bmset.id):
                any_missing = True
                break
        if not any_missing:
            print(
                f"All beatmapsets in pack {tag} are already in Milvus, skipping download."
            )
            break

        # Download the pack zip
        dl_dir = os.path.join(ROOT_DIR, f"pack_{tag}")
        os.makedirs(dl_dir, exist_ok=True)
        zip_path = os.path.join(dl_dir, f"{tag}.zip")
        print(f"Downloading pack {tag} from {pack.url}...")
        success = await download_file(pack.url, zip_path)
        if not success:
            print(f"Failed to download pack {tag}")
            continue

        # Unzip pack ZIP
        print(f"Extracting pack zip {zip_path}...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dl_dir)

        # Extract each .osz file inside into separate folders
        extract_osz_files(dl_dir)

        downloaded += 1

    if downloaded == 0:
        return

    # Run osu_skills_rs for each mod combination
    for mod_name, mod_val in MOD_PRESETS_SKILLS.items():
        out_csv = os.path.join(OUTPUT_DIR, f"skills_{mod_name}.csv")
        command = [
            OSU_SKILLS_RS,
            f"--in={ROOT_DIR}",
            "--is-dir=SUBDIR",
            "--output-type=file-csv",
            f"--out={out_csv}",
            f"--mods={mod_val}",
            "--alg=default",
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"FAILED for {mod_name}: {e}")

    # Insert embeddings into Milvus using existing function
    insert_beatmaps_into_milvus(collection)

    # Cleanup all downloaded and extracted files
    print("Cleaning up temporary files...")
    shutil.rmtree(ROOT_DIR, ignore_errors=True)
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.makedirs(ROOT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def find_similar_beatmaps_by_id(
    collection: Collection, beatmap_id: int, mod: int, top_n=10
):
    expr = f"(BeatmapID == {beatmap_id}) and (Mods == {mod})"
    res = collection.query(
        expr=expr,
        output_fields=["embedding"]
        + SKILL_COLUMNS
        + ["Title", "Version", "BeatmapID", "Mods", "BeatmapsetID"],
        limit=1,
    )
    if not res:
        return None, None
    query_record = res[0]
    query_vector = query_record["embedding"]
    query_skill_vector = [query_record[skill] for skill in SKILL_COLUMNS]
    query_skill_sum = sum(query_skill_vector)
    search_results = collection.search(
        data=[query_vector],
        anns_field="embedding",
        param=search_params,
        limit=top_n + 1,
        output_fields=["BeatmapID", "BeatmapsetID", "Mods", "Title", "Version"]
        + SKILL_COLUMNS,
    )
    if not search_results or len(search_results[0]) <= 1:
        return None, query_skill_sum
    filtered_hits = [
        hit for hit in search_results[0] if hit.entity["BeatmapID"] != beatmap_id
    ][:top_n]
    rows = []
    for hit in filtered_hits:
        entity = hit.entity
        skill_diff = query_skill_sum - sum(entity[s] for s in SKILL_COLUMNS)
        acc_mult = (query_skill_sum + skill_diff) / query_skill_sum
        row = {
            "BeatmapID": entity["BeatmapID"],
            "BeatmapsetID": entity["BeatmapsetID"],
            "Mods": entity["Mods"],
            "Title": entity["Title"],
            "Version": entity["Version"],
            "Distance": hit.distance,
            "AccMult": acc_mult,
        }
        for skill in SKILL_COLUMNS:
            row[skill] = entity[skill]
        rows.append(row)
    return rows, query_skill_sum


async def get_user_top_scores(client: aiosu.v2.Client, user_id, n_scores=100):
    best_scores = await client.get_user_bests(
        user_id=user_id,
        mode=aiosu.models.gamemode.Gamemode.STANDARD,
        limit=n_scores,
        new_format=True,
    )
    # print(best_scores[:5])
    result = []
    for score in best_scores:
        beatmap = score.beatmap
        mods_short = [m.acronym.lower() for m in (score.mods or [])]
        result.append(
            {
                "beatmap": {"id": beatmap.id if beatmap else None},
                "mods": mods_short,
                "accuracy": score.accuracy,
            }
        )
    return result


from typing import Any, Dict, List

import aiosu


async def get_user_recent_scores(
    client: aiosu.v2.Client, user_id: int, n_scores: int = 50
) -> List[Dict[str, Any]]:
    best_scores = await client.get_user_recents(
        user_id=user_id,
        mode=aiosu.models.gamemode.Gamemode.STANDARD,
        limit=n_scores,
        new_format=True,
    )

    return [
        {
            "beatmap": {"id": score.beatmap.id if score.beatmap else None},
            "mods": [m.acronym.lower() for m in (score.mods or [])],
            "accuracy": score.accuracy,
        }
        for score in best_scores
        if score.beatmap.status == aiosu.models.BeatmapRankStatus.RANKED
    ]


def tally_neighbors(collection: Collection, user_scores: list, top_n_neighbors=50):
    neighbor_info = defaultdict(
        lambda: {
            "distances": [],
            "weights": [],
            "accuracies": [],
            "title": None,
            "version": None,
        }
    )
    max_distance = None
    for idx, score in enumerate(user_scores):
        beatmap_id = score["beatmap"]["id"]
        mod = (
            sum(MOD_PRESETS.get(m.lower(), 0) for m in score["mods"])
            if score["mods"]
            else 0
        )
        user_weight = 1 - (idx / 100)
        user_accuracy = score.get("accuracy", 0)
        neighbor_rows, skill_value = find_similar_beatmaps_by_id(
            collection, beatmap_id, mod, top_n=10
        )
        if neighbor_rows is None or skill_value is None:
            continue
        for row in neighbor_rows:
            key = (row["BeatmapID"], row["BeatmapsetID"], row["Mods"])
            neighbor_info[key]["distances"].append(row["Distance"])
            neighbor_info[key]["weights"].append(user_weight)
            neighbor_info[key]["accuracies"].append(
                np.clip(user_accuracy * row["AccMult"], 0, 1)
            )
            if neighbor_info[key]["title"] is None:
                neighbor_info[key]["title"] = row["Title"]
            if neighbor_info[key]["version"] is None:
                neighbor_info[key]["version"] = row["Version"]
            if max_distance is None or row["Distance"] > max_distance:
                max_distance = row["Distance"]
    epsilon = 1e-6
    summary = []
    for key, val in neighbor_info.items():
        count = len(val["distances"])
        avg_distance = (sum(val["distances"]) / count) / max_distance
        avg_weight = sum(val["weights"]) / count
        avg_accuracy = sum(val["accuracies"]) / count
        summary.append(
            {
                "BeatmapID": key[0],
                "BeatmapsetID": key[1],
                "Mods": key[2],
                "Count": count,
                "AvgDistance": avg_distance,
                "AvgWeight": avg_weight,
                "AvgAccuracy": avg_accuracy,
                "Title": val["title"],
                "Version": val["version"],
            }
        )
    if not summary:
        return []
    distances = norm.pdf(zscore(np.array([entry["AvgDistance"] for entry in summary])))
    for i, entry in enumerate(summary):
        count = entry["Count"]
        avg_distance = entry["AvgDistance"]
        avg_weight = entry["AvgWeight"]
        entry["ZDistance"] = distances[i]
        entry["Score"] = (
            (((0.1 * log2(count + 1)) + 0.9) * ((2 ** (avg_weight**4)) - 1))
            / (avg_distance + epsilon)
            * distances[i]
        )
    summary_sorted = sorted(summary, key=lambda x: -x["Score"])
    return summary_sorted[:top_n_neighbors]


@app.get("/")
async def health():
    return {"status": "ok"}


@app.get("/similar_beatmaps/")
async def api_similar_beatmaps(beatmap_id: int, mods: int, top_n: int = 10):
    rows, skill_sum = find_similar_beatmaps_by_id(
        app.state.collection, beatmap_id, mods, top_n
    )
    if rows is None:
        return {"error": "No such beatmap found"}
    return {"skill_sum": skill_sum, "neighbors": rows}


@app.post("/user_top_neighbors/")
async def api_user_top_neighbors(req: UserRequest):
    try:
        user_scores = await get_user_top_scores(app.state.aiosu_client, req.user_id)
        summary = tally_neighbors(
            app.state.collection,
            user_scores,
            req.top_n_neighbors,
        )
        return {"user_id": req.user_id, "top_neighbors": summary}
    except Exception as e:
        return {"error": str(e)}


@app.post("/user_flow/")
async def api_user_top_neighbors(req: UserRequest):
    try:
        user_scores = await get_user_recent_scores(app.state.aiosu_client, req.user_id)
        summary = tally_neighbors(
            app.state.collection,
            user_scores,
            req.top_n_neighbors,
        )
        return {"user_id": req.user_id, "top_neighbors": summary}
    except Exception as e:
        return {"error": str(e)}
