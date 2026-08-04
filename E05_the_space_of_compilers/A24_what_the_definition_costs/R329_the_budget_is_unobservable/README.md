# R329 — the budget I matched on is unobservable, and the bracket straddles the crossing

**Decision this makes safe:** whether R328's budget-matched admission of `topw_k4` may be published.
**It may not.** `coval_core` survives untouched; **`topw_k4` is UNVERIFIED at clause ② under
budget-matching — not refuted, not established.**

## The gauge test that started it — three lines, zero compute

> **Transformation:** commit N more rule × k cores under `corebench/results/`, do not touch `topw_k4`.
> **Property invariant?** **Yes** — its selected criteria, its npz, its A2 vector are byte-identical.
> **Measurement invariant?** **No** — R328 counts committed siblings as its budget, matches the
> reference to that count, and reads the verdict off best-of-m. More siblings → higher reference →
> the verdict flips.

**Measurement varies where the property does not ⇒ the budget-matched verdict is a fact about the
repository, not about the arm.** R328 called the count a lower bound and signed the error direction;
that part was right. The defect is that it then offered **"6× headroom"** as reassurance **without
ever asking how large the search space was.**

## W-STRADDLES

| enumeration | U | U/L | `topw_k4` in-sample (crossing = 64) |
|---|---:|---:|---|
| U1 rules-used × k-used | 35 | 3.2× | below |
| U2 all k-rules × k-used | 56 | 5.1× | below |
| **U3 all k-rules × k∈1..16** | **128** | 11.6× | **at/above** |
| **U4 U3 + fit-parity variants** | **256** | 23.3× | **at/above** |

**2 of 4 defensible enumerations reach the crossing; 2 do not.** The verdict is fixed by an
unobservable — how large a rule family was actually searched — and not by the data.

`coval_core` is untouched: bracket **[1, 1]**, crossing at m=512 in-sample and never on the grid
held-out. The asymmetry R328 found is real; only the arm on the searched side is unreadable.

## ⚠ And R328's own artifact already contained the second defect

| arm | mode | first fail | last BEATS | monotone | sign changes | cells in [0.95, 1.05] |
|---|---|---:|---:|---|---:|---:|
| `coval_core` | in-sample | 512 | 256 | ✓ | 1 | 1 |
| `coval_core` | held-out | *none* | 1820 | ✓ | 0 | 0 |
| `topw_k4` | in-sample | 64 | 32 | ✓ | 1 | 1 |
| **`topw_k4`** | **held-out** | **512** | **1024** | **✗** | **3** | **5** |

`first m that fails` is a valid summary **only if the verdict is monotone in m**. For
`topw_k4|held-out` it is not — the verdict crosses 1.00× three times, with five cells sitting inside
`[0.95, 1.05]`. **R328's README quoted `47×` for that mode on the strength of the first of several
sign changes.** `min/max of N draws quoted as an interval`, in a new costume. **Retracted.**

## Controls

| control | result |
|---|---|
| **positive** — every enumeration must generate all 11 committed cells | **4 of 4 PASS**, none missing |
| **positive @ g=0** — the *empty* enumeration run through the same code | correctly **fails** |
| **sham** — 128 cells, same size as U3, rule names that don't exist | correctly **fails** |
| **negative** — the same bracket applied to `coval_core` | **does not straddle** (crossing 512 > max enumeration 256) |
| **placebo** — R328's `crossing` re-derived from its own `cells` | **identical** |
| noise floor | cells within `[0.95, 1.05]` of the boundary, reported per mode |
| multiplicity | 16 lookups printed; **no new test — R328 spent the p-values and they are not re-spent** |

### ⚠ Both of those controls were vacuous in v1, and the negative one gated the kill

`neg_ok = True` — **a literal, with a comment explaining why it could not fail.** §4 row 1, in the
flattering direction, and third mis-specified control in three consecutive rounds. `empty_fails =
bool(set(committed) - set())` was the same shape: `True` for any non-empty repo.

**Repairing the negative control produced a finding v1 could not have had.** The right question was
never *"does `coval_core` move?"* — it was **"is straddling a property of the arm's search, or of the
bracket's width?"** Applied to `coval_core`, the identical bracket does **not** straddle: its
crossing sits at 512, above the largest enumeration at 256. **So straddling localises to the searched
arm**, which is what makes W-STRADDLES a statement about `topw_k4` rather than about the design.

## What this does NOT say

**`topw_k4` is not refuted.** UNVERIFIED never becomes OVERTURNED — the budget-matched test cannot
decide it, which is a statement about the test. Its clause-② standing under the campaign's *published*
references (R326) is unchanged: 1.19× at `generic` k=4, 0.92× at the best held-out of 1,820.

## ⚠ The register gains an entry

> **`budget-matched clause ② for a rule-derived arm` — structurally impossible here.**
> Requires a search log the campaign never kept, or a rule family pre-registered before the arms
> were scored. **Counting committed artifacts is the flattering substitute, and it is what R328 did.**

## Scope

The 11 committed deterministic rule × k cores · the reachable grid of `corebench/select_core.py`,
read from its own argparse `choices` · R328's committed 90-cell verdict grid, **reused not
recomputed** · 968 prompts, A2 vs sampled annotator, k=4 arms.

**Seeds: none, and that is stated rather than faked** — the estimand is a count and a lookup into a
committed grid. R328 carries the three seeds this reuses.

## What this cannot do

Recover the actual search. There is no log. The bracket is what partial identification licenses, and
a point estimate inside it would be the thing this round exists to refuse.
