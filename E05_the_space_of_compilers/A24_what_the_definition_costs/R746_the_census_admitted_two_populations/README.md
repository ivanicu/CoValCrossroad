# R746 · the census admitted arms measured on two different populations

**The four unresolved tags are REPLICAS — `topw_k4_detA/detB` are identical to `topw_k4` on all
15,488 cells, and `coval_core_2bA/_2bB` are identical to `coval_core` on all 3,168 cells they share
with it. So the census's 11 extra admissions contain no new SELECTOR object: 7 are the target-reading
class ③ excludes and 4 are duplicates already counted. ⛔ And underneath the naming question: prompt
coverage over the 92 takes 4 distinct values from 4 to 968, the committed extension is all at 968, and
the two `_2b` admissions sit at 200.**

## check #348 — the previous NEXT proposed an instrument undefined on half its subject

R745 closed by proposing R525's exact identity relation on today's 92. ⛔ **File sizes killed half of
it before any code existed:**

| arm | bytes | cells | prompts |
|---|---|---|---|
| `sat_coval_core.npz` | 100,207 | 15,312 | **968** |
| `sat_coval_core_2bA/2bB.npz` | 22,161 | 3,168 | **200** |
| `sat_topw_k4.npz` | 100,313 | 15,488 | 968 |
| `sat_topw_k4_detA/detB.npz` | 100,313 | 15,488 | 968 |

**Identity between vectors over different cell sets is not false — it is undefined.** The comparison
had to be restricted to shared cells, which is a weaker relation, and R746 says so rather than
reporting a verdict the relation cannot carry *(ledger 1004)*.

## E2 — identity ON SHARED CELLS, sound in one direction only

| pair | identical | shared / larger |
|---|---|---|
| `topw_k4_detA` vs `topw_k4` | **✓** | 15,488 / 15,488 = **1.000** |
| `topw_k4_detB` vs `topw_k4` | **✓** | 15,488 / 15,488 = **1.000** |
| `topw_k4_detA` vs `topw_k4_detB` | **✓** | 15,488 / 15,488 = **1.000** |
| `coval_core_2bA` vs `coval_core_2bB` | **✓** | 3,168 / 3,168 = **1.000** |
| `coval_core_2bA` vs `coval_core` | **✓** | 3,168 / 15,312 = **0.207** |

⚠ **`identical ⇒ indistinguishable THERE` · `not identical ⇒ different objects`.** The `_2b` verdict
covers 20.7% of `coval_core`'s cells and is a **bound**, not a proof of sameness elsewhere.
⚠ Whether the **7 target-reading tags** are 7 **objects** is not measured here. R730's precedent — 7
tags collapsing to 4 — says expect fewer. **`UNVERIFIED`.**

## E1 — the coverage grid, 3 definitions × 3 populations

| definition | population | min | median | max | distinct | below max |
|---|---|---|---|---|---|---|
| **prompts** | **admitted(16)** | **200** | 968 | 968 | **2** | **2** |
| prompts | added(51) | 4 | 968 | 968 | 3 | 3 |
| prompts | all(92) | **4** | 968 | 968 | **4** | 5 |
| cells | admitted(16) | 3,168 | 15,488 | 30,680 | 6 | 15 |
| cells | added(51) | 256 | 15,488 | 43,812 | 9 | 47 |
| cells | all(92) | 256 | 15,488 | 59,936 | 13 | 90 |
| pairs | admitted(16) | 792 | 3,872 | 7,670 | 6 | 15 |
| pairs | added(51) | 64 | 3,872 | 10,953 | 9 | 47 |
| pairs | all(92) | 64 | 3,872 | 14,984 | 13 | 90 |

⭐ **The committed extension is uniform: `coval_core`, `topw_k3`, `topw_k4`, `topw_k6`, `topw_k8` — all
968.** The heterogeneity arrived with the drift.

## ⛔ the arithmetic was derived BEFORE the measurement, and it points away from a defect

`R728.decide()` computes `mde = ZEFF·std/√n`. At equal `std`, **968 → 200 multiplies the bar by
2.2000**. Low coverage makes admission **harder**.

**Realised:** the low-coverage admissions cleared a mean `mde1` of **0.026962** against **0.013275**
for the rest — a **2.03×** wider bar, matching the derivation. **They were admitted despite a harder
threshold.**

⛔ **My verdict string asserted the opposite and the same run refuted it three lines above.** v1
branched on the share comparison alone and printed *"low coverage is an admission advantage — the
construction is wrong on its own terms"* while `harder` sat computed and unused. **Over-representation
and advantage are different claims and only the first was measured** *(ledger 1006)*. The branch now
references the threshold it had already computed, and the mechanism is reported as **unexplained**.

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| B1 distinct coverage values over the 92 | 3, band [1, 10] | **4** | in band, point wrong |
| B2 added arms below 968 | 8, band [0, 51] | **3** | in band, point wrong *(1007)* |
| B3 committed extension all at 968 | yes | **yes** | ✓ |
| B4 admitted arms below 968 | 2, band [2, 16] | **2** | ✓ (≥2 was forced by the sighting) |
| B5 the five identity tests | all yes | **all yes** | ✓ |
| **D** coverage does not predict admission | true | **false** — 0.1250 vs 0.0395 | ⛔ |

⚠ **World A was already dead before registration and the preregistration says so.** I had seen the
200-prompt coverage while inspecting the objects, so no blind prediction was registered about it —
second declared sighting in two rounds.

## controls — 6 PASS, 0 FAIL

| control | returned |
|---|---|
| **POSITIVE** | the parser separates two arms whose **file sizes** differ **4.52×** — a signal it never reads. Band computed: a constant parser cannot separate them (floor), the real one does |
| **g=0** | an arm with empty meta → `UNREADABLE`, never `0` prompts. **A silent zero would have entered the low-coverage count and manufactured World B.** None found, and the list is printed |
| **NEGATIVE** | parsing field 1 instead of field 0 moves coverage on **20/20** sampled arms |
| **SHAM** | ingredient **absent**: the same counting on the **76** arms the census did **not** admit — 3/76 low-coverage |
| **PLACEBO** | each arm's coverage against itself → **0** on all 92 |
| **UNIT** | every tag resolves to exactly one `.npz`; asserted, not assumed |

## the sentence I can no longer write

*"the four suffixed tags might be new objects."* All four are identical, on every cell they share, to
members of the committed extension.

## NEXT

The census's admitted set is 16 tags and, after this round, at most 12 distinct objects — and the
uncounted part is the 7 target-reading tags, which R730's method resolves. Applying exact identity
within that family gives the object count of the admitted set, which is the number the deliverable
should carry instead of 16. The registered quantity is that object count against the tag count of 16;
R730 measured 7 tags collapsing to 4 in a neighbouring family, so a collapse is expected here and its
size is the measurement. The design question to settle first is whether identity is computed within
the target-reading family alone or against the whole 92, since a target-reading arm identical to a
SELECTOR arm would be a finding about the rules rather than about the tags.
