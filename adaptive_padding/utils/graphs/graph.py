import json
from sys import argv
from typing import List, Any, Tuple

from seaborn import barplot, color_palette, set_style, scatterplot
import matplotlib.pyplot as plt

set_style("whitegrid")

NUMBER_ALGORITHMS: int = 4


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class SingletonPalette:
    instance = None
    colors = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            data = json.load(open(argv[3], mode="r"))
            cls.colors = {key: value for key, value in zip(
                data["names"],
                color_palette("husl", n_colors=len(data["names"])))}
        return cls.instance


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
        plt.xlabel(kwargs["x_label"], fontsize=18)
        plt.ylabel(kwargs["y_label"], fontsize=18)
        plt.legend(
            loc="upper center",
            bbox_to_anchor=(0.5, 1.05),
            ncol=len(args[1]),
            fancybox=True,
            fontsize=14,
            shadow=True)
        plt.xticks(fontsize=18)
        plt.savefig(kwargs["filename"], bbox_inches="tight")
    return wrapper


@setup_graph
def make_barplot(
        x,
        y,
        x_label: str,
        y_label: str,
        filename: str,
        hue: List[str],
        strategy_names: List[str],
        order: bool = False):
    singleton_palette = SingletonPalette()
    colors = singleton_palette.colors
    if order:
        sorted_x, sorted_y = _sort_values(x, y)
        actual_hue = sorted_x
    else:
        sorted_x = x
        sorted_y = y
        actual_hue = hue
    barplot(x=sorted_x, y=sorted_y, hue=actual_hue, palette=colors)


@setup_graph
def make_scatterplot(x, y, x_label: str, y_label: str, filename: str, hue: List[str], style: List[str]):
    palette = color_palette("husl", n_colors=len(x) // NUMBER_ALGORITHMS)
    scatterplot(x=x, y=y, hue=hue, palette=palette, style=style)
    plt.ylim(min(y) * 0.9, max(y) * 1.10)
