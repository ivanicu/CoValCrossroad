"""A05 -- What KIND of value does compression silence?

CoVal-core preserves consensus items better than polarized ones.  That says
compression loses conflict.  It does not say WHICH VALUES the conflict was about -- and that
is the decision-relevant question, because "the core drops disputed items" is
tolerable if the disputed items are stylistic, and serious if they are about
autonomy, legality, or who gets harmed.

This assigns every one of the 15,248 full criteria to value families with a
transparent, auditable lexicon (no model, no embedding -- so the taxonomy can be
inspected and disputed line by line), then cross-tabulates family against:

  * visibility   singleton write-in vs shared seed
  * polarization sign disagreement among raters
  * survival     does a semantically near item appear in the prompt's core

Survival is computed lexically (token-overlap).  Two independent instruments
agreeing is evidence; one instrument repeated is not.

  ** CORRECTION 2026-07-28. **  This docstring used to open with "The prior
  analysis established that CoVal-core preserves consensus items better than
  polarized ones (embedding similarity 0.736 vs 0.520)", and justified the
  lexical measure as "a different instrument from the one that produced the
  0.736/0.520 result".  A construct review went looking for that result.  It
  appears in this one docstring, entered in the commit that created the file,
  and is computed NOWHERE -- not in this repository and not in its history
  (`git log --all -S"0.736"`).  It was inherited from the source package and
  cited as established without ever being checked.

  So this round's own argument was standing on ONE instrument, inside a
  paragraph explaining that one instrument is not enough.  The number is not
  refuted -- it is UNVERIFIED, which is not an acquittal, and it has been
  removed from the reasoning rather than repaired.

  `second_instrument.py` supplies the second measure that was always supposed
  to be here: TF-IDF cosine against the same core, thresholded to match this
  round's overall survival rate so the comparison tests the instrument and not
  the cutoff.  Result: the polarization penalty is negative in 11 of 11
  families under both, and the family ordering agrees at Spearman rho=+0.891
  (p=2.3e-4).  The claim holds.

  Residual gap, stated because the agreement does not close it: BOTH measures
  are lexical.  A criterion that survives in meaning but not in wording is
  invisible to both, so their agreement cannot rule out a shared blindness to
  paraphrase -- and the embedding result that would have covered exactly that
  gap is the one that could not be found.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = str(_HERE.parents[2])
_RES = str(_HERE / "results")

# Auditable lexicon. Each family is a list of stems; a criterion may belong to
# several. Deliberately conservative: unmatched items are reported as 'other'
# rather than forced into a family.
FAMILIES: dict[str, tuple[str, ...]] = {
    "safety_harm": ("harm", "danger", "safe", "unsafe", "risk", "suicid", "self-harm",
                    "violen", "weapon", "abuse", "crisis", "hotline", "emergency", "lethal"),
    "accuracy_evidence": ("accurat", "factual", "correct", "evidence", "cite", "citation",
                          "source", "research", "study", "data", "statistic", "verif",
                          "misinform", "false", "true", "hallucin"),
    "legality_policy": ("legal", "illegal", "law", "lawyer", "attorney", "regulat",
                        "polic", "compliance", "rights", "liabilit", "jurisdiction"),
    "autonomy_choice": ("autonom", "decide for", "own decision", "their choice",
                        "user decid", "not tell", "respect the user", "agency",
                        "let the user", "personal choice", "self-determin"),
    "balance_plurality": ("both sides", "multiple perspective", "balanc", "differing",
                          "various view", "range of", "alternativ", "counterargument",
                          "nuanc", "differing opinion", "pros and cons", "trade-off",
                          "tradeoff", "acknowledge disagree"),
    "neutrality_nonjudgment": ("neutral", "unbiased", "without judg", "non-judg",
                               "impartial", "not moraliz", "avoid preach", "lectur",
                               "condescend", "not push", "opinionated"),
    "empathy_tone": ("empath", "compassion", "supportive", "kind", "respectful",
                     "tone", "warm", "sensitiv", "validat", "dismissive", "polite"),
    "actionability": ("actionable", "step", "practical", "concrete", "specific advice",
                      "how to", "guidance", "recommend", "suggestion", "next step",
                      "example"),
    "clarity_format": ("clear", "concise", "brief", "short", "length", "bullet",
                       "format", "structur", "readab", "jargon", "plain language",
                       "organiz"),
    "professional_referral": ("professional", "expert", "doctor", "therapist",
                              "counsel", "specialist", "seek help", "consult a"),
    "cultural_context": ("cultur", "religio", "countr", "local", "region", "language",
                         "tradition", "communit", "context-specific", "western"),
    "privacy_consent": ("privacy", "consent", "confidential", "personal data",
                        "identif", "anonym", "disclose"),
}


def families_of(text: str) -> list[str]:
    t = text.lower()
    hits = [f for f, stems in FAMILIES.items() if any(s in t for s in stems)]
    return hits or ["other"]


STOP = set("""a an the and or of to in for on with is are be that this it as at by from not
if you your they their we our i my do does should must can will would could may might
when which who whom whose what how why than then there here about into over under""".split())


def toks(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z']+", s.lower()) if len(w) > 2 and w not in STOP}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--rubrics", type=Path, default=Path(_ROOT + "/data/conversation_rubrics.jsonl"))
    p.add_argument("--out", type=Path, default=Path(_RES + "/a05_value_taxonomy.json"))
    p.add_argument("--survival-threshold", type=float, default=0.34)
    a = p.parse_args()

    rows = []
    for line in open(a.rubrics, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        core = [c["criterion"] for c in (rec.get("coval_core") or [])]
        core_toks = [toks(c) for c in core]
        items = rec.get("coval_full") or []
        raters = {s["annotator_id"] for it in items for s in it.get("scores") or []}
        thr = max(2, (len(raters) + 1) // 2)
        for it in items:
            sc = [float(s["score"]) for s in it.get("scores") or []]
            if not sc:
                continue
            arr = np.array(sc)
            n = len(arr)
            pos = float((arr > 0).mean())
            neg = float((arr < 0).mean())
            t = toks(it["criterion"])
            best = 0.0
            for ct in core_toks:
                if t or ct:
                    j = len(t & ct) / max(len(t | ct), 1)
                    best = max(best, j)
            rows.append({
                "criterion": it["criterion"],
                "n": n,
                "shared": n >= thr,
                "mean": float(arr.mean()),
                "polarized": bool(pos > 0 and neg > 0 and min(pos, neg) >= 0.25),
                "survives": best >= a.survival_threshold,
                "best_overlap": best,
                "families": families_of(it["criterion"]),
            })

    print(f"criteria classified: {len(rows):,}")
    fam_count = Counter(f for r in rows for f in r["families"])
    print(f"unmatched ('other'): {fam_count['other']:,} "
          f"({fam_count['other']/len(rows):.1%}) -- lexicon coverage "
          f"{1-fam_count['other']/len(rows):.1%}")

    print(f"\n{'family':24s} {'n':>6} {'%singleton':>11} {'%polarized':>11} "
          f"{'%survives':>10} {'surv|shared':>12} {'surv|polar':>11} {'mean':>7}")
    out = {}
    for fam in list(FAMILIES) + ["other"]:
        sub = [r for r in rows if fam in r["families"]]
        if len(sub) < 30:
            continue
        shared = [r for r in sub if r["shared"]]
        polar = [r for r in sub if r["polarized"]]
        rec = {
            "n": len(sub),
            "singleton_share": float(np.mean([not r["shared"] for r in sub])),
            "polarized_share": float(np.mean([r["polarized"] for r in sub])),
            "survival": float(np.mean([r["survives"] for r in sub])),
            "survival_given_shared": float(np.mean([r["survives"] for r in shared])) if shared else None,
            "survival_given_polarized": float(np.mean([r["survives"] for r in polar])) if polar else None,
            "mean_score": float(np.mean([r["mean"] for r in sub])),
        }
        out[fam] = rec
        sg = f"{rec['survival_given_shared']:.3f}" if rec["survival_given_shared"] is not None else "  n/a"
        sp = f"{rec['survival_given_polarized']:.3f}" if rec["survival_given_polarized"] is not None else "  n/a"
        print(f"{fam:24s} {rec['n']:>6,} {rec['singleton_share']:>11.1%} "
              f"{rec['polarized_share']:>11.1%} {rec['survival']:>10.3f} {sg:>12} {sp:>11} "
              f"{rec['mean_score']:>7.2f}")

    # the headline contrast: survival penalty for being polarized, per family
    print("\n=== survival penalty from polarization (shared items only) ===")
    pen = {}
    for fam in out:
        sub = [r for r in rows if fam in r["families"] and r["shared"]]
        pol = [r["survives"] for r in sub if r["polarized"]]
        non = [r["survives"] for r in sub if not r["polarized"]]
        if len(pol) >= 20 and len(non) >= 20:
            d = float(np.mean(pol) - np.mean(non))
            pen[fam] = {"polarized": float(np.mean(pol)), "consensus": float(np.mean(non)),
                        "penalty": d, "n_pol": len(pol), "n_non": len(non)}
    for fam, v in sorted(pen.items(), key=lambda kv: kv[1]["penalty"]):
        print(f"  {fam:24s} polarized={v['polarized']:.3f}  consensus={v['consensus']:.3f}  "
              f"penalty={v['penalty']:+.3f}  (n={v['n_pol']}/{v['n_non']})")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "criteria": len(rows),
        "lexicon_coverage": 1 - fam_count["other"] / len(rows),
        "survival_threshold": a.survival_threshold,
        "families": out,
        "polarization_penalty": pen,
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
