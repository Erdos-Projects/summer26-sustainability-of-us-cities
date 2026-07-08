import data


def test_clean_fips_pads_to_five_digits():
    assert data.clean_fips(1001.0) == "01001"


def test_clean_fips_five_digit_code_unchanged():
    assert data.clean_fips(48201.0) == "48201"


def test_clean_fips_accepts_string_input():
    assert data.clean_fips("1001.0") == "01001"


def test_clean_fips_returns_none_for_nan():
    assert data.clean_fips(float("nan")) is None


def test_load_data_shape_and_columns():
    df = data.load_data(data.DATA_PATH)
    assert list(df.columns) == ["fips", "stability_score", "state", "county"]
    # 3154 rows in source, 1 has a null FIPS and is dropped.
    assert len(df) == 3153
    assert df["fips"].map(len).eq(5).all()
    assert df["stability_score"].isna().sum() == 0


def test_load_data_titlecases_names():
    df = data.load_data(data.DATA_PATH)
    row = df[df["fips"] == "01001"].iloc[0]
    assert row["state"] == "Alabama"
    assert row["county"] == "Autauga"


def test_compute_score_is_stability_score():
    df = data.load_data(data.DATA_PATH)
    scored = data.compute_score(df)
    assert "score" in scored.columns
    assert scored["score"].equals(scored["stability_score"])


def test_add_dimension_scores_present_and_financial_scaled():
    df = data.add_dimension_scores(data.load_data(data.DATA_PATH))
    for dimension in data.DIMENSIONS:
        assert dimension in df.columns
        assert df[dimension].notna().all()
    # Financial Well-Being is the real, 0-100 stability_score.
    assert df[data.FINANCIAL_DIMENSION].between(0, 100).all()


def test_financial_dimension_equals_stability_score():
    df = data.add_dimension_scores(data.load_data(data.DATA_PATH))
    assert df[data.FINANCIAL_DIMENSION].equals(df["stability_score"])


def test_placeholder_dimensions_are_deterministic():
    base = data.load_data(data.DATA_PATH)
    first = data.add_dimension_scores(base)
    second = data.add_dimension_scores(base)
    for dimension in data.PLACEHOLDER_DIMENSIONS:
        assert first[dimension].equals(second[dimension])


def test_compute_score_financial_only_matches_stability():
    base = data.load_data(data.DATA_PATH)
    scored = data.compute_score(base, {data.FINANCIAL_DIMENSION: 100})
    assert (scored["score"] - scored["stability_score"]).abs().max() < 1e-9


def test_compute_score_equal_weights_is_mean_of_dimensions():
    base = data.load_data(data.DATA_PATH)
    scored = data.compute_score(base, {d: 50 for d in data.DIMENSIONS})
    expected = scored[data.DIMENSIONS].mean(axis=1)
    assert (scored["score"] - expected).abs().max() < 1e-9


def test_compute_score_all_zero_weights_falls_back_to_stability():
    base = data.load_data(data.DATA_PATH)
    scored = data.compute_score(base, {d: 0 for d in data.DIMENSIONS})
    assert scored["score"].equals(scored["stability_score"])


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
