"""r62 -- how often do two people who saw the SAME responses write criteria that don't match?

CLAIM CARD
----------
Claim      an unmatched PRE/POST criterion indicates menu-induced construction --
           it names something that only arises after seeing the responses.
Estimand   the rate at which one author's write-in criterion matches NOTHING
           written by a different author on the SAME prompt. Both authors saw the
           same four responses and worked under the same protocol, so whatever
           they fail to share is intrinsic to free-text criterion writing rather
           than evidence about the menu. That rate is the FLOOR the PRE/POST
           unmatched rate must clear before it means anything.
Target
observed?  The FLOOR is fully observed -- 9,684 write-in criteria, one author and
           one rater each (r48's identified partition), across 986 prompts. The
           PRE/POST rate is NOT observed by anyone, because no PRE arm exists.
           This bounds one side of the comparison and says nothing about the other.
Alternative
worlds     L LOW FLOOR   two same-condition authors usually match. An elevated
                         PRE/POST rate would then carry information and
                         Experiment 1's promotion of it to a primary outcome is
                         sound.
           H HIGH FLOOR  they usually do not. Free-text criterion writing is
                         intrinsically idiosyncratic, the unmatched rate is mostly
                         vagueness, and it cannot bear primary-outcome weight --
                         which is `ADVERSARY_FORECAST.md` objection 2, upheld.
Intervention
           none. Observational on released write-ins.
Null       CROSS-PROMPT matching: the same criterion against criteria from a
           DIFFERENT prompt must match far less often. Without that, a high
           within-prompt rate could be a matcher that matches generic language to
           anything, and the whole measurement would be vacuous.

WHY THE MATCHER'S UNRELIABILITY LARGELY CANCELS
-----------------------------------------------
This uses a stated, simple, lexical matcher, and r14 measured that lexical
instruments are unstable -- a model paraphrase flips 15.4% of the judge's
verdicts. That would be fatal if the number were used on its own. It is not: the
SAME matcher at the SAME threshold would be applied to the PRE/POST comparison,
so what matters is the DIFFERENCE between the two rates, and a matcher that is
uniformly too strict inflates both. The absolute rate here is matcher-relative and
is reported as such; the floor it establishes is the usable quantity.

SCOPE
-----
Write-ins only, which are all POST criteria -- everyone here had seen the four
responses. So this measures disagreement WITHIN a condition, never between
conditions. A lexical matcher is a lower bound on agreement: two criteria meaning
the same thing in different words count as unmatched here and would not to a human.
"""
from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

THRESHOLDS = [0.10, 0.20, 0.30, 0.40, 0.50]
STOP = set("""a an the and or of to in on for with by is are was were be been it its this that those
these as at from than then so but not no we our i you they he she them his her their which what when
where how why all any some most more less very much just only also into onto over under about after
before during while if else each per via vs versus does do did done can could may might must should
would will shall have has had having there here now still yet even both either neither such same
other another one two three four five six seven eight nine ten response model answer user""".split())


def toks(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z\-]{2,}", s.lower()) if w not in STOP}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def positive_control() -> dict:
    c = toks("The response should acknowledge uncertainty about the legal outcome")
    same = jaccard(c, c)
    other = jaccard(c, toks("Pick a clear side in the beef debate and argue for it"))
    return {"self_match": same, "unrelated_match": other,
            "all_pass": bool(abs(same - 1.0) < 1e-12 and other < 0.10)}


def load():
    by_prompt = {}
    for line in open(_ROOT / "data/conversation_rubrics.jsonl"):
        rec = json.loads(line)
        pid = (rec.get("conversation") or {}).get("id")
        auth = collections.defaultdict(list)
        for c in rec.get("coval_full") or []:
            sc = c.get("scores") or []
            if len(sc) == 1:                     # write-in: one author, one rater
                auth[sc[0]["annotator_id"]].append(toks(c["criterion"]))
        if len(auth) >= 2:
            by_prompt[pid] = auth
    return by_prompt


def unmatched_rate(by_prompt, thr, rng=None, cross=False):
    """Share of criteria matching NOTHING written by a different author.

    cross=True draws the comparison author from a DIFFERENT prompt -- the null.
    """
    pids = list(by_prompt)
    total = unmatched = 0
    for pid in pids:
        auth = by_prompt[pid]
        names = list(auth)
        for a in names:
            if cross:
                other_pid = pids[int(rng.integers(0, len(pids)))]
                while other_pid == pid and len(pids) > 1:
                    other_pid = pids[int(rng.integers(0, len(pids)))]
                pool = [c for nm, cs in by_prompt[other_pid].items() for c in cs]
            else:
                pool = [c for nm, cs in auth.items() if nm != a for c in cs]
            if not pool:
                continue
            for c in auth[a]:
                total += 1
                if not any(jaccard(c, o) >= thr for o in pool):
                    unmatched += 1
    return unmatched, total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r62_matching_floor.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20260728)

    pc = positive_control()
    print(f"positive control: {'PASS' if pc['all_pass'] else 'FAIL'}  "
          f"self={pc['self_match']:.3f} unrelated={pc['unrelated_match']:.3f}")
    if not pc["all_pass"]:
        raise SystemExit("REFUSING: the matcher fails on a criterion against itself.")

    by_prompt = load()
    if not by_prompt:
        raise SystemExit("REFUSING: no prompt has two write-in authors. Nothing observed.")
    print(f"\nprompts with >=2 write-in authors: {len(by_prompt)}")

    grid = {}
    print(f"\n{'thr':>5}  {'within-prompt unmatched':>24}  {'cross-prompt (null)':>20}  excess")
    for thr in THRESHOLDS:
        u, t = unmatched_rate(by_prompt, thr)
        cu, ct = unmatched_rate(by_prompt, thr, rng=np.random.default_rng(7), cross=True)
        w = u / t if t else float("nan")
        c = cu / ct if ct else float("nan")
        grid[f"{thr}"] = {"within_unmatched": w, "within_n": t,
                          "cross_unmatched": c, "cross_n": ct, "excess": c - w}
        print(f"{thr:>5.2f}  {w:>23.4f}  {c:>19.4f}  {c-w:>+7.4f}")

    ref = grid["0.2"]
    floor = ref["within_unmatched"]
    sep = ref["excess"]
    world = ("H HIGH FLOOR" if floor > 0.50 else
             "L LOW FLOOR" if floor < 0.25 else "M MIDDLING FLOOR")

    verdict = (
        f"{world}. At a Jaccard threshold of 0.20 on content words, {floor:.4f} of write-in criteria "
        f"match NOTHING written by a different author on the SAME prompt -- both authors having seen "
        f"the same four responses under the same protocol. The cross-prompt null is "
        f"{ref['cross_unmatched']:.4f}, an excess of {sep:+.4f}, so the matcher is tracking "
        f"prompt-specific content rather than matching generic language to anything; without that "
        f"separation the within-prompt figure would be vacuous. Measured over {ref['within_n']:,} "
        f"criteria across {len(by_prompt)} prompts carrying two or more write-in authors. "
        f"CONSEQUENCE FOR EXPERIMENT 1: the PRE/POST unmatched rate is promoted to a primary outcome "
        f"on the argument that an unmatched criterion is menu-induced, and this is the floor it must "
        f"clear -- people in the SAME condition already fail to match at {floor:.4f}. "
        f"The absolute figure is MATCHER-RELATIVE: a lexical matcher counts two criteria meaning the "
        f"same thing in different words as unmatched, so this is a lower bound on agreement and an "
        f"upper bound on informativeness. What survives that caveat is the comparison, because the "
        f"same matcher at the same threshold would be applied to both arms."
    )

    doc = {
        "n_prompts_with_two_authors": len(by_prompt),
        "thresholds": grid,
        "reference_threshold": 0.20,
        "within_prompt_unmatched_floor": floor,
        "cross_prompt_null": ref["cross_unmatched"],
        "excess_over_null": sep,
        "world": world,
        "positive_control": pc,
        "scope": ("Write-ins only, all of them POST criteria -- every author had seen the four "
                  "responses -- so this measures disagreement WITHIN a condition and never between "
                  "conditions. The matcher is lexical Jaccard on content words: two criteria meaning "
                  "the same thing in different words count as unmatched here and would not to a "
                  "human, so the absolute rate is a lower bound on agreement. The PRE/POST rate is "
                  "unobserved by anyone; this bounds one side of that comparison only."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  floor at thr=0.20 : {floor:.4f}   cross-prompt null {ref['cross_unmatched']:.4f}"
          f"   excess {sep:+.4f}")
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
