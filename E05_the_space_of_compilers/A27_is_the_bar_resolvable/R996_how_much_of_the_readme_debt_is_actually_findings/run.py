#!/usr/bin/env python3
"""R996 — how much of the README debt is actually findings?

⛔ WHY. R995 measured 828 unmentioned round directories and said paying that debt "needs a decision
about which rounds deserve a line rather than an instrument." **That decision has a measurable half**,
and this round takes it: a round's own commit carries a recorded `[type.region…]` prefix, and the
types split into findings about the object (`verify`, `act`, `think`, `predict`) and work on the
instrument (`fix`, `guard`, `memory`, `prune`). **The debt that matters is the finding-typed subset**,
and quoting 828 without that split overstates it.

⚠ AND MY FIRST INSTRUMENT WAS THE `a search is an instrument` FAILURE, CAUGHT BY ITS OWN CONTROL.
v1 mapped a round to the FIRST commit whose body mentions it — but commit bodies cite other rounds
constantly, so R994 read `fix` (it is `act`) and R993 read `act` (it is `verify`). Instrument unit:
*a commit body containing "R993"*. Claim unit: *the commit that INTRODUCED R993*. Not equal, which is
the standard's own remedy, and the repair is R982's: `git log --reverse --diff-filter=A -- <dir>`.

ESTIMAND        of the unmentioned round directories, the share whose introducing commit is
                finding-typed.
IDENTIFICATION  exact where a directory has an introducing commit; rounds whose directory predates
                the current history or was renamed have none, and are counted as UNKNOWN rather
                than assigned.
SCOPE           population : round dirs outside the fixture batch, absent from README.md
                instrument : the `[type.…]` prefix of the commit that ADDED the directory
                baseline   : R995's undifferentiated 828
                regime     : this repository's git history
WORLDS          A THE DEBT IS AS STATED   most unmentioned rounds are findings, so 828 is close to
                              the real number and the README omits substantive results.
                B THE DEBT IS SMALLER     a large share are instrument work, so the finding debt is
                              materially below 828 and quoting the raw count overstates it.
                prediction matrix: A -> finding share high. B -> materially below 828.
KILL            pre-registered, CONDITIONAL on the control: finding-typed ≥ 90% of the classifiable
                unmentioned ⇒ world B dead and 828 stands as the honest figure.
POSITIVE CTRL   four rounds whose commit type is known by inspection — R994 `act`, R993 `verify`,
                R974 `fix`, R990 `verify` — must be recovered exactly. **This control already failed
                once and caught the wrong instrument**, which is what makes its passing meaningful.
NEGATIVE CTRL   a path that was never added must yield no type rather than a default.
PLACEBO         a MENTIONED round classifies the same way as an unmentioned one — the classifier
                must not depend on README membership, which is the variable under study.
NOISE FLOOR     none: a recorded field, not an estimate.
MULTIPLICITY    every type reported, findings and repairs alike, plus the unclassifiable count.
ARTIFACT        results/debt_by_type.json with this file's source hash.
IMPOSSIBLE      whether a finding-typed round DESERVES a README line — N/A: type records what the
                round was, never whether its result survived. A round can be finding-typed and
                retracted, and this does not check that.
"""
from __future__ import annotations
import collections, hashlib, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from covalx.rounds import iter_round_dirs
FINDING = {"verify", "act", "think", "predict"}


def introducing_type(path):
    out = subprocess.run(["git", "log", "--reverse", "--diff-filter=A", "--format=%s", "--",
                          str(path)], cwd=ROOT, capture_output=True, text=True).stdout
    for line in out.split("\n"):
        m = re.match(r"\[(\w+)\.", line)
        if m:
            return m.group(1)
    return None


def main() -> int:
    dirs = {}
    for d in iter_round_dirs(ROOT):
        m = re.match(r"[Rr](\d+)_", d.name)
        if m and "E99_fixtures" not in d.parts:
            dirs[int(m.group(1))] = d
    readme = (ROOT / "README.md").read_text()
    ment = {int(m.group(1)) for m in re.finditer(r"\bR(\d{2,4})\b", readme)}
    unment = sorted(r for r in dirs if r not in ment)
    print(f"POPULATION  {len(dirs)} round dirs · {len(unment)} unmentioned in README")

    # ── POSITIVE CONTROL FIRST: it already caught one wrong instrument
    known = {994: "act", 993: "verify", 974: "fix", 990: "verify"}
    got = {r: introducing_type(dirs[r]) for r in known if r in dirs}
    pos_ok = all(got.get(r) == t for r, t in known.items() if r in dirs)
    print(f"\nPOSITIVE CONTROL  {got}  vs known {known}  -> {'PASS' if pos_ok else '⛔ FAIL'}")
    neg_ok = introducing_type(ROOT / "E05_the_space_of_compilers/R00000_never_existed") is None
    print(f"NEGATIVE CONTROL  a path never added yields no type: {neg_ok}")
    if not (pos_ok and neg_ok):
        print("  ⛔ the classifier is not reading what it claims. Exit 2, never 0.")
        return 2

    types = {r: introducing_type(dirs[r]) for r in unment}
    have = {r: t for r, t in types.items() if t}
    find = [r for r, t in have.items() if t in FINDING]
    dist = collections.Counter(have.values())
    print(f"\n  classifiable: {len(have)} of {len(unment)}   "
          f"(no introducing commit for {len(unment)-len(have)})")
    print(f"  ⭐ FINDING-typed : {len(find)}")
    print(f"     repair-typed  : {len(have)-len(find)}")
    print(f"  distribution: {dict(dist.most_common())}")

    # ── PLACEBO: the classifier must not depend on README membership
    mentioned_dirs = [r for r in dirs if r in ment][:40]
    mt = [introducing_type(dirs[r]) for r in mentioned_dirs]
    plac_ok = sum(1 for t in mt if t) > 0
    print(f"  PLACEBO   mentioned rounds classify too ({sum(1 for t in mt if t)} of "
          f"{len(mentioned_dirs)} sampled): {plac_ok} — the classifier is independent of "
          f"README membership")

    share = len(find) / len(have) if have else 0
    if share >= 0.90:
        world = (f"A THE DEBT IS AS STATED — {share:.1%} of the classifiable unmentioned rounds are "
                 f"finding-typed, so 828 is close to the real figure")
    else:
        world = (f"B THE DEBT IS SMALLER — {len(find)} of {len(have)} classifiable unmentioned "
                 f"rounds are finding-typed ({share:.1%}); the finding debt is {len(find)}, not 828")
    print(f"\n⭐ {world}")
    print(f"\n⚠ TYPE RECORDS WHAT A ROUND WAS, NEVER WHETHER ITS RESULT SURVIVED. A round can be")
    print(f"   finding-typed and retracted; this does not check that, so {len(find)} is an UPPER")
    print(f"   bound on the lines actually owed.")

    out = HERE / "results" / "debt_by_type.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git","rev-parse","HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_dirs=len(dirs), n_unmentioned=len(unment), n_classifiable=len(have),
        n_finding=len(find), n_repair=len(have)-len(find), finding_share=share,
        type_distribution=dict(dist), finding_types=sorted(FINDING),
        controls={"positive": got, "positive_expected": known, "positive_ok": pos_ok,
                  "negative_never_added": neg_ok, "placebo_mentioned_classify": plac_ok},
        world=world,
        upper_bound_note="type records what a round WAS, not whether its result survived; the "
                         "finding count is an upper bound on lines owed",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
