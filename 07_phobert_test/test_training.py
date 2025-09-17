from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset
import torch

# model pretrained PhoBERT
model_name = "vinai/phobert-base-v2"

# tokenizer (PhoBERT dùng sentencepiece BPE)
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)

# model phân loại (classification head), num_labels = 3 (hay, dở, bình thường)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=3)


dataset = load_dataset("csv", data_files="review.csv")

def preprocess_function(examples):
    return tokenizer(examples["review"], padding="max_length", truncation=True, max_length=256)

encoded_dataset = dataset.map(preprocess_function, batched=True)



training_args = TrainingArguments(
    output_dir="./results",
    eval_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir='./logs',
    save_total_limit=2,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=encoded_dataset["train"],
    eval_dataset=encoded_dataset["train"].select(range(3)),  # ví dụ lấy 200 mẫu để eval
)

trainer.train()



text = "Phim này quá hay, nội dung cuốn hút!"
device = "cpu"

inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256).to(device)
model.to(device)

outputs = model(**inputs)

pred = torch.argmax(outputs.logits, dim=1).item()

if pred == 0:
    print("Phim dở")
elif pred == 1:
    print("Phim bình thường")
else:
    print("Phim hay")