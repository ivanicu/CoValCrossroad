"""R397 -- did R394's 13 "STABLE" subjects actually SUCCEED, or did some crash identically twice?

While writing R396 I had to name the failure it must not commit: a crash is byte-identical twice, so
a round that cannot run emits the same traceback on both draws, the number multisets match, and the
comparison prints STABLE. Writing that sentence down made it obvious that R394 -- committed one hour
earlier -- HAS THAT DEFECT. It captures `p.stdout + p.stderr` and never reads `p.returncode`.

⛔ AND R393 IS WORSE, IN THE SAME DIRECTION. Its timing loop discards the CompletedProcess entirely,
   so `COMPLETE` means "finished inside 90s" and NOT "succeeded". A round crashing in 0.4s was
   recorded COMPLETE and became one of R394's subjects.

⛔ AND THE CONTAMINATION PROPAGATES TO R395, WHICH IS THE PART THAT MAKES THIS URGENT. R395 scored its
   source detector against "13 rounds R394 measured as STABLE", calling every hit among them a FALSE
   POSITIVE BY CONSTRUCTION. If some of those 13 never executed, they are not labelled negatives at
   all, the 23% false-positive rate is measured against a corrupted answer key, and the
   W-GAUGE-DECISIVE verdict that halved the expensive step rests on it.

⚠ THERE IS A SPECIFIC REASON TO EXPECT FAILURES RATHER THAN A GENERIC WORRY. R393 reset the worktree
  between subjects with a hard checkout AND a recursive untracked-file purge. R390 established that
  the release data under `data/` is UNTRACKED and had to be linked in by hand. So R393's own hygiene
  step plausibly removed the inputs its later subjects needed. That is a mechanism, named before the
  run, and it predicts failures concentrated in data-reading rounds.

⛔ ARITHMETIC TRAP. Could this come out otherwise? YES, in both directions and I do not know which.
   Every subject may have exited 0, in which case R394 and R395 survive intact and a hole is closed
   at the cost of 46 seconds. Or some crashed, and two committed findings need correcting. Nothing
   about the design forces either.

ESTIMAND        for each of R394's 13 STABLE subjects: its process return code, and whether its
                output contains a Python traceback. Reported per round, named, never as a pass rate
                alone.

IDENTIFICATION  Exact -- a return code is observed, not inferred. NOT identified: a round that exits
                0 while silently producing nothing meaningful. The traceback check is a second,
                partial signal for exactly that gap and is reported separately rather than merged.

SCOPE           population: R394's 13 STABLE subjects · instrument: process return code + traceback
                search · baseline: two planted scripts with known exit codes · regime: R394's OWN
                worktree, unreset, because the claim under test is about R394's measurement and a
                different regime would test a different thing.

WORLDS
  W-LABELS-SOUND  every subject exits 0. R394's STABLE labels mean what they said, R395's answer key
                  is intact, and both verdicts stand. The defect is real but was not load-bearing.
  W-LABELS-DIRTY  >= 1 subject exits non-zero. Then R394 certified a crash as stability, R395's
                  false-positive rate is measured against a corrupted key, and both must be corrected
                  in place -- with the corrected numbers carried, not merely a note added.

PREDICTION MATRIX
  W-LABELS-SOUND -> 13 of 13 exit 0, 0 tracebacks
  W-LABELS-DIRTY -> >= 1 non-zero exit or traceback, subjects named

PRE-REGISTERED KILL -- conditional on the controls, never on the counts alone.
    if fail_plant_detected and pass_plant_clean:
        if all 13 exit 0 and no traceback -> W-LABELS-SOUND
        else                              -> W-LABELS-DIRTY, subjects named, corrections owed
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  PLANT (+)   a script that exits non-zero must be classified FAILED. Without it, "13 of 13 exited 0"
              is silence from an instrument never shown to detect a failure.
  PLANT (-)   a script that exits cleanly must be classified OK, so the detector is not a constant
              that condemns everything.
  REGIME      R394's own worktree, NOT reset first -- testing a claim about R394 requires R394's
              conditions. Resetting would silently answer a different question.
  EMPTY       fewer than 10 subjects -> exit 2, never 0.

MULTIPLICITY    13 subjects x 2 signals (exit code, traceback). Every result printed.
SEEDS           none -- an exit code is not a draw.
ARTIFACT        results/r397_subject_exit_codes.json with the source hash.

IMPOSSIBLE HERE
  a round that exits 0 while doing nothing -- partially covered by the traceback signal, not fully.
  re-deciding R394's STABLE comparison     -- this round measures whether its subjects RAN, not
                                              whether their numbers matched. Separate questions.
  a second release                         -- one release.

EXIT
    0  controls hold and the subjects are classified
    1  a control misbehaved -- UNVERIFIED
    2  the population is unusable -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
PY = ROOT / ".venv" / "bin" / "python"
WT = pathlib.Path("/tmp/claude-1000/-home-ivan/7d277876-c2fd-4a27-9b05-652b391121ff/scratchpad/r390_wt")
R394 = HERE.parent / "R394_is_the_source_hash_a_valid_key" / "results" / "r394_source_hash_key.json"
TIMEOUT = 300


def main() -> int:
    if not R394.exists():
        print("  UNRUNNABLE: R394's artifact absent. Exit 2, never 0."); return 2
    if not WT.exists():
        print("  UNRUNNABLE: R394's worktree absent. Exit 2, never 0."); return 2
    a394 = json.loads(R394.read_text())
    subjects = sorted(k for k, v in a394["rows"].items() if v["status"] == "STABLE")
    if len(subjects) < 10:
        print(f"  UNRUNNABLE: {len(subjects)} subjects. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R397 · did R394's STABLE subjects actually succeed?   HEAD {head}\n")
    print("  ⛔ R394 READS `p.stdout + p.stderr` AND NEVER `p.returncode`. A crash is byte-identical")
    print("     twice, so a round that cannot run emits the same traceback on both draws and the")
    print("     comparison prints STABLE. R393 is worse in the same direction: it discards the")
    print("     CompletedProcess entirely, so COMPLETE means `finished inside 90s`, not `succeeded`.")
    print("  ⛔ AND R395 SCORED ITS DETECTOR AGAINST THESE 13 AS LABELLED NEGATIVES. If any never")
    print("     executed, the 23% false-positive rate is measured against a corrupted answer key.\n")

    def classify(path, cwd, timeout=TIMEOUT):
        try:
            p = subprocess.run([str(PY), str(path)], cwd=str(cwd), capture_output=True,
                               text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return dict(status="TIMEOUT", rc=None, traceback=None, last="")
        tb = "Traceback (most recent call last)" in (p.stdout + p.stderr)
        return dict(status=("OK" if (p.returncode == 0 and not tb) else "FAILED"),
                    rc=p.returncode, traceback=tb,
                    last=(p.stderr.strip().splitlines()[-1][:110] if p.stderr.strip() else ""))

    # ---- CONTROLS, both directions --------------------------------------------------------------
    plants = HERE / "results" / "_plants"
    plants.mkdir(parents=True, exist_ok=True)
    (plants / "boom.py").write_text("raise SystemExit(3)\n")
    (plants / "fine.py").write_text("print('ok 1.0')\n")
    boom = classify(plants / "boom.py", plants, 60)
    fine = classify(plants / "fine.py", plants, 60)
    pos_ok = boom["status"] == "FAILED"
    neg_ok = fine["status"] == "OK"
    print("  CONTROLS on the exit-code detector")
    print(f"    PLANT (+)  a script exiting 3 is classified {boom['status']}   "
          f"{'PASS' if pos_ok else 'FAIL — every OK below would be silence'}")
    print(f"    PLANT (-)  a clean script is classified {fine['status']}   "
          f"{'PASS' if neg_ok else 'FAIL — the detector condemns everything'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the detector is blind in one direction. Exit 1."); return 1

    # ---- the subjects, in R394's OWN regime -----------------------------------------------------
    print(f"\n  {len(subjects)} SUBJECTS R394 CALLED STABLE — run in R394's own worktree, UNRESET,")
    print("  because a claim about R394's measurement needs R394's conditions")
    rows, failed = {}, []
    for name in subjects:
        d = next((q for q in WT.glob(f"E0*/A*/{name}") if q.is_dir()), None)
        if d is None or not (d / "run.py").exists():
            rows[name] = dict(status="ABSENT"); failed.append(name)
            print(f"    {name:<44} ABSENT"); continue
        r = classify(d / "run.py", d)
        rows[name] = r
        if r["status"] != "OK":
            failed.append(name)
        print(f"    {name:<44} {r['status']:<8} rc={r['rc']}"
              + ("  TRACEBACK" if r.get("traceback") else "")
              + (f"  {r.get('last','')}" if r["status"] != "OK" else ""))

    print(f"\n    OK {len(subjects)-len(failed)} of {len(subjects)} · NOT-OK {len(failed)}")

    # ---- VERDICT --------------------------------------------------------------------------------
    print()
    if not failed:
        v = "W_LABELS_SOUND"
        print(f"  W-LABELS-SOUND — {len(subjects)} of {len(subjects)} exited 0 with no traceback.")
        print("  R394's STABLE labels mean what they said and R395's answer key is intact, so both")
        print("  verdicts stand. The defect in R394 and R393 is REAL and was NOT load-bearing here —")
        print("  which is a fact about this population, not a property of the code. The gate that")
        print("  prevents it is R396's exit-code class, already committed, and it applies from now on")
        print("  rather than retroactively excusing the two rounds that lacked it.")
    else:
        v = "W_LABELS_DIRTY"
        print(f"  W-LABELS-DIRTY — {len(failed)} of {len(subjects)} did not succeed: {failed}.")
        print("  R394 certified a crash as stability. R395's 23% false-positive rate is measured")
        print("  against a corrupted answer key and its W-GAUGE-DECISIVE verdict -- the one that")
        print("  halved the expensive step -- rests on it. Both need CORRECTING IN PLACE with the")
        print("  recomputed numbers carried, not a note appended.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, n_subjects=len(subjects), rows=rows, failed=failed,
               controls=dict(boom=boom, fine=fine, pos_ok=pos_ok, neg_ok=neg_ok), verdict=v)
    outp = HERE / "results" / "r397_subject_exit_codes.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
