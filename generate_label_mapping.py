import random
import os
import json
import tqdm

from os import listdir
from datasets import load_dataset
from transformers import RobertaTokenizer


LIST_OF_DATASETS = listdir("/home/q524745/bachelor_thesis/datasets")
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
    for file_name in tqdm.tqdm(dataset_names):
        filepath = os.path.join(dir_path, file_name)
        dataset = load_dataset("csv", data_files=filepath, split="train", streaming=True)
        for example in dataset:
            if "main_category" in example: 
                unique_labels.add(example["main_category"])
    print(f"Unique labels: {len(unique_labels)}")
    label_mapping = {label:idx for idx, label in enumerate(sorted(unique_labels))}

    with open(save_path, "w") as file:
        json.dump(label_mapping, file)

    return label_mapping

labels = build_label_mapping(train_dataset_names, DIR, save_path="label_mapping.json")

print("done")