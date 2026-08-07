# R401 — the transport route is closed at n=99; the clause-② route is open by two orders of magnitude

**The decision this makes safe:** *is the depth-matched transport test worth GPU?* **No — and the
same arithmetic shows which test is.**

## Result — `W_UNDERPOWERED`. Three controls pass. **No GPU spent — that is the finding.**

### ⛔ The MDE formula is a DERIVATION and is labelled one

`MDE = ZEFF · sd / √n` **could not have come out otherwise.** It is algebra, not evidence. What is
*not* forced — and is this round's only contribution — is the **comparison**: the derived resolution
floor set beside the effects this campaign has actually measured.

### The curve at n = 99, swept over the discordance rate

| `p_d` | MDE | vs largest measured (**+0.0992**, R368 exact) |
|---:|---:|---|
| 0.05 | 0.0630 | 0.63× resolvable |
| 0.10 | 0.0890 | 0.90× resolvable |
| **0.15** | **0.1091** | **1.10× UNRESOLVABLE** |
| 0.20 | 0.1259 | 1.27× UNRESOLVABLE |
| 0.30 | 0.1542 | 1.55× UNRESOLVABLE |
| 0.45 | 0.1889 | 1.90× UNRESOLVABLE |
| 0.60 | 0.2181 | 2.20× UNRESOLVABLE |

**10 of 12 cells unresolvable (83%).** **Crossing at `p_d` = 0.1241** — the test resolves *only* if
the two arms disagree on **fewer than 12.4%** of conversations. Two differently-constructed criterion
sets judging the same responses do not agree that closely.

## ⛔ And the verdict is scoped to ONE design — which I almost failed to notice

`n = 99` binds a **depth-matched cross-corpus** test. But **clause ② is an INTRA-corpus comparison** —
a core against a prompt-blind size-matched set, both scored on the *same* conversations. **That design
never touches CoVal's sample, so CoVal's 1,078 conversations do not bound it.**

| design | n | MDE @ `p_d`=0.30 | |
|---|---:|---:|---|
| interactions with one `if_chosen` (R399) | **26,886** | **0.0094** | resolvable |
| conversations (R398) | **8,011** | **0.0171** | resolvable |
| depth-matched cross-corpus (priced above) | 99 | 0.1542 | **UNRESOLVABLE** |

> **⚠ They are different questions.** *"Does a core transport from CoVal to here"* is **not** *"does
> clause ② hold here"*. The second is answerable and cheap; **it is not a substitute for the first.**
> Quoting the closed route as though it closed the open one — or the reverse — is exactly the scope
> error this campaign keeps paying for.

## Controls

| | returned |
|---|---|
| **MDE (+)** | at n = 1,000,000 → **0.00048**, below the *smallest* effect — `PASS` |
| **MDE (−)** | at n = 4 → **0.7674**, above the *largest* — `PASS`. Together these establish **floor < threshold < ceiling** rather than assuming it — the *"control that cannot PASS"* failure, built 4× here |
| **MONOTONE** | strictly decreasing over n ∈ (10, 50, 100, 500, 1000): `0.4852 → 0.2170 → 0.1534 → 0.0686 → 0.0485` — `PASS`. A function returning a constant would pass a single-point check |
| **EFFECTS** ⭐ | all four reference effects **asserted present in `DEFINITION.md`** before use, so they inherit that document's gate. *A number I recall is a number I may have invented* |
| **GRID** | the whole `p_d` range printed, including the two cells that would have killed the verdict |

## ⚠ Two directional caveats, both stated before the run

1. **`sd = √p_d` holds under a symmetric null.** With a non-zero effect the variance is slightly
   smaller, so this MDE is **mildly conservative — it makes `underpowered` HARDER to conclude, not
   easier.** Stated because a conservative approximation pointing at my preferred answer would be
   worth nothing.
2. **Transporting an effect *size* is itself an assumption.** The reference effects were measured on
   CoVal; the second corpus could carry a larger one. **What is not an assumption is `n = 99`, and n
   is what sets the floor.**

## Register

| criterion | status |
|---|---|
| **measuring `p_d`** | **N/A** — needs both arms run, which is the test being priced. Swept instead |
| **the effect's true size on corpus two** | **UNKNOWN** — CoVal's effects used as reference, and that substitution is named |
| **a one-sided design's smaller MDE** | **N/A** — would need a pre-registered direction, which clause ② does not commit to on a new corpus |

## The sentence I can no longer write

> *"the second corpus opens transport"* — **without saying which transport.** The cross-corpus route
> is closed at depth-matched n by a factor of 1.6×; the intra-corpus clause-② question is open with
> ~100× the sample. **One discovery, two fates.**

Artifact: `results/r401_power_at_99.json`, source-stamped.
