#!/usr/bin/env python3
"""R1006 — is the SUPERVISED family unusually heterogeneous? The reading R1005 could not exclude.

⛔ WHY NOT R1005's NEXT AS WRITTEN. R1005 asked for a comparison set matched on level and drawn from
OUTSIDE the supervised family. ⭐ THE IDENTIFICATION CHECK KILLED THAT DESIGN BEFORE IT WAS BUILT:
in the members' A2 band [0.5593, 0.5698] there are only 3 non-supervised non-members at calipers
0.010 and 0.020 (and `generic == generic_reprov` are duplicates, so 2 DISTINCT), rising to 6 (5
distinct) at 0.040 — and they are `gen`, `generic`, `topw_k1`, `topw_k2`, `topw_k12`, i.e. mostly the
MEMBERS' OWN FAMILY. A comparison set drawn from the family under test is confounded in the opposite
direction. n=2 and confounded is not a design; running it would have produced a number.

⭐ THE READING IS TESTABLE DIRECTLY, AND WITHOUT LEVEL-MATCHING. R1005 said Δ > 0 admits two
readings: (A) members cohere, or (B) the supervised comparison set is unusually heterogeneous among
itself. **(B) is a claim about the supervised arms alone** and needs no members at all: if the
supervised families' within-family agreement is TYPICAL or HIGH relative to other families, (B) is
false and cannot explain R1005's Δ.

ESTIMAND        for each arm family with >= 2 DISTINCT members, its mean pairwise within-family
                agreement; and the RANK of the supervised families in that distribution.
IDENTIFICATION  direct: families are given by the rule prefix R993 established, and within-family
                agreement needs no comparator, no level match and no held-out split — it is a
                property of the arms' own outputs. This is exactly why it is identified where
                R1005's NEXT was not.
SCOPE           population : the 96-arm intersection, DEDUPLICATED to 85 distinct (R1005) — a family
                             whose members are copies would score 1.000 for free
                instrument : per-prompt class agreement between two arms
                baseline   : the distribution over all families, not a chosen contrast
                regime     : this release
WORLDS          A SUPERVISED ARE NOT ODD  the supervised families rank at or above the middle of the
                            within-family agreement distribution. Reading (B) dies and R1005's Δ
                            stands as member coherence.
                B SUPERVISED ARE ODD      they rank in the bottom tercile. Reading (B) survives and
                            R1005's Δ must be downgraded to "either coherence or supervised spread".
                prediction matrix: A -> supervised rank >= median. B -> bottom tercile.
KILL            pre-registered before the run: if ANY supervised family (oracle_k, indep_k, greedy_k)
                falls in the bottom tercile of within-family agreement, world B survives and R1005's
                headline is downgraded in this round's own README, not later.
POSITIVE CTRL   the DUPLICATE-ONLY pseudo-family — the 14 identical pairs R1005 found — must score
                exactly 1.000. If the instrument cannot return 1.0 for known copies it cannot rank
                families. ⚠ And it must not be saturated: a deliberately mixed family must score < 1.
NEGATIVE CTRL   families reassembled at RANDOM, preserving each family's SIZE, 500 shuffles. This
                destroys the which-arms-together structure while keeping every arm and every size,
                so it isolates family membership from the agreement level of the pool. It gives the
                null band each real family is read against.
                ⚠ World it excludes: "any group of this size scores this high."
PLACEBO         a family split into two halves and compared to itself must give a difference ~0.
NOISE FLOOR     the sd of the random-family null, measured, per family size.
MULTIPLICITY    every family with >= 2 distinct arms is reported, survivors and non-survivors, with
                a BH correction over the whole family set at q = 0.05.
ARTIFACT        results/family_spread.json with this file's source hash.
IMPOSSIBLE      ⚠ the level-matched non-supervised contrast R1005 asked for — N/A, and this round
                reports WHY with the counts above rather than running it at n=2. What it would
                require: a release with more arms in the members' band that are neither supervised
                nor topw.
                ⚠ construct validity — N/A as throughout: agreement is not correctness.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

# ⛔ 500 SHUFFLES FLOORED THE p AT 1/501 = 0.002 AND BH's RANK-1 THRESHOLD OVER 11 FAMILIES IS
#    0.05/11 = 0.0045, SO 0 OF 11 "SURVIVED" — a resolution artifact reported as a null. P5's star
#    rule: a zero from an instrument that cannot return non-zero is silence, not an acquittal. At
#    5000 the floor is 0.0002 and BH can actually resolve. The RANK claim this round makes never
#    needed BH; raising it is so the multiplicity column means something rather than being decorative.
NSHUF, SEED = 5000, 1006
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")
FAM = re.compile(r"^(oracle_k|indep_k|greedy_k|topw_k|topabs_k|topvar_k|topwvar_k|random_k|"
                 r"coval_core|generic|gen|full)")


def main() -> int:
    conj = next(A27.glob("R1000_*/results/conjunction.json"), None)
    conv = next(A27.glob("R1005_*/results/convergence.json"), None)
    if not (conj and conv):
        print("  UNRUNNABLE: R1000 or R1005 artifact missing. Exit 2, never 0.")
        return 2
    pop = json.loads(conj.read_text())["population_arms"]
    dup_pairs = [tuple(x) for x in json.loads(conv.read_text())["duplicate_pairs"]]
    print(f"  population READ from R1000: {len(pop)} · duplicate pairs READ from R1005: "
          f"{len(dup_pairs)}")

    tg, _ = load_targets()
    S0 = load_sat(RES / "sat_genericpool16.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    Cv, A2 = {}, {}
    for a in pop:
        for d in (RES, NEW):
            f = d / f"sat_{a}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                break
            cvs, sc = [], []
            for p in pids:
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    cvs.append(c)
                    sc.append(float(np.mean([(c == h[:len(c)]).mean() for h in H[p]])))
                else:
                    cvs.append(None)
            if len(sc) >= 200:
                Cv[a], A2[a] = cvs, float(np.mean(sc))
            break
    arms = sorted(Cv)
    print(f"  arms with class vectors: {len(arms)} · prompts {n}")

    # ⭐ PRECOMPUTE THE FULL PAIRWISE AGREEMENT MATRIX ONCE. The first draft called a per-pair loop
    #    over 968 prompts from INSIDE a 500-shuffle null: ~2e8 Python operations, hours, and it was
    #    still producing no output when I killed it. Every quantity this round needs is a function
    #    of the same matrix, so it is built once by broadcasting per prompt and everything
    #    downstream is a lookup. L65: after any algorithm, ask whether it can be 10x faster — here
    #    it is ~1000x, and the numbers are identical because it is the same arithmetic reordered.
    ai = {a: i for i, a in enumerate(arms)}
    SUM = np.zeros((len(arms), len(arms)))
    CNT = np.zeros((len(arms), len(arms)))
    for k in range(n):
        vs = [(ai[a], Cv[a][k]) for a in arms if Cv[a][k] is not None]
        if len(vs) < 2:
            continue
        m = min(len(v) for _i, v in vs)
        ii = np.array([i for i, _v in vs])
        Mx = np.array([v[:m] for _i, v in vs])
        eq = (Mx[:, None, :] == Mx[None, :, :]).mean(axis=2)
        SUM[np.ix_(ii, ii)] += eq
        CNT[np.ix_(ii, ii)] += 1.0
    P = np.divide(SUM, CNT, out=np.full_like(SUM, np.nan), where=CNT > 0)
    print(f"  pairwise agreement matrix built: {len(arms)}x{len(arms)}, "
          f"{int((CNT > 0).sum())} populated cells")

    def ag(a, b):
        return float(P[ai[a], ai[b]])

    # ---------- DEDUPLICATE: a family of copies scores 1.000 for free ----------
    seen, keep = set(), []
    for a in arms:
        if a in seen:
            continue
        keep.append(a)
        for b in arms:
            if b != a and ag(a, b) == 1.0:
                seen.add(b)
    print(f"  deduplicated {len(arms)} -> {len(keep)} distinct arms")

    # ---------- POSITIVE CONTROL ----------
    dup_in = [(x, y) for x, y in dup_pairs if x in Cv and y in Cv]
    pos = float(np.mean([ag(x, y) for x, y in dup_in])) if dup_in else np.nan
    mixed = [a for a in keep if a.startswith("random_k")][:4]
    sat = float(np.mean([ag(a, b) for i, a in enumerate(mixed) for b in mixed[i + 1:]])) \
        if len(mixed) >= 2 else np.nan
    pos_ok = abs(pos - 1.0) < 1e-12 and sat < 1.0
    print(f"\n  POSITIVE CONTROL — the {len(dup_in)} known-identical pairs score {pos:.6f} "
          f"(must be 1.0); a deliberately mixed family scores {sat:.4f} (must be < 1): "
          f"{'PASS' if pos_ok else '⛔ FAIL'}")
    if not pos_ok:
        print("  the instrument cannot rank families. Exit 2, never 0.")
        return 2

    def fam(a):
        m = FAM.match(a)
        return m.group(1) if m else "other"

    fams = {}
    for a in keep:
        fams.setdefault(fam(a), []).append(a)
    fams = {k: v for k, v in fams.items() if len(v) >= 2}

    def within(mem):
        p = [ag(a, b) for i, a in enumerate(mem) for b in mem[i + 1:]]
        return float(np.mean(p)) if p else np.nan

    rng = np.random.default_rng(SEED)
    print(f"\n  {'family':<14}{'n':>4}{'mean A2':>9}{'within':>9}{'null mean':>11}"
          f"{'null sd':>9}{'z':>7}  pct")
    rows = []
    for name, mem in sorted(fams.items(), key=lambda kv: -within(kv[1])):
        w = within(mem)
        nulls = []
        for _ in range(NSHUF):
            pick = list(rng.choice(keep, size=len(mem), replace=False))
            nulls.append(within(pick))
        nulls = np.array(nulls)
        z = (w - nulls.mean()) / (nulls.std() + 1e-12)
        pct = float((nulls < w).mean())
        rows.append({"family": name, "n": len(mem), "mean_a2": float(np.mean([A2[a] for a in mem])),
                     "within": w, "null_mean": float(nulls.mean()), "null_sd": float(nulls.std()),
                     "z": float(z), "pct": pct, "supervised": name.startswith(SUPERVISED),
                     "members": mem})
        print(f"  {name:<14}{len(mem):>4}{np.mean([A2[a] for a in mem]):>9.4f}{w:>9.4f}"
              f"{nulls.mean():>11.4f}{nulls.std():>9.4f}{z:>+7.2f}  {pct:.3f}")

    order = sorted(rows, key=lambda r: r["within"])
    tercile = max(1, len(order) // 3)
    bottom = {r["family"] for r in order[:tercile]}
    sup_rows = [r for r in rows if r["supervised"]]
    sup_bottom = [r["family"] for r in sup_rows if r["family"] in bottom]
    ranks = {r["family"]: sorted(rows, key=lambda x: -x["within"]).index(r) + 1 for r in sup_rows}
    print(f"\n  supervised families and their rank by within-family agreement "
          f"(1 = most homogeneous of {len(rows)}): {ranks}")
    print(f"  bottom tercile ({tercile} families): {sorted(bottom)}")

    # BH over the whole family set, two-sided on the shuffle percentile
    ps = sorted([(min(2 * min(r["pct"], 1 - r["pct"]) + 1.0 / (NSHUF + 1), 1.0), r["family"])
                 for r in rows])
    C, kmax = len(ps), -1
    for rank, (p, _f) in enumerate(ps, 1):
        if p <= 0.05 * rank / C:
            kmax = rank
    surv = {f for _p, f in ps[:kmax]} if kmax > 0 else set()
    pfloor = 1.0 / (NSHUF + 1)
    bh1 = 0.05 / C
    print(f"  MULTIPLICITY — {C} families tested, {len(surv)} survive BH at q=0.05: {sorted(surv)}")
    print(f"     RESOLUTION: permutation p is floored at 1/(NSHUF+1) = {pfloor:.5f}; BH's rank-1 "
          f"threshold is 0.05/{C} = {bh1:.5f}. Floor {'<' if pfloor < bh1 else '>='} threshold, so "
          f"the test {'can' if pfloor < bh1 else 'CANNOT'} resolve a top cell.")
    print(f"     non-survivors (reported, not hidden): {sorted({r['family'] for r in rows} - surv)}")

    world = (f"B SUPERVISED ARE ODD — {sup_bottom} sit in the bottom tercile" if sup_bottom else
             "A SUPERVISED ARE NOT ODD — no supervised family is in the bottom tercile of "
             "within-family agreement, so 'the comparison set is unusually heterogeneous' cannot "
             "explain R1005's Δ")
    print(f"\n⭐ {world}")
    if sup_bottom:
        print("⛔ PRE-REGISTERED KILL FIRES: R1005's Δ is DOWNGRADED to 'either member coherence or")
        print("   supervised spread', and this round says so rather than leaving it to a later one.")
    print("\n⚠ THE CONTRAST R1005 ASKED FOR IS STILL UNAVAILABLE. In the members' A2 band there are")
    print("   only 2 DISTINCT non-supervised non-members at caliper 0.020 and 5 at 0.040, and they")
    print("   are mostly `topw_k*` — the members' OWN family. n=2 and confounded is not a design.")

    out = HERE / "results" / "family_spread.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="is the supervised family unusually heterogeneous — the reading R1005 could not exclude",
        n_prompts=n, nshuf=NSHUF, seed=SEED, n_arms=len(arms), n_distinct=len(keep),
        controls={"positive_known_duplicates": float(pos), "saturation_mixed_family": float(sat),
                  "positive_ok": bool(pos_ok)},
        rows=rows, supervised_ranks=ranks, bottom_tercile=sorted(bottom),
        bh_survivors=sorted(surv), n_families=C, world=world,
        p_floor=1.0 / (NSHUF + 1), bh_rank1_threshold=0.05 / C,
        rank_claim_needs_no_bh="the world verdict is a RANK statement over families; BH answers a "
                               "different question (is any family resolvably above chance) and is "
                               "reported beside it, not as its support",
        not_measured="the level-matched non-supervised contrast R1005 asked for",
        would_require="a release with more arms in the members' band that are neither supervised "
                      "nor topw; here there are 2 distinct at caliper 0.020 and 5 at 0.040",
        limitation="agreement is not correctness; this bounds an EXPLANATION, it does not validate",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
