"""r33 -- What IS CoVal-core? A pre-registered test that it launders post-choice polarity into text.

The sentence that makes this testable
--------------------------------------
`data/DATASET_CARD.md:74`, on how core is built:

    "Our process first rewrites all rubric items to have positive weight and
     then merges semantically redundant rubric items while adjusting their
     scores."

So core is not a SUBSET of full. It is a TRANSFORMATION, and one of its steps
takes a quantity that lived in the human ratings -- the sign a participant
attached to a criterion AFTER ranking the candidates -- and rewrites it into the
criterion's wording.

r32 measured what that sign is worth. Holding judge, responses and criterion text
fixed and varying only the weighting:

    full, equal weights (text only)      0.5899
    full, + human-rated sign             0.6775      polarity channel = +0.0876

If core has genuinely moved polarity into the sentences, then core scored with
EQUAL weights should already carry what full only reaches once the ratings are
applied -- because for core there are no negative weights left to apply.

Pre-registered predictions, written before the run
---------------------------------------------------
    P1  core/equal  >>  full/equal          polarity is in core's TEXT
    P2  core/signed  ~  core/equal          nothing left for weights to add,
                                            since every core weight is positive
    P3  full/signed  ~  core/equal          the same information, relocated

If P1 fails, the rewriting does not preserve polarity and core simply loses it.
If P2 fails, core's weights still carry something the text does not.

Why this matters beyond bookkeeping
------------------------------------
An external review listed "post-choice criterion selection and synthesis" as one
of the channels by which a response-blind-looking rubric can still encode facts
produced after participants saw the candidates. This measures that channel
directly. If core's readable, positively-phrased sentences are carrying
information that was supplied post-choice, then core is the artifact MOST likely
to be mistaken for a clean, response-independent value specification -- it is the
one that looks like a hand-written checklist -- and is the one where that reading
is least available.

Scope
-----
Evaluation pairs come from the ORIGINAL rankings, so this is internal concordance
on the elicitation manifold (entry 36). Both sources share that limitation, and
the comparison is between them.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import human_pairs, load_join  # noqa: E402


def load_sat(path):
    z = np.load(path, allow_pickle=True)
    out = defaultdict(dict)
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        out[pid][(int(ci), lab)] = float(s)
    return out


def weights(items, mode):
    """Weight per criterion. Items with no `scores` field get 1.0, not 0.0.

    CoVal-core ships ONLY the criterion text -- its released items carry no
    `scores` and no `rubric_item_id`, verified field by field. The first version
    assigned them weight 0.0, so every core prompt was skipped and the whole arm
    silently produced nothing. That is also a finding in its own right: the
    released core rubric has no weights, so equal weighting is the ONLY rule
    defined on it, and anyone scoring with core is necessarily using the
    configuration that scores 0.5899 on full -- unless the positive-weight
    rewriting moved the polarity into the sentences, which is exactly P1.
    """
    w = []
    for it in items:
        sc = [float(s["score"]) for s in (it.get("scores") or [])]
        if not sc:
            w.append(1.0)
            continue
        mean = float(np.mean(sc))
        w.append(1.0 if mode == "equal" else (float(np.sign(mean)) or 1.0)
                 if mode == "sign" else mean)
    return np.array(w, dtype=float)


def accuracy_series(sat, rub_items, pairs, mode):
    accs, pidlist = [], []
    for pid, items in rub_items.items():
        if pid not in sat:
            continue
        w = weights(items, mode)
        if np.abs(w).sum() < 1e-9:
            continue
        score = {}
        for lab in {l for (_c, l) in sat[pid]}:
            num = den = 0.0
            for ci in range(len(w)):
                s = sat[pid].get((ci, lab))
                if s is None or abs(w[ci]) < 1e-12:
                    continue
                num += w[ci] * s
                den += abs(w[ci])
            if den > 0:
                score[lab] = num / den
        if len(score) < 2:
            continue
        ok = tot = 0
        for x, y in pairs[pid]:
            if x in score and y in score:
                tot += 1
                ok += int(score[x] > score[y])
        if tot:
            accs.append(ok / tot)
            pidlist.append(pid)
    return np.array(accs), pidlist


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--full", type=Path,
                   default=_ROOT / "rounds/r04_rebuild_satisfaction/results/a04_full.npz")
    p.add_argument("--core", type=Path,
                   default=_ROOT / "rounds/r04_rebuild_satisfaction/results/a04_core.npz")
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r33_core_launders_polarity.json")
    p.add_argument("--boot", type=int, default=4000)
    a = p.parse_args()

    sat = {"full": load_sat(a.full), "core": load_sat(a.core)}
    joined = load_join(a.comparisons, a.rubrics)
    pairs, items = {}, {"full": {}, "core": {}}
    neg_share = {"full": [], "core": []}
    for pid, comp, rub in joined:
        hp = human_pairs(comp["metadata"]["assessments"])
        if not hp:
            continue
        pairs[pid] = hp
        for src, key in (("full", "coval_full"), ("core", "coval_core")):
            it = rub.get(key) or []
            if it:
                items[src][pid] = it
                sc = [float(np.mean([float(s["score"]) for s in (x.get("scores") or [])]))
                      for x in it if x.get("scores")]
                if sc:
                    neg_share[src].append(float(np.mean(np.array(sc) < 0)))

    print("=== the claim being tested, from the dataset card ===")
    print('  core "first rewrites all rubric items to have positive weight"\n')
    for src in ("full", "core"):
        print(f"  share of {src:4s} criteria with a NEGATIVE mean human rating: "
              f"{np.mean(neg_share[src]):.4f}  (over {len(neg_share[src]):,} prompts)")

    rng = np.random.default_rng(20260728)
    grid, series = {}, {}
    print(f"\n{'source':6s} {'weighting':10s} {'accuracy':>9} {'95% CI':>20} {'prompts':>8}")
    for src in ("full", "core"):
        for mode in ("equal", "sign", "signed_magnitude"):
            arr, pl = accuracy_series(sat[src], items[src], pairs, mode)
            if len(arr) < 30:
                continue
            bs = np.array([arr[rng.integers(0, len(arr), len(arr))].mean()
                           for _ in range(a.boot)])
            lo, hi = np.percentile(bs, [2.5, 97.5])
            grid.setdefault(src, {})[mode] = {
                "accuracy": float(arr.mean()), "ci": [float(lo), float(hi)],
                "prompts": int(len(arr))}
            series[(src, mode)] = (arr, pl)
            print(f"{src:6s} {mode:10s} {arr.mean():>9.4f} "
                  f"{f'[{lo:.4f}, {hi:.4f}]':>20} {len(arr):>8}")

    def paired(k1, k2):
        (a1, p1), (a2, p2) = series[k1], series[k2]
        common = sorted(set(p1) & set(p2))
        i1 = {p: i for i, p in enumerate(p1)}
        i2 = {p: i for i, p in enumerate(p2)}
        d = np.array([a2[i2[p]] - a1[i1[p]] for p in common])
        bs = np.array([d[rng.integers(0, len(d), len(d))].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return float(d.mean()), float(lo), float(hi), len(common)

    print("\n=== pre-registered predictions ===")
    tests = {
        "P1 core/equal >> full/equal": (("full", "equal"), ("core", "equal")),
        "P2 core/signed ~ core/equal": (("core", "equal"), ("core", "signed_magnitude")),
        "P3 full/signed ~ core/equal": (("full", "signed_magnitude"), ("core", "equal")),
    }
    res = {}
    for name, (k1, k2) in tests.items():
        if k1 not in series or k2 not in series:
            continue
        m, lo, hi, nn = paired(k1, k2)
        res[name] = {"delta": m, "ci": [lo, hi], "n": nn,
                     "excludes_zero": bool(lo > 0 or hi < 0)}
        print(f"  {name:30s} {m:>+8.4f}  [{lo:+.4f}, {hi:+.4f}]  n={nn}  "
              f"{'DIFFERENT' if (lo > 0 or hi < 0) else 'indistinguishable'}")

    p1 = res.get("P1 core/equal >> full/equal", {})
    p2 = res.get("P2 core/signed ~ core/equal", {})
    # A PREDICTION CANNOT FAIL IF ITS ARM NEVER RAN.  The first version reported
    # "PREDICTION P1 FAILS -- the rewriting does not relocate polarity", a
    # substantive scientific claim, on an arm that produced ZERO prompts because
    # core items have no `scores` field and every weight came out 0.0.  That is
    # the fourth conclusion string in one day to speak where it had nothing to
    # say.  An absent arm is UNVERIFIED, which is not a refutation.
    core_ran = ("core", "equal") in series and len(series[("core", "equal")][0]) >= 30
    if not core_ran:
        verdict = ("UNVERIFIED -- THE CORE ARM DID NOT RUN. No prediction here has been "
                   "tested, in either direction. Check that coval_core items were scored "
                   "and that their weights are defined; an arm that produces no prompts "
                   "refutes nothing.")
        print(f"\n  -> {verdict}")
        _RES.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps(
            {"status": "CORE_ARM_EMPTY", "grid": grid, "predictions": res,
             "verdict": verdict}, indent=1))
        print(f"\nwrote {a.out}")
        return
    verdict = (
        "CORE LAUNDERS POST-CHOICE POLARITY INTO TEXT. Scored with EQUAL weights -- no human "
        f"ratings used at all -- core beats full by {p1.get('delta', float('nan')):+.4f}, and "
        f"applying ratings to core adds {p2.get('delta', float('nan')):+.4f} more. The sign a "
        "participant supplied AFTER ranking the candidates now lives in the criterion's "
        "wording, where nothing marks it as post-choice. Core is the artifact most likely to "
        "be read as a clean, response-independent value specification -- readable, "
        "positively-phrased, four items -- and it is the one where that reading is least "
        "available."
        if p1.get("excludes_zero") and p1.get("delta", 0) > 0 else
        "PREDICTION P1 FAILS: core scored with equal weights does not beat full scored the "
        "same way, so the positive-weight rewriting does not, by itself, relocate the "
        "polarity information into the text. Whatever core does, this is not it.")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"negative_share": {k: float(np.mean(v)) for k, v in neg_share.items()},
         "grid": grid, "predictions": res, "verdict": verdict,
         "card_quote": "core 'first rewrites all rubric items to have positive weight' "
                       "(DATASET_CARD.md:74)",
         "scope": "Evaluation pairs come from the ORIGINAL rankings: internal concordance "
                  "on the elicitation manifold (entry 36). Both sources share that "
                  "limitation; the comparison is between them."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
