# R1100 — clause ③'s leakage list **survives execution, exactly**. And the authorship axis is confounded, with its witness.

**The decision this round makes safe:** whether ③-scoped statements in this arc rest on a measured
property or on a list of names read out of source. **They rest on a measurement** — the executed
verdict reproduces R1094's `leakage_excludes` on **11 of 11** configurations, **0 disagreements**.
And the same run shows the **authorship** reading has no valid instrument yet, because the arm that
reads nothing human moves under the intervention meant to detect human content.

## ⛔ First, R1099's NEXT is REFUSED as framed — and it was my own sentence

R1099 closed with *"whether the three `topw` arms in the surviving slack are baselines too … computed
by scoring each against the released comparators."* **R1098's committed `released` set already
answers it, and the framing presupposes `topw` has one status.**

| arm | in released ②′ (beats both released comparators) |
|---|---|
| `topw_k1`, `topw_k2` | ❌ |
| `topw_k3`, `topw_k4`, `topw_k4_detA`, `topw_k4_detB`, `topw_k6`, `topw_k8` | ✅ |
| `topw_k12` | ❌ |

⭐ **Six `topw` arms DO resolvably beat both released comparators.** `topw` is neither a baseline nor
a candidate — **`k` decides**, and the admitted region is a **band**: refused at 1–2, admitted at
3–8, refused at 12. This is a **DERIVATION** off a committed set, labelled as one, not a measurement.

⛔ Exactly §4's *the closing sentence is a claim and never gets a control* — written last, acted on
first, and the falsifying table was committed by me two rounds earlier.

## The instrument this round actually attacks

Clause ③ — *consumes no prompt-specific human labels* — is operationalised in this arc by R1094's
`leakage_excludes`: **a list of 19 names, built by READING `corebench/select_core.py`.** R1084
measured a static source read on this repo at **precision 0.111, recall 1.000** and ruled that the
parse *can NOMINATE and cannot DECIDE*. **R1094's list is a nomination this arc has been spending as
a decision.** This round runs the confirmation.

**Method — intervention on the input, real generator, unmodified.** Nine isolated roots; the released
`select_core.py` re-run against data whose structure has been destroyed one axis at a time, comparing
the emitted `sat_<tag>.npz` arrays (*which* criteria were selected) against the identity run.

| axis | intervention | preserved |
|---|---|---|
| **T** | the `assessments` blocks **deranged across prompts** | every record, field, count, and the join |
| **P** | each prompt's `coval_full` **deranged across records** | the join keys, untouched |
| **identity** | byte copy, nothing deranged | everything — the g=0 guard |

## ⭐ The result — 11 configurations, 2 axes, 22 cells, all reported

| configuration | T: consumes the human target | P: selection moves | in R1094's list | agree |
|---|---|---|---|---|
| `topw_k1` · `topw_k4` · `topw_k12` | **blind** | moves | ❌ | ✅ |
| `topabs_k4` · `topvar_k4` · `topwvar_k4` | **blind** | moves | ❌ | ✅ |
| `random_k4` · `full` | **blind** | moves | ❌ | ✅ |
| `indep_k4_fit1` · `greedy_k4_fit1` · `oracle_k4_fit1` | **CONSUMES** | moves | ✅ | ✅ |

**T: 3 consume, 8 blind. Disagreements with the name list: 0.** All three verdicts agree across
**3 seeds**, and the identity run is byte-stable across all three.

⭐ **World A survives. The name list IS the measurement here** — so R1094, R1095 and R1099's
③-scoped statements are not resting on a string match, and that is now a fact rather than a hope.
**This is Closure, and it is labelled as Closure**: nothing about the definition changed. What
changed is that a load-bearing instrument stopped being unverified.

## ⛔ And the P axis carries NO authorship claim — its own placebo says so

`coval_full` is **crowd-written, prompt-specific, human-authored**, with human-assigned signed
weights (dataset card, *"Annotators could also author their own rubric items"*). So it is tempting to
read *"the arm moves under P"* as *"the arm consumes prompt-specific human labels"* — clause ③'s
**authorship** reading — which would exclude **all 11** configurations, including the six `topw` arms
the released ②′ set admits.

⚠ **That reading is invalid, and the round computes the witness rather than asserting it.**
`random_k4` **moves under P** — and it reads **no criterion text, no human weight and no human
label**, drawing uniformly from the judged index set; the only human-determined thing it touches is
**how many** criteria the prompt has. **So P measures *the record moved*, not *authorship was
consumed*.** It cannot
separate `consumes the human WEIGHTS` from `consumes the candidate SET`, and no authorship statement
may be built on it. §4's *the instrument's unit is not the claim's unit*, caught by the placebo
firing on the axis it was not declared for.

## The gauge test that would have made every answer wrong, measured before the round

`select_core.py` computes `ROOT = Path(__file__).resolve().parent.parent`. **`.resolve()` follows
symlinks.** Executed on a symlinked copy:

```
resolve -> /home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable
```

**A symlinked generator reads the REAL data**, every intervention becomes a silent no-op, and every
configuration returns `blind` — including the oracle. `shutil.copy2` in `build_root` is load-bearing,
and the POSITIVE control (`oracle_k4_fit1` must move under T) is what makes that failure visible
rather than flattering.

## Controls — 9, all green

| control | result |
|---|---|
| POSITIVE T `oracle_k4_fit1` moves when the rankings are deranged | PASS |
| POSITIVE P `full` moves when the rubric pairing is deranged | PASS |
| g=0 the identity intervention changes **nothing**, every configuration | PASS |
| PLACEBO `random_k4` is unchanged on T | PASS |
| NEGATIVE the derangements have **zero** fixed points | PASS |
| NEGATIVE record counts preserved by every intervention | PASS |
| NEGATIVE the join size identical across configurations | PASS |
| SEEDS every verdict agrees across 3 seeds | PASS |
| SEEDS **the seed flag changes the draw** — 3 distinct oracle emissions under T | PASS |

⚠ The last one exists because *"agrees across 3 seeds"* is worthless if the three seeds silently
produced the same permutation — that would be **one run reported three times**, and it would read as
the strongest line in the table.

**The kill was gated on its own controls** — `if pos_ctrl and identity_clean: evaluate(threshold)
else: UNVERIFIED` — so a disagreement found while the harness was broken could not have been
published as a kill.

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| the executed verdict for `coval_core*`, `gen`, `generic`, `genericpool16` | **N/A** | their generators. `select_core.py` does not produce them, and `core_generic.json` is a **fixed 4-criterion list repeated on all 968 prompts** — it has no rule to re-run |
| the verdict for `*_08bR` arms | **N/A** | the 8B judge npz — a different instrument axis, and mixing it would make the comparison unattributable |
| the verdict for `*_detA/B`, `*_kA/kB` | **N/A** | the tag-suffix provenance of those variants, which is not recorded in `select_core.py` |
| separating **weights** from **candidate set** on the P axis | **N/A here** | a within-prompt derangement of the per-criterion `scores` — named in NEXT, not attempted here |
| cross-release | **N/A** | a second release with its own generator |

`run.py` · `results/leakage_executed.json`
