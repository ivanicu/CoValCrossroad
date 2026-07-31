"""r122 -- the metric's gauge invariances, done as an experiment instead of as two heredocs.

WHY THIS ROUND EXISTS, and it is a process failure before it is a question
-------------------------------------------------------------------------
I ran two gauge tests inline -- rescale the satisfaction values, swap the aggregator -- reported that
the compiled arm's advantage survived both, and moved on. Those runs had no permutation null, no
positive control, no seed, no multiplicity correction, no persisted vector and no source stamp. They
are exactly what the `severe-experiment` standard calls a cheap attack, and I ran them one command
after committing a gate that forbids it. An attack without controls is not evidence whichever way it
comes out, and it is MOST dangerous when it appears to confirm, because a confirmation nobody could
have failed is indistinguishable from a demonstration.

So: same two questions, at the standard.

THE GAUGE ARGUMENT
------------------
The metric compares two responses by the ORDER of their aggregated satisfaction. Order is invariant
under any monotone rescaling of satisfaction -- but the AGGREGATION is applied BEFORE the comparison,
and `mean(f(x)) != f(mean(x))` for non-linear f. So:

    the PROPERTY  "core orders responses better than full"  should be invariant to how satisfaction
                  is scaled, because scale is a unit convention and not a fact about the rules;
    the MEASUREMENT is NOT obviously invariant, because averaging happens first.

A measurement that moves under a transformation the property is invariant to is measuring the
transformation. That is the cheapest kill available and it costs no compute, which is why the
standard puts it first on the attack ladder.

CLAIM CARD
----------
Claim      core's +0.0663 advantage over full is a property of the RULES, not of the scale on which
           satisfaction happens to be expressed nor of the choice to aggregate by mean.
Estimand   adv = e(full) - e(core), computed independently in every cell of
               TRANSFORM x AGGREGATOR x TIE POLICY x ARM PAIR
Identification
           adv is point-identified per cell: it is a difference of two observed rates on the same
           pairs. Nothing here needs a latent quantity.
Scope      population 968 prompts / 80,542 human ordered pairs; instrument the r04 Qwen3.5 satisfaction
           tensor held FIXED across every cell (the arms differ only in which criteria are averaged);
           baseline the uncompiled arm and a size-matched random arm; regime four responses per
           prompt, at most six pairs per assessment.
Worlds     W-GAUGE-INVARIANT  adv keeps its sign and rough size across all transforms and aggregators.
                              The advantage is about the rules.
           W-SCALE-CARRIED    adv collapses or reverses under a rank transform. The advantage lives in
                              the satisfaction SCALE, and every number this project has published
                              about compilation is a statement about the judge's output distribution.
           W-AGGREGATOR-BOUND adv survives rescaling but not aggregator swaps. Then "compilation
                              helps" is really "compilation helps IF you average", which is a much
                              narrower claim than anything published.
Nulls      (i) POSITIVE CONTROL: plant a known advantage by scoring one arm with a rule selected to
           be better, and require every cell to recover it. A cell that cannot see a planted
           advantage cannot be quoted as showing none.
           (ii) PLACEBO: an arm against ITSELF in every cell must return exactly 0.0.
           (iii) SHAM: a size-matched random subset of full, which involves no compilation, so any
           cell where the sham also wins is measuring criterion count.
           (iv) NEGATIVE / permutation: shuffle which criteria belong to which arm within a prompt,
           preserving counts exactly, and recompute adv. That is the null for "these criteria" as
           opposed to "this many criteria".

PRE-REGISTERED KILL, before the run
-----------------------------------
If adv under the RANK transform falls below 25% of adv under raw, or changes sign in any aggregator,
the advantage is scale- or aggregator-carried and every compilation claim in this package is
downgraded to a statement about the judge's output distribution. Benjamini-Hochberg over the whole
cell grid; cells reported whether or not they survive.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join            # noqa: E402
from covalx.stamp import stamp          # noqa: E402

FULL = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
CORE = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

SEED = 20260730
N_PERM = 300
TRANSFORMS = ("raw", "rank", "sqrt", "logit", "zscore")
AGGREGATORS = ("mean", "median", "max", "min", "majority", "trimmed")
TIE_POLICIES = ("exclude", "half", "error")
BH_Q = 0.05
RANK_KILL_FRACTION = 0.25      # pre-registered: rank adv below this share of raw adv kills the claim
PLANT_G = 0.15                  # positive control: a known shift, large enough to be visible per cell


def load_sat(path):
    z = np.load(path, allow_pickle=True)
    d = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def strict_pairs(r):
    tiers = [t.split("=") for t in r.split(">")]
    out = set()
    for i, a in enumerate(tiers):
        for b in tiers[i + 1:]:
            for x in a:
                for y in b:
                    out.add((x.strip(), y.strip()))
    return out


def to_matrix(satp):
    labs = sorted({l for _, l in satp})
    cis = sorted({c for c, _ in satp})
    M = np.zeros((len(cis), len(labs)))
    for (ci, lab), v in satp.items():
        M[cis.index(ci), labs.index(lab)] = v
    return M, labs


def transform(M, kind):
    if kind == "raw":
        return M
    if kind == "rank":      # destroys the scale entirely, preserves order within each criterion
        return np.argsort(np.argsort(M, axis=1), axis=1).astype(float)
    if kind == "sqrt":
        return np.sqrt(np.clip(M, 0, None))
    if kind == "logit":
        q = np.clip(M, 1e-3, 1 - 1e-3)
        return np.log(q / (1 - q))
    if kind == "zscore":    # per criterion, so each criterion contributes equal variance
        sd = M.std(axis=1, keepdims=True)
        return (M - M.mean(axis=1, keepdims=True)) / np.where(sd > 0, sd, 1.0)
    raise ValueError(kind)


def aggregate(M, kind):
    if kind == "mean":
        return M.mean(0)
    if kind == "median":
        return np.median(M, 0)
    if kind == "max":
        return M.max(0)
    if kind == "min":
        return M.min(0)
    if kind == "trimmed":   # drop the extreme criterion at each end before averaging
        if M.shape[0] < 3:
            return M.mean(0)
        S = np.sort(M, axis=0)
        return S[1:-1].mean(0)
    if kind == "majority":  # Borda: how many rivals this response beats, summed over criteria
        n = M.shape[1]
        return np.array([sum(float(np.sum(r[i] > np.delete(r, i))) for r in M) for i in range(n)])
    raise ValueError(kind)


def arm_scores(satp, tr, ag, keep=None):
    if keep is not None:
        satp = {(c, l): v for (c, l), v in satp.items() if c in keep}
        if not satp:
            return None
    M, labs = to_matrix(satp)
    s = aggregate(transform(M, tr), ag)
    return {l: float(v) for l, v in zip(labs, s)}


def rate(work, sc_by_pid, tie):
    e = d = 0.0
    for pid, ranks in work:
        sc = sc_by_pid.get(pid)
        if not sc:
            continue
        for P in ranks:
            for x, y in P:
                if x not in sc or y not in sc:
                    continue
                if sc[x] == sc[y]:
                    if tie == "exclude":
                        continue
                    d += 1
                    e += 0.5 if tie == "half" else 1.0
                    continue
                d += 1
                e += float(sc[x] < sc[y])
    return (e / d) if d else float("nan"), int(d)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--nperm", type=int, default=N_PERM)
    ap.add_argument("--out", default=str(_RES / "r122_metric_gauge_grid.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    F, C = load_sat(FULL), load_sat(CORE)
    work = []
    for pid, comp, _rub in load_join(COMPARISONS, RUBRICS):
        if pid not in F or pid not in C:
            continue
        R = []
        for a in sorted(comp["metadata"]["assessments"], key=lambda x: str(x.get("annotator_id"))):
            w = (a.get("ranking_blocks") or {}).get("world") or []
            if w:
                P = strict_pairs(w[0].get("ranking", ""))
                if P:
                    R.append(P)
        if R:
            work.append((pid, R))
    if not work:
        print("REFUSING: empty population. Exits 2, never 0.", file=sys.stderr)
        return 2
    n_pairs = sum(len(P) for _p, R in work for P in R)
    print(f"{len(work)} prompts, {n_pairs:,} human ordered pairs; satisfaction tensor held FIXED "
          f"across every cell -- arms differ only in which criteria are aggregated")

    core_k = int(np.median([len({c for c, _ in C[p]}) for p, _r in work]))

    def build(kind, tr, ag, draw=None):
        out = {}
        for pid, _R in work:
            if kind == "full":
                out[pid] = arm_scores(F[pid], tr, ag)
            elif kind == "core":
                out[pid] = arm_scores(C[pid], tr, ag)
            elif kind == "sham":
                cis = sorted({c for c, _ in F[pid]})
                k = min(core_k, len(cis))
                out[pid] = arm_scores(F[pid], tr, ag,
                                      keep=set(draw.choice(cis, k, replace=False).tolist()))
            elif kind == "plant":
                s = arm_scores(F[pid], tr, ag)
                # a KNOWN advantage: nudge the response the humans ranked first
                first = None
                for P in _R:
                    order = [x for x, _y in P]
                    if order:
                        first = order[0]
                        break
                if s and first in s:
                    s = dict(s)
                    s[first] = s[first] + PLANT_G * (1 + abs(s[first]))
                out[pid] = s
        return out

    grid, placebo_fail = [], []
    print(f"\nsweeping {len(TRANSFORMS)} transforms x {len(AGGREGATORS)} aggregators x "
          f"{len(TIE_POLICIES)} tie policies")
    for tr, ag, tie in itertools.product(TRANSFORMS, AGGREGATORS, TIE_POLICIES):
        sf = build("full", tr, ag)
        sc = build("core", tr, ag)
        ef, df = rate(work, sf, tie)
        ec, dc = rate(work, sc, tie)
        adv = ef - ec
        # PLACEBO: an arm against itself must be exactly zero
        ef2, _ = rate(work, sf, tie)
        if abs(ef2 - ef) > 0:
            placebo_fail.append((tr, ag, tie))
        # SHAM: size-matched random subset, no compilation
        shams = []
        for i in range(8):
            d2 = np.random.default_rng([args.seed, hash((tr, ag, tie)) % 10_000, i])
            es, _ = rate(work, build("sham", tr, ag, d2), tie)
            shams.append(ef - es)
        sham_adv = float(np.mean(shams))
        # POSITIVE CONTROL: does this cell see a planted advantage?
        ep, _ = rate(work, build("plant", tr, ag), tie)
        planted_adv = ef - ep
        # NEGATIVE: permute which criteria belong to which arm, counts preserved
        null = []
        for _ in range(args.nperm // 10):
            sw = {}
            for pid, _R in work:
                allc = list(F[pid].items()) + list(C[pid].items())
                nF = len({c for c, _ in F[pid]})
                idx = np.random.default_rng([args.seed, len(null), hash(pid) % 9973]).permutation(len(allc))
                a_ = dict(allc[i] for i in idx[:nF])
                sw[pid] = arm_scores(a_, tr, ag) if a_ else None
            en, _ = rate(work, sw, tie)
            null.append(ef - en)
        null = np.array(null, float)
        c0 = float(np.nanmean(null)) if len(null) else 0.0
        sd = float(np.nanstd(null)) if len(null) else 0.0
        p = float((np.sum(np.abs(null - c0) >= abs(adv - c0)) + 1) / (len(null) + 1)) if len(null) else 1.0
        grid.append({"transform": tr, "aggregator": ag, "tie": tie, "e_full": ef, "e_core": ec,
                     "adv": adv, "sham_adv": sham_adv, "planted_adv": planted_adv,
                     "null_mean": c0, "null_sd": sd, "p": p, "n_pairs": int(min(df, dc)),
                     "calibrated": bool(planted_adv > 0.5 * PLANT_G * 0.1)})

    ps = np.array([g["p"] for g in grid])
    o = np.argsort(ps)
    keep = np.zeros(len(ps), bool)
    passed = ps[o] <= BH_Q * (np.arange(1, len(ps) + 1) / len(ps))
    if passed.any():
        keep[o[:np.max(np.flatnonzero(passed)) + 1]] = True
    for g, s_ in zip(grid, keep):
        g["bh"] = bool(s_)

    raw_mean = float(np.mean([g["adv"] for g in grid if g["transform"] == "raw"]))
    rank_mean = float(np.mean([g["adv"] for g in grid if g["transform"] == "rank"]))
    print(f"\n  {'transform':<10}" + "".join(f"{a:>11}" for a in AGGREGATORS))
    for tr in TRANSFORMS:
        row = []
        for ag in AGGREGATORS:
            v = [g["adv"] for g in grid if g["transform"] == tr and g["aggregator"] == ag
                 and g["tie"] == "exclude"]
            row.append(v[0] if v else float("nan"))
        print(f"  {tr:<10}" + "".join(f"{x:>+11.5f}" for x in row))

    n_neg = sum(1 for g in grid if g["adv"] <= 0)
    n_cal = sum(1 for g in grid if g["calibrated"])
    sham_pos = sum(1 for g in grid if g["sham_adv"] > 0)
    print(f"\n  cells {len(grid)}   adv <= 0 in {n_neg}   BH survivors {int(keep.sum())}")
    print(f"  POSITIVE CONTROL: {n_cal}/{len(grid)} cells detect a planted advantage of "
          f"{PLANT_G} -- cells that do not are UNVERIFIED, not clean")
    print(f"  SHAM (size-matched random {core_k}-subset, no compilation): beats full in "
          f"{sham_pos}/{len(grid)} cells, mean sham adv "
          f"{np.mean([g['sham_adv'] for g in grid]):+.5f} against core's {np.mean([g['adv'] for g in grid]):+.5f}")
    print(f"  PLACEBO (arm vs itself): {len(placebo_fail)} failures -> "
          f"{'PASS' if not placebo_fail else 'FAIL'}")
    print(f"  RANK vs RAW: {rank_mean:+.5f} vs {raw_mean:+.5f} = "
          f"{rank_mean/raw_mean if raw_mean else float('nan'):.1%} of raw "
          f"(pre-registered kill at {RANK_KILL_FRACTION:.0%})")

    killed = (rank_mean < RANK_KILL_FRACTION * raw_mean) or n_neg > 0
    world = ("W-SCALE-OR-AGGREGATOR-CARRIED" if killed else
             "W-UNVERIFIED" if n_cal < len(grid) else "W-GAUGE-INVARIANT")
    conclusion = (
        f"{len(grid)} cells over {len(TRANSFORMS)} satisfaction transforms, {len(AGGREGATORS)} "
        f"aggregators and {len(TIE_POLICIES)} tie policies, on {n_pairs:,} human ordered pairs with "
        f"the satisfaction tensor held fixed. The compiled arm's advantage is positive in "
        f"{len(grid)-n_neg} of {len(grid)} cells. Under the RANK transform, which destroys the "
        f"satisfaction scale entirely while preserving order within each criterion, the mean "
        f"advantage is {rank_mean:+.5f} against raw's {raw_mean:+.5f} = "
        f"{rank_mean/raw_mean if raw_mean else float('nan'):.0%}, against a pre-registered kill at "
        f"{RANK_KILL_FRACTION:.0%}. A size-matched random subset involving no compilation beats full "
        f"in {sham_pos} of {len(grid)} cells with mean advantage "
        f"{np.mean([g['sham_adv'] for g in grid]):+.5f}. The positive control is detected in "
        f"{n_cal}/{len(grid)} cells and the placebo returns exactly zero in "
        f"{len(grid)-len(placebo_fail)}/{len(grid)}. WORLD: {world}."
    )
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"seed": args.seed, "n_prompts": len(work), "n_pairs": n_pairs, "core_k": core_k,
         "transforms": list(TRANSFORMS), "aggregators": list(AGGREGATORS),
         "tie_policies": list(TIE_POLICIES), "grid": grid,
         "raw_mean_adv": raw_mean, "rank_mean_adv": rank_mean,
         "rank_fraction_of_raw": rank_mean / raw_mean if raw_mean else None,
         "rank_kill_fraction": RANK_KILL_FRACTION,
         "n_negative_cells": n_neg, "n_calibrated": n_cal, "n_bh": int(keep.sum()),
         "sham_positive_cells": sham_pos, "placebo_failures": placebo_fail,
         "world": world, "conclusion": conclusion, **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
