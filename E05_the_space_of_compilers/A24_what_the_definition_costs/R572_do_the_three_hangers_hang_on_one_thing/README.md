# R572 · The three hanging gates do not hang on one thing

**Decision this makes safe:** whether one fix clears three of the suite's non-passes. **It does not.**

**WORLD A.** `run_all`'s own source documents a candidate: *"a gate that spawns a grandchild and
exits… the child dies, the grandchild holds the pipe, and the runner blocks forever."* **Refuted on
both sides:**

| gate | `subprocess` calls | discovers gates | hangs |
|---|---|---|---|
| `attack_the_suite` | 1 | 0 | **yes** |
| `backfilled_findings_are_rederivable` | 4 | 0 | **yes** |
| **`what_did_each_check_actually_read`** | **0** | 1 | **yes** |
| `attack_no_withdrawn_framings` — **control** | 1 | 0 | **no, 6.18s** |

- **NOT NECESSARY** — one hanger makes **zero** subprocess calls.
- **NOT SUFFICIENT** — a gate that makes one finishes in **6.18s**.

**So `ERROR 3` is at least two distinct defects**, and my own NEXT line's framing — *"one question
that could remove three of the suite's sixteen non-passes"* — is dead.

## ⭐ Why this round differs from the three before it
R569, R570 and R571 each had their hypothesis refuted **and left the question open**. **This one is
refuted and the question is ANSWERED**: *do they hang on the same thing?* **No** — established by a
two-sided argument with its own negative control, not by absence of evidence.

## Controls
- **Negative control is load-bearing here**: without a non-hanging gate that *does* call
  `subprocess`, "not sufficient" would be unsupported and the refutation would be one-sided.
