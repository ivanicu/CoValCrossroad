# Retractions

Every claim this repository made and then killed, scoped or corrected — in the order
it happened, with what did the killing.

The rounds are numbered by when they ran, not by what survived. Read in that order
the repository looks like a sequence of findings. It is not. **Eleven of these
forty-two entries are a later round destroying an earlier round's conclusion, and in
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
| 29 | **r27's actor control** — "the negative tail vanishes among pairs of two generally-agreeable raters, so it is an actor effect, not blocs" | Two defects. **(a)** A pair's own agreement feeds both members' actor scores, so selecting *both above median* selects directly on the outcome; fixed leave-one-out, which moved it only 0.20×→0.24×. **(b)** Fatal: under **unequal** bloc sizes a majority-bloc member agrees with most people and is therefore "agreeable" **by construction**, so both-high pairs are mostly *same-bloc* and the control could not have found blocs even if they were there | The observation (far tail at 0.24× the null among agreeable pairs, z=−10.00), not the inference |
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
