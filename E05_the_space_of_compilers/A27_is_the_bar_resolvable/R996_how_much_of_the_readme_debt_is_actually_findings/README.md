# R996 · 829 overstates the debt — the finding debt is 504, and my first classifier was the search failure

**THE DECISION THIS MAKES SAFE.** How large the README debt actually is. **504 finding-typed rounds,
not 829** — and 504 is itself an upper bound.

---

## The split

R995 said paying the debt *"needs a decision about which rounds deserve a line rather than an
instrument."* That decision has a measurable half: **a round's own commit carries a recorded
`[type.…]` prefix.**

| | |
|---|---|
| unmentioned round dirs | **829** |
| classifiable (have an introducing commit) | 828 |
| **finding-typed** — `verify` 385 · `act` 95 · `think` 22 · `predict` 2 | **504** |
| instrument repairs — `fix` 318 · `guard` 6 | 324 |

**A repair round earns a line in a gate's docstring, not in the findings index.** Quoting 829 as the
findings debt counts the instrument work twice — once where it belongs and once where it does not.

⚠ **504 is an UPPER bound.** The type records what a round *was*, never whether its result survived.
A finding-typed round that was later retracted is counted here and owes no line.

## ⛔ My first classifier was the *a search is an instrument* failure, and its own control caught it

v1 mapped each round to the **first commit whose body mentions it**. But commit bodies cite other
rounds constantly — this project's whole diary style depends on it — so:

| round | v1 said | actually |
|---|---|---|
| R994 | `fix` | **`act`** |
| R993 | `act` | **`verify`** |

**Instrument unit: *a commit body containing "R993"*. Claim unit: *the commit that INTRODUCED R993*.
Not equal** — which is the standard's own remedy, stated as two strings and required to match. The
repair is the one R982 needed: `git log --reverse --diff-filter=A -- <dir>`.

⭐ **This is the sixth population-or-instrument catch this session**, and the first where I ran the
positive control *before* the measurement rather than after. That ordering is why the wrong number
never reached a report.

## Controls

| control | result |
|---|---|
| **POSITIVE** | R994 `act` · R993 `verify` · R974 `fix` · R990 `verify` — all four recovered exactly. **This control already failed once and caught the wrong instrument**, which is what makes its passing mean something |
| **NEGATIVE** | a path never added yields **no type**, not a default |
| **PLACEBO** | **mentioned** rounds classify identically (40 of 40 sampled) — the classifier does not depend on README membership, which is the variable under study |
| **NOISE FLOOR** | none — a recorded field, not an estimate |

## What landed

The README's debt paragraph now carries the split, the type distribution, and the upper-bound
caveat — so the next reader inherits **504 with its scope** rather than 829 without one.

## Alternatives considered

**Filter further to rounds whose result still stands.** Not done here: it needs the retraction ledger
joined to round ids, which is its own instrument with its own control. Naming 504 as an upper bound
and saying what would tighten it is the honest stopping point.

**Classify by reading each round's README.** Refused: 828 reads by the document's own author is the
weakest evidence available, and a recorded field beats a judgement call — the same reasoning that
made R993's generator tag admissible.
