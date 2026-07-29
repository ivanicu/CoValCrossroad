"""A round stamps the sha256 of its own source into its output, so an artifact cannot outlive the
code that claims to have produced it.

Deliberately duplicated rather than imported from the sibling assurance repo: a round in this
repository must not depend on a path outside it. Three lines of duplication is the correct price for
a package that runs on its own. The auditing gate lives elsewhere and only ever READS json, so the
two copies never have to agree on anything but the key name and the algorithm.

WHY, in one sentence: the two-hashseed reproducibility gate runs a file twice and compares the two
fresh runs to EACH OTHER, so it certifies determinism and never currency, and a round patched after
it ran passes that gate forever while its persisted numbers no longer exist in any output.
"""
from __future__ import annotations

import hashlib
import pathlib

STAMP_KEY = "source_sha256"


def stamp(source_file: str) -> dict:
    """Merge into a round's output dict as `**stamp(__file__)`."""
    p = pathlib.Path(source_file).resolve()
    return {STAMP_KEY: hashlib.sha256(p.read_bytes()).hexdigest(), "source_name": p.name}
