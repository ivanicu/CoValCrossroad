#!/usr/bin/env python3
"""R513 — the size of my own assurance surface.

ESTIMAND (before method): fraction of verdict-asserting gates declaring a positive control.
POPULATION: run_all.discover() — ASKED from the harness, never re-globbed.
INSTRUMENT: case-insensitive source search. Sound only for ABSENCE of a declaration.
BASELINE: n/a, census.  REGIME: the surface at this sha.
POSITIVE CONTROL: discover() must exclude a known non-gate (it excludes 8 names + 2 prefixes).
PRE-REGISTERED KILL: <25% declaring neither control kills world B.
IMPOSSIBLE HERE: whether each gate's control FIRES — needs 45 controls executed and observed,
  which is 45 small experiments, not one scan. Named, not marked planned.
"""
import importlib.util, json, pathlib, re, subprocess, sys

def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    spec = importlib.util.spec_from_file_location("ra", root / "assurance/run_all.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    gates = m.discover()
    if not gates:
        print("  empty population -> UNRUNNABLE"); return 2
    raw = [p for p in (root / "assurance").glob("*.py")]
    print(f"  POSITIVE CONTROL discover() excludes non-gates: "
          f"raw={len(raw)} discovered={len(gates)} -> "
          f"{'PASS' if len(gates) < len(raw) else 'FAIL'}")
    POS = re.compile(r"positive[ _]control", re.I)
    NEG = re.compile(r"negative[ _]control|placebo|sham", re.I)
    c = {"both": 0, "pos": 0, "neg": 0, "neither": 0}
    for g in gates:
        s = g.read_text(); p, n = bool(POS.search(s)), bool(NEG.search(s))
        c["both" if p and n else "pos" if p else "neg" if n else "neither"] += 1
    frac = c["neither"] / len(gates)
    for k, v in c.items(): print(f"    {k:<10}{v:>3}  ({v/len(gates):.0%})")
    world = "B" if frac >= 0.25 else "A"
    print(f"  neither = {frac:.0%} -> WORLD {world}")
    out = pathlib.Path(__file__).parent / "results/control_census.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"n_gates": len(gates), "counts": c,
                               "frac_neither": round(frac, 4), "world": world,
                               "bound": "upper -- >=2 of the flagged gates currently FAIL, "
                                        "so they demonstrably can return non-zero"}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
