# R985 · k comes from the object, not a ledger — and clause ①'s zero survives at full population

**THE DECISION THIS MAKES SAFE.** Whether R984's *"clause ① drops 0 clause-② passers"* was a
population artefact. It was not: **all 99 arms are now scoreable**, clause ① drops 4, and **none of
the 4 passes clause ②**.

---

## `k` was never a ledger job

R984 left **57 of 99 arms unscoreable** because R360's ledger records `k` for 42, and its NEXT called
recording the rest a ledger job. It is cheaper: `load_sat` returns a dict keyed by
`(criterion_index, response_letter)`, so **the criterion count is in each arm's own artifact**.
Derived for **99 of 99**.

⚠ **And R984's refusal is honoured here.** Every arm's name carries its k — `greedy_k8_fit1` — and
parsing the name is a proxy for the property. The derivation reads the satisfaction matrix, never the
string.

## The positive control, with its exceptions pre-named

| | |
|---|---|
| derived `k` reproduces R360 | **40 of 42** |
| mismatches | `full`, `full_sham` |
| pre-named as variable-k **before the control ran** | `full`, `full_sham` |
| **the mismatch set is exactly the pre-named one** | **True** |

Both mismatches are the same fact: their per-prompt k runs **4 to 39**, so **a scalar is the wrong
TYPE** for them and R360's recorded 15 is a summary, not a value. The round persists the distribution
rather than inventing a summary of its own.

⭐ A control that tolerated *arbitrary* mismatches would test nothing. Naming which two, in advance,
is what makes 40/42 a pass rather than an excuse.

## The result — and the specification axis that matters

| reading | clause ① drops |
|---|---|
| **min per-prompt k > 1** | 4 — `gen`, `gen_sham`, `topw_k1`, `topw_k1_08b` |
| **modal k > 1** | 2 — `topw_k1`, `topw_k1_08b` |

`gen` and `gen_sham` have **min per-prompt k = 1**, so the two readings disagree about them. **Both
are reported**; neither is chosen.

**The join** — do any of the four pass clause ②?

| arm | mean A2 | margin vs `generic` | passes ② |
|---|---|---|---|
| `gen` | 0.535173 | −0.016181 | **False** |
| `gen_sham` | 0.482801 | −0.068554 | **False** |
| `topw_k1` | 0.525582 | −0.025773 | **False** |
| `topw_k1_08b` | 0.439021 | −0.112333 | **False** |

**None.** So clause ① drops 0 clause-② passers on the full inventory, under **either** reading.
**R984's zero was not the missing 57.**

## ⛔ And v1 of this round called a four-comparison gap an impossibility

R984's artifact persists the passer **count** (24) and not the passer **list**, so v1 stopped and
reported that the intersection *"cannot be computed from artifacts alone"*. That was true and it was
lazy: clause-② admission for **four named arms is four bootstrap comparisons**. A gap that costs four
comparisons is not a wall, and calling it one is the **fabricated-impossibility** failure — the one
that makes stopping feel earned so nobody audits it.

## Controls

| control | result |
|---|---|
| **POSITIVE** | 40/42 exact; mismatch set exactly the two pre-named variable-k arms |
| **NEGATIVE** | an arm with no artifact stays unscoreable — 0 such here, and the repair from R984 survives the population change |
| **PLACEBO** | `topw_k1` derives k = 1 under both readings |
| **REPRODUCIBILITY** | two runs byte-identical (`e0cb1bd4…`) |

**NOISE FLOOR: none needed** — `k` is a count read from a matrix, not an estimate. Stated rather
than fabricated.

## What this does not say

- It establishes what `k` **is**, never that *"size > 1"* is the right clause.
- **R984's structural limit stands**: an inventory we built cannot separate an idle clause from one
  whose excluded object nobody has constructed. That needs a third party building arms without
  seeing the definition, and no amount of population-closing substitutes for it.

## Alternatives considered

**Pick the modal reading and report 2 drops.** Refused: `gen` is an arm the definition discusses by
name, and the two readings disagree exactly there. Choosing one would hide the disagreement, which
is the informative part.

**Backfill R360's ledger with the derived values.** Not done here: R360 is a committed artifact of a
closed round, and editing it would make a past round's output depend on a later one. The derivation
lives in this round's artifact where a reader can see who computed it.
