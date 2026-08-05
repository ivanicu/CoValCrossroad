"""Extract EVERY prompt in the release as a browsable object, plus a domain clustering.

ARCHITECTURE. One small index (all prompts, one row each, with cluster + summary stats) and
one detail file per prompt (lazy-loaded on click). A single 30 MB payload would make the page
unopenable; 968 small files cost one fetch each and nothing up front.

CLUSTERING IS A CHOICE, NOT A MEASUREMENT, and the page says so. TF-IDF over the prompt text
+ KMeans. Chosen over embeddings because the cluster's top terms ARE the label -- an embedding
clustering would need a second model to name itself, and that model's opinion would then be
reported as a property of the data.
"""
import json, collections, pathlib, sys, re, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from covalx.judge import load_join
from corebench.select_core import cls, parse_ranking, L, PAIRS

OUT = ROOT / "atlas"
DET = OUT / "p"
DET.mkdir(parents=True, exist_ok=True)
FULL_NPZ = (ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
                   "/R04_rebuild_satisfaction/results/a04_full.npz")
CORE_NPZ = ROOT / "corebench/results/sat_coval_core.npz"
K_CLUSTERS = 14


def load_sat(path):
    d = np.load(path, allow_pickle=True)
    s = collections.defaultdict(dict)
    for kk, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(kk).split("|")
        s[pid][(int(i), ltr)] = float(v)
    return s


sat, csat = load_sat(FULL_NPZ), load_sat(CORE_NPZ)
joined = load_join(ROOT / "data/comparisons.jsonl", ROOT / "data/conversation_rubrics.jsonl")
rub = {p: r for p, _, r in joined}
comp = {}
for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
    if line.strip():
        q = json.loads(line)
        comp[q["prompt_id"]] = q

print(f"comparisons {len(comp)}  rubrics-joined {len(rub)}")

# ------------------------------------------------------------------ per prompt
rows, texts, order = [], [], []
for pid, q in comp.items():
    msgs = q["prompt"]["messages"]
    user = " ".join(m["content"] for m in msgs if m["role"] == "user")
    dev = " ".join(m["content"] for m in msgs if m["role"] == "developer")
    asst = [m["content"] for m in msgs if m["role"] == "assistant"]
    A = q["metadata"]["assessments"]

    ranks, pers, unacc, rats = [], [], [], []
    imp, rep, subj = collections.Counter(), collections.Counter(), collections.Counter()
    splits = 0
    for x in A:
        rb = x["ranking_blocks"]
        w = (rb.get("world") or [{}])[0]
        p_ = (rb.get("personal") or [{}])[0]
        u_ = (rb.get("unacceptable") or [{}])[0]
        if w.get("ranking"):
            ranks.append(w["ranking"])
        if p_.get("ranking"):
            pers.append(p_["ranking"])
        if u_.get("rating"):
            unacc.append(u_["rating"])
        if w.get("ranking") and p_.get("ranking") and \
           w["ranking"].replace(" ", "") != p_["ranking"].replace(" ", ""):
            splits += 1
        imp[x.get("importance")] += 1
        rep[x.get("representativeness")] += 1
        subj[x.get("subjectivity")] += 1
        rats.append({"aid": x["annotator_id"][:8],
                     "world": w.get("ranking"), "world_why": (w.get("rationale") or "")[:1200],
                     "personal": p_.get("ranking"), "personal_why": (p_.get("rationale") or "")[:1200],
                     "unacceptable": u_.get("rating"), "unacceptable_why": (u_.get("rationale") or "")[:1200]})

    ys = [parse_ranking(r) for r in ranks]
    ys = [y for y in ys if y]
    cnt = collections.Counter(cls(np.array(y, float)) for y in ys) if ys else collections.Counter()
    tgt = list(cnt.most_common(1)[0][0]) if cnt else None
    tie = bool(len(cnt) > 1 and cnt.most_common()[0][1] == cnt.most_common()[1][1])
    # pairwise consensus strength: mean |mean sign| over the six pairs
    consensus = None
    if ys:
        Mx = np.array([cls(np.array(y, float)) for y in ys], float)
        consensus = float(np.mean(np.abs(Mx.mean(axis=0))))

    r = rub.get(pid)
    crit, ncrit, wmin, wmax, negshare = [], 0, None, None, None
    core_txt, core_in_full = [], []
    if r:
        items = r.get("coval_full") or []
        ncrit = len(items)
        ws = []
        for i, it in enumerate(items):
            sc = [s["score"] for s in it.get("scores") or []]
            wv = float(np.mean(sc)) if sc else 0.0
            ws.append(wv)
            sv = [sat[pid].get((i, x)) for x in L] if pid in sat else [None] * 4
            crit.append({"i": i, "text": it["criterion"], "w": wv, "n": len(sc),
                         "scores": sc, "sat": sv,
                         "var": float(np.var([v for v in sv if v is not None])) if all(v is not None for v in sv) else None})
        if ws:
            wmin, wmax = float(min(ws)), float(max(ws))
            negshare = float(np.mean(np.array(ws) < 0))
        fulltxt = {it["criterion"] for it in items}
        for x in (r.get("coval_core") or []):
            core_txt.append(x["criterion"])
            core_in_full.append(x["criterion"] in fulltxt)

    # arm verdicts on this prompt
    verdicts = {}
    if r and pid in sat and tgt:
        items = r.get("coval_full") or []
        ok = [i for i in range(len(items)) if all(sat[pid].get((i, x)) is not None for x in L)]
        if ok:
            w_ = {i: crit[i]["w"] for i in ok}
            v_ = {i: crit[i]["var"] or 0.0 for i in ok}

            def hit(pairs, s=sat):
                y = np.array([sum(c * s[pid][(i, x)] for i, c in pairs) for x in L])
                return int(sum(cls(y)[q] == tgt[q] for q in range(6)))
            rng = np.random.default_rng(0)
            verdicts = {
                "full": hit([(i, 1) for i in ok]),
                "full_weighted": hit([(i, w_[i]) for i in ok]),
                "topw_k4": hit([(i, 1) for i in sorted(ok, key=lambda i: -w_[i])[:4]]),
                "topabs_k4": hit([(i, 1) for i in sorted(ok, key=lambda i: -abs(w_[i]))[:4]]),
                "topvar_k4": hit([(i, 1) for i in sorted(ok, key=lambda i: -v_[i])[:4]]),
                "random_k4": hit([(int(i), 1) for i in rng.choice(ok, min(4, len(ok)), replace=False)]),
            }
            if pid in csat:
                nc = len({i for (i, x) in csat[pid]})
                verdicts["coval_core"] = hit([(i, 1) for i in range(nc)], csat)

    detail = {
        "pid": pid, "developer": dev, "user": user, "prior_assistant": asst,
        "n_turns": len(msgs),
        "responses": [{"label": "ABCD"[i], "text": x["messages"][0]["content"]}
                      for i, x in enumerate(q["responses"])],
        "assessments": rats,
        "target": tgt, "target_tie": tie, "consensus": consensus,
        "ranking_counts": [{"cls": list(k), "n": v} for k, v in cnt.most_common()],
        "world_rankings": collections.Counter(r_.replace(" ", "") for r_ in ranks).most_common(),
        "personal_rankings": collections.Counter(r_.replace(" ", "") for r_ in pers).most_common(),
        "unacceptable": collections.Counter(str(u) for u in unacc).most_common(),
        "importance": imp.most_common(), "representativeness": rep.most_common(),
        "subjectivity": subj.most_common(),
        "criteria": crit, "coval_core": core_txt, "core_in_full": core_in_full,
        "verdicts": verdicts, "personal_world_splits": splits,
    }
    (DET / f"{pid}.json").write_text(json.dumps(detail, ensure_ascii=False))

    rows.append({
        "pid": pid, "title": re.sub(r"\s+", " ", user).strip()[:150],
        "n_ann": len(A), "n_crit": ncrit, "n_turns": len(msgs),
        "has_rubric": bool(r), "n_core": len(core_txt),
        "core_in_full": int(sum(core_in_full)),
        "target": tgt, "tie": tie, "consensus": consensus,
        "splits": splits, "split_rate": splits / max(len(A), 1),
        "wmin": wmin, "wmax": wmax, "negshare": negshare,
        "n_unacc": len(unacc),
        "subj_major": subj.most_common(1)[0][0] if subj else None,
        "imp_major": imp.most_common(1)[0][0] if imp else None,
        "verdicts": verdicts,
        "len_user": len(user),
        "len_resp": [len(x["messages"][0]["content"]) for x in q["responses"]],
    })
    texts.append(user)
    order.append(pid)

# ------------------------------------------------------------------ clustering
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

vec = TfidfVectorizer(max_features=8000, stop_words="english", ngram_range=(1, 2),
                      min_df=3, sublinear_tf=True)
X = vec.fit_transform(texts)
km = KMeans(n_clusters=K_CLUSTERS, n_init=10, random_state=0).fit(X)
lab = km.labels_
terms = np.array(vec.get_feature_names_out())

clusters = []
for c in range(K_CLUSTERS):
    idx = np.where(lab == c)[0]
    centroid = km.cluster_centers_[c]
    top = terms[np.argsort(-centroid)[:12]].tolist()
    sub = [rows[i] for i in idx]

    def m(key):
        v = [r[key] for r in sub if r.get(key) is not None]
        return float(np.mean(v)) if v else None
    subj = collections.Counter(r["subj_major"] for r in sub if r["subj_major"])
    imp = collections.Counter(r["imp_major"] for r in sub if r["imp_major"])
    arms = collections.defaultdict(list)
    for r in sub:
        for k, v in (r["verdicts"] or {}).items():
            arms[k].append(v)
    clusters.append({
        "id": c, "n": len(idx), "terms": top,
        "label": " · ".join(top[:3]),
        "mean_crit": m("n_crit"), "mean_ann": m("n_ann"), "mean_consensus": m("consensus"),
        "mean_split_rate": m("split_rate"), "mean_negshare": m("negshare"),
        "mean_len_user": m("len_user"), "mean_turns": m("n_turns"),
        "tie_rate": float(np.mean([r["tie"] for r in sub])),
        "unacc_rate": float(np.mean([r["n_unacc"] > 0 for r in sub])),
        "subjectivity": subj.most_common(3), "importance": imp.most_common(3),
        "arm_hits": {k: float(np.mean(v)) for k, v in arms.items()},
    })

for i, r in enumerate(rows):
    r["cluster"] = int(lab[i])

src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
(OUT / "corpus.json").write_text(json.dumps({
    "rows": rows, "clusters": clusters, "k": K_CLUSTERS,
    "method": "TF-IDF (1-2 grams, min_df=3, sublinear, english stopwords, 8000 feats) + KMeans k=14, seed 0",
    "caveat": "the clustering is a CHOICE, not a property of the release: k was set by hand and "
              "another k gives another partition. The top terms are the centroid's, so a cluster's "
              "name is computed, never assigned.",
    "n_prompts": len(rows), "n_with_rubric": sum(1 for r in rows if r["has_rubric"]),
    "source_sha256_16": src,
}, ensure_ascii=False))

print("wrote corpus.json:", (OUT / "corpus.json").stat().st_size, "bytes")
print("wrote", len(rows), "detail files into", DET)
for c in clusters:
    print(f"  c{c['id']:<2} n={c['n']:<4} {c['label'][:60]}")
