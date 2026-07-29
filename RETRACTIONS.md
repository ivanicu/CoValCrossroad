# Retractions

Every claim this repository made and then killed, scoped or corrected — in the order
it happened, with what did the killing.

The rounds are numbered by when they ran, not by what survived. Read in that order
the repository looks like a sequence of findings. It is not. **Eleven of these
forty-seven entries are a later round destroying an earlier round's conclusion, and in
all eleven both rounds are mine.** Nine more were found by outside challengers in
roughly 45 minutes each, against twenty rounds of self-review that had already passed
over every one of them.

This file exists because the git log has all of it and nobody reads a git log.

**Reading order matters.** Entries 1–12 are one failure mode; 13–26 add a second;
27–32 add a third that neither of the first two can warn you about; 33–35 are the
largest untested assumption finally being tested, and the answer widening the headline
rather than confirming it; **36–40 are a fourth, found by reading OpenAI's protocol
documentation rather than by running anything** — five measurements named for what they
were meant to capture instead of what they compute; **41 is the round written to fix four
rounds, audited eight hours later, and substantially withdrawn.** Where a later
entry supersedes an earlier one the earlier text is **annotated, never rewritten** —
a ledger that edits its own history is the thing it exists to prevent.

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
| 14 | **r01's ρ=0.147 as evidence for structured plurality (M2)**, the premise the whole r16/r17/r18 arm is built on | Statistics review, then [r23](rounds/r23_actor_vs_dyad). Agreement persists with **no blocs at all** if raters merely differ in reliability — a careful rater agrees with everyone. That is an additive **actor** effect, and r01's null (shuffling rater IDs) destroys actor and dyad identity together, so it had nowhere to land but "structure". Fitting `A_ij = μ + a_i + a_j` per prompt: the actor model takes **47.2%** of dyad variance and actor-only persistence is **0.254** — *higher than the headline itself* | Only the residual: pair-specific ρ=**0.034**, z=**+4.67** against a dyad-permutation null. Real, and **20–23% of what r01 reported**. The sharper test — an excess of pairs reliably negative in *both* halves, which reliability heterogeneity cannot produce because noise attenuates toward zero and never below it — **returns null at z=+1.40**. So the residual is equally consistent with unequal-size blocs and with a second axis of rater competence. **M2 is weakened, not rescued** — ⚠ **and this whole cell is superseded by [31](#the-pluralism-question--five-separators-four-of-them-mine-and-wrong): the additive model it rests on is the wrong functional form, and the `z=+1.40` sign test could not have separated those two worlds in either direction.** Kept as written because the ledger annotates and does not rewrite |
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
| 29 | **r27's actor control** — "the negative tail vanishes among pairs of two generally-agreeable raters, so it is an actor effect, not blocs" | Two defects. **(a)** A pair's own agreement feeds both members' actor scores, so selecting *both above median* selects directly on the outcome; fixed leave-one-out, which moved it only 0.20×→0.24×. **(b)** Fatal: under **unequal** bloc sizes a majority-bloc member agrees with most people and is therefore "agreeable" **by construction**, so both-high pairs are mostly *same-bloc* and the control could not have found blocs even if they were there | The observation (far tail at 0.24× the null among agreeable pairs, z=−7.72 — **the −10.00 first published here was computed against a null estimated from 15 replicates; at 200 it is 23% smaller**), not the inference |
| 30 | **r27's verdict**, which printed `VALUE BLOCS` | Its own control, ten lines above it in the same output, saying the opposite. The verdict block ranked thresholds and never read the control | Nothing. **This is item 11 on the step-size checklist in my own skill file — *a script's own conclusion string saying what you wanted to hear* — committed inside the round written to avoid exactly that.** The verdict now consults the control and cannot outrank it |
| 31 | **The additive decomposition itself**, and with it the residual r23, r25, r26 and r27 all read as "pair-specific structure" | Classical test theory. Under one latent target with heterogeneous reliability, agreement is a **product**: `A_ij = ρ_i ρ_j`. Fit `μ + a_i + a_j` to that and the residual is **not noise** — it is `(ρ_i−m)(ρ_j−m)`: positive when both raters are above average, positive when both are below, negative when they straddle. **A U-shape, generated entirely by the wrong functional form, with no blocs anywhere in the process.** r27 measured that U-shape (+0.0538 / −0.0567 / +0.0552) and I read the positive both-low arm as a minority bloc | [r28](rounds/r28_multiplicative) fits both forms on the same 6,193 dyads. Multiplicative wins **with one fewer parameter** (R² 0.6604 vs 0.5784). Under it `both_high` and `mixed` collapse to **exactly zero** (z=−0.73, −1.43) and one stratum survives: `both_low` **+0.0125 [+0.0004, +0.0241], z=+2.50**, replicated at +0.0208 (spearman) and +0.0122 (cosine). **A minority bloc is real and 4.4× smaller than the additive analysis implied** |
| 32 | **r28's own model comparison on the fourth metric** | negative-mean-absolute-difference is bounded *above* by zero, so a rank-1 product of real factors cannot represent it; ALS diverged to **R² = −13.14**. My code compared that to 0.5717 and printed *"the ADDITIVE form fits better"* — which would have entered the record as one metric of four dissenting, **manufacturing a robustness caveat out of a numerical failure** | A guard: R² < 0 now reports `MULTIPLICATIVE_INAPPLICABLE` and states explicitly that the additive form is **not** thereby supported. Attacked; it fires and returns before touching the strata |

---

## The cross-family question — a false claim, then a false acquittal, then an answer

| # | The claim | What killed or scoped it | What survived |
|---|---|---|---|
| 33 | **"SURVIVES A CHANGE OF FAMILY"** — r22's first verdict, on the project's single largest untested assumption: every judge had been Qwen | Reading which judges it meant. Both were Qwen. `fams = {k.split("-")[0] for k in usable}` turns `"qwen3.5-2b-base"` and `"qwen2.5-3b-instruct"` into two different **strings**, so one lineage counted as two families — and the gate checked `len(usable) >= 2`, never that the families differed | Nothing. Family is now **declared**, never inferred from a nickname, and the gate counts distinct families. A single-family outcome gets its own verdict that says the round *has not tested the thing its title names* |
| 34 | **`phi-3.5-mini: positive_control_passed = False`**, own accuracy 0.0000 — recorded as a fact about phi | One line in `covalx/judge.py`. `yes_id, no_id = tok.encode(" Yes")[0], tok.encode(" No")[0]` is right for BPE (`[7179]` vs `[2233]`) and wrong for SentencePiece, which emits the whitespace as its own token: phi gives `[29871, 3869]` and `[29871, 1939]`, **so both ids were 29871 and the logit gap was identically zero.** Every score was exactly 0.5, every response tied, accuracy 0.0000 **by construction** | phi passes its control at **0.6410**, level with both Qwen judges. **The zero was not a wrong number, it was a mislabelled one** — and the question it silently closed was the only one this project had never answered. A judge emitting constant output has not failed a control, it has not been measured; r22 now detects sd < 1e-6 and files it as `DEGENERATE_OUTPUT_HARNESS_FAILURE` |
| 35 | **"27%–67%"** as the prompt-specific share, with the floor named as its only degree of freedom | r22, once phi could be scored. phi's *unrelated-rubric* floor is **0.6053** against Qwen's 0.5759/0.5767 — it earns more generic response quality for free — so the share runs **25.3% (phi) to 53.8% (qwen2.5-3b) at a fixed floor, a 2.13× span**, independent of r19's 2.47× across floors | The direction: attribution is positive on **both** families with intervals clear of zero, so the decomposition is not a Qwen artifact. Not the magnitude. Observed cells span **13.6%** (phi, near floor) to **~74%** (qwen, far floor) — **≈5.4×**. The quantity is a property of *(dataset, floor donor, judge family)*, and the last two are analyst choices the source package never reports |

---

## External methodological review — 2026-07-28, entries 36–40

A reviewer read the whole repository against the CoVal protocol documentation and the
dataset card, rather than against its own code, and named five claims the evidence does
not support. **Four of the five were established by reading OpenAI's documentation — not
by running anything.** That is a different failure surface from every earlier entry here:
not a bad null or an unmatched pairing, but *not having read the protocol that produced
the data*.

| # | The claim | What killed or scoped it | What survived |
|---|---|---|---|
| 36 | **"validated against 80,542 held-out human pairs"** — r04, and the word "held-out" throughout | The pairs are **pairwise decompositions of the same rankings**: same prompts, same four candidates, and the criteria were written *by those participants after ranking those candidates*. Holding out individual pairs does not break that path. **OpenAI ran a separate validation study with new raters and new completions precisely because the original rankings are unsuitable for out-of-sample rubric validity** | The number, under its real name: **internal reconstructive concordance on the elicitation manifold**, 0.686. That is substantial and it is endogenous. The round's title changes; the measurement does not |
| 37 | **"the advantage inverts on fresh responses"** — r12, the repository's most-cited anomaly | There are **no human rankings on the fresh responses**, and cannot be without new collection. The yardstick is a head fitted on human rankings of the *original* responses. So the object measured is **rubric-vs-proxy disagreement under response-distribution shift**, not inversion of human preference. The discrimination control shows the proxy is more *discriminative* there — it does not show it is *correct*. **Variance is not calibration** | The datum, replicated on a fresh sample: **−0.058 [−0.085, −0.031]**. And its status as the project's highest-value open question. **Human rankings on the exact saved fresh responses now outrank every remaining computational round** |
| 38 | **"response-set knowledge is not the mechanism"** — r13 | It rules out only the narrowest channel, literal memorisation of candidate *strings*. Three survive: a **shared viewpoint generator** (candidates were produced from generated viewpoints; nothing establishes the seeds were independent of that scaffold), the **prompt-construction manifold** (prompts synthesised for specific Model-Spec tensions, candidates instantiating them), and **post-choice selection into core** (LM synthesis of *highly rated* criteria, so which response-blind sentences survive is decided post-response) | The narrow claim, plus one channel genuinely closed and now stated: **r13's estimator uses an unweighted mean of judge satisfaction and no human rating sign or magnitude anywhere**, so post-choice *weighting* cannot enter this particular number. The reviewer also **corrected me in my own favour**: the release states write-ins were never shown to others, so singletons *are* write-ins by protocol, and the provenance proxy is firmer than I had scoped it |
| 39 | **"effort steps −38.6% at task 6 — a regime change"** — r02, defended by r24 | `DATASET_CARD.md:81`: *"a minimum of 5 tasks and up to 20 per session"*. **The breakpoint is the study's continuation boundary.** Positions 1–5 hold everyone who started; 6 holds only those who continued. And r24's null shuffles positions globally, which **destroys the censoring process that creates the confound** — it could not have detected this | [r31](rounds/r31_within_person) runs the repair. On the **933 people present at both**, the paired drop is **−179.2 chars [−196.2, −162.3], −53.3%**, against **6.1% attrition**; between-person is −53.2%, essentially identical. **Composition is excluded.** But the mechanism is not: with sessions of 5 or 15 prompts and **no session identifier or timestamp anywhere in the release** (verified — the only assessment fields are annotator_id, conversation_id, importance, ranking_blocks, representativeness, subjectivity), position 6 is the **first task of a later session** for anyone whose first batch held five. Within-session fatigue and between-session habituation are **not separable from this data** |
| 40 | **"the rubric is blind to anthropomorphism"** — r07 | Three overreaches at once. **Construct**: the effect is carried by `user_directed_warmth`, and warmth is not anthropomorphism — claims of subjective experience, agency, relational reciprocity and identity confusion are all distinct and untested. **Causal**: a positive residual after controlling for rubric score and length can arise from omitted response quality, safety posture, specificity or discourse structure. **Outcome**: it measures immediate *preference*, not *impacts* — trust calibration, reliance, disclosure, attachment | A **residual association**: a marker retains t=+4.02 after controlling for rubric score and length, while 0.046% of criteria address the construct. Excellent motivation for a randomised warmth × agency-claim experiment. Not its conclusion |

**The pattern in these five.** Every one is the same error in a new place: **a measurement
was named for the thing it was meant to capture rather than the thing it computes.**
"Held-out" for pairs that share every causal path with the training data. "Inversion of
preference" for disagreement with a proxy. "Not the mechanism" for one of four channels.
"Regime change" for a discontinuity at a design boundary. "Blind to anthropomorphism" for
a residual on a warmth marker. The instruments were fine. **The names were claims, and
nobody checked them against the protocol that produced the data.**

---

## Entry 41 — the round written to fix four rounds, audited eight hours later

An adversary was given a frozen clone of **the seven rounds written that same day**, none
of which any outsider had seen. It was handed the two attacks I most expected to land and
found both — plus one I had not thought to ask for, which is the one that inverted the
conclusion.

| # | The claim | What killed or scoped it | What survived |
|---|---|---|---|
| 41 | **Entry 31's headline** — "agreement is multiplicative, the multiplicative form fits better *with one fewer parameter*, and a minority bloc survives at +0.0125, z=+2.50" | Three independent defects, each verified here rather than taken on report. **(a) The parameter claim is arithmetically false.** The additive design has 925 columns and numerical rank **924**: `μ → μ−2t` with `a_i → a_i+t` leaves every fitted value unchanged, and `‖X·(that direction)‖ = 0.000e+00` exactly. Effective dof are **equal** — and that sentence was the one written specifically to pre-empt *"it's just the bigger model"*. **(b) The reported z came from a non-deterministic pipeline.** `u, v = tuple(pair)` on a `frozenset` makes rater→row assignment depend on `PYTHONHASHSEED`, and `fit_rank1` is coordinate descent over row index. The adversary measured z ranging **2.2177–2.4409** across five seeds; I had committed **2.5049**, the top of the spread. Deterministic value after `sorted(pair)`: **2.1226**. **(c) It does not generalise.** Over ten held-out splits the multiplicative R² spans **[−1.64, +0.51]** against the additive shape's tight **[+0.34, +0.42]**; ~1 split in 10 collapses when thin raters get a `c_i` pinned to the `0.1` initialisation fallback — **a silent imputation**. In-sample fit was never the test | **The algebra only.** Fitting `μ + a_i + a_j` to a product genuinely leaves residual `(ρ_i−m)(ρ_j−m)` — positive at both extremes, negative in the middle — so the additive decomposition r23/r25/r26/r27 relied on **is** misspecifiable, and r27's U-shape **is** what that produces. **But the multiplicative alternative is not thereby established, so the question those four rounds existed to settle is OPEN.** C4 is withdrawn; C15 rewritten to test held-out prediction and now **FAILS** at 0.2514 against 0.3879 |

**Three things worth keeping from how this one went.**

**The round's own stability check could not fire.** It cross-validated on three splits, and
seeds 1–3 all land on well-behaved masks. A guard that samples too little to observe the
failure it guards against is the same defect as a threshold that cannot be reached — it is
now ten splits, and the catastrophic mode appears.

**My first replication of the adversary's finding contradicted it.** Three splits gave
multiplicative R² of 0.487/0.499/0.458 — all positive, all beating additive. Only at ten
splits did split 5 return **−1.64**. Had I stopped at three, I would have filed their
finding as unreproducible and been wrong, with a clean-looking run to point at.

**The script looked reproducible, which is why nobody checked.** It sets
`np.random.default_rng(20260728)` at the top. A visible seed on the wrong source of
randomness is worse than no seed, because it answers the question before it is asked.

---

## Entry 42 — the smoke-run habit, caught by auditing instead of by an adversary

| # | The claim | What killed or scoped it | What survived |
|---|---|---|---|
| 42 | **"Every rung is non-significant"** (C36/r37) and **"φ_T gap spans zero"** (C35/r36) | Auditing whether each committed result was its *full* run. Both were published from **smoke runs** — 2 seeds where the design called for 8 and 5 — launched in the background while the smoke numbers went into the README. The full runs finished afterward and **both calls flip**: r37's `A2` held-out-rater-folds rung is **+0.0026 [+0.0004, +0.0049]**, and r36's `φ_T` gap is **+0.0017 [+0.0005, +0.0028]**. Neither interval contains zero | The direction and the magnitudes, which barely moved. What did not survive is the *significance* language, and the correct C36 statement is now narrower: **one rung is significant** — a small-sample group-fitting effect of about 0.4% — while individual circularity and population dependence remain absent, and held-out **country** costs *less* than held-out rater folds |

**This is [entry 41's](#) failure repeating in the opposite direction.** There, a 2-null-rep
smoke read `z=+10.26` where 40 reps read `+1.40` — the smoke **overstated**. Here the smoke
runs had *wider* intervals and **understated**, so three claims were published as null that
are not. Both directions have the same cause: **a smoke run is a number whose uncertainty is
wrong, and its point estimate being close is exactly what makes it dangerous.**

Worth noting how it was found. No adversary this time — it came from asking one question of
the repository's own artifacts: *is every committed result the full run its design specifies?*
That check costs nothing and had never been run.

---

## Entries 43–47 — the framing itself, and four claims scoped to what was actually tested

A second methodological review reframed the research object. The project had been asking *what
fraction of a rubric's accuracy is values*; the object is really **a scoped, compiled,
context-indexed normative measurement program** `M(R, J, π, Q, P)` whose layers do not preserve
one invariant. Four claims and one framing were rescoped as a result.

| # | The claim | What killed or scoped it | What survived |
|---|---|---|---|
| 43 | **"Less than half of a values evaluation measures values"** — the framing this project was named for | The contrast is `own-rubric performance − SELECTED reference-rubric performance`. It is not `values − non-values`. Whatever an unrelated prompt's rubric recovers is itself made of accuracy, clarity, caution, non-deception, relevance, proportionality — **norms, not the absence of them** | The subtraction, under its real name: **source specificity**, or incremental prompt-conditioned information. Every number stands; the name never did. The framing is retired, not corrected |
| 44 | **"Not same-sample leakage"** (C16) | It excludes the *individual* loop only. **Every participant saw the same four-response menu**, so `menu → shared salience → Sᵢ` produces directions that agree across raters *and* are still menu-constructed. Cross-rater agreement is evidence against individual circularity and **is not evidence for a pre-existing norm** | *Not primarily same-**rater** circularity* — which is what C33/C36 actually measured. Shared-menu endogeneity is untouched, and no split of these annotators can touch it |
| 45 | **"Not a forced-choice artifact"** (C18) | Dropping low-consensus criteria **after collection** cannot simulate what a participant would have written had *"no general direction"* or *"depends on implementation"* been on the screen. Elicitation format changes the response it elicits, and that is not recoverable by filtering the responses it already produced | *Robust to **post-hoc** criterion abstention* — dropping 54% of criteria costs under one point. The real test needs the option **at elicitation time** |
| 46 | **"Not population-conditional"** (C19) | **`p > 0.05` is not equivalence.** Six countries is silence about anything smaller than the design can see, and aggregate accuracy conceals criterion-level **sign reversals**, minority-only criteria, and groups choosing alike *for different reasons* | *No aggregate loss detected in the splits tested* — a non-rejection. Invariance needs an equivalence test against a declared margin and a criterion-level heterogeneity model, neither run |
| 47 | **"r12's inversion is not an OOD artifact"** (C20) | The three metrics tested are **generic** — hidden-state geometry and likelihood. A fresh response can be close in embedding, style, length *and* likelihood while combining criterion satisfactions **no original candidate exhibited**. That is a normative-support shift and generic distance cannot see it | *Not explained by monotone degradation under the tested generic distances.* Silent on judge accuracy on fresh, proxy validity on fresh, and rubric-conditioned support — the last being the distance a rubric failure would actually live in |

**The pattern, which is the same one as entries 36–40 one level up.** Each of these four was a
measurement named for the *hypothesis it was aimed at* rather than the *contrast it computed*.
"Not leakage" for a test of one leakage path. "Not a forced-choice artifact" for a filter applied
afterwards. "Not population-conditional" for a non-rejection. "Not an OOD artifact" for three
generic distances. **The numbers were right in every case. The nouns were the claims.**

Also retired: describing CoVal-core as **laundering** polarity. It imputes intent. The accurate
statement is that core **internalises polarity into rewritten criterion semantics while
discarding most of the original rating and disagreement provenance** — an artifact-design
consequence, not a deception. And the 76% figure is **not decomposed**: rewrite, merge, dedup,
compatibility-selection and truncation are confounded inside it.

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

## Entry 48 — a control is a claim about what does not matter, and I never tested it

**What was published.** r41 concluded that criterion space does not explain r12: every
novelty measure died, and the two that had looked significant — hull violation −0.1837
and rank instability +0.1993 — dissolved once I partialled out the rubric's own score
spread. The round was written up as a negative result whose value was closing a door.

**What was wrong.** The variable I partialled out is not a nuisance imported from
outside the question. *"The rubric separates the fresh responses less than it separated
the originals"* is itself a criterion-space property — arguably the most basic one. I
introduced it as a control, used it to kill two measures, printed its correlation with
the drop as a bare **−0.2246** with no confidence interval, no permutation test and no
length control, and then described the round as finding nothing.

Given the same scrutiny as the measures it killed:

| | |
|---|---:|
| spread loss → drop | **+0.2246** [+0.098, +0.344], p = 0.0007 |
| length-controlled | **+0.2309** [+0.108, +0.341], p = 0.0010 |
| correlation with generic embedding distance | **−0.056** |

It is the **largest effect in the round**, and it is nearly orthogonal to the distance
r40 measured — which is precisely the gap r41 existed to fill.

**The control it demanded, run before publishing it.** A rubric that stops separating
responses scores nearer chance, so its accuracy falls — but the attribution *subtracts*
a donor rubric scored on the same responses, and if both arms degraded together the
difference would not move. Both arms had been persisted:

| | |
|---|---:|
| corr(own spread loss, donor spread loss) | +0.4509 |
| **donor** spread loss → drop | −0.0351, p = 0.586 |
| **own** spread loss → drop, donor partialled out | **+0.2693** [+0.154, +0.380], p = 0.0002 |

They move together and only the own-rubric arm predicts the drop. Not mechanical.

**STATUS UPDATED 2026-07-28: NOT REPLICATED — the claimed magnitude is withdrawn.**
⚠ *Sharpened again after r57/entry 55:* "single-sample artifact" was itself too strong. The
held-out estimate, corrected for the outcome's measured reliability, is **+0.076 [−0.105, +0.260]**
— which excludes the discovery magnitude but is consistent with a *moderate* real effect. What
failed is the preregistered size, not the existence of any effect. The distinction matters because
the two licence different next steps.

r46 committed a numeric prediction to git (`ecf3576`), then tested the effect on 250 prompts
nothing in this project had touched. Predicted `r ∈ [+0.12, +0.34]` with the CI excluding zero;
observed **+0.0496 [−0.068, +0.169]**, p = 0.44. That is the declared NOT REPLICATED branch.

The controls passed, so this is a clean negative rather than a broken run — and **r12's own
phenomenon replicated**: own-rubric advantage +0.0847 on the held-out originals (r12: +0.102) and
−0.0716 on fresh (r12: −0.064).

**What made it look solid.** Four checks agreed with it — the donor-arm control, a second judge
lineage (phi, +0.1724), and two rubric-independent heterogeneity measures showing the fresh
responses were *more* varied rather than less. **All four ran on the same 250 prompts.** Each
varied the instrument, the control, or the alternative explanation; none varied the sample. I
treated them as accumulating evidence, and they were four views of one correlation. **Robustness
to the instrument is not generalisation across samples**, and nothing in the checklist said so.

*Original status, kept for the record:*
**EXPLORATORY, and labelled so everywhere it appears** — in the generated
verdict, in the README, and in a post-hoc addendum appended to the claim card. The card
preregistered *novelty*; novelty is refuted and this does not rescue it. A post-hoc
measure with a good p-value and no stated provenance reads exactly like a prediction,
and that is the failure this register exists for.

**The general lesson, which is new here.** Every earlier entry is a claim asserted
beyond its evidence. This one is the opposite shape: **a claim asserted by omission.**
Choosing a control is asserting that the controlled variable does not carry the effect
— a substantive claim, made silently, tested never. Nothing in the checklist covered
it, because the checklist was built to catch numbers that say too much, and a control
says nothing at all.

**How it was caught.** Not by an outsider. The ordered queue had emptied, and the only
work left was attacking this session's own results — which is the one condition under
which I have historically found my own defects: when there was nothing else to do
except look.

## Entry 49 — a magnitude quoted without asking what the sample size does by itself

**What was reported** (to the user, in a turn summary, before any file said it): that r08's
gold head "orders responses by length at |r| ≈ 0.6–0.7 **in both sets**", offered as evidence
that the project's outcome variable is substantially a length detector everywhere.

**What was wrong.** Each prompt has **four** responses. Two *independent* 4-vectors already
correlate at

```
E|r| = 0.5005          (200,000 draws, n = 4)
```

So the observed magnitudes are excesses of **+0.115** (original) and **+0.191** (fresh), not
0.616 and 0.691. **The "in both sets" half of the sentence was the null.** The magnitude on the
original candidates — the one that made the claim sound general — is barely above what four
arbitrary points produce.

**What survives, and it was always the part doing the work.** The *signed* correlation moves
**+0.0770 → +0.4579** between released candidates and generated responses, and the signed null
is 0 by symmetry. The shift is real and large; the magnitude was mostly sample size.

**Why it happened.** I reached for |r| because the signed mean on the originals (+0.077) looked
too small to matter, and I wanted a statistic that would show the channel was present anyway.
That is the shape of the error: **a magnitude was recruited to rescue a signed result**, and the
thing recruited had a floor I never checked.

**Class.** Same family as the "fancy invariant vs trivial scalar" entries, but the trivial
scalar here is not intrinsic dimension or variance — it is **n**. Sample size is the most
trivial confound available and the easiest to skip, because it does not look like a variable.

**Fixed.** r47 computes the null for its own n and prints the **excess** beside every raw
magnitude, so the bare number cannot be quoted again.

**Caught by:** noticing that the human win-rate showed |r| = 0.5733 against length while its
signed correlation was +0.041 with a CI spanning zero. Two quantities that disagree that badly
about the same relationship meant one of them was not measuring it.

## Entry 50 — the anomaly that drove four rounds was partly a property of the outcome variable

**What was published.** r12's inversion — that on generated responses the own rubric scores
*below* an unrelated one, attribution −0.064 — reported as the project's most robust unexplained
result, replicated on held-out prompts by r46 at −0.072, and chased by r40, r41 and r46 in turn.

**What was missed.** All three of those rounds tested a property of the **rubric**. Every one held
the **outcome variable** fixed, and the outcome is agreement with r08's gold head — which is
`hstack([embedding, [char_len, word_len]]) @ w`, with length as an explicit input at |w| = 0.2085
against a mean embedding weight of 0.0620. Generated responses vary 3.4× more in length than the
released candidates, and gold's within-prompt correlation with length rises from **+0.077 → +0.458**
(discovery) and **+0.026 → +0.548** (held out).

**What changes.** Measured against the procedure's own null, ~57% of the inversion survives
length-residualisation. More importantly, the **sharpest** part does not replicate:

| fresh arm, length-residualised | discovery | held out |
|---|---:|---:|
| | −0.0307 [−0.0567, −0.0053] | **+0.0047 [−0.0213, +0.0320]** |

On held-out prompts the fresh arm stops being negative. So **"an unrelated rubric beats the own
rubric on generated responses" is withdrawn** — it is not established. What survives, on both
samples, is the ordinary claim that **the advantage does not transfer**.

**Why it took this long.** The strangeness of the result is what made it interesting, and the
strangeness was the part least supported. Four rounds searched the rubric for an explanation of a
number produced jointly by the rubric *and* the proxy, and nothing in the process rules asks
"is this a property of the outcome variable?" — they ask about construction data reaching
evaluation, about instruments, about populations. The outcome had been fixed since r08 and had
stopped looking like a choice.

**The proxy is not broken, which is what made it invisible.** On the original candidates — the
only arm with human rankings — gold and humans agree: +0.1020 vs +0.0876 and +0.0853 vs +0.0742,
both differences spanning zero, per-prompt r = +0.60 and +0.65. It is validated exactly where its
length channel is weakest and applied where it is strongest, and validating it on originals
licenses nothing about generated text.

**Consequence.** `PREREGISTRATION.md` now requires response length to be recorded for every
response in H_fresh and reported with every estimate.

## Entry 51 — five rounds silently analysed 36.5% of the criteria, and it is the shared 36.5%

**What was published.** C16–C19 and the README all state that the post-ranking criterion
direction "generalises across people" (+0.0576 cross-fitted, r34), that the decay across
isolation rungs is flat (r37), that abstention costs nothing (r35), that sign is the largest
Shapley channel (r36), and that group heterogeneity does not change which response wins (r43).

**What none of them said.** All five filter the criterion set the same way —
`rounds/r34_global_rater_crossfit/run.py:132`, `if len(sc) >= thr` — keeping only criteria rated
by a majority of the prompt's raters. That discards **9,684 of 15,248 criteria (63.5%)**.

r48 then established what that filter selects. The partition is structural (0.1% in the gap) and
the surviving class is capped at exactly six per prompt: it is the **pre-seeded** set, the
criteria OpenAI pre-populated and showed to *every* participant. The discarded 63.5% are the
**write-ins** — authored by one participant and rated by that participant alone.

**Why this sharpens the rescope rather than merely annotating it.** Item 1 rescoped "not leakage"
to leave shared-menu endogeneity open, on the grounds that every participant saw the same four
responses. The sharper statement is that r34's cross-rater agreement is agreement **about the same
six sentences everyone was shown**. The shared-criterion channel is not a residual worry in those
results — it is the entire population they were computed on.

**Direction of the error.** The filter is defensible: a criterion rated by one person has a sign
from a sample of one. But "we restricted to reliably-rated criteria" and "we restricted to the
criteria OpenAI supplied" are the same operation described two ways, and only the first was ever
said. Nobody chose to exclude participant-authored criteria; the rater-count threshold did it.

**Not yet established, and the reason this entry is not larger.** Whether the direction also
transfers on the private write-ins is a live question (r49). A first pass including them gave
**+0.0800** against r34's **+0.0576** — suggesting private criteria *add* to cross-rater transfer
rather than dilute it — but that arm was not r34's estimator in other respects, so it is a signal
to chase, not a result.

**How it was caught.** r49's positive control, which required a reimplementation to reproduce
r34's number before any per-class figure could be read. It refused, and the reason it refused was
the finding.

## Entry 52 — I claimed a universal about *designs*, and a design existed

**What was said**, in a turn report rather than in any artifact: that "shared-response artifact"
and "population property" *"make identical predictions in every design this release permits."*

That is a claim about the space of possible designs, asserted by the only person who would have
had to find the counterexample, one turn after being caught twice on exactly that pattern (S_pre's
unreachability, entry 51's population).

**A design exists.** Write-in criteria vary in how much they are *about* the four candidates —
*"invents a statute"* versus *"maintain a respectful tone"*. If the transferable direction were a
shared-response artifact it should concentrate in the response-anchored ones. r50 measures
anchoring as lexical containment of a criterion's content words in the best-matching response and
splits at the within-prompt median.

| | gap: anchored − generic |
|---|---:|
| write-ins | **+0.0271 [+0.0134, +0.0405]** |
| pre-seeded control | +0.0106 [−0.0008, +0.0226] |
| **excess (write-in − seeded)** | **+0.0141 [−0.0050, +0.0326]** |

So the design returns a signal: anchored write-in criteria carry more of the cross-rater direction
than generic ones. **What it cannot do is attribute it** — the seeded class shows the same
tendency and the excess spans zero.

**The error the round nearly published.** The first verdict branched on "seed gap significant?"
first, found it was not while the write-in gap was, and declared the effect specific to
participants — **difference of significance read as significance of difference**. The quantity that
actually separates the worlds is the excess, and it does not exclude zero. The branch order now
reads the excess first and nothing downstream can overrule it.

**Status.** The universal is **withdrawn as stated**: a design exists. The substantive separation
is **not achieved**: this one is underpowered to attribute its own signal, and its control is not
airtight either — the release never says how the seeded six were produced, so "not
participant-authored" does not establish "not response-derived."

**The class.** Entries 48, 50 and 51 are all claims that outran their evidence about *the world*.
This one outran its evidence about *what could be measured*, which is a claim I have less standing
to make than any other, because it is a claim about my own failure to think of something.

## Entry 53 — not a retraction: the instrument was never characterised, and now it is

This register holds claims that outran their evidence. This entry is the opposite shape and is
recorded here because it changes the scope of nearly every other one.

**What was never asked.** Every cross-rater result in this repository runs through one judge:
*"does response r satisfy criterion c?"*. r04 validated it in aggregate against held-out human
rankings — which establishes it predicts something, not what it reads. Across 51 rounds, nobody
asked what it was using. The instrument had been fixed since r04 and had stopped looking like a
choice, exactly as the gold head had (entry 50).

**What it is using, in part.** r51 measured the correlation: within a fixed (prompt, criterion),
satisfaction across the four responses tracks criterion↔response lexical overlap at **+0.2068**
(null −0.0034, +0.1886 with length partialled out). r52 then **intervened** — appending six
distinctive tokens from response A rather than B, to the *same* criterion, moves the A-vs-B
satisfaction gap by **+0.2507 [+0.2300, +0.2714]**, with an unrelated-token null of −0.0045.

**What this does and does not license.** It does not show the judge is *wrong*: overlap and
genuine satisfaction covary in the world, and the release has no satisfaction ground truth. It
does not measure behaviour on natural high-overlap criteria — the intervention perturbs the text,
so it **bounds** overlap-sensitivity rather than measuring it in situ. What it does establish is
that the satisfaction layer has a demonstrated surface-form channel of substantial size, and every
claim in this repository that passes through that layer inherits the fact.

**Why it belongs in this register.** Entries 49–52 are each a case of a quantity being trusted
because nobody had asked what it was made of — the n=4 null, the gold head's length feature, the
criterion population, the space of designs. This is the fifth, and the largest: the judge itself.
The common failure is not over-claiming from evidence. It is **not noticing that a fixed part of
the apparatus was ever a choice.**

## Entry 54 — the last fixed component, interrogated, and it was fine

Entry 53 named the failure behind 49–52: a fixed part of the apparatus stops looking like a
choice, and then nobody interrogates it. Having named it, the obligation is to finish the list
rather than to stop at the instances that happened to yield findings.

The remaining component was **the join**. `covalx.load_join` pairs every rubric to a comparison
record, and every round in the repository is built on that pairing. It has printed the same line
on each of 52 runs — `{'role_canonical': 966, 'fuzzy>=0.95': 2, 'unmatched': 18}` — and nobody
had asked what those numbers were.

The stakes were the highest available: a mispaired rubric means criteria scored against responses
they were never written for, in every downstream round, with no symptom.

**It is fine.**

- both fuzzy pairs differ by a typo and are plainly the same prompt (0.9896: *"should people stop
  eat beef"* vs *"stop eating beef"*; 0.9903: *"mrna vaccines?"* vs *"mrna vaccines???"*)
- the 18 unmatched rubrics are **not** excluded by the 0.95 cutoff. Their best available
  similarity to *any* released prompt has median **0.7727** and max **0.9364** — those prompts are
  absent from `comparisons.jsonl` rather than narrowly missed. Only one would be recovered even at
  0.90, and the threshold is therefore not what defines the analysed set

**What the audit produces instead of a defect** is the population statement, which entry 51 shows
is worth having explicit: **968 of 1,078 released prompts (89.8%)**, the shortfall being 92
prompts with no rubric record at all plus 18 rubrics whose prompts are not in the comparison file.

**Recorded because a negative audit is a result.** Four of the five components interrogated under
this pattern produced findings; this one did not, and reporting only the four would make the
pattern look more damning than the evidence supports. One borderline remains and is named in the
round's own verdict: the closest unmatched record sits at 0.9364, which a 0.90 cutoff would admit
and which nothing here proves is a different prompt.

## Entry 55 — "every mechanism failed" was half a claim about the mechanisms and half about an instrument I never checked

**What was said, repeatedly and to the user:** that r12's transfer failure "has defeated" generic
distance (r40), criterion-space novelty (r41), spread loss (r46), the length channel (r47),
lexical overlap (r54/r55) and semantic selectivity (r56) — and that this is "an argument for
H_fresh, not for a seventh mechanism."

**What was never checked.** Every one of those searched for a **per-prompt correlate** of the
attribution drop. That drop is a difference of two pairwise accuracies, each over the 6
comparisons among 4 responses, so each takes values in {0, ⅙, …, 1} and the difference inherits
both quantisations. Nobody asked how much of its per-prompt variation is signal.

**It is mostly not.** Split-half reliability (3 pairs vs 3, 200 random splits, Spearman-Brown to
full length), on both independent samples:

| | discovery | held out |
|---|---:|---:|
| reliability | **0.302** | **0.422** |
| attenuation √rel | 0.549 | 0.649 |
| a true 0.50 is observed at | 0.275 | 0.325 |
| a true 0.30 is observed at | 0.165 | 0.195 |
| smallest true r distinguishable from 0 at n=250 | **0.23** | **0.19** |

**So the six nulls do not say what I said they say.** They show no mechanism with a *true*
per-prompt correlation above roughly **0.2** explains r12. A moderate real mechanism — true
correlation 0.15, 0.20 — would have been invisible to every single one of them, and I would have
reported it as absent each time.

**What this does NOT rescue.** The two mechanisms that failed to **replicate** — entry 48's spread
loss and r56's semantic selectivity — failed against their own *preregistered* intervals. That is
a different and stronger kind of failure than being underpowered, and low reliability does not
undo it. Low reliability attenuates true effects; it does not manufacture a +0.23 on one sample
and a +0.05 on another.

**The class.** Entries 49–54 were each a fixed part of the apparatus that stopped looking like a
choice. This is the same failure applied to a **conclusion drawn across rounds**: six nulls were
aggregated into a claim about the world without anyone asking whether the shared outcome variable
could have detected the thing being ruled out. The aggregate was weaker than any of its parts
looked.

## Entry 56 — "six mechanisms failed" resolves into three different kinds of failure

Entry 55 established the outcome's reliability caps every per-prompt search. It stopped there,
leaving six results as undifferentiated nulls. Dividing each observed correlation by
√(outcome reliability) turns them into bounded statements — and they do not all say the same thing.

| round | mechanism | observed | disattenuated (lower bound) |
|---|---|---:|---:|
| r40 | generic NN distance | −0.125 | −0.228 |
| r41 | criterion-space NN | −0.083 [−0.188, +0.028] | −0.151 [−0.342, +0.051] |
| r41 | hull violation | −0.184 [−0.275, −0.082] | **−0.334 [−0.501, −0.149]** |
| r41 | rank instability | +0.199 [+0.065, +0.333] | **+0.363 [+0.119, +0.606]** |
| r41 | spread loss (discovery) | +0.231 [+0.105, +0.344] | **+0.420 [+0.192, +0.626]** |
| r46 | spread loss (HELD OUT) | +0.050 [−0.068, +0.169] | +0.076 [−0.105, +0.260] |
| r54 | mean lexical overlap collapse | −0.074 [−0.206, +0.061] | −0.134 [−0.375, +0.111] |
| r55 | lexical selectivity collapse | +0.007 [−0.122, +0.141] | +0.012 [−0.222, +0.257] |

Disattenuation divides by √reliability of the **outcome** only. The covariates' own reliabilities
are unmeasured, so every figure is a **lower bound** on the true correlation.

**The three kinds:**

**1. Conclusions resting on a tight DIRECT estimate — these hold.** r55's argument was never the
correlation; it was that lexical selectivity does not collapse *at all* (+0.0002, equivalent to
zero at δ = 0.01). A tightly-bounded quantity does not need the outcome to be reliable, because
nothing is being correlated. r47's length residualisation and r55's equivalence are in this class.

**2. Conclusions resting on an underpowered CORRELATION — much weaker than I reported.** r40,
r41's criterion-space NN, r54 and r56's held-out value all have disattenuated intervals spanning
from meaningfully negative to meaningfully positive. Calling these "ruled out" was wrong.
**⚠ r56's interval is itself UNVERIFIED (entry 101):** its code was never committed, its bounds
0.1592 and 0.2880 appear in no artifact, and [r66](rounds/r66_r56_reconstruction) could not
recompute them. Its *conclusion* survives an independent method; the *interval quoted here* has
no artifact behind it and should not be used as a measured quantity.

**3. Conclusions that failed a PREREGISTERED replication — the magnitude dies, the effect may
not.** Entry 48 and r56 both failed their declared intervals, which no amount of power correction
undoes. But "failed to replicate at the claimed size" is not "shown absent", and I had been
writing the second. Entry 48's status is corrected above.

**What this costs.** My repeated summary that "every computational mechanism has failed" was a
class-1 statement made about a set that is mostly class 2 and 3. The strongest honest version:
**no mechanism with a large true per-prompt correlation survives, two specific mechanisms failed
at their claimed magnitudes, and moderate effects are uniformly undetectable in this design.**

## Entry 57 — the assurance document truncated every claim at 110 characters, and the scope lives after character 110

**What happened.** `ASSURANCE.md` is the human-readable half of the assurance package — the
document an outsider opens. Its claim table rendered each statement as `statement[:110]…`.

Every scope clause added over the last several days sits **after** the headline sentence, by
construction: you state what was found, then what it does not establish. So:

| clause | in MANIFEST.json | in ASSURANCE.md |
|---|---|---|
| `NOT ESTABLISHED: …` (item 1's four rescopes) | yes | **0 occurrences** |
| `POPULATION (entry 51): …` | yes | **0 occurrences** |
| `DETECTION FLOOR: …` (entry 56) | yes | **0 occurrences** |

Item 1 was the queue's first and highest-priority task. Entry 51 was a repository-wide population
correction. Entry 56 was the power classification. **All three landed in the JSON and none of them
reached the page a reader reads.**

**Why it is the same failure as the container ones.** A cap that deletes from one end is not
neutral about *what* it deletes. Prose puts the claim first and the qualification second, so a
tail-truncating renderer removes qualifications specifically — it cannot remove headlines. The
truncation was there from the start and looked like formatting.

**Fixed.** The table now carries the first sentence only and is followed by every statement in
full, under a heading saying why. Verified by counting the clauses in the rendered file: 4
`NOT ESTABLISHED`, 8 `POPULATION (entry 51)`, 1 `DETECTION FLOOR`, and **0** remaining ellipses.

**What it says about the rescoping work.** Nine turns of scope corrections were being written into
a file whose reader-facing view could not display them. The corrections were real; their delivery
was not. Writing the caveat and shipping the caveat are different acts, and only the first was
ever checked.

**ADDENDUM — I then asserted "no other renderer truncates" without checking, and swept for it.**
That sentence went into the commit body one turn after this entry documented the failure mode.
The sweep found most `[:N]` slices are console output, which is transient and harmless, and two
that are not:

- `r53_join_audit` persisted the unmatched prompt text as `ck[:160]` into its results JSON — mine,
  from this session, fixed.
- `r21_donor_distance` cuts the **generation input** at 400 characters, which is data rather than
  display. **52 of 968 prompts (5.4%) exceed it**, up to 829 characters, so for those the
  paraphrase — the round's "known-related" anchor — is a paraphrase of a *fragment*. Direction of
  the bias: a fragment paraphrase is less similar to the full prompt, so the anchor is weaker and
  the distance scale it calibrates is compressed, which works *against* r21 finding transfer
  rather than for it. Left in place with the bound stated, because changing it would change
  published numbers.

Both are smaller than the ASSURANCE.md case. The point of recording them is that the assertion
came first and the check came second, which is the habit this entry exists to break.

## Entry 58 — a round answered a question the project later spent four rounds on, and nobody had ever mentioned it

**How it was found.** Entry 57 closed the delivery gap for the *generated* package. My commit body
conceded that hand-written surfaces "remain governed by review", which names a gap rather than
closing it. The crisp checkable part: **a round that ran, produced a verdict, and appears nowhere
in README.md is undelivered.** 55 rounds have a non-smoke result. One was invisible.

**`r29_gold_ood`.** It asked whether the gold preference head is unstable off-distribution — the
exact question r47, r54, r55 and entry 50 later circled — and answered it:

> GOLD IS STABLE OFF-DISTRIBUTION: two independently-fitted heads agree about as well on generated
> responses (0.590) as on released ones (0.543). **RELIABILITY only — the two heads share an
> architecture and an embedding model, so a bias common to both is invisible here.**

**The caveat was prescient and r47 is its answer.** Length is an *explicit feature* of the
architecture both heads share, so both read it, and their agreement could never have revealed it.
r29 named the blind spot; r47 measured what was in it, eighteen rounds later; **nothing connected
them, because one end of the connection was not in the document.**

**What that cost.** r47 was framed as opening a question about the proxy. It was partly *closing*
one r29 had already posed and explicitly deferred. The project re-derived the question instead of
inheriting it, and the register is where that should have been visible.

**Two checks, two surfaces.** `scope_reaches_the_reader.py` guards the generated package, where a
renderer can silently truncate. `every_round_reaches_the_readme.py` guards the hand-written
surface, where the failure is plainer — a result nobody writes down. Both flag omission only, and
both say so: named is not accurately summarised, and **nothing in this package checks a round's
wording against its own verdict.** That gap is now stated rather than assumed away.

## Entry 59 — queue item 2 froze a line, and five rounds went on asserting it in their own artifacts

**The third instance of one failure.** Entry 51: a rescope reached README and the manifest, not the
rounds. Entry 57: scope clauses reached MANIFEST.json, not the rendered document. This: **queue
item 2's freeze reached FROZEN.md and the README, and not the rounds** — which regenerate their
verdicts at run time and so kept emitting the frozen conclusions into their results files.

What the artifacts still said, against a freeze recording the line as **UNRESOLVED**:

| round | its own verdict |
|---|---|
| r01 | "STRUCTURE (M2): agreement persists across prompts beyond the null" |
| r23 | "M2 WEAKENED: …" |
| r26 | "M2: pair identity carries structure AND that structure is signed — **there are pairs that reliably disagree**" |
| r27 | "**ACTOR EFFECT, NOT BLOCS**: …" |
| r28 | "**A MINORITY BLOC SURVIVES**, an order of magnitude smaller than …" — ⚠ **see the correction below; this was not r28's verdict** |

FROZEN.md meanwhile records why each of those four separators *could not* separate: r23's z read
+10.26 at 2 null reps and +1.40 at 40; r26's centred residual gives "below average" and "actually
disagreeing" the same number; r27's control selects same-bloc pairs under unequal bloc sizes and so
could not have found blocs if they existed; r28 was rank-deficient by exactly 1, its z moved with
`PYTHONHASHSEED`, and its held-out R² spanned [−1.64, +0.51].

So r27 asserts "NOT BLOCS" from a control that could not detect blocs, and r28 asserts "A MINORITY
BLOC SURVIVES" from a fit the register calls unusable — **in the files an outsider opens**.

**How it was found.** Not by looking for it. Entry 58 left "wording" as the one unchecked surface,
so I surveyed the verdict vocabulary to see whether a wording check was soundly buildable. **It is
not** — 36 rounds share no status grammar, and a keyword checker on that would misfire and be
switched off. But the survey printed the leading tokens, and "A MINORITY BLOC SURVIVES" sat next to
a queue that lists r28's ontology as frozen.

**Fixed by a register rounds can read, in two passes.** `covalx/frozen.py` holds the freeze text
once; each affected round appends it to its own generated verdict. That fixes the DEFAULT output
only — sweep rounds write one file per setting (r26 nine, r27 five, r28 four) and refreshing those
means re-running each cell, which the metric-sweep freeze forbids. So
`assurance/apply_freeze_status.py` stamps the register's text into every existing cell, by the same
mechanism and for the same reason as `apply_outcome_scope.py`: the string lives once, in code, and
the utility copies it.

**And the stamper's own first version reported 20/20 while missing three rounds.** It looked only
for a `verdict` field. r17 and r18 use `conclusion`; **r16 has neither — and has a key literally
named `blocs_are_real`, putting the frozen claim in the schema rather than in prose.** "20/20" was
coverage of what the stamper could see, not of the register it was given. All three shapes are now
handled, and r16's file carries an explicit note that its key name asserts what the freeze
withdraws. The finding about a round's own data is
untouched and still correct — what is appended is the status of the **line** the finding belongs
to. No conclusion string was hand-edited.

**The uncomfortable arithmetic.** Item 2 was completed many turns ago and reported as done. It was
done in two of three places. Each of these three entries was found by a different accident, and
none by a check that existed at the time.

---

### CORRECTION to this entry, one turn later — I misattributed r28

**r28's own verdict was already right.** `r28_pearson.json`, the primary output, reads:

> FUNCTIONAL FORM UNRESOLVED. The algebra stands … But the multiplicative alternative is NOT
> thereby established. It wins only in sample … out of sample its R² ranges [−1.6442, +0.5109]
> against the additive shape's tight [+0.3377, +0.4208] … **the both_low number below must not be
> read as a measurement of anything.**

That is more self-critical than the freeze text I appended to it.

**What I actually quoted** was `r28_cosine.json` / `r28_spearman.json` / `r28_multiplicative.json`
— **secondary metric cells written 07-28 12:05–12:09 and never re-run** after r28's verdict logic
was corrected. They carried the withdrawn "A MINORITY BLOC SURVIVES" wording because they predated
the fix, not because r28 asserted it.

**So the entry above overstated one of its five rows**, in a register whose purpose is to stop
exactly that. The other four rows stand: r01, r23, r26 and r27 did assert the frozen conclusions in
their primary artifacts.

**Fixed:** all four metric cells re-run and now carrying both the corrected verdict and the freeze;
the duplicate `r28_multiplicative.json` archived under `_superseded/`.

**The lesson is not "check harder".** It is that *"a round's verdict"* is not well-defined when a
round writes five results files, and I read one directory listing's first match as though it were.
The frozen list in the queue names "r25 metric cells" for exactly this reason — metric sweeps
produce cells that go stale independently of the round that made them.

## Entry 60 — three instruments in three turns reported completeness over their own visible subset, and the fix is to enumerate from the requirement

**The shape, now attested three times:**

| turn | instrument | what it reported | what it could not see |
|---|---|---|---|
| −3 | `ASSURANCE.md` renderer | claims present | everything after character 110 — i.e. every scope clause |
| −2 | `results_match_their_code.py` | round "ok" | four stale cells, because it took `max()` over results |
| −1 | `apply_freeze_status.py` | "20/20 verdicts" | three rounds using `conclusion` or no verdict field at all |

None was wrong about what it saw. **Each was wrong about what it had been asked to cover**, and
each was built to catch the previous one.

**The structural fix.** `registries_are_satisfied.py` enumerates from the **registry** — the list
of things that *must* carry an annotation — and checks each. A registry entry with nothing to
inspect is then a **loud failure** rather than an absence from the denominator. That inversion is
the whole content of the check.

**It found a real one on its first run.** `covalx/frozen.py` named `r25_metric_sweep`. The round is
**`r25_actor_dyad_sweep`** — I guessed the directory when writing the registry. It has no `run.py`
(it is `cell.py` + `collect.py`), and **145 sweep cells, none of which carry a verdict string**, so
every string-stamping utility passed over it in silence while reporting totals that looked
complete. 145 cells of a frozen line, asserting nothing but annotated with nothing either.

Now stamped: **145/145**, and the registry-side check passes with 9 freeze entries and 13
outcome-scope declarers, all satisfied.

**What it still cannot do**, stated because the entries above are all about instruments that
overstated themselves: carried is not correct and not prominent. This flags omission only, and it
cannot judge whether a given freeze is the *right* annotation for a round — only that the round was
not skipped.

---

### EXTENSION — the registry was internally satisfied and covered two of five frozen lines

The check above verifies registry entries are *satisfied*. It never asked whether the **registry
matches its own authoritative source**. `FROZEN.md` names five frozen lines; `covalx/frozen.py`
covered two.

**Section 2 — the task-position regime reading, `r02`, `r24`, `r31` — had never been delivered to
any round.** That freeze is not cosmetic: the discontinuity is real and within-person (−179.2
chars [−196.2, −162.3], −53.3%, on the 933 people present at both positions), but the release has
**no session identifier and no timestamp**, so within-session fatigue is not separable from
between-session habituation. All three rounds now carry it, with the instruction *do not call this
fatigue*.

The check gained a third section comparing the registry against `FROZEN.md` sections 1–3 — the
**interpretation** freezes, which name their rounds in the header. Sections 4 and 5 freeze
*activities* ("more best-of-n") and a headline, which are not round annotations; that exemption is
stated in the code rather than silently applied. 11 rounds named, 11 in the registry.
Positive-controlled: deleting r24 from the registry makes it fire and name r24.

**The recursion is the point.** Entry 60 was about instruments reporting completeness over their
visible subset. The fix — enumerate from the registry — has the same failure one level up, because
**a registry is itself a visible subset of what should be in it.** The only exit is to check each
level against the level that authorises it, and to say where that chain stops: `FROZEN.md` is
hand-maintained and nothing checks *it* against the queue.

## Entry 61 — "unfixable without re-running a frozen round" was the sixth boundary I asserted and could have tested

**The working rule, arrived at the hard way over five entries:** *when I say something cannot be
checked, that claim is the next thing to check.* This entry is that rule applied to my own most
recent ceiling.

**What I said, twice:** that r16's key `blocs_are_real` "remains unfixable without re-running a
frozen round", and later that it "stays unfixable… so the note is the honest ceiling."

**Both wrong, for two independent reasons.**

1. **The freeze is on the interpretation, not on execution.** Renaming a field so it stops
   asserting the withdrawn claim *implements* the freeze; it does not extend the frozen line. I had
   collapsed "this line is frozen" into "this round may not be touched."
2. **The cost claim was never checked.** r16 is a **190-line CPU round** with no torch or CUDA, the
   key was written in **exactly one place** and read **nowhere**. Ninety seconds of work sat behind
   a ceiling I had recorded twice.

**Done.** The key is now `profile_regret_exceeds_random_by_1.15x` — which is precisely what the
boolean computes: the profile split's mean regret against a random split's, at a 1.15× bar. The
round's console line no longer says "blocs are a real constituency". Numbers unchanged: regret
**2.0699** profile vs **1.1017** random. A `schema_note` records the old name and why it went.

**Why the schema mattered more than the prose.** Every annotation this session — freeze text,
outcome scope, population note — is a *string in a field*. A misleading **field name** is
unreachable by all of it: no stamper can annotate a key. That is why it survived the freeze, the
stamping, the registry check and the registry-completeness check, and was visible only as a line in
my own detection logic.

**Sixth instance.** Truncation, `max()`, field-name, registry coverage, "a human comparison", and
now this. Each was a place I declared the boundary of what could be verified, and each was one step
short of where the boundary actually was.

## Entry 62 — the sweep behind entry 61: 35 schema-level assertions, and the frozen words are in field names

Entry 61 renamed one misleading key and identified the class: **every annotation this project
produces is a string in a field, so a misleading field NAME is unreachable by all of it.** That was
an anecdote. This is the measurement.

Across every non-smoke results file: **1,217 distinct keys, 35 whose name asserts something.**
Most are honest and describe what was measured — `positive_control_passed`, `threshold_is_inert`,
`delta_is_a_stipulation`, `cutoff_is_binding`, `partition_is_structural`. Some are questions whose
value answers them, which is fine: r28's `multiplicative_generalises_better` is **False**, and r54's
`mechanism_explains_r12` is **False**.

**The ones that assert a frozen or retired claim in the name:**

| key | round(s) | status |
|---|---|---|
| `min_bloc`, `mean_bloc`, `min_bloc_ci`, `random_blocs` | r16 | **renamed** → `min_segment`, `mean_segment`, `min_segment_ci`, `random_splits` |
| `bloc_axis_singular_share` | r18 | **renamed** → `profile_axis_singular_share` |
| `structure_is_signed` = **True**, `pair_structure` | r26 (9 cells) | **DONE** → `s2_exceeds_dyad_permutation_null`, `s1_exceeds_dyad_permutation_null` — names that describe the *tests* (two dyad-permutation tail probabilities) rather than the reading FROZEN.md §1 withdraws |
| `constituency` | r06 + 4 | **outstanding** — the frozen term, though here it names a *rule* being compared, not a finding |
| `D_leakage` | r34 | **DONE** → `D_same_sample_premium`, with manifest C17's gate path updated in the same edit; r34, r42 and the manifest all re-run, C17 still HOLDS at 0.0055 < 0.01 |

**Costs, stated rather than used as an excuse.** r16 and r18 are single-file CPU rounds and were
renamed and re-run; both now have zero keys containing "bloc". `D_leakage` needed a coordinated
edit — r34, `assurance/manifest.py`'s C17 gate path, r42 (which walks r34's estimand keys) and the
README — and is **done**: C17 still HOLDS at 0.0055 < 0.01, and r42 still lists the contrast in its
"real but negligible" cell. **r26 is done too, and my cost estimate for it was wrong in the usual direction.** I said "nine
cells at ~10 minutes each, so ~90 minutes", which assumed sequential execution. The historical
pueue timings show the eight original cells ran **in parallel** — all started 11:52:27, all finished
by 12:24 — so the wall-clock is ~30 minutes, and `cpu-run` has parallelism 20. A cost asserted
without checking, used to defer work, and wrong by 3×.

**And the rename itself failed once first, in a way worth recording.** My first attempt used a
word-level regex on `structure` and `signed`. Those words appear throughout r26's docstring and
inside its verdict *prose*, where they are correct English — so the substitution produced
`"M2: pair identity carries s1_exceeds_null AND that s1_exceeds_null is s2_exceeds_null"`. Not a
rename: corruption of the conclusion text. Reverted via git and redone against the two assignments,
the two dict keys and the three branch conditions only, with an assertion that no bare
`structure`/`signed` assignment survives in code. The verdict prose is verbatim unchanged.

**Two self-inflicted stumbles worth recording, because both are the same shape as findings above.**
My first rename attempt asserted `"D_leakage" not in source` and fired — the *comment explaining
the rename* contained the retired token, so the guard rejected its own documentation. That is
exactly the r12 case from earlier in this register, where a withdrawal narrative put the retired
phrase back into the artifact an outsider greps. The assertion now checks **code lines only**, and
the comment is written to avoid repeating the token anyway. And both failed attempts aborted
*before* the write while the subsequent commands ran regardless — so an unchanged `C17 HOLDS`
printed twice and could have been read as success.

**Why this is worth a register entry rather than a silent fix.** FROZEN.md section 3 instructs:
*read the partition as a latent profile split, never as a bloc, minority or constituency.* That
instruction was written, delivered to prose, stamped into artifacts — and the word it forbids was
sitting in twelve field names the whole time, in the same files carrying the freeze text.

## Entry 63 — a wait loop whose condition can never be true is indistinguishable from a wait that finished

**What happened.** I launched nine r26 cells in parallel, then waited on them with

```
until [ "$(pueue status | grep -c 'r26-.*-rename.*Running\|r26-.*-rename.*Queued')" = "0" ]; do sleep 30; done
```

`pueue status` prints the **status column before the label**, so `r26-…-rename.*Running` can never
match. `grep -c` returned 0 on the first evaluation, the loop exited immediately, and the
verification that followed ran against the **pre-rename** files — reporting *"old key present in 9,
new key in 0"* as though the re-runs had completed and failed.

They had not completed. They were still running.

**Why this is the same defect twice in two turns.** Last turn: a guard aborted before its write
while the commands after it ran anyway, so `C17 HOLDS` printed from an unchanged repository. This
turn: a wait condition that cannot be satisfied exits at once, so a verification prints from
unchanged files. **Both produce a confident, specific, wrong report — and in both cases the shell
gave no error at all**, because nothing failed. A pattern that matches nothing is not an error; a
loop that runs zero times is not an error.

**What distinguishes them from the earlier entries.** Entries 57–62 are about instruments reporting
completeness over a visible subset. This pair is narrower and more embarrassing: **the instrument
never ran, and its silence was formatted as a result.**

**Fixed** by waiting through `pueue status --json` and testing the status field directly, rather
than grepping a table whose column order I had assumed.

**The general form, since this is now the working rule's second corollary:** a check that reports
"nothing outstanding" must be able to distinguish *nothing outstanding* from *nothing observed*.
Neither the grep nor the loop could.

**Demonstrated side by side, against nine genuinely pending jobs**, which is a control only
available while they were still running:

```
OLD grep pattern   matches = 0   -> until-loop exits immediately, reports "done"
NEW waiter         exit    = 3   -> still waiting
ground truth       9 tasks actually pending
```

`assurance/pueue_wait.py` replaces the pattern: it reads `pueue status --json` and inspects the
status field, so column order cannot fool it, and it **returns exit 2 — not success — when it
matches no task at all**, because that is precisely the state this entry is about. Both behaviours
are positive-controlled above rather than asserted.

## Entry 64 — every check in this package returned success on an empty observation

Entry 63's corollary was stated as a rule: *a check reporting "nothing outstanding" must be able to
distinguish nothing outstanding from nothing observed.* I wrote that about a shell loop and did not
apply it to the six checks in `assurance/`.

**Tested, not read.** Emptying `MANIFEST.json`'s claim list and running the delivery check:

```
claims in manifest: 0   carrying a scope clause: 0
reproduced verbatim in ASSURANCE.md: 0
Every claim statement reaches the document in full.        exit 0
```

A check built two turns earlier **specifically to catch delivery failures** passed on a manifest
containing nothing. The same defect was present in `every_round_reaches_the_readme`,
`no_withdrawn_framings`, `outcome_variable_declared` and `registries_are_satisfied` — five of six.

**The one exception is instructive.** `registries_are_satisfied` already treats a registry entry
with no inspectable files as a **loud failure**, because entry 60 forced that design. It got the
per-entry case right and still returned 0 if the registry itself were empty. Getting the principle
right in one place does not propagate it.

**Fixed** with a shared `_floor(n, what)` in each: an empty population now returns **exit 2**,
distinct from pass (0) and fail (1), printing *"a check with no population has not passed, it has
not run."* Verified by re-running the emptied-manifest control: **exit 0 → exit 2**.

**Why this matters more than the individual bugs.** Six checks, six turns, each written to catch
the previous one's failure — and all six shared a defect that any one of them would have caught if
pointed at itself. The suite was never tested against the state it exists to detect: **absence.**

---

### The floor, verified for all five rather than the one I demonstrated

`assurance/attack_the_suite.py` empties each check's population, asserts the exit code, restores,
and re-runs the live suite so a broken restore cannot pass silently. **5/5.**

| check | emptied | expected | why |
|---|---:|---:|---|
| `scope_reaches_the_reader` | 2 | 2 | zero claims → nothing to check |
| `every_round_reaches_the_readme` | 2 | 2 | zero rounds → nothing to check |
| `no_withdrawn_framings` | 2 | 2 | zero files → nothing to check |
| `outcome_variable_declared` | 2 | 2 | zero gold-scored rounds → nothing to check |
| `registries_are_satisfied` | **1** | **1** | **a detected failure, not blindness** |

**The last row is the design working, and my first harness got it wrong.** I asserted empty→2
uniformly and marked `registries_are_satisfied` BROKEN. Reading its output instead of trusting my
expectation: with an empty registry it reports **11 rounds that `FROZEN.md` names and the registry
no longer contains**. It enumerates from the *requirement*, so deleting what exists cannot silence
it — which is exactly what entry 60 built it to do. **A check that knows what ought to exist is
immune to the entry-64 defect on that input**, and the harness now records why rather than
flattening it.

The invariant is therefore weaker and truer than "empty must be 2": *emptied must never be 0* —
either the check says it observed nothing, or it detects a failure from a population it did not
lose.

## Entry 65 — the retired framing was the README's headline for fourteen turns

**Queue item 1, the first and highest-priority task, says the values-vs-non-values contrast "must
never be a headline again."** It was the README's subtitle, on line 3, the whole time:

> **Does a public-input values rubric actually measure values?**

Item 1 was worked through eight places in the prose, four claims in the manifest, the round verdicts
(entry 59), the assurance renderer (entry 57) and the gated statements (entry 51). **Every one of
those was downstream of the sentence that states the project's question.**

**Why no check could have caught it.** `no_withdrawn_framings` scans results JSONs and deliberately
excludes prose — because README legitimately *discusses* withdrawn framings in order to withdraw
them, and a checker that cannot tell assertion from mention would either flag that forever or be
taught to ignore the sentences it exists to police. That exemption is correct and it is exactly the
hole this fell through. The one surface no instrument watches is the one a reader meets first.

**How it was found.** Not by looking. I added the layer table above the headline, printed the first
eight lines to confirm it landed, and the retired question was sitting directly beneath the title in
the output.

**Fixed.** The subtitle is now *"What does a public-input values rubric actually measure, and at
what scope?"*, with the withdrawal recorded inline — because deleting it silently would leave a
reader of the git history unable to tell that the framing was ever wrong, and the register's whole
premise is that a corrected claim should be visible as corrected.

**The uncomfortable count.** Entries 51, 57, 59, 61, 62 and now 65 are all one failure: a correction
made and not delivered somewhere. Six instances, each found by accident, in a project whose central
finding is that **a measurement's scope must travel with its number.**

---

### "Unwatchable by construction" was wrong too — the seventh boundary I asserted and could test

I closed this entry saying the prose surface is unwatchable. The reason given was real: README
legitimately *discusses* withdrawn framings, so assertion cannot be told from mention. But there is
a sound narrower population — **structural position.** A title, a subtitle, a header and a table
cell assert by where they sit; body prose can be a mention.

Measured before building anything:

| document | headers/subtitle | table cells | body prose |
|---|---:|---:|---:|
| README.md | 0 | 0 | 3 |
| FROZEN.md | 0 | 0 | 0 |
| PREREGISTRATION.md | 0 | 0 | 0 |

The three body hits are the withdrawal discussions. So the assertion positions are already clean and
a check over them fires **zero false positives** while catching exactly what entry 65 records.
`RETRACTIONS.md` is excluded: quoting withdrawn claims is its function, and 5 of its table cells do
so deliberately.

`retired_framing_in_assertion_positions.py` scans 256 such positions across three documents.
Attacked, 3 vectors: entry 65's **exact subtitle** restored → fires and names `README.md:3
(subtitle)`; a retired phrase in a section header → fires; the same phrase in body prose → **does
not** fire, which is required, or the check would flag every withdrawal and be switched off.

**It narrows the unwatchable surface; it does not close it.** A retired framing asserted in a full
body sentence is still invisible, and the module says so on every clean run.

## Entry 66 — the layer table I built to state the object reproduced a correction the same file already carries

**One turn after adding it.** The `M(R,J,π,Q,P)` table's **J** row read:

> predicts **held-out human rankings** above chance (r04)

The README's own scope correction, in a blockquote **twenty lines above it**, says:

> Earlier versions called the 80,542 pairs "held-out human preference". They are **pairwise
> decompositions of the same rankings**, on the same prompts and the same four candidates the
> criteria were written about, by participants who had already ranked them. Holding out individual
> *pairs* does not break that dependence.

I wrote the withdrawn phrasing into the document's new authoritative summary, in the same file,
below the paragraph withdrawing it.

**How it was found.** Verifying that each cited round *supports* its claim rather than merely
containing its number — which is the audit I had described as unbuildable as a general check and
did by hand for five rows. r04 turned out to have **no verdict field at all**; its result is
`pairwise_accuracy = 0.6860` on 80,542 pairs, and what that quantity *means* lives only in the
scope correction, not in the round.

**Corrected** to "reconstructs the missing satisfaction layer well enough to reach **0.686**
pairwise concordance — **internal reconstructive concordance on the elicitation manifold**, not
held-out human preference."

**A second, smaller repair in the same pass.** The **R** row cited "r14/r20" jointly for 97.4%.
Only r20 measures it — `advantage_retained_under_paraphrase = 0.9739`. r14 measures *paraphrase
fidelity* (99.2% kept) and has no verdict. The row now attributes each to the round that produced
it.

**What this says about the check I declined to build.** I concluded a wording-vs-verdict check was
unbuildable because 36 rounds share no status grammar — which is true. But the *hand* audit of five
rows found a withdrawn framing in the project's headline summary within minutes. **Unbuildable as an
automated check is not the same as not worth doing**, and I had let the first stand for the second.

## Entry 67 — the layer table's other three rows, audited: two more omissions, both toward "more settled"

Entry 66 audited the **R** and **J** rows and found a withdrawn framing. The remaining three,
checked the same way — reading each cited round's own verdict rather than its numbers:

**π — correct.** r48's *"IDENTIFIED, NOT PROXIED… 18 of 15,248 (0.1%)"* and r35's *"ROBUST TO
POST-HOC CRITERION ABSTENTION"* both say what the row says.

**P — omitted r42's own qualifier.** The row said the population contrasts are *"equivalent to zero
at δ = 0.01 rather than merely non-significant"*. r42's verdict ends: *"supported at this stipulated
margin **and at no other**"* — and its sweep is **12/21 equivalent at 0.01, 7/21 at 0.005, 4/21 at
0.0025**. A reader of the row would take the equivalence as a property of the data; it is a property
of the data *and a margin I chose*. Now stated inline.

**Q — understated its own round.** The row said the gold head "reads length (+0.077 → +0.458)".
r47's headline is stronger and cuts the other way: **roughly half the inversion rides on that
channel** — 57% survives residualisation against the procedure's own null, and on held-out prompts
the fresh arm **stops being negative** once length is removed (`fresh_still_inverted_after_length`
is `True, False` across the two samples). So *"the advantage does not transfer"* replicates and
*"an unrelated rubric beats it"* does not. Omitting that made the transport failure look more solid
than r47 supports.

**The direction is the finding.** Both omissions ran toward *more settled than the evidence*. Not a
number wrong anywhere — the numbers were verified before the table shipped. What was missing each
time was **the qualifier the round itself had already written**, which is the same defect as entries
51, 57, 59 and 66, now inside a table built to prevent exactly that.

**Five rows audited, three defective.** The hand audit cost minutes and found more than any
automated check in this package has.

## Entry 68 — under-replication does not move the estimate, it inflates the TEST STATISTIC

r27's null was estimated from **15 replicates**. Re-run at 200:

| quantity | 15 reps | 200 reps | moved |
|---|---|---|---|
| ratio just below zero | 1.1967 | **1.2019** | no (both round to 1.20) |
| ratio below −0.20 | 1.3519 | **1.3519** | no |
| far-tail actor-control **z** | **−10.00** | **−7.72** | **yes, 23%** |

**The mechanism is the point.** Under-replication left every *ratio* essentially unchanged — those
are means, and 15 draws estimate a mean adequately. What it corrupted is the **z**, whose
denominator is the null **SD**, and an SD from 15 draws is the unstable quantity. So the effect of
too few replicates ran entirely into the statistic that expresses *confidence*, and in the direction
of more of it. A reader auditing the ratios would have found nothing wrong.

**Where it had reached.** RETRACTIONS entry 29 — the document whose job is to say what survives a
retraction — recorded `z=−10.00` as *"the observation, not the inference"*. The thing I kept was
carrying the inflated number. Repaired inline, with the cause named.

**The sweep, and its own defect.** I then checked every round for under-replicated nulls. The first
instrument was wrong in both directions: it read booleans as counts (`isinstance(v, int)` is True
for `bool`, so `reversal_above_null: False` surfaced as *"min=0"*) and its regex mis-captured
argparse lines. Its output is not published. Hand-reading the flagged call sites settles it: every
other small count — `a.boot = 200`, `a.seeds = 3`, `a.prompts = 8` — sits inside an `if smoke:`
branch overriding a 4000 default. The one real small count is r47's `nrep = 20`, already declared.

**So: r27 was the only round with an under-replicated published null** — and that conclusion rests
on the hand-check, not on the automated sweep, which was unfit.

## Entry 69 — the check that verifies README numbers tested 8% of them, because tables have no blank lines

`readme_agrees_with_results.py` exists to catch prose that no longer matches the artifact it was
read from (entries 18, 42). It split the README on blank lines and skipped any block citing ≠1
round. **A markdown table contains no blank line**, so every table was one block citing every round
in it — and was skipped whole.

| | numbers reached a pool |
|---|---|
| before | **58 of 760 — 8%** |
| after row-splitting + a union arm | **336 of 760 — 44%** |

The three largest skipped blocks were the round-summary table (53 numbers, 21 rounds), the r39 table
(88, 19) and the **layer table I added two commits ago** (22, 18). The densest, most checkable,
most load-bearing prose in the document was invisible **because it was well-organised.**

**Three changes.** Table rows are split into their own blocks. A block citing several rounds is no
longer skipped but tested against the union of their pools, reported separately — *unmatched under
the union ⇒ unbacked by any cited round; matched ⇒ **some** cited round holds it, not the right one.*
A round **named in prose** may only widen a block into the weak arm, never drive the strong one: a
paragraph about r12's anomaly carries r41's measurements of it, and letting a bare mention attribute
them produced 33 false flags in one pass.

**The positive control failed first, and for the right reason.** Planting a fabricated value in a
table row, the check *found* it and **did not print it** — the union arm truncated its own flagged
list at 18 entries and the plant fell in the tail. That is entry 57 exactly (a renderer deleting
what it was built to deliver) reappearing inside the fix for a different bug. The list is now
printed in full.

**What it found in the README: nothing wrong.** Of 35 first-pass flags — 17 were values that appear
as JSON *keys*, invisible to `collect_floats`; 4 were correct prose the instrument mis-attributed
(line 1115 says *"r06's 0.6575 arm … on 945"* and the numbers are r06's, but only r04 was linked);
the rest were chance.

**The chance rate is the part worth keeping.** "This number also appears in a different round" felt
like entry 18's transplant. Against 32,164 stored values across 55 pools, the measured null match
rate for the flagged tokens was **62–100% for anything printed to one or two decimals** — `1.9`,
`0.75`, `91.6%` and `25.3%` all match something with probability 1.00. Only high-precision or
large-integer tokens are informative (`18,384` at 0.2%, `945` at 7.0%, `0.6575` at 25.5%). **A
coincidence detector run against a large enough pool detects coincidences**, and without that null I
would have published fifteen "possible transplants" of which eleven are arithmetic.

## Entry 70 — the equivalence round tested 21 contrasts and its verdict said "this package". There are 125.

r42 exists so that a non-significant result is never read as "no effect". Its population is
`SOURCES`, a **hand-written list of four rounds**. Its verdict reads *"the null readings in this
package are supported at this stipulated margin"* — and *this package* is four rounds.

**Its internal guard could not catch this.** After r36's contrasts were silently missed, I added:
*"REFUSING: this file contains N paired vectors but the walk reached M."* That compares counts
**inside files it already opened**. r13 stores zero nodes named `paired_differences`, so the guard
was satisfied at 0 == 0 while r13's seed-vs-write-in gap — the contrast the README uses to refute
r12's own mechanism — was never equivalence-tested at all.

**r58 enumerates instead of listing.** Every results node carrying an interval estimate:

| | at δ = 0.01 |
|---|---|
| interval contrasts in the package | **125** |
| tested by r42 | **21 (17%)** |
| real and material | 60 |
| real but negligible | 9 |
| no material effect | 24 |
| **INCONCLUSIVE** | **9** |
| **UNVERIFIED** | **23** |

**All 9 inconclusive contrasts are r43 group-weight cells** — the round whose verdict says *"no
group is predicted better by its own weights"*. For those 9, non-significance is **not** equivalence:
`ai_usage[3]` is −0.0014 **[−0.0323, +0.0290]**, an interval three times the margin wide. The claim
survives as *no detected effect*; it does not survive as *no effect*. This is the queue's
"p>0.05 is not equivalence" showing up inside the round built to study populations.

**UNVERIFIED is 23 and is not a pass.** Those rounds published a mean and a 95% CI but no raw paired
vector, so the 90% CI that TOST requires cannot be recovered. Folding them into "fine" would
manufacture 23 false acquittals; they are reported as their own class.

**What is NOT retracted.** r42's verdict is correct on its own 21 contrasts, and the arithmetic was
never wrong. What was wrong is the noun *package*. The instrument measured what it measured; the
sentence claimed a universe nobody had enumerated.

## Entry 71 — the smoke filter was case-sensitive, and one smoke file was lowercase

Two commits after deleting r47's smoke artifact for being a hazard, I committed one of my own with
r58. Looking for it found the older, worse instance.

**`a04_smoke.json` is lowercase.** Every check filtered on the uppercase literal
`"SMOKE" not in f.name` — seven of them — so `"SMOKE" in "a04_smoke.json"` is **False** and the file
was treated as a real result for the life of the project. It contributes **8 floats present in no
real r04 artifact**, and it carries `pairwise_accuracy: 0.6853540772532188` — the **same key** as the
project's most-quoted number at a different value.

**0.686 is safe**: it is backed by `a04_full.json` at 0.6860023. The smoke value sits one decimal
away, so a README quoting 0.685 would have been "verified" by a warm-up.

**Why the filter class fails.** Marking a run as provisional in its **filename** makes correctness
depend on spelling. The rule was written once as `_SMOKE` and once as `_smoke`, and nothing compared
them. Two independent exclusions now:

  * the name is matched **case-insensitively** (7 checks fixed)
  * smoke output is written to **`results/_smoke/`**, a directory four checks already exclude by its
    leading underscore, and which the non-recursive `results/*.json` glob cannot reach at all

Artifacts were **moved, not deleted** — they stay tracked at the new path.

**The pattern this belongs to.** Entry 69 found a check blind to markdown tables. This one was blind
to a lowercase letter. Both are *the check's population being narrower than its sentence*, and in
both the sentence read as coverage. **A filter is a scope claim, and a case-sensitive filter is a
scope claim about spelling.**

## Entry 72 — the check for entries 66/67/70, and it fires on the two claims the queue ordered rescoped

Three entries in a row were the same defect, all found by hand: *a qualifier the round itself wrote,
absent from the prose a reader meets*. Entry 67 observed the hand audit "found more than any
automated check in this package" — which argues for building the check, not for keeping the audit
manual. `assurance/readme_row_carries_the_verdict.py` extracts every **limitation sentence** from a
round's verdict and asks whether it has any lexical echo in that round's README row.

**The population is the first finding.** 57 README rows; **42** have a verdict to check against.
**15 do not** — r02, r04, r06, r07, r08, r09, r10, r13, r14, r16, r19, r25, r30, r39, r45 — so their
rows are hand-written prose with nothing in the artifact to compare against. Two have already
produced retractions on exactly that account: r04 in entry 66, and r13's *"as informative as"*
equivalence claim, asserted from a paired gap of +0.0231 **[−0.0079, +0.0541]**. They are reported
as UNCHECKABLE, never dropped from the denominator.

**Of 55 limitation sentences, 9 have no echo. Two are the queue's own [NOW] items:**

| round | its verdict says | its README row says |
|---|---|---|
| **r35** | *"NOT ESTABLISHED: the absence of a forced-choice effect"* | **"no."** — answering *does it depend on forcing a direction?* |
| **r37** | *"NOT ESTABLISHED: population invariance"* | **"almost not at all."** |

The r35 row **asserts the thing its own round says is not established.** The queue's second bullet —
*"not a forced-choice artifact" → ROBUST TO POST-HOC CRITERION ABSTENTION only* — was written into
the verdict and never reached the row. Same for the third bullet at r37.

Also flagged: **r15** (*"SCOPE CORRECTION: this does NOT resolve r12"* — the row never mentions r12),
**r47** (*"a SHARE, not a verdict … no binary reading is licensed"* — the row reads
*"partly, and the strangest part does not survive"*), r54, r55. Two flags are false positives from
the broad `does not` / `cannot` pattern (r27, r48), which is the price of a proxy that over-flags.

**What it cannot do, stated on every run.** An echo is not preservation. A row reading *"largely
established"* echoes *"not established"* and passes while inverting the claim. The weakened
paraphrase is the likelier and more dangerous failure and this instrument is blind to it.

## Entry 73 — the check built to catch narrow populations had a narrow population, one commit later

`readme_row_carries_the_verdict.py` read a round's claim from `verdict` or `conclusion` and reported
**15 rounds UNCHECKABLE**. Six of those fifteen state their bounds in the artifact under a different
key: `caveat` (r08), `note` (r19, r30), `schema_note` (r16), `outcome_variable_scope` (r08, r09).

**A round states its bounds wherever it states them.** Reading two field names and calling the rest
"uncheckable" is the same defect the check exists to catch, committed inside the check, one commit
after writing the docstring that names the defect.

Widening to `CLAIM_FIELDS` — verdict · conclusion · caveat · note · schema_note ·
outcome_variable_scope · scope — moved **42 → 47 checkable** and **55 → 76 limitation sentences**,
and surfaced **six omissions the narrower version could not see**:

| round | the sentence its README row did not carry |
|---|---|
| **r05** | *"the cited embedding result (0.736 vs 0.520) is **computed nowhere in this repository or its history** and remains UNVERIFIED"* |
| **r05** | *"both instruments here are lexical, so a shared blindness to paraphrase is not excluded"* |
| **r11** | the retraction is *"a statement about the **proxy-world measurement**"*, not about human preference |
| **r41** | *"`z_R` is produced by **the same judge whose off-distribution validity is unestablished**, so this round cannot separate 'new normative territory' from the judge behaving incoherently on fresh responses"* |
| **r55** | *"it does not establish that no semantic selectivity changed"* |
| **r58** | *"δ=0.01 is STIPULATED, not measured"* |

**r41's is the one that matters.** It is queue item 3's round — criterion-space support geometry —
and the caveat that its entire measurement is judge-relative, on a judge whose off-distribution
validity is exactly what is in question, was in the artifact and not in the row.

**r58's is mine, from this session.** I wrote the stipulation into the round's scope field, wrote
the README row by hand in the same hour, and left it out.

`frozen_line` is deliberately excluded: it is bloc-level boilerplate already enforced by
`registries_are_satisfied.py`, and demanding a per-row echo of it would drown the signal.

## Entry 74 — "response-blind" was carrying an S_pre reading the dataset card does not support

r13 is the closest thing in this package to **S_pre**, one of the three counterfactuals that end this
project. Its README passage had three defects, and the passage contradicted itself.

**① The lead sentence claimed equivalence from a non-significant difference.** It said the seed
criteria *"are as informative as criteria authored after reading them"* — from a paired gap of
**+0.0231 [−0.0079, +0.0541]**, `excludes_zero: False`. Eleven lines below, the same passage says
*"which of the two provenances carries more is **not established**"*. Both sentences, same page.
r58 settles it: the 95% interval spans **0.062, which is 3.1× the ±0.01 window** — this contrast is
**INCONCLUSIVE**, neither an ordering nor a null.

**② "Written *before anyone saw them*" is not what the card says.** Verbatim, `DATASET_CARD.md`:

> L72 **Candidates**: For each prompt, we pre-generated four candidate responses (labeled A–D).
>     These candidates represent a range of potential model behaviors to be evaluated.
> L73 **Full rubrics**: **In parallel**, we prepared initial rubric items as examples of possible
>     objective, prompt-specific evaluation criteria.

**In parallel**, not before. Same *"we"*. The team writing example criteria for a prompt was
simultaneously choosing four candidates *"to represent a range of potential model behaviors"* for
that same prompt.

**③ "Never tailored to the responses" appears nowhere in the card.** It was my inference, printed as
provenance.

**The distinction that matters.** The seeds are blind with respect to **participant exposure** — no
participant had read the four responses when the seed text was written — and that is exactly what
the leakage argument needs, so **r13's refutation of r12's mechanism stands**. They are **not**
independent of the responses by **design**, which is what an S_pre reading needs. Two different
properties, and one word was carrying both. Every occurrence of "response-blind" for the seed arm is
now "participant-blind", with the design coupling stated where a reader meets the number.

**What this costs.** The package's nearest approach to S_pre is weaker than it read. S_pre remains
what r48 already said it was: **unreachable from this release.**

## Entry 75 — entry 71 fixed the spelling and the next provisional file used a different word

Entry 71 made the smoke filter case-insensitive and concluded: *"a filter is a scope claim, and a
case-sensitive filter is a scope claim about spelling."* The conclusion was right and the fix was
still one word wide.

**`a06_dryrun.json`** sits in `rounds/r06_rule_tournament/results/`. Its name contains no form of
"smoke", so it survived entry 71's fix and was in the results pools **at the moment that entry was
written**. It reports rule accuracies of **~0.115** where the real run reports **~0.657** — a dry
run whose numbers are nothing like the round's.

Found by auditing the rounds that have never had a limitation recorded anywhere, not by any check.

**Two fixes, and only the second is real.**

  * every filter now matches a **class** — `smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip`
  * the artifact is moved to **`results/_smoke/`**, excluded by the leading-underscore rule, which
    does not depend on the name at all

The pattern is belt and braces. **Naming is what keeps failing** — twice now — so the exclusion that
survives is the one keyed to location.

**And one check had no name filter at all.** `readme_agrees_with_results.py` relied entirely on its
non-recursive `results/*.json` glob, which `a06_dryrun.json` defeated by being written straight into
`results/`. Verified end to end: a planted `a06_dryrun2.json` no longer reaches r06's float pool.

**The audit that found it also found two unscoped rows** — see entry 76.

## Entry 76 — auditing the rounds nothing had ever attacked: a mean over a sign inversion, and a 6.2× arm choice

Seven rounds have a README row, no claim field in the artifact, and **no limitation recorded
anywhere in this repository** — not in RETRACTIONS, not in the row, nowhere. Nothing has ever
attacked them. Reading three of the load-bearing ones against their own numbers:

**r10 — "stable across judge size and template; 23.7% of the gap is topic, not value".** Three
defects in eleven words.

| cell | attribution vs random | topic share |
|---|---:|---:|
| qwen3.5-2b/A | +0.0869 | +0.3004 |
| qwen3.5-2b/B | +0.0594 | +0.4486 |
| qwen3.5-0.8b/A | +0.0449 | **−0.0369** |

  * **"stable"** — the attribution survives in every cell, which is the real finding, but it nearly
    **halves** from the 2B judge to the 0.8B. A 1.9× range is not what "stable" conveys.
  * **"23.7%"** is `topic_share_mean` — the mean of a quantity that **inverts sign** across the very
    dimension the word "stable" names. In the 0.8B cell `near` (0.4939) sits *below* `random`
    (0.4956), which is what makes it negative.
  * **"topic, not value"** is the retired framing the queue's first line forbids: *never values vs
    non-values*. It survived every framing check because those scan results strings and a fixed
    phrase list, and this phrasing was on neither.

**r14 — "a semantically faithful rewording flips 15.4%".** The round has two arms and the row quotes
one without naming it:

| arm | sign-flip rate | r | fidelity kept |
|---|---:|---:|---:|
| model paraphrase | **15.4%** | 0.871 | 99.1% |
| mechanical rewording | **2.5%** | 0.989 | **100%** |

**6.2× apart, and the arm with the *higher* measured fidelity is the one that barely moves.** The
15.4% is quoted throughout this repository — including the frontier-skill worked example — as the
judge's instability. It is the model arm.

**And a third number.** The layer table's **R** row said r14 filtered paraphrases at *"99.2% kept"*.
The artifact says `fidelity_kept.model = 0.9911616` — **99.1%**. Third defect found in the layer
table that entries 66 and 67 already audited twice.

**The population is the point.** These rounds were not wrong because they were hard. They were wrong
because nothing had ever looked. Rounds with no recorded limitation are not clean; they are
**unexamined**, and the two categories are indistinguishable from the outside.

## Entry 77 — the last four unaudited rounds: a "running" round that finished, and a freeze with no anchor

Completing the audit of rounds that carry a README row, no claim field, and no limitation recorded
anywhere. r02 and r07 hold up — r07's row is among the best-scoped in the document. The other two
do not.

**r25 said "*running*". It had finished.** All **144** cells are on disk (4 metrics × 3 overlaps ×
3 shared-item thresholds × standardise × centre = 144 exactly, 144 distinct configs), plus a
summary. The README has been reporting a completed sweep as in progress.

Its own numbers answer the question, and the answer is *both*:

| | |
|---|---|
| usable cells | 138 of 144 |
| residual clears z>2 | **138 of 138 — 100%** |
| share of variance | **0.2018 – 0.7000**, median 0.2650 |

So the residual is **not** a Pearson artifact — it survives every metric — and its **size** is
metric-dependent across a **3.5× range**. Existence invariant, magnitude not. The gauge control
behaved as predicted: Pearson is invariant to centring (Δ=2.8e-17), cosine and negl1 are not
(Δ=0.0339, 0.0907). The row now reports the sweep's numbers only; the rater-structure ontology it
feeds stays FROZEN as UNRESOLVED, which is a separate question this does not reopen.

**r45's freeze had `"frozen_at_commit": None` — hard-coded, never populated.** `freeze.py:91` set
the literal `None`. A field with that name holding null reads as *"the anchor was recorded"* while
recording nothing, and this is the artifact whose own row calls it *"the only definition of the
object H_fresh refers to"* — one of the three counterfactuals that end this project.

What can and cannot be recovered: `69bda3b9` is the commit that **introduced** the file, from git
history. That bounds when the frame entered the repository. It does **not** establish what tree the
freeze was computed against, which is what a stamped anchor would prove. So the null is **left in
place beside it**, with the recovered value under its own key and the difference stated, rather than
overwritten to look like an anchor that was never taken. `freeze.py` now stamps HEAD **and a
tree-dirty flag** — a freeze from a dirty tree names a state that was never what ran, which is worse
than no anchor at all.

**The manifest is untouched**: `313044ea…`, 60 prompts, 540 hashed responses. What was missing was
provenance for the freeze, not integrity of the frozen payload.

## Entry 78 — the world the claim card did not contain: the rubric flips LESS than its own permutation

r59 asks what a criterion is worth to the judge's ranking: leave one out of the persisted r41 tensor
and see whether the winner changes. No GPU — that tensor reproduced all 1,500 of r12's per-prompt
values exactly, so the judge pass was already paid for.

The claim card enumerated three worlds: **A** a minority of criteria decide it, **B** influence is
spread, **C** influence just tracks discriminating power. **All three assume the real rubric flips
at least as often as a permuted one.**

| | top-1 flip rate |
|---|---|
| real rubric | **14.7%** [12.6%, 17.1%] |
| within-prompt column permutation | **26.1%** |
| shuffled arm (criteria from *other* prompts) | 14.9% |

Paired difference **−0.1140 [−0.1483, −0.0797]**. The rubric is **more** robust to losing a
criterion than a version of itself with each criterion's four values shuffled — a null that
preserves every criterion's own spread exactly and destroys only its association with the responses.
That is a fourth world, **D CONCORDANT**, and it was not on the card. Recorded as added-after, with
its own flag in the artifact, rather than folded into B — which would have reported *"influence is
diffuse"* for what is actually *"the criteria agree with each other."*

**And the shuffled arm kills the interesting version of D.** At 14.9% against the real 14.7%, the
concordance is **not** a product of CoVal-core's compatibility selection: criteria borrowed from
*other prompts entirely* agree about these four responses just as strongly. So what the leave-one-out
measures is the **generic normative backbone this project already documented from the other
direction** — unrelated rubrics beating chance — arriving here as *robustness*, and it says nothing
about whether the compiler's C5 selection is doing anything.

**What it does not touch.** Judge-relative, equal-weight. The released scoring rule is not
equal-weight, and this is **not τ_c** — the change in *human* preference under a criterion
intervention, which no release data reaches.

**The meta-separator earned its place.** The instruction is to ask whether a credible outcome would
show the world-decomposition itself is wrong. Here one did, on the first run, and the honest move was
to name the missing world rather than pick the nearest of three.

## Entry 79 — "selection is a real second term" reported the favourable half of a two-number result

r59's open question was whether CoVal-core's C5 compatibility selection does anything the generic
backbone does not. **r44 already answered it, and the README reported one side of the answer.**

| | accuracy |
|---|---:|
| S3 dedup | 0.6647 |
| **S5 compatibility selection** | **0.6465** |
| S5 null — random, same size | 0.6317 |
| C6 **real** core | 0.6577 |

Two contrasts, both significant, both real:

  * the selection stage **costs −0.0181** [−0.0241, −0.0125] — truncating to four criteria throws
    information away
  * it beats a **size-matched random** four by **+0.0149** [+0.0082, +0.0221]

The round-table row carried only the second: *"Selection also beats a size-matched random choice by
+0.0149, so item membership carries signal too."* The body's heading said *"Selection is a real
second term."* Both read as **selection helps**. The stage is **net negative**, and choosing which
four survive **recovers most of what truncating to four destroys without repaying it**. Membership
is mitigation, not contribution.

The −0.0181 was in the body table the whole time, two lines above the sentence that omitted it — so
this is not a missing measurement, it is **a summary that kept the flattering number**. Every check
in this package passed on it, including `readme_row_carries_the_verdict`, because r44's verdict says
*"selection is a real second term"* too: **the artifact and the prose agreed with each other and
both were one-sided.** A check that compares a row to its verdict cannot catch a verdict that
already dropped the qualifier.

**The arc, stated once.** Polarity rewrite takes 0.5915 → 0.6648. **Every reconstructed stage after
it nets −0.0183**, landing at 0.6465. The real core sits at 0.6577, +0.0112 above the reconstruction
— the part of OpenAI's compiler this cannot see. So queue item 6's answer is: **the compiler's gain
is the polarity rewrite; compression is a cost that careful selection partly limits.**

## Entry 80 — I predicted verdicts hide unfavourable numbers. They don't. They omit numbers entirely.

Entry 79 found r44's verdict citing +0.0733, +0.0662, +0.0149 and omitting **−0.0181**, its only
negative contrast. The obvious hypothesis: verdicts across this package keep the flattering half.
`verdict_cites_its_own_contrasts.py` tests it against r58's census of every significant contrast.

**The hypothesis is refuted.**

| | |
|---|---|
| omissions in rounds that cite *something* | 19 |
| of which opposite-signed to their headline | **5** |
| base rate among CITED contrasts | 4/23 = 0.174 → expected **3.3** |
| P(≥5 \| citation independent of sign) | **0.2249** |

r44 is a real instance and **not** a pattern. World A survives.

**And the check's first run had a denominator bug that made the null look four times stronger.** A
round citing *no* contrast has no headline sign, so its omissions can never be counted as
opposite-signed — **by construction, not by balance**. Counting all 47 omissions gave **p = 0.9294**;
counting only the 19 that could ever have been classified gives **p = 0.2249**. Same conclusion,
one-quarter the evidence. *An unclassifiable case folded into a null is a manufactured acquittal* —
the same error as folding UNVERIFIED into OVERTURNED, in a new place.

**What the check found instead is worse than what I was looking for. Seven rounds cite NONE of their
own significant contrasts:**

| round | significant contrasts | cited |
|---|---:|---:|
| **r12** | 2 — the project's central inversion **+0.102 → −0.064** | **0** |
| **r28** | 12 | 0 |
| **r43** | 7 | 0 |
| r11, r17, r20, r31 | 1–3 each | 0 |

r12's and r43's verdicts contain **zero numeric tokens**. r28's contains five, and **none of them is
one of its twelve significant contrasts** — it quotes different quantities entirely.

A verdict that states no number **cannot be compared to its round**, and every prose check in this
package will agree with it happily: `readme_row_carries_the_verdict` compares a README row to the
verdict, and if the verdict is qualitative the comparison is vacuous. **The chain of checks I built
this session bottoms out in strings that are, for seven rounds, connected to their own measurements
by nothing at all.**

This is not a claim that those verdicts are wrong. It is the statement that **nothing in this
repository could tell.**

## Entry 81 — the project's headline number was wrong in three places, and my own check flagged one of them

Following r12 because its verdict cites no numbers, I compared the README to the artifact.

| where | fresh-arm attribution | correct? |
|---|---|---|
| layer table, **Q** row | −0.064 | ✅ |
| body, line 265 | −0.0716 (r46), r12 −0.064 | ✅ |
| **the central r12 table** | **−0.042** [−0.068, −0.015] | ❌ stored: **−0.0640** [−0.092, −0.0367] |
| **the replication sentence** | **−0.058** [−0.085, −0.031] | ❌ r46 stores **−0.0716** (original +0.0847) |
| **the r12 round row** | **−0.042** | ❌ |

`0.042` does not appear anywhere in r12's results — **no stored value lies within [0.038, 0.047]**.
The same table's ORIGINAL row (0.657 / 0.555 / +0.102) matches the artifact exactly, so one row was
updated and the other was not.

**The check found it, and I dismissed it.** On the first run of the repaired
`readme_agrees_with_results`, `r12 0.042` appeared in the unmatched list. I triaged it under
"matches a different round — possible transplant", measured the chance-match null, found that a
3-decimal token matches something in a 32,164-value pool with probability ~1.00, and dropped the
flag as noise.

**The null answered a different question than the flag asked.** The flag said *0.042 is not in r12's
pool*. My triage asked *is 0.042 appearing elsewhere evidence of a transplant?* — and correctly
answered no. Refuting one interpretation of a signal is not refuting the signal. **A null scopes to
the reading it was built for**, and I let it retire the whole flag. That is the same shape as folding
UNVERIFIED into OVERTURNED, arriving through a correct piece of statistics.

**Why the other two were invisible.** Neither the table row nor the replication sentence cited a
round, so both sat in the 56% of README numbers that reach no pool. The table now carries a
`[r12]` link in its header — coverage 44% → **49%** — so its rows are attributable from here on.

**What does not change.** The inversion is real and replicates: **+0.102 → −0.064** on the released
set, **+0.0847 → −0.0716** on 250 held-out prompts with **zero** overlap. The direction, the
significance and every conclusion drawn from them stand. What was wrong was the magnitude a reader
was given, in the three places they were most likely to read it.

## Entry 82 — re-auditing the batch I dismissed: one real error, and my row-splitting had caused half the blindness

Entry 81 found I had retired a flag with a null that answered a different question. So I re-asked the
original question — *is this token in the pool of the round its block cites?* — for all 28 tokens in
that batch.

**No second `0.042`.** The 19 that came back unbacked resolve into three harmless classes:

| class | example | why it is not an error |
|---|---|---|
| cross-attributed | r04's block quoting **18,384**, **0.6575**, **945** | they are r02's and r06's, and the prose *says so* — the block links only r04 |
| derived, never stored | r48's **63.5% / 36.4%** | 9684/15248 and 5546/15248, computed shares |
| derived, never stored | r06's *"four rules span **1.9** points"* | ×100 of a spread between stored accuracies |

`0.042` remains the only genuine defect in that batch. **The dismissal cost one error, not a class.**

**But the audit found the structural cause of the blindness, and it was mine.** Entry 69's
row-splitting fixed tables being skipped whole — and *detached every row from its table's
attribution*. 426 claim-like numbers across 145 blocks became unattributable, and **entry 81's two
invisible stale figures were exactly there**. Table rows now inherit their table's round ids as bare
**mentions**, so a header-attributed row is checkable at union strength.

One guard was needed and measured: applying inheritance to rows that already cite a round widened
them into the union arm and **collapsed the strong arm from 166 checked numbers to 39**. A row that
names its own source keeps the stronger test.

Both paths are controlled: a plant in a row citing r01 still fires, and a plant in the r12 table's
header-attributed row — *the exact block that hid −0.042* — now surfaces as `0.913 cited: r12`.

**And two tables were mixing two rounds' outputs under one round's name.** The judge-family tables
carry r22's accuracies beside r30's prompt-specific shares; only r22 was linked, so the six share
percentages sat in no pool. All six verify against r30. Both headers now cite both sources.

| | coverage |
|---|---|
| entry 69, before | 8% |
| entry 69, after | 44% |
| entry 81, table link | 49% |
| **this entry** | **55%** |

## Entry 83 — two corrections from this session never reached the document that "cannot be softened later"

`PREREGISTRATION.md` opens by stating its conclusions are written down now *"so that they cannot be
softened later."* It was carrying two claims this session had already corrected elsewhere.

| claim as it stood | corrected by | where the fix landed | where it did not |
|---|---|---|---|
| *"97.4% survives faithful paraphrase (**r14/r20**)"* | entry 66 | README | **PREREGISTRATION, FROZEN** |
| *"+0.0733 to the polarity rewrite with a further +0.0149 to which items survive"* | entry 79 | README | **PREREGISTRATION** |

The first credits 97.4% to two rounds when **r20 alone** measures retention — r14 supplies the
fidelity filter and measures a different thing entirely (a *model* paraphrase flips 15.4% of the
judge's verdicts, a *mechanical* one 2.5%). The second is entry 79's one-sided reading: it omits that
compatibility selection **costs −0.0181**, so selection reads as gain when it is mitigation.

**Nothing scanned for this.** `retired_framing_in_assertion_positions.py` watches the same three
documents — but only for retired *framings*, and only in headers, bold leads and table cells. These
were **number and attribution corrections in body prose**. Every check passed while the un-softenable
document stated two superseded claims.

`corrections_propagated.py` registers each corrected claim as a pattern with its entry number and the
correct statement, and scans every watched document. A hit tells a reader **what to write**, not just
that something is wrong. Five are registered — including entry 81's `+0.102 → −0.042` and
`replicates at −0.058`, and entry 76's `filtered at 99.2%`, so those cannot come back either.

**Its own limit, stated on every run:** it only knows the corrections registered in it. *Registering
is part of correcting* — an unregistered fix is invisible to it, which is the honest boundary of a
pattern registry.

**And it under-covered on its first run.** `WATCHED` listed `ASSURANCE.md`, which resolves to the
repo root; the generated ledger lives at `assurance/ASSURANCE.md`. It printed *"3 of 4"* and skipped
the file silently. A missing watched document is now named and called **unscanned, not clean**.

## Entry 84 — sweeping all 38 entries: 15 hits, 14 were the corrected form, and the one that wasn't is a stale PREMISE

Entry 83's registry started at five, so I swept every quoted span in RETRACTIONS against the four
watched documents. 102 spans, **15 found verbatim in a live document**.

**Fourteen are the sweep working as designed and finding nothing.** An entry quotes both the
withdrawn claim and its replacement, so a hit is a question, not a verdict — and on reading, the
README's subtitle is entry 65's *replacement* (the withdrawn form was *"Does a public-input values
rubric actually **measure values**?"*), entry 66's phrase appears as *"**not** held-out human
preference"*, entry 42's retired headline appears inside the sentence retracting it, and entry 70's
r43 quote carries the INCONCLUSIVE qualifier I added. **The dismissal rate is the point: 14 of 15
correct is what a high-recall proxy looks like, and entry 81 is why each one got read.**

**The fifteenth is a different kind of defect.** Entry 51 established that r34's +0.0576 is computed
on the **majority-rated 36.5%** of criteria — a filter five rounds shared without stating it.
`PREREGISTRATION.md` states r34's result, and contains **no mention of 36.5%, 63.5%, 9,684, or the
majority filter**. The README carries it (lines 666–667); the preregistration never received it.

**And the sharper miss underneath.** Experiment 1's motivation says shared-menu endogeneity is
untouched. **r49 has since narrowed it** — write-in criteria authored by *one* participant and rated
by *only* that participant transfer at **+0.0777** [+0.0674, +0.0883] against **+0.0599**
[+0.0514, +0.0687] for the shared six, paired gap **+0.0172** [+0.0034, +0.0307] excluding zero. So
**shared criterion TEXT is already excluded**; what survives is shared **response exposure**.
r49 is not cited anywhere in the preregistration — nor are r48, r51, r52, r54, r55, r58, r59.

The experiment does not change. **What it can claim does**: the PRE arm separates shared response
exposure, not shared-menu endogeneity entire, and selling it as the latter would overclaim a
counterfactual that has already been half-answered.

**A stale premise is not a wrong sentence.** Every sentence in that paragraph was true when written
and no check could flag it, because nothing in it is false — it is a document describing a state of
knowledge that moved. The registered pattern for it is correspondingly weaker than the others, and
says so where it sits.

## Entry 85 — the eight rounds the preregistration had never heard of, and one of them attacks its own linchpin

Entry 84 left the preregistration citing 21 rounds while the package holds 59. The eight absent ones
— r48, r49, r51, r52, r54, r55, r58, r59 — are all *later* than the document, and two change what
its experiments can claim.

**r52 attacks Experiment 3's linchpin.** That experiment states, in its own words, *"the
manipulation check is the experiment"*: minimal-pair edits are admitted only if a judge panel agrees
the target criterion moved **and the others did not**. But the judges performing that check score
**lexical overlap, causally** — appending six distinctive tokens from response A rather than B moves
the A-vs-B satisfaction gap by **+0.2507** [+0.2300, +0.2714] *for the same criterion*, against an
unrelated-token null of **−0.0045** [−0.0181, +0.0094] spanning zero. A minimal-pair edit necessarily
changes the text. **The instrument verifying "nothing else moved" responds causally to the thing the
edit does.**

The consequence is not noise, it is **selection on the estimand**: check (b) over-rejects, and the
surviving pairs are the ones achievable with the **least lexical change**, so τ_c would be estimated
on the subset of manipulations expressible without moving vocabulary. Now committed in advance —
lexical distance recorded per pair, exclusion rate reported against it, τ_c reported stratified by
it, and a human adjudication sub-sample to bound how much exclusion is instrument rather than
manipulation.

**r59 supplies a prior Experiment 3 needs and does not have.** Leave-one-criterion-out flips the
judge's top choice for **14.7%** [12.6%, 17.1%] of 991 criteria — *below* the **26.1%** from
permutation, because a rubric's criteria agree with each other. That is judge-relative and **not** a
measurement of humans, so it enters as a **prior, not a result**: if human choices are similarly
concordant, single-criterion manipulations move them rarely, and an underpowered τ_c would read as
*"criteria do not cause choices"* when it means *"this design could not have seen it."* The pilot
must estimate the human flip rate **before** n is fixed.

**r54 and r55 strengthen Experiment 2 instead of threatening it.** The judge's lexical channel is
real and causal and *still* fails to explain r12: the own-vs-donor overlap advantage collapses
**+0.1294 → +0.0945** on fresh responses but does not predict *which* prompts drop (corr −0.0736
[−0.2059, +0.0612], r54), and the ordering component is equivalent to zero at δ = 0.01 (**+0.0002**
[−0.0056, +0.0059], r55). A mechanism with a measured causal effect on the judge cannot account for
the transport failure — the strongest available argument that H_fresh is not answerable by any
further computational round.

**r58 corrects a conclusion the document was about to carry.** Its closing list now records that the
population nulls are **not equivalence**: 125 interval contrasts exist, 21 were tested, and **9 of
r43's group cells are INCONCLUSIVE at δ = 0.01**.

All 29 numbers added here were checked against their artifacts before the commit: **r54 8/8, r55
3/3, r59 5/5, r58 2/2 backed.** The preregistration now cites **29** rounds.

## Entry 86 — Experiment 3 redesigned: the fix for its broken check was already in the project

Entry 85 established that Experiment 3's manipulation check is performed by an instrument that
responds causally to the edit it is checking. Naming a threat is not repairing one, and the repair
turned out to be a design this project had already validated.

**r52's stated principle, verbatim from its own docstring:** *"The appendage is the same KIND of
object in both arms, so whatever effect gluing a token list onto a criterion has cancels in the
difference. That symmetry is the design."* r52 used it to neutralise the overlap confound while
measuring the judge. **Turn it on the check instead of the judge and the problem dissolves.**

**Old design.** Base response `R` versus an edit `R'` that changes criterion `c`. Judge verifies the
others did not move.

**New design.** Two edits of the same base — `R⁺` satisfying `c`, `R⁻` violating it, matched in
length and lexical distance from `R`. Participants choose between them; **`R` is never shown**. The
check becomes `s(c_j, R⁺) − s(c_j, R⁻)`: both arms are the same kind of object, so the generic
"the text was edited" response cancels.

**And it removes a second confound the old design never mentioned.** Base-vs-edited puts a
machine-edited response against an unedited one, so a participant can prefer the unedited one for
fluency artifacts having nothing to do with criterion `c`. That is a confound in the **outcome**, not
the check, and symmetry removes it outright rather than controlling for it. I did not notice it until
the symmetric design made it visible — which is the argument for fixing a design rather than
annotating it.

**Verification is now three layers, because no single one is sound.** A **mechanical locality** check
on the diff — the only layer with no instrument in it; the **differential judge check**, with its own
positive control (a placebo pair edited on a criterion *not* in the rubric must show ≈0 difference on
every rubric criterion, or the round reports **UNVERIFIED** rather than a τ); and **human
adjudication on a sub-sample**.

**What symmetry does not fix, stated rather than assumed.** It cancels what editing does *in common*
to both arms. If satisfying `c` reliably imports `c`'s own vocabulary while violating it does not,
a second-order difference survives for criteria sharing that vocabulary. So lexical distance is
matched by construction, the exclusion rate is reported against it, and **τ_c is reported stratified
by it — with the stratified result as the headline if the strata disagree**.

## Entry 87 — the same attack on Experiments 1 and 2: an unnamed matcher, and a "human" experiment with a model in it

Entry 86 fixed Experiment 3 by asking one question: **which instrument performs each verification
step, and does it respond to the manipulation?** Asked of the other two experiments, it finds one
defect each.

**Experiment 1 — "the same criterion" is a step nobody specified.** The primary outcome is sign
agreement between arms *"on the same criterion"*. But PRE participants **write their own** criteria
and POST participants **rate pre-seeded** ones — different objects. Every comparison therefore passes
through a **matcher**, and the design named none. The obvious choice is the worst available: r14
measured that a *model* paraphrase flips **15.4%** of this judge's verdicts where a *mechanical*
rewording flips **2.5%**, so a model asked *"are these the same criterion?"* is operating in its
least stable regime.

Now committed: matching is **human, blind to both arms' directions, two annotators plus a third for
disagreements**, with inter-matcher agreement reported. A model matcher may run alongside and have
its disagreement rate reported; it never produces the primary number.

**And the fix exposed a signal the design was about to discard.** A POST criterion with no PRE
counterpart is a criterion that **only arises after seeing the responses** — which is menu-induced
construction, measured directly. The unmatched rate is now a **primary outcome**, not an exclusion.
An experiment that quietly dropped unmatchable criteria would have thrown away its strongest
evidence for the very world it exists to test.

**Experiment 2 — it replaces one model in the chain, not both.** r12 scores both response sets with
`Judge(MODEL_DIR, batch=32)` (`rounds/r12_response_set/run.py:208`). Human rankings replace the
**gold head**; the **satisfaction layer** stays model-produced. The rubric side of "own-rubric
concordance" is still a judge answering *does response r satisfy criterion c?* — and that judge reads
lexical overlap **causally** (r51, r52).

**The instrument carries exactly the validity gap the experiment exists to measure.** r04 validates
the satisfaction layer against human rankings on the **released** responses (0.686 on 80,542 pairs).
**Nothing validates it on fresh ones.** So H_fresh would measure transport failure using a
satisfaction layer whose own transport is unestablished — the project's central finding reappearing
inside the experiment designed to settle it.

Now committed: a **satisfaction sub-study** in which humans answer the satisfaction question directly
on a sub-sample of (criterion, fresh response) pairs — the human-vs-judge agreement rate on fresh
responses that r04 supplies for originals and nobody supplies here. **If it is not run, the headline
reads "human rankings against a model-scored rubric", never "human-measured."**

Every figure above was checked against its artifact before commit: r04 2/2, r14 2/2, and the r12
line quoted from the file.

## Entry 88 — every number in this project is measured against the WORLD ranking, and no document said so

Auditing the human protocol for recruitment sent me to the dataset card's task flow, where CoVal
asks each participant for **two** orderings of the same four responses:

| block | the instruction participants were given |
|---|---|
| **personal** | rank them *"according to their own personal values and preferences"* |
| **world** | rank them again for *"what would be best for the world overall (a more impartial or societal perspective, rather than just their personal taste)"* |

**This project uses the world ranking, everywhere.** `covalx/judge.py:245` reads
`ranking_blocks["world"]`, and the function's own docstring says *"strict pairwise preferences from
world rankings"*. So **0.686**, **+0.102 → −0.064**, **+0.0576**, **97.4%** — every concordance
number in the package — means *agreement with what people said is best for the world*, **not**
*agreement with what people preferred*.

**Neither README.md nor PREREGISTRATION.md mentioned either word.** The choice was made once, in a
helper function, and never surfaced. A reader takes "predicts human rankings" to mean preference;
it means an explicitly impartial judgement that participants were asked to give *instead of* their
taste.

**And the unused half is the one the reframed object is about.** The personal ranking is present for
**76.9%** of assessments and **has never been touched here**. The literature framing this project
adopted turns on *preference is not value* — and CoVal collected both orderings, from the same
person, about the same four responses. That contrast has been sitting in the release the whole time.

**Consequences recorded, not just noted:**

- the README now states the outcome variable in its opening paragraph and in a block above the layer
  table, with the file and line
- H_fresh must collect the **world** ranking or it is not comparable to r12. Now committed — and
  committed to collect **both**, world primary, personal secondary and labelled exploratory, because
  the second screen is nearly free and yields a contrast nobody has run

**Why no check caught it.** `outcome_variable_declared.py` asks whether a round scoring against the
model gold head says so. This is a different axis entirely — *which human ordering* — and no
instrument in the package has ever had an opinion about it. The rounds' `outcome_variable_scope`
fields distinguish gold-proxy from human; none distinguishes world from personal.

## Entry 89 — I sampled the head of a file and published the number; and the contrast it pointed to is out of the release's reach

**The correction first.** Entry 88 said the personal ranking is present for **76.9%** of
assessments. It is **26.7%** — 4,901 of 18,384. I measured it by breaking out of the read loop after
400 lines and reported the result as a property of the file. The head of `comparisons.jsonl` is not
a random sample of it. Corrected in README and PREREGISTRATION, and registered so it cannot return.

**What the full pass shows, and it is the part worth keeping.** Where both orderings exist they
disagree constantly:

| | |
|---|---|
| assessments with both orderings | 4,901 (26.7%) |
| the two orderings **identical** | 53.2% |
| **top choice differs** | **29.0%** |
| strict world pairs **reversed** in personal | **9.70%** |

Asking the same person for an impartial judgement instead of their taste changes their ordering
about half the time. Entry 88's finding — that every number here is measured against one of these
and no document said so — is therefore material, not bookkeeping.

**r60 then runs the contrast on the only clean estimand this project has.** On the pairs where the
two orderings are *reversed*, they make opposite predictions, so the rubric must pick a side and
chance is **exactly 1/2** rather than estimated. Paired within person: population, prompt, response
set and rubric all held fixed by construction. No GPU — r41's persisted tensor already covers it.

**Result: the rubric sides with world on 0.5267 [0.4951, 0.5587]. INCONCLUSIVE.** The shuffled-rubric
arm gives 0.5183 [0.4840, 0.5527].

**And the power statement is the actual finding.** The observed half-width is **0.0318**, so
resolving δ = 0.01 would need about **14,358** reversed pairs. **The entire release contains 2,444.**
Using every one of them reaches a half-width of ~0.0242 — an answerable margin of roughly
**δ = 0.024**, and **0.17×** the data required for 0.01. So *"inconclusive"* here is a fact about the
**data**, not about the rubric, and reporting it without that number would have been the
uninterpretable kind of null this project keeps finding in other people's work and its own.

**It also bounds the planned human study.** H_fresh is 60 prompts × ≥8 raters ≈ 480 assessments,
which at the observed reversal rate yields on the order of **10²** reversed pairs — two orders of
magnitude short. The world-vs-personal contrast is **out of reach of both the release and the
protocol as designed**, and that belongs in the preregistration rather than being discovered after
collection.

## Entry 90 — the protocol specified instruments and outcomes and never said who would be recruited

Three experiments, each attacked and repaired, and none of them contained the words *recruitment*,
*eligibility*, *onboarding*, *quiz*, *compensation* or *platform*. π is one of the five layers the
research object names, and the preregistration specified every layer but that one — so it could have
been executed against a different population, under different training, and the comparison to r12
would have broken with nothing to notice it.

**The onboarding quiz is the sharp part, and it is a fork.** CoVal participants could not reach the
tasks until they passed a rubric-writing quiz teaching *objective vs subjective*, *prompt-specific vs
generic*, *both polarities*, and *weight calibration*. **Every released criterion was therefore
written by a trained participant.** "What people write as criteria" in this dataset means "what
people write **after that training**" — and the training is part of what the rubric measures.

So Experiment 1 has to choose deliberately: the PRE arm **takes the quiz too**, because S_pre asks
whether direction pre-exists the **menu**, not whether it pre-exists the **training**, and dropping
it would confound the arms with a variable the released data never varied. A **quiz-free third arm**
is worth running and is labelled exploratory, because *"the quiz is part of what the rubric
measures"* is an untested claim about π and this is the cheapest place it will ever be testable.

**Task position becomes a controlled variable, on this project's own evidence.** r31 measured the
same **933** people dropping **−179 characters [−196, −162], −53.3%** at task 6 — within-person, and
exactly at the platform's minimum-task boundary, so effort is confounded with a pay threshold. A
protocol that let position ride along would reproduce the release's own artefact and report it as a
finding. Position is now randomised within participant, recorded, and its effect reported.

**Also committed:** the released task-flow *order* (unacceptable-content check before rankings,
personal before world) for any arm claiming comparability; the same intake instrument, with achieved
demographics reported **against the release's own distribution**; and pay at or above the release's
rate, stated — $60 for survey plus 5 tasks, then $30/task with a $90 bonus, median 22 minutes per
task. **Attention is bought, and a cheaper study is not measuring the same thing.**

r31's figures were checked against its artifact before commit: 5/5 backed.

**What this entry is really about.** Nine entries of work went into naming the instrument behind
every verification step — and the protocol still had no answer to *who is in the room*. Specifying
the measurement is not specifying the measurement **program**, and π was the layer this project
named first and audited last.

## Entry 91 — the preregistration is `[unchallenged]`, and I wrote down what an adversary should find

Ten entries of design work on three experiments, all of it produced by the process that also
reviewed it. **A reviewer sampled from the weights that wrote a document can only attack what that
process already anticipated** — which is precisely why the anticipated parts read as fluent. Nothing
in `PREREGISTRATION.md` has been read by anyone but me.

I could not dispatch an independent reviewer in this session. The rule for that case is explicit:
say so, mark the work **`[unchallenged]`, never "clean"**, and pre-register what the adversary is
expected to overturn — because when one eventually runs, its findings score **my calibration about
my own work**, which is worth more than any single verdict.

`ADVERSARY_FORECAST.md` records six objections with probabilities, written before any review:

| # | objection | P(raised unprompted) |
|---|---|---:|
| 1 | δ=0.01 is stipulated in four places and connected to **no decision** | 0.85 |
| 2 | "the unmatched rate is the measurement" conflates *menu-induced* with *too vague to match* | 0.80 |
| 3 | **the τ_c symmetric design assumes both edits are the same kind of object, and often they are not** | 0.75 |
| 4 | Experiment 2's satisfaction sub-study has no n — an escape hatch dressed as a commitment | 0.70 |
| 5 | Experiment 1 has **no power calculation at all** | 0.65 |
| 6 | r60's "not answerable" assumes reversed pairs are spread evenly across prompts | 0.55 |

**Number 3 is the one that costs most, and it is an attack on the fix I was pleased with two entries
ago.** The symmetric design borrows r52's *"same kind of object"* logic, where both arms genuinely
were two token lists differing only in source. A satisfy-edit and a violate-edit usually are not:
for *"contains no factual errors"*, satisfying is leaving the text alone and violating means
inserting a falsehood. Insertion and deletion have different fluency signatures, and a participant
may be responding to the operation rather than the criterion.

**Number 5 is the plainest.** Experiment 2 carries reliability, attenuation and per-rater-count
detection floors. Experiment 3 now carries a flip-rate prior. Experiment 1 — the one addressing
S_pre, which this project calls one of the three counterfactuals that end it — has *"fixed n,
decided from a pilot"* and nothing else.

**Two predictions of survival** are recorded too, so the forecast is falsifiable in both directions
rather than a list of hedges: the world-vs-personal *documentation* finding, and the *logic* (not the
constructibility) of the symmetric fix.

**And the scoring rule matters more than the hit rate.** What counts is **what a reviewer raises
that is not on this list** — that number measures what this process cannot see about itself. A high
hit rate on six objections I wrote myself proves only that I can enumerate my own anticipated
weaknesses, which was never in doubt.

## Entry 92 — answering my own forecast, and getting the design effect wrong from the release's cluster size

`ADVERSARY_FORECAST.md` objection 5 (P=0.65): Experiment 1 has no power calculation, and the baseline
is computable from the release today. So I computed it rather than waiting for a reviewer.

**The baseline is 0.6459, not 0.5.** The POST arm writes **77.01%** positive criteria across 102,147
released ratings — the neutral point used **once**. Two independent sign-assigners with that marginal
agree ~65% of the time **by marginals alone**, so a naive test against 0.5 would have reported huge
agreement while measuring nothing but a shared tendency to write positive criteria. The
preregistration warned about this in words; it is now a number.

**And I got the design effect wrong on the first run.** I computed
`DEFF = 1 + (m−1)·ICC` with **m = 91.9**, the release's mean ratings per rater, and reported
**9.32** — which would have put the required sample at **20,482** pairs.

**Cluster size is a design parameter, not a property of the release.** An Experiment 1 participant
writes a handful of criteria, not ninety. At the planned **m = 5**, DEFF is **1.37** and the required
sample is **3,001** — I had inflated it **~7×** by importing a number from the data instead of from
the design. The ICC is the transferable quantity; the cluster size belongs to whoever runs the study.
The corrected round sweeps m ∈ {3, 5, 10, 20} and prints the release's own value beside them, marked
as *not this experiment's*.

| matched criterion pairs | minimum detectable departure |
|---:|---:|
| 400 | 0.0548 |
| 1,600 | 0.0274 |
| **3,001** | **0.02** |

**World B, and world C is ruled out.** Across the swept PRE marginal (0.50–0.95) the room above
chance never falls below **0.2569**, so sign agreement is *not* ceiling-compressed — the experiment
needs a derived n, not a different outcome variable.

**The PRE marginal is swept, never assumed.** Nobody in this release wrote a criterion before seeing
responses — which is why S_pre needs an experiment at all — so every figure here is conditional on
the swept value, and the round says so in its scope.

**The forecast is annotated, not edited.** Objection 5 now carries a note that it was self-answered
*after* the forecast was committed, and that **a scorer should exclude it from the hit rate**:
answering my own item is not evidence about what an independent reviewer would find. The forecast
text is left exactly as written.

## Entry 93 — the floor under Experiment 1's primary outcome is 87%, and I forecast this objection myself

`ADVERSARY_FORECAST.md` objection 2, at P=0.80: promoting the PRE/POST unmatched rate to a primary
outcome conflates *"this criterion could only arise after seeing responses"* with *"this criterion is
too woolly to match anything"*. The forecast said a within-arm baseline would settle it. r62 measures
that baseline on the release.

**Two people who saw the same four responses, on the same prompt, under the same protocol:**

| Jaccard threshold | fail to match each other | cross-prompt null | excess |
|---:|---:|---:|---:|
| 0.10 | **53.3%** | 93.8% | +40.4 |
| **0.20** | **87.3%** | 99.6% | +12.3 |
| 0.30 | 96.9% | 100.0% | +3.1 |

Measured over 938 prompts carrying two or more write-in authors. **Even at the most lenient
threshold, more than half of criteria match nothing another same-condition author wrote.**

**The cross-prompt null is what makes the number mean anything.** At 0.10 the matcher separates
same-prompt from different-prompt criteria by 40 points, so it is tracking prompt-specific content
rather than matching generic language to everything. Without that arm a high unmatched rate would be
indistinguishable from a broken matcher.

**Objection 2 is upheld and the design changes.** The unmatched rate is now reported as an **excess
over a within-arm floor measured in the same study with the same human matchers** — PRE against PRE,
POST against POST — and the raw rate is never quoted without both. A design reporting the PRE/POST
rate alone would be reporting mostly the idiosyncrasy of free-text criterion writing and calling it
menu-induced construction.

**Two forecast items in two entries, both self-answered, both excluded from the hit rate.** Entry 92
answered #5, this one confirms #2, and both are annotated in the forecast as raised-by-me with the
forecast text left unchanged. That leaves four unexamined — and the number that will matter is still
**what a reviewer raises that is not on the list at all**.

**The absolute figure is matcher-relative and says so.** A lexical Jaccard counts two criteria
meaning the same thing in different words as unmatched, so 87.3% is a lower bound on agreement. What
survives that caveat is the *comparison*: the same matcher at the same threshold applied to both
arms, which is why the floor is usable even though the matcher is not trustworthy alone.

## Entry 94 — a forecast item examined and found NOT to bite, which is what makes the forecast mean anything

`ADVERSARY_FORECAST.md` objection 6, P=0.55, written by me: r60 scales its half-width by √n to
conclude the world-vs-personal contrast is unanswerable from this release, and that step assumes
reversed pairs are spread evenly across prompts. If they concentrate, the effective n is below the
pair count and the published requirement is **too small**.

**Checked. It does not bite.**

| | |
|---|---|
| design effect implied by r60's own cluster bootstrap | **1.499** (half-width 0.03178 vs binomial 0.02595) |
| uniform-redistribution null | **0.886** |
| prompts contributing reversed pairs | **238 of 250**, mean 5.97, max 21 |
| concentration | top 26% carry half, top 54% carry 80% |

Three things follow. **The clustering was already inside the interval the projection scaled from** —
it was not omitted and then re-derivable, it was in the published half-width all along. **The
inflation is a property of the data, not the estimator**, because redistributing the same pairs
uniformly returns a design effect of 0.886. And **the growth mode settles it**: the release's
remaining reversed pairs live in the other 718 prompts, so scaling from 1,422 to 2,444 adds
*prompts* at a similar cluster size and holds DEFF at 1.499 — precisely the condition √n needs.

Had the extra pairs come from more raters on the **same** prompts, the mean cluster would double and
DEFF would rise to **2.099**, inflating the requirement by **1.40×**. That is the version of the
objection that would have bitten, and it is not the version the release offers.

**This is the entry I would have been tempted to skip.** It confirms a number I already published,
and produces no correction. But a forecast in which every item is upheld is not a forecast, it is a
list of things I already believed — and objection 6 was worth raising precisely because I could not
tell from the armchair which way it would go. **Recorded as negative, excluded from the hit rate,
forecast text unchanged.**

Three of six forecast items are now self-examined: **5 answered, 2 upheld, 6 not upheld.** All three
excluded from scoring, because what an independent reviewer would find is still entirely unmeasured
— and the number that matters remains **what they raise that is not on the list**.

## Entry 95 — I wrote that no data could anchor δ, and the anchor was in r06 the whole time

`ADVERSARY_FORECAST.md` objection 1, P=0.85, the highest on the list: every experiment reports
equivalence at δ = 0.01, the stipulation is flagged in four places, and **none of them says what
decision changes at 0.01 that does not change at 0.02**. When I closed the last entry I wrote that
this was *"the one no data can settle"*. That was wrong, and it was wrong in the laziest available
way — I had not looked.

**The decision is which aggregation rule to use.** The release explicitly invites it, calling
CoVal-core *"an invitation for others to develop and validate better synthesis and aggregation
methods for this format"*. r06 ran five:

| | accuracy | vs no-compression |
|---|---:|---:|
| utility | 0.6575 | **+0.0067** |
| constituency | 0.6567 | **+0.0070** |
| majority | 0.6552 | +0.0044 |
| conflict-aware | 0.6446 | −0.0058 |
| consensus | 0.6387 | **−0.0113** |

They span **0.0188**, and consensus ties random selection (0.6384). So **δ = 0.01 is 53% of the
entire best-to-worst distance across every aggregation rule anyone has proposed**, and larger in
magnitude than three of the five rules' own effects against no-compression.

**That fixes the reading of every equivalence claim in the package.** *"Equivalent to zero at
δ = 0.01"* now means *"smaller than half the swing you get from changing the aggregation rule"* —
a decision somebody actually makes, with a number attached, instead of a threshold chosen because it
is round. The margin was never arbitrary; it was **unjustified**, which is a different and fixable
thing, and four rounds of flagging it as *stipulated* had been standing in for the fix.

**And the row I went to for the anchor was wrong.** It read *"four rules span 1.9 points"*. The
artifact holds **seven** entries — five aggregation rules plus `no_compression` and `random_k4`
baselines — so it is **five** rules, spanning 0.0188; the 1.9 points was the span *including* the
random baseline. Corrected, with the count and both spreads stated.

**Four of six forecast items now self-examined** — 1 answered, 2 upheld, 5 answered, 6 not upheld —
all excluded from the hit rate. Objections 3 and 4 remain, and 3 is the one I still expect to cost
the most.

## Entry 96 — sizing the escape hatch found it could never have worked in the first place

`ADVERSARY_FORECAST.md` objection 4, P=0.70: Experiment 2's satisfaction sub-study is *"if that
sub-study is not run, the primary result is reported as…"* — no n, no power, no sampling frame, so it
can be skipped and the headline merely reworded. A caveat wearing the costume of a commitment.

**Sizing it exposed a deeper defect than the objection named.** The sub-study was one-armed: humans
adjudicate satisfaction on **fresh** (criterion, response) pairs, yielding a human-vs-judge agreement
rate. And that number has **nothing to be compared against** — **the release ships no satisfaction
labels at all**, which is the entire reason r04 exists to rebuild them. The judge's agreement with
humans is unmeasured on **original** responses too. A lone fresh-arm rate would have been a number
with no referent, and I had written it into the protocol as the thing that would rescue the headline.

**So it is two-armed now, and the estimand is a difference:** `Δ_sat` = agreement on **original**
minus agreement on **fresh**, in which the judge's unknown absolute accuracy cancels.

| base rate | d=0.05 | d=0.10 | d=0.15 |
|---:|---:|---:|---:|
| 0.60 | 2,099 | 531 | 237 |
| 0.70 | 1,884 | 488 | 223 |
| **0.80** | 1,497 | **402** | 189 |
| 0.90 | 939 | 273 | 137 |

**402 pairs per arm, 804 total** at base 0.80 and d=0.10, α=0.05, power 0.80, design effect 1.37 from
r61. The base rate is **unmeasured and swept** — 273 to 531 per arm across 0.60–0.90 — so the pilot
estimates it before n is fixed.

**And the escape hatch is closed by a rule, not a promise.** If `Δ_sat` is significantly positive
**and** exceeds the observed change in the own-minus-reference gap, the transport failure is
attributable to the **satisfaction layer**, and H_fresh's primary result is reported **UNVERIFIED for
transport** — not annotated, not reworded. That is the difference between a commitment and a caveat:
a stated outcome that invalidates rather than qualifies.

**Five of six forecast items self-examined** — 1 answered, 2 upheld, 4 answered, 5 answered, 6 not
upheld — all excluded from the hit rate. **Only objection 3 remains**, the τ_c edit-symmetry problem,
and it is the one I expect to cost the most because the fix is not writing but constructibility.

## Entry 97 — the last forecast objection, upheld at 18.62% — and my own check caught the round's regex over-firing

`ADVERSARY_FORECAST.md` objection 3, P=0.75, the one I predicted would cost most: τ_c's symmetric
design borrows r52's *"same kind of object"* logic, but a satisfy-edit and a violate-edit often are
not. r65 bounds how often.

**18.62% of CoVal-core criteria carry a deontic prohibition** — *"do not provide step-by-step
tactics"* — so satisfying them is an **absence** and violating them a **presence**. The two arms must
insert categorically different content (a refusal against the prohibited material), which is exactly
what the design assumes they are not.

**The first run said 21.31%, and this package's own check caught why.**
`readme_row_carries_the_verdict` flagged that r65's scope sentence — admitting the regex fires on
*"not only… but also"* constructions — had no echo in the README row. Following the flag found 105
matches that are affirmative criteria with an incidental negation: *"Explain that stepping on cracks
has **no** effect"*, *"Make clear that AI is **not** a substitute"*. Those are prescriptions. The
defensible figure is the **strict deontic 18.62%**; the loose 21.31% is an over-count, and both are
now published side by side.

**The floor is squeezed from both directions and says so.** Prohibitive surface ⇒ asymmetric, so it
is a floor. Affirmative surface ⇏ symmetric, so it is *only* a floor. Neither bound is tight.

**And the null turned into a finding.** `coval_full`, which the compiler has **not** polarity-
rewritten, carries **12.85%** — so **core is 1.45× as prohibitive as the raw set it was compiled
from**. r44's +0.0733 polarity rewrite, core's single largest source of advantage, changes **weights
to positive and leaves prohibitive phrasing in place**, increasing its share. **Positive weight is
not affirmative wording**, and I had been reading r44's "rewrites all rubric items to have positive
weight" as though it were.

**A hand-written clause had to go too.** The verdict said the two shares were *"essentially the
same"* — true at the loose threshold, false at the strict one (18.62% vs 12.85%). Replaced with a
computed ratio, which is what the no-hand-written-conclusions rule is for.

**Design consequence:** τ_c runs a **per-criterion constructibility screen first**, criteria failing
it are reported **τ_c NOT IDENTIFIED** rather than estimated, and the exclusion rate is a headline
with **18.6% as the floor it must clear**.

**All six forecast objections are now self-examined:** 1 answered, 2 upheld, 3 upheld, 4 answered,
5 answered, 6 not upheld — every one excluded from the hit rate. **What an independent reviewer
would find remains entirely unmeasured**, and that was always the number that matters.

## Entry 98 — the project's largest single effect is an upper bound, and the code said so in a comment nobody carried forward

r65 ended by showing that *positive weight is not affirmative wording*. That sent me back to the
number that phrase is attached to: r44's **+0.0733**, the largest single increment in this package
and the answer to queue item 6.

**`rounds/r44_compiler_lineage/run.py:112` states the limitation in its own comment:**

> *"C1 polarity rewrite. The text rewrite cannot be simulated; its EFFECT can: a criterion carrying a
> negative weight becomes a positively-phrased criterion whose satisfaction is the complement."*

and implements it as `s1 = -1.0 if mean_train_rating < 0 else 1.0`. **The stage applies the crowd's
rating sign numerically**, on rater-disjoint folds.

**That is a different information condition from the artifact it stands for.** The reconstruction is
*handed* the polarity at scoring time. The real CoVal-core has no such channel: it must encode
polarity **in rewritten words** and rely on a judge that never sees a rating to recover it. So
**+0.0733 measures what having the polarity is worth, and bounds from above what putting it into
prose can achieve.**

**r65 supplies the reason to think the gap is real.** If the rewrite converted prohibitions into
affirmations, the judge's job would be easy. It does not: **18.62%** of core criteria still read
*"do not X"* — **more** than the 12.85% in the un-rewritten full set. The rewrite changes weights and
leaves the wording, so the polarity the judge must recover from text is exactly the polarity that
was hardest to phrase away.

**What was wrong was nothing, and that is the point.** r44's scope field is correct
(*"RECONSTRUCTION, not decomposition"*), the README row carried it, and the code comment is exemplary.
The defect is that **a limitation stated in a code comment is not stated to a reader** — three
documents quoted +0.0733 as *the polarity rewrite's* contribution, and none said the stage never
rewrote anything. Now stated in the README table, the round row, and the preregistration, and
registered so it cannot drift back.

**This is the same shape as entry 73**, where six rounds' bounds sat in `caveat` and `note` fields no
instrument read — except here the bound was one level further down, in a comment, where no instrument
in this package looks at all.

## Entry 99 — two versions of a check failed their controls before one worked, and the second failure is the useful one

Entry 98 found a bound stated in a code comment that reached no reader. This builds the instrument
for that class — and the first two attempts could not have found the case they were built for.

**Version 1 failed a planted positive control.** It flagged a source line when its distinctive words
overlapped the README's prose about that round by fewer than two. Planting a bound in r59 — *"a
stand-in for the quantity humans would supply and cannot be recovered from any judge output"* — did
**not** flag, because `flip`, `judge` and `rate` appear in r59's row for unrelated reasons.

**Version 2 failed a retrospective control, and that one is the lesson.** It ranked lines by how
little of their vocabulary reached the README. Rebuilding the **pre-fix README from git** and
re-running put `r44:110` — the exact line the check exists for — at **rank 30 of 33**. It would have
been invisible.

**Why, and it generalises:** the comment says *"polarity rewrite"*, and so does the README. **A bound
stated in the same words as the finding it bounds cannot be told apart from that finding by counting
words.** Vocabulary overlap measures topic, and a bound shares its subject's topic by definition —
that is what makes it a bound rather than a digression.

**Version 3 scores the matched BOUND PHRASE** — *"cannot be simulated"*, *"upper bound"*,
*"stand-in for"* — not the line's vocabulary. Against the pre-fix README it flags r44; against the
current one it does not. **The instrument would have found what it was built for**, which is the only
control that settles a check written after its motivating case was already fixed.

**13 of 33 bound phrases are absent from the README's prose about their round.** The three lowest on
the first pass were instructive false positives, and each states a limitation *together with its
repair*: r23's *"the parameters are not identified … but the FITTED VALUES are, and only those are
used"*, r31's confound followed by a section headed *"The repair"*, r07's upper bound on a figure the
README does not quote. **No mechanical rule separates a hidden bound from a stated-and-repaired one**,
so this reports and never gates.

**Both dead versions are documented in the file rather than deleted.** A check's failure modes are
the part a future reader most needs, and they are invisible once the working version is the only one
on disk.

## Entry 100 — I documented the "untaken branch" false positive and then fell for it on the next case

Triaging entry 99's 13 flags. All 13 are false positives, in five classes — and the way I nearly
mishandled one is worth more than the triage.

**r29 looked like the worst defect of the session.** Its source builds a verdict reading
*"UNVERIFIED — THE DIAGNOSTIC IS UNFIT … their concordance on the fresh set is therefore two
uninformative scorers agreeing … an instrument that failed its positive control, which is silence,
not an acquittal."* The README row says **"stable"**. A round declaring itself unfit, presented as
having produced a result — I had the retraction half-written.

**It is a branch that never runs.** `anchor_ok = min(anchor.values()) > 0.55`, and the stored anchors
are **0.7098** and **0.6527**. The gate passes, the UNVERIFIED branch is skipped, and the stored
*"GOLD IS STABLE OFF-DISTRIBUTION"* verdict is the correct one. The results file is also **newer**
than the code, so nothing was stale.

**And I had identified this exact class two commands earlier**, from r11's `"WEAKENED: the
independent backbone cannot distinguish…"` — likewise a branch of a computed conclusion that did not
fire. I named the failure mode and walked into it on the next case, because the r29 text was
*dramatic* and the r11 text was not.

**Grep shows you source, not execution.** A conclusion string assembled inside an `if` is not a
claim the round makes; it is a claim the round would make under a condition. **Check which branch
executed before reading source text as a verdict.**

**The five classes, recorded in the check for the next triage:**

| | |
|---|---|
| stated with its repair | r23, r31, r07 |
| quoted in order to refute | r02 |
| **untaken conditional branch** | **r11, r29, r46** |
| design rationale or motivation | r22, r41 |
| already in the row, different words | r54, r62, r65 |

**Precision on the current corpus: 0 of 13.** One demonstrated true positive (r44, retrospectively)
and thirteen false ones. That is a **tripwire for future drift, not a source of findings**, and the
number now prints beside the output so nobody reads thirteen flags as thirteen problems.

## Entry 101 — the round that best exemplifies this project's discipline has no code in the repository

Auditing the README's headline found *"57 rounds establish that"* against 65 round directories. Chasing
the count found something worse: **`rounds/r56_semantic_selectivity/` contains one file,
`PREDICTION.md`, and has contained exactly that in every commit it has ever appeared in.** No `run.py`,
no results.

**r56 is the round I would have held up as the model.** A prediction committed to git *before* the
held-out number existed (`5cb7426`), then an honest **NOT REPLICATED** (`664c568`):
+0.1806 [+0.0708, +0.2880] on discovery, **+0.0198 [−0.1196, +0.1592]** held out, against a
preregistered [+0.06, +0.30] with a CI excluding zero. It is also the only round whose code was never
committed, and **its CI bounds 0.1592 and 0.2880 appear in no artifact in this package** — both are
4-decimal values, where entry 81's chance-match null is low, so that absence is real.

**RETRACTIONS entries 55 and 56 rest on it.** A published analysis depends on a number whose
computation exists in a commit message and prose.

**r66 tries to recompute it from the persisted tensors, and cannot.**

| | recomputed | published | |
|---|---:|---:|---|
| discovery | **+0.0365** [−0.0916, +0.1651] | +0.1806 | diverges by 0.144 |
| held out | **+0.0985** [−0.0188, +0.2124] | +0.0198 | diverges by 0.079 |

**Neither arm reproduces, so by the null r66 declared before running, it says nothing about whether
r56 was correct — UNVERIFIED, not overturned.** A reconstruction that does not share the original's
method cannot refute it, and building that rule into the world classification before seeing the
numbers is the only reason I can say so cleanly now.

**r56's conclusion survives anyway, by a different route.** The recomputed held-out CI
**[−0.0188, +0.2124] includes zero**, so the preregistered criterion fails under this method too.
The *number* is unverifiable; the *NOT REPLICATED* holds.

**A side finding worth its own line:** r46's tensor is persisted under **r41's** results directory.
The round that wrote it is not the round that names it, nothing in the package records where a tensor
lives, and I found it only by listing the directory after r66 refused to run.

**What this costs.** This project's answer to *"why should anyone believe you"* is that every number
has an artifact and every artifact has code. **One round breaks that, and it is the one whose
discipline I would have cited as proof.**

## Entry 102 — r56's code is unrecoverable, so its interval is marked and the blind spot is closed

Entry 101 found r56 has no code in the repository. Recovery first, marking second.

**Unrecoverable, and the search settles it.** `git log --all -S"semantic_selectivity"` returns
exactly one commit — my own, from entry 101. `git log --all -S"selectivity" -- 'rounds/**/*.py'`
returns that plus r55's, which computes a **different** quantity (containment overlap, not judge
satisfaction). The computation was never committed in any form, under any round.

**So the marking.** RETRACTIONS entry 56 lists *"r41's criterion-space NN, r54 and r56's held-out
value"* as conclusions resting on underpowered correlations. That use quotes r56's **interval**,
which has no artifact behind it. Marked in place: *its conclusion survives an independent method; the
interval quoted here does not, and should not be used as a measured quantity.* Registered so it
cannot be quoted unqualified again.

**Entry 56's other two uses of r56 are fine and stay unmarked** — they cite that it *failed its
preregistered interval*, which is a statement about a comparison r66 independently reproduces the
direction of. **The conclusion and the number have different evidential status and only one needed
touching.**

**And the blind spot is closed where it can be seen.** Every enumeration in this package starts from
results files, so a round with no code and no results is invisible to all of them —
`every_round_reaches_the_readme` is the only check that walks **directories**, so the report lives
there:

```
round directories: 66   with a non-smoke result: 64
⚠ 1 round(s) contain NO .py FILE: r56_semantic_selectivity
⚠ 2 round(s) have no non-smoke result: r39_feature_cache, r56_semantic_selectivity
```

r39 is legitimate — it caches representations as `.npz` and analyses nothing, which its own README
row says. r56 is not.

**The general shape, worth naming once.** An instrument that enumerates from artifacts cannot see a
missing artifact. Every check here starts from `results/**/*.json` because that is where the claims
are — and the failure mode that produces is exactly **a claim with no artifact**, which is the one
thing that enumeration is structurally blind to. It took auditing a stale round count in a headline
to find it.

## Entry 103 — the headline led with a point split for a quantity that spans twenty-fold, and the span I cited was mis-attributed

Queue item 1 is the [NOW] task and says the values-vs-non-values contrast **must never be a headline
again**. The nouns were corrected long ago. The **structure** was not: the Headline opened by
splitting 18.6 points into *"**7.9** are prompt-specific criterion content and **10.7** are generic
response quality any rubric earns for free"* — a point decomposition, presented before any scope.

**The scoping did arrive, one paragraph later, and it was too narrow.** The section said the floor
is a choice moving the number **2.47×** and gave **27%–67%**. That is the **floor dimension alone**.
The package also establishes a **judge** dimension, and with an interval in every cell r30 gives
**3.2%–65.8%** — a twenty-fold span, not a two-fold one.

**So the lead now states what is robust and what is not.** The *ordering* — own 0.686 > unrelated
0.607 > length 0.532 > chance 0.500 — holds across every judge and floor tested. The *split* is one
cell of a grid. And **7.9 and 10.7 are not two quantities, they are one cell**: the second is not
identified as "generic quality" by anything measured here, since r59 finds criteria borrowed from
other prompts are just as concordant about these responses as a prompt's own.

**And the number I reached for was mis-attributed, which I found by checking before committing.**
I wrote *"the judge family moves it **2.13×** ([r22])"*. **2.13 is not in r22's artifact.** It is
derived from **r30's** shares: 53.8% ÷ 25.3% = 2.1265. The README's r22 row had carried the same
mis-attribution — *"a 2.13× judge span"* — since long before this entry. Both now say where the
number comes from and that r22 does not store it.

**This is the third instance of one shape**: r30's prompt-specific shares living inside r22's tables
(entry 82), and now r30's derived judge span credited to r22 twice more. **r22 measures accuracies;
r30 measures shares.** Every span in this package is r30's, and the row that reads most naturally as
the source is the wrong one.

Coverage of `readme_agrees_with_results` is now **59%**, up from 8% when this session began.

## Entry 104 — "polarity carries roughly half" cited the round that corrects it

The layer table's **R** row and the preregistration's closing list both said *"post-ranking polarity
carries roughly half the above-chance concordance ([r32], [r36])"* — citing **r36** for a figure
**r36 exists to correct**.

| | value | share of the 18.6 above-chance points |
|---|---:|---:|
| sign added **last to text alone** (r32) | **+0.0876** | **47%** |
| Shapley value over **all 16 coalitions** (r36) | **+0.0214** | **12%** |

r36's own verdict: *"r32's +0.0876 was the value of adding sign LAST to text alone — **one path
through the lattice, not the channel's average worth**."* Its README row says so too — *"r32's
sequential split **over-attributed** to polarity"*. **The correction was published in the row and
never reached the two summaries that sit above it.**

**"Roughly half" is the maximum over entry orders**, not the channel's contribution. Four-fold
apart, and the summaries picked the larger and credited both rounds for it.

**This is entry 79's shape, third occurrence.** There it was compatibility selection: the row quoted
*"+0.0149 better than random"* and omitted *"−0.0181 cost"*. Here it is polarity: the summaries quote
the path-maximal +0.0876 and omit the order-averaged +0.0214. **Both times a two-number result
reached the top of the document as its flattering half, and both times the corrected figure was
already sitting one table lower.**

**Why `corrections_propagated` did not catch it:** entry 83 built that check to stop a correction
landing in one document and not another — and it only knows what is **registered** in it. r36's
correction of r32 was made long before the registry existed and was never added. It is registered
now, which is the only part of this that generalises: *registering is part of correcting*, stated in
the check's own output since entry 83, and still not done for a correction made before it.

## Entry 105 — a missing import plus a bare `except Exception` produced a clean zero

Entry 104's defect — r36's verdict correcting r32, never reaching the summaries — is invisible to
every mechanism in `corrections_propagated.py`. The **registry** only knows what someone added to it,
and entry 84's **RETRACTIONS sweep** only sees corrections written as retraction entries. That one
lived in one round's verdict, about another round.

**Sweeping all 65 verdicts finds exactly four such sentences**, and three are corrections this
session already handled (r36→r32 in entry 104, r66→r56 twice in 101/102). The fourth is r15's
*"the two are different questions and r15 neither confirms nor refutes r12"* — already carried in
r15's README row since entry 72, and r15 and r12 are never co-cited anywhere else. **The class is
small and currently clean**, which is why the detection was folded into an existing check as a
standing list rather than becoming a thirteenth file.

**And the folded version reported 0.**

My scratchpad sweep found 4. The same loop, run inline with the module's own compiled constants,
found 4. The module's own function returned **0**. The constants were right, the regexes fired on
the exact sentence, 238 files were reached.

**`json` was never imported at module level.** The function calls `json.loads` inside
`try: … except Exception: continue`. Every one of the 238 files raised `NameError`, every one was
swallowed, and the check printed a confident **zero** — *"cross-round corrections stated in verdicts:
0"* — which reads exactly like a clean result.

**A bare `except Exception` around a body that can raise NameError converts a broken function into a
passing one.** The narrowed version catches `OSError` and `json.JSONDecodeError` — what a bad *file*
raises — and lets a broken *function* crash, which is the only way the failure becomes visible.

**It survived because the answer was plausible.** Zero cross-round corrections is a perfectly
believable number for a package where verdicts mostly discuss their own round. I only caught it
because I had a scratchpad sweep from ten minutes earlier that said 4 — **the check was validated
against a prior run, not against a control**, and without that accident it would have shipped.

## Entry 106 — sweeping the hazard entry 105 named: 21 bare excepts, four of the dangerous shape

Entry 105's bug was a missing import swallowed by `except Exception`. The sweep for the same shape
finds **21 bare `except Exception:` / `except:` sites**, in four classes:

| class | sites | hazard |
|---|---|---|
| **file-parsing loops that skip** | 4 | **the exact bug** — one broken name silently empties the population |
| optional `from covalx.frozen import append_to` | 9 | deliberate optional dependency; swallows errors *inside* `append_to` too |
| subprocess/git wrappers | 3 | legitimately broad; git fails many ways |
| manifest path/format helpers | 5 | mild |

**The four dangerous ones are narrowed** to `(OSError, json.JSONDecodeError)` — what a bad *file*
raises — so a broken *function* crashes instead of skipping.

**And each now counts what it skipped.** Narrowing fixes the cause I found; counting reveals causes I
have not. A parse failure prints `⚠ N results file(s) could not be parsed and were SKIPPED`, verified
by planting a corrupt JSON and watching it appear, then removing it and watching it go.

**One site was worse than the others and the sweep nearly missed it.**
`readme_agrees_with_results` used `except Exception: **pass**`, not `continue` — so my pattern did not
match and the first pass skipped the file entirely. `pass` is the more dangerous of the two: it hides
the file **and leaves an empty pool entry behind**, so the round looks present with no values in it.
A check whose population silently empties one round at a time reports "rounds with results: 55"
either way.

**One check exits 1 by design and that is not a regression.** `verdict_cites_its_own_contrasts`
returns 1 whenever any round cites none of its own significant contrasts — seven do (entry 80). It
had not been in my batch list, so adding it here surfaced its designed state as if it were a failure.
Recorded so the next person reading a suite run does not chase it.

## Entry 107 — "exhausting the alternatives" was asserted for 64 rounds and never enumerated

The README's closing claim is that **none of the three counterfactuals is computable from this
release, and 64 rounds establish that by exhausting the alternatives rather than by assertion**.
That sentence is itself an assertion unless the alternatives can be listed. **Nothing listed them.**

**They enumerate to thirteen.** Every mechanism ever proposed for r12's inversion, its round, and its
outcome — now a table in the README. Mechanical enumeration was not enough to build it: only **8
rounds name r12** in a verdict or scope field, while r40, r41, r50–r52 and r59 test mechanisms for it
without saying so there. The ledger had to be assembled by reading, and each row checked against its
artifact.

**All 28 numbers in it verify: 0 unbacked.**

**The ledger's own limit is the first thing in it.** A list bounds exhaustiveness **from below** and
can never prove it — no enumeration shows that no other mechanism exists. What the table shows is the
set that was *proposed and tested*, which is a weaker and honest claim than "exhausted".

**And it makes visible something the scattered rows did not.** Five of the thirteen — rows 3, 4, 5,
10, 12 — are **correlational**, and r57 measured the per-prompt outcome's split-half reliability at
**0.302 / 0.422**, so any mechanism with a true correlation below ≈**0.2** is invisible to all of
them. Those five say *"not detected above the floor"*, not *"absent"*. The other five refutations
(rows 1, 2, 6, 11, 13) rest on **tightly-bounded contrasts** and do not inherit that limit.

**That distinction existed in entry 55 and had never been applied per-mechanism.** Reading the rounds
one at a time, "refuted" looks uniform; in a table with the floor stated once at the bottom, it
splits five-and-five. **The strongest thing this project can say — "nothing explains the remainder" —
is five real refutations and five undetected-below-a-floor, and it now reads that way.**

## Entry 108 — one shared detection floor hid a 1.35× spread, and the round I did not build is the point

Entry 107's ledger carried a single caveat: *"a mechanism with a true per-prompt correlation below
≈0.2 is invisible to all of them."* Each correlational row has its own n and its own interval, so
each has its own floor.

**Computed from each row's published CI:**

| row | half-width | disattenuated floor (rel 0.422 → 0.302) |
|---|---:|---:|
| 3 · generic distance (r40) | 0.0988 | 0.152 → 0.180 |
| 4 · criterion-space support (r41) | 0.1010 | 0.155 → 0.184 |
| 5 · spread loss, held out (r46) | 0.1175 | 0.181 → 0.214 |
| 10 · overlap transfer (r54) | 0.1336 | 0.206 → 0.243 |

**A 1.35× spread**, and "≈0.2" sits mid-band. ⚠ **r41's figure was wrong in the first version of
this entry and of the ledger**: I took `raw[0]`'s interval (half-width 0.1080) when the row cites
`D_hull_violation`, which is `raw[1]` — half-width **0.1010**, floor 0.155 → 0.184. Caught by the
same per-round CI verification I ran to confirm the table, minutes after committing it. r54 could not have detected a true correlation below
**≈0.21 even optimistically** — so *"the overlap channel does not explain r12"* is a weaker statement
than the neighbouring rows' refutations, and the shared caveat made all four read alike.

**Every figure is a LOWER bound on the true floor**: it takes the predictor as perfectly reliable,
which none of them is. The real floors are higher, by an unmeasured amount.

**And the decision not to build a round for this is the entry's actual content.** I had r67 scoped —
per-mechanism detection floors, claim card, positive control. Then I computed the band and found it
**confirms the existing caveat rather than changing it**: 0.15–0.24 around a stated ≈0.2. A round
would have produced an artifact, a verdict, a README row and a retraction entry, to say what four
lines of arithmetic on already-published intervals say.

**The cost meter has to run on instrumentation too.** This session has added nine rounds and two
checks, and the discipline that justifies them is the same one that has to be able to say *no* — a
measurement whose result is known in advance to agree with what is already written is Closure with a
ceremony attached. The band is now in the ledger, derived in place, with its own bound stated, and
there is no r67.

## Entry 109 — the term entry 108 left out was worth 1.23×, and r54's refutation could not have seen r = 0.3

Entry 108 published per-row detection floors and stated plainly that each takes the **predictor** as
perfectly reliable, making every figure a lower bound. It also declined to build a round whose answer
was already known. **This is the round whose answer was not**: if the predictors were as noisy as the
outcome, those five refutations would rule out almost nothing.

**Measured: Spearman-Brown reliability 0.657**, from splitting each prompt's criteria 2-2 and
recomputing the quantity on each half — spread loss +0.6512, criterion-space geometry +0.6629, over
241 prompts with 9 excluded for having fewer than four criteria. Controls first: self-correlation
**1.0000**, one half against a shuffled other half **+0.0992**.

**Neither extreme world.** Not A (>0.7, floors barely move), not B (≈0.35, floors double). **World C:
floors multiply by 1.23×.**

| row | published as a lower bound | measured |
|---|---:|---:|
| 3 · generic distance (r40) | 0.180 | **0.222** |
| 4 · criterion-space support (r41) | 0.184 | **0.227** |
| 5 · spread loss, held out (r46) | 0.214 | **0.264** |
| 10 · overlap transfer (r54) | 0.243 | **0.300** |

**r54 could not have detected a true correlation of 0.30.** Its verdict — *"the mechanism is real and
does not explain r12"* — is a real result about a real causal channel, and what it rules out is
mechanisms above 0.30, not mechanisms in general. That row has been the strongest-sounding refutation
in the ledger and is the weakest test in it.

**What r67 does not measure, and says so.** r40's predictor is an embedding distance and the
embeddings were never persisted, so its reliability is **unmeasured**; its corrected floor borrows
the mean of the two that could be measured. That is an assumption wearing a number, flagged in the
round, the row and the ledger.

**Entry 108 declined a round because its answer was known; this one earned its place because it was
not.** The distinction is the whole content of both entries: 0.657 was not predictable from anything
already written, and it changed four published figures.

## Entry 110 — the 1.23× correction was itself mis-applied to a predictor with nothing to split

Entry 109 measured predictor reliability at **0.657** by splitting each prompt's criteria 2-2, and
multiplied all four ledger floors by 1.23×. **That transfer is wrong for one of them.**

**r40's predictor is an embedding distance.** It has no criteria to split — it is one number per
prompt from a deterministic computation over response text. A criteria-split reliability measures how
much a quantity moves when you average a different handful of judge scores; there is no such handful
here, so the 0.657 does not describe it and applying it inflated r40's floor from 0.180 to 0.222 on
no evidence.

**What r40 does have is three unrelated pretraining runs, and they agree.** Nearest-neighbour
correlates with the attribution drop at **−0.1324, −0.1428, −0.1011** — same sign, **SD 0.0217** on a
mean of −0.1254, a coefficient of variation of **0.173**. That is a consistent instrument, which
points the other way: r40's true floor sits nearer the **0.180** end, and its refutation of the
generic-distance mechanism is *stronger* than entry 109 left it.

**So it is a range now, 0.180–0.222**, with the upper bound retained only because predictor
reliability is genuinely **not measurable from persisted data** for this row — the embeddings were
never saved. A range with both ends earned beats a point estimate with one end assumed.

**And the SD was wrong in the first draft of this fix.** I wrote 0.0173 into two places in the README
before computing it; `np.std(ddof=1)` gives **0.0217**. Corrected before the commit, by running the
number I had already asserted.

**The pattern, twice in three entries.** Entry 108 took `raw[0]`'s interval where the row cited
`raw[1]`. This one took a reliability estimate from two predictors and applied it to a third of a
different kind. **Both are the same move — carrying a number across a boundary it does not cross —
and neither was caught by any check, because both produce perfectly plausible values.**

## Entry 111 — the defect in entries 108 and 110 is not mechanically detectable, and I measured that before building the check

Entries 108 and 110 share one shape: **a number computed correctly and applied to the wrong object.**
`raw[0]`'s interval where the row cited `raw[1]`; a criteria-split reliability applied to an embedding
distance. Neither was caught by any check. The obvious response is a thirteenth check, and entry 108's
own lesson is that instrumentation needs a cost meter, so I measured first.

**The candidate:** a derived number should NAME its derivation, as entry 82 started doing
(*"2.13×, derived as 53.8 ÷ 25.3 from r30's shares"*). Mechanically: unmatched in every pool **and**
no derivation phrase nearby.

**What it would flag: 82 numbers.** Scanning them, most are model version strings (`3.5` from
`qwen3.5`, `-3.5` from `phi-3.5-mini`), prompt counts, and derived values whose explanation sits in
the adjacent block rather than the same one — the row-splitting from entry 69 puts each table row in
its own block, so a table's explanatory paragraph is never in the row's block.

**And it would have caught neither motivating case.** Entry 108's error was choosing `raw[0]`'s
half-width over `raw[1]`'s: **both are derived, both unmatched, and the check flags them
identically** — it cannot say which interval the row was about. Entry 110's `1.23×` and `0.222` are
likewise unmatched, and the flag would carry no information about whether the multiplier belonged to
that predictor.

**So: 82 flags, near-zero precision, and zero recall on the two cases it was designed for.** Not
built.

**What actually caught both** was running the number before asserting it — entry 108's r41 half-width
fell out of a verification loop I ran to confirm the table I had just committed, and entry 110's SD
fell out of computing a figure I had already written down. **That is a practice, not an instrument**,
and this package now has twelve instruments and one demonstrated way of catching this class.

**Recording a check I did not build, with its measured miss rate**, because the alternative is
building it, watching it flag 82 things, and adding it to the suite as evidence of diligence.

## Entry 112 — the section explaining why to trust this package was the stalest text in it

*"What is unusual here"* is where a reader goes to decide whether the apparatus is real. Every
quantitative claim in it was wrong.

| it said | actual |
|---|---|
| RETRACTIONS has **twelve entries** | **120** — 54 table rows, 66 written out, numbered to 111 |
| `assurance/` freezes **thirteen claims** | **20** |
| **four fail** | **6 fail**, 3 marginal, 11 hold |
| a bullet list of controls ending at **r12** | 67 rounds exist |

**Ten times understated on the first, and every number moved in the direction of a smaller, tidier
package than the one that exists.** Not one of them was caught by any check, because no instrument in
this repository reads the section where the repository describes itself — every check enumerates
rounds, results, verdicts or watched documents, and this is prose about the *apparatus*.

**And two adversary documents had drifted into one description.** `assurance/ADVERSARY_BRIEF.md` is
the mandate — what to attack. `ADVERSARY_FORECAST.md` is the scoring sheet — six objections with
probabilities committed before review. The section described the first as containing the second's
contents. Both are now named with their distinct jobs, and the forecast's status is stated: **all six
self-examined, all six excluded from the hit rate, and what matters is what a reviewer raises that is
not on the list.**

**The verify-before-assert practice is now written into that section**, next to the twelve checks,
with the fact that it has a better record than they do on the entry-108/110 class and the measured
evidence for that from entry 111. **It is written down because it is much easier to add a check than
to keep a habit**, and a habit nobody recorded is one the next reader has no reason to keep.

**The pattern this closes.** Entry 102 found that an enumeration over artifacts cannot see a missing
artifact. This is the same blind spot one level up: **an apparatus that checks claims about the
research cannot see claims about the apparatus.**

## Entry 113 — "0.36 GPU-hours for the full pipeline" was one round of seventeen

Continuing entry 112's audit of the sections that describe the apparatus rather than the research.

**The cost claim counts one round and names the whole.** `r04` is the **only** round in this
repository that records its own elapsed time — 1,352 s across three result files, **0.375 h**.
**Seventeen rounds use the GPU** (r04, r08–r15, r20–r22, r29, r39, r41, r46, r52) and **sixteen of
them measure nothing**. The true total is unmeasured and strictly larger than the figure published as
*"measured cost of the full pipeline"*.

**Same shape as entry 102**, one level over: a number computed on what could be reached, presented as
a property of everything. There the enumeration could not see a missing artifact; here the timer could
not see sixteen rounds that never started one.

**What survives exactly: "zero API spend."** No paid inference is used anywhere, and that is checkable
and true.

**The clean-clone claim is stale, not false, and the distinction is the point.** *"Verified from a
clean clone"* was true when written. **Ten rounds have been added since** and nobody has re-run it —
including [r66](rounds/r66_r56_reconstruction), which imports from another round's module and needs
the repository root on `sys.path`. The `__init__.py` files for that exist; a clean-clone execution
does not. Marked as unverified rather than quietly kept or quietly deleted.

**One Boundaries claim checked out exactly**: *"0.61 on picking a single best response"* against
`prompt_concordance = 0.6126`. Verified rather than assumed, which is the practice entry 112 wrote
into the section directly above it.

## Entry 114 — ran the clean-clone verification instead of marking it stale, and it found the one check that could not survive a clone

Entry 113 marked *"verified from a clean clone"* as stale and stopped there. **Stale is a state you
can leave things in; it is not an answer.** So: local clone, no virtualenv inside it, `data/*.jsonl`
absent because they are gitignored.

| | |
|---|---|
| round + assurance + `covalx` files parsed | **94, 0 syntax errors** |
| assurance checks running from a bare clone | **11 of 12** |
| data-free rounds running from a bare clone | **5 of 7** |

**The two rounds that failed are not defects.** r61 and r63 open `data/conversation_rubrics.jsonl`
and `data/comparisons.jsonl`, which the README's own instructions fetch in the step before — I
skipped `python data/fetch.py` deliberately, and they failed exactly there. **A failure at the
documented step is the instructions working.**

**The one real defect:** `assurance/attack_the_suite.py` invoked `<repo>/.venv/bin/python` — a path
that exists only in a working copy. The check whose job is to attack the other checks was the single
one that could not run from a clone.

**And the first patch for it was accidentally correct.** I wrote `PY = str(ROOT / sys.executable)`,
which works only because `pathlib` discards the left operand when the right is absolute. It passed
both runs. **Code that works for a reason other than the one you intended is a defect that has not
happened yet** — rewritten as `PY = sys.executable`, with the near-miss recorded in the file.

**What the run settled that entry 113 could only flag:** the `.npz` tensors *are* committed, so r66
and r67 — which import across round modules and needed `rounds/__init__.py` — both run from the
clone. That was the specific unverified thing, and it is now verified rather than annotated.

## Entry 115 — the repository cites a file its own fetch script does not fetch

`data/fetch.py` verifies the release byte-for-byte, and running it against the files on disk passes:
all four `.jsonl` files match their recorded hashes. **The data these results were computed on is the
released data**, checked rather than assumed.

**But the dataset CARD is neither fetched nor committed.** It was gitignored *and* absent from
`FILES`, so a reproducer following the README's own instructions gets every number and **none of the
text three of this session's findings rest on**:

| entry | what it reads from the card |
|---|---|
| **74** | *"In parallel, we prepared initial rubric items"* (L73) — the provenance that turned "response-blind" into "participant-blind" |
| **88** | the personal-vs-world ranking instructions — every concordance number in this package is against the **world** ordering |
| **90** | recruitment, the onboarding rubric quiz, task order, compensation — the whole π layer |

**Those are not decorative citations.** Entry 74 withdrew an S_pre reading on the strength of one
sentence in that file. A reader who could not obtain it could not check the withdrawal.

**Fixed:** `fetch.py` now fetches and hash-verifies the card as a fifth file
(`92ba4a96…`, 27,509 bytes), and reports 5 of 5.

**And the remote path, flagged UNVERIFIED when this entry was written, is now verified**
(entry 116): `huggingface.co/datasets/openai/coval/resolve/main/README.md` returns HTTP 200,
27,509 bytes, **hash identical to the local copy**. So the quotations entries 74, 88 and 90 rest on
are checkable against the live source, not only against a file on this disk.

**The shape.** Entry 102: an enumeration over artifacts cannot see a missing artifact. Entry 113: a
timer cannot see rounds that never started one. This one: **a fetch script's file list is a claim
about what the work depends on, and it was three entries out of date within one session.** Every
instance is a container that only knows what was put in it.

## Entry 116 — the last unverified assertion took one request, and the card is byte-identical to the live source

Entry 115 fixed `fetch.py` to fetch the dataset card and flagged one thing as unverified: **the remote
path**. On the Hub a dataset card is `README.md` at the repo root, and I had hashed the local file
without ever fetching it.

**One request settled it.** `huggingface.co/datasets/openai/coval/resolve/main/README.md` →
**HTTP 200, 27,509 bytes, sha256 `92ba4a96…`** — identical to the local copy, byte for byte.

**That is worth more than tidying a comment.** Entries 74, 88 and 90 quote that file as evidence:
*"In parallel, we prepared initial rubric items"*, the personal-vs-world ranking instructions, the
onboarding quiz. Until now those quotations were checkable only against **a file on this disk**, with
no established relationship to what OpenAI published. They are now checkable against the live source,
and the hash makes the relationship exact rather than assumed.

**The whole chain is short and it was worth walking.** Entry 113 marked a claim stale. Entry 114 ran
the clone rather than leaving it stale, and found a real defect. Entry 115 found the card missing from
the fetch list and flagged its remote path. This one fetched it. **Four entries, each closing exactly
the thing the previous one deferred** — and the only reason any of it happened is that "stale" was
treated as a state to be exited rather than a label to apply.

## Entry 117 — I asserted an absence twice without looking, and the file was 57 MB, tracked in git

Entries 109 and 110 both said r40's predictor reliability could not be measured because *"the
embeddings are not persisted"*. Entry 110 built a whole argument on it, publishing a **range**
0.180–0.222 where every other row got a point estimate, with the upper bound retained solely because
the number was supposedly unobtainable.

**`rounds/r39_feature_cache/results/r39_feature_cache.npz` is 57 MB and tracked in git.** It holds
`mean_last` for **qwen, phi and internlm** over all 2,000 responses. r39's entire job is caching
representations — its README row says so — and I had audited that row in entry 102, four hours
earlier, for having no results JSON.

**Measured, and the estimator is better than the one I could not use.** r40's predictor has no
internal parts to split, but it has **three unrelated pretraining runs**, which is agreement between
*instruments* rather than internal consistency:

| | |
|---|---:|
| qwen ~ phi | **+0.9023** |
| qwen ~ internlm | +0.7234 |
| phi ~ internlm | +0.7085 |
| Spearman-Brown, k=3 | **0.9132** |

Controls first: a lineage against itself **1.0000**, against a prompt-shuffled copy **−0.0980**.

**So r40's floor is 0.188**, not a range and not 0.222. **The row I marked as vaguest is the
strongest refutation in the ledger.**

**The failure is not the arithmetic, it is the assertion.** Nothing forced me to claim the
embeddings were gone; I inferred it from r40 not storing them and never checked the round whose only
purpose is storing them. **Twice.** Entry 111 concluded that the practice which catches this class is
*running the number before asserting it* — and this was an assertion about a **file**, where the
check is `ls`.

**One more, smaller:** my first parser assumed the cache's `meta` was JSON. It is
`"<prompt_id>|<kind>|<n>"`. It crashed on the first row, which is the correct failure and cost one
minute — the opposite of entry 105, where a bare `except` turned the same class of mistake into a
confident zero.

## Entry 118 — auditing the other asserted absences: three verified, one already wrong

Entry 117's failure was an **asserted absence** — r40's embeddings, claimed missing twice, sitting in
a tracked 57 MB file. That is a class, so the rest of the session's absence claims got the same
treatment.

| claim | how it was established | verdict |
|---|---|---|
| r56's **code** was never committed | `git log --all -S"semantic_selectivity"` over all history (entry 102) | **verified** |
| r56's **CI bounds** appear in no artifact | search of every results file; both 4-decimal, where the chance-match null is low (entry 101) | **verified** |
| `0.042` appears nowhere in r12's results | pool search, no value within [0.038, 0.047] (entry 81) | **verified** |
| the release ships **no satisfaction labels** | **this entry** | **verified** |
| r40's embeddings were never persisted | *inferred from r40 not storing them* | **WRONG** (entry 117) |

**The satisfaction claim is load-bearing and had never been checked directly.** r04 exists to rebuild
that layer; r64's two-arm design exists because a fresh-arm agreement rate has no referent without
it. Streaming every field name from all four release files — 1,078 + 986 + 18,384 + 1,012 lines,
**103 distinct fields** — returns **no** satisfaction-, meets-, fulfils- or per-criterion-score field
in any of them.

**Streamed, not sampled.** Entry 89 published 76.9% from the head of one file when the true figure
was 26.7%; this reads every line of all four and accumulates only field names, which is
memory-safe.

**The distinguishing feature of the one that was wrong is visible in the table.** Four were
established by *searching for the thing*. The fifth was established by *noticing it wasn't where I
happened to look*. Absence of evidence became evidence of absence in exactly the case where no search
was run — and the search, when finally run, took one `ls`.

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

## Entry 119 — the ledger's one reliability column was wrong in both directions, and I predicted the wrong one

**The claim.** The exhaustion ledger published r54's detection floor as **0.300**, computed by
applying r67's predictor reliability of **0.657** to r54's half-width of 0.1336.

**Why I went looking.** Entry 110 caught this exact transfer onto r40 and entry 117 measured r40's
own predictor at **0.9132**. r54 was the same move, unchecked: r67 measured *spread loss* and
*criterion-space geometry*, both judge outputs, and r54's predictor is a word count. r54's own
scope line says so — *"The overlap quantities are exact text statistics."*

**What I predicted, in writing, before running it.** That the reliability would come back **above**
0.657 — because a deterministic text statistic has no judge noise in it — and that r54's floor would
fall to ≈0.256. I wrote both alternative worlds *above* 0.657.

**What it is.** **0.3794** (split-half +0.2341 over the 241 prompts with four core criteria;
+0.2200 → 0.3606 over all 250). Far **below** the transferred value. r54's floor **rises to 0.395**.

**The error in my reasoning, which is the point of this entry.** I conflated two things that share a
word. *Determinism* is a property of the **instrument**: given the text, `containment()` returns the
same number every time, with zero measurement error. *Split-half reliability* here is a property of
the **criteria sample**: how much of the per-prompt variance survives swapping one half of a
prompt's criteria for the other. A function with zero measurement error still scores low when a
prompt's own criteria disagree about the quantity — and they do. Two criteria from one rubric share
about a quarter of their collapse variance.

**The instability is not the contrast's fault.** The raw containment **level**, split the same way,
is already **0.4104** — before any difference is taken. So it is not that a difference-of-differences
amplifies noise; two criteria from one rubric simply do not have similar lexical overlap with the
same responses.

**The world I failed to name.** My first world assignment read
`world = "D DETERMINISTIC" if rel > R67_REL + 0.10 else "T TRANSFERS"` — a one-sided threshold, so
0.3794 was labelled *"the transfer was harmless"*. Both worlds I wrote sat above 0.657, and the
outcome that happened had nowhere to land. Same family as entry 96: a check that can only fire in
the direction I expected. Fixed to a three-way test; the third world is named `U UNDER-CREDITED`
and is named only because the result forced it.

**The control that made this readable.** My first reading — *"the collapse is unstable"* — was drawn
from a **second low number** (the level's 0.4104), which is silence, not a measurement: a low
split-half is evidence about the criteria only if the estimator can return a high one. Splitting the
**responses** instead of the criteria, keeping every criterion, returns **0.8020** (shuffled
+0.0039). The machinery works. The criterion axis is genuinely the noisy one.

**What this does to the ledger.** The single reliability column moved **two rows in opposite
directions**: r40 up (0.657 → 0.9132, floor 0.222 → 0.188), r54 down (0.657 → 0.3794, floor
0.300 → 0.395). A ledger-wide reliability is therefore not a conservative simplification — it is a
number with no sign guarantee, and only measuring each predictor against its own construct says
which way a given row moves. r67's 0.657 stands for **r41 and r46 only**, whose predictors are
judge outputs.

**Corrected.** README ledger row 10 → 0.395; the r67 paragraph rewritten to scope 1.23× to r41/r46;
r67's summary row marked superseded; r69 row added.

**Still true.** r54's own headline is untouched: the overlap mechanism is real (+0.1294 → +0.0945 on
fresh, drop +0.0349 [+0.0266, +0.0434]) and does not predict *which* prompts drop. What changes is
how much that failure rules out — less than published, on a row that was already the weakest in the
table.

**A repository note found on the way.** `rounds/r54_overlap_transfer/run.py` defaults `--gen` to
`a12_response_set.json`, which has no `prompt_ids` key and raises KeyError; r54 was run with an
explicit `--gen a12_fresh_generations.json`. The committed default cannot reproduce the committed
result. Recorded, not silently repaired, because the fix belongs to whoever re-runs r54.

## Entry 120 — a single split-half is one realisation, and I published two of them the same day

**The claim.** r69, committed hours ago, reported r54's predictor reliability as **0.3794** and its
detection floor as **0.395**. r70's first version reported the outcome's criterion-axis reliability
as **0.3911**.

**Both were single draws.** Each split every prompt's four criteria 2-2 **once**, from one seed, and
reported the resulting correlation as the reliability. r57 — the round whose number sits on the other
side of the very same formula — averages over **200 random splits**, and says so in its own method
line. I read that line, reused r57's role in the arithmetic, and did not reuse its method.

**What averaging does.**

| quantity | single draw | 200-split mean | sd | range across draws |
|---|---:|---:|---:|---|
| r54 predictor (r69) | +0.2341 | **+0.2805** | 0.0399 | +0.183 … +0.387 |
| attribution drop (r70) | +0.2431 | **+0.1774** | 0.0426 | +0.092 … +0.323 |

The two errors went in **opposite** directions — r69's draw was unfavourable, r70's favourable — so
this is not a bias with a sign I could have corrected for. It is variance I did not measure.

**Corrected numbers.** r54's predictor reliability **0.3794 → 0.4381**; its floor **0.395 → 0.367**.
r54 is still the ledger's weakest row and r69's world (`U UNDER-CREDITED`) is unchanged: 0.4381 is
still far below the 0.657 transferred onto it, so entry 119's finding stands and only its magnitude
moves.

**Why the spread is not sampling noise.** For K=4 there are exactly three distinct 2-2 partitions.
More draws would not shrink the range; it is the real heterogeneity between one prompt's criteria.
Which is the same fact entry 119 reported — measured properly, it is *larger* than entry 119 said.

**What r70 found that motivated the recheck.** The ledger's floor formula is
`half-width / sqrt(rel_predictor × rel_outcome)` — and **the two reliabilities are estimated along
different axes**. r57 splits the six *pairs*; r67 and r69 split *criteria*. Nobody wrote that down,
including me, in either round. Rebuilding the attribution drop from criteria halves (on a tensor
whose full-criteria rebuild reproduces every one of r12's published per-prompt values to 0.0e+00)
gives a criterion-axis outcome reliability of **0.3013**, close to r57's 0.302/0.422 — so for the
outcome the two axes happen to agree, even though they differ roughly twofold for r54's predictor.

**The ladder, which is the more useful result.** Same criteria halves, three quantities:
accuracy **0.6462**, attribution **0.2695**, drop **0.3013**. The criterion split does not destroy
signal by itself, so the reliability is lost in the *contrast* — confirming r57's own stated worry,
which r57 never tested: *"A DIFFERENCE of two accuracies is inherently less reliable than either."*

**What is left open, deliberately.** Whether a floor is *entitled* to divide by criterion-axis
reliability at all is **not an empirical question** — it asks what `M(R,J,π,Q,P)` holds fixed.
Under **F** (R is part of the program, so this rubric's criteria are not error) the 1.23× multiplier
is an over-correction. Under **S** (criteria sampled from a repertoire) the current floors stand.
Under **B** (the rows are mechanism claims, so both axes are error) r54's floor would be **0.669**.
r70 reports all three columns and declares no winner, because that is a decision about the research
object and r70 measured a correlation. What r70 *did* settle is that world B's arithmetic is at least
valid on its own terms: splitting both axes at once gives **+0.0785 [+0.0061, +0.1480]**, covering
the independent-sources product (+0.0463) and excluding the shared-source value (+0.1808).

**The rule.** A split-half reported from one split is a point estimate of a quantity that varies by
3.5× across splits. Average it, report the spread, or do not report it.

## Entry 121 — r67 survives its re-run, and I overstated the reason within the hour

**The audit.** Entry 120's rule — *average a split-half or do not report it* — corrected r69 and r70
but not **r67**, which is the one the README still leans on: 0.657 is the only predictor reliability
available for r41 and r46, and the ledger's 1.23× comes from it.

**It survives.** r67's estimator re-run verbatim, 200 draws instead of one: spread loss **0.6849**
(sd 0.0294), criterion-space geometry **0.6653** (sd 0.0304), mean **0.6751** against the published
0.657 — a shift of **+0.018**. Multiplier 1.217× not 1.234×. r41's floor 0.227 → **0.224**, r46's
0.264 → **0.260**. World `A STABLE`. All three reliability rounds are now averaged.

**What I got wrong in the same commit.** I wrote that "across-split volatility scales with
unreliability", citing relative spreads of 5.8% / 14% / 24% against raw correlations of 0.51 / 0.28 /
0.18, and called the pattern the finding. It is mostly arithmetic:

| quantity | mean raw | sd across splits | relative |
|---|---:|---:|---:|
| r67 spread loss | +0.5207 | 0.0294 | 5.6% |
| r67 geometry | +0.4984 | 0.0304 | 6.1% |
| r70 accuracy | +0.4773 | 0.0321 | 6.7% |
| r69 r54 predictor | +0.2805 | 0.0399 | 14.2% |
| r70 drop | +0.1774 | 0.0426 | 24.0% |
| r70 attribution | +0.1557 | 0.0448 | 28.8% |

The **absolute** sd spans 0.0294 to 0.0448 — a 1.5× range across six quantities whose correlations
differ by 3.3×. So the relative column moves because its **denominator** moves. I built a ratio,
watched the denominator drive it, and reported the ratio as a property of the numerator — which is
the same defect this repository has already logged (see the correction below).

**The corrected statement, which reaches the same practical place.** A single split perturbs a raw
correlation by roughly **±0.04 regardless of the quantity**. That is negligible at r≈0.51 and
material at r≈0.18 — so averaging matters most for the least reliable quantities, but because the
error is a **constant additive** term, not because volatility scales with anything.

**Why this entry exists at all.** The overstatement changed no number and no decision. It is logged
because the failure mode — *a ratio whose movement belongs to its denominator, reported as a finding
about its numerator* — has occurred before in this project, and this occurrence was inside a commit
whose whole subject was correcting a measurement error.

**⚠ CORRECTION to this entry, made the same day, and it is the sharper lesson.** As first written
this entry said the defect *"has now occurred three times in this project"* and named two
precedents: a ratio of noisy reciprocals, and a path-dependent per-cause percentage. **Neither is in
this ledger.** `grep -niE "noisy reciprocal|per-cause|decomposition is path" RETRACTIONS.md` returns
only the sentence that names them. Both live in my cross-project memory files, one of which does
concern CoVal — and I cited them as if they were entries *here*, from memory, without looking.

The genuine precedent, and there is exactly one, is **[Entry 68](#entry-68)** — *under-replication
does not move the estimate, it inflates the TEST STATISTIC*: every ratio there was unchanged because
ratios are means, while the **z** moved 23% because its denominator is a null SD estimated from 15
draws. Same class, verified by reading it.

So the count in this repository is **two, not three** — Entry 68 and this one. That matters
operationally: *"same bug three times → build infrastructure, not a third patch"* is a standing rule,
and at two instances **it does not fire.** No check is built. Had I not verified the citation I would
have built one on a count I invented.

The lesson is one level up from the entry it corrects: I wrote an entry about a number I had not
checked, and inside it cited two precedents I had also not checked. **The citation is the part of a
retraction least likely to be audited, because it looks like bookkeeping rather than a claim.**

**One control detail worth keeping.** The shuffled null is re-run on **every** draw and reported as a
**maximum** (0.2016), never a mean. A control averaged over 200 draws would hide one bad draw, which
is precisely the failure r71 exists to close.

## Entry 122 — the ledger's 224 numbered citations all resolve; the risk was never in the numbered ones

**Why this ran.** Entry 121's correction found a fabricated precedent — two prior instances cited
from memory that are not in this ledger. The obvious follow-up is whether that is systematic.

**It is not.** Every `entry N` reference in RETRACTIONS.md was resolved against the document:

- **224** numbered citations, across **85** distinct entry numbers
- **0 dangling** — every cited number has a record
- entries **1–40** live as **table rows**, **41–121** as `## Entry` headings; a first pass indexed
  only the headings and reported **14 false dangles**, which is this project's own catalogued failure
  (*a check is only as good as its population*) committed inside the audit of a citation error
- the row extractor over-matches one number (**400**, a data row, not an entry). No citation
  references it, so no resolution passes through junk — checked rather than assumed, since an
  over-broad population turns a dangling citation into a false pass

**Where the risk actually lives.** Precedent claims made in **prose with no entry number** — a
resolver cannot check those, and the fabricated one was exactly that shape. There are **two** in the
whole document:

1. entry 121's *"already logged twice…"* — **fabricated, corrected above**
2. entry 59's *"The third instance of one failure."* — **fully specified**, because the very next
   sentence names both precedents by number (51 and 57) and states what each was

So the defect rate on unnumbered precedent claims is 1 of 2, and on numbered citations 0 of 224.
**The failure mode is not "citations rot" — it is "a precedent asserted without a number is not a
citation at all."**

**What this changes.** Nothing retroactive. Going forward, a precedent claim in this ledger names its
entry number, so it lands in the 0-of-224 population rather than the 1-of-2 one.

**What was NOT built, deliberately.** A citation resolver. It would have scored 224/224 clean and
**zero recall on the one real defect**, which named no number — the same shape as the check measured
and declined at entry 108. Measuring it cost one command; building it would have bought a green light
on the population that was never at risk.

## Entry 123 — the only human-validated number in the package was computed, stored, and never read out

**The standing line.** Every correlational round carries a scope sentence: *"scored by the r08 model
gold head, not by humans (entry 50, r47)."* It reads as a limitation being honestly declared. It is —
but it is declared alongside a **measurement of how much that limitation costs**, which nobody
surfaced.

**What was sitting there.** `rounds/r47_gold_is_length/results/r47_gold_is_length.json` →
`samples[*].proxy_validation_on_original`. It ran on **all 250 prompts, in both samples**. Its
per-prompt correlations — **0.6029** and **0.6509** — return **zero** matches across README.md,
RETRACTIONS.md and PREREGISTRATION.md. So does the human-scored attribution itself.

**Recomputed independently** (r72), from the released `ranking_blocks["world"]` rankings. The gold
side reproduces r47's stored 0.1020 to **0.0e+00**, so this is the same quantity, not a lookalike.

| attribution, original arm | value | 95% CI |
|---|---:|---|
| scored by the model gold head | +0.1020 | [+0.0727, +0.1320] |
| scored by **real human rankings** | +0.0876 | [+0.0678, +0.1075] |
| human − gold | **−0.0144** | [−0.0392, +0.0086] |

**Significance and equivalence disagree, and only one was ever quoted.** r47 stored `differ: False`.
That is a *non-significance* call. Tested for practical equivalence at the preregistered **δ=0.01**,
the 90% interval is **[−0.0344, +0.0060]** — **2.0× wider than the margin**, with the point estimate
alone at **1.4× the margin**. So it is **NOT EQUIVALENT**. A field named `differ` holding `False`
invites exactly the reading the data does not support, and the whole point of queue item 4 is that
non-significance is not equivalence.

**The number that matters more.** The per-prompt **validity coefficient is 0.6029** — gold-scored and
human-scored attribution share about **36%** of their variance across prompts. Every correlational
row in the exhaustion ledger operates at per-prompt resolution.

**What I refuse to do with it, explicitly.** Apply it to those rows as a third attenuation term. Their
outcome is the **drop** (original − fresh); this coefficient is measured on the **original
attribution** alone, because the release contains no human rankings for generated responses. That is
the boundary-crossing error of entries 110, 119 and 120 — and unlike those three, this boundary
**cannot be crossed by any recomputation.** Only H_fresh crosses it. Stating the coefficient and
refusing to transfer it is the whole discipline here.

**What it does establish.** The proxy is validated exactly where it is **least stressed** — the
original candidates — and applied where it is most stressed. r47 identified that asymmetry for its
*length* channel. It holds for its *validity* too, and now has a number.

**How nearly I misread it.** Locating the field, I twice read `None` off the wrong level of the JSON:
once by indexing a dict as if it were a list, once by asking for `human_validation` (the *function's*
name) instead of `proxy_validation_on_original` (the *key*). Either misread would have produced a
much more dramatic entry — *"the validation silently returned nothing"* — and I was one command from
writing it. The object was fine both times; the reader was wrong. **A `None` from an accessor is a
claim about the accessor until the accessor has been shown to return something.**

## Entry 124 — the repository's most-used check never calibrated its own PASS side, and the check I was about to build fails 94% of the time

**What prompted this.** Entry 123 found a measured qualifier — r47's `proxy_validation_on_original` —
that no document ever quoted. The obvious follow-up is a mirror check: `readme_agrees_with_results`
tests **README → artifact**; nobody has tested **artifact → README**, the direction that hides
*findings* rather than *errors*.

**I measured that check before building it, and it fails.** Testing whether an artifact value appears
anywhere in README + RETRACTIONS (354,586 chars):

| draw | chance-match rate |
|---|---:|
| correlation-like, U(−1, 1) | **94.1%** |
| accuracy-like, U(0.4, 0.8) | **93.2%** |
| small-effect-like, U(−0.15, 0.15) | **100.0%** |

A value that never existed "appears" as often as one that did. The instrument would report almost
everything as surfaced, and it **fails toward PASS**. Its nominal positive control made this concrete:
of r47's 22 `proxy_validation` values, it flagged **2** against the pre-r72 documents — the other 20
"passed" by coincidence, including **0.1020** and **0.0876**, which I had established by grep an hour
earlier were *other quantities* in the README. **Not built.** The real case was found by reading the
artifact, which no matcher did or could.

**Then the same question, turned on the check already in production.** `readme_agrees_with_results`
has run for many rounds and its *matches* have been read as agreement. Its pools are one round's
values, not a 354k-char corpus, so its chance rate should be lower — but *should be* is not a
measurement:

| decimals | chance-match rate (mean over 70 pools) | worst pool | share of README tokens |
|---|---:|---:|---:|
| 1 | **56.8%** | 100.0% | 12% |
| 2 | 23.0% | 100.0% | 11% |
| 3 | 8.1% | 52.5% | 19% |
| 4 | **2.4%** | 27.5% | 44% |

**So the check is strong exactly where most of the README lives and nearly worthless at the margin.**
A match on a 4-decimal figure is real evidence; a match on a 1-decimal figure is close to free, and
against the largest pool it is free outright. 44% of README tokens sit in the strong band, 23% in the
two weak ones.

**What changed.** The table is now **recomputed at run time and printed with every result**, so the
PASS side cannot be read as uniform again. Nothing about the check's flags changes — the *unmatched*
side was always the informative one, and it still is. What changes is that its **matched** side now
arrives with a price tag.

**The general form, which is the reason this entry exists.** A matcher's silence is only evidence if
the matcher would usually speak. This repository has a law about that for nulls — *a measured zero is
inadmissible until the instrument has passed a positive control* — and it had never been applied to
**agreement** instruments, only to measurement ones. A check that says *"these numbers agree"* needs a
chance-match null exactly as much as an ablation needs a positive control.
