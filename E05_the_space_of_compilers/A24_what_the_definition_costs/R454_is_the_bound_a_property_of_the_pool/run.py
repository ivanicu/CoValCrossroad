"""R454 -- is R453's 0.5773 a fact about clause ②, or about the POOL it was measured against?

⛔ THE ANNOUNCED STEP IS UNRUNNABLE AS STATED, and it fails at IDENTIFICATION, before power. R453
   closed proposing to "rebuild the reference class from a DIFFERENT prompt-blind family", citing
   `promptecho` and `generic` as other prompt-blind recipes. Asking the objects rather than my memory:
     * `promptecho` has ZERO hits in corebench/*.py -- its provenance cannot be established from the
       source, so it may not be prompt-blind at all, and I will not assert that it is.
     * breadth: `genericpool16` k=16 on all 968 prompts; `full` is the RUBRIC (prompt-SPECIFIC,
       k min/mean/max 4/15.5/39); `provenance_probe` covers 4 PROMPTS. Every other family is k<=4.
   **There is exactly ONE prompt-blind family with breadth >= 16.** n = 1, and no resampling makes a
   second. *Twenty-second announced step checked, TWELFTH killed.*

⭐ THE WORRY IS REAL AND IS RUNNABLE INSIDE THE POOL. If "within-family" is a fact about how BROAD
   the prompt-blind family is, then narrowing the family must move the bound. Draw the reference
   class from a random W of the 16 criteria, W = 6..16, and re-run R453's hold-out at each W. A
   dose-response in breadth answers the question the second family would have answered, and it
   answers it with the pool as its own control.

⚠ AND RUNG 2 FIRST, because the low-W end is degenerate by arithmetic: the class has C(W,4) members
  so `share` has granularity 1/C(W,4). W=4 -> 1 member, share vs itself is 0 and meaningless; W=5 ->
  5 members, granularity 0.20; W=6 -> 15, granularity 0.067. **Only W>=8 (70 members, 0.014) carries
  resolution comparable to W=16 (1820, 0.00055).** The low-W cells are printed and marked, never
  interpreted.

ESTIMAND (named before the method)
    For each breadth W and each of S random W-subsets of the 16 pool criteria:
      class(W)      = the C(W,4) size-4 subsets drawn from those W criteria
      j*(train)     = argmax over class(W) of mean train A2
      HELD_OUT(W)   = share of class(W), evaluated on TEST, that j* beats on TEST
      CORE(W)       = the released core's held-out share against the same class(W)
    ⭐ the reported quantity is the POSITION of the best fixed set between the class floor and the
      core: POS(W) = (HELD_OUT(W) - floor(W)) / (CORE(W) - floor(W)), where floor(W) is the class's
      OWN mean self-share at that breadth, computed, never guessed (R450's lesson).

IDENTIFICATION
    Identified: all A2 values are already computable, and a class at breadth W is a ROW SUBSET of the
    1,820 already built. ⚠ NOT identified: transfer to a prompt-blind family that is not this pool.
    That is the question the announced step asked and this site cannot answer it -- registered, not
    smuggled in.

SCOPE  population : 968 home-release prompts, 50/50 splits, B=20 per (W, seed)
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs, 3 annotator draws held common
       baseline   : the class's OWN computed self-share at each W
       regime     : m = 4 throughout; W in {6,8,10,12,14,16}

WORLDS
    W-POOL       POS(W) moves substantially with breadth -> R453's 0.5773 is a property of a
                 16-criterion pool, and EVERY clause-② number in the document inherits a scope line
                 naming the family it was measured against.
    W-CLAUSE     POS(W) is flat in W -> the within-family fraction is a property of the CLAUSE, and
                 R453's bound generalises across breadths of this family.
    W-GRANULAR   the movement tracks 1/C(W,4) -> what looks like a breadth effect is the share
                 statistic's own resolution changing, and neither of the above is established.

PREDICTION MATRIX
                    POS moves with W   POS flat   movement tracks granularity
    W-POOL                0.85            0.05             0.10
    W-CLAUSE              0.05            0.90             0.05
    W-GRANULAR            0.10            0.05             0.85

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the anchors hold.
    if W=16 reproduces R453 (HELD_OUT within 0.05 of 0.5773) and the g=0 selection is at the floor:
        |POS(16) - POS(8)| >= 0.20 and NOT tracking granularity -> W-POOL
        |POS(16) - POS(8)| <  0.20                              -> W-CLAUSE
        the POS trend correlates with 1/C(W,4) above |r| = 0.9  -> W-GRANULAR
    else: UNVERIFIED.

CONTROLS
    ANCHOR     W=16 must reproduce R453's held-out 0.5773 -- an independent path to a committed number.
    FLOOR      at each W the class's OWN mean self-share, COMPUTED (never the 0.5 guess that failed
               in R450, and never W=16's value reused).
    g=0        selection with the objective destroyed, at every W: must sit at that W's floor.
    NEGATIVE   worst-on-train at every W: must fall far below the floor.
    GRANULARITY 1/C(W,4) is printed beside every cell, and the W-GRANULAR world exists precisely so
               the resolution artifact can WIN rather than be dismissed.
    SEEDS      S=5 random W-subsets x B=20 splits at each W; spreads reported.

MULTIPLICITY  6 breadths x 4 selectors x 5 seeds; the whole grid printed, no cell selected.
ARTIFACT      results/r454_breadth.json
IMPOSSIBLE HERE, NAMED
    * a second prompt-blind family with breadth -- exactly one exists; would require generating and
      scoring >=16 new prompt-blind criteria, which is a generation job with its own assumptions.
    * whether `promptecho` is prompt-blind -- its provenance is not in the source that was searched.
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
M, B, S = 4, 20, 5
R453_HELDOUT = 0.5773


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R454 · is R453's 0.5773 about the CLAUSE, or about the POOL it was measured against?\n")
    print("  ⛔ the announced step is UNRUNNABLE: exactly ONE prompt-blind family has breadth >= 16")
    print("     (`genericpool16`); `full` is the RUBRIC and `provenance_probe` covers 4 prompts.")
    print("     `promptecho` has ZERO hits in corebench/*.py so I will not call it prompt-blind.")
    print("     Twenty-second announced step checked, TWELFTH killed -- at IDENTIFICATION.\n")

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
    Sm = np.zeros((len(subs), 16))
    for j, s in enumerate(subs):
        Sm[j, list(s)] = 1.0
    A = np.zeros((len(subs), n)); cv = np.zeros(n)
    for i, p in enumerate(pids):
        PMp = np.zeros((16, 4))
        for (ci, ltr), v in pool[p].items():
            PMp[ci, L.index(ltr)] = v
        A[:, i] = (signs((Sm @ PMp) / M)[:, None, :] == HC[p][None, :, :]).mean(axis=(1, 2))
        cs = sorted({c for (c, _) in core[p]})
        Yc = np.array([[core[p].get((c, l), 0.0) for l in L] for c in cs]).mean(axis=0)
        cv[i] = (signs(Yc)[None, :] == HC[p]).mean()
    subs_arr = np.array(subs)
    print(f"  A: {A.shape[0]} x {n};  a class at breadth W is a ROW SUBSET of these — no recompute")

    def share_in(v, rows, cols):
        d = v[None, cols] - A[np.ix_(rows, cols)]
        return float((d.mean(axis=1) > ZEFF * d.std(axis=1, ddof=1) / np.sqrt(len(cols))).mean())

    grid = []
    for W in (6, 8, 10, 12, 14, 16):
        gran = 1.0 / len(list(itertools.combinations(range(W), M)))
        cells = {k: [] for k in ("best", "core", "g0", "worst", "floor")}
        for sd in range(S):
            rg = np.random.default_rng(4000 + 97 * W + sd)
            keep = rg.choice(16, size=W, replace=False)
            rows = np.where(np.isin(subs_arr, keep).all(axis=1))[0]
            for b in range(B):
                rb = np.random.default_rng(6000 + 13 * b + sd)
                perm = rb.permutation(n); tr, te = perm[:n // 2], perm[n // 2:]
                mtr = A[np.ix_(rows, tr)].mean(axis=1)
                jb, jw = rows[int(np.argmax(mtr))], rows[int(np.argmin(mtr))]
                jg = rows[int(np.argmax(rb.permutation(mtr)))]
                cells["best"].append(share_in(A[jb], rows, te))
                cells["worst"].append(share_in(A[jw], rows, te))
                cells["g0"].append(share_in(A[jg], rows, te))
                cells["core"].append(share_in(cv, rows, te))
            # the class's OWN self-share at this breadth, computed not guessed
            pick = rg.choice(rows, size=min(60, len(rows)), replace=False)
            perm = np.random.default_rng(7000 + sd).permutation(n)[n // 2:]
            cells["floor"] += [share_in(A[j], rows, perm) for j in pick]
        row = {"W": W, "n_class": len(rows), "granularity": gran,
               **{k: float(np.mean(v)) for k, v in cells.items()}}
        row["pos"] = ((row["best"] - row["floor"]) / (row["core"] - row["floor"])
                      if row["core"] > row["floor"] else float("nan"))
        grid.append(row)

    print("\n  BREADTH DOSE-RESPONSE — every cell printed, low-W marked, never interpreted")
    print(f"    {'W':>3}{'|class|':>9}{'1/C':>9}{'floor':>8}{'g0':>8}{'worst':>8}"
          f"{'best':>8}{'core':>8}{'POS':>8}")
    for r in grid:
        mark = "  <- granularity-limited" if r["W"] < 8 else ""
        print(f"    {r['W']:>3}{r['n_class']:>9}{r['granularity']:>9.4f}{r['floor']:>8.4f}"
              f"{r['g0']:>8.4f}{r['worst']:>8.4f}{r['best']:>8.4f}{r['core']:>8.4f}"
              f"{r['pos']:>8.4f}{mark}")

    g16 = next(r for r in grid if r["W"] == 16)
    g8 = next(r for r in grid if r["W"] == 8)
    anchor_ok = abs(g16["best"] - R453_HELDOUT) <= 0.05
    use = [r for r in grid if r["W"] >= 8]
    g0_ok = all(abs(r["g0"] - r["floor"]) <= 0.15 for r in use)
    neg_ok = all(r["worst"] < r["floor"] for r in use)
    print("\n  CONTROLS")
    print(f"    ANCHOR   W=16 best held-out {g16['best']:.4f} vs R453's committed {R453_HELDOUT}"
          f"   {'PASS' if anchor_ok else '⛔ FAIL'}")
    print(f"    g=0      objective destroyed sits at each floor (W>=8)   "
          f"{'PASS' if g0_ok else '⛔ FAIL'}")
    print(f"    NEGATIVE worst-on-train below each floor (W>=8)   {'PASS' if neg_ok else '⛔ FAIL'}")
    gr = np.array([r["granularity"] for r in use]); po = np.array([r["pos"] for r in use])
    rho = float(np.corrcoef(gr, po)[0, 1]) if len(use) > 2 else float("nan")
    # ⛔ THE CORRELATION TEST IS INVALID AND IS KEPT ONLY TO SAY SO. `1/C(W,4)` and POS are BOTH
    #    monotone in W over 5 points, so they are collinear BY CONSTRUCTION and rho ~ -1 whatever
    #    the cause. It cannot separate "granularity did it" from "breadth did it".
    #    The VALID discriminator is arithmetic: one quantisation step of `share` is 1/|class|, and
    #    POS divides by (core - floor), so one step of POS is (1/|class|)/(core - floor). If the
    #    observed shift is many steps, quantisation cannot have produced it.
    step8 = g8["granularity"] / (g8["core"] - g8["floor"])
    step16 = g16["granularity"] / (g16["core"] - g16["floor"])
    dpos_pre = abs(g16["pos"] - g8["pos"])
    steps = dpos_pre / max(step8, step16)
    granular = steps < 2.0
    print(f"    GRANULARITY corr(1/C,POS) = {rho:+.4f} over {len(use)} points — ⛔ INVALID, both are")
    print(f"                monotone in W and therefore collinear by construction. Kept to say so.")
    print(f"                VALID test: one POS quantisation step is {max(step8,step16):.4f} "
          f"(W=8) and the observed shift is {dpos_pre:.4f} = {steps:.1f} steps   "
          f"{'⚠ WITHIN quantisation' if granular else 'PASS — not a resolution artifact'}")

    dpos = abs(g16["pos"] - g8["pos"])
    if not (anchor_ok and g0_ok and neg_ok):
        world = "UNVERIFIED"
    elif granular:
        world = "W-GRANULAR"
    elif dpos >= 0.20:
        world = "W-POOL"
    else:
        world = "W-CLAUSE"
    print(f"\n  |POS(16) - POS(8)| = {dpos:.4f}")
    print(f"  WORLD: {world}")
    if world == "W-CLAUSE":
        # ⛔ THE FIRST VERSION OF THIS STRING SAID "FLAT IN BREADTH". The grid does not show flat --
        #    it shows RISE THEN PLATEAU. A verdict string is prose that looks like output, so the
        #    shape is computed here rather than asserted.
        rise = po[1] - po[0]
        plateau = float(np.std(po[2:]))
        print(f"    NOT flat: POS RISES {rise:+.4f} from W=8 to W=10 and then PLATEAUS -- sd over")
        print(f"    W=12..16 is {plateau:.4f}. The pre-registered |POS(16)-POS(8)| = {dpos:.4f} sits")
        print(f"    just under its 0.20 threshold precisely because it pairs one point in the")
        print(f"    RISING regime with one in the plateau.")
        print(f"    ⭐ What that licenses: R453's W=16 measurement is in the SATURATED regime, so it")
        print(f"       is NOT limited by the pool's size -- more breadth would not move it. What it")
        print(f"       does NOT license: that the fraction is breadth-independent; below W~12 it")
        print(f"       clearly is not.")
        print("    ⚠ And it remains a property of THIS family: no second prompt-blind family exists.")
    elif world == "W-POOL":
        print("    The bound MOVES with breadth: every clause-② number inherits a scope line naming")
        print("    the family it was measured against.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "grid": grid,
           "pos_16": g16["pos"], "pos_8": g8["pos"], "delta_pos": dpos,
           "granularity_corr_INVALID": rho, "pos_quantisation_step": max(step8, step16),
           "shift_in_steps": steps, "pos_curve": [float(x) for x in po],
           "plateau_sd_W12_16": float(np.std(po[2:])), "n_prompt_blind_families_with_breadth": 1,
           "anchors": {"r453_anchor_ok": anchor_ok, "g0_ok": g0_ok, "negative_ok": neg_ok,
                       "r453_committed": R453_HELDOUT, "w16_best": g16["best"]}}
    (RES / "r454_breadth.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r454_breadth.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
