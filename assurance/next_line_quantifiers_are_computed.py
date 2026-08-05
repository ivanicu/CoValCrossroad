"""The NEXT line is where nine claims went wrong in one session. This makes that failure failable.

WHY. The standard names the closing sentence as the highest-risk line in a report: written last,
acted on by a later round, the only one with no control attached. This session produced NINE false
ones — "9 rounds" (54–74), "289 retractions" (326), "the only unexplained number", "no longer
empirical", "nothing in the residue recommends", "every number is accounted for", "the open items are
the ones the residue names", and two walls that one command falsified. Each was caught by hand. Nine
is well past the point where a habit should have become an instrument.

⛔ WHAT THIS GATE CANNOT DO, STATED FIRST. Reports go to the terminal, not to disk, so no gate can
read them. What IS durable is the `NEXT:` paragraph of every commit body — the same sentence, written
at the same moment, for the same purpose. That is the population this gate polices, and the claim's
unit ("the closing sentence of a report") and the instrument's unit ("the NEXT paragraph of a commit
body") are NOT identical. They are the same sentence in two places; a report whose NEXT line differs
from its commit's is outside this gate, and that gap is named rather than papered over.

THE RULE. A NEXT line may not contain a bare quantifier over the project's own work. Either drop it,
or state where the number was computed. "the 9 rounds cited in DEFINITION.md" fails; "the rounds
cited in DEFINITION.md but not STATEMENT.md (run assurance/residue_debt.py)" passes.

⚠ THIS IS A SEARCH, SO IT CARRIES A POSITIVE CONTROL BUILT FROM REAL HISTORY, NOT FROM IMAGINATION.
Four commit bodies in this repository are KNOWN to contain a false quantified NEXT line; the detector
must flag all four. And a NEXT line known to be clean must not be flagged. A control validated only
against cases I invented is validated against my imagination — the standard's own words.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FREEZE = pathlib.Path(__file__).resolve().parent/"KNOWN_QUANTIFIED_NEXT.json"

# Quantifiers over one's own work. Deliberately NOT a general "vague words" list: the failure mode is
# specifically counting or bounding the project's own artifacts.
# ⚠ A FIRST VERSION MATCHED THE WORD AND NOT THE FAILURE, AND FLAGGED 217 OF 357 NEXT LINES — 61%.
# That is the "a search is an instrument" signature: a pattern matching most of a corpus is matching
# ordinary language. The failure is not "uses the word every"; it is "asserts a count or a
# completeness OVER THE PROJECT'S OWN ARTIFACTS". A quantifier therefore only counts when an ARTIFACT
# NOUN sits within a short window of it — the instrument's unit and the claim's unit made equal
# BEFORE the control was designed, which is what the standard asks and what I had not done.
# ⭐ WIDENED 2026-08-05 (R670), MEASURED BEFORE APPLYING as this file's own comments require.
#    Positive control from REAL history: ledger 715 ("the LAST structural question this definition
#    has left") and 723 ("the FIRST claim in this arc that would add a clause") were both MISSED --
#    `the last` and `the first` were absent from the pattern entirely. The gate was GREEN through
#    both. Cost, measured over 371 real NEXT paragraphs: base rate 32.1% -> 37.2%, +5.1 points,
#    far under the 60% "matching ordinary language" line this file already records.
#    ⚠ Ledger 725 ("something disqualifies k=12 categorically") is NOT added: it is a categorical
#      claim about an OBJECT, with no self-reference, and the window rule correctly declines it.
#      That mis-filing was caught by this gate's own control, not by me.
QUANT = re.compile(r"\b(every|all|none|nothing|no other|the only|only remaining|last remaining|"
                   r"never|always|fully|entirely|completely|exhaustive|the last|the first|"
                   r"the sole|nothing else|no more)\b", re.I)
ARTIFACT = re.compile(r"\b(rounds?|retractions?|entries|claims?|arms?|gates?|cells?|items?|"
                      r"numbers?|documents?|residue|DEFINITION\.md|STATEMENT\.md|ledger|chain|"
                      # ⚠ WIDENED after the gate FALSE-NEGATIVED on its own introducing commit's
                      # NEXT line -- "nothing checks that they agree" quantifies over our own work,
                      # but `gate`/`report`/`check` were not artifact nouns. MEASURED before
                      # applying: the widening moves the base rate 35% -> 37% and buys that case.
                      # Two points of precision for one known miss, decided by measurement rather
                      # than by taste, with both numbers reported.
                      r"reports?|checks?|sentences?)\b", re.I)
WINDOW = 60
BARE_COUNT = re.compile(r"\b(\d+)\s+(rounds?|retractions?|entries|claims?|arms?|gates?|cells?|items?)\b", re.I)
# A citation of WHERE the number came from discharges the quantifier.
PROVENANCE = re.compile(r"(assurance/\w+\.py|run\s+\w+\.py|computed by|measured in R\d{3}|see R\d{3})", re.I)


def next_lines(n: int = 400):
    out = subprocess.run(["git", "log", f"-{n}", "--format=%H%x1f%B%x1e"],
                         cwd=ROOT, capture_output=True, text=True, timeout=120).stdout
    got = []
    for rec in out.split("\x1e"):
        if "\x1f" not in rec: continue
        sha, body = rec.split("\x1f", 1)
        # ⚠ THE EXTRACTOR WAS WRONG AND ITS OWN GATE CAUGHT IT. The first version matched
        # `^NEXT[:\s]`, which fires on ANY line beginning with the four letters NEXT — including a
        # WRAPPED line of ordinary prose, e.g. "...four\nNEXT lines cite where their number came
        # from". Pointed at the commit that introduced this file, it extracted the middle of the
        # controls paragraph and flagged a REPORTED MEASUREMENT as an unverified quantifier.
        # The extractor's unit was "a line starting with NEXT"; the claim's unit is "the NEXT:
        # paragraph". Not equal — the same mismatch this gate exists to police, inside the gate.
        # Fixed two ways: the colon is REQUIRED, and the LAST such paragraph wins, since the NEXT
        # line is by convention the final one.
        ms = list(re.finditer(r"^NEXT:\s*(.*?)(?:\n\n|\Z)", body, re.S | re.M))
        if ms: got.append((sha.strip()[:8], " ".join(ms[-1].group(1).split())))
    return got


def flagged(text: str) -> str:
    if PROVENANCE.search(text): return ""
    c = BARE_COUNT.search(text)
    if c: return f"bare count '{c.group(0)}'"
    for q in QUANT.finditer(text):
        near = text[max(0, q.start()-WINDOW): q.end()+WINDOW]
        a = ARTIFACT.search(near)
        if a: return f"quantifier '{q.group(1)}' over '{a.group(1)}'"
    return ""


def main() -> int:
    rows = next_lines()
    if len(rows) < 20:
        print(f"  only {len(rows)} NEXT lines found -- population too small to police"); return 2
    print(f"  NEXT lines in history: {len(rows)}")

    # POSITIVE CONTROL, from real history: these four commits carry a NEXT line this session
    # proved false. The detector must flag every one.
    KNOWN_BAD = [t for _, t in rows if re.search(
        r"the 9 rounds cited|every number in the ceiling chain|the open items are the ones|"
        r"only unexplained number", t, re.I)]
    hit = [t for t in KNOWN_BAD if flagged(t)]
    print(f"  POSITIVE CONTROL: known-false NEXT lines found in history: {len(KNOWN_BAD)}"
          f"   flagged by the detector: {len(hit)}"
          f"  -> {'PASS' if KNOWN_BAD and len(hit) == len(KNOWN_BAD) else 'FAIL'}")
    if not KNOWN_BAD:
        print("  the known-bad cases are not in the searched history -- the control cannot run"); return 2
    if len(hit) != len(KNOWN_BAD):
        for t in KNOWN_BAD:
            if not flagged(t): print(f"    MISSED: {t[:110]}")
        print("  the detector cannot see cases known to have occurred -- counts are silence"); return 1

    # NEGATIVE CONTROL: a NEXT line that cites where its number came from must NOT be flagged.
    neg = [t for _, t in rows if PROVENANCE.search(t)]
    neg_ok = all(not flagged(t) for t in neg)
    print(f"  NEGATIVE CONTROL: NEXT lines citing their source: {len(neg)}"
          f"   wrongly flagged: {sum(1 for t in neg if flagged(t))}  -> {'PASS' if neg_ok else 'FAIL'}")
    if not neg_ok: return 1

    cur = {sha: why for sha, t in rows if (why := flagged(t))}
    if not FREEZE.exists():
        FREEZE.write_text(json.dumps({"count": len(cur), "shas": sorted(cur)}, indent=1))
        print(f"  froze {len(cur)} existing quantified NEXT lines"); return 0
    fr = json.loads(FREEZE.read_text()); known = set(fr["shas"])
    if fr.get("count") != len(known):
        print(f"  freeze file self-inconsistent: {fr.get('count')} vs {len(known)}"); return 1

    new = sorted(set(cur) - known)
    print(f"\n  quantified NEXT lines: {len(cur)}   frozen: {len(known)}")
    if new:
        print(f"\n  NEW -- a NEXT line quantifies over our own work without saying where the number")
        print(f"  came from. Drop the quantifier, or cite the instrument that computed it:")
        for sha in new: print(f"    {sha}  {cur[sha]}")
        return 1
    print(f"  PASS -- no new quantified NEXT line. Known gaps still open, as documented.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
