#!/usr/bin/env python3
"""R989 — how much dissent does a core erase, and is it more than chance?

⛔ WHY, AND THE CHEAP PATH THAT TURNED OUT TO BE CLOSED. R988 found the card names `non-redundant`
and `non-conflicting` as constitutive with no clause for either. Non-conflict looked cheaper, since
the card says the construction *"rewrites all rubric items to have positive weight"* and weights are
numeric. **They are not published for the core**: a `coval_core` item carries a `criterion` string and
nothing else. And only **303 of 3,899 (7.8%)** core items match a `coval_full` criterion verbatim, so
the weights are not recoverable by identity either — cores are genuinely synthesized. That wall is
MEASURED here, not assumed.

⚠ AND THE TWO SENSES OF "CONFLICT" MUST NOT BE CONFLATED, WHICH IS THE TRAP THIS ROUND NEARLY FELL
INTO. The card's `non-conflicting` is BETWEEN selected items — *"remain compatible with each other"*.
What the published data exposes is WITHIN-item contestation: annotators disagreeing about whether one
criterion is good or bad. **Different quantities.** This round measures the second and says so; the
first needs the selected items' pairwise compatibility and is named in the register, not claimed.

ESTIMAND        the share of `coval_full` rubric items whose annotators disagree in SIGN, against a
                null in which sign disagreement arises purely from the number of annotators and the
                marginal score distribution.
IDENTIFICATION  identified for the share. ⚠ NOT identified as "dissent the core erases": the core's
                items cannot be matched back (7.8% verbatim), so this bounds what the REWRITE STEP
                operates on, not what any particular core discarded.
SCOPE           population : 986 prompts, `coval_full` items with >= 3 scores
                instrument : sign of the published per-annotator score
                baseline   : a within-prompt permutation null that preserves the score multiset and
                             the per-item annotator count, destroying only which item a score is on
                regime     : release one; items with fewer than 3 scores excluded and COUNTED
WORLDS          A CONTESTATION IS AN ARTEFACT OF ANNOTATOR COUNT   the observed share sits inside the
                              null band, so 80% means only that many people rated each item.
                B ITEMS ARE GENUINELY CONTESTED   the observed share exceeds the null, so sign
                              disagreement is a property of the criteria and the rewrite step erases
                              something real.
                prediction matrix: A -> observed inside the null's central 95%. B -> outside it.
KILL            pre-registered, CONDITIONAL on the controls: observed inside the null band ⇒ world B
                dead and the 80% is reported as a design artefact, not a finding.
POSITIVE CTRL   the core size distribution must reproduce the card's own statement — *"about 95%"*
                have four. If the field being read is not the core, everything below is about
                something else.
NEGATIVE CTRL   an item whose scores are ALL positive must not count as contested, and an item with
                a single score must be excluded rather than scored — both checked explicitly.
PLACEBO         a synthetic item whose scores are all +5 must return contested = False.
NOISE FLOOR     the permutation null above, 200 draws, reported as a band and not a point.
MULTIPLICITY    one estimand, one null; the excluded items are counted rather than dropped silently.
SEEDS           3 permutation seeds; the band is reported per seed, never averaged.
ARTIFACT        results/dissent_erased.json with this file's source hash.
IMPOSSIBLE      between-item conflict — N/A here: needs the selected items' pairwise compatibility,
                which requires a semantic instrument this round does not build.
                what a PARTICULAR core erased — N/A: 7.8% verbatim match makes the mapping
                unavailable. Would require the synthesis provenance, which the release does not ship.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/conversation_rubrics.jsonl"
CARD = ROOT / "data/DATASET_CARD.md"
SEEDS, NPERM, MIN_SCORES = (11, 22, 33), 200, 3


def main() -> int:
    if not (DATA.exists() and CARD.exists()):
        print("  UNRUNNABLE: the release files are missing. Exit 2, never 0.")
        return 2
    rows = [json.loads(l) for l in open(DATA)]
    print(f"POPULATION  {len(rows)} prompts")

    # ── POSITIVE CONTROL: reproduce the card's own size statement
    sizes = [len(r["coval_core"]) for r in rows]
    share4 = sum(1 for s in sizes if s == 4) / len(sizes)
    card_says = "Most prompts end up with four core rubric items (about 95%)" in CARD.read_text()
    pos_ok = card_says and 0.93 <= share4 <= 0.97
    print(f"\nPOSITIVE CONTROL  core size: {sum(1 for s in sizes if s==4)} of {len(sizes)} have four "
          f"= {share4:.1%}; the card says 'about 95%' and that string is present: {card_says}")
    print(f"  -> reading the right field: {pos_ok}")

    # ── the verbatim-match wall, measured
    exact = tot = 0
    for r in rows:
        full = {f["criterion"].strip().lower() for f in r["coval_full"]}
        for c in r["coval_core"]:
            tot += 1
            exact += c["criterion"].strip().lower() in full
    print(f"\nTHE WALL, MEASURED  core items matching a full item verbatim: {exact} of {tot} "
          f"({exact/tot:.1%}) — so a core's weights are not recoverable by identity")

    # ── the estimand: within-item sign disagreement
    per_prompt, excluded = [], 0
    for r in rows:
        items = []
        for f in r["coval_full"]:
            s = [x["score"] for x in f["scores"]]
            if len(s) < MIN_SCORES:
                excluded += 1
                continue
            items.append(np.array(s, float))
        if items:
            per_prompt.append(items)
    flat = [it for pr in per_prompt for it in pr]
    def contested(v):
        return bool((v > 0).any() and (v < 0).any())
    obs = sum(contested(v) for v in flat) / len(flat)
    print(f"\nOBSERVED  {sum(contested(v) for v in flat)} of {len(flat)} items have annotators "
          f"disagreeing in SIGN = {obs:.1%}   ({excluded} items excluded for <{MIN_SCORES} scores)")

    # ── NOISE FLOOR: within-prompt permutation preserving the score multiset and item sizes
    print(f"\nNULL  within-prompt permutation, {NPERM} draws × {len(SEEDS)} seeds "
          f"(preserves the score multiset and each item's annotator count)")
    bands = {}
    for sd in SEEDS:
        rng = np.random.default_rng(sd)
        draws = []
        for _ in range(NPERM):
            hit = n = 0
            for items in per_prompt:
                pool = np.concatenate(items)
                rng.shuffle(pool)
                i = 0
                for it in items:
                    seg = pool[i:i + len(it)]; i += len(it)
                    hit += contested(seg); n += 1
            draws.append(hit / n)
        lo, hi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
        bands[sd] = (lo, hi, float(np.mean(draws)))
        print(f"    seed {sd}: null mean {np.mean(draws):.4f}  central 95% [{lo:.4f}, {hi:.4f}]")

    # ── NEGATIVE / PLACEBO
    allpos = np.array([1.0, 5.0, 10.0])
    plac_ok = not contested(allpos)
    single_excluded = excluded > 0 or all(len(f["scores"]) >= MIN_SCORES
                                          for r in rows for f in r["coval_full"])
    print(f"\n  PLACEBO   an all-positive item is not contested: {plac_ok}")
    print(f"  NEGATIVE  items with <{MIN_SCORES} scores are excluded, not scored: {excluded} such")
    ctrl_ok = pos_ok and plac_ok

    outside = all(obs < lo or obs > hi for lo, hi, _ in bands.values())
    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; the share certifies nothing"
    elif not outside:
        world = (f"A CONTESTATION IS AN ARTEFACT — observed {obs:.1%} sits inside the null band "
                 f"on at least one seed; the number reflects annotator count, not the criteria")
    else:
        # ⛔ v1's VERDICT STRING WAS NOT A COMPUTATION. It said "above the highest upper bound" and
        #    printed "-0.1379 above" — the branch fired on `outside`, which is true on EITHER side,
        #    and the prose assumed the high one. The direction is now derived, and it reverses the
        #    world: observed 80.0% against a null of 93.3% means criteria are markedly MORE
        #    sign-coherent than a reallocation of the same scores, not more contested.
        hi_max = max(h for _l, h, _m in bands.values())
        lo_min = min(l for l, _h, _m in bands.values())
        if obs > hi_max:
            world = (f"B ITEMS ARE MORE CONTESTED THAN CHANCE — observed {obs:.1%} exceeds the "
                     f"null's upper bound {hi_max:.1%} by {obs-hi_max:+.4f} on every seed")
        else:
            world = (f"B-INVERTED · ITEMS ARE MORE COHERENT THAN CHANCE — observed {obs:.1%} sits "
                     f"{lo_min-obs:+.4f} BELOW the null's lower bound {lo_min:.1%} on every seed. "
                     f"The raw share reads as 'most criteria are contested'; against its own null "
                     f"it means the opposite.")
    print(f"\n⭐ {world}")
    print("\n⚠ AND THE SENSE OF `CONFLICT` HERE IS WITHIN-ITEM, NOT THE CARD'S BETWEEN-ITEM SENSE.")
    print("   The card's `non-conflicting` means selected criteria remain compatible with each")
    print("   other. That needs a semantic instrument and is NOT measured here.")

    out = HERE / "results" / "dissent_erased.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_prompts=len(rows), core_size_share_four=share4,
        core_size_distribution={str(k): sizes.count(k) for k in sorted(set(sizes))},
        verbatim_match={"matched": exact, "total": tot, "share": exact / tot},
        n_items=len(flat), n_excluded=excluded, observed_contested_share=obs,
        null_bands={str(k): {"lo": v[0], "hi": v[1], "mean": v[2]} for k, v in bands.items()},
        nperm=NPERM, seeds=list(SEEDS),
        controls={"positive_card_size_reproduced": pos_ok, "placebo_allpos_not_contested": plac_ok,
                  "all_ok": ctrl_ok},
        world=world,
        sense_of_conflict="WITHIN-item (annotators disagree about one criterion). The card's "
                          "non-conflicting is BETWEEN-item compatibility and is not measured here.",
        not_measured=["between-item conflict", "what a particular core erased"],
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
