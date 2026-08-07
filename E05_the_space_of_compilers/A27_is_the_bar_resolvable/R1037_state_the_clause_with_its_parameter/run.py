#!/usr/bin/env python3
"""R1037 — the clause still names no parameter. State it, and verify the STATED form computes.

The canonical clause at `DEFINITION.md:808` and `README.md:65` reads "resolvably beats the certified
prompt-blind comparator set". R1034 measured that quantifying over the CLOSED set is vacuous, and
R1035/R1036 replaced the max with a family quantile whose onset size grows with q. **None of that is
in the clause.** It carries no q, no family, no closure — so a reader implementing it implements the
vacuous form.

⛔ AND §4 DECIDES WHAT THE CLAUSE MAY SAY. *"A definition that names a number it cannot resolve is how
   'four' got in. State the bound the design supports, not the value the instance happens to have."*
   R1036 found THREE scale-free quantiles (50, 75, 90) and no evidence selecting among them. So the
   clause must carry q as a DECLARED PARAMETER with its measured onset — not a fabricated value, and
   not silence.

ESTIMAND        whether the clause AS NEWLY STATED — "resolvably beats at least q% of the certified
                prompt-blind family, for a declared q" — computes R1036's committed grid.
IDENTIFICATION  exact. The stated form is implemented literally from the wording and compared to a
                committed artifact produced by different code.
SCOPE           population : R1000's committed `population_arms` · 968 prompts
                instrument : R923's operator repaired per R1024 · baseline : R1036's committed grid
WORLDS          A THE STATED FORM COMPUTES — the literal reading of the new wording reproduces
                  R1036's grid at every scale-free q. Then the clause can be repaired at both sites
                  and a reader implementing the sentence gets what the arc measured.
                B THE WORDING UNDER-SPECIFIES — the literal reading admits more than one
                  implementation and they disagree. Then the sentence is not yet a definition and
                  naming q does not fix it.
                prediction matrix: A -> exact agreement at q ∈ {50,75,90,95,99}.
                                   B -> a disagreement, and the ambiguous phrase is named.
KILL            pre-registered and CONDITIONAL:
                  if the literal implementation runs at all:
                      it reproduces R1036's grid at every scale-free q -> World A, repair both sites
                      otherwise                                         -> World B, name the ambiguity
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   R1036's committed grid, produced by different code in a different round, is the
                anchor. It can fail: any drift in how "at least q% of the family" is read breaks it.
NEGATIVE CTRL   a DELIBERATELY MISREAD wording — "beats the q-th percentile COMPARATOR" rather than
                "beats q% of the family" — must give a DIFFERENT answer. That is R1035's own ill-posed
                first construction, kept as the negative control precisely because it failed there.
PLACEBO         q=0 must admit every arm the operator can admit at all, since it imposes no
                requirement; it is reported and EXCLUDED from the clause as degenerate.
NOISE FLOOR     3 bootstrap seeds; agreement required at all three.
MULTIPLICITY    every scale-free q is checked, not just the one the clause will name.
SEEDS           3.
IMPOSSIBLE      which q is RIGHT. R1036 established scale-stability is necessary and not sufficient,
                and no measurement over this release selects among the three. N/A — what it would
                require is an external criterion for what the comparator family represents (R1028).
                ⭐ So the clause DECLARES q rather than fixing it, which is the honest form.
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
NS = (1, 100, 300, 1000, 2000, 4261)
FAM_SEEDS = (11, 22, 33)
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

    # ---------- the STATED form, implemented literally from the new wording ----------
    r1036 = json.loads(next(A27.glob("R1036_*/results/*.json")).read_text())
    grid36 = {k: (set(v) if v is not None else None) for k, v in r1036["grid"].items()}
    NN = 4261
    print(f"\n  ⭐ THE STATED FORM — 'resolvably beats at least q% of the certified prompt-blind")
    print(f"     family', implemented LITERALLY from the wording, against R1036's committed grid")
    print(f"     {'q':>6}{'stated':>9}{'R1036':>8}  agree")
    ok_all, rows = True, []
    for q in QS:
        per = set()
        for s in SEEDS[:3]:
            e = {a for a in CAND if (LO[(s, a)] > 0).mean() * 100 >= q}
            per.add(frozenset({a for a in e if a in size986 and not a.startswith(SUPERVISED)}))
        mine = set(next(iter(per))) if len(per) == 1 else None
        want = grid36.get(f"{NN}|{q}")
        ag = (mine is not None and want is not None and mine == want)
        if q in r1036["scale_free_q"] and q > 0:
            ok_all &= ag
        rows.append({"q": q, "stated": sorted(mine) if mine else None,
                     "r1036": sorted(want) if want else None, "agree": bool(ag)})
        print(f"     {q:>6}{(len(mine) if mine else -1):>9}{(len(want) if want else -1):>8}  {ag}")

    # ⚠⚠ THE NEGATIVE CONTROL FAILED FOR ITS OWN REASONS ON THE FIRST RUN. It compared the two
    #   readings at q=90 ONLY, got 11 = 11, and reported the wording as under-specified — while the
    #   table above showed all seven q agreeing. R1025 already explains the coincidence: the two
    #   certified comparators are near-interchangeable in the POINT estimate, so at a mid quantile
    #   the designated-comparator reading and the coverage reading can land on the same set without
    #   being the same rule. A control must be run where the two CAN differ, which is the whole
    #   curve, not one cell.
    strict = A2S.mean(axis=0); order = np.argsort(strict)
    print(f"\n  NEGATIVE — R1035's ill-posed reading ('beats the q-th percentile COMPARATOR') across")
    print(f"     the WHOLE curve, because at one q the two readings can coincide by accident:")
    print(f"     {'q':>6}{'stated':>9}{'misread':>10}  differ")
    diffs = 0
    for q in QS:
        j = int(order[min(len(order) - 1, int(round(q / 100 * (len(order) - 1))))])
        m = {a for a in CAND
             if float(np.percentile(BOOT[(SEEDS[0], a)] - (W[SEEDS[0]] @ A2S[:, j]), 2.5)) > 0}
        m = {a for a in m if a in size986 and not a.startswith(SUPERVISED)}
        w = grid36.get(f"{NN}|{q}")
        d = (w is None) or (m != w)
        diffs += int(d)
        print(f"     {q:>6}{(len(w) if w else -1):>9}{len(m):>10}  {d}")
    neg_ok = diffs > 0
    print(f"     the two readings differ at {diffs} of {len(QS)} quantiles: "
          f"{'PASS — they are different rules' if neg_ok else '⛔ FAIL — extensionally identical here'}")

    # ⚠ AND THE VERDICT IS COMPUTED FROM THE ROWS, NOT FROM A CONJUNCTION OF CONTROLS. The first
    #   run fired World B because `ok_all and neg_ok` was False on the NEGATIVE — and then asserted
    #   "the literal reading does not reproduce R1036", which the table refuted line by line.
    scale_free = [x for x in r1036["scale_free_q"] if x > 0]
    agree_rows = [r for r in rows if r["q"] in scale_free]
    ok_all = bool(agree_rows) and all(r["agree"] for r in agree_rows)
    print()
    if not neg_ok:
        world = (f"⛔ UNVERIFIED ON THE CONTROL — the stated form reproduces R1036 at every "
                 f"scale-free q ({[r['q'] for r in agree_rows]}), but the misread reading is "
                 f"extensionally identical to it across the whole curve, so this design cannot "
                 f"demonstrate that the wording picks one rule rather than the other.")
    elif ok_all:
        world = (f"⭐ A THE STATED FORM COMPUTES — the literal reading of 'resolvably beats at least "
                 f"q% of the certified prompt-blind family' reproduces R1036's committed grid at "
                 f"every scale-free q > 0, under 3 seeds, against code from a different round. The "
                 f"clause can be repaired at both canonical sites, and a reader implementing the "
                 f"sentence gets what the arc measured.")
    else:
        world = (f"⭐ B THE WORDING UNDER-SPECIFIES — the literal reading does not reproduce R1036 "
                 f"at every scale-free q. Naming q does not fix the sentence; the ambiguity is in "
                 f"the phrase itself and is named in the rows above.")
    print(world)
    print(f"⛔ AND q IS DECLARED, NOT FIXED. R1036 found scale-stability NECESSARY and not sufficient:")
    print(f"   q ∈ {[x for x in r1036['scale_free_q'] if x > 0]} are all size-independent and no")
    print(f"   measurement over this release selects among them. §4: a definition that names a number")
    print(f"   it cannot resolve is how 'four' got in — so the clause states the PARAMETER and its")
    print(f"   measured onset, never a value.")
    print(f"⚠ AND q=100 IS EXCLUDED BY MEASUREMENT, not by taste: R1036 showed the max never")
    print(f"   stabilises in family size, so 'beats the whole family' cannot be stated at any size")
    print(f"   this release reaches.")

    out = HERE / "results" / "stated_form_verifies.json"
    out.write_text(json.dumps({
        "round": "R1037", "seeds": list(SEEDS[:3]), "anchor": "R1036 grid at n=4261",
        "rows": rows, "all_scale_free_agree": bool(ok_all),
        "negative_misread_disagrees": bool(neg_ok),
        "declared_not_fixed": [x for x in r1036["scale_free_q"] if x > 0],
        "q100_excluded_because": "R1036: the max never stabilises in family size",
        "world": world,
        "limitation": "which q is RIGHT is not decided here; scale-stability is necessary and not "
                      "sufficient, and selecting among the three needs an external criterion (R1028)",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
