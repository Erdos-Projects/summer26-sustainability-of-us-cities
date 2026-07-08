import plotly.express as px


def build_map(df):
    """US-counties choropleth colored by `score` (RdYlGn)."""
    fig = px.choropleth(
        df,
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations="fips",
        color="score",
        color_continuous_scale="RdYlGn",
        range_color=(0, 100),
        scope="usa",
        hover_name="county",
        hover_data={"state": True, "score": ":.2f", "fips": False},
        labels={"score": "Stability"},
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig
