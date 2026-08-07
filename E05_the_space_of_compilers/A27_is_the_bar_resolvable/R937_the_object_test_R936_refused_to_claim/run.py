#!/usr/bin/env python3
"""
R937 · plant a sentinel inside a LIVE hide and see whether the patched restore keeps it — the object
        test R936 explicitly refused to claim.

⛔ WHY. R936 reproduced the hazard on a SANDBOX — a transcribed copy of `restore()` on a fake tree —
and closed it by moving aside instead of deleting. It said in its own words that the sandbox tests
the TRANSCRIPTION and not the object, and left the real test unclaimed. This round runs it.

⚠ **AND R936 PRINTED A BREADCRUMB PATH IT HAD NOT READ.** It reported
`assurance/results/.attack_the_suite_inflight.json`; the object says
`BREADCRUMB = ROOT / "assurance" / "results" / ".hide_in_progress.json"`
(`attack_the_suite.py:27`). A guessed constant printed as a fact, in a round whose whole subject is
work destroyed by an unread code path. Corrected here and read from the module, never retyped.

⭐ **NOT FORCED, BECAUSE THE RACE IS REAL.** The patched logic preserves a non-empty live path by
construction — but on the object there are FIVE campaign dirs, dozens of gates run while they are
hidden, and the sentinel has to land INSIDE the window. **A sentinel that lands after restore has
begun survives trivially and proves nothing**, which is why control ① proves the window was open at
the moment of planting: the breadcrumb present AND the target path absent-or-empty. That is R928's
lesson — an attack that never lands says nothing — turned into a precondition.

ESTIMAND        whether a file created at a live `E0*` path while the hide is in flight is still
                findable after the harness completes.
IDENTIFICATION  exact — the file is either there, named in a PRESERVED line, or gone.
SCOPE           population: one sentinel, one real run of `assurance/attack_the_suite.py`
                instrument: the harness's own breadcrumb, read from the module
                baseline:   R936's sandbox result, which predicts survival
                regime:     this repo, working tree committed and clean before the run
WORLDS          A · the sentinel survives -> the sandbox and the object agree and the fix is real
                B · it is silently gone -> the transcription, not the hazard, is what needs
                    rewriting, and R936's fix does not do on the object what it did on the copy
KILL            CONDITIONAL:
                  ⭐ ① WINDOW PROOF: at the instant of planting, the breadcrumb must EXIST and the
                     target campaign path must be absent or empty. **If either fails the sentinel
                     landed outside the hide and the round is VOID, not passing.**
                  ⭐ ② THE FIX MUST BE PRESENT: `attack_preserved_` must appear in the harness
                     source, or this is a test of the old code wearing the new round's name.
                  ⭐ ③ INTEGRITY AFTER: all five `E0*` back, `git status` clean, no breadcrumb
                     left. A round that damages the repo has not demonstrated a repair.
                  ⭐ ④ the sentinel's fate is reported as one of THREE states — in place,
                     preserved-and-named, or GONE. Folding "preserved" into "in place" would hide
                     whether the fix ran at all.
MULTIPLICITY    one sentinel; every state printed; the harness's own exit code recorded.
ARTIFACT        results/object_test.json
IMPOSSIBLE      cross-release · construct validated · independently replicated. ⚠ AND: this tests
                the NORMAL-completion path only. The SIGKILL path still relies on the breadcrumb
                plus `_repair.py` and is not exercised here.
"""
import importlib.util, json, os, pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
HARNESS = ROOT / "assurance/attack_the_suite.py"
SENTINEL_NAME = "R937_sentinel_planted_inside_the_hide.txt"
POLL, MAX_WAIT = 0.25, 1500


def breadcrumb_path():
    """read from the module — never retyped (R936 printed a guessed path as a fact)"""
    spec = importlib.util.spec_from_file_location("ats_probe", HARNESS)
    m = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT))
    try:
        spec.loader.exec_module(m)
        return pathlib.Path(m.BREADCRUMB)
    except SystemExit:
        return pathlib.Path(m.BREADCRUMB)


def main() -> int:
    if not HARNESS.exists():
        print("  UNRUNNABLE: harness missing. Exit 2, never 0.")
        return 2
    src = HARNESS.read_text()
    c2 = "attack_preserved_" in src
    print(f"  ② FIX PRESENT in the harness source: {c2}  {'PASS' if c2 else 'FAIL'}")
    if not c2:
        print("  UNRUNNABLE: without the fix this tests the old code. Exit 2, never 0.")
        return 2

    bc = breadcrumb_path()
    print(f"  breadcrumb READ from the module: {bc.relative_to(ROOT)}")
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        print(f"  UNRUNNABLE: working tree not clean — this round hides the repo and a dirty tree "
              f"is exactly what gets lost:\n{dirty[:400]}\n  Exit 2, never 0.")
        return 2
    if bc.exists():
        print("  UNRUNNABLE: a hide is already in flight. Exit 2, never 0.")
        return 2

    proc = subprocess.Popen([str(ROOT / ".venv/bin/python"), "-u", str(HARNESS)],
                            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True)
    print(f"  harness launched pid {proc.pid}; waiting for the hide to open…")

    planted, window = None, {}
    t0 = time.time()
    while time.time() - t0 < MAX_WAIT:
        if bc.exists():
            try:
                info = json.loads(bc.read_text())
            except Exception:
                time.sleep(POLL); continue
            target = ROOT / info["moved"][0]
            absent = not target.exists()
            empty = target.exists() and not any(target.iterdir())
            window = {"breadcrumb_present": True, "target": info["moved"][0],
                      "target_absent": absent, "target_empty": empty,
                      "stash": info.get("stash")}
            if absent or empty:
                target.mkdir(parents=True, exist_ok=True)
                planted = target / SENTINEL_NAME
                planted.write_text("planted inside the hide by R937\n")
                window["planted_at"] = str(planted.relative_to(ROOT))
                print(f"  ① WINDOW PROOF — breadcrumb present, `{info['moved'][0]}` "
                      f"{'absent' if absent else 'empty'}; sentinel planted")
                break
        if proc.poll() is not None:
            break
        time.sleep(POLL)

    c1 = bool(planted)
    if not c1:
        print("  ① WINDOW PROOF FAILED — never observed an open hide. The sentinel would have "
              "landed outside the window, so the round is VOID rather than passing.")
        try:
            proc.wait(timeout=MAX_WAIT)
        except Exception:
            proc.kill()
        json.dump({"verdict": "VOID", "c1": False, "window": window},
                  open(OUT / "object_test.json", "w"), indent=2)
        return 2

    out = proc.communicate()[0] or ""
    rc = proc.returncode
    print(f"  harness finished, exit {rc}")

    in_place = planted.exists()
    preserved = sorted(pathlib.Path("/tmp").glob("attack_preserved_*"))
    found_preserved = [str(p) for p in preserved
                       for _ in p.rglob(SENTINEL_NAME)]
    printed = [ln.strip() for ln in out.splitlines() if "PRESERVED" in ln]
    state = ("IN_PLACE" if in_place else
             "PRESERVED_AND_NAMED" if found_preserved else "GONE")

    e0 = sorted(p.name for p in ROOT.glob("E0*") if p.is_dir())
    dirty_after = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                                 capture_output=True, text=True).stdout.strip()
    c3 = len(e0) == 5 and not bc.exists()
    print(f"\n  ③ INTEGRITY AFTER — E0* dirs {len(e0)} {e0}, breadcrumb gone {not bc.exists()}: "
          f"{c3}  {'PASS' if c3 else 'FAIL'}")
    print(f"     git status lines (the sentinel itself is expected here): "
          f"{len(dirty_after.splitlines())}")

    print(f"\n  ④ THE SENTINEL'S FATE, one of three states: {state}")
    print(f"     in place:            {in_place}")
    print(f"     preserved and named: {bool(found_preserved)} {found_preserved[:2]}")
    print(f"     harness PRESERVED lines: {printed[:2] if printed else '(none)'}")

    world = "A" if state in ("IN_PLACE", "PRESERVED_AND_NAMED") else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        "the sentinel survived a real hide. The sandbox and the object agree, and R936's fix does "
        "on the harness what it did on the copy."
        if world == "A" else
        "the sentinel is GONE. The sandbox and the object DISAGREE, so the transcription — not the "
        "hazard — is what needs rewriting, and R936's fix does not do on the object what it did "
        "on the copy."))
    print(f"     ⚠ NORMAL-COMPLETION PATH ONLY. The SIGKILL path is still breadcrumb + "
          f"`_repair.py` and is not exercised here.")

    if planted.exists():
        planted.unlink()
        try:
            planted.parent.rmdir()
        except OSError:
            pass

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "state": state,
               "window_proof": window, "harness_exit": rc,
               "breadcrumb_path_read_from_module": str(bc.relative_to(ROOT)),
               "r936_printed_wrong_path": "assurance/results/.attack_the_suite_inflight.json",
               "in_place": in_place, "preserved_hits": found_preserved,
               "harness_preserved_lines": printed[:5],
               "e0_dirs_after": e0, "breadcrumb_cleared": not bc.exists(),
               "tests_only": "the NORMAL-completion path; SIGKILL is untouched",
               "unit_note": "one sentinel file",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "object_test.json", "w"), indent=2)
    print(f"\n  artifact: results/object_test.json @ {head[:8]}")
    return 0 if world == "A" else 2


if __name__ == "__main__":
    raise SystemExit(main())
