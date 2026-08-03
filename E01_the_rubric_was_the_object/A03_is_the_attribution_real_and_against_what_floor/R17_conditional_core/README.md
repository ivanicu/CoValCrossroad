# R17_conditional_core

**Does conditional encoding rescue conflict-aware aggregation — when the routing
has to be earned rather than assumed?**

r16 scored every rule by its worst-off bloc and conflict-aware came last, below
random selection. But that metric forces one direction per core item, and a
genuinely conflict-aware output would not commit.

The trap: let each bloc apply its own preferred direction and satisfaction rises
mechanically. That check cannot fail.

## The first design was infeasible, and why that is itself a result

The obvious fix routes a rater using some of the prompt's criteria and scores them
on the rest. **CoVal cannot support it.** Every prompt shows the same six seed
criteria, so the shared-criterion budget is hard-capped: 731 prompts have exactly
6, 197 have 5, 33 have 4, and **none has 10**. A k=4 core already consumes four of
the six. There is no room left for a routing set.

    no held-out design at the CRITERION level is possible on this release

Raters are the plentiful axis instead: median 17 per prompt, and each person rated
5-20 prompts.

## The design that survives

Route each rater by their behaviour on **other prompts** — the cross-prompt
structure r01 established (rho=0.147 style-controlled, z=+16.6) — and never by the
prompt being scored. This is also the deployment situation: you know a user from
their history and must decide how to serve them on something new.

  SINGLE   one direction for everyone (what r16 measured)
  LEARNED  per-bloc directions, raters routed from their OTHER prompts only
  ORACLE   each bloc handed whichever direction map suits it, an unreachable
           ceiling reported so LEARNED can be read against it
