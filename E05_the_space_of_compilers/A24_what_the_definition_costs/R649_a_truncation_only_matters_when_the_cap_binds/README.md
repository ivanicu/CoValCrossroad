# R649 · A truncation is only a defect when the cap binds — and only a *finding* when it changes the answer

**Decision this makes safe:** whether R648's closing repair — *"never pipe an instrument's output
through a truncating filter"* — needs to become a code change across the corpus. **No. It is one
site, the cap binds on 4 of 900 files, and it changes nothing today.**

## Three levels, and only two of them were true

| level | count | |
|---|---|---|
| **① sites** — a truncation between the data and a search | **2** in **1** round | R601:104 (`read_text()[:200000]`) · R601:109 |
| **② binding** — the cap is exceeded by a file *that site reads* | **4 of 900** | 246 KB · 1.36 MB · 1.29 MB · 2.61 MB |
| **③ consequence** — the classification actually changes | **0** | no tail carries a token its head lacks |

⭐ **Binding is not consequence, and I would have reported ② as the finding.** The corpus contains
the pattern, the cap really is exceeded, and R601's published answer is still correct — *by luck,
not by design.* One artifact over 200,000 chars that mentions the second corpus flips a round to
home-only, silently.

## ⛔ The round's own first two instruments were both wrong, in opposite directions

| pass | rule | returned | why it was discarded |
|---|---|---|---|
| **v0** syntactic | slice inside `print()` or not | **587** "suspects" | top rows were `hexdigest()[:16]` — *a hash is not a truncated population* |
| **v1** AST, loose | any slice on a read/stream that is *used* | **36** sites | **34 were `git rev-parse HEAD`.stdout`[:12]`** — an artifact stamp. A truncated **identity** is not a truncated **population**: shortening a sha costs collision resistance, never a member |
| **v2** AST, tight | must reach a search *through a name* | **0** sites | over-corrected — R601 writes `blob += …[:200000]` and searches `v["blob"]`; the value escapes into a **dict**, and no name-level rule follows it. **The pre-registered KILL caught this** |
| **v3** intrinsic | a truncated **file read** always can lose members; a truncated **process line** only if searched | **2** | *the discrimination moved off dataflow and onto the source* |

**v1 → v2 → v3 is the shape worth keeping:** too loose gave 36, too tight gave 0, and the fix was
not a better threshold but **a different thing to condition on.**

## ⛔⛔ And the positive control passed on the wrong site

v1 printed `POSITIVE … FOUND at line 109, cap 110 → PASS`. **Line 109 is R601's README heading — a
display slice.** The known member is line 104. The control asked *is R601 in the list*, took
`pos[0]`, and I read it as *the classifier sees the known member*.

> §4, verbatim: *a positive control asks "can this instrument see?" and never asks "is what it sees
> the thing I am about to claim about?"* — **this time inside the control itself.** Repaired to pin
> the exact `(file, line, cap)`.

## ⭐⭐⭐ And the impossibility register was wrong in the flattering direction

The docstring registered *"whether any round's published number is wrong … needs a different
round"*. **It needed one pass over four files.** For a search-type site the question is not *re-run
without the cap* but *does the tail match where the head does not* — with a planted token past the
cap as its own positive control.

**An impossibility that saves work is the one to check first.** §4's `a wall never checked`.

## Controls

| control | returned |
|---|---|
| **positive** — R601:104, cap 200000, pinned by file+line+cap | **FOUND — PASS** |
| **negative-1** — `hexdigest()[:16]` + a `print()` slice | **0 classified** (hash=1, display=1) — PASS |
| **negative-2** — a git sha `[:12]` stored in an artifact | **0 classified** — PASS, *an identity is not a population* |
| **g=0** — an empty program | **0 sites** — PASS, it can fail |
| **placebo** — a reader method no file calls | **0 sites** — PASS |
| **positive (consequence)** — a token planted *past* the cap | **seen in tail, not head** — PASS |

**MULTIPLICITY:** 1 classifier × **324 rounds** × 6 controls + 3 caps swept per-site.
**Non-survivors reported: 10 display + 188 hash + 35 stamp slices classified NOT defects** — the
non-survivors outnumber the finding 116:1, which is the point.

**IMPOSSIBLE, named:** the consequence test needs the site's read population to be **re-derivable
from its own source**. **1 site (R601:109) is not** and is reported `UNVERIFIED`, never "inert".

## The sentence I can no longer write

> *"the truncate-before-parse error is only in my shell commands."*

It is in the corpus — **once**. And the mirror sentence is equally dead: *"587 slices are
suspect"*, *"36 rounds truncate before counting"*. **116 of 118 slices in this corpus are correct.**

## NEXT

**R601:109's population is not re-derivable from its own source, which is why it returned
UNVERIFIED — and that is a property of how the round was written, not of the question.** The site
reads `(d / "README.md")` under a glob that *is* in the file; my `population_of` simply has no
entry for it. **Check whether the read population of every site in this corpus is recoverable by
resolving the globs in the same function**, because if it is, the `UNVERIFIED` here was mine and
not the code's — and the same hand-written lookup table will silently return `UNVERIFIED` for
every future site, which is a control that fails toward "nothing to see".
