# R569 · The suite and a standalone run disagree, and my explanation is refuted

**Decision this makes safe:** none. **UNVERIFIED, and the refuted hypothesis is the product.**

## What is established
- `run_all` reports **`statement_provenance … rc=2 UNRUNNABLE: STATEMENT.md absent`**.
- **That gate exits 0 standalone** — from the repo root *and* from `/home/ivan`.
- **It passed before every commit of this session**, anchoring every decimal on the deliverable.
- `run_all`'s summary: **`PASS 22 of 46 · FAIL 16 · UNRUNNABLE 5 · ERROR 3`**, and it emits a **row
  only for non-passing gates** — PASS is a count, never a line.

## ⛔ My hypothesis, tested and refuted
`run_all` invokes gates with **`cwd=ROOT.parent`** (`/home/ivan`), so I predicted they were blind to
the repo. **Refuted by direct test:** `ROOT = HERE.parent` derives from `__file__`, and the gate
passes from `/home/ivan` unchanged. **The mechanism is UNVERIFIED.**

## Two positive controls failed, and both times it was my instrument
1. *"a known-crashing gate is detected as crashed"* — **`source_stamp_is_current` does not crash
   standalone**; it exits 2, UNRUNNABLE.
2. *"gates passing in BOTH arms"* returned **0** — because **`run_all` prints no row for a passing
   gate**, so my regex could only ever see failures. **Seventh instrument defect of this class this
   session.**

⭐ **Both controls did their job: each refused to let a verdict out.** The round produces no count,
which is the correct output when the instrument cannot see the population.

## Why it matters more than a runner bug
**The divergence has now been observed on four gates** — `attack_scope_reaches_the_reader`,
`corrections_propagated` *(R562)*, `source_stamp_is_current`, `statement_provenance` *(here)*.
**`statement_provenance` is the gate the deliverable's provenance rests on.** It passed standalone
every time I invoked it; **the suite's own view is that it never ran.** Which view is right is
exactly what is unverified.

## Controls
- **Negative** — the same gate run twice standalone gives the same rc, so the standalone arm is
  stable and a comparison would have been licensed. **PASS.**
- **Positive ×2** — both **FAILED**, and the round stopped. **Correct behaviour.**
