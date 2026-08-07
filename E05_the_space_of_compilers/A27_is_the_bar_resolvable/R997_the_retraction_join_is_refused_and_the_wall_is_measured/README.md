# R997 · the retraction join is refused, and the wall is measured with its mechanism

**THE DECISION THIS MAKES SAFE.** Whether R996's **504** can be tightened. **Not on this corpus** —
and the reason is a structural fact with an exact reopening condition, not a shrug.

---

## The control ran first, and it refused the join

R996 said the join needs "its own control before its own count." It got one.

| | |
|---|---|
| numbered ledger entries | 1,149, ids **236..1387** |
| gate floor (`a_retraction_declares_its_class.py:50`) | **1388** |
| **entries carrying a declared link** | **0** |
| entries matching a loose `R\d{2,4}` scan | **799 (70%)** |

**R954's header format binds from entry 1388 and the ledger stops at 1387 — so it has never bound on
a single entry.** The gate says so itself, printing *"0 entr(y/ies) in scope"* and exiting **2,
empty population, correctly.**

⭐ **So the loose scan fires on 70% of entries with zero ground truth to calibrate against.** That is
uncalibrated **by construction** — the failure R996 caught one round ago, and here there is no
positive control available *at all*. **A hit from an instrument never shown to return a correct miss
is not evidence**, so the 799 is inadmissible and **504 stands as an upper bound.**

## Controls

| control | result |
|---|---|
| **POSITIVE** | the header regex **matches** a synthetic entry in R954's own documented format — so "0 declared links" is a **measurement of absent structure**, not a broken pattern |
| **NEGATIVE** | it does **not** match a bare prose mention (`"this withdraws what R123 said"`) — exactly what the loose scan counts |
| **PLACEBO** | the ledger's highest id **1387** sits below the floor **1388** — the emptiness is **structural, not accidental**, and that one-integer gap is the whole mechanism |

The positive control is the load-bearing one: without it, this round would be reporting silence.

## ⭐ Reopens at entry 1388

Exactly. The gate already exists, its vocabulary is already loaded, and its first real test is the
next retraction written. **A gate that binds only on the future is not broken — but its emptiness is
not evidence of compliance either**, which is why it exits 2 rather than 0.

## ⚠ An unresolved discrepancy, recorded rather than explained away

**R951 reported 8 entries declaring a link. Under R954's header the count is 0.** R951 predates that
format, so these are probably different instruments — but *probably* is not a finding. It is logged
as UNVERIFIED in the artifact, because folding it into "different instruments, no issue" would be the
false-acquittal direction, and a cleared discrepancy is one nobody re-examines.

## Alternatives considered

**Use the loose scan and report a tightened number.** Refused: 70% hit rate with no ground truth is
the exact instrument R996 caught, and repeating it one round later would make the catch worthless.

**Lower the gate's floor to bind on history.** Refused: R951 established the history carries no class
structure, so a floor at 236 would make the gate fail on 1,149 entries forever — and a gate that
fails on all history is one nobody runs, which this project has already written down as a rule.
