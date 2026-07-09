import streamlit as st

import data
import viz

st.set_page_config(page_title="County Sustainability", layout="wide")


@st.cache_data
def get_base_data():
    """Load the merged per-county dimension scores once; cached across reruns."""
    return data.load_data(data.DATA_PATH)


# Per-dimension info shown in each slider's popover. "Current score" describes
# the data feeding the dashboard today; "Suggested variables / Scoring rule /
# Fixes" are drawn from the team's
# "Suggested variables, fixes and scoring recommendations.xlsx".
# All dimensions are on a 0-100, higher-is-better scale. Edit freely (Markdown).
DIMENSION_INFO = {
    "Financial Well-Being": (
        "**Current score:** `stability_score` (0–100, higher = better) — "
        "composite of county income, jobs and employment "
        "(`code/financial_sustainability.csv`).\n\n"
        "**Suggested variables:**\n"
        "- *Income:* higher = better — median household income, % households "
        "> $200k; lower = better — poverty rate, % households < $30k.\n"
        "- *Jobs:* higher = better — employment rate, jobs within 5 mi, annual "
        "job growth; lower = better — unemployment rate.\n"
        "- *Housing / cost of living:* lower = better — severe housing cost "
        "burden, housing burden %, two-bedroom rent, energy burden.\n\n"
        "**Scoring rule:** normalize each variable, invert the lower-is-better "
        "ones, then average."
    ),
    "Environmental Sustainability": (
        "**Current score:** inverted, percentile-ranked `Environmental_Risk_Index`"
        " (0–100, higher = lower risk) — air pollution / toxics "
        "(`data/environmental_ranking.csv`).\n\n"
        "**Suggested variables:**\n"
        "- *Air & pollution (lower = better):* PM2.5, ozone, air-toxics cancer "
        "risk; optional traffic proximity, wastewater discharge.\n"
        "- *Climate & hazard risk (lower = better):* FEMA overall risk & "
        "expected annual loss, drought, wildfire, flood; optional hurricane.\n\n"
        "**Scoring rule:** normalize each, average the inverted risk metrics → "
        "higher = cleaner air / lower hazard risk.\n\n"
        "**Fixes:** use a single PM2.5 source; consider adding NOAA "
        "climate-trend variables (extreme-heat days, temperature/precipitation "
        "trend)."
    ),
    "Safety and Crime": (
        "**Current score:** `Crime Score` (0–100, higher = safer) "
        "(`code/Security/Crime_Score_by_County.csv`); covers ~88% of counties."
        "\n\n"
        "**Suggested variables** (FBI crime data, lower = better): violent "
        "crime, property crime; optional homicide, motor-vehicle theft.\n\n"
        "**Scoring rule:** convert counts to per-capita rates, invert, and "
        "average → higher = safer.\n\n"
        "**Fix:** always use per-capita rates — raw counts penalize larger "
        "counties."
    ),
    "Infrastructure and Community": (
        "**Current score:** `social_capital_mobility_index` (0–100, higher = "
        "better) (`social_capital_mobility_index.csv`).\n\n"
        "**Suggested variables:**\n"
        "- *Mobility & infrastructure:* higher = better — broadband access; "
        "lower = better — long solo commute, average commute time (population "
        "density is context only).\n"
        "- *Social capital & community (higher = better):* economic "
        "connectedness, social support ratio; optional volunteering rate, "
        "civic organizations, childhood economic connectedness.\n\n"
        "**Scoring rule:** invert commute metrics, keep broadband and social "
        "metrics positive, normalize and average."
    ),
    "Quality of Life": (
        "**Current score:** `Health and Quality of Life Score` (0–100, higher = "
        "better) (`code/Health and Quality of Life/…Score by County.csv`).\n\n"
        "**Suggested variables:**\n"
        "- *Health & QoL:* higher = better — quality-of-life index, life "
        "expectancy; lower = better — injury deaths (backup).\n"
        "- *Water, food & amenities:* lower = better — drinking-water "
        "violations, low food access; higher = better — recreation/fitness "
        "facilities, food hubs.\n\n"
        "**Scoring rule:** keep positive health/livability metrics, invert "
        "burdens and violations, normalize and average.\n\n"
        "**Note:** don’t use `QOL_index` as both an input and the target if "
        "building a custom score."
    ),
}


def _weight_key(dimension):
    return f"weight_{dimension}"


def _default_weight(dimension):
    """Default: every dimension weighted 50, so the initial map (and the reset
    button) shows an equal blend of all five dimensions."""
    return 50


def reset_weights():
    """Reset every slider to its default. Runs as a button on_click callback,
    before the sliders are re-rendered, so the widgets pick up the new values."""
    for dimension in data.DIMENSIONS:
        st.session_state[_weight_key(dimension)] = _default_weight(dimension)


def render_weight_sliders():
    """Render the five dimension-weight sliders (each with an info popover) and
    a reset button in the sidebar, and return a {dimension: weight} dict."""
    st.sidebar.header("Dimension weights")
    st.sidebar.caption(
        "Blend the five dimensions into the ranking. Each is a 0–100 "
        "(higher = better) county score; see each dimension's info for source "
        "and methodology."
    )
    st.sidebar.button(
        "Reset to defaults", on_click=reset_weights, use_container_width=True
    )

    weights = {}
    for dimension in data.DIMENSIONS:
        key = _weight_key(dimension)
        st.session_state.setdefault(key, _default_weight(dimension))
        st.sidebar.slider(dimension, 0, 100, key=key)
        with st.sidebar.popover("ℹ️ Data & methodology", use_container_width=True):
            st.markdown(f"**{dimension}**")
            st.markdown(DIMENSION_INFO[dimension])
        weights[dimension] = st.session_state[key]
    return weights


def render_table(title, table):
    st.subheader(title)
    display = table.rename(
        columns={"county": "County", "state": "State", "score": "Score"}
    )
    display["Score"] = display["Score"].round(2)
    st.dataframe(display, hide_index=True, use_container_width=True)


def main():
    st.title("County Sustainability Dashboard")

    try:
        base = get_base_data()
    except FileNotFoundError:
        st.error(f"Data file not found at '{data.DATA_PATH}'.")
        return
    except ValueError as err:
        st.error(f"Could not read data: {err}")
        return

    if base.empty:
        st.warning("No county data available to display.")
        return

    weights = render_weight_sliders()
    df = data.compute_score(base, weights)

    map_col, table_col = st.columns([3, 1])

    with map_col:
        st.plotly_chart(viz.build_map(df), use_container_width=True)

    with table_col:
        top, bottom = data.top_bottom(df)
        render_table("Top 5", top)
        render_table("Bottom 5", bottom)


if __name__ == "__main__":
    main()
