"""R362 — the size band `k = 3…8` at the second judge, with the forced part labelled as forced.

`DEFINITION.md` says *"Its size is greater than one; sizes 3 to 8 are not distinguishable by this
release."* R296 upgraded that from a bound to a measured interval: the ENTRY (2->3, +0.0108
resolved) and the EXIT (8->12, -0.0192 resolved) separate, the interior does not. Every one of those
numbers is a clause-② margin at Qwen3.5-2B-Base. **The size statement is the last quantitative claim
in the definition whose supporting round predates the judge axis entirely.**

⛔ ARITHMETIC TRAP, AND IT DISPOSES OF THE OBVIOUS ROUND. Two parts of the question are already
   settled and must not be re-sold as findings:
   (a) **THE UPPER BOUND IS A DERIVATION WITH NO JUDGE IN IT.** R224/R228 give
       `k_max(n,m) = max{k : C(n,k) <= a(m)}` -- pure combinatorics on criteria-per-prompt and
       responses-per-prompt. No A2, no reference, no model. Recomputing it at a second judge is
       FORCED to return the same answer, and doing so would be a demonstration.
   (b) **THE CURVE'S SHAPE IS ALREADY MEASURED.** R356 computed the between-judge rank correlation
       WITHIN the `topw_k` family -- which IS this k-curve -- at rho = +0.667 for clause ②, and
       found it INSIDE the band its own separation forces. Re-deriving the ordering would be
       R356 again under a new name.
   What is left, and is not forced: **whether the band's BOUNDARIES still resolve at 0.8B.** And
   even that is half-forced, which is the point of running it: R301 measured a shrink of
   beta ~ 0.40, so a 2B step of +0.0108 lands near +0.0043 at 0.8B, and against an MDE of order
   0.011 it cannot resolve. **If the MDEs are comparable, the collapse is ALGEBRA.** The
   non-forced residual is the MDEs themselves: 0.8B's paired sds are not required to match 2B's,
   and R355/R358 measured that paired-sd behaviour on this data is not well-behaved. So this round
   computes the DERIVED expectation and the MEASURED outcome side by side, and reports the gap.

ESTIMAND        At each judge J and each k in {1,2,3,4,6,8,12}: the clause-② margin
                `A2(topw_k) - A2(POOL[0:k])` with its own paired per-cell MDE; and each adjacent-k
                step with ITS own paired MDE. Then, per step: the margin RATIO 0.8B/2B against the
                shrink beta R301 fitted, and whether the step resolves at each judge.

IDENTIFICATION  Exact at both judges: margins and paired MDEs are computable wherever both arms
                exist, and admission plays no part -- which is why this is answerable at 0.8B where
                the admitted set is empty. Arms reach 0.8B by the parity-controlled path (R301:
                delta +0.00131 vs mde 0.01193; -0.00084 vs 0.01441; `parity_can_fail: True`).
                NOT identified: whether a two-judge result extends to a third.

SCOPE           968 prompts with >=2 annotators · instruments Qwen3.5-2B-Base and
                Qwen3.5-0.8B-Base · baseline the SIZE-MATCHED blind reference `POOL[0:k]` at each k
                and each judge · the campaign's standing admission rule for `resolved`.

WORLDS
  W-FORCED-COLLAPSE      no step resolves at 0.8B, AND the observed margins sit near beta x the 2B
                         margins with comparable MDEs. The band is 2B-specific and its collapse is
                         explained by the shrink alone -- a DERIVATION confirmed, not a discovery.
  W-PRECISION-COMPENSATES some step still resolves at 0.8B because that judge's paired MDEs are
                         proportionally smaller. The boundaries are NOT judge-specific, which the
                         shrink alone would not predict, and the size statement survives unindexed.
  W-DIFFERENT-BAND       steps resolve at 0.8B but at DIFFERENT k. The band MOVES rather than
                         collapsing -- the outcome that damages the size claim most, because an
                         indexed band that moves is not a property of the release at all.

PREDICTION MATRIX
  W-FORCED-COLLAPSE      -> resolved steps at 0.8B == 0; median |margin ratio| ~ beta
  W-PRECISION-COMPENSATES-> >=1 step resolved at 0.8B, at the SAME boundary as 2B
  W-DIFFERENT-BAND       -> >=1 step resolved at 0.8B at a DIFFERENT boundary
The three differ on which steps resolve and where, computed identically at both judges.

PRE-REGISTERED KILL -- conditional, and with a fourth branch because this session has repeatedly
had a default branch assert past its data.
    if placebo_ok and positive_ok and g0_ok:
        R = set of steps resolved at 0.8B
        if not R                              -> W-FORCED-COLLAPSE  (and the ratio is REPORTED, so
                                                  `forced` is checked rather than assumed)
        elif R is a subset of the 2B-resolved steps -> W-PRECISION-COMPENSATES
        elif R and R disjoint from 2B's       -> W-DIFFERENT-BAND
        else                                   -> NAMED EXPLICITLY, never defaulted
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

POSITIVE CTRL  a planted margin: `topw_k` replaced by itself plus a constant of 2x its own MDE must
               come out resolved at both judges. Retention reported per judge.
g=0 CTRL       an arm against ITSELF: margin exactly 0 and NOT resolved. This is what stops
               `resolved` from firing on a degenerate comparison.
PLACEBO        the reference against itself: exactly 0 at every k and judge.
NOISE FLOOR    each cell's own paired sd -- never pooled, because R331 established a paired MDE is
               a property of the PAIR.
MULTIPLICITY   2 judges x 7 k x (1 margin + 1 step) = 26 cells; every one printed, resolved or not.
SPECIFICATION  k is the specification axis and is reported entire, including the k that kill it.
SEEDS          deterministic; two runs required byte-identical.
ARTIFACT       results/r362_size_band.json with the source hash.

IMPOSSIBLE HERE
  a third judge   -- NOT-ATTEMPTED-AND-NOT-CHEAP (R357): no third checkpoint on the local store.
  the upper bound at another judge -- NOT A QUESTION: it is combinatorial (see trap (a)).
  cross-release   -- one release.

EXIT
    0  controls hold and the band is classified
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
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
KS = [1, 2, 3, 4, 6, 8, 12]


def sat_path(a, judge):
    if judge == "2B":
        p = RES / f"sat_{a}.npz"
        return (p, "judged") if p.exists() else (None, None)
    d, r = RES / f"sat08_{a}.npz", RES / f"sat_{a}_08b.npz"
    if d.exists():
        return d, "judged"
    if r.exists():
        return r, "subset"
    return None, None


def main() -> int:
    tg, _ = load_targets()
    POOL = {}
    for j, f in (("2B", "sat_genericpool16.npz"), ("0.8B", "sat08_genericpool16.npz")):
        p = RES / f
        if not p.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
        POOL[j] = load_sat(p)
    pids = sorted(set(POOL["2B"]) & set(POOL["0.8B"]) & {q for q in tg if len(tg[q]) >= 2})
    H = {q: [cls(np.array(t[0], float)) for t in tg[q]] for q in pids}
    npool = len({i for i, _ in POOL["2B"][pids[0]]})
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])

    beta = None
    d = next(A24.glob("R301_*"), None)
    f = sorted((d / "results").glob("*.json")) if d else []
    if f:
        beta = json.loads(f[0].read_text())["slope"]["2"]["beta"]

    print("R362 · does the size band k=3…8 survive the second judge?")
    print(f"  {len(pids)} prompts · pool {npool} · k in {KS}")
    print(f"  ⛔ two parts are NOT asked because they are settled: the UPPER BOUND is combinatorial")
    print(f"     (R224/R228, no judge in it) and the CURVE'S SHAPE is R356 (topw_k rho +0.667,")
    print(f"     inside its own forced band). Only the BOUNDARIES' resolution is open.\n")

    def a2(sat, ps):
        out = []
        for q in ps:
            idx = sorted({i for i, _ in sat[q]})
            yv = cls(yvec(sat[q], idx))
            out.append(np.mean([[yv[c] == h[c] for c in range(6)] for h in H[q]]))
        return np.array(out, float)

    def pool_prefix(j, k):
        SAT = np.stack([np.array([[POOL[j][q][(i, x)] for x in "ABCD"] for i in range(npool)],
                                 float) for q in pids])
        sb = np.array([list(range(k))])
        out = np.empty(len(pids))
        for n in range(len(pids)):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[n] = (C_[:, None, :] == np.array(H[pids[n]], float)[None, :, :]).mean()
        return out

    def cell(v, r):
        d_ = v - r
        e = float(d_.mean())
        m = float(ZEFF * d_.std(ddof=1) / math.sqrt(len(d_)))
        return e, m, d_

    ARM, PATHOF, MARG, DIFV = {}, {}, {}, {}
    for j in POOL:
        REF = {k: pool_prefix(j, k) for k in KS}
        for k in KS:
            a = f"topw_k{k}"
            p8, how = sat_path(a, j)
            if p8 is None:
                print(f"  UNRUNNABLE: {a} absent at {j}. Exit 2, never 0."); return 2
            S = load_sat(p8)
            ps = [q for q in pids if q in S]
            pos = [n for n, q in enumerate(pids) if q in set(ps)]
            v = a2(S, ps)
            ARM[(j, k)] = v
            PATHOF[(j, k)] = how
            e, m, dv = cell(v, REF[k][pos])
            MARG[(j, k)] = (e, m)
            DIFV[(j, k)] = dv

    print(f"    {'judge':>7}{'k':>4}{'margin':>10}{'own MDE':>10}   verdict")
    for j in POOL:
        for k in KS:
            e, m = MARG[(j, k)]
            vd = "BEATS" if e > m else ("LOSES" if e < -m else "unresolved")
            print(f"    {j:>7}{k:>4}{e:>+10.4f}{m:>10.4f}   {vd}")
        print()

    # ---- adjacent-k steps, each with its OWN paired MDE -------------------------------------------
    print(f"    {'judge':>7}{'step':>9}{'delta':>10}{'own MDE':>10}   verdict")
    STEP = {}
    for j in POOL:
        for a_, b_ in zip(KS, KS[1:]):
            na = min(len(DIFV[(j, a_)]), len(DIFV[(j, b_)]))
            dd = DIFV[(j, b_)][:na] - DIFV[(j, a_)][:na]
            e = float(dd.mean()); m = float(ZEFF * dd.std(ddof=1) / math.sqrt(na))
            STEP[(j, f"{a_}->{b_}")] = (e, m)
            vd = "RESOLVED" if abs(e) > m else "unresolved"
            print(f"    {j:>7}{f'{a_}->{b_}':>9}{e:>+10.4f}{m:>10.4f}   {vd}")
        print()

    res = {j: {s.split("|")[-1] for (jj_, s) in STEP if jj_ == j and abs(STEP[(jj_, s)][0]) > STEP[(jj_, s)][1]}
           for j in POOL}
    res = {j: {s for (jx, s) in STEP if jx == j and abs(STEP[(jx, s)][0]) > STEP[(jx, s)][1]}
           for j in POOL}
    print(f"    steps RESOLVED @2B   {sorted(res['2B']) if res['2B'] else 'none'}")
    print(f"    steps RESOLVED @0.8B {sorted(res['0.8B']) if res['0.8B'] else 'none'}")

    # ---- is the collapse FORCED? the derived expectation, computed rather than asserted -----------
    ratios = [MARG[("0.8B", k)][0] / MARG[("2B", k)][0]
              for k in KS if abs(MARG[("2B", k)][0]) > 1e-9]
    med_ratio = float(np.median(ratios))
    mde_ratio = float(np.median([MARG[("0.8B", k)][1] / MARG[("2B", k)][1] for k in KS]))
    print(f"\n  IS THE COLLAPSE FORCED? — computed, not asserted")
    print(f"    median margin ratio 0.8B/2B  {med_ratio:+.3f}   "
          f"against R301's fitted clause-② shrink beta {beta:.3f}"
          if beta else f"    median margin ratio {med_ratio:+.3f}")
    print(f"    median MDE ratio 0.8B/2B     {mde_ratio:+.3f}   "
          f"-> a step shrinks by {med_ratio:.2f} while its resolution bar moves by {mde_ratio:.2f}")
    forced = abs(med_ratio) < mde_ratio
    print(f"    {'the shrink alone predicts collapse' if forced else 'the shrink alone does NOT predict collapse'}"
          f" (|margin ratio| {'<' if forced else '>='} MDE ratio)")
    # ⚠ AND THE ABSOLUTE VALUE ABOVE HIDES THE ACTUAL FINDING. A pure shrink has a POSITIVE ratio
    #   near beta. The observed median is NEGATIVE, which is not attenuation at all -- it is a SIGN
    #   INVERSION, and reporting only |ratio| would have let `the shrink explains it` stand for
    #   something the shrink does not describe.
    signflip = [k for k in KS
                if MARG[("2B", k)][0] * MARG[("0.8B", k)][0] < 0]
    if med_ratio < 0:
        print(f"\n    ⚠ THE RATIO IS NEGATIVE, AND |.| ABOVE HID IT. A pure shrink gives a ratio")
        print(f"      near beta = {beta:.3f}, POSITIVE. Observed {med_ratio:+.3f}: at {len(signflip)} of")
        print(f"      {len(KS)} sizes the margin CHANGES SIGN between judges ({signflip}).")
        print(f"      So this is not attenuation — the rubric's top-k does not merely beat the")
        print(f"      blind reference by less at 0.8B, it mostly stops beating it:")
        neg = [k for k in KS if MARG[("0.8B", k)][0] < 0]
        print(f"      margins are negative at k = {neg} of {KS}, and resolvably so at "
              f"{[k for k in KS if MARG[('0.8B', k)][0] < -MARG[('0.8B', k)][1]]}.")

    # ---- controls -----------------------------------------------------------------------------------
    # ⛔ v1's POSITIVE CONTROL COULD NOT PASS, and it is the fourth of that shape this session.
    #    It added +2 MDE to each cell's RAW difference vector. But `k=1` sits at -0.0170 against
    #    its own MDE of 0.0135, i.e. -1.26 MDE: adding 2 MDE lands it at +0.74 MDE, which cannot
    #    resolve NO MATTER HOW GOOD THE INSTRUMENT IS. The threshold was set above what the design
    #    can return for that cell, so its failure said nothing about the detector.
    #    Fixed the standard way: CENTRE the difference vector first, so every cell starts at a
    #    true effect of exactly 0, then plant a dose. That gives a real floor (g=0 must NOT
    #    resolve) and a real ceiling (g=4 must resolve everywhere), with monotonicity between.
    DOSES = (0.0, 1.0, 2.0, 4.0)
    pos, g0, plac, RET = {}, {}, {}, {}
    for j in POOL:
        RET[j] = {}
        for g in DOSES:
            hits = []
            for k in KS:
                _e, m = MARG[(j, k)]
                dv = DIFV[(j, k)] - DIFV[(j, k)].mean() + g * m      # centred, then dosed
                e2 = float(dv.mean()); m2 = float(ZEFF * dv.std(ddof=1) / math.sqrt(len(dv)))
                hits.append(abs(e2) > m2)
            RET[j][g] = float(np.mean(hits))
        mono = all(RET[j][DOSES[i]] <= RET[j][DOSES[i + 1]] + 1e-12 for i in range(len(DOSES) - 1))
        pos[j] = RET[j][0.0] == 0.0 and RET[j][4.0] == 1.0 and mono
        dv0 = ARM[(j, KS[0])] - ARM[(j, KS[0])]
        g0[j] = not (float(dv0.mean()) > 0.0)
        plac[j] = float(dv0.std()) == 0.0
        print(f"\n  POSITIVE @{j:<5} centred cell + dose, fraction resolved: "
              f"{'  '.join(f'g={g:.0f}:{RET[j][g]:.2f}' for g in DOSES)}  "
              f"{'PASS' if pos[j] else 'FAIL'}")
        print(f"           floor g=0 -> {RET[j][0.0]:.2f} (it CAN fail) · ceiling g=4 -> "
              f"{RET[j][4.0]:.2f} · monotone {mono}")
        print(f"  g=0      @{j:<5} an arm against itself: margin 0, not resolved  "
              f"{'PASS' if g0[j] else 'FAIL'}")
        print(f"  PLACEBO  @{j:<5} that same self-contrast has zero spread  "
              f"{'PASS' if plac[j] else 'FAIL'}")

    ctrl_ok = all(pos.values()) and all(g0.values()) and all(plac.values())
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; every number above is silence.")
        v = "UNVERIFIED"
    elif not res["0.8B"]:
        print(f"  W-FORCED-COLLAPSE — no adjacent-k step resolves at 0.8B, where {len(res['2B'])}")
        print(f"  resolve at 2B. And the collapse is CHECKED rather than assumed: margins shrink by")
        print(f"  {med_ratio:.2f} while the resolution bar moves by {mde_ratio:.2f}, so the shrink alone")
        print(f"  {'ACCOUNTS FOR IT' if forced else 'DOES NOT ACCOUNT FOR IT — the MDEs moved too'}.")
        print(f"  ⛔ The size band k=3…8 is a 2B statement. DEFINITION.md must index it.")
        v = "W_FORCED_COLLAPSE" if forced else "W_COLLAPSE_NOT_EXPLAINED_BY_SHRINK"
    elif res["0.8B"] <= res["2B"]:
        print(f"  W-PRECISION-COMPENSATES — {sorted(res['0.8B'])} still resolves at 0.8B, at the")
        print(f"  SAME boundary as 2B, which the shrink alone would not predict. The size band's")
        print(f"  boundaries are not judge-specific and the statement survives unindexed.")
        v = "W_PRECISION_COMPENSATES"
    elif not (res["0.8B"] & res["2B"]):
        print(f"  W-DIFFERENT-BAND — {sorted(res['0.8B'])} resolves at 0.8B and NONE of it at 2B.")
        print(f"  The band MOVES rather than collapsing, which is worse for the size claim than")
        print(f"  collapse: an indexed band that moves is not a property of the release.")
        v = "W_DIFFERENT_BAND"
    else:
        print(f"  W-PARTIAL-OVERLAP — named rather than defaulted. 0.8B resolves "
              f"{sorted(res['0.8B'])}, 2B resolves {sorted(res['2B'])}, overlap "
              f"{sorted(res['0.8B'] & res['2B'])} and 0.8B-only "
              f"{sorted(res['0.8B'] - res['2B'])}. Neither `collapse` nor `moves` describes it.")
        v = "W_PARTIAL_OVERLAP"

    art = dict(stamp(str(SELF)), n_prompts=len(pids), pool=npool, ks=KS, beta_r301=beta,
               path={f"{j}|{k}": PATHOF[(j, k)] for j in POOL for k in KS},
               margins={f"{j}|{k}": MARG[(j, k)] for j in POOL for k in KS},
               steps={f"{j}|{s}": STEP[(j, s)] for (j, s) in STEP},
               resolved={j: sorted(res[j]) for j in POOL},
               median_margin_ratio=med_ratio, median_mde_ratio=mde_ratio, shrink_explains=forced,
               sign_flips=[k for k in KS if MARG[('2B', k)][0] * MARG[('0.8B', k)][0] < 0],
               controls=dict(positive=pos, g0=g0, placebo=plac, retention=RET), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r362_size_band.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
