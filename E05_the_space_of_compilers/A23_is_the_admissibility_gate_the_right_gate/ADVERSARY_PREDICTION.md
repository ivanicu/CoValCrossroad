# What I expect the adversary to overturn — written before it returns

**Dispatched 2026-08-03**, clean context, mandate to move claims DOWN, three-valued verdicts.
`frontier` §5: *"pre-register what you expect the adversary to overturn — when one finally runs, its
findings score your calibration about your own work, which is worth more than any individual
verdict."*

## The five I named to it, and what I actually believe about each

| # | claim | my prediction | why |
|---|---|---|---|
| a | claim 2's **36×** — my `+0.0068` against R235's `+0.2466` | **OVERTURNED** | different targets *and* different baseline formats. A ratio across two scales is a category error, and I wrote it as though it quantified a disagreement |
| b | claim 3's `+0.019 at R=14 against a seed spread of 0.06 — inside` | **UNVERIFIED** | no MDE. I never showed the design could have returned otherwise at R=14 |
| c | did the DEFINITION change today? | **it ended where it started** | R248 replaced the gate with `A_real`, R253 retracted it. The gate is `C(n,k) ≤ a(m)` again — what R228 used. I expect this stated bluntly and I expect it to be right |
| d | claim 4's **47×** between regimes | **UNVERIFIED** | a ratio of two effects where the denominator (`+0.0118`) is itself inside its own seed spread (`0.0296`). A ratio whose denominator is noise is not a magnitude |
| e | a claim contradicted by its own round's controls | **claim 1** | "class recovery 1.0000 at zero noise" is labelled an identity, which I think holds — but R230's 13-of-72 is quoted in claim 1 *and* was the seed of the retracted gate |

## What I expect it to find that I did NOT name

Nothing specific — and that is the honest answer rather than a hedge. If it returns only the five
above, the dispatch bought calibration and no information, which is itself a result about how much
self-attack is worth here. **If it finds a sixth, that is the measurement.**

## The scoring rule, fixed now

- it overturns something on this list → my self-attack reaches that far
- it overturns something NOT on this list → **the gap between what I can see about my own work and
  what a clean context sees, measured in claims**
- it confirms something I predicted OVERTURNED → I am over-retracting, which this session has done
  at least once already (R251's verdict was right about the number and wrong about the word)

---

# SCORED, 2026-08-03 — the adversary returned

## My five, against its verdicts

| # | my prediction | its verdict | scored |
|---|---|---|---|
| a | claim 2's 36× → OVERTURNED | **OVERTURNED** | ✅ **verdict right, mechanism wrong.** I said "different targets and baseline formats." It is **different SCALES**: `+0.0068` is a mean pairwise agreement on `[0,1]`; `+0.2466` is Kendall τ_b on `[−1,+1]`. Zero sign-ties, so `τ = 2·frac − 1` holds *identically* — R243's core τ is 0.6643 against R235's 0.663. **On one scale the ratio is 18×, not 36×.** |
| b | claim 3 → UNVERIFIED, no MDE | **UNVERIFIED** | ✅ right, and for my reason: effect/floor = 0.32, below the repo's own 1.5 rule |
| c | "the definition ended where it started" | **wrong, and blunter** | ❌ **it ended two steps behind.** The gate is now `C(n,k) ≤ a(m)` = `log₂ 75 = 6.23` — *the exact number claim 5 measures at `[1.02, 3.45]` and still calls wrong.* Un-retracting `A_real` reverted `H_eff` too, and only `A_real` was retracted |
| d | claim 4's 47× → UNVERIFIED | **UNVERIFIED** | ✅ right, plus one I missed: R227 sweeps observable **richness**, never **independence** — the headline word has no experiment behind it |
| e | claim 1 holds | **CONFIRMED** | ✅ right |

**4 of 5 verdicts correct; the one I got wrong I got wrong in the flattering direction.**

## What it found that I did not — and this is the measurement

**Six, and the pattern in them is one thing:**

1. **`DEF` OVERTURNED — the definition contradicts its own claim 5.** The gate installs `a(m) = 75`
   ⇒ 6.23 bits, which claim 5 (still `MEASURED`, never retracted) says is wrong by 2–6×.
2. **Claim 8 OVERTURNED at `FORMULATION.md:191`** — I fixed the *heading* in `fc2c5c4` and left the
   consequence paragraph three lines below reading *"only the second number predicts whether a core
   is recoverable."* **A fix that landed on one path of two.**
3. **R257's own results file already prints `OVERTURNED` on Q1** — under the flip the core goes from
   *at* its floor (0.4040 / 0.3870) to *below* it (0.3160 / 0.3722) — **and `grep -n "R257"
   FORMULATION.md` returns nothing.**
4. **Claim 6 UNVERIFIED** — R239 checks independence by *exact token-set identity*, and **my own
   R255** measured that half of co-prompt pairs share no content word and still agree. Lexical
   distinctness ⇏ observational independence.
5. **Claim 5's status line is stale** — "superseded by claim 8", whose gate role R253 retracted.
6. **The `0.3836 [0.3657, 0.4019]` min/max bracket is still quoted at two lines** — the exact form
   my own *"sentences that can no longer be written"* list forbids, in the same document.

**Plus a defect I had no category for**: R243's floor is seeded with `abs(hash((p, d)))` on a
**string** prompt id, so under `PYTHONHASHSEED=1/2/3/unset` the delta is `+0.0084 / +0.0090 /
+0.0083 / +0.0098` — **the published `+0.0068` is below all four**, the extreme that maximises the
ratio. And `RETRACTIONS.md` declared this class *"real but rare: 2 instances in 83 rounds"* — **the
sweep never covered E05.**

## The finding about my own process, which is what the dispatch bought

**Five of the six are PROPAGATION failures, not measurement failures.** R255, R257 and R259 each
produced a result that never reached the claim it bears on; two more are fixes that landed on one
path of two. **I can measure my own work. I cannot reliably carry the measurement back into the
document that states it** — and every one of those gaps is invisible from inside, because the
round that found it reads as finished.

The prediction said: *"If it finds a sixth, that sixth IS the measurement."* It found six, and they
share a mechanism.
