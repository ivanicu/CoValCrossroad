#!/usr/bin/env python3
"""R487 — the ③-admissible prompt-aware population is 32 arms, not three.

⛔ WHY, AND IT IS THE SAME ERROR A THIRD TIME. R478 caught R477 bounding the rival class by the nine
arms that happened to carry a `.npz`. R485 and R486 then bounded the ADMISSIBLE class by a hand-picked
list of 14 arms, and R486's report asserted *"gen, topvar_k4 and full are the whole population"*.
`corebench/results/` holds **101** `sat_*.npz`; 58 are base (2B, non-sham); **36 are ③-admissible and
32 of those are prompt-aware.** The unscored set includes an entire `transport_*` family and the
`random_k{2,3,6,8,12}` ladder — and R477's own spec curve showed the random family IMPROVING with k,
so `random_k12` was never going to sit where `random_k4` sits.

ESTIMAND
    BEST_ADMISSIBLE = max{ A2(a) : a ∈ every ③-admissible prompt-aware arm on disk }, and its
    percentile in the 1,820-subset prompt-blind class. R485's conflict claim and R486's downgrade
    both rest on this maximum, and both computed it over a subset chosen by hand.

IDENTIFICATION
    Fully identified from committed sat matrices. ⚠ Arms are admitted by `clause3_as_written.excluded`
    plus R475's ruling on `coval_core` (and therefore on its judge-replicates `coval_core_2bA/2bB`).
    Prompt-BLIND arms are named explicitly and held out, as in R485.

SCOPE
    population  per arm, the prompts it covers ∩ the pool's 968; REPORTED PER ARM and never pooled,
                because `provenance_probe` covers 4 prompts and a max over unequal populations is not
                a maximum. Arms below 90% coverage are listed and EXCLUDED from the max with a reason.
    instrument  A2 vs a held-out human annotator, 20 draws, crc32-seeded.
    baseline    the 1,820-subset class (R486 quantiles) and its cross-fitted ceiling 0.5404 (R478).
    regime      Qwen3.5-2B.

WORLDS
    A  R485 DIES        some admissible prompt-aware arm clears the ceiling -> ② and ③ are jointly
                        satisfiable here and the conflict was an artifact of my arm list.
    B  R485 SURVIVES,   none clears, and the best sits well inside the class -> R486's downgrade holds
       R486 HOLDS       and the honest state is still UNDETERMINED.
    C  R485 SURVIVES,   none clears BUT the best sits high in the class (>= p75) -> the admissible side
       R486 DIES        is NOT weak after all, and R486's "the arm is weak" downgrade was itself an
                        artifact of scoring only `gen`. R485's conflict reading is restored.

PREDICTION MATRIX
                        clears ceiling   best percentile   what it licenses
    A  R485 dies             YES              n/a          ② and ③ jointly satisfiable
    B  both hold             no             < p75          UNDETERMINED stands
    C  R486 dies             no             >= p75         conflict reading restored

PRE-REGISTERED KILL
    if positive_control_fires and g0_is_null:
        A if best > CEILING + FLOOR ; C if pct(best) >= 75 ; else B
    else:
        UNVERIFIED

CONTROLS
    POSITIVE   a ③-EXCLUDED arm (`topw_k4`) must clear the ceiling and sit at a high percentile — the
               bar is reachable and the scale measures reaching it.
    g=0        `random_k4_s0` must sit low. A scale on which a random arm scores high is not a scale.
    COVERAGE   every arm's prompt count printed; anything under 90% of the pool is excluded from the
               max WITH ITS COUNT, never silently dropped (`provenance_probe` covers 4).
    PLACEBO    the winning arm re-scored against shuffled rankings -> ~0.428.

MULTIPLICITY  all 32 arms printed with score, coverage and percentile — survivors and not.

ARTIFACT  results/r487_full_admissible.json     deterministic (crc32).

IMPOSSIBLE HERE, NAMED
    a second judge -- most admissible arms have no `_08b` build (R477).
    a NEW arm -- generating and judging criteria is a GPU round; this one only counts what exists.
"""
import collections, itertools, json, pathlib, sys, zlib
import numpy as np
ROOT = pathlib.Path("."); L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R487_the_admissible_population_is_32_not_three/results"
sys.path.insert(0, str(ROOT/"corebench")); import score as SC
sys.path.insert(0, str(ROOT/"assurance")); from clause3_as_written import excluded

CEILING, FLOOR, CHANCE = 0.5404, 0.0122, 0.428
BLIND = {"generic", "genericpool16", "promptecho", "generic_reprov"}
# R475: the dataset card puts the released core on ③'s excluded side; its judge-replicates too.
CORE_FAMILY = {"coval_core", "coval_core_2bA", "coval_core_2bB"}
def cls(y): return tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
tgt, _ = SC.load_targets(); TGT = {p: [tuple(y) for y, _ in v] for p, v in tgt.items()}

# ⛔ NOT EVERY `sat_*.npz` IS AN ARM ON THIS BENCHMARK. The `transport_*` family keys its cells
# `c365|int10006|ut3170|0` -- conversation / intent / utterance ids from a DIFFERENT study -- against
# this benchmark's `prompt|criterion|response`. Counting them as admissible arms was the same
# population error one scale down: files matching a naming pattern are not members of a population.
# They are excluded BY SCHEMA and named, never silently dropped.
SCHEMA_MISMATCH = []
def load(a):
    f = ROOT/"corebench"/"results"/f"sat_{a}.npz"
    if not f.exists(): return None
    d = np.load(f, allow_pickle=True)
    if len(d["meta"]) and str(d["meta"][0]).count("|") != 2:
        SCHEMA_MISMATCH.append(a); return None
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    return o

POOL = load("genericpool16"); pids = sorted(p for p in POOL if p in TGT)
H = np.zeros((len(pids), 20, 6), dtype=np.float32)
IDX = {p: i for i, p in enumerate(pids)}
for a, p in enumerate(pids):
    r = np.random.default_rng(zlib.crc32(p.encode())); v = TGT[p]
    for b in range(20): H[a, b] = cls(np.array(v[int(r.integers(len(v)))], float))
M = np.array([[[POOL[p].get((i, x), 0.0) for x in L] for i in range(16)] for p in pids])
census = np.array([float((np.stack([np.sign(Y[:, i]-Y[:, j]) for i, j in PAIRS], -1)[:, None, :] == H).mean())
                   for Y in (M[:, s, :].sum(1) for s in itertools.combinations(range(16), 4))])
pct = lambda s: float(100*(census < s).mean())
print(f"  pool prompts {len(pids)}   class subsets {len(census)}   ceiling {CEILING}  floor {FLOOR}")

def score(a, shuffle=False):
    o = load(a)
    if not o: return None
    ok = [p for p in o if p in IDX]
    if not ok: return None
    sel = [IDX[p] for p in ok]
    idx = {p: sorted({i for i, _ in o[p]}) for p in ok}
    Y = np.array([[sum(o[p].get((i, x), 0.0) for i in idx[p]) for x in L] for p in ok])
    c = np.stack([np.sign(Y[:, i]-Y[:, j]) for i, j in PAIRS], -1)
    Hs = H[sel]
    if shuffle:
        r = np.random.default_rng(11); Hs = Hs[:, :, r.permutation(6)]
    return float((c[:, None, :] == Hs).mean()), len(ok)

base = sorted(p.stem[4:] for p in (ROOT/"corebench"/"results").glob("sat_*.npz")
              if not p.stem.endswith(("_08b", "_08bR")) and "_sham" not in p.stem)
adm_aware = [a for a in base if not excluded(a) and a not in CORE_FAMILY and a not in BLIND]
print(f"  ③-admissible PROMPT-AWARE arms on disk: {len(adm_aware)}   (R485/R486 scored 3)\n")

rows = []
for a in adm_aware:
    r = score(a)
    if not r: continue
    s, n = r
    rows.append({"arm": a, "a2": s, "n": n, "cov": n/len(pids), "pct": pct(s),
                 "clears": bool(s > CEILING + FLOOR)})
rows.sort(key=lambda r: -r["a2"])
print(f"  {'arm':<26} {'A2':>7} {'prompts':>8} {'cov':>6} {'pctile':>7}  clears")
for r in rows:
    flag = "  ⚠ <90% coverage — excluded from the max" if r["cov"] < 0.9 else ""
    print(f"  {r['arm']:<26} {r['a2']:>7.4f} {r['n']:>8} {r['cov']:>6.1%} {r['pct']:>7.1f}"
          f"  {'YES' if r['clears'] else 'no'}{flag}")

elig = [r for r in rows if r["cov"] >= 0.9]
best = max(elig, key=lambda r: r["a2"])
tp = score("topw_k4"); rk = score("random_k4_s0")
pos_ok = tp and tp[0] > CEILING + FLOOR and pct(tp[0]) >= 90
g0_ok = rk and pct(rk[0]) <= 25
pl = score(best["arm"], shuffle=True)
pl_ok = pl and abs(pl[0] - CHANCE) < 0.03
print(f"\n  POSITIVE  topw_k4 clears and sits at p{pct(tp[0]):.1f}   : {pos_ok}")
print(f"  g=0       random_k4_s0 at p{pct(rk[0]):.1f}              : {g0_ok}")
print(f"  COVERAGE  arms under 90% excluded from the max: "
      f"{[r['arm'] for r in rows if r['cov'] < 0.9]}")
print(f"  SCHEMA    excluded as NOT THIS BENCHMARK (different key schema): {sorted(set(SCHEMA_MISMATCH))}")
print(f"  PLACEBO   {best['arm']} vs shuffled = {pl[0]:.4f}         : {pl_ok}")

print(f"\n  ── THE ESTIMAND ──")
print(f"    BEST ③-admissible prompt-aware arm : {best['arm']} at {best['a2']:.4f} (p{best['pct']:.1f})")
print(f"    R485/R486 used `gen`               : {next(r['a2'] for r in rows if r['arm']=='gen'):.4f} "
      f"(p{next(r['pct'] for r in rows if r['arm']=='gen'):.1f})")
print(f"    ceiling {CEILING}   clears: {best['clears']}")

if not (pos_ok and g0_ok and pl_ok):
    verdict, world = "UNVERIFIED", "a control failed"
elif best["clears"]:
    verdict, world = "MEASURED", f"A (R485 DIES — `{best['arm']}` clears the ceiling; ②∧③ satisfiable here)"
elif best["pct"] >= 75:
    verdict, world = "MEASURED", (f"C (R486 DIES — best admissible sits at p{best['pct']:.1f}, not weak; "
                                  f"R485's conflict reading is restored)")
else:
    verdict, world = "MEASURED", (f"B (BOTH HOLD — best admissible p{best['pct']:.1f} < p75; "
                                  f"the state stays UNDETERMINED)")
print(f"\n  VERDICT {verdict}\n  world: {world}")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"n_admissible_aware": len(adm_aware), "schema_mismatch": sorted(set(SCHEMA_MISMATCH)), "rows": rows, "best": best,
           "ceiling": CEILING, "controls": {"positive": bool(pos_ok), "g0": bool(g0_ok),
           "placebo": bool(pl_ok)}, "verdict": verdict, "world": world},
          open(OUT/"r487_full_admissible.json", "w"), indent=2)
sys.exit(0 if verdict != "UNVERIFIED" else 2)
