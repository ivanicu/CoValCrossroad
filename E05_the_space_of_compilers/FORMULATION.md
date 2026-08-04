# What a "core" is — the formulation, stated once

## ⛔ THE FITTED ARMS' ADVANTAGE VANISHES WHERE THE ANNOTATOR HALVES DISAGREE (R295)

The three admitted fitted arms carry the campaign's largest clause-② margins, and clause ③ passes
for them by its own words: the evaluation annotator (parity 0) **is** held out from the construction
(parity 1). **But the split is by ANNOTATOR while the selection is PER PROMPT** — the fit sees this
prompt's human labels, just a different half of them, and the halves agree at 0.5520 against a
measured chance of 0.3833.

**Clause-② margin by quintile of within-prompt half-agreement:**

| arm | Q1 (halves disagree) | Q3 | Q5 (halves agree) | slope/sd |
|---|---:|---:|---:|---:|
| `oracle_k4_fit1` | **−0.0054** | +0.0633 | **+0.0815** | +0.0337 |
| `greedy_k4_fit1` | **+0.0011** | +0.0640 | **+0.0763** | +0.0297 |
| `indep_k4_fit1` | **−0.0019** | +0.0450 | **+0.0604** | +0.0252 |
| `coval_core` (unfitted) | +0.0083 | +0.0078 | +0.0322 | +0.0085 |
| `topw_k4` (unfitted) | +0.0066 | +0.0188 | +0.0182 | +0.0046 |

> **W-LEAK.** In the quintile where the two annotator halves disagree, **all three fitted arms have
> no advantage at all.** The unfitted arms are roughly flat. Excess slope over the unfitted floor:
> +0.0252 / +0.0211 / +0.0167 against a floor CI width of 0.0156 — **all three clear it.**
>
> **Clause ③ must say "held out from the PROMPT", not merely "from the construction."** A core
> selected using any of a prompt's own human labels is not producible from the conversation, which
> is the input class the rest of the definition is about.

⚠ **The positive control failed, and its failure is the mechanism.** I pre-registered that the
fully-leaky `oracle_k4` must show the **steepest slope**. It does not (+0.0215 vs +0.0337). The
correct prediction is the opposite: `oracle_k4` was fitted on **all** annotators including parity 0,
so it does not *need* the halves to agree — **full leakage BYPASSES the boundary and shows as a high
INTERCEPT** (+0.0441 in Q1, where every other arm is near zero), while leakage *through* the boundary
shows as a **slope**. Corrected control — highest Q1 margin — passes, and identifies `oracle_k4`.

⚠ **The KILL's set had the same defect**: it required all four fitted arms to clear, including the
one this round had just shown uses a different route. **As pre-registered: `False`. On the three
arms it is about: `True`.** Both are printed; neither is discarded.

---

## 🔷 THE DEFINITION AGAINST EVERY OBJECT THE BENCHMARK CONTAINS (R294)

**41 judged arms, not the nine the definition was developed against. 5 admitted (12.2%)** under
clause ③ as tightened by R295 — was 8 while ③ read *"held out from the construction"*.

**⚠ AND `5 admitted` IS A COUNT WITHOUT ITS SAMPLING DISTRIBUTION (R339).** Cluster-bootstrapped
over prompts (2,000 draws × 2 seeds), **this exact set of five recurs in 53.4% of resamples** (seed
2: 55.8%) **across 30 distinct admitted sets.** So the last column below is an **inclusion
probability**, not a checkmark — and two arms the table used to omit entirely are now in it, because
*an arm admitted in one resample of eight is not the same object as one admitted in none.*

| admitted | k | A2 | ① vs random | ② vs size-matched blind | ③ | **P(admitted)** |
|---|---:|---:|---:|---:|---|---:|
| `topw_k6` | 6 | 0.5641 | +0.0714 | +0.0208 | ✓ | **0.995** |
| `topw_k3` | 3 | 0.5632 | +0.0705 | +0.0180 | ✓ | **0.943** |
| `coval_core` | 4 | 0.5665 | +0.0738 | +0.0160 | ✓ no prompt labels | **0.919** |
| `topw_k8` | 8 | 0.5593 | +0.0666 | +0.0152 | ✓ | **0.882** |
| `topw_k4` | 4 | 0.5642 | +0.0715 | +0.0137 | ✓ | **0.763** |
| *`topw_k2`* — **not** admitted at the point estimate | 2 | — | resolved | below MDE | ✓ | *0.130* |
| *`generic`* — **not** admitted at the point estimate | 4 | 0.5514 | resolved | 0 by construction | ✓ | *0.051* |

> **`topw_k4` carries a checkmark and is admitted three times in four. `topw_k2` carries none and is
> admitted one time in eight.** The five most common resampled sets are the published one (0.534),
> `+ topw_k2` (0.122), `− topw_k4` (0.112), `+ generic` (0.037) and `− topw_k8` (0.035).
>
> ⛔ **And clause ② carries 100% of that uncertainty.** `P(clause ①) = 1.000` for every arm with any
> clause-② mass, so `P(both) ≡ P(②)` **by arithmetic** — measured at the set level, not just per arm.
> *(The independence contrast is therefore UNIDENTIFIED here, and the instrument was checked where
> dependence can appear: a synthetic arm with clause ① shrunk to its own MDE shows excess +0.037.)*
| ~~`oracle_k4_fit1`~~ | 4 | 0.6142 | +0.1215 | ~~+0.0637~~ | ✗ **uses this prompt's labels** |
| ~~`greedy_k4_fit1`~~ | 4 | 0.6106 | +0.1179 | ~~+0.0602~~ | ✗ |
| ~~`indep_k4_fit1`~~ | 4 | 0.5941 | +0.1014 | ~~+0.0436~~ | ✗ |
| ~~`oracle_k4`~~ | 4 | 0.6283 | +0.1356 | ~~+0.0779~~ | ✗ fitted on **all** annotators |

> **The three struck rows are the largest clause-② margins this campaign produced, and the
> tightened clause removes all of them.** The definition got stricter and the best result got
> smaller — the direction that costs something.

**Excluded, all 33**, including every `*_sham` (5 of 5), `generic`, `gen`, `full`, `promptecho`,
every `random_k*`, and `oracle_k4` — **which clears ① and ② and is excluded by ③ alone.** That is
the positive control: **③ excludes exactly one arm, and it is the leaky one.** 64 of 82 cells
survive BH.

> **W-SPARSE.** The definition is selective over the **full** arm space, not only over the nine it
> was built against — and the `topw_k` family shows the k-sweep it always lacked: **k = 3, 4, 6, 8
> all admitted; k = 1, 2 and 12 not.**

⚠ **THE FIRST RUN OF THIS CENSUS SAID 3 of 41 AND EXCLUDED `coval_core`.** It intersected all 41
arms' prompt sets, and `promptecho` covers **398** — so every arm was scored at n=398, every MDE
was ~1.6× wider, and two admitted arms were excluded **by lost resolution rather than by anything
about them.** *A census that intersects its members is governed by its smallest member.* Fixed:
each arm is evaluated on **its own** population and the per-arm `n` is printed, so a small-coverage
arm is **visible rather than contagious**.

⚠ **And my inline check of that first result printed "THE VERDICT FLIPS ON WHICH JUDGING IS USED"
— typed above the numbers, which showed it does not** (both judgings of the same four sentences
give BEATS for both arms). The verdict-string failure, committed in a throwaway diagnostic, in the
same hour as building the module that exists to prevent it.

---

## ✅ WHAT STANDS — the claims a next decision can rest on

*Placed first deliberately. This arc produced 18 rounds and a long chain of corrections, and a file
that leads with its ledger is a file about its author. Every line below survived the audit that
follows it.*

| claim | number | scope |
|---|---|---|
| **A core, defined, with both clauses worded against a named object** | see below | A2·annotator, Qwen3.5-2B-Base |
| **Five arms admitted of forty-one** | `coval_core`, `topw_k3·k4·k6·k8` | at 2B; **none** at 0.8B |
| **The k-sweep the arc always lacked** | k = 3, 4, 6, 8 admitted; k = 1, 2, 12 not | `topw` family |
| **Every per-prompt-fitted arm excluded by ③** | 4 of 4, including the campaign's 3 largest margins | R295 |
| **The whole rubric is worse than the same NUMBER of prompt-blind criteria** | −0.0331 [−0.0413,−0.0254] | k=15, resolved |
| **At matched size only 2 of 7 ways of reading the prompt beat four fixed sentences** | 5 lose by up to −0.065 | k=4, all resolved |
| **Criterion count buys nothing past k≈4** | +0.0019 for k=4→16 vs MDE 0.0121 | prompt-blind pool |
| **`generic` is not degenerate** | +0.1077 [+0.0925,+0.1226] over the best of 75 constants | cluster-corrected |
| **The value is in the COMBINATION, not any member** | every criterion of **both** admitted arms loses alone to one generic; both sums win | R298, R300 |
| **Importance is real but COARSE** | +0.0474 block-level, no resolvable rank ordering | R299 |
| **The admitted size band** | **k = 3…8**, entry and exit both resolved | R296 |
| **The admissible band is 12.57 MDE units wide** | chance 0.3833 → human ceiling 0.5519 | measured, not assumed |
| **Clause ① is judge-robust; clause ② is judge-bound** | 6/6 vs 0/3 cells | 2B and 0.8B |
| **The structural wall, priced** | `full` vs `topwvar_k4` needs **3,352 prompts, 3.5×** this release | not a shrug |

### 🔷 THE SIZE QUESTION, ANSWERED AT ITS BOUNDARIES (R296)

The definition has said *"more than one, and 3 to 8 are indistinguishable"* since R276. With clause
② now evaluated against a **size-matched** blind reference at every k, that can be replaced by a
measurement:

| k | clause-② margin | own MDE | |
|---:|---:|---:|---|
| 1 | **−0.0170** [−0.0267,−0.0080] | 0.0135 | **LOSES** — one criterion from the rubric is worse than one generic one |
| 2 | +0.0072 [−0.0017,+0.0155] | 0.0119 | unresolved |
| 3 | **+0.0180** [+0.0099,+0.0261] | 0.0114 | **BEATS** |
| 4 | **+0.0137** [+0.0058,+0.0215] | 0.0109 | **BEATS** |
| **6** | **+0.0208** [+0.0131,+0.0283] | 0.0107 | **BEATS** — largest |
| 8 | **+0.0152** [+0.0077,+0.0225] | 0.0108 | **BEATS** |
| 12 | −0.0040 [−0.0119,+0.0039] | 0.0113 | unresolved |

**Adjacent-k differences — the boundaries separate, the interior does not:**

| step | Δ margin | |
|---|---:|---|
| 1 → 2 | **+0.0241** [+0.0161,+0.0324] | **resolved — the band's entry** |
| 2 → 3 | **+0.0108** [+0.0040,+0.0172] | **resolved** |
| 3 → 4 | −0.0042 | unresolved |
| 4 → 6 | +0.0070 | below resolution |
| 6 → 8 | −0.0056 | below resolution |
| 8 → 12 | **−0.0192** [−0.0245,−0.0138] | **resolved — the band's exit** |

> **So the size statement upgrades from a bound to a measured interval with unresolved interior:**
> **the admitted band is k = 3…8, its entry (between 2 and 3) and its exit (between 8 and 12) are
> both resolved, and no ordering within 3–8 is.** The old wording was right about the interior and
> **silent about the boundaries** — which were measurable all along, once the reference was
> size-matched.

### ⭐ THE COMBINATION FINDING HOLDS FOR BOTH ADMITTED ARMS, WHICH SHARE NO METHOD (R300)

R298/R299 decomposed one selector. `coval_core` is the other admitted arm and a different kind of
object: the release's own compiler output, **rewritten, not selected** — only 8% of its items appear
verbatim in `coval_full`, so it has no importance rank to decompose by. The **structural** question
transfers exactly.

| `coval_core` criterion, alone | A2 | vs 1 generic | |
|---|---:|---:|---|
| #0 | 0.5545 | +0.0114 | **below resolution** |
| #1 | 0.5284 | **−0.0147** | **LOSES** |
| #2 | 0.5258 | **−0.0173** | **LOSES** |
| #3 | 0.5059 | **−0.0372** | **LOSES** |
| **all four** | **0.5671** | **+0.0163** [+0.0086,+0.0236] vs *four* generic | **BEATS** |

**No singleton beats one generic criterion.** The sum beats its own best singleton by **+0.0126**
[+0.0059,+0.0196]. **6 of 6 cells survive BH.**

> **So every criterion of BOTH admitted arms loses alone to a single generic one, and both sums
> win** — across two compilers that share no method: one **selects** from a rubric by human
> importance, the other **rewrites** from the conversation. That is the widest comparison this
> release supports, and it is the strongest form of *the value is in the combination, not in any
> member* available here.

⚠ **What "generalises" means in that sentence**: *holds for both of the two admitted arms*, and
nothing more. A third compiler is not available, and the claim is scoped to two objects.

### 🔷 IMPORTANCE IS INFORMATIVE AT BLOCK RESOLUTION, NOT AT RANK RESOLUTION (R299)

R298 left a tension: **selection** by importance carries +0.0715 over a random draw, while **no rank
ordering** within the top four is resolvable. Both cannot be about the same quantity. `sat_topw_k8`
stores ranks 1–8 in importance order, so **ranks 5–8 are their own k=4 arm** — never scored until now:

| block | A2 | |
|---|---:|---|
| ranks 1–4 | **0.5664** | |
| ranks 5–8 | **0.5404** | |
| random k=4 | 0.4930 | |

| contrast | | |
|---|---:|---|
| ranks 1–4 − ranks 5–8 | **+0.0260** [+0.0177,+0.0346] | **BEATS** |
| ranks 5–8 − random k=4 | **+0.0474** [+0.0372,+0.0573] | **BEATS** |
| ranks 1–4 − random k=4 | **+0.0734** [+0.0645,+0.0834] | **BEATS** |

> **The +0.0734 decomposes into +0.0474 for being in the top eight at all (65%) and +0.0260 for
> being in the top four rather than 5–8 (35%).** Both survive BH; 4 of 4 cells do.

**So importance is informative at BLOCK resolution and not at RANK resolution** — blocks of four
separate, individual ranks (R298: 1v2, 2v3, 3v4, all unresolved) do not. That is exactly the
signature of a **noisy measurement of a real quantity**: averaging four recovers signal no single
one carries, which is also why every criterion loses alone and the sum wins.

**Three rounds now explain the k-curve together**: the tie mechanism is dead (R297), the value is in
the combination (R298), and the combination works because importance is real but coarse (R299).
Positive control: ranks 1–8 beat random k=8 by +0.0600 on this population — the comparison the
definition already admits, reproduced where the decomposition is computed.

### 🔷 THE VALUE IS IN THE COMBINATION, NOT IN ANY MEMBER (R298)

`sat_topw_k4` stores its four criteria **in descending human-importance order**, so each can be
scored alone. Every one of them, alone, is at or below **a single generic criterion** — and together
they beat **four** generic ones:

| criterion, alone | A2 | vs 1 generic | |
|---|---:|---:|---|
| rank #1 (most important) | 0.5364 | −0.0061 | below resolution |
| rank #2 | 0.5314 | −0.0111 | below resolution |
| rank #3 | 0.5233 | **−0.0192** | **LOSES** |
| rank #4 | 0.5225 | **−0.0200** | **LOSES** |
| **all four summed** | **0.5642** | **+0.0216** | **BEATS** |
| *one generic criterion* | *0.5425* | | |

**And no rank ordering among the four is resolvable** — adjacent pairs 1v2 −0.0058, 2v3 +0.0081,
3v4 +0.0008, rank1−rank4 +0.0031 against an MDE of 0.0149, **none separating.** The point-estimate
order is [2, 1, 3, 4], which is not the importance order, but **nothing in it is measured.**

> **So the human importance ranking carries no resolvable predictive ordering at its own top** —
> a weaker and different claim than *anti-predictive*, which the round's own adjacent-pair table
> refutes. **`topw` succeeds at k ≥ 3 by aggregation over a list whose order is unverified**, and
> the definition admits it on that basis.

This is also the k-curve's explanation: **k=1 loses because no single rubric criterion beats a
generic one; k ≥ 3 wins because aggregating rubric criteria beats aggregating generic ones.**
Positive control: all four beat the best singleton by **+0.0328** [+0.0251,+0.0400] — summation is
doing the work, and doing a lot of it.

⚠ **`k=1` LOSING HAS NO MECHANISM, AND THE OBVIOUS ONE IS DEAD** (R297). I pre-registered that a
single high-importance criterion is often a specific requirement all four responses either meet or
miss, so it emits **ties**, and a tie can never match a human's non-zero sign. Measured:

| k=1 statistic | `topw` | generic | Δ | |
|---|---:|---:|---:|---|
| across-response spread | 0.1362 | 0.1401 | −0.0038 | **unresolved** |
| tie rate | **5.10%** | **4.06%** | +1.0 pt | **below resolution** (kill threshold was 5 pts) |
| **A2 on NON-TIED pairs only** | **0.5435** | **0.5585** | **−0.0150** | the deficit **survives** removing ties entirely |

> **The tie explanation is dead.** Restricting to pairs where `topw_k1` emits a non-zero sign leaves
> the deficit essentially unchanged (−0.0150 against an overall −0.0170). So **the single criterion
> the humans rated most important predicts their own pairwise preferences worse than *"the reply is
> accurate and factually correct"* — and this file has no mechanism for that.** It is recorded as an
> open finding, not resolved by the nearest available story.

Positive control: `topvar_k4`, which selects **by** spread, exceeds `topw_k4` at the same k
(**0.5663 vs 0.4531**) — the spread statistic is not blind, so the null above is a measurement.

Positive control: k=1 → k=4, the widest span in the band, separates at **+0.0307** [+0.0212,+0.0398]
against an MDE of 0.0133 — the design can see k. Negative: k=4 against itself exactly 0. 10 of 13
cells survive BH.

**The cell census, closed** (R292): **134 published cells** carrying an effect and an interval.
**71 judgeable** (an MDE *and* a stored verdict) — **0 disagreements** with `report.verdict()`.
The remaining 63 were one bucket labelled *unjudgeable*; they are two:

| | | |
|---|---:|---|
| **no MDE stored** | 45 | all R304 — **a real gap**, and its 45 cells are the same pairs R306 recomputed with per-cell MDEs, so they are **superseded, not unchecked** |
| **no VERDICT stored** | 18 | all R276 — it computes an MDE and never writes a verdict. **Nothing to check: you cannot audit a claim that was never made** |
| neither | 0 | |

**Instruments built, reusable on any next object:** `corebench/report.py` (an effect cannot be
printed without its interval; the verdict is computed, not typed) · `R292`'s cell census (every
published cell re-judged, with its own positive control) · the four-budget baseline curve (R287) ·
the 16-criterion prompt-blind pool, judged once so any k is free.

**Decisions closed, so a next person need not reopen them:** which target (A2·annotator, argued on
resolving power, R289) · what a baseline may be (selection budget named, R287) · whether the clause
measures cores or my vocabulary (1,820 subsets enumerated, R286) · whether the price survives
size-matching (it does, and it costs `full` its admission, R307).

---

## ⭐ THE DEFINITION AS IT STANDS, 2026-08-03 — both clauses restated to say what they test

> **A core is a set of criteria, built WITHOUT any human label for the conversation it describes,**
> **whose verdicts agree pairwise with that conversation's human annotators**
> **① better than the same number drawn at random from that conversation's own rubric, and**
> **② better than the same number that never read the conversation at all.**

---

## ⛔ NEITHER CLAUSE'S WORDING DESCRIBES WHAT IT COMPUTES (2026-08-04)

The heading above says *"both clauses restated to say what they test."* Measured against
`R294/run.py`, **neither does** — and the gaps run in opposite directions.

| clause | what the definition SAYS | what `R294` COMPUTES | the gap |
|---|---|---|---|
| ① | *"the same number drawn at random from that conversation's own rubric"* | `random_k4_s0` — **one fixed draw at k=4, seed 0**, for every arm | **not size-matched** (23 of 41 arms have k ≠ 4; the correct per-k references exist on disk, three seeds each, unused) and **not re-drawn** (one seed) |
| ② | *"the same number that never read the conversation at all"* | `POOL[0:k]` — the **first k rows** of a curated 16-criterion pool | criterion sets that never read the conversation but were **crowd-written** do *no better* than clause ①'s own reference, and **2 of 5 are resolvably worse** (R348). The clause tests a **curated instrument**, not blindness — and *which* subset was decided by **file order**, at the **93.7th percentile of all 1,820 size-4 subsets** (rank 1707/1820, exhaustive) |

> ⛔ **AND CLAUSE ② CANNOT BE REPAIRED BY RESTATING IT RELATIVELY (R359).** The clause is
> stated ABSOLUTELY — beat `POOL[0:k]`, a level every judge rescales — and the definition
> admits **5 arms at 2B and 0 at 0.8B**. Self-normalising it (*beat the p-th percentile of the
> blind class as scored by whatever judge is in use*) changes **nothing at matched strictness**:
> at the published reference's own **93.7th** percentile the two forms give **9 vs 9** at 2B and
> **0 vs 0** at 0.8B, on 42 arms. The relative form admits arms at 0.8B only for p = 50–75,
> every one **below 93.7 by construction** — a lower bar, not a better definition.
> **The judge-dependence is in the ARMS' ORDERING** (R356/R357 measured one family inverting),
> and a reference sits above an ordering without being able to reorder it. A judge-invariant
> definition needs a judge named inside its text, or a different observable.

**Clause ② is the binding one** (R347), so the second row is the one that matters: **the entire
admitted set rests on a reference whose wording admits any blind set and whose implementation is one
arbitrary slice of one curated pool.** The set moves **7 → 0** across ~0.019 of reference level.

### Two repairs, and choosing between them is a DECISION, not a measurement

**(A) Narrow the wording to what is computed** — *"better than a size-matched subset of the
benchmark's generic criterion pool."* Honest immediately, and it makes the definition
**benchmark-specific**: it would not transfer to a release without that pool.

**(B) Broaden the implementation to match the wording** — draw the reference at random, per arm,
per seed, from a stated population. Then **which population, and with how much search?** That is
R287's unanswered budget question, and it is now load-bearing rather than open.

**Neither is chosen here.** What decides it is the measurement that has not been run: **permute the
pool and recount**, turning the reference's rank into a distribution over ADMITTED SETS —
the enumeration below settles where the subset sits; it does not yet say which arms survive at each
level. Until then the honest statement is that **the published five is one draw from a distribution
whose spread is unmeasured, and the definition's own words do not name the draw.**

---

## ⛔ CLAUSE ① HAS NEVER EXCLUDED ANYTHING CLAUSE ② ADMITS (R347, 2026-08-03)

Over all **41** judged arms, the cell **(① fails, ② passes)** is **empty**; clause ② excludes **8**
that ① admits; every arm clearing ② clears ① by **≥5.36× its own MDE**. **Clause ② carries the
entire boundary.**

**The mechanism, and it could have come out the other way:**

| reference | level |
|---|---:|
| ① a random draw from **this prompt's own rubric** | **0.4922** |
| ② a size-matched **prompt-blind** set | **0.5462** |

**② − ① = +0.0540; minimum over 41 arms +0.0470 — never negative.** The clause-② reference outscores
a random draw of the conversation's own criteria on every arm, and that is what makes ② bind.

**⚠ THE MECHANISM SENTENCE WAS TOO GENERAL, AND IS RETRACTED (R348).** What beats the own-rubric
draw is the **curated** pool — `sat_genericpool16`, sixteen criteria authored for the benchmark —
**not blindness**. Crowd criteria applied to the *wrong* conversation: **0 of 5 resolvably better,
2 resolvably worse, mean c1 −0.0170**, against `generic`'s **+0.0587**. *Blind* and *curated* are two
properties and I generalised the second into the first. **Clause ②'s reference is hard because it is
a curated instrument**, so R287's unanswered question — what selection budget a baseline should
have — is load-bearing for the whole clause-② boundary. → `R348_is_it_blindness_or_curation`


**⛔ The empty cell is a DERIVATION, not a measurement — and my first reading of it was wrong.**
An arm is a counterexample iff `A > ref₂ + mde₂` and `A ≤ ref₁ + mde₁`, so the region is non-empty
iff **`GAP < SLACK`**, with `GAP = ref₂ − ref₁` and `SLACK = mde₁ − mde₂`. Measured: **min GAP
0.0470, max SLACK 0.01217 — GAP exceeds SLACK by 3.9× on the tightest arm, and GAP ≥ SLACK on all
41.** No arm of any size this benchmark contains can be a counterexample.

*The first version of this round tested `mde₁ ≤ mde₂` — which forces the implication but is not
required for it — called 18 arms "contingent", and closed that a counterexample was "constructible
in principle". None of those 18 can host one. A sufficient condition stood in for a
necessary-and-sufficient one, and it made the result look weaker than it is.*

⚠ It is a derivation **about this release**: it rests on `ref₂ − ref₁ ≈ +0.05` against MDEs of
0.011–0.013. A release with a weaker blind reference, or a far more precise design, could break it.

Swept over MDE multipliers 0.5–2.0: **no multiplier produces a counterexample, and none makes the
region non-empty either.** **Permuting the `(c1, c2)` pairing fills the cell (6, 5, 6 across three
seeds)** — the emptiness is a property of which arm
carries which margin, not of the marginals.

> **On this release clause ① is implied by clause ②.** It is not deleted — the implication rests on
> a measured reference gap, not on the definition's own logic, and a different release could break
> it. But the definition must stop reading as though both clauses contribute an exclusion, and the
> next round must not go looking for a counterexample: **the arithmetic says there is none to find
> here.**
→ `R347_does_clause_one_ever_bind`

---

## ⭐ CLAUSE ② NOW NAMES ITS REFERENCE BY A PROCEDURE (R327–R333, 2026-08-03)

**Clause ① named a procedure — *drawn at random from that conversation's own rubric*. Clause ②
named a CLASS and no member**, and for forty rounds the campaign quietly supplied one, four
different ones in four different tables. Six rounds establish what the reference must be, and one
establishes what the definition can never say here.

### ⛔ ...BUT THE REFERENCE'S OWN SUBSET WAS CHOSEN BY FILE ORDER (read from the source, 2026-08-03)

`R294/run.py:140` builds the clause-② reference as **`POOL[0:k]`** — *the first k criteria in
`sat_genericpool16.npz`*. Not a random draw, not a best-of, not a stated rule: **the order the file
happens to be in.**

**`POOL[0:4]` sits at the 93.7th percentile of ALL 1,820 size-4 subsets — rank 1707 of 1820.**
Exhaustive enumeration, n=968 prompts, all annotators, 11 s:

| min | p25 | median | p75 | max | mean | sd |
|---:|---:|---:|---:|---:|---:|---:|
| 0.5144 | 0.5329 | 0.5391 | 0.5446 | **0.5575** | 0.5386 | 0.0082 |

**published `POOL[0:4]` = 0.5504.** Not merely above average — **in the top 6% of every subset the
pool can produce**, chosen by file order.

⚠⚠ **AND THIS RANK WAS ALREADY ON THIS PAGE.** Line ~1039 has said, since long before I measured
it: *"The incumbent `generic` sits at the 93.7th percentile of 1,820 … the top 7% of every quadruple
the pool can form."* `POOL[0:4]` scores **0.5504** and R287's hand-picked `generic` scores **0.5504**
— the same object. So the enumeration above is a **VERIFICATION**, not a finding, and what is
actually new is narrow: that the census's `POOL[0:k]` **is** that incumbent subset, and the
distribution's shape (min 0.5144, median 0.5391, sd 0.0082), which the existing line does not give.

⛔ *And it retracts a "63rd percentile" I published one cycle earlier **into this same file** — a
figure computed against three of R287's reference points rather than the distribution, and
contradicting a number already sitting 700 lines below it.* The prior-art gate exists for exactly
this and I did not run it on my own document.

**Why it matters:** the admitted set moves **7 → 0** across a reference range of ~0.019, and
`coval_core` drops out at **+0.0054** above the published level. The distance from here to
"budget 1820" is **+0.0055**.

### ⛔ AND THE PUBLISHED FIVE RECURS IN 7.7% OF POOL ORDERINGS (R353, 2026-08-04)

The census's reference is `POOL[0:k]` — a **prefix of a file**. Permuting the pool and recounting,
400 orderings × 2 seeds:

| | seed 3531 | seed 3532 |
|---|---:|---:|
| **P(published set)** | **0.077** | **0.070** |
| distinct sets | 24 | 25 |
| mean \|admitted\| | 6.90 | 6.78 |

**The published five is a TAIL draw, not a central one** — the reference sits at the 93.7th
percentile of size-4 subsets, so the baseline is unusually strict and the set unusually small. A
typical ordering admits **about seven**.

| arm | P(admitted over orderings) | in the published five? |
|---|---|---|
| `coval_core` · `topw_k6` · `topw_k4` · `topw_k8` · `topw_k3` | 0.94 – 1.00 | ✓ |
| **`generic`** | **0.76 – 0.80** | ✗ |
| **`topw_k2`** | **0.69 – 0.72** | ✗ |
| **`topw_k1`** | **0.42 – 0.43** | ✗ |
| `gen` | 0.045 | ✗ |

⭐ **Two uncertainty sources give opposite pictures of the same arms.** R339 bootstrapped over
**prompts**: `topw_k2` admitted 13% of resamples, `generic` 5%. This varies the **reference subset**:
`topw_k2` **69–72%**, `generic` **76–80%**. Both correct, different questions — sampling noise says
those arms are marginal; the choice of baseline says they are admitted unless the baseline is
unusually strict, **which the published one is.** Neither number alone characterises the arm.

*Reproduction control: the identity permutation yields exactly the committed five.*
→ `R353_the_admitted_set_under_every_pool_order`

### ⛔⛔ AND AT THE REFERENCE THIS CAMPAIGN ARGUED FOR, THE DEFINITION ADMITS TWO (R354, 2026-08-04)

R331 derived the rule — put the reference high in the blind distribution, **p99 not p94** — because
every one of the 1,820 blind k=4 subsets is a member of clause ②'s own reference class, and a
reference admitting any of them is refuted by the clause's own words. **The rule was never
evaluated.** Applied:

| percentile | ref level (k=4) | \|admitted\| | set |
|---:|---:|---:|---|
| 50 | 0.5391 | 7 | + `generic`, `topw_k2` |
| 75 – 95 | 0.5446 – 0.5511 | **5** | the published five, **flat across the whole band** |
| **99** | **0.5545** | **2** | **`coval_core`, `topw_k6`** |

**The published p93.7 reference is not where the collapse happens** — five is stable from p75 to p95.
It falls to two only at p99, and p93.7 admits **3** blind sets where p99 admits **0**.

⚠ **But the "two" is a measurement of an unstable quantity.** R332 swept 46 blind references across
**0.25 of `coval_core`'s own MDE** around this altitude and found **two distinct admitted sets inside
that quarter-MDE** — *"the admitted set is not a stable quantity at this site, and any statement of
the form 'N arms are admitted' inherits that."* R354's p99 lands inside that band. R332 reports
**three** there and R354 **two**, and they do not contradict: R332 moves only the k=4 reference while
holding k=3 and k=6 at their own closure levels, R354 puts every k at the same percentile, so
`topw_k3` faces a different bar in each. **What survives every reference at this altitude is
`coval_core` and `topw_k6`** — and that pair, not a count, is what the altitude supports.

*Controls: the census's own reference reproduces the committed five exactly; the p99 level matches
R331's committed 0.5547 with a resolvable blind-admission rate of 0; the set shrinks monotonically.*
⚠ **And p99 is not itself established as safe at every k (R355).** The minimal reference above which
the clause is *always* closed sits at **p99.5 for k=6 and k=8** — so a rule that puts every k at p99
is below safe at two of them. The "two" above is therefore bounded on **both** sides: unstable within
0.25 MDE (R332) and measured at a reference that is not closed at all k (R355).

→ `R354_what_the_safe_reference_admits`, `R332_the_closure_level_derives_reading_A`,
`R355_is_the_closed_region_upward_closed`

### ① The reference — computed, not chosen

> **THE CLOSURE TEST.** A candidate clause-② reference is **CLOSED** if **no member of clause ②'s
> own reference class** — no prompt-blind criterion set of the same size — is resolvably better than
> it. **The reference is the LOWEST closed level of the size-matched blind class.**
> Weaker admits an object the clause exists to exclude; stronger is gratuitous.

Measured over **every** `C(16,k)` subset of the 16-criterion blind pool — the class, not a sample:

| clause-② reference | its percentile | blind sets it admits, of 1,820 |
|---|---:|---:|
| a random draw (`p50`) | 50 | **424 · 23.3%** |
| `p90` | 90 | 16 · 0.9% |
| **the reference this page published** | **93.7** | **3 · 0.16%** |
| **the closure level** | **96.4** | **0** |
| the class maximum | 99.9 | 0 |

**Two things this settles.** The reference the campaign was using is **not closed** — it admits three
prompt-blind quadruples. And *"better than the BEST prompt-blind set"* is **sufficient and not
minimal**: closure sits **0.0055 below** the class max, because clearing requires beating the
reference by an MDE.

**Closure levels, per k:** `k=3` 0.5519 · `k=4` 0.5520 · `k=6` 0.5519 · `k=8` 0.5505.

> ⛔ **THOSE ARE THE FIRST CLOSED REFERENCE, NOT THE LOWEST SAFE ONE — and the difference is real
> (R355).** The definition of closure used above says *"anything stronger is gratuitous"*; the code
> takes the **first** grid point whose blind-admission rate is 0. Those coincide only if the closed
> region is an **upward set**, and at **6 of 9 k it is not**: **18 references stronger than the
> published closure admit blind sets again.** Corrected minimal-safe levels — `k=3` **0.5530**
> (p96.2) · `k=4` **0.5537** (p98.5) · `k=6` **0.5531** (p99.5) · `k=8` **0.5517** (p99.5); `k=1`,
> `k=2` and `k=15` unchanged.
>
> **The mechanism is this page's own, one axis over.** R331 established that *a paired MDE is a
> property of the PAIR, not of the design* — a near-neighbour clears its own resolution on a tiny
> gap. That was applied to **arms**. Admission compares a class member against a reference **vector**
> on `(e>0) & (|e|≥mde)` with a **per-prompt paired** sd, so a reference with a **higher mean** but a
> different **profile** can admit a near-neighbour. Measured excess **+1.19 shared criteria over each
> k's own null (MDE 0.42, n=25 pairs), positive at all six violating k.**
>
> **The rival world was built, not imagined:** flatten every reference to a constant vector at its
> own mean — admission becomes a pure threshold and upward-closure is algebraic — and violations fall
> to **0 at every k**. **R358 replicates this at Qwen3.5-0.8B-Base on the identical pool**:
> violations at both judges at overlapping k (12, 13), none at the 9-point grid at either, and the
> synthetic control null at both. **So the defect is the ESTIMATOR, not the model.** At 0.8B **no arm
> clears any reference at or above that judge's own closure**. Placebo 0/315 self-admissions; the detector fires on an injected weak
> reference and not on an injected class-max one in the same slot.
>
> ⚠ **And the number is a lower bound, not a converged one.** The 9-point grid finds **0**
> violations, 45 finds **18**, 91 finds **50** — a coarse grid cannot see a reference it never
> evaluates. **This is why R331 reported none.**

⛔ **What does NOT work, measured rather than argued.** *Budget-matching* — giving each arm a
reference matched to its own selection budget — **admits `generic` at all five readings tested**.
`generic` is one criterion set across 968 prompts: a member of the class clause ② quantifies over.
As a singleton it draws the *weakest* reference and clears it. **A rule that rewards not searching is
correct about selection and wrong about this clause.**

**⚠ AND THIS RULE GOVERNS CLAUSE ② ONLY (R334).** Clause ①'s reference class is
**quality-degenerate**: its members are *per-prompt* random draws, so they are exchangeable and
the class has no percentile to sit at. Measured — across-member sd over sampling error, **τ/se =
0.72 for clause ① against 3.61 for clause ②**, where exchangeability predicts exactly **1/√2 =
0.707**. Clause ①'s closure rate is **0.0000**. So clause ② needs a computed reference and clause ①
does not, and the reason is the shape of the class rather than the size of the margin.

### ② The admitted set is a BAND, not a list

**Two distinct admitted sets lie inside 0.25 of one MDE.** Sweeping the k=4 reference across the 46
blind references between the closure level (0.551951) and the best held-out of 1,820 (0.554602) — a
width of **0.0027**:

| at the closure level | at the top of the band |
|---|---|
| `coval_core` · `topw_k3` · **`topw_k4`** · `topw_k6` | `coval_core` · `topw_k3` · `topw_k6` |

> **So no sentence of the form "N arms are admitted" is supportable here** — including this page's
> own. `topw_k4`'s admission turns on a reference difference four times smaller than the design can
> resolve.

### ③b ⛔ REGISTER — clause ③'s TESTABILITY, measured twice and bounded (R335–R338)

**Clause ③ is decided per arm by reading `select_core.py`.** That is an annotation, not a
measurement — and whether it *could* be a measurement has now been tested along both available
routes. Both bound out.

**Route 1 · through PERFORMANCE — REFUTED.** R295's leak slope was the campaign's only clause-③
instrument. Run blind over 41 arms it has sensitivity **1.000** and specificity **0.886** — and its
four false positives are **exactly the admitted set** (`topw_k6`, `topw_k8`, `coval_core`,
`topw_k3`), all borderline. The reason: **`corr(slope, A2) = +0.934`.** Quality-adjusted, the
annotated-leaky arms carry excess z `[+0.45, +0.35, −0.12, −3.25]` against the false positives'
`[+0.36, +0.32, −0.39, −0.52]` — **complete overlap** — and `oracle_k4`, the *maximally* leaky arm,
sits **3.25 sd BELOW** what its quality alone predicts. **There is no residual leak signal.**

> **The confound is structural, not fixable.** Fitting on labels is *what makes an arm better*, so
> any detector built on performance measures the leak's **effect** and cannot be separated from it.
> This also retracts R335, whose 32.9-sd dose-response separated **dose-induced quality**.

**Route 2 · through SELECTION — works for one rule family, and only that one.** Label-free features
of the *selected criterion set* (importance weight, satisfaction variance, rubric position, criterion
length, token Jaccard, verbatim-match rate — none touching a human label):

| | within-arm | held-out-**arm** | folds |
|---|---:|---:|---|
| structure only | 0.836 | 0.834 | 0.871 · 0.748 · 0.860 · 0.857 |
| text only | 0.654 | 0.658 | — |
| **structure + text** | **0.870** | **0.866** | 0.901 · **0.789** · 0.889 · 0.885 |

*(398 prompts · 15,920 rows · planted-signature control 1.000 · arm-label shuffle 0.509 · pure noise
0.520.)*

**But held out by MECHANISM rather than by arm, it reaches chance: 0.510**, with a flat dose
response. **And the number is unreadable as rule-specificity** — trained *on* that second mechanism
the same features reach only **0.565**, so they are blind to it, and a transfer failure against
something you cannot see is silence.

> **Register entry:** *clause ③ is detectable for the release's one annotated rule family
> (`select_core.py`'s fitted rules) at held-out-arm AUC **0.866**, folds 0.789–0.901; **invisible**
> for a second, manufactured mechanism (0.565 even trained on it); and **no third mechanism exists
> on this release** to test against.* What it would require: a release carrying more than one leak
> family, or a construction log.

**So the ✓/✗ in the clause-③ column below remains a source-reading.** It is corroborated for the
family it was read from, and unproven for any other route.

---

### ③ ⛔ REGISTER — the admitted set is structurally unresolvable on this release

| | |
|---|---:|
| σ_b · σ_w of the paired clause-② difference (`coval_core`) | 0.1077 · 0.1777 |
| MDE at 968 prompts × every annotator | **0.0106** |
| floor as annotators → ∞ | **0.0097** |
| what infinite annotation buys | **7.6%** |
| prompts needed to resolve the 0.0027 band | **12,494 — 12.9× the release** |

`MDE(N,m) = Z·√(σ_b² + σ_w²/m)/√N`, so the annotator axis is **bounded below by σ_b** and only the
prompt count moves the floor. The release ships 968 prompts and **15,593 annotations at a median of
16 per prompt — that axis is spent.**

> **Register entry:** *deciding which arms clause ② admits — requires a release of ~13,000 prompts
> at this annotation depth. **Not achievable by any re-analysis of this one.*** No cleverer
> reference, estimator or aggregation reaches it.

**What the definition may therefore assert:** `coval_core` is admitted at every closed reference
tested. The `topw` family sits **on the boundary**, and this site cannot separate its members from
it. That is the honest output, and it is smaller than the table below was written to carry.

⛔ **"held out from the core's own construction" is new, and it is there because R293 fired.** The
previous wording said *"a held-out human annotator"* — an **adjective nothing computed.** Applied to
`oracle_k4`, an arm `select_core.py` describes in its own docstring as *"LEAKY BY CONSTRUCTION — an
upper bound, labelled, never a candidate"*, the definition **ADMITTED it**: ① +0.1333, ② +0.0757,
both resolved, both BH survivors.

> **It was never a candidate to its AUTHOR. That is not the same as being excluded by the
> DEFINITION** — and I do not get to reject it by pointing at a docstring, which records intent,
> not a verdict.
>
> **An adjective in a definition is not a clause unless something computes it.** `held-out` sat in
> the sentence for as long as the sentence existed and caught nothing, because no cell ever asked
> *held out from what?*

⚠ **AND THE SAME ROUND FOUND SOMETHING THAT IS NOT A DEFECT AT ALL.** Three arms fitted on
**parity-1 annotators and evaluated on parity-0** — genuinely disjoint — are all admitted, and they
beat every arm in the main table on clause ②:

| arm | ① vs random | ② vs prompt-blind | |
|---|---:|---:|---|
| `oracle_k4_fit1` | +0.1056 [+0.0944,+0.1170] | **+0.0460** [+0.0360,+0.0555] | held out, admitted |
| `greedy_k4_fit1` | +0.1047 [+0.0935,+0.1159] | **+0.0451** [+0.0356,+0.0545] | held out, admitted |
| `indep_k4_fit1` | +0.0929 [+0.0823,+0.1035] | **+0.0333** [+0.0240,+0.0419] | held out, admitted |
| *`coval_core`, for comparison* | +0.0738 | *+0.0151* | the release's own compiler |

> **A core fitted to human judgements and honestly held out beats the release's own compiler by
> 3× on clause ②.** That is a finding about what a core CAN be, not a defect — and it is the first
> route this campaign has found that clears the prompt-blind arm by a wide margin.

Positive control: `oracle_k4` scores 0.5977 on the annotators it was fitted on against 0.4927 for
the best honest reference — the fit took, and by a wide margin. Negative control: `gen_sham` loses
at −0.0688. 8 of 8 cells survive BH.

⚠ **"a held-out human annotator's, pairwise" is load-bearing, not throat-clearing** — R288 swept six
defensible agreement targets and got **four different admitted sets**. `predicts held-out human
judgement` is underdetermined on this release; the statistic is part of the definition.

**And the choice of *that* statistic is now argued rather than inherited** (R289). Its closest rival,
`A2·consensus`, agrees on the ordering at **Kendall τ = +0.956** and admits the same two arms — so
the two cannot be separated on what they say, only on how much they can say:

| target | measured chance | ceiling | band | **pairs RESOLVED** | median \|gap\|/MDE |
|---|---:|---:|---:|---:|---:|
| **A2 · annotator** | 0.4308 | 0.5519 | 0.1211 | **36 / 45** | **2.56** |
| A2 · consensus | 0.4895 | 0.6671 | 0.1776 | 34 / 45 | 2.25 |

> **The wider band resolves LESS**, which is the part worth keeping: `A2·annotator` averages over
> ~16 annotator comparisons per prompt, shrinking per-prompt variance, while `A2·consensus` is a
> single vector per prompt. **Denoising the TARGET does not compensate for losing the averaging over
> the COMPARISONS.** The incumbent turned out to be the defensible choice — but it was defensible by
> accident until it was measured, and the kill was written so it would have had to change.

Controls: self-comparison exactly 0 under both; the same random rule at two seeds unresolved under
both (−0.0055 vs MDE 0.0140; −0.0096 vs MDE 0.0229). 74 of 90 cells survive BH.

⚠ **Resolving power says nothing about whether either target is the right GOAL.** A sharper
instrument pointed at the wrong thing is sharper. Construct validity remains **structurally
impossible here** — it needs an external criterion the release does not carry.

**Why both clauses are worded against a named object rather than against "chance".** R285 measured
chance directly, by drawing the comparison partner from a *different* prompt: **0.3833** human-vs-
human, **0.4257** for `random_k4` vs human. **Every arm in this benchmark is above chance** — so a
clause saying "better than chance" excludes nothing, while the test that was actually being run
("better than `random_k4`") excludes four. The wording now matches the test.

### The complete evidence table — all 15,593 annotations, each cell against its own MDE

| arm | A2 | ① vs random-from-rubric (eff / its own MDE) | ② vs size-matched prompt-blind | verdict |
|---|---:|---|---|---|
| **`coval_core`** | 0.5665 | **+0.0738** / 0.0132 = **5.61×** | **+0.0262** [+0.0192,+0.0332] | **ADMITTED** |
| **`topw_k4`** | 0.5642 | **+0.0715** / 0.0128 = **5.58×** | **+0.0239** [+0.0169,+0.0312] | **ADMITTED** |
| `generic` | 0.5514 | +0.0587 / 0.0144 = 4.09× | **0 by construction** | excluded (②) |
| `gen` | 0.5352 | +0.0425 / 0.0149 = 2.84× | **−0.0153 … −0.0194** at the two references that can resolve | **excluded** (②) |
| `full` | 0.5087 | +0.0160 / 0.0113 = **1.41×** — the thinnest resolved row | **−0.0331** [−0.0413,−0.0254] | excluded (②) |
| `topwvar_k4` | 0.5040 | +0.0113 / 0.0134 = **0.84×** — BH survivor, **below its own MDE** | — | **not resolvably better** (①) |
| `topabs_k4` | 0.4894 | −0.0033 / 0.0154 = 0.21× | — | **not resolvably better** (①) |
| `topvar_k4` | 0.4863 | −0.0064 / 0.0134 = 0.48× | — | **not resolvably better** (①) |
| `gen_sham` | 0.4828 | −0.0099 / 0.0165 = 0.60× | — | **not resolvably better** (①) |

⛔ **AND CLAUSE ② IS WHERE THE DEFINITION ACTUALLY BINDS — AT 1.19× ITS OWN MDE (R326).** The
column above carries intervals but not the eff/MDE ratio, so a reader can see that an interval
excludes zero and cannot see how close the effect is to what the design could resolve. Clause ② has
**two published references** and the table shows one; both, with their ratios:

| arm | ② vs neutral pool-16 (R307, shown above) | ② vs `generic` at matched k=4 (R308) |
|---|---|---|
| **`coval_core`** | +0.0262 / 0.0099 = **2.63×** | +0.0151 / 0.0107 = **1.41×** |
| **`topw_k4`** | +0.0239 / 0.0100 = **2.39×** | +0.0128 / 0.0108 = **1.19×** |
| `gen` | −0.0051 / 0.0109 = 0.47× — **unresolved** | −0.0162 / 0.0119 = 1.36× |
| `full` | −0.0331 / 0.0117 = 2.84× | — |

> ### The two admitted arms clear clause ① by **5.6×** and clause ② by as little as **1.19×**.
> **Clause ② is the binding constraint, and both admissions sit near its resolution floor** — an
> arm 20% weaker than `topw_k4` would be unresolvable there while still clearing clause ① five
> times over. That is a property of the definition worth knowing before anyone builds a core to
> satisfy it.

⚠ **And `gen`'s exclusion is reference-dependent in the honest direction**: unresolved at 0.47×
under the neutral pool, resolved at 1.36× under matched-k4. The table already says so — *"at the
two references that can resolve"* — and this is the arithmetic behind that phrase.

⛔ **THE FOUR CLAUSE-① ROWS SAY `not resolvably better`, NOT `worse` (R325).** All four sit BELOW
their own MDE, so **the sign is not readable** and this design cannot call any of them worse than
the baseline. `excluded` remains correct for an admission rule that requires a resolvable positive
— but a negative number printed beside the word `excluded` reads as a refutation, and there is
none. The clause-① column now carries each cell's MDE the way clause ② carries its interval.

⚠ **And `topwvar_k4` is a BH survivor at 0.84× its own MDE** — significant and unresolvable at
once. Multiplicity asks *is this distinguishable from zero across the family*; an MDE asks *could
this design have seen an effect this size*. Different questions, and this row answers them
differently, which is why both are shown.

> ### ✅ And the sham lands exactly where a sham should — ON the floor, not below it.
> `gen_sham` loses **resolvably** to all six real arms — `coval_core` 5.47×, `topw_k4` 5.41×,
> `generic` 4.98×, `gen` 3.39×, `full` 1.74×, `topwvar_k4` 1.27× — while being **indistinguishable
> from the random-from-rubric baseline** at 0.60× its own MDE. A sham that landed *below* the
> random baseline would be a treatment with the sign flipped; one that lands *on* it is the
> ingredient genuinely absent. Both halves are needed to read it, and both are now on the page.

> **~~Two arms admitted of nine.~~** ⛔ **RETRACTED (R327–R333).** The count is not supportable at
> any precision this site has. It was true under one reading of clause ② and false under another
> before a reference rule existed; and now that one does, **two admitted sets sit inside 0.25 of one
> MDE** and the design would need **12.9× more prompts** to choose between them. Against the *best
> held-out* prompt-blind quadruple out of all 1,820 (R286), the margins are **+0.0119**
> [+0.0048,+0.0187] and **+0.0096** [+0.0026,+0.0164] — both separable, both BH survivors, and
> **`topw_k4`'s is below its own MDE at that reference.** The numbers stand; the count does not.

⛔ **AND AT THAT REFERENCE `topw_k4` IS BELOW ITS OWN MDE (R326).** "Separable and a BH survivor" is
true and is not the same as resolvable: `coval_core` sits at **+0.0119 / 0.0101 = 1.18×** and
`topw_k4` at **+0.0096 / 0.0104 = 0.92×**. The clause-② baseline curve, five distinct legitimate
references ordered by strength:

| reference | ref A2 | `coval_core` | `topw_k4` |
|---|---:|---|---|
| budget 0 · random draw | 0.5397 | **2.69×** | — |
| neutral pool-16 | 0.5403 | 2.63× | 2.39× |
| budget 1 · hand-picked | 0.5504 | 1.51× | — |
| `generic` at matched k=4 | 0.5514 | 1.41× | 1.19× |
| **best held-out of 1,820** | 0.5546 | **1.18×** | **0.92× UNRESOLVED** |
| *in-sample argmax — disqualified* | 0.5575 | *0.87×* | — |

> ### `coval_core`'s admission holds at every legitimate reference. `topw_k4`'s does not — it is
> ### resolvable against four of the five and unresolvable against the strongest.

⚠ **The monotone decline itself is a DERIVATION, not a finding**: `gap = arm_A2 − ref_A2` with the
arm fixed, verified to four decimals at every point, so plotting the gap against reference strength
plots a quantity against what it is defined as a difference from. **What is measured is where the
ratio to each cell's own MDE crosses 1.0**, because those MDEs vary independently (0.0099–0.0108).

**⚠ `gen`'s row closed, and what closed it was asking how much SELECTION BUDGET a baseline may
have** (R287). The verdict looked like it depended on an arbitrary choice of prompt-blind reference.
It does not — the references form an ordered curve:

| baseline's selection budget | reference A2 | `gen` − reference | |
|---|---:|---:|---|
| **0** — a random quadruple | 0.5397 | −0.0045 [−0.0124,+0.0031] | unresolved · **fails BH** |
| **1** — the hand-picked incumbent | 0.5504 | **−0.0153** [−0.0238,−0.0072] | **LOSES** |
| **1820, held out** — best of all, clean split | 0.5546 | **−0.0194** [−0.0283,−0.0110] | **LOSES** |
| ~~1820, in-sample~~ | ~~0.5575~~ | ~~−0.0223~~ | **DISQUALIFIED — see below** |

**The sign is stable at every budget; only the resolution moves.** `gen` is worse than every
prompt-blind reference, separably at **2 of 3** defensible budgets, and the one cell that cannot
resolve it is the **weakest** reference — a random draw is simply too weak a baseline to test
anything against. `gen_sham` loses at every budget (negative control ✓).

> ⛔ **The positive control disqualified a reference, which is what it was for.** `coval_core` is
> admitted, so it must clear every legitimate baseline — and it does **not** clear the in-sample
> argmax (+0.0090 [+0.0014,+0.0160] against an MDE of 0.0104, unresolved). **An argmax over 1,820
> with no split is a selection artifact, not a baseline**, and the round was pre-registered to say
> so rather than to treat an admitted arm's failure as evidence against the arm. The remaining
> asymmetry is named and not used: **a searched baseline against an unsearched arm is mismatched**,
> and compute-matched selection for generated cores would need a population the release lacks.

**⚠ What admission does NOT mean.** `topw_k4` selects using **human importance metadata that is not
a property of the conversation** — no compiler working from the conversation alone has it. Whether
`coval_core`'s advantage is the *same* mechanism was tested (R284) and **could not be supported**:
0.6856 Pearson against a matched no-shared-mechanism floor of 0.5581, clearing on Pearson and not on
Spearman. So *"every route to a core runs through human annotation"* is **not claimed.**

### ⛔ THE PARTITION IS TARGET-DEPENDENT — the definition must name its statistic (R288)

Every number above is **A2 against a single drawn annotator**. That is one of six defensible
human-agreement targets this release supports. Swept:

| target | `coval` | `topw` | `generic` | `gen` | `full` | `sham` | ADMITTED |
|---|---:|---:|---:|---:|---:|---:|---|
| **A2 · annotator** | 0.5665 | 0.5642 | 0.5514 | 0.5352 | 0.5087 | 0.4828 | **coval, topw** |
| A2 · consensus | 0.6853 | 0.6823 | 0.6632 | 0.6367 | 0.5921 | 0.5608 | **coval, topw** |
| A1 · annotator | 0.0665 | 0.0660 | 0.0592 | 0.0610 | 0.0447 | 0.0382 | **none** |
| A1 · consensus | 0.1519 | 0.1539 | 0.1312 | 0.1343 | 0.0868 | 0.0919 | **none** |
| Kendall τ · mean | 0.4092 | 0.4040 | 0.3700 | 0.3161 | 0.2261 | 0.1583 | **coval only** |
| top-1 · mean | 0.5424 | 0.5548 | 0.5052 | 0.4876 | 0.4215 | 0.3740 | **topw only** |

**Four distinct admitted sets across six targets.** Positive control (`gen_sham` excluded
everywhere) ✓; negative control (an arm against itself, all targets) exactly 0 ✓; 73 of 108 cells
survive BH.

> **So the definition's text must name A2·annotator.** "Predicts held-out human judgement" is
> underdetermined — the release supports six readings of it and they partition differently.

⚠ **But what moves is RESOLUTION, not mostly direction — and I had to compute that rather than
assume it.** Pairwise ordering agreement across the six targets: **Kendall τ min 0.556, median
0.778, max 1.000.** Against A2·annotator, four of five other targets sit at **τ = +0.944** and move
only the two worst arms. **A1·consensus is the outlier at τ = +0.556**, and it is where the
partition breaks hardest: nothing is admissible because A1's base rate is ~6% and every margin sits
inside its own resolution.

⚠ **The single most uncomfortable cell, stated because it is the one I would rather not have found:
on A1·consensus, `full` (0.0868) scores BELOW `gen_sham` (0.0919)** — the entire rubric below
criteria written for a *different conversation*. One target of six, and the only one where any arm
crosses the sham. It is not evidence that `full` is worse than a sham; it is evidence that
**A1·consensus cannot tell them apart**, which is the same thing as saying it cannot carry this
definition.

### The scope every number above carries

| | |
|---|---|
| population | 968 CoVal prompts with ≥2 annotators · 15,593 annotations, median 16/prompt |
| instrument | **Qwen3.5-2B-Base** — LOAD-BEARING (R290): at Qwen3.5-0.8B-Base the admitted set is **empty**. Cross-artifact noise 0.0009 at the mean. |
| baseline | named per clause above — never "chance" |
| regime | k=4 unless stated; A2 = pairwise accuracy over 6 pairs; cluster bootstrap over prompts |
| resolution | per-cell MDE **0.0084–0.0178**; the admissible band is **12.57 MDE units** wide |
| what is structurally unresolvable | `full` vs `topwvar_k4` (+0.0048): needs **3,352 prompts, 3.5× this release** |

### ⛔ THE PARTITION IS JUDGE-DEPENDENT — and it localises to clause ② (R290)

Five arms re-judged by **Qwen3.5-0.8B-Base**, a model 2.5× smaller. Both judges clear their controls:
each beats its own measured chance floor, each recovers the benchmark's largest known gap
(`generic − random`: **+0.0587** at 2B, **+0.0692** at 0.8B), and an arm against itself returns
exactly 0 under both. **This is not a blind second judge.**

| judge | arm | A2 | ① vs random-from-rubric | ② vs prompt-blind | |
|---|---|---:|---:|---:|---|
| **2B** | `coval_core` | 0.5665 | **+0.0738** | **+0.0151** | **ADMITTED** |
| **2B** | `topw_k4` | 0.5642 | **+0.0715** | **+0.0128** | **ADMITTED** |
| **2B** | `gen` | 0.5352 | +0.0425 | −0.0162 | excluded |
| **0.8B** | `coval_core` | 0.4695 | **+0.0620** | **−0.0072** | **excluded** |
| **0.8B** | `topw_k4` | 0.4659 | **+0.0583** | **−0.0109** | **excluded** |
| **0.8B** | `gen` | 0.4736 | **+0.0660** | −0.0031 | excluded |

> ⛔ **Admitted set: `{coval_core, topw_k4}` at 2B, `{}` at 0.8B.** The definition's scope line must
> name **Qwen3.5-2B-Base**, exactly as R288/R289 forced it to name its statistic.

**And the dependence localises precisely.** **Clause ① is judge-ROBUST** — all **six** cells are
resolvably positive, and at 0.8B `gen` has the *largest* margin of any (+0.0660 [+0.0563,+0.0747]).
**Clause ② is judge-BOUND** — 2 of 3 resolvably positive at 2B, **0 of 3** at 0.8B.

⚠ **But the 0.8B failures are not all reversals, and my first reading of them was too strong.**
Printing the intervals:

| 0.8B, clause ② | gap | 95% CI | |
|---|---:|---|---|
| `topw_k4` | −0.0109 | [−0.0201, −0.0020] | ⚠ **the two criteria DISAGREE**: CI excludes zero, but \|eff\| = 0.0109 is below its own MDE of 0.0110 — **below resolution** by this arc's own rule |
| `coval_core` | −0.0072 | [−0.0157, **+0.0003**] | **UNRESOLVED** — spans zero |
| `gen` | −0.0031 | [−0.0112, **+0.0040**] | **UNRESOLVED** — spans zero |

**So "the prompt-blind arm beats every prompt-specific one at 0.8B" is true of NO arm under this
arc's own resolution rule, and of one arm under a CI-only rule.** The admitted set is empty either
way — admission needs clause ② *resolvably positive* and none of the three is. **The mechanism is
not an inversion at all; it is three failures to resolve**, and the disagreement between the two
criteria on `topw_k4` is published rather than settled by picking one.

> **A weaker judge can still tell good criteria from random ones. It cannot make prompt-specific
> criteria pay off over generic ones.** *Aboutness is the part that needs a capable instrument to
> be visible at all* — which is a claim about the instrument, not about cores, and is exactly the
> distinction clause ② was built to draw.

⚠ **Under 0.8B the ordering inverts**: `gen` scores highest (0.4736) of the three, where at 2B it is
lowest. Per-prompt score correlation between judges: **0.404–0.593** — moderate, not strong. 10 of
12 cells survive BH.

### ⚠ WHAT `SWEPT` MEANS ON EACH AXIS — counted, because the summary overstated two of them

Four axes carry every claim in this file. Saying they are "all swept except the release" is true of
the **axes** and false of the **grid**:

| axis | swept | **at what width** |
|---|---|---|
| **arm** | 41 judged arms (R294) | **full — 41 of 41** |
| **statistic** | 6 agreement targets (R288) | **10 arms of 41** |
| **judge** | 2 models (R290 · **R301**) | ~~3 arms of 41~~ → **41 of 41** |
| **release** | 1 | **not swept — genuinely impossible** |

> **Only the arm axis was swept at full width.** The statistic and judge results are real and
> resolved, and they are established on **a quarter and a fourteenth of the arm space** respectively.
> A claim that the partition survives a change of judge is a claim about **`coval_core`, `topw_k4`
> and `gen`**, not about the eight admitted arms or the thirty-six excluded ones.

> ⛔ **THE JUDGE ROW UNDERSTATED ITS OWN EVIDENCE BY 13.7×, and the correction was on disk the
> whole time.** `R301` re-judged **all 41 arms** at 0.8B — not 3 — and returned the **same empty
> admitted set**. So the paragraph above is out of date in the *strengthening* direction: the
> judge-dependence is established at **full arm width**, and `{}` at 0.8B is not an extrapolation
> from three arms. **R301 was cited nowhere in this file or the top-level README** until now, which
> is how a page comes to understate itself: nothing checks that a *committed* round reached the
> synthesis, only that it reached *a* README.
>
> **What R301 could NOT settle, and R356 sharpens.** Its pre-registered kill needed
> `R2 = min(pooled, worst leave-one-family-out) ≥ 0.50`; pooled was 0.6124/0.5447 and the worst LOFO
> **0.4817**, so it printed `UNRESOLVED` between SHRINK (β ≈ 0.40–0.43, ordering intact) and REORDER.
> `R356` prices the within-family correlations R301 printed but never used, each against the null its
> **own arm separation** implies:
>
> | family | n | ρ (2B vs 0.8B) | separation | its own null | reading |
> |---|---:|---:|---:|---:|---|
> | `random_k` | 17 | **−0.512 / −0.429** | 2.2 se | **0.00 percentile** | **real inversion**, survives Bonferroni |
> | `topw_k` | 8 | +0.810 / +0.667 | 5.7 se | 20th / 10th pctile | **forced** — carries no information |
>
> **So `REORDER` survives with an address.** The judges resolvably invert one family; the family that
> looked like agreement was separated enough that agreement was nearly certain. **No family agrees
> MORE than forced**, so the shared-judge-error confound — which would inflate every between-judge
> number here — is not observed.
>
> ⚠ **R357 gauge-tested that reading and it PARTITIONS.** Swapping which judge is called *truth* —
> a transformation the property *do these judges disagree* is invariant under — leaves `random_k`
> flagged at the **0.00 percentile both ways** (**the inversion survives**) but moves `topw_k` from
> 20.16% to **1.43%**. So *"`topw_k` is forced and carries no information"* is **withdrawn**; what
> survives is *"it agrees LESS than its separation forces"*, since it sits in the low tail in both
> directions. Mechanism: `β(2B→0.8B) = 0.4340` vs `β(0.8B→2B) = 1.4112` — an **expansion, not the
> reciprocal 2.30**. Regression to the mean, and taking the noisier judge as truth inflates the
> apparent separation.

**This is the third time today a closing summary quantified without counting**, and the first time
the rule carved into `realstat §4` caught it before it was published rather than after.

### The impossibility register, AUDITED (R290, R291) — three lines were wrong

Every round in this arc carried a register of what the site "cannot meet". **Its lines had never
been checked**, which makes it the most expensive unchecked wall in the campaign — a register's only
job is to be the honest list.

| line | status after audit |
|---|---|
| `cross-model` | ⛔ **FALSE.** The judge is my instrument, not the site. Qwen3.5-0.8B-Base was on disk the whole time; five arms are re-judged and R290 decides whether the partition moves. |
| `position randomized` | ⛔ **FALSE — the field exists** (`responses[].response_index`), and testing it found a **resolved slot effect in the HUMAN target** (spread 0.1181 vs null 0.0453, p = 0.0010) that **no judge shares** (p = 0.075–0.305, none survives BH). Slot is therefore an unreachable component of the target that **caps** achievable A2 rather than inflating it. |
| `temporally resolved` | ✅ **CONFIRMED — now measured.** No time, date or stamp field anywhere in the schema. Same verdict as before, but it is now a fact rather than an assumption, and those are different objects. |
| `independently replicated` | ⚠ **NOT impossible — NOT ATTEMPTED.** `realstat §2.5` makes it reachable by triple-blind agents, and this session runs under a standing instruction not to dispatch them. **That is a budget, not a wall**, and calling it impossible would be an unavailability claim in the flattering direction — exactly what the register forbids. |
| `construct / criterion validated` | ✅ **genuinely impossible.** Needs an external gold standard; whether human pairwise agreement is the right goal is untouched by anything here. |
| `cross-RELEASE` | ✅ **genuinely impossible.** One release. Nothing in this file bounds what the definition admits on a second one. |
| `cross-architecture` | ⚠ **NOT impossible — NOT DOWNLOADED.** The HF cache holds **8 cross-architecture causal-LM configs** (`SmolLM2-1.7B` Llama, `OLMo-2-1B`, `phi-2`, `Mistral-7B`, `internlm2-1.8b`, `falcon-rw-1b`, `starcoder2-3b`, `Qwen3-1.7B`) — and **every one carries 0.00 GB of weights.** Config-only. Obtaining one is a **download**, not a query. |

> ⚠ **`config.json` present, weights absent — and that nearly wrote a fourth false line.** My first
> enumeration read architectures out of `config.json` and would have reported *"8 cross-architecture
> judges available"*. Following the symlinks into `blobs/` gives **zero weight-sized files for all
> eight.** **A config is not a model**, exactly as a heading is not an entry and a spec is not an
> implementation — the same instrument error this file has now recorded three times in three
> different vocabularies.

> **Three of six were wrong, and all three were wrong in the direction that excused work.** The
> register's failure mode is not lying about the data — it is inheriting a line from a template and
> never asking it a question.

---


*Every claim carries its round and its status. Nothing here is asserted without one.*

**Status vocabulary.** `DERIVED` — forced by the algebra, labelled as such, evidence of nothing on
its own. `MEASURED` — with population, instrument, baseline, regime. `UNVERIFIED` — the measurement
ran and its controls did not behave; never an acquittal. `OPEN` — running now.

---

## The definition — COMPLETE EVIDENCE TABLE, 2026-08-03

> ⛔ **THE TABLE BELOW WAS COMPUTED ON 3 ANNOTATORS PER PROMPT. THE RELEASE SHIPS A MEDIAN OF 16.**
> R306 recomputed every arm and all 45 pairs on **all 15,593 annotations**, with each cell against
> **its own** MDE rather than a global bracket. **Seven resolvability verdicts flipped, all toward
> RESOLVED.** The A2 column moves by ≤0.005 and no ADMIT/EXCLUDE call changes, so the partition
> stands — but the *resolvability* annotations below are superseded by this block:
>
> | pair | 3-draw | **all-annotator** | own MDE | |
> |---|---:|---:|---:|---|
> | `topw_k4` − `generic` | +0.0078 | **+0.0128** [+0.0050,+0.0203] | 0.0108 | **RESOLVED** (was below) |
> | `coval_core` − `generic` | +0.0110 | **+0.0151** [+0.0076,+0.0226] | 0.0107 | **RESOLVED** (was marginal) |
> | `generic` − `full` (the price) | +0.0447 | **+0.0426** [+0.0345,+0.0515] | 0.0121 | RESOLVED |
> | `coval_core` − `topw_k4` | +0.0032 | **+0.0023** [−0.0038,+0.0085] | 0.0085 | **BELOW RESOLUTION** — the two best arms are tied |
> | **`full` − `topwvar_k4`** | +0.0089 | **+0.0048** [−0.0016,+0.0114] | 0.0094 | **BELOW RESOLUTION** — the only straddling cell left |
>
> **Totals: RESOLVED 36/45 · BELOW RESOLUTION 9/45 · BH survivors 37/45.** Per-cell MDE spans
> **0.0084–0.0178**, a 2.1× range — *a global bracket over-resolves the quiet pairs and
> under-resolves the loud ones, which is how six cells were mislabelled MARGINAL.*
>
> ⚠ **The value of aboutness is a VALUE again: +0.0128, above its own resolution.** The bound
> `< 0.019` recorded one round earlier was an artifact of the 3-draw design, not a property of the
> release. Controls: an arm against itself returns exactly 0 with a CI of exactly [0,0]; two draws
> of the same random rule differ by −0.0055 against their own MDE of 0.0140.
>
> ⚠ **Movement went BOTH ways** — 4 cells shrank >25% (`full−topwvar` 0.54×, `topabs−topvar` 0.53×)
> and several grew (`topw−generic` 1.64×). The 3-draw estimator is unbiased; it was noisy, and the
> movement is concentrated in the small effects exactly as sampling noise predicts. **No systematic
> inflation is claimed and none was found.**


> **A core is a set of criteria that predicts held-out human judgement better than chance, and
> better than the same criteria applied to a different prompt.**

### ⛔ CLAUSE 2 IS BEING REPLACED — the sentence above encodes the POISON comparison

*"the same criteria applied to a different prompt"* is the ingredient **misdirected**, not
**absent** (`realstat §4`). It bounds `benefit + harm` and cannot isolate benefit. The replacement:

> **A core is a set of criteria that predicts held-out human judgement better than chance, and
> better than the same NUMBER of criteria that never read the conversation.**

⛔ **AND CLAUSE 1 DOES NOT SAY WHAT IT DOES** (R285). *"better than chance"* is operationalised
throughout as *better than `random_k4`* — and `random_k4` is **not chance.** Measured by drawing the
comparison partner from a **different prompt**, 5 seeds:

| comparison type | measured chance | |
|---|---:|---|
| human vs human | **0.3833** (sd 0.0077) | |
| arm `random_k4` vs human | **0.4257** (sd 0.0031) | and `random_k4` *scores* 0.4927 |
| arm `generic` vs human | 0.4300 (sd 0.0050) | |
| arm `coval_core` vs human | 0.4314 (sd 0.0060) | |

> **`random_k4` sits 4.99 MDE units ABOVE its own chance level.** So the clause's *words* say
> "above chance", which **excludes nothing in this benchmark**, while the clause's *test* says
> "above four criteria drawn from the right rubric", which excludes four arms. The words and the
> test are different requirements and the words are what a reader acts on.

⚠ **`A2 = 0.5` was never chance either.** A2 counts matches on a **three-valued** sign vector
(−1, 0, +1), so random agreement is `Σpᵢ²` over the sign marginal — not ½. The pre-registered
control said "the cross-prompt floor must land near 0.5", it returned **0.3869**, and **the control
was right and the pre-registration wrong.** Using 0.5 would have made the admissible band
**0.0519 instead of 0.1686 — 0.31× the real width.**

**The band, correctly floored:** chance(human–human) **0.3833** → human ceiling **0.5519** =
**0.1686 wide = 12.57 MDE units** (R306 median MDE 0.0134). Two other ceilings exist and are the
wrong ones for these arms: human-vs-consensus **0.6352** and per-prompt oracle **0.6862**, both
higher because they are denoised targets our arms are never scored against.

| arm | A2 | its own chance | MDE units above it |
|---|---:|---:|---:|
| `coval_core` | 0.5665 | 0.4314 | **10.07** |
| `topw_k4` | 0.5642 | 0.4311 | 9.92 |
| `generic` | 0.5514 | 0.4300 | 9.05 |
| `random_k4` | 0.4927 | 0.4257 | **4.99** |
| HUMAN | 0.5519 | 0.3833 | 12.57 |

Positive control: an annotator against themselves returns A2 = 1.000000000000 exactly.

**The exclusion test — *name an admissible object this clause excludes* — is the only thing that
makes a clause load-bearing:**

| clause | what it excludes | status |
|---|---|---|
| 1 · > chance | `topvar_k4` (−0.0123, below chance), `gen_sham`, `topabs_k4`, `random_k4` | MEASURED |
| **2 · > k prompt-blind criteria** | **`gen` (−0.0162 [−0.0247,−0.0080], resolved at k=4)** and `topwvar_k4` (−0.0474) — **both of which clause 1 ADMITS** | **MEASURED** |

> ⚠ **A strict upgrade in evidentiary status, not just wording.** The OLD clause 2's
> load-bearingness rested on a **DERIVATION**: `generic`'s criteria are identical across prompts,
> so its own sham *is* itself and Δ=0 is forced by algebra. The NEW clause 2 excludes **`gen` — an
> arm the old table ADMITTED — by a resolved measurement at exactly matched size.** A clause proved
> necessary by an identity has been replaced by one proved necessary by a falsifiable comparison
> that came out against its author.

### ⛔ `full` FAILS THE NEUTRAL CLAUSE AT ITS OWN SIZE — the rubric is not worth its length (R307)

A pool of **16 generic criteria judged once** (61,952 calls) makes every k free. The neutral
dose-response curve, 20 random subsets per k, all annotators:

| k | 1 | 2 | 4 | 8 | 12 | **15** | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|
| A2 | 0.5218 | 0.5366 | 0.5403 | 0.5390 | 0.5412 | **0.5418** | 0.5422 |

> **The curve saturates by k≈4.** `+0.0186` from k=1→4, then **`+0.0019` from k=4→16 against an
> MDE of 0.0121 — below resolution.** Criterion **count** buys nothing past four.

| arm | k | A2 | neutral@k | gap | | |
|---|---:|---:|---:|---:|---|---|
| `coval_core` | 4 | 0.5665 | 0.5403 | **+0.0262** [+0.0192,+0.0332] | **PASSES** | BH ✓ |
| `topw_k4` | 4 | 0.5642 | 0.5403 | **+0.0239** [+0.0169,+0.0312] | **PASSES** | BH ✓ |
| `gen` | 4 | 0.5352 | 0.5403 | −0.0051 [−0.0129,+0.0024] | **UNRESOLVED** | — |
| **`full`** | **15** | 0.5087 | **0.5418** | **−0.0331** [−0.0413,−0.0254] | **FAILS** | BH ✓ |

> ⛔ **The entire rubric — 15 criteria written for that conversation — is separably WORSE than 15
> criteria that never read it.** The size confound is closed in the direction that costs `full` its
> admission, not in the one that rescues the price.

⚠ **THE NEUTRAL BASELINE IS ITSELF A CHOICE, and `gen`'s verdict turns on it.** The incumbent
`generic` (four hand-picked sentences) scores **0.5514**; a *random* four from the 16-pool average
**0.5403 ± 0.0070**. So `gen` FAILS against the first (−0.0162, resolved) and is UNRESOLVED against
the second (−0.0051). **Both are defensible neutral arms and they disagree** — that spread is the
finding, and no single "the neutral arm" number should be quoted without it.

⚠ **The identity control FAILED and the round reported anyway — here is exactly why that is not
loosening it.** `pool[0:4]` should reproduce `generic` bit-for-bit and does not (mean A2 0.5504 vs
0.5514). Diagnosed on the 15,488 raw satisfaction cells: **66% exact zeros, mean |Δ| 0.0086, mean
SIGNED Δ −0.0006.** Zero systematic component ⇒ **instrument noise, not a text or index mismatch**
(a mismatch shows a low zero-rate *and* a large signed mean). But it is **4× R260's independently
measured batch-noise envelope**, so **R260's number was scoped to the batch change *it* tested and
I had been carrying it as "the" batch noise.** Consequence, stated as a scope rule rather than a
pass: **pool-internal comparisons across k share one run and are exact; pool-vs-published
comparisons carry 0.0009 at the mean**, below the 0.0134 MDE.

**Under the revision: 2 admitted of the 9 arms it can judge** — `coval_core` and `topw_k4`. `full`
is **PENDING**: the only arm whose size is unmatched (median 15 vs 4), neutral arm on the GPU (R307).

### ✅ CLAUSE 2 SURVIVES ITS OWN META-SEPARATOR — 1,820 subsets enumerated exactly (R286)

The clause says *better than the same NUMBER of criteria that never read the conversation.* If its
threshold moves with **how good my generic criteria happen to be**, it measures my baseline, not
cores. All `C(16,4) = 1820` prompt-blind quadruples, enumerated **exhaustively** and pool-internal:

| min | p25 | median | p75 | p90 | p99 | **max (in-sample)** |
|---:|---:|---:|---:|---:|---:|---:|
| 0.5144 | 0.5329 | 0.5391 | 0.5446 | 0.5490 | 0.5546 | **0.5575** |

**Even the in-sample argmax — a selection artifact, quoted only to be dismissed — falls short of
`coval_core`'s 0.5665.** Held out properly (chosen on half the prompts, scored on the other half,
10 splits):

| selection rule | in-sample | held-out | shrinkage |
|---|---:|---:|---:|
| best | 0.5584 | **0.5549** | +0.0036 |
| 2nd best | 0.5576 | 0.5554 | +0.0022 |
| 90th pct | 0.5487 | 0.5506 | −0.0019 |

| arm | vs best held-out blind | |
|---|---:|---|
| `coval_core` | **+0.0119** [+0.0048, +0.0187] | separable, BH ✓ |
| `topw_k4` | +0.0096 [+0.0026, +0.0164] | ⚠ **BELOW RESOLUTION** — its own MDE is **0.0104**. CI excludes zero, \|eff\| does not clear the MDE. **Downgraded by R292.** |

> ⚠ **W-BASELINE, PARTIAL — and the kill fired once its own rule was applied.** `coval_core` stays
> separably ahead of the best held-out blind quadruple (+0.0119 vs MDE 0.0101). **`topw_k4` does
> not** (+0.0096 vs MDE 0.0104). So *"no prompt-blind quadruple reaches the admitted arms"* is
> established for **one** of the two — for `topw_k4` the blind arm is **not shown to be behind,
> only not shown ahead.** Bounded to this 16-criterion pool either way.

⚠ **R286's KILL originally read `lo > 0` — the CI criterion — while its own table read
`|eff| ≥ MDE`.** A kill running a different rule than the table above it is the verdict-string
failure moved into the branch, **which is worse: the table is read by a person and the branch is
not.** Both now use the same computed verdict, and the kill's answer changed from `False` to `True`.

⚠ **The incumbent `generic` sits at the 93.7th percentile of 1,820.** Four criteria written by hand
in one line, with no fitting, land in the top 7% of every quadruple the pool can form — which is
why it was such a punishing baseline, and a reminder that *hand-picked* is not *weak*.

⚠ **The first bootstrap here was wrong and the correction widened it 2×.** It concatenated 10
eval-halves into 4,840 rows — but those are **968 prompts appearing ~5 times each**, so `n_eff` is
the cluster count, not the row count (P14). Corrected to average each prompt over the splits where
it was held out and bootstrap the 968: `coval_core`'s CI went **[+0.0070,+0.0136] → [+0.0048,+0.0187]**.
Verdict unchanged, interval not.

⚠ **What the revision does NOT license.** Both survivors depend on a *selector*, and `topw_k4`'s
reads **human importance metadata that is not a property of the conversation**. The tempting
conclusion — every route to a core runs through human annotation — **was tested in R284 and not
supported**: the survivors' per-prompt advantages correlate at 0.6856 (Pearson) against a matched
no-shared-mechanism floor of 0.5581, clearing it on Pearson and **not on Spearman**. The
specifications disagree, so the sentence is not written.

⚠ **AND THIS DEFINITION IS STATED TWICE IN THIS FILE** (here and again below, in the clause-audit
section). That is the "one home per fact" violation P16 exists to prevent, and it is how the two
copies drift. The second occurrence is **superseded by this block** and is left in place under L81
(annotate, never rewrite) because its clause-audit table is the record of how the earlier clauses
died.


**Both clauses have now been tested against every object this benchmark builds.** Nine arms, each
admitted or excluded by measurement, none by assertion.

| arm | A2 | clause 1: > chance | clause 2: > its own sham | |
|---|---:|---|---|---|
| `topw_k4` | 0.5667 | **+0.0692** [+0.0570,+0.0814] | **+0.0736** [+0.0648,+0.0820] | **ADMITTED** |
| `coval_core` | 0.5671 | separable | **+0.0694** [+0.0609,+0.0777] | **ADMITTED** |
| `gen` | 0.5350 | **+0.0390** [+0.0304,+0.0478] | **+0.0522** [+0.0428,+0.0625] | **ADMITTED** |
| `full` | 0.5134 | **+0.0131** [+0.0061,+0.0202] | **+0.0465** [+0.0379,+0.0553] | ⚠ **ADMITTED — UNRESOLVED** |
| `topwvar_k4` | 0.5059 | +0.0092 [−0.0003,+0.0153] — **includes 0** | — | ⚠ **excluded — UNRESOLVED** |
| `random_k4` | 0.4943 | 0 by construction | — | **excluded** |
| `topabs_k4` | 0.4941 | −0.0003 [−0.0146,+0.0177] | — | **excluded** |
| `topvar_k4` | 0.4884 | **−0.0123** [−0.0203,−0.0040] — *below* chance | — | **excluded** |
| `gen_sham` | 0.4828 | below random | — | **excluded** |

### ⛔ THE TABLE'S OWN BOUNDARY IS NOT RESOLVABLE, AND ONE ADMITTED ROW RESTS ON NOTHING

R304, all 45 pairs among the ten arms, cluster bootstrap over 968 prompts, one shared index matrix
so cells are paired, BH over the whole grid, against R303's MDE bracket **[0.0100, 0.0200]**:

| | | |
|---|---:|---:|
| **RESOLVED** (\|effect\| ≥ 0.0200) | 29 / 45 | 64.4% |
| **MARGINAL** (0.0100 ≤ \|effect\| < 0.0200) | 6 / 45 | 13.3% |
| **BELOW RESOLUTION** (< 0.0100) | 10 / 45 | 22.2% |
| BH survivors | 35 / 45 | |

**Five of the 24 cells that straddle the definition are not RESOLVED**, and three of them are
`full`'s:

| straddling pair | effect | verdict |
|---|---:|---|
| `topw_k4` (A) − `generic` (e) | +0.0078 | **BELOW RESOLUTION** |
| **`full` (A) − `topwvar_k4` (e)** | **+0.0089** | **BELOW RESOLUTION** |
| `coval_core` (A) − `generic` (e) | +0.0110 | MARGINAL |
| **`full` (A) − `random_k4_s0` (e)** | **+0.0182** | MARGINAL |
| **`full` (A) − `topabs_k4` (e)** | **+0.0195** | MARGINAL |

> ⛔ **`full` is resolvably better ONLY than the two arms that score below chance** (`topvar_k4`,
> `gen_sham`). Against every excluded arm that is not itself sub-chance, its margin is inside the
> design's resolution. **The whole rubric is admitted on evidence this design cannot resolve.**

⛔ **And the negative control is the sharpest number in the round.** Two independent random draws of
the *same* rule, `random_k4_s0` vs `random_k4_s1`, differ by **−0.0081** [−0.0196, +0.0040]:

> **The gap that admits `full` and excludes `topwvar_k4` (+0.0089) is the same size as the gap
> between two random draws of one rule (0.0081).** Nothing separates them but which seed was run.

### ⛔ THE BOUNDARY IS STRUCTURALLY UNRESOLVABLE, AND I HAD BEEN DISCARDING RESOLUTION FOR FREE

R305 — variance decomposition of the paired per-prompt difference, using **every annotator**, not a
draw. Positive control (does the decomposition reproduce the observed 1-draw sd?) **0.7% error**;
negative control (an arm against itself) **σ²_b = σ²_w = 0 exactly**.

**The release carries a median of 16 annotators per prompt — 15,593 annotations. Every number on
this page used 3.**

| `full − topwvar_k4` | |
|---|---:|
| effect at 3 draws (R304) | +0.0089 |
| **effect using ALL annotators** | **+0.0048** |
| σ_between (prompt heterogeneity, irreducible) | 0.0986 |
| σ_within (annotator noise, removable) | 0.1289 — **63% of the variance** |
| MDE at k = 1 / 3 / 10 / all-on-disk / ∞ | 0.0146 / 0.0111 / 0.0096 / **0.0094** / **0.0089** |

> **Two separate findings, and they point opposite ways.**
> ① **The wall is real.** Even with *infinite* annotators per prompt the design floors at **0.0089**,
> above the all-annotator effect of 0.0048. **No annotator budget resolves this edge.** Reaching it
> would need **3,352 prompts — 3.5× this release.** That is a specification for a next site, not a
> shrug.
> ② **But 63% of the variance was removable and I was not removing it.** Going from 3 draws to
> every annotator on disk moves the MDE 0.0111 → 0.0094, **~15% of resolution available at zero
> cost**, and it changes effect estimates: the boundary effect nearly halves.

The contrast cell behaves as it should: `coval_core − topvar_k4` = +0.0802 clears its MDE at
**k = 1**. The placebo — two draws of the same random rule — comes to **−0.0055**, still the same
magnitude as the boundary effect it is being compared against.

**What this does NOT do.** It does not overturn `coval_core`, `topw_k4` or `gen`, whose separations
from every excluded arm are RESOLVED at 0.031–0.083. The definition's partition is a measurement
over most of its range and a coin flip at exactly one edge — and that edge had been written down in
the same bold type as the rest.

### ⚠ Both clauses are load-bearing — the object that proves it

Nothing above passes one clause and fails the other, which by the exclusion test left **clause 2
untested as an independent requirement.** The object that separates them:

**Four generic quality criteria, identical on every prompt** — *accurate · clear · helpful ·
avoids harm.*

| | | |
|---|---|---|
| **clause 1** | `generic − random` = **+0.0611** [+0.0515, +0.0702] | **PASSES** |
| **clause 2** | `generic − its sham` = **0.0000 exactly** | **FAILS** |

`generic` scores **0.5554** against `topw_k4`'s 0.5667 — **within 0.011 of the best arm in the
benchmark**, on criteria that never look at the prompt. Clause 1 alone would admit it.

⚠ **The clause-2 side is a DERIVATION, not a measurement.** The criteria are identical across
prompts, so prompt *i*'s sham *is* prompt *i*'s core and Δ=0 is forced by the algebra. It shows
clause 2 **can** reject what clause 1 admits — which is what "does this clause do work" asks —
and it must never be quoted as a measured rejection.

### ⛔ THE DEFINITION IS NOT MONOTONE IN FIDELITY, AND THE COST IS SEPARABLE

The exclusion test asks whether a clause rejects an admissible object. It does not ask **how good
the rejected object is.** Asked directly, over the same 968 prompts, 3 seeds, paired bootstrap:

| | A2 | |
|---|---:|---|
| `generic` | **0.5554** | **EXCLUDED** by clause 2 |
| `full` | **0.5134** | **ADMITTED** |

> **`generic − full` = `+0.0420` [+0.0334, +0.0502] — separable.**

**The definition rejects a separably better predictor than one it admits.** That is not an error in
either verdict; it is the price of the second clause, and it now has a number. **What clause 2 buys
is aboutness; what it costs is up to 0.042 of A2** — four times the +0.011 that being about the
prompt is worth at the top of the table.

⛔ **AND THE PRICE IS MEASURED ACROSS TWO AXES AT ONCE — `generic` has k=4, `full` has a MEDIAN
OF 15** (min 4, max 39). So `generic − full = +0.0426` confounds **prompt-specificity** with
**criterion count**, and no reading of that one number separates them. The size-matched neutral arm
did not exist when the price was first quoted; R307 builds it (a 16-criterion generic pool judged
once, so every k is free) and the price is **provisional until that lands**.

⚠ **AND CLAUSE 2 ENCODES THE WRONG CONTROL IN ITS OWN TEXT.** It reads *"better than the same
criteria applied to a different prompt"* — the **poison** comparison this campaign established
bounds `benefit + harm`. The neutral form is *better than prompt-neutral criteria of the same
size*, and under it the extension changes: at the all-annotator numbers `gen` (0.5352) and `full`
(0.5087) both sit **below** `generic` (0.5514), so a neutral clause 2 would exclude two arms this
table admits. **Whether that reading survives depends entirely on the size match**, which is what
R307 is for.

### ⛔ AT EXACTLY MATCHED SIZE, READING THE PROMPT BUYS NOTHING ON ITS OWN — 2 OF 7 (R308)

Seven arms are **k=4 by construction** and drawn from the same `coval_full` rubric, differing only
in **selection rule**; `generic` is also k=4. So the neutral clause is answerable at exactly
matched size with no size adjustment made or needed. All annotators. **All 8 cells survive BH;
every verdict is resolved against its own MDE.**

| arm | A2 | − `generic` | 95% CI | | what selects it |
|---|---:|---:|---|---|---|
| `coval_core` | 0.5665 | **+0.0151** | [+0.0076,+0.0226] | **BEATS** | the release's own compiler |
| `topw_k4` | 0.5642 | **+0.0128** | [+0.0050,+0.0203] | **BEATS** | the rubric's top 4 by **human importance metadata** |
| **`generic`** | **0.5514** | — | | | **never reads the conversation** |
| **`gen`** | 0.5352 | **−0.0162** | [−0.0247,−0.0080] | **LOSES** | generated from the conversation alone |
| `topwvar_k4` | 0.5040 | −0.0474 | [−0.0573,−0.0377] | LOSES | importance × spread |
| `random_k4` | 0.4927 | −0.0587 | [−0.0691,−0.0484] | LOSES | 4 at random from the same rubric |
| `topabs_k4` | 0.4894 | −0.0620 | [−0.0735,−0.0507] | LOSES | top 4 by \|importance\| |
| `topvar_k4` | 0.4863 | −0.0651 | [−0.0755,−0.0549] | LOSES | top 4 by satisfaction spread |

> ⛔ **Clause 2 is not tracking ABOUTNESS. It is tracking aboutness CONDITIONAL ON A SELECTOR** —
> and the only two selectors that clear the prompt-blind arm are the release's own compiler and one
> that reads **human importance metadata a compiler working from the conversation alone would not
> have.** Five of seven ways of reading the prompt lose to four generic sentences by a resolved
> margin.

⚠ **And `gen` — an arm this table ADMITS — loses at −0.0162, resolved.** A core generated from the
conversation alone, with no metadata, is separably **worse** than four sentences that never read it.
Controls: `generic` against itself exactly 0 with CI [0,0]; the same random rule at two seeds
differs by −0.0055 inside its own MDE of 0.0140 (three seeds: 0.4927 / 0.4981 / 0.4884).

**The obvious escape does not open** (R276). *Perhaps `generic` only looks good because A2 rewards
the common verdict* — i.e. it is a constant in disguise, and clause 2 discards nothing. Tested
against the **best of all 75 weak orderings, chosen with hindsight**, which is the strongest
prompt-blind constant that exists:

| | margin over best constant | emitted-class entropy |
|---|---:|---:|
| `coval_core` | +0.1187 [+0.1064,+0.1310] | 4.555 bits (0.772 of human) |
| `topw_k4` | +0.1155 [+0.1037,+0.1273] | 4.584 (0.777) |
| **`generic`** | **+0.1077** [+0.0952,+0.1198] | **4.579 (0.777)** |
| `full` | +0.0630 [+0.0507,+0.0749] | 4.561 (0.773) |

**`generic` is not degenerate by any measure available here** — its verdict entropy is
*indistinguishable from the best arm's* (4.579 vs 4.584), it departs from its own modal class on
94.4% of prompts, and it clears the hardest constant baseline by +0.108. Positive control (a
constant arm reproducing its own baseline) exact to 0.00e+00; placebo 0.0000; best/modal/mean-of-75
baselines agree in sign on all six arms.

⚠ **And the reason it is not degenerate is worth stating, because the label misleads**: `generic`
is **criteria-blind to the prompt, not response-blind.** The judge still scores those four fixed
criteria against *that prompt's four responses*. Prompt-blindness in the strong sense is the
constant baseline, and everything here beats it — including `random_k4` at +0.0448, **which is why
this statistic answers "is `generic` degenerate" and cannot rank arms.** All six clear BH.

⚠ **This is a CHOICE, and it must be read as one.** A definition of "core" keyed on fidelity alone
would admit `generic` and rank it fourth of eleven. This one does not, because a set of criteria
that never reads the conversation cannot be *a core of that conversation* whatever it scores — the
same reason a stopped clock is not a chronometer. **But nothing measured here forces that
preference.** It is a commitment about what the word is for, priced at −0.042, and the price is
stated so that anyone who disagrees can pay it back.

**4 admitted, 6 excluded.** Every sham lands at or below random — **0.4931 · 0.4976 · 0.4828 ·
0.4669** against 0.4943 — and `full`'s is the lowest: **fifteen criteria about the wrong
conversation are worse than four drawn at random from the right one.**

⚠ **AND THAT PATTERN IS A DIAGNOSIS, NOT A RESULT** (carved into `realstat §4` the same day). A
placebo should land **on** the floor; landing **below** it means the arm was built with the
ingredient *inverted*, not *absent*. So the clause-2 column above bounds **benefit + harm**, and
the value of aboutness in isolation is the neutral gap `topw − generic`, whose CI is
[+0.0045, +0.0192].

⛔ **BUT THAT GAP IS NOT A VALUE — IT IS BELOW THIS DESIGN'S RESOLUTION** (R303). The MDE of the
design that produced every number on this page — paired A2, 968 prompts, cluster bootstrap over
prompts, 80% power at a two-sided 5% test — measured on **real arm-vs-arm difference vectors** as
the noise template:

| specification | MDE (A2 units) |
|---|---:|
| `generic−full` template · percentile CI | [0.0140, 0.0180] |
| `generic−full` template · basic CI | [0.0160, 0.0200] |
| `topw−coval` template · percentile CI | [0.0100, 0.0120] |
| `topw−coval` template · basic CI | [0.0100, 0.0140] |

Placebo rejects at 0.040 / 0.080 / 0.050 / 0.030 against a nominal 0.05; positive control reaches
1.000 at the top dose in all four.

| claim | effect | effect / MDE | |
|---|---:|---|---|
| `topw − generic` | 0.0114 | [0.57, 1.14] | **AT OR BELOW RESOLUTION** |
| `coval_core − generic` | 0.0117 | [0.58, 1.17] | **AT OR BELOW RESOLUTION** |
| **`generic − full` (the price)** | **0.0420** | **[2.10, 4.20]** | **CLEARS** |
| `generic − random` | 0.0611 | [3.06, 6.11] | **CLEARS** |

**So the −0.0420 price stands as a value and the +0.0114 does not.** Below the bracket in 2 of 4
specifications, inside it in the other 2, above it in none. The honest form is a **bound**: *the
benefit of being about the prompt is positive and smaller than ~0.019* — still 4× below the sham
gap, so the correction to the sham reading holds with a bound in place of a point.

⚠ **The `site MDE 0.1250` from A13 does NOT govern any of this**, and reading it as if it did was a
scope error in the word *site*. That number is `P(force class agreement)` for a **subset-core
against the full rubric**, on **A1 exact class agreement**, at **n=250**, with a one-sample
detector. Every number on this page is a **paired A2 difference between arms against human
classes** at **n=968**. Different statistic, different comparand, different n, different test.
(⚠ and `0.1250` is superseded: it came from a hand-retyped-prompt tensor. On the canonical one the
arc's four detectors give (0.08, 0.09] to [0.105, 0.125] — R319, R320. It does not change this
paragraph's point, which is about the wrong statistic being imported, not about its size.)

⚠ **This is a CHOICE, and it must be read as one.**

⚠ **What the table does NOT claim.** The four admitted arms span A2 0.513–0.567 and their sham
gaps span +0.047 to +0.074 with **overlapping intervals**. Only `topw_k4` vs `coval_core` was
tested for a tie and found one (5 of 5 fidelity dimensions null). **Any ordering read off this
column is an argmax over overlapping brackets** — the failure retracted at k=4 this morning.

⚠ **And the clause that is NOT here.** Nothing about **size**, **source**, or a **ceiling**.
Each was tried, each named a number or a provenance the release cannot resolve, and each was
removed by the exclusion test rather than softened. `k = 3…8` are mutually indistinguishable;
a generated core with 98.8% novel content is admitted; the rubric's own reliability is
1.0 by construction.

---

## The definition — THIRD REWRITE, superseded by the table above, kept per L81

The second rewrite added a mechanical test: **for each clause, name an admissible object it
EXCLUDES.** Applied to itself, in one command, it killed four of its own five clauses.

| clause of rewrite #2 | what it excludes | verdict |
|---|---|---|
| *a small set of criteria* | k=12 — but k=12 vs k=4 is **−0.0069 [−0.0210, +0.0072]**, not separable | **under-determined at the upper end** |
| *reproduces human judgement* | `random_k4` — agrees with the rubric at 0.8247 and with the human at chance | **CLEAN. The only clause that does work.** |
| *at the humans' own level* | `gen`, at **−0.0183 [−0.0323, −0.0036] BELOW** the ceiling — and the benchmark accepts `gen`. Meanwhile `coval_core` **+0.0176** and `topw_k4` **+0.0141** are separably **ABOVE** it | **FALSE in both directions** |
| *may be selected or written* | nothing | **decoration** |
| *on this release selection measures better* | nothing | **a finding, not a clause** |

> ⛔ **SUPERSEDED — DO NOT READ THIS AS THE DEFINITION.** The sentence below is the 2026-08-03
> morning version, kept under L81 because the clause-audit table beneath it is the record of how the
> earlier clauses died. **The live definition is at the top of this file** and differs in both
> clauses: "chance" is now the named random-from-rubric baseline (R285: every arm is above literal
> chance) and "the same criteria on a different prompt" is now the size-matched prompt-blind arm
> (the poison-vs-placebo correction).
>
> *A core is a set of criteria that predicts held-out human judgement better than chance, and
> better than the same criteria applied to a different prompt.*

| clause | the admissible object it excludes |
|---|---|
| **better than chance** | `random_k4` (0.5005 ≈ chance) · `topvar_k4`, separably **below** random at −0.0123 [−0.0203, −0.0040] |
| **better than the same criteria on a different prompt** | `gen_sham` (0.4834, below random). This is the **aboutness** requirement, and it is the clause the whole sham design exists to make testable |

**Admits:** `coval_core`, `topw_k4`, `gen`, `full` — each beats chance *and* beats its sham.
**Excludes:** `random_k4`, `gen_sham`, `topvar_k4`.

⚠ **It does not distinguish a core from the rubric it compresses, and neither does the data.**
`full` qualifies. Size, source and ceiling are all **out** — every attempt to put them in named a
number or a provenance the release cannot resolve. What is left is small enough to be true.

---

## The definition — SECOND REWRITE, superseded, kept per L81

The first rewrite is annotated below. **Three of its five clauses failed the same test within
hours: a word chosen because it described the released object, then carried as though it had
been measured.** `four` (k-sweep: 3–8 indistinguishable) · `its verdicts` (cores track the human,
not the rubric) · `the rubric's own reliability` (a rubric is deterministic; its reliability is
1.0 by construction). This version states each clause with what currently supports it.

> **A core is a small set of criteria that reproduces human judgement at the humans' own level
> of agreement with each other. It may be selected from an existing rubric or written from the
> conversation; on this release selection measures better.**

| clause | status | the measurement |
|---|---|---|
| **a small set of criteria** | **MEASURED, size unresolved** | k=1 is separably worse; **k = 3…8 are mutually indistinguishable**; k=12 and the full 15.5 lose. "Four" is retracted — it was the released core's k |
| **reproduces human judgement** | **MEASURED, and corrected** | normalised by each target's ceiling, top cores reach **1.04 / 1.04 / 0.99** of the human ceiling against **0.74–0.80** of the deterministic rubric. `its verdicts` retracted |
| **at the humans' own level of agreement** | **MEASURED, and corrected** | the ceiling is **0.5451** (A2, one annotator vs another) — the *human's*. `the rubric's own reliability` named a quantity that is **1.0000 by construction** |
| **may be selected or written** | **MEASURED, permission not prescription** | a core generated from the conversation alone, **98.8% novel, 0 verbatim**, beats random and beats its own sham — but is **separably worse than selection on A2/A3/A4/A5** |
| **on this release selection measures better** | **MEASURED** | `topw_k4` and `coval_core` are the only pair no fidelity comparison separates; `gen` sits separably below both |

⚠ **`of a rubric` is gone from the definition on purpose.** The generated core never saw
`coval_full` and is still admissible, so the rubric is a **source of candidates**, not a
constitutive part of what a core is. Keeping the phrase would have made the definition false of
an object the benchmark accepts.

---

## The definition — FIRST REWRITE, superseded, kept per L81

The old definition is kept below, annotated, because a ledger that edits its own history is
the thing it exists to prevent. What follows replaces it. **Six measurements constrain it;
each clause names the one it rests on and the scope over which that holds.**

> **A core is a rewriting of a rubric that preserves its verdicts at the rubric's own
> reliability, using fewer criteria than the rubric contains.**

| clause | why it is worded that way | the measurement |
|---|---|---|
| **a rewriting** | not *a subset*. `coval_core` shares only **8%** of its text verbatim with `coval_full`, 23% at similarity ≥ 0.90, median best-match **0.676**. The task the release actually performed is GENERATION | overlap gradient over 792 core items |
| **of a rubric** | the source is named, because the compression is only defined relative to it | — |
| **that preserves ~~its~~ THE HUMAN'S verdicts** | ⚠ **`its` was wrong and is retracted the same day.** Normalised by each target's own reliability, every top core reaches the **human** ceiling (1.04, 1.04, 0.99) while reproducing only **0.74–0.80** of the deterministic rubric it compresses. A core is **not a summary of the rubric** — it tracks the judgement the rubric was written to approximate, and departs from the rubric to do it | measured human ceiling 0.5451; Δ normalised +0.23 to +0.26, all top arms |
| **at the rubric's own reliability** | two annotators of one prompt agree on the exact class **8.0%** of the time; a constant gets **4.0%**; the best available predictor **15.0%**. A definition demanding high absolute agreement is incoherent on this data | R283, controls saturated |
| **using fewer criteria** | 4 criteria beat 15 by a **separable** paired margin, and adding the discarded criteria back COSTS 1.5 points. Compression is a gain, not a loss to be bounded | B1 = 1.30 ± 0.10; topw_k4 − full = +0.0203 [+0.0055, +0.0362] |
| **(no admissibility gate)** | deliberately absent. Every counting gate — capacity, realised alphabet, ordered Bell — gated a combinatorial structure the data does not exhibit | see below |

### What the definition deliberately does NOT contain, and why

**⛔ No admissibility gate.** `C(n,k) ≤ a(m)` was undefined (two readings of `n` give 0% and
91.7% violation), was violated by its own founding round in **292 of 750 cells**, and compared
*candidate representatives* to *behaviour classes* — two different units. Its only unit-coherent
ancestor, `log₂|H(Q)| ≤ H_eff`, does not admit this release under any reading.

**⛔ No combinatorial requirement.** A core's value is **additive over its criteria**: an
independent per-criterion scorer reaches a combination search, +0.0079 [−0.0079, +0.0238], and
the separator returns **+0.4467** on a synthetic world that does contain set structure — 57×.
Any interaction is below **+0.0176**, the smallest effect this design resolved.

**⛔ No provenance requirement.** Resemblance to the source rubric predicts **nothing** about a
criterion's usefulness: slope −0.0145 [−0.063, +0.033] over 968 clusters, and the decile curve's
range is **1.06×** its own permutation null. Traceability is worth measuring — it is a property
you either want or do not — but it **does not buy fidelity**.

**⛔ No discrimination requirement.** Selecting criteria by satisfaction spread is
**indistinguishable from selecting at random**, +0.0017 [−0.0131, +0.0165]. *Zero variance ⇒
inert* is sound; *high variance ⇒ informative* is its converse and is false.

### ⚠ How few is "fewer"? — the clause above was under-tested when written

`k` was swept on the same rule, paired against k=4, the same day the clause was written:

| k | A1 | norm | paired vs k=4 |
|---:|---:|---:|---|
| 1 | 0.0472 | +0.048 | **−0.0244 [−0.0413, −0.0079] — separably WORSE** |
| 2 | 0.0640 | +0.204 | −0.0072 [−0.0213, +0.0072] |
| **3** | **0.0758** | +0.312 | **+0.0007 [−0.0117, +0.0134]** |
| 4 | 0.0761 | +0.316 | — |
| 6 | 0.0751 | +0.306 | −0.0007 [−0.0131, +0.0121] |
| 8 | 0.0751 | +0.306 | +0.0007 [−0.0127, +0.0145] |
| 12 | 0.0613 | +0.179 | −0.0069 [−0.0210, +0.0072] |

**6 comparisons, 1 separable.** Only `k=1` is distinguishable from `k=4`; **3 through 8 tie**, and
the k=4 "peak" beats k=3 by **0.0003**, which is noise.

⛔ **So "four" is not supported and I inherited it from the released core without testing it.**
What the data supports is: **more than one criterion, and this release cannot resolve `k` anywhere
in 3–8.** The reference construction below is stated at k=4 for comparability with `coval_core`,
**not because 4 was measured to be right.**

### The reference construction, and it is one line

**Take the four highest-mean-importance criteria of `coval_full`.** It ties the hand-built
released core on **every** fidelity dimension (11 cells, 0 separable), is 100% traceable where
the release is 40% novel, costs **no GPU**, and **no fitted model has beaten it** — a ridge over
8 deployable features returns −0.0110 [−0.0255, +0.0028] while its own leaky arm gains +0.1026,
so the design could have seen a gain and there was none.

⚠ **Status: this is what SURVIVED, not what is proven.** Every clause is scoped to one release,
one judge, and exact-class agreement. The register of what this site structurally cannot answer —
cross-release, construct validity, causal identification — is in `corebench/DIMENSIONS.md` and is
not a formality.

---

## The definition — SUPERSEDED, kept per L81

> **A core is a quadruple `(Q, class, representative, certificate)`.**
>
> | | |
> |---|---|
> | `Q` | the declared family of questions the downstream system must answer |
> | `class` | `[N]_Q` — the equivalence class of behaviours under `Q`. **This is the object.** |
> | `representative` | the criteria actually printed. **A choice, not a measurement.** |
> | `certificate` | which is which, at what noise, on whose instrument, and what was not measured |
>
> **Admissible only if** `C(n,k) ≤ a(m)`, where `a(m)` is the ordered Bell number — `a(4) = 75`,
> i.e. **`log₂ 75 = 6.23` bits.**
>
> ⛔ **AND IT WAS VIOLATED BY ITS OWN FOUNDING ROUND, IN 292 OF 750 CELLS** (R279, 2026-08-03).
> R248 introduced this gate and its persisted artifact records `C` for every cell it studied.
> At R248's **own** `a(4) = 75`, over R248's **own** 250 prompts:
>
> | k | violating | share | |
> |---|---:|---:|---|
> | 1 | 0 / 250 | — | **DERIVATION**: `C(n,1)=n≤14≤75`, forced by algebra, never evidence |
> | 2 | 84 / 250 | 33.6% | smallest violating `n` is 13 |
> | 3 | 208 / 250 | 83.2% | smallest violating `n` is 9 |
> | **all** | **292 / 750** | **38.9%** | |
>
> Controls: the artifact's `C` equals `math.comb(n,k)` in **750 of 750** cells, so the field is
> what its name says; negative control `n→n+6` moved 834→1412; placebo (`k=1` under `a(5)`) exactly
> zero; two hash seeds byte-identical. **k=4 is out of reach and registered as such** — R248 never
> ran it.
>
> ⛔ **AND THE LEFT-HAND SIDE IS UNDEFINED** (R278, same day). `n` admits two defensible readings
> and they do not disagree about a magnitude — they disagree about whether this release is
> admissible at all. At the operating point `m=4, k=4`: `n` = `coval_full` (median 15, max 39) →
> **888 of 968 prompts violate (91.7%)**; `n` = the six seed criteria → **0 of 968 (0.0%)**.
> R248/R252/R253 all draw from `coval_full`, which settles the reading by code rather than taste.
>
> **How this was missed for five rounds:** the argument was about whether the right-hand side should
> be `6.23` bits or `3.45`. Both sides took `C(n,k)` as given, so neither could see that the
> left-hand side had already broken the gate. **A unit check would have caught it before any of it**
> — `C(n,k)` counts *candidate representatives*, `a(m)` counts *behaviour classes*, and those
> strings are not equal.
>
> ⛔ **AND THE DEFINITION CONTRADICTS ITS OWN CLAIM 5.** Claim 5 is still `MEASURED` and was never
> retracted: the channel delivers `H_eff ∈ [1.02, 3.45]` bits, so the gate's 6.23 is wrong by 2–6×.
> The gate went `log₂|H(Q)| ≤ H_eff` → `C(n,k) ≤ A_real` → `C(n,k) ≤ a(m)`, and **un-retracting
> `A_real` silently reverted `H_eff` too — only `A_real` was retracted.** So this is not where the
> definition started; it is two steps behind it, at the pre-R237 noiseless bound.
>
> **What that leaves, stated plainly: the definition currently carries NO admissibility criterion
> valid in this release's own noise regime.** The gate is a number the document says is wrong, its
> replacement is retracted (R253), and the one surviving upgrade is scoped to `eps = 0` (R259) — a
> world with 47.8% two-rater agreement is not that world. **Found by a clean-context adversary, not
> by me, and I had predicted "it ended where it started", which was the flattering reading.**
>
> ⛔ **`A_real` was tried as the right-hand side and is RETRACTED (R248 → R253).** It measures
> something real (claim 8, which survives) but it **predicts nothing about recoverability that the
> criterion count `n` does not already predict** — partial rank correlation `−0.0380` and `+0.0107`
> at k = 1, 2, against a permutation `|null|₉₅` of `0.1152` / `0.1399`, `p = 0.535` / `0.850`; and
> adding it makes held-out error **worse** (`+0.0183`, `+0.0085`). `n` alone predicts recovery
> *better* than `A_real` does (`−0.2516` vs `−0.1881`). **The gate had `n` on both sides.**
>
> ⚠ **The measurement R248 made is intact and is not the gate.** Over 250 prompts the median
> `admitted / A_real` is **1.33 / 4.67 / 5.77** at k = 1 / 2 / 3, reaching **10.71** at the ninth
> decile: the data realises far fewer classes than the observation space admits. True, and it
> **does not license a replacement**, because both sides of that ratio are functions of `n` and `k`
> and the difference carries no incremental information about what is recoverable.
>
> **Admissibility is a RATE, not a predicate — AT ZERO RATER NOISE, AND ONLY THERE** (R248,
> scoped by R259). The share of size-`k` subsets this release can identify is
> **U(1) = 0.5714 · U(2) = 0.0606 · U(3) = 0.0105**. Exhaustive arithmetic about the tie structure,
> not a renaming — **and it stops predicting anything once the release's own rater noise is
> present.**
>
> | k | eps | recovery | partial(U \| n) | perm `\|null\|₉₅` |
> |---:|---:|---:|---:|---:|
> | 1 | **0.00** *(forced)* | 0.7470 | **0.7269** | 0.1324 |
> | 1 | **0.25** *(the release's own)* | 0.2566 | **0.0999** | 0.1340 |
> | 2 | **0.00** *(forced)* | 0.2215 | **0.4127** | 0.1265 |
> | 2 | **0.25** | 0.0682 | **0.0541** | 0.1216 |
>
> The `eps=0` row is **algebra, not evidence** — R228 showed noiseless recovery is `E[1/|ties|]` and
> `U` is the share with `|ties| = 1`. It is the positive control, and it fires, so the machinery
> works. At the noise calibrated to the release's own **47.8% two-rater agreement**, `U` is inside
> its permutation null at both k, and adding it to `n` **raises** held-out error (`+0.0143`,
> `+0.0021`) where at `eps=0` it lowered it (`−0.0325`). **The rate says nothing about what is
> recoverable in this release's actual noise regime.**

---

## The eight claims it rests on

**1 · The class is always identifiable; the member never is.** `DERIVED` (R230)
`|{classes under Q}| ≤ |{observations}|` by construction, because `Q`'s classes are *defined* by the
observation. Measured consequence: 72 subsets per prompt collapse into **13** classes, 5.2:1, never
above the forced bound of 75. Class recovery **1.0000** at zero noise (an identity, labelled),
**0.3233** at the release's own rater noise, against the member's **0.0613**.

**2 · The answer is a function of `Q` **and of the baseline's format**, and the sign can flip on
either.** `MEASURED` (R231, R243, and R235 independently)
On `Q =` reproduce Full's weak ordering, the official core scores **0.3864** against a random-4 floor
of **0.3836** — inside the floor's own draw spread, whose `[0.3657, 0.4019]` is a MIN AND MAX OF 20 DRAWS and is no longer quoted as an interval. On `Q =` predict human pairwise
preferences (R220), **0.6602** against a random range of **0.645–0.659**.

⚠ **"Clearly above" is retired, and what replaces it is stronger in one way and weaker in another**
(R262). Re-run under `PYTHONHASHSEED 0/1/2/3`, R220's floor spans **[0.6420, 0.6580]** and the core
clears the top of **every** seed's range — so unlike R231's, this comparison does **not** flip with
the environment, and it had been run exactly once before today. **But the margin over the worst
seed's ceiling is `+0.0022`, and the floor's own hash-seed spread is `0.0020–0.0030`.** A margin the
size of its baseline's arbitrariness is *above*, not *clearly above*. Same data,
same judge, opposite verdicts. **Reporting a preservation percentage without naming `Q` reports a
choice.**

⚠ **Corrected 2026-08-03 by the blind arm.** R243 swept `Q`'s granularity and the sign flips between
requiring **6 of 6** pairwise relations and **5 of 6** — so granularity explains the *sign*. It does
not explain the *magnitude* — **but "36×" is wrong twice and both errors inflate it.**
`+0.0068` is a mean pairwise agreement on `[0,1]`; `+0.2466` is Kendall τ_b on `[−1,+1]`. With zero
sign-ties `τ = 2·frac − 1` holds *identically*, and R243's core τ is `0.6643` against R235's `0.663`
— **on one scale the ratio is 18×.** And the numerator is not reproducible: R243's floor is seeded
with `abs(hash((p, d)))` on a **string** id, so under `PYTHONHASHSEED = 1/2/3/unset` the delta is
`+0.0084 / +0.0090 / +0.0083 / +0.0098` — **the published `+0.0068` is below all four**, the extreme
that maximises the ratio. Honestly re-run it is 25–30×; on a common scale, 18×. **A second
axis differs, and R235 found it without being told to look**: whether the random baseline is granted
the **signed** weights the core's format cannot carry. R235's own grid: *"72 of 286 cells have a CI
containing 0 or Δ<0 and **all** of them use signed weighting; **zero** uniform cells fail."*
**Reporting a preservation number requires declaring the baseline format as well as `Q`.**

**3 · Adding raters does not raise the within-prompt channel.** `MEASURED` (R225)
Recovery gain from keeping individual rankings instead of the consensus: `+0.019` at R=14 against a
seed spread of `0.06` — inside. It fires only at R=2, where the consensus is itself degenerate.
Three estimands were needed to establish this; the first two failed because *tie-count saturates at
both ends*, and the decisive bug was caught by arithmetic, not by a control.

**4 · Precision does not close the gap; independence does.** `MEASURED` (R227)
A 10-point score beats a ranking by `+0.5607` at zero noise and `+0.0118` at the noise level
calibrated to the release's own 47.8% two-rater agreement — **inside** a seed spread of `0.0296`. A
47× difference between the regime the capacity argument assumed and the one that applies.

**5 · The bound must use the noisy channel — and the gate now CONTRADICTS this claim.** `MEASURED`,
as a bracket (R237). ⚠ **The status line used to read "superseded as the gate by claim 8 (R248)";
claim 8's gate role was itself retracted by R253, so this was superseded by nothing.**
`H_eff ∈ [1.02, 3.45]` bits at the release's noise and rater count, against the `6.23` five rounds
assumed. `k=1` needs `3.91`, so **a one-criterion core sits at the edge of the bracket.** Partially
identified, so bounds and not a point.

⚠ R237 sharpened the *capacity* — how much the channel delivers under noise. R248 showed capacity is
the wrong quantity at any sharpness: the binding constraint is how many classes the **rubric**
separates, which is a property of the criteria's mutual agreement and is invisible to every channel
argument. `H_eff` stays as the noise correction it is; it is no longer the gate.

**6 · The failure is the per-prompt factoring, not the data volume.** ⚠ `UNVERIFIED` (R239,
downgraded by R255)
**R239 checked its independence assumption by EXACT TOKEN-SET IDENTITY** — of 15,058 criterion
token-sets, one recurs. **R255 then measured that half of all co-prompt criterion pairs share no
content word at all and still agree behaviourally** (median lexical Jaccard `0.0000`; discrimination
predicts agreement at ρ +0.1440 where lexis manages +0.0447). **Lexical distinctness does not imply
observational independence, and the bits-add derivation `[1006, 3402]` and `k ≤ 119` rest on it.**
Found by a clean context reading two of my own rounds against each other.
Within a prompt the bits do not add; across 986 prompts they do — `[1006, 3402]`. A **global** core
of up to `k=119` is identifiable at the conservative end while a per-prompt core of **2** is not.
The independence assumption was checked: of 15,058 distinct criterion token-sets, **one** appears in
more than one prompt. **CoVal ships the per-prompt object.**

**7 · The bits add across prompts and there is still nothing to identify.** `MEASURED` (R240 → R246
→ R247), and **claim 6 is demoted to true-and-inconsequential**, exactly as `A10/PREDICTION.md`
registered in advance.

R240 fitted a 32-criterion global core on 160,000 judgements over 200 prompts and printed *"A GLOBAL
CORE TRANSFERS."* Three rounds later that verdict is gone and the tensor never changed:

| | fitted core, held out | random-k floor | unselected all-200 | length only |
|---|---|---|---|---|
| R240, **3 seeds**, vs floor's **max of 20 draws** | 0.3500 | max 0.3467 | — | — |
| R247, **10 seeds**, vs the floor's **own 500-draw distribution** | **0.3060** (ptp 0.1100) | 0.2649 | **0.2550** | 0.0420 |

- **Empirical p over the whole k grid: 0.0699–0.1637. BH at q=0.05 kills all six.** R240's crossing
  was `0.3500 − 0.3467 = 0.0033` — **one prompt out of 300** — against the *maximum* of 20 draws,
  which is an extreme order statistic and not a floor.
- **Selection is not the ingredient either.** Using the **entire** 200-criterion vocabulary scores
  0.2550, inside the fitted arm's seed spread at every k. There is no compression to call a *core*.
- **The effect that remains is a direction, not a count**: fitted sits above the floor's *mean* at
  6 of 6 k with the same sign (+0.012 … +0.061), against a seed spread of 0.08–0.11. `effect/floor
  spread < 1.5`, so no share, no percentage — a gradient only.

⚠ **Two of R240's own controls said this before I did, and I read past both.** Its negative control
printed `NOT NULL` and `A10/PREDICTION.md` — written *before* the run — says a non-null negative
control makes the round `UNVERIFIED` regardless of its number. R246 then measured *why*: the arm
evaluated an already-fitted core on a random half of **all** prompts, which is **50.00%** training
data by construction. It could not have come back null.

**What survives, and it is narrower than a core.** Greedy selection over a generic vocabulary
recovers the modal-plus structure out of sample better than *scrambled-target* selection does
(0.2080 vs 0.3060 at k=32) — so the fitter is not overfitting. It simply has nothing to find that
the whole vocabulary does not already carry.

**And two rivals died on the way, which is why the null is admissible.** The target class
distribution is nearly flat — 24 classes over 200 prompts, modal share 0.10, entropy **4.485** bits
against 4.585 for uniform — so a response-blind modal predictor scores **0.0633**, not 0.35.
Response length alone scores **0.0420**. Neither artifact explains anything here.

**8 · The rubric is redundant beyond its own marginals — but "binding constraint" is RETRACTED.**
`MEASURED` (R248, defended R252); the *binding* claim killed by R253

⚠ **The heading used to read "the binding constraint is the rubric's own redundancy, not the
channel."** That is two claims and only the first survives. Redundancy is real and survives its
strongest confound. **Whether it BINDS anything was never tested, and when it was (R253), the
quantity carrying it — `A_real` — predicted recovery no better than the criterion count.** A
property can be present, robust, and load-bearing for nothing. The phrase stayed for five rounds
because it was doing rhetorical work the measurement never did.
Paired per prompt, against a **random tensor of identical shape**: the real rubric separates
**fewer** classes than random noise does, at **62.0% / 90.4% / 91.2%** of prompts for k = 1 / 2 / 3
(median deficit −0.60 / −4.80 / −6.00 classes). This kills the reading that the collapse is
geometry — the quotient of subset-sums into 75 weak orderings — because random criteria pass
through the same quotient and come out **more** separated. **The criteria agree with one another.**

**And it survives its own strongest confound** (R252, run one round later, against my own claim).
R248's rival was `rng.random()` — **uniform, sd 0.2887, against the real tensor's 0.2399: 20.3% more
spread.** A weak ordering is a function of pairwise gaps, so a wider marginal separates more classes
for reasons that have nothing to do with redundancy. R248 varied two things and named one.

The control that separates them: **permute the four response values independently within each
criterion row** — every criterion keeps its *exact* multiset of values, so the marginal is identical
not approximately but exactly, while the alignment *between* criteria is destroyed.

| k | REAL | UNIFORM | **ROW-PERMUTED** (marginal-matched) | GAUSS-MATCHED |
|---:|---:|---:|---:|---:|
| 1 | 8.00 | 9.20 | **10.10** | 9.40 |
| 2 | 12.00 | 17.10 | **17.90** | 17.40 |
| 3 | 12.00 | 19.60 | **19.60** | 19.40 |

Paired sign test over 250 prompts (scale fixed before the run, after R249's mis-scaling):
`k=1 +1.40, 210 up / 30 down, p = 1.9e-34` · `k=2 +5.40, 228/19, p = 1.1e-46` ·
`k=3 +5.80, 230/18, p = 5.0e-48`.

**The uniform rival was CONSERVATIVE, not liberal**, at k=1 and k=2 (+0.60 and +4.80 against the
marginal-matched +1.40 and +5.40). Controls: identical criteria give `A_real = 1` and rise to 7.2 /
18.0 / 17.4 after row-permutation; the identity permutation reproduces the real tensor exactly; and
the **sham** — the *same* permutation applied to every criterion, i.e. relabelling the responses —
leaves `A_real` **unchanged at 9 / 14 / 15**, which is what isolates *agreement* from *labelling*.

⛔ **Consequence: none for the definition.** This paragraph used to end *"only the second number
predicts whether a core is recoverable"* — verbatim the sentence R253 retracted, left standing three
lines under a heading I had already fixed (`fc2c5c4`). **A fix that landed on one path of two**, and
a clean context found it before I did. `A_real` predicts recovery no better than `n`; redundancy is
a real property of the rubric that governs nothing measured here.

⚠ **This round's first positive control could not pass, and repairing it produced the result.** It
demanded `A_real = C(n,k)` from a "maximally separated" synthetic prompt — but a class is a **weak
ordering**, a quotient of the sum vector, so distinct sums need not give distinct classes and no
construction in vector space forces the quotient injective. It returned **10 of 28** at k=2 while a
real prompt returns **12**: *the synthetic bracket sat below the data it was built to bound.* The
replacements are a k=1 case where the ceiling is constructible (exact, passes) and an independent
recount through a second code path (exact agreement, 25 prompts × 3 k). **Fifth
control-that-cannot-pass in this arc, and the first whose repair was the finding.**

---

## 9 · The triple blind, CLOSED — both arms reported, read under the rule fixed before they ran

`A08/README.md` fixed the reading before either agent launched: *disagree on sign → the framing is
the finding, find the assumption they differ on and test that* · **the three will not be averaged.**

### The assumption they differ on, and design A tested it itself

| arm | target | core vs a top-4-by-weight heuristic |
|---|---|---|
| **R234** primary, `Φ` | the full rubric's own signed-weight ordering | **top4_pos beats core +0.0352**, survives BH |
| **R235** | rubric-to-rubric | **top-4-by-mean-weight beats core in 76/286 cells, core wins 0** |
| **R234** leakage-controlled | same target, **top4 selected on a DISJOINT annotator half** | **core 0.8182 > top4 0.8066 — the sign REVERSES** |
| **R234** human arm | the humans' `world` rankings | core **0.6593** vs top4_pos 0.6547; `−0.0046 [−0.0122,+0.0029]`, p=0.26, **BH-killed**, `CI_width/|eff| = 3.3` |
| **R231** (mine) | Full's exact weak-ordering class | core 0.3864 vs random-4 floor 0.3836 — inside. **I never ran a top-k arm** |

⚠ **R234 retracted the mechanical-compiler result by its own analysis, and the reason applies to
R235's too**: *"that target structurally favours subset compilers, since a subset is a sub-sum of
the target's own basis."* The weights used to **select** top-4 are the same weights that **define**
the target. Under leakage control the gap inverts; the human arm is null; the K-sweep is null.
**R235's 76-of-286 is measured on the confounded target, and this arc carried it for two rounds.**

**And the prior-art check neither R235 nor I ran**: R234 read `data/DATASET_CARD.md` first. The card
**documents `top4_pos` as the release's own selection rule**, and documents the positive-weight
rewrite. So "a four-line compiler matches the core on selection" is **the card restating itself** —
the compiler's remaining work is the *rewrite*, which is exactly where R249's redundancy finding
and R250's provenance curve live.

### R234's headline, with its scope

**`Λ_budget = 0.4237`** (seeds 0.4273 / 0.4188 / 0.4252) — the core reaches 42% of what any
4-criterion unit-weight compiler can reach. **Bounded, not estimated**: greedy verified exhaustively
on the 458 prompts with n ≤ 14 (suboptimal on 4.1%, shortfall 0.0069 Φ), so **`Λ_budget ≤ 0.44`**.

| compiler | Φ vs full signed | | human `world` |
|---|---:|---|---:|
| full_signed (target) | 1.0000 *(derivation)* | full_signed | 0.6765 |
| oracle4 (greedy ceiling) | 0.9797 | **core** | **0.6593** |
| top4_pos *(the card's own rule)* | 0.8622 | top4_pos | 0.6547 |
| **core (shipped)** | **0.8270** | full_unit | 0.5961 |
| full_unit (signs dropped) | 0.7669 | sham | 0.5024 |
| random4 — measured floor | 0.7146 ± 0.006 | | |
| sham_core — negative control | 0.4945 *(chance)* | | |
| worst4 | 0.2785 | | |

**Compression cost against humans: `0.0173` [0.0100, 0.0250], 2.1× the measured resolution floor of
0.0081. Above-chance retention 90.1%.** The K-sweep peaks at K=5 (0.6560) then declines — **the core
sits above every K from 1 to 10.**

> **R234's verdict, in its words:** *"The core is a faithful compression of what the full rubric can
> **decide**, and an unfaithful compression of what the full rubric **is**. The loss is in the
> FORMAT, not in this compiler's choices."*

### What R234 found against itself — all four reported, none buried

- **Its pre-registered ceiling was wrong**: `Λ_prereg = 1.142`, outside [0,1], because the split-half
  ceiling compares two n/2 aggregates while the core is scored on the n aggregate. It calls this
  *"the control-that-cannot-pass failure in mirror image"* — **independently hitting the failure mode
  this arc hit six times.**
- **A reproducibility defect in its own code**: `list(set(prompt_ids))` in the cluster bootstrap, and
  Python salts string hashing per process. Two identical runs gave a byte-identical grid but a
  **different summary** — 23 se/p values moved (largest p 0.095 → 0.117). No BH decision flipped,
  and it says so: *"luck, not design."* Fixed to `sorted(...)`, then byte-identical.
- **It retracted its own prohibition finding.** Its first statistic was a ratio of Fisher-z means
  with a near-zero denominator, permutation null centred at **−1.43**. The difference-in-differences
  gives `A = −0.057 [−0.162, +0.041]`, BH-killed. The veto arm points the other way: **the core
  retains 76.1% of above-floor veto detection while mechanically dropping the signs retains 0.9%.**
  The card's documented positive-weight rewrite does real work.
- **S1 is `UNVERIFIED`, not null**: the polarity asymmetry's **sign flips across instruments**
  (+0.19 / −0.20 / −0.21 / −0.29). It is a property of the judge, not of the rubrics.

### The gauge finding that reaches every round in this repository

**The judge is not label-order symmetric.** Reversing *"Yes or No"* to *"No or Yes"* in the question
moves its output to **r = 0.77 against itself**. R234's positive control reproduces the cached tensor
at r = 0.998, so the instrument is faithfully re-implemented — and then fails a basic gauge test that
**every round here, including all of mine, has assumed away.**

**R257 ran the propagation R234 called for, and its repaired pass reproduces R234's instrument
exactly: `r = 0.9980, MAD 0.0082` against R234's `0.998 / 0.008`.** The first pass had retyped the
prompt and scored 0.9407; importing `covalx.judge.build_prompt` closed it.

| control | value |
|---|---|
| **positive** — default re-judge vs the r04 cache | **r 0.9980, MAD 0.0082** |
| **negative** — 200 tasks judged twice in one process | 90.5% exact, **r 0.999450**, max 0.03097 |
| **gauge** — default vs flipped label order | **r 0.7851, MAD 0.2745** |
| **sham** — one extra space, same words, same order | r 0.9853, MAD 0.0669 |
| affine residual per prompt | 0.0340 (only this can reorder) |

**The flip is 4.1× the whitespace sham and 33× the determinism floor** — it is label order, not
prompt fragility in general.

| quantity | default | flipped | verdict |
|---|---:|---:|---|
| **Q1** R231 core vs floor | 0.4120 vs 0.3846 (**+0.0274**) | 0.3560 vs 0.3664 (**−0.0104**) | **OVERTURNED — sign flips** |
| Q2 R252 redundancy sign | 205/41 · 234/14 · 229/21 | 193/41 · 221/26 · 215/32 | **CONFIRMED** |
| **Q3** R249 minimal size | 1.4680 | 1.6360 (**+0.1680 = 7.7× its own se**) | **DOWNGRADED gauge-dependent** |
| Q4 R256 λ₁ excess | 0.1432 | 0.1423 | **CONFIRMED** |
| Q4b R256 rank-1 class | 0.4320 | 0.4200 | **OVERTURNED** |

### The hierarchy of error on that one number, measured (R266)

Three axes were reported today and nobody asked **which binds**. They have different remedies —
draw noise is bought with compute, instrument noise is not bought with anything this release
carries.

| DRAWS | floor mean | seed spread | gap (core − floor) |
|---:|---:|---:|---:|
| 10 | 0.3819 | 0.0096 | +0.0045 |
| 20 *(R231's committed value)* | 0.3833 | 0.0075 | +0.0031 |
| 100 | 0.3835 | 0.0024 | +0.0029 |
| **200** | 0.3829 | **0.0034** | **+0.0035** |

| source | size | vs the residual |
|---|---:|---:|
| residual **draw** spread at 200 | 0.0034 | 1× |
| **label order** (R257) | 0.0378 | **11.1×** |
| **batch bf16 noise** (R260) | 0.0568 | **16.7×** |
| **the gap itself** | **+0.0035** | 1.0× |

**The effect is the same size as the smallest noise source and one sixteenth of the largest.** The
gap's sign is stable at `+` across all five draw levels once draw noise is removed — **and it is
still not resolvable**, because the two axes compute cannot touch are an order larger.

> ⛔ **"More draws would settle it" is forbidden.** What R231 needs is a second instrument, and the
> release does not carry one — R164's variant tensors cover the full and core sets, not the
> arbitrary subsets the floor draws from.

Controls: the forced `1/√DRAWS` law holds (2.82 against a predicted 4.47, a harness check and not
evidence); the floor's **mean does not drift** (0.0022 against the DRAWS=10 spread of 0.0096), so
`DRAWS` changes precision and not the estimand; `DRAWS=20` lands inside R262's measured band.

⛔ **Q1 is now overturned or unresolvable on THREE independent axes** — label order (here), measured
batch noise (R260: interval contains 0), and `PYTHONHASHSEED` (R261: the sign flips between seeds 2
and 3). Three unrelated sources of arbitrariness, one conclusion: **`0.3864` against `0.3836` was
never a comparison.**

**And exactly two quantities in this arc survive every gauge tested: R252's redundancy sign and
R256's λ₁ excess.** Neither instrument is privileged — a quantity that moves is `UNVERIFIED`, never
"right in the default".

Stable across all four instruments: `top4_pos − core` on humans is **null on all four**, and core
veto retention ≫ full_unit on all four. **Not** stable: above-chance retention (0.673–0.919), veto
retention magnitude (0.458–0.864), and the polarity sign.

Multiplicity: BH q=0.05 over **C=46** p-valued tests, **31 survive**, non-survivors listed. 120
specification rows carry no p-value and are published whole; `Λ_budget` spans [0.375, 0.477] and
**100% land in the same verdict band.**

---

## 10 · What the blind arm established that this arc never did — `SINGLE ARM`, R235, seed 29

Attributed, not absorbed. Design A has not returned and none of this is replicated here.

- **Compiler intelligence: ⛔ this line is RETRACTED by the other blind arm.** R235 measured
  `top-4-by-mean-weight` beating the official core in **76 of 286** cells, core in **0**, primary
  `−0.0224 [−0.0407, −0.0050]`, and concluded *"the compilation adds no selection value."*
  **R234 tested that target and it does not hold up**: the weights used to *select* top-4 are the
  same weights that *define* the target, so a subset is a sub-sum of the target's own basis. Select
  top-4 on a **disjoint annotator half** and the sign inverts — core **0.8182** vs top4 **0.8066**.
  The human arm is null, the K-sweep is null. **And the card documents `top4_pos` as the release's
  own selection rule**, so the comparison was the card restating itself.
  *Kept rather than deleted (L81): this is what a confounded target looks like when every number in
  it is correct.*
- **Extrinsic retention `0.855 [0.818, 0.890]`** — the share of the full rubric's agreement with human
  *world* rankings that survives compilation. A number this arc never produced.
- **The weight matrix is `39.7%` filled, and the score `0` is used once in `102,147` ratings.**
  *"Not rated" and "rated zero" are not distinguishable.* R235 carries both readings as separate
  specification cells and they give different answers (η 0.10 vs 0.25). **This is a missing-data
  semantics problem affecting every weighted claim in this repository, including mine.**
- **`personal` rankings cover `29.8%` of prompts** — a prompt-level split, so a valid subpopulation.
  Consistent with R220's 26.66% of *assessments*; different denominator, same restriction.
- **The rubric and prompt files share no key** — 0 of 986 IDs overlap; the join is rebuilt from prompt
  text, which `covalx/judge.py` documents and R235 rediscovered and positive-controlled at 966/966.
- **R235's own pre-registered negative control could not fail** and it said so: permuting the
  interaction residual preserves every column mean, so an unsigned uniform rubric — which scores by
  the *mean* — is unchanged in **47.2%** of prompts. **Same failure mode this arc hit four times,
  found independently, reported rather than buried.**

## What the official core scores against this, and why that is not an indictment

R236 issued the certificate as **NOT ADMISSIBLE, two fields FAILED** — ⚠ **and that header is now
stale, because the two bullets under it repair both fields it names.** `representative` was issued
by R249; `provenance` is ≥ 0.0777 by string identity (R250). The header stood for eight rounds and
then survived its own repair by three.

- `representative` **— the split now exists** (R249). Eight rounds repeated *"naming the split would
  pass the field"* without producing it, because R228's `k_max` describes the **space of candidate
  subsets** and the certificate needs a statement about **the four criteria that were printed.**
  Measured by exhaustive leave-one-out over the printed set, 967 prompts, r04 tensor:

  | | |
  |---|---:|
  | criteria printed per core | **3.95** |
  | necessary-within-set | **1.45 (36.7%)** |
  | minimal subset reproducing the core's own class | **1.42** |
  | prompts where **zero** printed criteria are necessary | **23.8%** |
  | prompts where **all** are | 5.4% |
  | minimal size = 1 | **642 of 967 (66.4%)** |

  **On two thirds of prompts a single printed criterion reproduces what all four produce.**
  Controls: a synthetic core of one discriminating + three constant criteria returns exactly
  `necessary=1, minimal=1` and flags the right one; four identical criteria return `0, 1`; the
  placebo (the minimal subset induces the core's own class) holds on all 967.

  ⚠ **PROXY LEDGER.** `necessary` is *necessary-within-the-printed-set*, never *identified among the
  `C(n,k)` alternatives* — R231 measured that separately at 0.3864 against a floor of 0.3836. Only
  **`redundant` is sound in both directions**: if the class does not move, that criterion
  contributed nothing to this observable, full stop.
- `provenance` **— `0.00` is RETRACTED** (R250). R232's query is intact and still holds: across all
  986 rubrics every `coval_core` item carries exactly one field, `criterion`. **But the absence of a
  lineage COLUMN was reported as the absence of lineage,** and that inference was never checked —
  including by me, one round ago, in a commit body that said the field *"cannot be repaired from
  this release."*

  Asked of the object rather than of memory: of **3,899** printed core items, **303 (7.77%)** are
  **verbatim string matches** to a criterion in their own prompt's full rubric, and **943 (24.19%)**
  reach token-Jaccard ≥ 0.6. Provenance is therefore **at least 0.0777**, established by string
  identity with no inference at all.

  Those 303 are also the first **ground truth** this arc has had for anything: their parent is known
  without a model. R250 calibrates how far a rewrite can travel before provenance stops being
  recoverable — 298 usable items, 14,304 judgements, chance `0.0792` (mean candidate set 14.43):

  | dose | text-Jaccard to parent | **behaviour route** | text route |
  |---|---:|---:|---:|
  | identity | 1.0000 | 0.9883 *(identity, not a test)* | 0.9883 |
  | drop 20% | 0.7995 | **0.3031** (± 0.0436) | 0.9883 |
  | drop 40% | 0.6000 | **0.1913** (± 0.0235) | 0.9871 |
  | drop 60% | 0.4014 | 0.1051 (± 0.0168) | 0.9855 |
  | first-clause truncation | 0.4621 | **0.2299** | 0.9883 |

  **Provenance is recoverable by judge behaviour alone at 2.4–3.8× chance out to 40% content-token
  deletion, and at 2.9× chance under first-clause truncation** — the direction R249 showed the
  compiler actually travels. It reaches chance around Jaccard ≈ 0.40, which is the MDE.

  ⚠ **The text route's flat 0.988 is not evidence.** Deleting tokens never *introduces* a
  competitor's tokens, so a subset of the parent stays nearer the parent than anything else — token
  deletion cannot kill a set-overlap matcher. Real rewriting **substitutes** words; this dose axis
  does not. Likewise **shuffle is a null perturbation for the text route** (Jaccard is set-based),
  which its `1.0000` distance column makes visible.

  **R251 added substitution and the text route still did not move** — 0.9883 / 0.9860 / 0.9696
  (rival 20/40/60%) and 0.9883 / 0.9883 / 0.9855 (generic), at Jaccard down to **0.2848**. Behaviour
  fell as before: 0.2366 / 0.1353 / 0.0755 and 0.2349 / 0.1387 / 0.0968 against chance 0.0792.
  Its distance control passed — every substitution dose moves the text further than matched
  deletion — and its negative control sat at chance on all seven doses.

  ⛔ **But R251's verdict called that "adversarial substitution" and it was not.** Its donor pool was
  the **union of every rival criterion**, so the injected tokens *scatter* and no single competitor
  can overtake the parent. **A set-overlap matcher is not beaten by noise; it is beaten by
  concentration.** Fifth conclusion-string failure in the session, same shape as the other four: a
  comparative asserted rather than computed. R254 runs the concentrated version — substitute toward
  the **single nearest rival** and measure the crossover — with both ends of its positive control
  pinned (`f=0` must return 0.9883; `f=1` must return ≈0 *and* name the rival as top hit). Running
  on GPU task 570.

  Controls: the ceiling is **computed**, not assumed — `0.9883`, because 7 of 298 parents have a
  duplicate in their own rubric and the 1/k tie rule makes exact 1.0 unreachable. *The first
  threshold demanded 1.0 and was the sixth control-that-cannot-pass in this arc.* The repaired
  negative control keeps the candidate set (parent reachable) and destroys the query: **0.077–0.089
  text, 0.047–0.055 behaviour, against chance 0.0792 — at chance at every dose.** *The first version
  matched against a different prompt's rubric, where the parent is absent, so its 0.0000 was forced
  by the candidate set.*
- `transport` **NOT_MEASURED** — requires a second candidate set. Now runnable; `UNVERIFIED` at R233
  because its own floors showed the arms differ in difficulty.

**And the redundancy is inherited from the WRITING, not from the SELECTION** (R249, W4 arm,
registered before it ran). Paired on the same 200 prompts:

| minimal sufficient size | mean |
|---|---:|
| the printed **core** | 1.3750 |
| random 4 from R240's **generic vocabulary** (real full-rubric criteria, chosen only for token genericness) | 1.3707 |
| random 4 from the **full rubric** | 1.6207 |

`core − generic = +0.0042 [−0.0870, +0.0955]` — CI contains zero.
`full-random − generic = +0.2500 [0.2077, 0.2923]` — it does not.

**Generic criteria agree with one another, and the compiler writes generic criteria.** That is a
different defect from "the compiler picks redundant criteria."

⚠ **But "generic TEXT" is the weaker of two mechanisms, and R255 measured both.** Over **14,687
within-prompt criterion pairs across 250 prompts** (`n_eff = 250`, not 14,687 — pairs inside a
prompt share their criteria), clustered bootstrap, 1000 resamples:

| predictor of behavioural agreement | ρ | CI95 |
|---|---:|---|
| **lexical** similarity (Jaccard) | **+0.0447** | [+0.0172, +0.0741] |
| the same, containment · Pearson · both | +0.0439 … +0.0481 | all nonzero, all tiny |
| **discrimination** — `min(sd across the 4 responses)` | **+0.1440** | [+0.1103, +0.1800] |
| sham: token-count difference | −0.0114 | [−0.0356, +0.0117] — contains 0 |
| negative: pairs across *different* prompts | −0.0002 | at its null |

**The CIs do not overlap: saturation beats lexis by 3.2×.** And the base rate is the striking part —
**the median lexical Jaccard between two criteria in the same prompt is `0.0000`**. Half of all
co-prompt pairs share *no content word at all*, yet their judgements agree. **Whatever makes this
rubric redundant, it is mostly not shared vocabulary.**

**And a fourth property was tried and retracted the same day.** R256 found a common factor above
its measured null (λ₁ excess **+0.1394**, permutation null 0.6210) but carrying the *decision* on
only **0.4440** of prompts. Its core-vs-full contrast — core 0.6000, full 0.4440 — **is a size
effect** (R258): the statistic falls **1.0000 → 0.6322 → 0.5458 → 0.5134 → 0.4886 → 0.4740** for
k = 1…6 **by construction**, because a 1-row subset *is* rank one. At matched size the core scores
0.6000 against random-4's **0.5134**, `+0.0866` inside a draw spread of **0.2148**. And the
cross-prompt sham tracks random almost exactly (0.5192 vs 0.5134) — **the statistic is structure-free
geometry of k rows in 4 dimensions.**

⛔ **And neither mechanism closes it.** R255's generic vocabulary is *less* discriminating than the
full rubric (0.0951 vs 0.1043), which fits saturation — but R234 measured the **core** as *more*
discriminating than the full rubric (`core/full sd = 1.1047`). **The core matches the generic
vocabulary on redundancy while differing from it on discrimination.** A third property is doing the
work and this arc has not named it. Residual gap, stated rather than smoothed.

⚠ **The pre-registered kill for that comparison was mis-scaled and is recorded `UNVERIFIED`.** It
compared a paired mean over 967 prompts (−0.2083) against a **per-prompt range over 20 draws**
(2.2378) — the same error this repository added to `realstat` as *"min/max of N draws quoted as an
interval"* three commits earlier, committed again while writing the round that cites it. The W4 arm
settles the question; the original threshold settles nothing.

**Every core is a choice of representative.** The official one is a defensible choice for the purpose
its dataset card states — a short readable summary. The certificate's job is to make the purpose and
the choice visible, not to score the object against a purpose it never claimed.

---

## The site's own MDE — what this release could ever have shown (R268)

Thirteen rounds measured what is not resolvable. This is the constructive form of the same
measurement, and it is the arc's real output.

**Detector calibrated empirically to α = 0.05 on 200 no-effect replicates, then validated on 200
FRESH ones it never saw: `α̂ = 0.0600`.** (R267's detector — `arm > max(3 floor draws)`, which is
**the comparison form R231 and R220 use** — fired at **0.2000** on the same test. That defect is
what this replaces.)

| g | mean arm | detect |
|---:|---:|---:|
| 0.00 | 0.3790 | 0.0800 |
| 0.06 | 0.4154 | 0.4300 |
| **0.10** | 0.4418 | **0.7700** |
| **0.12** | 0.4535 | **0.8600** |
| 0.20 | 0.5104 | 1.0000 |

> ### The site's MDE is **[0.1250, 0.1250]** in class-agreement units (R274; R268's `(0.10, 0.12]` was read off a 0.02 grid with a 200-draw calibration and is superseded **upward**).
>
> ### And the arc chose the coarser statistic: the HUMAN-ranking statistic's MDE is **[0.0260, 0.0300]** — the gap is **[4.17×, 4.81×]**, on the same release (R271 → R274).

⛔ **SUPERSEDED — AND THE NUMBER ABOVE CAME FROM A HAND-RETYPED PROMPT (R319, R320).** The line is
left standing because R274 computed it correctly from the tensor it was given; what was wrong was
the tensor. Six A23 rounds read `_archive/r257_first_pass/instruments_retyped_prompt.npz`, which
git object hashes prove is R257's **pre-fix** output — commit `4498585` records the cause in its own
body: *"my own positive control caught me retyping the prompt instead of importing it."* The
canonical tensor has existed since ten minutes later and nobody re-pointed the readers. **All six
now read it.**

**The site MDE, canonical tensor, four detectors on one release:**

| round | MDE | of the 5 published effects |
|---|---|---|
| R267 | **(0.08, 0.09]** | 4 below · 1 resolvable |
| R268 | **(0.08, 0.10]** | 4 below · 1 resolvable |
| R269 | **(0.08, 0.10]** | 4 below · 1 resolvable |
| R274 | **[0.105, 0.125]** | R249's move reaches detection 1.0 |

**One split** — everything this arc reported is below its own MDE **except**
`R249 minimal-size move under label order` at **0.1680**.

⛔ **THE FOUR BRACKETS ARE NOT FOUR OPINIONS ABOUT THE SITE, AND THE SPREAD IS NOW FULLY
DECOMPOSED (R321–R324).** Calling it "the honest width" was wrong; every component below was
measured with the others held fixed, and none of them is the release.

| component | round | what it does | evidence |
|---|---|---|---|
| **two estimands** | R321 | R267/268/269 take `min(g : observed ≥ 0.8)` bracketed by the **dose step**; R274 takes the range where a **binomial CI** contains 0.8 | R267's rule on R274's own curve gives `[0.110, 0.115]`, which R274's `[0.105, 0.125]` **contains** — on identical data the rules agree |
| **replicates** | R322 | the CI's **lower** end falls with fewer replicates; the upper end does not | 400→[0.105,0.125], 100→[0.090,0.125], 40→[0.085,0.125], everything else identical |
| **threshold** | R323 | `tau` is the **calibration size**, not a judgement | `quantile(cal[:200], .95) = 0.416000` = R268's committed tau; `cal[:3000] → 0.424000` = R274's. Both from **one array**, exact to six decimals |
| **dose grid** | R324 | a coarser grid shifts the bracket; a **short** grid cannot produce one | R268's step 0.02 moves both ends **+0.015**; R267's grid stops at 0.12 and its **upper end is undefined** |

**What is left over: nothing.** `tau` was the last unexplained number and it reproduces exactly.

⚠ **And R267's grid maximum is 0.12 while the one effect it calls resolvable is 0.1680.** It never
measured detection there — it **divided**, and its own output labels that section *"A DERIVATION,
not evidence"*. A grid that stops below the largest published effect can never do anything else.

> **So the site MDE is R274's `[0.105, 0.125]` — the finest grid, the most replicates, the largest
> calibration set, and the only one of the four whose interval is a statement about precision
> rather than about grid spacing. The other three are not rival measurements to be averaged or
> spread; they are the same release read through coarser instruments, and the differences are
> priced above rather than absorbed into a width.**

**And the statistic-choice gap two lines above moves with it, because it is that bracket divided by
a constant.** On the canonical tensor: `0.105/0.030 = 3.50` and `0.125/0.026 = 4.81`, so
**[3.50×, 4.81×]** replaces **[4.17×, 4.81×]**. Its upper end is unchanged and its lower end is not —
the same shape as the MDE it is built from, **as it must be**. Labelled a **DERIVATION** for that
reason, not a second measurement.

⛔ **AND THE ARC ONLY DISAGREED WITH ITSELF BECAUSE OF A TYPED WORD.** R267, R268 and R269 each
printed `0.1680 … resolvable` in their own effect table and then asserted *"NO EFFECT THIS ARC
REPORTED WAS RESOLVABLE AT THIS INSTRUMENT"* — a branch written against R260's interval (0.0568) as
though that were the largest published effect. The numbers were computed; the quantifier was typed.
**R274's retraction of that sentence was correct all along**, on either tensor. All three now compute
the split. `the verdict string is not a computation`.

> ### ⚠ The one effect this release can resolve is a measurement of the INSTRUMENT, not of the object.
> `R249 minimal-size move under label order` is how far the judge moves when two answer words are
> swapped. R267's own header keeps that axis **outside** the MDE deliberately — a single alternative
> instrument is a **bias**, and folding it into a **variance** would average the two. So the site can
> resolve its own instrument and nothing it went looking for.

**The two-tensor range is retained as history, not as the headline.** The tensors correlate at
**0.9508** — far from the **0.998** a faithful re-implementation achieves and well short of the
**0.77** a label-order flip produces (R234) — so they were never exchangeable draws. But one of the
two is a typo, and `neither instrument is privileged` was R257's line about **default vs flipped
label order**, a gauge. **A typo is not a gauge**, and quoting that line to avoid choosing was
wrong.


⚠ **R270 measured that gap at 2× and said it missed its own 3× threshold. R271 supersedes it**: R270
collapsed each prompt's annotators to a consensus *sign* first, giving 5,808 rows over 968 clusters
(ratio 6). The real structure is **93,558 rows over 968 prompts, ratio 96.7**. With the per-annotator
rows the gap is **4.0×**, which clears the threshold R270 set and could not reach.

### And the clustering inflation, as an interval rather than a point (R273)

Resampling **prompts** vs resampling **rows** on the same statistic:

| | MDE | |
|---|---|---|
| prompt-clustered | **[0.0260, 0.0300]** | the honest unit |
| pooled-row | **[0.0100, 0.0110]** | the wrong unit, run deliberately |
| **inflation** | **[2.36×, 3.00×]** | against `√(rows/clusters) = 9.83` |

Each bound is *the range of g where a 95% CI on detection still contains 0.8* — no interpolation, no
monotone fit. **The realised inflation reaches only 24–31% of what independence predicts**, so
intra-cluster correlation is large and **`√(rows/clusters)` overstates what the wrong resampling unit
buys** — the opposite of the direction the rule is usually quoted in.

⛔ **R272's point estimate of 2.0× is RETRACTED — it lies outside this interval.** R272 concluded
that *the grid, not the calibration, was the limiting term*, and then quoted a number the grid had
produced: at a 0.005 step the pooled MDE read as `(0.010, 0.015]`, where a 0.001 step puts it at
`[0.0100, 0.0110]`. **The coarse grid did not merely blur the number, it biased it low.**

| published effect | value | effect/MDE | |
|---|---:|---:|---|
| R231 core−floor gap | 0.0035 | **0.03** | below |
| R249 paired se | 0.0219 | **0.18** | below |
| R257 label-order delta | 0.0378 | **0.32** | below |
| R260 batch interval | 0.0568 | **0.47** | below |
| **R249 minimal-size move under label order** | **0.1680** | **1.40** | **resolvable** |

**Exactly one quantity this arc ever reported clears the site's own detection floor — and it is a
measure of the INSTRUMENT moving, not of the object.** Every substantive effect is 3–30× below what
this release can show. *Today's downgrades were forced by the site, not by the individual rounds*,
and **E05's real output is a specification for a better instrument rather than a set of findings.**

Controls: **positive** — the largest dose is detected 1.0000 against g=0's 0.0800, clearing 3
binomial se (0.0814); the threshold is **computed from two measured numbers**, where R267's was
typed as `> 0.9` and the design returned exactly 0.9000. **Placebo** — identical arms at the same
seed differ by exactly `0.000000`.

⚠ **R268's sham was void — and repairing it (R269) confirmed the MDE rather than moving it.**
It re-randomised *which* prompts carry the plant, and the carrier was all-`True`, so permuting it was
a no-op: 0.7200 against 0.7700 at the same g. **And the obvious repair is void too** — prompts are
exchangeable, so permuting which exchangeable units carry an effect changes nothing in distribution
at *any* fill rate. **A sham must destroy something the statistic depends on, and "which prompt" is
not such a thing.**

Two replacements, and only one of them is a test:

| | | |
|---|---:|---|
| **SHAM-A** uniform shift of g on all four responses | **0.1100** vs α 0.0600 | ⚠ **FORCED** — a constant cannot move a sign. A *placebo* in a sham's name; it checks only that the class function is shift-invariant **as coded**. |
| **SHAM-B** the same g applied to the **TARGET** instead of the arm | **0.0200** vs real **0.7700** | **can fail, and did not** — detection collapses below α when the plant is aimed at the reference |

**SHAM-B is the one that matters**: had making the reference easier *also* raised detection, the
statistic would not be measuring the arm and the MDE would be void. It falls from 0.7700 to 0.0200.

⛔ **The label-order axis is deliberately NOT inside this MDE.** It is one alternative instrument,
not a distribution — folding its 0.0378 in would average a **bias** into a **variance**.

---

## What is `UNVERIFIED` right now, and stays that way until it is not

| | |
|---|---|
| candidate-set transport (R233) | ⛔ **the reason carries a RATE, not a verdict** (R263 → R264). R241 concluded *"NO VALID STRATIFIER EXISTS"*, and that null closed this line. Re-run over **24 hash seeds**, R241's **own controls pass on 15 of 24 = `0.6250`, Wilson `[0.4271, 0.7884]`** — an interval that **excludes 0.9**, which was the pre-registered threshold for "cannot be quoted without its rate". On the other 9 seeds it prints `UNVERIFIED — the correlation machinery did not pass its own controls`. **Conditional on the controls passing the conclusion is stable (1 distinct verdict across all 15)** — so R241 is not *wrong*, it is **unreadable on 37.5% of runs**, and nothing records which kind the published run was. Positive control: the int-keyed R230 is identical at all 24 seeds, rate exactly `1.0000`. R238's headline separately moves `+0.0976 … +0.1242` (27%) on the same axis |
| the two independent designs (R234, R235) | dispatched blind at seeds 11 and 29. **The reading rule was fixed before they were launched** and they will not be averaged |

## What no elicitation here can settle

- whether a `k ≤ 2` core is **useful** — identifiability is not utility, and utility needs a
  downstream task the release does not carry
- whether **humans** would endorse any of these classes on unseen responses — no labels exist
- whether a core reaches a **trained model** — no `Y` in the release
- three designs from one model family test **framing**, never **population**

## The sentences that can no longer be written

- *"The core preserves X% of the rubric."* — unfinished until `Q` is named.
- *"This release cannot identify a core."* — it cannot identify a **per-prompt** one.
- *"The compiler selected four criteria."* — it selected two it could have identified and two it
  could not, and nothing in the artifact tells them apart.
- *"Candidate-set generalisation is structurally undetectable here."* — the artifact was in this
  repository for six days while I said that four times.
- *"The positive control failed, so the instrument is broken."* — five times out of five, the
  instrument was fine and the threshold was impossible. In R248 the impossible threshold was a
  synthetic control that scored **below** the real data.
- *"Admissibility is `C(n,k) ≤ A_real`."* — I wrote that into the definition, defended it against
  its strongest confound, and then found it predicts nothing `n` does not. **A quantity can be real,
  survive its confound, and still be decorative in the place you put it.**
- *"The capacity gate is loose by 5.5×, so it is the wrong quantity."* — looseness is not evidence
  of wrongness when the tighter quantity is a function of the same variables.
- *"A global core transfers to prompts it was never fitted to."* — R240 printed it, R247 killed it
  off R240's own tensor, and R240's own negative control had already said the round was unreadable.
- *"The floor is 0.2983 [0.2567, 0.3467]."* — that bracket is the **min and max of 20 draws**, not a
  floor. Comparing to the max is over-strict, comparing to the mean is under-strict, and **only the
  draw distribution is a null.** Three rounds quoted the bracket as though it were an interval.
