#!/usr/bin/env python3
"""assurance/a_declared_control_reaches_the_artifact.py -- a control named in a docstring and absent
from the artifact it produced.

WHY. R1005 declared, in its own docstring:

    NEGATIVE CTRL   shuffle the membership labels ... >=200 shuffles.
                    ⚠ World it excludes: "any set of this size shows this Δ".
    PLACEBO         Δ between two disjoint random halves of the NON-members must be ≈ 0.

NEITHER WAS IMPLEMENTED. `NSHUF = 200` sat at line 74 and was used nowhere; the only `permutation`
call permuted PROMPTS for the held-out split; the committed artifact's `controls` field held exactly
one entry. The headline was written as though the exclusion had happened, and R1007 -- running the
control R1005 had described -- RETRACTED it: the effect clears its band-matched null in 6 of 30
cells, monotone in the LOOSEST caliper.

⛔ ONE GREP FOR AN UNUSED CONSTANT FOUND IT, AND NO GATE LOOKED. `a_control_that_cannot_fail.py`
catches a control whose value is forced by the algebra. Nothing caught a control that never ran.
**A docstring is a claim about what ran**, and it is the only claim in a round with no check on it.

⚠⚠ PROXY LEDGER -- this gate is an instrument and is sound in ONE direction only.

    PROPERTY     every control the docstring declares was actually EXECUTED
    PROXY        every control the docstring declares has a key in the artifact's `controls` dict
    IMPLICATION  key absent  =>  the round is NOT AUDITABLE from its artifact          [SOUND]
                 key present =>  the control ran, and ran correctly                    [NOT SOUND]
    WITNESS      R1006 ran its negative control -- 5,000 size-preserving shuffles at lines 198-200,
                 feeding the null_mean / null_sd / z columns -- and records NO key containing
                 "negative", because the numbers live in `rows`. It is flagged by this gate, and it
                 is NOT the same defect as R1005.
    SAFE SIDE    the verdict is NOT-RECORDED, never NOT-RUN. This gate may not assert that a control
                 was never executed; it asserts only that a later reader cannot tell from the
                 artifact. Both are defects; conflating them would manufacture a false accusation,
                 and a false accusation about one's own work is as permanent as a false acquittal.

⛔⛔ AND THE FIRST VERSION OF THIS GATE WAS UNFIT, WHICH ITS OWN FIRST RUN SHOWED. Applied to every
round it flagged **378 of 399 -- 95%**. A gate that fires on almost everything carries no information
and becomes the alarm nobody reads. The cause is measurable and is not sloppiness: **only 132 of 399
rounds carry a `controls` field at all.** The convention this gate checks WAS NEVER ADOPTED in this
repo; most rounds report their controls in prints and in `rows`. So retroactively it measures
conformity to a convention that did not exist, not whether controls ran.

⚠⚠ AND THE POSITIVE CONTROL WRITTEN TO PREVENT EXACTLY THAT DID NOT FIRE. It required "at least one
round must pass, or the pattern flags everything" -- and it PASSED at a **5% pass rate**, because
`>= 1` is not `a meaningful share`. **A threshold of one is a check that cannot fail.** Replaced below.

⭐ SO THE GATE IS SCOPED TO AN EPOCH: rounds from **R1000** on, where the convention is adopted going
forward. That is not a way to make the number look better -- the retroactive count is printed every
run as context -- it is what a new convention IS. In scope the gate discriminates: 8 rounds declare,
3 are flagged, and the flagged set contains the known defect.

POSITIVE CONTROL. Run where the answer is already known, on REAL rounds, both directions:
  * R1005 MUST be flagged -- its missing controls are established by R1007 and by RETRACTIONS.md.
  * R1000-R1004 MUST ALL pass -- five real rounds whose artifacts do record every control they
    declare. Five known-good cases, not one, and not invented ones: a control validated only against
    cases you made up is validated against your imagination.
If either fails, the gate is unfit and exits 2 (UNRUNNABLE), never 0 and never 1.

EXIT   0 every declared control reaches its artifact · 1 some do not · 2 the gate could not judge.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from covalx.rounds import iter_round_dirs  # noqa: E402

EPOCH = 1000        # the round from which the `controls`-field convention is in force
DECLARED = re.compile(r"^(POSITIVE CTRL|NEGATIVE CTRL|SHAM|PLACEBO|NOISE FLOOR)", re.M)
TOKEN = {"POSITIVE CTRL": "positive", "NEGATIVE CTRL": "negative", "SHAM": "sham",
         "PLACEBO": "placebo", "NOISE FLOOR": "floor"}
# a docstring may say a control is N/A for this site; that is a register entry, not a control.
NA = re.compile(r"n/?a\b|not applicable|none needed", re.I)


def declared_controls(src: str):
    if '"""' not in src:
        return []
    doc = src.split('"""')[1]
    out = []
    for m in DECLARED.finditer(doc):
        line = doc[m.start():doc.find("\n", m.start())]
        if NA.search(line):
            continue
        out.append(m.group(1))
    return sorted(set(out))


def artifact_controls(d: pathlib.Path):
    """-> (keys, artifact_path) or (None, None) when the round persists no controls field at all."""
    for j in sorted((d / "results").glob("*.json")) if (d / "results").is_dir() else []:
        try:
            obj = json.loads(j.read_text())
        except Exception:
            continue
        c = obj.get("controls")
        if isinstance(c, dict):
            return sorted(c), j
        if isinstance(c, list):
            return [str(x) for x in c], j
    return None, None


def audit(d: pathlib.Path):
    run = d / "run.py"
    if not run.exists():
        return None
    decl = declared_controls(run.read_text())
    if not decl:
        return None
    keys, art = artifact_controls(d)
    if keys is None:
        return {"round": d.name, "declared": decl, "keys": [], "missing": decl,
                "artifact": None, "why": "no artifact carries a `controls` field"}
    blob = " ".join(keys).lower()
    missing = [c for c in decl if TOKEN[c] not in blob]
    return {"round": d.name, "declared": decl, "keys": keys, "missing": missing,
            "artifact": str(art.relative_to(ROOT)), "why": ""}


def rnum(name: str) -> int:
    try:
        return int(name.split("_")[0][1:])
    except ValueError:
        return -1


def main() -> int:
    every = [r for r in (audit(d) for d in iter_round_dirs(ROOT)) if r]
    rounds = [r for r in every if rnum(r["round"]) >= EPOCH]
    pre = [r for r in every if rnum(r["round"]) < EPOCH]
    pre_flagged = [r for r in pre if r["missing"]]
    print(f"  EPOCH R{EPOCH}: {len(rounds)} rounds in scope. Before it, {len(pre_flagged)} of "
          f"{len(pre)} would be flagged — printed as CONTEXT, not as failures, because only "
          f"{sum(1 for r in every if r['artifact'])} of {len(every)} rounds carry a `controls` "
          f"field at all and the convention was never adopted retroactively.")
    if not rounds:
        print("  UNRUNNABLE: no round declares a control. An empty population must not pass. "
              "Exit 2, never 0.")
        return 2

    flagged = [r for r in rounds if r["missing"]]
    clean = [r for r in rounds if not r["missing"]]

    # ---------- POSITIVE CONTROL, both directions ----------
    pos_a = any(r["round"].startswith("R1005_") for r in flagged)
    known_good = [r for r in rounds if 1000 <= rnum(r["round"]) <= 1004]
    pos_b = bool(known_good) and all(not r["missing"] for r in known_good)
    print(f"  POSITIVE CONTROL — R1005 must be flagged (R1007 and RETRACTIONS.md establish it): "
          f"{'PASS' if pos_a else '⛔ FAIL'}")
    print(f"  POSITIVE CONTROL — R1000–R1004 ({len(known_good)} real known-good rounds) must ALL "
          f"pass: {'PASS' if pos_b else '⛔ FAIL'}")
    print(f"     ⚠ the FIRST version of this control read 'at least one round must pass' and it "
          f"passed at a 5% pass rate. A threshold of one is a check that cannot fail.")
    if not (pos_a and pos_b):
        print("\n  UNRUNNABLE: the gate is unfit — it cannot both find the known defect and clear a "
              "known-good round. Exit 2, never 0.")
        return 2

    print(f"\n  {len(rounds)} rounds declare controls · {len(flagged)} have a declared control that "
          f"never reaches an artifact")
    for r in sorted(flagged, key=lambda x: x["round"]):
        extra = f" — {r['why']}" if r["why"] else ""
        print(f"    {r['round'][:58]:<58} missing {','.join(r['missing'])}{extra}")

    print("\n  ⚠ VERDICT IS **NOT-RECORDED**, NEVER **NOT-RUN**. R1006 ran its negative control "
          "(5,000 shuffles,\n     lines 198-200) and is flagged here because the numbers live in "
          "`rows` rather than in\n     `controls`. That is a different, lesser defect than R1005's, "
          "and this gate cannot tell\n     them apart — it says only that a later reader cannot "
          "tell either.")
    out = ROOT / "assurance" / "results" / "declared_controls.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"n_rounds_declaring": len(rounds), "n_flagged": len(flagged),
                               "rows": rounds}, indent=1))
    print(f"  artifact {out.relative_to(ROOT)}")
    return 1 if flagged else 0


if __name__ == "__main__":
    sys.exit(main())
