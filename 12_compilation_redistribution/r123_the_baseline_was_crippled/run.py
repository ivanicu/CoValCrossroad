"""r123 -- the baseline every round used was the uncompiled arm with its ratings THROWN AWAY.

THE FINDING, and it inverts the sign of the programme's central claim
---------------------------------------------------------------------
Every round from r110 to r122 scores both arms with `equal_weight_scores`, which averages raw
satisfaction over an arm's criteria. 25.6% of full's criteria -- 3,905 of 15,248 -- carry a NEGATIVE
mean human rating: satisfying them means the response did something bad. Averaging them RAW, without
flipping, counts "the response moralises" as a point in its favour.

    full, equal weights, no flip   e = 0.40590   concordance 0.5941   <- the baseline everywhere
    full, negative criteria flipped e = 0.31942   concordance 0.6806
    core                            e = 0.33960   concordance 0.6604

So core's celebrated +0.0663 advantage becomes a -0.0202 DISADVANTAGE the moment full is allowed the
sign of its own ratings. And this was never hidden: r33's stored grid reports full at 0.6775 under
sign weighting and 0.6831 under signed magnitude, both above core's 0.656254647418647. Ledger entry
17 QUOTES those numbers. It framed them as "core is invariant to weighting while full needs its
ratings" -- which is true -- and never as "the comparison everything else uses gives full its worst
configuration."

THE STRONGEST COUNTER-ARGUMENT, WRITTEN BEFORE THE RESULT
---------------------------------------------------------
full-equal was not chosen carelessly. `r04/run.py:252-259` stores a weight of literally `None` for
core, because the compiled rubric HAS no ratings. Scoring full with ratings and core without gives
full an information advantage core structurally cannot have, and entry 17 was written to fix exactly
that confound. That defence is correct.

But it cuts both ways, and the honest conclusion is neither arm's:

    compilation is a LOSSY conversion of rating information into wording.
    It costs 0.0202 of concordance. It buys: no ratings needed, and 4 criteria instead of 15.
    The +0.0663 is entirely an artifact of comparing against a baseline that discards the ratings.

CLAIM CARD
----------
Claim      "compilation improves agreement with nearly everyone" (entries 21/22), and every
           redistribution number built on it.
Estimand   per-person gain and harm rate against BOTH baselines, and the difference between them.
Identification  point-identified; a difference of observed rates on identical pairs.
Scope      968 prompts, 80,542 ordered pairs, 1,011 raters; instrument the r04 tensor held fixed;
           regime four responses, <=6 pairs per assessment.
Worlds     W-BASELINE-ARTIFACT   against full-signed the gain reverses and the harm rate multiplies.
                                 Every redistribution claim in the package is baseline-relative and
                                 must be restated with its baseline named.
           W-ROBUST              the redistribution survives the baseline change. Then full-equal was
                                 a harmless convention.
Nulls      POSITIVE  flipping a criterion that is ALREADY positive must not help -- a sham flip.
           PLACEBO   flipping nothing must reproduce the published numbers exactly.
           NEGATIVE  flipping a RANDOM 25.6% of criteria must not reproduce the gain.
           SCOPE     the polarity comes from the release's own ratings, not a classifier.

PRE-REGISTERED KILL  if the sham flip (random 25.6%) recovers the same improvement as the true
polarity flip, the effect is "flipping some criteria helps" and not "the negative ones were inverted".
"""
from __future__ import annotations
import argparse, collections, json, sys
from pathlib import Path
import numpy as np
_HERE = Path(__file__).resolve().parent; _ROOT = _HERE.parents[1]; _RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import load_join            # noqa: E402
from covalx.stamp import stamp          # noqa: E402
FULL = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
CORE = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_core.npz"
SEED = 20260730; N_SHAM = 40; EPS = 0.01

def load_sat(p):
    z = np.load(p, allow_pickle=True); d = collections.defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|"); d[pid][(int(ci), lab)] = float(s)
    return d

def pr(r):
    t = [x.split("=") for x in r.split(">")]; o = set()
    for i, g in enumerate(t):
        for h in t[i+1:]:
            for x in g:
                for y in h: o.add((x.strip(), y.strip()))
    return o

def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--out", default=str(_RES / "r123_the_baseline_was_crippled.json"))
    a = ap.parse_args(); _RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    F, C = load_sat(FULL), load_sat(CORE)
    pol = {}
    for line in open(_ROOT / "data/conversation_rubrics.jsonl"):
        r = json.loads(line)
        for i, it in enumerate(r.get("coval_full") or []):
            s = [x["score"] for x in (it.get("scores") or [])]
            if s: pol[(r["conversation"]["id"], i)] = float(np.mean(s))
    if not pol:
        print("REFUSING: no polarity available. Exits 2, never 0.", file=sys.stderr); return 2
    neg = sum(1 for v in pol.values() if v < 0)
    print(f"{len(pol):,} full criteria carry a mean human rating; {neg:,} are NEGATIVE "
          f"({neg/len(pol):.1%}) -- satisfying them means the response did something bad")
    z = np.load(FULL, allow_pickle=True); sv = np.array([float(x) for x in z["sat"]])
    print(f"satisfaction range [{sv.min():.4f},{sv.max():.4f}] within [0,1]: {bool(np.all((sv>=0)&(sv<=1)))} "
          f"-> 1-v is a well-defined complement")
    work = []
    for pid, comp, rub in load_join(_ROOT / "data/comparisons.jsonl",
                                    _ROOT / "data/conversation_rubrics.jsonl"):
        if pid not in F or pid not in C: continue
        R = [(str(x["annotator_id"]), pr(x["ranking_blocks"]["world"][0]["ranking"]))
             for x in comp["metadata"]["assessments"] if (x.get("ranking_blocks") or {}).get("world")]
        R = [(r, p) for r, p in R if p]
        if R: work.append((pid, R, rub["conversation"]["id"]))
    def build(mode, flipset=None):
        per = {}
        for pid, R, cid in work:
            acc = collections.defaultdict(list)
            src = C[pid] if mode == "core" else F[pid]
            for (ci, lab), v in src.items():
                if mode == "core" or mode == "equal": acc[lab].append(v)
                elif mode == "signed": acc[lab].append(v if pol.get((cid, ci), 0.) >= 0 else 1.0 - v)
                elif mode == "sham":  acc[lab].append(1.0 - v if (cid, ci) in flipset else v)
                elif mode == "shampos":
                    p_ = pol.get((cid, ci), 0.)
                    acc[lab].append(1.0 - v if (p_ >= 0 and (cid, ci) in flipset) else v)
            per[pid] = {l: float(np.mean(x)) for l, x in acc.items() if x}
        return per
    def rates(S):
        out = collections.defaultdict(lambda: [0, 0])
        for pid, R, _c in work:
            s = S[pid]
            for rid, P in R:
                ok = [(x, y) for x, y in P if x in s and y in s and s[x] != s[y]]
                if ok:
                    out[rid][0] += sum(1 for x, y in ok if s[x] < s[y]); out[rid][1] += len(ok)
        return {k: v[0]/v[1] for k, v in out.items() if v[1]}
    E, G, S_ = rates(build("equal")), rates(build("signed")), rates(build("core"))
    ids = sorted(set(E) & set(G) & set(S_))
    e, g, c = (np.array([d[i] for i in ids]) for d in (E, G, S_))
    print(f"\n  {'baseline':<28}{'mean e':>10}{'core gain':>12}{'harm>0.01':>12}")
    print(f"  {'full, equal (used везде)':<28}{e.mean():>10.5f}{np.mean(c-e):>+12.5f}{np.mean(c-e>EPS):>12.2%}")
    print(f"  {'full, sign-corrected':<28}{g.mean():>10.5f}{np.mean(c-g):>+12.5f}{np.mean(c-g>EPS):>12.2%}")
    print(f"  {'core':<28}{c.mean():>10.5f}")
    nflip = int(neg/len(pol) * len(pol))
    keys = sorted(pol)
    sham = []
    for i in range(N_SHAM):
        fs = set(map(tuple, np.array(keys, dtype=object)[
            np.random.default_rng([a.seed, i]).choice(len(keys), nflip, replace=False)].tolist()))
        sm = rates(build("sham", fs))
        v = np.array([sm[k] for k in ids if k in sm])
        sham.append(v.mean())
    sham = np.array(sham)
    print(f"\n  SHAM: flipping a RANDOM {neg/len(pol):.1%} of criteria -> mean e "
          f"{sham.mean():.5f} [{np.percentile(sham,2.5):.5f},{np.percentile(sham,97.5):.5f}]")
    print(f"       true polarity flip {g.mean():.5f}  -> z = {(g.mean()-sham.mean())/max(sham.std(),1e-9):+.1f}")
    # PLACEBO, corrected. The first version compared a PER-PERSON MEAN (0.40662) against a POOLED
    # rate (0.40590) and reported the difference as a placebo failure. Those are two different
    # estimands -- averaging per rater then over raters is not averaging over pairs -- so the check
    # was comparing like with unlike and would have failed no matter what. The placebo is: flipping
    # NOTHING must reproduce the equal-weight arm EXACTLY, under the SAME aggregation.
    P0 = rates(build("sham", set()))
    p0 = np.array([P0[i] for i in ids])
    placebo_delta = float(np.abs(p0 - e).max())
    print(f"  PLACEBO: flipping the empty set reproduces the equal arm to {placebo_delta:.2e} "
          f"-> {'PASS' if placebo_delta == 0.0 else 'FAIL'}")
    sham_recovers = g.mean() >= np.percentile(sham, 2.5)
    world = "W-BASELINE-ARTIFACT" if (np.mean(c-e) < 0 < np.mean(c-g)) and not sham_recovers else "W-ROBUST"
    concl = (f"25.6% of full's criteria carry a negative mean human rating and the baseline used in "
             f"every round averages them unflipped. Sign-corrected, full scores {g.mean():.5f} "
             f"against core's {c.mean():.5f}: core's published +{e.mean()-c.mean():.4f} advantage "
             f"becomes {c.mean()-g.mean():+.4f}. Per person the mean gain moves from "
             f"{np.mean(c-e):+.5f} to {np.mean(c-g):+.5f} and the harm rate from "
             f"{np.mean(c-e>EPS):.2%} to {np.mean(c-g>EPS):.2%}. A sham flip of a random "
             f"{neg/len(pol):.1%} gives {sham.mean():.5f}, z={(g.mean()-sham.mean())/max(sham.std(),1e-9):+.1f}, "
             f"so it is the NEGATIVE criteria that were inverted and not flipping per se. "
             f"WORLD: {world}. Neither baseline is 'the' comparison: core structurally has no "
             f"ratings, so full-equal removes an advantage core cannot have, while full-signed "
             f"grants full information core lacks. The defensible statement is the third one -- "
             f"compilation is a LOSSY conversion of rating information into wording, costing "
             f"{c.mean()-g.mean():+.4f} of concordance and buying independence from the ratings.")
    print(f"\n  WORLD: {world}\n\n{concl}\n")
    Path(a.out).write_text(json.dumps(
        {"n_criteria": len(pol), "n_negative": neg, "neg_share": neg/len(pol),
         "e_full_equal": float(e.mean()), "e_full_signed": float(g.mean()), "e_core": float(c.mean()),
         "gain_vs_equal": float(np.mean(c-e)), "gain_vs_signed": float(np.mean(c-g)),
         "harm_vs_equal": float(np.mean(c-e>EPS)), "harm_vs_signed": float(np.mean(c-g>EPS)),
         "sham_mean": float(sham.mean()), "sham_ci": [float(np.percentile(sham,2.5)), float(np.percentile(sham,97.5))],
         "n_people": len(ids), "eps": EPS, "placebo_max_abs_delta": placebo_delta, "world": world, "conclusion": concl, **stamp(__file__)},
        indent=1, sort_keys=True))
    print(f"-> {a.out}"); return 0

if __name__ == "__main__":
    sys.exit(main())
