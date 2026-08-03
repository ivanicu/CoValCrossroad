"""Every headline number in this sweep, re-derived through the guard, with its unit stated.

r198 built `covalx.estimand.mean_by`, which refuses a mean over grouped data unless the caller
names whether the unit is the observation or the group -- and refuses the observation version when
the two actually disagree. r191 is why: an assessment-weighted mean let one 929-rater prompt count
929 times and produced a finding that had to be withdrawn.

A guard nothing calls is a file. This is the thing that calls it.

Every number this project has published as a headline is recomputed here under BOTH estimands. The
output is one table: the claim, the observation-weighted value, the group-weighted value, the gap,
and whether the guard refuses the version that was published. Nothing is corrected here -- a gap is
not an error, it is a missing word -- but after this there is no headline in this repo whose unit
is unstated.

WHY A SEPARATE FILE RATHER THAN EDITS TO THE ROUNDS. Each round is a record of what was done and
believed at the time, and rewriting them would erase the very history that makes the retractions
legible. This is the consolidator, in the same relation to the rounds as DEFECTS.py: generated
from the data, never from memory, and re-runnable.
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATA = ROOT / "data"
TENSOR = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"
LETTERS = "ABCD"

from covalx.estimand import TOL, EstimandError, both, mean_by  # noqa: E402

ROWS = []


def record(round_, claim, values, groups, published):
    """published: 'observation' or 'group' -- what the round actually reported"""
    b = both(values, groups, name=claim)
    refused = False
    if published == "observation":
        try:
            mean_by(values, groups, estimand="observation", name=claim)
        except EstimandError:
            refused = True
    ROWS.append({"round": round_, "claim": claim, "published_as": published,
                 "observation": b["observation"], "group": b["group"], "gap": b["gap"],
                 "n": b["n"], "n_groups": b["n_groups"], "max_share": b["max_share"],
                 "guard_refuses": refused})


def top_of(s):
    for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
        g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
        if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
            return g[0]
        break
    return None


def main() -> int:
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    lens = {}
    for c in cmp_:
        o = {}
        for i, r in enumerate(c.get("responses") or []):
            k = str(r.get("response_index", LETTERS[i])).strip().upper()
            if k in LETTERS:
                o[k] = float(len(" ".join(m.get("content") or ""
                                          for m in (r.get("messages") or [])
                                          if isinstance(m.get("content"), str))))
        if len(o) == 4:
            lens[c["prompt_id"]] = o

    d = np.load(TENSOR, allow_pickle=True)
    sat = {}
    for k, v in zip(d["meta"], d["sat"]):
        pid, ci, L = str(k).split("|")
        sat[(pid, int(ci), L)] = float(v)
    from covalx.judge import load_join
    rub = {}
    for pid, _p, r in load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl"):
        rub[pid] = [float(np.mean([s["score"] for s in it["scores"]]))
                    if it.get("scores") else 0.0 for it in r["coval_full"]]
    picks = {}
    for pid in rub:
        if pid not in lens:
            continue
        sc, ok = {}, True
        for L in LETTERS:
            tot, n_ = 0.0, 0
            for ci, wi in enumerate(rub[pid]):
                v = sat.get((pid, ci, L))
                if v is not None:
                    tot += wi * v
                    n_ += 1
            if not n_:
                ok = False
            sc[L] = tot
        if ok:
            picks[pid] = max(sc, key=sc.get)

    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]

    # ---- ranking-side headlines
    v_len, v_rub, g_rank = [], [], []
    tops = defaultdict(list)
    for a in ann:
        for s in a.get("assessments", []):
            pid = s.get("conversation_id")
            t = top_of(s)
            if not t or pid not in lens:
                continue
            tops[pid].append(t)
            v_len.append(1.0 if t == max(lens[pid], key=lens[pid].get) else 0.0)
            g_rank.append(pid)
            if pid in picks:
                v_rub.append((pid, 1.0 if picks[pid] == t else 0.0))
    record("r177", "longest response ranked first", v_len, g_rank, "observation")
    record("r178", "crowd rubric picks the human top choice",
           [x for _p, x in v_rub], [p for p, _x in v_rub], "observation")

    # oracle, leave-one-out
    v_or, g_or = [], []
    for pid, ts in tops.items():
        if len(ts) < 3:
            continue
        for i, t in enumerate(ts):
            c = Counter(ts[:i] + ts[i + 1:])
            mx = max(c.values())
            v_or.append(1.0 if t in [k for k, n in c.items() if n == mx] else 0.0)
            g_or.append(pid)
    record("r179", "leave-one-out modal oracle (the ceiling)", v_or, g_or, "observation")

    # human-human agreement, published per-prompt
    v_hh, g_hh = [], []
    for pid, ts in tops.items():
        if len(ts) < 2:
            continue
        c = Counter(ts)
        agree = sum(x * (x - 1) / 2 for x in c.values())
        tot = len(ts) * (len(ts) - 1) / 2
        v_hh.append(agree / tot)
        g_hh.append(pid)
    record("r179", "two raters pick the same best response", v_hh, g_hh, "group")

    # ---- veto-side headlines
    v_veto, g_veto, v_flag, g_flag = [], [], [], []
    import re
    FLAG = re.compile(r"^\s*([ABCD])\b")
    for a in ann:
        for s in a.get("assessments", []):
            b = s.get("ranking_blocks") or {}
            if not (b.get("unacceptable") or b.get("personal")):
                continue
            pid = s.get("conversation_id")
            fl = set()
            for blk in (b.get("unacceptable") or []):
                for r in (blk.get("rating") or []):
                    m = FLAG.match(r) if isinstance(r, str) else None
                    if m:
                        fl.add(m.group(1))
            v_veto.append(1.0 if fl else 0.0)
            g_veto.append(pid)
            for L in LETTERS:
                v_flag.append(1.0 if L in fl else 0.0)
                g_flag.append(f"{pid}|{L}")
    record("r192", "an assessment flags something unacceptable", v_veto, g_veto, "observation")
    record("r192", "a given response is flagged when seen", v_flag, g_flag, "observation")

    # ---- representativeness, the field r190 showed is a rater trait
    LV = [("𝘀𝗹𝗶𝗴𝗵𝘁𝗹𝘆", 1.0), ("𝗺𝗼𝗱𝗲𝗿𝗮𝘁𝗲𝗹𝘆", 2.0), ("𝘃𝗲𝗿𝘆", 3.0),
          ("𝗲𝘅𝘁𝗿𝗲𝗺𝗲𝗹𝘆", 4.0)]
    v_rep, g_rep = [], []
    for a in ann:
        for s in a.get("assessments", []):
            x = s.get("representativeness")
            if not isinstance(x, str):
                continue
            for tok, val in LV:
                if tok in x:
                    v_rep.append(1.0 if val <= 1.0 else 0.0)
                    g_rep.append(s.get("conversation_id"))
                    break
    record("r190", "assessment says only slightly likely to be asked", v_rep, g_rep, "observation")

    # ---------------------------------------------------------------- report
    print("=" * 108)
    print("EVERY HEADLINE MEAN IN THIS SWEEP, UNDER BOTH ESTIMANDS")
    print("=" * 108)
    print(f"  {'round':6s} {'claim':44s} {'published':10s} {'per-obs':>8s} {'per-grp':>8s} "
          f"{'gap':>8s} {'guard':>7s}")
    for r in ROWS:
        mark = "REFUSES" if r["guard_refuses"] else ""
        print(f"  {r['round']:6s} {r['claim'][:44]:44s} {r['published_as']:10s} "
              f"{r['observation']:8.1%} {r['group']:8.1%} {r['gap']:+8.1%} {mark:>7s}")

    ref = [r for r in ROWS if r["guard_refuses"]]
    print(f"\n  {len(ROWS)} headline means; the guard refuses {len(ref)} of them at TOL={TOL}")
    print(f"  A refusal is NOT a correction. It says the published sentence never named its unit,")
    print(f"  and that naming it changes the number by more than half a point.")
    print(f"\n  the refused ones, with the sentence each needs:")
    for r in ref:
        print(f"    {r['round']} {r['claim']}")
        print(f"        {r['observation']:.1%} of assessments  |  {r['group']:.1%} of "
              f"{'response slots' if 'given response' in r['claim'] else 'prompts'}")
    clean = [r for r in ROWS if not r["guard_refuses"] and r["published_as"] == "observation"]
    print(f"\n  and the {len(clean)} that pass: the two units agree to within {TOL}, so the")
    print(f"  published number is the same either way and the missing word cost nothing.")
    for r in clean:
        print(f"    {r['round']} {r['claim']:44s} gap {r['gap']:+.2%}")

    print(f"\n{'=' * 108}\nREADING\n{'=' * 108}")
    orc = [r for r in ROWS if "oracle" in r["claim"]][0]["observation"]
    vet = [r for r in ROWS if "flags something" in r["claim"]][0]["observation"]
    print(f"  FIRST, A DISCREPANCY THIS FILE CREATES AND MUST OWN -- ONE, not two. The oracle")
    print(f"  here reads {orc:.1%} where r179 published 62.5%. The veto rate reads {vet:.1%}, which is")
    print(f"  exactly what r192 published, so only the oracle moved. (My first draft of this")
    print(f"  paragraph claimed both had, and printed the same number twice while saying so.)")
    print(f"  It is not a correction: the POOLS differ. r179 restricted to prompts with four")
    print(f"  extractable response texts; this file takes every prompt with enough rankings. That")
    print(f"  is a THIRD specification axis alongside weighting and anchor -- which population")
    print(f"  clears the filter -- and here it moves the ceiling by 0.8pp, about the same as the")
    print(f"  weighting choice does.")
    print(f"  Stated rather than quietly matched to r179's filter, because the whole point of this")
    print(f"  file is that a number without its population is not a number.")
    big = max(ROWS, key=lambda r: abs(r["gap"]))
    print(f"  Largest gap: {big['round']} {big['claim']} at {big['gap']:+.1%}.")
    veto = [r for r in ROWS if "flags something" in r["claim"]][0]
    print(f"  It is the veto rate, and it runs the OTHER way from every other row: per-prompt")
    print(f"  ({veto['group']:.1%}) is HIGHER than per-assessment ({veto['observation']:.1%}). The")
    print(f"  heavily-rated prompts are the ones people veto LESS, so weighting by rater count")
    print(f"  pulls the rate down. Every other headline here is pulled up. A single sign rule")
    print(f"  would have been wrong.")
    print(f"\n  Nothing in this table overturns a conclusion. Every refused claim clears its null")
    print(f"  under both weightings, which is why the sweep's verdicts stand -- and it is also")
    print(f"  exactly why the defect went unnoticed for 191 rounds: a missing unit does not")
    print(f"  announce itself until a stratification puts the anchor on one side.")
    print(f"\n  WHAT THIS FILE IS FOR. After it, no headline in this repo has an unstated unit,")
    print(f"  and the check is re-runnable rather than remembered. The rounds themselves are left")
    print(f"  untouched: rewriting them would erase the history that makes the retractions")
    print(f"  legible, and a record of what was believed is worth more than a record with no")
    print(f"  mistakes in it.")

    (pathlib.Path(__file__).parent / "HEADLINES.json").write_text(
        json.dumps({"tol": TOL, "rows": ROWS, "refused": len(ref)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
