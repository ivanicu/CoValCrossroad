# R340 — the definition survives its first deliberate adversary

**Decision this makes safe:** whether the definition admits objects built to *satisfy* it rather
than to be cores. **At a 300-subset search budget, no label-free adversary gets in.** **W-ROBUST.**

## ⛔ The derivation came first, and it narrowed the attack surface before any compute

Clause ① is `arm − random_k4_s0`; clause ② is `arm − blind_k`. **Both baselines are fixed vectors the
arm cannot influence**, so both margins rise **iff the arm's own A2 rises**.

> **Neither clause is gameable without genuinely agreeing with the humans more.** That is algebra,
> not a finding — and it means the attack had to come through **clause ③**, which is exactly the
> clause R336–R338 bounded.

## The arms

| arm | A2 | ① eff/MDE | ② eff/MDE | admitted | label-free |
|---|---:|---:|---:|---|---|
| `adv_mimic` — imitate the **full rubric** | 0.5087 | 1.41 | **−3.42** | no | yes |
| `adv_decisive` — maximise verdict **confidence** | 0.5033 | 0.74 | **−3.04** | no | yes |
| `adv_antiblind` — maximise **disagreement with the blind reference** | **0.3601** | −7.05 | **−8.39** | no | yes |
| **ORACLE** *(positive control — reads labels)* | 0.6431 | 11.79 | 9.33 | **ADMITTED** | **NO** |
| random *(g=0)* | 0.4945 | 0.13 | −3.96 | no | yes |

*Reference: `topw_k4` (the campaign's best label-free arm) 0.5642 · random floor 0.4927.*

## The sharpest cell is `adv_antiblind`

**The objective aimed most directly at clause ②'s numerator produces the WORST arm on the page —
0.3601, far *below* chance.** Maximising disagreement with the blind reference means disagreeing with
the humans too. **The derivation, confirmed empirically rather than assumed.**

## The sham has a number now

`adv_mimic` is the same search with the target swapped from the human to the **rubric**. It lands at
**0.5087** — which is exactly R294's `full` arm's A2, as it should, since it is optimising toward the
full rubric's own verdict.

> **Aiming at the human rather than at the rubric is worth `+0.0555`.** R294's *"cores depart from the
> rubric to track the human"* now has a magnitude attached rather than only a direction.

## Controls

| control | result |
|---|---|
| **positive** — the ORACLE (the *one* objective that reads labels) must be admitted | **ADMITTED**, ① 11.79× ② 9.33× |
| **positive @ g=0** — same search, *random* objective | 0.4945 vs floor 0.4927, not admitted |
| **negative** — label-freeness asserted **mechanically** from each objective's own source | 3 adversaries `False`, ORACLE `True` |
| **placebo** — an arm against itself | 0.0 |

**The positive control is what makes the failures readable.** The search *can* find an admissible arm
at this budget when allowed to see the answer — so the three failures are **measurements, not
silence**. And the label-free claim is read off `inspect.getsource`, not asserted: the harness
demonstrably flags the one objective that does touch labels.

## ⚠ At this budget

**300 subsets per prompt.** A larger budget can only help the adversary, so **W-ROBUST is a statement
at this search size, not a proof.** Stated rather than hidden.

## Scope

968 CoVal prompts with ≥2 annotators · Qwen3.5-2B-Base under R234's canonical builder · baselines
exactly as R294 published them · k=4 · 5 arms × 2 clauses × 3 seeds.

## What this cannot do

Test an adversary with unbounded search, or one that attacks **clause ③** — the only surface the
derivation leaves open. R336–R338 bounded clause ③'s testability; an adversary aimed *there* would
need a leak mechanism the release does not carry.
