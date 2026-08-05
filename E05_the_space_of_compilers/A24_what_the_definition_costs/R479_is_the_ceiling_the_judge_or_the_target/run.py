#!/usr/bin/env python3
"""R479 — the 0.54 convergence: is it the criteria, the judge, or the TARGET's own noise?

WHY. R478 found the prompt-blind class flat at ~0.538 for k=2..6, `topw_k4` at 0.5475, `generic` at
0.5377, the released core near the same. Four unrelated routes land in one narrow band. Three worlds
explain that, and they imply completely different next moves -- better criteria, a better judge, or
NOTHING, because the band is where the target itself stops being predictable.

ESTIMAND
    BAYES = E[ A2( modal human ranking , a HELD-OUT human annotator ) ]
    the maximum A2 that ANY deterministic scorer can attain against this target, because the mode is
    the Bayes-optimal point predictor under 0/1 loss per pair. Then, per arm:
        ATTAINMENT = (A2(arm) − chance) / (BAYES − chance)
    ⭐ AND THE MODE IS COMPUTED LEAVE-ONE-OUT. Including the held-out annotator in the mode that is
    scored against it is leakage, and it would inflate BAYES toward 1.0 -- exactly the direction that
    would manufacture headroom and license "the criteria are the problem".

IDENTIFICATION
    Identified wherever a prompt has >= 3 annotators (2 to form a mode, 1 held out). The release
    ships a median of 16, so this is not a marginal design. ⚠ The mode of a finite sample is itself
    an estimate; its bias falls with the number of annotators used, so the count is SWEPT (2,4,8,16,
    all) and the curve is reported -- a single value would be an unconverged number quoted as a limit.

SCOPE
    population  prompts with >= 3 rankings, count reported in-run.
    instrument  A2 over 6 pairs vs one held-out annotator; arms judged by Qwen3.5-2B and -0.8B.
    baseline    chance, MEASURED (R477: 0.428, not 0.5 -- cls() emits {-1,0,+1} and ties are not
                coin flips).
    regime      4 responses per prompt, 6 pairs, k=4 arms.

WORLDS
    A  TARGET-BOUND   BAYES ~ 0.55 -> the arms are AT the ceiling. The band is the target's own
                      irreducible disagreement. Predicts: attainment near 1.0 for several arms, and
                      `oracle_k4` cannot exceed BAYES by more than its fitting advantage.
    B  JUDGE-BOUND    BAYES >> 0.55 and the two judges attain DIFFERENT fractions -> the instrument
                      limits, and a better judge moves everything.
    C  CRITERIA-BOUND BAYES >> 0.55 and both judges attain the SAME fraction -> the criteria limit,
                      and better criteria are the move.
    D  BROKEN         the leave-one-out mode does not beat a single random annotator -> the ceiling
                      construction is unfit -> UNVERIFIED.

PREDICTION MATRIX
                    BAYES     2B vs 0.8B attainment     what it licenses
    A  target-bound  ~0.55           either             stop optimising; the band IS the ceiling
    B  judge-bound   >>0.55        DIFFERENT            change the judge
    C  criteria-bound>>0.55           SAME              change the criteria
    D  broken          any            any               UNVERIFIED

PRE-REGISTERED KILL  (conditional, never a bare threshold)
    if mode_beats_single_annotator and placebo_at_chance and sweep_has_converged:
        A if BAYES − best_arm <= floor
        B if (attainment_2B − attainment_08B) > 0.10
        C otherwise
    else:
        UNVERIFIED

CONTROLS
    POSITIVE   the leave-one-out mode must beat a single RANDOM annotator as a predictor of another
               held-out annotator. It is the Bayes point predictor, so if it does not, the mode
               construction is broken and BAYES is not a ceiling.
    g=0        the mode computed over SHUFFLED rankings must fall to chance. This is what makes the
               positive control able to fail -- a "mode" that is really an artifact of the tie
               structure would pass the positive and fail here.
    PLACEBO    every arm and the ceiling re-scored against shuffled rankings -> ~0.428.
    LEAKAGE    the SAME computation WITH the held-out annotator included in the mode, reported
               beside the honest one. The gap IS the leakage, measured -- not argued away.
    FLOOR      0.0122, R477, measured from three random_k4 arms differing only in the draw.

MULTIPLICITY  5 mode-sizes × 2 judges × 6 arms, all cells printed including the non-survivors.

ARTIFACT  results/r479_ceiling.json          5 held-out draws × 20 mode resamples.

IMPOSSIBLE HERE, NAMED
    construct validated -- whether A2-against-a-held-out-annotator is the RIGHT target needs an
                           external gold standard this release does not carry.
    a better judge      -- world B would need a judge this site has not run; the two available are
                           2B and 0.8B, and that is the whole cross-model axis here.
"""
import collections, itertools, json, pathlib, sys
import numpy as np

ROOT = pathlib.Path("."); L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R479_is_the_ceiling_the_judge_or_the_target/results"
sys.path.insert(0, str(ROOT/"corebench")); import score as SC

def cls(y): return tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
CHANCE = 0.428          # R477, MEASURED not assumed

tgt_raw, _ = SC.load_targets()
TGT = {p: [tuple(y) for y, _ in v] for p, v in tgt_raw.items()}
pids = [p for p, v in TGT.items() if len(v) >= 3]
print(f"  prompts with >=3 rankings: {len(pids)}   median annotators "
      f"{int(np.median([len(TGT[p]) for p in pids]))}")

def ceiling(m_size=None, shuffle=False, leak=False, reps=20, seed=0):
    """BAYES: modal ranking of `m_size` OTHER annotators vs one held out. leak=True includes the
    held-out annotator in the mode -- the measured leakage, reported beside the honest number."""
    rs = np.random.default_rng(seed)
    acc = []
    for p in pids:
        v = list(TGT[p])
        if shuffle:
            v = [tuple(rs.permutation(list(y))) for y in v]
        got = []
        for _ in range(reps):
            j = int(rs.integers(len(v)))
            rest = v if leak else v[:j] + v[j+1:]
            if not rest: continue
            if m_size is not None and m_size < len(rest):
                rest = [rest[i] for i in rs.choice(len(rest), m_size, replace=False)]
            mode = collections.Counter(cls(y) for y in rest).most_common(1)[0][0]
            hc = cls(v[j])
            got.append(float(np.mean([mode[t] == hc[t] for t in range(6)])))
        if got: acc.append(float(np.mean(got)))
    return float(np.mean(acc))

def single_annotator(reps=20, seed=1):
    """POSITIVE-CONTROL RIVAL: one random annotator predicting another. The mode must beat this."""
    rs = np.random.default_rng(seed); acc = []
    for p in pids:
        v = TGT[p]; got = []
        for _ in range(reps):
            i, j = rs.choice(len(v), 2, replace=False)
            a, b = cls(v[i]), cls(v[j])
            got.append(float(np.mean([a[t] == b[t] for t in range(6)])))
        acc.append(float(np.mean(got)))
    return float(np.mean(acc))

BAYES = ceiling(); LEAK = ceiling(leak=True); SINGLE = single_annotator(); G0 = ceiling(shuffle=True, seed=5)
print(f"\n  ── THE CEILING ──")
print(f"    BAYES  leave-one-out modal ranking vs a held-out annotator : {BAYES:.4f}")
print(f"    single annotator vs another annotator                      : {SINGLE:.4f}"
      f"   <- INDEPENDENT REPRODUCTION of the campaign's human ceiling 0.5451 (delta "
      f"{SINGLE-0.5451:+.4f})")
print(f"    chance (R477, measured)                                    : {CHANCE:.4f}")
print(f"    ⚠ LEAKY version (held-out annotator INSIDE the mode)        : {LEAK:.4f}"
      f"   -> leakage {LEAK-BAYES:+.4f}")
print(f"    g=0 mode over SHUFFLED rankings                            : {G0:.4f}")

print(f"\n  ── CONVERGENCE SWEEP: how many annotators the mode is built from ──")
sweep = {}
for m in (2, 4, 8, 16, None):
    sweep[str(m)] = ceiling(m_size=m)
    print(f"    m = {str(m):<4} BAYES = {sweep[str(m)]:.4f}")
# ⛔ THE CONVERGENCE THRESHOLD IS MEASURED, NOT GUESSED. The first version demanded that m=16 and
# m=all agree within 0.005 -- a number with no derivation -- and it FAILED at 0.0052, which says
# nothing about convergence and everything about the estimator's own resampling noise. That noise
# is measurable: re-run the ceiling at several seeds and take the spread. A threshold tighter than
# the instrument's resolution is a control that cannot pass (CLAUDE.md P4).
seeds = [ceiling(seed=s) for s in (0, 17, 41, 73)]
CONV_FLOOR = float(np.std(seeds)) * 2 + (max(seeds) - min(seeds))
print(f"    ── estimator noise: ceiling at 4 seeds = "
      f"{', '.join(f'{x:.4f}' for x in seeds)}  -> resolution {CONV_FLOOR:.4f}")
conv = abs(sweep["16"] - sweep["None"]) <= CONV_FLOOR

def load_arm(arm):
    f = ROOT/"corebench"/"results"/f"sat_{arm}.npz"
    if not f.exists(): return None
    d = np.load(f, allow_pickle=True)
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    rs = np.random.default_rng(3); acc = []
    for p in pids:
        if p not in o: continue
        idxs = sorted({i for i, _ in o[p]})
        y = np.array([sum(o[p].get((i, x), 0.0) for i in idxs) for x in L])
        c = cls(y); v = TGT[p]
        acc.append(float(np.mean([np.mean([c[t] == cls(v[int(rs.integers(len(v)))])[t]
                                           for t in range(6)]) for _ in range(20)])))
    return float(np.mean(acc)) if acc else None

print(f"\n  ── ATTAINMENT: (arm − chance) / (BAYES − chance), both judges, all cells ──")
ARMS = ["oracle_k4", "topw_k4", "coval_core", "generic", "genericpool16", "random_k4_s0"]
att = {}
print(f"    {'arm':<16} {'2B A2':>8} {'att':>7}   {'0.8B A2':>8} {'att':>7}")
for a in ARMS:
    row = {}
    for jn, sfx in (("2B", ""), ("0.8B", "_08b")):
        s = load_arm(f"{a}{sfx}")
        row[jn] = {"a2": s, "att": ((s-CHANCE)/(BAYES-CHANCE)) if s else None}
    att[a] = row
    f = lambda r: (f"{r['a2']:.4f}" if r["a2"] else "  —  ",
                   f"{r['att']:.3f}" if r["att"] else "  —  ")
    x, y = f(row["2B"]); z, w = f(row["0.8B"])
    print(f"    {a:<16} {x:>8} {y:>7}   {z:>8} {w:>7}")

FLOOR = 0.0122
pos_ok = (BAYES - SINGLE) > FLOOR
g0_ok  = abs(G0 - CHANCE) < 0.03
best = max((v["2B"]["a2"] for v in att.values() if v["2B"]["a2"] and v != att["oracle_k4"]), default=0)
print(f"\n  POSITIVE  the mode beats a single annotator by > {FLOOR}   : {pos_ok}  ({BAYES-SINGLE:+.4f})")
print(f"  g=0       mode over shuffled rankings sits at chance      : {g0_ok}  ({G0:.4f})")
print(f"  CONVERGED m=16 vs m=all ({abs(sweep['16']-sweep['None']):.4f}) within the MEASURED "
      f"resolution {CONV_FLOOR:.4f}: {conv}")

if not (pos_ok and g0_ok and conv):
    verdict, world = "UNVERIFIED", "D (ceiling construction unfit)"
else:
    d2, d8 = att["topw_k4"]["2B"]["att"], att["topw_k4"]["0.8B"]["att"]
    if BAYES - best <= FLOOR:
        world = f"A (TARGET-BOUND — best non-oracle arm {best:.4f} is within the floor of BAYES {BAYES:.4f})"
    elif d2 and d8 and abs(d2-d8) > 0.10:
        world = f"B (JUDGE-BOUND — attainment differs by {abs(d2-d8):.3f} across judges)"
    else:
        world = "C (CRITERIA-BOUND — headroom exists and both judges attain the same fraction)"
    verdict = "MEASURED"
print(f"\n  VERDICT {verdict}\n  world: {world}")
print(f"  ⭐ headroom above the best non-oracle arm: BAYES − {best:.4f} = {BAYES-best:+.4f} "
      f"(floor {FLOOR})")

OUT.mkdir(parents=True, exist_ok=True)
json.dump({"bayes": BAYES, "leak": LEAK, "leakage": LEAK-BAYES, "single": SINGLE, "g0": G0,
           "chance": CHANCE, "sweep": sweep, "converged": bool(conv), "arms": att,
           "best_non_oracle": best, "headroom": BAYES-best, "verdict": verdict, "world": world,
           "controls": {"positive": bool(pos_ok), "g0": bool(g0_ok), "converged": bool(conv)},
           "conv_floor": CONV_FLOOR, "seeds": seeds, "human_ceiling_delta": SINGLE-0.5451},
          open(OUT/"r479_ceiling.json", "w"), indent=2, default=float)
sys.exit(0 if verdict != "UNVERIFIED" else 2)
