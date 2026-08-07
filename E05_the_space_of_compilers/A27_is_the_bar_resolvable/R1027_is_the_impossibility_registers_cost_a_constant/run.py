#!/usr/bin/env python3
"""R1027 — `15,488 judge calls` decides what this arc calls impossible. It has never been re-derived.

The figure appears in `DEFINITION.md` twice and in four rounds' impossibility registers, always as a
CONSTANT: "a new comparator costs 15,488 judge calls". Nobody re-derived it. That is the "wall never
checked" shape — a permanent limit asserted from a citation, where the falsifying arithmetic sits in
the committed files.

⛔ THE DERIVATION, FROM THE SOURCE, BEFORE ANY COUNTING. `covalx/judge.py:151` is
   `build_prompt(criterion, reply)` — ONE call scores ONE (criterion, reply) pair. So the cost of
   scoring an arm is `prompts × replies × k`, and it is LINEAR IN k. That is forced by the call
   signature, not measured. What is NOT forced, and is measured below, is the value of `replies`, the
   `k` of each committed arm, and therefore which arm the quoted number actually describes.

⚠ AND I ALMOST ADOPTED THE WRONG READING FROM MY OWN REPO. `STATEMENT.md:2085` says "the pool's
   15,488 instances are 16 criteria seen 968 times", which reads as 968 × 16 and would make the figure
   the cost of a SIXTEEN-criterion pool. 968 × 16 = 15,488 is arithmetically true, so the sentence is
   self-consistent and wrong for this purpose: it describes a different object (a criterion-instance
   pool), not an arm's judge cost. A number that factorises two ways is a number to check, not quote.

ESTIMAND        the marginal judge-call count to score one new comparator, as a function of its
                criterion count k; and the UNIT those calls are denominated in.
IDENTIFICATION  exact. One call per (criterion, reply) is read from the judge's signature; cell counts
                and per-arm k are in the committed artifacts.
SCOPE           population : every scoreable arm with a committed selection file
                instrument : `covalx.judge.build_prompt` (one call per criterion×reply), local CUDA
                baseline   : the quoted constant, 15,488 · regime : 968 prompts
WORLDS          A THE WALL IS A CONSTANT — cell counts are ~15,488 for every arm regardless of k.
                  Then the register is right and a new comparator costs what it says.
                B THE WALL SCALES WITH k — cells = prompts × replies × k, so the quoted figure is ONE
                  arm's cost quoted as universal. Then the register overstates the cost of small-k
                  comparators and UNDERSTATES the cost of a member the certified set already contains,
                  and "N/A, would require 15,488 calls" is false in both directions.
                prediction matrix: A -> cells constant across arms of different k; residual ~0 for a
                                        constant model.
                                   B -> cells / (prompts × replies) equals k EXACTLY, arm by arm.
                ⚠ ONTOLOGICAL: A makes the constraint a fixed overhead, B makes it a per-criterion
                  price. They imply different repairs — accept the wall, or pick a smaller k.
KILL            pre-registered and CONDITIONAL:
                  if the identity's positive control fires and the variable-k negative control fails
                  the identity as it must:
                      every fixed-k arm satisfies cells == P × R × k EXACTLY -> World B
                      else                                                   -> World A
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the identity `cells == prompts × replies × k` must hold with residual EXACTLY 0 for
                every arm whose selection has a single k. It can fail: a batched judge, a cached
                criterion, or a per-prompt reply count would all break it.
                ⚠ and it must FAIL where it should — see the negative control, which is the g=0 arm.
NEGATIVE CTRL   an arm whose k VARIES per prompt (`coval_core`) must NOT satisfy the identity for any
                single integer k. If it did, the identity would be reading file size rather than k,
                and would confirm itself on anything.
PLACEBO         the residual `cells − P × R × k` must be exactly 0, not merely small, for fixed-k arms.
NOISE FLOOR     none needed — these are exact counts, not estimates. Stated rather than omitted.
MULTIPLICITY    every scoreable arm is tested, and the non-conforming ones are listed in full.
SEEDS           N/A — the quantity is deterministic. Stated rather than silently skipped.
IMPOSSIBLE      the WALL-CLOCK cost of those calls. The judge loads to CUDA (`device_map="cuda"`) at
                batch 32, so the unit is local GPU time and not paid API spend — but this round does
                not run it and does not claim a runtime. What that would require: one timed batch.
"""
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat  # noqa: E402

QUOTED = 15488


def main() -> int:
    src = ROOT / "covalx" / "judge.py"
    if not src.exists():
        print("  UNRUNNABLE: covalx/judge.py missing, so the call granularity cannot be read. "
              "Exit 2, never 0.")
        return 2
    sig = [l.strip() for l in src.read_text().splitlines()
           if l.strip().startswith("def build_prompt")]
    print(f"  ⛔ DERIVATION, read from the source — {src.relative_to(ROOT)}:\n     {sig[0]}")
    print( "     ONE call scores ONE (criterion, reply) pair ⇒ cost = prompts × replies × k, LINEAR")
    print( "     in k. Forced by the signature. What is measured below is `replies`, each arm's k,")
    print( "     and therefore WHICH ARM the quoted constant actually describes.")

    arms = sorted({f.stem[4:] for d in (RES, NEW) if d.exists() for f in d.glob("sat_*.npz")})
    rows, bad_pos, fixed_k = [], [], []
    varying = []
    for a in arms:
        f = next((d / f"sat_{a}.npz" for d in (RES, NEW) if (d / f"sat_{a}.npz").exists()), None)
        try:
            S = load_sat(f)
        except Exception:
            continue
        cells = int(sum(len(v) for v in S.values()))
        P = len(S)
        self_ = next((d / f"core_{a}.json" for d in (RES, NEW)
                      if (d / f"core_{a}.json").exists()), None)
        ks = None
        if self_:
            try:
                sel = json.loads(self_.read_text())
                sizes = {len(v) for v in sel.values() if v}
                ks = sorted(sizes)
            except Exception:
                ks = None
        # replies per prompt: cells / (k * P) when k is single-valued
        rows.append({"arm": a, "prompts": P, "cells": cells, "k": ks})
        if ks and len(ks) == 1:
            fixed_k.append((a, P, cells, ks[0]))
        elif ks and len(ks) > 1:
            varying.append((a, P, cells, ks))

    if not fixed_k:
        print("  UNRUNNABLE: no fixed-k arm found — an empty population must not pass. Exit 2.")
        return 2

    # replies is inferred from ONE arm and then required to hold for ALL of them
    a0, P0, c0, k0 = fixed_k[0]
    R = c0 / (P0 * k0)
    R_int = int(round(R))
    print(f"\n  replies per prompt, inferred from `{a0}` then REQUIRED of every other arm: "
          f"{c0} / ({P0} × {k0}) = {R:.4f} → {R_int}")

    print(f"\n  POSITIVE — the identity `cells == prompts × replies × k` must hold with residual "
          f"EXACTLY 0\n     for all {len(fixed_k)} fixed-k arms:")
    print(f"     {'arm':<22}{'k':>4}{'prompts':>9}{'cells':>9}{'P×R×k':>9}{'residual':>10}")
    shown = 0
    for a, P, cells, k in fixed_k:
        pred = P * R_int * k
        res = cells - pred
        if res != 0:
            bad_pos.append((a, k, cells, pred, res))
        if shown < 6 or res != 0:
            print(f"     {a:<22}{k:>4}{P:>9}{cells:>9}{pred:>9}{res:>10}")
            shown += 1
    print(f"     … {len(fixed_k)} arms tested · residual != 0 for {len(bad_pos)}: "
          f"{'PASS' if not bad_pos else '⛔ FAIL ' + str(bad_pos[:4])}")

    print(f"\n  NEGATIVE — an arm whose k VARIES must NOT satisfy the identity for any single "
          f"integer k,\n     or the identity is reading file size rather than k:")
    neg_ok = True
    for a, P, cells, ks in varying[:4]:
        q = cells / (P * R_int)
        ok = abs(q - round(q)) > 1e-9
        neg_ok &= ok
        print(f"     {a:<22}k∈{str(ks)[:24]:<26}cells/(P×R) = {q:.4f}  "
              f"{'non-integer as required' if ok else '⛔ integer — the identity self-confirms'}")
    if not varying:
        print("     ⚠ NO variable-k arm found, so this control did not run. That is UNVERIFIED, "
              "not a pass.")
        neg_ok = False

    # ---------- what the quoted constant actually is ----------
    # ⚠ THE FIRST VERSION OF THIS TABLE COLLAPSED (k, cost) ACROSS ARMS WITH DIFFERENT PROMPT
    #   COUNTS, so it printed TWO k=4 rows — 6368 and 15488 — and attached "THE QUOTED FIGURE" to
    #   one of them arbitrarily. 6368 = 398 x 4 x 4 is a partial-coverage arm. Cost depends on
    #   BOTH factors, and a table that hides one of them is a verdict string wearing a table's
    #   clothes. Full coverage and partial coverage are now separated.
    PFULL = max(P for _a, P, _c, _k in fixed_k)
    match = sorted({(k, PFULL * R_int * k) for _a, P, _c, k in fixed_k if P == PFULL})
    partial = sorted({(P, k, P * R_int * k) for _a, P, _c, k in fixed_k if P != PFULL})
    print(f"\n  ⭐ WHAT `{QUOTED}` ACTUALLY IS — cost by criterion count at FULL coverage "
          f"({PFULL} prompts × {R_int} replies):")
    for k, cost in match:
        tag = ("   <- THE QUOTED FIGURE" if cost == QUOTED else
               "   <- `genericpool16`, ALREADY a certified comparator" if k == 16 else "")
        print(f"     k={k:<4}{cost:>9} judge calls{tag}")
    if partial:
        print(f"     ⚠ and {len(partial)} PARTIAL-coverage cell(s), which is the second factor: "
              + ", ".join(f"{P}p × k={k} = {c}" for P, k, c in partial))
    is_k4 = any(cost == QUOTED and k == 4 for k, cost in match)
    k1 = next((c for k, c in match if k == 1), None)
    pool16 = next((cost for k, cost in match if k == 16), None)

    print()
    if bad_pos or not neg_ok:
        world = "UNVERIFIED — a control did not fire; no verdict is admissible"
    elif len(match) > 1:
        world = (f"⭐ B THE WALL SCALES WITH k — cells = prompts × replies × k EXACTLY for all "
                 f"{len(fixed_k)} fixed-k arms, residual 0. `{QUOTED}` is the cost of a "
                 f"{'k=4' if is_k4 else '?'} arm quoted as universal. A k=1 prompt-blind comparator "
                 f"costs {k1} calls — {QUOTED/k1:.0f}x cheaper — while "
                 f"`genericpool16`, ALREADY IN the certified set, cost {pool16} — "
                 f"{pool16/QUOTED:.0f}x MORE than the figure the register quotes.")
    else:
        world = (f"⭐ A THE WALL IS A CONSTANT — every arm costs the same regardless of k, so the "
                 f"register's figure is right as stated.")
    print(world)
    print(f"⛔ AND THE LINEARITY IS DERIVED, NOT MEASURED. It follows from `build_prompt(criterion, "
          f"reply)`.\n   What the counts BUY is the constants — replies = {R_int}, and which arm the "
          f"quoted number is.\n   The identity could still have failed (a batched judge, a cached "
          f"criterion, a per-prompt reply\n   count would each break it), so the residual-0 result "
          f"is a measurement of those constants.")
    print(f"⚠ AND THE REGISTER MIS-STATES THE CURRENCY AS WELL AS THE AMOUNT. The judge loads with "
          f"`device_map=\"cuda\"` at batch 32 — the unit is LOCAL GPU TIME, not paid API spend. "
          f"This round\n   does NOT run it and claims NO runtime; what that would require is one "
          f"timed batch.")
    print(f"⚠ WHAT DOES NOT CHANGE: R1026's finding. A cheaper comparator still has to be BUILT and "
          f"be\n   prompt-blind, and no such arm exists in the release. The cost was never the only "
          f"obstacle —\n   it was the one the register named, and it named it wrongly.")

    out = HERE / "results" / "cost_by_k.json"
    out.write_text(json.dumps({
        "round": "R1027", "quoted_constant": QUOTED,
        "derivation": {"source": "covalx/judge.py build_prompt(criterion, reply)",
                       "statement": "one judge call per (criterion, reply) pair, so cost = "
                                    "prompts x replies x k, linear in k", "label": "DERIVED"},
        "misreading_avoided": "STATEMENT.md:2085 reads 15,488 as 968 x 16 criterion-instances; that "
                              "is a different object and 968x16 is a coincidence of factorisation",
        "replies_per_prompt": R_int, "n_fixed_k_arms": len(fixed_k),
        "identity_violations": bad_pos, "negative_control_ok": bool(neg_ok),
        "variable_k_arms": [{"arm": a, "cells": c, "ks": ks} for a, _P, c, ks in varying],
        "cost_by_k_full_coverage": [{"k": k, "judge_calls": c} for k, c in match],
        "partial_coverage_cells": [{"prompts": P, "k": k, "judge_calls": c}
                                   for P, k, c in partial],
        "full_coverage_prompts": PFULL,
        "quoted_is_k4": bool(is_k4), "genericpool16_cost": pool16,
        "unit": "local CUDA judge calls, batch 32 — not paid API spend; no runtime measured here",
        "world": world,
        "limitation": "the cost was never the only obstacle; a comparator must also be prompt-blind, "
                      "and R1026 showed none beyond the two exists in this release",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
