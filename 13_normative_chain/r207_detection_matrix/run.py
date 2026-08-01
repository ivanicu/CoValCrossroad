"""19 measurement families x 23 loss shapes: which family can even SEE which shape.

ESTIMAND        for each (family i, shape j): does family i's statistic move when shape j is
                INJECTED at dose g, relative to its own movement at g=0 and under a size-matched
                null mutation. Named before any method: this is a SENSITIVITY, not an effect.
IDENTIFICATION  a cell is identified iff the shape can be injected in this data AND the family can
                be computed on it. Cells failing either are BLIND or NO-DATA, and the register
                below says which, with what each would require. That register is the deliverable
                as much as the numbers are.
SCOPE           population: the 968 prompts carrying a rubric join. instrument: structural for the
                no-judge half; Qwen3.5-2B-Base for the judge half. baseline: g=0. regime: 4
                responses per prompt, 3 dimensions after centring.
WORLDS          W1 the families are largely redundant -- most see most shapes, and a single
                retention score was defensible all along.
                W2 the families are largely COMPLEMENTARY -- each sees a different subset, most
                cells are blind, and no scalar can summarise them.
                Prediction matrix: W1 -> detection matrix is dense and low-rank. W2 -> sparse,
                and blindness is structured by family type rather than by shape severity.
KILL            pre-registered: if the detection matrix has rank 1 after thresholding -- one factor
                explaining which cells fire -- then C3 of the north star ("loss has shapes that do
                not average") is DEAD and a single score was right.
POSITIVE CTRL   `deletion` at g=1.0 removes a criterion entirely. Every family that claims to
                measure anything about criteria must fire on it. A family that does not is not
                blind to the shape -- it is broken, and it is removed from the matrix rather than
                scored 0.
NEGATIVE CTRL   `identity` -- the mutation that returns the input. Every cell must read 0. This is
                the g=0 check, and it exists because this project has built a check that cannot
                fail four times.
SHAM            `relabel` -- rename the criterion's id, change nothing semantic. Same operation
                cost, no normative content. Distinguishes "the family notices ANY edit" from "the
                family notices THIS edit".
PLACEBO         `permute_responses` on a family that is response-order invariant by construction
                must return exactly 0.
NOISE FLOOR     measured per family over 5 seeds of the null mutation, not assumed.
MULTIPLICITY    over the WHOLE grid: 19 x 23 = 437 cells. Bonferroni-scale |z| > 4.0. Cells tested
                and cells surviving both reported; non-survivors listed.
SEEDS           5, and the runner asserts the draws actually differ between seeds.
IMPOSSIBLE      §2 register printed with what each unavailable cell would require. Marked N/A, not
                "planned".

THE GRID IS A GAUGE TEST AT SCALE, which is rung 1 of the attack ladder and the cheapest kill
available. Name the transformation; ask whether the measurement notices. 437 times.

WHY IT SPLITS IN TWO. A mutation that edits criterion TEXT changes what the judge returns, so the
cell needs re-judging: 12 operators x 15,248 criteria x 4 responses is over 700k model calls, which
is why covalx/chain/mutate.py has existed with pre-registered predictions since this phase began
and NO ROUND HAS EVER CALLED IT. Cells whose shape is structural (delete a criterion, strip an
author, coerce a veto to a weight, swap the executor) need no judge and run here. The text half is
queued to the GPU separately and this file reports it as PENDING rather than as absent.
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
LETTERS = "ABCD"
SEEDS = [0, 1, 2, 3, 4]
BAR = 4.0                      # Bonferroni-scale over 437 cells

# ---------------------------------------------------------------- the 23 shapes
# status: STRUCTURAL (runs here) · TEXT (needs the judge, queued) · NODATA (with what it needs)
SHAPES = [
    ("deletion", "STRUCTURAL", "remove a criterion entirely"),
    ("substitution", "STRUCTURAL", "replace a criterion with another prompt's"),
    ("inversion", "STRUCTURAL", "flip the sign of the weight"),
    ("weakening", "STRUCTURAL", "shrink |weight| toward zero"),
    ("strengthening", "STRUCTURAL", "inflate |weight| to the scale maximum"),
    # CORRECTED BY THE MODULE I IMPORTED, not by me. My first register called these three NODATA
    # on the grounds that no scope or exception FIELD is elicited. But mutate.py injects them into
    # the TEXT -- narrow_scope appends a qualifier, remove_exception strips a carve-out -- so the
    # shapes ARE injectable. What is absent is not the ability to inject; it is the ability to
    # verify preservation by reading a field, which leaves only the behavioural route.
    ("scope_contraction", "TEXT", "append a narrowing qualifier; always applicable"),
    ("scope_expansion", "TEXT-COND", "strip an existing qualifier; only where one is present"),
    ("exception_erasure", "TEXT-COND", "strip a carve-out; only where one is present"),
    ("type_coercion", "STRUCTURAL", "represent a veto as a large negative weight"),
    ("decontextualization", "STRUCTURAL", "move a criterion to a different prompt"),
    ("provenance_stripping", "STRUCTURAL", "drop the author id"),
    ("conflation", "STRUCTURAL", "merge two criteria into one averaged item"),
    ("fragmentation", "STRUCTURAL", "split one criterion's weight across two copies"),
    ("cancellation", "STRUCTURAL", "add an equal and opposite criterion"),
    ("redundancy_masking", "STRUCTURAL", "duplicate a criterion so it counts twice"),
    ("synergy_destruction", "STRUCTURAL", "remove a pair that only matters jointly"),
    ("behavioral_inertness", "STRUCTURAL", "add a criterion with zero effect on the decision"),
    ("spurious_activation", "STRUCTURAL", "add a criterion that fires where it should not"),
    ("candidate_set_overfitting", "NODATA", "requires fresh responses; the release ships four"),
    ("executor_dependence", "STRUCTURAL", "swap the judge for a gauge variant"),
    ("path_dependence", "STRUCTURAL", "score via full-then-core against core directly"),
    ("unidentifiability", "META", "a property of the matrix, not an injectable shape"),
    ("unrepairability", "META", "a property of the repair set, not an injectable shape"),
]

# ---------------------------------------------------------------- the 19 families
FAMILIES = [
    ("literal", "STRUCTURAL", "exact match / token overlap on criterion text"),
    ("field_reconstruction", "PARTIAL", "only polarity is recoverable; scope and exception absent"),
    ("query_sufficiency", "NODATA", "needs a declared query family with ground truth"),
    ("deductive_closure", "NODATA", "criteria are not formalised; no entailment relation"),
    ("ranking", "STRUCTURAL", "Kendall tau / top-1 / winner flip on the induced ordering"),
    ("distribution", "STRUCTURAL", "the panel's distribution over top choices"),
    ("decision_sufficiency", "STRUCTURAL", "regret under a finite declared decision family"),
    ("rate_distortion", "PARTIAL", "computable only with a stipulated normative distortion"),
    ("information_bottleneck", "PARTIAL", "needs a target T; the choice of T dominates"),
    ("causal_response", "STRUCTURAL", "does intervening on the field move the decision"),
    ("causal_mediation", "STRUCTURAL", "stage-wise: full -> core -> decision"),
    ("monotonicity", "STRUCTURAL", "raise a weight, does compliance rise"),
    ("type_integrity", "STRUCTURAL", "does non-compensation survive; the veto block exists"),
    ("provenance_attribution", "STRUCTURAL", "Shapley over the aggregation, per participant"),
    ("pid", "PARTIAL", "no unique decomposition; redundancy vs unique only"),
    ("transfer", "NODATA", "requires held-out responses the release does not ship"),
    ("path_composition", "STRUCTURAL", "full path against core path on the same prompts"),
    ("repairability", "PARTIAL", "expensive; needs the repair set enumerated first"),
    ("strategic_distortion", "NODATA", "requires manipulating an actor's incentives"),
]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    n_cells = len(FAMILIES) * len(SHAPES)
    print("=" * 100)
    print(f"THE GRID: {len(FAMILIES)} families x {len(SHAPES)} shapes = {n_cells} cells")
    print("=" * 100)

    # ---------------------------------------------------------------- §2 register FIRST
    fam_bad = [(n, s, w) for n, s, w in FAMILIES if s in ("NODATA",)]
    shp_bad = [(n, s, w) for n, s, w in SHAPES if s in ("NODATA", "META")]
    print(f"\n§2 REGISTER -- what this SITE cannot do, marked N/A with what each requires")
    print(f"\n  families unavailable ({len(fam_bad)} of {len(FAMILIES)}):")
    for n, _s, w in fam_bad:
        print(f"    {n:26s} N/A -- {w}")
    print(f"\n  shapes not injectable ({len(shp_bad)} of {len(SHAPES)}):")
    for n, s, w in shp_bad:
        print(f"    {n:26s} {s:6s} -- {w}")

    fam_ok = [n for n, s, _w in FAMILIES if s != "NODATA"]
    shp_ok = [n for n, s, _w in SHAPES if s not in ("NODATA", "META")]
    runnable = len(fam_ok) * len(shp_ok)
    print(f"\n  IDENTIFIED CELLS: {len(fam_ok)} x {len(shp_ok)} = {runnable} of {n_cells} "
          f"({runnable / n_cells:.0%})")
    print(f"  The other {n_cells - runnable} are NOT failures of this experiment. They are")
    print(f"  properties of the RELEASE, and the register above is the specification for the next")
    print(f"  elicitation.")

    # ---------------------------------------------------------------- the judge split
    print(f"\n{'=' * 100}")
    print("THE SPLIT: which identified cells need the judge")
    print("=" * 100)
    print(f"  A shape that edits criterion TEXT changes what the judge returns, so its cells need")
    print(f"  re-judging. covalx/chain/mutate.py has carried 12 text operators WITH PRE-REGISTERED")
    print(f"  PREDICTIONS since this phase began, and no round has ever called it -- because the")
    print(f"  full sweep is 12 x 15,248 x 4 = 732k model calls.")
    print(f"  Structural shapes -- delete a criterion, strip an author, coerce a veto to a weight,")
    print(f"  swap the executor -- need no judge and run in this file.")

    from covalx.chain import mutate as mu
    text_ops = [f.__name__ for f in getattr(mu, "DETERMINISTIC", [])]
    print(f"\n  text operators available and unused: {len(text_ops)}")

    # APPLICABILITY IS DATA, NOT AN ASSERTION. Several operators self-report ok=False when the
    # input has nothing to mutate -- no qualifier to strip, no carve-out to remove. Measured on
    # the real corpus rather than assumed, because "this shape is injectable" is false for a
    # criterion the operator cannot touch, and the RATE is what decides whether the cell has power.
    crit = []
    for line in (DATA / "conversation_rubrics.jsonl").open():
        r = json.loads(line)
        crit += [it["criterion"] for it in r["coval_full"]]
    rng = random.Random(0)
    samp = rng.sample(crit, min(2000, len(crit)))
    rate = {}
    for f in getattr(mu, "DETERMINISTIC", []):
        oks = sum(1 for t in samp if getattr(f(t), "ok", True))
        rate[f.__name__] = oks / len(samp)
    for t in text_ops:
        r_ = rate.get(t, float("nan"))
        flag = "" if r_ > 0.5 else ("  <- applies to a MINORITY" if r_ > 0.02
                                    else "  <- effectively INAPPLICABLE")
        print(f"    {t:24s} applies to {r_:6.1%} of 2,000 sampled criteria{flag}")
    dead = [t for t, r_ in rate.items() if r_ <= 0.02]
    print(f"\n  {len(dead)} operator(s) are effectively inapplicable on this corpus: {dead}")
    print(f"  Their cells are IDENTIFIED but UNPOWERED -- a distinction the register would have")
    print(f"  hidden, because 'injectable in principle' and 'injectable here' are different claims.")

    (OUT / "register.json").write_text(json.dumps(
        {"families": [{"name": n, "status": s, "note": w} for n, s, w in FAMILIES],
         "shapes": [{"name": n, "status": s, "note": w} for n, s, w in SHAPES],
         "cells_total": n_cells, "cells_identified": runnable,
         "unavailable_families": [n for n, _s, _w in fam_bad],
         "uninjectable_shapes": [n for n, _s, _w in shp_bad],
         "text_operators_unused": text_ops, "operator_applicability": rate,
         "inapplicable_operators": dead,
         "multiplicity_bar_z": BAR, "seeds": SEEDS}, indent=1))
    print(f"\n  register written. Next: the structural half runs; the text half is a GPU job.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
