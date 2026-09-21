"""Regenerate the README's raw transaction charts from the local WIOD CSV."""
from pathlib import Path
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from raw_sector_visualizations import SECTORS, load_panel, plot_country_year, plot_pooled


def main():
    destination = ROOT / 'docs' / 'images'
    panel = load_panel()
    for role in ('producer', 'consumer', 'combined'):
        fig = plot_pooled(panel, role)
        fig.savefig(destination / f'pooled-{role}.png', dpi=140)
        plt.close(fig)
    fig = plot_country_year(panel, 'USA', 2000)
    fig.savefig(destination / 'raw-sector-averages-usa-2000.png', dpi=140)
    plt.close(fig)

    data = pd.read_csv(ROOT / 'lr_wiod_wiot_wide.csv')
    codes = list(SECTORS)
    block = data.loc[(data.row_country == 'USA') & (data.year == 2000)]
    matrix = block.set_index('row_isic3').loc[codes, [f'USA_{code}' for code in codes]] / 1000
    fig, ax = plt.subplots(figsize=(14, 12))
    sns.heatmap(matrix, ax=ax,
                cmap=sns.cubehelix_palette(start=2, rot=0, dark=0, light=.95, as_cmap=True),
                xticklabels=list(SECTORS.values()), yticklabels=list(SECTORS.values()),
                vmin=0, vmax=50, cbar_kws={'label': 'Billions of Current USD', 'extend': 'max'})
    ax.set_title('Domestic Interindustry Transactions | USA, 2000', fontsize=16, pad=16)
    ax.set_xlabel('Consuming Sector (Columns)')
    ax.set_ylabel('Producing Sector (Rows)')
    ax.tick_params(axis='both', labelsize=9)
    plt.setp(ax.get_xticklabels(), rotation=55, ha='right')
    plt.setp(ax.get_yticklabels(), rotation=0)
    fig.tight_layout()
    fig.savefig(destination / 'current-sector-heatmap.png', dpi=140)
    plt.close(fig)
    print('Saved five README charts to', destination)


if __name__ == '__main__':
    main()
