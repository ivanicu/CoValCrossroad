"""r23 -- Is r01's persistence a property of PEOPLE-IN-GENERAL or of PAIRS?

Raised by an independent statistics review, 2026-07-28.  r01 established that
pairwise rater agreement persists across disjoint prompt sets (rho=0.147,
z=+16.6 against a label-permutation null) and read that as M2, structured
plurality: raters cluster into value blocs, so a single core rubric is the
wrong object.  r16/r17/r18 are all downstream of that reading.

The reviewer's attack: agreement between i and j can persist with NO blocs at
all, if raters simply differ in how reliable they are.  A careful rater agrees
with everyone; a careless one agrees with nobody.  That is an ADDITIVE ACTOR
effect and it is fully compatible with M1 -- one shared target, heterogeneous
measurement noise -- whose prescription is the opposite of M2's: keep the
single core, weight raters by reliability, collect more data.

r01 cannot tell these apart.  Its permutation null shuffles rater IDs within a
prompt, which destroys actor identity and dyad identity together, so any actor
effect lands in the "structure" column by construction.

  M1b  one target, heterogeneous reliability
       A_ij(p) = mu(p) + a_i(p) + a_j(p) + noise, exactly.
       Persistence survives actor removal: NO.
       Reliably-disagreeing pairs beyond chance: NO.

  M2   value blocs
       Agreement additionally depends on WHICH pair, not just who is in it.
       Persistence survives actor removal: YES.
       Reliably-disagreeing pairs beyond chance: YES -- out-bloc pairs.

The second row is the part the reviewer did not test and is the sharper
separator.  An additive actor effect is ALSO what M2 produces when blocs are
unequal in size: a rater in the majority bloc agrees with more people.  So a
collapse of the residual does not by itself establish M1b -- but a residual
carrying reliably NEGATIVE pairs cannot be produced by reliability alone,
because low reliability attenuates agreement toward zero, never below it.

Estimator
---------
Per prompt, fit A_ij = mu + a_i + a_j by least squares over the observed dyads
and keep the residual.  Then run r01's own split-half persistence on three
series: the raw agreement, the fitted actor part, and the residual.

Controls in the same pass:
  * dyad-permutation null for the residual -- permute residual values across
    dyad slots WITHIN each prompt, so the residual distribution is preserved
    and only pair identity is destroyed.  This is the null r01 lacked.
  * sign concordance -- of pairs seen in both halves, how many are negative in
    both?  Compared against the same permutation null.
  * the whole thing is also run on style-standardised scores, since r01's
    headline control was per-rater z-scoring within prompt.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from pathlib import Path
import sys as _sys, pathlib as _pl  # noqa: E402
_sys.path.insert(0, str(_pl.Path(__file__).resolve().parents[3]))
from covalx.frozen import append_to as _freeze  # noqa: E402


import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"


def _load_r01():
    """Import r01's loaders by path, so this round cannot drift from it."""
    p = _ROOT / "rounds/01_object_and_rebuild/r01_rater_structure/run.py"
    spec = importlib.util.spec_from_file_location("r01", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def additive_fit(ag: dict, raters: list[str]):
    """A_ij = mu + a_i + a_j by least squares over the OBSERVED dyads.

    The parameters are not identified (mu absorbs any shift in a), but the
    FITTED VALUES are, and only those are used.  Returns (fitted, resid, r2)
    keyed the same way as `ag`.
    """
    keys = list(ag.keys())
    if len(keys) < 3:
        return None
    pos = {r: i for i, r in enumerate(raters)}
    n = len(raters)
    X = np.zeros((len(keys), n + 1))
    y = np.zeros(len(keys))
    for k, (u, v) in enumerate(keys):
        X[k, 0] = 1.0
        X[k, pos[u] + 1] += 1.0
        X[k, pos[v] + 1] += 1.0
        y[k] = ag[(u, v)]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    yhat = X @ beta
    resid = y - yhat
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - float((resid ** 2).sum()) / ss_tot if ss_tot > 1e-12 else float("nan")
    return ({k: float(v) for k, v in zip(keys, yhat)},
            {k: float(v) for k, v in zip(keys, resid)}, r2)


def split_half(by_pair: dict, rng) -> dict:
    """r01's estimator: disjoint halves of each pair's prompt series."""
    xs, ys = [], []
    for _pair, vals in by_pair.items():
        if len(vals) < 2:
            continue
        v = np.array(vals)
        idx = rng.permutation(len(v))
        half = len(v) // 2
        xs.append(v[idx[:half]].mean())
        ys.append(v[idx[half: 2 * half]].mean())
    if len(xs) < 30:
        return {"n_pairs": len(xs), "rho": float("nan"), "neg_both": float("nan")}
    xs, ys = np.array(xs), np.array(ys)
    return {"n_pairs": int(len(xs)),
            "rho": float(np.corrcoef(xs, ys)[0, 1]),
            "neg_both": float(np.mean((xs < 0) & (ys < 0))),
            "pos_both": float(np.mean((xs > 0) & (ys > 0)))}


def collect(data, r01, rng, standardize: bool, permute_resid: bool = False):
    """Build the three per-pair series (raw / actor / residual) across prompts."""
    raw, act, res = defaultdict(list), defaultdict(list), defaultdict(list)
    r2s = []
    for rec in data:
        mat = r01.standardize_raters(rec["m"]) if standardize else rec["m"]
        ag = r01.pair_agreements(mat, rec["raters"])
        if len(ag) < 3:
            continue
        fit = additive_fit(ag, rec["raters"])
        if fit is None:
            continue
        yhat, resid, r2 = fit
        r2s.append(r2)
        vals = np.array(list(ag.values()))
        mu = vals.mean()                       # r01 centres each prompt
        rvals = list(resid.values())
        if permute_resid:
            rvals = list(rng.permutation(rvals))
        for (k, _), rv in zip(resid.items(), rvals):
            raw[frozenset(k)].append(ag[k] - mu)
            act[frozenset(k)].append(yhat[k] - mu)
            res[frozenset(k)].append(rv)
    return raw, act, res, float(np.mean(r2s)) if r2s else float("nan")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--data", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r23_actor_vs_dyad.json")
    p.add_argument("--null-reps", type=int, default=40)
    a = p.parse_args()

    rng = np.random.default_rng(20260728)
    r01 = _load_r01()
    data = r01.load_rubric_matrices(a.data)
    print(f"prompts with usable rubric matrices: {len(data)}\n")

    out = {}
    for tag, std in (("as r01 reported (raw scores)", False),
                     ("style-removed (per-rater z within prompt)", True)):
        raw, act, res, r2 = collect(data, r01, rng, standardize=std)
        s_raw, s_act, s_res = (split_half(raw, rng), split_half(act, rng),
                               split_half(res, rng))

        null = []
        for _ in range(a.null_reps):
            _, _, nres, _ = collect(data, r01, rng, standardize=std, permute_resid=True)
            null.append(split_half(nres, rng))
        nrho = np.array([x["rho"] for x in null if x["rho"] == x["rho"]])
        nneg = np.array([x["neg_both"] for x in null if x["neg_both"] == x["neg_both"]])
        z = (s_res["rho"] - nrho.mean()) / (nrho.std() + 1e-12)
        zneg = (s_res["neg_both"] - nneg.mean()) / (nneg.std() + 1e-12)

        print(f"=== {tag} ===")
        print(f"  additive actor model explains {r2:.1%} of within-prompt dyad variance")
        print(f"  {'series':10s} {'rho':>8} {'pairs':>7}   split-half persistence")
        print(f"  {'raw':10s} {s_raw['rho']:>8.4f} {s_raw['n_pairs']:>7}   <- r01's headline")
        print(f"  {'actor':10s} {s_act['rho']:>8.4f} {s_act['n_pairs']:>7}   "
              f"<- people-in-general, M1b-compatible")
        print(f"  {'residual':10s} {s_res['rho']:>8.4f} {s_res['n_pairs']:>7}   "
              f"<- pair-specific, the ONLY M2 evidence")
        print(f"  dyad-permutation null for residual: {nrho.mean():+.4f} "
              f"+/- {nrho.std():.4f}   z = {z:+.2f}")
        print(f"  pairs negative in BOTH halves: {s_res['neg_both']:.3f} vs null "
              f"{nneg.mean():.3f} +/- {nneg.std():.3f}   z = {zneg:+.2f}")
        share = s_res["rho"] / s_raw["rho"] if abs(s_raw["rho"]) > 1e-9 else float("nan")
        print(f"  -> pair-specific share of the headline: {share:.1%}\n")

        out[("raw" if not std else "style_removed")] = {
            "actor_model_r2": r2, "raw": s_raw, "actor": s_act, "residual": s_res,
            "resid_null_mean": float(nrho.mean()), "resid_null_sd": float(nrho.std()),
            "resid_z": float(z), "neg_both_null_mean": float(nneg.mean()),
            "neg_both_null_sd": float(nneg.std()), "neg_both_z": float(zneg),
            "pair_specific_share_of_headline": float(share),
        }

    ref = out["style_removed"]
    surv = ref["resid_z"] > 2.0
    negs = ref["neg_both_z"] > 2.0
    verdict = (
        "M2 SURVIVES: pair-specific persistence exceeds the dyad-permutation null"
        if surv and negs else
        "M2 WEAKENED: pair-specific persistence survives, but no excess of reliably "
        "disagreeing pairs -- consistent with unequal-size blocs OR with a second "
        "reliability dimension"
        if surv else
        "M1b: the persistence r01 reported is an additive actor effect; removing it "
        "leaves nothing above the null, so a single core with rater weighting is not "
        "excluded by this observable"
    )
    print(f"VERDICT: {verdict}")
    _RES.mkdir(parents=True, exist_ok=True)
    out["verdict"] = _freeze(verdict, "r23_actor_vs_dyad")
    out["note"] = ("r01's permutation null shuffles rater ids, destroying actor and "
                   "dyad identity together, so an additive actor effect was scored as "
                   "structure. This round separates them. The sign-concordance test is "
                   "the sharper separator: low reliability attenuates agreement toward "
                   "zero, it cannot drive a pair reliably below zero.")
    a.out.write_text(json.dumps(out, indent=1))
    print(f"wrote {a.out}")


if __name__ == "__main__":
    main()
