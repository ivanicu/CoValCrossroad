# Claim card — intervene on lexical overlap and watch the judge

Written before any code. This round exists because r51 declared itself undercontrolled, in its
own output, and named the control it lacked.

---

## Claim

r51 found the judge's satisfaction correlates with criterion↔response lexical overlap at
**+0.2068** (null −0.0034, +0.1886 length-controlled). Correlational: overlap and genuine
satisfaction covary in the world, so the number does not separate *"the judge reads overlap"*
from *"overlapping criteria are genuinely the satisfied ones"*.

**Claim to test, causally:** appending distinctive tokens taken from response **A** to a criterion
raises that criterion's satisfaction score on **A** relative to **B**, compared with appending
tokens taken from **B**.

## Estimand

For a prompt with criterion `c` and two responses `A`, `B`:

```
c_A = c + tokens distinctive to A
c_B = c + tokens distinctive to B

Δ = [ s(c_A,A) − s(c_A,B) ] − [ s(c_B,A) − s(c_B,B) ]
```

`Δ > 0` means the judge moved toward whichever response donated the tokens. **The appendage is the
same kind of object in both arms**, so whatever semantic effect appending a token list has cancels
in the difference. That symmetry is the whole design.

## Is the target observed?

**Yes — this is an intervention on the instrument, and the instrument is fully available.** Unlike
every human-facing question in this project, nothing here needs a counterfactual the release
lacks: I can build `c_A`, build `c_B`, and read both scores.

What is *not* observed is whether the appended tokens change what `c` genuinely asks. A token list
glued to a criterion is not a natural criterion, and a large Δ shows the judge is overlap-sensitive
**on perturbed text**, which bounds but does not equal its behaviour on natural criteria.

## Alternative worlds

| world | prediction |
|---|---|
| **judge reads overlap** | Δ > 0, and larger for rarer donated tokens |
| **judge reads meaning only** | Δ ≈ 0 — the appendage is uninformative either way |
| **appendage is read as a requirement** | both arms drop in absolute score, but Δ still ≈ 0, since the requirement is symmetric |
| **judge is confused by malformed text** | scores drift toward 0.5 in both arms; Δ ≈ 0 with inflated variance |

Worlds 3 and 4 both predict Δ ≈ 0, so a **null** here is ambiguous between "meaning-only" and
"the perturbation broke the instrument". Absolute score shift and score variance are therefore
reported alongside Δ, to tell those apart.

## Intervention

**Yes, and it is the point.** This is the only genuinely interventional round in the project —
everything else is observational on a fixed release.

## Null / positive control

- **Null:** append tokens drawn from an **unrelated prompt's** response. Those are distinctive to
  neither A nor B, so Δ must be ≈ 0. This is the design's own falsifier: if a random appendage
  produces the same Δ, the effect is the act of appending, not the source of the tokens.
- **Sanity:** the un-appended criterion's `s(c,A) − s(c,B)` is recorded so the baseline gap is
  visible and Δ is not read against an unstated zero.

---

## Five mandatory checks

**1. Can this instrument return the opposite answer?** Yes: Δ ≈ 0 is fully possible and would
undercut the instrument reading of r51 and r50.

**2. Does it observe the target?** It observes the judge under intervention exactly. It does not
observe behaviour on *natural* high-overlap criteria — that is the bound, stated wherever Δ is.

**3. By what path can construction data reach evaluation?** None. No ratings, no rankings, no
human data enters. Tokens come from response text only.

**4. What other world produces this?** **Token rarity** — distinctive tokens are rare, and a judge
might react to rarity rather than to matching. Partly addressed by the unrelated-prompt null,
whose tokens are equally rare but match neither response.

**5. Which decision changes?** A positive Δ makes the instrument reading of r50's anchoring effect
concrete rather than hypothetical, and puts a measured scope note on the satisfaction layer that
nearly every round in this repository inherits. A null leaves r51's +0.21 as a correlation with no
demonstrated mechanism.

---

## Stopping rule

One GPU pass: 250 prompts × 1 criterion × 3 arms (A-donated, B-donated, unrelated) × 2 responses,
plus the un-appended baseline. No sweeps. Ends when Δ has its null and the absolute-shift
diagnostic. If the unrelated-token null produces the same Δ, the round reports that and nothing
else.
