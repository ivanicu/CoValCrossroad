# R302 — is a committed artifact reproducible from its committed code?

**The decision this round makes safe:** *may `FORMULATION.md` cite a number from a round whose
artifact I have not re-run?* Every published interval in this campaign was read off a results JSON.
If a JSON is not a function of its own code, the citation is to a draw, not to a result.

---

## How it started, and why that matters

Eight result JSONs have sat modified-but-uncommitted for days. The session hook has printed them
at every start. Diffing them was meant to be a two-minute cleanup.

**742 leaf values differ across the eight, and three changed a `verdict` string.** R241's
*committed* artifact says `valid = ['FLOOR_circular']`; three runs of the *committed code* say
`valid = []` and `UNVERIFIED`.

> A dirty file that nobody diagnoses is not noise on the way to the work. It was the only place
> this defect was visible, and it was visible for days.

## The mechanism, established before this round

`R241/run.py:93` seeds an rng with `abs(hash((pid, arm, dd))) % 2**32`. Python randomises `hash()`
of a `str` per process unless `PYTHONHASHSEED` is set. Measured, with the placebo:

| | |
|---|---|
| same `PYTHONHASHSEED` twice | artifacts **identical** |
| different `PYTHONHASHSEED` | artifacts **differ** |

So this round measures the defect's **reach**, not its existence.

## The unit trap, written before the run

A grep found **24** `run.py` files containing `default_rng(...hash(...))`. The instrument's unit is
*file contains a pattern*; the claim's unit is *this round's artifact moves*. **They are not
equal.** A hash-seeded rng can be inert — a display sample, or averaged away. So the 24 are
**candidates**, and the count that gets reported is what running them does.

## Worlds and kill

| world | claim | consequence |
|---|---|---|
| **W-INERT** | no candidate artifact moves | the eight dirty files have another cause, still open |
| **W-NUMERIC** | artifacts move, no verdict does | published intervals are understated by the between-seed spread |
| **W-VERDICT** | ≥1 verdict field moves | **an artifact can assert a conclusion its code does not reproduce**, and no number from an affected round is citable until re-run under a fixed seed |

```
if positive_control_recovers_R241 and placebo_holds:
    >=1 verdict field differs            -> W-VERDICT
    >=1 artifact differs, no verdict does-> W-NUMERIC
    none differ                          -> W-INERT
else:
    UNVERIFIED       # never W-INERT — a sweep that cannot see R241 has not acquitted anything
```

## Controls

| | |
|---|---|
| **POSITIVE** | R241 must be recovered as differing. It is already proven to differ, so a sweep that reports it identical is broken. Fails at g=0: a round with no rng cannot differ. |
| **NEGATIVE** | the non-candidate rounds. If those differ too, `hash()` is not the mechanism and the framing is wrong — reported, not suppressed. Size-bounded to the first 12 by path, named in the artifact, **not** described as a random sample. |
| **PLACEBO** | every round is also run twice at the *same* seed and must be byte-identical. A round failing this has some other nondeterminism and goes in its own bucket, never merged into the hash-seed count. |
| **EXCLUSIONS, NAMED** | rounds that load a judge are excluded (three model loads each, contending for a 16 GB card with the live queue) and printed by name. A silent skip would read as *swept everything* — the exact error the last two closing summaries made. Timeouts are `UNVERIFIED`, never `identical`. |
| **SIDE EFFECTS** | these scripts write into their own `results/`. Every directory is byte-snapshotted before and restored after, extra files deleted, and the restoration verified. A sweep that silently rewrote 24 committed artifacts would be worse than the defect it measures. |

## Impossible here

| | would require |
|---|---|
| whether a round is reproducible on a **different machine** | a second machine |
| whether the 2B/0.8B judge itself is deterministic across processes | that is `R301`'s parity control, not this round |
