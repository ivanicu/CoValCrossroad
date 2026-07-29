"""r52 -- intervene on lexical overlap and watch the judge move.

CLAIM_CARD.md is the contract.  r51 found satisfaction correlates with
criterion<->response overlap at +0.2068 and said, in its own output, that it was
undercontrolled: overlap and genuine satisfaction covary in the world, so a
correlation cannot separate "the judge reads overlap" from "overlapping criteria
are the satisfied ones".

This intervenes.  For a criterion c and two responses A, B:

    c_A = c + tokens distinctive to A
    c_B = c + tokens distinctive to B
    D   = [s(c_A,A) - s(c_A,B)] - [s(c_B,A) - s(c_B,B)]

The appendage is the same KIND of object in both arms, so whatever effect gluing
a token list onto a criterion has cancels in the difference.  That symmetry is
the design.  A third arm appends tokens from an UNRELATED prompt's response --
equally rare, distinctive to neither -- and must give D ~ 0, or the effect is the
act of appending rather than the source of the tokens.

This is the only interventional round in the project.  Everything else is
observational on a fixed release.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import torch

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import MODEL_DIR, Judge, build_prompt, load_join  # noqa: E402

OUTCOME_SCOPE = (
    "Descriptive on the judge's own outputs under intervention. No human rankings and "
    "no preference proxy enter this round."
)
STOP = set("the a an and or of to in for on with is are be that this it as at by from "
           "not no should must does do response answer model user its their they was "
           "have has had can will would could may might also more most other such".split())


def toks(s):
    return [w for w in re.findall(r"[a-z']{4,}", str(s).lower()) if w not in STOP]


def distinctive(src_tokens, other_tokens, df, k=6):
    """Tokens in src, absent from the other response, rarest first by corpus df."""
    cand = [w for w in dict.fromkeys(src_tokens) if w not in other_tokens]
    cand.sort(key=lambda w: df.get(w, 0))
    return cand[:k]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r52_overlap_intervention.json")
    p.add_argument("--prompts", type=int, default=250)
    p.add_argument("--k", type=int, default=6, help="tokens appended")
    p.add_argument("--batch", type=int, default=32)
    p.add_argument("--boot", type=int, default=4000)
    p.add_argument("--smoke", action="store_true")
    a = p.parse_args()
    if a.smoke:
        a.prompts, a.boot = 12, 200
        a.out = a.out.with_name(a.out.stem + "_SMOKE.json")
        print("*** SMOKE -- must never reach the README ***")

    joined = load_join(a.comparisons, a.rubrics)
    items = []
    for pid, comp, rub in joined:
        crits = [c["criterion"] for c in (rub.get("coval_full") or [])]
        resp = [r["messages"][0]["content"] for r in comp["responses"]]
        if len(crits) >= 1 and len(resp) >= 2:
            items.append({"pid": pid, "crit": crits[0], "A": resp[0], "B": resp[1]})
    items = items[: a.prompts]
    n = len(items)
    if n < (8 if a.smoke else 100):
        raise SystemExit(f"REFUSING: only {n} usable prompts")

    df = Counter()
    for it in items:
        for w in set(toks(it["A"])) | set(toks(it["B"])):
            df[w] += 1

    rng = np.random.default_rng(20260728)
    tasks, meta = [], []
    kept = []
    for k_, it in enumerate(items):
        ta, tb = toks(it["A"]), toks(it["B"])
        dA = distinctive(ta, set(tb), df, a.k)
        dB = distinctive(tb, set(ta), df, a.k)
        # unrelated donor: another prompt's response, tokens distinctive to
        # neither A nor B -- equally rare, matching nothing here.
        j = int(rng.integers(0, n))
        while j == k_ and n > 1:
            j = int(rng.integers(0, n))
        tu = toks(items[j]["A"])
        dU = [w for w in distinctive(tu, set(ta) | set(tb), df, a.k * 3)][: a.k]
        if len(dA) < a.k or len(dB) < a.k or len(dU) < a.k:
            continue
        kept.append(k_)
        arms = {"base": it["crit"],
                "donA": it["crit"] + " Terms: " + ", ".join(dA) + ".",
                "donB": it["crit"] + " Terms: " + ", ".join(dB) + ".",
                "donU": it["crit"] + " Terms: " + ", ".join(dU) + "."}
        for arm, text in arms.items():
            for lab in ("A", "B"):
                tasks.append(build_prompt(text, it[lab]))
                meta.append((k_, arm, lab))
    print(f"prompts usable {len(kept)}/{n}   judgements {len(tasks):,}")

    judge = Judge(MODEL_DIR, batch=a.batch)
    sc = judge.score(tasks)
    del judge
    torch.cuda.empty_cache()

    S = {}
    for (k_, arm, lab), v in zip(meta, sc):
        S[(k_, arm, lab)] = float(v)

    def gap(arm, k_):
        return S[(k_, arm, "A")] - S[(k_, arm, "B")]

    D_real = np.array([gap("donA", k_) - gap("donB", k_) for k_ in kept])
    base = np.array([gap("base", k_) for k_ in kept])
    # NULL: the unrelated arm cannot favour A or B, so contrasting it with
    # itself is meaningless -- instead contrast donU against base, which is the
    # "effect of appending anything at all" and must not reproduce D_real.
    D_null = np.array([gap("donU", k_) - gap("base", k_) for k_ in kept])
    shiftA = np.array([S[(k_, "donU", "A")] - S[(k_, "base", "A")] for k_ in kept])
    shiftB = np.array([S[(k_, "donU", "B")] - S[(k_, "base", "B")] for k_ in kept])

    def ci(x):
        bs = np.array([x[rng.integers(0, len(x), len(x))].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return float(x.mean()), float(lo), float(hi)

    dm, dlo, dhi = ci(D_real)
    nm, nlo, nhi = ci(D_null)
    bm, blo, bhi = ci(base)
    sa, _, _ = ci(shiftA)
    sb, _, _ = ci(shiftB)
    print(f"\nbaseline gap s(c,A)-s(c,B)                {bm:+.4f} [{blo:+.4f},{bhi:+.4f}]")
    print(f"INTERVENTION  D = donA-gap minus donB-gap  {dm:+.4f} [{dlo:+.4f},{dhi:+.4f}]"
          f"{'  SIGNIFICANT' if (dlo > 0 or dhi < 0) else '  (ns)'}")
    print(f"NULL  unrelated-token arm minus base       {nm:+.4f} [{nlo:+.4f},{nhi:+.4f}]"
          f"{'  <- MUST be ~0' if True else ''}")
    print(f"  absolute shift from appending unrelated tokens: A {sa:+.4f}  B {sb:+.4f}")
    print(f"  (a large symmetric shift with D~0 would mean the perturbation broke the "
          f"instrument rather than that the judge reads meaning only)")

    sig = bool(dlo > 0)
    null_clean = bool(nlo < 0 < nhi)
    if sig and null_clean:
        verdict = (
            f"THE JUDGE READS OVERLAP, CAUSALLY. Appending six distinctive tokens from "
            f"response A rather than from B moves the judge's A-vs-B satisfaction gap by "
            f"{dm:+.4f} [{dlo:+.4f},{dhi:+.4f}] for the SAME criterion. The appendage is "
            f"the same kind of object in both arms, so its semantic effect cancels; what "
            f"differs is only which response donated the words. The unrelated-token null "
            f"is {nm:+.4f} {[nlo, nhi]}, spanning zero, so this is the SOURCE of the "
            f"tokens and not the act of appending. r51's +0.2068 correlation now has a "
            f"demonstrated mechanism, and r50's anchoring effect has a concrete instrument "
            f"explanation. BOUND, NOT EQUALITY: this shows overlap-sensitivity on PERTURBED "
            f"text; natural high-overlap criteria are not perturbed and this does not "
            f"measure the judge's behaviour on them")
    elif sig:
        verdict = (
            f"THE INTERVENTION MOVES THE JUDGE ({dm:+.4f}) BUT SO DOES THE NULL "
            f"({nm:+.4f}), so the effect is not shown to come from the SOURCE of the "
            f"appended tokens rather than from appending text at all. The design's own "
            f"falsifier fired and nothing causal is established")
    else:
        verdict = (
            f"NO DETECTED OVERLAP EFFECT UNDER INTERVENTION: {dm:+.4f} "
            f"[{dlo:+.4f},{dhi:+.4f}]. r51's correlation keeps its size and loses its "
            f"mechanism -- consistent with overlap tracking genuine satisfaction rather "
            f"than driving the score. AMBIGUOUS: 'judge reads meaning only' and 'the "
            f"perturbation broke the instrument' both predict this, which is why the "
            f"absolute shifts are reported (A {sa:+.4f}, B {sb:+.4f}); a large symmetric "
            f"shift points at the second")
    print(f"\n-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "prompts": len(kept), "tokens_appended": a.k, "judge": MODEL_DIR,
        "batch": a.batch,
        "baseline_gap": [bm, blo, bhi],
        "intervention_D": [dm, dlo, dhi],
        "unrelated_token_null": [nm, nlo, nhi],
        "absolute_shift_unrelated": {"A": sa, "B": sb},
        "verdict": verdict, "outcome_variable_scope": OUTCOME_SCOPE,
        "scope": ("Interventional on the judge. Shows overlap-sensitivity on PERTURBED "
                  "criterion text -- a criterion with a token list glued to it is not a "
                  "natural criterion, so this BOUNDS the judge's overlap sensitivity "
                  "rather than measuring its behaviour on naturally high-overlap "
                  "criteria. Token rarity is a live alternative to token matching, "
                  "addressed only partly by the unrelated-donor arm whose tokens are "
                  "equally rare."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
