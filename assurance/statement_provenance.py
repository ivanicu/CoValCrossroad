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
            if isinstance(j, dict) and isinstance(j.get("world"), str):
                return j["world"]
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
    print(f"  {'round':>7}  world")
    bad = []
    for c in cites:
        w = world_of("R" + c)
        flag = "" if (w and w != "UNVERIFIED") else "   ⛔"
        if flag:
            bad.append(("R" + c, w))
        print(f"  {'R'+c:>7}  {w or '(no artifact / no world)'}{flag}")
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
        print(f"\n  ⛔ FAIL: {len(bad)} citation(s) name a round that is UNVERIFIED or has no verdict:")
        for r, w in bad:
            print(f"    {r}: {w or 'no artifact'}")
        return 1
    print(f"\n  PASS — all {len(cites)} cited rounds carry a settled verdict.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
