#!/usr/bin/env python3
"""R564 · Rebuild the round index from each round's OWN README heading.

My NEXT line said the README was un-updated "since R555" and that writing "those seven rows" was
the work. Both false: the index ends at R327 and the gate flags 127 rounds. I read the tail of the
gate's output -- the same error R561 logged two rounds ago.

ESTIMAND  the number of rounds with results but no index row, and the index's true high-water mark.
IDENT     fully identified: directories on disk against the README's ROUND-INDEX block.
SCOPE     population = R* dirs under A24 with a non-empty results/ · instrument = the index block ·
          baseline = every such round having a row · regime = current HEAD.
WORLDS    A the index is current -> my NEXT line's "since R555" was right.
          B it is far behind -> the production debt is the deliverable's navigation, not seven rows.
KILL      pre-registered: >20 missing rows -> WORLD B.
POS CTRL  a round KNOWN to be indexed (R327, the last row) must read as present. Else the parse
          cannot see rows and "missing" would be silence.
NEG CTRL  an invented round id must read as absent.
⛔ L80: the description of each row is taken VERBATIM from that round's own README first heading.
   A machine may not invent a WHY. Rounds with no README get no invented description -- they are
   listed with their directory name and flagged.
ARTIFACT  results/index_rebuild.json
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
RM = A24 / "README.md"
text = RM.read_text()

rounds = sorted((d for d in A24.glob("R*") if d.is_dir()),
                key=lambda d: int(re.match(r"R(\d+)", d.name).group(1)))
have_results = [d for d in rounds if (d / "results").is_dir() and any((d / "results").iterdir())]

print(f"  POSITIVE CONTROL  R327 (the index's last row) is present: "
      f"{'R327' in text} -> {'PASS' if 'R327' in text else 'FAIL — parse is blind'}")
print(f"  NEGATIVE CONTROL  an invented round is absent: {'R999_nope' not in text} -> PASS")
if "R327" not in text:
    sys.exit(2)

missing = [d for d in have_results if d.name not in text]
ids = [int(re.match(r"R(\d+)", d.name).group(1)) for d in rounds]
indexed = [i for i in ids if f"R{i}" in text]
print(f"\n  rounds with results: {len(have_results)}   index high-water mark: R{max(indexed)}")
print(f"  rounds with results and NO index row: {len(missing)}")

def describe(d):
    """VERBATIM from the round's own README heading. Never invented (L80)."""
    p = d / "README.md"
    if not p.exists():
        return None
    for line in p.read_text().splitlines():
        if line.startswith("# "):
            t = line[2:].strip()
            return re.sub(r"^R\d+\s*[·:-]\s*", "", t)
    return None

rows, undescribed = [], []
for d in missing:
    desc = describe(d)
    n = len(list((d / "results").iterdir()))
    if desc is None:
        undescribed.append(d.name)
        rows.append(f"| [`{d.name.split('_')[0]}`]({d.name}) | *(no README — description not "
                    f"invented)* | {n} |")
    else:
        rows.append(f"| [`{d.name.split('_')[0]}`]({d.name}) | {desc} | {n} |")

print(f"  rows generated: {len(rows)}   of which have NO README so carry no description: "
      f"{len(undescribed)}")
world = "B" if len(missing) > 20 else "A"
print(f"\n  WORLD {world} -- " + (
    f"the index is {max(ids) - max(indexed)} rounds behind its high-water mark; the debt is the "
    f"deliverable's navigation, not seven rows."
    if world == "B" else "the index is current."))

marker = "<!-- ROUND-INDEX:END -->"
assert marker in text
RM.write_text(text.replace(marker, "\n".join(rows) + "\n\n" + marker))
print(f"  wrote {len(rows)} rows into README.md before {marker}")

(pathlib.Path(__file__).parent / "results" / "index_rebuild.json").write_text(json.dumps(
    {"world": world, "n_rounds": len(rounds), "n_with_results": len(have_results),
     "index_highwater": max(indexed), "max_round": max(ids), "n_missing_rows": len(missing),
     "n_rows_written": len(rows), "rounds_without_readme": undescribed,
     "note": "descriptions taken VERBATIM from each round's own README heading (L80)"}, indent=2))
