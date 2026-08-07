# R699 · self-inclusion across the sweepers — **R697 is the extreme, and the basis is why**

**⭐⭐⭐ Self-inclusion: **R690 0.0%**, **R692 1.0%**, **R697 34.6%**. The difference is not care — it
is the **basis**. R690 and R692 sweep **source** files, where a round contributes one file among
hundreds. R697 sweeps **artifacts**, and *an artifact that records matched items is itself dense in
them*. **A round that writes what it found into the corpus it searches compounds; a round that reads
code does not.****

## ⛔ CHECK #301 · R698's NEXT PROPOSED THE ACTION R698 HAD JUST PROVED HARMFUL
Its closing line said *"re-run each with its own output excluded"* — and **ledger 848, in the same
commit**, records that re-running a round **overwrites its artifact** and that I had just done it to
R697. **The closing sentence proposed re-running three rounds one paragraph after documenting why
not to.** The safe form — the one R698 itself used on R697 — is to **re-implement and never
execute**. ⚠ **No round's `run.py` was executed by this round.**

## THE MEASUREMENT

| sweeper | basis | with self | without self | ⭐ self-share |
|---|---|---|---|---|
| R690 | source | 3 | 3 | **0.0%** |
| R692 | source | 98 | 97 | **1.0%** |
| **R697** | **artifact** | 81 | 53 | **34.6%** |

Registered **A (R690 15% / R692 5%, `[0,60]`) → 0.0% / 1.0%** · **B (1 of 3 above 20%) → 1, error 0**
· **directional (R697 largest) HOLDS** · kill did not fire.

**Controls:** POSITIVE — excluding R697's own file reduces its count 81→53. **g=0** — excluding a
round with no matching items → **delta 0**, *the instrument can return no-effect*. NEGATIVE —
excluding a nonexistent round changes nothing. PLACEBO — identical.

## ⚠ 34.6% HERE vs 71% IN R698 — BOTH CORRECT, AT DIFFERENT STAGES
R698 measured the **post-filter admissible** population (14 → 4 = 71%); this measures **raw
co-located triples** (81 → 53 = 34.6%). **The filters CONCENTRATE self-inclusion**, because R697's
artifact stores exactly the kind of cells that survive filtering. **Two numbers, one phenomenon, and
quoting either without its stage would look like a contradiction.**

## ⚠ THE UNIT GAP R698 HAD AND DID NOT NAME
These counts are under **my re-implementation**, not under each round's own matcher. **If my matcher
differs from theirs, the share is a property of my code.** R698 had the same gap for R697 and left it
unstated; naming it here is the correction.

## IMPOSSIBLE HERE
Measuring what each round **actually** counted needs its original file list. **None of them recorded
one** — the gap R695 named, R698 inherited, and this round inherits again.

## NEXT
The three sweepers differ by basis, not by care (`results/self_share.json`, field `rows`). Artifact
sweepers compound because their output is dense in what they search for. Enumerate the rounds in this arc
whose `run.py` reads `results/*.json` — a superset of these three — and of those, count how many write
an artifact containing the same field names they search on. That population is the one where the
compounding applies, and it has never been enumerated.
