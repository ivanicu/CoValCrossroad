# R841 · does the exact-class interval close when every annotator is used?

**Arc A24 — what the definition costs.** Opened against **my own entry 1352**, which declared clause
② **undecidable** under an exact-class reading and filed that as a property of the release.

**It drew 3 annotators per prompt. The release ships 18,384 annotator rankings over 1,078 prompts,
median 16 — so 1352 consumed 3,234, i.e. 17.6% of what was on disk.** The failure register's own
row is mechanical about this: *count what the release contains and what your code consumed, and
require those two numbers to match.* **Fourth instance of a row already wrong three times.**

---

## ⛔ FINDING 0 — entry 1352's numbers are NOT REPRODUCIBLE, by construction

1352 seeded its per-prompt annotator draw with `np.random.default_rng(900+s+hash(p)%1000)`.
**Python randomises `hash()` of a `str` per process.** Measured, with a positive control on the test
itself:

| | run 1 | run 2 | run 3 |
|---|---:|---:|---:|
| `hash('prompt_42') % 1000` | **924** | **294** | **947** |
| `zlib.crc32(b'prompt_42') % 1000` *(control)* | 632 | 632 | 632 |

⭐ **So 1352's draw was effectively UNSEEDED.** Its `+0.0151` / `+0.0083`, its CIs, its MDEs and its
verdicts are **one unlabelled draw from a distribution it never characterised** → **UNVERIFIED**,
not overturned, and **not to be quoted**. This round seeds with `crc32`.

⚠ **Measured here: the seed spread on the 3-draw design is 0.0041 on an effect of ~0.007 — 59% of
the effect.** That is exactly the quantity 1352 omitted, and it is why its number moved.

## ⭐ CONTROLS

| control | result |
|---|---|
| **PLACEBO** `coval_core` − itself, both metrics | **+0.00e+00 · PASS** (exactly zero, so the pairing is intact) |
| **POSITIVE** same stable seed twice → byte-identical | **PASS** |
| **g=0** a *different* seed changes the draw | **PASS** — required, because reproducibility alone is satisfied by a constant, and a constant is what an unseeded-but-cached draw looks like from outside |
| **NEGATIVE** `sham` − `generic`, exact, ALL | **−0.0193 [−0.0255, −0.0129]** — **below zero**, the register's *"the sham is a poison, not a placebo"* tell. Reported as a magnitude bounding *benefit + harm*, **never** as the ingredient's value. |

## ⭐⭐ THE GRID — 8 cells, reported whole, non-survivors included

`coval_core − generic`, paired per prompt, cluster bootstrap over prompts, 4,000 resamples.

| annotators used | metric | obs | 95% CI | MDE | verdict |
|---|---|---:|---|---:|---|
| 3 draws *(1352's design)* | graded | +0.0191 | [+0.0099, +0.0285] | 0.0133 | RESOLVED |
| **3 draws** | **exact** | **+0.0010** | **[−0.0103, +0.0127]** | 0.0163 | **contains 0** |
| ≤16 | graded | +0.0159 | [+0.0084, +0.0235] | 0.0107 | RESOLVED |
| **≤16** | **exact** | **+0.0085** | **[+0.0016, +0.0155]** | 0.0098 | **RESOLVED** |
| ≤64 | graded | +0.0151 | [+0.0076, +0.0226] | 0.0106 | RESOLVED |
| ≤64 | exact | +0.0073 | [+0.0005, +0.0141] | 0.0096 | RESOLVED |
| **ALL** | graded | +0.0151 | [+0.0076, +0.0226] | 0.0106 | RESOLVED |
| **ALL** | **exact** | **+0.0073** | **[+0.0005, +0.0141]** | 0.0096 | **RESOLVED** |

⭐ **WORLD A. Exact-class RESOLVES on every annotator** — CI width **0.0135** against **0.0231** at
3 draws, a **42% narrowing**. The two non-survivors are **both** 3-draw cells. **`≤64` and `ALL` are
identical to four places**, so the one prompt carrying 1,012 annotators drives nothing — the cap was
the check, and it passed.

## ⛔⛔ AND 1352's ONTOLOGY SHIFT IS OVERTURNED, NOT JUST ITS NUMBER

1352 claimed *"the stricter reading is also the lower-resolution one"* from `MDE_exact 0.0159 >
MDE_graded 0.0134`. **On all annotators the ordering REVERSES: `MDE_exact 0.0096 < MDE_graded
0.0106`.**

⭐ **So exact-class is not intrinsically lower-resolution.** It was lower-resolution **at 3 draws** —
a binary hit needs more annotators to stabilise than a 6-pair mean does. **The property 1352
attributed to the METRIC belonged to the SAMPLE SIZE.**

## WHAT THIS SITE STRUCTURALLY CANNOT DO
| criterion | what it would require |
|---|---|
| independently replicated | a second release or a second team |
| construct validated | an external gold standard for *"the right agreement metric"* — the card explicitly declines to supply one |
| cross-dataset / cross-domain | more than this release |
| causally identified | an intervention on the annotators, not a re-read of them |

⚠ **N/A with what each would require — never "planned".**
