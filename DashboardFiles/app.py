import streamlit as st

import data
import viz

st.set_page_config(
    page_title="County Sustainability Explorer", page_icon="🌎", layout="wide"
)

# Styling tuned so everything fits in one viewport (no scrolling): a tight main
# area, compact metric cards, and an aggressively condensed sidebar so all eight
# sliders are visible at once.
st.markdown(
    """
    <style>
      .block-container {padding-top: 1.4rem; padding-bottom: 0.5rem; max-width: 100%;}
      h1 {font-weight: 800; letter-spacing: -0.5px; font-size: 1.9rem; margin-bottom: 0;}

      /* Condense the sidebar while leaving room for each slider's value bubble. */
      section[data-testid="stSidebar"] {min-width: 300px; max-width: 320px;}
      section[data-testid="stSidebar"] .block-container {padding-top: 0.25rem;}
      section[data-testid="stSidebar"] h2 {margin-top: 0; padding-top: 0;}
      section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap: 0.65rem;}
      section[data-testid="stSidebar"] [data-testid="stSlider"] label p {font-size: 0.82rem;}
      section[data-testid="stSidebar"] div[data-testid="stSliderTickBarMin"],
      section[data-testid="stSidebar"] div[data-testid="stSliderTickBarMax"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

# Emoji + short label for each dimension (used on sliders and table headers).
DIMENSION_META = {
    "Financial Well-Being": ("💰", "Financial"),
    "Air Pollution and Climate Risk": ("🌫️", "Air & Climate"),
    "Security": ("🛡️", "Security"),
    "Housing": ("🏠", "Housing"),
    "Health and Quality of Life": ("❤️", "Health & QoL"),
    "Mobility and Infrastructure": ("🚗", "Mobility"),
    "Social Capital and Community": ("🤝", "Social Capital"),
    "Food, Water, Amenities": ("🥑", "Food & Water"),
}


def _short_label(dimension):
    emoji, short = DIMENSION_META[dimension]
    return f"{emoji} {short}"


@st.cache_data
def get_base_data():
    """Load the merged per-county dimension scores once; cached across reruns."""
    return data.load_data(data.DATA_PATH)


# Per-dimension methodology shown in each slider's ⓘ help tooltip. "Current
# score" is the data feeding the dashboard today; "Considered variabless /
# Scoring rule / Fixes" come from the team's
# "Considered variabless, fixes and scoring recommendations.xlsx".
DIMENSION_INFO = {
    "Financial Well-Being": (
        "**Current score:** `stability_score` (0–100, higher = better) — "
        "composite of county income, jobs and employment.\n\n"
        "**Considered variables:** *Income* — median household income, poverty "
        "rate, income distribution; *Jobs* — employment rate, jobs within 5 mi, "
        "job growth, unemployment.\n\n"
        "**Scoring rule:** normalize each, invert the lower-is-better ones, "
        "then average."
    ),
    "Air Pollution and Climate Risk": (
        "**Current score:** inverted, percentile-ranked `Environmental_Risk_Index`"
        " (0–100, higher = lower risk).\n\n"
        "**Considered variabless:** *Air* — PM2.5, ozone, air-toxics cancer risk; "
        "*Climate/hazard* — FEMA risk & expected annual loss, drought, "
        "wildfire, flood.\n\n"
        "**Scoring rule:** average the inverted risk metrics → higher = cleaner "
        "air / lower hazard risk."
    ),
    "Security": (
        "**Current score:** `Crime Score` (0–100, higher = safer); covers ~88% "
        "of counties.\n\n"
        "**Considered variabless** (FBI crime data): violent crime, property "
        "crime; optional homicide, motor-vehicle theft.\n\n"
        "**Scoring rule:** convert to per-capita rates, invert, average."
    
    ),
    "Housing": (
        "**Current score:** `Housing Score` (0–100, higher = more affordable)."
        "\n\n**Considered variabless** (lower = better): severe housing cost "
        "burden, housing burden %, two-bedroom rent; optional energy burden.\n\n"
        "**Scoring rule:** average the inverted burden metrics."
    ),
    "Health and Quality of Life": (
        "**Current score:** `Health and Quality of Life Score` (0–100, higher = "
        "better).\n\n"
        "**Considered variabless:** quality-of-life index, life expectancy "
        "(higher = better); injury deaths (lower = better, backup).\n\n"
        "**Scoring rule:** keep positive health metrics, invert injury deaths, "
        "average."
    ),
    "Mobility and Infrastructure": (
        "**Current score:** inverted `commute_burden_index` (100 − burden; "
        "0–100, higher = easier daily life).\n\n"
        "**Considered variabless:** broadband access (higher = better); long solo "
        "commute, average commute time (lower = better).\n\n"
        "**Scoring rule:** invert commute metrics, keep broadband positive, "
        "average."
    ),
    "Social Capital and Community": (
        "**Current score:** `economic_connectedness_index` (0–100, higher = "
        "better).\n\n"
        "**Considered variabless** (higher = better): economic connectedness, "
        "social support ratio; optional volunteering, civic organizations.\n\n"
        "**Scoring rule:** normalize and average the community-strength metrics."
    ),
    "Food, Water, Amenities": (
        "**Current score:** `Food, Water and Amenities Score` (0–100, higher = "
        "better).\n\n"
        "**Considered variabless:** drinking-water violations, low food access "
        "(lower = better); recreation facilities, food hubs (higher = better)."
        "\n\n**Scoring rule:** invert violations/low-access, keep amenities "
        "positive, average."
    ),
}


def _weight_key(dimension):
    return f"weight_{dimension}"


def _default_weight(dimension):
    """Every dimension defaults to 50, so the dashboard opens on (and resets to)
    an equal blend of all eight dimensions."""
    return 50


DEFAULT_POP_WEIGHT = 50


def reset_all():
    """Reset every dynamic control on the page — the dimension weights, the
    population slider, the state filter and the search box — to defaults. Runs
    as a button on_click callback, before the widgets are re-created, so they
    pick up the reset values."""
    for dimension in data.DIMENSIONS:
        st.session_state[_weight_key(dimension)] = _default_weight(dimension)
    st.session_state["pop_weight"] = DEFAULT_POP_WEIGHT
    st.session_state["state_filter"] = []
    st.session_state["county_search"] = ""


def render_weight_sliders():
    """Render the compact dimension-weight sliders (each with a ⓘ methodology
    tooltip) and a reset button in the sidebar; return a {dimension: weight}."""
    st.sidebar.markdown("## Weights")

    weights = {}
    for dimension in data.DIMENSIONS:
        key = _weight_key(dimension)
        st.session_state.setdefault(key, _default_weight(dimension))
        st.sidebar.slider(
            _short_label(dimension), 0, 100, key=key, help=DIMENSION_INFO[dimension]
        )
        weights[dimension] = st.session_state[key]

    st.sidebar.markdown("---")
    st.session_state.setdefault("pop_weight", DEFAULT_POP_WEIGHT)
    st.sidebar.slider(
        "🏙️ Favor populous areas",
        0,
        100,
        key="pop_weight",
        help=(
            "Blends county population into the ranking so tiny counties don't "
            "dominate on noisy scores. 0 = ignore population; higher = favor "
            "more-populous counties."
        ),
    )
    return weights, st.session_state["pop_weight"]


def render_explorer(df, all_states, state_scoped):
    """Searchable, sortable table of the (already state-scoped) counties'
    per-dimension scores. The state filter is rendered here but applied upstream
    (it also drives the map); this function only applies the text search."""
    st.markdown("##### 📋 Explore every county")
    f1, f2 = st.columns(2)
    query = f1.text_input(
        "search",
        placeholder="🔎 Search county or state",
        label_visibility="collapsed",
        key="county_search",
    )
    f2.multiselect(
        "states",
        all_states,
        placeholder="Filter by state",
        label_visibility="collapsed",
        key="state_filter",
    )

    view = df
    if query:
        q = query.lower()
        view = view[
            view["county"].str.lower().str.contains(q, na=False)
            | view["state"].str.lower().str.contains(q, na=False)
        ]

    friendly = {dimension: _short_label(dimension) for dimension in data.DIMENSIONS}
    display = view.rename(
        columns={
            "county": "County",
            "state": "State",
            "population": "Population",
            "score": "Overall %ile",
            **friendly,
        }
    )
    lead = ["County", "State"]
    if "Population" in display.columns:
        lead.append("Population")
    display = display[lead + ["Overall %ile"] + list(friendly.values())].sort_values(
        "Overall %ile", ascending=False
    )

    score_cols = ["Overall %ile"] + list(friendly.values())
    # Whole-number scores with "N/A" for missing dimensions; population with
    # thousands separators. Values stay numeric underneath, so sorting is numeric.
    fmt = {col: "{:.0f}" for col in score_cols}
    if "Population" in display.columns:
        fmt["Population"] = "{:,.0f}"
    styled = display.style.format(fmt, na_rep="N/A")
    scope = "within the selected state(s)" if state_scoped else "national"
    st.caption(
        f"**Overall %ile** = {scope} percentile of the weighted composite "
        "(0–100). Dimension columns are 0–100 scores; **N/A** = no data."
    )
    st.dataframe(
        styled,
        hide_index=True,
        use_container_width=True,
        height=430,
    )


def main():
    st.title("🌎 County Sustainability Explorer")
    st.caption(
        "Blend the eight factors that matter to you and see how every U.S. "
        "county measures up."
    )
    reset_col, _ = st.columns([2, 8])
    reset_col.button("↺ Reset all", on_click=reset_all, use_container_width=True)

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

    weights, pop_weight = render_weight_sliders()
    df = data.compute_score(base, weights, pop_weight)

    # The table's state filter (rendered below) also drives the map. When one or
    # more states are selected, restrict to those states, zoom in, and re-rank
    # the percentile within the selection (state-relative instead of national).
    all_states = sorted(base["state"].dropna().unique())
    selected_states = st.session_state.get("state_filter", [])
    if selected_states:
        scoped = data.rescore_percentile(df[df["state"].isin(selected_states)])
    else:
        scoped = df

    st.plotly_chart(
        viz.build_map(scoped, zoom_to_data=bool(selected_states)),
        use_container_width=True,
    )
    render_explorer(scoped, all_states, bool(selected_states))


if __name__ == "__main__":
    main()
