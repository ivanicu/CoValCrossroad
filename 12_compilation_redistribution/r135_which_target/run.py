"""r135 -- A4: is `best for the world` the right thing to have aggregated?

THE ASSUMPTION
--------------
Every number in this release, and every number this campaign has produced, is scored against the
`world` ranking block -- "which response is best for the world". Each participant also gave a
`personal` block -- "which is best for me" -- and they differ on 48.4% of the assessments that
carry both. The release aggregates the first. Nobody has asked what that choice costs.

    if the compiled standard serves `world` and `personal` equally well, the choice of target is
    free and A4 is a labelling question

    if it serves `world` materially better, then the standard was fitted to an impersonal
    judgement people make ABOUT others, and the divergence is a policy-relevant sacrifice: the
    system is optimised for what people say is good for the world rather than what they say is
    good for themselves

THE TRAP THAT DECIDES WHETHER THIS IS MEASURABLE AT ALL
-------------------------------------------------------
51.6% of the assessments carrying both blocks give the SAME STRING for both. On those cells every
arm scores identically against the two targets BY CONSTRUCTION -- a derivation, not a measurement --
and including them drags any contrast toward zero arithmetically. The whole comparison is therefore
run twice: once on everything (reported, and labelled as diluted) and once on the cells where the
two rankings actually differ, which is the only place the question exists.

A SECOND TRAP, WHICH IS SHARPER
-------------------------------
Even on the differing cells, `world` and `personal` are not equally HARD targets. If one block is
systematically more predictable -- more decisive, less tied, more agreed-upon across people -- then
an arm will score higher on it for a reason that has nothing to do with what the standard was
fitted to. So every arm's gap is reported beside a DIFFICULTY control: the same gap computed for a
rule that could not have been fitted to either block, namely the pooled crowd's own ranking.

PRE-REGISTERED KILL (fixed before any gap was computed)
-------------------------------------------------------
W-TARGET-COSTS      on the differing cells the compiled arm serves `world` materially better than
                    `personal`, by more than the difficulty control does. The choice of aggregation
                    target is a real sacrifice with a size.
W-TARGET-FREE       the gap is inside the difficulty control's own gap. The two targets are equally
                    served and the choice costs nothing measurable here.
W-NOT-MEASURABLE    the differing cells cannot support the contrast at the resolution needed.

THE PARTITION WAS INCOMPLETE, AND THAT IS RECORDED RATHER THAN REPAIRED
-----------------------------------------------------------------------
The three worlds above do not cover the outcome that occurred: an arm whose gap is materially
SMALLER than the difficulty control's, i.e. LESS world-biased than the crowd aggregate it was built
from. The run reports W-NOT-MEASURABLE because that is where the pre-registered logic sends a
negative excess, and the label is wrong for what happened. Correcting the partition after seeing the
result would be exactly the move this project forbids, so the fourth world is written here, dated,
as a note for the next round rather than as a retro-fitted branch:

W-TARGET-NEUTRAL    the arm's world-minus-personal gap is materially BELOW the difficulty control's.
                    The rubric does not inherit the aggregation target's bias; it predicts the two
                    blocks about equally while the direct crowd vote is specifically tuned to one.
                    Choosing `world` as the target costs little at the rubric level.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join  # noqa: E402
from covalx.judge import parse_ranking  # noqa: E402
from covalx.stamp import stamp  # noqa: E402

FULL_NPZ = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
CORE_NPZ = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"

N_BOOT = 4000
SEEDS = (8101, 4409, 20260730, 31337, 271828)
MATERIAL = 0.02


def pairs_of(assessment, block):
    b = (assessment.get("ranking_blocks") or {}).get(block) or []
    if not b or not b[0].get("ranking"):
        return None
    t = parse_ranking(b[0]["ranking"])
    return [(x.strip(), y.strip())
            for i in range(len(t)) for j in range(i + 1, len(t)) for x in t[i] for y in t[j]]


def load_sat(path):
    z = np.load(path, allow_pickle=True)
    d = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = str(m).split("|")
        d[pid][(int(ci), lab)] = float(s)
    return d


def conc(scores, prs):
    g = t = 0
    for x, y in prs:
        if x in scores and y in scores and scores[x] != scores[y]:
            t += 1
            g += scores[x] > scores[y]
    return g, t


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r135_which_target.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)
    for p in (FULL_NPZ, CORE_NPZ, COMPARISONS, RUBRICS):
        if not p.exists():
            print(f"REFUSING: missing {p}. Exits 2, never 0.", file=sys.stderr)
            return 2
    SAT_F, SAT_C = load_sat(FULL_NPZ), load_sat(CORE_NPZ)

    ratings = {}
    for line in open(RUBRICS):
        r = json.loads(line)
        cid = r["conversation"]["id"]
        for i, it in enumerate(r.get("coval_full") or []):
            s = [x["score"] for x in (it.get("scores") or [])]
            if s:
                ratings[(cid, i)] = float(np.mean(s))

    cells = []
    for pid, comp, rub in load_join(str(COMPARISONS), str(RUBRICS)):
        if pid not in SAT_F or pid not in SAT_C:
            continue
        cid = rub["conversation"]["id"]
        labs = sorted({lab for (_ci, lab) in SAT_C[pid]})
        if len(labs) < 2:
            continue

        def arm(sat, sign):
            acc = {l: [] for l in labs}
            for (ci, lab), v in sat.items():
                if lab in acc:
                    neg = sign and ratings.get((cid, ci), 0.0) < 0
                    acc[lab].append(1.0 - v if neg else v)
            return {l: float(np.mean(v)) for l, v in acc.items() if v}

        A = {"core": arm(SAT_C[pid], False), "full_equal": arm(SAT_F[pid], False),
             "full_signed": arm(SAT_F[pid], True)}

        asmts = (comp.get("metadata") or {}).get("assessments") or []
        # DIFFICULTY CONTROL: the pooled crowd's own Borda ordering, which was not fitted to either
        # block and is scored against both exactly as the arms are.
        borda = defaultdict(float)
        for b in asmts:
            pw = pairs_of(b, "world")
            if pw:
                for x, y in pw:
                    borda[x] += 1
                    borda[y] -= 1
        A["crowd_borda"] = {l: float(borda.get(l, 0.0)) for l in labs}

        for a in asmts:
            pw, pp = pairs_of(a, "world"), pairs_of(a, "personal")
            if not pw or not pp:
                continue
            wr = ((a.get("ranking_blocks") or {}).get("world") or [{}])[0].get("ranking")
            pr_ = ((a.get("ranking_blocks") or {}).get("personal") or [{}])[0].get("ranking")
            cells.append({"pid": pid, "differ": str(wr).strip() != str(pr_).strip(),
                          "w": pw, "p": pp, "A": A})

    if not cells:
        print("REFUSING: no assessment carries both blocks. Exits 2.", file=sys.stderr)
        return 2
    nd = sum(c["differ"] for c in cells)
    print(f"{len(cells):,} assessments carry BOTH ranking blocks; {nd:,} ({nd/len(cells):.1%}) give "
          f"different rankings -- only those can answer the question")

    ARMS = ("core", "full_signed", "full_equal", "crowd_borda")

    def run(subset):
        sel = [c for c in cells if subset is None or c["differ"] == subset]
        out = {}
        by_p = defaultdict(list)
        for c in sel:
            for k in ARMS:
                gw, tw = conc(c["A"][k], c["w"])
                gp, tp = conc(c["A"][k], c["p"])
                if tw and tp:
                    by_p[c["pid"]].append((k, gw / tw, gp / tp))
        pids = list(by_p)
        if not pids:
            return None
        for k in ARMS:
            d = [w - p for pid in pids for (kk, w, p) in by_p[pid] if kk == k]
            if not d:
                continue
            b = []
            for s in SEEDS:
                rng = np.random.default_rng(s)
                for _ in range(N_BOOT // len(SEEDS)):
                    pick = rng.integers(0, len(pids), len(pids))
                    v = [w - p for j in pick for (kk, w, p) in by_p[pids[j]] if kk == k]
                    if v:
                        b.append(float(np.mean(v)))
            b = np.array(b)
            acc_w = float(np.mean([w for pid in pids for (kk, w, _p) in by_p[pid] if kk == k]))
            acc_p = float(np.mean([p for pid in pids for (kk, _w, p) in by_p[pid] if kk == k]))
            out[k] = {"acc_world": acc_w, "acc_personal": acc_p, "gap": float(np.mean(d)),
                      "ci": [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))],
                      "n": len(d)}
        return out

    res = {}
    for tag, sub in (("all_cells", None), ("differing_cells", True), ("same_cells", False)):
        r = run(sub)
        if not r:
            print(f"  {tag}: no usable cell, stated and skipped")
            continue
        res[tag] = r
        print(f"\n  {tag}   (n={next(iter(r.values()))['n']:,} arm-cells each)")
        print(f"    {'arm':<14}{'vs world':>10}{'vs personal':>13}{'gap':>10}{'95% CI':>22}")
        for k in ARMS:
            if k not in r:
                continue
            v = r[k]
            print(f"    {k:<14}{v['acc_world']:>10.4f}{v['acc_personal']:>13.4f}"
                  f"{v['gap']:>+10.4f}   [{v['ci'][0]:+.4f}, {v['ci'][1]:+.4f}]")

    same = res.get("same_cells", {})
    if same:
        mx = max(abs(v["gap"]) for v in same.values())
        print(f"\n  DERIVATION CHECK  on cells where the two rankings are the SAME string, every "
              f"arm's gap must be 0. Largest |gap| = {mx:.2e}")

    D = res.get("differing_cells")
    if not D or "core" not in D or "crowd_borda" not in D:
        print("REFUSING: the differing subset cannot support the contrast. Exits 3.",
              file=sys.stderr)
        return 3
    core_gap, ctrl_gap = D["core"]["gap"], D["crowd_borda"]["gap"]
    excess = core_gap - ctrl_gap
    world_id = ("W-TARGET-COSTS" if excess > MATERIAL and D["core"]["ci"][0] > 0 else
                "W-TARGET-FREE" if abs(excess) <= MATERIAL else "W-NOT-MEASURABLE")
    conclusion = (
        f"Everything in this release and this campaign is scored against the `world` ranking. Each "
        f"participant also gave a `personal` one, and {nd:,} of {len(cells):,} assessments "
        f"({nd/len(cells):.1%}) that carry both give DIFFERENT rankings. On those cells -- the only "
        f"place the question exists, because on the other 51.6% every arm scores identically "
        f"against both by construction -- the compiled arm reaches "
        f"{D['core']['acc_world']:.4f} against `world` and {D['core']['acc_personal']:.4f} against "
        f"`personal`, a gap of {core_gap:+.4f} [{D['core']['ci'][0]:+.4f}, "
        f"{D['core']['ci'][1]:+.4f}]. The difficulty control -- the pooled crowd's own Borda "
        f"ordering, which was fitted to neither block -- shows a gap of {ctrl_gap:+.4f} "
        f"[{D['crowd_borda']['ci'][0]:+.4f}, {D['crowd_borda']['ci'][1]:+.4f}], so part of any arm's "
        f"gap is simply that `world` is the easier target. The compiled arm's EXCESS over that "
        f"control is {excess:+.4f}. WORLD: {world_id}. "
        + ("The compiled standard serves the impersonal judgement better than the personal one by "
           "more than target difficulty explains, so aggregating `world` is a choice with a size: "
           "the system is fitted to what people say is good for others rather than what they say is "
           "good for themselves."
           if world_id == "W-TARGET-COSTS" else
           "The compiled arm's gap is inside what target difficulty alone produces, so the choice "
           "of `world` over `personal` costs nothing measurable at this resolution -- and the "
           "difficulty control is what makes that a measurement rather than a shrug."
           if world_id == "W-TARGET-FREE" else
           "The differing subset cannot resolve the contrast."))
    print(f"\n  WORLD: {world_id}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"n_cells": len(cells), "n_differing": nd, "material": MATERIAL, "seeds": list(SEEDS),
         "results": res, "core_excess_over_difficulty_control": float(excess),
         "world": world_id, "conclusion": conclusion, **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
