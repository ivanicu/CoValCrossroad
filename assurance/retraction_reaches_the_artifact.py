"""A retraction written only in prose leaves the artifact asserting the overturned verdict.

WHY THIS EXISTS. R499 was retracted into RETRACTIONS.md, DEFINITION.md, STATEMENT.md and its own
README, and `statement_provenance.py` still reported `R497 -> B (REAL STRUCTURE)` and
`R499 -> B CANCELLING FUNCTIONS` as SETTLED, because that gate reads `results/*.json`. R500 then
counted 18 of 98 cited rounds in the same state. A gate that reads artifacts cannot see prose, and
its PASS then certifies json freshness as though it were truth.

WHY NOT MAKE THE GATE READ PROSE INSTEAD. Derivation, not a measurement, and labelled as one:
R500 measured 20-29 ledger entries whose retraction DIRECTION is ambiguous (no `A -> B` arrow), so
teaching a gate to parse the ledger imports a 20-29-case classification problem it does not have
today, and every one of those cases would become a gate verdict nobody can audit. The artifact is
the home; the retraction must travel to it. That is HB7 -- one home per fact -- applied to verdicts.

RATCHET, NOT A CLIFF. 18 cases exist and most are un-triaged: R500's hand read of 5 found 3 that
retract an ANNOUNCED NEXT STEP or a METHOD, leaving the world untouched, so demanding all 18 be
annotated today would demand work that may not be owed. The gate therefore freezes the known 18 and
fails when (a) the debt GROWS, or (b) a frozen entry stops being detected -- which means either it
was fixed (update the freeze) or the detector went blind (fix the detector). Both need a human.

⚠ THE DETECTOR IS A SEARCH, SO IT CARRIES ITS POSITIVE CONTROL. Before any count, it must find a
case known to exist: R485's artifact carries `superseded_by`, and an un-annotated fixture is built
in memory and must be flagged. A count from an instrument never shown to return non-zero is silence.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
E05 = ROOT/"E05_the_space_of_compilers"
A24 = E05/"A24_what_the_definition_costs"
FREEZE = pathlib.Path(__file__).resolve().parent/"KNOWN_UNANNOTATED_ARTIFACTS.json"
MARK = ("RETRACTED", "retracted_by", "SUPERSEDED", "superseded_by", "withdrawn", "WITHDRAWN")


def is_annotated(o: dict) -> bool:
    blob = json.dumps(o, ensure_ascii=False)
    return any(m in blob for m in MARK)


def cited() -> set[str]:
    t = (E05/"DEFINITION.md").read_text() + (E05/"STATEMENT.md").read_text()
    return {f"R{n}" for n in re.findall(r"\(R(\d{3})[,)]", t) + re.findall(r"R(\d{3})[,)]", t)}


def retracted_party() -> set[str]:
    """Left side of an explicit `A -> B` arrow in a ledger heading. Ambiguous entries EXCLUDED --
    counting them would make the gate assert a direction R500 measured as undetermined."""
    out = set()
    for b in re.split(r"\n(?=## )", (ROOT/"RETRACTIONS.md").read_text()):
        head = b.split("\n", 1)[0]
        m = re.search(r"R(\d{3})\s*(?:->|→)\s*R(\d{3})", head)
        if m: out.add(f"R{m.group(1)}")
    return out


def unannotated(ids: set[str]) -> set[str]:
    bad = set()
    for rid in ids:
        for d in A24.glob(f"{rid}_*"):
            for f in sorted((d/"results").glob("*.json")):
                try: o = json.loads(f.read_text())
                except Exception: continue
                if isinstance(o, dict) and o.get("world") and not is_annotated(o):
                    bad.add(rid)
    return bad


def main() -> int:
    pop = cited() & retracted_party()
    if not pop:
        print("  population EMPTY -- no cited round is named as a retracted party."); return 2

    # POSITIVE CONTROL, two-sided, on real objects.
    fixture = {"world": "B (SOMETHING)", "n": 1}
    ok_pos = not is_annotated(fixture)
    r485 = None
    for d in A24.glob("R485_*"):
        for f in sorted((d/"results").glob("*.json")):
            o = json.loads(f.read_text())
            if isinstance(o, dict) and o.get("world"): r485 = o
    ok_neg = r485 is not None and is_annotated(r485)
    print(f"  positive control: an un-annotated artifact is detected        "
          f"{'PASS' if ok_pos else 'FAIL'}")
    print(f"  negative control: R485 (annotated) is NOT detected            "
          f"{'PASS' if ok_neg else 'FAIL'}")
    if not (ok_pos and ok_neg):
        print("  a control misbehaved -- counts below are silence"); return 1

    now = unannotated(pop)
    if not FREEZE.exists():
        FREEZE.write_text(json.dumps({"count": len(now), "ids": sorted(now)}, indent=1))
        print(f"  froze {len(now)} known-unannotated artifacts"); return 0
    fr = json.loads(FREEZE.read_text())
    known = set(fr["ids"])
    if fr.get("count") != len(known):
        print(f"  freeze file is self-inconsistent: count {fr.get('count')} vs {len(known)} ids")
        return 1

    grew = sorted(now - known)
    gone = sorted(known - now)
    print(f"\n  cited AND named as retracted party : {len(pop)}")
    print(f"  artifacts with no retraction marker: {len(now)}   frozen: {len(known)}")
    if grew:
        print(f"\n  NEW DEBT -- these were retracted in prose and the artifact never learned it:")
        for r in grew: print(f"    {r}")
        print(f"  Annotate the artifact (preserve `world_original`), or explain why the world stands.")
        return 1
    if gone:
        print(f"\n  frozen entries no longer detected: {gone}")
        print(f"  Either they were annotated (update {FREEZE.name}) or the detector went blind.")
        return 1
    print(f"\n  PASS -- debt is {len(now)}, unchanged. Known gaps still open, as documented.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
