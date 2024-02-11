from typing import List

from seaborn import barplot, color_palette, set_style
import matplotlib.pyplot as plt

set_style("whitegrid")

NUMBER_ALGORITHMS: int = 4

def make_barplot(x, y, x_label: str, y_label: str, filename: str, hue: List[str]):
    plt.figure(figsize=(14, 6))
    palette = color_palette("colorblind", n_colors=len(x) // NUMBER_ALGORITHMS)
    barplot(x=x, y=y, hue=hue, palette=palette)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 1.05),
        ncol=len(x),
        fancybox=True,
        shadow=True)
    plt.savefig(filename, bbox_inches="tight")
