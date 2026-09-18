# Economic Input-Output Model

**Exploring how industries connect—and what those connections reveal about regional economies.**

Rutgers University · CS 439 · December 2025

**1st place among 30+ teams in a coursewide competition · Presented to 200+ students**

This team project turns decades of World Input-Output Database (WIOD) transactions into country-year datasets, visualizes sector relationships, and uses Leontief inverse matrices as features for machine learning. We investigated whether economic structure distinguishes geographic regions and whether those patterns persist in later years.

**25 countries · 23 sectors · 1965–2000 · Python / Pandas / NumPy / scikit-learn / Matplotlib / Seaborn**

[Explore the notebook](econ_input_output.ipynb) · [Read the presentation](Economic%20Input-Output%20Model.pdf) · [Results & methodology](docs/methodology.md) · [Setup & reproduction](docs/reproduction.md)

## A look inside

![China's 2000 interindustry transactions, with producing sectors on rows and consuming sectors on columns](docs/images/sector-heatmap.png)

*An original notebook output from the interactive country/year query: China, 2000. Flows are shown in billions of current US dollars; the fixed color scale saturates at 50 billion.*

## My contribution

I'm **[Ryan Vukicevic](https://github.com/RyanVukicevic)**. I led our three-person team and focused on making the economic data usable, interpretable, and explorable:

- **Data cleaning and restructuring:** transformed the wide WIOD transaction tables into standardized country-year datasets, mapped sector codes to readable names, and organized the data for analysis.
- **Visual analysis:** developed heatmaps and bar charts to communicate intersectoral flows and sector-level summaries.
- **Interactive exploration:** built notebook prompts that let viewers select a country and year to query the data and display visualizations.
- **ML guidance:** advised the team's choice of algorithms for regional classification, dimensionality reduction, and clustering.

The modeling results below are **team outcomes**. The project was completed with **Lawrence Ho** and **Paolo Gervasoni**; see [team credits](docs/credits.md).

## What we built

```mermaid
flowchart LR
    A[WIOD transaction tables] --> B[Clean and label country-year data]
    B --> C[Interactive heatmaps and sector charts]
    B --> D[Leontief inverse matrices]
    D --> E[529 features per country-year]
    E --> F[KNN and decision trees]
    E --> G[PCA and K-means]
    F --> H[Regional classification and later-year evaluation]
    G --> I[Structure and class-imbalance analysis]
```

The economic model relates total output **x**, intermediate input coefficients **A**, and final demand **y**:

$$x = Ax + y, \qquad L = (I-A)^{-1}, \qquad x = Ly$$

Each 23 × 23 Leontief matrix becomes a 529-feature representation of a country's sector relationships. The team compared three regional labels—Europe, Asia-Pacific, and Americas—and explored alternative East/West groupings.

## Selected findings

The following are **results reported in the original presentation**, not newly reproduced benchmarks.

| Experiment | Reported test accuracy | Evaluation |
| --- | ---: | --- |
| KNN, full Leontief features | **94.8%** | Train on 1965–1990; evaluate on 1991–2000 |
| KNN with 7-component PCA | **86.4%** | Same year-based split |
| Decision tree | **98.3%** | Random 80/20 split across country-year observations |

- **Later-year classification retained useful signal.** KNN classified regional labels from later economic structures with 94.8% reported accuracy. This measures classification of observed later-year matrices, not forecasting future output or GDP.
- **Compression had a measurable tradeoff.** The PCA variant reduced temporal test accuracy by **8.4 percentage points**, suggesting that the retained components did not preserve all useful classification information in this experiment.
- **Clustering exposed a different challenge.** K-means did not recover the three geographic regions cleanly; larger classes dominated many assignments. Region coverage was uneven: 14 European, 7 Asia-Pacific, and 4 Americas countries.

Random splits include repeated observations of the same countries, and some original preprocessing occurs before splitting. The original clustering code also refits on evaluation data in its subset experiments. These results are exploratory; [methodology notes](docs/methodology.md) explain the evaluation limits and an identified matrix-construction issue.

## Explore the project

**No setup needed:** open the [52-slide presentation](Economic%20Input-Output%20Model.pdf) for the complete story or browse the [notebook](econ_input_output.ipynb) for the implementation and saved visual outputs.

| Interested in… | Start here |
| --- | --- |
| Data preparation | Notebook: **Data Prepreparation → Sector Mapping → Subsetting by Country** |
| My interactive visualizations | Notebook: **Heatmap**, **Leontief**, and **Interactive Demo Functions** |
| Model comparison | Presentation, slides **19–39** |
| Later-year evaluation | Presentation, slides **26–30** |
| Class imbalance and alternative labels | Presentation, slides **40–49** |
| Technical details and limitations | [Methodology](docs/methodology.md) |

The original notebook ran in Google Colab with data stored in Google Drive. The raw CSV and precomputed matrix cache are not included, so this repository currently supports **browsing the original work**, while a complete rerun requires restoring those inputs and addressing the documented setup issues. See [reproduction instructions](docs/reproduction.md).

<details>
<summary><strong>More original visualizations: demand trends and regional coverage</strong></summary>

![Final-demand component trends for the 25 countries](docs/images/final-demand-trends.png)

*The notebook summarizes demand components across sector rows for each country and year. Values are nominal; these curves are not inflation-adjusted growth estimates.*

![Country counts by region: Europe 14, Asia-Pacific 7, Americas 4](docs/images/regional-coverage.png)

*Regional coverage provides context for the class-imbalance analysis.*

</details>

## Repository guide

```text
econ_input_output.ipynb          Original team notebook and saved outputs
econ_input_output.py             Original Colab Python export
Economic Input-Output Model.pdf  Original team presentation
requirements.txt                Analysis dependencies for restoring the environment
docs/
  methodology.md                Results, experiment design, and limitations
  reproduction.md               Data requirements and execution notes
  credits.md                    Contributions and source attribution
  images/                       Figures extracted from saved notebook outputs
```

## Data and acknowledgments

Data: [Long-run WIOD, University of Groningen](https://www.rug.nl/ggdc/valuechain/long-run-wiod), version 1.1. The source covers 1965–2000, including 25 countries and a rest-of-world category. Our analysis selects domestic country blocks and excludes rest-of-world and total rows.

Required data attribution: Woltjer, P., Gouma, R., and Timmer, M. P. (2021), *Long-run World Input-Output Database: Version 1.1 Sources and Methods*, GGDC Research Memorandum 190. [Dataset DOI](https://doi.org/10.34894/A7AXDN).

The original notebook, export, and presentation are preserved as course-project artifacts. Portfolio documentation and extracted figure previews were added afterward. Competition placement and audience size are reported by Ryan; the repository does not contain separate award documentation. Dataset terms and team attribution are detailed in [credits](docs/credits.md).
