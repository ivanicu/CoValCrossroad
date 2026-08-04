"""R428/recover -- put back what the eight mutilations took, and PROVE each file arrived.

⛔ COPYING IS NOT RECOVERING. `shutil.copy2` returning without an exception says the call did not
   raise; it says nothing about whether the bytes on the far side are the bytes that left. Every
   file here is verified by sha256 AFTER the write, and the count of verified files is the only
   number this script is allowed to report. A recovery that reports what it ATTEMPTED is the same
   shape as a gate that reports success having examined nothing.

TWO POPULATIONS, TWO DIFFERENT ACTIONS, AND THE DIFFERENCE IS THE WHOLE DESIGN

  A · ABSENT from the tree (23 untracked, minus the exclusions below)
      -> COPY IN. Strictly additive: there is nothing at the destination, so no version of
         anything can be destroyed by this. Risk-free in the only direction that matters.

  B · PRESENT in the tree but with DIFFERENT, never-committed bytes (3 paths, all R389)
      -> NEVER OVERWRITE. The tree's R389 README is titled "...and my tooling deleted the round"
         and its artifact carries `"destroyed_and_rewritten": true`, so the TREE holds the REWRITE
         and the STASH holds the PRE-DELETION ORIGINAL. Overwriting would destroy the current
         documented round to restore its ancestor -- the exact inversion this campaign keeps
         making. They go to `_archive/pre_deletion_original/` instead: annotate, never rewrite;
         `mv`, never `rm`.

EXCLUSIONS, NAMED RATHER THAN SILENT
  * `__pycache__/**` (14 paths) -- regenerable by CPython. Restoring interpreter cache would
    inflate the recovered count with files that cost nothing to lose, and this round already
    ruled that a count which cannot rank importance must not smuggle importance in through what
    it chooses to copy.
  * `E99_fixtures/**` -- a GATE'S OWN SCRATCH. `attack_every_check` plants and removes it; a
    pre-existing fixture changes what the next gate run sees. Restoring it would make this
    recovery an intervention on an instrument, which is a different act than recovering data and
    must not be done under the same verdict.

CONTROLS
  POSITIVE   before copying anything, a canary file is written to a temp dir and verified through
             the SAME verify() the real files use. If verify() cannot confirm a file that is
             provably correct, every PASS it prints afterwards is meaningless.
  NEGATIVE   verify() is then run against a deliberately corrupted copy and must return False.
             Without this, verify() might be a function that always says yes.
  g=0        with an empty work list the recovered count must be 0 -- a recovery that reports
             success having copied nothing is the empty-population failure.
  POST       after every copy, the destination is re-hashed from disk (not from memory) and
             compared to the source. Mismatch aborts rather than warning.

PRE-REGISTERED: this script may only print RECOVERED n if n files were hash-verified at their
destination. Any mismatch -> exit 2 and no verdict. There is no partial-success wording.

EXIT 0 all planned files verified at destination · 2 a control failed or a copy did not verify
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
TMP = pathlib.Path("/tmp")
EXCLUDE_PREFIX = ("E99_fixtures/",)


def sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def verify(src: pathlib.Path, dst: pathlib.Path) -> bool:
    """Re-read BOTH from disk. Never compare a remembered digest to a written one."""
    return dst.exists() and dst.is_file() and sha(dst) == sha(src)


def main() -> int:
    lost = RES / "what_was_lost.json"
    if not lost.exists():
        print("  UNRUNNABLE: what_was_lost.json absent. Exit 2, never 0."); return 2
    W = json.loads(lost.read_text())

    print("R428 · recover — and prove each file arrived\n")

    # ------------------------------------------------------------------------------- controls
    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        a, b = t / "a.bin", t / "b.bin"
        a.write_bytes(b"R428 canary \x00\x01" * 101)
        shutil.copy2(a, b)
        pos = verify(a, b)
        bb = bytearray(b.read_bytes()); bb[3] ^= 0xFF; b.write_bytes(bytes(bb))
        neg = verify(a, b)
        print(f"  POSITIVE  verify() on a provably identical copy -> {pos}, must be True"
              f"   {'PASS' if pos else '⛔ FAIL'}")
        print(f"  NEGATIVE  verify() on a one-byte-corrupted copy  -> {neg}, must be False"
              f"   {'PASS' if not neg else '⛔ FAIL — verify() always says yes'}")
        if not (pos and not neg):
            print("\n  UNVERIFIED — verify() is unfit. Nothing is copied."); return 2

    # ------------------------------------------------------------- locate each path in a stash
    stashes = sorted(p for p in TMP.glob("attack_rounds_*") if p.is_dir())

    def find(rel: str) -> pathlib.Path | None:
        for s in stashes:
            p = s / rel
            if p.is_file():
                return p
        return None

    plan_a = [r for r in W["irrecoverable"] if not r.startswith(EXCLUDE_PREFIX)]
    skipped = [r for r in W["irrecoverable"] if r.startswith(EXCLUDE_PREFIX)]
    plan_b = [e["path"] for e in W["never_committed"]]

    print(f"\n  PLAN A · absent from the tree, copied in   {len(plan_a)}")
    print(f"  PLAN B · present but never-committed, ARCHIVED not overwritten   {len(plan_b)}")
    print(f"  EXCLUDED · a gate's own fixture   {len(skipped)}   {skipped}")
    print(f"  EXCLUDED · __pycache__ (regenerable)   {len(W['regenerable'])}\n")

    if not plan_a and not plan_b:
        print("  UNRUNNABLE: nothing to do — an empty work list must never print RECOVERED. Exit 2.")
        return 2

    ok, done_a, done_b, missing = True, [], [], []

    for rel in plan_a:
        src = find(rel)
        if src is None:
            missing.append(rel); ok = False; continue
        dst = ROOT / rel
        if dst.exists():
            # ⚠ the census said ABSENT. If it is here now, the world changed under the plan and
            #   this script must NOT proceed on a stale reading.
            print(f"    ⛔ {rel} EXISTS now but the census said absent — refusing, plan is stale")
            ok = False; continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        if verify(src, dst):
            done_a.append(rel)
        else:
            print(f"    ⛔ VERIFY FAILED at destination: {rel}"); ok = False

    for rel in plan_b:
        src = find(rel)
        if src is None:
            missing.append(rel); ok = False; continue
        rd = pathlib.PurePosixPath(rel)
        # round dir = the R### component's parent path
        parts = list(rd.parts)
        i = next((k for k, s in enumerate(parts) if s.startswith("R")), None)
        # ⛔ THIS WAS `_archive/pre_deletion_original` AND IT WAS THE SAME BUG ONE LEVEL UP.
        #    `.gitignore:3` ignores `_archive/`. So the first version of this script took the ONLY
        #    surviving copy of a never-committed source version and filed it into exactly the class
        #    of path this round had just measured as unrecoverable -- an untracked file whose sole
        #    copy is outside git. Ten minutes after proving that class is what gets destroyed.
        #    `git check-ignore` now decides the destination instead of my sense of where archives
        #    belong, and the recovery is worthless if its output is not in the index.
        base = ROOT.joinpath(*parts[: i + 1]) / "pre_deletion_original"
        dst = base / pathlib.PurePosixPath(*parts[i + 1:])
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        ig = subprocess.run(["git", "check-ignore", "-q", str(dst.relative_to(ROOT))],
                            cwd=str(ROOT), capture_output=True).returncode == 0
        if ig:
            print(f"    ⛔ DESTINATION IS GITIGNORED: {dst.relative_to(ROOT)} — recovering a "
                  f"never-committed file into an ignored path recreates the loss. REFUSING.")
            ok = False
            continue
        if verify(src, dst):
            done_b.append(str(dst.relative_to(ROOT)))
        else:
            print(f"    ⛔ VERIFY FAILED at destination: {dst}"); ok = False

    print(f"  RECOVERED (hash-verified at destination)   A {len(done_a)}   B {len(done_b)}")
    for r in done_a:
        print(f"    A  {r}")
    for r in done_b:
        print(f"    B  {r}")
    if missing:
        print(f"\n  ⛔ {len(missing)} planned paths were not found in any stash: {missing[:5]}")

    (RES / "recovered.json").write_text(json.dumps(
        {"plan_a": plan_a, "recovered_a": done_a, "plan_b": plan_b, "recovered_b": done_b,
         "excluded_fixture": skipped, "excluded_pycache": W["regenerable"],
         "missing": missing, "all_verified": ok}, indent=1))

    if not ok:
        print("\n  EXIT 2 — at least one file did not verify at its destination. There is no")
        print("  partial-success wording available here on purpose.")
        return 2
    print(f"\n  every planned file is byte-identical at its destination.")
    print(f"  artifact -> {(RES / 'recovered.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
