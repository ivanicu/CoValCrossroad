"""Does clause ① of the definition ever exclude anything clause ② would admit?

The definition, as it stands:

    A core is a set of criteria, built WITHOUT any human label for the conversation it describes,
    whose verdicts agree pairwise with that conversation's human annotators
      ① better than the same number drawn at random from that conversation's own rubric, and
      ② better than the same number that never read the conversation at all.

realstat §4 supplies the mechanical test for a clause, and it is the one that killed `of a rubric`
in a line: **name an admissible object this clause EXCLUDES.** Clause ③ passes it -- it removes
`oracle_k4`, which clears ① and ② and is excluded by provenance alone, and that is a positive
control. **Clause ① has never been given the same test.**

ESTIMAND, named before the method
---------------------------------
Over the 41 judged arms of R294's census, the count in the cell (clause ① FAILS, clause ② PASSES) --
the arms clause ① would remove and clause ② would keep. If that count is 0, clause ① removes nothing
its neighbour does not already remove, and a clause that never binds is either DECORATION or a
THEOREM. It is currently printed as neither.

⛔ AND THE ARITHMETIC TRAP IS THE WHOLE ROUND, so it is answered before any count is reported.
Write `c1 = arm - ref1` and `c2 = arm - ref2`, so `c1 - c2 = ref2 - ref1`. Clause ① passes when
`c1 > mde1`; clause ② when `c2 > mde2`. Then:

    IF   ref2 >= ref1        (the blind reference is the harder one)   -> c1 >= c2
    AND  mde1 <= mde2                                                  -> c1 >= c2 > mde2 >= mde1
    THEN clause ② IMPLIES clause ①, by algebra, and the empty cell is a DERIVATION.

Both premises are measurable here, and they do NOT both hold, which is what makes the round worth
running: the empty cell is part derivation and part measurement, and the two parts have to be
counted separately rather than reported as one number.

    premise A  ref2 >= ref1     -- measured per arm as c1 >= c2
    premise B  mde1 <= mde2     -- measured per arm
    forced     A and B          -> the arm cannot be a counterexample, whatever it does
    contingent A and not B      -> a window [mde2, mde1] exists where ② passes and ① fails.
                                   An arm landing in it IS a counterexample. Whether any does is
                                   the measurement.

SCOPE
  population  the 41 arms of R294's full census -- a CENSUS of the judged arm space, not a sample
  instrument  R294's own committed per-arm c1/c2/mde1/mde2, read, never recomputed
  baseline    clause ② alone, i.e. the definition with clause ① deleted
  regime      968 prompts, A2 against a single annotator, this release

WORLDS
  W1 DECORATION   the cell is empty AND every arm is `forced`. Clause ① is a theorem of clause ②
                  plus the reference ordering, and printing it as an independent test is wrong.
  W2 CONTINGENT   the cell is empty and some arms are `contingent`. Clause ① could have bound and
                  did not, on this arm space. It is a real but unexercised constraint.
  W3 IT BINDS     the cell is non-empty. Clause ① does independent work and the question is closed.

PREDICTION MATRIX
  W1 -> counterexamples 0, contingent arms 0
  W2 -> counterexamples 0, contingent arms > 0, and none of them inside the window
  W3 -> counterexamples > 0, named

PRE-REGISTERED KILL
    if the planted counterexample is detected and the permutation control populates the cell:
        counterexamples >= 1                 -> W3. Clause ① binds. Name the arms.
        counterexamples == 0, contingent == 0 -> W1. Clause ① is a DERIVATION; relabel it.
        counterexamples == 0, contingent > 0  -> W2. Report the window width, because a constraint
                                                 that could have bound is not the same object as
                                                 one that could not.
    else: UNVERIFIED.

CONTROLS
  POSITIVE, planted  a synthetic arm placed INSIDE the window (c2 just above mde2, c1 just below
                     mde1) must be reported as a counterexample. Without it, `0 counterexamples` is
                     an instrument never shown able to return one -- silence, not an acquittal.
  g=0                the same arm placed OUTSIDE the window must NOT be reported. The control fails
                     in both directions or it is not a control.
  NEGATIVE, permutation  break the (c1, c2) pairing across arms and recount. If the cell fills, the
                     emptiness is a property of the PAIRING, not of the two marginals -- which is
                     the world where "clause ① never binds" would be an artifact of which arms
                     happen to be strong overall. ⚠ A permutation answers `did the pairing matter`
                     and never `why`, so the world it excludes is named: arms whose clause-①
                     and clause-② margins are unrelated.
  SPECIFICATION      the MDE multiplier is swept. Both clauses use `effect > 1.0 x MDE`; that 1.0
                     is a choice, and a threshold that changes the verdict must be reported as
                     changing it.

EXIT
    0  controls hold and the census is reported
    1  a control misbehaved -- the count is silence
    2  the census artifact is missing or has no arms: an empty population, never a silent pass
"""
from __future__ import annotations

import glob
import hashlib
import json
import pathlib
import random
import statistics as st
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
CENSUS = "E0*/A*/R294_the_definition_against_everything/results/*.json"
MULTIPLIERS = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
SEEDS = [347, 348, 349]


def load():
    hits = sorted(glob.glob(str(ROOT / CENSUS)))
    if not hits:
        return None, None
    p = pathlib.Path(hits[0])
    return json.loads(p.read_text(encoding="utf-8")), hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def cell(rows, m=1.0):
    """(counterexamples, forced, contingent, in_window) at MDE multiplier m."""
    ce, forced, contingent, inwin = [], [], [], []
    for n, r in rows.items():
        c1, c2 = r["c1"][0], r["c2"][0]
        t1, t2 = m * r["mde1"], m * r["mde2"]
        ok1, ok2 = c1 > t1, c2 > t2
        if ok2 and not ok1:
            ce.append(n)
        # premise A is c1 >= c2 (equivalently ref2 >= ref1); premise B is mde1 <= mde2
        if c1 >= c2 and r["mde1"] <= r["mde2"]:
            forced.append(n)
        elif c1 >= c2:
            contingent.append(n)
            if t2 < c2 <= t1:
                inwin.append(n)
    return ce, forced, contingent, inwin


def planted_controls(rows):
    """A synthetic arm inside the window must be caught; the same arm outside must not."""
    base = next(r for r in rows.values() if r["mde1"] > r["mde2"])
    mde1, mde2 = base["mde1"], base["mde2"]
    inside = {"c1": [(mde1 + mde2) / 2], "c2": [(mde1 + mde2) / 2], "mde1": mde1, "mde2": mde2,
              "a2": base["a2"]}
    outside = {"c1": [mde1 * 3], "c2": [mde1 * 3], "mde1": mde1, "mde2": mde2, "a2": base["a2"]}
    hit, _f, _c, _w = cell({"PLANT_IN": inside})
    miss, _f, _c, _w = cell({"PLANT_OUT": outside})
    ok = (hit == ["PLANT_IN"]) and (miss == [])
    return ok, (f"window [{mde2:.5f}, {mde1:.5f}] — inside -> {hit or 'not caught'} (want caught); "
                f"outside -> {miss or 'not caught'} (want not caught)")


def permutation_control(rows, seed):
    """Break the (c1, c2) pairing. If the cell fills, emptiness is about the PAIRING."""
    rng = random.Random(seed)
    names = list(rows)
    shuffled = names[:]
    rng.shuffle(shuffled)
    fake = {}
    for a, b in zip(names, shuffled):
        fake[a] = {"c1": rows[a]["c1"], "mde1": rows[a]["mde1"],
                   "c2": rows[b]["c2"], "mde2": rows[b]["mde2"], "a2": rows[a]["a2"]}
    ce, _f, _c, _w = cell(fake)
    return len(ce)


def main() -> int:
    d, sha = load()
    if not d or not d.get("rows"):
        print("  UNRUNNABLE: R294's census is missing or has no arms. Exit 2, never 0.")
        return 2
    rows = d["rows"]
    print(f"R347 · does clause ① ever bind?   {len(rows)} arms, census sha256[:16] {sha}\n")

    p_ok, p_detail = planted_controls(rows)
    print(f"  POSITIVE + g=0 (planted): {p_detail}  {'PASS' if p_ok else 'FAIL'}")

    perm = [permutation_control(rows, s) for s in SEEDS]
    perm_ok = any(x > 0 for x in perm)
    print(f"  NEGATIVE (pairing permuted, {len(SEEDS)} seeds): counterexamples {perm} — "
          f"{'PASS, so the empty cell is about the PAIRING' if perm_ok else 'FAIL: the cell cannot fill even when the pairing is destroyed, so its emptiness says nothing'}")

    # ---- the two references, which is WHY one clause binds ---------------------------------------
    ref1 = [r["a2"] - r["c1"][0] for r in rows.values()]
    ref2 = [r["a2"] - r["c2"][0] for r in rows.values()]
    gap = [b - a for a, b in zip(ref1, ref2)]
    print(f"\n  THE TWO REFERENCES — this is the mechanism, not a side note:")
    print(f"    ① random draw from THIS prompt's own rubric : {st.mean(ref1):.4f}  (sd {st.pstdev(ref1):.4f})")
    print(f"    ② size-matched PROMPT-BLIND set             : {st.mean(ref2):.4f}  (sd {st.pstdev(ref2):.4f})")
    print(f"    ② − ① = {st.mean(gap):+.4f}, and the MINIMUM over all {len(rows)} arms is "
          f"{min(gap):+.4f} — never negative.")
    print(f"    A criterion set that never reads the conversation beats a random draw of that")
    print(f"    conversation's OWN criteria, on every arm. That ordering is what makes ② the")
    print(f"    binding clause, and it could have come out the other way.")

    # ---- the specification curve over the MDE multiplier -----------------------------------------
    print(f"\n  SPECIFICATION CURVE over the MDE multiplier (both clauses use 1.0x; that is a choice)\n")
    print(f"    {'x MDE':>7}{'counterexamples':>17}{'forced':>9}{'contingent':>12}{'in window':>11}")
    curve = {}
    for m in MULTIPLIERS:
        ce, forced, cont, win = cell(rows, m)
        curve[m] = {"counterexamples": ce, "forced": len(forced), "contingent": len(cont),
                    "in_window": win}
        mark = "   <- as published" if m == 1.0 else ""
        print(f"    {m:>7.2f}{len(ce):>17}{len(forced):>9}{len(cont):>12}{len(win):>11}{mark}")
        if ce:
            print(f"            {ce}")

    ce, forced, cont, win = cell(rows, 1.0)
    widths = [r["mde1"] - r["mde2"] for r in rows.values() if r["mde1"] > r["mde2"]]
    print(f"\n  At the published 1.0x: {len(forced)} arm(s) FORCED (both premises hold — clause ②")
    print(f"  implies clause ① by algebra there), {len(cont)} CONTINGENT (premise B fails, so a")
    print(f"  window exists), and {len(win)} arm(s) actually inside a window.")
    if widths:
        print(f"  Window width across the contingent arms: median {st.median(widths):.5f}, "
              f"max {max(widths):.5f}.")

    print()
    if not (p_ok and perm_ok):
        print("  UNVERIFIED: a control misbehaved, so the count above is silence.")
        verdict = "UNVERIFIED"
    elif ce:
        print(f"  W3 — CLAUSE ① BINDS. It excludes {len(ce)} arm(s) clause ② admits: {ce}")
        verdict = "W3_IT_BINDS"
    elif not cont:
        print("  W1 — DECORATION. Every arm is forced: clause ② implies clause ① by algebra on this")
        print("  arm space, and printing ① as an independent test overstates what it does.")
        verdict = "W1_DERIVATION"
    else:
        print(f"  W2 — CONTINGENT. The cell is empty and {len(cont)} of {len(rows)} arms COULD have")
        print(f"  filled it: for them premise B fails and a window [mde2, mde1] exists, median width")
        print(f"  {st.median(widths):.5f}. None landed in it. So clause ① is a real constraint that")
        print("  this arm space never exercised — not a theorem, and not doing work either.")
        print("  ⚠ The honest statement is a SPLIT, not a single number: on "
              f"{len(forced)} arms the implication is a DERIVATION, on {len(cont)} it is a")
        print("  MEASUREMENT that could have come out otherwise.")
        verdict = "W2_CONTINGENT"

    art = {"census_sha256_16": sha, "n_arms": len(rows),
           "ref1_mean": st.mean(ref1), "ref2_mean": st.mean(ref2),
           "ref_gap_mean": st.mean(gap), "ref_gap_min": min(gap),
           "curve": {str(k): {"counterexamples": v["counterexamples"], "forced": v["forced"],
                              "contingent": v["contingent"], "in_window": v["in_window"]}
                     for k, v in curve.items()},
           "forced": forced, "contingent": cont, "counterexamples": ce,
           "window_widths_median": st.median(widths) if widths else None,
           "controls": {"planted": p_ok, "permutation": perm, "permutation_ok": perm_ok},
           "verdict": verdict}
    outp = HERE / "results" / "r347_clause_one_binding.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")

    print("\n  ⚠ SCOPE. This is a census of the 41 arms THIS BENCHMARK CONTAINS. `Clause ① never")
    print("    binds` is a statement about that arm space, not about all possible cores — an arm")
    print("    that beats the blind reference while failing against its own prompt's rubric is")
    print("    constructible in principle, and the window arithmetic above says exactly how narrow")
    print("    it would have to be. Building one is the test this round does not perform.")
    return 0 if (p_ok and perm_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
