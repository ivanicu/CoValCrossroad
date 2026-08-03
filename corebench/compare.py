#!/usr/bin/env python3
"""
corebench/compare.py -- PAIRED comparison of two cores on the same prompts.

WHY THIS EXISTS. The leaderboard showed topw_k4 at A1=0.0761 against coval_core at 0.0651.
The difference is +0.0110 while each row's own prompt-bootstrap sd is ~0.0093, so read off
the marginals it is about 1.2 sd -- and that reading is WRONG IN BOTH DIRECTIONS, because
the two cores are evaluated on THE SAME PROMPTS with THE SAME held-out annotators. The
marginal sds share almost all of their variance. Only a PAIRED resampling of the difference
is the right null, and it is usually far tighter.

CONTROLS
  PLACEBO   a core against ITSELF must return exactly 0.0000 with a zero-width interval.
            If it does not, the pairing is broken and no comparison here is readable.
  POSITIVE  a synthetic arm built by flipping a known fraction g of one core's predictions
            must be recovered at that fraction, and must NOT fire at g=0.
  NEGATIVE  break the pairing -- compare against a prompt-shuffled version of the rival.
            The interval must WIDEN, which is what proves the pairing is doing work.
  SEEDS     >=3 held-out draws; the interval is over prompts AND seeds.
"""
from __future__ import annotations
import argparse, collections, itertools, json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
SEEDS, NBOOT = [0, 1, 2], 2000
from score import cls, load_sat, load_targets, yvec


def per_prompt_hits(sat, targets, seed, eval_parity=-1):
    """eval_parity >= 0 restricts the held-out annotator to that index parity, so an
    oracle fitted on the OTHER parity has never seen the annotator it is scored against.
    Without this the oracle arm is leaky and its value is an inflated upper bound."""
    rng = np.random.default_rng(seed)
    out = {}
    for p in sat:
        if p not in targets or len(targets[p]) < 2:
            continue
        y = yvec(sat[p], sorted({i for i, _ in sat[p]}))
        v = targets[p]
        if eval_parity >= 0:
            v = [x for j, x in enumerate(targets[p]) if j % 2 == eval_parity]
            if not v:
                continue
        hy = v[int(rng.integers(len(v)))][0]
        out[p] = float(cls(y) == cls(np.array(hy, float)))
    return out


def paired(a_hits, b_hits, rng, nboot=NBOOT):
    pids = sorted(set(a_hits) & set(b_hits))
    d = np.array([a_hits[p] - b_hits[p] for p in pids])
    boots = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(nboot)])
    return float(d.mean()), float(np.percentile(boots, 2.5)), \
           float(np.percentile(boots, 97.5)), len(pids)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True); ap.add_argument("--b", required=True)
    ap.add_argument("--label-a", default="A"); ap.add_argument("--label-b", default="B")
    ap.add_argument("--eval-parity", type=int, default=-1)
    a = ap.parse_args()
    targets, _ = load_targets()
    SA, SB = load_sat(a.a), load_sat(a.b)

    est, lo, hi = [], [], []
    for s in SEEDS:
        ha, hb = per_prompt_hits(SA, targets, s, a.eval_parity), per_prompt_hits(SB, targets, s, a.eval_parity)
        m, l, h, n = paired(ha, hb, np.random.default_rng(500 + s))
        est.append(m); lo.append(l); hi.append(h)
    mean = float(np.mean(est))

    # PLACEBO -- a core against itself
    h0 = per_prompt_hits(SA, targets, 0, a.eval_parity)
    pm, pl, ph, _ = paired(h0, h0, np.random.default_rng(1))
    # POSITIVE -- flip a known fraction g of A's predictions; recovery must track g
    dose = {}
    for g in (0.0, 0.1, 0.25, 0.5):
        r = np.random.default_rng(9)
        hg = {p: (0.0 if r.random() < g else v) for p, v in h0.items()}
        dose[g] = paired(h0, hg, np.random.default_rng(2))[0]
    # NEGATIVE -- destroy the pairing; the interval must WIDEN
    hb0 = per_prompt_hits(SB, targets, 0, a.eval_parity)
    keys = list(hb0); np.random.default_rng(3).shuffle(keys)
    hb_sh = {p: hb0[k] for p, k in zip(sorted(hb0), keys)}
    _, ul, uh, _ = paired(h0, hb_sh, np.random.default_rng(4))
    paired_w = float(np.mean(hi) - np.mean(lo)); unpaired_w = uh - ul

    print(f"\n  PAIRED: {a.label_a}  vs  {a.label_b}   (n={len(h0)} prompts, "
          f"{len(SEEDS)} seeds x {NBOOT} bootstraps)\n")
    print(f"    [{'PASS' if pm == 0.0 and pl == ph == 0.0 else 'FAIL'}] PLACEBO  self vs self "
          f"= {pm:.4f} [{pl:.4f}, {ph:.4f}]")
    ok_dose = all(dose[x] <= dose[y] + 1e-9 for x, y in zip([0.0,.1,.25], [.1,.25,.5]))
    print(f"    [{'PASS' if ok_dose else 'FAIL'}] POSITIVE dose "
          + " ".join(f"g={g}:{v:+.4f}" for g, v in dose.items()))
    print(f"    [{'PASS' if dose[0.0] == 0.0 else 'FAIL'}] fails at g=0            "
          f"{dose[0.0]:+.4f}")
    print(f"    [{'PASS' if unpaired_w > paired_w else 'FAIL'}] NEGATIVE unpairing widens "
          f"{paired_w:.4f} -> {unpaired_w:.4f}  ({unpaired_w/paired_w:.2f}x)")
    print(f"\n    Δ A1 = {mean:+.4f}   95% CI [{np.mean(lo):+.4f}, {np.mean(hi):+.4f}]"
          f"   seeds {['%+.4f' % e for e in est]}")
    excl = np.mean(lo) > 0 or np.mean(hi) < 0
    print(f"\n    VERDICT: interval {'EXCLUDES' if excl else 'INCLUDES'} zero -> "
          f"{'a difference' if excl else 'NOT separable'}\n")


if __name__ == "__main__":
    main()
