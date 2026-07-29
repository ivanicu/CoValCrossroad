"""The freeze register, as a thing rounds can READ.

Queue item 2 froze the rater-structure ontology after four separators failed for
four different reasons.  That freeze was written into FROZEN.md and the README.
It never reached the rounds, which regenerate their verdicts at run time -- so
r26 still asserted "there are pairs that reliably disagree", r27 "ACTOR EFFECT,
NOT BLOCS", and r28 "A MINORITY BLOC SURVIVES", each of which the freeze says is
not established.

That is the third time a correction landed in a summary document and not in the
artifacts (entry 51: the rescope; entry 57: the renderer; this).  So the freeze
lives here, in one place, and the affected rounds append it to their own verdicts
rather than anyone hand-editing a conclusion string.

A round's finding about ITS OWN DATA is not altered -- those numbers are right.
What is appended is the status of the LINE the finding belongs to.
"""
from __future__ import annotations

RATER_STRUCTURE = (
    "FROZEN LINE (queue item 2, see FROZEN.md): this round belongs to the "
    "rater-structure ontology -- r01, r23, r25, r26, r27, r28 -- which is FROZEN as "
    "UNRESOLVED. Four separators failed for four unrelated reasons: r23's sharper "
    "test read z=+10.26 at 2 null reps and +1.40 at 40; r26's centred residual gives "
    "'below average' and 'actually disagreeing' the same number when mean agreement "
    "is +0.25; r27's agreeable-pair control selects same-bloc pairs under unequal "
    "bloc sizes and so could not have found blocs if they existed; r28's design was "
    "rank-deficient by exactly 1, its z moved with PYTHONHASHSEED, and its held-out "
    "R2 spanned [-1.64,+0.51]. The numbers below are correct about this round's own "
    "data. They do NOT establish that value blocs exist, and they do not establish "
    "that they do not. Neither reading is available from this release."
)

BLOC_INTERPRETATION = (
    "FROZEN LINE (queue item 2, see FROZEN.md): the bloc / minority / constituency "
    "reading of r16-r18 is FROZEN. The partition is a median split on a principal "
    "component carrying 0.541% of the singular mass and is not any nameable "
    "constituency -- gender (1.145) and country (1.198) both fail r16's own 1.267 "
    "bar, and 148 of 1,160 criterion raters (12.8%) have no demographics at all. "
    "Read the partition as a 'latent profile split', never as a bloc, minority or "
    "constituency."
)

REGISTRY = {
    "r01_rater_structure": RATER_STRUCTURE,
    "r23_actor_vs_dyad": RATER_STRUCTURE,
    "r25_metric_sweep": RATER_STRUCTURE,
    "r26_sign_no_split": RATER_STRUCTURE,
    "r27_raw_negative_tail": RATER_STRUCTURE,
    "r28_multiplicative": RATER_STRUCTURE,
    "r16_minority_regret": BLOC_INTERPRETATION,
    "r17_conditional_core": BLOC_INTERPRETATION,
    "r18_routing_difficulty": BLOC_INTERPRETATION,
}


def status_for(round_dir: str) -> str | None:
    """Freeze status for a round directory name, or None if the line is live."""
    return REGISTRY.get(round_dir)


def append_to(verdict: str, round_dir: str) -> str:
    """Append the freeze status to a generated verdict, if the line is frozen."""
    s = status_for(round_dir)
    return f"{verdict} || {s}" if s else verdict
