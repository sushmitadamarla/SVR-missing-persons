import json
import traceback
from collections import defaultdict
import numpy as np
import pandas as pd
from scipy.spatial.distance import cosine
from pages.helper import db_queries


def cosine_similarity(emb1, emb2):
    """Compute cosine similarity between two embeddings."""
    if emb1 is None or emb2 is None:
        return 0.0
    return 1 - cosine(emb1, emb2)


def get_registered_cases_data(status="NF"):
    """Fetch registered cases and load embeddings."""
    try:
        result = db_queries.fetch_registered_cases(train_data=True, status=status)
        df = pd.DataFrame(result, columns=["id", "embedding"])
        df["embedding"] = df["embedding"].apply(
            lambda x: np.array(json.loads(x)) if x else None
        )
        df = df.dropna(subset=["embedding"])
        return df
    except Exception:
        traceback.print_exc()
        return None


def get_public_cases_data(status="NF"):
    """Fetch public cases and load embeddings."""
    try:
        result = db_queries.fetch_public_cases(train_data=True, status=status)
        df = pd.DataFrame(result, columns=["id", "embedding"])
        df["embedding"] = df["embedding"].apply(
            lambda x: np.array(json.loads(x)) if x else None
        )
        df = df.dropna(subset=["embedding"])
        return df
    except Exception:
        traceback.print_exc()
        return None


def match(threshold=0.35):
    """
    Match embeddings between registered and public cases using cosine similarity.
    Higher similarity → more likely match.
    """
    matched_cases = defaultdict(list)

    registered_df = get_registered_cases_data(status="NF")
    public_df = get_public_cases_data(status="NF")

    if registered_df is None or public_df is None:
        return {"status": False, "message": "Database fetch failed"}
    if registered_df.empty or public_df.empty:
        return {"status": False, "message": "No data available"}

    # Compare every public case with each registered case
    for _, pub_row in public_df.iterrows():
        pub_id = pub_row["id"]
        pub_emb = pub_row["embedding"]

        best_match_id = None
        best_similarity = 0.0

        for _, reg_row in registered_df.iterrows():
            reg_id = reg_row["id"]
            reg_emb = reg_row["embedding"]

            sim = cosine_similarity(pub_emb, reg_emb)

            if sim > best_similarity:
                best_similarity = sim
                best_match_id = reg_id

        # ✅ If similarity above threshold, it's a match
        if best_similarity >= threshold:
            matched_cases[best_match_id].append(pub_id)
            print(f"[MATCH] {pub_id} ↔ {best_match_id} (Similarity: {best_similarity:.3f})")
        else:
            print(f"[NO MATCH] {pub_id} best similarity = {best_similarity:.3f}")

    return {"status": True, "result": matched_cases}


if __name__ == "__main__":
    result = match(threshold=0.35)
    print(result)
