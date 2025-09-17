import torch
from transformers import AutoTokenizer, AutoModel
import torch.nn.functional as F

# Load PhoBERT
tokenizer = AutoTokenizer.from_pretrained("vinai/phobert-base-v2")
model = AutoModel.from_pretrained("vinai/phobert-base-v2")

# Hàm sinh embedding cho câu
def get_sentence_embedding(text):
    # Tokenize
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)

    # Lấy hidden states từ model
    with torch.no_grad():
        outputs = model(**inputs)
        # outputs[0] = last hidden state (batch_size, seq_len, hidden_dim)
        last_hidden_state = outputs.last_hidden_state  

    # Lấy mean pooling (trung bình vector các token)
    embedding = last_hidden_state.mean(dim=1)  # shape: (batch_size, hidden_dim)
    return embedding

# 2 câu ví dụ
text1 = "Bộ phim này rất hay và cảm động."
text2 = "Mình thấy phim này thật sự tuyệt vời."

# Lấy embedding
emb1 = get_sentence_embedding(text1)
emb2 = get_sentence_embedding(text2)

# Tính cosine similarity
similarity = F.cosine_similarity(emb1, emb2)
print("Độ tương đồng:", similarity.item())
