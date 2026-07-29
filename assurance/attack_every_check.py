"""Plant the defect each check hunts, and require the check to FIRE.

Entry 124 established the rule for one instrument: *a matcher's silence is
evidence only if the matcher would usually speak.* This applies it to the rest of
the suite.

WHAT WAS ALREADY COVERED, AND WHAT WAS NOT
------------------------------------------
* `attack_the_suite.py` empties each check's INPUT and requires exit 2 -- the
  nothing-to-hunt-in axis, where entry 64 found five checks failing.
* `attack_no_withdrawn_framings.py`, `attack_outcome_variable_declared.py` and
  `attack_scope_reaches_the_reader.py` inject the specific defect for their own
  three checks.

That left eight checks green with no demonstration they can fire at all.

TWO THINGS THIS SCRIPT LEARNED ABOUT ITSELF, WHICH ARE THE POINT
----------------------------------------------------------------
Its first version reported **three of six checks as never firing**. All three
were **bad plants**, not broken checks:

1. `code_states_a_bound...` -- the planted "unstated bound" used the words
   *donor, permutation, separate, uniform, contribution, absent*, which occur in
   README 28, 7, 16, 5, 7 and 6 times. The bound DID reach the reader, so the
   check was right to stay silent.
2. `readme_row_carries_the_verdict` -- the plant stripped the first table row
   containing a warning glyph, which was the **layer table's**, not a round's.
   The check maps rounds to rows by link and never tracked it.
3. `results_match_their_code` -- it DID detect the planted round and named it in
   stdout. It exits 0 **by design**: *"Not a gate. A round can legitimately be
   edited without re-running, and making this fail a build would push those edits
   toward not being made at all."* The harness had assumed a uniform exit
   contract.

So the first version manufactured three false accusations -- the mirror of a
false acquittal, and as damaging. Two fixes follow from that, and they are why
this file is worth keeping:

* **every plant SELF-VALIDATES**: it asserts the planted state actually differs
  in the way the target check cares about, before the check is ever run. A plant
  that cannot show it planted anything reports PLANT INVALID, never "check
  broken".
* **each check declares its CONTRACT**: `gate` (non-zero exit) or `report`
  (exit 0 by design; must NAME the planted item in stdout when planted and not
  when clean). Assuming one contract for a suite that has two is how a working
  check gets called broken.

WHAT THIS DOES NOT ESTABLISH
----------------------------
That a check catches every instance of its defect -- only the one planted. That
is recall, and it is unmeasured. What is answered is the prior question, which
had no answer at all: does this check ever say no?
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable
README = ROOT / "README.md"
R72 = ROOT / "rounds/r72_proxy_validity_coefficient/results/r72_proxy_validity_coefficient.json"


def run(check: str, cwd: Path = ROOT):
    p = subprocess.run([PY, f"assurance/{check}.py"], cwd=cwd,
                       capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr


def verify(name, contract, rc_bad, out_bad, rc_good, out_good, token, why):
    """One place where 'fired' is defined, per contract."""
    if contract == "gate":
        if rc_bad == 0:
            return name, False, f"DID NOT FIRE on {why} (exit 0)"
        if rc_good != 0:
            return name, False, f"fires on the CLEAN tree too (exit {rc_good}) -- not specific"
        return name, True, f"exit {rc_bad} on {why}; clean after restore"
    named_bad, named_good = token in out_bad, token in out_good
    if not named_bad:
        return name, False, f"DID NOT NAME the planted item on {why}"
    if named_good:
        # Measured: this check names 71 of 72 rounds on a clean tree. A report
        # whose population is saturated cannot signal anything by naming one more
        # -- the same shape as a 94% chance-match rate (entry 124).
        return name, False, (f"SATURATED -- names {token} on the CLEAN tree too; "
                             f"no plant is detectable against that background")
    return name, True, f"named {token} on {why} (report contract: exit 0 by design)"


def readme_plant(name, contract, mutate, why, token="", validate=None):
    original = README.read_text()
    try:
        planted = mutate(original)
        if planted == original:
            return name, None, "PLANT INVALID -- the mutation changed nothing"
        if validate is not None:
            bad = validate(planted)
            if bad:
                return name, None, f"PLANT INVALID -- {bad}"
        README.write_text(planted)
        rc_bad, out_bad = run(name)
        README.write_text(original)
        rc_good, out_good = run(name)
        return verify(name, contract, rc_bad, out_bad, rc_good, out_good, token, why)
    finally:
        README.write_text(original)


def drop_round_link(text):
    return text.replace("rounds/r72_proxy_validity_coefficient", "rounds/_no_such_round")


def insert_retired_framing(text):
    i = text.index("\n## ")
    return text[:i] + "\n\n## The share that measures values\n" + text[i:]


def insert_superseded_number(text):
    i = text.index("\n## ")
    return text[:i] + "\n\nThe fresh arm falls +0.102 → −0.042 on generated responses.\n" + text[i:]


def bound_plant():
    """A bound in a round's SOURCE whose words genuinely do NOT reach the reader.

    The first version planted vocabulary the README already used many times over,
    then blamed the check for staying silent. The plant now proves its own
    premise before running anything.
    """
    name = "code_states_a_bound_the_reader_never_sees"
    words = ["kurtosis", "heteroskedastic", "monotonic", "isotonic"]
    readme = README.read_text().lower()
    present = [w for w in words if w in readme]
    if present:
        return name, None, f"PLANT INVALID -- README already contains {present}"
    target = ROOT / "rounds/r72_proxy_validity_coefficient/run.py"
    original = target.read_text()
    try:
        target.write_text(original + "\n# This estimator cannot distinguish a heteroskedastic"
                                     " kurtosis shift from an isotonic monotonic drift.\n")
        rc_bad, out_bad = run(name)
        target.write_text(original)
        rc_good, out_good = run(name)
        return verify(name, "gate", rc_bad, out_bad, rc_good, out_good, "",
                      "a source bound whose words appear nowhere in README")
    finally:
        target.write_text(original)


def verdict_limitation_plant():
    """A round's verdict gains a limitation its README row does not carry."""
    name = "readme_row_carries_the_verdict"
    original = R72.read_text()
    doc = json.loads(original)
    # The trailing clause "and no isotonic control was run" was REMOVED after it
    # silently disarmed this plant: the check scores VOCABULARY OVERLAP between
    # the limitation sentence and the README row, and words like `control` and
    # `run` already appear there, pushing the overlap over threshold so the row
    # counted as carrying a limitation it does not carry. Adding words to a plant
    # can WEAKEN it -- the plant must be as lexically foreign as the defect is.
    sentence = (" The criterion-space kurtosis pathway is NOT ESTABLISHED for the "
                "heteroskedastic arm.")
    if "kurtosis" in README.read_text().lower():
        return name, None, "PLANT INVALID -- README already carries the planted vocabulary"
    try:
        doc["verdict"] = doc["verdict"] + sentence
        R72.write_text(json.dumps(doc, indent=1))
        rc_bad, out_bad = run(name)
        R72.write_text(original)
        rc_good, out_good = run(name)
        return verify(name, "gate", rc_bad, out_bad, rc_good, out_good, "",
                      "a verdict limitation absent from the round's README row")
    finally:
        R72.write_text(original)


def clone_plant():
    """Code committed after its results -- only expressible in git history.

    REPORT contract: this check deliberately exits 0. Its own words: "Not a gate.
    A round can legitimately be edited without re-running." So firing means
    NAMING the round, not failing the build.
    """
    name = "results_match_their_code"
    # r72 is already named on the clean tree, so planting there proves nothing.
    token = "r70_outcome_criterion_axis"
    tmp = Path(tempfile.mkdtemp(prefix="attack_every_"))
    try:
        subprocess.run(["git", "clone", "-q", str(ROOT), str(tmp / "c")],
                       capture_output=True, check=True)
        c = tmp / "c"
        rc_good, out_good = run(name, c)
        rp = c / "rounds/r70_outcome_criterion_axis/run.py"
        rp.write_text(rp.read_text() + "\n# planted: code newer than its results\n")
        subprocess.run(["git", "-c", "user.name=a", "-c", "user.email=a@b",
                        "commit", "-q", "--no-verify", "-am", "plant"],
                       cwd=c, capture_output=True)
        rc_bad, out_bad = run(name, c)
        return verify(name, "report", rc_bad, out_bad, rc_good, out_good, token,
                      "code committed after its results")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    results = [
        readme_plant("every_round_reaches_the_readme", "gate", drop_round_link,
                     "a round no document mentions"),
        readme_plant("retired_framing_in_assertion_positions", "gate",
                     insert_retired_framing, "a withdrawn framing in a heading"),
        readme_plant("corrections_propagated", "gate", insert_superseded_number,
                     "a superseded number reinstated"),
        bound_plant(),
        verdict_limitation_plant(),
        clone_plant(),
    ]
    print(f"{'check':44s} {'fired?':>8}  detail")
    for name, ok, detail in results:
        tag = "INVALID" if ok is None else ("YES" if ok else "NO")
        print(f"{name:44s} {tag:>8}  {detail}")

    dirty = subprocess.run(["git", "diff", "--quiet"], cwd=ROOT).returncode
    print(f"\nrestore verification: working tree {'CLEAN' if dirty == 0 else 'DIRTY'}")
    if dirty != 0:
        print("  A plant survived the restore. That is worse than any check tested here.")
        return 2

    fired = [n for n, ok, _ in results if ok is True]
    silent = [n for n, ok, _ in results if ok is False]
    invalid = [n for n, ok, _ in results if ok is None]
    print(f"\n{len(fired)} of {len(results)} checks demonstrably fire on the defect they hunt.")
    if invalid:
        print(f"  PLANT INVALID (says nothing about the check): {', '.join(invalid)}")
    if silent:
        print(f"  NEVER FIRED: {', '.join(silent)}")
        print("  A check that has never said no is silent, not passing.")
    print("\nNOT established: that a check catches EVERY instance of its defect. That is")
    print("recall, and it is unmeasured. What is established is that these checks can say")
    print("no at all -- which before this script had no evidence either way.")
    return 1 if silent else 0


if __name__ == "__main__":
    sys.exit(main())
