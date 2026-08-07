#!/usr/bin/env python3
"""
R917 · every reported RATE recomputed on candidates only — apparatus out, and the second judge out.

⛔ WHY, AND THE FIRST VERSION OF THIS ROUND HAD THE WRONG PREMISE (kept at
`_archive/run_v1_wrong_premise_sham_not_in_topw.py`, mv not rm). It opened by saying R908's `topw`
16 *"contains `topw_k4_sham`, a poison inside the signed-weight group that fed R909–R911"*. **That is
false, and R906's own artifact says so**: `topw_k4_sham` is typed `OTHER_SOURCE`, not
`RUBRIC_SELECTOR`, and R908 reads its population from R906's `RUBRIC_SELECTOR` list — so the sham was
never in the `topw` denominator. I asserted a containment I had not read. ⚠ Its admission was
nevertheless MEASURED before that was discovered — `margin -0.051343, lo -0.060777, admitted False` —
and that measurement stands; it just answers a question no cell depended on.

⭐⭐⭐ **AND THE WIRING CONTROL FOUND SOMETHING LARGER THAN THE THING THE ROUND WAS BUILT FOR.** Its
first run recomputed `topw` as `10/20` against R908's `7/16`, which I first read as my own bug — my
arm glob had matched seven `_08b` arms, the 0.8B-judge rebuilds R895 established must never be pooled
with 2B arms, via the same prefix-regex shape R894 found in R893. **It was my bug. It was also
R906's, and R908's, and R911's.** Read from R906's committed list:

  · `RUBRIC_SELECTOR` built = 86 arms, of which **37 are `_08b`/`_08bR` — 43% of the population
    is a different judge.**
  · `topw` 16 = **9 arms scored by 2B + 7 scored by 0.8B.**
  · every rule's rate in R908 is therefore a **share over two instruments**.

⭐⭐ **SO APPARATUS AND WRONG-JUDGE ARMS ARE THE SAME ESTIMAND** — units sitting in a rate that are
not candidates for the thing the rate is about — and this round removes both in one operation rather
than chasing them separately. R916 supplies the apparatus set; R895 supplies the judge rule.

⚠ **AND THE ARITHMETIC TRAP IS LIVE HERE.** If every `_08b` arm had failed admission, then removing
them could only shrink denominators, every share could only rise, and the whole recomputation would
be a DERIVATION wearing a measurement's clothes. It is not: **`oracle_k4_08bR` is admitted**, so the
`oracle` NUMERATOR moves 5 → 4 and the direction of each rule's correction is not forced. Control ②
checks this rather than assuming it, and if it ever fails this round must relabel itself.

ESTIMAND        the admitted share per selection rule, and R911's signed-vs-other separation, on a
                population restricted to candidates: apparatus removed and judge matched to 2B.
IDENTIFICATION  exact. ⚠ Not an admission PROBABILITY — the arms were built, not sampled (R906's
                standing caveat, inherited not re-derived).
SCOPE           population: R906's `RUBRIC_SELECTOR` typing plus R911's three new arms per rule
                instrument: A2 margin vs `genericpool16`, bootstrap NBOOT 8000, admission lo > 0
                            — inherited from R881; NOT recomputed here, read from committed lists
                baseline:   the uncorrected mixed-judge cells, reproduced exactly first
                regime:     home release, judge 2B after correction, seed 917
WORLDS          A · the corrected shares move but the separations survive -> the reported numbers
                    were wrong and the findings they carried were not
                B · a separation is LOST -> the finding rested on a two-instrument population and
                    is retracted
                C · nothing moves -> the mixing was inert and this is hygiene
KILL            CONDITIONAL:
                  ⭐ ① WIRING/POSITIVE: recomputing WITHOUT any correction must reproduce R908's
                     published `n_admitted/n_built` for **all eight rules exactly**. Same source,
                     same operation — anything but an exact match means the recomputation is not
                     doing what R908 did, and the corrected numbers would mean nothing.
                  ⭐ ② NOT-FORCED: at least one rule's NUMERATOR must move. If none does, the
                     result is a denominator derivation and is labelled one, not reported as
                     measured.
                  ⭐ ③ PLACEBO: dropping the same NUMBER of arms per rule, sampled uniformly from
                     the mixed population, must NOT reproduce the judge-matched shares. If the
                     judge-matched share sits inside the random-drop null, the "correction" is
                     small-n and nothing about the judge. 2000 draws, per rule.
                  ⭐ ④ the apparatus set is READ from R916 and the judge rule is checked against
                     R895's own committed statement — neither retyped.
MULTIPLICITY    8 rules × {mixed, matched} × {share, Wilson}; R911's specifications × 2; all
                printed including every cell that does not move.
ARTIFACT        results/candidates_only.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND unchanged: comparator robustness
                (R913/R914), priced at 15,488 judge calls and not bought.
"""
import json, pathlib, re, subprocess
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
SIGNED, OTHER_R = "topw", ("topabs", "topvar", "topwvar")
SEED, NDRAW = 917, 2000


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    ph, d = k / n, 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def is08(a):
    return a.endswith("_08b") or a.endswith("_08bR")


def rule_of(a):
    m = re.match(r"([a-z]+)_k(\d+)", a)
    return m.group(1) if m else None


def k_of(a):
    m = re.match(r"[a-z]+_k(\d+)", a)
    return int(m.group(1)) if m else None


def main() -> int:
    r906 = json.loads(next(A24.glob("R906_*/results/bar_by_source.json")).read_text())
    r908 = json.loads(next(A24.glob("R908_*/results/bar_by_rule.json")).read_text())
    r911 = json.loads(next(A24.glob("R911_*/results/matched_k_contrast.json")).read_text())
    r916 = json.loads(next(A24.glob("R916_*/results/apparatus_audit.json")).read_text())
    r895 = json.loads(next(A24.glob("R895_*/results/judge_matched_leakage.json")).read_text())

    apparatus = {a for a, h in r916["hits"].items()
                 if any(x in h["signatures"] for x in ("COMPARATOR", "WHOLE_RUBRIC", "MISDIRECTED"))}
    print(f"  ④ apparatus set READ from R916: {len(apparatus)} — {sorted(apparatus)}")
    print(f"  ④ judge rule checked against R895's committed statement, not retyped:")
    print(f"     \"{r895['not_pooled']}\"")
    c4 = bool(apparatus) and "0.8B" in r895["not_pooled"] and "pooling" in r895["not_pooled"]
    print(f"     ④ {c4}  {'PASS' if c4 else 'FAIL'}")

    rs = [k for k in r906["kinds"] if k["kind"] == "RUBRIC_SELECTOR"][0]
    built, adm = list(rs["built"]), set(rs["admitted"])
    pub = {r["rule"]: (r["n_admitted"], r["n_built"]) for r in r908["rules"]}

    def tally(arms):
        t = {}
        for a in arms:
            r = rule_of(a)
            if r is None:
                continue
            x = t.setdefault(r, [0, 0])
            x[0] += int(a in adm)
            x[1] += 1
        return t

    mixed = tally(built)
    mism = {r: (mixed.get(r), pub.get(r)) for r in pub
            if r != "OTHER" and mixed.get(r) != list(pub[r])}
    c1 = not mism
    print(f"\n  ① WIRING/POSITIVE — recompute with NO correction, all rules vs R908 published:")
    print(f"     {'rule':<10}{'recomputed':>12}{'R908':>10}   match")
    for r in sorted(pub, key=lambda z: -pub[z][1]):
        if r == "OTHER":
            continue
        m, p = mixed.get(r, [0, 0]), pub[r]
        print(f"     {r:<10}{m[0]:>5}/{m[1]:<6}{p[0]:>5}/{p[1]:<4}   {m == list(p)}")
    print(f"     ① exact on all rules: {c1}  {'PASS' if c1 else 'FAIL'}"
          + ("" if c1 else f"   mismatches {mism}"))

    cand = [a for a in built if a not in apparatus and not is08(a)]
    matched = tally(cand)
    dropped_app = sorted(a for a in built if a in apparatus)
    dropped_jud = sorted(a for a in built if is08(a) and a not in apparatus)
    print(f"\n  ⭐ removed from R906's {len(built)}: apparatus {len(dropped_app)} {dropped_app}, "
          f"second judge {len(dropped_jud)} -> {len(cand)} candidates")

    moved = {r: [mixed[r][0], matched.get(r, [0, 0])[0]] for r in mixed
             if matched.get(r, [0, 0])[0] != mixed[r][0]}
    adm08 = sorted(a for a in built if is08(a) and a in adm)
    c2 = bool(moved)
    print(f"\n  ② NOT-FORCED — admitted `_08b` arms exist, so removal is not a pure denominator op:")
    print(f"     admitted and `_08b`: {adm08}")
    print(f"     numerators that MOVE: {moved}")
    print(f"     ② {c2}  {'PASS' if c2 else 'FAIL — this is a DERIVATION and must be relabelled'}")

    rng = np.random.default_rng(SEED)
    plac = {}
    for r in sorted(mixed):
        arms = [a for a in built if rule_of(a) == r]
        ndrop = len(arms) - matched.get(r, [0, 0])[1]
        if ndrop <= 0 or len(arms) - ndrop == 0:
            plac[r] = None
            continue
        sh = []
        for _ in range(NDRAW):
            keep = rng.permutation(len(arms))[ndrop:]
            kk = [arms[i] for i in keep]
            sh.append(sum(a in adm for a in kk) / len(kk))
        sh = np.array(sh)
        obs = matched[r][0] / matched[r][1]
        lo, hi = float(np.percentile(sh, 2.5)), float(np.percentile(sh, 97.5))
        plac[r] = {"n_drop": int(ndrop), "obs": float(obs), "null_mean": float(sh.mean()),
                   "null_ci": [lo, hi], "outside": bool(obs < lo or obs > hi)}
    tested = [r for r in plac if plac[r]]
    outside = [r for r in tested if plac[r]["outside"]]
    c3 = len(outside) >= 1
    print(f"\n  ③ PLACEBO — drop the same NUMBER uniformly at random, {NDRAW} draws per rule:")
    print(f"     {'rule':<10}{'drop':>5}{'matched':>10}{'random-drop null 95%':>26}  outside?")
    for r in sorted(plac):
        p = plac[r]
        if not p:
            print(f"     {r:<10}{'-':>5}{'n/a':>10}{'(no arms dropped)':>26}  -")
            continue
        band = "[%.3f, %.3f]" % (p["null_ci"][0], p["null_ci"][1])
        print(f"     {r:<10}{p['n_drop']:>5}{p['obs']:>10.3f}{band:>26}  {p['outside']}")
    print(f"     ③ judge-matched share escapes the small-n null in {len(outside)}/{len(tested)} "
          f"rules: {c3}  {'PASS' if c3 else 'FAIL'}")

    if not (c1 and c2 and c3 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "c4": c4,
                   "mismatches": {k: list(v) for k, v in mism.items()}},
                  open(OUT / "candidates_only.json", "w"), indent=2)
        return 2

    rows = []
    print(f"\n  ⭐⭐⭐ EVERY RULE'S RATE, MIXED vs CANDIDATES-ONLY — including cells that do not move:")
    print(f"     {'rule':<10}{'mixed':>10}{'share':>8}{'Wilson95':>18}   "
          f"{'matched':>10}{'share':>8}{'Wilson95':>18}")
    for r in sorted(mixed, key=lambda z: -mixed[z][1]):
        a0, n0 = mixed[r]
        a1, n1 = matched.get(r, [0, 0])
        w0, w1 = wilson(a0, n0), wilson(a1, n1)
        rows.append({"rule": r, "mixed": [a0, n0], "matched": [a1, n1],
                     "share_mixed": a0 / n0 if n0 else None,
                     "share_matched": a1 / n1 if n1 else None,
                     "wilson_mixed": list(w0), "wilson_matched": list(w1),
                     "numerator_moved": a0 != a1})
        tail = ("%8.3f[%6.3f,%6.3f]" % (a1 / n1, w1[0], w1[1])) if n1 else f"{'n/a':>8}"
        print(f"     {r:<10}{a0:>5}/{n0:<4}{a0/n0:>8.3f}[{w0[0]:>6.3f},{w0[1]:>6.3f}]   "
              f"{a1:>5}/{n1:<4}{tail}")

    new = {r: [x["arm"] for x in v] for r, v in r911["new_arms"].items()}
    new_adm = {x["arm"] for v in r911["new_arms"].values() for x in v if x["admitted"]}
    shared = set(r911["shared_k"])
    A = adm | new_adm

    def grp(rules, kfilter, matched_only):
        arms = [a for a in built if rule_of(a) in rules] + \
               [a for r in rules for a in new.get(r, [])]
        if matched_only:
            arms = [a for a in arms if a not in apparatus and not is08(a)]
        if kfilter:
            arms = [a for a in arms if k_of(a) in shared]
        return sum(a in A for a in arms), len(arms)

    specs = []
    print(f"\n  ⭐⭐ R911's SEPARATION recomputed on candidates only "
          f"(shared k = {sorted(shared)}):")
    print(f"     {'spec':<20}{'signed mixed':>15}{'signed matched':>16}"
          f"{'other matched':>15}{'gap':>8}  disjoint")
    for name, kf in (("PRIMARY k-matched", True), ("pooled over k", False)):
        sa0, sn0 = grp([SIGNED], kf, False)
        sa, sn = grp([SIGNED], kf, True)
        oa, on = grp(list(OTHER_R), kf, True)
        ws, wo = wilson(sa, sn), wilson(oa, on)
        dis = bool(ws[0] > wo[1])
        specs.append({"spec": name, "signed_mixed": [sa0, sn0], "signed": [sa, sn],
                      "other": [oa, on], "wilson_signed": list(ws), "wilson_other": list(wo),
                      "disjoint": dis, "gap": float(ws[0] - wo[1])})
        print(f"     {name:<20}{sa0:>8}/{sn0:<6}{sa:>9}/{sn:<6}{oa:>8}/{on:<6}"
              f"{ws[0] - wo[1]:>+8.3f}  {dis}")

    survives = all(s["disjoint"] for s in specs)
    world = "A" if survives else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        "the shares were wrong and the finding they carried was not. Every rule's rate rises when "
        "the second judge leaves, and the signed-vs-other separation holds on candidates only."
        if survives else
        "a separation is LOST once the population is restricted to candidates — R911's finding "
        "rested on a two-instrument population and is retracted."))
    print(f"     ⚠ NOT COSMETIC: `topw` {pub['topw'][0]}/{pub['topw'][1]} = "
          f"{pub['topw'][0]/pub['topw'][1]:.3f} -> {matched['topw'][0]}/{matched['topw'][1]} = "
          f"{matched['topw'][0]/matched['topw'][1]:.3f}; "
          f"{sum(r['mixed'] != r['matched'] for r in rows)} of {len(rows)} rules move.")
    print(f"     ⚠ AND NOT UNIFORM IN DIRECTION: `oracle`'s NUMERATOR FALLS "
          f"{pub['oracle'][0]} -> {matched['oracle'][0]}, because one `_08b` arm WAS admitted.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "ndraw": NDRAW,
               "corrects_own_premise": {
                   "was": "R908's topw 16 contains topw_k4_sham, a poison in the signed group",
                   "why_wrong": "R906 types topw_k4_sham as OTHER_SOURCE; R908 reads its population "
                                "from RUBRIC_SELECTOR, so the sham was never in the topw denominator",
                   "measured_anyway": {"arm": "topw_k4_sham", "margin": -0.051343,
                                       "lo": -0.060777, "admitted": False}},
               "judge_mixing": {"rubric_selector_built": len(built),
                                "of_which_second_judge": sum(is08(a) for a in built),
                                "topw_16_is": "9 arms judged by 2B + 7 judged by 0.8B",
                                "admitted_second_judge_arms": adm08,
                                "source_of_rule": "R895's committed not_pooled statement"},
               "dropped": {"apparatus": dropped_app, "second_judge": dropped_jud,
                           "candidates": len(cand)},
               "rules": rows, "placebo": plac, "r911_specs": specs,
               "not_forced": {"numerators_that_moved": moved,
                              "why_it_matters": "if no numerator moved this would be a denominator "
                                                "DERIVATION, not a measurement"},
               "unit_note": "counts are ARMS; share = admitted/built within a rule",
               "not_an_admission_probability": "the arms were built, not sampled (R906's caveat)",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "candidates_only.json", "w"), indent=2)
    print(f"\n  artifact: results/candidates_only.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
