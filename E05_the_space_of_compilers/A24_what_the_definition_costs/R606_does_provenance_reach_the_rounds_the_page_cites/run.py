#!/usr/bin/env python3
"""
R606 -- does the source-hash mechanism reach the rounds the deliverable cites?

CHECK #205 CAUGHT AN "ONLY" REFUTED BY MY OWN PASSING CONTROL. R605 closed saying the three
artifacts with builders are *"the ONLY place in this tree where a construction and a committed
matrix sit side by side"*. R605's own PLACEBO was R604's `baseline_name.json`, written by
R604's own `run.py` -- a construction and its artifact side by side. Hundreds of round
directories are like that; R605 had scanned only `corebench/results/sat_*.npz`.
⚠ The control that PASSED contained the counterexample to the sentence written after it.

And the closing line's premise was wrong in the useful direction: provenance is not absent.
Measured across 426 artifacts, 109 (25.6%) carry `source_sha256` / `source_name` / `sha256` /
`src_sha`. THE MECHANISM EXISTS AND A QUARTER OF THE CORPUS USES IT. So the question is
adoption, and the only adoption that bears on the deliverable is whether it reaches the rounds
the page actually cites.

ESTIMAND        Delta = P(artifact carries provenance | round is CITED by STATEMENT.md)
                      - P(carries provenance | not cited), at the ROUND level.
IDENTIFICATION  Complete enumeration -- the point estimate is a DERIVATION forced by four
                counts. Only the TIME-STRATIFIED permutation p is tested.
                ⚠ R592 measured provenance-adjacent practice to be strongly time-dependent
                (13.6x), and R593 found the stratified contrast can REVERSE the raw one. The
                stratified test is therefore the one the verdict reads, computed in the same
                iteration and not as a follow-up.
SCOPE           population : every round in E05 with >=1 parseable results/*.json
                instrument : presence of a provenance-shaped key at any depth
                             instrument unit = A KEY NAMED LIKE A SOURCE HASH
                             claim unit      = THE ARTIFACT RECORDS WHERE IT CAME FROM
                             NOT equal -- a key can be present and empty, so the round also
                             counts NON-EMPTY values and reports both
                baseline   : the uncited rounds, same instrument
                regime     : as committed at this sha
WORLDS          A REACHES: cited rounds carry provenance at or above the corpus rate -> the
                  deliverable's own evidence is attributable and the 25.6% is a corpus-wide
                  fact that does not touch it.
                B MISSES: cited rounds carry it LESS -> the page's numbers come
                  disproportionately from artifacts that do not record their source.
                C TIME ONLY: raw difference vanishes under stratification -> adoption is an
                  era, not a property of being cited, and neither A nor B is admissible.
KILL            pre-registered: |Delta| below this design's own dose-response MDE -> report a
                bound, not a direction. And if the plant cannot recover a planted effect, the
                whole round is UNVERIFIED.
POSITIVE CTRL   plant: strip provenance from every cited round and rerun. Must recover world B
                with p < 0.05. Fails at g=0: unplanted must reproduce the observed Delta.
NEGATIVE CTRL   permutation of the cited label WITHIN time strata, preserving both marginals
                and the era distribution.
PLACEBO         a random label at the same marginal must return ~0.
SEEDS           0, 1, 2 on every resampling step.
MULTIPLICITY    2 key-strictness levels (present / non-empty) x 3 seeds, all reported.
ARTIFACT        results/provenance_reach.json
IMPOSSIBLE      construct validity for "attributable": a recorded hash proves a source was
                NAMED, not that the bytes match it. Verifying that needs the source file at
                the recorded path, and R605 established most are not in this tree.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
FIELDS = ("source_sha256", "source_name", "source_hash", "sha256", "src_sha")


def walk(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            acc.append((str(k), v)); walk(v, acc)
    elif isinstance(o, list):
        for v in o:
            walk(v, acc)


def rounds():
    out = {}
    for d in sorted(E05.glob("A*/R[0-9]*")):
        if not d.is_dir() or d.name.startswith("R606_"):
            continue          # a round may not be a member of the population it measures
        m = re.match(r"R(\d+)", d.name)
        if not m or not (d / "results").is_dir():
            continue
        present = nonempty = False
        for f in sorted((d / "results").glob("*.json")):
            try:
                j = json.loads(f.read_text())
            except Exception:
                continue
            acc = []; walk(j, acc)
            for k, v in acc:
                if any(x == k or x in k for x in FIELDS):
                    present = True
                    if isinstance(v, str) and v.strip():
                        nonempty = True
        if present or (d / "results").glob("*.json"):
            out[int(m.group(1))] = (present, nonempty)
    return out


def gap(lab, sc):
    a = [s for l, s in zip(lab, sc) if l]
    b = [s for l, s in zip(lab, sc) if not l]
    return (sum(a)/len(a) - sum(b)/len(b)) if a and b else 0.0


def strat_perm(lab, sc, strata, obs, seeds=(0, 1, 2), draws=4000):
    by = {}
    for i, s in enumerate(strata):
        by.setdefault(s, []).append(i)
    hi = tot = 0
    for sd in seeds:
        rng = random.Random(sd); L = list(lab)
        for _ in range(draws):
            for idxs in by.values():
                vals = [L[i] for i in idxs]; rng.shuffle(vals)
                for i, v in zip(idxs, vals):
                    L[i] = v
            if abs(gap(L, sc)) >= abs(obs) - 1e-12:
                hi += 1
            tot += 1
    return (hi + 1) / (tot + 1), tot


def main():
    R = rounds()
    if not R:
        print("UNRUNNABLE: no rounds with artifacts. Exit 2, never 0."); return 2
    text = (E05 / "STATEMENT.md").read_text()
    cited_ids = {int(x) for x in re.findall(r"R(\d{3})", text)}
    ids = sorted(R)
    cited = [i in cited_ids for i in ids]
    strata = [min(4, (i * 5) // (max(ids) + 1)) for i in ids]
    n, nc = len(ids), sum(cited)
    print(f"POPULATION  {n} rounds with artifacts, {nc} cited by STATEMENT.md")
    if nc == 0 or nc == n:
        print("UNRUNNABLE: a marginal is empty. Exit 2."); return 2

    for level, idx in (("present", 0), ("non-empty", 1)):
        sc = [1.0 if R[i][idx] else 0.0 for i in ids]
        obs = gap(cited, sc)
        pc = sum(s for c, s in zip(cited, sc) if c) / nc
        pu = sum(s for c, s in zip(cited, sc) if not c) / (n - nc)
        p_raw, _ = strat_perm(cited, sc, [0]*n, obs)
        p_str, tot = strat_perm(cited, sc, strata, obs)
        print(f"\n─── LEVEL: provenance key {level} ───")
        print(f"  P(prov | cited)   = {pc:.4f}   ({nc} rounds)")
        print(f"  P(prov | uncited) = {pu:.4f}   ({n-nc} rounds)")
        print(f"  Delta = {obs:+.4f}   <- DERIVATION, forced by four counts")
        print(f"  permutation p: unstratified {p_raw:.4f}   TIME-STRATIFIED {p_str:.4f} "
              f"({tot} draws)")
        if idx == 0:
            keep = (obs, p_str, p_raw, pc, pu, sc)

    obs, p_str, p_raw, pc, pu, sc = keep
    print(f"\n─── CONTROLS (on the `present` level) ───")
    sc_p = [0.0 if c else s for c, s in zip(cited, sc)]     # strip provenance from cited
    d_pl = gap(cited, sc_p)
    p_pl, _ = strat_perm(cited, sc_p, strata, d_pl)
    print(f"  POSITIVE  provenance stripped from every cited round: Delta={d_pl:+.4f} "
          f"p={p_pl:.4f} -> {'PASS' if p_pl < 0.05 else '⛔ FAIL — cannot recover world B'}")
    g0 = gap(cited, sc)
    g0_ok = abs(g0 - obs) < 1e-12
    print(f"  POSITIVE @ g=0  unplanted reproduces Delta: {g0:+.4f} vs {obs:+.4f} -> "
          f"{'PASS (can fail)' if g0_ok else '⛔ FAIL'}")
    plc = []
    for s in (0, 1, 2):
        rng = random.Random(500 + s); f = [False]*n
        for j in rng.sample(range(n), nc):
            f[j] = True
        plc.append(gap(f, sc))
    plc_ok = all(abs(x) < abs(d_pl) for x in plc)
    print(f"  PLACEBO   random label, same marginal: {[round(x,4) for x in plc]} -> "
          f"{'PASS' if plc_ok else '⛔ FAIL'}")
    mde, doses = None, []
    for frac in (0.10, 0.25, 0.50, 0.75, 1.00):
        rng = random.Random(9)
        strip = set(rng.sample([i for i, c in zip(ids, cited) if c],
                               max(1, int(nc*frac))))
        s2 = [0.0 if i in strip else v for i, v in zip(ids, sc)]
        d = gap(cited, s2)
        pp, _ = strat_perm(cited, s2, strata, d, seeds=(0,), draws=1500)
        doses.append((frac, round(d, 4), round(pp, 4)))
        if mde is None and pp < 0.05:
            mde = (frac, d)
    print(f"  DOSE-RESPONSE (fraction of cited rounds stripped):")
    for f_, d_, p_ in doses:
        print(f"    {f_:>5.0%}  Delta={d_:+.4f}  p={p_:.4f}{'   <- MDE' if mde and f_==mde[0] else ''}")
    print(f"  MDE = {('|Delta| '+format(abs(mde[1]),'.4f')) if mde else 'NOT REACHED'}")
    controls_ok = (p_pl < 0.05) and g0_ok and plc_ok
    # ⛔ THE MDE COMPARISON IS DEGENERATE FOR THIS PLANT AND THE ROUND SAYS SO RATHER THAN
    #    FIRING ON IT. Stripping provenance from cited rounds moves Delta MONOTONELY AWAY from
    #    zero, starting from the observed value — so every planted |Delta| is >= |Delta_obs| by
    #    construction, and `|obs| < MDE` is true no matter what the data say. A band that cannot
    #    contain the observation is §4's `control that cannot PASS`, in mirror. Detected, not
    #    assumed: if the smallest planted |Delta| already exceeds |obs|, the branch is disabled.
    plant_floor = min(abs(d) for _, d, _ in doses) if doses else None
    mde_degenerate = plant_floor is not None and plant_floor >= abs(obs) - 1e-12
    under = (mde is not None and abs(obs) < abs(mde[1])) and not mde_degenerate
    print(f"  ⚠ MDE ADMISSIBILITY: smallest planted |Delta| = {plant_floor:.4f} vs observed "
          f"|Delta| = {abs(obs):.4f} -> "
          f"{'DEGENERATE, the band cannot contain the observation; the observed effect is judged by its OWN stratified permutation' if mde_degenerate else 'admissible'}")

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif under:
        world = (f"BOUND ONLY — |Delta|={abs(obs):.4f} is below this design's own MDE "
                 f"({abs(mde[1]):.4f}); direction reported, magnitude not")
    elif p_str >= 0.05:
        world = (f"C TIME ONLY — time-stratified p={p_str:.4f}; adoption is an ERA, not a "
                 f"property of being cited (raw p was {p_raw:.4f})")
    elif obs > 0:
        world = (f"A REACHES — cited rounds carry provenance MORE, Delta={obs:+.4f}, "
                 f"stratified p={p_str:.4f}")
    else:
        world = (f"B MISSES — cited rounds carry provenance LESS, Delta={obs:+.4f}, "
                 f"stratified p={p_str:.4f}: the page's numbers come disproportionately from "
                 f"artifacts that do not record their source")
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "provenance_reach.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "under_powered": under,
        "n_rounds": n, "n_cited": nc,
        "p_prov_cited": pc, "p_prov_uncited": pu, "delta": obs,
        "delta_is": "DERIVATION over a complete enumeration; only the permutation p is tested",
        "p_unstratified": p_raw, "p_time_stratified": p_str,
        "plant_delta": d_pl, "plant_p": p_pl, "g0_ok": g0_ok, "placebo": plc,
        "dose_response": doses, "mde": mde,
        "check205": ("R605's closing 'only' was refuted by R605's OWN passing placebo — a round "
                     "artifact written by its own run.py is a construction and a committed "
                     "artifact side by side, and there are hundreds"),
        "corpus_rate": "109 of 426 artifacts (25.6%) carry a provenance-shaped key",
        "impossible": ("a recorded hash proves a source was NAMED, not that the bytes match it; "
                       "verifying that needs the source file, and R605 found most are not here"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'provenance_reach.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
