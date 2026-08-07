#!/usr/bin/env python3
"""R763 · did the drift return, and does the answer depend on which UNIT you count?

⛔ CHECK #365 -- TWO FINDINGS BEFORE R762's PROPOSED ROUND COULD RUN.
① The arithmetic in my own NEXT line was wrong: two overlapping MARGINAL intervals do not imply a
   non-significant PAIRED difference, and both Jaccards are computed against the SAME resampled
   robust set, so they are paired by construction.
② R664 committed "0 of 24 object headlines, R640-R663" with controls and the verdict "the loop is
   the defect, and the next round must move the definition or not run." THE GATE HAS NOT BEEN RUN
   SINCE, and R664's glob is hardcoded `R6[0-9][0-9]_*` so the instrument cannot see this era.

⚠ AND R664's RULE HAS A BLIND SPOT ITS OWN README DECLARES -- a keyword test on a headline is a
  LOWER bound. §4: a control sharing the instrument's blind spot licenses nothing; name the
  INSTRUMENT'S unit and the CLAIM'S unit and require them equal. Instrument unit = a HEADLINE
  STRING. Claim unit = DID THE ROUND CHANGE WHAT THE PAGE SAYS A CORE IS. Not equal -> build C2.

C1  R664's keyword rule, verbatim, on the headline.
C2  did the round's own commit edit a line inside STATEMENT.md's `## The definition` block, with the
    block bounds RECOMPUTED AT THAT COMMIT (the page grew 1177 -> 1313 lines in this arc).

CONTROLS  POSITIVE-1 (C1 reproduces R664's committed 0 of 24 on R664's own era; band computed) ·
          POSITIVE-2 (C2 fires on R760, C1 fires on R527/R519) · NEGATIVE (C1 not OBJECT on R654;
          C2 not fired by a commit touching no STATEMENT.md) · g=0 (empty headline; empty diff) ·
          SHAM (a RANDOM equal-length block elsewhere in the page, 200 draws) · PLACEBO (R664's) ·
          CONFOUND (how many rounds edited STATEMENT.md AT ALL -- if equal to C2, C2 measures the
          convention, not the content).
UNIT      C1 = a headline STRING · C2 = a DIFF HUNK · claim = a ROUND. Never merged into one score.
"""
import json, pathlib, re, subprocess, sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
STATEMENT = "E05_the_space_of_compilers/STATEMENT.md"
OBJ = re.compile(r"\bcore\b|\bclause\b|\bdefinition\b|\brelease\b|\bextension\b", re.I)
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")
BLOCK_START, BLOCK_END = "## The definition", "## What each clause is worth"


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout


def is_object(h):
    return bool(OBJ.search(h))


def headline(d):
    f = d / "README.md"
    return f.read_text(errors="ignore").split("\n")[0].lstrip("# ").strip() if f.is_file() else ""


def rounds_in(lo, hi):
    out = []
    for d in sorted(A24.glob("R[0-9][0-9][0-9]_*")):
        m = re.match(r"R(\d+)", d.name)
        if m and lo <= int(m.group(1)) <= hi and (d / "README.md").is_file():
            out.append((int(m.group(1)), d))
    return out


def commit_of(d):
    """R758's resolver: the commit that ADDED the round's run.py. Empty -> the round is uncommitted."""
    s = git("log", "--diff-filter=A", "--format=%H", "-1", "--", str(d.relative_to(ROOT)) + "/run.py")
    return s.strip() or None


CLAUSE = re.compile(r"^\s*- \*\*[①②③④⑤]\*\*")


def clause_spans(sha):
    """C3's unit: the clause BULLETS themselves -- `- **②**` and its continuations. Recomputed at
    the commit. 41 lines today = 3.1% of the page, against the definition block's 36.6%."""
    txt = git("show", f"{sha}:{STATEMENT}")
    if not txt:
        return []
    L = txt.split("\n"); spans = []; i = 0
    while i < len(L):
        if CLAUSE.match(L[i]):
            j = i + 1
            while j < len(L) and (L[j].startswith("  ") or L[j].startswith("- ") or not L[j].strip()):
                if L[j].startswith("- ") and not CLAUSE.match(L[j]):
                    break
                j += 1
            spans.append((i + 1, j)); i = j
        else:
            i += 1
    return spans


def block_bounds(sha):
    """Recomputed AT THAT COMMIT -- the page has grown and a fixed range would be wrong."""
    txt = git("show", f"{sha}:{STATEMENT}")
    if not txt:
        return None
    lines = txt.split("\n")
    a = b = None
    for i, ln in enumerate(lines, 1):
        if ln.startswith(BLOCK_START) and a is None: a = i
        elif a is not None and ln.startswith(BLOCK_END): b = i; break
    return (a, b if b else len(lines)) if a else None


def touched_ranges(sha):
    """New-file line ranges this commit added/changed in STATEMENT.md."""
    d = git("show", "--unified=0", "--format=", sha, "--", STATEMENT)
    out = []
    for ln in d.split("\n"):
        m = HUNK.match(ln)
        if m:
            st = int(m.group(1)); n = int(m.group(2) or 1)
            if n: out.append((st, st + n - 1))
    return out


def overlaps(ranges, lo, hi):
    return any(not (b < lo or a > hi) for a, b in ranges)


def classify(lo, hi):
    rows = []
    for num, d in rounds_in(lo, hi):
        sha = commit_of(d)
        h = headline(d)
        r = {"round": d.name, "n": num, "headline": h, "C1": is_object(h),
             "sha": sha[:8] if sha else None, "C2": False, "touched_statement": False,
             "ranges": [], "block": None, "C3": False, "clause_spans": []}
        if sha:
            rg = touched_ranges(sha); bb = block_bounds(sha)
            cs = clause_spans(sha)
            r["ranges"] = rg; r["block"] = bb; r["clause_spans"] = cs
            r["touched_statement"] = bool(rg)
            r["C2"] = bool(rg and bb and overlaps(rg, *bb))
            r["C3"] = bool(rg and any(overlaps(rg, a, b) for a, b in cs))
        rows.append(r)
    return rows


def main():
    print("─── CONTROLS ───")
    # POSITIVE-1 · the strong one: R664's own era, against its committed number.
    r664 = json.loads((A24 / "R664_twentyfour_rounds_zero_object_claims/results/"
                       "object_vs_apparatus.json").read_text())
    old = classify(640, 663)
    old = [r for r in old if r["round"] != "R664_twentyfour_rounds_zero_object_claims"]
    c1_old = sum(1 for r in old if r["C1"])
    ok1 = (c1_old == r664["A_object_headlines"] and len(old) == r664["n_rounds"])
    print(f"  POSITIVE-1  C1 on R664's era: {c1_old} of {len(old)} vs committed "
          f"{r664['A_object_headlines']} of {r664['n_rounds']}  {'PASS' if ok1 else '⛔ FAIL'}")
    print(f"              band: a rule matching NOTHING also returns 0 here (excluded by POSITIVE-2);"
          f" one matching EVERYTHING returns {len(old)}. Threshold unreachable from that end.")

    pos2a = [is_object(headline(d)) for _, d in rounds_in(519, 519) + rounds_in(527, 527)]
    r760 = [d for _, d in rounds_in(760, 760)]
    sha760 = commit_of(r760[0]) if r760 else None
    bb760 = block_bounds(sha760) if sha760 else None
    rg760 = touched_ranges(sha760) if sha760 else []
    pos2b = bool(rg760 and bb760 and overlaps(rg760, *bb760))
    ok2 = all(pos2a) and pos2b
    print(f"  POSITIVE-2  C1 on R527/R519 -> {pos2a} · C2 on R760 (known definition-block edit) "
          f"-> {pos2b}  {'PASS' if ok2 else '⛔ FAIL'}")

    neg1 = any(is_object(headline(d)) for _, d in rounds_in(654, 654))
    nostmt = [r for r in classify(739, 762) if not r["touched_statement"]]
    neg2 = all(not r["C2"] for r in nostmt)
    ok3 = (not neg1) and neg2
    print(f"  NEGATIVE    C1 on R654 -> {'OBJECT' if neg1 else 'APPARATUS'} · "
          f"{len(nostmt)} rounds touching no STATEMENT.md, C2 fired on "
          f"{sum(1 for r in nostmt if r['C2'])}  {'PASS' if ok3 else '⛔ FAIL'}")

    ok4 = (not is_object("")) and (not overlaps([], 1, 10))
    print(f"  g=0         empty headline not OBJECT · empty diff not C2  "
          f"{'PASS' if ok4 else '⛔ FAIL'}")
    plc = not is_object("The suite was consistent and I truncated its output")
    print(f"  PLACEBO     keyword-free headline -> not OBJECT  {'PASS' if plc else '⛔ FAIL'}")

    # ---- the window -------------------------------------------------------------------------
    rows = classify(739, 762)
    C1 = sum(1 for r in rows if r["C1"]); C2 = sum(1 for r in rows if r["C2"])
    TOUCH = sum(1 for r in rows if r["touched_statement"])
    print(f"\n─── THE WINDOW · R739-R762, n = {len(rows)} ───")
    print(f"  C1 keyword-on-headline   OBJECT: {C1:>3} / {len(rows)}")
    print(f"  C2 edited-the-definition OBJECT: {C2:>3} / {len(rows)}")
    print(f"  ⚠ CONFOUND  rounds editing STATEMENT.md AT ALL: {TOUCH} / {len(rows)}  -> "
          f"{'C2 IS the convention' if C2 == TOUCH else 'C2 separates from the convention'}")

    # ---- SHAM · the ingredient is the BLOCK BOUNDARY -----------------------------------------
    rng = np.random.default_rng(763)
    sham = []
    for _ in range(200):
        k = 0
        for r in rows:
            if not (r["ranges"] and r["block"]): continue
            lo, hi = r["block"]; L = hi - lo
            txt_len = max(L + 2, len(git("show", f"{r['sha']}:{STATEMENT}").split("\n")))
            st = int(rng.integers(1, max(2, txt_len - L)))
            if overlaps(r["ranges"], st, st + L): k += 1
        sham.append(k)
    C3 = sum(1 for r in rows if r["C3"])
    sham3 = []
    for _ in range(200):
        k = 0
        for r in rows:
            if not (r["ranges"] and r.get("clause_spans")): continue
            txt_len = max(60, len(git("show", f"{r['sha']}:{STATEMENT}").split("\n")))
            hit = False
            for a, b in r["clause_spans"]:
                L = b - a
                st = int(rng.integers(1, max(2, txt_len - L)))
                if overlaps(r["ranges"], st, st + L): hit = True
            if hit: k += 1
        sham3.append(k)

    s2lo, s2hi = np.percentile(sham, 2.5), np.percentile(sham, 97.5)
    s3lo, s3hi = np.percentile(sham3, 2.5), np.percentile(sham3, 97.5)
    c2_adm = not (s2lo <= C2 <= s2hi)
    c3_adm = not (s3lo <= C3 <= s3hi)
    print(f"  C3 edited-a-clause-bullet OBJECT: {C3:>3} / {len(rows)}")
    print(f"\n  ⭐ G4 · THE UNIT IS A SPECIFICATION, so each is priced against its OWN sham")
    print(f"  {'unit':<34}{'% of page':>10}{'count':>7}{'sham 95%':>14}   admissible?")
    pg = len(git("show", f"{rows[-1]['sha']}:{STATEMENT}").split("\n"))
    bl = rows[-1]["block"]; cl = rows[-1].get("clause_spans") or [(0, 0)]
    print(f"  {'C2 the definition block':<34}{(bl[1]-bl[0])/pg:>9.1%}{C2:>7}"
          f"{f'[{s2lo:.0f}, {s2hi:.0f}]':>14}   {'YES' if c2_adm else '⛔ NO — inside its own sham'}")
    print(f"  {'C3 the clause bullets':<34}"
          f"{sum(b-a+1 for a,b in cl)/pg:>9.1%}{C3:>7}"
          f"{f'[{s3lo:.0f}, {s3hi:.0f}]':>14}   {'YES' if c3_adm else '⛔ NO — inside its own sham'}")

    # ---- the 2x2, every disagreeing round NAMED ----------------------------------------------
    cell = {(a, b): [r["round"][:40] for r in rows if r["C1"] == a and r["C2"] == b]
            for a in (True, False) for b in (True, False)}
    print(f"\n  {'':>18}{'C2 OBJECT':>12}{'C2 apparatus':>14}")
    print(f"  {'C1 OBJECT':>18}{len(cell[(True,True)]):>12}{len(cell[(True,False)]):>14}")
    print(f"  {'C1 apparatus':>18}{len(cell[(False,True)]):>12}{len(cell[(False,False)]):>14}")
    for k, lbl in [((True, False), "C1 only -- headline claims the object, page's definition untouched"),
                   ((False, True), "C2 only -- edited the definition under an apparatus headline")]:
        print(f"\n  ⭐ {lbl}: {len(cell[k])}")
        for n in cell[k]: print(f"       {n}")

    print(f"\n  {'round':<44}{'C1':>4}{'C2':>4}  headline")
    for r in rows:
        print(f"  {r['round'][:44]:<44}{'O' if r['C1'] else '.':>4}"
              f"{'O' if r['C2'] else '.':>4}  {r['headline'][:60]}")

    # ⛔ THE VERDICT MUST REFERENCE EVERY CONTROL THE ROUND DECLARED (§4). The first version of this
    # branch printed WORLD C off |C1-C2| alone while the SHAM two lines above said C2 is inside its
    # own random-block band -- a verdict string asserting what its own control forbade.
    controls_ok = ok1 and ok2 and ok3 and ok4 and plc
    admissible = [("C1", C1, True)] + [(n, v, a) for n, v, a in
                                       (("C2", C2, c2_adm), ("C3", C3, c3_adm)) if a]
    if not controls_ok:
        world = "UNVERIFIED"
    elif len(admissible) == 1:
        world = ("A · on the ONLY admissible unit — C1 = %d of %d. The second and third units are "
                 "UNVERIFIED, not disagreeing." % (C1, len(rows))) if C1 <= 4 else \
                ("B · on the only admissible unit — C1 = %d of %d" % (C1, len(rows)))
    else:
        spread = max(v for _, v, _ in admissible) - min(v for _, v, _ in admissible)
        if spread >= 6:
            world = "C · admissible units disagree by %d" % spread
        elif all(v <= 6 for _, v, _ in admissible):
            world = "A"
        elif all(v >= 10 for _, v, _ in admissible):
            world = "B"
        else:
            world = "NO WORLD -- counts reported, none claimed"
    print(f"\n  admissible units: {[n for n,_,a in admissible]}   "
          f"UNVERIFIED: {[n for n,v,a in (('C2',C2,c2_adm),('C3',C3,c3_adm)) if not a]}")
    print(f"  WORLD {world}")

    out = HERE / "results/drift_by_two_units.json"
    out.write_text(json.dumps({
        "tree_sha": git("rev-parse", "HEAD^{tree}").strip()[:16],
        "window": [739, 762], "n": len(rows), "C1": C1, "C2": C2, "C3": C3,
        "c2_admissible": bool(c2_adm), "c3_admissible": bool(c3_adm),
        "sham3_mean": float(np.mean(sham3)), "sham3_lo": float(s3lo), "sham3_hi": float(s3hi),
        "touched_statement": TOUCH,
        "controls": {"positive1_c1_on_r664_era": c1_old, "positive1_committed":
                     r664["A_object_headlines"], "positive1_pass": ok1,
                     "positive2_pass": ok2, "negative_pass": ok3, "g0_pass": ok4, "placebo": plc},
        "sham_mean": float(np.mean(sham)), "sham_lo": float(np.percentile(sham, 2.5)),
        "sham_hi": float(np.percentile(sham, 97.5)),
        "cells": {f"C1={a},C2={b}": v for (a, b), v in cell.items()},
        "rows": rows, "world": world,
    }, indent=2, default=str))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
