# R343 · Does any check tie an artifact to its source?

**The decision this makes safe:** whether an artifact-side verdict in this repository can be read as
a statement about the computation that produced it. **It cannot.** Nothing here verifies that the
JSON beside a `run.py` came from that `run.py`.

## Result

**277 rounds edited to compute a MEDIAN instead of a MEAN. Every committed artifact left
byte-identical, now holding numbers its own source can no longer produce. Zero of 21 checks moved —
on either instrument.**

| condition | files touched | moved (exit) | moved (report) |
|---|---:|---:|---:|
| g=0 — copy, mutate nothing | 0 | 0 | 0 |
| **sham** — comment appended to every `run.py` | 328 | 0 | 0 |
| **T_src** — `mean → median`, artifacts untouched | **277** | **0** | **0** |
| **positive** — one point moved outside its own CI | 1 | 0 | **2** |

The positive control moved, so the zero is a **measurement, not silence**.

## Half the answer is a derivation, and it is labelled

A read census — from an **audit hook on `open`**, not from reading the code and forming an opinion:

**7 of 21 checks open a round's `run.py`. 13 open only artifacts, documents or registries.**

⛔ A check that never opens a `run.py` **cannot** respond to a source edit. That is forced by *a
function's output depends only on its inputs* — a derivation, not a finding. **The measurement is the
remainder: 7 checks read sources, and none of them noticed either.**

What those 7 read sources *for* is structure — retired framings, link targets, variable-name pairing,
declared outcome variables. **Not one asks whether the numbers next to the source came out of it.**

## Three controls, and every one of them caught a defect in this round

**① The copy was silently broken.** `/tmp` is tmpfs, the repo is ext4 — `cp -al` died on the first
cross-device link, left a partial tree, and the fallback `cp -a src dst` found `dst` existing and
nested the repo inside it. Every glob returned 0. Every condition printed `verdict changed: 0`,
**including what would have read as the headline.** Only the positive control failing made it a
`FAIL` instead of a finding. `make_copy` now lands on the same filesystem and **refuses to return
success unless the copy holds the same number of round sources as the original.**

**② The exit code was saturated.** `artifacts_are_internally_coherent` already exits 1 on R141's six
violations, so a planted seventh **cannot** move it — realstat §4's *control that cannot PASS*, with
`floor == ceiling == 1`. Hence two instruments, exit code and report digest. **Which one carries the
headline is decided by whether the sham moves under it**, before any `T_src` number is read — not by
which gives the nicer answer. The sham moved neither, so the finer one is admissible, and it is the
one reporting **0**.

**③ The positive control's unit was not the claim's unit.** It planted corruption wherever a numeric
key stem-matched a two-element list. The gate pairs only where **its** `MEANISH` matches the mean and
**its** `CIISH` matches the interval — so the plant landed on `R03_stated_vs_revealed`, a pair that
gate never looks at, and reported `0 moved` **while the harness was working perfectly.** The
regexes are now imported from the gate, never re-typed.

> realstat §4 states this remedy literally: *name the instrument's unit and the claim's unit as two
> separate strings and require them to be equal, before the control is even designed.* Mine were
> *any stem-matched numeric* and *a pair this gate checks* — **and I had written the gate.**

**Isolation** was asserted, not trusted. The copy is hardlinked, so an in-place write edits the
**original**; mutation unlinks before writing. Verified against a throwaway pair first — in-place
write propagated to the original, unlink-then-write did not — and the real repository's `git status`
is compared before and after every run.

## Reproducibility is a fixpoint, not an identity

Run 1 → `8dc9b3c8`; runs 2, 3, 4 → `2ee66bcc`, byte-identical. **The round's own artifact lands in
the corpus the next run measures**, and several checks count corpus files. Stable from the second run
on. Reporting *"two runs byte-identical"* without that sentence would have been true and misleading —
and **measuring a system you are inside of is what every check in this suite also does.**

## Register

| criterion | status |
|---|---|
| multi-seed | **N/A** — no rng; the conditions are deterministic edits |
| multiplicity | one family, 21 cells × 4 conditions. No correction: these are verdict changes, not test statistics, and calling them significant would be the arithmetic trap in the other direction |
| construct-validated | **N/A** — "did a check notice" has no external gold standard; the positive control is the closest available and it is mine |
| **the reverse direction** | **not tested** — an artifact hand-edited to agree with a source that never produced it. Needs a recorded output hash per round, which no round writes |

## Verdict

`W2_NOBODY_CHECKS`. Every artifact-side verdict in this repository — 389 coherence pairs, 382 centred
intervals, every degeneracy and contrast check — rests on an assumption **no instrument here tests**.
A stale artifact, a hand-edited artifact, and an honest artifact are **indistinguishable** to this
suite.

## The sentence I can no longer write

> *"the suite verifies the rounds."*

It verifies the **artifacts**, and it has never once asked where they came from.

Artifact: `results/r343_provenance_gauge.json`.
