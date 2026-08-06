# R781 · the 1,820-member reference class has an effective size of 1.1

`run.py` · `PREREGISTRATION.txt` · `results/extension_distribution.json` · 968 prompts · 1,820 references
· 20 k=4 arms

## THE DECISION THIS MAKES SAFE

**Stop describing clause ②'s comparator as a class of 1,820.** Its members correlate at **+0.8709**
pairwise, giving an effective size of **1.1** — statistically one reference — and the whole class spans
A2 **0.5144 to 0.5575**, a range of **0.0431**, about **2× the MDE** of the contrast it decides
(0.0216, R780). The baseline choice R527 and R665 exposed is therefore not a choice among 1,820
comparators; it is **a choice of where to stand on a 0.043-wide line**, and the extension's 8 → 2
collapse happens inside that window.

## ⚠ WHAT THIS ROUND CLAIMS, AND WHAT ITS OWN CONTROL FORBIDS

The script's registered branch fired **WORLD B — the choice is marginal**: 100.0% of arms sit outside
[0.10, 0.90] and 0.0% in [0.35, 0.65]. **That branch is not the finding, because the DEPENDENCE
measurement — which the preregistration required be printed BEFORE any q is interpreted — says the
shape statistic is inadmissible as registered.** `q` was defined as an admission probability *over a
reference drawn at random from the class*; with n_eff = 1.1 there is no meaningful draw. **The
distributional reading is UNVERIFIED, and the bimodality is the arithmetic consequence of comparing
20 arms to a 0.043-wide band, not evidence about the arms.**

## E1 · q OVER THE CLASS, LEAVE-ONE-OUT

| arm | A2 | q | q resolved |
|---|---:|---:|---:|
| oracle_k4 · oracle_kA · oracle_kB | 0.6283 | 1.0000 | 1.0000 |
| greedy_k4_greedy_kA · kB | 0.6226 | 1.0000 | 1.0000 |
| oracle_k4_fit1 | 0.6142 | 1.0000 | 1.0000 |
| greedy_k4_fit1 | 0.6106 | 1.0000 | 1.0000 |
| indep_k4_indep_kA · kB | 0.6031 | 1.0000 | 1.0000 |
| indep_k4_fit1 | 0.5941 | 1.0000 | 1.0000 |
| topw_k4 · detA · detB | 0.5642 | 1.0000 | 0.9835 |
| **`generic` = POOL[0:4]** | 0.5504 | **0.9379** | 0.7422 |
| topwvar_k4 | 0.5040 | 0.0000 | 0.0000 |
| random_k4_s0 · s1 · s2 | 0.4884–0.4981 | 0.0000 | 0.0000 |
| topabs_k4 | 0.4894 | 0.0000 | 0.0000 |
| topvar_k4 | 0.4863 | 0.0000 | 0.0000 |

⭐ **Exactly one arm is not at 0 or 1, and it is the published comparator itself** — which is a member
of the class and therefore cannot be far from it. Leave-one-out excluded **1** self-matching
reference, for that arm alone. **So the entire baseline sensitivity of the definition is carried by
the one arm that is definitionally inside its own reference class.**

## E4 · RELEASE 2, 5-MEMBER BLIND CLASS

`transport_gen` 0.5541 (q = 1.00 over 5) · `transport_generic` 0.5522 (1.00 over 4) ·
`transport_randblind_s2` 0.5301 (0.75) · `transport_gen_sham` 0.5278 (0.60) ·
`transport_randblind_s0` 0.5209 (0.50) · `transport_vacuous` 0.5126 (0.25) ·
`transport_randblind_s1` 0.5006 (0.00). **q takes 6 values on 5 references — an ordering, never a
shape.** Reported as registered, claimed as nothing more.

## CONTROLS — AND TWO OF THEM ARE DEFECTIVE

| control | returned | |
|---|---|---|
| OBJECT | 16 pool criteria · C(16,4) = **1820** · 968 prompts · class mean 0.5386, range [0.5144, 0.5575] | PASS, else exit 2 |
| DEPENDENCE | mean pairwise reference correlation **+0.8709** → **n_eff = 1.1** | **the round's finding** |
| LEAKAGE | self-matching references excluded: **1**, on `generic_POOL0-3` only | PASS |
| PLACEBO | an arm against itself, q = **0.0000** (tied, not greater) | PASS |
| g=0 | a class member scored leave-one-out returns q **0.7273** against its own rank **0.7269** | PASS — this is the control that would have caught self-comparison |
| POSITIVE | dominating plant q **1.0000**, dominated plant q **0.0000**; every real arm inside the measured band | PASS |
| **NEGATIVE** | pairing permuted, 200 draws: **[0.9374, 0.9379]** against a real **0.9379** | ⛔ **VOID — a DERIVATION** |
| **SHAM** | criterion content destroyed: q **1.0000**, *above* the real 0.9379 | ⛔ **VOID — a poison** |

### ⛔ the negative control cannot fail, and the arithmetic says so

`q` counts references whose mean paired difference is positive, and that difference is
`mean(v) − mean(REF_i)` — **invariant under permuting `v` across prompts.** So the permuted q equals
the real q by construction; the 0.0005 spread is float noise. This is the *same* derivation R780
caught one round earlier in its own pairing permutation, **built again in the very next round**, which
makes it a habit and not an accident. **The round has no valid negative control for `q`.** A valid one
would have to destroy the *reference*-side structure while preserving its marginal — which is what the
SHAM attempted, and:

### ⛔ the sham is a poison, not a placebo — §4's row, committed again

Shuffling the pool satisfactions across prompts destroyed the **references'** alignment with their own
prompts, so the entire class collapsed and a fixed arm beat all of it: q **1.0000 > 0.9379**. The tell
is exactly the one §4 names, mirrored — the sham moved the comparison in the *flattering* direction
because I degraded the comparator instead of removing the ingredient from the arm. **The ingredient
under study is the arm's relation to the class; the sham removed the class's relation to the prompts.**

## WHAT DIED

- **"a 1,820-member reference class"** as a description of clause ②'s comparator. n_eff = 1.1.
- **the distributional reading of `q`** — my own registered estimand, killed by my own dependence control.
- **R780's NEXT as I wrote it** — I counted blind arms *with an npz on disk* (2) when the claim was
  about blind references *available*; every k=4 subset of `sat_genericpool16.npz` is one, and the
  construction is prior art in R446, R488, R527, R528, R604, R664, R665, R666 and R761.

## WHAT SURVIVES, AND IS STRENGTHENED

R527's and R665's finding that the extension is baseline-conditional — now with its mechanism: the
sensitivity is carried by **one arm inside its own class**, across a window of **0.0431**, roughly
**2 MDEs** wide.

## SCOPE

population 968 prompts, 20 k=4 home-judge arms with full coverage · instrument A2 over all annotators
· baseline the 1,820-subset class (r1) and the 5 scored blind arms (r2) — **the swept axis** · regime
first release + second release, home judge, k=4.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| an out-of-sample reference class | a second prompt-blind pool; these 16 criteria are the only ones the release ships, so every reference is in-sample and R666's order-statistic bias applies at the extremes |
| a release-2 class of comparable size | release 2 ships `core_generic.json` at k=4, not a 16-criterion pool; its blind class has 5 members |
| a judge-free reference | the class is scored by the same judge as the arms |
| a valid negative control for `q` | a permutation that destroys reference-side structure while preserving each reference's marginal — the arm-side permutation is provably invariant |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The dependence number reframes the open question: if the class is effectively one reference with a
0.043 range, then **the quantity that decides the extension is where an arm sits relative to that
band's WIDTH**, not which member is named. That is a different estimand from anything measured so far
— computed by this round's `run.py`, the class range is 0.0431 and R780's MDE for the matched contrast
is 0.0216, so the band is 1.99 MDEs wide and an arm within ±1 MDE of the class mean is
baseline-conditional by arithmetic. The step is to enumerate which arms fall in that zone across the
whole 41-arm census rather than the 20 with k=4 coverage, and to state the definition's extension as
{resolved above} + {inside the band, named} + {resolved below}.
