### Erdos Institute Summer 2026 
### Data Science Project

&#9989; <font color=blue> <font color=blue> **Customizable County Relocation Ranking: A Data-Driven Framework for Personalized Sustainability Decisions**
By Gabriel Collado, Nkechi Nnadi, Shyam Ravichandran, Hazal Sena Aydogdu, & Laila Shaaban

#### Project Overview
Relocating to a new community is one of the most consequential personal and economic decisions individuals make. Existing "Best Places to Live" rankings typically assume that every person values the same characteristics, producing a single universal ranking even though relocation decisions are inherently subjective. Our project addresses this challenge by developing a customizable county-level relocation ranking system that allows users to prioritize the factors that matter most to them. Rather than producing one fixed ranking of U.S. counties, our framework combines diverse sustainability and quality-of-life indicators into interpretable category scores that users can weight according to their own preferences. The [resulting interactive application](https://sustainabilitydashboard.streamlit.app/) generates personalized rankings together with a nationwide heatmap for visual comparison.
 [Web App:](https://sustainabilitydashboard.streamlit.app/)

#### Data Integration
The project integrates publicly available county-level datasets covering multiple aspects of sustainability and quality of life. Data sources include the U. S. Environmental Protection Agency (EPA) and the Federal Emergency Management Agency (FEMA), the USDA Food Environment Atlas, the FBI Crime Data Explorer, the Opportunity Insights website, the CDC, and the Climate and Economic Screening Tool (CEJST). After cleaning and validation, the final datasets contain more than 3,000 U.S. counties, each represented by a comprehensive collection of standardized indicators spanning **eight (8)** major categories of sustainability:
- Food, Water & Amenities
- Health & Quality of Life
- Housing
- Security
- Air Pollution & Climate Risk
- Financial Sustainability
- Mobility & Infrastructure
- Social Capital & Community

Our data integration pipeline consisted of the following steps:
1. *Collect data from multiple public sources*. We assembled county- and census tract-level datasets from federal agencies, including EPA EJSCREEN environmental indicators, FEMA's National Risk Index, health risk datasets, housing and demographic statistics, transportation measures, food access indicators, and other sustainability metrics.
2. *Harmonize geographic units*. Since several datasets were reported at the census tract level while others were reported at the county level, all variables were converted to a common county-level unit of analysis. 
3. *Merge datasets*. County FIPS codes served as the primary key for integrating all data sources into a single analytical table. Careful verification ensured that counties were matched consistently across datasets.
4. *Clean and validate the integrated data*. Duplicate counties, territorial observations, inconsistent identifiers, missing values, and incompatible variable formats were identified and addressed. Variables measured on different numerical scales were standardized, and indicator directions were aligned so that higher values consistently represented more desirable outcomes.
5. *Construct the analytical dataset*. The resulting dataset contains over 3,000 U.S. counties, each represented by a comprehensive set of indicators in each category. These unified datasets serve as the foundation for the feature engineering, scoring model, and interactive relocation ranking.

#### Methodology
Many variables within each category measure similar underlying concepts and exhibit strong correlations. Simply averaging all variables would therefore overweight redundant information and reduce interpretability.
To address this issue, we performed exploratory data analysis using correlation matrices and applied Principal Component Analysis (PCA) independently within each category. PCA reduces correlated variables into a smaller number of orthogonal components while preserving most of the variation present in the original data.

To transform hundreds of heterogeneous county-level measurements into interpretable sustainability scores, we developed a feature-engineering pipeline as follows: 
Aggregate and clean data. Certain data measurements were originally available at the census tract level and were aggregated to county-level values using population-weighted averages. Missing values, duplicate counties, inconsistent identifiers, and differing measurement scales were addressed to create a unified county-level dataset.
Select variables. Variables within each category were selected using domain knowledge, data availability, and exploratory data analysis. Correlation matrices and variance inflation factors (VIFs) were used to identify redundancy and multicollinearity within each category.
Align variable directions. Variables were transformed so that higher values consistently represented more desirable outcomes. For example, indicators measuring pollution, hazard, or disease burden were reverse coded before constructing category scores.
Reduce redundancy where appropriate. Rather than applying Principal Component Analysis (PCA) indiscriminately, we used it selectively for categories exhibiting substantial multicollinearity. For instance, in the Air Pollution & Climate Risk category, strongly correlated EPA pollutant variables were summarized using a weighted combination of the first three principal components, which together explained approximately 76% of the total variance. This approach captured multiple dimensions of environmental quality while substantially reducing redundancy. In contrast, categories whose variables measured complementary rather than redundant concepts, such as health risk metrics and FEMA National Risk Index measures, were represented using standardized composite scores or existing validated indices instead of PCA.
Construct category scores. Each sustainability category was represented by a single interpretable score derived from either PCA-based dimensionality reduction or standardized composite scoring, depending on the statistical characteristics of the underlying variables.
Normalize scores. All category scores were rescaled to a common 0–100 range, allowing direct comparison across categories and enabling users to assign personalized weights when generating county rankings.
This feature engineering strategy produced standardized, interpretable, and statistically robust category scores while preserving the distinct information contained within each sustainability dimension. The resulting framework forms the foundation of our customizable relocation ranking application.

#### Validation and Findings
Rather than validating against a predefined "correct" ranking, we evaluated whether the category scores exhibit reasonable relationships with observed migration patterns. Migration data were used solely as an external benchmark, not as an input to the ranking model.
The analysis revealed generally weak to modest correlations between individual category scores and migration rates. While no single category fully explains migration decisions, several categories demonstrated meaningful positive trends, particularly with international migration. These findings are consistent with the complex nature of relocation decisions, which depend on employment opportunities, family considerations, housing markets, public policy, and personal preferences in addition to quality-of-life measures.
#### Impact and Future Work
The primary contribution of this project is a transparent, customizable decision-support framework rather than another fixed "best counties" list. By separating sustainability into interpretable categories and allowing user-defined weighting, the framework accommodates diverse relocation priorities while remaining easy to understand and modify. Essentially, we developed a reproducible data pipeline that integrates heterogeneous public datasets into standardized sustainability scores and an interactive relocation-ranking application that enables personalized county comparisons across the United States.
Future work includes incorporating more recent datasets, performing sensitivity analyses on weighting strategies, validating against additional external benchmarks, and extending the methodology to cities and international regions. The framework could also support planners, policymakers, employers, and organizations interested in comparing communities under different sustainability objectives.
Ultimately, this project demonstrates how data integration, dimensionality reduction, and interpretable scoring methods can transform complex public datasets into a flexible tool for evidence-based relocation and community comparison.

