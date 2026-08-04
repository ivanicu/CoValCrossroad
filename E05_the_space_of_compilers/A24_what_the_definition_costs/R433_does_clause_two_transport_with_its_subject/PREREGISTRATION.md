# R433 · PRE-REGISTRATION — written while the GPU is still generating, before any arm is scored

**Committed at:** generation jobs `646` (real) and `647` (sham) queued and running; **no arm has
been judged, and no accuracy exists yet.** This file states the kill so it cannot be fitted.

## The claim under test

Clause ② of the definition: *a core is **better than a size-matched set that never read the
conversation**.* Every cross-release number so far measures the **comparator** — `generic`,
prompt-blind by construction. Clause ②'s **subject**, a prompt-specific core, has never existed on
the second corpus. R433 generates it.

## The estimand, named before the method

> **`ACC_gen` = P(the response the generated core ranks first is the one a human chose)**, over the
> same 2,200-conversation sample, the same judge, the same `build_prompt`/`Judge.score` path, at the
> same k=4 — so the **only** thing that varies between arms is the criterion text.

## ⛔ THE BAR IS 0.5096, NOT `generic`

| arm | value | source |
|---|---|---|
| chance | 0.4194 | R427, committed |
| **`generic` (the NEUTRAL arm — criteria present, conversation unread)** | **0.4374** | R427, committed |
| **longest-reply, judge-free** | **0.5096** | R427, committed |
| oracle over 5 existing texts (**upper bound, uses the answer**) | 0.7220 | R432, committed |

**Beating `generic` is a bar the arm is already known to be able to clear and it settles nothing** —
R427 showed `generic` loses to a heuristic that reads no criteria at all. **A core that cannot beat
the length rule is not a core anyone should adopt**, whatever it does to its own comparator.

## ⛔ AMENDMENT 1 — the sham gate was mis-specified. Made **before any arm was scored.**

**State of the world when this was written:** generation jobs `646` and `647` **Success**; judging
job `648` **Running**, `649` **Queued**; `sat_transport_gen.npz` and `sat_transport_gen_sham.npz`
**absent from disk**. **No accuracy for either generated arm exists.** Amending after the numbers
land would be fitting the kill; amending now, on a defect the *selftest* found, is not — and the
distinction is only credible because the state above is checkable in the job log.

**The defect.** The gate below required `SHAM scores BELOW the real arm`. That **presupposes a
non-null effect** — precisely the ledger's *the control fails for its own reasons*, form ②:
*"`|permuted| < |real|` is a coin flip when the real effect is null, which is exactly when you are
running it."* `selftest.py`'s `LOSES` fixture — where the generated arm genuinely carries nothing —
returned **`W-FILLER` instead of `W-LOSES`**, because with `gen ≈ sham` the comparison is a coin
flip. **A true null would have been reported as a broken generator half the time.**

**Two things were wrong, not one.**
1. The comparison had no resolution attached. Replaced by: the sham fires only when it sits
   **resolvedly above** the real arm — `acc_sham − acc_gen > MDE_sham`, with `MDE_sham` from the
   paired per-conversation difference by cluster bootstrap.
2. **`W-FILLER` should never have been a veto.** The primary question — does the generated core
   beat the length rule — is answerable whether or not the *conversation-match* is inert. The sham
   informs the **reading**, not the **admissibility**. It is demoted from the gate to a reported
   diagnostic, and it can still fire as a world in its own right when it fires resolvedly.

**The gate is therefore now: parse rate ≥ 0.80 AND coverage ≥ 0.80.** Both are about whether the
arm exists at all. Nothing else was touched: the bar stays **0.5096**, the kill thresholds stay
`± MDE`, and the worlds keep their meanings.

**What this amendment cannot excuse:** if the real run returns a number I dislike, that is not
grounds for a second amendment. This one is spent.

## PRE-REGISTERED KILL — conditional, and the condition comes first

```
evaluate ONLY IF:
    parse rate >= 0.80                    (a generator that fails to parse is not a finding
                                           about cores; below this the round is UNRUNNABLE)
AND coverage >= 0.80 of sampled conversations carry a generated core
AND the SHAM arm scores BELOW the real arm's own value      (if the wrong-conversation arm
                                           matches the right one, the criteria are generic
                                           filler and the whole contrast is void)

then:
  ACC_gen - 0.5096 > its own paired MDE          -> W-TRANSPORTS.  clause ② holds on a second
                                                    release with its subject present.
  ACC_gen - 0.5096 < -MDE                        -> W-LOSES.       clause ② does not transport
                                                    even with its subject present, and the
                                                    definition owes a scope line.
  |ACC_gen - 0.5096| <= MDE                      -> W-UNRESOLVED.  report the BOUND, not a point.
otherwise                                        -> UNVERIFIED. Never OVERTURNED, never CONFIRMED.
```

**`MDE` is computed from the paired per-conversation difference vector by cluster bootstrap over
conversations (R413: the conversation is the unit), ≥3 seeds — not modelled, not assumed.**

## Worlds, differing ontologically

| world | what it means for the definition |
|---|---|
| **W-TRANSPORTS** | clause ② is a property of *cores*, not of the home release. The definition's transport row changes from a stated limit to a measured result. |
| **W-LOSES** | clause ② is **descriptive of what CoVal did**, not a licence. A prompt-specific core generated from the conversation alone does not beat a length heuristic, and the clause needs a scope line naming the release it holds on. |
| **W-UNRESOLVED** | the design cannot separate them. Report the bound and the MDE; do **not** report a point. |
| **W-FILLER** | the sham matches the real arm ⇒ "prompt-specific" criteria are generic text that happens to be generated per conversation. This is a finding about the *generator*, and it voids the other three. |

## Prediction matrix

| | gen ≫ 0.5096 | gen ≈ 0.5096 | gen ≪ 0.5096 |
|---|---|---|---|
| W-TRANSPORTS | 0.85 | 0.1 | 0.02 |
| W-LOSES | 0.05 | 0.2 | 0.9 |
| W-FILLER | 0.1 | 0.7 | 0.5 |

## Controls, specified now

- **NEUTRAL** — `generic` (0.4374), already scored. The ingredient *absent*, not misdirected. The
  gap `gen − generic` isolates **benefit**.
- **SHAM** — the same generator on a **different conversation** (job 647). The gap `gen − sham`
  bounds **benefit + harm** and is *not* the value of the ingredient. ⚠ *The ledger's row: a sham
  landing at or below the random baseline means a treatment with the sign flipped, and its gap must
  never be quoted as the ingredient's value.*
- **PLACEBO** — the arm against itself: exactly 0.
- **POSITIVE** — plant the human's choice into the generated core's ranking at rate g; accuracy must
  rise monotonically and be **unchanged at g=0**.
- **PARSE RATE / COVERAGE** — reported **before any accuracy**, per the gate above.
- **DROPPED** — interactions whose conversation produced no core are dropped and **counted**, never
  scored with another conversation's criteria (that would leak the sham into the real arm).

## Impossible here, named

- **construct validity of `chosen`** — the release's own human choice; no external gold standard.
- **causal attribution to any criterion** — nothing intervenes on individual criteria. Requires an
  ablation per criterion, which is k× the compute.
- **cross-model** — one judge, Qwen3.5-2B-Base. Requires a second judge on the same responses.
- **position randomisation** — the corpus carries storage order only.
- **that the generated core is the BEST obtainable** — one greedy decode, one few-shot prompt.
  Requires a generation sweep, which is a separate round.
