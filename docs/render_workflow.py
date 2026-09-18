"""Render the README workflow with fixed wrapping and portable vector text."""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


def main():
    destination = Path(__file__).resolve().parent / "images"
    plt.rcParams.update({"font.family": "DejaVu Sans", "svg.fonttype": "path"})
    fig, ax = plt.subplots(figsize=(8, 8.4), dpi=150)
    fig.patch.set_facecolor("#f8fafc")
    ax.set(xlim=(0, 800), ylim=(840, 0))
    ax.axis("off")
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    def card(x, y, width, height, title, lines, accent="#2563eb"):
        ax.add_patch(FancyBboxPatch(
            (x, y), width, height, boxstyle="round,pad=0,rounding_size=12",
            linewidth=1.3, edgecolor="#cbd5e1", facecolor="white", zorder=2))
        ax.plot([x + 18, x + 18], [y + 20, y + height - 20],
                color=accent, linewidth=3, solid_capstyle="round", zorder=3)
        ax.text(x + 36, y + 31, title, fontsize=14, fontweight="bold",
                color="#0f172a", va="center", zorder=3)
        for i, line in enumerate(lines):
            ax.text(x + 36, y + 60 + i * 25, line, fontsize=12,
                    color="#475569", va="center", zorder=3)

    def arrow(points):
        for first, last in zip(points[:-2], points[1:-1]):
            ax.plot([first[0], last[0]], [first[1], last[1]],
                    color="#64748b", linewidth=1.5, zorder=1)
        ax.add_patch(FancyArrowPatch(points[-2], points[-1],
                     arrowstyle="-|>", mutation_scale=14,
                     linewidth=1.5, color="#64748b", zorder=1))

    ax.text(400, 33, "FROM ECONOMIC DATA TO INSIGHT", ha="center",
            fontsize=12, fontweight="bold", color="#475569")
    card(155, 65, 490, 112, "WIOD transaction tables",
         ["25 countries  /  23 sectors", "Annual observations, 1965-2000"])
    card(155, 220, 490, 112, "Clean and organize",
         ["Standardize country-year data", "Map and align industry sectors"])
    arrow([(400, 177), (400, 220)])

    card(35, 390, 350, 137, "Interactive exploration",
         ["Choose a country and year", "View heatmaps and", "sector summary charts"], "#0d9488")
    card(415, 390, 350, 137, "Leontief matrices",
         ["Model industry dependencies", "23 x 23 entries become", "529 features per country-year"])
    arrow([(400, 332), (400, 360), (210, 360), (210, 390)])
    arrow([(400, 332), (400, 360), (590, 360), (590, 390)])

    card(35, 595, 350, 168, "KNN + decision trees",
         ["Classify geographic regions", "Evaluate on later years", "Inspect sector relationships"], "#7c3aed")
    card(415, 595, 350, 168, "PCA + K-means",
         ["Reduce dimensionality", "Explore economic groupings", "Assess class imbalance"], "#7c3aed")
    arrow([(590, 527), (590, 560), (210, 560), (210, 595)])
    arrow([(590, 527), (590, 595)])
    ax.text(400, 807, "Explore the data. Compare structures. Evaluate the models.",
            ha="center", fontsize=11, color="#64748b")

    fig.savefig(destination / "project-workflow.svg", metadata={"Date": None})
    fig.savefig(destination / "project-workflow.png")
    plt.close(fig)


if __name__ == "__main__":
    main()
