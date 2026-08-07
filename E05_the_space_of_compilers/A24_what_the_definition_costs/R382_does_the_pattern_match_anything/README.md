# R382 — one pattern matches nothing, the other matches 505 times, and they are not a class

**The decision this makes safe:** *are the flagged regexes one shared defect?* **No.** Separate
repairs — and my own count of them was wrong before the measurement started.

## Result — `W_MIXED`. Three controls PASS. Two runs byte-identical. **No GPU spent.**

| gate | pattern | README | arc READMEs | round sources | total |
|---|---|---:|---:|---:|---:|
| `donor_numbers_carry_their_draw_scope` | `rounds/r8[89]_[a-z_]+\)` | 0 | 0 | 0 | **0** |
| `synthesis_cites_recent_work` | `(?:\d\d_[a-z0-9_]+/)?r(\d+)_` | 1 | 22 | 482 | **505** |
| `seed_filter_is_disclosed` *(not a link)* | `len\(raters\)\s*\+\s*1\)\s*//\s*2\|>=\s*thr\b` | 0 | 0 | 32 | 32 |

Corpora: **1 + 24 + 364** files, **5.6 M** characters.

## ⛔ First, a correction to my own count

R381 reported **three** red gates carrying a *"stale link format"* regex.
`seed_filter_is_disclosed`'s pattern is `len(raters)+1)//2 | >= thr` — it was flagged because `//`
is **integer division**, and R381's `path_shaped` accepts any literal with a slash.

**The link class is two, not three.** R381's number was right about what it measured and wrong as a
description of what it found — **the fourth distinct false-positive class that census has produced.**
The excluded pattern is still measured and printed, because *hiding a number because it does not fit
the class is how a class becomes unfalsifiable*.

## ⛔ I did not infer any pattern's target

Reading the source says `CITE` is applied to README lines and `FILTER` to round sources — **but a
claim resting on my reading of three call sites is a claim resting on me.** Each pattern was run
against **every** corpus it could possibly be applied to. A zero across all of them is a zero
wherever it is pointed, with no inference about intent. **A superset of the intended target makes a
zero strictly stronger.**

## ⛔ The negative control failed first, and was right to

`zzq_no_such_token_zzq` matched **twice** — both inside **this round's own source** (the docstring
and the `NEG` constant). Not a quirk of the control: **it would have inflated all three pattern
counts too**, because this round prints the patterns it measures.

**A round whose own text joins the corpus must exclude itself** — R376's scaffolding lesson at a
fourth level. Excluded structurally by path, and the control then returns 0/0/0.

## ⭐ Two facts, and they point opposite ways

**`donor_numbers…SCOPE` is dead — and this is an independent second confirmation.** R380 measured
that gate's GATE 2 vacuous by counting **locatable README table rows** (0). R382 measures the same
vacancy by counting **pattern matches** (0). *Two different instruments, one conclusion.*

**`synthesis_cites_recent_work.CITE` matches 505 times.** R381's *"stale link format"* reading is
**refuted for it** — its exit 2 has some other cause entirely, and looking for a stale pattern there
would have been a repair aimed at a symptom that does not exist.

## Controls

| | returned |
|---|---|
| **POSITIVE** | `round_links_resolve.LINK` — lifted from a gate that **exits 0** — matches **83** lines of README.md. A counter returning zero for everything would make every zero below meaningless |
| **NEGATIVE** ⭐ | an impossible token matches **0 / 0 / 0** after self-exclusion. Both directions, because a counter returning large numbers for everything would pass the positive control |
| **EXTRACTED** | every pattern read out of gate source by `ast`, **never retyped** — a retyped regex is a different regex |
| **CORPUS** | sizes printed; an empty corpus exits 2, because a zero from an empty corpus is silence |
| reproducibility | two runs **byte-identical** (`778654351532`) |

## Register

| criterion | status |
|---|---|
| **whether a zero CAUSES its gate to fail** | **N/A** — that is R380's shape of round, and it needed a disarm proof at the end. This measured the **pattern**, never the **gate** |
| **patterns built at runtime** | **N/A** — only module-level compiled patterns are extracted |
| **a second release** | **N/A** — one release |

## The sentence I can no longer write

> *"[HYPOTHESIS] I expect at least two of the three to match zero lines … because both link patterns
> encode the pre-migration form."*

**The class was two, not three; of those two, one matches zero and the other matches 505 times. They
are separate repairs, and calling them one would be the grouping error R379 already cost a round.**

Artifact: `results/r382_pattern_matches.json`, source-stamped.
