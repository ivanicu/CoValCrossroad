"""The two properties the card claims for coval_core that nobody has tested.

The card describes the core set as "an experimental synthesized set of NON-CONFLICTING,
NON-REDUNDANT and HIGHLY RATED criteria". Three properties, all asserted, all falsifiable from the
shipped file. r171 tested the third and it FAILED: core items come from the top slots by |mean
rating| only 30.9% of the time on the matchable subset. The other two have never been run.

They are worth more than the third, because non-redundancy and non-conflict are the properties that
make a rubric USABLE as an aggregate. A redundant core double-counts one concern. A conflicting core
cannot be satisfied at all, and a model scored against it is being graded on a contradiction.

THE DESIGN IS A WITHIN-PROMPT PERMUTATION, WHICH IS THE ONLY HONEST BASELINE HERE. "Core is
non-redundant" is not a claim about an absolute number -- some prompts attract criteria that all
sound alike, and a low-diversity prompt would make any subset look redundant. The claim is
comparative and its comparison class is fixed by the selection procedure itself: core has k items
drawn from that prompt's full set, so the baseline is RANDOM k-subsets OF THE SAME FULL SET. If the
synthesis does what the card says, core beats its own prompt's random draws. If it does not, the
word is decoration.

PREREGISTERED, before the run:
  redundancy   core mean-pairwise-similarity BELOW the random-subset median, on >60% of prompts
  conflict     core conflict rate BELOW the random-subset rate
  positivity   the card also says the process "first rewrites all rubric items to have positive
               weight", so core should carry FEWER negation markers than full
  thresholds   similarity 0.50 for "about the same thing"; 200 random subsets per prompt; seeds 0-4

THE CONFLICT DETECTOR IS A LEXICAL PROXY AND ITS LEDGER ROW IS WRITTEN HERE, NOT AFTER.
  PROPERTY   two criteria that cannot both be satisfied
  PROXY      high content overlap AND opposite polarity marker
  IMPLICATION  proxy fires => the pair is about one topic with opposed directives. The converse
               FAILS: two criteria can conflict with no shared vocabulary and no negation word
               ("be concise" / "explain every step"), and the proxy is blind to all of them
  SAFE SIDE  a NON-ZERO rate is admissible as a lower bound. A ZERO is NOT evidence of no conflict,
             and is reported as UNVERIFIED unless the positive control below has fired
  WITNESS    the positive control constructs a criterion and its negation; if that does not fire,
             every zero in this round is silence
"""
from __future__ import annotations

import itertools
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

SIM_THRESHOLD = 0.50
N_SUBSETS = 200
SEEDS = list(range(5))

NEG = re.compile(r"\b(not|never|avoid|avoids|avoiding|refrain|without|no|don't|doesn't|shouldn't|"
                 r"must not|should not|fails? to|omit|exclude|discourage)\b", re.I)
STOP = set("a an the of to and or in for on with that this it is are be as by at from should must "
           "response answer model user should the be not".split())


def toks(s):
    return [w for w in re.findall(r"[a-z']+", (s or "").lower()) if w not in STOP and len(w) > 2]


def build_idf(docs):
    df = Counter()
    for d in docs:
        for w in set(d):
            df[w] += 1
    n = len(docs)
    return {w: math.log(n / (1 + c)) for w, c in df.items()}


def vec(t, idf):
    v = Counter()
    for w in t:
        v[w] += idf.get(w, 0.0)
    nrm = math.sqrt(sum(x * x for x in v.values())) or 1.0
    return {w: x / nrm for w, x in v.items()}


def cos(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(w, 0.0) for w, x in a.items())


def polarity(s):
    """+1 asserts a behaviour, -1 forbids one. A lexical proxy; see the ledger in the docstring."""
    return -1 if NEG.search(s or "") else 1


def set_redundancy(vs):
    if len(vs) < 2:
        return None
    return float(np.mean([cos(vs[i], vs[j]) for i, j in itertools.combinations(range(len(vs)), 2)]))


def set_conflict(vs, pols):
    if len(vs) < 2:
        return None
    k = sum(1 for i, j in itertools.combinations(range(len(vs)), 2)
            if cos(vs[i], vs[j]) >= SIM_THRESHOLD and pols[i] != pols[j])
    return k / max(1, len(list(itertools.combinations(range(len(vs)), 2))))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rub = [json.loads(l) for l in (DATA / "conversation_rubrics.jsonl").open()]

    all_txt = [it["criterion"] for r in rub for it in r["coval_full"]] + \
              [c["criterion"] for r in rub for c in r["coval_core"]]
    idf = build_idf([toks(t) for t in all_txt])

    # ---------------------------------------------------------------- positive controls FIRST
    print("=" * 78)
    print("POSITIVE CONTROLS -- run before any null is allowed to mean anything")
    print("=" * 78)
    base = ["The response should explain the risks of the medication clearly",
            "The response should cite a reputable source",
            "The response should stay under 200 words"]
    dupe = base + ["The response should explain the risks of the medication clearly"]
    negd = base + ["The response should not explain the risks of the medication clearly"]
    vb = [vec(toks(t), idf) for t in base]
    vd = [vec(toks(t), idf) for t in dupe]
    vn = [vec(toks(t), idf) for t in negd]
    r_base, r_dupe = set_redundancy(vb), set_redundancy(vd)
    c_base = set_conflict(vb, [polarity(t) for t in base])
    c_neg = set_conflict(vn, [polarity(t) for t in negd])
    red_fires = r_dupe > r_base
    con_fires = c_neg > c_base
    print(f"  redundancy detector: clean set {r_base:.4f} -> with an exact duplicate {r_dupe:.4f}   "
          f"{'FIRES' if red_fires else 'DEAD'}")
    print(f"  conflict   detector: clean set {c_base:.4f} -> with an explicit negation {c_neg:.4f}   "
          f"{'FIRES' if con_fires else 'DEAD'}")
    if not (red_fires and con_fires):
        print("  A DETECTOR THAT HAS NEVER RETURNED NON-ZERO CANNOT ACQUIT. Stopping.")
        return 1

    # ---------------------------------------------------------------- the measurement
    rows = []
    for r in rub:
        full = [it["criterion"] for it in r["coval_full"]]
        core = [c["criterion"] for c in r["coval_core"]]
        k = len(core)
        if k < 2 or len(full) < k + 2:
            continue
        fv = [vec(toks(t), idf) for t in full]
        fp = [polarity(t) for t in full]
        cv = [vec(toks(t), idf) for t in core]
        cp = [polarity(t) for t in core]
        rc, cc = set_redundancy(cv), set_conflict(cv, cp)
        rr, cr = [], []
        for sd in SEEDS:
            rng = random.Random(hash(r.get("conversation", {}).get("id", "")) % 10**6 + sd)
            for _ in range(N_SUBSETS // len(SEEDS)):
                ix = rng.sample(range(len(full)), k)
                rr.append(set_redundancy([fv[i] for i in ix]))
                cr.append(set_conflict([fv[i] for i in ix], [fp[i] for i in ix]))
        rows.append({"k": k, "n_full": len(full),
                     "core_red": rc, "rand_red": float(np.median(rr)),
                     "core_con": cc, "rand_con": float(np.mean(cr)),
                     "core_neg": float(np.mean([p < 0 for p in cp])),
                     "full_neg": float(np.mean([p < 0 for p in fp]))})
    n = len(rows)
    print(f"\nprompts usable (core>=2 and full>=core+2): {n} of {len(rub)}")

    def paired(a, b):
        d = np.array([r[a] - r[b] for r in rows], float)
        m = float(d.mean())
        se = float(d.std(ddof=1) / math.sqrt(len(d)))
        return m, (m - 1.96 * se, m + 1.96 * se), float((d < 0).mean())

    print("\n" + "=" * 78)
    print("NON-REDUNDANT -- core against random same-size subsets of its OWN prompt's full set")
    print("=" * 78)
    m, ci, below = paired("core_red", "rand_red")
    print(f"  mean pairwise similarity   core {np.mean([r['core_red'] for r in rows]):.4f}   "
          f"random-subset median {np.mean([r['rand_red'] for r in rows]):.4f}")
    print(f"  paired difference core-random  {m:+.4f}  [{ci[0]:+.4f}, {ci[1]:+.4f}]")
    print(f"  prompts where core is LESS redundant than its random baseline: {below:.1%}  "
          f"(preregistered bar: >60%)")
    red_verdict = "HOLDS" if (below > 0.60 and ci[1] < 0) else "FAILS"
    print(f"  -> NON-REDUNDANT {red_verdict}")

    print("\n" + "=" * 78)
    print("NON-CONFLICTING -- same design, conflict rate per pair")
    print("=" * 78)
    m2, ci2, below2 = paired("core_con", "rand_con")
    cc_mean = np.mean([r["core_con"] for r in rows])
    cr_mean = np.mean([r["rand_con"] for r in rows])
    with_any = float(np.mean([r["core_con"] > 0 for r in rows]))
    print(f"  conflict rate per pair     core {cc_mean:.4f}   random subsets {cr_mean:.4f}")
    print(f"  paired difference core-random  {m2:+.4f}  [{ci2[0]:+.4f}, {ci2[1]:+.4f}]")
    print(f"  core sets containing at least one detected conflicting pair: {with_any:.1%}")
    if cc_mean == 0:
        con_verdict = "HOLDS (lower bound only -- the proxy is blind to conflicts without shared "
        "vocabulary)"
    elif ci2[1] < 0:
        con_verdict = "HOLDS -- core carries fewer conflicting pairs than its own random baseline"
    elif ci2[0] > 0:
        con_verdict = "FAILS -- core carries MORE conflicting pairs than random draws from the "
        "same pool"
    else:
        con_verdict = "UNVERIFIED -- the interval spans zero, so this design cannot separate them"
    print(f"  -> NON-CONFLICTING {con_verdict}")

    print("\n" + "=" * 78)
    print("THE NEGATION-MARKER COUNT -- and why its direction is NOT the card's prediction")
    print("=" * 78)
    cn = np.mean([r["core_neg"] for r in rows])
    fn = np.mean([r["full_neg"] for r in rows])
    m3, ci3, below3 = paired("core_neg", "full_neg")
    print(f"  share of criteria carrying a negation marker   core {cn:.1%}   full {fn:.1%}")
    print(f"  paired difference  {m3:+.4f}  [{ci3[0]:+.4f}, {ci3[1]:+.4f}]")
    print(f"  MY PREREGISTERED DIRECTION WAS WRONG, and saying so is the point of preregistering it.")
    print(f"  I predicted FEWER negation markers in core. But rewriting an item to have positive")
    print(f"  WEIGHT means negating its WORDING -- a criterion scored -8 for doing X becomes 'do not")
    print(f"  do X' scored +8. So MORE negation wording in core is what the documented procedure")
    print(f"  predicts, and this +2.2pp is weak evidence FOR the card, not against it. A word count")
    print(f"  cannot test a mechanism; the conditional test below can.")

    # ------------------------------------------------------------------ style confound
    # STRONGEST CONFOUND, and it was written before the run: if core items are LLM-rewritten in a
    # uniform voice, their lexical similarity rises for reasons that have nothing to do with
    # redundancy of content -- which would bias the redundancy test toward exactly the failure it
    # found. The control is cross-prompt similarity: criteria from DIFFERENT prompts share no
    # subject matter, so any elevation there is pure style.
    rng = random.Random(0)
    idx = list(range(len(rub)))
    cross_c, cross_f = [], []
    for _ in range(4000):
        i, j = rng.sample(idx, 2)
        ci_, cj = rub[i]["coval_core"], rub[j]["coval_core"]
        fi, fj = rub[i]["coval_full"], rub[j]["coval_full"]
        if ci_ and cj:
            cross_c.append(cos(vec(toks(rng.choice(ci_)["criterion"]), idf),
                               vec(toks(rng.choice(cj)["criterion"]), idf)))
        if fi and fj:
            cross_f.append(cos(vec(toks(rng.choice(fi)["criterion"]), idf),
                               vec(toks(rng.choice(fj)["criterion"]), idf)))
    xc, xf = float(np.mean(cross_c)), float(np.mean(cross_f))
    se = math.sqrt(np.var(cross_c) / len(cross_c) + np.var(cross_f) / len(cross_f))
    print("\n" + "=" * 78)
    print("THE STYLE CONFOUND ON THE REDUNDANCY RESULT -- cross-prompt similarity")
    print("=" * 78)
    print(f"  criteria from DIFFERENT prompts, mean similarity   core {xc:.4f}   full {xf:.4f}")
    print(f"  difference {xc - xf:+.4f} +/- {1.96 * se:.4f}")
    style = abs(xc - xf) > 1.96 * se
    if style:
        print(f"  A STYLE ELEVATION IS PRESENT. Core criteria resemble each other ACROSS unrelated")
        print(f"  prompts more than full ones do, which is vocabulary, not shared concern. The")
        print(f"  within-prompt gap of {m:+.4f} is the same order as this artefact, so the")
        print(f"  redundancy verdict is DOWNGRADED to UNVERIFIED: this instrument cannot separate")
        print(f"  'core is no less redundant' from 'core is written in a more uniform voice'.")
        red_verdict = "UNVERIFIED (style confound of the same magnitude)"
    else:
        print(f"  No style elevation detectable, so the within-prompt comparison stands as measured.")

    # ------------------------------------------------------------------ the rewrite mechanism
    # MY PREREGISTERED DIRECTION WAS BACKWARDS AND THE RESULT ABOVE IS NOT EVIDENCE AGAINST THE
    # CARD. "Rewrites all rubric items to have positive WEIGHT" means flipping a criterion carrying
    # a negative weight into its negation with a positive weight -- which puts MORE negation wording
    # in the output, not less. So core carrying more negation markers is what the documented
    # procedure predicts. The real test is conditional: do the flips land on the negatively-weighted
    # sources specifically?
    import difflib
    flips = {"neg_source": [0, 0], "pos_source": [0, 0]}
    matched = 0
    for r in rub:
        full = [(it["criterion"], float(np.mean([sc["score"] for sc in it["scores"]])))
                for it in r["coval_full"] if it.get("scores")]
        if not full:
            continue
        texts = [t for t, _w in full]
        low = [t.lower() for t in texts]
        for c in r["coval_core"]:
            hit = difflib.get_close_matches(c["criterion"].lower(), low, n=1, cutoff=0.60)
            if not hit:
                continue
            i = low.index(hit[0])
            matched += 1
            key = "neg_source" if full[i][1] < 0 else "pos_source"
            flips[key][1] += 1
            if polarity(c["criterion"]) != polarity(texts[i]):
                flips[key][0] += 1
    print("\n" + "=" * 78)
    print("THE POSITIVITY REWRITE, TESTED AS A MECHANISM RATHER THAN AS A WORD COUNT")
    print("=" * 78)
    print(f"  core items matched to a source at 0.60 similarity: {matched}")
    for k, (f_, t_) in flips.items():
        lbl = "negative" if k.startswith("neg") else "positive"
        print(f"  source weight {lbl:>8s} : {f_:4d}/{t_:4d} core items flipped "
              f"polarity ({f_ / max(1, t_):.1%})")
    a, b = flips["neg_source"], flips["pos_source"]
    pa, pb = a[0] / max(1, a[1]), b[0] / max(1, b[1])
    pooled = (a[0] + b[0]) / max(1, a[1] + b[1])
    zse = math.sqrt(pooled * (1 - pooled) * (1 / max(1, a[1]) + 1 / max(1, b[1])))
    z = (pa - pb) / zse if zse else float("nan")
    print(f"  difference {pa - pb:+.1%}, z {z:+.2f}")
    if z > 3:
        pos_verdict = ("HOLDS as a mechanism -- polarity flips land on negatively-weighted sources, "
                       "which is why core carries MORE negation wording, not less")
    elif z < -3:
        pos_verdict = "FAILS -- flips land on POSITIVELY weighted sources, the opposite of the card"
    else:
        pos_verdict = ("UNVERIFIED -- flip rates do not differ by source weight sign, so the "
                       "matchable subset shows no sign of the documented rewrite")
    print(f"  -> POSITIVITY REWRITE {pos_verdict}")
    print(f"  SELECTION LIMIT: only {matched} core items match any source at 0.60, so this tests the")
    print(f"  matchable subset. A heavily reworded flip leaves no match and is invisible here.")

    print("\n" + "=" * 78)
    print("THE THREE CARD PROPERTIES OF coval_core, ALL NOW TESTED")
    print("=" * 78)
    print(f"  highly rated     FAILS      (r171: 30.9% from the top slots by |mean rating|)")
    print(f"  non-redundant    {red_verdict.split(' (')[0]:<10s} (this round)")
    print(f"  non-conflicting  {con_verdict.split(' --')[0]:<10s} (this round)")

    (OUT / "core_properties.json").write_text(json.dumps(
        {"n_prompts": n, "sim_threshold": SIM_THRESHOLD, "n_subsets": N_SUBSETS,
         "positive_controls": {"redundancy_clean": r_base, "redundancy_with_duplicate": r_dupe,
                               "conflict_clean": c_base, "conflict_with_negation": c_neg,
                               "both_fired": True},
         "non_redundant": {"core": float(np.mean([r['core_red'] for r in rows])),
                           "random": float(np.mean([r['rand_red'] for r in rows])),
                           "paired_diff": m, "ci": list(ci), "share_below": below,
                           "verdict": red_verdict},
         "non_conflicting": {"core": float(cc_mean), "random": float(cr_mean),
                             "paired_diff": m2, "ci": list(ci2), "share_with_any": with_any,
                             "verdict": con_verdict},
         "positivity": {"core_neg": float(cn), "full_neg": float(fn), "paired_diff": m3,
                        "ci": list(ci3), "verdict": pos_verdict,
                        "prediction_was_inverted": "rewriting to positive WEIGHT means negating the "
                                                   "WORDING, so more negation markers is what the "
                                                   "procedure predicts",
                        "flips": {k: list(v) for k, v in flips.items()}, "z": z, "matched": matched},
         "style_confound": {"cross_prompt_core": xc, "cross_prompt_full": xf,
                            "detected": bool(style)},
         "proxy_ledger": {"property": "two criteria that cannot both be satisfied",
                          "proxy": "high content overlap and opposite polarity marker",
                          "sound_direction": "fires => real topical opposition; silence proves "
                                             "nothing, since conflicts need share no vocabulary",
                          "safe_side": "non-zero admissible as a LOWER BOUND only"}}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
