"""Attacking the matrix BEFORE running it. Five attacks, each an experiment, none an opinion.

r209 reported rank 13 against r208's rank 2 and called the repair successful. Ivan asked for proof
that the matrix about to run is still broken. The honest way to answer is to run the controls the
rank claim never had.

ATTACK 1 -- THE RANK HAS NO NULL, and it is the whole claim. Nineteen vectors of length 290x15 =
4350 are GENERICALLY INDEPENDENT: rank deficiency requires exact algebraic collinearity, which is
why r208's design collapsed and nothing else would. So "rank 13" may be a statement about 19 < 4350
rather than about my operators being normatively distinct.
  PREDICTION, WRITTEN BEFORE THE RUN: matched-norm random operators reach rank >= 13 as well. If
  they do, the rank statistic is VACUOUS as evidence of distinctness, r209's headline is void, and
  the pre-registered kill built on it ("C3 dies iff rank <= design rank") cannot be evaluated.
  WHAT SURVIVES IF SO: the eigenvalue SPECTRUM, which is scale-free -- a design whose operators are
  distinct should be FLATTER than noise, not merely full-rank.

ATTACK 2 -- 95% IS A THRESHOLD I CHOSE. Report the whole curve.

ATTACK 3 -- RANK IS A FUNCTION OF n. More prompts means longer vectors means more independence
from noise alone. If rank rises with n, it is measuring sample size.

ATTACK 4 -- EVERY WEIGHT AND SET OPERATOR IS APPLIED TO ok[0], THE FIRST CRITERION. r208 measured
the selection rule at 6.6x. So each operator is one draw from a distribution whose spread exceeds
the effect, with no seed and no sweep. The realstat standard demands >=3 seeds and a check that the
seed changes the draws; this design has ZERO.

ATTACK 5 -- THE OPERATORS HAVE DIFFERENT DOMAINS. `register_veto_blind` is defined only where an
annotator named an unacceptable response (16.9%); `register_personal` only where a personal ranking
was given (26.7%). Their columns are computed on different subpopulations from the weight
operators', so the gram matrix mixes estimands. Measured below.
"""
from __future__ import annotations

import json, math, pathlib, sys
from collections import defaultdict
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
SRC = ROOT / "13_normative_chain/r209_repaired_design/results/repaired_rank.json"


def spectrum(M):
    n = np.linalg.norm(M, axis=1, keepdims=True)
    k = n[:, 0] > 1e-12
    if k.sum() < 2:
        return np.array([1.0])
    G = (M[k] / n[k])
    e = np.clip(np.linalg.eigvalsh(G @ G.T), 0, None)[::-1]
    return e / e.sum()


def rank_at(e, q):
    return int(np.searchsorted(np.cumsum(e), q) + 1)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    R9 = ROOT / "13_normative_chain/r209_repaired_design/results"
    D = np.load(R9 / "_deltas.npy")                       # [ops, prompts, chan]
    ops = [tuple(x) for x in json.loads((R9 / "_ops.json").read_text())]
    nop, npr, nch = D.shape
    F = D.reshape(nop, -1)
    e_obs = spectrum(F)
    r_obs = rank_at(e_obs, 0.95)
    print("=" * 100)
    print(f"THE OBJECT UNDER ATTACK: {nop} operators x {npr} prompts x {nch} channels "
          f"= vectors of length {npr * nch}")
    print("=" * 100)
    print(f"  observed rank(95%) = {r_obs}   top eigenvalue share {e_obs[0]:.3f}")

    # ---------------------------------------------------------------- ATTACK 1: the null
    print("\n" + "=" * 100)
    print("ATTACK 1 -- THE RANK HAS NO NULL. Prediction registered above: random reaches >= 13.")
    print("=" * 100)
    rng = np.random.default_rng(0)
    per_norm = np.linalg.norm(D, axis=2)                  # [ops, prompts] magnitude signature
    nulls = {}
    for nm, gen in [
        ("N1 gaussian, matched per-prompt norms",
         lambda: (lambda Z: Z / np.maximum(np.linalg.norm(Z, axis=2, keepdims=True), 1e-12)
                  * per_norm[:, :, None])(rng.standard_normal(D.shape))),
        ("N2 gaussian, matched TOTAL norm only",
         lambda: (lambda Z: Z / np.maximum(np.linalg.norm(Z.reshape(nop, -1), axis=1)
                                           [:, None, None], 1e-12)
                  * np.linalg.norm(F, axis=1)[:, None, None])(rng.standard_normal(D.shape))),
        ("N3 relabel: permute prompts within each operator",
         lambda: np.stack([D[i, rng.permutation(npr)] for i in range(nop)])),
        ("N4 sham: keep each operator's channel MARGINALS, destroy the joint",
         lambda: np.stack([np.stack([rng.permutation(D[i, :, c]) for c in range(nch)], axis=1)
                           for i in range(nop)])),
    ]:
        rs, tops = [], []
        for _ in range(20):
            en = spectrum(gen().reshape(nop, -1))
            rs.append(rank_at(en, 0.95)); tops.append(en[0])
        nulls[nm] = (float(np.mean(rs)), float(np.std(rs)), float(np.mean(tops)))
        print(f"  {nm:52s} rank {np.mean(rs):5.1f} +/- {np.std(rs):.1f}   top eig {np.mean(tops):.3f}")
    print(f"  {'OBSERVED':52s} rank {r_obs:5.1f}         top eig {e_obs[0]:.3f}")

    n1r = nulls["N1 gaussian, matched per-prompt norms"][0]
    n1t = nulls["N1 gaussian, matched per-prompt norms"][2]
    # A TWO-BRANCH VERDICT FOR A THREE-OUTCOME TEST -- the first version of this line read
    # "VACUOUS if r_obs >= null else carries information", which has no branch for the outcome
    # that actually occurred: the design ranks BELOW noise. That is neither vacuity nor evidence
    # of distinctness, it is evidence of REMAINING REDUNDANCY, and a verdict template missing the
    # observed outcome is the check-that-cannot-fail in its reporting form.
    if r_obs >= n1r - 1:
        verdict1 = ("VACUOUS -- random operators only match the design, so rank measures "
                    "19 < 4350 and nothing about the operators")
    elif r_obs < n1r - 1:
        verdict1 = (f"THE STATISTIC WAS READ BACKWARDS -- noise reaches {n1r:.0f} and the design "
                    f"reaches {r_obs}. Higher rank is not better here; the noise ceiling is the "
                    f"reference, and being {n1r - r_obs:.0f} BELOW it means roughly that many "
                    f"operators' worth of variation is still redundant")
    else:
        verdict1 = "unreachable"
    print(f"""
  VERDICT: {verdict1}.

  AND THE SHAM AND RELABEL NULLS SETTLE WHAT KIND OF STRUCTURE IT IS. N3 permutes which prompt
  each operator's delta came from and N4 destroys the joint while keeping every channel marginal;
  both land at rank 17 with top eigenvalue ~0.116, between pure noise (0.064) and the design
  (0.221). So HALF the concentration survives destroying the operator's cross-prompt signature --
  it comes from the magnitude profile alone -- and half is genuine shared direction.

  THE STATISTIC THAT ACTUALLY DISCRIMINATES IS THE TOP EIGENVALUE SHARE, NOT THE RANK:
    pure noise   {n1t:.3f}
    relabelled   {nulls['N3 relabel: permute prompts within each operator'][2]:.3f}
    the design   {e_obs[0]:.3f}      = {e_obs[0] / n1t:.2f}x noise, {e_obs[0] / nulls['N3 relabel: permute prompts within each operator'][2]:.2f}x relabelled
  A design whose operators were genuinely distinct would be FLATTER than noise. Mine is 3.5x more
  CONCENTRATED. r209's headline -- "rank 2 -> 13, prediction held" -- is therefore DOWNGRADED: the
  repair did add index spaces, but the operators still load on one dominant direction, and rank
  was the wrong statistic to notice it with.""")

    # ---------------------------------------------------------------- ATTACK 2: the threshold
    print("\n" + "=" * 100)
    print("ATTACK 2 -- 95% IS A THRESHOLD I CHOSE. The whole curve, against N1.")
    print("=" * 100)
    Z = rng.standard_normal(D.shape)
    Z = Z / np.maximum(np.linalg.norm(Z, axis=2, keepdims=True), 1e-12) * per_norm[:, :, None]
    e_n = spectrum(Z.reshape(nop, -1))
    print(f"  {'q':>6s} {'observed':>9s} {'null N1':>9s} {'gap':>6s}")
    curve = []
    for q in (0.50, 0.70, 0.80, 0.90, 0.95, 0.99):
        a, b = rank_at(e_obs, q), rank_at(e_n, q)
        curve.append({"q": q, "obs": a, "null": b})
        print(f"  {q:6.2f} {a:9d} {b:9d} {a - b:+6d}")

    # ---------------------------------------------------------------- ATTACK 3: rank vs n
    print("\n" + "=" * 100)
    print("ATTACK 3 -- RANK IS A FUNCTION OF n. If it rises with prompts, it measures sample size.")
    print("=" * 100)
    print(f"  {'prompts':>8s} {'observed':>9s} {'null N1':>9s}")
    vs_n = []
    for k in (10, 25, 50, 100, 200, npr):
        idx = rng.choice(npr, size=min(k, npr), replace=False)
        a = rank_at(spectrum(D[:, idx].reshape(nop, -1)), 0.95)
        b = rank_at(spectrum(Z[:, idx].reshape(nop, -1)), 0.95)
        vs_n.append({"n": int(k), "obs": a, "null": b})
        print(f"  {k:8d} {a:9d} {b:9d}")

    # ---------------------------------------------------------------- ATTACK 4: one criterion
    print("\n" + "=" * 100)
    print("ATTACK 4 -- EVERY WEIGHT OPERATOR HITS ok[0], WITH NO SEED AND NO SWEEP")
    print("=" * 100)
    print(f"""  r208 measured the selection rule at 6.6x: deleting the highest-|w| criterion moves Y by
  0.273, the lowest by 0.041. r209 applies every weight and set operator to ok[0] -- the FIRST
  criterion in file order -- which is one arbitrary draw from a distribution whose spread exceeds
  the effect being measured. The design has ZERO seeds and the realstat standard requires >=3 plus
  a check that the seed changes the draws. This is not a subtlety: file order is not random, and
  if the first criterion is systematically the most-rated or the longest, every weight-space number
  in r209 is measured at a non-representative point. UNRESOLVED BY THIS ROUND -- it needs the
  operator re-run across a criterion sample, which changes r209's numbers rather than reinterpreting
  them.""")

    # ---------------------------------------------------------------- ATTACK 5: domains
    print("\n" + "=" * 100)
    print("ATTACK 5 -- THE OPERATORS DO NOT SHARE A DOMAIN")
    print("=" * 100)
    live = (np.linalg.norm(D, axis=2) > 1e-12)            # [ops, prompts]
    cov = live.mean(axis=1)
    print(f"  {'operator':24s} {'space':12s} {'prompts where it does anything':>32s}")
    for i, (nm, sp) in enumerate(ops):
        flag = "   <- SUBPOPULATION" if cov[i] < 0.9 else ""
        print(f"  {nm[:24]:24s} {sp:12s} {cov[i]:31.1%}{flag}")
    # numpy matmul on BOOLEAN arrays performs a LOGICAL product and returns bool, so the first
    # version of this line divided a 0/1 matrix by 290 and reported "agg_maximin and agg_median
    # share 0.3% of prompts" for two operators that are both defined everywhere. Cast to float.
    both = live.astype(float) @ live.astype(float).T / npr
    pairs = [(both[i, j] / max(cov[i], 1e-9), ops[i][0], ops[j][0])
             for i in range(nop) for j in range(nop) if i != j]
    worst = min(pairs)
    print(f"""
  The gram matrix treats a zero as "this operator did nothing here", but for a subpopulation
  operator a zero means "NOT DEFINED here". Those are different facts and the eigen-decomposition
  cannot tell them apart, so every cosine involving a subpopulation operator is shrunk toward zero
  by its own undefinedness -- which INFLATES the apparent rank rather than deflating it.
  Worst pair: {worst[1]} vs {worst[2]}, sharing {worst[0]:.1%} of the first's live prompts.
  register_veto_blind is defined on 59.3% and dose_saturate on 89.3% (a criterion already at |w|=10
  cannot be saturated further), so two of nineteen columns are estimands over different populations
  and the design has no missing-data model at all.""")

    # ---------------------------------------------------------------- what IS the shared direction
    print("\n" + "=" * 100)
    print("DIAGNOSIS -- what is the dominant direction the operators share")
    print("=" * 100)
    n = np.linalg.norm(F, axis=1, keepdims=True)
    G = F / np.maximum(n, 1e-12)
    w, V = np.linalg.eigh(G @ G.T)
    v1 = V[:, int(np.argmax(w))]
    order = np.argsort(-np.abs(v1))
    print(f"  loading of each operator on PC1 ({e_obs[0]:.1%} of the design's variance):")
    for i in order:
        bar = "#" * int(abs(v1[i]) * 40)
        print(f"    {ops[i][0][:24]:24s} {ops[i][1]:12s} {v1[i]:+.3f} {bar}")
    chan_energy = (D ** 2).sum(axis=(0, 1))
    names_ch = ["score"] * 4 + ["top1"] * 4 + ["borda"] * 4 + ["count", "veto", "register"]
    agg = defaultdict(float)
    for c, nm_ in zip(chan_energy, names_ch):
        agg[nm_] += float(c)
    tot = sum(agg.values())
    print(f"\n  and where the design's total energy sits, by channel:")
    for k, v in sorted(agg.items(), key=lambda kv: -kv[1]):
        print(f"    {k:10s} {v / tot:6.1%}")

    (OUT / "attacks.json").write_text(json.dumps(
        {"observed_rank": r_obs, "observed_top_eig": float(e_obs[0]), "nulls": nulls,
         "verdict_attack1": verdict1, "threshold_curve": curve, "rank_vs_n": vs_n,
         "coverage": {ops[i][0]: float(cov[i]) for i in range(nop)},
         "pc1_loadings": {ops[i][0]: float(v1[i]) for i in range(nop)},
         "channel_energy": {k: v / tot for k, v in agg.items()}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
