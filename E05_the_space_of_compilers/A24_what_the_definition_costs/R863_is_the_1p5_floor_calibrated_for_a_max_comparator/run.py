#!/usr/bin/env python3
"""
R863 · is the 1.5× floor measuring what it was chosen to measure, when the comparator is a MAX?

⛔ WHY. Three rounds corrected this comparison's DENOMINATOR — R860 replaced a borrowed MDE, R862
corrected a fixed argmax — and all three treated **1.5 as fixed**. But `margin / MDE >= 1.5` was
adopted for **paired arm-vs-arm** designs. Here the comparator is `max over 1,820 blind 4-subsets`,
an **order statistic**, and nobody has asked whether the bar still carries its intended
false-positive meaning against one.

⛔ THE ARITHMETIC RUNG, RUN FIRST, AND IT IS THE MOST INFORMATIVE THING IN THE ROUND.
`MDE = 2.802 * SE` is the 80%-power/α=0.05 constant (1.960 + 0.842), so `margin/MDE >= 1.5` demands
`margin >= 4.203 * SE` — a **z of 4.2**, which for a paired two-arm design is a one-sided p of about
**1.3e-5**. **That is the bar's intended severity, and it is already extreme.**
⭐ Now stack the comparator on top. **Under exchangeability of the arm with the family, the arm is
the maximum with probability exactly `1/(N+1) = 1/1821 ≈ 5.5e-4`** — so a margin that is merely
POSITIVE is already an extreme-order-statistic event. **This is a DERIVATION** and could not have
come out otherwise; its assumption is exchangeability, which is FALSE here (a core is not drawn from
the same distribution as blind 4-subsets). **So it bounds rather than measures**, and the
measurement below is what the round is actually for.


⛔⛔⛔ POST-RUN RETRACTION, WRITTEN BEFORE THE ROUND WAS COMMITTED. **THE PRINTED `WORLD A` VERDICT
IS WITHDRAWN, AND THE LOO NULL IS RETRACTED AS A CALIBRATION INSTRUMENT.** The run is kept intact
(L81: annotate, never rewrite) because what it measured is worth more than what it concluded.

**What happened.** KILL ③ asked whether the LOO null is non-degenerate and accepted `> 0` positive
margins. It got **1 of 1820** and printed PASS. **That threshold was far too weak, and the round's
own DERIVATION says why:** under exchangeability the arm is the maximum with probability
`1/(M+1) = 1/1821`, so **the expected number of positive LOO margins is 1**. Observed: **1**.

⭐ **The derivation and the measurement agree to within a single case — and that agreement is
precisely what makes the instrument useless.** A member of the family cannot beat the max of its own
family except by BEING that max. So `p95 = −1.0113` and `FP rate = 0.0000%` are **forced by the
construction, not measured from it**, and no statement about whether 1.5 is over- or under-strict
can rest on them. §4's `check that cannot fail`, inverted: a null in which 1819 of 1820 outcomes are
negative by arithmetic cannot calibrate a POSITIVE threshold.

⚠ **The named limitation in SCOPE above saw the correlation and still under-rated it.** It said LOO
arms are "maximally correlated with their own comparator" and therefore "conservative in a specific
direction". That was true and far too mild: the defect is not conservatism, it is **degeneracy**.
Naming a confound is not controlling it — the control was written, ran, and passed.

⭐ **WHAT SURVIVES, and it is the more useful half.**
  ① **The derivation is CONFIRMED against data**: 1 observed vs 1 expected. A positive margin
     against a max-of-1820 is a ~5.5e-4 event under exchangeability, so **the comparator is already
     doing severe work before the 1.5 bar is applied at all.**
  ② **The POSITIVE CONTROL is clean and independent of the defect**: planting g on the arm gives
     ratios 0.8683 → 1.3505 → 1.8327 → 2.7972 → 4.7262, **monotone**, not clearing at g=0, first
     clearing at **g = 0.01**. So the bar's own resolution on this design is **a planted advantage
     of about one A2 point in a hundred**, and `coval_core`'s true margin is under half of it.
  ③ **The SECOND null is the one that was actually informative, and it disagrees with the first by
     more than two units of the statistic**: shuffled target gives −0.1038, +0.0258, −0.2815, mean
     **−0.1198** — centred near ZERO, while the LOO null's median is **−2.1843**. **The two nulls
     are not two estimates of one thing; the LOO null is in the wrong place entirely.**

⛔ **AND THE SECOND NULL IS UNDERPOWERED AND HAS ITS OWN KNOWN DEFECT — stated, not smuggled.**
Three seeds cannot estimate a null's spread (observed sd ≈ 0.155 at n=3), and the pair shuffle is
the null R852/R853 already showed is NOT pure: it preserves each prompt's marginal verdict mix and
left ~14 arms clearing clause ②. **So the calibration question this round set out to answer is
STILL OPEN**, and it is open in a sharper form than before: it needs a properly powered null that
does not share either defect.

**The sentence this round cannot support:** *"the floor is far over-strict against a max
comparator."* What it can support: *the LOO null cannot address that question, the relevant null
sits near zero rather than near −2.18, and the design resolves a planted advantage of g = 0.01.*

ESTIMAND        the empirical null distribution of the reported statistic `margin / MDE` when the
                arm has NO advantage over the family, and the percentile at which this project's
                1.5 floor sits in it.
IDENTIFICATION  exact and cheap, by LEAVE-ONE-OUT: each of the 1,820 subsets can play the ARM
                against the max of the remaining 1,819, using the identical statistic. That is
                1,820 draws of the exact quantity being thresholded, from arms that are genuinely
                exchangeable with the comparator family.
SCOPE           population: 968 prompts scored by both `genericpool16` and `coval_core`
                instrument: A2 vs every annotator; comparator = max over the family
                baseline:   the LOO null; and a second, independent null (shuffled target)
                regime:     home release, judge J
                ⚠ NAMED LIMITATION: LOO arms are MEMBERS of the family, so they are maximally
                  correlated with their own comparator. That makes this null CONSERVATIVE in a
                  specific direction — it understates the spread an OUTSIDE arm would show. The
                  shuffled-target null is included precisely because it does not share that defect,
                  and the two are reported side by side rather than one standing for both.
WORLDS          A · the null's 95th percentile is far BELOW 1.5 -> the floor is over-strict against
                    a max comparator; it is rejecting at a far smaller false-positive rate than it
                    was chosen to deliver, and `coval_core`'s failure at 0.910 may be a property of
                    the BAR rather than of the core
                B · the null's 95th percentile is at or ABOVE 1.5 -> the floor is not conservative
                    here at all; a max comparator inflates the statistic and 1.5 is too PERMISSIVE
                C · the null's 95th percentile brackets 1.5 -> the bar transfers, and three rounds
                    of denominator corrections were the right place to have been looking
KILL            CONDITIONAL, all arms required:
                  ① reproduce R331's blind max and `coval_core` to 1e-9
                  ② reproduce R860's committed MDE 0.010343530538451993 to 1e-12
                  ⭐ ③ the LOO null must be NON-DEGENERATE: if every LOO arm returns a negative
                     margin by construction, the null cannot produce a false positive and the
                     percentile is meaningless — §4's `check that cannot fail`, inverted.
POSITIVE CTRL   a planted dose-response on the arm: g in {0, .005, .01, .02, .04} added to the
                arm's per-prompt scores. The ratio must RISE with g and must NOT already clear 1.5
                at g=0. Reports the g at which the bar is first cleared — the bar's own MDE.
PLACEBO         the arm against ITSELF must give margin exactly 0 and ratio exactly 0.
MULTIPLICITY    the LOO family is 1,820 cells; the whole distribution is reported, not its tail.
SEEDS           3 bootstrap seeds; spread reported.
ARTIFACT        results/floor_calibration.json
IMPOSSIBLE      construct validated (needs an external gold standard) · cross-release (needs a
                second release) · causally identified (needs an intervention on the mechanism).
"""
import itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

R331_MAX = 0.55747530882624
CORE_MEAN = 0.5664774811929549
R860_MDE = 0.010343530538451993
PAIRS = list(itertools.combinations(range(4), 2))
NBOOT, ZEFF, FLOOR = 4000, 2.802, 1.5
DOSES = (0.0, 0.005, 0.01, 0.02, 0.04)


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    A = load_sat(ROOT / "corebench" / "results" / "sat_coval_core.npz")
    pids = sorted(set(S) & set(A) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    subs = np.array(list(itertools.combinations(range(npool), 4)))
    M = len(subs)
    SAT = np.stack([np.array([[S[p][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                    for p in pids])
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    B = np.empty((M, N))
    for n in range(N):
        Y = SAT[n][subs].sum(axis=1)
        C_ = np.sign(Y[:, ii] - Y[:, jj])
        B[:, n] = (C_[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))
    per = B.mean(1)
    o = np.argsort(-per); kglob, k2nd = int(o[0]), int(o[1])
    core = np.array([np.mean([[cls(yvec(A[p], sorted({i for i, _ in A[p]})))[c] == h[c]
                               for c in range(6)] for h in H[n]]) for n, p in enumerate(pids)])
    print(f"  prompts {N} · family {M} · argmax #{kglob} {per[kglob]:.10f} · "
          f"runner-up #{k2nd} {per[k2nd]:.10f}")

    d1 = abs(float(per[kglob]) - R331_MAX); d2 = abs(float(core.mean()) - CORE_MEAN)
    rng860 = np.random.default_rng(31)
    idx860 = np.array([rng860.integers(0, N, N) for _ in range(NBOOT)])
    mde860 = ZEFF * float((core - B[kglob])[idx860].mean(1).std(ddof=1))
    d3 = abs(mde860 - R860_MDE)
    print(f"  KILL ①  blind max |Δ|={d1:.3e}  ·  coval_core |Δ|={d2:.3e}  "
          f"{'PASS' if max(d1, d2) <= 1e-9 else 'FAIL'}")
    print(f"  KILL ②  R860 MDE  |Δ|={d3:.3e}  {'PASS' if d3 <= 1e-12 else 'FAIL'}")
    if max(d1, d2) > 1e-9 or d3 > 1e-12:
        print("\n  UNVERIFIED: cannot reproduce what it extends. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "floor_calibration.json", "w"), indent=2)
        return 2

    def ratios(Arms, Comp, seed):
        """Arms: (K, N) arm vectors. Comp: (K, N) each arm's COMPARATOR VECTOR.

        ⚠ Takes the comparator as a VECTOR, not an index into B. The first draft indexed the global
        B, so the shuffled-target null had to overwrite B and restore it — and any exception between
        those two assignments would leave every later cell silently computing against a shuffled
        family, with nothing in the output to show it. A function that reads mutable global state is
        an instrument whose calibration depends on when you call it.
        """
        W = np.zeros((NBOOT, N))
        bidx = np.random.default_rng(seed).integers(0, N, size=(NBOOT, N))
        for b in range(NBOOT):
            np.add.at(W[b], bidx[b], 1.0)
        W /= N
        D = Arms - Comp                               # (K, N) paired difference vectors
        DM = W @ D.T                                  # (NBOOT, K) exact bootstrap means
        se = DM.std(axis=0, ddof=1)
        mde = ZEFF * se
        return D.mean(1) / np.maximum(mde, 1e-300), D.mean(1), mde

    # ---- PLACEBO: the arm against itself --------------------------------------------------------
    pl_r, pl_m, _ = ratios(B[kglob][None, :], B[kglob][None, :], 11)
    pl_ok = abs(float(pl_m[0])) < 1e-15
    print(f"  PLACEBO  argmax vs ITSELF: margin {float(pl_m[0]):+.3e}  "
          f"{'PASS' if pl_ok else 'FAIL'}")

    # ---- LOO NULL: each subset is the arm against the max of the other 1,819 --------------------
    comp = np.full(M, kglob); comp[kglob] = k2nd
    loo, loo_m, _ = ratios(B, B[comp], 11)
    nondeg = bool((loo_m > 0).sum() > 0)
    print(f"  KILL ③   LOO null NON-DEGENERATE (some arm beats its comparator): {nondeg}  "
          f"{'PASS' if nondeg else 'FAIL'}   ({int((loo_m>0).sum())} of {M} positive)")
    print("    Only the argmax can beat the max of the others, so a degenerate null here would be")
    print("    a threshold with no false-positive rate to calibrate — a check that cannot fail.")
    if not (pl_ok and nondeg):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "placebo": float(pl_m[0]), "nondeg": nondeg},
                  open(OUT / "floor_calibration.json", "w"), indent=2)
        return 2

    qs = [50, 90, 95, 99, 99.9, 100]
    pv = np.percentile(loo, qs)
    print(f"\n  LOO NULL of `margin/MDE` over all {M} cells (the WHOLE distribution, not its tail):")
    for q, v in zip(qs, pv):
        print(f"    p{q:<6} {v:+.4f}")
    core_r, core_m, core_mde = ratios(core[None, :], B[kglob][None, :], 11)
    cr = float(core_r[0])
    pct = float((loo < cr).mean() * 100)
    print(f"\n  ⭐ `coval_core` ratio {cr:+.4f}  (margin {float(core_m[0]):+.10f}, "
          f"MDE {float(core_mde[0]):.10f})")
    print(f"     sits at the {pct:.3f}th percentile of the LOO null")

    p95 = float(np.percentile(loo, 95))
    world = "A" if p95 < FLOOR * 0.5 else ("B" if p95 >= FLOOR else "C")
    print(f"\n  ⭐ null p95 = {p95:+.4f}  vs the project's floor {FLOOR}")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "the floor is FAR over-strict against a max comparator — it rejects at a far smaller"
             " false-positive rate than it was chosen to deliver",
        "B": "the floor is NOT conservative here — a max comparator inflates the statistic and 1.5"
             " is too PERMISSIVE",
        "C": "the null's p95 brackets 1.5 — the bar transfers, and the denominator was the right"
             " place to have been looking"}[world])
    fp = float((loo >= FLOOR).mean())
    print(f"     empirical false-positive rate of `ratio >= {FLOOR}` under this null: {fp*100:.4f}%"
          f"  ({int((loo>=FLOOR).sum())} of {M})")

    # ---- POSITIVE CONTROL: planted dose-response, and it must fail at g=0 -----------------------
    print(f"\n  POSITIVE CONTROL  plant g on the arm; the ratio must RISE and must NOT clear"
          f" {FLOOR} at g=0")
    dose = []
    for g in DOSES:
        rr, mm, _ = ratios((core + g)[None, :], B[kglob][None, :], 11)
        dose.append({"g": g, "ratio": float(rr[0]), "margin": float(mm[0]),
                     "clears": bool(rr[0] >= FLOOR)})
        print(f"    g={g:<6} ratio {float(rr[0]):+.4f}  {'CLEARS' if rr[0] >= FLOOR else 'below'}")
    rises = all(dose[i + 1]["ratio"] > dose[i]["ratio"] for i in range(len(dose) - 1))
    g0_ok = not dose[0]["clears"]
    print(f"    monotone in g: {rises}  {'PASS' if rises else 'FAIL'}   ·   "
          f"does NOT clear at g=0: {g0_ok}  {'PASS' if g0_ok else 'FAIL'}")
    first = next((d["g"] for d in dose if d["clears"]), None)
    print(f"    smallest planted g clearing the floor: {first}"
          f"{'  (none in the swept range)' if first is None else ''}")

    # ---- SECOND NULL: shuffled target, which does NOT share the LOO null's defect ---------------
    sh = []
    for sd in (11, 22, 33):
        r = np.random.default_rng(sd)
        Hs = [h[:, r.permutation(6)] for h in H]
        Bs = np.empty((M, N)); cs = np.empty(N)
        for n in range(N):
            Y = SAT[n][subs].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            Bs[:, n] = (C_[:, None, :] == Hs[n][None, :, :]).mean(axis=(1, 2))
            cv = cls(yvec(A[pids[n]], sorted({i for i, _ in A[pids[n]]})))
            cs[n] = np.mean([[cv[c] == h[c] for c in range(6)] for h in Hs[n]])
        kk = int(Bs.mean(1).argmax())
        rr, _, _ = ratios(cs[None, :], Bs[kk][None, :], 11)
        sh.append(float(rr[0]))
    print(f"\n  SECOND NULL (shuffled target, does NOT share the LOO null's membership defect):")
    print(f"    core-vs-max ratio over 3 seeds: {[round(x, 4) for x in sh]}  "
          f"mean {np.mean(sh):+.4f}")
    print(f"    ⚠ reported BESIDE the LOO null, not merged into it — the two nulls destroy"
          f" different structure.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "n_prompts": N, "family": M, "world": world,
               "derivation_exchangeable_p_positive": 1.0 / (M + 1),
               "bar_implied_z": FLOOR * ZEFF,
               "loo_null_percentiles": dict(zip([str(q) for q in qs], [float(x) for x in pv])),
               "loo_null_positive_margins": int((loo_m > 0).sum()),
               "core_ratio": cr, "core_percentile_in_null": pct,
               "null_p95": p95, "floor": FLOOR,
               "empirical_fp_rate_at_floor": fp,
               "dose_response": dose, "dose_monotone": rises, "fails_at_g0": g0_ok,
               "first_clearing_g": first,
               "second_null_shuffled_target": sh,
               "controls": {"placebo_margin": float(pl_m[0]), "loo_nondegenerate": nondeg,
                            "reproduced_r860_mde": mde860}},
              open(OUT / "floor_calibration.json", "w"), indent=2)
    print(f"\n  artifact: results/floor_calibration.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
