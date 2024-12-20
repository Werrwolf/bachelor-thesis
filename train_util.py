import random
import os
import torch
import json

import numpy as np
import torch.optim as optim
import torch.nn as nn

from os import listdir
from datasets import load_dataset
from transformers import RobertaTokenizer
from torch.utils.data import Dataset
from transformers import AutoModel
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from torch.optim.lr_scheduler import CosineAnnealingLR
import logging
from itertools import tee

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

############################################################# Label Mapping #####################################################
def load_label_mapping(file_path="label_mapping.json"):
    with open(file_path, "r") as file:
        label_mapping = json.load(file)
    return label_mapping

############################################################# Dataloader #####################################################
def streaming_load_data_files(dataset_names, dir_path):
    for file_name in dataset_names:
        filepath = os.path.join(dir_path, file_name)
        dataset = load_dataset("csv", data_files=filepath, split="train", streaming=True)
        for example in dataset:
            yield example

############################################################# Custom Dataset #####################################################
class CustomDataset(Dataset):
    def __init__(self, dataset_stream, tokenizer, label_mapping, max_token_length=512):
        self.data_stream = dataset_stream
        self.tokenizer = tokenizer
        self.label_mapping = label_mapping
        self.max_token_length = max_token_length

    def __iter__(self):
        for example in self.data_stream:
            try:
                tokenized_example = self.tokenizer(
                    example["log_line"],
                    padding="max_length",
                    truncation=True,
                    max_length=self.max_token_length,
                    return_tensors="pt",
                    clean_up_tokenization_spaces=False
                )
                labels = torch.tensor(self.label_mapping[example["main_category"].lower()]).unsqueeze(0)  # Add batch dimension
                
                # Check tensor dimensions
                logger.debug(f"Input IDs: {tokenized_example['input_ids'].shape}")
                logger.debug(f"Attention Mask: {tokenized_example['attention_mask'].shape}")
                logger.debug(f"Labels: {labels.shape}")

                tokenized_example["labels"] = labels
                yield tokenized_example
            except KeyError as e:
                logger.error(f"Missing field {e} in example: {example}")
                continue

    def __len__(self):
        return sum(1 for _ in self.data_stream)

############################################################# Custom Dataloader #####################################################
class CustomDataModule:
    def __init__(self, train_dataset_names, val_dataset_names, test_dataset_names, dir_path, batch_size=16, max_token_length=512, label_mapping="label_mapping.json"):
        self.label_mapping = label_mapping
        self.train_dataset_names = train_dataset_names
        self.val_dataset_names = val_dataset_names
        self.test_dataset_names = test_dataset_names
        self.dir_path = dir_path
        self.batch_size = batch_size
        self.max_token_length = max_token_length
        self.tokenizer = RobertaTokenizer.from_pretrained('roberta-base')

    def setup(self):
        # Train data
        self.train_stream = streaming_load_data_files(self.train_dataset_names, self.dir_path)

        # Validation data
        self.val_stream = streaming_load_data_files(self.val_dataset_names, self.dir_path)

        # Test data
        self.test_stream = streaming_load_data_files(self.test_dataset_names, self.dir_path)

        logger.info("Datasets are set up for streaming.")

        # Create datasets
        self.train_dataset = CustomDataset(self.train_stream, self.tokenizer, self.label_mapping, max_token_length=self.max_token_length)
        self.val_dataset = CustomDataset(self.val_stream, self.tokenizer, self.label_mapping, max_token_length=self.max_token_length)
        self.test_dataset = CustomDataset(self.test_stream, self.tokenizer, self.label_mapping, max_token_length=self.max_token_length)


    def train_dataloader(self):
        # Reinitialize train dataset for every epoch
        self.train_stream = streaming_load_data_files(self.train_dataset_names, self.dir_path)
        self.train_dataset = CustomDataset(self.train_stream, self.tokenizer, self.label_mapping, max_token_length=self.max_token_length)
        return iter(self.train_dataset)

    def val_dataloader(self):
        # Reinitialize validation dataset for every epoch
        self.val_stream = streaming_load_data_files(self.val_dataset_names, self.dir_path)
        self.val_dataset = CustomDataset(self.val_stream, self.tokenizer, self.label_mapping, max_token_length=self.max_token_length)
        return iter(self.val_dataset)

    def test_dataloader(self):
        # Test dataset loader
        self.test_stream = streaming_load_data_files(self.test_dataset_names, self.dir_path)
        self.test_dataset = CustomDataset(self.test_stream, self.tokenizer, self.label_mapping, max_token_length=self.max_token_length)
        return iter(self.test_dataset)
    
############################################################# Classifier #####################################################
class RoBERTaClassifier(nn.Module):
    def __init__(self, n_labels):
        super(RoBERTaClassifier, self).__init__()
        self.roberta = AutoModel.from_pretrained('roberta-base', return_dict=True)
        self.classifier = nn.Linear(self.roberta.config.hidden_size, n_labels)
        self.dropout = nn.Dropout(p=0.3)
        self.loss_function = nn.CrossEntropyLoss()

    def forward(self, input_ids, attention_mask, labels=None):
        outputs = self.roberta(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.last_hidden_state.mean(dim=1)
        logits = self.classifier(self.dropout(pooled_output))
        loss = 0
        if labels is not None:
            loss = self.loss_function(logits, labels)
        return loss, logits

    def save_pretrained(self, save_directory):
        model_save_path = os.path.join(save_directory, "pytorch_model.bin")
        torch.save(self.state_dict(), model_save_path)
        self.roberta.config.save_pretrained(save_directory)

    @classmethod
    def from_pretrained(cls, save_directory, n_labels):
        model = cls(n_labels)
        model_path = os.path.join(save_directory, "pytorch_model.bin")
        model.load_state_dict(torch.load(model_path, map_location=torch.device("cuda" if torch.cuda.is_available() else "cpu")))
        return model

############################################################# Training loop #####################################################
def train_model(model, data_module, config):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    optimizer = optim.AdamW(model.parameters(), lr=config["learning_rate"], weight_decay=config["weight_decay"])
    scheduler = CosineAnnealingLR(optimizer, T_max=config["n_epochs"], eta_min=1e-6)

    for epoch in range(config["n_epochs"]):
        logger.info(f"Starting epoch {epoch + 1}...")
        model.train()
        train_loss = 0
        train_stream = data_module.train_dataloader()
        train_batch_counter = 0

        for example in train_stream:
            logger.debug(f"Type of example: {type(example)}")
            if example is None:
                logger.error("Dataset yielded None instead of a batch. Skipping.")
                continue

            optimizer.zero_grad()
            batch = {k: v.to(device) for k, v in example.items()}

            # Debugging: Check batch shapes
            logger.debug(f"Batch Input IDs shape: {batch['input_ids'].shape}")
            logger.debug(f"Batch Labels shape: {batch['labels'].shape}")

            if batch["labels"].size(0) == 0:
                logger.error("Empty labels found in batch. Skipping.")
                continue

            loss, logits = model(batch["input_ids"], batch["attention_mask"], batch["labels"])
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
            train_batch_counter += 1

        if train_batch_counter == 0:
            logger.error("No batches were processed during training.")
            return model

        model.eval()
        val_loss = 0
        val_batch_counter = 0
        val_stream = data_module.val_dataloader()
        with torch.no_grad():
            for example in val_stream:
                batch = {k: v.to(device) for k, v in example.items()}
                loss, logits = model(batch["input_ids"], batch["attention_mask"], batch["labels"])
                val_loss += loss.item()
                val_batch_counter += 1

        train_loss /= train_batch_counter
        val_loss /= val_batch_counter

        logger.info(f"Epoch {epoch + 1}, Train Loss: {train_loss:.4f}, Validation Loss: {val_loss:.4f}")
        scheduler.step()

    return model

###########################################################################################################
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support

def evaluate_model(model, dataloader, device, label_mapping):
    model.eval()
    all_preds = []
    all_labels = []
    
    # Reverse label mapping to map indices back to label names
    idx_to_label = {v: k for k, v in label_mapping.items()}
    
    with torch.no_grad():
        for example in dataloader:
            batch = {k: v.to(device) for k, v in example.items()}
            _, logits = model(batch["input_ids"], batch["attention_mask"])
            
            # Get predicted class indices and true labels
            preds = torch.argmax(logits, dim=1).cpu().numpy()
            labels = batch["labels"].cpu().numpy()
            
            all_preds.extend(preds)
            all_labels.extend(labels)
    
    # Find unique classes in predictions and labels
    unique_classes = sorted(set(all_labels) | set(all_preds))
    unique_class_names = [idx_to_label[i] for i in unique_classes]
    
    # Calculate metrics
    accuracy = accuracy_score(all_labels, all_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_preds, labels=unique_classes, average=None)
    macro_avg = precision_recall_fscore_support(all_labels, all_preds, labels=unique_classes, average='macro')
    weighted_avg = precision_recall_fscore_support(all_labels, all_preds, labels=unique_classes, average='weighted')

    # Classification report (text format)
    class_report = classification_report(all_labels, all_preds, target_names=unique_class_names, labels=unique_classes, zero_division=0)

    # Consolidate metrics into a dictionary
    metrics_report = {
        "accuracy": accuracy,
        "precision_per_class": precision,
        "recall_per_class": recall,
        "f1_per_class": f1,
        "macro_avg": macro_avg,
        "weighted_avg": weighted_avg,
        "class_report": class_report
    }
    
    return metrics_report


# Training config
config = {
    "learning_rate": 1e-5, 
    "weight_decay": 0.01,
    "n_epochs": 3,
    "batch_size": 16
}

if __name__ == "__main__":
    print("'train.util' cannot be run directly. Try running 'train.py' instead")
