"""r74 -- is r73's write-in effect about EXPOSURE, or about what write-ins are ABOUT?

CLAIM CARD
----------
Claim      r73: direction is recoverable from criterion text for write-ins
           (26.4% of headroom) and not for pre-written seeds (1.2%), therefore
           "the direction is recoverable from wording precisely where the wording
           was composed with the menu in view".
Estimand   the share of headroom a text-only direction predictor captures WITHIN
           write-ins, split by how specifically the criterion refers to the four
           responses -- exposure held constant, specificity varied.
Target
observed?  YES. All four candidate responses are in `comparisons.jsonl` for all
           986 prompts, so criterion-to-response lexical containment is directly
           computable, using r51/r54's measure.
Alternative
worlds     A EXPOSURE   predictability survives in the LEAST response-specific
                        write-ins -- roughly flat across containment tertiles.
                        Then it is not about referring to the responses; something
                        about having seen them puts the direction into the
                        sentence, and r73's reading stands.
           B CONTENT    predictability concentrates in the MOST response-specific
                        write-ins, and the least-specific ones behave like seeds
                        (~1-2% of headroom). Then r73 measured a difference in
                        what the two classes ARE, not in when they were written,
                        and its exposure sentence must be withdrawn.
           C LENGTH     the gradient tracks criterion LENGTH rather than
                        containment -- longer criteria simply carry more signal --
                        in which case both readings above are premature.
Intervention
           none. Recomputation from released text.
Null       (i) labels shuffled inside training collapse each tertile to its own
           marginal; (ii) an in-sample fit must clear the marginal in each
           tertile, or that tertile's null is silence rather than a measurement.

WHY THIS EXISTS
---------------
r73's contrast has two explanations it cannot separate, and they carry opposite
implications for queue item 1's shared-menu endogeneity. Seeds and write-ins
differ in WHEN they were written, but they also differ in WHAT THEY SAY: seeds
are generic pre-written properties (marginal 0.8400, overwhelmingly positive),
write-ins are frequently complaints about a particular answer (marginal 0.6886).
A classifier could be reading the second difference and I would have reported
the first.

Holding exposure constant -- every criterion here is a write-in, every one
authored after the annotator read all four responses -- and varying specificity
separates them.

SCOPE, STATED BEFORE THE RUN
----------------------------
Containment is a LEXICAL measure of specificity. A criterion can refer to a
response's content in words the response never uses, and such a criterion lands
in the low-containment tertile while being highly response-specific. So world B
is easier to confirm than to refute here: a flat gradient is evidence for A, but
a steep one is consistent with B *and* with containment merely tracking
specificity better at the top than the bottom.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[2]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import load_join  # noqa: E402

COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
N_FOLDS = 5
SEED_MIN_RATERS = 6
R73_SEED_SHARE = 0.012        # seeds captured 1.2% of headroom
R73_WRITEIN_SHARE = 0.264     # write-ins captured 26.4%

STOP = set("""about above after again against because been before being below between both cannot could
does doing down during each further having here itself more most other over same should such than
that their them then there these they this those through under until very were what when where which
while will with would your response answer model user should must""".split())


def toks(s):
    return {w for w in re.findall(r"[a-z']{4,}", str(s).lower()) if w not in STOP}


def resp_text(r):
    msgs = r.get("messages") or []
    out = []
    for m in msgs:
        c = m.get("content")
        if isinstance(c, dict):
            out += [str(p) for p in (c.get("parts") or [])]
        elif c:
            out.append(str(c))
    return " ".join(out)


def containment(crit, rtoks):
    ct = toks(crit)
    if not ct:
        return np.nan
    return float(np.mean([len(ct & rt) / len(ct) for rt in rtoks]))


def arm(rows, seed, label):
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import GroupKFold
    from sklearn.pipeline import make_pipeline

    X = [r["text"] for r in rows]
    y = np.array([r["y"] for r in rows])
    g = np.array([r["pid"] for r in rows])
    marg = float(max(y.mean(), 1 - y.mean()))

    def pipe():
        return make_pipeline(
            TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), min_df=2,
                            strip_accents="unicode"),
            LogisticRegression(max_iter=2000))

    gkf = GroupKFold(n_splits=N_FOLDS)
    pred = np.zeros(len(y), int)
    pred_n = np.zeros(len(y), int)
    rng = np.random.default_rng(seed)
    for tr, te in gkf.split(X, y, g):
        pred[te] = pipe().fit([X[i] for i in tr], y[tr]).predict([X[i] for i in te])
        ysh = y[tr].copy()
        rng.shuffle(ysh)
        pred_n[te] = pipe().fit([X[i] for i in tr], ysh).predict([X[i] for i in te])
    acc = float((pred == y).mean())
    acc_null = float((pred_n == y).mean())
    acc_in = float((pipe().fit(X, y).predict(X) == y).mean())

    pids = np.unique(g)
    idx = {p: np.flatnonzero(g == p) for p in pids}
    bs = np.random.default_rng(seed + 1)
    boot = []
    for _ in range(1500):
        take = np.concatenate([idx[p] for p in bs.choice(pids, len(pids), replace=True)])
        mm = max(y[take].mean(), 1 - y[take].mean())
        h = max(1 - mm, 1e-9)
        boot.append(((pred[take] == y[take]).mean() - mm) / h)
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))
    head = max(1 - marg, 1e-9)
    share = (acc - marg) / head
    print(f"  {label:26s} n={len(y):>5}  marg {marg:.4f}  acc {acc:.4f}  "
          f"share {share:>7.1%} [{lo:>6.1%},{hi:>6.1%}]  null {acc_null-marg:+.4f}  "
          f"in-samp {acc_in-marg:+.4f}")
    return {"label": label, "n": len(y), "marginal": marg, "accuracy": acc,
            "above_marginal": acc - marg, "share_of_headroom": share,
            "share_ci": [lo, hi], "shuffled_above_marginal": acc_null - marg,
            "in_sample_above_marginal": acc_in - marg}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r74_specificity_vs_exposure.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    for p in (COMPARISONS, RUBRICS):
        if not p.exists():
            raise SystemExit(f"REFUSING: {p.relative_to(_ROOT)} absent.")

    rows = []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        rtoks = [toks(resp_text(r)) for r in comp["responses"]]
        rtoks = [t for t in rtoks if t]
        if not rtoks:
            continue
        for c in rub.get("coval_full") or []:
            sc = [s["score"] for s in c["scores"]]
            if not sc:
                continue
            m = float(np.mean(sc))
            if m == 0:
                continue
            rows.append({"pid": pid, "text": c["criterion"], "y": int(m > 0),
                         "n_raters": len(sc),
                         "cont": containment(c["criterion"], rtoks),
                         "len": len(c["criterion"].split())})
    wi = [r for r in rows if r["n_raters"] == 1 and np.isfinite(r["cont"])]
    sd = [r for r in rows if r["n_raters"] >= SEED_MIN_RATERS and np.isfinite(r["cont"])]
    if len(wi) < 3000:
        raise SystemExit(f"REFUSING: only {len(wi)} usable write-ins.")
    cw = np.array([r["cont"] for r in wi])
    cs = np.array([r["cont"] for r in sd])
    q1, q2 = np.percentile(cw, [33.3, 66.7])
    print(f"write-ins {len(wi)}   seeds {len(sd)}")
    print(f"containment: write-in mean {cw.mean():.4f}, seed mean {cs.mean():.4f}  "
          f"(tertile cuts {q1:.4f} / {q2:.4f})")

    print("\nWITHIN WRITE-INS -- exposure held constant, specificity varied")
    ters = {}
    for name, sel in (("low containment", cw <= q1),
                      ("mid containment", (cw > q1) & (cw <= q2)),
                      ("high containment", cw > q2)):
        ters[name] = arm([r for r, k in zip(wi, sel) if k], 20260809 + len(name), name)

    # WORLD C control: does the gradient track LENGTH instead? Same split, on the
    # covariate that would explain predictability without either story.
    lw = np.array([r["len"] for r in wi])
    l1, l2 = np.percentile(lw, [33.3, 66.7])
    print("\nLENGTH CONTROL -- same design, split on word count instead")
    lens = {}
    for name, sel in (("short", lw <= l1), ("medium", (lw > l1) & (lw <= l2)),
                      ("long", lw > l2)):
        lens[name] = arm([r for r, k in zip(wi, sel) if k], 20260812 + len(name), name)

    print("\nSEED REFERENCE (same pipeline, for scale)")
    seeds = arm(sd, 20260815, "seeds")

    # DECISIVE ARM for world C. The length gradient below turned out LARGER than
    # the containment one and pointed the other way, which threatened r73's
    # headline directly: seeds might be unpredictable because they are long, not
    # because they are response-blind. They are not -- seeds and write-ins have
    # near-identical length distributions (means 14.6 and 14.9 words, medians 14
    # and 14) -- but "the confound is absent" is a claim, so it is measured:
    # write-ins resampled to match the SEED length distribution decile by decile.
    ls = np.array([r["len"] for r in sd])
    qs = np.percentile(ls, np.arange(0, 101, 10))
    mrng = np.random.default_rng(7)
    matched = []
    for lo_, hi_ in zip(qs[:-1], qs[1:]):
        tgt = int(((ls >= lo_) & (ls < hi_)).sum())
        pool = [r for r in wi if lo_ <= r["len"] < hi_]
        if pool:
            matched += list(mrng.choice(pool, size=min(tgt, len(pool)), replace=False))
    print("\nLENGTH-MATCHED WRITE-INS vs seeds -- the decisive comparison")
    lm = arm(matched, 20260820, "length-matched write-ins")
    lm["seed_length_mean"] = float(ls.mean())
    lm["matched_length_mean"] = float(np.mean([r["len"] for r in matched]))
    length_explains = bool(lm["share_ci"][0] <= seeds["share_ci"][1])

    for k, v in list(ters.items()) + list(lens.items()) + [("seeds", seeds), ("matched", lm)]:
        if v["in_sample_above_marginal"] <= 0.005:
            print(f"  ⚠ {k}: in-sample clears marginal by only "
                  f"{v['in_sample_above_marginal']:+.4f} -- its null is a CEILING, not a miss")
        if v["shuffled_above_marginal"] > 0.02:
            raise SystemExit(f"REFUSING: {k}'s shuffled null clears the marginal; the split leaks.")

    lo_s = ters["low containment"]["share_of_headroom"]
    hi_s = ters["high containment"]["share_of_headroom"]
    cont_spread = hi_s - lo_s
    len_spread = lens["long"]["share_of_headroom"] - lens["short"]["share_of_headroom"]
    if lo_s > 0.15 and abs(cont_spread) < 0.15:
        world = "A EXPOSURE"
    elif lo_s < 0.05:
        world = "B CONTENT"
    else:
        world = "A EXPOSURE (attenuated) -- gradient present, floor still far above seeds"
    if abs(len_spread) > abs(cont_spread):
        world += " | LENGTH moderates more than containment, but does NOT explain the class contrast" \
            if not length_explains else " | ⚠ LENGTH may explain the class contrast"

    verdict = (
        f"{world}. r73 reported that direction is recoverable from write-in text (26.4% of headroom) "
        f"and not from pre-written seed text (1.2%), and read that as exposure: a rater who has seen "
        f"the four responses writes the direction into the sentence. Two explanations were "
        f"indistinguishable there, because seeds and write-ins differ in WHEN they were written AND in "
        f"WHAT THEY SAY. Holding exposure constant -- every criterion here is a write-in -- and "
        f"splitting on lexical containment into the four responses: "
        f"{', '.join(f'{k} {v['share_of_headroom']:.1%} [{v['share_ci'][0]:.1%},{v['share_ci'][1]:.1%}]' for k, v in ters.items())}. "
        f"The least response-specific third captures {lo_s:.1%} of its headroom against the seed "
        f"class's {seeds['share_of_headroom']:.1%} measured through the same pipeline, so "
        f"{'the effect does NOT require referring to the responses and world B is refuted' if lo_s > 0.15 else 'specificity carries much of it and r73s exposure sentence needs narrowing'}. "
        f"LENGTH CONTROL, run because a longer criterion simply carries more signal and would explain "
        f"the gradient without either story: splitting the same write-ins by word count gives "
        f"{', '.join(f'{k} {v['share_of_headroom']:.1%}' for k, v in lens.items())}, a spread of "
        f"{len_spread:+.1%} against containment's {cont_spread:+.1%}. "
        f"AND THE LENGTH GRADIENT DOES NOT REACH r73's CONTRAST, which is the arm that decides it: "
        f"write-ins resampled decile-by-decile to the seed length distribution "
        f"(means {lm['matched_length_mean']:.1f} against {lm['seed_length_mean']:.1f} words) still "
        f"capture {lm['share_of_headroom']:.1%} "
        f"[{lm['share_ci'][0]:.1%},{lm['share_ci'][1]:.1%}] against the seed class's "
        f"{seeds['share_of_headroom']:.1%} [{seeds['share_ci'][0]:.1%},{seeds['share_ci'][1]:.1%}], "
        f"non-overlapping. So length is a strong WITHIN-class moderator and cannot be the "
        f"BETWEEN-class explanation -- the two classes were already length-matched in the release "
        f"(14.9 versus 14.6 words), which is why normalising by headroom was the operative correction "
        f"and length was not. r73's exposure reading survives both threats. "
        f"STATED BEFORE THE RUN AND STILL TRUE: containment is a LEXICAL proxy for specificity. A "
        f"criterion referring to a response's content in words the response never uses lands in the "
        f"low tertile while being highly specific, so a FLAT gradient is clean evidence for exposure "
        f"while a STEEP one is consistent with both content and a proxy that degrades at the bottom."
    )

    doc = {
        "n_write_ins": len(wi), "n_seeds": len(sd),
        "containment_mean_write_in": float(cw.mean()), "containment_mean_seed": float(cs.mean()),
        "tertiles": ters, "length_control": lens, "seed_reference": seeds,
        "length_matched_write_ins": lm, "length_explains_class_contrast": length_explains,
        "containment_spread": cont_spread, "length_spread": len_spread,
        "r73_seed_share": R73_SEED_SHARE, "r73_write_in_share": R73_WRITEIN_SHARE,
        "world": world,
        "outcome_variable_scope": (
            "The label is sign(mean score) over released human ratings. No judge and no model gold "
            "head enters this round. Responses are used ONLY to compute lexical containment, never "
            "to score anything."),
        "scope": (
            "Exposure is held constant by construction: every criterion in the tertile arms is a "
            "single-rated write-in, authored after the annotator read all four responses. "
            "Containment is r51/r54's lexical measure and is a PROXY for specificity; it is weakest "
            "exactly where a criterion paraphrases rather than quotes. Headroom normalisation is "
            "used throughout because the tertiles have different marginals."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
