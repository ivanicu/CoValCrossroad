# R724 · could the producer have returned otherwise

**Decision this makes safe:** whether the one computation the deliverable now rests on (R294, after
R723) is a measurement or a derivation. **It is a measurement — 6 distinct extensions are reachable
across 100 defensible cells and the released 5-set is modal at 30.0%.** So R723's "one independent
computation" survives as one rather than collapsing to zero.

## The specification curve — 100 cells, all reported
`clause-① rule ×5 · clause-② rule ×5 · clause③ on/off ×2 · k-capped arms kept/dropped ×2`

| cells | size | extension |
|---|---|---|
| **30** | 5 | **coval_core, topw_k3, topw_k4, topw_k6, topw_k8 — RELEASED** |
| 30 | 9 | the same five + `oracle_k4`, `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` (③ off) |
| 10 | 1 | **`topw_k6` alone** |
| 10 | 5 | `topw_k6` + the four ③ excludes |
| 10 | 7 | + `generic`, `topw_k2` |
| 10 | 11 | + `generic`, `topw_k2` and the four ③ excludes |

The released set is the answer of **15 of 25** clause-①② rule combinations with ③ on.

## ⭐ The cell that matters: the released core drops out
**All 5 combinations reading clause ② as `lo > mde` — the whole interval above resolution — exclude
`coval_core`, whatever rule clause ① takes.** The surviving arm is `topw_k6`, and it is alone.

`coval_core`'s clause-② interval is `[0.008274, 0.024117]` against `mde2 = 0.010616`: its **effect**
clears resolution, its **lower bound** does not. R294's rule (`lo > 0` **and** `|eff| ≥ mde`) admits
it; the stricter reading does not. So the released core's membership in its own extension rests on
reading clause ② as *effect above resolution* rather than *interval above resolution*, and that is a
choice, not a fact about the arm.

## ⚠ One swept axis could not have changed anything
**`drop_kcap` is inert across all 50 rule combinations** — identical extension in every pair. R294
flagged k-capped arms as favoured by their comparison, and correctly; but no k-capped arm's
admission is rule-sensitive here, so sweeping it was free and told us nothing. *An axis that cannot
move the answer belongs in the report as such, not as evidence of breadth.*

## Registered
| point | registered | measured | in interval |
|---|---|---|---|
| A distinct extensions | 12 [2, 100] | **6** | yes |
| B released share | 0.25 [0, 1] | **0.30** | yes |
| C size with ③ off | 7 [5, 41] | **9** | yes |
| DIRECTIONAL released == modal | — | **holds** (30 cells) | — |

⛔ **C is a DERIVATION, not evidence.** Turning ③ off can only *add* the arms ③ excluded, so
`C = 5 + |{a ∈ USES_PROMPT_LABELS : a clears ①②}|` by algebra. It came out 9 and the four added arms
are exactly `oracle_k4, oracle_k4_fit1, greedy_k4_fit1, indep_k4_fit1`. Registering it made the
arithmetic explicit; it is not a test and is not quoted as one.

## Controls — 6 PASS, 0 FAIL
**g=0 / POSITIVE**: the reconstruction reproduces R294's committed `admitted` on **41/41** arms,
band `floor 0 < t 41 ≤ ceiling 41` — a reconstruction that cannot reproduce the committed set
licenses nothing · **PLANT**: maximal-margin arm clears all 5 rules, zero-margin arm clears none
(the half that must fail) · **NEGATIVE**: arm→statistics pairing permuted, released set not
recovered — excluding *"the rule returns the same set whatever the data"* · **SHAM**: criteria
removed → all 41, absence not inversion · **PLACEBO**: released cell against itself → symmetric
difference exactly 0 · **UNIT**: instrument and claim units stated separately with the residue named.

## Residue, stated rather than waived
The bootstrap seed, `NBOOT`, the BH `q` and the ≥2-annotator population filter are **fixed inside
the artifact** and would need R294's census re-run against the sat store. **So 6 is a lower bound on
the reachable extensions, never a count of them.**

**Reproducibility:** byte-identical under `PYTHONHASHSEED` 0 and 9137.
**Artifact:** `results/r724_producer_degrees_of_freedom.json` · 100 cells persisted individually.
