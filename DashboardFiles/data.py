import math

import numpy as np
import pandas as pd

DATA_PATH = "financial_sustainability.csv"
USED_COLUMNS = ["5fipscode", "stability_score", "State Name", "County Name"]

# The five ranking dimensions. Only Financial Well-Being is backed by real
# data (stability_score); the rest are deterministic placeholders on a 0-100
# scale until real per-county data is supplied.
FINANCIAL_DIMENSION = "Financial Well-Being"
PLACEHOLDER_DIMENSIONS = [
    "Environmental Sustainability",
    "Safety and Crime",
    "Infrastructure and Community",
    "Quality of Life",
]
DIMENSIONS = [FINANCIAL_DIMENSION] + PLACEHOLDER_DIMENSIONS


def clean_fips(value):
    """Convert a raw FIPS value (e.g. 1001.0 or '1001.0') to a 5-digit
    zero-padded string, or None if missing/unparseable."""
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return None
    return f"{number:05d}"


def load_data(path):
    """Read the CSV, keep the relevant columns, clean FIPS, title-case names,
    and drop rows with missing FIPS or missing stability_score."""
    df = pd.read_csv(path, usecols=USED_COLUMNS)
    df = df.rename(
        columns={
            "5fipscode": "fips",
            "State Name": "state",
            "County Name": "county",
        }
    )
    df["fips"] = df["fips"].map(clean_fips)
    df["state"] = df["state"].str.title()
    df["county"] = df["county"].str.title()
    df = df.dropna(subset=["fips", "stability_score"])
    return df[["fips", "stability_score", "state", "county"]].reset_index(drop=True)


def add_dimension_scores(df):
    """Return a copy of df with a 0-100 score column for each of the five
    dimensions. Financial Well-Being mirrors the real stability_score; the
    other four are deterministic placeholders (seeded, so they are stable
    across reruns) until real per-county data replaces them."""
    result = df.copy()
    if FINANCIAL_DIMENSION not in result.columns:
        result[FINANCIAL_DIMENSION] = result["stability_score"]
    for offset, dimension in enumerate(PLACEHOLDER_DIMENSIONS):
        if dimension in result.columns:
            continue
        rng = np.random.default_rng(1000 + offset)
        result[dimension] = rng.normal(60, 20, size=len(result))
    return result


def compute_score(df, weights=None):
    """Return a copy of df with a `score` column on a 0-100 scale.

    With no weights (or all-zero weights) the score is the Financial
    Well-Being dimension (stability_score). Otherwise the score is the
    weight-normalized average of the five dimension columns:
    score = sum(weight_i * dimension_i) / sum(weight_i)."""
    result = add_dimension_scores(df)
    total = sum(weights.values()) if weights else 0
    if total == 0:
        result["score"] = result["stability_score"]
        return result
    weighted = sum(
        weights.get(dimension, 0) * result[dimension] for dimension in DIMENSIONS
    )
    result["score"] = weighted / total
    return result


def top_bottom(df, n=5):
    """Return (top_n, bottom_n) by `score`, each with county/state/score."""
    ordered = df.sort_values("score", ascending=False)
    columns = ["county", "state", "score"]
    top = ordered.head(n)[columns].reset_index(drop=True)
    bottom = ordered.tail(n)[columns].iloc[::-1].reset_index(drop=True)
    return top, bottom
