import glob
import json
from glob import glob
from os.path import join
from typing import Dict

import pandas as pd

from adaptive_padding.constants import FolderPath
from adaptive_padding.experiment.evaluation import ExperimentConfiguration
from adaptive_padding.prepare_features import Feature


def process_file(csv_folder: str, output_folder: str, filename: str) -> pd.DataFrame:
	features = Feature(csv_folder, output_folder)
	dataset = Feature.load_dataset(filename)
	dataset = features.encode_labels(dataset)
	dataset = Feature.filter_iot_devices(dataset)
	dataset.drop(dataset["Length"][dataset["Length"] == "None"].index, inplace=True)
	return dataset


def iterate_over_files(csv_folder: str, output_folder: str) -> pd.DataFrame:
	dataset = pd.DataFrame()
	files = glob(join(csv_folder, "*.xz"))
	for filename in files:
		data = process_file(csv_folder, output_folder, filename)
		dataset = pd.concat([dataset, data])
	return dataset


def process_raw_data() -> int:
	csv_folder = FolderPath.RAW_DATA.value
	output_folder = FolderPath.GROUND_TRUTH_FEATURES.value
	data = iterate_over_files(csv_folder, output_folder)
	return data["Length"].sum()


def process_padding_data(padding: str, padding_strategy: str) -> int:
	csv_folder = join(FolderPath.PADDING_DATA.value, padding, padding_strategy)
	output_folder = join(FolderPath.PADDING_FEATURES.value, padding_strategy)
	data = iterate_over_files(csv_folder, output_folder)
	return data["Length"].sum()


def write_file(filename: str, overhead: Dict[str, float]):
	with open(filename, mode="w") as file_writer:
		json.dump(overhead, file_writer)


def main():
	configuration_file = join(FolderPath.CONFIGURATION.value, "experiment_configuration.json")
	setup = ExperimentConfiguration.load_configuration(configuration_file)
	raw_data_length = process_raw_data()
	byte_overhead = {}

	padding_strategies = setup["padding_strategies"]
	for padding_strategy in padding_strategies:
		padding_data_length = process_padding_data(setup["padding"], padding_strategy)
		byte_overhead[padding_strategy] = padding_data_length / raw_data_length
	write_file("byte_overhead.json", byte_overhead)


if __name__ == "__main__":
	main()
