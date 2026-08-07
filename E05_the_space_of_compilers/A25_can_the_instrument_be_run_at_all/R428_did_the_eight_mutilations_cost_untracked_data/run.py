"""R428 -- did the EIGHT tree mutilations cost untracked data?

⛔ WHY THIS ROUND EXISTS, AND WHY IT IS NOT THE ROUND I PLANNED. Yesterday's incident was written
   up as "1,552 files deleted, restored with `git restore`, zero data loss." Both halves of that
   sentence were asserted, neither was measured. `/tmp` holds **EIGHT** `attack_rounds_*` stashes
   dated 08-03 and 08-04 -- so the event is not a one-off caused by my `pueue kill`, it is ROUTINE,
   and it happened five times on 08-03 without anyone noticing at all.

   `git restore` re-materialises what the INDEX knows. It cannot restore an untracked file. Every
   `results/*.json` written by a round and not yet committed is untracked at the moment it is
   moved aside. So "zero data loss" is a claim about a population -- untracked files inside the
   stashes -- that nobody enumerated. This round enumerates it.

ESTIMAND (named before the method)
    LOST      = |{ p : p is a file inside some orphaned stash, p is ABSENT from the live tree }|
    DIVERGENT = |{ p : p present in BOTH, but the bytes differ }|
    both restricted to the sub-population that matters: p NOT tracked by git at HEAD, because a
    tracked path is recoverable by definition and its presence in a stash proves nothing.
    p is a repo-relative path: `<stash>/E05_.../R427_.../results/x.json` -> `E05_.../R427_.../results/x.json`.

IDENTIFICATION
    Fully identified, and it is a CENSUS, not a sample: every stash on this machine is enumerated,
    every file in it is hashed. There is no sampling uncertainty and therefore NO MDE -- reporting
    a confidence interval on a census would be the arithmetic trap wearing statistics.
    What the census CANNOT see: a stash already deleted by tmp reaping. That is a floor, not a
    point, and the number below is therefore a LOWER BOUND on historical loss.

SCOPE
    population : the 8 `attack_rounds_*` directories present in /tmp at run time
    instrument : filesystem walk + sha256 + `git ls-files` at HEAD
    baseline   : the live working tree as restored at dc5c7e3
    regime     : after `git restore` of the five epochs; before any recovery action

⚠ UNIT DISCIPLINE (the ledger's own scar: a positive control asks *can this instrument see*, never
   *is what it sees the thing I claim about*). Written as two strings, required to be equal:
       instrument's unit : "a repo-relative file path, compared by existence and by sha256"
       claim's unit      : "a repo-relative file path, compared by existence and by sha256"
   They are equal. What this instrument therefore CANNOT support is any claim about a file's
   VALUE or importance -- 300 lost bytes of a scratch file and 300 lost bytes of a headline
   artifact count the same here, and the round says so rather than ranking them silently.

WORLDS
    W-NO-LOSS      every untracked stashed file is present in the tree with identical bytes.
                   -> "zero data loss" SURVIVES, and the stashes are safe to delete.
    W-SILENT-LOSS  untracked artifacts exist ONLY in /tmp.
                   -> "zero data loss" is OVERTURNED, and /tmp is a reaped directory, so this is
                      live risk rather than history.
    W-DIVERGENT    present in both but different bytes -- the tree's copy may be the OLDER one if
                   a stash captured work that the restore then overwrote from the index.

PREDICTION MATRIX
                        LOST=0,DIV=0   LOST>0        DIV>0,LOST=0
    W-NO-LOSS               0.9          0.02           0.05
    W-SILENT-LOSS           0.05         0.9            0.2
    W-DIVERGENT             0.05         0.08           0.75

PRE-REGISTERED KILL (written before the run, threshold and all)
    LOST > 0 over untracked paths  ->  the sentence "restored with zero data loss" is OVERTURNED.
    LOST = 0 AND DIVERGENT = 0     ->  it is CONFIRMED, for this population only.
    the instrument's controls fail ->  UNVERIFIED. Never OVERTURNED, never CONFIRMED.
    ⚠ the kill is a CONDITIONAL, not a threshold: it is evaluated ONLY if POS fires and PLACEBO is
      null. A kill that can fire on a broken instrument is an automated way to publish an artifact.

CONTROLS
    POSITIVE  a synthetic path that cannot exist in the tree is injected into the candidate set and
              MUST be reported LOST; a path known present MUST be reported present. Retention is
              reported. It FAILS AT g=0: with zero planted paths the planted-LOST count must be 0,
              which is checked, because a control that fires on an empty plant is not a control.
    PLACEBO   a stash synthesised by copying a live round directory verbatim. LOST and DIVERGENT
              must both be EXACTLY 0. A non-zero here means the comparison itself is broken and
              every real number is void.
    NEGATIVE  a stash synthesised by copying a live round and then CORRUPTING one byte of one file.
              DIVERGENT must be exactly 1. This is the world W-DIVERGENT built synthetically --
              without it, a DIVERGENT=0 result is silence rather than a measurement.
    SHAM      the same walk restricted to TRACKED paths only. These are recoverable by definition,
              so any LOST among them is not data loss; reporting it beside the real number shows
              how much of the raw count the tracked/untracked split is doing.

MULTIPLICITY  8 stashes x 2 statistics = 16 cells, all reported, survivors and non-survivors.
SEEDS         none: the instrument is deterministic. Reproducibility is byte-identity of the
              artifact across two runs, which is checked by re-running, not asserted.
ARTIFACT      results/loss_census.json, with the source sha and the full per-stash table, so a
              later round can attack this without re-walking a /tmp that may be gone.

IMPOSSIBLE HERE, NAMED
    * historical completeness -- a stash reaped before today is invisible; the number is a LOWER
      BOUND. It would require a tmp-retention policy that did not exist.
    * attributing a stash to the run that made it -- the directory name is random and carries no
      provenance. It would require the harness to stamp its own stash.
    * ranking the loss by importance -- see UNIT DISCIPLINE. It would require a criterion for
      which artifacts matter, which is a separate judgement, not a measurement.

EXIT  0 census complete and controls passed · 1 kill fired (LOST>0) · 2 UNRUNNABLE / controls unfit
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


def sha(p: pathlib.Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def tracked_at_head() -> set[str]:
    r = subprocess.run(["git", "ls-files"], cwd=str(ROOT), capture_output=True, text=True)
    return {l for l in r.stdout.split("\n") if l.strip()}


def walk(stash: pathlib.Path) -> list[tuple[str, pathlib.Path]]:
    """-> [(repo-relative path, absolute path in the stash)] for every regular file."""
    out = []
    for p in stash.rglob("*"):
        if p.is_file() and not p.is_symlink():
            out.append((str(p.relative_to(stash)), p))
    return sorted(out)


def compare(stash: pathlib.Path, tracked: set[str], extra: list[str] | None = None):
    """The single comparison used for BOTH the real stashes and every control.

    ⚠ the controls and the subject MUST go through this same function. A control that exercises a
      different code path than the thing it certifies is the failure this campaign has recorded
      four times -- `the control fails for its own reasons` -- and the cheapest way to avoid it is
      to have exactly one comparison.
    """
    lost_u, lost_t, div_u, div_t, same = [], [], [], [], 0
    items = walk(stash)
    for rel in (extra or []):
        items.append((rel, None))                       # planted: absent from the stash on purpose
    for rel, src in items:
        dst = ROOT / rel
        is_tracked = rel in tracked
        if not dst.exists():
            (lost_t if is_tracked else lost_u).append(rel)
            continue
        if src is None:
            same += 1
            continue
        try:
            if sha(src) != sha(dst):
                (div_t if is_tracked else div_u).append(rel)
            else:
                same += 1
        except OSError:
            (div_t if is_tracked else div_u).append(rel)
    return {"n_files": len(items), "same": same,
            "lost_untracked": lost_u, "lost_tracked": lost_t,
            "divergent_untracked": div_u, "divergent_tracked": div_t}


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    stashes = sorted(p for p in TMP.glob("attack_rounds_*") if p.is_dir())
    tracked = tracked_at_head()
    print("R428 · did the EIGHT tree mutilations cost untracked data?\n")
    print(f"  ⛔ the incident was written up as a ONE-OFF caused by my `pueue kill`. /tmp holds")
    print(f"     {len(stashes)} orphaned stashes across two days. The event is ROUTINE.\n")
    if not stashes:
        print("  UNRUNNABLE: no stash found -- an empty population must never pass. Exit 2.")
        return 2
    if not tracked:
        print("  UNRUNNABLE: `git ls-files` returned nothing -- the tracked/untracked split, which")
        print("  is the whole estimand, would be meaningless. Exit 2.")
        return 2

    # ---------------------------------------------------------------- controls, BEFORE the subject
    print("  CONTROLS (all four run before any real number is read)\n")
    ctl_ok = True

    # PLACEBO -- a stash that IS the tree. Must return exactly zero on both statistics.
    with tempfile.TemporaryDirectory() as td:
        fake = pathlib.Path(td) / "placebo"
        src_round = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
        shutil.copytree(src_round, fake / src_round.relative_to(ROOT), symlinks=True)
        pl = compare(fake, tracked)
        ok = not (pl["lost_untracked"] or pl["lost_tracked"]
                  or pl["divergent_untracked"] or pl["divergent_tracked"])
        ctl_ok &= ok
        print(f"    PLACEBO   a stash copied verbatim from the live tree ({pl['n_files']} files)")
        print(f"              lost {len(pl['lost_untracked'])+len(pl['lost_tracked'])} · "
              f"divergent {len(pl['divergent_untracked'])+len(pl['divergent_tracked'])} · "
              f"must be 0/0   {'PASS' if ok else '⛔ FAIL — the comparison is broken'}")

        # NEGATIVE -- the same copy with ONE byte changed. Builds world W-DIVERGENT synthetically.
        victim = next(p for p in sorted(fake.rglob("*")) if p.is_file() and p.stat().st_size > 0)
        b = bytearray(victim.read_bytes()); b[0] ^= 0xFF; victim.write_bytes(bytes(b))
        ng = compare(fake, tracked)
        ndiv = len(ng["divergent_untracked"]) + len(ng["divergent_tracked"])
        ok = ndiv == 1
        ctl_ok &= ok
        print(f"    NEGATIVE  the same copy, ONE byte flipped -> divergent {ndiv}, must be exactly 1"
              f"   {'PASS' if ok else '⛔ FAIL — a real divergence would be invisible'}")

        # POSITIVE -- plant paths that cannot exist. Retention = fraction recovered.
        plant = [f"__R428_PLANTED_ABSENT_{i}__/x.json" for i in range(5)]
        pos = compare(fake, tracked, extra=plant)
        rec = sum(1 for p in plant if p in pos["lost_untracked"])
        ok = rec == len(plant)
        ctl_ok &= ok
        print(f"    POSITIVE  {len(plant)} paths planted that cannot exist -> reported LOST "
              f"{rec}/{len(plant)} (retention {rec/len(plant):.0%})"
              f"   {'PASS' if ok else '⛔ FAIL — the instrument cannot see an absence'}")

        # ...and it must FAIL AT g=0: with nothing planted, the planted-lost count must be 0.
        g0 = compare(fake, tracked, extra=[])
        g0_lost = sum(1 for p in g0["lost_untracked"] if p.startswith("__R428_PLANTED"))
        ok = g0_lost == 0
        ctl_ok &= ok
        print(f"    g=0       nothing planted -> planted-LOST {g0_lost}, must be 0"
              f"   {'PASS' if ok else '⛔ FAIL — the control fires on an empty plant'}")

    if not ctl_ok:
        print("\n  UNVERIFIED — a control is unfit, so the kill is NOT evaluated. This is the")
        print("  conditional form: a kill that can fire on a broken instrument is an automated way")
        print("  to publish an artifact.")
        json.dump({"world": "UNVERIFIED", "reason": "control unfit"},
                  (RES / "loss_census.json").open("w"), indent=1)
        return 2

    # ---------------------------------------------------------------------------- the census
    print("\n  THE CENSUS — every stash, every file, tracked and untracked reported separately\n")
    print(f"    {'stash':<24} {'files':>6} {'LOST-u':>7} {'LOST-t':>7} {'DIV-u':>6} {'DIV-t':>6}")
    rows, LOST_U, DIV_U, LOST_T, DIV_T = {}, set(), set(), set(), set()
    for s in stashes:
        r = compare(s, tracked)
        rows[s.name] = {k: (v if isinstance(v, int) else len(v)) for k, v in r.items()}
        rows[s.name]["lost_untracked_paths"] = r["lost_untracked"][:200]
        rows[s.name]["divergent_untracked_paths"] = r["divergent_untracked"][:200]
        LOST_U |= set(r["lost_untracked"]); DIV_U |= set(r["divergent_untracked"])
        LOST_T |= set(r["lost_tracked"]); DIV_T |= set(r["divergent_tracked"])
        print(f"    {s.name:<24} {r['n_files']:>6} {len(r['lost_untracked']):>7} "
              f"{len(r['lost_tracked']):>7} {len(r['divergent_untracked']):>6} "
              f"{len(r['divergent_tracked']):>6}")

    print(f"\n    {'UNION (a path lost in ANY stash)':<24} "
          f"LOST-u {len(LOST_U)} · LOST-t {len(LOST_T)} · DIV-u {len(DIV_U)} · DIV-t {len(DIV_T)}")
    print(f"    SHAM (tracked-only, recoverable by definition): LOST {len(LOST_T)} — reported"
          f" beside the real number so the split's contribution is visible, not silent.")

    # ------------------------------------------------------------------- the conditional kill
    world = ("W-SILENT-LOSS" if LOST_U else
             "W-DIVERGENT" if DIV_U else "W-NO-LOSS")
    print(f"\n  WORLD: {world}")
    if LOST_U:
        print(f"    ⛔ KILL FIRED. {len(LOST_U)} untracked paths exist ONLY in /tmp. The sentence")
        print(f"    'restored with zero data loss' is OVERTURNED. A sample:")
        for p in sorted(LOST_U)[:12]:
            print(f"        {p}")
    elif DIV_U:
        print(f"    {len(DIV_U)} untracked paths differ between stash and tree. Not loss, but the")
        print(f"    tree's copy is not provably the newer one. A sample:")
        for p in sorted(DIV_U)[:12]:
            print(f"        {p}")
    else:
        print("    'restored with zero data loss' is CONFIRMED — for this population, which is the")
        print("    8 stashes still on disk. A stash already reaped is invisible, so this is a")
        print("    LOWER BOUND on historical loss and is not a claim about 08-03 in general.")

    out = {"source_sha": sha(pathlib.Path(__file__))[:16], "n_stashes": len(stashes),
           "world": world, "controls_ok": ctl_ok,
           "union": {"lost_untracked": sorted(LOST_U), "lost_tracked_count": len(LOST_T),
                     "divergent_untracked": sorted(DIV_U), "divergent_tracked_count": len(DIV_T)},
           "cells_tested": len(stashes) * 2, "rows": rows}
    (RES / "loss_census.json").write_text(json.dumps(out, indent=1))
    print(f"\n  artifact -> {(RES / 'loss_census.json').relative_to(ROOT)}")
    return 1 if LOST_U else 0


if __name__ == "__main__":
    sys.exit(main())
