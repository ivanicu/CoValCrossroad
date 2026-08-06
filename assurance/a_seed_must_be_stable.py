#!/usr/bin/env python3
"""A seed built from `hash()` of a string is not a seed.

⛔ WHY. R841 found that entry 1352's per-prompt annotator draw was seeded with
`np.random.default_rng(900 + s + hash(p) % 1000)` where `p` is a prompt UUID **string**.
**Python randomises `hash()` of a `str` per process.** Measured against a `crc32` control:

    hash('prompt_42') % 1000   ->  924 / 294 / 947   across three fresh processes
    crc32(b'prompt_42') % 1000 ->  632 / 632 / 632   in the same three

So the draw was **unseeded**, the `seeds=(...)` argument was decorative, and the round's numbers
were one unlabelled sample from a distribution nobody characterised. Measured cost in that one
case: the spread across seed sets was **0.0041 on an effect of ~0.007 — 59% of the effect.**

Swept across the project afterwards: **33 code lines in 29 files** do the same thing.

⚠ WHAT THIS DOES AND DOES NOT ASSERT.
  DOES     those draws cannot be reproduced; an exact number quoted from them cannot be re-derived,
           `>=3 seeds` never isolated seed variance, and two-seed byte-identity was unachievable.
  DOES NOT say the results are WRONG. An unseeded draw is still an unbiased sample. What is void is
           the REPRODUCIBILITY claim and the SEED-SPREAD claim, not the estimate.
  DOES NOT generalise R841's 59% to the other 28 files. That is one measured case, not a rate.

PROXY LEDGER
  PROPERTY    every RNG in a round is seeded reproducibly across processes
  PROXY       no code line constructs an RNG seed from `hash(...)`
  IMPLICATION `hash(` in a seed -> not reproducible is SOUND (for str/tuple-of-str arguments).
              absence -> reproducible is NOT: a seed can be stable and still be read from the
              clock, an env var, or an unsorted set. This rules on ONE failure mode.
  SAFE SIDE   flags only the pattern it can prove unstable. Silence is not a certificate.
"""
import pathlib, re, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = pathlib.Path(__file__).resolve().parent / "KNOWN_UNSTABLE_SEEDS.json"
RX = re.compile(r"(default_rng|RandomState|seed\s*=)\s*\(?[^)\n]*\bhash\s*\(")


def offenders(paths):
    out = []
    for f in paths:
        try:
            lines = f.read_text(errors="ignore").splitlines()
        except Exception:
            continue
        for i, ln in enumerate(lines, 1):
            if ln.lstrip().startswith("#"):
                continue
            code = ln.split("#")[0]
            if RX.search(code):
                try:
                    name = str(f.relative_to(ROOT))
                except ValueError:
                    name = str(f)          # synthetic control files live outside the repo
                out.append((name, i, code.strip()[:100]))
    return out


def synthetic_controls() -> bool:
    """Positive: the pattern must be caught. g=0: a stable seed and a mere MENTION must not be."""
    d = pathlib.Path(tempfile.mkdtemp())
    bad = d / "bad.py"
    bad.write_text("import numpy as np\nrng = np.random.default_rng(7 + hash(p) % 99)\n")
    good = d / "good.py"
    good.write_text("import numpy as np, zlib\n"
                    "rng = np.random.default_rng(7 + zlib.crc32(p.encode()) % 99)\n"
                    "# do not seed from hash(p) -- this COMMENT must not be flagged\n")
    pos = len(offenders([bad])) == 1
    g0 = len(offenders([good])) == 0
    print(f"  POSITIVE CONTROL  a hash()-seeded RNG is flagged: {pos}  {'PASS' if pos else 'FAIL'}")
    print(f"  g=0               a crc32 seed and a COMMENT mentioning hash(p) are NOT flagged: "
          f"{g0}  {'PASS' if g0 else 'FAIL'}")
    print("    The g=0 arm is not decorative: the first version of this sweep matched its own")
    print("    explanatory comment and reported a file that had already been repaired.")
    return pos and g0


def main() -> int:
    if not synthetic_controls():
        print("\n  UNVERIFIED: the detector failed its own controls. Exit 2, never 0.")
        return 2

    paths = sorted(ROOT.glob("E0*/A*/R*/run.py")) + sorted(ROOT.glob("corebench/*.py"))
    if not paths:
        print("\n  OBSERVED NOTHING: no run.py found. A check with no population has not passed.")
        print("  Exit 2 — and note this is also the tree-loss signature; check the working tree.")
        return 2

    hits = offenders(paths)
    files = {h[0] for h in hits}
    print(f"\n  scanned {len(paths)} files · {len(hits)} seed line(s) built from hash() "
          f"in {len(files)} file(s)")

    frozen = set()
    if FROZEN.exists():
        import json
        frozen = set(json.loads(FROZEN.read_text())["files"])
    new = sorted(files - frozen)
    fixed = sorted(frozen - files)

    if fixed:
        print(f"  ⓘ {len(fixed)} previously-offending file(s) now use a stable seed: {fixed[:3]}")
    if new:
        print(f"\n  FAIL: {len(new)} NEW file(s) seed an RNG from hash():")
        for f in new[:10]:
            ln = next(h for h in hits if h[0] == f)
            print(f"    {f}:{ln[1]}  {ln[2][:78]}")
        print("  Use a stable digest — `zlib.crc32(s.encode())` — or an index. A `seeds=(...)`")
        print("  argument that feeds hash() of a string is decorative, and the round that")
        print("  discovered this had published a CI, an MDE and two verdicts from such a draw.")
        return 1

    print(f"\n  PASS: no NEW unstable seed. {len(frozen)} file(s) frozen as pre-existing —")
    print("  frozen means RECORDED, not forgiven: each still cannot reproduce its own numbers.")
    print("  ⚠ Rules on ONE failure mode. A seed can be stable and still be read from the clock.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
