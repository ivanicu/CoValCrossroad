# R570 · The suite's failure count is not reproducible, in either mode

**Decision this makes safe:** how any suite count may be quoted. **It may not be quoted as a
measurement.**

**WORLD B.**

| mode | PASS | FAIL | of |
|---|---|---|---|
| serial, 1 worker | **30** | **9** | 46 |
| serial, 1 worker *(repeat)* | **29** | **10** | 46 |
| parallel, 12 workers | **26** | **13** | 46 |

⭐⭐⭐⭐ **Two serial runs of the same suite on the same tree disagree.** So the count is
nondeterministic **at one worker**, and my concurrency-race explanation — the one this round was
built to confirm — **is refuted as sufficient.** What survives: **parallelism amplifies it
(13 > 10 > 9); it does not cause it. Mechanism: UNVERIFIED.**

## What this retracts
**Every failure count quoted this session was an unlabelled draw from a distribution**, not a
measurement: R561's *"9 live-debt gates"*, R569's *"15 FAIL"*, and the *"13 live"* I reported two
rounds ago. **They are consistent with each other only because they are samples of the same unstable
quantity.**

⚠ **n = 2 serial, n = 1 parallel.** The **spread** is established; **the distribution is not**, and
the run that would have settled it timed out at 9m40s. Reported rather than rounded up.

## Controls
- **The comparison is its own control**: two runs of the *identical* command differ, which no
  hypothesis about *modes* can explain away.
- ⛔ **This round's own hypothesis was refuted by its own data** — the second serial run.

⭐ **The prior rounds' numbers were not wrong to record; they were wrong to state without a run
count.** A suite verdict is a draw, and this suite has never reported how many times it was drawn.
