import os
import json
import tqdm
from collections import defaultdict
import unicodedata
import matplotlib.pyplot as plt
import warnings
import numpy as np
from os import listdir
from datasets import load_dataset

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
DIR = "datasets"

def normalize_text(text):
    """Normalize text by removing leading/trailing whitespaces, converting to lower case, and removing non-ASCII characters."""
    if text is None:
        return None
    # Normalize unicode characters and strip leading/trailing whitespace
    return unicodedata.normalize("NFKC", text).strip().lower()

def build_label_mapping(dir_path, save_path="label_mapping.json"):
    dataset_names = listdir(DIR)
    unique_labels = set()
    label_counts = defaultdict(int)  # To count occurrences of each main_category
    for file_name in tqdm.tqdm(dataset_names):
        filepath = os.path.join(dir_path, file_name)
        dataset = load_dataset("csv", data_files=filepath, split="train", streaming=True)
        for example in dataset:
            if "main_category" in example:
                main_category = normalize_text(example["main_category"])  # Normalize category
                if main_category is None:  # Check if main_category is None
                    print(f"Found None for 'main_category' in file: {file_name}")
                else:
                    label_counts[main_category] += 1  # Increment count
                    unique_labels.add(main_category)
            else:
                print(f"'main_category' not found in file: {file_name}")

    print(f"Unique labels: {len(unique_labels)}")
    print("Distribution of main categories:")
    for label, count in label_counts.items():
        print(f"{label}: {count} occurrences")

    # Assuming label_counts is already defined and populated
    # Sorting labels and counts by count value
    sorted_labels_counts = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_labels, sorted_counts = zip(*sorted_labels_counts)
    sorted_counts = list(sorted_counts)
    label_mapping = {label: idx for idx, label in enumerate(sorted(unique_labels))}
    with open(save_path, "w") as file:
        json.dump(label_mapping, file)

    # Logarithmic Bar Chart
    plt.figure(figsize=(12, 6))
    plt.barh(sorted_labels, sorted_counts, color='skyblue')
    plt.xscale('log')  # Use a logarithmic scale on the x-axis
    plt.xlabel('Occurrences (Log Scale)')
    plt.ylabel('Main Categories')
    plt.title('Distribution of Main Categories (Log Scale)')
    plt.tight_layout()
    plt.show()

    # Cumulative Distribution Plot
    cumulative_counts = np.cumsum(sorted_counts)
    plt.figure(figsize=(12, 6))
    plt.plot(sorted_labels, cumulative_counts, marker='o')
    plt.xticks(rotation=90)
    plt.xlabel('Main Categories (Sorted)')
    plt.ylabel('Cumulative Occurrences')
    plt.title('Cumulative Distribution of Main Categories')
    plt.tight_layout()
    plt.show()

    return label_mapping

if __name__ == "__main__":
    labels = build_label_mapping(DIR, save_path="label_mapping.json")
    print("done")