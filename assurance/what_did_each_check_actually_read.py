#!/usr/bin/env python3
"""assurance/what_did_each_check_actually_read.py — a passing check that opened nothing is silence.

WHY. Twice today a check exited cleanly having examined NOTHING. `DEFECTS.py` printed
*"0/0 checks came back clean"* for a day because the E/A/R migration moved the rounds out from
under its path, and the string is success-shaped. That is `realstat §4 · empty population passes`,
and the only reason it surfaced is that its artifact shrank when I ran it.

**19 checks in this directory currently exit 0.** The question this round asks of every one of
them is the question that caught the other two: *did it pass, or did it examine nothing?*

⚠ THE UNIT PROBLEM, AND WHY THIS DOES NOT PARSE STDOUT. Every check prints its population
differently — "checks", "rounds", "files", "items", or not at all — so a regex over stdout
measures MY VOCABULARY, not the check's population. It would also be a search instrument with no
positive control, which this project has now been burned by three times.

So the population is measured at the only place it is unambiguous: **the files the process
actually opened.** `sys.addaudithook` sees every `open()` in the child, including inside library
code, and cannot be fooled by a check that computes from an empty list without saying so. The unit
of the instrument (`repo files opened`) and the unit of the claim (`the check examined project
data`) are then the same string, which is the remedy the search row demands.

ESTIMAND      per check: the number of DISTINCT repo files it opened, split into
              round artifacts (E0*/A*/R*/...) and everything else. Reported per check.
IDENTIFICATION exact. An audit hook is not a sample.
SCOPE         population every *.py in assurance/ that exits 0 · instrument a CPython audit hook ·
              baseline the check's own claim to have passed · regime this tree, this venv.
POSITIVE CTRL `DEFECTS.py` with its repair reverted — the known case, which exits 0 having read
              no round artifacts at all. It must land in the `read nothing` bucket.
              Fails at g=0: the REPAIRED `DEFECTS.py` must not.
NEGATIVE CTRL a check that legitimately reads only top-level docs (README, RETRACTIONS) is NOT
              defective — it is scoped to documents. Those are reported in their own bucket and
              never merged into the empty count, because collapsing them would manufacture a
              scandal out of a design choice.
MULTIPLICITY  no test statistic; every check is listed with its own two counts.
ARTIFACT      results/what_each_check_read.json with source hash.
IMPOSSIBLE    whether the files it opened are the RIGHT files. This measures that it opened some;
              aiming is a different round.
"""
from __future__ import annotations
import hashlib, json, os, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _isolated import ensure_worktree, restore, run_isolated   # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[1]
# ⚠ CAPTURED ONCE, AT IMPORT, AND NEVER RE-GLOBBED. The repair below restores the epoch
# directories with `git checkout`, and the first version worked out WHICH ones by globbing
# `E0*` AT REPAIR TIME -- i.e. from the already-mutilated tree. A subject that had moved an
# epoch aside made that epoch invisible to its own restore, so the repair silently skipped
# exactly the directory that needed repairing. Result: FOUR OF FIVE EPOCHS, 1,075 files,
# deleted from the working tree, recoverable only because everything was committed.
# An enumeration used to REPAIR damage must never be taken from the damaged thing.
EPOCHS = sorted(p.name for p in ROOT.glob("E0*") if p.is_dir())
HERE = ROOT / "assurance"
PY = str(ROOT / ".venv" / "bin" / "python")
SELF = pathlib.Path(__file__).resolve()
TIMEOUT = 200

# ⚠ The in-place SHIM and `run_traced` that lived here are GONE. They ran each subject in the
# live tree, which is how the sweep measured subjects inside each other's wreckage and how
# 1,075 files were deleted. Both now come from `_isolated`, which runs a subject in a git
# worktree and restores it FROM GIT -- and whose selftest proves containment with a
# saboteur that really executes.

# ⛔ RE-ENTRANCY GUARD — 2026-08-03, after a runaway that had to be killed by hand.
# This file SWEEPS every *.py in assurance/. So does the OTHER sweep in this directory. Each
# therefore swept the other, which swept the first: mutual recursion with no base case. It
# orphaned itself to `systemd --user`, kept running after its parent shell was gone, and every
# generation ran subjects that MOVE EPOCH DIRECTORIES by design. Four of five epochs were deleted
# from the working tree TWICE, ~15 minutes apart -- and the second time was not a repeat, it was
# the same runaway still going, still spawning children with an elapsed time of 0 seconds while I
# was inspecting the damage.
#
# A NAME LIST would only block the chains I thought of. An environment flag blocks every chain,
# including one through a script that does not exist yet: the first sweep to start owns the flag,
# subprocess inherits the environment, and any sweep starting underneath refuses.
# Constitution L60 bans recursive AGENT fan-out; the same ban belongs on PROCESS fan-out.
_SWEEP_FLAG = "ASSURANCE_SWEEP_ACTIVE"
if os.environ.get(_SWEEP_FLAG):
    print(f"  REFUSING: {_SWEEP_FLAG} is set, so this sweep is running INSIDE another sweep. "
          f"Two mutually-sweeping scripts recurse without bound. Exit 3, examined nothing.")
    raise SystemExit(3)
os.environ[_SWEEP_FLAG] = "1"


def main():
    """⚠ PORTED ONTO WORKTREE ISOLATION, 2026-08-03. The previous main() ran every subject in the
    LIVE tree with an `assurance/` snapshot for protection. Two subjects move epoch directories at
    the repository root, so the snapshot protected nothing: subjects were measured in each other's
    wreckage (`consistency.py` read 0 files in the sweep and 8 traced alone) and the repair
    enumerated `E0*` from the already-damaged tree, deleting 1,075 files. Every number that harness
    produced was retracted. This one runs each subject inside a git worktree that is restored FROM
    GIT between subjects, and `_isolated.selftest()` demonstrates -- with a saboteur that really
    executes -- that a subject erasing an epoch reaches only the worktree."""
    wt = ensure_worktree()
    restore(wt)
    scripts = sorted(p.name for p in (wt / "assurance").glob("*.py")
                     if p.name != SELF.name and not p.name.startswith("_"))

    # positive control planted INTO THE WORKTREE, after the restore, so it survives to run --
    # the selftest's own false pass came from planting before a restore that then erased it.
    pos_name = "_poscontrol_unrepaired.py"
    src = (wt / "assurance" / "DEFECTS.py").read_text()
    (wt / "assurance" / pos_name).write_text(
        src.replace("p = round_results(rnd, fn)\n        if p is None:\n            continue",
                    'p = HERE / rnd / "results" / fn')
           .replace("if not items:", "if False and not items:"))
    scripts.append(pos_name)

    print(f"  {len(scripts)} scripts (incl. 1 planted positive control), each in its own restored "
          f"worktree\n")
    print(f"  {'check':<46}{'exit':>6}{'round files':>13}{'other repo':>12}   verdict")
    rows, empty, docs_only, never_ran = {}, [], [], []
    for i, name in enumerate(scripts):
        # the positive control is untracked, so a restore between subjects would erase it; re-plant
        if name == pos_name and not (wt / "assurance" / pos_name).exists():
            (wt / "assurance" / pos_name).write_text(src)
        rc, files, dirtied = run_isolated(f"assurance/{name}", restore_first=(name != pos_name))
        if name != pos_name:
            (wt / "assurance" / pos_name).write_text(
                src.replace("p = round_results(rnd, fn)\n        if p is None:\n            continue",
                            'p = HERE / rnd / "results" / fn')
                   .replace("if not items:", "if False and not items:"))
        rf = [f for f in files if f.startswith("E0") and "/R" in f]
        of = [f for f in files if not f.startswith("E0") and not f.startswith("assurance/")
              and not f.startswith(".venv")]
        ran = isinstance(rc, int)
        if not ran:
            v = f"⛔ NEVER RAN ({rc})"; never_ran.append(name)
        elif rc == 0 and not rf and not of:
            v = "⚠ READ NOTHING"; empty.append(name)
        elif rc == 0 and not rf and of:
            v = "docs-only (scoped)"; docs_only.append(name)
        elif rc == 0:
            v = "read the tree"
        else:
            v = f"exit {rc}, not a pass"
        rows[name] = dict(exit=rc, round_files=len(rf), other_files=len(of), verdict=v,
                          dirtied=len(dirtied), sample=sorted(of)[:4])
        print(f"    {name[:44]:<46}{str(rc):>6}{len(rf):>13}{len(of):>12}   {v}")

    pr = rows.get(pos_name, {})
    pos_ok = pr.get("exit") == 0 and pr.get("round_files") == 0
    neg_ok = rows.get("DEFECTS.py", {}).get("round_files", 0) > 0
    (wt / "assurance" / pos_name).unlink(missing_ok=True)
    empty = [e for e in empty if e != pos_name]

    print(f"\n  POSITIVE CTRL  unrepaired DEFECTS.py exits 0 having read 0 round files: {pos_ok}")
    print(f"  FAILS AT g=0   the REPAIRED DEFECTS.py read "
          f"{rows.get('DEFECTS.py', {}).get('round_files')} round files: {neg_ok}")
    print(f"  NEVER RAN      {len(never_ran)} subject(s): {never_ran}  "
          f"(counted as UNVERIFIED, never as a pass)")
    print("\n  " + "=" * 76)
    if not (pos_ok and neg_ok):
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. The instrument cannot separate the case it was built from.")
    elif empty:
        world = "SOME-PASS-ON-NOTHING"
        print(f"  -> {len(empty)} check(s) exit 0 having opened NO project file: {empty}")
    else:
        world = "EVERY-PASS-READ-SOMETHING"
        print(f"  -> every exit-0 check opened at least one project file. {len(docs_only)} are")
        print(f"     scoped to top-level DOCUMENTS rather than rounds, which is a design choice")
        print(f"     and is listed rather than counted as a defect: {docs_only}")
    print("  " + "=" * 76)

    o = HERE / "results" / "what_each_check_read.json"
    o.parent.mkdir(exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        isolation="git worktree per subject, restored from git between subjects",
        read_nothing=empty, docs_only=docs_only, never_ran=never_ran,
        positive_control_ok=pos_ok, fails_at_g0=neg_ok, rows=rows), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
