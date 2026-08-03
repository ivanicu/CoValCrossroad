'''Template for a new round. Copy the docstring; do not copy the prose.

WHY THIS EXISTS, AND WHY IT IS NOT A FIX FOR THE THING THAT PROMPTED IT
    R242 audited E05's 23 rounds against realstat §5 behaviourally and found SEEDS declared 0/23
    while EVIDENCED 10/23 -- ten rounds sweep >=3 seeds and none wrote the header. SPECIFICATION
    declared 2/23, PLACEBO 5/23.

    The tempting repair is to go back and add the headers. That would raise the declared column to
    match the behaviour and change nothing about the work -- teaching to my own test, and R242's
    whole point is that the two columns diverge. So the 23 rounds are LEFT AS THEY ARE and this
    template exists so the gap closes FORWARD, in rounds not yet written, by making the checklist
    the first thing present rather than the thing remembered.

    ⚠ A template cannot make a control good. R238 declared and implemented a positive control that
    predicted nothing, and R242 scored it compliant. Filling every field below is necessary and
    nowhere near sufficient.
'''

TEMPLATE = '''"""RNNN -- one sentence: the belief this round can change.

ESTIMAND        the quantity, named BEFORE the method
IDENTIFICATION  can it be estimated here at all? if partial -> BOUNDS, not a point
SCOPE           population · instrument · baseline · regime -- eleven of twelve retractions in
                this programme were a correct number reported without the scope it held over
WORLDS          >=2, differing ONTOLOGICALLY, with a prediction matrix
KILL            pre-registered, with its threshold, written before the run. A CONDITIONAL, not a
                bare number: binding only if the controls behaved
POSITIVE CTRL   planted effect · retention · MDE · fails at g=0 · and its CEILING COMPUTED, not
                assumed -- covalx.control_band.check(name, floor, ceiling, threshold). The ceiling
                is 1.0 only where the answer is unique; with ties or saturation it is lower
NEGATIVE CTRL   what structure it destroys · what world it excludes · built synthetically
SHAM            the same operation minus the ingredient, size- and compute-matched
PLACEBO         a contrast that must return exactly zero
NOISE FLOOR     MEASURED by replicates, never modelled
MULTIPLICITY    correction over the WHOLE grid · cells tested beside cells surviving
SPECIFICATION   the axes swept, and the cells that KILL the finding
SEEDS           >=3, and verify the seed flag actually changed the draws
ARTIFACT        persist the TENSOR before any summary -- what a LATER round needs to ATTACK this.
                R233 spent 33,320 GPU judgements and wrote 620 bytes
REPRODUCIBILITY two hash seeds byte-identical
IMPOSSIBLE      what this site cannot meet, each with what it WOULD REQUIRE. Never "planned".
                And check it with an `ls` BEFORE writing it -- RETRACTIONS entry 96 is an
                impossibility asserted four times while the counter-artifact sat in this repo
"""
'''

if __name__ == "__main__":
    print(TEMPLATE)
