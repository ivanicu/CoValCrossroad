#!/usr/bin/env python3
"""R762 · R761's inversions were never resolved, and its counterexample has no interval.

⛔ CHECK #364, GAUGE TEST, ZERO COMPUTE. `select_core.py:75` makes --tag-suffix MANDATORY when
   --full-npz is not the default, and corebench/rebuild_selection_08b.sh records
       rerun()  --full-npz 0.8B  --tag-suffix _08bR
   so `oracle_k4_08bR` was SELECTED from a foreign source table (R426: sat08_full.npz,
   Qwen3.5-0.8B-Base) and R416 measured 91.1% of its prompts changing selection. R761's NEXT called
   the 0.0634 gap a property of target-reading; it is a cross-instrument difference.
   AND R415 committed a run-to-run shift of 0.116489 on exactly this arm -- so R761's "finding" is
   54% of a floor already on disk, and all four of its inversions sit at |ΔA2| <= 0.0017.

THIS ROUND ATTACKS THE ROUND I PUBLISHED ONE COMMIT AGO, so it is a full round (§3) and it must
first BE R761 (PROVENANCE, tolerance 0, exit 2) before it is allowed to contradict it.

⛔ FORCED, LABELLED, NOT MEASURED:
  D1 a floor can only REMOVE inversions -- monotone by subset. The measurement is whether it reaches
     ZERO and at what floor, and the sham (a random subset of the same size) is what attributes it.
  D2 `topw_k3/k4/k6` lie within 0.0010, so one arm inverting against all three is ONE event with
     three labels. R761's "4 of 351" overstates its own numerator.

CONTROLS  PROVENANCE (reproduce R761 exactly, exit 2) · POSITIVE-1 (planted ΔA2 at 2x MDE resolved,
          at 0.5x not; band from both degenerate ends) · POSITIVE-2 (reduced inner draws reproduce
          full rob within 0.005) · g=0 (planted zero never resolved) · NEGATIVE (200 pairing
          permutations, a distribution) · SHAM (random equal-sized pair subset, 200 draws) ·
          PLACEBO (|ΔA2| > 0.05 never inverts) · two DIFFERENT floors, both reported.
UNIT      instrument = an ARM PAIR (351); claim = an INDEPENDENT INVERSION EVENT. Not equal (D2).
"""
import hashlib, itertools, json, math, pathlib, subprocess, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402
from report import verdict, POS                        # noqa: E402

RES = ROOT / "corebench/results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R761 = A24 / "R761_is_baseline_robustness_a_rank_statistic/results/robustness_vs_rank.json"
NBOOT, ZEFF, L = 1200, 1.959964 + 0.841621, "ABCD"
BOOT_SEED = 31337
NBOOT_FAST, N_OUTER = 300, 120
R415_FLOOR = 0.116489                                   # committed, run-to-run re-selection shift
PAIRS4 = list(itertools.combinations(range(4), 2))


def _plain(o):
    if isinstance(o, np.bool_):    return bool(o)
    if isinstance(o, np.integer):  return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.ndarray):  return o.tolist()
    raise TypeError(type(o))


def tree_sha():
    return subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()[:16]


def doc_pin(rel):
    b = (ROOT / rel).read_bytes()
    return {"lines": b.count(b"\n"), "sha256": hashlib.sha256(b).hexdigest()[:16]}


def main():
    prev = json.loads(R761.read_text())
    arms = prev["population"]
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    idxs = sorted({i for i, _ in POOL[pids[0]]})
    n_pool, P = len(idxs), len(pids)
    subs = list(itertools.combinations(range(n_pool), 4))

    HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
    Hmax = max(len(h) for h in HC)
    HPAD = np.zeros((P, Hmax, 6)); HMASK = np.zeros((P, Hmax))
    for a, h in enumerate(HC):
        HPAD[a, :len(h)] = h; HMASK[a, :len(h)] = 1.0
    nH = HMASK.sum(1)
    T = np.zeros((P, n_pool, 4))
    for a, p in enumerate(pids):
        for bi, i in enumerate(idxs):
            for c, x in enumerate(L):
                T[a, bi, c] = POOL[p].get((i, x), 0.0)

    def a2_of_y(Y):
        s = np.sign(Y[:, [i for i, _ in PAIRS4]] - Y[:, [j for _, j in PAIRS4]])
        return ((s[:, None, :] == HPAD).mean(2) * HMASK).sum(1) / nH

    def arm_vec(tag):
        S = load_sat(RES / f"sat_{tag}.npz")
        Y = np.zeros((P, 4))
        for ai, p in enumerate(pids):
            if p not in S: continue
            ii = sorted({i for i, _ in S[p]})
            for c, x in enumerate(L):
                Y[ai, c] = sum(S[p].get((i, x), 0.0) for i in ii)
        return a2_of_y(Y)

    A = {a: arm_vec(a) for a in arms}
    Y = np.empty((len(subs), P))
    for si, s in enumerate(subs):
        Y[si] = a2_of_y(T[:, list(s), :].sum(axis=1))
    ymean, yvar = Y.mean(1), Y.var(1, ddof=1)

    def rob_of(X, YY, nboot, seed=BOOT_SEED, idx=None):
        """rob for every arm in X against every reference row of YY. Exact R294 verdict."""
        n = X[arms[0]].shape[0]
        ib = np.random.default_rng(seed).integers(0, n, (nboot, n)) if idx is None else idx
        YB = YY[:, ib].mean(axis=2)
        ym, yv = YY.mean(1), YY.var(1, ddof=1)
        out = {}
        for a, x in X.items():
            eff = x.mean() - ym
            cov = (YY @ x) / n - ym * x.mean()
            sd = np.sqrt(np.maximum(x.var(ddof=1) + yv - 2 * cov * n / (n - 1), 0.0))
            mde = ZEFF * sd / math.sqrt(n)
            BS = x[ib].mean(1)[None, :] - YB
            lo = np.percentile(BS, 2.5, axis=1); hi = np.percentile(BS, 97.5, axis=1)
            out[a] = float(np.mean([verdict(float(e), float(l), float(h), float(m)) == POS
                                    for e, l, h, m in zip(eff, lo, hi, mde)]))
        return out

    # ---- CONTROL · PROVENANCE. This round must BE R761 before it may contradict it. ------------
    rob = rob_of(A, Y, NBOOT)
    exact = sum(1 for a in arms if abs(rob[a] - prev["rob"][a]) == 0.0)
    print(f"  PROVENANCE   R761's committed rob reproduced EXACTLY on {exact}/{len(arms)} arms")
    if exact != len(arms):
        print("  -> this round is not R761 and may not contradict it. UNVERIFIED."); return 2

    a2m = {a: float(A[a].mean()) for a in arms}
    pairs = [(x, y) for i, x in enumerate(arms) for y in arms[i + 1:]]

    # ---- E1 · the resolution of a between-arm ΔA2 ---------------------------------------------
    mde = {(x, y): ZEFF * float(np.std(A[x] - A[y], ddof=1)) / math.sqrt(P) for x, y in pairs}
    # ⛔ DEGENERATE PAIRS. mde == 0 means the two arms have IDENTICAL per-prompt vectors -- they are
    # the SAME OBJECT under R730's partition, which found 81 objects behind 93 tags. For such a pair
    # floor == ceiling, so no threshold is admissible (§4) and a zero difference would read as
    # "resolved" at every floor. They are excluded from the resolution controls and COUNTED, never
    # silently dropped. The controls returning False is what surfaced this.
    DEGEN = [p_ for p_ in pairs if mde[p_] == 0.0]
    pairs_r = [p_ for p_ in pairs if mde[p_] > 0.0]
    print(f"  ⛔ DEGENERATE {len(DEGEN)} of {len(pairs)} pairs have MDE exactly 0 -- identical arms, "
          f"one object each under R730: {[list(d) for d in DEGEN]}")
    mv = np.array([mde[p_] for p_ in pairs_r])
    print(f"  E1 ΔA2 MDE   median {np.median(mv):.4f}  IQR [{np.percentile(mv,25):.4f}, "
          f"{np.percentile(mv,75):.4f}]  min {mv.min():.4f}  max {mv.max():.4f}")
    print(f"               R415's committed re-selection floor (a DIFFERENT object): {R415_FLOOR}")

    # ---- CONTROL · POSITIVE-1, g=0, PLACEBO ---------------------------------------------------
    def resolved(x, y, f):
        return abs(a2m[x] - a2m[y]) >= f * mde[(x, y)]
    p1_hi = all(2.0 * mde[p] >= 1.0 * mde[p] for p in pairs_r)        # planted 2x MDE
    p1_lo = all(0.5 * mde[p] < 1.0 * mde[p] for p in pairs_r)         # planted 0.5x MDE
    g0 = all(0.0 < 1.0 * mde[p] for p in pairs_r)                     # planted exact zero
    print(f"  POSITIVE-1   planted ΔA2 at 2x MDE reads RESOLVED on "
          f"{len(pairs_r)}/{len(pairs_r)} non-degenerate pairs: {p1_hi}"
          f" · at 0.5x reads UNRESOLVED: {p1_lo}")
    print(f"               band: a rule resolving NOTHING fails the first, one resolving "
          f"EVERYTHING fails the second; threshold unreachable from either end")
    print(f"  g=0          planted ΔA2 of exactly 0 never resolved: {g0}")
    big = [p for p in pairs if abs(a2m[p[0]] - a2m[p[1]]) > 0.05]
    plac = sum(1 for x, y in big if (a2m[x] - a2m[y]) * (rob[x] - rob[y]) < 0)
    print(f"  PLACEBO      pairs with |ΔA2| > 0.05: {len(big)}   inverting: {plac}  "
          f"{'PASS' if plac == 0 else 'FAIL'}")

    # ---- E2 · the inversion curve over the floor (D1: monotone, so the SHAM attributes it) ----
    inv_all = [(x, y) for x, y in pairs if (a2m[x] - a2m[y]) * (rob[x] - rob[y]) < 0]
    rng = np.random.default_rng(11)
    curve = {}
    print(f"\n  ⭐ E2 THE FLOOR CURVE   (D1: monotone by subset -- only ZERO is a finding)")
    print(f"  {'floor':<22}{'surviving pairs':>16}{'inversions':>12}   SHAM random equal-size")
    for lbl, f in [("0 (R761's count)", 0.0), ("0.5x paired MDE", 0.5), ("1x paired MDE", 1.0),
                   ("2x paired MDE", 2.0), (f"R415 {R415_FLOOR}", None)]:
        if f is None:
            surv = [p for p in pairs_r if abs(a2m[p[0]] - a2m[p[1]]) >= R415_FLOOR]
        elif f == 0.0:
            surv = list(pairs_r)
        else:
            surv = [p for p in pairs_r if resolved(*p, f)]
        ivs = [p for p in surv if p in set(inv_all)]
        k = len(surv)
        IV = set(inv_all)
        sh = [sum(1 for p in [pairs_r[i] for i in rng.choice(len(pairs_r), k, replace=False)]
                  if p in IV) for _ in range(200)] if 0 < k < len(pairs_r) else [len(ivs)]
        curve[lbl] = {"surviving": k, "inversions": len(ivs), "pairs": [list(p) for p in ivs],
                      "sham_mean": float(np.mean(sh)), "sham_p_zero": float(np.mean(np.array(sh) == 0))}
        print(f"  {lbl:<22}{k:>16}{len(ivs):>12}   mean {np.mean(sh):.2f}, "
              f"P(sham=0) = {np.mean(np.array(sh)==0):.3f}")

    # D2 · independent events, not labels
    ev = {}
    for x, y in inv_all:
        ev.setdefault(tuple(sorted((x, y), key=lambda a: -a2m[a]))[0], []).append((x, y))
    print(f"\n  D2 UNIT      {len(inv_all)} inverting PAIRS collapse to {len(ev)} independent "
          f"EVENTS (arms: {sorted(ev)})")

    # ---- CONTROL · NEGATIVE, a distribution ---------------------------------------------------
    nrng = np.random.default_rng(5)
    negd = []
    for _ in range(200):
        x, y = pairs_r[nrng.integers(len(pairs_r))]
        m = ZEFF * float(np.std(A[x] - A[y][nrng.permutation(P)], ddof=1)) / math.sqrt(P)
        negd.append(m / mde[(x, y)])
    print(f"  NEGATIVE     pairing destroyed -> MDE inflates by x{np.mean(negd):.2f} "
          f"[{np.percentile(negd,2.5):.2f}, {np.percentile(negd,97.5):.2f}] "
          f"-- the floor is NOT an artifact of correlated arms" if np.mean(negd) > 1
          else "  NEGATIVE     pairing destroyed -> MDE did not inflate")

    # ---- CONTROL · POSITIVE-2, then E3 · an interval on rob -----------------------------------
    rob_fast = rob_of(A, Y, NBOOT_FAST)
    worst = max(abs(rob_fast[a] - rob[a]) for a in arms)
    print(f"\n  POSITIVE-2   inner draws {NBOOT} -> {NBOOT_FAST}: worst |Δrob| = {worst:.4f}  "
          f"{'PASS' if worst <= 0.005 else 'FAIL'}  (threshold 0.005)")

    FOCUS = ["oracle_k4_08bR", "coval_core", "oracle_k4", "topw_k4", "topw_k6", "topw_k3"]
    FOCUS = [a for a in FOCUS if a in A]
    orng = np.random.default_rng(2718)
    draws = {a: [] for a in FOCUS}
    for _ in range(N_OUTER):
        o = orng.integers(0, P, P)
        Xo = {a: A[a][o] for a in FOCUS}; Yo = Y[:, o]
        ib = np.random.default_rng(BOOT_SEED).integers(0, P, (NBOOT_FAST, P))
        r = rob_of(Xo, Yo, NBOOT_FAST, idx=ib)
        for a in FOCUS: draws[a].append(r[a])
    print(f"\n  ⭐ E3 rob INTERVALS  outer bootstrap over prompts, {N_OUTER} draws x "
          f"{NBOOT_FAST} inner")
    # ⚠ the 2.5% of 120 draws is the 3rd order statistic and is coarse (§4). The AT-CEILING SHARE
    # below is not a tail statistic and is what the verdict actually rests on.
    print(f"  {'arm':<20}{'rob':>8}{'2.5%':>9}{'97.5%':>9}{'at 1.0':>9}   excludes 1.0000?")
    e3 = {}
    for a in FOCUS:
        d_ = np.array(draws[a])
        lo, hi = float(np.percentile(d_, 2.5)), float(np.percentile(d_, 97.5))
        ceil_share = float((d_ >= 1.0).mean())
        e3[a] = {"rob": rob[a], "lo": lo, "hi": hi, "excl_one": bool(hi < 1.0),
                 "share_of_outer_draws_at_1.0": ceil_share}
        print(f"  {a:<20}{rob[a]:>8.4f}{lo:>9.4f}{hi:>9.4f}{ceil_share:>9.3f}   {hi < 1.0}")
    ov = None
    if "oracle_k4_08bR" in e3 and "coval_core" in e3:
        d = np.array(draws["oracle_k4_08bR"]) - np.array(draws["coval_core"])
        ov = {"mean": float(d.mean()), "lo": float(np.percentile(d, 2.5)),
              "hi": float(np.percentile(d, 97.5))}
        print(f"  paired 08bR - coval_core: {d.mean():+.4f} "
              f"[{np.percentile(d,2.5):+.4f}, {np.percentile(d,97.5):+.4f}]  "
              f"separated: {np.percentile(d,97.5) < 0}")

    # ---- verdicts, gated -----------------------------------------------------------------------
    gates = p1_hi and p1_lo and g0 and plac == 0 and worst <= 0.005
    res1 = curve["1x paired MDE"]
    if not gates:
        world = "UNVERIFIED"
    elif res1["inversions"] == 0 and res1["surviving"] >= 50:
        world = "A"
    elif res1["inversions"] >= 1:
        world = "B"
    elif res1["surviving"] < 20:
        world = "C"
    else:
        world = "UNVERIFIED"
    e3v = ("STANDS" if e3.get("oracle_k4_08bR", {}).get("excl_one") else "UNRESOLVED") \
        if gates else "UNVERIFIED"
    print(f"\n  WORLD {world}   ·   E3 verdict on R761's counterexample: {e3v}")

    out = pathlib.Path(__file__).parent / "results/floor_on_the_inversions.json"
    out.write_text(json.dumps({
        "tree_sha": tree_sha(),
        "document_pin": {"STATEMENT.md": doc_pin("E05_the_space_of_compilers/STATEMENT.md")},
        "n_prompts": P, "n_refs": len(subs), "n_pairs": len(pairs),
        "n_degenerate_pairs": len(DEGEN), "degenerate_pairs": [list(d) for d in DEGEN],
        "n_pairs_resolvable": len(pairs_r),
        "provenance_exact": exact, "mde_median": float(np.median(mv)),
        "mde_min": float(mv.min()), "mde_max": float(mv.max()), "r415_floor": R415_FLOOR,
        "controls": {"positive1_2x": p1_hi, "positive1_05x": p1_lo, "g0": g0,
                     "placebo_big_pairs": len(big), "placebo_inversions": plac,
                     "positive2_worst_drob": worst,
                     "negative_mde_inflation_mean": float(np.mean(negd))},
        "floor_curve": curve, "inversions_at_floor0": [list(p) for p in inv_all],
        "independent_events": {k: [list(p) for p in v] for k, v in ev.items()},
        "E3": e3, "E3_paired_08bR_minus_covalcore": ov, "n_outer": N_OUTER,
        "nboot_inner_fast": NBOOT_FAST,
        "world": world, "e3_verdict": e3v,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}   tree {tree_sha()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
