"""Which rounds put something in the graph, and which only printed to a terminal nobody kept.

The ledger now reports 55 claims with evidence from r123-r196. The sweep has more rounds than
that, and until r199 rebuilt the graph nobody could ask which ones actually deposited anything.
The question matters for one reason: a round that only printed leaves nothing for a reader who
was not there. Its result exists in a commit message and in a results/*.json nobody indexes, and
the claim graph -- the thing built to be the ontology rather than a log about it -- does not know
it happened.

THIS IS NOT A DEMAND THAT EVERY ROUND PRODUCE A CLAIM. Several should not:

  instrument rounds   built a tool and tested it; the tool is the deposit, not a claim
  audit rounds        checked other rounds; the correction belongs to the claim it corrected
  census waves        their output IS DEFECTS.py, a different consolidator with its own home
  negative rounds     found nothing, which is worth recording only if the null was powered

So the output is a classification, not a score. What it is looking for is the fourth category
nobody would defend: a round that produced a substantive result about the release and deposited
it nowhere except its own stdout.

METHOD. Round directories on disk against evidence experiment tags in the graph. A round counts as
deposited if any evidence row names it, or if a node's statement cites it -- the second because
several rounds appear as the KILLER of a claim rather than the source of one, and killing is a
deposit.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

# parents[1] is 13_normative_chain, not the repo root -- the SECOND time this exact off-by-one has
# appeared (r197's glob was the first), and both times the symptom was a component that found
# nothing rather than one that errored loudly. Here it did error, because an import cannot fail
# quietly; r197's glob could, and only its calibration check caught it.
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "db"))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"

import derivation_chain as dc  # noqa: E402

RN = re.compile(r"\br(\d+)\b")          # for prose: r195, r191's, r183-resolution-floor
# A DIRECTORY NAME NEEDS A DIFFERENT PATTERN and the first version used RN for both. "r150_does_
# the_veto_do_anything" does not match \br(\d+)\b, because the underscore after 150 is a WORD
# character and there is no boundary there. The result was an empty round list from a glob that
# had already asserted non-empty -- so the assert passed, `nums` came back empty, and min() raised
# on the next line. Two lines apart, and the guard could not see it because it was guarding the
# wrong quantity.
DIRN = re.compile(r"^r(\d+)")

# Rounds whose deposit is legitimately somewhere other than the claim graph. Stated here so the
# classification is a claim about each round rather than a residual bucket.
ELSEWHERE = {
    "166": "census wave -> DEFECTS.py", "167": "census wave -> DEFECTS.py",
    "168": "census wave -> DEFECTS.py", "169": "census wave -> DEFECTS.py",
    "170": "census wave -> DEFECTS.py", "171": "card audit -> card_audit.json + DEFECTS.py",
    "175": "audit of DEFECTS.py -> corrections wired into DEFECTS.py itself",
    "197": "instrument, reported INSUFFICIENT -> the negative result is the deposit",
    "198": "instrument -> covalx/estimand.py",
    "200": "this audit",
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    dirs = sorted(p.parent.name for p in (ROOT / "13_normative_chain").glob("r*/run.py"))
    assert dirs, "no round directories found -- the glob is wrong, not the corpus"
    nums = {}
    for d in dirs:
        m = DIRN.match(d)
        if m:
            nums[m.group(1)] = d
    print(f"round directories on disk: {len(nums)}  "
          f"(r{min(nums, key=int)} to r{max(nums, key=int)})")

    cited = Counter()
    for (exp,) in dc.q("SELECT experiment FROM evidence"):
        for m in RN.finditer(exp or ""):
            cited[m.group(1)] += 1
    for (stmt,) in dc.q("SELECT coalesce(statement,'') FROM node"):
        for m in RN.finditer(stmt):
            cited[m.group(1)] += 1
    print(f"distinct rounds referenced anywhere in the graph: "
          f"{len([k for k in cited if k in nums])} of {len(nums)} on disk")

    deposited = {k for k in nums if cited.get(k)}
    silent = {k for k in nums if k not in deposited and k not in ELSEWHERE}
    elsewhere = {k for k in nums if k not in deposited and k in ELSEWHERE}

    print("\n" + "=" * 78)
    print("ROUNDS THAT DEPOSITED INTO THE GRAPH")
    print("=" * 78)
    for k in sorted(deposited, key=int):
        print(f"  r{k:<4s} {nums[k][len('r' + k) + 1:][:56]:56s} cited {cited[k]}x")

    print("\n" + "=" * 78)
    print("ROUNDS WHOSE DEPOSIT IS ELSEWHERE, BY DESIGN")
    print("=" * 78)
    for k in sorted(elsewhere, key=int):
        print(f"  r{k:<4s} {nums[k][len('r' + k) + 1:][:40]:40s} {ELSEWHERE[k]}")

    print("\n" + "=" * 78)
    print("ROUNDS THAT LEFT NOTHING BUT STDOUT")
    print("=" * 78)
    if not silent:
        print("  none")
    for k in sorted(silent, key=int):
        res = list((ROOT / "13_normative_chain" / nums[k] / "results").glob("*.json")) \
            if (ROOT / "13_normative_chain" / nums[k] / "results").exists() else []
        doc = ""
        try:
            src = (ROOT / "13_normative_chain" / nums[k] / "run.py").read_text()
            doc = (src.split('"""')[1].strip().splitlines() or [""])[0][:60]
        except Exception:                                        # noqa: BLE001
            pass
        print(f"  r{k:<4s} {nums[k][len('r' + k) + 1:][:34]:34s} "
              f"{len(res)} result file(s)")
        print(f"        {doc}")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    print(f"  {len(deposited)} deposited, {len(elsewhere)} deposited elsewhere by design, "
          f"{len(silent)} left only stdout.")
    if silent:
        print(f"  Each of those {len(silent)} produced a results/*.json, so nothing is LOST -- but a")
        print(f"  JSON in a round directory is a file, and the graph is the index. A reader who")
        print(f"  was not here finds the claim only if they already know which round to open,")
        print(f"  which is the definition of not being an index.")
        print(f"  This is not a scolding of past rounds; it is the list of what to deposit, and it")
        print(f"  could not be produced before r199 made the graph current.")
    else:
        print(f"  Nothing in the sweep exists only as terminal output.")
    print(f"\n  THE LIMIT: 'cited' means a round number appears in an evidence tag or a node")
    print(f"  statement. A round could be cited for a trivial reason and count as deposited, and a")
    print(f"  round whose finding was folded into another node's statement without its number")
    print(f"  would read as silent. This measures REFERENCE, not deposit -- and the two differ")
    print(f"  exactly where someone wrote a claim without saying where it came from.")

    (OUT / "trace.json").write_text(json.dumps(
        {"on_disk": len(nums), "deposited": sorted(deposited, key=int),
         "elsewhere": {k: ELSEWHERE[k] for k in sorted(elsewhere, key=int)},
         "stdout_only": sorted(silent, key=int),
         "limit": "measures reference in evidence tags and node statements, not deposit"},
        indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
