import numpy as np
import random
import os
import torch
import warnings

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

"""
Why use CosineAnnealingLR: 

CosineAnealingLR is a scheduling strategy for the learning rate that adjusts the learning rate dynamically/gradually during training (based on a cosine curve). 
This helps for more efficient training and avoids overfitting, especially for many training epochs. For a small number of epochs (below 10) it could be better 
to use another scheduler(e.g. StepLR, ExponentialLR, ReduceOnPlateauLR).
here specifically, the learning rate starts at config["learning_rate"] and decreases gradually until almost zero (eta_min=1e-6). 
    "warm restarts": Learning rate decays to low value but jumps back up to a higher value for a new epoch. (Higher than the value it decayed to, but lower than the initial start).
                    Helps avoid getting stuck in local minimas.
    Without: Learning rate decays gradually over all epochs.
"""


LIST_OF_DATASETS = listdir("/home/q524745/bachelor_thesis/datasets")
DIR = "datasets"  ## TODO change
TRAIN_PERCENTAGE = 0.8
TEST_PERCENTAGE = 0.2

random.shuffle(LIST_OF_DATASETS)

SPLIT_CUTOFF = int(len(LIST_OF_DATASETS) * TRAIN_PERCENTAGE)

train_dataset_names  = LIST_OF_DATASETS[:SPLIT_CUTOFF]
test_dataset_names = LIST_OF_DATASETS[SPLIT_CUTOFF:]

tokenizer = RobertaTokenizer.from_pretrained("roberta-base")

############################################################# Label Mapping #####################################################

def build_label_mapping(dataset_names, dir_path, save_path="label_mapping.json"):
    unique_labels = set()
    for file_name in dataset_names:
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


def load_label_mapping(file_path="label_mapping.json"):
    with open(file_path, "r") as file:
        label_mapping=json.load(file)
    return label_mapping

############################################################# Dataloader #####################################################

def streaming_load_data_files (dataset_names, dir_path):
    for file_name in dataset_names:
        filepath = os.path.join(dir_path, file_name)
        dataset = load_dataset("csv", data_files=filepath, split="train", streaming=True)
        for example in dataset:
            yield example


# def tokenize_something(example):
#     return tokenizer(example["log_line"], truncation=True, padding=True, clean_up_tokenization_spaces=False)

############################################################# Custom Dataset #####################################################

class CustomDataset(Dataset):
    def __init__(self, dataset_stream, tokenizer, label_mapping, max_token_length=512):
        self.data_stream = dataset_stream
        self.tokenizer = tokenizer
        self.label_mapping = label_mapping
        self.max_token_length = max_token_length

    def __iter__(self):
        # Iterate over the streaming dataset and debug
        for example in self.data_stream:
            try: 
                log_line = example["log_line"]
                main_category = example["main_category"]
            except KeyError as e:
                print(f"Missing field{e} in example: {example}")
                continue
            
            # Proceed with tokenization if both fields are present
            tokenized_input = self.tokenizer.encode_plus(
                log_line,
                add_special_tokens=True,
                truncation=True,
                padding="max_length",
                max_length=self.max_token_length,
                return_attention_mask=True,
                return_tensors="pt"
            )
            # Check if 'main_category' exists, otherwise set a default
            label = torch.tensor(self.label_mapping.get('main_category', 0), dtype=torch.long)  # Default to 0 if 'main_category' is missing

            yield {
                "input_ids": tokenized_input["input_ids"],
                "attention_mask": tokenized_input["attention_mask"],
                "labels": label.unsqueeze(0)
            }

############################################################# Custom Dataloader #####################################################
class CustomDataModule:
    def __init__(self, train_dataset_names, test_dataset_names, dir_path, batch_size=16, max_token_length=512, mapping_file="label_mapping.json"):                #TODO Rename dir_path to clearer name, Why this batch size & toen length?
        self.train_dataset_names = train_dataset_names
        self.test_dataset_names = test_dataset_names
        self.dir_path = dir_path
        self.batch_size = batch_size
        self.max_token_length = max_token_length
        self.tokenizer = RobertaTokenizer.from_pretrained('roberta-base')
        # self.label_mapping = 
        try:
            with open('label_mapping.json', "r") as f:
                if os.path.exists(mapping_file):
                    self.label_mapping = load_label_mapping(mapping_file)
                else:
                    self.label_mapping = build_label_mapping(self.train_dataset_names, self.dir_path, save_path="mapping_file")
        except Exception:
            print("'label-mapping' is empty. Fix it")

    def setup(self):
        # Load streaming data
        self.train_stream = streaming_load_data_files(self.train_dataset_names, self.dir_path)
        self.test_stream = streaming_load_data_files(self.test_dataset_names, self.dir_path)

        # Create datasets from streams
        self.train_dataset = CustomDataset(self.train_stream, self.tokenizer, max_token_length=self.max_token_length)
        self.test_dataset = CustomDataset(self.test_stream, self.tokenizer, max_token_length=self.max_token_length)

    def train_dataloader(self):
        return iter(self.train_dataset)
    
    # def val_dataloader(self):
    #     return self.test_dataset

    def test_dataloader(self):
        return iter(self.test_dataset)

############################################################# Classifier #####################################################

class RoBERTaClassifier(nn.Module):                                                  # TODO All of this class
    def __init__(self, n_labels):
        super(RoBERTaClassifier, self).__init__()
        # steup roberta model
        self.roberta = AutoModel.from_pretrained('roberta-base', return_dict=True)
        self.classifier = nn.Linear(self.roberta.config.hidden_size, n_labels)
        self.dropout = nn.Dropout(p=0.3)                    # TODO Why 0.3 --> Standard
        self.loss_function = nn.CrossEntropyLoss()

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state.mean(dim=1)           # macht mean hier sinn? wenns ja ne categorical nummer is? maybe median notwendig?! Muss da noch drüber nachdenken
        logits = self.classifier(self.dropout(pooled_output))
        loss = 0
        
        if labels is not None:
            loss = self.loss_function(logits, labels)

        return loss, logits
    
############################################################# Training loop #####################################################
def train_model(model, data_module, config):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    optimizer = optim.AdamW(model.parameters(), lr=config["learning_rate"],weight_decay=config["weight_decay"])
    scheduler = CosineAnnealingLR(optimizer, T_max=config["n_epochs"], eta_min=1e-6)                            # TODO Questions

    for epoch in range(config["n_epochs"]):
        model.train()
        train_loss = 0
        train_batch_counter = 0
        train_stream = data_module.train_dataloader()

        # iterate over datastream
        for example in train_stream:
            optimizer.zero_grad()
            """
            In PyTorch, for every mini-batch during the training phase, we typically want to explicitly set the gradients to zero before starting
            to do backpropagation (i.e., updating the Weights and biases) because PyTorch accumulates the gradients on subsequent backward passes.
            This accumulating behavior is convenient while training RNNs or when we want to compute the gradient of the loss summed over multiple mini-batches.
            So, the default action has been set to accumulate (i.e. sum) the gradients on every loss.backward() call.

            Because of this, when you start your training loop, ideally you should zero out the gradients so that you do the parameter update correctly. Otherwise,
            the gradient would be a combination of the old gradient, which you have already used to update your model parameters and the newly-computed gradient.
            It would therefore point in some other direction than the intended direction towards the minimum (or maximum, in case of maximization objectives).
            @ https://stackoverflow.com/questions/48001598/why-do-we-need-to-call-zero-grad-in-pytorch

            """
            batch = {k: v.to(device) for k, v, in example.items()}
            
            #Forward pass
            loss, logits = model(batch["input_ids"], batch["attention_mask"], batch["labels"])
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            train_batch_counter +=1


        # Validation loop
        model.eval()
        val_loss = 0
        val_batch_counter = 0
        val_stream = data_module.val_dataloader()
        with torch.no_grad():
            for example in val_stream:
                batch = {k: v.to(device) for k, v, in example.items()}
                loss, logits = model(batch["input_ids"], batch["attention_mask"], batch["labels"])
                val_loss += loss.item()
                val_batch_counter += 1

        train_loss = train_loss/train_batch_counter
        val_loss = val_loss/val_batch_counter

        print(f"Epoch {epoch+1}, Train Loss: {train_loss:.4f}, Validation Loss: {val_loss:.4f}")
        scheduler.step()
    return model


# Training config
config = {
    "learning_rate": 1e-5, 
    "weight_decay": 0.01,
    "n_epochs": 1,
    "batch_size": 16
}

# # Init data module and model
data_module = CustomDataModule(train_dataset_names,test_dataset_names, DIR, batch_size=config["batch_size"])
data_module.setup()
label_mapping =  build_label_mapping(train_dataset_names, DIR, save_path="label_mapping.json")
n_labels=len(data_module.label_mapping)

print(n_labels)
# model = RoBERTaClassifier(n_labels=config["n_labels"])

# # # Train model
# # trained_model = train_model(model, data_module, config)

# # # Predict on test set
# # predictions = predict_on_testdata(trained_model, data_module)
# # # print(f"Predictions on test set: {predictions}")

# # print("Training and Predictions completed")