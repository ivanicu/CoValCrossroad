# R1030 — a gate exists to catch NEXT lines proposing existing work. It never runs on live ones.

**The decision this round makes safe:** whether a green gate suite is evidence about the corpus. Here
it is not — one gate passes while the failure it was built for runs at **71.4%**.

## What provoked it

Five consecutive rounds of mine proposed work that already existed:

| round | its NEXT proposed | what existed |
|---|---|---|
| R1026 | re-derive the 15,488 cost | *genuinely new* — R1027 did it |
| R1027 | audit the register as an instrument | R291 / R472 / R547 / R660 / **R802** |
| R1028 | re-score entries for **presence** of a requirement | **R472** did exactly that |
| R1029 | a typed entry template, one gate | **`assurance/register_requirements.py`** — and its docstring already states R1029's limit |

And **`assurance/next_gradient_is_new.py` exists to catch precisely this**, built after R858 measured
**7 of 26 (27%)**.

## ⛔ Why it did not fire: it is a SELF-TEST, not a MONITOR

Run with no arguments it validates its searcher against **four historical cases**, prints *"every
historical case is still detected"*, and exits **0** — **without ever pointing that searcher at the
NEXT lines the session is writing.** It certifies **capability**, never **currency** — the same shape
as *determinism read as currency*.

## Result — **World B.** 5 of 7 = **0.714**, against R858's **0.269**, while the gate exits 0.

| round | prior art | where |
|---|---|---|
| R1022 | **YES** | `E01_the_rubric_was_the_object/A03_…` |
| R1023 | no | — |
| R1024 | no | — |
| R1025 | **YES** | `A26_can_the_definition_be_applied…` |
| R1026 | *excluded* | subject created by R1027 — counting it conditions on the outcome |
| R1027 | **YES** | `A24_what_the_definition_costs/…` |
| R1028 | **YES** | `A24_…` |
| R1029 | **YES** | `A24_…` |

## ⛔ Four self-attacks, each of which lowered or could have killed the number

1. **My own `run.py` was in the corpus.** The negative marker was found *in my own file*; worse,
   **POSITIVE ② passed for the wrong reason** — R1027/R1028's terms were located in this script, not
   in prior art. *A control that finds its answer inside the question confirms nothing.*
2. **The searcher reads CONTENTS, not paths.** `NG.corpus()` returns `(path, contents)`.
3. **Paths alone were not enough either — and this is the mechanism.** Round directories are
   `R472_the_register_half_complies` (**underscores**); a NEXT is prose (**spaces**). `NG.search`
   compiles `re.escape(term)`, so an exact match **can never bridge them**. The committed gate is
   **structurally unable to match a prior-art ROUND from a prose subject** — and a round is the
   dominant form of prior art here.
   ⚠ **Normalising alone is a TRADE, not a fix**: it breaks the gate's own underscore-literal cases
   (`R306_the_table_at_every_annotator`, `register_requirements`). The instrument must search **both**
   corpora.
4. **The first rate was 7/7 = 1.000 — self-confirmation one level up.** Searching `false-admission`
   for R1022's NEXT finds **R1023**, the round that acted on it and coined the term. Prior art must be
   **strictly earlier**. And **shared files are dropped entirely**: R1023's first "prior art" hit was
   in the fact registry **I edited an hour earlier**. Only hits inside a strictly-earlier **round
   directory** count — conservative, and it can only **lower** the rate, which is the direction that
   could have refuted the finding. It did: **1.000 → 0.714**, and 2 of 7 flipped to `no`.

## Controls

- **POSITIVE ①** — the imported searcher reproduces the gate's **own** four historical cases: **PASS**.
  Without it, no comparison to R858 is licensed.
- **POSITIVE ②** — **four live cases labelled by hand**, which the self-test does not have: **PASS**.
- **NEGATIVE** — a term existing nowhere returns nothing: **PASS**.
- **PLACEBO** — `coval_core` must hit, or the negative passes trivially by finding nothing: **PASS**.
- **g=0** — an empty term list is UNRUNNABLE, never a silent pass: **PASS**.

## Bounds

- ⛔ **Only the HIT direction is sound.** A term found is prior art; a term **not** found is **not**
  evidence of novelty, because I chose the terms. **0.714 is a lower bound**, and each `no` is
  **UNVERIFIED**, not clear.
- ⚠ **Subject novelty is not substantive novelty.** R1027–R1029 each produced a real result *on* an
  existing subject. The cost is not that they were wasted — it is that **each spent part of itself
  discovering prior art the NEXT line should have named.**
- ⚠ **The repair is one argument, not a new gate.** `next_gradient_is_new.py` already accepts terms on
  `argv`. What it lacks is a **caller** that feeds it the NEXT being written. **This round does not
  make that change — naming it is not doing it.**

`run.py` · `results/next_novelty_live.json`
