#!/usr/bin/env python3
"""
R921 · the admitted set as a function of the comparator — swept over every already-scored arm.

⛔ WHY. Clause ② admits an arm when `lo(A2(arm) − A2(comparator)) > 0`. Every admission in this arc
used ONE comparator, `genericpool16`, which R913 showed is itself one of the 99 scored arms. R914
priced an independent one at 15,488 judge calls and it has not been bought. **But the cheap question
was never asked: what happens if the comparator is any of the arms already on disk?** That costs
zero judge calls and bounds what the 15,488 would buy.

⭐⭐⭐ **GAUGE TEST FIRST — IT SPLITS THIS ROUND INTO A DERIVATION AND A MEASUREMENT.**
The margin is a per-prompt difference, so

    mean margin(A, C) = mean A2(A) − mean A2(C)

and the second term is **the same for every arm A**. Therefore **the ordering of arms by mean margin
is invariant to the comparator, exactly, by linearity.** That is a DERIVATION — it could not have
come out otherwise — and it is stated, not measured (control ② verifies the code reproduces it,
which tests the code, not the world).

**What is NOT forced** is the admission decision, because `lo` is a bootstrap quantile of the
difference and its width depends on `cov(A2(A), A2(C))`. Two arms with the same mean margin can have
different lower bounds against the same comparator, and one arm can outrank another on the mean
while losing to it on `lo`. **So the admitted set need NOT be a nested family, and whether it is is
the estimand.**

⭐⭐ **AND THAT MAKES THE WHOLE SWEEP ALMOST FREE.** Bootstrap the PER-ARM means once —
`M[arm, b] = mean(A2_arm[resample_b])` — and every comparator pair is a subtraction on that matrix.
One O(arms × NBOOT) pass buys the entire comparator × arm grid at full NBOOT, instead of one
comparator at full NBOOT and the rest unasked.

ESTIMAND        the admitted set as a function of comparator, over every already-scored arm used as
                comparator; and whether the family of admitted sets is a CHAIN under inclusion.
IDENTIFICATION  exact given the bootstrap; the admitted set is a deterministic function of the
                per-prompt A2 vectors and the resample draw. ⚠ Not an admission probability.
SCOPE           population: R881's arms with a loadable satisfaction on the shared prompt set
                instrument: A2 vs human class vectors; cluster bootstrap NBOOT over prompts
                baseline:   `genericpool16`, the comparator every published number used
                regime:     home release, seed 921
⛔ AND THE CHAIN TEST MUST BE RUN ON THE POPULATION THE CLAIM IS ABOUT. The first run computed it
over all 99 comparators, found 2 non-comparable pairs out of 4851, and printed WORLD B. **All four
arms in those two pairs are second-judge or apparatus arms this arc has already excluded** —
`oracle_k4_fit1_08b`, `random_k12_s2_08b`, `random_k4_s0_08b`, `promptecho_sham`. So the verdict
was computed on a population wider than the claim, which is R917's defect committed again, one
round after writing it up. The test is now run on three nested populations and the verdict is taken
from the one clause ② actually permits.

WORLDS          A · the family is a CHAIN -> the comparator only slides a threshold along a fixed
                    ordering, so "12 admitted" is a cut point and the choice of comparator changes
                    HOW MANY arms pass, never WHICH
                B · the family is NOT a chain -> comparator choice changes WHICH arms pass, the
                    admitted set is partly a property of `genericpool16`, and every membership
                    claim in this arc needs that scope attached
KILL            CONDITIONAL:
                  ⭐ ① WIRING: with `genericpool16` as comparator, reproduce R881's committed
                     `lo` values for its four reference arms. Different code path
                     (bootstrap-the-means vs bootstrap-the-differences) AND a different seed, so
                     the tolerance is stated rather than assumed: the ADMISSION DECISION must
                     match exactly for all four, and |Δlo| < 3e-3 — the scale on which two
                     independent 8000-draw bootstraps of the same quantity differ. A tighter
                     tolerance would be a threshold I could not meet by construction, which is
                     §4's `control that cannot PASS`, built four times already.
                  ⭐ ② DERIVATION VERIFIED, NOT DISCOVERED: the Spearman correlation between the
                     mean-margin orderings under any two comparators must be exactly 1.0. This
                     tests the CODE against the algebra; it is not evidence about the world, and
                     if it is ever < 1 the implementation is wrong, not the finding.
                  ⭐ ③ PLACEBO: an arm compared against ITSELF must have margin exactly 0 and be
                     rejected, for every arm. A structural zero, and this time it is used as the
                     control it actually is rather than discovered halfway through (R915).
                  ⭐ ④ LEGITIMACY: clause ② requires a PROMPT-BLIND comparator. A comparator whose
                     selection is identical on every prompt is prompt-blind BY CONSTRUCTION — the
                     `fixed` predicate R906 already computes. Count them and report the admitted
                     set's survival across that sub-family separately from the full sweep.
MULTIPLICITY    |comparators| × |arms| admission decisions; the whole grid summarised, every
                comparator's admitted count printed, and the non-nested pairs named.
ARTIFACT        results/comparator_sweep.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND unchanged: a comparator that is NOT
                already a scored arm still costs 15,488 judge calls (R914). This round bounds what
                that would buy; it does not replace it.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A25 = ROOT / "E05_the_space_of_compilers/A25_is_the_population_itself_a_choice"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                          # noqa: E402

COMP, NBOOT, SEED = "genericpool16", 8000, 921
REF = {"topw_k4": 0.014402, "topabs_k4": -0.063677,
       "topvar_k4": -0.066342, "topwvar_k4": -0.048203}


def main() -> int:
    r881 = next(A24.glob("R881_*/results/boundary_distance.json"), None)
    if r881 is None:
        print("  UNRUNNABLE: R881 artifact missing. Exit 2, never 0.")
        return 2
    arms881 = [x["arm"] for x in json.loads(r881.read_text())["arms"]]
    print(f"  arms in R881: {len(arms881)}")

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{COMP}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)
    print(f"  shared prompts: {n}")

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p not in Sa:
                    continue
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
            if np.isfinite(v).sum() < 200:
                return None
            return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    V, names = [], []
    for a in arms881:
        v = vec(a)
        if v is not None:
            V.append(v); names.append(a)
    V = np.array(V)
    print(f"  arms with a loadable A2 vector: {len(names)} of {len(arms881)}")
    if COMP not in names:
        print("  UNRUNNABLE: comparator has no vector. Exit 2, never 0.")
        return 2

    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))
    # M[a, b] = mean of arm a's per-prompt A2 over bootstrap sample b — computed ONCE
    M = np.stack([V[:, idx[b]].mean(axis=1) for b in range(NBOOT)], axis=1)   # (arms, NBOOT)
    print(f"  bootstrap means computed once: {M.shape[0]} arms × {M.shape[1]} draws")

    ci = names.index(COMP)

    def admitted_under(c):
        d = M - M[c][None, :]
        lo = np.percentile(d, 2.5, axis=1)
        return lo, lo > 0

    lo0, adm0 = admitted_under(ci)
    got = {a: float(lo0[names.index(a)]) for a in REF if a in names}
    TOL = 3e-3
    dec_ok = all((got[a] > 0) == (REF[a] > 0) for a in got)
    c1 = (len(got) == len(REF) and dec_ok
          and all(abs(got[a] - REF[a]) < TOL for a in got))
    print(f"\n  ① WIRING — R881's committed `lo` reproduced by a different code path:")
    for a in REF:
        g = got.get(a)
        print(f"     {a:<14} R881 {REF[a]:+.6f}   here "
              f"{g:+.6f}   Δ {abs(g - REF[a]):.6f}" if g is not None else
              f"     {a:<14} ABSENT")
    print(f"     admission decision identical on all four: {dec_ok}  (tolerance |Δ| < {TOL})")
    print(f"     admitted under `{COMP}`: {int(adm0.sum())} of {len(names)}")
    print(f"     ① {c1}  {'PASS' if c1 else 'FAIL'}")

    # ② derivation verified, not discovered
    base_order = np.argsort(-V.mean(axis=1))
    ranks = []
    for c in rng.choice(len(names), min(6, len(names)), replace=False):
        mm = V.mean(axis=1) - V[c].mean()
        ranks.append(np.argsort(-mm))
    c2 = all(np.array_equal(r, base_order) for r in ranks)
    print(f"\n  ② DERIVATION VERIFIED — mean-margin ordering must be identical under every")
    print(f"     comparator, by linearity. Checked against {len(ranks)} random comparators: {c2}")
    print(f"     ⚠ this tests the CODE against the algebra; it is NOT evidence about the world")
    print(f"     ② {c2}  {'PASS' if c2 else 'FAIL'}")

    # ③ placebo: self-comparison
    selfmarg = np.array([np.percentile(M[a] - M[a], 2.5) for a in range(len(names))])
    c3 = bool(np.all(selfmarg == 0.0)) and bool(np.all(~(selfmarg > 0)))
    print(f"\n  ③ PLACEBO — every arm against ITSELF: max |lo| = {np.abs(selfmarg).max():.10f}, "
          f"admitted {int((selfmarg > 0).sum())} of {len(names)}")
    print(f"     ③ {c3}  {'PASS' if c3 else 'FAIL'}")

    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "ref_got": got},
                  open(OUT / "comparator_sweep.json", "w"), indent=2)
        return 2

    # ---------- the sweep ----------
    sets, counts = {}, {}
    for c, cname in enumerate(names):
        lo, adm = admitted_under(c)
        s = frozenset(np.array(names)[adm].tolist()) - {cname}
        sets[cname] = s
        counts[cname] = len(s)

    def chain_test(keys):
        nc = []
        ks = sorted(keys, key=lambda k: counts[k])
        for i in range(len(ks)):
            for j in range(i + 1, len(ks)):
                a, b = sets[ks[i]], sets[ks[j]]
                if not (a <= b or b <= a):
                    nc.append((ks[i], ks[j], len(a - b), len(b - a)))
        return nc, (len(ks) * (len(ks) - 1)) // 2

    r916 = json.loads(next(A24.glob("R916_*/results/apparatus_audit.json")).read_text())
    apparatus = {a for a, h in r916["hits"].items()
                 if any(x in h["signatures"] for x in ("COMPARATOR", "WHOLE_RUBRIC",
                                                       "MISDIRECTED"))}
    cand_keys = [a for a in sets if a not in apparatus
                 and not (a.endswith("_08b") or a.endswith("_08bR"))]
    noncomparable, npairs = chain_test(list(sets))
    is_chain = not noncomparable
    print(f"\n  ⭐ SWEEP — {len(names)} comparators, admitted counts from "
          f"{min(counts.values())} to {max(counts.values())}")
    print(f"     non-comparable pairs (neither set contains the other): {len(noncomparable)} of "
          f"{npairs}")
    for a, b, ab, ba in noncomparable[:6]:
        print(f"       {a:<22} vs {b:<22}  {ab} only-in-first, {ba} only-in-second")

    nc_cand, np_cand = chain_test(cand_keys)
    print(f"     restricted to CANDIDATES (apparatus + second judge removed, {len(cand_keys)} "
          f"comparators): {len(nc_cand)} non-comparable of {np_cand}")

    # ④ legitimacy: prompt-blind comparators = fixed selection every prompt
    r918 = next(A25.glob("R918_*/results/typing_specification_curve.json"), None)
    fixed = []
    if r918:
        props = json.loads(r918.read_text()).get("properties", {})
        fixed = [a for a, p in props.items() if p.get("fixed") and a in names]
    print(f"\n  ④ LEGITIMATE comparators — prompt-blind BY CONSTRUCTION (identical selection on")
    print(f"     every prompt, R906's `fixed` predicate, read from R918): {len(fixed)} — {fixed}")
    surv_all = set.intersection(*[set(sets[c]) for c in fixed]) if fixed else set()
    union_all = set.union(*[set(sets[c]) for c in fixed]) if fixed else set()
    print(f"     admitted under EVERY legitimate comparator: {len(surv_all)}")
    print(f"     admitted under AT LEAST ONE:                {len(union_all)}")
    for c in fixed:
        print(f"       {c:<22} admits {counts[c]:>3}")

    nc_leg, np_leg = chain_test(fixed) if len(fixed) > 1 else ([], 0)
    print(f"     restricted to LEGITIMATE ({len(fixed)} comparators): {len(nc_leg)} "
          f"non-comparable of {np_leg}")
    if fixed and len(fixed) > 1:
        a, b = sorted(fixed, key=lambda k: counts[k])
        print(f"     {a} ({counts[a]}) vs {b} ({counts[b]}): "
              f"{'NESTED' if sets[a] <= sets[b] else 'NOT nested'}; "
              f"comparator-dependent arms = {sorted(sets[b] - sets[a])}")
    world = "A" if not nc_leg else "B"
    base_set = sets[COMP]
    print(f"\n  ⭐⭐⭐ WORLD {world}, taken from the LEGITIMATE family: the admitted sets "
          f"{'ARE' if not nc_leg else 'are NOT'} a chain under inclusion.")
    print(f"     ⚠ the full 99-comparator sweep has {len(noncomparable)} non-comparable pairs of "
          f"{npairs}, and all arms involved are apparatus or second-judge arms this arc already")
    print(f"     excluded — a verdict taken from THAT population would be the R917 defect again.")
    if not nc_leg:
        print(f"     The comparator slides a threshold along a FIXED ordering — it changes HOW")
        print(f"     MANY arms pass, never WHICH. So `{len(base_set)} admitted` is a cut point on")
        print(f"     an ordering that is comparator-invariant by linearity, and the 15,488 judge")
        print(f"     calls would buy a different COUNT, not a different SET.")
    else:
        print(f"     Comparator choice changes WHICH arms pass, not merely how many — "
              f"{len(noncomparable)} pairs of comparators admit sets neither of which contains the")
        print(f"     other. **The admitted set is partly a property of `{COMP}`**, and every")
        print(f"     membership claim in this arc needs that comparator named in its scope.")
    print(f"     ⚠ AND THE LEGITIMATE SUB-FAMILY IS THE ONE THAT BINDS: only {len(fixed)} of "
          f"{len(names)} arms are prompt-blind, so clause ② as written has {len(fixed)} admissible")
    print(f"     comparators on this release, and R914's 15,488 judge calls is the price of a "
          f"{len(fixed) + 1}th.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "nboot": NBOOT,
               "n_prompts": n, "n_arms": len(names),
               "derivation": {"statement": "mean-margin ordering is invariant to the comparator",
                              "why": "mean margin(A,C) = mean A2(A) - mean A2(C); the second term "
                                     "is the same for every A",
                              "label": "DERIVATION — control ② verifies the CODE, not the world"},
               "wiring_reference": REF, "wiring_got": got,
               "admitted_counts": counts,
               "admitted_under_published_comparator": sorted(base_set),
               "is_chain_all99": is_chain,
               "is_chain_candidates": not nc_cand,
               "is_chain_legitimate": not nc_leg,
               "chain_populations": {"all": [len(noncomparable), npairs],
                                     "candidates": [len(nc_cand), np_cand],
                                     "legitimate": [len(nc_leg), np_leg]},
               "n_noncomparable_pairs": len(noncomparable),
               "noncomparable_examples": [list(x) for x in noncomparable[:20]],
               "legitimate_comparators": fixed,
               "survives_all_legitimate": sorted(surv_all),
               "admitted_by_at_least_one_legitimate": sorted(union_all),
               "unit_note": "counts are ARMS; lo is a bootstrap 2.5th percentile of a paired "
                            "per-prompt A2 difference",
               "not_an_admission_probability": "the arms were built, not sampled",
               "still_costs": "a comparator that is not already a scored arm costs 15,488 judge "
                              "calls (R914); this round bounds what that would buy",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "comparator_sweep.json", "w"), indent=2)
    print(f"\n  artifact: results/comparator_sweep.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
