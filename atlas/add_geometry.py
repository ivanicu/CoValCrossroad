"""Give every prompt AND every round a position, so the corpus can be seen as a cloud.

Projection is t-SNE on PCA-50 of the 0.8B mean-pooled embeddings. Silhouette of the
k-means partition IS REPORTED on the page: at its best (k=8) it is 0.0485, four times
TF-IDF's but still low -- the cloud is shown so the reader can judge the structure, not
told that structure exists.
"""
import json, pathlib, collections, subprocess, sys
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "atlas"
K = 12

z = np.load(OUT / "emb.npz", allow_pickle=True)
E, pids = z["emb"], [str(x) for x in z["pid"]]
XY = np.load(OUT / "_xy.npy")
corpus = json.loads((OUT / "corpus.json").read_text())
rows = {r["pid"]: r for r in corpus["rows"]}

km = KMeans(n_clusters=K, n_init=10, random_state=0).fit(E)
lab = km.labels_
sil = float(silhouette_score(E, lab))
sil_by_k = {}
for k in (8, 12, 18, 24):
    sil_by_k[k] = float(silhouette_score(E, KMeans(n_clusters=k, n_init=8, random_state=0).fit(E).labels_))

# name each cluster by the terms that separate it, computed not assigned
texts = {}
for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
    if line.strip():
        q = json.loads(line)
        texts[q["prompt_id"]] = " ".join(m["content"] for m in q["prompt"]["messages"] if m["role"] == "user")
T = [texts[p] for p in pids]
vec = TfidfVectorizer(max_features=20000, stop_words="english", ngram_range=(1, 2),
                      min_df=3, max_df=0.30, sublinear_tf=True)
X = vec.fit_transform(T)
terms = np.array(vec.get_feature_names_out())
Xd = np.asarray(X.todense())

clusters = []
for c in range(K):
    m = lab == c
    score = Xd[m].mean(0) - Xd[~m].mean(0)          # separating, not merely frequent
    top = terms[np.argsort(-score)[:14]].tolist()
    sub = [rows[p] for i, p in enumerate(pids) if m[i] and p in rows]

    def mm(key):
        v = [r[key] for r in sub if r.get(key) is not None]
        return float(np.mean(v)) if v else None
    arms = collections.defaultdict(list)
    for r in sub:
        for kk, vv in (r.get("verdicts") or {}).items():
            arms[kk].append(vv)
    subj = collections.Counter(r["subj_major"] for r in sub if r["subj_major"])
    imp = collections.Counter(r["imp_major"] for r in sub if r["imp_major"])
    clusters.append({
        "id": c, "n": int(m.sum()), "terms": top, "label": " · ".join(top[:3]),
        "cx": float(XY[m, 0].mean()), "cy": float(XY[m, 1].mean()),
        "mean_crit": mm("n_crit"), "mean_ann": mm("n_ann"), "mean_consensus": mm("consensus"),
        "mean_split_rate": mm("split_rate"), "mean_negshare": mm("negshare"),
        "mean_len_user": mm("len_user"), "mean_turns": mm("n_turns"),
        "tie_rate": float(np.mean([r["tie"] for r in sub])) if sub else None,
        "unacc_rate": float(np.mean([r["n_unacc"] > 0 for r in sub])) if sub else None,
        "subjectivity": subj.most_common(3), "importance": imp.most_common(3),
        "arm_hits": {kk: float(np.mean(v)) for kk, v in arms.items()},
    })

for i, p in enumerate(pids):
    if p in rows:
        rows[p]["cluster"] = int(lab[i])
        rows[p]["x"] = float(XY[i, 0])
        rows[p]["y"] = float(XY[i, 1])

corpus["rows"] = list(rows.values())
corpus["clusters"] = clusters
corpus["k"] = K
corpus["method"] = ("Qwen3.5-0.8B-Base mean-pooled last hidden state, L2-normalised → PCA-50 → "
                    "t-SNE(perplexity 30, pca init, seed 0). KMeans k=12 on the 1024-d embedding.")
corpus["silhouette"] = sil
corpus["silhouette_by_k"] = sil_by_k
corpus["silhouette_tfidf_best"] = 0.0148
corpus["caveat"] = ("STRUCTURE IS WEAK AND IS SHOWN, NOT ASSERTED. Best silhouette over k∈{8,12,18,24} "
                    "is %.4f; the best TF-IDF partition reached 0.0148. Both are far below the ~0.25 "
                    "at which a partition is usually called clean, so the cloud is drawn ungated and "
                    "the reader decides. k=12 is a CHOICE. Cluster names are the terms that most "
                    "SEPARATE the cluster from the rest, computed, never assigned." % max(sil_by_k.values()))

# ---- the rounds, as their own cloud
rounds = []
for e in corpus.get("_epochs", []) or []:
    pass
P = json.loads((OUT / "payload.json").read_text())
gi = 0
for ei, e in enumerate(P["campaign"]["epochs"]):
    for ai, a in enumerate(e["arcs"]):
        for r in a["rounds"]:
            rounds.append({"i": gi, "id": r["id"], "title": r["title"], "slug": r["slug"],
                           "epoch": ei, "epoch_id": e["id"], "arc": a["id"], "arc_title": a["title"],
                           "n_results": r["n_results"], "readme": r["has_readme"], "run": r["has_run"]})
            gi += 1
corpus["rounds"] = rounds
(OUT / "corpus.json").write_text(json.dumps(corpus, ensure_ascii=False))
print("silhouette k=12 %.4f   by k: %s" % (sil, sil_by_k))
print("wrote corpus.json", (OUT / "corpus.json").stat().st_size, "bytes  ·", len(rounds), "rounds")
for c in clusters:
    print(f"  c{c['id']:<2} n={c['n']:<4} {' · '.join(c['terms'][:5])}")
