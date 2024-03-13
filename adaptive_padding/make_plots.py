from typing import Dict, List
from sys import argv

from adaptive_padding.utils.graphs.graph import make_barplot, make_scatterplot, sort_values

import json
from glob import glob


def load_file(filepath: str):
    with open(filepath, mode="r") as file_reader:
        return json.load(file_reader)


def organize_data(performance: Dict[str, str], metric_name: str):
    algorithms_map = {
        "RandomForestClassifier()": "Random Forest",
        "SVC()": "SVM",
        "DecisionTreeClassifier()": "DT",
        "KNeighborsClassifier()": "KNN"}
    algorithm_names = []
    average_accuracy = []
    strategies = []
    for algorithm in algorithms_map.keys():
        average_accuracy_per_algorithm = []
        strategies_per_algorithm = []
        for strategy in performance:
            algorithm_names.append(algorithms_map[algorithm])
            average_accuracy_per_algorithm.append(get_performance(
                algorithm,
                performance,
                strategy,
                metric_name))
            strategies_per_algorithm.append(strategy)
        strategies_per_algorithm, average_accuracy_per_algorithm =\
            sort_values(strategies_per_algorithm, average_accuracy_per_algorithm)
        average_accuracy.extend(average_accuracy_per_algorithm)
        strategies.extend(strategies_per_algorithm)
    return algorithm_names, average_accuracy, strategies


def get_performance(algorithm: str, performance: Dict[str, str], strategy: str, metric_name: str):
    return list(
        filter(
            lambda d: d["name"] == algorithm,
            performance[strategy]
            )
        )[0][metric_name] * 100


def main():
    files: List[str] = glob(argv[1])
    performance = {}
    for file in files:
        performance[file.split("_")[0]] = load_file(file)
    metric_names = {"Average accuracy": "Accuracy", "Average recall": "Recall", "Average f1_score": "F1 score"}
    byte_overhead = load_file(argv[2])
    for metric_name, metric_label in metric_names.items():
        algorithm_names, average_accuracy, strategies = organize_data(performance, metric_name)
        make_barplot(
            algorithm_names,
            average_accuracy,
            x_label="Classifier",
            y_label=f"{metric_label} (%)",
            filename=f"{metric_name.replace(' ', '_')}.png",
            hue=strategies)
        byte_overhead_per_strategy = [byte_overhead[strategy] * 100 for strategy in strategies]
        make_scatterplot(
            average_accuracy,
            byte_overhead_per_strategy,
            x_label=f"{metric_label} (%)",
            y_label="Byte overhead (%)",
            filename=f"byte_overhead_{metric_name.replace(' ', '_')}.png",
            hue=algorithm_names,
            style=strategies)
        unique_strategies = list(set(strategies))
        byte_overhead_strategy = [byte_overhead[strategy] * 100 for strategy in unique_strategies]
        make_barplot(
            unique_strategies,
            byte_overhead_strategy,
            x_label="strategies",
            y_label="byte overhead (%)",
            filename="byte_overhead.png",
            hue=unique_strategies,
            order=True)


if __name__ == "__main__":
    main()
