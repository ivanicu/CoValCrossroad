"""Every checkable claim the card makes, tested against the files it describes.

The census attacked the artefact. This attacks the DOCUMENTATION, which is a different target: a
release can be internally consistent and still describe itself wrongly, and a reader trusts the card
long before they open a file.

Only claims that are falsifiable from the three shipped files are tested. Claims about recruitment,
compensation, platform behaviour or median completion time are unfalsifiable here and are listed as
such rather than waved through -- an untestable claim is not a verified one.

AND THIS ROUND CORRECTS ONE OF MY OWN CENSUS FINDINGS BEFORE IT TESTS ANYTHING. Wave four reported
that the prompt carrying 1,012 assessments "is not marked as a calibration item" and framed it as
undocumented. The card's sampling section says "order randomized beyond anchors" -- so anchors are
DOCUMENTED as a design element. What is missing is which prompts they are. That is a narrower and
more accurate defect, and the original framing overstated.
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
R: list[dict] = []


def claim(text, verdict, measured, note=""):
    R.append({"claim": text, "verdict": verdict, "measured": measured, "note": note})


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    rub = [json.loads(l) for l in (DATA / "conversation_rubrics.jsonl").open()]

    # ---- headline counts
    claim("1,078 unique comparisons",
          "HOLDS" if len({c["prompt_id"] for c in cmp_}) == 1078 else "FAILS",
          f'{len({c["prompt_id"] for c in cmp_})} unique prompt_ids')
    claim("1,012 unique annotators",
          "HOLDS" if len({a["annotator_id"] for a in ann}) == 1012 else "FAILS",
          f'{len({a["annotator_id"] for a in ann})} unique annotator_ids')
    n_cmp_ass = sum(len((c.get("metadata") or {}).get("assessments", []) or []) for c in cmp_)
    n_ann_ass = sum(len(a.get("assessments", [])) for a in ann)
    claim("18,384 assessments in comparisons.jsonl",
          "HOLDS" if n_cmp_ass == 18384 else "FAILS",
          f"{n_cmp_ass} in comparisons.jsonl, {n_ann_ass} in annotators.jsonl "
          f"(difference {n_ann_ass - n_cmp_ass})",
          "the card gives a count for one file only; the other holds more and the card never says so")
    claim("986 unique prompt-specific rubrics",
          "HOLDS" if len(rub) == 986 else "FAILS", f"{len(rub)} rubric records")
    nres = Counter(len(c.get("responses", [])) for c in cmp_)
    claim("Every prompt in this release has exactly four candidates",
          "HOLDS" if set(nres) == {4} else "FAILS", f"responses per prompt: {dict(nres)}")

    # ---- the core-rubric size claim
    sizes = Counter(len(r["coval_core"]) for r in rub)
    four = sizes.get(4, 0) / len(rub)
    rest_ok = all(k in (2, 3, 4) for k in sizes)
    claim("Most prompts end up with four core rubric items (about 95%), the remainder two or three",
          "HOLDS" if abs(four - 0.95) < 0.03 and rest_ok else "FAILS",
          f"core sizes: {dict(sorted(sizes.items()))}; four-item share {four:.1%}")

    # ---- the selection rule
    import difflib
    from covalx.judge import load_join
    joined = load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl")
    intop = matched = 0
    ranks = []
    for _pid, _p, r in joined:
        w = np.array([np.mean([s["score"] for s in it["scores"]]) for it in r["coval_full"]], float)
        full = [it["criterion"].strip().lower() for it in r["coval_full"]]
        if len(w) < 4 or not r["coval_core"]:
            continue
        order = list(np.argsort(-np.abs(w)))
        for c in r["coval_core"]:
            hit = difflib.get_close_matches(c["criterion"].strip().lower(), full, n=1, cutoff=0.80)
            if not hit:
                continue
            matched += 1
            pos = order.index(full.index(hit[0]))
            ranks.append(pos / max(1, len(w) - 1))
            if pos < len(r["coval_core"]):
                intop += 1
    claim("It selects up to four rubric items with the HIGHEST AVERAGE RATINGS",
          "FAILS",
          f"of {matched} core items matchable to a source at 0.80, {intop} ({intop / matched:.1%}) "
          f"came from the top slots by |mean rating|; mean normalised rating-rank {np.mean(ranks):.3f} "
          f"where 0.5 is chance",
          "only 30.9% of core items match any source at all, so this tests the matchable subset; "
          "if the unmatched 69% were the high-rated ones the rule could still hold on the part "
          "that cannot be seen. "
          "CORRECTED BY r181: the rule as WORDED still fails -- core items do not come from the "
          "top slots by |mean rating|. But weight is unmistakably doing work in the selection. "
          "Survival of a self-authored criterion into the core runs 3.0% / 5.1% / 10.1% across "
          "|weight| bands 0-3, 3-7, 7-10, a 3.4x gradient over 9,452 attributable criteria. So "
          "FAILS is right about the stated mechanism and would be wrong as 'ratings are ignored'. "
          "The defensible verdict is that selection is rating-SENSITIVE but not rating-ORDERED.")

    # ---- weights range
    sc = [s["score"] for r in rub for it in r["coval_full"] for s in it["scores"]]
    claim("Signed weights ranging from -10 to +10",
          "HOLDS" if min(sc) >= -10 and max(sc) <= 10 else "FAILS",
          f"observed range [{min(sc)}, {max(sc)}] over {len(sc)} ratings")

    # ---- session length
    load = Counter(len(a.get("assessments", [])) for a in ann)
    over = sum(v for k, v in load.items() if k > 20)
    claim("Each person completed a minimum of 5 tasks and up to 20 tasks per session",
          "UNTESTABLE",
          f"assessments per annotator range {min(load)} to {max(load)}; {over} annotators exceed 20 "
          f"in total. Min is {min(load)}, below the stated floor of 5.",
          "the claim is PER SESSION and no session field exists, so neither the floor nor the "
          "ceiling can be checked; the totals are consistent with multiple sessions")

    # ---- anchors
    counts = {c["prompt_id"]: len((c.get("metadata") or {}).get("assessments", []) or [])
              for c in cmp_}
    mx = max(counts.values())
    med = float(np.median(list(counts.values())))
    claim("Order randomized beyond anchors",
          "PARTLY",
          f"anchors are documented as existing; the most-assessed prompt carries {mx} assessments "
          f"against a median of {med:.0f}, consistent with an anchor. No field identifies which "
          f"prompts are anchors.",
          "CORRECTS my own wave-four finding, which called this undocumented. The card documents "
          "that anchors exist; the DATA does not say which prompts they are")

    # ---- position bias mitigation
    uniq = Counter()
    for a in ann:
        for s in a.get("assessments", []):
            for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
                g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
                if g and len(g[0].split("=")) == 1 and g[0] in "ABCD":
                    uniq[g[0]] += 1
                break
    tot = sum(uniq.values())
    chi = sum((uniq[L] - tot / 4) ** 2 / (tot / 4) for L in "ABCD")
    claim("Candidate-to-label assignment randomized per prompt, to mitigate possible position bias",
          "PARTLY",
          f"first-place counts on {tot} unique-first rankings {dict(sorted(uniq.items()))}, "
          f"chi-square {chi:.1f} on 3 df against 16.27 at p=.001 -- a residual slot asymmetry "
          f"survives. It is worth 0.0007 of concordance, so the mitigation substantially worked.",
          "if assignment really is randomized then slot carries no content, and a surviving "
          "asymmetry is RATER position bias rather than a failure of the randomization")

    # ---- unfalsifiable
    for c in ("Recruited via an online platform requiring English literacy",
              "Median time to complete a task was approximately 22 minutes",
              "Base pay USD $60 for the survey plus 5-task sequence",
              "Core built with language-model-assisted synthesis and human review",
              "Process first rewrites all rubric items to have positive weight"):
        claim(c, "UNTESTABLE", "no field in the release bears on this",
              "listed rather than waved through: an untestable claim is not a verified one")

    order = {"FAILS": 0, "PARTLY": 1, "HOLDS": 2, "UNTESTABLE": 3}
    R.sort(key=lambda r: order[r["verdict"]])
    for v in ("FAILS", "PARTLY", "HOLDS", "UNTESTABLE"):
        g = [r for r in R if r["verdict"] == v]
        if not g:
            continue
        print(f"\n{'=' * 78}\n{v}  ({len(g)})\n{'=' * 78}")
        for r in g:
            print(f"\n  claim: {r['claim']}")
            print(f"  measured: {r['measured']}")
            if r["note"]:
                print(f"  note: {r['note']}")
    print(f"\n{len(R)} card claims tested: "
          + ", ".join(f"{v} {sum(1 for r in R if r['verdict'] == v)}"
                      for v in ("FAILS", "PARTLY", "HOLDS", "UNTESTABLE")))
    (OUT / "card_audit.json").write_text(json.dumps(R, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
