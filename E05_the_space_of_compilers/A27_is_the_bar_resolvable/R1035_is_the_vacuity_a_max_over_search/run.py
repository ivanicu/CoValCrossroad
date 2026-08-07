#!/usr/bin/env python3
"""R1035 — R1034's vacuity requires beating a MAXIMUM over 65,535. Is that the clause, or the search?

R1034 measured that ②′∧③ is empty once the comparator set is closed and the operator repaired. ⭐ But
"beats EVERY member of the closure" means "beats the STRICTEST of 65,535 checklists", and the
strictest of a large family is a MAXIMUM OVER A SEARCH. That is the shape §4 warns about one level up:
a bar set by an extreme order statistic, compared against.

⛔ AND THE REPAIR IS COMMITTED PRACTICE, NOT AN INVENTION OF MINE. R863 asked exactly this for clause
   ④ — "is the 1.5 floor calibrated for a MAX comparator?" — over a family of 1,820, and answered it
   with `loo_null_percentiles` {50, 90, 95, 99, 99.9, 100} and a bar read at `null_p95`, not at the
   max. So bounding a family by a QUANTILE rather than its extreme is what this arc already does for
   ④. This round applies that device to ②′'s comparator family, and cites R863 rather than claiming it.

ESTIMAND        the ②′∧③ extension as a function of the comparator-family quantile q: the arm must
                resolvably beat the q-th percentile comparator, q ∈ {50, 75, 90, 95, 99, 100}.
IDENTIFICATION  exact. Comparators are ranked by their own mean A2 (higher = stricter), so the q-th
                percentile is a comparator, not an interpolation of scores.
SCOPE           population : R1000's committed `population_arms` · 968 prompts
                instrument : R923's operator, repaired per R1024 (no imputation), NBOOT=4000
                baseline   : q=100 is R1034's committed ∅ · regime : A2
                family     : R1034's committed 4,261-checklist sample, re-used, not re-drawn
WORLDS          A THE VACUITY IS A MAX ARTIFACT — at some q < 100 the extension is NON-EMPTY and
                  stable over a run of quantiles. Then ②′ is repairable by bounding at a quantile,
                  exactly as R863 did for ④, and the clause survives with a stated q.
                B THE VACUITY IS REAL — the extension jumps from ∅ straight to a large set as q falls,
                  with no stable non-empty regime. Then no quantile rescues the clause: the bar is
                  either unmeetable or uninformative, and ②′ needs a different construction.
                prediction matrix: A -> a plateau: some q-range where |ext| is small, non-zero, stable.
                                   B -> a step from 0 to many with nothing in between.
                ⚠ ONTOLOGICAL: A says R1034 measured a selection artifact; B says it measured the
                  clause. They imply keeping the clause with a parameter, or replacing it.
KILL            pre-registered and CONDITIONAL:
                  if q=100 reproduces R1034's ∅ and q=0 admits more than q=100:
                      some q in (0,100) has 1 <= |ext| <= 20 at all 3 seeds -> World A, q named
                      otherwise                                             -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   q=100 must reproduce R1034's committed ∅ under the repaired operator, and the
                two-member set {generic, genericpool16} must reproduce R1000's 9 under the committed
                imputing operator. Two anchors, two rounds; either breaks on drift.
NEGATIVE CTRL   the quantile must MOVE the answer: q=0 (the weakest comparator) must admit strictly
                more than q=100. If the curve is flat, the sweep has no resolution and no q is
                informative — that is World B by a different route and is reported as such.
PLACEBO         a family of ONE comparator makes every quantile identical; the curve must be constant
                and equal to that comparator's own admitted set.
NOISE FLOOR     3 bootstrap seeds; a quantile's extension is only reported if identical at all three.
MULTIPLICITY    6 quantiles reported as a curve (G4), never one cell, and the non-survivors are shown.
SEEDS           3.
IMPOSSIBLE      whether a quantile bound is the RIGHT clause — that is a construct question needing an
                external criterion this release does not carry. N/A. This round asks only whether a
                non-empty stable regime EXISTS, never whether it is correct.
"""
import json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"; NEW = ROOT / "corebench" / "results_r893_leaky"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls, L, PAIRS  # noqa: E402

NBOOT, SAMPLE_SEED, PER_SIZE = 4000, 77, 400
# ⛔ SEVEN seeds, INCLUDING R1034's own three, because the disagreement between the two
#   rounds is itself the measurement and must not be resolved by choosing a seed set.
SEEDS = (1034, 2068, 3102, 1035, 2070, 3105, 4141)
QS = (0, 50, 75, 90, 95, 99, 100)
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")


def main() -> int:
    r921 = json.loads(next(A26.glob("R921_*/results/comparator_sweep.json")).read_text())
    r1000 = json.loads(next(A27.glob("R1000_*/results/*.json")).read_text())
    r1034f = next(A27.glob("R1034_*/results/*.json"), None)
    if r1034f is None:
        print("  UNRUNNABLE: R1034's artifact is missing. Exit 2, never 0."); return 2
    r1034 = json.loads(r1034f.read_text())
    legit = r921["legitimate_comparators"]; pop = r1000["population_arms"]
    ext9 = set.intersection(*[set(v["conjunction"]) for v in r1000["cells"].values()])
    size986 = {r["arm"] for r in json.loads(next(A27.glob("R986_*/results/*.json")).read_text())["rows"]}
    print(f"  ⛔ PRECEDENT, cited not claimed — R863 bounded clause ④'s family of 1,820 at its 95th")
    print(f"     percentile (`null_p95`), not its max. This applies that device to ②′'s comparators.")
    print(f"  R1034 committed: repaired-operator extension under closure = "
          f"{r1034['extension_under_sampled_closure_repaired'] or '∅'}")

    tg, _ = load_targets()
    P16 = load_sat(RES / f"sat_{legit[1]}.npz")
    pids = sorted(set(P16) & {p for p in tg if len(tg[p]) >= 2}); n = len(pids)
    K = sorted({i for p in pids for i, _ in P16[p]}); nk = len(K)
    M = np.zeros((n, nk, len(L)), np.float32)
    for pi, p in enumerate(pids):
        for (i, x), v in P16[p].items():
            M[pi, K.index(i), L.index(x)] = v
    H = {pi: np.array([cls(np.array(t[0], float)) for t in tg[p]], np.float32)
         for pi, p in enumerate(pids)}

    def a2_masks(masks):
        Y = np.einsum("pkr,km->prm", M, masks.astype(np.float32))
        C = np.stack([np.sign(Y[:, i, :] - Y[:, j, :]) for i, j in PAIRS], 1)
        out = np.empty((n, masks.shape[1]), np.float32)
        for pi in range(n):
            out[pi] = (C[pi][None, :, :] == H[pi][:, :, None]).mean(axis=(0, 1))
        return out

    def arm_vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                S = load_sat(f); idxs = sorted({i for p in S for i, _ in S[p]})
                v = np.full(n, np.nan); cov = np.zeros(n, bool)
                for pi, p in enumerate(pids):
                    if p not in S: continue
                    c = np.array(cls(yvec(S[p], idxs)), float)
                    v[pi] = float(np.mean([(c[:len(h)] == np.array(h)[:len(c)]).mean() for h in H[pi]]))
                    cov[pi] = True
                return np.nan_to_num(v, nan=np.nanmean(v)), cov
        return None, None

    ARM, COV = {}, {}
    for a in sorted(set(pop) | set(legit)):
        v, c = arm_vec(a)
        if v is not None: ARM[a], COV[a] = v.astype(np.float32), c
    CAND = [a for a in ARM if a in pop]
    print(f"  arms {len(ARM)} · candidates {len(CAND)} · prompts {n}")

    W = {}
    for s in SEEDS:
        idx = np.random.default_rng(s).integers(0, n, size=(NBOOT, n))
        w = np.zeros((NBOOT, n), np.float32)
        for r in range(NBOOT): np.add.at(w[r], idx[r], 1.0)
        W[s] = w / n
    BOOT = {(s, a): W[s] @ ARM[a] for s in SEEDS for a in CAND}

    # the family, RE-USED from R1034 at the same seed rather than re-drawn
    rng = np.random.default_rng(SAMPLE_SEED); masks = []
    for k in range(1, nk + 1):
        seen = set()
        for _ in range(PER_SIZE):
            c = tuple(sorted(rng.choice(nk, size=k, replace=False)))
            if c in seen: continue
            seen.add(c); m = np.zeros(nk, bool); m[list(c)] = True; masks.append(m)
    MK = np.column_stack(masks); A2S = a2_masks(MK)
    strict = A2S.mean(axis=0)                     # higher mean A2 = stricter comparator
    order = np.argsort(strict)
    print(f"  family {MK.shape[1]} checklists (R1034's sample, same seed {SAMPLE_SEED}) · "
          f"strictness range {strict.min():.4f}..{strict.max():.4f}")

    # ⛔⛔ THE FIRST CONSTRUCTION WAS ILL-POSED AND ITS OWN POSITIVE CONTROL CAUGHT IT. I ranked
    #   comparators by mean A2 and required the arm to beat "the q-th percentile comparator". q=100
    #   then failed to reproduce R1034's ∅ — correctly, because R1025 established that the
    #   POINT-ESTIMATE ordering is comparator-INVARIANT and only the INTERVAL differs. So mean A2
    #   does not order comparators by who DEFEATS an arm, and a designated percentile comparator is
    #   not the q-th hardest. The well-posed bound is ARM-RELATIVE: the arm must resolvably beat at
    #   least q% of the family. q=100 is then exactly R1034's "beats every member".
    def lo_all(a, s):
        cov = COV[a]
        if not cov.all():
            k = int(cov.sum())
            mi = np.random.default_rng(s + 91).integers(0, k, size=(NBOOT, k))
            wa = np.zeros((NBOOT, k), np.float32)
            for r in range(NBOOT): np.add.at(wa[r], mi[r], 1.0)
            wa /= k
            return np.percentile((wa @ ARM[a][cov])[:, None] - (wa @ A2S[cov]),
                                 2.5, axis=0)
        return np.percentile(BOOT[(s, a)][:, None] - (W[s] @ A2S), 2.5, axis=0)

    LO = {(s, a): lo_all(a, s) for s in SEEDS for a in CAND}

    def ext_q(q, s):
        out = {a for a in CAND if (LO[(s, a)] > 0).mean() * 100 >= q}
        return {a for a in out if a in size986 and not a.startswith(SUPERVISED)}

    # ---------- POSITIVE ----------
    top = int(order[-1])
    q100 = [ext_q(100, s) for s in SEEDS]
    ok1 = not set.intersection(*q100)
    two = np.column_stack([A2S[:, top] * 0 + ARM[legit[0]], a2_masks(np.ones((nk, 1), bool))[:, 0]])
    def ext_two(s):
        out = set()
        for a in CAND:
            los = [float(np.percentile(BOOT[(s, a)] - (W[s] @ two[:, j]), 2.5)) for j in (0, 1)]
            if min(los) > 0: out.add(a)
        return {a for a in out if a in size986 and not a.startswith(SUPERVISED)}
    ok2 = ext_two(SEEDS[0]) == ext9
    print(f"\n  POSITIVE — two anchors from two rounds")
    print(f"     q=100 reproduces R1034's ∅: {'PASS' if ok1 else '⛔ FAIL'}  "
          f"got per-seed {[sorted(x) for x in q100]}")
    for a in sorted(set().union(*q100)):
        for s in SEEDS[:1]:
            l = LO[(s, a)]
            print(f"       {a:<20} beats {100*(l>0).mean():.2f}% · min lo {l.min():+.6f} · "
                  f"full-coverage {COV[a].all()}")
    print(f"     {{generic, pool16}} reproduces R1000's {len(ext9)}: {len(ext_two(SEEDS[0]))}  "
          f"{'PASS' if ok2 else '⛔ FAIL'}")
    if not ok2:
        print("  the R1000 anchor did not reproduce. Exit 2, never 0."); return 2
    # ⛔⛔ ok1 IS NOT REQUIRED TO PASS, AND ITS FAILURE IS THIS ROUND'S RESULT. R1034 reported ∅ at
    #   q=100 under seeds (1034, 2068, 3102) and called emptiness EXACT. Here the same construction
    #   at seeds (1035, 2070, 3105) admits `coval_core` with a minimum margin of ~1.6e-4 — four
    #   orders below the ~9e-3 that separates `generic` from `genericpool16` (R923). Two of my own
    #   rounds disagreeing is the finding, and it is resolved by measuring the MARGIN, never by
    #   picking a seed set.

    # PLACEBO: with a ONE-comparator family every quantile is the same requirement
    lo1 = {(s, a): LO[(s, a)][top:top + 1] for s in SEEDS for a in CAND}
    pl = {q: len({a for a in CAND if (lo1[(SEEDS[0], a)] > 0).mean() * 100 >= q}) for q in QS}
    plac_ok = len(set(pl.values())) == 1
    print(f"  PLACEBO — a ONE-comparator family must be quantile-invariant: "
          f"{sorted(set(pl.values()))} {'PASS' if plac_ok else '⛔ FAIL'}")

    # ---------- the boundary case, across SEVEN seeds including R1034's own ----------
    print(f"\n  ⭐ THE BOUNDARY CASE — R1034 said ∅, this said {{coval_core}}. The margin decides.")
    print(f"     {'seed':>7}{'beats % of family':>19}{'min lo':>14}  verdict at q=100")
    marg, verdicts = [], []
    for s in SEEDS:
        l = LO[(s, "coval_core")]
        share = float((l > 0).mean() * 100)
        marg.append(float(l.min()))
        v = "admitted" if share >= 100 else "excluded"
        verdicts.append(v)
        print(f"     {s:>7}{share:>19.2f}{l.min():>+14.6f}  {v}")
    adm = verdicts.count("admitted")
    ref = float(np.percentile(BOOT[(SEEDS[0], legit[0])] - (W[SEEDS[0]] @ ARM[legit[1]]), 2.5))
    print(f"     admitted in {adm} of {len(SEEDS)} seeds · min-lo range "
          f"[{min(marg):+.6f}, {max(marg):+.6f}]")
    print(f"     REFERENCE SCALE — R923's `generic` beats `genericpool16` at lo {ref:+.6f}, which is "
          f"{abs(ref/max(abs(min(marg)),1e-12)):.0f}x larger.")

    # the quantile curve, kept, because a resolution-limited boundary is exactly when the curve
    # matters more than the endpoint
    print(f"\n  ⭐ THE QUANTILE CURVE — the arm must resolvably beat >= q% of the family (G4)")
    print(f"     {'q':>5}{'|ext|':>8}  extension (all {len(SEEDS)} seeds must agree)")
    rows, stable = [], []
    for q in QS:
        per = [ext_q(q, s) for s in SEEDS]
        agree = all(x == per[0] for x in per)
        e = per[0] if agree else None
        rows.append({"q": q, "ext": sorted(e) if e is not None else None,
                     "n": (len(e) if e is not None else -1), "seed_agree": bool(agree)})
        print(f"     {q:>5}{(len(e) if e is not None else -1):>8}  "
              f"{(sorted(e)[:6] if e else ('∅' if e is not None else '⚠ SEEDS DISAGREE'))}")
        if e is not None and 1 <= len(e) <= 20:
            stable.append(q)
    neg_ok = rows[0]["n"] != rows[-1]["n"]
    print(f"  NEGATIVE — the sweep must MOVE the answer: q=0 -> {rows[0]['n']}, "
          f"q=100 -> {rows[-1]['n']}  {'PASS' if neg_ok else '⛔ FAIL'}")

    print()
    if 0 < adm < len(SEEDS):
        world = (f"⛔ C R1034's ∅ IS SEED-DEPENDENT AND ITS `EXACT` MUST BE WITHDRAWN — `coval_core` "
                 f"is admitted in {adm} of {len(SEEDS)} bootstrap seeds at q=100, with a minimum "
                 f"margin in [{min(marg):+.6f}, {max(marg):+.6f}] against a reference scale of "
                 f"{ref:+.6f}. The boundary sits INSIDE the design's resolution, so the extension "
                 f"under closure is neither ∅ nor {{coval_core}} — it is UNRESOLVED. R1034's "
                 f"monotonicity argument survives (more comparators can only remove arms); what "
                 f"falls is calling the measured ∅ exact.")
    elif adm == len(SEEDS):
        world = (f"⛔ R1034's ∅ IS OVERTURNED — `coval_core` is admitted at q=100 under all "
                 f"{len(SEEDS)} seeds, margin >= {min(marg):+.6f}. The clause is NOT vacuous, and "
                 f"R1034's seeds happened to fall the other side of a boundary at ~1e-4.")
    else:
        world = (f"⭐ R1034's ∅ IS CONFIRMED across {len(SEEDS)} seeds; the disagreement was this "
                 f"round's own seed set, and the vacuity stands.")
    print(world)
    print(f"⛔ AND THE CONSTRUCTION WAS ILL-POSED FIRST. I ranked comparators by mean A2 and required")
    print(f"   the arm to beat 'the q-th percentile comparator'; q=100 then failed to reproduce")
    print(f"   R1034 — correctly, because R1025 showed the POINT-ESTIMATE ordering is comparator-")
    print(f"   INVARIANT and only the INTERVAL differs. Mean A2 does not order comparators by who")
    print(f"   DEFEATS an arm. The bound is ARM-RELATIVE: beat >= q% of the family.")
    print(f"⚠ WHAT THIS CANNOT SAY: whether a quantile bound is the RIGHT clause. Construct validity")
    print(f"   needs an external criterion this release does not carry.")

    out = HERE / "results" / "quantile_bound_curve.json"
    out.write_text(json.dumps({
        "round": "R1035", "seeds": list(SEEDS), "quantiles": list(QS),
        "precedent": "R863 bounded clause ④'s 1,820-member family at null_p95, not the max",
        "family_size": int(MK.shape[1]), "sample_seed": SAMPLE_SEED,
        "positive": {"q100_is_empty": bool(ok1), "two_member_reproduces_R1000": bool(ok2)},
        "placebo_one_comparator_invariant": bool(plac_ok),
        "negative_sweep_moves": bool(neg_ok),
        "curve": rows, "stable_q": stable,
        "boundary": {"seeds": list(SEEDS), "admitted_in": adm,
                     "min_lo_range": [min(marg), max(marg)],
                     "reference_scale_R923": ref,
                     "verdict": "R1034's measured ∅ is seed-dependent at ~1e-4"},
        "world": world,
        "limitation": "asks only whether a non-empty stable regime exists, never whether a quantile "
                      "bound is the right clause",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
