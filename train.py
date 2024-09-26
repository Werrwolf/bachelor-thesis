import numpy as np
import random
import os
import torch
import warnings
import train_util

import torch.nn as nn
import json
import torch.optim as optim

from os import listdir
from datasets import load_dataset
from transformers import RobertaTokenizer
from torch.utils.data import Dataset
from transformers import AutoModel
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from torch.optim.lr_scheduler import CosineAnnealingLR
from transformers import logging as transformers_logging

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
transformers_logging.set_verbosity_error()
warnings.filterwarnings(
    'ignore',
    message="The dataloader, val_dataloader 0, does not have many workers which may be a bottleneck."
)

LIST_OF_DATASETS = listdir("/home/q524745/bachelor_thesis/ten_ds")
DIR = "ten_ds"  ## TODO change
TRAIN_PERCENTAGE = 0.8
TEST_PERCENTAGE = 0.2

random.shuffle(LIST_OF_DATASETS)

SPLIT_CUTOFF = int(len(LIST_OF_DATASETS) * TRAIN_PERCENTAGE)

train_dataset_names  = LIST_OF_DATASETS[:SPLIT_CUTOFF]
test_dataset_names = LIST_OF_DATASETS[SPLIT_CUTOFF:]

tokenizer = RobertaTokenizer.from_pretrained("roberta-base")

config = {
    "learning_rate": 1e-5, 
    "weight_decay": 0.01,
    "n_epochs": 1,
    "batch_size": 16            # depends on memory
}


if __name__ == "__main__":
    # # Init data module and model
    data_module = train_util.CustomDataModule(train_dataset_names,test_dataset_names, DIR, batch_size=config["batch_size"])
    data_module.setup()
    n_labels=len(data_module.label_mapping)
    model = train_util.RoBERTaClassifier(n_labels=n_labels)

    # Train model
    trained_model = train_util.train_model(model, data_module, config)

    # # Predict on test set
    # predictions = predict_on_testdata(trained_model, data_module)
    # # print(f"Predictions on test set: {predictions}")

    # print("Training and Predictions completed")