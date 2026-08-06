#!/usr/bin/env python3
"""assurance/run_all.py — run EVERY gate and publish the denominator.

⛔ WHY THIS FILE EXISTS. There are 52 files in `assurance/`. For an entire campaign session I ran
FOUR of them and reported "all four gates PASS" after every round. Nothing was lying: each of the
four did pass. But "all four" was read — by me, in my own reports — as "the assurance layer is
green", and there was no runner, no Makefile and no manifest to contradict it.

⭐ THIS IS EXACTLY THE DEFECT R476 FOUND ONE LEVEL DOWN. `definition_matches_the_record.py` reported
"302 of 302 assertions" — a count with no denominator — and a corrupted number sailed through. The
same shape at the suite level: a count of gates run, with no count of gates that exist. **A numerator
reported alone will be read as a proportion. Always.**

⚠ AND THE GATES THAT WENT UNRUN WERE NOT RANDOM. `seed_filter_is_disclosed.py` is precisely the
defect R481 retracted (entry 304, an undeclared seed axis). `next_gradient_is_new.py` checks the
sentence type that produced retractions 300 and 302. The unrun subset contained the checks aimed at
the errors actually being made.

WHAT THIS DOES
    discover  every *.py in assurance/ that is a GATE (not a helper, not an applier)
    run       each in a subprocess with a timeout, capturing its exit code
    classify  0 = PASS · 1 = FAIL · 2 = UNRUNNABLE/empty-population · other = ERROR · timeout
    report    the whole table, PASS COUNT **beside the denominator**, never alone
    exit      1 if any gate FAILs; 2 if the discovered gate population is EMPTY (§4: a gate that
              reports success having examined nothing must exit 2, and that applies to this one)

POSITIVE CONTROL (`--selftest`)
    Writes a temporary gate that exits 1 and one that exits 2, runs discovery, and requires the
    runner to classify both correctly and to return a non-zero overall status. A runner that cannot
    detect a failing gate is a runner that reports green forever — and that is the failure this file
    was written to end, so it must be the failure this file can itself be caught committing.
"""
from __future__ import annotations
import collections, os, pathlib, subprocess, sys, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parent
# Helpers and appliers are NOT gates: they mutate state or expose functions rather than ruling.
NOT_A_GATE = {"run_all", "DEFECTS", "HEADLINES", "manifest", "pueue_wait",
              "clause3_as_written", "generate_round_index",
              # ⚠ audit_the_auditors is a META-GATE: it runs every gate in this directory,
              # including this runner. R498 measured the cycle (run_all discovers it; it
              # discovers run_all) and measured it at >=150s against this suite's 90s timeout,
              # so the suite could NEVER exit 0 while it was inside. A runner that cannot pass
              # gets replaced by a decoration -- which is exactly what happened for twenty
              # rounds, entry 335. Excluded here for the same reason run_all excludes itself,
              # and RUN SEPARATELY, which is printed below so the exclusion is never invisible.
              "audit_the_auditors"}
META_GATES = {"audit_the_auditors"}
PREFIX_SKIP = ("_", "apply_")
# Gates that MOVE the epoch directories out of the live tree. Killing one of these does not lose a
# verdict, it loses the repository's working tree into a `mkdtemp` nobody can name. Kept as an
# explicit list rather than detected, because a heuristic that misses one fails silently in the
# expensive direction — and there are two, both named in `_repair.py`'s docstring.
MUTATES_TREE = {"attack_the_suite", "attack_every_check"}
MUTATES_TREE_TIMEOUT = 600      # measured 40.9s alone in a worktree; 600 is room for a loaded box


def discover(root: pathlib.Path = ROOT) -> list[pathlib.Path]:
    return sorted(p for p in root.glob("*.py")
                  if p.stem not in NOT_A_GATE and not p.stem.startswith(PREFIX_SKIP))


def run_one(p: pathlib.Path, timeout: int = 90) -> tuple[str, int, float, str]:
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True,
                           timeout=timeout, cwd=ROOT.parent)
        rc, out = r.returncode, (r.stdout + r.stderr)
    except subprocess.TimeoutExpired:
        return p.stem, -1, time.time()-t0, f"TIMEOUT after {timeout}s"
    tag = next((l.strip() for l in out.splitlines()
                if any(m in l for m in ("⛔", "FAIL", "Error", "Traceback"))), "")
    # ⛔ THE KIND IS COMPUTED ON THE FULL OUTPUT AND CARRIED, never re-derived from the extract.
    # The first version classified `msg` -- a one-line display extract -- and
    # `next_gradient_labels_its_hypotheses` would have been read as LIVE-DEBT, because its extract is
    # "POSITIVE CONTROL the two NEXT blo..." while "a control misbehaved" is three lines later.
    # The classifier's input was not the population the claim was about (§4, unit vs unit).
    kind = classify_fail(out) if rc == 1 else ""
    disp = (tag or (out.strip().splitlines() or [""])[-1])[:120]
    return p.stem, rc, time.time()-t0, (f"[{kind}] {disp}" if kind else disp)


# ---- THE FOURTH BUCKET ---------------------------------------------------------------------------
# ⛔ WHY. The census returned 9 FAIL, and reading them showed three unlike things pooled under one
# word: live debt, a gate failing BY DESIGN as a standing register (`attack_no_withdrawn_framings`
# reports "1/1 KNOWN GAPS still open, as documented", and its own comment says a CAUGHT known-gap
# would also fail — it cannot exit 0), and a gate whose OWN CONTROL broke ("FAIL: a control
# misbehaved; the counts above are silence"), which says nothing about the repo at all.
# A single count of 9 conflates a defect, a ledger entry and an instrument fault. It will be quoted.
#
# PROXY LEDGER (CLAUDE.md P6) — this classifier reads MESSAGES, not structure:
#   PROPERTY   "this FAIL is / is not a live defect"
#   PROXY      the gate's stdout contains a control-failure or known-gap phrase
#   IMPLICATION  phrase present ⇒ not live debt.   ABSENCE PROVES NOTHING: a gate whose control
#                broke silently, or whose register is undeclared, is classified LIVE and must be.
#   SAFE SIDE  the classifier may only DEMOTE a FAIL out of "live"; it may never promote one in.
CONTROL_BROKE = ("a control misbehaved", "counts above are silence", "control failed")
BY_DESIGN     = ("known gaps still open, as documented", "cannot exit 0 by design")


def classify_fail(out: str) -> str:
    low = out.lower()
    if any(s in low for s in CONTROL_BROKE):
        return "CONTROL-BROKE"
    if any(s in low for s in BY_DESIGN):
        return "BY-DESIGN"
    return "LIVE-DEBT"


def _classifier_selftest() -> bool:
    """POSITIVE CONTROL on the classifier, using the two REAL messages that motivated it, plus a
    negative: ordinary failure text must stay LIVE-DEBT. A classifier validated only on strings I
    invented would be validated against my imagination (§4)."""
    cases = [
        ("FAIL: a control misbehaved; the counts above are silence.", "CONTROL-BROKE"),
        ("1/1 KNOWN GAPS still open, as documented -- a claim inside a declared payload path",
         "BY-DESIGN"),
        ("FINDING: 1 round(s) apply the filter and are not registered:", "LIVE-DEBT"),
        ("", "LIVE-DEBT"),                       # silence is never an acquittal
    ]
    ok = True
    for text, want in cases:
        got = classify_fail(text)
        ok &= got == want
        print(f"    {want:<14} <- {got:<14} {'ok' if got == want else '⛔'}  {text[:52]!r}")
    return ok


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    # ⛔ REPAIR ON ENTRY, BECAUSE THIS RUNNER IS THE THING THAT BREAKS THE TREE.
    #    `attack_the_suite` MOVES every E##_ epoch aside to prove the gates fail on an empty
    #    population, and restores in a `finally:` -- which SIGKILL does not run. This runner kills
    #    every gate at a flat 90s (`run_one`), and `attack_the_suite` does not finish in 90s: on
    #    2026-08-06 it was killed at 90.1s and left the ENTIRE tree, 2,911 files, in /tmp.
    #    ⭐ /tmp then held ELEVEN orphaned `attack_rounds_*` stashes over four days -- R428 counted
    #    eight over two and diagnosed it, and the rate did not fall, because the diagnosis produced
    #    `_repair.py` and nothing CALLED it. It was reachable from `attack_the_suite` (which is
    #    the gate that gets killed) and from its own `__main__` (which nobody runs on a schedule).
    #    The runner that causes the damage was the one place it was not wired.
    #    `repair_full` never overwrites an existing path and is a no-op with no breadcrumb, so this
    #    costs a healthy tree one `git ls-files --deleted`.
    try:
        from _repair import repair_full
        r = repair_full(verbose=False)
        if r["moved_home"] or r["still_missing"] or r["restored"]:
            print(f"  ⛔ ENTRY REPAIR: a previous run left the tree damaged. "
                  f"recovered {len(r['moved_home'])} untracked from the stash · "
                  f"{len(r['restored'])} tracked from the index · "
                  f"{len(r['still_missing'])} STILL MISSING")
    except Exception as e:                       # a broken repair must not hide the suite
        print(f"  ⚠ ENTRY REPAIR UNAVAILABLE ({type(e).__name__}: {e}) — the tree was NOT checked, "
              f"so a green run below is not evidence the population was whole.")
    gates = discover()
    print(f"  META-gates excluded from this suite and RUN SEPARATELY: "
          f"{sorted(META_GATES)} — see entry 335 for why an unpassable runner "
          f"gets replaced by a decoration.")
    if not gates:                       # §4: empty population must EXIT 2, never 0
        print("⛔ no gates discovered — the runner examined nothing. EXIT 2.")
        return 2
    # ⚠ SERIAL WAS THE REAL REASON THIS RUNNER WAS ABANDONED. 45 gates x a 90s timeout is 68
    # minutes worst case on a 24-thread machine using one of them -- unusable as a pre-commit
    # check, so it was replaced by a for-loop that printed verdicts and blocked nothing (entry
    # 335). Excluding the meta-gate made the suite ABLE to exit 0; this makes it worth running.
    # Threads, not processes: run_one is subprocess-bound, so the GIL is irrelevant.
    # `--serial` keeps the old path so correctness can be CHECKED against it, not assumed.
    jobs = 1 if "--serial" in sys.argv else min(12, (os.cpu_count() or 4) - 2)
    # ⛔ A GATE THAT MOVES THE TREE MAY NOT RUN INSIDE THE POOL, AND THE REASON IS MEASURED.
    #    `attack_the_suite` and `attack_every_check` hide every E##_ epoch and restore in a
    #    `finally:`, which SIGKILL does not run. On 2026-08-06 `attack_the_suite` was killed at
    #    90.1s here and left 2,911 files in /tmp.
    #    ⭐ THE OBVIOUS DIAGNOSIS WAS WRONG AND I HAD ALREADY WRITTEN IT DOWN: "the gate cannot
    #    finish in 90s." Measured alone in a linked worktree it finishes in 40.9s -- comfortably
    #    inside. It exceeded 90s because it was competing with ELEVEN OTHER GATES for the machine.
    #    So the defect is not the timeout's value; it is that the only gates whose interruption
    #    DESTROYS STATE were the ones made slowest by the pool. Raising the timeout would have
    #    made the window rarer and left the mechanism intact.
    #    They therefore run ALONE, after the pool, with a timeout set from the measurement plus
    #    room for a loaded machine. Serial cost: ~40s each, paid once.
    pool = [p for p in gates if p.stem not in MUTATES_TREE]
    solo = [p for p in gates if p.stem in MUTATES_TREE]
    if jobs > 1:
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=jobs) as ex:
            rows = list(ex.map(run_one, pool))
    else:
        rows = [run_one(p) for p in pool]
    for p in solo:
        print(f"  … {p.stem} runs ALONE (it moves the tree; an interrupted hide is not a red line, "
              f"it is a lost round)")
        rows.append(run_one(p, timeout=MUTATES_TREE_TIMEOUT))
    print(f"  ran {len(gates)} gates with {jobs} worker(s) · {len(solo)} run serially after the pool")
    buckets = {"PASS": [], "FAIL": [], "UNRUNNABLE": [], "ERROR": []}
    for name, rc, el, msg in rows:
        b = "PASS" if rc == 0 else "FAIL" if rc == 1 else "UNRUNNABLE" if rc == 2 else "ERROR"
        buckets[b].append((name, rc, el, msg))
    for b in ("FAIL", "ERROR", "UNRUNNABLE"):
        for name, rc, el, msg in buckets[b]:
            print(f"  {b:<11} {name:<48} rc={rc:<3} {el:5.1f}s  {msg}")
    kinds = collections.Counter(m.split("]")[0].lstrip("[") for _n, _r, _e, m in buckets["FAIL"])
    if kinds:
        print(f"\n  FAIL breakdown — a single count conflates three unlike things:")
        for k in ("LIVE-DEBT", "BY-DESIGN", "CONTROL-BROKE"):
            print(f"    {k:<14} {kinds.get(k, 0)}")
        print(f"    ⚠ PROXY: reads messages, may only DEMOTE out of LIVE-DEBT, never promote in.")
    n = len(rows)
    print(f"\n  PASS {len(buckets['PASS'])} of {n}   FAIL {len(buckets['FAIL'])}   "
          f"UNRUNNABLE {len(buckets['UNRUNNABLE'])}   ERROR {len(buckets['ERROR'])}")
    print(f"  ⭐ the denominator is {n}. A pass count quoted without it is not a coverage claim.")
    return 1 if buckets["FAIL"] or buckets["ERROR"] else 0


def selftest() -> int:
    """The runner must detect a gate that fails. Otherwise it reports green forever."""
    ok = True
    with tempfile.TemporaryDirectory() as d:
        dd = pathlib.Path(d)
        (dd/"zz_fails.py").write_text("import sys; print('⛔ deliberate'); sys.exit(1)")
        (dd/"zz_empty.py").write_text("import sys; print('nothing to examine'); sys.exit(2)")
        (dd/"zz_ok.py").write_text("print('fine')")
        (dd/"_helper.py").write_text("print('should be skipped')")
        found = {p.stem for p in discover(dd)}
        good = found == {"zz_fails", "zz_empty", "zz_ok"}
        ok &= good
        print(f"  POSITIVE  discovery finds gates and skips `_helper`: {sorted(found)}  "
              f"{'PASS' if good else '⛔ FAIL'}")
        codes = {p.stem: run_one(p)[1] for p in discover(dd)}
        exp = {"zz_fails": 1, "zz_empty": 2, "zz_ok": 0}
        good2 = codes == exp
        ok &= good2
        print(f"  POSITIVE  each exit code classified correctly: {codes}  "
              f"{'PASS' if good2 else '⛔ FAIL'}")
        # ⭐ THE TIMEOUT PATH, WHICH THE FIRST SELFTEST DID NOT EXERCISE. A gate that spawns a
        # grandchild and exits is the shape that defeated `subprocess.run(timeout=)`: the child dies,
        # the grandchild holds the pipe, and the runner blocks forever with no output. Measured
        # before the fix: a real gate ran 98s against a 75s limit. This plants that exact shape and
        # requires the runner to return within a small multiple of the timeout.
        (dd/"zz_hangs.py").write_text(
            "import subprocess,sys,time\n"
            "subprocess.Popen([sys.executable,'-c','import time; time.sleep(600)'])\n"
            "time.sleep(600)\n")
        t0 = time.time()
        name, rc, el, msg = run_one(dd/"zz_hangs.py", timeout=3)
        wall = time.time() - t0
        good4 = rc == -1 and wall < 12
        ok &= good4
        print(f"  TIMEOUT   a gate spawning a grandchild is killed: rc={rc} in {wall:.1f}s "
              f"(limit 3s)  {'PASS' if good4 else '⛔ FAIL — the process group survived'}")

    empty = discover(pathlib.Path(tempfile.mkdtemp()))
    good3 = empty == []
    ok &= good3
    print(f"  g=0       an empty directory discovers nothing (-> main would EXIT 2): {good3}")
    print(f"  CLASSIFIER on the two REAL messages that motivated it, plus a live one and silence:")
    ok &= _classifier_selftest()
    print(f"\n  {'PASS' if ok else '⛔ FAIL'} — the runner can detect a failing gate.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
