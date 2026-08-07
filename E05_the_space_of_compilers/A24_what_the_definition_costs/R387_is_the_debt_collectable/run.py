"""R387 — is the missing-findings debt collectable? Can the rounds still be re-run?

R386 established that a finding's numbers are 9% in the artifact that produced it, so the 243 rounds
with no finding site cannot be drafted by generation. Its NEXT asked whether a finding is still
RECOVERABLE from what was persisted -- if not, the debt is not merely unpaid but uncollectable.

⛔ "IS A FINDING RECOVERABLE" IS MY JUDGEMENT, AND THAT MAKES IT VOID. I would be the one deciding
   whether a JSON blob still supports a sentence, which is the self-review this project treats as
   void rather than weak -- the same trap R385's NEXT walked into and R386 refused. So it is
   replaced by a question the machine answers:

       CAN THE ROUND STILL BE RE-RUN?

   That is the strongest form of recoverability there is. If `run.py` executes, its output can be
   read and the finding written from it. If it does not, one would be reconstructing from a JSON
   alone, which R386 measured at 9% of the numbers. The estimand is an exit code, not an opinion.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES, wide open. These
   rounds were written months apart against a tree that has since been restructured (R380 found one
   glob matching 0 of 363 files), so wholesale failure is entirely plausible -- and so is wholesale
   success, since they were working when they were written and the data has not moved. Nothing in
   the design forces either.
   ⚠ And one thing IS forced and is therefore excluded from the verdict: a round needing GPU or
   minutes of compute will TIME OUT inside any budget I set. A timeout is NOT a failure -- the code
   got far enough to run -- so it is recorded as its own outcome and never folded into either side.

ESTIMAND        over the oldest rounds that have an artifact, a `run.py`, and NO finding site:
                the exit status of executing `run.py` in an isolated worktree, in three classes --
                RAN (exit 0), FAILED (non-zero, with the exception class), TIMEOUT (unverified).

IDENTIFICATION  Exact per round for RAN and FAILED. TIMEOUT is genuinely unverified and is counted
                separately rather than assigned. NOT identified: whether a round that runs produces
                a READABLE finding -- executability is necessary, not sufficient, and the sufficiency
                question is the one I am not allowed to answer alone.

SCOPE           population: the 12 lowest-numbered such rounds · instrument: the repaired
                `_isolated` harness (R376), which restores the tree from git after every subject ·
                baseline: two known answers · regime: HEAD.

WORLDS
  W-COLLECTABLE     most re-run. The debt is real work but payable: re-run, read, write. The 243 is
                    a backlog with a known unit cost.
  W-UNCOLLECTABLE   most fail. The findings cannot be recovered without first repairing each
                    round's code, so the honest act is to RECORD the debt as uncollectable rather
                    than write 238 paragraphs reconstructing nothing.
  W-UNRESOLVED      most time out. Then this budget cannot answer the question and a larger one
                    must, which is a statement about my design rather than about the corpus.

PREDICTION MATRIX
  W-COLLECTABLE   -> RAN >= 60% of the non-timeout subjects
  W-UNCOLLECTABLE -> FAILED >= 60% of them
  W-UNRESOLVED    -> TIMEOUT > 50% of all subjects

PRE-REGISTERED KILL -- conditional on the controls, never on the counts alone.
    if harness_positive_control_ran and harness_negative_control_failed:
        if timeouts > half of all subjects        -> W-UNRESOLVED
        elif ran >= 0.60 * (ran + failed)          -> W-COLLECTABLE
        elif failed >= 0.60 * (ran + failed)       -> W-UNCOLLECTABLE
        else                                       -> named explicitly, not defaulted
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  HARNESS (+)  a round known to execute -- one written THIS SESSION, whose run is in the log -- must
               come back RAN. If the harness cannot run a working round, every FAILED below is the
               harness's and not the corpus's.
  HARNESS (-)  a deliberately broken script (`import a_module_that_does_not_exist`) must come back
               FAILED. Both directions, because a harness reporting RAN for everything would pass
               the positive control and mean nothing.
  ISOLATION    every subject runs in a git worktree restored between subjects. These scripts WRITE
               to their own `results/`, so running them in the live tree would rewrite committed
               artifacts -- the measurement would damage the thing it measures.
  TIMEOUT      recorded as its own class. A slow round is not a dead one, and folding the two would
               manufacture the uncollectable verdict.

MULTIPLICITY    a census over a fixed prefix of the population. Every subject and its outcome
                printed, survivors and not.
SEEDS           none -- execution is the measurement.
ARTIFACT        results/r387_rerunnable.json with the source hash.

IMPOSSIBLE HERE
  whether a runnable round yields a READABLE finding  -- executability is necessary, not sufficient,
                                                         and sufficiency is a judgement I may not
                                                         make alone.
  the other 217 rounds  -- this is the oldest 12, chosen because age is the strongest reason to
                           expect rot. If they run, younger ones plausibly do too; if they fail,
                           that is a lower bound on the damage, not a total.
  a second release      -- one release.

EXIT
    0  controls hold and the debt is classified
    1  a control misbehaved -- UNVERIFIED
    2  fewer than 8 subjects available -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
N_SUBJECTS = 12
TIMEOUT_S = 90
POS = "R384_where_the_findings_are_not"      # written and executed this session
sys.path.insert(0, str(ROOT / "assurance"))
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def rnum(name):
    m = re.match(r"R(\d+)_", name)
    return int(m.group(1)) if m else 10 ** 9


def main() -> int:
    try:
        from _isolated import ensure_worktree, restore, run_isolated   # noqa: E402
    except Exception as e:
        print(f"  UNRUNNABLE: cannot import the repaired harness ({e}). Exit 2, never 0."); return 2

    root_txt = (ROOT / "README.md").read_text()
    cand = []
    for d in sorted(ROOT.glob("E0*/A*/R*")):
        if not d.is_dir() or d == HERE:
            continue
        if (d / "README.md").exists() or d.name in root_txt:
            continue
        if not (d / "results").is_dir() or not (d / "run.py").exists():
            continue
        cand.append(d)
    cand.sort(key=lambda d: rnum(d.name))
    subjects = cand[:N_SUBJECTS]
    if len(subjects) < 8:
        print(f"  UNRUNNABLE: only {len(subjects)} subjects. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R387 · is the debt collectable?   HEAD {head}\n")
    print(f"  ⛔ R386's NEXT asked whether a finding is still RECOVERABLE. I would be the one")
    print(f"     judging that, which is self-review and therefore void. Replaced by a question")
    print(f"     the machine answers: CAN THE ROUND STILL BE RE-RUN?\n")
    print(f"  {len(cand)} rounds have an artifact, a run.py and NO finding site.")
    print(f"  Subjects: the {len(subjects)} lowest-numbered — age is the strongest reason to expect")
    print(f"  rot, so this is a lower bound on the damage rather than a sample of it.")
    print(f"  Timeout {TIMEOUT_S}s per subject, and a TIMEOUT is recorded as its own class.")

    wt = ensure_worktree()
    # ⛔ THE WORKTREE WAS AT AN OLD COMMIT AND BOTH CONTROLS RETURNED `MISSING`. It was left where
    #   R375 finished, so every round committed since simply did not exist in it -- and `MISSING`
    #   is not `FAILED`, which is why the harness controls caught it instead of silently scoring
    #   twelve subjects as broken. Checked out to the live HEAD explicitly.
    subprocess.run(["git", "checkout", "-f", "-q", head], cwd=str(wt), capture_output=True)
    subprocess.run(["git", "clean", "-fdq"], cwd=str(wt), capture_output=True)
    restore(wt)

    def execute(rel: str, restore_first: bool = True):
        """THE classifier. Both controls and every subject go through THIS path.

        ⛔ v1 of the negative control re-implemented the classification inline and DISAGREED with
          it: a broken import came back `EXC ModuleNotFoundError`, which this function maps to
          FAILED and my duplicate mapped to itself. A control that re-implements the check it
          validates tests the copy, not the check -- and it is why the negative control read FAIL
          while the harness was working correctly.
        """
        try:
            rc, _files, _d = run_isolated(rel, timeout=TIMEOUT_S, restore_first=restore_first)
        except Exception as e:
            return "ERROR", type(e).__name__
        if rc == "TIMEOUT":
            return "TIMEOUT", ""
        if rc == "MISSING":
            return "MISSING", ""
        if rc == "NO-TRACE":
            return "NO-TRACE", ""
        return ("RAN" if rc == 0 else "FAILED"), str(rc)

    # ---- CONTROLS ------------------------------------------------------------------------------
    pos_dir = next((p for p in ROOT.glob(f"E0*/A*/{POS}") if p.is_dir()), None)
    pos_cls = execute(str((pos_dir / "run.py").relative_to(ROOT)))[0] if pos_dir else "ABSENT"
    # ⛔ AND THE NEGATIVE PROBE WAS ERASED BEFORE IT COULD RUN, which `_isolated`'s OWN DOCSTRING
    #   warns about in as many words: "restore_first=False EXISTS BECAUSE THE SELFTEST SILENTLY DID
    #   NOTHING ... the saboteur probe, which is untracked by construction, was erased before it
    #   could execute." I quoted a confession from a different gate one round ago and then walked
    #   into this one. The probe is untracked, so it must be run with restore_first=False.
    probe = "assurance/_r387_broken.py"
    (wt / probe).write_text("import a_module_that_does_not_exist\n")
    neg_cls, neg_detail = execute(probe, restore_first=False)
    (wt / probe).unlink(missing_ok=True)
    pos_ok = (pos_cls == "RAN")
    neg_ok = (neg_cls == "FAILED")
    print(f"\n  CONTROLS on the harness, before any subject")
    print(f"    HARNESS (+)  `{POS}` — written and executed THIS session — returns {pos_cls}  "
          f"{'PASS' if pos_ok else 'FAIL — every FAILED below would be the harness'}")
    print(f"    HARNESS (-)  a deliberately broken import returns {neg_cls} ({neg_detail})  "
          f"{'PASS' if neg_ok else 'FAIL — it cannot report failure'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the harness is blind in one direction. Exit 1."); return 1

    # ---- the subjects ---------------------------------------------------------------------------
    print(f"\n  RE-RUNNING THE OLDEST {len(subjects)}, each in a worktree restored from git")
    print(f"    {'round':<38}{'outcome':>10}{'exit':>7}")
    rows = {}
    for d in subjects:
        rel = str((d / "run.py").relative_to(ROOT))
        cls, detail = execute(rel)
        rows[d.name] = dict(outcome=cls, detail=detail, path=rel)
        print(f"    {d.name:<38}{cls:>10}{detail:>7}", flush=True)
    restore(wt)

    ran = [k for k, v in rows.items() if v["outcome"] == "RAN"]
    failed = [k for k, v in rows.items() if v["outcome"] == "FAILED"]
    timeout = [k for k, v in rows.items() if v["outcome"] == "TIMEOUT"]
    other = [k for k, v in rows.items() if v["outcome"] not in ("RAN", "FAILED", "TIMEOUT")]
    decided = len(ran) + len(failed)
    print(f"\n    RAN {len(ran)} · FAILED {len(failed)} · TIMEOUT {len(timeout)} · "
          f"other {len(other)}   (decided: {decided} of {len(subjects)})")

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if len(timeout) > len(subjects) / 2:
        print(f"  W-UNRESOLVED — {len(timeout)} of {len(subjects)} subjects exceeded the {TIMEOUT_S}s")
        print(f"  budget. This design cannot answer the question and a larger budget must. That is")
        print(f"  a statement about MY design, not about the corpus, and it is not evidence either")
        print(f"  way about whether the debt is collectable.")
        v = "W_UNRESOLVED"
    elif decided == 0:
        print(f"  UNVERIFIED — no subject returned a decidable outcome.")
        v = "UNVERIFIED"
    elif len(ran) >= 0.60 * decided:
        print(f"  W-COLLECTABLE — {len(ran)} of {decided} decided subjects re-run cleanly. The debt")
        print(f"  is real work but PAYABLE: re-run, read the output, write the finding. The 243 is")
        print(f"  a backlog with a known unit cost rather than a loss.")
        v = "W_COLLECTABLE"
    elif len(failed) >= 0.60 * decided:
        print(f"  W-UNCOLLECTABLE — {len(failed)} of {decided} decided subjects FAIL to execute.")
        print(f"  The findings cannot be recovered without repairing each round's code first, and")
        print(f"  R386 measured that the artifact alone carries 9% of the numbers. ⛔ So the honest")
        print(f"  act is to RECORD the debt as uncollectable rather than write paragraphs that")
        print(f"  reconstruct nothing.")
        v = "W_UNCOLLECTABLE"
    else:
        print(f"  W-SPLIT — {len(ran)} ran and {len(failed)} failed of {decided} decided, with")
        print(f"  neither side at 60%. Named rather than defaulted: the debt is PARTLY collectable,")
        print(f"  and the split itself is the estimate of how much.")
        v = "W_SPLIT"

    if failed:
        print(f"\n  the failures, named rather than counted:")
        for k in failed:
            print(f"    {k}  exit {rows[k]['detail']}")

    print(f"\n  ⚠ EXECUTABILITY IS NECESSARY, NOT SUFFICIENT. A round that runs can be read; whether")
    print(f"    its output supports a FINDING is a judgement, and that is the one I may not make")
    print(f"    alone. This measured that the door opens, never what is behind it.")
    print(f"  ⚠ AND THESE ARE THE {len(subjects)} OLDEST of {len(cand)}. Age is the strongest reason")
    print(f"    to expect rot, so a failure rate here is a LOWER bound on health and an UPPER bound")
    print(f"    on damage — not an estimate of the whole.")

    out = dict(stamp(str(SELF)), head=head, n_candidates=len(cand), n_subjects=len(subjects),
               timeout_s=TIMEOUT_S, rows=rows, ran=ran, failed=failed, timeout=timeout,
               other=other, controls=dict(harness_pos=pos_cls, harness_neg=neg_cls,
                                          pos_ok=pos_ok, neg_ok=neg_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r387_rerunnable.json"
    outp.write_text(json.dumps(out, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
