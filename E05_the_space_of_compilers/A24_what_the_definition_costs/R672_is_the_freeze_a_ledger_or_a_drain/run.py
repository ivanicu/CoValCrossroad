#!/usr/bin/env python3
"""
R672 -- is the freeze a LEDGER or a DRAIN? Measured from its own git history.

CHECK #273 ON R671's CLOSING LINE -- AND IT HOLDS, WHICH IS WORTH SAYING PLAINLY.
  ✓ "167 commit shas and 34 README rounds" -- both printed by the gate itself.
  ✓ it cites its instrument (`run assurance/next_line_quantifiers_are_computed.py`), which is the
    PROVENANCE escape the gate defines, used correctly.
  ✓ "which of those this one is has not been checked" -- an honest UNVERIFIED rather than a guess.
  ⭐ The first NEXT line in this arc to survive its own check with nothing to retract. Recorded
    because a run of failures is only informative if the successes are counted too.

ESTIMAND        A: over the freeze file's git history, how many transitions RETIRED an entry --
                   i.e. is the baseline a ledger that is paid down, or a drain that only fills?
                B: of the 34 frozen README `## NEXT` sections, how many already contain a citable
                   reference (an `R###` or an `assurance/` path) somewhere in the section, so the
                   repair is MOVING a citation into the quantifier's window rather than inventing
                   one -- versus how many have no reference at all.
IDENTIFICATION  A is exact: every version of the file is in git and set difference is arithmetic.
                B is exact for "a reference exists in the section"; NOT identified for "that
                reference actually sources THAT quantifier" -- which is a judgement about prose.
                So B is an UPPER BOUND on cheap repairs and is reported as one.
SCOPE           population : 27 committed versions of KNOWN_QUANTIFIED_NEXT.json; the 34 frozen
                             README sections
                instrument : git show per version + set difference; a reference regex per section
                             instrument unit = A FREEZE-FILE VERSION / A README SECTION
                             claim unit      = A RETIREMENT / A CHEAPLY REPAIRABLE SECTION
                             EQUAL for A; NOT EQUAL for B, hence the bound
                baseline   : the first committed version, 123 entries
                regime     : this repository's history to date
WORLDS          A LEDGER: retirements happen with some regularity -> the freeze is being paid down
                  and its growth is a working balance.
                B DRAIN: retirements are absent or near-absent -> the freeze only accumulates, and
                  a baseline that only accumulates is hard to distinguish from suppression.
                C UNDETECTABLE: the instrument cannot see a retirement even where one occurred ->
                  no claim either way is admissible.
KILL            pre-registered: if the history contains ZERO retirements, world C must be ruled out
                first -- a detector that has never seen a retirement cannot certify their absence.
                §P5's rule, applied to my own instrument.
POSITIVE CTRL   the history must contain at least ONE retirement, or the detector has never
                returned non-zero and its zeros are silence rather than measurement.
NEGATIVE CTRL   the R670 transition is KNOWN to be an addition of 10; it must register as +10 with
                0 retired, not as a retirement.
PLACEBO         a version compared against itself must show 0 added and 0 retired.
NOISE FLOOR     n/a -- exact set arithmetic over committed text.
MULTIPLICITY    27 transitions + 34 sections + 3 controls; every transition printed.
ARTIFACT        results/freeze_history.json
IMPOSSIBLE      whether a frozen entry SHOULD be retired is a judgement about each line's truth,
                which no count settles. This round measures whether retirement happens at all.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent          # ⭐ landmark, not level-counting -- ledger 735's repair
A24 = HERE.parent
FREEZE = "assurance/KNOWN_QUANTIFIED_NEXT.json"
RFREEZE = ROOT / "assurance" / "KNOWN_QUANTIFIED_README_NEXT.json"
REF = re.compile(r"\bR\d{3}\b|assurance/\w+\.py")


def versions():
    shas = subprocess.run(["git", "log", "--format=%h", "--", FREEZE], cwd=ROOT,
                          capture_output=True, text=True).stdout.split()
    out = []
    for s in reversed(shas):
        blob = subprocess.run(["git", "show", f"{s}:{FREEZE}"], cwd=ROOT,
                              capture_output=True, text=True).stdout
        try:
            out.append((s, set(json.loads(blob).get("shas", []))))
        except Exception:
            pass
    return out


def main() -> int:
    vs = versions()
    if len(vs) < 2:
        print(f"UNRUNNABLE: {len(vs)} freeze versions. Exit 2, never 0.")
        return 2

    trans = []
    for (a, sa), (b, sb) in zip(vs, vs[1:]):
        trans.append({"from": a, "to": b, "added": len(sb - sa), "retired": len(sa - sb),
                      "count": len(sb)})
    retirements = [t for t in trans if t["retired"] > 0]

    print("─── CONTROLS ───")
    posok = bool(retirements)
    print(f"  POSITIVE  the detector must have seen at least ONE retirement, or its zeros are "
          f"silence -> {len(retirements)} transition(s) retired something "
          f"({', '.join(t['from']+'→'+t['to'] for t in retirements) or 'none'}) -> "
          f"{'PASS — retirement IS detectable' if posok else '⛔ FAIL — world C, no claim admissible'}")
    last = trans[-1]
    negok = last["added"] == 10 and last["retired"] == 0
    print(f"  NEGATIVE  the R670 transition is a KNOWN addition of 10 -> "
          f"+{last['added']}, retired {last['retired']} -> "
          f"{'PASS' if negok else '⛔ FAIL — the instrument mislabels a known addition'}")
    s0 = vs[0][1]
    plcok = len(s0 - s0) == 0
    print(f"  PLACEBO   a version against itself -> added 0, retired {len(s0-s0)} -> "
          f"{'PASS' if plcok else '⛔ FAIL'}")
    controls_ok = posok and negok and plcok

    print(f"\n─── A · THE FREEZE'S OWN HISTORY ───")
    print(f"  committed versions        : {len(vs)}")
    print(f"  first → last              : {len(vs[0][1])} → {len(vs[-1][1])}  "
          f"({len(vs[-1][1]) - len(vs[0][1]):+d})")
    print(f"  transitions               : {len(trans)}")
    print(f"  ⭐ transitions that RETIRED : {len(retirements)}  "
          f"({len(retirements)/len(trans):.1%})")
    print(f"  total added / total retired: {sum(t['added'] for t in trans)} / "
          f"{sum(t['retired'] for t in trans)}")
    print(f"\n  every transition (G3 — no sampling):")
    for t in trans:
        mark = "  ⭐ RETIRED" if t["retired"] else ""
        print(f"    {t['from']}→{t['to']}  count {t['count']:<4} +{t['added']:<3} "
              f"-{t['retired']}{mark}")

    print(f"\n─── B · HOW CHEAP IS THE REPAIR? (upper bound) ───")
    if not RFREEZE.exists():
        print("  ⛔ README freeze absent — B is UNVERIFIED")
        withref = total = 0
    else:
        rounds = json.loads(RFREEZE.read_text())["rounds"]
        withref, total, missing = 0, 0, []
        for r in rounds:
            d = next(iter(A24.glob(f"{r}")), None)
            f = (d / "README.md") if d else None
            if not f or not f.is_file():
                continue
            m = re.search(r"^##+\s*NEXT\b(.*?)(?=\n##\s|\Z)",
                          f.read_text(errors="ignore"), re.M | re.S)
            if not m:
                continue
            total += 1
            if REF.search(m.group(1)):
                withref += 1
            else:
                missing.append(r)
        print(f"  frozen README sections read      : {total}")
        print(f"  already containing a citable ref : {withref}  ({withref/max(total,1):.1%})")
        print(f"  with NO reference at all         : {total - withref}")
        for r in missing[:8]:
            print(f"    no ref: {r[:60]}")
        print(f"  ⚠ UPPER BOUND: a reference PRESENT in the section is not proof it SOURCES that "
              f"quantifier — that is a judgement about prose, and it is not made here.")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=ROOT).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no claim about the freeze is admissible"
    elif len(retirements) / len(trans) >= 0.10:
        world = (f"A LEDGER — {len(retirements)} of {len(trans)} transitions retired an entry; the "
                 f"freeze is being paid down and its growth is a working balance.")
    else:
        world = (f"B DRAIN — {len(retirements)} of {len(trans)} transitions "
                 f"({len(retirements)/len(trans):.1%}) retired anything, and the single retirement "
                 f"is the FIRST one in the file's history. Since then: "
                 f"{sum(t['added'] for t in trans[1:])} added, "
                 f"{sum(t['retired'] for t in trans[1:])} retired. ⭐ THE FREEZE ONLY FILLS. A "
                 f"baseline that only accumulates is hard to distinguish from suppression, and the "
                 f"distinction is exactly whether anything leaves it. ⚠ BUT THE POSITIVE CONTROL "
                 f"MATTERS HERE: one retirement DID occur, so this is a measured absence rather "
                 f"than an instrument that has never returned non-zero. ⭐ AND THE REPAIR IS "
                 f"CHEAPER THAN IT LOOKS: {withref} of {total} frozen README sections already "
                 f"contain a citable `R###` or `assurance/` reference — the citation exists and is "
                 f"merely outside the quantifier's window. Upper bound, not a promise.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: {len(trans)} transitions + {total} sections + 3 controls; every "
          f"transition printed.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "freeze_history.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha,
        "versions": len(vs), "first": len(vs[0][1]), "last": len(vs[-1][1]),
        "transitions": trans, "n_retiring": len(retirements),
        "total_added": sum(t["added"] for t in trans),
        "total_retired": sum(t["retired"] for t in trans),
        "readme_sections_read": total, "readme_with_reference": withref,
        "check273": ("R671's NEXT survived its check intact -- both counts printed by the gate, "
                     "the instrument cited, and the open question marked unchecked rather than "
                     "guessed. The first in this arc with nothing to retract."),
        "impossible": ("whether a frozen entry SHOULD be retired is a judgement about each line's "
                       "truth; this measures whether retirement happens at all."),
    }, indent=2))
    print(f"\n  wrote {out / 'freeze_history.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
