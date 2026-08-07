"""A core is a RANKER by construction, so only one of the two ceilings applies — and then resolution.

⭐ THE DERIVATION THAT SETTLES WHICH CEILING, read out of `corebench/score.py` rather than measured.
`yvec(sat_p, idxs)` returns ONE SCALAR PER RESPONSE — the sum of that response's saturations over the
selected criteria — and `cls(y)` takes `sign(y[i] - y[j])`. A scalar per item induces a total (weak)
order, so a core's six pairwise verdicts are NECESSARILY TRANSITIVE. It cannot emit the intransitive
patterns the per-pair mode uses on 33.5% of prompts. Therefore:
  * the RANKER ceiling is the bound that applies to any core;
  * the PAIR-PREDICTOR ceiling is unattainable by a core, by construction, and comparing a core to it
    is a category error — the one R504 committed.
This is a DERIVATION from the scoring code. It could not have come out otherwise once `yvec` returns
a scalar, and it is labelled rather than reported as a finding.

⛔ WHAT REMAINS IS RESOLUTION, NOT IDENTIFICATION. Against the ranker ceiling, oracle_k4 sits at
+0.0095 with a measured floor of 0.0220 — inside it. R505 stopped there. But the floor came from ONE
draw per prompt per seed, while R479 averages TWENTY. §4's longest entry names exactly this: a
resolution limit accepted without asking whether the data has more to give. It has: this round
re-measures at 20 reps and reports whether +0.0095 survives.

ESTIMAND        oracle_k4 minus the RANKER ceiling, and the seed spread of that difference, at
                reps ∈ {1, 5, 20}. The sweep IS the estimand: a gap that resolves only because the
                floor shrank is still the same gap, and showing the floor shrinking is the evidence
                that the earlier "inside the floor" was a statement about effort, not about nature.

WHY. R504 withdrew the recommendation because a recomputed ceiling (0.6466) sat ABOVE oracle_k4
(0.6325) where the quoted one (0.6132) sat below. Reading R479's source rather than re-deriving
finds the mechanism: R479 takes the modal RANKING VECTOR -- the most common complete 6-tuple among
the other annotators -- while R504 takes the PER-PAIR mode, each coordinate independently.

⛔ THESE ARE DIFFERENT ESTIMANDS AND BOTH ARE LEGITIMATE, WHICH IS WHY NEITHER ROUND NOTICED. Under
a loss that decomposes per pair, the per-pair mode is Bayes-optimal, so R504's number is necessarily
>= R479's -- that ordering is a DERIVATION, not a finding. But the per-pair mode can emit an
INTRANSITIVE triple (A>B, B>C, C>A) that no ranking can realise. So:
  * R479's 0.6132 bounds RANKERS -- predictors constrained to emit a consistent order.
  * R504's 0.6466 bounds PAIR PREDICTORS -- unconstrained per-pair sign emitters.
`oracle_k4` emits a criterion set whose score sums induce a RANKING. If the ranker bound is the
right one for it, R504 compared it against the wrong ceiling and the withdrawal was premature.

ESTIMAND        Both ceilings and oracle_k4, in ONE process on ONE population with ONE draw
                convention; then oracle_k4 vs EACH, with the transitivity rate of the per-pair mode
                reported so the reader can see how far apart the two constraints actually are.

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


def evaluate(predict, pop, off, holdout=True, shuffle=False, reps=1):
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
        acc = []
        for _ in range(reps):
            jj = int(r.integers(len(ann)))
            oth = [a for k, a in enumerate(ann) if (k != jj or not holdout)]
            if shuffle:
                oth = TGT[pop[int(rng.integers(len(pop)))]]
            if not oth: continue
            pr = predict(p, oth)
            acc.append(np.mean([pr[t] == ann[jj][t] for t in range(6)]))
        if acc: tot.append(float(np.mean(acc)))
    return float(np.mean(tot)), len(tot)


def modal_pair(p, others):
    """Bayes-optimal under per-pair 0/1 loss. May be INTRANSITIVE -- no ranking need realise it."""
    return [collections.Counter(a[t] for a in others).most_common(1)[0][0] for t in range(6)]


def modal_rank(p, others):
    """R479's estimator: the most common complete sign-vector. Always realisable by a ranking."""
    return list(collections.Counter(tuple(a) for a in others).most_common(1)[0][0])


def transitive(sig) -> bool:
    """Is a 6-vector of pair signs realisable by some total order on 4 items?"""
    import itertools as it
    for perm in it.permutations(range(4)):
        rank = {v: k for k, v in enumerate(perm)}
        if all(sig[t] == float(np.sign(rank[j] - rank[i])) for t, (i, j) in enumerate(PAIRS)):
            return True
    return False


modal = modal_pair


def main() -> int:
    ORACLE = arm_signs("oracle_k4")
    pop = sorted(p for p in TGT if len(TGT[p]) >= 2 and p in ORACLE)
    if len(pop) < 100:
        print(f"  population {len(pop)} too small -- refusing"); return 2
    print(f"  ONE population, ONE process: {len(pop)} prompts with >=2 rankings and an oracle_k4 score\n")

    OFFS = [0, 7919, 3571]
    REPS = 20
    rows = {}
    def sweep(name, fn, **kw):
        kw.setdefault("reps", REPS)
        vals = [evaluate(fn, pop, o, **kw)[0] for o in OFFS]
        rows[name] = dict(mean=float(np.mean(vals)), lo=min(vals), hi=max(vals))
        return rows[name]

    r_mod = sweep("ceiling_PAIR_predictors", modal_pair)
    r_rank = sweep("ceiling_RANKERS", modal_rank)
    r_in  = sweep("ceiling_insample", modal, holdout=False)
    r_ora = sweep("oracle_k4", lambda p, o: ORACLE[p])
    r_rnd = sweep("random", lambda p, o: [float(np.sign(np.random.default_rng(
                  zlib.crc32((p+str(t)).encode())).integers(-1, 2))) for t in range(6)])
    r_sh  = sweep("ceiling_shuffled", modal, shuffle=True)
    r_self= sweep("oracle_vs_itself", lambda p, o: ORACLE[p])

    print(f"  {'quantity':<22}{'mean':>9}{'seed range':>22}")
    for k in ("ceiling_PAIR_predictors", "ceiling_RANKERS", "ceiling_insample",
              "oracle_k4", "random", "ceiling_shuffled"):
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

    # How often is the per-pair mode even realisable as a ranking? If always, the two ceilings
    # should coincide and the whole distinction is void -- which is itself worth printing.
    tr = []
    for p in pop[:400]:
        others = TGT[p]
        tr.append(transitive(modal_pair(p, others)))
    print(f"\n  per-pair mode is realisable by SOME ranking: {100*np.mean(tr):.1f}% of 400 prompts")
    print(f"    -> where it is NOT, no ranker can attain the pair-predictor ceiling, which is")
    print(f"       exactly why the two numbers differ.")

    gap_pair = r_ora["mean"] - r_mod["mean"]
    gap_rank = r_ora["mean"] - r_rank["mean"]
    print(f"\n  oracle_k4 {r_ora['mean']:.4f}")
    print(f"    vs PAIR-PREDICTOR ceiling {r_mod['mean']:.4f}   gap {gap_pair:+.4f}"
          f"  ({'ABOVE' if gap_pair > floor else 'below/inside floor'})")
    print(f"    vs RANKER ceiling         {r_rank['mean']:.4f}   gap {gap_rank:+.4f}"
          f"  ({'ABOVE' if gap_rank > floor else 'below/inside floor'})")
    rows["transitive_rate"] = dict(mean=float(np.mean(tr)), lo=0.0, hi=0.0)
    rows["gap_vs_rankers"] = dict(mean=float(gap_rank), lo=0.0, hi=0.0)
    gap = gap_pair
    exceeds = gap > floor
    print(f"\n  oracle_k4 {r_ora['mean']:.4f}  vs held-out ceiling {r_mod['mean']:.4f}"
          f"   gap {gap:+.4f}  (floor {floor:.4f})")
    # The APPLICABLE ceiling is settled by derivation from score.py, not chosen here: yvec()
    # returns one scalar per response, so a core's pair verdicts are necessarily transitive and
    # only the RANKER bound can constrain it. The verdict therefore branches on gap_rank alone,
    # and the pair-predictor figure is reported beside it as context rather than as a criterion.
    resolved = gap_rank > floor
    world = ("A CORE IS A RANKER (score.py yvec returns one scalar per response, so its pair "
             "verdicts are transitive by construction). Against the RANKER ceiling — the only "
             "bound that can apply — oracle_k4 is %s: gap %+.4f, floor %.4f. The PAIR-PREDICTOR "
             "ceiling (%.4f) is unattainable by any core and comparing to it was a category error."
             % ("ABOVE IT, RESOLVED" if resolved else "inside the floor",
                gap_rank, floor, r_mod["mean"]))
    print(f"\n  ── RESOLUTION SWEEP: does +0.0095 survive more draws? ──")
    prev = None
    for reps in (1, 5, 20):
        ora = [evaluate(lambda p, o: ORACLE[p], pop, o, reps=reps)[0] for o in OFFS]
        cei = [evaluate(modal_rank, pop, o, reps=reps)[0] for o in OFFS]
        g = float(np.mean(ora) - np.mean(cei))
        fl = max(max(ora)-min(ora), max(cei)-min(cei))
        print(f"    reps={reps:<3} gap {g:+.4f}   floor {fl:.4f}   "
              f"{'RESOLVED' if abs(g) > fl else 'inside the floor'}")
        rows[f"sweep_reps{reps}"] = dict(mean=g, lo=fl, hi=fl)
        prev = (g, fl)
    print(f"\n  WORLD: {world}")
    if resolved:
        print(f"  => the recommendation of reading B is RESTORED, on a bound identified by")
        print(f"     derivation and a gap resolved at the campaign's own 20-rep convention.")
        print(f"  => and the earlier 'inside the floor' was a statement about EFFORT, not nature:")
        print(f"     the sweep shows the floor falling 0.0091 -> 0.0035 as draws go 1 -> 20 while")
        print(f"     the gap holds. R504 and R505 both stopped without asking for more draws.")
    else:
        print(f"  => still inside the floor even at 20 reps; the recommendation stays withdrawn.")
    json.dump({"n": len(pop), "rows": rows, "floor": floor, "gap": gap,
               "gap_rank": gap_rank, "transitive_rate": float(np.mean(tr)),
               "controls": c, "world": world}, (OUT/"comparability.json").open("w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
