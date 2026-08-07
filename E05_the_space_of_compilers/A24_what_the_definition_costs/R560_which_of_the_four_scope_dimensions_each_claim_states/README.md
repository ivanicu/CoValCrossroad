# R560 · The scope column's defect is a shape, and `baseline` was stated by zero rows

**Decision this makes safe:** whether the scope column can be repaired axis by axis. **It cannot.**

**WORLD B.**

| dimension | rows stating it |
|---|---|
| **baseline** | **0 / 10** ⛔ |
| **regime** | 4 / 10 ⛔ |
| instrument | 6 / 10 |
| population | 8 / 10 |
| **all four** | **0 / 10** |

⭐⭐⭐ **`baseline` at 0/10 is the consequential one.** ②'s comparator is `POOL[0:4]` by **file
order** at percentile **93.7**, and **the extension moves 4 → 8 across that class** *(R527)*. Every
extension count was baseline-conditional on a baseline the page never named — the same defect R558
found for the target, on a different axis.

## Controls
- **Positive** — `population` found in **8 of 10** rows. **This is what makes the zero for
  `baseline` a measurement rather than a broken vocabulary**, and that distinction is the whole
  reason the control exists. **PASS.**
- **Negative** — an invented axis vocabulary matches **0** rows. **PASS.**

**Fix: structural, not another note.** Patching one axis per round would take four rounds and
converge on nothing, because the defect is that the column **had no shape** — it was prose, and
prose omits silently. Constants now sit in one table of four named fields; each row's cell carries
only its departures.
