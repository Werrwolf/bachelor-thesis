import os
import json
import tqdm
from collections import defaultdict
import unicodedata
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
from os import listdir
from datasets import load_dataset

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
DIR = "datasets"

def normalize_text(text):
    """Normalize text by removing leading/trailing whitespaces, converting to lower case, and removing non-ASCII characters."""
    if text is None:
        return None
    return unicodedata.normalize("NFKC", text).strip().lower()

def build_label_mapping(dir_path, save_path="label_mapping.json"):
    dataset_names = listdir(DIR)
    unique_labels = set()
    label_counts = defaultdict(int)  # To count occurrences of each main_category
    total_occurrences = 0  # To calculate total occurrences of all categories

    for file_name in tqdm.tqdm(dataset_names):
        filepath = os.path.join(dir_path, file_name)
        dataset = load_dataset("csv", data_files=filepath, split="train", streaming=True)
        for example in dataset:
            if "main_category" in example:
                main_category = normalize_text(example["main_category"])
                if main_category is None:
                    print(f"Found None for 'main_category' in file: {file_name}")
                else:
                    label_counts[main_category] += 1
                    total_occurrences += 1
                    unique_labels.add(main_category)
            else:
                print(f"'main_category' not found in file: {file_name}")

    print(f"Unique labels: {len(unique_labels)}")
    print(f"Total occurrences across all categories: {total_occurrences}")
    print("Distribution of main categories:")

    # Calculate percentages and print stats
    label_percentages = {}
    for label, count in label_counts.items():
        percentage = (count / total_occurrences) * 100
        label_percentages[label] = percentage
        print(f"{label}: {count} occurrences ({percentage:.2f}%)")

    # Sorting labels, counts, and percentages
    sorted_labels_counts = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_labels, sorted_counts = zip(*sorted_labels_counts)
    sorted_percentages = [label_percentages[label] for label in sorted_labels]

    label_mapping = {label: idx for idx, label in enumerate(sorted(unique_labels))}
    with open(save_path, "w") as file:
        json.dump(label_mapping, file)

    # Create combined plots using gridspec
    fig = plt.figure(figsize=(14, 20))  # Adjust figure size
    gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1])  # Create 3 rows with equal height

    # Total Occurrences Bar Chart
    ax1 = fig.add_subplot(gs[0])
    ax1.barh(sorted_labels, sorted_counts, color='skyblue')
    ax1.set_title('Total Number of Occurrences', fontsize=14, pad=10)
    ax1.set_xlabel('Occurrences', fontsize=12)
    ax1.set_ylabel('Main Categories', fontsize=12)
    ax1.tick_params(axis='x', labelsize=10)
    ax1.tick_params(axis='y', labelsize=8)

    # Percentage Bar Chart
    ax3 = fig.add_subplot(gs[2])
    ax3.barh(sorted_labels, sorted_percentages, color='limegreen')
    ax3.set_title('Percentage of Total Occurrences', fontsize=14, pad=10)
    ax3.set_xlabel('Percentage (%)', fontsize=12)
    ax3.set_ylabel('Main Categories', fontsize=12)
    ax3.tick_params(axis='x', labelsize=10)
    ax3.tick_params(axis='y', labelsize=8)

    # Adjust layout with sufficient padding
    plt.tight_layout(pad=3.0, h_pad=5.0, w_pad=5.0)
    plt.show()

    return label_mapping

if __name__ == "__main__":
    labels = build_label_mapping(DIR, save_path="label_mapping.json")
    print("done")
