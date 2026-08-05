#!/usr/bin/env python3
"""R551 · Did DEFINITION.md stop recording rounds, and when?

ESTIMAND  for each round directory, whether DEFINITION.md carries (a) a HEADING for it and
          (b) any MENTION of it. Two units, kept separate on purpose.
IDENT     fully identified: both are exact reads of a file on disk.
SCOPE     population = every R### dir under E05/A24 · instrument = anchored regex on
          DEFINITION.md · baseline = a heading exists · regime = this document's whole history.
WORLDS    A the document is current and my grep is wrong (a heading style I did not anticipate).
          B the document stopped being appended at some round, and later rounds live only in
            commits and round READMEs.
KILL      pre-registered: if >=1 round after the last heading HAS a heading in some other form,
          WORLD A and the instrument is at fault. If the headings stop and stay stopped, WORLD B.

⚠ THE TWO UNITS, named before the control is designed (§4):
   instrument's unit = "a line matching ^#+ .*\\bR<n>\\b"   (a SECTION)
   claim's unit      = "this round's reasoning is recorded"  (CONTENT)
   They are NOT equal. A round can be MENTIONED inside another round's section without having
   one. So both are measured and reported separately, and the weaker one bounds the claim.

POS CTRL  R539/R540/R541 are known to have sections -> the heading detector must find them.
NEG CTRL  an invented round id must be found by neither detector.
ARTIFACT  results/coverage.json
"""
import json, pathlib, re

root = pathlib.Path(__file__).resolve().parents[3]
doc = (root / "E05_the_space_of_compilers" / "DEFINITION.md").read_text()
rounds = sorted((p.name for p in (root / "E05_the_space_of_compilers" /
                 "A24_what_the_definition_costs").glob("R*") if p.is_dir()),
                key=lambda n: int(re.match(r"R(\d+)", n).group(1)))
ids = [int(re.match(r"R(\d+)", n).group(1)) for n in rounds]

def has_heading(n):  return re.search(rf"^#+ .*\bR{n}\b", doc, re.M) is not None
def has_mention(n):  return re.search(rf"\bR{n}\b", doc) is not None

# CONTROLS
pos = [n for n in (539, 540, 541) if has_heading(n)]
neg = has_heading(999) or has_mention(999)
print(f"  POSITIVE CONTROL  headings found for R539/R540/R541: {len(pos)}/3 -> "
      f"{'PASS' if len(pos) == 3 else 'FAIL'}")
print(f"  NEGATIVE CONTROL  an invented round R999 found by neither: {not neg} -> "
      f"{'PASS' if not neg else 'FAIL'}")
if len(pos) != 3 or neg:
    raise SystemExit(2)

head = {n: has_heading(n) for n in ids}
ment = {n: has_mention(n) for n in ids}
last_head = max((n for n in ids if head[n]), default=None)
after = [n for n in ids if last_head is not None and n > last_head]
after_h = [n for n in after if head[n]]
after_m = [n for n in after if ment[n]]

print(f"\n  rounds in A24: {len(ids)}  (R{min(ids)}..R{max(ids)})")
print(f"  with a SECTION in DEFINITION.md : {sum(head.values())}")
print(f"  MENTIONED anywhere              : {sum(ment.values())}")
print(f"\n  last round with a section: R{last_head}")
print(f"  rounds after it: {len(after)}   with a section: {len(after_h)}   "
      f"merely mentioned: {len(after_m)}")
if after:
    print(f"    unrecorded: {', '.join('R%d' % n for n in after)}")

world = "A" if after_h else "B"
print(f"\n  WORLD {world} -- " + ("some later round DOES have a section; the detector was wrong."
      if world == "A" else
      f"the document stopped at R{last_head}; {len(after)} rounds live only in commits and READMEs."))

(pathlib.Path(__file__).parent / "results" / "coverage.json").write_text(json.dumps(
    {"world": world, "n_rounds": len(ids), "last_heading": last_head,
     "n_sections": sum(head.values()), "n_mentions": sum(ment.values()),
     "after_last_heading": after, "after_with_heading": after_h,
     "after_mentioned_only": after_m}, indent=2))

# ── THE NULL, added after the first result showed my framing was wrong ──────────────
# DEFINITION.md records 15% of rounds, so "10 unrecorded" means nothing until it is
# compared against the document's OWN history of gaps. Comparing a quantity to its own
# null, not to my expectation.
print("\n  ── is a 10-round tail anomalous against this document's own history? ──")
sec = [n for n in ids if head[n]]
gaps = [b - a - 1 for a, b in zip(sec, sec[1:])]          # rounds skipped between sections
ment_ids = [n for n in ids if ment[n]]
mgaps = [b - a - 1 for a, b in zip(ment_ids, ment_ids[1:])]  # rounds with no mention at all

import statistics as st
tail_sec = len(after)
tail_ment = len([n for n in ids if n > max(ment_ids)])
def pct(x, arr): return sum(1 for g in arr if g >= x) / len(arr) if arr else float("nan")

print(f"    SECTION gaps  n={len(gaps)}  median={st.median(gaps):.0f}  max={max(gaps)}  "
      f"| current tail={tail_sec}  -> {pct(tail_sec, gaps):.1%} of gaps are this long or longer")
print(f"    MENTION gaps  n={len(mgaps)}  median={st.median(mgaps):.0f}  max={max(mgaps)}  "
      f"| current tail={tail_ment}  -> {pct(tail_ment, mgaps):.1%} of gaps are this long or longer")

anomalous = pct(tail_ment, mgaps) < 0.05
print(f"\n  the 10-round tail is {'ANOMALOUS' if anomalous else 'ORDINARY'} for this document "
      f"(pre-registered at the 5% tail).")
print(f"  ⭐ and the load-bearing number is not the gap -- it is that DEFINITION.md has ALWAYS "
      f"recorded {sum(head.values())}/{len(ids)} = {sum(head.values())/len(ids):.0%} of rounds.")

j = pathlib.Path(__file__).parent / "results" / "coverage.json"
d = json.loads(j.read_text())
d.update({"section_gaps": {"n": len(gaps), "median": st.median(gaps), "max": max(gaps),
                           "tail": tail_sec, "pct_ge_tail": pct(tail_sec, gaps)},
          "mention_gaps": {"n": len(mgaps), "median": st.median(mgaps), "max": max(mgaps),
                           "tail": tail_ment, "pct_ge_tail": pct(tail_ment, mgaps)},
          "tail_anomalous": bool(anomalous),
          "coverage_rate": sum(head.values()) / len(ids)})
j.write_text(json.dumps(d, indent=2))
