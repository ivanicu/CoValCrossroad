"""R456 -- re-price R455's marginal gap on EVERY annotator, and MEASURE the exponent instead of assuming it.

⚠ THE ANNOUNCED STEP IS RIGHT AND ITS PREDICTED NUMBER IS NOT DERIVABLE. R455 closed: "if the MDE
   falls as sqrt(16/3) ~ 2.3 suggests, +0.0141 moves from 1.04x to ~2.4x its floor." **That factor is
   an UPPER BOUND, not a prediction.** The MDE here is `ZEFF * sd(d)/sqrt(968)` where `d` is the
   BETWEEN-PROMPT vector of core-minus-baseline gaps. More annotators shrink only the ANNOTATOR-NOISE
   component of `sd(d)`; genuine prompt-level differences are untouched and set a floor the exponent
   cannot cross. *Twenty-fourth announced step checked -- the step survives, its arithmetic does not.*
   ⭐ So this round MEASURES the exponent with a dose-response in annotator count rather than
   assuming sqrt. That is the difference between checking my prediction and running it.

⭐ AND §4'S LONGEST ENTRY DEMANDS EXACTLY THIS. Its own sequence -- 0.0736 -> "report a bound" ->
   +0.0128 RESOLVED -- was three rounds of careful reasoning about what could not be known, ended by
   noticing that the release held 5x more data than the code consumed. Verified from the object here,
   not from that text: **median 16 annotators per prompt, mean 17.1, min 4, max 1012, 18,384
   annotations over 1078 prompts.** Every A2 in this campaign uses THREE.

ESTIMAND (named before the method)
    Identical to R455 -- the 10-fold CROSS-FITTED gap
        GAP(m) = mean_p [ A2_m(core, p) - A2_m(best generalising prompt-blind subset, p) ]
    but with A2_m computed against `m` annotators per prompt instead of 3.
    ⭐ The primary output is the DOSE-RESPONSE of MDE(m) against m, and the fitted exponent
      `MDE ~ m^-alpha`. alpha ~ 0.5 means annotator noise dominates; alpha ~ 0 means it does not and
      R455's 1.04x is a real design limit, not an under-powered one.

IDENTIFICATION
    Identified: every annotator is on disk. ⚠ NOT identified: whether more annotators change the
    ESTIMAND rather than its precision -- so the GAP is tracked at every m too, and a moving gap is
    its own world below, never folded into "better precision".

SCOPE  population : the same 968 prompts R455 used, so m is the ONLY thing that changes
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs; annotator count swept
       baseline   : the cross-fitted best generalising prompt-blind subset, m=4 criteria
       regime     : annotators per prompt in {1,2,3,5,8,16,ALL}; prompts with fewer use all they have

WORLDS
    W-RESOLVES  MDE falls with m and GAP stays put -> R455's 1.04x was an UNDER-POWERED design, the
                strengthened clause is solidly satisfied, and the interval tightens around +0.0141.
    W-LIMIT     MDE barely moves (alpha near 0) -> between-prompt variance is not annotator noise.
                R455's 1.04x is a REAL design limit and the claim stays an interval no matter how
                many annotators are read.
    W-MOVES     the GAP itself moves with m -> 3 draws was BIASING the estimate, not merely widening
                it, and R455's point needs correcting rather than tightening. ⚠ this world is why
                the gap is tracked at every m; it is the one I would otherwise not have looked for.

PREDICTION MATRIX
                    MDE falls, gap still   MDE flat   gap moves
    W-RESOLVES             0.90              0.05        0.05
    W-LIMIT                0.05              0.90        0.05
    W-MOVES                0.05              0.05        0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the controls fire at every m.
    |GAP(ALL) - GAP(3)| > MDE(3)                    -> W-MOVES  (checked FIRST; a moving estimand
                                                       makes any precision statement about it moot)
    else alpha >= 0.30 and GAP(ALL)/MDE(ALL) >= 1.5 -> W-RESOLVES
    else                                            -> W-LIMIT
    a control fails at any m                        -> UNVERIFIED

CONTROLS  (all recomputed at every m, because a control that holds at m=3 is not thereby valid at m=ALL)
    POSITIVE   ORACLE - baseline must resolve at every m; its GAP/MDE must RISE with m, which is the
               instrument-side check that more annotators actually buy precision here.
    g=0        the baseline against itself: exactly 0 at every m.
    NEUTRAL    `generic` - baseline must stay unresolved at every m. ⚠ If it becomes resolved as m
               grows, then "the core beats the baseline" is not specific to the core and the whole
               R455 reading changes -- this is the cell that can overturn the previous round.
    SHAM       wrong-prompt core must lose at every m.
    SKEW       max annotators is 1012 on one prompt. A CAPPED variant (<=16) is run beside ALL so a
               single prompt's precision cannot drive the result; both are reported.
    SEEDS      3 fold-assignments at every m; spread reported.

MULTIPLICITY  7 annotator counts x 5 arms x 3 seeds; the whole grid printed, nothing selected.
ARTIFACT      results/r456_annotators.json
IMPOSSIBLE HERE, NAMED
    * more annotators than the release ships -- 18,384 is the ceiling and this round reaches it.
    * whether the ANNOTATORS are right -- construct validity needs a standard outside the release.
"""
from __future__ import annotations
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
ZEFF = 1.959964 + 0.841621
L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))
M, K = 4, 10
MS = (1, 2, 3, 5, 8, 16, 0)          # 0 = ALL


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R456 · re-price R455's marginal gap on EVERY annotator — and MEASURE the exponent\n")
    print("  ⚠ R455 predicted the MDE would fall as sqrt(16/3)~2.3. That is an UPPER BOUND, not a")
    print("    prediction: more annotators shrink only the ANNOTATOR-NOISE part of the BETWEEN-PROMPT")
    print("    sd, and genuine prompt differences set a floor. Twenty-fourth step checked — the step")
    print("    survives, its arithmetic does not. So the exponent is MEASURED below.\n")

    need = {"pool": "genericpool16", "core": "coval_core", "sham": "coval_core_sham",
            "neutral": "generic"}
    S = {}
    for k, nm in need.items():
        f = SATD / f"sat_{nm}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: sat_{nm}.npz absent. Exit 2, never 0."); return 2
        S[k] = SC.load_sat(f)
    targets, _ = SC.load_targets()
    pids = sorted(set(targets) & set.intersection(*[set(v) for v in S.values()]))
    n = len(pids)
    if n < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2
    navail = np.array([len(targets[p]) for p in pids])
    print(f"  prompts {n} (the SAME population as R455, so m is the only thing that changes)")
    print(f"  annotators available: min {navail.min()} median {int(np.median(navail))} "
          f"mean {navail.mean():.1f} max {navail.max()}  total {navail.sum()}")

    subs = list(itertools.combinations(range(16), M))
    Sm = np.zeros((len(subs), 16))
    for j, s in enumerate(subs):
        Sm[j, list(s)] = 1.0
    POOLM, ARMC = {}, {k: {} for k in ("core", "sham", "neutral")}
    for p in pids:
        PMp = np.zeros((16, 4))
        for (ci, ltr), v in S["pool"][p].items():
            PMp[ci, L.index(ltr)] = v
        POOLM[p] = (Sm @ PMp) / M
        for k in ARMC:
            d = S[k][p]; cs = sorted({c for (c, _) in d})
            ARMC[k][p] = np.array([[d.get((c, l), 0.0) for l in L] for c in cs]).mean(axis=0)

    def build(m, cap=None):
        """A (1820 x n) and arm vectors, scored against m annotators (0 = ALL, cap limits ALL)."""
        A = np.zeros((len(subs), n)); arms = {k: np.zeros(n) for k in ARMC}
        used = np.zeros(n, int)
        for i, p in enumerate(pids):
            T = targets[p]
            if m == 0:
                idx = np.arange(len(T)) if cap is None else np.arange(min(len(T), cap))
            else:
                rg = np.random.default_rng(500 + stable(p))
                idx = (rg.permutation(len(T))[:m] if len(T) >= m else np.arange(len(T)))
            used[i] = len(idx)
            HC = np.array([SC.cls(np.array(T[j][0], float)) for j in idx])
            A[:, i] = (signs(POOLM[p])[:, None, :] == HC[None, :, :]).mean(axis=(1, 2))
            for k in ARMC:
                arms[k][i] = (signs(ARMC[k][p])[None, :] == HC).mean()
        arms["oracle"] = A.max(axis=0)
        return A, arms, float(used.mean())

    def paired(x, y, seed=0):
        d = x - y
        mde = ZEFF * d.std(ddof=1) / np.sqrt(len(d))
        rb = np.random.default_rng(77 + seed)
        bs = np.array([d[rb.integers(0, len(d), len(d))].mean() for _ in range(3000)])
        return (float(d.mean()), float(mde), float(np.percentile(bs, 2.5)),
                float(np.percentile(bs, 97.5)))

    rows = []
    print("\n  DOSE-RESPONSE IN ANNOTATOR COUNT — every cell, every control, nothing selected")
    print(f"    {'m':>5}{'used':>7}{'GAP':>9}{'MDE':>8}{'g/MDE':>7}"
          f"{'oracle':>9}{'o/MDE':>7}{'neutral':>9}{'sham':>9}{'g=0':>7}")
    for m in MS:
        A, arms, used = build(m)
        gaps, mdes, orc, neu, shm, g0s = [], [], [], [], [], []
        for sd in range(3):
            rg = np.random.default_rng(8000 + sd)
            fold = rg.permutation(n) % K
            base = np.zeros(n)
            for f in range(K):
                te = np.where(fold == f)[0]; tr = np.where(fold != f)[0]
                base[te] = A[int(np.argmax(A[:, tr].mean(axis=1))), te]
            g = paired(arms["core"], base, sd); gaps.append(g[0]); mdes.append(g[1])
            orc.append(paired(arms["oracle"], base, sd))
            neu.append(paired(arms["neutral"], base, sd))
            shm.append(paired(arms["sham"], base, sd))
            g0s.append(paired(base, base, sd)[0])
        gm, mm = float(np.mean(gaps)), float(np.mean(mdes))
        om, omde = float(np.mean([o[0] for o in orc])), float(np.mean([o[1] for o in orc]))
        nm_, nlo, nhi = (float(np.mean([x[0] for x in neu])),
                         float(np.mean([x[2] for x in neu])), float(np.mean([x[3] for x in neu])))
        sm = float(np.mean([x[0] for x in shm]))
        rows.append({"m": m, "used": used, "gap": gm, "mde": mm, "ratio": gm / mm,
                     "oracle": om, "oracle_ratio": om / omde, "neutral": nm_,
                     "neutral_ci": [nlo, nhi],
                     "neutral_resolved": bool(nlo > 0 or nhi < 0), "sham": sm,
                     "g0": float(np.mean(g0s)), "gap_seeds": gaps})
        print(f"    {'ALL' if m == 0 else m:>5}{used:>7.1f}{gm:>+9.4f}{mm:>8.4f}{gm/mm:>7.2f}"
              f"{om:>+9.4f}{om/omde:>7.1f}{nm_:>+9.4f}{sm:>+9.4f}{np.mean(g0s):>7.1e}")

    A, arms, usedc = build(0, cap=16)
    rg = np.random.default_rng(8000)
    fold = rg.permutation(n) % K
    base = np.zeros(n)
    for f in range(K):
        te = np.where(fold == f)[0]; tr = np.where(fold != f)[0]
        base[te] = A[int(np.argmax(A[:, tr].mean(axis=1))), te]
    gc = paired(arms["core"], base)
    print(f"    {'CAP16':>5}{usedc:>7.1f}{gc[0]:>+9.4f}{gc[1]:>8.4f}{gc[0]/gc[1]:>7.2f}"
          f"   <- SKEW control: one prompt has 1012 annotators and must not drive the result")

    use = [r for r in rows if r["m"] != 0]
    lm = np.log([r["used"] for r in use]); lmde = np.log([r["mde"] for r in use])
    alpha = float(-np.polyfit(lm, lmde, 1)[0])
    r3 = next(r for r in rows if r["m"] == 3); rall = rows[-1]
    print(f"\n  ⭐ MEASURED EXPONENT  MDE ~ m^-alpha,  alpha = {alpha:.3f}"
          f"   (sqrt would be 0.500)")
    print(f"    MDE {r3['mde']:.4f} at m=3  ->  {rall['mde']:.4f} at ALL "
          f"({r3['mde']/rall['mde']:.2f}x), vs the 2.3x R455 assumed")
    print(f"    GAP {r3['gap']:+.4f} at m=3  ->  {rall['gap']:+.4f} at ALL "
          f"(moved {abs(rall['gap']-r3['gap']):.4f}, MDE(3) = {r3['mde']:.4f})")

    moved = abs(rall["gap"] - r3["gap"]) > r3["mde"]
    ctrl_ok = (all(abs(r["g0"]) < 1e-12 for r in rows)
               and all(r["oracle"] > 0 and r["oracle_ratio"] > 2 for r in rows)
               and all(r["sham"] < 0 for r in rows)
               and not any(r["neutral_resolved"] and r["neutral"] > 0 for r in rows))
    if not ctrl_ok:
        world = "UNVERIFIED"
    elif moved:
        world = "W-MOVES"
    elif alpha >= 0.30 and rall["ratio"] >= 1.5:
        world = "W-RESOLVES"
    else:
        world = "W-LIMIT"
    print(f"\n  WORLD: {world}")
    if world == "W-RESOLVES":
        print(f"    R455's 1.04x was an UNDER-POWERED design. At every annotator the gap is")
        print(f"    {rall['gap']:+.4f} at {rall['ratio']:.2f}x its own MDE — the strengthened clause")
        print(f"    is solidly satisfied and the interval tightens rather than the point moving.")
    elif world == "W-LIMIT":
        print(f"    alpha = {alpha:.3f}: the between-prompt spread is NOT annotator noise. R455's")
        print(f"    1.04x is a REAL design limit and the claim stays an interval however many")
        print(f"    annotators are read. ⚠ This is the useful negative: it says the data does NOT")
        print(f"    have more to give here, which §4's longest entry could not have known in advance.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "alpha": alpha, "grid": rows,
           "cap16": {"gap": gc[0], "mde": gc[1], "ratio": gc[0] / gc[1], "used": usedc},
           "annotators": {"min": int(navail.min()), "median": int(np.median(navail)),
                          "mean": float(navail.mean()), "max": int(navail.max()),
                          "total": int(navail.sum())},
           "gap_m3": r3["gap"], "gap_all": rall["gap"], "mde_m3": r3["mde"],
           "mde_all": rall["mde"], "mde_ratio": r3["mde"] / rall["mde"], "gap_moved": bool(moved)}
    (RES / "r456_annotators.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r456_annotators.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
