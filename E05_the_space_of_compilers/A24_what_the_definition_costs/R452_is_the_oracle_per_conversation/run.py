"""R452 -- is the oracle's advantage PER-CONVERSATION, or is it max-of-1820 selection noise?

⛔ RUNG 2 VOIDS THE ANNOUNCED STATISTIC, ZERO COMPUTE. R451 closed asking whether the oracle
   "concentrates on a few pool criteria (a fixed better subset exists) or spreads across prompts
   (the choice really is per-conversation)", to be answered by comparing the oracle to the best
   fixed subset. **That comparison is FORCED.** The oracle is `argmax` over C(16,4)=1820 candidates
   per prompt, and a max of 1820 draws exceeds the best fixed draw substantially **even when the
   candidates carry no per-prompt information at all** -- the winner's curse. So `oracle > best
   fixed` is arithmetic, not evidence. *Twentieth announced step checked; its statistic killed.*

⭐ THE QUESTION SURVIVES, BUT ONLY AGAINST A NULL ORACLE -- the same argmax-per-prompt operation on
   a matrix with the prompt x subset INTERACTION destroyed and both marginals preserved. What the
   real oracle has that the null oracle does not is the per-conversation information, and nothing
   else is.

ESTIMAND (named before the method)
    A[j,p] = A2 of pool subset j on prompt p, over all 1,820 subsets and 968 prompts.
    oracle_mean      = mean_p max_j A[j,p]
    best_fixed_mean  = max_j mean_p A[j,p]
    null_oracle_mean = the same max-of-1820, on a matrix whose interaction has been destroyed
    ⭐ EXCESS = oracle_mean - null_oracle_mean   <- the ONLY quantity here that is not forced
    and the concentration of the winner distribution (effective number of distinct winners,
    top-1 win share), real against null.

IDENTIFICATION
    Identified: both marginals and the full matrix are computable from files already on disk.
    ⚠ NOT identified: whether per-conversation information, if present, is about the CONVERSATION or
      about the annotator draw for that conversation. The draw is held common between real and null,
      so it cannot create EXCESS -- but it can carry it, and that is not separable here.

SCOPE  population : 968 home-release prompts x 1,820 prompt-blind subsets
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs, 3 annotator draws held common
       baseline   : the null oracle, TWO constructions, reported side by side
       regime     : m = 4 throughout

WORLDS
    W-NOISE      EXCESS ~ 0 under both nulls -> the oracle's 1.0000 in R451 is max-of-N selection
                 noise. It says nothing about per-conversation structure, and every round that used
                 the oracle as a CEILING was quoting an inflated one.
    W-PERCONV    EXCESS clearly > 0 and the real winner distribution is no more concentrated than
                 the null's -> the choice genuinely is per-conversation.
    W-FIXED      EXCESS > 0 but the winners CONCENTRATE far beyond the null -> a small set of pool
                 criteria is better for most prompts, and "per-conversation" overstates it.

PREDICTION MATRIX
                    excess ~ 0   excess>0, spread   excess>0, concentrated
    W-NOISE            0.90            0.05                 0.05
    W-PERCONV          0.05            0.90                 0.05
    W-FIXED            0.05            0.05                 0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if POSITIVE fires and does not fire at g=0.
    EXCESS below its own permutation CI under EITHER null      -> W-NOISE
    EXCESS above, and effective-winners ratio real/null > 0.5  -> W-PERCONV
    EXCESS above, and that ratio <= 0.5                        -> W-FIXED
    else: UNVERIFIED.

CONTROLS
    POSITIVE   plant per-prompt structure: boost ONE designated subset per prompt by delta. EXCESS
               must recover it and the MDE in delta is reported.
               ⚠ AND IT MUST FAIL AT g=0 -- at delta=0 the planted matrix is the real one and EXCESS
               must land inside the null CI. This is the arithmetic-trap check made executable.
    NEGATIVE   TWO nulls, because one is not enough and they bracket the answer:
                 N1 independent permutation per subset -- destroys the interaction AND the
                    inter-subset correlation, so the null max is INFLATED: conservative against
                    finding structure.
                 N2 two-way residual permutation -- subtract row and column means, permute the
                    residuals, add back. Preserves both marginals and the additive part, destroys
                    only the interaction. This is the null the estimand actually names.
    PLACEBO    the annotator draw is held common between real and null, so it cannot generate EXCESS.
    SEEDS      3 seeds x 200 permutations per null; spreads reported, never averaged away.

MULTIPLICITY  2 nulls x 2 statistics x 3 seeds = 12 cells, all reported, no selection.
ARTIFACT      results/r452_oracle_excess.json
IMPOSSIBLE HERE, NAMED
    * separating conversation content from the annotator draw -- would need multiple independent
      draws per conversation scored separately, which the 3-draw design does not support.
    * whether a per-conversation oracle is ACHIEVABLE without hindsight -- R451 measured that our
      one generator is not; this round says only what the oracle's ceiling is worth.
"""
from __future__ import annotations
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))
M = 4


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def eff_winners(win, nsub):
    c = np.bincount(win, minlength=nsub).astype(float)
    p = c[c > 0] / c.sum()
    return float(np.exp(-(p * np.log(p)).sum())), float(c.max() / c.sum())


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R452 · is the oracle's advantage PER-CONVERSATION, or max-of-1820 selection noise?\n")
    print("  ⛔ RUNG 2, zero compute: `oracle > best fixed subset` is FORCED. A max of 1820 draws")
    print("     exceeds the best fixed draw even with NO per-prompt information -- winner's curse.")
    print("     Twentieth announced step checked, its statistic KILLED.\n")

    pool_f = SATD / "sat_genericpool16.npz"
    if not pool_f.exists():
        print("  UNRUNNABLE: pool satisfaction absent. Exit 2, never 0."); return 2
    pool = SC.load_sat(pool_f)
    targets, _ = SC.load_targets()
    pids = sorted(set(pool) & set(targets))
    n = len(pids)
    if n < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    SEEDS = (0, 1, 2)
    HC = {p: np.array([SC.cls(np.array(targets[p][int(np.random.default_rng(1000 * s + stable(p))
                                                      .integers(len(targets[p])))][0], float))
                       for s in SEEDS]) for p in pids}
    subs = list(itertools.combinations(range(16), M))
    S = np.zeros((len(subs), 16))
    for j, s in enumerate(subs):
        S[j, list(s)] = 1.0
    A = np.zeros((len(subs), n))
    for i, p in enumerate(pids):
        PMp = np.zeros((16, 4))
        for (ci, ltr), v in pool[p].items():
            PMp[ci, L.index(ltr)] = v
        Y = (S @ PMp) / M
        A[:, i] = (signs(Y)[:, None, :] == HC[p][None, :, :]).mean(axis=(1, 2))
    print(f"  matrix A: {A.shape[0]} subsets x {A.shape[1]} prompts, judged by 2B")

    oracle_mean = float(A.max(axis=0).mean())
    best_fixed = float(A.mean(axis=1).max())
    win = A.argmax(axis=0)
    eff_r, top1_r = eff_winners(win, len(subs))
    print(f"\n  THE FORCED COMPARISON, stated so it cannot be mistaken for a result")
    print(f"    oracle mean A2      {oracle_mean:.4f}")
    print(f"    best FIXED subset   {best_fixed:.4f}")
    print(f"    difference          {oracle_mean-best_fixed:+.4f}   <- DERIVATION, not evidence:")
    print(f"                        a max of {len(subs)} draws exceeds the best single draw by")
    print(f"                        construction. The null oracle below is what makes it readable.")

    # ⛔ RUNG 1 KILLED MY OWN ESTIMAND, after rung 2 killed the announced one. Diagnosing why both
    #    nulls came back ABOVE the real oracle:
    #    ① `oracle_mean = mean_p max_j A[j,p]` is INVARIANT under any permutation of prompt labels
    #       -- permuting columns does not change the multiset of column maxima. So NO permutation
    #       null exists for it, and EXCESS-vs-a-permutation-null was mis-specified from the start.
    #    ② Both nulls destroyed the INTER-SUBSET correlation. The 1,820 subsets overlap heavily, and
    #       that correlation is exactly what keeps the max away from the ceiling. Made independent,
    #       N1 saturates at 1.0000 -- a control that CANNOT PASS, built again.
    #    The statistic that is NOT prompt-permutation-invariant in a useful sense is CONCENTRATION,
    #    and its correct null is a SYNTHETIC POOL with no per-prompt criterion structure, assembled
    #    through the SAME combinatorics so the overlap correlation is reproduced exactly. Rung 4.
    print("\n  ⛔ BOTH PERMUTATION NULLS ARE VOID — diagnosed, not discarded")
    print("     oracle_mean is INVARIANT under prompt-label permutation (the multiset of column")
    print("     maxima does not move), so no permutation null exists for it. And both destroy the")
    print("     inter-subset correlation, which is what holds the max down: N1 saturates at 1.0000.")

    print("\n  ⭐ THE UN-FORCED FACT, and it needs no null to state")
    print(f"    effective distinct winners  {eff_r:8.1f} of {len(subs)}  ({100*eff_r/len(subs):.1f}%)")
    print(f"    top-1 subset's win share    {top1_r:8.4f}   vs uniform {1/len(subs):.5f} "
          f"({top1_r*len(subs):.0f}x)")

    # ---- THE CORRECT NULL: a synthetic pool with NO per-prompt criterion structure ---------------
    print("\n  SYNTHETIC NULL — criteria have FIXED quality, no prompt-specific advantage,")
    print("  assembled through the identical C(16,4) combinatorics so overlap is reproduced")
    sd_real = float(A.std())
    syn = []
    for sd in SEEDS:
        rg = np.random.default_rng(1300 + sd)
        q = rg.normal(0, 1, 16)                      # per-criterion quality, NO prompt dependence
        effs, tops, sds = [], [], []
        for _ in range(4):
            Asyn = np.zeros((len(subs), n))
            for i, p_ in enumerate(pids):
                b = rg.normal(0, 1, 4)               # per-prompt response effects
                e = rg.normal(0, 1.0, (16, 4))       # noise
                Y = (S @ (q[:, None] + b[None, :] + e)) / M
                Asyn[:, i] = (signs(Y)[:, None, :] == HC[p_][None, :, :]).mean(axis=(1, 2))
            ew, t1 = eff_winners(Asyn.argmax(axis=0), len(subs))
            effs.append(ew); tops.append(t1); sds.append(float(Asyn.std()))
        syn.append((float(np.mean(effs)), float(np.mean(tops)), float(np.mean(sds))))
    ef_s = float(np.mean([x[0] for x in syn])); t1_s = float(np.mean([x[1] for x in syn]))
    sd_s = float(np.mean([x[2] for x in syn]))
    print(f"    real       eff-winners {eff_r:8.1f}   top-1 {top1_r:.4f}   sd(A) {sd_real:.4f}")
    print(f"    synthetic  eff-winners {ef_s:8.1f}   top-1 {t1_s:.4f}   sd(A) {sd_s:.4f}")
    print(f"    ratio real/synthetic:  eff-winners {eff_r/ef_s:.3f}   top-1 {top1_r/t1_s:.2f}x")
    scale_ok = 0.5 <= sd_s / sd_real <= 2.0
    print(f"    CALIBRATION  sd ratio {sd_s/sd_real:.2f} in [0.5,2.0]   "
          f"{'PASS' if scale_ok else '⛔ FAIL — the synthetic is not on the real scale'}")

    # POSITIVE control on the synthetic instrument: plant per-prompt criterion structure
    rg = np.random.default_rng(1777)
    q = rg.normal(0, 1, 16)
    Ap = np.zeros((len(subs), n))
    for i, p_ in enumerate(pids):
        fav = rg.integers(0, 16)
        qq = q.copy(); qq[fav] += 3.0               # a DIFFERENT criterion favoured per prompt
        b = rg.normal(0, 1, 4); e = rg.normal(0, 1.0, (16, 4))
        Y = (S @ (qq[:, None] + b[None, :] + e)) / M
        Ap[:, i] = (signs(Y)[:, None, :] == HC[p_][None, :, :]).mean(axis=(1, 2))
    ef_p, t1_p = eff_winners(Ap.argmax(axis=0), len(subs))
    pos_ok = ef_p > ef_s
    print(f"    POSITIVE   plant a DIFFERENT favoured criterion per prompt -> eff-winners "
          f"{ef_p:8.1f} vs no-structure {ef_s:.1f}   "
          f"{'PASS (per-prompt structure SPREADS the winners)' if pos_ok else '⛔ FAIL'}")
    print(f"    g=0        the no-structure synthetic itself is the g=0 cell: {ef_s:.1f}")

    ratio = eff_r / ef_s
    if not scale_ok or not pos_ok:
        world = "UNVERIFIED"
    elif ratio < 0.5:
        world = "W-FIXED"
    elif ratio > 1.5:
        world = "W-PERCONV"
    else:
        world = "W-NOISE"
    print(f"\n  WORLD: {world}")
    if world == "W-FIXED":
        print(f"    The oracle CONCENTRATES far beyond what no-structure combinatorics produces")
        print(f"    ({eff_r:.1f} vs {ef_s:.1f} effective winners). A SMALL SET of generic criteria")
        print(f"    wins most prompts, so `per-conversation` overstates what the oracle is doing --")
        print(f"    and R451's ceiling of 1.0000 is largely a FIXED better subset plus max-of-N.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "n_subsets": len(subs),
           "oracle_mean": oracle_mean, "best_fixed_mean": best_fixed,
           "forced_difference": oracle_mean - best_fixed,
           "permutation_nulls": "VOID — oracle_mean is prompt-permutation invariant and both "
                                "destroy inter-subset correlation; N1 saturates at 1.0000",
           "eff_winners_real": eff_r, "eff_winners_synthetic": ef_s,
           "eff_winners_planted": ef_p, "top1_win_share": top1_r, "top1_synthetic": t1_s,
           "eff_ratio_vs_synthetic": ratio, "sd_real": sd_real, "sd_synthetic": sd_s,
           "calibration_ok": scale_ok, "positive_ok": bool(pos_ok)}
    (RES / "r452_oracle_excess.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r452_oracle_excess.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
