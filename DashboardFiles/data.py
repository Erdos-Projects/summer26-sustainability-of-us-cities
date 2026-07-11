import math

import numpy as np
import pandas as pd

# The merged, per-county dimension scores (built by build_dimensions.py). Every
# dimension column is on a 0-100, higher-is-better scale.
DATA_PATH = "dimension_scores.csv"

# The eight ranking dimensions, all backed by real data.
FINANCIAL_DIMENSION = "Financial Well-Being"
DIMENSIONS = [
    FINANCIAL_DIMENSION,
    "Air Pollution and Climate Risk",
    "Security",
    "Housing",
    "Health and Quality of Life",
    "Mobility and Infrastructure",
    "Social Capital and Community",
    "Food, Water, Amenities",
]


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
    """Read the merged dimension_scores CSV. Returns fips (5-digit string),
    state, county, and one 0-100 column per dimension. A dimension may be NaN
    for counties missing from that source; compute_score handles those."""
    df = pd.read_csv(path, dtype={"fips": str})
    df["fips"] = df["fips"].map(clean_fips)
    df = df.dropna(subset=["fips"]).reset_index(drop=True)
    return df[["fips", "state", "county"] + DIMENSIONS]


def compute_score(df, weights=None):
    """Return a copy of df with a `score` column on a 0-100 scale.

    With no weights (or all-zero weights) the score is the Financial
    Well-Being dimension. Otherwise the score is the weight-normalized average
    of the dimension columns, computed per county over the dimensions that are
    present (missing dimensions are skipped, and their weight drops out of the
    denominator) so partial-coverage counties still get a score:
    score = sum(w_i * dim_i) / sum(w_i)  over present dimensions."""
    result = df.copy()
    total = sum(weights.values()) if weights else 0
    if total == 0:
        result["score"] = result[FINANCIAL_DIMENSION]
        return result
    w = np.array([weights.get(dimension, 0) for dimension in DIMENSIONS], dtype=float)
    values = result[DIMENSIONS].to_numpy(dtype=float)
    present = ~np.isnan(values)
    denominator = present @ w  # per-county sum of weights where the value exists
    numerator = np.nansum(values * w, axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        result["score"] = np.where(denominator > 0, numerator / denominator, np.nan)
    return result


def top_bottom(df, n=5):
    """Return (top_n, bottom_n) by `score`, each with county/state/score.
    Counties with no score (all weighted dimensions missing) are excluded."""
    ordered = df.dropna(subset=["score"]).sort_values("score", ascending=False)
    columns = ["county", "state", "score"]
    top = ordered.head(n)[columns].reset_index(drop=True)
    bottom = ordered.tail(n)[columns].iloc[::-1].reset_index(drop=True)
    return top, bottom
