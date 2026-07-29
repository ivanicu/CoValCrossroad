"""Every round that scores against a MODEL PROXY must say so in its own results file.

Why this exists (retraction entry 50).  r12's inversion was chased through
three rounds -- r40, r41, r46 -- each of which varied a property of the RUBRIC.
Every one of them held the outcome variable fixed, and the outcome was
agreement with a model gold head that has response length as an explicit input.
Roughly half the anomaly lived there.

Nothing in the process rules asks *is this a property of the outcome variable?*
They ask about construction data reaching evaluation, about instruments, about
populations.  The outcome had been fixed since r08 and had stopped looking like
a choice -- which is exactly when a choice becomes invisible.

So this check makes the choice visible again: a round whose CODE evaluates
against the gold head must DECLARE that in its published artifact, where a
reader meets the number.

WHAT THIS CHECK IS SOUND FOR
----------------------------
  PROPERTY   no claim silently rests on a model-scored outcome
  PROXY      run.py references the gold head AND no results string says so
  IMPLICATION  undeclared  =>  worth reading.   declared  =>  NOTHING about
               whether the declaration is accurate or prominent enough.
  SAFE SIDE  flags only.  A declaration is not a defence of the outcome.

A round that uses human rankings needs no declaration -- the released rankings
ARE the target for the original candidates.  The exposure is specifically the
rounds that CANNOT use them, because no human ranked the responses they score:
anything built on generated text.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

# Code-level signatures.  Deliberately broad: over-flagging costs a sentence,
# under-flagging costs a retraction.
USES_GOLD = re.compile(r"a08_gold|gold_orig|gold_fresh|def gold\(|--gold\b")
USES_HUMAN = re.compile(r"individual_pairs|human_pairs|ranking_blocks|parse_ranking")

# A declaration must name the proxy nature of the outcome, not merely mention
# the word "gold" in passing.
DECLARES = re.compile(
    r"model[- ]scored|model gold|gold proxy|proxy world|proxy-world|"
    r"against a model|model proxy|no human rankings|judge-relative|"
    r"not human|model-scored outcome", re.I)


def strings(doc, path=""):
    if isinstance(doc, dict):
        for k, v in doc.items():
            yield from strings(v, f"{path}.{k}" if path else k)
    elif isinstance(doc, list):
        for i, v in enumerate(doc):
            yield from strings(v, f"{path}[{i}]")
    elif isinstance(doc, str):
        yield path, doc


def _floor(n: int, what: str) -> int:
    """Refuse to report success on an empty observation (entry 63/64).

    "Nothing outstanding" and "nothing observed" are different states, and every
    check in this package returned 0 for both. A check whose population is empty
    has measured nothing; that is exit 2, distinct from pass (0) and fail (1).
    """
    if n == 0:
        print(f"\nOBSERVED NOTHING: {what} is empty. This is exit 2, not success -- "
              f"a check with no population has not passed, it has not run.")
        return 2
    return 0

def main() -> int:
    rows, flagged = [], []
    for d in sorted(_ROOT.glob("rounds/*/")):
        run = d / "run.py"
        if not run.exists():
            continue
        src = run.read_text()
        gold = bool(USES_GOLD.search(src))
        human = bool(USES_HUMAN.search(src))
        if not gold:
            continue
        results = [f for f in d.glob("results/**/*.json")
                   if "SMOKE" not in f.name and "_smoke_archive" not in f.parts]
        declared, where = False, None
        for f in results:
            try:
                doc = json.loads(f.read_text())
            except json.JSONDecodeError:
                continue
            for jp, text in strings(doc):
                if DECLARES.search(text):
                    declared, where = True, f"{f.name}:{jp}"
                    break
            if declared:
                break
        rows.append((d.name, gold, human, declared, where, len(results)))
        if not declared:
            flagged.append((d.name, len(results)))

    print(f"rounds evaluating against the gold head: {len(rows)}")
    for name, _g, human, declared, where, nres in rows:
        tag = "declared" if declared else "UNDECLARED"
        extra = f"  <- {where}" if where else (
            "  (no results files)" if nres == 0 else "")
        print(f"  {name:34s} human_rankings={'yes' if human else 'NO ':3s} {tag}{extra}")

    floor = _floor(len(rows), "the set of rounds evaluating against the gold head")
    if floor:
        return floor
    if not flagged:
        print("\nEvery gold-scored round declares its outcome.")
        print("  This says nothing about whether those declarations are ACCURATE or "
              "prominent enough -- the check flags silence, not spin.")
        return 0
    print(f"\n{len(flagged)} round(s) score against a model proxy without saying so:")
    for name, nres in flagged:
        print(f"  {name}   ({nres} results file(s))")
    print("\nAdd a scope string naming the outcome as model-scored. Entry 50 is what "
          "happens when a reader meets the number without it.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
