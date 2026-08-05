#!/usr/bin/env python3
"""R480 — the judge moves every LEVEL. Does it move the ORDER?

WHY THIS AND NOT THE GRADIENT I ANNOUNCED.  R479 closed by proposing to select criteria to maximise
ATTAINMENT rather than A2.  ⛔ **That is void by algebra, not by measurement.**  attainment =
(A2 − chance)/(BAYES − chance), and both constants are properties of the human target, so the map is
affine with slope 1/(BAYES−chance) = 5.3997 > 0 and `argmax` is invariant under it.  Maximising
attainment IS maximising A2.  Killed at rung 1 of the attack ladder, zero compute.  **Labelled a
DERIVATION, not a finding.**

THE REPLACEMENT, and it is definitional rather than metric.  Clause ② reads *"better than the best
generalising prompt-blind set"* — a COMPARATIVE.  R479 showed the judge owns most of the level.  If
the judge preserves ORDER, "better than" is judge-invariant and ② can be stated without naming J.  If
order flips, ② is judge-relative at its core and no comparative in this definition is safe.

ESTIMAND
    SIGN_SURVIVAL = P( sign(A2_08B(a) − A2_08B(b)) == sign(A2_2B(a) − A2_2B(b)) )
    over arm pairs (a,b) that are RESOLVED under the 2B judge, i.e. |Δ_2B| > floor.
    ⚠ Restricting to resolved pairs is the whole identification argument: a pair whose 2B difference
    sits inside the floor can flip for free, and including such pairs would drive the statistic toward
    0.5 for reasons that have nothing to do with the judge.

IDENTIFICATION
    32 arms carry both judges; C(32,2) = 496 pairs, of which the resolved subset is counted in-run.
    ⚠ The arms are NOT independent -- random_k4_s0/s1/s2 are the same rule at three seeds, and the
    topw_k ladder is one rule at seven budgets. So a Spearman over all 32 would be inflated by the
    k-gradient. The pair-sign statistic is reported per STRATUM (within-family vs across-family) as
    well as pooled, and the pooled number is never quoted alone.

SCOPE
    population  prompts scored by BOTH judges for BOTH arms of a pair; counted per pair, never assumed.
    instrument  A2 vs a held-out human annotator, 20 draws; the two judges are Qwen3.5-2B and -0.8B.
    baseline    the split-half PLACEBO below -- the agreement achievable when the judge does NOT change.
    regime      k ∈ {1,2,3,4,6,8,12}; 6 selector families.

WORLDS
    A  NUISANCE   order survives -- sign survival near the split-half placebo. The judge is a level
                  shift and ②'s comparative is safe without J. Predicts: survival ≈ placebo.
    B  ORDINAL    order breaks -- survival far below the placebo but above 0.5. The judge changes
                  what counts as better, and ② must name J. Predicts: survival between 0.5 and placebo.
    C  DESTROYED  survival ≈ 0.5 on resolved pairs. The two judges rank arms independently, and no
                  comparative claim in this campaign transfers.
    D  UNREADABLE the split-half placebo is itself near 0.5 -> the estimate is too noisy to detect
                  any order at all, and every number above is silence. -> UNVERIFIED.

PREDICTION MATRIX
                    survival (resolved)   vs split-half placebo   what it licenses
    A  nuisance          high                  ≈ equal            ② stated as a comparative, no J
    B  ordinal           middling              well below         ② must carry J -- it already does
    C  destroyed          ~0.5                 far below          no comparative transfers at all
    D  unreadable         any                  placebo ~0.5       UNVERIFIED

PRE-REGISTERED KILL  (conditional, never a bare threshold)
    if placebo_resolves_order and negative_is_null:
        A if survival >= placebo − floor_on_a_proportion
        C if survival <= 0.55
        B otherwise
    else:
        UNVERIFIED

CONTROLS
    POSITIVE   the largest-|Δ| pairs under 2B (oracle vs random) must keep their sign under 0.8B. A
               judge swap that flips even those is measuring nothing.
    g=0        pairs UNRESOLVED under 2B (|Δ| <= floor) must survive at ~0.5. This is what makes the
               positive able to fail: a statistic that reports high survival everywhere, including
               where there is no true order, is not measuring order.
    NEGATIVE   arm labels shuffled within the 0.8B judge -> survival must fall to ~0.5.
    PLACEBO ⭐ SPLIT-HALF SAME JUDGE. Split the prompts in two and treat the halves as "two judges".
               This is the agreement attainable when the judge does NOT change, so it separates
               "the judges disagree" from "the estimate is noisy". Without it, low survival is
               uninterpretable -- and it is the control this round exists to carry.
    FLOOR      on A2 differences: 0.0122 (R477). On a PROPORTION: computed here by bootstrap.

MULTIPLICITY  the resolution threshold is swept at 1×, 2×, 3× floor; all cells reported.

ARTIFACT  results/r480_order.json          20 held-out draws; 200 bootstrap resamples; seeds 0..9.

IMPOSSIBLE HERE, NAMED
    a third judge   -- this site has exactly two, so "is 2B or 0.8B the outlier" is unanswerable.
    cross-architecture -- both judges are Qwen3.5; a different family would need a new judging run.
    construct validated -- whether either judge's ordering is the RIGHT one needs a gold standard.
"""
import collections, itertools, json, pathlib, sys, zlib
import numpy as np

ROOT = pathlib.Path("."); L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R480_does_the_judge_change_the_order_or_only_the_level/results"
sys.path.insert(0, str(ROOT/"corebench")); import score as SC
FLOOR = 0.0122

def cls(y): return tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
tgt_raw, _ = SC.load_targets()
TGT = {p: [tuple(y) for y, _ in v] for p, v in tgt_raw.items()}

ARMS = ["oracle_k4", "greedy_k4_fit1", "indep_k4_fit1", "topabs_k4", "topvar_k4", "topwvar_k4"] \
     + [f"topw_k{k}" for k in (1, 2, 3, 4, 6, 8, 12)] \
     + [f"random_k{k}_s{s}" for k in (2, 3, 4, 6, 8, 12) for s in (0, 1, 2)]

def family(a):
    if a.startswith("random"): return "random"
    if a.startswith("topw_k"): return "topw"
    return a

def per_prompt(arm, sfx):
    f = ROOT/"corebench"/"results"/f"sat_{arm}{sfx}.npz"
    if not f.exists(): return None
    d = np.load(f, allow_pickle=True)
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    out = {}
    for p, cells in o.items():
        v = TGT.get(p)
        if not v: continue
        idxs = sorted({i for i, _ in cells})
        c = cls(np.array([sum(cells.get((i, x), 0.0) for i in idxs) for x in L]))
        # ⛔ NOT `hash(p)`. Python salts string hashing with PYTHONHASHSEED, so the per-prompt
        # annotator draw differed between processes and every number in this round moved between
        # two runs (g=0 0.4375 -> 0.4247, negative 0.5031 -> 0.5082). §5 requires two seeds
        # byte-identical; a salted hash makes that impossible and the drift is invisible in one run.
        r = np.random.default_rng(zlib.crc32(p.encode()))
        out[p] = float(np.mean([np.mean([c[t] == cls(v[int(r.integers(len(v)))])[t]
                                         for t in range(6)]) for _ in range(20)]))
    return out

J2 = {a: per_prompt(a, "") for a in ARMS}
J8 = {a: per_prompt(a, "_08b") for a in ARMS}
ARMS = [a for a in ARMS if J2.get(a) and J8.get(a)]
COMMON = sorted(set.intersection(*[set(J2[a]) for a in ARMS], *[set(J8[a]) for a in ARMS]))
print(f"  arms with BOTH judges: {len(ARMS)}   common prompts: {len(COMMON)}   "
      f"pairs: {len(ARMS)*(len(ARMS)-1)//2}")
V2 = {a: np.array([J2[a][p] for p in COMMON]) for a in ARMS}
V8 = {a: np.array([J8[a][p] for p in COMMON]) for a in ARMS}
M2 = {a: float(v.mean()) for a, v in V2.items()}
M8 = {a: float(v.mean()) for a, v in V8.items()}

def survival(m_ref, m_test, thresh, shuffle=False, seed=0):
    """-> (survival, n_resolved). RESOLVED is judged on m_ref; the sign is read off m_test."""
    keys = list(m_ref)
    if shuffle:
        rs = np.random.default_rng(seed)
        vals = [m_test[k] for k in keys]; rs.shuffle(vals)
        m_test = dict(zip(keys, vals))
    ok = n = 0
    strat = collections.Counter(); strat_ok = collections.Counter()
    for a, b in itertools.combinations(keys, 2):
        d = m_ref[a]-m_ref[b]
        if abs(d) <= thresh: continue
        n += 1
        s = "within" if family(a) == family(b) else "across"
        strat[s] += 1
        good = np.sign(d) == np.sign(m_test[a]-m_test[b])
        ok += good; strat_ok[s] += good
    return (ok/n if n else float("nan"), n,
            {s: (strat_ok[s]/strat[s] if strat[s] else float("nan"), strat[s]) for s in strat})

# ---- PLACEBO ⭐ split-half of the SAME judge: agreement when the judge does NOT change -----------
rs = np.random.default_rng(0); pl = []
for rep in range(10):
    pm = rs.permutation(len(COMMON)); h = len(pm)//2
    A = {a: float(V2[a][pm[:h]].mean()) for a in ARMS}
    B = {a: float(V2[a][pm[h:]].mean()) for a in ARMS}
    pl.append(survival(A, B, FLOOR)[0])
PLACEBO = float(np.mean(pl))
print(f"\n  PLACEBO ⭐ split-half of the SAME judge (2B vs 2B) : {PLACEBO:.4f} ± {np.std(pl):.4f}")
print(f"            this is the ceiling on agreement when the judge does NOT change")

surv, n_res, strat = survival(M2, M8, FLOOR)
neg = float(np.mean([survival(M2, M8, FLOOR, shuffle=True, seed=s)[0] for s in range(10)]))
g0_ok_pairs = [(a, b) for a, b in itertools.combinations(ARMS, 2) if abs(M2[a]-M2[b]) <= FLOOR]
g0 = float(np.mean([np.sign(M2[a]-M2[b]) == np.sign(M8[a]-M8[b]) for a, b in g0_ok_pairs])) \
     if g0_ok_pairs else float("nan")
big = sorted(itertools.combinations(ARMS, 2), key=lambda ab: -abs(M2[ab[0]]-M2[ab[1]]))[:20]
pos = float(np.mean([np.sign(M2[a]-M2[b]) == np.sign(M8[a]-M8[b]) for a, b in big]))

print(f"\n  ── THE ESTIMAND: 2B -> 0.8B sign survival on pairs RESOLVED under 2B ──")
print(f"    survival {surv:.4f}   on {n_res} of {len(ARMS)*(len(ARMS)-1)//2} pairs")
for s, (v, c) in sorted(strat.items()):
    print(f"      {s:<7} {v:.4f}  ({c} pairs)")

# ⭐ WITHIN-FAMILY IS 0.33, BELOW CHANCE -- that is a REVERSAL, not disagreement, and a reversal has
# a direction worth naming. Break it out per family and report the k-gradient sign under each judge.
print(f"\n  ── THE REVERSAL, per family: does each judge prefer MORE criteria or FEWER? ──")
rev = {}
for fam in ("topw", "random"):
    mem = [a for a in ARMS if family(a) == fam]
    ks = {a: int(a.split("_k")[1].split("_")[0]) for a in mem}
    import numpy as _np
    kk = _np.array([ks[a] for a in mem], float)
    c2 = float(_np.corrcoef(kk, [M2[a] for a in mem])[0, 1])
    c8 = float(_np.corrcoef(kk, [M8[a] for a in mem])[0, 1])
    n_ok = sum(1 for a, b in itertools.combinations(mem, 2)
               if abs(M2[a]-M2[b]) > FLOOR and _np.sign(M2[a]-M2[b]) == _np.sign(M8[a]-M8[b]))
    n_all = sum(1 for a, b in itertools.combinations(mem, 2) if abs(M2[a]-M2[b]) > FLOOR)
    rev[fam] = {"corr_k_2B": c2, "corr_k_08B": c8, "surv": n_ok/n_all if n_all else float("nan"),
                "n": n_all, "members": len(mem)}
    print(f"    {fam:<8} corr(k, A2)  2B = {c2:+.4f}   0.8B = {c8:+.4f}   "
          f"sign survival {n_ok}/{n_all}")
    print(f"             -> 2B prefers {'MORE' if c2>0 else 'FEWER'} criteria, "
          f"0.8B prefers {'MORE' if c8>0 else 'FEWER'}  "
          f"{'⛔ OPPOSITE' if c2*c8 < 0 else 'same direction'}")

print(f"\n  POSITIVE  the 20 largest-|Δ| pairs keep their sign            : {pos:.4f}")
print(f"  g=0       pairs UNRESOLVED under 2B survive at ~0.5          : {g0:.4f}  "
      f"({len(g0_ok_pairs)} pairs)")
print(f"  NEGATIVE  0.8B arm labels shuffled                            : {neg:.4f}")

print(f"\n  ── SPECIFICATION CURVE: resolution threshold, all cells ──")
print(f"    {'thresh':>10} {'n pairs':>8} {'survival':>9} {'placebo':>9}")
spec = {}
for mult in (1, 2, 3):
    th = FLOOR*mult
    sv, nn, _ = survival(M2, M8, th)
    pls = []
    r2 = np.random.default_rng(mult)
    for rep in range(10):
        pm = r2.permutation(len(COMMON)); h = len(pm)//2
        pls.append(survival({a: float(V2[a][pm[:h]].mean()) for a in ARMS},
                            {a: float(V2[a][pm[h:]].mean()) for a in ARMS}, th)[0])
    spec[mult] = {"thresh": th, "n": nn, "surv": sv, "placebo": float(np.mean(pls))}
    print(f"    {th:>10.4f} {nn:>8} {sv:>9.4f} {np.mean(pls):>9.4f}")

# floor on a proportion, by bootstrap over pairs
rb = np.random.default_rng(7)
res_pairs = [(a, b) for a, b in itertools.combinations(ARMS, 2) if abs(M2[a]-M2[b]) > FLOOR]
hits = np.array([np.sign(M2[a]-M2[b]) == np.sign(M8[a]-M8[b]) for a, b in res_pairs], float)
bs = np.array([hits[rb.integers(0, len(hits), len(hits))].mean() for _ in range(200)])
lo, hi = np.percentile(bs, [2.5, 97.5])
print(f"\n    survival 95% CI over pairs: [{lo:.4f}, {hi:.4f}]")

pl_ok = PLACEBO > 0.75          # the placebo must itself resolve order, or nothing is readable
neg_ok = abs(neg - 0.5) < 0.15
if not (pl_ok and neg_ok):
    verdict, world = "UNVERIFIED", "D (split-half placebo cannot resolve order, or negative is not null)"
else:
    prop_floor = float(np.std(pl)) * 2
    if surv >= PLACEBO - prop_floor: world = "A (NUISANCE — the judge shifts levels, not order)"
    elif surv <= 0.55:               world = "C (DESTROYED — no comparative transfers)"
    else:                            world = "B (ORDINAL — the judge changes what counts as better)"
    verdict = "MEASURED"
print(f"\n  VERDICT {verdict}\n  world: {world}")
print(f"  ⭐ survival {surv:.4f} vs same-judge placebo {PLACEBO:.4f}  -> gap {surv-PLACEBO:+.4f}")

OUT.mkdir(parents=True, exist_ok=True)
json.dump({"n_arms": len(ARMS), "n_prompts": len(COMMON), "survival": surv, "n_resolved": n_res,
           "ci": [float(lo), float(hi)], "placebo": PLACEBO, "placebo_sd": float(np.std(pl)),
           "positive": pos, "g0": g0, "negative": neg, "strata": {k: list(v) for k, v in strat.items()},
           "spec": spec, "reversal": rev, "verdict": verdict, "world": world,
           "controls": {"placebo": bool(pl_ok), "negative": bool(neg_ok)}},
          open(OUT/"r480_order.json", "w"), indent=2, default=float)
sys.exit(0 if verdict != "UNVERIFIED" else 2)
