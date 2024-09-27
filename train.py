import numpy as np
import random
import os
import warnings
import train_util
import json

from os import listdir
from transformers import RobertaTokenizer
from transformers import logging as transformers_logging

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
transformers_logging.set_verbosity_error()
warnings.filterwarnings(
    'ignore',
    message="The dataloader, val_dataloader 0, does not have many workers which may be a bottleneck."
)

# LIST_OF_DATASETS = listdir("/home/q524745/bachelor_thesis/datasets")
# DIR = "datasets"
# TRAIN_PERCENTAGE = 0.8
# TEST_PERCENTAGE = 0.2
# OUTPUT_DIR = "model"
# random.shuffle(LIST_OF_DATASETS)
# SPLIT_CUTOFF = int(len(LIST_OF_DATASETS) * TRAIN_PERCENTAGE)

# train_dataset_names  = LIST_OF_DATASETS[:SPLIT_CUTOFF]
# test_dataset_names = LIST_OF_DATASETS[SPLIT_CUTOFF:]

# tokenizer = RobertaTokenizer.from_pretrained("roberta-base")

config = {
    "learning_rate": 1e-5, 
    "weight_decay": 0.01,
    "n_epochs": 1,
    "batch_size": 16            # depends on memory
}

with open ('label_mapping.json') as f:
    label_mapping=json.load(f)

print(label_mapping)

# if __name__ == "__main__":
#     # # Init data module and model
#     # data_module = train_util.CustomDataModule(train_dataset_names,test_dataset_names, DIR, batch_size=config["batch_size"])
#     # data_module.setup()

#     with open ('label_mapping.json') as f:
#         label_mapping=json.load(f)
#     n_labels=len(label_mapping)

#     print(n_labels)
#     model = train_util.RoBERTaClassifier(n_labels=n_labels)

#     # Train model
#     trained_model = train_util.train_model(model, config)
    
#     # Create output directory if needed
#     if not os.path.exists(OUTPUT_DIR):
#         os.makedirs(OUTPUT_DIR)
    
#     model_to_save = trained_model.module if hasattr(model, 'module') else trained_model  # Take care of distributed/parallel training
#     model_to_save.save_pretrained(OUTPUT_DIR)
#     tokenizer.save_pretrained(OUTPUT_DIR)
#     print("Saved model to %s" % OUTPUT_DIR)
    
    # # TODO Predict on test set
    # predictions = predict_on_testdata(trained_model, data_module)
    # # print(f"Predictions on test set: {predictions}")
    # print("Training and Predictions completed")