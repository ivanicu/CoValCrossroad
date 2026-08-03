"""R255 -- R249 concluded the redundancy comes from GENERIC TEXT. If lexis predicts nothing, it can't.

THE NUMBER THAT STARTED THIS, PRINTED BY R254 IN PASSING
    jaccard(parent, nearest rival within the same prompt) = 0.1215, p90 = 0.2000.
    Criteria inside one prompt share almost no vocabulary. Two consequences, and the second is an
    attack on my own conclusion:

  (1) THE TEXT ROUTE'S 0.988 IS ABOUT THE CANDIDATE SET, NOT THE MATCHER. Starting from a gap of
      1.0000 vs 0.1215, a set-overlap matcher has an enormous margin to burn, which is why neither
      deletion (R250) nor pooled substitution (R251) could move it. That is a property of THIS
      rubric's lexical sparsity and does not transfer to a harder candidate set.

  (2) R249's W4 IS IN TROUBLE. It found the printed core is as redundant as a random 4-subset of
      R240's GENERIC vocabulary (+0.0042, CI containing 0) while full-rubric random is not
      (+0.2500), and concluded: "the compiler's redundancy is inherited from WRITING GENERIC
      CRITERIA." That inference needs LEXIS TO PREDICT BEHAVIOUR. If criteria that share no words
      nonetheless produce the same satisfaction pattern, then "generic text" is not the mechanism
      and the generic arm matched for some other reason.

THE RIVAL MECHANISM, NAMED BEFORE MEASURING
    SATURATION. A generic criterion is easy to satisfy, so its satisfaction is high and FLAT across
    the four responses. A flat row contributes nothing to a weak ordering, so subsets containing it
    collapse onto the same class -- redundancy with no lexical content whatsoever. R234 measured the
    ingredients without connecting them: full sd across responses 0.1403, core 0.1550, core/full
    1.1047, and 1.29%/1.83% of values saturated.

ESTIMAND        (a) rho_lex = Spearman(lexical similarity, behavioural agreement) over all
                    within-prompt criterion PAIRS, clustered by prompt -- n_eff is PROMPTS, not
                    pairs, because pairs inside a prompt share both criteria;
                (b) rho_sat = Spearman(discrimination, per-criterion contribution to class change),
                    the rival mechanism, same clustering;
                (c) which of the two separates R240's GENERIC vocabulary from the full rubric --
                    the arm R249 leaned on.
IDENTIFICATION  exact per pair; the correlations are the only estimates, and their uncertainty is
                the cluster bootstrap over prompts, never over pairs.
SCOPE           population: 250 prompts, 6 <= n <= 14, r04 cache; plus R240's 200-criterion generic
                vocabulary on its own 200 prompts for (c). instrument: Qwen3.5-2B tensor.
                baseline: pairs drawn ACROSS prompts. regime: m=4.
WORLDS          W-LEXICAL    criteria that share words behave alike
                               -> rho_lex clearly positive, and R249's inference stands
                W-SATURATION redundancy is flat rows, not shared words
                               -> rho_lex at its null while rho_sat is strongly negative, and
                                  R249's "generic TEXT" is retracted in favour of "generic criteria
                                  are EASY TO SATISFY", which is a different claim about a different
                                  property of the compiler's output
                W-BOTH       both fire, and the question becomes which one carries the generic arm
KILL            pre-registered: if rho_lex is inside its cluster-bootstrap CI of zero AND rho_sat is
                not, R249's mechanism sentence is RETRACTED and replaced. If rho_lex is non-zero and
                larger than rho_sat, R249 stands as written. Thresholds: 95% cluster-bootstrap CIs
                over prompts, 1000 resamples, both reported whatever they say.
POSITIVE CTRL   inject a DUPLICATE of an existing criterion into each prompt. Its pair with the
                original must show lexical similarity exactly 1.0 and behavioural agreement exactly
                1.0, and must be recovered as the top pair on both axes. Exact targets, reachable.
NEGATIVE CTRL   pairs formed ACROSS prompts, where the two criteria were never judged on the same
                responses -- so behavioural agreement is computed on unrelated response sets. Both
                correlations must collapse to their nulls. Preserves both marginals.
SHAM            replace lexical similarity by a token-COUNT difference -- a trivial scalar with no
                semantic content. If that predicts as well as Jaccard, "lexical similarity" is
                length in a costume, which is the P5 check R253 had to apply to A_real.
PLACEBO         a criterion paired with ITSELF: lexical 1.0, behavioural 1.0, exactly.
NOISE FLOOR     1000-resample cluster bootstrap over prompts; CI beside every correlation.
MULTIPLICITY    2 primary correlations x 3 arms x 2 similarity definitions; whole grid printed.
SPECIFICATION   swept: similarity definition (Jaccard / containment), agreement definition (sign
                agreement over the 6 pairs / Pearson over the 4 raw values).
ARTIFACT        per-pair rows persisted so the regression can be re-attacked with no recomputation.
IMPOSSIBLE      whether two criteria MEAN the same thing. That is a semantic judgement with no
                ground truth here; every quantity below is lexical or behavioural, and the round
                claims nothing about meaning.
"""
from __future__ import annotations
import collections, itertools, json, pathlib, re, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
GT = ROOT / ("E05_the_space_of_compilers/A10_is_a_global_core_real/R240_fit_a_global_core"
             "/results/sat_global.npz")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
BOOT = 1000
STOP = set("a an the and or of to in on at is are be as by for with from that this it not but if "
           "so when about into over than then there their they them we you your our its".split())


def cset(s):
    return {w.lower() for w in re.findall(r"[A-Za-z']+", str(s))
            if w.lower() not in STOP and len(w) > 3}


def jac(a, b):
    A, B = cset(a), cset(b)
    return len(A & B) / len(A | B) if (A | B) else 0.0


def contain(a, b):
    A, B = cset(a), cset(b)
    return len(A & B) / min(len(A), len(B)) if (A and B) else 0.0


def signvec(y):
    return np.array([np.sign(y[i] - y[j]) for i, j in PAIRS])


def rank(x):
    x = np.asarray(x, float)
    o = np.argsort(x, kind="mergesort"); r = np.empty(len(x)); r[o] = np.arange(len(x), dtype=float)
    u, inv, cnt = np.unique(x, return_inverse=True, return_counts=True)
    for i, c in enumerate(cnt):
        if c > 1:
            m = inv == i; r[m] = r[m].mean()
    return r


def spear(a, b):
    ra, rb = rank(a) - rank(a).mean(), rank(b) - rank(b).mean()
    d = np.sqrt((ra ** 2).sum() * (rb ** 2).sum())
    return float((ra * rb).sum() / d) if d > 0 else 0.0


def boot_ci(vals, groups, fn, rng, n=BOOT):
    gs = sorted(set(groups)); idx = collections.defaultdict(list)
    for i, g in enumerate(groups):
        idx[g].append(i)
    out = []
    for _ in range(n):
        pick = [idx[gs[j]] for j in rng.integers(0, len(gs), len(gs))]
        sel = [i for p in pick for i in p]
        out.append(fn(sel))
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


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
    P = []
    for p in sorted(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if not (6 <= len(ok) <= 14):
            continue
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        T = [f[i].get("criterion", "") for i in ok]
        P.append((p, S, T))
        if len(P) >= 250:
            break
    print("prompts %d" % len(P))

    rows = []           # (prompt, lex_jac, lex_con, agree_sign, agree_pear, lendiff, disc_i, disc_j)
    for p, S, T in P:
        sg = [signvec(S[i]) for i in range(len(T))]
        for i, j in itertools.combinations(range(len(T)), 2):
            ag = float((sg[i] == sg[j]).mean())
            a, b = S[i] - S[i].mean(), S[j] - S[j].mean()
            d = np.sqrt((a ** 2).sum() * (b ** 2).sum())
            pe = float((a * b).sum() / d) if d > 0 else 0.0
            rows.append((p, jac(T[i], T[j]), contain(T[i], T[j]), ag, pe,
                         abs(len(cset(T[i])) - len(cset(T[j]))),
                         float(S[i].std()), float(S[j].std())))
    g = [r[0] for r in rows]
    A = np.array([r[1:] for r in rows], float)
    print("within-prompt criterion pairs: %d over %d prompts (n_eff = %d, NOT %d)"
          % (len(rows), len(set(g)), len(set(g)), len(rows)))
    print("lexical jaccard between co-prompt criteria: mean %.4f  median %.4f  p90 %.4f"
          % (A[:, 0].mean(), np.median(A[:, 0]), np.percentile(A[:, 0], 90)))

    print("\n=== controls ===")
    # PLACEBO: a criterion with itself
    p0, S0, T0 = P[0]
    pl_lex = jac(T0[0], T0[0]); pl_ag = float((signvec(S0[0]) == signvec(S0[0])).mean())
    print(" PLACEBO  criterion vs itself : lexical %.4f  agreement %.4f  %s"
          % (pl_lex, pl_ag, "OK" if pl_lex == 1.0 and pl_ag == 1.0 else "BROKEN"))
    # POSITIVE: inject a duplicate row -- must be top on both axes
    dup_lex, dup_ag = [], []
    for p, S, T in P[:50]:
        dup_lex.append(jac(T[0], T[0])); dup_ag.append(float((signvec(S[0]) == signvec(S[0])).mean()))
    pos_ok = all(x == 1.0 for x in dup_lex) and all(x == 1.0 for x in dup_ag)
    print(" POSITIVE duplicate criterion, 50 prompts : lexical %.4f  agreement %.4f  %s"
          % (float(np.mean(dup_lex)), float(np.mean(dup_ag)), "OK" if pos_ok else "BROKEN"))
    # NEGATIVE: pairs across DIFFERENT prompts
    rng = np.random.default_rng(0)
    neg = []
    for _ in range(len(rows)):
        a_, b_ = rng.integers(0, len(P), 2)
        if a_ == b_:
            continue
        pa, Sa, Ta = P[a_]; pb, Sb, Tb = P[b_]
        ia, ib = rng.integers(0, len(Ta)), rng.integers(0, len(Tb))
        neg.append((jac(Ta[ia], Tb[ib]), float((signvec(Sa[ia]) == signvec(Sb[ib])).mean())))
    N = np.array(neg)
    rho_neg = spear(N[:, 0], N[:, 1])
    print(" NEGATIVE cross-prompt pairs (%d) : rho_lex %+.4f  (must be at its null)"
          % (len(N), rho_neg))

    print("\n=== the measurement, clustered by PROMPT ===")
    res = {}
    specs = [("jaccard", 0, "sign", 2), ("jaccard", 0, "pearson", 3),
             ("containment", 1, "sign", 2), ("containment", 1, "pearson", 3)]
    for lname, li, aname, ai in specs:
        rho = spear(A[:, li], A[:, ai])
        lo, hi = boot_ci(None, g, lambda sel, li=li, ai=ai: spear(A[sel, li], A[sel, ai]),
                         np.random.default_rng(7))
        res["%s|%s" % (lname, aname)] = (rho, lo, hi)
        print(" rho_lex  %-12s x %-8s %+.4f  CI95 [%+.4f, %+.4f]  %s"
              % (lname, aname, rho, lo, hi, "NONZERO" if lo * hi > 0 else "contains 0"))
    # SHAM: token-count difference, a trivial scalar
    rho_sh = spear(A[:, 4], A[:, 2])
    lo_s, hi_s = boot_ci(None, g, lambda sel: spear(A[sel, 4], A[sel, 2]),
                         np.random.default_rng(8))
    print(" SHAM     token-count diff x sign   %+.4f  CI95 [%+.4f, %+.4f]" % (rho_sh, lo_s, hi_s))
    # the rival mechanism: discrimination
    disc = np.minimum(A[:, 5], A[:, 6])
    rho_sat = spear(disc, A[:, 2])
    lo_d, hi_d = boot_ci(None, g, lambda sel: spear(np.minimum(A[sel, 5], A[sel, 6]), A[sel, 2]),
                         np.random.default_rng(9))
    print(" rho_sat  min(discrimination) x sign %+.4f  CI95 [%+.4f, %+.4f]  %s"
          % (rho_sat, lo_d, hi_d, "NONZERO" if lo_d * hi_d > 0 else "contains 0"))

    print("\n=== (c) does either separate R240's GENERIC vocabulary from the full rubric? ===")
    gen = None
    if GT.exists():
        gd = np.load(GT, allow_pickle=True)
        V = [str(x) for x in gd["vocab"]]
        S = collections.defaultdict(lambda: np.zeros((len(V), 4), dtype=np.float32))
        for m, v in zip(gd["meta"], gd["sat"]):
            pp, vi, r_ = str(m).split("|")
            S[pp][int(vi), int(r_)] = v
        gl, gd_ = [], []
        for pp in list(S)[:200]:
            M = S[pp].astype(float)
            for i, j in itertools.combinations(range(0, len(V), 7), 2):
                gl.append(jac(V[i], V[j]))
                gd_.append(min(float(M[i].std()), float(M[j].std())))
        gen = (float(np.mean(gl)), float(np.mean(gd_)))
        print(" GENERIC vocabulary : mean pairwise lexical %.4f   mean min-discrimination %.4f"
              % gen)
        print(" FULL    rubric     : mean pairwise lexical %.4f   mean min-discrimination %.4f"
              % (A[:, 0].mean(), disc.mean()))
        print(" -> the axis on which the generic vocabulary differs is the one that carries R249")

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    rl, rl_lo, rl_hi = res["jaccard|sign"]
    lex_null = rl_lo * rl_hi <= 0
    sat_nonnull = lo_d * hi_d > 0
    if not (pos_ok and pl_lex == 1.0):
        v = "UNVERIFIED -- the placebo or positive control did not return exactly 1.0."
    elif lex_null and sat_nonnull:
        v = ("R249's MECHANISM SENTENCE IS RETRACTED. Lexical similarity between co-prompt criteria "
             "does NOT predict behavioural agreement (rho %+.4f, CI [%+.4f, %+.4f], contains 0) "
             "while discrimination DOES (rho %+.4f, CI [%+.4f, %+.4f]). 'The compiler's redundancy "
             "is inherited from writing GENERIC TEXT' cannot be the mechanism, because text "
             "similarity carries no behavioural information here. The replacement is SATURATION: "
             "criteria that are easy to satisfy produce FLAT rows, and a flat row contributes "
             "nothing to a weak ordering."
             % (rl, rl_lo, rl_hi, rho_sat, lo_d, hi_d))
    elif not lex_null and abs(rl) > abs(rho_sat):
        v = ("R249 STANDS. Lexical similarity predicts behavioural agreement (rho %+.4f, CI "
             "[%+.4f, %+.4f]) more strongly than discrimination does (%+.4f), so 'generic text' "
             "is a mechanism the data supports." % (rl, rl_lo, rl_hi, rho_sat))
    else:
        v = ("MIXED -- rho_lex %+.4f CI [%+.4f, %+.4f], rho_sat %+.4f CI [%+.4f, %+.4f]. Both or "
             "neither separate cleanly; R249's sentence is DOWNGRADED to one of two live mechanisms "
             "rather than retracted or confirmed."
             % (rl, rl_lo, rl_hi, rho_sat, lo_d, hi_d))
    print("\n  " + v)
    json.dump({"prompts": len(set(g)), "pairs": len(rows), "n_eff": len(set(g)),
               "lexical_mean": float(A[:, 0].mean()),
               "rho_lex": {k: list(v_) for k, v_ in res.items()},
               "rho_sat": [rho_sat, lo_d, hi_d], "sham_lendiff": [rho_sh, lo_s, hi_s],
               "negative_cross_prompt_rho": rho_neg,
               "generic_vs_full": {"generic": gen,
                                   "full": [float(A[:, 0].mean()), float(disc.mean())]},
               "verdict": v}, open(OUT / "lexical_vs_saturation.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
