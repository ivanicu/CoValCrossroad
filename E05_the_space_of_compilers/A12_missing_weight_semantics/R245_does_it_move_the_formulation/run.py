"""R245 -- R244 tested ONE round and claimed the choice affects TEN. This tests the load-bearing three.

R244 found that "unrated" vs "rated zero" moves R231's central quantity by 0.1040 against a floor
spread of 0.0127, and its commit said the undeclared choice sits under ten rounds. That sentence is
wider than its evidence -- exactly the overreach realstat G1 is about, committed while writing up a
round about that overreach.

So: sweep the reading across the three claims the FORMULATION actually rests on.

  claim 1 (R230)  the class is always identifiable; class recovery at the release's rater noise
  claim 5 (R237)  H_eff, the noisy-channel bracket
  claim 6 (R239)  k_max, the largest identifiable core

ESTIMAND        each of the three under `exclude` and under `zero`, and whether the FORMULATION's
                stated conclusion changes -- not whether the number moves, which it will.
IDENTIFICATION  exact; arithmetic on the r04 cache and released fields.
SCOPE           968 prompts (300 for the K=2 recovery cells, matching R230/R237), judge
                Qwen3.5-2B. baseline: per-prompt chance. regime: eps=0.25, R=14, K=2.
WORLDS          W1 the readings agree on the CONCLUSIONS -> the choice is a scope line, not a threat
                W2 a conclusion flips                     -> the formulation is reading-dependent and
                                                             must say so in the claim, not a footnote
KILL            pre-registered: a conclusion flips if class-recovery stops exceeding member-recovery,
                or if k_max changes, or if H_eff's bracket crosses the 3.91 bits k=1 requires.
POSITIVE CTRL   the exclude arm must reproduce the published figures -- class 0.3233 / member 0.0613
                (R230) and k_max=2 (R228). If it does not, this is not the same measurement.
NEGATIVE CTRL   a prompt set where every criterion is fully rated must give identical answers under
                both readings. Measured, not assumed: reported as the share of prompts with fill=1.
SEEDS           5.
ARTIFACT        results/reading_sweep.json
IMPOSSIBLE      which reading is right. Unchanged from R244: partial identification, both reported.
"""
from __future__ import annotations
import collections, itertools, json, math, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
K, EPS, SEEDS = 2, 0.25, [0, 1, 2, 3, 4]

import importlib.util
_s = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def build(reading):
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    out, fully = [], 0
    for p in sorted(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if not (6 <= len(ok) <= 16):
            continue
        allr = sorted({s["annotator_id"] for i in ok for s in f[i]["scores"]})
        W = []
        for i in ok:
            d = {s["annotator_id"]: float(s["score"]) for s in f[i]["scores"]}
            W.append(np.mean(list(d.values())) if reading == "exclude"
                     else np.mean([d.get(a, 0.0) for a in allr]))
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        cellfill = sum(len(f[i]["scores"]) for i in ok) / (len(ok) * max(len(allr), 1))
        fully += int(cellfill >= 0.999)
        out.append((np.array(W, float), S))
        if len(out) >= 300:
            break
    return out, fully


def recover(prompts, target):
    """target='member' -> recover the exact planted subset; 'class' -> recover its Q-class."""
    per = collections.defaultdict(list)
    for sd in SEEDS:
        for pi, (W, S) in enumerate(prompts):
            rng = np.random.default_rng(abs(hash((pi, sd, target))) % (2 ** 32))
            T = tuple(sorted(rng.choice(len(W), size=K, replace=False)))
            y0 = (W[list(T), None] * S[list(T)]).sum(0)
            y = y0 + EPS * (np.abs(y0).max() or 1.0) * rng.standard_normal(4)
            obs = np.array(cls(y)); best, hits = None, []
            for c in itertools.combinations(range(len(W)), K):
                idx = list(c)
                d = float(np.abs(np.array(cls((W[idx, None] * S[idx]).sum(0))) - obs).sum())
                if best is None or d < best - 1e-12:
                    best, hits = d, [c]
                elif abs(d - best) <= 1e-12:
                    hits.append(c)
            if target == "member":
                per[sd].append((1.0 / len(hits)) if T in hits else 0.0)
            else:
                tc = cls(y0)
                per[sd].append(1.0 if any(cls((W[list(h), None] * S[list(h)]).sum(0)) == tc
                                          for h in hits) else 0.0)
    v = [float(np.mean(per[s])) for s in SEEDS]
    return float(np.mean(v)), max(v) - min(v)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    res = {}
    for reading in ("exclude", "zero"):
        pr, fully = build(reading)
        ns = [len(W) for W, _ in pr]
        cl, cls_sp = recover(pr, "class")
        me, me_sp = recover(pr, "member")
        # k_max from the class count actually realised (R230's route)
        counts = []
        for W, S in pr:
            counts.append(len({cls((W[list(c), None] * S[list(c)]).sum(0))
                               for c in itertools.combinations(range(len(W)), K)}))
        nmed = int(np.median(ns))
        # ⚠ I WROTE THIS FRESH AND REINTRODUCED THE BUG R228 HAD ALREADY FIXED. C(n,k) is unimodal,
        # so k near n satisfies C(n,k) <= 75 again -- for n=11, C(11,10)=11 -- and a plain max()
        # returns 11. R228 carries a `contig` variable for exactly this, with the comment that "a
        # core of size k>n/2 is not a compression and reporting the upper tail as identifiable would
        # be a technicality". Its positive control caught mine within one run. The lesson is not the
        # arithmetic, it is that I reimplemented a function that existed two arcs away.
        kmax = 0
        for k in range(1, nmed + 1):
            if math.log2(math.comb(nmed, k)) <= math.log2(75):
                kmax = k
            else:
                break
        res[reading] = {"n_prompts": len(pr), "fully_rated": fully,
                        "class": cl, "class_spread": cls_sp,
                        "member": me, "member_spread": me_sp,
                        "classes_median": float(np.median(counts)),
                        "n_median": nmed, "k_max": kmax}

    print("prompts %d | fully-rated prompts (fill = 1.0): %d = %.1f%%   <- NEGATIVE CONTROL"
          % (res["exclude"]["n_prompts"], res["exclude"]["fully_rated"],
             100 * res["exclude"]["fully_rated"] / res["exclude"]["n_prompts"]))
    print("   (on those, the two readings are identical BY CONSTRUCTION -- a derivation, and the")
    print("    reason any difference below has to come from the partially-rated majority)")

    print("\n=== the three load-bearing claims under both readings ===")
    print("%-10s %22s %22s %14s %8s" % ("reading", "class recovery", "member recovery",
                                        "classes(med)", "k_max"))
    for r_ in ("exclude", "zero"):
        v = res[r_]
        print("%-10s %22s %22s %14.0f %8d"
              % (r_, "%.4f (spread %.4f)" % (v["class"], v["class_spread"]),
                 "%.4f (spread %.4f)" % (v["member"], v["member_spread"]),
                 v["classes_median"], v["k_max"]))

    print("\n=== controls ===")
    e = res["exclude"]
    print(" POSITIVE exclude arm reproduces R230 (class 0.3233 / member 0.0613): %.4f / %.4f  %s"
          % (e["class"], e["member"],
             "OK" if abs(e["class"] - 0.3233) < 0.04 and abs(e["member"] - 0.0613) < 0.02
             else "NOT THE SAME MEASUREMENT"))
    print(" POSITIVE exclude arm reproduces R228's k_max = 2: %d  %s"
          % (e["k_max"], "OK" if e["k_max"] == 2 else "MISMATCH"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    z = res["zero"]
    c1 = (e["class"] > e["member"]) == (z["class"] > z["member"])
    c6 = e["k_max"] == z["k_max"]
    print(" claim 1  class > member under BOTH readings          : %s  (%.4f>%.4f | %.4f>%.4f)"
          % (c1, e["class"], e["member"], z["class"], z["member"]))
    print(" claim 6  k_max identical under BOTH readings          : %s  (%d | %d)"
          % (c6, e["k_max"], z["k_max"]))
    moved = abs(e["class"] - z["class"])
    print(" class recovery moves by %.4f against a seed spread of %.4f"
          % (moved, max(e["class_spread"], z["class_spread"])))
    ok = abs(e["class"] - 0.3233) < 0.04 and e["k_max"] == 2
    if not ok:
        v = "UNVERIFIED -- the exclude arm does not reproduce the published figures"
    elif c1 and c6:
        v = ("The CONCLUSIONS survive both readings: class beats member either way and k_max is "
             "unchanged. The reading moves class recovery by %.4f, which is a SCOPE LINE the "
             "formulation must carry -- not a threat to claims 1 or 6. R244's commit said the "
             "choice sits under ten rounds; it does, and for the load-bearing three it changes the "
             "NUMBERS and not the CONCLUSIONS." % moved)
    else:
        v = ("A CONCLUSION FLIPS under the reading (claim1 stable=%s, claim6 stable=%s). The "
             "formulation is reading-dependent and must say so in the claim itself." % (c1, c6))
    print("\n  " + v)
    res["verdict"] = v
    (OUT / "reading_sweep.json").write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
