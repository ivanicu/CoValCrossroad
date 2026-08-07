# R691 · reused or coincident? — **coincident, 12.8 hours apart**

**⭐⭐⭐ R360 bound `PUBLISHED_FIVE` at 02:05 and R442 bound it to different members at 14:53 the same
day — **12.8 hours**, no retraction in the ledger at the time. **A ledger gate would have had nothing
to warn against.** The enforceable invariant is NAMING, and this round builds that gate.**

## THE DECISION THIS MAKES SAFE
Reuse-after-retraction → build a ledger gate. Independent coincidence → a ledger gate is useless.
**Measured: coincidence.** So R690's closing line pointed at the wrong build, and the right one is a
naming rule.

| | |
|---|---|
| first | **R360** `19892ed6` 2026-08-04 **02:05:45** — `coval_core topw_k3 topw_k4 topw_k6 topw_k8` |
| second | **R442** `d27c9ace` 2026-08-04 **14:53:36** — `coval_core topabs_k4 topvar_k4 topw_k4 topwvar_k4` |
| gap | **12.8 hours**, different commits |
| prior retraction of the claim | **NONE** — 228 ledger versions existed before the second binding and not one mentions it |

Registered **A (R360 first) HOLDS** · **B (no prior entry) HOLDS** · **C 20 [0,90] days → 0, INSIDE**
· **directional (different commits) HOLDS.**

**Controls (git log is an instrument):** POSITIVE — a tracked file returns a commit date. **g=0** — a
nonexistent path returns **nothing**, not a fabricated date. NEGATIVE — a tracked file never
containing the token → none. PLACEBO — identical.

## ⛔ MY REGISTERED UNIT WAS COARSER THAN THE PHENOMENON
I registered the gap in **days** on an interval `[0, 90]`. The observed gap is **same-day**, and a
day-resolution interval **cannot distinguish 0 from 23 hours**. Reporting *"0 days apart"* reads as
*simultaneous* when it is nearly thirteen hours. **That is a design defect in the registration, not a
result** — and it went unnoticed until the number came back.

## ⭐ THE PRODUCTION STEP: `assurance/release_names_resolve_to_one_set.py`
A literal whose **name** asserts a release property must (a) resolve to the **same member set**
everywhere and (b) contain only members **`data/DATASET_CARD.md` names**.

- **644 `run.py` scanned**; rounds that *document* the defect (R689–R691) excluded by construction
- **positive control**: a synthetic collision must be detected, or a pass is silence → **fires**
- **empty population → exit 2**, never a pass
- `PUBLISHED_FIVE` **frozen with a written reason** — both rounds are committed and their artifacts
  carry source hashes, and re-running a round to fix its source **destroyed an artifact once in this
  arc**. The retraction reaches `STATEMENT.md` and both READMEs instead.
- ⚠ **floor, not certificate**: a release claim under a neutral name (`FIVE`, `TARGET`) is invisible

## IDENTIFICATION LIMIT
Git records the commit that first **contains** a binding, not the moment it was **chosen** — R678's
write-not-author limit, restated because it binds here too.

## NEXT
The gate covers names that assert a release property (`results/name_reuse.json` records the two
bindings it was built from). Its stated blind spot is a release claim under a neutral name. Measure
that blind spot rather than assuming it is small: take the arm-name vocabulary from R680 and count
how many literals bind ≥2 arm names under a name matching neither the release pattern nor an
our-arms pattern — that is the population the gate cannot see.
