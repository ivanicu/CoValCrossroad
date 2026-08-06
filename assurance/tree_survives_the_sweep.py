#!/usr/bin/env python3
"""Did the working tree survive whatever just ran?

⛔ WHY THIS EXISTS. Twice now the round tree has been found with ~2,960 tracked files DELETED —
once mid-sweep (a tree-moving script SIGTERM'd by the harness's 2-minute limit) and once during a
sequence where BOTH named candidates were subsequently KILLED by direct test:

    generate_round_index.py --apply   832 dirs -> 832 dirs, 0 deleted   NOT the cause
    audit_the_auditors.py (to completion and interrupted)  832 -> 832   NOT the cause

So the cause is **UNVERIFIED**, and that is the whole point of this file. A destruction whose
cause cannot be named is a destruction that will recur, and the reason it could not be named is
that nobody was measuring the tree ACROSS the operation -- only noticing afterwards, by which
time every candidate looks equally guilty. **This is the positive control the incident lacked.**

PROXY LEDGER
  PROPERTY    the working tree still holds every round the repository tracks
  PROXY       count of `git ls-files` paths under E*/A*/R* that are MISSING from disk
  IMPLICATION missing -> destroyed is SOUND. present -> intact is NOT: a file can be present and
              corrupted, which this does not test and does not claim to.
  SAFE SIDE   rules only on destruction. Silence here is never a certificate of integrity.

USAGE
  tree_survives_the_sweep.py --stamp     write the census BEFORE the risky operation
  tree_survives_the_sweep.py             compare against it; exit 1 if anything vanished
  Exit 2 if there is no stamp, or if git is unavailable -- an unknown baseline fails CLOSED,
  because "I cannot tell" reported as "fine" is how the first incident went unnoticed for an hour.
"""
import json, pathlib, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
STAMP = ROOT / "assurance" / "results" / "tree_census.json"


def tracked_rounds():
    out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "E01*", "E02*", "E03*",
                          "E04*", "E05*"], capture_output=True, text=True, timeout=120)
    if out.returncode != 0:
        return None
    return sorted(ln for ln in out.stdout.splitlines() if ln)


def census():
    t = tracked_rounds()
    if t is None:
        return None
    missing = [p for p in t if not (ROOT / p).exists()]
    return {"tracked": len(t), "missing": len(missing), "sample": missing[:5]}


def synthetic_controls() -> bool:
    """The instrument must SEE a disappearance and must NOT invent one. Both, or it is silence."""
    d = pathlib.Path(tempfile.mkdtemp())
    (d / "a").write_text("x")
    present = [p for p in ["a", "b"] if (d / p).exists()]
    g0 = present == ["a"]                       # sees 'a', does not hallucinate 'b'
    (d / "a").unlink()
    after = [p for p in ["a", "b"] if (d / p).exists()]
    pos = after == []                           # sees the disappearance it was built for
    print(f"  POSITIVE CONTROL  a file that vanishes is detected: {pos}  "
          f"{'PASS' if pos else 'FAIL'}")
    print(f"  g=0               a file that never existed is NOT reported as vanished: {g0}  "
          f"{'PASS' if g0 else 'FAIL'}")
    print("    Both arms are required: an instrument that answers 'destroyed' to everything")
    print("    would pass the first arm alone, and that is the control this suite keeps rebuilding.")
    return pos and g0


def main() -> int:
    if not synthetic_controls():
        print("\n  UNVERIFIED: the detector failed its own controls. Exit 2, never 0.")
        return 2

    c = census()
    if c is None:
        print("\n  UNRUNNABLE: git could not list tracked files. An unknown baseline fails CLOSED —")
        print("  reporting 'fine' when the baseline is unknown is how the first incident went")
        print("  unnoticed for an hour. Exit 2.")
        return 2

    if "--stamp" in sys.argv:
        STAMP.parent.mkdir(parents=True, exist_ok=True)
        STAMP.write_text(json.dumps(c, indent=2))
        print(f"\n  stamped: {c['tracked']} tracked round files, {c['missing']} missing now")
        return 0

    if not STAMP.exists():
        print("\n  UNRUNNABLE: no stamp to compare against. Run --stamp BEFORE the risky")
        print("  operation. A comparison with no baseline is not a measurement. Exit 2.")
        return 2

    was = json.loads(STAMP.read_text())
    lost = c["missing"] - was["missing"]
    print(f"\n  tracked round files: {was['tracked']} at stamp -> {c['tracked']} now")
    print(f"  missing from disk  : {was['missing']} at stamp -> {c['missing']} now  (Δ {lost:+d})")
    if c["missing"] > was["missing"]:
        print(f"\n  FAIL: {lost} tracked round file(s) VANISHED since the stamp. Examples:")
        for p in c["sample"]:
            print(f"    {p}")
        print("  Recover with `git restore --staged --worktree .` — this has been needed twice,")
        print("  and both times the cause was named confidently and both names were later killed")
        print("  by direct test. Record what ran between the stamp and now BEFORE restoring.")
        return 1
    print("\n  PASS: nothing tracked vanished. ⚠ This rules on DESTRUCTION only — a file can be")
    print("  present and corrupted, which this does not test and does not claim to.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
