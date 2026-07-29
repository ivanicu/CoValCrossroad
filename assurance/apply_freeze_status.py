"""Stamp the freeze status into every results file of a frozen round.

`covalx/frozen.py` holds the freeze text once, and rounds append it to verdicts
they generate at run time. That fixes the DEFAULT output. It does not fix SWEEP
CELLS -- r26 writes nine results files (metric x min-prompts), r27 five, r28
four -- because refreshing those means re-running each cell, and the queue
freezes further metric sweeps.

Those cells are the problem case: r26's assert "M2: pair identity carries
structure AND that structure is signed", r27's "ACTOR EFFECT, NOT BLOCS" --
exactly what the freeze withdraws. A NO_RERUN note saying "historical artifact"
does not help a reader who opens the file and sees the claim.

So the freeze is stamped in, by the same mechanism and for the same reason as
`apply_outcome_scope.py`: the string lives in ONE place, in code, and this
copies it. It is not a hand-written conclusion -- it is the status of a LINE,
read from the register. The round's own finding is untouched.

Idempotent: a second run changes nothing.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
from covalx.frozen import REGISTRY  # noqa: E402

SEP = " || "


def main() -> int:
    changed = checked = 0
    for round_dir, status in sorted(REGISTRY.items()):
        d = _ROOT / "rounds" / round_dir
        if not d.exists():
            print(f"  ! {round_dir}: no such round -- SKIPPED, and skipped is unstamped")
            continue
        files = [f for f in d.glob("results/**/*.json")
                 if "smoke" not in f.name.lower()
                 and not any(p.startswith("_") for p in f.parts)]
        for f in files:
            try:
                doc = json.loads(f.read_text())
            except json.JSONDecodeError:
                continue
            if not isinstance(doc, dict):
                continue
            # Rounds do not agree on a field name. r01/r23/r26/r27/r28 use
            # "verdict"; r17/r18 use "conclusion"; r16 has NEITHER -- and has a
            # key literally called "blocs_are_real", which puts the frozen claim
            # in the SCHEMA rather than in prose. A stamper that only knew
            # "verdict" reported 20/20 while three rounds in the register were
            # untouched, which is coverage of what it could see rather than of
            # what it was asked to cover.
            field = next((k for k in ("verdict", "conclusion")
                          if isinstance(doc.get(k), str)), None)
            checked += 1
            if field is not None:
                if "FROZEN LINE" in doc[field]:
                    continue
                doc[field] = doc[field] + SEP + status
            else:
                # no prose to append to: carry it as its own top-level field so a
                # reader meets it, and name the schema problem where it applies
                if doc.get("frozen_line"):
                    continue
                # r16's key WAS `blocs_are_real`, which put the frozen claim in the
                # schema where no prose annotation could reach it. I recorded that
                # as an unfixable ceiling; it was not -- r16 is a 190-line CPU
                # round, the key was written in one place and read nowhere, and
                # renaming it IMPLEMENTS the freeze rather than extending the
                # frozen line. Renamed and re-run; this detection is kept so an
                # older artifact still gets the note.
                doc["frozen_line"] = status + (
                    " SCHEMA NOTE: this file predates the 2026-07-28 rename and its key "
                    "`blocs_are_real` asserts the claim the freeze withdraws. The current "
                    "round writes `profile_regret_exceeds_random_by_1.15x`, which is what "
                    "the boolean actually measures."
                    if "blocs_are_real" in doc else "")
            f.write_text(json.dumps(doc, indent=1))
            changed += 1
            print(f"  stamped {f.relative_to(_ROOT)} ({field or 'frozen_line'})")
    print(f"\n{changed} file(s) stamped, {checked} verdict(s) checked "
          f"(idempotent: a second run changes nothing)")
    if changed == 0 and checked:
        print("  Every frozen round's results already carry the freeze.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
