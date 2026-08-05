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

    # ⛔ R550: tracking is not CURRENCY. 116 of 542 rounds (21.4%) were amended after their
    # first commit, so "has a tracked file" cannot certify a directory is up to date. The
    # hazard is measured; the blind spot's historical occupancy is NOT -- git history cannot
    # observe an uncommitted state, so that question is structurally unanswerable and this
    # check closes the hazard prospectively rather than diagnosing the past.
    porc = subprocess.run(["git", "status", "--porcelain"], cwd=root,
                          capture_output=True, text=True).stdout.splitlines()
    relr = {str(d.relative_to(root)) for d in rounds}
    # ⛔ FALSE POSITIVE, caught by this gate blocking a healthy commit one round after it
    # shipped. Porcelain column 0 is the INDEX, column 1 is the WORKTREE. 'A ' means STAGED,
    # which at commit time is the CORRECT state -- flagging it fires on the healthy world.
    # Only an unstaged WORKTREE change (column 1 non-blank) is the failure this gate names.
    dirty = [l for l in porc if not l.startswith("??") and l[1] != " "
             and any(l[3:].strip().startswith(r + "/") for r in relr)]

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

    # POSITIVE CONTROL for the dirty check: the `??` prefix must be EXCLUDED, else an
    # untracked new round reads as a modified one -- the exact defect R550 made by hand.
    # The control must span EVERY porcelain category, not the two I happened to think of.
    # Its first version tested ' M' and '??' only, passed, and the gate still fired on 'A '.
    r0 = next(iter(relr))
    cases = {" M": True, "MM": True, "??": False, "A ": False, "M ": False, "R ": False}
    got = {c: (not f"{c} {r0}/x".startswith("??") and c[1] != " ") for c in cases}
    ok = got == cases
    print(f"  POSITIVE CONTROL  dirty filter over ALL 6 porcelain categories "
          f"(staged must NOT flag): {ok} -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        print(f"    expected {cases}\n    got      {got}")
        return 2

    print(f"\n  round directories: {len(rounds)}   untracked: {len(untracked)}   "
          f"tracked-but-dirty: {len(dirty)}")
    if dirty:
        print("  ⛔ a committed round was modified and not re-committed -- tracking is not currency:")
        for l in dirty:
            print(f"    {l}")
        return 1
    if untracked:
        print(f"  ⛔ built but never committed -- reporting is not committing:")
        for d in untracked:
            print(f"    {d.relative_to(root)}")
        return 1
    print("  PASS -- every round directory is tracked.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
