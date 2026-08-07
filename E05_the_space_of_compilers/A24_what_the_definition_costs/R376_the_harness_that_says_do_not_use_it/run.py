"""R376 — the isolation harness fails its own selftest. Is it leaking, or is the criterion wrong?

R375's NEXT was to classify what four commits DID. Reaching for the instrument that answers it --
`assurance/what_did_each_check_actually_read.py`, which records every file a check opens via a
CPython audit hook -- surfaced something larger: it is built on `assurance/_isolated.py`, and
`_isolated.py` fails its OWN selftest and prints, in its own words, **"FAIL — do not use this
harness"**. It is also one of the five gates R374 found BORN RED.

So the read-set measurement R375 asked for cannot be trusted until this is settled, and settling it
is worth more: it decides whether a whole instrument family is admissible.

⛔ THE FAILING LINE, QUOTED FROM ITS OWN OUTPUT:
     g=0 (harmless subject)  : exit 0, dirtied 2 path(s)   ⚠ fires with nothing planted
   The criterion is `len(changed0) <= 1`. Two paths were dirtied by a subject whose entire body is
   `print('noop')`.

⛔ AND THIS CAMPAIGN'S OWN LEDGER SAYS WHICH WAY TO BET, WHICH IS EXACTLY WHY IT MUST BE MEASURED.
   `realstat §4 · the control fails for its own reasons` was measured at 4 of 7 mis-specified
   controls in one day -- the DOMINANT mode -- and exactly 1 of the 7 failed in the flattering
   direction. Betting on the base rate would give `the criterion is wrong` before any evidence.
   That is a prior, not a measurement, and a prior that happens to excuse my own harness is the one
   I should trust least. Both worlds are built and the paths are read.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. The dirtied paths
   are free to be tracked corpus files (a genuine leak) or the probe's own untracked scaffolding
   (a criterion counting itself). Nothing in the design forces either, and the discriminator --
   `git ls-files --error-unmatch` on each path -- is a fact about the repository, not a judgement.

ESTIMAND        (a) the IDENTITY of every path the g=0 (harmless) subject dirties, and for each,
                    whether git TRACKS it;
                (b) the same for the saboteur subject, whose behaviour is known independently;
                (c) whether the harness's containment claim -- the MAIN tree survives -- holds,
                    measured separately from the criterion that is failing.

IDENTIFICATION  Exact. `git status --porcelain` and `git ls-files` are enumerations, not samples.
                NOT identified: whether some OTHER subject leaks. This measures the two subjects the
                selftest itself runs; a claim about all subjects would need all subjects.

SCOPE           population: the g=0 probe and the saboteur probe as `_isolated.selftest` defines
                them · instrument: git status/ls-files plus the harness's own `run_isolated` ·
                baseline: a tracked path dirtied is contamination, an untracked probe file is not ·
                regime: this worktree, this commit.

WORLDS
  W-CRITERION-MALFORMED  every g=0 dirtied path is the harness's OWN scaffolding or process
                         residue, and NONE is tracked content. The harness isolates; the criterion
                         counts itself and has been failing for that. Action: fix the criterion,
                         and prove the fix does not disarm it.
  W-LEAK                 at least one g=0 dirtied path is TRACKED content the harness claims to
                         protect. Isolation genuinely fails, every read-set number built on it is
                         void, and R375's NEXT cannot be answered with this instrument at all.
  W-CONTAINMENT-BROKEN   the MAIN tree does not survive the saboteur. Then the harness is dangerous
                         rather than merely mis-scored, and nothing else matters.

PREDICTION MATRIX
  W-CRITERION-MALFORMED -> g0_tracked == 0 ; main tree safe ; saboteur dirties tracked content
  W-LEAK                -> g0_tracked  > 0 ; main tree safe
  W-CONTAINMENT-BROKEN  -> main tree epochs change

PRE-REGISTERED KILL -- conditional on the controls, never on a count alone.
    if saboteur_ran and classifier_positive_control_ok:
        if main tree changed                 -> W-CONTAINMENT-BROKEN
        elif g0_tracked > 0                  -> W-LEAK
        elif g0_tracked == 0                 -> W-CRITERION-MALFORMED, and the repair must then
                                                 be shown NOT to disarm the control
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  CLASSIFIER (+)  the saboteur deletes an epoch directory, so its dirtied set MUST contain tracked
                  content. If the tracked/untracked classifier cannot see that, it is blind and
                  every zero it reports is silence. Known independently of this round.
  CLASSIFIER (-)  a path that is definitely untracked (the probe file this round writes) must
                  classify as untracked. Both directions, because a classifier that calls
                  everything tracked would also "pass" the positive control.
  SABOTEUR RAN    an `rc` that is not an int means the subject never executed, and a main tree that
                  survives an attack THAT NEVER HAPPENED is the empty-population pass one level up.
                  Checked explicitly, as `_isolated` itself learned to do.
  REPAIR NOT DISARMED  if the verdict is W-CRITERION-MALFORMED, the repaired criterion is run
                  against the SABOTEUR and must still FIRE. A criterion that no longer fails is
                  not a fixed control, it is a deleted one.

MULTIPLICITY    no test family, no threshold. Every dirtied path is listed with its git status.
SEEDS           none -- nothing here is random.
ARTIFACT        results/r376_isolation.json with the source hash.

IMPOSSIBLE HERE
  whether OTHER subjects leak    -- needs all subjects; this measures the two the selftest defines.
  what the four R375 commits did -- deliberately deferred: that question depends on this answer,
                                    and answering it first would be building on an untrusted
                                    instrument.
  a second release               -- one release.

EXIT
    0  controls hold and the harness is classified
    1  a control misbehaved -- UNVERIFIED
    2  the worktree or harness is unusable -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys
import textwrap

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
sys.path.insert(0, str(ROOT / "assurance"))
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def main() -> int:
    try:
        from _isolated import ensure_worktree, restore, run_isolated   # noqa: E402
    except Exception as e:
        print(f"  UNRUNNABLE: cannot import _isolated ({e}). Exit 2, never 0."); return 2

    def git(*a, cwd=None):
        return subprocess.run(["git", *a], cwd=str(cwd or ROOT), capture_output=True,
                              text=True, timeout=300)

    wt = ensure_worktree()
    print(f"R376 · the harness says do not use it. Leak, or criterion?\n")
    print(f"  worktree {wt}\n")

    def classify(lines):
        """each porcelain line -> (status, path, tracked?). TRACKED is asked of GIT, not guessed."""
        out = []
        for ln in lines:
            st, path = ln[:2].strip(), ln[3:].strip().strip('"').rstrip("/")
            r = git("ls-files", "--error-unmatch", "--", path, cwd=wt)
            out.append(dict(status=st or "??", path=path, tracked=(r.returncode == 0)))
        return out

    # ---- CLASSIFIER controls, before any subject is judged -----------------------------------
    known_tracked = "assurance/_isolated.py"
    probe_rel = "assurance/_r376_probe.py"
    restore(wt)
    (wt / probe_rel).write_text("print('noop')\n")
    c_pos = git("ls-files", "--error-unmatch", "--", known_tracked, cwd=wt).returncode == 0
    c_neg = git("ls-files", "--error-unmatch", "--", probe_rel, cwd=wt).returncode != 0
    print("  CONTROLS")
    print(f"    CLASSIFIER (+)  `{known_tracked}` is tracked: {c_pos}  "
          f"{'PASS' if c_pos else 'FAIL'}")
    print(f"    CLASSIFIER (-)  a freshly written probe is untracked: {c_neg}  "
          f"{'PASS' if c_neg else 'FAIL'}")
    if not (c_pos and c_neg):
        (wt / probe_rel).unlink(missing_ok=True)
        print("\n  UNVERIFIED — the tracked/untracked classifier is blind in one direction. Exit 1.")
        return 1

    # ---- the g=0 arm, reproduced exactly as the selftest runs it -----------------------------
    rc0, _f0, changed0 = run_isolated(probe_rel, restore_first=False)
    (wt / probe_rel).unlink(missing_ok=True)
    g0 = classify(changed0)
    g0_tracked = [r for r in g0 if r["tracked"]]
    print(f"\n  g=0 SUBJECT — body is `print('noop')`.  exit {rc0}, "
          f"{len(changed0)} path(s) dirtied")
    for r in g0:
        print(f"      {r['status']:>3}  {'TRACKED' if r['tracked'] else 'untracked':>9}  "
              f"{r['path']}")
    print(f"    -> tracked content dirtied: {len(g0_tracked)}")

    # ---- the saboteur, the classifier's positive control with a known answer -----------------
    before = sorted(p.name for p in ROOT.glob("E0*") if p.is_dir())
    restore(wt)
    sab_rel = "assurance/_r376_saboteur.py"
    (wt / sab_rel).write_text(textwrap.dedent('''
        import pathlib, shutil
        R = pathlib.Path(__file__).resolve().parents[1]
        for e in sorted(R.glob("E0*")):
            if e.is_dir():
                shutil.rmtree(e); print("deleted", e.name); break
    '''))
    rcs, _fs, changeds = run_isolated(sab_rel, restore_first=False)
    (wt / sab_rel).unlink(missing_ok=True)
    after = sorted(p.name for p in ROOT.glob("E0*") if p.is_dir())
    sab = classify(changeds[:4000])
    sab_tracked = [r for r in sab if r["tracked"]]
    ran = isinstance(rcs, int)
    main_safe = (before == after)
    print(f"\n  SABOTEUR — deletes an epoch directory.  exit {rcs!r}, "
          f"{len(changeds)} path(s) dirtied")
    print(f"    tracked content dirtied: {len(sab_tracked)}  "
          f"(the classifier must see this; it is the positive control)")
    print(f"    MAIN tree epochs before/after: {len(before)} / {len(after)}  "
          f"{'SAFE' if main_safe else '⚠ DAMAGED'}")
    print(f"    the subject actually ran: {ran}  "
          f"(a tree surviving an attack that never happened is not evidence)")
    sab_ok = ran and len(sab_tracked) > 0
    print(f"    CLASSIFIER (+) on a real destructive subject: "
          f"{'PASS' if sab_ok else 'FAIL — blind, every zero above is silence'}")

    restore(wt)
    ctrl_ok = c_pos and c_neg and sab_ok

    # ---- VERDICT ------------------------------------------------------------------------------
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the paths above are silence, not a result.")
        v = "UNVERIFIED"; repaired_fires = None
    elif not main_safe:
        print("  W-CONTAINMENT-BROKEN — the MAIN tree changed while the saboteur ran in the")
        print("  worktree. The harness is dangerous, not merely mis-scored, and nothing else")
        print("  about it matters until that is fixed.")
        v = "W_CONTAINMENT_BROKEN"; repaired_fires = None
    elif g0_tracked:
        print(f"  W-LEAK — the harmless subject dirtied {len(g0_tracked)} TRACKED path(s):")
        for r in g0_tracked:
            print(f"      {r['path']}")
        print("  Isolation genuinely fails. Every read-set number built on this harness is void,")
        print("  and R375's NEXT cannot be answered with this instrument at all.")
        v = "W_LEAK"; repaired_fires = None
    else:
        print(f"  W-CRITERION-MALFORMED — the g=0 subject dirtied {len(changed0)} path(s) and "
              f"NONE is tracked.")
        print(f"  Both are the harness's own scaffolding. The criterion `len(changed) <= 1` counts")
        print(f"  the probe file the selftest itself writes, so it fires on the harness rather than")
        print(f"  on a leak. Containment holds: the main tree is intact and the saboteur really ran.")
        # ⛔ AND A REPAIRED CONTROL MUST STILL BE ABLE TO FAIL. Fixing a criterion by loosening it
        #   until it passes is deleting the control, not repairing it. The repaired rule --
        #   count TRACKED paths dirtied -- is run against the SABOTEUR here and must fire.
        repaired_g0 = len(g0_tracked) == 0
        repaired_fires = len(sab_tracked) > 0
        print(f"\n  REPAIR, and the proof it is not a deletion:")
        print(f"    proposed criterion: `no TRACKED path may be dirtied by the g=0 subject`")
        print(f"      on g=0      : {len(g0_tracked)} tracked -> "
              f"{'PASSES' if repaired_g0 else 'still fails'}")
        print(f"      on saboteur : {len(sab_tracked)} tracked -> "
              f"{'STILL FIRES' if repaired_fires else '⛔ DISARMED — do not apply'}")
        if repaired_g0 and repaired_fires:
            print(f"    -> the repair passes the benign case AND still catches the destructive one,")
            print(f"       which is the only evidence that distinguishes a fix from a deletion.")
            v = "W_CRITERION_MALFORMED_REPAIRABLE"
        else:
            print(f"    -> the repair is NOT applied: it does not separate the two cases.")
            v = "W_CRITERION_MALFORMED_NO_SAFE_REPAIR"

    print(f"\n  ⚠ SCOPE, restated where a summary usually widens it: this measured the TWO subjects")
    print(f"    `_isolated.selftest` defines. It says nothing about whether some other subject")
    print(f"    leaks, and `no leak here` is not `no leak`.")
    print(f"  ⚠ AND R375's QUESTION IS STILL UNANSWERED, deliberately. What the four commits did")
    print(f"    depends on this instrument, and answering it first would have been building on a")
    print(f"    harness that says in its own output not to use it.")

    art = dict(stamp(str(SELF)), g0=dict(exit=rc0, dirtied=g0, tracked=len(g0_tracked)),
               saboteur=dict(exit=str(rcs), n_dirtied=len(changeds),
                             tracked=len(sab_tracked), ran=ran,
                             sample=[r["path"] for r in sab_tracked[:6]]),
               main_tree=dict(before=len(before), after=len(after), safe=main_safe),
               controls=dict(classifier_pos=c_pos, classifier_neg=c_neg, saboteur=sab_ok),
               repaired_criterion_fires_on_saboteur=repaired_fires,
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r376_isolation.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
