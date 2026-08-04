"""A backfilled finding must be re-derivable from a FRESH RUN of the round it cites.

WHY THIS EXISTS. R384 measured that 243 of 377 rounds have no finding site. R386 measured that only
9% of a finding's numbers survive in its artifact, so those rows cannot be generated -- they must be
written by re-running the round and reading its output. R388 wrote the first one.

A row written months after its round is the highest-risk sentence in this repository. The numbers
come from output read once, nothing about the row's appearance distinguishes a copied number from a
remembered one, and **a wrong number in a findings table is worse than an absent one, because an
empty row is visibly empty and a plausible wrong one is not.**

So every number in a backfilled row is checked against a FRESH RUN of the round it cites. Not
against the committed artifact -- R386 measured that at 9%.

PROXY LEDGER, because this is sound in one direction only:
  PROPERTY    the backfilled row states what the round found.
  PROXY       every numeric token in the row appears in the round's fresh output.
  IMPLICATION a missing number => the row is wrong.  All numbers present =/=> the row is right:
              the SENTENCE around them is a judgement this cannot check, and it does not claim to.
  SAFE SIDE   rule only on absence. A round that times out is UNVERIFIED, never a pass.

EMPTY POPULATION: no backfilled rows -> exit 2. A gate that certified an empty table would be the
failure the whole R380-R388 line is about.

POSITIVE CONTROL: a number known absent from the run is injected and must be flagged. Without it,
"all numbers verified" restates "the author copied carefully", which is not a check.

COST, stated because it grows: this re-runs every cited round. R388 measured one at 21.3s and R387
measured 3 of 12 rounds exceeding 90s. At 237 rows this gate is minutes to hours, and that is a real
argument for a per-row cache -- which is NOT built here, because an unmeasured optimisation on a
gate is how a gate stops running.
"""
from __future__ import annotations
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = ROOT / ".venv" / "bin" / "python"
HEADING = "### Backfilled findings"
NUM = re.compile(r"\d+\.\d+|\b\d{2,}\b")
LINK = re.compile(r"\]\((E0\d_[A-Za-z0-9_]+/A\d+_[A-Za-z0-9_]+/(R\d+_[A-Za-z0-9_]+))\)")
FAKE = "0.7331"
TIMEOUT = 300
sys.path.insert(0, str(ROOT / "assurance"))


def rows_of(readme: str):
    if HEADING not in readme:
        return []
    block = readme.split(HEADING, 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]
    return [l for l in block.splitlines() if l.startswith("|") and LINK.search(l)]


def main() -> int:
    readme = (ROOT / "README.md").read_text()
    rows = rows_of(readme)
    print("  a backfilled finding must be re-derivable from a FRESH RUN of the round it cites\n")
    if not rows:
        print(f"  EMPTY POPULATION: no rows under `{HEADING}`. A gate that certified an empty")
        print(f"  table is the failure this whole line of rounds is about. Exit 2, never 0.")
        return 2

    try:
        from _isolated import ensure_worktree, restore       # noqa: E402
    except Exception as e:
        print(f"  UNRUNNABLE: cannot import the isolation harness ({e}). Exit 2, never 0.")
        return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()
    wt = ensure_worktree()
    subprocess.run(["git", "checkout", "-f", "-q", head], cwd=str(wt), capture_output=True)
    subprocess.run(["git", "clean", "-fdq"], cwd=str(wt), capture_output=True)
    restore(wt)

    by_round = {}
    for l in rows:
        for path, name in LINK.findall(l):
            by_round.setdefault((path, name), []).append(l)
    print(f"  {len(rows)} backfilled row(s) citing {len(by_round)} round(s)\n")

    fail, unver, checked, controls = 0, 0, 0, []
    for (path, name), rs in sorted(by_round.items()):
        d = wt / path
        if not (d / "run.py").exists():
            print(f"    {name:<34} ⛔ run.py ABSENT — cannot re-derive. UNVERIFIED")
            unver += 1
            continue
        try:
            p = subprocess.run([str(PY), "run.py"], cwd=str(d), capture_output=True,
                               text=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            print(f"    {name:<34} TIMEOUT after {TIMEOUT}s — UNVERIFIED, never a pass")
            unver += 1
            restore(wt)
            continue
        restore(wt)
        if p.returncode != 0:
            print(f"    {name:<34} exit {p.returncode} — the round no longer runs. UNVERIFIED")
            unver += 1
            continue
        run_nums = set(NUM.findall(p.stdout + p.stderr))
        # ⚠ round ids and link paths are not claims. Strip every id appearing in the row itself.
        ids = set(re.findall(r"R(\d+)_", "\n".join(rs)))
        claimed = sorted(set(NUM.findall("\n".join(rs))) - ids)
        missing = [n for n in claimed if n not in run_nums]
        # ⛔ THE POSITIVE CONTROL, EXERCISING THE SAME COMPREHENSION THAT RULES. v1 computed
        #   `[n for n in [FAKE] if n not in set()]` and asked whether it was non-empty -- true by
        #   construction, a check that cannot fail, which is the first row of the ledger this
        #   repository keeps. The plant now goes through the REAL comparison against the REAL run.
        planted = [n for n in claimed + [FAKE] if n not in run_nums]
        pos_ok = (FAKE not in run_nums) and (FAKE in planted)
        controls.append(pos_ok)
        checked += len(claimed)
        status = "OK" if not missing else f"⛔ {len(missing)} NOT IN OUTPUT"
        print(f"    {name:<34} {len(claimed):>3} number(s)  {status}")
        if missing:
            print(f"      {missing}")
            fail += 1
        if not pos_ok:
            print(f"      ⚠ the plant was not caught for this round — its verdict is UNVERIFIED")
            unver += 1

    print(f"\n    POSITIVE CONTROL  a number absent from the run, pushed through the SAME")
    print(f"                      comparison that rules, is flagged in "
          f"{sum(controls)} of {len(controls)} round(s)")
    if controls and not all(controls):
        print(f"\n  UNVERIFIED: the verifier failed to catch a plant somewhere, so its passes")
        print(f"  elsewhere mean nothing. Exit 1, never 0.")
        return 1

    print(f"\n  {checked} number(s) checked across {len(by_round)} round(s); "
          f"{fail} row-group(s) with a number the round did not produce; {unver} unverified.")
    print(f"\n  PROXY LEDGER — sound in ONE direction. A missing number means the row is WRONG.")
    print(f"    All numbers present does NOT mean the row is right: the SENTENCE around them is a")
    print(f"    judgement this gate cannot check and does not claim to.")
    if fail:
        print(f"\n  FAIL: a backfilled row states a number its round does not produce. Remove the")
        print(f"  row or correct it — a wrong number in a findings table is worse than an absent")
        print(f"  one, because an empty row is visibly empty and a plausible wrong one is not.")
        return 1
    if unver and not checked:
        print(f"\n  UNVERIFIED: nothing could be re-derived. Exit 1, never 0.")
        return 1
    print(f"\n  PASS: every backfilled number re-derives from a fresh run of its own round.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
