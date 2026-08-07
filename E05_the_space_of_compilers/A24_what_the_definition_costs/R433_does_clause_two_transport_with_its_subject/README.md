# R433 · clause ②'s **subject** on a second release — **`W-LOSES`**

**The decision this round makes safe:** whether clause ② is a property of *cores* or a description
of what CoVal did. **It is a description.** A prompt-specific core generated from the conversation
alone — the clause's subject, which had never existed off the home release — **loses to a judge-free
length heuristic by −0.0545, resolved**, and does not even resolvedly beat its own prompt-blind
comparator.

## The numbers, on the round's own population

| arm | CONV | INTER |
|---|---|---|
| **`gen`** — criteria generated per conversation | 0.4500 | **0.4590** |
| `sham` — the same generator, **wrong** conversation | 0.4437 | 0.4540 |
| `generic` — the NEUTRAL arm, conversation unread | 0.4374 | 0.4497 |
| **`length`** — judge-free longest reply | **0.5104** | **0.5135** |

| contrast | CONV | INTER | verdict |
|---|---|---|---|
| **`gen − length`** | **−0.0604 [−0.0781, −0.0418]** vs MDE 0.0258 | **−0.0545 [−0.0706, −0.0377]** vs MDE 0.0235 | **RESOLVED, both** |
| `gen − generic` (clause ②'s own claim) | +0.0127 [+0.0010, +0.0233] vs MDE 0.0154 | +0.0093 [**−0.0008**, +0.0186] vs MDE 0.0140 | **NOT RESOLVED** |
| `gen − sham` | +0.0063 | +0.0050 vs MDE 0.0176 | `W-NO-MEASURABLE-MATCH` |

**Population** 7,342 interactions over 2,200 conversations (intersection of all arms; 2 dropped for
no `chosen`) · **instrument** Qwen3.5-2B-Base at k=4, 74,048 judge calls per arm · **baseline**
recomputed here, **not quoted from R427** · **regime** n ∈ {2,3,4}, one release, no rubric.

## ⭐ The two findings, and the second is the sharper one

1. **Clause ② does not transport.** The subject loses to a rule that reads nothing at all.
2. **Clause ② is not even *satisfied* resolvedly.** Its own statement is `core > neutral`, and that
   gap is **+0.0093 [−0.0008, +0.0186]** — the interval contains zero under the weighting R413
   argues for. **So the clause names a bar its subject cannot be shown to clear, while a heuristic
   that reads neither conversation nor criteria beats them both by a resolved margin.**

⚠ And the **conversation-match buys less than 0.0176**: swapping in another conversation's criteria
costs +0.0050, inside the floor. **Which conversation the criteria came from is not measurably doing
work here** — a bound, not a zero.

## Controls, and what each returned

| control | returned |
|---|---|
| provenance cross-check — both arms hash-match the core files on disk | **PASS** (`87949b432160`) |
| gate — parse rate | **1.0000** ≥ 0.80 |
| gate — coverage | **1.0000** ≥ 0.80 (0 of 7,344 interactions dropped) |
| PLACEBO — the arm against itself | **0.0e+00** |
| g=0 — a no-op plant | **0.4590 → 0.4590**, unchanged |
| POSITIVE — dose sweep | **0.4590 → 0.5132 → 0.5928 → 0.7268**, monotone |
| SHAM is genuinely a sham | **0 of 2200** criterion sets identical; hashes differ |
| generation | parse rate **2200/2200**, **99.7%** distinct criterion sets |

## ⛔ Four defects caught before or during, none by reading the code

1. **The pre-registered gate presupposed a non-null effect** — `sham < real` is a coin flip when the
   arm carries nothing. The selftest's `LOSES` fixture returned `W-FILLER`. **A true null would have
   been reported as a broken generator half the time** — and given the actual result, that is
   precisely the error I would have made. Fixed by AMENDMENT 1, *before any arm was scored*.
2. **Two producers sampling "2,200 conversations at seed 0" drew two different 2,200** — the judge
   samples only conversations with a *usable* interaction. Coverage 0.7473 tripped my own gate.
   Fixed by importing the judge's sampler: **0.7473 → 1.0000 by construction.**
3. **`parse_rate` divided by a hard-coded 2200** — found by making the fixture write real core
   files. It fails toward *"the generator is broken"*, so I'd have blamed the generator.
4. **The neutral gap was printed as a point with no resolution**, and then its paired vector used
   conversation means under *both* weightings — caught because both rows printed an identical
   interval. `lib/cluster.py`'s invariant ①.

## Impossible here, named

- **construct validity of `chosen`** — the release's own human choice; no external gold standard.
- **that this is the BEST obtainable core** — one greedy decode, one few-shot prompt. R432's oracle
  over five existing texts reaches **0.7220**, so the ceiling is far above what this generator
  produced: **the failure is this generator's, not proof that no generator can.**
- **causal attribution to any single criterion** — requires a per-criterion ablation, k× the compute.
- **cross-model** — one judge. Requires a second scored on the same responses.
- **position randomisation** — storage order only.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
The kill is in `PREREGISTRATION.md`, committed at `fa8eea5` before any arm was scored, with
`AMENDMENT 1` timestamped against a job log.
