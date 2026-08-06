#!/usr/bin/env python3
"""R839 -- the threshold curve the record never had.

See PREREGISTRATION.txt, committed before this ran.

ESTIMAND        across every cell persisting an effect and its MDE, the share whose SEPARABLE/not
                verdict changes between the 1x and 2x thresholds -- per CELL and per ROUND.
⛔ WHY          my NEXT invoked pre-registration to avoid this curve. G4 requires it: enumerate
                every defensible choice and run all of them. A pre-registration protects against
                CHOOSING after seeing; it does not forbid REPORTING the curve.
⚠ CONFOUND      R789 alone holds 416 of 1,335 cells, so a pooled share is mostly about one round.
                The per-round distribution is reported beside it and the pooled share is recomputed
                with the largest round excluded.
⚠ SCOPE         THE CELLS ARE NOT COMMENSURABLE ACROSS ROUNDS. The share counts verdict changes,
                never a pooled effect size.
KILL            CONDITIONAL on a 1.5x synthetic flipping, a 5x synthetic not flipping, and a zero
                cell never separable.
ARTIFACT        results/r839_threshold_curve.json -- per round: cells, flips, share.
"""
from __future__ import annotations
import hashlib, json, pathlib, statistics, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
RES = HERE / "results"
EFF_KEYS = ("gap", "d", "eff", "effect", "delta")


def cells(obj):
    """every dict carrying BOTH an MDE and an effect -> (effect, mde)."""
    out = []
    def walk(o):
        if isinstance(o, dict):
            low = {k.lower(): k for k in o}
            if "mde" in low:
                for e in EFF_KEYS:
                    if e in low:
                        try:
                            v, m = float(o[low[e]]), float(o[low["mde"]])
                        except (TypeError, ValueError):
                            break
                        out.append((v, m)); break
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(obj); return out


def sep(v, m, k):
    return m > 0 and abs(v) > k * m


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("\n  R839 · THE THRESHOLD CURVE THE RECORD NEVER HAD\n")
    # ---- controls --------------------------------------------------------------------------
    pc1 = sep(1.5, 1.0, 1) and not sep(1.5, 1.0, 2)          # 1.5x must FLIP
    pc2 = sep(5.0, 1.0, 1) and sep(5.0, 1.0, 2)              # 5x must NOT flip
    nc = not sep(0.0, 1.0, 1) and not sep(0.0, 1.0, 2)       # zero is never separable
    print(f"  POSITIVE  a 1.5x cell flips between 1x and 2x: {pc1}   "
          f"{'PASS' if pc1 else '⛔ FAIL — blind'}")
    print(f"  POSITIVE  a 5.0x cell does NOT flip:           {pc2}   "
          f"{'PASS' if pc2 else '⛔ FAIL — over-fires'}")
    print(f"  NEGATIVE  a zero-gap cell is never separable:  {nc}   "
          f"{'PASS' if nc else '⛔ FAIL'}")

    rows, out_of_scope = [], 0
    for f in sorted(A24.glob("R*/results/*.json")):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        cs = cells(d)
        if not cs:
            out_of_scope += 1; continue
        flips = sum(1 for v, m in cs if sep(v, m, 1) != sep(v, m, 2))
        # ⛔ v1 used f.parts[2]. A24 is an ABSOLUTE path, so parts[2] is "ivan" -- every one
        #    of the 44 rows was labelled with a home-directory component. The counts were
        #    right and the table was unreadable, which is the failure a reader meets first.
        rows.append({"round": f.relative_to(A24).parts[0], "artifact": f.name,
                     "cells": len(cs),
                     "sep_1x": sum(1 for v, m in cs if sep(v, m, 1)),
                     "sep_2x": sum(1 for v, m in cs if sep(v, m, 2)),
                     "flips": flips, "share": flips / len(cs)})
    if not rows:
        print("\n  ⛔ EMPTY POPULATION — no artifact persists an effect with its MDE. Exit 2.")
        return 2

    tot = sum(r["cells"] for r in rows); fl = sum(r["flips"] for r in rows)
    biggest = max(rows, key=lambda r: r["cells"])
    rest = [r for r in rows if r is not biggest]
    tot_x = sum(r["cells"] for r in rest); fl_x = sum(r["flips"] for r in rest)
    shares = sorted(r["share"] for r in rows)
    med = statistics.median(shares)

    print(f"\n  artifacts swept: {len(rows)}   OUT OF SCOPE (no MDE persisted): {out_of_scope}")
    print(f"  cells: {tot}   verdicts that CHANGE between 1x and 2x: {fl}  "
          f"({fl/tot:.1%} pooled)")
    print(f"  ⚠ largest artifact is {biggest['round'][:44]} with {biggest['cells']} cells;")
    print(f"     pooled share EXCLUDING it: {fl_x}/{tot_x} = {fl_x/tot_x:.1%}")
    print(f"  per-ARTIFACT share: median {med:.1%}   "
          f"min {shares[0]:.1%}   max {shares[-1]:.1%}\n")
    print(f"  {'artifact':<52}{'cells':>7}{'1x':>6}{'2x':>6}{'flips':>7}{'share':>8}")
    for r in sorted(rows, key=lambda r: -r["share"])[:14]:
        print(f"  {r['round'][:52]:<52}{r['cells']:>7}{r['sep_1x']:>6}{r['sep_2x']:>6}"
              f"{r['flips']:>7}{r['share']:>8.1%}")

    controls_ok = pc1 and pc2 and nc
    if not controls_ok:
        world, verdict = "UNVERIFIED", "a control is unfit; no share is reported"
    elif med > 0.10:
        world = "W-THRESHOLD-DEPENDENT"
        verdict = (f"the per-artifact MEDIAN share of verdicts that move is {med:.1%} -- a material "
                   f"part of the committed record depends on a choice never stated as one")
    else:
        world = "W-ROBUST"
        verdict = (f"the per-artifact median share is {med:.1%} -- the 1x/2x inconsistency is "
                   f"cosmetic and the record reads the same either way")
    print(f"\n  VERDICT: {world} -- {verdict}\n")
    print("  ⚠ CELLS ARE NOT COMMENSURABLE ACROSS ARTIFACTS. The share counts VERDICT CHANGES,")
    print("     never a pooled effect size, and no round is dropped for being small.\n")

    out = {"world": world, "verdict": verdict, "rows": rows, "n_artifacts": len(rows),
           "out_of_scope": out_of_scope, "cells": tot, "flips": fl,
           "pooled_share": fl / tot, "pooled_share_excl_largest": fl_x / tot_x,
           "largest_artifact": biggest["round"], "per_artifact_median_share": med,
           "controls": {"pos_1p5_flips": pc1, "pos_5x_stable": pc2, "neg_zero_never": nc},
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r839_threshold_curve.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r839_threshold_curve.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
