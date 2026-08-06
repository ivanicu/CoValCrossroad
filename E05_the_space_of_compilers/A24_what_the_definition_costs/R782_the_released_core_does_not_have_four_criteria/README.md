# R782 · the released core does not have four criteria, and the conditional arm was excluded by a regex

`run.py` · `PREREGISTRATION.txt` · `results/size_and_comparator.json` · 968 prompts · 50 scored arms

## THE DECISION THIS MAKES SAFE

**Stop selecting the k=4 population by name, and stop calling the released core a four-criterion
object.** `coval_core` carries **4 criteria on 925 prompts, 3 on 42, and 2 on 1** — and the rubric is
**never smaller than 4** on any prompt, so its shortness is not the rubric running out. Correcting the
population from a name regex to the object adds **6 arms**, and one of them **overturns R781's
headline**.

## ⭐ THE ARM THAT WAS MISSING IS THE ONE THAT MATTERS

| arm | A2 | q | q_resolved | |
|---|---:|---:|---:|---|
| oracle_k4 · _oracle_kA · _oracle_kB | 0.6283 | 1.0000 | 1.0000 | |
| greedy_k4_greedy_kA · _kB | 0.6226 | 1.0000 | 1.0000 | |
| oracle_k4_fit1 | 0.6142 | 1.0000 | 1.0000 | |
| greedy_k4_fit1 | 0.6106 | 1.0000 | 1.0000 | |
| indep_k4_indep_kA · _kB | 0.6031 | 1.0000 | 1.0000 | |
| indep_k4_fit1 | 0.5941 | 1.0000 | 1.0000 | |
| **`coval_core`** | **0.5665** | 1.0000 | **0.9978** | **absent from R781** |
| topw_k4 · _detA · _detB | 0.5642 | 1.0000 | 0.9835 | |
| `generic` · `generic_reprov` | 0.5514 | 0.9538 | 0.7780 | absent from R781 |
| **`gen`** | **0.5352** | **0.3308** | **0.0396** | ⭐ **absent from R781** |
| topwvar_k4 · random_k4_s1 · `coval_core_sham` · random_k4_s0 · `topw_k4_sham` · topabs_k4 · random_k4_s2 · topvar_k4 · `gen_sham` | 0.4828–0.5040 | 0.0000 | 0.0000 | 4 absent from R781 |

**Shape over 26 arms: middle band [0.35, 0.65] = 0.0000 · extreme outside [0.10, 0.90] = 0.9615.**
The single arm in **neither** band is **`gen`, at q = 0.3308** — the prompt-specific generated core.

⛔ **This overturns R781's headline.** R781 reported the baseline sensitivity as carried by
`generic` — the comparator inside its own class — because its name regex `_k4(_|$)` excluded `gen`.
With the population read from the object, **`generic` is at 0.9538 and the genuinely
baseline-conditional arm is `gen`**. And `gen` is exactly the arm R665's curve admits at p000 and
drops at p005: **R665's 8 → 7 step is `gen`, and R781 could not see it.**

## E1 · SIZE IS A DISTRIBUTION, NOT A NUMBER

**18 of 50 arms are ragged.** Most raggedness is *forced*: the rubric `full` spans **4 to 39**
criteria, so a k=6 draw is short exactly where the rubric holds fewer than 6 — `random_k6` is
`{4:3, 5:1, 6:964}`, off-modal on **4** prompts; `random_k8` on 49; `random_k12` on 234.

⭐ **`coval_core` is the exception and it is the released core.** It is short on **43** prompts while
**0** prompts have a rubric smaller than 4. Whatever produces it, the cause is not the rubric running
out. `gen` is off-modal on 2.

**E1b · core files and sat files agree on size for all 48 arms with a readable core file.** Two have
none — `coval_core` (R441 recorded this) and `generic_reprov`.

## E2 · R604's QUESTION, CLOSED — **WORLD B**

R604 registered as UNVERIFIED whether `POOL[0:4]` and the scored `generic` denote the same arm,
saying *"it needs the scorer, not a search."* Both were on disk.

| | |
|---|---|
| raw satisfaction arrays identical | **False**, max \|dY\| **0.120967** |
| A2 | `POOL[0:4]` **0.550436** · `generic` **0.551354** |
| paired difference | **−0.000918** [−0.002430, +0.000562], MDE **0.002188** → **UNRESOLVED** |
| per-prompt A2 differs | **73 of 968** prompts, max \|diff\| **0.2500** |

**They are different objects and the difference is below resolution.** Exactly D3, derived before
measuring: the pages must name which arm they mean, and **no published ② verdict moves.**

## E3 · THREE FILTERS, SIDE BY SIDE

| filter | admits |
|---|---:|
| name regex `_k4(_\|$)` — R781's | **20** |
| strict, k = 4 on every prompt — my first replacement | **22** |
| modal, k = 4 on most prompts — the object | **26** |

`modal \ name` = `coval_core`, `coval_core_sham`, `gen`, `gen_sham`, `generic`, `generic_reprov`.
`modal \ strict` = `coval_core`, `coval_core_sham`, `gen`, `gen_sham`. `name \ modal` = **∅**.
**Both filters I wrote are strict subsets of the object's answer, and both drop the released core.**

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | 968 prompts · 50 home-judge arms with full coverage · both comparators on disk | PASS, else exit 2 |
| PLACEBO | an arm against itself **0.000000** | PASS |
| g=0 | the same file scored twice **0.000000**, and does not resolve | PASS |
| REPLICA | `topw_k4` vs `topw_k4_detA` (R766's within-pass pair) **0.000000** | PASS — **this is the negative's job** |
| POSITIVE | 0×MDE UNRESOLVED · 0.5× UNRESOLVED · 1× UNRESOLVED · 4× **BEATS** | PASS, band computed at both ends |
| **SHAM** | −0.123362 [−0.136431, −0.111547] | ⛔ **INADMISSIBLE — see below** |

### ⛔ the negative control was not built, on purpose

D2, derived before the run: a paired mean is invariant under permuting one arm across prompts, so the
arm-side permutation null is void. R780 caught it, R781 built it anyway (ledger 1125). **This round
does not build it** and gives the negative's job to a **replica pair** R766 already established is
within-pass identical. It returns exactly 0.

### ⛔ and the sham is inadmissible for a different reason — the object has no ingredient to remove

`generic` is **prompt-blind**: the same four criteria on every prompt. The ingredient a sham should
remove is *prompt-specificity*, and this arm has none. What the code actually did was misalign the
predicted scores against the targets, which is **§4's poison** with the harmful sign (−0.1234), for
the third time in three rounds. **The honest statement is that a sham is undefined for a prompt-blind
comparator**, not that it returned −0.1234. The replica control carries the round.

## WHAT DIED

- **"four criteria"** as a property of the released core. It has four on 95.6% of prompts.
- **R781's headline** — the conditional arm is `gen`, not `generic`, and R781's regex excluded it.
- **R604's UNVERIFIED** — resolved to *different objects*, and simultaneously to *no verdict moves*.
- **both population filters I wrote**, each a strict subset of the object's answer.

## SCOPE

population 968 prompts · 50 home-judge arms with full coverage, 26 modal-k=4 · instrument distinct
criterion indices per prompt (E1) and A2 over all annotators (E2, E4) · baseline the 1,820-subset
class with **n_eff = 1.1** stated beside it (R781) · regime first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| why the released core is short on 43 prompts | the generator's logs, off-repository — R605 measured that no script in this tree writes 98 of 101 sat artifacts |
| a judge-free size | the size is read from the sat file, which the judge wrote |
| a sham for a prompt-blind arm | an arm with a prompt-specific ingredient to remove; `generic` has none |
| cross-release size comparison | release 2 ships `core_generic.json` at k=4 only |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

`gen` is the one arm whose admission depends on where in the 0.043-wide band the comparator is placed,
and R780 measured it LOSING to the blind reference on release 1 (−0.0267) while release 2 left it
UNRESOLVED (+0.0020). Those are the same arm at three different comparators, and this round's table
adds a fourth reading (q = 0.3308, q_resolved = 0.0396). **The quantity never computed is how much of
that spread is the comparator and how much is the estimator**: the four readings use two different
targets (the mean-ranking and the every-annotator target, both measured in R780) and two different
reference sets, and no round has crossed them. Computed by this round's `run.py`, `gen` appears in the
E4 table once and in R780's table once, so the cross is 2 targets × 2 references = 4 cells, of which
**2 have been measured** and the other two are one script away.
