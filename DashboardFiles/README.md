# County Financial Stability Dashboard

Interactive map of US counties colored by `stability_score`, with Top 5 and
Bottom 5 county tables.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

The app reads `financial_sustainability.csv`, which lives alongside `app.py` in this folder. Run the commands from inside `DashboardFiles`.

## Test

```bash
pytest -v
```
