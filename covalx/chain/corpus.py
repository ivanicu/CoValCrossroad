"""Step 2 -- the source corpus, drawn from the release rather than invented.

r142 showed the release carries real individual norms with recoverable authors: a criterion rated
by exactly one person was written by that person, and the population is separated from the lab's
pre-seeded items by an EXACTLY EMPTY band at two and three raters. So the front of the chain does
not have to be fabricated. What has to be added is the typed layer, because the release records
content and not force.

DOMAIN, locked before selection: personal health and wellbeing, non-emergency. Chosen because it is
the one domain where all five structures the programme needs can be instantiated in concrete
response pairs -- scope (general information vs personal advice), exceptions (emergency), factual
non-endorsement, a genuine categorical constraint (no diagnosis, no dosage), and emotional
acknowledgement. 80 conversations, 807 self-authored norms available.

SELECTION IS MECHANICAL AND PREREGISTERED, so that the corpus cannot be tuned toward a result:
  domain match  AND  exactly one rater  AND  40 <= len <= 300  AND  contains a finite verb

STRATIFICATION IS DELIBERATE AND MUST BE DECLARED WHEREVER THIS CORPUS IS USED. Equal numbers of
positive- and negative-weight rules are taken, which over-samples prohibitions relative to their
31.1% share of the self-authored pool. Prohibitions are the class whose force is in question, so
powering them is the point -- but it means NO RATE COMPUTED ON THIS CORPUS IS A RATE ABOUT THE
RELEASE. Anything of the form "N% of criteria ..." is invalid here by construction.
"""
from __future__ import annotations

import json
import pathlib
import re

from .record import Provenance, Rule, UNRECOVERABLE

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data"

DOMAIN = "personal_health_wellbeing_nonemergency"
DOMAIN_KW = (
    "mental health", "therapy", "therapist", "depress", "anxi", "suicid", "grief", "lonely",
    "self-harm", "panic", "counsel", "emotional support", "burnout", "symptom", "diagnos",
    "medication", "doctor", "disease", "treatment", "vaccine", "cancer", "sleep", "nutrition",
    "exercise", "pregnan", "addict", "smok", "alcohol", "weight loss", "supplement", "fatigue",
    "stress",
)
MIN_LEN, MAX_LEN = 40, 300
VERB = re.compile(
    r"\b(should|must|avoid|provide|give|offer|include|explain|acknowledge|suggest|recommend|"
    r"mention|state|ask|encourage|refer|cite|list|describe|use|make|keep|tell|present|address|"
    r"respect|clarify|note|warn|remind|do|does|be|is|are|assume|imply|claim|diagnose|prescribe)\b",
    re.I)


def _text(msgs) -> str:
    return " ".join(p for m in msgs for p in (m.get("content", {}) or {}).get("parts", []) or []
                    if isinstance(p, str))


def in_domain(prompt: str) -> bool:
    p = prompt.lower()
    return any(k in p for k in DOMAIN_KW)


def load_domain_conversations() -> list[dict]:
    out = []
    with (DATA / "conversation_rubrics.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            if in_domain(_text(r["conversation"]["messages"])):
                out.append(r)
    return out


def eligible(criterion: str) -> bool:
    t = criterion.strip()
    return MIN_LEN <= len(t) <= MAX_LEN and bool(VERB.search(t))


def build(n_per_stratum: int = 50) -> tuple[list[Rule], list[dict]]:
    """Returns (rules, provenance_rows). Rules carry UNRECOVERABLE for every typed field -- the
    annotation step fills them, and has to declare which instrument did it."""
    convs = load_domain_conversations()
    pos, neg = [], []
    for r in convs:
        cid = r["conversation"]["id"]
        prompt = _text(r["conversation"]["messages"])
        for it in r["coval_full"]:
            if len(it["scores"]) != 1:
                continue                                   # not self-authored -> no author exists
            if not eligible(it["criterion"]):
                continue
            s = it["scores"][0]
            row = {"rule_id": it["rubric_item_id"], "text": it["criterion"].strip(),
                   "author_id": s["annotator_id"], "raw_weight": float(s["score"]),
                   "conversation": cid, "prompt": prompt}
            (pos if row["raw_weight"] >= 0 else neg).append(row)

    # deterministic order: by absolute weight then id, so no rng and no seed dependence
    pos.sort(key=lambda r: (-abs(r["raw_weight"]), r["rule_id"]))
    neg.sort(key=lambda r: (-abs(r["raw_weight"]), r["rule_id"]))
    chosen = pos[:n_per_stratum] + neg[:n_per_stratum]

    rules = [Rule(rule_id=r["rule_id"], text=r["text"], polarity=UNRECOVERABLE,
                  force=UNRECOVERABLE, normative_type=UNRECOVERABLE, compensable=UNRECOVERABLE,
                  generality=UNRECOVERABLE, provenance=Provenance.SELF_AUTHORED,
                  source_conversation=r["conversation"]) for r in chosen]
    return rules, chosen


def stats() -> dict:
    convs = load_domain_conversations()
    solo = [it for r in convs for it in r["coval_full"] if len(it["scores"]) == 1]
    elig = [it for it in solo if eligible(it["criterion"])]
    neg = sum(1 for it in elig if it["scores"][0]["score"] < 0)
    return {"domain": DOMAIN, "conversations": len(convs), "self_authored": len(solo),
            "eligible": len(elig), "eligible_negative": neg,
            "eligible_negative_share": round(neg / len(elig), 4) if elig else None}
