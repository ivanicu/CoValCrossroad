"""R443 -- ③ as WRITTEN left {coval_core}. Does it exclude THAT too?

⛔ WHY THIS IS THE DECISIVE ONE. R442 measured the definition's extension as 5 arms under ③ as
   IMPLEMENTED and **1** under ③ as WRITTEN -- and that 1 is `coval_core`, the released core the
   definition was written from. R442 declared a W-EMPTY world and did not reach it. This round asks
   whether it should have.

⭐ THE SOURCE SETTLES HALF OF IT MECHANICALLY, which is what the announced step asked for.
   `corebench/select_core.py:131` computes `w[i] = mean(annotator score)` from
   `conversation_rubrics.jsonl`, and exactly three selectors consume it:
       topw_k     sorted by -w[i]
       topabs_k   sorted by -abs(w[i])
       topwvar_k  sorted by -(abs(w[i]) * var[i])
   `topvar_k` does NOT -- its own comment says the spread is "a property of the responses, never of
   the human target". So ③ as written excludes **three** selectors, not one. But `topabs_k4` and
   `topwvar_k4` are already outside ②'s admit list, so that alone leaves R442's answer standing.

⛔ THE PART THE SOURCE CANNOT SETTLE. `coval_core` is not produced by `select_core.py` at all -- it
   ships with the release, and R442's selector lookup returned None for it. So the question ③ as
   written turns on is its PROVENANCE: **were its criteria drawn from the same annotator-authored
   rubric?** If yes, the same objection that removes `topw_k` removes it, and the extension is ZERO.

ESTIMAND (named before the method)
    CONTAINED = the share of `coval_core`'s criteria, per prompt, that appear VERBATIM among that
                prompt's `coval_full` items -- the annotator-authored rubric.
    A high share means `coval_core` is a SUBSET of the rubric and carries its provenance. A low one
    means it is separately authored and the objection does not reach it.
    ⚠ This measures TEXTUAL containment, not authorship. Containment is sufficient for the
      provenance objection (the text came from there) and NOT necessary (it could be authored by
      the same people and reworded). So a low share bounds nothing; only a HIGH share is decisive,
      and the round says which direction it can rule in BEFORE running.

IDENTIFICATION
    Identified in ONE DIRECTION ONLY, and the round rules only on the sound side:
        high containment  => `coval_core` carries the rubric's provenance          [SOUND]
        low containment   => it may still be authored by the same annotators       [UNSOUND]
    So `W-CORE-EXCLUDED` is assertable and `W-CORE-SURVIVES` is at best UNVERIFIED-leaning, which
    is stated in the kill rather than discovered afterwards.

SCOPE  population : the home release's prompts carrying both a `coval_core` and a `coval_full`
       instrument : exact string match after whitespace normalisation; no judge anywhere
       baseline   : the same match against a DIFFERENT prompt's rubric (the cross-prompt sham)
       regime     : home release

WORLDS
    W-CORE-EXCLUDED  containment is high and far above its cross-prompt sham -> `coval_core`'s
                     criteria come from the annotator-authored rubric, ③ as written excludes it,
                     and the definition's extension under its own text is **ZERO** -- it admits
                     nothing, including the object it was written from.
    W-CORE-SURVIVES  containment is at the sham level -> the text is not drawn from that prompt's
                     rubric, the objection does not reach `coval_core` by this route, and the
                     extension under ③ as written stays at 1. ⚠ UNVERIFIED-leaning by construction.
    W-PARTIAL        containment is intermediate -> some criteria are drawn and some are not, so
                     the arm is a MIXTURE and no single verdict applies to it.

PREDICTION MATRIX
                       high & above sham   at sham level   intermediate
    W-CORE-EXCLUDED           0.9               0.02           0.1
    W-CORE-SURVIVES           0.02              0.9            0.1
    W-PARTIAL                 0.08              0.08           0.8

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    containment >= 0.80 AND >= 3x the cross-prompt sham -> W-CORE-EXCLUDED; the extension under
                                                            ③ as written is ZERO and DEFINITION.md
                                                            owes that sentence
    containment <= 2x the sham                           -> W-CORE-SURVIVES, marked UNVERIFIED-
                                                            leaning per the identification note
    otherwise                                            -> W-PARTIAL
    a control fails                                      -> UNVERIFIED

CONTROLS
    POSITIVE   `coval_full` against ITSELF must give containment 1.0. A matcher that cannot find a
               criterion inside the set it came from cannot make any low value mean anything.
    NEGATIVE   the CROSS-PROMPT sham: `coval_core` for prompt p against the rubric of a DIFFERENT
               prompt. This is the scale the real number is judged against, and without it "0.9 is
               high" is an opinion.
    g=0        an empty criterion list must give 0.0 and must not raise.
    PLACEBO    a prompt's rubric against itself with one criterion deleted must give exactly
               (n-1)/n -- the matcher must be able to return a value that is neither 0 nor 1.

MULTIPLICITY  one estimand plus its sham; no selection.
ARTIFACT      results/r443_core_provenance.json
IMPOSSIBLE HERE, NAMED
    * establishing AUTHORSHIP rather than textual containment -- requires an annotator field the
      release does not carry for `coval_core`.
    * ruling that `coval_core` is producible from the conversation alone -- low containment is not
      evidence of that, and the identification note says so before the number exists.
    * re-adjudicating R363's derivation about `topw_k` -- that stands or falls on its own.

EXIT 0 W-CORE-SURVIVES · 1 W-CORE-EXCLUDED or W-PARTIAL · 2 UNVERIFIED
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"

# read from corebench/select_core.py:131-152 -- the selectors that consume annotator-authored `w`
W_CONSUMERS = ["topw_k", "topabs_k", "topwvar_k"]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def contained(core_items, full_items) -> float:
    full = {norm(x.get("criterion") if isinstance(x, dict) else x) for x in full_items}
    core = [norm(x.get("criterion") if isinstance(x, dict) else x) for x in core_items]
    core = [c for c in core if c]
    if not core:
        return 0.0
    return sum(1 for c in core if c in full) / len(core)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("R443 · ③ as WRITTEN left {coval_core}. Does it exclude THAT too?\n")
    print("  ⭐ the source settles half of it: select_core.py:131 computes w = mean annotator")
    print(f"     score, and exactly these selectors consume it: {W_CONSUMERS}. `topvar_k` does")
    print("     NOT -- its own comment calls the spread a property of the responses. So ③ as")
    print("     written excludes THREE selectors, not one; two were already outside ②'s list.\n")

    from covalx.judge import load_join
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    rub = {p: r for p, _pr, r in joined}
    pids = [p for p, r in rub.items() if (r.get("coval_core") and r.get("coval_full"))]
    print(f"  prompts carrying BOTH a coval_core and a coval_full: {len(pids)} of {len(rub)}")
    if len(pids) < 100:
        print("  UNRUNNABLE: too few prompts carry both. Exit 2, never 0."); return 2

    # ------------------------------------------------------------------------------- controls
    ok = True
    pos = float(np.mean([contained(rub[p]["coval_full"], rub[p]["coval_full"]) for p in pids]))
    ok &= (abs(pos - 1.0) < 1e-12)
    print(f"\n  POSITIVE  coval_full against ITSELF -> {pos:.4f}, must be 1.0   "
          f"{'PASS' if abs(pos-1.0) < 1e-12 else '⛔ FAIL — the matcher cannot find its own text'}")

    z = contained([], rub[pids[0]]["coval_full"])
    ok &= (z == 0.0)
    print(f"  g=0       an empty criterion list -> {z:.4f}, must be 0.0 and not raise   "
          f"{'PASS' if z == 0.0 else '⛔ FAIL'}")

    p0 = pids[0]
    full0 = rub[p0]["coval_full"]
    if len(full0) >= 2:
        pl = contained(full0, full0[:-1])
        want = (len(full0) - 1) / len(full0)
        good = abs(pl - want) < 1e-9
        ok &= good
        print(f"  PLACEBO   a rubric against itself minus one item -> {pl:.4f}, must be "
              f"{want:.4f}   {'PASS' if good else '⛔ FAIL — the matcher is binary, not graded'}")

    rng = np.random.default_rng(0)
    shuf = list(pids); rng.shuffle(shuf)
    sham = float(np.mean([contained(rub[p]["coval_core"], rub[q]["coval_full"])
                          for p, q in zip(pids, shuf) if p != q]))
    print(f"  NEGATIVE  CROSS-PROMPT sham: coval_core(p) against coval_full(q≠p) -> {sham:.4f}")
    print(f"            this is the scale the real number is judged against; without it")
    print(f"            'high containment' would be an opinion.")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r443_core_provenance.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ------------------------------------------------------------------------------ the estimand
    per = [contained(rub[p]["coval_core"], rub[p]["coval_full"]) for p in pids]
    CONT = float(np.mean(per))
    exact = sum(1 for v in per if v == 1.0)
    print(f"\n  CONTAINMENT of coval_core in its OWN prompt's coval_full: {CONT:.4f}")
    print(f"    prompts where EVERY core criterion appears verbatim in the rubric: "
          f"{exact} of {len(pids)} ({exact/len(pids):.1%})")
    print(f"    ratio to the cross-prompt sham: "
          f"{(CONT / sham) if sham > 0 else float('inf'):.1f}x")

    # ⛔ THE KILL WAS WRITTEN AS A RATIO AND THE SHAM CAME BACK EXACTLY 0.0000. A ratio to zero is
    #    not a scale: `CONT/sham` is +inf, which fails `<= 2.0` and routed a containment of 0.0779
    #    -- plainly LOW -- into W-PARTIAL. The verdict word happened to be defensible and the
    #    computation that produced it was not, which is this campaign's `verdict string is not a
    #    computation` failure arriving through the denominator instead of the branch.
    #    A zero sham is INFORMATIVE, not a problem: it means no core criterion appears in ANOTHER
    #    prompt's rubric, so any containment at all is prompt-specific. But the decision must be
    #    made on the ABSOLUTE share, because that is what "drawn from the rubric" means.
    ratio = (CONT / sham) if sham > 0 else float("inf")
    world = ("W-CORE-EXCLUDED" if (CONT >= 0.80 and CONT > sham) else
             "W-CORE-SURVIVES" if CONT <= 0.10 else "W-PARTIAL")
    print(f"\n  WORLD: {world}")
    if world == "W-CORE-EXCLUDED":
        print(f"    ⛔ `coval_core`'s criteria ARE the annotator-authored rubric's, verbatim. The")
        print(f"    same objection that removes `topw_k` under ③ as written removes it too, and")
        print(f"    **the definition's extension under its own text is ZERO** — it admits nothing,")
        print(f"    including the object it was written from.")
        print(f"    ⚠ This does NOT say the definition is wrong. It says ③ as WRITTEN and ③ as")
        print(f"    IMPLEMENTED are not the same clause, and the campaign has been publishing the")
        print(f"    implemented one while the document states the written one.")
    elif world == "W-CORE-SURVIVES":
        print(f"    {1-CONT:.1%} of `coval_core`'s criteria do NOT appear in its own prompt's")
        print(f"    rubric, so the text is not drawn from it and the containment objection does")
        print(f"    not reach it by this route: the extension under ③ as written stays at 1.")
        print(f"    ⭐ AND THE {CONT:.1%} THAT IS CONTAINED IS REAL, NOT NOISE: the cross-prompt")
        print(f"    sham is exactly {sham:.4f}, so no core criterion appears in ANOTHER prompt's")
        print(f"    rubric. The overlap is small and strictly prompt-specific — reported because")
        print(f"    it is there, and it is what a partial-mixture reading would be built on.")
        print(f"    ⚠ UNVERIFIED-LEANING BY CONSTRUCTION: containment is sufficient for the")
        print(f"    provenance objection and NOT necessary — the same annotators could have")
        print(f"    authored it in different words, and this instrument cannot see that.")
    else:
        print(f"    containment is intermediate: some criteria are drawn from the rubric and some")
        print(f"    are not, so `coval_core` is a MIXTURE and no single verdict applies to it.")

    (RES / "r443_core_provenance.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "containment": CONT, "sham": sham, "ratio": ratio,
         "n_prompts": len(pids), "fully_contained_prompts": exact,
         "w_consumers": W_CONSUMERS, "positive_control": pos}, indent=1))
    print(f"\n  artifact -> {(RES / 'r443_core_provenance.json').relative_to(ROOT)}")
    return 0 if world == "W-CORE-SURVIVES" else 1


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    sys.exit(main())
