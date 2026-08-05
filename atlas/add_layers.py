"""Six projections of the same cloud, and the campaign's findings as LAYERS over it.

WHY SIX AND NOT ONE. t-SNE preserves neighbourhoods and destroys distance; PCA preserves
distance and destroys locality; a sorted lattice destroys geometry entirely and in exchange
gives ZERO occlusion and an exactly decodable position. They disagree, and the disagreement
is information. A single projection asserted as "the map" is the failure this file avoids.

WHAT A LAYER IS. Each layer is a FINDING re-expressed as a predicate over prompts: the set
this finding is about. Turning a conclusion back into a subset is what makes it falsifiable
by eye — if a layer that claims to be about a mechanism scatters uniformly over the corpus,
that is visible immediately, and it is reported next to the layer as a spatial statistic.
"""
import json, pathlib, collections, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "atlas"
sys.path.insert(0, str(ROOT))

z = np.load(OUT / "emb.npz", allow_pickle=True)
E, pids = z["emb"], [str(x) for x in z["pid"]]
corpus = json.loads((OUT / "corpus.json").read_text())
rows = {r["pid"]: r for r in corpus["rows"]}
idx = {p: i for i, p in enumerate(pids)}

# ------------------------------------------------------------------ projections
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE, MDS

PROJ = {}


def norm(XY):
    XY = np.asarray(XY, float)
    lo, hi = XY.min(0), XY.max(0)
    return ((XY - lo) / np.where(hi - lo == 0, 1, hi - lo)).astype(np.float32)


PROJ["tsne"] = norm(np.load(OUT / "_xy.npy"))
print("tsne ok")

P50 = PCA(n_components=50, random_state=0).fit(E)
PROJ["pca"] = norm(P50.transform(E)[:, :2])
evr = P50.explained_variance_ratio_[:2]
print("pca ok", evr)

import umap
PROJ["umap"] = norm(umap.UMAP(n_neighbors=25, min_dist=0.12, random_state=0).fit_transform(E))
print("umap ok")

sub = np.random.default_rng(0).choice(len(E), min(len(E), 700), replace=False)
mds = MDS(n_components=2, random_state=0, normalized_stress="auto", n_init=1, max_iter=140)
M = np.full((len(E), 2), np.nan)
M[sub] = mds.fit_transform(P50.transform(E)[sub][:, :20])
# place the rest at their nearest embedded neighbour among the subset
D = E @ E[sub].T
for i in range(len(E)):
    if np.isnan(M[i, 0]):
        M[i] = M[sub[int(np.argmax(D[i]))]]
PROJ["mds"] = norm(M)
print("mds ok (700 embedded, rest snapped to nearest)")

# a sorted lattice: zero occlusion, position exactly decodable
n = len(pids)
cols = int(np.ceil(np.sqrt(n * 1.9)))
key = np.array([(rows[p]["cluster"], -(rows[p].get("n_crit") or 0)) for p in pids],
               dtype=[("c", int), ("k", int)])
order = np.argsort(key, order=("c", "k"))
G = np.zeros((n, 2))
for rank, i in enumerate(order):
    G[i] = [(rank % cols) / max(cols - 1, 1), 1 - (rank // cols) / max((n - 1) // cols, 1)]
PROJ["grid"] = norm(G)
print("grid ok", cols, "cols")

# beeswarm on consensus: x = the value itself, y = jitter that avoids collision
vals = np.array([rows[p].get("consensus") or 0.0 for p in pids])
o = np.argsort(vals)
B = np.zeros((n, 2))
lane = collections.defaultdict(float)
for rank, i in enumerate(o):
    x = (vals[i] - vals.min()) / max(float(vals.max() - vals.min()), 1e-9)
    slot = int(x * 190)
    B[i] = [x, 0.5 + ((lane[slot] % 22) - 11) * 0.028]
    lane[slot] += 1
PROJ["swarm"] = norm(B)
print("swarm ok")

for p, i in idx.items():
    if p in rows:
        for k, XY in PROJ.items():
            rows[p]["x_" + k] = float(XY[i, 0])
            rows[p]["y_" + k] = float(XY[i, 1])

corpus["projections"] = {
    "tsne": {"label": "t-SNE", "note": "neighbourhoods preserved, distances NOT — read near/far only"},
    "umap": {"label": "UMAP", "note": "n_neighbors 25, min_dist 0.12 — more global structure than t-SNE, still not a metric"},
    "pca": {"label": "PCA", "note": f"linear, distances ARE meaningful; these 2 axes hold {100*evr.sum():.1f}% of the variance"},
    "mds": {"label": "MDS", "note": "700 prompts embedded by stress majorisation; the rest snapped to their nearest neighbour — stated, not hidden"},
    "grid": {"label": "sorted lattice", "note": "geometry discarded; ZERO occlusion and position exactly decodable — sorted by neighbourhood, then criteria count"},
    "swarm": {"label": "beeswarm", "note": "x = consensus strength, y = collision-avoiding jitter only — a 1-D distribution with every point still separate"},
}

# ------------------------------------------------------------------ audit layers
def get(p, k, d=None):
    return rows[p].get(k, d)


V = lambda p, a: (rows[p].get("verdicts") or {}).get(a)

LAYERS = []


def add(key, label, finding, pred, colour):
    members = [p for p in rows if pred(p)]
    LAYERS.append({"key": key, "label": label, "finding": finding, "colour": colour,
                   "pids": members, "n": len(members)})


add("no_rubric", "no rubric — silently dropped",
    "110 prompts (10.2%) carry comparisons and rankings but no rubric row, so every round in this "
    "campaign ran on 968 and never explained the missing 110.",
    lambda p: not get(p, "has_rubric"), "#f7768e")

add("modal_tie", "modal target is a TIE",
    "The 'human answer' is the most common pairwise class. On these prompts two classes are equally "
    "common and the winner is decided by dictionary insertion order.",
    lambda p: bool(get(p, "tie")), "#ff9e64")

add("all_tie", "humans tied all four",
    "The modal class is all-zero: an empty core scores 6/6 by construction.",
    lambda p: get(p, "target") is not None and all(v == 0 for v in get(p, "target")), "#bb9af7")

add("core_beats_topw", "coval_core BEATS topw_k4",
    "The released core and the top-weight rule are statistically indistinguishable in aggregate "
    "(0.6092 vs 0.6090). Per prompt they disagree constantly — this is where the incumbent wins.",
    lambda p: V(p, "coval_core") is not None and V(p, "topw_k4") is not None
              and V(p, "coval_core") > V(p, "topw_k4"), "#9ece6a")

add("topw_beats_core", "topw_k4 BEATS coval_core",
    "The same comparison, the other way. If the aggregate tie were an identity these two sets would "
    "be empty; they are not, and their near-equal SIZE is what makes the aggregate a tie.",
    lambda p: V(p, "coval_core") is not None and V(p, "topw_k4") is not None
              and V(p, "topw_k4") > V(p, "coval_core"), "#7aa2f7")

add("sign_rescue", "the sign rescues the sum",
    "full_weighted (Σ w·sat) strictly beats full (Σ sat) here. This is the mechanism: the unsigned "
    "sum adds a −10 criterion exactly like a +10 one.",
    lambda p: V(p, "full_weighted") is not None and V(p, "full") is not None
              and V(p, "full_weighted") > V(p, "full"), "#e0af68")

add("sign_hurts", "the sign HURTS the sum",
    "The control on the layer above. If signing were a universal improvement this set would be empty. "
    "It is not — so the sign is a mechanism with a cost, not a free win.",
    lambda p: V(p, "full_weighted") is not None and V(p, "full") is not None
              and V(p, "full_weighted") < V(p, "full"), "#f7768e")

add("full_beats_all", "no k=4 core beats full",
    "Selection strictly loses here: the whole rubric outscores every four-criterion rule tried.",
    lambda p: V(p, "full") is not None and (rows[p].get("verdicts") or {}) and
              V(p, "full") > max([v for k, v in (rows[p].get("verdicts") or {}).items()
                                  if k not in ("full", "full_weighted")] or [99]), "#73daca")

add("topabs_collapse", "topabs_k4 collapses",
    "The |w| rule scores 2 or fewer of six. It selects on magnitude, which admits the −10 criteria "
    "the unsigned sum then adds as credit.",
    lambda p: V(p, "topabs_k4") is not None and V(p, "topabs_k4") <= 2, "#f7768e")

add("all_arms_fail", "every construction fails",
    "No arm reaches 4/6. Neither the rubric nor any core recovers this prompt's human ordering.",
    lambda p: (rows[p].get("verdicts") or {}) and
              max((rows[p].get("verdicts") or {}).values()) < 4, "#565d78")

add("all_arms_win", "every construction succeeds",
    "Every arm reaches 5/6 or better — the prompt is easy for the whole family, so it separates nothing.",
    lambda p: (rows[p].get("verdicts") or {}) and
              min((rows[p].get("verdicts") or {}).values()) >= 5, "#9ece6a")

add("split_heavy", "personal ≠ world for a third of raters",
    "The campaign uses the WORLD ranking only. Here at least a third of annotators ranked differently "
    "when asked for their personal preference — so the target is a choice with visible cost.",
    lambda p: (get(p, "split_rate") or 0) >= 1 / 3, "#bb9af7")

add("unacceptable", "someone flagged an answer unacceptable",
    "The unacceptable block is never used as a target by any round. These are the prompts where it fires.",
    lambda p: (get(p, "n_unacc") or 0) > 0, "#ff9e64")

add("neg_heavy", "a third of criteria carry w < 0",
    "Where the unsigned aggregator has the most to destroy.",
    lambda p: (get(p, "negshare") or 0) >= 1 / 3, "#f7768e")

add("core_not_in_full", "released core shares NO text with full",
    "coval_core is an LM distillation that merges, negates and selects — the card says it can 'drift "
    "from the data'. Here not one of its criteria appears verbatim in the rubric it distils.",
    lambda p: get(p, "n_core", 0) and get(p, "core_in_full", 0) == 0, "#e0af68")

# ---- spatial statistic per layer: is it concentrated, or uniform over the cloud?
XY = PROJ["tsne"]
for L in LAYERS:
    m = np.array([idx[p] for p in L["pids"] if p in idx])
    if len(m) < 8:
        L["dispersion"] = None
        L["cluster_conc"] = None
        continue
    pts = XY[m]
    # mean pairwise distance of the layer against 200 size-matched random draws
    rng = np.random.default_rng(0)

    def mpd(a):
        s = a[rng.choice(len(a), min(len(a), 160), replace=False)] if len(a) > 160 else a
        d = np.linalg.norm(s[:, None] - s[None], axis=2)
        return float(d[np.triu_indices(len(s), 1)].mean())
    obs = mpd(pts)
    null = [mpd(XY[rng.choice(len(XY), len(m), replace=False)]) for _ in range(60)]
    L["dispersion"] = obs
    L["null_mean"] = float(np.mean(null))
    L["null_sd"] = float(np.std(null))
    L["z"] = float((obs - np.mean(null)) / (np.std(null) or 1))
    cc = collections.Counter(rows[p]["cluster"] for p in L["pids"])
    L["cluster_conc"] = float(max(cc.values()) / len(L["pids"]))
    L["top_cluster"] = int(cc.most_common(1)[0][0])

corpus["layers"] = LAYERS
corpus["layer_note"] = ("Each layer is a finding re-expressed as a set of prompts. `z` compares the "
                        "layer's mean pairwise distance in the t-SNE view against 60 size-matched "
                        "random draws: z near 0 means the finding is spread uniformly over the corpus "
                        "and is NOT a property of any domain; strongly negative means it concentrates.")
(OUT / "corpus.json").write_text(json.dumps(corpus, ensure_ascii=False))
print("\nwrote corpus.json", (OUT / "corpus.json").stat().st_size, "bytes")
print(f"{'layer':<34}{'n':>6}{'z':>8}{'top cluster share':>20}")
for L in LAYERS:
    print(f"{L['label'][:33]:<34}{L['n']:>6}{(f'{L[chr(122)]:+.2f}' if L.get('z') is not None else '—'):>8}"
          f"{(f'{100*L[chr(99)+chr(108)+chr(117)+chr(115)+chr(116)+chr(101)+chr(114)+chr(95)+chr(99)+chr(111)+chr(110)+chr(99)]:.0f}% in c{L[chr(116)+chr(111)+chr(112)+chr(95)+chr(99)+chr(108)+chr(117)+chr(115)+chr(116)+chr(101)+chr(114)]}' if L.get('cluster_conc') else '—'):>20}")
