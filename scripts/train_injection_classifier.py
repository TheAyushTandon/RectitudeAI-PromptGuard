import pandas as pd
import torch
from torch.utils.data import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import numpy as np
import os

# ✅ Custom PyTorch Dataset
class PromptInjectionDataset(Dataset):
    def __init__(self, dataframe, tokenizer, max_length=256):
        self.tokenizer = tokenizer
        self.texts = dataframe["text"].tolist()
        self.labels = dataframe["label"].tolist()
        self.max_length = max_length

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        encoded = self.tokenizer(
            self.texts[idx],
            padding="max_length",
            truncation=True,
            max_length=self.max_length,
            return_tensors="pt"
        )
        return {
            "input_ids": encoded["input_ids"].squeeze(),
            "attention_mask": encoded["attention_mask"].squeeze(),
            "labels": torch.tensor(self.labels[idx], dtype=torch.long)
        }

# ✅ Load data
train_df = pd.read_parquet("data/attacks/train.parquet")
test_df = pd.read_parquet("data/attacks/test.parquet")

# ✅ Model + Tokenizer
model_ckpt = "distilbert-base-uncased"
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
model = AutoModelForSequenceClassification.from_pretrained(model_ckpt, num_labels=2)

# ✅ Wrap data into PyTorch datasets
train_dataset = PromptInjectionDataset(train_df, tokenizer)
test_dataset = PromptInjectionDataset(test_df, tokenizer)

# ✅ Metrics function
def compute_metrics(pred):
    labels = pred.label_ids
    preds = np.argmax(pred.predictions, axis=1)
    acc = accuracy_score(labels, preds)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")
    return {"accuracy": acc, "precision": precision, "recall": recall, "f1": f1}

# ✅ Training arguments
args = TrainingArguments(
    output_dir="data/models/injection_classifier",
    evaluation_strategy="epoch",
    logging_strategy="epoch",
    save_strategy="epoch",
    num_train_epochs=3,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    load_best_model_at_end=True,
    logging_dir="logs"
)

# ✅ Trainer
trainer = Trainer(
    model=model,
    args=args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics
)

# ✅ Train + Save
trainer.train()
trainer.save_model("data/models/injection_classifier")
tokenizer.save_pretrained("data/models/injection_classifier")