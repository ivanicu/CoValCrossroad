# R509 · A checkable ③ does not rescue the definition — it makes the same vacuity harder to see

**Decision this makes safe:** whether to replace ③ (*not built by reading the labels* — provenance)
with ③′ (*not **optimised** against the labels* — checkable from the artifact plus the rubric, per
R508). **Do not.**

## The five arms admitted by ①∧②∧④, under both readings

| arm | criterion text on disk | ③′ verdict |
|---|---|---|
| `oracle_k4` | yes | **EXCLUDED** — separates as an optimiser (measured) |
| `greedy_k4_fit1` | yes | **EXCLUDED** — measured |
| `indep_k4_fit1` | yes | **EXCLUDED** — measured |
| `topw_k4` | yes | excluded by **derivation** — its rule is stated over the ordering |
| **`coval_core`** | **no** | ⛔ **CANNOT RULE — no criterion text, so no positions** |

| | |
|---|---|
| ③ extension | **0** |
| ③′ extension | **1** — `coval_core` |
| …of which **adjudicated** (instrument looked, found nothing) | **0** |
| …of which **blind spots** (instrument could not look) | **1** |

**POSITIVE control passes:** the instrument ruled on **4 of 5** by measurement, so this is not the
silence of an instrument that never fires.

## The finding

**③′'s entire extension is an arm the instrument cannot see.** Of 95 arms with a criterion-text file
on this release, **the released core is not one of them** — only `core_coval_core_sham.json` exists.

> **A zero from an instrument that could not look is silence, not an acquittal. `coval_core` is not a
> member of ③′; it is missing data wearing a member's clothes.**

**So narrowing ③ to something checkable does not rescue the definition. It converts *"empty because ③
excludes everything"* into *"one member the instrument cannot see"* — the same vacuity, harder to
notice. That is worse, not better.**

⭐ **And it sharpens the fork rather than dissolving it.** The choice is not *provenance vs.
checkability*; it is **an honest zero vs. a flattering one**. ③ reports its emptiness. ③′ reports a
member and would need a footnote nobody reads to say the member was never examined.

## Bound

Whether `coval_core` would actually separate is **undecidable on this release** — it ships no
criterion text. It would require the released core's criteria as text, which the second release may
carry and this one does not. **Stated as a requirement, not as an unavailability.**
