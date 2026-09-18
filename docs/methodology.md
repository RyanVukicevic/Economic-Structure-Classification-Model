# Methodology and recorded results

## Research question

Can sector-to-sector economic relationships distinguish regional economies, and do classifiers trained on earlier country-year observations still recognize those regions in later years?

The original project combines descriptive economic analysis with supervised and unsupervised learning. It does not establish causal explanations for economic events or predict future GDP.

## Data representation

- Source: [Long-run WIOD, version 1.1](https://www.rug.nl/ggdc/valuechain/long-run-wiod).
- Coverage: 25 countries, 23 industry sectors, and 1965–2000 inclusive (**36 years**; some original slide text says 35).
- A complete country-year panel would contain **900 observations**, each represented by **529 matrix entries**.
- Source transaction values are in millions of current US dollars. The heatmap divides by 1,000 to show billions.
- The notebook maps ISIC sector codes to descriptions, selects same-country rows and columns, and groups countries into Europe (14), Asia-Pacific (7), and Americas (4).
- Final-demand components are household consumption, government consumption, gross fixed capital formation, and inventory changes.

The matrices model domestic interindustry inputs. The current rerun normalizes them by reported gross output (`xTOT_xGO`), which includes production for export. Cross-border propagation is outside the model; this is not a full global trade model. Nominal-value trends also reflect price changes and cannot alone establish real economic growth.

## Leontief representation

For an appropriately balanced transaction matrix **Z**, with producing sectors in rows and consuming sectors in columns, total output is related to intermediate transactions and final demand by:

$$x_i = \sum_j Z_{ij} + y_i, \qquad A_{ij} = Z_{ij}/x_j, \qquad L = (I-A)^{-1}$$

Flattening each **L** supplies features for classification and clustering. The notebook's sector bar chart averages the row and column means of **L**. This is an exploratory linkage score, not a validated measure of causal sector importance or GDP contribution.

**Local rerun correction:** the original `compute_L()` used column sums plus domestic final demand as the output denominator. Even replacing column sums with row sums is insufficient: some export-heavy sectors have negative domestic totals after inventory adjustments. The local version uses WIOD's reported gross output (`xTOT_xGO`) for `x`, aligns all sector rows and columns explicitly, and sets the accounting residual `y = x - Z.sum(axis=1)`. Here `y` includes demand outside domestic intermediate use, including exports and source accounting adjustments; it is not just the four domestic final-demand columns.

Every country-year matrix is checked for finite inputs, positive gross output, `A @ x + y = x`, `L @ y = x`, and `(I - A) @ L = I`, with numerical tolerances. These identities verify computational consistency, not independent empirical validation of the economic model. The returned country dataframe now matches the query, fixing chart labels. The missing cache is rebuilt from the CSV every time.

## Experiment record

Values below are historical results transcribed from the presentation. New locally executed results are saved in the current notebook and `outputs/run_summary.json`; the numerical corrections mean the two sets of results are not expected to match exactly.

| Experiment | Train accuracy | Test accuracy | Presentation |
| --- | ---: | ---: | --- |
| KNN, all years, random split | — | 100% | Slide 21 |
| KNN, earlier years → later years | 99.85% | 94.8% | Slide 26 |
| KNN + 7-component PCA, earlier → later years | 100% | 86.4% | Slide 30 |
| Decision tree, random split | 100% | 98.33% | Slide 33 |

For the temporal experiments, the code uses `range(1965, 1991)` for training: **1965–1990 (26 years)**, with the remaining dataset years **1991–2000 (10 years)** for evaluation. With a complete panel, this is 650 training and 250 evaluation observations. Labels describe regions; future economic matrices are inputs at evaluation time.

KNN uses a grid search over neighbor counts and uniform/distance weighting. Decision trees search depth, minimum split size, minimum leaf size, and impurity criterion. PCA explores lower-dimensional representations. K-means explores whether unsupervised groups align with regional labels; labels are assigned to clusters by majority vote.

## What the evaluation supports—and its limits

1. **Repeated countries:** random country-year splits can put nearby years from the same country in training and testing. High random-split accuracy does not demonstrate generalization to unseen countries.
2. **Preprocessing leakage:** whole-data helpers standardize before the holdout split. Temporal helpers fit scaling on training years only, but scaling/PCA still occur outside the grid search's individual cross-validation folds. A revised evaluation should fit preprocessing inside each fold through a pipeline.
3. **Clustering evaluation:** the original subset clustering functions refitted on evaluation observations and derived cluster labels from evaluation labels. The local version now fits centers and label mappings on training observations, then predicts the holdout. The PCA clustering variant also reuses the training PCA transformation. Historical slide results remain descriptive clustering agreement; corrected holdout outputs are in the notebook.
4. **Unequal classes:** a classifier predicting Europe for every observation would achieve 56% accuracy on the complete panel. Class-specific recall, balanced accuracy, and macro F1 would give a fuller comparison.
5. **PCA interpretation:** the reported 8.4-point temporal accuracy drop is evidence about this configuration. It does not establish that dimensionality reduction is generally harmful.
6. **Historical explanations:** the slides suggest possible explanations for particular misclassifications. These are hypotheses, not tested causal findings.
7. **Presentation versus implementation:** slide 16 is a dashboard mockup; the implemented interface is notebook prompts. Slide 17 mentions random forests, but the inspected modeling implementation and reported tree results use a decision tree. This showcase describes the implemented methods.

## Remaining improvements

Use preprocessing pipelines, chronological validation within training years, and grouped evaluation by country. Report class-level metrics alongside accuracy and compare against simple baselines. Random-split and cross-validation preprocessing limitations above remain in this restoration of the original project.

Other execution fixes include importing metrics before use, bounding per-year neighbor counts to fit the small training folds, using three stratified folds for the small per-year training sets, deterministic tree/K-means seeds, retaining the fitted PCA for its demonstration, and keeping row order consistent in the final cluster visualization. The notebook's original interpretation paragraphs are historical commentary; use the new saved outputs when discussing the rerun.
