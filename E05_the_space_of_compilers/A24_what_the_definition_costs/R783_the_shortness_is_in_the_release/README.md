# R783 · the shortness is shipped — and the impossibility I registered was false inside the round

`run.py` · `PREREGISTRATION.txt` · `results/release_vs_pipeline.json` · 986 released conversations ·
968 scored prompts

## THE DECISION THIS MAKES SAFE

**R782's headline survives its own attack and upgrades from *the scored core* to *the core as
shipped*.** The release itself carries **44 of 986** cores with fewer than four criteria (**4.46%**),
the rubric `coval_full` never drops below 4 on any record, and once the release-to-scored join is
applied the two instruments agree **exactly**. **WORLD A.**

## ⛔ AND THE ROUND KILLED A WALL I HAD JUST BUILT

The preregistration's impossibility register says, in my own words:

> *which 18 records went unscored, by id — the recovered cross-space key; the id spaces are disjoint*

**That is false, and R468 said so before I wrote it** — *"the join exists, is exact and total"*, built
from rubric **criterion texts**, which are short exact strings carried in both spaces, needing no
threshold and no new data. Rebuilt from scratch here: **968 of 968 exact, 0 unmatched, 0 ambiguous.**
So E2 is an identification, not a count.

**I wrote a fabricated impossibility into the register of the round whose neighbour (R780) exists
because I had been copying a fabricated impossibility into every round.** The wall was mine alone —
`NEXT_SITE.md` item 2 states the join correctly (it records that it *was* recovered, 968 of 968, and
asks for a shipped key only as a convenience), so the spec was right and the register was wrong.

## E1 · TWO INDEPENDENT INSTRUMENTS ON ONE OBJECT

| | release JSON | scored `sat_*.npz` |
|---|---|---|
| `coval_core` size | **{2: 1, 3: 43, 4: 942}** | **{2: 1, 3: 42, 4: 925}** |
| `coval_full` size | min **4**, max **39**, below 4: **0** | min **4**, max **39**, below 4: **0** |
| fewer than four criteria | **44 of 986 = 4.46%** | **43 of 968 = 4.44%** |

Residual per cell `{2: 0, 3: 1, 4: 17}`, worst **17**, against the D1 bound of **18** — within it.

## E2 · AND THE JOIN MAKES THE AGREEMENT EXACT, NOT MERELY BOUNDED

The 18 released records never scored have core sizes **{3: 1, 4: 17}**.

```
release              {2: 1, 3: 43, 4: 942}
minus the unscored   {      3:  1, 4:  17}
=                    {2: 1, 3: 42, 4: 925}      the scored sat file, exactly
```

⭐ **Two instruments that share no code path — a JSON list length and a count of distinct criterion
indices in a judge-written array — agree on every cell.** The D1 bound was never needed; it was the
right guard to derive in advance and the answer beat it.

Short share among the unscored: **1 of 18** against **44 of 986** overall — the unscored are not
enriched for shortness.

## E3 · WHY A SHORT CORE IS SHORT

Across all **44** short records: **0** empty items, **0** whitespace-only, **0** duplicates within a
record. Criterion text length **31 / 89 / 215** (min / median / max). **The generator produced fewer
distinct substantive criteria** — not a de-duplication or emptiness artifact.

## E4 · AND ITS POWER, STATED RATHER THAN HIDDEN

| population | n | A2 | q | q_resolved |
|---|---:|---:|---:|---:|
| all prompts | 968 | 0.5665 | 1.0000 | 0.9978 |
| 4-criterion only | 925 | 0.5671 | 1.0000 | 0.9978 |

⚠ **This cell could barely have come out otherwise, and I knew that before it printed.** R782 already
had `coval_core` at q_resolved **0.9978** — 1,816 of 1,820 references beaten resolvedly — so dropping
43 prompts had almost no room to move it. **E4 is close to the arithmetic trap**: a quantity computed
and reported as though tested. What it establishes is narrow and worth exactly that much: *the
released core's clause-② standing does not rest on its short prompts.*

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | 986 records · 0 missing a key · 986 distinct ids · **0 duplicates** · 968 scored · overlap 0 | PASS, else exit 2 |
| CROSS-INSTRUMENT | the release JSON and the scored npz, no shared code path | **the round's real control** — exact after the join |
| PLACEBO | recounting the same file returns identical counts | PASS |
| g=0 | an empty list counts 0; records with an empty core: **0** | PASS |
| POSITIVE | injected sizes {0, 1, 4, 39} recovered exactly; the deliberately **broken** counter returns {2, 20, 80, 809} | PASS, floor and ceiling both computed |
| DUPLICATES | **0** — so "18 unscored" is clean arithmetic, not a file with repeats | the registered confound, dead |
| NEGATIVE | ⛔ **not built** — D2: a multiset is order-invariant | the void control of ledger 1125, declined *before* the run |
| SHAM | ⛔ **not built** — D3: a counting instrument has no ingredient to remove | ledger 1131 applied *before* the fact |

**Two controls were declined in the preregistration rather than built and then retracted.** That is
the first time in this arc the lesson transferred forward instead of being re-learned.

## ⛔ ONE MORE DEFECT, SELF-CAUGHT

The object check printed *"per-record join IMPOSSIBLE, marginal only"* — and E2, forty lines later,
built one. **A printed impossibility that the same script refutes is §4's *the verdict string is not a
computation*.** The string now says what is actually absent: a shared ID, not a join.

## WHAT DIED

- **the attack on R782** — the shortness is shipped, confirmed at the source.
- **my own register entry** — a fabricated impossibility, killed inside its own round.
- **the self-refuting object-check string.**

## SCOPE

population 986 released conversations (E1–E3) and 968 scored prompts (E1, E4) · instrument JSON list
length, distinct criterion indices, A2 over all annotators · baseline each instrument is the other's ·
the 1,820-subset class carries **n_eff = 1.1** (R781), so q is a band fraction and never a probability
· regime first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| why the generator produced three criteria | the generator's logs, off-repository (R605: no script in this tree writes 98 of 101 sat artifacts) |
| a judge-free size for the scored side | the sat file is judge-written; the release side is judge-free and agrees |
| cross-release size comparison | release 2 ships `core_generic.json` at k=4 only |
| independently replicated | a second designer; the session prompt forbids agents |

*(The entry "which 18 records went unscored, by id" was listed here in the preregistration and is
removed: it was answerable, and this round answered it.)*

## NEXT

The join is exact and rebuilt in fifteen lines, which makes a question no round has asked cheap: the
release ships **986** conversations and this arc scores **968**, and the 18 are now named. **Whether
those 18 were dropped for a reason that also biases what remains is untested** — computed by this
round's `run.py`, their core-size profile {3:1, 4:17} is indistinguishable from the release's, but
size is one axis of many. The step is to compare the 18 against the 968 on the axes the release
carries and the scoring pipeline consumed — rubric size, conversation length, response count — since a
population filtered on any of those would bound the scope of the numbers this arc reports, each of
which is computed by a `run.py` over exactly the 968.
