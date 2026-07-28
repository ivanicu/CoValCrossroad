# r20_paraphrase_transfer

**Is the own-prompt advantage content, or wording?**

r15 established that a prompt's own criteria beat the floor (+0.073) while criteria
from the most topically similar other prompt do not (+0.018). r14 established that
the judge is not paraphrase-invariant: a faithful rewording flips 15.4% of its
Yes/No verdicts.

Those two together admit a deflationary reading of everything in this repository:
the "prompt-specific advantage" could be lexical coupling. A criterion written for
prompt P shares P's exact vocabulary, and P's responses were generated from P, so
they share it too. A near-topic prompt shares the topic but not the wording.

The test writes itself. Paraphrase a prompt's own criteria — same demand, different
words — and re-grade its own responses against real human rankings.

  advantage survives paraphrase -> it is content; the transfer boundary is real
                                   specificity, not vocabulary overlap
  advantage collapses           -> the attribution measured throughout this
                                   repository is substantially lexical, and every
                                   headline needs restating in those terms

The fidelity filter from r14 is retained: a paraphrase that drifted in meaning would
make a collapse ambiguous between "the advantage was lexical" and "I changed the
criterion".
