#!/usr/bin/env python3
"""R486 — is ②'s bar an unbeatable OUTLIER, or does the admissible arm genuinely sit inside the class?

WHY. R485 found ② and ③ conflict: every arm clearing the cross-fitted prompt-blind ceiling is one ③
excludes. That is only a fact about the CLAUSES if the bar is fair. If `genericpool16` happened to be
an arbitrarily strong pool, the "conflict" would be an artifact of the reference class.

⚠ AND THE SIZE HALF IS ALREADY SETTLED, WHICH MY NEXT-GRADIENT LINE DID NOT KNOW.
`R454_is_the_bound_a_property_of_the_pool` swept pool breadth W ∈ {6,8,10,12,14,16} and found the
bound SATURATES by W≈12 (sd over W=12..16 is 0.0153). So the bar is not pool-SIZE limited. What R454
did not ask is whether those 16 hand-written criteria are an unusually STRONG generic set.

ESTIMAND
    PCT = the percentile of `gen` (R485's best ③-admissible PROMPT-AWARE arm) within the distribution
    of all C(16,4) = 1,820 prompt-blind 4-subsets, on the same prompts and instrument.
    ⭐ It discriminates two worlds that R485 alone cannot separate:
      - bar is an OUTLIER  -> `gen` sits HIGH in the class (beats most subsets) and loses only to a
        thin tail. Then ② is effectively "beat the best of 1,820 draws", an order statistic, and the
        conflict is about the BAR.
      - bar is the CLASS   -> `gen` sits MID-pack. Then the prompt-blind class as a whole matches it,
        the conflict is about the CLAUSES, and R485 stands.

IDENTIFICATION
    Fully identified from committed sat matrices; no judge call. ⚠ It cannot show `genericpool16` is
    a FAIR sample of possible generic criteria — that needs a second hand-written pool, which this
    site does not have (R454: exactly one prompt-blind family with breadth ≥ 16, and no resampling
    makes a second). Named in the register, not claimed.

SCOPE
    population  968 prompts covered by the pool, counted in-run.
    instrument  A2 vs a held-out human annotator, 20 draws, crc32-seeded.
    baseline    the whole 1,820 distribution, published as quantiles rather than a chosen point.
    regime      k=4; Qwen3.5-2B (the pool has no `_08b` build — R477).

WORLDS
    A  BAR IS AN OUTLIER  PCT >= 90 -- `gen` beats almost the whole class and loses to a thin tail.
                          ② is then an order-statistic bar and R485's conflict is about the bar.
    B  BAR IS THE CLASS   40 <= PCT < 90 -- `gen` is mid-pack; the class matches it broadly and the
                          conflict is about ② and ③ themselves.
    C  ARM IS WEAK        PCT < 40 -- the admissible arm is simply poor, and the conflict says little
                          about ③: almost any prompt-blind set beats it.

PREDICTION MATRIX
                       PCT of `gen`     what it licenses
    A  bar is outlier      >= 90        restate ② against a QUANTILE, not the max
    B  bar is the class    40-90        R485 stands as a clause-level finding
    C  arm is weak          < 40        the finding is about `gen`, not about ③

PRE-REGISTERED KILL
    if positive_control_fires and g0_is_null:
        A if PCT >= 90 ; C if PCT < 40 ; else B
    else:
        UNVERIFIED

CONTROLS
    POSITIVE   a ③-EXCLUDED arm known to clear the ceiling (`topw_k4`) must land at a HIGH percentile
               -- it beat the cross-fitted best, so it must beat most of the class. If it does not,
               the percentile scale is not measuring what the ceiling comparison measured.
    g=0        `random_k4_s0` must land LOW. A percentile scale on which a random arm scores high is
               not a scale. This is what makes the positive able to fail.
    PLACEBO    the pool's own subsets re-scored against shuffled rankings must collapse to a
               degenerate distribution (spread far below the real one).
    CROSS-CHK  `generic` -- the released prompt-blind set -- is itself in the class's universe, so its
               percentile is reported as an orientation point, NOT as evidence.

MULTIPLICITY  the full quantile ladder is printed, not a single percentile.

ARTIFACT  results/r486_bar_percentile.json     deterministic (crc32).

IMPOSSIBLE HERE, NAMED
    a second generic pool -- would settle whether these 16 criteria are a strong SELECTION rather than
        a representative one. R454 established no second prompt-blind family of breadth >= 16 exists
        here; building one requires writing criteria and judging them, which is a GPU round.
"""
import collections, itertools, json, pathlib, sys, zlib
import numpy as np
ROOT = pathlib.Path("."); L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R486_is_clause_two_bar_an_outlier_or_the_class/results"
sys.path.insert(0, str(ROOT/"corebench")); import score as SC
def cls(y): return tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
tgt, _ = SC.load_targets(); TGT = {p: [tuple(y) for y, _ in v] for p, v in tgt.items()}

def load(arm):
    f = ROOT/"corebench"/"results"/f"sat_{arm}.npz"
    if not f.exists(): return None
    d = np.load(f, allow_pickle=True); o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    return o

POOL = load("genericpool16")
pids = sorted(p for p in POOL if p in TGT)
print(f"  pool prompts usable: {len(pids)}")
M = np.array([[[POOL[p].get((i, x), 0.0) for x in L] for i in range(16)] for p in pids])  # [P,16,4]

# held-out human class vectors, fixed per prompt across every arm and subset
H = np.zeros((len(pids), 20, 6), dtype=np.float32)
for a, p in enumerate(pids):
    r = np.random.default_rng(zlib.crc32(p.encode())); v = TGT[p]
    for b in range(20):
        H[a, b] = cls(np.array(v[int(r.integers(len(v)))], float))

def score_mat(Y):                       # Y: [P,4] -> mean A2
    c = np.stack([np.sign(Y[:, i] - Y[:, j]) for i, j in PAIRS], axis=-1)
    return float((c[:, None, :] == H).mean())

def score_arm(arm, shuffle=False):
    o = load(arm)
    if not o: return None
    ok = [p for p in pids if p in o]
    if len(ok) < 0.9*len(pids): return None
    idx = {p: sorted({i for i, _ in o[p]}) for p in ok}
    Y = np.array([[sum(o[p].get((i, x), 0.0) for i in idx[p]) for x in L] for p in ok])
    if not shuffle and ok == pids: return score_mat(Y)
    sel = [pids.index(p) for p in ok]
    c = np.stack([np.sign(Y[:, i] - Y[:, j]) for i, j in PAIRS], axis=-1)
    Hs = H[sel]
    if shuffle:
        r = np.random.default_rng(9); Hs = Hs[:, :, r.permutation(6)]
    return float((c[:, None, :] == Hs).mean())

subs = list(itertools.combinations(range(16), 4))
census = np.array([score_mat(M[:, s, :].sum(axis=1)) for s in subs])
q = np.percentile(census, [0, 10, 25, 50, 75, 90, 100])
print(f"\n  ── the class: all {len(subs)} prompt-blind 4-subsets ──")
print("    " + "  ".join(f"p{p}={v:.4f}" for p, v in zip((0, 10, 25, 50, 75, 90, 100), q)))

pct = lambda s: float(100 * (census < s).mean())
arms = {a: score_arm(a) for a in ("gen", "topw_k4", "random_k4_s0", "generic", "coval_core", "full")}
print(f"\n  {'arm':<14} {'A2':>8} {'percentile in the class':>24}")
for a, s in arms.items():
    if s is None: print(f"  {a:<14} {'—':>8}   UNAVAILABLE"); continue
    print(f"  {a:<14} {s:>8.4f} {pct(s):>23.1f}")

pos_ok = arms["topw_k4"] is not None and pct(arms["topw_k4"]) >= 90
g0_ok = arms["random_k4_s0"] is not None and pct(arms["random_k4_s0"]) <= 25
shuf = np.array([score_mat(M[:, s, :].sum(axis=1)) for s in subs[:200]])
Hsave = H.copy(); r = np.random.default_rng(9)
H = H[:, :, r.permutation(6)]
shufc = np.array([score_mat(M[:, s, :].sum(axis=1)) for s in subs[:200]])
H = Hsave
pl_ok = float(np.std(shufc)) < float(np.std(census)) * 1.5
print(f"\n  POSITIVE  topw_k4 (clears the ceiling) sits at p{pct(arms['topw_k4']):.1f}  : {pos_ok}")
print(f"  g=0       random_k4_s0 sits at p{pct(arms['random_k4_s0']):.1f}              : {g0_ok}")
print(f"  PLACEBO   class sd real {np.std(census):.4f} vs pair-shuffled {np.std(shufc):.4f} : {pl_ok}")

g = pct(arms["gen"])
if not (pos_ok and g0_ok and pl_ok):
    verdict, world = "UNVERIFIED", "controls failed — the percentile scale is not validated"
elif g >= 90:
    verdict, world = "MEASURED", f"A (BAR IS AN OUTLIER — `gen` at p{g:.1f}; ② is an order-statistic bar)"
elif g < 40:
    verdict, world = "MEASURED", f"C (ARM IS WEAK — `gen` at p{g:.1f}; the finding is about the arm)"
else:
    verdict, world = "MEASURED", (f"B (BAR IS THE CLASS — `gen` at p{g:.1f}: mid-pack, so the class "
                                  f"broadly matches it and R485's conflict is about the CLAUSES)")
print(f"\n  VERDICT {verdict}\n  world: {world}")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"n_prompts": len(pids), "n_subsets": len(subs),
           "quantiles": dict(zip(("p0","p10","p25","p50","p75","p90","p100"), map(float, q))),
           "arms": {a: (None if s is None else {"a2": s, "pct": pct(s)}) for a, s in arms.items()},
           "controls": {"positive": bool(pos_ok), "g0": bool(g0_ok), "placebo": bool(pl_ok)},
           "verdict": verdict, "world": world}, open(OUT/"r486_bar_percentile.json", "w"), indent=2)
sys.exit(0 if verdict != "UNVERIFIED" else 2)
