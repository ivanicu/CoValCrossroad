# R675 · a citation that names a FILE TYPE, not a file

**⭐⭐⭐ 22 of 27 unresolvable citations come from commit bodies, which carry no directory at all. The
defect is in the writing, not the instrument — and my registered prediction missed by 66.5 points
because I wrote the identification limit before the run and then predicted as if it did not bind.**

## ⭐ CHECK #276 · R674's NEXT PROPOSED A ROUND WITH AN EMPTY POPULATION
It asked to split the 27 into *"never existed"* vs *"renamed since"*. **All 27 are neither** — every
one is a bare basename (`run.py`, `README.md`) matching **630 files**. Both proposed causes have
population **zero**. Running that round would have been a gate reporting success having examined
nothing. *And ledger 748 — "a bucket named for what it lacks hides how many distinct causes are in
it" — was written in the same commit as the NEXT line that undercounted them.*

## THE PRE-REGISTERED KILL FIRED
Registered **85% [60%, 100%]** of under-specified pairs recover under contextual resolution; kill if
fewer than 10 recover. **5 recovered. Error −66.5 pts.**

| | |
|---|---|
| under-specified pairs | 27 |
| README-sourced (**have** a directory) | **5** |
| commit-sourced (**have none**) | **22** |
| recovered by contextual resolution | **5 (18.5%)** |

## ⭐ THE MECHANISM WAS RIGHT AND THE POPULATION WAS WRONG
**5 of 5** README-sourced pairs recovered — **100% where context exists.** **0 of 22** where it does
not, and no resolver can place them: a commit body has no directory, so `run.py` in one identifies
nothing. My resolver *was* wrong to drop the 5. Fixing it recovers 5, not 27.

**Controls.** POSITIVE: a pair citing its own round's file resolves to **that** file. **g=0**: the
same control **fails** against a directory lacking it. NEGATIVE: a bare basename with no directory
stays UNRESOLVABLE. PLACEBO: a basename no file carries stays UNRESOLVABLE.

## WHAT THIS DOES TO R674's 47.5%
**It stands, and now its denominator has a name:** it is measured over citations that *identify a
file*. The 22 that name a file *type* are correctly outside it.

⚠ **Estimand B was NOT computed** — the pre-registration says it is not computed when the kill fires,
and that is binding. What is available without computing it is **arithmetic, labelled as such**:
adding 5 pairs to 80 decidable can move the rate by **at most 5/85 = 5.9 pts** in either direction.
That is a **DERIVATION** — it could not have come out otherwise — and it is not evidence.

## IMPOSSIBLE HERE
Resolving a commit body's bare basename would require inferring which round the commit touched.
**That is an inference, not a citation**, and imputing it would manufacture provenance rather than
measure it.

## NEXT
22 of 27 under-specified citations sit in commit bodies (`results/contextual_resolution.json`, field
`commit_sourced`). A commit body **does** carry one piece of context my resolver ignored — its own
diff. Test whether restricting resolution to the paths the citing commit actually touched places
those 22, and report the share placed and the share still ambiguous. If a commit's own diff resolves
its citations, the writing defect is smaller than this round concluded and the bound of 5.9 pts above
is the wrong bound to have quoted.
