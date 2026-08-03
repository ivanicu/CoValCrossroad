# r220 — Compiler Tournament

Written **before** any number in this round existed. Committed before `run.py` was run.

## What changed, and why the previous framing is withdrawn

The previous framing was: *Core is Full's minimal sufficient executable program under a declared
use*, and the implied next step was *search a minimal criterion subset that reproduces Full's
decisions on A–D*.

**That version is withdrawn.** It would very likely have produced a thing that beats the official
Core **on our own instrument, on our own candidate set, against our own target** — which is
proxy preservation wearing the costume of normative preservation. Seven assumptions were hidden
inside it; each is listed in `THREATS.md` with what it would take to discharge it.

The replacement is not a better Core. It is a **contest that any Core has to enter**, in which our
own proposals have no immunity.

## The object being built

Not `Core v2`. Three separable layers, of which only the second is executable:

| layer | answers | status here |
|---|---|---|
| Source Ledger | what did people actually provide? | the release, uncompressed, plus protocol version |
| Compiled Policy | how should the system decide? | the eight arms below |
| Validation Certificate | what entitles us to call a compression safe? | this file + `results/tournament.json` |

The honest name for the deliverable is **Retrospective CoVal Compiler Benchmark**, not
*Proven Normative Core*. Everything in §"Cannot be run here" is why.

## Arms

Every arm is a map `prompt -> score over {A,B,C,D}`. All are built from the **same** cached
satisfaction tensors, so no arm gets a compute advantage.

| arm | construction |
|---|---|
| `A_official` | the released `coval_core` criteria, unweighted (the release ships no core weights) |
| `B_full` | every `coval_full` criterion at its mean rating — **the reference, not a contestant to beat** |
| `C_signed_topk` | the 4 criteria of largest \|mean rating\|, sign kept |
| `D_decision` | greedy ≤4 subset maximising agreement with `B_full`'s ranking on A–D, **fitted on judge `base` only** |
| `E_typed` | `D_decision`'s subset plus a non-compensatory layer: prohibition-marked criteria act as a filter, not a summand |
| `F_random` | 4 criteria drawn uniformly, 20 seeds — the size-matched floor |
| `G_medoid` | 4 medoids of a lexical clustering of the full rubric — ICAI-**shaped**, not ICAI |
| `H_sign_only` | every full criterion at `sign(w)` — one bit per criterion |

`G_medoid` is not ICAI. ICAI generates new principle text from preference data; nothing here
generates text, because new text needs new judge passes and the point of this round is that the
instrument must not be re-chosen per arm. `G` is the closest no-new-text neighbour and is labelled
as such wherever it appears.

## Axes — a vector, never a weighted total

A single score would smuggle the governance choice back in as weights. `E(C)` is reported as a
vector and the frontier is published, not a champion.

| axis | question |
|---|---|
| `rank_acc` | does it still predict the humans' own world rankings? |
| `regret` | how bad is its winner in `B_full`'s own units? |
| `veto_rate` | does it select a response somebody marked unacceptable? |
| `worst_group` | is the loss concentrated on one demographic group? |
| `transport` | delete a source criterion — does the arm's decision move the way `B_full`'s does? |
| `gauge_spread` | how much of the result is the instrument? |
| `K` | criteria and characters a human must read |

## Instruments

Arms are **built** on `base` (Qwen3.5-2B). They are **judged** on `phi`, `qwen3b`,
`swapped` (response order permuted) and `no_fewshot`. An arm whose advantage exists only on `base`
is gaming the instrument, and this round is designed so that shows up as a number rather than a
worry.

## Pre-registered death conditions

Each is a claim we would like to be true, with the result that kills it. Verdicts are three-valued:
`SUPPORTED` / `REFUTED` / `NOT IDENTIFIED`. **`NOT IDENTIFIED` is never folded into either of the
others** — an unfit check is not an acquittal.

| # | claim | dies if |
|---|---|---|
| K1 | `D_decision` is more faithful than `A_official` | its `rank_acc` advantage over `A_official` does not survive on the evaluation judges (`phi`, `qwen3b`) |
| K2 | decision-fitting learns norms, not the proxy | `D_decision` does not beat `F_random` by more than the seed spread of `F_random` on an evaluation judge |
| K3 | typing prevents type collapse | `E_typed` does not reduce `veto_rate` relative to `D_decision` |
| K4 | compression preserves pluralism | the compressed arms' `worst_group` deficit exceeds `B_full`'s by more than their mean deficit — i.e. loss is concentrated, with no declared governance reason |
| K5 | selection is stable enough to name a Core | bootstrap over annotators changes the selected subset while `rank_acc` stays flat — then there is no *the* Core, only an inclusion probability |

**No threshold in this file is a round number chosen by us.** Every comparison is against either a
competing arm or the resampling spread of a control, per the failure that killed five earlier
claims.

## What CANNOT be run here — the register

Marked `N/A` with what each would require. Never `planned`.

| criterion | what it would require |
|---|---|
| new candidate sets (Test 3) | generating responses E, F, … per prompt **and new human rankings on them**. The release has exactly one 4-response set per prompt, so candidate-set overfitting is **structurally undetectable here** |
| training transport (Test 7) | training `M_A … M_H` plus `+d/−d` twins, and hidden witness cases |
| true lineage | a `source_criterion_id` field on each core item. Inferred lineage is text similarity; only 7.8% is verbatim |
| global veto | `unacceptable` is a **local** exclusion over the four shown responses, collected only in the first ~5 tasks (26.66% of assessments). It cannot be promoted to a hard constraint without new elicitation |
| stable personal norms | `personal` ranking shares that same 26.66% coverage; long-form and short-form protocols are mixed in the release |
| independent replication | a second team or a second release |

`veto_rate` and any `personal`-route number below are therefore computed on the long-form subset
only, and say so at the point of use.

## The circularity that must be declared, not hidden

`D_decision` is fitted to reproduce `B_full`'s decision on the same four responses on which its
`regret` is then measured. **Its `regret` is therefore near-zero by construction and is not
evidence of anything.** It is reported so the reader can see the tautology, and it is excluded from
every verdict. `D_decision`'s admissible axes are `rank_acc` (humans, never seen by the fit),
`veto_rate`, `transport`, and the cross-judge columns.

## Multiplicity

8 arms × 7 axes × 4 instruments. The full grid is published including every cell that kills a
finding. No axis is reported for a subset of arms.
