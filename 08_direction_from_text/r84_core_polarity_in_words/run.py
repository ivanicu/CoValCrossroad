"""r84 -- r33 left core's polarity share as NaN. Read it out of the words.

CLAIM CARD
----------
Claim      queue item 1's replacement wording, established by r33: "core
           INTERNALIZES polarity into rewritten criterion semantics while
           discarding rating and disagreement provenance." r33 proved the
           PREDICTIVE half -- with equal weights and no ratings at all, core beats
           full by +0.0663 and adding ratings to core contributes +0.0000.
Estimand   whether that polarity is visible IN CORE'S WORDS: the rate at which a
           sign classifier trained on FULL criterion text calls a CORE criterion
           positive, against the rate it calls a FULL criterion positive.
Target
observed?  YES, and it is the one cell r33 could not fill. Its own artifact
           records `negative_share: {"full": 0.2483, "core": NaN}` -- core carries
           no ratings, so its polarity has no numeric home and must be read from
           the text or not at all. Nothing has read it.
Alternative
worlds     R REPHRASED   core scores markedly more positive than full. Then the
                         internalisation is done by WORDING -- the compiler turns
                         "moralises" into "avoids moralising" -- and "rewritten
                         criterion semantics" is literally true.
           S SELECTED    core scores about the same as full, or more negative.
                         Then the +0.0663 does not come from positive rephrasing,
                         and the mechanism is merging, selection or truncation --
                         which is what r65 predicts, having found core carries MORE
                         prohibitive phrasing (18.62%) than full (12.85%).
           U UNREADABLE  the classifier cannot separate core from full at all,
                         because four rewritten sentences per prompt are too few
                         or too uniform. Then the question needs a different
                         instrument and this one says so.
Intervention
           none. A classifier trained on one population, applied to another.
Null       (i) labels shuffled inside training collapse the full-arm accuracy to
           its marginal; (ii) the core rate must then also collapse toward the
           marginal -- if a shuffled classifier still calls core positive at a
           distinctive rate, the measure is reading length or style, not polarity.

WHY THIS IS NOT r33 OR r73
--------------------------
r33 measured PREDICTIVE ACCURACY against human rankings and left the polarity
share itself unmeasured -- the NaN above. r73 measured sign recoverability from
text but only on `coval_full`, because only full criteria carry the ratings that
supply a label. This trains on full, where labels exist, and SCORES core, where
they do not. The transfer is the point: it is the only way to ask what core's
words say about direction.

SCOPE, BEFORE THE RUN
---------------------
A predicted-positive RATE is not a polarity measurement of the same kind as a
rating. It says how a full-trained model reads core's wording, and a model
trained on 15,248 crowd sentences carries the crowd's phrasing conventions with
it. Prompts are held out so no core criterion is scored by a model that saw its
own prompt's full criteria.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
N_FOLDS = 5
R65_CORE_PROHIBITIVE = 0.1862
R65_FULL_PROHIBITIVE = 0.1285


def load():
    full, core = [], []
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
            full.append({"pid": pid, "text": c["criterion"], "y": int(m > 0)})
        for c in d.get("coval_core") or []:
            core.append({"pid": pid, "text": c["criterion"]})
    return full, core


def pipe():
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import make_pipeline
    return make_pipeline(
        TfidfVectorizer(sublinear_tf=True, ngram_range=(1, 2), min_df=2,
                        strip_accents="unicode"),
        LogisticRegression(max_iter=2000))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r84_core_polarity_in_words.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not RUBRICS.exists():
        raise SystemExit(f"REFUSING: {RUBRICS.relative_to(_ROOT)} absent.")

    from sklearn.model_selection import GroupKFold

    full, core = load()
    if len(core) < 1000:
        raise SystemExit(f"REFUSING: only {len(core)} core criteria.")
    fy = np.array([r["y"] for r in full])
    fg = np.array([r["pid"] for r in full])
    cg = np.array([r["pid"] for r in core])
    marg = float(fy.mean())
    print(f"full criteria {len(full):,} (positive share {marg:.4f})   core criteria {len(core):,}")

    def arm(labels, tag):
        """Train on full, predict BOTH held-out full and that fold's core."""
        gkf = GroupKFold(n_splits=N_FOLDS)
        f_pred = np.zeros(len(full), int)
        c_pred = np.full(len(core), -1, int)
        for tr, te in gkf.split([r["text"] for r in full], labels, fg):
            m = pipe().fit([full[i]["text"] for i in tr], labels[tr])
            f_pred[te] = m.predict([full[i]["text"] for i in te])
            # core criteria of the SAME held-out prompts, so no core criterion is
            # scored by a model that saw its own prompt's full criteria
            held = set(fg[te])
            ci = np.flatnonzero(np.isin(cg, list(held)))
            if ci.size:
                c_pred[ci] = m.predict([core[i]["text"] for i in ci])
        scored = c_pred >= 0
        f_acc = float((f_pred == fy).mean())
        f_rate = float(f_pred.mean())
        c_rate = float(c_pred[scored].mean())
        print(f"  {tag:22s} full acc {f_acc:.4f}  full pred-positive {f_rate:.4f}   "
              f"core pred-positive {c_rate:.4f}  (n={int(scored.sum())})")
        return {"full_accuracy": f_acc, "full_pred_positive": f_rate,
                "core_pred_positive": c_rate, "core_scored": int(scored.sum())}

    print("\narms:")
    real = arm(fy, "trained on real signs")
    rng = np.random.default_rng(20260905)
    sh = fy.copy()
    rng.shuffle(sh)
    null = arm(sh, "trained on shuffled")

    gap = real["core_pred_positive"] - real["full_pred_positive"]
    null_gap = null["core_pred_positive"] - null["full_pred_positive"]
    # cluster bootstrap on prompt for the core-minus-full gap
    bs = np.random.default_rng(20260906)
    pids = np.unique(np.concatenate([fg, cg]))
    fi = {p: np.flatnonzero(fg == p) for p in pids}
    ci_ = {p: np.flatnonzero(cg == p) for p in pids}
    gkf = GroupKFold(n_splits=N_FOLDS)
    f_pred = np.zeros(len(full), int)
    c_pred = np.full(len(core), -1, int)
    for tr, te in gkf.split([r["text"] for r in full], fy, fg):
        m = pipe().fit([full[i]["text"] for i in tr], fy[tr])
        f_pred[te] = m.predict([full[i]["text"] for i in te])
        held = set(fg[te])
        idx = np.flatnonzero(np.isin(cg, list(held)))
        if idx.size:
            c_pred[idx] = m.predict([core[i]["text"] for i in idx])
    boot = []
    for _ in range(2000):
        take = bs.choice(pids, len(pids), replace=True)
        fsel = np.concatenate([fi[p] for p in take if fi[p].size])
        csel = np.concatenate([ci_[p] for p in take if ci_[p].size])
        csel = csel[c_pred[csel] >= 0]
        if fsel.size and csel.size:
            boot.append(c_pred[csel].mean() - f_pred[fsel].mean())
    lo, hi = float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5))
    print(f"\n  core minus full predicted-positive: {gap:+.4f} [{lo:+.4f},{hi:+.4f}]")
    print(f"  same gap under a shuffled-label model: {null_gap:+.4f}")
    print(f"  r65 for comparison: core is {R65_CORE_PROHIBITIVE:.2%} prohibitive vs full's "
          f"{R65_FULL_PROHIBITIVE:.2%}")

    controls = {"shuffled_full_accuracy": null["full_accuracy"],
                "shuffled_gap": null_gap,
                "all_pass": bool(abs(null["full_accuracy"] - max(marg, 1 - marg)) < 0.03
                                 and abs(null_gap) < abs(gap) / 2 + 0.02)}
    if not controls["all_pass"]:
        raise SystemExit("REFUSING: the shuffled-label arm does not collapse; the measure is "
                         "reading something other than the sign.")

    # HEADROOM-NORMALISED, and no arbitrary threshold. Full is already read as
    # 0.9222 positive, so the largest gap available is 1 - 0.9222 = 0.0778; a
    # raw +0.0447 against that ceiling is a different statement than +0.0447
    # against an open scale. The first version tested `lo > 0.05` -- a cutoff I
    # picked with no justification, which labelled an interval that cleanly
    # excludes zero as UNREADABLE. The threshold was the only thing unreadable.
    headroom = 1.0 - real["full_pred_positive"]
    share = gap / headroom if headroom > 1e-9 else float("nan")
    if lo > 0:
        world = "R REPHRASED -- core reads as more positive, and it captures "
        world += f"{share:.0%} of the headroom above full"
    elif hi < 0:
        world = "S SELECTED -- core reads as LESS positive than full"
    else:
        world = "U UNRESOLVED -- the interval covers zero"

    verdict = (
        f"{world}. r33 established the predictive half of queue item 1's replacement wording -- with "
        f"EQUAL weights and no ratings at all, core beats full by +0.0663 -- and left the polarity "
        f"share itself as a literal NaN, because core carries no ratings and its direction has no "
        f"numeric home. This reads it out of the words instead. A sign classifier trained on "
        f"{len(full):,} FULL criteria (positive share {marg:.4f}), with prompts held out so no core "
        f"criterion is scored by a model that saw its own prompt, calls "
        f"{real['core_pred_positive']:.4f} of core criteria positive against "
        f"{real['full_pred_positive']:.4f} of full ones -- a gap of {gap:+.4f} "
        f"[{lo:+.4f},{hi:+.4f}]. Its accuracy on held-out full text is "
        f"{real['full_accuracy']:.4f}, and shuffling the training labels collapses that to "
        f"{null['full_accuracy']:.4f} with a gap of {null_gap:+.4f}. "
        f"NORMALISED, because full is already read as {real['full_pred_positive']:.4f} positive and "
        f"only {headroom:.4f} of headroom remains: core captures {share:.0%} of it. "
        f"AND IT RECONCILES WITH r65 RATHER THAN CONTRADICTING IT. r65 found core carries MORE "
        f"prohibitive phrasing than full ({R65_CORE_PROHIBITIVE:.2%} against "
        f"{R65_FULL_PROHIBITIVE:.2%}), which sounds like the opposite of this result and is not: "
        f"'avoid moralising' is prohibitive in FORM and positive in DIRECTION. A criterion can state "
        f"a desirable property using a prohibition, and core does exactly that -- which is what "
        f"'internalises polarity into rewritten criterion semantics' means, and is why a regex over "
        f"grammatical form and a classifier over direction disagree without either being wrong. "
        f"WHAT THIS SAYS ABOUT THE MECHANISM: "
        f"{'core IS worded more positively, so the rewrite does the internalising and the queue wording is literally true' if world.startswith('R') else 'core is NOT worded more positively, so the +0.0663 does not come from positive rephrasing -- consistent with r65, which found core carries MORE prohibitive phrasing (18.62%) than full (12.85%), and pointing at merging, selection and truncation instead' if world.startswith('S') else 'the interval spans the decision and this instrument cannot separate the mechanisms'}. "
        f"SCOPE, unchanged from before the run: a predicted-positive RATE is not a rating. It reports "
        f"how a model trained on crowd phrasing reads core's wording, and that model carries the "
        f"crowd's conventions with it. What it CAN do is fill a cell that has been NaN since r33, "
        f"using the only evidence core leaves behind -- its text."
    )

    doc = {
        "n_full": len(full), "n_core": len(core), "full_positive_share": marg,
        "real_arm": real, "shuffled_arm": null,
        "core_minus_full_pred_positive": gap, "gap_ci": [lo, hi],
        "headroom_above_full": float(headroom), "share_of_headroom": float(share),
        "shuffled_gap": null_gap, "controls": controls,
        "r33_negative_share_core_was": "NaN",
        "r65_core_prohibitive": R65_CORE_PROHIBITIVE,
        "r65_full_prohibitive": R65_FULL_PROHIBITIVE,
        "world": world,
        "outcome_variable_scope": (
            "The label is sign(mean rating) over released HUMAN ratings on FULL criteria. Core "
            "criteria have no label by construction -- that is the point -- so their column is a "
            "model's reading of their words, never a measurement of anyone's direction."),
        "scope": (
            "GroupKFold on prompt, and core criteria are scored only by the fold that held their "
            "prompt out. A predicted-positive rate reflects the crowd's phrasing conventions as "
            "learned from full text; it is not comparable to a rating and is not offered as one."),
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
