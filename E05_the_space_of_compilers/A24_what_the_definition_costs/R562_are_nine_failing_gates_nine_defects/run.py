#!/usr/bin/env python3
"""R562 · Are the nine failing gates nine defects, or one defect seen from nine angles?

ESTIMAND  the number of DISTINCT objects named by the nine failing gates, and the overlap
          structure between them.
IDENT     fully identified: each gate prints the rounds/files it flags; the union and the
          pairwise intersections are counts over those sets.
SCOPE     population = the 9 gates R561 classified as real live debt · instrument = each gate's
          own stdout · baseline = 9 disjoint sets (nine defects) · regime = current HEAD.
WORLDS    A nine disjoint object sets -> nine defects, and each needs its own round.
          B heavy overlap -> one defect seen from nine angles, and one fix clears most of them.
KILL      pre-registered: if the largest shared object appears in <=2 gates, WORLD A.
POS CTRL  each gate must name at least one concrete object (an R-id or a path). A gate naming
          nothing cannot be grouped, and counting it as 'disjoint' would manufacture WORLD A.
NEG CTRL  an invented R-id must appear in no gate's output.
ARTIFACT  results/nine_or_one.json
"""
import collections, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
GATES = ["arm_population_is_derived", "artifacts_are_internally_coherent", "attack_every_check",
         "attack_outcome_variable_declared", "attack_scope_reaches_the_reader",
         "corrections_propagated", "every_round_reaches_the_readme",
         "outcome_variable_declared", "seed_filter_is_disclosed"]

named, empty = {}, []
for g in GATES:
    r = subprocess.run([sys.executable, str(ROOT / "assurance" / f"{g}.py")],
                       capture_output=True, text=True, timeout=280)
    out = r.stdout + r.stderr
    ids = set(re.findall(r"\bR\d{3}\b", out)) | set(re.findall(r"\b[a-z_]+\.py\b", out))
    ids -= {f"{g}.py"}
    named[g] = ids
    if not ids: empty.append(g)
    print(f"  {g:<40} rc={r.returncode}  names {len(ids)} object(s)")

print(f"\n  POSITIVE CONTROL  every gate names >=1 concrete object: {not empty} -> "
      f"{'PASS' if not empty else 'PARTIAL — ' + str(empty)}")
fake = any("R999" in s for s in map(str, named.values()))
print(f"  NEGATIVE CONTROL  an invented R-id appears nowhere: {not fake} -> "
      f"{'PASS' if not fake else 'FAIL'}")

groupable = {g: s for g, s in named.items() if s}
if len(groupable) < 3:
    print("  too few groupable gates -> UNRUNNABLE"); sys.exit(2)

freq = collections.Counter(o for s in groupable.values() for o in s)
top = freq.most_common(8)
union = set(freq)
print(f"\n  gates groupable: {len(groupable)} of {len(GATES)}   distinct objects named: {len(union)}")
print(f"  most-shared objects:")
for o, c in top:
    print(f"    {c} gate(s)  {o}")

max_share = top[0][1] if top else 0
# ⛔ THE FIRST VERSION BRANCHED ONLY ON max_share AND PRINTED "WORLD A -- nine defects" while the
# positive control had just reported that 6 of 9 gates name NO object. A verdict computed over a
# third of the population, with the control's own words on screen above it. §4's verdict-string
# failure, in the round about reading failures properly.
# The branch now references EVERY control the round declared.
control_ok = not empty
if not control_ok:
    world = "UNVERIFIED"
elif max_share > 2:
    world = "B"
else:
    world = "A"
print(f"\n  largest shared object appears in {max_share} gate(s)   [KILL at <=2 -> WORLD A]")
if world == "UNVERIFIED":
    print(f"  ⛔ VERDICT: UNVERIFIED -- {len(empty)} of {len(GATES)} gates name no object, so the "
          f"grouping saw {len(groupable)}/{len(GATES)} of the population.")
    print(f"     A disjointness verdict over a third of the population is not a measurement.")
    print(f"     What is needed: the six silent gates must be made to NAME what they flag.")
elif world == "B":
    print(f"  WORLD B -- one object is flagged by {max_share} of the nine: angles on a smaller "
          f"defect set.")
else:
    print(f"  WORLD A -- object sets disjoint across ALL {len(GATES)} gates: nine defects.")
(pathlib.Path(__file__).parent / "results" / "nine_or_one.json").write_text(json.dumps(
    {"world": world, "n_gates": len(GATES), "n_groupable": len(groupable),
     "gates_naming_nothing": empty, "n_distinct_objects": len(union),
     "max_share": max_share, "top_objects": top,
     "per_gate_counts": {g: len(s) for g, s in named.items()}}, indent=2))
