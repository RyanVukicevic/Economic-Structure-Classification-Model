"""Presentation helpers; these do not change the underlying model calculations."""
import numpy as np
import matplotlib.pyplot as plt


def plot_sector_linkages(avgs, aliases, country, year):
    scores = avgs['Avg_of_Avgs'].sort_values()
    fig, ax = plt.subplots(figsize=(12, 9))
    ax.barh([aliases.get(name, name) for name in scores.index], scores,
            color='#466b9e')
    ax.set_title(f'Sector linkage scores | {country}, {year}\n'
                 'Mean of row and column averages of the Leontief inverse', pad=14)
    ax.set_xlabel('Average Leontief coefficient (unitless; not a monetary flow)')
    ax.set_ylabel('Sector')
    ax.grid(axis='x', alpha=0.25)
    ax.set_axisbelow(True)
    fig.text(0.5, 0.015,
             '23 sectors; diagonal entries included. Descriptive score, not causal importance.',
             ha='center', fontsize=10)
    fig.tight_layout(rect=(0, 0.04, 1, 1))
    return fig


def plot_tree_importance(model, columns, aliases, target, years, n_countries, n_train):
    importance = model.feature_importances_
    indices = np.argsort(importance)[::-1]
    indices = indices[importance[indices] > 0][:20][::-1]
    labels = []
    for i in indices:
        source, destination = columns[i].split('->', 1)
        labels.append(f'{aliases.get(source, source)} -> {aliases.get(destination, destination)}')
    fig, ax = plt.subplots(figsize=(12, max(5, 2.4 + len(indices) * 0.36)))
    ax.barh(labels, importance[indices], color='#466b9e')
    ax.set_title(f'Decision-tree feature importance | {target}\n'
                 f'{n_countries} countries, {min(years)}-{max(years)}; '
                 f'random 80/20 split ({n_train} training observations)', pad=14)
    ax.set_xlabel('Normalized impurity reduction (unitless)')
    ax.set_ylabel('Leontief entry: output sector -> final-demand sector')
    ax.grid(axis='x', alpha=0.25)
    ax.set_axisbelow(True)
    fig.text(0.5, 0.015,
             'Up to 20 nonzero features shown. Model-specific importance, not flow size or causality.',
             ha='center', fontsize=10)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    return fig
