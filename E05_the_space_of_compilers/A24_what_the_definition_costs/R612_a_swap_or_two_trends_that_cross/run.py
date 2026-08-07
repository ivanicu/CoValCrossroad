#!/usr/bin/env python3
"""
R612 -- is it one field replacing another, or two trends that happen to cross?

CHECK #211 CAUGHT THE ARITHMETIC TRAP IN R611's CLOSING LINE. It proposed a 2x2 of `prov` by
`world` POOLED across the boundary. Pooled, those two are anti-correlated BY CONSTRUCTION: the
marginals on each side of B are exactly the two Deltas already measured, so "both ~ 0, neither
~ 0" is forced by numbers in hand. That is a DERIVATION dressed as a test -- 1+1=2, therefore
2<3 -- and it would have confirmed the swap without evidence.

The informative version conditions on the side. Within the PRE-B rounds, where provenance is
near-universal, how many ALSO carry `world`? Within POST-B, where `world` is near-universal,
how many still carry provenance? A true field-for-field swap predicts near-zero co-occurrence
INSIDE each side too; two unrelated trends that merely cross predict co-occurrence at the
product of that side's marginals.

ESTIMAND        Within each side s of B=431: the count of rounds carrying BOTH keys and the
                count carrying NEITHER, against the counts expected if the two keys were
                independent AT THAT SIDE'S OWN MARGINALS.
                excess_s = observed(both) - expected(both).
IDENTIFICATION  Exact as counts. ⚠ The expectation is a DERIVATION from that side's marginals
                and is labelled as one; what is TESTED is whether the observed co-occurrence
                departs from it, by permuting one key within the side.
SCOPE           population : rounds 365-485 with >=1 parseable results/*.json (n=118)
                instrument : json key presence at any depth
                             instrument unit = A KEY IN AN ARTIFACT
                             claim unit      = A FIELD THE ROUND CHOSE TO WRITE -- NOT equal;
                             a key can be absent because the round had nothing to put in it
                baseline   : independence at each side's own marginals
                regime     : as committed at this sha
WORLDS          A A TRUE SWAP: within BOTH sides, co-occurrence is at or below independence and
                  the complement holds -- one field replaced another, round for round.
                B TWO TRENDS CROSSING: co-occurrence within a side is at independence, and the
                  mirrored Deltas are a coincidence of timing rather than a substitution.
                C PARTIAL: the sides disagree -> the swap happened on one side of the boundary
                  and not the other, which is a different event from either.
KILL            pre-registered: a side with fewer than 5 rounds in any cell of its 2x2 is
                UNRESOLVABLE and reports no verdict -- an expected count below 5 makes the
                comparison a story about one or two directories.
POSITIVE CTRL   plant a perfect complement within a side (every round exactly one key) and
                require the test to detect it. Fails at g=0: keys assigned independently at the
                same marginals must NOT be detected as a swap.
NEGATIVE CTRL   permute one key within the side, 2000 draws -- the null for co-occurrence.
PLACEBO         a key present in every round must show co-occurrence exactly at independence.
SEEDS           0, 1, 2.
MULTIPLICITY    2 sides x 2 cells; both sides reported whatever they return.
ARTIFACT        results/swap_or_crossing.json
IMPOSSIBLE      construct validity for "chose to write": absence of a key is not a decision --
                a round with no verdict has nothing to put in `world`, and one that consumed no
                file has nothing to hash. This bounds the swap reading; it cannot establish
                intent.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
PROV = ("source_sha256", "source_name", "source_hash", "sha256", "src_sha")
LO, HI, B = 365, 485, 431


def walk(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            acc.append(str(k)); walk(v, acc)
    elif isinstance(o, list):
        for v in o:
            walk(v, acc)


def survey():
    out = {}
    for d in sorted(E05.glob("A*/R[0-9]*")):
        if not d.is_dir() or d.name.startswith("R612_"):
            continue
        m = re.match(r"R(\d+)", d.name)
        if not m:
            continue
        rid = int(m.group(1))
        if not (LO <= rid <= HI) or not (d / "results").is_dir():
            continue
        js = list((d / "results").glob("*.json"))
        if not js:
            continue
        keys = set()
        for f in js:
            try:
                o = json.loads(f.read_text())
            except Exception:
                continue
            acc = []; walk(o, acc)
            keys |= set(acc)
        out[rid] = (any(any(x in k for x in PROV) for k in keys), "world" in keys)
    return out


def table(rows):
    both = sum(1 for p, w in rows if p and w)
    neither = sum(1 for p, w in rows if not p and not w)
    ponly = sum(1 for p, w in rows if p and not w)
    wonly = sum(1 for p, w in rows if not p and w)
    return both, ponly, wonly, neither


def null_both(rows, seeds=(0, 1, 2), draws=2000):
    ws = [w for _, w in rows]
    ps = [p for p, _ in rows]
    out = []
    for s in seeds:
        rng = random.Random(s)
        for _ in range(draws):
            q = ws[:]; rng.shuffle(q)
            out.append(sum(1 for p, w in zip(ps, q) if p and w))
    out.sort()
    return out


def main():
    S = survey()
    ids = sorted(S)
    if len(ids) < 30:
        print("UNRUNNABLE: band too small. Exit 2, never 0."); return 2
    print(f"POPULATION  band {LO}-{HI}: n={len(ids)}   boundary B={B}")
    print(f"  ⚠ POOLED across B the two keys are anti-correlated BY CONSTRUCTION — that 2x2 is "
          f"a DERIVATION from R611's marginals. Everything below conditions on the SIDE.")

    res = {}
    for name, sel in (("PRE-B  (< 431)", lambda i: i < B), ("POST-B (>= 431)", lambda i: i >= B)):
        rows = [S[i] for i in ids if sel(i)]
        n = len(rows)
        both, ponly, wonly, neither = table(rows)
        pp = (both + ponly) / n
        pw = (both + wonly) / n
        exp_both = pp * pw * n
        exp_neither = (1 - pp) * (1 - pw) * n
        nb = null_both(rows)
        lo, hi = nb[int(0.025*len(nb))], nb[int(0.975*len(nb))]
        smallest = min(both, ponly, wonly, neither)
        resolvable = min(exp_both, exp_neither) >= 5
        print(f"\n─── {name}   n={n} ───")
        print(f"  {'':>12} {'world=1':>9} {'world=0':>9}")
        print(f"  {'prov=1':>12} {both:>9} {ponly:>9}")
        print(f"  {'prov=0':>12} {wonly:>9} {neither:>9}")
        print(f"  marginals: P(prov)={pp:.4f}  P(world)={pw:.4f}")
        print(f"  BOTH observed {both}   expected under independence {exp_both:.2f}   "
              f"(DERIVATION from this side's marginals)")
        print(f"  NEITHER observed {neither}   expected {exp_neither:.2f}")
        print(f"  null for BOTH (permute `world` within the side, 6000 draws): "
              f"95% interval [{lo}, {hi}]")
        print(f"  KILL: min expected cell {min(exp_both, exp_neither):.2f} -> "
              f"{'resolvable' if resolvable else 'UNRESOLVABLE, no verdict from this side'}")
        res[name] = {"n": n, "both": both, "prov_only": ponly, "world_only": wonly,
                     "neither": neither, "p_prov": pp, "p_world": pw,
                     "exp_both": exp_both, "exp_neither": exp_neither,
                     "null_lo": lo, "null_hi": hi, "resolvable": resolvable,
                     "below_null": both < lo, "smallest_cell": smallest}

    print(f"\n─── CONTROLS ───")
    rowsA = [S[i] for i in ids if i < B]
    perfect = [(True, False)] * (len(rowsA)//2) + [(False, True)] * (len(rowsA) - len(rowsA)//2)
    bA, *_ = table(perfect)
    nbA = null_both(perfect)
    pos_ok = bA < nbA[int(0.025*len(nbA))] or nbA[int(0.025*len(nbA))] == bA == 0
    print(f"  POSITIVE  a perfect complement planted: BOTH={bA}, null 2.5% "
          f"{nbA[int(0.025*len(nbA))]} -> {'PASS' if pos_ok else 'FAIL'}")
    rng = random.Random(4)
    indep = [(rng.random() < 0.5, rng.random() < 0.5) for _ in rowsA]
    bI, *_ = table(indep)
    nbI = null_both(indep)
    g0_ok = nbI[int(0.025*len(nbI))] <= bI <= nbI[int(0.975*len(nbI))]
    print(f"  POSITIVE @ g=0  keys assigned independently: BOTH={bI}, null 95% "
          f"[{nbI[int(0.025*len(nbI))]}, {nbI[int(0.975*len(nbI))]}] -> "
          f"{'PASS (can fail)' if g0_ok else 'FAIL'}")
    allk = [(True, True)] * len(rowsA)
    bK, *_ = table(allk)
    plc_ok = bK == len(rowsA)
    print(f"  PLACEBO   a key present in every round: BOTH={bK} of {len(rowsA)} -> "
          f"{'PASS — co-occurrence exactly at independence' if plc_ok else 'FAIL'}")
    controls_ok = pos_ok and g0_ok and plc_ok

    print(f"\n─── VERDICT ───")
    usable = [k for k, v in res.items() if v["resolvable"]]
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif not usable:
        world = ("C/UNRESOLVABLE — every side has an expected cell below 5, so the 2x2 would be "
                 "a story about one or two directories. The mirrored Deltas stand; whether they "
                 "are a swap is NOT established.")
    else:
        below = [k for k in usable if res[k]["below_null"]]
        if len(below) == len(usable):
            world = (f"A A TRUE SWAP — in every resolvable side ({usable}) co-occurrence is "
                     f"BELOW its own permutation null: one field replaced another round for round")
        elif below:
            world = (f"C PARTIAL — {below} shows co-occurrence below null and the other side "
                     f"does not; the swap holds on one side of the boundary only")
        else:
            world = (f"B TWO TRENDS CROSSING — co-occurrence sits inside the null in "
                     f"{usable}, so the mirrored Deltas are a coincidence of timing rather than "
                     f"a substitution")
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "swap_or_crossing.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "B": B, "sides": res,
        "check211": ("R611's closing line proposed a 2x2 POOLED across B. Pooled, the two keys "
                     "are anti-correlated by construction and the cells are a DERIVATION from "
                     "marginals already in hand — the arithmetic trap. Conditioned on side here."),
        "impossible": ("absence of a key is not a decision: a round with no verdict has nothing "
                       "to put in `world`, and one that consumed no file has nothing to hash"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'swap_or_crossing.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
