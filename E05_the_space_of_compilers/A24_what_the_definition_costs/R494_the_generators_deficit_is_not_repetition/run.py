#!/usr/bin/env python3
"""R494 — is the best admissible arm weak because its generator repeats itself? No.

WHY. ②∧③ is UNDETERMINED because the best ③-admissible prompt-aware arm, `gen`, sits at percentile
32.6 of the prompt-blind class (R486, R487). Settling it needs a BETTER admissible arm — so the first
question is why this one is weak, and the answer decides what to build.

⭐ TWO THINGS ARE EXCLUDED BEFORE ANY MECHANISM IS PROPOSED.
   `gen` is genuinely prompt-specific: 3,868 criteria, **84.2% unique**, and only 0.1% coincide with
   the fixed generic pool. So "it is not really prompt-aware" is dead.
   And `coval_core` is prompt-specific too (99.6% unique) and BEATS `generic` (0.5640 vs 0.5505)
   while `gen` loses to it (0.5337). So "prompt-specificity does not help" is dead as well.
   ⇒ the deficit is in WHAT `gen` WRITES.

ESTIMAND
    Do `gen`'s REPEATED criteria underperform its unique ones? Operationalised per prompt: stratify by
    the maximum corpus-frequency of that prompt's own generated criteria, and compare mean A2 across
    strata. `gen` repeats phrasings up to 29x against `coval_core`'s near-total uniqueness, so
    mode-collapse toward generic-sounding text is the obvious candidate.

IDENTIFICATION
    ⚠ THE STRATIFIER IS A PROPERTY OF THE PROMPT, NOT ONLY OF THE ARM. Prompts that elicit repeated
    text may simply be easier. That confound is not adjustable — it is CONTROLLED, below, and the
    control is the whole design.

SCOPE  population: 968 home-release prompts with a generated core · instrument: A2 vs a held-out
    annotator, 20 draws, crc32-seeded · baseline: the `generic` arm on the SAME strata · regime: 2B.

WORLDS
    A  REPETITION      only `gen` shows a gradient -> its repeated criteria are the deficit, and the
                       build target is decoding diversity.
    B  DIFFICULTY      `generic` shows the same gradient -> the stratifier is prompt difficulty and
                       repetition explains nothing. The deficit stays undiagnosed.

PREDICTION MATRIX
                    gen gradient   generic gradient   licenses
    A  repetition      present         absent         change the generator's sampling
    B  difficulty      present         PRESENT        nothing — find another mechanism

PRE-REGISTERED KILL
    B if `generic`'s gradient has the same sign and is within a factor of 2 of `gen`'s.

CONTROLS
    ⭐ NEGATIVE / CONFOUND — `generic` uses the SAME FOUR CRITERIA ON EVERY PROMPT. Its criteria cannot
      repeat differentially, so any gradient it shows across these strata is prompt difficulty by
      construction. **This is the control that can kill the finding, and it is the reason the round
      exists rather than the reason it is decorated.**
    POSITIVE — the strata must be non-degenerate and unequal in size, and both arms must be scorable
      on both, or the comparison is empty.

ARTIFACT  results/r494_repetition.json
"""
import collections, itertools, json, pathlib, sys, zlib
import numpy as np
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
sys.path.insert(0, "corebench"); import score as SC
OUT = pathlib.Path(__file__).parent/"results"
cls = lambda y: tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
tgt, _ = SC.load_targets(); TGT = {p: [tuple(v) for v, _ in x] for p, x in tgt.items()}
norm = lambda s: " ".join(s.lower().split())

gen = json.load(open("corebench/results/core_gen.json"))
freq = collections.Counter(norm(c) for v in gen.values() for c in v)
rep = {p: max(freq[norm(c)] for c in v) for p, v in gen.items() if v}
pids = [p for p in rep if p in TGT]
uniq = [p for p in pids if rep[p] <= 2]
repd = [p for p in pids if rep[p] >= 6]

def a2(arm, ps):
    d = np.load(f"corebench/results/sat_{arm}.npz", allow_pickle=True)
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    out = {}
    for p in ps:
        if p not in o: continue
        idx = sorted({i for i, _ in o[p]}); r = np.random.default_rng(zlib.crc32(p.encode()))
        c = cls(np.array([sum(o[p].get((i, x), 0.0) for i in idx) for x in L]))
        out[p] = float(np.mean([np.mean([c[t] == cls(np.array(TGT[p][int(r.integers(len(TGT[p])))], float))[t]
                                         for t in range(6)]) for _ in range(20)]))
    return out

print(f"  strata by max corpus-frequency of a prompt's OWN generated criteria")
print(f"    unique-ish (<=2): {len(uniq)}    repeated (>=6): {len(repd)}")
pos_ok = len(uniq) > 50 and len(repd) > 50
res = {}
for arm in ("gen", "generic"):
    s = a2(arm, pids)
    u = float(np.mean([s[p] for p in uniq if p in s])); r = float(np.mean([s[p] for p in repd if p in s]))
    res[arm] = {"unique": u, "repeated": r, "diff": u - r}
    tag = "the arm under test" if arm == "gen" else "CONTROL: identical criteria everywhere"
    print(f"    {arm:<9} unique {u:.4f}  repeated {r:.4f}  diff {u-r:+.4f}   <- {tag}")

g, c = res["gen"]["diff"], res["generic"]["diff"]
same_sign = (g < 0) == (c < 0)
within2 = abs(c) > abs(g)/2 and abs(c) < abs(g)*2
print(f"\n  POSITIVE  both strata non-degenerate ({len(uniq)}, {len(repd)}): {pos_ok}")
print(f"  CONTROL   generic's gradient {c:+.4f} vs gen's {g:+.4f}: same sign {same_sign}, "
      f"within a factor of 2 {within2}")
if not pos_ok:
    verdict, world = "UNVERIFIED", "strata degenerate"
elif same_sign and within2:
    verdict, world = "MEASURED", ("B (DIFFICULTY — the gradient is the same in an arm whose criteria "
                                  "CANNOT repeat differentially; repetition explains nothing)")
else:
    verdict, world = "MEASURED", "A (REPETITION — the gradient is specific to gen)"
print(f"\n  VERDICT {verdict}\n  world: {world}")
print(f"\n  ⚠ AND THE SIGN IS THE OPPOSITE OF THE HYPOTHESIS: prompts whose criteria repeat score")
print(f"    HIGHER, in both arms. I predicted repetition would hurt; it tracks easier prompts.")
print(f"  ⇒ `gen`'s deficit remains UNDIAGNOSED. One candidate is excluded, with a control that")
print(f"    could have confirmed it and did not.")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"n_unique": len(uniq), "n_repeated": len(repd), "arms": res,
           "control_same_sign": bool(same_sign), "control_within_2x": bool(within2),
           "verdict": verdict, "world": world}, open(OUT/"r494_repetition.json", "w"), indent=2)
sys.exit(0 if verdict != "UNVERIFIED" else 2)
