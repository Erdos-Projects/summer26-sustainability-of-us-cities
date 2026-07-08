import streamlit as st

import data
import viz

st.set_page_config(page_title="County Financial Stability", layout="wide")


@st.cache_data
def get_base_data():
    """Load and attach dimension columns once; cached across reruns."""
    return data.add_dimension_scores(data.load_data(data.DATA_PATH))


# Per-dimension "how the data was sourced and studied" text shown in each
# slider's info popover. Replace the placeholders with real methodology notes
# (Markdown is supported).
DIMENSION_INFO = {
    "Financial Well-Being": (
        "_Currently the real `stability_score` (0-100)._\n\n"
        "**Source:** _TODO_\n\n"
        "**Methodology:** _TODO — how the data was sourced and studied._"
    ),
    "Environmental Sustainability": (
        "_Placeholder data until real values are supplied._\n\n"
        "**Source:** _TODO_\n\n"
        "**Methodology:** _TODO — how the data was sourced and studied._"
    ),
    "Safety and Crime": (
        "_Placeholder data until real values are supplied._\n\n"
        "**Source:** _TODO_\n\n"
        "**Methodology:** _TODO — how the data was sourced and studied._"
    ),
    "Infrastructure and Community": (
        "_Placeholder data until real values are supplied._\n\n"
        "**Source:** _TODO_\n\n"
        "**Methodology:** _TODO — how the data was sourced and studied._"
    ),
    "Quality of Life": (
        "_Placeholder data until real values are supplied._\n\n"
        "**Source:** _TODO_\n\n"
        "**Methodology:** _TODO — how the data was sourced and studied._"
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
        "Blend the five dimensions into the ranking. Only Financial "
        "Well-Being uses real data; the others are placeholders until real "
        "per-county data is added."
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
    st.title("County Financial Stability Dashboard")

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
