# Claim card — is the satisfaction judge partly a string matcher?

Written before any code, per the binding process rule.

---

## Claim

Every cross-rater result in this repository runs through one instrument: the judge that answers
*"does response r satisfy criterion c?"*. r04 validated it against held-out human rankings in
aggregate. Nothing has asked **what it is using**.

r50 gives a specific reason to ask. It found that criteria whose words overlap the four
candidates carry more of the cross-rater direction than generic ones (+0.0271 among write-ins).
The values reading is that concrete, response-relevant criteria are more discriminating. The
instrument reading is that **the judge scores lexical overlap**, so overlapping criteria are the
ones it gets right — and the effect is a fact about `J`, not about `R` or `P`.

**Claim to test:** within a fixed (prompt, criterion), the judge's satisfaction score across the
four responses tracks lexical overlap between the criterion and each response.

## Estimand

For each (prompt p, criterion c), across that prompt's four responses:

```
ρ_pc = corr( s(c, r) ,  overlap(c, r) )        r = 1..4
```

reported as the **mean signed ρ**, whose null is 0 by symmetry. Magnitude is **not** the headline:
at n = 4 two independent vectors give E|r| ≈ 0.50, and quoting a bare |r| here is the error of
entry 49.

## Is the target observed?

**Yes, exactly, and that is unusual for this project.** Satisfaction scores, criterion text and
response text are all in hand. The question "does this instrument's output move with lexical
overlap?" is fully answerable — no proxy, no human data required.

What remains unobserved is whether overlap-driven scoring is *wrong*. A response that satisfies
"cite specific statutes" will genuinely contain statute words. **Lexical overlap and true
satisfaction are correlated in the world**, so a positive ρ is not by itself a defect — it is a
defect only if it exceeds what genuine satisfaction would produce, and this round cannot
establish that ceiling.

## Alternative worlds

| world | prediction |
|---|---|
| **judge is a string matcher** | ρ large and positive; and it should be *larger* for criteria whose satisfaction is hard to evaluate semantically |
| **overlap tracks real satisfaction** | ρ positive but comparable to what a human-scored ceiling would give — unobservable here, so this world is not confirmable |
| **judge is overlap-blind** | ρ ≈ 0 |
| **negation trap** | ρ *negative* for criteria phrased as prohibitions ("must not mention X"), because a violating response contains X. A pooled positive ρ would then be hiding two opposite mechanisms |

Row 4 is why criteria are split by polarity of their **human mean rating** before ρ is pooled.

## Intervention

None. Descriptive, on artifacts already computed.

## Null / positive control

- **Null:** permute responses within prompt, breaking the (criterion, response) pairing while
  preserving both marginals. Mean signed ρ must go to ≈ 0.
- **Positive control:** a synthetic criterion built by copying tokens out of one specific response
  must produce a strongly positive ρ. If the measurement cannot detect overlap-driven scoring when
  it is manufactured, a null on the real criteria is silence.

---

## Five mandatory checks

**1. Can this instrument return the opposite answer?** Yes: ρ ≈ 0 would say the judge ignores
surface overlap, which would strengthen r50's values reading rather than undercut it.

**2. Does it observe the target?** It observes the judge exactly. It does **not** observe whether
overlap-driven scoring is erroneous — that needs a satisfaction ground truth the release lacks.

**3. By what path can construction data reach evaluation?** None: overlap is computed from text
only, satisfaction was computed before this round existed, and no ranking enters.

**4. What other world produces this?** **Length** — a longer response contains more tokens and so
overlaps more with everything, and longer responses may genuinely satisfy more criteria. Overlap
is therefore reported both raw and normalised by response length, and ρ is recomputed with
response length partialled out within prompt.

**5. Which decision changes?** If ρ is large, r50's anchoring result is reinterpreted as an
instrument property and the anchoring axis is dropped as evidence about participants. It would
also put a scope note on **every** round that uses the satisfaction layer — which is nearly all of
them.

---

## Stopping rule

CPU only. Ends when ρ has its null, its positive control, its polarity split and its
length-controlled version. If the positive control fails, nothing is reported.
