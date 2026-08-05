#!/usr/bin/env python3
"""R490 — is the announced GPU round (a) new, and (b) able to settle ②∧③? Neither.

⚠ ACTION CLASS: CLOSURE. It resolves no fork; it kills a proposed FRONTIER action before compute, by
P4's prior-art gate and one table read. Labelling it a discovery would be closure disguised as one.

WHY. R490's predecessor closed: *"a strong rating-blind prompt-aware arm, scored under more than one
judge… one GPU round, and the first thing in this arc that compute would actually settle."* Two
claims, both checkable at zero cost, and the prior-art gate exists precisely for the first.

ESTIMAND
    (a) NOVELTY  — does a rating-blind, rubric-blind, prompt-aware core generator already exist here?
    (b) POWER    — can the second judge available on this site adjudicate the +0.0067 gap R485/R487
                   left open?
    ⚠ (b) is NOT "is the 0.8B judge worse". It is whether a contrast measured under it carries
    information about the ARM rather than about the JUDGE, which is decided by where an arm with a
    KNOWN advantage lands under it.

IDENTIFICATION
    (a) is a file question, answered by reading the source, not by memory (P4: "this thing's
        non-existence — did I establish it by asking the system, or did I read it somewhere?").
    (b) is identified from R479's committed attainment table: `oracle_k4` reads the human target
        DIRECTLY, so it is the strongest possible positive control on a judge's discriminating power.

SCOPE  population: this repository at HEAD · instrument: the file system and R479's artifact ·
       baseline: R479's 2B attainments · regime: the two judges this site has.

WORLDS
    A  NEW AND POWERED     no generator exists AND the second judge discriminates -> run the GPU round.
    B  ALREADY BUILT       a generator exists -> the proposal was to rebuild a measured object.
    C  UNDERPOWERED        the second judge cannot separate a known-large advantage -> a contrast
                           under it measures the judge, and the register must say what WOULD settle it.

PREDICTION MATRIX
                       generator exists   oracle attainment @0.8B    licenses
    A  new and powered        no                  high               spend the GPU
    B  already built          YES                 any                improve, do not rebuild
    C  underpowered           any                 LOW                name the real constraint

PRE-REGISTERED KILL
    B if `generate_core.py` is rating-blind and prompt-aware by its own source.
    C if oracle_k4's 0.8B attainment is below half its 2B attainment.
    A only if neither fires.

CONTROLS
    POSITIVE   the novelty check must FIND a generator that exists — verified by reading the file's
               own stated contract, not by its name. A filename is not a contract.
    g=0        the same check applied to a capability the site genuinely lacks (a third judge) must
               return absent. A prior-art gate that finds everything present is not a gate.
    NEGATIVE   `topw_k4`, an arm with a KNOWN advantage under 2B, must also collapse under 0.8B —
               otherwise the collapse is specific to the oracle and says nothing general.

ARTIFACT  results/r490_prior_art.json
"""
import json, pathlib, re, sys
ROOT = pathlib.Path(".")
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R490_the_announced_compute_was_already_built/results"

# ---- (a) NOVELTY: ask the system, do not recall -------------------------------------------------
gen = ROOT/"corebench"/"generate_core.py"
src = gen.read_text() if gen.exists() else ""
blind_rubric = bool(re.search(r"MUST NOT SEE\s+`?coval_full", src))
prompt_aware = bool(re.search(r"sees the\s+CONVERSATION and the FOUR RESPONSES", src))
exists = gen.exists() and blind_rubric and prompt_aware
print(f"  (a) NOVELTY — corebench/generate_core.py present: {gen.exists()}")
print(f"      its OWN CONTRACT says rubric-blind : {blind_rubric}")
print(f"      its OWN CONTRACT says prompt-aware : {prompt_aware}")
print(f"      POSITIVE: a generator exists and is the proposed object -> {exists}")
third = list((ROOT/"corebench"/"results").glob("sat_*_3b*.npz")) + \
        list((ROOT/"corebench"/"results").glob("sat_*_7b*.npz"))
print(f"      g=0: the same check for a THIRD judge finds {len(third)} artifacts -> "
      f"{'absent, as it must be' if not third else '⛔ gate finds everything'}")

# ---- (b) POWER: can the second judge separate a KNOWN advantage? ---------------------------------
c = json.load(open(ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/"
                   "R479_is_the_ceiling_the_judge_or_the_target/results/r479_ceiling.json"))
att = {k: (v["2B"]["att"], v["0.8B"]["att"]) for k, v in c["arms"].items()
       if v["2B"]["att"] is not None and v["0.8B"]["att"] is not None}
print(f"\n  (b) POWER — attainment of the Bayes ceiling, by judge (R479):")
for k, (a2, a8) in sorted(att.items(), key=lambda kv: -kv[1][0]):
    print(f"      {k:<16} 2B {a2:>+7.3f}   0.8B {a8:>+7.3f}   ratio {a8/a2 if a2 else float('nan'):>6.2f}")
o2, o8 = att["oracle_k4"]
t2, t8 = att["topw_k4"]
underpowered = o8 < 0.5*o2
neg_ok = t8 < 0.5*t2
print(f"      ORACLE reads the target DIRECTLY: 0.8B keeps {o8/o2:.1%} of its 2B attainment")
print(f"      NEGATIVE: topw_k4 collapses too ({t8/t2:.1%}) -> not oracle-specific: {neg_ok}")

if exists:
    verdict, world = "MEASURED", "B (ALREADY BUILT — the proposal was to rebuild a measured object)"
elif underpowered:
    verdict, world = "MEASURED", "C (UNDERPOWERED)"
else:
    verdict, world = "MEASURED", "A (new and powered)"
if exists and underpowered:
    world = ("B+C — the generator already exists AND the second judge cannot adjudicate the gap; "
             "what would settle ②∧③ is a judge STRONGER than Qwen3.5-2B, which this site lacks")
print(f"\n  VERDICT {verdict}\n  world: {world}")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"generator_exists": bool(exists), "rubric_blind": blind_rubric,
           "prompt_aware": prompt_aware, "third_judge_artifacts": len(third),
           "attainment": att, "oracle_ratio": o8/o2, "topw_ratio": t8/t2,
           "underpowered": bool(underpowered), "verdict": verdict, "world": world},
          open(OUT/"r490_prior_art.json", "w"), indent=2)
sys.exit(0)
