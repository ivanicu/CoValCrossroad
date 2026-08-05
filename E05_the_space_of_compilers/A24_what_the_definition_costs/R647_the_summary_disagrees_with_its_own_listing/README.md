# R647 · The suite's summary disagrees with its own printed listing, by exactly three

**Decision this makes safe:** how many live debts the assurance suite actually reports. **Six that
can be named, not eleven.**

| | printed | summary claims | Δ |
|---|---|---|---|
| FAIL | **10** | 13 | **+3** |
| LIVE-DEBT | **8** | 11 | **+3** |
| ERROR | 3 | 3 | 0 |
| UNRUNNABLE | 4 | 4 | 0 |

**The +3 is uniform and equals the ERROR/timeout count exactly** — so the likely reading is that the
three 90-second timeouts are counted as FAIL in the summary and printed under ERROR in the listing.
⚠ **That is a hypothesis from an arithmetic coincidence, not a reading of the code, and it is
labelled as one. The discrepancy is MEASURED; its cause is GUESSED.**

## ⛔ Two of the eight printed LIVE-DEBT entries are broken gates, visible in their own messages
| entry | its own message |
|---|---|
| `retired_framing_in_emittable_source` | **`Traceback (most recent call last):`** |
| `seed_filter_is_disclosed` | **`SyntaxWarning: invalid escape sequence '\)'`** |

**Neither is a debt in the deliverable; both are gates that crashed.** So **genuine live debts among
the printed rows are 6 of 8.**

⭐ **And the suite predicted this in its own caveat** — the classifier *"may only DEMOTE out of
LIVE-DEBT, never promote in"*, so LIVE-DEBT is its **catch-all and over-reports by construction.**
**The caveat was printed, correct, and quoted-past by me one round ago.**

## ⛔⛔ And I committed the same error while reporting it
I counted **nine** FAIL rows by eye off a truncated display; the parse says **ten**. ⭐ *An eyeball
count of a display is the exact failure this round is about, and it survived into the round's own
first reading.*

## ⛔ Check #248
*"Eleven live-debt failures, **each named**"* — the suite printed a **breakdown count** and I inferred
the names from it. It does name them, so the concern was unfounded — **but checking produced this
round's finding, which asserting would not have.**

## The sentence I can no longer write
> *"eleven live-debt failures, each named — a list a person can work."*

**Eight are named, six are real, and three are counted but never shown.**

## NEXT
The six genuine live debts are named and small enough to read, but **the three counted-and-unshown
FAILs are the sharper object**: a summary can only be trusted where it can be checked against a
listing, and here it cannot. **Read `run_all.py`'s reporting path and determine whether the three are
the timeouts double-counted or three genuinely suppressed rows** — because the first is a display bug
and the second means the suite has been under-reporting its own failures to every round that ever
quoted it.
