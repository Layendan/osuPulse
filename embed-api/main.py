import asyncio
import os
import shutil
import struct
import subprocess
from collections import defaultdict
from contextlib import asynccontextmanager
from math import log2
from pathlib import Path
from urllib.parse import unquote

import aiohttp
import aiosu
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import rosu_pp_py as rosu
from embeddings import generate_embeddings_and_insert_into_database
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymilvus import MilvusClient

COLUMNS_TO_USE = [
    "BeatmapId",
    "BeatmapSetId",
    "Mods",
    "Title",
    "Version",
]
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
MAPPERATOR = "./Mapperator.ConsoleAppLinux"
OSU_SKILLS_RS = "./osu_skills_rs_0.1.1_linux-x64"
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
SKILLS_DIR = "skills_outputs"
MAPPERATOR_DIR = "extracted"
DATA_DIR = os.path.join(MAPPERATOR_DIR, "data")
METADATA_FILE = os.path.join(MAPPERATOR_DIR, "metadata.parquet")
DIFFICULTY_FILE = "difficulty.parquet"
ONLINE_CACHE_PATH = "online_cache.jsonl"

COLLECTION_NAME = "osu_beatmap_collection"


class BeatmapQuery(BaseModel):
    beatmap_id: int
    mods: int
    top_n: int = 10
    show_nsfw: bool = True
    min_stars: float | None = None
    max_stars: float | None = None
    min_pp: float | None = None
    max_pp: float | None = None
    min_hit_length: int | None = None
    max_hit_length: int | None = None
    min_bpm: float | None = None
    max_bpm: float | None = None
    exclude_mods_filter: int | None = None
    include_mods_filter: int | None = None


class UserRequest(BaseModel):
    user_id: int
    top_n_neighbors: int = 50
    show_nsfw: bool = True
    min_stars: float | None = None
    max_stars: float | None = None
    min_pp: float | None = None
    max_pp: float | None = None
    min_hit_length: int | None = None
    max_hit_length: int | None = None
    min_bpm: float | None = None
    max_bpm: float | None = None
    exclude_mods_filter: int | None = None
    include_mods_filter: int | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = MilvusClient(os.environ.get("MILVUS_URL", "http://localhost:19530"))
    client.load_collection(collection_name=COLLECTION_NAME)

    aiosu_client = aiosu.v2.Client(
        client_id=int(os.getenv("OSU_CLIENT_ID")),
        client_secret=os.getenv("OSU_CLIENT_SECRET"),
    )

    app.state.milvus_client = client
    app.state.aiosu_client = aiosu_client

    cleanup_dirs()
    ingest_task = asyncio.create_task(background_beatmap_ingest(app))

    yield

    await aiosu_client.aclose()
    client.close()
    ingest_task.cancel()


app = FastAPI(lifespan=lifespan)


async def background_beatmap_ingest(app):
    while True:
        client = app.state.milvus_client
        print("Processing new beatmaps")
        try:
            await process_new_ranked_maps(client)
        except Exception as e:
            print(f"Error processing new beatmaps: {str(e)}")
        finally:
            await asyncio.sleep(1800)  # 30 minutes


async def download_file(url: str, filepath: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if "content-disposition" in response.headers:
                header = response.headers["content-disposition"]
                filename = unquote(header.split("filename=")[1].replace('"', ""))
            else:
                filename = f"{url.split('/')[-1]}.osz"
            path = os.path.join(filepath, filename)
            with open(path, "wb") as file:
                while True:
                    chunk = await response.content.read()
                    if not chunk:
                        break
                    file.write(chunk)
                print(f"Downloaded file {filename}")


def beatmapset_exists_in_milvus(client: MilvusClient, beatmapsetid: int):
    results = client.query(
        collection_name=COLLECTION_NAME,
        filter=f"BeatmapSetId == {beatmapsetid}",
        output_fields=["BeatmapSetId"],
        limit=1,
    )
    return len(results) > 0


def cleanup_dirs():
    shutil.rmtree(ROOT_DIR, ignore_errors=True)
    shutil.rmtree(SKILLS_DIR, ignore_errors=True)
    shutil.rmtree(MAPPERATOR_DIR, ignore_errors=True)
    if os.path.exists(DIFFICULTY_FILE):
        os.remove(DIFFICULTY_FILE)
    if os.path.exists(ONLINE_CACHE_PATH):
        os.remove(ONLINE_CACHE_PATH)

    os.makedirs(ROOT_DIR, exist_ok=True)
    os.makedirs(SKILLS_DIR, exist_ok=True)
    os.makedirs(MAPPERATOR_DIR, exist_ok=True)


async def download_missing_beatmapsets(client: MilvusClient):
    index = 0
    page = 0
    page_size = 50
    async with aiohttp.ClientSession() as session:
        while True:
            params = {
                "m": "osu",
                "s": "ranked,loved",
                "nsfw": "true",
                "sort": "ranked_desc",
                "ps": page_size,
                "p": page,
            }
            async with session.get(
                "https://api.nerinyan.moe/search", params=params
            ) as resp:
                beatmapsets = await resp.json()

            # If no results on this page, stop early
            if not beatmapsets:
                return index

            num_missing = 0
            for beatmapset in beatmapsets:
                if beatmapset["availability"]["download_disabled"]:
                    continue
                if beatmapset_exists_in_milvus(client, beatmapset["id"]):
                    continue

                url = f"https://api.nerinyan.moe/d/{beatmapset['id']}?noBg=true&NoHitsound=true&NoStoryboard=true&noVideo=true"
                await download_file(url, ROOT_DIR)
                index += 1
                num_missing += 1

            if num_missing == 0:
                return index

            page += 1


def calculate_strains():
    columns = [
        "Id",
        "BeatmapSetId",
        "ModeInt",
        "Ranked",
        "BeatmapSetFolder",
        "BeatmapFile",
    ]
    print("Reading metadata parquet file")
    df = pd.read_parquet(METADATA_FILE)
    results = []
    batch_size = 1000
    batch_num = 0
    writer = None  # Will be initialized after the first batch

    for row in df[columns].itertuples():
        if int(row.ModeInt) != 0 or not (int(row.Ranked) == 1 or int(row.Ranked) == 4 or int(row.Ranked) == 2):
            continue

        path = os.path.join(
            DATA_DIR,
            row.BeatmapSetFolder,
            row.BeatmapFile,
        )

        map = rosu.Beatmap(path=path)

        if map.is_suspicious():
            print(f"Skipping suspicious beatmap: {row.Id}")
            continue

        print(f"Processing strain values for beatmap: {row.Id}")

        for _, mod_val in MOD_PRESETS_SKILLS.items():
            diff = rosu.Difficulty(mods=mod_val)
            strains = diff.strains(map)
            performance = diff.performance().calculate(map)

            result = {
                "Id": row.Id,
                "BeatmapSetId": row.BeatmapSetId,
                "Mods": mod_val,
                "AimStrain": strains.aim,
                "AimNoSlidersStrain": strains.aim_no_sliders,
                "SpeedStrain": strains.speed,
                "FlashlightStrain": strains.flashlight,
                "AimStars": performance.difficulty.aim,
                "SpeedStars": performance.difficulty.speed,
                "FlashlightStars": performance.difficulty.flashlight,
                "Stars": performance.difficulty.stars,
                "AimPP": performance.pp_aim,
                "SpeedPP": performance.pp_speed,
                "AccuracyPP": performance.pp_accuracy,
                "FlashlightPP": performance.pp_flashlight,
                "TotalPP": performance.pp,
            }
            results.append(result)

            if len(results) >= batch_size:
                batch_df = pd.DataFrame(results)
                batch_table = pa.Table.from_pandas(batch_df)
                batch_num += 1
                if writer is None:
                    writer = pq.ParquetWriter(DIFFICULTY_FILE, batch_table.schema)
                writer.write_table(batch_table)
                print(f"Writing batch: {batch_num}")
                results.clear()

    # Write any leftovers after the loop
    if results:
        batch_df = pd.DataFrame(results)
        batch_table = pa.Table.from_pandas(batch_df)
        if writer is None:
            writer = pq.ParquetWriter(DIFFICULTY_FILE, batch_table.schema)
        writer.write_table(batch_table)

    if writer is not None:
        writer.close()
        print("Combined parquet saved to", DIFFICULTY_FILE)
    else:
        print("No data to write.")


EOCD_SIGNATURE = b"\x50\x4b\x05\x06"
EOCD_FIXED_SIZE = 22  # bytes before the variable-length comment
MAX_COMMENT = 0xFFFF  # spec limit


def repair_zip(path: Path) -> bool:
    data = path.read_bytes()
    # Search only in the last 64K+EOCD, like zipfile does
    search_start = max(0, len(data) - (MAX_COMMENT + EOCD_FIXED_SIZE))
    pos = data.rfind(EOCD_SIGNATURE, search_start)
    if pos == -1:
        print(f"[SKIP] No EOCD found: {path}")
        return False

    # EOCD layout: 4s H H H H I I H  (total 22 bytes)
    if pos + EOCD_FIXED_SIZE > len(data):
        print(f"[SKIP] EOCD truncated: {path}")
        return False

    # Unpack to get comment length (last field)
    fields = struct.unpack_from("<4sHHHHIIH", data, pos)
    comment_len = fields[-1]

    # End of EOCD including comment
    end_eocd = pos + EOCD_FIXED_SIZE + comment_len
    if end_eocd > len(data):
        # Inconsistent comment length -> probably not a valid ZIP; do not touch
        print(f"[SKIP] Inconsistent EOCD/comment: {path}")
        return False

    if end_eocd == len(data):
        # Already clean; nothing to do
        print(f"[OK] Already clean: {path}")
        return True

    # Only now is it safe to truncate trailing junk
    path.write_bytes(data[:end_eocd])
    print(f"[FIXED] Truncated trailing junk: {path}")
    return True


def repair_all_zips(dir_path: str):
    base = Path(dir_path)
    for zip_path in base.glob("*.osz"):
        if not repair_zip(zip_path):
            os.remove(zip_path)


async def process_new_ranked_maps(client: MilvusClient):
    print("Downloading missing beatmapsets")

    # Download beatmaps
    downloaded_len = await download_missing_beatmapsets(client)

    if downloaded_len == 0:
        print("No beatmaps to download")
        return

    print("Removing corrupted files")

    repair_all_zips(ROOT_DIR)

    print("Creating dataset")

    # Get metadata and parse osz files
    mapperator_command = [
        MAPPERATOR,
        "dataset2",
        "-i",
        ROOT_DIR,
        "-o",
        MAPPERATOR_DIR,
        "-s",
    ]
    try:
        subprocess.run(mapperator_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FAILED MAPPERATOR: {e}")
        cleanup_dirs()
        return

    print("Calculating osu!skills")

    # Generate osu!skills values
    for mod_name, mod_val in MOD_PRESETS_SKILLS.items():
        out_csv = os.path.join(SKILLS_DIR, f"skills_{mod_name}.csv")
        command = [
            OSU_SKILLS_RS,
            f"--in={DATA_DIR}",
            "--is-dir=SUBDIR",
            "--output-type=file-csv",
            f"--out={out_csv}",
            f"--mods={mod_val}",
            "--alg=rebalance_1",
        ]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"FAILED for {mod_name}: {e}")

    print("Calculating pp values and strains")

    # Generate PP, Stars, and Strains values
    calculate_strains()

    print("Generating embeddings and inserting into Milvus")

    # Preprocess data and insert into the database
    generate_embeddings_and_insert_into_database(
        client, COLLECTION_NAME, METADATA_FILE, DIFFICULTY_FILE, SKILLS_DIR
    )

    cleanup_dirs()

    print("Finished processing new ranked maps")
    print(f"Number of beatmapsets processed: {downloaded_len + 1}")


def build_filter_template_expression(
    include_mods_filter: int | None = None,
    exclude_mods_filter: int | None = None,
    show_nsfw: bool = True,
    min_stars: float | None = None,
    max_stars: float | None = None,
    min_pp: float | None = None,
    max_pp: float | None = None,
    min_hit_length: float | None = None,
    max_hit_length: float | None = None,
    min_bpm: float | None = None,
    max_bpm: float | None = None,
    exclude_beatmapset_id: int | None = None,
):
    # Helper to find all mod values including bits of given filter bitmask
    def expand_include_filter(filter_bit):
        return [
            val
            for val in MOD_PRESETS_SKILLS.values()
            if val != 0 and (val & filter_bit) == filter_bit
        ]

    # Helper to find all mod values including any excluded bits
    def expand_exclude_filter(filter_bit):
        return [
            val
            for val in MOD_PRESETS_SKILLS.values()
            if val != 0 and (val & filter_bit) != 0
        ]

    include_list = []
    if include_mods_filter is not None and include_mods_filter != 0:
        include_list = expand_include_filter(include_mods_filter)

    exclude_list = []
    if exclude_mods_filter is not None and exclude_mods_filter != 0:
        exclude_list = expand_exclude_filter(exclude_mods_filter)

    expr_parts = []
    filter_params = {}

    # Mods inclusion/exclusion
    if include_list:
        expr_parts.append("Mods in {include_mods}")
        filter_params["include_mods"] = include_list
    if exclude_list:
        expr_parts.append("Mods not in {exclude_mods}")
        filter_params["exclude_mods"] = exclude_list

    # show_nsfw filter (Nsfw field is bool)
    if not show_nsfw:
        expr_parts.append("Nsfw == false")

    # Stars range filter (float)
    if min_stars is not None:
        expr_parts.append("Stars >= {min_stars}")
        filter_params["min_stars"] = min_stars
    if max_stars is not None:
        expr_parts.append("Stars <= {max_stars}")
        filter_params["max_stars"] = max_stars

    # PP range filter (float)
    if min_pp is not None:
        expr_parts.append("PP >= {min_pp}")
        filter_params["min_pp"] = min_pp
    if max_pp is not None:
        expr_parts.append("PP <= {max_pp}")
        filter_params["max_pp"] = max_pp

    # HitLength range filter (int16)
    if min_hit_length is not None:
        expr_parts.append("HitLength >= {min_hit_length}")
        filter_params["min_hit_length"] = min_hit_length
    if max_hit_length is not None:
        expr_parts.append("HitLength <= {max_hit_length}")
        filter_params["max_hit_length"] = max_hit_length

    # Bpm range filter (float)
    if min_bpm is not None:
        expr_parts.append("Bpm >= {min_bpm}")
        filter_params["min_bpm"] = min_bpm
    if max_bpm is not None:
        expr_parts.append("Bpm <= {max_bpm}")
        filter_params["max_bpm"] = max_bpm

    # Exclude other maps from the same beatmapset
    if exclude_beatmapset_id is not None:
        expr_parts.append("BeatmapSetId != {beatmapsetid}")
        filter_params["beatmapsetid"] = exclude_beatmapset_id

    expr = " and ".join(expr_parts) if expr_parts else ""

    return expr, filter_params


def find_similar_beatmaps_by_id(
    client: MilvusClient,
    beatmap_id: int,
    mod: int,
    top_n=10,
    show_nsfw: bool = True,
    min_stars: float | None = None,
    max_stars: float | None = None,
    min_pp: float | None = None,
    max_pp: float | None = None,
    min_hit_length: int | None = None,
    max_hit_length: int | None = None,
    min_bpm: float | None = None,
    max_bpm: float | None = None,
    exclude_mods_filter: int | None = None,
    include_mods_filter: int | None = None,
    exclude_beatmapset: bool = False,
):
    """Nearest Neighbor Beatmap Search"""
    expr = f"(BeatmapId == {beatmap_id}) and (Mods == {mod})"
    res = client.query(
        collection_name=COLLECTION_NAME,
        filter=expr,
        output_fields=[
            "Embedding",
            "Title",
            "Version",
            "BeatmapId",
            "Mods",
            "BeatmapSetId",
            "Stars",
            "Ranked",
            "RankedDate"
        ],
        limit=1,
    )
    if not res:
        return None
    query_record = res[0]
    query_vector = query_record["Embedding"]

    expr, filter_params = build_filter_template_expression(
        include_mods_filter,
        exclude_mods_filter,
        show_nsfw,
        min_stars,
        max_stars,
        min_pp,
        max_pp,
        min_hit_length,
        max_hit_length,
        min_bpm,
        max_bpm,
        exclude_beatmapset_id=(
            query_record["BeatmapSetId"] if exclude_beatmapset else None
        ),
    )

    search_results = client.search(
        collection_name=COLLECTION_NAME,
        data=[query_vector],
        filter=expr,
        filter_params=filter_params,
        anns_field="Embedding",
        limit=top_n + 1,
        output_fields=[
            "BeatmapId",
            "BeatmapSetId",
            "Mods",
            "Title",
            "Version",
            "Stars",
            "PP",
            "Ranked",
            "RankedDate",
        ],
    )
    if not search_results or len(search_results[0]) <= 1:
        return None

    # Filter out identical beatmap
    filtered_hits = [
        hit for hit in search_results[0] if hit.entity["BeatmapId"] != beatmap_id
    ][:top_n]

    rows = []
    query_stars = query_record["Stars"]
    for hit in filtered_hits:
        entity = hit.entity
        neighbor_stars = entity["Stars"]

        if query_stars > 0 and neighbor_stars > 0:
            x = query_stars / neighbor_stars
            k = 0.2  # increase for a steeper curve
            x0 = 1
            acc_mult = 1.99 / (1 + np.exp(-k * (x - x0)))
        else:
            acc_mult = 1  # fallback if no star rating

        row = {
            "BeatmapId": entity["BeatmapId"],
            "BeatmapSetId": entity["BeatmapSetId"],
            "Mods": entity["Mods"],
            "Title": entity["Title"],
            "Version": entity["Version"],
            "Ranked": entity["Ranked"],
            "Distance": hit.distance,
            "Stars": neighbor_stars,
            "PP": entity["PP"],
            "LastUpdated": entity["RankedDate"],
            "AccMult": acc_mult,
        }
        rows.append(row)
    return rows


async def get_user_top_scores(client: aiosu.v2.Client, user_id: int, n_scores=50):
    """Returns top user pp std scores"""
    best_scores = await client.get_user_bests(
        user_id=user_id,
        mode=aiosu.models.gamemode.Gamemode.STANDARD,
        limit=n_scores,
        new_format=True,
    )
    result = []
    for score in best_scores:
        beatmap = score.beatmap
        beatmapset = score.beatmapset
        mods_short = [m.acronym.lower() for m in (score.mods or [])]
        result.append(
            {
                "beatmap": {
                    "id": beatmap.id,
                    "version": beatmap.version,
                    "status": beatmap.status,
                },
                "beatmapset": {
                    "id": beatmapset.id,
                    "title": beatmapset.title,
                },
                "mods": mods_short,
                "accuracy": score.accuracy,
            }
        )
    return result


async def get_user_recent_scores(
    client: aiosu.v2.Client, user_id: int, n_scores: int = 50
):
    """Returns recent user std scores"""
    recent_scores = await client.get_user_recents(
        user_id=user_id,
        mode=aiosu.models.gamemode.Gamemode.STANDARD,
        limit=n_scores,
        new_format=True,
    )
    seen = {}
    accuracy_bucket = defaultdict(
        lambda: {
            "accuracies": [],
            "title": None,
            "version": None,
            "status": None,
        }
    )
    key_order = []
    for score in recent_scores:
        if (score.beatmap.status == aiosu.models.BeatmapRankStatus.RANKED or score.beatmap.status == aiosu.models.BeatmapRankStatus.APPROVED or score.beatmap.status == aiosu.models.BeatmapRankStatus.LOVED) and (
            not isinstance(score.mods, list)
            or not any("speed_change" in mod.settings for mod in score.mods)
        ):
            beatmap_id = score.beatmap.id if score.beatmap else None
            beatmapset_id = score.beatmap.beatmapset_id if score.beatmap else None
            mods = tuple(sorted([m.acronym.lower() for m in (score.mods or [])]))
            key = (beatmap_id, beatmapset_id, mods)
            accuracy_bucket[key]["accuracies"].append(score.accuracy)
            accuracy_bucket[key]["title"] = score.beatmapset.title
            accuracy_bucket[key]["version"] = score.beatmap.version
            accuracy_bucket[key]["status"] = score.beatmap.status
            if key not in seen:
                seen[key] = (beatmap_id, mods)
                key_order.append(key)
    result = []
    for key in key_order:
        beatmap_id, beatmapset_id, mods = key
        avg_accuracy = sum(accuracy_bucket[key]["accuracies"]) / len(
            accuracy_bucket[key]["accuracies"]
        )
        result.append(
            {
                "beatmap": {
                    "id": beatmap_id,
                    "version": accuracy_bucket[key]["version"],
                    "status": accuracy_bucket[key]["status"],
                },
                "beatmapset": {
                    "id": beatmapset_id,
                    "title": accuracy_bucket[key]["title"],
                },
                "mods": list(mods),
                "accuracy": avg_accuracy,
            }
        )
    return result


def tally_neighbors(
    client: MilvusClient,
    user_scores: list[aiosu.models.beatmap.Beatmap],
    top_n_neighbors=50,
    show_nsfw: bool = True,
    min_stars: float | None = None,
    max_stars: float | None = None,
    min_pp: float | None = None,
    max_pp: float | None = None,
    min_hit_length: int | None = None,
    max_hit_length: int | None = None,
    min_bpm: float | None = None,
    max_bpm: float | None = None,
    exclude_mods_filter: int | None = None,
    include_mods_filter: int | None = None,
):
    """Neighbor tally and scoring using distances"""
    neighbor_info = defaultdict(
        lambda: {
            "distances": [],
            "neighbors": [],
            "weights": [],
            "accuracies": [],
            "title": None,
            "version": None,
            "ranked": None,
            "stars": None,
            "pp": None,
            "updated": None,
        }
    )
    # max_distance = None
    for idx, score in enumerate(user_scores):
        beatmap_id = score["beatmap"]["id"]
        mod = (
            sum(MOD_PRESETS.get(m.lower(), 0) for m in score["mods"])
            if score["mods"]
            else 0
        )
        user_weight = 1 - (idx / 100)
        user_accuracy = score.get("accuracy", 0)
        neighbor_rows = find_similar_beatmaps_by_id(
            client,
            beatmap_id,
            mod,
            top_n=10,
            show_nsfw=show_nsfw,
            min_stars=min_stars,
            max_stars=max_stars,
            min_pp=min_pp,
            max_pp=max_pp,
            min_hit_length=min_hit_length,
            max_hit_length=max_hit_length,
            min_bpm=min_bpm,
            max_bpm=max_bpm,
            exclude_mods_filter=exclude_mods_filter,
            include_mods_filter=include_mods_filter,
            exclude_beatmapset=True,
        )
        if neighbor_rows is None:
            continue
        for row in neighbor_rows:
            key = (row["BeatmapId"], row["BeatmapSetId"], row["Mods"])
            neighbor_info[key]["distances"].append(
                row["Distance"] / neighbor_rows[-1]["Distance"]
            )
            neighbor_info[key]["neighbors"].append(
                {
                    "beatmap_id": beatmap_id,
                    "beatmapset_id": score["beatmapset"]["id"],
                    "mods": mod,
                    "distance": row["Distance"],
                    "title": score["beatmapset"]["title"],
                    "version": score["beatmap"]["version"],
                    "ranked": score["beatmap"]["status"],
                }
            )
            neighbor_info[key]["weights"].append(user_weight)
            multiplied = user_accuracy * row["AccMult"]
            # Use negative log: sharply penalizes above 1, and close to 0 as it approaches 0
            # The +1 in log keeps the range defined at 0, but for harsher effect, use log base < 1
            harsh_log_acc = (
                1 - np.log1p(max(multiplied - 1, 0) * 10) / np.log1p(10)
                if multiplied > 1
                else multiplied
            )
            log_acc = np.clip(harsh_log_acc, 0, 1)
            neighbor_info[key]["accuracies"].append(log_acc)
            if neighbor_info[key]["title"] is None:
                neighbor_info[key]["title"] = row["Title"]
            if neighbor_info[key]["version"] is None:
                neighbor_info[key]["version"] = row["Version"]
            if neighbor_info[key]["ranked"] is None:
                neighbor_info[key]["ranked"] = row["Ranked"]
            if neighbor_info[key]["stars"] is None:
                neighbor_info[key]["stars"] = row["Stars"]
            if neighbor_info[key]["pp"] is None:
                neighbor_info[key]["pp"] = row["PP"]
            if neighbor_info[key]["updated"] is None:
                neighbor_info[key]["updated"] = row["LastUpdated"]
    epsilon = 1e-6
    summary = []
    beatmap_to_index = {
        score["beatmap"]["id"]: idx for idx, score in enumerate(user_scores)
    }
    for key, val in neighbor_info.items():
        count = len(val["distances"])
        min_distance = min(val["distances"])
        max_weight = max(val["weights"])
        avg_accuracy = sum(val["accuracies"]) / count
        penalty = 1.0
        if key[0] in beatmap_to_index:
            penalty = 0
        summary.append(
            {
                "BeatmapId": key[0],
                "BeatmapSetId": key[1],
                "Mods": key[2],
                "Ranked": val["ranked"],
                "Stars": val["stars"],
                "PP": val["pp"],
                "LastUpdated": val["updated"],
                "Count": count,
                "MinDistance": min_distance,
                "MaxWeight": max_weight,
                "AvgAccuracy": avg_accuracy,
                "Title": val["title"],
                "Version": val["version"],
                "Neighbors": val["neighbors"],
                "Penalty": penalty,
                "Score": (
                    (((0.1 * log2(count + 1)) + 0.9) * ((2 ** (max_weight**4)) - 1))
                    / (min_distance + epsilon)
                    * penalty
                ),
            }
        )
    if not summary:
        return []

    summary_sorted = sorted(summary, key=lambda x: -x["Score"])
    return summary_sorted[:top_n_neighbors]


@app.get("/")
async def health():
    return {"status": "ok"}


@app.get("/get_difficulties/")
async def get_difficulties(
    beatmapset_id: int,
):
    try:
        client: MilvusClient = app.state.milvus_client
        expr = f"(BeatmapSetId == {beatmapset_id}) and (Mods == 0)"
        beatmaps = client.query(
            collection_name=COLLECTION_NAME,
            filter=expr,
            output_fields=[
                "BeatmapId",
                "BeatmapSetId",
                "Title",
                "Version",
                "Ranked",
                "Nsfw",
                "Stars",
                "PP",
            ],
        )
        return beatmaps
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/similar_beatmaps/")
async def api_similar_beatmaps(
    beatmap_id: int,
    mods: int,
    top_n: int = 10,
    show_nsfw: bool = True,
    min_stars: float | None = None,
    max_stars: float | None = None,
    min_pp: float | None = None,
    max_pp: float | None = None,
    min_hit_length: int | None = None,
    max_hit_length: int | None = None,
    min_bpm: float | None = None,
    max_bpm: float | None = None,
    exclude_mods_filter: int | None = None,
    include_mods_filter: int | None = None,
):
    rows = find_similar_beatmaps_by_id(
        app.state.milvus_client,
        beatmap_id,
        mods,
        top_n,
        show_nsfw,
        min_stars,
        max_stars,
        min_pp,
        max_pp,
        min_hit_length,
        max_hit_length,
        min_bpm,
        max_bpm,
        exclude_mods_filter,
        include_mods_filter,
    )
    if rows is None:
        raise HTTPException(status_code=404, detail="No beatmap found")
    return {"neighbors": rows}


@app.post("/user_top_neighbors/")
async def api_user_top_neighbors(req: UserRequest):
    try:
        user_scores = await get_user_top_scores(app.state.aiosu_client, req.user_id)
        summary = tally_neighbors(
            app.state.milvus_client,
            user_scores,
            req.top_n_neighbors,
            req.show_nsfw,
            req.min_stars,
            req.max_stars,
            req.min_pp,
            req.max_pp,
            req.min_hit_length,
            req.max_hit_length,
            req.min_bpm,
            req.max_bpm,
            req.exclude_mods_filter,
            req.include_mods_filter,
        )
        return {"user_id": req.user_id, "top_neighbors": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/user_pulse/")
async def api_user_recent_neighbors(req: UserRequest):
    try:
        user_scores = await get_user_recent_scores(app.state.aiosu_client, req.user_id)
        summary = tally_neighbors(
            app.state.milvus_client,
            user_scores,
            req.top_n_neighbors,
            req.show_nsfw,
            req.min_stars,
            req.max_stars,
            req.min_pp,
            req.max_pp,
            req.min_hit_length,
            req.max_hit_length,
            req.min_bpm,
            req.max_bpm,
            req.exclude_mods_filter,
            req.include_mods_filter,
        )
        return {"user_id": req.user_id, "top_neighbors": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
