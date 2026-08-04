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

# ⚠ THIRD LAYOUT, 2026-08-02: rounds moved again, into the EAR tree E<epoch>/A<arc>/R<round>,
# and the leaf is now capital R. This is the exact failure the docstring above describes, one
# level deeper -- which is why the depth is expressed HERE and nowhere else. Both cases are
# accepted so that a stale reference to `r019_x` still resolves to `R019_x`.
ROUND_RE = re.compile(r'^[Rr]\d+_')
GLOB = "E*/A*/R*"
# Named to LOOK LIKE A CAMPAIGN on purpose. Every glob is anchored on [0-9][0-9]_* now, because at the
# repository root a bare */ would match data/, covalx/, assurance/ and .venv/. Anchoring is correct and
# it has a cost: a fixture batch called "_fixtures" is invisible to the very globs it must be seen by,
# so three attack harnesses planted fixtures nothing could find and reported 0 vectors caught. The
# batch therefore carries a two-digit prefix, and 99 keeps it last in any sorted listing.
FIXTURE_BATCH = "E99_fixtures/A01_planted"


def iter_round_dirs(root: pathlib.Path):
    """Every real round directory, ordered by round number. Batch dirs are not rounds."""
    out = [p for p in root.glob("E*/A*/*") if p.is_dir() and ROUND_RE.match(p.name)]
    return sorted(out, key=lambda p: int(p.name.split("_")[0][1:]))


def round_dir(root: pathlib.Path, name: str):
    """Resolve a round by BARE name (`r31_within_person`) without knowing its batch. Returns None if
    no such round -- callers that treat a registry entry's absence as a loud failure depend on the
    difference between 'not found' and 'found in an unexpected place'."""
    want = name.lower()
    hits = [p for p in root.glob("E*/A*/*") if p.is_dir() and p.name.lower() == want]
    return hits[0] if hits else None


def fixture_dir(root: pathlib.Path, name: str) -> pathlib.Path:
    """Where a planted fake round must go to be visible to the same globs the real ones are.

    REFUSES a name the globs cannot match. Every glob is anchored `[0-9][0-9]_*/r*/`, so a fixture
    called `_attack_tmp` is invisible and the harness that planted it reports "0/5 vectors caught" --
    which reads as a gate that fails to catch things rather than an attack that was never planted.
    That happened to three harnesses at once. A loud refusal is the only acceptable behaviour here,
    because the silent form is indistinguishable from a real negative result."""
    # The requirement is exactly the glob's: `[0-9][0-9]_*/r*/`, so the name must START WITH r.
    # My first version of this guard demanded r + DIGITS and rejected `rZZ_plant`, a placeholder one
    # harness had used for years -- a guard stricter than the thing it guards, which breaks working
    # callers to prevent a fault they never had.
    # ⚠ REPAIRED at R340. This required only `startswith("r")` while discovery requires
    # ROUND_RE = ^[Rr]\d+_ , so `rZZ_plant` PASSED this guard and was then invisible to
    # iter_round_dirs. The comment below justified the loosening as "a guard stricter than the
    # thing it guards" -- but ROUND_RE IS the thing it guards, and it demands digits. Loosening
    # did not spare the caller, it blinded it: artifacts_are_internally_coherent's positive
    # control has been reporting outside=[] contradict=[] -> FAIL ever since, which is the
    # honest form of the failure and is how it was found. The guard now enforces EXACTLY the
    # discovery contract, because a planting guard looser than the discovery it plants for is
    # the one shape that cannot be detected from the inside.
    if not ROUND_RE.match(name):
        raise ValueError(
            f"fixture name {name!r} must match ROUND_RE ^[Rr]\\d+_ to match the EAR-anchored glob "
            f"E*/A*/R*/; anything else is planted where nothing can find it, and the harness "
            f"then reports zero vectors caught instead of an error")
    return root / FIXTURE_BATCH / name
