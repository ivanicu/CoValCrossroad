# R581 · `regime` is not a condition on the extension — it varies inside it

**Decision this makes safe:** the scope marker on row 2 is complete.

**WORLD B.** The extension of ② ∧ ③ is `coval_core`, `topw_k3`, `topw_k4`, `topw_k6`, `topw_k8` —
**k = 3, 4, 6, 8.** ⭐⭐⭐ **k varies INSIDE the count. `5` is already taken across k, not at one k**,
so `regime` cannot condition it the way `target` or `baseline` do.

**And R441 answers the question my NEXT line asked.** Its artifact records
`k_spread: [1, 2, 3, 4, 6, 8, 12, 16, 39]`, `redundant: 0`, `world: W-DECORATION` — it measured
**whether the size clause excludes anything** (it does not), **never how the extension varies with
k.** So the sweep did not touch the extension. **But that turns out not to matter, because the
question was malformed.**

## What this corrects
**R580 listed `regime` as *conditioned but unmeasured*** and marked it untested — the careful-looking
move. **It is not conditioned at all.** ⭐ **"Untested" and "not applicable" look identical from
outside, and only one of them is a gap.** I had reached for the conservative label without checking
which it was — the same generosity R580 itself warned about, one axis over.

## Controls
- **Positive** — the members were **parsed from the page**, not typed from memory. **PASS.**
- **Negative** — `coval_core`, which carries no `k` in its name, parses as `None` rather than being
  silently coerced. **PASS.**

**The marker now reads: three axes measured, and `regime` explicitly not a condition — with the
reason on the page.**
