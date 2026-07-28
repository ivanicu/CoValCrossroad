# Retractions

Every claim this repository made and then killed, scoped or corrected — in the order
it happened, with what did the killing.

The rounds are numbered by when they ran, not by what survived. Read in that order
the repository looks like a sequence of findings. It is not. **Nine of these entries
are a later round destroying an earlier round's conclusion, and in seven of them
both rounds are mine.**

This file exists because the git log has all of it and nobody reads a git log.

| # | The claim | What killed or scoped it | What survived |
|---|---|---|---|
| 1 | **"Governance uncertainty exceeds sampling uncertainty at k=4"** (+0.028), inherited from the source package and reproduced bit-identically | Matched-pairing analysis. The two halves were different objects: a distance from a bootstrap to a **noise-free reference** versus a distance between **two objects both carrying noise**. Under either matched pairing the sign reverses: −0.032 draw-vs-draw, −0.003 reference-vs-reference | The k-curve shape. The zero crossing moves from between k=5 and k=6 to between k=1 and k=2 |
| 2 | **"2.96% of crowd-written criteria address anthropomorphism"** (r07, first lexicon) | Substring matching. `persona` was catching *personal*, *personality*, *personalities*; `friend` was catching *friendly*, *friendships*. 321 of 452 hits were false | Word-boundary regexes give **0.16%** — twelve times smaller. The finding got *stronger* via a bug |
| 3 | **Pre-registered gaming prediction**: a majority-generic target should show rising verbosity and criterion-keyword overlap under optimization (r09) | r09 itself. Every marker **fell**: words 125→116, overlap 0.307→0.284, bullets 1.62→1.34 | Nothing of the prediction. Reported as refuted rather than reframed |
| 4 | **"Optimizing the rubric improves held-out preference"** (+0.53 [0.06, 0.99], r09) | r11's independent-backbone control. The gold head shared Qwen3.5-2B with the judge. On an independent 0.8B backbone the change is **+0.05 [−0.44, +0.53]** — indistinguishable from zero | Only the bound: *no overoptimization detected at this pressure, and no improvement established either*. r09 had passed its own positive control and its own paired test |
| 5 | **Assurance claim C6 passed** while testing `positive_control_passed`, a field unrelated to its own statement about lexical overlap | Reading the claim next to its test. Rewritten to test what it asserts; it now **FAILS** at −0.0229 | The habit, generalised: every claim's test must be readable against its own sentence |
| 6 | **"The advantage is response-set-specific"** — criteria were written after their authors read the four candidates, so they encode facts about them (r12) | r13. Seed criteria, prepared alongside candidate generation and **never tailored to those responses**, carry *more* attribution (+0.039, CI excludes 0) than write-ins authored after reading them (+0.029, CI includes 0) | The datum: the advantage does not transfer, +0.102 → −0.042. Only the mechanism died, and what replaced it is stranger |
| 7 | **The whole assurance manifest**, after the repository was reorganised into `rounds/` | Running it. Every claim source had moved and all thirteen resolved to `UNSUPPORTED`, which reads as *not yet measured* rather than *this package can no longer find its own evidence* | A new status, `BROKEN_HARNESS`, that refuses to emit a manifest at all |
| 8 | **r17's first design** — route a rater on half a prompt's criteria, score them on the rest | The data. Every prompt shows the same six seed criteria: 731 prompts have exactly 6, none has 10, and a k=4 core consumes four. **No held-out design at the criterion level is possible on CoVal** | The constraint became a finding, and routing moved to cross-prompt history |
| 9 | **"Preserving disagreement harms the worst-off bloc"** (r16) | r17. With routing learned from a rater's *other* prompts, conditional directions help exactly the rules carrying contested items — conflict_aware +0.195, constituency +0.148 — while consensus-seeking rules move by less than 0.02 | The ranking. Conditional conflict_aware still reaches only 2.999 against un-conditioned utility at 3.609. The correct claim is narrower: preserving disagreement **with a single direction** harms the worst-off bloc |
| 10 | **My own suspicion** that r17's 84.6% routing accuracy was entirely free | r18. The inflation is real, +0.147 — but on contested items the router still reaches **0.666 [0.643, 0.688]**, nowhere near chance | Routing works, and works far less often than the headline implied. *The first time the data corrected a doubt of mine rather than a claim* |
| 11 | **"Less than half of a values evaluation measures values"** — reported as 43% | r19. The shuffled arm used a **random** donor, which retains 47–60% of the self signal because a random prompt sometimes shares topic. Against a nearest-topic floor the attribution is 0.047; against the farthest, 0.115. **Span 2.47×** | The bracket, 27%–67%, and the rule that any single figure must name its floor |
| 12 | **r19's own first bracket**, 29%–63% | r19's proper runner. The inline version averaged in a judge cell whose self accuracy was **0.5405** — barely above chance, therefore not decomposable. Excluding it *widened* the spread to 27%–67% | The direction is worth noting: the reported interval was too **narrow**, and it was narrow because noise had been averaged in as data |

---

## The adversary round — 2026-07-28

Entries 1–12 were found by me. Every one of them.

On 2026-07-28 three independent clean-context challengers were given a frozen clone
at `87ef2ab`, one lens each — statistics, construct validity, reproducibility — and
**no sight of [ADVERSARY_BRIEF.md](assurance/ADVERSARY_BRIEF.md)**, which had been
withheld precisely so that what they found could be scored against what I predicted
they would find. In roughly 45 minutes each they produced the following. Nine of the
twelve are theirs.

| # | The claim | What killed or scoped it | What survived |
|---|---|---|---|
| 13 | **r01's response-style control**, reported as one of three independent ways the persistence could have died (0.1479 → 0.1471) | My own gauge test, prompted by the reviews. **Pearson correlation is invariant to per-rater affine rescaling**, so z-scoring each rater within a prompt cannot move a Pearson-based agreement — ever. Measured: **131,771 of 131,771 dyads unchanged, median \|Δ\| = 5.55e-17**, machine epsilon | The persistence. But it was defended by **two** controls, not three; the third was algebra wearing the costume of evidence |
| 14 | **r01's ρ=0.147 as evidence for structured plurality (M2)**, the premise the whole r16/r17/r18 arm is built on | Statistics review, then [r23](rounds/r23_actor_vs_dyad). Agreement persists with **no blocs at all** if raters merely differ in reliability — a careful rater agrees with everyone. That is an additive **actor** effect, and r01's null (shuffling rater IDs) destroys actor and dyad identity together, so it had nowhere to land but "structure". Fitting `A_ij = μ + a_i + a_j` per prompt: the actor model takes **47.2%** of dyad variance and actor-only persistence is **0.254** — *higher than the headline itself* | Only the residual: pair-specific ρ=**0.034**, z=**+4.67** against a dyad-permutation null. Real, and **20–23% of what r01 reported**. The sharper test — an excess of pairs reliably negative in *both* halves, which reliability heterogeneity cannot produce because noise attenuates toward zero and never below it — **returns null at z=+1.40**. So the residual is equally consistent with unequal-size blocs and with a second axis of rater competence. **M2 is weakened, not rescued** |
| 15 | **r13's attribution, +0.039 seed vs +0.029 write-in** — the numbers that killed entry 6's mechanism | Statistics review; confirmed at the object. `run.py:164` computed `arr[:len(sa)].mean() - sa.mean()`: a **positional prefix** of an all-prompts array minus a differently-ordered subset, printed beside a `real` spanning all 968. The columns do not subtract to the published figure — **0.5835 − 0.5368 = 0.0468, but 0.0391 was reported**. A comment asserted pairing was unavailable; the pids were in hand and simply never recorded | Refit per prompt with a paired bootstrap: seed **+0.0457** [+0.0234,+0.0687] (n=300), write-in **+0.0262** [+0.0022,+0.0506] (n=293), gap **+0.0194**. The reviewer predicted the gap would collapse ~5× under a matched computation; **it roughly doubled** — their diagnosis of the bug was exact and their forecast of its direction was not, which is why a bug must be fixed and re-run rather than argued about. **But the write-in interval now excludes zero**, and *"write-ins carry no significant attribution"* was half of entry 6's argument. See the amendment below |
| 16 | **Assurance claim C1 HOLDS** | Reproducibility review. C1 asserts a **proportion** ("less than half of a rubric's ability") and tested `rubric_contribution` — a raw 0.0791 accuracy-point difference — against 0.5. Pairwise accuracy differences cannot reach 0.5, so **the test returns HOLDS at a true share of 90%** | The claim (42.5% < 50%), not the check. Rewired to test the share. **Second live instance of the exact class entry 5 claimed to have generalised away** |
| 17 | **That r13 is a CPU round that reproduces as documented** | Reproducibility review, by running it. Without `--with-shuffled` it wrote a 4-line JSON over the 20-line one, **silently deleting the attribution fields entry 6 stands on**, and exited 0 | A guard that refuses to overwrite a richer result, writes the partial elsewhere, and names the missing flag. Attacked before being believed |
| 18 | **Three README numbers** | Reproducibility review. Span **2.2×** where three other places in the repo say 2.47×; most-dissimilar-donor **0.102**, which is r12's in-distribution figure transplanted (r19 says 0.115); "the official core scores 0.660, **level with** the best simple rule" | The 0.660 is real — but it is r04-core, released rubric, 968 prompts, against r06's k=4 compression of `coval_full` on 945. **Nothing ever measured them against each other.** Two of the three are entry 12 not propagated to the prose |
| 19 | **"step R²=0.964 vs trend 0.448"** | Both reviews independently: **no script in the repository computed it.** `git log --all -S"0.964"` finds it only in prose. Worse, a free-breakpoint step charges nothing for choosing its breakpoint, so beating a straight line is close to automatic | [r24](rounds/r24_regime_receipt) supplies the receipt and the control it never had: breakpoint found by **search** (independently at position 6), against a null that **re-searches the breakpoint on every shuffle**. Null best-step R² = 0.172; observed 0.964, z=+7.09, **p=0.0001**. Within-segment slopes +6.84 and +1.04. The claim survives, stronger than when it was asserted |
| 20 | **r07's Tier-1 anthropomorphism rate, 0.16%** | Construct review, by reading all 24 hits. 7–8 of the 9 `personal opinion` matches **instruct the model to avoid** opinions; one `as an ai` hit is literally an anti-anthropomorphism disclosure rule; 4 `persona` hits are content roleplay on request. At most 11/24 are on-construct — true rate **~0.05–0.09%** | The direction, more extremely. **The same lexicon that produced entry 2 failed a second time**, in the same way, after being "fixed" |
| 21 | **That r16's blocs are a constituency** | Construct review, substituting demographic strata the release actually ships. Gender split regret **1.145**, country split **1.198** — both below r16's **own** 1.15×-random bar of 1.267 | The regret arithmetic and r18's contested-item router (0.6656, reproduced exactly). Not the word "minority", which no test in this repository supports |
| 22 | **ASSURANCE's population boundary, "1,012 annotators"** | Reproducibility review's from-scratch recount, reproduced independently here. The release has **two** populations, not one. Comparison rankings: 1,012, every one of whom also scored criteria. Criterion scoring: **1,160** distinct raters, of whom **148 (12.8%) appear in no annotator record** and therefore carry **no demographic, country or consent metadata at all** | The comparison rounds. Not the scope sentence — and this is load-bearing for entry 21: the demographic substitution that showed r16's blocs are not a gender or country constituency **could only be computed on the 87.2% who have demographics.** A bloc analysis cannot be checked against strata for raters who have none. Both the original bloc claim and its refutation are scoped to that subset |
| 23 | **That this file is complete** — "Every claim this repository made and then killed" | Reproducibility review. `r15`'s stored result carries both `conclusion` and `conclusion_original`, the latter headed **SCOPE CORRECTION**, and the commit message names it. `grep -in "r15" RETRACTIONS.md` → **zero hits** | Nothing. A ledger of retractions that omits a retraction is the failure it exists to catch |
| 24 | **r05's stated justification for using two instruments** — "embedding similarity 0.736 vs 0.520" | Construct review, confirmed by grep and `git log --all -S`. The number appears in **one docstring**, entered in the commit that created the file, and is computed **nowhere** | **UNVERIFIED**, which is not an acquittal. Separately: r05's actual headline *survived* a genuinely different instrument (TF-IDF cosine, family ranking ρ=0.93) — the round I most expected to fall |
| 25 | **Entry 6's entire argument** — "seed criteria carry attribution (CI excludes 0) and write-ins do not (CI includes 0), therefore seeds carry *more*", the asymmetry that made the response-set mechanism look dead | Entry 15's repair, then the interval I had never computed. **Both halves fail.** Write-ins clear zero after all (**+0.0262 [+0.0022, +0.0506]**). And the difference, bootstrapped paired on the 293 prompts carrying both arms, is **+0.0231 [−0.0079, +0.0541] — it includes zero.** The ordering is not established | Not the comparison. What survives is a **one-arm** argument, which is different and narrower: seed criteria — prepared alongside candidate generation and never tailored to those responses — carry **+0.0457 [+0.0234, +0.0687]** on their own. If the advantage were knowledge of the response set, response-blind criteria should carry ~none, and they carry as much as write-ins do. That still refuses the response-set mechanism; it no longer ranks the two. **And even that rests on a proxy**: "seed" is inferred from rating count, not read from a release field (below) |
| 26 | **The direction of the correction itself** — that fixing a broken estimator makes a finding firmer | The same run. The point estimate rose at every repair — **+0.0102** broken, **+0.0194** unpaired means, **+0.0231** properly paired — while the claim got *weaker at every step*, because the uncertainty was never computed until last. A bigger number and a dead claim, from one bootstrap | The rule, in its sharpest form yet: **the size of an effect and the strength of a claim are independent quantities, and this repository spent twenty rounds reporting the first as though it were the second** |

---

## The pluralism question — five separators, four of them mine and wrong

Entries 27–31 all belong to one question: **is r01's cross-prompt persistence value
blocs (M2), or raters differing in reliability (M1b)?** It is the premise the r16/r17/r18
arm rests on. It took five attempts, and the failures are more instructive than the
answer.

| # | The claim | What killed or scoped it | What survived |
|---|---|---|---|
| 27 | **r26's sign test**, and with it the claim that the pair-specific residual is *signed* — the one signature reliability heterogeneity cannot fake, since attenuation moves agreement toward zero and stops there | The statistic does not implement that reasoning. Mean raw agreement is **+0.2513**, so a pair with *zero* competence sits 0.25 below the mean and has a strongly negative **centred** residual **while never once disagreeing**. r26 scored "below average" and "actually anti-correlated" with the same number — and those are exactly the two worlds it existed to separate | Nothing. Re-asked on the raw scale by r27, where zero is a real boundary rather than a consequence of centring |
| 28 | **That the sign test had returned an answer at all** | It returned **+1.40, +2.26, +2.68 and +10.26** on identical data, varying only with how many random half-splits were averaged and whether the null used the same number. Four answers to one question | The diagnosis: that is a reading of the estimator, not a measurement. [r26](rounds/r26_sign_no_split) removes the split entirely and works on each pair's full residual series |
| 29 | **r27's actor control** — "the negative tail vanishes among pairs of two generally-agreeable raters, so it is an actor effect, not blocs" | Two defects. **(a)** A pair's own agreement feeds both members' actor scores, so selecting *both above median* selects directly on the outcome; fixed leave-one-out, which moved it only 0.20×→0.24×. **(b)** Fatal: under **unequal** bloc sizes a majority-bloc member agrees with most people and is therefore "agreeable" **by construction**, so both-high pairs are mostly *same-bloc* and the control could not have found blocs even if they were there | The observation (far tail at 0.24× the null among agreeable pairs, z=−10.00), not the inference |
| 30 | **r27's verdict**, which printed `VALUE BLOCS` | Its own control, ten lines above it in the same output, saying the opposite. The verdict block ranked thresholds and never read the control | Nothing. **This is item 11 on the step-size checklist in my own skill file — *a script's own conclusion string saying what you wanted to hear* — committed inside the round written to avoid exactly that.** The verdict now consults the control and cannot outrank it |
| 31 | **The additive decomposition itself**, and with it the residual r23, r25, r26 and r27 all read as "pair-specific structure" | Classical test theory. Under one latent target with heterogeneous reliability, agreement is a **product**: `A_ij = ρ_i ρ_j`. Fit `μ + a_i + a_j` to that and the residual is **not noise** — it is `(ρ_i−m)(ρ_j−m)`: positive when both raters are above average, positive when both are below, negative when they straddle. **A U-shape, generated entirely by the wrong functional form, with no blocs anywhere in the process.** r27 measured that U-shape (+0.0538 / −0.0567 / +0.0552) and I read the positive both-low arm as a minority bloc | [r28](rounds/r28_multiplicative) fits both forms on the same 6,193 dyads. Multiplicative wins **with one fewer parameter** (R² 0.6604 vs 0.5784). Under it `both_high` and `mixed` collapse to **exactly zero** (z=−0.73, −1.43) and one stratum survives: `both_low` **+0.0125 [+0.0004, +0.0241], z=+2.50**, replicated at +0.0208 (spearman) and +0.0122 (cosine). **A minority bloc is real and 4.4× smaller than the additive analysis implied** |
| 32 | **r28's own model comparison on the fourth metric** | negative-mean-absolute-difference is bounded *above* by zero, so a rank-1 product of real factors cannot represent it; ALS diverged to **R² = −13.14**. My code compared that to 0.5717 and printed *"the ADDITIVE form fits better"* — which would have entered the record as one metric of four dissenting, **manufacturing a robustness caveat out of a numerical failure** | A guard: R² < 0 now reports `MULTIPLICATIVE_INAPPLICABLE` and states explicitly that the additive form is **not** thereby supported. Attacked; it fires and returns before touching the strata |

**Why entry 31 is the most serious thing in this file.** Every other retraction is a
statistical error — a wrong null, an unmatched pairing, a missing interval, a check that
could not fail. Careful practice catches those. Entry 31 is the **model of the object**
being wrong: four rounds asked a well-posed question, with correct nulls and honest
intervals, about the residual of a functional form that *generates the effect they were
measuring*. No amount of rigour about sampling units or multiplicity would have found
it. Only asking **what produces agreement in the first place** does.

### Scoring the pre-registration

The brief bet on which claims would fall. Its own stated purpose: *"if a challenger
overturns something from the safe column, my sense of my own work is worse calibrated
than I think — and that is the more useful result."*

| | Predicted | Outcome |
|---|---|---|
| **A1** blocs | falls | **fell**, by the exact attack named (demographic strata) |
| **A2** r05 compression | falls | **held** under a different lexical instrument |
| **A3** r07 lexicon | falls | **fell**, harder — hits are not merely noisy, several are *reversed* |
| **A4/A5** judge, gold model | falls | untested — GPU was withheld from the challengers |
| **B1** r01 persistence | safest | **hit twice**: interpretation overturned, and one of its three controls was algebra |
| **B2** singleton arithmetic | safe | **exact**, on an independent from-scratch recount |
| **B3** two-regime step | safe | **UNVERIFIED** — no code existed — then confirmed by r24 |
| **B4** r19 span 2.47× | safe | **exact**, twice — while the README quoted 2.2× |

**Two of four "safest" claims went down; two of three testable "likely to fall" fell.**
Calibration on the risky column was good and on the safe column was bad, which is the
worse of the two ways to be wrong: the claims I defended hardest were the ones I had
stopped attacking.

---

## The pattern

Entries 1–12 were one failure. Entries 13–24 are **two**, and the second is new.

### First: a number reported without the scope over which it holds

Eleven of the first twelve, and 14 · 18 · 19 · 20 · 21 · 22 of the second batch. It is
the failure this repository's North Star names:

> **a number was reported without the scope over which it holds.**

- an uncertainty compared against a differently-paired uncertainty (1)
- a lexicon whose match rule was not the concept (2)
- a gold model whose backbone was shared with the thing it judged (4)
- a claim whose test was not its statement (5)
- a mechanism attributed to a datum that did not require it (6)
- a manifest that could not tell *unmeasured* from *unfindable* (7)
- a metric that assumed an output format the claim did not (9)
- an accuracy averaged over cases where nothing had to be decided (10)
- a floor treated as measured when it was chosen (11, 12)

The exception is 3 — a prediction that was simply wrong.

### Second: an instrument that could not have returned the other answer

This class does not appear once in entries 1–12. It appears **four times** in 13–24,
and it is worse, because a claim with a missing scope is at least *measuring* something:

- **a control invariant by construction** (13) — Pearson cannot see a per-rater
  rescaling, so the control could only ever return "survived"
- **a check whose threshold is unreachable** (16) — a proportion claim tested as a raw
  difference against 0.5, on a quantity bounded far below it
- **a null that shares the observed statistic's selection advantage** (19) — a
  free-breakpoint step compared against a fixed-form line
- **a permutation null that destroys two things at once** (14) — r01 shuffled rater
  IDs, killing actor identity and dyad identity together, so an actor effect had
  nowhere to land except the "structure" column

- **a statistic that scores both worlds identically** (27) — a centred residual cannot
  tell "below average" from "actually disagreeing" when the mean is +0.25
- **a control confounded by the thing it controls for** (29) — under unequal blocs, a
  majority member is "agreeable" by construction
- **a conclusion string that never reads its own control** (30)
- **a model comparison against a diverged optimiser** (32)

The diagnostic is one question, and it costs nothing: **name the world in which this
check returns the other answer.** If you cannot, you have not built a check. Three of
the first four were invisible to twenty rounds of my own review and took an outsider, or
a three-line piece of algebra, to see. The four added on the same day were found only
because the adversary round had already made me look — and every one of them was
committed *after* I wrote the checklist naming its own failure mode.

## What this costs and what it buys

Of the first twelve, **seven were caught by a later round of my own**. Of the next
twelve, **nine were caught by outsiders in about forty-five minutes each** — against
roughly twenty rounds of self-review that had already passed over every one of them.

That ratio is the finding. Not because the challengers were better, but because they
were **elsewhere**: a reviewer sampled from the process that produced the material can
only attack what that process already anticipated, which is exactly why those parts
read as fluent. The three defects I found myself in this round (13, and the design
weaknesses repaired in r23 and r24) all came *after* reading someone else's attack —
the outsider did not have to name them, only to point near them.

**The expensive part of this project was never any experiment. It was noticing which
number had not been asked where it stops being true — and that turned out to be a
thing I cannot reliably do to my own work.**
