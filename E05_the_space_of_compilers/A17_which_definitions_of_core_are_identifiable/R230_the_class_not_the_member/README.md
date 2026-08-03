# R230 — the arc was identifying the wrong object

**Arc E05·A04.** R224–R228 all set `H_need = log₂C(n,k)` — the bits needed to name *which* k-subset
— found it too large, and concluded the core was unidentifiable.

But the project's own definition (paper §2, **C6**) says normative information **is** the equivalence
class `[N]_Q`. Under that definition the object to identify is not a subset, it is a **class of
behaviours**, and

```
|{classes under Q}|  ≤  |{possible observations}|  =  a(m)
```

**by construction**, because Q's classes are *defined* by the observation. So
`H_need(class) ≤ log₂a(m) = H_have`, **always**.

> **The class is always identifiable. The member never is.**
> And R228's *"three of the official core's four criteria are not recoverable"* is not a defect —
> **it is what choosing a representative means.**

## The derivation

| | median | max |
|---|---:|---:|
| `C(n,K)` subsets per prompt | 72 | 120 |
| **distinct Q-classes they fall into** | **13** | **27** |
| collapse factor | **5.2 subsets per class** | |

`log₂13 = 3.70 bits` needed against `log₂75 = 6.23` available — identifiable with room to spare. No
prompt exceeds `a(4) = 75`, which is forced, not measured.

## The measurement — noise and degeneracy are different obstacles

| eps | member | spread | class | spread | gap |
|---:|---:|---:|---:|---:|---:|
| 0.00 | 0.1868 | 0.0188 | **1.0000** | 0.0000 | **+0.8132** |
| 0.10 | 0.1009 | 0.0155 | 0.5320 | 0.0833 | +0.4311 |
| **0.25** | 0.0613 | 0.0322 | **0.3233** | 0.0967 | +0.2620 |
| 0.50 | 0.0364 | 0.0144 | 0.1767 | 0.0367 | +0.1403 |

Class recovery of exactly `1.0000` at zero noise is a **derivation** — the class *is* the
observation — and is labelled one. What is measured is what survives noise: at the release's own
rater noise the class is recovered **32.3%** of the time against the member's **6.1%**.

**Degeneracy is dissolved by the reframing. Noise is not.** The class still has to survive people
disagreeing, and it does five times more often than the member does.

## ⚠ A limitation of R229's band check, found on its first use

Both controls printed *"100% of band"*. For class recovery that is correct — the ceiling is 1.0 and
the observation reaches it. For **member** recovery it is **circular**: I had no independent ceiling,
so I passed `observed + 1e-9` as the ceiling and the check duly reported the observation filling its
own band.

> **The band check validates a threshold against a band. It cannot validate that the ceiling was
> *computed* rather than *assumed*.** That is the next layer, and supplying the observation as its
> own ceiling defeats the tool exactly the way R229 was built to prevent.

The correct ceiling here is `E[1/|ties|]`, which R228 measured at **0.1951** for k=2 — close to the
0.1868 observed, so the conclusion is unaffected. The defect is in the invocation, and it was caught
by reading, not by the checker.

## The formulation, in its current form

```
core = (Q, class, representative, certificate)

  Q               the declared query family
  class           [N]_Q  — IDENTIFIABLE by construction, and the measured object
  representative  the printed criteria — a CHOICE, never identified
  certificate     says which is which, and at what noise the class survives
```

Under this, R228's finding inverts from an indictment into a specification: **every core is a choice
of representative.** An honest artifact declares the class it stands for, admits it printed one
member, and reports the rate at which the class survives rater disagreement.

## The sentence that can no longer be written

*"The core is unidentifiable on this release."* The **class** is identifiable at 3.70 bits against
6.23 available. What is unidentifiable is which four sentences you print — and no definition ever
asked for those.
