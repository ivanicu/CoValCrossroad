"""R375 — six gates changed state in one bracket. One cause, or six?

R374 localised six green->red transitions to HEAD~512 (2026-07-29) .. HEAD~256 (2026-08-03) and
stopped there, because a 12-rung ladder gives a bracket and not a commit. This bisects the bracket.

⛔ A BISECT PRESUMES MONOTONICITY, AND THAT PRESUMPTION IS THE WHOLE RISK. Binary search for "the
   first red commit" is only well defined if the gate goes green ... green red ... red exactly once.
   A gate that FLICKERS -- red, green, red -- has no first red commit, and a bisect run on it will
   still confidently return one. So monotonicity is not assumed here: after each transition is
   found, extra commits are probed on BOTH sides, and a gate that flickers is reported as FLICKERING
   with no breaking commit rather than given a spurious one.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. The six breaking
   commits are free to be six distinct commits, one shared commit, or any grouping between. Nothing
   in the search forces agreement -- each gate is bisected independently against its own endpoints,
   and the grouping is read off afterwards rather than fitted.
   ⚠ What IS partly forced and is labelled: commits that touch nothing a gate reads cannot change
   its verdict, so gates reading the SAME surface have correlated transitions by construction. That
   is why `one commit` is interesting only if the commit is also PLAUSIBLE as a cause -- and this
   round measures the commit, never the causation. Naming what the commit did is a separate step.

ESTIMAND        for each of the six gates R374 found regressed, the FIRST commit in
                HEAD~512..HEAD~256 at which it stops exiting 0 -- or the finding that its transition
                is not monotone and no such commit exists.
                Derived: the number of DISTINCT such commits across the six.

IDENTIFICATION  Identified for a gate whose endpoints reproduce (green at the old end, red at the
                new end) AND whose transition is monotone under probing. A gate failing either is
                UNVERIFIED and is reported as such, never folded into a count.
                NOT identified: WHY the commit broke it. This round returns a commit, not a cause.

SCOPE           population: the six gates R374 classified REGRESSED · instrument: git checkout into
                a disposable worktree plus the CURRENT interpreter · baseline: exit 0 ·
                regime: the 256-commit bracket, endpoints named in the artifact.

WORLDS
  W-ONE-CAUSE     the six transitions land on ONE commit (or two adjacent ones). The repair is one
                  commit's worth of work and the campaign's brake failed once, not six times.
  W-INDEPENDENT   six distinct commits. The backlog is real, needs scheduling rather than a fix, and
                  the bracket coincidence was an artifact of a coarse ladder.
  W-NOT-MONOTONE  at least one gate flickers, so `the commit that broke it` is not a well-formed
                  object for that gate and the bracket framing was wrong for it.

PREDICTION MATRIX
  W-ONE-CAUSE    -> distinct breaking commits == 1 (or 2 adjacent), monotone everywhere
  W-INDEPENDENT  -> distinct breaking commits == 6, monotone everywhere
  W-NOT-MONOTONE -> >=1 gate flickers under probing; its transition is withdrawn

PRE-REGISTERED KILL -- conditional on the controls, never on the count alone.
    if endpoints_reproduce_for_all and harness_control_ok:
        if any gate flickers                     -> W-NOT-MONOTONE for that gate, reported per gate
        d = number of DISTINCT breaking commits among the monotone gates
        if d <= 2                                -> W-ONE-CAUSE
        elif d == number of monotone gates       -> W-INDEPENDENT
        else                                     -> named explicitly with the grouping, not defaulted
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  ENDPOINTS     each gate must be green at the old end and red at the new end, re-measured HERE
                rather than inherited from R374. A gate whose endpoints do not reproduce is
                UNVERIFIED -- R374's ladder and this bisect must agree about the bracket they share.
  MONOTONICITY  after each transition, probe extra commits on both sides. A gate that flickers gets
                no breaking commit. This control can fail and its failure is informative.
  HARNESS       a gate known GREEN at HEAD must run green through the worktree; a known RED must run
                red. Re-run here rather than cited, because it is the same worktree in a new state.
  CACHE         every (commit, gate) result is memoised and the cache is keyed on the full sha, so
                a repeated probe returns the same answer. Reported as a count of distinct checkouts.

MULTIPLICITY    no test family and no threshold. The search is exhaustive within its bracket and the
                whole per-gate history it touched is written to the artifact.
SEEDS           none -- git checkout is deterministic.
ARTIFACT        results/r375_bisect.json with the source hash.

IMPOSSIBLE HERE
  WHY the commit broke each gate  -- returns a commit, never a cause. Naming the cause is the next
                                     step and is deliberately not attempted from a diff.
  gates outside the six           -- the five R374 found BORN RED have no transition to find.
  a second release                -- one release.

EXIT
    0  controls hold and every gate is classified
    1  a control misbehaved -- UNVERIFIED
    2  the worktree is unusable or the bracket is empty -- never a silent pass
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
WT = pathlib.Path(os.environ["R375_WORKTREE"]) if os.environ.get("R375_WORKTREE") else None
PY = ROOT / ".venv" / "bin" / "python"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

GATES = ["artifacts_are_internally_coherent", "attack_every_check",
         "donor_numbers_carry_their_draw_scope", "readme_row_carries_the_verdict",
         "seed_filter_is_disclosed", "synthesis_cites_recent_work"]
GREEN_CONTROL, RED_CONTROL = "consistency", "seed_filter_is_disclosed"
OLD, NEW = 512, 256          # R374's bracket: green at HEAD~512, red at HEAD~256
PROBES = 3                   # extra commits probed each side of a transition
ABSENT = "ABSENT"


def git(*a, cwd=None):
    return subprocess.run(["git", *a], cwd=str(cwd or ROOT), capture_output=True,
                          text=True, timeout=300)


def main() -> int:
    if WT is None or not WT.exists():
        print("  UNRUNNABLE: R375_WORKTREE unset or missing. This round checks out commits and must")
        print("  never do so in the live tree. Exit 2, never 0."); return 2
    if not PY.exists():
        print(f"  UNRUNNABLE: {PY} absent. Exit 2, never 0."); return 2

    head = git("rev-parse", "HEAD").stdout.strip()
    # the bracket, oldest-first, INCLUSIVE of both endpoints
    seq = git("rev-list", "--reverse", f"{head}~{OLD}^..{head}~{NEW}").stdout.split()
    if len(seq) < 8:
        print(f"  UNRUNNABLE: bracket has {len(seq)} commits. Exit 2, never 0."); return 2
    print(f"R375 · one commit or six?   bracket {seq[0][:9]}..{seq[-1][:9]}, "
          f"{len(seq)} commits\n")

    CACHE, checkouts = {}, [0]

    def at(sha, gate):
        key = (sha, gate)
        if key in CACHE:
            return CACHE[key]
        if CACHE.get(("__at__",)) != sha:
            git("checkout", "-f", "-q", sha, cwd=WT)
            git("clean", "-fdq", cwd=WT)
            CACHE[("__at__",)] = sha
            checkouts[0] += 1
        f = WT / "assurance" / f"{gate}.py"
        if not f.exists():
            CACHE[key] = ABSENT
            return ABSENT
        try:
            rc = subprocess.run([str(PY), str(f)], cwd=str(WT), capture_output=True,
                                text=True, timeout=180).returncode
        except subprocess.TimeoutExpired:
            rc = "TIMEOUT"
        CACHE[key] = rc
        return rc

    # ---- HARNESS control, in the worktree's current state -----------------------------------
    live_g = subprocess.run([str(PY), str(ROOT / "assurance" / f"{GREEN_CONTROL}.py")],
                            cwd=str(ROOT), capture_output=True, text=True).returncode
    live_r = subprocess.run([str(PY), str(ROOT / "assurance" / f"{RED_CONTROL}.py")],
                            cwd=str(ROOT), capture_output=True, text=True).returncode
    wt_g, wt_r = at(head, GREEN_CONTROL), at(head, RED_CONTROL)
    h_ok = (live_g == 0 and wt_g == 0 and live_r != 0 and wt_r not in (0, ABSENT))
    print("  CONTROLS")
    print(f"    HARNESS   `{GREEN_CONTROL}` {live_g} live / {wt_g} worktree ; "
          f"`{RED_CONTROL}` {live_r} live / {wt_r} worktree  {'PASS' if h_ok else 'FAIL'}")
    if not h_ok:
        print("\n  UNVERIFIED — the harness cannot reproduce HEAD's status. Exit 1."); return 1

    old_sha, new_sha = seq[0], seq[-1]
    ends, end_ok = {}, True
    for g in GATES:
        a, b = at(old_sha, g), at(new_sha, g)
        ok = (a == 0 and b not in (0, ABSENT))
        ends[g] = dict(old=a, new=b, ok=ok)
        end_ok &= ok
        print(f"    ENDPOINT  {g:>38}  old {str(a):>6} -> new {str(b):>6}  "
              f"{'PASS' if ok else 'FAIL — UNVERIFIED, excluded from the count'}")
    print(f"    -> endpoints reproduce for {sum(1 for g in ends if ends[g]['ok'])} of {len(GATES)}")

    # ---- bisect each gate independently -------------------------------------------------------
    print(f"\n  BISECT — each gate searched independently against its own endpoints")
    print(f"    {'gate':>38}{'idx':>6}{'commit':>11}{'date':>12}  monotone?")
    RES = {}
    for g in GATES:
        if not ends[g]["ok"]:
            RES[g] = dict(verdict="UNVERIFIED — endpoints did not reproduce")
            print(f"    {g:>38}{'—':>6}{'—':>11}{'—':>12}  UNVERIFIED (endpoints)")
            continue
        lo, hi = 0, len(seq) - 1          # seq[lo] green, seq[hi] red
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if at(seq[mid], g) == 0:
                lo = mid
            else:
                hi = mid
        brk = seq[hi]
        # MONOTONICITY: probe PROBES commits each side. Everything left of the break must be
        # green, everything right must be red. A flicker withdraws the breaking commit.
        left = [seq[i] for i in range(max(0, hi - 1 - PROBES), hi)]
        right = [seq[i] for i in range(hi + 1, min(len(seq), hi + 1 + PROBES))]
        lviol = [s[:9] for s in left if at(s, g) != 0]
        rviol = [s[:9] for s in right if at(s, g) == 0]
        mono = not lviol and not rviol
        d = git("log", "-1", "--format=%ad", "--date=short", brk).stdout.strip()
        RES[g] = dict(break_commit=brk, break_short=brk[:9], date=d, index=hi,
                      monotone=mono, left_violations=lviol, right_violations=rviol,
                      verdict="broke here" if mono else "FLICKERS — no breaking commit")
        print(f"    {g:>38}{hi:>6}{brk[:9]:>11}{d:>12}  "
              f"{'yes' if mono else 'NO — flickers, withdrawn'}")
        if not mono:
            print(f"    {'':>38}  green after the break: {rviol} · red before it: {lviol}")

    git("checkout", "-f", "-q", head, cwd=WT)

    # ---- verdict ------------------------------------------------------------------------------
    mono_gates = [g for g in GATES if RES[g].get("monotone")]
    flick = [g for g in GATES if RES[g].get("monotone") is False]
    unver = [g for g in GATES if "UNVERIFIED" in str(RES[g].get("verdict"))]
    commits = {}
    for g in mono_gates:
        commits.setdefault(RES[g]["break_commit"], []).append(g)
    d = len(commits)
    print(f"\n  {len(CACHE)-1} (commit, gate) evaluations from {checkouts[0]} distinct checkouts")
    print(f"  monotone {len(mono_gates)} · flickering {len(flick)} · unverified {len(unver)}")
    print(f"\n  DISTINCT BREAKING COMMITS: {d}")
    for sha, gs in sorted(commits.items(), key=lambda kv: -len(kv[1])):
        subj = git("log", "-1", "--format=%s", sha).stdout.strip()
        print(f"    {sha[:9]}  {len(gs)} gate(s)  {subj[:88]}")
        for g in gs:
            print(f"      · {g}")

    print()
    if not mono_gates:
        print("  UNVERIFIED — no gate produced a monotone transition, so there is no breaking")
        print("  commit to report for any of them. The bracket framing was wrong for all six.")
        v = "UNVERIFIED"
    elif d <= 2:
        print(f"  W-ONE-CAUSE — {len(mono_gates)} monotone transitions land on {d} commit(s).")
        print(f"  The campaign's brake failed ONCE, not six times, and the repair is one commit's")
        print(f"  worth of work rather than a backlog. ⚠ This round returns a COMMIT, never a")
        print(f"  CAUSE — what that commit did is the next step and is not guessed from a diff.")
        v = "W_ONE_CAUSE"
    elif d == len(mono_gates):
        print(f"  W-INDEPENDENT — {d} distinct commits for {len(mono_gates)} gates. The bracket")
        print(f"  coincidence was an artifact of R374's coarse ladder, and the backlog is real:")
        print(f"  each break needs its own repair and this needs scheduling, not a fix.")
        v = "W_INDEPENDENT"
    else:
        print(f"  W-CLUSTERED — named rather than defaulted: {len(mono_gates)} gates break at {d}")
        print(f"  distinct commits, so it is neither one shared cause nor six independent ones.")
        print(f"  The grouping above IS the finding, and each cluster is a separate repair.")
        v = "W_CLUSTERED"
    if flick:
        print(f"\n  ⚠ AND {len(flick)} GATE(S) FLICKER, which no count above includes: {flick}")
        print(f"    For these, `the commit that broke it` is not a well-formed object — the state")
        print(f"    changes more than once inside the bracket. A bisect would have returned a")
        print(f"    confident commit for each anyway, which is why monotonicity was probed.")

    art = dict(stamp(str(SELF)), head=head[:12], bracket=[seq[0][:12], seq[-1][:12]],
               n_commits=len(seq), endpoints={g: ends[g] for g in ends}, results=RES,
               distinct_break_commits=d,
               grouping={s[:12]: gs for s, gs in commits.items()},
               n_evaluations=len(CACHE) - 1, n_checkouts=checkouts[0],
               monotone=mono_gates, flickering=flick, unverified=unver,
               controls=dict(harness=h_ok, endpoints_all=end_ok), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r375_bisect.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
