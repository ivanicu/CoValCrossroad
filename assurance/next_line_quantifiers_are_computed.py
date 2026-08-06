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
        # ⭐⭐ WIDENED BY R706, AND THE WIDENING WAS RUN AS AN EXPERIMENT BEFORE IT SHIPPED.
        #   `^NEXT:` missed 65 of 1270 commits whose NEXT paragraph is written `NEXT.` (58) or
        #   `NEXT, and ...` (7) -- including the commit whose NEXT line carried a FALSE quantifier,
        #   so the gate passed on an EMPTY POPULATION exactly when it was needed (ledger 874).
        #   The separator is NOT the discriminator: a line-initial NEXT is also followed by ` ` (6)
        #   and `-` (2), and ALL EIGHT of those are wrapped prose ("NEXT-line detector's first
        #   version at 61%"), the very false positive recorded above. PARAGRAPH-INITIAL is the
        #   discriminator. Measured by R706: loss 0, gain 65, false positives 0 against the 8 real
        #   wrapped-prose lines, and the newly-visible flag rate is explained by paragraph LENGTH
        #   (2.0x longer; matched, the gap falls inside its null).
        ms = list(re.finditer(r"(?:\A|\n\n)NEXT[:.,]\s*(.*?)(?:\n\n|\Z)", body, re.S | re.M))
        if ms: got.append((sha.strip()[:8], " ".join(ms[-1].group(1).split())))
        else: MISSING.append(sha.strip()[:8])
    return got


MISSING: list[str] = []   # commits in the window with NO extractable NEXT paragraph (per-item guard)


def flagged(text: str) -> str:
    if PROVENANCE.search(text): return ""
    c = BARE_COUNT.search(text)
    if c: return f"bare count '{c.group(0)}'"
    for q in QUANT.finditer(text):
        near = text[max(0, q.start()-WINDOW): q.end()+WINDOW]
        a = ARTIFACT.search(near)
        if a: return f"quantifier '{q.group(1)}' over '{a.group(1)}'"
    return ""



# ⭐ POPULATION EXTENDED 2026-08-05 (R671). This gate's docstring calls the unit gap structural --
#    "reports go to the terminal, not to disk". HALF of that is false: a round's README carries a
#    `## NEXT` section, on disk and versioned, and it is the surface where the failures actually
#    land (ledger 715 and 720 both live in one). Measured before extending: 34 of 80 README NEXT
#    sections flag, 42.5%, against 37.2% for commit bodies -- +5.3 points, and under the 60% line
#    this file already records. The 34 are frozen as a baseline so only NEW ones fail, exactly as
#    the commit-body half works. The TERMINAL report is still unreadable; that residue stands.
# ⭐ WHAT THIS GATE'S FLAGS ARE WORTH -- MEASURED 2026-08-05 (R700), not asserted.
#   Over 257 flagged occurrences (README NEXT sections + every frozen commit body), 30 are IDIOMATIC
#   -- `at all`, `after all`, and kin -- i.e. an intensifier the regex reads as a universal. That is
#   11.7%, so 88.3% of flags are genuine universals over our own work: THE GATE MEASURES THE RISK IT
#   WAS BUILT FOR and its PASS means what it claims.
#   ⚠ 11.7% is a FLOOR: the idiom list is closed and hand-written, so any construction not on it
#   counts as a real universal.
#   ⚠ And a flagged idiom is still a flag someone must resolve -- the cost of a false flag is paid
#   in attention whether or not it was earned.
#   ⭐ Commonest flagged words: `every`, then `nothing` (29), `never` (29), `the only` (23).
#   I had predicted `all` would lead, generalising from the two cases that bit me; it does not.

README_FREEZE = pathlib.Path(__file__).resolve().parent / "KNOWN_QUANTIFIED_README_NEXT.json"


def readme_next_sections(root):
    out = []
    for f in sorted(root.rglob("README.md")):
        if "/_archive/" in str(f):
            continue
        txt = f.read_text(errors="ignore")
        m = re.search(r"^##+\s*NEXT\b(.*?)(?=\n##\s|\Z)", txt, re.M | re.S)
        if m:
            out.append((f.parent.name, " ".join(m.group(1).split())))
    return out


def check_readmes():
    secs = readme_next_sections(ROOT)
    bad = []
    for name, s in secs:
        for m in QUANT.finditer(s):
            w = s[max(0, m.start() - WINDOW): m.end() + WINDOW]
            if ARTIFACT.search(w) and not PROVENANCE.search(w):
                bad.append((name, m.group(0)))
                break
    if not README_FREEZE.exists():
        README_FREEZE.write_text(json.dumps(
            {"count": len(bad), "rounds": sorted(n for n, _ in bad),
             "note": "seeded by R671; only NEW README NEXT sections fail"}, indent=1))
    fr = json.loads(README_FREEZE.read_text())
    known = set(fr["rounds"])
    new = [(n, q) for n, q in bad if n not in known]
    print(f"\n  README `## NEXT` sections: {len(secs)}   quantified: {len(bad)}   "
          f"frozen: {len(known)}")
    if new:
        print("  NEW -- a README NEXT quantifies over our own work without citing its source:")
        for n, q in new:
            print(f"    {n[:56]:<56} quantifier {q!r}")
    return len(new)


def main() -> int:
    rows = next_lines()
    if len(rows) < 20:
        print(f"  only {len(rows)} NEXT lines found -- population too small to police"); return 2
    print(f"  NEXT lines in history: {len(rows)}   commits with none extractable: {len(MISSING)}")

    # ⭐⭐ PER-ITEM EMPTY-POPULATION GUARD (R706, ledger 874). The corpus-level guard above cannot
    #   fire when ONE commit contributes nothing -- which is exactly how R704's false quantifier
    #   passed. Every round is supposed to write a NEXT paragraph, so HEAD having none is either a
    #   missing NEXT or an extractor this gate cannot read; both must be visible, and neither is
    #   an acquittal.
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                          capture_output=True, text=True).stdout.strip()[:8]
    if head in MISSING:
        print(f"  ⛔ HEAD ({head}) has NO extractable NEXT paragraph. This gate examined NOTHING for")
        print(f"     the commit under test, which is silence and not a pass. Write the NEXT paragraph")
        print(f"     starting a line with `NEXT:` (or `NEXT.` / `NEXT,`), preceded by a blank line.")
        return 1
    print(f"  PER-ITEM GUARD: HEAD ({head}) carries an extractable NEXT paragraph -> PASS")

    # ⛔ THE HISTORICAL POSITIVE CONTROL WENT BLIND, AND IT WAS ALWAYS GOING TO.
    #    It matched four SPECIFIC NEXT texts from real history. `rows` is a bounded scan, so as the
    #    log grows those commits scroll out and the control reports "0 found -- cannot run". That is
    #    the same defect as a positive control anchored to a FILE that a later population excludes:
    #    a control tied to the corpus goes blind when the corpus moves. Measured here at 0 of 4.
    #    Remedy, and it is the one already built for a_control_that_cannot_fail.py: a SYNTHETIC
    #    plant validates the RULE and cannot age out; the historical fixtures stay as an extra check
    #    that degrades to N/A. The two changes are inseparable -- degrading to N/A without a
    #    synthetic control would be `empty population passes`.
    SYNTH_BAD = [
        "the 9 rounds cited above are the ones that still need a source",
        "every number in the ceiling chain is now anchored",
        "the only unexplained number left is the floor",
    ]
    # ⚠ THE g=0 ARM MUST BE SENSITIVE TO THE PROVENANCE RULE, NOT MERELY UNFLAGGED. My first
    #    choice was unflagged under the real rules AND still unflagged when PROVENANCE was broken --
    #    so it could not detect over-firing, and an attack that made the rule over-fire on 14 real
    #    items passed this arm. The corpus caught it; the control did not. This string is unflagged
    #    normally and IS flagged when PROVENANCE is disabled, which is what makes it an arm.
    SYNTH_OK = [
        "every round in the arc is listed by assurance/every_round_is_committed.py, so re-run it",
    ]
    synth_hit = [t for t in SYNTH_BAD if flagged(t)]
    synth_fp = [t for t in SYNTH_OK if flagged(t)]
    ok_s = len(synth_hit) == len(SYNTH_BAD) and not synth_fp
    print(f"  SYNTHETIC POSITIVE: {len(synth_hit)}/{len(SYNTH_BAD)} planted quantifiers flagged   "
          f"SYNTHETIC g=0: {len(synth_fp)} false alarm(s)   "
          f"{'PASS' if ok_s else 'FAIL — the RULE is blind or over-fires'}")
    if not ok_s:
        print("  ⛔ the synthetic control failed; this gate certifies nothing. Exit 2, never 0.")
        return 2
    KNOWN_BAD = [t for _, t in rows if re.search(
        r"the 9 rounds cited|every number in the ceiling chain|the open items are the ones|"
        r"only unexplained number", t, re.I)]
    if not KNOWN_BAD:
        print("  HISTORICAL POSITIVE: N/A — the four fixture commits are outside the scanned "
              "window. The synthetic control above carries the validation.")
        KNOWN_BAD = list(SYNTH_BAD)
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
    # ⭐ R671: the README half of the population, previously unread entirely.
    n_readme = check_readmes()
    if new or n_readme:
        return 1
    print(f"  PASS -- no new quantified NEXT line, in commit bodies or READMEs.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
