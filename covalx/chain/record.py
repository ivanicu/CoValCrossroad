"""The typed normative record, as reconciled from three independent designs.

Three record types, because one cannot carry them:

  RULE          invariant under WHO touches it   -- text, polarity, force, scope, exceptions, witnesses
  PERSON        invariant under WHICH rule       -- author identity, importance, confidence, subjectivity
  EVENT         invariant under WHICH rule passed through it -- one row per hop of the chain

Putting a person-fact on a rule is the error that makes "whose values are these?" unanswerable,
because the aggregate then has no slot left to disagree in. The separation is enforced here by
having three classes rather than one wide one, so the mistake is a type error and not a habit.

Every field carries a FALSIFICATION TEST -- the computation that shows the field was not preserved
downstream. A field with no such test is decoration and is not in this module. The tests live in
`metrics.py`; the docstrings here name which one applies.

`force` deserves its own note. The release cannot express it: every criterion is a scalar in
[-10,+10] and the only dispositive channel anywhere is an `unacceptable` block attached to a
RESPONSE, never to a criterion. So `force` is not merely uncollected in CoVal -- it is
unrepresentable, and this enum exists to make the absence nameable rather than invisible.
"""
from __future__ import annotations

import dataclasses
import enum
import hashlib
import json
from typing import Any


class Polarity(str, enum.Enum):
    """Grammatical direction. Falsifier: flip it and a witness score must move as predicted."""
    REQUIRE = "require"
    PREFER = "prefer"
    PERMIT = "permit"
    DISCOURAGE = "discourage"
    FORBID = "forbid"

    @property
    def sign(self) -> int:
        return {"require": +1, "prefer": +1, "permit": 0, "discourage": -1, "forbid": -1}[self.value]

    def flipped(self) -> "Polarity":
        return {Polarity.REQUIRE: Polarity.FORBID, Polarity.PREFER: Polarity.DISCOURAGE,
                Polarity.PERMIT: Polarity.PERMIT, Polarity.DISCOURAGE: Polarity.PREFER,
                Polarity.FORBID: Polarity.REQUIRE}[self]


class Force(str, enum.Enum):
    """Standing. Falsifier: a VETO that any combination of other criteria can outweigh has been
    converted to a preference, whatever the text still says."""
    VETO = "veto"                       # ends the discussion; not tradeable at any price
    HARD_CONSTRAINT = "hard_constraint"  # tradeable only against another hard constraint
    STRONG_DEFAULT = "strong_default"
    SOFT_PREFERENCE = "soft_preference"

    @property
    def dispositive(self) -> bool:
        return self in (Force.VETO, Force.HARD_CONSTRAINT)


class NormativeType(str, enum.Enum):
    PREFERENCE = "preference"
    PRINCIPLE = "principle"
    VETO = "veto"
    RIGHT = "right"
    PROCEDURE = "procedure"
    UNCERTAINTY = "uncertainty"


class Generality(str, enum.Enum):
    """How far the author licensed the rule to travel. Falsifier: score matched in-scope and
    out-of-scope witnesses; equal movement means scope was discarded."""
    THIS_PROMPT_ONLY = "this_prompt_only"
    THIS_TOPIC_CLASS = "this_topic_class"
    GENERAL_POLICY = "general_policy"


class ExceptionEffect(str, enum.Enum):
    SUSPEND = "suspend"
    REVERSE = "reverse"
    NARROW = "narrow"


class Subjectivity(str, enum.Enum):
    FACTUAL = "factual"
    CONTESTED = "contested"
    PERSONAL = "personal"


class Confidence(str, enum.Enum):
    CERTAIN = "certain"
    PROBABLE = "probable"
    TENTATIVE = "tentative"


class Provenance(str, enum.Enum):
    """Recovered in r142, not shipped. `pre_seeded` items have NO author -- they are the lab's own
    text and are not human normative input at all."""
    SELF_AUTHORED = "self_authored"
    PRE_SEEDED = "pre_seeded"
    UNKNOWN = "unknown"


class EdgeType(str, enum.Enum):
    IDENTITY = "identity"
    PARAPHRASE = "paraphrase"
    POLARITY_FLIP = "polarity_flip"
    MERGE = "merge"
    SPLIT = "split"
    SCOPE_NARROW = "scope_narrow"
    SCOPE_WIDEN = "scope_widen"
    FORCE_UPGRADE = "force_upgrade"
    FORCE_DOWNGRADE = "force_downgrade"
    DROP_BY_RULE = "drop_by_rule"
    SUPERSEDE = "supersede"


class ExclusionReason(str, enum.Enum):
    """Dropping is the MODAL outcome -- 74.4% of items -- and most drops are correct. Without this
    field an audit flags normal pipeline behaviour as anomalous, which is the loudest way to be
    wrong about an artefact."""
    REDUNDANT_WITH_SURVIVOR = "redundant_with_survivor"   # requires a pointer
    LOW_RATED = "low_rated"
    CONFLICTING = "conflicting"
    NOT_REVIEWED = "not_reviewed"


class Disposition(str, enum.Enum):
    """DEFAULTS TO VANISHED. Any other value has to be earned by an edge that justifies it, and a
    DROP_BY_RULE whose rule cannot be re-run and reproduce the drop is downgraded back to vanished.
    The default is the whole point: an audit that assumes survival until proven otherwise will
    report survival."""
    VANISHED = "vanished"
    SURVIVED_INTACT = "survived_intact"
    SURVIVED_PARAPHRASED = "survived_paraphrased"
    MERGED = "merged"
    DROPPED_BY_RULE = "dropped_by_rule"


UNRECOVERABLE = "__unrecoverable__"
"""What an annotation instrument must write when it cannot determine a field. Distinct from a
default: a field filled by a guess and a field known to be undeterminable are different objects,
and collapsing them manufactures data. Two instruments disagreeing on a field make it
UNRECOVERABLE here rather than being averaged into a value neither produced."""


@dataclasses.dataclass(frozen=True, slots=True)
class Exception_:
    condition: str
    effect: ExceptionEffect

    def as_dict(self) -> dict[str, Any]:
        return {"condition": self.condition, "effect": self.effect.value}


@dataclasses.dataclass(frozen=True, slots=True)
class Witness:
    """A behaviour the AUTHOR says satisfies or violates the rule. The point of the field is that
    "does this response satisfy the rule?" gets answered against something supplied in advance,
    instead of against a later interpreter's reading of the text -- which is the same interpreter
    whose fidelity is under test."""
    text: str
    satisfies: bool
    boundary_case: bool = False


@dataclasses.dataclass(frozen=True, slots=True)
class Rule:
    rule_id: str
    text: str                                    # verbatim, always retained beside any encoding
    polarity: Polarity | str
    force: Force | str
    normative_type: NormativeType | str
    compensable: bool | str
    generality: Generality | str
    applies_when: tuple[str, ...] = ()
    excludes_when: tuple[str, ...] = ()
    exceptions: tuple[Exception_, ...] = ()
    witnesses: tuple[Witness, ...] = ()
    provenance: Provenance = Provenance.UNKNOWN
    source_conversation: str = ""

    @property
    def text_hash(self) -> str:
        return hashlib.sha256(self.text.strip().lower().encode()).hexdigest()[:16]

    @property
    def typed_fields_recovered(self) -> int:
        return sum(1 for f in (self.polarity, self.force, self.normative_type,
                               self.compensable, self.generality) if f != UNRECOVERABLE)

    def as_dict(self) -> dict[str, Any]:
        def v(x):
            return x.value if isinstance(x, enum.Enum) else x
        return {
            "rule_id": self.rule_id, "text": self.text, "text_hash": self.text_hash,
            "polarity": v(self.polarity), "force": v(self.force),
            "normative_type": v(self.normative_type), "compensable": self.compensable,
            "generality": v(self.generality), "applies_when": list(self.applies_when),
            "excludes_when": list(self.excludes_when),
            "exceptions": [e.as_dict() for e in self.exceptions],
            "witnesses": [dataclasses.asdict(w) for w in self.witnesses],
            "provenance": v(self.provenance), "source_conversation": self.source_conversation,
        }


@dataclasses.dataclass(frozen=True, slots=True)
class Person:
    """Author facts. `importance` and `confidence` are split out of CoVal's single [-10,+10] axis,
    which stacks direction, importance and how strongly this person feels, and which the compiler
    then reads as importance alone. Three quantities on one axis cannot be separated downstream."""
    author_id: str
    importance: float | str = UNRECOVERABLE       # 0..3
    confidence: Confidence | str = UNRECOVERABLE
    subjectivity: Subjectivity | str = UNRECOVERABLE
    raw_weight: float | None = None               # the released scalar, kept verbatim


@dataclasses.dataclass(frozen=True, slots=True)
class Endorsement:
    """A rater scoring someone ELSE's rule. Points at a rule; never mutates it.

    The distinction the release cannot make: a stranger scoring a rule low is input to aggregation,
    while the author scoring their own rule low is an amendment to the rule. One undifferentiated
    `scores[]` array cannot be both, and conflating them makes authorization undecidable."""
    rater_id: str
    rule_id: str
    rating: float
    is_author: bool


@dataclasses.dataclass(frozen=True, slots=True)
class Event:
    """One hop. `input_rule_ids` is a SET so merges are representable; it is the load-bearing field,
    because every preservation test is (source value) vs (value re-read off the linked downstream
    object). Delete it and all of them degrade to text-similarity guessing -- which on this release
    recovers 7.8% of lineage verbatim and 30.8% at 0.80 similarity."""
    event_id: str
    stage: str                                   # A | C | J | D
    input_rule_ids: tuple[str, ...]
    output_ref: str
    edge_type: EdgeType | str
    stage_run_id: str
    exclusion_reason: ExclusionReason | str | None = None
    redundant_with: str | None = None

    def __post_init__(self) -> None:
        if self.edge_type == EdgeType.DROP_BY_RULE and self.exclusion_reason is None:
            raise ValueError("a drop must name why; an unexplained drop is a VANISHED, not a drop")
        if (self.exclusion_reason == ExclusionReason.REDUNDANT_WITH_SURVIVOR
                and not self.redundant_with):
            raise ValueError("redundant_with_survivor requires the pointer to the survivor")


def dumps(rules: list[Rule]) -> str:
    return "\n".join(json.dumps(r.as_dict(), ensure_ascii=False) for r in rules)
