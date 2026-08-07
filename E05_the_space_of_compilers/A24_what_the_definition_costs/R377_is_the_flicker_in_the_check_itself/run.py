"""R377 — R375 called it a flicker across commits. Is it a flicker across RUNS, at one commit?

R375 bisected six gates and found `attack_every_check` non-monotone: red at two commits BEFORE the
one binary search returned. It withdrew the breaking commit rather than publish a spurious one, and
attributed nothing. R376's NEXT then blamed a read-isolation hazard I had introduced -- three rounds
pointing at `scratchpad/assurance_wt`, which is also `_isolated.py`'s default worktree.

⛔ THAT ATTRIBUTION IS WRONG AND THE SOURCE SAYS SO IN ONE LINE. `attack_every_check` runs with
   `cwd=ROOT` -- THE LIVE TREE -- and uses `tempfile.mkdtemp` only for one clone plant. It never
   touches `assurance_wt`. So my worktree could not have contaminated it, and R376's NEXT named the
   wrong mechanism. I am not repairing that sentence in R376; it is committed and it was wrong, and
   this round is the correction.

⛔ WHAT THE SOURCE DOES SAY IS FAR MORE INTERESTING: it PLANTS FILES INTO THE LIVE TREE and restores
   them. Two consecutive invocations, minutes apart, at the same commit, printed:
       restore verification: planted files DIRTY  (3 watched)     -> exit 2
       restore verification: planted files CLEAN  (3 watched)     -> ?
   Same tree, same commit, same code. If that is real, then R375's `flicker across commits` is not
   about commits at all -- it is a check that does not return the same answer twice, and a bisect
   over it was measuring noise with a binary search.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. N identical runs
   are free to return N identical results. Nothing in the design forces variation, and the positive
   control below establishes that the REPEAT HARNESS itself reports `identical` when the subject is
   deterministic -- so a variation, if seen, is the subject's and not the harness's.

⚠ AND THIS ROUND MUTATES THE LIVE TREE, because the subject does. Cleanliness is verified from git
  BEFORE and AFTER every run, any dirt is restored from git, and a run that cannot be cleaned aborts
  the round. The safety check is also the measurement: a plant that survives IS the state-dependence.

ESTIMAND        over N independent invocations of `attack_every_check` at ONE commit in a clean
                tree: (a) the set of distinct exit codes, (b) the set of distinct per-check verdict
                tables, (c) the set of distinct `restore verification` outcomes, and (d) whether the
                tree is dirty after each run.

IDENTIFICATION  Identified at this commit, this tree, this interpreter. NOT identified: whether the
                variation has the same cause at other commits -- R375's bracket is not re-walked
                here, and a claim about it would need the ladder again.
                NOT identified: WHICH of the check's internal steps is non-deterministic. This
                measures THAT it varies, not where.

SCOPE           population: N runs of one check · instrument: exit code plus the verbatim verdict
                lines · baseline: byte-identical output across runs · regime: HEAD, live tree.

WORLDS
  W-DETERMINISTIC     all N runs identical. Then the 1->2 move I observed was caused by something
                      that changed between them -- most plausibly my `_isolated` repair -- and it is
                      attributable rather than intrinsic. R375's flicker would still need an
                      explanation, but not this one.
  W-NONDETERMINISTIC  the runs differ at one commit with nothing changing between them. Then
                      R375's `flicker across commits` is a category error: the check does not
                      return the same answer twice, and ANY bisect over it measures noise. That
                      also means the OTHER five gates' breaking commits need re-examining, because
                      the same search assumed reproducibility it never tested.
  W-SELF-CONTAMINATING deterministic per run, but a run leaves the tree dirty and the next run sees
                      it. Then the check poisons its own successor and the fix is its restore, not
                      its logic.

PREDICTION MATRIX
  W-DETERMINISTIC      -> 1 distinct exit, 1 distinct table, tree clean after every run
  W-NONDETERMINISTIC   -> >1 distinct exit or table, tree clean after every run
  W-SELF-CONTAMINATING -> tree dirty after >=1 run, and the following run differs

PRE-REGISTERED KILL -- conditional on the controls, never on a count alone.
    if repeat_harness_positive_control_ok and tree_was_clean_at_start:
        if any run left the tree dirty                -> W-SELF-CONTAMINATING
        elif distinct_exits == 1 and distinct_tables == 1 -> W-DETERMINISTIC
        else                                          -> W-NONDETERMINISTIC
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.
⚠ The branches are ordered, not exclusive: a self-contaminating check is also non-deterministic in
  its output. The ordering says which FIX applies, and the other facts are printed regardless.

CONTROLS
  REPEAT (+)    a check known deterministic (`consistency`) is run the same N times through the same
                harness and must return ONE distinct result. If the harness reports variation there,
                the variation is the harness's and every number below is void.
  REPEAT (-)    a deliberately non-deterministic subject -- a two-line script exiting on a coin flip
                seeded from the clock -- must be reported as VARYING. A repeat-harness that has
                never reported variation cannot be trusted to report it here. Both directions,
                because a harness that always says `identical` would pass the positive control.
  TREE CLEAN    `git status --porcelain` before the round and after every run. Non-empty is
                recorded, restored from git, and counted -- never silently cleaned.
  ABORT         if the tree cannot be restored, the round exits 1 and says so. A measurement that
                leaves the repository damaged is not a measurement.

MULTIPLICITY    no test family. N runs of one subject plus N of two controls, all recorded.
SEEDS           the subject's own; this round adds no randomness except in the negative control,
                where it is the point.
ARTIFACT        results/r377_flicker.json with the source hash.

IMPOSSIBLE HERE
  WHICH internal step varies   -- needs tracing inside the subject; this measures that it varies.
  the other five gates         -- their bisects rest on the same untested reproducibility
                                  assumption, which is named as the consequence, not measured here.
  a second release             -- one release.

EXIT
    0  controls hold and the check is classified
    1  a control misbehaved, or the tree could not be restored -- UNVERIFIED
    2  the tree was already dirty, or the subject is missing -- never a silent pass
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
PY = ROOT / ".venv" / "bin" / "python"
SUBJECT = "attack_every_check"
DET_CONTROL = "consistency"
N = 8
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def git(*a):
    return subprocess.run(["git", *a], cwd=str(ROOT), capture_output=True, text=True, timeout=300)


# ⛔ THE ROUND'S OWN DIRECTORY IS NOT CONTAMINATION -- which is precisely R376's finding, applied
#   to myself one round later. `_isolated`'s criterion counted the probe the selftest itself wrote;
#   a start-clean check that counts THIS round's own uncommitted source and artifact would make the
#   same error and would be unrunnable by construction. Everything else in the tree still counts.
OWN = "E05_the_space_of_compilers/A24_what_the_definition_costs/R377_"


def dirty():
    out = []
    for l in git("status", "--porcelain").stdout.split("\n"):
        if not l.strip():
            continue
        if l[3:].strip().strip('"').startswith(OWN):
            continue
        out.append(l)
    return out


def run_check(name):
    p = subprocess.run([str(PY), str(ROOT / "assurance" / f"{name}.py")], cwd=str(ROOT),
                       capture_output=True, text=True, timeout=400)
    return p.returncode, p.stdout


# the verdict TABLE, normalised: the lines that state a per-check outcome. Timing and paths are
# stripped so a difference means a different VERDICT, never a different millisecond.
ROW = re.compile(r"^\s{2,}(\S[^\n]*?)\s{2,}(YES|NO|INVALID)\s{2,}(.*)$", re.M)


def table_of(out):
    return tuple(sorted((m.group(1).strip(), m.group(2), m.group(3).strip()[:70])
                        for m in ROW.finditer(out)))


def restore_line(out):
    m = re.search(r"restore verification: planted files (\w+)", out)
    return m.group(1) if m else "ABSENT"


def main() -> int:
    if not PY.exists() or not (ROOT / "assurance" / f"{SUBJECT}.py").exists():
        print("  UNRUNNABLE: interpreter or subject missing. Exit 2, never 0."); return 2
    start_dirty = dirty()
    if start_dirty:
        print(f"  UNRUNNABLE: the live tree is already dirty ({len(start_dirty)} path(s)).")
        print(f"  This round mutates the live tree and must start from a clean one. Exit 2.")
        for l in start_dirty[:8]:
            print(f"    {l}")
        return 2

    head = git("rev-parse", "HEAD").stdout.strip()[:12]
    print(f"R377 · does the check return the same answer twice?   HEAD {head}, N={N}\n")
    # ⛔ R376's NEXT blamed my shared worktree. MEASURED rather than asserted, because "the source
    #   says so in one line" is exactly the convincing description this campaign distrusts: the
    #   subject invokes SIX other checks, and if any of THEM used the worktree the coupling would
    #   be indirect and my refutation would be wrong. So all seven files are grepped here and the
    #   count goes into the artifact.
    INVOKED = ["every_round_reaches_the_readme", "retired_framing_in_assertion_positions",
               "corrections_propagated", "code_states_a_bound_the_reader_never_sees",
               "readme_row_carries_the_verdict", "results_match_their_code"]
    wt_refs = {}
    for name in [SUBJECT] + INVOKED:
        f = ROOT / "assurance" / f"{name}.py"
        txt = f.read_text() if f.exists() else ""
        wt_refs[name] = sum(txt.count(t) for t in
                            ("_isolated", "ASSURANCE_WORKTREE", "assurance_wt"))
    coupled = [k for k, v in wt_refs.items() if v]
    print(f"  ⛔ R376's NEXT blamed my shared worktree. MEASURED, not asserted — the subject AND")
    print(f"     the {len(INVOKED)} checks it invokes were all grepped for worktree references:")
    print(f"     files referencing the shared worktree: {coupled if coupled else 'NONE of 7'}")
    if coupled:
        print(f"     ⚠ the coupling is INDIRECT and real; R376's attribution is NOT refuted.")
    else:
        print(f"     `{SUBJECT}` runs with cwd=ROOT — the LIVE TREE — and no invoked check reaches")
        print(f"     assurance_wt. R376's NEXT named the wrong mechanism and is withdrawn here")
        print(f"     rather than edited out of R376.")
    print()

    # ---- REPEAT-HARNESS CONTROLS, both directions, before the subject ------------------------
    det = [run_check(DET_CONTROL) for _ in range(N)]
    det_exits = {r[0] for r in det}
    pos_ok = len(det_exits) == 1
    nd = ROOT / "assurance" / "_r377_coinflip.py"
    nd.write_text("import sys, time\nsys.exit(int(time.time_ns()) % 2)\n")
    flips = set()
    for _ in range(N * 4):
        flips.add(subprocess.run([str(PY), str(nd)], capture_output=True).returncode)
    nd.unlink(missing_ok=True)
    neg_ok = len(flips) > 1
    print("  CONTROLS on the repeat harness, before the subject runs")
    print(f"    REPEAT (+)  `{DET_CONTROL}` over {N} runs -> exits {sorted(det_exits)}  "
          f"{'PASS' if pos_ok else 'FAIL'}")
    print(f"    REPEAT (-)  a clock-seeded coin flip -> exits {sorted(flips)}  "
          f"{'PASS — the harness CAN report variation' if neg_ok else 'FAIL — it cannot'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the repeat harness is blind in one direction. Exit 1."); return 1

    # ---- the subject -------------------------------------------------------------------------
    print(f"\n  {SUBJECT} × {N}, live tree verified from git after every run")
    print(f"    {'run':>4}{'exit':>6}{'restore':>10}{'rows':>6}{'dirty after':>13}")
    runs, could_not_clean = [], []
    for i in range(N):
        rc, out = run_check(SUBJECT)
        d = dirty()
        if d:
            git("checkout", "--", ".")
            for ln in d:
                if ln.startswith("??"):
                    p = ROOT / ln[3:].strip().strip('"').rstrip("/")
                    try:
                        if p.is_file():
                            p.unlink()
                    except Exception:
                        pass
            if dirty():
                could_not_clean.append(i)
        tb = table_of(out)
        runs.append(dict(run=i, exit=rc, restore=restore_line(out), n_rows=len(tb),
                         table=[list(t) for t in tb], dirty_after=len(d),
                         dirty_paths=[x[:60] for x in d[:5]]))
        print(f"    {i:>4}{rc:>6}{restore_line(out):>10}{len(tb):>6}{len(d):>13}")

    exits = {r["exit"] for r in runs}
    tables = {tuple(tuple(x) for x in r["table"]) for r in runs}
    restores = {r["restore"] for r in runs}
    any_dirty = [r["run"] for r in runs if r["dirty_after"]]
    print(f"\n    distinct exit codes      : {sorted(exits)}")
    print(f"    distinct verdict tables  : {len(tables)}")
    print(f"    distinct restore verdicts: {sorted(restores)}")
    print(f"    runs leaving the tree dirty: {any_dirty if any_dirty else 'none'}")

    if could_not_clean:
        print(f"\n  ⛔ the tree could not be restored after run(s) {could_not_clean}. A measurement")
        print(f"     that leaves the repository damaged is not a measurement. Exit 1.")
        return 1

    # what differs, row by row, when tables differ
    diffs = []
    if len(tables) > 1:
        base = runs[0]["table"]
        for r in runs[1:]:
            for a, b in zip(base, r["table"]):
                if a != b and [a, b] not in diffs:
                    diffs.append([a, b])
        print(f"\n  ROWS THAT DIFFER BETWEEN RUNS — the same check, the same commit:")
        for a, b in diffs[:8]:
            print(f"    {a[0]}")
            print(f"      run 0 : {a[1]:>8}  {a[2]}")
            print(f"      later : {b[1]:>8}  {b[2]}")

    # ---- verdict ------------------------------------------------------------------------------
    print()
    if any_dirty:
        print(f"  W-SELF-CONTAMINATING — {len(any_dirty)} of {N} runs left the live tree dirty, so a")
        print(f"  run can see the previous run's residue. The fix is the check's RESTORE, not its")
        print(f"  logic, and until it is fixed no result from it is reproducible by construction.")
        v = "W_SELF_CONTAMINATING"
    elif len(exits) == 1 and len(tables) == 1:
        print(f"  W-DETERMINISTIC — {N} runs, one exit code, one verdict table, tree clean")
        print(f"  throughout. The 1->2 move I saw earlier was caused by something that changed")
        print(f"  between those two invocations — my `_isolated` repair is the candidate — and is")
        print(f"  attributable rather than intrinsic. R375's flicker still needs an explanation,")
        print(f"  but it is not this one.")
        v = "W_DETERMINISTIC"
    else:
        print(f"  W-NONDETERMINISTIC — at ONE commit, with nothing changing between invocations,")
        print(f"  the check returns {len(exits)} distinct exit code(s) and {len(tables)} distinct")
        print(f"  verdict table(s). ⛔ So R375's `flicker across commits` is a CATEGORY ERROR: the")
        print(f"  check does not return the same answer twice, and a binary search over it was")
        print(f"  measuring noise. R375 withdrew its breaking commit on the monotonicity control,")
        print(f"  which was right for a reason it had not established.")
        print(f"  ⛔ AND THE CONSEQUENCE REACHES THE OTHER FIVE: their bisects assumed a")
        print(f"     reproducibility none of them tested. That is a named residual, not a finding —")
        print(f"     this round measured ONE subject and says nothing about whether they vary.")
        v = "W_NONDETERMINISTIC"

    print(f"\n  ⚠ SCOPE: this measured THAT the subject varies, never WHERE. Which internal step is")
    print(f"    non-deterministic needs tracing inside it and is not claimed here.")

    art = dict(stamp(str(SELF)), head=head, n_runs=N, subject=SUBJECT,
               worktree_refs=wt_refs, worktree_coupled=coupled,
               runs=runs, distinct_exits=sorted(exits), n_distinct_tables=len(tables),
               distinct_restore=sorted(restores), dirty_runs=any_dirty, row_diffs=diffs,
               controls=dict(repeat_pos=pos_ok, repeat_neg=neg_ok,
                             det_exits=sorted(det_exits), flip_exits=sorted(flips),
                             tree_clean_at_start=True),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r377_flicker.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
