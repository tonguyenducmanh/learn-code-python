import random
from datasets import load_dataset
from sentence_transformers import SentenceTransformer, models, losses, InputExample, util
from torch.utils.data import DataLoader

# 1. Load dataset thơ
ds = load_dataset("phamson02/vietnamese-poetry-corpus")
ds_train = ds["train"].select(range(200))
# Giả sử ds["train"] có trường "text" (thơ / câu)
# Nếu dataset là bản thơ đầy đủ, có thể split thành câu
def split_into_sentences(poem_text):
    # Chuyển </n> thành xuống dòng
    poem_text = poem_text.replace("</n>", ".").replace("<\n>", ".")
    # Chia thành từng câu/thơ
    sents = [s.strip() for s in poem_text.split(".") if s.strip()]
    return sents

# 2. Tạo samples positive & negative
train_samples = []
neg_ratio = 1  # số negative trên mỗi positive

for item in ds_train:
    poem = item["content"]
    sents = split_into_sentences(poem)
    if len(sents) < 2:
        continue
    # tạo positive pairs từ cùng thơ
    # ví dụ lấy 2 câu bất kỳ trong cùng một bài thơ
    for _ in range(2):  # số cặp positive mỗi thơ
        a, b = random.sample(sents, 2)
        train_samples.append(InputExample(texts=[a, b], label=1.0))
    # tạo negative pairs: câu từ thơ khác
    for _ in range(neg_ratio):
        # lấy một thơ khác ngẫu nhiên
        other = ds_train[ random.randint(0, len(ds_train)-1) ]["content"]
        sents_other = split_into_sentences(other)
        if not sents_other:
            continue
        b2 = random.choice(sents_other)
        a2 = random.choice(sents)
        train_samples.append(InputExample(texts=[a2, b2], label=0.0))

# 3. Xây model SBERT từ PhoBERT
phobert = models.Transformer("vinai/phobert-base-v2")
pooling = models.Pooling(
    phobert.get_word_embedding_dimension(),
    pooling_mode_mean_tokens=True,
    pooling_mode_cls_token=False,
    pooling_mode_max_tokens=False
)
model = SentenceTransformer(modules=[phobert, pooling])

# 4. DataLoader & Loss
train_dataloader = DataLoader(train_samples, shuffle=True, batch_size=16)
# Dùng Loss contrastive hoặc CosineSimilarityLoss
loss_fct = losses.CosineSimilarityLoss(model)

# 5. Fine-tune
model.fit(
    train_objectives=[(train_dataloader, loss_fct)],
    epochs=3,
    warmup_steps=1000,
    output_path="phobert-poetry-sbert"
)

# 6. Kiểm thử
model = SentenceTransformer("phobert-poetry-sbert")
c1 = "Trăng tỏ trời quanh ánh ngọc mờ"
c2 = "Đêm sâu trăng sáng chiếu bao la"
emb1 = model.encode(c1, convert_to_tensor=True)
emb2 = model.encode(c2, convert_to_tensor=True)
sim = util.pytorch_cos_sim(emb1, emb2)
print("Sim:", sim.item())
