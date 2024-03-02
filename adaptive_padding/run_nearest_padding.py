from os.path import join
from typing import Dict

from adaptive_padding.experiment.evaluation import PaddingExperiment
from adaptive_padding.padding.padding_strategy import PaddingStrategy
from adaptive_padding.padding.strategies_mapping_factory import create_nearest_strategies_mapping
from adaptive_padding.constants import FolderPath


def main():
    strategies: Dict[str, PaddingStrategy] = create_nearest_strategies_mapping()
    experiment = PaddingExperiment(
        FolderPath.RAW_DATA.value,
        join(FolderPath.PADDING_DATA.value, "Proposal"),
        5,
        strategies)
    experiment.execute()


if __name__ == "__main__":
    main()
