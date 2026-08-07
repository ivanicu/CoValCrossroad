# R954 · the retraction header, shipped — and the attack found my floor was a count

**PRODUCTION.** R951, R952 and R953 measured the ledger's emptiness and R953 made it admissible with
positive controls on all three probes. This builds the repair those rounds specified.

## What was built

`assurance/a_retraction_declares_its_class.py` — from entry 1388 onward, a retraction must carry
`<!-- retraction: class=<§4 mode|new/<name>>; claim=R<n>; killed_by=R<n> -->`.

`assurance/attack_a_retraction_declares_its_class.py` — 8 vectors, vector pass rate 1.000000, each
run against a temporary ledger containing exactly what the vector plants.

## The load-bearing design choice

The vocabulary has an escape. R952 measured §4's 20 modes covering at most 0.093000 of this ledger,
so a closed vocabulary would force a wrong label on nine entries in ten — converting a silence into a
false attribution. `new/<name>` passes and is counted separately; `new/` with no name fails, so the
escape is visible rather than a loophole.

## The defect the attack found

The floor was set to 1150 because 1,149 entries exist. Entry IDs run 236 to 1387, so 238 committed
entries already sat at or above it and the gate would have retroactively bound them. A count is not
an identifier. Vector 8 caught it: the real ledger returned 1 where an empty population was expected.

## What it does not do

It cannot repair the 1,149 committed entries, and parsing does not mean the class is correct —
nothing mechanical can check that.
