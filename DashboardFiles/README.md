# County Sustainability Dashboard

Interactive US-county map colored by a weighted blend of eight 0–100 dimensions
(Financial Well-Being, Air Pollution and Climate Risk, Security, Housing,
Health and Quality of Life, Mobility and Infrastructure, Social Capital and
Community, Food, Water, Amenities). Compact sidebar weight sliders (each with a
methodology tooltip and a reset), a reactive KPI row, a full-width choropleth,
and a searchable, sortable table of every county's per-dimension scores.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Run from inside `DashboardFiles`. The app reads `dimension_scores.csv` (the
merged per-county dimension scores) from this folder.

## Rebuilding the data

`dimension_scores.csv` is produced by `build_dimensions.py`, which merges the
five source datasets on 5-digit FIPS and normalizes each to a 0–100,
higher-is-better scale (Environmental risk is inverted and percentile-ranked;
the rest are used as-is). Re-run it after any source updates, then commit the
result:

```bash
python build_dimensions.py            # uses the default source paths
python build_dimensions.py --infra /path/to/social_capital_mobility_index.csv
```

Note: the infrastructure source currently lives outside the repo; pass
`--infra` if it has moved.

## Test

```bash
pytest -v
```
