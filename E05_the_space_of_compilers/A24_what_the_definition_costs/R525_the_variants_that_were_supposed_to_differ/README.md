# R525 · Three variant runs produced no variant — and the source predicted they should

**Decision this makes safe:** whether R524's duplicate classes are design or defect, and what the
campaign's "six missing label-readers" actually were.

## ⛔ First — the wall, tested before anything else

`4b5150c` closed calling the duplicates' intent *"a question about the generating invocations
rather than about the artifacts."* **False, and the fourth wall of that shape this session.**
`select_core.py`'s own `--select-npz` help text makes a **falsifiable prediction**:

> *"Five rules consume satisfaction to choose criteria — `topvar_k`, `topwvar_k`, `oracle_k`,
> `greedy_k`, `indep_k` — so under a second judge those arms **change IDENTITY, not just score**.
> … The other rules (`random_k`, `topw_k`, `topabs_k`, `full`) are satisfaction-blind and the two
> specifications **coincide for them exactly**."*

**The intent was in the source all along.** A duplicate under a blind rule is correct; a duplicate
under a consuming rule is a variant that failed to vary.

## Result — WORLD B

| class | rule | consumes? | expected |
|---|---|---|---|
| `topw_k4` + `_detA` + `_detB` | `topw_k` | no | **duplicate is correct** |
| `random_k4_s0` + `_ctlS0` | `random_k` | no | duplicate is correct |
| `random_k4_s1` + `_ctlS1` | `random_k` | no | duplicate is correct |
| `coval_core_2bA` + `_2bB` | — | — | outside the rule families |
| `generic` + `generic_reprov` | — | — | outside the rule families |
| ⛔ `oracle_k4` + `_oracle_kA` + `_oracle_kB` | `oracle_k` | **yes** | **SHOULD DIFFER** |
| ⛔ `greedy_k4_greedy_kA` + `_kB` | `greedy_k` | **yes** | **SHOULD DIFFER** |
| ⛔ `indep_k4_indep_kA` + `_kB` | `indep_k` | **yes** | **SHOULD DIFFER** |

⭐⭐⭐ **3 of 8 duplicate classes are variant runs that were designed to change identity and did
not. A control that did not control.**

## Controls
- **Positive** — the source's prediction used as an instrument check: **all 3** blind-rule variant
  tags ARE duplicates, exactly as documented. **PASS.** Had a blind variant differed, the partition
  would be untrustworthy and no attribution admissible.
- **Negative** — `oracle_k4` ≠ `oracle_k4_fit1`: the consuming family **can** produce distinct
  objects, so identity here is a failed run rather than a degenerate family. **PASS.**
- **No noise floor** — exact equality, as in R523/R524.

## What it explains

**R523's "alias" now has a mechanism.** `oracle_k4_oracle_kA` is not a deliberate alias — it is a
**failed variant run**. The A/B tags were meant to be two different selections; they are one.

⭐ **And the campaign's "six missing label-readers" trace entirely to three such runs.** The literal
misses **2 distinct objects** (the greedy and indep variants, each real and distinct from every
census arm per R523) — and both exist only because a variant run produced an unvaried artifact.

⚠ **The `_ctlS0`/`_ctlS1` flag from R524 is WITHDRAWN.** Those are `random_k`, satisfaction-blind,
so their identity is the documented correct outcome. **I flagged them on the naming convention
rather than on the rule, which is a label read as a description.**

**Impossible here:** *why* a consuming variant produced no variant — whether the flag was omitted or
ineffective lives in the shell invocation, which the repository does not carry per arm.
