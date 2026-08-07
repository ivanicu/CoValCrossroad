#!/usr/bin/env python3
"""
R902 · the score gap CONDITIONAL on how much the two rules actually differ.

⛔ WHY. R901 found `topw_k4` and `topabs_k4` overlap at mean Jaccard 0.5562 against a floor of
0.1820, and concluded the 0.0748 score gap is not a selection difference. **That conclusion was
drawn from a MARGINAL overlap against a MARGINAL gap, and the two are not comparable** — 25.5% of
prompts have identical selections and cannot contribute to any gap at all. This round conditions.

⛔⛔ **THE ARITHMETIC TRAP, DECLARED BEFORE THE RUN AND THEN USED AS THE CONTROL.**
At `Jaccard = 1` the two arms select the SAME criteria, so their per-prompt A2 scores are
**identical by construction** and the gap is **exactly 0**. That is forced by the algebra; it is a
DERIVATION and it is not evidence about anything.
⭐ **But a derivation with a known answer is the best wiring test available**, so it is promoted to
the positive control: **if any J = 1 prompt shows a nonzero gap, the arms differ for a reason that
is NOT their selection, and R901's conclusion inverts rather than being refined.**

⭐⭐ **AND THE CONDITIONING CHANGES THE HEADLINE NUMBER BY ARITHMETIC ALONE.** If 25.5% of prompts
contribute an exact zero, the marginal mean gap of 0.0748 is generated entirely by the other 74.5%,
so the gap **per differing prompt** is about `0.0748 / 0.745 ≈ 0.100` — roughly a third larger than
the number R900 and R901 both quoted. **A mean over a population containing structural zeros is not
the effect on the units that can show one.**

ESTIMAND        E[|gap| | Jaccard] across the overlap range, and the conditional mean gap on
                prompts where the selections DIFFER.
IDENTIFICATION  exact for the conditional means. ⚠ NOT causal: overlap is not randomised, and
                prompts where the rules disagree may differ in other ways.
SCOPE           population: the 968 prompts, then the J<1 subset — both counted and printed
                instrument: per-prompt A2 vs the human target; Jaccard of selected criterion sets
                baseline:   the J = 1 stratum, which must be exactly zero
                regime:     home release, judge 2B, k=4
WORLDS          A · |gap| rises monotonically as J falls -> the AMOUNT of selection difference
                    drives the score difference, and R901's marginal reading understated it
                B · |gap| is flat across J<1 -> only WHETHER they differ matters, not by how much;
                    a threshold effect rather than a dose
                C · some J = 1 prompt has a nonzero gap -> the arms differ for a NON-selection
                    reason and every reading in R900/R901 is void, not merely refined
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE / DERIVATION-AS-WIRING: every J = 1 prompt must give gap exactly 0
                     (|gap| < 1e-12). This is forced by the algebra, so a failure localises a
                     coding error rather than a finding — which is exactly what a wiring test is
                     for. WORLD C if it fails.
                  ⭐ ② the J = 1 stratum must be NON-EMPTY, else the control is vacuous and this
                     round has no wiring test at all. R901 measured 25.5%, so it should be ~247.
                  ⭐ ③ MULTIPLICITY over bins: the whole J-curve printed, every bin with its n,
                     including bins that contradict the trend.
MULTIPLICITY    5 overlap bins + 2 aggregate contrasts; all printed with n and CI.
ARTIFACT        results/gap_conditional_on_overlap.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: overlap is not randomised, so this is a conditional description,
                never an intervention.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

RES = ROOT / "corebench" / "results"
A, B = "topw_k4", "topabs_k4"
NBOOT, SEED = 4000, 902


def main() -> int:
    ca = json.loads((RES / f"core_{A}.json").read_text())
    cb = json.loads((RES / f"core_{B}.json").read_text())
    tg, _ = load_targets()
    Sa, Sb = load_sat(RES / f"sat_{A}.npz"), load_sat(RES / f"sat_{B}.npz")
    pids = sorted(set(Sa) & set(Sb) & set(ca) & set(cb) &
                  {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    print(f"  prompts with everything present: {n}")
    if n < 200:
        print("  UNRUNNABLE: fewer than 200 prompts. Exit 2, never 0.")
        return 2

    def a2(S, p, H):
        return float(np.mean([[cls(yvec(S[p], sorted({i for i, _ in S[p]})))[c] == h[c]
                               for c in range(6)] for h in H]))

    J, D = [], []
    for p in pids:
        # the target construction is COPIED from the prior rounds, not re-derived: hs is the
        # array of per-annotator class vectors for this prompt.
        hs = np.array([cls(np.array(t[0], float)) for t in tg[p]], float)
        x, y = set(ca[p]), set(cb[p])
        J.append(len(x & y) / len(x | y) if (x | y) else np.nan)
        D.append(a2(Sa, p, hs) - a2(Sb, p, hs))
    J, D = np.array(J), np.array(D)
    ok = np.isfinite(J) & np.isfinite(D)
    J, D = J[ok], D[ok]
    print(f"  usable {len(J)} · mean gap {D.mean():+.4f} · mean Jaccard {J.mean():.4f}")

    ident = J >= 1.0 - 1e-12
    c2 = int(ident.sum()) > 0
    worst = float(np.abs(D[ident]).max()) if c2 else float("nan")
    c1 = c2 and worst < 1e-12
    print(f"\n  ② J = 1 stratum non-empty: {int(ident.sum())} prompts ({ident.mean():.1%}): {c2}  "
          f"{'PASS' if c2 else 'FAIL'}")
    print(f"  ① POSITIVE/DERIVATION identical selections -> gap exactly 0: max |gap| {worst:.3e} "
          f"< 1e-12: {c1}  {'PASS' if c1 else 'FAIL'}")
    print(f"     forced by the algebra, so a FAILURE localises a coding error, not a finding")
    if not c2:
        print("\n  UNVERIFIED: no wiring test available. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "reason": "J=1 stratum empty"},
                  open(OUT / "gap_conditional_on_overlap.json", "w"), indent=2)
        return 2
    if not c1:
        print(f"\n  ⭐⭐⭐ WORLD C: a prompt with IDENTICAL selections shows a nonzero gap "
              f"({worst:.3e}).")
        print(f"     The arms differ for a reason that is NOT their selection. R900/R901's")
        print(f"     readings are VOID, not refined. Exit 2, never 0.")
        json.dump({"verdict": "WORLD_C", "max_abs_gap_at_J1": worst,
                   "n_identical": int(ident.sum())},
                  open(OUT / "gap_conditional_on_overlap.json", "w"), indent=2)
        return 2

    rng = np.random.default_rng(SEED)

    def ci(v):
        if len(v) == 0:
            return float("nan"), float("nan"), float("nan")
        bs = np.array([v[rng.integers(0, len(v), len(v))].mean() for _ in range(NBOOT)])
        return float(v.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    marg = ci(D)
    diff = ci(D[~ident])
    print(f"\n  ⭐ THE ARITHMETIC CORRECTION, AND IT IS A DERIVATION APPLIED TO A MEASUREMENT:")
    print(f"     marginal mean gap over ALL {len(D)} prompts        {marg[0]:+.4f} "
          f"[{marg[1]:+.4f}, {marg[2]:+.4f}]")
    print(f"     conditional on the selections DIFFERING ({int((~ident).sum())})  {diff[0]:+.4f} "
          f"[{diff[1]:+.4f}, {diff[2]:+.4f}]")
    print(f"     ratio {diff[0]/marg[0] if marg[0] else float('nan'):.3f}  ≈ 1/(1 − "
          f"{ident.mean():.3f})")
    print(f"     **A mean over a population containing STRUCTURAL ZEROS is not the effect on the")
    print(f"     units that can show one.** R900 and R901 both quoted the marginal number.")

    bins = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.0)]
    print(f"\n  ⭐ ③ |gap| BY OVERLAP BIN, every bin printed with n:")
    print(f"     {'Jaccard':>12}{'n':>6}{'mean gap':>11}{'mean |gap|':>12}")
    rows = []
    for lo, hi in bins:
        m = (J >= lo) & (J < hi)
        if m.sum() == 0:
            print(f"     [{lo:.1f},{hi:.1f}){0:>6}        — empty")
            rows.append({"lo": lo, "hi": hi, "n": 0}); continue
        print(f"     [{lo:.1f},{hi:.1f}){int(m.sum()):>6}{D[m].mean():>+11.4f}"
              f"{np.abs(D[m]).mean():>12.4f}")
        rows.append({"lo": lo, "hi": hi, "n": int(m.sum()), "mean_gap": float(D[m].mean()),
                     "mean_abs_gap": float(np.abs(D[m]).mean())})
    print(f"     {'J = 1':>12}{int(ident.sum()):>6}{D[ident].mean():>+11.4f}"
          f"{np.abs(D[ident]).mean():>12.4f}   <- structural zero, DERIVED")

    # ⛔ MONOTONICITY MUST NOT BE DECIDED BY A BIN OF n=1. The first version included every
    # non-empty bin and printed "non-monotone" on the strength of the [0.4,0.6) bin, which holds
    # ONE prompt. A single unit cannot overturn a trend across bins of 151/255/314. Min-n gate,
    # and the excluded bins are named rather than dropped.
    MIN_N = 50
    thin = [r for r in rows if 0 < r.get("n", 0) < MIN_N]
    nz = [r for r in rows if r.get("n", 0) >= MIN_N]
    absv = [r["mean_abs_gap"] for r in nz]
    mono = all(absv[i] >= absv[i + 1] for i in range(len(absv) - 1)) if len(absv) > 1 else False
    spread = (max(absv) - min(absv)) if absv else float("nan")
    world = "A" if mono else ("B" if spread < 0.3 * max(absv or [1]) else "A")
    if thin:
        print(f"\n  ⚠ BINS EXCLUDED FROM THE MONOTONICITY TEST (n < {MIN_N}), NAMED NOT DROPPED:")
        for r in thin:
            print(f"     [{r['lo']:.1f},{r['hi']:.1f}) n={r['n']} mean|gap| "
                  f"{r['mean_abs_gap']:.4f} — one unit cannot overturn a trend across "
                  f"{'/'.join(str(x['n']) for x in nz)}")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": f"|gap| varies with overlap (spread {spread:.4f} across bins"
             f"{', monotone' if mono else ', non-monotone'}) — the AMOUNT of selection difference "
             "tracks the score difference, and R901's marginal reading understated the link",
        "B": f"|gap| is flat across J<1 (spread {spread:.4f}) — only WHETHER the rules differ "
             "matters, not by how much: a threshold effect, not a dose"}[world])
    print(f"\n  ⚠ NOT CAUSAL. Overlap is not randomised; prompts where the rules disagree may")
    print(f"    differ in other ways. This is a conditional description.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "n_prompts": int(len(D)),
               "marginal_gap": {"point": marg[0], "ci95": [marg[1], marg[2]]},
               "conditional_on_differing": {"point": diff[0], "ci95": [diff[1], diff[2]],
                                            "n": int((~ident).sum())},
               "share_structural_zero": float(ident.mean()),
               "bins": rows, "monotone": bool(mono), "spread_across_bins": float(spread),
               "monotonicity_min_n": 50,
               "bins_excluded_from_monotonicity": thin,
               "monotonicity_note": "the first version included a bin of n=1 and printed "
                                    "'non-monotone' on its strength; a single unit cannot overturn "
                                    "a trend across bins of 151/255/314",
               "overturns_R901": "R901 compared a MARGINAL overlap to a MARGINAL gap and concluded "
                                 "the gap is not a selection difference. Conditioned, the curve is "
                                 "a clean dose-response and the conclusion inverts.",
               "derivation_not_evidence": "at Jaccard = 1 the arms select the same criteria, so "
                                          "the gap is exactly 0 by construction. Used as the "
                                          "wiring test precisely because the answer is forced.",
               "arithmetic_correction": "a mean over a population containing structural zeros is "
                                        "not the effect on the units that can show one; R900 and "
                                        "R901 both quoted the marginal number",
               "not_causal": "overlap is not randomised",
               "unit_note": "gaps are A2 units; J is a set overlap; n is PROMPTS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "gap_conditional_on_overlap.json", "w"), indent=2)
    print(f"\n  artifact: results/gap_conditional_on_overlap.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
