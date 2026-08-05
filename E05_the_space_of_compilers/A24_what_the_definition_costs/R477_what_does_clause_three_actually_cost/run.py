#!/usr/bin/env python3
"""R477 — what does clause ③ COST? Does reading the annotator ratings buy a core anything?

WHY THIS ROUND AND NOT THE FORK IT ANSWERS.  R475 left a fork: weaken ③ to forbid only the prompt's
RANKINGS, or keep it strong and accept that the definition excludes CoVal-core.  ⛔ **That fork as
posed is a STIPULATION, not an experiment** -- both branches are internally consistent and no
measurement adjudicates a convention.  What IS measurable, and what should decide the convention:

ESTIMAND
    VALUE_OF_RATINGS = A2(top-w selector at k) − A2(a ③-ADMISSIBLE selector at the SAME k)
    i.e. what a core gains from consuming `w = mean annotator score`, holding fixed that it selects
    k criteria by ranking them on some scalar.  If ~0, ③ forbids something worthless and staying
    strong is free.  If large, ③ forbids the working mechanism and defines an unachievable object.

    ⭐ THE SHAM IS `topvar_k4`, AND IT IS THE WHOLE DESIGN.  §4: a sham is the same operation MINUS
    the ingredient, never the ingredient inverted.  `topvar_k` ranks every criterion by a scalar and
    takes the top k -- identical machinery -- but the scalar is the VARIANCE OF SATISFACTION ACROSS
    RESPONSES, which `select_core.py:145` states in its own comment is *"a property of the responses,
    never of the human target"*.  So `topw − topvar` isolates READING THE RATINGS from SELECTING AT
    ALL, and `topw − random` bounds selection-plus-ratings together.  Both are reported; only the
    first answers the question.

IDENTIFICATION
    Identified at matched k from committed artifacts.  ⚠ Comparing `topw_k4` to `full` would confound
    the ingredient with k, and comparing to `coval_core` would confound it with LM rewriting -- both
    refused.  ⚠ `topvar` exists only at k=4, so the k dose-response is available for topw−random on
    both judges and for topw−topvar at k=4 only.  Stated, not smoothed over.

SCOPE
    population  prompts scored in both arms of each contrast (reported per contrast, never assumed).
    instrument  A2 = mean over 6 response pairs of sign agreement with a HELD-OUT human annotator,
                averaged over which annotator is held out.  Two judges: Qwen3.5-2B, Qwen3.5-0.8B.
    baseline    `random_k` at matched k, 3 seeds -- the floor is MEASURED, not chosen.
    regime      k ∈ {1,2,3,4,6,8,12}; the release's own core is k≈4 for 95% of prompts.

WORLDS
    A  CHEAP     |topw − topvar| within the measured floor -> ③ forbids nothing that works.
                 Predicts: the gap is inside the random-seed spread on BOTH judges.
    B  EXPENSIVE topw − topvar clearly positive -> ③ forbids the mechanism; a definition holding ③
                 describes an object nobody has built.  Predicts: positive and outside the floor.
    C  CONFOUND  the gap exists but flips sign across judge or k -> not attributable to the ratings;
                 the contrast is measuring the judge or the budget, and the estimand is not identified.
    D  BLIND     the positive control (`oracle_k4`, which reads the human target directly) fails to
                 beat random -> A2 cannot resolve selection quality at this k, and every gap above
                 is silence.  -> UNVERIFIED, never A.

PREDICTION MATRIX
                    topw−topvar   sign stable across judge   oracle−random
    A  cheap          ~0 (in floor)        n/a                  > floor
    B  expensive       > floor             yes                  > floor
    C  confounded      > floor             NO                   > floor
    D  blind             any               any                 <= floor  -> UNVERIFIED

PRE-REGISTERED KILL  (conditional, never a bare threshold)
    if oracle_beats_random_beyond_floor:            # the instrument demonstrably resolves selection
        A if |topw−topvar| <= floor on both judges
        B if topw−topvar >  floor and same sign on both judges
        C otherwise
    else:
        UNVERIFIED

CONTROLS
    POSITIVE   `oracle_k4` reads the held-out human rankings directly. It MUST beat `random_k4` by
               more than the measured floor. If it cannot, A2 is blind here and no gap is readable.
    g=0        `random_k4` at seeds 0,1,2 against each other -- three arms differing in NOTHING but
               the draw. Their spread IS the floor, measured rather than modelled, and it is what
               makes the positive control able to fail.
    SHAM       `topvar_k4` -- same ranking machinery, ingredient removed (see ESTIMAND).
    PLACEBO    every arm re-scored against SHUFFLED human rankings must land at chance. A2's chance
               level is DERIVED, not assumed: cls() ∈ {−1,0,+1} per pair, so agreement with a random
               relabelling is not 0.5 in general -- the placebo measures it rather than asserting it.
    NEGATIVE   `topw_k4_sham`, reported as-is with whatever it turns out to be; it is NOT relied on,
               because this round did not build it and its construction is not established here.

MULTIPLICITY
    topw−random: 7 k-levels × 2 judges = 14 cells, all reported including sign disagreements.
    topw−topvar: 2 cells (one per judge). No selection over cells; the whole grid is printed.

ARTIFACT  results/r477_value_of_ratings.json     SEEDS 0,1,2 for the random arms; 5 held-out draws.

IMPOSSIBLE HERE, NAMED
    interventionally validated -- would require re-running the release's selector with ratings
                                  withheld, and that pipeline is not shipped (R475).
    cross-dataset              -- a second values release with this schema.
    construct validated        -- an external gold standard for "a good core"; A2 against held-out
                                  humans is the criterion this site has, and it is not that.
"""
import collections, itertools, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(".")
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R477_what_does_clause_three_actually_cost/results"
HELD_SEEDS = [0, 1, 2, 3, 4]

def cls(y): return tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
# POSITIVE CONTROL ON THE LOADER ITSELF: it must return non-empty, or every downstream
# 'UNAVAILABLE' is silence rather than absence (CLAUDE.md P5 ★).

def load_sat(p):
    d = np.load(p, allow_pickle=True)
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|")
        o[pid][(int(i), ltr)] = float(v)
    return o

# ⛔ DO NOT REIMPLEMENT THE LOADER. The first version of this round read rankings from
# `annotations[].ranking`; the release stores them at `metadata.assessments[].ranking_blocks.
# world[].ranking`, so every target list came back EMPTY and all 20 cells printed UNAVAILABLE.
# That failed safe -- exit 2, no number published -- but only by luck: a partially-wrong path
# would have produced a smaller population and a publishable difference. The campaign already
# owns a validated loader; use it, and let the round inherit its corrections.
sys.path.insert(0, str(ROOT/"corebench"))
import score as SC
_tgt_raw, _ = SC.load_targets()
TGT = {pid: [y for y, _demo in v] for pid, v in _tgt_raw.items()}
print(f"  targets loaded via corebench/score.py: {len(TGT)} prompts, "
      f"median {int(np.median([len(v) for v in TGT.values()]))} rankings/prompt")

def per_prompt_a2(arm, shuffle_targets=False, seed=0):
    """-> {pid: A2}, averaged over which annotator is held out. The arm's y-vector is the SUM of
    satisfaction over its selected criteria, exactly as score.py:yvec computes it."""
    f = ROOT/"corebench"/"results"/f"sat_{arm}.npz"
    if not f.exists(): return None
    sat = load_sat(f)
    rs = np.random.default_rng(seed)
    out = {}
    for pid, cells in sat.items():
        tv = TGT.get(pid)
        if not tv or len(tv) < 2: continue
        idxs = sorted({i for i, _ in cells})
        y = np.array([sum(cells.get((i, x), 0.0) for i in idxs) for x in L])
        cy = cls(y)
        acc = []
        for s in HELD_SEEDS:
            r = np.random.default_rng(s)
            hy = tv[int(r.integers(len(tv)))]
            if shuffle_targets: hy = list(rs.permutation(hy))
            hc = cls(hy)
            acc.append(float(np.mean([cy[t] == hc[t] for t in range(6)])))
        out[pid] = float(np.mean(acc))
    return out

def paired(a, b, B=2000, seed=0):
    """cluster (=prompt) bootstrap of the paired A2 difference. n_eff is PROMPTS, not pairs."""
    ks = sorted(set(a) & set(b))
    if len(ks) < 30: return None
    d = np.array([a[k]-b[k] for k in ks])
    rs = np.random.default_rng(seed)
    bs = np.array([d[rs.integers(0, len(d), len(d))].mean() for _ in range(B)])
    return {"n": len(ks), "diff": float(d.mean()),
            "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5))}

JUDGES = {"2B": "", "0.8B": "_08b"}
KS = [1, 2, 3, 4, 6, 8, 12]
res = {"floor": {}, "positive": {}, "topw_minus_topvar": {}, "topw_minus_random": {}, "placebo": {}}

print("  ── g=0 / FLOOR: three random_k4 arms differing in NOTHING but the draw ──")
for jn, sfx in JUDGES.items():
    rr = [per_prompt_a2(f"random_k4_s{s}{sfx}") for s in (0, 1, 2)]
    rr = [x for x in rr if x]
    if len(rr) < 2: print(f"    {jn:<5} UNAVAILABLE"); continue
    ds = [paired(rr[i], rr[j]) for i, j in itertools.combinations(range(len(rr)), 2)]
    ds = [d for d in ds if d]
    fl = max(abs(d["diff"]) for d in ds)
    hw = max(d["hi"]-d["lo"] for d in ds)/2
    res["floor"][jn] = {"max_abs_seed_diff": fl, "max_halfwidth": hw, "floor": max(fl, hw)}
    print(f"    {jn:<5} max |seed−seed| = {fl:.4f}   max CI halfwidth = {hw:.4f}   -> FLOOR {max(fl,hw):.4f}")

print("\n  ── POSITIVE CONTROL: oracle_k4 reads the human target directly ──")
for jn, sfx in JUDGES.items():
    o = per_prompt_a2(f"oracle_k4{sfx}"); r = per_prompt_a2(f"random_k4_s0{sfx}")
    if not (o and r): print(f"    {jn:<5} UNAVAILABLE"); continue
    d = paired(o, r); res["positive"][jn] = d
    fl = res["floor"].get(jn, {}).get("floor", float("inf"))
    print(f"    {jn:<5} oracle − random = {d['diff']:+.4f} [{d['lo']:+.4f}, {d['hi']:+.4f}]  "
          f"n={d['n']}   beats floor {fl:.4f}: {d['diff'] > fl}")

print("\n  ── THE ESTIMAND: topw_k4 − topvar_k4  (same machinery, ingredient removed) ──")
for jn, sfx in JUDGES.items():
    a = per_prompt_a2(f"topw_k4{sfx}"); b = per_prompt_a2(f"topvar_k4{sfx}")
    if not (a and b): print(f"    {jn:<5} UNAVAILABLE"); continue
    d = paired(a, b); res["topw_minus_topvar"][jn] = d
    fl = res["floor"].get(jn, {}).get("floor", float("inf"))
    print(f"    {jn:<5} topw − topvar = {d['diff']:+.4f} [{d['lo']:+.4f}, {d['hi']:+.4f}]  "
          f"n={d['n']}   |gap| > floor: {abs(d['diff']) > fl}")

# ⭐ THE COMPARATOR MUST BE THE BEST OF ITS CLASS, NOT ONE MEMBER OF IT. `topvar_k4` is ONE
# ③-admissible selector; if some other admissible arm scores higher, the gap above overstates what
# the ratings are worth. Sweeping every ③-admissible arm on disk turns a single-rival contrast into
# a bound against the whole class this site can build.
ADMISSIBLE = ["topvar_k4", "full", "generic", "genericpool16", "promptecho", "gen",
              "random_k4_s0", "random_k4_s1", "random_k4_s2"]
print("\n  ── THE ADMISSIBLE CLASS: every ③-admissible arm on disk, so the comparator is its BEST ──")
res["admissible_class"] = {}
for jn, sfx in JUDGES.items():
    tab = {}
    for arm in ADMISSIBLE:
        a = per_prompt_a2(f"{arm}{sfx}")
        if a: tab[arm] = float(np.mean(list(a.values())))
    if not tab: print(f"    {jn:<5} UNAVAILABLE"); continue
    best = max(tab, key=tab.get)
    w = per_prompt_a2(f"topw_k4{sfx}"); b = per_prompt_a2(f"{best}{sfx}")
    d = paired(w, b)
    res["admissible_class"][jn] = {"scores": tab, "best": best, "topw_minus_best": d}
    print(f"    {jn:<5} " + "  ".join(f"{k}={v:.4f}" for k, v in sorted(tab.items(), key=lambda x: -x[1])))
    fl = res["floor"][jn]["floor"]
    print(f"          BEST admissible = {best} ({tab[best]:.4f});  topw_k4 − best = "
          f"{d['diff']:+.4f} [{d['lo']:+.4f}, {d['hi']:+.4f}]   > floor {fl:.4f}: {d['diff'] > fl}")

print("\n  ── SPECIFICATION CURVE: topw_k − random_k over every k, both judges (all cells) ──")
print(f"    {'k':>3}  {'2B diff':>18}  {'0.8B diff':>18}   signs agree")
for k in KS:
    row, dd = {}, []
    for jn, sfx in JUDGES.items():
        a = per_prompt_a2(f"topw_k{k}{sfx}"); b = per_prompt_a2(f"random_k{k}_s0{sfx}")
        d = paired(a, b) if (a and b) else None
        row[jn] = d; dd.append(d["diff"] if d else None)
    res["topw_minus_random"][k] = row
    f = lambda d: f"{d['diff']:+.4f}[{d['lo']:+.3f},{d['hi']:+.3f}]" if d else "UNAVAILABLE"
    ag = "yes" if all(x is not None for x in dd) and dd[0]*dd[1] > 0 else \
         "no" if all(x is not None for x in dd) else "—"
    print(f"    {k:>3}  {f(row['2B']):>18}  {f(row['0.8B']):>18}   {ag}")

print("\n  ── PLACEBO: A2 against SHUFFLED human rankings (chance is MEASURED, not assumed) ──")
for arm in ("topw_k4", "topvar_k4", "oracle_k4", "random_k4_s0"):
    a = per_prompt_a2(arm, shuffle_targets=True, seed=7)
    if a: res["placebo"][arm] = float(np.mean(list(a.values())))
    print(f"    {arm:<14} A2 vs shuffled = {res['placebo'].get(arm, float('nan')):.4f}")
pl = list(res["placebo"].values())
pl_ok = bool(pl) and (max(pl)-min(pl)) < 0.05
print(f"    all arms land at the SAME chance level (spread < 0.05): {pl_ok}")

# ---- pre-registered kill, as a conditional ---------------------------------
pos_ok = all(res["positive"].get(j) and res["positive"][j]["diff"] > res["floor"][j]["floor"]
             for j in res["floor"])
if not (pos_ok and pl_ok and res["floor"]):
    verdict, world = "UNVERIFIED", "D (instrument not shown to resolve selection quality)"
else:
    # ⛔ THE VERDICT RULES ON THE ADMISSIBLE CLASS, NOT ON `topvar_k4`. The estimand is the value of
    # the ratings over the BEST rating-blind selector, and `topvar_k4` is not it -- it scores 0.4780,
    # BELOW the random baseline, which is §4's stated tell for a sham that is a poison rather than a
    # placebo. Ruling on it would have published +0.0695 as the ratings' value when most of that
    # number is the cost of ranking by variance.
    MIN_CLASS = 5     # a judge whose admissible class is barely populated cannot bound "the best"
    ruling = {}
    for j, blk in res["admissible_class"].items():
        if len(blk["scores"]) < MIN_CLASS:
            ruling[j] = ("UNVERIFIED", f"admissible class has only {len(blk['scores'])} arms "
                                       f"(<{MIN_CLASS}); 'the best admissible' is not bounded here")
            continue
        d, fl = blk["topw_minus_best"], res["floor"][j]["floor"]
        # P14: effect/floor below 1.5 admits NO count -- only a direction. Reported, not implied.
        ratio = abs(d["diff"]) / fl
        blk["effect_over_floor"] = ratio
        ruling[j] = (("B (EXPENSIVE)" if d["diff"] > fl else "A (CHEAP)"),
                     f"topw − best admissible = {d['diff']:+.4f} [{d['lo']:+.4f}, {d['hi']:+.4f}] "
                     f"vs floor {fl:.4f}   effect/floor = {ratio:.2f}"
                     + ("  -> NO COUNT ADMISSIBLE, direction only" if ratio < 1.5 else ""))
    print("\n  ── RULING, per judge, on the ADMISSIBLE-CLASS comparator ──")
    for j, (w, why) in ruling.items():
        print(f"    {j:<5} {w:<14} {why}")
    res["ruling"] = {j: list(v) for j, v in ruling.items()}
    live = [w for w, _ in ruling.values() if w != "UNVERIFIED"]
    if not live:
        verdict, world = "UNVERIFIED", "no judge has a populated admissible class"
    elif all(w.startswith("A") for w in live):
        verdict = "MEASURED"
        world = ("A (CHEAP — reading the ratings is NOT resolved above the floor against the best "
                 "rating-blind arm this site can build)")
    elif all(w.startswith("B") for w in live):
        verdict, world = "MEASURED", "B (EXPENSIVE — ③ forbids the mechanism)"
    else:
        verdict, world = "MEASURED", "C (CONFOUNDED — judges disagree)"
print(f"\n  VERDICT {verdict}   world: {world}")
res["verdict"], res["world"] = verdict, world
res["controls"] = {"positive": bool(pos_ok), "placebo": pl_ok}
OUT.mkdir(parents=True, exist_ok=True)
json.dump(res, open(OUT/"r477_value_of_ratings.json", "w"), indent=2, default=float)
sys.exit(0 if verdict != "UNVERIFIED" else 2)
