"""cluster -- the conversation-clustered estimator, written ONCE because it broke three times.

⛔ WHY THIS FILE EXISTS. The same estimator shape recurs in every arm comparison in R427, and I got
   it wrong three times in one session:

     1. `position.py`      -- a conversation-clustered observed rate compared against a FLAT mean of
                              1/n. Two weightings compared as one object.
     2. `arm_agreement.py` -- the identical defect, written again VERBATIM twenty minutes later.
     3. `arm_agreement.py` -- pooled with `{kk: v for n in S for kk, v in S[n].items()}`, where a
                              conversation appearing in SEVERAL strata OVERWRITES ITSELF and its
                              other strata are silently discarded.

   The campaign's own rule is that the same bug three times is an infrastructure problem, not a third
   patch. This is the infrastructure.

THE TWO INVARIANTS IT ENFORCES, which are what actually failed:
  ① EVERY quantity compared -- observed, expectation, null -- is aggregated by the SAME function over
     the SAME units. An expectation computed by a different weighting is a different object.
  ② Accumulating across strata APPENDS; it never assigns. A dict keyed on the conversation loses
     every stratum but the last, silently, and the loss looks like a smaller n rather than an error.
"""
from __future__ import annotations
import collections

import numpy as np

ZEFF = 1.959964 + 0.841621          # two-sided alpha .05 + power .80


class ByConv:
    """Accumulate per-conversation observations. APPENDS across strata -- never assigns."""

    def __init__(self):
        self._d = collections.defaultdict(lambda: collections.defaultdict(list))

    def add(self, conv, **quantities):
        """One interaction's worth of every quantity at once, so they cannot drift apart."""
        for name, value in quantities.items():
            self._d[conv][name].append(float(value))
        return self

    def names(self):
        return sorted({n for v in self._d.values() for n in v})

    def mean(self, name):
        """-> (mean, MDE, n_conv) over conversations. None if fewer than 2 conversations carry it."""
        a = np.array([np.mean(v[name]) for v in self._d.values() if v.get(name)], float)
        if len(a) < 2:
            return None
        return float(a.mean()), float(ZEFF * a.std(ddof=1) / np.sqrt(len(a))), len(a)

    def paired(self, x, y):
        """-> (mean difference, MDE, n_conv). Same units, same weighting, both sides."""
        ks = [k for k, v in self._d.items() if v.get(x) and v.get(y)]
        d = np.array([np.mean(self._d[k][x]) - np.mean(self._d[k][y]) for k in ks], float)
        if len(d) < 2:
            return None
        return float(d.mean()), float(ZEFF * d.std(ddof=1) / np.sqrt(len(d))), len(d)

    def n_conv(self):
        return len(self._d)

    def n_obs(self, name):
        return sum(len(v.get(name, ())) for v in self._d.values())
