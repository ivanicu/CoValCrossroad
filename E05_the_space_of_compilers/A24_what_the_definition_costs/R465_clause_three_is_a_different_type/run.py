"""R465 -- clause ③ is a PROVENANCE predicate, not a behavioural one. Measured by collision.

⛔ RUNG 1 KILLS THE ANNOUNCED STEP'S FRAMING, ZERO COMPUTE. R464 closed proposing to "construct the
   adversarial case and check the PREDICATE rather than the label" for clause ③. But ③ -- *no prompt
   labels* -- is derived by R444 from `select_core.py`: it is determined by WHICH SELECTOR BUILT THE
   ARM. **It is invariant under every measurable property of the object** -- its criteria, its
   satisfaction scores, its A2. Two arms with identical criteria, one built by reading the prompt's
   human labels and one by luck, are behaviourally indistinguishable and ③ must treat them
   differently. **So "measure that ③'s predicate fires on an object" is not a coherent test:
   ③ is a claim about CONSTRUCTION HISTORY.** *Thirty-third announced step checked; its framing
   killed, and the corrected question is sharper than the original.*

⭐ THE CORRECTED QUESTION, AND IT IS ABOUT THE DEFINITION'S TYPE STRUCTURE. ①, ② and ④ are BEHAVIOURAL
   predicates: hand someone an arm and they can check them. ③ is not. If ③ can separate two
   behaviourally IDENTICAL objects, the definition mixes two kinds of clause, and "a perfect
   formulation" must say which clauses are checkable from the object alone. That is measurable: build
   a label-READING selector and a label-FREE one and count how often they emit the SAME criterion set.

⚠ AND PART OF IT IS FORCED, WHICH IS SEPARATED OUT RATHER THAN QUOTED. Where a prompt's rubric has
  exactly k criteria, there is only ONE k-subset, so every selector emits it and the collision is a
  DERIVATION, not evidence. Those prompts are reported separately and excluded from the rate.

ESTIMAND (named before the method)
    Over prompts where a genuine CHOICE exists (rubric size > k, so >= 2 candidate subsets):
        COLLISION = fraction of prompts where the ORACLE selector (reads the prompt's own human
                    ranking -- a label-reader, excluded by ③) emits exactly the criterion set that a
                    LABEL-FREE random selector emits.
    ⭐ Any collision > 0 proves ③ separates behaviourally identical objects, because on a collided
      prompt the two arms ARE the same set of criteria with the same scores and the same A2.

IDENTIFICATION
    Identified: `sat_full.npz` carries every rubric criterion per prompt, so both selectors are
    constructible with no new judging, and set identity is exact.
    ⚠ NOT identified: whether a REAL generator would collide -- this constructs the collision to show
    ③'s type, not to estimate a natural rate.

SCOPE  population : home-release prompts carrying rubric and core; forced-choice prompts separated
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs, 3 annotator draws held common
       baseline   : the label-free random selector at matched k
       regime     : k matched per prompt to the core's own k (2..4)

WORLDS
    W-PROVENANCE  collisions occur -> ③ separates behaviourally identical objects, so it is a
                  provenance predicate of a different TYPE from ①②④, and the definition must say
                  which clauses are checkable from the object alone.
    W-BEHAVIOURAL no collision ever occurs where a choice exists -> the label-reader's output is
                  always distinguishable, and ③ may be behaviourally implied after all.
    W-FORCED      collisions occur ONLY on prompts with no choice -> the whole effect is the
                  derivation above and nothing is shown.

PREDICTION MATRIX
                    collisions with choice   none   only forced
    W-PROVENANCE            0.90              0.05      0.05
    W-BEHAVIOURAL           0.05              0.90      0.05
    W-FORCED                0.05              0.05      0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the controls fire.
    collision rate on FORCED prompts != 1.0            -> UNVERIFIED (set identity is broken)
    collision rate on CHOICE prompts > 0               -> W-PROVENANCE
    collision rate on CHOICE prompts == 0 and n >= 200 -> W-BEHAVIOURAL
    otherwise                                          -> W-FORCED

CONTROLS
    DERIVATION  prompts where rubric size == k admit exactly ONE subset, so the collision rate there
                must be EXACTLY 1.0 by construction. It is checked, and it doubles as the positive
                control on set identity: if it is not 1.0, the comparison is broken.
    IDENTITY    on a collided prompt the two arms must have identical A2 to machine precision --
                the behavioural indistinguishability the round claims. Asserted, not assumed.
    NEGATIVE    two INDEPENDENT label-free draws collide at some rate too; that rate is the baseline
                a label-reader must be compared against, otherwise "they sometimes agree" says
                nothing about labels.
    SEEDS       3 draws of the random selector; spread reported.

MULTIPLICITY  2 selector pairs x 3 seeds x {forced, choice}; all printed.
ARTIFACT      results/r465_clause_three_type.json
IMPOSSIBLE HERE, NAMED
    * a natural collision rate for a real generator -- needs a generator; this constructs instead.
    * checking ③ on an object without its construction history -- that is the finding, not a gap.
"""
from __future__ import annotations
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R465 · clause ③ is a PROVENANCE predicate, not a behavioural one\n")
    print("  ⛔ RUNG 1, zero compute: ③ is derived from WHICH SELECTOR built the arm, so it is")
    print("     invariant under every measurable property of the object. 'Measure that ③'s predicate")
    print("     fires' is not a coherent test. Thirty-third step checked, framing killed.\n")

    for nm in ("full", "coval_core"):
        if not (SATD / f"sat_{nm}.npz").exists():
            print(f"  UNRUNNABLE: sat_{nm}.npz absent. Exit 2, never 0."); return 2
    rub, core = SC.load_sat(SATD / "sat_full.npz"), SC.load_sat(SATD / "sat_coval_core.npz")
    targets, _ = SC.load_targets()
    pids = sorted(set(rub) & set(core) & set(targets))
    n = len(pids)
    if n < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2
    SEEDS = (0, 1, 2)
    HC = {p: np.array([SC.cls(np.array(targets[p][int(np.random.default_rng(1000 * s + stable(p))
                                                      .integers(len(targets[p])))][0], float))
                       for s in SEEDS]) for p in pids}
    RM, KK = {}, {}
    for p in pids:
        cs = sorted({c for (c, _) in rub[p]})
        RM[p] = np.array([[rub[p].get((c, l), 0.0) for l in L] for c in cs])
        KK[p] = min(len({c for (c, _) in core[p]}), len(cs))
    forced = [p for p in pids if len(RM[p]) == KK[p]]
    choice = [p for p in pids if len(RM[p]) > KK[p]]
    print(f"  prompts {n}:  FORCED (rubric size == k, one subset only) {len(forced)}   "
          f"CHOICE {len(choice)}")

    def a2(idx, p):
        return float((signs(RM[p][list(idx)].mean(axis=0))[None, :] == HC[p]).mean())

    def cands(p, rg, cap=400):
        allc = list(itertools.combinations(range(len(RM[p])), KK[p]))
        if len(allc) <= cap:
            return allc
        return [tuple(sorted(rg.choice(len(RM[p]), size=KK[p], replace=False))) for _ in range(cap)]

    def pick(p, kind, seed):
        rg = np.random.default_rng(seed * 7717 + stable(p))
        cs = cands(p, rg)
        if kind == "oracle":                     # READS the prompt's own human ranking
            return tuple(sorted(cs[int(np.argmax([a2(c, p) for c in cs]))]))
        return tuple(sorted(cs[int(rg.integers(len(cs)))]))   # label-FREE

    print("\n  CONTROLS")
    fr = []
    for sd in SEEDS:
        hits = [pick(p, "oracle", sd) == pick(p, "random", sd) for p in forced] if forced else []
        fr.append(float(np.mean(hits)) if hits else float("nan"))
    d_ok = bool(forced) and abs(np.nanmean(fr) - 1.0) < 1e-12
    print(f"    DERIVATION  prompts with exactly ONE possible subset -> collision rate "
          f"{np.nanmean(fr):.4f} (must be exactly 1.0 BY CONSTRUCTION)   "
          f"{'PASS' if d_ok else '⛔ FAIL — set identity is broken'}")
    nr = []
    for sd in SEEDS:
        hits = [pick(p, "random", sd) == pick(p, "random", sd + 50) for p in choice]
        nr.append(float(np.mean(hits)))
    print(f"    NEGATIVE    two INDEPENDENT label-free draws collide at {np.mean(nr):.4f} — the")
    print(f"                baseline a label-reader must be read against")

    cr, ident = [], []
    for sd in SEEDS:
        hits, same = [], []
        for p in choice:
            o, r = pick(p, "oracle", sd), pick(p, "random", sd)
            hits.append(o == r)
            if o == r:
                same.append(abs(a2(o, p) - a2(r, p)) < 1e-12)
        cr.append(float(np.mean(hits)))
        ident.append(bool(np.all(same)) if same else True)
    rate = float(np.mean(cr))
    id_ok = all(ident)
    ncol = int(round(rate * len(choice)))
    print(f"    IDENTITY    on every collided prompt the two arms have identical A2 to machine")
    print(f"                precision: {id_ok}   {'PASS' if id_ok else '⛔ FAIL'}")

    print(f"\n  ⭐ COLLISION — does a LABEL-READER emit the same set as a LABEL-FREE selector?")
    print(f"    on CHOICE prompts (n={len(choice)}): {rate:.4f}  ({ncol} prompts), "
          f"seed spread {np.std(cr):.4f}")
    print(f"    on FORCED prompts (n={len(forced)}): {np.nanmean(fr):.4f}  <- DERIVATION, excluded")
    print(f"    label-free vs label-free baseline:  {np.mean(nr):.4f}")

    if not (d_ok and id_ok):
        world = "UNVERIFIED"
    elif rate > 0:
        world = "W-PROVENANCE"
    elif len(choice) >= 200:
        world = "W-BEHAVIOURAL"
    else:
        world = "W-FORCED"
    print(f"\n  WORLD: {world}")
    if world == "W-PROVENANCE":
        print(f"    ⭐ On {ncol} prompts a label-READING selector emits EXACTLY the set a label-FREE")
        print(f"       one emits — identical criteria, identical scores, identical A2 — and ③")
        print(f"       excludes one and admits the other. **③ separates behaviourally identical")
        print(f"       objects**, so it is a PROVENANCE predicate of a different TYPE from ①②④.")
        print(f"    ⭐ What that costs the formulation: ①, ② and ④ can be checked on an object you")
        print(f"       are handed; ③ cannot. A definition mixing the two types must SAY so, because")
        print(f"       a reader holding a criterion set can verify three of its four clauses and")
        print(f"       has no way to verify the fourth.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "n_forced": len(forced),
           "n_choice": len(choice), "collision_choice": rate, "collision_forced": float(np.nanmean(fr)),
           "baseline_labelfree_pair": float(np.mean(nr)), "n_collided": ncol,
           "seed_spread": float(np.std(cr)),
           "controls": {"derivation_ok": bool(d_ok), "identity_ok": bool(id_ok)}}
    (RES / "r465_clause_three_type.json").write_text(json.dumps(out, indent=2))
    print(f"\n  artifact: {RES/'r465_clause_three_type.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
