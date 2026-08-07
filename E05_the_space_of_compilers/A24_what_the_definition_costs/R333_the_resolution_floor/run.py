"""R333 — the annotator axis was exhausted 26 rounds ago, and the floor it leaves is the real limit.

R332 closed by naming the next gradient: "the release ships a median of 16 annotators per prompt and
every A2 here samples ONE, so the cheapest available precision gain is the annotator axis." That is
false twice over, and both refutations were one read away:

  (1) `load_targets()` returns EVERY assessment, and R331/R332 build H[n] from all of tg[p] and
      average over it. Mean 16.1 annotators per prompt, 15,593 annotations. Nothing samples one.
  (2) R306 -- "the table at every annotator" -- performed exactly this migration TWENTY-SIX ROUNDS
      AGO, and its own docstring says so: "every number in this campaign used 3 ... use every
      annotator, so the estimate is the release's rather than a draw's."

§4 records that a `next gradient` sentence is the highest-risk line in a report and that its
direction is not systematic -- one excuses work, one manufactures it. This one MANUFACTURED it: the
round I proposed would have measured nothing. So this round asks the question that survives the
correction, which is the opposite one.

WHAT SURVIVES. If the annotator axis is already spent, what bounds the resolution? The two-level
decomposition makes it explicit and separable:

    MDE(N, m) = ZEFF * sqrt(sigma_b^2 + sigma_w^2 / m) / sqrt(N)

The m axis shrinks only the second term, so it is BOUNDED BELOW by ZEFF*sigma_b/sqrt(N) -- a floor no
amount of annotation can cross. The N axis shrinks everything. So the question "can this design ever
resolve R332's 0.0027 band?" has an exact analytic answer once sigma_b and sigma_w are measured, and
the answer decides whether the campaign's admitted set is a measurable quantity on this release at
all.

⛔ THE ARITHMETIC TRAP, DECLARED FIRST. The 1/sqrt(N) extrapolation is FORCED by the estimator's
algebra -- reporting that MDE falls with N is not a finding. What is NOT forced and is measured:
sigma_b and sigma_w themselves, the SHAPE of the empirical m-curve against the analytic one, and
whether the empirical N-subsampling actually follows 1/sqrt(N) (clustering and prompt heterogeneity
can bend it). The required-N figure is labelled a derivation wherever it appears.

ESTIMAND      (i) sigma_b and sigma_w of the paired clause-2 difference, per boundary arm;
              (ii) the MDE surface over (N prompts x m annotators-per-prompt), empirical by
              subsampling and analytic from the decomposition, required to agree;
              (iii) the m -> infinity floor, and the N at which the floor reaches R332's band width
              of 0.0027.
IDENTIFICATION Exact for sigma_b, sigma_w and the surface. The required-N is a DERIVATION under the
              assumption that sigma_b is a property of the population rather than of these 968
              prompts -- stated, and its direction of error noted: if the release's prompts are
              more homogeneous than the population, required-N is understated.
SCOPE         population 968 CoVal prompts with >=2 annotators, 15,593 annotations · instrument
              Qwen3.5-2B-Base under R234's canonical builder · baseline the k-matched first-k
              subset of the generic pool (R294's published reference) · regime per-annotator
              agreement over the 6 pairwise comparisons.
WORLDS        W-ANNOTATOR-LEFT  the m-curve still falls materially between m=16 and m=infinity ->
                                more annotation per prompt would help and R306's migration did not
                                exhaust the axis.
              W-PROMPT-BOUND    the m-curve is within a few percent of its floor at m=16, and the
                                required N to reach 0.0027 is far beyond 968 -> the admitted set is
                                STRUCTURALLY unresolvable on this release, which is a register
                                entry and not a to-do.
              W-REACHABLE       required N <= 968, i.e. the band is already resolvable and R332's
                                instability comes from something other than sample size.
KILL          pre-registered, conditional on the controls:
                MDE(N=968, m=inf) / MDE(N=968, m=16) < 0.90     -> W-ANNOTATOR-LEFT
                else required_N <= 968                          -> W-REACHABLE
                else                                            -> W-PROMPT-BOUND
POSITIVE CTRL at (N=968, m=all) the empirical MDE must reproduce the MDE this campaign publishes
              for the same arm/reference pair, to 1e-12. If the decomposition's parent statistic is
              not the published one, nothing downstream is about the published table.
              And it FAILS at g=0: at m=1 the MDE must be STRICTLY larger than at m=all, or the
              annotator knob is dead and the whole surface is one number repeated.
NEGATIVE CTRL a SYNTHETIC world where sigma_w is zero BY CONSTRUCTION: replace every annotator's
              ranking within a prompt by that prompt's modal ranking. The m-curve must then be
              EXACTLY flat and the estimated sigma_w must be ~0. This is the world the rival
              predicts -- "the m axis does nothing because within-prompt noise is negligible" --
              built rather than argued.
PLACEBO       the subsampler at (N=968, m=all) against the unsubsampled computation: exactly 0.
NOISE FLOOR   the across-seed spread of each surface cell, printed beside it.
MULTIPLICITY  |N grid| x |m grid| x |arms| cells, all printed; no hypothesis test is performed, so
              no correction is due and that is stated rather than silently skipped.
SPECIFICATION the surface IS the curve; both the empirical and the analytic version are published,
              including the cells where they disagree.
SEEDS         3 subsample seeds; every cell reported with its across-seed spread.
ARTIFACT      results/resolution_floor.json with source hash.
IMPOSSIBLE    - more prompts. The release ships 968 with >=2 annotators; N is fixed by the site.
              - establishing sigma_b for the POPULATION rather than for this release, which needs a
                second release. Named, and it is what the required-N derivation rests on.
"""
from __future__ import annotations
import collections, hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

SELF = pathlib.Path(__file__).resolve()
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
SEEDS = (0, 1, 2)
BAND = 0.0027                                   # R332's closure-to-readingA band width
ARMS = ("coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8")
N_FRAC = (0.10, 0.25, 0.50, 0.75, 1.00)
M_GRID = (1, 2, 4, 8, 16, 0)                    # 0 = every annotator the prompt has


def load_json(pat):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def main() -> int:
    r294 = load_json("R294_*")
    if r294 is None:
        print("  UNRUNNABLE: R294 absent."); return 2
    rows = r294["rows"]

    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    ARMSAT = {}
    for a in ARMS:
        f = ROOT / "corebench" / "results" / f"sat_{a}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: sat_{a}.npz absent."); return 2
        ARMSAT[a] = load_sat(f)
    pids = sorted(set(S) & set.intersection(*(set(v) for v in ARMSAT.values())) &
                  {p for p in tg if len(tg[p]) >= 2})
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[pids[n]]], float) for n in range(N)]
    mcount = np.array([len(h) for h in H])
    print(f"  {N} prompts · {int(mcount.sum())} annotations · median {int(np.median(mcount))} "
          f"per prompt · pool {npool}\n")

    # ---- per-annotator agreement vectors, arm and k-matched reference ---------------------------
    def ref_cls(k):
        sel = list(range(min(k, npool)))
        out = []
        for n, p in enumerate(pids):
            Y = np.array([[S[p][(i, x)] for x in "ABCD"] for i in sel], float).sum(axis=0)
            out.append(np.sign(np.array([Y[i] - Y[j] for i, j in PAIRS])))
        return out

    REFC = {k: ref_cls(k) for k in sorted({min(rows[a]["k"], npool) for a in ARMS})}

    D = {}                                       # arm -> list of per-annotator difference arrays
    for a in ARMS:
        k = min(rows[a]["k"], npool)
        rc = REFC[k]
        per = []
        for n, p in enumerate(pids):
            ac = cls(yvec(ARMSAT[a][p], sorted({i for i, _ in ARMSAT[a][p]})))
            arm_agree = np.array([[ac[c] == h[c] for c in range(6)] for h in H[n]], float).mean(1)
            ref_agree = np.array([[rc[n][c] == h[c] for c in range(6)] for h in H[n]], float).mean(1)
            per.append(arm_agree - ref_agree)
        D[a] = per

    def decompose(per):
        mu = np.array([v.mean() for v in per])
        sb2 = float(mu.var(ddof=1))
        wv = np.array([v.var(ddof=1) if len(v) > 1 else 0.0 for v in per])
        sw2 = float(wv.mean())
        # sigma_b^2 is inflated by sigma_w^2/m_p inside each prompt mean; remove it
        sb2_c = max(sb2 - float(np.mean(wv / np.maximum([len(v) for v in per], 1))), 0.0)
        return math.sqrt(sb2_c), math.sqrt(sw2), mu

    print(f"  VARIANCE DECOMPOSITION of the paired clause-2 difference\n")
    print(f"    {'arm':<14}{'k':>3}{'effect':>10}{'sigma_b':>10}{'sigma_w':>10}"
          f"{'MDE(968,all)':>14}{'floor m→∞':>12}{'m=16 / floor':>14}")
    DEC = {}
    for a in ARMS:
        sb, sw, mu = decompose(D[a])
        mde_all = ZEFF * mu.std(ddof=1) / math.sqrt(N)
        floor = ZEFF * sb / math.sqrt(N)
        mde16 = ZEFF * math.sqrt(sb ** 2 + sw ** 2 / 16) / math.sqrt(N)
        DEC[a] = dict(sb=sb, sw=sw, eff=float(mu.mean()), mde_all=float(mde_all),
                      floor=float(floor), mde16=float(mde16),
                      ratio=float(mde16 / floor) if floor > 0 else float("inf"))
        print(f"    {a:<14}{min(rows[a]['k'], npool):>3}{mu.mean():>+10.4f}{sb:>10.4f}{sw:>10.4f}"
              f"{mde_all:>14.4f}{floor:>12.4f}{mde16/floor:>14.3f}")

    # ---- POSITIVE CTRL · reproduce the published MDE for the same pair --------------------------
    pub = {a: rows[a]["mde2"] for a in ARMS}
    dev = {a: abs(DEC[a]["mde_all"] - pub[a]) for a in ARMS}
    pos_ok = max(dev.values()) < 1e-12
    print(f"\n  POSITIVE CTRL  reproduce R294's committed mde2 for the same arm/reference pair")
    for a in ARMS:
        print(f"    {a:<14}{DEC[a]['mde_all']:.12f}  vs committed {pub[a]:.12f}   "
              f"{'PASS' if dev[a] < 1e-12 else f'FAIL by {dev[a]:.2e}'}")

    # ---- the surface ------------------------------------------------------------------------------
    def mde_cell(per, n_take, m_take, seed):
        rng = np.random.default_rng(31337 + 977 * seed + 13 * n_take + m_take)
        idx = rng.choice(len(per), n_take, replace=False) if n_take < len(per) else np.arange(len(per))
        mu = []
        for i in idx:
            v = per[i]
            if m_take and m_take < len(v):
                v = v[rng.choice(len(v), m_take, replace=False)]
            mu.append(v.mean())
        mu = np.array(mu)
        return ZEFF * mu.std(ddof=1) / math.sqrt(len(mu))

    print(f"\n  MDE SURFACE — `coval_core`, empirical subsampling, {len(SEEDS)} seeds "
          f"(0 = every annotator)\n")
    print("    " + f"{'N':>6}" + "".join(f"{'m='+ (str(m) if m else 'all'):>12}" for m in M_GRID))
    surf = {}
    for f_ in N_FRAC:
        n_take = max(3, int(round(f_ * N)))
        cells = []
        for m in M_GRID:
            vals = [mde_cell(D["coval_core"], n_take, m, s) for s in SEEDS]
            surf[(n_take, m)] = (float(np.mean(vals)), float(np.std(vals)))
            cells.append(f"{np.mean(vals):.4f}")
        print(f"    {n_take:>6}" + "".join(f"{c:>12}" for c in cells))
    print("    " + f"{'sd@N=968':>6}" + "".join(f"{surf[(N, m)][1]:>12.5f}" for m in M_GRID))

    g0_ok = surf[(N, 1)][0] > surf[(N, 0)][0]
    print(f"\n    g=0 · m=1 MDE {surf[(N,1)][0]:.4f} must exceed m=all {surf[(N,0)][0]:.4f}: "
          f"{'PASS — the annotator knob is alive' if g0_ok else 'FAIL — the surface is one number repeated'}")

    # ---- empirical vs analytic ---------------------------------------------------------------------
    sb, sw = DEC["coval_core"]["sb"], DEC["coval_core"]["sw"]
    print(f"\n  EMPIRICAL vs ANALYTIC at N={N}\n")
    print(f"    {'m':>6}{'empirical':>12}{'analytic':>12}{'ratio':>9}")
    agree = []
    for m in M_GRID:
        me = surf[(N, m)][0]
        mm = float(np.mean(mcount)) if m == 0 else m
        ma = ZEFF * math.sqrt(sb ** 2 + sw ** 2 / mm) / math.sqrt(N)
        agree.append(abs(me / ma - 1.0))
        print(f"    {(str(m) if m else 'all'):>6}{me:>12.4f}{ma:>12.4f}{me/ma:>9.3f}")
    analytic_ok = max(agree) < 0.15
    print(f"    -> max |empirical/analytic - 1| = {max(agree):.3f}  "
          f"{'PASS — the decomposition describes the subsampler' if analytic_ok else 'FAIL — they are different objects'}")

    # ---- NEGATIVE · synthetic world with sigma_w = 0 by construction ------------------------------
    synth = []
    for n in range(N):
        v = D["coval_core"][n]
        synth.append(np.full_like(v, v.mean()))          # every annotator = the prompt's mean
    sb_s, sw_s, _ = decompose(synth)
    flat = [mde_cell(synth, N, m, 0) for m in M_GRID]
    neg_ok = sw_s < 1e-9 and (max(flat) - min(flat)) < 1e-9
    print(f"\n  NEGATIVE CTRL  synthetic world, every annotator replaced by the prompt's mean")
    print(f"    estimated sigma_w = {sw_s:.2e} (must be ~0)   m-curve spread = "
          f"{max(flat)-min(flat):.2e} (must be ~0)   {'PASS' if neg_ok else 'FAIL'}")

    # ---- PLACEBO -----------------------------------------------------------------------------------
    plc = abs(mde_cell(D["coval_core"], N, 0, 0) - DEC["coval_core"]["mde_all"])
    plc_ok = plc < 1e-12
    print(f"  PLACEBO        subsampler at (N=968, m=all) vs the direct computation: {plc:.1e}  "
          f"{'PASS' if plc_ok else 'FAIL'}")

    # ---- the required N ------------------------------------------------------------------------------
    print(f"\n  ⛔ DERIVATION, not a measurement — MDE ∝ 1/sqrt(N) is forced by the estimator.")
    print(f"    Required N for the m→∞ FLOOR to reach R332's band width {BAND}:\n")
    print(f"    {'arm':<14}{'floor@968':>11}{'required N':>13}{'× the release':>15}")
    req = {}
    for a in ARMS:
        fl = DEC[a]["floor"]
        rn = N * (fl / BAND) ** 2
        req[a] = float(rn)
        print(f"    {a:<14}{fl:>11.4f}{rn:>13.0f}{rn/N:>15.1f}")

    ctrl = pos_ok and g0_ok and analytic_ok and neg_ok and plc_ok
    ann_left = DEC["coval_core"]["floor"] / DEC["coval_core"]["mde16"] < 0.90
    reachable = req["coval_core"] <= N
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  g0={g0_ok}  analytic={analytic_ok}  negative={neg_ok}  "
          f"placebo={plc_ok}  -> {'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the resolution floor is not readable.")
    elif ann_left:
        world = "W-ANNOTATOR-LEFT"
        print(f"  -> W-ANNOTATOR-LEFT. The floor is "
              f"{DEC['coval_core']['floor']/DEC['coval_core']['mde16']:.2f} of the m=16 MDE, so more")
        print("     annotation per prompt still buys precision and R306's migration did not")
        print("     exhaust the axis.")
    elif reachable:
        world = "W-REACHABLE"
        print(f"  -> W-REACHABLE. Required N = {req['coval_core']:.0f} <= {N}: the band is already")
        print("     resolvable and R332's instability is not a sample-size problem.")
    else:
        world = "W-PROMPT-BOUND"
        print(f"  -> W-PROMPT-BOUND. At m=16 the MDE is already "
              f"{DEC['coval_core']['mde16']/DEC['coval_core']['floor']:.3f} of its m→∞ floor, so the")
        print(f"     annotator axis is spent — R306 closed it 26 rounds ago and this confirms it")
        print(f"     quantitatively. Reaching R332's {BAND} band needs "
              f"{req['coval_core']:.0f} prompts, {req['coval_core']/N:.0f}× the release.")
        print("     THE ADMITTED SET IS STRUCTURALLY UNRESOLVABLE HERE. That is a register entry,")
        print("     not a to-do: it would require a larger release, and no analysis of this one")
        print("     can produce it.")
    print("  " + "=" * 78)
    print(f"\n  MULTIPLICITY  {len(N_FRAC)}x{len(M_GRID)} surface cells x {len(SEEDS)} seeds, all")
    print(f"                printed. No hypothesis test is performed here, so no correction is due.")

    o = SELF.parent / "results" / "resolution_floor.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_prompts=N, n_annotations=int(mcount.sum()), median_m=int(np.median(mcount)),
        decomposition=DEC, band=BAND, required_N=req,
        surface={f"{n}|{m}": surf[(n, m)] for (n, m) in surf},
        empirical_vs_analytic_max_dev=float(max(agree)),
        synthetic=dict(sigma_w=float(sw_s), m_curve_spread=float(max(flat) - min(flat))),
        controls=dict(positive=bool(pos_ok), g0=bool(g0_ok), analytic=bool(analytic_ok),
                      negative=bool(neg_ok), placebo=bool(plc_ok)),
        corrects=("R332's next-gradient line claimed every A2 samples ONE annotator; "
                  "load_targets returns every assessment and R306 migrated 26 rounds ago"),
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
