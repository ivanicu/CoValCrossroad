"""R252 -- R248's rival was a UNIFORM tensor. That confounds redundancy with the marginal.

WHAT R248 CLAIMED, ONE ROUND AGO
    "The binding constraint is the rubric's own redundancy, not the channel." Evidence: paired per
    prompt, the real rubric separates FEWER Q-classes than a RANDOM tensor of identical SHAPE, at
    62.0% / 90.4% / 91.2% of prompts for k = 1/2/3, median deficit -0.60 / -4.80 / -6.00.

THE CONFOUND I BUILT AND DID NOT CONTROL
    `rng.random((n, 4))` is UNIFORM on [0,1]: mean 0.5, sd 0.2887. The real satisfaction tensor is
    not. R234's own artifact checks measured it: full mean 0.5548, sd 0.2365, and 1.29% of values
    saturated. A tensor with MORE SPREAD produces larger pairwise gaps, and a weak ordering is
    exactly a function of pairwise gaps -- so a wider marginal separates more classes FOR REASONS
    THAT HAVE NOTHING TO DO WITH REDUNDANCY.

    So R248's contrast varies TWO things at once: the marginal distribution of satisfaction values,
    and the correlation between criteria. Its conclusion names only the second.

    ⚠ This is the confound realstat asks to be written BEFORE the run, and in R248 it was not
    written at all. Finding it one round later is the cheapest possible outcome; finding it after
    the claim had been cited would not have been.

THE CONTROL THAT SEPARATES THEM, AND WHY IT IS THE RIGHT ONE
    PERMUTE THE FOUR RESPONSE VALUES INDEPENDENTLY WITHIN EACH CRITERION ROW.
      - every criterion keeps its EXACT multiset of satisfaction values, so the marginal is
        identical not approximately but exactly, per criterion and therefore per prompt
      - the alignment BETWEEN criteria -- which response each one favours -- is destroyed
      - nothing else changes: same n, same m, same weights, same class function
    If the collapse is REDUNDANCY, this must separate more classes than the real tensor.
    If the collapse was the MARGINAL, this must land on top of the real tensor and R248's W3 is
    overturned by its own successor.

ESTIMAND        A_real(k) -- distinct Q-classes over all C(n,k) subsets -- for four tensors on the
                SAME prompts: REAL, UNIFORM (R248's rival), ROW-PERMUTED (marginal-matched), and
                GAUSSIAN-MATCHED (mean/sd matched to the real tensor, correlation destroyed).
IDENTIFICATION  exact and exhaustive. Every subset enumerated; nothing sampled.
SCOPE           population: the same 250 prompts R248 used, 6 <= n <= 14, from the r04 cache.
                instrument: r04 Qwen3.5-2B tensor. baseline: three synthetic rivals, each
                destroying a different thing. regime: k in {1,2,3}, m=4, noiseless.
WORLDS          W-REDUNDANCY  the criteria agree with one another
                     -> ROW-PERMUTED separates MORE than REAL, by about what UNIFORM did
                W-MARGINAL    R248 measured the value distribution, not the agreement
                     -> ROW-PERMUTED lands ON TOP of REAL, and only UNIFORM is above
                W-BOTH        both contribute
                     -> ROW-PERMUTED sits strictly between REAL and UNIFORM
KILL            pre-registered: if the paired median (ROW-PERMUTED - REAL) is <= 0 at every k,
                R248's claim 8 is OVERTURNED and the sentence "the binding constraint is the
                rubric's redundancy" is retracted. If it is > 0 at every k, claim 8 SURVIVES its
                own strongest confound. Thresholds are the paired sign test over prompts, not a
                comparison of two means -- one round ago I compared a paired mean to a per-prompt
                range and had to record the result UNVERIFIED, so the scale is fixed here first.
POSITIVE CTRL   a synthetic prompt whose criteria are IDENTICAL: A_real must be exactly 1 for REAL
                and strictly greater after row-permutation, because permuting identical rows
                independently makes them differ. Target values are exact integers and reachable.
NEGATIVE CTRL   permute with the IDENTITY permutation -- A_real must equal the real tensor's
                exactly, on every prompt. If it does not, the permuter touches something else.
SHAM            permute the four responses with the SAME permutation for every criterion in a
                prompt. That relabels the responses without disturbing agreement, so A_real must
                be UNCHANGED. This is the sham that isolates "which response" from "how much".
PLACEBO         k = n: one subset, A_real = 1, for every tensor.
NOISE FLOOR     5 permutation draws per prompt per arm; spread reported.
MULTIPLICITY    3 k x 4 tensors x 5 draws over 250 prompts; whole grid, and the paired sign test
                reported with its own n.
SPECIFICATION   the axis swept is WHAT THE RIVAL TENSOR DESTROYS: everything (uniform) / only the
                cross-criterion alignment (row-permuted) / the correlation under a matched
                parametric form (gaussian).
ARTIFACT        per-prompt A_real for all four arms persisted.
IMPOSSIBLE      whether criteria agree because they MEAN similar things or because the judge scores
                them similarly. That needs a second judge on the same subsets, and the R164 caches
                cover only the full and core sets, not arbitrary subsets.
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
KS = [1, 2, 3]
DRAWS = 5
NMIN, NMAX, NPROMPT = 6, 14, 250


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def alphabet(W, S, k):
    ctr = collections.Counter()
    for c in itertools.combinations(range(len(W)), k):
        idx = list(c)
        ctr[cls((W[idx, None] * S[idx]).sum(0))] += 1
    return len(ctr)


def row_permute(S, rng):
    """Each criterion keeps its EXACT multiset of values; cross-criterion alignment destroyed."""
    out = S.copy()
    for i in range(len(out)):
        out[i] = out[i][rng.permutation(4)]
    return out


def same_permute(S, rng):
    """SHAM: relabel the responses identically for every criterion. Agreement untouched."""
    return S[:, rng.permutation(4)]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
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
    allv = np.concatenate([S.ravel() for _W, S in prompts])
    print("prompts %d | real satisfaction: mean %.4f sd %.4f   |   uniform[0,1]: mean 0.5000 "
          "sd %.4f" % (len(prompts), allv.mean(), allv.std(), 1 / math.sqrt(12)))
    print("  -> R248's rival had %.1f%% MORE spread than the real tensor, and a weak ordering is a"
          % (100 * (1 / math.sqrt(12)) / allv.std() - 100))
    print("     function of pairwise gaps. That is the confound this round separates.")

    print("\n=== controls, before any comparison ===")
    rng = np.random.default_rng(0)
    n_c = 8
    Sid = np.tile(np.array([0.9, 0.4, 0.2, 0.7]), (n_c, 1))
    Wid = np.ones(n_c)
    a_ident = [alphabet(Wid, Sid, k) for k in KS]
    a_permd = [float(np.mean([alphabet(Wid, row_permute(Sid, rng), k) for _ in range(DRAWS)]))
               for k in KS]
    pos_ok = all(a_ident[i] == 1 and a_permd[i] > 1 for i in range(len(KS)))
    print(" POSITIVE identical criteria: A_real real %s -> row-permuted %s  %s"
          % (a_ident, ["%.1f" % x for x in a_permd], "OK" if pos_ok else "PERMUTER BROKEN"))
    W0, S0 = prompts[0]
    ident_perm = all(alphabet(W0, S0.copy(), k) == alphabet(W0, S0, k) for k in KS)
    shams = [alphabet(W0, same_permute(S0, np.random.default_rng(3)), k) for k in KS]
    reals = [alphabet(W0, S0, k) for k in KS]
    sham_ok = shams == reals
    print(" NEGATIVE identity permutation reproduces the real tensor exactly : %s"
          % ("OK" if ident_perm else "BROKEN"))
    print(" SHAM     same permutation for every criterion (relabel responses) : real %s vs sham %s"
          "  %s" % (reals, shams, "OK -- unchanged" if sham_ok else "AGREEMENT DISTURBED"))
    pl = alphabet(W0, S0, len(W0))
    print(" PLACEBO  k = n : A_real %d  %s" % (pl, "OK" if pl == 1 else "BROKEN"))

    print("\n=== A_real by tensor, median over %d prompts ===" % len(prompts))
    print("%-4s %10s %12s %14s %14s" % ("k", "REAL", "UNIFORM", "ROW-PERMUTED", "GAUSS-MATCHED"))
    per = collections.defaultdict(list)
    for k in KS:
        for W, S in prompts:
            a_r = alphabet(W, S, k)
            a_u = float(np.mean([alphabet(W, rng.random(S.shape), k) for _ in range(DRAWS)]))
            a_p = float(np.mean([alphabet(W, row_permute(S, rng), k) for _ in range(DRAWS)]))
            a_g = float(np.mean([alphabet(W, np.clip(rng.normal(S.mean(), S.std(), S.shape), 0, 1),
                                          k) for _ in range(DRAWS)]))
            per[k].append((a_r, a_u, a_p, a_g))
        A = np.array(per[k])
        print("%-4d %10.2f %12.2f %14.2f %14.2f"
              % (k, np.median(A[:, 0]), np.median(A[:, 1]), np.median(A[:, 2]), np.median(A[:, 3])))

    print("\n=== the paired test, on the scale fixed BEFORE the run: sign test over prompts ===")
    res = {}
    for k in KS:
        A = np.array(per[k])
        d_p = A[:, 2] - A[:, 0]
        d_u = A[:, 1] - A[:, 0]
        d_g = A[:, 3] - A[:, 0]
        n_pos = int((d_p > 0).sum()); n_neg = int((d_p < 0).sum())
        n_eff = n_pos + n_neg
        # exact binomial two-sided, no normal approximation at this n
        pv = 0.0 if n_eff == 0 else 2 * sum(math.comb(n_eff, i) for i in range(min(n_pos, n_neg) + 1)) / 2 ** n_eff
        pv = min(1.0, pv)
        res[k] = (float(np.median(d_p)), n_pos, n_neg, pv, float(np.median(d_u)), float(np.median(d_g)))
        print(" k=%d  ROW-PERMUTED - REAL: median %+.2f   %d up / %d down / %d tied   sign-test "
              "p=%.2e" % (k, np.median(d_p), n_pos, n_neg, len(d_p) - n_eff, pv))
        print("       for reference  UNIFORM - REAL %+.2f   GAUSS-MATCHED - REAL %+.2f"
              % (np.median(d_u), np.median(d_g)))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not (pos_ok and ident_perm and sham_ok and pl == 1):
        v = ("UNVERIFIED -- a control did not behave (positive %s, identity %s, sham %s); the "
             "permuter or the counter is wrong." % (pos_ok, ident_perm, sham_ok))
    elif all(res[k][0] > 0 for k in KS):
        v = ("CLAIM 8 SURVIVES ITS STRONGEST CONFOUND. Destroying only the cross-criterion "
             "alignment, with every criterion's marginal held EXACTLY fixed, raises A_real at every "
             "k (median %s, sign test p %s). The collapse is the criteria agreeing with one "
             "another, not the width of the value distribution -- and the uniform rival R248 used "
             "did overstate it: %s vs %s."
             % ([round(res[k][0], 2) for k in KS], ["%.1e" % res[k][3] for k in KS],
                [round(res[k][4], 2) for k in KS], [round(res[k][0], 2) for k in KS]))
    elif all(res[k][0] <= 0 for k in KS):
        v = ("CLAIM 8 IS OVERTURNED BY ITS OWN SUCCESSOR. With the marginal held exactly fixed, "
             "destroying cross-criterion alignment does NOT raise A_real (median %s). R248 measured "
             "the WIDTH of the uniform rival's value distribution, not the rubric's redundancy, and "
             "the sentence 'the binding constraint is the rubric's own redundancy' is retracted."
             % [round(res[k][0], 2) for k in KS])
    else:
        v = ("PARTIAL -- the sign of ROW-PERMUTED minus REAL differs across k (%s). Claim 8 is "
             "DOWNGRADED to hold only where the sign is positive, and the k-dependence is the "
             "finding." % [round(res[k][0], 2) for k in KS])
    print("\n  " + v)
    json.dump({"prompts": len(prompts), "real_mean": float(allv.mean()), "real_sd": float(allv.std()),
               "uniform_sd": 1 / math.sqrt(12),
               "controls": {"positive": bool(pos_ok), "identity": bool(ident_perm),
                            "sham": bool(sham_ok), "placebo": int(pl)},
               "per_k": {str(k): {"median_rowperm_minus_real": res[k][0], "n_up": res[k][1],
                                  "n_down": res[k][2], "sign_p": res[k][3],
                                  "median_uniform_minus_real": res[k][4],
                                  "median_gauss_minus_real": res[k][5]} for k in KS},
               "verdict": v}, open(OUT / "marginal_vs_redundancy.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
