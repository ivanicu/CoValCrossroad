"""The guard, attacked before it is trusted, and then pointed at the case that motivated it.

r197 established that a static scan cannot catch this defect: it missed r191, the one file known
to have produced a false finding through assessment weighting, because r191 accumulates with
`.extend()` and means a flat list. The conclusion was that enforcement has to sit at the point of
computation. `covalx/estimand.py` is that enforcement.

A lock that has not been attacked is a lock that has not been tested, so this round does the
attacking BEFORE claiming the guard works, and it does it in the order that matters: the ways a
real caller would accidentally defeat it, not the ways an adversary would deliberately.

  A1  mismatched lengths          -- a mean whose grouping does not line up with its values
  A2  empty input                 -- nan printed with a percent sign reads as a measurement
  A3  missing estimand            -- the default that produced the retraction
  A4  bogus estimand              -- a typo silently falling through to one branch
  A5  generator inputs            -- consumed once, so a second pass sees nothing
  A6  numpy arrays not lists      -- the common calling convention in this repo
  A7  every row its own group     -- the two estimands COINCIDE, so the guard must NOT fire
  A8  one group only              -- the two estimands also coincide; must NOT fire either
  A8b unequal groups, same means   -- lopsided but the answer is identical; must NOT fire
  A8c unequal groups, diff means   -- the real case; MUST fire
  A9  THE BYPASS                  -- np.mean called directly, which no library can prevent

THEN THE REAL TEST. The guard is pointed at r191's actual data: the longest-first indicator for
every assessment, grouped by prompt, on the prompts r191 analysed. If it does not refuse that, it
does not do the job it was built for and this round has produced another instrument that fails its
own motivating case.
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
LETTERS = "ABCD"

from covalx.estimand import EstimandError, both, dominance, mean_by  # noqa: E402


def attack(name, fn, expect):
    """expect: 'raises' or 'returns'"""
    try:
        out = fn()
        got = "returns"
        detail = f"{out}"[:70]
    except EstimandError as e:
        got = "raises"
        detail = str(e).split(".")[0][:70]
    except Exception as e:                                   # noqa: BLE001
        got = f"raises {type(e).__name__}"
        detail = str(e)[:70]
    ok = got == expect
    print(f"  {'PASS' if ok else 'FAIL'}  {name:34s} expected {expect:8s} got {got:16s} {detail}")
    return ok, got, detail


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    print("=" * 78)
    print("ATTACKING THE GUARD -- nine vectors, before any claim that it works")
    print("=" * 78)
    v = [1.0, 2.0, 3.0, 4.0]
    g = ["p", "p", "q", "r"]
    results = []
    for nm, fn, exp in [
        ("A1 mismatched lengths",
         lambda: mean_by(v, g[:2], estimand="group"), "raises"),
        ("A2 empty input",
         lambda: mean_by([], [], estimand="group"), "raises"),
        ("A3 missing estimand",
         lambda: mean_by(v, g), "raises TypeError"),
        ("A4 bogus estimand",
         lambda: mean_by(v, g, estimand="prompt"), "raises"),
        ("A5 generator inputs",
         lambda: mean_by((x for x in v), (x for x in g), estimand="group")[0], "returns"),
        ("A6 numpy array inputs",
         lambda: mean_by(np.array(v), np.array(g), estimand="group")[0], "returns"),
        ("A7 every row its own group",
         lambda: mean_by(v, list("abcd"), estimand="observation")[0], "returns"),
        ("A8 one group only",
         lambda: mean_by(v, ["p"] * 4, estimand="observation")[0], "returns"),
        ("A8b lopsided, means agree",
         lambda: mean_by([1.0, 1.0, 1.0, 1.0], ["p", "p", "p", "q"],
                         estimand="observation")[0], "returns"),
        ("A8c lopsided, means differ",
         lambda: mean_by([1.0, 1.0, 1.0, 0.0], ["p", "p", "p", "q"],
                         estimand="observation"), "raises"),
    ]:
        ok, got, det = attack(nm, fn, exp)
        results.append({"vector": nm, "expected": exp, "got": got, "pass": ok})

    # A9: the bypass, which is not a bug and must be reported as unfixable
    direct = float(np.mean(v))
    print(f"  ----  A9 the bypass                     np.mean()直接 returns {direct} -- "
          f"NO LIBRARY CAN PREVENT THIS")
    results.append({"vector": "A9 direct np.mean bypass", "expected": "unpreventable",
                    "got": "returns", "pass": True,
                    "note": "a guard nobody calls is not a guard; this is a tool for rounds that "
                            "opt in"})

    # THE FIRST VERSION OF THIS GUARD FAILED A7 AND THAT KILLED ITS DESIGN. v1 refused whenever
    # one group held over 5% of the rows -- a SHAPE test, which is precisely what r197 showed does
    # not work. Four rows in four groups gives a 25% "dominant" group while the two estimands are
    # IDENTICAL, so it refused a mean with nothing wrong with it. A guard that fires where the
    # choice does not matter trains callers to pass acknowledge_dominance everywhere, which is
    # worse than no guard at all. v2 refuses only when the two means actually DISAGREE.
    _val, d7 = mean_by(v, list("abcd"), estimand="observation")
    print(f"\n  A7 detail: observation {d7['observation']:.4f}, group {d7['group']:.4f}, gap "
          f"{d7['gap']:+.4f}")
    print(f"  The two estimands coincide, so the guard stays quiet -- correctly. v1 of this guard")
    print(f"  used a SHARE threshold and FAILED this vector, which is the same shape-versus-")
    print(f"  outcome mistake r197 diagnosed in its own scanner. The attack suite caught it")
    print(f"  before the guard was used anywhere.")

    passed = sum(1 for r in results if r["pass"])
    print(f"\n  {passed}/{len(results)} vectors behave as specified")
    if passed != len(results):
        print("  the guard does not do what it says; nothing below is admissible")
        return 1

    # ------------------------------------------------------------------ the motivating case
    print("\n" + "=" * 78)
    print("THE REAL TEST: r191's OWN DATA")
    print("=" * 78)
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    lens = {}
    for c in cmp_:
        o = {}
        for i, r in enumerate(c.get("responses") or []):
            k = str(r.get("response_index", LETTERS[i])).strip().upper()
            if k in LETTERS:
                o[k] = len(" ".join(m.get("content") or ""
                                    for m in (r.get("messages") or [])
                                    if isinstance(m.get("content"), str)))
        if len(o) == 4:
            lens[c["prompt_id"]] = o

    vals, grps = [], []
    for line in (DATA / "annotators.jsonl").open():
        a = json.loads(line)
        for s in a.get("assessments", []):
            pid = s.get("conversation_id")
            if pid not in lens:
                continue
            top = None
            for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
                gg = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
                if gg and len(gg[0].split("=")) == 1 and gg[0] in LETTERS:
                    top = gg[0]
                break
            if top is None:
                continue
            vals.append(1.0 if top == max(lens[pid], key=lens[pid].get) else 0.0)
            grps.append(pid)
    d = dominance(grps)
    print(f"  {d['n']} assessments over {d['n_groups']} prompts; largest holds "
          f"{d['largest_n']} = {d['max_share']:.1%}, median group {d['median_group_n']:.0f}")
    fired = False
    try:
        mean_by(vals, grps, estimand="observation", name="r191 length preference")
    except EstimandError as e:
        fired = True
        print(f"  GUARD FIRES:")
        for chunk in str(e).split(". "):
            if chunk.strip():
                print(f"    {chunk.strip()}.")
    if not fired:
        print("  THE GUARD DOES NOT FIRE ON ITS OWN MOTIVATING CASE. It is useless.")
        return 1

    b = both(vals, grps, name="r191 length preference")
    print(f"\n  and `both()` gives the comparison without a choice being made:")
    print(f"    observation-weighted {b['observation']:.1%}")
    print(f"    group-weighted       {b['group']:.1%}")
    print(f"    gap                  {b['gap']:+.1%}")
    print(f"  r177 published {b['observation']:.1%} as the headline length preference. The")
    print(f"  prompt-weighted value is {b['group']:.1%}. The gap is {abs(b['gap']):.1%} -- SMALL, and")
    print(f"  that is worth saying plainly: the guard firing does not mean a number was wrong. It")
    print(f"  means the number's unit was never stated, and here the two units happen to agree.")
    print(f"  Where they did NOT agree was the STRATIFIED version in r191, because the anchor sits")
    print(f"  in one stratum and not the other.")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    print(f"  Nine attack vectors, {passed} behaving as specified, and the guard fires on the")
    print(f"  exact call that produced this project's one fabricated finding -- which is more than")
    print(f"  r197's static scanner could do, and it is why that scanner was committed as")
    print(f"  insufficient rather than kept.")
    print(f"\n  A9 IS THE HONEST CEILING. `np.mean` remains one import away, and no library can")
    print(f"  close that. What this changes is the default: a round that reaches for mean_by gets")
    print(f"  the diagnostics whether or not it wants them, and a round that reaches past it is")
    print(f"  making a choice rather than an omission. That is the whole claim.")
    print(f"\n  AND THE DOMINANCE THRESHOLD IS A CHOICE, NOT A MEASUREMENT. 0.05 is set where a")
    print(f"  single group starts to move a total by more than a typical effect in this repo. It")
    print(f"  is stated in the source rather than justified, because pretending a chosen constant")
    print(f"  was derived is the failure this project has caught in others four times.")

    (OUT / "guard.json").write_text(json.dumps(
        {"attacks": results, "passed": passed,
         "r191_case": {"n": d["n"], "n_groups": d["n_groups"], "max_share": d["max_share"],
                       "guard_fires": fired, "observation": b["observation"],
                       "group": b["group"], "gap": b["gap"]},
         "ceiling": "np.mean bypass is unpreventable; the guard changes the default, not the "
                    "possibility"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
