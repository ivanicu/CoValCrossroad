#!/usr/bin/env python3
"""assurance/audit_the_auditors.py — do the checks in this directory still SEE anything?

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


def snap(d: pathlib.Path):
    return {p: p.read_bytes() for p in d.rglob("*") if p.is_file() and "__pycache__" not in str(p)}


def restore(s, d: pathlib.Path):
    changed = []
    for p in list(d.rglob("*")):
        if p.is_file() and "__pycache__" not in str(p) and p not in s:
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
        touched = restore(before, HERE)
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
