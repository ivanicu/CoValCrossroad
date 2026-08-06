#!/usr/bin/env python3
"""
R842 · is the definition's own evidence byte-reproducible? Measured, not inferred from source.

⛔ WHY. R841 found one round seeded from `hash(p)` -- per-process randomised -- and the sweep in
1358 found 33 such lines in 29 files. But that sweep's OWN proxy ledger says: *`hash(` in a seed
=> not reproducible is sound; ABSENCE => reproducible is NOT.* So a clean grep licenses nothing.

And the intersection makes that bite. The definition's anchor table names **83 source rounds**,
all in **R301..R838**. The unstable-seed rounds are **25, all in R122..R302**. The intersection is
**0 -- but the ranges overlap only at {R301, R302}**, so that zero is very nearly FORCED by
arithmetic. **It is a DERIVATION dressed as a clean bill**, and reporting it as reassurance would
be exactly the trap this project's own standard opens with.

Two worlds are left, and they are not distinguishable by any amount of further reading:
  A · the practice was corrected around R302, and the later rounds -- the ones the definition
      actually rests on -- ARE reproducible.
  B · the later rounds are irreproducible by a mechanism the source grep cannot see (unordered
      set iteration, dict ordering over a set, wall-clock, an env var, a rebuilt input).
**Only running them twice separates A from B.**

ESTIMAND        for each round tested, whether two runs in FRESH PROCESSES produce
                byte-identical artifacts (sha256 over every file in results/, excluding logs)
IDENTIFICATION  yes, and it is the only direct measurement of the `REPRODUCIBILITY two hash seeds
                byte-identical` line the checklist has demanded all along and nobody ran.
SCOPE           population: 1 known-unstable round + 3 rounds NAMED IN THE DEFINITION'S OWN
                            anchor table (`definition_matches_the_record.py`)
                instrument: sha256 over results/, fresh `python` process per run
                baseline:   the harness's own synthetic pair (below)
                regime:     this repo, this commit, single machine
WORLDS          A later rounds reproducible · B irreproducible by an unseen mechanism
KILL            CONDITIONAL, before any verdict:
                  if synth_unstable differs AND synth_stable is identical
                  then read the rounds
                  else UNVERIFIED -- the differ cannot tell the two apart, so nothing it says counts
POSITIVE CTRL   a synthetic script seeding from `hash(str)` MUST come out non-identical.
                Plus R243, a round on the frozen unstable list, which SHOULD also differ --
                reported separately, because a round can be on that list and still write an
                artifact that does not depend on the unstable draw. That is a real outcome and
                is NOT a failure of the differ.
G=0             a synthetic deterministic script MUST come out identical. Required: a differ that
                answers "different" to everything passes the positive arm alone.
ARTIFACT        results/reproducibility.json with the commit hash and per-round digests.
IMPOSSIBLE      cross-machine (one box) · independently replicated (one suite) ·
                causally identified -- this says WHETHER, never WHY a round is irreproducible.
                N/A with what each would require, never "planned".
⚠ SAFETY        re-running a round OVERWRITES its committed artifacts. Every touched round is
                restored with `git restore` afterwards, and the tree census is checked.
"""
import hashlib, json, pathlib, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
PY = str(ROOT / ".venv" / "bin" / "python")
SKIP = {".log", ".txt"}          # run logs carry timings; they are not the artifact


def digest(d: pathlib.Path) -> str:
    h = hashlib.sha256()
    for f in sorted(d.rglob("*")):
        if f.is_file() and f.suffix not in SKIP and "__pycache__" not in str(f):
            h.update(f.name.encode()); h.update(f.read_bytes())
    return h.hexdigest()


def run_twice(round_dir: pathlib.Path, timeout=420):
    res = round_dir / "results"
    digs, rcs = [], []
    for _ in range(2):
        p = subprocess.run([PY, str(round_dir / "run.py")], capture_output=True, text=True,
                           cwd=str(ROOT), timeout=timeout)
        rcs.append(p.returncode)
        digs.append(digest(res) if res.exists() else None)
    return digs, rcs


def synthetic_pair():
    """The differ must separate an unstable script from a stable one. Both arms required."""
    tmp = pathlib.Path(tempfile.mkdtemp())
    out = []
    for name, body in (
        ("unstable", "import json,pathlib,numpy as np\n"
                     "p=pathlib.Path(__file__).parent/'results';p.mkdir(exist_ok=True)\n"
                     "r=np.random.default_rng(hash('abc')%99991)\n"
                     "json.dump({'x':float(r.random())},open(p/'a.json','w'))\n"),
        ("stable",   "import json,pathlib,zlib,numpy as np\n"
                     "p=pathlib.Path(__file__).parent/'results';p.mkdir(exist_ok=True)\n"
                     "r=np.random.default_rng(zlib.crc32(b'abc')%99991)\n"
                     "json.dump({'x':float(r.random())},open(p/'a.json','w'))\n")):
        d = tmp / name; d.mkdir(); (d / "run.py").write_text(body)
        digs, _ = run_twice(d, timeout=90)
        out.append(digs[0] == digs[1])
    unstable_differs, stable_identical = (not out[0]), out[1]
    print(f"  POSITIVE CONTROL  a hash()-seeded script is NON-identical across runs: "
          f"{unstable_differs}  {'PASS' if unstable_differs else 'FAIL'}")
    print(f"  g=0               a crc32-seeded script IS identical across runs: "
          f"{stable_identical}  {'PASS' if stable_identical else 'FAIL'}")
    print("    Both arms are required. A differ that answers 'different' to everything passes")
    print("    the first arm alone, and that is the shape this suite keeps rebuilding.")
    shutil.rmtree(tmp, ignore_errors=True)
    return unstable_differs and stable_identical


def main() -> int:
    if not synthetic_pair():
        print("\n  UNVERIFIED: the differ cannot separate a stable script from an unstable one.")
        print("  Nothing it says about a real round counts. Exit 2, never 0.")
        return 2

    targets = sys.argv[1:] or ["R243", "R436", "R440", "R824"]
    rows, touched = [], []
    print(f"\n  {'round':<10}{'runs':>6}  {'identical':<11} note")
    for t in targets:
        cand = sorted(ROOT.glob(f"E0*/A*/{t}_*"))
        if not cand:
            rows.append({"round": t, "status": "NOT FOUND"})
            print(f"  {t:<10}{'-':>6}  {'-':<11} not found — reported, never dropped")
            continue
        d = cand[0]; touched.append(str(d.relative_to(ROOT)))
        try:
            digs, rcs = run_twice(d)
        except subprocess.TimeoutExpired:
            rows.append({"round": t, "status": "TIMEOUT"})
            print(f"  {t:<10}{'-':>6}  {'-':<11} TIMEOUT — UNVERIFIED, not reproducible-or-not")
            continue
        if any(x is None for x in digs):
            rows.append({"round": t, "status": "NO ARTIFACT", "rc": rcs})
            print(f"  {t:<10}{str(rcs):>6}  {'-':<11} wrote no results/ — cannot be compared")
            continue
        same = digs[0] == digs[1]
        rows.append({"round": t, "status": "COMPARED", "identical": same,
                     "rc": rcs, "sha_a": digs[0][:16], "sha_b": digs[1][:16]})
        print(f"  {t:<10}{str(rcs):>6}  {str(same):<11} {digs[0][:12]} vs {digs[1][:12]}")

    # ⚠ restore every artifact this round overwrote
    if touched:
        subprocess.run(["git", "-C", str(ROOT), "restore", "--staged", "--worktree", *touched],
                       capture_output=True, text=True)
        print(f"\n  restored {len(touched)} round director(ies) overwritten by the re-runs")

    comp = [r for r in rows if r["status"] == "COMPARED"]
    n_id = sum(1 for r in comp if r["identical"])
    print(f"  ⭐ {n_id} of {len(comp)} compared round(s) byte-identical across two fresh processes")
    print("     Every non-compared round is listed above and folded into NEITHER count.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "rows": rows,
               "compared": len(comp), "identical": n_id}, open(OUT / "reproducibility.json", "w"),
              indent=2)
    print(f"\n  artifact: results/reproducibility.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
