# R745 · are the added arms candidate cores, or our own apparatus?

**`16` is not a rival number to `5`. Of the 11 arms the census newly admits on today's population,
**7 are TARGET-READING** — `oracle_k`, `greedy_k`, `indep_k`, the exact class clause ③ exists to
exclude — and the remaining 4 carry caller-supplied suffixes (`coval_core_2bA/2bB`,
`topw_k4_detA/detB`) that this instrument **cannot** resolve. **Zero of the 11 is an established new
candidate core.** The partition is read off `select_core.py`, not chosen by me.**

## check #347 — it holds, and the design it proposed does not survive its own cost

✓ `assurance/what_did_each_check_actually_read.py`'s docstring states it uses `sys.addaudithook` and
records the repo files each process opens.

⛔ **But executing 16 rounds to compare *named* against *opened*** means running bootstraps of
1,200–76,800 resamples **and overwriting their committed `results/*.json`** — the instrument would
mutate the objects it measures. And `opened ⊅ depends-on` in either direction: a round can open a
file and discard it, or depend on data an import already loaded. **Deferred with the reason stated,
not silently dropped.**

## the gap this round took instead, and P4 on it

R728's own artifact records its residue verbatim: *"whether R294's construction is the right one is
not addressed here."* It found the census admits **16** on today's 92-arm store versus **5** on the
committed 41, and called that *"not a correction to the extension — a scope condition."*

| layer | result |
|---|---|
| **L1** live code | `select_core.py` — supplies the grammar; **REUSE**, the partition is read off it |
| **L3** this project | R487 censused the store at **101** and asked which arms are *scorable*; R478 (1,820-subset class), R637 (the observer in the file tree), R652 (population depth) — **none asks whether the added arms are candidate cores** |
| ⇒ | **TRUE GAP.** No recomputation needed: R728's artifact already records `population_drift_new_arms` (51), `extra_admits_today` (11), `extension_over_todays_population` (16) |

## identification — read off the builder, asserted in code

| line | what it establishes |
|---|---|
| `select_core.py:50-52` | the rule vocabulary is a **closed set of nine** |
| `:102` | `if a.rule in ("oracle_k", "indep_k", "greedy_k"):` **loads the human target** |
| `:204` | the tag is **emitted by the builder** from rule + k + seed + fit-parity + suffix |

⇒ **TARGET-READING** `oracle_k · indep_k · greedy_k` · **RANDOM** `random_k` · **CEILING** `full` ·
**SELECTOR** `topw_k · topabs_k · topvar_k · topwvar_k`. All three provenance assertions are checked
against the source at runtime; the round **exits 2** if the builder does not carry them.

⚠ **The gauge test bounds the scope.** A name is invariant under renaming while the property is not,
so name classification is blind **in general**. It is admissible here **only** because the builder
emits the tag from the rule. Anything not parsing under that grammar returns **`UNPARSED`** and is
never folded into a class.

## the grid — 3 classifiers × 3 populations, and the curve is FLAT

| classifier | population | SEL | TGT | RND | CEIL | UNPARSED | non-SEL share |
|---|---|---|---|---|---|---|---|
| loose | added(51) | 14 | 13 | 20 | 0 | 4 | 0.7021 |
| **tight** | **added(51)** | **14** | **13** | **20** | **0** | **4** | **0.7021** |
| family | added(51) | 14 | 13 | 20 | 0 | 4 | 0.7021 |
| loose | newly admitted(11) | 2 | 7 | 0 | 0 | 2 | 0.7778 |
| **tight** | **newly admitted(11)** | **2** | **7** | **0** | **0** | **2** | **0.7778** |
| family | newly admitted(11) | 2 | 7 | 0 | 0 | 2 | 0.7778 |
| tight | committed extension(5) | 4 | 0 | 0 | 0 | 1 | **0.0000** |

⚠ **The specification curve is flat — and that is a fact about these tags, not robustness.** Every
tag here is builder-emitted with a clean rule prefix, so loose, tight and family **could not have
differed**. Reporting a flat curve as agreement would be claiming a test that did not run.

## the 11, named

| tag | class | what it is |
|---|---|---|
| `oracle_k4_08bR`, `oracle_k4_oracle_kA/kB` | **TARGET-READING** | reads the human target at `:102` |
| `greedy_k4_greedy_kA/kB` | **TARGET-READING** | same |
| `indep_k4_indep_kA/kB` | **TARGET-READING** | same |
| `coval_core_2bA`, `coval_core_2bB` | **UNPARSED** | `coval_core` is not a builder rule |
| `topw_k4_detA`, `topw_k4_detB` | **SELECTOR** | the one candidate-core family present |

⚠ **`UNVERIFIED`, and it is the sentence I most want to write:** the suffixes `_2bA/_2bB` and
`_detA/_detB` *look* like second-judge and determinism replicas of `coval_core` and `topw_k4`, both
already in the committed extension — which would make the 11 contain **no new object whatsoever**.
`tag_suffix` is **caller-supplied**, not rule-emitted, so the gauge test's own bound forbids reading
it. **Settling this needs R525's satisfaction-vector partition on today's 92**, not a name.

## registered vs measured

| | registered | measured | |
|---|---|---|---|
| P1 share of the 51 parsing | ≥ 0.70 | **0.9216** | ✓ |
| P2 non-SELECTOR share of the 51 | 0.55, band [0.20, 0.90] | **0.7021** | ✓ in band |
| P3 non-SELECTOR of the 11 | 9, band [0, 11] | **7** | in band, point wrong |
| **D** the 11 are more non-SELECTOR than the 51 | true | **true** (0.7778 vs 0.7021) | ✓ |

⚠ **P3 was PARTIALLY SIGHTED and it is declared in the preregistration**: while checking that R728's
artifact carried the objects at all, a truncated print showed **6 of the 11 names** before I
registered. An undeclared sighting is an unavailability claim in the flattering direction.

⛔ **The 11 are a SUBSET of the 51** — not independent draws. D is a within-population contrast and
**no significance is claimed for it.** A derivation, labelled.

## controls — 6 PASS, 0 FAIL

| control | returned |
|---|---|
| **PROVENANCE** | all three source assertions hold against `select_core.py`; the round exits 2 otherwise |
| **POSITIVE** | `random_k8_s0 → RANDOM`, `topw_k4 → SELECTOR`, in **different** classes. Band computed: at a floor classifier assigning everything one class the two **cannot** separate (`False`), at the real one they do |
| **g=0** | `coval_core`, `zzz_not_a_rule`, `generic_reprov` → **`UNPARSED`**. A silent `SELECTOR` default would have **manufactured World A** |
| **NEGATIVE** | rule→class shuffled: `{TGT 29, SEL 14, CEIL 2, RND 2}` vs real `{RND 20, SEL 14, TGT 13}` — the classification is destroyed |
| **SHAM** | ingredient **absent**: the committed extension, non-SELECTOR **0/4 parsed** vs the added set's 0.7021 |
| **PLACEBO** | 10 non-tag strings → **0 in every class**, reported as **0 of 10**, not 0 of 0 |

⚠ **The SHAM's shortfall is stated, not papered over.** R728's artifact records the committed
**count** (41) but not the committed **names**, so the sham ran on the **5** it does record. Five is a
subset of forty-one and a small one.

## what this changes in the deliverable

| before | after |
|---|---|
| *"the same procedure re-run over today's population admits **16**, not 5"* *(R728, on the page)* | still true, and **7 of the 11 extra are the target-reading class ③ exists to exclude** |
| *"the latent defect is now realised"* | **the realisation is our own apparatus entering the population**, not new cores appearing |
| the extension as population-indexed | **World A killed**: the wider population is not a wider sample of cores |

## the sentence I can no longer write

*"the extension is 5 on the committed population and 16 on today's."* The 16 counts seven arms that
read the human target and four whose provenance this instrument cannot resolve.

## NEXT

The four unresolved tags are the whole residue, and the instrument that settles them exists: R525
partitioned 56 tags into objects by **exact satisfaction-vector identity**, and R730 reused it to
turn 7 tags into 4 objects. Applying it to today's 92 answers whether `coval_core_2bA/2bB` and
`topw_k4_detA/detB` are distinct objects or replicas of extension members already counted — and the
same partition gives the per-OBJECT class shares this round could report only per TAG, which is the
limit named in its own impossibility register. The registered quantity is the object count of the 11,
against the tag count of 11; R730's precedent says a tag count of 7 collapsed to 4, so a collapse
here is expected and its SIZE is the measurement.
