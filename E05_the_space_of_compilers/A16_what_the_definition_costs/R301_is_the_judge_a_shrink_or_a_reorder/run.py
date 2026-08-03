"""R301 — is the judge dependence a SHRINK or a REORDER?

Design, worlds, controls and the pre-registered kill are in README.md, committed as `5f8a685`
BEFORE any 0.8B satisfaction file existed. Read that first; this file only executes it.

The one thing worth restating here, because it decides what the round can mean: **W-LEVEL is dead
by algebra.** Both clauses are a difference between two arms scored by the SAME judge, so an
additive judge offset cancels exactly and every clause effect would be judge-invariant. R290
measured +0.0151 -> -0.0072. That is a DERIVATION, not a measurement — it could not have come out
otherwise — and its whole value is that it points the design at the SLOPE instead of the intercept.

ESTIMAND        beta and R^2 of  eff_08B ~ eff_2B  over the clause-① effects of the arms sharing
                the reference population; separately for clause ②. Plus the admitted set at 0.8B
                at full arm width.
IDENTIFICATION  exact for the arms whose population is the reference arm's. `promptecho` and its
                sham cover 398 prompts and are EXCLUDED FROM THE SLOPE (a joint prompt-resample
                needs one population) — reported in the table, counted in the exclusion line,
                never silently dropped.
SCOPE           population CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base and
                Qwen3.5-0.8B-Base, byte-identical prompt template · baseline named per clause ·
                regime A2·annotator, cluster bootstrap over prompts.
WORLDS          W-SHRINK / W-REORDER / W-SELECTIVE — see README.
KILL            conditional on the controls; thresholds R^2>=0.50 & 0<beta<1 -> SHRINK,
                R^2<0.25 or beta CI spanning 0 -> REORDER, else UNRESOLVED.
POSITIVE CTRL   ① construction parity: `topw_k4` / `random_k4_s0` reach 0.8B by two independent
                paths (directly judged; subset of the judged full) and must agree to float32.
                34 of 41 arms depend on that equality. ② the 0.8B judge is not blind:
                `generic − random_k4_s0` resolvably positive. Both fail at g=0 by construction.
NEGATIVE CTRL   every *_sham excluded at 0.8B.
PLACEBO         an arm against itself: exactly 0.
NOISE FLOOR     per-cell MDE at each arm's own n, never pooled.
MULTIPLICITY    41 arms x 2 clauses at 0.8B; BH q=0.05 over the whole grid; non-survivors printed.
SEEDS           bootstrap seed fixed at 31337 (as every round in this arc); the random_k arms carry
                s0/s1/s2, which is the seed sweep on the baseline itself.
ARTIFACT        results/judge_slope.json with source hash.
IMPOSSIBLE      a third judge scale (not-attempted, not impossible — the template is a drop-in);
                whether the shrink generalises to another release (needs a second release).
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
from report import row, header, verdict, POS, NEG            # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
NBOOT = 1200
RES = ROOT / "corebench" / "results"
USES_PROMPT_LABELS = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}
BASE_ARM = "random_k4_s0"


def sat08_path(a):
    """The 0.8B artifact for arm `a`, by either construction path. Directly-judged wins so the
    parity control below compares the two paths rather than a file with itself."""
    d = RES / f"sat08_{a}.npz"
    r = RES / f"sat_{a}_08b.npz"
    if d.exists():
        return d, "judged"
    if r.exists():
        return r, "subset"
    return None, None


def main():
    tg, _ = load_targets()
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and p.stem != "sat_genericpool16"
                  and not p.stem.endswith(("_08b", "_08bR")))
    S2, S8, PATH, K = {}, {}, {}, {}
    missing = []
    for a in arms:
        try:
            S2[a] = load_sat(RES / f"sat_{a}.npz")
        except Exception:
            continue
        p8, how = sat08_path(a)
        if p8 is None:
            missing.append(a); continue
        S8[a], PATH[a] = load_sat(p8), how
        ks = [len({i for i, _ in S2[a][p]}) for p in list(S2[a])[:200]]
        K[a] = int(np.median(ks))
    arms = [a for a in arms if a in S8]
    if missing:
        print(f"  ⚠ {len(missing)} arms have NO 0.8B artifact and are absent from every count "
              f"below, not scored as failures: {sorted(missing)}")
    if BASE_ARM not in arms or "generic" not in arms:
        print("  UNRUNNABLE: the reference arms are not both present at 0.8B."); return 2
    for tag, need in (("pool2", "sat_genericpool16.npz"), ("pool8", "sat08_genericpool16.npz")):
        if not (RES / need).exists():
            print(f"  UNRUNNABLE: {need} absent — clause ② is size-matched against the pool and "
                  f"cannot be computed without it at both judges."); return 2
    POOL2 = load_sat(RES / "sat_genericpool16.npz")
    POOL8 = load_sat(RES / "sat08_genericpool16.npz")

    BASE = set(POOL2) & set(POOL8) & {p for p in tg if len(tg[p]) >= 2}
    PIDS = {a: sorted(set(S2[a]) & set(S8[a]) & BASE) for a in arms}
    pids = sorted(BASE & set(S2[BASE_ARM]) & set(S8[BASE_ARM]))
    N = len(pids)
    HC = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    npool = min(len({i for i, _ in POOL2[pids[0]]}), len({i for i, _ in POOL8[pids[0]]}))
    print(f"  {len(arms)} arms at BOTH judges · reference population {N} prompts · "
          f"blind pool {npool}\n")
    nsub = sum(1 for a in arms if PATH[a] == "subset")
    print(f"  construction: {len(arms)-nsub} judged directly at 0.8B, {nsub} rebuilt by subsetting "
          f"the judged full\n")

    def on(sat, ps, idx=None):
        return np.array([np.mean([[cls(yvec(sat[p], idx if idx is not None
                                            else sorted({i for i, _ in sat[p]})))[q] == h[q]
                                   for q in range(6)] for h in HC[p]]) for p in ps])

    # ---- POSITIVE CONTROL 1 · construction parity -------------------------------------------
    # `topw_k4` and `random_k4_s0` were judged directly at 0.8B in R290 AND are subsets of the
    # 0.8B full. If those two paths disagree, the subset property is false under this judge and
    # every rebuilt arm is void — while R290 stands untouched. The control localises exactly.
    print("  POSITIVE CONTROL 1 — construction parity (two independent paths to the same arm)\n")
    par, par_ok = {}, True
    for a in ("topw_k4", BASE_ARM):
        alt = RES / f"sat_{a}_08b.npz"
        if not alt.exists():
            print(f"    {a:<16} only one path present — UNVERIFIED, not a pass"); par_ok = False
            par[a] = None; continue
        v_direct = on(S8[a], pids)
        v_subset = on(load_sat(alt), pids)
        mx = float(np.max(np.abs(v_direct - v_subset)))
        ok = mx < 1e-6
        par[a] = mx; par_ok &= ok
        print(f"    {a:<16} max |direct − subset| over {N} prompts = {mx:.3e}  "
              f"{'PASS' if ok else 'FAIL — the subset property is FALSE under this judge'}")
    if par_ok:
        print("    -> the 0.8B arms rebuilt by subsetting are the same object as a direct judging")

    IDX = np.random.default_rng(31337).integers(0, N, (NBOOT, N))

    def cell(x, y, n=None, idx=None):
        d = x - y
        n = n or len(d)
        bs = d[(IDX if idx is None else idx)].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                float(2 * min((bs <= 0).mean(), (bs >= 0).mean())),
                ZEFF * d.std(ddof=1) / math.sqrt(n))

    # ---- POSITIVE CONTROL 2 · the 0.8B judge is not blind ------------------------------------
    g2 = cell(on(S2["generic"], pids), on(S2[BASE_ARM], pids))
    g8 = cell(on(S8["generic"], pids), on(S8[BASE_ARM], pids))
    self8 = cell(on(S8["generic"], pids), on(S8["generic"], pids))
    blind_ok = verdict(*g2[:3], g2[4]) == POS and verdict(*g8[:3], g8[4]) == POS
    print("\n  POSITIVE CONTROL 2 — `generic − random_k4_s0`, which must fire under BOTH judges\n")
    print("  " + header("judge", width=10))
    print("  " + row("2B", *g2[:3], g2[4], width=10))
    print("  " + row("0.8B", *g8[:3], g8[4], width=10))
    print(f"  {'PASS' if blind_ok else 'FAIL — a judge that cannot see this cannot rank arms'}")
    print(f"  PLACEBO  an arm against itself at 0.8B: {self8[0]:.2e}  "
          f"{'PASS' if self8[0] == 0 else 'FAIL'}")

    # ---- the two clauses under both judges, per arm ------------------------------------------
    rows, grid = {}, []
    for a in arms:
        if a == BASE_ARM:
            continue
        ps = PIDS[a]; na = len(ps)
        ia = np.random.default_rng(31337).integers(0, na, (NBOOT, na))
        k = min(K[a], npool)
        c1_2 = cell(on(S2[a], ps), on(S2[BASE_ARM], ps), na, ia)
        c2_2 = cell(on(S2[a], ps), on(POOL2, ps, list(range(k))), na, ia)
        c1_8 = cell(on(S8[a], ps), on(S8[BASE_ARM], ps), na, ia)
        c2_8 = cell(on(S8[a], ps), on(POOL8, ps, list(range(k))), na, ia)
        ok3 = a not in USES_PROMPT_LABELS
        adm8 = (verdict(*c1_8[:3], c1_8[4]) == POS and verdict(*c2_8[:3], c2_8[4]) == POS and ok3)
        adm2 = (verdict(*c1_2[:3], c1_2[4]) == POS and verdict(*c2_2[:3], c2_2[4]) == POS and ok3)
        rows[a] = dict(k=K[a], n=na, path=PATH[a], full_pop=bool(na == N), ok3=bool(ok3),
                       a2_2=float(on(S2[a], ps).mean()), a2_8=float(on(S8[a], ps).mean()),
                       c1_2=c1_2[:3], mde1_2=c1_2[4], c1_8=c1_8[:3], mde1_8=c1_8[4],
                       c2_2=c2_2[:3], mde2_2=c2_2[4], c2_8=c2_8[:3], mde2_8=c2_8[4],
                       adm2=bool(adm2), adm8=bool(adm8))
        grid += [(f"{a}|1", c1_8[3]), (f"{a}|2", c2_8[3])]
    grid.sort(key=lambda z: z[1]); C = len(grid)
    surv = sum(1 for i, (_, p) in enumerate(grid, 1) if p <= 0.05 * i / C)

    adm2 = sorted(a for a in rows if rows[a]["adm2"])
    adm8 = sorted(a for a in rows if rows[a]["adm8"])
    print(f"\n  THE CENSUS AT BOTH JUDGES  ({len(rows)} arms)\n")
    print(f"  {'arm':<20}{'k':>3}{'n':>6}{'A2·2B':>8}{'A2·.8B':>8}"
          f"{'①2B':>9}{'①.8B':>9}{'②2B':>9}{'②.8B':>9}  verdict")
    for a in sorted(rows, key=lambda a: -rows[a]["a2_2"]):
        r = rows[a]
        v = ("ADMITTED both" if r["adm2"] and r["adm8"] else
             "2B only" if r["adm2"] else "0.8B only" if r["adm8"] else "excluded both")
        print(f"    {a:<20}{r['k']:>3}{r['n']:>6}{r['a2_2']:>8.4f}{r['a2_8']:>8.4f}"
              f"{r['c1_2'][0]:>+9.4f}{r['c1_8'][0]:>+9.4f}"
              f"{r['c2_2'][0]:>+9.4f}{r['c2_8'][0]:>+9.4f}  {v}")
    print(f"\n  BH q=0.05 over {C} 0.8B cells · {surv} survive · {C-surv} do not")
    print(f"  ADMITTED at 2B  ({len(adm2)}): {adm2}")
    print(f"  ADMITTED at 0.8B ({len(adm8)}): {adm8}")

    shams = [a for a in rows if a.endswith("_sham")]
    neg_ok = all(not rows[a]["adm8"] for a in shams)
    print(f"  NEGATIVE CTRL   every *_sham excluded at 0.8B ({len(shams)} of them): {neg_ok}")

    # ---- THE ESTIMAND · slope of eff_08B on eff_2B, bootstrapped over prompts ----------------
    # One prompt-resample must apply to every arm in the fit, so the fit is over the arms whose
    # population IS the reference population. The others are in the table above and are counted
    # here; nothing is dropped silently.
    fit = [a for a in rows if rows[a]["full_pop"]]
    off = sorted(a for a in rows if not rows[a]["full_pop"])
    print(f"\n  SLOPE FIT over {len(fit)} arms sharing the reference population of {N} prompts.")
    print(f"    EXCLUDED from the fit ({len(off)}), because a joint prompt-resample needs one\n"
          f"    population: {off}  — their effects are in the table and in the artifact.")

    Vb2, Vb8 = on(S2[BASE_ARM], pids), on(S8[BASE_ARM], pids)
    V2 = {a: on(S2[a], pids) for a in fit}
    V8 = {a: on(S8[a], pids) for a in fit}
    P2 = {a: on(POOL2, pids, list(range(min(K[a], npool)))) for a in fit}
    P8 = {a: on(POOL8, pids, list(range(min(K[a], npool)))) for a in fit}

    def slope_boot(clause):
        """Returns (beta, R2) point estimate and their bootstrap distributions."""
        if clause == 1:
            X = np.stack([V2[a] - Vb2 for a in fit]); Y = np.stack([V8[a] - Vb8 for a in fit])
        else:
            X = np.stack([V2[a] - P2[a] for a in fit]); Y = np.stack([V8[a] - P8[a] for a in fit])

        def fitxy(x, y):
            xc, yc = x - x.mean(), y - y.mean()
            b = float(xc @ yc / (xc @ xc)) if xc @ xc > 0 else float("nan")
            r = float((xc @ yc) ** 2 / ((xc @ xc) * (yc @ yc))) if (xc @ xc) * (yc @ yc) > 0 \
                else float("nan")
            return b, r
        b0, r0 = fitxy(X.mean(1), Y.mean(1))
        bs = np.empty((NBOOT, 2))
        for t in range(NBOOT):
            bs[t] = fitxy(X[:, IDX[t]].mean(1), Y[:, IDX[t]].mean(1))
        return b0, r0, bs

    res = {}
    print(f"\n  {'clause':<10}{'beta':>9}  {'95% CI':<22}{'R^2':>8}  {'95% CI':<22}")
    for cl in (1, 2):
        b0, r0, bs = slope_boot(cl)
        blo, bhi = np.percentile(bs[:, 0], [2.5, 97.5])
        rlo, rhi = np.percentile(bs[:, 1], [2.5, 97.5])
        res[cl] = dict(beta=b0, beta_lo=float(blo), beta_hi=float(bhi),
                       r2=r0, r2_lo=float(rlo), r2_hi=float(rhi))
        print(f"  {'① vs random' if cl == 1 else '② vs blind':<10}{b0:>+9.4f}  "
              f"[{blo:+.4f}, {bhi:+.4f}]  {r0:>8.4f}  [{rlo:.4f}, {rhi:.4f}]")

    # W-SELECTIVE: do the two clause slopes have non-overlapping intervals?
    selective = (res[1]["beta_lo"] > res[2]["beta_hi"]) or (res[2]["beta_lo"] > res[1]["beta_hi"])
    # sign reversals: an arm resolvable and opposite under the two judges
    rev = [a for a in fit if a != BASE_ARM and
           verdict(*rows[a]["c1_2"], rows[a]["mde1_2"]) in (POS, NEG) and
           verdict(*rows[a]["c1_8"], rows[a]["mde1_8"]) in (POS, NEG) and
           (rows[a]["c1_2"][0] > 0) != (rows[a]["c1_8"][0] > 0)]

    # ---- SPECIFICATION CURVE · the arms that change IDENTITY under the judge -----------------
    # Five rules consume satisfaction to select. Under `_08bR` the rule is re-run at 0.8B and the
    # arm is a different criterion set; under `_08b` (used above) the 2B selection is frozen and
    # only the scoring changes. The estimand is what the JUDGE does, so frozen is primary -- but
    # the gap between the two IS the size of the confound, and it is published rather than argued.
    print("\n  SPECIFICATION CURVE — the 5 arms whose RULE consumes satisfaction\n")
    print(f"  {'arm':<20}{'① frozen':>11}{'① rerun':>11}{'Δ':>10}   what the difference is")
    spec = {}
    for a in ("topvar_k4", "topwvar_k4", "oracle_k4", "greedy_k4_fit1", "indep_k4_fit1"):
        alt = RES / f"sat_{a}_08bR.npz"
        if a not in rows or not alt.exists():
            print(f"    {a:<20}{'—':>11}{'—':>11}{'—':>10}   artifact absent, NOT counted as equal")
            spec[a] = None; continue
        ps = PIDS[a]
        e_f = rows[a]["c1_8"][0]
        e_r = float((on(load_sat(alt), ps) - on(S8[BASE_ARM], ps)).mean())
        spec[a] = dict(frozen=e_f, rerun=e_r, delta=e_r - e_f)
        print(f"    {a:<20}{e_f:>+11.4f}{e_r:>+11.4f}{e_r-e_f:>+10.4f}   "
              f"{'re-selection helps' if e_r > e_f else 're-selection hurts'} at 0.8B")
    got = [v for v in spec.values() if v]
    if got:
        print(f"\n    max |Δ| from re-selection = {max(abs(v['delta']) for v in got):.4f}; the "
              f"frozen spec is\n    the one reported above, and the confound it avoids is that "
              f"size.")

    # ---- PRE-REGISTERED KILL, conditional on the controls ------------------------------------
    print("\n  " + "=" * 78)
    ctrl = par_ok and blind_ok and self8[0] == 0 and neg_ok
    print(f"  CONTROLS  parity={par_ok}  not-blind={blind_ok}  placebo={self8[0] == 0}  "
          f"sham={neg_ok}   -> {'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        print("  -> UNVERIFIED. A control did not behave; neither world is readable, and this is")
        print("     NOT a verdict of REORDER. The kill is not evaluated on a broken instrument.")
        world = "UNVERIFIED"
    else:
        r2, blo, bhi = res[1]["r2"], res[1]["beta_lo"], res[1]["beta_hi"]
        if r2 >= 0.50 and blo > 0 and bhi < 1:
            world = "W-SHRINK"
            print(f"  -> W-SHRINK. R^2 = {r2:.3f} and beta = [{blo:.3f}, {bhi:.3f}] lies inside")
            print("     (0,1): the smaller judge preserves the ORDERING of arms and compresses")
            print("     the differences. The definition is judge-bound through RESOLUTION, and")
            print("     FORMULATION.md's instrument line is too strong as written.")
        elif r2 < 0.25 or (blo <= 0 <= bhi):
            world = "W-REORDER"
            print(f"  -> W-REORDER. R^2 = {r2:.3f}, beta = [{blo:.3f}, {bhi:.3f}]. The two judges")
            print("     do not order the arms the same way; no re-thresholding rescues clause ②,")
            print("     and the instrument belongs inside the definition's text.")
        else:
            world = "UNRESOLVED"
            print(f"  -> UNRESOLVED between SHRINK and REORDER: R^2 = {r2:.3f}, "
                  f"beta = [{blo:.3f}, {bhi:.3f}] falls in neither pre-registered band.")
    print(f"  W-SELECTIVE (clause slopes have disjoint CIs): {selective}")
    print(f"  resolvable SIGN REVERSALS on clause ①: {len(rev)} {rev}")
    print("  " + "=" * 78)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "judge_slope.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=src, n_prompts=N, n_arms=len(rows), fit_arms=sorted(fit), off_fit=off,
        rows=rows, slope=res, world=world, selective=bool(selective), reversals=rev,
        admitted_2b=adm2, admitted_08b=adm8, bh_cells=C, bh_survive=surv,
        controls=dict(parity=par, parity_ok=bool(par_ok), not_blind=bool(blind_ok),
                      placebo=float(self8[0]), sham_ok=bool(neg_ok)),
        spec_curve=spec, missing_08b=sorted(missing)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
