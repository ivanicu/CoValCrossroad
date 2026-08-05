#!/usr/bin/env python3
"""R560 · G1 names FOUR scope dimensions. How many does each claim state?

R558 found the TARGET missing from 10 of 10 claim rows and fixed it with one note. That was one
axis found by hand. G1 requires four -- population, instrument, baseline, regime -- and the
baseline is known to matter: R527 measured the extension moving 4 -> 8 across the baseline class.
Doing all four at once, so a third round is not spent finding the third axis.

ESTIMAND  per claim row, which of G1's four scope dimensions its scope column states.
IDENT     fully identified: text on one page, matched against vocabularies drawn from the page's
          own usage rather than invented.
SCOPE     population = the 10 numbered claim rows · instrument = anchored row parse + per-axis
          token sets · baseline = a row stating all four · regime = current STATEMENT.md.
WORLDS    A the rows state all four, and R558's target gap was a one-off.
          B one or more axes are systematically absent -> the scope column has a SHAPE defect,
            not a missing entry, and patching axes one at a time will not converge.
KILL      pre-registered: any axis stated by <5 of 10 rows -> WORLD B for that axis.
POS CTRL  'population' must be found in nearly every row -- the arms/prompts counts are visibly
          there. An axis vocabulary that finds nothing everywhere is a broken vocabulary, not an
          absent axis, and that is the distinction this control exists to make.
NEG CTRL  an invented axis vocabulary must match 0 rows.
ARTIFACT  results/scope_axes.json
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
stmt = (ROOT / "E05_the_space_of_compilers" / "STATEMENT.md").read_text()
rows = re.findall(r"^\|\s*\*\*(\d+)\*\*\s*\|(.+?)\|(.+?)\|\s*$", stmt, re.M)
claims = [(int(n), c.strip(), s.strip()) for n, c, s in rows if int(n) <= 10][:10]
if len(claims) < 10:
    print(f"  parsed {len(claims)} of 10 claim rows -> UNRUNNABLE"); sys.exit(2)

# vocabularies taken from THIS PAGE's own usage, not invented
AXES = {
 "population": ("arms", "prompts", "968", "41", "tags", "population", "census"),
 "instrument": ("judge", "0.8b", "2b", "target", "a2", "annotator", "consensus"),
 "baseline":   ("baseline", "pool[", "prompt-blind", "percentile", "floor", "ceiling",
                "comparator", "null"),
 "regime":     ("k=", "k=4", "at p", "per-prompt", "held-out", "release", "specification"),
}
FAKE = ("zzaxis9q", "quuxbaseline")

def has(s, toks): return any(t in s.lower() for t in toks)

tbl = {n: {ax: has(sc, tk) for ax, tk in AXES.items()} for n, _c, sc in claims}
pop_n = sum(v["population"] for v in tbl.values())
print(f"  POSITIVE CONTROL  'population' found in {pop_n} of 10 rows -> "
      f"{'PASS' if pop_n >= 8 else 'FAIL -- vocabulary is broken, not the axis absent'}")
fake_n = sum(has(sc, FAKE) for _n, _c, sc in claims)
print(f"  NEGATIVE CONTROL  an invented axis vocabulary matches {fake_n} rows -> "
      f"{'PASS' if fake_n == 0 else 'FAIL'}")
if pop_n < 8 or fake_n:
    sys.exit(2)

print(f"\n  claim  population  instrument  baseline  regime   stated")
for n in sorted(tbl):
    v = tbl[n]
    print(f"   {n:>4}  {str(v['population']):>10}  {str(v['instrument']):>10}  "
          f"{str(v['baseline']):>8}  {str(v['regime']):>6}   {sum(v.values())}/4")

counts = {ax: sum(v[ax] for v in tbl.values()) for ax in AXES}
print(f"\n  axis coverage over 10 rows:")
for ax, c in sorted(counts.items(), key=lambda kv: kv[1]):
    print(f"    {ax:<11} {c:>2}/10  {'⛔ BELOW THE KILL (5)' if c < 5 else ''}")
full = sum(1 for v in tbl.values() if all(v.values()))
print(f"  rows stating ALL FOUR: {full} of 10")

weak = [ax for ax, c in counts.items() if c < 5]
world = "B" if weak else "A"
print(f"\n  WORLD {world} -- " + (
    f"{', '.join(weak)} {'is' if len(weak)==1 else 'are'} systematically absent: the scope column "
    f"has a SHAPE defect, and patching one axis per round will not converge."
    if world == "B" else "every axis clears the kill; R558's target gap was a one-off."))
(pathlib.Path(__file__).parent / "results" / "scope_axes.json").write_text(json.dumps(
    {"world": world, "n_rows": len(claims), "per_row": tbl, "axis_counts": counts,
     "rows_stating_all_four": full, "axes_below_kill": weak,
     "note": "vocabularies drawn from the page's own usage; the population control distinguishes "
             "a broken vocabulary from an absent axis"}, indent=2))
