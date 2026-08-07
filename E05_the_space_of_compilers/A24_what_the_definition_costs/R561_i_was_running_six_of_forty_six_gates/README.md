# R561 · I was running six of forty-six gates

**Decision this makes safe:** what the commit gate actually is.

**WORLD B.** `assurance/run_all.py` **exists**, discovers **46** gates by glob, parallelises at 12
workers, and excludes meta-gates by design. My last NEXT line said *"that script does not exist
yet."* **It does, and retraction 1 of this session was already about re-deriving a population
`run_all.discover()` defines.**

**Of the 40 gates outside my hand-typed six, classified three-valued rather than counted:**

| verdict | n |
|---|---|
| **FAIL — real live debt** | **9** |
| **UNRUNNABLE (exit 2) — empty population** | 4 |
| **UNVERIFIED — its own control failed** | 1 |

The nine: `arm_population_is_derived` · `artifacts_are_internally_coherent` · `attack_every_check` ·
`attack_outcome_variable_declared` · `attack_scope_reaches_the_reader` · `corrections_propagated` ·
`every_round_reaches_the_readme` · `outcome_variable_declared` · `seed_filter_is_disclosed`.

⚠ **`next_gradient_labels_its_hypotheses` is UNVERIFIED, not FAIL** — its own positive control broke,
so it says nothing in either direction. **Folding it into the failure count would manufacture a
tenth defect from a broken instrument.**

⚠ **My classifier is imperfect**: 2 of 3 "unclassified" rows are parse artifacts (the `ran 46 gates`
summary line and a `breakdown` header) rather than gates. Reported rather than quietly dropped.

## ⛔ I reimplemented the runner inside the round about having reimplemented the runner
The first version ran the 40 serially in a loop I wrote. It died on `attack_the_suite.py`, a
**meta-gate that runs the whole suite** and which `run_all` excludes by design. **The error the round
was about, committed while committing it.**

## Controls
- **Positive** — `discover()` finds **all six** I was hand-running, so the two populations are
  comparable and the difference is meaningful. **PASS.**
- **Negative** — an invented gate name is not discovered. **PASS.**

⚠ **Not fixed here.** Nine live failures are pre-existing debt; this round establishes that they
exist and were invisible, not that they are resolved.
