import sys
sys.path.append('C:\\Users\\q524745\\Documents\\bachelor_thesis\\.venv\\lib\\site-packages')

import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import math
import torch.nn.functional as F
import pytorch_lightning as pl
import multiprocessing

from transformers import AutoTokenizer, AutoModel, AdamW, get_cosine_schedule_with_warmup
from torch.utils.data import Dataset
from torch.utils.data import DataLoader

train_data = pd.read_csv("train.csv")
train_path = "train.csv"

val_data = pd.read_csv("val.csv") 
val_path = "val.csv"

train_data['unhealthy'] = np.where(train_data['healthy'] == 1, 0, 1)
attributes = ['antagonize', 'condescending', 'dismissive', "generalisation", "generalisation_unfair", "hostile", "unhealthy"]


class UCC_Dataset(Dataset):
    """
    @param sample: Because it is a highly unbalanced dataset, using the sample size manually cuts of the majority class once the max is reached
    """
    def __init__(self, data_path, tokenizer, attributes, max_token_length: int = 512, sample = 5000):
        self.data_path = data_path
        self.tokenizer = tokenizer
        self.attributes = attributes
        self.max_token_length = max_token_length
        self.sample = sample
        self.__prepare_data()


    def __prepare_data(self):
        data = pd.read_csv(self.data_path)
        data['unhealthy'] = np.where(data['healthy'] == 1, 0, 1)

        if self.sample is not None:
            unhealthy = data.loc[data[attributes].sum(axis=1) > 0 ]
            healthy = data.loc[data[attributes].sum(axis=1) == 0 ]
            self.data = pd.concat([unhealthy, healthy.sample(self.sample, random_state=666)])

        else:
            self.data = data


    def __len__(self):
        return(len(self.data))


    def __getitem__(self, index):
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
        
        return {'input_ids': tokens.input_ids.flatten(), 'attention_mask': tokens.attention_mask.flatten(), 'labels': attributes }
    
model_name = "roberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
ucc_ds = UCC_Dataset(train_path, tokenizer, attributes)

ucc_ds_val = UCC_Dataset(val_path, tokenizer, attributes, sample =None)


class UCC_Data_Module(pl.LightningDataModule):

    def __init__(self, train_path, val_path, attributes, batch_size: int = 16, max_token_len: int =512, model_name = "roberta-base"):
        super().__init__()
        self.train_path = train_path
        self.val_path = val_path
        self.attributes = attributes
        self.batch_size = batch_size
        self.max_token_len = max_token_len
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def setup(self, stage = None):
        if stage in (None, "fit"):
            self.train_dataset = UCC_Dataset(self.train_path, self.tokenizer, self.attributes)
            self.val_dataset = UCC_Dataset(self.val_path, self.tokenizer, self.attributes, sample = None)
        
        if stage == "predict":
            self.val_dataset = UCC_Dataset(self.val_path, self.tokenizer, self.attributes, sample = None)

    def train_dataloader(self):
        return DataLoader(self.train_dataset, batch_size = self.batch_size, num_workers=0, shuffle=True)
    
    def val_dataloader(self):
        return DataLoader(self.val_dataset, batch_size = self.batch_size, num_workers=0, shuffle=False)
    
    def predict_dataloader(self):
        return DataLoader(self.val_dataset, batch_size = self.batch_size, num_workers=0, shuffle=False)
    

ucc_data_module = UCC_Data_Module(train_path, val_path, attributes)
ucc_data_module.setup()

class UCC_Classifier(pl.LightningModule):
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.pretrained_model = AutoModel.from_pretrained(config["model_name"], return_dict = True)
        
        self.hidden = nn.Linear(self.pretrained_model.config.hidden_size, self.pretrained_model.config.hidden_size )
        self.classifier = nn.Linear(self.pretrained_model.config.hidden_size, self.config["n_labels"])
        
        torch.nn.init.xavier_uniform_(self.hidden.weight)
        torch.nn.init.xavier_uniform_(self.classifier.weight)

        self.loss_func = nn.BCEWithLogitsLoss(reduction="mean")
        self.dropout = nn.Dropout()

    def forward(self, input_ids, attention_mask, labels = None):
        output = self.pretrained_model(input_ids = input_ids, attention_mask = attention_mask)
        pooled_output = torch.mean(output.last_hidden_state, 1)

        pooled_output = self.hidden(pooled_output)
        pooled_output = self.dropout(pooled_output)
        pooled_output = F.relu(pooled_output)
        logits = self.classifier(pooled_output)
        loss = 0

        if labels is not None:
            loss = self.loss_func(logits.view(-1, self.config["n_labels"]), labels.view(-1, self.config["n_labels"]))
        
        return loss, logits
    
    def training_step(self, batch, batch_index):
        loss, logits = self(**batch)
        self.log("train_loss", loss, prog_bar=True, logger= True)
        return {"loss": loss, "predictions": logits, "labels": batch["labels"]}
    

    def validation_step(self, batch, batch_index):
        loss, logits = self(**batch)
        self.log("validation_loss", loss, prog_bar=True, logger= True)
        return {"val_loss": loss, "predictions": logits, "labels": batch["labels"]}
    

    def prediction_step(self, batch, batch_index):
        __, logits = self(**batch)
        return logits


    def configure_optimizers(self):
        optimizer = AdamW(self.parameters(), lr=self.config["lr"], weight_decay=self.config["w_decay"])
        total_steps = self.config["train_size"] / self.config["bs"]
        warmup_steps = math.floor(total_steps * self.config["warmup"])

        scheduler = get_cosine_schedule_with_warmup(optimizer, warmup_steps, total_steps)
        return [optimizer], [scheduler]
    

# Debugging: Check if tensors require gradients
def check_requires_grad(model):
    for name, param in model.named_parameters():
        if not param.requires_grad:
            print(f"Parameter {name} does not require gradients!")


config = {
    'model_name': "distilroberta-base",
    "n_labels": len(attributes), 
    "bs": 512, 
    "lr": 1.5e-6,
    "warmup": 0.2,
    "train_size": len(ucc_data_module.train_dataloader()), 
    "w_decay": 0.001,
    "n_epochs": 1
    }   

if __name__ == '__main__':

    multiprocessing.set_start_method('spawn', force=True)

    ucc_data_module = UCC_Data_Module(train_path, val_path, attributes, batch_size=config["bs"])
    ucc_data_module.setup()

    model = UCC_Classifier(config)

    check_requires_grad(model)

    trainer = pl.Trainer(max_epochs=config["n_epochs"], num_sanity_val_steps=50 )
    trainer.fit(model, ucc_data_module)
