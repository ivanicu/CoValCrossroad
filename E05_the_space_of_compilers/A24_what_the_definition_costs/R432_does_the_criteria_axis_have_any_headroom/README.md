# R432 · before spending GPU on generation, does the criteria axis have any headroom here? — **yes, and the ceiling clears the length rule by +0.2124**

**The decision this round makes safe:** whether to run the generation round R431 named. **Yes** — and
it now has a stated bar and a stated ceiling, neither of which existed before.

## Result — **`W-HEADROOM`**, at zero GPU cost

| weighting | BEST single arm | ORACLE over 5 | HEADROOM | floor |
|---|---|---|---|---|
| **CONV** | 0.4397 (`randblind_s0`) | **0.7129** | **+0.2732** | 0.0091 |
| **INTER** | 0.4527 (`randblind_s1`) | **0.7220** | **+0.2693** | 0.0084 |

**Reference points, committed in R427:** chance **0.4194** · judge-free longest-reply **0.5096**.

> **⭐ The oracle clears the length rule by +0.2124.** *Some* one of five criterion texts ranks the
> human's choice first on **72%** of interactions, while the best single text manages **45%**. A
> selection among criterion texts *can* beat the heuristic — so a prompt-specific arm that fails
> would be failing **about the criteria**, not about the instrument. That is the fact the GPU round
> needed and did not have.

⚠ **What this is not.** The oracle chooses with **hindsight, using the answer**. It is an *upper
bound* on what criterion selection can buy. The next round's arm must be judged against **0.5096**,
never against 0.7220.

⚠ **And the best single arm is a `randblind` one, not `generic`** — consistent with R427, where all
three randblind seeds scored fractionally above generic. Nothing here rescues `generic`.

**Population** 7,342 usable interactions of 7,344 (2 dropped: no `chosen`; 0 with <2 responses; 0
missing an arm) over 2,200 conversations · **instrument** Qwen3.5-2B-Base at k=4 · **regime** n ∈
{2,3,4}, one release, no rubric.

## ⛔ Three control corrections — and two are defects this campaign had already recorded

| # | what it did | why it was wrong |
|---|---|---|
| 1 | POSITIVE: plant the human's choice into **one** arm | headroom **fell** monotonically (0.2693 → 0.1320). The instrument was right: as one arm approaches an oracle, `BEST` rises faster than `ORACLE` and the value of having five arms goes to zero. **HEADROOM measures complementarity**, so the plant must be one only the *union* can see — a **different** arm on each planted interaction. (Ledger: *the control fails for its own reasons*, form ④.) |
| 2 | SHAM: permute each arm's picked **response ID** across interactions | **response ids are unique per interaction**, so a permuted id can essentially never match the chosen one. Null headroom came back **+0.0004** — zero *by construction*. **This campaign recorded the identical defect once already** (R427/`arm_agreement.py`). Fixed the same way: permute **positions**, map back to that interaction's own responses. |
| 3 | the corrected SHAM, used as the kill | **it is a POISON, not a placebo** — see below. Removed from the kill entirely. |

## ⛔ The sham is a poison — measured, named, and demoted

Corrected null headroom is **+0.4767**, *far above* the real **+0.2693**.

The ledger's row says a sham landing **below** the floor means the treatment is sign-flipped. **This
is its mirror.** Permuting each arm independently destroyed criteria content **and the inter-arm
correlation** — and the five arms agree with each other **64–77%** of the time (R427), which
*suppresses* their union. **Its gap bounds `content + decorrelation`, never content**, so it cannot
carry the kill and does not.

**Two admissible references replace it, one derived and one measured:**

- **INDEPENDENCE BOUND** — *a DERIVATION, labelled as one*: were the arms independent with their own
  accuracies, `ORACLE = 1 − Π(1−p_a)` = **0.9432 (CONV) · 0.9490 (INTER)**. Forced by the algebra.
  **The real arms sit between their best single arm and independence: correlated, but far from
  identical.**
- **THE LENGTH RULE** — 0.5096, measured, judge-free. The question the GPU round needs answered is
  whether *any* selection among criterion texts beats it, and `ORACLE` answers that **without a
  null**.

## Controls, final state

| control | returned |
|---|---|
| PLACEBO — oracle over five **copies** of one arm | **0.0e+00** from that arm ✅ |
| g=0 — a no-op plant | **+0.2693 → +0.2693**, unchanged ✅ |
| POSITIVE — union-visible dose sweep | **+0.2693 → +0.2901 → +0.3131 → +0.3507**, monotone ✅ |
| SHAM — 20 within-stratum position permutations | 20 distinct draws, sd 0.0035 ✅ *(and demoted, above)* |
| IDENT — unusable interactions | **2** of 7,344, counted and named |

## Impossible here, named

- **headroom of criteria outside these five texts** — five texts are a *sample* of criterion-space,
  not a basis. Requires generating them, which is the round this one gates.
- **a bias shared by all five arms** — no permutation of five arms detects a bias they all have.
  Requires an arm built on a **different judge**.
- **that any writeable rule reaches the oracle** — the oracle uses the answer. Requires the
  generation round itself.
- **construct validity of `chosen`** — the release's own human choice; no external gold standard.
- **cross-model** — one judge, one k.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
