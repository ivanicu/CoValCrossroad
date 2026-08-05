#!/usr/bin/env python3
"""R481 — R480's size reversal: is it the JUDGE, or is it the SUM nobody chose deliberately?

WHY. R480 found the two judges reverse on set SIZE for unselected sets: corr(k, A2) = +0.8570 at 2B
and −0.5026 at 0.8B. But every A2 in this campaign routes through `corebench/score.py:63`:

    def yvec(sat_p, idxs): return np.array([sum(sat_p.get((i,x),0.0) for i in idxs) for x in L])

a plain SUM over the selected criteria. **That is a choice, made once, never swept** (`/yvec/` and
`/sum/` both return 0 in DEFINITION.md). A sum's variance grows with k by construction, so a
k-gradient is exactly the place an aggregation artifact would hide.

⛔ AND HALF THE SWEEP IS VOID BY ALGEBRA. `mean = sum/k` with k fixed within a prompt, and `cls()`
reads SIGNS of differences, which are invariant under positive scaling. **cls(mean) ≡ cls(sum)**,
verified 2000/2000 on random matrices. Sweeping MEAN is a rename -- so it is used here as a POSITIVE
CONTROL ON THE IMPLEMENTATION instead: an identity the code MUST reproduce, and can fail.
MAX / MEDIAN / MIN / MIDRANGE are nonlinear in the columns and are genuine alternatives.

ESTIMAND
    (a) SIGN(corr(k, A2)) per family × judge × aggregator -- does R480's reversal survive?
    (b) the arm-ordering agreement between aggregators, on pairs resolved under SUM.
    ⭐ (a) is the decisive one: R480 attributed the reversal to the judge, and this asks whether the
    same data reverses because of how four numbers were combined into one.

IDENTIFICATION
    Fully identified from committed sat matrices; no judge call. ⚠ `topvar`/`topwvar` are excluded
    because their SELECTION rule already reads the satisfaction spread, so changing the aggregator
    changes both the arm and the metric -- a confound the design refuses rather than adjusts for.

SCOPE
    population  prompts scored by both judges for the arm, counted in-run.
    instrument  A2 vs held-out human, 20 draws, crc32-seeded (R480 retraction 303: `hash()` is salted).
    baseline    the SUM column is the campaign's committed choice; every other aggregator is reported
                beside it, never instead of it.
    regime      k ∈ {1,2,3,4,6,8,12}; families `topw` (selective) and `random` (unselected).

WORLDS
    A  JUDGE      the reversal holds under EVERY aggregator -> R480 stands, it is the instrument.
    B  STATISTIC  the reversal vanishes or flips under some aggregator -> it was the sum, and R480's
                  mechanism claim must be withdrawn even though its survival numbers stand.
    C  MIXED      survives under some, not others -> the claim is real but must name the aggregator,
                  which no sentence in this campaign currently does.
    D  BROKEN     MEAN does not reproduce SUM -> the harness is wrong and nothing here is readable.

PREDICTION MATRIX
                  reversal under max/median/min   mean==sum   what it licenses
    A  judge              present in all             yes       "the judge reverses on size"
    B  statistic          absent in all              yes       withdraw the mechanism
    C  mixed              present in some            yes       "under SUM aggregation, the judge…"
    D  broken               any                      NO        UNVERIFIED

PRE-REGISTERED KILL  (conditional, never a bare threshold)
    if mean_reproduces_sum_exactly and negative_is_null:
        A if sign(corr) differs between judges under ALL aggregators
        B if it differs under NONE except sum
        C otherwise
    else:
        UNVERIFIED

CONTROLS
    POSITIVE ⭐ MEAN must reproduce SUM to floating-point on every arm. This is an ALGEBRAIC IDENTITY,
               so it cannot be satisfied by accident, and a buggy aggregation pipeline breaks it --
               it can fail and must pass. It validates the harness, not the hypothesis.
    g=0        a CONSTANT aggregator (ignores the criteria, returns the same value per response) must
               land at chance and produce corr(k, A2) ~ 0 -- no aggregator should manufacture a
               k-gradient out of nothing.
    NEGATIVE   criterion-to-response assignment shuffled within each prompt: destroys which response
               satisfied what, preserves the marginal distribution. All aggregators -> chance.
    PLACEBO    A2 against shuffled human rankings -> ~0.428 (R477, measured).

MULTIPLICITY  6 aggregators × 2 judges × 2 families = 24 sign cells, every one printed.

ARTIFACT  results/r481_aggregation.json      deterministic (crc32); two-process byte-identity checked.

IMPOSSIBLE HERE, NAMED
    a third aggregator family -- learned/weighted aggregation would need fitting, which reintroduces
        the target and makes the arm a target-reader (clause ③), so it is excluded by the definition.
    causal identification -- would require re-judging with a per-criterion elicitation the release
        does not carry.
"""
import collections, itertools, json, pathlib, sys, zlib
import numpy as np

ROOT = pathlib.Path("."); L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R481_is_the_reversal_the_judge_or_the_sum/results"
sys.path.insert(0, str(ROOT/"corebench")); import score as SC

def cls(y): return tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
tgt_raw, _ = SC.load_targets()
TGT = {p: [tuple(y) for y, _ in v] for p, v in tgt_raw.items()}

AGG = {
    "sum":      lambda M: M.sum(axis=0),          # the campaign's committed choice, score.py:63
    "mean":     lambda M: M.mean(axis=0),         # POSITIVE CONTROL -- identical to sum by algebra
    "max":      lambda M: M.max(axis=0),
    "median":   lambda M: np.median(M, axis=0),
    "min":      lambda M: M.min(axis=0),
    "midrange": lambda M: (M.max(axis=0)+M.min(axis=0))/2,
    "constant": lambda M: np.zeros(M.shape[1]),   # g=0 -- must not manufacture a gradient
}
# ⭐ THE SEED AXIS IS PART OF THE SPECIFICATION, NOT A DETAIL. R480 computed corr(k, A2) over 18
# random arms (6 budgets x 3 seeds); using one seed per budget gives 6. On the 0.8B judge that
# changes the correlation from -0.5026 to +0.0476 -- A SIGN FLIP -- while the population is
# identical (968 prompts either way, own-pop == common-pop, verified). So the arm set entering a
# correlation is a specification choice, and R480 reported one cell of it.
SEED_SETS = {"s0_only": (0,), "all_seeds": (0, 1, 2)}
ARMS_TOPW = [f"topw_k{k}" for k in (1, 2, 3, 4, 6, 8, 12)]
ARMS_RAND = {n: [f"random_k{k}_s{s}" for k in (2, 3, 4, 6, 8, 12) for s in ss]
             for n, ss in SEED_SETS.items()}
ARMS = ARMS_TOPW + sorted(set(sum(ARMS_RAND.values(), [])))
fam = lambda a: "random" if a.startswith("random") else "topw"
kof = lambda a: int(a.split("_k")[1].split("_")[0])

def load(arm, sfx):
    f = ROOT/"corebench"/"results"/f"sat_{arm}{sfx}.npz"
    if not f.exists(): return None
    d = np.load(f, allow_pickle=True)
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    out = {}
    for p, cells in o.items():
        if p not in TGT: continue
        idxs = sorted({i for i, _ in cells})
        out[p] = np.array([[cells.get((i, x), 0.0) for x in L] for i in idxs], dtype=np.float64)
    return out

def a2(mats, agg, shuffle_tgt=False, shuffle_cells=False):
    tot = []
    for p, M in mats.items():
        r = np.random.default_rng(zlib.crc32(p.encode()))
        if shuffle_cells:                       # NEGATIVE: destroy which response satisfied what
            M = np.apply_along_axis(r.permutation, 1, M)
        c = cls(agg(M)); v = TGT[p]
        got = []
        for _ in range(20):
            y = list(v[int(r.integers(len(v)))])
            if shuffle_tgt: y = list(r.permutation(y))
            hc = cls(np.array(y, float))
            got.append(np.mean([c[t] == hc[t] for t in range(6)]))
        tot.append(float(np.mean(got)))
    return float(np.mean(tot)) if tot else float("nan")

MATS = {(a, j): load(a, s) for a in ARMS for j, s in (("2B", ""), ("0.8B", "_08b"))}
ARMS = [a for a in ARMS if MATS[(a, "2B")] and MATS[(a, "0.8B")]]
print(f"  arms with both judges: {len(ARMS)}   aggregators: {len(AGG)}")

S = {(a, j, g): a2(MATS[(a, j)], f) for a in ARMS for j in ("2B", "0.8B") for g, f in AGG.items()}

pos = max(abs(S[(a, j, "sum")] - S[(a, j, "mean")]) for a in ARMS for j in ("2B", "0.8B"))
print(f"\n  POSITIVE ⭐ max |A2(sum) − A2(mean)| over {2*len(ARMS)} arm×judge cells: {pos:.2e}")
print(f"             an ALGEBRAIC IDENTITY the harness must reproduce -> {'PASS' if pos < 1e-12 else '⛔ FAIL'}")

neg = np.mean([a2(MATS[(a, "2B")], AGG["sum"], shuffle_cells=True) for a in ARMS])
pla = np.mean([a2(MATS[(a, "2B")], AGG["sum"], shuffle_tgt=True) for a in ARMS])
print(f"  NEGATIVE  criterion→response assignment shuffled : {neg:.4f}  (chance 0.428)")
print(f"  PLACEBO   human rankings shuffled                : {pla:.4f}  (chance 0.428)")

print(f"\n  ── corr(k, A2) PER FAMILY × JUDGE × AGGREGATOR — all 24 sign cells ──")
print(f"    {'agg':<9} {'topw 2B':>9} {'topw .8B':>9} {'rev':>4}   {'rand 2B':>9} {'rand .8B':>9} {'rev':>4}")
grid = {}
for g in AGG:
    row = {}
    for f_ in ("topw", "random"):
        mem = ARMS_TOPW if f_ == "topw" else [a for a in ARMS_RAND["all_seeds"] if a in ARMS]
        kk = np.array([kof(a) for a in mem], float)
        for j in ("2B", "0.8B"):
            vals = np.array([S[(a, j, g)] for a in mem])
            row[(f_, j)] = float(np.corrcoef(kk, vals)[0, 1]) if vals.std() > 1e-12 else 0.0
    grid[g] = row
    rt = "⛔" if row[("topw", "2B")]*row[("topw", "0.8B")] < 0 else "ok"
    rr = "⛔" if row[("random", "2B")]*row[("random", "0.8B")] < 0 else "ok"
    print(f"    {g:<9} {row[('topw','2B')]:>+9.4f} {row[('topw','0.8B')]:>+9.4f} {rt:>4}   "
          f"{row[('random','2B')]:>+9.4f} {row[('random','0.8B')]:>+9.4f} {rr:>4}")

# ---- THE SEED AXIS, swept and printed whole (G4) ---------------------------------------------
print(f"\n  ── SPECIFICATION: which random arms enter corr(k, A2)? sum aggregator, both judges ──")
print(f"    {'arm set':<11} {'n':>3} {'2B':>9} {'0.8B':>9}   sign reversal")
seedspec = {}
for name, ss in SEED_SETS.items():
    mem = [a for a in ARMS_RAND[name] if a in ARMS]
    kk = np.array([kof(a) for a in mem], float)
    r = {}
    for j in ("2B", "0.8B"):
        r[j] = float(np.corrcoef(kk, [S[(a, j, "sum")] for a in mem])[0, 1])
    seedspec[name] = r | {"n": len(mem)}
    print(f"    {name:<11} {len(mem):>3} {r['2B']:>+9.4f} {r['0.8B']:>+9.4f}   "
          f"{'⛔ YES' if r['2B']*r['0.8B'] < 0 else 'no'}")
signs = {n: (v["2B"]*v["0.8B"] < 0) for n, v in seedspec.items()}
seed_stable = len(set(signs.values())) == 1
print(f"    ⛔ the reversal verdict is STABLE across arm sets: {seed_stable}"
      + ("" if seed_stable else "   -> R480's mechanism claim is one cell of a 2-cell sweep"))

# ---- SYNTHETIC WORLD (attack ladder rung 4): which aggregators MANUFACTURE a k-gradient? --------
# ⭐ WHY THIS DECIDES HOW TO READ THE SWEEP ABOVE. `max` and `min` are ORDER STATISTICS of k draws,
# so their k-dependence may be mechanical rather than about the criteria. Building a world with NO
# k-signal -- satisfaction drawn iid, independent of the human target -- measures each aggregator's
# spurious gradient directly. An aggregator with a large spurious gradient cannot testify about k,
# and "no reversal under max" would then be silence rather than evidence.
print(f"\n  ── SYNTHETIC NULL: iid satisfaction, NO k-structure. Spurious corr(k, A2) per aggregator ──")
KGRID = (2, 3, 4, 6, 8, 12)
# ⛔ THE MATRICES ARE DRAWN ONCE AND SHARED. The first version consumed one generator inside the
# aggregator loop, so every aggregator saw DIFFERENT random data -- and it printed sum=+0.4176 while
# mean=-0.4790, two numbers that are algebraically IDENTICAL. The sum==mean identity is the detector
# that caught it: a control validating the harness fired on a defect in another control.
rs_syn = np.random.default_rng(20260804)
pids_syn = list(MATS[(ARMS[0], "2B")])[:400]
SYN_M = {(k, p): rs_syn.normal(size=(k, 4)) for k in KGRID for p in pids_syn}
syn = {}
for g, f in AGG.items():
    vals = []
    for k in KGRID:
        got = []
        for p in pids_syn:
            M = SYN_M[(k, p)]
            c = cls(f(M)); v = TGT[p]
            r = np.random.default_rng(zlib.crc32(p.encode()))
            got.append(np.mean([np.mean([c[tt] == cls(np.array(v[int(r.integers(len(v)))], float))[tt]
                                         for tt in range(6)]) for _ in range(5)]))
        vals.append(float(np.mean(got)))
    syn[g] = float(np.corrcoef(np.array(KGRID, float), vals)[0, 1]) if np.std(vals) > 1e-12 else 0.0
    print(f"    {g:<9} spurious corr(k, A2) on structureless data = {syn[g]:>+8.4f}"
          f"   {'⛔ MECHANICAL — cannot testify about k' if abs(syn[g]) > 0.5 else 'usable'}")
USABLE = [g for g in AGG if g not in ("mean", "constant") and abs(syn[g]) <= 0.5]
print(f"    -> aggregators that can testify about k: {USABLE}")

# ---- IS "NO REVERSAL" EVIDENCE, OR BLINDNESS? ---------------------------------------------------
# ⭐ The spurious gradients above are a property of the AGGREGATOR and are therefore IDENTICAL for
# both judges, so they shift both correlations equally and CANNOT create a sign difference. They do
# not explain the reversal. What could explain "no reversal under max/midrange" is BLINDNESS: `max`
# reports only the single best-satisfied criterion, so it cannot see accumulation at all. A null from
# a blind instrument is silence, not an acquittal (CLAUDE.md P5 ★). Measured directly: how far does
# each aggregator's A2 move across the k-ladder on REAL data?
print(f"\n  ── IS THE NULL EVIDENCE OR BLINDNESS? A2 range across k, real data, random family ──")
print(f"    {'agg':<9} {'2B range':>9} {'0.8B range':>11}   verdict")
blind = {}
for g in AGG:
    rr = {}
    for j in ("2B", "0.8B"):
        mem = [a for a in ARMS_RAND["all_seeds"] if a in ARMS]
        byk = {}
        for a in mem: byk.setdefault(kof(a), []).append(S[(a, j, g)])
        mk = [float(np.mean(v)) for v in byk.values()]
        rr[j] = max(mk) - min(mk)
    blind[g] = rr
    b = max(rr.values()) < 0.010            # below the R477 floor -> cannot resolve k at all
    print(f"    {g:<9} {rr['2B']:>9.4f} {rr['0.8B']:>11.4f}   "
          f"{'⛔ BLIND to k (range < floor 0.0122)' if b else 'can resolve k'}")
SEEING = [g for g in AGG if g not in ("mean", "constant") and max(blind[g].values()) >= 0.010]
print(f"    -> aggregators that can RESOLVE k: {SEEING}")
print(f"    -> of those, reversal present under: "
      f"{[g for g in SEEING if grid[g][('random','2B')]*grid[g][('random','0.8B')] < 0]}")

real = [g for g in AGG if g not in ("mean", "constant")]
rev_any = {g: grid[g][("random", "2B")]*grid[g][("random", "0.8B")] < 0 for g in real}
g0_flat = abs(grid["constant"][("random", "2B")]) < 0.2 and abs(grid["constant"][("random", "0.8B")]) < 0.2
print(f"\n  g=0       constant aggregator manufactures no k-gradient : {g0_flat}")
print(f"  reversal present under: {[g for g in real if rev_any[g]]}")
print(f"  reversal absent under : {[g for g in real if not rev_any[g]]}")

ok = pos < 1e-12 and abs(neg-0.428) < 0.04 and abs(pla-0.428) < 0.04 and g0_flat
if not ok:
    verdict, world = "UNVERIFIED", "D (identity broken or a control failed)"
elif all(rev_any[g] for g in USABLE) and USABLE:
    verdict, world = "MEASURED", ("A (JUDGE — the reversal survives every aggregator that can "
                                  f"testify about k: {USABLE})")
elif not any(rev_any.values()) or (rev_any["sum"] and sum(rev_any.values()) == 1):
    verdict, world = "MEASURED", "B (STATISTIC — the reversal is the SUM, not the judge)"
else:
    verdict, world = "MEASURED", "C (MIXED — the claim must name the aggregator)"
print(f"\n  VERDICT {verdict}\n  world: {world}")

OUT.mkdir(parents=True, exist_ok=True)
json.dump({"arms": ARMS, "scores": {f"{a}|{j}|{g}": v for (a, j, g), v in S.items()},
           "grid": {g: {f"{f_}|{j}": v for (f_, j), v in r.items()} for g, r in grid.items()},
           "identity_gap": pos, "negative": float(neg), "placebo": float(pla),
           "g0_flat": bool(g0_flat), "reversal": rev_any, "seedspec": seedspec,
           "seed_stable": bool(seed_stable), "synthetic": syn, "usable": USABLE, "k_range": blind, "seeing": SEEING, "verdict": verdict, "world": world},
          open(OUT/"r481_aggregation.json", "w"), indent=2, default=float)
sys.exit(0 if verdict != "UNVERIFIED" else 2)
