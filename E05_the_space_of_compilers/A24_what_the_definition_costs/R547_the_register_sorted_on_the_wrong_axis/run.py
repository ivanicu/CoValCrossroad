#!/usr/bin/env python3
"""R547 — is the register's row 1 reachable from this site, or only cheap?

The register orders "by what it costs to remove" and its header calls that ordering the
deliverable. Row 1 is `source_rubric_item_ids` at cost "a schema line" -- ranked cheapest. This
asks whether it is REACHABLE here, which is a different question from whether it is cheap.

ESTIMAND (before method): whether `source_rubric_item_ids` exists in any release or code file on
  this site, and how much of the mapping it would carry is reconstructible here.
IDENTIFICATION: fully identified -- a field either appears in the shipped files or it does not.
SCOPE  population: data/ and corebench/ · instrument: a literal string search · baseline: fields
  known to exist in the release · regime: this checkout.
WORLDS  A · the field or its content is reachable here, so "a schema line" is a fair cost and the
              ordering is sound.
        B · it is not, so row 1 requires the PUBLISHER and the ordering conflates effort with
              agency -- cheap in keystrokes, unavailable in fact.
KILL (pre-registered): any occurrence of the field in data/ kills world B.
POSITIVE CONTROL: the search must FIND fields that do exist in the release -- `annotator_id` and
  `ranking_blocks` are read by score.py's load_targets, so they must be present. A search that
  cannot find them cannot report an absence.
NEGATIVE CONTROL: an invented field name must NOT be found, else the search matches anything.
NOISE FLOOR: none -- exact string presence.
MULTIPLICITY: 4 field probes across 2 trees; all printed.
IMPOSSIBLE HERE: adding the field. It belongs to an already-shipped release, and R509 measured
  only 6.6% of its content as verbatim-reconstructible from `coval_full`.
"""
import json, pathlib, sys

FIELD = "source_rubric_item_ids"
PRESENT = ["annotator_id", "ranking_blocks"]      # read by score.py::load_targets
ABSENT = "zzz_not_a_field_zzz"

def seen(root, needle):
    hits = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix not in (".jsonl", ".json", ".py", ".md"):
            continue
        try:
            if needle in p.read_text(errors="ignore"):
                hits.append(str(p.relative_to(root.parent)))
        except Exception:
            pass
    return hits

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    data, code = root / "data", root / "corebench"

    pos = {f: seen(data, f) for f in PRESENT}
    ok_pos = all(v for v in pos.values())
    print(f"  POSITIVE CONTROL  fields known to exist are found in data/:")
    for f, v in pos.items():
        print(f"    {f:<16}{len(v)} file(s)  {v[:2]}")
    print(f"    -> {'PASS' if ok_pos else 'FAIL -- the search cannot report an absence'}")
    if not ok_pos: return 0

    neg = seen(data, ABSENT) + seen(code, ABSENT)
    print(f"  NEGATIVE CONTROL  an invented field is not found: {len(neg)} -> "
          f"{'PASS' if not neg else 'FAIL'}")
    if neg: return 0

    in_data, in_code = seen(data, FIELD), seen(code, FIELD)
    world = "A" if (in_data or in_code) else "B"
    print(f"\n  ⭐ `{FIELD}` in data/  : {len(in_data)} file(s)")
    print(f"     `{FIELD}` in corebench/: {len(in_code)} file(s)")
    print(f"  WORLD {world} -- " +
          ("the field is reachable here; 'a schema line' is a fair cost" if world == "A" else
           "the field exists in NEITHER tree. Row 1 requires the PUBLISHER to add it to an "
           "already-shipped release, so the register's cheapest row is the one thing this site "
           "cannot do -- the ordering conflates effort with agency"))
    print(f"  ⚠ and R509 measured only 6.6% of the mapping as verbatim-reconstructible here, so "
          f"the content cannot be rebuilt either.")

    out = pathlib.Path(__file__).parent / "results/row1_reachability.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"field": FIELD, "in_data": in_data, "in_code": in_code,
                               "positive_control": {k: len(v) for k, v in pos.items()},
                               "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
