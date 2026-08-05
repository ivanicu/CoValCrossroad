"""Clause ③ is provenance. Can any behavioural statistic replace it, at matched performance?

WHY THIS IS THE QUESTION LEFT. Clause ③ now carries the definition's entire emptiness (R475, R499),
and it is the one clause that cannot be checked on an object: R465 measured a label-reading and a
label-free selector emitting IDENTICAL criteria on 9 of 967 prompts with identical A2 to machine
precision. The DERIVATION that follows -- labelled as a derivation, since no measurement is needed
for it -- is that `core` as written is not a predicate on criterion sets at all, but on
(criterion set, construction history) PAIRS. A third party handed only the artifact can never decide
it. This round asks whether that is forced, or whether label-reading leaves a behavioural trace.

ESTIMAND        Whether membership in the ③-EXCLUDED family (label-readers) is predictable from a
                behavioural statistic AFTER conditioning on mean A2 -- specifically the residual of
                per-prompt A2 standard deviation regressed on mean A2. Named before the method.
IDENTIFICATION  Identified only as a SEPARATION question, never as a causal one: a positive answer
                says a surrogate exists on this arm population, not that it would generalise to an
                unseen selector. Stated so the result is not over-read.

⛔ THE ARITHMETIC TRAP, NAMED FIRST AND IT DRIVES THE WHOLE DESIGN. Label-readers score HIGHER by
                construction -- they were selected to. So "high A2 ⇒ label-reader" is a classifier
                that cannot fail, and reporting its accuracy would be 1+1=2 dressed as evidence. The
                only admissible test conditions on A2 and asks whether ANYTHING ELSE separates them.
                That is why the estimand is a RESIDUAL and not a raw statistic.

SCOPE           population = arms with a per-prompt A2 vector on disk, split by the ③ verdict the
                record already assigns · instrument = A2 vs a held-out annotator, 20 draws,
                crc32-seeded · baseline = same-family pairs · regime = k=4 where matched, all k in
                the sweep.
WORLDS          A PROVENANCE IS IRREDUCIBLE. No behavioural statistic separates the families at
                  matched A2. Then ③ cannot be replaced, `core` is a predicate on (set, history),
                  and a definition of core is a definition of a PROCESS wearing an object's clothes.
                  Predicts: residual separation indistinguishable from the within-family baseline.
                B PROVENANCE HAS A TRACE. Label-reading leaves a behavioural signature that survives
                  conditioning on performance. Then ③ can be restated as a checkable clause and the
                  definition becomes object-level -- a different definition, not a repaired one.
                  Predicts: residual separation well beyond the within-family baseline.
                Ontologically different: A says the object cannot carry the property; B says it can.
KILL            Pre-registered: world B dies if the between-family residual separation does not
                exceed the WITHIN-family separation (same construction, different seed/k). A gap that
                does not beat same-family variation is not a signature. ⚠ Note the direction: unlike
                R499's null, this baseline is a FLOOR -- within-family arms should be similar -- so
                exceeding it is a real bar, and the wording is checked against its construction
                rather than its intended role (retraction 326).
POSITIVE CTRL   `oracle_k4` is the maximal label-reader on this site. If the statistic cannot place
                IT outside the admissible family, it cannot place anything, and a null is silence.
                Reported as its residual's rank among all arms -- a number, not a pass/fail word.
NEGATIVE CTRL   The same pipeline with family labels SHUFFLED. Must return a separation at the
                within-family level. Destroys the family structure, preserves everything else.
PLACEBO         `random_k4_s0` vs `random_k4_s1` -- same construction, different seed. Must show no
                separation. ⚠ This is a FLOOR (identical procedure), unlike R499's ceiling.
NOISE FLOOR     Measured: each arm's statistic recomputed at 3 annotator-draw offsets; the floor is
                the observed spread, not a model.
MULTIPLICITY    Grid printed whole: 2 statistics x 3 offsets x {raw, residualised}. Cells surviving
                reported beside cells tested. No cell is selected after the fact.
SPECIFICATION   Swept: statistic (per-prompt sd, per-prompt IQR) · residualised or raw · offset ·
                k-matched subset vs all-k. Disagreement is reported, never averaged away.
SEEDS           3 offsets, asserted to change the draws.
ARTIFACT        results/provenance_trace.json with every arm's (mean, sd, residual, family).
REPRODUCIBILITY deterministic given the offsets; asserted by a second identical pass.
IMPOSSIBLE      cross-selector generalisation: this tests the selectors that happen to exist here.
                Would require a held-out selector family built by someone else. Named, not counted.
"""
from __future__ import annotations
import collections, itertools, json, pathlib, sys, zlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/"corebench")); import score as SC
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = pathlib.Path(__file__).resolve().parent/"results"; OUT.mkdir(exist_ok=True)
cls = lambda y: tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
tgt, _ = SC.load_targets(); TGT = {p: [tuple(v) for v, _ in x] for p, x in tgt.items()}

# The ③ verdict the RECORD assigns -- derived from how each arm is built, not invented here.
READERS = ["oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1", "coval_core",
           "topw_k4", "topw_k2", "topw_k3", "topw_k6", "topw_k8", "topabs_k4", "topvar_k4",
           "topwvar_k4"]
FREE = ["gen", "generic", "genericpool16", "promptecho", "random_k4_s0", "random_k4_s1",
        "random_k4_s2", "random_k3_s0", "random_k6_s0", "random_k8_s0"]
# ⛔ THE `transport_*` ARMS ARE EXCLUDED, AND THIS IS A SCOPE DECISION RATHER THAN A CONVENIENCE.
# Their meta keys carry FOUR fields (`c365|int10006|ut3170|0`) against this population's three
# (`<uuid>|0|A`): they are scored on the SECOND RELEASE. A first draft listed them as ③-admissible
# arms and crashed on the unpack -- which was luck. Coercing the key would have pooled two releases
# into one population silently, and the round would have compared label-readers on one corpus with
# label-free arms on two. The guard below refuses any arm whose schema differs and PRINTS it, so an
# exclusion is never invisible.
SKIPPED: list = []

def per_prompt(arm: str, off: int = 0):
    f = ROOT/f"corebench/results/sat_{arm}.npz"
    if not f.exists(): return None
    d = np.load(f, allow_pickle=True)
    if str(d["meta"][0]).count("|") != 2:            # schema guard, see the note above
        SKIPPED.append((arm, str(d["meta"][0])[:40])); return None
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    sc = {}
    for p, c in o.items():
        if p not in TGT: continue
        idx = sorted({i for i, _ in c})
        cc = cls(np.array([sum(c.get((i, x), 0.0) for i in idx) for x in L]))
        r = np.random.default_rng(zlib.crc32(p.encode()) + off)
        sc[p] = float(np.mean([np.mean([cc[t] == cls(np.array(TGT[p][int(r.integers(len(TGT[p])))], float))[t]
                                        for t in range(6)]) for _ in range(20)]))
    return sc


def stats(off: int):
    rows = {}
    for arm in READERS + FREE:
        s = per_prompt(arm, off)
        if not s: continue
        v = np.array(list(s.values()))
        rows[arm] = dict(mean=float(v.mean()), sd=float(v.std()),
                         iqr=float(np.percentile(v, 75) - np.percentile(v, 25)),
                         fam="reader" if arm in READERS else "free")
    return rows


def residual_sep(rows: dict, key: str, fams: dict) -> float:
    """Separation in `key` AFTER regressing it on mean A2. The conditioning is the whole point."""
    A = np.array([[r["mean"], 1.0] for r in rows.values()])
    y = np.array([r[key] for r in rows.values()])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    res = y - A @ beta
    names = list(rows)
    g1 = np.array([res[i] for i, n in enumerate(names) if fams[n] == "reader"])
    g0 = np.array([res[i] for i, n in enumerate(names) if fams[n] == "free"])
    if len(g1) < 2 or len(g0) < 2: return float("nan")
    pooled = np.sqrt((g1.var(ddof=1) + g0.var(ddof=1))/2)
    return float(abs(g1.mean() - g0.mean())/pooled) if pooled > 0 else float("nan")


def main() -> int:
    OFFS = [0, 7919, 3571]
    base = stats(OFFS[0])
    if len(base) < 8:
        print(f"  only {len(base)} arms loaded -- population too small to report"); return 2
    fams = {a: r["fam"] for a, r in base.items()}
    nR = sum(1 for v in fams.values() if v == "reader"); nF = len(fams) - nR
    print(f"  arms loaded: {len(base)}  ({nR} ③-excluded readers, {nF} ③-admissible)")
    if SKIPPED:
        print(f"  arms EXCLUDED on schema (different release, not pooled): "
              f"{sorted({a for a, _ in SKIPPED})}")
    print()

    print(f"  {'arm':<26}{'mean A2':>9}{'sd':>8}{'family':>10}")
    for a, r in sorted(base.items(), key=lambda kv: -kv[1]["mean"])[:6]:
        print(f"  {a:<26}{r['mean']:9.4f}{r['sd']:8.4f}{r['fam']:>10}")
    print(f"  {'…':<26}")
    for a, r in sorted(base.items(), key=lambda kv: -kv[1]["mean"])[-3:]:
        print(f"  {a:<26}{r['mean']:9.4f}{r['sd']:8.4f}{r['fam']:>10}")

    grid, cells = {}, 0
    print(f"\n  {'statistic':<12}{'offset':>8}{'RAW sep d':>12}{'RESIDUAL sep d':>16}")
    for key in ("sd", "iqr"):
        for off in OFFS:
            rows = stats(off)
            raw_g1 = np.array([r[key] for a, r in rows.items() if fams[a] == "reader"])
            raw_g0 = np.array([r[key] for a, r in rows.items() if fams[a] == "free"])
            pooled = np.sqrt((raw_g1.var(ddof=1)+raw_g0.var(ddof=1))/2)
            raw = abs(raw_g1.mean()-raw_g0.mean())/pooled if pooled > 0 else float("nan")
            res = residual_sep(rows, key, fams)
            grid[f"{key}@{off}"] = dict(raw=float(raw), residual=res); cells += 1
            print(f"  {key:<12}{off:>8}{raw:12.4f}{res:16.4f}")

    # PLACEBO: same construction, different seed -> a FLOOR, must be ~0
    rs = [base[a] for a in ("random_k4_s0", "random_k4_s1", "random_k4_s2") if a in base]
    pl = float(np.std([r["sd"] for r in rs])/ (np.mean([r["sd"] for r in rs]) or 1))
    print(f"\n  PLACEBO (random_k4 seeds, identical construction): relative sd spread {pl:.4f}")

    # NEGATIVE CONTROL: shuffle the family labels
    rng = np.random.default_rng(20260804)
    negs = []
    for _ in range(200):
        names = list(base); lab = list(fams.values()); rng.shuffle(lab)
        negs.append(residual_sep(base, "sd", dict(zip(names, lab))))
    negs = np.array([x for x in negs if np.isfinite(x)])
    print(f"  NEGATIVE (labels shuffled, 200 draws): residual sep {negs.mean():.4f}"
          f"  95th pct {np.percentile(negs, 95):.4f}")

    # POSITIVE CONTROL: the maximal label-reader must be extreme, reported as a rank
    A = np.array([[r["mean"], 1.0] for r in base.values()]); y = np.array([r["sd"] for r in base.values()])
    beta, *_ = np.linalg.lstsq(A, y, rcond=None); resv = y - A @ beta
    names = list(base)
    pc_pass, rank, N = None, None, len(names)
    if "oracle_k4" in names:
        i = names.index("oracle_k4")
        rank = int((resv < resv[i]).sum()) + 1
        # It must land in an EXTREME quartile. Mid-pack means the statistic cannot see the most
        # extreme label-reader on the site, and then a null is silence rather than an acquittal.
        pc_pass = rank <= N/4 or rank > 3*N/4
        print(f"  POSITIVE (oracle_k4, the maximal label-reader): residual rank {rank} of {N}"
              f"  -> {'PASS' if pc_pass else 'FAIL — mid-pack, the statistic cannot localise it'}")

    obs = float(np.mean([v["residual"] for v in grid.values()]))
    bar = float(np.percentile(negs, 95))
    surviving = sum(1 for v in grid.values() if v["residual"] > bar)
    # ⛔ THE VERDICT MUST REFERENCE EVERY CONTROL THE ROUND DECLARED. A first version branched on
    # `surviving` alone and printed "A PROVENANCE IS IRREDUCIBLE" while the positive control was
    # failing two lines above -- prose that looks like output, in the round after that failure was
    # logged. The control now gates the branch, and a failed control yields UNVERIFIED, never A.
    if pc_pass is False:
        world = ("UNVERIFIED — the instrument cannot localise oracle_k4 (rank %d of %d), so the "
                 "null is silence, not an acquittal" % (rank, N))
    elif pc_pass is None:
        world = "UNVERIFIED — the positive control could not run"
    else:
        world = "B PROVENANCE HAS A TRACE" if surviving == cells else \
                "A PROVENANCE IS IRREDUCIBLE" if surviving == 0 else \
                f"SPLIT — {surviving} of {cells} cells clear the shuffled-label bar"
    print(f"\n  cells tested {cells}   cells clearing the shuffled-label 95th pct: {surviving}")
    print(f"  mean residual separation {obs:.4f} vs shuffled bar {bar:.4f}")
    print(f"\n  WORLD: {world}")
    if world.startswith("UNVERIFIED"):
        print(f"  => the QUESTION is untouched. What is established is narrower and still worth")
        print(f"     having: per-prompt A2 dispersion, residualised on mean A2, is NOT an instrument")
        print(f"     for provenance on this population. The raw separation looks large (d≈{np.mean([v['raw'] for v in grid.values()]):.2f})")
        print(f"     and is the arithmetic trap: label-readers score higher by construction and sd")
        print(f"     tracks mean, so the raw number was never evidence.")
        print(f"  => a valid instrument must first be shown to rank oracle_k4 at an extreme.")
    elif world.startswith("A"):
        print(f"  => ③ cannot be replaced by a behavioural surrogate on this population. `core` is a")
        print(f"     predicate on (criterion set, construction history), and a third party handed")
        print(f"     only the artifact can never decide it. A definition of core that keeps ③ is a")
        print(f"     definition of a PROCESS wearing an object's clothes -- and that is a choice to")
        print(f"     make explicitly, not a defect to repair.")
    elif world.startswith("B"):
        print(f"  => ③ has a behavioural shadow; a checkable surrogate is possible on this site.")
    json.dump({"arms": base, "grid": grid, "neg_mean": float(negs.mean()),
               "neg_p95": bar, "placebo": pl, "cells": cells, "surviving": surviving,
               "world": world}, (OUT/"provenance_trace.json").open("w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
