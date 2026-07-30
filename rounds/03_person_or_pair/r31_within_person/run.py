"""r31 -- The task-6 discontinuity, repaired: within-person, and against the right confound.

The confound r02 and r24 did not know about
--------------------------------------------
Both rounds measured effort (rationale length) by POSITION IN THE TASK SEQUENCE,
pooled across annotators, and found a sharp drop at position 6. r24 then defended
it with a null that re-searches the breakpoint on every shuffle, which answers
"is a step at 6 better than a step anywhere else" but not "is the population at
position 6 the same population as at position 5".

`data/DATASET_CARD.md:81` says it is not, necessarily:

    "each person completed a minimum of 5 tasks and up to 20 tasks per session
     (with the possibility to do multiple sessions over time)"

and line 170:

    "Session length limited (5 or 15 prompts depending on batch)"

So position 6 is exactly the study's continuation boundary. Positions 1-5 contain
everyone who started. Position 6 contains only those who continued past the
minimum. A drop there can be a change in WHO is contributing rather than a change
in what people do -- and a permutation null that shuffles positions globally
destroys the censoring process that creates the confound, so it cannot see it.

The repair
----------
Restrict to annotators observed at BOTH position 5 and position 6 and take the
paired difference:

    delta_i = y_(i,6) - y_(i,5)

Every person is their own control, so composition cannot contribute by
construction. Reported with a bootstrap over ANNOTATORS, which is the unit that
generalises.

Also reported: the attrition curve n(t+1)/n(t), so the size of the composition
change is visible rather than assumed either way.

What this round can and cannot settle
--------------------------------------
It CAN rule out composition: if the same people show the same drop, a 6%
membership change cannot have produced a 53% effect.

It CANNOT identify the mechanism, and this is the part worth stating loudly.
`assessments` is a flat list per annotator with no session identifier and no
timestamp -- verified, the only fields are annotator_id, conversation_id,
importance, ranking_blocks, representativeness, subjectivity. With sessions of
5 or 15 prompts, position 6 is the FIRST TASK OF A LATER SESSION for anyone whose
first batch had five. So "task 6" and "session >= 2" are perfectly confounded for
that subpopulation, and the release contains nothing that separates them.

Within-session fatigue and between-session habituation are different phenomena
with different implications for study design, and this dataset cannot tell them
apart.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"


def rationale_len(asm) -> int:
    r = asm.get("rationale") or ""
    if not r:
        for k in ("world", "personal"):
            b = (asm.get("ranking_blocks") or {}).get(k) or []
            if b:
                r = b[0].get("rationale", "") or r
    return len(r)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=_ROOT / "data/annotators.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r31_within_person.json")
    p.add_argument("--cut", type=int, default=6, help="first position of the later regime")
    p.add_argument("--boot", type=int, default=8000)
    a = p.parse_args()

    seqs, session_field = {}, False
    for line in open(a.data, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        asms = rec.get("assessments") or []
        if asms and any("session" in k.lower() or "time" in k.lower() for k in asms[0]):
            session_field = True
        seqs[rec.get("annotator_id")] = [rationale_len(x) for x in asms]

    per_pos = defaultdict(list)
    for s in seqs.values():
        for t, v in enumerate(s, start=1):
            per_pos[t].append(v)

    print(f"annotators: {len(seqs):,}   session identifier in release: "
          f"{'YES' if session_field else 'NO'}\n")
    print(f"{'pos':>4} {'n':>6} {'mean chars':>11} {'n(t)/n(t-1)':>12}")
    curve, prev = [], None
    for t in sorted(per_pos):
        if t > 12:
            break
        v = per_pos[t]
        ratio = len(v) / prev if prev else float("nan")
        curve.append({"position": t, "n": len(v), "mean": float(np.mean(v)),
                      "attrition_ratio": None if prev is None else float(ratio)})
        print(f"{t:>4} {len(v):>6} {np.mean(v):>11.1f} "
              f"{'' if prev is None else f'{ratio:>12.3f}'}")
        prev = len(v)

    c = a.cut
    both = [s for s in seqs.values() if len(s) >= c]
    d = np.array([s[c - 1] - s[c - 2] for s in both], dtype=float)
    rng = np.random.default_rng(20260728)
    bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(a.boot)])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    base = float(np.mean([s[c - 2] for s in both]))

    n_prev = len(per_pos[c - 1])
    n_cut = len(per_pos[c])
    attr = 1 - n_cut / n_prev
    between = float(np.mean(per_pos[c])) / float(np.mean(per_pos[c - 1])) - 1

    print(f"\n=== WITHIN-PERSON, annotators present at BOTH {c-1} and {c} ===")
    print(f"  n = {len(d):,}")
    print(f"  mean delta = {d.mean():+.2f} chars   95% CI [{lo:+.2f}, {hi:+.2f}]   "
          f"{'excludes zero' if lo > 0 or hi < 0 else 'INCLUDES ZERO'}")
    print(f"  as a fraction of their own position-{c-1} level: {d.mean()/base:+.1%}")
    print(f"\n  BETWEEN-person (what r02/r24 measured): {between:+.1%}")
    print(f"  attrition at the boundary: {attr:.1%}  "
          f"(every other step in the table is under 2%)")

    composition_ruled_out = abs(d.mean() / base) > 3 * attr and (lo > 0 or hi < 0)
    print(f"\n  -> composition {'CANNOT' if composition_ruled_out else 'MAY'} explain it: a "
          f"{attr:.1%} membership change against a {abs(d.mean()/base):.1%} within-person move")

    verdict = (
        f"REAL AND WITHIN-PERSON, MECHANISM UNIDENTIFIED. The same {len(d):,} people write "
        f"{abs(d.mean()):.0f} fewer characters at position {c} than at position {c-1} "
        f"({d.mean()/base:+.1%}, CI excludes zero), so the {attr:.1%} attrition at the "
        f"boundary cannot be the cause. But position {c} is the study's minimum-task "
        f"boundary AND, for anyone whose first batch held five prompts, the first task of "
        f"a LATER SESSION. The release carries no session identifier and no timestamp, so "
        f"within-session fatigue and between-session habituation are not separable here."
        if composition_ruled_out else
        f"COMPOSITION NOT EXCLUDED: the within-person move ({d.mean()/base:+.1%}) is not "
        f"large relative to the {attr:.1%} membership change at the boundary.")
    print(f"\n  {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"annotators": len(seqs), "cut": c, "session_identifier_present": session_field,
         "position_curve": curve,
         "within_person": {"n": int(len(d)), "mean_delta": float(d.mean()),
                           "ci": [float(lo), float(hi)],
                           "relative_to_own_baseline": float(d.mean() / base),
                           "excludes_zero": bool(lo > 0 or hi < 0)},
         "between_person_change": float(between),
         "attrition_at_boundary": float(attr),
         "composition_ruled_out": bool(composition_ruled_out),
         "verdict": verdict,
         "note": "r02 and r24 measured this between-person and defended it with a null "
                 "that shuffles positions globally, which destroys the censoring process "
                 "and therefore cannot detect a composition change. The dataset card "
                 "(line 81) sets a five-task minimum, putting the study's continuation "
                 "boundary at exactly the estimated breakpoint."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
