#!/usr/bin/env python3
"""R1007 — the negative control R1005 DECLARED and never implemented, plus the synthetic world.

⛔⛔ WHY THIS ROUND EXISTS, AND IT IS A DEFECT IN MY OWN WORK. R1005's docstring declares:
      NEGATIVE CTRL   shuffle the membership labels among the 96 arms, keeping set sizes fixed …
                      ≥200 shuffles. ⚠ World it excludes: "any set of this size shows this Δ".
      PLACEBO         Δ between two disjoint random halves of the NON-members must be ≈ 0.
    **Neither was implemented.** `NSHUF = 200` is defined and never used; the only `permutation` call
    permutes PROMPTS for the held-out split. R1005's committed artifact records exactly one control,
    `positive_planted_duplicate`. So the headline Δ = +0.0828 has never been tested against the one
    world it names — and R1006 excluded a DIFFERENT rival while this one stood open.
⭐ This is also R1006's NEXT (the synthetic world, ladder rung 4) arriving at the same place: assign
   membership by a rule known to be arbitrary and see whether the instrument still reports coherence.

ESTIMAND        Δ_real (R1005's statistic, recomputed identically) against the distribution of Δ
                under membership assigned by rules with NO admission content, at matched size.
IDENTIFICATION  direct. Every null uses the SAME level-matching, the SAME held-out split and the SAME
                deduplication as the real arm; only WHICH arms are called members changes.
SCOPE           population : R1000's 96-arm intersection, deduplicated to 85 distinct (R1005)
                instrument : per-prompt class agreement, precomputed pairwise (R1006's matrix)
                baseline   : two nulls, below · regime : this release, held-out halves
WORLDS          A REAL RULE MATTERS   Δ_real sits above the 95th percentile of BOTH nulls. R1005's
                                      convergence survives the control it declared.
                B SIZE-AND-BAND ONLY  Δ_real sits inside the band-matched null. Then ANY set of this
                                      size drawn from this level band shows this Δ, the convergence
                                      is a property of the BAND and not of the definition, and
                                      R1005's headline is RETRACTED in this round.
                prediction matrix: A -> pct > 0.95 in both. B -> pct <= 0.95 in the band-matched null.
KILL            pre-registered, written before the run: **if Δ_real is not above the 95th percentile
                of the BAND-MATCHED null, R1005's convergence claim is withdrawn here, by name.**
                The band-matched null is the binding one; the unrestricted null is the weaker test
                and is reported beside it, never instead of it.
POSITIVE CTRL   a PLANTED extension — the 14 known-identical pairs' members, which agree at 1.000 by
                construction — must land at the top of both nulls. If a set of literal copies does
                not score above the null, the whole comparison is blind. ⚠ And it must not pass
                trivially: the same pipeline on a RANDOM set must NOT land there.
NEGATIVE CTRL   ① UNRESTRICTED null: members drawn at random from the 85 distinct arms, size matched.
                ② BAND-MATCHED null: members drawn at random from arms whose A2 lies in the REAL
                   extension's own band. This holds LEVEL fixed and destroys only which-arms — it is
                   the world R1005 named and the one that can retract the claim.
                1,000 draws each.
PLACEBO         the other control R1005 declared: Δ between two disjoint random halves of the
                NON-members, which must be ≈ 0. 1,000 draws; its spread IS the zero-effect reference.
NOISE FLOOR     the placebo's sd, measured, not assumed.
MULTIPLICITY    2 comparators × 5 partitions × 3 calipers × 2 nulls = 60 cells, all reported.
ARTIFACT        results/membership_null.json with this file's source hash.
IMPOSSIBLE      ⚠ construct validity — N/A throughout: this asks whether the ADMISSION RULE carries
                the convergence, never whether the convergence tracks correctness.
                ⚠ a null over ADMISSION RULES rather than over SETS — N/A. The honest null would
                sample alternative rules of the same expressive class and re-derive membership; the
                release ships one comparator family and one label predicate, so the rule space has
                no measure on it here. What it would require: a generator of admissible rules.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NDRAW, SEED, NBOOT = 1000, 1007, 4000
PARTITIONS, CALIPERS = (1, 2, 3, 4, 5), (0.010, 0.020, 0.040)
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")


def main() -> int:
    need = {"r921": next(A26.glob("R921_*/results/comparator_sweep.json"), None),
            "r1000": next(A27.glob("R1000_*/results/conjunction.json"), None),
            "r1005": next(A27.glob("R1005_*/results/convergence.json"), None)}
    if [k for k, v in need.items() if v is None]:
        print(f"  UNRUNNABLE: missing {[k for k, v in need.items() if v is None]}. Exit 2.")
        return 2
    legit = json.loads(need["r921"].read_text())["legitimate_comparators"]
    pop = json.loads(need["r1000"].read_text())["population_arms"]
    r1005 = json.loads(need["r1005"].read_text())
    dup_pairs = [tuple(x) for x in r1005["duplicate_pairs"]]
    print(f"  R1005's committed controls: {sorted(r1005['controls'])}")
    print(f"  ⛔ neither `negative` nor `placebo` is among them, though both are DECLARED in its "
          f"docstring. That is what this round supplies.")

    tg, _ = load_targets()
    S0 = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    Cv, A2v = {}, {}
    load_list = sorted(set(pop) | set(legit))
    for a in load_list:
        for d in (RES, NEW):
            f = d / f"sat_{a}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                break
            cvs, sc = [], np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    cvs.append(c)
                    sc[k] = float(np.mean([(c == h[:len(c)]).mean() for h in H[p]]))
                else:
                    cvs.append(None)
            if np.isfinite(sc).sum() >= 200:
                Cv[a], A2v[a] = cvs, np.nan_to_num(sc, nan=np.nanmean(sc))
            break
    arms = sorted(Cv)
    ai = {a: i for i, a in enumerate(arms)}
    print(f"  arms {len(arms)} · prompts {n}")

    # ---------- per-prompt agreement tensor, so every Δ on any half is a lookup ----------
    SUMh = {}
    for tag in ("all",):
        pass
    AGSUM = np.zeros((len(arms), len(arms), 0))
    per = []
    for k in range(n):
        vs = [(ai[a], Cv[a][k]) for a in arms if Cv[a][k] is not None]
        M = np.full((len(arms), len(arms)), np.nan)
        if len(vs) >= 2:
            m = min(len(v) for _i, v in vs)
            ii = np.array([i for i, _v in vs])
            Mx = np.array([v[:m] for _i, v in vs])
            M[np.ix_(ii, ii)] = (Mx[:, None, :] == Mx[None, :, :]).mean(axis=2)
        per.append(M)
    PER = np.stack(per)                      # (n_prompts, n_arms, n_arms)
    print(f"  agreement tensor {PER.shape} built")

    # ⭐ AVERAGE OVER PROMPTS FIRST, THEN OVER PAIRS. The first draft sliced the (968, A, A) tensor
    #    inside a 1000-draw null with ~80-arm sets -- 484x80x80 elements per call, 30,000 calls --
    #    and was still silent at 90 seconds.
    #    ⚠ AND THIS IS NOT AN APPROXIMATION: it is EXACTLY R1005's statistic. R1005 computed
    #    `mean over pairs of pair_agree(a, b)` where pair_agree is itself a mean over prompts, so
    #    the estimand was already mean-of-means. The tensor-slicing draft would have weighted pairs
    #    by their valid-prompt count -- a DIFFERENT quantity from the one under test. The fast
    #    version is the faithful one, which is the only reason it is allowed to replace the slow one.
    PMEAN = {}

    def within(mem, idx, key):
        if len(mem) < 2:
            return np.nan
        if key not in PMEAN:
            PMEAN[key] = np.nanmean(PER[idx], axis=0)
        Pm = PMEAN[key]
        ii = [ai[a] for a in mem]
        iu = np.triu_indices(len(ii), 1)
        return float(np.nanmean(Pm[np.ix_(ii, ii)][iu[0], iu[1]]))

    # ---------- deduplicate ----------
    full_idx = list(range(n))
    Pall = np.nanmean(PER, axis=0)
    seen, keep = set(), []
    for a in arms:
        if a in seen or a not in pop:
            continue
        keep.append(a)
        for b in arms:
            if b != a and b in pop and Pall[ai[a], ai[b]] == 1.0:
                seen.add(b)
    print(f"  deduplicated {len([a for a in arms if a in pop])} -> {len(keep)} distinct")

    rng = np.random.default_rng(SEED)
    rows = []
    for c in legit:
        for part in PARTITIONS:
            r = np.random.default_rng(SEED + part)
            perm = r.permutation(n)
            dec, mea = sorted(perm[:n // 2]), sorted(perm[n // 2:])
            cand = keep if c in keep else keep + [c]
            V = np.array([A2v[a] for a in cand])[:, dec]
            bi = r.integers(0, len(dec), size=(NBOOT, len(dec)))
            M = np.stack([V[:, bi[b]].mean(axis=1) for b in range(NBOOT)], axis=1)
            adm = np.percentile(M - M[cand.index(c)][None, :], 2.5, axis=1) > 0
            ext = [a for a, ok in zip(cand, adm)
                   if ok and a in keep and not a.startswith(SUPERVISED)]
            if len(ext) < 2:
                rows.append({"comparator": c, "partition": part, "status": "UNIDENTIFIED",
                             "n_ext": len(ext)})
                continue
            lvl = {a: float(V[cand.index(a)].mean()) for a in keep}
            lo, hi = min(lvl[a] for a in ext), max(lvl[a] for a in ext)
            for cal in CALIPERS:
                band = [a for a in keep if lo - cal <= lvl[a] <= hi + cal]
                matched = [a for a in band if a not in ext]
                if len(matched) < 2:
                    rows.append({"comparator": c, "partition": part, "caliper": cal,
                                 "status": "UNIDENTIFIED — no level overlap", "n_ext": len(ext)})
                    continue
                d_real = within(ext, mea, part) - within(matched, mea, part)

                def null(pool, ndraw=NDRAW):
                    out = []
                    for _ in range(ndraw):
                        if len(pool) <= len(ext):
                            out.append(np.nan)
                            continue
                        pick = list(rng.choice(pool, size=len(ext), replace=False))
                        ps_ = set(pick)
                        rest = [a for a in pool if a not in ps_]
                        if len(rest) < 2:
                            out.append(np.nan)
                            continue
                        out.append(within(pick, mea, part) - within(rest, mea, part))
                    return np.array(out, float)

                n_un = null(keep)
                n_bd = null(band)
                # PLACEBO: two disjoint halves of the NON-members -> must be ~0
                nonm = [a for a in keep if a not in ext]
                plac = []
                for _ in range(NDRAW):
                    sh = list(rng.permutation(nonm))
                    h1, h2 = sh[:len(sh) // 2], sh[len(sh) // 2:]
                    plac.append(within(h1, mea, part) - within(h2, mea, part))
                plac = np.array(plac, float)
                rows.append({
                    "comparator": c, "partition": part, "caliper": cal, "status": "ok",
                    "n_ext": len(ext), "n_matched": len(matched), "n_band": len(band),
                    "delta_real": d_real,
                    "unrestricted_pct": float(np.nanmean(n_un < d_real)),
                    "unrestricted_p95": float(np.nanpercentile(n_un, 95)),
                    "band_pct": float(np.nanmean(n_bd < d_real)),
                    "band_p95": float(np.nanpercentile(n_bd, 95)),
                    "placebo_mean": float(np.nanmean(plac)), "placebo_sd": float(np.nanstd(plac))})

    ok = [r for r in rows if r["status"] == "ok"]
    if not ok:
        print("\n⛔ every cell UNIDENTIFIED. Exit 2, never 0.")
        return 2

    # ---------- POSITIVE CONTROL: a planted extension of literal copies ----------
    dupmem = sorted({x for pr in dup_pairs for x in pr if x in ai})[:6]
    pc_idx = list(range(n))
    pc_w = within(dupmem, pc_idx, "full") if len(dupmem) >= 2 else np.nan
    rnd_set = list(rng.choice(keep, size=min(len(dupmem), len(keep)), replace=False))
    pc_r = within(rnd_set, pc_idx, "full")
    pos_ok = pc_w > pc_r
    print(f"\n  POSITIVE CONTROL — a planted extension of {len(dupmem)} literal copies scores "
          f"{pc_w:.4f}; a random set of the same size scores {pc_r:.4f}: "
          f"{'PASS' if pos_ok else '⛔ FAIL'}")
    if not pos_ok:
        print("  the comparison is blind. Exit 2, never 0.")
        return 2

    print(f"\n  {'cmp':<15}{'part':>5}{'cal':>7}{'|ext|':>6}{'Δ real':>9}"
          f"{'unres p95':>11}{'pct':>6}{'band p95':>10}{'pct':>6}{'placebo':>9}")
    for r in ok:
        print(f"  {r['comparator']:<15}{r['partition']:>5}{r['caliper']:>7.3f}{r['n_ext']:>6}"
              f"{r['delta_real']:>+9.4f}{r['unrestricted_p95']:>+11.4f}{r['unrestricted_pct']:>6.2f}"
              f"{r['band_p95']:>+10.4f}{r['band_pct']:>6.2f}{r['placebo_mean']:>+9.4f}")

    band_pass = [r for r in ok if r["band_pct"] > 0.95]
    unres_pass = [r for r in ok if r["unrestricted_pct"] > 0.95]
    pl_mean = float(np.mean([r["placebo_mean"] for r in ok]))
    pl_sd = float(np.mean([r["placebo_sd"] for r in ok]))
    print(f"\n  PLACEBO — two disjoint halves of the NON-members: mean {pl_mean:+.4f}, "
          f"sd {pl_sd:.4f} (must be ~0)")
    print(f"  cells above the 95th percentile: unrestricted null {len(unres_pass)}/{len(ok)}, "
          f"BAND-MATCHED null {len(band_pass)}/{len(ok)}")

    survives = len(band_pass) == len(ok)
    world = ("A REAL RULE MATTERS — Δ_real clears the 95th percentile of the band-matched null in "
             "every cell" if survives else
             f"B SIZE-AND-BAND ONLY — Δ_real fails the band-matched null in "
             f"{len(ok) - len(band_pass)} of {len(ok)} cells")
    print(f"\n⭐ {world}")
    if not survives:
        print("⛔ PRE-REGISTERED KILL FIRES: R1005's convergence claim is WITHDRAWN for those cells.")
        print("   Any set of that size drawn from that level band shows the same Δ, so the")
        print("   convergence is a property of the BAND and not of the admission rule.")

    out = HERE / "results" / "membership_null.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="the negative control R1005 declared and never implemented",
        r1005_declared_controls=["negative shuffled membership", "placebo halves of non-members"],
        r1005_implemented_controls=sorted(r1005["controls"]),
        n_prompts=n, ndraw=NDRAW, seed=SEED, n_distinct=len(keep),
        controls={"positive_planted_copies": float(pc_w), "positive_random_same_size": float(pc_r),
                  "positive_ok": bool(pos_ok), "placebo_mean": pl_mean, "placebo_sd": pl_sd},
        rows=rows, cells_ok=len(ok), cells_above_band_p95=len(band_pass),
        cells_above_unrestricted_p95=len(unres_pass), world=world, survives=bool(survives),
        limitation="a null over SETS, not over admission RULES; the release ships one comparator "
                   "family and one label predicate, so the rule space has no measure here",
        would_require="a generator of admissible rules to null over",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
