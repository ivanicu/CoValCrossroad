# R1011 · the definition contains the released core without singling it out

**THE DECISION THIS MAKES SAFE.** Whether the definition, after every repair in this arc, distinguishes
the object it was written from. **It does not.** Five of six admitted arms are not resolvably ordered
against the instance.

---

## The result

Extension under ②′, all arms at full 968-prompt coverage, 8,000 cluster-bootstrap draws:

| admitted arm | Δ (core − arm) | lo | hi | resolvable |
|---|---:|---:|---:|---|
| `topw_k3` | +0.0033 | −0.0029 | +0.0095 | **no** |
| `topw_k4` | +0.0023 | −0.0037 | +0.0084 | **no** |
| `topw_k4_detA` / `_detB` | +0.0023 | −0.0037 | +0.0084 | **no** |
| `topw_k6` | +0.0024 | −0.0032 | +0.0079 | **no** |
| `topw_k8` | +0.0072 | +0.0013 | +0.0130 | core better |

⭐⭐⭐ **The definition admits a set in which the released core has no special status.** It *contains*
the core; it does not *single it out*. That is **"the definition describes the instance" read from the
other side** — the clauses were written from one object and cannot rank that object above the trivial
family they also admit.

## Controls

| control | result |
|---|---|
| **POSITIVE** | core vs `random_k4_s0`: **+0.0738 [+0.0646, +0.0829]** — the instrument can order |
| **NEGATIVE** | `topw_k4_detA` vs `_detB`, a deterministic pair at full coverage: **exactly 0.0000** with a degenerate interval |
| **SHAM** | core vs `coval_core_sham` (ingredient inverted): **+0.0709 [+0.0615, +0.0801]** — a definition whose instance cannot beat its own sham has no content |
| **PLACEBO** | core vs itself: exactly zero |
| **NOISE FLOOR** | the twin interval's width — **measured on a known-zero effect in this same design**, not assumed |

## ⛔ The first negative control failed, and the diagnosis is a defect

v1 used `coval_core_2bA`, which R1005's census reports as agreeing with `coval_core` at **exactly
1.000** — so their A2 difference had to be zero. It returned **−0.0033 [−0.0122, +0.0051]**.

| arm | prompts scored |
|---|---:|
| `coval_core` | 968 / 968 |
| **`coval_core_2bA`**, **`_2bB`** | **200 / 968 (21%)** |
| `promptecho`, `promptecho_sham` | 398 / 968 (41%) |
| the other 92 arms | 968 / 968 |

**The committed A2 loader fills missing prompts with the arm's own mean**
(`np.nan_to_num(v, nan=np.nanmean(v))`, guarded only by `< 200`). So the twins entered R1000's
extension with **79% of their A2 imputed**, and R1005's 1.000 is a statement about the **200 shared
prompts** — its `pair_agree` skipped what an arm did not cover. **Two populations, and the control was
right to refuse.**

⭐ **Bounded, and it states itself:** deduplication removes both twins and the **4 distinct objects are
all at 968/968**. R1004's count of **9** was inflated by duplication **and** imputation; the distinct
figure is clean, and every number in the table above is imputation-free.

## ⚠ Why not R1010's NEXT

It asked for the reader-ratio of each artifact's **strongest** field. **`strongest` is not identified**
— deciding it is a per-artifact judgement, so the quantity cannot be computed without supplying the
answer it is meant to test. **Withdrawn rather than approximated.** (The identified version — the share
of committed fields never read by later code — is a different question.)

And three of the last four rounds were about the loop. This one is about the object.

## ⚠ Impossible here

**Construct validity — N/A.** *"Better"* means **agrees more with this release's own annotators**. A2
is the release's target and there is no external criterion, so nothing here says a better *core*.

**Cross-release — N/A.** One release, one core.

## Alternatives considered

**Report the k=8 cell as "the core is better".** Refused — it is 1 of 6, and reporting the one
resolvable cell while the other five straddle zero is the multiplicity failure with manners.

**Keep the twins in the extension.** Refused once coverage was measured: an arm whose A2 is 79%
imputed cannot carry an admission, and leaving it in would have propagated R1004's inflated count.
