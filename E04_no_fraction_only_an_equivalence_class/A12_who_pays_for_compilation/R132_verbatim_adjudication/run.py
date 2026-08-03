"""r132 -- the one analysis that settles whether DISAGREEMENT itself gets a criterion dropped.

THE DISPUTE
-----------
Two independent designs measured whether contested criteria survive compilation and reached
opposite verdicts, and the difference is a design difference, not noise:

  design A   continuous matchability score (|corr| of a criterion's 4-response satisfaction vector
             with the compiled arm's), regressed linearly on |mean rating|. Adjusted effect
             +0.003 [-0.019, 0.025]. Verdict: the raw association is entirely magnitude-mediated.
  design B   binary retention (is this criterion some core criterion's nearest neighbour within a
             calibrated radius), logistic on standardised |mean| and log rater count. Adjusted
             OR 0.354 [0.247, 0.493]. Verdict: it survives magnitude.

Both instruments are PROXIES for retention, because the release ships no provenance. But design B
found something neither used as an adjusted outcome: 298 of core's 3,828 criteria (7.8%) are
VERBATIM copies of a full criterion after normalisation. On that subset, retention is not a proxy.
It is a fact.

B did report the verbatim arm -- 11.2% of the copied criteria are contested against a 40.9%
population base rate, z = -10.2 -- but UNADJUSTED, and magnitude is exactly the quantity in dispute.
So the decisive analysis is the one nobody ran: adjusted, on ground truth.

    outcome    was this coval_full criterion copied verbatim into coval_core?   (no proxy)
    predictor  is it contested -- do raters split by sign?
    adjust     |mean rating|, rater count, and the criterion's own discriminability

WHAT THIS CAN AND CANNOT SETTLE
-------------------------------
Verbatim copying is one retention PATHWAY, not retention. A criterion can be retained by being
rewritten, and 92% of core is. If contested criteria are retained at the same overall rate but
preferentially by rewriting rather than copying, this design would see a drop that is really a
change of pathway. That limit is structural and is stated in the conclusion rather than argued
away -- but it cuts the same way for both disputants, and it is the only ground truth on offer.

PRE-REGISTERED KILL (fixed before any adjusted coefficient was computed)
-----------------------------------------------------------------------
W-DISAGREEMENT-PENALISED  contested stays significantly negative after adjustment. Design B is
                          right on ground truth, and disagreement itself costs a criterion its
                          place.
W-MAGNITUDE-ONLY          contested's adjusted coefficient's CI covers zero while |mean rating|
                          stays significant. Design A is right; the drop is the release's own
                          documented "pick the highest-rated" rule and nothing more.
W-NEITHER                 neither predictor survives on ground truth, so the verbatim subset cannot
                          adjudicate and the dispute stands open.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx.stamp import stamp  # noqa: E402

RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
FULL_NPZ = _ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz"

MIN_RATERS = 4        # pre-registered: contestedness is undefined below this, and the release has
                      # a literal hole at n=2 and n=3, so 4 is the first estimable count
CONTEST_MIN = 0.20    # pre-registered: contested iff min(pos,neg)/n >= this
N_BOOT = 4000         # cluster bootstrap over PROMPTS
SEEDS = (8101, 4409, 20260730, 31337, 271828)


def norm(s):
    """Normalisation for the verbatim match. Deliberately conservative: case, whitespace and
    terminal punctuation only. Anything more aggressive would start matching paraphrases, which is
    the semantic matching this round exists to avoid."""
    return re.sub(r"\s+", " ", (s or "").strip().lower()).rstrip(" .;:!")


def logistic(X, y, iters=200, ridge=1e-6):
    """Newton-Raphson. Returns coefficients; separation is caught by the caller via the CI."""
    b = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1.0 / (1.0 + np.exp(-np.clip(X @ b, -30, 30)))
        W = p * (1 - p)
        H = X.T @ (X * W[:, None]) + ridge * np.eye(X.shape[1])
        g = X.T @ (y - p) - ridge * b
        step = np.linalg.solve(H, g)
        b += step
        if np.max(np.abs(step)) < 1e-9:
            break
    return b


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(_RES / "r132_verbatim_adjudication.json"))
    args = ap.parse_args()
    _RES.mkdir(parents=True, exist_ok=True)

    for p in (RUBRICS, FULL_NPZ):
        if not p.exists():
            print(f"REFUSING: missing {p}. Exits 2, never 0.", file=sys.stderr)
            return 2

    z = np.load(FULL_NPZ, allow_pickle=True)
    sat = defaultdict(lambda: defaultdict(list))
    for m, v in zip(z["meta"], z["sat"]):
        pid, ci, _lab = str(m).split("|")
        sat[pid][int(ci)].append(float(v))
    # the tensor's first field is the PROMPT id; the rubrics record carries a CONVERSATION id.
    # They are not the same key. The first version looked the tensor up by conversation id, got {}
    # every time, and silently scored every criterion's discriminability as 0.0 -- an adjustment
    # claimed and not made. The tell was p = 2.0000 on that term, which is not a p-value at all.
    from covalx import load_join  # noqa: E402
    cid2pid = {}
    for pid, _comp, rub in load_join(str(_ROOT / "data/comparisons.jsonl"), str(RUBRICS)):
        cid2pid[rub["conversation"]["id"]] = pid

    rows = []
    n_core_total = n_verbatim_total = 0
    n_core_verbatim = [0]   # counted on the CORE side; n_verbatim_total counts the FULL side and
                            # the two are different numbers because a core text can match several
    for line in open(RUBRICS):
        r = json.loads(line)
        cid = r["conversation"]["id"]
        core_texts = {norm(it.get("criterion")) for it in (r.get("coval_core") or [])
                      if (it.get("criterion") or "").strip()}
        n_core_total += len(r.get("coval_core") or [])
        n_core_verbatim_local = sum(
            1 for t in core_texts if t in {norm(it.get("criterion"))
                                           for it in (r.get("coval_full") or [])})
        n_core_verbatim[0] += n_core_verbatim_local
        by_ci = sat.get(cid2pid.get(cid, ""), {})
        for i, it in enumerate(r.get("coval_full") or []):
            s = [x["score"] for x in (it.get("scores") or [])]
            if len(s) < MIN_RATERS:
                continue
            a = np.asarray(s, float)
            npos, nneg = int((a > 0).sum()), int((a < 0).sum())
            frac = min(npos, nneg) / len(a)
            vals = by_ci.get(i, [])
            copied = norm(it.get("criterion")) in core_texts
            n_verbatim_total += copied
            rows.append({
                "cid": cid,
                "copied": int(copied),
                "contested": int(frac >= CONTEST_MIN),
                "frac_minority": frac,
                "abs_mean": abs(float(a.mean())),
                "log_n": float(np.log(len(a))),
                "discrim": float(np.std(vals)) if len(vals) > 1 else 0.0,
                "n": len(a),
            })

    if not rows:
        print(f"REFUSING: no criterion has >= {MIN_RATERS} raters. Exits 2.", file=sys.stderr)
        return 2
    y = np.array([r["copied"] for r in rows], float)
    if y.sum() < 20:
        print(f"REFUSING: only {int(y.sum())} verbatim-copied criteria clear the rater floor. A "
              f"logistic on ground truth needs a population, and this is not one. Exits 3.",
              file=sys.stderr)
        return 3

    c = np.array([r["contested"] for r in rows], float)
    print(f"{len(rows):,} coval_full criteria with >= {MIN_RATERS} raters")
    print(f"  verbatim-copied into core: {int(y.sum())} ({y.mean():.1%})")
    print(f"  contested (minority share >= {CONTEST_MIN:.0%}): {c.mean():.1%}")
    print(f"  contested share AMONG the copied: {c[y == 1].mean():.1%}  "
          f"vs among the not-copied: {c[y == 0].mean():.1%}")
    print(f"  (whole release: {n_core_verbatim[0]} of {n_core_total} CORE criteria have a verbatim "
          f"twin in full, {n_core_verbatim[0]/max(n_core_total,1):.1%}; separately "
          f"{n_verbatim_total} FULL criteria at this rater floor were copied -- different sides of "
          f"the same match, not the same number)")

    def design(rs):
        return np.column_stack([
            np.ones(len(rs)),
            np.array([r["contested"] for r in rs], float),
            _std([r["abs_mean"] for r in rs]),
            _std([r["log_n"] for r in rs]),
            _std([r["discrim"] for r in rs]),
        ])

    def _std(v):
        v = np.asarray(v, float)
        s = v.std()
        return (v - v.mean()) / (s if s > 0 else 1.0)

    NAMES = ("intercept", "contested", "|mean rating|", "log raters", "discriminability")
    X = design(rows)
    b_obs = logistic(X, y)

    # cluster bootstrap over PROMPTS -- criteria within a prompt compete for the same 4 core slots,
    # so they are not independent draws and a criterion-level bootstrap would understate the spread
    by_prompt = defaultdict(list)
    for r in rows:
        by_prompt[r["cid"]].append(r)
    cids = list(by_prompt)
    boots = {s: [] for s in SEEDS}
    for s in SEEDS:
        rng = np.random.default_rng(s)
        for _ in range(N_BOOT // len(SEEDS)):
            pick = rng.integers(0, len(cids), len(cids))
            rs = [r for j in pick for r in by_prompt[cids[j]]]
            yy = np.array([r["copied"] for r in rs], float)
            if yy.sum() < 5 or yy.sum() == len(yy):
                continue
            boots[s].append(logistic(design(rs), yy))
    allb = np.array([v for s in SEEDS for v in boots[s]])
    print(f"\n  {len(allb)} cluster-bootstrap fits over {len(cids)} prompts, {len(SEEDS)} seeds")
    print(f"\n  {'term':<20}{'coef':>9}{'OR':>9}{'95% CI on OR':>24}{'p':>9}")
    out = {}
    for j, nm in enumerate(NAMES):
        lo, hi = np.percentile(allb[:, j], [2.5, 97.5])
        pv = 2 * min((allb[:, j] <= 0).mean(), (allb[:, j] >= 0).mean())
        pv = max(pv, 1.0 / (len(allb) + 1))
        out[nm] = {"coef": float(b_obs[j]), "or": float(np.exp(b_obs[j])),
                   "or_ci": [float(np.exp(lo)), float(np.exp(hi))], "p": float(pv)}
        print(f"  {nm:<20}{b_obs[j]:>+9.4f}{np.exp(b_obs[j]):>9.4f}"
              f"   [{np.exp(lo):.4f}, {np.exp(hi):.4f}]{pv:>9.4f}")
    per_seed = {str(s): float(np.mean([v[1] for v in boots[s]])) for s in SEEDS if boots[s]}
    print(f"  per-seed mean contested coefficient: "
          + ", ".join(f"{k}:{v:+.4f}" for k, v in per_seed.items()))

    # ---- POSITIVE CONTROL: the instrument must move on a predictor whose answer is known --------
    # |mean rating| is the release's own documented selection signal. If the fit cannot recover it,
    # the contested null below would be silence rather than a measurement.
    pos = out["|mean rating|"]
    pos_ok = pos["or_ci"][0] > 1.0 or pos["or_ci"][1] < 1.0
    print(f"\n  POSITIVE CONTROL  |mean rating| OR {pos['or']:.4f} "
          f"[{pos['or_ci'][0]:.4f}, {pos['or_ci'][1]:.4f}] -> "
          f"{'MOVES' if pos_ok else 'DOES NOT MOVE'}")
    if not pos_ok:
        print("REFUSING to adjudicate: the fit cannot recover the release's own documented "
              "selection signal, so a null on `contested` would be silence. Exits 3.",
              file=sys.stderr)
        return 3

    # ---- PLACEBO with an answer known in advance ----------------------------------------------
    # permuting `copied` WITHIN prompt destroys every predictor's relationship while preserving the
    # number of copies per prompt. The contested coefficient must go to zero.
    rng = np.random.default_rng(SEEDS[0])
    pl = []
    for _ in range(400):
        rs = []
        for cid2, group in by_prompt.items():
            yy = np.array([r["copied"] for r in group], float)
            rng.shuffle(yy)
            for r, v in zip(group, yy):
                r2 = dict(r)
                r2["copied"] = int(v)
                rs.append(r2)
        pl.append(logistic(design(rs), np.array([r["copied"] for r in rs], float))[1])
    pl = np.array(pl)
    print(f"  PLACEBO  within-prompt permutation of the outcome, 400 draws: contested coefficient "
          f"{pl.mean():+.4f} (sd {pl.std():.4f}); observed {b_obs[1]:+.4f} sits at z = "
          f"{(b_obs[1]-pl.mean())/max(pl.std(),1e-9):+.2f}")

    ct = out["contested"]
    contested_survives = ct["or_ci"][1] < 1.0
    world = ("W-DISAGREEMENT-PENALISED" if contested_survives else
             "W-MAGNITUDE-ONLY" if pos_ok else "W-NEITHER")
    conclusion = (
        f"The dispute between the two contested-criteria designs is adjudicated on the only ground "
        f"truth the release offers: {n_core_verbatim[0]} of {n_core_total} coval_core criteria "
        f"({n_core_verbatim[0]/max(n_core_total,1):.1%}) have a verbatim twin in coval_full "
        f"criterion, so for those, retention is a fact rather than a proxy. Among the "
        f"{len(rows):,} full criteria with at least {MIN_RATERS} raters, {int(y.sum())} were "
        f"copied; {c[y==1].mean():.1%} of the copied are contested against {c[y==0].mean():.1%} of "
        f"the not-copied. Adjusted -- logistic on contestedness with |mean rating|, log rater count "
        f"and the criterion's own across-response discriminability, cluster-bootstrapped over "
        f"{len(cids)} prompts at {len(allb)} fits over {len(SEEDS)} seeds -- contested carries "
        f"OR {ct['or']:.4f} [{ct['or_ci'][0]:.4f}, {ct['or_ci'][1]:.4f}], p {ct['p']:.4f}, while "
        f"|mean rating| carries OR {pos['or']:.4f} [{pos['or_ci'][0]:.4f}, {pos['or_ci'][1]:.4f}]. "
        f"A within-prompt permutation of the outcome puts the contested coefficient at "
        f"{pl.mean():+.4f} (sd {pl.std():.4f}), and the observed value sits "
        f"{(b_obs[1]-pl.mean())/max(pl.std(),1e-9):+.2f} sd from it. WORLD: {world}. "
        + ("Disagreement costs a criterion its place even after the release's own stated selection "
           "signal is adjusted for, so the second design is right on ground truth."
           if world == "W-DISAGREEMENT-PENALISED" else
           "Once magnitude is adjusted for, contestedness carries no independent penalty on ground "
           "truth: the drop is the documented 'pick the highest-rated' rule, and the first design "
           "is right."
           if world == "W-MAGNITUDE-ONLY" else
           "Neither predictor survives on the verbatim subset, so it cannot adjudicate.")
        + " STRUCTURAL LIMIT, stated rather than argued away: verbatim copying is ONE retention "
          "pathway and 92% of core is rewritten rather than copied. If contested criteria are "
          "retained at the same rate but preferentially by rewriting, this design would read a "
          "change of pathway as a drop. That limit cuts identically for both disputants, and it is "
          "the only ground truth available.")
    print(f"\n  WORLD: {world}\n\n{conclusion}\n")

    Path(args.out).write_text(json.dumps(
        {"n_criteria": len(rows), "n_copied": int(y.sum()),
         "n_core_total": n_core_total, "n_full_side_copied": n_verbatim_total,
         "n_core_side_verbatim": n_core_verbatim[0],
         "contested_share_overall": float(c.mean()),
         "contested_share_copied": float(c[y == 1].mean()),
         "contested_share_not_copied": float(c[y == 0].mean()),
         "min_raters": MIN_RATERS, "contest_min": CONTEST_MIN, "n_boot_fits": len(allb),
         "seeds": list(SEEDS), "per_seed_contested_coef": per_seed,
         "terms": out, "positive_control_moves": bool(pos_ok),
         "placebo_mean": float(pl.mean()), "placebo_sd": float(pl.std()),
         "placebo_z": float((b_obs[1] - pl.mean()) / max(pl.std(), 1e-9)),
         "world": world, "conclusion": conclusion, **stamp(__file__)}, indent=1, sort_keys=True))
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
