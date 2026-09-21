# Run the project locally

Place `lr_wiod_wiot_wide.csv` beside `economic_structure_classification_model.ipynb`. The notebook reads this local file directly; no Google Drive account or precomputed pickle is needed.

## Setup

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Execute the complete notebook

```bash
python run_notebook.py
```

The runner starts a fresh kernel with the same Python environment, executes every code cell, saves the notebook with its new charts/results, and writes `outputs/run_summary.json`. It fails on the first error and saves a diagnostic notebook under `outputs/failed-notebook.ipynb` rather than reporting a partial execution as successful.

Alternatively, open the notebook in JupyterLab and use **Restart Kernel and Run All Cells**:

```bash
python -m jupyterlab economic_structure_classification_model.ipynb
```

The notebook's working directory must be this repository. Select the environment where you installed the dependencies. The final demo cells supply example country/year values so a complete execution never waits for input.

The synchronized Python export also supports:

```bash
python economic_structure_classification_model.py
```

This displays figures through your Matplotlib backend. For unattended script execution, set `MPLBACKEND=Agg` in your shell; the notebook runner already uses an inline backend.

## Inputs and generated files

| File | Purpose |
| --- | --- |
| `lr_wiod_wiot_wide.csv` | Local WIOD input; excluded from Git because of its size |
| `L_matrix_dict.pkl` | Rebuilt on every execution from the CSV: 900 country-year matrices with numeric arrays and labeled dataframes |
| `outputs/run_summary.json` | Completed-run record, data SHA-256, package versions, and printed metrics |
| `outputs/region_count_barplot.pdf` | Regional coverage figure |
| `outputs/knn_results_per_year.png` | Tuning curves for every year |
| `economic_structure_classification_model.ipynb` | Executed analysis, visualizations, and saved results |

The cache is generated locally and never loaded from an external pickle. Country-year blocks are checked for 23 aligned sectors, finite values, positive gross output, and consistency of the input-output and inverse identities. Modeling still has the limitations described in [methodology](methodology.md).

## Query a country and year

After running the notebook, use:

```python
heatmap("CHN", 2000)
leontief("USA", 2000)
heatmap_demo()                  # Interactive country/year prompts
leontief_demo()                 # Interactive country/year prompts
heatmap_demo("GBR", 1990)       # Equivalent nonblocking query
```

Use a three-letter country code from the dataset and a year from 1965 through 2000. Invalid queries raise a clear error.

## Obtain the data on another computer

Download **WIOTs in current prices ? Excel** from the official [Long-run WIOD page](https://www.rug.nl/ggdc/valuechain/long-run-wiod). Convert the third sheet of `lr_wiod_wiot_wide.xlsx` using:

```bash
xlsx2csv -s 3 lr_wiod_wiot_wide.xlsx lr_wiod_wiot_wide.csv
```

Check the header for `year`, `row_country`, `row_isic3`, country-prefixed industry and final-demand columns, and `xTOT_xGO` (reported gross output). The project uses Long-run WIOD version 1.1, not the separate WIOD 2016 release. Attribute the dataset as described in [credits](credits.md).

## Generate the raw-dollar chart previews

```bash
python raw_sector_visualizations.py --country USA --year 2000
```

This runs independently of the ML notebook. It reads the same local CSV and writes four charts and their underlying tables to `outputs/raw-sector-preview/`: a country/year average chart and pooled producer, consumer, and combined rankings for all 25 countries over 1965-2000. The README displays the three pooled rankings and notebook heatmap queries for USA, China, and Germany in 2000. The country/year averages chart remains a local query output. To regenerate all six README images directly in `docs/images/`, run `python docs/render_showcase.py`. Pooled charts display trillions of current USD; the country/year chart and exported tables use billions.

In a notebook, use the new raw-data query without running the classification experiments:

```python
from raw_sector_visualizations import load_panel, raw_flow_demo, plot_pooled
panel = load_panel()
raw_flow_demo(panel)  # Prompts for country/year
# Or: raw_flow_demo(panel, country="USA", year=2000)
```

The original `leontief_demo()` still shows unitless coefficients; `raw_flow_demo()` shows monetary transactions. Each name retains its distinct meaning.

## Historical artifacts

The presentation file has the new project name; its slides retain the original course title and results as a historical artifact. The original notebook and Python export are available in [the initial showcase commit](https://github.com/RyanVukicevic/Economic-Structure-Classification-Model/tree/1fc6abf). The current versions include local execution fixes and corrected matrix/clustering calculations, so their results need not match the slides.

Four previews in `docs/images/` are historical PNG outputs extracted from the original notebook (zero-based cells 16, 18, 138, and 140). Newly executed figures are available within the current notebook; the original sector-score image can have an incorrect country label because of the old global-variable issue.

The `heatmap-usa-2000.png`, `heatmap-chn-2000.png`, and `heatmap-deu-2000.png` previews are regenerated by `docs/render_showcase.py`, which executes the notebook preparation cells and calls its `heatmap()` function. Only display styling changes; each plotted matrix is checked against the original domestic CSV block. The older `current-sector-heatmap.png` is no longer embedded in the README. The unused `current-sector-linkages.png` preview was extracted from the successful local notebook rerun; the README no longer displays the Leontief averages chart. The latest full run executed 81 code cells with zero errors in 214.25 seconds and saved 54 charts.
