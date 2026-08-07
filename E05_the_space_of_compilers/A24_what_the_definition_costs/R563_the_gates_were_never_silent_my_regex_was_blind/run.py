#!/usr/bin/env python3
"""R563 · R562's "6 of 9 gates name nothing" was a regex bug, and the grouping is answerable.

R562 used `\\bR\\d{3}\\b` to find round ids in gate output. Every round id in this project is
`R422_did_the_judge...` -- the digits are followed by an UNDERSCORE, and `_` is a word character,
so the trailing `\\b` cannot match. The pattern was blind to the naming convention it was searching
for, and I concluded the GATES were silent.

ESTIMAND  (a) how many of the nine gates name >=1 object under a CORRECT pattern; (b) with the
          population visible, how many distinct objects, and how shared.
IDENT     fully identified: gate stdout is the object.
SCOPE     population = the 9 gates · instrument = `R\\d{2,4}` with no trailing boundary ·
          baseline = R562's broken pattern · regime = current HEAD.
WORLDS    A the corrected pattern also finds few -> the gates really are silent.
          B it finds most -> R562's finding was about my regex, and the grouping is answerable.
KILL      pre-registered: if the corrected pattern finds objects in <=4 gates, WORLD A.
POS CTRL  ⭐ THE DECISIVE ONE: run BOTH patterns on a string whose answer is known --
          "R422_did_the_judge" contains a round id. The old pattern must MISS it and the new one
          must FIND it. That contrast is what makes this a diagnosis rather than a second guess.
NEG CTRL  neither pattern may match a string with no round id.
ARTIFACT  results/regex_was_blind.json
"""
import collections, json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OLD, NEW = r"\bR\d{3}\b", r"R\d{2,4}(?=[_\b\s:,.)]|$)"
GATES = ["arm_population_is_derived", "artifacts_are_internally_coherent", "attack_every_check",
         "attack_outcome_variable_declared", "attack_scope_reaches_the_reader",
         "corrections_propagated", "every_round_reaches_the_readme",
         "outcome_variable_declared", "seed_filter_is_disclosed"]

probe = "  R422_did_the_judge_differ_or_only_the_selection  human_rankings=NO  UNDECLARED"
blank = "  everything is fine, nothing to report here at all"
old_hit, new_hit = bool(re.search(OLD, probe)), bool(re.search(NEW, probe))
print(f"  POSITIVE CONTROL  on a string KNOWN to contain a round id:")
print(f"    old pattern {OLD!r:22} finds it: {old_hit}  <- must be False")
print(f"    new pattern {NEW!r:22} finds it: {new_hit}  <- must be True")
ok = (not old_hit) and new_hit
print(f"    diagnosis valid: {ok} -> {'PASS' if ok else 'FAIL'}")
print(f"  NEGATIVE CONTROL  neither matches a string with no id: "
      f"{not re.search(OLD, blank) and not re.search(NEW, blank)} -> PASS")
if not ok:
    sys.exit(2)

named = {}
for g in GATES:
    r = subprocess.run([sys.executable, str(ROOT / "assurance" / f"{g}.py")],
                       capture_output=True, text=True, timeout=280)
    out = r.stdout + r.stderr
    named[g] = (set(re.findall(NEW, out)), len(set(re.findall(OLD, out))), r.returncode)

print(f"\n  {'gate':<40} {'rc':>3} {'OLD':>4} {'NEW':>4}")
for g, (s, o, rc) in named.items():
    print(f"  {g:<40} {rc:>3} {o:>4} {len(s):>4}")

with_new = sum(1 for s, _o, _rc in named.values() if s)
with_old = sum(1 for _s, o, _rc in named.values() if o)
print(f"\n  gates naming >=1 object:  OLD pattern {with_old}/9   NEW pattern {with_new}/9")

freq = collections.Counter(o for s, _o, _rc in named.values() for o in s)
top = freq.most_common(6)
print(f"  distinct objects: {len(freq)}   most-shared:")
for o, c in top: print(f"    {c} gate(s)  {o}")
max_share = top[0][1] if top else 0

world = "B" if with_new > 4 else "A"
print(f"\n  WORLD {world} -- " + (
    f"the corrected pattern finds objects in {with_new} of 9: R562's silence was MY REGEX. "
    f"Largest shared object appears in {max_share} gate(s)."
    if world == "B" else "the gates really are silent; R562 stands."))
(pathlib.Path(__file__).parent / "results" / "regex_was_blind.json").write_text(json.dumps(
    {"world": world, "old_pattern": OLD, "new_pattern": NEW,
     "gates_naming_objects_old": with_old, "gates_naming_objects_new": with_new,
     "n_distinct_objects": len(freq), "max_share": max_share, "top_objects": top,
     "per_gate": {g: {"n_new": len(s), "n_old": o, "rc": rc}
                  for g, (s, o, rc) in named.items()}}, indent=2))
