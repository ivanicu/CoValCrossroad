# R834 · adjudicating the eleven records by reading

**The decision this made safe:** whether R831's W-SELF-DEFEATING rests on enough evidence to keep.
**It does, and on more than before** — the substantive set grows from **3 arms in 1 family** to
**6 arms across 4**, and the top 8 remain **8/8** label-readers.

Design in `PREREGISTRATION.txt`, committed before the recomputation. `run.py` and
`adjudication.json` committed before it ran.

## Why not the round my own NEXT named

R833 closed: *"any replacement instrument must parse negation."* ⛔ **That is a third regex
refinement**, and §4's *a search is an instrument* has already been wrong **twice** — at the loose
pattern, and at the tight pattern **with a passing positive control**.

**R833 already showed what works**: four full commit bodies read by hand in one command gave the
right answer; the regex is what got it wrong. **Adjudication is the measurement**, established four
times in this arc. So this round reads all eleven.

## The adjudication — committed as DATA, with every verdict quoted

| arm | rank | by record | resting on |
|---|---|---|---|
| `coval_core` | 11 | **EXCLUDED** | *"select up to four rubric items with the highest average ratings"* — the **release's** card, via R475 |
| `coval_core_2bA` / `2bB` | 14 · 15 | NO-RECORD | no introducing commit; inheriting a sibling's provenance is **inference, not record** |
| `generic` | **21** | **ADMITTED** | *"four GENERIC quality criteria, identical on every prompt"* — all four listed verbatim |
| `generic_reprov` | 22 | NO-RECORD | — |
| `genericpool16` | 25 | UNDECIDED | the record discusses clause 2's **wording**, not this arm's construction |
| `gen` | 27 | **ADMITTED** | *"a local 2B model that saw the CONVERSATION and the FOUR RESPONSES and never the rubric"*, with I2 verbatim **0.0000**, I3 novel **0.9920** |
| `coval_core_sham` | 40 | **EXCLUDED** | *"prompt i gets prompt i+1's coval_core criteria"* |
| `gen_sham` · `promptecho` · `promptecho_sham` | 52 · 66 · 70 | ADMITTED | same constructions, misdirected |

**Controls**: `coval_core` → EXCLUDED from an **external** record (**PASS** — my reading did not
drift toward comfort) · every ADMITTED/EXCLUDED verdict quoted **7/7** · two-seed byte-identical.

⭐ **Three of R833's regex statuses are corrected here**, and the corrections are visible only
because the artifact carried the quotes: `gen` was EXCLUDED off the **negation** *"never having seen
coval_full"*; `genericpool16` off a sentence about the **clause**; `coval_core_sham` ADMITTED off a
commit **subject line**.

## The recomputation

| | R831 | R834 |
|---|---|---|
| substantive ③-admissible set | **3** arms | **6** arms |
| families | **1** (`topvar`) | **4** (`generic`, `gen`, `promptecho`, `topvar`) |
| best rank | 50 / 93 | **21 / 93** |
| top-8 that are label-readers | 8/8 | **8/8** |

**W-STRENGTHENED.** R831's NEXT asked me to *build* a second family of label-free substantive arms.
**Two more were already on disk**, and a third. The `BASELINE` regex and rank source are copied
unchanged from R831, so the new number is comparable to the one it replaces.

## NEXT

Four arms remain unreachable — `coval_core_2bA`, `coval_core_2bB`, `generic_reprov` have **no
introducing commit**, and `genericpool16`'s record does not name its construction. ⛔ **CORRECTED THE NEXT ROUND.** Those three arms have **no `core_*.json`** — they are scored from
`sat_*.npz`, whose introducing commits exist but are **housekeeping**: `generic_reprov`'s is a
**file-restoration** commit, `coval_core_2bA/2bB`'s does not name their construction. So the gap is
in **my record-finder's population**, and the proxy limit is that **an introducing commit is the
constructing round only when the file was first committed by the round that made it**. See
`RETRACTIONS.md` 1293.
