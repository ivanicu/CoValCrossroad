# R571 · The timeout hypothesis is refuted, and three gates do not terminate

**Decision this makes safe:** the flip is **not** a timeout-boundary artifact. **Mechanism still
UNVERIFIED.**

**WORLD A.** Timed serially on an unloaded machine:

| | |
|---|---|
| `backfilled_findings_are_rederivable` | **90.09s — cap** |
| `attack_the_suite` | **90.09s — cap** |
| `what_did_each_check_actually_read` | **90.00s — cap** |
| next slowest (`attack_no_withdrawn_framings`) | **6.18s** |
| gates in **[10s, 90s)** | **0** |
| gates in **[30s, 90s)** | **0** |

**Nothing sits within 84 seconds of the boundary.** Load cannot carry a 6-second gate past 90, so
the timeout **cannot** explain the 9 → 13 spread. **The hypothesis this round was built to confirm
is dead.**

## ⭐ What the gap establishes instead
**Those three gates are not slow — they hang.** All three hit the cap **exactly** (90.09, 90.09,
90.00) while the other 43 finish in **under 7 seconds**. A distribution with 43 points below 6.2s
and 3 pinned at the limit is not a runtime spread; **it is 43 terminating processes and 3
non-terminating ones.** `ERROR 3` is a hang, not a tuning problem — a distinct, actionable defect
from the flip.

## ⚠ What is still NOT established
Check #171 asked for **a gate that flips between two runs of the SAME mode on the SAME tree.**
**I still do not have one.** `code_states_a_bound_the_reader_never_sees` reads `rc=0` here and was
`rc=1` with a traceback in an earlier listing — **but the tree had changed between them**, so it is
not the object the question asked for. **Naming it as the flipper would be exactly the shortcut
these three refutations have been protecting against.**

## Controls
- **Positive** — the three known-timeout gates are observed at the cap, so the timer measures what
  `run_all` measures. **PASS.**
- **Negative** — a known-fast gate reads fast (`statement_provenance` < 1s). **PASS.**
