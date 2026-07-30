"""Where a round lives, asked once, so 25 gates stop hard-coding its depth.

Rounds moved from `rounds/rNN_name/` into `rounds/NN_campaign/rNN_name/` so that 113 of them read as
12 experiments rather than one flat wall. Every path built as `rounds/<round>` broke, and the failure
mode was quiet in the worst way: a gate globbing `rounds/*/` still matched -- it just matched the
twelve BATCH directories and reported twelve rounds with no results, i.e. a completeness verdict over
the wrong population. Seven gates did exactly that.

So the depth is expressed once, here, and a gate that asks this module cannot be wrong about it again.
Fixtures get a batch of their own (`_fixtures/`) for the same reason: an attack that plants a fake
round has to plant it where the real ones are, or the attack silently tests nothing.
"""
from __future__ import annotations

import pathlib
import re

ROUND_RE = re.compile(r'^r\d+_')
GLOB = "rounds/*/r*"
FIXTURE_BATCH = "_fixtures"


def iter_round_dirs(root: pathlib.Path):
    """Every real round directory, ordered by round number. Batch dirs are not rounds."""
    out = [p for p in root.glob("rounds/*/*") if p.is_dir() and ROUND_RE.match(p.name)]
    return sorted(out, key=lambda p: int(p.name.split("_")[0][1:]))


def round_dir(root: pathlib.Path, name: str):
    """Resolve a round by BARE name (`r31_within_person`) without knowing its batch. Returns None if
    no such round -- callers that treat a registry entry's absence as a loud failure depend on the
    difference between 'not found' and 'found in an unexpected place'."""
    hits = [p for p in root.glob(f"rounds/*/{name}") if p.is_dir()]
    return hits[0] if hits else None


def fixture_dir(root: pathlib.Path, name: str) -> pathlib.Path:
    """Where a planted fake round must go to be visible to the same globs the real ones are."""
    return root / "rounds" / FIXTURE_BATCH / name
