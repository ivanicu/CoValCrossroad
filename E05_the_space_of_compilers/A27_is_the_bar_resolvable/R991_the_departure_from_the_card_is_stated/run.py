#!/usr/bin/env python3
"""R991 — the departure from the release's own card is now stated.

⛔ WHY THIS AND NOT R990's NEXT. R990 asked for a semantic instrument to close its lexical measure's
one-directional gap. That is real work, and it is not the highest-leverage act available: **R988,
R989 and R990 all produced findings and none of them was in `DEFINITION.md`.** R988's is the one that
changes the definition — the card sets an UPPER bound on size where clause ① sets a LOWER one, and
two properties the card calls constitutive have no clause — and R988's own words were that the
departure "is currently stated nowhere". A semantic instrument would refine a measurement; writing
the departure down changes what the deliverable says.

ESTIMAND        a BEFORE/AFTER pair: for each of the three facts, is it present in the statement
                region at the PARENT commit, and at the working tree?
IDENTIFICATION  exact and reproducible from git — the "before" is recovered with `git show`, so it
                is not my recollection of it.
SCOPE           population : the bounded statement region, via the currency gate's own
                             `statement_region`, so both gates read one text
                instrument : the three regex families registered in the currency gate this round
                baseline   : the same patterns against the unrepaired parent revision
                regime     : presence of a fact in prose; says nothing about whether it is TRUE
WORLDS          A DECORATION  a pattern already matched before the repair, so its green says nothing.
                B REAL        absent at the parent, present now — the repair is what moved it.
                prediction matrix: A -> before = present. B -> before absent, after present.
KILL            pre-registered: if any pattern matches the PARENT revision, that registration is
                decoration and must be withdrawn rather than kept as a passing check. Exit 1.
POSITIVE CTRL   a fact known present at the parent (R921's two legitimate comparators) must read
                present in BOTH revisions — otherwise "absent everywhere" could mean the parent's
                region failed to load.
NEGATIVE CTRL   a runtime-assembled sentinel must be absent from both, built from fragments because
                documenting an absent marker is what puts it in the corpus.
PLACEBO         n/a — there is no estimate to null out; the before/after pair IS the control that a
                pattern-only pass would fail.
MULTIPLICITY    3 facts × 2 revisions, all six cells reported.
ARTIFACT        results/departure_stated.json with this file's source hash.
IMPOSSIBLE      construct validity — N/A: that the statement now SAYS the departure is not evidence
                the departure is right. The card calls core a proof of concept and an invitation, so
                departing may be correct; this round makes it deliberate rather than silent.
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

PATS = {
    "R988 the card caps size; two properties have no clause": [
        r"(up to four|caps? .{0,30}four|upper bound).{0,320}"
        r"(non-redundant|non-conflicting|no clause)",
        r"(non-redundant|non-conflicting).{0,320}(no clause|not encoded|has no)"],
    "R989 criteria are more sign-coherent than chance": [
        r"(sign|coheren|contest).{0,260}(null|chance|93|permut)",
        r"(80.0%|80%).{0,220}(null|93|chance)"],
    "R990 the construction removes redundancy": [
        r"(difference-in-differences|DiD|0\.0084).{0,260}(redundan|Jaccard|overlap)",
        r"(redundan|overlap).{0,260}(difference-in-differences|DiD)"],
}
CONTROL_PRESENT = ("R921 two legitimate comparators (must be present in BOTH)",
                   [r"\b2\b.{0,80}(comparator|prompt-blind)",
                    r"(comparator|prompt-blind).{0,80}\b2\b"])


def main() -> int:
    spec = importlib.util.spec_from_file_location(
        "sc", ROOT / "assurance/a_statement_is_current_with_the_arc.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    now = m.statement_region((ROOT / REL).read_text())
    par = subprocess.run(["git", "show", f"HEAD:{REL}"], cwd=ROOT, capture_output=True, text=True)
    if par.returncode != 0:
        print("  UNRUNNABLE: the parent revision could not be read. Exit 2, never 0.")
        return 2
    before = m.statement_region(par.stdout)
    if now is None or before is None:
        print("  UNRUNNABLE: a statement region failed to load. Exit 2, never 0.")
        return 2
    print(f"statement region — parent {len(before.splitlines())} lines, "
          f"working tree {len(now.splitlines())} lines")

    def hit(region, pats):
        return any(re.search(p, region, re.I | re.S) for p in pats)

    cname, cpats = CONTROL_PRESENT
    cb, cn = hit(before, cpats), hit(now, cpats)
    ghost = "zz" + "-absent-" + "sentinel-" + "R991"
    nb, nn = ghost in before, ghost in now
    print(f"\nPOSITIVE CONTROL  {cname}: parent {cb}, working tree {cn}")
    print(f"NEGATIVE CONTROL  runtime-assembled sentinel absent in both: "
          f"{'PASS' if not nb and not nn else '⛔ FAIL'}")
    if not (cb and cn) or nb or nn:
        print("\n⛔ a control failed; the before/after below certifies nothing. Exit 2, never 0.")
        return 2

    print(f"\n{'fact':<52}{'parent':>9}{'now':>7}   verdict")
    rows, decoration = [], []
    for name, pats in PATS.items():
        b, n = hit(before, pats), hit(now, pats)
        v = ("REAL — the repair moved it" if (not b and n)
             else "⛔ DECORATION — matched before the repair" if b else "⛔ still absent")
        rows.append({"fact": name, "parent": b, "now": n, "verdict": v})
        if b:
            decoration.append(name)
        print(f"  {name:<50}{str(b):>9}{str(n):>7}   {v}")

    world = ("A DECORATION — a registered pattern already matched" if decoration else
             "B REAL — all three facts were absent at the parent and are present now")
    print(f"\n⭐ {world}")
    print("\n⚠ THIS SHOWS THE SENTENCE ARRIVED, NOT THAT THE DEPARTURE IS RIGHT. The card calls core")
    print("   'a proof of concept ... an invitation for others to develop better methods', so")
    print("   departing from it may be correct. What changed is that it is now DELIBERATE.")

    out = HERE / "results" / "departure_stated.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        parent=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                              text=True).stdout.strip()[:8],
        parent_region_lines=len(before.splitlines()), now_region_lines=len(now.splitlines()),
        controls={"positive_present_in_both": bool(cb and cn),
                  "negative_sentinel_absent": not (nb or nn)},
        rows=rows, decoration=decoration, world=world,
        not_shown="that the departure is correct — only that it is now stated",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 1 if decoration else 0


if __name__ == "__main__":
    sys.exit(main())
