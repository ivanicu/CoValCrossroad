"""Scan every round's GENERATED conclusion strings for withdrawn framings.

Why this exists.  Rounds build their verdicts at run time.  When a framing is
withdrawn, editing README.md and assurance/manifest.py leaves every results
JSON still asserting it, and the next run re-emits the withdrawn sentence into
the artifact -- which is the file an outsider opens.  That happened twice: the
"values %" framing, and then r35's "does not depend on forcing" plus r37's
"nor country-conditional", both re-emitted an hour after item 1 rescoped the
prose.

WHAT THIS CHECK IS SOUND FOR -- read this before trusting a PASS
----------------------------------------------------------------
  PROPERTY   no withdrawn framing is ASSERTED anywhere in the package
  PROXY      no withdrawn PHRASE occurs in a results JSON's conclusion field
  IMPLICATION  phrase present  =>  worth reading.   phrase absent  =>  NOTHING.
  WITNESS    a verdict saying "the advantage is largely non-value generic
             quality" asserts the withdrawn framing without any listed phrase
  SAFE SIDE  this check can FLAG.  It can never CLEAR.

So a clean run is reported as NO LISTED PHRASE FOUND, never as "no withdrawn
framing present".  You cannot grep for an absence, and a word list cannot prove
presence either.

ATTACKED, and the holes that remain
-----------------------------------
`assurance/attack_no_withdrawn_framings.py` plants five withdrawn framings a
real round could plausibly emit.  The first version of this checker caught 2/5:
it whitelisted five field names (missed a claim under "interpretation"), only
looked at a claim field when that field was a string (missed a list-valued
verdict), and used a flat glob (missed a results file one directory deeper).
All three are fixed and it now catches 5/5.

Known holes NOT closed, stated because an unstated hole is a false acquittal:
  * NON-JSON artifacts under results/ are not scanned at all.  There is 1
    today (r19's console.txt).  A conclusion written there is invisible here.
  * SYNONYM assertions are invisible by construction -- "the fraction that is
    genuinely about values" carries the withdrawn framing with none of the
    listed phrases.  No word list can fix that; it is why the check flags and
    never clears.

The population is deliberately narrow: generated strings in
results/**/*.json.  Prose files legitimately DISCUSS withdrawn framings in order
to withdraw them -- README says "launders is withdrawn as a description", and a
checker that cannot tell assertion from mention would either flag that forever
or be taught to ignore the very sentences it exists to police.  Prose is
governed by review, not by this.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

# EVERY string value is scanned, not a whitelist of field names.
#
# The first version whitelisted {verdict, conclusion, summary, headline,
# finding}, and an attack planted the same claim under "interpretation" and
# walked straight past.  A whitelist encodes the field names I happened to
# think of, which is a fact about me, not about where a conclusion can live.
# Scanning everything raises the flag rate, and flagging is this check's SOUND
# direction -- it can flag, it can never clear -- so the extra flags are paid
# for by an explicit, reasoned allowlist below rather than by narrowing what is
# looked at.
# PAYLOAD FIELDS -- quoted data, not claims this repository makes.
#
# Widening the scan to every string was right (a field whitelist had missed real
# cases), but results files also carry MODEL OUTPUT and DATASET TEXT, and a
# generated response that happens to discuss "money laundering" is not this
# repository asserting anything.  That fired on r46's saved generations.
#
# Re-adding a claim-field whitelist would restore the hole the widening closed.
# So instead: an enumerated list of PAYLOAD paths, each with a reason, PRINTED
# on every run.  This is bounded leniency -- the exclusions are visible, finite
# and justified, rather than a silent narrowing of what gets looked at.
#
# THE GAP THIS LEAVES, stated because an unstated gap is a false acquittal: a
# claim written INSIDE one of these paths is invisible to this check.  The
# attack suite has a vector for exactly that, and it is recorded as a KNOWN
# ACCEPTED GAP rather than as a pass.
PAYLOAD = [
    (r"generations\.json$", ("original", "fresh"),
     "verbatim model output and released response text"),
    (r"r45_frozen_frame\.json$", ("prompts",),
     "the frozen human-experiment payload: prompt and response text plus hashes"),
    (r"_receipt\.json$", ("criteria",),
     "verbatim CoVal criterion text, quoted from the release"),
]


def payload_rule(relpath: str, jpath: str):
    """Return the matching payload rule, or None."""
    for rx, roots, why in PAYLOAD:
        if re.search(rx, relpath) and jpath.split(".")[0].split("[")[0] in roots:
            return (rx, roots, why)
    return None

# (regex, what was withdrawn and what replaced it)
WITHDRAWN = [
    (r"\bmeasures?\s+values\b",
     "the values%/non-values framing -- the contrast is own-rubric vs "
     "reference-rubric performance, never values vs non-values"),
    (r"\bvalue[-_ ]carrying share\b",
     "same; use 'source specificity' or incremental prompt-conditioned information"),
    (r"\bnot\s+(?:same-sample\s+)?leakage\b",
     "-> NOT PRIMARILY SAME-RATER circularity; shared-menu endogeneity is untouched"),
    (r"\bdoes not depend on forcing\b",
     "-> ROBUST TO POST-HOC CRITERION ABSTENTION only"),
    (r"\bnor country-conditional\b|\bnot population-conditional\b",
     "-> no aggregate loss detected in the tested splits; p>0.05 is not equivalence"),
    (r"\bnot\s+(?:an\s+)?OOD artifact\b",
     "-> not explained by monotone degradation under the tested generic metrics"),
    (r"\blaunder(?:s|ed|ing)\b",
     "-> core INTERNALISES polarity into rewritten criterion semantics while "
     "discarding rating and disagreement provenance"),
]


def claim_strings(doc, path=""):
    """Yield (json path, text) for EVERY string in the document.

    Including strings inside lists: an attack planted a withdrawn framing as
    the second element of a list-valued verdict and the field-oriented walker
    missed it, because it only looked at a claim field when that field was
    itself a string.
    """
    if isinstance(doc, dict):
        for k, v in doc.items():
            yield from claim_strings(v, f"{path}.{k}" if path else k)
    elif isinstance(doc, list):
        for i, v in enumerate(doc):
            yield from claim_strings(v, f"{path}[{i}]")
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
    # ** rather than * : an attack put a results file one directory deeper and
    # the flat glob never saw it.  A checker's population must be the files
    # that exist, not the layout I assumed.
    files = sorted(_ROOT.glob("rounds/*/results/**/*.json"))
    files = [f for f in files if "_smoke_archive" not in f.parts and "SMOKE" not in f.name]
    hits, scanned, fields = [], 0, 0
    excluded = {}
    for f in files:
        try:
            doc = json.loads(f.read_text())
        except json.JSONDecodeError:
            print(f"  ! {f.relative_to(_ROOT)} is not valid JSON -- SKIPPED, and a "
                  f"skipped file is unchecked, not clean")
            continue
        scanned += 1
        rel = str(f.relative_to(_ROOT))
        for jp, text in claim_strings(doc):
            rule = payload_rule(rel, jp)
            if rule is not None:
                excluded[rule[2]] = excluded.get(rule[2], 0) + 1
                continue
            fields += 1
            for rx, why in WITHDRAWN:
                m = re.search(rx, text, flags=re.I)
                if m:
                    lo = max(0, m.start() - 60)
                    hits.append((f.relative_to(_ROOT), jp, m.group(0),
                                 text[lo:m.end() + 60].replace("\n", " "), why))

    print(f"scanned {scanned} results files, {fields} strings")
    if excluded:
        print(f"  excluded {sum(excluded.values())} payload strings (quoted data, not claims):")
        for why, cnt in sorted(excluded.items()):
            print(f"    {cnt:6d}  {why}")
        print("    ^ a claim written inside these paths would be INVISIBLE here")
    floor = _floor(scanned, "the set of results files scanned")
    if floor:
        return floor
    if not hits:
        print("NO LISTED PHRASE FOUND.")
        print("  This is NOT a certificate that no withdrawn framing is asserted -- the "
              "check is sound only in the flagging direction (see the module docstring).")
        return 0
    print(f"\n{len(hits)} withdrawn framing(s) still asserted in generated conclusions:\n")
    for f, jp, phrase, ctx, why in hits:
        print(f"  {f}")
        print(f"    field   {jp}")
        print(f"    phrase  {phrase!r}")
        print(f"    context ...{ctx}...")
        print(f"    rescope {why}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
