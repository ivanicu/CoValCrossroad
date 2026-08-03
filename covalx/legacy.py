"""Resolve a round directory by ROUND ID, so a reorganisation cannot break a citation again.

WHY THIS EXISTS. R315 measured that 25 of 278 probed rounds could not resolve their inputs, and
the largest single cause was rounds naming a sibling by a path that encodes the epoch and arc:

    ROOT / "E01" / "R04_rebuild_satisfaction" / "results" / "a04_full.npz"

That was correct when written. The EAR reorganisation renamed `E01` to
`E01_the_rubric_was_the_object` and inserted an arc level, and nothing noticed for weeks because
nothing re-runs rounds. Seven distinct legacy targets are now dead — `E01/`, `rounds/` and `E04/`
prefixes — and R315's count is a FLOOR, because a probe records only the FIRST failing read and a
round that dies early never reaches its second broken path.

THE FIX IS TO STOP ENCODING LOCATION. A round id is stable by construction: `EAR.md` requires
every id to be unique project-wide and forbids reuse, which is exactly the property a key needs.
Epoch and arc names are not stable — an epoch is renamed the moment its ontology shifts, which is
what an epoch IS.

    from covalx.legacy import round_dir
    base = round_dir("R04") / "results"

⚠ AND IT REFUSES RATHER THAN GUESSES. Two rounds matching one id is a violation of EAR's
uniqueness rule and a silent pick would resolve to whichever the filesystem listed first — the
same class of defect as the one this module exists to remove. Zero matches raises too: a resolver
that returns a plausible path for a round that does not exist would push the failure downstream to
a FileNotFoundError with no explanation, which is what we already had.
"""
from __future__ import annotations

import functools
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
_ID = re.compile(r"^[Rr](\d+)$")


@functools.lru_cache(maxsize=None)
def _index() -> dict[str, pathlib.Path]:
    out: dict[str, list[pathlib.Path]] = {}
    for p in ROOT.glob("E*/A*/R*"):
        if not p.is_dir():
            continue
        m = _ID.match(p.name.split("_")[0])
        if m:
            out.setdefault(f"R{int(m.group(1))}", []).append(p)
    return {k: v for k, v in out.items()}


def round_dir(round_id: str) -> pathlib.Path:
    """`round_dir("R04")` -> the one directory whose id is 4, wherever it now lives.

    Accepts `R4`, `R04`, `r04`. Raises on 0 or >1 matches; never guesses.
    """
    m = _ID.match(str(round_id).strip())
    if not m:
        raise ValueError(f"not a round id: {round_id!r} (expected e.g. 'R04')")
    key = f"R{int(m.group(1))}"
    hits = _index().get(key, [])
    if len(hits) == 1:
        return hits[0]
    if not hits:
        raise FileNotFoundError(
            f"no round directory with id {key} under {ROOT}/E*/A*/. "
            f"If it was archived, read it from _archive/ explicitly and say so in the round.")
    raise RuntimeError(
        f"{len(hits)} directories claim id {key}: {[str(h.relative_to(ROOT)) for h in hits]}. "
        f"EAR requires ids to be unique project-wide; fix the duplicate rather than picking one.")


def round_results(round_id: str, filename: str | None = None) -> pathlib.Path:
    """The `results/` directory of a round, or a named file inside it."""
    d = round_dir(round_id) / "results"
    return d / filename if filename else d
