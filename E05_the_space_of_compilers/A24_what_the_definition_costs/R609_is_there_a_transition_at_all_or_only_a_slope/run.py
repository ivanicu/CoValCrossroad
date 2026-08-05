#!/usr/bin/env python3
"""
R609 -- is there a transition at all, or only a slope?

CHECK #208 CAUGHT R608's CLOSING LINE ASSERTING AN OBJECT IT NEVER ESTABLISHED. It said *"THE
TRUE TRANSITION is somewhere in 365-485"* and proposed locating it. But `late_in_era`
separating is equally consistent with a GRADUAL DECLINE, with a transition OUTSIDE the band
that the binning aliases, or with no transition at all. Naming the transition before
establishing one exists is §4's `the definition describes the instance`, applied to a shape
instead of a category: the sentence describes what a step model would look like and then
treats the step as given.

So this round refuses the located-transition framing and asks the prior question, with the
whole cut curve reported either way.

ESTIMAND        (i) the FULL curve Delta(c) = P(prov | id < c) - P(prov | id >= c) over every
                admissible cut c in the band -- reported entire, not at its maximum.
                (ii) which of three shapes the data prefer: FLAT (no dependence on id), SLOPE
                (monotone in id), STEP (one cut dominating).
IDENTIFICATION  (i) is exact. ⚠ (ii) is the question the design is weakest on: n=35 with 9
                positives, and a step and a steep slope are near-indistinguishable at that n.
                The model comparison is therefore run against a null that INCLUDES the
                selection of the best cut, so the winning cut cannot be credited for being the
                best of many.
SCOPE           population : rounds 365-485 cited by STATEMENT.md (n=35)
                instrument : provenance-shaped key at any depth; round id as the ordering
                             instrument unit = A ROUND'S POSITION IN THE ID ORDER
                             claim unit      = ITS POSITION IN TIME -- NOT equal; ids are a
                             proxy and no artifact carries a timestamp
                baseline   : the same statistics under label permutation
                regime     : as committed at this sha
WORLDS          A STEP: the best cut's |Delta| beats a null that already includes best-cut
                  selection -> a transition exists and is locatable.
                B SLOPE: the rank correlation of provenance with id survives while no single
                  cut beats the selection-aware null -> a gradual decline, and R608's
                  `late_in_era` was a coarse read of it.
                C UNRESOLVABLE: neither statistic clears its null -> at this n the shape
                  cannot be read, and NAMING a transition is exactly the error check #208
                  caught.
KILL            pre-registered: if the best-cut |Delta| does not exceed the 95th percentile of
                the MAX-OVER-CUTS null, no transition is admissible -- however large it looks.
                That null is the multiplicity correction, built in rather than applied.
POSITIVE CTRL   a synthetic step planted at a known cut must be recovered, with its location.
                Fails at g=0: provenance independent of id must not produce a step.
NEGATIVE CTRL   label permutation, 400 draws, giving the max-over-cuts null directly.
PLACEBO         a constant provenance vector must give Delta = 0 at every cut.
SEEDS           0, 1, 2.
MULTIPLICITY    every admissible cut, and the null is on the MAXIMUM across them.
ARTIFACT        results/shape.json
IMPOSSIBLE      construct validity for "transition in TIME": round ids order the work, they do
                not date it. Nothing in the artifacts carries a timestamp -- the register's
                `temporally resolved` row, landing again on my own instrument.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
FIELDS = ("source_sha256", "source_name", "source_hash", "sha256", "src_sha")
LO, HI, MINSIDE = 365, 485, 5


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
        if not d.is_dir() or d.name.startswith("R609_"):
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


def main():
    S = survey()
    cited = {int(x) for x in re.findall(r"R(\d{3})", (E05 / "STATEMENT.md").read_text())}
    ids = sorted(i for i in S if i in cited)
    if len(ids) < 12:
        print(f"UNRUNNABLE: only {len(ids)} cited rounds in band. Exit 2, never 0."); return 2
    y = [1.0 if S[i] else 0.0 for i in ids]
    n, npos = len(ids), int(sum(y))
    cuts = sorted({i for i in ids})
    curve = cut_curve(ids, y, cuts)
    if not curve:
        print("UNRUNNABLE: no cut leaves both sides populated. Exit 2."); return 2
    print(f"POPULATION  band {LO}-{HI}, cited only: n={n}, with provenance {npos}")
    print(f"  admissible cuts (>= {MINSIDE} rounds each side): {len(curve)}")

    print(f"\n─── THE FULL CUT CURVE (reported entire, not at its maximum) ───")
    print(f"{'cut':>6} {'n<':>4} {'n>=':>4} {'P(prov|<)':>10} {'P(prov|>=)':>11} {'Delta':>9}")
    for c, d, na, nb in curve:
        pa = sum(v for i, v in zip(ids, y) if i < c)/na
        pb = sum(v for i, v in zip(ids, y) if i >= c)/nb
        print(f"{c:>6} {na:>4} {nb:>4} {pa:>10.4f} {pb:>11.4f} {d:>+9.4f}")
    best_c, best_d = max(((c, d) for c, d, _, _ in curve), key=lambda t: abs(t[1]))
    rho = spearman(ids, y)
    print(f"\n  best cut {best_c}: Delta={best_d:+.4f}   |   Spearman(id, prov) = {rho:+.4f}")

    print(f"\n─── CONTROLS ───")
    rng = random.Random(0)
    maxnull, rhonull = [], []
    for _ in range(400):
        yp = y[:]; rng.shuffle(yp)
        cc = cut_curve(ids, yp, cuts)
        maxnull.append(max(abs(d) for _, d, _, _ in cc) if cc else 0.0)
        rhonull.append(abs(spearman(ids, yp)))
    maxnull.sort(); rhonull.sort()
    t_cut = maxnull[int(0.95*len(maxnull))]
    t_rho = rhonull[int(0.95*len(rhonull))]
    print(f"  NEGATIVE  max-over-cuts null (400 label permutations): median "
          f"{maxnull[len(maxnull)//2]:.4f}  p95 {t_cut:.4f}  max {maxnull[-1]:.4f}")
    print(f"            |Spearman| null: median {rhonull[len(rhonull)//2]:.4f}  p95 {t_rho:.4f}")
    mid = ids[n//2]
    ystep = [1.0 if i < mid else 0.0 for i in ids]
    cs = cut_curve(ids, ystep, cuts)
    bc, bd = max(((c, d) for c, d, _, _ in cs), key=lambda t: abs(t[1]))
    pos_ok = abs(bd) > t_cut and bc == mid
    print(f"  POSITIVE  a step planted at {mid}: best cut {bc}, |Delta|={abs(bd):.4f} vs "
          f"{t_cut:.4f} -> {'PASS — recovered with its location' if pos_ok else '⛔ FAIL'}")
    rng3 = random.Random(3)
    yind = [1.0 if rng3.random() < npos/n else 0.0 for _ in ids]
    ci = cut_curve(ids, yind, cuts)
    g0 = max(abs(d) for _, d, _, _ in ci)
    g0_ok = g0 <= t_cut
    print(f"  POSITIVE @ g=0  provenance independent of id: max|Delta|={g0:.4f} -> "
          f"{'PASS (can fail)' if g0_ok else '⛔ fires on noise'}")
    cconst = cut_curve(ids, [1.0]*n, cuts)
    plc_ok = all(abs(d) < 1e-12 for _, d, _, _ in cconst)
    print(f"  PLACEBO   constant provenance: max|Delta|="
          f"{max(abs(d) for _, d, _, _ in cconst):.4f} -> "
          f"{'PASS — zero at every cut' if plc_ok else '⛔ FAIL'}")
    controls_ok = pos_ok and g0_ok and plc_ok

    print(f"\n─── VERDICT ───")
    step_wins = abs(best_d) > t_cut
    slope_wins = abs(rho) > t_rho
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif step_wins and not slope_wins:
        world = (f"A STEP — best cut {best_c} at |Delta|={abs(best_d):.4f} clears the "
                 f"selection-aware null {t_cut:.4f}, while the rank correlation does not")
    elif slope_wins and not step_wins:
        world = (f"B SLOPE — |Spearman|={abs(rho):.4f} clears {t_rho:.4f} while no single cut "
                 f"clears {t_cut:.4f}: a gradual decline, and R608's `late_in_era` was a coarse "
                 f"read of it")
    elif step_wins and slope_wins:
        world = (f"A/B BOTH CLEAR — |Delta|={abs(best_d):.4f} > {t_cut:.4f} AND "
                 f"|rho|={abs(rho):.4f} > {t_rho:.4f}. At n={n} a step and a steep slope are "
                 f"not distinguishable; the data show a DECLINE and cannot say its shape.")
    else:
        world = (f"C UNRESOLVABLE — neither the best cut ({abs(best_d):.4f} vs {t_cut:.4f}) nor "
                 f"the rank correlation ({abs(rho):.4f} vs {t_rho:.4f}) clears its null. At "
                 f"n={n} the shape cannot be read, and naming a transition would be the error "
                 f"check #208 caught.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: {len(curve)} cuts, null taken on the MAXIMUM across them, so the "
          f"best cut is not credited for being the best of many.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "shape.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "n": n, "n_prov": npos,
        "curve": [{"cut": c, "delta": d, "n_lo": a, "n_hi": b} for c, d, a, b in curve],
        "best_cut": best_c, "best_delta": best_d, "spearman": rho,
        "null_max_cut_p95": t_cut, "null_rho_p95": t_rho,
        "step_clears": step_wins, "slope_clears": slope_wins,
        "check208": ("R608's closing line said 'THE TRUE TRANSITION is somewhere in 365-485' — "
                     "naming an object whose existence was never established, when the same "
                     "evidence is equally consistent with a gradual decline"),
        "impossible": ("round ids order the work, they do not date it; no artifact carries a "
                       "timestamp, so 'transition in time' is not what this measures"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'shape.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
