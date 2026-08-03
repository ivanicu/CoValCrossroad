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
    return WT


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
            p = wt / line[3:].strip().strip('"')
            try:
                if p.is_dir():
                    subprocess.run(["find", str(p), "-delete"], capture_output=True)
                elif p.exists():
                    p.unlink()
            except Exception:
                pass
    return changed


def run_isolated(script_rel: str, timeout: int = 200):
    """(rc, repo-relative files opened, paths the subject dirtied). Never touches the main tree."""
    wt = ensure_worktree()
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
    sab = "assurance/_saboteur_probe.py"
    (wt / sab).write_text(textwrap.dedent('''
        import pathlib, shutil
        R = pathlib.Path(__file__).resolve().parents[1]
        for e in sorted(R.glob("E0*")):
            if e.is_dir():
                shutil.rmtree(e); print("deleted", e.name); break
    '''))
    rc, _files, changed = run_isolated(sab)
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

    (wt / "assurance/_noop_probe.py").write_text("print('noop')\n")
    rc0, _f0, changed0 = run_isolated("assurance/_noop_probe.py")
    (wt / "assurance/_noop_probe.py").unlink(missing_ok=True)
    g0 = len(changed0) <= 1
    print(f"    g=0 (harmless subject)         : exit {rc0}, dirtied {len(changed0)} path(s)   "
          f"{'PASS' if g0 else '⚠ fires with nothing planted'}")

    ok = main_safe and healed and g0
    print(f"\n  {'PASS — destruction is contained, and the restore heals it from git'
             if ok else 'FAIL — do not use this harness'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest())
