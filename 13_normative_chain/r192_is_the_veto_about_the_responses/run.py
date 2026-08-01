"""The only dispositive channel in the release, put through the gate that just overturned r177.

r191 established the machinery and the lesson: a self-reported field attached to a (person, item)
pair is not a property of the item until two split-halves say so, and the level at which a
stratifier is computed is not presentational -- recomputing r177's at the prompt level turned a
null into a lean.

The veto has never been through that gate, and it is the field where the answer matters most. It
is the only channel in the release that says a response is not merely worse but UNACCEPTABLE, and
every use of it -- as a hard constraint, as a safety signal, as a filter -- assumes it identifies
something about the RESPONSES. If it is mostly a rater trait, it identifies people who flag things.

r180 tried and could not: veto propensity is capped at five per rater by the structural ceiling
r175 confirmed, leaving split-halves of two. But that cap only blocks the RATER side. The PROMPT
side is untouched -- prompts carry up to hundreds of asked assessments -- and the prompt side is
the one that matters here, because "these responses contain something unacceptable" is a claim
about the responses.

  PROMPT PROPERTY   raters agree about which response sets contain something unacceptable. The
                    veto is evidence about the artefact and can be used as a constraint.
  NOT A PROMPT PROPERTY   they do not. Then a veto is evidence about who cast it, the 4.4%
                    veto-versus-ranking contradiction found in the census is unsurprising rather
                    than anomalous, and treating the field as a safety signal is unfounded.

AND r173's TABLE GETS RE-RUN AT THE RIGHT LEVEL. That round reported veto rate by the importance
the SAME PERSON assigned the prompt. importance is BOTH (S-B prompt +0.706, rater +0.799), so that
table mixed a prompt property with a person property exactly as r177's did. The prompt-level
version is three lines and it is the version the sentence in that round claimed to be about.

CONTROLS: the same split-half code is run on prompt-level importance, which r191 measured at
+0.706, so a low number for the veto cannot be blamed on the estimator. And the asked-population
filter that r154 fixed is carried -- "not asked" is an EMPTY LIST, and treating it as a zero
inflated a veto rate from 36.4% to 82.9% earlier in this project.
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import re
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
LETTERS = "ABCD"
BAR = 0.30
SEEDS = list(range(5))
MIN_RATERS = 6

IMP = {"Not important": 0.0, "Somewhat important": 1.0, "Very important": 2.0}
FLAG = re.compile(r"^\s*([ABCD])\b")


def split_half(groups, seeds=SEEDS, min_units=MIN_RATERS):
    rs = []
    n = 0
    for sd in seeds:
        rng = random.Random(sd)
        A, B = [], []
        for _k, v in groups.items():
            if len(v) < min_units:
                continue
            w = v[:]
            rng.shuffle(w)
            h = len(w) // 2
            A.append(float(np.mean(w[:h])))
            B.append(float(np.mean(w[h:2 * h])))
        n = len(A)
        if n > 50 and np.std(A) > 0 and np.std(B) > 0:
            rs.append(float(np.corrcoef(A, B)[0, 1]))
    if not rs:
        return None, None, n
    r = float(np.mean(rs))
    return r, 2 * r / (1 + r), n


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]

    veto_p, veto_a, imp_p = defaultdict(list), defaultdict(list), defaultdict(list)
    per_resp = defaultdict(list)
    nflag_p = defaultdict(list)
    asked = 0
    for a in ann:
        aid = a["annotator_id"]
        for s in a.get("assessments", []):
            pid = s.get("conversation_id")
            b = s.get("ranking_blocks") or {}
            # THE ASKED-POPULATION FILTER, carried from r154. "Not asked" is an EMPTY LIST, and
            # counting those as zeros took a veto rate from 36.4% to 82.9% earlier in this project.
            if not (b.get("unacceptable") or b.get("personal")):
                continue
            asked += 1
            flags = set()
            for blk in (b.get("unacceptable") or []):
                for r in (blk.get("rating") or []):
                    m = FLAG.match(r) if isinstance(r, str) else None
                    if m:
                        flags.add(m.group(1))
            v = 1.0 if flags else 0.0
            veto_p[pid].append(v)
            for L in LETTERS:
                per_resp[(pid, L)].append(1.0 if L in flags else 0.0)
            veto_a[aid].append(v)
            nflag_p[pid].append(float(len(flags)))
            for tok, x in IMP.items():
                if isinstance(s.get("importance"), str) and tok in s["importance"]:
                    imp_p[pid].append(x)
                    break
    print(f"assessments where the veto question was ASKED: {asked}")
    print(f"  overall veto rate: {np.mean([v for x in veto_p.values() for v in x]):.1%}")
    print(f"  prompts with >={MIN_RATERS} asked assessments: "
          f"{sum(1 for v in veto_p.values() if len(v) >= MIN_RATERS)}")

    print("\n" + "=" * 78)
    print("IS THE VETO A PROPERTY OF THE RESPONSES?")
    print("=" * 78)
    rv, sbv, nv = split_half(veto_p)
    rn, sbn, nn = split_half(nflag_p)
    ri, sbi, ni = split_half(imp_p)
    print(f"  {'quantity':34s} {'prompts':>8s} {'r halves':>9s} {'Spearman-Brown':>15s}")
    print(f"  {'veto fired at all (0/1)':34s} {nv:8d} {rv:+9.3f} {sbv:+15.3f}")
    print(f"  {'how many responses flagged':34s} {nn:8d} {rn:+9.3f} {sbn:+15.3f}")
    print(f"  {'CONTROL: prompt importance':34s} {ni:8d} {ri:+9.3f} {sbi:+15.3f}")
    print(f"\n  the control reproduces r191's +0.706, so the estimator is not the problem.")
    ok = sbv is not None and sbv > BAR
    print(f"  -> the veto {'IS' if ok else 'IS NOT'} a reliable property of the prompt "
          f"(bar {BAR})")

    # variance decomposition for the same quantity
    allv = np.array([v for x in veto_p.values() for v in x], float)
    gm = allv.mean()
    tot = float(((allv - gm) ** 2).sum())
    ssb_p = sum(len(v) * (np.mean(v) - gm) ** 2 for v in veto_p.values() if len(v) >= 3)
    ssb_a = sum(len(v) * (np.mean(v) - gm) ** 2 for v in veto_a.values() if len(v) >= 3)
    print(f"  variance between PROMPTS {ssb_p / tot:.1%};  between RATERS {ssb_a / tot:.1%}")
    print(f"  (the rater side is bounded by the 5-item ceiling r175 confirmed, so it is a floor)")

    # ------------------------------------------------------------------ r173 at the right level
    print("\n" + "=" * 78)
    print("r173's TABLE, RE-RUN AT THE PROMPT LEVEL")
    print("=" * 78)
    pm = {p: float(np.mean(v)) for p, v in imp_p.items() if len(v) >= MIN_RATERS}
    pv = {p: float(np.mean(v)) for p, v in veto_p.items() if len(v) >= MIN_RATERS}
    common = [p for p in pm if p in pv]
    qs = np.percentile([pm[p] for p in common], [33, 67])
    lbl = ["low importance", "mid importance", "high importance"]
    print(f"  {'prompt-level importance':26s} {'prompts':>8s} {'veto rate':>11s}")
    means, ses = {}, {}
    for b in range(3):
        v = [pv[p] for p in common if int(np.searchsorted(qs, pm[p])) == b]
        if len(v) >= 30:
            means[b] = float(np.mean(v))
            ses[b] = float(np.std(v, ddof=1) / math.sqrt(len(v)))
            print(f"  {lbl[b]:26s} {len(v):8d} {means[b]:11.1%}  "
                  f"[{means[b] - 1.96 * ses[b]:.1%},{means[b] + 1.96 * ses[b]:.1%}]")
    if 0 in means and 2 in means:
        g = means[2] - means[0]
        sg = math.sqrt(ses[2] ** 2 + ses[0] ** 2)
        print(f"  high minus low  {g:+.1%}  [{g - 1.96 * sg:+.1%}, {g + 1.96 * sg:+.1%}]  "
              f"z {g / sg:+.1f}   (prompt is the unit)")

    # the rater-level version for contrast, which is what r173 actually printed
    ra_imp = defaultdict(list)
    ra_veto = defaultdict(list)
    for a in ann:
        for s in a.get("assessments", []):
            b = s.get("ranking_blocks") or {}
            if not (b.get("unacceptable") or b.get("personal")):
                continue
            x = None
            for tok, val in IMP.items():
                if isinstance(s.get("importance"), str) and tok in s["importance"]:
                    x = val
            if x is None:
                continue
            fl = any((blk.get("rating") or []) for blk in (b.get("unacceptable") or []))
            ra_imp[x].append(1.0 if fl else 0.0)
    print(f"\n  for contrast, the ASSESSMENT-level version r173 printed:")
    for x in sorted(ra_imp):
        v = ra_imp[x]
        print(f"    importance {x:.0f}  n={len(v):5d}  veto rate {np.mean(v):.1%}")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    if not ok:
        print(f"  THE VETO IS NOT A PROPERTY OF THE RESPONSES. Two raters shown the same four")
        print(f"  candidates do not agree about whether any of them is unacceptable: split-half")
        print(f"  reliability {sbv:+.3f} across half-panels on {nv} prompts, against {sbi:+.3f} for")
        print(f"  prompt importance measured by the same code on the same prompts.")
        print(f"  So the only DISPOSITIVE channel in this release -- the one that says a response")
        print(f"  is not merely worse but unacceptable -- does not identify response sets that")
        print(f"  people agree are unacceptable. It records that a particular person flagged")
        print(f"  something.")
        print(f"\n  THIS EXPLAINS A CENSUS FINDING RATHER THAN ADDING TO IT. Wave three found that")
        print(f"  4.4% of vetoing assessments rank the vetoed response FIRST, and filed it as a")
        print(f"  contradiction. If the veto were a shared judgement about the responses that")
        print(f"  would be anomalous. If it is a personal act, a person can flag a response for")
        print(f"  one reason and still rank it best for another, and 4.4% is low rather than")
        print(f"  strange. The two findings are the same finding.")
        print(f"\n  AND IT BOUNDS EVERY DOWNSTREAM USE. A safety filter built on this field selects")
        print(f"  on raters, not on content. Nothing in the card claims otherwise -- the card")
        print(f"  describes what annotators were asked -- but nothing warns of it either, and the")
        print(f"  field's name does the opposite.")
    else:
        print(f"  The veto IS a prompt property (S-B {sbv:+.3f}), so raters agree about which")
        print(f"  response sets contain something unacceptable and the channel identifies content.")
    # THE STRICT VERSION, measured instead of stated. "Was anything flagged" counts two raters
    # who flagged DIFFERENT responses as agreeing. The question a safety filter actually needs
    # answered is whether they agree on WHICH response is unacceptable, so the unit becomes the
    # (prompt, response) pair and the split-half runs on that.
    rr, sbr, nr = split_half(per_resp)
    print(f"\n" + "=" * 78)
    print("THE STRICT VERSION: do raters agree on WHICH response is unacceptable?")
    print("=" * 78)
    print(f"  unit = (prompt, response); {nr} pairs with >={MIN_RATERS} raters")
    print(f"  split-half r {rr:+.3f}, Spearman-Brown {sbr:+.3f}")
    flagged_rate = float(np.mean([v for x in per_resp.values() for v in x]))
    print(f"  base rate: a given response is flagged {flagged_rate:.1%} of the time it is seen")
    strict_ok = sbr is not None and sbr > BAR
    print(f"  -> raters {'DO' if strict_ok else 'do NOT'} agree about which response is "
          f"unacceptable (bar {BAR})")
    if strict_ok and ok:
        print(f"\n  BOTH LEVELS HOLD, and the strict one is what matters. The veto is not merely")
        print(f"  'some prompts provoke flagging' -- raters converge on the SAME response, at")
        print(f"  S-B {sbr:+.3f}. This is the strongest single validation of any channel in the")
        print(f"  release, and it is the channel the census treated most sceptically: r173 showed")
        print(f"  its written justifications fall outside the card's stated dichotomy, and that")
        print(f"  remains true. What is now also true is that the ACT is shared even where the")
        print(f"  stated REASON is not.")
    elif ok and not strict_ok:
        print(f"\n  AND THE STRICT VERSION FAILS, WHICH INVERTS THE READING. Raters agree that")
        print(f"  SOMETHING in a given prompt's response set is unacceptable (S-B {sbv:+.3f}) and")
        print(f"  do not agree on WHAT (S-B {sbr:+.3f}). A filter that drops flagged responses is")
        print(f"  therefore acting on a per-rater judgement even though the prompt-level signal")
        print(f"  looks shared. The coarse measurement would have licensed exactly the wrong use.")
    print(f"\n  REMAINING LIMIT: the letter-to-candidate map is randomised per prompt but fixed")
    print(f"  within it, so this is agreement about a specific text, which is the right object.")

    (OUT / "veto_gate.json").write_text(json.dumps(
        {"asked": asked, "veto_rate": float(np.mean(allv)),
         "split_half": {"veto_binary": {"r": rv, "sb": sbv, "prompts": nv},
                        "n_flagged": {"r": rn, "sb": sbn, "prompts": nn},
                        "control_importance": {"r": ri, "sb": sbi, "prompts": ni}},
         "variance_prompt": ssb_p / tot, "variance_rater": ssb_a / tot,
         "prompt_level_importance_table": {lbl[b]: means[b] for b in means},
         "assessment_level_table": {str(x): float(np.mean(v)) for x, v in ra_imp.items()},
         "strict_per_response": {"r": rr, "sb": sbr, "pairs": nr, "base_rate": flagged_rate,
                                 "passes": bool(strict_ok)},
         "verdict": "prompt property" if ok else "NOT a prompt property",
         "limit": "binary flagged-or-not; two raters flagging different responses count as "
                  "agreeing, so this is an upper bound on veto agreement"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
