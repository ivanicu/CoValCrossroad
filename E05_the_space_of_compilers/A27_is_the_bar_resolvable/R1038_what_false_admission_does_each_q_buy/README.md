# R1038 — the family is its own null, so each q has a measurable **false-admission rate**

**The decision this round makes safe:** which q the definition declares by default. **q = 90** — the
only scale-free quantile whose false-admission rate reaches the operator's own nominal level.

## ⛔ The third route R1036 and R1037 both missed

Both closed saying the choice among q ∈ {50, 75, 90} runs through construct validity and **cannot be
measured on this release**. It can. **Every member of the comparator family is itself a scoreable
arm**, so the family is its **own reference population**: run the q-bar on family members and the
share that clears it is a **false-admission rate**, because *a checklist is not a core*.

This is **R1023's device** — which priced the coverage guard against an exact null — applied one
level up, to **the bar** rather than the loader.

## ⛔ Part of it is forced, and that part is not the finding

A member at rank *r* of *N* beats about *r/N* of the family **by construction**, so the rate **must**
fall in q. **The direction was guaranteed; the level was not.**

## Result — ⭐ **World A**

| q | false-admission rate | across-seed spread |
|---:|---:|---:|
| 0 | 1.0000 | 0.0000 |
| 50 | **0.2550** | 0.0000 |
| 75 | **0.1217** | 0.0050 |
| **90** | **0.0250** | 0.0000 |
| 95 | 0.0200 | 0.0000 |
| 99 | 0.0050 | 0.0000 |
| 100 | 0.0000 | 0.0000 |

**Among the three scale-free quantiles, only q = 90 reaches nominal.** q=50 and q=75 are decisively
above it — 0.255 and 0.122 against an SE of ±0.035 and ±0.023.

⚠ **The exact match of 0.0250 to the nominal 0.025 is arithmetic, not significance:** it is **5 of
200** members, and the binomial SE there is **±0.0110**. The claim the design supports is *"at nominal
within resolution"*, not *"exactly nominal"*.

## Controls

- **POSITIVE ①** — a **real** arm must clear the bar: `coval_core` is in R1036's committed q=90
  extension: **True**.
- **POSITIVE ②** — the rate must be able to reach 1: q=0 gives **1.0000**: **PASS**.
- **NEGATIVE** — the rate must **fall** as q rises, or the bar orders nothing: **PASS**.
- **PLACEBO** — a member cannot beat 100% of a family **containing it** (its own difference is exactly
  0, never > 0), so the q=100 rate must be **exactly 0**: **0.0000**: **PASS**.
- **NOISE FLOOR** — binomial SE at 200 members: ±0.0354 at p=0.5, ±0.0110 at p=0.025. No rate read
  finer.
- **SEEDS** — 3; worst across-seed spread **0.0050**.

## What this narrows, and what it does not

- ⭐ **R1037's "declared, not fixed" is narrowed to a DEFAULT of q = 90, with its cost stated.** q
  remains a declared parameter — the definition still names the curve — but the default is now
  selected **on evidence** rather than left to taste.
- ⚠ **A low rate would not make q RIGHT.** A bar can be strict and still measure the wrong thing.
  That is **construct validity**, needing the criterion vocabulary **R1028** showed this release does
  not carry. **N/A, stated not planned.**

`run.py` · `results/false_admission_by_q.json`
