# Customizable County Relocation Ranking

A county-level decision-support tool for comparing U.S. counties based on several factors and user preferences. Instead of producing one fixed “best places to live” ranking, this project creates interpretable category scores and lets users adjust category weights in an interactive Streamlit app.

**Web app:** https://sustainabilitydashboard.streamlit.app/

## Research Question

Main question: What counties look historically strongest for relocation once we account for multiple sustainability categories and user preferences?

## Unit of Analysis

- U.S. counties
- County FIPS codes are used as the main merge key across datasets.

## Categories

The final scoring framework uses eight categories:

1. Food, Water & Amenities
2. Health & Quality of Life
3. Housing
4. Security
5. Air Pollution & Climate Risk
6. Financial Sustainability
7. Mobility & Infrastructure
8. Social Capital & Community

### Category: Food, Water & Amenities
This category captures county-level conditions related to food access, water conditions, and basic amenities.

Datasets used and sources
- County Health Rankings https://www.countyhealthrankings.org/
- USDA Food Environment https://www.ers.usda.gov/data-products/food-environment-atlas

Raw data location
- data/CountyHealthRankings/analytic_data2025_v3.csv
- data/Food Environment/StateAndCountyData.csv

Cleaned data with selected variables
- code/Food Water and Amenities/food_water_amenities.csv

EDA notebook
- code/Food Water and Amenities/Food_water_and_amenities.ipynb

Final category score output
- code/Food Water and Amenities/Final Food, Water and Amenities Score.csv
 
### Category: Health & Quality of Life
This category captures county-level health outcomes, access to care, and overall quality-of-life conditions that may matter for long-term relocation decisions.

Datasets used and sources
- County Health Rankings https://www.countyhealthrankings.org/

Raw data location
- data/CountyHealthRankings/analytic_data2025_v3.csv

Cleaned data with selected variables
- code/Health and Quality of Life/health_and_quality_of_life.csv

EDA notebook
- code/Health and Quality of Life/Health_and_quality_of_life.ipynb

Final category score output
- code/Health and Quality of Life/Health and Quality of Life Score by County.csv

### Category: Safety
This category captures county-level crime raw values and crime rates per capita.

Datasets used and sources
- FBI webpage: https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/downloads

Raw data location
- data/Security

Cleaned data with selected variables
- data/Security/crime_per_capita_wide.csv 

EDA notebook
- code/Security/Crime_EDA.ipynb

Final category score output
- code/Security/Crime_Score_by_County.csv

### Category: Housing
This category captures county-level housing and cost of living values such as monthly and annual 2 bedroom rent, median house-hold income, housing affordability, severe housing cost burden and severe housing problems

Datasets used and sources
- https://www.huduser.gov/portal/datasets/50per.html

Raw data location
- data/Housing

Cleaned data with selected variables
- data/Housing/housing_data_wide.csv 

EDA notebook
- code/Housing/Housing_EDA.ipynb

Final category score output
- code/Housing/Housing_Score_by_County.csv

### Category: Air pollution & climate risk
Captures US counties' risk level for air pollution and climate-related disasters 

Datasets used and sources
- EPA EJScreen 

Raw data location
- data/EPAEJScreen/epa_2024.csv (file too large, it is not on the repo)
- data/NRI_Table_Counties/NRI_Table_Counties.csv
- data/Food Environment/nata2014v2_national_allhi.xlsx
- data/Food Environment/nata2014v2_national_cancerrisk_by_tract_srcgrp.xlsx

Cleaned data with selected variables
- data/master_pollution_data.csv

EDA/merging notebook
- code/Merging_pollution_data.ipynb

Scoring methodology:
- code/pollution_data_ranking.ipynb

Final category score output
- data/environmental_ranking.csv

### Category: Financial Well-Being
This category captures county-level data about job access, income, employment, and debt.

Datasets used and sources
- US Census/ Neighborhood Characteristics by Tract
https://www.census.gov/programs-surveys/ces/data/public-use-data/opportunity-atlas-data-tables.html

- County Health Rankings https://www.countyhealthrankings.org/

- US Census / Employment Status for Block Groups
https://www.census.gov/data/datasets/time-series/demo/labor-force/acs-employ.html

Raw data location
- data/social_economic/nbhd_characteristics_by_census_tract.csv
- data/social_economic/nbhd_characteristics_by_census_tract.csv
- data/CountyHealthRankings/analytic_data2025_v3.csv
- data/social_economic/avg_credit_card_balance_2020_cty.csv
- data/social_economic/avg_credit_score_2020_cty.csv

Cleaned data with selected variables
- code/financial_sustainability.csv

EDA notebook
- code/financial_sustainability_analysis.ipynb

Final category score output
- code/financial_sustainability.csv


## Data Sources

The project uses publicly available county-level and census-tract-level datasets from various sources. Some datasets were originally reported at the census tract level and were aggregated to the county level. After cleaning and merging, the final analytical data covers more than 3,000 U.S. counties.

## Methodology

The scoring process follows these main steps:

1. Collect public datasets from multiple sources.
2. Harmonize all data to the county level.
3. Merge datasets using county FIPS codes.
4. Clean missing values, duplicates, inconsistent identifiers, and incompatible formats.
5. Align variable directions so higher values consistently mean better outcomes.
6. Create category scores using PCA.
7. Rescale all category scores to a common 0–100 scale.
8. Combine category scores using user-selected weights in the web app.

The overall score is calculated as a weighted average of all category scores, based on users’ priorities.

## Validation

Migration data is used as an external benchmark, not as an input to the scoring model. Individual category scores are compared with domestic, international, and total migration rates to check whether the scores show reasonable external patterns.

Overall, the category scores show weak to modest relationships with migration, often stronger for international migration than domestic migration. This is expected because relocation decisions depend on many factors, including employment, housing, family, policy, and personal preferences.

## Repository Structure

```
summer26-sustainability-of-us-cities/
│
├── README.md
├── requirements.txt
│
├── data/
│   └── raw data
│
├── code/
│   ├── Food Water and Amenities/
│   ├── Health and Quality of life/
│   ├── Housing/
│   ├── Security/
│   ├── pollution_data_EDA.ipynb
│   ├── financial_sustainability_analysis.ipynb
│   ├── Mobility_Code.ipynb
│   └── Social_Capital_Code.ipynb
│
├── DashboardFiles/
│   └── streamlit app files
│
└── deliverables/
    └── final slides and summary files
```

## Main Outputs

- Eight category-level county scores on a 0–100 scale
- Final customizable county ranking
- Interactive county heatmap
- User-adjustable category weights
- Final county score table for the web app

## Limitations

- Data sources cover different years and may use different measurement methods.
- Some variables required aggregation from census tract level to county level.
- Missingness and data availability vary by category.
- Migration data is not a perfect ground truth for relocation quality.
- User preferences are subjective, so the app is designed for exploration rather than one universal ranking.

## Future Work

- Add more recent datasets when available.
- Improve sensitivity analysis for different weighting choices.
- Compare results with additional external benchmarks.
- Extend the framework to cities or international regions.
- Add more user-facing explanations inside the web app.
