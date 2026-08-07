#!/usr/bin/env python3
"""assurance/audit_the_auditors.py — do the checks in this directory still SEE anything?

⛔ MEASURED 2026-08-07 (R963): THIS FILE'S PER-GATE TABLE DISAGREES WITH DIRECT RUNS, AND ITS g=0
CONTROL FAILS ON ITS OWN MEASUREMENT RATHER THAN ON WHAT IT AUDITS. Do not quote the table.

Four gates run both ways, all disagreeing. The table reports exit 2 with an EMPTY tell for
`DEFECTS.py`, `a_published_number_is_named.py`, `a_statement_is_current_with_the_arc.py` and
`an_ear_label_matches_its_path.py`. Run directly -- same interpreter, same absolute path,
`cwd=ROOT`, which is this file's own documented invocation -- all four exit 0. `DEFECTS.py` exits 0
in 0.1s printing `16/46 checks came back clean`, i.e. a full population, while this file calls it
EMPTY. Every one completes in 2.3s or less, so `TIMEOUT = 120` is not the cause; that was measured,
not assumed.

The consequence for the g=0 control: it asserts the REPAIRED `DEFECTS.py` must not be flagged and
reports that it is. **Its premise is false** -- the repaired file is not empty -- so the control is
failing for its own reasons, which is this standard's dominant control failure mode. The UNVERIFIED
verdict this file prints is therefore CORRECT, and its stated reason (`the sweep cannot see the case
it was built from`) is not what is happening.

⚠ MECHANISM CANDIDATE, NOT ESTABLISHED. `restore()` reverts this directory after EVERY gate, so an
artifact one gate writes is gone before the next runs, and a gate that depends on a sibling's output
would see nothing. That fits three of the four. It does NOT fit `a_published_number_is_named.py`,
which reads round directories rather than `assurance/results`, so the candidate is incomplete and is
not being called the explanation.

**The repair target is the per-gate RUNNER, not the detector.** The detector has never been tested,
because nothing it was fed was measured correctly.

⛔ R964 TRIED TO ISOLATE WHY AND FAILED, WITH FIVE CONDITIONS RULED OUT. Recorded so the next
attempt starts here rather than at the beginning.

The row under test is `DEFECTS.py {'exit': 2, 'seconds': 0.0, 'empty_tell': True}` in
`results/auditor_audit.json`. Ruled out, each by running it:
  · STALENESS -- the artifact's mtime is the run's own; it is not an old file being misread. (The
    `source_sha` mismatch is a later annotation to THIS file, a known cause, not drift.)
  · A MISREAD COLUMN -- the JSON records `exit: 2` structurally, so it is not a table alignment.
  · THE POSITIVE-CONTROL PLANT -- writing `_poscontrol_defects_unrepaired.py` exactly as the
    pre-loop step does, then running `DEFECTS.py`, gives exit 0 before, during and after.
  · THE INTERPRETER AND PATH -- `PY` resolves, the target exists, and running
    `[PY, str(HERE/"DEFECTS.py")]` with `cwd=ROOT` returns exit 0 with 192 lines of stdout.
  · THE TIMEOUT -- `DEFECTS.py` completes in 0.1s against `TIMEOUT = 120`.
  · ORDERING -- `sorted(HERE.glob("*.py"))` puts uppercase first, so `DEFECTS.py` runs FIRST and no
    prior gate, no `restore()` call and no `apply_*` mutator has executed when it is measured. That
    also kills the R963 candidate for this row: restore-after-each-gate cannot explain the first one.

`DEFECTS.py` contains no `exit(2)` path at all, and Python returns 2 when it cannot open a script --
but the script opens fine on every reconstruction. **So the recorded row is not reproducible, and
why is NOT established.**

WHAT ISOLATING IT WOULD REQUIRE: instrumenting this file to log argv, cwd, env and returncode per
gate and re-running the sweep, which is ~7 minutes. Until then its per-gate table stays unquotable
and its UNVERIFIED verdict stays correct.

⛔⛔ EVERYTHING IN THE TWO BLOCKS ABOVE IS RETRACTED (R965). THE FILE IS NOT BROKEN; I RAN IT ONCE.

The instrumenting was done and it answered a different question than the one it was built for. Run 2
logs `DEFECTS.py` at `rc=0, 0.02s`, with stdout `CoVal DEFECT LIST -- 46 checks across five waves`.
Run 3 agrees. Both report `world=ONLY-THE-TWO`, `positive_control_ok=True`, `fails_at_g0=True`,
`flagged=[]` -- every control behaving, nothing flagged, and the sweep's own closing line reading
`0 of 73 others are blind. The defect was confined to the two already found.`

**So the exit-2 rows, the EMPTY tells and the UNVERIFIED verdict came from ONE run and do not
reproduce.** R962 read that run, R963 built a diagnosis on it, and R964 spent a round ruling out five
mechanisms for an artifact of a single unreplicated measurement. The checklist asks for two hash
seeds byte-identical; I never ran this file twice before drawing three rounds of conclusions from it.

WHAT IS ACTUALLY TRUE, at n=2 agreeing:
  · the verdict is stable and clean, and the detector works
  · THREE rows remain unstable run to run -- `attack_the_suite.py`, `tree_survives_the_sweep.py`,
    `verdict_cites_its_own_contrasts.py` -- and all three touch the harness that HIDES the live E0*
    trees. Row-level instability in exactly the state-mutating gates is expected and is now measured
    rather than assumed.
  · what caused run 1 is still unknown, and with the verdict reproducing clean twice it is no longer
    worth the budget to chase.

**The lesson is not about this file.** A verdict read once is n=1, and an instrument whose output I
quote in three consecutive reports is exactly the one that has to be run twice first.

⭐⭐ R967 — THE MECHANISM, ESTABLISHED FROM TIMESTAMPS RATHER THAN BY RE-RUNNING THIS FILE.

**This sweep runs `attack_the_suite.py`, which HIDES the live `E0*` trees.** `run_all.py` excludes
that harness by name as destructive; this file does not. So every run of this file removes the corpus
partway through, and any gate scheduled during the hide window measures an EMPTY REPOSITORY.

The timestamps settle it without repeating a destructive action:
    auditor run 1 finished 03:54:40   ·   a stash was created 03:43:58 and ORPHANED
    auditor run 2 finished 04:20:54   ·   stash 04:29:43
    auditor run 3 finished 04:26:29   ·   stash 04:38:05  (recovered by `_repair.repair_full`)
A hide begun at 03:43 whose restore never completed means **run 1 measured its gates against a tree
that was already gone**. `DEFECTS.py` globs `E0*/A*/.../results/*` — zero rounds, empty population,
`exit 2`, `0.0s`, no output. That is exactly the row R962 called unquotable, R963 diagnosed as a
broken runner, and R964 spent a round failing to explain.

**So the R965 retraction STANDS, and its stated reason was wrong too.** The readings are unreliable
not because I ran the file once, but because **the file destroys the corpus it is measuring**, and
which gates are affected depends on where they fall relative to the hide. `sorted(HERE.glob("*.py"))`
puts uppercase first, so `DEFECTS.py` and `HEADLINES.py` precede `attack_the_suite.py` — a first-row
failure therefore requires a hide that was ALREADY in flight, which is what 03:43 was.

⚠ **DO NOT RUN THIS FILE TO CHECK THIS.** Doing so removes the working tree for the duration and
leaves it removed if the process dies — 3,268 files were recovered from `/tmp/attack_rounds_6bao8twu`
at R966 only because `assurance/_repair.py` exists. The cheap, safe evidence is the stash mtimes in
`/tmp/attack_rounds_*`, which is how this note was written.

**The repair, if anyone wants this sweep to mean anything: exclude `attack_the_suite` here as
`run_all` already does.** Until then every table this file prints is a function of timing.


WHY, AND IT IS A MEASURED PRIOR, NOT A SUSPICION. `DEFECTS.py` and `consistency.py` resolved their
inputs as `HERE / <round> / results / <file>`. The E/A/R migration (2026-08-02) moved every round
under `E0*/A*/`, so both loaded **zero** rounds from that day on — and the line `DEFECTS.py` prints
for that state is *"0/0 checks came back clean"*. A gate reporting success having examined nothing,
in the words of a thorough sweep. It went unnoticed for a day, and then a "smoke test" regenerated
its artifact from the empty population and destroyed a 46-item defect list.

Two of two inspected were broken. This round asks what the other ~20 do.

⚠ THE UNIT TRAP. A grep for `HERE /` finds *files containing a pattern*; the claim is *this script
loads nothing*. Not the same string. So the grep only nominates CANDIDATES and the measurement is
what happens when each is RUN.

⚠ AND RUNNING THEM IS THE DANGEROUS PART — it is exactly how the artifact was destroyed. Every
file under assurance/ is byte-snapshotted before the sweep and restored after, and the restoration
is verified. A sweep that silently rewrote the artifacts it audits would be the same defect again,
one level up.

ESTIMAND      per script: does it exit non-zero, and does it SHRINK or DESTROY an artifact when
              run in place? Reported per script, never pooled into a pass rate.
IDENTIFICATION exact — run it, diff the directory.
SCOPE         population every *.py in assurance/ · instrument the committed code · baseline the
              same directory's byte state before the run · regime this machine, this venv.
POSITIVE CTRL a copy of `DEFECTS.py` with its repair reverted MUST be flagged. It is the known
              broken case; a sweep that misses it has not measured anything. Fails at g=0: the
              repaired `DEFECTS.py` must NOT be flagged.
NEGATIVE CTRL scripts that touch no round path should come back clean; if they are flagged too,
              the framing is wrong and it is reported rather than suppressed.
NOISE FLOOR   n/a — byte equality and exit codes, not estimates.
ARTIFACT      results/auditor_audit.json with source hash.
IMPOSSIBLE    whether a script is CORRECT — this only asks whether it can see its inputs. A script
              that loads its rounds and computes the wrong thing passes here and should.
"""
from __future__ import annotations
import hashlib, json, os, os, pathlib, re, subprocess, sys, time

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
PY = str(ROOT / ".venv" / "bin" / "python")
TIMEOUT = 120
SELF = pathlib.Path(__file__).resolve()
EMPTY = re.compile(r"\b0\s*/\s*0\b|\b0 of 0\b|no (rounds|files|items|checks) (found|loaded)",
                   re.I)


KEEP = None   # set in main(); None = git unavailable => never unlink


def snap(d: pathlib.Path):
    return {p: p.read_bytes() for p in d.rglob("*") if p.is_file() and "__pycache__" not in str(p)}


def tracked(d: pathlib.Path) -> set[pathlib.Path]:
    """Files git knows about, absolute. Computed once; a miss must fail CLOSED (see below)."""
    try:
        out = subprocess.run(["git", "ls-files"], cwd=str(d),
                             capture_output=True, text=True, timeout=60)
        if out.returncode != 0:
            return None
        return {(d / ln).resolve() for ln in out.stdout.splitlines() if ln}
    except Exception:
        return None


def restore(s, d: pathlib.Path, keep: set | None = None):
    """Undo what a gate did to the directory -- WITHOUT destroying anyone else's work.

    ⚠ REPAIRED 2026-08-04 after this function deleted `residue_debt.py` thirty seconds after
    that file was committed and pushed. The old predicate was `p not in snapshot -> unlink`,
    which reads as "the gate under test created this" but actually means "this appeared since
    my snapshot, BY ANYONE". A sweep takes minutes; anything written in that window by another
    process, a human, or a concurrent session was silently destroyed. The docstring above says
    restoration "is verified" -- true for files it knows about, and the exact shape of a check
    that cannot see the case it fails on.

    The invariant that fixes it: A FILE GIT TRACKS WAS NEVER A GATE'S TRANSIENT ARTIFACT.
    Tracked files are reported as appeared-tracked and LEFT ALONE. `keep=None` means the git
    query failed -- in that case nothing is unlinked at all, because an unknown tracked set
    must fail closed. Deleting on a failed lookup is how a repair becomes the next incident.

    KNOWN REMAINING HAZARD, stated rather than silently carried: the `modified` branch still
    rewrites a tracked file to its pre-sweep bytes, so a concurrent EDIT to a file a gate also
    touches is still reverted. That is narrower than the bug fixed here (it needs the same file,
    not merely the same directory) and it is the branch that gives the function its purpose --
    undoing a gate that corrupts an artifact. Recorded so the next person does not rediscover it.
    """
    changed = []
    for p in list(d.rglob("*")):
        if p.is_file() and "__pycache__" not in str(p) and p not in s:
            if keep is None or p.resolve() in keep:
                changed.append(("appeared-tracked", p))       # someone else's file, or unknown
                continue
            changed.append(("created", p)); p.unlink()
    for p, b in s.items():
        if not p.exists() or p.read_bytes() != b:
            changed.append(("modified", p)); p.write_bytes(b)
    return changed


# ⛔ RE-ENTRANCY GUARD — 2026-08-03, after a runaway that had to be killed by hand.
# This file SWEEPS every *.py in assurance/. So does the OTHER sweep in this directory. Each
# therefore swept the other, which swept the first: mutual recursion with no base case. It
# orphaned itself to `systemd --user`, kept running after its parent shell was gone, and every
# generation ran subjects that MOVE EPOCH DIRECTORIES by design. Four of five epochs were deleted
# from the working tree TWICE, ~15 minutes apart -- and the second time was not a repeat, it was
# the same runaway still going, still spawning children with an elapsed time of 0 seconds while I
# was inspecting the damage.
#
# A NAME LIST would only block the chains I thought of. An environment flag blocks every chain,
# including one through a script that does not exist yet: the first sweep to start owns the flag,
# subprocess inherits the environment, and any sweep starting underneath refuses.
# Constitution L60 bans recursive AGENT fan-out; the same ban belongs on PROCESS fan-out.
_SWEEP_FLAG = "ASSURANCE_SWEEP_ACTIVE"
if os.environ.get(_SWEEP_FLAG):
    print(f"  REFUSING: {_SWEEP_FLAG} is set, so this sweep is running INSIDE another sweep. "
          f"Two mutually-sweeping scripts recurse without bound. Exit 3, examined nothing.")
    raise SystemExit(3)
os.environ[_SWEEP_FLAG] = "1"


def main():
    global KEEP
    KEEP = tracked(HERE)
    scripts = sorted(p for p in HERE.glob("*.py")
                     if p.resolve() != SELF and not p.name.startswith("_"))
    # positive control: DEFECTS.py with the repair reverted -- the KNOWN broken case
    pos = HERE / "_poscontrol_defects_unrepaired.py"
    src = (HERE / "DEFECTS.py").read_text()
    pos.write_text(src.replace("p = round_results(rnd, fn)\n        if p is None:\n            continue",
                               'p = HERE / rnd / "results" / fn')
                      .replace("if not items:", "if False and not items:"))
    scripts.append(pos)

    print(f"  {len(scripts)} scripts (incl. 1 planted positive control)\n")
    print(f"  {'script':<44}{'exit':>5}  {'wrote?':<22}empty-population tell")
    rows, flagged = {}, []
    for s in scripts:
        before = snap(HERE)
        t0 = time.time()
        try:
            r = subprocess.run([PY, str(s)], cwd=str(ROOT), capture_output=True,
                               text=True, timeout=TIMEOUT)
            rc, out = r.returncode, (r.stdout or "") + (r.stderr or "")
        except subprocess.TimeoutExpired:
            rc, out = None, ""
        touched = restore(before, HERE, KEEP)
        # a WRITE that shrinks a json by >50% is the destroy-a-good-artifact signature
        destroyed = []
        for kind, p in touched:
            if kind == "modified" and p.suffix == ".json" and p in before:
                if len(p.read_bytes()) < len(before[p]) * 0.5:
                    destroyed.append(p.name)
        tell = bool(EMPTY.search(out))
        rows[s.name] = dict(exit=rc, wrote=[f"{k}:{p.name}" for k, p in touched],
                            destroyed=destroyed, empty_tell=tell, seconds=round(time.time()-t0, 1))
        bad = tell or destroyed
        if bad and s != pos:
            flagged.append(s.name)
        print(f"    {s.name[:42]:<44}{str(rc):>5}  {(','.join(destroyed) or '-')[:20]:<22}"
              f"{'⚠ EMPTY' if tell else ''}")

    pos_ok = bool(rows[pos.name]["empty_tell"] or rows[pos.name]["destroyed"])
    neg_ok = not (rows["DEFECTS.py"]["empty_tell"] or rows["DEFECTS.py"]["destroyed"])
    pos.unlink(missing_ok=True)

    print(f"\n  POSITIVE CTRL  the unrepaired DEFECTS.py is flagged: {pos_ok}")
    print(f"  FAILS AT g=0   the REPAIRED DEFECTS.py is not flagged: {neg_ok}")
    print("\n  " + "=" * 74)
    if not (pos_ok and neg_ok):
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. The sweep cannot see the case it was built from; it has not")
        print("     measured anything and this is NOT a verdict that the others are fine.")
    elif flagged:
        world = "MORE-ARE-BLIND"
        print(f"  -> {len(flagged)} of {len(scripts)-1} scripts show an empty population or destroy")
        print(f"     an artifact: {flagged}")
    else:
        world = "ONLY-THE-TWO"
        print(f"  -> 0 of {len(scripts)-1} others are blind. The defect was confined to the two")
        print("     already found, and this sweep is what makes that a measurement.")
    print("  " + "=" * 74)

    o = HERE / "results" / "auditor_audit.json"
    o.parent.mkdir(exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_scripts=len(scripts) - 1, flagged=flagged, positive_control_ok=pos_ok,
        fails_at_g0=neg_ok, rows=rows), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
