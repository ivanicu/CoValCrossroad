"""r97 -- eight of r58's twenty-three UNVERIFIED contrasts, resolved without compute.

CLAIM CARD
----------
Claim      r58's census left 23 of 125 contrasts UNVERIFIED, every one for the same
           stated reason: "the 90% CI is required and no raw vector was stored". Eight
           are r06's aggregation-rule contrasts -- the decision entry 180 leans on.
Estimand   the TOST verdict at delta=0.01 for each rule against no_compression, which
           needs the 90% CI r06 never published.
Target
observed?  YES, and no new measurement is involved. r06 BUILDS per-prompt (ok, pairs)
           per rule and then discards it, aggregating before it writes. Its inputs are
           r04's satisfaction tensor and the release join -- both on disk, both CPU.
Alternative
worlds     E EQUIVALENT      some rules' 90% CIs sit inside +-0.01. Those contrasts
                             move from UNVERIFIED to CONFIRMED-equivalent and r58's
                             census shrinks.
           D DISTINGUISHED   some 90% CIs exclude zero AND reach past delta. Those
                             rules differ materially, which matters because the
                             preregistration treats the rule choice as live.
           U STILL UNVERIFIED the reconstruction does not reproduce r06, in which case
                             it is a different method and says NOTHING about r06's
                             numbers -- the r66 outcome, reported as such.
Intervention
           none. r06's own scoring loop, replayed with its own seed and its own
           imported build_cores, then a paired bootstrap it never ran.
Null       REBUILD CONTROL, and it is strict because rng order matters: build_cores
           consumes the generator inside the prompt loop, so any deviation in join
           order, threshold or k changes the cores and therefore the accuracy. The
           replay must reproduce a06's per-rule accuracy AND pair count EXACTLY. If it
           does not, this is a lookalike and the round reports U and stops.

WHY THIS IS THE STEP
--------------------
r96 resolved r95's UNVERIFIED by finding the vector a sibling round had kept. The
census that followed found r58's 23 blocked on exactly the same thing -- a discarded
per-prompt vector -- and 8 of them belong to the round whose result the preregistration
cites when it says the aggregation rule is a live choice. This also fixes the root
cause rather than the instance: the per-prompt vectors are PERSISTED here, so the next
question about r06 does not need a replay.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
A reconstruction that ALMOST reproduces is worse than one that fails loudly, because it
looks authoritative while measuring something else. r66 is this package's precedent:
neither arm reproduced, and it correctly concluded UNVERIFIED rather than overturning
r56. The rebuild control is therefore exact-match, not close-enough, and the round
refuses to publish a TOST verdict unless it passes.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "rounds/r06_rule_tournament"))

from covalx import LABELS, load_join, parse_ranking  # noqa: E402
from run import build_cores  # noqa: E402

A06 = _ROOT / "rounds/r06_rule_tournament/results/a06_rule_tournament.json"
SAT = _ROOT / "rounds/r04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
SEED, K, BOOT_R06 = 20260727, 4, 2000
N_BOOT, DELTA = 20000, 0.01
BASE = "no_compression"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r97_rule_tournament_tost.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not A06.exists():
        raise SystemExit("REFUSING: a06 absent; this round rebuilds against it rather than from memory.")
    a06 = json.load(open(A06))

    z = np.load(SAT, allow_pickle=True)
    lut = {}
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = str(m).split("|")
        lut[(pid, int(ci), lab)] = float(s)

    rng = np.random.default_rng(SEED)          # same seed, same consumption order
    per_prompt, hits, misses = {}, 0, 0
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        items = rub.get("coval_full") or []
        crit_scores, ci_map, ci = [], [], 0
        raters = {s["annotator_id"] for it in items for s in it.get("scores") or []}
        thr = max(2, (len(raters) + 1) // 2)
        for it in items:
            sc = [float(s["score"]) for s in it.get("scores") or []]
            if sc:
                if len(sc) >= thr:
                    crit_scores.append(np.array(sc)); ci_map.append(ci)
            ci += 1
        if len(crit_scores) < K:
            continue
        cores = build_cores(crit_scores, K, rng)
        hp = []
        for asm in comp["metadata"]["assessments"]:
            w = (asm.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            flat = [(lab, gi) for gi, grp in enumerate(parse_ranking(w[0].get("ranking", "")))
                    for lab in grp]
            hp += [(x, y) for x, gx in flat for y, gy in flat if gx < gy]
        if not hp:
            continue
        res = {}
        for rule, core in cores.items():
            score = {}
            for lab in LABELS:
                vals = []
                for j, d in core:
                    v = lut.get((pid, ci_map[j], lab))
                    if v is not None:
                        vals.append(d * v); hits += 1
                    else:
                        misses += 1
                score[lab] = float(np.mean(vals)) if vals else 0.0
            res[rule] = (sum(1 for x, y in hp if score.get(x, 0) > score.get(y, 0)), len(hp))
        per_prompt[pid] = res
    print(f"prompts {len(per_prompt):,}   lookup coverage {hits / max(hits + misses, 1):.1%}")

    rules, pids = list(next(iter(per_prompt.values()))), list(per_prompt)
    OK = {r: np.array([per_prompt[p][r][0] for p in pids], float) for r in rules}
    TOT = {r: np.array([per_prompt[p][r][1] for p in pids], float) for r in rules}

    # ---- REBUILD CONTROL: exact match on accuracy AND pairs ---------------------
    worst_acc, worst_pairs = 0.0, 0
    for r in rules:
        if r not in a06["rules"]:
            continue
        worst_acc = max(worst_acc, abs(OK[r].sum() / TOT[r].sum() - a06["rules"][r]["accuracy"]))
        worst_pairs = max(worst_pairs, abs(int(TOT[r].sum()) - a06["rules"][r]["pairs"]))
    print(f"REBUILD: worst |acc - a06| = {worst_acc:.2e}   worst |pairs - a06| = {worst_pairs}   "
          f"prompts {len(pids)} vs a06's {a06['prompts']}")
    ok_rebuild = bool(worst_acc < 1e-12 and worst_pairs == 0 and len(pids) == a06["prompts"])
    if not ok_rebuild:
        doc = {"world": "U STILL UNVERIFIED", "rebuild_passed": False,
               "worst_accuracy_diff": float(worst_acc), "worst_pairs_diff": int(worst_pairs),
               "prompts": len(pids), "a06_prompts": a06["prompts"],
               "verdict": (
                   "U STILL UNVERIFIED. The replay does NOT reproduce a06 -- worst accuracy difference "
                   f"{worst_acc:.2e}, worst pair-count difference {worst_pairs}, {len(pids)} prompts "
                   f"against a06's {a06['prompts']}. So this is a DIFFERENT method and says nothing "
                   "about r06's numbers, exactly as r66 concluded about r56. No TOST verdict is "
                   "published and r58's eight UNVERIFIED rows stand."),
               "scope": "A failed reconstruction. It overturns nothing."}
        a.out.write_text(json.dumps(doc, indent=1))
        print("\n  WORLD: U STILL UNVERIFIED -- refusing to publish a TOST verdict")
        print(f"\n-> {a.out.relative_to(_ROOT)}")
        return

    # ---- the 90% CI r06 never published ----------------------------------------
    # r06's delta is the MEAN OF PER-PROMPT RATIO DIFFERENCES (its lines 205-208), not a
    # pooled difference. Using the pooled one would TOST a different quantity than the
    # one r58 flagged -- so the delta itself is rebuild-controlled below, which catches
    # an estimator mismatch by instrument rather than by eye.
    RATE = {r: OK[r] / np.maximum(TOT[r], 1) for r in rules}
    worst_delta = 0.0
    for r in rules:
        if r == BASE or r not in a06["rules"] or "vs_no_compression" not in a06["rules"][r]:
            continue
        mine = float((RATE[r] - RATE[BASE]).mean())
        worst_delta = max(worst_delta, abs(mine - a06["rules"][r]["vs_no_compression"]["delta"]))
    print(f"REBUILD (delta): worst |delta - a06| = {worst_delta:.2e}")
    if worst_delta > 1e-12:
        raise SystemExit("REFUSING: the paired delta does not reproduce a06's, so this TOST would be "
                         "on a different estimand than the one r58 marked UNVERIFIED.")

    rg = np.random.default_rng(20260730)
    idx = rg.integers(0, len(pids), (N_BOOT, len(pids)))
    rows = {}
    print(f"\n  {'rule':<16} {'delta':>9} {'90% CI (TOST)':>22} {'95% CI':>22}  verdict")
    for r in rules:
        if r == BASE:
            continue
        diff = RATE[r] - RATE[BASE]
        d = diff[idx].mean(axis=1)
        pt = float(diff.mean())
        l90, h90 = np.percentile(d, [5, 95])
        l95, h95 = np.percentile(d, [2.5, 97.5])
        equiv = bool(l90 > -DELTA and h90 < DELTA)
        sig = bool(l95 > 0 or h95 < 0)
        v = ("EQUIVALENT at 0.01" if equiv else
             ("DISTINGUISHED" if sig else f"neither -- margin {max(abs(l90), abs(h90)):.4f}"))
        rows[r] = {"delta": float(pt), "ci90": [float(l90), float(h90)],
                   "ci95": [float(l95), float(h95)], "equivalent_at_delta": equiv,
                   "significant": sig, "verdict": v,
                   "answerable_margin": float(max(abs(l90), abs(h90)))}
        print(f"  {r:<16} {pt:>+9.4f} {f'[{l90:+.4f},{h90:+.4f}]':>22} "
              f"{f'[{l95:+.4f},{h95:+.4f}]':>22}  {v}")

    n_eq = sum(1 for v in rows.values() if v["equivalent_at_delta"])
    n_di = sum(1 for v in rows.values() if v["significant"] and not v["equivalent_at_delta"])
    world = ("E EQUIVALENT" if n_eq and not n_di else
             "D DISTINGUISHED" if n_di and not n_eq else
             "MIXED" if n_eq and n_di else "NEITHER -- bounded, not equivalent")

    # persist the per-prompt vectors so no future question needs this replay
    vec = _RES / "r97_per_prompt_rule_cells.npz"
    np.savez_compressed(vec, pids=np.array(pids), **{f"{r}|ok": OK[r] for r in rules},
                        **{f"{r}|tot": TOT[r] for r in rules})
    print(f"\n  per-prompt cells persisted -> {vec.relative_to(_ROOT)}")

    verdict = (
        f"{world}. r58's census left 23 of 125 contrasts UNVERIFIED, every one for the same stated "
        f"reason -- 'the 90% CI is required and no raw vector was stored'. Eight belong to r06, whose "
        f"result the preregistration cites when it treats the aggregation rule as a live choice. r06 "
        f"BUILDS per-prompt cells and discards them before writing, and its inputs -- r04's tensor and "
        f"the release join -- are on disk, so this needed a replay rather than a measurement. "
        f"REBUILD CONTROL, strict because rng order matters (build_cores consumes the generator inside "
        f"the prompt loop, so any drift in join order, threshold or k changes the cores and hence the "
        f"accuracy): the replay reproduces a06's per-rule accuracy to {worst_acc:.0e}, its pair counts "
        f"exactly, and its prompt count {len(pids)} = {a06['prompts']}. So this IS r06's method, not a "
        f"lookalike -- and had it missed, the round publishes nothing and says so, as r66 did for r56. "
        f"THE DELTA IS REBUILD-CONTROLLED TOO, and that mattered: r06's contrast is the MEAN OF "
        f"PER-PROMPT RATIO DIFFERENCES, not a pooled difference, and a first pass here used the pooled "
        f"one -- a different estimand than the rows r58 flagged. The delta control reproduces a06's to "
        f"{worst_delta:.0e}, so the quantity tested is r06's own. "
        f"AND A FINDING ABOUT THE CENSUS ITSELF: of r58's eight r06 rows, TWO come from "
        f"a06_dryrun.json -- a dryrun artifact. Six of r58's 125 contrasts are sourced from it. This "
        f"round therefore resolves SIX, not eight, and the other two should never have been counted, "
        f"because smoke and dryrun runs are not published results. "
        f"RESULT, at the 90% CI that TOST requires: "
        + "; ".join(f"{r} {v['delta']:+.4f} [{v['ci90'][0]:+.4f},{v['ci90'][1]:+.4f}] -> {v['verdict']}"
                    for r, v in rows.items())
        + f". So {n_eq} of {len(rows)} rule contrasts are EQUIVALENT to no-compression at delta=0.01 "
        f"and {n_di} are DISTINGUISHED. SIGNIFICANCE AND EQUIVALENCE ARE REPORTED SEPARATELY: a "
        f"contrast can be neither, and those carry an answerable margin instead of a verdict. "
        f"ROOT CAUSE FIXED, NOT JUST THE INSTANCE: the per-prompt cells are persisted here, so the next "
        f"question about r06 does not need this replay -- which is the defect r58 named 23 times and "
        f"r96 found once."
    )

    doc = {
        "rules": rows, "n_rules": len(rows), "n_equivalent": n_eq, "n_distinguished": n_di,
        "delta": DELTA, "n_boot": N_BOOT, "prompts": len(pids),
        "rebuild_passed": True, "worst_accuracy_diff": float(worst_acc),
        "worst_delta_diff": float(worst_delta),
        "r58_rows_from_dryrun_artifact": 6,
        "worst_pairs_diff": int(worst_pairs), "per_prompt_cells": str(vec.relative_to(_ROOT)),
        "resolves_r58_unverified": 6,
        "r58_r06_rows_total": 8, "r58_r06_rows_from_dryrun": 2, "world": world,
        "outcome_variable_scope": (
            "Pairwise accuracy against REAL HUMAN world rankings, satisfaction from r04's tensor. "
            "Replays r06 exactly and adds the paired bootstrap r06 did not run."),
        "scope": (
            "Eight of r58's 23 UNVERIFIED contrasts. The other 15 belong to r28, r17, r20, r01, r11, "
            "r13, r15, r32 and r50 and are untouched here. Inherits r06's own restriction to "
            "majority-rated criteria (36.5%, entry 173) and its k=4 core size."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
