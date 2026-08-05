"""The 1,012 annotators as their own cloud, positioned by how they actually voted.

⛔ THIS RUNS NO NEW EXPERIMENT, AND THAT IS THE POINT. The prior-art gate found both
questions already answered by this campaign:
  R183 — does any shipped demographic mark a coherent values bloc? 28 levels tested with
         a permutation null; 2 clear, both countries, at ~+6%, against a PLANTED bloc at
         +73.7%. (Its NEGATIVE control failed its pre-registered 0.02 bound and reached
         0.0257, so the resolution floor was raised to the p95 — carried onto the page.)
  R03  — do stated values predict revealed choices? 11,327 judgements: +0.0017
         [-0.0061,+0.0097] over a permuted null. Chance.
So this file REUSES those verdicts and gives them a body: the space the raters occupy, so
that "no demographic bloc" can be looked at instead of taken on the number.

POSITION IS VOTES, NOT DEMOGRAPHICS. Each rater is a sparse sign vector over
(prompt × pair); cosine between two raters is therefore computed on the prompts they
SHARE and is silent elsewhere. If demographics organised the panel, colouring this cloud
by any field would show bands. That is the falsifiable part, and it is left to the eye
because R183 already did it with a null.
"""
import json, collections, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "atlas"
PEO = OUT / "a"
PEO.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT))
from corebench.select_core import cls, parse_ranking, L, PAIRS

# ------------------------------------------------------------------ read
demo, ideal = {}, {}
for line in open(ROOT / "data/annotators.jsonl", encoding="utf-8"):
    if not line.strip():
        continue
    r = json.loads(line)
    d = r.get("demographics") or {}
    demo[r["annotator_id"]] = d
    ideal[r["annotator_id"]] = d.get("ideal-model-behavior") or ""

work = collections.defaultdict(list)          # aid -> [(pid, world, personal, unacc, why...)]
pmeta = {}
for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
    if not line.strip():
        continue
    q = json.loads(line)
    pid = q["prompt_id"]
    user = " ".join(m["content"] for m in q["prompt"]["messages"] if m["role"] == "user")
    pmeta[pid] = user[:150]
    for a in q["metadata"]["assessments"]:
        rb = a["ranking_blocks"]
        w = (rb.get("world") or [{}])[0]
        p_ = (rb.get("personal") or [{}])[0]
        u_ = (rb.get("unacceptable") or [{}])[0]
        work[a["annotator_id"]].append({
            "pid": pid, "world": w.get("ranking"), "personal": p_.get("ranking"),
            "world_why": (w.get("rationale") or "")[:900],
            "personal_why": (p_.get("rationale") or "")[:900],
            "unacceptable": u_.get("rating"), "unacceptable_why": (u_.get("rationale") or "")[:600],
            "importance": a.get("importance"), "representativeness": a.get("representativeness"),
            "subjectivity": a.get("subjectivity")})

aids = sorted(work)
print(len(aids), "raters,", len(pmeta), "prompts")

# ------------------------------------------------------------------ vote vectors
pidx = {p: i for i, p in enumerate(sorted(pmeta))}
Vt = np.zeros((len(aids), len(pidx) * 6), dtype=np.float32)
for i, a in enumerate(aids):
    for it in work[a]:
        y = parse_ranking(it["world"] or "")
        if not y:
            continue
        c = cls(np.array(y, float))
        base = pidx[it["pid"]] * 6
        for k in range(6):
            Vt[i, base + k] = c[k]
nrm = np.linalg.norm(Vt, axis=1, keepdims=True)
Vn = Vt / np.where(nrm == 0, 1, nrm)
Sim = Vn @ Vn.T                                # cosine, implicitly over shared prompts only
shared = ((Vt != 0).astype(np.float32) @ (Vt != 0).astype(np.float32).T) / 6.0
np.fill_diagonal(shared, 0)
print("pairs sharing >=1 prompt: %.1f%%" % (100 * (shared > 0).sum() / (len(aids) ** 2 - len(aids))))

from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
D = 1.0 - Sim
P30 = PCA(n_components=30, random_state=0).fit_transform(Sim)
XY = TSNE(n_components=2, perplexity=28, init="pca", random_state=0, max_iter=1000).fit_transform(P30)
XY = (XY - XY.min(0)) / (XY.max(0) - XY.min(0))
PC = PCA(n_components=2, random_state=0).fit_transform(Sim)
PC = (PC - PC.min(0)) / (PC.max(0) - PC.min(0))

# ------------------------------------------------------------------ per-rater rows + detail
FIELDS = ["age", "gender", "country_of_residence", "education_level",
          "generative_ai_usage", "ai_concern_level"]
rows = []
for i, a in enumerate(aids):
    W = work[a]
    nsplit = sum(1 for it in W
                 if it["world"] and it["personal"]
                 and it["world"].replace(" ", "") != it["personal"].replace(" ", ""))
    nun = sum(1 for it in W if it["unacceptable"])
    wl = [len(it["world_why"]) for it in W if it["world_why"]]
    d = demo.get(a, {})
    rows.append({
        "aid": a, "short": a[:8],
        "n_prompts": len(W), "n_split": nsplit, "split_rate": nsplit / max(len(W), 1),
        "n_unacc": nun, "unacc_rate": nun / max(len(W), 1),
        "mean_why_len": float(np.mean(wl)) if wl else 0.0,
        "ideal_len": len(ideal.get(a, "")),
        "x": float(XY[i, 0]), "y": float(XY[i, 1]),
        "x_pca": float(PC[i, 0]), "y_pca": float(PC[i, 1]),
        **{f: d.get(f) for f in FIELDS},
    })
    (PEO / f"{a}.json").write_text(json.dumps({
        "aid": a, "demographics": d, "ideal": ideal.get(a, ""),
        "work": [dict(it, title=pmeta.get(it["pid"], "")) for it in W],
    }, ensure_ascii=False))

# ------------------------------------------------------------------ reuse the two verdicts
B = json.loads((ROOT / "E04_no_fraction_only_an_equivalence_class/A14_do_our_own_claims_survive_an_adversary"
                       "/R183_does_any_attribute_mark_a_bloc/results/blocs.json").read_text())
S = json.loads((ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
                       "/R03_stated_vs_revealed/results/a03_stated_vs_revealed.json").read_text())

# how many raters carry each level, for the cloud's legend
counts = {f: collections.Counter(r[f] for r in rows if r[f]) for f in FIELDS}

(OUT / "people.json").write_text(json.dumps({
    "rows": rows, "fields": FIELDS, "counts": {f: counts[f].most_common() for f in FIELDS},
    "n": len(rows),
    "r183": {"levels": B["levels"], "z_threshold": B["z_threshold"],
             "resolution_floor": B["resolution_floor"],
             "planted": B["controls"]["positive_planted_bloc"],
             "negative_p95": B["controls"]["negative_p95_resolution_floor"],
             "negative_bound": B["controls"]["negative_preregistered_bound"],
             "negative_passed": B["controls"]["negative_passed"],
             "positive_passed": B["controls"]["positive_passed"],
             "perms": B["perms"], "min_n": B["min_n"], "raters": B["raters"],
             "blocs": B.get("blocs"), "antiblocs": B.get("antiblocs"), "tested": B.get("tested")},
    "r03": {"hit": S["hit_rate"], "hit_ci": S["hit_ci"], "null": S["permuted_null"],
            "diff": S["difference"], "diff_ci": S["difference_ci"],
            "n_j": S["judgements"], "n_a": S["annotators"], "verdict": S["verdict"]},
    "source": "votes: data/comparisons.jsonl (world block) · demographics: data/annotators.jsonl · "
              "verdicts REUSED verbatim from R183 and R03, not recomputed",
}, ensure_ascii=False))
print("wrote people.json", (OUT / "people.json").stat().st_size, "bytes ·", len(rows), "detail files")
print("R183: %d levels, %d clear z>%.1f | planted bloc %+.3f | negative control passed: %s"
      % (len(B["levels"]), sum(1 for l in B["levels"] if l["z"] > B["z_threshold"]),
         B["z_threshold"], B["controls"]["positive_planted_bloc"], B["controls"]["negative_passed"]))
print("R03 : hit %.4f vs null %.4f, diff %+.4f %s" % (S["hit_rate"], S["permuted_null"],
                                                      S["difference"], S["difference_ci"]))
