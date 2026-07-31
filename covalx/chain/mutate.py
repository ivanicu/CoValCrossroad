"""The semantic mutation suite -- each operator carries its predicted downstream effect IN CODE.

A mutation whose prediction is written after the result is a narrative. Here the prediction is a
field on the operator, so it exists before anything runs and cannot be edited into agreement
afterwards without showing up in the diff.

The suite is built around three kinds of operator and all three are required:

  SEMANTIC   change what the rule means -- polarity, scope, exception, force. Prediction: a
             specific, signed change in the score of a specific witness.
  NULL       change the wording without changing the meaning. Prediction: NO CHANGE. This is the
             one that bounds every other effect, because whatever it moves is what the instrument
             moves on its own.
  DISRUPTION change the text by an amount comparable to a semantic edit, but content-free.
             Prediction: whatever happens here is the price of editing at all, and a semantic
             effect no larger than this one has not been demonstrated.

Without the last two, a semantic effect is uninterpretable: any edit to a criterion moves a judge
somewhat, and a design that only runs semantic edits will report that movement as meaning.

Deterministic operators are preferred over model-backed ones wherever the edit can be made by rule,
because a model in the MUTATION step is a second instrument whose failures are indistinguishable
from the pipeline's. Model-backed operators are marked `needs_model` and their outputs are checked
by a fidelity gate before use.
"""
from __future__ import annotations

import dataclasses
import enum
import re


class Predict(str, enum.Enum):
    INVERT = "invert"            # satisfaction should become violation on the same response
    DECREASE = "decrease"
    INCREASE = "increase"
    NO_CHANGE = "no_change"
    SCOPE_GATED = "scope_gated"  # unchanged in scope, moves toward neutral out of scope


class Kind(str, enum.Enum):
    SEMANTIC = "semantic"
    NULL = "null"
    DISRUPTION = "disruption"


@dataclasses.dataclass(frozen=True, slots=True)
class Mutation:
    op: str
    kind: Kind
    axis: str
    predicted: Predict
    text: str
    ok: bool = True
    note: str = ""


# --------------------------------------------------------------------------- polarity

_REQ = re.compile(r"\b(should|must|needs? to|has to|ought to)\b", re.I)
_NEG = re.compile(r"\b(should not|shouldn't|must not|mustn't|does not|doesn't|do not|don't|"
                  r"never|avoid|refrain from|without)\b", re.I)
_VERB_HEAD = re.compile(r"^\s*(?:it\s+)?(?:should\s+|must\s+)?([a-z]+(?:s|es)?)\b", re.I)


def flip_polarity(text: str) -> Mutation:
    """require <-> forbid. Deterministic: negate the head directive.

    A criterion in this corpus is usually an imperative or a third-person description of the
    wanted behaviour ("Provides X", "Avoid Y"), so the flip is a negation of the head, not a
    thesaurus substitution."""
    t = text.strip()
    if _NEG.search(t):
        out = _NEG.sub(lambda m: {"should not": "should", "shouldn't": "should",
                                  "must not": "must", "mustn't": "must",
                                  "does not": "does", "doesn't": "does",
                                  "do not": "do", "don't": "do",
                                  "never": "always", "avoid": "actively provide",
                                  "refrain from": "engage in", "without": "with"}
                      [m.group(0).lower()], t, count=1)
        return Mutation("polarity_flip", Kind.SEMANTIC, "polarity", Predict.INVERT, out)
    if _REQ.search(t):
        out = _REQ.sub(lambda m: m.group(0) + " not", t, count=1)
        return Mutation("polarity_flip", Kind.SEMANTIC, "polarity", Predict.INVERT, out)
    m = _VERB_HEAD.match(t)
    if m:
        v = m.group(1)
        out = t[:m.start(1)] + f"does not {_singular_to_bare(v)}" + t[m.end(1):]
        return Mutation("polarity_flip", Kind.SEMANTIC, "polarity", Predict.INVERT, out)
    return Mutation("polarity_flip", Kind.SEMANTIC, "polarity", Predict.INVERT, t, ok=False,
                    note="no head directive found; not mutated rather than mutated wrongly")


def _singular_to_bare(v: str) -> str:
    if v.lower().endswith("ies") and len(v) > 4:
        return v[:-3] + "y"
    if v.lower().endswith(("ses", "shes", "ches", "xes")):
        return v[:-2]
    if v.lower().endswith("s") and not v.lower().endswith("ss"):
        return v[:-1]
    return v


# --------------------------------------------------------------------------- scope

NARROW_CLAUSE = " -- but only when the user has explicitly asked for medical detail"
WIDEN_PAT = re.compile(r"\s*(?:,\s*)?(?:but\s+)?only\s+(?:when|if)[^.;]*", re.I)


def narrow_scope(text: str) -> Mutation:
    t = text.rstrip(". ")
    return Mutation("scope_narrow", Kind.SEMANTIC, "scope", Predict.SCOPE_GATED,
                    t + NARROW_CLAUSE + ".")


def widen_scope(text: str) -> Mutation:
    if not WIDEN_PAT.search(text):
        return Mutation("scope_widen", Kind.SEMANTIC, "scope", Predict.INCREASE, text, ok=False,
                        note="no scope qualifier present to remove")
    return Mutation("scope_widen", Kind.SEMANTIC, "scope", Predict.INCREASE,
                    WIDEN_PAT.sub("", text).strip())


def change_subject(text: str) -> Mutation:
    sub = {"the user": "the assistant", "the reader": "the assistant",
           "the patient": "the clinician", "people": "medical professionals"}
    for a, b in sub.items():
        if a in text.lower():
            i = text.lower().index(a)
            return Mutation("subject_change", Kind.SEMANTIC, "scope", Predict.DECREASE,
                            text[:i] + b + text[i + len(a):])
    return Mutation("subject_change", Kind.SEMANTIC, "scope", Predict.DECREASE, text, ok=False,
                    note="no addressable subject term")


# --------------------------------------------------------------------------- exceptions

EXC_LEGIT = " This does not apply when the user describes an emergency."
EXC_ILLEGIT = " This does not apply on Tuesdays."
EXC_PAT = re.compile(r"\s*(?:unless|except (?:when|if|that)|this does not apply[^.]*)[^.]*\.?",
                     re.I)


def remove_exception(text: str) -> Mutation:
    if not EXC_PAT.search(text):
        return Mutation("exception_remove", Kind.SEMANTIC, "exception", Predict.INCREASE, text,
                        ok=False, note="no carve-out present to remove")
    return Mutation("exception_remove", Kind.SEMANTIC, "exception", Predict.INCREASE,
                    EXC_PAT.sub("", text).strip())


def add_legit_exception(text: str) -> Mutation:
    return Mutation("exception_add_legit", Kind.SEMANTIC, "exception", Predict.SCOPE_GATED,
                    text.rstrip() + EXC_LEGIT)


def add_illegit_exception(text: str) -> Mutation:
    """An irrelevant carve-out. Prediction NO_CHANGE on ordinary witnesses: an executor reading
    content should ignore a condition that never fires. Movement here means the executor is
    responding to the presence of a clause, not to what it says."""
    return Mutation("exception_add_illegit", Kind.DISRUPTION, "exception", Predict.NO_CHANGE,
                    text.rstrip() + EXC_ILLEGIT)


# --------------------------------------------------------------------------- force

def veto_to_scalar(text: str) -> Mutation:
    return Mutation("veto_to_scalar", Kind.SEMANTIC, "force", Predict.DECREASE,
                    "Among several considerations, it is somewhat preferable that: "
                    + text[0].lower() + text[1:])


def scalar_to_veto(text: str) -> Mutation:
    return Mutation("scalar_to_veto", Kind.SEMANTIC, "force", Predict.INCREASE,
                    "It is absolutely unacceptable to fail this, whatever else the answer does: "
                    + text[0].lower() + text[1:])


# --------------------------------------------------------------------------- surface form

FILLER = (" The assistant is a computer program. Responses are displayed as text on a screen. "
          "The interface supports scrolling.")


def unrelated_tokens(text: str) -> Mutation:
    """The disruption control. Adds length and irrelevant content comparable to a semantic edit,
    carrying no normative content whatsoever. Any semantic effect not clearly larger than this one
    is a measurement of editing, not of meaning."""
    return Mutation("unrelated_tokens", Kind.DISRUPTION, "surface", Predict.NO_CHANGE,
                    text.rstrip() + FILLER)


def lexical_echo(text: str, response: str) -> Mutation:
    """Copy surface tokens from the response into the criterion without changing what it asks for.
    A content-sensitive executor should not move; a lexically-coupled one should rise."""
    words = [w for w in re.findall(r"\b[a-z]{6,}\b", response.lower())][:6]
    if not words:
        return Mutation("lexical_echo", Kind.NULL, "surface", Predict.NO_CHANGE, text, ok=False,
                        note="no content words to echo")
    return Mutation("lexical_echo", Kind.NULL, "surface", Predict.NO_CHANGE,
                    text.rstrip(". ") + " (relevant terms: " + ", ".join(words) + ").")


DETERMINISTIC = (flip_polarity, narrow_scope, widen_scope, change_subject, remove_exception,
                 add_legit_exception, add_illegit_exception, veto_to_scalar, scalar_to_veto,
                 unrelated_tokens)


def apply_all(text: str, response: str | None = None) -> list[Mutation]:
    out = [f(text) for f in DETERMINISTIC]
    if response:
        out.append(lexical_echo(text, response))
    return out


def suite_summary(muts: list[Mutation]) -> dict:
    by = {}
    for m in muts:
        by.setdefault(m.op, {"kind": m.kind.value, "axis": m.axis,
                             "predicted": m.predicted.value, "applied": 0, "skipped": 0})
        by[m.op]["applied" if m.ok else "skipped"] += 1
    return by
