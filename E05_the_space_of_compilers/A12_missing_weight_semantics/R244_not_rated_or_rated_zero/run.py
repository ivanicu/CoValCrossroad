"""R244 -- "not rated" and "rated zero" are indistinguishable, and every weighted number here assumes one.

The blind arm (R235, seed 29, no sight of E05) reported that the weight matrix is 39.7% filled and
that the score 0 appears once in 102,147 ratings -- so a criterion a person did not rate and a
criterion they rated exactly zero cannot be told apart. It carried both readings as separate
specification cells and they gave different answers (eta 0.10 vs 0.25).

Every round in E05 uses W = mean of the scores THAT EXIST. That is the exclude-missing reading, and
it was never declared as a choice, never swept, and never named in any scope line. It is an
assumption under R220, R221, R222, R223, R228, R230, R231, R237, R239 and R243.

FIRST VERIFY THE CLAIM INDEPENDENTLY. A number from another arm is a hypothesis, not a fact, and
adopting it without checking is the failure this project has hit by trusting agent self-reports.

ESTIMAND        (a) the fill rate and the frequency of an exact zero -- verification.
                (b) R231's central quantity (official core vs random-4 floor, exact Q-class) under
                    BOTH readings, on the same prompts, same judge, same floor draws.
IDENTIFICATION  exact; arithmetic on released fields plus the r04 cache.
SCOPE           986 rubrics for (a); 968 prompts for (b), judge Qwen3.5-2B, floor 20 draws.
WORLDS          W1 the readings agree -> the assumption is harmless and can be declared and dropped
                W2 they disagree      -> every weighted number in E05 carries an undeclared choice
KILL            pre-registered: if the two readings move R231's core-minus-floor by more than the
                floor's own draw spread, E05's scope lines are incomplete and must say which
                reading they used.
POSITIVE CTRL   a synthetic rubric where every criterion IS rated must give identical answers under
                both readings -- if it does not, the two code paths differ for a reason unrelated to
                missingness and nothing below is readable.
NEGATIVE CTRL   a rubric where NO criterion is rated: both readings must be degenerate, not merely
                similar.
SEEDS           5 on the floor draws.
IMPOSSIBLE      which reading is CORRECT. The release does not say, and no analysis of the release
                can. This is partial identification and the honest output is both numbers.
"""
from __future__ import annotations
import collections, json, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
DRAWS, SEEDS = 20, [0, 1, 2, 3, 4]

import importlib.util
_s = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rub = [json.loads(l) for l in (DATA / "conversation_rubrics.jsonl").open()]

    # ---- (a) VERIFY the blind arm's claim rather than adopt it
    cells = filled = zeros = total_scores = 0
    vals = collections.Counter()
    for d in rub:
        raters = set()
        for it in d["coval_full"]:
            for s in (it.get("scores") or []):
                raters.add(s["annotator_id"])
        n_c = len([it for it in d["coval_full"] if it.get("scores")])
        cells += n_c * len(raters)
        for it in d["coval_full"]:
            for s in (it.get("scores") or []):
                filled += 1; total_scores += 1
                v = float(s["score"]); vals[v] += 1
                zeros += int(v == 0.0)
    print("=== (a) verifying R235's claim independently ===")
    print(" criterion x rater cells %d | filled %d | FILL RATE %.4f  (R235 said 0.397)"
          % (cells, filled, filled / cells if cells else 0))
    print(" exact zeros %d of %d ratings = 1 in %s   (R235 said 1 in 102,147)"
          % (zeros, total_scores, "%d" % (total_scores // zeros) if zeros else "never"))
    print(" the five most common values: %s"
          % ", ".join("%+g x%d" % (v, c) for v, c in vals.most_common(5)))
    verified = abs(filled / cells - 0.397) < 0.02 if cells else False
    print(" -> %s" % ("VERIFIED, within 2 points" if verified
                      else "NOT REPRODUCED -- the blind arm's figure does not hold here"))

    # ---- (b) R231's central quantity under both readings
    sf = r220.load_sat(R4 / "a04_full.npz")
    sc = r220.load_sat(R4 / "a04_core.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    def weights(f, ok, reading, all_raters):
        out = []
        for i in ok:
            sc_ = {s["annotator_id"]: float(s["score"]) for s in f[i]["scores"]}
            if reading == "exclude":
                out.append(np.mean(list(sc_.values())) if sc_ else 0.0)
            else:                                   # missing counted as an explicit zero
                out.append(np.mean([sc_.get(a, 0.0) for a in all_raters]) if all_raters else 0.0)
        return np.array(out, float)

    res = {}
    for reading in ("exclude", "zero"):
        core_hits, fl_seed = [], collections.defaultdict(list)
        for p in sorted(sf):
            if p not in recs:
                continue
            f = recs[p]["coval_full"]
            ok = [i for i, it in enumerate(f)
                  if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
            ci = sorted({k[0] for k in (sc.get(p) or {})})
            if len(ok) < 4 or not ci or not all((j, x) in sc[p] for j in ci for x in L):
                continue
            allr = sorted({s["annotator_id"] for i in ok for s in f[i]["scores"]})
            W = weights(f, ok, reading, allr)
            S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
            cf = cls((W[:, None] * S).sum(0))
            core_hits.append(cls(np.array([[sc[p][(j, x)] for x in L] for j in ci], float).sum(0)) == cf)
            for sd in SEEDS:
                rg = np.random.default_rng(abs(hash((p, sd, reading))) % (2 ** 32))
                # ⚠ THE FIRST VERSION CALLED rg.choice TWICE IN ONE EXPRESSION -- once to index W
                # and once to index S -- so the "random 4-criterion arm" multiplied one random
                # subset's WEIGHTS by a DIFFERENT random subset's SATISFACTIONS. Not a random arm at
                # all, a scrambled object. It showed as a floor of 0.1826 where R231 measured 0.3836
                # on the nominally identical design, and that discrepancy is the only reason it
                # surfaced: the core cell reproduced R231 exactly, so the fault had to be the floor.
                fl = []
                for _ in range(DRAWS // len(SEEDS)):
                    idx = list(rg.choice(len(ok), size=min(4, len(ok)), replace=False))
                    fl.append(cls((W[idx, None] * S[idx]).sum(0)) == cf)
                fl_seed[sd] += fl
        c = float(np.mean(core_hits))
        per = [float(np.mean(fl_seed[sd])) for sd in SEEDS]
        res[reading] = {"core": c, "floor": float(np.mean(per)),
                        "floor_min": min(per), "floor_max": max(per),
                        "delta": c - float(np.mean(per)), "n": len(core_hits)}

    ex = res["exclude"]
    print("\n=== ARITHMETIC CHECK against R231, before reading anything ===")
    print(" exclude-missing IS R231's reading. core %.4f vs R231's 0.3864 : %s"
          % (ex["core"], "OK" if abs(ex["core"] - 0.3864) < 0.005 else "MISMATCH"))
    print(" floor %.4f vs R231's 0.3836                                  : %s"
          % (ex["floor"], "OK" if abs(ex["floor"] - 0.3836) < 0.03 else "MISMATCH -- not the same arm"))
    print("\n=== (b) R231's central quantity under both readings ===")
    print("%-10s %8s %8s %10s %22s" % ("reading", "core", "floor", "core-floor", "floor [min,max]"))
    for k, v in res.items():
        print("%-10s %8.4f %8.4f %+10.4f %22s"
              % (k, v["core"], v["floor"], v["delta"],
                 "[%.4f, %.4f]" % (v["floor_min"], v["floor_max"])))
    spread = max(v["floor_max"] - v["floor_min"] for v in res.values())
    move = abs(res["exclude"]["delta"] - res["zero"]["delta"])

    print("\n=== controls ===")
    # POSITIVE: a fully-rated synthetic rubric must give identical answers under both readings
    rgc = np.random.default_rng(0)
    Wf = rgc.normal(size=8); Sf = rgc.random((8, 4))
    full_r = [{"scores": [{"annotator_id": "a", "score": Wf[i]}]} for i in range(8)]
    a = cls((np.array([np.mean([s["score"] for s in it["scores"]]) for it in full_r])[:, None] * Sf).sum(0))
    b = cls((np.array([np.mean([{"a": it["scores"][0]["score"]}.get(r_, 0.0) for r_ in ["a"]])
                       for it in full_r])[:, None] * Sf).sum(0))
    print(" POSITIVE fully-rated rubric, both readings identical : %s" % ("OK" if a == b else "PATHS DIFFER"))
    print(" NEGATIVE (a rubric with no ratings is excluded upstream by `it.get('scores')`,")
    print("           so the degenerate case cannot enter -- stated, not claimed as a pass)")

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    print(" the two readings move core-minus-floor by %.4f, floor draw spread %.4f" % (move, spread))
    if a != b:
        v = "UNVERIFIED -- the positive control failed; the two code paths differ for another reason"
    elif move > spread:
        v = ("E05's scope lines are INCOMPLETE. The exclude-missing reading is a choice worth "
             "%.4f on the central quantity, larger than the floor's own spread of %.4f, and no "
             "round declared it." % (move, spread))
    else:
        v = ("The reading is worth %.4f against a floor spread of %.4f -- INSIDE it. E05's numbers "
             "do not depend on the choice, and the assumption is harmless HERE. It is still "
             "undeclared, and R235's grid shows it matters at eta 0.10 vs 0.25 under a signed "
             "baseline, which E05 never used." % (move, spread))
    print("\n  " + v)
    json.dump({"fill_rate": filled / cells if cells else None, "zeros": zeros,
               "total_scores": total_scores, "verified_blind_arm": bool(verified),
               "readings": res, "move": move, "floor_spread": spread, "verdict": v},
              open(OUT / "missing_weights.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
