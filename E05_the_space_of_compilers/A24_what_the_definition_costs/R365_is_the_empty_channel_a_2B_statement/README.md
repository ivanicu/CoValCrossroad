# R365 — the empty channel is not a 2B statement: the first claim here to survive a change of judge

**The decision this makes safe:** *does R364's null need a judge index, like everything else in this
definition?* **No.** The dose is flat at both judges, and the second judge's design could have seen
what the first excluded.

## Result — `W_BOTH_EMPTY`. All controls PASS **at both judges**. Two runs byte-identical.

This is R364's design with **one input changed**. The same function computes both judges, so a
difference would be a difference in the data and not in the code.

| judge | LEVEL `margin(d=0)` | | DELTA `margin(1) − margin(0)` | seeds | |
|---|---:|---|---:|---|---|
| **2B** | **+0.0139** vs MDE 0.0117 | resolved | **−0.0000** vs MDE **0.0096** | +0.0035 / +0.0001 / −0.0036 | inside |
| **0.8B** | −0.0126 vs MDE 0.0145 | **UNRESOLVED** | **+0.0000** vs MDE **0.0107** | +0.0080 / −0.0026 / −0.0053 | inside |

**0.8B's MDE is 1.11× 2B's** — so it *could* have excluded a channel the size 2B excluded. That is
what separates this from silence, and it is why the kill carried a third branch.

## The third branch, pre-registered because the level is null there

R362 measured `topw_k4`'s margin at 0.8B as **−0.0102 vs MDE 0.0134 — unresolved**. So at that judge
the level this channel would be a fraction *of* is itself null. A flat dose there **could** have been
uninformative rather than confirming, and the kill was written to say so:

> `elif mde_08B > 1.5 × mde_2B → W-UNINFORMATIVE` — *silence, not agreement.*

It came in at **1.11×**, so the branch did not fire. **Had the second instrument been much wider, this
round would have reported silence rather than a replication** — and that distinction was fixed before
the numbers existed.

## Controls, at each judge

| | 2B | 0.8B |
|---|---|---|
| **SHAM** — permute which annotator's scores carry which id | −0.0021 vs 0.0101, **inside** | −0.0016 vs 0.0105, **inside** |
| **POSITIVE** — planted person-specific channel | g=0 −0.0000/0.0096 **undetected** · g=2 **+0.0547** detected | g=0 +0.0000/0.0107 **undetected** · g=2 **+0.0727** detected |
| **SPLIT** — a dose that does not move never ran | 0.000 → 1.000 | 0.000 → 1.000 |
| reproducibility | two runs **byte-identical** (`6cef240c76e7`) | |

**The positive control is the one that makes this readable.** A null at a judge whose design was
never shown able to see a planted channel is silence — and here the plant is detected at *both*.

## What it earns, stated at the size the design supports

⭐ **`The rubric channel carries nothing` is not a 2B statement.** After a session in which a change
of judge emptied clause ②, inverted one arm family's ordering, destroyed the size band's premise and
cost clause ③ its irreplaceability, **this is the first claim in the definition to come through
unchanged.**

Two caveats, both in the run's own output rather than added afterwards:

- ⚠ **Two judges can refute instrument-independence and never establish it.** The claim earned is
  **"not refuted at a second judge"**, and that is what the definition will say.
- ⚠ **At 0.8B the level is unresolved** (−0.0126 vs 0.0145). This is a flat dose on a **null level**,
  which licenses less than the same flatness at 2B where the level is resolved.

## Register

| criterion | status |
|---|---|
| **a third judge** | **NOT-ATTEMPTED-AND-NOT-CHEAP** (R357) — no third checkpoint on the local store |
| **establishing instrument-independence** | **N/A** — two points can only refute |
| **a channel below either MDE** | **N/A** — needs more prompts or a lower-variance contrast |
| **cross-release** | **N/A** — one release |

## The sentence I can no longer write

> *"the channel is empty — but that is a 2B statement, like everything else here."*

**It is flat at both judges, and the second judge's design was wide enough by only 1.11× to say so.**

Artifact: `results/r365_channel_second_judge.json`, source-stamped.
