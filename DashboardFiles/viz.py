import plotly.express as px


def build_map(df, zoom_to_data=False):
    """US-counties choropleth colored by `score` (RdYlGn).

    With zoom_to_data=True the view fits the counties present in `df` (used when
    the table is filtered to specific states); otherwise it shows the whole US."""
    fig = px.choropleth(
        df,
        geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
        locations="fips",
        color="score",
        color_continuous_scale="RdYlGn",
        range_color=(0, 100),
        scope=None if zoom_to_data else "usa",
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
    if zoom_to_data:
        fig.update_geos(fitbounds="locations", visible=True)
    return fig
