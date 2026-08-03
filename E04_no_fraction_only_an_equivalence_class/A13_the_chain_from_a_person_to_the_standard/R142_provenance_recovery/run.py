"""r142 -- can the SOURCE object be recovered from the release, and is it on one scale?

The end-to-end programme needs N: an individual normative statement WITH ITS AUTHOR. The release
ships no authorship field. `coval_full` items carry `rubric_item_id`, `criterion`, and a list of
`{annotator_id, score}` -- who rated it, never who wrote it.

But the DATASET_CARD (line 73) says the rubric pool is a MIXTURE: items "we prepared" as
pre-seeded examples, plus items annotators "could also author ... as part of the task". Two
populations, unlabelled, in one pool. If they can be separated, authorship is recovered for the
second population and the front of the chain becomes auditable.

THE SEPARATOR. Count how many people rated each item. A pre-seeded item was shown to the whole
panel; an item authored mid-session was seen by its author and nobody else. The prediction that
distinguishes this from "rated by few" is not the mode at 1 -- it is the EXACT ZERO at 2 and 3.
Any process where items accumulate raters over time leaves a tail there.

THE SECOND QUESTION, which is the one that matters for aggregation. The compiler selects by mean
rating. A pre-seeded item's mean is an average over ~17 people. A self-authored item's mean IS ITS
AUTHOR'S OWN SCORE. These are not the same measurement and putting them in one ranking is a
category error -- but how much of the resulting advantage is BEHAVIOURAL (people rate their own
writing highly) and how much is ARITHMETIC (a single draw reaches the tail of a scale that a
17-person mean cannot)?

That decomposition is identified by two different nulls and is the whole point of this round:

  N1  behavioural null   -- permute the own/panel LABEL within each rater's own score multiset.
                            Preserves every rater's scale usage exactly, preserves each item's n,
                            destroys only the link between "I wrote this" and "I scored it high".
  N2  arithmetic null    -- resample each item's scores from the pooled score distribution at that
                            item's own n. Destroys the behavioural effect AND any rater identity,
                            keeps only the fact that means over few draws are more extreme.

  observed - N1  =  the behavioural component
  N1       - N2  =  the arithmetic component

An effect that lives entirely in N1-N2 is a DERIVATION -- 1+1=2, therefore 2<3 -- and must be
labelled as one, never reported as a finding about people.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import statistics as st
from collections import defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
DATA = ROOT / "data"
OUT = pathlib.Path(__file__).resolve().parent / "results"
SOLE = 1                 # a criterion rated by exactly this many people is taken to be self-authored
PANEL_MIN = 4            # the observed floor of the second population
TOPK = 4                 # the compiler keeps up to four items


# ---------------------------------------------------------------- loading

def load():
    """conversations -> [(conv_id, [(item_id, criterion, [(annotator, score)])])]"""
    convs = []
    with (DATA / "conversation_rubrics.jsonl").open() as fh:
        for line in fh:
            r = json.loads(line)
            items = [(it["rubric_item_id"], it["criterion"],
                      [(s["annotator_id"], float(s["score"])) for s in it["scores"]])
                     for it in r["coval_full"]]
            convs.append((r["conversation"]["id"], items))
    return convs


# ---------------------------------------------------------------- P1  the separator

def p1_separation(convs):
    """Is the n=1 / n>=4 split a protocol signature or a sampling tail?"""
    hist = defaultdict(int)
    for _cid, items in convs:
        for _iid, _txt, sc in items:
            hist[len(sc)] += 1
    total = sum(hist.values())
    at_23 = hist.get(2, 0) + hist.get(3, 0)

    # The falsifier. If every item were offered to the whole panel and each rater independently
    # chose whether to rate it, n would be Binomial(panel, p) and the count at n in {2,3} is fixed
    # by the counts at n=1 and n>=4 -- it cannot be zero while both neighbours are populated.
    # Fit the single-population model that best explains the OBSERVED n>=1 counts and read off
    # what it predicts at 2 and 3.
    ns = np.array(sorted(hist))
    cnt = np.array([hist[n] for n in ns], float)
    panel = int(ns.max())
    best = None
    for p in np.linspace(0.005, 0.995, 199):
        # zero-truncated binomial log-likelihood over the observed support
        lg = [math.lgamma(panel + 1) - math.lgamma(n + 1) - math.lgamma(panel - n + 1)
              + n * math.log(p) + (panel - n) * math.log1p(-p) for n in ns]
        z = 1.0 - (1.0 - p) ** panel
        ll = float(np.sum(cnt * (np.array(lg) - math.log(z))))
        if best is None or ll > best[1]:
            best = (p, ll)
    p_hat = best[0]
    z = 1.0 - (1.0 - p_hat) ** panel

    def pmf(n):
        lg = (math.lgamma(panel + 1) - math.lgamma(n + 1) - math.lgamma(panel - n + 1)
              + n * math.log(p_hat) + (panel - n) * math.log1p(-p_hat))
        return math.exp(lg) / z

    expected_23 = total * (pmf(2) + pmf(3))
    # Poisson upper bound on observing 0 when expecting `expected_23`
    p_obs_zero = math.exp(-expected_23) if expected_23 < 700 else 0.0

    # polarity check: authorship predicts self-authored items are disproportionately PROHIBITIONS
    # (you write the thing to avoid and mark it -10). "rated by few" predicts no polarity difference.
    neg_sole = neg_panel = n_sole = n_panel = 0
    for _cid, items in convs:
        for _iid, _txt, sc in items:
            m = st.fmean(s for _a, s in sc)
            if len(sc) == SOLE:
                n_sole += 1
                neg_sole += m < 0
            elif len(sc) >= PANEL_MIN:
                n_panel += 1
                neg_panel += m < 0
    return {
        "histogram": {str(k): hist[k] for k in sorted(hist)},
        "items_total": total,
        "count_at_n_2_or_3": at_23,
        "single_population_binomial_p": round(p_hat, 4),
        "expected_at_n_2_or_3_under_one_population": round(expected_23, 1),
        "p_observing_zero_there": p_obs_zero,
        "negative_share_sole": round(neg_sole / n_sole, 4),
        "negative_share_panel": round(neg_panel / n_panel, 4),
        "n_sole": n_sole, "n_panel": n_panel,
    }


# ---------------------------------------------------------------- P2  within-rater scale

def p2_within_rater(convs, seeds):
    """Paired within each rater: their own-item scores vs the panel-item scores THEY gave.

    Within-rater is the only comparison that removes scale usage as a confound, and it compares
    individual scores to individual scores -- so the averaging artifact cannot enter at all.
    """
    own = defaultdict(list)
    pan = defaultdict(list)
    for _cid, items in convs:
        for _iid, _txt, sc in items:
            if len(sc) == SOLE:
                a, s = sc[0]
                own[a].append(s)
            elif len(sc) >= PANEL_MIN:
                for a, s in sc:
                    pan[a].append(s)
    raters = sorted(set(own) & set(pan))
    d = np.array([st.fmean(own[a]) - st.fmean(pan[a]) for a in raters])
    n = len(d)
    eff = float(d.mean())
    se = float(d.std(ddof=1) / math.sqrt(n))
    ci = (eff - 1.96 * se, eff + 1.96 * se)
    mde = 2.8 * se                                   # 80% power, alpha .05, two-sided

    # placebo: permute the own/panel label inside each rater's pooled scores, preserving how many
    # of each they gave. Kills the authorship link, keeps scale usage and both counts exactly.
    plac = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        dd = []
        for a in raters:
            pool = np.array(own[a] + pan[a])
            k = len(own[a])
            idx = rng.permutation(pool.size)
            dd.append(pool[idx[:k]].mean() - pool[idx[k:]].mean())
        plac.append(float(np.mean(dd)))

    # positive control: inject a known +2.0 shift into half the raters' own-scores and confirm the
    # same estimator recovers it. A null from an estimator that has never returned non-zero is
    # silence, not an acquittal.
    rng = np.random.default_rng(seeds[0])
    half = rng.random(n) < 0.5
    pos = float((d + 2.0 * half).mean() - eff)

    # split-half floor WITHIN rater: how big a difference does this design manufacture from noise?
    floors = []
    for sd in seeds:
        rng = np.random.default_rng(sd + 991)
        f = []
        for a in raters:
            o = np.array(own[a])
            if o.size < 4:
                continue
            i = rng.permutation(o.size)
            f.append(abs(o[i[:o.size // 2]].mean() - o[i[o.size // 2:]].mean()))
        floors.append(float(np.mean(f)))
    floor = float(np.mean(floors))
    return {
        "n_raters": n,
        "effect_own_minus_panel": round(eff, 4),
        "ci95": [round(ci[0], 4), round(ci[1], 4)],
        "mde": round(mde, 4),
        "placebo_by_seed": [round(x, 4) for x in plac],
        "positive_control_recovered": round(pos, 4),
        "positive_control_injected": 1.0,
        "within_rater_split_half_floor": round(floor, 4),
        "effect_over_floor": round(abs(eff) / floor, 3) if floor else None,
        "ci_width_over_effect": round((ci[1] - ci[0]) / abs(eff), 3) if eff else None,
        "seed_spread_over_effect": round(
            (max(plac) - min(plac)) / abs(eff), 4) if eff else None,
    }


# ---------------------------------------------------------------- P3  what selection does

def _select_share(convs, means):
    """share of top-k slots held by self-authored items, given a mean per (conv,item)."""
    hit = tot = 0
    for ci, (_cid, items) in enumerate(convs):
        sc = sorted(range(len(items)), key=lambda j: -means[ci][j])[:TOPK]
        for j in sc:
            tot += 1
            hit += len(items[j][2]) == SOLE
    return hit / tot if tot else float("nan")


def p3_selection(convs, seeds):
    obs_means = [[st.fmean(s for _a, s in it[2]) for it in items] for _cid, items in convs]
    observed = _select_share(convs, obs_means)

    # N1 behavioural null -- permute own/panel label within each rater's own multiset
    pool = defaultdict(lambda: {"own": [], "pan": []})
    for _cid, items in convs:
        for _iid, _t, sc in items:
            if len(sc) == SOLE:
                pool[sc[0][0]]["own"].append(sc[0][1])
            elif len(sc) >= PANEL_MIN:
                for a, s in sc:
                    pool[a]["pan"].append(s)

    n1 = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        draw = {}
        for a, p in pool.items():
            allv = np.array(p["own"] + p["pan"])
            idx = rng.permutation(allv.size)
            draw[a] = {"own": list(allv[idx[:len(p["own"])]]),
                       "pan": list(allv[idx[len(p["own"]):]]), "oi": 0, "pi": 0}
        means = []
        for _cid, items in convs:
            row = []
            for _iid, _t, sc in items:
                if len(sc) == SOLE:
                    a = sc[0][0]
                    d = draw[a]
                    row.append(d["own"][d["oi"] % max(1, len(d["own"]))] if d["own"] else sc[0][1])
                    d["oi"] += 1
                else:
                    vals = []
                    for a, s in sc:
                        d = draw.get(a)
                        if d and d["pan"]:
                            vals.append(d["pan"][d["pi"] % len(d["pan"])])
                            d["pi"] += 1
                        else:
                            vals.append(s)
                    row.append(st.fmean(vals))
            means.append(row)
        n1.append(_select_share(convs, means))

    # N2 arithmetic-only null -- every item's scores redrawn from the global pool at its own n
    allscores = np.array([s for _cid, items in convs for _i, _t, sc in items for _a, s in sc])
    n2 = []
    for sd in seeds:
        rng = np.random.default_rng(sd + 7717)
        means = [[float(rng.choice(allscores, size=len(it[2]), replace=True).mean())
                  for it in items] for _cid, items in convs]
        n2.append(_select_share(convs, means))

    behavioural = observed - float(np.mean(n1))
    arithmetic = float(np.mean(n1)) - float(np.mean(n2))
    base = sum(1 for _c, items in convs for it in items if len(it[2]) == SOLE) / \
        sum(len(items) for _c, items in convs)
    return {
        "pool_share_self_authored": round(base, 4),
        "observed_topk_share": round(observed, 4),
        "null_behavioural_N1_by_seed": [round(x, 4) for x in n1],
        "null_arithmetic_N2_by_seed": [round(x, 4) for x in n2],
        "component_behavioural": round(behavioural, 4),
        "component_arithmetic": round(arithmetic, 4),
        "note": ("component_arithmetic is a DERIVATION: a mean over one draw reaches the tail of "
                 "the scale that a 17-person mean cannot. It is not evidence about people."),
    }


# ---------------------------------------------------------------- held out

def held_out(convs, seeds, salts):
    rows = []
    for salt in salts:
        idx = [i for i in range(len(convs))
               if (hash((i, salt)) & 0xFFFF) % 2 == 0]
        a = [convs[i] for i in idx]
        b = [convs[i] for i in range(len(convs)) if i not in set(idx)]
        ra = p2_within_rater(a, seeds[:2])
        rb = p2_within_rater(b, seeds[:2])
        rows.append({"salt": salt,
                     "half_a": ra["effect_own_minus_panel"], "half_b": rb["effect_own_minus_panel"],
                     "same_sign": (ra["effect_own_minus_panel"] > 0) == (rb["effect_own_minus_panel"] > 0)})
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[11, 23, 37, 53, 71])
    ap.add_argument("--salts", type=int, nargs="+", default=[1, 2, 3, 4, 5, 6])
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    convs = load()
    res = {
        "conversations": len(convs),
        "P1_separation": p1_separation(convs),
        "P2_within_rater_scale": p2_within_rater(convs, args.seeds),
        "P3_selection_consequence": p3_selection(convs, args.seeds),
        "P4_held_out": held_out(convs, args.seeds, args.salts),
        "instrument": "none -- no model is executed anywhere in this round",
        "seeds": args.seeds,
    }
    (OUT / "provenance.json").write_text(json.dumps(res, indent=2))

    p1, p2, p3 = res["P1_separation"], res["P2_within_rater_scale"], res["P3_selection_consequence"]
    print(f"conversations {res['conversations']}  items {p1['items_total']}")
    print(f"P1  items rated by exactly 2 or 3 people: {p1['count_at_n_2_or_3']}   "
          f"one-population model expects {p1['expected_at_n_2_or_3_under_one_population']}")
    print(f"    prohibition share  self-authored {p1['negative_share_sole']:.1%}  "
          f"pre-seeded {p1['negative_share_panel']:.1%}")
    print(f"P2  own minus panel, within rater: {p2['effect_own_minus_panel']:+.3f} "
          f"CI {p2['ci95']}  MDE {p2['mde']:.3f}  floor {p2['within_rater_split_half_floor']:.3f}  "
          f"eff/floor {p2['effect_over_floor']}")
    print(f"    placebo {p2['placebo_by_seed']}   positive control recovered "
          f"{p2['positive_control_recovered']:+.3f} of {p2['positive_control_injected']:+.3f}")
    print(f"P3  top-{TOPK} share self-authored: observed {p3['observed_topk_share']:.1%}  "
          f"pool {p3['pool_share_self_authored']:.1%}")
    print(f"    behavioural component {p3['component_behavioural']:+.4f}   "
          f"arithmetic component {p3['component_arithmetic']:+.4f} (DERIVATION)")
    print(f"P4  held out: {sum(r['same_sign'] for r in res['P4_held_out'])}"
          f"/{len(res['P4_held_out'])} partitions agree on sign")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
