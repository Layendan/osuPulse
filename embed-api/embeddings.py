import csv
import os

import joblib
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from calcModStats import mod_calculator_factory
from pymilvus import MilvusClient
from scipy.interpolate import interp1d
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUM_SCALER_PATH = "num_scaler.joblib"
SKILL_SCALER_PATH = "skill_scaler.joblib"
STRAIN_SCALER_PATH = "strain_scaler.joblib"

MOD_PRESETS = {
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

genre_encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
GENRES = [
    "Anime",
    "Classical",
    "Electronic",
    "Folk",
    "Hip Hop",
    "Jazz",
    "Metal",
    "Novelty",
    "Other",
    "Pop",
    "Rock",
    "Unspecified",
    "Video Game",
]
genre_encoder.fit(np.array(GENRES).reshape(-1, 1))

EMBED_DTYPE = np.int8           # or np.int8
STRAIN_BINS = 128               # try 128 first; 256 if quality drops too much
QUANT_MIN = -6.0                # for int8 only
QUANT_MAX = 6.0                 # for int8 only


# Utility Functions
def rescale_to_bins(strain_array, num_bins=STRAIN_BINS):
    flat = []
    for x in np.array(strain_array).flatten():
        if isinstance(x, (float, int, np.float32, np.float64, np.int32, np.int64)):
            flat.append(float(x))
        elif isinstance(x, (list, np.ndarray)):
            flat.extend(
                [
                    float(y)
                    for y in np.array(x).flatten()
                    if isinstance(y, (float, int, np.float32, np.float64, np.int32, np.int64))
                ]
            )

    strain_array = np.array(flat, dtype=np.float32)
    if len(strain_array) == 0:
        return np.zeros(num_bins, dtype=np.float32)

    if len(strain_array) == 1:
        return np.full(num_bins, strain_array[0], dtype=np.float32)

    x_original = np.linspace(0, 1, len(strain_array))
    x_new = np.linspace(0, 1, num_bins)
    f = interp1d(x_original, strain_array, kind="linear", fill_value="extrapolate")
    return f(x_new).astype(np.float32)

def quantize_embedding(x, dtype=EMBED_DTYPE):
    x = np.asarray(x, dtype=np.float32)

    if dtype == np.int8:
        clipped = np.clip(x, QUANT_MIN, QUANT_MAX)
        scaled = (clipped - QUANT_MIN) / (QUANT_MAX - QUANT_MIN)
        q = np.round(scaled * 255.0 - 128.0).astype(np.int8)
        return q

    return x.astype(dtype)


# Load skills CSV files into dict by mod key
def load_skills(skills_folder="skills_output"):
    skills_data = {}
    for fname in os.listdir(skills_folder):
        if fname.startswith("skills_") and fname.endswith(".csv"):
            mod_key = fname[7:-4]
            df = pd.read_csv(
                os.path.join(skills_folder, fname),
                usecols=[
                    "BeatmapID",
                    "BeatmapsetID",
                    "Mods",
                    "Stamina",
                    "Tenacity",
                    "Agility",
                    "Accuracy",
                    "Precision",
                    "Reaction",
                    "Memory",
                ],
                dtype={
                    "BeatmapID": "Int64",
                    "BeatmapsetID": "Int64",
                    "Mods": "Int64",
                    "Stamina": "float64",
                    "Tenacity": "float64",
                    "Agility": "float64",
                    "Accuracy": "float64",
                    "Precision": "float64",
                    "Reaction": "float64",
                    "Memory": "float64",
                },
                engine="python",
                quoting=csv.QUOTE_MINIMAL,
                on_bad_lines="skip",
                escapechar="\\",
            )
            skills_data[mod_key] = df.set_index("BeatmapID")
    return skills_data


def create_embedding(
    row_meta,
    row_diff,
    skills_row,
    num_scaler: StandardScaler,
    skill_scaler: StandardScaler,
    strain_scaler: StandardScaler,
):
    num_features = np.array(
        [
            row_meta["MaxCombo"],
            row_meta["Ar"],
            row_meta["Accuracy"],
            row_meta["Bpm"],
            row_meta["CountCircles"],
            row_meta["CountSliders"],
            row_meta["CountSpinners"],
            row_meta["Cs"],
            row_meta["Drain"],
            row_meta["HitLength"],
        ]
    ).reshape(1, -1)
    genre_vector = genre_encoder.transform([[row_meta["GenreName"]]])
    num_features_with_genre = np.hstack([num_features, genre_vector])
    num_scaled = num_scaler.transform(num_features_with_genre)

    skill_values = skills_row[
        ["Stamina", "Tenacity", "Agility", "Accuracy", "Precision", "Reaction"]
    ].values.reshape(1, -1)
    skill_scaled = skill_scaler.transform(skill_values)

    strain_vecs = []
    for strain_name in ["AimStrain", "AimNoSlidersStrain", "SpeedStrain"]:
        strain_arr = row_diff[strain_name]
        strain_bin = rescale_to_bins(strain_arr, STRAIN_BINS)
        strain_vecs.append(strain_bin)
    strain_concat = np.concatenate(strain_vecs).reshape(1, -1)
    strain_scaled = strain_scaler.transform(strain_concat)

    total_len = num_scaled.size + skill_scaled.size + strain_scaled.size
    features_weight = 0.20 * total_len / num_scaled.size
    skills_weight = 0.50 * total_len / skill_scaled.size
    strain_weight = 0.30 * total_len / strain_scaled.size

    weighted_features = num_scaled.flatten() * features_weight
    weighted_skills = skill_scaled.flatten() * skills_weight
    weighted_strain = strain_scaled.flatten() * strain_weight

    embedding = np.hstack([weighted_features, weighted_skills, weighted_strain])
    embedding = quantize_embedding(embedding)
    return embedding


EXPECTED_DTYPES = {
    "BeatmapId": "int64",
    "BeatmapSetId": "int64",
    "Title": "string",
    "Version": "string",
    "Artist": "string",
    "Mods": "int64",
    "Mode": "string",
    "ModeInt": "int64",
    "Ranked": "int64",
    "Status": "string",
    "Nsfw": "bool",
    "Spotlight": "bool",
    "Genre": "string",
    "Language": "string",
    "Embedding": "object",  # list of floats, stored as object
    "Stars": "float64",
    "PP": "float64",
    "MaxCombo": "int64",
    "Ar": "float64",
    "Od": "float64",
    "Cs": "float64",
    "Hp": "float64",
    "Bpm": "float64",
    "HitLength": "int64",
    "RankedDate": "datetime64[ns]",
}


def enforce_dtypes(df):
    for col, dtype in EXPECTED_DTYPES.items():
        if col in df.columns:
            if dtype == "string":
                df[col] = df[col].astype("string")
            elif dtype == "bool":
                df[col] = df[col].astype("bool")
            else:
                df[col] = df[col].astype(dtype)

    # Handle RankedDate for TIMESTAMPTZ
    if "RankedDate" in df.columns:
        df["RankedDate"] = pd.to_datetime(df["RankedDate"]).dt.strftime('%Y-%m-%dT%H:%M:%S%z')

    if "Embedding" in df.columns:
        df["Embedding"] = df["Embedding"].apply(list)
    return df


def beatmap_exists_in_milvus(
    client: MilvusClient, collection_name: str, beatmapid: int, mods_val: int
):
    results = client.query(
        collection_name=collection_name,
        filter=f"BeatmapId == {beatmapid} and Mods == {mods_val}",
        output_fields=["BeatmapId"],
        limit=1,
    )
    return len(results) > 0


# Main program
def generate_embeddings_and_insert_into_database(
    client: MilvusClient,
    collection_name: str,
    metadata_file: str,
    difficulty_file: str,
    skills_folder: str,
):
    strain_scaler: StandardScaler = joblib.load(STRAIN_SCALER_PATH)
    skill_scaler: StandardScaler = joblib.load(SKILL_SCALER_PATH)
    num_scaler: StandardScaler = joblib.load(NUM_SCALER_PATH)

    skills_data = load_skills(skills_folder)

    diff_pq = pq.ParquetFile(difficulty_file)

    metadata_df = pd.read_parquet(
        metadata_file,
        columns=[
            "Id",
            "BeatmapSetId",
            "Title",
            "Version",
            "Artist",
            "Mode",
            "ModeInt",
            "Ranked",
            "Status",  # Ranked/Grave/Qualified/Loved etc
            "Nsfw",
            "Spotlight",
            "GenreName",
            "LanguageName",
            "MaxCombo",
            "Ar",
            "Accuracy",
            "Bpm",
            "CountCircles",
            "CountSliders",
            "CountSpinners",
            "Cs",
            "Drain",
            "HitLength",
            "RankedDate",
        ],
    ).set_index("Id")

    results = []
    BATCH_SIZE = 1000
    batch_idx = 0

    for rg_idx in range(diff_pq.num_row_groups):
        diff_table = diff_pq.read_row_group(rg_idx)
        diff_df = diff_table.to_pandas()

        num_features_list = []
        skill_values_list = []
        strain_list = []

        for _, diff_row in diff_df.iterrows():
            beatmap_id = diff_row["Id"]
            mod_val = diff_row["Mods"]

            if beatmap_id not in metadata_df.index:
                continue
            meta_row = metadata_df.loc[beatmap_id]

            mod_key = [k for k, v in MOD_PRESETS.items() if v == mod_val]
            if not mod_key or mod_key[0] not in skills_data:
                continue
            skills_df = skills_data[mod_key[0]]
            if beatmap_id not in skills_df.index:
                continue

            skills_row = skills_df.loc[beatmap_id]

            # Adjust meta for mods here before feature extraction!
            adjusted_meta = dict(meta_row)
            if mod_val != 0:
                calculator = mod_calculator_factory(
                    meta_row["Ar"],
                    meta_row["Accuracy"],
                    meta_row["Cs"],
                    meta_row["Drain"],
                    meta_row["Bpm"],
                    meta_row["HitLength"],
                    mod_val,
                )
                mod_stats = calculator.calculate_all()
                adjusted_meta.update(
                    {
                        "Ar": round(mod_stats["ar"], 2),
                        "Accuracy": round(mod_stats["od"], 2),
                        "Cs": round(mod_stats["cs"], 2),
                        "Drain": round(mod_stats["hp"], 2),
                        "Bpm": round(mod_stats["bpm"]),
                        "HitLength": round(mod_stats["length"]),
                    }
                )

            # Extract features on adjusted meta, *not* raw meta!
            num_features = np.array(
                [
                    adjusted_meta["MaxCombo"],
                    adjusted_meta["Ar"],
                    adjusted_meta["Accuracy"],
                    adjusted_meta["Bpm"],
                    adjusted_meta["CountCircles"],
                    adjusted_meta["CountSliders"],
                    adjusted_meta["CountSpinners"],
                    adjusted_meta["Cs"],
                    adjusted_meta["Drain"],
                    adjusted_meta["HitLength"],
                ]
            )
            genre_vec = genre_encoder.transform([[adjusted_meta["GenreName"]]])[0]
            num_features_list.append(np.hstack([num_features, genre_vec]))

            skill_vals = skills_row[
                ["Stamina", "Tenacity", "Agility", "Accuracy", "Precision", "Reaction"]
            ].values
            skill_values_list.append(skill_vals)

            strain_vecs = []
            for strain_name in ["AimStrain", "AimNoSlidersStrain", "SpeedStrain"]:
                strain_arr = diff_row[strain_name]
                strain_bin = rescale_to_bins(strain_arr, STRAIN_BINS)
                strain_vecs.append(strain_bin)
            strain_concat = np.concatenate(strain_vecs)
            strain_list.append(strain_concat)

        if num_features_list:
            num_features_batch = np.vstack(num_features_list)
            skill_values_batch = np.vstack(skill_values_list)
            strain_batch = np.vstack(strain_list)

            if num_scaler is None:
                num_scaler = StandardScaler()
                num_scaler.partial_fit(num_features_batch)
            else:
                num_scaler.partial_fit(num_features_batch)

            if skill_scaler is None:
                skill_scaler = StandardScaler()
                skill_scaler.partial_fit(skill_values_batch)
            else:
                skill_scaler.partial_fit(skill_values_batch)

            if strain_scaler is None:
                strain_scaler = StandardScaler()
                strain_scaler.partial_fit(strain_batch)
            else:
                strain_scaler.partial_fit(strain_batch)

            # Now transform right after partial_fit and create embeddings
            for i, diff_row in enumerate(diff_df.itertuples()):
                beatmap_id = diff_row.Id
                mod_val = diff_row.Mods

                if beatmap_exists_in_milvus(
                    client, collection_name, beatmap_id, mod_val
                ):
                    print(f"Skipping: {beatmap_id} - {mod_val}")
                    continue

                if beatmap_id not in metadata_df.index:
                    continue
                meta_row = metadata_df.loc[beatmap_id]

                mod_key = [k for k, v in MOD_PRESETS.items() if v == mod_val]
                if not mod_key or mod_key[0] not in skills_data:
                    continue
                skills_df = skills_data[mod_key[0]]
                if beatmap_id not in skills_df.index:
                    continue

                skills_row = skills_df.loc[beatmap_id]

                adjusted_meta = dict(meta_row)
                if mod_val != 0:
                    calculator = mod_calculator_factory(
                        meta_row["Ar"],
                        meta_row["Accuracy"],
                        meta_row["Cs"],
                        meta_row["Drain"],
                        meta_row["Bpm"],
                        meta_row["HitLength"],
                        mod_val,
                    )
                    mod_stats = calculator.calculate_all()
                    adjusted_meta.update(
                        {
                            "Ar": round(mod_stats["ar"], 2),
                            "Accuracy": round(mod_stats["od"], 2),
                            "Cs": round(mod_stats["cs"], 2),
                            "Drain": round(mod_stats["hp"], 2),
                            "Bpm": round(mod_stats["bpm"]),
                            "HitLength": round(mod_stats["length"]),
                        }
                    )

                embedding = create_embedding(
                    adjusted_meta,
                    diff_row._asdict(),
                    skills_row,
                    num_scaler,
                    skill_scaler,
                    strain_scaler,
                )

                results.append(
                    {
                        "BeatmapId": beatmap_id,
                        "BeatmapSetId": adjusted_meta.get("BeatmapSetId"),
                        "Title": adjusted_meta.get("Title"),
                        "Version": adjusted_meta.get("Version"),
                        "Artist": adjusted_meta.get("Artist"),
                        "Mods": mod_val,
                        "Mode": adjusted_meta.get("Mode"),
                        "ModeInt": adjusted_meta.get("ModeInt"),
                        "Ranked": adjusted_meta.get("Ranked"),
                        "Status": adjusted_meta.get("Status"),
                        "Nsfw": adjusted_meta.get("Nsfw"),
                        "Spotlight": adjusted_meta.get("Spotlight"),
                        "Genre": adjusted_meta.get("GenreName"),
                        "Language": adjusted_meta.get("LanguageName"),
                        "Embedding": embedding.tolist(),
                        "Stars": getattr(diff_row, "Stars", None),
                        "PP": getattr(diff_row, "TotalPP", None),
                        "MaxCombo": adjusted_meta.get("MaxCombo"),
                        "Ar": adjusted_meta.get("Ar"),
                        "Od": adjusted_meta.get("Accuracy"),
                        "Cs": adjusted_meta.get("Cs"),
                        "Hp": adjusted_meta.get("Drain"),
                        "Bpm": adjusted_meta.get("Bpm"),
                        "HitLength": adjusted_meta.get("HitLength"),
                        "RankedDate": adjusted_meta.get("RankedDate"),
                    }
                )

                if len(results) == BATCH_SIZE:
                    df = pd.DataFrame(results)
                    records = df.to_dict("records")
                    client.insert(collection_name=collection_name, data=records)
                    records.clear()
                    batch_idx += 1
                    print(f"Inserted batch {batch_idx}")

    if len(results) > 0:
        df = pd.DataFrame(results)
        records = df.to_dict("records")
        client.insert(collection_name=collection_name, data=records)
        records.clear()
        print("Inserted final batch")

    print("Flushing collection")

    client.flush(collection_name)

    print("Finished")

    joblib.dump(num_scaler, NUM_SCALER_PATH)
    joblib.dump(skill_scaler, SKILL_SCALER_PATH)
    joblib.dump(strain_scaler, STRAIN_SCALER_PATH)
