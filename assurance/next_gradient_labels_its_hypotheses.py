"""next_gradient_labels_its_hypotheses — a causal claim in a NEXT block must cite or be labelled.

WHY THIS EXISTS, measured rather than assumed. §4 of `realstat` names the highest-risk sentence in
any report:

    "The `next gradient` line is the highest-risk sentence in a report: it is written last, it is the
     one a later round acts on, and it is the only one with no control attached."

R366 measured the cost on this campaign: five of nine consecutive rounds corrected a claim published
within the previous three, and the last one corrected a sentence from the IMMEDIATELY PRECEDING
commit -- `"it survived because it is a DIFFERENCE ... the definition should be restated in
differences"`, which was refuted by an artifact already committed two rounds earlier. The RESULT was
measured; the EXPLANATION offered beside it was not; and the explanation is what the next round acted
on.

⚠ THE POPULATION WAS CHOSEN BY MEASUREMENT, AND THE FIRST CANDIDATE WAS WRONG. The obvious surface
  was `DEFINITION.md`, and it is not where the error lives: 80 units, 5 tight causal connectives, and
  every one of them a derivation that already cites its round -- because that document is gated. The
  errors live in COMMIT `NEXT:` BLOCKS, which nothing checks. Building the gate over the document
  would have been the instrument's-unit-vs-claim's-unit failure: it would have watched the surface
  where the mistakes are not.

PROXY LEDGER -- this check is weaker than it looks and the limit is the whole point:
  PROPERTY   "the explanation a future round will act on is true"
  PROXY      "a causal claim in a NEXT block either cites a round or is labelled a hypothesis"
  IMPLICATION  NEITHER direction is sound for the property. This gate CANNOT tell a right
               explanation from a wrong one and must never be read as doing so.
  WHAT IT DOES ENFORCE, soundly: **labelling**. An untested explanation must be marked untested.
               R365's sentence would have had to read `HYPOTHESIS (untested)`, and R366's refutation
               would then have cost nothing, because nothing would have been proposed on it.
  SAFE SIDE  it is a RATCHET, not a verdict: the historical blocks are frozen in
             `KNOWN_UNLABELLED.json` so the debt cannot grow silently, and the check fails on a NEW
             offender or on a frozen one that becomes compliant (shrink-only, like the stamp gate).

EMPTY POPULATION: no commits, or no NEXT blocks at all -> exit 2, never 0.

POSITIVE CONTROL: the two blocks R366 refuted (`a83f458`, `5422ffa3`) MUST be flagged by the
pattern. A detector that cannot see the errors it was built for is silence.
"""
from __future__ import annotations
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
FROZEN = pathlib.Path(__file__).resolve().parent / "KNOWN_UNLABELLED.json"
N_COMMITS = 60

NEXT = re.compile(r"^NEXT:(.*)$", re.S | re.M)
ROUND = re.compile(r"\bR\d{2,3}\b")
CAUSAL = re.compile(r"\b(because|therefore|hence|thus|since|which is why|implies|so that|"
                    r"means that|the reason)\b", re.I)
# ⚠ A LABEL MUST BE A MARKER, NOT A MENTIONED WORD -- caught by this file's own positive control.
# v1 matched the bare token, and `5422ffa`'s NEXT block says "...or marked UNTESTED" as SUBJECT
# MATTER. The gate read that as a label on its own claim and excused the very commit it was built
# from. That is the instrument's-unit-vs-claim's-unit failure, committed inside the instrument.
# A marker has a FORM: bracketed, or followed by a colon/dash. Mentioning the word does not.
LABEL = re.compile(r"(\[(HYPOTHESIS|UNTESTED|SPECULATIVE|GUESS|UNVERIFIED)\]"
                   r"|\((HYPOTHESIS|UNTESTED|SPECULATIVE|GUESS|UNVERIFIED)\)"
                   r"|\b(HYPOTHESIS|UNTESTED|SPECULATIVE|GUESS|UNVERIFIED)\s*[:\u2014-])", re.I)
# the two blocks R366 refuted -- the detector must see both, or it cannot see what it is for
KNOWN_BAD = ("a83f458", "5422ffa")


def blocks(n=N_COMMITS):
    out = subprocess.run(["git", "-C", str(ROOT), "log", f"-{n}",
                          "--format=%H%x01%s%x01%b%x02"],
                         capture_output=True, text=True).stdout
    recs = []
    for r in out.split("\x02"):
        if not r.strip():
            continue
        parts = (r.split("\x01") + ["", ""])[:3]
        m = NEXT.search(parts[2] or "")
        if m:
            recs.append((parts[0].strip()[:8], parts[1][:70], m.group(1)))
    return recs


def offends(text):
    """A causal claim, no round cited, and not labelled as a hypothesis."""
    return bool(CAUSAL.search(text)) and not ROUND.search(text) and not LABEL.search(text)


def main() -> int:
    recs = blocks()
    if not recs:
        print("  UNRUNNABLE: no commit carries a NEXT: block. Exit 2, never 0 — a gate that")
        print("  examined nothing has not passed.")
        return 2

    flagged = [(h, s) for h, s, t in recs if offends(t)]
    frozen = set(json.loads(FROZEN.read_text())["unlabelled"]) if FROZEN.exists() else set()

    print(f"  {len(recs)} commits carry a NEXT: block; {len(flagged)} state a causal claim with")
    print(f"  no round citation and no hypothesis label.\n")
    print(f"    {'commit':>9}{'status':>12}   subject")
    new, fixed = [], []
    for h, s in flagged:
        st = "frozen" if h in frozen else "NEW"
        if h not in frozen:
            new.append((h, s))
        print(f"    {h:>9}{st:>12}   {s}")
    # ⚠ A TIME-WINDOWED POPULATION NEEDS PER-ENTRY POPULATION LOGIC, and v1 did not have it.
    #   This corpus is `the last N commits`, so a frozen entry leaves it by SCROLLING OUT, not by
    #   being fixed. v1 treated both as "no longer offends" and demanded the list be edited for a
    #   commit that had simply aged out -- which would have made the ratchet's count fall without
    #   anyone improving anything, i.e. a shrinking number meaning the OPPOSITE of what it means in
    #   every other ratchet here. That exact failure was written down as a labelled `[UNTESTED]`
    #   prediction two commits before it fired, and it fired on the very next run: 1 entry scrolled
    #   out, 0 genuinely fixed. Corrected: OUT OF WINDOW is out of population and is dropped
    #   silently; only an entry STILL IN the window that stops offending is a real shrink.
    in_window = {h for h, _s, _t in recs}
    scrolled = [h for h in sorted(frozen) if h not in in_window]
    for h in sorted(frozen):
        if h in in_window and h not in {x[0] for x in flagged}:
            fixed.append(h)
    # ⚠⚠ AND THE COUNT ABOVE CHANGES ITS MEANING WHEN `frozen` EMPTIES (entry 1354, measured).
    # `scrolled` is correct and is the mechanism: refusing to call out-of-window entries FIXED, while
    # the window slides past all of them, leaves the baseline correct-but-EMPTY. Measured today:
    # 12 of 12 frozen hashes sit at depth 707..765 with N_COMMITS=60, so ZERO are in population.
    # With an empty baseline every offender is labelled NEW, and the headline silently converts from
    # an INCREMENT (a regression since baseline) to a PREVALENCE (the whole offending population).
    # This is the sibling of the expiring positive control below: same root cause, fixed anchors in a
    # sliding window -- but where that one goes SILENT and says so, this one keeps printing a
    # plausible number under a word that no longer describes it, which is the more dangerous half.
    # The general shape: A CORRECTION THAT PRESERVES AN INVARIANT CAN STILL DESTROY A DEFINITION.
    # `scrolled` preserves MONOTONICITY -- the count cannot fall for free. It does not preserve WHAT
    # THE COUNT COUNTS. Not "fixed" by re-freezing today's offenders: that would ratchet in the
    # flattering direction. Named instead, so the headline cannot be read as a regression count.
    if not (frozen & in_window) and frozen:
        print(f"\n  ⚠ BASELINE OUT OF POPULATION: all {len(frozen)} frozen hashes are outside the")
        print(f"    {N_COMMITS}-commit window, so the effective baseline is EMPTY and the count below")
        print( "    is a PREVALENCE (the whole offending population), not an INCREMENT since baseline.")
    if scrolled:
        print(f"\n  ⓘ {len(scrolled)} frozen entr(ies) have SCROLLED OUT of the {N_COMMITS}-commit")
        print(f"    window and are out of population, not fixed: {scrolled}. Dropped silently —")
        print(f"    counting them as fixed would make this ratchet shrink by the passage of time")
        print(f"    rather than by work, which is the opposite of what every other ratchet means.")

    # ---- positive control: it must see the two blocks R366 refuted -------------------------------
    # ⚠ REPAIRED: this control was ANCHORED TO FIXED COMMITS AND EVALUATED INSIDE A SLIDING WINDOW.
    # `flagged` is computed over the last N_COMMITS=60 commits; a83f458 and 5422ffa are 707 and 706
    # commits deep. So it demanded a 60-commit window contain objects ~707 deep, and had been
    # STRUCTURALLY IMPOSSIBLE TO PASS for ~646 commits — during which the gate refused to report
    # (correctly) and its silence was counted in the census as an ordinary FAIL.
    # The class is new and is NOT "a check that cannot fail" nor "a control that cannot pass":
    # this control COULD pass and DID pass, and then THE POPULATION MOVED OUT FROM UNDER IT.
    # A control that expires. The identical time-dependence was already found and corrected for the
    # ratchet 15 lines above — `scrolled` drops out-of-window frozen entries precisely so the number
    # cannot shrink "by the passage of time rather than by work" — and was never applied down here.
    # Fix: fetch the two anchors BY HASH, independent of the window, and run the SAME `offends`
    # predicate the gate rules with, so the control still tests the ruling code and not a copy.
    _pc = subprocess.run(["git", "-C", str(ROOT), "show", "-s", "--format=%b", *KNOWN_BAD],
                         capture_output=True, text=True)
    _pc_blocks = []
    for _k in KNOWN_BAD:
        _b = subprocess.run(["git", "-C", str(ROOT), "show", "-s", "--format=%b", _k],
                            capture_output=True, text=True).stdout
        _m = NEXT.search(_b or "")
        _pc_blocks.append((_k, _m.group(1) if _m else None))
    _missing = [k for k, t in _pc_blocks if t is None]
    if _missing:
        print(f"\n  POSITIVE CONTROL UNRUNNABLE: {_missing} carry no NEXT: block — the anchor is")
        print( "    gone, not the detector. Exit 2: an anchor that cannot be read is silence.")
        return 2
    caught = [k for k, t in _pc_blocks if offends(t)]
    pos_ok = len(caught) == len(KNOWN_BAD)
    print(f"\n  POSITIVE CONTROL  the two NEXT blocks R366 refuted must be flagged: "
          f"{len(caught)}/{len(KNOWN_BAD)} caught {sorted(caught)}  "
          f"{'PASS' if pos_ok else 'FAIL'}")
    print(f"    A detector that cannot see the errors it was built for is silence, not a clean bill.")

    # ---- g=0: a compliant block must NOT be flagged ----------------------------------------------
    probe_cited = "this rests on R362's table, so the next step is to re-run it"
    probe_labelled = "HYPOTHESIS: it survived because it is a difference"
    probe_mentions = "pair each because with the round that tested it, or marked UNTESTED"
    g0_ok = (not offends(probe_cited)) and (not offends(probe_labelled)) \
        and offends("it survived because it is a difference, so restate the definition") \
        and offends(probe_mentions)      # MENTIONING the word must NOT excuse the claim
    print(f"  g=0               a block that CITES a round -> not flagged; one LABELLED "
          f"HYPOTHESIS -> not flagged;")
    print(f"                    the same sentence with neither -> flagged; and a block that only")
    print(f"                    MENTIONS the word UNTESTED -> still flagged.  "
          f"{'PASS' if g0_ok else 'FAIL'}")

    print(f"\n  PROXY LEDGER — this enforces LABELLING, never correctness. It cannot tell a right")
    print(f"    explanation from a wrong one and must not be read as doing so. What it makes")
    print(f"    impossible is proposing an ACTION on an untested `because` without saying so.")

    if not pos_ok or not g0_ok:
        print("\n  FAIL: a control misbehaved; the counts above are silence.")
        return 1
    if new:
        print(f"\n  FAIL: {len(new)} NEW unlabelled causal NEXT block(s): "
              f"{[h for h, _ in new]}")
        print(f"  Cite the round that tested the claim, or mark it HYPOTHESIS/UNTESTED. The point")
        print(f"  is not to forbid a hunch — it is to stop the next round acting on one silently.")
        return 1
    if fixed:
        print(f"\n  FAIL (shrink-only ratchet): {len(fixed)} frozen entr(ies) no longer offend: "
              f"{fixed}")
        print(f"  Remove them from KNOWN_UNLABELLED.json so the debt list keeps shrinking and")
        print(f"  cannot quietly become a confession nobody re-reads.")
        return 1
    print(f"\n  PASS: every NEXT block in the last {len(recs)} either cites a round, carries no")
    print(f"  causal claim, or is labelled a hypothesis. Frozen debt: {len(frozen)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
