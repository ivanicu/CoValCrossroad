# R788 · clause ② pays 0.235 of `q_resolved` for being low-variance, and prompt-blind arms are low-variance

`run.py` · `PREREGISTRATION.txt` · `results/membership.json` · 27 arms × 1,820 references ·
**WORLD C**

## THE DECISION THIS MAKES SAFE

**Clause ②'s resolution criterion confers a large, structural advantage on arms that vary little
against the blind class — and prompt-blind arms are exactly those arms.** Holding `generic`'s A2
fixed and giving it `gen`'s per-reference sd (a factor of **1.871**) moves its `q_resolved` from
**0.7780 to 0.5429 — a shift of −0.2352.** The definition's only measured clause rewards resembling
its own baseline.

## ⛔ AND MY REGISTERED CONFOUND WON — **WORLD C, NOT B**

I hypothesised the advantage came from `generic` being a **member** of its own comparator class. It
is one: `core_generic.json`'s four criteria are pool indices **[0, 1, 2, 3]**, so `generic` **is**
reference **#0** of the 1,820. But the confound control settles it the other way:

| arm | blind? | member? | k | sd(v − REF) |
|---|---|---|---:|---:|
| `generic` | yes | **yes** | 4 | 0.0711 |
| `genericpool16` | yes | **no** | 16 | **0.0635** |

**`genericpool16` is blind but not a member, and its sd is LOWER.** So the low variance is a property
of **prompt-blindness**, not of membership. The confound was written into the preregistration
precisely because blindness and membership were conflated in my hypothesis, and it separated them.

## ⭐ THE EXCLUSION RULE IS MATCHING THE WRONG UNIT

R781 and R782 exclude a self-matching reference when the per-prompt difference is identically zero —
that is, they match on the **judge's output**. `generic` and its own subset were scored in **two
different passes**, so they differ (mean |Δ| **0.005638**; R782 measured a maximum of 0.121 on 73 of
968 prompts). The result:

| exclusion rule | references excluded for `generic` |
|---|---:|
| satisfaction-based (R781/R782's) | **0** |
| criterion-based (the right unit) | **1** — reference #0 |

**POSITIVE control, band computed at both ends**: at jitter **0** the satisfaction rule catches 1; at
jitter 0.001 and at the observed 0.005638 it catches **0**, while the criterion rule catches 1 at
every level. §4's *instrument unit versus claim unit*, this time **inside the exclusion rule itself**.

⚠ **And by D1 the exclusion is worth almost nothing anyway**: removing one reference of 1,820 shifts
`q_resolved` by **+0.000428**, inside the derived bound of 0.000549. **The rule is wrong and fixing it
changes nothing** — the leak I went looking for is real, exactly located, and negligible. What matters
is the variance term, which is 550× larger.

## E1 · THE DECOMPOSITION, VERIFIED

`Var(v − REF) = Var(v) + Var(REF) − 2·Cov(v, REF)` — worst mismatch over 27 arms × 1,820 references:
**2.082e-17**. ⚠ A zero here is a DERIVATION check on the code, not evidence.

## E3 · THE MAGNITUDES, SIDE BY SIDE

| | q | q_resolved |
|---|---:|---:|
| published (R782) | 0.9538 | 0.7780 |
| recomputed here | 0.9538 | 0.7780 |
| self-reference #0 removed | 0.9538 | 0.7784 (**+0.000428**) |
| **sd scaled to `gen`'s (1.871×)** | — | **0.5429 (−0.2352)** |

## CONTROLS

| control | returned | |
|---|---|---|
| OBJECT | `generic` ⊆ pool at indices [0,1,2,3] · class rebuilt to **1820** · its own subset is reference **#0** | PASS, else exit 2 |
| E1 | decomposition worst mismatch **2.082e-17** | the algebra is what the code computes |
| PLACEBO | an arm against itself: sd **0.000000** | PASS |
| POSITIVE | jitter 0 → satisfaction rule catches **1**; 0.001 → **0**; 0.005638 → **0**; criterion rule catches **1** throughout | PASS, band computed at both ends |
| **CONFOUND** | `genericpool16` sd **0.0635** vs `generic` **0.0711**, ratio **0.893** | ⭐ **it won — blindness, not membership** |
| COUNTERFACTUAL | the sd swap, labelled a construction | the mechanism, **−0.2352** |

## WHAT DIED

- **my own hypothesis** — that `generic`'s advantage is self-comparison leakage. The blind non-member
  has a *lower* sd; the confound I registered killed the world I expected.
- **`generic`'s `q_resolved` of 0.7780 as a clean number** — it is inflated by roughly 0.235 through
  the variance term, so R786's counterexample survives as a statement about **A2** and its q_resolved
  value is contaminated.
- **the satisfaction-based leave-one-out** — it matches the judge's output where it should match the
  criterion set, and has never fired for the one arm that needs it.

## WHAT SURVIVES

`generic` **is** reference #0 of its own comparator class — an object fact, verified, and worth
recording even though it turns out not to be the mechanism. And R787's variance term, which "did not
fire" on the observed arms, **does** fire here: 0.235 of q_resolved separates a low-variance arm from
a high-variance one at equal A2.

## SCOPE

population 27 arms (R782's 26 plus `genericpool16`) × the 1,820-subset class × 968 prompts ·
instrument A2 over all annotators; q and q_resolved exactly as R781/R782 computed them · baseline the
published values · regime first release, home judge.

## IMPOSSIBLE HERE

| | what it would require |
|---|---|
| scoring `generic` and POOL[0:4] in one pass | a re-run of the judge (R605: no script here writes 98 of 101 sat files) |
| separating judge-pass variance from criterion-set variance | repeated passes of the same arm; the release ships one per arm |
| a leak-free clause ② | a comparator class built to exclude every scored arm's criteria — a different benchmark |
| independently replicated | a second designer; the session prompt forbids agents |

## NEXT

The variance term's size is now measured — **0.235 of q_resolved per 1.87× of sd** — and its direction
is the problem: it rewards arms that track the blind class. A core is supposed to be prompt-specific,
so the clause that certifies it is paying arms for being *less* so. Computed by this round's `run.py`,
the blind arms sit at sd 0.0635–0.0711 against a prompt-specific range of 0.123–0.174 — two bands
that, as computed by this round's `run.py` over the 27 arms, no member of either crosses. The step is a formulation one rather than another measurement:
**clause ② should compare on A2 against a stated cut, which R787 showed loses nothing, instead of on
`q_resolved`, which adds a variance term that runs against the definition's own intent.**
