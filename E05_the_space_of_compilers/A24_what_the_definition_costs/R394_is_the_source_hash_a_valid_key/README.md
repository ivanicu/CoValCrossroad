# R394 — the key is sound for fast rounds, and the tail it must serve is untested

**The decision this makes safe:** *can the cache be keyed on the round's source hash?* **Yes for the
rounds measured — and the measurement cannot speak for the rounds the cache exists to serve.**

## Result — `W_KEY_VALID`. Both plants caught. **No GPU spent.**

| | |
|---|---:|
| subjects (R393's COMPLETE set) | **13** |
| **STABLE across two runs at unchanged source** | **13 / 13** |
| numbers compared | **538** |
| UNSTABLE | **0** |
| ABSENT / TIMEOUT | 0 |

## ⛔ The premise R393's NEXT did not examine

R393's NEXT specified a cache *"keyed on the round's source hash, so a changed round invalidates its
own row."* **A source hash is a valid key only if an *unchanged* source yields unchanged numbers** —
and nothing in Python guarantees that. Unseeded rng, wall-clock, filesystem order, hash randomisation
and pointer-keyed iteration all vary at fixed source.

**And this was never only about a cache that does not exist.** R388's gate **already** re-runs every
cited round and compares its numbers against the README row. **A round that moves at fixed source
makes that gate convict an honest backfill** — a live bug in a committed gate, whose failure nobody
would have read as anything but a bad row.

## Controls — both directions

| | returned |
|---|---|
| **PLANT (+)** | an **unseeded** rng draw is classified **unstable** — `PASS`. Without it, *13 of 13 stable* is silence from an instrument never shown to return instability |
| **PLANT (−)** | a constant is classified **stable** — `PASS`. The mirror control, which this campaign's own failure table says is the one that gets skipped |
| **EXTRACTOR** ⭐ | the gate's `NUM` regex is **imported from the gate**, never copied. A re-implemented classifier tests the copy — R387 already paid for that lesson |
| **REGIME** | consecutive runs in a worktree at HEAD, so the committed artifact is present on run 1 and overwritten by run 1 on run 2 — **the regime the gate actually runs in** |

## ⚠ It was measured UNDER LOAD — and that is one-directional

A concurrent session was running a long round throughout (`timeout 5400 … run.py`, confirmed by
`pgrep`). A guard refusing to run under load was added to this round's source **after** the
measurement, and it now correctly refuses.

> **Load can manufacture instability; it cannot manufacture stability.** A timeout or a timing print
> perturbed by a busy machine makes two runs *differ*. Nothing about contention makes two differing
> outputs identical. So the omission could only have produced a **false UNSTABLE**, and the verdict
> was **STABLE** — the result survives, and is if anything a harsher test than a quiet machine.

**Attribution, checked rather than asserted:** the artifact's `source_sha256` is
`c0470d92e3b5…`, which **matches commit `e01f187`'s `run.py` exactly** and not the current file. The
artifact is not orphaned — it names a committed source, just not the newest one. **The debt: re-run
under the guarded source on a quiet machine.** Stated as owed, not as done.

## ⚠ Two limits, both written before the run

**① `STABLE` means "not caught in two draws", never "deterministic."** Two runs bound the detection
probability from below only. **A round that varies once in fifty is called stable here and would
still break a cache.**

**② The population is selected toward this answer.** These are R393's **COMPLETE** subjects — the
rounds that finished inside 90 s, i.e. **the ones loading no model and drawing no samples, which are
exactly the rounds most likely to be deterministic.**

> **R393's two censored rounds carry 80% of the gate's cost, and they are precisely the rounds this
> design cannot speak for.** The selection biases toward `W-KEY-VALID` — the flattering direction for
> building the cache — which is why it was named in the docstring before the answer was known.

## Register

| criterion | status |
|---|---|
| **proof of determinism** | **N/A** — two draws cannot establish it. Only *not caught* is available |
| **the censored rounds** | **N/A here** — they exceed the budget that made this affordable, and are where the answer matters most. **The next step, not a caveat** |
| **artifact-only variation** | **N/A** — a round whose file changes while its stdout does not is invisible to this instrument |
| **a quiet-machine replication** | **OWED** — the guarded source has not yet produced an artifact |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"key the cache on the source hash, so a changed round invalidates its own row"* — **as though the
> converse were free.** An *unchanged* round returning an unchanged row is the half nobody tested,
> and it is the half that decides whether the cache certifies or merely remembers.

Artifact: `results/r394_source_hash_key.json`, source-stamped to `e01f187`.
