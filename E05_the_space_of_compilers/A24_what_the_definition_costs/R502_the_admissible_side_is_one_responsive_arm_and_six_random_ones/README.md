# R502 · The ③-admissible side of clause ② is one responsive arm, six random draws and two fixed sets

**Decision this makes safe:** whether ②∧③'s `UNDETERMINED` verdict is about the *definition* or about
the *arm population*. **It is about the population**, and the population has one real candidate.

## The census

| ③-admissible, by composition | n | arms |
|---|---|---|
| **prompt-RESPONSIVE, full coverage** | **1** | `gen` |
| prompt-varying but random | 6 | `random_k{3,4,4,4,6,8}_s*` |
| prompt-blind (one fixed set) | 2 | `generic`, `genericpool16` |
| partial coverage | 3 | `promptecho` (398/968), `randblind_k4_s0` (1), `vacuous_k4` (1) |
| **③-EXCLUDED, prompt-varying** | **14** | the whole label-reading family |

**Controls.** Positive, two-sided and able to fail: `generic` must return **1** distinct criterion set
and `oracle_k4` must return **>1** — measured **1** and **968**. Specification: three equality rules
(exact / order-insensitive / case-normalised) — **the classification does not change.** Negative:
single-prompt arms are reported at coverage 1 rather than silently pooled.

## What it explains

R486/R487 downgraded *"② and ③ conflict"* to `UNDETERMINED` because the best admissible prompt-aware
arm sat at **p32.6 of 23** with **22 others at p0.0**. That read as *a weak field*. **It is not a
field at all** — it is **one candidate and a floor**. The 22 at p0.0 are random draws and fixed sets
doing exactly what they should.

⭐ **So the verdict's scope changes without its value changing.** `UNDETERMINED` was right, and the
reason is not that the definition is unresolvable — it is that **the site ships one ③-admissible
prompt-responsive arm.** That is a property of the release, and it names precisely what a second site
would have to supply: **more ③-admissible prompt-responsive generators.** No analysis here can make
one.

## ⛔ The wall that fell, and the probe that was blind

I was one command from recording *"arms cannot be classified as prompt-varying from these
artifacts"* — true of `sat_*.npz`, which carry only `(key, float)`. **It is false of the release:
`core_<arm>.json` holds the criterion TEXT for 92 arms, 968 prompts each. Fifth false wall this
session**, and like the other four it was asserted right after correctly checking something adjacent.

**And the first probe was blind in the now-familiar way:** it counted distinct criterion **index**
sets, but every k=4 arm uses `{0,1,2,3}` on every prompt, so it returned **1** for `oracle_k4` — an
arm that re-optimises on every prompt. **Instrument's unit: index structure. Claim's unit: criterion
content.** Third occurrence this session. It was caught only because I happened to know one answer in
advance, **which is not a method** — hence the two-sided positive control now built into the round.

## ⛔ And a design killed before compute

The announced next step was cross-prompt transfer: *a per-prompt optimiser's criteria should transfer
worse.* **That comparison is the arithmetic trap.** A prompt-blind arm uses the same criteria
everywhere, so its transfer decrement is **identically zero by construction**, while any per-prompt
arm must decay. The statistic would have separated the families perfectly and meant nothing. **The
severe version compares only prompt-varying arms — and this census shows the admissible side has
exactly one, so the design is not viable here.** Named with what it requires, per §2.

## The bound on all of the above

**Prompt-RESPONSIVE vs merely prompt-VARYING is assigned from construction knowledge, not measured.**
Measuring it would need to permute prompts and check whether the emitted criteria follow — which
requires the generator, not its output. Every claim here inherits that bound.
