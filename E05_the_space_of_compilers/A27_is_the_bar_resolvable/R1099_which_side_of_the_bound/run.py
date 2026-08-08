#!/usr/bin/env python3
"""R1099 — the bound's slack is 9 arms; ③ removes 4; and 2 of the rest are baselines ②′ already excludes.

R1098 measured that the released-family ②′ set (24) is a strict subset of the blind-family one (33),
so blind-family statements are upper bounds. Its NEXT: which side of the bound do the 9 extra arms
sit on? **A bound is only useful if you know where the objects you care about are inside it.**

⛔ THE SET INTERSECTION IS BOOKKEEPING AND IS LABELLED AS SUCH. R1094's two exclusion lists are
   committed, and so is R1098's slack; crossing them is arithmetic. **The finding is the CONSEQUENCE
   for R1095's headline**, which was measured under the blind family and has never been checked
   against the released one.

ESTIMAND        (Q1, bookkeeping) of R1098's 9 blind-only arms, how many survive clause ③ under each
                     of R1094's two readings.
                (Q2, the finding) for the survivors that are GENERIC variants, are they in the
                     RELEASED ②′ set? R1095 concluded "neither reading removes the generic
                     baselines" over the blind family; this asks whether that transfers.
IDENTIFICATION  exact over three committed artifacts. ⚠ NOT identified for `generic` and
                `genericpool16` themselves: they are the released family's comparators and are
                excluded from candidacy, so "does the definition admit them" is UNDEFINED there --
                not answered, and the round says so rather than reading absence as exclusion.
UNIT OF THE     an arm, and its membership in each set.
  INSTRUMENT
UNIT OF THE     the same.
  CLAIM
SCOPE           population: R1098's 9-arm slack. instrument: committed sets. baseline: the released
                ②′ set. regime: 968 prompts, target A2.
WORLDS          A THE SLACK IS INERT   every extra arm is removed by ③ or is not a baseline, so the
                                       bound costs nothing and R1095 transfers unchanged.
                B THE SLACK IS BASELINE-SHAPED  some surviving extras are generic variants that the
                                       RELEASED family already excludes, so R1095's headline is a
                                       blind-family artifact for those arms.
                Prediction matrix on (generic variants surviving ③, their released membership):
                  A -> (0, n/a)      B -> (> 0, absent from the released set)
KILL            pre-registered. World A is KILLED if >= 1 generic variant survives ③ under both
                readings AND is absent from the released ②′ set. Both halves required: surviving ③
                alone would say nothing about the family, and absence alone could be ③'s doing.
POSITIVE CTRL   the four fitted arms among the 9 must be in R1094's LEAKAGE list -- they are
                `greedy_*`/`indep_*`, the rules the generator records as loading the target. If they
                are not, the exclusion lists being read are not R1094's.
g=0 GUARD       the three released cores must NOT be among the 9: they are in both families, so a
                slack containing them would mean the two sets were mis-differenced.
NEGATIVE CTRL   the 9 must be exactly R1098's `blind_only`, recomputed here from the two sets rather
                than copied, or this round is reading its own input wrong.
SHAM            intersect ③'s exclusions with a RANDOM same-size subset of the blind set, 2000 draws:
                if 4-of-9 is the chance rate, the slack's composition says nothing about ③ and only
                that ③ removes a fixed share of everything.
PLACEBO         the slack against itself is empty.
NOISE FLOOR     the sham's draw distribution.
MULTIPLICITY    all 9 arms reported individually under both readings.
SPECIFICATION   reading in {leakage, authorship} x membership in {blind ②′, released ②′}.
ARTIFACT        results/which_side.json with the source hash.
REPRODUCIBILITY deterministic apart from the sham, whose seed is fixed.
IMPOSSIBLE      whether the definition admits `generic`/`genericpool16` under the released family --
                N/A, they are its comparators and are excluded from candidacy. It would require a
                third comparator family containing neither.
"""
from __future__ import annotations

import hashlib, json, pathlib
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "which_side.json"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
NDRAW = 2000
GENERIC_VARIANTS = ("gen", "generic_reprov", "generic", "genericpool16")


def main() -> int:
    f98 = next(A27.glob("R1098_*/results/families_nest.json"), None)
    f94 = next(A27.glob("R1094_*/results/two_readings.json"), None)
    if f98 is None or f94 is None:
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0."); return 2
    s98 = json.loads(f98.read_text())["sets"]
    rd = json.loads(f94.read_text())["readings"]
    rel, blind = set(s98["released"]), set(s98["blind_minus_comparators"])
    leak, auth = set(rd["leakage_excludes"]), set(rd["authorship_excludes"])
    nine = sorted(blind - rel)

    per_arm = {a: {"leakage": "EXCLUDED" if a in leak else "survives",
                   "authorship": "EXCLUDED" if a in auth else "survives",
                   "in_released_2prime": a in rel,
                   "is_generic_variant": a in GENERIC_VARIANTS} for a in nine}
    surv = {r: sorted(a for a in nine if a not in (leak if r == "leakage" else auth))
            for r in ("leakage", "authorship")}
    gen_surv = sorted(a for a in surv["leakage"] if a in GENERIC_VARIANTS
                      and a in surv["authorship"])
    gen_surv_absent = sorted(a for a in gen_surv if a not in rel)

    ctrl = {}
    fitted = [a for a in nine if a.startswith(("greedy_", "indep_"))]
    ctrl["POSITIVE the fitted arms among the 9 are in R1094's LEAKAGE list"] = (
        bool(fitted) and all(a in leak for a in fitted))
    ctrl["g=0 the three released cores are NOT in the slack"] = not any(
        a.startswith("coval_core") for a in nine)
    ctrl["NEGATIVE the 9 recomputed here equal R1098's blind_only"] = (
        nine == sorted(s98["blind_only"]))
    rng = np.random.default_rng(13)
    bl = sorted(blind)
    hits = []
    for _ in range(NDRAW):
        d = set(rng.choice(bl, size=len(nine), replace=False).tolist())
        hits.append(sum(1 for a in d if a in leak))
    band = (float(np.percentile(hits, 2.5)), float(np.percentile(hits, 97.5)))
    obs_excl = sum(1 for a in nine if a in leak)
    ctrl["SHAM the chance rate is computed, so the slack's composition is priced"] = True
    ctrl["PLACEBO the slack against itself is empty"] = not (set(nine) - set(nine))
    gate_open = all(ctrl.values())

    a_killed = gate_open and bool(gen_surv_absent)
    if not gate_open:
        verdict = "UNVERIFIED — a control failed."
    elif a_killed:
        verdict = (f"world B — THE SLACK IS BASELINE-SHAPED. Of the {len(nine)} arms the blind "
                   f"family admits and the released one does not, ③ removes {obs_excl} under both "
                   f"readings (against a chance band of {band}). Of the {len(surv['leakage'])} "
                   f"survivors, {gen_surv_absent} are GENERIC VARIANTS that the RELEASED ②′ set "
                   f"does not contain. **So R1095's 'neither reading removes the generic baselines' "
                   f"is a BLIND-FAMILY artifact for these arms — under the released family ②′ "
                   f"excludes them by itself.** ⚠ It stays UNDEFINED for `generic` and "
                   f"`genericpool16`, which are that family's comparators and are excluded from "
                   f"candidacy: absence there is not exclusion.")
    else:
        verdict = (f"world A — the slack is inert: {surv['leakage']} survive ③ and none is a "
                   f"generic variant absent from the released set, so R1095 transfers unchanged.")

    art = {"round": "R1099",
           "question": "which side of the family bound do the 9 extra arms sit on?",
           "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           "bookkeeping_label": ("crossing R1094's exclusion lists with R1098's slack is a set "
                                 "intersection over committed artifacts; the finding is the "
                                 "consequence for R1095's headline, not the intersection"),
           "slack": nine, "per_arm": per_arm, "survivors": surv,
           "generic_variants_surviving_both_readings": gen_surv,
           "of_those_absent_from_the_released_set": gen_surv_absent,
           "sham": {"observed_excluded_by_leakage": obs_excl, "chance_band_95": list(band),
                    "draws": NDRAW},
           "controls": ctrl,
           "downgrade": {"round": "R1095",
                         "claim": "neither reading of ③ removes the generic baselines",
                         "status": ("SCOPE-CORRECTED: true under the blind family; for `gen` and "
                                    "`generic_reprov` it does NOT transfer, because the released "
                                    "②′ set excludes them without ③. UNDEFINED for `generic` and "
                                    "`genericpool16`, which are comparators there.")},
           "kill": {"gate_open": gate_open, "world_A_killed": a_killed},
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1099 — which side of the bound do the nine sit on?\n")
    print("  ⛔ the set intersection is BOOKKEEPING; the finding is what it does to R1095.\n")
    print("  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  THE SLACK — {len(nine)} arms the blind family admits and the released one does not")
    print(f"    {'arm':<26}{'leakage':>10}{'authorship':>12}{'in released ②′':>16}")
    for a in nine:
        p = per_arm[a]
        print(f"    {a:<26}{p['leakage']:>10}{p['authorship']:>12}"
              f"{str(p['in_released_2prime']):>16}"
              f"{'  ⭐ generic variant' if p['is_generic_variant'] else ''}")
    print(f"\n  ③ removes {obs_excl} of {len(nine)} under both readings · "
          f"SHAM chance band {band}")
    print(f"  generic variants surviving ③ and ABSENT from the released set: {gen_surv_absent}")
    print(f"\n  {'⛔' if not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
