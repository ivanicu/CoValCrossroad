# R986 · the definition names a scalar size, and the released core does not have one

**THE DECISION THIS MAKES SAFE.** Whether clause ①'s *"its size"* can be read as a number. **Not for
`coval_core`** — the released core's per-prompt size runs **2 to 4**, with a **43-prompt residual**
that pool capping does not explain.

---

## The clause, read from the object

`DEFINITION.md:61`:

> Its size, **under that same judge J**, is **greater than one**.
> *(Reported, not required: sizes **3 to 8 are not distinguishable** by this release.)*

**"Its size" is a scalar**, and so is the parenthetical. **34 of 96 arms have no scalar size.**

## The decomposition — two causes, and only one is about the arm

| | |
|---|---|
| arms with a variable per-prompt size | **34 of 96** |
| explained **entirely** by pool capping — the prompt offers fewer criteria than the rule asks for | **28** |
| with a **residual**: the arm selects fewer than the pool allows | **6** |

| arm | nominal | min | max | residual prompts | share |
|---|---|---|---|---|---|
| **`coval_core`** | 4 | **2** | 4 | **43** | 4.4% |
| `coval_core_sham` | 4 | 2 | 4 | 43 | 4.4% |
| `coval_core_2bA` / `_2bB` | 4 | 3 | 4 | 8 | 4.0% |
| `gen` / `gen_sham` | 4 | **1** | 4 | 2 | 0.2% |

⭐ **Pool capping is a fact about PROMPTS, not arms** — all four `k12` arms share a byte-identical
per-prompt profile, as do the `k8` and `k6` families. **The residual is the part that belongs to the
arm**, and `coval_core` has one.

## What this does and does not change

- **`coval_core`'s verdict is unaffected**: its minimum is 2, so it clears *"greater than one"* under
  every reading. **The problem is the type, not the truth.**
- **`gen`'s verdict IS affected**: minimum 1. Under *min per-prompt size > 1* it fails clause ①;
  under *nominal k > 1* it passes. R985 found this disagreement; here is its cause.
- **The parenthetical is worse off than the clause.** *"Sizes 3 to 8 are not distinguishable"*
  presumes each arm has one size to compare. For 34 of 96 there is no such number.

## ⛔ The control failed first, and the population was the reason — the fifth time this session

v1 grouped arms by **modal k** and the positive control returned **25 of 26**. The one mismatch was
`full` vs `full_sham` — a pair that **should** differ, since a sham draws a different prompt's
criteria, and whose modal 13 is a summary of a 4..39 distribution that means nothing.

⭐ **The repair is a classifier read from the object, not a name list**: an arm draws from the
prompt's pool iff its size never exceeds it. That separates

| class | members |
|---|---|
| prompt-pool | 97 |
| pool-exhaustive (`size == pool` everywhere) | **1** — `full` |
| external-pool (`size > pool` somewhere) | **2** — `full_sham`, `genericpool16` |

`genericpool16` carries **16 criteria where the pool is 4**, so `min(k, pool)` was simply the wrong
baseline for it and its 54.9% "residual" was an artefact of my population, not a property of the arm.
With the classification applied, the control is **25 of 25**.

## Controls

| control | result |
|---|---|
| **POSITIVE** | arms sharing a nominal k share an identical per-prompt profile — **25 of 25** |
| **NEGATIVE** | `full` equals the pool exactly — the pool proxy is the pool |
| **PLACEBO** | `topw_k1` (nominal 1, minimum pool 4) shows **zero** variation |
| **NOISE FLOOR** | none quoted — these are counts, not estimates |

## What this deliberately does not do

It establishes that *"its size"* is **ambiguous** between the rule's nominal k, the realised
per-prompt size, and arm-specific selection. **Which reading the clause should take is an authorial
decision, not a measurement**, and this round does not make it. Naming the ambiguity and choosing the
resolution are different acts, and only the first is evidence.

## Alternatives considered

**Rewrite the clause to say "nominal size".** Refused here: the clause text is anchored by 343
assertions and L81 says annotate rather than rewrite — and more importantly, the choice between the
three readings changes `gen`'s verdict, so it is a decision that should be made deliberately rather
than folded into a measurement round.

**Report `coval_core` as failing clause ①.** It does not. Its minimum is 2 under every reading. The
finding is about the clause's **type**, and inflating it to a verdict would be the more dramatic
claim the data does not support.
