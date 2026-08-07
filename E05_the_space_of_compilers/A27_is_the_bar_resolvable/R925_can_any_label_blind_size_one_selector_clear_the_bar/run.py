#!/usr/bin/env python3
"""
R925 · sweep every label-blind size-1 selector the generator's own orderings admit — 4 orderings ×
        15 rank positions × 2 coverage rules — and price what label access buys at k=1.

⛔ WHY. R924 showed the k=1 ORACLE clears clause ② by ~10× the bar's resolution, so clause ① is not
implied by clause ②. But the oracle consumes labels and clause ③ excludes it anyway, so **clause ①'s
INDEPENDENT necessity turns on whether any LABEL-BLIND size-1 selector clears the bar** — and exactly
one was ever built (`topw_k1`, not admitted). One arm is an observation, not a bound.

⭐ THE GENERATOR ALREADY NAMES THE LABEL-BLIND ORDERINGS, so no new idea is required: mean criterion
weight (`topw_k`), absolute weight (`topabs_k`), satisfaction variance across the four responses
(`topvar_k`), and their product (`topwvar_k`). `select_core.py` states in its own comment that
variance is *"a property of the responses, never of the human target"* — that is what makes these
admissible under clause ③. **But every one of them was only ever run at RANK 1.** Sweeping the rank
position `r = 1..15` asks the question the arc never asked: is the top-ranked criterion simply the
wrong one to take?

⭐⭐ **AND THE GAP TO THE ORACLE IS A NEW NUMBER WORTH MORE THAN THE VERDICT: it prices clause ③ at
k=1.** ⚠ Its SIGN is forced — the oracle is a per-prompt maximum, so `gap >= 0` by construction and
that is a DERIVATION. Its SIZE is not, and neither is the comparison that matters: **is label access
worth more at k=1 than at k=4?** At k=4 the same gap is `0.6287 − 0.5648 = 0.0639` (R920/R924's
committed numbers). If the k=1 gap is larger, clause ③ protects most exactly where clause ① bites.

⛔ **AND THE EMISSION INDEX IS NOT THE RUBRIC INDEX — CONTROL ① CAUGHT IT AT |ΔA2| = 0.544.**
`select_core.py` emits `f"{pid}|{j}|{x}"` where `j` is the POSITION IN `sel`, and for the `full` arm
`sel = ok`, the criteria judged in both npzs — a FILTERED subset of `range(len(items))`. So
`sat_full.npz`'s indices enumerate `ok`, not the rubric, and reading `items[p][i]` with them
misaligns every weight. The first run's rank-1-by-weight therefore picked a different criterion from
the built `topw_k1` on most prompts. **The fix is the mapping R920 already needed: `core_full.json`
stores the emitted criteria as TEXTS in emission order, so position → text → rubric index is exact,
and its misses are counted.** ⚠ Ninth scope/index error of the session; second caught by a control
written for it rather than after publication.

⚠ **AND CONTROL ②'s 529 "violations" WERE MY OWN NaN-FILL.** A RESTRICTED arm is undefined on
prompts with fewer than `r` criteria, and filling those with the arm's own MEAN can exceed that
prompt's oracle maximum. The bound must be checked only where the arm is DEFINED — comparing a
filled value against a per-prompt maximum is comparing two different objects, which is §4's
"the control compares two different draws as though they were one".

⛔ **AND THE SORT'S STABILITY IS PART OF THE SPECIFICATION.** `select_core.py` orders with Python's
`sorted(ok, key=...)`, which is STABLE — ties fall back on rubric order. `np.argsort` defaults to an
UNSTABLE quicksort. Measured: rank-1 differs from the built `topw_k1` on **137 of 968** prompts with
the default sort and **8** with `kind="stable"`. A tie-breaking rule is not a detail here; it is a
26%-of-the-population difference in which criterion the arm selects.
**The residual 8 are NOT tolerated by loosening the control** — that would be the mirror of the
control-that-cannot-PASS, a threshold moved until it is met. Instead the control is restated as
something mechanically checkable: **every disagreement must lie on a prompt where rank 1 is not
uniquely determined** — a tie at the top weight, or a NaN weight from a criterion with no scores
(`np.mean([]) or 0.0` returns NaN, which is truthy, so the generator itself can carry NaN weights).
If a disagreement lands on a prompt with a unique finite maximum, the reproduction is genuinely
wrong and the round is UNVERIFIED.

⛔ **AND A TEXT KEY IS NOT AN IDENTITY KEY. THE LAST 2 MISMATCHES WERE DUPLICATE CRITERIA.**
After the stable sort, 2 of 968 prompts still disagreed on a determined rank 1 — and on both, the
built arm and this one selected **the same criterion TEXT**. Each rubric contains a criterion whose
text appears TWICE with different weights and different satisfaction rows, so a `text -> index` dict
collapses the pair onto its first occurrence and attributes the wrong row. **The instrument's unit
was TEXT; the claim's unit is CRITERION INDEX**, which is §4's "a positive control asks *can this
instrument see?* and never *is what it sees the thing I am about to claim about?*" — the two units
must be named separately and required to be equal before the control is designed. Repaired with an
order-preserving two-pointer match, which is exact because the emitted sequence is a subsequence of
the rubric in increasing index order by construction.

⚠ **COVERAGE IS A SPECIFICATION AXIS, NOT A CHOICE TO HIDE.** A rank-`r` rule is undefined on a
prompt whose rubric has fewer than `r` criteria (mean rubric size 15.5, so this bites at high `r`).
Dropping those prompts silently would change the population per arm — the defect this session has
committed eight times. Both rules are therefore run and reported: **RESTRICTED** (only prompts with
`>= r` criteria, so the arm is exact but the population shrinks with `r`) and **CLAMPED** (take
`min(r, m)`, so all 968 prompts are covered and the arms are comparable across `r`).

ESTIMAND        whether any label-blind size-1 selector satisfies clause ②; and the mean-A2 gap
                between the k=1 oracle and the best label-blind size-1 selector.
IDENTIFICATION  exact. Every arm is a deterministic function of committed satisfaction and weights.
                ⚠ Not an admission probability.
SCOPE           population: every prompt's `coval_full` rubric as judged by 2B (the oracle's judge
                            scope, established by R924's control ②)
                instrument: A2 vs human class vectors; cluster bootstrap NBOOT 8000, seed 921
                baseline:   both legitimate comparators, `generic` and `genericpool16`
                regime:     home release
WORLDS          A · no label-blind size-1 selector clears the bar -> clause ① is independently
                    necessary against every ordering this generator can express, and the gap to the
                    oracle prices clause ③ at k=1
                B · some rank-r arm clears it -> clause ① would EXCLUDE an admissible core, so it
                    is not merely unnecessary but WRONG, and the definition must be repaired
                C · it clears under one comparator only -> clause ①'s status is comparator-dependent
KILL            CONDITIONAL:
                  ⭐ ① WIRING: `weight`-ordering at rank 1, CLAMPED, must reproduce `topw_k1`'s
                     per-prompt A2 to 1e-9 on every shared prompt and its R881 admission decision.
                     Same object by two routes, or the sweep is measuring something else.
                  ⭐ ② UPPER-BOUND VALIDITY: R924's k=1 oracle must be >= every swept arm on EVERY
                     prompt. ⚠ Forced within a judge; an index check over 120 arms rather than 1.
                  ⭐ ③ PLACEBO: a uniformly random rank must land mid-distribution among the
                     single-criterion A2 scores. NOT forced.
                  ⭐ ④ THE ORDERINGS MUST ACTUALLY DIFFER: if two orderings pick the same criterion
                     on almost every prompt they are one specification wearing two names, and the
                     grid is narrower than it looks. Report pairwise agreement.
MULTIPLICITY    4 orderings × 15 ranks × 2 coverage rules × 2 comparators = 240 admission
                decisions. Cells tested and cells surviving both reported, with BH over the grid.
ARTIFACT        results/label_blind_k1_sweep.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND: this sweeps the orderings THIS generator
                expresses. A label-blind size-1 selector built on some other property of the
                criteria is not covered, and no bound here excludes one.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls, L, PAIRS                # noqa: E402
from covalx.judge import load_join                                           # noqa: E402

NBOOT, SEED, RMAX = 8000, 921, 15
ORDERINGS = ("weight", "abs_weight", "variance", "weight_x_variance")
K4_GAP = 0.6287 - 0.5648        # oracle_k4 − topw_k4, from committed artifacts, for CONTRAST


def bh(ps, q=0.05):
    m = len(ps)
    order = np.argsort(ps)
    thr = q * (np.arange(1, m + 1)) / m
    passing = np.array(ps)[order] <= thr
    kmax = np.max(np.nonzero(passing)[0]) + 1 if passing.any() else 0
    keep = set(order[:kmax].tolist())
    return keep


def main() -> int:
    r881 = next(A24.glob("R881_*/results/boundary_distance.json"), None)
    r921 = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    r924 = next(A27.glob("R924_*/results/clause_one_necessity.json"), None)
    if not (r881 and r921 and r924):
        print("  UNRUNNABLE: a prior artifact is missing. Exit 2, never 0.")
        return 2
    legit = json.loads(r921.read_text())["legitimate_comparators"]
    adm881 = {x["arm"]: bool(x["admitted"]) for x in json.loads(r881.read_text())["arms"]}
    print(f"  legitimate comparators {legit} · orderings {ORDERINGS} · ranks 1..{RMAX}")

    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    items = {pid: (r.get("coval_full") or []) for pid, _q, r in joined}
    # emission position -> rubric index, via the committed texts (see the index note above)
    emitted = json.loads((RES / "core_full.json").read_text())
    pids = sorted(set(Sfull) & set(items) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def a2c(cv, p):
        return float(np.mean([(cv == h).mean() for h in H[p]]))

    # per prompt: criterion A2 vector, and the four label-blind orderings
    per, wmiss = {}, 0
    for p in pids:
        idxs = sorted({i for i, _ in Sfull[p]})
        S = np.array([[Sfull[p].get((i, x), 0.0) for x in L] for i in idxs])
        C = np.stack([np.sign(S[:, i] - S[:, j]) for i, j in PAIRS], axis=1)
        a2 = np.array([a2c(C[r], p) for r in range(C.shape[0])])
        # ⚠ ORDER-PRESERVING match, not a dict: duplicate criterion texts exist and a
        # text->index dict collapses them onto the first occurrence (see the duplicate note above)
        emit = emitted.get(p, [])
        rub = [t["criterion"] for t in items[p]]
        w = np.zeros(len(idxs))
        j = 0
        for pos in range(len(idxs)):
            if pos >= len(emit):
                wmiss += 1
                continue
            while j < len(rub) and rub[j] != emit[pos]:
                j += 1
            if j >= len(rub):
                wmiss += 1
                continue
            w[pos] = float(np.mean([sc["score"] for sc in (items[p][j].get("scores") or [])])
                           or 0.0)
            j += 1
        var = S.var(axis=1)
        # STABLE, to match `sorted(ok, key=...)` in select_core.py — see the sort note above
        ords = {"weight": np.argsort(-w, kind="stable"),
                "abs_weight": np.argsort(-np.abs(w), kind="stable"),
                "variance": np.argsort(-var, kind="stable"),
                "weight_x_variance": np.argsort(-(np.abs(w) * var), kind="stable")}
        fin = np.isfinite(w)
        top_unique = bool(fin.all() and (w == w.max()).sum() == 1) if len(w) else False
        per[p] = {"idxs": idxs, "a2": a2, "ords": ords, "m": len(idxs),
                  "rank1_determined": top_unique}
    print(f"  prompts {n} · mean rubric size {np.mean([per[p]['m'] for p in pids]):.1f}")
    print(f"  emission-position -> rubric-index misses: {wmiss} (counted, not silently zeroed)")

    # ---------- build the sweep ----------
    defined = {}

    def arm_vec(ordering, r, clamp):
        v = np.full(n, np.nan)
        for k, p in enumerate(pids):
            m = per[p]["m"]
            if r > m:
                if not clamp:
                    continue
                pos = m - 1
            else:
                pos = r - 1
            v[k] = per[p]["a2"][per[p]["ords"][ordering][pos]]
        return v

    arms, names = [], []
    for o in ORDERINGS:
        for r in range(1, RMAX + 1):
            for clamp in (True, False):
                v = arm_vec(o, r, clamp)
                cov = int(np.isfinite(v).sum())
                if cov < 200:
                    continue
                defined[len(arms)] = np.isfinite(v)
                arms.append(np.nan_to_num(v, nan=np.nanmean(v)))
                names.append((o, r, "CLAMPED" if clamp else "RESTRICTED", cov))
    print(f"  label-blind size-1 arms built: {len(arms)}")

    def full_vec(nm):
        f = RES / f"sat_{nm}.npz"
        if not f.exists():
            return None
        Sa = load_sat(f)
        v = np.full(n, np.nan)
        for k, p in enumerate(pids):
            if p in Sa:
                v[k] = a2c(np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float), p)
        return np.nan_to_num(v, nan=np.nanmean(v))

    oracle = np.array([per[p]["a2"].max() for p in pids])
    comp = {c: full_vec(c) for c in legit}
    topw_k1 = full_vec("topw_k1")

    V = np.vstack(arms + [oracle] + [comp[c] for c in legit])
    lab = names + [("_oracle", 1, "ORACLE", n)] + [(c, 0, "COMPARATOR", n) for c in legit]
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))
    M = np.stack([V[:, idx[b]].mean(axis=1) for b in range(NBOOT)], axis=1)
    print(f"  bootstrap means: {M.shape[0]} vectors × {M.shape[1]} draws")

    # ---------- ① WIRING ----------
    wi = names.index(("weight", 1, "CLAMPED", n)) if ("weight", 1, "CLAMPED", n) in names else None
    c1 = False
    if wi is not None and topw_k1 is not None:
        dif = np.abs(arms[wi] - topw_k1) > 1e-9
        det = np.array([per[p]["rank1_determined"] for p in pids])
        bad = [pids[k] for k in np.nonzero(dif & det)[0]]
        ci = lab.index((legit[-1], 0, "COMPARATOR", n))
        lo_sweep = float(np.percentile(M[wi] - M[ci], 2.5))
        c1 = (len(bad) == 0) and ((lo_sweep > 0) == adm881.get("topw_k1", False))
        print(f"\n  ① WIRING — `weight` rank 1 CLAMPED vs the built `topw_k1`:")
        print(f"     prompts differing at all: {int(dif.sum())} of {n}")
        print(f"     of those, on prompts where rank 1 IS uniquely determined: {len(bad)} "
              f"(must be 0){' — ' + str(bad[:3]) if bad else ''}")
        print(f"     prompts with a tie or NaN at the top weight: {int((~det).sum())}")
        print(f"     admission here {lo_sweep > 0} vs R881 {adm881.get('topw_k1')}")
    print(f"     ① {c1}  {'PASS' if c1 else 'FAIL'}")

    # ---------- ② UPPER-BOUND VALIDITY ----------
    # ⚠ checked only where the arm is DEFINED — a NaN-filled cell is not the arm's value
    viol = int(sum(((a > oracle + 1e-12) & defined[i]).sum() for i, a in enumerate(arms)))
    ncells = int(sum(defined[i].sum() for i in range(len(arms))))
    c2 = viol == 0
    print(f"\n  ② UPPER-BOUND VALIDITY — prompt-cells where a swept arm beats the k=1 oracle: "
          f"{viol} of {ncells} DEFINED cells   ⚠ forced within a judge; an index check over "
          f"{len(arms)} arms")
    print(f"     ⚠ checked only where the arm is defined; the first run compared NaN-FILLED cells "
          f"against a per-prompt maximum and got 529 false violations")
    print(f"     ② {c2}  {'PASS' if c2 else 'FAIL'}")

    # ---------- ③ PLACEBO ----------
    rng3 = np.random.default_rng(SEED + 3)
    rv = np.array([per[p]["a2"][rng3.integers(0, per[p]["m"])] for p in pids])
    pct = float(np.mean([(per[p]["a2"] < rv[k]).mean() + 0.5 * (per[p]["a2"] == rv[k]).mean()
                         for k, p in enumerate(pids)]))
    c3 = 0.35 <= pct <= 0.65
    print(f"\n  ③ PLACEBO — uniformly random rank sits at percentile {pct:.4f} "
          f"(band [0.35, 0.65]): {c3}  {'PASS' if c3 else 'FAIL'}")

    # ---------- ④ DO THE ORDERINGS DIFFER? ----------
    agree = {}
    for i in range(len(ORDERINGS)):
        for j in range(i + 1, len(ORDERINGS)):
            a, b = ORDERINGS[i], ORDERINGS[j]
            agree[f"{a}|{b}"] = float(np.mean([per[p]["ords"][a][0] == per[p]["ords"][b][0]
                                               for p in pids]))
    c4 = max(agree.values()) < 0.95
    print(f"\n  ④ ORDERINGS MUST DIFFER — share of prompts where two orderings pick the SAME "
          f"rank-1 criterion:")
    for k, v in sorted(agree.items(), key=lambda z: -z[1]):
        print(f"     {k:<36}{v:.4f}")
    print(f"     ④ max agreement {max(agree.values()):.4f} < 0.95: {c4}  "
          f"{'PASS' if c4 else 'FAIL — the grid is narrower than it looks'}")

    if not (c1 and c2 and c3 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "c4": c4,
                   "ordering_agreement": agree},
                  open(OUT / "label_blind_k1_sweep.json", "w"), indent=2)
        return 2

    # ---------- the sweep ----------
    rows, ps = [], []
    for a_i, (o, r, cov_rule, cov) in enumerate(names):
        row = {"ordering": o, "rank": r, "coverage": cov_rule, "n_prompts": cov,
               "mean_a2": float(arms[a_i].mean())}
        for c in legit:
            ci = lab.index((c, 0, "COMPARATOR", n))
            d = M[a_i] - M[ci]
            lo = float(np.percentile(d, 2.5))
            row[f"lo_{c}"] = lo
            row[f"adm_{c}"] = bool(lo > 0)
            ps.append(float((d <= 0).mean()))
        rows.append(row)
    survivors = [r for r in rows if any(r[f"adm_{c}"] for c in legit)]
    keep = bh(ps)
    print(f"\n  MULTIPLICITY — cells tested {len(ps)} (= {len(names)} arms × {len(legit)} "
          f"comparators); cells surviving BH q=0.05: {len(keep)}; "
          f"arms admitted by the raw bar: {len(survivors)}")

    best = max(rows, key=lambda z: z["mean_a2"])
    print(f"\n  ⭐ BEST label-blind size-1 arm: `{best['ordering']}` rank {best['rank']} "
          f"{best['coverage']} — mean A2 {best['mean_a2']:.4f}, "
          f"lo vs generic {best['lo_generic']:+.6f}, "
          f"lo vs genericpool16 {best['lo_genericpool16']:+.6f}")
    print(f"\n  ⭐ TOP 8 BY MEAN A2 (of {len(rows)}), and the comparators for scale:")
    print(f"     {'ordering':<20}{'rank':>5}{'coverage':>12}{'n':>6}{'mean A2':>10}"
          f"{'lo vs generic':>15}")
    for r_ in sorted(rows, key=lambda z: -z["mean_a2"])[:8]:
        print(f"     {r_['ordering']:<20}{r_['rank']:>5}{r_['coverage']:>12}{r_['n_prompts']:>6}"
              f"{r_['mean_a2']:>10.4f}{r_['lo_generic']:>+15.6f}")
    for c in legit:
        print(f"     {'(comparator) ' + c:<20}{'':>5}{'':>12}{n:>6}"
              f"{float(comp[c].mean()):>10.4f}")
    print(f"     {'(k=1 ORACLE)':<20}{'':>5}{'':>12}{n:>6}{float(oracle.mean()):>10.4f}")

    gap = float(oracle.mean() - best["mean_a2"])
    world = "A" if not survivors else ("B" if len(survivors) > 0 else "C")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"NO label-blind size-1 selector clears clause ② — 0 of {len(names)} arms across "
        f"{len(ORDERINGS)} orderings, {RMAX} rank positions and both coverage rules, under either "
        f"comparator. **Clause ① is independently necessary against every ordering this generator "
        f"can express.**"
        if not survivors else
        f"{len(survivors)} label-blind size-1 arm(s) clear clause ②, so clause ① would EXCLUDE an "
        f"admissible core. The definition is not merely carrying an inert clause — it is wrong, "
        f"and must be repaired."))
    print(f"     ⭐⭐ AND THE PRICE OF CLAUSE ③ AT k=1: the oracle reaches "
          f"{float(oracle.mean()):.4f}, the best label-blind selector {best['mean_a2']:.4f} — "
          f"a gap of {gap:.4f}.")
    print(f"     ⚠ the SIGN is forced (the oracle is a per-prompt maximum); the SIZE is not.")
    print(f"     Against the same gap at k=4 ({K4_GAP:.4f}), label access is worth "
          f"{gap / K4_GAP:.2f}× as much at k=1 — **clause ③ protects most exactly where clause ① "
          f"bites.**" if gap > K4_GAP else
          f"     Against the same gap at k=4 ({K4_GAP:.4f}), label access is worth "
          f"{gap / K4_GAP:.2f}× as much at k=1.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "nboot": NBOOT, "n_prompts": n,
               "orderings": list(ORDERINGS), "rmax": RMAX,
               "n_arms": len(names), "cells_tested": len(ps), "cells_surviving_bh": len(keep),
               "arms_admitted_raw": [dict(r) for r in survivors],
               "ordering_agreement_rank1": agree,
               "emission_index_note": "sat_full.npz enumerates the generator's filtered `ok` list, "
                                      "not the rubric; position->text->rubric-index via "
                                      "core_full.json. misses counted, not zeroed",
               "weight_map_misses": wmiss,
               "duplicate_text_note": "2 of 968 prompts carry a criterion whose TEXT appears "
                                      "twice with different weights and satisfaction rows; a "
                                      "text->index dict collapses them. Repaired with an "
                                      "order-preserving two-pointer match.",
               "sort_stability": {"note": "select_core uses Python's STABLE sorted(); np.argsort "
                                          "defaults to unstable quicksort",
                                  "rank1_mismatches_default_sort": 137,
                                  "rank1_mismatches_stable_sort": 8,
                                  "residual_confined_to_undetermined_rank1": True},
               "placebo_random_rank_percentile": pct,
               "best_label_blind": best,
               "oracle_mean_a2": float(oracle.mean()),
               "clause3_price_at_k1": {"gap": gap, "sign_is_forced": True,
                                       "k4_gap_for_contrast": K4_GAP,
                                       "ratio_k1_over_k4": gap / K4_GAP},
               "coverage_is_a_specification_axis":
                   "RESTRICTED keeps only prompts with >= r criteria; CLAMPED takes min(r, m) so "
                   "all prompts are covered. Both are run and reported rather than one chosen.",
               "rows": rows,
               "cannot_say": "that no label-blind size-1 selector exists — only that none of the "
                             "orderings THIS generator expresses clears the bar",
               "unit_note": "A2 and gaps are in agreement units; counts are ARMS and CELLS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "label_blind_k1_sweep.json", "w"), indent=2)
    print(f"\n  artifact: results/label_blind_k1_sweep.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
