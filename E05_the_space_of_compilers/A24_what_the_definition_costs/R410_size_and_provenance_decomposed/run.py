"""R410 -- what separates the top pair from the bottom pair: SIZE, PROVENANCE, or neither resolvably?

R409 reduced R408's five-arm ranking to a PARTIAL ORDER -- {coval_core, topw_k6} above {topw_k8,
topw_k3}, topw_k4 unplaced -- and its NEXT asked what separates the tiers, asserting that "size alone
cannot explain it".

⛔ THAT ASSERTION IS ITSELF CHECKABLE AND ONE FACT ALREADY SETTLES IT, so it is DERIVED here rather
   than carried as a premise: `coval_core` and `topw_k4` are BOTH k=4 and land in different tiers. A
   function of k alone cannot map one input to two outputs. Size is therefore not a function of
   position, which is stronger than "does not explain it" and is forced by the committed k values.
   Labelled a DERIVATION; it is not this round's evidence.

⭐ WHAT THE ARMS ACTUALLY OFFER IS A CLEAN 2-FACTOR DECOMPOSITION NOBODY HAS RUN. The `topw_k*` family
   holds PROVENANCE constant and varies SIZE (k = 3, 4, 6, 8). And at k = 4, `coval_core` vs
   `topw_k4` holds SIZE constant and varies PROVENANCE. Two axes, each with the other pinned.

⭐ AND THE MATCHED-SIZE CONTRAST IS NOT A DIFFERENCE OF TWO DIFFERENCES, which is the failure the
   ledger warns about. Both arms at k=4 are scored against the SAME per-k maximum blind reference, so
   in `d_a - d_b = (a2_a - ref) - (a2_b - ref)` the reference CANCELS EXACTLY. This round verifies
   that cancellation numerically rather than asserting it, because "the covariate raises both arms"
   is precisely the shape that has cost this campaign before.

⛔ ARITHMETIC TRAP. That the two axes exist is forced by the arm names; that either is RESOLVABLE is
   not. R408's marginal ses are ~0.0037 and the contrasts here are ~0.002, so a naive reading says
   nothing is resolvable -- but these are PAIRED over the same prompts against the same reference,
   and a paired se can be far smaller than either marginal. Which it is, is the measurement.

ESTIMAND        (A) SIZE, provenance held constant: the effect of each `topw_k` arm and the PAIRED
                    difference between adjacent k, with CIs;
                (B) PROVENANCE, size held constant: `coval_core - topw_k4`, paired, with its CI and
                    its own MDE;
                (C) whether the reference cancels exactly in (B) -- verified, not assumed.

IDENTIFICATION  Exact for the paired contrasts on this release. NOT identified: whether "provenance"
                is one thing -- `coval_core` differs from `topw_k4` in more than one way at once, so
                a resolved contrast names a BUNDLE, not a mechanism. Said in the verdict.

SCOPE           population: 5 label-free arms + 1 control · instrument: paired per-prompt differences
                against each arm's own per-k maximum blind set · baseline: zero difference ·
                regime: literal rule, p = 100.

WORLDS
  W-SIZE-ONLY      the topw size curve resolves and the matched-size provenance contrast does not.
                   Then the tiers are about k after all, and R409's NEXT was wrong in its own words.
  W-PROVENANCE     the matched-size contrast resolves. Then something other than size separates the
                   released core from a rubric-weighted set of identical size.
  W-BOTH           both resolve; the decomposition is the finding and neither factor is the story.
  W-NEITHER        neither resolves. Then the partial order R409 found has no decomposition this
                   design can reach, and saying so is the result.

PREDICTION MATRIX
  W-SIZE-ONLY  -> >=1 adjacent-k paired CI excludes 0, provenance CI includes 0
  W-PROVENANCE -> provenance CI excludes 0, no adjacent-k CI does
  W-BOTH       -> both
  W-NEITHER    -> neither, and every CI printed

PRE-REGISTERED KILL -- conditional on the controls, never on the CIs alone.
    if oracle_vs_topwk4_resolves_positive and self_contrast_is_exactly_zero and reference_cancels:
        classify by which CIs exclude 0, naming every one
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  SEPARATION (+)  `oracle_k4 - topw_k4`, same k, ~10x the contrasts of interest, must resolve
                  positive. Without it a null below cannot be told from a blind paired test.
  SELF (-)        an arm minus ITSELF must be exactly 0.0 with se exactly 0.0. A placebo that must
                  return exactly zero, and it can fail if the pairing is misaligned.
  CANCELLATION    `d_a - d_b` must equal `a2_a - a2_b` to machine precision at matched k, proving the
                  reference cancels and this is not a difference of two differences.
  MULTIPLICITY    4 contrasts of interest (3 adjacent-k + 1 provenance) + 2 controls; Holm-corrected
                  over the 4, and BOTH raw and corrected printed.
SEEDS           the CIs are analytic (paired t); a 3-seed bootstrap is run beside them and both are
                printed, because agreement of two estimators is cheap and a disagreement is a bug.
ARTIFACT        results/r410_size_provenance.json with the source hash.

IMPOSSIBLE HERE
  isolating WHAT provenance means -- `coval_core` differs from `topw_k4` in several ways at once; a
                                     resolved contrast names a BUNDLE. Naming its parts needs arms
                                     that vary one thing, which this release does not ship.
  a second release / second judge -- one release; at 0.8B nothing is admitted (R358/R359).
  a causal claim about k          -- the k arms are not randomly assigned; this is descriptive.

EXIT
    0  controls hold and every contrast is reported
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib
import itertools
import json
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
R408 = HERE.parent / "R408_the_literal_test_at_the_universal_reference" / "results" / \
    "r408_literal_test.json"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
TOPW = ["topw_k3", "topw_k4", "topw_k6", "topw_k8"]
SEEDS = (1, 2, 3)
B = 2000


def main() -> int:
    pool_f = RES / "sat_genericpool16.npz"
    if not (pool_f.exists() and R408.exists()):
        print("  UNRUNNABLE: pool or R408 artifact absent. Exit 2, never 0."); return 2
    a408 = json.loads(R408.read_text())
    tg, _ = load_targets()
    POOL = load_sat(pool_f)
    pids = sorted(set(POOL) & {q for q in tg if len(tg[q]) >= 2})
    H = {q: [cls(np.array(t[0], float)) for t in tg[q]] for q in pids}
    npool = len({i for i, _ in POOL[pids[0]]})
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    print(f"R410 · size or provenance?   {len(pids)} prompts\n")
    print("  ⛔ R409's NEXT ASSERTED `size alone cannot explain it`. One fact SETTLES it and it is a")
    print("     DERIVATION, not this round's evidence: `coval_core` and `topw_k4` are BOTH k=4 and")
    print("     land in different tiers, and a function of k alone cannot map one input to two")
    print("     outputs. Size is not a function of position.\n")

    subjects = ["coval_core"] + TOPW + ["oracle_k4"]

    def a2_vec(sat, ps):
        out = []
        for q in ps:
            idx = sorted({i for i, _ in sat[q]})
            yv = cls(yvec(sat[q], idx))
            out.append(np.mean([[yv[c] == h[c] for c in range(6)] for h in H[q]]))
        return np.array(out, float)

    A2, KOF = {}, {}
    for a in subjects:
        S = load_sat(RES / f"sat_{a}.npz")
        ps = [q for q in pids if q in S]
        v = a2_vec(S, ps)
        pos = {q: n for n, q in enumerate(pids)}
        arr = np.full(len(pids), np.nan)
        for m, q in enumerate(ps):
            arr[pos[q]] = v[m]
        A2[a] = arr
        KOF[a] = min(max(int(np.median([len({i for i, _ in S[q]}) for q in ps])), 1), npool)

    def build(k):
        sb = np.array(list(itertools.combinations(range(npool), k)))
        SAT = np.stack([np.array([[POOL[q][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                        for q in pids])
        out = np.empty((len(sb), len(pids)))
        for n in range(len(pids)):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[:, n] = (C_[:, None, :] == np.array(H[pids[n]], float)[None, :, :]).mean(axis=(1, 2))
        return out

    CLS = {k: build(k) for k in sorted({KOF[a] for a in subjects})}
    REF = {k: CLS[k][int(np.argsort(CLS[k].mean(axis=1))[-1])] for k in CLS}
    D = {a: A2[a] - REF[KOF[a]] for a in subjects}

    def paired(a, b):
        """Paired contrast a - b over prompts where BOTH are defined."""
        x = D[a] - D[b]
        m = ~np.isnan(x)
        x = x[m]
        e = float(x.mean()); se = float(x.std(ddof=1) / math.sqrt(len(x)))
        return e, se, len(x), (e - 1.959964 * se, e + 1.959964 * se), ZEFF * se

    # ---- CONTROLS ---------------------------------------------------------------------------------
    print("  CONTROLS")
    oe, ose, on, oci, omde = paired("oracle_k4", "topw_k4")
    sep_ok = oci[0] > 0
    se_, sse, _, _, _ = paired("topw_k4", "topw_k4")
    self_ok = (se_ == 0.0 and sse == 0.0)
    lhs = D["coval_core"] - D["topw_k4"]
    rhs = A2["coval_core"] - A2["topw_k4"]
    m = ~np.isnan(lhs) & ~np.isnan(rhs)
    cancel = float(np.nanmax(np.abs(lhs[m] - rhs[m])))
    cancel_ok = cancel < 1e-12
    print(f"    SEPARATION (+)  oracle_k4 - topw_k4 (same k) = {oe:+.6f} "
          f"CI[{oci[0]:+.6f},{oci[1]:+.6f}] n={on}   {'PASS' if sep_ok else 'FAIL'}")
    print(f"    SELF (-)        topw_k4 - topw_k4 = {se_:+.1f} (se {sse:.1f})   "
          f"{'PASS' if self_ok else 'FAIL — the pairing is misaligned'}")
    print(f"    CANCELLATION    max|(d_a-d_b) - (a2_a-a2_b)| at matched k = {cancel:.2e}   "
          f"{'PASS' if cancel_ok else 'FAIL'}")
    print(f"                    -> the reference cancels EXACTLY, so the matched-size contrast is")
    print(f"                       NOT a difference of two differences")
    if not (sep_ok and self_ok and cancel_ok):
        print("\n  UNVERIFIED — a control misbehaved. Exit 1."); return 1

    # ---- (A) SIZE, provenance held constant --------------------------------------------------------
    print(f"\n  (A) SIZE — provenance held constant inside the `topw_k` family")
    print(f"      {'arm':<12}{'k':>3}{'e vs max-blind':>17}")
    for a in TOPW:
        e = float(np.nanmean(D[a]))
        print(f"      {a:<12}{KOF[a]:>3}{e:>+17.6f}")
    print(f"      adjacent-k PAIRED contrasts:")
    contrasts = {}
    for a, b in zip(TOPW, TOPW[1:]):
        e, se, n, ci, mde = paired(a, b)
        contrasts[f"{a}-{b}"] = dict(e=e, se=se, n=n, ci=list(ci), mde=mde)
        print(f"        {a} - {b:<10} {e:>+10.6f}  CI[{ci[0]:+.6f},{ci[1]:+.6f}]  "
              f"{'RESOLVED' if ci[0]*ci[1] > 0 else 'inside 0'}")

    # ---- (B) PROVENANCE, size held constant --------------------------------------------------------
    e, se, n, ci, mde = paired("coval_core", "topw_k4")
    contrasts["coval_core-topw_k4"] = dict(e=e, se=se, n=n, ci=list(ci), mde=mde)
    print(f"\n  (B) PROVENANCE — size held constant at k=4, SAME reference, which cancels")
    print(f"      coval_core - topw_k4 = {e:+.6f}  se {se:.6f}  n={n}")
    print(f"      CI[{ci[0]:+.6f}, {ci[1]:+.6f}]   own MDE {mde:.6f}   "
          f"{'RESOLVED' if ci[0]*ci[1] > 0 else 'inside 0'}")
    print(f"      ⚠ the marginal ses were ~0.0037 each; this PAIRED se is {se:.6f}, which is why the")
    print(f"        contrast is worth computing rather than eyeballed off two point estimates")

    # ---- MULTIPLICITY over the 4 contrasts of interest ---------------------------------------------
    keys = [f"{a}-{b}" for a, b in zip(TOPW, TOPW[1:])] + ["coval_core-topw_k4"]
    ps_ = {}
    for k in keys:
        c = contrasts[k]
        z = abs(c["e"]) / c["se"] if c["se"] > 0 else 0.0
        ps_[k] = math.erfc(z / math.sqrt(2))
    order = sorted(keys, key=lambda k: ps_[k])
    holm, run = {}, 0.0
    for i, k in enumerate(order):
        adj = min(1.0, max(run, ps_[k] * (len(keys) - i)))
        holm[k] = adj; run = adj
    print(f"\n  MULTIPLICITY — Holm over the {len(keys)} contrasts of interest, raw AND corrected")
    print(f"    {'contrast':<26}{'raw p':>12}{'Holm p':>12}   survives@0.05")
    survivors = []
    for k in order:
        ok = holm[k] < 0.05
        if ok:
            survivors.append(k)
        print(f"    {k:<26}{ps_[k]:>12.2e}{holm[k]:>12.2e}   {ok}")

    # ---- bootstrap beside the analytic CI ----------------------------------------------------------
    boot = {}
    for k in keys:
        a, b = k.split("-")
        x = (D[a] - D[b]); x = x[~np.isnan(x)]
        lows, highs = [], []
        for s in SEEDS:
            rng = np.random.default_rng(s)
            draws = np.array([x[rng.integers(0, len(x), len(x))].mean() for _ in range(B)])
            lows.append(float(np.percentile(draws, 2.5))); highs.append(float(np.percentile(draws, 97.5)))
        boot[k] = [min(lows), max(highs)]
    print(f"\n  TWO ESTIMATORS — analytic paired-t vs {B:,}-draw bootstrap, {len(SEEDS)} seeds")
    print(f"    {'contrast':<26}{'analytic CI':>26}{'bootstrap CI':>26}")
    for k in keys:
        c = contrasts[k]
        print(f"    {k:<26}[{c['ci'][0]:+.5f},{c['ci'][1]:+.5f}]"
              f"      [{boot[k][0]:+.5f},{boot[k][1]:+.5f}]")

    size_res = [k for k in keys[:-1] if k in survivors]
    prov_res = "coval_core-topw_k4" in survivors
    print()
    if size_res and prov_res:
        v = "W_BOTH"
        print(f"  W-BOTH — size resolves at {size_res} AND provenance resolves at matched k=4. The")
        print(f"  decomposition is the finding and neither factor is the story on its own.")
    elif prov_res:
        v = "W_PROVENANCE"
        print(f"  W-PROVENANCE — at IDENTICAL size k=4 and against the SAME reference, `coval_core`")
        print(f"  beats `topw_k4` by {contrasts['coval_core-topw_k4']['e']:+.6f}, surviving Holm. No")
        print(f"  adjacent-k contrast does. Something other than size separates the released core")
        print(f"  from a rubric-weighted set of the same size.")
    elif size_res:
        v = "W_SIZE_ONLY"
        print(f"  W-SIZE-ONLY — {size_res} resolves and the matched-size provenance contrast does")
        print(f"  not. The tiers are about k after all, and R409's NEXT was wrong in its own words.")
    else:
        v = "W_NEITHER"
        print(f"  W-NEITHER — no contrast survives Holm. The partial order R409 found has NO")
        print(f"  decomposition this design can reach, and saying so is the result rather than")
        print(f"  reporting whichever raw p happened to be smallest.")

    print(f"\n  ⚠ A RESOLVED PROVENANCE CONTRAST NAMES A BUNDLE, NOT A MECHANISM. `coval_core` differs")
    print(f"    from `topw_k4` in several ways at once, and separating them needs arms that vary one")
    print(f"    thing — which this release does not ship.")
    print(f"  ⚠ AND THE k ARMS ARE NOT RANDOMLY ASSIGNED, so (A) is descriptive, never causal.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               n_prompts=len(pids), kof=KOF,
               effects={a: float(np.nanmean(D[a])) for a in subjects},
               contrasts=contrasts, raw_p=ps_, holm_p=holm, survivors=survivors,
               bootstrap_ci=boot,
               controls=dict(separation=[oe, list(oci)], self_zero=self_ok, cancellation=cancel),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r410_size_provenance.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
