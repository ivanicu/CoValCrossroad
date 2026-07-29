"""Every published donor-difference number is ONE DRAW. Say so, or don't publish it.

WHY THIS EXISTS
---------------
Three separate numbers had to be scoped for this in a single session -- r86's
long-vs-short form gap, r87's deterministic-vs-random offset, and entry 164's claim
that a cell sat "half a point short" of a published edge. Three of the same defect is
the threshold where a fourth patch is the wrong move and infrastructure is the right
one.

The defect: the free donor construction draws INDEPENDENTLY per prompt, so it samples
WITH REPLACEMENT. A single draw uses ~63% of available donor rubrics. r88 measured the
resulting spread at sd 0.0055 (n=968) and r89 at sd 0.0095 (n=300) -- comparable to,
and in one case indistinguishable from, differences this package had already published
as results.

WHAT THIS CHECKS -- and the two gates are different in kind
-----------------------------------------------------------
GATE 1, COMPLETENESS. Every round whose source constructs a donor mapping must appear
in the registry below. This is the gate that matters. A hand-written population turns
an objective check into self-report, and this package has logged exactly that failure:
a check that is right about what it iterates over and blind to what is missing. So the
registry is not trusted -- it is VERIFIED against the source tree on every run, and a
new donor round that nobody classified FAILS rather than passing silently.

GATE 2, SCOPE CARRIED. Every registry entry marked needs_scope must have a README row
that names the draw -- by citing r88/r89 or by saying "donor draw" in as many words.

TWO DONOR IDIOMS, because one pattern would have missed a round
---------------------------------------------------------------
    A  (i + 1 + rng.integers(0, n - 1)) % n     sampling WITH replacement -- 14 rounds
    B  rng.permutation(...) used to build a donor map    -- r04, which idiom A misses
Idiom B was found only by looking for what idiom A could not see. If a third idiom
appears, GATE 1 fires on the unregistered round; it does not silently pass.

THE PROXY LEDGER -- which direction this check is sound in
----------------------------------------------------------
PROPERTY    the README row states the draw scope of a donor-difference number.
PROXY       the row contains a LINK to r88 or r89.
IMPLICATION link absent  => scope absent            SOUND, and this is what it gates on.
            link present => scope stated            NOT SOUND. A row can cite r88 and say
                                                    nothing useful about its own number.
WITNESS     attack vector V5: the string "donor draw" alone passed the first version of
            this check. Requiring the link kills that exact witness and no more.
SAFE SIDE   this check may report a MISSING scope. It may never certify that a present
            one is adequate -- that is a reading, and it is left to review.

WHAT THIS CHECK CANNOT DO
-------------------------
It cannot tell whether a round's PUBLISHED number is a donor difference -- that is a
reading of the claim, not a property of the source. So needs_scope is a HUMAN
classification with a stated reason per round, and it is wrong in the permissive
direction if I misclassified one as not needing scope. The registry records the reason
so the judgement is reviewable rather than implicit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"

# round -> (needs_scope, why). needs_scope=True when the round's README row quotes a
# number that is itself an own-minus-donor difference, or a difference between two
# donor conditions. False entries carry the reason they are exempt.
REGISTRY = {
    "r04_rebuild_satisfaction":     (False, "donor arm is an internal shuffle CONTROL; the row publishes the reconstruction, not a donor difference"),
    "r10_attribution_robustness":   (True,  "publishes attribution against four donors -- the headline's 7.9 comes from its random cell"),
    "r12_response_set":             (True,  "publishes the own-minus-donor attribution whose sign inverts on fresh responses"),
    "r15_indistribution_transfer":  (False, "row publishes a transfer rate, not a donor difference"),
    "r20_paraphrase_transfer":      (True,  "row publishes the advantage RETAINED against a random donor arm"),
    "r21_donor_distance":           (True,  "row publishes attribution as a function of donor distance"),
    "r22_cross_family":             (True,  "row publishes per-judge own-vs-random attribution"),
    "r46_spread_replication":       (True,  "row reproduces r12's attribution inversion on a held-out set"),
    "r54_overlap_transfer":         (False, "row publishes a predictor correlation; the donor arm is a control"),
    "r55_overlap_selectivity":      (False, "row publishes selectivity of the overlap channel, not a donor difference"),
    "r69_r54_predictor_reliability": (False, "row publishes a split-half reliability; the donor arm is a control"),
    "r86_attribution_by_form":      (True,  "row publishes attribution by collection form"),
    "r87_criterion_count_channel":  (True,  "row publishes attribution under three donor pairings"),
    "r88_donor_draw_variance":      (True,  "the round IS the draw measurement"),
    "r89_floor_draw_at_panel_size": (True,  "the round IS the draw measurement at panel size"),
}

IDIOM_A = re.compile(r"\+\s*1\s*\+\s*rng\.integers\(\s*0\s*,\s*n\s*-\s*1\s*\)")
IDIOM_B = re.compile(r"\bdonor\b[^\n]*\bshuffle_map\b|\bshuffle_map\b[^\n]*\bdonor\b", re.S)
# A LINK to the measuring round, not merely the WORDS. Attack vector V5 showed a bare
# "donor draw" with no content passed the phrase version -- a keyword gate cannot prove
# presence, only absence. Requiring the citation raises the floor; it does not make the
# check sound in the positive direction. See the proxy ledger below.
SCOPE = re.compile(r"rounds/r8[89]_[a-z_]+\)", re.I)


def rows_for(readme: str, rnd: str) -> list[str]:
    return [l for l in readme.splitlines() if f"rounds/{rnd})" in l and l.lstrip().startswith("|")]


def main() -> int:
    readme = README.read_text()
    found = {}
    for run in sorted((ROOT / "rounds").glob("*/run.py")):
        src = run.read_text()
        idiom = "A" if IDIOM_A.search(src) else ("B" if IDIOM_B.search(src) else None)
        if idiom:
            found[run.parent.name] = idiom

    print(f"rounds constructing a donor mapping: {len(found)}   registry entries: {len(REGISTRY)}")
    for r, i in sorted(found.items()):
        print(f"    {r:<32} idiom {i}")

    fail = 0

    # ---- GATE 1: completeness. The registry is verified, never trusted. ----------
    unregistered = sorted(set(found) - set(REGISTRY))
    stale = sorted(set(REGISTRY) - set(found))
    if unregistered:
        fail += 1
        print(f"\nFINDING: {len(unregistered)} round(s) construct a donor mapping and are NOT in the "
              f"registry -- nobody decided whether their published number is a single draw:")
        for r in unregistered:
            print(f"    {r}  (idiom {found[r]})")
    if stale:
        fail += 1
        print(f"\nFINDING: {len(stale)} registry entr(ies) name a round that no longer constructs a "
              f"donor mapping -- the registry has drifted from the source:")
        for r in stale:
            print(f"    {r}")

    # ---- GATE 2: the scope is actually carried in the README --------------------
    missing, exempt = [], []
    for r, (needs, why) in sorted(REGISTRY.items()):
        if r not in found:
            continue
        rows = rows_for(readme, r)
        if not needs:
            exempt.append((r, why))
            continue
        if not rows:
            continue                      # not published in the README -> nothing to scope
        if not any(SCOPE.search(l) for l in rows):
            missing.append((r, why))

    if missing:
        fail += 1
        print(f"\nFINDING: {len(missing)} round(s) publish a donor-difference number in the README "
              f"with no draw scope. Each is one draw of a construction whose spread is 0.0055 at "
              f"n=968 and 0.0095 at n=300 (r88, r89):")
        for r, why in missing:
            print(f"    {r}\n        {why}")

    print(f"\n{len(exempt)} registered as NOT needing a draw scope, with reasons:")
    for r, why in exempt:
        print(f"    {r}\n        {why}")

    if fail:
        print(f"\n{fail} gate(s) failed.")
        return 1
    print("\nall donor rounds are registered, and every registered publisher carries its draw scope.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
