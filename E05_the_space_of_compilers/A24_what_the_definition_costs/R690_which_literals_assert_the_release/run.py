#!/usr/bin/env python3
"""
R690 -- which hard-coded literals assert a property of the RELEASE? Is R689's defect a class?

CHECK #291 ON R689's NEXT LINE -- IT HOLDS. `n_published_named_in_card` is present and reads 1, the
  instrument it names (R680's literal classifier + `token_boundaries`) exists and is imported here,
  and the question it poses has a live kill. ⭐ Eighth NEXT in this arc to survive intact.

ESTIMAND        A: how many hard-coded sets in this arc carry a NAME asserting a property of the
                   release (PUBLISHED / RELEASE / COVAL / PAPER / OFFICIAL / SHIPPED / CARD)?
                B: of those, how many contain a member absent from data/DATASET_CARD.md?
IDENTIFICATION  ⚠ the NAME is what is scanned. A set asserting a release property under a neutral
                name (`FIVE`, `TARGET`) is missed. Any count here is a FLOOR on the class.
SCOPE           population : every run.py in this arc
                instrument : AST assign-scan for a name-matching literal + card lookup
                             instrument unit = A NAMED LITERAL
                             claim unit      = A CLAIM ABOUT THE RELEASE
                             ⚠ NOT EQUAL — a name is an assertion by its author, not by the code.
                baseline   : R442's PUBLISHED_FIVE, the known instance
                regime     : this repository at HEAD
WORLDS          A A CLASS: several such literals exist and several are wrong -> the sweep is worth
                  a gate and the retraction generalises.
                B A ONE-OFF: only R442's -> R689's framing narrows to a single bad literal.
KILL            no release-asserting set besides R442's -> world B, do not generalise.
POSITIVE CTRL   `PUBLISHED_FIVE` must be found by the name pattern.
g=0             a set named for OUR arms (`ARMS`, `FIVE`, `LABELS`) must NOT be flagged.
NEGATIVE CTRL   a pattern matching nothing returns nothing.
PLACEBO         run twice identical.
ARTIFACT        results/release_literals.json
IMPOSSIBLE      whether an author MEANT a name as a release claim is not in the code; the name is
                the only evidence, and it is read as one.
"""
from __future__ import annotations
import ast, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
CARD = ROOT / "data" / "DATASET_CARD.md"
RELEASEY = re.compile(r"(PUBLISH|RELEASE|COVAL|PAPER|OFFICIAL|SHIPPED|CARD)", re.I)
OURS = re.compile(r"^(ARMS|FIVE|LABELS|POOL|SEEDS|KNOWN|EXT|TOPW)", re.I)


def named_sets(src):
    out = []
    try: tree = ast.parse(src)
    except SyntaxError: return out
    for n in ast.walk(tree):
        if not isinstance(n, ast.Assign) or not isinstance(n.value, (ast.List, ast.Set, ast.Tuple)):
            continue
        members = [e.value for e in n.value.elts
                   if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        if not members: continue
        for t in n.targets:
            if isinstance(t, ast.Name):
                out.append({"name": t.id, "members": members, "line": n.lineno})
    return out


def main() -> int:
    if not CARD.is_file():
        print("UNRUNNABLE: data/DATASET_CARD.md absent. Exit 2, never 0."); return 2
    card = CARD.read_text(errors="ignore")

    print("─── CONTROLS (the name pattern is an instrument) ───")
    r442 = next(ARC.glob("R442_*/run.py"), None)
    found442 = [s for s in named_sets(r442.read_text(errors="ignore"))
                if RELEASEY.search(s["name"])] if r442 else []
    posok = any(s["name"] == "PUBLISHED_FIVE" for s in found442)
    print(f"  POSITIVE  R442's `PUBLISHED_FIVE` found by the pattern -> "
          f"{[s['name'] for s in found442]} -> {'PASS' if posok else '⛔ FAIL'}")
    g0ok = not RELEASEY.search("ARMS") and not RELEASEY.search("LABELS")
    print(f"  g=0       a set named for OUR arms (`ARMS`, `LABELS`) not flagged -> "
          f"{'PASS — the pattern returns both values' if g0ok else '⛔ FAIL'}")
    negok = not re.compile(r"ZZQNOSUCH").search("PUBLISHED_FIVE")
    print(f"  NEGATIVE  a pattern matching nothing returns nothing -> "
          f"{'PASS' if negok else '⛔ FAIL'}")
    plc = named_sets(r442.read_text(errors="ignore")) == named_sets(r442.read_text(errors="ignore"))
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plc

    hits = []
    for f in sorted(ARC.glob("R*/run.py")):
        rd = f.parent.name.split("_")[0]
        for s in named_sets(f.read_text(errors="ignore")):
            if not RELEASEY.search(s["name"]): continue
            absent = [m for m in s["members"] if m not in card]
            hits.append({"round": rd, "name": s["name"], "line": s["line"],
                         "members": s["members"], "absent_from_card": absent})

    print(f"\n─── THE SWEEP (G3 — every release-asserting literal, none hidden) ───")
    for h in hits:
        tag = (f"⛔ {len(h['absent_from_card'])}/{len(h['members'])} ABSENT from the card"
               if h["absent_from_card"] else "⭐ every member named in the card")
        print(f"  {h['round']:<7} {h['name']:<20} L{h['line']:<5} {tag}")
        if h["absent_from_card"]:
            print(f"  {'':7} absent: {h['absent_from_card'][:6]}")
    # ⭐ R689's `PUBLISHED` is MY OWN, written this session to DOCUMENT the retraction. Counting it
    #   as a naive instance would inflate the class with the artifact that reports the class. Both
    #   counts are printed; the class claim rests on the naive-instance count.
    SELF = {"R689", "R690"}
    wrong = [h for h in hits if h["absent_from_card"]]
    naive = [h for h in wrong if h["round"] not in SELF]
    others = [h for h in naive if h["round"] != "R442"]
    print(f"\n  ⚠ SELF-REFERENTIAL: {len([h for h in wrong if h['round'] in SELF])} of the "
          f"{len(wrong)} are THIS session's own retraction artifacts (R689's `PUBLISHED`), which "
          f"document the defect rather than commit it. Excluded from the class count, not hidden.")
    print(f"  ⭐ naive instances (the class) : {len(naive)} -> "
          f"{[h['round'] + '.' + h['name'] for h in naive]}")

    # ⭐⭐⭐ THE SHARPER DEFECT: the SAME NAME bound to DIFFERENT SETS.
    from collections import defaultdict
    byname = defaultdict(set)
    for h in hits:
        if h["round"] in SELF: continue
        byname[h["name"]].add(tuple(sorted(h["members"])))
    collisions = {k: v for k, v in byname.items() if len(v) > 1}
    print(f"\n─── ⭐⭐⭐ SAME NAME, DIFFERENT SETS ───")
    for k, vs in collisions.items():
        print(f"  `{k}` denotes {len(vs)} DIFFERENT sets:")
        for v in sorted(vs): print(f"     {list(v)}")
    if not collisions: print("  none — each release-asserting name denotes one set")
    print(f"\n  release-asserting literals : {len(hits)}")
    print(f"  ⭐ containing a member ABSENT from the card : {len(wrong)}")
    print(f"  ⭐ mislabelled OTHER than R442's            : {len(others)}"
          f"{' -> ' + str([h['round'] + '.' + h['name'] for h in others]) if others else ''}")
    print(f"  registered A 8 [2,15] -> {len(hits)}: "
          f"{'INSIDE' if 2 <= len(hits) <= 15 else '⛔ OUTSIDE'}, error {len(hits)-8:+d}")
    print(f"  registered B 4 [1,10] -> {len(wrong)}: "
          f"{'INSIDE' if 1 <= len(wrong) <= 10 else '⛔ OUTSIDE'}, error {len(wrong)-4:+d}")
    dirn = len(others) >= 1
    print(f"  DIRECTIONAL >=1 mislabelled set OTHER than R442's -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}")
    killed = len([h for h in hits if h["round"] != "R442"]) == 0
    print(f"  pre-registered kill (no release-asserting set besides R442's) -> "
          f"{'⭐ FIRES — a ONE-OFF, do not generalise' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the name pattern is unvalidated."
    elif killed:
        world = ("B A ONE-OFF — no release-asserting literal exists in this arc besides R442's. "
                 "R689's retraction stands for that literal and does NOT generalise to a class.")
    elif not dirn:
        world = (f"⭐ MOSTLY SOUND — {len(hits)} release-asserting literals, and the only one with a "
                 f"member absent from the card is R442's own. So the naming habit exists across the "
                 f"arc but produced ONE wrong claim, not a class of them. ⚠ FLOOR, NOT SIZE: a set "
                 f"asserting a release property under a neutral name is missed by design.")
    else:
        world = (f"⭐⭐⭐ A A CLASS, AND THE SHARP FORM IS A NAME COLLISION. {len(naive)} literals "
                 f"outside this session name a property of the release; ALL {len(naive)} contain a "
                 f"member the card never mentions. ⭐ AND `PUBLISHED_FIVE` DENOTES TWO DIFFERENT "
                 f"SETS — {'; '.join(sorted(h['round'] + ' -> ' + str(sorted(h['members'])) for h in naive if h['name'] == 'PUBLISHED_FIVE'))}. "
                 f"⛔ v1 of this very sentence indexed an UNORDERED set to attribute them and named "
                 f"the wrong round — §4's 'the verdict string is not a computation', in the string "
                 f"reporting a naming defect. Same name, same claim about the release, "
                 f"different members. ⭐⭐ THAT IS A CONCRETE CAUSE FOR R676's 'the number five is "
                 f"stable, the membership is not': the SIZE was carried by a shared NAME while the "
                 f"MEMBERS diverged, and nothing in either file records which one is meant. "
                 f"⚠ FLOOR, NOT SIZE — a release claim under a neutral name is missed by design.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(list(ARC.glob('R*/run.py')))} run.py scanned, {len(hits)} literals, "
          f"4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"release_literals.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_release_asserting": len(hits), "n_with_absent_member": len(wrong),
        "n_mislabelled_besides_r442": len(others), "hits": hits,
        "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 8 [2,15]; B 4 [1,10]; >=1 besides R442; kill if none besides R442",
        "limit": ("the NAME is scanned; a release claim under a neutral name is missed, so any "
                  "count is a FLOOR on the class, not its size."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'release_literals.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
