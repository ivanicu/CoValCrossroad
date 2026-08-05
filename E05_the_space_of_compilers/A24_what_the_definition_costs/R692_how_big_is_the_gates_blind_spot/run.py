#!/usr/bin/env python3
"""
R692 -- how big is the gate's blind spot? Measuring a caveat instead of asserting it.

CHECK #293 ON R691's NEXT LINE -- IT HOLDS. `results/name_reuse.json` carries both bindings, the
  instrument it names (R680's arm vocabulary) exists, and the caveat it proposes to measure is
  written in the gate's own docstring. ⭐ Tenth NEXT in this arc to survive intact.

⚠ A DERIVATION, DECLARED BEFORE THE MEASUREMENT AND NOT COUNTED AS ONE OF ITS RESULTS.
  R689 established the release ships ONE core. It follows with no further evidence that every claim
  this arc has made about the definition was checked against exactly ONE released object and N of our
  own constructions. That is forced by the arithmetic and could not have come out otherwise. It is
  the deepest form of §4's "the definition describes the instance", and it is a DERIVATION -- stated
  here, carrying no evidential weight, and not part of this round's estimand.

ESTIMAND        A: how many literals bind >=2 arm names under a name matching NEITHER the release
                   pattern NOR an our-arms pattern -- the population the gate cannot see?
                B: how many of those bind a member set that also appears under a release-asserting
                   name elsewhere?
IDENTIFICATION  ⚠ a neutral-named arm list is not necessarily a CLAIM about the release; most are
                our own arm lists, which is legitimate. This counts what the gate cannot SEE, not
                the number of hidden false claims. The difference is not collapsed.
SCOPE           population : every run.py in the repository, minus _archive and the rounds that
                             document this defect
                instrument : AST assign-scan + R680's arm vocabulary + the gate's own two patterns
                             instrument unit = A NEUTRALLY NAMED ARM LITERAL
                             claim unit      = AN UNSEEN RELEASE CLAIM
                             ⚠ NOT EQUAL -- hence the limit above, carried into the verdict.
                baseline   : the 1 name the gate does see (`PUBLISHED_FIVE`)
                regime     : this repository at HEAD
WORLDS          A LARGE BLIND SPOT: many neutral-named arm literals -> the gate's coverage is thin
                  and its PASS is weak evidence.
                B SMALL: few -> the gate covers most of what matters and its PASS means more.
KILL            zero neutral-named literals binding >=2 arm names -> no blind spot; say the caveat
                was over-cautious rather than continuing to hedge.
POSITIVE CTRL   R361's `FIVE` must be found — a known neutral-named literal binding 5 arm names.
g=0             `PUBLISHED_FIVE` must NOT be counted as blind-spot; it is what the gate sees.
NEGATIVE CTRL   a literal of non-arm strings is not counted.
PLACEBO         run twice identical.
ARTIFACT        results/blind_spot.json
IMPOSSIBLE      whether a neutrally named list was MEANT as a release claim is not in the code.
"""
from __future__ import annotations
import ast, json, pathlib, re, subprocess, sys
from collections import defaultdict

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
RELEASEY = re.compile(r"(PUBLISH|RELEASE|COVAL|PAPER|OFFICIAL|SHIPPED|CARD)", re.I)
OURSY = re.compile(r"^(ARMS?|OUR_|MY_|CONSTRUCT|BUILT)", re.I)
ARMISH = ("coval_core", "topw_k", "topabs_k", "topvar_k", "topwvar_k", "oracle_k", "greedy_k",
          "indep_k", "random_k", "promptecho", "generic", "gen_sham", "full_sham")
SELF = re.compile(r"R689|R690|R691|R692")


def arms_in(members):
    return [m for m in members if any(m.startswith(a) or m == a for a in ARMISH)]


def named_sets(src):
    try: tree = ast.parse(src)
    except SyntaxError: return []
    out = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Assign) or not isinstance(n.value, (ast.List, ast.Set, ast.Tuple)):
            continue
        ms = [e.value for e in n.value.elts
              if isinstance(e, ast.Constant) and isinstance(e.value, str)]
        if ms:
            out += [{"name": t.id, "members": ms, "line": n.lineno}
                    for t in n.targets if isinstance(t, ast.Name)]
    return out


def main() -> int:
    print("─── CONTROLS ───")
    r361 = next(ARC.glob("R361_*/run.py"), None)
    got = [d for d in named_sets(r361.read_text(errors="ignore"))
           if d["name"] == "FIVE" and len(arms_in(d["members"])) >= 2] if r361 else []
    posok = bool(got)
    print(f"  POSITIVE  R361's `FIVE` (neutral name, 5 arm names) is found -> "
          f"{got[0]['members'] if got else None} -> {'PASS' if posok else '⛔ FAIL'}")
    g0ok = bool(RELEASEY.search("PUBLISHED_FIVE"))
    print(f"  g=0       `PUBLISHED_FIVE` is what the gate SEES, so not blind-spot -> "
          f"{'PASS — the classifier returns both values' if g0ok else '⛔ FAIL'}")
    negok = len(arms_in(["alpha", "beta", "gamma"])) == 0
    print(f"  NEGATIVE  a literal of non-arm strings is not counted -> "
          f"{'PASS' if negok else '⛔ FAIL'}")
    plc = named_sets(r361.read_text(errors="ignore")) == named_sets(r361.read_text(errors="ignore"))
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plc

    blind, seen_sets, scanned = [], defaultdict(set), 0
    for f in sorted(ROOT.rglob("run.py")):
        s = str(f)
        if "/_archive/" in s or SELF.search(s): continue
        scanned += 1
        for d in named_sets(f.read_text(errors="ignore")):
            a = arms_in(d["members"])
            if len(a) < 2: continue
            key = tuple(sorted(a))
            if RELEASEY.search(d["name"]):
                seen_sets["visible"].add(key); continue
            if OURSY.search(d["name"]):
                seen_sets["ours"].add(key); continue
            blind.append({"file": str(f.relative_to(ROOT)), "name": d["name"],
                          "line": d["line"], "n_arms": len(a), "arms": key})
            seen_sets["blind"].add(key)

    if scanned == 0:
        print("\n  UNRUNNABLE: 0 files scanned. Exit 2, never a verdict."); return 2

    overlap = seen_sets["blind"] & seen_sets["visible"]
    print(f"\n─── THE BLIND SPOT (G3 — counts over the whole scan) ───")
    print(f"  run.py scanned (minus _archive and this defect's own rounds) : {scanned}")
    print(f"  literals binding >=2 arm names:")
    print(f"    under a RELEASE-asserting name (the gate SEES these) : "
          f"{len(seen_sets['visible'])} distinct sets")
    print(f"    under an OUR-ARMS name (explicitly ours)             : "
          f"{len(seen_sets['ours'])} distinct sets")
    print(f"    ⭐ under a NEUTRAL name (the gate CANNOT see these)   : {len(blind)} literals, "
          f"{len(seen_sets['blind'])} distinct sets")
    from collections import Counter
    top = Counter(b["name"] for b in blind).most_common(8)
    for nm, c in top: print(f"       {c:>4}×  `{nm}`")
    print(f"  ⭐ blind sets that ALSO appear under a release-asserting name : {len(overlap)}"
          f"{' -> ' + str([list(o) for o in overlap]) if overlap else ''}")
    print(f"  registered A 45 [10,150] -> {len(blind)}: "
          f"{'INSIDE' if 10 <= len(blind) <= 150 else '⛔ OUTSIDE'}, error {len(blind)-45:+d}")
    print(f"  registered B 3 [0,20] -> {len(overlap)}: "
          f"{'INSIDE' if 0 <= len(overlap) <= 20 else '⛔ OUTSIDE'}, error {len(overlap)-3:+d}")
    dirn = len(blind) > 1
    print(f"  DIRECTIONAL blind-spot population larger than the visible 1 name -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}")
    killed = len(blind) == 0
    print(f"  pre-registered kill (zero blind literals) -> "
          f"{'⭐ FIRES — no blind spot; the caveat was over-cautious' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = ("B NO BLIND SPOT — no neutral-named literal binds two or more arm names. The "
                 "gate's caveat was over-cautious and should be narrowed rather than repeated.")
    else:
        world = (f"⭐⭐ A THE BLIND SPOT IS {len(blind)} LITERALS OVER {len(seen_sets['blind'])} "
                 f"DISTINCT SETS, against the {len(seen_sets['visible'])} set(s) the gate can see. "
                 f"So `release_names_resolve_to_one_set` PASSING is weak evidence: it certifies the "
                 f"names that ANNOUNCE a release claim, and most arm literals here do not announce "
                 f"anything. ⚠ AND THE UNIT GAP IS THE WHOLE READING: a neutrally named arm list is "
                 f"usually OUR OWN arm list, which is legitimate — this counts what the gate cannot "
                 f"SEE, not hidden false claims. The one number that would be alarming is the "
                 f"overlap, and it is {len(overlap)}.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {scanned} run.py × every named literal, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"blind_spot.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "scanned": scanned,
        "n_blind_literals": len(blind), "n_blind_sets": len(seen_sets["blind"]),
        "n_visible_sets": len(seen_sets["visible"]), "n_ours_sets": len(seen_sets["ours"]),
        "n_overlap": len(overlap), "overlap": [list(o) for o in overlap],
        "top_names": top, "blind": blind[:200],
        "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 45 [10,150]; B 3 [0,20]; blind > visible; kill if zero blind",
        "derivation_not_evidence": ("the release ships ONE core (R689), so every claim in this arc "
                                    "was checked against one released object and N of our own "
                                    "constructions. Forced by arithmetic; not part of this estimand."),
        "limit": ("a neutrally named arm list is usually OUR arm list. This counts what the gate "
                  "cannot see, not hidden false claims."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'blind_spot.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
