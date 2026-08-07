# R1077 — 34 blind sites is not 34 defects. ⭐ **22 CANNOT be exposed; 12 are at-risk — and that is an upper bound.**

**The decision this round makes safe:** how much of R1076's `34 precision-blind` needs acting on.
**At most 12** — and the sound claim is the other half.

## Result

| | |
|---|---:|
| precision-blind sites (R1076) | **34** |
| **NOT-EXPOSED** — the round reads no prose at all | **22** |
| **AT-RISK** — the round reads prose somewhere | **12** |
| UNKNOWN | 0 |
| at-risk share | **0.353** — neither pre-registered band |

⭐ **The 22 compare values that never left a computation, where exactness is correct.** The 12 are the
list to read.

## The proxy ledger, written before the run

| | |
|---|---|
| **PROPERTY** | the exact comparison can meet a value that was *displayed* before being compared |
| **PROXY** | the round's source performs an actual `.md` file operation |
| **IMPLICATION** | `reads no prose ⇒ cannot be exposed` **SOUND** · `reads prose ⇒ is exposed` **NOT SOUND** |
| **WITNESS** | a round may read prose for titles or sections and never compare a displayed value |
| **SAFE SIDE** | prose-reading returns **AT-RISK**, never CONFIRMED |

⭐ **So the round's actual claim is the negative one: 22 sites cannot be exposed.** The 12 is an
**upper bound**, reported as such.

## ⛔ The proxy's first version matched mentions, not reads

Searching for `DEFINITION`, `README`, `.md` as **words** classified nearly everything as
prose-reading — **every round's docstring discusses the definition**. §4's *a grep is a measuring
instrument*, third time this window.

⭐ **And the fix was not a tighter word list.** It was to **strip comments and docstrings via AST and
search executable code only**. A mention is not a read. The negative control — R923, which reads only
`.npz` and prior artifacts — is what forced it, and it went from **False** to **True** on that change
alone.

## Controls

- **POSITIVE** — **R1070**, whose exact test caused R1075's retraction by comparing against a value
  read from the statement, must classify **AT-RISK**: **True**. A separator that misses the one
  confirmed case cannot triage the rest.
- **NEGATIVE** — **R923**, which reads only `.npz` and prior artifacts, must classify
  **NOT-EXPOSED**: **True** *after* the docstring fix; **False** before it.
- **PLACEBO** — an unreadable file yields **UNKNOWN**, never NOT-EXPOSED.
- **MULTIPLICITY** — all 34 reported with verdicts, not only the exposed.

## IMPOSSIBLE here

- **whether an AT-RISK site actually compares a displayed value** — needs the dataflow, not the file
  list. **SETTLES: IN-RELEASE** by reading each; **narrowing 34 to 12 is the point.**

`run.py` · `results/exposed_sites.json`
