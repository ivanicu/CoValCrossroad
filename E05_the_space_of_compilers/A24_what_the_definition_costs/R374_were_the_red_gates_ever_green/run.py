"""R374 — eleven gates are red. Were they ever green, or were they born that way?

R373's commit corrected a false all-clear: the previous round reported "41 doc gates exit 0" from a
shell loop whose `$?` read `basename`'s exit code, not the gate's. Measured properly, TWELVE gates
fail, eleven of them not attributable to any round in this session. R373's NEXT proposed classifying
them, with the hypothesis that most are stale registrations rather than real defects.

⛔ THAT HYPOTHESIS IS NOT WHAT MATTERS, AND SAYING SO IS THE POINT OF THIS ROUND. `stale registration`
   vs `real defect` is a taxonomy, and a taxonomy of my own failures is exactly the kind of thing I
   can produce for free in any shape I like. The decision-relevant question is temporal and has an
   answer that does not depend on my judgement:

       WAS THIS GATE EVER GREEN?

   If a gate has never exited 0 since the day it was committed, then it was never a brake -- the
   campaign added a check it could not satisfy and moved on. If it was green and turned red, there
   is a specific commit that broke it and a real regression to fix. Those are different worlds with
   different actions, and neither is a matter of opinion.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES, both ways and per
   gate. A gate born green and later broken leaves a transition in the ladder below; a gate born red
   leaves none. Nothing about the design forces either. What IS forced, and is labelled rather than
   reported as a finding: a gate committed at time T cannot be measured before T, so `never green`
   is always bounded below by its own birth commit, never by the ladder's oldest rung.

ESTIMAND        for each currently-red gate, the most recent commit at which THE GATE AS IT WAS THEN
                exited 0 on THE TREE AS IT WAS THEN -- or the finding that no such commit exists in
                the sampled ladder.

IDENTIFICATION  Identified only at the sampled commits. A ladder of 12 rungs over 692 commits
                localises a transition to a BRACKET, not a point, and the bracket is what is
                reported. Refining a bracket to a commit is a further bisect and is NOT done here
                for gates whose bracket already answers the question.
                NOT identified: why a gate is red. This round measures WHEN, never WHY -- the two
                are separate questions and conflating them is how a taxonomy gets published as a
                diagnosis.

SCOPE           population: the 11 gates red at HEAD and not attributable to this session ·
                instrument: `git checkout` into a disposable worktree plus the CURRENT interpreter ·
                baseline: exit 0 · regime: the ladder's rungs, named in the artifact.

⚠ THE INSTRUMENT RUNS THE GATE AS IT WAS, NOT AS IT IS. That is a choice and it decides the
  question. Running today's gate on an old tree asks "when did the CORPUS break this rule"; running
  the old gate on the old tree asks "was the campaign GREEN at that time". The second is the
  question, because the claim under test is that the campaign has been reporting green while its
  brake was off. Both are legitimate; only one is measured here, and the other is named in the
  register rather than silently conflated.

WORLDS
  W-BORN-RED     no rung since birth has the gate at 0. It was never a brake. The action is to
                 decide, per gate, whether to satisfy it or retire it -- and a gate nobody can
                 satisfy is a claim about the corpus that the corpus never made.
  W-REGRESSED    a rung has it green and a later rung red. There is a real regression with a
                 findable commit, and the action is to bisect and fix.
  W-MIXED        both patterns occur across the eleven. Then the single sentence "the campaign has
                 no working brake" is wrong in one direction or the other and must be split.

PREDICTION MATRIX
  W-BORN-RED  -> zero gates show a green rung after their birth commit
  W-REGRESSED -> every gate shows a green rung followed by a red one
  W-MIXED     -> some of each; the count is the finding

PRE-REGISTERED KILL -- conditional on the controls, never on the threshold alone.
    if harness_reproduces_head and green_control_ok and red_control_ok:
        g = number of gates with at least one green rung at or after their birth
        if g == 0            -> W-BORN-RED
        elif g == n_gates    -> W-REGRESSED
        else                 -> W-MIXED, and the split is reported per gate
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  HARNESS (+)   a gate GREEN at HEAD in the real tree must come back green when run through the
                worktree at HEAD. If the harness cannot reproduce a known pass, every red it
                reports is its own artifact.
  HARNESS (-)   a gate RED at HEAD in the real tree must come back red through the worktree at
                HEAD. A harness that turns everything green is the flattering failure.
  ABSENT        a gate that did not exist at a rung must be recorded ABSENT, never green. An
                absent file is not a passing check.
  EMPTY         if no rung is evaluable, exit 2. A ladder that measured nothing never passes.

MULTIPLICITY    11 gates x 12 rungs = 132 cells, all recorded in the artifact and the non-green
                ones printed. No selection is made on any threshold.
SEEDS           none -- git checkout is deterministic. Stated rather than padded.
ARTIFACT        results/r374_gate_history.json with the source hash.

IMPOSSIBLE HERE
  WHY each gate is red        -- a separate question; this measures WHEN.
  the exact breaking commit   -- a ladder gives a bracket; a bisect would give the commit, and is
                                 named as the follow-up rather than approximated here.
  gates red before their birth -- undefined, not green. Recorded ABSENT.

EXIT
    0  controls hold and every gate is classified
    1  a control misbehaved -- UNVERIFIED
    2  the ladder is empty or the worktree is unusable -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
WT = pathlib.Path(os.environ.get("R374_WORKTREE", "")) if os.environ.get("R374_WORKTREE") else None
PY = ROOT / ".venv" / "bin" / "python"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

GATES = ["artifacts_are_internally_coherent", "attack_every_check", "attack_no_withdrawn_framings",
         "attack_outcome_variable_declared", "donor_numbers_carry_their_draw_scope", "_isolated",
         "pueue_wait", "readme_row_carries_the_verdict", "seed_filter_is_disclosed",
         "synthesis_cites_recent_work", "verdict_cites_its_own_contrasts"]
GREEN_CONTROL = "consistency"        # known green at HEAD, independently of this harness
RED_CONTROL = "seed_filter_is_disclosed"
RUNGS = (0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 692)
ABSENT, TIMEOUT = "ABSENT", "TIMEOUT"


def git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=str(cwd or ROOT), capture_output=True,
                          text=True, timeout=300)


def run_gate(tree: pathlib.Path, name: str):
    f = tree / "assurance" / f"{name}.py"
    if not f.exists():
        return ABSENT
    try:
        p = subprocess.run([str(PY), str(f)], cwd=str(tree), capture_output=True,
                           text=True, timeout=180)
        return p.returncode
    except subprocess.TimeoutExpired:
        return TIMEOUT


def main() -> int:
    if WT is None or not WT.exists():
        print("  UNRUNNABLE: R374_WORKTREE is unset or missing. This round needs a disposable")
        print("  git worktree; it must never check out commits in the live tree. Exit 2, never 0.")
        return 2
    if not PY.exists():
        print(f"  UNRUNNABLE: {PY} absent. Exit 2, never 0."); return 2

    head = git("rev-parse", "HEAD").stdout.strip()[:12]
    print(f"R374 · were the eleven red gates ever green?   HEAD {head}\n")

    # birth commit per gate -- `never green` is bounded by THIS, never by the ladder's oldest rung
    birth = {}
    for g in GATES:
        r = git("log", "--diff-filter=A", "--format=%H %ad", "--date=short", "-1",
                "--", f"assurance/{g}.py")
        parts = r.stdout.strip().split()
        birth[g] = (parts[0], parts[1]) if len(parts) >= 2 else (None, None)

    # ---- CONTROLS on the harness itself, before any history is read -------------------------
    live_green = subprocess.run([str(PY), str(ROOT / "assurance" / f"{GREEN_CONTROL}.py")],
                                cwd=str(ROOT), capture_output=True, text=True).returncode
    live_red = subprocess.run([str(PY), str(ROOT / "assurance" / f"{RED_CONTROL}.py")],
                              cwd=str(ROOT), capture_output=True, text=True).returncode
    git("checkout", "-f", "-q", head, cwd=WT)
    git("clean", "-fdq", cwd=WT)
    wt_green = run_gate(WT, GREEN_CONTROL)
    wt_red = run_gate(WT, RED_CONTROL)
    g_ok = (live_green == 0 and wt_green == 0)
    r_ok = (live_red != 0 and wt_red != 0 and wt_red != ABSENT)
    print("  CONTROLS on the harness, run before any history is touched")
    print(f"    HARNESS (+)  `{GREEN_CONTROL}` is {live_green} live and {wt_green} through the "
          f"worktree at the same commit  {'PASS' if g_ok else 'FAIL'}")
    print(f"    HARNESS (-)  `{RED_CONTROL}` is {live_red} live and {wt_red} through the "
          f"worktree  {'PASS' if r_ok else 'FAIL'}")
    if not (g_ok and r_ok):
        print("\n  UNVERIFIED — the harness cannot reproduce HEAD's own status, so every red it")
        print("  reports below would be its own artifact. Nothing is measured. Exit 1.")
        return 1

    # ---- the ladder ---------------------------------------------------------------------------
    rungs = []
    for n in RUNGS:
        r = git("rev-parse", f"HEAD~{n}") if n else git("rev-parse", "HEAD")
        if r.returncode != 0:
            continue
        sha = r.stdout.strip()
        d = git("log", "-1", "--format=%ad", "--date=short", sha).stdout.strip()
        rungs.append((n, sha, d))
    if not rungs:
        print("  UNRUNNABLE: the ladder is empty. Exit 2, never 0."); return 2

    print(f"\n  LADDER — {len(rungs)} rungs over {RUNGS[-1]} commits, all 11 gates at each "
          f"({len(rungs)*len(GATES)} cells)")
    print(f"    {'back':>6}{'commit':>10}{'date':>12}   " + "".join(f"{g[:4]:>6}" for g in GATES))
    HIST = {}
    for n, sha, d in rungs:
        git("checkout", "-f", "-q", sha, cwd=WT)
        git("clean", "-fdq", cwd=WT)
        row = {}
        for g in GATES:
            row[g] = run_gate(WT, g)
        HIST[str(n)] = dict(commit=sha[:12], date=d, results=row)
        cells = "".join(f"{('—' if row[g]==ABSENT else str(row[g])):>6}" for g in GATES)
        print(f"    {n:>6}{sha[:9]:>10}{d:>12}   {cells}", flush=True)
    git("checkout", "-f", "-q", head, cwd=WT)

    print(f"\n    columns, in order: " + " · ".join(GATES))
    print(f"    `—` = the gate did not exist at that commit. ABSENT is NOT green.")

    # ---- classification -------------------------------------------------------------------
    print(f"\n  PER GATE — the most recent rung at which it exited 0")
    print(f"    {'gate':>38}{'born':>12}{'green rungs':>13}   verdict")
    CLASS, ever = {}, 0
    for g in GATES:
        greens = [n for n in sorted((int(k) for k in HIST), reverse=True)
                  if HIST[str(n)]["results"][g] == 0]
        reds = [n for n in sorted((int(k) for k in HIST), reverse=True)
                if HIST[str(n)]["results"][g] not in (0, ABSENT)]
        present = [n for n in sorted((int(k) for k in HIST))
                   if HIST[str(n)]["results"][g] != ABSENT]
        if greens:
            ever += 1
            newest = min(greens)          # fewest commits back = most recent
            older_red = [n for n in reds if n > newest]
            verdict = (f"REGRESSED between HEAD~{newest} and HEAD~"
                       f"{max([r for r in reds if r < newest], default=0)}"
                       if [r for r in reds if r < newest] else "green at some rung")
            if older_red:
                verdict += " (and red further back too)"
        else:
            verdict = ("BORN RED — no rung since birth exits 0"
                       if present else "NEVER EVALUABLE at any rung")
        CLASS[g] = dict(born=birth[g][1], born_commit=birth[g][0], greens=greens, reds=reds,
                        n_present=len(present), verdict=verdict)
        print(f"    {g:>38}{str(birth[g][1]):>12}{len(greens):>13}   {verdict}")

    # ---- VERDICT -------------------------------------------------------------------------
    print()
    if ever == 0:
        print(f"  W-BORN-RED — NOT ONE of the {len(GATES)} gates exits 0 at any rung back to")
        print(f"  HEAD~{RUNGS[-1]}. They were never brakes. A gate that has never passed is a claim")
        print(f"  about the corpus that the corpus never made, and the action is per gate: satisfy")
        print(f"  it or retire it. There is no regression to find because there was no green state.")
        v = "W_BORN_RED"
    elif ever == len(GATES):
        print(f"  W-REGRESSED — all {len(GATES)} gates were green at some rung and are red now.")
        print(f"  Each has a findable breaking commit and the action is to bisect and fix.")
        v = "W_REGRESSED"
    else:
        print(f"  W-MIXED — {ever} of {len(GATES)} gates were green at some sampled rung; "
              f"{len(GATES)-ever} never were.")
        print(f"  ⛔ So `the campaign has no working brake` is TOO COARSE and is withdrawn as")
        print(f"     written. The two halves need different actions: the never-green ones are")
        print(f"     unsatisfied claims to satisfy or retire; the regressed ones are real breaks")
        print(f"     with a findable commit.")
        v = "W_MIXED"

    print(f"\n  ⚠ EVERY `never green` IS BOUNDED BY ITS OWN BIRTH COMMIT, not by the ladder. A gate")
    print(f"    committed after HEAD~{RUNGS[-1]} simply cannot be measured further back, and the")
    print(f"    birth column above is what bounds it.")
    print(f"  ⚠ AND THIS ROUND MEASURED **WHEN**, NEVER **WHY**. No sentence here diagnoses a")
    print(f"    single gate. R373's hypothesis — that most are stale registrations — is neither")
    print(f"    confirmed nor refuted by a temporal measurement, and is left open.")

    art = dict(stamp(str(SELF)), head=head, rungs=[dict(back=n, commit=s[:12], date=d)
                                                   for n, s, d in rungs],
               history=HIST, classification=CLASS, n_gates=len(GATES), n_ever_green=ever,
               controls=dict(harness_green=g_ok, harness_red=r_ok,
                             live_green=live_green, wt_green=wt_green,
                             live_red=live_red, wt_red=wt_red),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r374_gate_history.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
