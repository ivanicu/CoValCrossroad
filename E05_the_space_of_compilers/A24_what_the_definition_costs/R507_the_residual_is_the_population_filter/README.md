# R507 · The residual was arm coverage, not the ranking filter — and the filter turned out to be a no-op

**Decision this makes safe:** whether the last unexplained number in the ceiling chain
(**0.6220** vs R479's **0.6132**) hides a defect. **It does not.** The chain is closed.

## What was measured

| population | n | ranker ceiling | seed range |
|---|---|---|---|
| **all ≥3-ranking prompts — R479's actual population** | **1078** | **0.6174** | [0.6143, 0.6189] |
| only prompts `oracle_k4` covers — R504–R506's population | 968 | **0.6218** | [0.6193, 0.6242] |

**On R479's own population the ceiling reproduces at |Δ| = 0.0042, inside R479's stated resolution of
0.0093.** The residual was **my restriction to `oracle_k4`'s 968 prompts**, and nothing else.

⭐ **R506's comparison remains correct — because of that restriction, not despite it.** Comparing an
arm to a ceiling requires both sides on the same prompts, which is exactly what it did.

## ⛔ The hypothesis this round was built on died to its own positive control

The round opened on `R479:91` — `pids = [... if len(v) >= 3]` against my `>= 2` — and predicted the
filter explained the gap. **Swept: n = 1078 at m = 1, 2 *and* 3.** Every prompt in the release carries
at least three rankings, so **R479's filter excludes nothing. It is a no-op.**

The control that required the sweep to *move* **FAILED, and the script refused to report** — then the
round redirected to the axis that does vary. **A flat sweep is not evidence of "no effect"; it is
evidence the axis was mis-chosen**, and only the control distinguishes those.

⚠ **The naive direction argument was not refuted — it was never applicable.** *"A 2-annotator prompt
leaves one annotator to form the mode, so including such prompts should lower the ceiling"* presumes
2-annotator prompts exist. **There are none.**

## And a verdict string that went stale mid-round

After the redirect, one line still printed *"including 2-annotator prompts RAISES/LOWERS the
ceiling"* from two values that are **identical** — a comparative word emitted about a difference of
exactly zero. **§4's "the verdict string is not a computation", surviving an axis change that made it
meaningless.** Replaced with the measured difference and an explicit statement that no direction
exists to report.

## Controls

`n` falls monotonically in `m` **PASS** (the filter does filter, above m=3) · placebo `m=1 == m=2`
**PASS** · the ranking-filter sweep must move **FAIL — and that failure is the finding** · the
coverage axis must move **PASS**.
