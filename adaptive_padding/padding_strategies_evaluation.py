import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from os import cpu_count
from os.path import join
from random import seed
from typing import Tuple

import numpy as np
import pandas as pd
import typer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, recall_score, f1_score
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from tqdm import tqdm

from adaptive_padding.constants import FolderPath, ATTACKER
from adaptive_padding.experiment.evaluation import ExperimentConfiguration

logging.basicConfig(level=logging.INFO)

seed(42)


class Experiment:
	def __init__(self, padding_strategy, ground_truth_folder_features, padding_folder_features):
		"""
		Initializes the variables used throughout the experiment. 
		
		Parameters:
		paddingStrategy: padding strategy evaluated (can take the following values: 100, 500, 700, 900, Exponential, Linear, Mouse_elephant, Random, Random255, and MTU).
		groundTruthFolderFeatures: folder where files with IoT traffic features are located;
		paddingFolderFeatures: folder where the files with traffic features modified by the padding strategy are located.
		"""
		self.filenames = [
			'16-09-23.csv',
			'16-09-24.csv',
			'16-09-25.csv',
			'16-09-26.csv',
			'16-09-27.csv',
			'16-09-28.csv',
			'16-09-29.csv',
			'16-09-30.csv',
			'16-10-01.csv',
			'16-10-02.csv',
			'16-10-03.csv',
			'16-10-04.csv',
			'16-10-05.csv',
			'16-10-06.csv',
			'16-10-07.csv',
			'16-10-08.csv',
			'16-10-09.csv',
			'16-10-10.csv',
			'16-10-11.csv',
			'16-10-12.csv']
		self.__padding_strategy = padding_strategy
		self.__ground_truth_folder_features = ground_truth_folder_features
		self.__padding_folder_features = padding_folder_features

		self.rfc = RandomForestClassifier()
		self.svc = SVC()
		self.dtc = DecisionTreeClassifier()
		self.knn = KNeighborsClassifier(n_neighbors=5)
		self.skf = StratifiedKFold(n_splits=10)

		self.rfc_dict = [[], [], []]
		self.svc_dict = [[], [], []]
		self.dtc_dict = [[], [], []]
		self.knn_dict = [[], [], []]

		self.classifiers = {
			self.rfc: self.rfc_dict,
			self.svc: self.svc_dict,
			self.dtc: self.dtc_dict,
			self.knn: self.knn_dict}

	def compute_classifier_performance(self) -> Tuple[float, float, float]:
		"""
		Calculates accuracy, recall, and F1-score metric values. 
		"""
		self.accuracy = accuracy_score(self.y_test, self.y_pred)
		self.recall = recall_score(self.y_test, self.y_pred, average='micro')
		self.f1_measurement = f1_score(self.y_test, self.y_pred, average='micro')
		return self.accuracy, self.recall, self.f1_measurement

	def write_file(self, classifier, traffic_filename, filename):
		"""
		Write the values of the accuracy, recall, and F1-score metrics in a text file.  

		Parameters:
		classifier: classifier name.
		trafficFilename: name of the CSV file that stores the data coming from the IoT traffic. 
		filename: file name in which accuracy, recall, and F1-score metric values are written.
		"""
		with open(filename, mode='a') as file_writer:
			file_writer.write(f"{traffic_filename} ------ {classifier}.\n")
			file_writer.write(f"accuracy: {self.accuracy}.\n")
			file_writer.write(f"recall: {self.recall}.\n")
			file_writer.write(f"f1_score: {self.f1_measurement}.\n")
			file_writer.write("\n\n######################################")
	
	def update_classifiers_performance(self, classifier):
		"""
		Stores the accuracy, recall and F1-score for each classifier evaluated in each analyzed dataset. 

		Parameters:
		classifier: name of the evaluated classifier. 
		""" 
		self.classifiers[classifier][0].append(self.accuracy)
		self.classifiers[classifier][1].append(self.recall)
		self.classifiers[classifier][2].append(self.f1_measurement)
	
	def save_classifiers_performance_to_file(self, filename: str):
		"""
		It stores the average, minimum and maximum values of accuracy, recall and F1-score metrics for each evaluated classifier in a file. 

		Parameters:
		filename: name of the file in which the results obtained in the experiment will be stored. 
		"""
		classifiers_performance = []
		for classifier in self.classifiers:
			performance = {
				"name": str(classifier),
				"Average accuracy": np.mean(self.classifiers[classifier][0]),
				"Min accuracy": np.min(self.classifiers[classifier][0]),
				"Max accuracy": np.max(self.classifiers[classifier][0]),
				"Average recall": np.mean(self.classifiers[classifier][1]),
				"Min recall": np.min(self.classifiers[classifier][1]),
				"Max recall": np.max(self.classifiers[classifier][1]),
				"Average f1_score": np.mean(self.classifiers[classifier][2]),
				"Min f1_score": np.min(self.classifiers[classifier][2]),
				"Max f1_score": np.max(self.classifiers[classifier][2])
			}
			classifiers_performance.append(performance)

		with open(filename, mode="w") as file_writer:
			json.dump(classifiers_performance, file_writer)

	def run_train_test_split(self):
		"""
		It performs an experiment in which classifiers are trained with features calculated from the original IoT traffic, while testing these models with features calculated from the traffic changed by padding strategy. 
		"""
		for filename in tqdm(self.filenames):
			self.train_data = pd.read_csv(os.path.join(self.__ground_truth_folder_features, f"{filename}.tar.xz_features.csv"))
			self.test_data = pd.read_csv(os.path.join(self.__padding_folder_features, self.__padding_strategy, f"{filename.replace('.csv', '.xz')}_features.csv"))

			self.X_train = self.train_data[['avg', 'std', 'total']]
			self.y_train = self.train_data['label']

			self.X_test = self.test_data[['avg', 'std', 'total']]
			self.y_test = self.test_data['label']

			with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
				executor.map(
					lambda cls: cls.fit(self.X_train, self.y_train),
					self.classifiers)


			for classifier in self.classifiers:
				self.y_pred = classifier.predict(self.X_test)
				self.accuracy, self.recall, self.f1_measurement = self.compute_classifier_performance()
				self.update_classifiers_performance(classifier)
				self.write_file(classifier, filename, f"{self.__padding_strategy}_train_test_split.txt")

		self.save_classifiers_performance_to_file(f"{self.__padding_strategy}_train_test_split.json")

	def run_cross_validation(self):
		"""
		Evaluates classifiers only on the attributes of traffic changed by padding strategies. 
		Models are trained and tested on the same datasets using the cross-validation technique. 
		"""
		for filename in tqdm(self.filenames):
			self.test_data = pd.read_csv(os.path.join(
				self.__padding_folder_features,
				self.__padding_strategy,
				f"{filename.replace('.csv', '.xz')}_features.csv"))

			self.X = self.test_data[['avg', 'std', 'total']].values
			self.y = self.test_data['label'].values

			for train_index, test_index in self.skf.split(self.X, self.y):
				self.X_train, self.X_test = self.X[train_index], self.X[test_index]
				self.y_train, self.y_test = self.y[train_index], self.y[test_index]

				with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
					executor.map(
						lambda cls: cls.fit(self.X_train, self.y_train),
						self.classifiers)

				for classifier in self.classifiers:
					self.y_pred = classifier.predict(self.X_test)
					self.accuracy, self.recall, self.f1_measurement = self.compute_classifier_performance()
					self.update_classifiers_performance(classifier)
					self.write_file(classifier, filename, f"{self.__padding_strategy}_cross_validation.txt")

		self.save_classifiers_performance_to_file(f"{self.__padding_strategy}_cross_validation.json")


def main(filename: str = "", attacker: str = ""):
	configuration_file = os.path.join(FolderPath.CONFIGURATION.value, filename)
	experiment_configuration = ExperimentConfiguration()
	setup = experiment_configuration.load_configuration(configuration_file)
	strategies = setup["padding_strategies"]
	for strategy in strategies:
		print(f"Evaluating strategy {strategy}.")
		experiment = Experiment(
			padding_strategy=strategy,
			ground_truth_folder_features=join(FolderPath.GROUND_TRUTH_FEATURES.value),
			padding_folder_features=join(FolderPath.PADDING_FEATURES.value))
		if attacker == ATTACKER.EXTERNAL.value:
			experiment.run_train_test_split()
		elif attacker == ATTACKER.INTERNAL.value:
			experiment.run_cross_validation()


if __name__ == "__main__":
	typer.run(main)
