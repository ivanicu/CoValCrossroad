# R1017 · the belonging clause fails twice over — not evaluable, and implied by ② where it is

**THE DECISION THIS MAKES SAFE.** Whether the arc's one surviving candidate clause is worth stating.
**It is not**, and for two independent reasons.

---

## The clause, in the only form worth testing

> **⑤** an arm **belongs** iff it discriminates **resolvably more than the same criteria on the wrong
> prompt** — i.e. it beats **its own sham**.

Self-referential: no threshold, no comparator, no calibration against another arm. That is what makes
it worth testing rather than the version that would have needed a cut chosen by me.

## ⛔ First failure — identification, and it is a result not a preliminary

**A sham must be SCORED, not computed.** Misdirecting criteria changes which `(criterion, response)`
pairs exist, so a sham's satisfaction matrix **cannot** be derived from its parent's.

| | |
|---|---:|
| arms in the population | **96** |
| arms with a **scored** sham | **4 (4.2%)** — `coval_core`, `gen`, `promptecho`, `topw_k4` |

**A clause that cannot be applied to 96% of candidates is not a clause.** Making it one means running
the judge on a misdirected version of every candidate — **15,488 judge calls per new scored object**
(R921's own price).

## ⛔ Second failure — independent of the first

On the 4 arms where ⑤ *can* be evaluated:

| | belongs | does not belong |
|---|---|---|
| **clause ②** | `coval_core`, `topw_k4` | **0** |
| **not clause ②** | `gen`, `promptecho` | **0** |

**Nothing clause ② admits fails belonging, and belonging admits two more.** ⑤ is **strictly weaker** —
implied by ②, so stating it would be decoration.

⚠ **On 4 arms this is a bound from a handful, not a law** — the same limit as the identification
result, seen from the other side. Both failures are reported; neither is used to excuse the other.

## Controls

| control | result |
|---|---|
| **POSITIVE** | `coval_core` passes ⑤ at **+0.013993 [+0.012842, …]** |
| **NEGATIVE** | **every sham, treated as a candidate, FAILS ⑤ against its parent.** This is the direction that matters: a belonging test a sham passes is not a belonging test |
| **PLACEBO** | an arm against itself returns exactly **0** and fails the strict `lo > 0` — so the clause is not degenerate |
| **NOISE FLOOR** | the deterministic pair's interval width, measured |

## ⭐ Where this leaves the arc

Both available routes to an additional clause are now closed:

| route | verdict |
|---|---|
| **text-only properties** | **closed** — the instance's sham is an exact derangement (R1014) |
| **pairing-dependent: discriminativeness** | post-hoc (R1015) · measures **belonging, not merit** (R1016) · **neither evaluable nor additive** (R1017) |

**The formulation stands at ②′ ∧ ③**, with size and margin **reported, not required**.

## Alternatives considered

**Report the 2×2 as the finding and treat 4.2% as a caveat.** Refused — the order matters. An
unevaluable clause's 2×2 is a curiosity; presenting it first would make a coverage failure read as a
footnote to a result.

**Set a discriminativeness threshold instead, so every arm is evaluable.** Refused: any threshold not
derived from the arm's own sham has to be calibrated against something, and the only things available
are the arms the clause is supposed to judge. That is the circularity R1015 already flagged, rebuilt
to dodge a coverage problem.
