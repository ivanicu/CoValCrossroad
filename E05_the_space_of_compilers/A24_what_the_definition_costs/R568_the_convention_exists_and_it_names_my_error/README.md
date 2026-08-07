# R568 · The floor convention exists, and its docstring diagnoses my own error

**Decision this makes safe:** whether to build a floor-key convention. **Do not — it exists.**

**WORLD B.** `assurance/an_mde_records_its_denominator.py` **exists and exits 0** (frozen debt: 0).

⭐⭐⭐⭐ **Its docstring contains the diagnosis of R567's exact method, written by R373:**

> *"R373 tried to MEASURE how many past rounds record their denominator, using a whitelist of key
> names. **That is invalid: a guessed list cannot prove an absence**, and R355 and R368 were both
> false negatives. This gate does something different in kind — it **SPECIFIES** the acceptable names
> going forward. A specification cannot be wrong about absence, because it defines what counts.
> **The same list is invalid as a measurement and valid as a convention.**"*

**R567 did the invalid version — a guessed key list — and got a false `0 of 0`. The warning was in a
file that ran and passed on every commit of this session.**

## What this retracts
**R567's conclusion "60+ names, no schema" is wrong as stated.** The convention exists as a
**forward ratchet with frozen debt 0**; the 60+ historical names are precisely what it **does not
attempt to migrate**, by design. **The heterogeneity is historical, not unschematised** — a
different fact, and a much less alarming one.

## ⛔ And this round made the same class of error while diagnosing it
The first version searched the raw docstring for that sentence and returned **False** — on a
sentence I had just quoted from the same file. **The docstring wraps across lines, so the match
failed on whitespace.** Same class as R562's underscore and R567's UUID: **sixth occurrence this
session.** Normalised, it returns True.

⭐ **A prose search must normalise whitespace before it may claim an absence** — otherwise line
wrapping is indistinguishable from the text not being there.

## Controls
- **Positive** — a known gate (`statement_provenance`) reads present and passing, so "exists and
  passes" is a measurement. **PASS.**
- **Negative** — an invented gate name is not found. **PASS.**
