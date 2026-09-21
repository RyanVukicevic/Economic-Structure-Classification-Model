"""Raw domestic WIOD transactions, in billions of current USD.

Run this file to regenerate the country-year preview and the three pooled rankings.
No Leontief transformation, model fitting, or price adjustment is applied.
"""
from pathlib import Path
import argparse
import json
import hashlib

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

ROOT = Path(__file__).resolve().parent
SECTORS = {
    'AtB': 'Agriculture & fishing', 'C': 'Mining & quarrying',
    'D15t16': 'Food, beverages & tobacco', 'D17t19': 'Textiles & leather',
    'D21t22': 'Paper & printing', 'D23': 'Petroleum & nuclear fuel',
    'D24': 'Chemicals', 'D25': 'Rubber & plastics',
    'D26': 'Non-metallic minerals', 'D27t28': 'Metals',
    'D29': 'Machinery', 'D30t33': 'Electrical & optical equipment',
    'D34t35': 'Transport equipment', 'Dnec': 'Other manufacturing',
    'E': 'Electricity, gas & water', 'F': 'Construction',
    'G': 'Wholesale & retail trade', 'H': 'Hotels & restaurants',
    'I60t63': 'Transport & storage', 'I64': 'Post & telecommunications',
    'J': 'Finance', 'K': 'Real estate & business services',
    'LtQ': 'Public & other services',  # Includes administration, education, and health.
}
COLORS = {'producer': '#287c8e', 'consumer': '#b86a30', 'combined': '#7255a0'}


def load_panel(path=ROOT / 'lr_wiod_wiot_wide.csv'):
    """Return 23 sector records for each of the 900 country-year blocks."""
    df = pd.read_csv(path)
    required = {'year', 'row_country', 'row_isic3'}
    if not required.issubset(df.columns):
        raise ValueError('CSV is missing year/country/sector columns')
    codes = list(SECTORS)
    domestic = df.loc[~df.row_country.isin(['xROW', 'xTOT'])]
    if domestic.duplicated(['row_country', 'year', 'row_isic3']).any():
        raise ValueError('Duplicate sector rows')
    countries = sorted(domestic.row_country.unique())
    years = list(range(1965, 2001))
    if len(countries) != 25 or sorted(domestic.year.unique()) != years:
        raise ValueError('Expected 25 countries and 1965-2000 coverage')
    records = []
    for (country, year), block in domestic.groupby(['row_country', 'year'], sort=True):
        if len(block) != 23 or set(block.row_isic3) != set(codes):
            raise ValueError(f'Incomplete sector coverage for {country}, {year}')
        z = block.set_index('row_isic3').loc[codes, [f'{country}_{s}' for s in codes]].to_numpy(dtype=float)
        if not np.isfinite(z).all():
            raise ValueError(f'Non-finite transactions for {country}, {year}')
        # Rows sell; columns buy. Source unit is millions; convert once to billions.
        producer = z.sum(axis=1) / 1000
        consumer = z.sum(axis=0) / 1000
        np.testing.assert_allclose(producer.sum(), consumer.sum(), rtol=1e-12)
        for i, code in enumerate(codes):
            records.append({'country': country, 'year': int(year), 'sector': code,
                            'producer': producer[i], 'consumer': consumer[i],
                            'combined': (producer[i] + consumer[i]) / 2})
    panel = pd.DataFrame(records)
    if len(panel) != 25 * 36 * 23:
        raise ValueError('Missing country-year blocks')
    return panel


def country_year_scores(panel, country='USA', year=2000):
    block = panel.loc[(panel.country == country.upper()) & (panel.year == int(year))]
    if len(block) != 23:
        raise ValueError(f'No complete data for {country}, {year}')
    # Mean across the 23 partner sectors, including the same sector.
    return block.set_index('sector')[['producer', 'consumer', 'combined']] / 23


def pooled_scores(panel):
    """Cumulative domestic transactions across all country-years, not per-year means."""
    return panel.groupby('sector')[['producer', 'consumer', 'combined']].sum()


def _finish(fig, ax, caption):
    ax.grid(axis='x', alpha=0.22)
    ax.set_axisbelow(True)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.0f}'))
    fig.text(0.02, 0.025, caption, fontsize=9, color='#475569', va='bottom')
    fig.tight_layout(rect=(0, 0.10, 1, 1))
    return fig


def plot_country_year(panel, country='USA', year=2000):
    scores = country_year_scores(panel, country, year).sort_values('combined')
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 10}):
        fig, ax = plt.subplots(figsize=(13, 10))
        ax.barh([SECTORS[s] for s in scores.index], scores.combined, color=COLORS['combined'])
        ax.set_title(f'Average raw sector transactions | {country.upper()}, {year}\n'
                     'Mean of producer row average and consumer column average', fontsize=15, pad=18)
        ax.set_xlabel('Billions of current USD per partner sector')
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}'))
        for i, value in enumerate(scores.combined):
            ax.text(value, i, f'  {value:,.2f}', va='center', fontsize=9)
        ax.set_xlim(0, scores.combined.max() * 1.15)
        _finish(fig, ax, 'Raw domestic intermediate transactions; 23 sectors; same-sector flows included.\n'
                        'Source: Long-run WIOD v1.1 (millions USD, divided by 1,000). No Leontief transformation.')
        ax.xaxis.set_major_formatter(StrMethodFormatter('{x:,.1f}'))
    return fig


def plot_pooled(panel, role='producer'):
    if role not in COLORS:
        raise ValueError('role must be producer, consumer, or combined')
    values = pooled_scores(panel)[role].sort_values()
    titles = {'producer': 'Producer ranking: sales to domestic industries',
              'consumer': 'Consumer ranking: purchases from domestic industries',
              'combined': 'Combined ranking: average of sales and purchases'}
    with plt.rc_context({'font.family': 'DejaVu Sans', 'font.size': 10}):
        fig, ax = plt.subplots(figsize=(13, 10))
        ax.barh([SECTORS[s] for s in values.index], values, color=COLORS[role])
        ax.set_title(titles[role] + '\n25 countries | 1965-2000 cumulative totals', fontsize=15, pad=18)
        ax.set_xlabel('Cumulative billions of current USD (sum across 36 years)')
        for i, value in enumerate(values):
            ax.text(value, i, f'  {value:,.0f}', va='center', fontsize=9)
        ax.set_xlim(0, values.max() * 1.17)
        _finish(fig, ax, 'Domestic intermediate transactions only; same-sector flows included; final demand and cross-border flows excluded.\n'
                        'Nominal-dollar totals favor larger economies and later years. Combined = (sales + purchases) / 2; not GDP.')
    return fig


def raw_flow_demo(panel=None, country=None, year=None):
    """Prompt for a country/year or accept arguments, without running the ML notebook."""
    if panel is None:
        panel = load_panel()
    country = country or input('Country code (e.g. USA): ').strip().upper()
    year = int(year if year is not None else input('Year (1965-2000): '))
    fig = plot_country_year(panel, country, year)
    plt.show()
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--country', default='USA')
    parser.add_argument('--year', type=int, default=2000)
    args = parser.parse_args()
    panel = load_panel()
    output = ROOT / 'outputs' / 'raw-sector-preview'
    output.mkdir(parents=True, exist_ok=True)
    totals = pooled_scores(panel)
    panel.to_csv(output / 'annual_country_sector_totals.csv', index=False)
    totals.rename(index=SECTORS).to_csv(output / 'pooled_sector_totals_billions.csv')
    country_year_scores(panel, args.country, args.year).rename(index=SECTORS).to_csv(output / 'country_year_averages_billions.csv')
    figure = plot_country_year(panel, args.country, args.year)
    figure.savefig(output / 'country-year-raw-averages.png', dpi=140)
    plt.close(figure)
    for role in COLORS:
        figure = plot_pooled(panel, role)
        figure.savefig(output / f'pooled-{role}.png', dpi=140)
        plt.close(figure)
    with (ROOT / 'lr_wiod_wiot_wide.csv').open('rb') as stream:
        checksum = hashlib.file_digest(stream, 'sha256').hexdigest()
    result = {'csv_sha256': checksum, 'countries': 25, 'years': [1965, 2000],
              'country_year_blocks': 900, 'sectors': 23,
              'scope': 'Sum of domestic blocks; no cross-border flows or final demand',
              'unit': 'billions of current USD',
              'combined_definition': '(producer + consumer) / 2',
              'producer_grand_total': float(totals.producer.sum()),
              'consumer_grand_total': float(totals.consumer.sum()),
              'top_five': {role: totals[role].nlargest(5).rename(index=SECTORS).to_dict() for role in COLORS}}
    (output / 'summary.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    print('Charts and underlying tables saved to', output)


if __name__ == '__main__':
    main()
