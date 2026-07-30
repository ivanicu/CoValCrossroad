"""Does every committed result come from the version of the code that is committed beside it?

The question
------------
A results file can be stale in two ways, and this repository has produced both.

  1. the prose no longer matches the artifact
     -> assurance/readme_agrees_with_results.py

  2. the artifact no longer matches the CODE that sits next to it, because the
     round was patched after the result was written and never re-run
     -> this file

Case 2 is the more dangerous one. A reader who opens `run.py` and reads its
results directory reasonably assumes the second came from the first. Today alone
r39's `ll_cond`, r40's verdict logic and r38's variance estimate were all patched
after an earlier version had already produced output.

Why not mtime
-------------
The obvious check -- is run.py newer than results/*.json -- is wrong, and running
it flagged r08, r09, r10 and r11. All four were false positives: their last
content change is the commit that CREATED them, and `git add` set the file mtime
at commit time while the results had been produced during development minutes
earlier. Filesystem mtime measures when a byte was last written, not when the
logic last changed.

So compare COMMIT times of content changes instead, taken from git:

    code_t    last commit that changed run.py
    result_t  last commit that changed anything in results/

`code_t > result_t` means the round was edited and its results were not
regenerated in the same commit -- the case worth knowing about. Files not tracked
by git are reported separately rather than silently passing.

Not a gate
----------
Exit code is always 0. A round can legitimately be edited without re-running --
a docstring correction, a comment, a renamed output path -- and turning this into
a gate would push those edits toward not being made. It prints what to check.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

# A provisional run is not a result. Matching one WORD failed twice: once on
# case (a04_smoke.json, entry 71) and once on vocabulary (a06_dryrun.json,
# entry 75). Match the class, and prefer the results/_smoke/ directory rule,
# which does not depend on the name at all.
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip",
                         re.I)

_ROOT = Path(__file__).resolve().parents[1]


def last_commit_ts(path: str) -> int | None:
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%ct", "--", path],
            cwd=_ROOT, text=True, stderr=subprocess.DEVNULL).strip()
        return int(out) if out else None
    except Exception:
        return None


def changed_files(commit: str, path: str) -> list[str]:
    try:
        return subprocess.check_output(
            ["git", "show", "--name-only", "--format=", commit],
            cwd=_ROOT, text=True, stderr=subprocess.DEVNULL).split()
    except Exception:
        return []


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", default="rounds")
    a = ap.parse_args()

    rows, untracked, no_results = [], [], []
    for d in sorted((_ROOT / a.rounds).glob("*/r*/")):
        run = d / "run.py"
        if not run.exists():
            continue
        rel_run = str(run.relative_to(_ROOT))
        res_dir = d / "results"
        res = sorted(res_dir.rglob("*")) if res_dir.exists() else []
        res = [f for f in res if f.is_file()
               # SMOKE outputs are excluded everywhere else in this package and
               # were not excluded here, so a stray smoke file made a round look
               # stale. Archived directories likewise.
               and not PROVISIONAL.search(f.name)
               and not any(part.startswith("_") for part in f.parts)
               # MODEL WEIGHTS are frozen INPUTS, not conclusions. r08's gold
               # head is consumed by r12/r29/r41/r46/r47; re-fitting it would
               # invalidate every downstream number. Its .npz being older than
               # its run.py is the intended state, not staleness.
               and f.suffix != ".npz"]
        if not res:
            no_results.append(d.name)
            continue
        code_t = last_commit_ts(rel_run)
        # PER FILE, not max(). This line used to take the NEWEST result and
        # compare that to the code, so a round with one current file and four
        # stale ones passed. r28 writes five results -- one per metric -- and
        # four of them sat at 07-28 12:05-12:09 carrying a verdict the round had
        # since withdrawn, while r28_pearson.json was current. The round looked
        # clean and I quoted one of the stale cells in a retraction entry as
        # though it were the round's conclusion.
        #
        # A round has as many verdicts as it has results files, and staleness is
        # a property of each.
        per_file = {str(f.relative_to(_ROOT)): (last_commit_ts(str(f.relative_to(_ROOT))) or 0)
                    for f in res}
        res_t = max(per_file.values())
        oldest_t = min(per_file.values())
        stale_files = sorted(k for k, v in per_file.items() if v and code_t and v < code_t)
        if code_t is None:
            untracked.append(d.name)
            continue
        if res_t == 0:
            untracked.append(f"{d.name} (results not committed)")
            continue
        rows.append((d.name, code_t, res_t, bool(stale_files), stale_files, oldest_t))

    print(f"{'round':34s} {'code':>6} {'results':>8}  status")
    stale = []
    for name, ct, rt, bad, stale_files, oldest_t in rows:
        import datetime as _dt
        cs = _dt.datetime.fromtimestamp(ct).strftime("%d/%H:%M")
        rs = _dt.datetime.fromtimestamp(rt).strftime("%d/%H:%M")
        if bad:
            stale.append(name)
        note = "CODE CHANGED AFTER RESULTS" if bad else "ok"
        if bad and len(stale_files) < len([1 for _ in stale_files]) + 1:
            pass
        print(f"{name:34s} {cs:>6} {rs:>8}  {note}")
        # name the individual stale files: a round with 1 current result and 4
        # stale ones is the case this check used to miss entirely
        for f in stale_files:
            print(f"{'':34s} {'':6} {'':8}    stale cell -> {f}")

    if no_results:
        print(f"\n  no results directory (or non-json artifacts only): {no_results}")
        print("  -> r39 caches a .npz by design; this script globs all files, so a round "
              "listed\n     here genuinely has no artifact rather than one in another format.")
    if untracked:
        print(f"\n  untracked or uncommitted: {untracked}")

    # A NOTE MECHANISM, because the advice below used to ask for something the
    # script could not read.  A round may declare, in NO_RERUN.md beside its
    # run.py, why an edit could not have moved its numbers.  The note is
    # REPORTED, never silently honoured -- a stale round with a note is still
    # printed as stale, with its reason, so a reader judges the reason instead
    # of the script judging it for them.
    noted, unnoted = [], []
    for name in stale:
        n = _ROOT / "rounds" / name / "NO_RERUN.md"
        (noted if n.exists() else unnoted).append(name)

    print("\n  excluded from staleness: SMOKE outputs, archived (_*) directories, and")
    print("  .npz model weights, which are frozen INPUTS other rounds consume rather")
    print("  than conclusions this round asserts.")
    print(f"\n  rounds whose code changed after their results: {stale or 'none'}")
    for name in noted:
        first = (_ROOT / "rounds" / name / "NO_RERUN.md").read_text().strip().split("\n")
        why = next((l for l in first if l.strip() and not l.startswith("#")), "(empty)")
        print(f"    {name}: NOTE -> {why[:96]}")
    if unnoted:
        print(f"  WITHOUT a note: {unnoted}")
        print("  Each needs one of: a re-run, or a NO_RERUN.md beside its run.py saying "
              "why\n  the edit could not affect the numbers (docstring, comment, renamed "
              "path).")
    print("\n  Not a gate. A round can legitimately be edited without re-running, and making")
    print("  this fail a build would push those edits toward not being made at all.")


if __name__ == "__main__":
    main()
