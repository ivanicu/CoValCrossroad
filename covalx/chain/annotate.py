"""Fill the typed fields -- by FORCED CHOICE over the enum, never by free generation.

Free generation plus parsing fails in a way that is invisible: an unparseable answer becomes a
default, and defaults look like data. Instead every field is asked as a lettered multiple choice
and the answer is read off the logits at the single next position. That is exact, deterministic,
one forward pass per (rule, field), and it yields a margin for free.

THE MARGIN IS THE POINT. A field is written only when the two independent instruments AGREE and
each is above its margin floor. Otherwise the field is UNRECOVERABLE -- which is a different object
from a default, and keeping them distinct is what stops the corpus from manufacturing data. Two
instruments disagreeing are never averaged into a value neither produced.

WHAT THIS CANNOT BE. The memo requires author-supplied fields; these authors are unreachable, so
every value here is an INTERPRETER'S RECONSTRUCTION of what the author meant. That is a permanent,
structural limitation of auditing a released artefact and it is recorded on every row rather than
mentioned once in a limitations section. No claim built on these fields may be worded as a claim
about what the author intended.
"""
from __future__ import annotations

import dataclasses
import json
import pathlib

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from .record import (Confidence, Force, Generality, NormativeType, Polarity, Rule, Subjectivity,
                     UNRECOVERABLE)

MARGIN_FLOOR = 0.40      # top option must hold at least this share of the mass over the options
LETTERS = "ABCDEFGH"

FAMILIES = {
    "qwen25_7b": "/home/ivan/research.alignment.emergent-misalignment.developmental-spectroscopy."
                 "build.lg.private.editable/models/Qwen2.5-7B-Instruct",
    "phi35_mini": "/home/ivan/research/causal-publication-protocol/artifacts/model_phi-3.5-mini-instruct",
    "qwen25_3b": "/home/ivan/research/causal-publication-protocol/artifacts/model_qwen2.5-3b-instruct",
    "llama31_8b": "/home/ivan/research.alignment.emergent-misalignment.developmental-spectroscopy."
                  "build.lg.private.editable/models/judge_llama31_8b",
}


@dataclasses.dataclass(frozen=True, slots=True)
class Field:
    name: str
    question: str
    options: tuple[tuple[str, str], ...]      # (value, gloss)

    @property
    def values(self) -> tuple[str, ...]:
        return tuple(v for v, _g in self.options)


FIELDS = (
    Field("polarity",
          "What does this criterion tell the assistant to DO with the behaviour it names?",
          ((Polarity.REQUIRE.value, "it must always do this"),
           (Polarity.PREFER.value, "it is better if it does this"),
           (Polarity.PERMIT.value, "it is allowed to do this, either way is fine"),
           (Polarity.DISCOURAGE.value, "it is better if it does not do this"),
           (Polarity.FORBID.value, "it must never do this"))),
    Field("force",
          "How much weight does this criterion have when it conflicts with other good qualities of "
          "a response?",
          ((Force.VETO.value,
            "absolute -- a response breaking this is unacceptable no matter how good it is otherwise"),
           (Force.HARD_CONSTRAINT.value,
            "near-absolute -- only another rule of the same kind could outweigh it"),
           (Force.STRONG_DEFAULT.value, "strong, but a clearly better response could outweigh it"),
           (Force.SOFT_PREFERENCE.value, "one consideration among several"))),
    Field("normative_type",
          "What KIND of statement is this?",
          ((NormativeType.PREFERENCE.value, "a taste or preference about style or emphasis"),
           (NormativeType.PRINCIPLE.value, "a general principle about how to behave"),
           (NormativeType.VETO.value, "a prohibition on a specific unacceptable behaviour"),
           (NormativeType.RIGHT.value, "something the user is entitled to receive"),
           (NormativeType.PROCEDURE.value, "a step or order of operations to follow"),
           (NormativeType.UNCERTAINTY.value, "a statement about handling what is not known"))),
    Field("compensable",
          "If a response breaks this criterion but is excellent in every other way, can the other "
          "qualities make up for it?",
          (("true", "yes -- enough other merit can outweigh breaking it"),
           ("false", "no -- breaking it is not made acceptable by any amount of other merit"))),
    Field("generality",
          "How far beyond THIS conversation was this criterion meant to apply?",
          ((Generality.THIS_PROMPT_ONLY.value, "only to this specific question"),
           (Generality.THIS_TOPIC_CLASS.value, "to questions on this kind of topic"),
           (Generality.GENERAL_POLICY.value, "to the assistant's behaviour in general"))),
    Field("subjectivity",
          "Would reasonable people disagree about whether this criterion is right?",
          ((Subjectivity.FACTUAL.value, "no -- it is a matter of fact or professional standard"),
           (Subjectivity.CONTESTED.value, "yes -- people with different values would disagree"),
           (Subjectivity.PERSONAL.value, "it is a matter of individual taste"))),
    Field("confidence",
          "How firmly is this criterion stated?",
          ((Confidence.CERTAIN.value, "stated as settled"),
           (Confidence.PROBABLE.value, "stated as a strong view"),
           (Confidence.TENTATIVE.value, "stated with hedging or doubt"))),
)


class ForcedChoice:
    """One forward pass per question; the answer is read from the logits over the option letters."""

    def __init__(self, path: str, device: str = "cuda", dtype=torch.bfloat16) -> None:
        self.tok = AutoTokenizer.from_pretrained(path)
        self.model = AutoModelForCausalLM.from_pretrained(
            path, dtype=dtype, attn_implementation="sdpa").to(device).eval()
        self.device = device
        # letter ids as they appear after "Answer:" -- with the leading space, which is how the
        # model actually continues. Getting this wrong silently scores the wrong tokens.
        self.letter_ids = [self.tok.encode(f" {c}", add_special_tokens=False)[-1]
                           for c in LETTERS]

    def _chat(self, user: str) -> str:
        if getattr(self.tok, "chat_template", None):
            return self.tok.apply_chat_template(
                [{"role": "user", "content": user}], tokenize=False, add_generation_prompt=True
            ) + "Answer:"
        return user + "\nAnswer:"

    @torch.no_grad()
    def ask(self, context: str, field: Field) -> tuple[str, float, list[float]]:
        opts = "\n".join(f"{LETTERS[i]}. {g}" for i, (_v, g) in enumerate(field.options))
        user = (f"{context}\n\n{field.question}\n\n{opts}\n\n"
                f"Reply with one letter only.")
        ids = self.tok(self._chat(user), return_tensors="pt").to(self.device)
        logits = self.model(**ids).logits[0, -1]
        k = len(field.options)
        sel = torch.tensor(self.letter_ids[:k], device=logits.device)
        p = torch.softmax(logits[sel].float(), dim=-1).tolist()
        j = max(range(k), key=lambda i: p[i])
        return field.values[j], p[j], p

    def close(self) -> None:
        del self.model
        torch.cuda.empty_cache()


def context_for(rule: Rule, prompt: str) -> str:
    return (f"A person was shown this question asked of an AI assistant:\n\n\"{prompt.strip()}\"\n\n"
            f"They then wrote down a criterion they wanted the assistant's answer to meet:\n\n"
            f"\"{rule.text}\"")


def annotate(rules: list[Rule], rows: list[dict], family: str,
             out: pathlib.Path) -> list[dict]:
    fc = ForcedChoice(FAMILIES[family])
    recs = []
    for rule, row in zip(rules, rows):
        ctx = context_for(rule, row["prompt"])
        rec = {"rule_id": rule.rule_id, "family": family}
        for f in FIELDS:
            v, m, dist = fc.ask(ctx, f)
            rec[f.name] = v
            rec[f"{f.name}__margin"] = round(m, 4)
            rec[f"{f.name}__dist"] = [round(x, 4) for x in dist]
        recs.append(rec)
    fc.close()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(json.dumps(r) for r in recs))
    return recs


def merge(a: list[dict], b: list[dict]) -> tuple[list[dict], dict]:
    """Agreement gate. A field survives only if both instruments chose it and both cleared the
    margin floor; otherwise UNRECOVERABLE. Returns (merged, per-field agreement)."""
    by_b = {r["rule_id"]: r for r in b}
    merged, agree, total = [], {f.name: 0 for f in FIELDS}, 0
    for ra in a:
        rb = by_b.get(ra["rule_id"])
        if rb is None:
            continue
        total += 1
        m = {"rule_id": ra["rule_id"]}
        for f in FIELDS:
            same = ra[f.name] == rb[f.name]
            agree[f.name] += same
            ok = same and min(ra[f"{f.name}__margin"], rb[f"{f.name}__margin"]) >= MARGIN_FLOOR
            m[f.name] = ra[f.name] if ok else UNRECOVERABLE
            m[f"{f.name}__agreed"] = same
            m[f"{f.name}__min_margin"] = round(
                min(ra[f"{f.name}__margin"], rb[f"{f.name}__margin"]), 4)
        merged.append(m)
    rates = {k: round(v / total, 4) for k, v in agree.items()} if total else {}
    return merged, {"n": total, "agreement": rates}
