"""The release's only dispositive channel -- is it a veto, or the bottom of the ranking renamed?

Every thread in this audit has converged on force. r143 showed force was never elicited in the
criteria: under 1% of 15,248 carry any absolute-force marker, so compilation could not have lost what
was never collected. But there IS one place in this release where an absolute judgement is recorded:
the `unacceptable` block, attached to a RESPONSE rather than to a criterion. It is the only
dispositive signal in the whole artefact.

So it deserves the two questions that decide whether it is force at all.

  IS IT DISTINCT?   If "unacceptable" is simply whatever a person ranked last, the channel carries
                    no information the ranking does not, and the release's one dispositive signal is
                    a scalar in disguise. Mean vetoes per person is 1.09 out of four -- suspiciously
                    close to the 1.00 that "mark your last place" would produce, so this rival is
                    live and has to be killed or accepted on evidence.
  DOES IT DO ANYTHING?  A veto that never changes which response wins is a preference, whatever it
                    is called. This is the same test applied to the criteria and it is the one that
                    matters: force is as force does.

THE DISCRIMINATING SIGNATURES, written before the run:

  distinct  P(unacceptable) varies at FIXED rank position -- people veto their second choice, or
            veto nothing at all, or veto three of four. Count varies across people.
  redundant P(unacceptable | ranked last) ~ 1 and ~0 elsewhere, with everyone marking exactly one.

  consequential  a veto-respecting chooser picks a different response than the plurality often
                 enough to matter, and the switch is not simply the plurality's second choice.
  decorative     the veto-respecting chooser almost always picks what the plurality already picked.

COVERAGE IS ITSELF A RESULT. Only 330 of 1100 prompts carry any unacceptable block. Whether that is
because the question was asked on a subset, or because most people declined to use it, changes what
the channel is: an optional escape hatch that most people ignore is a different object from a
question everyone answered with mostly-empty sets. Both are measured here rather than assumed.

No model is executed anywhere in this round.
"""
from __future__ import annotations

import argparse
import json
import math
import pathlib
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}


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


def parse_unacceptable(blocks):
    """Returns (set_of_indices, block_present). The distinction matters: an empty set because the
    person said nothing is unacceptable is a JUDGEMENT; a missing block is a MISSING ANSWER, and
    collapsing them would turn silence into an endorsement."""
    blk = blocks.get("unacceptable")
    if blk is None:
        return set(), False
    out = set()
    for b in blk or []:
        for r in b.get("rating", []) or []:
            s = r.strip()
            for letter, idx in RANK_MAP.items():
                if s.startswith(letter):
                    out.add(idx)
    return out, True


def load():
    rank: dict[str, dict[str, np.ndarray]] = defaultdict(dict)
    veto: dict[str, dict[str, set]] = defaultdict(dict)
    present: dict[str, set] = defaultdict(set)
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
                u, has = parse_unacceptable(blocks)
                if has:
                    present[cid].add(aid)
                    veto[cid][aid] = u
    return rank, veto, present, demo


def rank_position(v: np.ndarray) -> dict[int, int]:
    """response index -> 0-based rank, ties share the better position."""
    order = sorted(range(4), key=lambda i: -(v[i] if not np.isnan(v[i]) else -99))
    pos, out, prev = 0, {}, None
    for n, i in enumerate(order):
        val = v[i]
        if prev is None or val != prev:
            pos = n
        out[i] = pos
        prev = val
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rank, veto, present, demo = load()

    n_prompts = len(rank)
    with_block = len(present)
    answered = sum(len(v) for v in present.values())
    total_assess = sum(len(v) for v in rank.values())
    print(f"prompts {n_prompts}   prompts where anyone answered the veto question {with_block}")
    print(f"assessments {total_assess}   with a veto block {answered} "
          f"({answered / total_assess:.1%})")

    # ---- IS IT DISTINCT?
    by_rank = Counter()
    tot_rank = Counter()
    counts = Counter()
    for cid, per in rank.items():
        for aid, v in per.items():
            if aid not in veto.get(cid, {}):
                continue
            u = veto[cid][aid]
            counts[len(u)] += 1
            pos = rank_position(v)
            for r in range(4):
                tot_rank[pos[r]] += 1
                if r in u:
                    by_rank[pos[r]] += 1
    print("\nP(marked unacceptable | rank position)")
    for p in sorted(tot_rank):
        print(f"   rank {p}: {by_rank[p] / tot_rank[p]:6.1%}   (n={tot_rank[p]})")
    print("number of responses a person marks unacceptable:")
    tot_c = sum(counts.values())
    for c in sorted(counts):
        print(f"   {c}: {counts[c] / tot_c:6.1%}")

    # a rank-only predictor: does knowing the rank tell you the veto?
    pr = {p: by_rank[p] / tot_rank[p] for p in tot_rank}
    ll_rank = ll_base = 0.0
    base = sum(by_rank.values()) / sum(tot_rank.values())
    for p in tot_rank:
        k, n = by_rank[p], tot_rank[p]
        for q, acc in ((pr[p], "r"), (base, "b")):
            q = min(max(q, 1e-9), 1 - 1e-9)
            val = k * math.log(q) + (n - k) * math.log(1 - q)
            if acc == "r":
                ll_rank += val
            else:
                ll_base += val
    mcfadden = 1 - ll_rank / ll_base
    print(f"\nrank-only model pseudo-R2 (McFadden) = {mcfadden:.4f}   "
          f"-> rank explains {'nearly all' if mcfadden > 0.6 else 'only part'} of the veto")

    # ---- DOES IT DO ANYTHING?
    same = diff = testable = 0
    switch_rank = Counter()
    served_plur, served_veto = [], []
    for cid, per in rank.items():
        vv = veto.get(cid, {})
        if len(per) < 6 or len(vv) < 3:
            continue
        tops = {a: set(np.nonzero(x >= np.nanmax(x) - 1e-9)[0].tolist()) for a, x in per.items()}
        counts_top = [sum(1 for t in tops.values() if r in t) for r in range(4)]
        plur = int(np.argmax(counts_top))
        vcount = [sum(1 for u in vv.values() if r in u) for r in range(4)]
        # veto-respecting chooser: fewest vetoes, plurality breaks ties
        best = min(vcount)
        cand = [r for r in range(4) if vcount[r] == best]
        vch = max(cand, key=lambda r: counts_top[r])
        testable += 1
        if vch == plur:
            same += 1
        else:
            diff += 1
            pos = rank_position(np.array(counts_top, float))
            switch_rank[pos[vch]] += 1
        served_plur.append(np.mean([1 if plur in t else 0 for t in tops.values()]))
        served_veto.append(np.mean([1 if vch in t else 0 for t in tops.values()]))
    print(f"\nprompts where the veto channel is testable: {testable}")
    print(f"   veto-respecting chooser agrees with plurality: {same}/{testable} "
          f"({same / testable:.1%})")
    print(f"   it changes the winner:                        {diff}/{testable} "
          f"({diff / testable:.1%})")
    if diff:
        print(f"   when it switches, the new pick's plurality rank: "
              f"{dict(sorted(switch_rank.items()))}")
    sp, sv = float(np.mean(served_plur)), float(np.mean(served_veto))
    se = float(np.std(np.array(served_veto) - np.array(served_plur), ddof=1)
               / math.sqrt(len(served_plur)))
    print(f"   people served: plurality {sp:.3f}  veto-respecting {sv:.3f}  "
          f"delta {sv - sp:+.4f} +- {1.96 * se:.4f}")

    # ---- who uses the channel
    grp = defaultdict(list)
    for cid, per in rank.items():
        for aid in per:
            if aid in veto.get(cid, {}):
                for k, val in (demo.get(aid) or {}).items():
                    if isinstance(val, str) and val and len(val) < 60:
                        grp[(k, val)].append(len(veto[cid][aid]))
    rows = [(k, float(np.mean(v)), len(v)) for k, v in grp.items() if len(v) >= 50]
    rows.sort(key=lambda r: -r[1])
    overall = float(np.mean([x for v in grp.values() for x in v]))
    print(f"\nmean vetoes cast (overall {overall:.3f}) -- extremes among groups with n>=50:")
    for k, m, n in rows[:3] + rows[-3:]:
        print(f"   {k[1][:30]:30s} {m:.3f}  (n={n})")

    (OUT / "veto.json").write_text(json.dumps({
        "prompts": n_prompts, "prompts_with_any_veto_block": with_block,
        "assessments": total_assess, "assessments_with_block": answered,
        "coverage": round(answered / total_assess, 4),
        "p_unacceptable_by_rank": {str(p): round(by_rank[p] / tot_rank[p], 4) for p in tot_rank},
        "veto_count_distribution": {str(c): round(counts[c] / tot_c, 4) for c in sorted(counts)},
        "rank_only_pseudo_r2": round(mcfadden, 4),
        "testable_prompts": testable, "agrees_with_plurality": same, "changes_winner": diff,
        "change_rate": round(diff / testable, 4) if testable else None,
        "served_plurality": round(sp, 4), "served_veto_respecting": round(sv, 4),
        "served_delta": round(sv - sp, 5), "served_delta_ci95": [round(sv - sp - 1.96 * se, 5),
                                                                 round(sv - sp + 1.96 * se, 5)],
        "mean_vetoes_overall": round(overall, 4),
        "group_extremes": [{"axis": k[0], "group": k[1], "mean_vetoes": round(m, 4), "n": n}
                           for k, m, n in rows[:5] + rows[-5:]],
        "instrument": "none -- human rankings and veto blocks only",
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
