# Viewing and reproducing the project

## View without installing anything

Open the [presentation](../Economic%20Input-Output%20Model.pdf), [notebook](../econ_input_output.ipynb), or the figures embedded in the [README](../README.md). Saved visual outputs are included; most ML results are documented in the presentation rather than saved notebook outputs.

## Current reproducibility status

The supplied files contain the original notebook, its Colab Python export, and the presentation. They do **not** include:

- `lr_wiod_wiot_wide.csv`, the raw input used by the notebook.
- `L_matrix_dict.pkl`, the precomputed country/year Leontief matrices used by the modeling cells.
- A package lockfile or the original runtime's exact library versions.

The original analysis has not been rerun for this portfolio. The dependency list is a reconstruction from imports, not a tested recreation of the original environment. A successful `pip install` alone does not make the notebook runnable end to end.

## Restore the data

1. Visit the official [Long-run WIOD page](https://www.rug.nl/ggdc/valuechain/long-run-wiod) and download **WIOTs in current prices → Excel**. Select the long-run dataset rather than the separate 2016 WIOD release.
2. The original workflow converted the workbook's third sheet to CSV using `xlsx2csv`:

   ```bash
   xlsx2csv -s 3 lr_wiod_wiot_wide.xlsx lr_wiod_wiot_wide.csv
   ```

   Verify the sheet and resulting header against the downloaded workbook. The notebook expects `year`, `row_country`, `row_isic3`, and country-prefixed industry/final-demand columns, such as `USA_AtB` and `USA_xCONS_h`.

3. In Google Drive, place the CSV under `My Drive/CS439 Final Project/`, or edit the notebook's input path to your chosen location.
4. Restore the original trusted matrix cache if available. Its expected structure is:

   ```python
   L_matrix_dict[country_code][year] = {
       "matrix": ...,   # NumPy array, shape (23, 23)
       "labeled": ...,  # Pandas dataframe with sector row/column labels
   }
   ```

   Rebuilding the cache requires resolving the matrix-construction concerns in [methodology](methodology.md); reproducing the slide metrics cannot be guaranteed from the supplied files. Only load a pickle from a trusted source because deserialization executes Python objects.

## Restore the notebook environment

The original environment was **Google Colab**. Upload the notebook and install the analysis dependencies in a setup cell (upload `requirements.txt` as well):

```python
%pip install -r requirements.txt
```

Run the import and Drive-mount cells, then update any `/content/drive/...` paths. Create the directory used by the chart export (`MyDrive/figures`) before running that cell, or change its output path.

For local inspection, create a virtual environment and install dependencies:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m jupyterlab econ_input_output.ipynb
```

For local execution, also remove the Colab Drive mount and replace Drive paths with local paths. The `.py` file is an original Colab export, not a standalone CLI: it includes notebook-specific commands and interactive prompts.

## Interactive functions

After restoring inputs and running the relevant preparation/function-definition cells, the notebook exposes:

```python
heatmap("CHN", 2000)   # Domestic interindustry flows, billions of USD
heatmap_demo()         # Prompt for country and year
leontief_demo()        # Prompt for country/year and show sector linkage scores
```

The heatmap requires the imports, sector mapping, country subsetting, sector aliases, and heatmap definitions. It does not require the precomputed ML cache. The Leontief chart additionally needs the Leontief pipeline definitions and the corrections described in the methodology notes.

The archived notebook is exploratory and relies on shared state. In particular, the PCA temporal-evaluation helper uses `precision_score`, `recall_score`, and `f1_score` before their later import; import those metrics before calling it. Several function names are redefined in later experiments. Review section dependencies before running individual cells.

## Figure provenance

The files in `docs/images/` were decoded directly from existing PNG outputs in the original notebook. No data or plots were regenerated:

| File | Original cell index (zero-based) | Content |
| --- | ---: | --- |
| `sector-heatmap.png` | 140 | China, 2000, transaction heatmap |
| `sector-linkages.png` | 138 | Saved Leontief sector-score chart; chart country label is affected by the original global-variable issue |
| `final-demand-trends.png` | 16 | Final-demand component plots across countries |
| `regional-coverage.png` | 18 | Country counts per region |
