# R342 · How many of the points this suite CHECKS are ratios?

**The decision this makes safe:** whether the guard's coverage number can be read as a validity
number. It cannot yet — **not because the corpus is contaminated, but because my reader is.**

## Why the question

R341 named an exception class and stopped: `point inside its own interval` is stated **sound** in the
guard's proxy ledger and gated on, and it is **not sound** for a ratio summarised by its bootstrap
mean. R341 could stop because `eta` is not a `MEANISH` name — an accident of naming, not a property
of the suite. So: of the pairs the guard *does* check, how many are ratios?

## Identification, before power

A published number carries no record of how it was built. `0.0128` is a difference, a ratio and a
regression coefficient in the same JSON. **The quantity is not identified from artifacts at any
sample size** — no amount of offcentre arithmetic decides it. It is identified from the source, by
the construction of the expression assigned to the key. Hence an AST, not a regex: a substring search
for `/` matches every path literal in the corpus.

## Result — a bound, and the bound is the reader

Population: the **42 distinct (round, mean_key)** pairs behind the guard's **389** checked pairs — a
census, not a sample.

| label | keys | checked pairs |
|---|---:|---:|
| RATIO_DATA | **1** | 6 |
| RATIO_CONST | 0 | 0 |
| NON_RATIO | 28 | 155 |
| **UNRESOLVED** | **13** | **228** |

`UNRESOLVED` is **31% of keys** — above the 25% pre-registered ceiling — so the pre-registered
branch fires **W3**: report a bound. **RATIO_DATA is between 1 and 14**, and a point estimate here
would be a guess wearing a count's clothes.

**The unreadable cases are idioms, not obscurity**: `items()`, `values()`, `get()`, `zip()`,
`defaultdict()` — dict traversal and comprehensions this reader does not follow. One key,
`R235_independent_B:delta`, is **178 of the 228**.

## The one flag, adjudicated by reading rather than by a rule

`R06_rule_tournament:delta` is `wins / max(n, 1) − wins_b / max(n_b, 1)` (`run.py:210-211`).
**`max(count, 1)` is bounded below by one, so the denominator cannot approach zero** and the
pathology cannot occur.

**I did not teach the reader about `max(x, c)`.** That rule would have been added *after* seeing
which case it clears — a threshold chosen to fit a result. So the rule stands, the flag stands, and
the case is adjudicated in the source by a read, **labelled a judgement and kept out of the count**.

## The repair ledger — four repairs, each moving the count

| repair | forced by | RATIO_DATA after |
|---|---|---:|
| tuple-unpack targets | 7 of 9 UNRESOLVED were `d, lo, hi = …` — the corpus's commonest idiom | 1 |
| local function bodies | the division lives inside `ci()` / `paired()`, invisible at the call site | 1 |
| positional tuple binding | **the cross-instrument prediction** — see below | 0 |
| method form of a reduction | planted control: `x.mean()` has no args, the operand is the base | 1 |
| ⛔ **not made**: `max(x, c)` bounded | would be a rule chosen after seeing which case it clears | — |

**Every repair was forced by a planted control failing or by a conservatism this file had already
declared in writing — never by disliking the number.** That each one moved the count is the finding
about this class of instrument as much as the census is.

## The cross-instrument prediction, and it fired

Pre-registered: a live ratio should *also* show a large |offcentre| on the **artifact** side
(R340's table). Agreement is weak evidence; **disagreement means the framing is the finding.**

It disagreed. The source side called `R127_whose_sign` a live ratio while the artifact side put it at
**offcentre 0.02** — and a real ratio pathology cannot be centred. Reading it: R127 does
`d_all, lo_all, hi_all, p_all = paired_boot(...)`, and `paired_boot` returns
`(mean(dd), pct(dd,2.5), pct(dd,97.5), max(p, 1.0/(n+1)))`. **The only division is the permutation
p-value floor, in the fourth slot**, and my conservative whole-RHS binding handed it to `d_all`, the
plain mean the guard actually checks. Positional binding is *exact* there, not merely tighter.

**A prediction that could not have come out `disagree` would not have been a test.** This one did,
and it localised to my instrument in one read.

## Controls

| | returned |
|---|---|
| **PLANTED**, 22 cases, both directions on every capability | **22/22 OK** |
| **REAL**, R235 `eta` (known ratio) | want RATIO_DATA, got **RATIO_DATA** |
| **REAL**, R141 `delta_mean` (known mean) | want NON_RATIO, got **NON_RATIO** |
| **SPEC CURVE**, MAXDEPTH ∈ {1,2,3,4,6,10} | RATIO_DATA ∈ {0,1}; stable at 1 from depth 3 |
| empty population | exit 2 |

**Two planted controls caught real defects in the reader**, and both were false *clears*:
`{"delta": float(np.mean(ds))}` with `ds` undefined (my expectation was wrong, the instrument was
right — an unfollowable name is not a cleared name), and `d, lo, hi = opaque_call()`, where a
function whose body this reader has never seen was being returned **NON_RATIO**. Every real case in
the corpus happens to call a reduction, so **only the plant could have found it.**

## Register — what this site structurally cannot do

| criterion | status |
|---|---|
| multi-seed | **N/A** — deterministic AST census; two runs byte-identical (`b5c72ee46c8e`) |
| uncertainty-quantified | **N/A** — complete-population count, no sampling error |
| multiplicity | family size 1 |
| construct-validated | **N/A** — "is this expression a ratio" has no external gold standard; the planted cases are the closest available and they are mine |
| **the reader's own coverage** | **the binding limit, and it is not structural** — comprehensions and dict traversal are implementable; 228 of 389 pairs wait on that, not on the corpus |

## Verdict

`W3_BOUND_ONLY`. **RATIO_DATA ∈ [1, 14] keys**, the one flag adjudicated safe by reading. The guard's
389-pair coverage number **cannot yet be read as a validity number**, and the obstacle is the reader.

## The sentence I can no longer write

> *"zero of the checked points are ratios, so the exception class is dormant."*

It was true of three of my four readers and false of the fourth, and the honest output was never a
count.

Artifact: `results/r342_ratio_census.json`, guard `sha256[:12] 653d2b0f5f22`.
