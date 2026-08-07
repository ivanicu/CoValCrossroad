# R453 · clause ② is **partially** within-family — and a mismatched attack nearly retracted a true claim

**The decision this round makes safe:** whether clause ② tests prompt-specificity or ranks within the
prompt-blind family. **Partially the latter.** `W-PARTIAL`, reported as a bound.

## ⛔ The announced test was forced — one line of arithmetic

R452 closed proposing to *"compute the share of the BEST fixed prompt-blind subset."* The share of a
subset is the fraction of the 1,820-member class it beats — and the best subset **is a member of that
class**, selected by exactly the quantity the share ranks on. **Near 1 by construction.**
*Twenty-first announced step checked, its statistic killed.*

**The non-circular form is a hold-out**, which is precisely the instrument that prices a winner's
curse: choose on one half of the prompts, score on the other.

## Result — every number at n=484, in-sample printed beside held-out

| selector | IN *(derivation)* | **HELD-OUT** |
|---|---|---|
| best fixed subset | 0.8508 | **0.5773** [0.3188, 0.7456] |
| released core | 0.8433 | **0.8194** [0.4522, 0.9802] |
| g=0 (objective destroyed) | 0.1160 | 0.1327 |
| worst-on-train | 0.0000 | 0.0000 |

> **A fixed, prompt-BLIND set reaches 0.5773 on prompts it was never chosen on** — well above the
> class floor **0.2198** and above g=0's **0.1327**, but below the core's **0.8194**. On the
> floor→core scale that is **59.6%** of the way.

**So clause ② is not purely a prompt-specificity test — but the released core still clearly beats the
best *generalising* prompt-blind set.** The honest output is that bound, not a verdict either way.

The core drops only 0.8433 → 0.8194 because it is **not selected on train** and suffers no curse.
The best fixed subset drops **0.2734** — the winner's curse, priced.

## ⭐ The near-miss that matters more than the result

My first re-pricing of R452 selected on train by **highest mean A2** and asked how often that subset
won held-out prompts: **0.32%**, against R452's committed **33.57%**. A 100× collapse. It would have
read as *"R452's concentration was selection noise"* and retracted a true claim.

**R452 selected by a different rule — the subset that WINS THE MOST PROMPTS.** Two different objects.
Matched to R452's own rule:

| | train | **held-out** |
|---|---|---|
| top subset's win share | 33.47% | **33.68%** [31.29%, 36.43%] |

**R452's 33.57% survives out-of-sample essentially unchanged. It is real and it generalises.**

⛔ This is §3's warning made concrete: *a cheap attack that appears to kill a claim is the most
expensive kind of error, because it retracts something true.* The attack was not cheap in compute —
it was cheap in **checking that its two sides were the same object.**

⭐ **And the pair is a finding in its own right:** selecting by *wins-most-prompts* generalises
perfectly (33.47 → 33.68); selecting by *highest mean A2* loses 0.2734 to the curse. **Two defensible
selection rules on the same matrix, opposite robustness.**

## ⛔ The anchor also compared two different objects — third time in four rounds

The first anchor required the core's **half-sample** held-out share to reproduce its committed
**0.9841**. It returned 0.8194 and printed `⛔ FAIL`. **The arithmetic says why:** `share` counts
references beaten by more than `ZEFF·sd/√n`, so at n=484 the bar is **√2 = 1.41× higher** and *every*
half-sample share is structurally lower. Same family as R450's floor anchor.

Repaired into two separate checks, which is what it should have been:

| anchor | returned |
|---|---|
| PIPELINE — the core at the committed n=968 | **0.9841** vs 0.9841 ✅ *exact* |
| REFERENCE — the core on half-samples, the bar every selector is compared to | 0.8194 |
| g=0 — selection with the objective destroyed | 0.1327 vs floor 0.2198 ✅ |
| NEGATIVE — worst-on-train | 0.0000 ✅ *selection transfers* |

## Impossible here, named

- **whether a generalising prompt-blind set is "really" a core** — needs a standard outside this
  definition.
- **transfer across corpora** — would need the pool's 16 criteria scored on the second release; they
  do not exist there.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
