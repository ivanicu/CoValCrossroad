# R648 · The suite was consistent, I truncated its output, and committing a round moved its numbers

**Decision this makes safe:** whether the assurance suite mis-reports itself. **It does not. I did.**

| | complete capture |
|---|---|
| summary | **PASS 25 of 46 · FAIL 15 · UNRUNNABLE 3 · ERROR 3** |
| labels | LIVE-DEBT **13** + BY-DESIGN **1** + CONTROL-BROKE **1** = **15** ✓ |

**`run_all.py` prints every member of `buckets["FAIL"]` (151–153) and counts `len(buckets['FAIL'])`
(161) — the same list.** The summary *cannot* exceed the listing. **R647 is retracted.**

## ⛔⛔⛔ The discrepancy was my own pipe
I invoked the suite as `run_all.py 2>&1 | tail -25` and read the remnant as complete. The capture
lacks **both** the `ran N gates` header **and** the `META-gates excluded` line, which print *before*
the listing.

⭐ **And R647 saw the truncation without following it home** — it corrected an eyeball count of nine
to a parsed ten and wrote *"off a truncated display"* in its own README, **then treated that same
file as the population.** *The symptom was fixed and the cause left standing, in adjacent sentences.*

⚠ **My parse also over-counted 16 vs 15**: `^\s+FAIL\s` matched the suite's **own section header** —
*"FAIL breakdown — a single count conflates three unlike things:"*. **A pattern that reads the
report's furniture as data.**

## The mis-filed gates are 4 of 13, not 2 of 8
| gate | its own message |
|---|---|
| `code_states_a_bound_the_reader_never_sees` | broke |
| `retired_framing_in_emittable_source` | Traceback |
| `seed_filter_is_disclosed` | SyntaxWarning |
| `source_stamp_is_current` | broke |

**Two I had never seen — they were in the rows my pipe removed.** The earlier *"2 of 8"* had the
right observation and the wrong denominator.

## ⭐⭐⭐ And committing a round about the suite moved the suite's numbers
| | run 1 | run 2 |
|---|---|---|
| PASS | 26 | **25** |
| FAIL | 13 | **15** |
| UNRUNNABLE | 4 | **3** |

**R647's own commit added 4 files / 123 insertions.** ⚠ **Not non-determinism** — the tree differed
and the diff is in the git log. **This is R636's mechanism arriving on the instrument that measures
the corpus: the corpus is the population, and every round adds to it.**

**IMPOSSIBLE, named:** the classifier reads **messages**, so *"the gate broke"* is inferred from
output text. **A gate that fails silently while broken is invisible**, so 4 is a **lower bound**.

## The sentence I can no longer write
> *"the suite's summary disagrees with its own listing."*

**It agrees exactly.** I compared a complete summary against a listing I had cut myself, and wrote a
retraction accusing a correct tool.

## NEXT
The standing repair is mechanical and belongs in the operating rules, not in resolve: **never pipe an
instrument's output through a truncating filter before parsing it — capture whole, then slice.**
Three rounds in this arc were spent on truncations I introduced (`[:12]`, `head -3`, `tail -25`).
**Check whether any committed round's `run.py` pipes a subprocess through `head`, `tail` or a slice
before parsing** — because if the pattern is in the corpus rather than only in my shell commands,
the same error is waiting in code that will be re-run.
