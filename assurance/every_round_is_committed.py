#!/usr/bin/env python3
"""Every round directory in the EAR tree must be tracked by git.

⛔ WHY THIS EXISTS. Six times in one session a round was built, run, and REPORTED, and left
uncommitted until the following round noticed. It was logged in RETRACTIONS.md five times as a
process note and never instrumented -- which is precisely the shape of failure every other gate
here was built for. "Reporting is not committing" was true each time and changed nothing, because
a sentence in a ledger is not a check.

PROPERTY : every RNNN_* directory under an ENN/ANN path is committed
PROXY    : `git ls-files` lists at least one file inside it
IMPLICATION: untracked ⇒ uncommitted  (sound). tracked ⇒ fully committed is NOT claimed --
             a tracked directory can still hold unstaged edits, which `git status` covers and
             this does not. Sound in one direction, stated.
SAFE SIDE: flags only directories with NO tracked file at all.
"""
import pathlib, subprocess, sys

def main():
    root = pathlib.Path(__file__).resolve().parent.parent
    tracked = set(subprocess.run(["git", "ls-files"], cwd=root, capture_output=True,
                                 text=True).stdout.splitlines())
    if not tracked:
        print("  git ls-files returned nothing -> UNRUNNABLE"); return 2
    rounds = sorted(p for p in root.glob("E*/A*/R*") if p.is_dir())
    if not rounds:
        print("  no round directories found -> UNRUNNABLE"); return 2

    def has_tracked(d):
        pre = str(d.relative_to(root)) + "/"
        return any(f.startswith(pre) for f in tracked)

    untracked = [d for d in rounds if not has_tracked(d)]
    committed = [d for d in rounds if has_tracked(d)]

    # POSITIVE CONTROL: the instrument must be able to SEE tracked rounds, else "0 untracked"
    # is silence rather than a pass.
    print(f"  POSITIVE CONTROL  rounds with tracked files: {len(committed)} of {len(rounds)} -> "
          f"{'PASS' if committed else 'FAIL -- cannot distinguish tracked from not'}")
    if not committed:
        return 2
    # NEGATIVE CONTROL: an invented path must not appear tracked.
    fake = root / "E00_not_a_thing" / "A00_x" / "R000_y"
    print(f"  NEGATIVE CONTROL  an invented round reads as untracked: {not has_tracked(fake)} -> "
          f"{'PASS' if not has_tracked(fake) else 'FAIL'}")

    print(f"\n  round directories: {len(rounds)}   untracked: {len(untracked)}")
    if untracked:
        print(f"  ⛔ built but never committed -- reporting is not committing:")
        for d in untracked:
            print(f"    {d.relative_to(root)}")
        return 1
    print("  PASS -- every round directory is tracked.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
