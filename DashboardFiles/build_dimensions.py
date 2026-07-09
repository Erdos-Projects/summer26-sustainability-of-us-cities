"""Build the merged dimension_scores.csv the dashboard reads.

Reads the five real dimension sources, normalizes each to a 0-100
"higher is better" scale, joins them on 5-digit FIPS onto the financial
county list, and writes dimension_scores.csv.

Scaling decisions (confirmed with the project owner):
- Financial, Safety/Crime, Quality of Life, Infrastructure: already 0-100 and
  oriented higher = better -> used as-is.
- Environmental_Risk_Index is a risk z-score (higher = worse) -> inverted and
  percentile-ranked to an even 0-100 spread (robust to its heavy right skew).

The Infrastructure source lives outside the repo; override with --infra if it
moves. Re-run this script whenever a source updates, then commit the output.
"""

import argparse
import os

import numpy as np
import pandas as pd

from data import (
    FINANCIAL_DIMENSION,
    clean_fips,
)

# Dimension name -> (source path, fips column, value column)
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UIC_ROOT = os.path.dirname(REPO_ROOT)

FINANCIAL_SRC = os.path.join(REPO_ROOT, "code", "financial_sustainability.csv")
DEFAULT_INFRA_SRC = os.path.join(UIC_ROOT, "Claude", "social_capital_mobility_index.csv")

SOURCES = {
    FINANCIAL_DIMENSION: (FINANCIAL_SRC, "5fipscode", "stability_score"),
    "Environmental Sustainability": (
        os.path.join(REPO_ROOT, "data", "environmental_ranking.csv"),
        "FIPS",
        "Environmental_Risk_Index",
    ),
    "Safety and Crime": (
        os.path.join(REPO_ROOT, "code", "Security", "Crime_Score_by_County.csv"),
        "FIPS_5digit",
        "Crime Score",
    ),
    "Quality of Life": (
        os.path.join(
            REPO_ROOT,
            "code",
            "Health and Quality of Life",
            "Health and Quality of Life Score by County.csv",
        ),
        "FIPS",
        "Health and Quality of Life Score",
    ),
    "Infrastructure and Community": (
        DEFAULT_INFRA_SRC,
        "5fipscode",
        "social_capital_mobility_index",
    ),
}

# Dimensions that arrive already on a 0-100, higher-is-better scale.
AS_IS_DIMENSIONS = {
    FINANCIAL_DIMENSION,
    "Safety and Crime",
    "Quality of Life",
    "Infrastructure and Community",
}


def _load_dimension(dimension, path, fips_col, value_col):
    """Return a DataFrame [fips, <dimension>] on a 0-100 higher-is-better scale."""
    df = pd.read_csv(path)
    if fips_col not in df.columns or value_col not in df.columns:
        raise ValueError(f"{dimension}: missing '{fips_col}' or '{value_col}' in {path}")
    out = pd.DataFrame()
    out["fips"] = df[fips_col].map(clean_fips)
    values = pd.to_numeric(df[value_col], errors="coerce")
    if dimension in AS_IS_DIMENSIONS:
        out[dimension] = values
    else:
        # Environmental_Risk_Index: invert (low risk -> high) then percentile-rank.
        out[dimension] = (-values).rank(pct=True) * 100
    out = out.dropna(subset=["fips"]).drop_duplicates(subset=["fips"])
    return out


def _financial_names(path):
    """Base county list with display names, from the financial source."""
    df = pd.read_csv(path, usecols=["5fipscode", "State Name", "County Name"])
    base = pd.DataFrame()
    base["fips"] = df["5fipscode"].map(clean_fips)
    base["state"] = df["State Name"].str.title()
    base["county"] = df["County Name"].str.title()
    return base.dropna(subset=["fips"]).drop_duplicates(subset=["fips"])


def build(infra_src=None, out_path="dimension_scores.csv"):
    if infra_src:
        SOURCES["Infrastructure and Community"] = (
            infra_src,
            *SOURCES["Infrastructure and Community"][1:],
        )
    merged = _financial_names(FINANCIAL_SRC)
    for dimension, (path, fips_col, value_col) in SOURCES.items():
        dim = _load_dimension(dimension, path, fips_col, value_col)
        merged = merged.merge(dim, on="fips", how="left")
    merged = merged.reset_index(drop=True)
    merged.to_csv(out_path, index=False)
    return merged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--infra", default=None, help="path to the infrastructure source CSV")
    parser.add_argument("--out", default="dimension_scores.csv")
    args = parser.parse_args()
    result = build(infra_src=args.infra, out_path=args.out)
    dims = [c for c in result.columns if c not in ("fips", "state", "county")]
    print(f"wrote {args.out}: {len(result)} counties")
    for d in dims:
        s = result[d]
        print(f"  {d:32s} coverage={s.notna().mean()*100:5.1f}%  "
              f"min={s.min():6.2f} max={s.max():6.2f} mean={s.mean():6.2f}")
