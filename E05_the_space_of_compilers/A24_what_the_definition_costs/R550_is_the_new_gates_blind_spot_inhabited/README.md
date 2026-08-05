# R550 · The blind spot's hazard is real; its occupancy is unobservable

**Decision this makes safe:** whether last round's gate is complete as built.

**WORLD B, at 2× the pre-registered kill.** **116 of 542 round directories (21.4%) carry ≥2
commits** — they were committed and then amended. Kill was set at ≥10% before the run.

| commits | rounds |
|---|---|
| 1 | 425 |
| 2–3 | 107 |
| 4+ | 9 (max **24×**, `R427_does_the_definition_transport_at_all`) |

**So tracking a directory once cannot certify it is current** — and `every_round_is_committed.py`
claimed only that, correctly and insufficiently.

## ⭐⭐⭐ The estimand was not what the instrument measures

I asked *"is the blind spot inhabited?"* — the blind spot being **modified and NOT re-committed**.
**Git history cannot observe an uncommitted state.** Every one of those 116 amendments *was*
eventually committed, which is why history can see it at all. **The 21.4% measures the HAZARD —
rounds do get modified — and says nothing about OCCUPANCY, which is structurally unanswerable
here.** Occupancy: **UNVERIFIED**, and permanently so from this instrument.

## ⚠ A defect in my own live check, caught by reading its one hit

It counted every `git status --porcelain` line and reported 1. That line was `??` — **untracked**
(R550 itself), not `M` **modified**. Tracked-but-dirty: **0**. The extended gate now carries a
control that admits `' M'` and rejects `'??'`, because that is exactly the confusion I just made.

## Controls
- **Positive** — `assurance/` returns **282** commits, so the counter can see multi-commit paths. **PASS.**
- **Negative** — an invented path returns 0. **PASS.**
- **Positive (dirty filter)** — admits `' M'`, rejects `'??'`. **PASS.**

**Remedy shipped:** the gate now fails on tracked-but-dirty round directories too. It closes the
hazard **prospectively**; it does not diagnose the past, and the file says so.
