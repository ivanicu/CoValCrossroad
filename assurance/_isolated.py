#!/usr/bin/env python3
"""assurance/_isolated.py — run a check where it cannot damage the thing it is measuring.

WHY, AND NONE OF IT IS HYPOTHETICAL. Two sweeps in this directory snapshotted `assurance/` and
restored it after each subject. Three separate failures came out of that one assumption:

  * `attack_the_suite.py` and `attack_every_check.py` MOVE EPOCH DIRECTORIES at the repository
    root — their own docstring says "each is moved separately and restored separately".
    Snapshotting `assurance/` protects nothing against that.
  * `audit_the_auditors.py` snapshots `assurance/` and DELETES files not in its snapshot. Run as a
    subject of the other sweep, it deleted that sweep's own in-flight artifact.
  * the repair was worse than the damage: it restored the epochs with
    `git checkout -- [p.name for p in ROOT.glob("E0*")]`, globbing **at repair time, from the
    already-mutilated tree**, so an epoch that had been moved aside was invisible to its own
    restore. Four of five epochs — 1,075 files — deleted from the working tree.

And underneath all three, the reason it kept coming back: the two sweeps SWEPT EACH OTHER, so the
chain orphaned itself to `systemd` and kept running after its shell was gone. That is fixed
separately by the re-entrancy flag; this file fixes the other half.

One shape, four times in a day: **the instrument's world was allowed to be changed by the thing it
was measuring.** No snapshot fixes it, because a snapshot is itself an enumeration of the tree, and
the tree is what the subject breaks.

WHAT THIS DOES INSTEAD
  * every subject runs inside a **git worktree**, so the main checkout is not reachable at all;
  * between subjects the worktree is restored **from git**, never from a directory listing, so a
    moved-aside path is re-materialised by name from the index rather than skipped for being
    invisible;
  * population is still measured by an audit hook on `open`, the only unit that means the same
    thing to every check.

THE CONTROL THAT MAKES IT SEVERE. `selftest()` plants a subject whose only job is to delete an
epoch directory, runs it, and then asserts the MAIN tree still has all five. That is the exact
event this module exists to prevent, so a harness that has not been shown to survive it is not
isolated — it is untested. And it fails at g=0: a harmless subject must dirty nothing.

⚠ COMMITTED BEFORE IT WAS EVER RUN. The first version of this file was written and destroyed by
the runaway before it reached git. Writing the guard first and the test second is the only order
that survives its own subject matter.
"""
from __future__ import annotations
import json, os, pathlib, subprocess, sys, tempfile, textwrap

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = str(ROOT / ".venv" / "bin" / "python")
WT = pathlib.Path(os.environ.get(
    "ASSURANCE_WORKTREE",
    "/tmp/claude-1000/-home-ivan/7d277876-c2fd-4a27-9b05-652b391121ff/scratchpad/assurance_wt"))

SHIM = textwrap.dedent('''
    import sys, os, runpy, json, pathlib
    ROOT = pathlib.Path({root!r}).resolve()
    OUT  = pathlib.Path({out!r})
    seen = set()
    def hook(ev, args):
        if ev == "open":
            p = args[0]
            if isinstance(p, (str, bytes, os.PathLike)):
                try:
                    q = pathlib.Path(os.fsdecode(p)).resolve()
                    if ROOT in q.parents:
                        seen.add(str(q.relative_to(ROOT)))
                except Exception:
                    pass
    sys.addaudithook(hook)
    rc = 0
    try:
        sys.argv = [{tgt!r}]
        runpy.run_path({tgt!r}, run_name="__main__")
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 0
    except BaseException as e:
        rc = "EXC " + type(e).__name__
    finally:
        OUT.write_text(json.dumps({{"rc": rc, "files": sorted(seen)}}))
''')


def _git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=str(cwd or ROOT), capture_output=True, text=True)


def ensure_worktree(rev: str = "HEAD") -> pathlib.Path:
    if (WT / ".git").exists():
        return WT
    WT.parent.mkdir(parents=True, exist_ok=True)
    _git("worktree", "prune")
    r = _git("worktree", "add", "--detach", str(WT), rev)
    if not (WT / ".git").exists():
        raise RuntimeError(f"worktree add failed: {r.stderr[:300]}")
    _link_untracked_inputs()
    return WT


# Inputs that are deliberately NOT in git and that checks legitimately read. `data/` is the CoVal
# release itself -- 69 MB, correctly uncommitted. Isolation is what surfaced this: two subjects
# that pass in the live tree died in a clean worktree with FileNotFoundError on
# `data/comparisons.jsonl`, which is not a defect in them but a statement about what the repo
# alone can reproduce. They are SYMLINKED, not copied: a subject that corrupts the release would
# then reach the real one, so this is the single hole in the isolation and it is named here rather
# than left for someone to discover.
# ⚠ `.venv` ADDED 2026-08-03 by R316. Six rounds (R261-R266) shell out to
# `ROOT / ".venv/bin/python"`, and a worktree has no `.venv` because it is gitignored -- so
# `subprocess.run` raised FileNotFoundError and R315 classified all six BROKEN-INPUT. They are
# not broken; the isolation was. A venv is ENVIRONMENT, recreatable by ordinary setup, and
# excluding it measures the machine rather than the repository. `_archive/` is deliberately NOT
# added: it is gitignored DATA that no setup step can recreate, so a round reading it genuinely
# cannot be reproduced from a clean clone, and that is a finding rather than an artifact.
UNTRACKED_INPUTS = ("data", ".venv")


def _link_untracked_inputs() -> None:
    """⚠ REPAIRED 2026-08-03 by R315. The previous body linked the DIRECTORY and guarded on
    `not dst.exists()` -- and `data/` always exists in a fresh worktree, because `data/fetch.py`
    IS tracked. So the guard was true on every run, the symlink was NEVER created, and every
    isolated run since this harness was written has executed against a `data/` holding one
    3.9 KB script and none of the 69 MB release.

    The cost of that is not the missing files, it is the MISATTRIBUTION: the harness's own
    comment records two subjects dying on `data/comparisons.jsonl` and reads it as `a statement
    about what the repo alone can reproduce`. It was a statement about this function. A harness
    that silently supplies an empty input directory turns every subject into a false BROKEN, and
    the explanation written next to it made the false positive look like a finding.

    Fixed by linking per ENTRY, so a directory git has already materialised for a tracked file
    is filled in rather than skipped."""
    for name in UNTRACKED_INPUTS:
        src, dst = ROOT / name, WT / name
        if not src.exists():
            continue
        if not dst.exists():
            dst.symlink_to(src, target_is_directory=src.is_dir())
            continue
        if src.is_dir() and dst.is_dir():
            for child in src.iterdir():
                target = dst / child.name
                if not target.exists() and not target.is_symlink():
                    target.symlink_to(child, target_is_directory=child.is_dir())


def restore(wt: pathlib.Path) -> list[str]:
    """Restore FROM GIT, never from a directory listing.

    `git checkout -- .` re-materialises every tracked path the INDEX knows about, including one a
    subject moved away — precisely the case a glob of the live tree cannot see. Untracked
    leftovers are enumerated by `git status`, also from git.
    """
    changed = [l for l in _git("status", "--porcelain", cwd=wt).stdout.split("\n") if l.strip()]
    _git("checkout", "--", ".", cwd=wt)
    for line in changed:
        if line.startswith("??"):
            rel = line[3:].strip().strip('"').rstrip("/")
            # ⚠ THE LINKED INPUTS ARE UNTRACKED BY DESIGN AND MUST SURVIVE THE RESTORE. The first
            # version deleted them, because `git status` reports a symlink to the release as `??`
            # like any other untracked path -- so `data/` vanished after the first subject and
            # every later subject died on FileNotFoundError. The restore was erasing the thing it
            # had just been told to provide.
            if rel.split("/")[0] in UNTRACKED_INPUTS:
                continue
            p = wt / rel
            try:
                if p.is_dir():
                    subprocess.run(["find", str(p), "-delete"], capture_output=True)
                elif p.exists():
                    p.unlink()
            except Exception:
                pass
    _link_untracked_inputs()   # re-provide after every restore, never assume it survived
    return changed


def run_isolated(script_rel: str, timeout: int = 200, restore_first: bool = True):
    """(rc, repo-relative files opened, paths the subject dirtied). Never touches the main tree.

    ⚠ `restore_first=False` EXISTS BECAUSE THE SELFTEST SILENTLY DID NOTHING. `restore()` deletes
    untracked files, and it ran BEFORE the subject -- so the saboteur probe, which is untracked by
    construction, was erased before it could execute. `run_isolated` returned "MISSING", the
    selftest counted the main tree as unharmed, and printed PASS. A control that reports success
    having executed nothing, inside the module written to prevent exactly that. It was visible
    only because the exit code was printed beside the verdict; had I printed the verdict alone it
    would have read as a clean result.
    """
    wt = ensure_worktree()
    if restore_first:
        restore(wt)
    tgt = wt / script_rel
    if not tgt.exists():
        return "MISSING", [], []
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td) / "t.json"
        shim = pathlib.Path(td) / "s.py"
        shim.write_text(SHIM.format(root=str(wt), out=str(out), tgt=str(tgt)))
        env = dict(os.environ, ASSURANCE_SWEEP_ACTIVE="1")   # subjects may not start a sweep
        try:
            subprocess.run([PY, str(shim)], cwd=str(wt), capture_output=True,
                           timeout=timeout, env=env)
        except subprocess.TimeoutExpired:
            return "TIMEOUT", [], restore(wt)
        if not out.exists():
            return "NO-TRACE", [], restore(wt)
        d = json.loads(out.read_text())
    return d["rc"], d["files"], restore(wt)


def selftest() -> int:
    print("  SELFTEST — plant a subject whose only job is to DESTROY, and require the MAIN tree to\n"
          "  survive it. This is the exact event that deleted 1,075 files twice today; a harness\n"
          "  that has not been shown to survive it is not isolated, only untested.\n")
    before = sorted(p.name for p in ROOT.glob("E0*") if p.is_dir())
    wt = ensure_worktree()
    restore(wt)          # clean the worktree FIRST, then plant into it
    sab = "assurance/_saboteur_probe.py"
    (wt / sab).write_text(textwrap.dedent('''
        import pathlib, shutil
        R = pathlib.Path(__file__).resolve().parents[1]
        for e in sorted(R.glob("E0*")):
            if e.is_dir():
                shutil.rmtree(e); print("deleted", e.name); break
    '''))
    rc, _files, changed = run_isolated(sab, restore_first=False)
    after = sorted(p.name for p in ROOT.glob("E0*") if p.is_dir())
    wt_epochs = sorted(p.name for p in wt.glob("E0*") if p.is_dir())
    (wt / sab).unlink(missing_ok=True)

    main_safe = before == after
    healed = len(wt_epochs) == len(before)
    print(f"    saboteur exit                  : {rc}")
    print(f"    MAIN tree epochs before/after  : {len(before)} / {len(after)}   "
          f"{'SAFE' if main_safe else '⚠ DAMAGED'}")
    print(f"    worktree epochs after restore  : {len(wt_epochs)} of {len(before)}   "
          f"{'healed FROM GIT' if healed else '⚠ NOT healed'}")
    print(f"    paths the saboteur dirtied     : {len(changed)}")

    restore(wt)
    (wt / "assurance/_noop_probe.py").write_text("print('noop')\n")
    rc0, _f0, changed0 = run_isolated("assurance/_noop_probe.py", restore_first=False)
    (wt / "assurance/_noop_probe.py").unlink(missing_ok=True)
    # ⛔ REPAIRED 2026-08-04 (R376). The criterion was `len(changed0) <= 1`, and it FAILED --
    #   printing "do not use this harness" for as long as this file has existed, which R374
    #   measured as BORN RED. R376 read the two paths instead of the count: they are `.venv`
    #   and `assurance/_noop_probe.py` -- the linked interpreter and THE PROBE THIS SELFTEST
    #   ITSELF WRITES. Neither is tracked; neither is content the harness claims to protect.
    #   The criterion was counting the harness's own scaffolding as contamination, which is
    #   `realstat §4 · the control fails for its own reasons`.
    #   The repair counts TRACKED paths, because a tracked path dirtied is the thing that
    #   would actually mean a leak. ⚠ AND A LOOSENED CRITERION IS A DELETED CONTROL UNLESS IT
    #   STILL FIRES: R376 ran this exact rule against the SABOTEUR, which dirties 95 tracked
    #   paths, and it fires. That contrast -- 0 on the benign subject, 95 on the destructive
    #   one -- is the only evidence separating a fix from a quiet disarm, and it is why the
    #   number is not simply raised from 1 to 2.
    g0_tracked = [ln[3:].strip().strip('"').rstrip("/") for ln in changed0
                  if _git("ls-files", "--error-unmatch", "--",
                          ln[3:].strip().strip('"').rstrip("/"), cwd=wt).returncode == 0]
    g0 = not g0_tracked
    print(f"    g=0 (harmless subject)         : exit {rc0}, dirtied {len(changed0)} path(s), "
          f"{len(g0_tracked)} TRACKED   "
          f"{'PASS' if g0 else '⚠ dirtied tracked content with nothing planted'}")
    if g0_tracked:
        print(f"      tracked paths dirtied: {g0_tracked[:5]}")

    # ⛔ THE PLANT MUST HAVE ACTUALLY RUN. "MISSING"/"TIMEOUT"/"NO-TRACE" mean the subject never
    # executed, and a main tree that survives an attack THAT NEVER HAPPENED is not evidence of
    # containment -- it is the empty-population pass, one level up, inside the control itself.
    ran = isinstance(rc, int)
    if not ran:
        print(f"\n    ⛔ THE SABOTEUR NEVER RAN (rc={rc!r}). The main tree being intact says")
        print("       NOTHING about containment. This is not a pass; it is an examined-nothing.")
    ok = ran and main_safe and healed and g0
    print(f"\n  {'PASS — destruction is contained, and the restore heals it from git'
             if ok else 'FAIL — do not use this harness'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest())
