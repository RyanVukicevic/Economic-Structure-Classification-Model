"""Regenerate the README's raw transaction charts from the local WIOD CSV."""
from pathlib import Path
import sys
import ast
import json
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from raw_sector_visualizations import SECTORS, load_panel, plot_pooled


def main():
    destination = ROOT / 'docs' / 'images'
    panel = load_panel()
    for role in ('producer', 'consumer', 'combined'):
        fig = plot_pooled(panel, role)
        fig.savefig(destination / f'pooled-{role}.png', dpi=140)
        plt.close(fig)
    # Execute the notebook's preparation cells and its actual heatmap query.
    notebook = json.loads((ROOT / 'economic_structure_classification_model.ipynb').read_text(encoding='utf-8'))
    context = {'Path': Path, 'pd': pd, 'plt': plt, 'sns': sns,
               '__file__': str(ROOT / 'economic_structure_classification_model.py')}
    for index in (5, 10, 13, 24):
        exec(''.join(notebook['cells'][index]['source']), context)
    source = next(''.join(cell['source']) for cell in notebook['cells']
                  if cell['cell_type'] == 'code' and 'def heatmap(' in ''.join(cell['source']))
    function = next(node for node in ast.parse(source).body
                    if isinstance(node, ast.FunctionDef) and node.name == 'heatmap')
    exec(compile(ast.Module(body=[function], type_ignores=[]), '<notebook heatmap>', 'exec'), context)
    data = pd.read_csv(ROOT / 'lr_wiod_wiot_wide.csv')
    codes = list(SECTORS)
    for country, name, palette in [('USA', 'USA', 'Greens'), ('CHN', 'China', 'Reds'),
                                    ('DEU', 'Germany', 'GermanyGold')]:
        context['heatmap'](country, 2000, vmin=0, vmax=50)
        fig = plt.gcf()
        ax = fig.axes[0]
        mesh = ax.collections[0]
        # Confirm the notebook query matches the original domestic matrix.
        block = data.loc[(data.row_country == country) & (data.year == 2000)]
        expected = block.set_index('row_isic3').loc[codes, [f'{country}_{code}' for code in codes]] / 1000
        np.testing.assert_allclose(np.asarray(mesh.get_array()).reshape(23, 23), expected)
        if country == 'CHN':
            palette = LinearSegmentedColormap.from_list('ChinaRed', ['#fff7f7', '#df5555', '#790000'])
        elif country == 'DEU':
            palette = LinearSegmentedColormap.from_list('GermanyGold', ['#fffde7', '#e6c600', '#756000'])
        mesh.set_cmap(palette)
        mesh.colorbar.set_label('Billions of Current USD (50+ Saturates)')
        fig.set_size_inches(14, 12)
        ax.set_title(f'Domestic Interindustry Transactions | {name}, 2000', fontsize=16, pad=16)
        ax.set_xticklabels(list(SECTORS.values()), rotation=55, ha='right')
        ax.set_yticklabels(list(SECTORS.values()), rotation=0)
        ax.tick_params(axis='both', labelsize=9)
        fig.tight_layout()
        fig.savefig(destination / f'heatmap-{country.lower()}-2000.png', dpi=140)
        plt.close(fig)
    print('Saved six README charts; three notebook heatmap queries verified against the CSV.')


if __name__ == '__main__':
    main()
