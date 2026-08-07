"""A01 -- Is disagreement NOISE or STRUCTURE? The M1-vs-M2 separator.

The whole pluralistic-alignment programme forks here:

  M1 latent consensus / noisy measurement
      Disagreement is sampling noise around one shared target.  Two raters who
      agree on prompt A tell you NOTHING about whether they agree on prompt B.
      Prescription: collect more ratings; the target converges.

  M2 structured plurality
      Disagreement is a stable property of people.  Raters who agree on A tend
      to agree on B.  Prescription: a single core is the wrong object; you need
      group-conditional or steerable targets, and more data will not converge.

These make OPPOSITE predictions about one observable already in the release:
the cross-prompt persistence of pairwise rater agreement.

Estimator
---------
For every pair of raters (u,v) who co-rated >= 2 prompts, compute their
agreement on each shared prompt, then correlate agreement across disjoint
prompt pairs.  Persistence rho > 0 => structure.  rho = 0 => noise.

Controls that must run in the same pass (P0 gate 7):
  * label permutation null -- shuffle rater ids within each prompt; any
    persistence that survives is an artifact of prompt difficulty, not people.
  * prompt-difficulty control -- centre each prompt's agreements before
    correlating, so "some prompts are easy" cannot masquerade as "some people
    are alike".
  * split-half by disjoint prompt sets, so the same prompt never appears on
    both sides of the correlation.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(next(p for p in _pl.Path(__file__).resolve().parents if (p / "covalx").is_dir())))
from covalx.frozen import append_to as _freeze  # noqa: E402


import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = str(next(p for p in _HERE.parents if (p / "covalx").is_dir()))
_RES = str(_HERE / "results")


def load_rubric_matrices(path: Path):
    """Per prompt: rater ids and their signed scores on commonly-rated items."""
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        rec = json.loads(line)
        items = rec.get("coval_full") or []
        raters = set()
        for it in items:
            for s in it.get("scores") or []:
                raters.add(s["annotator_id"])
        if len(raters) < 4:
            continue
        thr = max(2, (len(raters) + 1) // 2)
        shared = [it for it in items if len(it.get("scores") or []) >= thr]
        if len(shared) < 3:
            continue
        rl = sorted(raters)
        pos = {r: i for i, r in enumerate(rl)}
        m = np.full((len(rl), len(shared)), np.nan)
        for j, it in enumerate(shared):
            for s in it["scores"]:
                m[pos[s["annotator_id"]], j] = float(s["score"])
        out.append({"prompt": rec["conversation"]["id"], "raters": rl, "m": m})
    return out


def standardize_raters(mat: np.ndarray) -> np.ndarray:
    """Remove per-rater scale use: z-score each rater's scores within the prompt.

    If cross-prompt persistence survives this, two raters agreeing is about WHAT
    they value, not about both of them being shouters.
    """
    out = mat.copy()
    for i in range(out.shape[0]):
        row = out[i]
        ok = ~np.isnan(row)
        if ok.sum() < 2:
            continue
        mu, sd = row[ok].mean(), row[ok].std()
        out[i, ok] = (row[ok] - mu) / (sd if sd > 1e-9 else 1.0)
    return out


def pair_agreements(mat: np.ndarray, raters: list[str], min_overlap: int = 3):
    """Agreement between every co-rating pair on this prompt.

    Agreement = Pearson correlation of their signed score profiles over items
    both rated.  Correlation (not raw distance) so that a rater who simply uses
    a wider scale is not counted as disagreeing.
    """
    res = {}
    n = len(raters)
    for i, j in combinations(range(n), 2):
        a, b = mat[i], mat[j]
        ok = ~np.isnan(a) & ~np.isnan(b)
        if ok.sum() < min_overlap:
            continue
        x, y = a[ok], b[ok]
        if x.std() < 1e-9 or y.std() < 1e-9:
            continue
        res[(raters[i], raters[j])] = float(np.corrcoef(x, y)[0, 1])
    return res


def persistence(per_prompt, centre: bool, rng, permute: bool = False, standardize: bool = False):
    """Correlate a pair's agreement on one prompt with their agreement on another."""
    by_pair = defaultdict(list)
    for rec in per_prompt:
        raters = list(rec["raters"])
        if permute:
            raters = list(rng.permutation(raters))
        mat = standardize_raters(rec["m"]) if standardize else rec["m"]
        ag = pair_agreements(mat, raters)
        if not ag:
            continue
        vals = np.array(list(ag.values()))
        mu = vals.mean() if centre else 0.0
        for pair, v in ag.items():
            by_pair[frozenset(pair)].append(v - mu)

    xs, ys = [], []
    for pair, vals in by_pair.items():
        if len(vals) < 2:
            continue
        v = np.array(vals)
        idx = rng.permutation(len(v))
        half = len(v) // 2
        xs.append(v[idx[:half]].mean())
        ys.append(v[idx[half : 2 * half]].mean())
    if len(xs) < 30:
        return {"n_pairs": len(xs), "rho": float("nan")}
    xs, ys = np.array(xs), np.array(ys)
    return {
        "n_pairs": int(len(xs)),
        "rho": float(np.corrcoef(xs, ys)[0, 1]),
        "mean_agreement": float(np.mean([v for vs in by_pair.values() for v in vs])),
    }


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=Path(_ROOT + "/data/conversation_rubrics.jsonl"))
    p.add_argument("--out", type=Path, default=Path(_RES + "/a01_rater_structure.json"))
    p.add_argument("--null-reps", type=int, default=50)
    p.add_argument("--boot", type=int, default=200)
    a = p.parse_args()

    rng = np.random.default_rng(20260727)
    data = load_rubric_matrices(a.data)
    print(f"prompts with usable rubric matrices: {len(data)}")

    n_multi = len(
        {
            pr
            for rec in data
            for pr in pair_agreements(rec["m"], rec["raters"]).keys()
        }
    )
    print(f"distinct co-rating rater pairs: {n_multi}")

    obs_raw = persistence(data, centre=False, rng=rng)
    obs_ctr = persistence(data, centre=True, rng=rng)
    print(f"observed persistence  raw={obs_raw['rho']:.4f}  prompt-centred={obs_ctr['rho']:.4f}"
          f"  (pairs={obs_ctr['n_pairs']})")

    obs_std = persistence(data, centre=True, rng=rng, standardize=True)
    print(f"CONTROL response-style removed (per-rater z within prompt): rho={obs_std['rho']:.4f}")

    null = [persistence(data, centre=True, rng=rng, permute=True)["rho"]
            for _ in range(a.null_reps)]
    null = np.array([x for x in null if not np.isnan(x)])
    print(f"permutation null: mean={null.mean():+.4f} sd={null.std():.4f} "
          f"95%=[{np.percentile(null,2.5):+.4f},{np.percentile(null,97.5):+.4f}]")

    boot = np.array([persistence(data, centre=True, rng=rng)["rho"] for _ in range(a.boot // 10)])
    z = (obs_ctr["rho"] - null.mean()) / (null.std() + 1e-12)
    verdict = (
        "STRUCTURE (M2): agreement persists across prompts beyond the null"
        if obs_ctr["rho"] > np.percentile(null, 97.5)
        else "NOISE (M1): no persistence beyond the permutation null"
        if obs_ctr["rho"] < np.percentile(null, 97.5)
        else "UNVERIFIED"
    )
    print(f"z vs null = {z:+.2f}   ->  {verdict}")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    sb = lambda r: 2 * r / (1 + r) if r == r else float("nan")
    print(f"Spearman-Brown corrected (split-half -> full): raw={sb(obs_ctr['rho']):.4f} "
          f"style-removed={sb(obs_std['rho']):.4f}")

    a.out.write_text(json.dumps({
        "prompts": len(data),
        "observed_style_removed": obs_std,
        "spearman_brown_centred": sb(obs_ctr["rho"]),
        "spearman_brown_style_removed": sb(obs_std["rho"]),
        "observed_raw": obs_raw,
        "observed_prompt_centred": obs_ctr,
        "null_mean": float(null.mean()),
        "null_sd": float(null.std()),
        "null_ci": [float(np.percentile(null, 2.5)), float(np.percentile(null, 97.5))],
        "resample_spread": [float(boot.min()), float(boot.max())] if len(boot) else None,
        "z_vs_null": float(z),
        "verdict": _freeze(verdict, "R01_rater_structure"),
    }, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
