# R1101 — `topw` **ranks by prompt-specific human ratings**, 11 of 11 cells as pre-registered. And the authorship reading, applied consistently, admits **nothing**.

**The decision this round makes safe:** whether clause ③'s AUTHORSHIP reading can be executed rather
than named. **It can** — and the price of executing it is that the released ②′ set goes to **zero**.
R1094 established that ③'s own control cannot separate its two readings; what a control could not
settle, a **cost** now can.

## The intervention R1100 named, built

R1100's P axis deranged the whole rubric record and moved `random_k4` too — an arm that reads no
criterion text, no human weight and no human label — so it measured *the record moved*, never
*authorship was consumed*. **This round permutes, WITHIN each prompt, which criterion carries which
annotator `scores` list.** Criterion texts stay put. Criterion count identical. Judged index set `ok`
identical. Satisfaction npz untouched. **The only thing that moves is `w[i] = mean(scores)`, the
vector of human importance ratings.**

## ⭐ The result — pre-registration written from source, before the run

| configuration | pre-registered | executed | per-prompt change rate | reversal |
|---|---|---|---:|---:|
| `topw_k1` | MOVE | **MOVES** | **0.981** | 1.000 |
| `topw_k4` | MOVE | **MOVES** | **0.994** | 0.997 |
| `topw_k12` | MOVE | **MOVES** | **0.685** | 0.688 |
| `topabs_k4` | MOVE | **MOVES** | **0.997** | 0.807 |
| `topwvar_k4` | MOVE | **MOVES** | **0.899** | 0.845 |
| `topvar_k4` | stable | **stable** | 0.000 | 0.000 |
| `random_k4` | stable | **stable** | 0.000 | 0.000 |
| `full` | stable | **stable** | 0.000 | 0.000 |
| `indep_k4_fit1` | stable | **stable** | 0.000 | 0.000 |
| `greedy_k4_fit1` | stable | **stable** | 0.000 | 0.000 |
| `oracle_k4_fit1` | stable | **stable** | 0.000 | 0.000 |

**5 move, 6 byte-stable, 0 mismatches with the pre-registration.** World B holds exactly. ⭐ **`topw`
ranks by prompt-specific human ratings** — measured by intervention, not read off a docstring.

⚠ **The STABLE set deliberately contained the three LEAKY arms**, so the prediction had both
directions populated and could not be satisfied by an over-broad intervention. All three are
byte-identical to the untouched run.

⚠ **`topw_k12` at 0.685 is the informative cell, not the weak one.** With k = 12 out of a rubric
whose modal size is 13–16, most of the set is selected whatever the ratings say — so the *graded*
rate falls while the binary verdict does not. A binary verdict alone could not have shown that, which
is why both are reported.

## ⭐⭐ The consequence — a DERIVATION over committed sets, labelled

| reading of clause ③ | released ②′ admits |
|---|---:|
| — (no clause) | **24** |
| **LEAKAGE** (R1094's operative reading) | **9** — 3 `coval_core*` + 6 `topw` |
| **AUTHORSHIP**, as R1094's list applied it | **6** — the `topw` arms only |
| **AUTHORSHIP**, extended by this round's measurement | ⛔ **0** |

⛔ **R1094's authorship list was internally incomplete, and this round is what shows it.** It excluded
arms consuming the human *target* or the authored core, but not arms consuming the human *ratings* on
the prompt's own criteria — and `topw` does exactly that. Applied consistently, the authorship reading
removes the six `topw` arms as well, and **the admitted set is empty.**

**A definition whose admitted set is empty describes no object.** That is a cost the leakage reading
does not carry.

⚠ **This is an argument, not an adjudication.** Vacuity prices the alternative; it does not make the
leakage reading *true*. **R1094's finding stands unchanged:** the clause's own control cannot separate
its readings.

## Controls — 8, all green

| control | result |
|---|---|
| **SHAM** the JSON round-trip alone moves **nothing** | PASS |
| **SHAM** the round-trip's per-prompt change rate is exactly **0.000** | PASS |
| POSITIVE reversal makes `topw_k1` select the previously **lowest**-rated criterion | PASS |
| PLACEBO `random_k4` and `full` are exactly stable under W | PASS |
| NEGATIVE the within-prompt derangements have **zero** fixed points | PASS |
| NEGATIVE criterion texts and counts preserved by every intervention | PASS |
| SEEDS every W verdict agrees across 3 seeds | PASS |
| SEEDS the seed flag **changes the draw** — distinct emissions for a mover | PASS |

⭐ **The SHAM is the load-bearing one, and a byte copy could not have been it.** The W axis rewrites
every rubric record through `json.loads`/`json.dumps`. If that round-trip alone re-formatted a float
and shifted `w`, every W verdict would be measuring **serialisation**. So the sham is the *same*
rewrite with the permutation set to the identity — §1's definition exactly, one ingredient removed —
and it moves nothing, at rate 0.000.

⭐ **And the positive control demands a predicted OUTCOME, not movement.** Reversing the rating order
within each prompt must make `topw_k1` select what previously had the **lowest** mean rating. It does,
on **0.775 of 968 prompts**, against **0.000** on the identity run. The residual 0.225 is stated in
advance and is structural: `ok` excludes criteria unjudged in the npz, so the argmin over the *full*
rubric can sit outside the candidate set. **A control that only asked "did it move" would have shared
the instrument's blind spot.**

## Impossibility register

| criterion | status | what it would require |
|---|---|---|
| the verdict for `coval_core*`, `gen`, `generic`, `genericpool16` | **N/A** | their generators; `select_core.py` does not produce them |
| the verdict for `*_08bR`, `*_detA/B`, `*_kA/kB` | **N/A** | the 8B judge npz / the tag-suffix provenance, which `select_core.py` does not record |
| whether the annotators' signed ratings **are** "prompt-specific human labels" in the clause's sense | **N/A** | a reading of the clause. The dataset card's wording is quoted; the round measures consumption and does not adjudicate the word |
| adjudicating between ③'s two readings | **N/A** | an external criterion. R1094 showed the clause's own control cannot; this round prices one side and does not settle it |
| cross-release | **N/A** | a second release with its own generator |

`run.py` · `results/weights_separate.json`
