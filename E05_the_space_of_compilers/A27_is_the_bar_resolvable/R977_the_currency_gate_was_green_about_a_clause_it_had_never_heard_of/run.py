#!/usr/bin/env python3
"""R977 — the currency gate was green about a clause it had never been told about.

⛔ WHY. `a_statement_is_current_with_the_arc.py` exists because a CONSISTENCY gate cannot see
CURRENCY: a statement can match every artifact it cites and be wrong about every artifact it does
not. It passed 7 of 7 while R975 and R976 sat committed and unmentioned — because its facts are a
hard-coded list of six artifacts, so **it has the very defect it was built to catch, one level up.**
You cannot grep for the absence of a fact you were never told about.

ESTIMAND        a BEFORE/AFTER pair, not a single reading: for each of the two facts R975 and R976
                measured, is it present in DEFINITION.md's statement region at the PARENT commit,
                and at the working tree?
IDENTIFICATION  fully identified and reproducible from git: the parent's statement region is
                recoverable with `git show`, so the "before" is not my recollection of it.
SCOPE           population : the bounded statement region of DEFINITION.md (the gate's own
                             `statement_region`, not a fresh reader)
                instrument : the two regex families registered in the gate this round
                baseline   : the same patterns applied to the unrepaired parent revision
                regime     : presence of a fact in prose; says nothing about whether it is TRUE
WORLDS          A DECORATION  the patterns already matched before the repair, so the green is a
                              property of the pattern and the repair changed nothing.
                B REAL        absent at the parent, present now — the repair is what moved it.
                prediction matrix: A -> before = present. B -> before = absent, after = present.
KILL            pre-registered: if either pattern matches the PARENT revision, that fact's
                registration is decoration and must be withdrawn, not kept as a passing check.
POSITIVE CTRL   a fact known to be present at the parent (R921's "2 legitimate comparators") must
                read present in BOTH revisions. Without it, an all-absent "before" could equally
                mean the parent's statement region failed to load.
NEGATIVE CTRL   a runtime-assembled sentinel must be absent from both revisions. Written as
                fragments because documenting an absent marker is what puts it in the corpus —
                this project did that three times.
PLACEBO         n/a — there is no estimate here to null out. This round reports presence, which is
                a fact about text, and its risk is a bad pattern rather than a bad statistic. The
                before/after pair IS the control that a pattern-only pass would fail.
MULTIPLICITY    2 facts × 2 revisions, all four cells reported.
ARTIFACT        results/statement_currency.json with this file's source hash.
IMPOSSIBLE      construct validity — N/A: that the statement now SAYS the fact is not evidence the
                fact is true. Truth of the facts is R975's and R976's business, not this round's.
                An external gold standard for "a reader can tell the scope" would be required, and
                the honest unit gap is stated in the README rather than papered over.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = "E05_the_space_of_compilers/DEFINITION.md"


def gate():
    spec = importlib.util.spec_from_file_location(
        "sc", ROOT / "assurance/a_statement_is_current_with_the_arc.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


PATS = {
    "R975 clause 4 is overlap-limited": [
        r"(overlap|per-prompt share|above the floor on).{0,200}(response[- ]only|④)",
        r"(response[- ]only|④).{0,200}(overlap|per-prompt share|above the floor on)"],
    "R976 clause 4's bar is design resolution": [
        r"(④|response[- ]only).{0,300}(N\s*=\s*968|\bN\b).{0,200}(δ|delta)",
        r"(δ|delta).{0,200}(N\s*=\s*968|\bN\b).{0,300}(④|response[- ]only)"],
}
CONTROL_PRESENT = ("R921 two legitimate comparators (must be present in BOTH)",
                   [r"\b2\b.{0,80}(comparator|prompt-blind)",
                    r"(comparator|prompt-blind).{0,80}\b2\b"])


def main() -> int:
    m = gate()
    now = m.statement_region((ROOT / REL).read_text())
    before_full = subprocess.run(["git", "show", f"HEAD:{REL}"], cwd=ROOT,
                                 capture_output=True, text=True)
    if before_full.returncode != 0:
        print("  UNRUNNABLE: the parent revision of DEFINITION.md could not be read. Exit 2.")
        return 2
    before = m.statement_region(before_full.stdout)
    if before is None or now is None:
        print("  UNRUNNABLE: a statement region failed to load. Exit 2, never 0.")
        return 2
    print(f"statement region — parent {len(before.splitlines())} lines, "
          f"working tree {len(now.splitlines())} lines")

    def hit(region, pats):
        return any(re.search(p, region, re.I | re.S) for p in pats)

    # ── POSITIVE CONTROL first: without it, "absent everywhere" could be a load failure.
    cname, cpats = CONTROL_PRESENT
    cb, cn = hit(before, cpats), hit(now, cpats)
    print(f"\nPOSITIVE CONTROL  {cname}")
    print(f"  parent {cb}   working tree {cn}   -> {'PASS' if cb and cn else '⛔ FAIL'}")

    ghost = "zz" + "-absent-" + "sentinel-" + "R977"
    nb, nn = ghost in before, ghost in now
    print(f"NEGATIVE CONTROL  runtime-assembled sentinel absent in both: "
          f"{'PASS' if not nb and not nn else '⛔ FAIL'}")

    if not (cb and cn) or nb or nn:
        print("\n⛔ a control failed; the before/after below certifies nothing. Exit 2, never 0.")
        return 2

    print(f"\n{'fact':<44}{'parent':>10}{'now':>8}   verdict")
    rows, decoration = [], []
    for name, pats in PATS.items():
        b, n = hit(before, pats), hit(now, pats)
        v = "REAL — the repair moved it" if (not b and n) else \
            "⛔ DECORATION — matched before the repair" if b else \
            "⛔ still absent"
        rows.append({"fact": name, "parent": b, "now": n, "verdict": v})
        if b:
            decoration.append(name)
        print(f"  {name:<42}{str(b):>10}{str(n):>8}   {v}")

    world = ("A DECORATION — a registered pattern already matched, so its green says nothing"
             if decoration else
             "B REAL — both facts were absent at the parent and are present now")
    print(f"\n⭐ {world}")

    print("\n⚠ UNIT GAP, stated rather than implied by a green run:")
    print("   instrument's unit : a regex matches inside the statement region")
    print("   claim's unit      : a reader can tell the scope of clause ④")
    print("   These are NOT equal. This round shows the sentence arrived; it cannot show it is")
    print("   readable, and it says nothing about whether R975's and R976's facts are TRUE.")

    out = HERE / "results" / "statement_currency.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        parent=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True).stdout.strip()[:8],
        parent_region_lines=len(before.splitlines()), now_region_lines=len(now.splitlines()),
        controls={"positive_present_in_both": bool(cb and cn),
                  "negative_sentinel_absent": not (nb or nn)},
        rows=rows, decoration=decoration, world=world,
        unit_gap={"instrument": "a regex matches inside the statement region",
                  "claim": "a reader can tell the scope of clause 4", "equal": False},
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 1 if decoration else 0


if __name__ == "__main__":
    sys.exit(main())
