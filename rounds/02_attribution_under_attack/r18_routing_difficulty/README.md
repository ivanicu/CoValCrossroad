# r18_routing_difficulty

**Decomposes r17's 84.6% router accuracy, which I flagged as probably free.**

r17 routed raters by their behaviour on other prompts and reported the learned
router matching the oracle on 84.6% of blocs. The bloc axis carries only 0.541% of
the singular mass, so that number was suspicious on its face: if most core items
are not contested, both blocs' direction maps agree and matching costs nothing.

Routing only ever matters on a **contested item** — one where the two blocs would
sign it differently. So measure there, per rater, against the only ground truth
available: the rater's own sign on that item.

    chance = 50%. If the learned router sits at chance on contested items, then
    r17's headline routing accuracy was entirely an artifact of agreement.
