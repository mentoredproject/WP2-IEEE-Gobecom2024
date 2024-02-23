from typing import Dict, List

from adaptive_padding.utils.graphs.graph import make_barplot, make_scatterplot

import json
from glob import glob


def load_file(filepath: str):
    with open(filepath, mode="r") as file_reader:
        return json.load(file_reader)


def organize_data(algorithms: List[str], performance: Dict[str, str], metric_name: str):
    algorithm_names = []
    average_accuracy = []
    strategies = []
    for algorithm in algorithms:
        for strategy in performance:
            algorithm_names.append(algorithm)
            average_accuracy.append(get_performance(
                algorithm,
                performance,
                strategy,
                metric_name))
            strategies.append(strategy)
    algorithm_names = list(map(
        lambda name: name.replace("()", ""),
        algorithm_names))
    return algorithm_names, average_accuracy, strategies


def get_performance(algorithm: str, performance: Dict[str, str], strategy: str, metric_name: str):
    return list(
        filter(
            lambda d: d["name"] == algorithm,
            performance[strategy]
            )
        )[0][metric_name] * 100


def main():
    files: List[str] = glob("*_train_test_split.json")
    performance = {}
    for file in files:
        performance[file.split("_")[0]] = load_file(file)
    algorithms = [
        "RandomForestClassifier()",
        "SVC()",
        "DecisionTreeClassifier()",
        "KNeighborsClassifier()"]
    metric_names = {"Average accuracy": "Accuracy", "Average recall": "Recall", "Average f1_score": "F1 score"}
    byte_overhead = load_file("byte_overhead.json")
    for metric_name, metric_label in metric_names.items():
        algorithm_names, average_accuracy, strategies = organize_data(algorithms, performance, metric_name)
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


if __name__ == "__main__":
    main()
