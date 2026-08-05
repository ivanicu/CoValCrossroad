"""Mean-pooled hidden states from the local 0.8B base model as prompt embeddings.

WHY NOT TF-IDF. Measured first: TF-IDF (4 configs, k=14..30) gives silhouette 0.011-0.013,
i.e. no cluster structure at all. This script produces the alternative so the two can be
COMPARED on the same metric, rather than swapping instruments and asserting an improvement.
"""
import json, pathlib, sys
import numpy as np, torch
from transformers import AutoTokenizer, AutoModel

ROOT = pathlib.Path(__file__).resolve().parent.parent
MODEL = "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/Qwen3.5-0.8B-Base"

texts, pids = [], []
for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
    if not line.strip():
        continue
    q = json.loads(line)
    texts.append(" ".join(m["content"] for m in q["prompt"]["messages"] if m["role"] == "user"))
    pids.append(q["prompt_id"])
print(len(texts), "prompts")

tok = AutoTokenizer.from_pretrained(MODEL)
if tok.pad_token_id is None:
    tok.pad_token = tok.eos_token
model = AutoModel.from_pretrained(MODEL, dtype=torch.bfloat16).cuda().eval()

E = []
B = 16
with torch.no_grad():
    for i in range(0, len(texts), B):
        enc = tok(texts[i:i + B], return_tensors="pt", padding=True, truncation=True,
                  max_length=512).to("cuda")
        h = model(**enc).last_hidden_state.float()
        m = enc["attention_mask"].unsqueeze(-1).float()
        E.append(((h * m).sum(1) / m.sum(1)).cpu().numpy())
        if i % 320 == 0:
            print(i, flush=True)
E = np.concatenate(E)
E = E / np.linalg.norm(E, axis=1, keepdims=True)
np.savez_compressed(ROOT / "atlas" / "emb.npz", emb=E.astype(np.float32), pid=np.array(pids))
print("wrote emb.npz", E.shape)
