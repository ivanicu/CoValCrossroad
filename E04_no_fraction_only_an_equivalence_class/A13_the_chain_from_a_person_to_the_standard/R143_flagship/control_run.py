"""Positive control for the typed annotator, plus the chance correction the raw rates lack.

Two independent families agreed on only 46% of `force`, 39% of `normative_type`, 26% of
`confidence` and 16% of `generality` when reading real crowd-written criteria. Three worlds explain
that and they demand different responses:

  W1  the fields are genuinely underdetermined by the text. Then the typed layer CANNOT be
      reconstructed post hoc from a released dataset, and it has to be collected from authors at
      write time -- which changes what the whole programme can be built on.
  W2  the instruments are unfit for this task. Then the low agreement is silence, not evidence, and
      nothing about the release follows from it.
  W3  the question wording is bad. A design failure, fixable, and it would masquerade as W1.

The separator: run the SAME annotator, with the SAME wording, on criteria whose field value is
unambiguous BY CONSTRUCTION. "Never do this under any circumstances, no matter what else the answer
achieves" is a veto or the instrument cannot read English.

  high accuracy on constructed + low agreement on real  -> W1 survives, W2/W3 die
  low accuracy on constructed                           -> W2 or W3; the real-criteria number is
                                                            INADMISSIBLE and must not be reported

And the raw agreement rates are corrected here, because they are not interpretable as they stand:
99% agreement on a binary field where both models answer the same way 99% of the time is chance.
Cohen's kappa is computed against each model's own marginals, and a field where both instruments
are degenerate is reported as degenerate rather than as agreement.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())))

from covalx.chain.annotate import FIELDS, FAMILIES, ForcedChoice  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parent / "results"

PROMPT = ("Should I take melatonin to help me sleep? I have been having trouble for a few weeks.")

# (text, field, known value). Every item is unambiguous on ITS OWN field by construction; no item
# is used to score a field it was not written for.
CONTROL: list[tuple[str, str, str]] = [
    # ---- force: the distinction the release cannot express at all
    ("Never state a specific dosage, under any circumstances, no matter how good the rest of the "
     "answer is.", "force", "veto"),
    ("Under no condition may the answer claim to diagnose the user; this is unacceptable even if "
     "everything else is excellent.", "force", "veto"),
    ("It is absolutely forbidden to tell the user to stop a prescribed medication, whatever else "
     "the answer does well.", "force", "veto"),
    ("It would be slightly nicer if the answer used shorter paragraphs.", "force",
     "soft_preference"),
    ("A friendly opening line is a small plus, among many other things that matter.", "force",
     "soft_preference"),
    ("All else being equal, a marginally warmer tone is somewhat preferable.", "force",
     "soft_preference"),
    # ---- normative_type
    ("The answer must never recommend an unapproved substance.", "normative_type", "veto"),
    ("The user is entitled to be told when the assistant is uncertain.", "normative_type", "right"),
    ("First acknowledge the difficulty, then give the information, then suggest next steps.",
     "normative_type", "procedure"),
    ("I simply prefer answers that open with a short summary.", "normative_type", "preference"),
    ("Honesty should guide the response in general.", "normative_type", "principle"),
    ("When the evidence is mixed, the answer should say that the evidence is mixed.",
     "normative_type", "uncertainty"),
    # ---- generality
    ("For this specific question about melatonin and nothing else, mention the 3 mg figure.",
     "generality", "this_prompt_only"),
    ("Only in this one conversation, keep the answer under fifty words.", "generality",
     "this_prompt_only"),
    ("For any question about sleep and supplements, recommend consulting a pharmacist.",
     "generality", "this_topic_class"),
    ("Whenever the topic is health, the answer should name its sources.", "generality",
     "this_topic_class"),
    ("In every conversation on any subject whatsoever, the assistant should be honest.",
     "generality", "general_policy"),
    ("As a matter of overall policy across all topics, never fabricate a citation.",
     "generality", "general_policy"),
    # ---- confidence
    ("This is settled and not open to debate: the answer must not diagnose.", "confidence",
     "certain"),
    ("It is definitely required that the answer mention side effects.", "confidence", "certain"),
    ("I am fairly sure the answer should mention side effects, though I could be wrong.",
     "confidence", "probable"),
    ("I think, probably, the answer ought to suggest a pharmacist.", "confidence", "probable"),
    ("I am really not sure about this, but maybe the answer could mention dosage timing?",
     "confidence", "tentative"),
    ("Perhaps -- and I hesitate to say it -- a shorter answer might possibly be better.",
     "confidence", "tentative"),
    # ---- polarity, as the comparator that already agrees at 71% on real data
    ("The answer must always recommend seeing a doctor.", "polarity", "require"),
    ("The answer must never recommend seeing a doctor.", "polarity", "forbid"),
    ("It is better if the answer mentions side effects.", "polarity", "prefer"),
    ("It is better if the answer does not mention side effects.", "polarity", "discourage"),
    ("The answer may mention side effects or not; either is fine.", "polarity", "permit"),
    # ---- compensable
    ("No amount of other merit can make up for giving a dosage number.", "compensable", "false"),
    ("If the rest of the answer is strong enough, a missing summary line is fine.", "compensable",
     "true"),
]

BY_FIELD = {f.name: f for f in FIELDS}


def kappa(a: list[str], b: list[str]) -> tuple[float, bool]:
    """Cohen's kappa plus a degeneracy flag. A field where one option holds >=95% of BOTH models'
    answers is reported as degenerate: raw agreement there is chance and means nothing."""
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum((ca[k] / n) * (cb[k] / n) for k in set(ca) | set(cb))
    k = (po - pe) / (1 - pe) if pe < 1 else float("nan")
    deg = max(ca.values()) / n >= 0.95 and max(cb.values()) / n >= 0.95
    return k, deg


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs=2, default=["phi35_mini", "qwen25_3b"])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    # ---- chance-correct the real-criteria agreement already measured
    real = {}
    for fam in args.families:
        p = OUT / f"annot_{fam}.jsonl"
        real[fam] = [json.loads(l) for l in p.open()] if p.exists() else []
    corrected = {}
    if all(real.values()):
        A, B = real[args.families[0]], real[args.families[1]]
        idx = {r["rule_id"]: r for r in B}
        pairs = [(a, idx[a["rule_id"]]) for a in A if a["rule_id"] in idx]
        for f in FIELDS:
            ka, deg = kappa([a[f.name] for a, _b in pairs], [b[f.name] for _a, b in pairs])
            top_a = Counter(a[f.name] for a, _b in pairs).most_common(1)[0]
            corrected[f.name] = {
                "raw_agreement": round(sum(a[f.name] == b[f.name] for a, b in pairs) / len(pairs), 4),
                "cohens_kappa": round(ka, 4), "degenerate": deg,
                "modal_answer": top_a[0], "modal_share": round(top_a[1] / len(pairs), 4)}

    # ---- the positive control
    res = {fam: [] for fam in args.families}
    for fam in args.families:
        fc = ForcedChoice(FAMILIES[fam])
        for text, field, known in CONTROL:
            ctx = (f"A person was shown this question asked of an AI assistant:\n\n\"{PROMPT}\"\n\n"
                   f"They then wrote down a criterion they wanted the assistant's answer to "
                   f"meet:\n\n\"{text}\"")
            got, margin, _d = fc.ask(ctx, BY_FIELD[field])
            res[fam].append({"field": field, "known": known, "got": got,
                             "margin": round(margin, 4), "correct": got == known})
        fc.close()

    acc = {}
    for f in FIELDS:
        rows = {fam: [r for r in res[fam] if r["field"] == f.name] for fam in args.families}
        if not rows[args.families[0]]:
            continue
        n = len(rows[args.families[0]])
        chance = 1.0 / len(f.options)
        acc[f.name] = {
            "n_control": n, "chance": round(chance, 3),
            **{fam: round(sum(r["correct"] for r in rows[fam]) / n, 3) for fam in args.families},
            "both_correct": round(sum(a["correct"] and b["correct"]
                                      for a, b in zip(rows[args.families[0]],
                                                      rows[args.families[1]])) / n, 3),
        }

    out = {"control_accuracy": acc, "real_criteria_agreement_corrected": corrected,
           "families": args.families, "n_control_items": len(CONTROL)}
    (OUT / "annot_control.json").write_text(json.dumps(out, indent=1))
    (OUT / "annot_control_raw.json").write_text(json.dumps(res, indent=1))

    print(f"{'field':16s} {'ctl n':>5} {'chance':>7} "
          f"{args.families[0][:10]:>11} {args.families[1][:10]:>11} {'both':>6} | "
          f"{'real raw':>9} {'kappa':>7}  flag")
    for f in FIELDS:
        a = acc.get(f.name)
        c = corrected.get(f.name, {})
        if not a:
            continue
        flag = "DEGENERATE" if c.get("degenerate") else ""
        print(f"{f.name:16s} {a['n_control']:5d} {a['chance']:7.3f} "
              f"{a[args.families[0]]:11.3f} {a[args.families[1]]:11.3f} {a['both_correct']:6.3f} | "
              f"{c.get('raw_agreement', float('nan')):9.3f} {c.get('cohens_kappa', float('nan')):7.3f}"
              f"  {flag}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
