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
    for h in sorted(frozen):
        if h not in {x[0] for x in flagged}:
            fixed.append(h)

    # ---- positive control: it must see the two blocks R366 refuted -------------------------------
    seen = {h for h, _ in flagged}
    caught = [k for k in KNOWN_BAD if any(h.startswith(k) or k.startswith(h) for h in seen)]
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
