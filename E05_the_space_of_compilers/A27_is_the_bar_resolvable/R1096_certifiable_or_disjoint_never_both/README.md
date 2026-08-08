# R1096 — **certifiable XOR disjoint** — and the barrier is bookkeeping, not the rule.

**The decision this round makes safe:** whether R1095's scope caveat is a permanent limit of the
release. **It is not.** A comparator family that is both certifiable and disjoint from the candidates
is **one committed selection file away**, and the release simply never wrote one.

## ⛔ Half of this is a derivation, and it is labelled first

R1056's certification rule **types ARMS** — it reads `core_<arm>.json` and keeps the low-diversity
ones. So the certified family is an **arm subset by construction**, and `family ∩ arms = family` at
every threshold. **"Is the certified family disjoint from the candidates?" cannot come out yes.**
That is a fact about the *procedure*, not a measurement of this release, and reporting the overlap as
evidence would be the arithmetic trap.

| threshold | family | overlap with arms |
|---|---:|---:|
| `n_distinct ≤ 1` … `≤ 25` | 2 | **2** |
| … 17 thresholds on R1056's curve | | minimum **2** |

## ⭐ The measurement — the disjoint family is *outside the rule's population*

**0 of the 15 blind subsets are in the certification population at any threshold.** Not
certified-and-failed — **absent from the population the rule ranges over.** They are constructed
objects; the rule reads a per-arm selection file; a constructed subset has none.

**That distinction is the whole point:** an absence and a verdict are different facts with different
repairs, and folding one into the other is how a false acquittal gets made.

## ⭐⭐ The SHAM decides which repair — and it is the cheap one

Give one blind subset the artifact the rule reads, with a single fixed selection, and re-run the
rule: **it certifies.** So the barrier is **bookkeeping, not the rule**.

**A comparator that is both certifiable and disjoint requires one committed per-prompt selection
file for a constructed comparator.** The release does not ship one; the rule would accept it.

## Controls — 5, all green

| control | result |
|---|---|
| POSITIVE the strictest threshold reproduces R918's `fixed` set — R1056's own committed control | PASS |
| g=0 a threshold of 0 yields an **empty** family, not a default | PASS |
| NEGATIVE the blind subsets are absent at **every** threshold, not merely the strict end | PASS |
| SHAM a subset **given** the artifact certifies — isolating bookkeeping from the rule | PASS |
| PLACEBO re-reading the curve returns identical family sizes | PASS |

**Noise floor: none.** The curve and the file list are deterministic reads.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| a family both **certifiable and disjoint** | **N/A in this release as shipped** | **one committed per-prompt selection file for a constructed comparator** — which the SHAM shows the rule would accept |
| certifying an object the rule's population excludes | **N/A** | either the file above, or a rule that ranges over constructed comparators |
| cross-release | **N/A** | a second release |

`run.py` · `results/certifiable_xor_disjoint.json`
