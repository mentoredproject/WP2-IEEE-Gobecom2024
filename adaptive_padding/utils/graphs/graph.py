import json
from sys import argv
from typing import List, Any, Tuple, Union

from matplotlib.axes import Axes
from seaborn import barplot, color_palette, set_style, scatterplot
import matplotlib.pyplot as plt
plt.rcParams['figure.dpi'] = 300

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


def sort_values(x, y) -> Tuple[List[Any], List[Any]]:
    zipped = zip(y, x)
    sorted_values = sorted(zipped, reverse=True)
    sorted_x = [x for _, x in sorted_values]
    sorted_y = [y for y, _ in sorted_values]
    return sorted_x, sorted_y


def setup_graph(func):
    def wrapper(*args, **kwargs):
        plt.figure(figsize=(14, 6))
        func(*args, **kwargs)
        plt.xlabel(kwargs["x_label"], fontsize=20)
        plt.ylabel(kwargs["y_label"], fontsize=20)
        plt.legend(
            loc="lower left",
            bbox_to_anchor=(0.9, 0.5),
            ncol=1,
            fancybox=True,
            fontsize=18,
            shadow=True)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.savefig(kwargs["filename"], bbox_inches="tight")
    return wrapper


def set_y_lim(y_lim: Tuple[Union[float, int]] = None):
    if y_lim is not None:
        plt.ylim(*y_lim)

def add_labels(ax: Axes):
    for i in ax.containers:
        ax.bar_label(i, )

@setup_graph
def make_barplot(
        x,
        y,
        x_label: str,
        y_label: str,
        filename: str,
        hue: List[str],
        order: bool = False,
        y_lim: Tuple[int, int] = None):
    singleton_palette = SingletonPalette()
    colors = singleton_palette.colors
    if order:
        sorted_x, sorted_y = sort_values(x, y)
        actual_hue = sorted_x
    else:
        sorted_x = x
        sorted_y = y
        actual_hue = hue
    rounded_values = list(map(lambda a: round(a, 2), sorted_y))
    ax = barplot(x=sorted_x, y=rounded_values, hue=actual_hue, palette=colors)
    add_labels(ax)
    set_y_lim(y_lim)


@setup_graph
def make_scatterplot(x, y, x_label: str, y_label: str, filename: str, hue: List[str], style: List[str]):
    palette = color_palette("husl", n_colors=len(x) // NUMBER_ALGORITHMS)
    scatterplot(x=x, y=y, hue=hue, palette=palette, style=style)
    plt.ylim(min(y) * 0.9, max(y) * 1.10)
