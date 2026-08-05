# R576 · Fleet size does not separate the cappers — and the data was in an exception I discarded

**Decision this makes safe:** fleet size is **not** the discriminator. **My NEXT line's premise is
dead.**

**WORLD A.** Spawns counted with `sys.addaudithook` on `subprocess.Popen`, 25s window, serial:

| gate | caps | spawns | finished in window |
|---|---|---|---|
| `attack_scope_reaches_the_reader` | no | **5** | ✔ |
| `attack_outcome_variable_declared` | no | **5** | ✔ |
| `attack_no_withdrawn_framings` | no | **7** | ✔ |
| `attack_every_check` | no | **11** | ✔ |
| **`backfilled_findings_are_rederivable`** | **⏱ yes** | **9 ≥** | ✘ |
| `attack_the_suite` | ⏱ yes | 22 ≥ | ✘ |
| `what_did_each_check_actually_read` | ⏱ yes | 60 ≥ | ✘ |

⭐⭐⭐ **`attack_every_check` spawns 11 and finishes; `backfilled_findings_are_rederivable` had
spawned only 9 when the window cut it.** A non-capper exceeds a capper's count, so **spawn count
does not separate the groups** — the kill fired as pre-registered.

⚠ **Capper counts are LOWER BOUNDS**, truncated at 25s. That does not rescue the hypothesis: a lower
bound of 9 against a completed 11 already breaks the ordering **at the point the comparison is made**.

## ⛔ The defect, and it is a new class
The first two runs returned nothing for all three cappers. **`subprocess.TimeoutExpired` carries
`.stderr` with everything the child printed before it was killed — and my handler returned the string
`"TIMEOUT"` and threw it away.**

⭐⭐⭐ **This is not the ninth pattern failure; it is a different kind. The measurement SUCCEEDED and
the error path destroyed it.** A pattern that misses returns a wrong number; **an error path that
discards returns nothing at all, and "nothing" reads as "the instrument could not reach it" rather
than "I dropped it on the floor."**

## Controls
- **Negative** — `statement_provenance` spawns exactly **0**. **PASS.**
- **Positive** — `attack_no_withdrawn_framings` returns **7 > 0**, so the hook is not blind. **PASS.**
  *(This is the control R575 lacked, which is why R575 wrote a verdict under seven zeros.)*
