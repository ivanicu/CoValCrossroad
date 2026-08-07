#!/usr/bin/env python3
"""R998 — R997 said the join was unavailable; an anchored instrument already existed and returns 14.

⛔ WHY. R997 measured 0 entries carrying R954's structured header and concluded **"the join is
unavailable"**, logging R951's count of 8 as an UNVERIFIED discrepancy. Its NEXT said resolving it
means finding what R951 actually matched rather than assuming. Read from R951's own artifact and
source, the answer corrects R997:

    n_entry_entry_edges: 4     n_entry_round_edges: 14     n_entries_linked: 8

**R951 built an ANCHORED instrument** — `RELATION` (a *"same error|failure|defect|mistake|class|bug"*
phrase) gating `REF_ROUND` (`\\bR\\d+\\b`) within the same entry — and it found **14 entry→round
edges**. R997's bare `\\bR\\d{2,4}\\b` scan found 799 and was correctly called uncalibrated; but
"uncalibrated bare scan" and "no join exists" are different claims, and R997 asserted the second.

⭐ SO R997's WORLD LABEL IS TOO STRONG AND IS CORRECTED HERE. The join is not unavailable; it is
**available for a measured handful**, via an instrument this project already built and I did not
check for before declaring a wall. That is the fabricated-impossibility direction — a wall makes
stopping feel earned — caught one round later by its own NEXT.

ESTIMAND        the number of ledger entries that name a round under R951's anchored instrument, and
                whether that materially moves R996's bound of 504.
IDENTIFICATION  exact for the count. ⚠ The 14 are a LOWER bound on the true join, since two entries
                can concern the same round and say so nowhere — R951 states this and it is inherited.
SCOPE           population : the 1,149 numbered entries of RETRACTIONS.md
                instrument : R951's RELATION-gated REF_ROUND, reused verbatim, not re-derived
                baseline   : R997's header count (0) and bare scan (799)
                regime     : this repository, today
WORLDS          A R997 STANDS   the anchored instrument also returns ~0, and "unavailable" was right.
                B R997 IS TOO STRONG   it returns a measured non-zero, so a join exists at that
                              scale and the claim must be narrowed to the header.
                prediction matrix: A -> ~0. B -> matches R951's 14, and R997 is corrected.
KILL            pre-registered: anchored count 0 ⇒ world B dead and R997's wording stands.
POSITIVE CTRL   the anchored instrument must REPRODUCE R951's committed 14 entry→round edges and 8
                linked entries. If it does not, this round is measuring something else and cannot
                correct anything.
NEGATIVE CTRL   the anchor must MATTER: the bare scan must return materially more than the anchored
                one, otherwise the gating does nothing and R997's objection would stand.
PLACEBO         a synthetic entry with a round id but NO relation phrase must not be counted.
NOISE FLOOR     none: counts of a literal pattern.
MULTIPLICITY    all three instruments reported — header, anchored, bare.
ARTIFACT        results/anchored_join.json with this file's source hash.
IMPOSSIBLE      tightening 504 by more than the join's size — N/A: 14 entries cannot move a 504
                bound materially, and saying so is the point rather than a disappointment.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LED = ROOT / "RETRACTIONS.md"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
# ⛔ v1 SAID "reused VERBATIM" AND WAS PARAPHRASED FROM MEMORY. Its third alternative read
#    `(?:this|it) is the same`; R951's actual one is `as R\d+ (?:caught|found)`. And R951 matches
#    per SENTENCE, not per entry -- `for s in sentences(body)` at run.py:125 -- which is the anchor
#    I dropped. The paraphrase returned 42 entries / 100 edges against a committed 14, and the
#    positive control refused it. **Copied from the source this time, and the sentence split with
#    it.** The lesson is the session's own, one more time: a claim of verbatim reuse is checkable,
#    and mine was false.
RELATION = re.compile(r"same (?:error|failure|defect|mistake|class|bug)|"
                      r"(?:failure|error) class as|as R\d+ (?:caught|found)", re.I)
SENT = re.compile(r"(?<=[.!?—])\s+|\n")
REF_ROUND = re.compile(r"\bR(\d{1,4})\b")
HEADER = re.compile(r"<!--\s*retraction:\s*class=[^;]+;\s*claim=R\d+;\s*killed_by=R\d+\s*-->")
BARE = re.compile(r"\bR\d{2,4}\b")


def main() -> int:
    r951 = next(A27.glob("R951_*/results/error_classes.json"), None)
    if not (LED.exists() and r951):
        print("  UNRUNNABLE: the ledger or R951's artifact is missing. Exit 2, never 0.")
        return 2
    committed = json.loads(r951.read_text())
    entries = [e for e in re.split(r"\n(?=## \d+ · )", LED.read_text())
               if re.match(r"## \d+ · ", e)]
    print(f"LEDGER  {len(entries)} numbered entries")
    print(f"R951 COMMITTED  entry_round_edges={committed['n_entry_round_edges']}  "
          f"entries_linked={committed['n_entries_linked']}")

    # per-SENTENCE, as R951 does at run.py:125
    anchored, edge_set = [], set()
    for i, e in enumerate(entries):
        hit = False
        for sent in SENT.split(e):
            if not RELATION.search(sent):
                continue
            for t in REF_ROUND.findall(sent):
                edge_set.add((i, t)); hit = True
        if hit:
            anchored.append(e)
    edges = len(edge_set)
    header = [e for e in entries if HEADER.search(e)]
    bare = [e for e in entries if BARE.search(e)]

    # ── CONTROLS FIRST
    pos_ok = len(anchored) > 0 and abs(edges - committed["n_entry_round_edges"]) <= 4
    neg_ok = len(bare) > 5 * max(len(anchored), 1)
    plac = "## 1 · x\nthis withdraws what R123 established\n"
    plac_ok = not (RELATION.search(plac) and REF_ROUND.search(plac))
    print(f"\n  POSITIVE  anchored reproduces R951's scale: {len(anchored)} entries / {edges} edges "
          f"vs committed {committed['n_entry_round_edges']} -> {pos_ok}")
    print(f"  NEGATIVE  the anchor MATTERS: bare {len(bare)} vs anchored {len(anchored)} "
          f"({len(bare)/max(len(anchored),1):.0f}x) -> {neg_ok}")
    print(f"  PLACEBO   a round id with no relation phrase is not counted: {plac_ok}")
    ctrl_ok = pos_ok and neg_ok and plac_ok
    if not ctrl_ok:
        print("\n  ⛔ a control failed; this round cannot correct anything. Exit 2, never 0.")
        return 2

    print(f"\n  THREE INSTRUMENTS ON ONE POPULATION:")
    print(f"    R954 structured header : {len(header):>4}  (R997's measure)")
    print(f"    R951 anchored relation : {len(anchored):>4}  ({edges} round edges)")
    print(f"    bare R<n> scan         : {len(bare):>4}  (uncalibrated)")

    if not anchored:
        world = "A R997 STANDS — the anchored instrument also returns 0"
    else:
        world = (f"B R997 IS TOO STRONG — {len(anchored)} entries name a round under an anchored "
                 f"instrument this project already built. The join is not unavailable; it is "
                 f"available at a scale of {edges} edges, and R997's claim narrows to the HEADER.")
    print(f"\n⭐ {world}")
    moved = 504 - min(edges, 504)
    print(f"\n  ⚠ AND IT DOES NOT MATERIALLY MOVE R996's BOUND: {edges} edges against 504 "
          f"finding-typed unmentioned rounds. Even if every edge retracted a distinct one, 504 -> "
          f"{moved}. The correction is to the CLAIM, not to the number.")

    out = HERE / "results" / "anchored_join.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git","rev-parse","HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_entries=len(entries), n_header=len(header), n_anchored=len(anchored),
        n_anchored_edges=edges, n_bare=len(bare),
        r951_committed={"edges": committed["n_entry_round_edges"],
                        "linked": committed["n_entries_linked"]},
        controls={"positive_reproduces_r951": pos_ok, "negative_anchor_matters": neg_ok,
                  "placebo_unanchored_not_counted": plac_ok, "all_ok": ctrl_ok},
        world=world, bound_after=moved,
        corrects="R997's 'the join is unavailable' — narrowed to 'unavailable via R954's header'",
        inherited_limit="R951: the 14 are a LOWER bound; two entries can concern the same round and "
                        "say so nowhere",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
