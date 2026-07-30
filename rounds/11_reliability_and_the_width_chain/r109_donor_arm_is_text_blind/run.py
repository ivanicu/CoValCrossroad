"""r109 -- the headline's donor arm cannot see a single word of the donor's rubric.

CLAIM CARD
----------
Claim      The README quotes r86's +0.1215 as "CONFIRMED, not revised, by the largest-n
           cell available" for the attribution headline -- own-minus-donor over the whole
           968-prompt join, presented as the same contrast r10 and r12 measured on fewer
           prompts. r86's own comment above the line calls the donor "a rubric written for
           another question", and its scope says "a donor rubric brings its own criterion
           count".
Estimand   whether the CPU line's donor arm responds to the donor's criterion CONTENT at
           all -- and if not, which channel it does respond to.
Target
observed?  YES, and by construction rather than by inference. `agree()` scores with
           `satp`, THIS prompt's satisfaction values from r04's tensor, indexed by the
           donor's criterion POSITIONS; `weights()` reads only each item's `scores` list.
           Neither ever touches `criterion`. So the question is settled by mutating the
           donor's text and seeing whether the number moves.
Alternative
worlds     B BLIND      replacing every donor criterion's text with a fixed nonsense string
                        leaves the attribution bit-identical. Then the CPU donor arm holds
                        criterion CONTENT fixed at this prompt's own content and varies
                        only the WEIGHT VECTOR and criterion count -- so what it measures
                        is weight specificity, and r10/r12's transplant contrast, in which
                        the judge reads the donor's actual criteria, is a different
                        decomposition rather than the same number on fewer prompts.
           S SENSITIVE  the number moves. Then the text reaches the arm by some path this
                        card has not found, and the reading above is wrong.
Intervention
           three arms on one construction: (1) r86's canonical computation, (2) every
           donor criterion's TEXT replaced, weights untouched, (3) every donor criterion's
           WEIGHTS replaced, text untouched.
Null       (i) REBUILD CONTROL -- arm 1 must reproduce r86's stored 0.12146457748752204
           exactly. A demonstration about r86's number that cannot recompute it is about
           something else.
           (ii) THE MUTATION MUST LAND. Assert the mutated objects actually differ from
           the originals before recomputing, and count how many changed. A no-op mutation
           produces "bit-identical" for the most boring possible reason, and this project
           has produced three of those.
           (iii) POSITIVE CONTROL ON THE HARNESS -- arm 3 must MOVE. If mutating the
           weights also changed nothing, the harness would not be reaching the computation
           at all and arm 2's null would be worthless.

WHY THIS IS THE STEP
--------------------
r106 established that the donor arm scores this prompt's satisfactions with the donor's
weight vector, and used the fact only to make a redraw cheap. Its consequence for what the
package MEASURES was never followed. Meanwhile r10 pairs the donor's criterion TEXT with
these responses through the judge (r10:152-157) and r12 does the same (r12:231-232). Two
constructions carry one name.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
A null here does NOT show the two constructions disagree numerically -- they might land in
the same place, and this round cannot check that without the judge, which is frozen until
the human protocol is. It shows they cannot be the same MEASUREMENT, because one is
provably insensitive to a variable the other is built on. That is a claim about what the
number can mean, not about its value, and the verdict says so.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "rounds/09_form_donor_draw_and_unit/r85_agreement_by_form"))

from covalx import human_pairs, load_join  # noqa: E402
from run import agree, weights  # noqa: E402

SAT = _ROOT / "rounds/01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
R86 = _ROOT / "rounds/09_form_donor_draw_and_unit/r86_attribution_by_form/results/r86_attribution_by_form.json"
DONOR_SEED = 20260727           # r12/r54's seed, the one r86 uses
NONSENSE = "zzzz qqqq xxxx vvvv"


def attribution(keep, donor, sat):
    own_ok = own_tot = don_ok = don_tot = 0
    for k, r in enumerate(keep):
        satp = sat[r["pid"]]
        o1, t1 = agree(satp, r["items"], weights(r["items"]), r["pairs"])
        d = keep[int(donor[k])]
        o2, t2 = agree(satp, d["items"], weights(d["items"]), r["pairs"])
        if t1 and t2:
            own_ok += o1; own_tot += t1
            don_ok += o2; don_tot += t2
    return own_ok / own_tot - don_ok / don_tot, own_ok / own_tot, don_ok / don_tot


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r109_donor_arm_is_text_blind.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not R86.exists():
        raise SystemExit("REFUSING: r86's result is absent; this round recomputes its number.")

    z = np.load(SAT, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s_ in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s_)

    keep = []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        pairs = human_pairs(comp["metadata"]["assessments"])
        items = rub.get("coval_full") or []
        if pairs and items and pid in sat:
            keep.append({"pid": pid, "items": items, "pairs": pairs})
    n = len(keep)
    rng = np.random.default_rng(DONOR_SEED)
    donor = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])
    print(f"prompts {n}")

    # ---- CONTROL (i): rebuild r86 exactly -------------------------------------
    base, own_a, don_a = attribution(keep, donor, sat)
    stored = json.load(open(R86))["attribution_whole_join"]
    drift = abs(base - stored)
    print(f"\nCONTROL (i) rebuild of r86: {base:.17f} vs stored {stored:.17f}   drift {drift:.1e}")
    if drift > 1e-15:
        raise SystemExit("REFUSING: this does not reproduce r86's number, so whatever it demonstrates "
                         "is about a different computation.")
    print(f"   -> PASS   own {own_a:.4f}  donor {don_a:.4f}")

    # ---- ARM 2: replace every donor criterion's TEXT --------------------------
    kt = copy.deepcopy(keep)
    changed = 0
    for k in range(n):
        for it in kt[int(donor[k])]["items"]:
            if it.get("criterion") != NONSENSE:
                it["criterion"] = NONSENSE
                changed += 1
    # CONTROL (ii): the mutation must have LANDED, and against the object the code reads.
    orig_txt = [it.get("criterion") for r in keep for it in r["items"]]
    mut_txt = [it.get("criterion") for r in kt for it in r["items"]]
    really = sum(x != y for x, y in zip(orig_txt, mut_txt))
    print(f"\nCONTROL (ii) mutation landed: {changed:,} criterion strings overwritten, "
          f"{really:,} of {len(orig_txt):,} differ from the originals")
    if really == 0:
        raise SystemExit("REFUSING: the text mutation did not land, so a null below would mean nothing.")
    text_attr, _, text_don = attribution(kt, donor, sat)
    print(f"  attribution with every donor criterion replaced by {NONSENSE!r}: {text_attr:.17f}")
    print(f"  moved by {abs(text_attr - base):.1e}")

    # ---- ARM 3: replace every donor criterion's WEIGHTS (harness control) -----
    kw = copy.deepcopy(keep)
    wrng = np.random.default_rng(20260737)
    wchanged = 0
    for k in range(n):
        for it in kw[int(donor[k])]["items"]:
            for s_ in (it.get("scores") or []):
                s_["score"] = float(wrng.integers(-10, 11))
                wchanged += 1
    w_before = np.concatenate([weights(r["items"]) for r in keep])
    w_after = np.concatenate([weights(r["items"]) for r in kw])
    wdiff = int((w_before != w_after).sum())
    print(f"\nCONTROL (iii) weight mutation landed: {wchanged:,} scores rewritten, "
          f"{wdiff:,} of {len(w_before):,} weight values differ")
    weight_attr, _, weight_don = attribution(kw, donor, sat)
    moved = abs(weight_attr - base)
    print(f"  attribution with donor WEIGHTS randomised: {weight_attr:.6f}   moved {moved:.4f}")
    if moved < 1e-6:
        raise SystemExit("REFUSING: randomising the donor's weights changed nothing either, so the "
                         "mutation harness is not reaching the computation and arm 2's null is "
                         "worthless.")
    print("   -> PASS: the harness reaches the computation, so arm 2's null is informative.")

    blind = abs(text_attr - base) == 0.0
    world = "B BLIND" if blind else "S SENSITIVE"

    verdict = (
        f"{world}. The README quotes r86's {stored:.4f} as CONFIRMED, not revised, by the largest-n "
        f"cell available -- own-minus-donor over the whole {n}-prompt join, presented as the contrast "
        f"r10 and r12 measured on fewer prompts. r86's own comment calls the donor a rubric written for "
        f"another question. REPLACING EVERY DONOR CRITERION'S TEXT WITH {NONSENSE!r} -- {really:,} of "
        f"{len(orig_txt):,} strings genuinely overwritten, asserted before recomputing -- MOVES THE "
        f"NUMBER BY {abs(text_attr - base):.1e}. "
        + ("It is bit-identical. The CPU line's donor arm cannot see a single word of the donor's "
           "rubric, and this is not a property of the data: `agree()` scores with THIS prompt's "
           "satisfaction values from r04's tensor, indexed by the donor's criterion POSITIONS, and "
           "`weights()` reads only each item's `scores` list. Neither ever touches `criterion`. "
           if blind else
           "The text reaches the computation by a path this round did not anticipate, and the reading "
           "below does not hold. ") +
        f"POSITIVE CONTROL ON THE HARNESS, which is what makes that null informative rather than "
        f"boring: randomising the DONOR's ratings instead -- {wdiff:,} of {len(w_before):,} weight "
        f"values changed -- moves the attribution by {moved:.4f}, to {weight_attr:.4f}. The harness "
        f"reaches the computation; the text simply is not in it. REBUILD CONTROL: arm 1 reproduces "
        f"r86's stored value to {drift:.0e}. "
        f"WHAT THIS MEANS, AND IT IS A SCOPE CLAIM NOT A VALUE CLAIM: two constructions carry one name "
        f"in this package. r10 pairs the DONOR's criterion TEXT with these responses and sends it "
        f"through the judge (r10:152-157); r12 does the same (r12:231-232). Those arms vary criterion "
        f"CONTENT. The CPU line's arm holds content fixed at this prompt's OWN criteria and varies the "
        f"WEIGHT VECTOR and criterion count -- and r87 already showed a 120x spread in criterion count "
        f"moves attribution not at all, which leaves the weight vector. SO r86's {stored:.4f} IS A "
        f"WEIGHT-SPECIFICITY NUMBER: the value of knowing which of THIS prompt's criteria matter and "
        f"in which direction, not the value of having this prompt's criteria at all. It cannot confirm "
        f"a transplant contrast, because it is provably insensitive to the variable a transplant "
        f"varies. "
        f"THE CONFOUND, WRITTEN BEFORE THE RUN: this does NOT show the two constructions disagree "
        f"NUMERICALLY. They may land in the same place, and checking that needs the judge, which is "
        f"frozen until the human protocol is. It shows they cannot be the same MEASUREMENT. "
        f"SCOPE: one donor draw under r12's seed {DONOR_SEED}, the whole {n}-prompt join, r04's "
        f"satisfaction tensor taken as given -- and that tensor is where the criterion text entered, "
        f"once, for the OWN criteria only."
    )

    doc = {
        "n_prompts": n, "donor_seed": DONOR_SEED,
        "canonical_attribution": base, "r86_stored": stored, "rebuild_drift": float(drift),
        "own_accuracy": own_a, "donor_accuracy": don_a,
        "text_mutated_attribution": text_attr,
        "text_mutation_moved_by": float(abs(text_attr - base)),
        "criterion_strings_overwritten": int(really),
        "criterion_strings_total": int(len(orig_txt)),
        "weight_mutated_attribution": weight_attr,
        "weight_mutation_moved_by": float(moved),
        "weight_values_changed": wdiff, "weight_values_total": int(len(w_before)),
        "world": world,
        "outcome_variable_scope": (
            "Own-minus-donor accuracy against real human rankings over the whole join, recomputed "
            "under two mutations of the DONOR's rubric objects: its criterion text, and its ratings. "
            "No judge call and no new measurement."),
        "scope": (
            "A claim about what the number can MEAN, not about its value: it does not show the two "
            "donor constructions disagree numerically, which needs the judge. One donor draw under "
            "r12's seed. r04's satisfaction tensor is taken as given, and that tensor is where "
            "criterion text entered -- once, for the OWN criteria only."),
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
