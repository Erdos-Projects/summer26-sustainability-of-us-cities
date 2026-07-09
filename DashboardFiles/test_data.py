import numpy as np
import pandas as pd

import data


def test_clean_fips_pads_to_five_digits():
    assert data.clean_fips(1001.0) == "01001"


def test_clean_fips_five_digit_code_unchanged():
    assert data.clean_fips(48201.0) == "48201"


def test_clean_fips_accepts_string_input():
    assert data.clean_fips("1001.0") == "01001"


def test_clean_fips_returns_none_for_nan():
    assert data.clean_fips(float("nan")) is None


def test_load_data_columns_and_shape():
    df = data.load_data(data.DATA_PATH)
    assert list(df.columns) == ["fips", "state", "county"] + data.DIMENSIONS
    assert len(df) == 3153
    assert df["fips"].map(len).eq(5).all()
    # Financial Well-Being is the real, fully-populated 0-100 base dimension.
    assert df[data.FINANCIAL_DIMENSION].between(0, 100).all()
    assert df[data.FINANCIAL_DIMENSION].isna().sum() == 0


def test_load_data_has_named_counties():
    df = data.load_data(data.DATA_PATH)
    row = df[df["fips"] == "01001"].iloc[0]
    assert row["state"] == "Alabama"
    assert row["county"] == "Autauga"


def test_compute_score_default_is_financial_dimension():
    df = data.load_data(data.DATA_PATH)
    scored = data.compute_score(df)
    assert "score" in scored.columns
    assert scored["score"].equals(scored[data.FINANCIAL_DIMENSION])


def test_compute_score_financial_only_matches_financial():
    df = data.load_data(data.DATA_PATH)
    scored = data.compute_score(df, {data.FINANCIAL_DIMENSION: 100})
    diff = (scored["score"] - scored[data.FINANCIAL_DIMENSION]).abs().max()
    assert diff < 1e-9


def test_compute_score_equal_weights_is_row_nanmean():
    df = data.load_data(data.DATA_PATH)
    scored = data.compute_score(df, {d: 50 for d in data.DIMENSIONS})
    # Equal weights => per-county mean over the dimensions present (skipna).
    expected = scored[data.DIMENSIONS].mean(axis=1)
    assert (scored["score"] - expected).abs().max() < 1e-9
    assert scored["score"].between(0, 100).all()


def test_compute_score_all_zero_weights_falls_back_to_financial():
    df = data.load_data(data.DATA_PATH)
    scored = data.compute_score(df, {d: 0 for d in data.DIMENSIONS})
    assert scored["score"].equals(scored[data.FINANCIAL_DIMENSION])


def _synthetic(n_rows=1):
    rows = pd.DataFrame(
        {
            "fips": [f"{i:05d}" for i in range(1, n_rows + 1)],
            "state": ["A"] * n_rows,
            "county": [f"C{i}" for i in range(n_rows)],
        }
    )
    for dimension in data.DIMENSIONS:
        rows[dimension] = 50.0
    return rows


def test_compute_score_skips_missing_dimension():
    df = _synthetic(2)
    # Row 0: one dimension missing, another raised; weight of the missing
    # dimension must drop out of the denominator.
    df.loc[0, "Safety and Crime"] = np.nan
    df.loc[0, "Environmental Sustainability"] = 100.0
    scored = data.compute_score(df, {d: 10 for d in data.DIMENSIONS})
    # Row 0 present dims: 50, 100, 50, 50 -> mean 62.5 (Safety excluded).
    assert abs(scored.loc[0, "score"] - 62.5) < 1e-9
    # Row 1 untouched: all 50 -> 50.
    assert abs(scored.loc[1, "score"] - 50.0) < 1e-9


def test_compute_score_nan_when_all_weighted_dims_missing():
    df = _synthetic(1)
    for dimension in data.DIMENSIONS:
        df.loc[0, dimension] = np.nan
    scored = data.compute_score(df, {d: 10 for d in data.DIMENSIONS})
    assert pd.isna(scored.loc[0, "score"])


def test_top_bottom_sizes_and_order():
    df = data.compute_score(data.load_data(data.DATA_PATH))
    top, bottom = data.top_bottom(df)
    assert len(top) == 5
    assert len(bottom) == 5
    assert list(top.columns) == ["county", "state", "score"]
    assert top["score"].is_monotonic_decreasing
    assert bottom["score"].is_monotonic_increasing
    assert top["score"].iloc[0] == df["score"].max()
    assert bottom["score"].iloc[0] == df["score"].min()


def test_top_bottom_excludes_nan_scores():
    scored = _synthetic(6)
    scored["score"] = [10.0, 20.0, 30.0, 40.0, 50.0, np.nan]
    top, bottom = data.top_bottom(scored, n=2)
    assert top["score"].notna().all()
    assert bottom["score"].notna().all()
    assert top["score"].tolist() == [50.0, 40.0]
    assert bottom["score"].tolist() == [10.0, 20.0]
