from typing import List, Any, Tuple

from seaborn import barplot, color_palette, set_style, scatterplot
import matplotlib.pyplot as plt

set_style("whitegrid")

NUMBER_ALGORITHMS: int = 4


def _sort_values(x, y) -> Tuple[List[Any], List[Any]]:
    zipped = zip(y, x)
    sorted_values = sorted(zipped, reverse=True)
    sorted_x = [x for _, x in sorted_values]
    sorted_y = [y for y, _ in sorted_values]
    return sorted_x, sorted_y


def setup_graph(func):
    def wrapper(*args, **kwargs):
        plt.figure(figsize=(14, 6))
        func(*args, **kwargs)
        plt.xlabel(kwargs["x_label"])
        plt.ylabel(kwargs["y_label"])
        plt.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.05),
            ncol=len(args[1]),
            fancybox=True,
            shadow=True)
        plt.savefig(kwargs["filename"], bbox_inches="tight")
    return wrapper


@setup_graph
def make_barplot(x, y, x_label: str, y_label: str, filename: str, hue: List[str]):
    palette = color_palette("colorblind", n_colors=len(x) // NUMBER_ALGORITHMS)
    sorted_x, sorted_y = _sort_values(x, y)
    barplot(x=sorted_x, y=sorted_y, hue=hue, palette=palette)
    barplot(x=x, y=y, hue=hue, palette=palette,order=x)


@setup_graph
def make_scatterplot(x, y, x_label: str, y_label: str, filename: str, hue: List[str], style: List[str]):
    palette = color_palette("colorblind", n_colors=len(x) // NUMBER_ALGORITHMS)
    scatterplot(x=x, y=y, hue=hue, palette=palette, style=style)
    plt.ylim(min(y) * 0.9, max(y) * 1.10)
