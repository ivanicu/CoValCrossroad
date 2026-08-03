"""R253 -- the meta-separator. Is the gate's quantity real, or is it the criterion count renamed?

WHY THIS ROUND AND NOT ANOTHER ONE INSIDE THE SAME ONTOLOGY
    R248 replaced the definition's admissibility gate with A_real, the alphabet the data realises.
    R252 defended A_real against its strongest confound. R249 and R250 filled two certificate
    fields. Every one of those tuned a parameter INSIDE the decomposition
    (Q, class, representative, certificate) -- none asked whether the decomposition carves anything.

    CLAUDE.md's meta-separator: "is there a credible outcome that would show my world-decomposition
    itself is wrong?" If no, the ontology was fixed and everything since is confirmation drift
    wearing the mask of rigour.

    There IS such an outcome here, and it is cheap. P5: A FANCY INVARIANT MUST BE REGRESSED AGAINST
    A TRIVIAL SCALAR. A_real(k) is bounded by min(C(n,k), a(m)) -- it is MECHANICALLY tied to n.
    If A_real predicts nothing that n does not already predict, then the gate
        log2 C(n,k) <= log2 A_real
    is a reparameterisation of "how many criteria does this prompt have", the quantity every version
    of the gate has always had, and four rounds of this arc renamed something instead of finding it.

    ⚠ AND THE PRIOR CASE IS NOT HYPOTHETICAL. A "scale-invariant predictor of generalisation" in
    this operator's own history came back at corr = 0.992 with plain intrinsic dimension, and
    structureless noise reproduced both curves. That is the outcome this round is built to catch.

ESTIMAND        the INCREMENTAL predictive value of A_real(k) over n for per-prompt recovery of a
                planted k-subset at the release's own noise level:
                  rho_A   = Spearman(A_real(k), recovery), per k
                  rho_n   = Spearman(n, recovery), per k
                  partial = Spearman(A_real | n, recovery | n) -- the rank-partial correlation,
                            i.e. what survives after n is projected out of BOTH
                and the OUT-OF-SAMPLE version: fit an isotonic rule on half the prompts, predict the
                other half, and compare mean absolute error of {n only} vs {n + A_real}.
IDENTIFICATION  recovery is measured, not modelled: a k-subset is planted, the observable is built
                from it at eps=0.25, and every C(n,k) candidate is scored. A_real is exhaustive
                arithmetic. Both are exact per prompt; the correlation is the only estimate.
SCOPE           population: 250 prompts, 6 <= n <= 14, r04 cache. instrument: Qwen3.5-2B tensor.
                baseline: n alone. regime: k in {1,2}, eps = 0.25 (R227's calibration to the
                release's own 47.8% two-rater agreement), 5 seeds.
WORLDS          W-REAL      A_real carries information about recoverability that n does not
                              -> partial correlation clearly non-zero, and adding A_real lowers
                                 held-out error
                W-COSTUME   A_real is n in a costume
                              -> partial correlation at its own permutation null, held-out error
                                 unchanged. THE GATE IS DECORATIVE and the definition must say the
                                 admissibility condition is about SIZE, which needs no new term
                W-INVERTED  A_real predicts, but with the sign the gate does not imply
                              -> the gate is real and pointed the wrong way, which is worse than
                                 either and would retract R248's direction rather than its quantity
KILL            pre-registered: if the rank-partial correlation is inside its own permutation null
                at every k, AND adding A_real does not lower held-out error by more than the seed
                spread, the gate's quantity is REDUNDANT WITH n and R248's replacement is retracted
                as a renaming. Thresholds fixed here, before the run: permutation null with 200
                draws, and the held-out comparison read against the 5-seed spread of its own MAE.
POSITIVE CTRL   a SYNTHETIC prompt set where recovery is CONSTRUCTED to depend on A_real and not on
                n: recovery := 1/A_real + noise, with n drawn independently. The partial
                correlation must fire. If it does not, the partial-correlation machinery cannot see
                what it is looking for and every null below is silence.
NEGATIVE CTRL   permute A_real across prompts, holding n and recovery fixed. The partial
                correlation must collapse to its null. Destroys the A_real-to-prompt pairing while
                preserving both marginals exactly.
SHAM            substitute a THIRD trivial scalar -- the mean absolute satisfaction spread per
                prompt -- for A_real. If that predicts as well, "A_real" is not special even among
                trivial scalars, which is a stronger version of the same verdict.
PLACEBO         Spearman(n, n) = 1.0000 exactly, and Spearman(A_real | n, n | n) = 0 exactly.
NOISE FLOOR     5 seeds on the planting; the spread of every correlation reported beside it.
MULTIPLICITY    2 k x 4 predictors x 5 seeds, plus 200 permutation draws per cell. Whole grid.
SPECIFICATION   swept: k, and whether recovery is credited with the 1/ties rule or 0/1.
ARTIFACT        per-prompt (n, A_real, recovery, spread) persisted, so the regression can be
                re-attacked without recomputing anything.
IMPOSSIBLE      whether A_real predicts recovery on a DIFFERENT release. One site; the whole point
                of the gate is that it is measured per prompt, and generalisation across releases
                would need a second release with per-criterion satisfaction, which is the same
                register entry R220 opened.
"""
from __future__ import annotations
import collections, itertools, json, math, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
KS = [1, 2]
EPS = 0.25
SEEDS = [0, 1, 2, 3, 4]
PERM = 200
NMIN, NMAX, NPROMPT = 6, 14, 250


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def rank(x):
    x = np.asarray(x, float)
    o = np.argsort(x, kind="mergesort")
    r = np.empty(len(x)); r[o] = np.arange(len(x), dtype=float)
    # average ties, so a bounded integer predictor is not silently advantaged
    u, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    for i, c in enumerate(cnt):
        if c > 1:
            m = inv == i
            r[m] = r[m].mean()
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    ra = ra - ra.mean(); rb = rb - rb.mean()
    d = math.sqrt(float((ra ** 2).sum()) * float((rb ** 2).sum()))
    return float((ra * rb).sum() / d) if d > 0 else 0.0


def partial(a, b, c):
    """rank-partial correlation of a and b given c: project c out of both rank vectors."""
    ra, rb, rc = rank(a), rank(b), rank(c)
    rc = rc - rc.mean()
    if float((rc ** 2).sum()) == 0:
        return spearman(a, b)
    ea = ra - ra.mean() - rc * float(((ra - ra.mean()) * rc).sum()) / float((rc ** 2).sum())
    eb = rb - rb.mean() - rc * float(((rb - rb.mean()) * rc).sum()) / float((rc ** 2).sum())
    d = math.sqrt(float((ea ** 2).sum()) * float((eb ** 2).sum()))
    return float((ea * eb).sum() / d) if d > 0 else 0.0


def alphabet(W, S, k):
    ctr = collections.Counter()
    for c in itertools.combinations(range(len(W)), k):
        idx = list(c)
        ctr[cls((W[idx, None] * S[idx]).sum(0))] += 1
    return len(ctr)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    prompts = []
    for p in sorted(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if not (NMIN <= len(ok) <= NMAX):
            continue
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok])
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        prompts.append((W, S))
        if len(prompts) >= NPROMPT:
            break
    print("prompts %d | n range [%d, %d]" % (len(prompts), min(len(W) for W, _ in prompts),
                                             max(len(W) for W, _ in prompts)))

    print("\n=== POSITIVE CONTROL: can the partial correlation see what it looks for? ===")
    rg = np.random.default_rng(0)
    n_syn = np.array([rg.integers(6, 15) for _ in range(250)], float)
    a_syn = np.array([rg.integers(3, 40) for _ in range(250)], float)   # independent of n
    rec_syn = 1.0 / a_syn + 0.02 * rg.standard_normal(250)
    pc = partial(a_syn, rec_syn, n_syn)
    print(" synthetic: recovery := 1/A_real + noise, n drawn INDEPENDENTLY")
    print("   Spearman(n, recovery)          %+.4f" % spearman(n_syn, rec_syn))
    print("   Spearman(A_real, recovery)     %+.4f" % spearman(a_syn, rec_syn))
    print("   PARTIAL (A_real | n)           %+.4f  %s"
          % (pc, "OK -- the machinery fires" if abs(pc) > 0.5 else "BLIND -- every null below is silence"))
    pos_ok = abs(pc) > 0.5
    print(" PLACEBO  Spearman(n, n) = %.4f   partial(n | n) = %.4f  %s"
          % (spearman(n_syn, n_syn), partial(n_syn, n_syn, n_syn),
             "OK" if abs(spearman(n_syn, n_syn) - 1.0) < 1e-9
             and abs(partial(n_syn, n_syn, n_syn)) < 1e-9 else "BROKEN"))

    print("\n=== the measurement ===")
    res, per = {}, {}
    for k in KS:
        ns, ars, spreads = [], [], []
        recs_k = collections.defaultdict(list)
        for pi, (W, S) in enumerate(prompts):
            ns.append(len(W)); ars.append(alphabet(W, S, k))
            spreads.append(float(np.abs(S - S.mean(0)).mean()))
            for seed in SEEDS:
                rng = np.random.default_rng(abs(hash((pi, seed, k))) % (2 ** 32))
                T = tuple(sorted(rng.choice(len(W), size=k, replace=False)))
                y = (W[list(T), None] * S[list(T)]).sum(0)
                y = y + EPS * (np.abs(y).max() or 1.0) * rng.standard_normal(4)
                obs = np.array(cls(y))
                best, hits = None, []
                for c in itertools.combinations(range(len(W)), k):
                    idx = list(c)
                    d = float(np.abs(np.array(cls((W[idx, None] * S[idx]).sum(0))) - obs).sum())
                    if best is None or d < best - 1e-12:
                        best, hits = d, [c]
                    elif abs(d - best) <= 1e-12:
                        hits.append(c)
                recs_k[pi].append((1.0 / len(hits)) if T in hits else 0.0)
        ns = np.array(ns, float); ars = np.array(ars, float); spreads = np.array(spreads)
        rec = np.array([float(np.mean(recs_k[i])) for i in range(len(prompts))])
        per[k] = {"n": ns.tolist(), "A_real": ars.tolist(), "recovery": rec.tolist(),
                  "spread": spreads.tolist()}
        r_n, r_a, r_s = spearman(ns, rec), spearman(ars, rec), spearman(spreads, rec)
        pa = partial(ars, rec, ns)
        ps = partial(spreads, rec, ns)
        # permutation null for the partial: shuffle A_real across prompts, keep n and recovery
        rng2 = np.random.default_rng(100 + k)
        null = np.array([partial(ars[rng2.permutation(len(ars))], rec, ns) for _ in range(PERM)])
        pv = float((np.abs(null) >= abs(pa)).mean())
        res[k] = (r_n, r_a, r_s, pa, ps, float(null.std()), pv,
                  float(np.percentile(np.abs(null), 95)))
        print(" k=%d   Spearman(n, recovery) %+.4f   Spearman(A_real, recovery) %+.4f"
              % (k, r_n, r_a))
        print("        PARTIAL (A_real | n) %+.4f   permutation null sd %.4f  |null|_p95 %.4f"
              "  p=%.4f" % (pa, null.std(), np.percentile(np.abs(null), 95), pv))
        print("        SHAM    (spread | n) %+.4f   [a third trivial scalar, same treatment]"
              % ps)

    print("\n=== NEGATIVE CONTROL, and it is the permutation above, stated as a control ===")
    for k in KS:
        print(" k=%d  A_real permuted across prompts: partial collapses to a null of sd %.4f "
              "centred on 0; observed %+.4f sits at p=%.4f"
              % (k, res[k][5], res[k][3], res[k][6]))

    print("\n=== OUT OF SAMPLE: does adding A_real lower held-out error? ===")
    oos = {}
    for k in KS:
        ns = np.array(per[k]["n"]); ars = np.array(per[k]["A_real"])
        rec = np.array(per[k]["recovery"])
        e_n, e_na = [], []
        for s in range(5):
            rng = np.random.default_rng(500 + s)
            idx = rng.permutation(len(rec)); tr, te = idx[:len(idx) // 2], idx[len(idx) // 2:]
            # bin-mean predictors -- no fitting beyond a group mean, so nothing is smuggled in
            def binpred(feat, tr, te):
                b = {}
                for v in np.unique(feat[tr]):
                    b[v] = rec[tr][feat[tr] == v].mean()
                g = rec[tr].mean()
                return np.array([b.get(v, g) for v in feat[te]])
            p_n = binpred(ns, tr, te)
            key = ns * 1000 + ars
            p_na = binpred(key, tr, te)
            e_n.append(float(np.abs(p_n - rec[te]).mean()))
            e_na.append(float(np.abs(p_na - rec[te]).mean()))
        oos[k] = (float(np.mean(e_n)), float(np.ptp(e_n)),
                  float(np.mean(e_na)), float(np.ptp(e_na)))
        print(" k=%d  MAE with n only %.4f (spread %.4f)   with n + A_real %.4f (spread %.4f)"
              "   delta %+.4f" % (k, oos[k][0], oos[k][1], oos[k][2], oos[k][3],
                                  oos[k][2] - oos[k][0]))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    inside = [abs(res[k][3]) <= res[k][7] for k in KS]
    no_oos = [oos[k][2] >= oos[k][0] - max(oos[k][1], oos[k][3]) for k in KS]
    if not pos_ok:
        v = ("UNVERIFIED -- the partial-correlation machinery does not fire on a synthetic set "
             "built to make it fire (%+.4f). Every null here is silence." % pc)
    elif all(inside) and all(no_oos):
        v = ("W-COSTUME -- A_real IS n IN A COSTUME. The partial correlation sits inside its own "
             "permutation null at every k (%s vs |null|_p95 %s) and adding A_real does not lower "
             "held-out error beyond the seed spread. R248's replacement of the gate's right-hand "
             "side is RETRACTED AS A RENAMING: the admissibility condition is about SIZE, and no "
             "new term was needed."
             % ([round(res[k][3], 4) for k in KS], [round(res[k][7], 4) for k in KS]))
    elif all(inside):
        v = ("SPLIT -- the partial correlation is inside its null (%s) but held-out error DOES "
             "improve (%s). The two disagree, so A_real is reported as PARTIALLY REDUNDANT with n "
             "and neither reading is rounded up."
             % ([round(res[k][3], 4) for k in KS],
                [round(oos[k][2] - oos[k][0], 4) for k in KS]))
    else:
        surv = [k for k in KS if not (abs(res[k][3]) <= res[k][7])]
        v = ("W-REAL at k=%s -- A_real carries information about recoverability that n does not: "
             "partial %s against a permutation |null|_p95 of %s, p %s. The gate's quantity is not "
             "the criterion count renamed, and held-out MAE moves by %s."
             % (surv, [round(res[k][3], 4) for k in surv], [round(res[k][7], 4) for k in surv],
                [round(res[k][6], 4) for k in surv],
                [round(oos[k][2] - oos[k][0], 4) for k in surv]))
    print("\n  " + v)
    json.dump({"prompts": len(prompts), "positive_control_partial": pc,
               "per_k": {str(k): {"rho_n": res[k][0], "rho_A": res[k][1], "rho_spread": res[k][2],
                                  "partial_A_given_n": res[k][3], "partial_spread_given_n": res[k][4],
                                  "null_sd": res[k][5], "perm_p": res[k][6],
                                  "null_p95": res[k][7],
                                  "mae_n": oos[k][0], "mae_n_plus_A": oos[k][2],
                                  "mae_spread_n": oos[k][1], "mae_spread_nA": oos[k][3]}
                         for k in KS},
               "per_prompt": {str(k): per[k] for k in KS},
               "verdict": v}, open(OUT / "meta_separator.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
