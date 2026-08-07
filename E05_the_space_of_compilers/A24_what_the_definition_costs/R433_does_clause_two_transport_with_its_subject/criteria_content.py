"""R433/criteria_content -- do the generated criteria EVALUATE, or do they restate the prompt?

⛔ WHY THIS RUNS BEFORE THE JUDGE LANDS, NOT AFTER. Whatever accuracy the generated arm returns,
   there are two readings and they are not the same finding:

     READING A  the core encodes WHAT A GOOD ANSWER LOOKS LIKE for this conversation -> clause ②
                is about evaluative content, and an accuracy above the length rule vindicates it.
     READING B  the core RESTATES THE PROMPT in criterion clothing -> the arm is a lexical-overlap
                detector wearing a rubric's syntax, and the same accuracy means something else
                entirely. R427 already measured that stripping ALL evaluative content (`vacuous`)
                changes neither the accuracy nor the ranking, which makes B the live rival, not a
                paranoid one.

   Running this AFTER the number lands would let the number choose the reading. It runs now, on
   CPU, while the GPU is still judging.

ESTIMAND (named before the method)
    OWN   = mean content-word Jaccard between a conversation's four generated criteria and ITS OWN
            prompt text
    OTHER = the same against a RANDOM OTHER conversation's prompt, matched on draw count
    LIFT  = OWN - OTHER
    and separately, EVAL = the share of generated criteria containing an evaluative predicate from
    a FIXED list fixed BEFORE looking at the criteria (see EVAL_WORDS below).

IDENTIFICATION
    LIFT is fully identified from the two files. EVAL is identified only up to the word list, which
    is an instrument: a word list cannot prove the ABSENCE of evaluation (a criterion may evaluate
    with words not on it). ⚠ So EVAL is reported as a LOWER BOUND on evaluative content and never
    as a measurement of its absence. This campaign's ledger has the rule: you cannot grep for an
    absence.

SCOPE  population : the 2,200 generated cores and their conversations
       instrument : content-word Jaccard after stopword removal; a fixed evaluative-word list
       baseline   : a random other conversation's prompt
       regime     : k=4, greedy decode, one few-shot prompt

WORLDS
    W-EVALUATIVE  LIFT is small relative to its null and EVAL is high -> the criteria are about
                  what a good answer does, only loosely anchored to the prompt's vocabulary.
    W-RESTATEMENT LIFT is large -> the criteria carry the prompt's own words, and a downstream
                  accuracy must be read as lexical matching, not as evaluation.
    W-BOTH        LIFT large AND EVAL high -> the criteria are evaluative sentences built from the
                  prompt's vocabulary, which is what a competent rubric writer also does. Then the
                  arm's accuracy cannot be attributed to either alone by this round.

PRE-REGISTERED KILL -- conditional on the controls
    LIFT > 3x the OTHER-vs-OTHER null spread AND EVAL < 0.50  -> W-RESTATEMENT
    LIFT <= that AND EVAL >= 0.50                             -> W-EVALUATIVE
    otherwise                                                 -> W-BOTH
    a control fails                                           -> UNVERIFIED

CONTROLS
    POSITIVE  a criterion built by COPYING eight content words out of its own prompt must score
              near the top of the OWN distribution. A similarity instrument never shown to return
              a high value cannot make its low values mean anything.
    PLACEBO   a prompt against ITSELF must score exactly 1.0.
    NEGATIVE  OTHER-vs-OTHER: two random prompts against each other, which fixes the scale that
              LIFT is large or small RELATIVE TO. Without it "0.08 is small" is an opinion.
    g=0       an empty criterion set must yield 0.0 and must not raise an exception silently.
    EVAL-CTRL the word list is run on the FIXED `generic` core, whose criteria are known to be
              evaluative, and on the raw prompts, which are known not to be. Both directions.

MULTIPLICITY  3 statistics x 1 population; no selection. Reported whole.
SEEDS         >=3 for the OTHER draws; the round asserts the seeds moved.
ARTIFACT      results/r433_criteria_content.json
IMPOSSIBLE    * proving the criteria do NOT evaluate -- a word list cannot establish an absence.
              * distinguishing "restates the prompt" from "correctly identifies what this prompt
                needs" -- those coincide by design for a good rubric, and separating them needs a
                human judgement this release does not carry.

EXIT 0 a world is named · 2 UNVERIFIED
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import re
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SAT = ROOT / "corebench" / "results"

STOP = set("""a an the and or but if then than that this these those of to in on at for with by from
as is are was were be been being it its his her their our your my you we they he she i not no do
does did doing have has had having will would can could should may might must about into over
under again further more most some such only own same so too very just now what which who whom
when where why how all any both each few other own s t don now d ll m o re ve y ain aren couldn
didn doesn hadn hasn haven isn ma mightn mustn needn shan shouldn wasn weren won wouldn""".split())

# ⚠ FIXED BEFORE LOOKING AT THE GENERATED CRITERIA. A list assembled after reading them would be
#    fitted to them, and its "coverage" would be a statement about my editing rather than the text.
EVAL_WORDS = set("""accurate accurately acknowledge acknowledges actionable address addresses avoid
avoids clear clearly complete concrete concretely correct explain explains explicit helpful honest
includes provides realistic relevant respectful specific specifically suggests supports thorough
useful accurate balanced cites considers demonstrates ensures identifies offers recommends""".split())


def words(s):
    return {w for w in re.findall(r"[a-z']+", str(s).lower()) if w not in STOP and len(w) > 2}


def jac(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    core_p = SAT / "core_gen_second.json"
    if not core_p.exists():
        print("  UNRUNNABLE: the generated core is absent. Exit 2, never 0."); return 2
    core = json.loads(core_p.read_text())

    convs = collections.OrderedDict()
    with open(ROOT / "data" / "utterances.jsonl") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            c = r.get("conversation_id")
            if c in core:
                convs.setdefault(c, set()).add(str(r.get("user_prompt") or ""))
    prompts = {c: words(" ".join(sorted(v))) for c, v in convs.items()}
    ids = sorted(set(core) & set(prompts))
    print("R433/criteria_content · do the generated criteria EVALUATE, or restate the prompt?\n")
    print(f"  conversations with both a core and a prompt: {len(ids)} of {len(core)}")
    if len(ids) < 500:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    critw = {c: words(" ".join(core[c])) for c in ids}

    # ------------------------------------------------------------------------------- controls
    ok = True
    p0 = prompts[ids[0]]
    pl = jac(p0, p0)
    ok &= (abs(pl - 1.0) < 1e-12)
    print(f"  PLACEBO   a prompt against itself -> {pl:.4f}, must be 1.0   "
          f"{'PASS' if abs(pl-1.0) < 1e-12 else '⛔ FAIL'}")
    z = jac(set(), p0)
    ok &= (z == 0.0)
    print(f"  g=0       an empty criterion set -> {z:.4f}, must be 0.0 and not raise   "
          f"{'PASS' if z == 0.0 else '⛔ FAIL'}")

    rng = np.random.default_rng(0)
    own = np.array([jac(critw[c], prompts[c]) for c in ids])
    copied = []
    for c in ids[:400]:
        take = sorted(prompts[c])[:8]
        copied.append(jac(words(" ".join(take)), prompts[c]))
    copied = np.array(copied)
    pos = copied.mean() > np.percentile(own, 90)
    ok &= pos
    print(f"  POSITIVE  criteria COPIED from their own prompt -> {copied.mean():.4f}, must exceed "
          f"the 90th pct of OWN ({np.percentile(own, 90):.4f})   "
          f"{'PASS' if pos else '⛔ FAIL — the instrument cannot see high similarity'}")

    others, seeds = [], (11, 22, 33)
    for sd in seeds:
        r = np.random.default_rng(sd)
        perm = r.permutation(len(ids))
        others.append(np.array([jac(critw[ids[i]], prompts[ids[j]])
                                for i, j in zip(range(len(ids)), perm)]))
    moved = len({float(o.mean()) for o in others}) > 1
    ok &= moved
    pp = []
    for sd in seeds:
        r = np.random.default_rng(100 + sd)
        perm = r.permutation(len(ids))
        pp.append(np.mean([jac(prompts[ids[i]], prompts[ids[j]])
                           for i, j in zip(range(len(ids)), perm)]))
    print(f"  NEGATIVE  criteria vs a RANDOM OTHER prompt -> "
          f"{np.mean([o.mean() for o in others]):.4f} over {len(seeds)} seeds, "
          f"{'moved' if moved else 'DID NOT MOVE'}   {'PASS' if moved else '⛔ FAIL'}")
    print(f"            and prompt-vs-prompt (the scale LIFT is judged against) {np.mean(pp):.4f}")

    gen_p = SAT / "core_generic.json"
    ev_generic = ev_prompt = float("nan")
    if gen_p.exists():
        g = json.loads(gen_p.read_text())
        gl = list(g.values())[0] if isinstance(g, dict) else list(g)
        ev_generic = float(np.mean([bool(words(c) & EVAL_WORDS) for c in gl]))
    ev_prompt = float(np.mean([bool(prompts[c] & EVAL_WORDS) for c in ids[:800]]))
    ev_ok = (ev_generic >= 0.5) and (ev_prompt < 0.5)
    ok &= ev_ok
    print(f"  EVAL-CTRL the word list on `generic` (known evaluative) {ev_generic:.4f} must be "
          f">=0.5, and on raw prompts (known not) {ev_prompt:.4f} must be <0.5   "
          f"{'PASS' if ev_ok else '⛔ FAIL — the list does not separate the two known cases'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r433_criteria_content.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # -------------------------------------------------------------------------------- the test
    other_m = float(np.mean([o.mean() for o in others]))
    other_sd = float(np.mean([o.std() for o in others]))
    lift = float(own.mean() - other_m)
    ev = float(np.mean([bool(words(c) & EVAL_WORDS) for c in ids for c in core[c]]))
    print(f"\n  OWN   criteria vs their own prompt   {own.mean():.4f}  (sd {own.std():.4f})")
    print(f"  OTHER criteria vs a random prompt    {other_m:.4f}  (sd {other_sd:.4f})")
    print(f"  LIFT                                 {lift:+.4f}   vs 3x null spread "
          f"{3*other_sd:.4f}")
    print(f"  EVAL  share of criteria carrying an evaluative predicate  {ev:.4f}")
    print(f"        ⚠ a LOWER BOUND: a word list cannot prove an absence of evaluation.")

    big_lift = lift > 3 * other_sd
    world = ("W-BOTH" if (big_lift and ev >= 0.50) else
             "W-RESTATEMENT" if big_lift else
             "W-EVALUATIVE" if ev >= 0.50 else "W-BOTH")
    print(f"\n  WORLD: {world}")
    if world == "W-RESTATEMENT":
        print("    ⛔ the criteria carry their prompt's own words and few evaluative predicates.")
        print("    A downstream accuracy must be read as LEXICAL MATCHING, not as evaluation.")
    elif world == "W-EVALUATIVE":
        print("    the criteria are about what a good answer does and are only loosely anchored to")
        print("    the prompt's vocabulary. An accuracy above the length rule would speak to")
        print("    evaluative content.")
    else:
        print("    the criteria are EVALUATIVE SENTENCES BUILT FROM THE PROMPT'S VOCABULARY —")
        print("    which is what a competent rubric writer also does. This round therefore cannot")
        print("    attribute the arm's accuracy to either alone, and says so rather than picking.")

    (RES / "r433_criteria_content.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "own_mean": float(own.mean()), "own_sd": float(own.std()),
         "other_mean": other_m, "other_sd": other_sd, "lift": lift,
         "prompt_vs_prompt": float(np.mean(pp)), "eval_share": ev,
         "eval_control": {"generic": ev_generic, "raw_prompts": ev_prompt},
         "positive_copied": float(copied.mean()), "n": len(ids), "seeds": list(seeds)}, indent=1))
    print(f"\n  artifact -> {(RES / 'r433_criteria_content.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
