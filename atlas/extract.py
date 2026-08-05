"""Extract every number the atlas page shows, from the objects, into one payload.

NOTHING in the page is typed by hand. If a number is not in this payload it is not on the
page. The payload records, per block, WHERE it came from, so the page can print its own
provenance -- that is the completeness ledger P13 demands.
"""
import json, collections, itertools, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from covalx.judge import load_join, build_prompt
from corebench.select_core import cls, parse_ranking, L, PAIRS

OUT = ROOT / "atlas" / "payload.json"
FULL_NPZ = (ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
                   "/R04_rebuild_satisfaction/results/a04_full.npz")
CORE_NPZ = ROOT / "corebench/results/sat_coval_core.npz"
WORKED = "0164a085-1715-5f7f-b6e3-924d392d5dee"
P = {}


def load_sat(path):
    d = np.load(path, allow_pickle=True)
    s = collections.defaultdict(dict)
    for kk, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(kk).split("|")
        s[pid][(int(i), ltr)] = float(v)
    return s


def sh(cmd):
    return subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True).stdout.strip()


# ---------------------------------------------------------------- 1 · the campaign
epochs = []
for e in sorted(ROOT.glob("E0*")):
    if not e.is_dir():
        continue
    arcs = []
    for a in sorted(e.glob("A*")):
        if not a.is_dir():
            continue
        rounds = []
        for r in sorted(a.glob("R*")):
            if not r.is_dir():
                continue
            rounds.append({
                "id": r.name.split("_")[0],
                "slug": r.name,
                "title": r.name.split("_", 1)[1].replace("_", " ") if "_" in r.name else r.name,
                "has_run": (r / "run.py").exists(),
                "has_readme": (r / "README.md").exists(),
                "n_results": len(list((r / "results").glob("*"))) if (r / "results").is_dir() else 0,
            })
        arcs.append({"id": a.name.split("_")[0], "slug": a.name,
                     "title": a.name.split("_", 1)[1].replace("_", " ") if "_" in a.name else a.name,
                     "rounds": rounds})
    epochs.append({"id": e.name.split("_")[0], "slug": e.name,
                   "title": e.name.split("_", 1)[1].replace("_", " ") if "_" in e.name else e.name,
                   "arcs": arcs})
P["campaign"] = {
    "epochs": epochs,
    "n_epochs": len(epochs),
    "n_arcs": sum(len(e["arcs"]) for e in epochs),
    "n_rounds": sum(len(a["rounds"]) for e in epochs for a in e["arcs"]),
    "n_commits": int(sh("git rev-list --count HEAD") or 0),
    "n_runpy": int(sh("find E0* -name run.py | wc -l") or 0),
    "n_readme": int(sh("find E0* -name README.md | wc -l") or 0),
    "source": "directory tree + git rev-list, this repo",
}

# commit cadence
log = sh("git log --format=%ad --date=short | sort | uniq -c")
P["campaign"]["commits_by_day"] = [
    {"day": ln.split()[1], "n": int(ln.split()[0])} for ln in log.splitlines() if len(ln.split()) == 2]

# ---------------------------------------------------------------- 2 · the release
joined = load_join(ROOT / "data/comparisons.jsonl", ROOT / "data/conversation_rubrics.jsonl")
rub = {p: r for p, _, r in joined}
comp = {}
for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
    if line.strip():
        q = json.loads(line)
        comp[q["prompt_id"]] = q

sizes = [len(r.get("coval_full") or []) for r in rub.values()]
nscore, contested, reuse = [], 0, collections.Counter()
n_items = 0
for r in rub.values():
    for it in (r.get("coval_full") or []):
        sc = [s["score"] for s in it.get("scores") or []]
        if not sc:
            continue
        n_items += 1
        nscore.append(len(sc))
        if any(x > 0 for x in sc) and any(x < 0 for x in sc):
            contested += 1
        reuse[it["criterion"]] += 1

ppa = collections.defaultdict(set)
nann = []
for pid, q in comp.items():
    a = q["metadata"]["assessments"]
    nann.append(len(a))
    for x in a:
        ppa[x["annotator_id"]].add(pid)

# ranking blocks + rationale
blocks = collections.Counter()
nrat = 0
splits = 0
tgt, allranks = {}, {}
for pid, q in comp.items():
    per = {}
    for x in q["metadata"]["assessments"]:
        for bk in ("world", "personal", "unacceptable"):
            for e in (x["ranking_blocks"].get(bk) or []):
                blocks[bk] += 1
                if e.get("rationale"):
                    nrat += 1
        w = (x["ranking_blocks"].get("world") or [{}])[0].get("ranking")
        pv = (x["ranking_blocks"].get("personal") or [{}])[0].get("ranking")
        if w and pv and w.replace(" ", "") != pv.replace(" ", ""):
            splits += 1
        per.setdefault("w", []).append(w)
    ys = [parse_ranking(e["ranking"])
          for x in q["metadata"]["assessments"]
          for e in (x["ranking_blocks"].get("world") or []) if e.get("ranking")]
    ys = [y for y in ys if y]
    if ys:
        c = collections.Counter(cls(np.array(y, float)) for y in ys)
        allranks[pid] = c
        tgt[pid] = c.most_common(1)[0][0]

modal_tie = sum(1 for c in allranks.values()
                if len(c) > 1 and c.most_common()[0][1] == c.most_common()[1][1])
alltie = sum(1 for t in tgt.values() if all(v == 0.0 for v in t))

# author == ranker overlap
ov = []
for pid, r in rub.items():
    if pid not in comp:
        continue
    rankers = {a["annotator_id"] for a in comp[pid]["metadata"]["assessments"]}
    scorers = {s["annotator_id"] for it in (r.get("coval_full") or []) for s in (it.get("scores") or [])}
    if scorers:
        ov.append(len(rankers & scorers) / len(scorers))

P["release"] = {
    "n_comparison_rows": len(comp),
    "n_rubric_rows": sum(1 for _ in open(ROOT / "data/conversation_rubrics.jsonl", encoding="utf-8")),
    "n_joined": len(joined),
    "n_lost": len(comp) - len(joined),
    "n_annotators": len(ppa),
    "prompts_per_annotator": {"min": int(min(len(v) for v in ppa.values())),
                              "median": float(np.median([len(v) for v in ppa.values()])),
                              "max": int(max(len(v) for v in ppa.values())),
                              "over_card_cap": int(sum(1 for v in ppa.values() if len(v) > 20))},
    "annotators_per_prompt": {"min": int(min(nann)), "median": float(np.median(nann)), "max": int(max(nann))},
    "n_criteria": n_items,
    "criteria_per_prompt": {"min": int(min(sizes)), "median": float(np.median(sizes)), "max": int(max(sizes))},
    "scorers_per_criterion_hist": dict(sorted(collections.Counter(nscore).items())),
    "single_scored_share": float(np.mean(np.array(nscore) == 1)),
    "sign_contested_share": contested / n_items,
    "distinct_criterion_texts": len(reuse),
    "reused_texts": sum(1 for v in reuse.values() if v > 1),
    "ranking_blocks": dict(blocks),
    "n_rationales": nrat,
    "personal_world_splits": splits,
    "modal_target_ties": modal_tie,
    "all_tie_targets": alltie,
    "n_targets": len(tgt),
    "author_is_ranker_mean": float(np.mean(ov)),
    "author_is_ranker_full": int(sum(1 for x in ov if x == 1.0)),
    "source": "data/comparisons.jsonl + data/conversation_rubrics.jsonl, recomputed",
}

# ---------------------------------------------------------------- 3 · the worked example
sat = load_sat(FULL_NPZ)
csat = load_sat(CORE_NPZ)
pid = WORKED
items = rub[pid]["coval_full"]
ok = [i for i in range(len(items)) if all(sat[pid].get((i, x)) is not None for x in L)]
w = {i: float(np.mean([s["score"] for s in items[i].get("scores") or []]) or 0.0) for i in ok}
var = {i: float(np.var([sat[pid][(i, x)] for x in L])) for i in ok}
t = tgt[pid]


def agree(idxs):
    y = np.array([sum(sat[pid][(i, x)] for i in idxs) for x in L])
    return sum(cls(y)[q] == t[q] for q in range(6))


rules = {"full": ok}
rng = np.random.default_rng(0)
rules["random_k4"] = [int(x) for x in rng.choice(ok, 4, replace=False)]
rules["topw_k4"] = sorted(ok, key=lambda i: -w[i])[:4]
rules["topabs_k4"] = sorted(ok, key=lambda i: -abs(w[i]))[:4]
rules["topvar_k4"] = sorted(ok, key=lambda i: -var[i])[:4]
rules["topwvar_k4"] = sorted(ok, key=lambda i: -(abs(w[i]) * var[i]))[:4]
rules["indep_k4"] = sorted(ok, key=lambda i: -agree([i]))[:4]
g = []
for _ in range(4):
    g.append(max([i for i in ok if i not in g], key=lambda i: agree(g + [i])))
rules["greedy_k4"] = g
bh, bs = -1, ok[:4]
for c in itertools.combinations(ok, 4):
    h = agree(c)
    if h > bh:
        bh, bs = h, list(c)
rules["oracle_k4"] = bs

nc = len({i for (i, x) in csat[pid]})
P["worked"] = {
    "prompt_id": pid,
    "user_text": [m["content"] for m in comp[pid]["prompt"]["messages"] if m["role"] == "user"][0],
    "responses": [{"label": "ABCD"[i], "text": r["messages"][0]["content"]}
                  for i, r in enumerate(comp[pid]["responses"])],
    "target": list(t),
    "pairs": [f"{L[i]}{L[j]}" for i, j in PAIRS],
    "rankings": [{"world": (x["ranking_blocks"].get("world") or [{}])[0].get("ranking"),
                  "personal": (x["ranking_blocks"].get("personal") or [{}])[0].get("ranking"),
                  "world_rationale": (x["ranking_blocks"].get("world") or [{}])[0].get("rationale", "")[:400],
                  "personal_rationale": (x["ranking_blocks"].get("personal") or [{}])[0].get("rationale", "")[:400]}
                 for x in comp[pid]["metadata"]["assessments"]],
    "modal_counts": [{"cls": list(k), "n": v, "example": None} for k, v in allranks[pid].most_common()],
    "criteria": [{"i": i, "text": items[i]["criterion"], "w": w[i], "var": var[i],
                  "n_scores": len(items[i].get("scores") or []),
                  "scores": [s["score"] for s in items[i].get("scores") or []],
                  "sat": [sat[pid][(i, x)] for x in L], "solo_hit": agree([i])}
                 for i in ok],
    "rules": [{"name": k, "sel": sorted(int(i) for i in v),
               "y": [float(sum(sat[pid][(i, x)] for i in v)) for x in L],
               "hit": int(sum(cls(np.array([sum(sat[pid][(i, x)] for i in v) for x in L]))[q] == t[q]
                             for q in range(6)))}
              for k, v in rules.items()],
    "coval_core": {"n": nc,
                   "y": [float(sum(csat[pid][(i, x)] for i in range(nc))) for x in L],
                   "hit": int(sum(cls(np.array([sum(csat[pid][(i, x)] for i in range(nc)) for x in L]))[q] == t[q]
                                  for q in range(6))),
                   "texts": [x["criterion"] for x in (rub[pid].get("coval_core") or [])],
                   "in_full": [x["criterion"] in {items[i]["criterion"] for i in ok}
                               for x in (rub[pid].get("coval_core") or [])]},
    "judge_prompt": build_prompt(items[4]["criterion"], comp[pid]["responses"][0]["messages"][0]["content"]),
    "source": f"{FULL_NPZ.relative_to(ROOT)} + release, recomputed",
}

# ---------------------------------------------------------------- 4 · the sign mechanism
ZEFF = 1.959964 + 0.841621
acc = collections.defaultdict(list)
neg = collections.defaultdict(list)
rng = np.random.default_rng(0)
for p_, r_ in rub.items():
    if p_ not in tgt or p_ not in sat:
        continue
    it_ = r_.get("coval_full") or []
    ok_ = [i for i in range(len(it_)) if all(sat[p_].get((i, x)) is not None for x in L)]
    if not ok_:
        continue
    t_ = tgt[p_]
    w_ = {i: float(np.mean([s["score"] for s in it_[i].get("scores") or []]) or 0.0) for i in ok_}
    v_ = {i: float(np.var([sat[p_][(i, x)] for x in L])) for i in ok_}

    def f(pairs, s=sat):
        y = np.array([sum(c * s[p_][(i, x)] for i, c in pairs) for x in L])
        return sum(cls(y)[q] == t_[q] for q in range(6)) / 6

    R = {"full": ok_,
         "random_k4": [int(x) for x in rng.choice(ok_, min(4, len(ok_)), replace=False)],
         "topw_k4": sorted(ok_, key=lambda i: -w_[i])[:4],
         "topabs_k4": sorted(ok_, key=lambda i: -abs(w_[i]))[:4],
         "topvar_k4": sorted(ok_, key=lambda i: -v_[i])[:4],
         "topwvar_k4": sorted(ok_, key=lambda i: -(abs(w_[i]) * v_[i]))[:4]}
    for n_, s_ in R.items():
        acc[n_].append(f([(i, 1) for i in s_]))
        neg[n_].append(sum(1 for i in s_ if w_[i] < 0) / len(s_))
    pos = [i for i in ok_ if w_[i] > 0]
    if pos:
        acc["RANDOM_pos_k4"].append(f([(i, 1) for i in rng.choice(pos, min(4, len(pos)), replace=False)]))
        acc["BOTTOM_pos_k4"].append(f([(i, 1) for i in sorted(pos, key=lambda i: w_[i])[:4]]))
        acc["ALL_pos"].append(f([(i, 1) for i in pos]))
    acc["full_SIGNED"].append(f([(i, float(np.sign(w_[i]))) for i in ok_]))
    acc["full_WEIGHTED"].append(f([(i, w_[i]) for i in ok_]))
    if p_ in csat:
        n2 = len({i for (i, x) in csat[p_]})
        acc["coval_core"].append(f([(i, 1) for i in range(n2)], csat))

P["mechanism"] = {
    "arms": [{"name": k, "agree": float(np.mean(v)), "n": len(v),
              "neg_share": float(np.mean(neg[k])) if k in neg else None,
              "sd": float(np.std(v, ddof=1))}
             for k, v in acc.items()],
    "ZEFF": ZEFF,
    "statistic": "per-prompt mean pairwise agreement (A1-family), NOT the campaign's A2",
    "source": "recomputed here from a04_full.npz + sat_coval_core.npz",
}
a_, b_ = np.array(acc["topw_k4"]), np.array(acc["topabs_k4"])
d_ = a_ - b_
P["mechanism"]["topw_minus_topabs"] = {"delta": float(d_.mean()),
                                       "mde": float(ZEFF * d_.std(ddof=1) / np.sqrt(len(d_)))}
a_, b_ = np.array(acc["topw_k4"]), np.array(acc["RANDOM_pos_k4"])
m_ = min(len(a_), len(b_))
d_ = a_[:m_] - b_[:m_]
P["mechanism"]["topw_minus_randompos"] = {"delta": float(d_.mean()),
                                          "mde": float(ZEFF * d_.std(ddof=1) / np.sqrt(len(d_)))}

# ---------------------------------------------------------------- 5 · the leaderboard
lb = json.load(open(ROOT / "corebench/results/leaderboard.json"))
P["leaderboard"] = {
    "arms": sorted(lb),
    "metrics": sorted({k for a in lb for k in lb[a]}),
    "table": {a: {k: v for k, v in lb[a].items()} for a in lb},
    "source": "corebench/results/leaderboard.json, verbatim",
}

# ---------------------------------------------------------------- 6 · unused fields
FIELDS = ["model_provider", "included_in_balanced_subset", "moderation_flag", "pii_flag",
          "language_flag", "turns_user", "assistant_turn_share", "within_turn_id",
          "num_candidates", "en_flag", "conversation_type", "model_name", "if_chosen",
          "demographics", "rationale", "representativeness", "subjectivity"]
used = {}
for f in FIELDS:
    out = sh(f"grep -rl --include=*.py '{f}' . 2>/dev/null | grep -v '^./.git' | grep -v '^./_archive' | wc -l")
    used[f] = int(out or 0)
P["field_usage"] = {"counts": used, "source": "grep over *.py, excluding .git and _archive"}

mod = collections.Counter()
nmod = 0
flagged = 0
for line in open(ROOT / "data/metadata.jsonl", encoding="utf-8"):
    if not line.strip():
        continue
    r = json.loads(line)
    nmod += 1
    m = r.get("moderation_flag") or {}
    if m.get("flagged"):
        flagged += 1
    for k, v in (m.get("categories") or {}).items():
        if v:
            mod[k] += 1
P["moderation"] = {"n_rows": nmod, "flagged": flagged, "categories": dict(mod.most_common()),
                   "source": "data/metadata.jsonl, never read by any *.py"}

OUT.write_text(json.dumps(P, ensure_ascii=False))
print("wrote", OUT, OUT.stat().st_size, "bytes")
for k in P:
    print("  block:", k)
