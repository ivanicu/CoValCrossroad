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

# The dataset CARD, which this repository cites as evidence and which the four
# files above do not contain. Entries 74, 88 and 90 rest on it: the "in parallel"
# provenance of the seeded criteria (L73), the personal-vs-world ranking
# instructions, and the recruitment / onboarding-quiz / compensation protocol.
# It was gitignored and absent from FILES, so a reproducer following the README
# could obtain every number and none of the text those readings depend on.
#
# On the Hub a dataset's card is README.md at the repo root, so it is fetched
# from there and written under its local name. VERIFIED 2026-07-29: that URL
# returns HTTP 200, 27,509 bytes, sha256 92ba4a96... -- byte-identical to the
# local copy, so the quotations entries 74, 88 and 90 rest on are checkable
# against the live source and not only against a file on this disk.
CARD_LOCAL = "DATASET_CARD.md"
CARD_REMOTE = "README.md"
CARD = ("92ba4a96087b719e80ccbd0803a6d9bd6ab0582d963e95c20579efbb5a769de0", 27509)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    here = Path(__file__).resolve().parent
    bad = 0
    targets = {**FILES, CARD_LOCAL: CARD}
    for name, (want, size) in targets.items():
        dest = here / name
        remote = CARD_REMOTE if name == CARD_LOCAL else name
        if not dest.exists():
            print(f"downloading {name} ...", flush=True)
            try:
                urllib.request.urlretrieve(f"{REPO}/{remote}", dest)
            except Exception as e:
                print(f"  COULD NOT FETCH {name} from {REPO}/{remote}: {e}")
                if name == CARD_LOCAL:
                    print("    The card is the dataset page at "
                          "huggingface.co/datasets/openai/coval -- save it as "
                          f"data/{CARD_LOCAL} and re-run; the hash below still checks it.")
                bad += 1
                continue
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
    print(f"\nall {len(targets)} files match the recorded release")
    return 0


if __name__ == "__main__":
    sys.exit(main())
