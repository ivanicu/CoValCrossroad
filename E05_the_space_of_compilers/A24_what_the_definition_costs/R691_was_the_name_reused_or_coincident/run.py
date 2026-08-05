#!/usr/bin/env python3
"""
R691 -- was the name REUSED after retraction, or chosen independently? A build decision.

CHECK #292 ON R690's NEXT LINE -- IT HOLDS. `hits` is present and carries both bindings with their
  file and line, and the fork it names (reuse vs coincidence) has different builds behind it.
  ⭐ Ninth NEXT in this arc to survive intact.

ESTIMAND        A: which of R360's and R442's `PUBLISHED_FIVE` bindings was committed first?
                B: did any retraction-ledger entry about the published-five claim exist BEFORE the
                   second binding's commit?
                C: how far apart are they?
IDENTIFICATION  ⚠ the commit that first CONTAINS a binding is not necessarily the one that AUTHORED
                it; git records writes (R678's limit, restated because it applies here too).
SCOPE           population : 2 bindings + the retraction ledger's history
                instrument : git log --diff-filter=A over each round's run.py + ledger history
                             instrument unit = A COMMIT THAT FIRST CONTAINS A BINDING
                             claim unit      = THE ACT OF CHOOSING THE NAME
                             ⚠ NOT EQUAL — hence the write/author caveat, carried into the verdict.
                baseline   : R690's `hits`
                regime     : this repository's history
WORLDS          A REUSE AFTER RETRACTION: a ledger gate would have caught it -> build it.
                B INDEPENDENT COINCIDENCE: no retraction existed -> a ledger gate cannot help; the
                  remedy is a naming convention.
                C SAME COMMIT: one author, two meanings, at once -> neither remedy applies.
KILL            both bindings in one commit -> world C, build nothing on the ledger.
POSITIVE CTRL   a known-tracked file returns a commit date — git log is an instrument.
g=0             a nonexistent path returns NOTHING, not today's date.
NEGATIVE CTRL   a tracked file never containing the name returns no binding.
PLACEBO         run twice identical.
ARTIFACT        results/name_reuse.json
IMPOSSIBLE      whether the author of the second binding KNEW of the first is not in the repository.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
PRIOR = ARC / "R690_which_literals_assert_the_release" / "results" / "release_literals.json"


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def first_commit_containing(path: str, needle: str):
    """oldest commit whose version of `path` contains `needle`."""
    shas = git("log", "--reverse", "--format=%H", "--", path).split()
    for s in shas:
        blob = git("show", f"{s}:{path}")
        if needle in blob:
            return {"sha": s[:8], "date": git("show", "-s", "--format=%cI", s)}
    return None


def main() -> int:
    if not PRIOR.is_file():
        print("UNRUNNABLE: R690's artifact absent. Exit 2, never 0."); return 2
    hits = [h for h in json.loads(PRIOR.read_text())["hits"]
            if h["name"] == "PUBLISHED_FIVE"]
    if len(hits) < 2:
        print(f"UNRUNNABLE: {len(hits)} PUBLISHED_FIVE bindings. Exit 2."); return 2

    print("─── CONTROLS (git log is an instrument) ───")
    pc = first_commit_containing("RETRACTIONS.md", "##")
    posok = bool(pc and pc["date"])
    print(f"  POSITIVE  a known-tracked file returns a commit date -> "
          f"{pc['date'][:10] if pc else None} -> {'PASS' if posok else '⛔ FAIL'}")
    g0 = first_commit_containing("no/such/path.py", "x")
    print(f"  g=0       a nonexistent path returns NOTHING -> {g0} -> "
          f"{'PASS -- not a fabricated date' if g0 is None else chr(9940) + ' FAIL'}")
    neg = first_commit_containing("RETRACTIONS.md", "ZZQ_NO_SUCH_TOKEN")
    print(f"  NEGATIVE  a tracked file never containing the token -> {neg} -> "
          f"{'PASS' if neg is None else '⛔ FAIL'}")
    plc = first_commit_containing("RETRACTIONS.md", "##") == pc
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0 is None and neg is None and plc

    rows = []
    for h in hits:
        d = next(iter(ARC.glob(f"{h['round']}_*")), None)
        rel = str((d / "run.py").relative_to(ROOT)) if d else None
        c = first_commit_containing(rel, "PUBLISHED_FIVE") if rel else None
        rows.append({**h, "path": rel, "commit": c})
        print(f"\n  {h['round']:<7} {rel}")
        print(f"  {'':7} first commit containing the binding: "
              f"{c['sha'] if c else 'NOT FOUND'}  {c['date'][:19] if c else ''}")
        print(f"  {'':7} members: {h['members']}")

    dated = [r for r in rows if r["commit"]]
    if len(dated) < 2:
        print("\n  UNRUNNABLE: fewer than two bindings dated. Exit 2, never a verdict."); return 2
    dated.sort(key=lambda r: r["commit"]["date"])
    first, second = dated[0], dated[1]
    same = first["commit"]["sha"] == second["commit"]["sha"]

    from datetime import datetime
    dt = lambda s: datetime.fromisoformat(s)
    delta = dt(second["commit"]["date"]) - dt(first["commit"]["date"])
    gap = delta.days
    # ⭐ MY OWN UNIT WAS TOO COARSE FOR THE PHENOMENON. Registering the gap in DAYS cannot tell 0
    #   from 23 hours, and the observed gap is a same-day one. Reporting "0 days apart" reads as
    #   simultaneous. Hours are reported alongside, and the registered row is scored as the coarse
    #   thing it was.
    gap_h = delta.total_seconds() / 3600

    print(f"\n─── A · ORDER ───")
    print(f"  first  : {first['round']} @ {first['commit']['date'][:19]}")
    print(f"  second : {second['round']} @ {second['commit']['date'][:19]}")
    print(f"  ⭐ gap : {gap} days = {gap_h:.1f} HOURS   same commit: {same}")
    print(f"    ⚠ the registered interval was in DAYS and cannot distinguish 0 from 23 hours. The "
          f"phenomenon is same-day; my unit was coarser than the thing measured, and that is a "
          f"design defect in the registration rather than a result.")
    a_ok = first["round"] == "R360"
    print(f"  registered A (R360 predates R442) -> {a_ok}: {'HOLDS' if a_ok else '⛔ FAILS'}")
    print(f"  registered C 20 [0,90] days -> {gap}: "
          f"{'INSIDE' if 0 <= gap <= 90 else '⛔ OUTSIDE'}, error {gap-20:+d}")
    print(f"  DIRECTIONAL different commits -> {'HOLDS' if not same else '⛔ FAILS'}")

    print(f"\n─── B · WAS THE CLAIM RETRACTED BEFORE THE SECOND BINDING? ───")
    led_shas = git("log", "--reverse", "--format=%H%x1f%cI", "--", "RETRACTIONS.md").splitlines()
    prior_entry = None
    for line in led_shas:
        s, date = line.split("\x1f")
        if date >= second["commit"]["date"]: break
        blob = git("show", f"{s}:RETRACTIONS.md")
        if re.search(r"published[_ ]five|published five", blob, re.I):
            prior_entry = {"sha": s[:8], "date": date}
            break
    print(f"  ledger versions before the second binding : "
          f"{sum(1 for l in led_shas if l.split(chr(31))[1] < second['commit']['date'])}")
    print(f"  ⭐ a prior retraction mentioning the claim : "
          f"{prior_entry['sha'] + ' @ ' + prior_entry['date'][:19] if prior_entry else 'NONE'}")
    b_ok = prior_entry is None
    print(f"  registered B (no prior entry) -> {b_ok}: {'HOLDS' if b_ok else '⛔ FAILS'}")
    killed = same

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = ("C SAME COMMIT — one author wrote both meanings at once. Neither a ledger gate nor "
                 "a naming convention addresses that; build nothing on either.")
    elif prior_entry:
        world = (f"⭐ A REUSE AFTER RETRACTION — the claim was already retracted at "
                 f"{prior_entry['date'][:10]} when {second['round']} bound the name again "
                 f"{gap} days after {first['round']}. ⭐ A GATE ON THE RETRACTION LEDGER WOULD HAVE "
                 f"CAUGHT IT and is worth building.")
    else:
        world = (f"⭐⭐ B INDEPENDENT COINCIDENCE — {first['round']} bound `PUBLISHED_FIVE` at "
                 f"{first['commit']['date'][:10]} and {second['round']} bound it to DIFFERENT members "
                 f"{gap_h:.1f} HOURS later, with NO retraction of the claim in the ledger at that time. "
                 f"⛔ SO A LEDGER GATE CANNOT HELP: there was nothing to warn against. The remedy is "
                 f"a NAMING rule — a name asserting a property of the release must resolve to one "
                 f"set — and that is a different build from the one R690's closing line implied. "
                 f"⚠ AND THE WRITE/AUTHOR LIMIT STANDS: git records the commit that first CONTAINS a "
                 f"binding, not the moment it was chosen.")
    print(f"  {world}")

    sha = git("rev-parse", "HEAD")
    print(f"\n  MULTIPLICITY: 2 bindings × (first-containing-commit + ledger history), 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"name_reuse.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "bindings": rows, "first": first["round"], "second": second["round"],
        "gap_days": gap, "gap_hours": gap_h, "same_commit": same, "prior_retraction": prior_entry,
        "kill_fired": killed,
        "registered": "A R360 first; B no prior ledger entry; C 20 [0,90] days; different commits",
        "limit": ("git records the commit that first CONTAINS a binding, not the act of choosing "
                  "the name (R678's write-not-author limit, and it applies here too)."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'name_reuse.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
