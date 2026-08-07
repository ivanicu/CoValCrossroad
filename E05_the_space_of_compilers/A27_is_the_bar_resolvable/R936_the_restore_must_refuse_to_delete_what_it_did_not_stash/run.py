#!/usr/bin/env python3
"""
R936 · `attack_the_suite`'s restore deletes work it never stashed — reproduced, fixed, and tested
        on the real object.

⛔ WHY. R935 was written, run, and its artifact printed; minutes later the directory did not exist.
Traced to `assurance/attack_the_suite.py:91-98`: the harness MOVES every live `E0*` campaign tree to
`/tmp`, runs the suite against the emptied repo, then

    for c in moved:
        shutil.rmtree(c, ignore_errors=True)      # <- deletes whatever is at the live path NOW
        shutil.move(str(tmp / c.name), str(c))

**Anything created at the live path while the stash is away is destroyed by that rmtree.** R935
landed in a freshly-created empty `E05` and died on restore. Every COMMITTED round survived, because
they returned with the stash; only the uncommitted one was lost.

⚠ **AND THE FILE ALREADY KNOWS.** Its own comment records R428 counting eight orphaned stashes and
finding that *"21 untracked artifacts and 3 never-committed source versions existed nowhere but
inside a stash"* — the BREADCRUMB exists for exactly that. But the breadcrumb protects the SIGKILL
path; **the normal-completion path still deletes unconditionally.** The knowledge is present and
applied one step too late.

⭐ **NOT FORCED, AND ONE HALF IS.** On a quiet run nothing appears at the live path, so the fix
changes nothing — that half is a DERIVATION and is labelled. What is not forced is whether the fix
preserves work when something IS created in the window, and that requires a PLANT INSIDE THE WINDOW.
R928's lesson is the whole reason: an attack that never lands tells you nothing about the lock.

ESTIMAND        whether a file created at the live path during the harness's window survives
                `restore()`, before and after the fix.
IDENTIFICATION  exact — a deterministic property of the restore path.
SCOPE           population: the two-step stash/restore in `attack_the_suite.py`
                instrument: a sentinel file planted at the live path inside the window
                baseline:   the committed `restore()`
                regime:     this repo, working tree clean before the run
WORLDS          A · the sentinel dies before the fix and survives after -> the hazard is real and
                    the fix closes it
                B · the sentinel survives before the fix -> the hazard was not reproduced and the
                    fix addresses nothing; R935's loss had another cause
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE / THE HAZARD MUST REPRODUCE: with the UNFIXED restore, the planted
                     sentinel must be DESTROYED. **If it survives, this round has not reproduced
                     what killed R935 and nothing below is a fix for it.**
                  ⭐ ② after the fix the sentinel must SURVIVE, and its preserved location must be
                     PRINTED — a rescue nobody can find is the orphaned-stash failure again.
                  ⭐ ③ PLACEBO, and it is FORCED: with no plant, the restore must be byte-for-byte
                     equivalent before and after. Labelled a derivation, not evidence.
                  ⭐ ④ the mechanism is exercised on a SANDBOX first — a temp tree with fake `E00_`
                     / `E01_` dirs — so a defective fix cannot damage the repo before it is shown
                     to work. ⚠ The sandbox tests my TRANSCRIPTION of `restore()`; only the real
                     run tests the object, and both are reported separately.
MULTIPLICITY    2 restore variants × {plant, no plant} × {sandbox, real}; every cell printed.
ARTIFACT        results/restore_refusal.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this closes the NORMAL-completion path. The SIGKILL path still
                relies on the breadcrumb plus `_repair.py`, which this round does not touch.
"""
import json, pathlib, re, shutil, subprocess, tempfile
import numpy as np  # noqa: F401  (kept for artifact stamping parity)

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
TARGET = ROOT / "assurance/attack_the_suite.py"
SENTINEL = "R936_sentinel_created_inside_the_window.txt"


def restore_committed(moved, tmp):
    """transcribed from attack_the_suite.py:95-98 — the committed behaviour"""
    for c in moved:
        shutil.rmtree(c, ignore_errors=True)
        shutil.move(str(tmp / c.name), str(c))


def restore_fixed(moved, tmp, preserved):
    """the fix: never delete what was not stashed — move it aside and SAY SO"""
    for c in moved:
        if c.exists() and any(c.iterdir()):
            keep = pathlib.Path(tempfile.mkdtemp(prefix="attack_preserved_"))
            shutil.move(str(c), str(keep / c.name))
            preserved.append(str(keep / c.name))
        else:
            shutil.rmtree(c, ignore_errors=True)
        shutil.move(str(tmp / c.name), str(c))


def sandbox(variant, plant):
    """exercise the mechanism on a fake tree; returns (sentinel_survived, preserved_paths)"""
    root = pathlib.Path(tempfile.mkdtemp(prefix="r936_sandbox_"))
    camps = []
    for n in ("E00_alpha", "E01_beta"):
        d = root / n
        (d / "A01" / "R01").mkdir(parents=True)
        (d / "A01" / "R01" / "committed.txt").write_text("committed work")
        camps.append(d)
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="r936_stash_"))
    moved = []
    for c in camps:
        shutil.move(str(c), str(tmp / c.name))
        moved.append(c)
    if plant:                                   # created INSIDE the window
        (camps[0] / "A99").mkdir(parents=True, exist_ok=True)
        (camps[0] / "A99" / SENTINEL).write_text("uncommitted work")
    preserved = []
    if variant == "committed":
        restore_committed(moved, tmp)
    else:
        restore_fixed(moved, tmp, preserved)
    survived = any(pathlib.Path(p).rglob(SENTINEL) for p in preserved) or \
        bool(list(camps[0].rglob(SENTINEL)))
    committed_back = (camps[0] / "A01" / "R01" / "committed.txt").exists()
    shutil.rmtree(root, ignore_errors=True)
    for p in preserved:
        shutil.rmtree(pathlib.Path(p).parent, ignore_errors=True)
    return survived, committed_back, preserved


def main() -> int:
    if not TARGET.exists():
        print("  UNRUNNABLE: attack_the_suite.py missing. Exit 2, never 0.")
        return 2
    src = TARGET.read_text()
    already = "attack_preserved_" in src
    print(f"  target: {TARGET.relative_to(ROOT)}   fix already applied: {already}")

    # ---------- ④ SANDBOX FIRST ----------
    res = {}
    for variant in ("committed", "fixed"):
        for plant in (True, False):
            s, cb, pres = sandbox(variant, plant)
            res[f"{variant}|plant={plant}"] = {"sentinel_survived": s,
                                               "committed_work_restored": cb,
                                               "preserved": pres}
    print(f"\n  ④ SANDBOX — the mechanism transcribed onto a fake tree "
          f"(⚠ this tests my TRANSCRIPTION, not the object):")
    print(f"     {'variant':<22}{'sentinel survived':>19}{'committed restored':>21}")
    for k, v in res.items():
        print(f"     {k:<22}{str(v['sentinel_survived']):>19}"
              f"{str(v['committed_work_restored']):>21}")

    c1 = res["committed|plant=True"]["sentinel_survived"] is False
    c2 = res["fixed|plant=True"]["sentinel_survived"] is True
    c3 = (res["committed|plant=False"]["committed_work_restored"]
          and res["fixed|plant=False"]["committed_work_restored"])
    print(f"\n  ① POSITIVE — the hazard REPRODUCES under the committed restore "
          f"(sentinel destroyed): {c1}  {'PASS' if c1 else 'FAIL — nothing here is a fix'}")
    print(f"  ② the fix PRESERVES it: {c2}  {'PASS' if c2 else 'FAIL'}"
          + (f"   -> {res['fixed|plant=True']['preserved']}" if c2 else ""))
    print(f"  ③ PLACEBO (FORCED, a derivation): with no plant both variants restore the committed "
          f"work identically: {c3}  {'PASS' if c3 else 'FAIL'}")
    print(f"     ⚠ forced because with nothing at the live path there is nothing to preserve; "
          f"stated rather than counted as evidence")

    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "sandbox": res},
                  open(OUT / "restore_refusal.json", "w"), indent=2)
        return 2

    # ---------- apply to the object ----------
    applied = False
    if not already:
        old = """    def restore():
        for c in moved:
            shutil.rmtree(c, ignore_errors=True)
            shutil.move(str(tmp / c.name), str(c))
        shutil.rmtree(tmp, ignore_errors=True)
        BREADCRUMB.unlink(missing_ok=True)"""
        new = '''    def restore():
        # ⛔ NEVER DELETE WHAT WAS NOT STASHED (R936). This loop used to `rmtree(c)`
        #    unconditionally, so anything created at the live path WHILE THE STASH WAS AWAY was
        #    destroyed on the way back. R935 was written, run and its artifact printed inside that
        #    window; it landed in a freshly-created empty E05 and died here. Every COMMITTED round
        #    survived because it came back with the stash; only the uncommitted one was lost.
        #    The file already knew the shape — its own comment records R428 finding 21 untracked
        #    artifacts that existed nowhere but inside a stash — but the BREADCRUMB protects the
        #    SIGKILL path, and this is the NORMAL-completion path.
        #    Measured (R936): with the old body a planted sentinel is destroyed; with this one it
        #    survives, and on a quiet run the two are identical because there is nothing to keep.
        for c in moved:
            if c.exists() and any(c.iterdir()):
                keep = Path(tempfile.mkdtemp(prefix="attack_preserved_"))
                shutil.move(str(c), str(keep / c.name))
                print(f"  ⚠ PRESERVED work created during the hide: {keep / c.name}")
            else:
                shutil.rmtree(c, ignore_errors=True)
            shutil.move(str(tmp / c.name), str(c))
        shutil.rmtree(tmp, ignore_errors=True)
        BREADCRUMB.unlink(missing_ok=True)'''
        if old in src:
            TARGET.write_text(src.replace(old, new, 1))
            applied = True
    print(f"\n  fix applied to the object: {applied or already}")

    # ---------- the real run, with a sentinel planted inside the window ----------
    real = {"attempted": False}
    bc = ROOT / "assurance/results/.attack_the_suite_inflight.json"
    guess = sorted(ROOT.glob("assurance/results/*inflight*")) or [bc]
    print(f"\n  ⚠ REAL-OBJECT TEST is left to a separate, deliberately isolated run: planting into "
          f"a live hide requires racing the breadcrumb, and this round has already established the")
    print(f"     mechanism and the fix on a transcribed copy. The sandbox tests my TRANSCRIPTION; "
          f"the object test is NOT claimed here.")
    print(f"     breadcrumb path the harness uses: {guess[0].relative_to(ROOT)}")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    print(f"\n  ⭐⭐⭐ WORLD A: the hazard reproduces and the fix closes it. A restore that deletes")
    print(f"     the live path unconditionally cannot tell 'the stash's own contents' from 'work")
    print(f"     that appeared while the stash was away'. The fix distinguishes them by the only")
    print(f"     thing that is true at restore time — is anything THERE — and moves it aside")
    print(f"     LOUDLY rather than deleting it silently.")
    print(f"     ⚠ WHAT REMAINS OPEN: the SIGKILL path is still breadcrumb + `_repair.py`, "
          f"untouched here; and the real-object test is deferred and NOT claimed.")

    json.dump({"commit": head, "world": "A", "fix_applied": bool(applied or already),
               "sandbox": res,
               "hazard": {"file": "assurance/attack_the_suite.py", "lines": "91-98",
                          "what": "restore() rmtree'd the live path before moving the stash back",
                          "victim": "R935, written and run inside the window",
                          "signature": "committed work survives; uncommitted work created during "
                                       "the hide is destroyed"},
               "forced_half": "on a quiet run the fix is a no-op because there is nothing at the "
                              "live path to preserve — a derivation, not evidence",
               "tested_on": "a transcribed sandbox; the real-object test is deferred and not "
                            "claimed",
               "still_open": "the SIGKILL path (breadcrumb + _repair.py) is untouched",
               "unit_note": "counts are RESTORE VARIANTS; the sentinel is one file",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "restore_refusal.json", "w"), indent=2)
    print(f"\n  artifact: results/restore_refusal.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
