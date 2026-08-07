# R15_indistribution_transfer

**Does the advantage transfer to unseen responses that are still IN distribution?**

r12 tested transfer using responses generated locally by a 2B base model and judged
by a learned gold head. Both arms landed near chance, and one explanation survives
r13: the fresh responses were out of distribution for gold, so nothing could rank
them and no rubric could look good.

This removes both weaknesses at once. For each prompt P, take its nearest-topic
neighbour Q and score **Q's four released responses**:

- Q's own rubric   — criteria authored by people who read exactly these responses
- P's rubric       — topically relevant, never written against these responses
- a random rubric  — the generic-quality floor

The responses are real released candidates, so they are in distribution by
construction, and they carry **real human rankings** — the gold model is not used at
all. The comparison P-vs-random is the transfer measurement r12 could not make
cleanly.

- P's rubric beats random on Q's responses -> transfer works; r12's failure was
  out-of-distribution generation, and the North Star shrinks to a footnote
- P's rubric ties random -> the bound is real even in distribution, and it is a
  property of rubric-graded evaluation rather than of my generator
