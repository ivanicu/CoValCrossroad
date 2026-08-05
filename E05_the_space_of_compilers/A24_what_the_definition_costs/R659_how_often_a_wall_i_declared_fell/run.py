#!/usr/bin/env python3
"""
R659 -- how often has a wall I declared fallen? The prior R658's conclusion has to survive.

CHECK #260 ON R658's CLOSING LINE. BOTH CHECKABLE CLAUSES ARE WRONG, AND THE SECOND BADLY.
  ✓ "`d` accounts for 75 of the 126 unresolved pairs" -- 59.5%, correct.
  ⛔ "It IS a for-loop variable over an iterable the evaluator cannot resolve." Bound by `For`
     ONLY in 14 of 75. Twenty-three are `['Assign']` with no `For` at all, and the rest are
     multi-form. I described 75 sites from the shape of the ones I had happened to read.
  ⛔ "I have TWICE now declared a limit that a single mechanical fix would have moved." A keyword
     scan of the ledger returns 23 candidate entries, and two of them settle it without any
     instrument at all: entry 358 is TITLED "The fourth false wall", and entry 369 records "two
     more walls fell". So by entry 369 the count was already >= 6. **The number was in my own
     ledger, in a title, and I wrote "twice".**

⭐ AND THAT IS WHY THIS ROUND EXISTS RATHER THAN THE `d`-LOOP ONE. R658 concluded "the residual is
   closer to structural". Whether that should be believed depends on how often my declared limits
   have survived -- which is a measurable property of this corpus and is the prior the conclusion
   has to clear. The cheaper question (what 75 loops iterate over) does not test the conclusion.

ESTIMAND        A (exact): committed rounds whose run.py docstring declares an IMPOSSIBLE register
                  -- how many times I have written a limit down at all.
                B (tight instrument + positive control): RETRACTIONS.md entries recording a
                  previously-declared wall / impossibility / limit being OVERTURNED.
                C (the only per-wall quantity): entries in B that NAME a specific round, so the
                  overturned wall can be traced to where it was declared.
IDENTIFICATION  A is exact. B is a text classification and is bounded, not identified: a loose
                pattern over-counts (§4's row) and a tight one under-counts. BOTH are run and BOTH
                reported, and the claim is the INTERVAL between them, never one of the two.
                C is exact given B.
SCOPE           population : every A24 round's run.py docstring (A); all RETRACTIONS.md entries (B)
                instrument : ast.get_docstring for A; two patterns of different tightness for B
                             instrument unit = A DOCSTRING SECTION (A) / A LEDGER ENTRY (B)
                             claim unit      = A DECLARED LIMIT (A) / AN OVERTURNED LIMIT (B)
                             NOT EQUAL, and B/A is therefore NOT a rate -- a ledger entry can
                             overturn a wall that was never written into any register
                baseline   : R658's NEXT, which said "twice"
                regime     : at the tree sha persisted in the artifact
WORLDS          A "TWICE" WAS RIGHT: the tight count is <= 3 -> my sense of my own record is
                  calibrated and R658's "closer to structural" needs no discount.
                B "TWICE" WAS AN UNDERCOUNT: the tight count is much larger -> I systematically
                  under-remember my own overturned limits, and every structural conclusion in this
                  arc, R658's included, carries that prior.
                C THE INSTRUMENT CANNOT DECIDE: loose and tight differ by more than they agree ->
                  report the interval and refuse a point.
KILL            pre-registered in PREREGISTRATION.txt before the code: point 10, interval [5, 25],
                and the directional prediction that "twice" undercounts by >= 3x. If the TIGHT
                count is <= 3, that prediction is RETRACTED.
POSITIVE CTRL   entries 351, 358, 369 and 651 are KNOWN members -- each records a wall falling, and
                358's own title says "the fourth". The tight pattern must find all four, or it has
                not been shown to see the class and no count is admissible.
                Fails at g=0: an empty ledger yields 0.
NEGATIVE CTRL   entry 520 ("A placebo that was a tautology AND could not pass") is a control defect,
                NOT a wall falling. The tight pattern must NOT match it. The failure direction is a
                pattern that matches every self-critical entry, which is most of the file.
PLACEBO         a nonexistent marker must return 0 entries.
NOISE FLOOR     n/a -- a census of a fixed text. Deterministic.
SEEDS           n/a.
MULTIPLICITY    2 patterns x every ledger entry + 1 scan x every round docstring + 4 controls.
                Both counts reported, and the interval between them is the claim.
ARTIFACT        results/wall_record.json, with the tree sha and the pre-registration verbatim.
IMPOSSIBLE      "this entry overturns a wall" is a judgement about prose; no pattern decides it.
                That is why two patterns of different tightness are run and the INTERVAL is the
                result. Collapsing to a point would be the §4 row this round is about.
"""
from __future__ import annotations
import ast, json, pathlib, re, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
LEDGER = ROOT / "RETRACTIONS.md"

PREREG = {"point_B": 10, "interval_B": [5, 25],
          "directional": "R658's 'twice' undercounts by at least 3x",
          "kill": "a TIGHT count <= 3 retracts the directional prediction",
          "units_note": ("B/A is NOT a rate: a docstring section and a ledger entry are different "
                         "units, and a ledger entry can overturn a wall never written into any "
                         "register")}

# TIGHT: the entry must say a LIMIT-WORD and an OVERTURN-WORD, and the overturn must be about the
# limit rather than about a control or a number. Deliberately narrow; it will under-count.
WALL = r"(wall|impossib|structural limit|cannot be (?:known|measured|answered)|permanent limit|" \
       r"unavailab|no instrument|not recoverable|register)"
FELL = r"(fell|false|was one |turned out|retracted|overturn|it was not|is not impossible|" \
       r"needed only|one command|one query|one JSON|one pass|one grep)"
# LOOSE: any self-critical entry mentioning a limit at all. Deliberately wide; it will over-count.
LOOSE = r"(wall|impossib|limit|unavailab|cannot)"


def entries(text):
    out = []
    ms = list(re.finditer(r"^## (\d+) · (.+)$", text, re.M))
    for i, m in enumerate(ms):
        body = text[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(text)]
        out.append({"id": int(m.group(1)), "title": m.group(2), "body": body})
    return out


def tight(e):
    blob = (e["title"] + " " + e["body"]).lower()
    return bool(re.search(WALL, blob)) and bool(re.search(FELL, blob))


def loose(e):
    return bool(re.search(LOOSE, (e["title"] + " " + e["body"]).lower()))


def main() -> int:
    if not LEDGER.exists():
        print("UNRUNNABLE: RETRACTIONS.md absent. Exit 2, never 0.")
        return 2
    text = LEDGER.read_text()
    es = entries(text)
    if len(es) < 100:
        print(f"UNRUNNABLE: only {len(es)} ledger entries parsed. Exit 2.")
        return 2

    rounds = [d for d in sorted(A24.glob("R[0-9]*"))
              if (d / "run.py").is_file() and d.resolve() != HERE]
    declared = []
    for d in rounds:
        try:
            doc = ast.get_docstring(ast.parse((d / "run.py").read_text(errors="ignore"))) or ""
        except SyntaxError:
            continue
        if re.search(r"^IMPOSSIBLE\s", doc, re.M):
            declared.append(d.name)

    print("─── PRE-REGISTRATION (written before any code for this round) ───")
    print(f"  B: point {PREREG['point_B']}   interval {PREREG['interval_B']}")
    print(f"  directional: {PREREG['directional']}")
    print(f"  kill       : {PREREG['kill']}")
    print(f"  ⚠ {PREREG['units_note']}")

    print("\n─── CONTROLS ───")
    T = [e for e in es if tight(e)]
    L = [e for e in es if loose(e)]
    tids = {e["id"] for e in T}
    KNOWN = [351, 358, 369, 651]
    hit = [k for k in KNOWN if k in tids]
    print(f"  POSITIVE   known members {KNOWN} (358's own title says 'the fourth false wall') -> "
          f"found {hit} -> {'PASS' if len(hit) == len(KNOWN) else '⛔ FAIL — missing ' + str([k for k in KNOWN if k not in tids])}")
    NEG = 520          # "A placebo that was a tautology AND could not pass" — a control defect
    negok = NEG not in tids
    neg_e = next((e for e in es if e["id"] == NEG), None)
    print(f"  NEGATIVE   entry {NEG} ({(neg_e['title'] if neg_e else '?')[:52]}) is a CONTROL "
          f"defect, not a wall -> {'excluded' if negok else 'MATCHED'} -> "
          f"{'PASS' if negok else '⛔ FAIL — the pattern matches every self-critical entry'}")
    plc = [e for e in es if re.search(r"zzq_no_such_marker", e["body"])]
    print(f"  PLACEBO    a nonexistent marker -> {len(plc)} entries -> "
          f"{'PASS' if not plc else '⛔ FAIL'}")
    g0 = [e for e in entries("") if tight(e)]
    print(f"  g=0        an empty ledger -> {len(g0)} -> {'PASS' if not g0 else '⛔ FAIL'}")
    controls_ok = len(hit) == len(KNOWN) and negok and not plc and not g0
    print(f"  KILL       a TIGHT count <= 3 retracts the directional prediction")

    # ---- THE COUNTS -----------------------------------------------------------------
    named = [e for e in T if re.search(r"\bR\d{3}\b", e["title"] + e["body"])]
    print(f"\n─── HOW MANY TIMES A DECLARED LIMIT FELL ───")
    print(f"  ledger entries parsed          : {len(es)}")
    print(f"  A · rounds declaring IMPOSSIBLE : {len(declared)} of {len(rounds)} "
          f"({len(declared)/len(rounds):.1%})")
    print(f"  B · TIGHT  (under-counts)       : {len(T)}")
    print(f"  B · LOOSE  (over-counts)        : {len(L)}")
    print(f"  ⭐ the claim is the INTERVAL     : [{len(T)}, {len(L)}] — never a point")
    print(f"  C · of the TIGHT, NAMING a round: {len(named)} (the only per-wall traceable subset)")
    print(f"\n  the TIGHT members, every one (G3 — no truncation, check #258's lesson):")
    for e in T:
        print(f"    {e['id']:>4}  {e['title'][:92]}")

    lo, hi = PREREG["interval_B"]
    inside = lo <= len(T) <= hi
    directional = len(T) > 3 and len(T) >= 6
    print(f"\n─── THE PRE-REGISTERED ESTIMATE, EVALUATED ───")
    print(f"  point {PREREG['point_B']} · interval [{lo}, {hi}]   measured TIGHT {len(T)}")
    print(f"  => magnitude {'INSIDE' if inside else 'OUTSIDE'} the interval; error vs point "
          f"{len(T) - PREREG['point_B']:+d}")
    print(f"  => directional ('twice undercounts by >=3x'): "
          f"{'HOLDS' if directional else '⛔ RETRACTED'}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no count is admissible"
    elif len(T) <= 3:
        world = (f"A 'TWICE' WAS RIGHT — the tight instrument finds {len(T)}; my sense of my own "
                 f"record is calibrated and R658's 'closer to structural' needs no discount.")
    else:
        world = (f"B 'TWICE' WAS AN UNDERCOUNT — the tight instrument finds {len(T)} and the loose "
                 f"one {len(L)}, so a declared limit has fallen somewhere in [{len(T)}, {len(L)}] "
                 f"times against {len(declared)} rounds that declared one. ⭐ THE PRIOR THIS SETS: "
                 f"R658 concluded 'the residual is closer to structural', and in this corpus a "
                 f"structural conclusion of mine has been overturned at least {len(T)} times. "
                 f"That conclusion is DOWNGRADED — not refuted, because this round measures my "
                 f"record and not the residual, but it may not be quoted without the prior.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 2 patterns x {len(es)} entries + 1 scan x {len(rounds)} docstrings "
          f"+ 4 controls. Both counts reported; the interval is the claim.")
    print(f"  ⚠ B/A IS NOT A RATE — different units, stated in the pre-registration.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "wall_record.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha, "prereg": PREREG,
        "ledger_entries": len(es), "rounds": len(rounds),
        "A_declaring_impossible": len(declared), "A_members": declared,
        "B_tight": len(T), "B_loose": len(L), "B_interval": [len(T), len(L)],
        "C_named": len(named),
        "tight_members": [{"id": e["id"], "title": e["title"]} for e in T],
        "magnitude_inside": inside, "directional_holds": directional,
        "check260": ("R658's NEXT said `d` IS a for-loop variable -- bound by For ONLY in 14 of "
                     "75, with 23 bound by Assign and no For at all. And it said I had declared "
                     "such a limit TWICE; ledger entry 358 is titled 'The fourth false wall' and "
                     "369 records 'two more walls fell', so the number was in my own ledger, in "
                     "a title, and I wrote 'twice'."),
        "impossible": ("'this entry overturns a wall' is a judgement about prose and no pattern "
                       "decides it; two patterns of different tightness are run and the INTERVAL "
                       "is the result. Collapsing to a point would be the failure this round is "
                       "about."),
    }, indent=2))
    print(f"\n  wrote {out / 'wall_record.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
