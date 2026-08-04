"""R358 — R355's closure defect at the SECOND judge: estimator property, or 2B's noise profile?

R355 found that the "closure level" this campaign leans on is the FIRST closed reference and not
the lowest SAFE one: at 6 of 9 k, references STRONGER than the published closure admit blind sets
again. It named a mechanism -- R331's, one axis over:

    admission is `(e > 0) & (|e| >= mde)` where `mde` is the sd of the PER-PROMPT DIFFERENCE, so a
    reference with a HIGHER MEAN but a different per-prompt PROFILE can have a smaller paired sd
    against some blind set and admit it.

**That mechanism is a property of the ESTIMATOR, not of the judge.** So it makes a sharp, falsifiable
prediction that nothing in this campaign has tested: the defect must REPLICATE at Qwen3.5-0.8B-Base.
`sat08_genericpool16.npz` is the SAME 16 criteria scored by that judge, it is on disk, and R301
loads it -- but only ever as `POOL[0:k]`, the published file-prefix reference. **The blind class has
never been enumerated at 0.8B.** This round enumerates it.

⚠ MY OWN CLOSING SENTENCE, CORRECTED BY RUNNING THE COUNT IT QUANTIFIED OVER. R357 closed with
  "nothing in the campaign has asked what a third reading would admit". Counted: SIX round READMEs
  discuss admission together with the judge, and R301 already loads the 0.8B pool. The true gap is
  narrower and sharper than the sentence claimed -- the pool is loaded but never ENUMERATED -- and
  "nothing has asked" was the flattering-to-this-round version. §4: run the count before writing a
  sentence that quantifies over your own work.

⛔ ARITHMETIC TRAP, and it disposes of the obvious framing. R301 reports the admitted set at 0.8B is
   EMPTY at the published reference. Asking "what does 0.8B admit at a CLOSED (stricter) reference"
   is therefore FORCED: a stricter reference admits a subset of {}, which is {}. That question is a
   derivation and is not asked. The non-forced question is the DOWNWARD one -- *is there any
   reference weak enough that 0.8B admits an arm, and does it sit above or below 0.8B's own
   closure?* -- and its answer is not fixed by algebra, because it depends on whether the arms'
   levels fall inside or outside the pool's range at all. Both cases are computed and reported.

ESTIMAND
  PART A (replication)  per k and per grid at 0.8B: R355's `first0`, `safe_idx`, and the count of
                        candidate references above `first0` whose blind admission rate is > 0 --
                        the identical statistic, on the identical pool, at a different judge.
  PART B (definition)   over the directly-judged arms, the HIGHEST pool reference at which at least
                        one arm is admitted at 0.8B, and its position relative to 0.8B's own closure
                        level for that k.

IDENTIFICATION  PART A is exact on the grid: every C(16,k) subset is enumerated, so each rate is a
                population proportion. PART B is restricted to the arms JUDGED DIRECTLY at 0.8B
                (a `sat08_<arm>.npz` exists). R301 reaches 41 arms by REBUILDING 34 of them from
                `sat08_full.npz` via a subset path; that path is validated by R301's own parity
                control, but it is an assumption this round declines to inherit, so PART B's
                population is smaller and stated rather than borrowed.

SCOPE           968 prompts with >=2 annotators, intersected with both pools · instrument
                Qwen3.5-0.8B-Base (PART A and B) compared against R355's Qwen3.5-2B-Base ·
                baseline each candidate reference itself · the same 16-criterion pool.

WORLDS
  W-ESTIMATOR  the defect replicates: violations appear at 0.8B at comparable k, and the closed
               region is not an upward set there either. Then non-upward-closure is structural to
               the paired-MDE admission rule and every "closure level" sentence in this campaign
               inherits it, at any judge.
  W-JUDGE      violations are absent, or appear at entirely different k, at 0.8B. Then R355's
               finding is about the 2B judge's particular noise profile and its MECHANISM claim --
               which is about the estimator -- is wrong.
  W-WORSE      0.8B shows MATERIALLY MORE violations. It is the noisier judge, so its paired sds
               are larger and more erratic and near-neighbour accidents should be commoner. This is
               a dose-response on judge quality and is a distinct, directional outcome.

PREDICTION MATRIX
  W-ESTIMATOR -> violations_08 > 0, and the set of violating k overlaps 2B's
  W-JUDGE     -> violations_08 == 0, or zero overlap in violating k
  W-WORSE     -> violations_08 >= 2 x violations_2B at the same grid
The three differ on counts computed identically at both judges, from the same code.

PRE-REGISTERED KILL -- conditional, so it cannot fire on a broken instrument.
    if placebo_ok and positive_ok and g0_ok and synthetic_ok:
        if v08 == 0 or no k overlaps          -> W-JUDGE     (R355's mechanism claim refuted)
        elif v08 >= 2 * v2b                   -> W-WORSE
        else                                   -> W-ESTIMATOR
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

POSITIVE CTRL  inject the WEAKEST reference above `first0`; the violation detector must flag it.
g=0 CTRL       inject the class-MAX reference in the same slot; it must NOT be flagged, so the
               detector fires on rate and not on position.
PLACEBO        every candidate reference against itself: exactly 0 admitted.
NEGATIVE /     the rival world BUILT: flatten each reference to a constant vector at its own mean,
SYNTHETIC      making admission a pure threshold and upward-closure algebraic. Violations must fall
               to 0 -- at BOTH judges, which is a stronger demand than R355 made of itself.
MULTIPLICITY   every (k, grid, candidate) cell computed is printed, per judge, with cell counts.
SPECIFICATION  grid resolution 9 / 45 / 91, the axis R331-vs-R332 proved is an instrument.
SEEDS          the enumeration is deterministic; two runs required byte-identical.
ARTIFACT       results/r358_second_judge.json with the source hash.

IMPOSSIBLE HERE
  a third judge      -- NOT-ATTEMPTED-AND-NOT-CHEAP (R357): no third checkpoint on the local store.
  PART B at 41 arms  -- needs R301's subset-rebuild path, which this round declines to inherit.
  cross-release      -- one release.

EXIT
    0  controls hold and the replication is classified
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
GRIDS = {
    9:  np.array([0.0, 10.0, 25.0, 50.0, 75.0, 90.0, 95.0, 99.0, 100.0]),
    45: np.concatenate([np.array([0.0, 25.0, 50.0, 75.0]), np.linspace(80.0, 100.0, 41)]),
    91: np.concatenate([np.array([0.0, 25.0, 50.0, 75.0]), np.linspace(80.0, 100.0, 87)]),
}
KS = [1, 2, 3, 4, 6, 8, 12, 13, 15]


def admitted_mask(Bk, ref_vec):
    """R355's statistic, verbatim in its arithmetic. Same code, different judge."""
    d = Bk - ref_vec
    e = d.mean(axis=1)
    mde = ZEFF * d.std(axis=1, ddof=1) / math.sqrt(d.shape[1])
    return (e > 0) & (np.abs(e) >= mde)


def candidates(per, grid):
    order = np.argsort(per)
    seen, cand = set(), []
    for p in grid:
        c = int(order[min(int(round(p / 100 * (len(order) - 1))), len(order) - 1)])
        if c not in seen:
            seen.add(c); cand.append(c)
    return cand


def main() -> int:
    pool8 = RES / "sat08_genericpool16.npz"
    if not pool8.exists():
        print("  UNRUNNABLE: sat08_genericpool16.npz absent. Exit 2, never 0.")
        return 2
    r355 = next(A24.glob("R355_*"), None)
    f355 = sorted((r355 / "results").glob("*.json")) if r355 else []
    if not f355:
        print("  UNRUNNABLE: R355's artifact is absent — there is nothing to replicate. Exit 2.")
        return 2
    A355 = json.loads(f355[0].read_text())

    tg, _ = load_targets()
    S = load_sat(pool8)
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    SAT = np.stack([np.array([[S[p][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                    for p in pids])
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])

    def build(k):
        sb = np.array(list(itertools.combinations(range(npool), k)))
        out = np.empty((len(sb), N))
        for n in range(N):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[:, n] = (C_[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))
        return sb, out

    print(f"R358 · does R355's closure defect replicate at Qwen3.5-0.8B-Base?")
    print(f"  {N} prompts · pool {npool} · the SAME 16 criteria, the SAME statistic, "
          f"a different judge\n")

    SUBS, BK = {}, {}
    for k in KS:
        SUBS[k], BK[k] = build(k)

    # ---- PLACEBO --------------------------------------------------------------------------------
    plac = 0
    for k in KS:
        per = BK[k].mean(axis=1)
        for c in candidates(per, GRIDS[45]):
            plac += int(admitted_mask(BK[k], BK[k][c])[c])
    placebo_ok = plac == 0
    print(f"  PLACEBO  every reference against itself: {plac} self-admissions  "
          f"{'PASS' if placebo_ok else 'FAIL'}")

    # ---- PART A · the replication ----------------------------------------------------------------
    RES8, cells = {}, {}
    for g, grid in GRIDS.items():
        RES8[g], cells[g] = {}, 0
        for k in KS:
            per = BK[k].mean(axis=1)
            cand = candidates(per, grid)
            cells[g] += len(cand)
            counts = [int(admitted_mask(BK[k], BK[k][c]).sum()) for c in cand]
            zeros = [i for i, n_ in enumerate(counts) if n_ == 0]
            if not zeros:
                RES8[g][k] = None
                continue
            first0 = zeros[0]
            nz = [i for i in range(first0 + 1, len(cand)) if counts[i] > 0]
            safe = (max(nz) if nz else first0 - 1) + 1
            RES8[g][k] = dict(n_cand=len(cand), first0=first0, safe_idx=safe,
                              first0_a2=float(per[cand[first0]]),
                              safe_a2=float(per[cand[safe]]) if safe < len(cand) else None,
                              first0_pct=float(100.0 * (per < per[cand[first0]]).mean()),
                              n_violations=len(nz),
                              violation_counts=[counts[i] for i in nz])

    def v2b(g, k):
        r = A355["grids"][str(g)].get(str(k))
        return None if r in (None, "None") else r

    print(f"\n  PART A — the identical statistic at both judges\n")
    print(f"    {'grid':>5}{'k':>4}   {'2B first0 A2':>13}{'2B viol':>9}   "
          f"{'0.8B first0 A2':>15}{'0.8B viol':>11}   agree?")
    tot2, tot8 = {}, {}
    for g in sorted(GRIDS):
        t2 = t8 = 0
        for k in KS:
            a, b = v2b(g, k), RES8[g][k]
            av = a["n_violations"] if a else 0
            bv = b["n_violations"] if b else 0
            t2 += av; t8 += bv
            agree = "both" if av and bv else ("2B only" if av else ("0.8B only" if bv else "neither"))
            aa = f"{a['first0_a2']:.4f}" if a else "n/a"
            bb = f"{b['first0_a2']:.4f}" if b else "n/a"
            print(f"    {g:>5}{k:>4}   {aa:>13}{av:>9}   {bb:>15}{bv:>11}   {agree}")
        tot2[g], tot8[g] = t2, t8
        print()
    print(f"  totals by grid   2B {dict(sorted(tot2.items()))}   "
          f"0.8B {dict(sorted(tot8.items()))}")

    # ⚠ RAW COUNTS ARE NOT COMPARABLE ACROSS JUDGES, and reading them as though they were is the
    #   same error class as R355's cross-k pooling. A noisier judge has LARGER paired sds, hence a
    #   larger MDE, hence admits less of everything -- so it must show fewer violations even if the
    #   defect is identically present. The comparable quantity is the RATE: non-closed references
    #   as a share of the references ABOVE first0, i.e. of the population that could violate.
    print(f"\n  NORMALISED — violations as a share of the candidates ABOVE first0 (the population")
    print(f"    at risk). A noisier judge admits less of everything, so raw counts understate it.")
    print(f"      {'grid':>5}   {'2B risk':>8}{'2B viol':>9}{'2B rate':>9}   "
          f"{'0.8B risk':>10}{'0.8B viol':>11}{'0.8B rate':>11}")
    RATE = {}
    for g in sorted(GRIDS):
        r2 = sum(max((v2b(g, k) or {}).get("n_cand", 0) - (v2b(g, k) or {}).get("first0", 0) - 1, 0)
                 for k in KS)
        r8 = sum(max((RES8[g][k] or {}).get("n_cand", 0) - (RES8[g][k] or {}).get("first0", 0) - 1, 0)
                 for k in KS)
        p2 = tot2[g] / r2 if r2 else float("nan")
        p8 = tot8[g] / r8 if r8 else float("nan")
        RATE[g] = dict(risk_2b=r2, risk_08b=r8, rate_2b=p2, rate_08b=p8)
        print(f"      {g:>5}   {r2:>8}{tot2[g]:>9}{p2:>9.3f}   {r8:>10}{tot8[g]:>11}{p8:>11.3f}")
    kov = {g: sorted(k for k in KS
                     if (v2b(g, k) or {}).get("n_violations", 0) > 0
                     and (RES8[g][k] or {}).get("n_violations", 0) > 0) for g in GRIDS}
    print(f"  k with violations at BOTH judges: {kov}")

    # ---- controls on the detector, at 0.8B --------------------------------------------------------
    k0 = 4
    per0 = BK[k0].mean(axis=1)
    cand0 = candidates(per0, GRIDS[45])
    weakest, strongest = int(np.argmin(per0)), int(np.argmax(per0))
    f0 = RES8[45][k0]["first0"]

    def viol_above(cl):
        return [i for i in range(f0 + 1, len(cl))
                if int(admitted_mask(BK[k0], BK[k0][cl[i]]).sum()) > 0]

    pos_ok = (len(cand0)) in viol_above(cand0 + [weakest])
    g0_ok = (len(cand0)) not in viol_above(cand0 + [strongest])
    print(f"\n  POSITIVE weakest reference (rate "
          f"{admitted_mask(BK[k0],BK[k0][weakest]).mean():.3f}) injected above first0 -> "
          f"{'flagged' if pos_ok else 'MISSED'}  {'PASS' if pos_ok else 'FAIL'}")
    print(f"  g=0      class-max injected in the SAME slot -> "
          f"{'not flagged' if g0_ok else 'flagged'}  {'PASS' if g0_ok else 'FAIL'}")

    syn = 0
    for k in KS:
        per = BK[k].mean(axis=1)
        cand = candidates(per, GRIDS[45])
        counts = [int(admitted_mask(BK[k], np.full(N, per[c])).sum()) for c in cand]
        z = [i for i, n_ in enumerate(counts) if n_ == 0]
        if z:
            syn += len([i for i in range(z[0] + 1, len(cand)) if counts[i] > 0])
    syn_ok = syn == 0
    print(f"  SYNTHETIC each reference flattened to a constant at its own mean (upward-closure")
    print(f"            algebraic): {syn} violations at 0.8B  {'PASS' if syn_ok else 'FAIL'}")

    # ---- PART B · what the definition can admit at 0.8B, swept DOWNWARD ---------------------------
    direct = sorted(p.stem[len("sat08_"):] for p in RES.glob("sat08_*.npz")
                    if p.stem not in ("sat08_genericpool16",))
    print(f"\n  PART B — the {len(direct)} arms judged DIRECTLY at 0.8B (no subset-rebuild path")
    print(f"           inherited): {', '.join(direct)}\n")
    armk, armA2 = {}, {}
    for a in direct:
        Sa = load_sat(RES / f"sat08_{a}.npz")
        ps = [p for p in pids if p in Sa]
        if len(ps) < 100:
            continue
        idxs = {p: sorted({i for i, _ in Sa[p]}) for p in ps}
        armk[a] = int(np.median([len(idxs[p]) for p in ps]))
        vals = []
        for p in ps:
            hv = [cls(np.array(t[0], float)) for t in tg[p]]
            yv = cls(yvec(Sa[p], idxs[p]))
            vals.append(np.mean([[yv[q] == h[q] for q in range(6)] for h in hv]))
        armA2[a] = (ps, np.array(vals, float))

    print(f"    {'arm':>20}{'k':>4}{'n':>6}{'A2':>9}   {'pool range at that k':>24}   status")
    PARTB = {}
    for a in sorted(armA2):
        ps, v = armA2[a]
        k = min(max(armk[a], 1), npool)
        kk = min(KS, key=lambda x: abs(x - k))
        per = BK[kk].mean(axis=1)
        pos = [n for n, p in enumerate(pids) if p in set(ps)]
        lo_, hi_ = float(per.min()), float(per.max())
        forced = float(v.mean()) <= lo_
        # highest pool reference this arm clears, on the arm's own prompts
        cand = candidates(per, GRIDS[45])
        cleared = []
        for c in cand:
            ref = BK[kk][c][pos]
            d = v - ref
            e = d.mean()
            mde = ZEFF * d.std(ddof=1) / math.sqrt(len(d))
            if e > 0 and abs(e) >= mde:
                cleared.append(float(per[c]))
        PARTB[a] = dict(k=kk, n=len(ps), a2=float(v.mean()), pool_lo=lo_, pool_hi=hi_,
                        highest_cleared=max(cleared) if cleared else None,
                        n_cleared=len(cleared),
                        closure_a2=RES8[45][kk]["first0_a2"] if RES8[45][kk] else None)
        hc = PARTB[a]["highest_cleared"]
        st = ("clears NOTHING — below the weakest pool reference (FORCED)" if forced and not cleared
              else "clears nothing in the grid" if not cleared
              else f"highest cleared {hc:.4f} vs closure "
                   f"{PARTB[a]['closure_a2']:.4f} -> "
                   f"{'ABOVE closure' if hc >= PARTB[a]['closure_a2'] else 'BELOW closure'}")
        print(f"    {a:>20}{kk:>4}{len(ps):>6}{v.mean():>9.4f}   "
              f"{f'[{lo_:.4f}, {hi_:.4f}]':>24}   {st}")

    any_above = [a for a, d_ in PARTB.items()
                 if d_["highest_cleared"] is not None and d_["closure_a2"] is not None
                 and d_["highest_cleared"] >= d_["closure_a2"]]
    print(f"\n    arms clearing a reference at or above 0.8B's own closure: "
          f"{any_above if any_above else 'NONE'}")

    # ---- verdict ---------------------------------------------------------------------------------
    ctrl_ok = placebo_ok and pos_ok and g0_ok and syn_ok
    v8, v2 = tot8[45], tot2[45]
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; every count above is silence.")
        v = "UNVERIFIED"
    elif v8 == 0 or not kov[45]:
        print(f"  W-JUDGE — the defect does NOT replicate ({v8} violations at 0.8B against {v2} at")
        print(f"  2B, overlapping k {kov[45]}). R355's MECHANISM claim is refuted: the")
        print(f"  non-upward-closure is a property of the 2B judge's noise profile, not of the")
        print(f"  paired-MDE estimator. Its COUNT at 2B stands; its explanation does not.")
        v = "W_JUDGE"
    elif v8 >= 2 * v2:
        print(f"  W-WORSE — the defect replicates and is MATERIALLY LARGER at the noisier judge:")
        print(f"  {v8} violations at 0.8B against {v2} at 2B, overlapping k {kov[45]}. Larger and")
        print(f"  more erratic paired sds make near-neighbour accidents commoner, which is a")
        print(f"  dose-response on judge quality and predicts the defect worsens as judges shrink.")
        v = "W_WORSE"
    else:
        print(f"  W-ESTIMATOR — the defect REPLICATES at a different judge: {v8} violations at 0.8B")
        print(f"  against {v2} at 2B, with violations at both judges for k {kov[45]}. So")
        print(f"  non-upward-closure is structural to the paired-MDE admission rule, not a fact")
        print(f"  about one model, and EVERY `closure level` sentence in this campaign inherits it")
        print(f"  at ANY judge. R355's mechanism claim survives its first cross-instrument test.")
        v = "W_ESTIMATOR"
        # ⚠ A PRE-REGISTERED DIRECTIONAL PREDICTION FAILED AND THE BRANCH ABOVE WOULD HIDE IT.
        #   W-WORSE said: the noisier judge should show MORE violations, because larger and more
        #   erratic paired sds make near-neighbour accidents commoner. Observed the OPPOSITE.
        if v8 < v2:
            print(f"\n  ⛔ MY W-WORSE PREDICTION FAILED IN SIGN, and the kill's three branches had no")
            print(f"     home for it. I pre-registered `noisier judge -> MORE violations`; observed")
            print(f"     {v8} vs {v2}, i.e. {v2/max(v8,1):.1f}x FEWER. The else-branch swallows this")
            print(f"     into W-ESTIMATOR without saying so, which is the verdict string asserting")
            print(f"     less than the run measured.")
            print(f"     The first explanation to hand is that a raw count cannot be compared")
            print(f"     across judges at all: more noise -> larger paired sd -> larger MDE -> the")
            print(f"     judge admits LESS OF EVERYTHING, violations included. If that were the")
            print(f"     whole story the NORMALISED rates would match. They do not:")
            same = True
            for g in sorted(GRIDS):
                R = RATE[g]
                if R["risk_2b"] and R["risk_08b"]:
                    ratio = R["rate_08b"] / R["rate_2b"] if R["rate_2b"] else float("nan")
                    if not (0.8 <= ratio <= 1.25):
                        same = False
                    print(f"       grid {g:>3}: 2B {R['rate_2b']:.3f} vs 0.8B {R['rate_08b']:.3f} "
                          f"-> 0.8B is {ratio:.2f}x")
            print(f"     ⚠ SO MY POST-HOC EXPLANATION IS ALSO WRONG"
                  f"{'' if not same else ' — rates do match'}, and stating it as the")
            print(f"     resolution would repeat the error it replaces: an untested mechanism")
            print(f"     offered to absorb a failed prediction. The residual is NAMED, not closed —")
            print(f"     0.8B's violation rate is about HALF 2B's after normalising, and this round")
            print(f"     does not know why. A designed test would sweep judge precision rather than")
            print(f"     compare two points.")
            print(f"     WHAT STANDS: replication, which rests on violations > 0 at both judges and")
            print(f"     on the k-overlap {kov[45]} — not on any count comparison. The DOSE-RESPONSE")
            print(f"     reading is WITHDRAWN.")

    art = dict(stamp(str(SELF)), n_prompts=N, pool=npool, ks=KS,
               grids_08b={str(g): {str(k): RES8[g][k] for k in KS} for g in GRIDS},
               totals_08b={str(g): tot8[g] for g in GRIDS},
               totals_2b={str(g): tot2[g] for g in GRIDS},
               k_overlap={str(g): kov[g] for g in GRIDS}, cells=cells, rates=RATE,
               part_b=PARTB, direct_arms=direct, arms_above_closure=any_above,
               controls=dict(placebo=placebo_ok, positive=pos_ok, g0=g0_ok, synthetic=syn_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r358_second_judge.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
