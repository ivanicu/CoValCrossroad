"""r19 -- Which donor defines the generic-quality floor, and how much does it matter?

Pure re-analysis of r10's stored numbers. No model, no GPU, no new judgements.

r04's headline subtracts a shuffled-rubric arm to isolate "generic response quality
any rubric earns for free", and that arm used a RANDOM other prompt. r10 also graded
a nearest-topic donor and a farthest donor and filed them as a robustness check.
They are not a robustness check -- they are the same quantity measured against three
different floors, and the answer moves by more than 2x across them.

The 0.8B cell is excluded from the summary: its self accuracy is 0.5405, barely
above chance, so its decomposition is noise and averaging it in would hide the
spread rather than show it.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"

CHANCE = 0.5
DEGENERATE_SELF = 0.55   # a cell whose own accuracy is below this cannot be decomposed


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path,
                    default=_ROOT / "02_attribution_under_attack/r10_attribution_robustness/results/a10_attribution.json")
    ap.add_argument("--out", type=Path, default=_RES / "r19_floor_choice.json")
    a = ap.parse_args()

    if not a.source.exists():
        raise SystemExit(f"missing {a.source} -- run 02_attribution_under_attack/r10_attribution_robustness/run.py first")
    cells = json.loads(a.source.read_text())["cells"]

    print("=== r10's four donors, read as a decay curve in topical distance ===\n")
    print(f"{'cell':16s} {'self':>7} {'near':>7} {'random':>7} {'far':>7}   | above-chance retained")
    keep, per = [], {}
    for name, c in cells.items():
        ac = {k: c[k] - CHANCE for k in ("real", "near", "random", "far")}
        degenerate = c["real"] < DEGENERATE_SELF
        ret = {k: (ac[k] / ac["real"] if ac["real"] > 1e-9 else float("nan")) for k in ac}
        per[name] = {"self": c["real"], "near": c["near"], "random": c["random"],
                     "far": c["far"], "degenerate": bool(degenerate),
                     "vs_near": c["real"] - c["near"],
                     "vs_random": c["real"] - c["random"],
                     "vs_far": c["real"] - c["far"]}
        flag = "  <- EXCLUDED: self barely above chance" if degenerate else ""
        print(f"{name:16s} {c['real']:>7.4f} {c['near']:>7.4f} {c['random']:>7.4f} "
              f"{c['far']:>7.4f}   | near {ret['near']:>5.0%}  random {ret['random']:>5.0%}"
              f"  far {ret['far']:>5.0%}{flag}")
        if not degenerate:
            keep.append(name)

    if not keep:
        raise SystemExit("every cell is degenerate; nothing decomposable")

    print(f"\n=== attribution against each floor ({len(keep)} usable cells) ===\n")
    print(f"{'cell':16s} {'vs near':>9} {'vs random':>11} {'vs far':>9}   far/near")
    for name in keep:
        p = per[name]
        print(f"{name:16s} {p['vs_near']:>9.4f} {p['vs_random']:>11.4f} {p['vs_far']:>9.4f}"
              f"   {p['vs_far']/max(p['vs_near'],1e-9):>8.2f}x")

    m = {k: float(np.mean([per[n][k] for n in keep]))
         for k in ("vs_near", "vs_random", "vs_far")}
    span = m["vs_far"] / max(m["vs_near"], 1e-9)
    self_ac = float(np.mean([per[n]["self"] - CHANCE for n in keep]))
    share = {k: m[k] / self_ac for k in m}

    print(f"\n  mean vs near   = {m['vs_near']:.4f}   -> prompt-specific share ~{share['vs_near']:.0%}"
          f"   strictest floor")
    print(f"  mean vs random = {m['vs_random']:.4f}   -> ~{share['vs_random']:.0%}"
          f"   <- what the README reported")
    print(f"  mean vs far    = {m['vs_far']:.4f}   -> ~{share['vs_far']:.0%}   loosest floor")
    print(f"\n  span across floor choice: {span:.2f}x")
    print("  -> the generic floor is BRACKETED, not measured. Neither endpoint is clean:")
    print("     far is chosen by argmin similarity, so a judge that simply refuses it")
    print("     understates the floor; near shares topic, so it overstates it.")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"per_cell": per, "usable_cells": keep, "means": m,
         "prompt_specific_share": share, "span": span,
         "note": "attribution depends on which donor defines the generic-quality "
                 "floor; the reported figure used the random donor, which retains "
                 "47-60% of the self signal and is therefore not a clean floor"},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
