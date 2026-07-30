"""r98 -- triage r58's UNVERIFIED pool by what it would COST to resolve each contrast.

CLAIM CARD
----------
Claim      r58 reports 27 UNVERIFIED contrasts under a single label, as though they
           were one backlog.
Estimand   a partition of those 27 by RESOLVABILITY, on two axes that are decidable
           from the source tree: (a) does the estimand admit a per-unit paired vector
           at all, and (b) what would a replay cost.
Target
observed?  PARTLY, and the split is the point. Axis (b) is decidable by reading each
           round's source for a model load. Axis (a) is NOT decidable mechanically --
           it needs the contrast's estimator read -- and has been read for only two
           rounds. Every count below is labelled with which axis it rests on.
Alternative
worlds     B BACKLOG      most of the 27 are recoverable at low cost. Then the pool is
                          work not yet done, and r97's replay is the template.
           M MIXED        the pool contains structurally unverifiable contrasts, cheap
                          replays and expensive ones. Then "UNVERIFIED: 27" is not a
                          backlog figure and should never be quoted as one.
Intervention
           none. A census over r58's stored rows and the rounds' own source.
Null       the partition must sum to 27 and no contrast may fall in two classes. A
           triage whose classes overlap or leak is not a partition and cannot be
           quoted.

WHY THIS IS THE STEP
--------------------
Entry 189 left 27 UNVERIFIED and named two of them structural. Quoting "27" invites the
reading that 27 pieces of work remain, which is false in at least two directions: some
cannot be resolved at any cost, and some need a model that is frozen. A count that
cannot be acted on is worse than no count, because it looks like a plan.

WHAT THIS ROUND MUST NOT DO, WRITTEN BEFORE THE RUN
----------------------------------------------------
It must not label a contrast RECOVERABLE from the cost axis alone. Cheap-to-replay says
nothing about whether the estimand is a mean of paired units -- r87 and r96 are both
pure CPU and both structurally unverifiable, which is exactly the pair that would be
mislabelled by a cost-only reading. The recoverable class is therefore reported as
CANDIDATE, with its estimand type explicitly UNVERIFIED per contrast.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

_HERE = pathlib.Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

R58 = _ROOT / "06_the_judges_mechanism/r58_equivalence_census/results/r58_equivalence_census.json"
MODEL = re.compile(r"AutoModel|from_pretrained|torch\.|cuda|transformers|Judge\(|build_prompt", re.I)
GENERATES = re.compile(r"generate\(|do_sample|max_new_tokens", re.I)

# Estimand type READ from the round's own estimator, not inferred. Only these have been
# read; everything else is recorded as unread rather than assumed.
ESTIMAND_READ = {
    "r87": ("pooled ratio", "attribution arms are own/donor ratios of prompt-MEANS; a "
                            "nonlinear function of aggregates has no per-prompt decomposition"),
    "r96": ("pooled ratio", "share_near/share_random per judge, differenced across judges; "
                            "each share is itself a ratio of prompt-means"),
}
FROZEN_ROUNDS = {"r20": "more paraphrase sweeps are frozen"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=pathlib.Path, default=_RES / "r98_unverified_triage.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not R58.exists():
        raise SystemExit("REFUSING: r58's census is absent; this round triages its rows.")
    unv = [r for r in json.load(open(R58))["contrasts"] if r["cell"] == "UNVERIFIED"]
    total = len(unv)

    classes: dict[str, list] = {"structural": [], "candidate_cpu": [], "needs_model": [],
                                "needs_model_frozen": []}
    per_round = {}
    for rnd in sorted({r["round"] for r in unv}, key=lambda x: int(x[1:])):
        rows = [r for r in unv if r["round"] == rnd]
        src = next((p for p in _ROOT.glob(f"[0-9][0-9]_*/{rnd}_*/run.py")), None)
        t = src.read_text() if src else ""
        needs_model, gens = bool(MODEL.search(t)), bool(GENERATES.search(t))
        if rnd in ESTIMAND_READ:
            k = "structural"
        elif needs_model:
            k = "needs_model_frozen" if rnd in FROZEN_ROUNDS else "needs_model"
        else:
            k = "candidate_cpu"
        classes[k] += rows
        per_round[rnd] = {"n": len(rows), "class": k, "loads_model": needs_model,
                          "generates": gens,
                          "estimand_read": ESTIMAND_READ.get(rnd, (None, None))[0],
                          "frozen_because": FROZEN_ROUNDS.get(rnd)}
        print(f"  {rnd:<5} {len(rows):>2}  {k:<20} model={'Y' if needs_model else 'n'} "
              f"{'GENERATES' if gens else ''}{'  [' + FROZEN_ROUNDS[rnd] + ']' if rnd in FROZEN_ROUNDS else ''}")

    # ---- the partition must be a partition -------------------------------------
    counted = sum(len(v) for v in classes.values())
    ids = [(r["round"], r["path"], r["file"]) for v in classes.values() for r in v]
    if counted != total or len(set(ids)) != total:
        raise SystemExit(f"REFUSING: {counted} classified against {total} UNVERIFIED, "
                         f"{len(set(ids))} distinct. A triage whose classes overlap or leak is "
                         f"not a partition and cannot be quoted.")
    print(f"\n  partition check: {counted} classified = {total} UNVERIFIED, all distinct  OK")
    for k, v in classes.items():
        print(f"    {k:<22} {len(v):>2}")

    n = {k: len(v) for k, v in classes.items()}
    world = "M MIXED" if n["structural"] or n["needs_model_frozen"] else "B BACKLOG"

    verdict = (
        f"{world}. r58 reports {total} UNVERIFIED contrasts under one label, which invites reading it "
        f"as {total} pieces of outstanding work. It is not. Partitioned by what resolving each would "
        f"COST: {n['structural']} are STRUCTURAL -- r87's and r96's estimands are pooled ratios of "
        f"prompt-means, and a nonlinear function of aggregates has no per-unit paired vector, so no "
        f"amount of persistence or compute resolves them and r58's TOST cannot consume them in "
        f"principle. {n['needs_model']} need a MODEL LOADED to replay, and a further "
        f"{n['needs_model_frozen']} need one AND sit behind a freeze ("
        + "; ".join(f"{k}: {v}" for k, v in FROZEN_ROUNDS.items()) + f"). The remaining "
        f"{n['candidate_cpu']} are CANDIDATES for a CPU replay of the r97 kind -- inputs on disk, no "
        f"model, seconds of compute. "
        f"THE WORD 'CANDIDATE' IS DOING WORK AND IS NOT A HEDGE: cheap-to-replay says NOTHING about "
        f"whether the estimand is a mean of paired units, and the two rounds proven structural are "
        f"BOTH pure CPU -- exactly the pair a cost-only reading would have mislabelled as recoverable. "
        f"Estimand type has been READ for {len(ESTIMAND_READ)} rounds and is UNVERIFIED for the rest, "
        f"so the candidate count is an upper bound on recoverable work and not a work queue. "
        f"PARTITION CONTROL: {counted} rows classified against {total} UNVERIFIED, all distinct; the "
        f"round refuses to run if the classes overlap or leak, because a triage that is not a "
        f"partition cannot be quoted. WHAT THIS CHANGES: 'UNVERIFIED: {total}' should never again be "
        f"quoted as a backlog figure. At most {n['candidate_cpu']} of it is actionable without a "
        f"model, at least {n['structural']} of it is not actionable at all, and the difference is "
        f"invisible in the census's own label."
    )

    doc = {
        "total_unverified": total, "counts": n, "per_round": per_round,
        "estimand_read_for": sorted(ESTIMAND_READ), "frozen_rounds": FROZEN_ROUNDS,
        "partition_verified": True, "world": world,
        "outcome_variable_scope": (
            "A partition of r58's stored UNVERIFIED rows by resolvability. No measurement, no model, "
            "no new data -- the cost axis is read from each round's source, the estimand axis from "
            "its estimator where that has been read."),
        "scope": (
            "The COST axis is decidable from the source and is complete. The ESTIMAND axis is not "
            "mechanically decidable and has been read for r87 and r96 only, so 'candidate_cpu' is an "
            "UPPER BOUND on recoverable contrasts, never a work queue. A candidate whose estimand "
            "turns out pooled joins the structural class and no compute would have helped it."),
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
