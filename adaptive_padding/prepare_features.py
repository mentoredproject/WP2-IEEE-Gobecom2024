'''
This script reads the CSV files, in which padding was applied or not, and generates the files with the statistics used in the paper 'Adaptive Packet Padding Approach for Smart Home Networks: A Tradeoff Between Privacy and Performance'.
'''
import glob
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from glob import glob
from os import cpu_count
from os.path import join, basename
from tempfile import TemporaryDirectory

import pandas as pd

from adaptive_padding.constants import FolderPath
from adaptive_padding.experiment.evaluation import ExperimentConfiguration
from adaptive_padding.utils.utils import create_folder


class Feature:
	def __init__(self, csv_folder, output_folder):
		self.__csv_folder = csv_folder
		self.__output_folder = output_folder
		self.__device_id_generator = Feature.generate_device_id()
		self.__devices_mac_addresses = [
			"d0:52:a8:00:67:5e",
			"44:65:0d:56:cc:d3",
			"70:ee:50:18:34:43",
			"f4:f2:6d:93:51:f1",
			"00:16:6c:ab:6b:88",
			"30:8c:fb:2f:e4:b2",
			"00:62:6e:51:27:2e",
			"00:24:e4:11:18:a8",
			"ec:1a:59:79:f4:89",
			"50:c7:bf:00:56:39",
			"74:c6:3b:29:d7:1d",
			"ec:1a:59:83:28:11",
			"18:b4:30:25:be:e4",
			"70:ee:50:03:b8:ac",
			"00:24:e4:1b:6f:96",
			"74:6a:89:00:2e:25",
			"00:24:e4:20:28:c6",
			"d0:73:d5:01:83:08",
			"18:b7:9e:02:20:44",
			"e0:76:d0:33:bb:85",
			"70:5a:0f:e4:9b:c0"]
		self.devices = {device_address: next(self.__device_id_generator) for device_address in self.__devices_mac_addresses}
		self.__temporary_directory: TemporaryDirectory = TemporaryDirectory()

	@staticmethod
	def generate_device_id():
		device_id = 0
		while True:
			yield device_id
			device_id += 1

	def encode_labels(self, dataset: pd.DataFrame) -> pd.DataFrame:
		"""
		Converts the MAC address of IoT devices into integer labels. 

		Parameters:
		dataset: dataset with IoT traffic.

		Returns:
		a dataset with MAC addresses of IoT devices mapped to integer labels.
		"""
		for device in self.devices:
			dataset["src_mac"] = dataset["src_mac"].replace(device, self.devices[device])
		return dataset

	@staticmethod
	def filter_iot_devices(dataset: pd.DataFrame) -> pd.DataFrame:
		"""
		Selects only the IoT devices present in the analyzed data.

		Parameters:
		dataset: dataset with IoT traffic.

		Returns:
		a dataset that contains only samples coming from IoT devices. 
		"""
		return dataset[dataset['src_mac'].astype(str).str.isdigit()]

	def remove_temporary_files(self) -> None:
		"""
		Discards temporary files.  
		"""
		self.__temporary_directory.cleanup()

	def save_file(self, dataset: pd.DataFrame, filepath: str) -> None:
		"""
		Stores calculated features in a file. 

		Parameters:
		dataset: dataset with IoT traffic.
		filepath: path to the CSV file where the data will be stored. 
		"""
		dataset.to_csv(join(self.__output_folder, f"{basename(filepath)}_features.csv"), sep=",", index=False)

	def group_samples_per_second(self, dataset: pd.DataFrame) -> None:
		"""
		Calculates the average, standard deviation, and number of bytes statistics for the packet length grouped at one-second intervals. 

		Parameters:
		dataset: dataset with IoT traffic.
		"""
		dataset["Length"] = dataset["Length"].astype('int')
		group = dataset.groupby(by=["src_mac", "Time"])
		group.mean()["Length"].to_csv(
			join(self.__temporary_directory.name, "length_avg.csv"),
			sep=",",
			header=False)
		group.sum()["Length"].to_csv(
			join(self.__temporary_directory.name, "length_sum.csv"),
			sep=",",
			header=False)
		group.std()["Length"].to_csv(
			join(self.__temporary_directory.name, "length_std.csv"),
			sep=",",
			header=False)

	@staticmethod
	def load_dataset(filename: str) -> pd.DataFrame:
		"""
		Loads a CSV file containing the IoT traffic in the following format: each measurement corresponds to seconds from the start of capture. 
		At a minimum, the following columns must be present in the datasets: source MAC address, frame/packet size and time instant when the capture was performed. 

		Parameters:
		filename: name of the CSV file that stores the data to be loaded. 
		"""
		return pd.read_csv(
			filename,
			low_memory=False,
			encoding="iso-8859-1")[["src_mac", "Time", "Length"]]

	def create_features(self) -> pd.DataFrame:
		"""
		Builds a dataset from statistics calculated based on packet length. 
		"""		
		features = pd.DataFrame()
		features["avg"] = pd.read_csv(
			join(self.__temporary_directory.name, "length_avg.csv"),
			names=["label", "Time", "Length"])["Length"]
		features["std"] = pd.read_csv(
			join(self.__temporary_directory.name, "length_std.csv"),
			names=["label", "Time", "Length"])["Length"]
		features["total"] = pd.read_csv(
			join(self.__temporary_directory.name, "length_sum.csv"),
			names=["label", "Time", "Length"])["Length"]
		features["label"] = pd.read_csv(
			join(self.__temporary_directory.name, "length_avg.csv"),
			names=["label", "Time", "Length"])["label"]
		return features


def process_file(csv_folder: str, output_folder: str, filename: str):
	features = Feature(csv_folder, output_folder)
	dataset = Feature.load_dataset(filename)
	dataset = features.encode_labels(dataset)
	dataset = Feature.filter_iot_devices(dataset)
	dataset.drop(dataset["Length"][dataset["Length"] == "None"].index, inplace=True)
	features.group_samples_per_second(dataset)
	iot_features = features.create_features()
	iot_features.dropna(inplace=True)
	features.save_file(iot_features, filename)
	features.remove_temporary_files()


def iterate_over_files(csv_folder: str, output_folder: str):
	files = glob(join(csv_folder, "*.xz"))
	partial_process_file = partial(process_file, csv_folder, output_folder)
	with ProcessPoolExecutor(max_workers=cpu_count()) as executor:
		executor.map(partial_process_file, files)


def main():
	configuration_file = join(FolderPath.CONFIGURATION.value, "experiment_configuration.json")
	setup = ExperimentConfiguration.load_configuration(configuration_file)

	if setup["padding"] != "None" and setup["padding_strategies"] != "None":
		padding_strategies = setup["padding_strategies"]
		for padding_strategy in padding_strategies:
			print(f"Preparing features for strategy: {padding_strategy}.")
			csv_folder = join(FolderPath.PADDING_DATA.value, setup["padding"], padding_strategy)
			output_folder = join(FolderPath.PADDING_FEATURES.value, padding_strategy)
			create_folder(output_folder)
			iterate_over_files(csv_folder, output_folder)
	else:
		csv_folder = FolderPath.RAW_DATA.value
		output_folder = FolderPath.GROUND_TRUTH_FEATURES.value
		create_folder(output_folder)
		iterate_over_files(csv_folder, output_folder)


if __name__ == "__main__":
	main()
