# R427 · the first number on the second corpus — does a prompt-blind core pick what people picked?

**The decision this round makes safe:** whether the definition has *any* cross-release evidence. Its
own table has said `transfer to another release: RETRACTED` since R398, and nothing has walked
through the opening.

## ⛔ Seven rounds read the second corpus. Zero scored on it.

| round | what it did |
|---|---|
| R398 | the corpus exists — 68,371 human-scored rows, 8,011 conversations |
| R399 | the estimand it admits — `score` is a **rating** 1–100; overlap with CoVal is **3 prompts** |
| R400 · R412 · R413 | depth confound · clustering · score-clustering |
| R402 · R403 | harness · statability |
| **any round calling `select_core` / `judge_core` on it** | **none** |

**Six rounds of *"can we?"* and none of *"here is the number."*** That is preparing billed as
progress, and it is the campaign's largest open structural gap.

## The design

**Estimand:** `ACC` = P(the response the core ranks first is the one a human chose).
**Unit = conversation.** R413 measured `kappa_chosen = 1.0` and `p_in_argmax = 1.0` *within* a
conversation (`deff 3.317`, `n_eff 8,076` of 27,151). Using rows would shrink every interval by
**1.82×** and manufacture significance out of clustering.

**Sample:** 2,200 conversations, seeded → 7,344 interactions → 18,512 responses → **74,048 judge
calls** at `k = 4` (the CoVal full job is 61,952).

**Why the prompt-blind arm and not a prompt-specific one:** the second corpus has **no rubric**, so a
prompt-specific core would have to be *generated* first — a second GPU job with its own assumptions.
`core_generic.json` is prompt-blind by construction and transports unchanged. **This measures the
FLOOR of transport and speaks to no prompt-specific core.**

| world | what it would mean |
|---|---|
| **W-TIEBREAK** | the four tiebreak rules disagree → no accuracy admissible (outranks all below) |
| **W-DOES-NOT** | fails chance → every clause against `full` is release-local |
| **W-LENGTH** | beats chance, not the longest-response shortcut → criteria decorative |
| **W-ANY-CRITERIA** | beats both, but a **random prompt-blind core matches it** → clause ②'s *content* is not what carries |
| **W-TRANSPORTS** | clears all three |

## ⛔ A gauge test on my own estimand, run while the GPU worked — and then measured

**Rung 1, three lines, zero compute.** The winner was picked with
`max(row, key=lambda r: (row[r], r))`. Name a transformation leaving the **measurement** invariant
but not the **property**: let the criteria be trivially satisfied by everything. Every response ties
at 1.0, and the tuple key then resolves by **response-ID string order** — the accuracy becomes a
property of the ids.

**So the tiebreak became a swept specification** — `id` / `id_last` / `random` / `corpus-first` — with
the spread printed and a kill attached, plus a **`first`-position baseline** beside `length` (the
standard asks for position-randomised designs; this release has no presentation-order field, so the
honest substitute is to measure what the positional rule alone achieves).

⚠ **And then the risk was measured where it could be, which changes what may be claimed about it.**
On the **home** corpus:

| arm | mean sat | sd | share > 0.9 | **argmax tied** |
|---|---|---|---|---|
| `generic` | 0.5930 | 0.2092 | 4.2 % | **1 of 968 (0.1 %)** |
| `topw_k4` | 0.5604 | 0.2349 | 3.8 % | 0 of 968 |
| `full` | 0.5548 | 0.2365 | 3.5 % | 0 of 968 |

**`generic` does not saturate.** So this was a live **risk**, not a live **defect** — and saying
otherwise would have been a fabricated catch. The control stays, because the second corpus is a
different response distribution and the home-corpus rate bounds nothing there; but the honest
expectation is a flat curve, and the instrument is what will say.

## Impossible here, named

- **a prompt-specific core** — no rubric on this corpus; generating one is a separate job.
- **clauses defined against `full`** — R403 measured them NOT-STATABLE off the home release.
- **construct validity of `score`** — it is this release's own human rating; no external gold standard.
- **position randomisation** — no presentation-order field; the `first` baseline is the substitute.
- **a second team** — one operator.

Findings, with their scope, live in the top-level README. This file states the design.
