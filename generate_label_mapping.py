import random
import os
import json
import tqdm
from collections import defaultdict

from os import listdir
from datasets import load_dataset
from transformers import RobertaTokenizer

LIST_OF_DATASETS = listdir("datasets")
DIR = "datasets"
TRAIN_PERCENTAGE = 0.8
TEST_PERCENTAGE = 0.2

random.shuffle(LIST_OF_DATASETS)
SPLIT_CUTOFF = int(len(LIST_OF_DATASETS) * TRAIN_PERCENTAGE)

train_dataset_names  = LIST_OF_DATASETS[:SPLIT_CUTOFF]
test_dataset_names = LIST_OF_DATASETS[SPLIT_CUTOFF:]

tokenizer = RobertaTokenizer.from_pretrained("roberta-base")

def build_label_mapping(dataset_names, dir_path, save_path="label_mapping.json"):
    unique_labels = set()
    label_counts = defaultdict(int)  # To count occurrences of each main_category
    for file_name in tqdm.tqdm(dataset_names):
        filepath = os.path.join(dir_path, file_name)
        dataset = load_dataset("csv", data_files=filepath, split="train", streaming=True)
        for example in dataset:
            if "main_category" in example:
                main_category = example["main_category"]
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

    label_mapping = {label: idx for idx, label in enumerate(sorted(unique_labels))}

    with open(save_path, "w") as file:
        json.dump(label_mapping, file)

    return label_mapping

labels = build_label_mapping(train_dataset_names, DIR, save_path="label_mapping.json")
