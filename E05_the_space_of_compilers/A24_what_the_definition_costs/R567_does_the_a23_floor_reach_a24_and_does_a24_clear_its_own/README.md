# R567 · The A23 floor does not reach A24 — and A24's floors have no schema

**Decision this makes safe:** whether A23's MDE puts A24's headline effects under a floor. **It does
not.** A second question is raised and left **UNVERIFIED**.

## (a) Does the floor transfer? **WORLD B — no.**

| | A23 `R274` | A24 |
|---|---|---|
| n | **250** | **968** |
| statistic | admissibility / necessity, `tau = 0.424` | A2 vs held-out annotator |
| MDE | **[0.105, 0.125]** | per-round, e.g. **0.0119**, **0.0108** |
| its own comparison set | R231, R249, R257, R260 — all A23-era | — |

**n differs by 3.87× and the statistic differs, so no scaling is attempted.** A23's own per-round
MDEs are not A24's, and **A24's rounds report their own.**

## (b) Does every A24 effect clear its own floor? **UNVERIFIED.**

My extractor found **0** artifacts carrying both an effect and an MDE, out of 264 rounds — **an
empty population, which is silence and not an acquittal.** Two reasons, both mine:

⛔ **The matcher matched UUIDs.** The substring `c2` appears inside hex ids like
`…-c224-56f8-…`, so ~150 "effect" hits were identifiers. **§4's search-is-an-instrument row, fifth
occurrence this session.**

⭐⭐⭐ **And the real finding underneath: there are 60+ distinct MDE-key names across the arc** —
`floor` (14), `mde` (5), `pooled_mde`, `perm_floor`, `sham_mde`, `mde_lo`/`mde_hi`, `noise_floor`,
`data_floor`, `rule_floor`, `mechanical_floor`, `sign_floor`, `conv_floor`, `floor_2b`/`floor_8b`…
**The campaign has no schema for its own floors.** That is why no gate can ask whether every effect
clears its own — **the question is not answerable by any matcher, only by a convention that does not
exist.**

## Controls
- **Positive** — `R274` records its own `prompts`, `tau` and `mde_bracket`, so *"a different
  detector"* is a **reading**, not an inference from silence. **PASS.**
- **Negative** — an invented parameter key is absent from `R274`. **PASS.**
- ⛔ **(b) has no admissible control**: its population is empty, so the round returns UNVERIFIED for
  that half rather than a count.
