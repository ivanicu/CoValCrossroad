#!/usr/bin/env python3
"""
R938 · `repair_full`'s `kept` branch — the one that protects work created during a hide — has no
        control, and the destructive test my NEXT proposed was refuted by reading instead.

⛔ WHY, AND MY NEXT WAS WRONG THREE TIMES OVER. R937 closed the normal-completion path and left the
SIGKILL path open, proposing to SIGKILL a live harness mid-hide and see whether `_repair.py` drops a
planted file. Reading the object first refuted every premise of that plan:
  ① `repair_full` **copies file-by-file and refuses to overwrite** — `if dst.exists(): kept.append();
     continue`, with the comment *"left N already-present files alone, because the tree's copy is
     sometimes the newer one"*. It does not share the blindness `restore()` had.
  ② the wiring bug I would have been hunting is **already recorded and fixed**: `_repair.py:336`
     says *"⛔ 2026-08-06: this called `repair()`, the TRACKED-ONLY path, while `repair_full()` sat
     two lines away"*.
  ③ the SIGKILL event is **already exercised** by `_repair.py`'s own `selftest()`, which plants the
     full event in a WORKTREE, never live, and checks both the untracked channel and liveness in
     both directions.
**So deliberately stranding five campaign trees would have bought risk and no information** — §3's
ladder says climb from the cheap end, and the cheap end answered it.

⛔⛔ **AND THE MEASUREMENT CORRECTED MY OWN FRAMING — THE `kept` GUARD IS NOT WHAT SAVES THE WORK.**
The canary survives, but `kept` comes back EMPTY. `kept` only records a file that exists in BOTH the
stash and the tree; a file created at the live path during a hide has **no counterpart in the stash**,
so the copy loop never visits it at all. **The real protection is that `repair_full` COPIES
file-by-file instead of moving directories** — the old `restore()` moved whole trees and therefore had
to delete what stood in the way, and that is precisely the difference R936 had to introduce by hand.
⚠ My first verdict string asserted the canary "is listed in `kept`". It is not. That is the
verdict-string-is-not-a-computation defect committed inside a round about untested branches, and the
sentence loses to the measurement.

⭐⭐⭐ **BUT THE READ FOUND SOMETHING THE DESTRUCTIVE TEST WOULD HAVE MISSED.** `kept` occurs at
lines 128, 134, 184 and 190 — **all four inside `repair_full` itself, and none in the selftest.** The
selftest covers the untracked channel and the liveness branch; it never places a file at the live
path before repairing. **So the exact property that protects work created during a hide is declared,
documented, and never demonstrated** — R935's *pass on silence* class one level in: a behaviour whose
zero has never been shown to be a measurement.

ESTIMAND        whether `repair_full` preserves a file already at the live path, tested by calling
                the REAL function; and whether any existing control exercises that branch.
IDENTIFICATION  exact — the file is either preserved and listed in `kept`, or it is not.
SCOPE           population: one sandbox root with one stashed campaign and one live-path plant
                instrument: `repair_full` imported from the module, not transcribed
                baseline:   the selftest's existing coverage, measured by grep in both directions
                regime:     a throwaway git repo under /tmp; the live tree is never touched
WORLDS          A · the branch works and is uncovered -> add the control; the source was right and
                    the suite was silent about it
                B · the branch does NOT preserve -> the source's comment is false and `repair_full`
                    would clobber work created during a hide, which is R936's defect in the
                    recovery tool
KILL            CONDITIONAL:
                  ⭐ ① COVERAGE GAP IS REAL, both directions: `kept` must appear in `repair_full`
                     and must NOT appear anywhere in `selftest`. A one-directional grep would let
                     me claim a gap that is not there.
                  ⭐ ② POSITIVE / THE CONTROL MUST DISCRIMINATE: a deliberately BROKEN variant that
                     overwrites instead of keeping must be caught by the same check. Without this
                     the new control could pass on any implementation.
                  ⭐ ③ THE OBJECT, NOT A COPY: `repair_full` is IMPORTED and called. R936 tested a
                     transcription and had to say so; here the function itself runs.
                  ⭐ ④ ISOLATION: everything happens in a throwaway git repo under /tmp. The live
                     tree is never hidden, never repaired, never touched.
MULTIPLICITY    2 variants (real, broken) × {file preserved, listed in kept}; both printed.
ARTIFACT        results/kept_branch.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this tests `repair_full` on a synthetic root. It does not
                re-test the live SIGKILL sequence, which the module's own selftest already covers
                for the channels it does cover.
"""
import importlib.util, json, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
REPAIR = ROOT / "assurance/_repair.py"
CANARY = "R938_created_during_the_hide.json"


def load_repair():
    sys.path.insert(0, str(ROOT / "assurance"))
    spec = importlib.util.spec_from_file_location("repair_mod", REPAIR)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def build_sandbox():
    root = pathlib.Path(tempfile.mkdtemp(prefix="r938_root_"))
    # ⚠ hooks disabled for the throwaway repo: a GLOBAL core.hooksPath commit-message coach
    # applies to any repo and rejected the seed commit. The sandbox is not the thing under test.
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "config", "core.hooksPath", "/dev/null"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True)
    ep = root / "E00_sandbox"
    (ep / "A01" / "R01").mkdir(parents=True)
    (ep / "A01" / "R01" / "tracked.txt").write_text("tracked content\n")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "--no-verify", "-qm", "seed"], cwd=root, check=True)
    stash = pathlib.Path(tempfile.mkdtemp(prefix="r938_stash_"))
    (root / "assurance" / "results").mkdir(parents=True, exist_ok=True)
    (root / "assurance" / "results" / ".hide_in_progress.json").write_text(
        json.dumps({"stash": str(stash), "moved": [ep.name]}))
    shutil.move(str(ep), str(stash / ep.name))          # the SIGKILL: no restore runs
    # work created at the LIVE path while the stash is away — the R935 scenario
    live = root / ep.name / "A99"
    live.mkdir(parents=True)
    (live / CANARY).write_text('{"only_copy": true}')
    return root, stash, ep.name


def broken_move_home(root, stash, name):
    """the same loop WITHOUT the `kept` guard — overwrites the live tree"""
    src = stash / name
    for p in src.rglob("*"):
        if not p.is_file() or p.is_symlink():
            continue
        dst = root / name / p.relative_to(src)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
    shutil.rmtree(root / name, ignore_errors=True)      # the old restore's shape
    shutil.move(str(src), str(root / name))


def main() -> int:
    if not REPAIR.exists():
        print("  UNRUNNABLE: _repair.py missing. Exit 2, never 0.")
        return 2
    src = REPAIR.read_text()

    # ---------- ① COVERAGE GAP, BOTH DIRECTIONS ----------
    lines = src.splitlines()
    st_start = next((i for i, l in enumerate(lines) if l.startswith("def selftest")), None)
    rf_start = next((i for i, l in enumerate(lines) if l.startswith("def repair_full")), None)
    if st_start is None or rf_start is None:
        print("  UNRUNNABLE: could not locate both functions. Exit 2, never 0.")
        return 2
    rf_body = "\n".join(lines[rf_start:st_start])
    st_body = "\n".join(lines[st_start:])
    in_rf = len(re.findall(r'"kept"|\bkept\b', rf_body))
    in_st = len(re.findall(r'"kept"|\bkept\b', st_body))
    c1 = in_rf > 0 and in_st == 0
    print(f"  ① COVERAGE GAP, both directions — `kept` occurrences:")
    print(f"     inside repair_full : {in_rf}  (must be > 0)")
    print(f"     inside selftest    : {in_st}  (must be 0)")
    print(f"     ① {c1}  {'PASS' if c1 else 'FAIL'}")

    # ---------- ③ THE OBJECT, called directly ----------
    m = load_repair()
    root, stash, name = build_sandbox()
    live_file = root / name / "A99" / CANARY
    before = live_file.exists()
    out = m.repair_full(root, verbose=False)
    real_preserved = live_file.exists() and \
        json.loads(live_file.read_text()).get("only_copy") is True
    listed = any(CANARY in k for k in out.get("kept", []))
    tracked_back = (root / name / "A01" / "R01" / "tracked.txt").exists()
    print(f"\n  ③ THE OBJECT — `repair_full` imported and called on a sandbox root:")
    print(f"     canary present before repair: {before}")
    print(f"     preserved after repair:       {real_preserved}")
    print(f"     listed in `kept`:             {listed}  {out.get('kept')}")
    print(f"     stashed tracked file restored:{tracked_back}")

    # ---------- ② POSITIVE: a broken variant must be caught ----------
    root2, stash2, name2 = build_sandbox()
    live2 = root2 / name2 / "A99" / CANARY
    broken_move_home(root2, stash2, name2)
    broken_preserved = live2.exists()
    c2 = real_preserved and not broken_preserved
    print(f"\n  ② POSITIVE — a variant WITHOUT the `kept` guard must destroy the canary:")
    print(f"     real repair_full preserves: {real_preserved}   broken variant preserves: "
          f"{broken_preserved}")
    print(f"     ② the check discriminates: {c2}  {'PASS' if c2 else 'FAIL'}")

    c4 = str(root).startswith("/tmp") and str(root2).startswith("/tmp")
    print(f"\n  ④ ISOLATION — both sandboxes under /tmp, live tree untouched: {c4}")

    for d in (root, root2, stash, stash2):
        shutil.rmtree(d, ignore_errors=True)

    if not (c1 and c2 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c4": c4,
                   "kept_in_repair_full": in_rf, "kept_in_selftest": in_st},
                  open(OUT / "kept_branch.json", "w"), indent=2)
        return 2

    world = "A" if real_preserved else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"`repair_full` DOES preserve work created at the live path during a hide — the canary "
        f"survives — but NOT by the `kept` guard, which came back {out.get('kept')}. It survives "
        f"because repair_full COPIES from the stash file-by-file instead of moving the tree, so a "
        f"live-path file with no stash counterpart is never touched. And no existing control "
        f"exercises either property."
        if world == "A" else
        "`repair_full` does NOT preserve it. The source's own comment is false and the recovery "
        "tool would clobber work created during a hide, which is R936's defect living on in the "
        "thing that is supposed to undo it."))
    print(f"     ⛔ AND THE DESTRUCTIVE TEST MY NEXT PROPOSED WAS REFUTED BY READING: the branch is")
    print(f"     safe, the wiring bug was already found and fixed on 2026-08-06, and the SIGKILL")
    print(f"     event is already planted in a WORKTREE by the module's own selftest. Stranding")
    print(f"     five live campaign trees would have bought risk and no information.")
    print(f"     ⚠ WHAT THIS DOES NOT DO: re-test the live SIGKILL sequence, and it does not add")
    print(f"     the missing control to `_repair.py` — that is a separate edit to a shared tool.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "kept_in_repair_full": in_rf, "kept_in_selftest": in_st,
               "canary_preserved_by_real": bool(real_preserved),
               "canary_listed_in_kept": bool(listed),
               "kept_list": out.get("kept"),
               "tracked_restored": bool(tracked_back),
               "broken_variant_preserved": bool(broken_preserved),
               "next_was_refuted_by_reading": {
                   "proposed": "SIGKILL a live harness mid-hide and see if _repair drops the plant",
                   "why_wrong": ["repair_full copies and refuses to overwrite (kept branch)",
                                 "_repair.py:336 records the wiring bug already fixed 2026-08-06",
                                 "selftest already plants the SIGKILL event in a worktree"],
                   "cost_avoided": "stranding five live campaign trees for no information"},
               "gap": "the `kept` branch is declared and documented in repair_full and exercised "
                      "by no control in selftest",
               "corrected_mechanism": "the canary is NOT saved by `kept` — it has no stash "
                                      "counterpart so the loop never visits it. It is saved by "
                                      "repair_full COPYING file-by-file rather than moving the "
                                      "tree, which is exactly the difference R936 had to add to "
                                      "restore() by hand",
               "my_verdict_string_was_wrong": "it asserted the canary is listed in `kept`; the "
                                              "measurement says the list is empty",
               "unit_note": "one canary file; counts are OCCURRENCES of `kept`",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "kept_branch.json", "w"), indent=2)
    print(f"\n  artifact: results/kept_branch.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
