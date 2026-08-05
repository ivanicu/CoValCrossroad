#!/usr/bin/env python3
"""R485 — is the definition SATISFIABLE? Clause ② and clause ③ may be in direct tension.

WHY, AND IT IS THE CAMPAIGN'S OWN QUESTION RATHER THAN ITS PLUMBING. The extension is 0 (R475: the
dataset card puts `coval_core` on the wrong side of ③) and ③ costs nothing to keep (R477). Both are
facts about the release. Neither asks the thing a DEFINITION lives or dies by: **can anything satisfy
it?** A definition with an empty extension because the world happens not to contain a member is fine.
A definition with an empty extension because its own clauses CONFLICT is defective.

    ②  better than the best generalising prompt-blind set
    ③  not built by reading the prompt's human rankings or its annotator ratings

⭐ The tension is visible in numbers already committed: every ③-ADMISSIBLE arm on this site is either
IN the prompt-blind class or below it, while the only arms that clear the prompt-blind ceiling are
w-readers ③ excludes. If that holds under measurement, ②∧③ is unsatisfiable HERE.

ESTIMAND
    GAP_ADMISSIBLE = max{ A2(a) : a is ③-admissible AND prompt-aware } − CEILING_PROMPT_BLIND
    where CEILING is R478's CROSS-FITTED best 4-subset of `genericpool16` (0.5404), not its in-sample
    max, because ② says "the BEST prompt-blind set" and an in-sample maximum over 1,820 is an order
    statistic. GAP > floor ⇒ ② and ③ are jointly satisfiable here. GAP <= floor ⇒ they are not.

    ⚠ PROMPT-AWARE is the load-bearing restriction. A prompt-BLIND arm cannot satisfy ② against the
    prompt-blind class -- it is a member of the class, so the comparison is degenerate and would
    "fail" for a reason that has nothing to do with ③. `generic` and `genericpool16` are therefore
    EXCLUDED from the numerator and reported separately, not silently dropped.

IDENTIFICATION
    Identified from committed sat matrices. ⚠ It bounds satisfiability ON THIS SITE with THESE ARMS.
    It cannot show ②∧③ is unsatisfiable in principle -- only that nothing built here satisfies both,
    which is what the definition's authors can actually act on.

SCOPE
    population  968 prompts common to the arms compared, counted in-run.
    instrument  A2 vs a held-out human annotator, 20 draws, crc32-seeded.
    baseline    CEILING = 0.5404 (R478 cross-fitted); floor = 0.0122 (R477, measured).
    regime      Qwen3.5-2B judge; k=4; the 0.8B judge cannot host this comparison (R477: five of the
                admissible arms have no `_08b` build), and that is a scope limit, not a result.

WORLDS
    A  SATISFIABLE     some ③-admissible prompt-aware arm beats CEILING by > floor. The definition is
                       fine and the release simply ships no member.
    B  CONFLICTED      none does, while ③-EXCLUDED arms do. ② and ③ pull against each other: the only
                       route to beating the prompt-blind class that anyone has found is reading the
                       ratings, which ③ forbids. The definition is defective as written.
    C  BAR UNREACHABLE nothing beats CEILING, admissible or not -- then the null says nothing about
                       ③, only that the bar is set above what any arm here reaches. -> UNVERIFIED.

PREDICTION MATRIX
                     admissible beats?   excluded beats?   what it licenses
    A  satisfiable         YES               either        keep ② and ③ both
    B  conflicted          NO                 YES          one clause must yield; name which
    C  unreachable         NO                 NO           UNVERIFIED — the bar, not the clause

PRE-REGISTERED KILL  (conditional; the positive control decides whether the null is readable)
    if some ③-EXCLUDED arm beats CEILING by > floor:      # the bar is demonstrably reachable
        B if no ③-admissible prompt-aware arm beats CEILING by > floor
        A otherwise
    else:
        UNVERIFIED — a null about ③ is inadmissible when nothing clears the bar at all

CONTROLS
    POSITIVE ⭐ the ③-EXCLUDED w-readers must clear CEILING. This is what makes a null about the
               admissible arms EVIDENCE rather than silence: it proves the bar is reachable and that
               the design can detect clearing it. If they fail, the round is UNVERIFIED, not "B".
    g=0        `random_k4_s0` must NOT clear CEILING. A bar that a random arm clears is not a bar.
    PLACEBO    every arm re-scored against shuffled rankings -> ~0.428 (R477, measured chance).
    SCOPE CTRL prompt-BLIND admissible arms reported separately and excluded from the numerator,
               because their comparison against their own class is degenerate.

MULTIPLICITY  every arm printed with its admissibility and prompt-awareness, clearing or not.

ARTIFACT  results/r485_satisfiability.json     deterministic (crc32); two-process byte-identity.

IMPOSSIBLE HERE, NAMED
    "unsatisfiable in principle" -- would require enumerating all possible prompt-aware rating-blind
        selectors, which is not a finite object. This round bounds THIS SITE and says so.
    second judge -- five admissible arms have no `_08b` build (R477); the comparison cannot be made.
"""
import collections, itertools, json, pathlib, sys, zlib
import numpy as np
ROOT = pathlib.Path("."); L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R485_is_the_definition_satisfiable_at_all/results"
sys.path.insert(0, str(ROOT/"corebench")); import score as SC
sys.path.insert(0, str(ROOT/"assurance")); from clause3_as_written import excluded, selector_of

CEILING, FLOOR, CHANCE = 0.5404, 0.0122, 0.428      # R478 cross-fitted · R477 measured · R477 measured
def cls(y): return tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
tgt, _ = SC.load_targets(); TGT = {p: [tuple(y) for y, _ in v] for p, v in tgt.items()}

# PROMPT-BLIND arms: their criteria never see the prompt. Named explicitly rather than inferred.
PROMPT_BLIND = {"generic", "genericpool16", "promptecho"}
ARMS = ["coval_core", "gen", "topvar_k4", "full", "generic", "genericpool16", "promptecho",
        "random_k4_s0", "topw_k4", "topabs_k4", "topwvar_k4", "oracle_k4", "greedy_k4_fit1",
        "indep_k4_fit1"]

def a2(arm, shuffle=False):
    f = ROOT/"corebench"/"results"/f"sat_{arm}.npz"
    if not f.exists(): return None
    d = np.load(f, allow_pickle=True); o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    acc = []
    for p, c in o.items():
        if p not in TGT: continue
        idx = sorted({i for i, _ in c}); r = np.random.default_rng(zlib.crc32(p.encode()))
        cc = cls(np.array([sum(c.get((i, x), 0.0) for i in idx) for x in L]))
        got = []
        for _ in range(20):
            y = list(TGT[p][int(r.integers(len(TGT[p])))])
            if shuffle: y = list(r.permutation(y))
            hc = cls(np.array(y, float))
            got.append(np.mean([cc[t] == hc[t] for t in range(6)]))
        acc.append(float(np.mean(got)))
    return (float(np.mean(acc)), len(acc)) if acc else None

print(f"  CEILING (R478 cross-fitted best prompt-blind 4-subset) = {CEILING}")
print(f"  FLOOR   (R477 measured, three random_k4 arms)          = {FLOOR}\n")
print(f"  {'arm':<16} {'A2':>7} {'n':>5}  {'③':<10} {'prompt':<7} clears ceiling+floor")
rows = {}
for a in ARMS:
    r = a2(a)
    if not r: print(f"  {a:<16} {'—':>7}  UNAVAILABLE"); continue
    s, n = r
    exc = excluded(a) or a == "coval_core"        # R475: the card puts coval_core on the excluded side
    blind = a in PROMPT_BLIND
    clears = s > CEILING + FLOOR
    rows[a] = {"a2": s, "n": n, "excluded": bool(exc), "prompt_blind": bool(blind), "clears": bool(clears)}
    print(f"  {a:<16} {s:>7.4f} {n:>5}  {'EXCLUDED' if exc else 'admissible':<10} "
          f"{'blind' if blind else 'aware':<7} {'YES' if clears else 'no'}")

adm_aware = {a: v for a, v in rows.items() if not v["excluded"] and not v["prompt_blind"]}
exc_arms = {a: v for a, v in rows.items() if v["excluded"]}
pos_ok = any(v["clears"] for v in exc_arms.values())
g0_ok = not rows.get("random_k4_s0", {}).get("clears", True)
pl = a2("topw_k4", shuffle=True)
pl_ok = pl and abs(pl[0] - CHANCE) < 0.03

print(f"\n  POSITIVE ⭐ some ③-EXCLUDED arm clears the ceiling: {pos_ok}   "
      f"({[a for a, v in exc_arms.items() if v['clears']]})")
print(f"  g=0       random_k4_s0 does NOT clear it              : {g0_ok}")
print(f"  PLACEBO   topw_k4 vs shuffled rankings = {pl[0]:.4f}      : {pl_ok}")
print(f"  SCOPE     prompt-BLIND admissible arms excluded from the numerator: "
      f"{sorted(a for a, v in rows.items() if v['prompt_blind'] and not v['excluded'])}")

best = max(adm_aware.items(), key=lambda kv: kv[1]["a2"], default=(None, {"a2": float('nan')}))
gap = best[1]["a2"] - CEILING
print(f"\n  ── THE ESTIMAND ──")
print(f"    best ③-admissible PROMPT-AWARE arm : {best[0]} at {best[1]['a2']:.4f}")
print(f"    ceiling                            : {CEILING}")
print(f"    GAP                                : {gap:+.4f}   (floor {FLOOR})")

if not (pos_ok and g0_ok and pl_ok):
    verdict, world = "UNVERIFIED", "C (the bar is not demonstrably reachable, or a control failed)"
elif gap > FLOOR:
    verdict, world = "MEASURED", "A (SATISFIABLE — a rating-blind prompt-aware arm clears the class)"
else:
    verdict, world = "MEASURED", ("B (CONFLICTED — ② and ③ pull against each other: on this site the "
                                  "only arms that clear the prompt-blind class are the ones ③ excludes)")
print(f"\n  VERDICT {verdict}\n  world: {world}")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"ceiling": CEILING, "floor": FLOOR, "rows": rows, "best_admissible_aware": best[0],
           "gap": gap, "controls": {"positive": bool(pos_ok), "g0": bool(g0_ok), "placebo": bool(pl_ok)},
           "verdict": verdict, "world": world}, open(OUT/"r485_satisfiability.json", "w"), indent=2)
sys.exit(0 if verdict != "UNVERIFIED" else 2)
