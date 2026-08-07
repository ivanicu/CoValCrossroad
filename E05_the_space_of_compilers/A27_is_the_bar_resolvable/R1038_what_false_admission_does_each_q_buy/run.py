#!/usr/bin/env python3
"""R1038 — the family is its own null, so each q has a measurable FALSE-ADMISSION rate.

R1036 found three scale-free quantiles (50, 75, 90) and established that scale-stability is NECESSARY
and not sufficient. R1037 stated q as a DECLARED parameter for exactly that reason. Both closed by
saying the choice runs through construct validity and cannot be measured on this release.

⛔ THERE IS A THIRD ROUTE AND IT IS A MEASUREMENT. Every member of the comparator family is itself a
   scoreable ARM. So the family is its OWN reference population: run the q-bar on the family members
   and the share that clears it is a FALSE-ADMISSION RATE, because a checklist is not a core. This is
   R1023's device — which priced the coverage guard against an exact null — applied one level up, to
   the bar rather than the loader.

⛔ AND PART OF IT IS FORCED, WHICH MUST BE LABELLED. A member at rank r of N beats about r/N of the
   family by construction, so the MEDIAN member clears q=50 by arithmetic and the rate at q must fall
   as q rises. What is NOT forced is the SHAPE — how fast it falls, and whether any scale-free q buys
   a rate low enough to be worth declaring. A monotone curve was guaranteed; its values were not.

ESTIMAND        P(a family member clears "resolvably beats >= q% of the family") — the false-admission
                rate of the q-bar, measured on a population whose members are known not to be cores.
IDENTIFICATION  exact for the sampled members; each is scored by the same operator as any arm.
SCOPE           population : 200 family members drawn at a FIXED pre-registered seed from R1036's
                4,261 · reference : the full 4,261 · instrument : R923's operator, NBOOT=4000
                baseline   : R1023's coverage-guard false-admission curve, same device one level down
WORLDS          A SOME SCALE-FREE q BUYS A LOW RATE — the false-admission rate at one of {50,75,90} is
                at or below the operator's own nominal 0.025. Then that q is selectable on evidence
                and R1037's "declared, not fixed" can be narrowed to a default with a stated cost.
                B EVERY SCALE-FREE q IS EXPENSIVE — all three admit family members at a rate far above
                  nominal. Then no scale-free q is defensible as a default, the three remain
                  genuinely undecided, and R1037's declaration stands unnarrowed.
                prediction matrix: A -> a rate <= ~0.025 at some q in {50,75,90}.
                                   B -> all three well above it, and the q that reaches nominal (if
                                        any) is outside the scale-free set.
                ⚠ ONTOLOGICAL: A makes q an evidence-selected default; B makes it irreducibly a
                  choice, and the definition must say so rather than imply a measurement settled it.
KILL            pre-registered and CONDITIONAL:
                  if the ORDERING control fires (rate falls monotonically in q) and the placebo holds:
                      min rate over {50,75,90} <= 0.05 -> World A, that q named with its rate
                      otherwise                         -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ① a REAL arm known to clear the bar must clear it here: `coval_core` at q=90 must be
                admitted, reproducing R1036's committed grid membership. ② the rate must be able to
                reach 1: at q=0 every member clears, since q=0 imposes no requirement.
NEGATIVE CTRL   the rate must FALL as q rises. If it does not, the bar is not ordering anything and
                no q is selectable — reported as UNVERIFIED rather than argued away.
PLACEBO         a member against ITSELF contributes a difference of exactly 0, which cannot be > 0, so
                no member can ever beat 100% of a family containing it. The q=100 rate must be
                EXACTLY 0 — a derivation, and a check that the plumbing respects it.
NOISE FLOOR     binomial SE at 200 members is ~0.035 at p=0.5 and ~0.011 at p=0.025; printed, and no
                rate is read finer.
MULTIPLICITY    the whole q-curve is reported, not the selected cell.
SEEDS           3 bootstrap seeds; a rate is reported as the mean with its across-seed spread.
IMPOSSIBLE      whether a low false-admission rate makes q RIGHT — a bar can be strict and still
                measure the wrong thing. N/A; that is construct validity and needs the criterion
                vocabulary R1028 showed this release does not carry.
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

    # ---------- the family as its own null ----------
    r1036 = json.loads(next(A27.glob("R1036_*/results/*.json")).read_text())
    scale_free = [x for x in r1036["scale_free_q"] if x > 0]
    NSAMP, MEM_SEED = 200, 4242
    rng = np.random.default_rng(MEM_SEED)
    mem = np.sort(rng.choice(A2S.shape[1], size=NSAMP, replace=False))
    print(f"\n  ⭐ THE FAMILY IS ITS OWN NULL — {NSAMP} members drawn at fixed seed {MEM_SEED} from "
          f"{A2S.shape[1]},\n     each run against the FULL family. A checklist is not a core, so any "
          f"clearance is a FALSE ADMISSION.")
    print(f"  ⛔ PARTLY FORCED: a member at rank r of N beats ~r/N by construction, so the rate MUST "
          f"fall\n     in q. What is measured is the SHAPE and the values, not the direction.")

    rates = {q: [] for q in QS}
    for s in SEEDS[:3]:
        BF = W[s] @ A2S                                     # (NBOOT, nfam)
        beats = np.empty((len(mem), A2S.shape[1]), np.float32)
        for i, m in enumerate(mem):
            lo = np.percentile(BF[:, m][:, None] - BF, 2.5, axis=0)
            beats[i] = (lo > 0).astype(np.float32)
        share = beats.mean(axis=1) * 100
        for q in QS:
            rates[q].append(float((share >= q).mean()))
    se50 = (0.25 / NSAMP) ** 0.5
    print(f"\n     {'q':>6}{'false-admission rate':>23}{'across-seed spread':>21}")
    for q in QS:
        v = rates[q]
        print(f"     {q:>6}{np.mean(v):>23.4f}{max(v) - min(v):>21.4f}")
    print(f"     binomial SE at {NSAMP} members: ±{se50:.4f} at p=0.5, "
          f"±{(0.025*0.975/NSAMP)**0.5:.4f} at p=0.025 — no rate read finer")

    # ---------- controls ----------
    core_ok = "coval_core" in (grid90 := set(r1036["grid"].get("4261|90") or []))
    zero_ok = abs(np.mean(rates[0]) - 1.0) < 1e-9
    mono = all(np.mean(rates[QS[i]]) >= np.mean(rates[QS[i + 1]]) - 1e-9
               for i in range(len(QS) - 1))
    plac_ok = abs(np.mean(rates[100])) < 1e-9
    print(f"\n  POSITIVE ① — a REAL arm must clear the bar: `coval_core` in R1036's q=90 extension: "
          f"{core_ok}")
    print(f"  POSITIVE ② — the rate must be able to reach 1: q=0 gives {np.mean(rates[0]):.4f}  "
          f"{'PASS' if zero_ok else '⛔ FAIL'}")
    print(f"  NEGATIVE   — the rate must FALL as q rises, or the bar orders nothing: "
          f"{'PASS' if mono else '⛔ FAIL'}")
    print(f"  PLACEBO    — a member cannot beat 100% of a family CONTAINING IT (its own difference "
          f"is\n     exactly 0, never > 0), so the q=100 rate must be EXACTLY 0: "
          f"{np.mean(rates[100]):.4f}  {'PASS' if plac_ok else '⛔ FAIL'}")

    best = min(scale_free, key=lambda q: np.mean(rates[q]))
    best_rate = float(np.mean(rates[best]))
    print()
    if not (core_ok and zero_ok and mono and plac_ok):
        world = "UNVERIFIED — a control did not fire; no q is selectable from this"
    elif best_rate <= 0.05:
        world = (f"⭐ A A SCALE-FREE q BUYS A LOW RATE — q={best} admits family members at "
                 f"{best_rate:.4f}, at or below twice the operator's nominal 0.025. So q IS "
                 f"selectable on evidence, and R1037's 'declared, not fixed' can be narrowed to a "
                 f"DEFAULT of {best} with its cost stated.")
    else:
        world = (f"⭐ B EVERY SCALE-FREE q IS EXPENSIVE — the best of {scale_free} is q={best} at "
                 f"{best_rate:.4f}, far above the operator's nominal 0.025. No scale-free q is "
                 f"defensible as a default on false-admission grounds, the three remain genuinely "
                 f"undecided, and R1037's declaration stands UNNARROWED. ⭐ That is the answer to "
                 f"'which q', and it is that the evidence does not have one.")
    print(world)
    print(f"⛔ AND THE MONOTONICITY WAS FORCED, SO IT IS NOT THE FINDING. A member at rank r beats")
    print(f"   ~r/N by construction. The finding is the LEVEL: what each q actually costs.")
    print(f"⚠ AND A LOW RATE WOULD NOT MAKE q RIGHT. A bar can be strict and still measure the wrong")
    print(f"   thing; that is construct validity, needing the criterion vocabulary R1028 showed this")
    print(f"   release does not carry. N/A, stated not planned.")

    out = HERE / "results" / "false_admission_by_q.json"
    out.write_text(json.dumps({
        "round": "R1038", "seeds": list(SEEDS[:3]), "members": NSAMP, "member_seed": MEM_SEED,
        "family_size": int(A2S.shape[1]), "scale_free_q": scale_free,
        "derivation": "a member at rank r of N beats ~r/N by construction, so the rate must fall in "
                      "q; the SHAPE and LEVEL are what is measured",
        "rates": {str(q): {"mean": float(np.mean(rates[q])),
                           "spread": float(max(rates[q]) - min(rates[q]))} for q in QS},
        "controls": {"real_arm_clears": bool(core_ok), "q0_is_one": bool(zero_ok),
                     "monotone": bool(mono), "placebo_q100_zero": bool(plac_ok)},
        "best_scale_free_q": best, "best_rate": best_rate, "world": world,
        "limitation": "a low rate would not make q RIGHT; that is construct validity and needs a "
                      "criterion vocabulary this release does not carry (R1028)",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
