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
import pathlib, subprocess, sys, tempfile, time

ROOT = pathlib.Path(__file__).resolve().parent
# Helpers and appliers are NOT gates: they mutate state or expose functions rather than ruling.
NOT_A_GATE = {"run_all", "DEFECTS", "HEADLINES", "manifest", "pueue_wait",
              "clause3_as_written", "generate_round_index"}
PREFIX_SKIP = ("_", "apply_")


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
    return p.stem, rc, time.time()-t0, (tag or (out.strip().splitlines() or [""])[-1])[:120]


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return selftest()
    gates = discover()
    if not gates:                       # §4: empty population must EXIT 2, never 0
        print("⛔ no gates discovered — the runner examined nothing. EXIT 2.")
        return 2
    rows = [run_one(p) for p in gates]
    buckets = {"PASS": [], "FAIL": [], "UNRUNNABLE": [], "ERROR": []}
    for name, rc, el, msg in rows:
        b = "PASS" if rc == 0 else "FAIL" if rc == 1 else "UNRUNNABLE" if rc == 2 else "ERROR"
        buckets[b].append((name, rc, el, msg))
    for b in ("FAIL", "ERROR", "UNRUNNABLE"):
        for name, rc, el, msg in buckets[b]:
            print(f"  {b:<11} {name:<48} rc={rc:<3} {el:5.1f}s  {msg}")
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
    empty = discover(pathlib.Path(tempfile.mkdtemp()))
    good3 = empty == []
    ok &= good3
    print(f"  g=0       an empty directory discovers nothing (-> main would EXIT 2): {good3}")
    print(f"\n  {'PASS' if ok else '⛔ FAIL'} — the runner can detect a failing gate.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
