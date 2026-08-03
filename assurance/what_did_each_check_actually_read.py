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
import hashlib, json, pathlib, subprocess, sys, tempfile, textwrap

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
    except BaseException:
        rc = 99
    finally:
        OUT.write_text(json.dumps({{"rc": rc, "files": sorted(seen)}}))
''')


def run_traced(target: pathlib.Path):
    with tempfile.TemporaryDirectory() as td:
        out = pathlib.Path(td) / "trace.json"
        shim = pathlib.Path(td) / "shim.py"
        shim.write_text(SHIM.format(root=str(ROOT), out=str(out), tgt=str(target)))
        try:
            subprocess.run([PY, str(shim)], cwd=str(ROOT), capture_output=True, timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            return None, []
        if not out.exists():
            return None, []
        d = json.loads(out.read_text())
        return d["rc"], d["files"]


def main():
    scripts = sorted(p for p in HERE.glob("*.py")
                     if p.resolve() != SELF and not p.name.startswith("_"))
    pos = HERE / "_poscontrol_unrepaired.py"
    src = (HERE / "DEFECTS.py").read_text()
    pos.write_text(src.replace("p = round_results(rnd, fn)\n        if p is None:\n            continue",
                               'p = HERE / rnd / "results" / fn')
                      .replace("if not items:", "if False and not items:"))
    scripts.append(pos)

    print(f"  {len(scripts)} scripts (incl. 1 planted positive control)\n")
    print(f"  {'check':<46}{'exit':>5}{'round files':>13}{'other repo':>12}   verdict")
    rows, empty, docs_only = {}, [], []
    snap = {p: p.read_bytes() for p in HERE.rglob("*") if p.is_file() and "__pycache__" not in str(p)}
    interference = []
    for s in scripts:
        # ⚠ TREE INTEGRITY BETWEEN SUBJECTS — the defect that invalidated this round's first run.
        # `attack_the_suite.py` and `attack_every_check.py` MOVE EPOCH DIRECTORIES by design
        # ("each is moved separately and restored separately"). The first version of this harness
        # snapshotted only `assurance/`, so a subject that left the round tree mutilated changed
        # the environment of every subject after it -- and `consistency.py`, which sorts after
        # `attack_*`, was measured at 0 round files when tracing it ALONE gives 8. An uncontrolled
        # sweep in which one subject mutates the next one's world is not measuring the subjects.
        # The object contradicted the instrument and the object won.
        dirty = subprocess.run(["git", "status", "--porcelain", "--"] +
                               EPOCHS,
                               cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if dirty:
            interference.append(f"{s.name}: tree dirty BEFORE this subject ran")
            subprocess.run(["git", "checkout", "--"] + EPOCHS,
                           cwd=ROOT, capture_output=True)
        rc, files = run_traced(s)
        after = subprocess.run(["git", "status", "--porcelain", "--"] +
                               EPOCHS,
                               cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if after:
            interference.append(f"{s.name}: LEFT the round tree dirty")
            subprocess.run(["git", "checkout", "--"] + EPOCHS,
                           cwd=ROOT, capture_output=True)
        # restore anything the run wrote -- these scripts regenerate artifacts, and running an
        # auditor must never be how an artifact changes. This is the same protection the last
        # sweep needed, for the same reason.
        for p in list(HERE.rglob("*")):
            if p.is_file() and "__pycache__" not in str(p) and p not in snap:
                p.unlink()
        for p, b in snap.items():
            if not p.exists() or p.read_bytes() != b:
                p.write_bytes(b)
        rf = [f for f in files if f.startswith("E0") and "/R" in f]
        of = [f for f in files if not f.startswith("E0") and not f.startswith("assurance/")
              and not f.startswith(".venv")]
        if rc == 0 and not rf and not of:
            v, _ = "⚠ READ NOTHING", empty.append(s.name)
        elif rc == 0 and not rf and of:
            v, _ = "docs-only (scoped)", docs_only.append(s.name)
        elif rc == 0:
            v = "read the tree"
        else:
            v = f"exit {rc}, not a pass"
        rows[s.name] = dict(exit=rc, round_files=len(rf), other_files=len(of), verdict=v,
                            sample=sorted(of)[:4])
        print(f"    {s.name[:44]:<46}{str(rc):>5}{len(rf):>13}{len(of):>12}   {v}")

    pos_ok = rows[pos.name]["round_files"] == 0 and rows[pos.name]["exit"] == 0
    neg_ok = rows["DEFECTS.py"]["round_files"] > 0
    pos.unlink(missing_ok=True)
    empty = [e for e in empty if e != pos.name]

    print(f"\n  POSITIVE CTRL  unrepaired DEFECTS.py exits 0 having read 0 round files: {pos_ok}")
    print(f"  FAILS AT g=0   the REPAIRED DEFECTS.py read "
          f"{rows['DEFECTS.py']['round_files']} round files: {neg_ok}")
    print("\n  " + "=" * 76)
    if not (pos_ok and neg_ok):
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. The instrument cannot separate the case it was built from.")
    elif empty:
        world = "SOME-PASS-ON-NOTHING"
        print(f"  -> {len(empty)} check(s) exit 0 having opened NO project file at all: {empty}")
        print("     A pass from a check that read nothing is silence, not an acquittal.")
    else:
        world = "EVERY-PASS-READ-SOMETHING"
        print(f"  -> every exit-0 check opened at least one project file. "
              f"{len(docs_only)} are scoped to top-level DOCUMENTS rather than rounds,")
        print(f"     which is a design choice and is listed, not counted as a defect: {docs_only}")
    print("  " + "=" * 76)

    o = HERE / "results" / "what_each_check_read.json"
    o.parent.mkdir(exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        read_nothing=empty, docs_only=docs_only, interference=interference,
        positive_control_ok=pos_ok, fails_at_g0=neg_ok, rows=rows), indent=1))
    print(f"\n  ⚠ tree-interference events between subjects: {len(interference)}")
    for x in interference[:6]: print(f"      {x}")
    print(f"  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
