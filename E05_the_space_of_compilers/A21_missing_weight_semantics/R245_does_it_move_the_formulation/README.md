# R245 — R244 tested one round and claimed ten; this tests the load-bearing three

**Arc E05·A12.** R244's commit said the undeclared missing-weight choice *"sits under ten rounds"*
having measured **one**. That sentence is wider than its evidence — the exact overreach `realstat`
G1 exists for, committed while writing up a round about that overreach.

## The three claims the formulation actually rests on, under both readings

| reading | class recovery | member recovery | classes (median) | `k_max` |
|---|---|---|---:|---:|
| **exclude missing** | 0.2993 (spread 0.0767) | 0.0532 (spread 0.0109) | 13 | **2** |
| **missing = 0** | 0.2980 (spread 0.0600) | 0.0525 (spread 0.0285) | 12 | **2** |

**Controls:** the exclude arm reproduces R230 (0.3233 / 0.0613) and R228's `k_max = 2`. **Negative
control, measured rather than assumed:** only **2 of 300** prompts are fully rated, so the two
readings are identical by construction on 0.7% of the population — **any difference has to come from
the partially-rated majority, and that is why the near-zero movement below is informative.**

## The result, and it is the opposite of R244's

**Class recovery moves by `0.0013` against a seed spread of `0.0767`. `k_max` does not move at all.
Both conclusions survive.**

R244 found the same choice worth **`0.1040`** on R231's quantity against a spread of `0.0127`. **Both
are correct, and the contrast is the finding:**

> The reading matters enormously where the comparison is **official core vs random floor** — two
> objects weighted differently — and **not at all** where it is **planted recovery**, because there
> the same `W` builds both the target and every candidate, so a global reweighting largely cancels.

**So R244's "ten rounds" was right about the exposure and wrong about the consequence.** Corrected
here rather than left standing: the choice is a **scope line** the formulation must carry, not a
threat to claims 1 or 6.

## The bug this round's positive control caught in one run

`k_max` came back **11**. `C(n,k)` is unimodal, so `k` near `n` satisfies `C(n,k) ≤ 75` again —
`C(11,10) = 11` — and a plain `max()` returns the upper tail. **R228 already carries a `contig`
variable for exactly this**, with its own comment that *"a core of size k>n/2 is not a compression
and reporting the upper tail as identifiable would be a technicality."*

**I reimplemented a function that existed two arcs away and reintroduced the bug it had already
fixed.** The lesson is not the arithmetic — it is that the positive control was pinned to a *prior
round's published number*, and that is what made a fresh reimplementation visibly wrong within one
run.

## The sentence that can no longer be written

*"The missing-weight reading undermines E05's claims."* It moves the official-core comparison by
0.1040 and the formulation's load-bearing claims by 0.0013. **Exposure is not consequence, and R244
conflated them.**
