"""A round's recorded source hash must equal the sha256 of the source sitting beside it.

`covalx/stamp.py` has written this record since long before anyone checked it, and its own docstring
names the failure exactly:

    "a round patched after it ran passes that gate forever while its persisted numbers no longer
     exist in any output"

R345 measured what an unenforced record is worth: of 79 rounds carrying a stamp-like key, **33 were
STALE** -- the artifact had outlived the code claiming to have produced it -- 14 FRESH, and 32 whose
subject could not be established. Until this file existed, `grep -rl source_sha256` across
`assurance/`, `covalx/` and `db/` returned exactly ONE path: the definition. Written by 22 rounds,
read by nothing.

THREE-VALUED, and the third value is 32 rounds wide
----------------------------------------------------
  FRESH        recorded == sha256(run.py) today
  STALE        recorded != sha256(run.py), AND the source provably hashes ITSELF
  UNVERIFIED   a stamp-like key whose subject this check cannot establish -- it may hash an input,
               a dataset, a model. NEVER counted STALE, never counted FRESH.

The middle case is not caution for its own sake. A key-name match reported 38 stale; a tight regex
for an inline `sha256(Path(__file__).read_bytes())` reported 14; both were wrong, because
`**stamp(__file__)` puts the hash in ANOTHER FILE and no regex over a round's own text can see that
it hashes anything at all. Resolving both routes gives 33. A false conviction and a false acquittal
were one regex apart in the same measurement, which is why the resolution is explicit and the
unresolved are named rather than assigned.

⚠⚠ AND THE POPULATION IS 24% OF THE CORPUS. THIS IS THE LARGEST LIMIT AND IT WAS NOT IN v1.
326 rounds carry a json artifact. **79 carry a stamp of any kind.** The other **247 are outside this
check entirely** -- not FRESH, not STALE, not even UNVERIFIED, because there is nothing to compare.
Reporting "33 stale of 47 resolvable" without that denominator invites the reading that the corpus
is 70% drifted, when what is measured is 70% of the quarter that opted in.

I found this by getting a prediction wrong in the direction that matters. `R242_self_audit`
regenerates COMPLETELY differently -- committed `23 rounds / 151 declared / 8 gaps`, today
`124 rounds / 1405 declared / 217 gaps` -- so I expected regenerating it to flip a frozen entry to
FRESH and fire this check's second door. It fired nothing, correctly: R242 records no stamp, is in
no list, and is invisible here. Two populations I had silently merged -- "rounds whose re-run
differs" and "rounds whose stamp mismatches" -- and R242 is in the first and not the second.
**A round with no stamp cannot drift-detect, and its silence reads exactly like a clean one.**

⚠ WHAT THIS DETECTS, AND WHAT IT CANNOT
  DETECTS   DRIFT -- a source edited after its artifact was written.
  CANNOT    FORGERY -- whoever edits an artifact can write any hash into it, and this check would
            call the result FRESH. Only re-running the round tests that, which costs what R344
            measures. `FRESH` here means "no drift detected", never "produced by this source".
  CANNOT    CORRECTNESS -- an edit to a comment or a print statement changes the hash and nothing
            else. STALE means the artifact's currency is UNKNOWN, not that its numbers are wrong.

WHY A RATCHET AND NOT A GATE
-----------------------------
Failing outright on 33 pre-existing stale rounds turns the suite red until 33 artifacts are
regenerated, which is R344's cost question and not a decision this file gets to make. Reporting
without gating is worse: this package has already measured that a confession written into a
LIMITS file is walked past for rounds on end. So the debt is FROZEN in `KNOWN_STALE.json` and the
check fails on:

  (a) any round that is STALE and NOT in the frozen list  -- the debt may not grow;
  (b) any round in the frozen list that is now FRESH      -- the list may not outlive its reason,
                                                             so it shrinks and cannot become a
                                                             place where entries quietly accumulate.

(b) is what stops the allowlist from becoming the confession it replaced.

EXIT
    0  no new drift, and the frozen list contains nothing already fixed
    1  a round drifted, or the frozen list is stale itself
    2  no round carries a stamp, or the frozen list is missing: an empty population, never a pass
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = ROOT / "assurance" / "KNOWN_STALE.json"
STAMP_KEYS = re.compile(r"^(source_sha256|source_sha|src_sha|source_hash|src_hash|code_sha|"
                        r"run_sha|sha_source)$", re.I)
INLINE_SELFHASH = re.compile(r"sha256\(\s*(pathlib\.)?Path\(__file__\)[^)]*\.read_bytes\(\)|"
                             r"sha256\(\s*open\(__file__|__file__[^\n]*read_bytes\(\)\)\.hexdigest",
                             re.S)
HELPER_SELFHASH = re.compile(r"stamp\(\s*__file__\s*\)")


def self_hashes(src: str) -> str:
    if HELPER_SELFHASH.search(src):
        return "stamp(__file__)"
    if INLINE_SELFHASH.search(src):
        return "inline sha256(__file__)"
    return ""


def recorded(rd: pathlib.Path) -> list[str]:
    out, res = [], rd / "results"
    if not res.is_dir():
        return out
    for f in sorted(res.glob("*.json")):
        if "_smoke" in f.name or f.stat().st_size > 6_000_000:
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if (STAMP_KEYS.match(k) and isinstance(v, str)
                            and re.fullmatch(r"[0-9a-f]{8,64}", v)):
                        out.append(v)
                    else:
                        walk(v)
            elif isinstance(o, list):
                for v in o[:200]:
                    walk(v)
        walk(d)
    return out


def classify(rd: pathlib.Path):
    rp = rd / "run.py"
    if not rp.exists():
        return None
    rec = recorded(rd)
    if not rec:
        return None
    how = self_hashes(rp.read_text(encoding="utf-8", errors="replace"))
    full = hashlib.sha256(rp.read_bytes()).hexdigest()
    if not how:
        return ("UNVERIFIED", rec, full, "cannot establish the key hashes THIS source")
    return ("FRESH" if any(full.startswith(v) for v in rec) else "STALE", rec, full, how)


def planted() -> tuple[bool, str]:
    """Both directions, in a temp dir, on every run. A checker that returns the same label for a
    matching and a mismatching stamp measures nothing."""
    import shutil
    import tempfile
    d = pathlib.Path(tempfile.mkdtemp(prefix="stampctl_"))
    try:
        rd = d / "R000_plant"
        (rd / "results").mkdir(parents=True)
        src = "import hashlib, pathlib\nh = hashlib.sha256(pathlib.Path(__file__).read_bytes())\n"
        (rd / "run.py").write_text(src)
        h = hashlib.sha256((rd / "run.py").read_bytes()).hexdigest()
        (rd / "results" / "r.json").write_text(json.dumps({"source_sha256": h}))
        a = classify(rd)
        (rd / "run.py").write_text(src + "# drift\n")
        b = classify(rd)
        # and a stamp-like key with no self-hashing source must be UNVERIFIED, not either verdict
        rd2 = d / "R001_plant"
        (rd2 / "results").mkdir(parents=True)
        (rd2 / "run.py").write_text("x = 1\n")
        (rd2 / "results" / "r.json").write_text(json.dumps({"source_sha": "deadbeefdeadbeef"}))
        c = classify(rd2)
        ok = (a and a[0] == "FRESH") and (b and b[0] == "STALE") and (c and c[0] == "UNVERIFIED")
        return bool(ok), (f"matching -> {a[0] if a else None} (want FRESH); drifted -> "
                          f"{b[0] if b else None} (want STALE); unattributable -> "
                          f"{c[0] if c else None} (want UNVERIFIED)")
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main() -> int:
    p_ok, p_detail = planted()
    print(f"  planted control: {p_detail}  {'PASS' if p_ok else 'FAIL'}")

    rows = {}
    for rp in sorted(ROOT.glob("E*/A*/R*/run.py")):
        c = classify(rp.parent)
        if c:
            rows[rp.parent.name] = c
    if not rows:
        print("  UNRUNNABLE: no round carries a source stamp. Exit 2, never 0.")
        return 2
    if not FROZEN.exists():
        print(f"  UNRUNNABLE: {FROZEN.name} is missing, so `new drift` has no baseline to be new")
        print("  against, and a clean run would mean nothing. Exit 2, never 0.")
        return 2
    frozen = set(json.loads(FROZEN.read_text(encoding="utf-8"))["stale"])

    counts = {k: sum(1 for v in rows.values() if v[0] == k)
              for k in ("FRESH", "STALE", "UNVERIFIED")}
    # The denominator is printed on EVERY run, because the stamped set is a quarter of the corpus
    # and a rate quoted without it reads as a property of the whole.
    with_art = sum(1 for rp in ROOT.glob("E*/A*/R*/run.py")
                   if (rp.parent / "results").is_dir()
                   and any(f.suffix == ".json" and "_smoke" not in f.name
                           for f in (rp.parent / "results").glob("*")))
    print(f"  {len(rows)} round(s) carry a stamp — FRESH {counts['FRESH']}, "
          f"STALE {counts['STALE']}, UNVERIFIED {counts['UNVERIFIED']}  "
          f"(frozen debt: {len(frozen)})")
    print(f"  ⚠ POPULATION: {len(rows)} stamped of {with_art} rounds with an artifact "
          f"({len(rows)/with_art:.0%}). The other {with_art - len(rows)} are OUTSIDE this check —"
          f" not clean, unmeasurable.")

    new_drift = sorted(n for n, v in rows.items() if v[0] == "STALE" and n not in frozen)
    fixed = sorted(n for n in frozen if n in rows and rows[n][0] == "FRESH")
    gone = sorted(n for n in frozen if n not in rows)

    fail = 0
    if new_drift:
        fail = 1
        print(f"\n  NEW DRIFT — {len(new_drift)} round(s) STALE and not in the frozen debt:")
        for n in new_drift:
            print(f"      {n:<50} recorded {rows[n][1][0][:16]}  now {rows[n][2][:16]}")
        print("  Re-run the round, or add it to KNOWN_STALE.json with a reason. The debt may grow")
        print("  only deliberately.")
    if fixed:
        fail = 1
        print(f"\n  FROZEN LIST IS STALE — {len(fixed)} round(s) in it are now FRESH: {fixed}")
        print("  Remove them. A frozen list that outlives its reason is the confession this check")
        print("  was built to replace.")
    if gone:
        print(f"\n  ⚠ {len(gone)} frozen entr(ies) no longer carry a stamp at all: {gone}")
        print("    Not gated: a round may legitimately stop stamping. Reported so it is not silent.")

    print("\n  ⚠ FRESH means NO DRIFT DETECTED. It does not mean the artifact was produced by this")
    print("    source: whoever edits an artifact can write any hash into it, and this check would")
    print("    agree. Drift is detectable statically; forgery is not, and only re-running settles")
    print("    it. STALE likewise means the currency is UNKNOWN, not that the numbers are wrong —")
    print("    editing a comment changes the hash and nothing else.")

    if not p_ok:
        print("\n  DRIFTED: the planted control misbehaved, so the verdict above is silence.")
        return 1
    if fail:
        return 1
    print(f"\n  no new drift; the frozen debt of {len(frozen)} is unchanged and contains nothing "
          f"already fixed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
