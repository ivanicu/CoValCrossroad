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
import subprocess
from pathlib import Path

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
    for d in sorted((_ROOT / a.rounds).glob("r*/")):
        run = d / "run.py"
        if not run.exists():
            continue
        rel_run = str(run.relative_to(_ROOT))
        res_dir = d / "results"
        res = sorted(res_dir.glob("*")) if res_dir.exists() else []
        res = [f for f in res if f.is_file()]
        if not res:
            no_results.append(d.name)
            continue
        code_t = last_commit_ts(rel_run)
        res_t = max((last_commit_ts(str(f.relative_to(_ROOT))) or 0) for f in res)
        if code_t is None:
            untracked.append(d.name)
            continue
        if res_t == 0:
            untracked.append(f"{d.name} (results not committed)")
            continue
        rows.append((d.name, code_t, res_t, code_t > res_t))

    print(f"{'round':34s} {'code':>6} {'results':>8}  status")
    stale = []
    for name, ct, rt, bad in rows:
        import datetime as _dt
        cs = _dt.datetime.fromtimestamp(ct).strftime("%d/%H:%M")
        rs = _dt.datetime.fromtimestamp(rt).strftime("%d/%H:%M")
        if bad:
            stale.append(name)
        print(f"{name:34s} {cs:>6} {rs:>8}  {'CODE CHANGED AFTER RESULTS' if bad else 'ok'}")

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
