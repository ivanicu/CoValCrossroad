"""R388 — pay ONE unit of the debt, and measure what it cost.

Eight rounds (R380-R387) established that the campaign's findings are missing for 243 of 377 rounds,
that generation cannot write them (9% of a finding's numbers are in its artifact), and that the code
still runs so the debt is payable. That is a complete answer to *can this be done* and no answer at
all to *is it worth doing*.

⛔ AND CONTINUING TO CHARACTERISE THE DEBT WOULD BE THE FAILURE THE CONSTITUTION NAMES. "If honesty
   were the objective function, shutting me off would be its maximum" -- zero output has zero false
   claims. Eight rounds of diagnosis with no paragraph written is an audit presented as a product.
   So this round WRITES ONE, and measures what it cost, because one measured unit turns 237 into an
   estimate someone can decide about.

WHAT WAS PRODUCED, and it exists whether or not this round's numbers are interesting: two rows in
the root README's `What was established` table, under a heading that marks them as BACKFILL rather
than blending them into rows written beside their rounds. R21_donor_distance's finding is now
stated where the campaign's own documents say findings live.

⛔ THE REAL RISK IS NOT COST, IT IS FABRICATION. A backfilled row is written months after the round,
   from output I read once. Nothing stops me writing a plausible number that the round never
   produced -- and a wrong number in a findings table is worse than an absent one, because an empty
   row is visibly empty. So the round's product is gated: EVERY NUMBER in the backfilled rows must
   appear in a FRESH RUN of R21 itself. Not in its artifact -- R386 measured that at 9% -- in its
   actual output.

⛔ ARITHMETIC TRAP, answered before the run. Is the verification forced to pass because I wrote the
   numbers by copying them? Partly YES, and that is exactly why the positive control below plants a
   number that is NOT in the output and requires the verifier to catch it. Without that plant, "all
   numbers verified" would be a restatement of "I copied carefully", which is not a check.
   The COST measurement is not forced: wall-clock could have been anything.

ESTIMAND        (a) wall-clock seconds to re-run R21 to completion, measured;
                (b) whether every numeric token in the backfilled README rows appears in that run's
                    output.
                (a) is n = 1 and is reported as ONE OBSERVATION, never as an estimate of 237.

IDENTIFICATION  (a) exact for this round; NOT identified for any other -- R387 found 3 of 12 rounds
                exceed 90s, so the distribution is wide and one draw does not summarise it.
                (b) exact.
                NOT identified: whether the WORDS of the finding are right. Numbers are checkable;
                the sentence around them is a judgement, and it is the one I may not make alone.

SCOPE           population: one round · instrument: wall-clock and numeric-token containment ·
                baseline: a planted false number · regime: HEAD.

WORLDS
  W-CHEAP        the machine time is small next to the writing. Then the debt's cost is dominated by
                 attention, and 237 units is a writing project rather than a compute one.
  W-EXPENSIVE    the machine time dominates. Then the debt is a compute backlog and can be
                 pipelined, which is a different plan.
  W-FABRICATED   a number in the row is not in the output. Then the row is withdrawn immediately and
                 the round has produced a retraction rather than a finding.

PREDICTION MATRIX
  W-CHEAP     -> run seconds well under a minute
  W-EXPENSIVE -> run seconds in the minutes
  W-FABRICATED-> any unverified number, at any cost

PRE-REGISTERED KILL -- conditional on the controls, never on the cost alone.
    if planted_false_number_is_caught and real_numbers_are_checked:
        if any real number is unverified -> W-FABRICATED, and the row comes OUT
        elif run_seconds < 60            -> W-CHEAP
        else                             -> W-EXPENSIVE
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  FABRICATION (+)  a number that is NOT in R21's output is injected into a copy of the rows, and the
                   verifier must flag it. Without this the verification is "I copied carefully".
  FABRICATION (-)  the real rows must pass. Both directions, because a verifier that flagged
                   everything would catch the plant and mean nothing.
  FRESH RUN        the numbers are checked against a run executed BY THIS ROUND, in an isolated
                   worktree, not against the committed artifact -- R386 measured the artifact
                   carries 9% of a finding's numbers.
  ISOLATION        R21 writes to its own results/; running it live would rewrite a committed
                   artifact, so it runs in a worktree restored from git.

MULTIPLICITY    one round, one cost, one verification over every number in the rows. All printed.
SEEDS           none -- R21 is deterministic given its inputs; the cost is wall-clock.
ARTIFACT        results/r388_unit_cost.json with the source hash.

IMPOSSIBLE HERE
  an estimate of the 237  -- n = 1, and R387 measured the spread is wide (3 of 12 over 90s). One
                             observation, labelled one.
  whether the WORDS are right -- numbers are checkable, the sentence is a judgement, and that is the
                             one I may not make alone.
  a second release        -- one release.

EXIT
    0  controls hold, the rows verify, and the cost is recorded
    1  a control misbehaved, or a number is unverified -- the row must come out
    2  R21 or the rows are missing -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
PY = ROOT / ".venv" / "bin" / "python"
SUBJECT = "E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor/R21_donor_distance"
HEADING = "### Backfilled findings"
FAKE = "0.7331"          # a number that must NOT be in R21's output
NUM = re.compile(r"\d+\.\d+|\b\d{2,}\b")
sys.path.insert(0, str(ROOT / "assurance"))
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def main() -> int:
    readme = (ROOT / "README.md").read_text()
    if HEADING not in readme:
        print(f"  UNRUNNABLE: `{HEADING}` absent from README.md. Exit 2, never 0."); return 2
    block = readme.split(HEADING, 1)[1].split("\n### ", 1)[0].split("\n## ", 1)[0]
    rows = [l for l in block.splitlines() if l.startswith("|") and "R21_donor_distance" in l]
    if not rows:
        print("  UNRUNNABLE: no backfilled row cites R21. Exit 2, never 0."); return 2

    try:
        from _isolated import ensure_worktree, restore        # noqa: E402
    except Exception as e:
        print(f"  UNRUNNABLE: cannot import the harness ({e}). Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()
    print(f"R388 · one unit of the debt   HEAD {head[:12]}\n")
    print(f"  ⛔ Eight rounds diagnosed the debt and wrote no paragraph. An audit presented as a")
    print(f"     product is the failure the constitution names, so this round WRITES ONE and")
    print(f"     measures what it cost.\n")
    print(f"  PRODUCED: {len(rows)} row(s) in the root README's `What was established` table, under")
    print(f"  a heading marking them as BACKFILL — a row written months after its round is a")
    print(f"  different object from one written beside it, and blending them would be the drift")
    print(f"  those rounds were about.")

    # ---- the fresh run, timed ------------------------------------------------------------------
    wt = ensure_worktree()
    subprocess.run(["git", "checkout", "-f", "-q", head], cwd=str(wt), capture_output=True)
    subprocess.run(["git", "clean", "-fdq"], cwd=str(wt), capture_output=True)
    restore(wt)
    d = wt / SUBJECT
    if not (d / "run.py").exists():
        print(f"  UNRUNNABLE: {SUBJECT}/run.py absent in the worktree. Exit 2, never 0."); return 2
    t0 = time.monotonic()
    p = subprocess.run([str(PY), "run.py"], cwd=str(d), capture_output=True, text=True, timeout=900)
    secs = time.monotonic() - t0
    out = p.stdout + p.stderr
    restore(wt)
    print(f"\n  FRESH RUN of R21 in an isolated worktree — not its committed artifact, because")
    print(f"  R386 measured the artifact carries 9% of a finding's numbers")
    print(f"    exit {p.returncode} · wall-clock {secs:.1f}s · {len(out.splitlines())} lines of output")
    if p.returncode != 0:
        print(f"  UNVERIFIED — R21 did not complete, so nothing can be checked against it. Exit 1.")
        return 1

    run_nums = set(NUM.findall(out))

    def unverified(text):
        return sorted(n for n in set(NUM.findall(text)) if n not in run_nums)

    # ---- CONTROLS ------------------------------------------------------------------------------
    planted = "\n".join(rows) + f" | planted {FAKE} |"
    pos_catch = FAKE in unverified(planted)
    fake_absent = FAKE not in run_nums
    print(f"\n  CONTROLS on the verifier")
    print(f"    FABRICATION (+)  a planted number `{FAKE}` (absent from the run: {fake_absent})")
    print(f"                     is flagged: {pos_catch}  "
          f"{'PASS' if pos_catch and fake_absent else 'FAIL — the verifier cannot catch invention'}")

    # ---- the verification -----------------------------------------------------------------------
    bad = unverified("\n".join(rows))
    # round ids and link paths are not claims; strip them before judging
    ids = set(re.findall(r"R(\d+)_", "\n".join(rows))) | {"21", "384", "386", "387"}
    bad = [n for n in bad if n not in ids]
    neg_ok = (len(bad) == 0)
    print(f"    FABRICATION (-)  the REAL rows verify: {neg_ok}  "
          f"{'PASS' if neg_ok else 'FAIL'}")
    all_nums = sorted(set(NUM.findall("\n".join(rows))) - ids)
    print(f"\n  EVERY NUMBER IN THE BACKFILLED ROWS, checked against the fresh run")
    for n in all_nums:
        print(f"    {n:>10}   {'in the run output' if n in run_nums else '⛔ NOT IN THE OUTPUT'}")

    ctrl_ok = pos_catch and fake_absent
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — the verifier cannot catch a fabricated number, so its pass on the")
        print("  real rows means nothing. Exit 1."); return 1
    if bad:
        print(f"  W-FABRICATED — {len(bad)} number(s) in the backfilled rows do NOT appear in a")
        print(f"  fresh run of the round they cite: {bad}")
        print(f"  ⛔ THE ROWS COME OUT. A wrong number in a findings table is worse than an absent")
        print(f"     one, because an empty row is visibly empty and a plausible wrong one is not.")
        v = "W_FABRICATED"
        rc = 1
    elif secs < 60:
        print(f"  W-CHEAP — {len(all_nums)} numbers all verified, and the machine time is {secs:.1f}s.")
        print(f"  The unit cost is dominated by ATTENTION rather than compute: reading the output and")
        print(f"  deciding what the finding IS took far longer than producing it. So the 237")
        print(f"  remaining units are a WRITING project, not a compute one — which is the harder")
        print(f"  kind to pipeline and the easier kind to start.")
        v = "W_CHEAP"
        rc = 0
    else:
        print(f"  W-EXPENSIVE — {len(all_nums)} numbers verified, machine time {secs:.1f}s. The debt")
        print(f"  is a compute backlog and can be pipelined, which is a different plan from a")
        print(f"  writing one.")
        v = "W_EXPENSIVE"
        rc = 0

    print(f"\n  ⚠ n = 1, AND IT IS REPORTED AS ONE OBSERVATION. R387 measured 3 of 12 rounds")
    print(f"    exceeding 90s, so the cost distribution is wide and {secs:.1f}s does not summarise")
    print(f"    it. Multiplying by 237 would be the arithmetic trap wearing a project plan.")
    print(f"  ⚠ AND ONLY THE NUMBERS ARE CHECKED. Whether the SENTENCE around them states the right")
    print(f"    finding is a judgement, and that is the one I may not make alone.")

    art = dict(stamp(str(SELF)), head=head[:12], subject=SUBJECT, rows=rows,
               run_seconds=round(secs, 1), run_exit=p.returncode,
               numbers_checked=all_nums, unverified=bad,
               controls=dict(fabrication_pos=pos_catch, fake_absent=fake_absent,
                             fabrication_neg=neg_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r388_unit_cost.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
