# The EAR decomposition of this repository

**E** epoch · **A** arc · **R** round. Constitution §P16. Written 2026-08-02, before the `git mv`.

```
ENN_what_the_object_turned_out_to_be/
  ANN_the_decision_this_made_safe/
    RNNN_the_belief_that_changed/     <- run.py · README.md · results/
```

Prose address: **`E04·A13·R207`**.

---

## How the boundaries were found, and the two candidates that failed

**The count at every level is discovered, never chosen.** So the first job was to find an existing
record of ontology shifts rather than to invent one. Two candidate sources were tried and both
failed, which is worth writing down because each looked authoritative:

| candidate | why it failed |
|---|---|
| **the 13 existing phase directories** | they are imposed themes. `06_the_judges_mechanism` and `07_floors_for_the_counterfactuals` are two names for one question — *what can this apparatus resolve* — and `08_direction_from_text` is a third. Re-cutting a filing produces another filing |
| **the `Ω` impact letter in the commit grammar** | it should mark paradigm-level commits. **147 of 510 commits carry it — 29%.** In practice it came to mean *important*. A marker that fires on three commits in ten cannot locate five shifts |

What worked was the project's own retractions and its north star, because both were written at the
moment the object changed and neither was written to be a table of contents.

---

## `E` — the five epochs

An epoch closes when **the object under study turns out to be a different object**. Each boundary
below cites the round and the number that moved.

### `E01` · the rubric was the object — R001–R022

**Studied:** does the crowd's written rubric predict human choice; which aggregation rule is best;
can it be over-optimised.

**The object turned out to be different when** `R011`'s independent-backbone control ran. The gold
head shared Qwen3.5-2B with the judge; on an independent 0.8B backbone the headline
**+0.53 [0.06, 0.99] became +0.05 [−0.44, +0.53]**. `R019` sealed it: the same attribution is
**27% or 67%** depending only on which donor floor you pick, a span of **2.47×**.

> A number here was never about the rubric. It was about the rubric, the judge, and a floor
> somebody chose.

### `E02` · the plural public was the object, and it dissolved — R023–R045

**Studied:** structured plurality — do different people hold different values, and can a compiled
core preserve them.

**The shift:** `R023`. Agreement between raters persists **with no blocs at all** if raters merely
differ in reliability, because a careful rater agrees with everyone. Fitting `A_ij = μ + a_i + a_j`,
the additive actor model takes **47.2%** of dyad variance and actor-only persistence is **0.254** —
*higher than the 0.147 headline it was invoked to explain*. What survives is a pair-specific
**ρ = 0.034**, 20–23% of what was reported.

> "People disagree" stopped being evidence that people hold different values.

### `E03` · the instrument was the object — R046–R109

**Studied:** the judge, the floors, whether direction is readable from text alone, the resampling
unit, reliability, the width chain.

**The shift** is the one `E01` forced and the project took sixty rounds to act on: it stopped asking
what CoVal says and started asking **what its own apparatus can resolve**. The judge tracks lexical
overlap at **+0.21**; six copied words move it **a quarter of its scale**; a 21-point rating scale
turns out to have had its midpoint used **once in 102,147 ratings**.

### `E04` · there is no fraction — the object is an equivalence class — R110–R219

**Studied:** who pays for compilation, the chain N→Y, then the whole thing re-derived from zero.

**The shift is self-dated, in the project's own north star:**

> *"A pipeline does not preserve '73.4% of normative information', and asking for that number is
> the error this project made for sixty rounds."*

Normative information became `[N]_Q` — an equivalence class relative to a **declared** query family.
Three results sealed it, and none of them is a percentage:

- **no finite weight encodes a veto** — the penalty reproducing one depends on which candidates were
  shown, and `sup Δ = ∞`. Type is not compressible to magnitude
- **82.3%** of criteria carry no condition, exception, priority, hedge or prohibition. The structure
  a compiler is accused of destroying **was never collected**
- a person's own criteria predict a **stranger's** ranking at **0.310** and their own at **0.393**.
  The individual signal in the elicitation is **0.083 of cosine**

### `E05` · the space of compilers is the object — R220–

**Studied:** not what CoVal's core loses, but what *any* compiler must preserve.

**Opened by** `R220`'s preregistration, which withdrew the obvious next step *before building it*:
"search the minimal subset that reproduces Full on A–D" would have won on our instrument, our
candidate set and our own target, and meant nothing. The object became a tournament in which our own
arms carry no immunity — and on the first run three of five pre-registered claims died, including
the one that mattered.

---

## `A` — the arcs

An arc closes when **a decision becomes safe** — a choice no longer hinges on an unresolved unknown.
Deferring counts as closing, provided the single blocking unknown is written down.

| arc | the decision it made safe | rounds |
|---|---|---|
| **E01·A01** | can this release be analysed at all, or is the missing satisfaction layer fatal | R001–R005 |
| **E01·A02** | which aggregation rule should anything be scored with | R006–R009 |
| **E01·A03** | is the attribution real, and against what floor | R010–R022 |
| **E02·A01** | is the plurality structured, or is it reliability | R023–R032 |
| **E02·A02** | what is `coval_core`, mechanically | R033–R037 |
| **E02·A03** | does the human protocol have the power its claims need | R038–R045 |
| **E03·A01** | can a local judge be used as an instrument at all | R046–R059 |
| **E03·A02** | what floor does each counterfactual require before it may be read | R060–R072 |
| **E03·A03** | can criterion direction be recovered from text alone | R073–R084 |
| **E03·A04** | what is the resampling unit, and what is triage-able | R085–R099 |
| **E03·A05** | how wide is every interval really | R100–R109 |
| **E04·A01** | who pays for compilation, and is the sacrifice invisible | R110–R141 |
| **E04·A02** | what happens along the chain from a person to the compiled standard | R142–R165 |
| **E04·A03** | do this project's own claims survive an adversary | R166–R205 |
| **E04·A04** | is the detection design well-defined enough to run | R206–R218 |
| **E04·A05** | can a stranger check the argument without trusting the author | R219 |
| **E05·A01** | is our own compiler better than the official one | R220 |

**5 epochs · 17 arcs · 217 rounds.**

---

## Two deliberate deviations from §P16, each with its reason

**1. Rounds keep their global number.** §P16's prose address implies per-parent numbering. This
repository is public, and `RETRACTIONS.md` cites rounds by global number in ~95 entries, the README
links to them, and 267 code references resolve them by path. Renumbering would silently invalidate
every citation in a ledger whose entire purpose is that it cannot be quietly edited. So the tree is
three-level and the leaf is `R019_floor_choice`, not `R03_floor_choice`. **The address `E01·A03·R019`
still reads left to right; only the last field is globally unique instead of locally.**

**2. `covalx/` is not renamed to `lib/`.** §P16 wants shared code in `lib/` so that a cross-round
dependency is explicit rather than a relative path. `covalx` already satisfies that — it is an
importable package, imported by name from every round, never by relative path. Renaming it would
churn every import to satisfy the letter of a rule whose intent is already met.

---

## What this decomposition does not claim

The epoch boundaries are **judgments about a record**, not measurements. The evidence for each is a
citable event and is given above, so the cut can be attacked at a specific number rather than as a
matter of taste. The most contestable is `E03`: its shift is the one `E01` had already forced, and
one could argue they are a single epoch with a sixty-round latency. The argument for splitting them
is that between them sits `E02`, in which the object was the people and not the apparatus — and
epochs, being intervals of time, cannot interleave.

---

# ⚠ AMENDMENT — 2026-08-03. Three rules were being violated; one of them silently.

Ivan, reading the tree: *「A 应该也是连续记述而不是每个 E 刷新一次的，然后还有是应该是多个 R
组成一个 A」* — **A must be continuously numbered, not reset at each epoch, and an A must be made
of MULTIPLE R's.** Audited against that, four defects, in increasing severity:

| # | defect | measured |
|---|---|---|
| 1 | **`A` restarted at `A01` in every epoch** | all 5 epochs began at `A01`, so `A01` named five different decisions and an arc id was not a key |
| 2 | **arcs holding ONE round** | 7 of 30 — a round wearing an arc's clothes. P16: an arc closes when a *decision* becomes safe, and that takes several belief updates |
| 3 | **`E05` skipped `A14` and `A15`** | ran `A01..A13` then `A16`; the gap recorded nothing |
| 4 | ⛔ **SIX ROUND IDS NAMED TWO DIFFERENT ROUNDS EACH** | `R277–R282` existed under **both** `A13` and `A16` — 89 round directories, **83 distinct ids** |

**Defect 4 is the one that matters and it was invisible from the tree.** The six pairs are not
copies; they are different questions with different `run.py` and different results:

| id | one round | the other |
|---|---|---|
| `R277` | is necessity tolerance-free | the MDE of the design that priced it |
| `R278` | can the admissibility gate ever fire | is the boundary resolvable |
| `R279` | was the gate violated by its own founding round | what would resolve the boundary |
| `R280` | is the gate unit coherent | the table at every annotator |
| `R281` | does the coherent gate admit this release | a size-matched neutral arm |
| `R282` | is the saturation forced by sample size | neutral clause at matched k=4 |

A round id is **the key for one belief update**, and twelve updates were sharing six keys.
`FORMULATION.md` — the deliverable — cites **both** `R278`s and **both** `R279`s, in the same
file, meaning different rounds. No reader could have told them apart, and neither could I: I cited
`R281` several times this session without knowing there were two.

## The rules, now stated so they can be checked

1. **`A` is globally continuous.** `A01..A24` across the whole project. An arc id resolves to one
   decision without knowing its epoch.
2. **Every `A` holds ≥ 2 `R`.** Enforced by the migration's precondition, which refuses to run
   otherwise.
3. **Every `R` id is unique project-wide.** 305 round directories, 305 distinct ids.
4. **An arc need not be contiguous in id.** Ids are a counter over belief updates in time; two
   arcs running in parallel interleave. What must hold is that each round belongs to *exactly one*
   arc — a partition, not an interval.

## Who kept a contested id

**First claim wins, decided by `git`, not by which arc I happen to be working in.** `A23`'s six
were first committed 07:16–07:51; `A16`'s duplicates at 10:34–10:47, ~3 hours later. So the later
claim was reassigned: **`R277→R303  R278→R304  R279→R305  R280→R306  R281→R307  R282→R308`**.
Checked before choosing: **0 citations of these ids exist outside this repo**, so the renumber is
contained. `_ear/REMAP.tsv` holds every old→new path; `_ear/migrate_ear.py` holds the reasoning
and the preconditions it refused to proceed without.

**What is NOT repaired: commit messages.** They are immutable and several cite an ambiguous id.
`REMAP.tsv` is what makes them resolvable, and that is the honest repair for a record you cannot
edit — not a claim that the history is clean.

⚠ The prose address earlier in this file, `E04·A13·R207`, was written under the old scheme and is
now wrong: R207 sits in **`E04·A15`**. Left in place and corrected here rather than edited away,
because the stale example is the clearest evidence that an index ages the moment the tree moves.
