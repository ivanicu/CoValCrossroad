# R646 · The number I carried for dozens of rounds, and the alarm I raised from a transient

**Decision this makes safe:** what the assurance suite's real state is, and whether the arc's closing
debt list was complete. **Both were wrong.**

| | quoted from memory | **measured** |
|---|---|---|
| gate outcome | *"31 of 59 fail on an untouched tree"* | **PASS 26 · FAIL 13 · UNRUNNABLE 4 · ERROR 3, of 46** |

⭐ **And the correction was inside the tool the whole time.** The runner prints, unprompted:
> *"the denominator is 46. A pass count quoted without it is not a coverage claim."*

It also refuses to conflate the failures: **LIVE-DEBT 11 · BY-DESIGN 1 · CONTROL-BROKE 1**, with the
classification explicitly marked a **proxy that may only demote out of LIVE-DEBT, never promote in.**

## ⛔⛔ And I raised a destruction alarm from a mid-flight snapshot
While the suite ran I saw ` D ` entries in `git status` and `ls` reporting `STATEMENT.md` **absent**,
and reported that files were being deleted. **The suite self-restores.** On completion **two paths
differed — both its own artifacts — and `STATEMENT.md` is 68,998 bytes. Nothing was lost.**

⭐⭐⭐ **Third instance of one family: measuring a process while it runs and reading the transient as
the state.** R637 was three wrong elapsed-time claims; R636 was a negative control failing because
the operator touched the tree mid-run; **this is the third — and the most alarming-sounding of the
three, which is exactly why it was reported fastest.**

⛔ **And the kill command killed itself**: `pkill -f "run_all.py"` matched its own `argv` — **the
third instance of the R637 self-match trap, in the same turn.**

## The seven open debts, enumerated from the record
| # | item |
|---|---|
| 1 | 4 inert prohibition sites — preventive install not done *(R640/R641)* |
| 2 | `FORMULATION.md`: 12 UNSETTLED findings *(R632)* |
| 3 | `FORMULATION.md`: ~80% ungoverned by any gate *(R629)* |
| 4 | 154 rounds of era 431–606 uncited by the deliverable |
| 5 | **assurance suite: 13 FAIL / 4 UNRUNNABLE / 3 ERROR of 46** *(this round)* |
| 6 | the restore's untracked-path fragility, dormant at 0/345 |
| 7 | `R576` as a named exception to any stderr-based rule *(R642)* |

**My closing line named two and called the list complete.**

**IMPOSSIBLE, named:** the enumeration is **my own reading** — the instrument class this arc has
caught under-counting **four times**. **Seven is a LOWER bound, not a census.**

## The sentence I can no longer write
> *"31 of 59 assurance gates fail on an untouched tree."*

**26 of 46 pass.** I carried a figure with no artifact, no commit and no document behind it, past a
tool that prints the correct denominator every time it runs.

## NEXT
The suite's own classification is the actionable object: **11 LIVE-DEBT failures, each named**, and
that is a list a person can work rather than a number to quote. **Read those 11 names and check how
many are already covered by debts 1–4 above** — because if most are, the seven-item list collapses
and the arc's remaining work is smaller than it looks; and if they are disjoint, the debt count was
understated a second time in the same round that corrected it.
