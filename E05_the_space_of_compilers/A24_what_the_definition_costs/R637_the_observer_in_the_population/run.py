#!/usr/bin/env python3
"""
R637 -- the observer in the population: three ways I measured myself instead of the object

This round has no new computation of its own. It RECORDS a verification and three findings that
were produced read-only while R636's clean re-run executed, and it exists because the artifact is
the only durable carrier -- the run itself was R636's, re-executed under the operator-clean
condition R636's own negative control demanded.

WHAT WAS VERIFIED. R636 re-run with nothing touching the repository:
  ran 38 · failed 5 · wall clock 288s · byte-identical 38 · verdict-bearing changes 12
  POSITIVE PASS · NEGATIVE PASS · PLACEBO PASS -> VERDICT B SOME MOVE
The first pass reported the same 12 changes but with the NEGATIVE control failing, because I had
staged and unstaged files while it measured the repository. So R636's verdict moves from
UNVERIFIED to B, and check #237's exclusion -- "the operator rather than the code" -- is SUPPORTED
rather than assumed: with the operator still, the code restores correctly.

THE THREE FINDINGS, all read-only, all about the observer rather than the object:

  ① EXIT 1 IS A VERDICT, NOT A CRASH. R636 reported "ran 38 · failed 5". Four of the five declare
    an exit convention in their own docstrings -- R433 `EXIT 1 = W-LOSES`, R437 `W-INVERT`,
    R441 `W-DECORATION`, R442 `W-INSTANCE`. Only R431 shows none. Corrected: 42 ran, at most 1
    failed. An exit code is not a success signal when the program defines it as a verdict, and
    15 of the 43 rounds encode their world that way.

  ② WORLD C CAN FIRE ON NOTHING. DERIVATION, not a measurement: 15 verdict-encoding rounds vs a
    `>=1/3` threshold of 14.33 rounds; 15 >= 14.33. If every verdict-encoding round returned a
    non-zero VERDICT, the harness would count 15 "failures" and declare the corpus unreproducible
    while it ran perfectly -- by two thirds of a round. The mirror of a check that cannot fail is
    a WORLD THAT CAN FIRE WITHOUT ITS STATED CONDITION EVER OBTAINING.

  ③ A WAIT-LOOP WHOSE PREDICATE MATCHES ITS OWN COMMAND LINE NEVER TERMINATES.
    `until ! pgrep -f "R636_.../run.py"; do sleep 5; done` -- the shell running that loop has the
    pattern in its own argv, so pgrep always finds it. It was waiting for itself to disappear.
    Sixth self-contamination in this arc and the purest: not the round's artifact inside its
    population, not the operator acting on the population, but THE INSTRUMENT MATCHING ITSELF.

  ⚠ AND ③ IS WHY EVERY TIMING CLAIM THIS TURN WAS WRONG. I reported "~10 minutes", then ">750s",
    then "2x slower than the first pass". Measured: 288s against 284s -- the runs are the same
    speed. All three numbers were the elapsed time of my own waiting process. THREE WRONG
    ELAPSED-TIME CLAIMS FROM ONE ROOT, in the turn whose subject is measuring instead of assuming.

IMPOSSIBLE, unchanged: determinism of output says nothing about CORRECTNESS of output. Twelve
conclusions moved; that they moved is now a verdict, that any of them is now RIGHT is not.
"""
import json, pathlib, sys
p = pathlib.Path(__file__).resolve().parent / "results" / "observer_in_the_population.json"
print(json.dumps(json.loads(p.read_text()), indent=2) if p.exists() else "artifact missing")
sys.exit(0)
