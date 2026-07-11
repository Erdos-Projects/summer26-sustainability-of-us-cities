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
        hover_data={"state": True, "score": ":.0f", "fips": False},
        labels={"score": "Percentile"},
    )
    fig.update_layout(
        height=480,
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        geo={"bgcolor": "rgba(0,0,0,0)", "lakecolor": "rgba(0,0,0,0)"},
        paper_bgcolor="rgba(0,0,0,0)",
        coloraxis_colorbar={"title": "Percentile", "thickness": 12},
    )
    return fig
