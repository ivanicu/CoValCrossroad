# R483 · Nine FAILs were three unlike things

⚠ **Action class: CLOSURE + PRODUCTION.** No fork separated.

**The decision this made safe.** Whether R482's *"9 FAIL"* is a debt of nine defects. **It is not.**

| kind | count | meaning |
|---|---|---|
| **LIVE-DEBT** | **6** | real, payable, all pre-existing |
| **BY-DESIGN** | 1 | `attack_no_withdrawn_framings` — *"1/1 KNOWN GAPS still open, as documented"*, and its own comment says a **caught** known-gap would also fail. **It cannot exit 0.** |
| **CONTROL-BROKE** | 1 | `next_gradient_labels_its_hypotheses` — *"a control misbehaved; the counts above are silence."* **Says nothing about the repo.** |
| **PASS** | 1 | `source_stamp_is_current` — **paid during this round** |

⭐ **The payment was one line.** The ratchet said *"FROZEN LIST IS STALE — 1 round in it is now FRESH:
`R130_judge_gauge`. Remove them. **A frozen list that outlives its reason is the confession this check
was built to replace.**"* Removed, `count` kept as a checksum on the list (31 → 30), gate now exits 0.

## Produced

A fourth bucket in `run_all.py`, declared a **PROXY sound in one direction**: it reads *messages*, so
it may only **demote** a FAIL out of LIVE-DEBT, never promote one in. Its selftest uses **the two real
messages that motivated it**, a live one, and the empty string — because silence must classify as
LIVE-DEBT, never as an acquittal.

⚠ **And its first version was fed the wrong object** (retraction 311): `classify_fail(msg)` read the
one-line display extract, and `next_gradient_labels_its_hypotheses`'s extract is *"POSITIVE CONTROL
the two NEXT blo…"* while the identifying phrase is three lines later. **The one gate that motivated
the bucket would have been misfiled by the bucket.** Fixed by computing the kind on the **full output
at source** and carrying it.

## Run

    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R483_nine_fails_were_three_unlike_things/run.py
