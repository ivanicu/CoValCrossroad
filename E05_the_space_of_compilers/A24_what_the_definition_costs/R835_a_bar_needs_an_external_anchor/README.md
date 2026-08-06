# R835 · a bar cannot get discriminating power from the ordering it sits in

**The decision this made safe:** whether the definition's performance clause can be repaired by
restating it. **It cannot — not on this site.** Both candidate forms are *forced*, and the
external-anchor form that isn't forced comes back **empty**.

Design in `PREREGISTRATION.txt`, committed with `run.py` before it ran.

## A hypothesis checked and discarded before designing anything

I expected an **asymmetry**: ③ forbids the core its labels while ④ lets the bar be *fit* on labels.
Reading both verbatim: ③ forbids *"that prompt's **own** human labels"*; ④ permits fitting on
**other** prompts'. **The core is not forbidden other prompts' labels either.** No asymmetry.

## The derivation that motivated the round

**[provenance restriction P] ∧ [beat an ABSOLUTE bar B]** has extension

- **EMPTY** if `B > ceiling(P)`
- non-empty, possibly **VACUOUS** if `B ≤ ceiling(P)`

and **nothing ties `B` to `ceiling(P)`** — which is exactly what R826 measured when the bar
*saturated on* the released core and the verdict flipped across the plateau.

⛔ **And the obvious fix is broken too.** *"Beats every rule in the same provenance class"* is
satisfied by the class maximum **by construction** — §4's `check that cannot fail`. **Both forms are
forced; neither failure is a measurement.**

## What that leaves — and it is the only part that could come out otherwise

**④''** — *the core beats the best other rule in its class **by more than the MDE***. An **external**
anchor. Whether it is satisfiable here is a fact about the world.

| | |
|---|---|
| ③-admissible pool | **46** arms |
| adjacent pairs tested | **45** |
| **separable (gap > 2× MDE)** | **0** |
| positive control · negative control | `oracle_k4` vs `generic` **+0.0797 vs MDE 0.0227 → SEPARABLE** · arm vs itself → null |
| three seeds (1, 2, 7) | byte-identical `c94853d15d7c11905bf53b2b279f9ab5` |

**W-NO-SEPARABLE-BEST.** The best label-free arm `generic` (0.5556) is only **+0.0182** above `gen`
— **inside its own MDE of 0.0232**. **④'' is empty too.**

⚠ **The observation the table makes visible, reported beside the pre-registered verdict**, not
instead of it: `generic` vs the best **random** arm is **+0.0449 against MDE 0.0228 — a ratio of
1.97×**, right at the 2× boundary and therefore **unresolved**. So the class separates from random
only marginally, and internally not at all.

⛔ **The two-seed check caught a real bug in this round.** v1 sorted a `set` by `-a2[a]` alone; set
iteration over strings depends on `PYTHONHASHSEED`, and **24 arms in 11 groups share an identical A2
to 10 dp**, so tied arms swapped places between seeds. **The verdict never moved; the order did** —
which is exactly the silent nondeterminism a two-seed check exists to catch. Fixed with a name
tie-break and verified at three seeds.

⚠ The MDE used is each arm's paired MDE **against the BAR**, not against the other arm. A true
between-arm MDE needs per-pair difference vectors R436 did not persist.

## NEXT

The clause cannot be repaired by restatement because the label-free class is **unresolved at this
design's resolution** — 0 of 45 adjacent gaps clear 2× MDE. What is not established is whether that
is the *design's* resolution or the *class's* spread: the MDE here is arm-vs-bar, and an arm-vs-arm
MDE would need the per-prompt difference vectors, which is a re-run rather than a re-reading.
