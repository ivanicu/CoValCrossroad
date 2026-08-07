# R482 · The suite has 42 gates and this arc ran four

⚠ **Action class: CLOSURE + PRODUCTION, not Frontier.** It separates no worlds. It protects existing
conclusions by running the checks that already existed, and produces an instrument so the gap cannot
silently reopen. Calling it a discovery would be "closure disguised as discovery".

**The number.** `assurance/` holds 54 files; **42 are gates**. Every round this session ran **four**
and reported *"all four gates PASS"*. **Coverage 9.5%.** There was no Makefile, no runner and no
manifest, so nothing contradicted the reading that the layer was green.

## The census — all 42, whole

| | count | share |
|---|---|---|
| PASS | **25** | 60% |
| FAIL | **9** | 21% |
| UNRUNNABLE (exit 2, empty population) | **4** | 10% |
| TIMEOUT at 45 s | **4** | 10% |

**The four being run were all PASS. Of the 38 that were not, 17 do not return 0.**

⭐ **The unrun subset was not random.** `seed_filter_is_disclosed` FAILS — and it is exactly retraction
304's defect, reporting **7 rounds (36.5%) that analyse only pre-seeded criteria and say so nowhere**.
`next_gradient_labels_its_hypotheses` FAILS — the sentence type behind retractions 300 and 302.
`every_round_reaches_the_readme` FAILS naming **57 rounds that ran and appear nowhere in the top-level
README**, including all eight of this session's.

⚠ **And a FAIL is not always a defect.** `attack_no_withdrawn_framings` reports *"1/1 KNOWN GAPS still
open, as documented"*, and its own comment says a **caught** known-gap would also be a failure — *"in
the other direction"*. **It cannot exit 0 by design.** The runner's three buckets cannot express that,
and the count above is therefore an upper bound on live defects.

## Produced

`assurance/run_all.py` — discovery by a written rule (not a hand list), 0/1/2 classified separately so
UNRUNNABLE never reads as PASS, the pass count printed **beside the denominator**, **exit 2 on an empty
gate population**, and a timeout that kills the gate's **process group**.

`--selftest` plants three shapes and requires correct handling of each:

| control | returned |
|---|---|
| a gate that exits 1 | classified FAIL |
| a gate that exits 2 | classified UNRUNNABLE, never PASS |
| a gate spawning a hanging grandchild | **rc = −1 in 3.0 s** against a 3 s limit |
| an empty gate directory | discovers nothing → `main` exits 2 |

## What it cost — four retractions, none found by a gate

**307** *"52 gates"* was the **file** count; gates are **42**. The unit error the round is about,
inside it, inflating the denominator. `README.md:15`'s *"46 checks"* is `DEFECTS.py`'s defect ledger —
**a number of the right magnitude in the wrong unit survives a sanity check.**

**308** A commit ran a gate loop printing `⛔ EXIT2`×3 and committed anyway. **A `for` loop's output is
not a condition.** The gates re-ran clean; that commit was **correct by luck**. Now `gates && commit`.

**309** `subprocess.run(timeout=)` kills a child, not a process group. A gate ran **98 s against a 75 s
limit** with the census at **0 bytes for 4½ minutes**. ⚠ And the fix shipped **unverified for one
commit** — the selftest never exercised the timeout path.

**310** I attributed 308's transient failures to *"the documented bash wedge"* — a filed, plausible
environment fact. **`ps` showed my own orphans**: a census killed with `pkill -f` left a gate running
**4 m 38 s** past its parent. **The census jumped from 9 to 41 gates the instant they were reaped** —
the diagnosis, confirmed by intervention. ⛔ **A filed environment fact is a hypothesis with a
citation, not a finding, and `ps` costs nothing.**

## Residue

The eight rounds R475–R482 are now written into the top-level README with their numbers and links;
**unmentioned rounds fell 57 → 49**, and the README states the remaining 49 itself.

## Run

    .venv/bin/python assurance/run_all.py --selftest
    .venv/bin/python E05_the_space_of_compilers/A24_what_the_definition_costs/R482_the_suite_has_fifty_two_gates_and_i_ran_four/run.py

Artifact `results/r482_suite_census.json` · 45 s cap per gate · output flushed per gate.
