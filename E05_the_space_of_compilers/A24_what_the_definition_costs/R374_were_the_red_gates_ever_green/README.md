# R374 — five of the eleven red gates were never green, and six broke inside one bracket

**The decision this makes safe:** *is "the campaign has no working brake" one problem or two?*
**Two, and they need opposite actions.** The sentence is withdrawn as written.

## Result — `W_MIXED`. Both harness controls PASS. Two runs byte-identical. **No GPU spent.**

R373 closed by calling the eleven red gates *"the largest thing I can name"* and hypothesised most
were stale registrations. **That hypothesis is a taxonomy of my own failures — producible for free in
any shape I like.** The decision-relevant question has an answer that does not depend on my
judgement:

> **Was this gate ever green?**

| | |
|---|---:|
| gates measured | **11** |
| green at some rung since birth | **6** |
| **never green since the day they were committed** | **5** |
| ladder | 12 rungs over **692** commits = **132** cells |

## The ladder

| back | commit | date | arti | atck | nowd | outv | donor | isol | pueue | rdme | seed | synth | verd |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0–64 | `81c0789`… | 08-04 | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 2 | 1 | 2 | 2 |
| 128 | `1bef0c41a` | 08-03 | 1 | 1 | 1 | 1 | 1 | — | 2 | 1 | 1 | 2 | 1 |
| 256 | `c2e10c2a3` | 08-03 | 1 | 1 | 1 | 1 | 1 | — | 2 | 1 | 1 | 2 | 1 |
| **512** | **`c0b1981db`** | **07-29** | **0** | **0** | 1 | 1 | **0** | — | 2 | **0** | **0** | **0** | 1 |
| 692 | `e44704137` | 07-28 | — | — | 1 | 1 | — | — | — | — | — | — | — |

`—` = the gate did not exist. **ABSENT is not green.**

## ⛔ Born red — five gates that never passed

`attack_no_withdrawn_framings` · `attack_outcome_variable_declared` · `_isolated` · `pueue_wait` ·
`verdict_cites_its_own_contrasts`

**A gate that has never exited 0 is a claim about the corpus that the corpus never made.** There is
no regression to find, because there was no green state. The action is per gate: **satisfy it or
retire it.**

## ⛔ Six regressed — and all six in the *same* bracket

`artifacts_are_internally_coherent` · `attack_every_check` ·
`donor_numbers_carry_their_draw_scope` · `readme_row_carries_the_verdict` ·
`seed_filter_is_disclosed` · `synthesis_cites_recent_work`

**Every one green at HEAD~512 (07-29) and red by HEAD~256 (08-03).** Six simultaneous independent
regressions is a much worse explanation than one commit, and the bracket is 256 commits wide — a
bisect, not a guess. **That is the next round, and it is why this one stops here.**

## ⛔ R373's hypothesis is partly refuted by the table

R373 wrote: *"[HYPOTHESIS] most are stale registrations rather than real defects, because several
are exit 2, and an exit 2 means the gate lost its input rather than found a violation."*

**`readme_row_carries_the_verdict` and `synthesis_cites_recent_work` both exit 2 today and both
exited 0 at HEAD~512.** An exit-2 gate can be a regression that *destroyed its own input* — the
exit code says what the gate found, never whether it was always so. **The reasoning was sound and
the premise was wrong.**

## Controls

| | returned |
|---|---|
| **HARNESS (+)** | `consistency` is **0 live and 0 through the worktree** at the same commit — a harness that cannot reproduce a known pass makes every red its own artifact |
| **HARNESS (−)** | `seed_filter_is_disclosed` is **1 live and 1 through the worktree** — a harness that turns everything green is the flattering failure |
| **ABSENT** | recorded as `—`, never as green. 4 gates × 1 rung + 1 gate × 3 rungs |
| reproducibility | two runs **byte-identical** (`50484a7cbba4`) |

## The choice that decides the question

The harness runs **the gate as it was, on the tree as it was**. Running *today's* gate on an old tree
asks *"when did the corpus break this rule"*; running the *old* gate asks *"was the campaign green
at that time"*. **The second is the question**, because the claim under test is that the campaign
reported green while its brake was off. The other is named here rather than silently conflated.

## Register

| criterion | status |
|---|---|
| **WHY any gate is red** | **N/A here by design** — this measures **when**. No sentence in this round diagnoses a single gate |
| **the exact breaking commit** | **N/A** — a 12-rung ladder gives a **bracket**; the bisect is the follow-up, not approximated here |
| **gates before their birth commit** | **undefined, not green** — every "never green" is bounded by its own birth, printed in the table |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"a campaign that reports green while twelve gates are red has no working brake."*

**Five of them were never brakes at all — they are unsatisfied claims. Six were brakes and broke,
apparently together. Those need opposite actions, and the one sentence hid that.**

Artifact: `results/r374_gate_history.json`, source-stamped.
