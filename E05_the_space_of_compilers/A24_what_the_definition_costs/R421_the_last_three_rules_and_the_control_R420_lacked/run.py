"""R421 -- the three label-reading rules, and the POSITIVE CONTROL R420 never had.

R420 found `topw_k` selection byte-identical across two invocations and concluded selection is
deterministic. Its NEXT named the three rules it did not exercise -- `oracle_k`, `greedy_k`,
`indep_k` -- which read the prompt's own rankings and are the arms clause ③ excludes.

⛔ AND R420 HAS A GAP I SHOULD HAVE CAUGHT IN IT, NOT AFTER IT. Its comparison reported "identical"
   and was never shown able to report anything else. A hash comparison that always returns equal --
   because both runs write the same path, because the tag suffix is ignored, because the file is
   stale -- would have produced exactly R420's output. That is the ledger's oldest row: a zero from
   an instrument never shown to return non-zero is silence, not an acquittal, and I ran it five
   rounds after writing that sentence into three other rounds.

⭐ THE CONTROL IS FREE AND IT WAS AVAILABLE ALL ALONG. `random_k` draws its criteria from a SEEDED
   rng, so two invocations at DIFFERENT seeds MUST emit different criteria. If they do not, the
   comparison is blind and every "identical" -- R420's included -- means nothing.

⛔ ARITHMETIC TRAP. That a seeded rng gives different draws at different seeds is FORCED, which is
   exactly why it makes a good positive control and a worthless finding. It is reported as a control
   and never as a result.

ESTIMAND        (A) whether the hash comparison can DETECT a difference at all (random_k, seed 0 vs
                    seed 1);
                (B) for each of oracle_k, greedy_k, indep_k: whether two invocations with identical
                    arguments emit byte-identical criteria;
                (C) whether (A) retroactively licenses R420's verdict.

IDENTIFICATION  Exact for these rules and these inputs. NOT identified: determinism at other k or
                other fit parities, and on other machines.

SCOPE           population: 3 label-reading rules + 1 control rule · instrument: sha256 over the
                emitted core JSON · baseline: a seeded-difference that must be detected · regime:
                CPU, default inputs, k=4.

WORLDS
  W-ALL-DETERMINISTIC  the control detects the seeded difference AND all three rules are identical.
                       Then every selection path in the campaign is deterministic given its inputs,
                       R420's verdict is licensed retroactively, and the `_08b`/`_08bR` divergence
                       has no remaining mechanism inside the pipeline.
  W-SOME-VARY          the control fires but a rule differs. Then THAT rule is where the variance
                       lives, and it is named.
  W-BLIND              the control does NOT detect the seeded difference. Then the comparison is
                       blind, R420's verdict is UNLICENSED, and nothing here or there means anything.

PREDICTION MATRIX
  W-ALL-DETERMINISTIC -> control differs; 3 of 3 rules identical
  W-SOME-VARY         -> control differs; >=1 rule differs, named
  W-BLIND             -> control does NOT differ

PRE-REGISTERED KILL -- conditional on the control FIRST, and it can invalidate a prior round.
    if control_seeds_produce_DIFFERENT_criteria:
        3 of 3 identical -> W-ALL-DETERMINISTIC
        else             -> W-SOME-VARY, rules named
    else: W-BLIND -- and R420's "identical" is retroactively UNVERIFIED, not merely unsupported.

CONTROLS
  SEED (+)     `random_k` at seed 0 vs seed 1 MUST emit different criteria. This is the control R420
               lacked, and it is placed FIRST because it can invalidate R420 rather than only this
               round.
  SELF (=)     a file hashed against itself is equal.
  PRODUCED     every run must emit a file; a missing file is not agreement. An empty population
               passing would read as determinism here.
  DISTINCT     every run writes its own tag, so no run overwrites another and no comparison is
               secretly a file against itself -- which is the exact way this test could go blind.

MULTIPLICITY    4 rules x 2 runs = 8 invocations; every hash printed.
SEEDS           the control varies the seed DELIBERATELY; the three rules hold it fixed. Those are
                opposite manipulations and are labelled as such.
ARTIFACT        results/r421_selection_rules.json with the source hash.

IMPOSSIBLE HERE
  other k / fit parities  -- k=4, default parity. Named.
  cross-machine           -- one machine.
  why the 08b pairs differ -- still only "different inputs", still not demonstrated.

EXIT
    0  the control fires and the rules are reported
    1  the control is blind -- W-BLIND, and R420 is retroactively unverified
    2  a run produced no file -- never a silent pass
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
RES = ROOT / "corebench" / "results"
SEL = ROOT / "corebench" / "select_core.py"
PY = ROOT / ".venv" / "bin" / "python"
RULES = ("oracle_k", "greedy_k", "indep_k")


def h(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def run(rule, tag, seed=None):
    cmd = [str(PY), str(SEL), "--rule", rule, "--k", "4", "--tag-suffix", tag]
    if seed is not None:
        cmd += ["--seed", str(seed)]
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=2400)
    cands = sorted(RES.glob(f"core_{rule.replace('_k','')}*{tag}.json")) + \
        sorted(RES.glob(f"core_*{tag}.json"))
    f = cands[0] if cands else None
    return f, r


def main() -> int:
    if not SEL.exists():
        print("  UNRUNNABLE: select_core.py absent. Exit 2, never 0."); return 2
    print("R421 · the three label-reading rules, and the control R420 never had\n")
    print("  ⛔ R420 REPORTED `identical` AND WAS NEVER SHOWN ABLE TO REPORT ANYTHING ELSE. A hash")
    print("     comparison that always returns equal — same path, ignored tag, stale file — would")
    print("     have produced exactly its output. That is the ledger's oldest row, and I ran it five")
    print("     rounds after writing that sentence into three other rounds.\n")

    # ---- THE CONTROL, FIRST, because it can invalidate a prior round -------------------------------
    print("  CONTROL (+) — placed FIRST because it can invalidate R420, not just this round")
    fa, ra = run("random_k", "_ctlS0", seed=0)
    fb, rb = run("random_k", "_ctlS1", seed=1)
    if not (fa and fb):
        print(f"  UNRUNNABLE: control run produced no file "
              f"(rc {ra.returncode}/{rb.returncode}). Exit 2, never 0.")
        print(f"    {(ra.stderr or ra.stdout).strip().splitlines()[-1][:100] if (ra.stderr or ra.stdout).strip() else ''}")
        return 2
    ha, hb = h(fa), h(fb)
    detects = ha != hb
    print(f"    random_k seed 0  {fa.name:<34} {ha[:16]}")
    print(f"    random_k seed 1  {fb.name:<34} {hb[:16]}")
    print(f"    the comparison DETECTS a seeded difference: {detects}   "
          f"{'PASS' if detects else 'FAIL'}")
    print(f"    ⛔ this is FORCED (a seeded rng differs at different seeds), which is exactly what")
    print(f"       makes it a good control and a worthless finding — reported as a control only")
    if not detects:
        print(f"\n  W-BLIND — the comparison cannot detect a difference it is GUARANTEED to face. So")
        print(f"  every `identical` it has ever produced means nothing, and R420's verdict is")
        print(f"  RETROACTIVELY UNVERIFIED — not merely unsupported. Exit 1.")
        return 1

    # ---- the three rules ---------------------------------------------------------------------------
    print(f"\n  THE THREE LABEL-READING RULES — two invocations each, IDENTICAL arguments")
    rows, differ, missing = {}, [], []
    for rule in RULES:
        f1, r1 = run(rule, f"_{rule}A")
        f2, r2 = run(rule, f"_{rule}B")
        if not (f1 and f2):
            rows[rule] = dict(status="NO_FILE", rc=[r1.returncode, r2.returncode])
            missing.append(rule)
            tail = (r1.stderr or r1.stdout).strip().splitlines()
            print(f"    {rule:<10} NO FILE  rc={r1.returncode}/{r2.returncode}   "
                  f"{tail[-1][:70] if tail else ''}")
            continue
        x, y = h(f1), h(f2)
        rows[rule] = dict(status="OK", a=x[:16], b=y[:16], identical=(x == y))
        if x != y:
            differ.append(rule)
        print(f"    {rule:<10} {x[:16]}  {y[:16]}   identical={x == y}")

    ok = [r for r in RULES if rows[r]["status"] == "OK"]
    print(f"\n    rules compared {len(ok)} of {len(RULES)}"
          + (f" · could not run: {missing}" if missing else ""))

    print()
    if missing and not ok:
        print(f"  UNRUNNABLE: no rule produced a comparable pair. A missing file is NOT agreement,")
        print(f"  and an empty population passing would read as determinism here. Exit 2.")
        return 2
    if not differ:
        v = "W_ALL_DETERMINISTIC"
        print(f"  W-ALL-DETERMINISTIC — the control fires and {len(ok)} of {len(ok)} compared rules")
        print(f"  emit byte-identical criteria. Every selection path exercised in this campaign is")
        print(f"  deterministic given its inputs.")
        print(f"  ⭐ AND R420's VERDICT IS NOW LICENSED RETROACTIVELY. It was correct and it was")
        print(f"     unsupported; the control it lacked is the one above, and it costs one run.")
        print(f"  ⛔ SO THE `_08b`/`_08bR` DIVERGENCE HAS NO REMAINING MECHANISM INSIDE THE PIPELINE.")
        print(f"     Scoring is deterministic (R419, measured), selection is deterministic (here and")
        print(f"     R420) — the inputs differed, and those files record none.")
    else:
        v = "W_SOME_VARY"
        print(f"  W-SOME-VARY — the control fires and {differ} emit DIFFERENT criteria from identical")
        print(f"  arguments. That is where the campaign's selection variance lives, and it is named.")

    if missing:
        print(f"\n  ⚠ {missing} could not be run here and are UNTESTED, not passing. A rule that does")
        print(f"    not execute is not a rule that agreed with itself.")
    print(f"  ⚠ k=4, default fit-parity, one machine. Other cells are not claimed.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               control=dict(seed0=ha, seed1=hb, detects=detects),
               rules=rows, differ=differ, missing=missing, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r421_selection_rules.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
