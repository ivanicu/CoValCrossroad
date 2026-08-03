#!/usr/bin/env python3
"""SPECIFICATION AXIS NOT SWEPT IN run.py: the human-target accuracy is pooled
over PAIRS, so a prompt with 46 assessments counts more than one with 8.  The
defensible alternative is prompt-weighted (unweighted mean of per-prompt
accuracies).  If the two disagree, the estimand was never 'the accuracy' -- it
was 'the accuracy of whichever unit I happened to pool over'."""
import json
from pathlib import Path
import numpy as np
import run as R

rng = np.random.default_rng(11)
joined, _ = R.load_join()
bundles, _ = R.build(joined, R.load_sat("full"), R.load_sat("core"))
C_ = R.cache(bundles, "z", "mean")
out = {}
for rk in ("world", "personal"):
    tot, cnt = [], []
    for pid in sorted(bundles):
        b = bundles[pid]
        pairs = R.human_pairs(b, rk)
        if not pairs:
            continue
        Zf, Zc, w = C_[pid]
        comps = R.compile_scores(pid, b, Zf, Zc, w, 11)
        row = []
        for nm in R.LADDER:
            s = comps[nm]
            row.append(sum(1.0 if s[i]-s[j] > 1e-12 else (0.5 if abs(s[i]-s[j]) <= 1e-12 else 0.0)
                           for _a, i, j in pairs))
        tot.append(row); cnt.append(len(pairs))
    T = np.array(tot); c = np.array(cnt, float)
    pooled = T.sum(0) / c.sum()
    perprompt = (T / c[:, None]).mean(0)
    ci = R.LADDER.index("core")
    out[rk] = {nm: dict(pair_weighted=float(pooled[k]), prompt_weighted=float(perprompt[k]),
                        d_vs_core_pair=float(pooled[k]-pooled[ci]),
                        d_vs_core_prompt=float(perprompt[k]-perprompt[ci]))
               for k, nm in enumerate(R.LADDER)}
    out[rk]["_n_prompts"] = int(len(c))
    out[rk]["_sign_agreement"] = float(np.mean([
        np.sign(pooled[k]-pooled[ci]) == np.sign(perprompt[k]-perprompt[ci])
        for k in range(len(R.LADDER)) if k != ci]))
print(json.dumps(out, indent=1))
Path("results/weighting_check.json").write_text(json.dumps(out, indent=1, default=float))
