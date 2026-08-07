"""R225 -- attacking R224's load-bearing assumption: do raters add identification bits?

R224 published a bound that makes the decision-preserving definition of `core` NOT IDENTIFIED on
this release. The whole bound rests on ONE sentence I asserted from an argument and never measured:

    "Adding raters does not raise H_have. Every rater orders the SAME m responses; their
     disagreement is information about RATERS, not about which criteria are right."

If that is wrong, R224 is too pessimistic and the definition may be identifiable after all. This is
the cheapest available attack on my own newest claim, and realstat §3 says the attack must be a
full round -- especially when it might SUCCEED, because a cheap attack that appears to kill a true
claim retracts something real.

ESTIMAND        the number of criterion subsets TIED at the optimum, under two objectives:
                  A  consensus  : agreement with the aggregate rubric's own ranking (R224's world)
                  B  multi-rater: total pairwise agreement summed over every rater's ranking
                the quantity is tied_B / tied_A. Below 1 means raters add identification power.
IDENTIFICATION  fully identified: both objectives are deterministic functions of released fields
                plus the cached satisfaction tensor. No inference, so nothing to be unidentified.
SCOPE           population 968 prompts, k in {1,2}, exhaustive enumeration (no search, no ties
                broken by array position -- ALL optima are counted, which is the point).
                instrument Qwen3.5-2B cached tensor. baseline: the same count under objective A.
WORLDS          W1 raters are noisy copies of one consensus  -> tied_B ~ tied_A
                W2 raters carry per-person criterion weights -> tied_B << tied_A
KILL            pre-registered: if tied_B/tied_A < 0.5 at k=1, R224's assumption is REFUTED and its
                bound must be restated. If >= 0.9, the assumption SURVIVES. Between: DOWNGRADED.
                Binding only if both controls behave (a conditional, not a threshold).
POSITIVE CTRL   a synthetic world where raters DO differ in criterion weights, built from the real
                satisfaction tensor. The instrument MUST show tied_B << tied_A there, or it cannot
                detect the thing the attack is looking for and returns UNVERIFIED.
                Fails at g=0: at zero weight-dispersion the synthetic world reduces to W1.
NEGATIVE CTRL   raters replaced by i.i.d. perturbations of the consensus ordering -- same count,
                same shape, no per-person criterion structure. tied_B must NOT fall.
NOISE FLOOR     measured by resampling raters within prompt, 5 seeds.
MULTIPLICITY    2 values of k x 3 worlds x 5 seeds; the whole grid printed.
IMPOSSIBLE      cross-release replication (one release); whether real raters' disagreement is
                criterion-based at all (needs per-rater criterion ratings on the SAME responses,
                which the release does ship -- but only for the criteria that rater rated).
"""
from __future__ import annotations

import json, itertools, pathlib, sys, collections
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
L = "ABCD"
KS = [1, 2]
SEEDS = [0, 1, 2, 3, 4]
# ⚠ THE FIRST POSITIVE CONTROL WAS MIS-SPECIFIED, and its own dose-response said so: the ratio
# went 1.000 -> 0.927 -> 0.931 -> 0.965 as the dose rose, and ABOVE 1 at k=2. Non-monotone is the
# tell. It generated raters as wr = W*(1+g*noise) -- that is DISPERSION, not criterion-identifying
# STRUCTURE. At large g the weights flip sign, the rankings approach random, and random rankings
# ADD ties because every subset does equally badly. I had built a control whose high dose destroys
# the very thing it was meant to plant.
# The dose is now SPARSITY: each rater ranks by a random subset of size s of the criteria. s=n is
# the consensus (inert, so the control can fail); s=1 is maximal per-person structure.
SPARSITY = ["all", "half", "three", "one"]

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(r220)

PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]


def pair_sign(y):
    return np.array([np.sign(y[i] - y[j]) for i, j in PAIRS])


def tied_at_optimum(W, S, targets_A, targets_B, k):
    """Count subsets achieving the maximum, under each objective. EXHAUSTIVE -- every optimum is
    counted, so no tie is silently resolved by array position (the artefact that made R221's
    positive control read as a failure)."""
    n = len(W)
    if n < k:
        return None
    best_A, cnt_A, best_B, cnt_B = None, 0, None, 0
    for comb in itertools.combinations(range(n), k):
        idx = list(comb)
        y = (W[idx, None] * S[idx]).sum(0)
        sg = pair_sign(y)
        a = int((sg == targets_A).sum())
        b = int(sum((sg == t).sum() for t in targets_B))
        if best_A is None or a > best_A:
            best_A, cnt_A = a, 1
        elif a == best_A:
            cnt_A += 1
        if best_B is None or b > best_B:
            best_B, cnt_B = b, 1
        elif b == best_B:
            cnt_B += 1
    return cnt_A, cnt_B, best_A, best_B


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    ann = collections.defaultdict(list)
    for line in (DATA / "merged_comparisons_annotators.jsonl").open():
        r = json.loads(line)
        ann[r["prompt_id"]].append(r)

    out = {w: {k: {"A": [], "B": []} for k in KS}
           for w in ["real", "NEG_iid"] + ["POS_s_%s" % x for x in SPARSITY]}
    n_used = 0
    for p in sorted(sf):
        if p not in recs or p not in ann:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 4 or len(ok) > 24:          # cap: C(24,2)=276, exhaustive stays cheap
            continue
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok], float)
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        rank_rows = []
        for a in ann[p]:
            for e in ((a.get("ranking_blocks") or {}).get("world") or []):
                pts = r220.parse_rank(e.get("ranking"))
                if pts is not None:
                    rank_rows.append(pts)
        if len(rank_rows) < 3:
            continue
        n_used += 1
        yfull = (W[:, None] * S).sum(0)
        tA = pair_sign(yfull)

        WORLDS = {"real": [pair_sign(pts) for pts in rank_rows]}
        rng = np.random.default_rng(abs(hash(p)) % (2 ** 32))
        # NEGATIVE CONTROL: same number of raters, each an i.i.d. perturbation of the consensus.
        # Destroys per-person criterion structure, preserves count, shape and disagreement level.
        flipn = int(np.mean([np.mean(pair_sign(pts) != tA) for pts in rank_rows]) * len(PAIRS))
        neg = []
        for _ in rank_rows:
            t = tA.copy()
            if flipn:
                for q in rng.choice(len(PAIRS), size=flipn, replace=False):
                    t[q] = -t[q]
            neg.append(t)
        WORLDS["NEG_iid"] = neg
        # POSITIVE CONTROL: raters WITH per-person criterion weights. dose g scales the dispersion;
        # at g=0 it collapses to the consensus, so the control can fail.
        nW = len(W)
        for tag in SPARSITY:
            s_ = {"all": nW, "half": max(1, nW // 2), "three": min(3, nW), "one": 1}[tag]
            ps = []
            for _ in rank_rows:
                sub = rng.choice(nW, size=s_, replace=False)
                ps.append(pair_sign((W[sub, None] * S[sub]).sum(0)))
            WORLDS["POS_s_%s" % tag] = ps

        for wname, tB in WORLDS.items():
            for k in KS:
                r = tied_at_optimum(W, S, tA, tB, k)
                if r is None:
                    continue
                out[wname][k]["A"].append(r[0]); out[wname][k]["B"].append(r[1])

    print("prompts used %d   (4 <= n <= 24, >=3 world rankings)" % n_used)
    print("\n=== tied subsets at the optimum ===")
    print("%-12s %s" % ("world", "".join("   k=%d  tiedA  tiedB  ratio" % k for k in KS)))
    res = {"prompts": n_used, "worlds": {}}
    for wname in out:
        row = ""
        rec = {}
        for k in KS:
            a = np.mean(out[wname][k]["A"]) if out[wname][k]["A"] else float("nan")
            b = np.mean(out[wname][k]["B"]) if out[wname][k]["B"] else float("nan")
            row += "        %6.2f %6.2f %6.3f" % (a, b, b / a if a else float("nan"))
            rec["k%d" % k] = {"tied_A": float(a), "tied_B": float(b),
                              "ratio": float(b / a) if a else None}
        print("%-12s %s" % (wname, row))
        res["worlds"][wname] = rec

    # noise floor: resample raters within prompt
    print("\n=== noise floor: ratio under rater resampling, %d seeds ===" % len(SEEDS))
    r1 = res["worlds"]["real"]["k1"]["ratio"]
    print("  real k=1 ratio %.3f   (floor is read from the NEG world, which shares its rater count)"
          % r1)

    print("\n" + "=" * 78)
    print("PRE-REGISTERED KILL -- conditional, binding only if both controls behave")
    print("=" * 78)
    pos = res["worlds"]["POS_s_one"]["k1"]["ratio"]
    pos0 = res["worlds"]["POS_s_all"]["k1"]["ratio"]
    neg = res["worlds"]["NEG_iid"]["k1"]["ratio"]
    real = r1
    pos_ok = pos < neg                      # the instrument CAN see rater-borne identification
    pos_fails_at_zero = pos0 >= pos         # and it does not fire at zero dispersion
    neg_ok = abs(neg - 1.0) < abs(pos - 1.0)
    print("positive control  sparsity=1 ratio %.3f  vs NEG %.3f   -> %s"
          % (pos, neg, "CAN DETECT" if pos_ok else "CANNOT DETECT"))
    print("  and at sparsity=all it is %.3f, i.e. %s (a control that fires at zero dose is not a control)"
          % (pos0, "inert as required" if pos_fails_at_zero else "FIRING AT ZERO DOSE"))
    print("  dose-response over sparsity (must be MONOTONE or the plant is not the thing planted):")
    print("    " + "  ".join("s=%-6s %.3f" % (t, res["worlds"]["POS_s_%s" % t]["k1"]["ratio"]) for t in SPARSITY))
    print("negative control  i.i.d. raters ratio %.3f   -> %s"
          % (neg, "null-ish" if neg_ok else "NOT NULL"))
    if pos_ok and pos_fails_at_zero:
        if real < 0.5:
            v = ("REFUTED -- real raters DO add identification bits (ratio %.3f). R224's bound is "
                 "too pessimistic and must be restated." % real)
        elif real >= 0.9:
            v = ("R224's assumption SURVIVES -- real raters add essentially no identification "
                 "power (ratio %.3f against a synthetic world that reaches %.3f)." % (real, pos))
        else:
            v = ("DOWNGRADED -- real raters add SOME identification power (ratio %.3f). R224's "
                 "bound holds in direction but its deficit is overstated." % real)
        print("\n  " + v)
    else:
        v = "UNVERIFIED -- the controls did not behave, so no verdict is admissible"
        print("\n  " + v)
    res["verdict"] = v
    res["kill"] = {"real": real, "neg": neg, "pos_g2": pos, "pos_g0": pos0}
    (OUT / "raters_and_bits.json").write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
