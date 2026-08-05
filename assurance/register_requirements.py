#!/usr/bin/env python3
"""assurance/register_requirements.py — a register entry declares its requirement as an ENUM, not prose.

⛔ WHY, AND IT IS A CORRECTION TO THE CHECK R472 ANNOUNCED. R472 measured that 54 of 100 impossibility
   entries name no requirement, and closed proposing a gate that "a converted entry must name a
   CONCRETE ARTIFACT the next site would ship". **That gate would inherit the exact defect it exists
   to fix**: "names a concrete artifact" tested by pattern is a PHRASING test, and adding the right
   words without adding a requirement would pass it. R472's own classifier already failed that way --
   it measured phrasing and I reported it as content.

⭐ THE FIX IS THE CONSTITUTION'S OWN RULE, HB8: *if it can be an enum, it may NOT be text.* An entry
   declares `REQUIRES: <kind>` from a CLOSED SET, or declares itself `SCOPE_ONLY` or `RESTATES: R###`.
   **An enum cannot be gamed by wording** -- a wrong tag is a wrong tag, and an invented one is
   rejected by membership rather than by judgement.

THE THREE LEGITIMATE DECLARATIONS, and why the last two are not escapes:
    REQUIRES: <kind>   the entry names something the next site would SHIP. The kinds are drawn from
                       what this campaign was actually blocked on, not invented.
    SCOPE_ONLY         the entry is a scope statement mislabelled as an impossibility -- e.g. "a
                       clause that excludes the length rule: a category error, outside the domain".
                       Nothing is missing. ⚠ Declaring this is a CLAIM that nothing would lift it.
    RESTATES: R###     the entry repeats another round's limit. ⚠ The cited round must itself carry a
                       non-RESTATES declaration, so a chain of restatements cannot terminate in air.

⚠ WHAT THIS GATE CANNOT DO, stated: it checks that a DECLARATION EXISTS and is well-formed. It cannot
  check that the declaration is TRUE of the entry -- tagging a gold-standard entry `SECOND_JUDGE`
  passes. That is a different unit and would need a reader. **The enum removes the wording loophole,
  not the mislabelling one**, and saying which is which is the point of having the gate at all.
"""
from __future__ import annotations
import collections, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"

KINDS = {
    "SECOND_RELEASE",      # another corpus with the same object type
    "SECOND_JUDGE",        # a third scoring model, or a second judge PAIR
    "GOLD_STANDARD",       # an external criterion, not the release's own choice
    "GENERATOR",           # a procedure that produces candidate objects
    "MORE_ANNOTATORS",     # ⚠ already answered NO on this site (alpha = 0.208)
    "INTERVENTION",        # an operation ON the mechanism, not a re-description
    "SECOND_FAMILY",       # a second prompt-blind criterion family with breadth
    "SECOND_CORE",         # a second released core in the SAME release
    "CROSS_SPACE_KEY",     # a shipped id mapping between the release's two spaces
    "PROVENANCE_FIELD",    # how each object was built, shipped with the object
}
DECL = re.compile(r"\b(REQUIRES:\s*([A-Z_]+)|SCOPE_ONLY|RESTATES:\s*R(\d{3}))\b")


def entries():
    out = []
    for d in sorted(A24.glob("R4*")):
        f = d / "run.py"
        if not f.exists():
            continue
        m = re.search(r"IMPOSSIBLE HERE, NAMED(.*?)(?:\"\"\"|\n\nfrom |\nimport )", f.read_text(), re.S)
        if not m:
            continue
        cur = None
        for line in m.group(1).split("\n"):
            s = line.strip()
            if s.startswith("*"):
                cur = {"round": d.name[:4], "text": s.lstrip("* ").strip()}
                out.append(cur)
            elif cur and s and not s.startswith(("MULTIPLICITY", "ARTIFACT", "EXIT")):
                cur["text"] += " " + s
    return out


def classify(e):
    m = DECL.search(e["text"])
    if not m:
        return ("UNDECLARED", None)
    if m.group(2):
        return ("REQUIRES", m.group(2)) if m.group(2) in KINDS else ("BAD_KIND", m.group(2))
    if m.group(3):
        return ("RESTATES", "R" + m.group(3))
    return ("SCOPE_ONLY", None)


def selftest():
    """POSITIVE CONTROL: the gate must ACCEPT a valid tag and REJECT an invented one. A gate that
    cannot reject certifies nothing, and an enum's whole value is that rejection is mechanical."""
    ok = True
    cases = [("x REQUIRES: SECOND_JUDGE", "REQUIRES"), ("x REQUIRES: A_BETTER_VIBE", "BAD_KIND"),
             ("x SCOPE_ONLY", "SCOPE_ONLY"), ("x RESTATES: R435", "RESTATES"), ("x nothing", "UNDECLARED")]
    for txt, want in cases:
        got = classify({"text": txt})[0]
        hit = got == want
        ok &= hit
        print(f"    {txt:<28} -> {got:<11} want {want:<11} {'ok' if hit else '⛔'}")
    return ok


def main() -> int:
    print("REGISTER REQUIREMENTS — a requirement is an ENUM, never prose (HB8)\n")
    print("  POSITIVE CONTROL — the gate must accept a valid tag and reject an invented one:")
    if not selftest():
        print("\n  ⛔ the gate failed its own control. Exit 2, never 0.")
        return 2
    es = entries()
    if not es:
        print("\n  UNRUNNABLE: no register entries found. Exit 2, never 0.")
        return 2
    c = collections.Counter(classify(e)[0] for e in es)
    print(f"\n  {len(es)} register entries across {len({e['round'] for e in es})} rounds")
    for k in ("REQUIRES", "SCOPE_ONLY", "RESTATES", "BAD_KIND", "UNDECLARED"):
        print(f"    {k:<12} {c[k]:>4}")
    kinds = collections.Counter(classify(e)[1] for e in es if classify(e)[0] == "REQUIRES")
    if kinds:
        print("\n  declared requirement kinds:")
        for k, v in kinds.most_common():
            print(f"    {v:>4}  {k}")
    # a RESTATES chain must terminate in a real declaration
    byround = collections.defaultdict(list)
    for e in es:
        byround[e["round"]].append(classify(e))
    dangling = [e["round"] for e in es if classify(e)[0] == "RESTATES"
                and not any(k in ("REQUIRES", "SCOPE_ONLY") for k, _ in byround.get(classify(e)[1], []))]
    print(f"\n  RESTATES chains terminating in air: {len(dangling)}   {dangling or ''}")
    print(f"\n  ⚠ WHAT THIS GATE CANNOT DO: it checks a declaration EXISTS and is WELL-FORMED. It")
    print(f"    cannot check the declaration is TRUE of the entry — a gold-standard limit tagged")
    print(f"    SECOND_JUDGE passes. The enum removes the WORDING loophole, not the MISLABELLING one.")
    bad = c["BAD_KIND"] + len(dangling)
    print(f"\n  ⚠ UNDECLARED: {c['UNDECLARED']} of {len(es)} — NOT passes. This is the worklist R472")
    print(f"    measured, now with a gate that will not let a converted entry be prose.")
    declared = len(es) - c["UNDECLARED"]
    if declared == 0:
        print(f"\n  ⛔ EMPTY DECLARED POPULATION. The gate would 'PASS' having validated NOTHING —")
        print(f"     §4's `empty population passes`, and the selftest uses SYNTHETIC strings, so it")
        print(f"     is no evidence the gate works on real entries. Exit 2, never 0.")
        return 2
    if bad:
        print(f"\n  ⛔ FAIL: {bad} malformed declaration(s).")
        return 1
    print(f"\n  PASS — {declared} DECLARED entries, all well-formed; "
          f"{c['UNDECLARED']} remain undeclared (not passes).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
