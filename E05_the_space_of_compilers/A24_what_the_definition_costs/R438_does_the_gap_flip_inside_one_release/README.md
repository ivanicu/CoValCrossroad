# R438 · the GAP does **not** flip inside one release — `W-STABLE-SIGN`

**The decision this round makes safe:** whether R437's *"the bars invert between releases"* named the
right object. **It survives** the attack most likely to break it.

## ⭐ The announced stratifiers were checked, and only one existed

R437 proposed splitting on *"response count, prompt length, turn depth"*. **Response count is not a
stratifier at home** — every prompt there carries exactly four responses by construction
(`score.py: L = "ABCD"`). So **no cross-release stratified sweep exists at all.**

What does exist is decisive on its own: the second release has n ∈ {2,3,4}. A sign flip *there*
falsifies the release-level ontology using **one release, one statistic, no cross-scale comparison**.
**Seventh announced step checked; it survived, in a smaller form than announced.**

## Result

| stratum | interactions | chance | BAR2 (`generic`) | BAR4 | **GAP** | MDE | |
|---|---|---|---|---|---|---|---|
| **n=2** | 5,204 | 0.5000 | 0.5081 | 0.5600 | **+0.0519** | 0.0283 | **RESOLVED** |
| n=3 | 454 | 0.3333 | 0.4053 | 0.4449 | +0.0396 | 0.0948 | — |
| **n=4** | 1,684 | 0.2500 | 0.2815 | 0.3884 | **+0.1069** | 0.0490 | **RESOLVED** |

**2 of 3 strata resolve; both positive.** The GAP keeps its sign across strata where **chance itself
moves from 0.2500 to 0.5000** — both bars had every opportunity to cross and did not.

⭐ **And the GAP grows with n** (+0.0519 → +0.1069): `generic` decays toward chance as responses are
added (0.2815 against a chance of 0.2500 at n=4) while the criterion-free rule does not. That is a
dose-response, reported because it is there — **not** a claim about mechanism.

## ⛔ The design decision that would have decided the answer, made explicit

`BAR4` is a **maximum over a family**, and R435 measured that such a maximum climbs by construction.
Re-selecting the best rule *within* each stratum is a max over 30 in a smaller sample — it inflates
`BAR4` and biases toward *"④ binds"*. Holding the global winner fixed does not, but is then not "the
best rule in that stratum".

**Both were computed, both reported**, and the kill rests on the FIXED version:

| selection inflation (RESELECTED − FIXED on BAR4) | n=2 | n=3 | n=4 |
|---|---|---|---|
| | **+0.0000** | **+0.0022** | **+0.0000** |

**Measured, not argued.** It is nil here because `max_len_chars` wins in 2 of 3 strata anyway — but
that is a *result*, not something I was entitled to assume. Choosing one mode silently would have
been the whole finding.

## Controls

| control | n=2 | n=3 | n=4 |
|---|---|---|---|
| POSITIVE — an oracle beats **BAR2** | +0.4919 (MDE 0.0189) | +0.5947 (0.0641) | +0.7185 (0.0305) |
| POSITIVE — an oracle beats **BAR4** | +0.4400 (0.0198) | +0.5551 (0.0663) | +0.6116 (0.0330) |
| g=0 — `generic` against itself | **0.0e+00** | **0.0e+00** | **0.0e+00** |
| NEGATIVE — chance printed beside both bars | 0.5000 | 0.3333 | 0.2500 |

**Multiplicity:** 6 cells (3 strata × 2 selection modes), **4 surviving BH(q=0.10)**, non-survivors
printed.

## What this establishes, and what it does not

- **Establishes:** the number of responses does not reorder the two bars. R437's release-level
  framing survives an attack aimed squarely at its ontology.
- **Does not establish:** that the framing is *right*. One attack survived is one attack survived.
  A stratum-level flip and a release-level flip could still be the same phenomenon — deciding that
  needs a stratifier both releases share, **and there is none**.
- ⚠ **`W-UNRESOLVED` would not have been an acquittal either.** Had fewer than two strata resolved,
  the attack would have failed to *be* an attack — which is different from the claim surviving one.
  The round says so in its own branch rather than only here.

## Impossible here, named

- **a stratified cross-release sweep** — home has 4 responses by construction; no shared axis.
- **whether a stratum flip and a release flip are one phenomenon** — needs that shared axis.
- **the supremum over criterion-free rules** — R435's 30-member family, restated.
- **a mechanism for the dose-response** — observed, not intervened on.

Findings and their scope live in `DEFINITION.md`. This file states the design and the corrections.
