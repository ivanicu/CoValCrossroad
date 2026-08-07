#!/usr/bin/env python3
"""R990 — does the core's construction actually remove redundancy, or only reword?

⛔ WHY. R988 found the card names `non-redundant` and `non-conflicting` as constitutive with no
clause for either. R989 went at non-conflict and hit a measured wall: core weights are not published
and only 7.8% of core items match a full item verbatim. **Non-redundancy is the one that is
reachable**, because criterion TEXT is published for both.

⚠ AND THE CONFOUND IS THE WHOLE DESIGN. Core items are SYNTHESIZED — *"rewrites all rubric items …
merges semantically redundant rubric items"* — so they use different words from full items **by
construction**. A lower within-core word overlap could therefore mean redundancy was removed, or
merely that rewriting changed the wording. **A raw core-vs-full comparison cannot tell those apart**,
so this round runs a difference-in-differences against cross-prompt baselines that carry the
vocabulary effect and no shared topic.

ESTIMAND        DiD = (core_within − core_cross) − (full_within − full_cross), where `within` is
                pairs from the same prompt and `cross` is pairs from different prompts. The cross
                terms absorb each set's own vocabulary; what remains is the selection step.
IDENTIFICATION  identified up to the similarity measure. ⚠ Jaccard over content words is a LEXICAL
                proxy for a SEMANTIC property — two criteria can repeat an idea in disjoint words.
                So the measure is sound in one direction: high overlap implies repetition; low
                overlap does NOT imply distinctness. Stated, not worked around.
SCOPE           population : 986 prompts; core pairs and size-matched full pairs
                instrument : Jaccard over content words, stopworded, model-free and reproducible
                baseline   : the same-prompt full-rubric subset (a SHAM — same topic, same
                             annotators, minus the selection step) and the cross-prompt terms
                regime     : release one; prompts with >= 2 core items and enough full items
WORLDS          A SELECTION REMOVES REDUNDANCY   DiD < 0 resolvably: core pairs overlap less than
                              size-matched full pairs, beyond what rewriting alone explains.
                B IT ONLY REWORDS   DiD is inside its own resolution: the raw gap is the vocabulary
                              shift, and the construction's non-redundancy claim is not visible in
                              the text it publishes.
                prediction matrix: A -> DiD negative with a CI excluding 0. B -> CI covering 0.
KILL            pre-registered, CONDITIONAL on the instrument controls: DiD's 95% CI covering 0 ⇒
                world A is dead and the raw −0.0072 is reported as vocabulary, not selection.
POSITIVE CTRL   the measure must SEE redundancy: a hand-written paraphrase pair must score high and
                an unrelated pair ~0. If it cannot separate those, nothing below is interpretable.
NEGATIVE CTRL   a criterion against ITSELF must score exactly 1.0.
SHAM            the same-prompt full subset: identical topic and annotator pool, size-matched,
                differing only in that no selection step ran.
NOISE FLOOR     cluster bootstrap over PROMPTS (the independent unit), 2000 draws, 3 seeds.
MULTIPLICITY    all four cells reported (core/full × within/cross), not just the contrast.
SEEDS           3 for the subset draw and the bootstrap; the CI is reported per seed.
ARTIFACT        results/redundancy_did.json with this file's source hash.
IMPOSSIBLE      semantic redundancy — N/A: needs an embedding or entailment model, and this round
                deliberately uses a model-free measure so the result cannot be an artefact of a
                judge. The lexical bound is what it buys, and it is stated.
                cross-release — N/A: one release.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import pathlib
import random
import re
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/conversation_rubrics.jsonl"
STOP = set("the a an and or of to in for on with that this it is are be as at by from not you your "
           "model response should does do any all more most if when than then but so its their "
           "there they them he she we our us can could would will may might have has had".split())
SEEDS, NBOOT = (11, 22, 33), 2000


def toks(s):
    return {w for w in re.findall(r"[a-z]{3,}", s.lower()) if w not in STOP}


def jac(a, b):
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def main() -> int:
    if not DATA.exists():
        print("  UNRUNNABLE: the rubrics file is missing. Exit 2, never 0.")
        return 2
    rows = [json.loads(l) for l in open(DATA)]

    # ── INSTRUMENT CONTROLS, before anything is computed on the corpus
    para = jac(toks("Provide a clear and direct answer to the question asked"),
               toks("Give a direct clear answer to the question that was asked"))
    unrel = jac(toks("Cite peer-reviewed sources for every factual claim"),
                toks("Use a warm friendly tone throughout"))
    selfsim = jac(toks("Acknowledge uncertainty explicitly"), toks("Acknowledge uncertainty explicitly"))
    print(f"INSTRUMENT CONTROLS  paraphrase {para:.3f} (high) · unrelated {unrel:.3f} (~0) · "
          f"self {selfsim:.3f} (exactly 1)")
    inst_ok = para > 0.4 and unrel < 0.05 and selfsim == 1.0
    if not inst_ok:
        print("  ⛔ the measure cannot separate repetition from distinctness. Exit 2, never 0.")
        return 2

    usable = []
    for r in rows:
        core = [toks(c["criterion"]) for c in r["coval_core"]]
        full = [toks(f["criterion"]) for f in r["coval_full"]]
        if len(core) >= 2 and len(full) >= len(core):
            usable.append((core, full))
    print(f"\nPOPULATION  {len(usable)} of {len(rows)} prompts usable "
          f"({len(rows)-len(usable)} excluded: <2 core items or too few full items)")

    def cells(seed):
        rng = random.Random(seed)
        cw, fw, cx, fx = [], [], [], []
        per_prompt = []
        allcore = [c for core, _f in usable for c in core]
        allfull = [f for _c, full in usable for f in full]
        for core, full in usable:
            w1 = [jac(a, b) for a, b in itertools.combinations(core, 2)]
            samp = rng.sample(full, len(core))
            w2 = [jac(a, b) for a, b in itertools.combinations(samp, 2)]
            cw += w1; fw += w2
            per_prompt.append((float(np.mean(w1)), float(np.mean(w2))))
        # cross-prompt baselines: same sets, no shared topic — these carry the vocabulary effect
        for _ in range(len(cw)):
            cx.append(jac(rng.choice(allcore), rng.choice(allcore)))
            fx.append(jac(rng.choice(allfull), rng.choice(allfull)))
        return (np.array(cw), np.array(fw), np.array(cx), np.array(fx), per_prompt)

    print(f"\n  {'seed':>5}{'core_within':>13}{'full_within':>13}{'core_cross':>12}"
          f"{'full_cross':>12}{'DiD':>10}{'95% CI':>22}")
    out_rows, verdicts = [], []
    for sd in SEEDS:
        cw, fw, cx, fx, pp = cells(sd)
        did = (cw.mean() - cx.mean()) - (fw.mean() - fx.mean())
        # cluster bootstrap over PROMPTS on the within terms; the cross terms are prompt-free
        rng = np.random.default_rng(sd)
        a = np.array([p[0] for p in pp]); b = np.array([p[1] for p in pp])
        idx = rng.integers(0, len(pp), (NBOOT, len(pp)))
        draws = (a[idx].mean(axis=1) - cx.mean()) - (b[idx].mean(axis=1) - fx.mean())
        lo, hi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
        verdicts.append(hi < 0)
        out_rows.append({"seed": sd, "core_within": float(cw.mean()), "full_within": float(fw.mean()),
                         "core_cross": float(cx.mean()), "full_cross": float(fx.mean()),
                         "did": float(did), "ci": [lo, hi], "resolved": bool(hi < 0)})
        print(f"  {sd:>5}{cw.mean():>13.4f}{fw.mean():>13.4f}{cx.mean():>12.4f}"
              f"{fx.mean():>12.4f}{did:>+10.4f}   [{lo:+.4f}, {hi:+.4f}]")

    raw = [r["core_within"] - r["full_within"] for r in out_rows]
    print(f"\n  RAW gap (core_within − full_within), before the vocabulary correction: "
          f"{np.mean(raw):+.4f}")
    print(f"  DiD  (after removing each set's cross-prompt baseline): "
          f"{np.mean([r['did'] for r in out_rows]):+.4f}")

    if all(verdicts):
        world = (f"A SELECTION REMOVES REDUNDANCY — DiD is negative with a CI excluding 0 on all "
                 f"{len(SEEDS)} seeds; the core's pairs overlap less than size-matched full pairs "
                 f"beyond what rewriting alone explains")
    elif not any(verdicts):
        world = (f"B IT ONLY REWORDS — the DiD interval covers 0 on every seed, so the raw gap is "
                 f"the vocabulary shift and non-redundancy is not visible in the published text")
    else:
        world = (f"UNVERIFIED — the seeds disagree: {sum(verdicts)} of {len(SEEDS)} resolve. "
                 f"The spread is the finding, not either side.")
    print(f"\n⭐ {world}")
    print("\n⚠ LEXICAL, ONE-DIRECTIONAL: high overlap implies repetition; low overlap does NOT imply")
    print("   distinctness. Two criteria can repeat an idea in disjoint words, and this measure")
    print("   cannot see that. A semantic instrument would be a different round.")

    out = HERE / "results" / "redundancy_did.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_prompts=len(rows), n_usable=len(usable), nboot=NBOOT, seeds=list(SEEDS),
        instrument_controls={"paraphrase": para, "unrelated": unrel, "self": selfsim, "ok": inst_ok},
        cells=out_rows, raw_gap_mean=float(np.mean(raw)),
        did_mean=float(np.mean([r["did"] for r in out_rows])), world=world,
        proxy_ledger={"property": "criteria do not repeat the same idea",
                      "proxy": "Jaccard over content words",
                      "implication": "high overlap => repetition; low overlap =/=> distinctness",
                      "safe_side": "a NEGATIVE DiD is evidence of removal; a null is NOT evidence "
                                   "of redundancy"},
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
