# R19_floor_choice

**The attribution number depends on which donor defines the floor, and I reported
one arbitrary point inside that range as if it were the number.**

r04's headline decomposition subtracts a shuffled-rubric arm to isolate "generic
response quality any rubric earns for free". The shuffled arm used a RANDOM other
prompt. r10 also graded a NEAREST-topic donor and a FARTHEST donor, but reported
them as a robustness check rather than reading them as what they are: a decay curve
in topical distance.

Read that way, a random donor retains 47-60% of the self signal. It is not a clean
generic floor -- a randomly chosen prompt sometimes shares topic.

    attribution vs near   0.0467   strictest floor
    attribution vs random 0.0638   what was reported
    attribution vs far    0.1020   loosest floor
    span                  2.18x

Translated to the headline, the prompt-specific share of the above-chance signal
runs from about 29% to about 63%. The reported 43% sits inside that, but was stated
as a measurement rather than as one choice of floor.

Neither endpoint is obviously right. FAR is adversarially selected -- the judge may
simply refuse everything, which understates the floor rather than measuring it.
NEAR shares topic, which overstates it. The generic floor is bracketed, not
measured.

The 0.8B cell is excluded from any reading: its self accuracy is 0.5405, barely
above chance, so its decomposition is noise.

Pure re-analysis of r10's stored numbers. No new compute.
