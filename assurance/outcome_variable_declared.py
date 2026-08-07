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
import ast as _ast
import io as _io
import tokenize as _tokenize


def _masked_spans(src: str):
    """byte spans of every string literal and every comment -- where a token is MENTIONED."""
    spans, offs, t = [], [0], 0
    for l in src.splitlines(keepends=True):
        t += len(l)
        offs.append(t)

    def off(row, col):
        return offs[row - 1] + col

    # ⛔ R971: MASK DOCSTRINGS AND COMMENTS ONLY -- NOT every string literal.
    #    R970 masked all of them, which made `np.load("a08_gold_08b.npz")` read as a MENTION: the
    #    filename IS a string, so the commonest real USE of the gold head became invisible. That is
    #    a false negative in the direction this gate exists to prevent, and the attack's vector 1
    #    caught it within one round.
    #    ⚠ AND R943's POSITIVE CONTROL COULD NOT HAVE CAUGHT IT. Its plant was
    #    `gold_orig = np.load("a08_gold_08b.npz")`, which matches on the VARIABLE NAME sitting
    #    outside the string -- it avoided the blind spot by accident instead of probing it, and so
    #    certified a filter that is blind to the plain form.
    #    A string used as a VALUE is data the round consumes. Only a bare string statement (a
    #    docstring) and a comment are prose. The cost is that an assigned payload string now flags,
    #    which is the deliberate direction: over-flagging costs a sentence, under-flagging a
    #    retraction.
    tree = _ast.parse(src)
    docstrings = set()
    # ⛔ `getattr(n, "body")` is a LIST on Module/FunctionDef/ClassDef but an EXPRESSION on IfExp
    #    and Lambda, so the first version raised `TypeError: 'Constant' object is not iterable` on
    #    the real corpus. My five snippets contained no such node and all passed -- a control
    #    validated against cases I invented, for the third time this session. Iterate only lists.
    for n in _ast.walk(tree):
        body = getattr(n, "body", None)
        if not isinstance(body, list):
            continue
        for child in body:
            if (isinstance(child, _ast.Expr) and isinstance(child.value, _ast.Constant)
                    and isinstance(child.value.value, str)):
                docstrings.add(id(child.value))
    # ⭐ R972: two CALL SITES join docstrings and comments as prose, measured from the object
    #    rather than guessed. The three rounds R971 left flagged carry their token in
    #    `re.compile('a08_gold_08b')`, `re.compile('a08_gold|gold_orig|...')` and `print(...)`.
    #    A regex naming the gold head DESCRIBES it; a print REPORTS it; neither LOADS it. The
    #    exception list stays short and each entry is justified by what the call does -- and
    #    `np.load(filename)` is deliberately NOT on it, so R971's true positive survives.
    DESCRIBES = {"re.compile", "print"}
    prose_args = set()
    for n in _ast.walk(tree):
        if isinstance(n, _ast.Call):
            try:
                fn = _ast.unparse(n.func)
            except Exception:
                continue
            if fn in DESCRIBES:
                for a in list(n.args) + [k.value for k in n.keywords]:
                    if isinstance(a, _ast.Constant) and isinstance(a.value, str):
                        prose_args.add(id(a))
    for n in _ast.walk(tree):
        if (isinstance(n, _ast.Constant) and isinstance(n.value, str) and n.end_lineno
                and (id(n) in docstrings or id(n) in prose_args)):
            spans.append((off(n.lineno, n.col_offset), off(n.end_lineno, n.end_col_offset)))
    try:
        for tok in _tokenize.generate_tokens(_io.StringIO(src).readline):
            if tok.type == _tokenize.COMMENT:
                spans.append((off(tok.start[0], tok.start[1]), off(tok.end[0], tok.end[1])))
    except (_tokenize.TokenError, IndentationError):
        pass
    return spans


def uses_outside_prose(src: str, rx) -> bool:
    """⭐ R970. `USES_GOLD` is a SOURCE-TEXT regex, so it could not tell a USE from a MENTION and
    every live flag this gate carried was a false positive: R422 matches only inside its docstring,
    R425 inside a `re.compile` literal, and R942/R945 carry the tokens as TEST PAYLOADS and a
    transcribed regex. R943 measured that -- 3 gold USERS against 11 MENTION-only rounds -- and built
    this classifier with planted controls in BOTH directions (a module-level `np.load` must read as
    USE; a docstring/comment/string-only occurrence must read as MENTION).

    ⛔ WHY THE ROUNDS WERE NOT 'FIXED' INSTEAD: adding a scope string to a round that does not score
    against a proxy is a FALSE DECLARATION, which is worse than the flag it silences. The instrument
    was wrong, so the instrument is what changed.

    A file that will not parse fails CLOSED -- treated as a use -- because an unreadable round is not
    an acquitted one."""
    if not rx.search(src):
        return False
    try:
        spans = _masked_spans(src)
    except SyntaxError:
        return True
    return any(not any(a <= m.start() < b for a, b in spans) for m in rx.finditer(src))


import json
import re
import sys
from pathlib import Path

# A provisional run is not a result. Matching one WORD failed twice: once on
# case (a04_smoke.json, entry 71) and once on vocabulary (a06_dryrun.json,
# entry 75). Match the class, and prefer the results/_smoke/ directory rule,
# which does not depend on the name at all.
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip",
                         re.I)

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

def main(only: str | None = None) -> int:
    """⭐ R973: `only` restricts the scan to ONE round directory.

    Its attack planted a fixture and then read this gate's WHOLE-REPO exit code, so every vector's
    verdict moved with the corpus rather than with the plant: R942 measured the channel saturated at
    1 by four false positives, and R970 saw it flip when those were removed. A harness whose claim is
    per-round must read a per-round verdict. Same repair as R954's `main(path, floor)`.
    """
    rows, flagged = [], []
    for d in sorted(_ROOT.glob("E*/A*/R*/")):
        if only and d.name != only:
            continue
        run = d / "run.py"
        if not run.exists():
            continue
        src = run.read_text()
        gold = uses_outside_prose(src, USES_GOLD)
        human = bool(USES_HUMAN.search(src))
        if not gold:
            continue
        results = [f for f in d.glob("results/**/*.json")
                   if not PROVISIONAL.search(f.name) and "_smoke_archive" not in f.parts]
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
