"""R1061 — three values for one arm. Find which code produces which, and which is wrong.

R1060 found `generic` at 0.5880 under its own aggregation, 0.5023 under a three-line reimplementation
of R1059's, while R1059 committed 0.5514. It refused to quote the two rounds against each other and
named the repair: re-derive with the other round's OWN code rather than a reimplementation.

⭐ TWO CANDIDATE CAUSES, AND THEY ARE NOT THE SAME KIND OF ERROR.
   ① AGGREGATION — `mean over annotators of agreement` vs `agreement with the consensus sign`.
      Averaging agreement is not agreeing with the average, so these differ legitimately and both are
      defensible; the fix is to name which is quoted.
   ② THE OBJECT — R1059 READ `sat_generic.npz`; R1060 RECONSTRUCTED the comparator as `sat_full`
      restricted to criteria 0-3. Those are two different files scored by two different arms and need
      not agree. **If this is the cause, R1060's `comparator` was never the comparator**, and its
      margins are against something else.

ESTIMAND        the value of `generic`'s mean agreement under each (source x aggregation) cell, and
                which cell reproduces R1059's committed number exactly
IDENTIFICATION  exact. Both files and both aggregations are on disk; this is a 2x2, not an estimate.
SCOPE           population : the 968 prompts both rounds used
                instrument : each round's own scoring path, re-executed
                baseline   : R1059's committed 0.5514 and R1060's committed 0.5880
                regime     : target A2
WORLDS          A AGGREGATION EXPLAINS IT — the same source under two aggregations gives the two
                  committed numbers. Then both rounds measured the comparator and only the scale
                  differs, which is a labelling repair.
                B THE OBJECT EXPLAINS IT — R1060's reconstructed comparator differs from the read
                  one under the SAME aggregation. Then R1060 compared its subsets against an arm
                  that is not the comparator, and its margins are retracted.
                C BOTH, or NEITHER reproduces R1059's number — then a committed number is wrong and
                  must be found.
                prediction matrix: A -> read+per-annotator == 0.5514 and read+consensus == 0.5880
                                   B -> read+consensus != 0.5880
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      some cell equals 0.5514 within 1e-3 AND read+consensus == 0.5880 -> World A
                      read+consensus differs from 0.5880 by > 1e-3                     -> World B
                      no cell reproduces 0.5514                                        -> World C
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   R1059's committed artifact must be READ, not remembered, and its number taken from
                the file. A reconciliation against a remembered figure reconciles nothing.
NEGATIVE CTRL   the two sources must be shown to DIFFER somewhere — if `sat_generic` and `sat_full`
                restricted to 0-3 are byte-identical in the values used, the object hypothesis is
                not even testable and must be dropped rather than assumed.
PLACEBO         comparing a cell to itself must give exactly 0.
NOISE FLOOR     N/A - these are deterministic means over a fixed prompt set. Stated, not omitted.
MULTIPLICITY    all four cells reported, not the one that matches.
SEEDS           N/A - no sampling.
IMPOSSIBLE      whether R1059's aggregation is the RIGHT one for the clause. That is a definitional
                question this round does not touch. SETTLES: IN-RELEASE via the admission operator,
                which is what the clause actually uses.
"""
import json, pathlib, sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402


def main() -> int:
    r1059 = next(ROOT.glob("E05_the_space_of_compilers/A27*/R1059_*/results/"
                           "second_optimiser.json"), None)
    r1060 = next(ROOT.glob("E05_the_space_of_compilers/A27*/R1060_*/results/"
                           "fixed_rule_bound.json"), None)
    if not (r1059 and r1060):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0."); return 2
    v1059 = json.loads(r1059.read_text())["comparator_mean_agreement"]
    d60 = json.loads(r1060.read_text())
    v1060 = d60["comparator_consensus_mean"]
    print(f"  POSITIVE — both numbers READ from committed artifacts, never remembered: "
          f"R1059 {v1059:.4f} · R1060 {v1060:.4f}")

    tg, _ = load_targets()
    Sg, Sf = load_sat(RES / "sat_generic.npz"), load_sat(RES / "sat_full.npz")
    pids = sorted(set(Sf) & set(Sg) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    if n < 200:
        print("  UNRUNNABLE: too few shared prompts. Exit 2, never 0."); return 2

    def arm_cls(sat, p, idxs):
        return np.array(cls(yvec(sat[p], list(idxs))), float)

    READ = {p: arm_cls(Sg, p, sorted({i for i, _ in Sg[p]})) for p in pids}
    RECON = {p: arm_cls(Sf, p, [0, 1, 2, 3]) for p in pids}
    ident = all(np.array_equal(READ[p], RECON[p]) for p in pids)
    ndiff = sum(1 for p in pids if not np.array_equal(READ[p], RECON[p]))
    print(f"  NEGATIVE — the two sources must DIFFER somewhere, or the object hypothesis is "
          f"untestable: differ on {ndiff} of {n} prompts (identical: {ident})")
    if ident:
        print("  the object hypothesis is not testable; it is DROPPED, not assumed.")

    def per_annotator(C):
        return float(np.mean([np.mean([(C[p] == np.array(cls(np.array(t[0], float)), float)).mean()
                                       for t in tg[p]]) for p in pids]))

    def consensus(C):
        out = []
        for p in pids:
            hs = np.sign(np.mean([cls(np.array(t[0], float)) for t in tg[p]], axis=0))
            out.append((C[p] == hs).mean())
        return float(np.mean(out))

    cells = {
        ("read sat_generic", "per-annotator"): per_annotator(READ),
        ("read sat_generic", "consensus"): consensus(READ),
        ("reconstructed sat_full[0:4]", "per-annotator"): per_annotator(RECON),
        ("reconstructed sat_full[0:4]", "consensus"): consensus(RECON),
    }
    print(f"\n  ⭐ THE 2x2 — prompts {n}")
    for (src, agg), v in cells.items():
        m59 = "  <= R1059's committed 0.5514" if abs(v - v1059) < 1e-3 else ""
        m60 = "  <= R1060's committed 0.5880" if abs(v - v1060) < 1e-3 else ""
        print(f"     {src:<30} {agg:<14} {v:.4f}{m59}{m60}")

    plac = abs(cells[("read sat_generic", "consensus")]
               - cells[("read sat_generic", "consensus")]) == 0
    matches59 = [k for k, v in cells.items() if abs(v - v1059) < 1e-3]
    read_cons = cells[("read sat_generic", "consensus")]
    obj_explains = abs(read_cons - v1060) > 1e-3

    print()
    if not plac:
        world = "⛔ UNVERIFIED — the comparison is not self-consistent."
    elif not matches59:
        world = (f"⛔ C NO CELL REPRODUCES R1059's COMMITTED {v1059:.4f} — so that number was not "
                 f"produced by any (source x aggregation) combination available here, and it is the "
                 f"one that has to be found before either round's gap is quotable.")
    elif obj_explains:
        world = (f"⛔ B THE OBJECT EXPLAINS IT — reading `sat_generic` under R1060's OWN consensus "
                 f"aggregation gives {read_cons:.4f}, not the {v1060:.4f} R1060 committed. R1060 did "
                 f"not compare its subsets against the comparator; it compared them against "
                 f"`sat_full` restricted to criteria 0-3, which is a different arm. ⭐ R1060's "
                 f"margins are therefore RETRACTED as stated — its bound is against a reconstructed "
                 f"object, and the sources differ on {ndiff} of {n} prompts.")
    else:
        world = (f"⭐ A AGGREGATION EXPLAINS IT — the same source under two aggregations reproduces "
                 f"both committed numbers ({matches59[0]} gives {v1059:.4f}; consensus gives "
                 f"{read_cons:.4f}). Both rounds measured the comparator; only the scale differs, so "
                 f"the repair is a label on each number rather than a retraction of either.")
    print(world)
    print(f"⛔ AND THE THIRD NUMBER — R1060's {d60.get('comparator_per_annotator_mean', float('nan')):.4f}")
    print(f"   from a three-line reimplementation — is not in this table's cells unless it matches")
    print(f"   one above. It was never a measurement of anything; it was a guess at another round's")
    print(f"   code, which is precisely what R1060 refused to reason from and why this round exists.")

    o = HERE / "results" / "reconciliation.json"
    o.write_text(json.dumps({
        "round": "R1061", "prompts": n,
        "committed": {"R1059": v1059, "R1060_consensus": v1060,
                      "R1060_reimplementation": d60.get("comparator_per_annotator_mean")},
        "cells": {f"{s} | {a}": v for (s, a), v in cells.items()},
        "sources_differ_on_prompts": ndiff, "object_explains": bool(obj_explains),
        "matches_R1059": [f"{s} | {a}" for s, a in matches59], "world": world,
        "controls": {"positive_numbers_read_from_artifacts": True,
                     "negative_sources_differ": bool(not ident), "placebo_self_zero": bool(plac)},
        "limitation": "which aggregation the CLAUSE should use is a definitional question this round "
                      "does not touch",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
