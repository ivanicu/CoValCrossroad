#!/usr/bin/env python3
"""
R642 -- the restore destroyed its own subject, and "strictly more general" was not better

TWO FINDINGS, BOTH FROM RUNNING THE REPAIR RATHER THAN REASONING ABOUT IT.

① THE PROHIBITION WORKS, AND ITS EFFECT IS A MEASUREMENT: byte-identical reproductions went
  38 -> 43 across the same 43 rounds. The five the harness had called "failures" all exit 1 as a
  DECLARED VERDICT, so under the prohibition they count as ran. 12 verdict-bearing changes and
  the world-B substance are unchanged, exactly as pre-registered.

② AND THE ROUND'S OWN NEGATIVE CONTROL REVERTED THE REPAIR, MID-RUN. `git checkout -- <A24>` is
  scoped to a directory that CONTAINS THIS HARNESS. It restored run.py along with the artifacts,
  wiping the prohibition; the tree then differed from its recorded pre-state and the control
  failed. Verified after the fact: the PROHIBITION token count on disk was 0.
  ⭐ A CLEANUP SCOPED TO A DIRECTORY THAT CONTAINS THE INSTRUMENT WILL REVERT THE INSTRUMENT.
  Seventh self-contamination in this arc, and a new vector: not the artifact in its population,
  not the operator on the population, not the instrument matching itself -- the instrument's
  CLEANUP destroying the instrument's MODIFICATION.
  Repaired: the restore now walks each round's results/ and never touches source.

③ AND THE "BETTER PREDICATE" FROM THE PREVIOUS TURN IS RETRACTED. I proposed replacing the
  keyword list with "non-zero exit + non-empty stderr = crash", called it strictly more general,
  and bounded its failure population at "<= 1 of 317". That bound was doing the opposite work I
  read it as doing: it did not mean ALMOST SAFE, it meant THERE IS EXACTLY ONE CANDIDATE, GO LOOK.
  One grep: R576 writes JSON to stderr as an IPC channel AND calls sys.exit(2). The one case is
  REAL. The stderr rule misreads it as a crash; the keyword list gets it right.
  ⭐ STRICTLY MORE GENERAL IS NOT BETTER -- generality bought coverage of hypothetical crash types
  at the price of the corpus's one actual verdict, and neither rule dominates.

VERDICT: the run is UNVERIFIED, because a failed negative control is not overridden by a passing
positive one. What is established is ① as a measurement and ② as a diagnosed cause with a repair.

IMPOSSIBLE, unchanged: no rule can decode the 18 semantics of `EXIT 1` (R638). Only the
deliberate-vs-crash distinction is available, and it is operational rather than semantic.
"""
import json, pathlib, sys
p = pathlib.Path(__file__).resolve().parent / "results" / "restore_destroyed_its_subject.json"
print(json.dumps(json.loads(p.read_text()), indent=2) if p.exists() else "artifact missing")
sys.exit(0)
