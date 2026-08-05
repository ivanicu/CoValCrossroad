#!/usr/bin/env python3
"""R514 — is clause ① independent of clause ②, or subsumed by it?

ESTIMAND (before method): the number of admissible objects that satisfy ② and violate ①.
  If 0, ① cannot narrow the definition's extension and is not an independent clause.
IDENTIFICATION: fully identified from the persisted census — both clause verdicts are
  already stored per arm as ok1/ok2 over the same 968 prompts and the same statistic (A2).
SCOPE  population: the 41 arms of R294 · instrument: A2 vs a scalar bar · baseline: the two
  bars themselves · regime: bars aggregated GLOBALLY, which is the load-bearing assumption.
WORLDS  A · ① is an independent criterion that happens to be unexercised.
        B · ① is logically subsumed: bar1 < bar2, so a2>bar2 implies a2>bar1 by transitivity.
KILL (pre-registered): any arm with ok2=True and ok1=False kills B.
POSITIVE CONTROL: the census must contain arms that FAIL ① (else the ① verdict is degenerate
  and no conclusion about binding is admissible). Requires >0 arms with ok1=False.
NEGATIVE CONTROL: recover both bars independently from each arm's own contrast and require
  the bar1<bar2 ordering to hold on EVERY arm, not just the one inspected.
ARITHMETIC TRAP: this is a DERIVATION, not a measurement. Reported as such. The assumption is
  that both bars are global scalars on a common statistic and direction; verified below.
IMPOSSIBLE HERE: whether ① binds under a PER-PROMPT bar. The census stores aggregate contrasts
  only; it would require re-scoring all 41 arms against each conversation's own random draw.
"""
import json, pathlib, sys

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    f = root / "E05_the_space_of_compilers/A24_what_the_definition_costs/R294_the_definition_against_everything/results/full_census.json"
    rows = json.loads(f.read_text())["rows"]
    rows = {k: v for k, v in rows.items() if "ok1" in v and "ok2" in v and "c1" in v}
    if not rows:
        print("  empty population -> UNRUNNABLE"); return 2

    n_fail1 = sum(1 for r in rows.values() if not r["ok1"])
    print(f"  POSITIVE CONTROL  arms failing ① = {n_fail1}  -> "
          f"{'PASS' if n_fail1 > 0 else 'FAIL (① verdict degenerate)'}")
    if n_fail1 == 0: return 2

    # NEGATIVE CONTROL: the bar ordering must hold on every arm independently
    bars = [(r["a2"] - r["c1"][0], r["a2"] - r["c2"][0]) for r in rows.values()]
    all_ordered = all(b1 < b2 for b1, b2 in bars)
    b1s = [b for b, _ in bars]; b2s = [b for _, b in bars]
    print(f"  NEGATIVE CONTROL  bar1<bar2 on all {len(bars)} arms -> "
          f"{'PASS' if all_ordered else 'FAIL'}")
    print(f"    bar1 range [{min(b1s):.4f}, {max(b1s):.4f}]   "
          f"bar2 range [{min(b2s):.4f}, {max(b2s):.4f}]")

    viol = [k for k, r in rows.items() if r["ok2"] and not r["ok1"]]
    print(f"\n  arms satisfying ② and violating ① : {len(viol)}  {viol}")
    world = "A" if viol else "B"
    print(f"  WORLD {world} -- "
          + ("① is independent" if viol else
             "① is SUBSUMED: a2>bar2 implies a2>bar1 by transitivity, DERIVED not measured"))

    out = pathlib.Path(__file__).parent / "results/subsumption.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({
        "n_arms": len(rows), "n_fail_clause1": n_fail1,
        "n_pass2_fail1": len(viol), "bar_ordering_holds_on_all_arms": all_ordered,
        "bar1_range": [min(b1s), max(b1s)], "bar2_range": [min(b2s), max(b2s)],
        "world": world, "kind": "DERIVATION",
        "assumption": "both bars are global scalars on a common statistic (A2) and direction",
        "what_would_break_it": "a PER-PROMPT bar1, which for some conversations exceeds bar2",
    }, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
