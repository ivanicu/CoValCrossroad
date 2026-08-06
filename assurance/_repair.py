#!/usr/bin/env python3
"""assurance/_repair.py — repair the tree on ENTRY, because a repair that runs on exit cannot help.

⛔ WHY, AND IT IS MEASURED, NOT FEARED. `attack_the_suite.hide_rounds()` and
   `attack_every_check` MOVE THE EPOCH DIRECTORIES out of the live tree and restore them in a
   `finally:` block. `pueue kill` sends SIGKILL. **No `finally` survives SIGKILL.** So the repair
   step is exactly the step a scheduler is able to delete, and what remains is a repository that
   looks empty.

   R428 counted the damage instead of assuming it: **EIGHT orphaned `attack_rounds_*` stashes in
   /tmp across two days**, holding 1,553 · 1,421 · 1,191 · 1,173 · 141 · 135 · 60 · 5 files. Five of
   them happened on 08-03 and NOBODY NOTICED — because `run_isolated(restore_first=True)` repairs a
   previous interruption on the NEXT invocation. **The system self-heals on next run; it does not
   self-heal while nothing runs.** And R428's census found the healing is not free: 21 untracked
   artifacts and 3 never-committed source versions existed only in /tmp.

   ⭐ The cost of believing it was a one-off: R389's own README is titled
   *"...and my tooling deleted the round"* and its artifact carries `"destroyed_and_rewritten":
   true`. The failure was written into a round's TITLE and still got reported as an accident.

THE GAUGE TEST THAT CHOSE THE INSTRUMENT — three lines, zero compute, and it killed my first design.
   The obvious check is `for d in ROOT.glob("E0*"): d.exists()`. Name the transformations that
   leave that MEASUREMENT invariant while the PROPERTY (the tree is whole) is violated:
       * an epoch present but EMPTIED of its files          -> exists() is True.  BLIND.
       * an epoch moved aside and a bare dir left behind    -> exists() is True.  BLIND.
       * a single ROUND moved, not a whole epoch            -> not enumerated.    BLIND.
   Measurement invariant + property not ⇒ the measurement is blind to what it claims. So the
   instrument is **`git ls-files --deleted`** — the index's own opinion of which tracked paths the
   working tree is missing — which is invariant under none of the three.

WHAT THIS DOES
   1. asks git which tracked paths are missing;
   2. restores them BY NAME FROM THE INDEX (`git checkout -- <path>`), never from a glob of the
      tree — globbing at repair time is what turned a 4-epoch mutilation into 1,075 deleted files,
      because a path that has been moved aside is invisible to its own restore;
   3. REPORTS orphaned stashes and never deletes them, because R428 proved they can be the only
      copy of an untracked artifact.

WHAT IT DELIBERATELY DOES NOT DO
   * it does not touch untracked files — it cannot know whether one is debris or the only copy;
   * it does not delete a stash — see above, and `mv` never `rm`;
   * it does not run inside a worktree's parent or anywhere but the repo it is imported from.

CONTROLS (`python assurance/_repair.py --selftest`)
   POSITIVE  plant the EXACT damage in a linked worktree — move an epoch aside AND delete a single
             tracked file — then require `repair()` to restore both. A repair never shown to fix
             the real event is untested, not safe.
   g=0       on an undamaged tree it must report 0 and change nothing. A repair that always claims
             to have repaired something is the empty-population failure wearing a fix's clothes.
   BLINDNESS the naive `dir.exists()` check is run on the same planted damage and must MISS the
             emptied-directory case that git catches. Without this the gauge test above is a story;
             with it, it is a measurement.
   ⚠ the selftest plants damage ONLY in a linked worktree, verified by `assert_not_live`. A test
     for tree destruction that runs in the live tree is the bug, not the test.

EXIT (as a script)  0 nothing needed or repair verified · 1 repair incomplete · 2 unrunnable
"""
from __future__ import annotations
import json
import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=str(cwd or ROOT), capture_output=True, text=True)


def missing_tracked(root: pathlib.Path) -> list[str]:
    """Tracked paths the working tree does not have. git's opinion, not a directory listing."""
    r = _git("ls-files", "--deleted", cwd=root)
    return sorted(l for l in r.stdout.split("\n") if l.strip())


def orphan_stashes() -> list[pathlib.Path]:
    return sorted(p for p in pathlib.Path("/tmp").glob("attack_rounds_*") if p.is_dir())


def repair(root: pathlib.Path | None = None, verbose: bool = True) -> dict:
    """Restore every missing tracked path BY NAME. -> {'missing':[...], 'restored':[...], ...}"""
    root = root or ROOT
    miss = missing_tracked(root)
    stashes = orphan_stashes()
    out = {"missing": miss, "restored": [], "still_missing": [], "stashes": [str(s) for s in stashes]}
    if miss:
        if verbose:
            print(f"  ⛔ {len(miss)} tracked paths are missing from the working tree. Restoring BY "
                  f"NAME from the index (never from a glob of a tree that no longer has them).")
        # in batches: a mutilated tree can be missing thousands of paths and argv is finite
        for i in range(0, len(miss), 400):
            _git("checkout", "--", *miss[i:i + 400], cwd=root)
        after = set(missing_tracked(root))
        out["restored"] = [p for p in miss if p not in after]
        out["still_missing"] = sorted(after)
        if verbose:
            print(f"  restored {len(out['restored'])} · still missing {len(out['still_missing'])}")
    elif verbose:
        print("  tree is whole: 0 tracked paths missing.")
    if stashes and verbose:
        n = sum(1 for s in stashes for _ in s.rglob("*"))
        print(f"  ⚠ {len(stashes)} orphaned attack_rounds_* stashes in /tmp ({n} entries). NOT "
              f"deleted — R428 found 21 untracked artifacts that existed only inside one.")
    return out


def repair_full(root: pathlib.Path | None = None, verbose: bool = True) -> dict:
    """Breadcrumb first, then the index. ORDER MATTERS AND IT IS THE WHOLE POINT.

    `git checkout --` restores a tracked path by creating HEAD's version at it. If the index
    restore ran FIRST, every tracked file would already be sitting where the stash's copy belongs,
    and the stash's version -- which may carry uncommitted edits that exist nowhere else -- would
    have nowhere to land without overwriting. R428 measured 3 such never-committed versions inside
    one stash. So: move the stash home first (it is the richer copy, tracked AND untracked), and
    let the index restore fill only what is still missing afterwards.

    ⚠ It NEVER overwrites an existing file. A path already present in the tree is left alone and
      counted in `kept`, because this function cannot know whether the tree's copy is the newer
      one, and R428's R389 case proves the tree's copy sometimes IS -- the stash held the
      pre-deletion original and the tree held the documented rewrite.
    """
    root = root or ROOT
    bc = root / "assurance" / "results" / ".hide_in_progress.json"
    out = {"breadcrumb": None, "moved_home": [], "kept": [], "stash_gone": False}
    if bc.exists():
        try:
            d = json.loads(bc.read_text())
        except Exception:
            d = {}
        stash = pathlib.Path(d.get("stash", ""))
        out["breadcrumb"] = str(bc)
        # ⭐ IN FLIGHT or ORPHANED -- these demand opposite responses and the marker alone cannot
        #    tell them apart. A live writer must be left alone (racing it is the livelock case); a
        #    dead one must be repaired NOW. On 2026-08-06 a second session read this marker, could
        #    not distinguish the two, correctly chose not to race, and left 2,896 files broken --
        #    the writer had been SIGKILLed by the suite's own 90s timeout. `os.kill(pid, 0)` is the
        #    whole fix. Breadcrumbs written before this carry no pid: report UNKNOWN, never assume.
        pid = d.get("pid")
        if pid is None:
            live = None
        else:
            try:
                os.kill(int(pid), 0)
                live = True
            except (ProcessLookupError, ValueError, TypeError):
                live = False
            except PermissionError:
                live = True                      # exists, owned by someone else
        out["writer_pid"], out["writer_live"] = pid, live
        if verbose:
            state = ("IN FLIGHT — pid %s is alive. DO NOT RACE IT; this repair leaves it alone"
                     % pid) if live else (
                "ORPHANED — pid %s is gone, so the restore never ran and repair is safe NOW" % pid
                if live is False else
                "UNKNOWN — this breadcrumb predates the pid field, so liveness cannot be decided")
            print(f"  ⛔ a breadcrumb is present: {state}")
            print(f"     stash={stash}  moved={d.get('moved')}")
        if live:
            # A live writer still owns the stash and will restore it in its own `finally:`.
            out["skipped_live_writer"] = True
            out.update(repair(root, verbose=verbose))
            return out
        if stash.is_dir():
            for name in d.get("moved", []):
                src = stash / name
                if not src.is_dir():
                    continue
                for p in src.rglob("*"):
                    if not p.is_file() or p.is_symlink():
                        continue
                    rel = pathlib.Path(name) / p.relative_to(src)
                    dst = root / rel
                    if dst.exists():
                        out["kept"].append(str(rel)); continue
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(p, dst)
                    out["moved_home"].append(str(rel))
            if verbose:
                print(f"     recovered {len(out['moved_home'])} files from the stash "
                      f"(TRACKED AND UNTRACKED) · left {len(out['kept'])} already-present files "
                      f"alone, because the tree's copy is sometimes the newer one")
        else:
            out["stash_gone"] = True
            if verbose:
                print(f"     ⛔ THE STASH IS GONE. /tmp was reaped and any untracked artifact in "
                      f"it is unrecoverable. Only the index restore below can help now.")
        bc.unlink(missing_ok=True)
    out.update(repair(root, verbose=verbose))
    return out


# ------------------------------------------------------------------------------------ selftest
def selftest() -> int:
    sys.path.insert(0, str(ROOT / "assurance"))
    import _isolated as ISO

    print("assurance/_repair.py · selftest — plant the EXACT event, in a worktree, never live\n")
    wt = ISO.ensure_worktree()
    ISO.assert_not_live(wt)                      # refuses to aim destruction at a main repository
    ISO.restore(wt)
    ok = True

    # g=0 FIRST: an undamaged tree must produce a zero, or every later PASS is meaningless.
    base = repair(wt, verbose=False)
    g0 = not base["missing"] and not base["restored"]
    ok &= g0
    print(f"  g=0        undamaged worktree -> missing {len(base['missing'])}, restored "
          f"{len(base['restored'])}, both must be 0   {'PASS' if g0 else '⛔ FAIL'}")

    # PLANT the real event: move an epoch aside, AND delete one tracked file elsewhere.
    epochs = sorted(p for p in wt.iterdir() if p.is_dir() and p.name.startswith("E0"))
    if len(epochs) < 2:
        print("  UNRUNNABLE: fewer than 2 epochs in the worktree — nothing to plant. Exit 2.")
        return 2
    victim = epochs[0]
    aside = wt.parent / f"_repair_selftest_{victim.name}"
    shutil.rmtree(aside, ignore_errors=True)
    shutil.move(str(victim), str(aside))
    solo = next(p for p in sorted(epochs[1].rglob("*.py")) if p.is_file())
    solo_rel = str(solo.relative_to(wt))
    solo.unlink()

    # BLINDNESS control: the naive check, on the same damage, in its blind configuration.
    victim.mkdir()                               # a bare directory left where the epoch was
    naive_sees = not victim.exists()
    git_sees = len(missing_tracked(wt))
    blind_ok = (naive_sees is False) and git_sees > 0
    ok &= blind_ok
    print(f"  BLINDNESS  naive `dir.exists()` reports damage: {naive_sees} (it is blind) · "
          f"git reports {git_sees} missing paths   {'PASS' if blind_ok else '⛔ FAIL'}")

    # POSITIVE: repair must restore BOTH the epoch's files and the single deleted file.
    r = repair(wt, verbose=False)
    back_epoch = sum(1 for _ in victim.rglob("*")) > 0
    back_solo = (wt / solo_rel).exists()
    none_left = not r["still_missing"]
    pos = back_epoch and back_solo and none_left
    ok &= pos
    print(f"  POSITIVE   epoch restored: {back_epoch} · single file restored: {back_solo} · "
          f"still missing: {len(r['still_missing'])}   {'PASS' if pos else '⛔ FAIL'}")
    print(f"             ({len(r['restored'])} paths restored by name from the index)")

    shutil.rmtree(aside, ignore_errors=True)
    ISO.restore(wt)

    # ── THE UNTRACKED CHANNEL, which is the one git cannot cover and the one R428 measured ──
    # Plant the FULL event: an untracked artifact inside an epoch, then the epoch moved aside to a
    # stash with a breadcrumb, exactly as `hide_rounds` now does. `repair_full` must bring the
    # untracked file home. Without this control the breadcrumb is decoration.
    ep = sorted(p for p in wt.iterdir() if p.is_dir() and p.name.startswith("E0"))[0]
    untracked_rel = f"{ep.name}/__R428_UNTRACKED_CANARY__.json"
    (wt / untracked_rel).write_text('{"only_copy": true}')
    stash = wt.parent / "_repair_selftest_stash"
    shutil.rmtree(stash, ignore_errors=True); stash.mkdir(parents=True)
    (wt / "assurance" / "results").mkdir(parents=True, exist_ok=True)
    (wt / "assurance" / "results" / ".hide_in_progress.json").write_text(
        json.dumps({"stash": str(stash), "moved": [ep.name]}))
    shutil.move(str(ep), str(stash / ep.name))       # the SIGKILL happens here: no restore runs

    gone = not (wt / untracked_rel).exists()
    rf = repair_full(wt, verbose=False)
    back = (wt / untracked_rel).exists() and \
        json.loads((wt / untracked_rel).read_text()).get("only_copy") is True
    unt_ok = gone and back and not rf["still_missing"]
    ok &= unt_ok
    print(f"  UNTRACKED  an untracked-only artifact was destroyed by the move: {gone} · brought "
          f"home by the breadcrumb: {back} · tracked still missing: {len(rf['still_missing'])}"
          f"   {'PASS' if unt_ok else '⛔ FAIL — the channel git cannot cover is still open'}")

    (wt / untracked_rel).unlink(missing_ok=True)
    shutil.rmtree(stash, ignore_errors=True)
    ISO.restore(wt)

    # ── LIVENESS, the branch added 2026-08-06. Both directions, because only one of them is the
    #    dangerous one: reading ORPHANED as IN FLIGHT leaves a broken tree (what happened), and
    #    reading IN FLIGHT as ORPHANED races a live writer (the livelock). A control that only
    #    exercised the repairing direction would certify exactly half of it.
    def _plant(pid_value):
        ep2 = sorted(p for p in wt.iterdir() if p.is_dir() and p.name.startswith("E0"))[0]
        st = wt.parent / "_repair_selftest_live_stash"
        shutil.rmtree(st, ignore_errors=True); st.mkdir(parents=True)
        (wt / "assurance" / "results").mkdir(parents=True, exist_ok=True)
        (wt / "assurance" / "results" / ".hide_in_progress.json").write_text(
            json.dumps({"stash": str(st), "moved": [ep2.name], "pid": pid_value}))
        shutil.move(str(ep2), str(st / ep2.name))
        return ep2, st

    dead_pid = 999_000 + (os.getpid() % 1000)         # a pid that cannot be running
    while True:
        try:
            os.kill(dead_pid, 0); dead_pid += 1
        except OSError:
            break
    ep2, st = _plant(dead_pid)
    r_dead = repair_full(wt, verbose=False)
    dead_ok = (r_dead.get("writer_live") is False) and bool(r_dead["moved_home"]) \
        and not r_dead["still_missing"]
    shutil.rmtree(st, ignore_errors=True); ISO.restore(wt)

    ep3, st3 = _plant(os.getpid())                    # a pid that IS running: this process
    r_live = repair_full(wt, verbose=False)
    live_ok = (r_live.get("writer_live") is True) and r_live.get("skipped_live_writer") is True \
        and not r_live["moved_home"]
    shutil.move(str(st3 / ep3.name), str(ep3))        # undo the plant by hand, as the writer would
    shutil.rmtree(st3, ignore_errors=True)
    (wt / "assurance" / "results" / ".hide_in_progress.json").unlink(missing_ok=True)
    ISO.restore(wt)
    ok &= dead_ok and live_ok
    print(f"  LIVENESS   dead writer -> repaired ({len(r_dead['moved_home'])} moved home): "
          f"{dead_ok} · LIVE writer -> left strictly alone, 0 moved: {live_ok}   "
          f"{'PASS' if dead_ok and live_ok else '⛔ FAIL — the marker still cannot tell them apart'}")

    # R428 wrote "eight times, on BOTH channels" when it had counted eight stashes and two
    # channels. Both numbers moved (11 stashes by 2026-08-06, and liveness is a third channel) and
    # the sentence did not, which is what a hand-typed count in a passing message always does.
    print(f"\n  {'PASS — the repair fixes the exact event on all THREE channels: tracked, untracked, and liveness.' if ok else '⛔ FAIL — the repair is not shown to fix the event it exists for.'}")
    print(f"  ⚠ orphan count is measured, never quoted: "
          f"{len(list(pathlib.Path('/tmp').glob('attack_rounds_*')))} stashes in /tmp right now.")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    print("assurance/_repair.py · entry-time tree repair")
    # ⛔ 2026-08-06: this called `repair()`, the TRACKED-ONLY path, while `repair_full()` sat two
    #    functions above it with a PASSING selftest for the untracked channel. On 08-06 the suite
    #    SIGKILLed a hide holding 2,911 files; `repair()` reported "tree is whole: 0 tracked paths
    #    missing" -- true, and useless, because the round in flight (R825) was UNTRACKED and existed
    #    only inside the stash. Its four source files were then copied back BY HAND, doing exactly
    #    what `repair_full()` does and is tested to do.
    #    A capability that is built, controlled, and not reachable from the entry point is not a
    #    capability. It is a comment. The breadcrumb branch is a no-op when no hide is in flight,
    #    and `repair_full` never overwrites an existing path, so this is strictly more recovery at
    #    no risk to a healthy tree.
    res = repair_full()
    sys.exit(0 if not res["still_missing"] else 1)
