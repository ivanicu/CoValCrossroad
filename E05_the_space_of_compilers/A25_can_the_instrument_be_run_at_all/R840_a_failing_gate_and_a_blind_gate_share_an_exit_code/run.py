#!/usr/bin/env python3
"""
R840 · a FAILING gate and a BLIND gate share an exit code.

ESTIMAND        among gates exiting non-zero, the count DARK (own controls did not validate,
                so the output is silence about the repo) vs FAILING (controls passed, defect real)
IDENTIFICATION  yes -- every gate prints its control lines. NOT recoverable from exit status,
                which is the finding: exit 1 is emitted by both classes.
SCOPE           population: the push sweep's gates that exited non-zero (14)
                instrument: the stdout classifier below, pre-registered in README.md
                baseline:   the census, which treats all 14 as one class
                regime:     this repo at this commit
WORLDS          A accident (~1 dark) · B population (several) · C classifier blind -> UNVERIFIED
KILL            conditional: positive control BOTH arms + the g=0 arm must be correct,
                or the counts are not reported at all
POSITIVE CTRL   the SAME gate at two PINNED commits -- fd99c0f0 known DARK (control 0/2),
                098784e9 known FAILING (control 2/2). They differ ONLY in the defect.
                Pinned by HASH, never by HEAD~n: an anchor must be an identity, not a position.
G=0             a gate that exits 0 must classify GREEN, not DARK and not FAILING.
                Without this a classifier that answers DARK to everything would pass.
NOISE FLOOR     n/a -- the quantity is a classification, not an estimate
MULTIPLICITY    14 gates, one classification each, no selection among them: the whole
                population is reported including every UNCLASSIFIED
ARTIFACT        results/classification.json, with the git hash and each gate's evidence line
IMPOSSIBLE      independently replicated · construct validated · cross-dataset · causally
                identified -- see README.md, each with what it would require
"""
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(exist_ok=True)
PY = str(ROOT / ".venv" / "bin" / "python")

# A control line is one that reports on the INSTRUMENT, not on the repo. This suite writes them
# with a leading marker word; the verdict token is the last PASS/FAIL on the line.
CTRL = re.compile(r"^\s*(POSITIVE CONTROL|NEGATIVE CONTROL|CONTROL|g=0|SHAM|PLACEBO)\b(.*)$",
                  re.M | re.I)
BAD = re.compile(r"\b(FAIL|UNRUNNABLE|BLIND|misbehaved)\b", re.I)
GOOD = re.compile(r"\bPASS\b")


def classify(exit_code: int, out: str):
    """Pre-registered in README.md before any gate was read. Three-valued."""
    if exit_code == 0:
        return "GREEN", "exit 0"
    if exit_code == 124:
        return "DARK", "exit 124 — timed out, no verdict was produced"
    if exit_code == 2:
        return "DARK", "exit 2 — this suite's declared code for unrunnable / empty population"
    ctrls = [(m.group(1), m.group(2)) for m in CTRL.finditer(out)]
    bad = [f"{a}{b}".strip()[:110] for a, b in ctrls if BAD.search(b) and not GOOD.search(b)]
    if bad:
        return "DARK", f"control line reports failure: {bad[0]}"
    if exit_code == 1 and ctrls:
        return "FAILING", f"{len(ctrls)} control line(s), all PASS"
    return "UNCLASSIFIED", f"exit {exit_code}, {len(ctrls)} control line(s) found"


def run_gate(path: str, timeout=200):
    p = subprocess.run([PY, path], capture_output=True, text=True,
                       cwd=str(ROOT), timeout=timeout + 60)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


# ⛔ PINNED, AND THE REASON IS THIS ROUND'S OWN SUBJECT. The first version of this control read
# `HEAD~1` -- A SLIDING REFERENCE TO A FIXED OBJECT, which is EXACTLY the defect entries 1353 and
# 1354 were measuring, built for the third time inside the round investigating the first two, within
# the same hour. It worked at launch and was already wrong twenty minutes later: the next commit made
# `HEAD~1` the REPAIRED file, so the "known DARK" arm would silently stop being dark and the control
# would fail for its own reasons. Both arms are now pinned by hash, so the control means the same
# thing on any future run -- which is what REPRODUCIBILITY in the docstring above actually requires.
# The general rule this round earned three times over: A CONTROL'S ANCHOR MUST BE AN IDENTITY,
# NEVER A POSITION. `HEAD~1`, `-n 60`, "the last release" and "recent commits" are all positions.
PC_DARK = "fd99c0f0"   # pre-repair: positive control caught 0/2
PC_FAIL = "098784e9"   # post-repair (entry 1353): positive control caught 2/2


def positive_control():
    """The same gate at two PINNED commits: fd99c0f0 DARK, 098784e9 FAILING.
    They differ only in the defect, so a classifier separating them separates the defect."""
    g = "assurance/next_gradient_labels_its_hypotheses.py"
    tmp = OUT / "_pc_prior.py"
    prior = subprocess.run(["git", "-C", str(ROOT), "show", f"{PC_DARK}:{g}"],
                           capture_output=True, text=True)
    if prior.returncode != 0:
        return False, "cannot fetch the pinned pre-repair version — control UNRUNNABLE, not passed"
    tmp.write_text(prior.stdout)
    rc_a, out_a = run_gate(str(tmp))
    cls_a, ev_a = classify(rc_a, out_a)
    tmp_b = OUT / "_pc_post.py"
    post = subprocess.run(["git", "-C", str(ROOT), "show", f"{PC_FAIL}:{g}"],
                          capture_output=True, text=True)
    if post.returncode != 0:
        return False, "cannot fetch the pinned post-repair version — control UNRUNNABLE"
    tmp_b.write_text(post.stdout)
    rc_b, out_b = run_gate(str(tmp_b))
    cls_b, ev_b = classify(rc_b, out_b)
    tmp.unlink(missing_ok=True); tmp_b.unlink(missing_ok=True)

    # g=0 arm: a gate known to exit 0 must NOT be called DARK or FAILING.
    rc_c, out_c = run_gate(str(ROOT / "assurance" / "definition_matches_the_record.py"))
    cls_c, ev_c = classify(rc_c, out_c)

    ok = (cls_a == "DARK") and (cls_b == "FAILING") and (cls_c == "GREEN")
    print(f"  POSITIVE CONTROL  known-DARK  {PC_DARK} -> {cls_a:<12} "
          f"{'PASS' if cls_a=='DARK' else 'FAIL'}   [{ev_a}]")
    print(f"                    known-FAIL  {PC_FAIL} -> {cls_b:<12} "
          f"{'PASS' if cls_b=='FAILING' else 'FAIL'}   [{ev_b}]")
    print(f"  g=0               known-GREEN          -> {cls_c:<12} "
          f"{'PASS' if cls_c=='GREEN' else 'FAIL'}   [{ev_c}]")
    print("    The two arms are the SAME FILE at two PINNED hashes, differing only in the defect,")
    print("    so a classifier that separates them is separating the defect and not the subject.")
    return ok, {"dark_arm": cls_a, "failing_arm": cls_b, "green_arm": cls_c}


def main() -> int:
    targets = sys.argv[1:]
    if not targets:
        print("  usage: run.py <gate.py> [...] — the sweep's non-zero gates")
        return 2

    ok, pc = positive_control()
    if not ok:
        print("\n  UNVERIFIED: the classifier cannot separate the one case already adjudicated.")
        print("  No counts are reported. A classifier that fails its own control is not entitled")
        print("  to an opinion about the gates nobody has read yet. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "positive_control": pc},
                  open(OUT / "classification.json", "w"), indent=2)
        return 2

    print(f"\n  {'gate':<46}{'exit':>5}  {'class':<13} evidence")
    rows = []
    for t in targets:
        path = ROOT / "assurance" / t
        try:
            rc, out = run_gate(str(path))
        except subprocess.TimeoutExpired:
            rc, out = 124, ""
        cls, ev = classify(rc, out)
        rows.append({"gate": t, "exit": rc, "class": cls, "evidence": ev})
        print(f"  {t:<46}{rc:>5}  {cls:<13} {ev[:64]}")

    n = {k: sum(r["class"] == k for r in rows) for k in
         ("DARK", "FAILING", "GREEN", "UNCLASSIFIED")}
    print(f"\n  ⭐ of {len(rows)} non-zero gates: {n['DARK']} DARK · {n['FAILING']} FAILING · "
          f"{n['UNCLASSIFIED']} UNCLASSIFIED · {n['GREEN']} now GREEN")
    print("     DARK means the gate's output is SILENCE ABOUT THE REPO, not a defect in it.")
    print("     Every UNCLASSIFIED is printed above and folded into neither class.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"verdict": "REPORTED", "commit": head, "positive_control": pc,
               "counts": n, "rows": rows},
              open(OUT / "classification.json", "w"), indent=2)
    print(f"\n  artifact: results/classification.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
