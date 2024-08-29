#################################################### ALL IN ONE VERSION ##################################################
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import pandas as pd
import numpy as np
import random
# import math
import warnings
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer, AutoModel #, AdamW, get_cosine_schedule_with_warmup
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from torch.optim.lr_scheduler import CosineAnnealingLR
# from torchmetrics.functional.classification import auroc
from transformers import logging as transformers_logging

# Suppress warnings
warnings.filterwarnings('ignore', category=FutureWarning)
transformers_logging.set_verbosity_error()
warnings.filterwarnings(
    'ignore',
    message="The dataloader, val_dataloader 0, does not have many workers which may be a bottleneck."
)

# Load all data
train_path = "train.csv"
val_path = "val.csv"
test_path = "val.csv"
train_data = pd.read_csv(train_path)
val_data = pd.read_csv(val_path)
val_data = pd.read_csv(test_path)

# Add an 'unhealthy' column for exploration
train_data['unhealthy'] = np.where(train_data['healthy'] == 1, 0, 1)
attributes = ['antagonize', 'condescending', 'dismissive', "generalisation", "generalisation_unfair", "hostile", "unhealthy"]


class UCC_Dataset(Dataset):
    """
    @param sample: Because it is a highly unbalanced dataset, using the sample size manually cuts of the majority class once the max is reached
    """
    def __init__(self, data_path, tokenizer, attributes, max_token_length: int = 64, sample = 5000):
        self.data_path = data_path
        self.tokenizer = tokenizer
        self.attributes = attributes
        self.max_token_length = max_token_length
        self.sample = sample
        self.__prepare_data()

    ## ( __ makes it a private funct)
    def __prepare_data(self):
        data = pd.read_csv(self.data_path)
        data['unhealthy'] = np.where(data['healthy'] == 1, 0, 1)

        if self.sample is not None:
            # if there is a positive attribute
            unhealthy = data.loc[data[attributes].sum(axis=1) > 0 ]
            healthy = data.loc[data[attributes].sum(axis=1) == 0 ]
            # random state for reproduction
            self.data = pd.concat([unhealthy, healthy.sample(self.sample, random_state=666)])

        else:
            self.data = data


    def __len__(self):
        return(len(self.data))


    def __getitem__(self, index):
        """
        Turn things into a tensor from string inputs
        @param add_special_tokens: ensure formatting by adding beggining & end of sentence tokens
        @param truncation: comments to max_length
        @param padding: pad tokens < 512 to may_length
        @param returns_attention_mask: 1s everywhere except for paddings (0)
        """
        item = self.data.iloc[index]
        comment = str(item.comment)
        attributes = torch.FloatTensor(item[self.attributes])
        tokens = self.tokenizer.encode_plus (comment,
                                                add_special_tokens = True,
                                                return_tensors="pt", 
                                                truncation =True,
                                                max_length = self.max_token_length,
                                                padding = "max_length",
                                                return_attention_mask=True)
        
        return {'input_ids': tokens.input_ids.flatten(),
                'attention_mask': tokens.attention_mask.flatten(),
                'labels': attributes }


class UCC_DataModule:
    def __init__(self, train_path, val_path, attributes, batch_size: int = 16, max_token_len: int = 64, model_name="roberta-base"):
        self.train_path = train_path
        self.val_path = val_path
        self.attributes = attributes
        self.batch_size = batch_size
        self.max_token_len = max_token_len
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

        self.train_dataset = None
        self.val_dataset = None

    def setup(self):
        self.train_dataset = UCC_Dataset(self.train_path, self.tokenizer, self.attributes, max_token_length=self.max_token_len)
        self.val_dataset = UCC_Dataset(self.val_path, self.tokenizer, self.attributes, max_token_length=self.max_token_len, sample=None)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size=self.batch_size, num_workers=0, shuffle=True)

    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size, num_workers=0, shuffle=False)
    
    def test_dataloader(self):
        return DataLoader(self.val_dataset, batch_size=self.batch_size, num_workers=0, shuffle=False)


class UCC_Classifier(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.pretrained_model = AutoModel.from_pretrained(config["model_name"], return_dict=True)
        
        # Appending a classification layer (="head") and a hidden layer before final_layer
        self.hidden = nn.Linear(self.pretrained_model.config.hidden_size, self.pretrained_model.config.hidden_size)
        self.classifier = nn.Linear(self.pretrained_model.config.hidden_size, self.config["n_labels"])
        
        # Initializing custom layers, optional, would also be done automatically, but better performance if stated explicitly)
        torch.nn.init.xavier_uniform_(self.hidden.weight)
        torch.nn.init.xavier_uniform_(self.classifier.weight)

         # Loss function
        self.loss_func = nn.BCEWithLogitsLoss(reduction="mean")
        
        # dropout layer; randomly activate/deactivate random nodes for each training loop; ensures model is not dependant on specific node
        self.dropout = nn.Dropout()

    # Forward pass, labels only needed while training, not for prediction, so set to none by default
    def forward(self, input_ids, attention_mask, labels=None):
        model_output = self.pretrained_model(
            input_ids=input_ids,
            attention_mask=attention_mask)
        last_hidden_state = model_output.last_hidden_state
        pooled_output = torch.mean(last_hidden_state, 1)

        # NN-layers
        pooled_output = self.hidden(pooled_output)  # pass sentence(or however tokens are pooled) through hidden layer
        pooled_output = self.dropout(pooled_output) # pass through dropout layer
        pooled_output = F.relu(pooled_output)   # pass through activatioin function( relu; in this case)
        logits = self.classifier(pooled_output)     # pass through classification layer

        loss = 0
        if labels is not None:
            loss = self.loss_func(logits.view(-1, self.config["n_labels"]), labels.view(-1, self.config["n_labels"]))
        # logits = fancy name for model output
        return loss, logits


def train(model, ucc_data_module, config):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # Set up optimizer and scheduler
    optimizer = optim.AdamW(model.parameters(), lr=config["lr"], weight_decay=config["w_decay"])
    scheduler = CosineAnnealingLR(optimizer, T_max=config["n_epochs"], eta_min=1e-6)

    # Training
    for epoch in range(config["n_epochs"]):
        model.train()
        train_loss = 0.0
        for batch in ucc_data_module.train_dataloader():
            batch = {k: v.to(device) for k, v in batch.items()}
            optimizer.zero_grad()
            loss, _ = model(**batch)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch in ucc_data_module.val_dataloader():
                batch = {k: v.to(device) for k, v in batch.items()}
                loss, _ = model(**batch)
                val_loss += loss.item()

        print(f"Epoch [{epoch+1}/{config['n_epochs']}], Train Loss: {train_loss/len(ucc_data_module.train_dataloader()):.4f}, Val Loss: {val_loss/len(ucc_data_module.val_dataloader()):.4f}")
        scheduler.step()

    return model


def predict_full_dataset(model, ucc_data_module):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    all_predicted_labels = []
    all_true_labels = []

    with torch.no_grad():
        for batch in ucc_data_module.val_dataloader():
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            _, logits = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            
            probabilities = torch.softmax(logits, dim=1)
            predicted_labels = torch.argmax(probabilities, dim=1)

            all_predicted_labels.append(predicted_labels.cpu())
            all_true_labels.append(torch.argmax(labels, dim=1).cpu())

    all_predicted_labels = torch.cat(all_predicted_labels, dim=0)
    all_true_labels = torch.cat(all_true_labels, dim=0)

    return all_predicted_labels, all_true_labels


def evaluate_predictions(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average='macro')
    precision = precision_score(y_true, y_pred, average='macro')
    recall = recall_score(y_true, y_pred, average='macro')

    print(f"Accuracy: {accuracy:.4f}")
    print(f"F1 Score: {f1:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall: {recall:.4f}")


def predict_single(model, ucc_data_module):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    # Get a random index from the test dataset
    random_index = random.randint(0, len(ucc_data_module.val_dataset) - 1)

    # Retrieve a sample directly from the dataset
    sample = ucc_data_module.val_dataset[random_index]
    
    # Prepare the sample for input
    input_ids = sample['input_ids'].unsqueeze(0).to(device)
    attention_mask = sample['attention_mask'].unsqueeze(0).to(device)
    labels = sample['labels'].unsqueeze(0).to(device) if 'labels' in sample else None

    # Make a prediction for the single sample
    with torch.no_grad():
        _, logits = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        probabilities = torch.sigmoid(logits).squeeze()

    # Return the raw probabilities or binary labels (as tensor)
    predicted_labels = (probabilities > 0.5).int()

    return probabilities, predicted_labels


config = {
    'model_name': "distilroberta-base",
    "n_labels": len(attributes), 
    "bs": 64,
    "lr": 1.5e-6,
    "warmup": 0.2,
    "train_size": len(train_data), 
    "w_decay": 0.001,
    "n_epochs": 1
    }

ucc_data_module = UCC_DataModule(train_path, val_path, attributes, batch_size=config["bs"])
ucc_data_module.setup()

model = UCC_Classifier(config)
trained_model = train(model, ucc_data_module, config)

# Predict for full test set
all_predicted_labels, all_true_labels = predict_full_dataset(trained_model, ucc_data_module)

# Print the first 5 predictions and corresponding actual labels
print(f"Predicted labels (first 5): \n{all_predicted_labels[:5]}")
print(f"Actual labels (first 5): \n{all_true_labels[:5]}")

# Convert tensors to numpy arrays for metric calculations
y_true = all_true_labels.numpy()
y_pred = np.array(all_predicted_labels)

# Evaluate predictions
evaluate_predictions(y_true, y_pred)

# Single prediction
probabilities, predicted_labels = predict_single(trained_model, ucc_data_module)
print(f"Predicted probabilities: {probabilities}")
print(f"Predicted labels: {predicted_labels}")