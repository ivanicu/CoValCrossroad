#!/usr/bin/env python3
"""R1085 — the 41 writing scripts, each run in its own clone, because in place they corrupt the tree.

R1084 could speak for 47 of 88 assurance scripts. The other 41 WRITE into the repository, and running
each twice in place made the second run read what the first wrote -- measured, expensively:
`ASSURANCE.md` truncated to 22 of 111 lines, `DEFECTS.json` down 395, `MANIFEST.json` churned 943.
Its NEXT named the remedy: **one isolated copy of the repository per run.** This is that round.

ESTIMAND        for each isolable writing script: is (exit code, normalised stdout) invariant between
                running from the clone's own root and running from an unrelated directory, when
                EVERY run gets a FRESH clone so no run can read another's writes?
                  Q1 moved       -- the pair differs
                  Q2 floor_dirty -- two fresh clones, both run from their own root, still differ
                                    (the determinism floor; without isolation R1084 could not
                                    measure it for these scripts at all)
IDENTIFICATION  identified for the 35 scripts whose paths are all relative or module-anchored.
                NOT identified for the 6 that carry an ABSOLUTE literal naming this repository:
                a clone cannot contain them -- they reach out and write to the original. Named,
                excluded, and demonstrated below with a synthetic world rather than by running them.
UNIT OF THE     a script, and whether its (rc, normalised stdout) moved between two CWDs, each run
  INSTRUMENT    in its own clone.
UNIT OF THE     the same.
  CLAIM
SCOPE           population: the 41 writers R1084 identified. instrument: `git clone --local
                --no-hardlinks` per run (~466 MB, ~0.4 s), CPython subprocess, 60 s timeout.
                baseline: the two-fresh-clone determinism floor. regime: this checkout.
⛔ MEASURED, ON THE FIRST FULL RUN: WORLD C FIRED. The round aborted with "the real repository
   changed while running backfilled_findings_are_rederivable.py" -- a script that launches
   `.venv/bin/python run.py` on round directories. Its grandchildren outlived a
   `subprocess.run(timeout=...)` that kills only the direct child, escaped the clone, and touched the
   original. **A clone is not isolation if the timeout does not bind.** The remedy is in `run_in`:
   `start_new_session=True` plus `os.killpg`, so the whole tree dies. The abort is kept in the
   history as the reason, because a safety control that has never fired is not known to work -- this
   one fired on its first real outing and stopped the round instead of reporting contaminated
   numbers.

WORLDS          A ISOLATION SUFFICES  a fresh clone per run makes the writers measurable: the floor
                                      is clean and any movement is about the CWD.
                B WRITES ARE THE SIGNAL even isolated, a script's own writes make its two runs
                                      differ -- because it writes and then reads within one run,
                                      and the content depends on the environment. Floor dirty.
                C ISOLATION LEAKS     the clone does not contain the script: the real repository
                                      changes. Then no number here is admissible and the round
                                      stops on the spot.
                Prediction matrix on (floor_dirty, real_repo_touched):
                  A -> (~0, no)     B -> (large, no)     C -> (any, YES -> abort)
KILL            pre-registered, evaluated ONLY if the control gate opens.
                  World A is KILLED if the floor is dirty for more than 10% of the isolable
                  scripts -- isolation would then not have bought a measurable instrument, and the
                  correct report is that these scripts are not comparable at all.
                  World C aborts the round: if the real repository's `git status` changes at ANY
                  point, every subsequent number is contaminated and the run exits 2.
POSITIVE CTRL   a planted script that writes a RELATIVE file. Required, both computed: the CLONE is
                dirtied (so the plant works and the harness can see a write) and the REAL repository
                is untouched (so isolation works). Retention 1.0; MDE is one file.
g=0 GUARD       a planted script that writes nothing leaves both clean. Without it, "the real repo
                is clean" would be satisfied before anything was planted.
NEGATIVE CTRL   the same plant with an ABSOLUTE path -- pointed at a SENTINEL in a scratch directory
                and never at this repository. It must escape the clone and hit the sentinel. That is
                the synthetic world showing why the 6 absolute-path scripts are excluded, built
                rather than asserted, and built somewhere it cannot do harm.
SHAM            the same operation MINUS the ingredient: run both arms in ONE clone, which is
                R1084's design in miniature. The gap between this and the isolated floor is exactly
                what isolation buys, in scripts.
PLACEBO         the isolated determinism floor itself: two fresh clones, both from their own root.
                Any movement there is the noise floor, measured rather than assumed.
NOISE FLOOR     the placebo above, per script.
MULTIPLICITY    all 41 reported -- 35 measured, 6 excluded with the reason.
SPECIFICATION   compare_on (rc only vs rc+stdout) x normalise (on/off); every cell a re-READING of
                the same captured runs, never a re-execution.
ARTIFACT        results/isolation_reaches_the_writers.json with the source hash and every capture.
REPRODUCIBILITY the captures are persisted so a later round can re-score without re-cloning.
IMPOSSIBLE      the 6 absolute-path scripts -- N/A. It would require rewriting them to derive their
                root from `__file__`, which is a repair, not a measurement.
                cross-repository -- N/A, a second assurance directory.
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "isolation_reaches_the_writers.json"
R1084 = next(ROOT.glob("E05_*/A27_*/R1084_*/results/parse_vs_run.json"), None)
TIMEOUT = 60
CLONES = pathlib.Path(tempfile.mkdtemp(prefix="r1085_", dir=str(ROOT.parent)))


def repo_state() -> str:
    """the real repository's fingerprint. If this ever moves, the round is over."""
    return subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                          capture_output=True, text=True).stdout


def has_absolute_self_reference(p: pathlib.Path) -> str | None:
    """a literal naming THIS repository escapes any clone -- isolation cannot help it."""
    try:
        tree = ast.parse(p.read_text(errors="replace"))
    except SyntaxError:
        return "unparsable"
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and str(ROOT) in n.value:
            return n.value[:70]
    return None


def clone(tag: str) -> pathlib.Path:
    d = CLONES / tag
    subprocess.run(["git", "clone", "--quiet", "--local", "--no-hardlinks", f"file://{ROOT}",
                    str(d)], capture_output=True, text=True, timeout=300, check=True)
    venv = ROOT / ".venv"
    if venv.exists():
        (d / ".venv").symlink_to(venv)      # ignored by git, referenced by 10 scripts
    return d


def run_in(clone_dir: pathlib.Path, rel: str, cwd: pathlib.Path, timeout=TIMEOUT):
    """⚠ THE TIMEOUT MUST KILL THE GROUP, NOT THE CHILD.

    Several assurance scripts spawn their own subprocesses -- `backfilled_findings_are_rederivable`
    launches `.venv/bin/python run.py` on round directories. `subprocess.run(timeout=...)` kills only
    the direct child and then keeps reading the pipes, which a living GRANDCHILD holds open; the
    timeout then does not bind, and a survivor can go on mutating a clone this round is about to
    delete. `start_new_session=True` puts the child in its own process group so the whole tree can
    be killed. Found while watching this round's own sweep sit on one script.
    """
    import os
    import signal
    proc = subprocess.Popen([sys.executable, str(clone_dir / rel)], cwd=str(cwd),
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                            start_new_session=True)
    try:
        out, _err = proc.communicate(timeout=timeout)
        return proc.returncode, out
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            proc.kill()
        try:
            proc.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            pass
        return None, ""


def dirty(d: pathlib.Path) -> int:
    return len(subprocess.run(["git", "-C", str(d), "status", "--porcelain"],
                              capture_output=True, text=True).stdout.splitlines())


def scrub(s: str, *paths) -> str:
    for p in paths:
        s = s.replace(str(p), "<PATH>")
    return re.sub(r"\d+\.\d+\s*s\b|\b\d{4}-\d\d-\d\d\b|/tmp/\S+|r1085_\S+", "<X>", s)


def read_capture(cap, normalise=True, on_stdout=True):
    ra, rb = cap["rc"]
    if ra is None or rb is None:
        return "UNVERIFIED_timeout"
    oa, ob = cap["out"]
    if normalise:
        oa, ob = scrub(oa, *cap["dirs"], ROOT), scrub(ob, *cap["dirs"], ROOT)
    return "MOVED" if (ra != rb or (on_stdout and oa != ob)) else "STABLE"


def main() -> int:
    if R1084 is None:
        print("  UNRUNNABLE: R1084's artifact is absent, so the population is unknown. Exit 2.")
        return 2
    writers = json.loads(R1084.read_text())["population"]["writers"]
    if not writers:
        print("  UNRUNNABLE: empty population. Exit 2, never 0.")
        return 2

    excluded = {n: has_absolute_self_reference(ROOT / "assurance" / n) for n in writers}
    excluded = {n: v for n, v in excluded.items() if v}
    isolable = [n for n in writers if n not in excluded]
    # a smoke limit, so a harness fault costs two clones and not thirty-five
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        isolable = isolable[:int(sys.argv[1])]

    baseline_state = repo_state()
    other = pathlib.Path(tempfile.mkdtemp(prefix="r1085_far_"))
    ctrl, caps, floor, sham, contaminated = {}, {}, {}, {}, None

    try:
        # ---------------- CONTROLS, before any measurement ----------------
        def plant_and_run(body: str, tag: str):
            """⛔ THE DELTA, NOT THE COUNT. The first version compared `dirty(c)` to zero -- but the
               plant FILE is itself written into the clone, so the clone is dirty by construction
               and the g=0 control could not pass whatever the plant did. §4's `control that cannot
               PASS`, built inside the round about isolation. Baseline is taken AFTER the plant is
               written and BEFORE it runs, so the number is what the EXECUTION changed."""
            c = clone(tag)
            (c / "assurance" / "_r1085_plant.py").write_text(body)
            before = dirty(c)
            rc, _out = run_in(c, "assurance/_r1085_plant.py", c)
            after = dirty(c)
            shutil.rmtree(c, ignore_errors=True)
            return rc, after - before

        sentinel = other / "sentinel.txt"
        sentinel.write_text("untouched")

        rc, d = plant_and_run('import pathlib\n'
                              'pathlib.Path("assurance/_written_by_the_plant.txt").write_text("x")\n'
                              'print("wrote")\n', "pos")
        ctrl["POSITIVE a relative write dirties the CLONE"] = d > 0
        ctrl["POSITIVE and leaves the REAL repository untouched"] = repo_state() == baseline_state

        rc, d = plant_and_run('print("I write nothing")\n', "g0")
        ctrl["g=0 a plant that writes nothing dirties neither"] = (
            d == 0 and repo_state() == baseline_state)

        rc, d = plant_and_run(f'import pathlib\n'
                              f'pathlib.Path({str(sentinel)!r}).write_text("ESCAPED")\n'
                              f'print("wrote absolute")\n', "neg")
        ctrl["NEGATIVE an ABSOLUTE write ESCAPES the clone (why 6 are excluded)"] = (
            sentinel.read_text() == "ESCAPED")
        ctrl["NEGATIVE and it still did not touch the REAL repository"] = (
            repo_state() == baseline_state)

        if not all(ctrl.values()):
            print("  the isolation harness does not separate the known cases. Exit 2, never 0.")
            for k, v in ctrl.items():
                print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
            return 2

        # ---------------- the sweep: three fresh clones per script ----------------
        for i, name in enumerate(isolable):
            rel = f"assurance/{name}"
            c1, c2, c3 = clone(f"a{i}"), clone(f"b{i}"), clone(f"c{i}")
            r1, o1 = run_in(c1, rel, c1)                 # arm A: from the clone's own root
            r2, o2 = run_in(c2, rel, other)              # arm B: from an unrelated directory
            r3, o3 = run_in(c3, rel, c3)                 # the floor: a second fresh clone, same cwd
            # SHAM: R1084's design in miniature -- both arms in ONE clone, no isolation
            r4, o4 = run_in(c1, rel, c1)                 # c1 already carries arm A's writes
            caps[name] = {"rc": (r1, r2), "out": (o1, o2), "dirs": (c1, c2)}
            floor[name] = read_capture({"rc": (r1, r3), "out": (o1, o3), "dirs": (c1, c3)})
            sham[name] = read_capture({"rc": (r1, r4), "out": (o1, o4), "dirs": (c1, c1)})
            for c in (c1, c2, c3):
                shutil.rmtree(c, ignore_errors=True)
            if repo_state() != baseline_state:
                contaminated = name
                break

        if contaminated:
            print(f"  ⛔ ABORT — the real repository changed while running {contaminated}. World C. "
                  f"Every number after this point would be contaminated. Exit 2, never 0.")
            return 2

        measured = [n for n in isolable if n in caps]
        eligible = [n for n in measured if floor[n] == "STABLE"]
        moved = [n for n in eligible if read_capture(caps[n]) == "MOVED"]
        floor_dirty = [n for n in measured if floor[n] == "MOVED"]
        timeouts = [n for n in measured if floor[n].startswith("UNVERIFIED")]
        sham_dirty = [n for n in measured if sham[n] == "MOVED"]

        ctrl["PLACEBO the isolated floor is clean for most of the population"] = (
            len(floor_dirty) <= 0.10 * max(1, len(measured)))
        gate_open = all(ctrl.values())

        spec = []
        for on_stdout in (True, False):
            for normalise in (True, False):
                spec.append({"compare_on": "rc+stdout" if on_stdout else "rc only",
                             "normalise": normalise, "scripts": len(eligible),
                             "moved": sum(1 for n in eligible
                                          if read_capture(caps[n], normalise, on_stdout) == "MOVED")})

        a_killed = gate_open and len(floor_dirty) > 0.10 * max(1, len(measured))
        if not gate_open:
            verdict = ("UNVERIFIED — a control failed, so no count licenses a claim about the "
                       "writers. A kill that can fire on a broken instrument is not a commitment.")
        elif a_killed:
            verdict = (f"world A (ISOLATION SUFFICES) is KILLED — the floor is dirty for "
                       f"{len(floor_dirty)} of {len(measured)}: a fresh clone per run is not enough "
                       f"to make these scripts comparable.")
        else:
            verdict = (f"world A survives — with a fresh clone per run the floor is clean for "
                       f"{len(eligible)} of {len(measured)} writing scripts, and {len(moved)} of "
                       f"them move between working directories. Without isolation the SAME floor is "
                       f"dirty for {len(sham_dirty)} of {len(measured)}, which is what the clone "
                       f"buys, in scripts.")

        art = {
            "round": "R1085",
            "question": "does one clone per run make the 41 writing scripts measurable?",
            "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
            "population": {"writers_from_R1084": len(writers), "isolable": len(isolable),
                           "excluded_absolute_self_reference": excluded,
                           "why_excluded": ("a literal naming this repository escapes any clone; "
                                            "isolation cannot contain it. Demonstrated by the "
                                            "NEGATIVE control against a scratch sentinel."),
                           "measured": len(measured), "timed_out": timeouts},
            "Q1_moved_between_cwds": moved,
            "Q2_floor_dirty_even_isolated": floor_dirty,
            "sham_no_isolation_floor_dirty": sham_dirty,
            "isolation_buys": len(sham_dirty) - len(floor_dirty),
            "controls": ctrl,
            "specification_curve": spec,
            "captures": {n: {"rc": list(c["rc"]),
                             "sha_a": hashlib.sha256(scrub(c["out"][0], *c["dirs"],
                                                           ROOT).encode()).hexdigest()[:16],
                             "sha_b": hashlib.sha256(scrub(c["out"][1], *c["dirs"],
                                                           ROOT).encode()).hexdigest()[:16],
                             "head_a": scrub(c["out"][0], *c["dirs"], ROOT)[:180],
                             "head_b": scrub(c["out"][1], *c["dirs"], ROOT)[:180]}
                         for n, c in sorted(caps.items())},
            "real_repository_unchanged_throughout": repo_state() == baseline_state,
            "kill": {"gate_open": gate_open, "world_A_killed": a_killed,
                     "world_C_aborted": bool(contaminated)},
            "verdict": verdict,
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

        print("R1085 — the writing scripts, one clone per run\n")
        print(f"  {len(writers)} writers from R1084 · {len(excluded)} carry an ABSOLUTE literal "
              f"naming this repo and are NOT ISOLABLE · {len(isolable)} measured")
        for n in sorted(excluded):
            print(f"      excluded  {n}")
        print("\n  CONTROLS")
        for k, v in ctrl.items():
            print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
        print(f"\n  THE MEASUREMENT — every run in its own fresh clone")
        print(f"    isolated floor clean          {len(eligible):>4} of {len(measured)}")
        print(f"    floor DIRTY even isolated     {len(floor_dirty):>4}  {floor_dirty[:6]}")
        print(f"    timed out                     {len(timeouts):>4}")
        print(f"    move between working dirs     {len(moved):>4}  {moved[:6]}")
        print(f"\n  SHAM — the same comparison with the ingredient (isolation) REMOVED")
        print(f"    floor dirty without isolation {len(sham_dirty):>4} of {len(measured)}")
        print(f"    ⭐ isolation buys {len(sham_dirty) - len(floor_dirty)} script(s) of measurable "
              f"floor")
        print(f"\n  SPECIFICATION CURVE — {len(spec)} cells, re-readings of the same runs")
        print(f"    {'compare_on':<12}{'normalise':>11}{'scripts':>9}{'moved':>8}")
        for s in spec:
            print(f"    {s['compare_on']:<12}{str(s['normalise']):>11}{s['scripts']:>9}"
                  f"{s['moved']:>8}")
        print(f"\n  real repository unchanged throughout: {repo_state() == baseline_state}")
        print(f"\n  KILL gate_open={gate_open}  world_A_killed={a_killed}")
        print(f"\n  {'⛔' if not gate_open or a_killed else '⭐'} {verdict}")
        print(f"\n  artifact {OUT.relative_to(ROOT)}")
        return 0
    finally:
        shutil.rmtree(CLONES, ignore_errors=True)
        shutil.rmtree(other, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
