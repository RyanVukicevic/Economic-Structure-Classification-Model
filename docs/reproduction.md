# Run the project locally

Place `lr_wiod_wiot_wide.csv` beside `econ_input_output.ipynb`. The notebook reads this local file directly; no Google Drive account or precomputed pickle is needed.

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
python -m jupyterlab econ_input_output.ipynb
```

The notebook's working directory must be this repository. Select the environment where you installed the dependencies. The final demo cells supply example country/year values so a complete execution never waits for input.

The synchronized Python export also supports:

```bash
python econ_input_output.py
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
| `econ_input_output.ipynb` | Executed analysis, visualizations, and saved results |

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

## Historical artifacts

The presentation retains the original course results. The original notebook and Python export are available in [the initial showcase commit](https://github.com/RyanVukicevic/economic-input-output-model/tree/1fc6abf). The current versions include local execution fixes and corrected matrix/clustering calculations, so their results need not match the slides.

The four files in `docs/images/` are historical PNG outputs extracted from the original notebook (zero-based cells 16, 18, 138, and 140). Newly executed figures are available within the current notebook; the original sector-score image can have an incorrect country label because of the old global-variable issue.

The `current-sector-heatmap.png` and `current-sector-linkages.png` previews were extracted from the successful local rerun. The latest full run executed 81 code cells with zero errors in 331.51 seconds and saved 54 charts.
