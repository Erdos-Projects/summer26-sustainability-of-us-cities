"""Build the merged dimension_scores.csv the dashboard reads.

Reads the eight real dimension sources, normalizes each to a 0-100
"higher is better" scale, joins them on 5-digit FIPS onto the financial
county list, and writes dimension_scores.csv.

Scaling / direction per source (all end up higher = better, 0-100):
- as-is        : already a 0-100 higher-is-better score.
- invert_100   : a 0-100 score where higher = worse -> 100 - x.
- invert_pct   : a raw index where higher = worse -> invert and
                 percentile-rank across counties (robust to skew/outliers).

FIPS is taken from a column, built from separate state+county FIPS columns,
or (for the social-capital file, which ships without a key) recovered by
row position from a sibling file that has FIPS.

Some sources live outside the repo (see UIC_ROOT/Claude); override the two
_with_index paths with --mobility / --social if they move. Re-run after any
source updates, then commit the output.
"""

import argparse
import os

import numpy as np
import pandas as pd

from data import DIMENSIONS, FINANCIAL_DIMENSION, clean_fips

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UIC_ROOT = os.path.dirname(REPO_ROOT)
CLAUDE = os.path.join(UIC_ROOT, "Claude")

FINANCIAL_SRC = os.path.join(REPO_ROOT, "code", "financial_sustainability.csv")
SOCIAL_FIPS_SIBLING = os.path.join(
    REPO_ROOT, "data", "social_economic",
    "social_capital_county_economic_connectedness.csv",
)


def _as_is(values):
    return values


def _invert_100(values):
    return 100 - values


def _invert_pct(values):
    # higher = worse -> invert, then percentile-rank to an even 0-100 spread.
    return (-values).rank(pct=True) * 100


def _fips_from_state_county(df, state_col, county_col):
    out = []
    for state, county in zip(df[state_col], df[county_col]):
        if pd.isna(state) or pd.isna(county):
            out.append(None)
        else:
            out.append(f"{int(state):02d}{int(county):03d}")
    return out


# name -> spec. fips is one of:
#   ("col", column)                     -> clean_fips on that column
#   ("state_county", state, county)     -> zero-padded state+county
#   ("positional", sibling_path, col)   -> FIPS by row position from sibling
def specs(mobility_src, social_src):
    return {
        FINANCIAL_DIMENSION: dict(
            path=FINANCIAL_SRC, fips=("col", "5fipscode"),
            value="stability_score", transform=_as_is),
        "Air Pollution and Climate Risk": dict(
            path=os.path.join(REPO_ROOT, "data", "environmental_ranking.csv"),
            fips=("col", "FIPS"), value="Environmental_Risk_Index",
            transform=_invert_pct),
        "Security": dict(
            path=os.path.join(REPO_ROOT, "code", "Security",
                              "Crime_Score_by_County.csv"),
            fips=("col", "FIPS_5digit"), value="Crime Score", transform=_as_is),
        "Housing": dict(
            path=os.path.join(REPO_ROOT, "code", "Housing",
                              "Housing_Score_by_County.csv"),
            fips=("col", "FIPS_5digit"), value="Housing Score", transform=_as_is),
        "Health and Quality of Life": dict(
            path=os.path.join(REPO_ROOT, "code", "Health and Quality of Life",
                              "Health and Quality of Life Score by County.csv"),
            fips=("col", "FIPS"), value="Health and Quality of Life Score",
            transform=_as_is),
        "Mobility and Infrastructure": dict(
            path=mobility_src, fips=("state_county", "state", "county"),
            value="commute_burden_index", transform=_invert_100),
        "Social Capital and Community": dict(
            path=social_src,
            fips=("positional", SOCIAL_FIPS_SIBLING, "county"),
            value="economic_connectedness_index", transform=_as_is),
        "Food, Water, Amenities": dict(
            path=os.path.join(REPO_ROOT, "code", "Food Water and Amenities",
                              "Final Food, Water and Amenities Score.csv"),
            fips=("col", "FIPS"), value="Food, Water and Amenities Score",
            transform=_as_is),
    }


def _load_dimension(name, spec):
    df = pd.read_csv(spec["path"])
    kind = spec["fips"][0]
    if kind == "col":
        fips = df[spec["fips"][1]].map(clean_fips)
    elif kind == "state_county":
        fips = _fips_from_state_county(df, spec["fips"][1], spec["fips"][2])
    elif kind == "positional":
        sibling = pd.read_csv(spec["fips"][1])
        if len(sibling) != len(df):
            raise ValueError(
                f"{name}: positional FIPS needs equal length "
                f"({len(df)} vs sibling {len(sibling)})")
        fips = sibling[spec["fips"][2]].map(clean_fips).tolist()
    else:
        raise ValueError(f"{name}: unknown fips kind {kind}")
    values = pd.to_numeric(df[spec["value"]], errors="coerce")
    out = pd.DataFrame({"fips": fips, name: spec["transform"](values)})
    return out.dropna(subset=["fips"]).drop_duplicates(subset=["fips"])


def _financial_names():
    df = pd.read_csv(FINANCIAL_SRC, usecols=["5fipscode", "State Name", "County Name"])
    base = pd.DataFrame({
        "fips": df["5fipscode"].map(clean_fips),
        "state": df["State Name"].str.title(),
        "county": df["County Name"].str.title(),
    })
    return base.dropna(subset=["fips"]).drop_duplicates(subset=["fips"])


def _population():
    """Per-county population (from the environmental source), keyed by FIPS."""
    path = os.path.join(REPO_ROOT, "data", "environmental_ranking.csv")
    df = pd.read_csv(path, usecols=["FIPS", "Population"])
    out = pd.DataFrame({
        "fips": df["FIPS"].map(clean_fips),
        "population": pd.to_numeric(df["Population"], errors="coerce"),
    })
    return out.dropna(subset=["fips"]).drop_duplicates(subset=["fips"])


def build(mobility_src, social_src, out_path="dimension_scores.csv"):
    merged = _financial_names()
    dim_specs = specs(mobility_src, social_src)
    for name in DIMENSIONS:  # preserve dashboard column order
        merged = merged.merge(_load_dimension(name, dim_specs[name]),
                              on="fips", how="left")
    # Population + its national percentile (0-100), for the "favor populous
    # areas" blend in the dashboard.
    merged = merged.merge(_population(), on="fips", how="left")
    # National population percentile (0-100). Counties missing population (e.g.
    # some Alaska boroughs) get the neutral median (50) so the "favor populous"
    # blend neither boosts nor penalizes them.
    merged["population_score"] = (merged["population"].rank(pct=True) * 100).fillna(50.0)
    cols = ["fips", "state", "county"] + DIMENSIONS + ["population", "population_score"]
    merged = merged[cols].reset_index(drop=True)
    merged.to_csv(out_path, index=False)
    return merged


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mobility",
                        default=os.path.join(CLAUDE, "MobilityData_with_index.csv"))
    parser.add_argument("--social",
                        default=os.path.join(CLAUDE, "SocialCapitalData_with_index.csv"))
    parser.add_argument("--out", default="dimension_scores.csv")
    args = parser.parse_args()
    result = build(args.mobility, args.social, args.out)
    print(f"wrote {args.out}: {len(result)} counties")
    for name in DIMENSIONS:
        s = result[name]
        print(f"  {name:32s} coverage={s.notna().mean()*100:5.1f}%  "
              f"min={s.min():6.2f} max={s.max():6.2f} mean={s.mean():6.2f}")
