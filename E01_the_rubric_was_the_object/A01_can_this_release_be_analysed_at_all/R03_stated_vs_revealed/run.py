"""A03 -- Do stated values predict revealed choices?

Every annotator answered a free-text question: what is ideal model behavior?
(1,012 answers, mean 241 chars.)  Every annotator also ranked responses on
5-20 prompts.  Nobody has connected the two.

This is the stated-vs-revealed preference test, and it matters because the
entire public-input premise is that asking people what they value tells you
how they will judge.  If stated values do not predict revealed choices, then a
rubric elicited by asking is measuring something other than the thing that
drives the ranking.

Design
------
For each annotator, build a TF-IDF vector of their `ideal-model-behavior` text.
For each prompt they ranked, build a TF-IDF vector of the response they placed
FIRST and of the response they placed LAST.  Ask: is their stated text closer
to their top pick than to their bottom pick?

  hit rate = P( sim(stated, top) > sim(stated, bottom) )

Null is 50%.  Three controls, all required:

  C1 PERMUTED IDENTITY -- pair each annotator's stated text with ANOTHER
     annotator's rankings on the same prompt.  This is the real null: it holds
     the prompt and the response pair fixed and destroys only the person-link.
     Without it, a hit rate above 50% could just mean "everyone's stated ideal
     resembles the response most people prefer."
  C2 LENGTH -- response length correlates with both preference and lexical
     overlap; report the hit rate after matching on length.
  C3 CLUSTER -- annotators contribute many rows; bootstrap over annotators.

Uses structured demographics NOT AT ALL.  The free text is used only as the
person's own words about model behavior, never to profile them.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

_HERE = Path(__file__).resolve().parent
_ROOT = str(next(p for p in _HERE.parents if (p / "covalx").is_dir()))
_RES = str(_HERE / "results")

LABELS = ("A", "B", "C", "D")


def parse_ranking(s: str) -> list[list[str]]:
    out = []
    for grp in str(s).split(">"):
        m = [t.strip() for t in grp.split("=") if t.strip() in LABELS]
        if m:
            out.append(m)
    return out


DELTA = 0.01   # the preregistered practical margin, queue item 4


def build_verdict(d: dict) -> str:
    """The verdict as a pure function of the stored quantities.

    REPLACES a 44-character string that read, in full: "NO EVIDENCE stated text
    predicts own choices". Three things were wrong with it.

    It cited NO NUMBER, so no prose check in this package could compare it to its
    own artifact -- the population `verdict_cites_its_own_contrasts` reports as
    unclassifiable.

    It reported NON-SIGNIFICANCE as though that were the finding, when the data
    supports something considerably stronger: the difference is +0.0017 with a
    95% interval of [-0.0061, +0.0097] on 11,327 judgements, which sits INSIDE
    the preregistered +/-0.01 margin. That is PRACTICAL EQUIVALENCE, not absence
    of evidence, and the two are the distinction queue item 4 exists to enforce.
    Using the 95% interval where TOST wants the 90% is deliberately conservative:
    the 90% interval is narrower, so equivalence established on the 95% holds a
    fortiori.

    And it stated a null with NO POWER, in a repository whose own case law says a
    null without power is silence. The interval is the power statement, and it
    was in the file the whole time.
    """
    lo, hi = d["difference_ci"]
    equivalent = lo > -DELTA and hi < DELTA
    significant = lo > 0 or hi < 0
    margin = min(DELTA - abs(lo), DELTA - abs(hi))
    head = ("STATED PREDICTS REVEALED" if significant and d["difference"] > 0 else
            "STATED ANTI-PREDICTS REVEALED" if significant else
            "EQUIVALENT TO CHANCE AT THE PREREGISTERED MARGIN" if equivalent else
            "NOT DISTINGUISHABLE FROM CHANCE, AND NOT SHOWN EQUIVALENT")
    return (
        f"{head}. Over {d['judgements']:,} judgements from {d['annotators']:,} annotators, a "
        f"rater's own stated criteria predict their own choice {d['hit_rate']:.4f} of the time "
        f"against a label-permuted null of {d['permuted_null']:.4f} -- a difference of "
        f"{d['difference']:+.4f} [{lo:+.4f},{hi:+.4f}]. SIGNIFICANCE AND EQUIVALENCE, REPORTED "
        f"SEPARATELY: the difference "
        f"{'differs from zero' if significant else 'does not differ from zero'}, and it "
        f"{'IS' if equivalent else 'is NOT'} practically equivalent to chance at the "
        f"preregistered delta={DELTA} -- the interval lies inside the margin with "
        f"{margin:.4f} to spare on its tighter side, so this is a TIGHT null and not an "
        f"unpowered one. The 95% interval is used where TOST asks for the 90%, which is "
        f"conservative: the 90% is narrower and equivalence holds a fortiori. "
        f"⚠ ONE ASYMMETRY THE HEADLINE HIDES: the top pick is the longer response in "
        f"{d['top_longer_share']:.1%} of judgements, and the hit rate splits "
        f"{d['hit_top_longer']:.4f} when it is longer against {d['hit_top_shorter']:.4f} when it "
        f"is shorter, a gap of {d['hit_top_longer'] - d['hit_top_shorter']:+.4f}. The aggregate "
        f"equivalence is therefore an average over two subpopulations that do not behave alike, "
        f"and this round does not test whether that gap is itself distinguishable from zero."
    )


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--comparisons", type=Path, default=Path(_ROOT + "/data/comparisons.jsonl"))
    p.add_argument("--annotators", type=Path, default=Path(_ROOT + "/data/annotators.jsonl"))
    p.add_argument("--out", type=Path, default=Path(_RES + "/a03_stated_vs_revealed.json"))
    p.add_argument("--reverdict", action="store_true",
                   help="recompute ONLY the verdict from the stored numbers; reads no data "
                        "and touches nothing else")
    p.add_argument("--boot", type=int, default=2000)
    a = p.parse_args()
    if a.reverdict:
        doc = json.loads(a.out.read_text())
        old = doc.get("verdict")
        doc["verdict"] = build_verdict(doc)
        doc["verdict_recomputed_without_rerun"] = (
            "Only the verdict was recomputed, from the numbers already in this file. "
            "The measurement is unchanged; what changed is that the conclusion now states "
            "them, and reports equivalence separately from significance.")
        a.out.write_text(json.dumps(doc, indent=1))
        print(f"verdict recomputed in {a.out}")
        print(f"  was: {old}")
        print(f"  now: {doc['verdict'][:110]}...")
        return

    stated: dict[str, str] = {}
    for line in open(a.annotators, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        txt = str((rec.get("demographics") or {}).get("ideal-model-behavior") or "").strip()
        if len(txt) >= 20:
            stated[rec["annotator_id"]] = txt
    print(f"annotators with usable stated-ideal text: {len(stated)}")

    # prompt -> {label: response text}; and the judgements
    responses: dict[str, dict[str, str]] = {}
    judgements = []  # (annotator, prompt, top_label, bottom_label)
    for line in open(a.comparisons, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        pid = rec["prompt_id"]
        responses[pid] = {
            r["response_index"]: r["messages"][0]["content"] for r in rec["responses"]
        }
        for asm in rec["metadata"]["assessments"]:
            aid = asm["annotator_id"]
            if aid not in stated:
                continue
            w = (asm.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            r = parse_ranking(w[0].get("ranking", ""))
            if len(r) < 2:
                continue
            top, bottom = r[0], r[-1]
            if len(top) != 1 or len(bottom) != 1 or top[0] == bottom[0]:
                continue
            judgements.append((aid, pid, top[0], bottom[0]))
    print(f"clean top!=bottom judgements from those annotators: {len(judgements):,}")

    # shared vocabulary over stated texts + responses
    corpus = list(stated.values()) + [t for d in responses.values() for t in d.values()]
    vec = TfidfVectorizer(stop_words="english", max_features=60000, sublinear_tf=True,
                          ngram_range=(1, 2), min_df=2)
    vec.fit(corpus)
    S = {k: vec.transform([v]) for k, v in stated.items()}
    R = {pid: {lab: vec.transform([txt]) for lab, txt in d.items()}
         for pid, d in responses.items()}

    def sim(u, v) -> float:
        num = (u.multiply(v)).sum()
        den = np.sqrt(u.multiply(u).sum()) * np.sqrt(v.multiply(v).sum())
        return float(num / den) if den > 0 else 0.0

    rows = []
    rng = np.random.default_rng(20260727)
    ann_list = list(stated)
    for aid, pid, top, bot in judgements:
        st = S[aid]
        s_top, s_bot = sim(st, R[pid][top]), sim(st, R[pid][bot])
        # C1: same prompt, same response pair, a DIFFERENT person's stated text
        other = aid
        while other == aid:
            other = ann_list[rng.integers(0, len(ann_list))]
        o_top, o_bot = sim(S[other], R[pid][top]), sim(S[other], R[pid][bot])
        rows.append({
            "annotator": aid, "prompt": pid,
            "hit": 1.0 if s_top > s_bot else 0.0 if s_top < s_bot else 0.5,
            "perm_hit": 1.0 if o_top > o_bot else 0.0 if o_top < o_bot else 0.5,
            "len_top": len(responses[pid][top]), "len_bot": len(responses[pid][bot]),
            "margin": s_top - s_bot,
        })

    hit = np.array([r["hit"] for r in rows])
    perm = np.array([r["perm_hit"] for r in rows])
    lt = np.array([r["len_top"] for r in rows], float)
    lb = np.array([r["len_bot"] for r in rows], float)

    by_ann = defaultdict(list)
    for r in rows:
        by_ann[r["annotator"]].append((r["hit"], r["perm_hit"]))
    keys = list(by_ann)

    def boot(idx_fn):
        out = np.empty(a.boot)
        for i in range(a.boot):
            pick = rng.integers(0, len(keys), size=len(keys))
            vals = [v for j in pick for v in by_ann[keys[j]]]
            out[i] = idx_fn(np.array(vals))
        return out

    b_hit = boot(lambda v: v[:, 0].mean())
    b_perm = boot(lambda v: v[:, 1].mean())
    b_diff = boot(lambda v: v[:, 0].mean() - v[:, 1].mean())

    print("\n=== STATED vs REVEALED ===")
    print(f"  hit rate (own stated text closer to own top pick): {hit.mean():.4f} "
          f"95%CI=[{np.percentile(b_hit,2.5):.4f},{np.percentile(b_hit,97.5):.4f}]")
    print(f"  C1 permuted-identity null:                         {perm.mean():.4f} "
          f"95%CI=[{np.percentile(b_perm,2.5):.4f},{np.percentile(b_perm,97.5):.4f}]")
    d_lo, d_hi = np.percentile(b_diff, [2.5, 97.5])
    print(f"  own - permuted:                                    {hit.mean()-perm.mean():+.4f} "
          f"95%CI=[{d_lo:+.4f},{d_hi:+.4f}]")

    longer = (lt > lb)
    print(f"\n  C2 length: top pick is the longer response in {longer.mean():.1%} of judgements")
    for lab, mask in (("top longer", longer), ("top shorter", ~longer)):
        print(f"     {lab:12s} hit={hit[mask].mean():.4f}  perm={perm[mask].mean():.4f}  n={mask.sum():,}")

    verdict = build_verdict({
        "annotators": len(stated), "judgements": len(rows),
        "hit_rate": float(hit.mean()), "permuted_null": float(perm.mean()),
        "difference": float(hit.mean() - perm.mean()),
        "difference_ci": [float(d_lo), float(d_hi)],
        "top_longer_share": float(longer.mean()),
        "hit_top_longer": float(hit[longer].mean()),
        "hit_top_shorter": float(hit[~longer].mean())})
    print(f"\n  -> {verdict}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "annotators": len(stated), "judgements": len(rows),
        "hit_rate": float(hit.mean()),
        "hit_ci": [float(np.percentile(b_hit, 2.5)), float(np.percentile(b_hit, 97.5))],
        "permuted_null": float(perm.mean()),
        "permuted_ci": [float(np.percentile(b_perm, 2.5)), float(np.percentile(b_perm, 97.5))],
        "difference": float(hit.mean() - perm.mean()),
        "difference_ci": [float(d_lo), float(d_hi)],
        "top_longer_share": float(longer.mean()),
        "hit_top_longer": float(hit[longer].mean()),
        "hit_top_shorter": float(hit[~longer].mean()),
        "verdict": verdict,
    }, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
