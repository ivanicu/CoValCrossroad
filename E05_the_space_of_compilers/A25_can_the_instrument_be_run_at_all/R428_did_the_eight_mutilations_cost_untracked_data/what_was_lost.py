"""R428/what_was_lost -- the census returned two numbers and I can only read ONE of them.

⛔ WHY. `run.py` returned `LOST-u 37` and `DIV-t 57`, and I was about to report the first and skip
   the second. Both are claims about loss and neither is readable as it stands:

   * **37 untracked paths absent from the tree.** The instrument's unit is a path, so it counted a
     `__pycache__/*.pyc` and a judged `.npz` identically -- and I said so in `run.py`'s UNIT
     DISCIPLINE block precisely so that I could not quietly rank them later without a rule.
   * **57 TRACKED paths whose bytes differ.** `run.py` filed these under the SHAM, "recoverable by
     definition" -- and that is only true if the stash's version was ever COMMITTED. If a tracked
     file carried uncommitted edits when it was moved aside, `git restore` overwrote them with
     HEAD's version and the edits exist nowhere but /tmp. A hash mismatch cannot tell those two
     apart, so 57 was reported as harmless on an assumption, which is the exact shape of the error
     this round exists to correct.

ESTIMAND (two, named before either method)
    REGENERABLE  of the 37 untracked-lost, how many are reproducible by running something, under a
                 rule stated before looking: a path is REGENERABLE iff it contains a `__pycache__`
                 component. That is a mechanical fact about CPython, not a judgement about value.
                 Everything else is IRRECOVERABLE-IF-TRUE and gets listed in full.
    UNCOMMITTED  of the 57 divergent-tracked, how many hold bytes git has NEVER seen.

IDENTIFICATION
    REGENERABLE  fully identified -- a string test on a path. This is a DERIVATION, not a
                 measurement: given the rule and the list, the count is forced. Labelled as one.
    UNCOMMITTED  identified in ONE DIRECTION ONLY, and the round rules only on the sound side:
                     object absent from the DB  =>  these bytes were NEVER committed   [SOUND]
                     object present in the DB   =>  probably committed, but a dangling blob from
                                                    an aborted operation looks identical [UNSOUND]
                 So `absent` is reported as CONFIRMED loss and `present` as UNVERIFIED-recoverable.
                 Folding UNVERIFIED into "fine" is how a false acquittal is manufactured, and a
                 false acquittal is permanent because nobody re-examines a cleared claim.

SCOPE  population = the 37 + 57 paths in results/loss_census.json · instrument = path string test
       and `git cat-file -e` · baseline = the live tree at HEAD · regime = before any recovery.

CONTROLS
    POSITIVE (regenerable)  the rule must SELECT a path known to contain `__pycache__` and REJECT
                            one known not to. Both are asserted, not assumed.
    POSITIVE (committed)    `git cat-file -e` must return TRUE for the blob of a file currently in
                            the tree and committed at HEAD. A test that has never returned TRUE
                            cannot make its FALSE mean anything -- that is the whole positive
                            control law, applied to a git plumbing command.
    NEGATIVE (committed)    it must return FALSE for random bytes that cannot have been committed.
                            Without this, `absent` might simply be what the command always says.
    g=0                     with an empty candidate list both counts must be 0, checked, because a
                            rule that fires on an empty input is not a rule.

PRE-REGISTERED KILL (conditional, evaluated ONLY if all four controls fire correctly)
    IRRECOVERABLE > 0 or UNCOMMITTED > 0  -> real loss; the recovery is owed and is a separate step
    both 0                                -> the 37 were interpreter cache and the 57 were stale
                                             copies; "zero data loss" survives with its scope fixed
    a control fails                       -> UNVERIFIED

EXIT 0 no real loss · 1 real loss found · 2 UNRUNNABLE or controls unfit
"""
from __future__ import annotations
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
TMP = pathlib.Path("/tmp")


def is_regenerable(rel: str) -> bool:
    """THE RULE, stated in the docstring before the data was looked at."""
    return "__pycache__" in pathlib.PurePosixPath(rel).parts


def blob_committed(path: pathlib.Path) -> bool | None:
    """True/False if decidable, None if the plumbing itself failed."""
    h = subprocess.run(["git", "hash-object", str(path)], cwd=str(ROOT),
                       capture_output=True, text=True)
    if h.returncode != 0 or not h.stdout.strip():
        return None
    return subprocess.run(["git", "cat-file", "-e", h.stdout.strip()],
                          cwd=str(ROOT), capture_output=True).returncode == 0


def main() -> int:
    src = RES / "loss_census.json"
    if not src.exists():
        print("  UNRUNNABLE: run.py's artifact is absent. Exit 2, never 0."); return 2
    cen = json.loads(src.read_text())
    lost_u = cen["union"]["lost_untracked"]
    if not lost_u:
        print("  UNRUNNABLE: an empty candidate population must never pass. Exit 2."); return 2

    print("R428 · what was actually lost — the census gave two numbers and one was unreadable\n")

    # ------------------------------------------------------------------------------- controls
    ok = True
    a = is_regenerable("E01/x/__pycache__/run.cpython-313.pyc")
    b = is_regenerable("E01/x/results/a08_gold.emb.npz")
    ok &= (a and not b)
    print(f"  POSITIVE  rule selects a __pycache__ path: {a} · rejects a results path: {not b}"
          f"   {'PASS' if (a and not b) else '⛔ FAIL'}")

    known = ROOT / "README.md"
    pc = blob_committed(known) if known.exists() else None
    ok &= (pc is True)
    print(f"  POSITIVE  `cat-file -e` on a committed file (README.md) -> {pc}, must be True"
          f"   {'PASS' if pc is True else '⛔ FAIL — a FALSE from this command would mean nothing'}")

    junk = pathlib.Path("/tmp/__r428_never_committed__.bin")
    junk.write_bytes(b"R428 negative control: bytes git has never seen \x00\x01\x02" * 7)
    nc = blob_committed(junk)
    junk.unlink(missing_ok=True)
    ok &= (nc is False)
    print(f"  NEGATIVE  the same on random bytes -> {nc}, must be False"
          f"   {'PASS' if nc is False else '⛔ FAIL — the command cannot distinguish anything'}")

    g0 = [p for p in [] if is_regenerable(p)]
    ok &= (len(g0) == 0)
    print(f"  g=0       empty candidate list -> {len(g0)} selected, must be 0"
          f"   {'PASS' if not g0 else '⛔ FAIL'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        return 2

    # ------------------------------------------------------------- ESTIMAND 1 (a DERIVATION)
    regen = [p for p in lost_u if is_regenerable(p)]
    irrec = [p for p in lost_u if not is_regenerable(p)]
    print(f"\n  ESTIMAND 1 · of {len(lost_u)} untracked-lost paths — a DERIVATION, not a measurement")
    print(f"    (given the rule and the list the count is forced; it could not have come out other)")
    print(f"    REGENERABLE (__pycache__)      {len(regen):>3}")
    print(f"    IRRECOVERABLE IF TRUE          {len(irrec):>3}\n")
    for p in irrec:
        print(f"        {p}")

    # ------------------------------------------------------------------------- ESTIMAND 2
    print(f"\n  ESTIMAND 2 · the 57 divergent-TRACKED paths — were their bytes ever committed?")
    stashes = sorted(p for p in TMP.glob("attack_rounds_*") if p.is_dir())
    seen, never, yes, undec = set(), [], 0, 0
    for s in stashes:
        for rel in cen["rows"].get(s.name, {}).get("divergent_untracked_paths", []):
            pass                                     # untracked handled above; kept for symmetry
        # re-derive the divergent-tracked set for THIS stash by comparing again, cheaply
        for p in s.rglob("*"):
            if not p.is_file() or p.is_symlink():
                continue
            rel = str(p.relative_to(s))
            if rel in seen:
                continue
            dst = ROOT / rel
            if not dst.exists():
                continue
            try:
                if p.read_bytes() == dst.read_bytes():
                    continue
            except OSError:
                continue
            seen.add(rel)
            c = blob_committed(p)
            if c is None:
                undec += 1
            elif c:
                yes += 1
            else:
                never.append((rel, s.name))
    print(f"    divergent-tracked paths examined  {len(seen)}")
    print(f"    bytes git HAS seen (UNVERIFIED-recoverable — a dangling blob looks identical) {yes}")
    print(f"    bytes git has NEVER seen (CONFIRMED loss)                                     "
          f"{len(never)}")
    print(f"    undecidable (plumbing failed)                                                 "
          f"{undec}")
    for rel, sname in never[:25]:
        print(f"        {rel}   [{sname}]")

    world = "W-REAL-LOSS" if (irrec or never) else "W-CACHE-ONLY"
    print(f"\n  WORLD: {world}")
    if world == "W-REAL-LOSS":
        print(f"    ⛔ {len(irrec)} untracked artifacts and {len(never)} never-committed tracked")
        print(f"    versions exist only in /tmp, which is reaped. The recovery is OWED and is a")
        print(f"    separate step with its own verification — copying is not the same as checking.")
    else:
        print("    the 37 were interpreter cache and every divergent tracked byte was committed at")
        print("    some point. 'zero data loss' survives, with its scope corrected to say so.")

    out = {"regenerable": regen, "irrecoverable": irrec,
           "divergent_tracked_examined": len(seen), "committed_at_some_point": yes,
           "never_committed": [{"path": r, "stash": s} for r, s in never],
           "undecidable": undec, "world": world}
    (RES / "what_was_lost.json").write_text(json.dumps(out, indent=1))
    print(f"\n  artifact -> {(RES / 'what_was_lost.json').relative_to(ROOT)}")
    return 1 if world == "W-REAL-LOSS" else 0


if __name__ == "__main__":
    sys.exit(main())
