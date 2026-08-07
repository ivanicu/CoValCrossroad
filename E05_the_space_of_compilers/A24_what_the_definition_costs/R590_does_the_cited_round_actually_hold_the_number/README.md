# R590 · The citations are mostly grounded — after my matcher stopped manufacturing orphans

**Decision this makes safe:** the shared values are largely **replication**, not carried-forward
citation. **Four remain open.**

**WORLD B, at 4 not 13.**

| | prefix matching *(v1)* | **rounded matching** |
|---|---|---|
| grounded | 6 | **15** |
| **ORPHAN** | **13** | **4** |

**Of 24 shared values, 19 carry a citation in `STATEMENT.md`. 15 are present in the cited round's own
artifact.** The remaining four: `0.0200 → R514` · `0.0779 → R535` · `0.5404 → R475` · `0.5451 → R479`.

## ⛔ Nine of the thirteen orphans were mine
**The document rounds to 4 places; the artifact stores full floats.** My v1 matcher required the
printed value to be a **prefix** of a stored one — so every value the document rounded **up** failed.
Spot-checking eight reported orphans: **7 matched once compared by rounding.**

⭐⭐⭐ **The confound was visible before running it and I checked it before reporting, which is the
only reason the headline is 4 and not 13.** A "13 of 19 citations are ungrounded" claim would have
been a serious accusation against the deliverable's provenance, published on an artifact of my own
string handling. **Thirteenth instance this session of matching the string as I picture it — and the
first caught by asking "what would make this wrong?" before the write-up rather than after.**

## What stands
**The 24-value bridge across the eras** *(R589)* **is mostly grounded replication**: the values recur
in later rounds' own artifacts, not merely in later prose. ⚠ **Four are unaccounted**, and each is a
specific, checkable pair — **not a diffuse worry, and not yet a defect either**: an absent value may
sit in a sibling round, a derived quantity, or a differently-named key.

## Controls
- **Positive** — a shared value is found in its cited round. **PASS** *(and it passed in v1 too, which
  is why the v1 failure was invisible to the control: a control that fires on one true case cannot
  detect a systematically biased matcher)*.
- **Negative** — an invented value found nowhere. **PASS.**
