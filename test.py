import os
import torch
import warnings
from train_util import load_label_mapping, CustomDataModule, RoBERTaClassifier, logger
import json

from os import listdir
from transformers import RobertaTokenizer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from transformers import logging as transformers_logging

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
transformers_logging.set_verbosity_error()
warnings.filterwarnings(
    'ignore',
    message="The dataloader, val_dataloader 0, does not have many workers which may be a bottleneck."
)


def test_model(saved_model_dir, data_module, label_mapping):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load the model
    model = RoBERTaClassifier.from_pretrained(saved_model_dir, n_labels=len(label_mapping))
    model.to(device)
    model.eval()

    predictions = []
    ground_truths = []
    dataloader = data_module.test_dataloader()

    with torch.no_grad():
        for example in dataloader:
            batch = {k: v.to(device) for k, v in example.items()}
            logits = model(batch["input_ids"], batch["attention_mask"])[1]
            pred_labels = torch.argmax(logits, dim=1).cpu().numpy()
            true_labels = batch["labels"].cpu().numpy()

            predictions.extend(pred_labels)
            ground_truths.extend(true_labels)

    # Calculate metrics
    accuracy = accuracy_score(ground_truths, predictions)
    f1 = f1_score(ground_truths, predictions, average="weighted")
    precision = precision_score(ground_truths, predictions, average="weighted")
    recall = recall_score(ground_truths, predictions, average="weighted")

    logger.info(f"Test Accuracy: {accuracy:.4f}")
    logger.info(f"Test F1 Score: {f1:.4f}")
    logger.info(f"Test Precision: {precision:.4f}")
    logger.info(f"Test Recall: {recall:.4f}")

    # Save predictions to a file
    with open("predictions.json", "w") as f:
        json.dump({"predictions": predictions, "ground_truths": ground_truths}, f, indent=4)

if __name__ == "__main__":
    # Load label mapping
    label_mapping = load_label_mapping("label_mapping.json")
    
    DIR = "single_dataset"
    list_of_datasets = listdir(DIR)

    # Initialize data module for testing
    data_module = CustomDataModule(
        train_dataset_names=[],  # No training needed
        test_dataset_names= list_of_datasets,  # Test dataset with same structure as train
        dir_path=DIR,
        label_mapping=label_mapping
    )
    data_module.setup()

    # Directory where the model was saved
    saved_model_dir = "model" 

    # Test the model
    test_model(saved_model_dir=saved_model_dir, data_module=data_module, label_mapping=label_mapping)