#!/usr/bin/env python3
"""
R671 -- extend the quantifier gate to the 80 README `## NEXT` sections it has never read.

CHECK #272 ON R670's CLOSING LINE. THE STALE COUNT SURVIVED INTO THE ROUND THAT CORRECTED IT.
  ⛔ "three of this arc's FOUR quantifier failures reached a README `## NEXT` section." R670 itself
     established there are **three** in-scope failures -- 725 is a categorical claim about an
     object, a different class -- and I wrote "four" one paragraph later. **The number I had just
     retracted reappeared in the closing line of the round that retracted it.**
  ⛔ And "three of them reached a README" is itself wrong: measured, **715 and 720 did; 723 did
     not.** Two of three.
  ✓ "the README half is a file, and a file can be read" -- 80 of 340 READMEs carry a `## NEXT`
     section, and the gate has never looked at any of them.

ESTIMAND        Applying the gate's own (widened) rule to the README `## NEXT` population: what
                fraction carry an unsourced quantifier over the project's own work, and how does
                that base rate compare with the 37.2% measured over commit bodies?
IDENTIFICATION  Exact for the flag count. NOT identified: whether a flagged line is actually FALSE
                -- the gate polices unsourced quantification, not truth, and always has. That
                distinction is the gate's, not this round's, and is restated rather than blurred.
SCOPE           population : every `## NEXT` section in every README under A24
                instrument : the gate's QUANT x ARTIFACT window rule, unchanged from R670
                             instrument unit = A README `## NEXT` SECTION
                             claim unit      = A CLOSING SENTENCE IN A REPORT
                             CLOSER THAN BEFORE BUT STILL NOT EQUAL -- a README NEXT is the
                             report's closing sentence written down, which is why this extension
                             narrows the gap the gate's docstring called structural; the terminal
                             half remains unreadable and is still named
                baseline   : 37.2% over 371 commit-body NEXT paragraphs (R670)
                regime     : this repository at this sha
WORLDS          A THE README IS WORSE: rate above the commit rate -> the surface where failures
                  actually land was the unpoliced one, and the extension is the repair.
                B THE README IS CLEANER: rate below -> commit bodies were the risky surface all
                  along and the extension buys little.
                C ORDINARY LANGUAGE: rate > 60% -> the rule does not transfer to this population
                  and the extension is NOT applied.
KILL            pre-registered in PREREGISTRATION.txt: point 40%, interval [20%, 60%]; > 60%
                blocks the extension outright.
POSITIVE CTRL   ledger 715 (R665's README) and 720 (R666's README) are KNOWN-false lines living in
                README `## NEXT` sections. The rule must flag both, or it cannot see the class in
                this population and no rate is admissible.
NEGATIVE CTRL   a README NEXT that cites its instrument must NOT flag -- the PROVENANCE escape has
                to work in the new population too, not just in commit bodies.
PLACEBO         a `## NEXT` with a quantifier and NO artifact noun must not fire.
NOISE FLOOR     n/a -- deterministic text matching over a fixed tree.
MULTIPLICITY    1 rule x 80 README sections + 3 controls; both base rates reported side by side.
ARTIFACT        results/readme_next.json
IMPOSSIBLE      the TERMINAL report is still unreadable -- it is never written to disk. This
                extension narrows the unit gap from "reports" to "reports minus the terminal
                half", and that residue is named rather than closed.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
sys.path.insert(0, str(ROOT / "assurance"))
G = __import__("next_line_quantifiers_are_computed")

PREREG = {"point_pct": 40, "interval_pct": [20, 60],
          "directional": "the README rate is HIGHER than the commit-body 37.2%",
          "kill": "> 60% blocks the extension"}


def readme_nexts():
    out = []
    for f in sorted(A24.rglob("README.md")):
        t = f.read_text(errors="ignore")
        m = re.search(r"^##+\s*NEXT\b(.*?)(?=\n##\s|\Z)", t, re.M | re.S)
        if m:
            out.append((f.parent.name, " ".join(m.group(1).split())))
    return out


def flagged(s):
    for m in G.QUANT.finditer(s):
        w = s[max(0, m.start() - G.WINDOW): m.end() + G.WINDOW]
        if G.ARTIFACT.search(w) and not G.PROVENANCE.search(w):
            return True, m.group(0)
    return False, None


def main() -> int:
    secs = readme_nexts()
    if len(secs) < 20:
        print(f"UNRUNNABLE: only {len(secs)} README NEXT sections. Exit 2, never 0.")
        return 2

    print("─── PRE-REGISTRATION (written before any code) ───")
    print(f"  point {PREREG['point_pct']}%  interval {PREREG['interval_pct']}%")
    print(f"  directional: {PREREG['directional']}   kill: {PREREG['kill']}")

    print("\n─── CONTROLS ───")
    known = {"715": "last structural question", "720": "only cell in this whole curve"}
    hits = {}
    for lid, ph in known.items():
        sec = next((s for _, s in secs if ph.lower() in s.lower()), None)
        hits[lid] = flagged(sec)[0] if sec else None
    posok = all(hits.values())
    print(f"  POSITIVE  known-false lines living in README NEXT sections -> "
          f"{ {k: ('FLAG' if v else 'MISS' if v is False else 'ABSENT') for k, v in hits.items()} } "
          f"-> {'PASS' if posok else '⛔ FAIL — the rule cannot see the class here'}")
    negs = "recompute the every-round table (run assurance/residue_debt.py) before quoting it"
    negok = not flagged(negs)[0]
    print(f"  NEGATIVE  a NEXT citing its instrument must NOT flag -> {'clean' if negok else 'FLAGGED'}"
          f" -> {'PASS — the provenance escape transfers' if negok else '⛔ FAIL'}")
    plc = "every morning the disk fills a little more and the fans spin up"
    plcok = not flagged(plc)[0]
    print(f"  PLACEBO   a quantifier with no artifact noun -> {'clean' if plcok else 'FLAGGED'} -> "
          f"{'PASS' if plcok else '⛔ FAIL'}")

    fl = [(r, s, flagged(s)[1]) for r, s in secs if flagged(s)[0]]
    rate = len(fl) / len(secs)
    COMMIT_RATE = 0.372
    print(f"\n─── THE POPULATION THE GATE HAS NEVER READ ───")
    print(f"  README `## NEXT` sections : {len(secs)}")
    print(f"  flagged                   : {len(fl)}  ({rate:.1%})")
    print(f"  commit-body rate (R670)   : {COMMIT_RATE:.1%}")
    print(f"  ⭐ difference              : {100*(rate-COMMIT_RATE):+.1f} pts")
    print(f"\n  a sample of what it flags, with the quantifier (G3 — not only the convenient ones):")
    for r, s, q in fl[:10]:
        print(f"    {r[:44]:<44} '{q}'  {s[:56]}")

    lo, hi = PREREG["interval_pct"]
    inside = lo <= 100 * rate <= hi
    directional = rate > COMMIT_RATE
    print(f"\n─── THE PRE-REGISTERED ESTIMATE ───")
    print(f"  point {PREREG['point_pct']}% · interval [{lo}%, {hi}%]   measured {100*rate:.1f}% -> "
          f"{'INSIDE' if inside else 'OUTSIDE'}; error {100*rate - PREREG['point_pct']:+.1f} pts")
    print(f"  directional ('README higher than commit bodies'): "
          f"{'HOLDS' if directional else '⛔ RETRACTED'}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=ROOT).stdout.strip()
    controls_ok = posok and negok and plcok
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; the extension is not applied"
    elif rate > 0.60:
        world = (f"C ORDINARY LANGUAGE — {rate:.1%} of README NEXT sections flag; the rule does "
                 f"not transfer to this population and the extension is NOT applied.")
    elif directional:
        world = (f"A THE README IS THE WORSE SURFACE — {len(fl)} of {len(secs)} sections "
                 f"({rate:.1%}) carry an unsourced quantifier over our own work, against "
                 f"{COMMIT_RATE:.1%} in commit bodies ({100*(rate-COMMIT_RATE):+.1f} pts). ⭐ THE "
                 f"SURFACE WHERE THE FAILURES ACTUALLY LAND WAS THE UNPOLICED ONE — 715 and 720 "
                 f"both live in README NEXT sections, and the gate has never read a single one of "
                 f"the {len(secs)}. ⚠ AND THE UNIT GAP NARROWS RATHER THAN CLOSES: a README NEXT "
                 f"is the report's closing sentence written down, but the TERMINAL report is never "
                 f"on disk and stays unreadable. The gate's docstring called that gap structural; "
                 f"it is structural for half of it.")
    else:
        world = (f"B THE README IS CLEANER — {rate:.1%} vs {COMMIT_RATE:.1%} in commit bodies; the "
                 f"risky surface was the one already policed and the extension buys little.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 rule x {len(secs)} README sections + 3 controls; both base rates "
          f"reported side by side.")
    print(f"  ⚠ THE GATE POLICES UNSOURCED QUANTIFICATION, NOT TRUTH — a flag is not a false "
          f"claim, and that has always been its scope.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "readme_next.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha, "prereg": PREREG,
        "n_sections": len(secs), "n_flagged": len(fl), "readme_rate": rate,
        "commit_rate": COMMIT_RATE, "delta_pts": 100 * (rate - COMMIT_RATE),
        "magnitude_inside": inside, "directional_holds": directional,
        "flagged": [{"round": r, "quantifier": q, "text": s[:200]} for r, s, q in fl],
        "check272": ("R670's NEXT said 'three of this arc's FOUR quantifier failures' one "
                     "paragraph after R670 established there are THREE in scope; and 'three "
                     "reached a README' is itself wrong -- 715 and 720 did, 723 did not."),
        "impossible": ("the TERMINAL report is never written to disk and stays unreadable; this "
                       "extension narrows the unit gap rather than closing it."),
    }, indent=2))
    print(f"\n  wrote {out / 'readme_next.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
