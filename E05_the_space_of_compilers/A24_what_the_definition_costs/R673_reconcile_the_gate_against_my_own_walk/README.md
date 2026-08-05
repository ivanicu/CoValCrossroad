# R673 · reconcile the gate's walk against my own — 249 vs 167

**⭐⭐⭐ The gate walks the last 400 of 1,233 commits. Its freeze is not a record of the repository —
it is a record of a MOVING WINDOW, and 68 of its 167 entries (40.7%) have already scrolled out of
the view that would ever re-check them.**

## THE PRE-REGISTERED KILL FIRED, AND MY HYPOTHESIS IS DEAD
Registered: *≥70% of the gap is the NEXT-extraction rule, not the commit range*; kill if the walks
differ by more than 20 commits. **They differ by 833.** Varying each factor alone:

| rule × range | flagged |
|---|---|
| gate rule × gate range (400) | 90 |
| ad-hoc rule × gate range (400) | 106 — **extraction effect +16 (10.1%)** |
| ad-hoc rule × all (1,233) | 249 — **range effect +143 (89.9%)** |
| gate rule × all (1,233) | 240 |
| freeze | 167 |

I registered extraction and the range is the larger term by 9×. Both real; the split is **10/90**.
(The extraction difference is the gate requiring `^NEXT:` **with a colon** and taking the LAST such
paragraph; mine required neither.)

## ⚠ THE −77 WAS NOT A RESIDUAL, AND REPORTING IT AS ONE WOULD HAVE HIDDEN THE FINDING
The gap was defined against the **freeze**, which is not one of the four cells — so the arithmetic
does not close, and the shortfall is a real quantity wearing a remainder's clothes:

| | |
|---|---|
| freeze entries resolvable to a commit | **167 of 167** |
| inside the gate's 400-commit window | 99 |
| ⭐ **scrolled out — frozen but invisible** | **68 (40.7%)** |
| in-window but no longer flagged by the gate's own rule | 9 |

**Controls:** POSITIVE — the two extractions agree on 83 shas in the shared window, so they measure
the same object. NEGATIVE — frozen shas are flagged by both walks. PLACEBO — the gate's extraction
run twice is identical.

## ⭐ CHECK #274 · R672's CITATION WAS FALSE, IN THE CLAUSE I WAS PROUDEST OF
R672 took the gate's PROVENANCE escape — untouched in 283 of 284 prior opportunities — citing
`results/freeze_history.json` for the number 249. **`grep -c 249` on that file returns 0.** The
escape passed because `PROVENANCE` matches the *shape* of a citation and **never opens the file**.
So the first use of the escape in this repository's history was a false one, and the gate certified
it. Recorded now, not deferred.

## WHAT THIS DOES TO R672
R672 concluded the freeze is a **drain** — it only fills. That stands and gets worse: it fills at one
end and **leaks at the other**, as entries scroll past commit 400 and become unreachable by the only
instrument that could retire them. The single retirement in 26 transitions was never going to be
joined by others; the mechanism forbids it.

## NEXT
`PROVENANCE` accepts a citation without reading the cited file (`results/reconciliation.json`,
field `check274`, and the false citation is in commit `424efff`). Build the semantic version — for
each accepted window, open the referenced path and test whether the number stated beside it actually
occurs there — and run it over the two known takers of the escape. Population is 2, so this measures
the *rule*, not a rate, and no share should be reported from it.
