# R1043 — the suite is green and it is all mine. **One of the three commit gates is blind.**

**The decision this round makes safe:** what a green `preflight` means. **For `anchoring`, nothing** —
it passes a corruption of a value it explicitly asserts.

## ⛔ `attack_the_suite.py` is the prior art, and it bounds what was left

It empties each check's input and confirms exit **2** rather than 0 — **the floor**. It does **not**
confirm any gate fires on **corrupted** content. A gate can exit 2 on empty and 0 on everything real:
`next_gradient_is_new` is a **self-test** (R1030) and `a_next_names_its_prior_art` has measured recall
**0 of 4** (R1031). **Detection was unestablished.**

## Result — ⭐ **World B**

| gate | clean | mutated | detects |
|---|---:|---:|---|
| currency | 0 | **1** | ✅ |
| **anchoring** | 0 | **0** | ⛔ **blind** |
| next | 0 | **1** | ✅ |

The anchoring mutation corrupted **`0.0098`**, a value chosen by **intersecting the gate's own
asserted numbers with those occurring exactly once in `DEFINITION.md`** — so it is guaranteed to hit
something the gate keys on. It still passed.

## ⚠⚠ The same error, caught twice inside this one round

**The mutation is itself an instrument and needs its own positive control.**

1. **currency** — I replaced `SETTLES:` and read GREEN, concluding it was blind. But I had watched it
   go **red-first on every fact registered this session**. Cause: R1042's fact carries **two
   alternative patterns** and I broke only one. **A mutation that doesn't break what the gate keys on
   tests nothing, and the gate's pass was correct.** Fixed: the mutation now verifies **every**
   alternative fails to match — measured `[True, True] → [False, False]` — before the verdict is read.
2. **anchoring** — my first mutation corrupted `0.9973`, which appears **zero** times in
   `definition_matches_the_record.py`. **The gate never asserts it**, so its GREEN tested nothing, and
   "anchoring is blind" would have been a **false retraction of a working gate**. Fixed by
   intersection, as above. **Only then** does the blindness stand.

⚠ And a third, smaller: my first anchor string was typed from memory of an annotation and **wasn't in
the file** — the same failure the `--next` gate caught on R1042. Anchors are now **grepped**.

## Controls

- **NEGATIVE** — all three GREEN on the untouched tree first, or a later RED isn't attributable:
  **PASS**.
- **PLACEBO** — a byte-identical rewrite leaves them GREEN: **PASS**.
- **MUTATION CONTROLS** — each mutation must provably break what its gate keys on, **before** the
  verdict is read (above).
- **RESTORE in `finally`** — `DEFINITION.md` put back and the gates re-run on the restored tree.
  ⚠ This is **this repository's own scar**: a timeout during `attack_the_suite` once left five epochs
  stashed and **776 files** needed recovery.

## What this does and does not license

- ⭐ A green **currency** or **next** is evidence about the **content**. A green **anchoring** is
  evidence about **its silence** — R1042's *"consistency, not correctness"* is now a **named hole**,
  not a general worry.
- ⚠ **Detection is necessary, not sufficient.** A gate that fires may still check the wrong property —
  the proxy-ledger problem this arc has hit at four levels.
- **SETTLES: OUT-OF-RELEASE** a reader who is not the author. ⚠ **And that tag is narrower than it
  looks**: §2.5's triple-blind agents would supply it, and they are unavailable **to this session by
  instruction**, not by a property of the release — the first live instance of the mislabelling the
  new enum cannot catch, one round after building it.

`run.py` · `results/mutation_test.json`
