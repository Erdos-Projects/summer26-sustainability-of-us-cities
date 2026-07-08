import data
import viz


def test_build_map_returns_figure_with_one_trace():
    df = data.compute_score(data.load_data(data.DATA_PATH))
    fig = viz.build_map(df)
    # One choropleth trace covering all rows.
    assert len(fig.data) == 1
    assert fig.data[0].type == "choropleth"
    assert len(fig.data[0].locations) == len(df)


def test_build_map_visual_properties():
    df = data.compute_score(data.load_data(data.DATA_PATH))
    fig = viz.build_map(df)

    # 1. Map scope is USA.
    assert fig.layout.geo.scope == "usa"

    # 2. Color range anchored to 0–100.
    assert fig.layout.coloraxis.cmin == 0
    assert fig.layout.coloraxis.cmax == 100

    # 3. RdYlGn color scale is applied: non-empty and spans the full [0, 1] range.
    colorscale = fig.layout.coloraxis.colorscale
    assert colorscale and len(colorscale) > 0
    assert colorscale[0][0] == 0.0   # scale starts at position 0
    assert colorscale[-1][0] == 1.0  # scale ends at position 1

    # 4. Hover template exposes the state field.
    assert "state" in fig.data[0].hovertemplate
