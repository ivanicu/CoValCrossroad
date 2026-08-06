# R829 · is the constant-control class wider than the rule that found it?

**The decision this made safe:** whether to build the differential detector R828's NEXT called for.
**No — not on the strength of any known instance.** The registered forms yield **0 of 947 modules**,
and the one candidate wider class is UNVERIFIED.

Design in `PREREGISTRATION.txt`, committed before `run.py` existed. `run.py` committed before it ran.

## Why this round replaced the one R828 named

P4 stopped the differential detector twice:

1. **The technique already exists here.** `assurance/attack_every_check.py` plants the defect each
   check hunts and requires it to FIRE. Its population is the **assurance suite**; mine would be the
   **rounds**. The gap is real; **the method is not new**.
2. **Its own history prices the build.** Its v1 reported 3 of 6 checks as never firing and **all three
   were bad plants** — a 50% false-accusation rate, fixed only by making every plant self-validate
   and every check declare its contract.

So: does the target population exist at all? A differential detector earns its cost only against
constancy that is **semantic** rather than syntactic.

## Result

| | |
|---|---|
| **estimand — F1 alias · F2 strict self-cmp · F3 type-bounded** | **0** |
| population | **947 modules**, `corebench` + `assurance` + `E01…E05` |
| positive controls (one plant per form) | **3 of 3 flagged, form named** |
| g=0 (clean source) · negative (two different producers) | **not flagged · not flagged** |
| two-seed | byte-identical `e85a54dfdb2803b9e25c1d77f6b0a698` |

**W-SATURATED** — the `a OP a` rule already saturates this corpus at the sound syntactic forms.

⛔ **The first run returned UNVERIFIED and withheld the count**, because F1's positive control MISSED.
The bug was mine: `_aliases` conflated *assigned from a non-Name* with *rebound*, so in the plant
`b = compute(); a = b` the alias was discarded. **Stability is how many times a name is bound, never
what it is bound to.** The conditional kill did exactly its job — no count was published while the
instrument was blind.

## The near-miss, which is the round's real content

Pricing the 67 `x == x` hits the pre-registration **excluded** as NaN-conditional, I split them by
whether each side **INVOKES** a producer or **READS** a stored value:

- **23 INVOKES** — `run(set()) == run(set())`, `count_R697(set()) == count_R697(set())`. The producer
  is called twice. **This is the correct determinism idiom — precisely what R828 had to hand-build
  for R332, R672 and R731. It was already on disk 23 times.**
- **44 READS** — I immediately classed these as defects. **Three read at random were all legitimate
  NaN guards**, and `R777:211` carries the comment `# NaN: undefined, as registered`.

A weaker proxy — *no NaN/finite word within ±2 lines* — flags 27 of the 44. **It has a named
witness**: `R247:214` is `(sc == sc).all(-1).mean()`, an elementwise array NaN check with no NaN word
nearby. Proxy satisfied, property violated ⇒ **unsound in the direction of accusation.**

**So the 44 stay excluded and UNVERIFIED, exactly as pre-registered.**

⭐ **The pre-registration did work no reasoning in the moment could do.** It said counting these
*"would be unsound in exactly the direction that manufactures a false accusation."* Twenty minutes
later, holding 67 hits, I built an axis that re-admitted 44 of them — and a three-line sample showed
the original exclusion was right.

## NEXT

The differential detector is **not justified by a known instance** and is not built. What is
established instead: `f() == f()` — invoking the producer twice — is the idiom that turns a placebo
into a test, and **23 rounds already use it while 6 did not**. The next step is to check whether
those 6 are the same 6, because a defect that co-occurs with a missing idiom is a habit, not an
accident.
