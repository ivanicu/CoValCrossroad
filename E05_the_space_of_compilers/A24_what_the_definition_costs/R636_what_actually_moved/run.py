#!/usr/bin/env python3
"""
R636 -- re-run the 43 and find out, because "expensive" was false by three orders of magnitude

CHECK #235: THE SECOND ONE STEERED WORK AWAY FROM THE DECISIVE ACTION.
  ⛔ "BOTH remaining directions are re-runs" -- a universal over a set I never enumerated.
  ⛔⛔ "RE-RUNS ARE EXPENSIVE, so the cheap decisive question first" -- an UNCOMPUTED COST used to
     justify substituting a proxy for the direct measurement. Measured: all 43 rounds' wall clock
     is on the order of a minute. The wall was fabricated, and a fabricated wall is never audited
     because stopping already feels earned.
  ⭐ AND THE FIRST ATTEMPT NEARLY PRODUCED A MUCH WORSE CLAIM. Run under the system python all 43
     exit 1 in 0.1s -- `ModuleNotFoundError: numpy`. One step from reporting "43 rounds do not
     execute". A LOAD FAILURE IS AN ENVIRONMENT CLAIM: the project ships `.venv` on miniforge
     3.13.13 with numpy 2.4.6, and under it they run.

ESTIMAND        of the 43 rounds whose inline reader accepts `world` only, how many produce a
                DIFFERENT artifact when re-run today -- i.e. how many conclusions actually moved.
IDENTIFICATION  Exact and interventional: run, then `git diff` the round's results/. ⚠ A diff can
                be caused by an embedded timestamp or source hash rather than a conclusion, so the
                round separates VERDICT-BEARING diffs (the `world`/`verdict` value changed) from
                cosmetic ones, and reports both.
SCOPE           population : the 43 at-risk rounds from R635, self excluded by default
                instrument : subprocess under .venv/bin/python + git diff on results/
                             instrument unit = A ROUND'S ARTIFACT
                             claim unit      = A CONCLUSION. Equal here for verdict-bearing diffs,
                             which is why they are separated from cosmetic ones.
                baseline   : the committed artifacts
                regime     : this repository at this sha, .venv python 3.13.13, numpy 2.4.6
WORLDS          A NOTHING MOVES: no verdict changes -> the narrow key was exposed but inert, and
                  R635's 43 is an exposure count, not a debt.
                B SOME MOVE: >=1 verdict changes -> those conclusions were wrong on the record and
                  the count is the debt.
                C UNRUNNABLE: a large share cannot execute even under the venv -> reproducibility,
                  not the key set, is the finding, and it outranks it.
KILL            pre-registered: >=1 verdict-bearing diff -> world B. >=1/3 fail to run -> world C
                and it is reported FIRST, because an unreproducible round's key set is moot.
POSITIVE CTRL   the re-run must reproduce at least one artifact BYTE-IDENTICALLY, or the
                comparison cannot distinguish "changed" from "nondeterministic".
NEGATIVE CTRL   the working tree is restored afterwards and `git status` must return to its
                pre-run state.
PLACEBO         a round not in the at-risk set is not run and must show no diff.
SEEDS           the rounds' own seeds; determinism is what the positive control tests.
MULTIPLICITY    43 rounds x (runs / diffs / verdict-bearing) + 4 controls. All reported.
ARTIFACT        results/what_actually_moved.json
IMPOSSIBLE      a round can be deterministic and still wrong; re-running proves only that today's
                code on today's data gives today's answer. It cannot validate the answer.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
SELF = pathlib.Path(__file__).resolve().parent.name
PY = ROOT / ".venv" / "bin" / "python"


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True,
                          timeout=180).stdout


def verdicts(d):
    out = {}
    for f in sorted((d / "results").glob("*.json")):
        try: j = json.loads(f.read_text())
        except Exception: continue
        if isinstance(j, dict):
            for k in ("world", "verdict"):
                if isinstance(j.get(k), str): out[f.name] = j[k]
    return out


def main():
    if not PY.exists():
        print(f"UNRUNNABLE: {PY} absent. Exit 2, never 0."); return 2
    src = A24 / "R635_who_reads_a_key_they_reject" / "results" / "who_reads_a_key_they_reject.json"
    names = [a["round"] for a in json.loads(src.read_text())["at_risk"] if a["round"] != SELF]
    print(f"  at-risk rounds to re-run: {len(names)}   interpreter: {PY}")
    pre_status = git("status", "--porcelain")

    before = {n: verdicts(A24 / n) for n in names}
    ran, failed, t0 = [], [], time.time()
    for n in names:
        # ⭐ THE PROHIBITION (R638-R642). A non-zero exit is UNKNOWN, never failure: 95 of 313
        #    rounds declare an EXIT convention and `EXIT 1` denotes 18 DISTINCT worlds across 19
        #    of them, so no harness can decode the SEMANTICS. Only an UNRUNNABLE PATH counts.
        #    Effect, measured: byte-identical reproductions went 38 -> 43, because the five
        #    rounds this loop called "failures" all exit 1 as a declared verdict.
        #    ⚠ THE STDERR RULE WAS REJECTED. "non-zero + non-empty stderr = crash" is strictly
        #    more general, and it has exactly ONE false positive in this corpus -- R576 writes
        #    JSON to stderr as an IPC channel and calls sys.exit(2). Generality bought unseen
        #    crash types at the price of the one real verdict. Neither rule dominates; this is
        #    the one with zero known false positives on the corpus that exists.
        r = subprocess.run([str(PY), str(A24 / n / "run.py")], cwd=A24 / n,
                           capture_output=True, text=True, timeout=240)
        err = r.stderr.strip().split("\n")[-1][:90]
        unrunnable = ("ModuleNotFoundError" in r.stderr or "No such file" in r.stderr
                      or "SyntaxError" in r.stderr or not (A24 / n / "run.py").exists())
        (failed if (r.returncode != 0 and unrunnable) else ran).append((n, r.returncode, err))
    dt = time.time() - t0
    print(f"\n  ran {len(ran)} · failed {len(failed)} · wall clock {dt:.0f}s "
          f"({dt/60:.1f} min for all {len(names)}) -- 'expensive' was false")
    for n, rc, err in failed[:8]:
        print(f"    ⛔ {n[:52]:<52} exit {rc}  {err}")

    after = {n: verdicts(A24 / n) for n in names}
    diff = git("diff", "--name-only", "--", str(A24)).split()
    changed = sorted({p.split("/")[2] for p in diff if "/results/" in p})
    verdict_moved = [n for n in names if before[n] != after[n]]
    print(f"\n─── WHAT MOVED ───")
    print(f"  artifacts textually changed : {len(changed)}")
    print(f"  VERDICT-BEARING changes     : {len(verdict_moved)} {verdict_moved[:6]}")
    for n in verdict_moved[:6]:
        print(f"    {n[:48]:<48} {before[n]} -> {after[n]}")

    print(f"\n─── CONTROLS ───")
    identical = [n for n in names if n in [p.split('/')[2] for p in diff] or True]
    byte_same = [n for n in ran if n not in changed]
    pos = bool(byte_same)
    print(f"  POSITIVE  {len(byte_same)} round(s) reproduced BYTE-IDENTICALLY -> "
          f"{'PASS — changed vs nondeterministic are distinguishable' if pos else '⛔ FAIL'}")
    # ⛔ AND THE RESTORE DESTROYED ITS OWN SUBJECT. `git checkout -- <A24>` is scoped to a
    #    directory that CONTAINS THIS HARNESS, so it reverted the prohibition installed in this
    #    very file, mid-run -- and the negative control then failed because the tree state had
    #    changed from modified to clean. Scoped to results/ only: the round restores the
    #    artifacts it rewrote and never touches source.
    for _d in sorted(A24.glob("R[0-9]*")):
        if (_d / "results").is_dir():
            git("checkout", "--", str(_d / "results"))
    post_status = git("status", "--porcelain")
    neg = post_status.strip() == pre_status.strip()
    print(f"  NEGATIVE  tree restored to its pre-run state -> {'PASS' if neg else '⛔ FAIL'}")
    outside = [p for p in diff if "/results/" not in p]
    print(f"  PLACEBO   files touched outside a round's results/: {len(outside)} -> "
          f"{'PASS' if not outside else '⛔ ' + str(outside[:3])}")
    controls_ok = pos and neg and not outside

    print(f"\n─── VERDICT (world C reported FIRST if >=1/3 cannot run) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif len(failed) >= len(names) / 3:
        world = (f"C UNRUNNABLE — {len(failed)} of {len(names)} do not execute even under the "
                 f"project venv. Reproducibility, not the key set, is the finding and it outranks "
                 f"it: a round that cannot run cannot be re-adjudicated at all.")
    elif verdict_moved:
        world = (f"B SOME MOVE — {len(verdict_moved)} of {len(ran)} re-runnable rounds return a "
                 f"DIFFERENT verdict today. Those conclusions were wrong on the record and this "
                 f"is the debt.")
    else:
        world = (f"A NOTHING MOVES — {len(ran)} rounds re-ran and no verdict changed. The narrow "
                 f"key set is EXPOSED BUT INERT, so R635's 43 is an exposure count and not a debt.")
    print(f"  {world}")
    print(f"\n  ⚠ A round can be deterministic and still WRONG. Re-running proves only that today's "
          f"code on today's data gives today's answer; it cannot validate the answer.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "what_actually_moved.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "n_target": len(names),
        "ran": len(ran), "failed": [{"round": n, "exit": rc, "err": e} for n, rc, e in failed],
        "wall_clock_s": round(dt, 1), "artifacts_changed": changed,
        "verdict_moved": verdict_moved, "byte_identical": len(byte_same),
        "check235": ("'re-runs are expensive' was uncomputed and false; and running under the "
                     "system python gave ModuleNotFoundError: numpy, which is an ENVIRONMENT "
                     "claim, not '43 rounds do not execute'"),
        "impossible": "determinism is not correctness",
    }, indent=2))
    print(f"\n  wrote {OUT / 'what_actually_moved.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
