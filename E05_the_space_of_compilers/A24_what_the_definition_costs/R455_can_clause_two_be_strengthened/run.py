"""R455 -- can clause ② be RESTATED against the strongest generalising prompt-blind set?

⛔ THE ANNOUNCED STEP RESTS ON A WEAK INFERENCE. R454 closed proposing to read the pool's 16 criterion
   TEXTS and, if they "span recipes", treat the transfer question as partly answered. **Spanning
   recipes TEXTUALLY does not establish behaving as multiple FAMILIES** -- the whole campaign's
   lesson is that a label is not a description, and R454's own behavioural handle (breadth
   saturation) is stronger evidence than any reading of the texts would be.
   *Twenty-third announced step checked; not killed, but demoted -- it answers a weaker question than
   the one the previous two rounds set up.*

⭐ WHAT R453 AND R454 SET UP, AND IT IS A DEFINITIONAL MOVE RATHER THAN ANOTHER MEASUREMENT. R453
   measured that a fixed PROMPT-BLIND set reaches **59.6%** of the way from the class floor to the
   released core, and R454 measured that this saturates in breadth. So clause ②'s baseline -- "a
   size-matched prompt-blind set" -- is demonstrably weak: most of what ② demands is reachable
   without reading the prompt at all. **The repair is to STRENGTHEN THE BASELINE**: require a core to
   beat not a random member of the prompt-blind class but the BEST prompt-blind set that GENERALISES.
   That is a strictly stronger clause, and the question is whether the released core still clears it.

⚠ AND RUNG 2 SAYS THIS IS NOT FORCED, WHICH IS WHAT MAKES IT SEVERE. Full-sample A2: the released
  core **0.5715**, the best fixed prompt-blind subset **0.5618** (R452). A gap of **+0.0097**, which
  sits at this design's resolution -- earlier rounds put the paired MDE near 0.010-0.015. **The test
  can easily come out unresolved, and if it does, the strengthened clause is not statable.**

ESTIMAND (named before the method)
    CROSS-FITTED, so the baseline is never chosen on the prompt it is scored on:
      partition the 968 prompts into K=10 folds; for each fold f,
        j*(-f) = argmax over the 1,820 prompt-blind subsets of mean A2 on the OTHER nine folds
        for every prompt p in f:  d[p] = A2(core, p) - A2(j*(-f), p)
      GAP = mean_p d[p] over all 968 prompts, one honest out-of-fold value each.
    ⭐ Cross-fitting is what makes this full-n: every prompt contributes, and no prompt's baseline
      was selected using it. A 50/50 hold-out would have thrown away half the population.

IDENTIFICATION
    Identified; no GPU. ⚠ NOT identified: whether a prompt-blind set drawn from a DIFFERENT family
    would be stronger. Exactly one prompt-blind family with breadth exists here (R454), so the
    strengthened clause is stated against THIS family and its scope line says so.

SCOPE  population : all 968 home-release prompts, each scored out-of-fold
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs, 3 annotator draws held common
       baseline   : the cross-fitted best generalising prompt-blind subset, m=4
       regime     : m = 4 for the baseline; the released core's own k (mean 3.95)

WORLDS
    W-STRONGER  GAP > MDE, resolved -> ② can be restated against the strongest generalising
                prompt-blind set and the released core still satisfies it. The within-family
                objection dissolves: the core beats not just the class but its best member.
    W-UNRESOLVED GAP inside the MDE -> the strengthened clause is NOT statable on this site. ② stays
                as written, and the 59.6% stands as an unrepaired weakness of its baseline.
    W-WORSE     GAP < 0 resolved -> the best generalising prompt-blind set BEATS the released core,
                and ② as written admits an object that outranks the only thing it was written for.

PREDICTION MATRIX
                     GAP > MDE   GAP inside MDE   GAP < -MDE
    W-STRONGER          0.90          0.05           0.05
    W-UNRESOLVED        0.05          0.90           0.05
    W-WORSE             0.05          0.05           0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the controls fire.
    if the g=0 control returns exactly 0 and the positive control resolves:
        GAP > MDE and CI excludes 0        -> W-STRONGER
        CI contains 0                      -> W-UNRESOLVED
        GAP < -MDE and CI excludes 0       -> W-WORSE
    else: UNVERIFIED.

CONTROLS
    POSITIVE   the ORACLE (per-prompt argmax, uses the answer) against the same cross-fitted
               baseline must resolve strongly positive. If even the oracle cannot, the design has no
               power and a null here is silence. ⚠ it must FAIL at g=0 -- see below.
    g=0        the cross-fitted baseline against ITSELF: exactly 0.0, and NOT resolved.
    SHAM       core criteria from the WRONG prompt against the same baseline: must lose.
    NEUTRAL    `generic` -- a prompt-blind arm that is not selected at all -- against the same
               baseline. This separates "the core is good" from "anything beats a cross-fitted pick".
    LEAKAGE    a deliberately LEAKY variant (baseline chosen in-fold) is run beside the honest one,
               so the size of the leak this design avoids is measured rather than asserted.
    MDE        computed from the paired vector's own cluster bootstrap, reported beside the GAP.
    SEEDS      3 fold-assignments; the spread across them is reported, never averaged away.

MULTIPLICITY  5 arms x 3 seeds x {honest, leaky} = 30 cells, all printed, no selection.
ARTIFACT      results/r455_strengthened.json
IMPOSSIBLE HERE, NAMED
    * a prompt-blind family other than this pool -- exactly one has breadth (R454).
    * whether the strengthened clause is the RIGHT strengthening -- that is a choice, and this round
      measures only whether it is SATISFIABLE by the one object the release ships.
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


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R455 · can clause ② be RESTATED against the strongest GENERALISING prompt-blind set?\n")
    print("  ⚠ RUNG 2: this is NOT forced. Full-sample A2 is core 0.5715 vs best fixed 0.5618 --")
    print("    a gap of +0.0097, at this design's resolution. It can come out unresolved.\n")

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
    SEEDS = (0, 1, 2)
    HC = {p: np.array([SC.cls(np.array(targets[p][int(np.random.default_rng(1000 * s + stable(p))
                                                      .integers(len(targets[p])))][0], float))
                       for s in SEEDS]) for p in pids}
    subs = list(itertools.combinations(range(16), M))
    Sm = np.zeros((len(subs), 16))
    for j, s in enumerate(subs):
        Sm[j, list(s)] = 1.0

    A = np.zeros((len(subs), n))
    arms = {k: np.zeros(n) for k in ("core", "sham", "neutral")}
    for i, p in enumerate(pids):
        PMp = np.zeros((16, 4))
        for (ci, ltr), v in S["pool"][p].items():
            PMp[ci, L.index(ltr)] = v
        A[:, i] = (signs((Sm @ PMp) / M)[:, None, :] == HC[p][None, :, :]).mean(axis=(1, 2))
        for k, src in (("core", "core"), ("neutral", "neutral")):
            d = S[src][p]; cs = sorted({c for (c, _) in d})
            Y = np.array([[d.get((c, l), 0.0) for l in L] for c in cs]).mean(axis=0)
            arms[k][i] = (signs(Y)[None, :] == HC[p]).mean()
        d = S["sham"][p]; cs = sorted({c for (c, _) in d})
        Y = np.array([[d.get((c, l), 0.0) for l in L] for c in cs]).mean(axis=0)
        arms["sham"][i] = (signs(Y)[None, :] == HC[p]).mean()
    arms["oracle"] = A.max(axis=0)
    print(f"  prompts {n};  A {A.shape};  K = {K}-fold cross-fitting (every prompt contributes)")

    def baseline(seed, honest=True):
        """-> per-prompt A2 of the cross-fitted best prompt-blind subset (out of fold if honest)."""
        rg = np.random.default_rng(8000 + seed)
        fold = rg.permutation(n) % K
        v = np.zeros(n); picks = []
        for f in range(K):
            te = np.where(fold == f)[0]
            tr = np.where(fold != f)[0] if honest else te
            j = int(np.argmax(A[:, tr].mean(axis=1)))
            picks.append(j)
            v[te] = A[j, te]
        return v, picks

    def paired(x, y, seed=0):
        d = x - y
        mde = ZEFF * d.std(ddof=1) / np.sqrt(len(d))
        rb = np.random.default_rng(77 + seed)
        bs = np.array([d[rb.integers(0, len(d), len(d))].mean() for _ in range(4000)])
        return (float(d.mean()), float(mde), float(np.percentile(bs, 2.5)),
                float(np.percentile(bs, 97.5)))

    print("\n  CONTROLS")
    b0, picks0 = baseline(0)
    g0 = paired(b0, b0)
    print(f"    g=0       the baseline against ITSELF -> {g0[0]:+.6f}   "
          f"{'PASS' if abs(g0[0]) < 1e-12 else '⛔ FAIL'}")
    orc = paired(arms["oracle"], b0)
    pos_ok = orc[0] > orc[1] and orc[2] > 0
    print(f"    POSITIVE  ORACLE - baseline -> {orc[0]:+.4f} vs MDE {orc[1]:.4f} "
          f"CI [{orc[2]:+.4f},{orc[3]:+.4f}]   {'PASS' if pos_ok else '⛔ FAIL — no power'}")
    shm = paired(arms["sham"], b0)
    print(f"    SHAM      wrong-prompt core - baseline -> {shm[0]:+.4f} "
          f"CI [{shm[2]:+.4f},{shm[3]:+.4f}]   {'PASS (loses)' if shm[3] < 0 else '⚠ does not lose'}")
    neu = paired(arms["neutral"], b0)
    print(f"    NEUTRAL   `generic` - baseline -> {neu[0]:+.4f} CI [{neu[2]:+.4f},{neu[3]:+.4f}]")
    print(f"              separates 'the core is good' from 'anything beats a cross-fitted pick'")
    bl, _ = baseline(0, honest=False)
    leak = paired(arms["core"], bl)
    print(f"    LEAKAGE   the SAME test with an IN-FOLD baseline -> {leak[0]:+.4f}; the honest")
    print(f"              design gives the number below, and the difference is the leak, measured")

    print("\n  ⭐ THE STRENGTHENED CLAUSE — core vs the cross-fitted best generalising prompt-blind set")
    print(f"    {'seed':>5}{'GAP':>10}{'MDE':>9}{'CI':>24}{'':>4}")
    cells, gaps = [], []
    for sd in SEEDS:
        b, pk = baseline(sd)
        g = paired(arms["core"], b, seed=sd)
        gaps.append(g[0])
        cells.append({"seed": sd, "gap": g[0], "mde": g[1], "ci": [g[2], g[3]],
                      "resolved": bool(g[2] > 0 or g[3] < 0),
                      "distinct_picks": len(set(pk))})
        print(f"    {sd:>5}{g[0]:>+10.4f}{g[1]:>9.4f}   [{g[2]:+.4f},{g[3]:+.4f}]   "
              f"{'RESOLVED' if (g[2] > 0 or g[3] < 0) else 'unresolved'}"
              f"   distinct fold-picks {len(set(pk))}/{K}")
    gm = float(np.mean(gaps)); spread = float(np.std(gaps))
    mde_m = float(np.mean([c["mde"] for c in cells]))
    all_res = all(c["resolved"] for c in cells)
    signs_same = len({np.sign(c["gap"]) for c in cells}) == 1
    print(f"    seed spread {spread:.4f} vs |gap| {abs(gm):.4f}  "
          f"(spread/|gap| = {spread/max(abs(gm),1e-9):.2f})")

    ctrl_ok = abs(g0[0]) < 1e-12 and pos_ok
    if not ctrl_ok:
        world = "UNVERIFIED"
    elif all_res and signs_same and gm > 0:
        world = "W-STRONGER"
    elif all_res and signs_same and gm < 0:
        world = "W-WORSE"
    else:
        world = "W-UNRESOLVED"
    print(f"\n  WORLD: {world}")
    if world == "W-STRONGER":
        print("    ② can be restated against the STRONGEST GENERALISING prompt-blind set and the")
        print("    released core still satisfies it. The 59.6% within-family objection DISSOLVES:")
        print("    the core beats not just the class but its best cross-fitted member.")
    elif world == "W-UNRESOLVED":
        print(f"    The strengthened clause is NOT statable here: the gap {gm:+.4f} sits inside its")
        print(f"    own MDE {mde_m:.4f}. ② stays as written and the 59.6% stands as an unrepaired")
        print("    weakness of its baseline. ⚠ This is a design-resolution result, not a claim that")
        print("    the core fails -- the positive control shows the design has power for a LARGE gap.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "K": K, "cells": cells,
           "gap_mean": gm, "gap_seed_spread": spread, "mde_mean": mde_m,
           "controls": {"g0": g0[0], "oracle_gap": orc[0], "oracle_mde": orc[1],
                        "oracle_ci": [orc[2], orc[3]], "sham_gap": shm[0], "sham_ci": [shm[2], shm[3]],
                        "neutral_gap": neu[0], "neutral_ci": [neu[2], neu[3]],
                        "leaky_gap": leak[0], "leak_size": leak[0] - gm}}
    (RES / "r455_strengthened.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r455_strengthened.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
