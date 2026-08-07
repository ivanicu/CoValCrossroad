# R1051 — execute the 16 flagged rounds. ⭐ **All 16 re-derive their committed values exactly. Zero drift, zero non-determinism.**

**The decision this round makes safe:** whether R1050's downgrade is about the **gate** or about the
**numbers**. **It is about the gate.** The values under the clause are re-derivable on demand.

## Result

| | |
|---|---:|
| flagged rounds executed (twice each) | **16 of 16** |
| errors / timeouts / missing artifacts | **0** |
| non-deterministic on values (`run1 ≠ run2`) | **0** |
| **drifted** (deterministic **and** ≠ committed) | **0** |
| match committed **values** | **16** |
| match committed **bytes** | **7** |

## ⛔ Why the design ran everything twice

A first probe showed R978's artifact changing on re-run and R1012's not. **`differs from committed`
has two causes demanding opposite conclusions** — non-determinism (comparison meaningless →
UNVERIFIED) or genuine drift (the committed artifact did not come from the committed code). §4's
*determinism read as currency*, run backwards. **`run1` vs `run2` is the noise floor, measured per
round.** It came back clean for all 16, which is what makes the committed-vs-run1 comparison readable.

## ⭐ The 9 byte-mismatches are a provenance stamp — and the scope is narrower than it first looked

Every byte-mismatching round differs by **exactly 2 diff lines**, and the differing key is a **git
hash stamp**: `commit` in R920/R921/R925, `head` in R975/R978/R986/R989.

**Census of the 16 committed artifacts:**

| | count | rounds |
|---|---:|---|
| carry a `commit`/`head` stamp | **13** | R920 R921 R922 R925 R926 R975 R978 R986 R989 R1000 R1001 R1005 R1012 |
| carry **no** stamp — untraceable to a producing commit | **3** | R1027 R1036 R1045 |
| **byte-mismatch** | **9** | ⭐ **every one is a stamped round: True** |

⚠ **So "the stamp records HEAD at run time" holds for 9 of the 13, not all of them** — four stamped
rounds (R1000 R1001 R1005 R1012) matched on bytes, so their stamp is **stable**, not HEAD-tracking.
**The containment claim is the measured one** (`byte-mismatch ⊆ stamped`); the mechanism claim carries
the narrower scope. Stating it unqualified would have been a correct observation reported without the
population it holds over.

- ⛔ **For the 9 HEAD-tracking rounds the byte cell of this specification curve is degenerate**:
  `floor == ceiling`, it can only ever return *differs*, and §4 says no threshold is admissible on a
  degenerate statistic. **The value cell is the only admissible one.**
- ⚠ **The mirror defect**: 3 artifacts carry no stamp at all and cannot be traced to their producing
  commit by any means.

⚠ **I nearly generalised the mechanism from R920 alone** — and R989's field is named `head`, not
`commit`, so a one-case explanation would have been wrong on 4 of 9. **That is R1045's error exactly**;
the remedy was to run the diff across all of them, and then the census across all 16.

## Controls

- **POSITIVE** — the differ must call a planted numeric mutation unequal on **bytes and values**:
  **True** — ⛔ **False on the first attempt**, because the mutation replaced the first `0` character,
  which landed inside the string `"R1000"` → bytes changed, no numeric value did. **The control was
  right; the mutation targeted the wrong unit.** Replaced with a numeric-leaf perturbation.
- **NEGATIVE** — identical bytes compare equal: **True**.
- **PLACEBO** — an erroring or timing-out round is **UNVERIFIED**, never counted as agreeing and never
  as drifted: **0 such rounds**.
- **NOISE FLOOR** — `run1` vs `run2` per round, measured.
- **SAFETY** — each artifact's committed bytes are read from **git**, not the worktree, and the file is
  restored with `git checkout --` in a `finally` block. Worktree verified clean afterwards.

## What this round cannot say

Whether a **drifted** artifact's committed value was ever correct — moot here, since **nothing
drifted**. And it does not re-verify the *gate*: R1050's downgrade stands as a statement about
attribution, now with the numbers confirmed underneath it.

## IMPOSSIBLE here

- **tracing an unstamped artifact to its producing commit** — the field is absent from the file.
  **SETTLES: IN-RELEASE** for future rounds only (add the stamp); **OUT-OF-RELEASE** retroactively,
  since no committed text records it.

`run.py` · `results/reran_the_flagged.json`
