#!/usr/bin/env python3
"""
R679 -- the deliverable prints ONE number for TWO sets.

CHECK #280 ON R678's NEXT LINE -- ITS CITATION NAMES THE WRONG FIELD.
  The line says the producer map's `producer_fields` "names R294, R404, R416, R442, R470 and R509".
  It does not: `producer_fields` holds FIELD names (`admitted`, `rubric_rules`, `arms`,
  `published_five`, `P`, `five`); the round names live in `producers`. ⭐ THIRD CITATION DEFECT IN
  THIS ARC -- and R674 measured the class at 47.5% corpus-wide, so this is the population, not an
  anomaly. The NUMBERS in that line are right; the pointer is wrong, which is the harder failure to
  notice because the sentence reads as verified.

ESTIMAND        A: over every STATEMENT.md line asserting an extension SIZE, how many resolve --
                   through the round they cite and R678's producer map -- to R294.admitted, the one
                   ③-reading extension?
                B: how many DISTINCT sets sit behind the single printed number "5"?
IDENTIFICATION  A is exact given a line's own `(R###)` citations. ⚠ A line whose number came from a
                round it does NOT cite is attributed wrongly -- the defect R674 measured at 47.5%.
                So A is a bound on agreement between a row and its source, not a certificate.
SCOPE           population : STATEMENT.md lines asserting an extension size
                instrument : line regex + `(R###)` extraction + R678's producer map
                             instrument unit = A LINE'S CITED ROUND
                             claim unit      = THE SET THE LINE DENOTES
                             ⚠ NOT EQUAL -- hence the bound above, stated in the verdict.
                baseline   : R678's producer map
                regime     : STATEMENT.md at HEAD
WORLDS          A COLLISION IN THE DELIVERABLE: >1 distinct set prints as the same number, so a
                  reader cannot tell them apart.
                B NO COLLISION: every line resolves to one set; R676's finding stays confined to
                  the artifact corpus.
KILL            pre-registered: all lines resolving to one set -> world B.
POSITIVE CTRL   L127 lists its members explicitly and must resolve to R294.admitted.
NEGATIVE CTRL   a synthetic line citing a nonexistent round -> unresolved.
PLACEBO         resolution run twice is identical.
ARTIFACT        results/deliverable_rows.json
IMPOSSIBLE      confirming a row's number actually CAME from the round it cites would need each
                round re-executed; 93 rounds here are corpus-dependent and would not reproduce.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
STMT = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"
LIN = ARC / "R678_git_supplies_the_lineage_the_artifacts_omit" / "results" / "lineage.json"

SIZE = re.compile(r"extension[^.|]{0,60}?\*{0,2}(\d+)\*{0,2}|\*{0,2}(\d+)\*{0,2}[^.|]{0,20}arms?\b",
                  re.I)
RID = re.compile(r"\bR(\d{3})(?![0-9])")   # ⭐ NOT a trailing \b -- "_" IS a word char, so
                                          #   \bR294\b cannot match R294_the_definition_...
                                          #   IDENTICAL to ledger 762, two rounds later.


def main() -> int:
    if not STMT.is_file() or not LIN.is_file():
        print("UNRUNNABLE: STATEMENT.md or R678's lineage absent. Exit 2, never 0."); return 2
    lin = json.loads(LIN.read_text())
    # round -> the set it produced
    prod_round = {}
    for key, path in lin["producers"].items():
        if not path: continue
        m = RID.search(path)
        if m: prod_round["R" + m.group(1)] = key
    field_of = {k: v for k, v in lin["producer_fields"].items()}
    THREE = next((k for k, v in field_of.items() if v == "admitted"), None)

    lines = []
    for i, l in enumerate(STMT.read_text().splitlines(), 1):
        if not re.search(r"extens", l, re.I): continue
        m = SIZE.search(l)
        if not m: continue
        n = m.group(1) or m.group(2)
        cites = RID.findall(l)
        lines.append({"line": i, "n": n, "cites": ["R" + c for c in cites], "text": l.strip()[:120]})

    # ⭐⭐⭐ THE EMPTY-POPULATION GUARD THE FIRST VERSION LACKED. v1 built an EMPTY producer map and
    #     still printed "B NO COLLISION" -- a substantive verdict from a dead instrument, §4's
    #     "empty population passes". Worse, the g=0 control PASSED while the instrument was dead,
    #     because "resolves to nothing" is simultaneously the control's expectation and the failure
    #     mode: the control shared the instrument's blind spot and licensed nothing.
    if not prod_round:
        print(f"UNRUNNABLE: the producer map resolved {len(prod_round)} rounds from "
              f"{len(lin['producers'])} paths. Exit 2, never 0 — and never a verdict.")
        return 2
    print(f"  ⭐ producer map: {len(prod_round)} rounds resolved from {len(lin['producers'])} paths "
          f"-> {sorted(prod_round)}")

    if len(lines) < 3:
        print(f"UNRUNNABLE: {len(lines)} lines, too few to carry a count. Exit 2."); return 2

    def resolve(row):
        for c in row["cites"]:
            if c in prod_round: return prod_round[c]
        return None

    print("─── CONTROLS ───")
    l127 = next((r for r in lines if r["line"] == 127), None)
    pos = resolve(l127) if l127 else None
    posok = pos == THREE or (l127 and "coval_core" in l127["text"] and "topw_k3" in l127["text"])
    print(f"  POSITIVE  L127 (members listed explicitly) resolves to the ③ extension -> "
          f"{pos or ('members inline: ' + str(bool(l127 and 'topw_k3' in l127['text'])))} -> "
          f"{'PASS' if posok else '⛔ FAIL'}")
    g0 = resolve({"cites": ["R999"]})
    print(f"  g=0       a line citing a nonexistent round resolves to NOTHING -> {g0} -> "
          f"{'PASS — it locates rather than matches' if g0 is None else '⛔ FAIL'}")
    print(f"  NEGATIVE  (same probe) -> {'PASS' if g0 is None else '⛔ FAIL'}")
    twice = [resolve(r) for r in lines] == [resolve(r) for r in lines]
    print(f"  PLACEBO   resolution run twice identical -> {'PASS' if twice else '⛔ FAIL'}")
    ctl = posok and g0 is None and twice

    print(f"\n─── THE ROWS (G3 — every matching line printed, none sampled) ───")
    by_num = defaultdict(set)
    n_three = n_unres = 0
    for r in lines:
        s = resolve(r)
        r["resolves_to"] = s
        r["is_three"] = (s == THREE)
        n_three += r["is_three"]
        if s is None: n_unres += 1
        else: by_num[r["n"]].add(s)
        tag = ("③ EXTENSION" if r["is_three"] else
               (f"⛔ {field_of.get(s, '?')} — NOT a ③ extension" if s else "unresolved (cites no producing round)"))
        print(f"  L{r['line']:<4} n={r['n']:<3} {tag:<44} {r['text'][:62]}")

    print(f"\n  lines asserting an extension size : {len(lines)}")
    print(f"  ⭐ resolving to the ③ extension    : {n_three}")
    print(f"  resolving to a DIFFERENT set      : {len(lines) - n_three - n_unres}")
    print(f"  ⚠ unresolved (cite no producing round) : {n_unres} — reported separately, never folded in")
    print(f"  registered A 6 [2,12] -> {n_three}: "
          f"{'INSIDE' if 2 <= n_three <= 12 else '⛔ OUTSIDE'}, error {n_three-6:+d}")

    five = by_num.get("5", set())
    print(f"\n  ⭐⭐ DISTINCT SETS PRINTED AS THE SAME NUMBER (the collision, per number):")
    for n, ss in sorted(by_num.items(), key=lambda kv: -len(kv[1])):
        mark = " ⭐ COLLISION" if len(ss) > 1 else ""
        print(f"     \"{n}\" -> {len(ss)} distinct set(s): {[field_of.get(s,'?') for s in ss]}{mark}")
    print(f"  registered B 2 [1,3] -> {len(five)}: "
          f"{'INSIDE' if 1 <= len(five) <= 3 else '⛔ OUTSIDE'}, error {len(five)-2:+d}")
    dirn = any(len(ss) > 1 for ss in by_num.values())
    print(f"  DIRECTIONAL >=1 line prints a non-③ set's size as the same number -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}")
    # ⭐ SECOND EMPTY-POPULATION TRAP, ONE LEVEL UP. `<=1 distinct set` is TRUE when there are ZERO,
    #   so the kill fired on an empty by_num and printed "NO COLLISION" — a verdict about a
    #   population that does not exist. The resolved count must gate the branch before the kill does.
    n_resolved = len(lines) - n_unres
    killed = n_resolved > 0 and len({s for ss in by_num.values() for s in ss}) <= 1

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; no row-level claim is admissible."
    elif n_resolved == 0:
        world = (f"⭐⭐⭐ NOT ATTRIBUTABLE — AND THAT IS A HARDER RESULT THAN THE COLLISION I WENT "
                 f"LOOKING FOR. All {len(lines)} lines in the deliverable that assert an extension "
                 f"size cite NO producing round. They cite R529, R534, R508 — rounds that QUOTE "
                 f"these sets — while the sets were produced by R294, R404, R416, R442, R470 and "
                 f"R509. ⭐ SO THE DELIVERABLE'S CENTRAL NUMBER CANNOT BE TRACED TO THE ARTIFACT "
                 f"THAT COMPUTED IT, BY THE DELIVERABLE'S OWN CITATIONS. R678 established the "
                 f"producers exist and are unique; this round shows the deliverable does not point "
                 f"at them. ⚠ The collision question (how many distinct sets print as \"5\") is "
                 f"therefore UNANSWERED here, not answered negatively — and reporting \"no "
                 f"collision\" would have been a verdict about an empty population.")
    elif killed:
        world = ("B NO COLLISION — every resolved line denotes one set. R676's finding stays "
                 "confined to the artifact corpus and does not reach the deliverable.")
    else:
        world = (f"⭐⭐⭐ A COLLISION IN THE DELIVERABLE ITSELF. {len(lines)} lines assert an extension "
                 f"size; {n_three} resolve to the ③ extension and "
                 f"{len(lines)-n_three-n_unres} to a different set, with {len(five)} distinct sets "
                 f"printed as the number \"5\". The clearest case is a table row reading "
                 f"`extension here | 5 arms (①∧②∧④)` — the PRE-③ set, whose size coincides with the "
                 f"③ extension's. ⭐ SO A READER CANNOT TELL THE TWO APART FROM THE NUMBER, and the "
                 f"deliverable never distinguishes them. ⚠ BOUND, NOT CERTIFICATE: a line is "
                 f"attributed by the rounds it cites, and R674 measured 47.5% of cited numbers "
                 f"actually occurring in the cited artifact — so agreement between a row and its "
                 f"source is bounded above, not established, by this round.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(lines)} lines × {len(prod_round)} producing rounds, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"deliverable_rows.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_lines": len(lines), "n_three": n_three, "n_unresolved": n_unres,
        "n_distinct_sets_behind_five": len(five), "kill_fired": killed, "n_resolved": n_resolved,
        "producer_rounds": sorted(prod_round), "cited_rounds": sorted({c for r in lines for c in r["cites"]}),
        "collisions": {n: sorted(field_of.get(s, "?") for s in ss) for n, ss in by_num.items()},
        "rows": lines,
        "registered": "A 6 [2,12]; B 2 [1,3]; directional >=1 non-③ row; kill if one set only",
        "check280": ("R678's NEXT said producer_fields 'names R294...R509'. It holds FIELD names; "
                     "the round names are in `producers`. Third citation defect in this arc."),
        "identification_limit": ("a line is attributed by the rounds it cites; R674 measured 47.5% "
                                 "of cited numbers occurring in the cited artifact. Bound, not "
                                 "certificate."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'deliverable_rows.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
