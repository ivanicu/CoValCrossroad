# R543 · The command was in the log too — the seventh wall, and the sixth false one

**Decision this makes safe:** whether the 79 s vs 157 s generation gap is attributable.

## ⛔ The wall, one round after the lesson

R542 closed: *"the logs record elapsed time and artifact name, but **not** batch size or prompt
count. That attribution is genuinely unavailable from the logs."*

**`pueue status --json` records the full command.** One field.

| tasks | invocation | population | seconds |
|---|---|---|---|
| 602 / 603 | *(no `--corpus`)* → home release | **968** | **79 / 80** |
| 646 / 647 / 649 / 650 | `--corpus second --convs 2200 --batch 24` | **2200** | 157 / 157 / 158 / 159 |

⭐ **The gap is fully explained: 2200 conversations against 968.** **2.27× the work took 1.99× the
time — sub-linear, which is what batching should produce.**

## What it fixes

**79 s is the right figure for the home release**, which is what a rows-3/4 round targets. The
4.63 min total stands, and now with its population attributed rather than assumed.

## The pattern, and it is the finding

**Seven walls checked this session; six false, one true** *(R538 — no judge stronger than 2B on
disk)*. And this one was raised **one round after** R542 concluded *"every model wrong, every log
right"* — ⭐ **the lesson did not survive a single round, because a wall does not feel like a model.
It feels like a fact about the world, which is exactly why it needs the same check.**
