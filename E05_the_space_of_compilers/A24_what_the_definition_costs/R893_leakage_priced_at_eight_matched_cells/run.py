#!/usr/bin/env python3
"""
R893 · leakage, priced at 8 matched cells instead of 3 — the missing run, run.

⛔ WHY. R892 tried to price clause ③ and ended UNVERIFIED for a reason that was about the RELEASE,
not the effect: the only cells where a leaky arm and a held-out arm share a rule and a `k` were
`greedy_k4`, `indep_k4`, `oracle_k4` — **three**. A paired sign-flip null over 3 cells has 2³ = 8
patterns and a floor of **0.1250**, so it could not reject at 0.05 whatever the data said.

⭐ **THAT WAS A MISSING RUN, NOT A WALL, AND THE GENERATOR SAYS SO ITSELF.** `select_core.py`'s
`--fit-parity` defaults to **−1 = all (LEAKY)**, so omitting the flag produces a leaky arm at any
`k` for 0 judge calls. Five arms were generated — `greedy_k` at k=2,8,12 and `indep_k` at k=2,8 —
taking the matched cells from **3 to 8** and the null floor from **0.1250 to 0.0039**.
⚠ They were written to `corebench/results_r893_leaky/`, NOT into `corebench/results/`, so the
99-arm corpus that R890 and R891 drew their nulls from is unchanged and their artifacts stay
readable. **Adding arms to a shared directory would have silently altered every earlier round's
population.**

⚠ **AND MY OWN NEXT MIS-COUNTED, WHICH IS WHY IT WAS CHECKED BEFORE IT WAS ACTED ON.** It said the
cells would go "3 → 6, floor 0.016". The unmatched held-out cells are **five**, so the answer is 8
and 0.0039. §4's rule about the closing sentence being the one with no control attached, again.

⚠ **AND A SECOND DOCUMENTATION DRIFT, IDENTICAL IN SHAPE TO THE ONE R888 FOUND.** `--fit-parity`'s
help string says *"oracle only"*, while `select_core.py:102` applies the branch to `oracle_k`,
`indep_k` AND `greedy_k`. R888 found a comment one rule behind the same branch. **Two independent
descriptions of that line are both stale; the line itself is the only reliable statement of it.**

⛔⛔ POST-RUN, AND IT IS THE ROUND'S REAL RESIDUE: **THE BATCH CONTROL IS DEGENERATE AND ITS PASS
IS NOT BANKED.** It compared generated cells (+0.0085, n=5) against shipped ones (+0.0866, n=3) —
**a 10× gap** — and passed only because the criterion was `|diff| <= 2 * pooled_sd`, where the
pooled sd (0.0412) is itself dominated by that same split. `0.0782 <= 0.0824` is a hair's breadth,
and the test would pass almost regardless of the data. **§4's `control validated by its own
instrument's noise`: the control's quantity appears on both sides of its own comparison.**

⛔⛔⛔ **AND THE CONFOUND R892 DIED OF IS STILL HERE, INVERTED.** The 3 shipped cells are EXACTLY
the 3 k=4 cells; the 5 generated ones are exactly the k≠4 cells. **So `provenance` and `k` are
perfectly confounded and this design cannot separate them.** Two readings fit the numbers equally:
  · leakage is strongly **k-dependent** — large at k=4 (+0.0866), small at k=2,8,12 (+0.0085);
  · leakage is **provenance-dependent** — my generated arms differ from the released ones.
**WORLD A's verdict (leakage is real, p = 0.0072) survives either reading**, because all 8 cells are
positive and the sign-flip null does not care which explanation holds. **What is NOT established is
the MAGNITUDE**, which ranges over an order of magnitude depending on which reading is right.

⭐ **THE SEPARATOR IS CHEAP AND IS BEING RUN:** generate leaky arms at k=4 for all three rules with
`--tag-suffix _regen`. Comparing generated-k4 against shipped-k4 holds `k` fixed and varies only
provenance. That is R894, and until it lands **the +0.0378 point estimate is UNVERIFIED even though
the sign is not.**

ESTIMAND        the paired mean of (leaky − held-out) per-prompt margin, over the matched
                (rule, k) cells — the value of scoring against annotators the arm was fitted on.
IDENTIFICATION  exact WITHIN a cell: rule and k are held fixed and only `fit_parity` moves.
                ⚠ ACROSS cells the pairing is what carries identification, which is why the null
                is a within-cell sign flip and not a stratum shuffle.
SCOPE           population: every (rule, k) cell where BOTH a leaky and a held-out arm exist — 8
                            after generation, listed in the output, DERIVED not globbed
                instrument: per-prompt A2 margin vs comparator genericpool16
                baseline:   zero gap, i.e. fitting on the scored annotators buys nothing
                regime:     home release, judge J, 968 prompts
WORLDS          A · gap > 0 and outside the sign-flip null -> leakage is real and priced, and
                    clause ③'s cheating-prevention half is justified on evidence
                B · gap inside the null at floor 0.0039 -> with 8 cells the design CAN reject and
                    does not; leakage is not detectable at this scale, and clause ③'s premise is
                    unsupported on this release
                C · the newly generated arms behave unlike the pre-existing ones -> my own
                    generation is the confound and nothing else in the round is readable
KILL            CONDITIONAL, pre-registered before the run:
                  ⭐ ① POSITIVE, on the archetype the release documents: the `oracle_k4` cell must
                     show a positive gap. `compare.py:35` states in its own words that an oracle
                     fitted on all parities is *"leaky and its value is an inflated upper bound"*.
                     **If the one case the codebase asserts is leaky shows no gap, the instrument
                     is blind and nothing else is readable.**
                  ⭐ ② BATCH PLACEBO: the 5 cells built by ME must not differ systematically from
                     the 3 that shipped. Compared explicitly; a difference sends the round to
                     WORLD C rather than being averaged away.
                  ⭐ ③ RESOLUTION: the null must have >= 100 distinct sign patterns, else this
                     round repeats R892's defect with a bigger number. 2^8 = 256.
                  ⭐ ④ pre-registered threshold: two-sided sign-flip p < 0.05, admissible ONLY if
                     ① and ② pass. Floor is 2/256 = 0.0078 two-sided.
MULTIPLICITY    one estimand; every cell's gap printed, positive and negative alike.
ARTIFACT        results/leakage_eight_cells.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · cross-model. ⚠ AND unchanged from R892: `held-out − label-free` stays
                UNIDENTIFIED and is not attempted here — the three label-consuming rules have no
                label-free twin, and the generator cannot make one because that branch opens the
                label file unconditionally.
"""
import collections, json, pathlib, re, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

BLIND = "genericpool16"
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
NBOOT, NPERM, SEED = 4000, 20000, 893


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(RES / f"sat_{BLIND}.npz")
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]

    def vec(path):
        try:
            Sa = load_sat(path)
        except Exception:
            return None
        v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                      for k, p in enumerate(pids)])
        return v if np.isfinite(v).sum() >= 200 else None

    base = vec(RES / f"sat_{BLIND}.npz")
    if base is None:
        print("  UNRUNNABLE: comparator vector missing. Exit 2, never 0.")
        return 2
    base = np.nan_to_num(base, nan=np.nanmean(base))

    def margin(path):
        v = vec(path)
        return None if v is None else np.nan_to_num(v, nan=np.nanmean(v)) - base

    def cell_of(name):
        m = re.match(r"(oracle|indep|greedy)_k(\d+)", name)
        return (m.group(1), int(m.group(2))) if m else None

    leaky, held, provenance = {}, {}, {}
    for d, tag in ((RES, "shipped"), (NEW, "generated")):
        for f in sorted(d.glob("sat_*.npz")):
            nm = f.stem[4:]
            c = cell_of(nm)
            if c is None:
                continue
            if "_fit" in nm:
                if d is RES:
                    held.setdefault(c, []).append(f)
            else:
                if c not in leaky or tag == "generated":
                    leaky.setdefault(c, []).append(f)
                    provenance[c] = tag
    cells = sorted(set(leaky) & set(held))
    print(f"  matched (rule,k) cells with BOTH a leaky and a held-out arm: {len(cells)}")
    for c in cells:
        print(f"    {c[0]}_k{c[1]:<3} leaky {len(leaky[c])} arm(s) [{provenance[c]}] · "
              f"held-out {len(held[c])} arm(s)")
    c3 = 2 ** len(cells) >= 100
    print(f"\n  ③ RESOLUTION 2^{len(cells)} = {2**len(cells)} sign patterns >= 100: {c3}  "
          f"{'PASS' if c3 else 'FAIL'}")
    if not cells or not c3:
        print("  UNVERIFIED: too few matched cells to build a null that can reject. Exit 2.")
        json.dump({"verdict": "UNVERIFIED", "n_cells": len(cells)},
                  open(OUT / "leakage_eight_cells.json", "w"), indent=2)
        return 2

    gaps = {}
    for c in cells:
        L = [margin(f) for f in leaky[c]]; Hh = [margin(f) for f in held[c]]
        L = [x for x in L if x is not None]; Hh = [x for x in Hh if x is not None]
        if not L or not Hh:
            continue
        gaps[c] = np.mean(L, axis=0) - np.mean(Hh, axis=0)
    cells = [c for c in cells if c in gaps]
    G = np.array([gaps[c] for c in cells])                     # cells x prompts
    per_cell = G.mean(axis=1)
    obs = float(per_cell.mean())

    # ---- CONTROLS -----------------------------------------------------------------------------
    oc = ("oracle", 4)
    c1 = oc in gaps and float(gaps[oc].mean()) > 0
    print(f"  ① POSITIVE oracle_k4 — the cell the codebase itself calls leaky — gap "
          f"{float(gaps[oc].mean()) if oc in gaps else float('nan'):+.4f} > 0: {c1}  "
          f"{'PASS' if c1 else 'FAIL'}")
    gen = [i for i, c in enumerate(cells) if provenance.get(c) == "generated"]
    shp = [i for i, c in enumerate(cells) if provenance.get(c) == "shipped"]
    if gen and shp:
        dg, ds = per_cell[gen].mean(), per_cell[shp].mean()
        pooled = per_cell.std(ddof=1) if len(per_cell) > 1 else 0.0
        c2 = pooled == 0 or abs(dg - ds) <= 2 * pooled
        print(f"  ② BATCH    generated cells {dg:+.4f} (n={len(gen)}) vs shipped {ds:+.4f} "
              f"(n={len(shp)}); |diff| {abs(dg-ds):.4f} <= 2sd {2*pooled:.4f}: {c2}  "
              f"{'PASS' if c2 else 'FAIL'}")
    else:
        dg = ds = float("nan"); c2 = False
        print(f"  ② BATCH    cannot compare: generated {len(gen)}, shipped {len(shp)}  FAIL")
    if not (c1 and c2):
        w = "C" if not c2 else "UNVERIFIED"
        print(f"\n  ⭐ {w}: " + ("the newly generated arms differ from the shipped ones — my own "
                                "generation is the confound" if not c2 else
                                "the archetype leak is undetectable; the instrument is blind"))
        json.dump({"verdict": "UNVERIFIED", "world": w, "controls": {"positive": bool(c1),
                   "batch": bool(c2)}, "generated_mean": float(dg), "shipped_mean": float(ds)},
                  open(OUT / "leakage_eight_cells.json", "w"), indent=2)
        return 2

    rng = np.random.default_rng(SEED)
    sgn = rng.choice([-1.0, 1.0], size=(NPERM, len(cells)))
    null = (sgn * per_cell[None, :]).mean(axis=1)
    p = float((np.abs(null) >= abs(obs)).mean())
    floor = 2 / 2 ** len(cells)
    idxb = [rng.integers(0, len(pids), len(pids)) for _ in range(NBOOT)]
    bs = np.array([float(G[:, b].mean(axis=1).mean()) for b in idxb])
    lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    print(f"\n  ⭐ PER-CELL GAPS (leaky − held-out), all {len(cells)} printed:")
    for c, g in zip(cells, per_cell):
        print(f"     {c[0]}_k{c[1]:<3} {g:+.4f}   [{provenance.get(c)}]")
    print(f"\n  ⭐⭐ paired mean = {obs:+.4f}   prompt-bootstrap CI [{lo:+.4f}, {hi:+.4f}]")
    print(f"     sign-flip p = {p:.4f} over {NPERM} draws  (floor {floor:.4f}, "
          f"{2**len(cells)} distinct patterns)")
    k4 = float(np.mean([per_cell[i] for i, c in enumerate(cells) if c[1] == 4]))
    print(f"     ⚠ R892's 3-cell k=4-only estimate was +0.0065; here the k=4 cells give "
          f"{k4:+.4f}")

    world = "A" if p < 0.05 else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": "leakage is REAL and priced — the gap survives a sign-flip null that CAN reject, so "
             "clause ③'s cheating-prevention half is justified on evidence and not only on "
             "principle",
        "B": f"with {len(cells)} cells the design CAN reject at 0.05 and does NOT — leakage is not "
             "detectable at this scale, and clause ③'s premise is unsupported on this release"}[world])
    print(f"\n  ⚠ UNCHANGED FROM R892: `held-out − label-free` stays UNIDENTIFIED and is not")
    print(f"    attempted here. This prices the leak, never the whole of clause ③.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "n_prompts": len(pids),
               "n_cells": len(cells),
               "cells": [{"rule": c[0], "k": c[1], "gap": float(g),
                          "provenance": provenance.get(c)} for c, g in zip(cells, per_cell)],
               "paired_mean": obs, "bootstrap_ci95": [lo, hi],
               "signflip_p": p, "signflip_floor": floor, "n_patterns": 2 ** len(cells),
               "k4_only_here": k4, "r892_k4_only": 0.0065,
               "controls": {"positive_oracle_k4": bool(c1), "batch_generated_vs_shipped": bool(c2),
                            "resolution_patterns_ge_100": bool(c3),
                            "generated_mean": float(dg), "shipped_mean": float(ds)},
               "generated_arms": "greedy_k at k=2,8,12 and indep_k at k=2,8, written to "
                                 "corebench/results_r893_leaky/ so the 99-arm corpus R890/R891 "
                                 "drew nulls from is unchanged",
               "still_unidentified": "held-out minus label-free — the three label-consuming rules "
                                     "have no label-free twin and the generator cannot make one",
               "doc_drift": "--fit-parity's help says 'oracle only' while select_core.py:102 "
                            "covers oracle_k, indep_k and greedy_k. Second stale description of "
                            "that same line; R888 found the first.",
               "post_run_correction": {
                   "batch_control_degenerate": "|diff| 0.0782 <= 2sd 0.0824 passed by a hair, and "
                                               "the pooled sd is dominated by the very split being "
                                               "tested — the control's quantity is on both sides",
                   "provenance_perfectly_confounded_with_k": "the 3 shipped cells ARE the 3 k=4 "
                                                             "cells; the 5 generated ones are the "
                                                             "k!=4 cells",
                   "what_survives": "the SIGN and the sign-flip p — all 8 cells positive, and the "
                                    "null does not care which explanation holds",
                   "what_does_not": "the MAGNITUDE +0.0378, which varies ~10x between the two "
                                    "readings (k-dependence vs provenance)",
                   "separator_running": "leaky k=4 arms regenerated with --tag-suffix _regen; "
                                        "generated-k4 vs shipped-k4 holds k fixed"},
               "unit_note": "gaps are A2 margin units vs genericpool16; counts are CELLS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "leakage_eight_cells.json", "w"), indent=2)
    print(f"\n  artifact: results/leakage_eight_cells.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
