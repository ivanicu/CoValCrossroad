"""Personal and world are the same ranking half the time. Are they the same REASON?

r168 found that the personal and world rankings are byte-identical in 52.1% of the 5,006 assessments
carrying both. That alone does not condemn the design: two questions can have the same answer and
still have collected different things, because each carries its own written rationale and the card
frames them as different perspectives -- one's own values against what would be best for the world.

So the design question is sharper than the ranking overlap suggests, and it splits three ways:

  SAME ranking, SAME rationale        the second question collected nothing. A duplicate.
  SAME ranking, DIFFERENT rationale   it collected a REASON. The answer coincides; the justification
                                      does not, and the impartial frame produced different thinking.
  DIFFERENT ranking                   it collected a preference, straightforwardly.

The first outcome is the one that matters, because it is invisible in any analysis that looks only
at rankings -- which is every analysis in this repo and, as far as the card shows, in the release.

MEASUREMENT. Rationale identity is measured three ways because "same text" is not one thing: byte
identity, identity after normalising whitespace and case, and similarity above 0.9. Reporting only
the strictest would understate duplication; reporting only the loosest would manufacture it.

AND THE DIRECTIONAL CHECK THE DESIGN IMPLIES. If the world frame does what it says, world rationales
should reach for impartial vocabulary -- society, everyone, people in general -- more than personal
ones do. That is a prediction the wording makes and it can be wrong.
"""
from __future__ import annotations

import difflib
import json
import math
import pathlib
import re
import sys
from collections import Counter

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"

IMPARTIAL = re.compile(r"\b(society|societal|everyone|the public|people in general|humanity|"
                       r"the world|community|collective|overall|as a whole|others|general public)\b",
                       re.I)
PERSONAL = re.compile(r"\b(I|me|my|myself|personally|in my opinion|I'd|I would|for me)\b")


def norm(s):
    return re.sub(r"\s+", " ", (s or "")).strip().lower()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]

    rows = []
    for a in ann:
        for s in a.get("assessments", []):
            b = s.get("ranking_blocks") or {}
            p = next((x for x in (b.get("personal") or []) if x.get("ranking")), None)
            w = next((x for x in (b.get("world") or []) if x.get("ranking")), None)
            if not p or not w:
                continue
            rows.append({
                "same_rank": p["ranking"].replace(" ", "") == w["ranking"].replace(" ", ""),
                "pr": p.get("rationale") or "", "wr": w.get("rationale") or "",
            })
    n = len(rows)
    both_rat = [r for r in rows if r["pr"].strip() and r["wr"].strip()]
    print(f"assessments with both rankings: {n}; with both rationales: {len(both_rat)}")

    exact = sum(1 for r in both_rat if r["pr"] == r["wr"])
    normed = sum(1 for r in both_rat if norm(r["pr"]) == norm(r["wr"]))
    near = sum(1 for r in both_rat
               if difflib.SequenceMatcher(None, norm(r["pr"])[:400], norm(r["wr"])[:400]).ratio()
               > 0.9)
    print(f"\nrationale identity, three ways (n={len(both_rat)}):")
    print(f"  byte-identical                 {exact:5d} ({exact / len(both_rat):.1%})")
    print(f"  identical after normalisation  {normed:5d} ({normed / len(both_rat):.1%})")
    print(f"  similarity above 0.9           {near:5d} ({near / len(both_rat):.1%})")

    same_r = [r for r in both_rat if r["same_rank"]]
    diff_r = [r for r in both_rat if not r["same_rank"]]

    def dup(rs):
        if not rs:
            return 0, 0.0
        k = sum(1 for r in rs
                if difflib.SequenceMatcher(None, norm(r["pr"])[:400], norm(r["wr"])[:400]).ratio()
                > 0.9)
        return k, k / len(rs)

    ks, fs = dup(same_r)
    kd, fd = dup(diff_r)
    print(f"\nthe three-way split:")
    print(f"  SAME ranking, near-identical rationale : {ks:5d} ({ks / len(both_rat):.1%} of all) "
          f"-- the second question collected NOTHING")
    print(f"  SAME ranking, different rationale      : {len(same_r) - ks:5d} "
          f"({(len(same_r) - ks) / len(both_rat):.1%}) -- same answer, different reason")
    print(f"  DIFFERENT ranking                      : {len(diff_r):5d} "
          f"({len(diff_r) / len(both_rat):.1%})")
    print(f"\n  rationale duplication given the same ranking: {fs:.1%}; "
          f"given a different ranking: {fd:.1%}")

    # the directional prediction the design makes
    pi = sum(1 for r in both_rat if IMPARTIAL.search(r["pr"]))
    wi = sum(1 for r in both_rat if IMPARTIAL.search(r["wr"]))
    pp = sum(1 for r in both_rat if PERSONAL.search(r["pr"]))
    wp = sum(1 for r in both_rat if PERSONAL.search(r["wr"]))
    N = len(both_rat)

    def z2(a, b):
        p1, p2 = a / N, b / N
        pooled = (a + b) / (2 * N)
        se = math.sqrt(2 * pooled * (1 - pooled) / N)
        return (p1 - p2) / se if se else float("nan")
    print(f"\nthe directional prediction: world rationales should reach for impartial vocabulary "
          f"more than personal ones")
    print(f"  impartial words   personal {pi / N:6.1%}   world {wi / N:6.1%}   "
          f"z {z2(wi, pi):+.1f}")
    print(f"  first-person      personal {pp / N:6.1%}   world {wp / N:6.1%}   "
          f"z {z2(pp, wp):+.1f}")
    verdict = ("PREDICTION HOLDS -- the world frame changes the vocabulary"
               if z2(wi, pi) > 3 else
               "PREDICTION FAILS -- the world frame does not change the vocabulary, so the two "
               "questions elicit the same kind of answer")
    print(f"  {verdict}")

    (OUT / "second_question.json").write_text(json.dumps(
        {"assessments_with_both": n, "with_both_rationales": len(both_rat),
         "rationale_identical_exact": exact, "identical_normalised": normed, "similar_over_0_9": near,
         "same_rank_and_same_rationale": ks, "same_rank_diff_rationale": len(same_r) - ks,
         "diff_rank": len(diff_r),
         "impartial_personal": pi, "impartial_world": wi,
         "firstperson_personal": pp, "firstperson_world": wp,
         "verdict": verdict}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
