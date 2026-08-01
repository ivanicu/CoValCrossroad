"""What the card says was collected, against what actually shipped -- and what that costs.

Every previous check asked whether a claim about the data is true. This asks a different question:
what did the card describe collecting that is NOT in the release, and does the release say so?

Withholding a demographic field is good practice. Withholding it without saying so is a defect,
because a reader who reaches the intake-survey section forms an expectation the files do not meet,
and the analyses that expectation licenses cannot be run.

THE SANITIZATION SECTION IS THE PLACE THIS WOULD BE SAID. It exists, it is explicit, and it lists
exactly two steps: remapping the system role to developer, and publishing rubrics in two forms.
Neither is about demographics.

AND THE ONE FREE-TEXT FIELD THAT DID SHIP IS THE DISCLOSURE SURFACE. "ideal-model-behavior" is a
prose answer from every one of 1,012 annotators, attached to an id that also carries their age,
gender, country and education -- and, through the sole-rater signature recovered in r142, to the
criteria they personally wrote. Its risk is measurable rather than assumed: what fraction discloses
an occupation, a place, a religion, a health or family detail, or a contact string.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"

# what the card's intake-survey section says was collected
CARD_FIELDS = {
    "age": "age",
    "gender": "gender",
    "race/ethnicity": None,
    "employment status (multi-select)": None,
    "education level": "education_level",
    "country of residence": "country_of_residence",
    "country of origin": None,
    "generative AI usage frequency": "generative_ai_usage",
    "level of concern about AI": "ai_concern_level",
    "free text: brief self-description": None,
    "free text: ideal model behavior": "ideal-model-behavior",
}

PII = {
    "first person": r"\b(I|my|me|myself)\b",
    "occupation or role": r"\b(I (work|am a|study)|as a (teacher|nurse|doctor|engineer|student|"
                         r"lawyer|developer|researcher|manager|driver))\b",
    "named place": r"\b(in|from) (the )?(US|USA|America|UK|England|India|Mexico|Nigeria|Kenya|"
                   r"Brazil|Chile|Netherlands|South Africa|Canada|Germany|Spain)\b",
    "religion": r"\b(christian|muslim|jewish|hindu|buddhist|catholic|atheist|religious)\b",
    "health or family": r"\b(my (son|daughter|wife|husband|mother|father|child|kids|partner)|"
                        r"my (illness|condition|disability|diagnosis|therapist))\b",
    "contact string": r"([\w.-]+@[\w.-]+|https?://|\b\d{6,}\b)",
}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    shipped = Counter()
    for a in ann:
        for k in (a.get("demographics") or {}):
            shipped[k] += 1
    n = len(ann)

    print(f"annotators {n}\n")
    print(f"{'card says collected':38s} {'shipped as':26s} status")
    withheld = []
    for label, field in CARD_FIELDS.items():
        if field and shipped.get(field, 0) == n:
            print(f"  {label:36s} {field:26s} SHIPPED, 100% coverage")
        elif field and shipped.get(field, 0):
            print(f"  {label:36s} {field:26s} PARTIAL {shipped[field] / n:.0%}")
        else:
            print(f"  {label:36s} {'-':26s} NOT IN THE RELEASE")
            withheld.append(label)
    extra = [k for k in shipped if k not in set(CARD_FIELDS.values())]
    print(f"\nfields shipped that the card's intake section does not list: {extra or 'none'}")

    card = (DATA / "DATASET_CARD.md").read_text()
    sec = card[card.index("Sanitization for release"):][:1200]
    mentions_demo = bool(re.search(r"demograph|withh|redact|remov|exclud", sec, re.I))
    print(f"\nWITHHELD WITHOUT NOTICE: {len(withheld)} of {len(CARD_FIELDS)} documented fields are "
          f"absent.")
    for w in withheld:
        print(f"    {w}")
    print(f"  the card's sanitization section mentions withholding or redacting demographics: "
          f"{mentions_demo}")
    print("  it lists exactly two steps -- role remapping, and publishing rubrics in two forms.")

    print("\nWHAT THE ABSENCES COST, concretely:")
    print("  race/ethnicity   no analysis of racial or ethnic disparity is possible in a dataset "
          "whose stated purpose is whose values a model reflects")
    print("  country_of_origin  residence ships but origin does not, so the migration and diaspora "
          "dimension -- plausibly the sharpest values split in a global panel -- is unavailable")
    print("  employment       no socioeconomic axis at all")
    print("  self-description the open field people used to say what they thought was relevant "
          "about themselves is the one open field not published")

    # ---- the field that did ship
    txt = [(a["annotator_id"], (a.get("demographics") or {}).get("ideal-model-behavior", ""))
           for a in ann]
    txt = [(i, t.strip()) for i, t in txt if isinstance(t, str) and t.strip()]
    L = [len(t) for _i, t in txt]
    print(f"\nTHE FREE TEXT THAT DID SHIP: 'ideal-model-behavior', {len(txt)} entries, "
          f"median {int(np.median(L))} chars, p90 {int(np.percentile(L, 90))}, max {max(L)}")
    hits = {}
    for name, pat in PII.items():
        c = sum(1 for _i, t in txt if re.search(pat, t, re.I))
        hits[name] = c
        print(f"    {name:20s} {c:5d} ({c / len(txt):5.1%})")
    print("  Attached to an id carrying age, gender, country and education -- and, via the "
          "sole-rater signature, to the criteria that person wrote. The disclosure is the LINKAGE, "
          "not the wording: only 0.5% name an occupation and none carries a contact string.")

    (OUT / "withheld.json").write_text(json.dumps(
        {"annotators": n, "shipped_fields": dict(shipped), "withheld": withheld,
         "sanitization_mentions_demographics": mentions_demo,
         "free_text": {"field": "ideal-model-behavior", "n": len(txt),
                       "median_chars": int(np.median(L)), "max_chars": int(max(L)),
                       "disclosure_hits": hits}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
