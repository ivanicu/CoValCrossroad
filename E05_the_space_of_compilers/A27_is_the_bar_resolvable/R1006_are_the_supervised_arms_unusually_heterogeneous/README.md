# ⚠ THIS ROUND'S MEASUREMENT STANDS; ITS PURPOSE IS MOOT (R1007)

> This round excluded a rival explanation for R1005's Δ. **R1007 then retracted Δ itself** —
> it fails the negative control R1005 declared and never implemented. So the table below is
> still a correct measurement (`indep_k` and `greedy_k` ARE the most homogeneous families in
> the release), but **it is no longer defending anything.** Recorded rather than deleted,
> because the measurement is reusable and the sequence is the lesson: I excluded one rival
> while the control that mattered stood unimplemented one round earlier.

---

# R1006 · the rival explanation for R1005's convergence is excluded

**THE DECISION THIS MAKES SAFE.** Whether R1005's Δ = +0.0828 means **members cohere** or means **the
supervised comparison set is unusually spread**. The second is dead: the two largest supervised
families are the **most homogeneous families in the release**, ranks **1** and **2** of 11.

---

## ⛔ Why R1005's NEXT was not run as written — the identification check killed it first

R1005 asked for a comparison set matched on level and drawn from **outside** the supervised family.
Counted before building:

| caliper | supervised non-members | **non-supervised non-members** |
|---:|---:|---:|
| 0.010 | 3 | **3** (2 distinct — `generic == generic_reprov`) |
| 0.020 | 6 | **3** (2 distinct) |
| 0.040 | 10 | **6** (5 distinct) |

And they are `gen`, `generic`, `topw_k1`, `topw_k2`, `topw_k12` — **mostly the members' own family**,
which confounds in the *opposite* direction. **n = 2 and confounded is not a design.** Running it
would have produced a number.

⭐ **But the reading is testable directly and needs none of that.** *"The supervised set is
heterogeneous"* is a claim about the supervised arms **alone** — no members, no comparator, no level
match. That is why it is identified where R1005's NEXT was not.

## The result

85 distinct arms (deduplicated — a family of copies scores 1.000 for free), 5,000 size-preserving
shuffles per family:

| family | n | within | null mean | z | rank |
|---|---:|---:|---:|---:|---:|
| **`indep_k`** (supervised) | 7 | **0.7663** | 0.6710 | **+3.24** | **1** |
| **`greedy_k`** (supervised) | 7 | **0.7511** | 0.6725 | **+2.68** | **2** |
| `coval_core` | 2 | 0.7297 | 0.6760 | +0.48 | 3 |
| `topvar_k` | 3 | 0.7230 | 0.6706 | +0.79 | 4 |
| `topwvar_k` | 3 | 0.7130 | 0.6720 | +0.61 | 5 |
| `topw_k` | 15 | 0.7018 | 0.6715 | +2.05 | 6 |
| **`oracle_k`** (supervised) | 5 | 0.7016 | 0.6710 | +0.77 | 7 |
| `random_k` | 36 | 0.6970 | 0.6716 | +3.52 | 8 |
| `gen` | 2 | 0.6946 | 0.6706 | +0.21 | 9 |
| `other` | 2 | 0.6583 | 0.6708 | −0.11 | 10 |
| `topabs_k` | 2 | 0.6405 | 0.6740 | −0.30 | 11 |

⭐⭐ **The rival reading required the supervised arms to be unusually spread. They are the most
homogeneous families in the release.** The reading is excluded and R1005's Δ stands as coherence.

## ⚠ Two things this table would let you misread

**① The BH column is driven by family SIZE, not homogeneity.** One family survives BH at q = 0.05 —
`random_k` — with a within-null gap of **+0.025**, while `indep_k`'s gap is **+0.095** and does not
survive. `random_k` has n = 36 (null sd 0.0072); `indep_k` has n = 7 (null sd 0.0294). **BH answers
"resolvably above its own null", which large families win by construction.** The verdict is a **rank**
statement and does not rest on it.

**② The bottom tercile is entirely n = 2 families**, whose within-agreement is a single pair. So
*"no supervised family is in the bottom tercile"* is a weak bar by itself — which is why the claim
made is the stronger positive one: **ranks 1 and 2, z = +3.24 and +2.68.**

## Controls and resolution

| control | result |
|---|---|
| **POSITIVE** | the 14 known-identical pairs score **1.000000** |
| **SATURATION** | a deliberately mixed family scores **0.7238** — the instrument is not pinned at 1 |
| **NEGATIVE / NULL** | families reassembled at random, **size preserved**, 5,000 shuffles. Excludes *"any group of this size scores this high"* |
| **DEDUPLICATION** | 96 → 85 distinct, so no family scores 1.000 by being copies |
| **MULTIPLICITY** | all 11 families reported, survivors **and** non-survivors |

⛔ **The first run used 500 shuffles and reported "0 of 11 survive BH" — a resolution artifact, not a
null.** The permutation p is floored at 1/(N+1) = 0.002 and BH's rank-1 threshold over 11 families is
0.05/11 = 0.0045, so **no cell could have survived whatever the data said**. At 5,000 the floor is
0.0002 < 0.0045 and the test can resolve. The round now prints that comparison so the column cannot
be read as a measurement when it is silence.

⚠ **Engineering note.** The first implementation called a per-pair loop over 968 prompts from inside
the shuffle null — ~2×10⁸ Python operations, still producing nothing when killed. Every quantity here
is a function of one pairwise matrix, so it is built once by broadcasting and all else is a lookup.
Same arithmetic, ~1000× faster.

## ⚠ Impossible here, with what it would require

**The level-matched non-supervised contrast** — N/A, with the counts above as the reason rather than
an assertion. It would require a release with more arms in the members' band that are neither
supervised nor `topw`.

**Construct validity** — N/A as throughout: agreement is not correctness. This round **bounds an
explanation**; it does not validate the definition.

## Alternatives considered

**Run R1005's NEXT at caliper 0.040 with 5 arms.** Refused: 5 arms of which 3 are the members' own
family is a comparison set that answers a different question, and its sign would have been
interpretable either way — the mark of a design that cannot embarrass you.

**Report `random_k` as the most homogeneous family.** Refused — that is the BH column read as
homogeneity, and it is a size effect. Its absolute gap is a quarter of `indep_k`'s.
