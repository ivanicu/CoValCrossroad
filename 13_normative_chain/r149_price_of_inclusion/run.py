"""Could ANY chooser have served them, and what would it have cost everyone else?

The surviving object after r148 is a LEVEL: South African participants are unserved 15.6 points more
than their co-panelists by the panel's own plurality, and compilation inherits that rather than
creating it. That level has never been attacked directly, and it has a rival that would dissolve it
entirely:

  CANDIDATE-SET FAILURE   the four responses were generated from a distribution these participants
                          sit further from, so the response they wanted was never on the menu. Then
                          no rubric of any kind could have served them, no aggregation rule is at
                          fault, and the finding is about response generation, not about alignment.
  AGGREGATION FAILURE     the response they wanted IS on the menu. They are simply outvoted. Then the
                          exclusion is a property of the aggregation and is in principle fixable.

THE SEPARATOR IS AN ORACLE, and it needs no model. For each prompt, ask what a chooser would achieve
if it were ALLOWED to pick the response that best serves this group -- the group-optimal choice
rather than the plurality one.

    group-oracle service ~ 100%   their preference exists in the candidate set; the failure is
                                  aggregation. The candidate-set rival dies.
    group-oracle service still low  their preference is not representable among these four; the
                                  rival survives and the level is about generation.

AND THEN THE QUANTITY THAT MATTERS FOR ANY REMEDY. If the oracle says they COULD have been served,
the next question is what serving them costs: switching from the plurality choice to the
group-optimal choice, how many other people lose service? That price is the actual distributive
object. A group excluded at no cost to anyone is an aggregation defect. A group whose inclusion costs
three other people their own top choice is a genuine conflict, and calling it a defect is a choice
about whose loss counts, not a measurement.

Everything here is computed from human rankings only. No model is executed anywhere in this round,
so unlike r146 and r148 nothing depends on the rebuilt judge.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
MIN_PROMPTS = 20


def parse_ranking(txt: str):
    v = np.full(4, np.nan)
    groups = [g.strip() for g in txt.replace(" ", "").split(">") if g.strip()]
    if not groups:
        return None
    for gi, g in enumerate(groups):
        for letter in g.split("="):
            if letter in RANK_MAP:
                v[RANK_MAP[letter]] = -gi
    return v if not np.isnan(v).all() else None


def parse_unacceptable(blocks) -> set:
    out = set()
    for b in blocks.get("unacceptable", []) or []:
        for r in b.get("rating", []) or []:
            for letter, idx in RANK_MAP.items():
                if r.strip().startswith(letter):
                    out.add(idx)
    return out


def load():
    rank: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    unacc: dict[str, dict[str, set]] = defaultdict(dict)
    demo: dict[str, dict] = {}
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            aid = rec["annotator_id"]
            demo[aid] = rec.get("demographics", {}) or {}
            for a in rec.get("assessments", []):
                blocks = a.get("ranking_blocks") or {}
                cid = a["conversation_id"]
                for key in ("world", "personal"):
                    got = False
                    for b in blocks.get(key, []) or []:
                        v = parse_ranking(b.get("ranking") or "")
                        if v is not None:
                            rank[cid][aid] = v
                            got = True
                            break
                    if got:
                        break
                u = parse_unacceptable(blocks)
                if u:
                    unacc[cid][aid] = u
    return rank, unacc, demo


N_ORACLE_DRAWS = 25


def analyse(rank, unacc, demo, axis_filter=None, seed: int = 7):
    rng = np.random.default_rng(seed)
    """Per group: plurality service, group-oracle service, and the price of switching."""
    acc: dict[tuple[str, str], dict] = defaultdict(
        lambda: {"plur_in": [], "orac_in": [], "orac_rand": [], "orac_rand_sd": [],
                 "price_out": [], "plur_out": [], "unacc_in": [], "unacc_out": [], "n_prompts": 0})
    for pid, per in rank.items():
        if len(per) < 6:
            continue
        tops = {a: set(np.nonzero(v >= np.nanmax(v) - 1e-9)[0].tolist()) for a, v in per.items()}
        counts = [sum(1 for t in tops.values() if r in t) for r in range(4)]
        plur = int(np.argmax(counts))
        ua = unacc.get(pid, {})
        axes = {k for a in per for k in (demo.get(a) or {})}
        for k in axes:
            if axis_filter and k != axis_filter:
                continue
            labels = {a: (demo.get(a) or {}).get(k) for a in per}
            labels = {a: v for a, v in labels.items()
                      if isinstance(v, str) and v and len(v) < 60}
            for g in set(labels.values()):
                ins = [a for a, v in labels.items() if v == g]
                outs = [a for a, v in labels.items() if v != g]
                if len(ins) < 2 or len(outs) < 2:
                    continue
                # what a chooser could achieve for this group if allowed to pick for them
                serve_in = [sum(1 for a in ins if r in tops[a]) for r in range(4)]
                orac = int(np.argmax(serve_in))
                # CONTROL. A group oracle below 1.0 may mean the candidate set fails the group, OR
                # merely that the group's own members disagree with each other -- one response
                # cannot be top for people who want different things. So the same oracle is
                # computed for a RANDOM subgroup of the SAME SIZE drawn from this prompt's panel.
                # That carries the identical internal-heterogeneity penalty and no group identity,
                # and is the only thing that makes the group's own oracle readable.
                # MULTI-SEED. The first version drew ONE random subgroup per prompt, so the whole
                # -0.078 excess rested on a single draw and its seed spread was UNCOMPUTED -- which
                # I recorded as a limitation rather than as a small number, because those are
                # different things. Averaging N independent draws per prompt turns the control
                # from one realisation into an estimate with a spread that can be reported.
                people = list(per)
                draws = []
                for _s in range(N_ORACLE_DRAWS):
                    idx = rng.permutation(len(people))[: len(ins)]
                    rand = [people[i] for i in idx]
                    sr = [sum(1 for a in rand if r in tops[a]) for r in range(4)]
                    draws.append(float(np.mean(
                        [1 if int(np.argmax(sr)) in tops[a] else 0 for a in rand])))
                d_rand = float(np.mean(draws))
                d_rand_sd = float(np.std(draws, ddof=1)) if len(draws) > 1 else float("nan")
                d = acc[(k, g)]
                d["n_prompts"] += 1
                d["plur_in"].append(np.mean([1 if plur in tops[a] else 0 for a in ins]))
                d["plur_out"].append(np.mean([1 if plur in tops[a] else 0 for a in outs]))
                d["orac_in"].append(np.mean([1 if orac in tops[a] else 0 for a in ins]))
                d["orac_rand"].append(float(d_rand))
                d["orac_rand_sd"].append(d_rand_sd)
                # price: what the OUT-group loses when the choice moves to the group optimum
                d["price_out"].append(
                    np.mean([1 if plur in tops[a] else 0 for a in outs])
                    - np.mean([1 if orac in tops[a] else 0 for a in outs]))
                if ua:
                    d["unacc_in"].append(np.mean([len(ua.get(a, set())) for a in ins]))
                    d["unacc_out"].append(np.mean([len(ua.get(a, set())) for a in outs]))
    res = {}
    for key, d in acc.items():
        if d["n_prompts"] < MIN_PROMPTS:
            continue

        def ms(v):
            arr = np.array(v, float)
            arr = arr[~np.isnan(arr)]
            if arr.size < 2:
                return None, None
            return float(arr.mean()), float(arr.std(ddof=1) / math.sqrt(arr.size))
        p_in, p_in_se = ms(d["plur_in"])
        o_in, o_in_se = ms(d["orac_in"])
        pr, pr_se = ms(d["price_out"])
        p_out, _ = ms(d["plur_out"])
        o_rnd, o_rnd_se = ms(d["orac_rand"])
        o_rnd_sd, _ = ms(d["orac_rand_sd"])
        u_in, _ = ms(d["unacc_in"])
        u_out, _ = ms(d["unacc_out"])
        res[key] = {
            "n_prompts": d["n_prompts"],
            "served_plurality": p_in, "served_plurality_se": p_in_se,
            "served_oracle": o_in, "served_oracle_se": o_in_se,
            "served_oracle_size_matched_random": o_rnd,
            "random_oracle_within_prompt_sd": o_rnd_sd,
            "random_oracle_se_across_prompts": o_rnd_se,
            "oracle_excess_over_random":
                (o_in - o_rnd) if (o_in is not None and o_rnd is not None) else None,
            "recoverable": (o_in - p_in) if (o_in is not None and p_in is not None) else None,
            "out_group_served_plurality": p_out,
            "price_to_out_group": pr, "price_se": pr_se,
            "mean_unacceptable_in": u_in, "mean_unacceptable_out": u_out,
        }
    return res


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", default="South Africa")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    rank, unacc, demo = load()
    res = analyse(rank, unacc, demo)
    print(f"groups {len(res)}   prompts {len(rank)}   "
          f"prompts with unacceptable blocks {len(unacc)}")

    rows = sorted(res.items(), key=lambda kv: kv[1]["served_plurality"])
    print(f"\n{'group':28s} {'served by':>10s} {'oracle':>8s} {'recover':>8s} "
          f"{'price to':>9s} {'unacc in':>9s} {'unacc out':>10s}")
    print(f"{'':28s} {'plurality':>10s} {'':8s} {'able':>8s} {'others':>9s}")
    for (ax, g), v in rows[:6] + rows[-3:]:
        print(f"  {g[:26]:26s} {v['served_plurality']:10.3f} {v['served_oracle']:8.3f} "
              f"{v['recoverable']:+8.3f} {v['price_to_out_group']:+9.3f} "
              f"{(v['mean_unacceptable_in'] or float('nan')):9.3f} "
              f"{(v['mean_unacceptable_out'] or float('nan')):10.3f}")

    tk = next((k for k in res if k[1] == args.target), None)
    if tk:
        t = res[tk]
        print(f"\n{args.target}  ({t['n_prompts']} prompts)")
        print(f"  served by plurality      {t['served_plurality']:.3f} "
              f"+- {1.96 * t['served_plurality_se']:.3f}")
        print(f"  served by group oracle   {t['served_oracle']:.3f} "
              f"+- {1.96 * t['served_oracle_se']:.3f}")
        print(f"  recoverable by switching {t['recoverable']:+.3f}")
        print(f"  price paid by others     {t['price_to_out_group']:+.3f} "
              f"+- {1.96 * t['price_se']:.3f}")
        exc_se = math.sqrt((t["served_oracle_se"] or 0) ** 2
                           + (t["random_oracle_se_across_prompts"] or 0) ** 2)
        print(f"  size-matched RANDOM oracle {t['served_oracle_size_matched_random']:.3f}"
              f"  ({N_ORACLE_DRAWS} draws/prompt, within-prompt sd "
              f"{t['random_oracle_within_prompt_sd']:.3f})")
        print(f"  excess {t['oracle_excess_over_random']:+.3f}  +- "
              f"{1.96 * exc_se:.3f}   -> the limitation recorded as UNCOMPUTED is now a number")
        exc = t["oracle_excess_over_random"]
        verdict = ("HETEROGENEITY ONLY -- the group's own oracle matches a random subgroup of the "
                   "same size, so nothing about this group is special"
                   if abs(exc) < 0.03 else
                   ("CANDIDATE SET -- even their own best choice fails them MORE than "
                    "heterogeneity explains" if exc < 0 else
                    "AGGREGATION -- their preferred response is on the menu and is being outvoted"))
        print(f"  VERDICT: {verdict}")

    # the exchange rate, across all groups: recoverable service vs price
    rec = np.array([v["recoverable"] for v in res.values()])
    pri = np.array([v["price_to_out_group"] for v in res.values()])
    print(f"\nacross {len(res)} groups: mean recoverable {rec.mean():+.4f}, "
          f"mean price to others {pri.mean():+.4f}, exchange rate "
          f"{pri.mean() / rec.mean() if rec.mean() else float('nan'):.2f} lost per 1 gained")

    (OUT / "price_of_inclusion.json").write_text(json.dumps({
        "n_groups": len(res), "n_prompts": len(rank),
        "target": args.target,
        "target_row": {k: (round(v, 5) if isinstance(v, float) else v)
                       for k, v in res[tk].items()} if tk else None,
        "mean_recoverable": round(float(rec.mean()), 5),
        "mean_price_to_others": round(float(pri.mean()), 5),
        "exchange_rate_lost_per_gained": round(float(pri.mean() / rec.mean()), 4)
        if rec.mean() else None,
        "groups": [{"axis": a, "group": g, **{kk: (round(vv, 5) if isinstance(vv, float) else vv)
                                              for kk, vv in v.items()}}
                   for (a, g), v in sorted(res.items(), key=lambda kv: kv[1]["served_plurality"])],
        "instrument": "none -- human rankings only, no model executed",
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
