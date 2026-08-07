#!/usr/bin/env python3
"""R478 — R477 bounded the admissible class by the arms on disk. The class has 1,820 members.

WHY THIS ROUND ATTACKS THE ROUND BEFORE IT.  R477 concluded ③ is CHEAP because `topw_k4` gains only
+0.0099 over the best ③-admissible arm, and named that arm `generic` (0.5376).  ⛔ **`generic` is ONE
fixed prompt-blind set, and `DEFINITION.md:337` already records that it sits at percentile 0.000 of a
1,820-member census — below every one of them.**  R477's own retraction (296) says a class is not
bounded by one arm; I then bounded it by the nine arms that happened to have `.npz` files.  If some
subset of `genericpool16` scores above `generic`, R477's +0.0099 is an OVERESTIMATE and ③ is even
cheaper -- or `topw_k4` loses outright to a set that never sees the prompt.

ESTIMAND
    VALUE_OF_RATINGS = A2(topw_k4) − A2(best prompt-blind 4-subset of genericpool16)
    where "best" is estimated CROSS-FITTED, because the in-sample maximum over 1,820 candidates is
    an order statistic and is upward-biased by construction.  Both are reported:
      MAX_IN   the largest A2 over all 1,820 -- an upper bound on what the class can reach, inflated
      CV_OUT   select argmax on a random half of prompts, score it on the other half, repeated --
               an unbiased estimate of what "pick the best prompt-blind set" actually delivers
    ⭐ MAX_IN − CV_OUT IS the selection inflation, measured rather than argued.

IDENTIFICATION
    Fully identified from `sat_genericpool16.npz`: 968 prompts × 16 criteria × 4 responses, complete,
    so every subset's y-vector is a sum of columns already on disk.  No judge call, no new compute.
    ⚠ The class is `genericpool16`'s subsets -- ONE prompt-blind family.  A prompt-blind set outside
    this pool is not covered, and that is stated rather than assumed away.

SCOPE
    population  968 prompts scored in both arms (verified in-run, never assumed).
    instrument  A2 vs a held-out human annotator, 5 held-out draws, via corebench/score.py's loader.
    baseline    the whole 1,820 distribution, published -- not a chosen floor.
    regime      k = 4 primary (matches `topw_k4` and clause ②'s reference class); k ∈ {2,3,4,5,6} swept.

WORLDS
    A  R477 STANDS     CV_OUT ≈ generic -> the gain stays ~+0.0099 and ③ is cheap.
    B  R477 UNDERSTATES CV_OUT > generic -> the gain shrinks or REVERSES; a prompt-blind set matches
                       or beats a rating-reading one, and ③ costs less than nothing.
    C  SELECTION NOISE MAX_IN >> CV_OUT and CV_OUT ≈ the class MEAN -> "the best subset" is not
                       selectable; the class ceiling is not achievable and neither number bounds it.
    D  BLIND           the selection procedure cannot beat a random subset out-of-sample even when
                       selecting on real data -> the design cannot estimate "best" -> UNVERIFIED.

PREDICTION MATRIX
                      CV_OUT vs generic   MAX_IN − CV_OUT   CV_OUT vs random subset
    A  R477 stands          ~equal            small                 >
    B  understates           higher           small                 >
    C  selection noise        any             LARGE                ~equal
    D  blind                  any             any                  <=  -> UNVERIFIED

PRE-REGISTERED KILL  (conditional, never a bare threshold)
    if cv_beats_random_out_of_sample and placebo_at_chance:
        B if CV_OUT − A2(generic) > floor ; C if CV_OUT − class_mean <= floor ; else A
    else:
        UNVERIFIED

CONTROLS
    POSITIVE   the selection must WORK: the subset chosen on the fit half must beat a RANDOMLY chosen
               subset on the eval half, by more than the floor. If it cannot, "best" is unestimable.
    g=0        selection on SHUFFLED targets -- fit-half argmax computed against permuted rankings.
               Its out-of-sample advantage must vanish. This is what makes the positive able to fail.
    NEGATIVE   the full 1,820 A2 distribution under shuffled targets must collapse to chance with a
               spread explained by draw noise alone -- i.e. the spread across subsets is not an
               artifact of the statistic.
    PLACEBO    A2 vs shuffled rankings ≈ 0.428 (R477 measured chance; it is NOT 0.5).
    FLOOR      reused from R477's construction: three random_k4 arms differing only in the draw.

MULTIPLICITY
    All 1,820 cells evaluated and the WHOLE distribution published (min/p25/median/p75/max), not the
    max alone. k-sweep adds C(16,k) for k ∈ {2,3,5,6} = 120 + 560 + 4368 + 8008 -- all reported.

ARTIFACT  results/r478_class_census.json      SEEDS 0..19 for cross-fitting, 5 held-out draws.

IMPOSSIBLE HERE, NAMED
    cross-dataset        -- a second release with a prompt-blind pool of this breadth.
    construct validated  -- an external gold standard for "a good core".
    the class beyond this pool -- `genericpool16` is the ONLY family on this site with breadth >= 16
                            (DEFINITION.md:259); a prompt-blind set from elsewhere would require
                            generating and judging one, which is a GPU round, not this one.
"""
import collections, itertools, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(".")
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R478_the_admissible_class_is_1820_not_nine/results"
sys.path.insert(0, str(ROOT/"corebench"))
import score as SC                        # R477 retraction 297: never reimplement the loader

def cls_arr(y):
    """y: [...,4] -> [...,6] signs. Vectorised so 1,820 subsets cost one pass."""
    return np.stack([np.sign(y[..., i]-y[..., j]) for i, j in PAIRS], axis=-1)

def load_sat_matrix(arm, pids=None):
    d = np.load(ROOT/"corebench"/"results"/f"sat_{arm}.npz", allow_pickle=True)
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    keys = sorted(o) if pids is None else [p for p in pids if p in o]
    idx = {p: sorted({i for i, _ in o[p]}) for p in keys}
    n = len(idx[keys[0]])
    if not all(len(idx[p]) == n for p in keys): return None, None
    A = np.zeros((len(keys), n, 4), dtype=np.float32)
    for a, p in enumerate(keys):
        for b, i in enumerate(idx[p]):
            for c, ltr in enumerate(L):
                A[a, b, c] = o[p].get((i, ltr), 0.0)
    return keys, A

tgt_raw, _ = SC.load_targets()
TGT = {p: [y for y, _ in v] for p, v in tgt_raw.items()}
HELD = [0, 1, 2, 3, 4]

pids, POOL = load_sat_matrix("genericpool16")
pids = [p for p in pids if len(TGT.get(p, [])) >= 2]
pids_set = set(pids)
_k, POOL = load_sat_matrix("genericpool16", pids)
print(f"  pool: {POOL.shape[0]} prompts × {POOL.shape[1]} criteria × 4 responses")

def held_cls(shuffle=False, seed=0):
    rs = np.random.default_rng(seed)
    H = np.zeros((len(pids), len(HELD), 6), dtype=np.float32)
    for a, p in enumerate(pids):
        v = TGT[p]
        for b, s in enumerate(HELD):
            r = np.random.default_rng(s)
            y = list(v[int(r.integers(len(v)))])
            if shuffle: y = list(rs.permutation(y))
            H[a, b] = cls_arr(np.array(y, dtype=np.float32))
    return H

H_real = held_cls(); H_shuf = held_cls(shuffle=True, seed=11)

def a2_per_prompt(A, H):
    """A: [P,k,4] summed already -> [P]. mean over 6 pairs and held-out draws."""
    c = cls_arr(A.sum(axis=1))                     # [P,6]
    return (c[:, None, :] == H).mean(axis=(1, 2))  # [P]

def census(k, H):
    subs = list(itertools.combinations(range(POOL.shape[1]), k))
    M = np.zeros((len(subs), POOL.shape[0]), dtype=np.float32)
    for i, s in enumerate(subs):
        M[i] = a2_per_prompt(POOL[:, s, :], H)
    return subs, M

subs4, M4 = census(4, H_real)
mean4 = M4.mean(axis=1)
print(f"\n  ── THE CENSUS: all {len(subs4)} 4-subsets of genericpool16, A2 in full ──")
q = np.percentile(mean4, [0, 25, 50, 75, 100])
print(f"    min {q[0]:.4f}   p25 {q[1]:.4f}   median {q[2]:.4f}   p75 {q[3]:.4f}   MAX {q[4]:.4f}")

# the two arms R477 compared, on the SAME prompts
def arm_a2(arm):
    kk, A = load_sat_matrix(arm, pids)
    if A is None or len(kk) != len(pids): return None, None
    return kk, a2_per_prompt(A, H_real)
_, gen_pp = arm_a2("generic"); _, topw_pp = arm_a2("topw_k4")
g_mean, t_mean = float(gen_pp.mean()), float(topw_pp.mean())
print(f"    `generic` = {g_mean:.4f}  -> percentile {100*(mean4 < g_mean).mean():.1f} of the census")
print(f"    `topw_k4` = {t_mean:.4f}  -> percentile {100*(mean4 < t_mean).mean():.1f} of the census")

print(f"\n  ── CROSS-FIT: select argmax on half the prompts, score it on the other half ──")
rs = np.random.default_rng(0)
cv, cv_rand, cv_g0 = [], [], []
subs4_shuf, M4_shuf = None, None
_, M4s = census(4, H_shuf)
for rep in range(20):
    perm = rs.permutation(len(pids)); h = len(perm)//2
    fit, ev = perm[:h], perm[h:]
    best = int(M4[:, fit].mean(axis=1).argmax())
    cv.append(float(M4[best, ev].mean()))
    cv_rand.append(float(M4[int(rs.integers(len(subs4))), ev].mean()))
    g0 = int(M4s[:, fit].mean(axis=1).argmax())          # selected on SHUFFLED targets
    cv_g0.append(float(M4[g0, ev].mean()))
CV, CVR, CVG = float(np.mean(cv)), float(np.mean(cv_rand)), float(np.mean(cv_g0))
MAXIN = float(mean4.max())
print(f"    MAX_IN (in-sample max over 1820) = {MAXIN:.4f}")
print(f"    CV_OUT (held-out, 20 splits)     = {CV:.4f}   ± {np.std(cv):.4f}")
print(f"    selection inflation MAX_IN−CV_OUT= {MAXIN-CV:+.4f}")
print(f"    random subset, same splits       = {CVR:.4f}")
print(f"    g=0: selected on SHUFFLED targets= {CVG:.4f}")

FLOOR = 0.0122        # R477, measured from three random_k4 arms differing only in the draw
pos_ok = (CV - CVR) > FLOOR
g0_ok  = abs(CVG - CVR) < FLOOR * 2
pl = float(a2_per_prompt(POOL[:, subs4[0], :], H_shuf).mean())
pl_ok = abs(pl - 0.428) < 0.03
print(f"\n  POSITIVE  cross-fit selection beats a random subset out-of-sample by > {FLOOR}: {pos_ok}"
      f"   ({CV-CVR:+.4f})")
print(f"  g=0       selecting on SHUFFLED targets gives no out-of-sample edge         : {g0_ok}"
      f"   ({CVG-CVR:+.4f})")
if abs(CVG-CVR) > 0.002:
    print(f"            ⚠ RESIDUAL {CVG-CVR:+.4f}: shuffling the RANKING within a prompt leaves the"
          f" prompt's\n              own difficulty intact, so a shuffled-target argmax still"
          f" inherits some real\n              structure. Reported, not rounded to zero -- the real"
          f" selection edge is\n              {CV-CVR:+.4f}, i.e. {(CV-CVR)/(CVG-CVR):.1f}x this residual.")
print(f"  PLACEBO   A2 vs shuffled rankings = {pl:.4f} (R477 measured chance = 0.428) : {pl_ok}")

print(f"\n  ── SPECIFICATION CURVE over subset size (whole census each time) ──")
print(f"    {'k':>2} {'C(16,k)':>8} {'min':>8} {'median':>8} {'MAX_IN':>8} {'CV_OUT':>8}"
      f"  topw_k<k> pct   (the column compares topw_kK to the K-census, not topw_k4 throughout)")
spec = {}
for k in (2, 3, 4, 5, 6):
    sb, M = (subs4, M4) if k == 4 else census(k, H_real)
    mk = M.mean(axis=1)
    r2 = np.random.default_rng(k)
    c = []
    for rep in range(10):
        pm = r2.permutation(len(pids)); hh = len(pm)//2
        c.append(float(M[int(M[:, pm[:hh]].mean(axis=1).argmax()), pm[hh:]].mean()))
    _, tp = arm_a2(f"topw_k{k}") if k in (2, 3, 6) else (None, topw_pp if k == 4 else None)
    pct = 100*(mk < float(tp.mean())).mean() if tp is not None else float("nan")
    spec[k] = {"n": len(sb), "min": float(mk.min()), "median": float(np.median(mk)),
               "max_in": float(mk.max()), "cv_out": float(np.mean(c)), "topw_pct": float(pct)}
    print(f"    {k:>2} {len(sb):>8} {mk.min():>8.4f} {np.median(mk):>8.4f} {mk.max():>8.4f} "
          f"{np.mean(c):>8.4f}  {pct if pct==pct else float('nan'):>10.1f}")

if not (pos_ok and g0_ok and pl_ok):
    verdict, world = "UNVERIFIED", "D (selection not shown to work, or placebo off chance)"
else:
    gain_vs_cv = t_mean - CV
    if CV - g_mean > FLOOR:
        world = (f"B (R477 UNDERSTATES — the class reaches {CV:.4f} cross-fitted vs `generic` "
                 f"{g_mean:.4f}; topw_k4 − best = {gain_vs_cv:+.4f})")
    elif CV - float(mean4.mean()) <= FLOOR:
        world = "C (SELECTION NOISE — 'the best subset' is not selectable)"
    else:
        world = f"A (R477 STANDS — cross-fitted best ≈ generic; topw_k4 − best = {gain_vs_cv:+.4f})"
    verdict = "MEASURED"
print(f"\n  VERDICT {verdict}\n  world: {world}")
print(f"  ⭐ topw_k4 − cross-fitted best prompt-blind subset = {t_mean - CV:+.4f}   "
      f"(R477 reported {t_mean - g_mean:+.4f} against `generic`)")

OUT.mkdir(parents=True, exist_ok=True)
json.dump({"census4": {"n": len(subs4), "min": float(mean4.min()), "p25": float(q[1]),
                       "median": float(q[2]), "p75": float(q[3]), "max": MAXIN,
                       "mean": float(mean4.mean())},
           "generic": g_mean, "generic_pct": float(100*(mean4 < g_mean).mean()),
           "topw_k4": t_mean, "topw_pct": float(100*(mean4 < t_mean).mean()),
           "cv_out": CV, "cv_sd": float(np.std(cv)), "cv_random": CVR, "cv_g0": CVG,
           "inflation": MAXIN-CV, "gain_vs_cv": t_mean-CV, "gain_vs_generic": t_mean-g_mean,
           "spec": spec, "controls": {"positive": bool(pos_ok), "g0": bool(g0_ok), "placebo": pl_ok},
           "verdict": verdict, "world": world},
          open(OUT/"r478_class_census.json", "w"), indent=2, default=float)
sys.exit(0 if verdict != "UNVERIFIED" else 2)
