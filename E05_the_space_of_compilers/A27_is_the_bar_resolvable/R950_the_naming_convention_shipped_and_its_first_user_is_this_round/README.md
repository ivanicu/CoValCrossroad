# R950 · the naming convention, shipped as a gate, with this round as its first user

**PRODUCTION.** Not a frontier action, and the label matters: R941–R949 were the measurement, and
nine consecutive rounds of instrument audit with nothing shipped is exactly the failure §0.2 names.
This builds the repair R949 identified, attacks it, and lands it.

## The decision this executes

R949 measured that a published number's JSON path and the sentence stating it share vocabulary at an
agreement of 0.200000, against a within-round permutation floor whose high end is 0.139000 — real
separation — and against a ceiling of 0.983000, so unusable keys explain almost none of the gap.
`cells[0].gap` holds the number the statement calls a *price*: both right, no shared word. No lexical
bridge can verify quantity-level attribution while the two vocabularies stay disjoint.

## What was built

`assurance/a_published_number_is_named.py` — from R950 onward, a number a round states in its README
must sit at a path that names it in the round's own words. It never reads the definition's statement,
because renaming keys to match a sentence would make the agreement true by construction.

`assurance/attack_a_published_number_is_named.py` — seven vectors, each performed against the live
gate in a subprocess. The attack's vector pass rate is 1.000000, covering the two failures this repo
has actually shipped: an empty population that passes, and a matcher that fires on function words.

## What it does not do

It cannot repair the roughly 900 committed rounds and does not try. R949's measurement of the
existing corpus stands unchanged. The proxy is one-directional — `gap` and `price` can both be
correct — so a failure means *unnamed by this check*, never *wrong*, and the remedy costs one word.

## The defect caught before shipping

The first draft globbed `E0*/A*/R*`, which misses `E99_fixtures/A01_planted`, where every attack
harness plants. The lock would have been untestable and its own attack would have reported vectors it
never ran — R928's failure, reproduced in a gate written after reading R928. Repaired by asking
`covalx/rounds.py`, which exists so that a gate cannot be wrong about where a round lives.
