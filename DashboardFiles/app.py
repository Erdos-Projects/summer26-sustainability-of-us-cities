import streamlit as st

import data
import viz

st.set_page_config(page_title="County Sustainability", layout="wide")


@st.cache_data
def get_base_data():
    """Load the merged per-county dimension scores once; cached across reruns."""
    return data.load_data(data.DATA_PATH)


# Per-dimension "how the data was sourced and studied" text shown in each
# slider's info popover. All dimensions are on a 0-100, higher-is-better scale.
# Edit freely (Markdown supported) to expand the methodology notes.
DIMENSION_INFO = {
    "Financial Well-Being": (
        "**Score:** `stability_score` (0–100, higher = better).\n\n"
        "**Source:** `code/financial_sustainability.csv`.\n\n"
        "**Methodology:** composite of county economic indicators — "
        "unemployment, median household income, job growth/density, employment "
        "rate, and income distribution."
    ),
    "Environmental Sustainability": (
        "**Score:** inverted `Environmental_Risk_Index`, percentile-ranked to "
        "0–100 (higher = lower environmental risk).\n\n"
        "**Source:** `data/environmental_ranking.csv`.\n\n"
        "**Methodology:** air-quality / pollution risk (PM2.5, ozone, NO₂, "
        "diesel PM, traffic, RSEI air toxics). The raw index is a risk z-score "
        "(higher = worse); it is inverted and percentile-ranked across counties."
    ),
    "Safety and Crime": (
        "**Score:** `Crime Score` (0–100, higher = safer).\n\n"
        "**Source:** `code/Security/Crime_Score_by_County.csv`.\n\n"
        "**Methodology:** county crime rates (FBI offense reports), scored so "
        "higher = safer. Covers ~88% of counties."
    ),
    "Infrastructure and Community": (
        "**Score:** `social_capital_mobility_index` (0–100, higher = better).\n\n"
        "**Source:** `social_capital_mobility_index.csv`.\n\n"
        "**Methodology:** county social-capital and economic-mobility index."
    ),
    "Quality of Life": (
        "**Score:** `Health and Quality of Life Score` (0–100, higher = better)."
        "\n\n**Source:** "
        "`code/Health and Quality of Life/Health and Quality of Life Score by "
        "County.csv`.\n\n"
        "**Methodology:** county health and quality-of-life composite."
    ),
}


def _weight_key(dimension):
    return f"weight_{dimension}"


def _default_weight(dimension):
    """Default: Financial Well-Being only, so the initial map matches the
    pure stability_score view."""
    return 100 if dimension == data.FINANCIAL_DIMENSION else 0


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
