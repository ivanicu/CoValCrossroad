#!/usr/bin/env python3
"""R1046 — a headline asserts; an artifact measures. Is every headline number IN its own artifact?

R1045 established that every artifact-loading round reads VALUES rather than mere existence, and
closed by naming what that does NOT license: R1043 read values throughout and still reported an exit
code as its finding. The distinguishing question is not *did the round open the object* but *is the
number it put in its headline the number it measured*.

⭐ THE HEADLINE IS THE HIGHEST-RISK SENTENCE IN A ROUND, for the same reason §4 gives for the closing
   line: it is written last, it is what a later round cites, and no control is attached to it.

ESTIMAND        the share of headline numbers, over rounds R1022-R1045, that are NOT present as a
                numeric value in that round's own results/*.json
IDENTIFICATION  ⚠ PARTIAL, AND THE LIMIT IS NAMED BEFORE THE METHOD. A headline number can be
                legitimately absent from the artifact by being a ROUND ID (R1044), a SECTION or
                VERSION marker, or a quantity the round quotes from an EARLIER round rather than
                measuring. Round ids are excluded lexically (an `R` immediately before the digits).
                The other two are not separable from a true miss by any rule available here, so the
                measured quantity is an UPPER BOUND on unbacked headline numbers, never a point.
SCOPE           population : R1022-R1045 READMEs, first heading line only
                instrument : literal numeric containment in the round's own results/*.json,
                             tolerance 1e-9 relative, plus list LENGTHS as backing values
                baseline   : R1045's finding that every such round reads artifact values
                regime     : one arc, one window, headline sentences only
WORLDS          A THE HEADLINE IS DOWNSTREAM OF THE ARTIFACT — nearly every headline number is in the
                  round's own JSON, so the assertion surface is anchored and R1043's error was about
                  WHICH value was read, not whether one was.
                B THE HEADLINE FLOATS — a substantial share of headline numbers appear nowhere in the
                  artifact, so the round's most-cited sentence is composed rather than read, and the
                  anchoring gate that guards DEFINITION.md has no counterpart guarding READMEs.
                prediction matrix: A -> unbacked share low, and the misses are quotes of prior rounds
                                   B -> unbacked share high, spread across rounds
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      unbacked share >= 0.25 -> World B
                      <= 0.10                -> World A
                      otherwise               -> report, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ the checker must find a number KNOWN to be in an artifact. R1045's headline says
                `n = 1`, and its JSON carries a one-element `rc_without_stdout`; more decisively, a
                value drawn AT RUNTIME from each artifact must be reported as backed. That second
                form is the real control: it cannot be satisfied by a rule that returns "backed" for
                everything, because the NEGATIVE below shares its machinery.
NEGATIVE CTRL   a value constructed to be absent (an artifact value + a large irrational offset) must
                be reported UNBACKED for every round. If both controls cannot fire on the same round,
                the checker discriminates nothing.
PLACEBO         a headline with NO numbers contributes no denominator — excluded, not scored 0.
NOISE FLOOR     the tolerance is stated (1e-9 relative) and the count of numbers that match only via
                a list LENGTH is reported separately, since that is the loosest backing rule.
MULTIPLICITY    every round reported, backed and unbacked, not only the failures.
SEEDS           N/A - deterministic over committed text.
IMPOSSIBLE      whether an unbacked number is WRONG. Absence from the artifact means the headline is
                not re-derivable from the round's own persisted output; it does not mean the value is
                false, and a number quoted from an earlier round is unbacked here and correct there.
                SETTLES: IN-RELEASE - each unbacked number can be resolved by reading the round it
                cites, at the cost of one reading per miss.
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")
RID = re.compile(r"R\d+")


def numbers_in(obj, out):
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        out.add(float(obj)); return
    if isinstance(obj, str):
        for m in NUM.finditer(obj):
            out.add(float(m.group(1)))
        return
    if isinstance(obj, list):
        out.add(float(len(obj)))
        for v in obj:
            numbers_in(v, out)
        return
    if isinstance(obj, dict):
        for v in obj.values():
            numbers_in(v, out)


def backed(x, pool):
    return any(abs(x - p) <= 1e-9 * max(1.0, abs(x)) for p in pool)


def main() -> int:
    rows = []
    for d in sorted(A27.glob("R10*")):
        m = re.match(r"R(\d+)", d.name)
        if not (m and 1022 <= int(m.group(1)) <= 1045):
            continue
        rm, js = d / "README.md", sorted((d / "results").glob("*.json"))
        if not (rm.exists() and js):
            continue
        # ⛔⛔ SPECIFICATION CURVE, AND THE FIRST CELL NEARLY CARRIED THE ROUND ALONE. Scoring
        #   the H1 line only admitted 4 of the 24 rounds and 7 numbers — because most headlines are
        #   prose, and a round's findings live in its RESULT TABLE. My controls passed anyway: they
        #   test the containment RULE and never ask whether the population is the one being claimed
        #   about. §4: name the instrument's unit and the claim's unit and require them EQUAL. The
        #   instrument's unit was `first heading line`; the claim's unit is `numbers this round
        #   asserts`. They are not equal, so BOTH cells are computed and both are reported.
        text = rm.read_text()
        cells = {"h1": text.split("\n", 1)[0], "body": text}
        pool = set()
        for j in js:
            numbers_in(json.loads(j.read_text()), pool)
        got = {}
        for cell, src in cells.items():
            want = [float(g) for g in NUM.findall(RID.sub(" ", src))]
            got[cell] = want
        if not any(got.values()):                        # PLACEBO: no numbers -> no denominator
            continue
        rows.append((m.group(0), got, pool))

    if not rows:
        print("  UNRUNNABLE: an empty population must not pass. Exit 2, never 0."); return 2

    # ---------- controls, on the same machinery the verdict uses ----------
    pos = all(backed(sorted(p)[len(p) // 2], p) for _r, _w, p in rows)
    neg = all(not backed(sorted(p)[len(p) // 2] + 987654.321, p) for _r, _w, p in rows)
    print(f"  POSITIVE — a value drawn AT RUNTIME from each artifact must read as backed, in all "
          f"{len(rows)} rounds: {pos}")
    print(f"  NEGATIVE — that same value plus a large offset must read as UNBACKED everywhere: {neg}")
    if not (pos and neg):
        print("  the checker does not discriminate. Exit 2, never 0."); return 2

    per = {}
    detail = []
    for rid, got, pool in rows:
        rec = {"round": rid}
        for cell, want in got.items():
            bad = [x for x in want if not backed(x, pool)]
            tot, miss = per.get(cell, (0, 0))
            per[cell] = (tot + len(want), miss + len(bad))
            rec[cell] = {"n": len(want), "unbacked": bad}
        detail.append(rec)

    print(f"\n  ⭐ SPECIFICATION CURVE — the cell is the choice of what counts as an assertion:")
    shares = {}
    for cell in ("h1", "body"):
        tot, miss = per[cell]
        shares[cell] = miss / tot if tot else None
        contrib = sum(1 for _r, g, _p in rows if g[cell])
        print(f"     {cell:5}  rounds contributing {contrib:>2} of {len(rows)} · numbers {tot:>4} · "
              f"UNBACKED {miss:>4} · share {shares[cell]:.3f}")

    share = shares["body"]
    print()
    if share >= 0.25:
        world = (f"⭐ B THE HEADLINE FLOATS — on the body cell, {share:.1%} of the numbers a round "
                 f"asserts appear nowhere in its own artifact, so a round's most-cited text is "
                 f"composed rather than read, and no gate guards READMEs the way anchoring guards "
                 f"DEFINITION.md.")
    elif share <= 0.10:
        world = (f"⭐ A THE TEXT IS DOWNSTREAM OF THE ARTIFACT — on the body cell {share:.1%} are "
                 f"unbacked, so the assertion surface is anchored.")
    else:
        world = (f"⭐ NEITHER BAND, AND THE TWO CELLS DISAGREE BY DESIGN — h1 {shares['h1']:.3f} on "
                 f"{per['h1'][0]} numbers, body {shares['body']:.3f} on {per['body'][0]}. The h1 cell "
                 f"admits only {sum(1 for _r, g, _p in rows if g['h1'])} of {len(rows)} rounds, so it "
                 f"was never a measurement of this arc — it was a measurement of the four rounds that "
                 f"happen to put a number in a heading.")
    print(world)
    print(f"⛔ THE FIRST CELL ALONE WOULD HAVE CARRIED A WORLD VERDICT OFF {per['h1'][0]} NUMBERS.")
    print(f"   Its controls passed — they test the containment RULE, never whether the population is")
    print(f"   the one the claim is about. That is §4's search-instrument row with the positive")
    print(f"   control in place: a control asks CAN THIS SEE, and never IS WHAT IT SEES THE THING.")
    # ⭐ TIGHTENING THE BOUND: an unbacked number that IS in some OTHER round's artifact is
    #   plausibly a quote — correct practice. One present in NO artifact in this arc is the strong
    #   form, and that residue is what the bound above was hiding.
    arc = set()
    for _r, _g, pl in rows:
        arc |= pl
    strong = elsewhere = 0
    for _rid, got, pool in rows:
        for x in got["body"]:
            if backed(x, pool):
                continue
            if backed(x, arc):
                elsewhere += 1
            else:
                strong += 1
    lo = strong / per["body"][0]
    print(f"⛔ AND BOTH CELLS ARE UPPER BOUNDS. Splitting the {per['body'][1]} unbacked numbers by")
    print(f"   whether they appear in ANY round's artifact in this arc: {elsewhere} do — plausibly")
    print(f"   quoted, which is correct practice — and {strong} appear in NO artifact here at all.")
    print(f"   ⭐ SO THE BRACKET IS [{lo:.3f}, {share:.3f}], and the LOWER end is the one that")
    print(f"   cannot be explained away by citation. Both ends are reported; neither is a point.")

    out = HERE / "results" / "headline_backing.json"
    out.write_text(json.dumps({
        "round": "R1046", "population": len(rows),
        "cells": {c: {"numbers": per[c][0], "unbacked": per[c][1],
                      "share_upper_bound": shares[c],
                      "rounds_contributing": sum(1 for _r, g, _p in rows if g[c])}
                  for c in ("h1", "body")},
        "controls": {"positive_runtime_value_backed": bool(pos),
                     "negative_offset_value_unbacked": bool(neg)},
        "unbacked_split": {"present_in_another_round_artifact": elsewhere,
                           "present_in_no_artifact_in_arc": strong,
                           "bracket": [lo, share]},
        "detail": detail, "world": world,
        "limitation": "upper bound only: a number quoted from an earlier round is unbacked here and "
                      "correct there, and no rule separates that from a true miss",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
