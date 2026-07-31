"""The executor factorial -- three model families and one executor with no model in it at all.

Every claim this campaign has ever made about compilation routed through ONE rebuilt 2B judge, and
twelve independent designs sharing one instrument are one instrument twelve times. The factorial
exists to put a number on how much of any effect is the instrument's.

  E1  qwen35_2b    the existing judge. Kept unchanged so every prior round remains comparable.
  E2  phi35_mini   Microsoft lineage -- different pretraining data, different tokenizer.
  E3  qwen25_7b    same lineage as E1 but 3.5x the parameters: separates FAMILY from SCALE, which a
                   two-model design cannot do.
  E4  lexical      no model. IDF-weighted content overlap, polarity-signed, thresholded.

E4 IS NOT A WEAK BASELINE, IT IS THE CONTROL THAT MAKES ONE MUTATION INTERPRETABLE. It is lexical
by construction, so the `lexical_echo` operator -- which copies surface words from the response into
the criterion without changing what the criterion asks for -- MUST move E4 and must not move a
content-sensitive executor. That gives the operator a positive control, and an executor that
behaves like E4 under it is telling you what it is reading.

All model arms score identically to r04: sigmoid(logit(" Yes") - logit(" No")) at the answer
position of the shared few-shot prompt. Nothing is quantised and no prompt is shortened, because a
gauge that changes two things at once measures neither.
"""
from __future__ import annotations

import dataclasses
import math
import pathlib
import re
import sys
from collections import Counter

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from covalx.fastjudge import FastJudge          # noqa: E402
from covalx.judge import build_prompt           # noqa: E402

MODELS = {
    "qwen35_2b": "/mnt/e/data.ai-models.local-model-store.storage.xl.private.readonly/"
                 "Qwen3.5-2B-Base",
    "phi35_mini": "/home/ivan/research/causal-publication-protocol/artifacts/"
                  "model_phi-3.5-mini-instruct",
    "qwen25_7b": "/home/ivan/research.alignment.emergent-misalignment.developmental-spectroscopy."
                 "build.lg.private.editable/models/Qwen2.5-7B-Instruct",
}

_WORD = re.compile(r"\b[a-z][a-z'-]{2,}\b")
STOP = frozenset("""the a an and or but if then than that this these those of to in on for with as
by at from is are was were be been being it its his her their our your my not no do does did have
has had will would should could can may might must about into over under more most less least very
should reply response assistant user answer question criterion""".split())


def _toks(s: str) -> list[str]:
    return [w for w in _WORD.findall(s.lower()) if w not in STOP]


@dataclasses.dataclass
class LexicalExecutor:
    """Zero-model arm. Deliberately lexical, so what it does under each mutation is a readout of
    what a purely surface-driven executor would do."""
    idf: dict[str, float] = dataclasses.field(default_factory=dict)
    name: str = "lexical"

    def fit(self, corpus: list[str]) -> "LexicalExecutor":
        df: Counter[str] = Counter()
        for d in corpus:
            df.update(set(_toks(d)))
        n = max(1, len(corpus))
        self.idf = {w: math.log(1 + n / (1 + c)) for w, c in df.items()}
        return self

    def _overlap(self, crit: str, reply: str) -> float:
        ct, rt = _toks(crit), set(_toks(reply))
        if not ct:
            return 0.0
        num = sum(self.idf.get(w, 1.0) for w in ct if w in rt)
        den = sum(self.idf.get(w, 1.0) for w in ct)
        return num / den if den else 0.0

    def score(self, criterion: str, reply: str, polarity_sign: int = +1) -> float:
        """Returns P(satisfied) in [0,1]. For a negative-polarity rule, presence of the named
        behaviour is a VIOLATION, so the overlap is inverted -- which is exactly the step the
        release's compiler performs implicitly and never records."""
        o = self._overlap(criterion, reply)
        s = 1.0 / (1.0 + math.exp(-8.0 * (o - 0.35)))
        return s if polarity_sign >= 0 else 1.0 - s


class ModelExecutor:
    def __init__(self, family: str, batch: int = 64) -> None:
        self.name = family
        self.judge = FastJudge(MODELS[family], batch=batch)

    def score_many(self, pairs: list[tuple[str, str]]) -> np.ndarray:
        return self.judge.score([build_prompt(c, r) for c, r in pairs])


def concordance(a: np.ndarray, b: np.ndarray) -> float:
    """Share of pairs ordered the same way by both executors -- the executor-variance measure that
    does not depend on either one being calibrated."""
    n = len(a)
    if n < 2:
        return float("nan")
    ia, ib = np.argsort(a), np.argsort(b)
    ra, rb = np.empty(n), np.empty(n)
    ra[ia] = np.arange(n)
    rb[ib] = np.arange(n)
    return float(np.corrcoef(ra, rb)[0, 1])
