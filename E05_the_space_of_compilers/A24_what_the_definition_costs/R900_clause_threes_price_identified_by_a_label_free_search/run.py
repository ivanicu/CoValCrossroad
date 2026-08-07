#!/usr/bin/env python3
"""
R900 · clause ③'s other half, IDENTIFIED — because a label-free SEARCH rule existed all along.

⛔ WHY, AND THE WALL WAS MY OWN SENTENCE FOR THE THIRD TIME IN THIS ARC. R892 declared
`held-out − label-free` structurally unidentified and R895/R899 repeated it verbatim:
*"oracle_k/indep_k/greedy_k consume labels BY CONSTRUCTION and have no label-free twin on this
release, so rule and label-access change together."* **That is false, and the generator says so in
two places that had to be read side by side:**
  · `select_core.py:102` — the branch that opens `data/comparisons.jsonl` covers exactly
    `oracle_k`, `indep_k`, `greedy_k`.
  · `select_core.py:68` — the rules that consume SATISFACTION to choose criteria are
    `topvar_k`, `topwvar_k`, `oracle_k`, `greedy_k`, `indep_k` — **five, not three.**
**So `topvar_k` and `topwvar_k` run a data-driven search over criteria and never touch a human
label.** They are on disk at k=4. The twin existed; nobody had put the two lists next to each other.

⭐ **AND IT GIVES A THREE-TIER DOSE LADDER, WHICH IS BETTER THAN THE BINARY I COULD NOT BUILD:**
  · **T1 no search** — `topw_k4`, `topabs_k4`: choose on the rubric's own weights, satisfaction-blind
  · **T2 label-free search** — `topvar_k4`, `topwvar_k4`: consume satisfaction, never labels
  · **T3 label-consuming search, HELD OUT** — `greedy_k4_fit1`, `indep_k4_fit1`, `oracle_k4_fit1`
So the confounded gap decomposes:
    **T2 − T1 = the value of searching at all**, with labels absent from both sides
    **T3 − T2 = the value of ALSO seeing labels** ← *this is clause ③'s price, identified*

⚠ **AND THE TWIN IS GOOD, NOT PERFECT — STATED BEFORE THE NUMBERS.** `topvar_k` selects by
satisfaction VARIANCE; `greedy_k` selects by greedy improvement against labels. Both search, on
different objectives. So T3 − T2 is *the value of a label-driven objective over a variance-driven
one*, which is narrower than *the value of labels* in the abstract. **It is an identified contrast
about these two searches, not a universal quantity**, and that is the honest scope.

ESTIMAND        T3 − T2 (labels, given a search) and T2 − T1 (search, without labels), in
                per-prompt A2 margin against comparator genericpool16.
IDENTIFICATION  T3 − T2 is identified for THESE rules: both tiers run a data-driven criterion
                search at the same k; only one consumes labels. ⚠ Not identified as "the value of
                labels" in general — see the objective caveat above.
SCOPE           population: the k=4 arms in each tier, listed in the output — DERIVED from the
                            generator's own rule taxonomy, not globbed
                instrument: per-prompt A2 margin vs genericpool16, judge 2B
                baseline:   zero gap between adjacent tiers
                regime:     home release, 968 prompts, k=4 throughout so k is HELD FIXED
WORLDS          A · T3 > T2 > T1, with T3−T2 resolvable -> clause ③'s price is identified and
                    positive: label access buys something beyond searching
                B · T3 ≈ T2 -> given a search, labels add nothing measurable, and clause ③ costs
                    almost nothing in accuracy — defensible on principle AND cheap
                C · T2 ≈ T1 -> searching itself buys nothing, so the whole ladder is flat and the
                    tiers are not measuring what they are named for
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE: T3 − T1, the full span, must be resolvable. If the ladder's two
                     ends are indistinguishable, no interior contrast is readable and the round
                     says nothing.
                  ⭐ ② PLACEBO: within T1, `topw_k4` vs `topabs_k4` — two satisfaction-BLIND rules.
                     Their difference is not a label effect and not a search effect, so it measures
                     **WITHIN-TIER HETEROGENEITY**, and a tier MEAN is only meaningful if it is
                     small.
                     ⛔⛔ POST-RUN, AND THE PLACEBO IS THE FINDING. It came back at **+0.0748
                     [+0.0665, +0.0834]** — nearly the whole T3−T1 span (+0.0795) and more than
                     double the T2−T1 search contrast (−0.0317). **Two rules that see no
                     satisfaction and no labels differ by more than the effects I was decomposing.**
                     So the tiers are NOT homogeneous and a tier mean is not a valid aggregation.
                     ⛔ My original criterion was `|placebo| < max(|labels|,|search|)`, which PASSED
                     on 0.0748 < 0.1112 — a technicality. It asked *is the placebo smaller than the
                     effect* when the question is *is the within-tier spread small enough for the
                     mean to mean anything*. **Re-pre-registered: the placebo must be under a THIRD
                     of the label contrast.** 0.0748/0.1112 = 0.67. It fails, and the round is
                     UNVERIFIED rather than WORLD A.
                  ⭐ ③ k IS HELD FIXED AT 4 in every tier, asserted in code — R892 died of a k
                     confound and R893 of a judge confound; both are pinned here by construction.
                  ④ tier membership READ from the generator's two rule lists, not typed.
MULTIPLICITY    3 tiers, 2 adjacent contrasts, 1 span, 1 placebo; all printed with CIs.
ARTIFACT        results/clause3_identified.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND the newly narrowed one: this identifies labels-vs-variance as
                search objectives, NOT "the value of human labels" in general.
"""
import json, pathlib, re, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

BLIND = "genericpool16"
RES = ROOT / "corebench" / "results"
GEN = ROOT / "corebench" / "select_core.py"
NBOOT, SEED, K = 4000, 900, 4
T1 = ["topw_k4", "topabs_k4"]
T2 = ["topvar_k4", "topwvar_k4"]
T3 = ["greedy_k4_fit1", "indep_k4_fit1", "oracle_k4_fit1"]


def rule_lists():
    s = GEN.read_text()
    m1 = re.search(r'if a\.rule in \(([^)]*)\):\s*\n\s*for line in open\([^)]*comparisons\.jsonl', s)
    m2 = re.search(r'choose criteria -- ([^"]*?) --', s)
    if not m1 or not m2:
        return None, None
    lab = [x.strip().strip('"\'') for x in m1.group(1).split(",") if x.strip()]
    sat = [x.strip() for x in m2.group(1).split(",")]
    return lab, sat


def main() -> int:
    lab, sat = rule_lists()
    if lab is None:
        print("  UNRUNNABLE: could not read the generator's rule lists. Exit 2, never 0.")
        return 2
    free_search = [r for r in sat if r not in lab]
    print(f"  ④ READ from {GEN.name}: label-consuming {lab}")
    print(f"     satisfaction-consuming {sat}")
    print(f"     -> LABEL-FREE SEARCH rules = {free_search}")
    if not free_search:
        print("  ⭐ the twin really does not exist. Exit 2, never 0.")
        return 2
    c4 = all(any(a.startswith(r[:-2]) for r in free_search) for a in T2)
    print(f"     T2 arms {T2} all come from those rules: {c4}  {'PASS' if c4 else 'FAIL'}")
    c3 = all(f"_k{K}" in a for a in T1 + T2 + T3)
    print(f"  ③ k held fixed at {K} in EVERY tier: {c3}  {'PASS' if c3 else 'FAIL'}")

    tg, _ = load_targets()
    S = load_sat(RES / f"sat_{BLIND}.npz")
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)

    def vec(nm):
        f = RES / f"sat_{nm}.npz"
        if not f.exists():
            return None
        try:
            Sa = load_sat(f)
        except Exception:
            return None
        v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                      for k, p in enumerate(pids)])
        return np.nan_to_num(v, nan=np.nanmean(v)) if np.isfinite(v).sum() >= 200 else None

    base = vec(BLIND)
    if base is None:
        print("  UNRUNNABLE: comparator missing. Exit 2, never 0.")
        return 2

    tiers, missing = {}, []
    for nm, arms in (("T1_no_search", T1), ("T2_label_free_search", T2),
                     ("T3_label_search_heldout", T3)):
        vs = []
        for a in arms:
            v = vec(a)
            (vs.append(v - base) if v is not None else missing.append(a))
        if not vs:
            print(f"  UNRUNNABLE: tier {nm} empty. Exit 2, never 0.")
            return 2
        tiers[nm] = np.mean(vs, axis=0)
    if missing:
        print(f"  ⚠ arms absent and EXCLUDED (named, not silently dropped): {missing}")
    print(f"  prompts {n}")

    rng = np.random.default_rng(SEED)
    idxb = [rng.integers(0, n, n) for _ in range(NBOOT)]

    def ci(d):
        bs = np.array([float(d[b].mean()) for b in idxb])
        return float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))

    t1, t2, t3 = (tiers["T1_no_search"], tiers["T2_label_free_search"],
                  tiers["T3_label_search_heldout"])
    span = ci(t3 - t1); search = ci(t2 - t1); labels = ci(t3 - t2)
    pv = vec(T1[0]); pv2 = vec(T1[1])
    plac = ci((pv - base) - (pv2 - base)) if pv is not None and pv2 is not None else (0, 0, 0)

    c1 = span[1] > 0 or span[2] < 0
    # re-pre-registered: within-tier spread must be under a THIRD of the contrast being claimed,
    # else the tier MEAN is not a valid aggregation and no between-tier number is readable.
    het = abs(plac[0]) / max(abs(labels[0]), 1e-9)
    c2 = het < (1 / 3)
    print(f"\n  ① POSITIVE T3 − T1 span {span[0]:+.4f} [{span[1]:+.4f}, {span[2]:+.4f}] excludes "
          f"0: {c1}  {'PASS' if c1 else 'FAIL'}")
    print(f"  ② PLACEBO  within-T1 {T1[0]} vs {T1[1]} (both satisfaction-BLIND): "
          f"{plac[0]:+.4f} [{plac[1]:+.4f}, {plac[2]:+.4f}]")
    print(f"     within-tier spread / label contrast = {het:.2f} < 0.33: {c2}  "
          f"{'PASS' if c2 else 'FAIL'}")
    print(f"     ⛔ this measures WITHIN-TIER HETEROGENEITY. Two satisfaction-BLIND rules differing")
    print(f"        by {abs(plac[0]):.4f} means the tier MEAN is not a valid aggregation.")
    if not (c1 and c2 and c3 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        print(f"\n  ⭐ WHAT IS NEVERTHELESS ESTABLISHED, AND IT IS THE ROUND'S REAL RESULT:")
        print(f"     **The label-free twin EXISTS.** `topvar_k`/`topwvar_k` search on satisfaction")
        print(f"     and never open the label file, so R892/R895/R899's `no label-free twin exists`")
        print(f"     is RETRACTED — asserted three times, false each time.")
        print(f"     **What is NOT established is the price**, because tiering these rules by mean")
        print(f"     is invalid: within-tier spread {abs(plac[0]):.4f} vs label contrast")
        print(f"     {abs(labels[0]):.4f}. The per-ARM values below are the readable object.")
        print(f"\n     per-arm margin vs {BLIND}, k={K}, every arm printed:")
        for nm, arms in (("T1 no search", T1), ("T2 label-free search", T2),
                         ("T3 label search (HO)", T3)):
            for a in arms:
                v = vec(a)
                if v is not None:
                    print(f"       {nm:<22} {a:<20} {float((v - base).mean()):+.4f}")
        print(f"\n     ⚠ The spread WITHIN `T1` and `T2` is what a next round must explain before")
        print(f"       any tier contrast is quotable. A mean over heterogeneous rules is the")
        print(f"       population-and-count failure this session has catalogued, at the level of")
        print(f"       the AGGREGATION rather than the filter.")
        json.dump({"verdict": "UNVERIFIED",
                   "reason": "within-tier heterogeneity (%.4f) is %.0f%% of the label contrast "
                             "(%.4f); a tier mean is not a valid aggregation"
                             % (abs(plac[0]), 100 * het, abs(labels[0])),
                   "controls": {"span": bool(c1), "placebo_heterogeneity_ratio": float(het),
                                "placebo_passes": bool(c2), "k_fixed": bool(c3),
                                "tier2_from_free_search": bool(c4)},
                   "per_arm": {a: (float((vec(a) - base).mean()) if vec(a) is not None else None)
                               for a in T1 + T2 + T3},
                   "tier_means_NOT_VALID": {"T1": float(t1.mean()), "T2": float(t2.mean()),
                                            "T3": float(t3.mean())},
                   "contrasts_NOT_READABLE": {"search_T2_minus_T1": search[0],
                                              "labels_T3_minus_T2": labels[0],
                                              "span_T3_minus_T1": span[0]},
                   "what_stands": "the label-free twin EXISTS — topvar_k/topwvar_k search on "
                                  "satisfaction and never open the label file. R892/R895/R899's "
                                  "'no label-free twin exists' is RETRACTED, asserted 3x, false "
                                  "each time.",
                   "criterion_was_re_pre_registered": "original |placebo| < max(|labels|,|search|) "
                                                      "passed at 0.0748 < 0.1112 on a technicality; "
                                                      "it asked whether the placebo was smaller "
                                                      "than the effect, not whether the tier mean "
                                                      "was a valid aggregation. Now < 1/3."},
                  open(OUT / "clause3_identified.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐ THE LADDER, k = {K} throughout, margin vs {BLIND}:")
    for nm, v in (("T1 no search        ", t1), ("T2 label-free search", t2),
                  ("T3 label search (HO)", t3)):
        print(f"     {nm}  {v.mean():+.4f}")
    print(f"\n  ⭐⭐ DECOMPOSITION:")
    print(f"     T2 − T1  search, labels absent from both sides : {search[0]:+.4f} "
          f"[{search[1]:+.4f}, {search[2]:+.4f}]")
    print(f"     T3 − T2  **LABELS, given a search — CLAUSE ③'s PRICE** : {labels[0]:+.4f} "
          f"[{labels[1]:+.4f}, {labels[2]:+.4f}]")
    res = labels[1] > 0 or labels[2] < 0
    world = "C" if not (search[1] > 0 or search[2] < 0) else ("A" if res else "B")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": f"clause ③'s price is IDENTIFIED and resolvable at {labels[0]:+.4f} — given a search, "
             "label access buys something, and excluding label-consumers costs that much",
        "B": "given a search, labels add nothing resolvable — clause ③ is defensible on principle "
             "AND nearly free in accuracy, which is a stronger position than the definition claims",
        "C": "searching itself buys nothing resolvable, so the ladder is flat and the tiers are "
             "not measuring what they are named for"}[world])
    print(f"\n  ⚠ SCOPE, NARROWED ON PURPOSE: `topvar_k` searches by satisfaction VARIANCE and")
    print(f"    `greedy_k` by improvement against LABELS. So this is the value of a label-driven")
    print(f"    objective OVER a variance-driven one — an identified contrast about these two")
    print(f"    searches, **not `the value of labels` in general.**")
    print(f"  ⛔ AND R892/R895/R899's `no label-free twin exists` is RETRACTED. It was asserted")
    print(f"     three times and was false each time; the generator's two rule lists differ by")
    print(f"     exactly the arms that identify this contrast.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "k": K, "n_prompts": n,
               "label_consuming_rules": lab, "satisfaction_consuming_rules": sat,
               "label_free_search_rules": free_search,
               "tiers": {"T1_no_search": T1, "T2_label_free_search": T2,
                         "T3_label_search_heldout": T3},
               "tier_means": {"T1": float(t1.mean()), "T2": float(t2.mean()),
                              "T3": float(t3.mean())},
               "contrast_search_T2_minus_T1": {"point": search[0], "ci95": [search[1], search[2]]},
               "contrast_labels_T3_minus_T2": {"point": labels[0], "ci95": [labels[1], labels[2]],
                                               "identified": True,
                                               "scope": "labels vs variance as SEARCH OBJECTIVES, "
                                                        "not the value of labels in general"},
               "span_T3_minus_T1": {"point": span[0], "ci95": [span[1], span[2]]},
               "placebo_within_T1": {"point": plac[0], "ci95": [plac[1], plac[2]],
                                     "why": "two satisfaction-blind rules; neither a label nor a "
                                            "search effect, so it is the round's noise scale"},
               "arms_absent": missing,
               "retracts": "R892/R895/R899's claim that no label-free twin exists on this release. "
                           "Asserted three times, false each time: select_core.py:102 lists three "
                           "label-consuming rules and :68 lists five satisfaction-consuming ones, "
                           "and the difference is topvar_k / topwvar_k.",
               "unit_note": "margins are A2 units vs genericpool16",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "clause3_identified.json", "w"), indent=2)
    print(f"\n  artifact: results/clause3_identified.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
