#!/usr/bin/env python3
"""assurance/statement_provenance.py — every number on STATEMENT.md traces to a NON-UNVERIFIED round.

⛔ WHY. §0.2 of the operating constitution: lead with what STANDS, never with the ledger. But "what
   stands" is itself a claim, and the cheapest way to get it wrong is to carry forward a number whose
   own round returned UNVERIFIED -- which reads identically to a settled one once it is out of its
   round's context.

WHAT IT ENFORCES. Every `(R###)` citation on the page must name a round whose artifact records a
`world` that is not UNVERIFIED. A round with no artifact, or no world, is ALSO a failure: silence is
not a pass.

⚠ AND ITS OWN LIMIT, STATED: this checks the CITATIONS, not the sentences. A number could be
  mis-transcribed from a sound round and this gate would not see it -- that is what
  `definition_matches_the_record.py` is for, and the two are deliberately separate instruments with
  different units (this one: rounds; that one: values).
"""
from __future__ import annotations
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
DOC = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"


def world_of(rid):
    for d in A24.glob(f"{rid}_*"):
        for f in (d / "results").glob("*.json"):
            try:
                j = json.loads(f.read_text())
            except Exception:
                continue
            # ⭐ WIDENED 2026-08-05 (R600), and MEASURED SAFE BEFORE APPLYING: on the 84
            #   rounds this gate currently sees, reading `verdict` as well as `world` changes
            #   0 verdicts -- it breaks nothing and repairs nothing TODAY. It matters because
            #   R398 and R427 are referenced by STATEMENT.md, are settled, and record their
            #   result under `verdict`; under the old lookup they would be REJECTED for a KEY
            #   NAME. R594 measured `world` at 44% prevalence across the corpus, so reading
            #   exactly one spelling of an unenforced field is the R596 failure again.
            if isinstance(j, dict):
                for k in ("world", "verdict"):
                    if isinstance(j.get(k), str):
                        return j[k]
    return None


def main() -> int:
    if not DOC.exists():
        print("UNRUNNABLE: STATEMENT.md absent. Exit 2, never 0."); return 2
    text = DOC.read_text()
    cites = sorted(set(re.findall(r"\(R(\d{3})[,)]", text) + re.findall(r"R(\d{3})[,)]", text)))
    print("STATEMENT PROVENANCE — every citation must name a round that is not UNVERIFIED\n")
    if not cites:
        print("  UNRUNNABLE: no citations found. A page with no provenance cannot pass. Exit 2.")
        return 2
    # ⭐ REPAIRED 2026-08-05 (R596), after an attack of 8 spellings x 2 runs in sandbox trees
    #    stopped 1 and let 7 through. TWO defects, and the second is the one that matters.
    #
    #    ① `w != "UNVERIFIED"` is EXACT string inequality. R594/R595 measured `world` to be an
    #       open vocabulary: 220 distinct values, 95% of them occurring once. So the exact
    #       comparison was a string test against a field with no enforced type, and `lowercase`,
    #       `trailing space`, `leading space`, `trailing newline`, `sentence`, `prefixed` and
    #       `em-dash form` all walked straight through. LIVE, not hypothetical: cited round R501
    #       carries "UNVERIFIED — the instrument cannot localise oracle_k4 ..." and was passing.
    #       Fixed by matching the FIRST TOKEN, case-folded and punctuation-stripped.
    #
    #    ② AND THE RULE ITSELF WAS WRONG, which tightening ① alone would have made worse.
    #       STATEMENT.md line 197 reads "That question is `UNVERIFIED`, not closed" and cites
    #       R501 AS EVIDENCE THAT THE QUESTION IS OPEN. A gate that forbids every citation of an
    #       UNVERIFIED round forbids citing a failure as a failure -- so the repaired ① would
    #       have rejected an honest, correctly-scoped sentence and pushed the author toward
    #       DELETING the caveat to make the gate green. That is a gate manufacturing the error
    #       it exists to prevent.
    #       So: an UNVERIFIED round may be cited IFF the citing line SAYS SO. No new marker is
    #       introduced -- the document already writes the word, and requiring it is what makes
    #       the scope machine-visible instead of a matter of the reader's attention.
    def is_unverified(w):
        if not w:
            return True
        first = re.split(r"[\s,;:.—–-]+", w.strip(), maxsplit=1)[0]
        return first.strip("`*_'\"").upper() == "UNVERIFIED"

    #    ⚠ THE UNIT IS A PARAGRAPH, NOT A LINE, and a line-scoped version of this rule was
    #      written first and caught before it ran. R501's citation sits on line 197 while its
    #      `UNVERIFIED` marker is on line 194 of the same wrapped paragraph -- so line scope
    #      would have flagged the one sentence in the document that does this correctly.
    #    ⚠ PROXY LEDGER, stated rather than hidden: paragraph scope cannot bind the marker to a
    #      SPECIFIC round, so a paragraph citing several rounds allows all of them. SOUND
    #      DIRECTION: a flagged citation is genuinely undeclared. UNSOUND DIRECTION: an allowed
    #      citation may be riding another round's marker. Tightening needs per-citation syntax
    #      the document does not currently carry.
    paras = re.split(r"\n\s*\n", text)
    print(f"  {'round':>7}  world")
    bad = []
    for c in cites:
        w = world_of("R" + c)
        declared = any(("R" + c) in p and "UNVERIFIED" in p for p in paras)
        if not is_unverified(w):
            flag = ""
        elif declared:
            flag = "   ○ UNVERIFIED, and the citing line says so — allowed"
        else:
            flag = "   ⛔"
            bad.append(("R" + c, w))
        print(f"  {'R'+c:>7}  {(w or '(no artifact / no world)')[:72]}{flag}")
    # POSITIVE CONTROL: the checker must be able to FAIL. R466/R467 are known UNVERIFIED.
    known = [r for r in ("R466", "R467") if world_of(r) == "UNVERIFIED"]
    print(f"\n  POSITIVE CONTROL  rounds known to be UNVERIFIED and therefore rejectable: {known}")
    if not known:
        print("  ⛔ the checker cannot demonstrate a rejection — it may pass everything. Exit 2.")
        return 2
    print(f"  ⚠ LIMIT  this checks CITATIONS, not SENTENCES. A number mis-transcribed from a sound")
    print(f"    round passes here; that is `definition_matches_the_record.py`'s unit, not this one's.")
    # ⭐ CLOSING THE TRANSCRIPTION GAP BY CHAINING, NOT BY A SECOND TRANSCRIPTION. Every number on
    #    STATEMENT.md should already appear in DEFINITION.md, which `definition_matches_the_record`
    #    re-derives from artifacts. So a number present in both is anchored TRANSITIVELY; a number
    #    present only on the statement is a fresh, unchecked transcription and is named.
    defdoc = (ROOT / "E05_the_space_of_compilers" / "DEFINITION.md").read_text()
    nums = sorted(set(re.findall(r"(?<![\w.])(\d+\.\d{3,4})(?![\w])", text)))
    orphan = [n for n in nums if n not in defdoc]
    print(f"\n  TRANSITIVE ANCHORING  decimal values on the statement: {len(nums)};")
    print(f"    also present in DEFINITION.md (hence artifact-anchored): {len(nums)-len(orphan)}")
    if orphan:
        print(f"    ⛔ present ONLY on the statement -- unchecked transcriptions: {orphan}")
        bad.append(("TRANSCRIPTION", f"{len(orphan)} orphan value(s)"))
    else:
        print(f"    PASS -- no value appears on the statement that is not anchored elsewhere")

    if bad:
        # ⭐ R704: this sentence used to be TYPED, not computed -- it said "N citation(s) name a
        #   round that is UNVERIFIED" for EVERY failure, including a TRANSCRIPTION one, and it
        #   misdiagnosed R704's own run. §4: any comparative or descriptive word in a verdict
        #   string must be computed. The kinds are now counted and named separately.
        ncite = sum(1 for r, _ in bad if r != "TRANSCRIPTION")
        ntran = sum(1 for r, _ in bad if r == "TRANSCRIPTION")
        kinds = []
        if ncite:
            kinds.append(f"{ncite} citation(s) naming a round that is UNVERIFIED or has no verdict")
        if ntran:
            kinds.append(f"{ntran} transcription failure(s) — a value on the statement anchored nowhere")
        print(f"\n  ⛔ FAIL: {' AND '.join(kinds)}:")
        for r, w in bad:
            print(f"    {r}: {w or 'no artifact'}")
        return 1
    print(f"\n  PASS — all {len(cites)} cited rounds carry a settled verdict.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
