#!/usr/bin/env python3
"""
R704 -- is F2's weight our REPLICATE COUNT rather than our naming? Held-out name-recoverability.

CHECK #306 ON R703's NEXT LINE -- ITS COUNTS ARE RIGHT AND ITS OWN ARTIFACT MISREPORTS THEM.
  4 / 20 / 2 confirmed from R703's `rows`; R694's 95.2% confirmed at its README:26. But R703's
  verdict string prints `str(r['unique'][:3])` (run.py:120) -- three members, no ellipsis, no count --
  beside `n_unique: 20` in the SAME file. ⭐ THIRD occurrence of a display contradicting the artifact
  beside it (R690, R698, now R703). Annotated onto R703/README.md; the gate is deferred WITH ITS
  COUNT rather than built blind.

⛔ THE ARITHMETIC TRAP, DECLARED BEFORE THE RUN (see PREREGISTRATION.txt).
  R360's ledger prints the (family,k) cells, so F2's split is DERIVABLE BY HAND. POINT A is therefore
  a check on MY ARITHMETIC and is labelled DERIVED. The frontier is POINTS B and C, which the
  derivation does not settle: whether the share beats its own null, and whether the cells that do the
  determining exist only because WE SHIPPED REPLICATES.

ESTIMAND        per clause, over the arms it UNIQUELY excludes, the three-way split of leave-one-out
                name-recoverability: CELL-DETERMINED / FALLBACK(base rate) / WRONG. Headline is
                CELL-DETERMINED, the only category in which the name did work.
IDENTIFICATION  identified from R360 + the name parse. LOO is mandatory: in-sample purity is FORCED
                for the 12 singleton cells, which is what made R694's 95.2% a construction.
SCOPE           population : the 42 arms of R360's ledger
                instrument : LOO cell-majority predictor over a partition of the arm NAMES
                             instrument unit = AN ARM
                             claim unit      = A CLAUSE
                             ⚠ NOT EQUAL -- a share over 4 or 2 arms is not a clause property.
                baseline   : per-clause majority floor + label-permutation null (2000 × 3 seeds)
                regime     : this repository at HEAD
WORLDS          A PARAMETERISATION · B BEHAVIOURAL · C REPLICATE ARTIFACT · D BLIND (see PREREG)
KILL            conditional on POSITIVE firing and NEGATIVE being null; see PREREGISTRATION.txt
POSITIVE CTRL   label = (family=='random'), a pure function of the partition; threshold required to
                sit strictly between the null FLOOR and the computed CEILING (non-singleton share).
g=0             an i.i.d. seeded coin-flip label must NOT clear that threshold.
NEGATIVE CTRL   shuffle the cell ASSIGNMENT preserving sizes and REFIT the majorities.
SHAM            single-cell partition -- the same operation minus the partition's resolution.
PLACEBO         two identical runs differ by exactly 0.
ARTIFACT        results/recoverability.json
IMPOSSIBLE      cross-release (the naming scheme is ours) · construct validity of "recoverable"
                (no external standard says what a generator name should encode).
"""
from __future__ import annotations
import json, pathlib, random, re, subprocess, sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
CARD_MAX, NDRAW, SEEDS = 4, 2000, (0, 1, 2)
INSTRUMENT_UNIT, CLAIM_UNIT = "AN ARM", "A CLAUSE"


def family(a):
    m = re.match(r"^([a-z]+?)(?:_k\d+)", a)
    return m.group(1) if m else re.sub(r"_(sham|fit\d|s\d|\d+b[AB]?|reprov)$", "", a)


def k_of(a):
    m = re.search(r"_k(\d+)", a)
    return m.group(1) if m else "none"


PARTITIONS = {
    "(family,k)":       lambda a: (family(a), k_of(a)),
    "family only":      lambda a: (family(a),),
    "k only":           lambda a: (k_of(a),),
    "(family,k,sham)":  lambda a: (family(a), k_of(a), a.endswith("_sham")),
    "single cell [SHAM]": lambda a: (),
}


def loo_predict(arms, lab, cellf, targets):
    """Leave-one-out cell-majority; empty or TIED cell -> leave-one-out global majority.

    Returns (n_cell_determined, n_fallback, n_wrong) over `targets`. Deterministic: ties never
    resolve by list order, they fall through to the global rule.
    """
    cells = defaultdict(list)
    for a in arms:
        cells[cellf(a)].append(a)
    tot, n = sum(lab[x] for x in arms), len(arms)
    csum = {c: sum(lab[x] for x in v) for c, v in cells.items()}
    cd = fb = wr = 0
    for a in targets:
        c = cellf(a)
        m, sz = csum[c] - lab[a], len(cells[c]) - 1
        gmaj = (tot - lab[a]) * 2 > (n - 1)
        used_cell, pred = False, gmaj
        if sz and m * 2 != sz:
            used_cell, pred = True, m * 2 > sz
        if pred != lab[a]:
            wr += 1
        elif used_cell:
            cd += 1
        else:
            fb += 1
    return cd, fb, wr


def base_rate_acc(arms, lab, targets):
    """⭐ THE SHAM, as a number: leave-one-out GLOBAL majority only. No partition at all."""
    tot, n = sum(lab[x] for x in arms), len(arms)
    return sum(1 for a in targets if ((tot - lab[a]) * 2 > (n - 1)) == lab[a]) / len(targets)


def null_dist(arms, lab, cellf, targets, seed):
    """Permute the LABEL VECTOR over the whole population, refit, recompute on the same arms.

    Returns (sorted cell-determined shares, sorted GAINs). The gain null is the one the repaired
    statistic needs; the share null is kept because it is what was pre-registered.
    """
    rng, vals, sh, gn = random.Random(seed), [lab[a] for a in arms], [], []
    for _ in range(NDRAW):
        rng.shuffle(vals)
        p = dict(zip(arms, vals))
        cd, fb, _ = loo_predict(arms, p, cellf, targets)
        sh.append(cd / len(targets))
        gn.append((cd + fb) / len(targets) - base_rate_acc(arms, p, targets))
    sh.sort(); gn.sort()
    return sh, gn


def null95(arms, lab, cellf, targets, seed):
    out, _ = null_dist(arms, lab, cellf, targets, seed)
    return out[int(0.95 * (len(out) - 1))], sum(out) / len(out)


def main() -> int:
    led = json.loads(next(ARC.glob("R360_*/results/*.json")).read_text())
    arms, K = list(led["arms"]), led["k"]
    pass2 = set(led["clause2_admits"])
    pass23 = set(led["clause23_admits"])
    pass3 = pass23 | (set(arms) - pass2)
    passF3 = {a for a in arms if K.get(a) is not None and 1 < K[a] <= CARD_MAX}
    CL = {"F1 provenance": pass3, "F2 behaviour": pass2, "F3 size (repaired)": passF3}
    LAB = {n: {a: (a in adm) for a in arms} for n, adm in CL.items()}

    uniq = {}
    for n, adm in CL.items():
        oth = set(arms)
        for m, o in CL.items():
            if m != n:
                oth &= o
        uniq[n] = sorted(oth - adm)

    fk = PARTITIONS["(family,k)"]
    cells = defaultdict(list)
    for a in arms:
        cells[fk(a)].append(a)
    nonsingle = [a for a in arms if len(cells[fk(a)]) > 1]

    print("─── CONTROLS ───")
    plant = {a: (family(a) == "random") for a in arms}
    pos_cd, _, _ = loo_predict(arms, plant, fk, arms)
    pos = pos_cd / len(arms)
    ceiling = len(nonsingle) / len(arms)          # a singleton can NEVER be cell-determined
    floor95, floor_mu = null95(arms, plant, fk, arms, 7)
    thresh = (floor95 + ceiling) / 2
    band = floor95 < thresh < ceiling
    posok = pos >= thresh and band
    print(f"  POSITIVE  plant label=(family=='random'), a pure function of the partition")
    print(f"            floor(null95)={floor95:.4f} < t={thresh:.4f} < ceiling={ceiling:.4f} -> "
          f"{'band is REAL' if band else '⛔ THRESHOLD UNREACHABLE OR UNREFUSABLE'}")
    print(f"            observed {pos:.4f} -> {'PASS — the instrument returns non-zero' if posok else '⛔ FAIL'}")
    rng = random.Random(11)
    coin = {a: rng.random() < 0.5 for a in arms}
    g0_cd, _, _ = loo_predict(arms, coin, fk, arms)
    g0 = g0_cd / len(arms)
    g0ok = g0 < thresh
    print(f"  g=0       i.i.d. coin-flip label -> {g0:.4f} vs t={thresh:.4f} : "
          f"{'PASS — the control can FAIL' if g0ok else '⛔ FAIL — it passes at g=0'}")
    rng2 = random.Random(23)
    shuffled = list(arms)
    rng2.shuffle(shuffled)
    remap = dict(zip(arms, shuffled))             # size-preserving reassignment of cells
    negf = lambda a: fk(remap[a])
    neg_cd, _, _ = loo_predict(arms, LAB["F2 behaviour"], negf, uniq["F2 behaviour"])
    neg = neg_cd / len(uniq["F2 behaviour"])
    negn95, _ = null95(arms, LAB["F2 behaviour"], negf, uniq["F2 behaviour"], 31)
    negok = neg <= negn95
    print(f"  NEGATIVE  cell assignment shuffled (sizes preserved), majorities REFIT -> "
          f"{neg:.4f} vs its own null95 {negn95:.4f} : {'PASS — falls to the null' if negok else '⛔ FAIL'}")
    a1 = loo_predict(arms, LAB["F2 behaviour"], fk, uniq["F2 behaviour"])
    a2 = loo_predict(arms, LAB["F2 behaviour"], fk, uniq["F2 behaviour"])
    plc = a1 == a2
    print(f"  PLACEBO   two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      instrument '{INSTRUMENT_UNIT}' != claim '{CLAIM_UNIT}' -> "
          f"{'PASS — the gap is carried to the verdict' if unitok else '⛔ FAIL'}")
    sd = [null95(arms, LAB["F2 behaviour"], fk, uniq["F2 behaviour"], s)[1] for s in SEEDS]
    seedok = len(set(f"{x:.6f}" for x in sd)) > 1
    print(f"  SEEDS     3 nulls, means {[round(x,4) for x in sd]} -> "
          f"{'PASS — the seed flag changes the draws' if seedok else '⛔ FAIL — seed is inert'}")
    ctl = posok and g0ok and negok and plc and unitok and seedok

    print(f"\n─── THE GRID (G3/G4 — 2 populations × {len(PARTITIONS)} partitions × 3 clauses) ───")
    print(f"  ⭐ `gain` IS THE PRE-REGISTERED SHAM CONTRAST: accuracy WITH the partition minus the")
    print(f"     base rate (leave-one-out global majority, no partition). It is what the ingredient")
    print(f"     is worth. NEGATIVE means the partition predicts WORSE than the majority class.")
    print(f"  ⛔ POPULATION AXIS ADDED AFTER THE FIRST RUN, AND IT IS THE ROUND'S REPAIR: my")
    print(f"     REGISTERED population was a clause's OWN unique exclusions, which conditions on the")
    print(f"     label being predicted (§4 'conditioning on the outcome'). A clause excluding >50% of")
    print(f"     the population then has base rate 1.000 BY ALGEBRA and one excluding <50% has 0.000,")
    print(f"     so `gain`'s SIGN is forced before any data. The 'all 42 arms' rows are the")
    print(f"     admissible ones; the conditioned rows are kept and marked, never deleted.")
    print(f"  {'population':<19}{'partition':<20}{'clause':<20}{'n':>3}{'cell':>5}{'fall':>5}{'wrng':>5}"
          f"{'share':>7}{'nul95':>7}{'exces':>7}{'acc':>7}{'base':>7}{'gain':>7}{'g_n95':>7}{'p_gain':>8}")
    rows, arith_ok = [], True
    for popname, popf in (("unique excl [OUTCOME-CONDITIONED]", lambda c: uniq[c]),
                          ("all 42 arms", lambda c: arms)):
      for pname, pf in PARTITIONS.items():
        for cname in CL:
            tg = popf(cname)
            cd, fb, wr = loo_predict(arms, LAB[cname], pf, tg)
            arith_ok &= (cd + fb + wr == len(tg))
            nd, ng = null_dist(arms, LAB[cname], pf, tg, SEEDS[0])
            n95, nmu = nd[int(0.95 * (len(nd) - 1))], sum(nd) / len(nd)
            share, acc = cd / len(tg), (cd + fb) / len(tg)
            base = base_rate_acc(arms, LAB[cname], tg)
            p = (sum(1 for x in nd if x >= share) + 1) / (len(nd) + 1)
            g95 = ng[int(0.95 * (len(ng) - 1))]
            p_gain = (sum(1 for x in ng if x >= acc - base) + 1) / (len(ng) + 1)
            # ⭐ did the CELL ever change a prediction the base rate would have made?
            informative = sum(1 for a in tg if loo_predict(arms, LAB[cname], pf, [a])[0] == 1
                              and base_rate_acc(arms, LAB[cname], [a]) != 1.0)
            rows.append({"population": popname, "partition": pname, "clause": cname,
                         "n": len(tg), "n_unique": len(uniq[cname]),
                         "cell_determined": cd, "fallback": fb, "wrong": wr,
                         "share": share, "null95": n95, "null_mean": nmu, "p": p,
                         "excess": share - n95, "survives": share > n95,
                         "accuracy": acc, "base_rate": base, "gain": acc - base,
                         "gain_null95": g95, "p_gain": p_gain,
                         "gain_survives": (acc - base) > g95, "cell_informative": informative})
            print(f"  {popname[:18]:<19}{pname:<20}{cname:<20}{len(tg):>3}{cd:>5}{fb:>5}{wr:>5}"
                  f"{share:>7.3f}{n95:>7.3f}{share-n95:>+7.3f}{acc:>7.3f}{base:>7.3f}"
                  f"{acc-base:>+7.3f}{g95:>+7.3f}{p_gain:>8.4f}")
    print(f"  ARITHMETIC cell+fallback+wrong == n_unique in every cell -> "
          f"{'PASS' if arith_ok else '⛔ FAIL'}")
    ctl = ctl and arith_ok

    COND, FULL = "unique excl [OUTCOME-CONDITIONED]", "all 42 arms"
    pick = lambda pop, part, cl: next(r for r in rows if r["population"] == pop
                                      and r["partition"].startswith(part) and r["clause"] == cl)
    print(f"\n─── ⛔ WHAT THE SHAM DID TO MY OWN HEADLINE STATISTIC ───")
    sh = pick(COND, "single", "F2 behaviour")
    tr = pick(COND, "(family,k)", "F2 behaviour")
    print(f"  registered headline (cell-determined share)  treatment {tr['share']:.3f} vs SHAM {sh['share']:.3f}")
    print(f"  §4: a sham scoring ABOVE the treatment means the statistic does not isolate the")
    print(f"      ingredient. Under one cell EVERYTHING is 'cell-determined' — the category collapses.")
    print(f"  the contrast the sham was registered FOR      accuracy {tr['accuracy']:.3f} vs base "
          f"{tr['base_rate']:.3f}  ⇒ gain {tr['gain']:+.3f}")
    print(f"  cells that CHANGED a prediction the base rate would have made: {tr['cell_informative']}")
    nz = [r for r in rows if r["cell_informative"] > 0]
    print(f"  over the whole grid, cells with any informative prediction: {len(nz)} of {len(rows)}")
    print(f"\n─── ⭐ THE REPLACEMENT STATISTIC GETS ITS OWN CONTROLS (a dead proxy announces itself;")
    print(f"    its replacement returns numbers at once, so `gain` is controlled from scratch) ───")
    pcd, pfb, _ = loo_predict(arms, plant, fk, arms)
    pg = (pcd + pfb) / len(arms) - base_rate_acc(arms, plant, arms)
    _, png = null_dist(arms, plant, fk, arms, 7)
    pg95 = png[int(0.95 * (len(png) - 1))]
    ccd, cfb, _ = loo_predict(arms, coin, fk, arms)
    cg = (ccd + cfb) / len(arms) - base_rate_acc(arms, coin, arms)
    _, cng = null_dist(arms, coin, fk, arms, 7)
    cg95 = cng[int(0.95 * (len(cng) - 1))]
    gain_posok, gain_g0ok = pg > pg95, cg <= cg95
    print(f"  POSITIVE(gain) plant (family=='random') -> gain {pg:+.3f} vs its null95 {pg95:+.3f} : "
          f"{'PASS — the gain statistic returns non-zero' if gain_posok else '⛔ FAIL'}")
    print(f"  g=0    (gain)  i.i.d. coin flip        -> gain {cg:+.3f} vs its null95 {cg95:+.3f} : "
          f"{'PASS — it can FAIL' if gain_g0ok else '⛔ FAIL — it passes at g=0'}")
    ctl = ctl and gain_posok and gain_g0ok

    print(f"\n  ⭐ THE ADMISSIBLE POPULATION — gain over the base rate on ALL 42 ARMS:")
    for cl in CL:
        gs = [(r['partition'], r['gain']) for r in rows if r["population"] == FULL and r["clause"] == cl]
        print(f"    {cl:<20}{'  '.join(f'{p.split()[0][:9]}:{g:+.3f}' for p, g in gs)}")
    print(f"    ⚠ F3 under `k only` is a DERIVATION, not a measurement: F3 IS the predicate "
          f"1 < k <= {CARD_MAX}, so a k-partition must recover it exactly.")

    def bh(key):
        rk, mt, out = sorted(rows, key=lambda r: r[key]), len(rows), []
        for i, r in enumerate(rk):
            if r[key] <= 0.10 * (i + 1) / mt:
                out = rk[:i + 1]
        return out
    bh_surv, bh_gain = bh("p"), bh("p_gain")
    tag = lambda rs: [("★" if r["population"] == FULL else "cond·") + r["partition"].split()[0][:9]
                      + "/" + r["clause"].split()[0] for r in rs]
    print(f"\n  ⭐ BH q=0.10 over all {len(rows)} cells")
    print(f"     on the REGISTERED share statistic -> {len(bh_surv)}: {tag(bh_surv) or 'NONE'}")
    print(f"     on the REPAIRED gain  statistic  -> {len(bh_gain)}: {tag(bh_gain) or 'NONE'}")
    print(f"     (★ = admissible population; cond· = outcome-conditioned, reported not used)")

    pk = lambda pop, part, cl: next(r for r in rows if r["population"] == pop
                                    and r["partition"] == part and r["clause"] == cl)
    A_f2, A_f1, A_f3 = (pk(COND, "(family,k)", c)["cell_determined"] for c in
                        ("F2 behaviour", "F1 provenance", "F3 size (repaired)"))
    B = pk(COND, "(family,k)", "F2 behaviour")["excess"]
    C = sum(1 for p in PARTITIONS
            if pk(COND, p, "F2 behaviour")["share"] > pk(COND, p, "F1 provenance")["share"])
    D = sum(1 for p in PARTITIONS
            if pk(COND, p, "F2 behaviour")["share"] > pk(COND, p, "F3 size (repaired)")["share"])

    print(f"\n─── ⭐ WHY THE CELLS DETERMINE: ARE THEY REPLICATES WE SHIPPED? ───")
    det = [a for a in uniq["F2 behaviour"]
           if loo_predict(arms, LAB["F2 behaviour"], fk, [a])[0] == 1]
    repl = [a for a in det if len(cells[fk(a)]) > 1 and
            all(family(x) == family(a) for x in cells[fk(a)])]
    dedup = sorted({fk(a): a for a in arms}.values())      # one arm per cell -> every cell singleton
    dd_cd, dd_fb, dd_wr = loo_predict(dedup, LAB["F2 behaviour"], fk,
                                      [a for a in uniq["F2 behaviour"] if a in dedup])
    print(f"  F2 cell-determined arms: {len(det)} -> {det}")
    print(f"  of those, in a cell made ONLY of same-generator replicates/shams: {len(repl)} of {len(det)}")
    print(f"  ⭐ DEDUPLICATED POPULATION (one arm per (family,k) cell, n={len(dedup)}): "
          f"cell-determined {dd_cd}, fallback {dd_fb}, wrong {dd_wr}")
    print(f"     [DERIVATION, not evidence: every cell is a singleton by construction, so "
          f"cell-determined CANNOT exceed 0. Stated to name the mechanism, not to test it.]")

    print(f"\n─── REGISTERED ───")
    print(f"  A [DERIVED] F2 cell-det = 13 [6,18] -> {A_f2}: error {A_f2-13:+d}   "
          f"F1 = 2 -> {A_f1} ({A_f1-2:+d})   F3 = 0 -> {A_f3} ({A_f3-0:+d})")
    print(f"  B [MEASURED] F2 excess over its null95 = +0.35 [+0.05,+0.65] -> {B:+.4f}: "
          f"error {B-0.35:+.4f}  {'INSIDE' if 0.05 <= B <= 0.65 else '⛔ OUTSIDE'}")
    print(f"  C [MEASURED] specs where F2's share > F1's = 4 of 5 [1,5] -> {C}: error {C-4:+d}")
    print(f"  DIRECTIONAL F2 > F3 in a majority of {len(PARTITIONS)} specs -> {D} : "
          f"{'HOLDS' if D * 2 > len(PARTITIONS) else '⛔ FAILS'}")

    surv = [r for r in rows if r["survives"]]
    gsurv = [r for r in rows if r["gain_survives"]]
    m = len(rows)
    dead = [("★" if r["population"] == FULL else "cond·") + r["partition"] + "/" + r["clause"]
            for r in rows if not r["gain_survives"]]
    print(f"\n  MULTIPLICITY: {m} cells tested. Uncorrected: {len(surv)} beat their share null95, "
          f"{len(gsurv)} beat their GAIN null95. BH q=0.10: {len(bh_surv)} / {len(bh_gain)}.")
    print(f"  NON-SURVIVORS ON THE REPAIRED STATISTIC ({len(dead)} of {m}, reported per G3):")
    for d in dead: print(f"     {d}")

    kill_B = not any(r["survives"] for r in rows if r["clause"] == "F2 behaviour")
    kill_D = not any(r["survives"] for r in rows)
    f2full = [r for r in rows if r["population"] == FULL and r["clause"] == "F2 behaviour"]
    f1full = [r for r in rows if r["population"] == FULL and r["clause"] == "F1 provenance"]
    canon = pk(FULL, "(family,k)", "F2 behaviour")
    gains_neg = not any(r["gain_survives"] for r in f2full)
    best_f2 = max(r["gain"] for r in f2full)
    best_f1 = max(r["gain"] for r in f1full)
    res = 1 / len(arms)
    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; these shares would be silence, not a measurement."
    elif gains_neg:
        world = (
            f"⭐⭐⭐ E BASE RATE — R703's PREMISE IS REFUTED: F2's WEIGHT IS NOT OUR PARAMETERISATION. "
            f"On the admissible population (all {len(arms)} arms, NOT the outcome-conditioned subset), "
            f"the generator name is worth {canon['gain']:+.3f} to F2 under the canonical (family,k) "
            f"partition — base rate {canon['base_rate']:.3f}, with the partition "
            f"{canon['accuracy']:.3f} — and its best gain over all {len(PARTITIONS)} partitions is "
            f"{best_f2:+.3f}, i.e. {round(best_f2*len(arms))} arms of {len(arms)}, which no "
            f"partition clears its own permutation null with. ⭐ SO THE ASYMMETRY R703 FOUND (20 "
            f"unique exclusions against 4 and 2) IS A COUNT, NOT A SIGNAL: F2 excludes "
            f"{sum(1 for a in arms if not LAB['F2 behaviour'][a])} of {len(arms)} arms, and a "
            f"demanding clause produces many unique exclusions whatever it encodes. ⛔ AND BOTH OF MY "
            f"OWN STATISTICS FAILED FIRST, EACH CAUGHT BY A CONTROL I REGISTERED: the cell-determined "
            f"share was refuted by its SHAM ({tr['share']:.3f} treatment vs {sh['share']:.3f} sham — "
            f"under one cell every prediction counts as cell-determined), and the population was "
            f"OUTCOME-CONDITIONED, which fixes the base rate at 1.000 for any clause excluding a "
            f"majority and 0.000 for any clause excluding a minority, BY ALGEBRA and before any data. "
            f"⚠ F1 gains {best_f1:+.3f} at best and F3 {max(r['gain'] for r in rows if r['population'] == FULL and r['clause'].startswith('F3')):+.3f}, "
            f"but F3's is a DERIVATION — F3 IS the predicate 1 < k <= {CARD_MAX}, so a k-partition "
            f"must recover it. ⚠ UNIT GAP: instrument unit is {INSTRUMENT_UNIT}, claim unit is "
            f"{CLAIM_UNIT}; at n={len(arms)} the resolution is {res:.3f} per arm, so a gain under "
            f"{2*res:.3f} is two arms and the cross-clause ORDERING is reported while the "
            f"cross-clause DIFFERENCE is not.")
    else:
        world = (f"⭐⭐ A PARAMETERISATION — on all {len(arms)} arms the name is worth "
                 f"{canon['gain']:+.3f} to F2 under (family,k) (best {best_f2:+.3f} across "
                 f"{len(PARTITIONS)} partitions) and at least one partition clears its own gain null, "
                 f"so R703's premise survives: part of F2's weight is our parameterisation. ⚠ but "
                 f"{len(repl)} of {len(det)} determining arms are same-generator replicates we "
                 f"shipped, and deduplicated to one arm per cell the cell contribution is {dd_cd}.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "recoverability.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "rows": rows,
        "unique": uniq, "f2_cell_determined_arms": det, "f2_replicate_cells": repl,
        "dedup_n": len(dedup), "dedup_cell_determined": dd_cd,
        "positive": {"observed": pos, "floor95": floor95, "threshold": thresh, "ceiling": ceiling,
                     "band_real": band},
        "g0": g0, "negative": {"observed": neg, "null95": negn95},
        "gain_controls": {"positive": pg, "positive_null95": pg95, "g0": cg, "g0_null95": cg95,
                          "both_pass": gain_posok and gain_g0ok},
        "admissible_population": FULL, "canonical_f2_gain": canon["gain"],
        "best_f2_gain": best_f2, "best_f1_gain": best_f1,
        "f2_beats_own_gain_null_anywhere": not gains_neg,
        "registered": ("A[DERIVED] F2 cell-det 13 [6,18]; B[MEASURED] excess +0.35 [+0.05,+0.65]; "
                       "C[MEASURED] specs F2>F1 = 4 of 5 [1,5]; directional F2>F3 in a majority"),
        "observed": {"A_f2": A_f2, "A_f1": A_f1, "A_f3": A_f3, "B": B, "C": C, "D": D},
        "kill_fired": kill_B or kill_D,
        "cells_tested": m, "cells_surviving_uncorrected": len(surv),
        "bh_survivors_share_stat": [r["population"] + "/" + r["partition"] + "/" + r["clause"]
                                    for r in bh_surv],
        "bh_survivors_gain_stat": [r["population"] + "/" + r["partition"] + "/" + r["clause"]
                                   for r in bh_gain],
        "sham_refuted_headline": tr["share"] < sh["share"],
        "f2_gain_over_base_rate_CONDITIONED_POP": tr["gain"],
        "f2_cell_informative_CONDITIONED_POP": tr["cell_informative"],
        # ⚠ NOT "all gains <= 0" — one F2 gain is positive (+0.048). This says NO F2 partition
        #   clears its OWN permutation null, which is the weaker and the true statement.
        "f2_no_partition_beats_its_gain_null": gains_neg,
        "limit": ("(family,k) is OUR parameterisation of arms WE built; and a share over 4 or 2 arms "
                  "is not a clause-level property — the ordering is reported, the difference is not."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
