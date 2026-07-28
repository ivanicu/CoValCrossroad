"""Fetch the CoVal public release and verify it byte-for-byte.

This repository does not redistribute the dataset. It records the exact hashes
every result was computed from, so a reproduction either gets the same bytes or
fails loudly. A silent mismatch is the failure mode this file exists to prevent.

    python data/fetch.py

CoVal is published by OpenAI under CC BY 4.0 at huggingface.co/datasets/openai/coval
"""
from __future__ import annotations

import hashlib
import sys
import urllib.request
from pathlib import Path

REPO = "https://huggingface.co/datasets/openai/coval/resolve/main"

# hashes recorded from the release the results in this repo were computed on
FILES = {
    "comparisons.jsonl":
        ("e107b7d233baedbc8c1b9c3f9aef9739592b93f6f202b9e4503b9cd3ca00d759", 18403444),
    "conversation_rubrics.jsonl":
        ("1ecc5f54d475f288edf6508ed64b5f89e9b40cbd6555acc107316721714e2979", 11418028),
    "merged_comparisons_annotators.jsonl":
        ("9f3225ef03decd164008bca143053438bef4fa3bb8c032c79ff07429490740b5", 26009185),
    "annotators.jsonl":
        ("6d99f1ba780da88eafb9f63857d0f88aa0be683c807ff536768409f92bc96057", 16044141),
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    here = Path(__file__).resolve().parent
    bad = 0
    for name, (want, size) in FILES.items():
        dest = here / name
        if not dest.exists():
            print(f"downloading {name} ...", flush=True)
            urllib.request.urlretrieve(f"{REPO}/{name}", dest)
        got = sha256(dest)
        if got == want:
            print(f"  OK       {name}  {dest.stat().st_size:,} bytes")
        else:
            bad += 1
            print(f"  MISMATCH {name}\n    expected {want}\n    got      {got}")
            print("    The release has changed since these results were computed. "
                  "Every claim in assurance/ is scoped to the hashes above and must "
                  "be recomputed, not carried over.")
    if bad:
        print(f"\n{bad} file(s) do not match the recorded release.")
        return 1
    print("\nall four files match the recorded release")
    return 0


if __name__ == "__main__":
    sys.exit(main())
