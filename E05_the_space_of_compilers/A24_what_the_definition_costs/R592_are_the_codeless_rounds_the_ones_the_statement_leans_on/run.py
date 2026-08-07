#!/usr/bin/env python3
"""
R592 -- are the rounds that persist no code the ones the deliverable leans on?

R591's NEXT line said "count how many rounds carry a runnable run.py". CHECK #192 KILLED IT
BEFORE IT RAN: `run.py` is a FILENAME and the property is RE-RUNNABILITY. Instrument unit and
claim unit are not equal -- §4's row, and the same class as the fourteen string errors before
it. Measured immediately: 339 rounds ship `run.py`, but the corpus also holds `selftest.py`,
`speccurve.py`, `strata.py`, `recovery.py` and 20 more one-off names, so a `run.py` census
would have mis-scored every round that named its script after its question.

And a bare census is CLOSURE. The frontier question is whether the missing code is DISTRIBUTED
AT RANDOM or concentrated exactly where the deliverable rests its weight -- those are different
objects and they license different confidence in the definition.

ESTIMAND        Delta = P(round is CITED by STATEMENT.md | round persists NO code)
                      - P(round is CITED by STATEMENT.md | round persists code)
IDENTIFICATION  Both terms are counts over a complete enumeration -- no sampling, no model.
                ⚠ So the point estimate is a DERIVATION, not a measurement (§ arithmetic
                trap). What is TESTED is whether |Delta| exceeds what label-shuffling
                produces, which is a separate quantity and the only one with a null.
SCOPE           population : all 583 round dirs across E01..E05
                instrument : filesystem -- presence of any *.py / *.sh at the round's top
                             level. This is a DIRECT property of the directory, not a proxy:
                             the claim is "the round persists its instrument", and a file
                             either is there or is not.
                baseline   : 5,000 label permutations of the codeless flag
                regime     : E01..E05 as committed at this sha
WORLDS          A INCIDENTAL: codeless rounds are spread at random over the corpus ->
                  Delta sits inside the permutation null. The gap is bookkeeping and the
                  deliverable's evidence is as attackable as the rest.
                B LOAD-BEARING: codeless rounds are ENRICHED among cited rounds -> the
                  statement leans hardest on exactly the rounds whose instrument cannot be
                  read, and every claim citing them must carry that scope.
                C PROTECTED: codeless rounds are DEPLETED among cited rounds -> the citing
                  discipline already avoided them, which is a property worth knowing and
                  worth not assuming.
KILL            pre-registered, evaluated ONLY if both controls fire:
                  two-sided permutation p >= 0.05 -> world A, and no claim about
                  concentration is admissible.
POSITIVE CTRL   plant: force the k rounds with the MOST citations to be codeless and rerun.
                Must recover world B. Fails at g=0: with no planting the planted-arm statistic
                must equal the observed one. Report the retention and the MDE.
NEGATIVE CTRL   the permutation null itself -- destroys the pairing between "is codeless" and
                "is cited" while preserving both marginals.
PLACEBO         a contrast that must return ~zero: `codeless` against a coin flip of the same
                marginal rate, which shares no structure with citation.
SEEDS           0, 1, 2 on every resampling step.
ARTIFACT        results/codeless.json
IMPOSSIBLE      construct validity for "attackable": persisting code is NECESSARY for a later
                round to read the instrument and NOT SUFFICIENT -- the script may import a
                deleted module or a dead path. Establishing sufficiency would require
                executing 583 scripts against their original environments, which no artifact
                records. The measurement below is therefore an UPPER BOUND on attackability,
                and it is reported as one.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STMT = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"
OUT = pathlib.Path(__file__).resolve().parent / "results"
CODE_SUFFIX = (".py", ".sh")


def rounds():
    """round-id -> (path, persists_code). Complete enumeration over E01..E05.

    ⚠ `d.is_dir()` is not defensive padding: the glob `A*/R[0-9]*` also matches FILES like
    `R276_PREDICTION.md`, which crashed v1. And ids are collected as a list before being
    keyed, because P16 numbers R globally continuous -- a duplicate id is a real defect and
    a dict would swallow it silently.
    """
    seen, dupes = {}, []
    for ep in sorted(ROOT.glob("E0*")):
        for d in sorted(ep.glob("A*/R[0-9]*")):
            if not d.is_dir():
                continue
            m = re.match(r"R(\d+)", d.name)
            if not m:
                continue
            rid = int(m.group(1))
            code = any(f.suffix in CODE_SUFFIX for f in d.iterdir() if f.is_file())
            if rid in seen:
                dupes.append((rid, str(seen[rid][0].relative_to(ROOT)),
                              str(d.relative_to(ROOT))))
            seen[rid] = (d, code)
    return seen, dupes


def perm_p(obs, flags, cited, seeds=(0, 1, 2), draws=5000):
    """Two-sided permutation p on Delta, pooled over seeds. Destroys the pairing only."""
    n_hi = 0
    tot = 0
    for s in seeds:
        rng = random.Random(s)
        f = list(flags)
        for _ in range(draws):
            rng.shuffle(f)
            if abs(delta(f, cited)) >= abs(obs) - 1e-12:
                n_hi += 1
            tot += 1
    return (n_hi + 1) / (tot + 1), tot


def delta(flags, cited):
    a = [c for f, c in zip(flags, cited) if f]          # codeless
    b = [c for f, c in zip(flags, cited) if not f]      # has code
    if not a or not b:
        return 0.0
    return sum(a) / len(a) - sum(b) / len(b)


def main():
    R, dupes = rounds()
    if not R:
        print("UNRUNNABLE: no rounds enumerated. Exit 2, never 0.")
        return 2
    text = STMT.read_text()
    cited_ids = {int(x) for x in re.findall(r"R(\d{3})", text)}

    ids = sorted(R)
    flags = [not R[i][1] for i in ids]                  # True = persists NO code
    cited = [1 if i in cited_ids else 0 for i in ids]
    n, n_codeless, n_cited = len(ids), sum(flags), sum(cited)
    if dupes:
        print(f"  ⚠ DUPLICATE ROUND IDS ({len(dupes)}), P16 requires them globally unique:")
        for rid, a, b in dupes[:8]:
            print(f"      R{rid}: {a}  ||  {b}")
    print(f"CORPUS  rounds={n}  persisting code={n - n_codeless}  CODELESS={n_codeless} "
          f"({n_codeless / n:.1%})   cited by STATEMENT.md={n_cited}")
    if n_cited == 0 or n_codeless == 0:
        print("UNRUNNABLE: a marginal is empty; Delta is undefined. Exit 2.")
        return 2

    # ---------------- CONTROLS FIRST. The verdict is a function of them. --------------
    obs = delta(flags, cited)
    p_codeless = sum(c for f, c in zip(flags, cited) if f) / n_codeless
    p_code = sum(c for f, c in zip(flags, cited) if not f) / (n - n_codeless)
    print(f"\n─── DERIVATION (a count, not a test) ───")
    print(f"  P(cited | codeless)  = {p_codeless:.4f}   ({sum(c for f,c in zip(flags,cited) if f)}/{n_codeless})")
    print(f"  P(cited | has code)  = {p_code:.4f}   "
          f"({sum(c for f,c in zip(flags,cited) if not f)}/{n - n_codeless})")
    print(f"  Delta                = {obs:+.4f}   <- forced by the four counts above")

    print(f"\n─── CONTROLS ───")
    p_obs, tot = perm_p(obs, flags, cited)
    print(f"  NEGATIVE (permutation null, 3 seeds x 5000): p = {p_obs:.4f}  over {tot} draws "
          f"(resolution floor {1/(tot+1):.5f})")

    # POSITIVE: plant enrichment by forcing the most-cited rounds codeless
    cite_count = {i: len(re.findall(rf"R{i:03d}\b", text)) for i in ids}
    k = n_codeless
    planted_ids = set(sorted(ids, key=lambda i: -cite_count[i])[:k])
    planted = [i in planted_ids for i in ids]
    d_plant = delta(planted, cited)
    p_plant, _ = perm_p(d_plant, planted, cited)
    print(f"  POSITIVE (plant: the {k} most-cited rounds forced codeless): "
          f"Delta={d_plant:+.4f}  p={p_plant:.4f}  "
          f"-> {'PASS' if p_plant < 0.05 else '⛔ FAIL (design cannot detect world B at all)'}")

    # POSITIVE @ g=0: no planting must reproduce the observed statistic exactly
    d_g0 = delta(list(flags), cited)
    g0_ok = abs(d_g0 - obs) < 1e-12
    print(f"  POSITIVE @ g=0 (nothing planted): Delta={d_g0:+.4f} vs observed {obs:+.4f} "
          f"-> {'PASS (can fail)' if g0_ok else '⛔ the plant leaks into the null arm'}")

    # MDE: smallest planted enrichment this design resolves, by dose-response
    mde, doses = None, []
    for frac in (0.05, 0.10, 0.20, 0.30, 0.50, 0.75, 1.00):
        kk = max(1, int(k * frac))
        pl = set(sorted(ids, key=lambda i: -cite_count[i])[:kk])
        # keep the codeless marginal fixed: top-up with random non-planted rounds
        rng = random.Random(0)
        rest = [i for i in ids if i not in pl]
        pl |= set(rng.sample(rest, k - len(pl)))
        fl = [i in pl for i in ids]
        d = delta(fl, cited)
        pp, _ = perm_p(d, fl, cited, seeds=(0,), draws=2000)
        doses.append((frac, round(d, 4), round(pp, 4)))
        if mde is None and pp < 0.05:
            mde = (frac, d)
    print(f"  DOSE-RESPONSE (frac of the codeless slots given to the most-cited rounds):")
    for f_, d_, p_ in doses:
        print(f"    {f_:>5.0%}  Delta={d_:+.4f}  p={p_:.4f}{'   <- MDE' if mde and f_ == mde[0] else ''}")
    print(f"  MDE = {'Delta ' + format(mde[1], '+.4f') + f' (at {mde[0]:.0%} planting)' if mde else 'NOT REACHED at 100% planting'}")

    # PLACEBO: a coin flip at the same marginal must return ~0
    plc = []
    for s in (0, 1, 2):
        rng = random.Random(100 + s)
        f = [False] * n
        for i in rng.sample(range(n), n_codeless):
            f[i] = True
        plc.append(delta(f, cited))
    plc_ok = all(abs(x) < abs(d_plant) for x in plc)
    print(f"  PLACEBO (random flag, same marginal, 3 seeds): "
          f"{[round(x, 4) for x in plc]} -> {'PASS' if plc_ok else '⛔ FAIL'}")

    controls_fired = (p_plant < 0.05) and g0_ok and plc_ok

    # ---------------- VERDICT: a function of the controls, nothing written between ----
    # ---- IS THE CODELESSNESS TEMPORAL RATHER THAN CITATIONAL? ---------------
    # 8 of the 8 cited-and-codeless rounds sit above R444. Before reading Delta as a
    # statement about CITATION, test the rival that explains it with one variable: the
    # practice decayed, and recent rounds are BOTH more codeless and more cited.
    codeless_ids = [i for i, f in zip(ids, flags) if f]
    med_all, med_cl = sorted(ids)[len(ids) // 2], sorted(codeless_ids)[len(codeless_ids) // 2]
    late = [i for i in ids if i > med_all]
    rate_late = sum(1 for i in late if not R[i][1]) / len(late)
    rate_early = sum(1 for i in ids if i <= med_all and not R[i][1]) / (len(ids) - len(late))
    n_hi = 0
    for s in (0, 1, 2):
        rng = random.Random(200 + s)
        for _ in range(5000):
            f = [False] * n
            for j in rng.sample(range(n), n_codeless):
                f[j] = True
            if sorted(i for i, x in zip(ids, f) if x)[n_codeless // 2] >= med_cl:
                n_hi += 1
    p_time = (n_hi + 1) / (15000 + 1)
    print(f"\n─── RIVAL: is codelessness TEMPORAL? ───")
    print(f"  median round id  all={med_all}  codeless={med_cl}")
    print(f"  codeless rate    early half={rate_early:.4f}   late half={rate_late:.4f}   "
          f"ratio={rate_late / rate_early if rate_early else float('inf'):.2f}x")
    print(f"  permutation p on the codeless median being this LATE: {p_time:.4f}")

    # STRONGEST CONFOUND, written before the run: recent rounds are BOTH more codeless AND
    # more cited (STATEMENT.md was written in the R451-559 era), so the citation Delta may be
    # entirely a shadow of the time trend. Stratify -- recompute Delta inside the late half,
    # where the time variable is held roughly fixed.
    li = [j for j, i in enumerate(ids) if i > med_all]
    f_late = [flags[j] for j in li]
    c_late = [cited[j] for j in li]
    d_late = delta(f_late, c_late)
    p_late, _ = perm_p(d_late, f_late, c_late)
    print(f"  STRATIFIED (late half only, n={len(li)}, codeless={sum(f_late)}, "
          f"cited={sum(c_late)}): Delta={d_late:+.4f}  p={p_late:.4f}")
    print(f"    -> the time trend {'DOES NOT explain' if p_late < 0.05 else 'CANNOT BE RULED OUT as'} "
          f"the citation gap")

    print(f"\n─── VERDICT ───")
    under_powered = mde is not None and abs(obs) < abs(mde[1])
    if not controls_fired:
        world, why = "UNVERIFIED", "a control did not fire; no concentration claim is admissible"
    elif under_powered:
        world, why = ("UNDER-POWERED",
                      f"|Delta|={abs(obs):.4f} is BELOW this design's own MDE "
                      f"({abs(mde[1]):.4f}); p={p_obs:.4f} is silence, not an acquittal. "
                      f"Worlds A and B are BOTH still live at this effect size.")
    elif p_obs >= 0.05:
        world, why = "A INCIDENTAL", f"p={p_obs:.4f} >= 0.05 -- inside the permutation null"
    elif obs > 0:
        world, why = "B LOAD-BEARING", f"codeless rounds are ENRICHED among cited, p={p_obs:.4f}"
    else:
        world, why = "C PROTECTED", f"codeless rounds are DEPLETED among cited, p={p_obs:.4f}"
    print(f"  {world} -- {why}")

    # which cited rounds are codeless, named -- the actionable residue either way
    exposed = sorted(i for i in ids if i in cited_ids and not R[i][1])
    print(f"\n  CITED AND CODELESS ({len(exposed)} of {n_cited} cited): {exposed}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "codeless.json").write_text(json.dumps({
        "world": world, "why": why,
        "n_rounds": n, "n_codeless": n_codeless, "n_cited": n_cited,
        "p_cited_given_codeless": p_codeless, "p_cited_given_code": p_code,
        "delta": obs, "delta_is": "DERIVATION -- forced by four counts; only p is tested",
        "perm_p": p_obs, "perm_draws": tot,
        "pos_plant_delta": d_plant, "pos_plant_p": p_plant, "pos_g0_ok": g0_ok,
        "dose_response": doses, "mde": mde,
        "placebo": plc, "controls_fired": controls_fired,
        "under_powered": under_powered,
        "temporal_rival": {"median_all": med_all, "median_codeless": med_cl,
                           "rate_early": rate_early, "rate_late": rate_late,
                           "p_codeless_median_this_late": p_time,
                           "stratified_late_delta": d_late,
                           "stratified_late_p": p_late,
                           "stratified_n": len(li)},
        "cited_and_codeless": exposed,
        "upper_bound_note": ("persisting code is NECESSARY and NOT SUFFICIENT for a later "
                             "round to attack the instrument; this is an upper bound on "
                             "attackability, never a measurement of it"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'codeless.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
