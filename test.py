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

def predict_on_testdata(model, data_module):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    predictions = []
    test_stream = data_module.test_dataloader()

    with torch.no_grad():
        for example in test_stream:
            batch = {k: v.to(device) for k, v, in example.items()}            
            loss, logits = model(batch["input_ids"], batch["attention_mask"])       
            predictions.append(torch.argmax(logits, dim=1).cpu().numpy())               # TODO HUH?

    return np.concatenate(predictions)

# Run
data_module = train_util.CustomDataModule(train_dataset_names,test_dataset_names, DIR, batch_size=config["batch_size"])
data_module.setup()
model= 0    # TODO load saved model  
predictions = predict_on_testdata(model, data_module)

# TODO Evaluation? Welche Metrik?