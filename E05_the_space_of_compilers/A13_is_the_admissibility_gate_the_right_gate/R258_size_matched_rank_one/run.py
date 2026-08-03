"""R258 -- R256's core-vs-full rank-1 gap is 4 rows against 11. This is the size-matched cell.

WHAT R256 REPORTED AND THE LINE IT ENDED ON
    A rank-1 reconstruction reproduces the object's own class on 0.4440 of prompts for the full
    rubric and 0.6000 for the printed core. R256's own commit body: "the core's 0.6000 against the
    full rubric's 0.4440 is SIZE-CONFOUNDED -- four rows versus eleven -- and the size-matched
    comparison against random 4-subsets is the missing cell."

    R256 already showed why the confound is not hypothetical: the core's lambda1_share is higher
    than the full rubric's (0.8138 vs 0.7604) AND SO IS ITS PERMUTATION NULL (0.6994 vs 0.6210),
    because fewer rows means less averaging. Against its own null the core's excess is LOWER. The
    measured null killed one interpretation there; this round asks whether it kills the other.

⛔ THE ARITHMETIC THAT MAKES THE PLACEBO EXACT, AND IT IS THE POINT OF THIS DESIGN
    A subset of size k=1 IS rank one. Its leading component is its only row, so rank-1 class
    agreement must be EXACTLY 1.0000 at k=1, by construction and not by measurement. That gives a
    placebo whose target is an exact integer and which no broken implementation can pass by
    accident -- and it also says the whole statistic is size-dependent BEFORE any data is read.
    Reading 0.6000 as "the core is more one-dimensional" without this sweep would have been
    reading the size.

ESTIMAND        rank1_selfclass(k) = P( class of the leading component of a k-subset == class of
                that same k-subset's own weighted sum ), for k = 1..6, on random subsets of the
                full rubric, versus the printed core at its own size.
IDENTIFICATION  exact per prompt and per draw; deterministic given the tensor.
SCOPE           population: the 250 prompts R256 used, 6 <= n <= 14, with a usable core tensor.
                instrument: r04 Qwen3.5-2B cache, identical to R256 -- so any difference from R256
                is arithmetic, never the judge. baseline: random k-subsets, 20 draws, same prompt.
                regime: m=4, row-centred, weighted by the population weights as R256 did.
WORLDS          W-SIZE      the 0.6000 is the core's SIZE
                              -> random 4-subsets land on 0.6000 too, and the core-vs-full gap
                                 carries no information about the compiler
                W-COMPILER  the core really is more one-dimensional than an arbitrary 4-subset
                              -> the core sits above random-4 by more than the draw spread
                W-INVERTED  the core is LESS one-dimensional than an arbitrary 4-subset
                              -> which would be a finding about the compiler in the opposite
                                 direction, and one no round has looked for
KILL            pre-registered: if |core - random4| is inside the random arm's own draw spread, the
                core-vs-full comparison in R256 is retracted as a size effect and the sentence
                "the core is more one-dimensional" may not be written in either direction.
POSITIVE CTRL   synthetic rank-1 subsets (rows = a_i * q + tiny noise) at every k must return
                1.0000, showing the statistic can reach its ceiling at k > 1 where it is not forced.
NEGATIVE CTRL   row-permuted subsets -- each row keeps its exact multiset, cross-row alignment
                destroyed (R252's control). Gives the null at every k.
SHAM            subsets drawn from a DIFFERENT prompt's rubric, evaluated on this prompt's
                responses. Size-matched, instrument-matched, structure-free.
PLACEBO         k = 1: exactly 1.0000, by construction. Anything else means the implementation is
                wrong, and the round is void.
NOISE FLOOR     20 draws per prompt per k; spread reported.
MULTIPLICITY    6 sizes x 4 arms x 250 prompts; whole grid printed including the sizes that show
                the trend rather than the finding.
SPECIFICATION   swept: subset size, which is the axis R256 held fixed without recording it.
ARTIFACT        per-prompt per-k values persisted.
IMPOSSIBLE      whether one-dimensionality is DESIRABLE. That needs a downstream task; this is a
                geometric statement about the tensor and nothing else.
"""
from __future__ import annotations
import collections, itertools, json, pathlib, sys
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
KS = [1, 2, 3, 4, 5, 6]
DRAWS = 20
R256 = {"full": 0.4440, "core": 0.6000}


def cls(y, tol_frac=1e-9):
    # ⚠ SECOND THING THE PLACEBO CAUGHT, AND IT REACHES BACK INTO R256.
    # The satisfaction tensor contains EXACT ties -- two responses with identical values -- and a
    # weak ordering records those as 0. An eigenvector does not: eigh returns components differing
    # at ~1e-17, and bare np.sign turns a genuine tie into +/-1. So the class of the rank-1
    # component was systematically finer than the class of the data, and every disagreement it
    # manufactured counted AGAINST agreement. R256's 0.4440 and 0.6000 were computed that way and
    # are therefore LOWER BOUNDS. Tolerance is relative to the vector's own range so it carries no
    # absolute scale assumption.
    y = np.asarray(y, float)
    tol = tol_frac * (float(y.max() - y.min()) or 1.0)
    return tuple(0.0 if abs(y[i] - y[j]) <= tol else float(np.sign(y[i] - y[j]))
                 for i, j in PAIRS)


def rank1_self(M):
    X = M - M.mean(1, keepdims=True)
    w, V = np.linalg.eigh(X.T @ X)
    o = np.argsort(w)[::-1]
    w, V = w[o], V[:, o]
    if float(w.sum()) <= 1e-12:
        # ⚠ THE PLACEBO CAUGHT THIS AND IT IS NOT A BUG -- it is a case with a defined answer that
        # I had not given it. A centred matrix of exactly zero means every row is CONSTANT across
        # the four responses, so the subset's own sum is constant too and its class is the
        # all-tied class. The rank-1 reconstruction of a constant IS that constant, so the two
        # agree: the answer is 1.0, not nan. Returning nan here poisoned the k=1 mean and would
        # have gone unnoticed at every k>=2, where two rows are rarely both flat.
        return 1.0
    comp = V[:, 0] * np.sign(float(V[:, 0] @ X.mean(0)) or 1.0)
    return float(cls(comp) == cls(M.sum(0)))


def row_permute(M, rng):
    o = M.copy()
    for i in range(len(o)):
        o[i] = o[i][rng.permutation(4)]
    return o


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    sc = r220.load_sat(R4 / "a04_core.npz")
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
        cj = sorted({k[0] for k in (sc.get(p) or {})})
        if not cj or not all((j, x) in sc[p] for j in cj for x in L):
            continue
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok])
        S = W[:, None] * np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        C = np.array([[sc[p][(j, x)] for x in L] for j in cj], float)
        P.append((S, C))
        if len(P) >= 250:
            break
    print("prompts %d | core sizes %s"
          % (len(P), dict(collections.Counter(len(C) for _S, C in P))))

    print("\n=== controls ===")
    rng = np.random.default_rng(0)
    q = rng.standard_normal(4)
    pos = [float(np.mean([rank1_self(np.array([rng.uniform(.3, 1.5) * q +
                                               0.01 * rng.standard_normal(4) for _ in range(k)]))
                          for _ in range(50)])) for k in KS]
    print(" POSITIVE synthetic rank-1 subsets, k=%s : %s  %s"
          % (KS, ["%.4f" % x for x in pos],
             "OK" if all(x > 0.99 for x in pos) else "STATISTIC CANNOT REACH ITS CEILING"))
    pl = float(np.mean([rank1_self(S[[0]]) for S, _C in P]))
    print(" PLACEBO  k=1 is rank one BY CONSTRUCTION : %.4f  %s"
          % (pl, "OK" if abs(pl - 1.0) < 1e-9 else "IMPLEMENTATION WRONG -- round is void"))
    pos_ok = all(x > 0.99 for x in pos) and abs(pl - 1.0) < 1e-9

    print("\n=== the sweep: rank-1 self-class agreement by SUBSET SIZE ===")
    print("%-4s %12s %12s %12s %12s" % ("k", "random", "spread", "row-perm null", "cross-prompt"))
    grid = {}
    for k in KS:
        rv, nv, sv = [], [], []
        for pi, (S, _C) in enumerate(P):
            if len(S) < k:
                continue
            r_ = [rank1_self(S[list(rng.choice(len(S), size=k, replace=False))])
                  for _ in range(DRAWS)]
            rv.append(float(np.mean(r_)))
            nv.append(float(np.mean([rank1_self(row_permute(
                S[list(rng.choice(len(S), size=k, replace=False))], rng)) for _ in range(5)])))
            oj = (pi + 1) % len(P)
            O = P[oj][0]
            if len(O) >= k:
                sv.append(float(np.mean([rank1_self(O[list(rng.choice(len(O), size=k,
                                                                      replace=False))])
                                         for _ in range(5)])))
        grid[k] = (float(np.mean(rv)), float(np.std(rv)), float(np.mean(nv)), float(np.mean(sv)))
        print("%-4d %12.4f %12.4f %12.4f %12.4f" % (k, *grid[k]))

    core_vals = [rank1_self(C) for _S, C in P]
    core = float(np.mean(core_vals))
    sizes = collections.Counter(len(C) for _S, C in P)
    kmode = sizes.most_common(1)[0][0]
    print("\n=== the size-matched comparison ===")
    print(" printed core (mean size %.2f, modal %d) : %.4f   [R256 reported %.4f]"
          % (float(np.mean([len(C) for _S, C in P])), kmode, core, R256["core"]))
    print(" random subsets at k=%d                   : %.4f  (draw spread %.4f)"
          % (kmode, grid[kmode][0], grid[kmode][1]))
    print(" full rubric, all criteria [R256]         : %.4f" % R256["full"])
    delta = core - grid[kmode][0]
    print(" core - random at matched size            : %+.4f" % delta)

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not pos_ok:
        v = ("UNVERIFIED -- the placebo (k=1 must be exactly 1.0000) or the synthetic ceiling did "
             "not behave; the statistic is not implemented correctly.")
    elif abs(delta) <= grid[kmode][1]:
        v = ("W-SIZE -- R256's core-vs-full rank-1 gap is RETRACTED AS A SIZE EFFECT. At matched "
             "size the printed core scores %.4f against random subsets' %.4f, a difference of "
             "%+.4f inside the draw spread of %.4f. The statistic falls from 1.0000 at k=1 to "
             "%.4f at k=6 BY CONSTRUCTION, so comparing a 4-criterion core to an 11-criterion "
             "rubric on it was comparing sizes. The sentence 'the core is more one-dimensional' "
             "may not be written in either direction."
             % (core, grid[kmode][0], delta, grid[kmode][1], grid[max(KS)][0]))
    elif delta > 0:
        v = ("W-COMPILER -- the printed core IS more one-dimensional than an arbitrary subset of "
             "the same size: %.4f vs %.4f, %+.4f against a draw spread of %.4f. That is a property "
             "of the compilation and no round has credited it."
             % (core, grid[kmode][0], delta, grid[kmode][1]))
    else:
        v = ("W-INVERTED -- the printed core is LESS one-dimensional than an arbitrary subset of "
             "the same size: %.4f vs %.4f, %+.4f. A finding in the direction nobody looked."
             % (core, grid[kmode][0], delta))
    print("\n  " + v)
    json.dump({"prompts": len(P), "core": core, "core_sizes": {str(k): v_ for k, v_ in sizes.items()},
               "grid": {str(k): list(grid[k]) for k in KS}, "delta_at_modal_size": delta,
               "controls": {"positive": pos, "placebo_k1": pl},
               "r256_published": R256, "verdict": v},
              open(OUT / "size_matched_rank1.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
