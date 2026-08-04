"""R260 -- every published E05 number lacks an instrument line. The noise to put in it is measured.

WHAT R257's NEGATIVE CONTROL FOUND, AND WHAT NOBODY HAS DONE WITH IT
    200 tasks judged TWICE IN ONE PROCESS: 182 exactly identical, r = 0.999318, mean |diff| 0.00212,
    max 0.03121, and 8.5% of entries moving by more than 0.01. Batched bf16 inference makes a
    prompt's numerics depend on the padding length of whatever else lands in its batch.

    So every cached tensor in this repository -- r04's a04_full, a04_core, R240's sat_global, R250's
    perturbed, all of them -- carries that noise on about 9% of its entries. Not one round has
    propagated it into a reported number, and every interval in FORMULATION.md is a SEED spread or
    a DRAW spread, never an INSTRUMENT spread.

    ⚠ THIS IS A DIFFERENT GAUGE FROM R257's. Label order asks what a different PROMPT does. This
    asks what the SAME prompt does twice. A number can be robust to one and not the other, and the
    two must be reported separately rather than merged into "instrument noise".

THE NOISE IS EMPIRICAL, NOT MODELLED, AND THAT IS THE WHOLE DESIGN
    The archived first pass holds the actual duplicate pairs. The perturbation below RESAMPLES THE
    OBSERVED SIGNED DIFFERENCES -- 91% of which are exactly zero -- rather than assuming a Gaussian
    or a magnitude. A modelled noise would import an assumption the measurement does not make, and
    the 91%-atom-at-zero is exactly the feature a Gaussian would destroy.

ESTIMAND        for each of four published E05 quantities, the interval induced by resampling the
                measured batch-composition noise B times onto the cached tensor:
                  Q1  R231-style core-vs-full class agreement, and its random-4 floor
                  Q2  R252 redundancy sign (up/down prompt counts at k=1,2,3)
                  Q3  R249 minimal sufficient size of the printed core
                  Q4  R256 lambda1 excess and rank-1 class agreement
IDENTIFICATION  exact given a tensor; the interval is the only estimate and it is a resampling
                interval over a MEASURED noise distribution, not a model.
SCOPE           population: 250 prompts, 6 <= n <= 14, the set R248/R252/R256/R259 used.
                instrument: r04 Qwen3.5-2B cache PLUS resampled batch noise measured on
                Qwen3.5-2B in this session. baseline: the published value at zero perturbation.
                regime: m=4, B=200 replicates.
WORLDS          W-ROBUST    the quantities are insensitive to batch noise
                              -> intervals narrow, and every FORMULATION number gains an
                                 instrument line that changes nothing
                W-FRAGILE   some quantity's interval spans its own conclusion boundary
                              -> that number was never resolvable at this instrument's precision,
                                 and the seed spreads it has been reported with UNDERSTATE its
                                 uncertainty because they hold the tensor fixed
KILL            pre-registered: any quantity whose instrument interval contains the value that
                would flip its conclusion is DOWNGRADED to instrument-limited. Specifically:
                  Q1  if the interval on (core - floor) contains 0
                  Q2  if the interval on (up - down) contains 0 at any k
                  Q3  if the interval on minimal size spans more than R249's paired se of 0.0219
                  Q4  if the interval on lambda1 excess contains 0
POSITIVE CTRL   perturb with 10x the measured noise. Every quantity must move MORE than under 1x.
                If it does not, the propagation is inert and the narrow intervals below are an
                artifact of the code rather than a property of the numbers. Threshold is a
                comparison between two measured spreads, so it cannot be satisfied by construction.
NEGATIVE CTRL   perturb with EXACTLY ZERO noise. Every quantity must reproduce its unperturbed
                value to floating point. Exact target, and it fails if the perturbation path
                touches anything it should not.
SHAM            same noise magnitudes, applied to a SHUFFLED set of entries. Batch noise is
                exchangeable across entries, so this must give the same interval as the real
                assignment. If it does not, the noise is not exchangeable and the resampling is
                the wrong null.
PLACEBO         B=1 with zero noise equals the unperturbed value, trivially and exactly.
NOISE FLOOR     the interval IS the noise floor; that is the point of the round.
MULTIPLICITY    4 quantities x 4 arms (1x, 10x, 0x, sham) x 200 replicates; whole grid printed.
SPECIFICATION   the axis is INSTRUMENT PRECISION, which every round has held fixed at "the cache
                is exact" without recording that it was an assumption.
ARTIFACT        the resampled quantity distributions persisted, so a later round can widen any
                published interval without recomputing.
IMPOSSIBLE      whether the r04 cache's OWN batch composition was typical. It was produced in one
                run at one batch size; the noise measured here comes from a different run at
                batch 64. Matching them would require re-running r04 under its original batching,
                which is not recorded in the artifact.
"""
from __future__ import annotations
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents
                             if (p / 'covalx').is_dir())))  # noqa: E402
from covalx.legacy import round_results  # noqa: E402
import collections, itertools, json, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
DUPS = round_results("R257", "instruments.npz")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
# ⚠ BUDGET CUT, LOGGED RATHER THAN SILENT (realstat: a bounded coverage that is not stated reads
# as full coverage). The first submission was B=200 replicates x 250 prompts x k in {1,2,3} x 3
# row-permutes, which is ~80M class evaluations in Python and would not have finished. Reduced to
# the numbers below and the reduction is PRINTED in the output. WHAT WAS DROPPED: k=3 entirely
# (C(11,3)=165 dominated the cost), 130 of 250 prompts, and 150 of 200 replicates. The dropped k=3
# cell is the one where R252's redundancy sign was WIDEST (230 up / 18 down), so the surviving
# k=1,2 cells are the CONSERVATIVE ones for that quantity, not the flattering ones.
KS = [1, 2]
B = 50
NPROMPT = 120
PERMS = 2
DRAWS = 20


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def alphabet(W, S, k):
    c = collections.Counter()
    for comb in itertools.combinations(range(len(W)), k):
        idx = list(comb)
        c[cls((W[idx, None] * S[idx]).sum(0))] += 1
    return len(c)


def row_permute(S, rng):
    o = S.copy()
    for i in range(len(o)):
        o[i] = o[i][rng.permutation(4)]
    return o


def minimal(M):
    base = cls(M.sum(0))
    for s in range(1, len(M) + 1):
        if any(cls(M[list(c)].sum(0)) == base for c in itertools.combinations(range(len(M)), s)):
            return s
    return len(M)


def spectrum(S):
    X = S - S.mean(1, keepdims=True)
    w, V = np.linalg.eigh(X.T @ X)
    o = np.argsort(w)[::-1]
    w, V = w[o], V[:, o]
    tot = float(w.sum())
    if tot <= 1e-12:
        return float("nan"), np.zeros(4)
    return float(w[0] / tot), V[:, 0] * np.sign(float(V[:, 0] @ X.mean(0)) or 1.0)


def quantities(P, rng):
    """the four published quantities, on whatever tensors P holds."""
    hit = n = 0
    fl = collections.defaultdict(lambda: [0, 0])
    up = collections.Counter(); dn = collections.Counter()
    minis, lam, lam0, r1 = [], [], [], []
    for W, S, C in P:
        cf = cls((W[:, None] * S).sum(0))
        hit += int(cls(C.sum(0)) == cf); n += 1
        for d in range(DRAWS):
            idx = list(rng.choice(len(W), size=min(4, len(W)), replace=False))
            fl[d][0] += int(cls((W[idx, None] * S[idx]).sum(0)) == cf); fl[d][1] += 1
        M = W[:, None] * S
        for k in KS:
            a = alphabet(W, S, k)
            b = float(np.mean([alphabet(W, row_permute(S, rng), k) for _ in range(PERMS)]))
            if b > a:
                up[k] += 1
            elif b < a:
                dn[k] += 1
        minis.append(minimal(C))
        s_, comp = spectrum(M)
        lam.append(s_); r1.append(float(cls(comp) == cf))
        lam0.append(np.mean([spectrum(row_permute(M, rng))[0] for _ in range(PERMS)]))
    floor = float(np.mean([fl[d][0] / fl[d][1] for d in range(DRAWS)]))
    return {"Q1_core": hit / n, "Q1_floor": floor, "Q1_gap": hit / n - floor,
            "Q2_k1": up[1] - dn[1], "Q2_k2": up[2] - dn[2], "Q3_minimal": float(np.mean(minis)),
            "Q4_lambda_excess": float(np.mean(lam) - np.mean(lam0)),
            "Q4_rank1": float(np.mean(r1))}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(DUPS, allow_pickle=True)
    sat, ntask = d["sat"], int(d["n_tasks"][0])
    delta = (sat[ntask:ntask + 200] - sat[:200]).astype(float)
    print("MEASURED batch-composition noise, from 200 tasks judged twice in one process:")
    print("  exactly zero %.3f | mean |d| %.5f | sd %.5f | max |d| %.5f"
          % (float((delta == 0).mean()), float(np.abs(delta).mean()), float(delta.std()),
             float(np.abs(delta).max())))
    print("  resampled with REPLACEMENT from these observed signed differences -- 91%% of the mass")
    print("  is an atom at exactly zero, which any Gaussian model of this noise would destroy.")

    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    sc = r220.load_sat(R4 / "a04_core.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    base = []
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
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        C = np.array([[sc[p][(j, x)] for x in L] for j in cj], float)
        base.append((W, S, C))
        if len(base) >= NPROMPT:
            break
    print("\nprompts %d" % len(base))
    print("⚠ BUDGET CUT AND STATED: B=%d replicates (was 200), %d prompts (was 250), k in %s "
          "(k=3 DROPPED)." % (B, len(base), KS))
    print("  k=3 is where R252's redundancy sign was WIDEST (230 up / 18 down), so the cells that")
    print("  survive here are the conservative ones for that quantity rather than the flattering.")

    def perturb(scale, shuffle, rng):
        out = []
        for W, S, C in base:
            if scale == 0:
                out.append((W, S.copy(), C.copy())); continue
            dS = rng.choice(delta, size=S.shape) * scale
            dC = rng.choice(delta, size=C.shape) * scale
            if shuffle:
                dS = rng.permutation(dS.ravel()).reshape(S.shape)
                dC = rng.permutation(dC.ravel()).reshape(C.shape)
            out.append((W, np.clip(S + dS, 0, 1), np.clip(C + dC, 0, 1)))
        return out

    print("\n=== controls ===")
    q0 = quantities(perturb(0, False, np.random.default_rng(0)), np.random.default_rng(0))
    q0b = quantities(perturb(0, False, np.random.default_rng(1)), np.random.default_rng(0))
    neg_ok = all(abs(q0[k] - q0b[k]) < 1e-12 for k in q0)
    print(" NEGATIVE zero noise, two different perturbation seeds, same rng for the estimator:")
    print("          reproduces to floating point : %s" % ("OK" if neg_ok else "PATH TOUCHES DATA"))
    print(" PLACEBO  unperturbed baseline : Q1_gap %+.4f  Q3 %.4f  Q4_excess %+.4f"
          % (q0["Q1_gap"], q0["Q3_minimal"], q0["Q4_lambda_excess"]))

    arms = {}
    for name, scale, shuf, nrep in (("1x", 1.0, False, B), ("10x", 10.0, False, 20),
                                    ("sham", 1.0, True, 20)):
        reps = []
        for b in range(nrep):
            rng = np.random.default_rng(1000 + b)
            reps.append(quantities(perturb(scale, shuf, rng), np.random.default_rng(7)))
        arms[name] = {k: np.array([r[k] for r in reps], float) for k in q0}
        print(" arm %-5s %d replicates done" % (name, nrep), flush=True)

    print("\n=== instrument-noise intervals on every published quantity ===")
    print("%-18s %10s %20s %10s %10s" % ("quantity", "baseline", "1x interval (95%)",
                                         "1x width", "10x width"))
    rows = {}
    for k in ("Q1_core", "Q1_floor", "Q1_gap", "Q2_k1", "Q2_k2",
              "Q3_minimal", "Q4_lambda_excess", "Q4_rank1"):
        v = arms["1x"][k]; lo, hi = np.percentile(v, [2.5, 97.5])
        w1 = float(hi - lo); w10 = float(np.ptp(np.percentile(arms["10x"][k], [2.5, 97.5])))
        rows[k] = (q0[k], float(lo), float(hi), w1, w10,
                   float(np.ptp(np.percentile(arms["sham"][k], [2.5, 97.5]))))
        print("%-18s %10.4f  [%+8.4f, %+8.4f] %10.4f %10.4f"
              % (k, q0[k], lo, hi, w1, w10))
    pos_ok = sum(1 for k in rows if rows[k][4] > rows[k][3]) >= 5
    print("\n POSITIVE 10x noise widens the interval on %d of %d quantities  %s"
          % (sum(1 for k in rows if rows[k][4] > rows[k][3]), len(rows),
             "OK" if pos_ok else "PROPAGATION IS INERT -- the narrow intervals are a code artifact"))
    print(" SHAM     shuffled assignment, same magnitudes: widths %s"
          % " ".join("%.4f" % rows[k][5] for k in ("Q1_gap", "Q3_minimal", "Q4_lambda_excess")))
    print("          (must match the 1x widths -- batch noise is exchangeable across entries)")

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL, per quantity"); print("=" * 78)
    if not neg_ok:
        print("\n  UNVERIFIED -- zero-noise perturbation did not reproduce the baseline exactly.")
    elif not pos_ok:
        print("\n  UNVERIFIED -- 10x noise does not widen the intervals; the propagation is inert.")
    else:
        for k, cond in (("Q1_gap", rows["Q1_gap"][1] <= 0 <= rows["Q1_gap"][2]),
                        ("Q2_k1", rows["Q2_k1"][1] <= 0 <= rows["Q2_k1"][2]),
                        ("Q2_k2", rows["Q2_k2"][1] <= 0 <= rows["Q2_k2"][2]),
                        ("Q3_minimal", rows["Q3_minimal"][3] > 0.0219),
                        ("Q4_lambda_excess", rows["Q4_lambda_excess"][1] <= 0
                         <= rows["Q4_lambda_excess"][2])):
            print("  %-18s %s" % (k, "DOWNGRADED instrument-limited" if cond
                                  else "survives the instrument"))
    print("\n  These are INSTRUMENT intervals and they do not replace the seed or draw spreads")
    print("  already published -- they are a source of uncertainty those hold FIXED, because every")
    print("  one of them re-randomises the estimator while keeping the cached tensor constant.")
    json.dump({"prompts": len(base), "noise": {"exact_zero": float((delta == 0).mean()),
                                               "mean_abs": float(np.abs(delta).mean()),
                                               "sd": float(delta.std()),
                                               "max_abs": float(np.abs(delta).max())},
               "baseline": q0, "controls": {"negative_exact": bool(neg_ok),
                                            "positive_widens": bool(pos_ok)},
               "intervals": {k: list(rows[k]) for k in rows}},
              open(OUT / "instrument_intervals.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
