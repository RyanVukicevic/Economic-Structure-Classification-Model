# Generated from economic_structure_classification_model.ipynb. Run from any directory.

# %% Notebook cell 1
# Data source: https://www.rug.nl/ggdc/valuechain/long-run-wiod
# Woltjer, Gouma and Timmer (2021), GGDC Research Memorandum 190.


# %% Notebook cell 4
from pathlib import Path
import hashlib
import json
import math
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import display
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
np.random.seed(42)
plt.rcParams['figure.dpi'] = 90

from visualizations import plot_sector_linkages, plot_tree_importance

plt.show()
plt.close('all')

# %% Notebook cell 5
PROJECT_DIR = Path(__file__).resolve().parent if '__file__' in globals() else Path.cwd()
DATA_PATH = PROJECT_DIR / 'lr_wiod_wiot_wide.csv'
OUTPUT_DIR = PROJECT_DIR / 'outputs'
OUTPUT_DIR.mkdir(exist_ok=True)
if not DATA_PATH.is_file():
    raise FileNotFoundError(f'Place lr_wiod_wiot_wide.csv in {PROJECT_DIR}')
df = pd.read_csv(DATA_PATH)
required = {'year', 'row_country', 'row_isic3'}
if not required.issubset(df.columns):
    raise ValueError(f'Missing CSV columns: {required - set(df.columns)}')
if df.duplicated(['year', 'row_country', 'row_isic3']).any():
    raise ValueError('Duplicate country/year/sector rows in CSV')
print(f'Loaded {DATA_PATH.name}: {len(df):,} rows, {len(df.columns)} columns')

plt.show()
plt.close('all')

# %% Notebook cell 6
# No Google Drive mount or externally supplied pickle is required.

plt.show()
plt.close('all')

# %% Notebook cell 7
pd.set_option('display.max_columns', None)

#prints every col by line
# for col in df.columns:
#     print(col)
plt.show()
plt.close('all')

# %% Notebook cell 10
#countries in dataset
# print(df['row_country'].value_counts(dropna=False))

#codes for sectors i presume

df.rename(columns={"year": "Year", "row_isic3": "Sector"}, inplace=True)

code_to_description = {
    "AtB": "Agriculture, Hunting, Forestry, and Fishing",
    "C": "Mining and Quarrying",
    "D15t16": "Food, Beverages, and Tobacco",
    "D17t19": "Textiles, Textile Products, Leather, Footwear",
    "D21t22": "Pulp, Paper, Printing, Publishing",
    "D23": "Coke, Refined Petroleum, and Nuclear Fuel",
    "D24": "Chemicals and Chemical Products",
    "D25": "Rubber and Plastics",
    "D26": "Other Non-Metallic Mineral Products",
    "D27t28": "Basic and Fabricated Metals",
    "D29": "Machinery and Equipment n.e.c.",
    "D30t33": "Electrical and Optical Equipment",
    "D34t35": "Transport Equipment",
    "Dnec": "Manufacturing n.e.c.; Recycling",
    "E": "Electricity, Gas, and Water Supply",
    "F": "Construction",
    "G": "Wholesale and Retail Trade; Repairs",
    "H": "Hotels and Restaurants",
    "I60t63": "Transport and Storage",
    "I64": "Post and Telecommunications",
    "J": "Financial Intermediation",
    "K": "Real Estate, Renting, and Business Activities",
    "LtQ": "Public Administration, Education, Health, and Other Services",
    "xCONS_h": "Final Consumption Expenditure by Households",
    "xCONS_g": "Final Consumption Expenditure by Government",
    "xGFCF": "Gross Fixed Capital Formation",
    "xINV": "Changes in Inventories"
}

df["Sector"] = df["Sector"].map(code_to_description)

for (k,v) in code_to_description.items():
    print(k, " --- ", v)

# print(df["row_isic3"].value_counts(dropna=False))



plt.show()
plt.close('all')

# %% Notebook cell 11
import matplotlib.font_manager
# sorted({f.name for f in matplotlib.font_manager.fontManager.ttflist})

plt.show()
plt.close('all')

# %% Notebook cell 13
countries = sorted([c for c in df['row_country'].unique() if c not in ['xROW', 'xTOT']])

region_map = {
    'USA': 'Americas',
    'CAN': 'Americas',
    'MEX': 'Americas',
    'AUT': 'Europe',
    'BEL': 'Europe',
    'DEU': 'Europe',
    'DNK': 'Europe',
    'ESP': 'Europe',
    'FIN': 'Europe',
    'FRA': 'Europe',
    'GBR': 'Europe',
    'GRC': 'Europe',
    'IRL': 'Europe',
    'ITA': 'Europe',
    'NLD': 'Europe',
    'PRT': 'Europe',
    'SWE': 'Europe',
    'AUS': 'Asia-Pacific',
    'CHN': 'Asia-Pacific',
    'HKG': 'Asia-Pacific',
    'IND': 'Asia-Pacific',
    'JPN': 'Asia-Pacific',
    'KOR': 'Asia-Pacific',
    'TWN': 'Asia-Pacific',
    'BRA': 'Americas'
}

#dict to store each df
country_dfs = {}

for country in countries:
    # Columns that belong to this country
    cols = ['row_country', 'Year', 'Sector'] + [c for c in df.columns if c.startswith(country + "_")]

    # Subset the dataframe for this country's rows
    country_df = df[df['row_country'] == country][cols].copy()

    rename_dict = {f"{country}_{k}": v for k, v in code_to_description.items() if f"{country}_{k}" in country_df.columns}
    country_df.rename(columns=rename_dict, inplace=True)

    #redundant info so drop row_country
    country_df.drop(columns=['row_country'], inplace=True)

    country_dfs[country] = country_df

print(f"Generated dataframes for {len(country_dfs)} countries: {list(country_dfs.keys())}")

#Lawrence Part
# plot y trends from year to year for each country, find L matrix and plot trends for all countries year to year for each entry
output_components = ["Final Consumption Expenditure by Households",
                     "Final Consumption Expenditure by Government",
                     "Gross Fixed Capital Formation",
                     "Changes in Inventories"]
df_all = []

for country, df_country in country_dfs.items():
    temp = df_country.copy()
    temp["Country"] = country
    temp["Region"] = country  # temporarily fill
    temp["Region"] = temp["Country"].map(region_map)  # map to region
    df_all.append(temp)

# Combine all countries
df_all = pd.concat(df_all, ignore_index=True)

component_titles = {
    "Final Consumption Expenditure by Households": "Final Consumption\nby Households",
    "Final Consumption Expenditure by Government": "Final Consumption\nby Government",
    "Gross Fixed Capital Formation": "Gross Fixed\nCapital Formation",
    "Changes in Inventories": "Changes in Inventories"
}

components_long = df_all.melt(
    id_vars=["Year", "Country"],
    value_vars=output_components,
    var_name="Component",
    value_name="Value"
)

plt.show()
plt.close('all')

# %% Notebook cell 15
sector_cols = [code_to_description[k] for k in list(code_to_description)[:23]]
sectors_long = df_all.melt(
    id_vars=['Year', 'Country', 'Region'], value_vars=sector_cols,
    var_name='Sector', value_name='Value')
regional_avg = sectors_long.groupby(['Year', 'Region', 'Sector'])['Value'].mean().reset_index()

plt.show()
plt.close('all')

# %% Notebook cell 16
# #plotting cell
sns.set_theme(style="whitegrid", context="talk")

fig, axes = plt.subplots(1, 5, figsize=(26, 10), gridspec_kw={'width_ratios': [1,1,1,1,0.3]})

for ax, comp in zip(axes[:4], output_components):
    if comp not in components_long["Component"].unique():
        ax.set_visible(False)
        continue

    sns.lineplot(
        data=components_long[components_long["Component"] == comp],
        x="Year", y="Value", hue="Country",
        ax=ax,
        errorbar=None
    )
    ax.set_title(component_titles.get(comp, comp))
    ax.set_xlabel("Year")
    ax.set_ylabel("Final Demand (Value)")
    ax.get_legend().remove()

# Legend-only axis
axes[-1].axis("off")  # hide the last subplot’s frame
handles, labels = axes[0].get_legend_handles_labels()
axes[-1].legend(
    handles, labels,
    title="Country",
    loc="center",
    fontsize=12,
    title_fontsize=16
)

plt.tight_layout()



plt.show()
plt.close('all')

# %% Notebook cell 17
sns.set_theme(style="whitegrid", context="talk")

sectors = sorted(regional_avg["Sector"].unique())
n_sectors = len(sectors)

# Decide grid size
ncols = 5
nrows = math.ceil(n_sectors / ncols)

fig, axes = plt.subplots(nrows, ncols, figsize=(6*ncols, 5*nrows))
axes = axes.flatten()  # flatten for easy indexing

for i, sector in enumerate(sectors):
    ax = axes[i]
    sns.lineplot(
        data=regional_avg[regional_avg["Sector"] == sector],
        x="Year", y="Value", hue="Region",
        ax=ax,
        errorbar=None
    )
    ax.set_title(sector, fontsize=10)
    ax.set_xlabel("Year")
    ax.set_ylabel("Avg Output")
    ax.get_legend().remove()  # remove individual legends

# Remove any empty subplots
for j in range(i+1, len(axes)):
    axes[j].axis("off")

# Create a single legend
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(
    handles, labels,
    title="Region",
    loc="upper center",
    bbox_to_anchor=(0.5, 1.05),
    ncol=len(labels),
    fontsize=20,
    title_fontsize=25
)

plt.tight_layout()
plt.show()

plt.show()
plt.close('all')

# %% Notebook cell 18
df_countries = df_all[['Country', 'Region']].drop_duplicates()

# Count countries per region
region_counts = df_countries['Region'].value_counts().reset_index()
region_counts.columns = ['Region', 'Count']

# Plot
sns.set_theme(style="whitegrid")
plt.figure(figsize=(8,5))
sns.barplot(data=region_counts, x='Region', y='Count', palette='Set2')
plt.title("Number of Countries per Region")
plt.xlabel("Region")
plt.ylabel("Number of Countries")
output_path = OUTPUT_DIR / "region_count_barplot.pdf"
plt.savefig(output_path, dpi=300, format='pdf', bbox_inches='tight')

plt.show()
plt.close('all')

# %% Notebook cell 20
# summary = []

# for country, df_country in country_dfs.items():
#     for year in sorted(df_country["Year"].unique()):
#         year_df = df_country[df_country["Year"] == year]

#         matrix = year_df.iloc[:, 2:]
#         display_matrix = matrix / 1000

#         summary.append({
#             "country": country,
#             "year": year,
#             "median": round(float(np.median(display_matrix.values)), 6),
#             "mean": round(float(np.mean(display_matrix.values)), 6),
#             "min":  round(float(display_matrix.values.min()), 6),
#             "max":  round(float(display_matrix.values.max()), 6),
#         })

# summary_df = pd.DataFrame(summary).sort_values(by=["year", "country"])


# sns.set_theme(style="whitegrid", font="DejaVu Serif")

# palette = sns.color_palette("husl", n_colors=len(country_dfs))

# metrics = ["median", "mean", "min", "max"]
# titles = {
#     "median": "Median Intersectoral Flow (Billions USD)",
#     "mean":   "Mean Intersectoral Flow (Billions USD)",
#     "min":    "Minimum Intersectoral Flow (Billions USD)",
#     "max":    "Maximum Intersectoral Flow (Billions USD)"
# }

# fig, axes = plt.subplots(2, 2, figsize=(11, 8))
# print("\nGraph displaying the median, mean, min, and max (in billions) for each country's intersectoral flow matrix from 1965–2000.\n")

# first_ax = axes.flatten()[0]
# sns.lineplot(
#     data=summary_df,
#     x="year", y=metrics[0], hue="country",
#     palette=palette, marker="o", ax=first_ax
# )
# first_ax.set_title(titles[metrics[0]], fontsize=12)
# first_ax.set_xlabel("Year")
# first_ax.set_ylabel("Billions USD")

# handles, labels = first_ax.get_legend_handles_labels()
# first_ax.get_legend().remove()

# for ax, metric in zip(axes.flatten()[1:], metrics[1:]):
#     sns.lineplot(
#         data=summary_df,
#         x="year", y=metric, hue="country",
#         palette=palette, marker="o", ax=ax,
#         legend=False
#     )
#     ax.set_title(titles[metric], fontsize=12)
#     ax.set_xlabel("Year")
#     ax.set_ylabel("Billions USD")

# fig.legend(
#     handles, labels,
#     title="Country",
#     loc="center left",
#     bbox_to_anchor=(.87, 0.5), #.87 super specific to get the legend at that exact position
#     fontsize=8, title_fontsize=10
# )

# plt.tight_layout(rect=[0, 0, 0.85, 1])
# plt.show()


plt.show()
plt.close('all')

# %% Notebook cell 21
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", font="DejaVu Serif")

# -----------------------------
# Prepare summary dataframe
# -----------------------------
summary = []

for country, df_country in country_dfs.items():
    for year in sorted(df_country["Year"].unique()):
        year_df = df_country[df_country["Year"] == year]
        matrix = year_df.iloc[:, 2:]
        display_matrix = matrix / 1000  # Convert to billions
        summary.append({
            "country": country,
            "year": year,
            "median": float(np.median(display_matrix.values)),
            "mean":   float(np.mean(display_matrix.values)),
            "min":    float(display_matrix.values.min()),
            "max":    float(display_matrix.values.max()),
        })

summary_df = pd.DataFrame(summary).sort_values(by=["year", "country"])

# -----------------------------
# Create a robust color palette
# -----------------------------
n_countries = len(country_dfs)

# Combine tab20 and tab20b to cover 40 distinct colors
base_palette = list(plt.cm.tab20.colors)
extra_palette = list(plt.cm.tab20b.colors)
palette = base_palette + extra_palette
palette = palette[:n_countries]  # trim to the exact number of countries

# -----------------------------
# Metrics and titles
# -----------------------------
metrics = ["median", "mean", "min", "max"]
titles = {
    "median": "Median Intersectoral Flow (Billions USD)",
    "mean":   "Mean Intersectoral Flow (Billions USD)",
    "min":    "Minimum Intersectoral Flow (Billions USD)",
    "max":    "Maximum Intersectoral Flow (Billions USD)"
}

# -----------------------------
# Create 2x2 subplots
# -----------------------------
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
axes_flat = axes.flatten()

# First metric with handles for legend
sns.lineplot(
    data=summary_df,
    x="year", y=metrics[0], hue="country",
    palette=palette, marker="o", ax=axes_flat[0]
)
axes_flat[0].set_title(titles[metrics[0]], fontsize=12)
axes_flat[0].set_xlabel("Year")
axes_flat[0].set_ylabel("Billions USD")

handles, labels = axes_flat[0].get_legend_handles_labels()
axes_flat[0].get_legend().remove()

# Remaining metrics
for ax, metric in zip(axes_flat[1:], metrics[1:]):
    sns.lineplot(
        data=summary_df,
        x="year", y=metric, hue="country",
        palette=palette, marker="o", ax=ax,
        legend=False
    )
    ax.set_title(titles[metric], fontsize=12)
    ax.set_xlabel("Year")
    ax.set_ylabel("Billions USD")

# -----------------------------
# Add figure-level legend
# -----------------------------
fig.legend(
    handles, labels,
    title="Country",
    loc="center left",
    bbox_to_anchor=(0.87, 0.5),
    fontsize=8,
    title_fontsize=10,
    ncol=1  # one column for better readability with 25+ countries
)

plt.tight_layout(rect=[0, 0, 0.85, 1])  # leave space for the legend
plt.show()

plt.show()
plt.close('all')

# %% Notebook cell 24
#do not delete or comment out

sector_aliases = {
    'Agriculture, Hunting, Forestry, and Fishing': 'Agriculture',
    'Mining and Quarrying': 'Mining',
    'Food, Beverages, and Tobacco': 'FoodBevTobacco',
    'Textiles, Textile Products, Leather, Footwear': 'Textiles',
    'Pulp, Paper, Printing, Publishing': 'PaperPrint',
    'Coke, Refined Petroleum, and Nuclear Fuel': 'Petroleum',
    'Chemicals and Chemical Products': 'Chemicals',
    'Rubber and Plastics': 'RubberPlastics',
    'Other Non-Metallic Mineral Products': 'NonMetalMinerals',
    'Basic and Fabricated Metals': 'Metals',
    'Machinery and Equipment n.e.c.': 'Machinery',
    'Electrical and Optical Equipment': 'Electronics',
    'Transport Equipment': 'TransportEquip',
    'Manufacturing n.e.c.; Recycling': 'ManufacturingOther',
    'Electricity, Gas, and Water Supply': 'Utilities',
    'Construction': 'Construction',
    'Wholesale and Retail Trade; Repairs': 'WholesaleRetail',
    'Hotels and Restaurants': 'Hospitality',
    'Transport and Storage': 'TransportStorage',
    'Post and Telecommunications': 'PostTelecom',
    'Financial Intermediation': 'Finance',
    'Real Estate, Renting, and Business Activities': 'RealEstateBusiness',
    'Public Administration, Education, Health, and Other Services': 'PublicServices'
}
plt.show()
plt.close('all')

# %% Notebook cell 26
def compute_L(country: str, year: int, output_components: list):
    country = country.upper()
    if country not in country_dfs:
        raise ValueError(f'Unknown country: {country}')
    names = list(sector_aliases)
    frame = country_dfs[country]
    subset = frame.loc[frame['Year'] == year].set_index('Sector')
    if len(subset) != len(names) or set(subset.index) != set(names):
        raise ValueError(f'Expected exactly 23 sectors for {country}, {year}')
    subset = subset.loc[names]
    Z = subset[names].to_numpy(dtype=float)
    # Normalize domestic inputs by reported gross output, including exports.
    # Domestic demand alone can be negative for export-heavy sectors with
    # inventory adjustments; it is not an appropriate gross-output denominator.
    totals = df.loc[(df['row_country'] == country) & (df['Year'] == year)].set_index('Sector')
    x = totals.loc[names, 'xTOT_xGO'].to_numpy(dtype=float)
    # Demand outside domestic intermediate use: final demand plus exports,
    # with published accounting adjustments retained through reported output.
    y = x - Z.sum(axis=1)
    if not np.isfinite(Z).all() or not np.isfinite(y).all() or np.any(x <= 0):
        raise ValueError(f'Invalid flows or nonpositive output for {country}, {year}')
    A = Z / x[np.newaxis, :]
    I = np.eye(len(names))
    L = np.linalg.solve(I - A, I)
    np.testing.assert_allclose(A @ x + y, x, rtol=1e-9, atol=1e-7)
    np.testing.assert_allclose(L @ y, x, rtol=1e-8, atol=1e-6)
    np.testing.assert_allclose((I - A) @ L, I, rtol=1e-8, atol=1e-8)
    return L, pd.DataFrame(L, index=names, columns=names), year, frame

plt.show()
plt.close('all')

# %% Notebook cell 27
L_matrix_dict = {}
for country in countries:
    L_matrix_dict[country] = {}
    for year in sorted(country_dfs[country]['Year'].unique()):
        matrix, labeled, _, _ = compute_L(country, int(year), output_components)
        L_matrix_dict[country][int(year)] = {'matrix': matrix, 'labeled': labeled}
assert len(L_matrix_dict) == 25
assert sum(map(len, L_matrix_dict.values())) == 900
with (PROJECT_DIR / 'L_matrix_dict.pkl').open('wb') as stream:
    pickle.dump(L_matrix_dict, stream, protocol=pickle.HIGHEST_PROTOCOL)
print('Rebuilt and validated 900 Leontief matrices (23 x 23) from the local CSV.')

plt.show()
plt.close('all')

# %% Notebook cell 29
def L_avgs(sample_labeled:pd.DataFrame) -> pd.DataFrame:
  """
  computes averages across each row, col, then an average of both (row,col)-
  -for each sector in the sample_labeled df, which is from compute_L()
  intended only for use after compute_L() is called
  returns dataframe "avgs" with cols Row_Avg, Col_Avg, Avg_of_Avgs (average of the two)
  Values are unitless averages of Leontief coefficients, including the diagonal.
  The plotting helper sorts scores; these are not monetary transaction flows.
  2nd fn in L_pipeline()
  """

  #row mean - forward influence, how much other sectors' outputs depend on this sector when facing demand
  #col mean - backward linkage, how much total economy wide output needed to satisfy demand in this sector

  #because each sector has its own row, and is a col for all others, it will contribute to other sectors scores, as other do it
  #so each sector then will have a row mean, col mean

  #avg_of_avgs is the middle point between these two means, because both the row and col means display a sectors importance seperately
  #then the avg of those two is a symetric display of importance altogether

  row_avg = sample_labeled.mean(axis=1)
  col_avg = sample_labeled.mean(axis=0)

  avgs = pd.DataFrame({
      "Row_Avg": row_avg,
      "Col_Avg": col_avg
  })

  avgs['Avg_of_Avgs'] = avgs.mean(axis=1)


  return avgs
plt.show()
plt.close('all')

# %% Notebook cell 31
def L_avgs_plot(L_country: pd.DataFrame, L_year: int, avgs: pd.DataFrame) -> None:
    country = next(k for k, frame in country_dfs.items() if frame is L_country)
    plot_sector_linkages(avgs, sector_aliases, country, L_year)
    plt.show()

plt.show()
plt.close('all')

# %% Notebook cell 32
country_dfs['USA'].columns
plt.show()
plt.close('all')

# %% Notebook cell 36
# compute_L(), L_avgs, L_avgs_plot() all in a standardized pipeline

def leontief(country_input:str, year_input:int):
  """
  full pipeline where information is passed along at each step-
  -and the user only need specify country, year:
  1. compute_L()
  2. L_avgs()
  3. L_avgs_plot()
  information is passed along, each fn using data from the previous, to show a summary
  of most important sectors for year, country
  """

  sample_matrix, sample_labeled, L_year, L_country = compute_L(
      # country_dfs[country_input],
      country_input,
      year_input,
      output_components
      )

  avgs = L_avgs(sample_labeled)
  L_avgs_plot(L_country, L_year, avgs)

plt.show()
plt.close('all')

# %% Notebook cell 38
# #example usage by querying usa vs for every decade 1970-2000

# #user only needs to know general structure of fn call for this
# # L_pipeline(3 letter country code keys from country_dfs dictionary, year in range 1965-2000)

# for i in range(1970, 2001, 10):
#     leontief("USA", i)
#     leontief("CHN", i)


plt.show()
plt.close('all')

# %% Notebook cell 39
#notes on pipeline / future fixes maybe

#avg of avgs is a heuristic, for more rigorous evaluation we may need to use some theory or formula but this heuristic is easily interprettable, good for display
#find a way to sort values wo messing up sector labels
#find way when computing avg of avgs, to ignore diagnal as any sector will have interaction w itself, might inflate relative importance
plt.show()
plt.close('all')

# %% Notebook cell 41
def leontief_demo(country=None, year=None):
    print("Interactive Demonstration:\nShowing Sector Importance by User Specification (Country, Year)\n")

    country_list = ", ".join(country_dfs.keys())
    print(f"Possible Country Query Inputs\n{country_list}")

    c_input = (country if country is not None else input("\nSelect a Country: ")).strip().upper()
    if c_input not in country_dfs.keys():
        raise ValueError("Invalid country code, try again")

    print(f"\nPossible Query Year Inputs: {df['Year'].min()} - {df['Year'].max()}")
    y_input = int(year if year is not None else input("\nSelect a Year: "))

    if y_input not in range(1965, 2001):
        raise ValueError("Invalid year, try again")

    print(f"\nCurrent Query:\nCountry: {c_input}\nYear: {y_input}\n")

    # leontief(c_input, y_input)
    leontief(c_input, y_input)

plt.show()
plt.close('all')

# %% Notebook cell 45
def heatmap(country_code, year, vmin=0, vmax=50):
    """
    Display the interindustry flow matrix as a heatmap for a given country and year,
    using short sector labels.

    Parameters
    ----------
    country_code : str
        The country code key from `country_dfs`, e.g. "USA", "CHN", "GBR"
    year : int
        Year to visualize (must exist in that country's data)
    vmin, vmax : float
        Color scale limits for consistency across plots
    """

    #vmin, vmax set to default [0,50]

    if country_code not in country_dfs:
        raise ValueError(f"'{country_code}' not found. Valid countries: {list(country_dfs.keys())}")

    df_country = country_dfs[country_code]
    if year not in df_country["Year"].values:
        raise ValueError(f"Year {year} not found for {country_code}. "
                         f"Available years: {sorted(df_country['Year'].unique())}")

    year_df = df_country[df_country["Year"] == year]
    matrix = year_df.iloc[:, 2:-4] #cut off the year, sector and the last 4 final demand stats
    display_matrix = matrix / 1000.0


    sectors = year_df["Sector"].replace(sector_aliases).fillna(year_df["Sector"])

    money = sns.cubehelix_palette(start=2, rot=0, dark=0, light=.95, as_cmap=True)

    plt.figure(figsize=(12, 9))
    sns.heatmap(
        display_matrix,
        cmap=money,
        xticklabels=sectors,
        yticklabels=sectors,
        vmin=vmin, vmax=vmax,
        cbar_kws={'label': 'Billions USD'}
    )

    plt.title(f"{country_code} Interindustry Flow Heatmap ({year})", fontsize=14)
    plt.xlabel("Consuming Sector (Columns)", fontsize=12)
    plt.ylabel("Producing Sector (Rows)", fontsize=12)
    # plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()

plt.show()
plt.close('all')

# %% Notebook cell 47
def heatmap_demo(country=None, year=None):

  print("Interactive Demonstration:\nShowing Heatmap for Sector Interaction (Country, Year)\n")

  print("Default Scale on Coloring Axis is Fixed for Ease of Use, Comparison\n")

  country_list = ", ".join(country_dfs.keys())
  print(f"Possible Country Query Inputs\n{country_list}")
  c_input = (country if country is not None else input("\nSelect a Country: ")).strip().upper()

  if c_input not in country_dfs.keys():
    raise ValueError("Invalid country code, try again")

  print(f"\nPossible Query Year Inputs: {df['Year'].min()} - {df['Year'].max()}")
  y_input = int(year if year is not None else input("\nSelect a Year: "))

  if y_input not in range(1965, 2001):
    raise ValueError("Invalid country code, try again")

  print(f"\nCurrent Query:\nCountry: {c_input}\nYear: {y_input}\n")

  heatmap(c_input, y_input)

plt.show()
plt.close('all')

# %% Notebook cell 50
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GridSearchCV, train_test_split, cross_val_predict, StratifiedKFold
from sklearn.metrics import confusion_matrix
plt.show()
plt.close('all')

# %% Notebook cell 51
# # Can't have a high k, imbalances in classes will quicikly turn the model into a majority rules thing
# # High dimensionality issues, PCA?
# # Stratify y, ensures the same distribution in both train and test sets (When split up by year, data is small(25 entries))



# #L_matrix_dict

def knn_per_year_data(year: int):
  X=[]
  y=[]
  for country in countries:
    X.append(L_matrix_dict[country][year]['matrix'].flatten())
    y.append(region_map[country])
  scaler = StandardScaler()
  Xs = scaler.fit_transform(X)
  #print(Xs.shape)
  return Xs, y

def tune_k_for_year(year: int):
  X, y = knn_per_year_data(year)
  max_k = 12  # Must fit inside every small training fold

  knn = KNeighborsClassifier()
  param_grid = {'n_neighbors': range(1, max_k+1), 'weights':['uniform', 'distance']}
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
  grid_search = GridSearchCV(knn, param_grid, cv=StratifiedKFold(3, shuffle=True, random_state=42), error_score="raise")
  grid_search.fit(X_train, y_train)

  optimal_k = grid_search.best_params_['n_neighbors']
  optimal_weight = grid_search.best_params_['weights']

  return optimal_k, optimal_weight, grid_search, X_train, X_test, y_train, y_test

def fit_evaluate(year:int, n_splits: int = 3):
  optimal_k, optimal_weight, _, X_train, X_test, y_train, y_test = tune_k_for_year(year)
  X, y = knn_per_year_data(year)
  skf = StratifiedKFold(n_splits=min(n_splits, len(y)), shuffle=True, random_state=42)

  knn = KNeighborsClassifier(n_neighbors=optimal_k, weights=optimal_weight)
  knn.fit(X, y)
  y_pred = cross_val_predict(knn, X, y, cv=skf)
  labels = sorted(list(set(y)))

  cm = confusion_matrix(y, y_pred, labels=labels)

  # Plot
  plt.figure(figsize=(8, 6))
  sns.heatmap(
      cm,
      annot=True,
      fmt="d",
      cmap="Blues",
      xticklabels=labels,
      yticklabels=labels
  )
  plt.xlabel("Predicted")
  plt.ylabel("True")
  plt.title(f"KNN Confusion Matrix — Year {year}\nK={optimal_k}, weights={optimal_weight}")

  return knn, cm

plt.show()
plt.close('all')

# %% Notebook cell 52
# # Model Parameter selection for every year maximizing the average CV accuracy
years=df_country["Year"].unique()
n_years = len(years)

ncols = 3
nrows = (n_years + ncols - 1) // ncols

fig, axes = plt.subplots(nrows, ncols, figsize=(ncols*6, nrows*5))
# fig, axes = plt.subplots(nrows, ncols, figsize=(12, 7))  # smaller figure for slides

axes = axes.flatten()

for i, year in enumerate(years):
    optimal_k, optimal_weight, grid_search, X_train, X_test, y_train, y_test = tune_k_for_year(year)
    results = grid_search.cv_results_

    k_values = results['param_n_neighbors'].data
    weights = results['param_weights'].data
    mean_scores = results['mean_test_score']

    for w in ['uniform', 'distance']:
        idx = [j for j, wt in enumerate(weights) if wt == w]
        axes[i].plot(
            np.array(k_values)[idx],
            np.array(mean_scores)[idx],
            marker='o',
            label=f"weights={w}"
        )

    axes[i].set_title(f"Year {year}")
    axes[i].set_xlabel("K")
    axes[i].set_ylabel("Mean CV Accuracy")
    axes[i].grid(True)
    axes[i].legend()

for j in range(i+1, len(axes)):
    axes[j].axis('off')

plt.tight_layout()
output_path = OUTPUT_DIR / "knn_results_per_year.png"
plt.savefig(output_path, dpi=100, bbox_inches='tight')
plt.show()
plt.close('all')

# %% Notebook cell 53
fit_evaluate(year = 2000)
fit_evaluate(year = 1977)
plt.show()
plt.close('all')

# %% Notebook cell 57
def whole_data(data):
  X = []
  y = []

  for country in countries:
      for year, entry in data[country].items():
          X.append(entry['matrix'].flatten())
          y.append(region_map[country])

  X = np.array(X)
  y = np.array(y)
  scaler = StandardScaler()
  Xs = scaler.fit_transform(X)
  return Xs, y

def tune_k(X, y):
  #X, y = whole_data(data)
  max_k = 70 # half smallest class size

  knn = KNeighborsClassifier()
  param_grid = {'n_neighbors': range(1, max_k+1), 'weights':['uniform', 'distance']}
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
  grid_search = GridSearchCV(knn, param_grid, cv=5)
  grid_search.fit(X_train, y_train)

  optimal_k = grid_search.best_params_['n_neighbors']
  optimal_weight = grid_search.best_params_['weights']

  return optimal_k, optimal_weight, grid_search, X_train, X_test, y_train, y_test

def fitting(data):
  X, y = whole_data(data)
  optimal_k, optimal_weight, grid_search, X_train, X_test, y_train, y_test = tune_k(X, y)
  model = KNeighborsClassifier(n_neighbors=optimal_k,
                               weights = optimal_weight,
                               )
  model.fit(X_train, y_train)
  #y_train_pred = model.predict(X_train)
  y_pred = model.predict(X_test)
  labels=sorted(list(set(y)))

  cm = confusion_matrix(y_test, y_pred, labels=labels)
  plt.figure(figsize=(8, 6))
  sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels,
                yticklabels=labels)
  plt.xlabel("Predicted")
  plt.ylabel("True")
  plt.title(f"KNN Confusion Matrix for All Data — \nK={optimal_k}, weights={optimal_weight}")

  return model
plt.show()
plt.close('all')

# %% Notebook cell 58
model = fitting(L_matrix_dict)

X, y_real= knn_per_year_data(2000)
y_pred= model.predict(X)
labels = sorted(list(set(y_real)))

cm = confusion_matrix(y_real, y_pred, labels=labels)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
              xticklabels=labels,
              yticklabels=labels)
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title(f"KNN Confusion Matrix for Year 2000— \nK=1, weights=uniform")

X, y_real= knn_per_year_data(1970)
y_pred= model.predict(X)
labels = sorted(list(set(y_real)))

cm = confusion_matrix(y_real, y_pred, labels=labels)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
              xticklabels=labels,
              yticklabels=labels)
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title(f"KNN Confusion Matrix for Year 1970— \nK=1, weights=uniform")
plt.show()
plt.close('all')

# %% Notebook cell 61
X, y = whole_data(L_matrix_dict)
_, _, _, X_train, _, _, _ = tune_k(X, y)
plt.show()
plt.close('all')

# %% Notebook cell 62
# Install dependencies once with pip install -r requirements.txt
from sklearn.decomposition import PCA
from kneed import KneeLocator
pca = PCA()
pca.fit(X_train)

explained = pca.explained_variance_ratio_
cumulative = np.cumsum(explained)

for i, c in enumerate(cumulative[:20]):
    print(i+1, round(c, 4))

max_pcs = min(20, X.shape[1])
explained = pca.explained_variance_ratio_[:max_pcs]
cumulative = np.cumsum(explained)
plt.figure(figsize=(7,4))
pcs = np.arange(1, max_pcs + 1)

# --- Detect elbow with Kneedle ---
kneedle = KneeLocator( pcs, explained, curve="convex", direction="decreasing" )

knee_pc = kneedle.knee
knee_val = kneedle.knee_y
print("Kneedle elbow PC:", knee_pc)
plt.plot(range(1, max_pcs+1), explained, marker='o')
if knee_pc is not None:
  plt.scatter([knee_pc], [knee_val], s=120)
  plt.axvline(knee_pc, linestyle='--')
  plt.xlabel("PC")
  plt.ylabel("Explained Variance")
  plt.title("Scree Plot (first 20 PCs)")
  plt.show() #Elbow point not clear. from ~7-18 PC a plateau ?

plt.show()
plt.close('all')

# %% Notebook cell 63
# from sklearn.model_selection import cross_val_score
# from sklearn.pipeline import Pipeline
# from sklearn.linear_model import LogisticRegression

# scores = []
# components = range(2, 21)

# for k in components:
#     pipe = Pipeline([
#         ('pca', PCA(n_components=k)),
#         ('clf', LogisticRegression(max_iter=2000))
#     ])
#     s = cross_val_score(pipe, X, y, cv=5).mean()
#     scores.append(s)

# for k, s in zip(components, scores):
#     print(k, round(s, 4))
# # iterates and stores the logistic regression cross val average accuracy for 2<=k<=20 PC
# # After 18 PC, changes in accuracy diminish.
plt.show()
plt.close('all')

# %% Notebook cell 64
from sklearn.decomposition import PCA
import matplotlib.patches as mpatches
def reduce_pca(X, y):
  pca = PCA(n_components=5)
  X_reduced = pca.fit_transform(X)
  return X_reduced, y, pca

def fitting_r(data):
  X, y = whole_data(data)
  Xr, y, reducer = reduce_pca(X, y)
  optimal_k, optimal_weight, grid_search, X_train, X_test, y_train, y_test = tune_k(Xr, y)
  model = KNeighborsClassifier(n_neighbors=optimal_k,
                               weights = optimal_weight,
                               )
  model.fit(X_train, y_train)
  #y_train_pred = model.predict(X_train)
  y_pred = model.predict(X_test)
  labels=sorted(list(set(y)))

  cm = confusion_matrix(y_test, y_pred, labels=labels)
  plt.figure(figsize=(8, 6))
  sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels,
                yticklabels=labels)
  plt.xlabel("Predicted")
  plt.ylabel("True")
  plt.title(f"KNN Confusion Matrix Test Set — \nK={optimal_k}, weights={optimal_weight}")
  # print(f'Train Accuracy{}')
  # print(f'Test Accuracy')
  model.pca_transformer_ = reducer
  return model

def plot_pca_clusters_2d(X, y, n_components):
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X)

    plt.figure(figsize=(10, 7))
    sns.scatterplot(
        x=X_pca[:, 0],
        y=X_pca[:, 1],
        hue=y,
        palette='Set2',
        s=120,
        alpha=0.8
    )

    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    plt.title("2D PCA Visulaization")
    plt.grid(True, alpha=0.3)
    plt.show()
def plot_pca_clusters_3d(X, y, n_components):
    pca = PCA(n_components=n_components)
    X_vis = pca.fit_transform(X)

    fig = plt.figure(figsize=(22, 15))
    ax = fig.add_subplot(111, projection="3d")
    labels, uniques = pd.factorize(y)


    scatter = ax.scatter(
        X_vis[:, 0], X_vis[:, 1], X_vis[:, 2],
        c=labels,
        cmap="Set2",
        s=80
    )
    colors = scatter.cmap(scatter.norm(range(len(uniques))))
    legend_handles = [
      mpatches.Patch(color=colors[i], label=str(uniques[i]))
      for i in range(len(uniques))
    ]
    ax.legend(handles=legend_handles, title="Classes")
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    ax.set_zlabel(f"PC3 ({pca.explained_variance_ratio_[2]*100:.1f}%)")
    ax.set_title(f"3D PCA Visualization", fontsize = 20)
    plt.show()

# Using accuracy to tune, PC = 18
# Using Variance (Kneedle point) to tune, PC = 4

plt.show()
plt.close('all')

# %% Notebook cell 65
plot_pca_clusters_2d(X, y, 4)
plot_pca_clusters_3d(X, y, 4)
plt.show()
plt.close('all')

# %% Notebook cell 66
reduced_knn = fitting_r(L_matrix_dict)
plt.show()
plt.close('all')

# %% Notebook cell 67
X2000, y2000= knn_per_year_data(2000)
model = reduced_knn
X2000 = model.pca_transformer_.transform(X2000)
y2000pred= model.predict(X2000)
cm=confusion_matrix(y2000, y2000pred)
labels=sorted(list(set(y2000)))

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
              xticklabels=labels,
              yticklabels=labels)
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title(f"KNN (PCA) on 2000 data (descriptive, overlaps training)")

plt.show()
plt.close('all')

# %% Notebook cell 71
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
#Decision tree for interpretability
# data- df_all (df_all.head())
plt.show()
plt.close('all')

# %% Notebook cell 72
years = sorted(df_country["Year"].unique())

def tree_data(L_matrix_dict):
    rows = []
    labels = []

    for year in years:
        for country in countries:


            L_df = L_matrix_dict[country][year]['labeled']  # a DataFrame

            # Flatten into 1D vector BUT preserve feature names
            flat = L_df.stack() # Allows you to preserve the index names while also flattening the matrix into 1x529 (23*23)
            flat.index = [f"{i}->{j}" for i, j in flat.index]  # rename features (Sector 'row' -> Sector 'col')

            rows.append(flat)
            labels.append(region_map[country])

    # Convert list of Series → DataFrame
    X = pd.DataFrame(rows)
    y = pd.Series(labels, name="region")
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    return Xs, y, X
def tune_tree(X, y):
  # Grid of parameters
  param_grid = {
      'max_depth': [3, 4, 5, 6],
      'min_samples_split': [2, 5, 10],
      'min_samples_leaf': [1, 2, 4],
      'criterion': ['gini', 'entropy']
  }

  tree = DecisionTreeClassifier(random_state=42)
  grid_search = GridSearchCV(tree, param_grid, cv=5, scoring='accuracy')
  grid_search.fit(X, y)

  best_depth = grid_search.best_params_['max_depth']
  best_min_split = grid_search.best_params_['min_samples_split']
  best_min_leaf = grid_search.best_params_['min_samples_leaf']
  best_criterion = grid_search.best_params_['criterion']

  return best_depth, best_min_split, best_min_leaf, best_criterion
plt.show()
plt.close('all')

# %% Notebook cell 73
X, y, X_df = tree_data(L_matrix_dict)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state = 42)
best_depth, best_min_split, best_min_leaf, best_criterion = tune_tree(X_train, y_train)
tree = DecisionTreeClassifier(
    max_depth=best_depth,
    min_samples_split = best_min_split,
    min_samples_leaf=best_min_leaf,
    criterion = best_criterion,
    class_weight="balanced", random_state=42
)
tree.fit(X_train, y_train)
plot_tree_importance(tree, X_df.columns, sector_aliases, 'Europe / Asia-Pacific / Americas',
                     years, len(countries), len(X_train))
plt.show()

plt.show()
plt.close('all')

# %% Notebook cell 74
from sklearn import tree as sktree

#import matplotlib.pyplot as plt

plt.figure(figsize=(24, 14))
sktree.plot_tree(
    tree,
    feature_names=X_df.columns,
    class_names=tree.classes_,
    filled=True,
    fontsize=10,
    rounded=True
)
plt.title(f"Decision Tree \nDepth = {tree.get_depth()}, leaves = {tree.get_n_leaves()}", fontsize=20)
plt.show()

plt.show()
plt.close('all')

# %% Notebook cell 75
plt.figure(figsize=(24,14))  # Larger figure for slides
sktree.plot_tree(
              tree,
               max_depth=2,      # Only top 2 levels
               feature_names=X_df.columns,
               class_names=tree.classes_,
               filled=True,
               rounded=True,
               fontsize=14)
plt.title(f"Decision Tree \nDepth = {tree.get_depth()}, leaves = {tree.get_n_leaves()}", fontsize=20)
plt.show()
plt.show()
plt.close('all')

# %% Notebook cell 76
# Overfit check, Train Accuracy high but so is test accuracy probably not overfit, makes sense intuitively as well
# since KNN was able to successfully classify with high accuracy as well.
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state = 42)
# tree.fit(X_train, y_train)

train_pred = tree.predict(X_train)
test_pred = tree.predict(X_test)

print("Train Accuracy:", accuracy_score(y_train, train_pred))
print("Test Accuracy:", accuracy_score(y_test, test_pred))
plt.show()
plt.close('all')

# %% Notebook cell 79
def subset_year_data(data):
    subset_years = set(range(1965, 1991))   # training years

    X_train, y_train, train_meta = [], [], []
    X_eval, y_eval, eval_meta = [], [], []

    for country in data.keys():
        for year in data[country].keys():
            vec = data[country][year]['matrix'].flatten()
            label = region_map[country]

            if year in subset_years:
                X_train.append(vec)
                y_train.append(label)
                train_meta.append((country, year))
            else:
                X_eval.append(vec)
                y_eval.append(label)
                eval_meta.append((country, year))

    X_train = np.array(X_train)
    y_train = np.array(y_train)
    X_eval = np.array(X_eval)
    y_eval = np.array(y_eval)

    # scale using training only
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_eval_scaled = scaler.transform(X_eval)

    return X_train_scaled, y_train, train_meta, X_eval_scaled, y_eval, eval_meta

def subset_year_tune_k(X_train, y_train):
    max_k = 70

    knn = KNeighborsClassifier()
    param_grid = {
        'n_neighbors': range(1, max_k+1),
        'weights': ['uniform', 'distance']
    }

    grid_search = GridSearchCV(knn, param_grid, cv=5)
    grid_search.fit(X_train, y_train)

    return (
        grid_search.best_params_['n_neighbors'],
        grid_search.best_params_['weights'],
        grid_search
    )


def subset_year_fitting(data):
    # Load processed data
    X_train, y_train, train_meta, X_eval, y_eval, eval_meta = subset_year_data(data)

    optimal_k, optimal_weight, grid_search = subset_year_tune_k(X_train, y_train)

    model = KNeighborsClassifier(
        n_neighbors=optimal_k,
        weights=optimal_weight
    )
    model.fit(X_train, y_train)

    # Evaluate on FUTURE years
    y_pred = model.predict(X_eval)

    # Confusion matrix
    labels=sorted(list(set(y_train)))
    cm = confusion_matrix(y_eval, y_pred, labels=labels)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels,
                yticklabels=labels)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"KNN Future Years Confusion Matrix — K={optimal_k}, weights={optimal_weight}")
    plt.show()

    # Overfit check
    train_pred = model.predict(X_train)
    print("Train Accuracy:", accuracy_score(y_train, train_pred))
    print("Test Accuracy:", accuracy_score(y_eval, y_pred))

    # ---- MISCLASSIFIED SAMPLES ----
    misclassified = []
    for i, (true, pred) in enumerate(zip(y_eval, y_pred)):
        if true != pred:
            country, year = eval_meta[i]
            misclassified.append({
                "Country": country,
                "Year": year,
                "True Region": true,
                "Predicted Region": pred
            })

    misclassified_df = pd.DataFrame(misclassified)
    print("\nMisclassified future-year cases:")
    display(misclassified_df)

    return model, misclassified_df

plt.show()
plt.close('all')

# %% Notebook cell 80
model = subset_year_fitting(L_matrix_dict)

# X, y_real= knn_per_year_data(2000)
# y_pred= model.predict(X)
# cm=confusion_matrix(y_real, y_pred)
# plt.figure(figsize=(8, 6))
# sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
#               xticklabels=list(set(y_test)),
#               yticklabels=list(set(y_test)))
# plt.xlabel("Predicted")
# plt.ylabel("True")
# plt.title(f"KNN Confusion Matrix — \nK=1, weights=uniform")
plt.show()
plt.close('all')

# %% Notebook cell 83
X_train, _, _, _, _, _= subset_year_data(L_matrix_dict)
plt.show()
plt.close('all')

# %% Notebook cell 84
pca = PCA()
pca.fit(X_train)

explained = pca.explained_variance_ratio_
cumulative = np.cumsum(explained)

for i, c in enumerate(cumulative[:20]):
    print(i+1, round(c, 4))

max_pcs = min(20, X_train.shape[1])
explained = pca.explained_variance_ratio_[:max_pcs]
cumulative = np.cumsum(explained)
plt.figure(figsize=(7,4))
pcs = np.arange(1, max_pcs + 1)

# --- Detect elbow with Kneedle ---
kneedle = KneeLocator(pcs, explained, curve="convex", direction="decreasing" )

knee_pc = kneedle.knee
knee_val = kneedle.knee_y
print("Kneedle elbow PC:", knee_pc)
plt.plot(range(1, max_pcs+1), explained, marker='o')
if knee_pc is not None:
  plt.scatter([knee_pc], [knee_val], s=120)
  plt.axvline(knee_pc, linestyle='--')
  plt.xlabel("PC")
  plt.ylabel("Explained Variance")
  plt.title("Scree Plot (first 20 PCs)")
  plt.show()

plt.show()
plt.close('all')

# %% Notebook cell 85
# from sklearn.model_selection import cross_val_score
# from sklearn.pipeline import Pipeline
# from sklearn.linear_model import LogisticRegression

# scores = []
# components = range(2, 21)

# for k in components:
#     pipe = Pipeline([
#         ('pca', PCA(n_components=k)),
#         ('clf', LogisticRegression(max_iter=2000))
#     ])
#     s = cross_val_score(pipe, X, y, cv=5).mean()
#     scores.append(s)

# for k, s in zip(components, scores):
#     print(k, round(s, 4))
# # iterates and stores the logistic regression cross val average accuracy for 2<=k<=20 PC
# # After 18 PC, changes in accuracy diminish.
plt.show()
plt.close('all')

# %% Notebook cell 86
def subset_year_data_pca(data):
    subset_years = set(range(1965, 1991))   # training years

    X_train, y_train, train_meta = [], [], []
    X_eval, y_eval, eval_meta = [], [], []

    for country in data.keys():
        for year in data[country].keys():
            vec = data[country][year]['matrix'].flatten()
            label = region_map[country]

            if year in subset_years:
                X_train.append(vec)
                y_train.append(label)
                train_meta.append((country, year))
            else:
                X_eval.append(vec)
                y_eval.append(label)
                eval_meta.append((country, year))

    X_train = np.array(X_train)
    y_train = np.array(y_train)
    X_eval = np.array(X_eval)
    y_eval = np.array(y_eval)

    # scale using training only
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_eval_scaled = scaler.transform(X_eval)

    # dimension reduction
    pca = PCA(n_components=7)
    X_train_pc = pca.fit_transform(X_train_scaled)
    X_eval_pc = pca.transform(X_eval_scaled)
    return X_train_pc, y_train, train_meta, X_eval_pc, y_eval, eval_meta, pca

def subset_year_fitting_pca(data):
    # Load processed data
    X_train, y_train, train_meta, X_eval, y_eval, eval_meta, pca = subset_year_data_pca(data)

    optimal_k, optimal_weight, grid_search = subset_year_tune_k(X_train, y_train)

    model = KNeighborsClassifier(
        n_neighbors=optimal_k,
        weights=optimal_weight
    )
    model.fit(X_train, y_train)

    # Evaluate on FUTURE years
    y_pred = model.predict(X_eval)

    # Confusion matrix
    labels=sorted(list(set(y_train)))
    cm = confusion_matrix(y_eval, y_pred, labels=labels)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels,
                yticklabels=labels)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"KNN Future Years Confusion Matrix — K={optimal_k}, weights={optimal_weight}")
    plt.show()

    # Overfit check
    train_pred = model.predict(X_train)
    print("Train Accuracy:", accuracy_score(y_train, train_pred))
    print("Test Accuracy:", accuracy_score(y_eval, y_pred))

    # MISCLASSIFIED SAMPLES
    misclassified = []
    for i, (true, pred) in enumerate(zip(y_eval, y_pred)):
        if true != pred:
            country, year = eval_meta[i]
            misclassified.append({
                "Country": country,
                "Year": year,
                "True Region": true,
                "Predicted Region": pred
            })

    misclassified_df = pd.DataFrame(misclassified)
    print("\nMisclassified future-year cases:")
    display(misclassified_df)
    print("\n=== Confusion Matrix Metrics (Future Years Evaluation) ===")
    print("Accuracy:", accuracy_score(y_eval, y_pred))
    print("Precision (macro):", precision_score(y_eval, y_pred, average='macro', zero_division=0))
    print("Recall (macro):", recall_score(y_eval, y_pred, average='macro', zero_division=0))
    print("F1 Score (macro):", f1_score(y_eval, y_pred, average='macro', zero_division=0))
    print("---------------------------------------------------------\n")
    return model, misclassified_df

plt.show()
plt.close('all')

# %% Notebook cell 87
X, y = whole_data(L_matrix_dict)
plot_pca_clusters_2d(X, y, 7)
plot_pca_clusters_3d(X, y, 7)
plt.show()
plt.close('all')

# %% Notebook cell 88
reduced_model, misclass = subset_year_fitting_pca(L_matrix_dict)

# Optimal model classifying future years is way worse with the PCA on features
plt.show()
plt.close('all')

# %% Notebook cell 89
# _df_20.groupby('Country').size().plot(kind='barh', color=sns.palettes.mpl_palette('Dark2'))
# plt.gca().spines[['top', 'right',]].set_visible(False)
# plt.title("KNN reduced Future Years Misclassified Countries", fontsize = 18)
plt.show()
plt.close('all')

# %% Notebook cell 93
from sklearn.cluster import KMeans
from scipy.stats import mode
def fit_clustering(data, n_clusters=3, random_state=42):
    X, y = whole_data(data)
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    model.fit(X)

    cluster_ids = model.labels_ #returns array of predictions (cluster #) for each sample

    cluster_to_label = {} #store cluster names
    for c in range(n_clusters):
        cluster_labels = y[cluster_ids == c] #for each cluster, attach all the labels in the cluster
        if len(cluster_labels) > 0:
          vals, counts = np.unique(cluster_labels, return_counts=True)
          cluster_to_label[c] = vals[np.argmax(counts)]
            # cluster_to_label[c] = mode(cluster_labels)[0][0]  #find the mode of each cluster's region, error, mode needs to be numeric now
        else:
            cluster_to_label[c] = None  # empty cluster

    mapped = [cluster_to_label[c] for c in cluster_ids] # store them in a list

    labels_sorted = sorted(set(y))
    cm = confusion_matrix(y, mapped, labels=labels_sorted)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels_sorted,
                yticklabels=labels_sorted)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"KMeans Confusion Matrix (K={n_clusters})- Whole Data")
    plt.show()

    return model, cluster_to_label

def fit_subset_clustering(data, n_clusters=3, random_state=42):
    X_train_scaled, y_train, train_meta, X_eval_scaled, y_eval, eval_meta = subset_year_data(data)
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    model.fit(X_train_scaled)

    train_cluster_ids = model.labels_
    cluster_ids = model.predict(X_eval_scaled) #returns array of predictions (cluster #) for each sample

    cluster_to_label = {} #store cluster names
    for c in range(n_clusters):
        cluster_labels = y_train[train_cluster_ids == c] #for each cluster, attach all the labels in the cluster
        if len(cluster_labels) > 0:
          vals, counts = np.unique(cluster_labels, return_counts=True)
          cluster_to_label[c] = vals[np.argmax(counts)]
            # cluster_to_label[c] = mode(cluster_labels)[0][0]  #find the mode of each cluster's region, error, mode needs to be numeric now
        else:
            cluster_to_label[c] = None  # empty cluster

    mapped = [cluster_to_label[c] for c in cluster_ids] # store them in a list

    labels_sorted = sorted(set(y_eval))
    cm = confusion_matrix(y_eval, mapped, labels=labels_sorted)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels_sorted,
                yticklabels=labels_sorted)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"KMeans Confusion Matrix (K={n_clusters})- Subset Year")
    plt.show()

    return model, cluster_to_label

plt.show()
plt.close('all')

# %% Notebook cell 94
clustering, labels = fit_clustering(L_matrix_dict)
model2, label = fit_subset_clustering(L_matrix_dict)
plt.show()
plt.close('all')

# %% Notebook cell 98
def pca_whole(X, y):
  pca = PCA(n_components=4)
  X_reduced = pca.fit_transform(X)
  return X_reduced, y, pca

def pca_subset(X, y):
  pca = PCA(n_components=7)
  X_reduced = pca.fit_transform(X)
  return X_reduced, y, pca
plt.show()
plt.close('all')

# %% Notebook cell 99
def fit_reduced_clustering(data, n_clusters=3, random_state=42):
    X, y = whole_data(data)
    Xr, y, _ = pca_whole(X, y)
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    model.fit(Xr)

    cluster_ids = model.labels_ #returns array of predictions (cluster #) for each sample

    cluster_to_label = {} #store cluster names
    for c in range(n_clusters):
        cluster_labels = y[cluster_ids == c] #for each cluster, attach all the labels in the cluster
        if len(cluster_labels) > 0:
          vals, counts = np.unique(cluster_labels, return_counts=True)
          cluster_to_label[c] = vals[np.argmax(counts)]
            # cluster_to_label[c] = mode(cluster_labels)[0][0]  #find the mode of each cluster's region, error, mode needs to be numeric now
        else:
            cluster_to_label[c] = None  # empty cluster

    mapped = [cluster_to_label[c] for c in cluster_ids] # store them in a list

    labels_sorted = sorted(set(y))
    cm = confusion_matrix(y, mapped, labels=labels_sorted)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels_sorted,
                yticklabels=labels_sorted)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"KMeans Confusion Matrix (K={n_clusters})- Whole Data Reduced")
    plt.show()

    return model, cluster_to_label

def fit_subset_reduced_clustering(data, n_clusters=3, random_state=42):
    X_train_scaled, y_train, train_meta, X_eval_scaled, y_eval, eval_meta = subset_year_data(data)
    Xr, yT, reducer = pca_subset(X_train_scaled, y_train)
    X_eval_r = reducer.transform(X_eval_scaled)
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    model.fit(Xr)

    train_cluster_ids = model.labels_
    cluster_ids = model.predict(X_eval_r) #returns array of predictions (cluster #) for each sample

    cluster_to_label = {} #store cluster names
    for c in range(n_clusters):
        cluster_labels = y_train[train_cluster_ids == c] #for each cluster, attach all the labels in the cluster
        if len(cluster_labels) > 0:
          vals, counts = np.unique(cluster_labels, return_counts=True)
          cluster_to_label[c] = vals[np.argmax(counts)]
            # cluster_to_label[c] = mode(cluster_labels)[0][0]  #find the mode of each cluster's region, error, mode needs to be numeric now
        else:
            cluster_to_label[c] = None  # empty cluster

    mapped = [cluster_to_label[c] for c in cluster_ids] # store them in a list

    labels_sorted = sorted(set(y_eval))
    cm = confusion_matrix(y_eval, mapped, labels=labels_sorted)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels_sorted,
                yticklabels=labels_sorted)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"KMeans Confusion Matrix (K={n_clusters})- Subset Year Reduced")
    plt.show()

    return model, cluster_to_label

plt.show()
plt.close('all')

# %% Notebook cell 100
model3, labels = fit_reduced_clustering(L_matrix_dict)
model4, labels = fit_subset_reduced_clustering(L_matrix_dict)
plt.show()
plt.close('all')

# %% Notebook cell 102
from sklearn.metrics import silhouette_score

sil_scores = []
for k in range(2, 11):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(X)
    sil_scores.append(silhouette_score(X, labels))

optimal_k = range(2, 11)[sil_scores.index(max(sil_scores))]
print("Optimal k by silhouette:", optimal_k)

#Sillhouette scores also kinds of supprots this thesis of being able to split the two East, West regions.
#Australia is considered geographically on the east but abstract political science definitions has them in the west. Will account for both types in running the clustering
#Also, South America is another continent heavily debated, whether it's part of the western world. Due to high amounts of European settlement and influence, I will include them as 'Western'
plt.show()
plt.close('all')

# %% Notebook cell 104
region_map = {
    'USA': 'Americas',
    'CAN': 'Americas',
    'MEX': 'Americas',
    'AUT': 'Europe',
    'BEL': 'Europe',
    'DEU': 'Europe',
    'DNK': 'Europe',
    'ESP': 'Europe',
    'FIN': 'Europe',
    'FRA': 'Europe',
    'GBR': 'Europe',
    'GRC': 'Europe',
    'IRL': 'Europe',
    'ITA': 'Europe',
    'NLD': 'Europe',
    'PRT': 'Europe',
    'SWE': 'Europe',
    'AUS': 'Asia-Pacific',
    'CHN': 'Asia-Pacific',
    'HKG': 'Asia-Pacific',
    'IND': 'Asia-Pacific',
    'JPN': 'Asia-Pacific',
    'KOR': 'Asia-Pacific',
    'TWN': 'Asia-Pacific',
    'BRA': 'Americas'
}

geographic_map= {
    'USA': 'Western',
    'CAN': 'Western',
    'MEX': 'Western',
    'AUT': 'Western',
    'BEL': 'Western',
    'DEU': 'Western',
    'DNK': 'Western',
    'ESP': 'Western',
    'FIN': 'Western',
    'FRA': 'Western',
    'GBR': 'Western',
    'GRC': 'Western',
    'IRL': 'Western',
    'ITA': 'Western',
    'NLD': 'Western',
    'PRT': 'Western',
    'SWE': 'Western',
    'AUS': 'Eastern',
    'CHN': 'Eastern',
    'HKG': 'Eastern',
    'IND': 'Eastern',
    'JPN': 'Eastern',
    'KOR': 'Eastern',
    'TWN': 'Eastern',
    'BRA': 'Western'
}

override_map = {
    'AUS': 'Western'
}
def get_political_region(country):
    # Use override first
    if country in override_map:
        return override_map[country]
    # Otherwise use geographic map
    else:
      return geographic_map[country]

plt.show()
plt.close('all')

# %% Notebook cell 105
counts_g = {}
counts_p = {}
for country in geographic_map:
    region_p = get_political_region(country)
    region_g = geographic_map[country]
    counts_g[region_g] = counts_g.get(region_g, 0) + 1
    counts_p[region_p]=counts_p.get(region_p, 0) + 1

# Plot
plt.figure(figsize=(8, 5))
plt.bar(list(counts_g.keys()), list(counts_g.values()))
plt.xlabel("Region")
plt.ylabel("Count")
plt.title("Country Counts by Geographic Region")
plt.tight_layout()
plt.show()

plt.figure(figsize=(8, 5))
plt.bar(list(counts_p.keys()), list(counts_p.values()))
plt.xlabel("Region")
plt.ylabel("Count")
plt.title("Country Counts by Political Region")
plt.tight_layout()
plt.show()
plt.show()
plt.close('all')

# %% Notebook cell 107
def whole_data2(data, ytype):
  X = []
  y = []

  for country in countries:
      for year, entry in data[country].items():
          X.append(entry['matrix'].flatten())
          #y.append(region_map[country])
          if ytype== 'geographic':
            y.append(geographic_map[country])
          elif ytype== 'political':
            y.append(get_political_region(country))

  X = np.array(X)
  y = np.array(y)
  scaler = StandardScaler()
  Xs = scaler.fit_transform(X)
  return Xs, y

def tune_k(X, y):
  #X, y = whole_data(data)
  max_k = 70 # half smallest class size

  knn = KNeighborsClassifier()
  param_grid = {'n_neighbors': range(1, max_k+1), 'weights':['uniform', 'distance']}
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
  grid_search = GridSearchCV(knn, param_grid, cv=5)
  grid_search.fit(X_train, y_train)

  optimal_k = grid_search.best_params_['n_neighbors']
  optimal_weight = grid_search.best_params_['weights']

  return optimal_k, optimal_weight, grid_search, X_train, X_test, y_train, y_test

def fitting(data, ytype):
  X, y = whole_data2(data, ytype)
  optimal_k, optimal_weight, grid_search, X_train, X_test, y_train, y_test = tune_k(X, y)
  model = KNeighborsClassifier(n_neighbors=optimal_k,
                               weights = optimal_weight,
                               )
  model.fit(X_train, y_train)
  #y_train_pred = model.predict(X_train)
  y_pred = model.predict(X_test)
  labels=sorted(list(set(y)))

  cm = confusion_matrix(y_test, y_pred, labels=labels)
  plt.figure(figsize=(8, 6))
  sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels,
                yticklabels=labels)
  plt.xlabel("Predicted")
  plt.ylabel("True")
  plt.title(f"KNN Confusion Matrix for All Data — {ytype} \nK={optimal_k}, weights={optimal_weight}")

  return model
plt.show()
plt.close('all')

# %% Notebook cell 108
political_class = fitting(L_matrix_dict, 'political')
geographic_class = fitting(L_matrix_dict, 'geographic')
plt.show()
plt.close('all')

# %% Notebook cell 109
# # X, y = whole_data2(L_matrix_dict, 'political') #Political optimal PC: 4
# # X, y = whole_data2(L_matrix_dict, 'geographic') #Geographic optimal PC: 4
# _, _, _, X_train, _, _, _ = tune_k(X, y)

# pca = PCA()
# pca.fit(X_train)

# explained = pca.explained_variance_ratio_
# cumulative = np.cumsum(explained)

# for i, c in enumerate(cumulative[:20]):
#     print(i+1, round(c, 4))

# max_pcs = min(20, X.shape[1])
# explained = pca.explained_variance_ratio_[:max_pcs]
# cumulative = np.cumsum(explained)
# plt.figure(figsize=(7,4))
# pcs = np.arange(1, max_pcs + 1)

# # --- Detect elbow with Kneedle ---
# kneedle = KneeLocator( pcs, explained, curve="convex", direction="decreasing" )

# knee_pc = kneedle.knee
# knee_val = kneedle.knee_y
# print("Kneedle elbow PC:", knee_pc)
# plt.plot(range(1, max_pcs+1), explained, marker='o')
# if knee_pc is not None:
#   plt.scatter([knee_pc], [knee_val], s=120)
#   plt.axvline(knee_pc, linestyle='--')
#   plt.xlabel("PC")
#   plt.ylabel("Explained Variance")
#   plt.title("Scree Plot (first 20 PCs)")
#   plt.show() #Elbow point not clear. from ~7-18 PC a plateau ?

plt.show()
plt.close('all')

# %% Notebook cell 111
def plot_pca_clusters_2d(X, y, ytype, n_components):
    pca = PCA(n_components=n_components)
    X_pca = pca.fit_transform(X)

    plt.figure(figsize=(10, 7))
    sns.scatterplot(
        x=X_pca[:, 0],
        y=X_pca[:, 1],
        hue=y,
        palette='Set2',
        s=120,
        alpha=0.8
    )

    plt.xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    plt.ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    plt.title(f"2D PCA Visulaization- {ytype}")
    plt.grid(True, alpha=0.3)
    plt.show()
def plot_pca_clusters_3d(X, y, ytype, n_components):
    pca = PCA(n_components=n_components)
    X_vis = pca.fit_transform(X)

    fig = plt.figure(figsize=(22, 15))
    ax = fig.add_subplot(111, projection="3d")
    labels, uniques = pd.factorize(y)


    scatter = ax.scatter(
        X_vis[:, 0], X_vis[:, 1], X_vis[:, 2],
        c=labels,
        cmap="Set2",
        s=80
    )
    colors = scatter.cmap(scatter.norm(range(len(uniques))))
    legend_handles = [
      mpatches.Patch(color=colors[i], label=str(uniques[i]))
      for i in range(len(uniques))
    ]
    ax.legend(handles=legend_handles, title="Classes")
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}%)")
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}%)")
    ax.set_zlabel(f"PC3 ({pca.explained_variance_ratio_[2]*100:.1f}%)")
    ax.set_title(f"3D PCA Visualization- {ytype}", fontsize = 20)
    plt.show()

def pca_whole2(X, y):
  pca = PCA(n_components=4)
  X_reduced = pca.fit_transform(X)
  return X_reduced, y, pca

def fitting_r_2(data, ytype):
  X, y = whole_data2(data, ytype)
  Xr, y, _ = pca_whole2(X, y)
  optimal_k, optimal_weight, grid_search, X_train, X_test, y_train, y_test = tune_k(Xr, y)
  model = KNeighborsClassifier(n_neighbors=optimal_k,
                               weights = optimal_weight,
                               )
  model.fit(X_train, y_train)
  #y_train_pred = model.predict(X_train)
  y_pred = model.predict(X_test)
  labels=sorted(list(set(y)))

  cm = confusion_matrix(y_test, y_pred, labels=labels)
  plt.figure(figsize=(8, 6))
  sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels,
                yticklabels=labels)
  plt.xlabel("Predicted")
  plt.ylabel("True")
  plt.title(f"KNN Confusion Matrix Test Set — \nK={optimal_k}, weights={optimal_weight} - {ytype}")
  plot_pca_clusters_2d(Xr, y,ytype, n_components=4)
  plot_pca_clusters_3d(Xr, y,ytype, n_components=4)
  return model
plt.show()
plt.close('all')

# %% Notebook cell 112
fitting_r_2(L_matrix_dict, 'political')
fitting_r_2(L_matrix_dict, 'geographic')
plt.show()
plt.close('all')

# %% Notebook cell 115
years = sorted(df_country["Year"].unique())

def tree_data2(L_matrix_dict, ytype):
    rows = []
    labels = []

    for year in years:
        for country in countries:


            L_df = L_matrix_dict[country][year]['labeled']  # a DataFrame

            # Flatten into 1D vector BUT preserve feature names
            flat = L_df.stack() # Allows you to preserve the index names while also flattening the matrix into 1x529 (23*23)
            flat.index = [f"{i}->{j}" for i, j in flat.index]  # rename features (Sector 'row' -> Sector 'col')

            rows.append(flat)
            if ytype=='geographic':
              labels.append(geographic_map[country])
            elif ytype=='political':
              labels.append(get_political_region(country))


    # Convert list of Series → DataFrame
    X = pd.DataFrame(rows)
    y = pd.Series(labels, name="region")
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    return Xs, y, X
def tune_tree(X, y):
  # Grid of parameters
  param_grid = {
      'max_depth': [3, 4, 5, 6],
      'min_samples_split': [2, 5, 10],
      'min_samples_leaf': [1, 2, 4],
      'criterion': ['gini', 'entropy']
  }

  tree = DecisionTreeClassifier(random_state=42)
  grid_search = GridSearchCV(tree, param_grid, cv=5, scoring='accuracy')
  grid_search.fit(X, y)

  best_depth = grid_search.best_params_['max_depth']
  best_min_split = grid_search.best_params_['min_samples_split']
  best_min_leaf = grid_search.best_params_['min_samples_leaf']
  best_criterion = grid_search.best_params_['criterion']

  return best_depth, best_min_split, best_min_leaf, best_criterion

def fit_tree(ytype):
  X, y, X_df = tree_data2(L_matrix_dict, ytype)
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state = 42)
  best_depth, best_min_split, best_min_leaf, best_criterion = tune_tree(X_train, y_train)
  tree = DecisionTreeClassifier(
      max_depth=best_depth,
      min_samples_split = best_min_split,
      min_samples_leaf=best_min_leaf,
      criterion = best_criterion,
      class_weight="balanced", random_state=42
  )
  tree.fit(X_train, y_train)
  plot_tree_importance(tree, X_df.columns, sector_aliases, f'{ytype} East / West',
                       years, len(countries), len(X_train))
  plt.show()

  plt.figure(figsize=(24,14))  # Larger figure for slides
  sktree.plot_tree(
                tree,
                max_depth=2,      # Only top 2 levels
                feature_names=X_df.columns,
                class_names=tree.classes_,
                filled=True,
                rounded=True,
                fontsize=14)
  plt.title(f"Decision Tree \nDepth = {tree.get_depth()}, leaves = {tree.get_n_leaves()} - {ytype}", fontsize=20)
  plt.show()

  if best_depth!=2:
    plt.figure(figsize=(24, 14))
    sktree.plot_tree(
        tree,
        feature_names=X_df.columns,
        class_names=tree.classes_,
        filled=True,
        fontsize=10,
        rounded=True
    )
    plt.title(f"Decision Tree \nDepth = {tree.get_depth()}, leaves = {tree.get_n_leaves()} - {ytype} full tree", fontsize=20)
    plt.show()

plt.show()
plt.close('all')

# %% Notebook cell 116
fit_tree('political')
fit_tree('geographic')
plt.show()
plt.close('all')

# %% Notebook cell 118
# Do first 25 years, last 10 altered for new regions
# Do Clustering analysis
plt.show()
plt.close('all')

# %% Notebook cell 120
def subset_year_data2(data, ytype):
    subset_years = set(range(1965, 1991))   # training years

    X_train, y_train, train_meta = [], [], []
    X_eval, y_eval, eval_meta = [], [], []

    for country in data.keys():
        for year in data[country].keys():
            vec = data[country][year]['matrix'].flatten()
            if ytype== 'geographic':
              label = geographic_map[country]
            elif ytype== 'political':
              label = get_political_region(country)
            #label = region_map[country]

            if year in subset_years:
                X_train.append(vec)
                y_train.append(label)
                train_meta.append((country, year))
            else:
                X_eval.append(vec)
                y_eval.append(label)
                eval_meta.append((country, year))

    X_train = np.array(X_train)
    y_train = np.array(y_train)
    X_eval = np.array(X_eval)
    y_eval = np.array(y_eval)

    # scale using training only
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_eval_scaled = scaler.transform(X_eval)

    return X_train_scaled, y_train, train_meta, X_eval_scaled, y_eval, eval_meta

# def subset_year_tune_k(X_train, y_train):
#     max_k = 70

#     knn = KNeighborsClassifier()
#     param_grid = {
#         'n_neighbors': range(1, max_k+1),
#         'weights': ['uniform', 'distance']
#     }

#     grid_search = GridSearchCV(knn, param_grid, cv=5)
#     grid_search.fit(X_train, y_train)

#     return (
#         grid_search.best_params_['n_neighbors'],
#         grid_search.best_params_['weights'],
#         grid_search
#     )


def subset_year_fitting2(data, ytype):
    # Load processed data
    X_train, y_train, train_meta, X_eval, y_eval, eval_meta = subset_year_data2(data, ytype)

    optimal_k, optimal_weight, grid_search = subset_year_tune_k(X_train, y_train)

    model = KNeighborsClassifier(
        n_neighbors=optimal_k,
        weights=optimal_weight
    )
    model.fit(X_train, y_train)

    # Evaluate on FUTURE years
    y_pred = model.predict(X_eval)

    # Confusion matrix
    labels=sorted(list(set(y_train)))
    cm = confusion_matrix(y_eval, y_pred, labels=labels)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels,
                yticklabels=labels)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"KNN Future Years Confusion Matrix — K={optimal_k}, weights={optimal_weight}- {ytype}")
    plt.show()

    # Overfit check
    train_pred = model.predict(X_train)
    print("Train Accuracy:", accuracy_score(y_train, train_pred))
    print("Test Accuracy:", accuracy_score(y_eval, y_pred))

    # ---- MISCLASSIFIED SAMPLES ----
    misclassified = []
    for i, (true, pred) in enumerate(zip(y_eval, y_pred)):
        if true != pred:
            country, year = eval_meta[i]
            misclassified.append({
                "Country": country,
                "Year": year,
                "True Region": true,
                "Predicted Region": pred
            })

    misclassified_df = pd.DataFrame(misclassified)
    print("\nMisclassified future-year cases:")
    display(misclassified_df)

    return model, misclassified_df

plt.show()
plt.close('all')

# %% Notebook cell 121
model5, misclass = subset_year_fitting2(L_matrix_dict, 'political')
model6, misclass = subset_year_fitting2(L_matrix_dict, 'geographic')
plt.show()
plt.close('all')

# %% Notebook cell 123
from sklearn.metrics import precision_score, recall_score, f1_score

def fit_clustering2(data, ytype, n_clusters=2, random_state=42):
    X, y = whole_data2(data, ytype)
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    model.fit(X)

    cluster_ids = model.labels_ #returns array of predictions (cluster #) for each sample

    cluster_to_label = {} #store cluster names
    for c in range(n_clusters):
        cluster_labels = y[cluster_ids == c] #for each cluster, attach all the labels in the cluster
        if len(cluster_labels) > 0:
          vals, counts = np.unique(cluster_labels, return_counts=True)
          cluster_to_label[c] = vals[np.argmax(counts)]
            # cluster_to_label[c] = mode(cluster_labels)[0][0]  #find the mode of each cluster's region, error, mode needs to be numeric now
        else:
            cluster_to_label[c] = None  # empty cluster

    mapped = [cluster_to_label[c] for c in cluster_ids] # store them in a list

    labels_sorted = sorted(set(y))
    cm = confusion_matrix(y, mapped, labels=labels_sorted)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels_sorted,
                yticklabels=labels_sorted)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"KMeans Confusion Matrix (K={n_clusters})- Whole Data- {ytype}")
    plt.show()
    # ---- PRINT METRICS ----
    print("\n=== Confusion Matrix Metrics (Whole Data) ===")
    print("Accuracy:", accuracy_score(y, mapped))
    print("Precision (macro):", precision_score(y, mapped, average='macro', zero_division=0))
    print("Recall (macro):", recall_score(y, mapped, average='macro', zero_division=0))
    print("F1 Score (macro):", f1_score(y, mapped, average='macro', zero_division=0))
    print("-------------------------------------------\n")
    return model, cluster_to_label

def fit_subset_clustering2(data, ytype, n_clusters=2, random_state=42):
    X_train_scaled, y_train, train_meta, X_eval_scaled, y_eval, eval_meta = subset_year_data2(data, ytype)
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    model.fit(X_train_scaled)

    train_cluster_ids = model.labels_
    cluster_ids = model.predict(X_eval_scaled) #returns array of predictions (cluster #) for each sample

    cluster_to_label = {} #store cluster names
    for c in range(n_clusters):
        cluster_labels = y_train[train_cluster_ids == c] #for each cluster, attach all the labels in the cluster
        if len(cluster_labels) > 0:
          vals, counts = np.unique(cluster_labels, return_counts=True)
          cluster_to_label[c] = vals[np.argmax(counts)]
            # cluster_to_label[c] = mode(cluster_labels)[0][0]  #find the mode of each cluster's region, error, mode needs to be numeric now
        else:
            cluster_to_label[c] = None  # empty cluster

    mapped = [cluster_to_label[c] for c in cluster_ids] # store them in a list

    labels_sorted = sorted(set(y_eval))
    cm = confusion_matrix(y_eval, mapped, labels=labels_sorted)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=labels_sorted,
                yticklabels=labels_sorted)
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.title(f"KMeans Confusion Matrix (K={n_clusters})- Subset Year - {ytype}")
    plt.show()

    # ---- PRINT METRICS ----
    print("\n=== Confusion Matrix Metrics (Subset Year) ===")
    print("Accuracy:", accuracy_score(y_eval, mapped))
    print("Precision (macro):", precision_score(y_eval, mapped, average='macro', zero_division=0))
    print("Recall (macro):", recall_score(y_eval, mapped, average='macro', zero_division=0))
    print("F1 Score (macro):", f1_score(y_eval, mapped, average='macro', zero_division=0))
    print("--------------------------------------------\n")
    return model, cluster_to_label

plt.show()
plt.close('all')

# %% Notebook cell 124
model7, labels = fit_clustering2(L_matrix_dict, 'political')
model8, label = fit_subset_clustering2(L_matrix_dict, 'political')
model9, labels = fit_clustering2(L_matrix_dict, 'geographic')
model10, label = fit_subset_clustering2(L_matrix_dict, 'geographic')
plt.show()
plt.close('all')

# %% Notebook cell 126
X, y = whole_data(L_matrix_dict)

wcss = []
k_range = range(1, 11)
for k in k_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X)
    wcss.append(km.inertia_)  # inertia_ = WCSS

kneedle = KneeLocator(k_range, wcss, curve="convex", direction="decreasing")
optimal_k = kneedle.knee
knee_val = kneedle.knee_y

print("Optimal k detected by Kneedle:", optimal_k)

# Plot
plt.figure(figsize=(8,5))
plt.plot(k_range, wcss, marker='o')
plt.scatter([optimal_k], [knee_val], s=120, color='red', label='Elbow')
plt.axvline(optimal_k, linestyle='--', color='gray')
plt.xlabel('Number of clusters (k)')
plt.ylabel('WCSS')
plt.title('Elbow Method for KMeans')
plt.legend()
plt.show()
plt.show()
plt.close('all')

# %% Notebook cell 128
def fit_clustering3(data, n_clusters=7, random_state=42):
    X, y, X_df = tree_data(L_matrix_dict)
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
    model.fit(X)

    # cluster_ids = model.fit_predict(X) #returns array of predictions (cluster #) for each sample

    # cluster_to_label = {} #store cluster names
    # for c in range(n_clusters):
    #     cluster_labels = y[cluster_ids == c] #for each cluster, attach all the labels in the cluster
    #     if len(cluster_labels) > 0:
    #       vals, counts = np.unique(cluster_labels, return_counts=True)
    #       cluster_to_label[c] = vals[np.argmax(counts)]
    #         # cluster_to_label[c] = mode(cluster_labels)[0][0]  #find the mode of each cluster's region, error, mode needs to be numeric now
    #     else:
    #         cluster_to_label[c] = None  # empty cluster

    # mapped = [cluster_to_label[c] for c in cluster_ids] # store them in a list

    # labels_sorted = sorted(set(y))
    # cm = confusion_matrix(y, mapped, labels=labels_sorted)

    # plt.figure(figsize=(8, 6))
    # sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
    #             xticklabels=labels_sorted,
    #             yticklabels=labels_sorted)
    # plt.xlabel("Predicted")
    # plt.ylabel("True")
    # plt.title(f"KMeans Confusion Matrix (K={n_clusters})- Whole Data- {ytype}")
    # plt.show()

    return model, X_df
plt.show()
plt.close('all')

# %% Notebook cell 129
model11, X_labels = fit_clustering3(L_matrix_dict)

print(model11.inertia_)

centers = pd.DataFrame(model11.cluster_centers_, columns=X_labels.columns)
(unique, counts) = np.unique(model11.labels_, return_counts=True)
print(dict(zip(unique, counts)))
plt.show()
plt.close('all')

# %% Notebook cell 130
X, y, _ = tree_data(L_matrix_dict)
labels = model11.predict(X)
pca = PCA(n_components=7)
X2d = pca.fit_transform(X)

plt.figure(figsize=(8,6))
plt.scatter(X2d[:,0], X2d[:,1], c=labels)
plt.title("Cluster Structure via PCA")
plt.xlabel("PC1")
plt.ylabel("PC2")
plt.show()

plt.show()
plt.close('all')

# %% Notebook cell 131
pca = PCA(n_components=3)
X3d = pca.fit_transform(X)

# 4. Plot in 3D
fig = plt.figure(figsize=(35, 15))
ax = fig.add_subplot(111, projection='3d')

scatter = ax.scatter(
    X3d[:, 0],
    X3d[:, 1],
    X3d[:, 2],
    c=labels
)

ax.set_title("Cluster Structure via 3D PCA")
ax.set_xlabel("PC1")
ax.set_ylabel("PC2")
ax.set_zlabel("PC3")

plt.show()
plt.close('all')

# %% Notebook cell 138
leontief_demo("USA", 2000)

plt.show()
plt.close('all')

# %% Notebook cell 140
heatmap_demo("CHN", 2000)

plt.show()
plt.close('all')
