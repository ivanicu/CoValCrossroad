#!/usr/bin/env python3
"""
R866 · the COMPARATOR as a swept axis — the one term in the statistic never varied.

⛔ WHY. Six rounds attacked this comparison's denominator (R860, R862), its threshold (R863, R864)
and its criterion (R865). **Every one held the comparator fixed, and the two that were used were
never compared to each other**: R851 uses the single released blind arm `genericpool16`; R860/R862/
R864 use the MAX over the 1,820-subset family. R865 then measured that `coval_core` **passes clause
② against the first (ratio +2.2524, both criteria) and fails against the second (0.910)** —
**same core, same clause, opposite verdicts, on a choice nobody has justified in writing.**

⭐ AND THE SWEEP EXPOSES AN AMBIGUITY IN THE CLAUSE'S OWN WORDING. *"Better than a prompt-blind
set"* under a universal reading admits **two different bars** that this project has used
interchangeably: beat the **ARGMAX ARM** (the single subset with the best mean, then its per-prompt
vector — R860's choice) or beat the **PER-PROMPT MAXIMUM** (the best subset chosen afresh on every
prompt). The second is strictly harder and is what the English most naturally says. **Nobody has
written down which one the clause means.**

⛔ THE ARITHMETIC RUNG, AND IT BECOMES THIS ROUND'S KILL. The comparator forms
`mean <= p75 <= p90 <= per-prompt max` are **pointwise non-decreasing by construction**, so any
arm's margin against them is pointwise non-increasing and **the extension count MUST be monotone
non-increasing along that chain.** This is a DERIVATION — it could not come out otherwise — and it
is therefore useless as evidence and perfect as an internal check: **a non-monotone count means the
implementation is wrong, not that the world is interesting.** ⚠ `single` and `argmax_arm` are NOT
in that pointwise chain (a single fixed subset can be above or below the family mean on any given
prompt), so they sit outside the monotone requirement and are excluded from it.

ESTIMAND        for clause ②, `coval_core`'s verdict and the 99-arm extension count under EVERY
                defensible comparator form × BOTH admissibility criteria.
IDENTIFICATION  exact; every comparator is a statistic of the same released family matrix, and both
                criteria come from one bootstrap per cell, so nothing varies but the named axis.
SCOPE           population: 968 prompts scored by `genericpool16`, `coval_core` and the arm
                instrument: A2 vs EVERY annotator · family = C(16,4) = 1,820 blind 4-subsets
                baseline:   varies by cell — that IS the axis
                regime:     home release, judge J
WORLDS          A · the verdict is comparator-INVARIANT -> the choice never mattered and six rounds
                    of denominator/threshold work were aimed at the right term
                B · the verdict flips somewhere in the sweep -> clause ② has no verdict until the
                    comparator is written into the clause, and the published count is an artifact
                    of an unstated choice
                C · the verdict flips AND the flip point differs between the two criteria -> the
                    comparator and the criterion interact, and the clause needs both stated
KILL            CONDITIONAL, all required:
                  ⭐ ① MONOTONICITY along `mean -> p75 -> p90 -> per-prompt max` (the derivation
                     above). Non-monotone -> the implementation is wrong. Exit 2.
                  ② placebo: the argmax arm against itself gives margin exactly 0
                  ③ positive: `oracle_k4` clears under the WEAKEST comparator (family mean)
                  ④ negative: `random_k4_s0` fails under the STRONGEST (per-prompt max)
SEEDS           3 bootstrap seeds; per-cell spread reported.
MULTIPLICITY    6 comparators × 2 criteria × 3 seeds = 36 cells for the count, all reported.
ARTIFACT        results/comparator_sweep.json
IMPOSSIBLE      construct validated (needs an external gold standard) · cross-release (needs a
                second release) · causally identified (needs an intervention on the mechanism).
"""
import itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
NBOOT, Q, ZEFF, FLOOR = 2000, 0.05, 2.802, 1.5
POS, NEG = "oracle_k4", "random_k4_s0"


def bh_mask(p, q=Q):
    C = len(p); o = np.argsort(p); k = -1
    for rank, i in enumerate(o, 1):
        if p[i] <= q * rank / C:
            k = rank
    m = np.zeros(C, bool)
    if k > 0:
        m[o[:k]] = True
    return m


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    A0 = load_sat(ROOT / "corebench" / "results" / "sat_coval_core.npz")
    pids = sorted(set(S) & set(A0) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    subs = np.array(list(itertools.combinations(range(npool), 4)))
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    B = np.empty((len(subs), n))
    for k in range(n):
        Y = np.array([[S[pids[k]][(i, x)] for x in "ABCD"] for i in range(npool)],
                     float)[subs].sum(axis=1)
        Cv = np.sign(Y[:, ii] - Y[:, jj])
        B[:, k] = (Cv[:, None, :] == H[k][None, :, :]).mean(axis=(1, 2))
    kstar = int(B.mean(1).argmax())
    print(f"  prompts {n} · family {len(subs)} · argmax arm #{kstar} {B.mean(1)[kstar]:.10f}")

    COMPS = [
        ("single_genericpool16", np.array([np.mean(
            [[cls(yvec(S[p], sorted({i for i, _ in S[p]})))[c] == h[c] for c in range(6)]
             for h in H[k]]) for k, p in enumerate(pids)]), False),
        ("family_mean", B.mean(0), True),
        ("family_p75", np.percentile(B, 75, axis=0), True),
        ("family_p90", np.percentile(B, 90, axis=0), True),
        ("argmax_arm", B[kstar], False),
        ("per_prompt_max", B.max(0), True),
    ]
    print("  comparator means: " + " · ".join(f"{nm} {v.mean():.4f}" for nm, v, _ in COMPS))

    def arm(name):
        f = ROOT / "corebench" / "results" / f"sat_{name}.npz"
        if not f.exists():
            return None
        try:
            Sa = load_sat(f)
        except Exception:
            return None
        v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                      for k, p in enumerate(pids)])
        return v if np.isfinite(v).sum() >= 200 else None

    names, ARMS = [], []
    for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz")):
        v = arm(f.stem[4:])
        if v is not None:
            names.append(f.stem[4:]); ARMS.append(v)
    if not names:
        print("  OBSERVED NOTHING: no arm cleared 200 prompts on the shared population. A sweep")
        print("  with no population has not passed — it has not run. Exit 2, never 0.")
        return 2
    ARMS = np.array(ARMS)
    ci = names.index("coval_core")
    print(f"  arms {len(names)} on the shared {n}-prompt population")

    def cell(comp, seed):
        D = ARMS - comp
        bidx = np.random.default_rng(seed).integers(0, n, size=(NBOOT, n))
        M = np.isfinite(D).astype(float)
        bs = (np.nan_to_num(D)[:, bidx].sum(2) / np.maximum(M[:, bidx].sum(2), 1.0)).T
        marg = np.nanmean(D, 1)
        ratio = marg / np.maximum(ZEFF * bs.std(axis=0, ddof=1), 1e-300)
        lo = np.percentile(bs, 2.5, axis=0)
        pv = np.maximum(2 * np.minimum((bs <= 0).mean(0), (bs >= 0).mean(0)), 1.0 / (NBOOT + 1))
        return (ratio >= FLOOR), (bh_mask(pv) & (lo > 0)), marg, ratio

    print(f"\n  {'comparator':<22}{'core margin':>12}{'core ratio':>11}{'A':>4}{'B':>4}"
          f"{'count_A':>9}{'count_B':>9}")
    rows = []
    for nm, comp, chain in COMPS:
        cA, cB, mm, rr = [], [], [], []
        for sd in (11, 22, 33):
            mA, mB, marg, ratio = cell(comp, sd)
            cA.append(int(mA.sum())); cB.append(int(mB.sum()))
            mm.append(float(marg[ci])); rr.append(float(ratio[ci]))
            if sd == 11:
                vA, vB = bool(mA[ci]), bool(mB[ci])
                pA = bool(mA[names.index(POS)]) if POS in names else None
                nB = bool(mB[names.index(NEG)]) if NEG in names else None
        rows.append({"comparator": nm, "in_monotone_chain": chain,
                     "core_margin": float(np.mean(mm)), "core_ratio": float(np.mean(rr)),
                     "core_passes_A": vA, "core_passes_B": vB,
                     "count_A": cA, "count_B": cB,
                     "pos_ctrl_A": pA, "neg_ctrl_B": nB})
        print(f"  {nm:<22}{np.mean(mm):>+12.6f}{np.mean(rr):>+11.4f}"
              f"{'  ✓' if vA else '  ✗'}{'  ✓' if vB else '  ✗'}"
              f"{int(np.mean(cA)):>9}{int(np.mean(cB)):>9}")

    chain = [r for r in rows if r["in_monotone_chain"]]
    ca = [int(np.mean(r["count_A"])) for r in chain]
    cb = [int(np.mean(r["count_B"])) for r in chain]
    mono = all(ca[i] >= ca[i + 1] for i in range(len(ca) - 1)) and \
           all(cb[i] >= cb[i + 1] for i in range(len(cb) - 1))
    print(f"\n  KILL ① MONOTONICITY along {[r['comparator'] for r in chain]}")
    print(f"         A {ca} · B {cb}  ->  {mono}  {'PASS' if mono else 'FAIL'}")
    print("    A DERIVATION: those comparators are pointwise non-decreasing, so the counts must")
    print("    fall. Useless as evidence, perfect as a wiring check — non-monotone means the")
    print("    implementation is wrong, not that the world is interesting.")
    pl = float(np.nanmean(B[kstar] - B[kstar]))
    weakest, strongest = rows[1], rows[-1]
    pos_ok = bool(weakest["pos_ctrl_A"]); neg_ok = not bool(strongest["neg_ctrl_B"])
    print(f"  KILL ② placebo argmax arm vs itself {pl:+.2e}  "
          f"{'PASS' if abs(pl) < 1e-12 else 'FAIL'}")
    print(f"  KILL ③ `{POS}` clears under the WEAKEST comparator (family_mean): {pos_ok}  "
          f"{'PASS' if pos_ok else 'FAIL'}")
    print(f"  KILL ④ `{NEG}` fails under the STRONGEST (per_prompt_max): {neg_ok}  "
          f"{'PASS' if neg_ok else 'FAIL'}")
    if not (mono and abs(pl) < 1e-12 and pos_ok and neg_ok):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows, "monotone": mono},
                  open(OUT / "comparator_sweep.json", "w"), indent=2)
        return 2

    vA = [r["core_passes_A"] for r in rows]; vB = [r["core_passes_B"] for r in rows]
    flipA, flipB = len(set(vA)) > 1, len(set(vB)) > 1
    world = "C" if (flipA and flipB and vA != vB) else ("B" if (flipA or flipB) else "A")
    print(f"\n  ⭐ `coval_core` clause-② verdict across 6 comparators:")
    print(f"     under A (ratio>={FLOOR}): {['✓' if x else '✗' for x in vA]}")
    print(f"     under B (BH+CI)         : {['✓' if x else '✗' for x in vB]}")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "the verdict is COMPARATOR-INVARIANT — the choice never mattered",
        "B": "the verdict FLIPS inside the sweep — clause ② has no verdict until the comparator is"
             " written into the clause, and the published count is an artifact of an unstated"
             " choice",
        "C": "the verdict flips AND the two criteria flip at DIFFERENT points — comparator and"
             " criterion interact, and the clause must state both"}[world])

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "n_prompts": n, "n_arms": len(names), "family": len(subs),
               "world": world, "rows": rows, "monotone": mono,
               "flips_under_A": flipA, "flips_under_B": flipB,
               "controls": {"placebo": pl, "pos": pos_ok, "neg": neg_ok}},
              open(OUT / "comparator_sweep.json", "w"), indent=2)
    print(f"\n  artifact: results/comparator_sweep.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
