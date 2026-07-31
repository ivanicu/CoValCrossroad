"""Is the unserved third a CONSTITUENCY, or does everyone take a turn?

r144 left a third of each panel unserved by the best available response -- 5.26 of 15.6 people
against 9.16 under a null that preserves everyone's decisiveness. That number is compatible with two
completely different worlds and they demand opposite responses:

  ROTATING    the same 33% rate, different people each time. Nobody is systematically excluded; the
              aggregate is simply coarse. This is a resolution limit, not a fairness failure, and
              there is no one to compensate.
  CONSTITUENCY the same people, prompt after prompt. Then the aggregate has a class it never serves,
              the loss has a bearer, and "who does this rubric serve" has an answer.

Only the second is a distributive failure, and the difference is measurable.

DEFINITION, deliberately the most generous one available. The "best single response" is the one that
is top-ranked by the greatest number of people on that prompt -- the utilitarian optimum over the
released candidates. Anyone unserved by THAT is unserved by any single choice whatsoever, so the
measurement cannot be accused of picking a weak aggregate to make the residual look bad.

THE FLOOR IS THE WHOLE TEST AND IT IS WHY THIS ROUND EXISTS RATHER THAN A HEADLINE. A between-person
spread in unserved rates is produced by chance alone: with about nine prompts each, binomial noise
manufactures apparent variation between people. So the between-person standard deviation is compared
against a WITHIN-person split-half floor -- split each person's own prompts in two, measure how far
their two halves differ from each other. Anything below 1.5x that floor licenses a direction and
never a count. This exact discipline retracted a person-level harm count in this project after four
rounds of work, and it is applied before the number is reported rather than after.
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
MIN_PROMPTS = 6          # a person needs enough prompts for a within-person split to mean anything


def parse_ranking(txt: str) -> np.ndarray | None:
    v = np.full(4, np.nan)
    groups = [g.strip() for g in txt.replace(" ", "").split(">") if g.strip()]
    if not groups:
        return None
    for gi, g in enumerate(groups):
        for letter in g.split("="):
            if letter in RANK_MAP:
                v[RANK_MAP[letter]] = -gi
    return v if not np.isnan(v).all() else None


def load() -> tuple[dict[str, dict[str, np.ndarray]], dict[str, dict]]:
    """(prompt -> annotator -> ranking vector, annotator -> demographics)"""
    rank: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    demo: dict[str, dict] = {}
    with (ROOT / "data" / "annotators.jsonl").open() as fh:
        for line in fh:
            rec = json.loads(line)
            aid = rec["annotator_id"]
            demo[aid] = rec.get("demographics", {}) or {}
            for a in rec.get("assessments", []):
                blocks = a.get("ranking_blocks") or {}
                for key in ("world", "personal"):
                    got = False
                    for b in blocks.get(key, []) or []:
                        v = parse_ranking(b.get("ranking") or "")
                        if v is not None:
                            rank[a["conversation_id"]][aid] = v
                            got = True
                            break
                    if got:
                        break
    return rank, demo


def unserved_table(rank, with_topk: bool = False):
    """(prompt, annotator, unserved) under the utilitarian best single response.

    `with_topk` also returns each person's top-set SIZE, which is the last confound standing: a
    person who marks three responses as equally best is served whenever any of the three wins, so
    an indecisive person is mechanically served more often than a decisive one. If a demographic
    group is simply more decisive, its higher unserved rate is a fact about how it uses the scale
    and not about whether the aggregate serves it.
    """
    rows, topk = [], []
    for pid, per in rank.items():
        if len(per) < 4:
            continue
        tops = {a: set(np.nonzero(v >= np.nanmax(v) - 1e-9)[0].tolist()) for a, v in per.items()}
        counts = [sum(1 for t in tops.values() if r in t) for r in range(4)]
        best = int(np.argmax(counts))
        for a, t in tops.items():
            rows.append((pid, a, 0 if best in t else 1))
            topk.append(len(t))
    return (rows, topk) if with_topk else rows


def decisiveness_matched_scan(rank, demo, min_prompts: int = 20) -> list[dict]:
    """The within-prompt scan again, but comparing only people with the SAME top-set size.

    Stratifying on top-set size inside each prompt removes decisiveness exactly rather than
    adjusting for it, at the cost of discarding every prompt-stratum with only one group present.
    """
    strata: dict[tuple[str, str], list[float]] = defaultdict(list)
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for pid, per in rank.items():
        if len(per) < 4:
            continue
        tops = {a: set(np.nonzero(v >= np.nanmax(v) - 1e-9)[0].tolist()) for a, v in per.items()}
        cnt = [sum(1 for t in tops.values() if r in t) for r in range(4)]
        best = int(np.argmax(cnt))
        for size in (1, 2, 3):
            members = [(a, 0 if best in t else 1) for a, t in tops.items() if len(t) == size]
            if len(members) < 4:
                continue
            for k in {kk for a, _u in members for kk in (demo.get(a) or {})}:
                vals = [(demo.get(a, {}).get(k), u) for a, u in members]
                vals = [(v, u) for v, u in vals if isinstance(v, str) and v and len(v) < 60]
                for g in {v for v, _u in vals}:
                    ins = [u for v, u in vals if v == g]
                    out = [u for v, u in vals if v != g]
                    if not ins or not out:
                        continue
                    strata[(k, g)].append(float(np.mean(ins)) - float(np.mean(out)))
                    counts[(k, g)] += len(ins)
    res = []
    for (k, g), d in strata.items():
        if len(d) < min_prompts:
            continue
        arr = np.array(d)
        m = float(arr.mean())
        se = float(arr.std(ddof=1) / math.sqrt(len(arr)))
        res.append({"axis": k, "group": g, "n_strata": len(d), "n_rows": counts[(k, g)],
                    "delta_matched": round(m, 4),
                    "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)],
                    "z": round(m / se, 3) if se else 0.0})
    return {(r["axis"], r["group"]): r for r in res}


def person_rates(rows) -> dict[str, list[int]]:
    by: dict[str, list[int]] = defaultdict(list)
    for _pid, a, u in rows:
        by[a].append(u)
    return {a: v for a, v in by.items() if len(v) >= MIN_PROMPTS}


def between_sd(by: dict[str, list[int]]) -> float:
    return float(np.std([np.mean(v) for v in by.values()], ddof=1))


def split_half_floor(by: dict[str, list[int]], seeds: list[int]) -> float:
    """Within-person: split each person's own prompts and measure how far the halves differ.

    This is what chance alone produces between people at this many prompts each. A between-person
    spread below it is not evidence that people differ.
    """
    out = []
    for sd in seeds:
        rng = np.random.default_rng(sd)
        d = []
        for v in by.values():
            x = np.array(v, float)
            i = rng.permutation(len(x))
            h = len(x) // 2
            d.append(abs(x[i[:h]].mean() - x[i[h:]].mean()))
        # the between-person sd implied by within-person noise alone
        out.append(float(np.mean(d)) * math.sqrt(math.pi / 4))
    return float(np.mean(out))


def label_null(rows, seeds: list[int]) -> tuple[float, list[float]]:
    """Permute unserved WITHIN each prompt: preserves every prompt's exact unserved count and panel
    size, destroys only which person carries it. If the between-person spread does not exceed this,
    the apparent constituency is bookkeeping."""
    by_p: dict[str, list[int]] = defaultdict(list)
    who: dict[str, list[str]] = defaultdict(list)
    for pid, a, u in rows:
        by_p[pid].append(u)
        who[pid].append(a)
    vals = []
    for sd in seeds:
        rng = np.random.default_rng(sd + 313)
        shuffled = []
        for pid, us in by_p.items():
            perm = rng.permutation(len(us))
            for a, j in zip(who[pid], perm):
                shuffled.append((pid, a, us[j]))
        vals.append(between_sd(person_rates(shuffled)))
    return float(np.mean(vals)), vals


def demographic_scan(by: dict[str, list[int]], demo: dict[str, dict], seeds) -> list[dict]:
    """Per group: mean unserved rate vs everyone else, with the SAME floor applied and BH over the
    whole family of tests -- not over the ones that looked interesting."""
    groups: dict[tuple[str, str], list[str]] = defaultdict(list)
    for a in by:
        for k, v in (demo.get(a) or {}).items():
            if isinstance(v, str) and v and len(v) < 60:
                groups[(k, v)].append(a)
    rates = {a: float(np.mean(v)) for a, v in by.items()}
    out = []
    for (k, v), members in groups.items():
        if len(members) < 20:
            continue
        inside = np.array([rates[a] for a in members])
        outside = np.array([rates[a] for a in by if a not in set(members)])
        d = float(inside.mean() - outside.mean())
        se = math.sqrt(inside.var(ddof=1) / len(inside) + outside.var(ddof=1) / len(outside))
        z = d / se if se else 0.0
        p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
        out.append({"axis": k, "group": v, "n": len(members), "delta": round(d, 4),
                    "z": round(z, 3), "p": p})
    ps = [r["p"] for r in out]
    order = sorted(range(len(ps)), key=lambda i: ps[i])
    kmax = -1
    for rank_, i in enumerate(order, 1):
        if ps[i] <= 0.05 * rank_ / len(ps):
            kmax = rank_
    for rank_, i in enumerate(order, 1):
        out[i]["bh_significant"] = rank_ <= kmax
    return sorted(out, key=lambda r: r["p"])


def within_prompt_scan(rows, demo, min_members: int = 20) -> list[dict]:
    """The control the between-person scan cannot do without.

    A group's unserved rate can differ because the group is excluded, OR because its members were
    assigned different prompts -- some prompts have a clear best answer and some do not, and if a
    country's annotators worked the hard ones their rate rises with no exclusion anywhere. Country
    and prompt assignment are confounded in this release and the between-person test cannot tell
    them apart.

    So compare INSIDE each prompt: on this exact prompt, with this exact panel and this exact set of
    candidate responses, is a member of the group more often unserved than a non-member? Prompt
    difficulty then cancels exactly, because it is shared by both arms of every comparison.
    """
    by_prompt: dict[str, list[tuple[str, int]]] = defaultdict(list)
    for pid, a, u in rows:
        by_prompt[pid].append((a, u))
    axes: dict[tuple[str, str], list[float]] = defaultdict(list)
    sizes: dict[tuple[str, str], int] = defaultdict(int)
    for _pid, members in by_prompt.items():
        for k in {kk for a, _u in members for kk in (demo.get(a) or {})}:
            vals = [(demo.get(a, {}).get(k), u) for a, u in members]
            vals = [(v, u) for v, u in vals if isinstance(v, str) and v and len(v) < 60]
            if len(vals) < 4:
                continue
            groups = {v for v, _u in vals}
            if len(groups) < 2:
                continue
            for g in groups:
                inside = [u for v, u in vals if v == g]
                outside = [u for v, u in vals if v != g]
                if not inside or not outside:
                    continue
                axes[(k, g)].append(float(np.mean(inside)) - float(np.mean(outside)))
                sizes[(k, g)] += len(inside)
    out = []
    for (k, g), d in axes.items():
        if len(d) < min_members:
            continue
        arr = np.array(d)
        m = float(arr.mean())
        se = float(arr.std(ddof=1) / math.sqrt(len(arr)))
        z = m / se if se else 0.0
        p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
        out.append({"axis": k, "group": g, "n_prompts": len(d), "n_rows": sizes[(k, g)],
                    "delta_within_prompt": round(m, 4),
                    "ci95": [round(m - 1.96 * se, 4), round(m + 1.96 * se, 4)],
                    "z": round(z, 3), "p": p})
    ps = [r["p"] for r in out]
    if ps:
        order = sorted(range(len(ps)), key=lambda i: ps[i])
        kmax = -1
        for rank_, i in enumerate(order, 1):
            if ps[i] <= 0.05 * rank_ / len(ps):
                kmax = rank_
        for rank_, i in enumerate(order, 1):
            out[i]["bh_significant"] = rank_ <= kmax
    return sorted(out, key=lambda r: r["p"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    ap.add_argument("--salts", type=int, nargs="+", default=[1, 2, 3, 4, 5, 6])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    rank, demo = load()
    rows = unserved_table(rank)
    by = person_rates(rows)
    overall = float(np.mean([u for _p, _a, u in rows]))

    sd_obs = between_sd(by)
    floor = split_half_floor(by, args.seeds)
    null_sd, null_vals = label_null(rows, args.seeds)
    ratio_floor = sd_obs / floor if floor else float("nan")
    ratio_null = sd_obs / null_sd if null_sd else float("nan")

    # held out: does the same person's rate in one half of prompts predict the other half?
    held = []
    for salt in args.salts:
        a_half, b_half = defaultdict(list), defaultdict(list)
        for pid, a, u in rows:
            (a_half if (hash((pid, salt)) & 0xFFFF) % 2 == 0 else b_half)[a].append(u)
        common = [a for a in a_half if a in b_half
                  and len(a_half[a]) >= 3 and len(b_half[a]) >= 3]
        if len(common) < 30:
            held.append({"salt": salt, "r": None, "n": len(common)})
            continue
        x = np.array([np.mean(a_half[a]) for a in common])
        y = np.array([np.mean(b_half[a]) for a in common])
        held.append({"salt": salt, "r": round(float(np.corrcoef(x, y)[0, 1]), 4),
                     "n": len(common)})

    scan = demographic_scan(by, demo, args.seeds)
    wscan = within_prompt_scan(rows, demo)
    wmap = {(r["axis"], r["group"]): r for r in wscan}
    dmap = decisiveness_matched_scan(rank, demo)

    res = {
        "person_prompt_rows": len(rows), "people_with_enough_prompts": len(by),
        "prompts": len(rank), "overall_unserved_rate": round(overall, 4),
        "between_person_sd": round(sd_obs, 5),
        "within_person_split_half_floor": round(floor, 5),
        "sd_over_floor": round(ratio_floor, 3),
        "label_permutation_null_sd": round(null_sd, 5),
        "null_sd_by_seed": [round(v, 5) for v in null_vals],
        "sd_over_null": round(ratio_null, 3),
        "held_out_person_rate_correlation": held,
        "demographic_scan_between_person": scan[:10],
        "demographic_scan_within_prompt": wscan[:10],
        "decisiveness_matched": [dmap[(r["axis"], r["group"])] for r in wscan[:10]
                                 if (r["axis"], r["group"]) in dmap],
        "n_groups_tested": len(scan),
        "n_groups_bh_between": sum(1 for r in scan if r.get("bh_significant")),
        "n_groups_bh_within_prompt": sum(1 for r in wscan if r.get("bh_significant")),
        "instrument": "none -- no model is executed anywhere in this round",
        "verdict_individual_level": (
            "CONSTITUENCY" if ratio_floor >= 1.5 and ratio_null >= 1.5 else "ROTATING"),
        "verdict_note": ("the individual-level verdict and the group-level scan answer different "
                         "questions and may legitimately disagree: a group of 130 averages away "
                         "the within-person noise that makes an individual rate inadmissible. "
                         "Only the WITHIN-PROMPT scan is free of the prompt-assignment confound."),
    }
    (OUT / "who_is_unserved.json").write_text(json.dumps(res, indent=1))

    print(f"person-prompt rows {len(rows)}   people with >={MIN_PROMPTS} prompts {len(by)}   "
          f"prompts {len(rank)}")
    print(f"overall unserved rate            {overall:.1%}")
    print(f"between-person sd of that rate   {sd_obs:.4f}")
    print(f"  within-person split-half floor {floor:.4f}   ratio {ratio_floor:.2f}"
          f"   (needs >=1.50 for a count)")
    print(f"  label-permutation null sd      {null_sd:.4f}   ratio {ratio_null:.2f}")
    rs = [h["r"] for h in held if h["r"] is not None]
    print(f"held out: person's rate in one half vs the other, r = "
          f"{np.mean(rs):.4f} over {len(rs)} partitions" if rs else "held out: insufficient")
    print(f"\nBETWEEN-PERSON scan (CONFOUNDED with prompt assignment): {len(scan)} groups, "
          f"BH-significant {sum(1 for r in scan if r.get('bh_significant'))}")
    print(f"WITHIN-PROMPT scan  (confound removed):                  {len(wscan)} groups, "
          f"BH-significant {sum(1 for r in wscan if r.get('bh_significant'))}")
    print(f"\n{'group':30s} {'between':>9s} {'within':>9s} {'+decisiveness matched':>22s}")
    for r in scan[:7]:
        key = (r["axis"], r["group"])
        w, dd = wmap.get(key), dmap.get(key)
        wv = f"{w['delta_within_prompt']:+9.4f}" if w else "        -"
        dv = (f"{dd['delta_matched']:+.4f} [{dd['ci95'][0]:+.3f},{dd['ci95'][1]:+.3f}]"
              if dd else "-")
        print(f"   {r['group'][:28]:28s} {r['delta']:+9.4f} {wv} {dv:>22s}")
    print(f"\nVERDICT (individual level): {res['verdict_individual_level']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
