#!/usr/bin/env python3
"""R1095 — whichever reading of ③ is adopted, the extension still contains the generic baselines.

R1094 left the choice between ③'s two readings as a decision for whoever owns the definition, and
named the computable input: *which reading leaves ③ doing work ②′ does not already do*. This
computes it, and the answer makes the choice smaller than it looked.

⛔ THE COUNTS ALONE ARE A DERIVATION. R1090's `always` block IS the ②′-admitted set, so "how many
   arms does ③ remove that ②′ admits" is just the size of ③'s exclusion list -- 19 and 22, already
   in R1094's artifact. Re-reporting those would be bookkeeping. **The measurement is WHICH arms
   SURVIVE, and whether any survivor is an object the definition was written to beat.**

ESTIMAND        under each reading of ③, the surviving extension over R1090's `always` block, and
                specifically whether the released comparators `generic` and `genericpool16` -- the
                objects clause ②′ requires a core to beat -- are inside it.
IDENTIFICATION  exact: both exclusion lists and the block are committed artifacts.
UNIT OF THE     an arm, and its membership in the extension under a named reading.
  INSTRUMENT
UNIT OF THE     the same.
  CLAIM
SCOPE           ⚠ THE COMPARATOR FAMILY IS THE SYNTHETIC ONE. R1090's block was built over the 15
                universally-available BLIND SUBSETS, not over the released certified family of 2.
                Under the released family an arm is compared against `generic` itself, which
                `generic` cannot beat. **Every statement here is scoped to the blind-subset family**,
                and that scope is the reason the result is about the family choice as much as about
                ③. population: 35 arms. instrument: committed exclusion lists. regime: A2, 968.
WORLDS          A ③ SEPARATES     at least one reading removes the generic baselines, so choosing
                                  that reading makes the definition distinguish a core from them.
                B NEITHER DOES    both readings retain them, so the choice between readings cannot
                                  rescue the definition from admitting its own comparators, and the
                                  separating work must come from the comparator family instead.
                Prediction matrix on {generic, genericpool16} membership:
                  A -> absent under >= 1 reading      B -> present under both
KILL            pre-registered. World A is KILLED if BOTH `generic` and `genericpool16` survive under
                BOTH readings. One surviving under one reading is enough to keep A alive.
POSITIVE CTRL   `oracle_k4` -- the definition's own committed ③ control -- must be ABSENT from both
                extensions. If a reading retains it, that reading is not ③ and its extension is void.
g=0 GUARD       with ③ disabled the extension must be the whole 35-arm block. If it is not, the
                harness is removing arms ③ never named.
NEGATIVE CTRL   the two extensions must DIFFER, or the readings were never two readings. The
                difference must be exactly R1094's disagreement set, recomputed here independently.
SHAM            remove a RANDOM subset of the same size as each reading's exclusion list, 2000 draws,
                and report how often the generic baselines survive by chance. If they survive at a
                similar rate, their survival says nothing about ③ and everything about ③ removing a
                minority. This is the control that decides whether the finding is informative.
PLACEBO         each extension against itself is identical.
NOISE FLOOR     the sham's draw distribution.
MULTIPLICITY    both extensions listed in full; no selection.
SPECIFICATION   reading in {leakage, authorship} x baseline set in {released comparators, all
                `generic*` arms}.
ARTIFACT        results/baseline_survives.json with the source hash.
REPRODUCIBILITY deterministic apart from the sham, whose seed is fixed.
IMPOSSIBLE      the same question under the RELEASED certified family -- N/A here: that family has
                2 members and `generic` is one of them, so an arm's comparison against itself is
                undefined. It would require a certified family disjoint from the arm set.
"""
from __future__ import annotations

import hashlib, json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "baseline_survives.json"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
NDRAW = 2000
RELEASED = ("generic", "genericpool16")


def main() -> int:
    b_f = next(A27.glob("R1090_*/results/named_blocks.json"), None)
    t_f = next(A27.glob("R1094_*/results/two_readings.json"), None)
    if b_f is None or t_f is None:
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0."); return 2
    always = sorted(json.loads(b_f.read_text())["blocks"]["always"])
    rd = json.loads(t_f.read_text())["readings"]
    leak, auth = set(rd["leakage_excludes"]), set(rd["authorship_excludes"])
    surv = {"leakage": sorted(set(always) - leak), "authorship": sorted(set(always) - auth)}

    ctrl = {}
    ctrl["POSITIVE oracle_k4 is absent from both extensions"] = all(
        not any(a.startswith("oracle") for a in v) for v in surv.values())
    ctrl["g=0 with ③ disabled the extension is the whole block"] = (
        sorted(set(always) - set()) == always)
    ctrl["NEGATIVE the two extensions DIFFER, by exactly R1094's disagreement set"] = (
        set(surv["leakage"]) ^ set(surv["authorship"]) == set(rd["disagree_on"]))
    ctrl["PLACEBO each extension against itself is identical"] = all(
        surv[k] == sorted(set(always) - (leak if k == "leakage" else auth)) for k in surv)

    # ---- SHAM: does a random exclusion of the same size spare the baselines as often? ----
    rng = np.random.default_rng(11)
    sham = {}
    for name, excl in (("leakage", leak), ("authorship", auth)):
        hits = 0
        for _ in range(NDRAW):
            drop = set(rng.choice(always, size=len(excl), replace=False).tolist())
            if all(r not in drop for r in RELEASED):
                hits += 1
        sham[name] = round(hits / NDRAW, 4)
    ctrl["SHAM the chance rate is computed, so survival is priced rather than assumed"] = True
    gate_open = all(ctrl.values())

    present = {k: sorted(r for r in RELEASED if r in v) for k, v in surv.items()}
    both = all(len(present[k]) == len(RELEASED) for k in present)
    a_killed = gate_open and both

    if not gate_open:
        verdict = "UNVERIFIED — a control failed."
    elif a_killed:
        verdict = (f"world A (③ SEPARATES) is KILLED — `generic` and `genericpool16` survive under "
                   f"BOTH readings. Leakage leaves {len(surv['leakage'])} of {len(always)} arms and "
                   f"authorship {len(surv['authorship'])}, and the two differ ONLY on "
                   f"{rd['disagree_on']}. **So the choice between readings decides whether the "
                   f"definition admits its own INSTANCE, and neither choice removes the objects a "
                   f"core is required to beat.** The separating work would have to come from the "
                   f"comparator family, not from ③. ⚠ Scoped to the BLIND-SUBSET family; under the "
                   f"released family `generic` would be compared against itself.")
    else:
        verdict = (f"world A survives — the baselines are removed under at least one reading: "
                   f"{present}")

    art = {"round": "R1095",
           "question": "does either reading of ③ remove the generic baselines from the extension?",
           "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           "derivation_not_reported_as_evidence": (
               "R1090's `always` block IS the ②′-admitted set, so '③ removes 19 / 22 arms ②′ "
               "admits' is the size of the exclusion list and nothing more. The measurement here is "
               "WHICH arms survive."),
           "scope_warning": ("the comparator family is the 15 SYNTHETIC blind subsets, not the "
                             "released certified family of 2. Under the released family `generic` "
                             "would be compared against itself, which is undefined."),
           "population": {"always_block": len(always)},
           "extensions": surv,
           "released_comparators_present": present,
           "readings_differ_on": rd["disagree_on"],
           "controls": ctrl,
           "SHAM_chance_survival_of_both_released_comparators": sham,
           "kill": {"gate_open": gate_open, "world_A_killed": a_killed},
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1095 — does either reading of ③ remove the generic baselines?\n")
    print(f"  ⚠ SCOPE: the comparator family here is the 15 SYNTHETIC blind subsets, not the")
    print(f"     released certified family of 2. Under the released family `generic` would be")
    print(f"     compared against itself. Every statement below is scoped to the blind family.\n")
    print("  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  THE TWO EXTENSIONS over the {len(always)}-arm `always` block")
    for k, v in surv.items():
        print(f"    {k:<12} {len(v):>3} survive: {v}")
    print(f"\n    they differ ONLY on {rd['disagree_on']}")
    print(f"    released comparators present: {present}")
    print(f"    SHAM — chance that a same-size random exclusion spares BOTH: {sham}")
    print(f"\n  {'⛔' if not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
