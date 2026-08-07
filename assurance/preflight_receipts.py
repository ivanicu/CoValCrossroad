#!/usr/bin/env python3
"""assurance/preflight_receipts.py -- how many commits carried a preflight receipt.

WHY. `preflight.py` is a habit with a visible bypass, not a constraint: `git add` still works and a
pre-commit hook cannot help, because this repo commits with `--no-verify` by standing rule. R1018's
NEXT said the only way to learn whether "an action rather than an omission" changes behaviour is to
COUNT later commits that went through it against those that did not -- and that the counting has to
START rather than be claimed.

⭐ THE RECEIPT IS SELF-EVIDENCING. preflight appends one line to
`assurance/results/preflight_log.jsonl` and stages it WITH the paths it cleared, so the receipt lands
inside the commit it gated. This check asks, per commit since the epoch: does it touch that log?

⚠⚠ WHAT IT CANNOT DO, STATED BEFORE THE NUMBER.
  * a receipt can be written BY HAND -- this detects the ordinary case, never a forgery;
  * a commit that touches ONLY the log is not evidence of anything, and is reported separately;
  * commits BEFORE the epoch have no receipt because the mechanism did not exist, which is not a
    bypass. The epoch is therefore printed with every count, and a rate quoted without it would be
    the same error as a share without its denominator.

EXIT   0 always -- this is a REPORT, not a gate. It has no failing side, and pretending otherwise
       would make a counter look like a constraint, which is the confusion the whole line is about.
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = "assurance/results/preflight_log.jsonl"


def sh(*a):
    return subprocess.run(a, cwd=ROOT, capture_output=True, text=True)


def main() -> int:
    first = sh("git", "log", "--reverse", "--format=%H", "--", LOG).stdout.split()
    if not first:
        print("  no commit has ever carried a preflight receipt. The counting starts with the next "
              "one; there is no rate to report and none is invented.")
        return 0
    epoch = first[0]
    rng = f"{epoch}~1..HEAD" if sh("git", "rev-parse", f"{epoch}~1").returncode == 0 else epoch
    lines = sh("git", "log", "--format=%H %s", rng).stdout.splitlines()
    with_r, without_r, log_only = [], [], []
    for line in lines:
        sha, _, subj = line.partition(" ")
        files = [f for f in sh("git", "show", "--name-only", "--format=", sha).stdout.split()
                 if f.strip()]
        if not files:
            continue
        if LOG in files:
            (log_only if files == [LOG] else with_r).append((sha[:8], subj[:70]))
        else:
            without_r.append((sha[:8], subj[:70]))
    tot = len(with_r) + len(without_r) + len(log_only)
    print(f"  epoch: the first commit carrying a receipt is {epoch[:8]}")
    print(f"  commits since (inclusive): {tot}")
    print(f"    WITH a receipt      {len(with_r):>3}")
    print(f"    WITHOUT             {len(without_r):>3}")
    print(f"    receipt-only        {len(log_only):>3}  (not evidence either way)")
    for tag, rows in (("with", with_r), ("without", without_r)):
        for sha, subj in rows:
            print(f"    {tag:<8}{sha}  {subj}")
    if tot <= 1:
        print("\n  ⚠ ONE COMMIT IS NOT A RATE. The counting has started; there is nothing to "
              "conclude yet, and saying so is the report.")
    print("\n  ⚠ A receipt can be written by hand, and commits before the epoch have none because "
          "the mechanism did not exist. Neither is a bypass.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
