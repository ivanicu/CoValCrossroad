#!/usr/bin/env python3
"""R1042 — the declared field, and this round is the first block that carries it.

R1039 measured that this arc's own IMPOSSIBLE lines fell at 4 of 16 (R1040 made it 5) against R802's
committed 1 of 30, all five sharing one shape. R1041 then closed the retroactive route: fallen and
standing blocks are indistinguishable in committed text (best p 0.0769 against a Bonferroni threshold
of 0.0056, label permutation 0.2637), so triage is out and the remedy is FORWARD-ONLY.

⛔ THIS ROUND IS PRODUCTION, NOT A MEASUREMENT, AND IS LABELLED AS SUCH. It builds the field and makes
   itself the first block to carry it. There is no world-separation here and none is claimed —
   pretending otherwise would be the "closure disguised as discovery" mode.

⭐ WHAT WAS BUILT: `assurance/an_impossibility_names_where_it_would_be_settled.py`. A block declares
   `SETTLES:` plus one tag from a CLOSED SET — HB8's rule (*if it can be an enum, it may NOT be
   text*) and R1029's (*store the field, do not recover it*):
       IN-RELEASE <object>     name the object inside this release that would settle it
       OUT-OF-RELEASE <what>   it genuinely needs something the release lacks
       UNATTACKED              no claim about possibility is being made
   ⚠ `OUT-OF-RELEASE` is the tag the five falsified lines wrongly deserved, so it is the one to be
   most suspicious of when writing it. `UNATTACKED` is the honest default and costs one word.

⛔ AND THE GATE WAS RED-FIRST IN THE ONLY SENSE AVAILABLE. With no round newer than R1041 it exits
   **2 — UNRUNNABLE**, on the suite's own convention (`register_requirements.py`: *"there is no
   evidence the gate works on real entries. Exit 2, never 0"*). This round's own block is what turns
   that 2 into a real check, so the population is n = 1 and the gate becomes runnable BECAUSE of the
   thing it is checking.

ESTIMAND        none. This is Production: a field, a gate, and the first block carrying it.
IDENTIFICATION  N/A — nothing is estimated.
SCOPE           the gate's scope is rounds newer than R1041, stated in the gate itself.
WORLDS          N/A — no fork. Labelling a construction as a frontier action would be the failure
                mode named above, and §0's honest answer is that this could not have come out
                otherwise once R1041 ruled out the retroactive route.
KILL            N/A. The verification is mechanical: the gate must exit 2 with no in-scope round,
                and 0 with this one present and declaring.
POSITIVE CTRL   the gate's own five constructed parser cases — no field, invented tag, tag naming
                nothing, valid IN-RELEASE, valid UNATTACKED — must return their known verdicts, and
                the gate refuses to run if they do not.
NEGATIVE CTRL   an empty in-scope population must exit 2, never 0 — verified before this round's
                block existed, which is the only red-first available for a forward-only check.
PLACEBO         N/A and stated rather than invented: there is no contrast here that must return zero.
NOISE FLOOR     N/A — the check is exact string structure.
MULTIPLICITY    N/A — one gate, one population.
SEEDS           N/A — deterministic.
IMPOSSIBLE      whether a DECLARATION IS TRUE. The enum removes the wording loophole, not the
                mislabelling one: tagging a genuinely external limit `IN-RELEASE` passes. That is the
                same boundary `register_requirements.py` draws for its own field.
                SETTLES: OUT-OF-RELEASE a reader who is not the author — checking a tag is honest
                needs someone without my context, which is door ③ and not a file in this repository.
"""
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GATE = ROOT / "assurance" / "an_impossibility_names_where_it_would_be_settled.py"


def main() -> int:
    if not GATE.exists():
        print("  UNRUNNABLE: the gate is missing. Exit 2, never 0."); return 2
    print("  ⛔ THIS ROUND IS PRODUCTION, NOT A MEASUREMENT. No world-separation is claimed.")
    st = subprocess.run([sys.executable, str(GATE), "--selftest"], capture_output=True, text=True)
    print(st.stdout.rstrip())
    live = subprocess.run([sys.executable, str(GATE)], capture_output=True, text=True)
    print(live.stdout.rstrip())
    ok = (st.returncode == 0 and live.returncode == 0)
    print(f"\n  parser self-test rc={st.returncode} · live rc={live.returncode}  "
          f"{'⭐ the gate is RUNNABLE and GREEN' if ok else '⛔ not green'}")
    print(f"  ⛔ AND IT WAS UNRUNNABLE (rc=2) BEFORE THIS ROUND'S BLOCK EXISTED — that is the only")
    print(f"     red-first a forward-only check admits, and it is the suite's own convention.")
    out = HERE / "results" / "field_and_gate.json"
    out.write_text(json.dumps({
        "round": "R1042", "kind": "PRODUCTION — no estimand, no worlds, no kill",
        "gate": GATE.relative_to(ROOT).as_posix(),
        "tags": ["IN-RELEASE", "OUT-OF-RELEASE", "UNATTACKED"],
        "cutoff": 1041, "selftest_rc": st.returncode, "live_rc": live.returncode,
        "was_unrunnable_before_this_round": True,
        "limitation": "checks that a declaration EXISTS and is well-formed, never that it is TRUE; "
                      "the enum removes the wording loophole, not the mislabelling one",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
