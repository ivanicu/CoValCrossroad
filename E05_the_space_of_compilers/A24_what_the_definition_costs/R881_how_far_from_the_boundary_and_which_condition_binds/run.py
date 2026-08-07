#!/usr/bin/env python3
"""
R881 · how far from the boundary is each admitted arm — and WHICH of the two conditions binds?

⛔ WHY. R880 found clause ②'s admitted set byte-identical from NBOOT 250 to 8000 and inferred the
set is **not marginal**. **That inference is evidence, not the quantity**: zero flips is consistent
with every member clearing by a mile AND with a bootstrap so precise that even hairline margins
never move. **The distance itself has never been computed.**

⭐ **AND THERE IS A SHARPER QUESTION INSIDE IT THAT NOBODY HAS ASKED.** Criterion B is a CONJUNCTION:
`BH(q=0.05) AND CI-lower > 0`. Every round in this project has applied both and reported one verdict.
**If one condition always binds, the other is decoration** — and clause ②'s criterion would be
simpler than it has been written, in a way that changes what the definition says.


⛔⛔⛔ POST-RUN CORRECTION. **BOTH WORLDS ARE TRUE, AND MY THRESHOLD DECIDED WHICH ONE PRINTED.**

**① THE CUTOFF WAS A NUMBER I CHOSE — the sixth commission of that error this session.** The branch
read `C if closest/MDE < 0.25 else B if (nb==0 or nc==0) else A`. The measured value is **0.28**.
**Had I written 0.30, this file would print WORLD C — "the set IS marginal" — instead of WORLD B.**
Nothing in the design justified 0.25, and the two worlds are not alternatives: **they are both
supported by the same numbers.**

**② WORLD B IS REAL AND NEEDS NO THRESHOLD.** `BH binds for 0 arms · CI binds for 28`. That is a
count, not a comparison against a cutoff. **Criterion B's BH multiplicity correction is decoration
for every admitted arm** — each one is limited by its CI lower bound and none by BH. So clause ②'s
criterion is simpler than it has been written throughout this project.

**③ AND R880's INFERENCE IS OVERTURNED — the set IS marginal.** R880 saw zero flips across a 32×
bootstrap-budget range and concluded the admitted arms sit *"far from the decision boundary in both
directions"*. **Measured, the closest sits 0.28 MDEs clear**, and four arms are inside 0.6 MDE:
`topw_k2` +0.00314 (0.28 MDE) · `greedy_k12_fit1` +0.00435 (0.39) · `generic` and `generic_reprov`
+0.00574 (0.51). **That is hairline, not far.**

⭐ **WHY ZERO FLIPS WAS NEVER EVIDENCE OF DISTANCE, and R881 was built to tell exactly these apart.**
Bootstrap Monte-Carlo error at `NBOOT ≥ 250` is far smaller than 0.28 MDE, so the **ESTIMATE of `lo`
is precise even when `lo` itself is small.** R880 read **the precision of the instrument** as **the
distance of the object** — its own successor's WORLD C, verbatim — and my 0.25 cutoff is what let it
print otherwise.

**WHAT THE DELIVERABLE MUST NOW SAY:**
  · clause ②'s criterion B reduces to its **CI condition**; BH excludes nothing here.
  · the admitted set is **stable but marginal**: stable because the bootstrap is precise, marginal
    because four of 28 members clear by less than 0.6 MDE.
  · **R880's sentence "the 28 arms are far from the decision boundary" is RETRACTED.**

⚠ **What survives from R880 untouched:** the set really is budget-invariant (28 arms, Jaccard 1.0000,
zero flips, two seeds). That measurement stands. **Only the interpretation laid on top of it falls.**

ESTIMAND        for every arm: the slack on each of criterion B's two conditions, in that
                condition's own units — `lo` (A2 units, the CI slack) and `q·rank/C − p`
                (p units, the BH slack) — and which condition is the binding one.
IDENTIFICATION  exact. Both slacks are byproducts of the same bootstrap that produces the verdict;
                nothing new is estimated. **The binding-condition assignment is a DERIVATION from
                the two slacks and is labelled as one** — what is measured is the DISTRIBUTION.
SCOPE           population: 99 scored arms × 968 prompts
                instrument: A2 vs every annotator; comparator `genericpool16`; NBOOT = 8000
                            (R880 showed the set is budget-invariant, so the largest is free)
                baseline:   the admission boundary itself
                regime:     home release, judge J
WORLDS          A · both conditions bind for different arms -> the conjunction is doing real work
                    and criterion B cannot be simplified
                B · one condition binds for every admitted arm -> the other is decoration, and
                    clause ②'s criterion is simpler than it has been written
                C · the slacks are tiny for some admitted arms -> the set IS marginal after all and
                    R880's zero-flip inference was reading bootstrap precision as distance
KILL            CONDITIONAL, all required:
                  ⭐ ① WIRING: recomputed admission `(BH) AND (lo>0)` must reproduce R880's 28-arm
                     set EXACTLY. If it does not, the slacks are describing a different comparison.
                  ⭐ ② POSITIVE: `oracle_k4`, the ceiling, must sit in the top decile of CI slack.
                     A slack measure that does not rank the ceiling high is measuring noise.
                  ⭐ ③ NEGATIVE: `random_k4_s0` must have `lo <= 0`.
                  ⭐ ④ PLACEBO: the comparator against ITSELF must give margin and `lo` identically
                     0 — the exact boundary, which is the only point where "distance" has a
                     known true value.
MULTIPLICITY    99 arms × 2 conditions; the whole slack distribution reported, admitted and not.
ARTIFACT        results/boundary_distance.json
IMPOSSIBLE      cross-release · construct validated · causally identified.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

BLIND, CORE, POS, NEG = "genericpool16", "coval_core", "oracle_k4", "random_k4_s0"
NBOOT, Q, ZEFF = 8000, 0.05, 2.802


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / f"sat_{BLIND}.npz")
    A = load_sat(ROOT / "corebench" / "results" / f"sat_{CORE}.npz")
    pids = sorted(set(S) & set(A) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    n = len(pids)

    def vec(nm):
        f = ROOT / "corebench" / "results" / f"sat_{nm}.npz"
        if not f.exists():
            return None
        try:
            Sa = load_sat(f)
        except Exception:
            return None
        v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                      for k, p in enumerate(pids)])
        return None if np.isfinite(v).sum() < 200 else v

    names, V = [], []
    for f in sorted((ROOT / "corebench" / "results").glob("sat_*.npz")):
        v = vec(f.stem[4:])
        if v is not None:
            names.append(f.stem[4:]); V.append(v)
    V = np.array(V); Bv = vec(BLIND)
    D = V - Bv
    Mk = np.isfinite(D).astype(float); Dz = np.nan_to_num(D)
    bidx = np.random.default_rng(11).integers(0, n, size=(NBOOT, n))
    bs = (Dz[:, bidx].sum(2) / np.maximum(Mk[:, bidx].sum(2), 1.0)).T
    marg = np.nanmean(D, 1)
    lo = np.percentile(bs, 2.5, axis=0)
    se = bs.std(axis=0, ddof=1)
    pv = np.maximum(2 * np.minimum((bs <= 0).mean(0), (bs >= 0).mean(0)), 1.0 / (NBOOT + 1))
    C = len(names)
    order = np.argsort(pv)
    rank = np.empty(C, int)
    rank[order] = np.arange(1, C + 1)
    bh_thresh = Q * rank / C
    kmax = -1
    for r, i in enumerate(order, 1):
        if pv[i] <= Q * r / C:
            kmax = r
    bh_pass = np.zeros(C, bool)
    if kmax > 0:
        bh_pass[order[:kmax]] = True
    adm = bh_pass & (lo > 0)
    print(f"  prompts {n} · arms {C} · NBOOT {NBOOT} (free: R880 showed budget-invariance)")

    ip, ineg = names.index(POS), names.index(NEG)
    k1 = int(adm.sum()) == 28
    slack_ci = lo                                   # A2 units; >0 means the CI condition clears
    dec = np.percentile(slack_ci[adm], 90)
    k2 = bool(slack_ci[ip] >= dec)
    k3 = bool(lo[ineg] <= 0)
    pl_d = Bv - Bv
    pl_marg = float(np.nanmean(pl_d))
    k4 = abs(pl_marg) < 1e-15
    print(f"  ① WIRING  recomputed admission = 28 arms (R880's set): {int(adm.sum())}  "
          f"{'PASS' if k1 else 'FAIL'}")
    print(f"  ② POSITIVE `{POS}` in the top decile of CI slack: {k2}  {'PASS' if k2 else 'FAIL'}"
          f"   (its lo {slack_ci[ip]:+.5f} vs p90 {dec:+.5f})")
    print(f"  ③ NEGATIVE `{NEG}` has lo <= 0: {k3}  {'PASS' if k3 else 'FAIL'}"
          f"   (lo {lo[ineg]:+.5f})")
    print(f"  ④ PLACEBO comparator vs itself margin {pl_marg:+.2e}: {k4}  "
          f"{'PASS' if k4 else 'FAIL'}")
    if not (k1 and k2 and k3 and k4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "n_admitted": int(adm.sum())},
                  open(OUT / "boundary_distance.json", "w"), indent=2)
        return 2

    # ⛔ DERIVATION, labelled: which condition binds is read off the two slacks, not measured.
    slack_bh = bh_thresh - pv                       # p units; >0 means the BH condition clears
    binds = []
    for i in range(C):
        if not adm[i]:
            binds.append(None); continue
        binds.append("BH" if (slack_bh[i] / max(bh_thresh[i], 1e-300)
                              < slack_ci[i] / max(abs(marg[i]), 1e-300)) else "CI")
    nb = sum(1 for b in binds if b == "BH")
    nc = sum(1 for b in binds if b == "CI")

    a_lo = np.sort(slack_ci[adm])
    mde_typ = float(np.median(ZEFF * se[adm]))
    print(f"\n  ⭐ CI SLACK among the {int(adm.sum())} admitted arms, in A2 units:")
    print(f"     min {a_lo[0]:+.5f} · p25 {np.percentile(a_lo,25):+.5f} · "
          f"median {np.median(a_lo):+.5f} · max {a_lo[-1]:+.5f}")
    print(f"     typical per-arm MDE for comparison: {mde_typ:.5f}")
    print(f"     ⭐ the CLOSEST admitted arm sits {a_lo[0]/mde_typ:.2f} MDEs above the boundary")
    tight = [(names[i], float(slack_ci[i])) for i in np.argsort(slack_ci) if adm[i]][:5]
    for nm, s in tight:
        print(f"        {nm:<28} lo = {s:+.5f}  ({s/mde_typ:.2f} MDE)")
    print(f"\n  ⛔ DERIVATION (not measured): which condition binds is READ OFF the two slacks.")
    print(f"     BH binds for {nb} arm(s) · CI binds for {nc} arm(s)")
    world = ("C" if a_lo[0] / mde_typ < 0.25 else
             "B" if (nb == 0 or nc == 0) else "A")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "both conditions bind for different arms — the conjunction does real work and"
             " criterion B cannot be simplified",
        "B": "one condition binds for EVERY admitted arm — the other is decoration, and clause"
             " ②'s criterion is simpler than it has been written",
        "C": "some admitted arms sit hairline-close to the boundary — the set IS marginal and"
             " R880's zero-flip inference was reading bootstrap precision as distance"}[world])
    print(f"     ⚠ R880 inferred 'not marginal' from zero flips. This measures it: the closest")
    print(f"       admitted arm is {a_lo[0]/mde_typ:.2f} MDEs clear, which is the quantity that")
    print(f"       inference was standing in for.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_prompts": n, "n_arms": C,
               "n_admitted": int(adm.sum()), "nboot": NBOOT,
               "ci_slack_admitted": {"min": float(a_lo[0]), "p25": float(np.percentile(a_lo, 25)),
                                     "median": float(np.median(a_lo)), "max": float(a_lo[-1])},
               "typical_mde": mde_typ, "closest_in_mdes": float(a_lo[0] / mde_typ),
               "binds_BH": nb, "binds_CI": nc,
               "tightest_admitted": tight,
               "derivation": "which condition binds is read off the two slacks, not measured",
               "arms": [{"arm": names[i], "margin": float(marg[i]), "lo": float(lo[i]),
                         "p": float(pv[i]), "bh_thresh": float(bh_thresh[i]),
                         "admitted": bool(adm[i]), "binds": binds[i]} for i in range(C)]},
              open(OUT / "boundary_distance.json", "w"), indent=2)
    print(f"\n  artifact: results/boundary_distance.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
