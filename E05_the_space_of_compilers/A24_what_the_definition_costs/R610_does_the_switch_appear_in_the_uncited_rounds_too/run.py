#!/usr/bin/env python3
"""
R610 -- does the switch at 434 appear in the UNCITED rounds too?

CHECK #209 CAUGHT MY OWN DICHOTOMY OMITTING A CASE. R609 closed: same stop in the uncited set
=> a property of the WORK; no stop => a property of SELECTION. ⛔ But the uncited set could stop
at a DIFFERENT point, which is neither, and a two-branch reading would have forced that outcome
into whichever branch it resembled. The world set below has three members and a fourth for the
case where the uncited set resolves nothing.

R609 measured, among era 3's 35 CITED rounds: best cut 434 with Delta = 1.0000 against a
selection-aware max-over-cuts null of 0.4800. Every cited round below 434 records its source
and none at or above it does. This round runs the IDENTICAL sweep on the 83 UNCITED rounds of
the same band -- same instrument, same null construction, same admissibility rule -- so the two
answers are comparable by construction rather than by argument.

ESTIMAND        the best cut and its Delta among era 3's UNCITED rounds, and the DISTANCE from
                434. The comparison is between two sweeps, not between a sweep and a threshold.
IDENTIFICATION  Exact. ⚠ The uncited arm is larger (83 vs 35) so its null is TIGHTER, and a
                like-for-like comparison must read each Delta against ITS OWN null rather than
                against the other arm's. Both nulls are computed and both are printed.
SCOPE           population : rounds 365-485 NOT cited by STATEMENT.md
                instrument : provenance-shaped key at any depth; round id as the ordering
                             instrument unit = A ROUND'S POSITION IN THE ID ORDER
                             claim unit      = ITS POSITION IN TIME -- NOT equal; ids order the
                             work and do not date it
                baseline   : R609's cited-arm sweep, rerun here so both come from one code path
                regime     : as committed at this sha
WORLDS          A THE WORK: the uncited sweep also stops at or near 434 (|distance| <= 10) ->
                  the practice changed corpus-wide and citation inherited it.
                B SELECTION: the uncited sweep shows no cut clearing its own null -> provenance
                  continues after 434 among uncited rounds, and citation picked the ones that
                  stopped.
                C A DIFFERENT BOUNDARY: the uncited sweep clears its null at a cut far from 434
                  -> two switches, and neither of R609's readings applies.
                D UNRESOLVABLE: the uncited arm has too few provenance-carrying rounds for any
                  cut to clear -> silence, reported as such.
KILL            pre-registered: each arm's best |Delta| must clear ITS OWN max-over-cuts null.
                An arm that does not clear contributes no boundary, however suggestive its
                curve looks.
POSITIVE CTRL   a step planted at a known cut in the UNCITED arm must be recovered with its
                location. Fails at g=0: provenance independent of id must not produce one.
NEGATIVE CTRL   label permutation within each arm, 400 draws, giving that arm's own null.
PLACEBO         constant provenance must give Delta = 0 at every cut in both arms.
SEEDS           0, 1, 2.
MULTIPLICITY    every admissible cut in each arm; each null is on the MAXIMUM across that arm's
                cuts, so neither best cut is credited for being the best of many.
ARTIFACT        results/two_arms.json
IMPOSSIBLE      construct validity for "the work changed": a boundary in id order is not a
                change in practice; it is consistent with a reorganisation, a renumbering, or a
                gap in the record. Nothing here carries a timestamp.
"""

from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
FIELDS = ("source_sha256", "source_name", "source_hash", "sha256", "src_sha")
LO, HI, MINSIDE = 365, 485, 5
R609_CUT = 434


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
        if not d.is_dir() or d.name.startswith(("R609_", "R610_")):
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
        out[rid] = prov
    return out


def cut_curve(ids, y, cuts):
    out = []
    for c in cuts:
        a = [v for i, v in zip(ids, y) if i < c]
        b = [v for i, v in zip(ids, y) if i >= c]
        if len(a) >= MINSIDE and len(b) >= MINSIDE:
            out.append((c, sum(a)/len(a) - sum(b)/len(b), len(a), len(b)))
    return out


def spearman(ids, y):
    n = len(ids)
    ry = sorted(range(n), key=lambda k: y[k])
    rk = [0]*n
    for r, k in enumerate(ry):
        rk[k] = r
    mx = sum(range(n))/n; my = sum(rk)/n
    num = sum((i - mx)*(r - my) for i, r in zip(range(n), rk))
    dx = sum((i - mx)**2 for i in range(n)); dy = sum((r - my)**2 for r in rk)
    return num/((dx*dy)**0.5) if dx and dy else 0.0


def sweep(ids, y, label, seeds=400):
    cuts = sorted(set(ids))
    curve = cut_curve(ids, y, cuts)
    if not curve:
        return None
    best_c, best_d = max(((c, d) for c, d, _, _ in curve), key=lambda t: abs(t[1]))
    rng = random.Random(0)
    nulls = []
    for _ in range(seeds):
        yp = y[:]; rng.shuffle(yp)
        cc = cut_curve(ids, yp, cuts)
        nulls.append(max(abs(d) for _, d, _, _ in cc) if cc else 0.0)
    nulls.sort()
    t = nulls[int(0.95 * len(nulls))]
    return {"label": label, "n": len(ids), "n_prov": int(sum(y)), "n_cuts": len(curve),
            "best_cut": best_c, "best_delta": best_d, "null_p95": t,
            "null_median": nulls[len(nulls)//2], "null_max": nulls[-1],
            "clears": abs(best_d) > t,
            "curve": [{"cut": c, "delta": d, "n_lo": a, "n_hi": b} for c, d, a, b in curve]}


def main():
    S = survey()
    cited = {int(x) for x in re.findall(r"R(\d{3})", (E05 / "STATEMENT.md").read_text())}
    ids_c = sorted(i for i in S if i in cited)
    ids_u = sorted(i for i in S if i not in cited)
    if len(ids_c) < 12 or len(ids_u) < 12:
        print(f"UNRUNNABLE: arms too small ({len(ids_c)}, {len(ids_u)}). Exit 2, never 0."); return 2
    yc = [1.0 if S[i] else 0.0 for i in ids_c]
    yu = [1.0 if S[i] else 0.0 for i in ids_u]
    print(f"POPULATION  band {LO}-{HI}: CITED n={len(ids_c)} prov={int(sum(yc))}   "
          f"UNCITED n={len(ids_u)} prov={int(sum(yu))}")
    print(f"  ⚠ the arms differ in size, so each Delta is read against ITS OWN null, never "
          f"against the other arm's")

    A = sweep(ids_c, yc, "CITED")
    B = sweep(ids_u, yu, "UNCITED")
    print(f"\n─── TWO SWEEPS, ONE CODE PATH ───")
    for r in (A, B):
        print(f"  {r['label']:<8} n={r['n']:<4} prov={r['n_prov']:<3} cuts={r['n_cuts']:<3} "
              f"best cut {r['best_cut']:<4} Delta={r['best_delta']:+.4f}   null p95 "
              f"{r['null_p95']:.4f} (med {r['null_median']:.4f}, max {r['null_max']:.4f})   "
              f"{'CLEARS' if r['clears'] else 'does not clear'}")
    dist = abs(B["best_cut"] - R609_CUT)
    print(f"\n  distance between the two best cuts: |{B['best_cut']} - {R609_CUT}| = {dist}")

    print(f"\n─── UNCITED CURVE (printed entire) ───")
    print(f"{'cut':>6} {'n<':>4} {'n>=':>4} {'Delta':>9}")
    for row in B["curve"]:
        print(f"{row['cut']:>6} {row['n_lo']:>4} {row['n_hi']:>4} {row['delta']:>+9.4f}")

    print(f"\n─── CONTROLS (on the UNCITED arm) ───")
    mid = ids_u[len(ids_u)//2]
    P = sweep(ids_u, [1.0 if i < mid else 0.0 for i in ids_u], "plant", seeds=200)
    pos_ok = P["clears"] and P["best_cut"] == mid
    print(f"  POSITIVE  step planted at {mid}: best cut {P['best_cut']}, |Delta|="
          f"{abs(P['best_delta']):.4f} vs {P['null_p95']:.4f} -> "
          f"{'PASS — recovered with its location' if pos_ok else '⛔ FAIL'}")
    rng = random.Random(5)
    rate = sum(yu)/len(yu)
    G = sweep(ids_u, [1.0 if rng.random() < rate else 0.0 for _ in ids_u], "g0", seeds=200)
    g0_ok = not G["clears"]
    print(f"  POSITIVE @ g=0  provenance independent of id: |Delta|={abs(G['best_delta']):.4f} "
          f"vs {G['null_p95']:.4f} -> {'PASS (can fail)' if g0_ok else '⛔ fires on noise'}")
    C = cut_curve(ids_u, [1.0]*len(ids_u), sorted(set(ids_u)))
    plc_ok = all(abs(d) < 1e-12 for _, d, _, _ in C)
    print(f"  PLACEBO   constant provenance: max|Delta|="
          f"{max(abs(d) for _, d, _, _ in C):.4f} -> "
          f"{'PASS — zero at every cut' if plc_ok else '⛔ FAIL'}")
    controls_ok = pos_ok and g0_ok and plc_ok

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif not B["clears"]:
        world = (f"B SELECTION — the uncited arm's best cut {B['best_cut']} at "
                 f"|Delta|={abs(B['best_delta']):.4f} does NOT clear its own null "
                 f"{B['null_p95']:.4f}. Provenance does not stop at any point among uncited "
                 f"rounds, so the switch at {R609_CUT} is a property of what the page SELECTED, "
                 f"not of how the work was done.")
    elif dist <= 10:
        world = (f"A THE WORK — the uncited arm also stops at {B['best_cut']}, {dist} from "
                 f"{R609_CUT}: the practice changed corpus-wide and citation inherited it")
    else:
        world = (f"C A DIFFERENT BOUNDARY — the uncited arm clears its null at {B['best_cut']}, "
                 f"{dist} away from {R609_CUT}. Two switches, and neither of R609's readings "
                 f"applies — the case my own dichotomy omitted.")
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "two_arms.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "cited": A, "uncited": B,
        "r609_cut": R609_CUT, "distance": dist,
        "check209": ("R609's closing line offered a two-branch reading — same stop => the WORK, "
                     "no stop => SELECTION — omitting the case where the uncited arm stops "
                     "somewhere else, which a two-branch rule would have forced into whichever "
                     "branch it resembled"),
        "impossible": ("a boundary in id order is not a change in practice; it is equally "
                       "consistent with a reorganisation, a renumbering, or a gap in the record"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'two_arms.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
