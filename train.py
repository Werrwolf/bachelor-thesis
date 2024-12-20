import numpy as np
import random
import os
import warnings
import train_util
import json
import torch

from os import listdir
from transformers import RobertaTokenizer
from transformers import logging as transformers_logging

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning)
transformers_logging.set_verbosity_error()
warnings.filterwarnings(
    'ignore',
    message="The dataloader, val_dataloader 0, does not have many workers which may be a bottleneck."
)

DIR = "datasets"
TRAIN_PERCENTAGE = 0.8
TEST_PERCENTAGE = 0.2
OUTPUT_DIR = "model"

list_of_datasets = listdir(DIR)
random.shuffle(list_of_datasets)
SPLIT_CUTOFF = int(len(list_of_datasets) * TRAIN_PERCENTAGE)

train_dataset_names  = list_of_datasets[:SPLIT_CUTOFF]
test_dataset_names = list_of_datasets[SPLIT_CUTOFF:]

tokenizer = RobertaTokenizer.from_pretrained("roberta-base")

config = {
    "learning_rate": 1e-5, 
    "weight_decay": 0.01,
    "n_epochs": 5               ,
    "batch_size": 16            # depends on memory
}

label_mapping = train_util.load_label_mapping('label_mapping.json')

if __name__ == "__main__":
    # Init data module and model
    data_module = train_util.CustomDataModule(train_dataset_names, test_dataset_names, DIR, batch_size=config["batch_size"], label_mapping=label_mapping)
    data_module.setup()
    n_labels = len(label_mapping)
                                                                                                                                                               
    print(f"Unique labels in dataset: {n_labels}")
    model = train_util.RoBERTaClassifier(n_labels=n_labels)

    # Train model
    trained_model = train_util.train_model(model=model, data_module=data_module, config=config)
    
    # Create output directory if needed
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    model_to_save = trained_model.module if hasattr(trained_model, 'module') else trained_model  # Take care of distributed/parallel training
    model_to_save.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Saved model to %s" % OUTPUT_DIR)
    
    print("Training and Validation (Predictions not implemented yet) completed")

    # Evaluate the model on the validation set
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    val_dataloader = data_module.val_dataloader()
    metrics = train_util.evaluate_model(trained_model, val_dataloader, device, label_mapping)
    
    print("Evaluation Metrics:")
    print(metrics["class_report"])  # Print the classification report
    print(f"Macro-Average Precision: {metrics['macro_avg'][0]:.4f}")
    print(f"Macro-Average Recall: {metrics['macro_avg'][1]:.4f}")
    print(f"Macro-Average F1 Score: {metrics['macro_avg'][2]:.4f}")
    print(f"Weighted F1 Score: {metrics['weighted_avg'][2]:.4f}")
    