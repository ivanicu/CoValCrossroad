"""R453 -- does a FIXED prompt-blind set clear clause ②'s bar on prompts it was not chosen on?

⛔ THE ANNOUNCED TEST IS FORCED, AND THE ARITHMETIC IS ONE LINE. R452 closed proposing to "compute
   the share of the BEST fixed prompt-blind subset, and if it clears the bar that admits the released
   core, ② does not test what its sentence says it tests." The share of a subset is the fraction of
   the 1,820-member class it beats -- and the BEST subset is a MEMBER OF THAT CLASS, selected by
   exactly the quantity the share ranks on. **Its share is near 1 by construction.** That is
   `1+1=2, therefore 2<3`. *Twenty-first announced step checked, its statistic killed.*

⭐ THE WORRY IS REAL AND HAS A NON-CIRCULAR FORM: HOLD OUT. Choose the best fixed subset on one half
   of the prompts, then score it on the OTHER half against the class evaluated on that same half.
   Cross-validation is exactly the instrument that prices the winner's curse, and the question it
   answers is the one the definition needs: **is there a fixed, prompt-BLIND set that generalises to
   new prompts and still beats the class there?**

⭐ AND IT RE-PRICES R452'S OWN HEADLINE. R452 measured that one subset wins 33.57% of prompts and
   that the oracle is 3.2x more concentrated than no-structure combinatorics -- all IN-SAMPLE. If
   that concentration is genuine quality it must survive to held-out prompts; if it is selection
   noise it will not. **The round that produced the claim could not test it; this one can.**

ESTIMAND (named before the method)
    Over B random halves of the 968 prompts:
      j*(train)          = argmax_j mean_{p in train} A[j,p]
      HELD_OUT_SHARE     = fraction of the class, evaluated on TEST, that j* beats on TEST
      IN_SAMPLE_SHARE    = the same on TRAIN                      <- DERIVATION, near 1 by construction
      TRANSFER           = HELD_OUT_SHARE, compared against the class's own self-share floor 0.2198
                           and against the released core's held-out share.
    Secondary, re-pricing R452: the share of TEST prompts won by the TRAIN-selected top subset.

IDENTIFICATION
    Fully identified; no GPU. ⚠ NOT identified: whether a prompt-blind set that generalises would be
    a "core" in any sense outside this definition. This asks what clause ② ADMITS, nothing more.

SCOPE  population : 968 home-release prompts, split 50/50, B=50 random splits
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs, 3 annotator draws held common
       baseline   : the class's own self-share (R450: 0.2198) and the released core
       regime     : m = 4 throughout, so size cannot explain any difference

WORLDS
    W-WITHIN-FAMILY  the train-selected subset's HELD-OUT share is far above the floor and near the
                     released core's -> a FIXED PROMPT-BLIND set clears ②'s bar on prompts it was
                     not chosen on. Clause ② is a WITHIN-FAMILY RANKING, not a prompt-specificity
                     test, and its sentence must be rewritten.
    W-CURSE          held-out share collapses to the floor -> the best fixed subset does not
                     generalise, R452's concentration is largely selection noise (and R452's
                     headline needs narrowing), and ② survives as written.
    W-PARTIAL        between the two: some transfer, not enough to clear the core's bar. Then the
                     honest output is a BOUND on how much of ② is within-family.

PREDICTION MATRIX
                       held-out ~ core   held-out ~ floor   in between
    W-WITHIN-FAMILY          0.90              0.03            0.07
    W-CURSE                  0.03              0.90            0.07
    W-PARTIAL                0.07              0.07            0.86

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the anchors hold.
    if the released core's held-out share is within 0.05 of its committed 0.9841
       and the g=0 selection lands within 0.10 of the floor:
        held-out share >= 0.80                       -> W-WITHIN-FAMILY
        held-out share <= floor + 0.10 (i.e. 0.32)   -> W-CURSE
        otherwise                                    -> W-PARTIAL, reported as a bound
    else: UNVERIFIED.

CONTROLS
    POSITIVE/ANCHOR  the released core is NOT selected on train, so it suffers no curse: its
                     held-out share must reproduce its committed 0.9841. This anchors the whole
                     pipeline against an independent code path.
    g=0              select on train using a SHUFFLED objective -- the selection carries no
                     information, so the held-out share must land at the floor. ⚠ this is the cell
                     that makes a low transfer readable rather than assumed.
    NEGATIVE         select the WORST subset on train; its held-out share must fall FAR BELOW the
                     floor. If it does not, selection does not transfer in EITHER direction and the
                     round is measuring nothing.
    DERIVATION       the in-sample share is printed beside every held-out share, labelled, so the
                     forced quantity cannot be mistaken for the measured one.
    SEEDS            B = 50 splits; the spread is reported, never averaged away.

MULTIPLICITY  4 selectors x 2 evaluation sides x 50 splits; every cell reported, no selection.
ARTIFACT      results/r453_holdout.json
IMPOSSIBLE HERE, NAMED
    * whether a generalising prompt-blind set is "really" a core -- needs a standard outside this
      definition.
    * a second release to check transfer across corpora -- R433 walked that route for a different
      question; here it would need the pool's 16 criteria scored there, which do not exist.
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
M, B = 4, 50
FLOOR = 0.2198          # R450, the class's own computed mean self-share
CORE_COMMITTED = 0.9841  # R446


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R453 · does a FIXED prompt-blind set clear ②'s bar on prompts it was NOT chosen on?\n")
    print("  ⛔ the announced test was FORCED: the BEST subset is a MEMBER of the class its share is")
    print("     computed against, selected by the very quantity that share ranks on -> near 1 by")
    print("     construction. Twenty-first announced step checked, its statistic killed.\n")

    pool_f, core_f = SATD / "sat_genericpool16.npz", SATD / "sat_coval_core.npz"
    if not (pool_f.exists() and core_f.exists()):
        print("  UNRUNNABLE: satisfaction absent. Exit 2, never 0."); return 2
    pool, core = SC.load_sat(pool_f), SC.load_sat(core_f)
    targets, _ = SC.load_targets()
    pids = sorted(set(pool) & set(core) & set(targets))
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
    cv = np.zeros(n)
    for i, p in enumerate(pids):
        PMp = np.zeros((16, 4))
        for (ci, ltr), v in pool[p].items():
            PMp[ci, L.index(ltr)] = v
        Y = (S @ PMp) / M
        A[:, i] = (signs(Y)[:, None, :] == HC[p][None, :, :]).mean(axis=(1, 2))
        cs = sorted({c for (c, _) in core[p]})
        Yc = np.array([[core[p].get((c, l), 0.0) for l in L] for c in cs]).mean(axis=0)
        cv[i] = (signs(Yc)[None, :] == HC[p]).mean()
    print(f"  matrix A: {A.shape[0]} subsets x {n} prompts;  B = {B} random 50/50 splits")

    def share_on(v, cols):
        d = v[None, cols] - A[:, cols]
        return float((d.mean(axis=1) > ZEFF * d.std(axis=1, ddof=1) / np.sqrt(len(cols))).mean())

    rows = {k: {"in": [], "out": []} for k in ("best", "worst", "g0", "core")}
    top_win_out, top_win_in = [], []
    for b in range(B):
        rg = np.random.default_rng(2000 + b)
        perm = rg.permutation(n)
        tr, te = perm[:n // 2], perm[n // 2:]
        mtr = A[:, tr].mean(axis=1)
        jbest, jworst = int(np.argmax(mtr)), int(np.argmin(mtr))
        jg0 = int(np.argmax(rg.permutation(mtr)))   # selection with the objective destroyed
        for k, j in (("best", jbest), ("worst", jworst), ("g0", jg0)):
            rows[k]["in"].append(share_on(A[j], tr))
            rows[k]["out"].append(share_on(A[j], te))
        rows["core"]["in"].append(share_on(cv, tr))
        rows["core"]["out"].append(share_on(cv, te))
        # ⛔ re-pricing R452 must use R452's OWN selection rule. R452's 33.57% was the win share of
        #    the subset that WINS THE MOST PROMPTS; `jbest` here is the highest MEAN A2. Different
        #    objects, and comparing them would be the "two different draws" mode. Select on train by
        #    R452's rule, evaluate on test.
        jwin = int(np.bincount(A[:, tr].argmax(axis=0), minlength=len(subs)).argmax())
        top_win_out.append(float((A[:, te].argmax(axis=0) == jwin).mean()))
        top_win_in.append(float((A[:, tr].argmax(axis=0) == jwin).mean()))

    def agg(x):
        return float(np.mean(x)), float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))

    print("\n  ANCHORS")
    # ⛔ THE FIRST ANCHOR COMPARED TWO DIFFERENT OBJECTS, and the arithmetic says so: `share` counts
    #    references beaten by more than ZEFF*sd/sqrt(n), so at n=484 the bar is sqrt(2) = 1.41x
    #    higher than at n=968 and EVERY half-sample share is structurally lower. Comparing the
    #    core's HALF-sample share to its committed FULL-sample 0.9841 was the R450 floor mistake
    #    again -- third time in four rounds. The pipeline anchor must be run at the committed n.
    full = share_on(cv, np.arange(n))
    anchor_ok = abs(full - CORE_COMMITTED) <= 0.02
    print(f"    PIPELINE  the core at the COMMITTED n={n}: {full:.4f} vs {CORE_COMMITTED}"
          f"   {'PASS' if anchor_ok else '⛔ FAIL — this is not the campaign pipeline'}")
    cm, clo, chi = agg(rows["core"]["out"])
    print(f"    REFERENCE the core on half-samples (n={n//2}, same as every selector below):")
    print(f"              {cm:.4f} [{clo:.4f},{chi:.4f}]  <- THIS is the bar to compare against,")
    print(f"              not 0.9841; the MDE at half the prompts is sqrt(2)x larger")
    gm, glo, ghi = agg(rows["g0"]["out"])
    g0_ok = abs(gm - FLOOR) <= 0.10
    print(f"    g=0  selection with the objective destroyed -> held-out {gm:.4f} "
          f"[{glo:.4f},{ghi:.4f}] vs floor {FLOOR}   "
          f"{'PASS' if g0_ok else '⛔ FAIL'}")
    wm, wlo, whi = agg(rows["worst"]["out"])
    neg_ok = wm < FLOOR
    print(f"    NEGATIVE  worst-on-train -> held-out {wm:.4f} [{wlo:.4f},{whi:.4f}], must be far")
    print(f"              below the floor   {'PASS — selection DOES transfer' if neg_ok else '⛔ FAIL'}")

    print("\n  ⭐ THE MEASUREMENT — in-sample beside held-out, so the forced number is visible")
    print(f"    {'selector':<10}{'IN (derivation)':>18}{'HELD-OUT':>26}")
    for k in ("best", "g0", "worst", "core"):
        im, ilo, ihi = agg(rows[k]["in"]); om, olo, ohi = agg(rows[k]["out"])
        print(f"    {k:<10}{im:>10.4f}        {om:>10.4f} [{olo:.4f},{ohi:.4f}]")

    bm, blo, bhi = agg(rows["best"]["out"])
    bim = float(np.mean(rows["best"]["in"]))
    twm, twlo, twhi = agg(top_win_out)
    tim = float(np.mean(top_win_in))
    print(f"\n  RE-PRICING R452 — using R452's OWN selection rule (most prompts won), not mean-A2")
    print(f"    train win share {100*tim:.2f}%   ->   HELD-OUT {100*twm:.2f}% "
          f"[{100*twlo:.2f}%,{100*twhi:.2f}%]")
    print(f"    R452's committed in-sample figure was 33.57%")
    print(f"    in-sample share {bim:.4f}  ->  held-out {bm:.4f}   "
          f"drop {bim-bm:+.4f}  <- the winner's curse, priced")

    anchors = anchor_ok and g0_ok and neg_ok
    if not anchors:
        world = "UNVERIFIED"
    elif bm >= 0.80:
        world = "W-WITHIN-FAMILY"
    elif bm <= FLOOR + 0.10:
        world = "W-CURSE"
    else:
        world = "W-PARTIAL"
    print(f"\n  WORLD: {world}")
    if world == "W-WITHIN-FAMILY":
        print("    ⛔ A FIXED PROMPT-BLIND SET clears ②'s bar on prompts it was not chosen on.")
        print("       Clause ② is a WITHIN-FAMILY RANKING, not a prompt-specificity test.")
    elif world == "W-CURSE":
        print("    The best fixed subset does NOT generalise. R452's concentration is largely")
        print("    selection noise, and clause ② survives as written.")
    elif world == "W-PARTIAL":
        print(f"    Partial transfer. The honest output is a BOUND: a fixed prompt-blind set reaches")
        print(f"    {bm:.4f} on unseen prompts, above the floor {FLOOR} and below the core's {cm:.4f}.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "n_subsets": len(subs), "B": B,
           "floor": FLOOR, "core_committed": CORE_COMMITTED,
           "held_out": {k: dict(zip(("mean", "lo", "hi"), agg(v["out"]))) for k, v in rows.items()},
           "in_sample_DERIVATION": {k: float(np.mean(v["in"])) for k, v in rows.items()},
           "top_subset_win_share": {"train": tim, "holdout": twm, "lo": twlo, "hi": twhi},
           "core_full_sample_share": full, "core_halfsample_share": cm,
           "winners_curse_drop": bim - bm,
           "anchors": {"core_ok": anchor_ok, "g0_ok": g0_ok, "negative_ok": neg_ok}}
    (RES / "r453_holdout.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r453_holdout.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
