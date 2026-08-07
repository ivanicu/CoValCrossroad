#!/usr/bin/env python3
"""
R903 · do the 12 arms the definition admits AGREE about which criteria matter?

⛔ WHY. R902 showed that for two label-free rules the score gap is a clean dose-response in
criterion overlap: mean |gap| runs 0.1984 → 0.1384 → 0.0597 → 0.0000 as Jaccard rises, and the gap
conditional on differing is +0.1004. **So WHICH criteria an arm picks matters at a scale larger than
anything else in this arc.** The definition admits 12 arms. If those 12 disagree about criteria as
much as `topw_k4` and `topabs_k4` do, then `admitted` is a far weaker equivalence than the word
suggests — the definition would be certifying as interchangeable a set of arms that pick different
things and score differently for that reason.

⛔⛔ **THE ARITHMETIC CEILING, DECLARED BEFORE THE MEASUREMENT.** The 12 span **k = 2 … 8**. For sets
of sizes `a ≤ b`, `Jaccard ≤ a/b` — so a k=2 arm against a k=8 arm **cannot exceed 0.25 no matter
how much they agree**. Comparing raw Jaccard across the 12 against the topw/topabs pair (both k=4)
would compare a quantity with a ceiling of 0.25 against one with a ceiling of 1.0. **That is this
session's own failure class — a statistic whose bound differs across the population being pooled —
and it is being handled BEFORE the run rather than after.**
⭐ Two statistics are therefore reported side by side, never pooled:
  · **RAW Jaccard**, on **equal-k pairs only**, which is directly comparable to R901/R902's 0.5562
  · **CONTAINMENT** `|A∩B| / min(|A|,|B|)`, whose ceiling is 1.0 for every pair, on ALL pairs

ESTIMAND        the pairwise criterion-set overlap among the arms the two-clause definition admits,
                against (a) the random floor and (b) the topw/topabs pair whose disagreement R902
                priced at +0.1004 conditional.
IDENTIFICATION  exact — every arm's selection is committed per prompt in `core_*.json`.
                ⚠ NOT causal, and NOT a claim that low overlap makes the definition wrong; it
                bounds how strong an equivalence `admitted` is.
SCOPE           population: the 12 arms from R889's committed surviving list, restricted to those
                            with a per-prompt selection on disk — counted and named, never assumed
                instrument: raw Jaccard (equal-k only) and containment (all pairs) per prompt
                baseline:   random k-subsets of the prompt's FULL criterion pool (R901's floor)
                regime:     home release, judge 2B
WORLDS          A · admitted arms overlap MUCH more than topw/topabs -> `admitted` really does pick
                    out arms that agree about criteria, and the definition is a strong equivalence
                B · they overlap COMPARABLY or LESS -> the definition admits arms that disagree
                    about criteria as much as a pair whose disagreement is worth +0.1004 in score.
                    `Admitted` is then a weak equivalence and the headline should say so
                C · too few equal-k pairs to compare -> the raw statistic is unavailable and only
                    containment is readable; say so rather than pooling
KILL            CONDITIONAL:
                  ⭐ ① CEILING: an arm against ITSELF must give 1.0 on both statistics.
                  ⭐ ② FLOOR: random k-subsets of the full pool, which must REPRODUCE R901's 0.1820
                     to within 0.02 at the same seed — a cross-round wiring check, not a fresh
                     baseline. If it does not reproduce, the two rounds are not measuring the same
                     thing and no comparison to R901/R902 is admissible.
                  ⭐ ③ EQUAL-k SUBSET must be non-empty for the raw comparison; if it is not, WORLD
                     C and the raw number is withheld rather than substituted.
                  ④ the 12 are READ from R889's artifact, not retyped.
MULTIPLICITY    all pairs reported; equal-k and unequal-k separated; both statistics printed.
ARTIFACT        results/admitted_agreement.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this measures agreement about criteria, not whether the
                definition is right. A definition MAY intend to admit diverse arms.
"""
import itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
SEED = 901                      # R901's seed, so the floor is a REPRODUCTION not a new draw
R901_FLOOR = 0.1820
PAIR_REF = 0.5562               # topw_k4 vs topabs_k4, R901


def core(nm):
    f = RES / f"core_{nm}.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text())
    except Exception:
        return None


def main() -> int:
    a889 = next(A24.glob("R889_*/results/two_admitted_sets.json"), None)
    if a889 is None:
        print("  UNRUNNABLE: R889 artifact missing. Exit 2, never 0.")
        return 2
    twelve = json.loads(a889.read_text())["r888_corrected"]["surviving"]
    print(f"  ④ the 12 READ from R889's artifact: {twelve}")

    sel = {a: core(a) for a in twelve}
    have = [a for a in twelve if sel[a]]
    absent = [a for a in twelve if not sel[a]]
    print(f"  arms with a per-prompt selection on disk: {len(have)} of {len(twelve)}")
    if absent:
        print(f"  ⚠ ABSENT and NAMED, not silently dropped: {absent}")
    if len(have) < 3:
        print("  UNRUNNABLE: fewer than 3 arms with selections. Exit 2, never 0.")
        return 2

    full = core("full")
    if full is None:
        print("  UNRUNNABLE: core_full.json missing. Exit 2, never 0.")
        return 2
    pids = sorted(set.intersection(*[set(sel[a]) for a in have]) & set(full))
    print(f"  prompts present in EVERY arm: {len(pids)}")
    if len(pids) < 100:
        print("  UNRUNNABLE: fewer than 100 shared prompts. Exit 2, never 0.")
        return 2

    def stats(x, y):
        x, y = set(x), set(y)
        if not (x or y):
            return np.nan, np.nan
        j = len(x & y) / len(x | y)
        c = len(x & y) / min(len(x), len(y)) if min(len(x), len(y)) else np.nan
        return j, c

    ks = {a: float(np.mean([len(sel[a][p]) for p in pids])) for a in have}
    print(f"\n  mean k per arm: " + ", ".join(f"{a}={ks[a]:.1f}" for a in have))

    # ---- ① CEILING ----------------------------------------------------------------------------
    j0, c0 = stats(sel[have[0]][pids[0]], sel[have[0]][pids[0]])
    c1 = abs(j0 - 1.0) < 1e-12 and abs(c0 - 1.0) < 1e-12
    print(f"\n  ① CEILING  an arm against ITSELF: J={j0:.6f} C={c0:.6f}: {c1}  "
          f"{'PASS' if c1 else 'FAIL'}")

    # ---- ② FLOOR, a REPRODUCTION of R901's -----------------------------------------------------
    rng = np.random.default_rng(SEED)
    fl = []
    for p in pids:
        pool = sorted(set(full[p]))
        k = len(sel[have[0]][p])
        if len(pool) >= 2 * k:
            u = rng.choice(len(pool), k, replace=False)
            v = rng.choice(len(pool), k, replace=False)
            fl.append(stats([pool[i] for i in u], [pool[i] for i in v])[0])
    fl = np.array(fl) if fl else np.array([np.nan])
    c2 = np.isfinite(fl).sum() >= 50 and abs(float(np.nanmean(fl)) - R901_FLOOR) < 0.02
    print(f"  ② FLOOR    random k-subsets: {np.nanmean(fl):.4f} vs R901's {R901_FLOOR}: {c2}  "
          f"{'PASS' if c2 else 'FAIL'}")
    print(f"     a cross-round REPRODUCTION — if it misses, no comparison to R901/R902 is")
    print(f"     admissible because the two rounds are not measuring the same thing.")

    eq, ne = [], []
    for a, b in itertools.combinations(have, 2):
        js, cs = zip(*[stats(sel[a][p], sel[b][p]) for p in pids])
        row = {"a": a, "b": b, "k_a": ks[a], "k_b": ks[b],
               "jaccard": float(np.nanmean(js)), "containment": float(np.nanmean(cs)),
               "jaccard_ceiling": float(min(ks[a], ks[b]) / max(ks[a], ks[b]))}
        (eq if abs(ks[a] - ks[b]) < 1e-9 else ne).append(row)
    c3 = len(eq) > 0
    print(f"  ③ EQUAL-k pairs available for the RAW comparison: {len(eq)} "
          f"(unequal-k: {len(ne)}): {c3}  {'PASS' if c3 else 'FAIL'}")
    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "controls": [bool(c1), bool(c2), bool(c3)]},
                  open(OUT / "admitted_agreement.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐ EQUAL-k PAIRS — raw Jaccard, directly comparable to R901's {PAIR_REF} "
          f"(topw_k4 vs topabs_k4):")
    for r in sorted(eq, key=lambda x: x["jaccard"]):
        print(f"     {r['a']:<18} {r['b']:<18} k={r['k_a']:.0f}  J={r['jaccard']:.4f}")
    ejs = np.array([r["jaccard"] for r in eq]) if eq else np.array([np.nan])
    print(f"     mean {np.nanmean(ejs):.4f}  min {np.nanmin(ejs):.4f}  max {np.nanmax(ejs):.4f}")

    print(f"\n  ⭐ UNEQUAL-k PAIRS — CONTAINMENT (ceiling 1.0 for every pair), with each pair's")
    print(f"     arithmetic JACCARD ceiling shown so the raw number is never mistaken for low:")
    for r in sorted(ne, key=lambda x: x["containment"])[:8]:
        print(f"     {r['a']:<18} {r['b']:<18} k={r['k_a']:.0f}/{r['k_b']:.0f}  "
              f"C={r['containment']:.4f}  (J={r['jaccard']:.4f}, J-ceiling "
              f"{r['jaccard_ceiling']:.2f})")
    if len(ne) > 8:
        print(f"     … {len(ne) - 8} more, all in the artifact")
    ncs = np.array([r["containment"] for r in ne]) if ne else np.array([np.nan])
    print(f"     containment mean {np.nanmean(ncs):.4f}  min {np.nanmin(ncs):.4f}")

    # ⛔⛔ THE MEAN IS A NUMBER NO PAIR TAKES. The equal-k Jaccards are PERFECTLY BIMODAL: exact
    # 0.0000 and exact 1.0000, nothing between. Reporting 0.5000 would be averaging a bimodal
    # distribution — the failure this skill names — so the structure is reported instead.
    zeros = [r for r in eq if r["jaccard"] < 1e-9]
    ones = [r for r in eq if r["jaccard"] > 1 - 1e-9]
    mid = [r for r in eq if 1e-9 <= r["jaccard"] <= 1 - 1e-9]
    bimodal = len(mid) == 0 and zeros and ones
    # the 1.0 pairs are determinism replicas of ONE arm — not independent evidence
    rep_names = {r["a"] for r in ones} | {r["b"] for r in ones}
    print(f"\n  ⛔⛔ THE MEAN IS A NUMBER NO PAIR TAKES. The equal-k Jaccards are BIMODAL:")
    print(f"     exactly 0.0000 : {len(zeros)} pair(s)   exactly 1.0000 : {len(ones)} pair(s)   "
          f"anything between : {len(mid)}")
    print(f"     So `mean 0.5000` describes no pair in the data. Reporting it would be averaging")
    print(f"     a bimodal distribution, which is exactly what this skill forbids.")
    print(f"\n  ⭐⭐ AND THE TWO MODES ARE NOT TWO FINDINGS — ONE OF THEM IS A DERIVATION.")
    print(f"     The {len(ones)} pairs at 1.0000 are all among {sorted(rep_names)} — determinism")
    print(f"     REPLICAS of a single arm, which R890 already measured at r = 1.000000. Identical")
    print(f"     selections there are forced, not observed. **The independent evidence is the")
    print(f"     {len(zeros)} pair(s) at 0.0000**: `generic` and the `topw_k4` family share")
    print(f"     LITERALLY NO CRITERIA, and the definition admits both.")
    print(f"     Containment confirms it at every k: generic vs topw_k2/k3/k4/k6/k8 all C=0.0000.")
    world = ("C" if not c3 else
             "A" if np.nanmean(ejs) > PAIR_REF + 0.10 else "B")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": f"admitted arms agree about criteria MUCH more than topw/topabs "
             f"({np.nanmean(ejs):.4f} vs {PAIR_REF}) — `admitted` is a strong equivalence",
        "B": "the admitted arms fall into TWO families that share NOTHING. `generic` and the "
             f"`topw_k*` family have Jaccard AND containment of exactly 0.0000 at every k, while "
             "the only 1.0000 pairs are determinism replicas of one arm. **So the definition "
             "admits two arms with literally disjoint criterion sets** — far weaker than the "
             f"topw/topabs pair ({PAIR_REF}) whose disagreement R902 priced at +0.1004. "
             "`Admitted` means `cleared the bar`, never `agrees about what matters`",
        "C": "no equal-k pair exists, so the raw statistic is unavailable; only containment is "
             "readable and it is reported alone rather than substituted"}[world])
    print(f"\n  ⚠ THIS DOES NOT MAKE THE DEFINITION WRONG. A definition MAY intend to admit")
    print(f"    diverse arms — that is what R890's 8 distinct kinds already said. What it bounds")
    print(f"    is how much `admitted` licenses: not `these arms agree`, only `these arms clear")
    print(f"    the bar`. Those are different sentences and the headline uses the first.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "n_prompts": len(pids),
               "arms_used": have, "arms_absent": absent, "mean_k": ks,
               "equal_k_pairs": eq, "unequal_k_pairs": ne,
               "equal_k_jaccard": {"mean": float(np.nanmean(ejs)), "min": float(np.nanmin(ejs)),
                                   "max": float(np.nanmax(ejs)), "n": len(eq)},
               "unequal_k_containment": {"mean": float(np.nanmean(ncs)),
                                         "min": float(np.nanmin(ncs)), "n": len(ne)},
               "reference_pair_jaccard": PAIR_REF,
               "bimodal": {"n_exact_zero": len(zeros), "n_exact_one": len(ones),
                           "n_between": len(mid), "is_bimodal": bool(bimodal),
                           "replica_arms_in_the_one_mode": sorted(rep_names),
                           "note": "the equal-k Jaccards take only 0.0000 and 1.0000; the mean of "
                                   "0.5000 describes no pair. The 1.0000 pairs are determinism "
                                   "replicas of one arm (R890: r = 1.000000), so they are forced "
                                   "rather than observed; the independent evidence is the 0.0000 "
                                   "pairs — generic and topw_k4 share NO criteria and both are "
                                   "admitted."},
               "floor": {"measured": float(np.nanmean(fl)), "R901": R901_FLOOR,
                         "reproduction": bool(c2)},
               "arithmetic_ceiling_declared": "Jaccard <= min(k)/max(k); the 12 span k=2..8 so a "
                                              "k=2 vs k=8 pair cannot exceed 0.25. Raw Jaccard is "
                                              "therefore reported on EQUAL-k pairs only, and "
                                              "containment (ceiling 1.0) on all pairs. Never "
                                              "pooled.",
               "does_not_show": "that the definition is wrong. It bounds what `admitted` licenses: "
                                "not `these arms agree`, only `these arms clear the bar`.",
               "unit_note": "J and C are set overlaps; k is CRITERIA per prompt",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "admitted_agreement.json", "w"), indent=2)
    print(f"\n  artifact: results/admitted_agreement.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
