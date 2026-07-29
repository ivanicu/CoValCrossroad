"""r73 -- is a criterion's DIRECTION recoverable from its words alone?

CLAIM CARD
----------
Claim      "No rater in the release rated a criterion before seeing four
           responses, so a response-blind direction is unreachable -- that is
           S_pre." (README, R-layer row.)
Estimand   the accuracy with which a criterion's aggregate direction
           sign(mean score) is predicted from its TEXT ALONE, on prompts held
           out entirely, measured ABOVE the positive-class marginal.
Target
observed?  PARTLY, and the part matters. The claim above is exactly right about
           what it says: no human rated pre-exposure, so no PERSON's pre-menu
           direction exists in this release. This round does NOT contradict it
           and does not measure it. It measures a different quantity that the
           release DOES contain: whether the direction is a function of the
           criterion's semantics, recoverable with no response ever entering the
           computation.
Alternative
worlds     P PRIOR-CARRIED  text alone predicts direction well above the 0.7435
                            marginal on held-out prompts. Then most of the
                            direction signal is in what the criterion SAYS, the
                            menu is not needed to recover it, and S_pre's human
                            arm should be powered on the RESIDUAL rather than on
                            the whole -- which changes the preregistration.
           C MENU-REQUIRED  text alone does not beat the marginal. Then direction
                            is not a property of the criterion's wording, the
                            human PRE arm is measuring something genuinely
                            unavailable here, and S_pre stays exactly as
                            preregistered.
Intervention
           none. Held-out prediction from released text.
Null       (i) labels shuffled WITHIN the training set must collapse to the
           marginal; (ii) an in-sample fit must beat the marginal -- if even
           that fails the pipeline cannot learn and any null is silence.

WHY THIS IS NOT A RESTATEMENT OF THE MARGINAL
---------------------------------------------
r61 measured the marginal and did the arithmetic that matters for the human
experiment: 77.01% of released RATINGS are positive, so chance agreement in the
PRE/POST design is 0.6459, not 0.5. On criterion AGGREGATES the marginal is
0.7435. A classifier that predicted "positive" always would score exactly that
and would have learned nothing. Every number below is reported against that
baseline, never against 0.5.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
Text-predictability is NOT evidence that any person held the direction before
seeing the menu. A shared PHRASING CONVENTION would produce it: criteria written
as "avoid X" or "fails to Y" carry their sign in their grammar, and annotators
were instructed to write both positive and negative criteria. So a high score
supports "the direction is recoverable without the menu" and NOT "the direction
pre-existed in the rater". The control for this is reported alongside: accuracy
restricted to criteria containing no overt negation marker, where the grammatical
shortcut is unavailable.

PROVENANCE SPLIT
----------------
r48 identified seed vs write-in by rating count -- perfectly bimodal, 9,684 items
with one score and the rest many-rated. Seeds were PRE-WRITTEN and shown to every
rater; write-ins were authored after the annotator read all four responses. If
text carries direction, it should carry it for BOTH, and the write-in arm is the
harder case because its text was composed with the menu in view.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
SEED_MIN_RATERS = 6          # r48's structural gap: 1 vs many, nothing between
N_FOLDS = 5
NEG = re.compile(r"\b(avoid|avoids|not|never|fail|fails|failing|without|instead|"
                 r"refuse|refuses|omit|omits|lack|lacks|no|nor|rather than)\b", re.I)


def load():
    rows = []
    for line in open(RUBRICS, encoding="utf-8"):
        d = json.loads(line)
        pid = (d.get("conversation") or {}).get("id")
        for c in d.get("coval_full") or []:
            sc = [s["score"] for s in c["scores"]]
            if not sc:
                continue
            m = float(np.mean(sc))
            if m == 0:
                continue
            rows.append({"pid": pid, "text": c["criterion"], "y": int(m > 0),
                         "n_raters": len(sc), "neg": bool(NEG.search(c["criterion"]))})
    return rows


def evaluate(rows, seed, label):
    """Group-held-out accuracy: no prompt appears in both train and test."""
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
            LogisticRegression(max_iter=2000, C=1.0, class_weight=None))

    gkf = GroupKFold(n_splits=N_FOLDS)
    pred = np.zeros(len(y), int)
    for tr, te in gkf.split(X, y, g):
        m = pipe().fit([X[i] for i in tr], y[tr])
        pred[te] = m.predict([X[i] for i in te])
    acc = float((pred == y).mean())

    # NULL: shuffle labels inside training only -- must collapse to the marginal
    rng = np.random.default_rng(seed)
    pred_n = np.zeros(len(y), int)
    for tr, te in gkf.split(X, y, g):
        ysh = y[tr].copy()
        rng.shuffle(ysh)
        m = pipe().fit([X[i] for i in tr], ysh)
        pred_n[te] = m.predict([X[i] for i in te])
    acc_null = float((pred_n == y).mean())

    # POSITIVE CONTROL: in-sample fit must clear the marginal, or the pipeline
    # cannot learn this task at all and its held-out null is silence, not a
    # finding.
    ins = pipe().fit(X, y)
    acc_in = float((ins.predict(X) == y).mean())

    # CONFOUND CONTROL: criteria with no overt negation marker, where the
    # grammatical shortcut is unavailable.
    nn = np.array([not r["neg"] for r in rows])
    acc_nn = float((pred[nn] == y[nn]).mean()) if nn.sum() > 50 else float("nan")
    marg_nn = float(max(y[nn].mean(), 1 - y[nn].mean())) if nn.sum() > 50 else float("nan")

    # prompt-clustered bootstrap on the held-out predictions
    pids = np.unique(g)
    idx = {p: np.flatnonzero(g == p) for p in pids}
    bs = np.random.default_rng(seed + 1)
    boot = []
    for _ in range(2000):
        take = np.concatenate([idx[p] for p in bs.choice(pids, len(pids), replace=True)])
        boot.append((pred[take] == y[take]).mean() - max(y[take].mean(), 1 - y[take].mean()))
    lo, hi = (float(x) for x in np.percentile(boot, [2.5, 97.5]))

    print(f"\n=== {label}   n={len(y)}  prompts={len(pids)}")
    print(f"  marginal (always-majority)      {marg:.4f}")
    print(f"  held-out accuracy from TEXT     {acc:.4f}   above marginal {acc-marg:+.4f} "
          f"[{lo:+.4f},{hi:+.4f}]")
    print(f"  shuffled-label null             {acc_null:.4f}   above marginal {acc_null-marg:+.4f}")
    print(f"  in-sample (positive control)    {acc_in:.4f}   above marginal {acc_in-marg:+.4f}")
    print(f"  no-negation subset              {acc_nn:.4f}   marginal there {marg_nn:.4f}  "
          f"above {acc_nn-marg_nn:+.4f}   (n={int(nn.sum())})")
    return {"n": len(y), "prompts": len(pids), "marginal": marg,
            "accuracy": acc, "above_marginal": acc - marg,
            "above_marginal_ci": [lo, hi],
            "shuffled_null": acc_null, "shuffled_above_marginal": acc_null - marg,
            "in_sample": acc_in,
            "no_negation_accuracy": acc_nn, "no_negation_marginal": marg_nn,
            "no_negation_above": acc_nn - marg_nn, "n_no_negation": int(nn.sum())}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r73_direction_from_text_alone.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not RUBRICS.exists():
        raise SystemExit(f"REFUSING: {RUBRICS.relative_to(_ROOT)} absent.")

    rows = load()
    seeds = [r for r in rows if r["n_raters"] >= SEED_MIN_RATERS]
    writeins = [r for r in rows if r["n_raters"] == 1]
    print(f"criteria with a non-zero mean: {len(rows)}   "
          f"seed-class (>={SEED_MIN_RATERS} raters) {len(seeds)}   write-ins (1 rater) {len(writeins)}")

    out = {"all": evaluate(rows, 20260806, "ALL CRITERIA"),
           "seeds": evaluate(seeds, 20260807, "SEED CLASS (pre-written, shown to every rater)"),
           "write_ins": evaluate(writeins, 20260808, "WRITE-INS (authored after reading all four)")}

    for k, v in out.items():
        if v["in_sample"] <= v["marginal"] + 0.01:
            raise SystemExit(f"REFUSING: the {k} pipeline cannot beat its own marginal in "
                             f"sample; its held-out result would be silence, not a null.")
        if v["shuffled_above_marginal"] > 0.02:
            raise SystemExit(f"REFUSING: the {k} shuffled-label null clears the marginal by "
                             f"{v['shuffled_above_marginal']:+.4f}; the split leaks.")

    # HEADROOM-NORMALISED, because the two arms have very different marginals
    # (seeds 0.8400, write-ins 0.6886) and an absolute margin is not comparable
    # across them: the seed arm simply has less room to gain. Share of available
    # headroom = above_marginal / (1 - marginal).
    for v in out.values():
        v["headroom"] = 1.0 - v["marginal"]
        v["share_of_headroom"] = v["above_marginal"] / v["headroom"]
    a_all, sd, wi = out["all"], out["seeds"], out["write_ins"]
    print(f"\nHEADROOM-NORMALISED (above-marginal as a share of what was available to gain)")
    for k, v in out.items():
        print(f"  {k:12s} headroom {v['headroom']:.4f}   captured "
              f"{v['share_of_headroom']:>7.1%}")

    # THREE worlds, because the result landed outside the two I wrote. P and C
    # both assumed the seed and write-in arms would agree; they do not, and
    # "recoverability is itself a product of exposure" had no label to land in.
    # Same one-sided-fork error as r69, caught here by the provenance split
    # rather than by the threshold.
    if sd["above_marginal_ci"][0] > 0.02:
        world = "P PRIOR-CARRIED"
    elif wi["above_marginal_ci"][0] > 0.02:
        world = "W WRITTEN-IN -- recoverable only from post-exposure text"
    else:
        world = "C MENU-REQUIRED"

    verdict = (
        f"{world}. THE PROVENANCE SPLIT INVERTS THE NAIVE READING, and it is the whole result. "
        f"Criteria whose TEXT is response-blind -- the pre-written seed class, shown to every rater "
        f"before they wrote anything -- carry essentially NO text-recoverable direction beyond their "
        f"marginal: {sd['above_marginal']:+.4f} "
        f"[{sd['above_marginal_ci'][0]:+.4f},{sd['above_marginal_ci'][1]:+.4f}], which is "
        f"{sd['share_of_headroom']:.1%} of the headroom available to them. Criteria composed AFTER "
        f"the annotator read all four responses carry {wi['above_marginal']:+.4f} "
        f"[{wi['above_marginal_ci'][0]:+.4f},{wi['above_marginal_ci'][1]:+.4f}], or "
        f"{wi['share_of_headroom']:.1%} of theirs. Normalising by headroom is required here and not "
        f"cosmetic: the seed marginal is {sd['marginal']:.4f} against {wi['marginal']:.4f}, so the "
        f"arms had very different room to gain and the raw margins are not comparable. "
        f"SO THE DIRECTION IS RECOVERABLE FROM WORDING PRECISELY WHERE THE WORDING WAS COMPOSED WITH "
        f"THE MENU IN VIEW. That is the signature of construction, not of a prior: a rater who has "
        f"seen the responses writes the direction into the sentence. It is not evidence that a "
        f"pre-menu direction is absent -- nothing here can see one -- but it removes the reading that "
        f"text-predictability demonstrates one. "
        f"The README's R-layer row says a response-blind direction is unreachable because no "
        f"rater in the release rated a criterion before seeing four responses. That is exactly right "
        f"about what it says, and this round neither contradicts nor measures it. It measures a "
        f"different quantity the release does contain: whether the direction is recoverable from the "
        f"criterion's WORDS, with no response entering the computation at any point. Predicting "
        f"sign(mean score) from text alone with prompts held out entirely, over {a_all['n']} criteria "
        f"on {a_all['prompts']} prompts: accuracy {a_all['accuracy']:.4f} against a majority-class "
        f"marginal of {a_all['marginal']:.4f}, i.e. {a_all['above_marginal']:+.4f} above it "
        f"[{a_all['above_marginal_ci'][0]:+.4f},{a_all['above_marginal_ci'][1]:+.4f}] under a "
        f"prompt-clustered bootstrap. Controls ran first and both are required to pass: shuffling "
        f"labels inside training collapses to {out['all']['shuffled_null']:.4f} "
        f"({out['all']['shuffled_above_marginal']:+.4f} above marginal), and the in-sample fit reaches "
        f"{a_all['in_sample']:.4f}, so a held-out null would have been a measurement rather than "
        f"silence. BY PROVENANCE: the seed class -- pre-written and shown to every rater -- scores "
        f"{out['seeds']['above_marginal']:+.4f} above its marginal, and write-ins, composed with the "
        f"menu in view, {out['write_ins']['above_marginal']:+.4f}. THE CONFOUND, WRITTEN BEFORE THE "
        f"RUN: a shared phrasing convention would produce this without anyone holding a prior "
        f"direction, since 'avoid X' carries its sign in its grammar. Restricted to criteria with no "
        f"overt negation marker the margin is {a_all['no_negation_above']:+.4f} on "
        f"{a_all['n_no_negation']} items, so the grammatical shortcut "
        f"{'does not account for it' if a_all['no_negation_above'] > 0.02 else 'may account for much of it'}. "
        f"WHAT THIS CHANGES: S_pre's human arm is preregistered against r61's chance baseline of "
        f"0.6459, which is the RATING marginal. For the PRE arm the relevant baseline is now sharper "
        f"still -- a text-only predictor scores {sd['accuracy']:.4f} on exactly the class of criteria "
        f"an S_pre participant would face (pre-written, response-blind), which is "
        f"{sd['above_marginal']:+.4f} above the marginal and therefore adds nothing beyond it. So for "
        f"SEEDS the preregistered baseline needs no adjustment, and that is a positive result for the "
        f"design. Where it does need adjusting is any arm using WRITE-IN text, where a text-only "
        f"predictor already captures {wi['share_of_headroom']:.1%} of the headroom and a human PRE "
        f"arm could score well while measuring the phrasing convention twice."
    )

    doc = {
        "arms": out, "world": world,
        "seed_min_raters": SEED_MIN_RATERS, "n_folds": N_FOLDS,
        "outcome_variable_scope": (
            "The label is sign(mean score) over a criterion's released ratings -- a HUMAN quantity, "
            "not a model gold head. No judge and no response text enters this round at any point."),
        "scope": (
            "Prompts are held out entirely (GroupKFold on prompt id), so no criterion from a test "
            "prompt informs training. This does NOT measure whether any person held a direction "
            "before seeing the menu -- that is S_pre and it remains unreachable in this release. It "
            "measures whether the direction is a function of the criterion's semantics. A shared "
            "phrasing convention is a live alternative and its control is reported."),
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
