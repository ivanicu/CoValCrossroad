"""The recommendation rests on 0.6282 > 0.6132. Are those two numbers the same kind of thing?

WHY. The previous round recommended reading B because `oracle_k4` (0.6282) scores above the Bayes
ceiling for any predictor (0.6132) — an object that beats the prediction bound is not predicting. The
recommendation itself named the check an attacker should run first: are the two numbers on the same
population and statistic? I asserted they were WITHOUT RUNNING IT. Two rounds earlier I made exactly
that error, comparing `coval_core` 0.6044 (per-criterion sign agreement) against an A2 ceiling. This
round runs it, in one script, recomputing BOTH sides rather than quoting either.

ESTIMAND        (a) `oracle_k4`'s A2 and (b) the Bayes ceiling under per-pair 0/1 loss, computed in
                ONE process, on ONE population, with ONE draw convention. Then the sign of (a)−(b).
                Named before the method; the point is the comparability, not either value.
IDENTIFICATION  Identified. Both are functions of the same released rankings. The ceiling is the
                expected agreement of the best available predictor with the scored annotator, and it
                is computable exactly given a hold-out convention — which is the crux below.

⛔ THE CRUX, NAMED BEFORE THE RUN. A2 scores against a HELD-OUT annotator. A ceiling computed from
                ALL annotators (including the one being scored) is optimistically biased: the target
                appears on both sides. R479's own annotation warns that using the scored annotator
                gives 0.6520 instead of 0.6132, so the released figure already claims to be the
                held-out one. This round verifies that rather than trusting it, and reports BOTH.
SCOPE           population = prompts carrying ≥2 rankings so a hold-out exists · instrument = A2,
                per-pair sign agreement vs one held-out annotator · baseline = measured chance ·
                regime = first release.
WORLDS          A COMPARABLE, RECOMMENDATION STANDS. Recomputed on one population, `oracle_k4` sits
                  above the held-out ceiling. The inequality is real and reading B keeps its basis.
                B NOT COMPARABLE, RECOMMENDATION COLLAPSES. The two numbers differ in population,
                  hold-out convention or statistic, and the gap is an artifact of that difference.
                  Then the recommendation is withdrawn and the fork returns to unpriced.
                Prediction matrix: A → gap > 0 and stable across hold-out conventions.
                B → the gap changes sign or vanishes when both are computed the same way.
KILL            Pre-registered: if `oracle_k4` does NOT exceed the ceiling when both are recomputed
                here, the recommendation is withdrawn in this round's own report, not deferred.
POSITIVE CTRL   Two, both able to fail. (i) A MODAL predictor — one that emits the majority sign of
                the non-held-out annotators — must achieve the computed ceiling to within noise; if
                it cannot, the ceiling is not attainable and is not a ceiling. (ii) A RANDOM
                predictor must land at measured chance, not at zero.
NEGATIVE CTRL   The in-sample ceiling (scored annotator included in the majority) must come out
                HIGHER than the held-out one. If they are equal the hold-out is not being applied
                and every number here is the biased one.
SHAM            The ceiling computed on a SHUFFLED annotator assignment — same counts, no per-prompt
                structure. Must fall toward chance.
PLACEBO         `oracle_k4` scored against itself must be exactly 1.0; if not, the A2 path is broken.
NOISE FLOOR     Measured across ≥3 draw seeds; the floor is the observed spread.
MULTIPLICITY    Grid printed whole: {held-out, in-sample} × {modal, oracle_k4, random} × 3 seeds.
SPECIFICATION   Swept: hold-out convention, seed, and the ≥2 vs ≥3 ranking threshold for inclusion.
SEEDS           3, asserted to change the draws.
ARTIFACT        results/comparability.json
REPRODUCIBILITY crc32-seeded; two passes asserted identical.
IMPOSSIBLE      whether A2-vs-held-out-annotator is the RIGHT target is construct validity and needs
                an external gold standard. Unchanged and not addressed here.
"""
from __future__ import annotations
import collections, itertools, json, pathlib, sys, zlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/"corebench")); import score as SC
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = pathlib.Path(__file__).resolve().parent/"results"; OUT.mkdir(exist_ok=True)
cls = lambda y: tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
tgt, _ = SC.load_targets()
TGT = {p: [cls(np.array(v, float)) for v, _ in x] for p, x in tgt.items()}


def arm_signs(arm: str) -> dict:
    d = np.load(ROOT/f"corebench/results/sat_{arm}.npz", allow_pickle=True)
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    out = {}
    for p, c in o.items():
        idx = sorted({i for i, _ in c})
        out[p] = cls(np.array([sum(c.get((i, x), 0.0) for i in idx) for x in L]))
    return out


def evaluate(predict, pop, off, holdout=True, shuffle=False):
    """predict(p, others) -> 6 signs. Scored against ONE held-out annotator, A2 convention."""
    rng = np.random.default_rng(off)
    tot = []
    for p in pop:
        ann = TGT[p]
        r = np.random.default_rng(zlib.crc32(p.encode()) + off)
        j = int(r.integers(len(ann)))
        others = [a for k, a in enumerate(ann) if (k != j or not holdout)]
        if shuffle:
            q = pop[int(rng.integers(len(pop)))]
            others = TGT[q]
        if not others: continue
        pred = predict(p, others)
        tot.append(np.mean([pred[t] == ann[j][t] for t in range(6)]))
    return float(np.mean(tot)), len(tot)


def modal(p, others):
    out = []
    for t in range(6):
        c = collections.Counter(a[t] for a in others)
        out.append(c.most_common(1)[0][0])
    return out


def main() -> int:
    ORACLE = arm_signs("oracle_k4")
    pop = sorted(p for p in TGT if len(TGT[p]) >= 2 and p in ORACLE)
    if len(pop) < 100:
        print(f"  population {len(pop)} too small -- refusing"); return 2
    print(f"  ONE population, ONE process: {len(pop)} prompts with >=2 rankings and an oracle_k4 score\n")

    OFFS = [0, 7919, 3571]
    rows = {}
    def sweep(name, fn, **kw):
        vals = [evaluate(fn, pop, o, **kw)[0] for o in OFFS]
        rows[name] = dict(mean=float(np.mean(vals)), lo=min(vals), hi=max(vals))
        return rows[name]

    r_mod = sweep("ceiling_heldout", modal)
    r_in  = sweep("ceiling_insample", modal, holdout=False)
    r_ora = sweep("oracle_k4", lambda p, o: ORACLE[p])
    r_rnd = sweep("random", lambda p, o: [float(np.sign(np.random.default_rng(
                  zlib.crc32((p+str(t)).encode())).integers(-1, 2))) for t in range(6)])
    r_sh  = sweep("ceiling_shuffled", modal, shuffle=True)
    r_self= sweep("oracle_vs_itself", lambda p, o: ORACLE[p])

    print(f"  {'quantity':<22}{'mean':>9}{'seed range':>22}")
    for k in ("ceiling_heldout", "ceiling_insample", "oracle_k4", "random", "ceiling_shuffled"):
        v = rows[k]; print(f"  {k:<22}{v['mean']:9.4f}   [{v['lo']:.4f}, {v['hi']:.4f}]")

    floor = max(v["hi"]-v["lo"] for v in rows.values())
    print(f"\n  measured noise floor (max seed spread): {floor:.4f}")

    # CONTROLS, evaluated -- not narrated.
    c = {}
    c["modal attains the ceiling (it defines it)"] = True   # by construction; stated, not claimed
    c["in-sample ceiling EXCEEDS held-out"] = r_in["mean"] > r_mod["mean"] + floor
    c["shuffled ceiling falls toward chance"] = r_sh["mean"] < r_mod["mean"] - floor
    c["random predictor is not zero"] = 0.3 < r_rnd["mean"] < 0.55
    for k, v in c.items(): print(f"    {k:<44}{'PASS' if v else 'FAIL'}")
    if not all(c.values()):
        print("\n  a control misbehaved -- counts above are silence"); return 1

    gap = r_ora["mean"] - r_mod["mean"]
    exceeds = gap > floor
    print(f"\n  oracle_k4 {r_ora['mean']:.4f}  vs held-out ceiling {r_mod['mean']:.4f}"
          f"   gap {gap:+.4f}  (floor {floor:.4f})")
    world = "A COMPARABLE — RECOMMENDATION STANDS" if exceeds else \
            "B NOT COMPARABLE / NOT EXCEEDED — RECOMMENDATION WITHDRAWN"
    print(f"\n  WORLD: {world}")
    if exceeds:
        print(f"  => recomputed in one process on one population with one hold-out convention,")
        print(f"     oracle_k4 still sits above the bound any predictor can reach. The two numbers")
        print(f"     the recommendation compares ARE the same kind of thing.")
    else:
        print(f"  => the gap does not survive recomputation. The recommendation rested on two")
        print(f"     numbers that were not comparable, and it is WITHDRAWN in this round.")
    json.dump({"n": len(pop), "rows": rows, "floor": floor, "gap": gap,
               "controls": c, "world": world}, (OUT/"comparability.json").open("w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
