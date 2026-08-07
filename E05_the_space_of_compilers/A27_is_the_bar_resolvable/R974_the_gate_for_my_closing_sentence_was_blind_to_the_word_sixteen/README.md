# R974 · the gate for my closing sentence was blind to the word `sixteen`

**THE DECISION THIS MAKES SAFE.** Whether the suite's red set can be tracked across rounds by its
count. It cannot, and the round settles that with a per-member check instead — so no later round
has to re-open "are we greener than we were".

---

## What was asked

R973 closed with: *"R961's red list had sixteen entries and three are now resolved."* Two things
turned out to be wrong with that sentence, and the second is the interesting one.

## ① The gauge test, which was the cheapest thing available and was tried first

`assurance/next_line_quantifiers_are_computed.py` exists for exactly this failure — a count over
the project's own work, uncomputed, written in the sentence nobody controls. It said nothing.

Writing a numeral as an English word leaves the **claim** identical. It did not leave the
**measurement** identical:

| form of the same sentence | `BARE_COUNT` |
|---|---|
| `16 entries` | flagged |
| `sixteen entries` | **invisible** |

Measurement not invariant, property invariant ⇒ **the measurement was blind**. Both positive
controls behaved (a known-bad line fires; a known-good line with provenance does not), so the
`False` is a measurement of blindness rather than silence.

## ② How much of history the rule could never have seen

Over **1,380 NEXT paragraphs**, extracted by the gate's *own* `next_lines` — not a new population:

| word list | word-numeral hits | uncited by provenance |
|---|---:|---:|
| `one..twenty` | 174 | 165 |
| **`two..twenty`** (shipped) | **145** | **138** |
| `three..twenty` | 114 | 110 |

Pre-registered kill: fewer than 20 uncited ⇒ world A, a curiosity about one sentence.
**Observed 138 ⇒ world B.** Flag rate over the same population, before → after: **25.2% → 32.0%.**

⚠ **`one` is excluded, and that is a measurement.** It adds 11 paragraphs and all **eleven** were
read, not sampled: every one is an indefinite or a named singular — *"planting one round"*, *"the
one arm the definition was written from"*, *"holds exactly one arm, topvar_k4"* (which names it, so
it is computed). 11 of 11 false positives.

⚠ **The rule still requires adjacency.** *"four of the five predate the current format"* carries a
count this pattern cannot see, because no artifact noun follows the numeral. The blindness is
**narrowed, not closed**, and that residue is stated here rather than implied by a green run.

## ③ The claim itself, checked per member instead of per count

The suite's sweep printed a histogram and persisted nothing, so **ten of R960's sixteen reds have
no name and never will**. Their status is UNIDENTIFIED — which is neither resolved nor unresolved.
Six were enumerated in commit `85acc2e9`, and those are checkable:

| R960's six named reds | at HEAD |
|---|---|
| `a_share_carries_its_counts` | FAIL |
| `arm_population_is_derived` | FAIL |
| `outcome_variable_declared` | FAIL |
| `verdict_cites_its_own_contrasts` | UNRUNNABLE — *observed nothing*, not repaired |
| `next_line_quantifiers_are_computed` | FAIL |
| `a_commit_body_names_its_own_round` | FAIL |

**0 of 6 are PASS.** And of R973's three claimed-resolved, `outcome_variable_declared` is **still
FAIL** — while the same commit body wrote *"the gate's whole-repo verdict is unchanged at 1"*. The
commit contradicted itself in two paragraphs.

**⛔ NO DELTA IS REPORTED against R960's 71.** That population excluded `attack_the_suite` by name;
this one includes it, and the current denominator is 64. The two counts are not the same
measurement, and subtracting them would manufacture a number.

## What this now rests on

- the gate's own extractor and regexes, so the population is the one the gate polices, not a new one
- `assurance/results/suite_sweep.json`, which this round's sibling change makes `run_all.py` write —
  **members**, not just counts, because a histogram cannot be diffed against a membership list
- commit `85acc2e9` as the only enumerated record of the red set that has ever existed

## The alternatives considered

**Rebuild the red list from history by re-running the suite at R961's tree.** Rejected: it needs a
worktree, and it would answer a question about a past commit rather than make the next one
checkable.

**Widen the rule to catch non-adjacent counts.** Rejected here: the docstring records a first
version that flagged 61% of all NEXT lines and had to be tuned back. A wider rule needs its own
false-positive measurement, and this round already spent its budget establishing the narrow one.
