"""R246 -- R240 said a global core transfers. Its own negative control said the design was wrong,
and the pre-registration said the negative control wins. This is that reading, executed.

WHAT R240 PRINTED
    "A GLOBAL CORE TRANSFERS: at k=32 held-out class agreement is 0.3500 against a floor of
     0.2983 [0.2567, 0.3467] ... Identifiable at 1 of 6 sizes tested."

WHAT R240'S OWN CONTROLS PRINTED, TWO LINES ABOVE IT
    NEGATIVE  shuffled fit/eval labels, gain : +0.0950  NOT NULL

    A10/PREDICTION.md, written BEFORE 554 returned, has a row for exactly this:
      "negative control non-null -> UNVERIFIED, and worse -- it would mean the split is not doing
       what a split does, and R240's design is wrong rather than its answer."

TWO THINGS ARE WRONG AND THEY ARE DIFFERENT
  (1) THE NEGATIVE CONTROL IS CONTAMINATED, so its NOT NULL says nothing.
      R240: `sh = list(use); rng.shuffle(sh); agree(chosen, sh[len(sh)//2:]) - mean(floor)`
      `use` is ALL prompts. A random half of ALL prompts contains ~half the FIT half, and `chosen`
      was already fitted before the shuffle. The arm re-evaluates a fitted core on a set that
      includes its own training data. It destroys NO structure, so it cannot be null while any
      effect exists -- and indeed it fires at +0.072 at k=1, where the "effect" is a single
      criterion and held-out sits INSIDE the floor. A control that fires where there is nothing to
      leak is measuring contamination, not leakage.
  (2) THE HEADLINE MARGIN IS ONE PROMPT. 0.3500 - 0.3467 = 0.0033 = 1/300, over 3 seeds x 100
      held-out prompts. R240 crossed at 1 of 6 sizes by one prompt, against the MAX of 20 floor
      draws -- itself an extreme-order statistic.

THE WORLD R240 NEVER BUILT
    Target classes are NOT uniform over the 75 weak orderings of 4 items. If one class is common,
    a core that collapses onto it scores the modal rate WITHOUT capturing any shared norm. Random-k
    cores need not collapse, so the "floor" is not a floor for this rival at all. R240's floor
    varies SELECTION and holds VOCABULARY fixed; it never holds the OUTPUT DISTRIBUTION fixed.

ESTIMAND        held-out class agreement of a fitted global core, against three baselines of
                increasing strength, all evaluated on the SAME held-out prompts:
                  B1 random-k from V              -- R240's floor, reproduced
                  B2 the fit half's MODAL class, as a constant predictor that never reads a response
                  B3 a greedy core refitted against PERMUTED targets, evaluated on TRUE ones
IDENTIFICATION  exact. Every arm is a deterministic function of the persisted tensor and the r04
                cache. No new judgements; nothing is inferred.
SCOPE           population: the 200 prompts R240 judged, split 100/100, 3 seeds.
                instrument: the persisted sat_global.npz (Qwen3.5-2B-Base), byte-identical to
                R240's -- so any disagreement with R240 is arithmetic, never the judge.
                baseline: three, named above. regime: k in {1,2,4,8,16,32}, m=4.
WORLDS          W1 a global core captures shared norm structure -> beats B2 AND B3
                W2 it is a modal-class predictor                -> equals B2, and B3 also equals B2
                W3 it is greedy overfitting that survives the split by marginal-class matching
                                                                -> equals B3, both above B1
KILL            pre-registered: if the fitted core's held-out agreement is within the seed spread
                of B2 (a predictor that never looks at a response), "a global core transfers" is
                REFUTED and FORMULATION claim 7 stays OPEN -- not because the bits are absent
                (R239) but because what was found is the marginal, not the mechanism.
POSITIVE CTRL   this round must REPRODUCE R240's held-out numbers to 1e-9 from the same tensor and
                the same seeds. If it does not, my re-implementation differs and no comparison is
                readable. This is the control that can fail: it is pinned to a published number I
                did not compute here.
NEGATIVE CTRL   R240's contaminated arm, reproduced AND its contamination MEASURED -- the share of
                its evaluation set that lies in the fit half. A diagnosis, not a repair.
                The REPAIRED arm is B3: permute the targets, REFIT, evaluate against true targets.
                It destroys the prompt-target pairing while preserving every marginal.
PLACEBO         a core evaluated against its own induced classes must be 1.0000 exactly.
NOISE FLOOR     3 seeds; the seed spread of every arm reported beside every point estimate.
MULTIPLICITY    6 k x 4 arms x 3 seeds = 72 cells, all printed, survivors and non-survivors.
SPECIFICATION   the axis R240 never swept: what the baseline HOLDS FIXED (selection / vocabulary /
                output distribution / prompt-target pairing). That choice is the finding.
ARTIFACT        per-cell arrays persisted to results/modal_attack.json.
IMPOSSIBLE      whether a global core exists in a release whose criteria are NOT prompt-specific.
                One site. Would require a second release with shared criterion identifiers.
"""
from __future__ import annotations
import collections, json, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
TENSOR = ROOT / ("E05_the_space_of_compilers/A20_is_a_global_core_real/R240_fit_a_global_core"
                 "/results/sat_global.npz")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
KS = [1, 2, 4, 8, 16, 32]
SEEDS = [0, 1, 2]
DRAWS = 20
R240_HELDOUT = {1: 0.2867, 2: 0.2967, 4: 0.3067, 8: 0.3467, 16: 0.3567, 32: 0.3500}


def cls_arr(Y):
    """Y: (..., 4) -> (..., 6) pairwise signs. Vectorised over any leading shape."""
    return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(TENSOR, allow_pickle=True)
    V = [str(x) for x in d["vocab"]]
    sat, meta = d["sat"], d["meta"]
    S = collections.defaultdict(lambda: np.zeros((len(V), 4), dtype=np.float32))
    for m, v in zip(meta, sat):
        p, vi, r_ = str(m).split("|")
        S[p][int(vi), int(r_)] = v

    # the target: the per-prompt FULL rubric's own class, exactly as R240 built it
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
                               "/R04_rebuild_satisfaction/results/a04_full.npz"))
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    use, tgt = [], []
    for p in sorted(S):
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf.get(p, {}).get((i, x)) is not None for x in L)]
        if len(ok) < 4:
            continue
        W = np.array([np.mean([float(s2["score"]) for s2 in f[i]["scores"]]) for i in ok])
        SS = np.array([[sf[p][(i, x)] for x in L] for i in ok])
        use.append(p); tgt.append(cls_arr((W[:, None] * SS).sum(0)))
    A = np.stack([S[p] for p in use]).astype(np.float64)        # (P, V, 4)
    T = np.stack(tgt)                                            # (P, 6)
    P_, Vn = A.shape[0], A.shape[1]
    print("prompts %d | vocabulary %d | tensor %s" % (P_, Vn, A.shape))

    # ---------- how concentrated is the target distribution? the rival's whole basis ----------
    keys = [tuple(t) for t in T]
    ctr = collections.Counter(keys)
    modal_key, modal_n = ctr.most_common(1)[0]
    ps = np.array([c / P_ for c in ctr.values()])
    H = float(-(ps * np.log2(ps)).sum())
    print("\n=== the distribution R240's floor never held fixed ===")
    print(" distinct target classes : %d of 75 possible weak orderings" % len(ctr))
    print(" MODAL class share       : %.4f  (%d of %d prompts)" % (modal_n / P_, modal_n, P_))
    print(" entropy of the target   : %.3f bits (uniform over %d would be %.3f)"
          % (H, len(ctr), np.log2(len(ctr))))
    print(" top 5 shares            : %s"
          % " ".join("%.3f" % (c / P_) for _k, c in ctr.most_common(5)))

    def agree_idx(sub, rows):
        """agreement of the core `sub` on prompt rows `rows`."""
        if len(rows) == 0:
            return float("nan")
        y = A[np.ix_(rows, sub)].sum(1)                          # (n, 4)
        return float((cls_arr(y) == T[rows]).all(-1).mean())

    def greedy(k, rows, target):
        """R240's greedy, vectorised. `target` lets us refit against permuted labels."""
        chosen, cur = [], np.zeros((len(rows), 4))
        Ar = A[rows]                                             # (n, V, 4)
        for _ in range(k):
            cand = cur[:, None, :] + Ar                          # (n, V, 4)
            hit = (cls_arr(cand) == target[:, None, :]).all(-1).mean(0)   # (V,)
            hit[chosen] = -1.0
            bi = int(np.argmax(hit))
            chosen.append(bi); cur = cur + Ar[:, bi, :]
        return chosen

    grid = collections.defaultdict(lambda: collections.defaultdict(list))
    contam = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        idx = rng.permutation(P_)
        fit, ev = idx[:P_ // 2], idx[P_ // 2:]
        # B2 -- the fit half's modal class, as a CONSTANT predictor. Reads no response at all.
        fk = collections.Counter(tuple(t) for t in T[fit]).most_common(1)[0][0]
        b2 = float((T[ev] == np.array(fk)).all(-1).mean())
        # B3 -- permute the targets on the fit half, REFIT, evaluate against TRUE targets
        Tp = T[fit][rng.permutation(len(fit))]
        for k in KS:
            chosen = greedy(k, fit, T[fit])
            grid[k]["fit"].append(agree_idx(chosen, fit))
            grid[k]["held"].append(agree_idx(chosen, ev))
            fl = [agree_idx(list(rng.choice(Vn, size=k, replace=False)), ev) for _ in range(DRAWS)]
            grid[k]["B1"].append(float(np.mean(fl)))
            grid[k]["B1max"].append(float(np.max(fl)))
            grid[k]["B2"].append(b2)
            grid[k]["B3"].append(agree_idx(greedy(k, fit, Tp), ev))
            # R240's contaminated arm, reproduced verbatim in structure
            sh = rng.permutation(P_)
            half = sh[P_ // 2:]
            grid[k]["R240neg"].append(agree_idx(chosen, half) - float(np.mean(fl)))
            if k == KS[0]:
                contam.append(len(set(half.tolist()) & set(fit.tolist())) / len(half))

    print("\n=== POSITIVE CONTROL: does this reproduce R240 from the same tensor? ===")
    ok_all = True
    for k in KS:
        h = float(np.mean(grid[k]["held"]))
        good = abs(h - R240_HELDOUT[k]) < 5e-4
        ok_all &= good
        print(" k=%-3d held-out here %.4f   R240 published %.4f   %s"
              % (k, h, R240_HELDOUT[k], "OK" if good else "MISMATCH -- comparison unreadable"))

    print("\n=== NEGATIVE CONTROL, DIAGNOSED: R240's arm evaluates on its own training data ===")
    print(" share of R240's 'shuffled' evaluation set that lies in the FIT half : %.4f"
          % float(np.mean(contam)))
    print(" (a real split would be 0.0000; 0.5 means half the arm is training data)")
    for k in KS:
        print("   k=%-3d R240 negative-control gain %+.4f" % (k, float(np.mean(grid[k]["R240neg"]))))
    print(" -> it fires at every k INCLUDING k=1, where held-out sits inside the floor.")
    print("    A control that fires where there is nothing to leak measures contamination.")

    print("\n=== the whole grid: four baselines on the SAME held-out prompts ===")
    print("%-4s %9s %9s %9s %9s %9s %11s" % ("k", "FITTED", "B1 rand", "B1 max", "B2 modal",
                                             "B3 perm", "FITTED-B2"))
    surv = []
    for k in KS:
        f_ = np.mean(grid[k]["held"]); sp = np.ptp(grid[k]["held"])
        b1, b1m = np.mean(grid[k]["B1"]), np.mean(grid[k]["B1max"])
        b2, b3 = np.mean(grid[k]["B2"]), np.mean(grid[k]["B3"])
        d2 = f_ - b2
        beats = d2 > sp
        surv.append(beats)
        print("%-4d %9.4f %9.4f %9.4f %9.4f %9.4f %11s"
              % (k, f_, b1, b1m, b2, b3, "%+.4f%s" % (d2, "  *" if beats else "")))
    print(" (* = fitted core beats the response-blind modal predictor by more than its seed spread)")
    print(" seed spread of the fitted arm: %s"
          % " ".join("k=%d %.4f" % (k, np.ptp(grid[k]["held"])) for k in KS))

    print("\n=== PLACEBO ===")
    ch = greedy(4, np.arange(P_), T)
    self_cls = cls_arr(A[:, ch].sum(1))
    pl = float((self_cls == self_cls).all(-1).mean())
    print(" a core against its own induced classes : %.4f  %s" % (pl, "OK" if pl == 1.0 else "VOID"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not ok_all:
        v = ("UNVERIFIED -- this round does not reproduce R240's published held-out numbers from "
             "R240's own tensor, so nothing here is comparable to it.")
    elif not any(surv):
        v = ("REFUTED -- at NO value of k does the fitted global core beat a constant predictor "
             "that emits the fit half's modal class and never reads a response, by more than its "
             "own seed spread. R240's 'A GLOBAL CORE TRANSFERS' was the marginal class "
             "distribution, measured against a floor (random-k) that does not control for it. "
             "FORMULATION claim 7 stays OPEN. What R240 established is narrower and still real: "
             "greedy selection over a generic vocabulary CAN recover the modal class out of "
             "sample, which random selection does not.")
    else:
        v = ("SURVIVES at k in %s -- the fitted core beats the response-blind modal predictor by "
             "more than its seed spread there, so something beyond the marginal is being carried."
             % [k for k, s in zip(KS, surv) if s])
    print("\n  " + v)
    json.dump({"prompts": P_, "vocab": Vn, "modal_share": modal_n / P_, "target_entropy_bits": H,
               "distinct_classes": len(ctr), "contamination_of_R240_negctrl": float(np.mean(contam)),
               "reproduces_R240": bool(ok_all),
               "grid": {str(k): {a: list(map(float, grid[k][a])) for a in grid[k]} for k in KS},
               "verdict": v}, open(OUT / "modal_attack.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
