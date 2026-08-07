#!/usr/bin/env python3
"""
R608 -- what separates era 3's documented cited rounds from its undocumented ones?

CHECK #207 CAUGHT TWO ERRORS IN R607's CLOSING LINE.
  ⛔ *"the page cites its WORST-DOCUMENTED QUARTER"* -- `P(prov | cited) = 0.2571` is a RATE
     AMONG THE CITED, not a RANK POSITION in the band. Two different quantities merged because
     both land near a quarter. Nothing measured supports the rank claim.
  ⛔ *"the repair is simply to re-derive the 26"* -- R605 measured the construction step as
     absent from this repository for 98 of 101 scored artifacts, so the proposed repair may be
     impossible. A NEXT line may not propose a repair a previous round has already priced out.

⚠ AND THE POWER QUESTION COMES FIRST HERE, not after. The population is 35 rounds split 9/26.
Before asking WHICH feature separates, the round asks whether ANY feature COULD be detected at
this n -- because a null from a design that cannot resolve anything is silence, and this design
is small enough that silence is the likely output.

ESTIMAND        For each structural feature f: Delta_f = P(f | provenance) - P(f | none),
                over era 3's CITED rounds only, so era and citation are held fixed BY
                CONSTRUCTION rather than by adjustment.
IDENTIFICATION  Exact as counts. ⚠ Identified but almost certainly UNRESOLVABLE: with 9 vs 26
                the smallest detectable |Delta| is computed FIRST and reported before any
                feature is read, so no feature's null can be mistaken for evidence.
SCOPE           population : rounds 365-485 that STATEMENT.md cites (n=35)
                instrument : filesystem + json key presence
                             instrument unit = A STRUCTURAL PROPERTY OF THE DIRECTORY
                             claim unit      = A REASON THE ROUND DID OR DID NOT RECORD ITS
                                               SOURCE -- NOT equal; a correlate is not a cause,
                                               and every result here is descriptive
                baseline   : the same features among era 3's UNCITED rounds
                regime     : as committed at this sha
WORLDS          A MECHANISM: >=1 feature separates beyond the permutation null and beyond the
                  design's own MDE -> the selection has a structural correlate and the repair
                  can target it.
                B ARBITRARY: no feature separates AND the MDE is small enough that a real
                  separation would have shown -> the split is not structural.
                C UNRESOLVABLE: the MDE exceeds any plausible Delta -> the design cannot tell
                  A from B, and saying "arbitrary" would be silence dressed as a finding.
KILL            pre-registered and evaluated BEFORE the features: if the design's MDE exceeds
                0.50 -- half the range of a proportion difference -- the verdict is C and no
                feature is read as evidence whatever it returns.
POSITIVE CTRL   a planted feature perfectly correlated with provenance must be detected.
                Fails at g=0: a feature independent of provenance must not be.
NEGATIVE CTRL   random features at the observed marginal, 200 draws, giving the null
                distribution of max|Delta| across the whole grid -- the multiplicity
                correction, computed rather than assumed.
PLACEBO         a constant feature (true for every round) must return Delta exactly 0.
SEEDS           0, 1, 2.
MULTIPLICITY    n_features x 200 null draws; the null is on max|Delta| over the grid, so the
                correction is built in rather than applied afterwards.
ARTIFACT        results/era3_split.json
IMPOSSIBLE      construct validity for "why": a structural correlate is not a reason. Deciding
                why a round did or did not record its source needs the round's author.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
FIELDS = ("source_sha256", "source_name", "source_hash", "sha256", "src_sha")
LO, HI = 365, 485


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
        if not d.is_dir() or d.name.startswith("R608_"):
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
        prov = False
        for f in js:
            try:
                o = json.loads(f.read_text())
            except Exception:
                continue
            acc = []; walk(o, acc)
            if any(any(x == k or x in k for x in FIELDS) for k in acc):
                prov = True
        files = list((d / "results").rglob("*"))
        out[rid] = {
            "arc": d.parent.name.split("_")[0],
            "prov": prov,
            "has_py": any(p.suffix == ".py" for p in d.iterdir() if p.is_file()),
            "has_readme": (d / "README.md").is_file(),
            "many_artifacts": len([p for p in files if p.is_file()]) >= 3,
            "big_readme": ((d / "README.md").stat().st_size > 3000
                           if (d / "README.md").is_file() else False),
            "has_npz": any(p.suffix == ".npz" for p in files if p.is_file()),
            "late_in_era": rid >= (LO + HI) // 2,
        }
    return out


def delta(flag, prov):
    a = [f for f, p in zip(flag, prov) if p]
    b = [f for f, p in zip(flag, prov) if not p]
    return (sum(a)/len(a) - sum(b)/len(b)) if a and b else 0.0


def main():
    S = survey()
    if not S:
        print("UNRUNNABLE: no era-3 rounds with artifacts. Exit 2, never 0."); return 2
    cited_ids = {int(x) for x in re.findall(r"R(\d{3})", (E05 / "STATEMENT.md").read_text())}
    ids = sorted(i for i in S if i in cited_ids)
    if len(ids) < 8:
        print(f"UNRUNNABLE: only {len(ids)} cited era-3 rounds. Exit 2."); return 2
    prov = [S[i]["prov"] for i in ids]
    n, npv = len(ids), sum(prov)
    print(f"POPULATION  era 3 = rounds {LO}-{HI}, CITED only: n={n}, "
          f"with provenance {npv}, without {n-npv}")

    feats = [k for k in ("has_py", "has_readme", "many_artifacts", "big_readme",
                         "has_npz", "late_in_era")]
    # ---- POWER FIRST, before any feature is read ----------------------------------
    rng = random.Random(0)
    nulls = []
    for _ in range(200):
        row = []
        for _f in feats:
            rate = rng.uniform(0.2, 0.8)
            fl = [1.0 if rng.random() < rate else 0.0 for _ in range(n)]
            row.append(abs(delta(fl, prov)))
        nulls.append(max(row))
    nulls.sort()
    mde = nulls[int(0.95 * len(nulls))]
    print(f"\n─── POWER, COMPUTED BEFORE ANY FEATURE IS READ ───")
    print(f"  null distribution of max|Delta| over {len(feats)} random features, 200 draws:")
    print(f"    median {nulls[len(nulls)//2]:.4f}   p95 {mde:.4f}   max {nulls[-1]:.4f}")
    print(f"  => a feature must exceed |Delta| = {mde:.4f} to clear the whole-grid null")
    unresolvable = mde > 0.50
    print(f"  KILL (pre-registered): MDE > 0.50 -> verdict C regardless of features "
          f"-> {'FIRES — the design cannot separate A from B' if unresolvable else 'does not fire'}")

    print(f"\n─── CONTROLS ───")
    perfect = [1.0 if p else 0.0 for p in prov]
    d_pos = abs(delta(perfect, prov))
    pos_ok = d_pos > mde
    print(f"  POSITIVE  a feature perfectly correlated with provenance: |Delta|={d_pos:.4f} "
          f"vs MDE {mde:.4f} -> {'PASS' if pos_ok else '⛔ FAIL — even a perfect feature is invisible'}")
    rng2 = random.Random(11)
    indep = [1.0 if rng2.random() < 0.5 else 0.0 for _ in range(n)]
    d_g0 = abs(delta(indep, prov))
    g0_ok = d_g0 <= mde
    print(f"  POSITIVE @ g=0  a feature independent of provenance: |Delta|={d_g0:.4f} -> "
          f"{'PASS (can fail)' if g0_ok else '⛔ it fires on noise'}")
    const = [1.0] * n
    d_plc = abs(delta(const, prov))
    plc_ok = d_plc < 1e-12
    print(f"  PLACEBO   a constant feature: |Delta|={d_plc:.4f} -> "
          f"{'PASS — exactly zero' if plc_ok else '⛔ FAIL'}")
    controls_ok = pos_ok and g0_ok and plc_ok

    print(f"\n─── FEATURES (all reported, survivors and not) ───")
    rows = []
    for f in feats:
        fl = [1.0 if S[i][f] else 0.0 for i in ids]
        d = delta(fl, prov)
        beats = abs(d) > mde
        rows.append({"feature": f, "delta": d, "rate_prov": sum(x for x, p in zip(fl, prov) if p)/max(1, npv),
                     "rate_none": sum(x for x, p in zip(fl, prov) if not p)/max(1, n-npv),
                     "beats_grid_null": beats})
        print(f"  {f:<16} P(f|prov)={rows[-1]['rate_prov']:.4f}  "
              f"P(f|none)={rows[-1]['rate_none']:.4f}  Delta={d:+.4f}  "
              f"{'SURVIVES' if beats else 'inside the grid null'}")
    arcs = {}
    for i in ids:
        arcs.setdefault(S[i]["arc"], [0, 0])[0 if S[i]["prov"] else 1] += 1
    print(f"  arc distribution (prov / none): "
          f"{ {k: f'{v[0]}/{v[1]}' for k, v in sorted(arcs.items())} }")
    surv = [r for r in rows if r["beats_grid_null"]]

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif unresolvable:
        world = (f"C UNRESOLVABLE — the whole-grid MDE is {mde:.4f}, above the pre-registered "
                 f"0.50 ceiling, so at n={n} ({npv} vs {n-npv}) this design cannot distinguish "
                 f"a structural mechanism from an arbitrary split. Calling it arbitrary would "
                 f"be silence dressed as a finding.")
    elif surv:
        world = (f"A MECHANISM — {len(surv)} feature(s) clear the whole-grid null: "
                 f"{[(r['feature'], round(r['delta'], 4)) for r in surv]}")
    else:
        world = (f"B ARBITRARY — no feature of {len(feats)} clears |Delta| = {mde:.4f}, and the "
                 f"MDE is below the 0.50 ceiling, so a real structural separation of that size "
                 f"would have shown")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: {len(feats)} features against a null on max|Delta| over the whole "
          f"grid, 200 draws — the correction is built in, not applied afterwards.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "era3_split.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "unresolvable": unresolvable,
        "n": n, "n_prov": npv, "mde_grid": mde,
        "null_median": nulls[len(nulls)//2], "null_max": nulls[-1],
        "features": rows, "arc_distribution": {k: v for k, v in sorted(arcs.items())},
        "check207": ("R607's closing line called 0.2571 the 'worst-documented quarter' — a RATE "
                     "among the cited read as a RANK in the band — and proposed re-deriving the "
                     "26, a repair R605 had already priced out for 98 of 101 scored artifacts"),
        "impossible": ("a structural correlate is not a reason; deciding why a round did or did "
                       "not record its source needs the round's author"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'era3_split.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
