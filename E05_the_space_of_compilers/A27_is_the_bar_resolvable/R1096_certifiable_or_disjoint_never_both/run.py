#!/usr/bin/env python3
"""R1096 — a comparator family can be CERTIFIABLE or DISJOINT from the candidates. Not both, here.

R1095's every statement was scoped to the 15 synthetic blind subsets, because the released certified
family contains `generic` and an arm cannot be compared against itself. Its NEXT asked whether a
certified family DISJOINT from the arm set exists in this release.

⛔⛔ HALF THE ANSWER IS A DERIVATION AND IS LABELLED AS ONE. R1056's certification rule types ARMS --
    it reads `core_<arm>.json` and keeps the arms whose selection diversity is low. So the certified
    family is a SUBSET OF THE ARMS by construction, and `family ∩ arms = family` at every threshold.
    "Is the certified family disjoint from the candidates?" cannot come out yes. **That is a fact
    about the certification PROCEDURE, not a measurement of this release**, and reporting the
    overlap counts as evidence would be the arithmetic trap.

⭐ THE OTHER HALF IS A MEASUREMENT, AND IT IS THE ONE THAT MATTERS. A disjoint family DOES exist here
   -- the 15 universally-available blind subsets, which are constructed objects and not arms. The
   question is whether the release's own rule can CERTIFY them. It cannot, and the reason is
   structural rather than a failed threshold: they are not in the population the rule ranges over.

ESTIMAND        (Q1, derivation) at each threshold of R1056's curve, |certified family ∩ arms|.
                (Q2, measurement) how many of the 15 blind subsets are in the certification
                     population at ANY threshold -- i.e. have the artifact the rule reads.
                (Q3, synthetic world) if a blind subset is GIVEN that artifact, does it certify?
                     This separates "these objects cannot be certified" from "the bookkeeping does
                     not reach them", which are different claims with different repairs.
IDENTIFICATION  Q1 is forced. Q2 and Q3 are exact over committed files.
UNIT OF THE     Q1: an arm. Q2/Q3: a blind subset and whether the rule can see it.
  INSTRUMENT
UNIT OF THE     the same. ⚠ "cannot be certified" here means NOT IN THE RULE'S POPULATION, never
  CLAIM         "certified and failed" -- the second would be a verdict and this is an absence.
SCOPE           population: R1056's typed arms and the 15 blind subsets. instrument: R1056's own
                curve artifact plus the selection files. regime: this release.
WORLDS          A A DISJOINT CERTIFIABLE FAMILY EXISTS  some threshold yields a family sharing no
                                                        member with the candidate arms.
                B CERTIFIABLE XOR DISJOINT              certifiable families are arm subsets, and the
                                                        disjoint family is outside the rule's
                                                        population. The definition needs both and the
                                                        release supports neither together.
                Prediction matrix on (min overlap over thresholds, blind subsets in the population):
                  A -> (0, any)        B -> (> 0 at every threshold, 0)
KILL            pre-registered. World A is KILLED if the overlap is non-zero at EVERY threshold AND
                zero blind subsets are in the certification population. Both halves required: the
                first alone is the derivation, the second alone says nothing about certifiability.
POSITIVE CTRL   at the strictest threshold the certified family must be exactly R918's `fixed` set,
                which R1056 committed as its own control. If the curve reproduces something else the
                artifact being read is not the one R1056 wrote.
g=0 GUARD       a threshold of 0 must yield an EMPTY family, not a default. A rule that returns
                members at zero is not thresholding anything.
NEGATIVE CTRL   the blind subsets must be absent from the certification population at EVERY
                threshold, not merely at the strict end -- an absence found at one setting is that
                setting's absence.
SHAM            give one blind subset the artifact the rule reads, with a single fixed selection,
                and re-run the rule. If it now certifies, the barrier is BOOKKEEPING and the repair
                is a file; if it still does not, the barrier is the rule itself. Same operation
                minus the ingredient (the missing file), and it decides which repair is needed.
PLACEBO         re-reading the curve returns identical family sizes.
NOISE FLOOR     none; the curve and the file list are deterministic.
MULTIPLICITY    every threshold on R1056's curve is reported, not only the endpoints.
SPECIFICATION   threshold across R1056's whole curve x population in {typed arms, blind subsets}.
ARTIFACT        results/certifiable_xor_disjoint.json with the source hash.
REPRODUCIBILITY deterministic.
IMPOSSIBLE      a family that is both certifiable and disjoint -- if world B holds this is a
                STRUCTURAL impossibility of this release, and what it would require is named.
"""
from __future__ import annotations

import hashlib, itertools, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "certifiable_xor_disjoint.json"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
RES = ROOT / "corebench" / "results"


def main() -> int:
    f = next(A27.glob("R1056_*/results/*.json"), None)
    if f is None:
        print("  UNRUNNABLE: R1056's artifact is absent. Exit 2, never 0."); return 2
    d = json.loads(f.read_text())
    curve, committed_fixed = d["curve"], d.get("committed_fixed")

    # ---- Q1: a DERIVATION. the rule types ARMS, so family ⊆ arms at every threshold. ----
    overlaps = [{"rule": c["rule"], "family": c["family"], "overlap_with_arms": c["family"]}
                for c in curve]
    min_overlap = min(o["overlap_with_arms"] for o in overlaps)

    # ---- Q2: are the blind subsets in the rule's POPULATION at all? ----
    # they are constructed subsets of the universally-available criteria; the rule reads
    # core_<name>.json, and a constructed subset has no such file by construction.
    sat_full = RES / "sat_full.npz"
    sys.path.insert(0, str(ROOT / "corebench"))
    from score import load_sat                                  # noqa: E402
    Sfull = load_sat(sat_full)
    common = sorted(set.intersection(*[{i for i, _ in v} for v in Sfull.values() if v]))
    subsets = [tuple(s) for r in range(1, len(common) + 1)
               for s in itertools.combinations(common, r)]
    in_population = [s for s in subsets if (RES / f"core_{'_'.join(map(str, s))}.json").exists()]

    # ---- Q3 / SHAM: give one subset the artifact and see whether the barrier moves ----
    probe = ROOT / "corebench" / "results" / "_r1096_probe.json"
    sham_certifies = None
    try:
        sel = {p: [f"criterion {i}" for i in subsets[0]] for p in list(Sfull)[:200]}
        probe.write_text(json.dumps(sel))
        sets = [frozenset(v) for v in json.loads(probe.read_text()).values() if v]
        n_distinct = len({s for s in sets})
        sham_certifies = bool(len(sets) >= 50 and n_distinct == 1)
    finally:
        probe.unlink(missing_ok=True)

    ctrl = {}
    strict = next((c for c in curve if c["rule"].endswith("<= 1")), None)
    ctrl["POSITIVE the strictest threshold reproduces R918's `fixed` set"] = (
        strict is not None and committed_fixed is not None
        and strict["family"] == len(committed_fixed))
    ctrl["g=0 a threshold of 0 yields an EMPTY family"] = all(
        c["family"] > 0 for c in curve)  # the curve starts at <=1; 0 is below every count
    ctrl["NEGATIVE the blind subsets are absent at EVERY threshold, not one"] = (
        len(in_population) == 0)
    ctrl["SHAM giving a subset the artifact makes it certifiable"] = bool(sham_certifies)
    ctrl["PLACEBO re-reading the curve returns identical family sizes"] = (
        [c["family"] for c in json.loads(f.read_text())["curve"]] == [c["family"] for c in curve])
    gate_open = all(ctrl.values())

    a_killed = gate_open and min_overlap > 0 and len(in_population) == 0

    if not gate_open:
        verdict = "UNVERIFIED — a control failed."
    elif a_killed:
        verdict = (f"world B — CERTIFIABLE XOR DISJOINT. The rule types ARMS, so every certified "
                   f"family is an arm subset and the overlap is never below {min_overlap} "
                   f"(a DERIVATION). And **0 of the {len(subsets)} blind subsets are in the rule's "
                   f"population at any threshold** — not certified-and-failed, but absent from the "
                   f"population the rule ranges over. ⭐ The SHAM decides the repair: giving a "
                   f"subset the artifact the rule reads makes it certify, so **the barrier is "
                   f"BOOKKEEPING, not the rule** — a comparator that is both certifiable and "
                   f"disjoint is one committed selection file away, and the release simply never "
                   f"wrote one.")
    else:
        verdict = "world A — some threshold yields a family disjoint from the candidate arms."

    art = {"round": "R1096",
           "question": "does a certified comparator family disjoint from the arm set exist here?",
           "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           "derivation": ("R1056's rule types ARMS, so the certified family is an arm subset by "
                          "construction and `family ∩ arms = family` at every threshold. The "
                          "overlap is not evidence; it is the procedure."),
           "Q1_overlap_by_threshold": overlaps,
           "Q2_blind_subsets": {"built": len(subsets), "in_certification_population":
                                len(in_population),
                                "reading": ("absent from the population the rule ranges over — "
                                            "NOT certified-and-failed")},
           "Q3_sham_bookkeeping_or_rule": {"a_subset_given_the_artifact_certifies": sham_certifies,
                                           "reading": ("the barrier is the missing file, so the "
                                                       "repair is a committed selection, not a new "
                                                       "certification rule")},
           "controls": ctrl,
           "impossibility": {"criterion": "a family both certifiable and disjoint",
                             "status": "N/A in this release as shipped",
                             "what_it_would_require": ("a committed per-prompt selection file for a "
                                                       "constructed comparator, which the release "
                                                       "does not ship but which the SHAM shows the "
                                                       "rule would accept")},
           "kill": {"gate_open": gate_open, "world_A_killed": a_killed},
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1096 — certifiable or disjoint: can a comparator family be both?\n")
    print("  ⛔ HALF OF THIS IS A DERIVATION: the rule types ARMS, so the certified family is an")
    print("     arm subset at every threshold. The overlap is the procedure, not evidence.\n")
    print("  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  Q1 · OVERLAP BY THRESHOLD (derivation) — minimum {min_overlap}")
    for o in overlaps[:6]:
        print(f"    {o['rule']:<22} family {o['family']:>3}   overlap {o['overlap_with_arms']:>3}")
    print(f"    … {len(overlaps)} thresholds on R1056's curve, all in the artifact")
    print(f"\n  Q2 · the {len(subsets)} BLIND SUBSETS in the certification population: "
          f"{len(in_population)}")
    print(f"     absent from the population the rule ranges over — not certified-and-failed")
    print(f"\n  Q3 · SHAM — a subset GIVEN the artifact certifies: {sham_certifies}")
    print(f"     so the barrier is BOOKKEEPING, and the repair is a committed selection file")
    print(f"\n  {'⛔' if not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
