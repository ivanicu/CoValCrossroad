#!/usr/bin/env python3
"""R565 · Do the nine arcs besides A24 reach the deliverable at all?

R564 found ten arcs (A16-A25) where I had been treating A24 as the epoch, and rebuilt A24's index.
every_round_reaches_the_readme still returns rc=1. The likely cause and the open scope question are
the same object: rounds outside A24.

ESTIMAND  per arc: rounds with results · rounds carrying an index row · rounds cited in STATEMENT.md.
IDENT     fully identified: directories, one README, one statement.
SCOPE     population = every R* dir under E05/A* with a non-empty results/ · instrument = substring
          presence in the two documents · baseline = A24's coverage after R564 · regime = HEAD.
WORLDS    A the other arcs are represented -> the deliverable spans the epoch.
          B they are not -> the statement rests on one arc of ten, and that is a scope fact the
            page does not carry.
KILL      pre-registered: if <50% of non-A24 rounds carry an index row, WORLD B.
POS CTRL  A24's own rounds must read as ~fully indexed after R564. If they do not, the presence
          test is broken and a zero elsewhere is silence.
NEG CTRL  an invented round id must appear in neither document.
ARTIFACT  results/nine_arcs.json
"""
import collections, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
IDX = (E05 / "A24_what_the_definition_costs" / "README.md").read_text()
STM = (E05 / "STATEMENT.md").read_text()

per = collections.defaultdict(lambda: {"rounds": 0, "indexed": 0, "cited": 0, "ids": []})
for arc in sorted(d for d in E05.glob("A*") if d.is_dir()):
    for d in sorted(x for x in arc.glob("R*") if x.is_dir() and re.match(r"R\d+_", x.name)):
        res = d / "results"
        if not (res.is_dir() and any(res.iterdir())): continue
        rid = d.name.split("_")[0]
        p = per[arc.name]
        p["rounds"] += 1
        p["indexed"] += d.name in IDX
        p["cited"] += bool(re.search(rf"\({rid}[,)]|{rid}[,)]", STM))
        p["ids"].append(rid)

a24 = per["A24_what_the_definition_costs"]
pc = a24["indexed"] / a24["rounds"] if a24["rounds"] else 0
print(f"  POSITIVE CONTROL  A24 indexed after R564: {a24['indexed']}/{a24['rounds']} = {pc:.1%} -> "
      f"{'PASS' if pc > 0.9 else 'FAIL — the presence test is broken'}")
nc = ("R999_nope" in IDX) or ("R999" in STM)
print(f"  NEGATIVE CONTROL  an invented id appears in neither document: {not nc} -> "
      f"{'PASS' if not nc else 'FAIL'}")
if pc <= 0.9 or nc:
    sys.exit(2)

print(f"\n  {'arc':<46} {'rounds':>7} {'indexed':>8} {'cited in STATEMENT':>19}")
tot = collections.Counter()
for a in sorted(per):
    v = per[a]
    tot["rounds"] += v["rounds"]; tot["indexed"] += v["indexed"]; tot["cited"] += v["cited"]
    print(f"  {a[:46]:<46} {v['rounds']:>7} {v['indexed']:>8} {v['cited']:>19}")

other = {a: v for a, v in per.items() if a != "A24_what_the_definition_costs"}
o_r = sum(v["rounds"] for v in other.values())
o_i = sum(v["indexed"] for v in other.values())
o_c = sum(v["cited"] for v in other.values())
print(f"\n  the NINE arcs besides A24: {o_r} rounds   indexed {o_i} ({o_i/o_r:.1%})   "
      f"cited in STATEMENT {o_c} ({o_c/o_r:.1%})")
print(f"  A24 alone:                 {a24['rounds']} rounds   indexed {a24['indexed']}   "
      f"cited {a24['cited']}")

world = "B" if (o_i / o_r) < 0.5 else "A"
print(f"\n  WORLD {world} -- " + (
    f"only {o_i/o_r:.1%} of non-A24 rounds carry an index row; the deliverable rests on one arc "
    f"of ten and the page does not say so."
    if world == "B" else "the other arcs are represented; the deliverable spans the epoch."))
(pathlib.Path(__file__).parent / "results" / "nine_arcs.json").write_text(json.dumps(
    {"world": world, "per_arc": {a: {k: v[k] for k in ("rounds", "indexed", "cited")}
                                 for a, v in per.items()},
     "non_a24": {"rounds": o_r, "indexed": o_i, "cited": o_c},
     "a24": {k: a24[k] for k in ("rounds", "indexed", "cited")},
     "total_rounds": tot["rounds"]}, indent=2))
