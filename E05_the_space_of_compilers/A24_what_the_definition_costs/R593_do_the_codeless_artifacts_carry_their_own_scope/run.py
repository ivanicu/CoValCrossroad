#!/usr/bin/env python3
"""
R593 -- do the codeless rounds' artifacts carry their own scope?

R592 left 8 codeless rounds cited by the deliverable and asked whether each artifact is
"internally sufficient to state its claim". CHECK #193 REFUSED THAT WORDING: sufficiency is
not measurable as written, and scoring it would mean inventing a rubric and grading against my
own imagination -- §4's `control validated on imagined cases`, which is the failure this whole
arc keeps re-committing in new clothes.

The fix is to STOP INVENTING THE RUBRIC. The corpus already has a convention: whatever keys
the 555 CODE-BEARING rounds actually put in their artifacts. Derive the vocabulary from THEM
(never from the group under test, which would be circular), then ask whether the codeless
rounds honour it.

⚠ AND THE CONFOUND IS ALREADY KNOWN. R592 measured the codeless rounds to be 13.6x
concentrated in the late half (p = 0.0001). Any raw comparison here repeats that error, so the
time-stratified contrast is computed in the SAME iteration and is the one the verdict reads.

ESTIMAND        Delta_meta = E[convention-key coverage | codeless]
                           - E[convention-key coverage | code-bearing],
                where coverage = |round's top-level keys INTERSECT convention| / |convention|.
IDENTIFICATION  Estimable: every round's artifact is on disk and the convention is derived
                from a disjoint group. ⚠ PARTIAL for the 8 cited codeless rounds specifically
                -- n=8 is far below what any of these nulls resolve, so that subgroup gets a
                BOUND and a named MDE, never a point.
SCOPE           population : all rounds in E01..E05 with >=1 results/*.json
                instrument : top-level JSON key sets. The unit is A KEY THE ARTIFACT DECLARES;
                             the claim's unit is ALSO a key the artifact declares. Written as
                             two strings and equal -- the check §4 demands before the control.
                baseline   : the code-bearing rounds' own key convention (>=20% prevalence)
                regime     : as committed at this sha
WORLDS          A COMPENSATED: codeless artifacts carry MORE convention keys -- the author knew
                  the code was absent and pushed the scope into the artifact. Claims stay
                  attackable and the R592 worry is answered.
                B DOUBLY THIN: codeless artifacts carry FEWER -- the claim has no carrier on
                  either channel and lives only in README prose.
                C THE ARTIFACT WAS NEVER THE CARRIER: coverage is uniformly low in BOTH groups
                  -- then "codeless" was the wrong variable and the README is the carrier
                  everywhere. An ontology shift, not a score.
KILL            pre-registered, evaluated ONLY if the controls fire: the TIME-STRATIFIED
                permutation p >= 0.05 -> no group difference is admissible, and the verdict
                falls to whichever of A/B/C the ABSOLUTE coverage levels support.
POSITIVE CTRL   plant: strip the convention keys from k random code-bearing rounds and relabel
                them codeless. Must recover world B. Fails at g=0 (no stripping -> statistic
                equals the observed one). Dose-response gives the MDE.
NEGATIVE CTRL   permutation of the codeless label WITHIN time strata -- destroys the pairing
                while preserving both marginals AND the time distribution.
PLACEBO         a random group flag at the same marginal; must return ~0.
SEEDS           0, 1, 2 everywhere.
ARTIFACT        results/scope_carriage.json
IMPOSSIBLE      construct validity for "attackable": key PRESENCE is not key CONTENT -- a
                round can write "world": "B" and mean nothing by it. Establishing that would
                need an external reader scoring each artifact against its own README, i.e. a
                gold standard this site does not have. Every number here bounds attackability
                from ABOVE and is reported as one.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
STMT = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"
OUT = pathlib.Path(__file__).resolve().parent / "results"
CODE_SUFFIX = (".py", ".sh")
PREVALENCE = 0.20


def walk_keys(o):
    """Every key at EVERY depth. The top-level-only view is a specification CHOICE, and a
    round that nests its scope one level down would be scored as carrying none."""
    if isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from walk_keys(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk_keys(v)


def survey():
    """round-id -> (has_code, top-level keys, all-depth keys)."""
    out = {}
    for ep in sorted(ROOT.glob("E0*")):
        for d in sorted(ep.glob("A*/R[0-9]*")):
            if not d.is_dir():
                continue
            m = re.match(r"R(\d+)", d.name)
            if not m:
                continue
            keys, deep = set(), set()
            res = d / "results"
            if res.is_dir():
                for f in sorted(res.rglob("*.json")):
                    try:
                        o = json.loads(f.read_text())
                    except Exception:
                        continue
                    if isinstance(o, dict):
                        keys |= {str(k).lower() for k in o}
                    deep |= {str(k).lower() for k in walk_keys(o)}
            if not keys and not deep:
                continue
            has_code = any(f.suffix in CODE_SUFFIX for f in d.iterdir() if f.is_file())
            out[int(m.group(1))] = (has_code, keys, deep)
    return out


def coverage(keys, conv):
    return len(keys & conv) / len(conv) if conv else 0.0


def strat_perm(labels, scores, strata, obs, seeds=(0, 1, 2), draws=4000):
    """Permute the label WITHIN each time stratum. Preserves marginals AND the time trend."""
    by = {}
    for i, s in enumerate(strata):
        by.setdefault(s, []).append(i)
    hi = tot = 0
    for sd in seeds:
        rng = random.Random(sd)
        lab = list(labels)
        for _ in range(draws):
            for idxs in by.values():
                vals = [lab[i] for i in idxs]
                rng.shuffle(vals)
                for i, v in zip(idxs, vals):
                    lab[i] = v
            d = gap(lab, scores)
            if abs(d) >= abs(obs) - 1e-12:
                hi += 1
            tot += 1
    return (hi + 1) / (tot + 1), tot


def gap(labels, scores):
    a = [s for l, s in zip(labels, scores) if l]
    b = [s for l, s in zip(labels, scores) if not l]
    if not a or not b:
        return 0.0
    return sum(a) / len(a) - sum(b) / len(b)


def analyse(S, ids, codeless, n, k, di, depth_name):
    """One full analysis at one DEPTH specification. Called for every cell of the curve --
    the depth choice is a specification axis, not a setting, and reporting one cell would be
    G4's failure at the scale of this round."""
    print(f"\n{'='*78}\nSPECIFICATION: {depth_name} keys\n{'='*78}")
    # ---- the convention, derived from the CODE-BEARING group only (never circular) ----
    base = [i for i in ids if S[i][0]]
    freq = {}
    for i in base:
        for kk in S[i][di]:
            freq[kk] = freq.get(kk, 0) + 1
    conv = {kk for kk, c in freq.items() if c / len(base) >= PREVALENCE}
    print(f"\n─── THE CONVENTION (keys in >={PREVALENCE:.0%} of the {len(base)} CODE-BEARING "
          f"rounds; the group under test contributed nothing to it) ───")
    for kk in sorted(conv, key=lambda x: -freq[x]):
        print(f"    {kk:<24} {freq[kk]:>4}/{len(base)} = {freq[kk]/len(base):.2f}")
    if not conv:
        print("UNRUNNABLE: the corpus has no shared key convention; the estimand is undefined.")
        return 2

    scores = [coverage(S[i][di], conv) for i in ids]
    strata = [min(4, (i * 5) // (max(ids) + 1)) for i in ids]   # 5 equal round-id bands
    obs_raw = gap(codeless, scores)
    mean_cl = sum(s for c, s in zip(codeless, scores) if c) / k
    mean_cb = sum(s for c, s in zip(codeless, scores) if not c) / (n - k)

    print(f"\n─── DERIVATION (means over a complete enumeration; only p is tested) ───")
    print(f"  coverage | codeless     = {mean_cl:.4f}   (n={k})")
    print(f"  coverage | code-bearing = {mean_cb:.4f}   (n={n-k})")
    print(f"  Delta_raw               = {obs_raw:+.4f}")

    # ---- CONTROLS FIRST. Nothing is written between them and the verdict. ------------
    print(f"\n─── CONTROLS ───")
    p_raw, _ = strat_perm(codeless, scores, [0] * n, obs_raw)          # unstratified
    p_str, tot = strat_perm(codeless, scores, strata, obs_raw)         # time-stratified
    print(f"  NEGATIVE unstratified : p = {p_raw:.4f}")
    print(f"  NEGATIVE time-stratified (5 bands, {tot} draws, floor {1/(tot+1):.5f}): "
          f"p = {p_str:.4f}   <- the one the verdict reads (R592: codeless is 13.6x late)")

    # POSITIVE: strip the convention from k code-bearing rounds and call them codeless
    rng = random.Random(0)
    planted_ids = set(rng.sample(base, k))
    sc_p = [0.0 if i in planted_ids else coverage(S[i][di], conv) for i in ids]
    lab_p = [i in planted_ids for i in ids]
    d_plant = gap(lab_p, sc_p)
    p_plant, _ = strat_perm(lab_p, sc_p, strata, d_plant)
    print(f"  POSITIVE (convention stripped from {k} random code-bearing rounds): "
          f"Delta={d_plant:+.4f}  p={p_plant:.4f}  "
          f"-> {'PASS' if p_plant < 0.05 else '⛔ FAIL -- the design cannot see world B at all'}")
    d_g0 = gap(codeless, scores)
    g0_ok = abs(d_g0 - obs_raw) < 1e-12
    print(f"  POSITIVE @ g=0 (nothing stripped): Delta={d_g0:+.4f} vs observed {obs_raw:+.4f} "
          f"-> {'PASS (can fail)' if g0_ok else '⛔ the plant leaks into the null arm'}")

    mde, doses = None, []
    for frac in (0.10, 0.25, 0.50, 0.75, 1.00):
        rr = random.Random(1)
        strip = set(rr.sample(sorted(planted_ids), max(1, int(k * frac))))
        sc = [0.0 if i in strip else coverage(S[i][di], conv) for i in ids]
        d = gap(lab_p, sc)
        pp, _ = strat_perm(lab_p, sc, strata, d, seeds=(0,), draws=1500)
        doses.append((frac, round(d, 4), round(pp, 4)))
        if mde is None and pp < 0.05:
            mde = (frac, d)
    print(f"  DOSE-RESPONSE (fraction of the planted arm actually stripped):")
    for f_, d_, p_ in doses:
        print(f"    {f_:>5.0%}  Delta={d_:+.4f}  p={p_:.4f}"
              f"{'   <- MDE' if mde and f_ == mde[0] else ''}")
    print(f"  MDE = {'|Delta| ' + format(abs(mde[1]), '.4f') if mde else 'NOT REACHED at 100% stripping'}")

    plc = []
    for sd in (0, 1, 2):
        rr = random.Random(300 + sd)
        f = [False] * n
        for j in rr.sample(range(n), k):
            f[j] = True
        plc.append(gap(f, scores))
    plc_ok = all(abs(x) < abs(d_plant) for x in plc)
    print(f"  PLACEBO (random flag, same marginal, 3 seeds): {[round(x,4) for x in plc]} "
          f"-> {'PASS' if plc_ok else '⛔ FAIL'}")

    controls_fired = (p_plant < 0.05) and g0_ok and plc_ok
    # ⛔ v1 SET `under_powered = |obs| < |mde|` AND THAT COMPARISON IS MALFORMED.
    # The dose-response MDE is the resolution for a CONCENTRATED plant -- scores forced to
    # 0.0 in a random subset -- while the observed contrast is spread across the group. Two
    # different variance structures compared as though they were one object: §4's `the
    # control fails for its own reasons`, form ①. The observed effect has its OWN test, the
    # stratified permutation, and that is the only admissible one for it. The plant MDE is
    # kept and reported because it bounds what a CONCENTRATED defect would need to be seen.
    mde_is_for = "a concentrated plant, NOT comparable to the spread observed contrast"
    under_powered = None

    # ---- VERDICT: a function of the controls, with nothing written in between ---------
    # ⛔ v1 CHAINED A/B/C WITH `elif` AND THE WORLD SET IS NOT A PARTITION. C is about the
    # ABSOLUTE level; A and B are about the DIFFERENCE. They are orthogonal axes, so the
    # chain let C shadow a second answer that was also true and also resolved. Both axes are
    # now computed and both are reported.
    print(f"\n─── VERDICT (two orthogonal axes -- the world set was never a partition) ───")
    lowish = max(mean_cl, mean_cb) < 0.5
    axis_level = ("C THE ARTIFACT WAS NEVER THE CARRIER" if lowish
                  else "the artifact IS a carrier in at least one group")
    if not controls_fired:
        axis_diff, tag_diff = "UNVERIFIED -- a control did not fire", "UNVERIFIED"
    elif p_str >= 0.05:
        axis_diff, tag_diff = f"NO GROUP DIFFERENCE -- time-stratified p={p_str:.4f}", "NONE"
    elif obs_raw > 0:
        axis_diff, tag_diff = f"A COMPENSATED -- codeless carry MORE, p={p_str:.4f}", "A"
    else:
        axis_diff, tag_diff = f"B DOUBLY THIN -- codeless carry FEWER, p={p_str:.4f}", "B"
    world = axis_level if not controls_fired else f"{axis_level}  AND  {axis_diff}"
    why = (f"level: {mean_cl:.4f} vs {mean_cb:.4f} against a convention whose most common key "
           f"reaches only {max(freq[k_] for k_ in conv)/len(base):.2f} prevalence; "
           f"difference: Delta={obs_raw:+.4f}, stratified p={p_str:.4f} over {tot} draws")
    print(f"  {world} -- {why}")

    # ---- the 8 cited codeless rounds, named, with their own resolution stated --------
    cited_ids = {int(x) for x in re.findall(r"R(\d{3})", STMT.read_text())}
    focus = sorted(i for i in ids if not S[i][0] and i in cited_ids)
    print(f"\n─── THE {len(focus)} CITED CODELESS ROUNDS (n far below any null here: a BOUND, "
          f"never a point) ───")
    for i in focus:
        have = sorted(S[i][di] & conv)
        print(f"  R{i}  coverage={coverage(S[i][di], conv):.4f}  convention keys present: "
              f"{have if have else '(none)'}")
    fm = (sum(coverage(S[i][di], conv) for i in focus) / len(focus)) if focus else None
    if fm is not None:
        print(f"  mean coverage over the {len(focus)} = {fm:.4f}  vs corpus {mean_cb:.4f} "
              f"(code-bearing).  MDE of this design = "
              f"{format(abs(mde[1]), '.4f') if mde else 'unreached'} -- "
              f"n={len(focus)} resolves nothing below it.")


    return {
        "depth": depth_name, "world": world, "why": why,
        "convention": sorted(conv), "convention_prevalence_floor": PREVALENCE,
        "mean_coverage_codeless": mean_cl, "mean_coverage_codebearing": mean_cb,
        "delta_raw": obs_raw, "delta_is": "DERIVATION over a complete enumeration",
        "p_unstratified": p_raw, "p_time_stratified": p_str, "perm_draws": tot,
        "pos_plant_delta": d_plant, "pos_plant_p": p_plant, "pos_g0_ok": g0_ok,
        "dose_response": doses, "mde": mde, "mde_is_for": mde_is_for,
        "axis_level": axis_level, "axis_difference": axis_diff,
        "tag": f"{'C' if lowish else 'carrier'}+{tag_diff}",
        "max_convention_prevalence": max(freq[k_] for k_ in conv) / len(base),
        "placebo": plc, "controls_fired": controls_fired,
        "cited_codeless": {str(i): {"coverage": coverage(S[i][di], conv),
                                    "keys": sorted(S[i][di] & conv)} for i in focus},
        "cited_codeless_mean": fm,
    }


def main():
    S = survey()
    if not S:
        print("UNRUNNABLE: no round shipped a readable JSON artifact. Exit 2, never 0.")
        return 2
    ids = sorted(S)
    codeless = [not S[i][0] for i in ids]
    n, k = len(ids), sum(codeless)
    print(f"CORPUS  rounds with a readable JSON artifact = {n}   codeless among them = {k}")
    if k == 0 or k == n:
        print("UNRUNNABLE: a marginal is empty. Exit 2.")
        return 2

    cells = [analyse(S, ids, codeless, n, k, di, nm)
             for nm, di in (("top-level", 1), ("all-depth", 2))]

    print(f"\n{'='*78}\nSPECIFICATION CURVE -- both cells, including any that kills the finding\n{'='*78}")
    print(f"{'depth':>12} {'|conv|':>7} {'cl':>8} {'cb':>8} {'Delta':>9} {'p_strat':>9} "
          f"{'MDE':>8}  verdict")
    for c in cells:
        print(f"{c['depth']:>12} {len(c['convention']):>7} {c['mean_coverage_codeless']:>8.4f} "
              f"{c['mean_coverage_codebearing']:>8.4f} {c['delta_raw']:>+9.4f} "
              f"{c['p_time_stratified']:>9.4f} "
              f"{(abs(c['mde'][1]) if c['mde'] else float('nan')):>8.4f}  {c['world']}")
    # ⛔ v1 compared c["world"], a formatted string with the p-value interpolated into
    # it -- so two IDENTICAL conclusions could never compare equal. Third unit mismatch
    # in this round alone. Compare the number-free tag.
    agree = len({c["tag"] for c in cells}) == 1
    print(f"\n  SPEC SURVIVAL: {'both cells agree' if agree else 'THE CELLS DISAGREE -- the '
          'depth choice IS the finding, and neither cell may be quoted alone'}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "scope_carriage.json").write_text(json.dumps({
        "world": cells[0]["world"] if agree else "SPEC-DEPENDENT",
        "spec_agree": agree, "n_rounds": n, "n_codeless": k, "cells": cells,
        "upper_bound_note": ("key PRESENCE is not key CONTENT; a round can write world: B and "
                             "mean nothing by it. Every number bounds attackability from above"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'scope_carriage.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
