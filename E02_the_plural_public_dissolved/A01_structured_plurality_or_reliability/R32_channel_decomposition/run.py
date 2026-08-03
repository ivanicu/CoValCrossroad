"""r32 -- Where does the local signal enter: the criterion TEXT, or the post-choice WEIGHTS?

The question an external review made unavoidable
------------------------------------------------
CoVal's protocol is sequential. Participants ranked four candidate responses
FIRST, and only then were shown six seeded criteria, rated them, and could write
their own. So even when a criterion's SENTENCE predates the candidates, its
RATING does not: the sign and magnitude attached to it were produced by someone
who had already chosen.

    Y_0  ->  A (their ranking)  ->  W (their criterion ratings)  ->  R (rubric)

r13 concluded "response-set knowledge is not the mechanism" on the strength of
seed criteria carrying attribution. That conclusion is withdrawn (entry 38),
partly because it never separated the channels. This round separates them.

The factorial
-------------
Every arm scores the SAME responses with the SAME judge satisfaction matrix,
already computed and saved by r04. Only the WEIGHTS change. No GPU, no new
judgements -- which is the point: if the answer moves, it moves because of what
the weights carry, not because anything was re-measured.

    provenance   seed (rated by a majority) | writein (single rater) | all
                the split is structural, not a threshold choice: r48 finds a
                clean gap and a fixed 6-per-prompt seeded set, so no
                threshold-sensitivity sweep is owed here
    weighting    equal            w_c = 1                       text only
                 sign             w_c = sign(mean rating)       + polarity
                 signed magnitude w_c = mean rating             + how much
                 + visibility     w_c = mean rating * n_raters  + who saw it

    score(r) = SUM_c w_c * sat[c,r] / SUM_c |w_c|

Reading it
----------
* If EQUAL already matches SIGNED, the post-choice weights contribute nothing
  and r13's text-only reading survives on this axis.
* If SIGN adds a lot, polarity is doing the work -- and polarity is post-choice.
  It is also the channel r04 and r13 silently dropped: an unweighted mean treats
  a criterion the raters marked NEGATIVE ("the model should not moralise") as
  something a good response should satisfy.
* If MAGNITUDE adds beyond SIGN, the graded post-choice weight is a channel.
* If VISIBILITY adds beyond that, seeding itself is a channel.

Scope, stated because entry 36 exists
--------------------------------------
The evaluation pairs come from the ORIGINAL rankings, on the same four candidates
these criteria were written and rated against. This is INTERNAL CONCORDANCE on
the elicitation manifold, not out-of-sample validation. Differences BETWEEN arms
are the object here, and every arm shares that limitation equally, so the
comparison is fair even though no arm's absolute number is transportable.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import human_pairs, load_join  # noqa: E402

WEIGHTINGS = ("equal", "sign", "signed_magnitude", "signed_mag_x_visibility")
PROVENANCE = ("all", "seed", "writein")


def criterion_weights(items, mode):
    """One weight per criterion index, from the HUMAN ratings only."""
    w, prov = [], []
    n_raters = {s["annotator_id"] for it in items for s in (it.get("scores") or [])}
    thr = max(2, (len(n_raters) + 1) // 2)
    for it in items:
        sc = [float(s["score"]) for s in (it.get("scores") or [])]
        if not sc:
            w.append(0.0), prov.append("none")
            continue
        mean = float(np.mean(sc))
        n = len(sc)
        prov.append("seed" if n >= thr else "writein")
        if mode == "equal":
            w.append(1.0)
        elif mode == "sign":
            w.append(float(np.sign(mean)) or 1.0)
        elif mode == "signed_magnitude":
            w.append(mean)
        elif mode == "signed_mag_x_visibility":
            w.append(mean * n)
        else:
            raise ValueError(mode)
    return np.array(w, dtype=float), prov


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--sat", type=Path,
                   default=_ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results/a04_full.npz")
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--out", type=Path, default=_RES / "r32_channel_decomposition.json")
    p.add_argument("--boot", type=int, default=4000)
    a = p.parse_args()

    z = np.load(a.sat, allow_pickle=True)
    sat = defaultdict(dict)                       # pid -> (ci, lab) -> satisfaction
    for m, s in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s)

    joined = load_join(a.comparisons, a.rubrics)
    pairs, rub_items = {}, {}
    for pid, comp, rub in joined:
        hp = human_pairs(comp["metadata"]["assessments"])
        it = rub.get("coval_full") or []
        if hp and it and pid in sat:
            pairs[pid] = hp
            rub_items[pid] = it
    print(f"prompts with satisfaction + rankings: {len(pairs):,}\n")

    rng = np.random.default_rng(20260728)
    grid = {}
    print(f"{'provenance':11s} {'weighting':24s} {'accuracy':>9} {'95% CI':>20} "
          f"{'prompts':>8} {'crit':>7}")
    per_prompt_store = {}
    for prov in PROVENANCE:
        for mode in WEIGHTINGS:
            accs, ncrit = [], []
            for pid, items in rub_items.items():
                w, pv = criterion_weights(items, mode)
                keep = np.array([(prov == "all" or pv[i] == prov) and abs(w[i]) > 0
                                 for i in range(len(w))])
                if keep.sum() < 2:
                    continue
                score = {}
                for lab in {l for (_c, l) in sat[pid]}:
                    num = den = 0.0
                    for ci in np.where(keep)[0]:
                        s = sat[pid].get((int(ci), lab))
                        if s is None:
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
                    ncrit.append(int(keep.sum()))
            arr = np.array(accs)
            if len(arr) < 30:
                continue
            bs = np.array([arr[rng.integers(0, len(arr), len(arr))].mean()
                           for _ in range(a.boot)])
            lo, hi = np.percentile(bs, [2.5, 97.5])
            grid.setdefault(prov, {})[mode] = {
                "accuracy": float(arr.mean()), "ci": [float(lo), float(hi)],
                "prompts": int(len(arr)), "mean_criteria": float(np.mean(ncrit))}
            per_prompt_store[(prov, mode)] = arr
            print(f"{prov:11s} {mode:24s} {arr.mean():>9.4f} "
                  f"{f'[{lo:.4f}, {hi:.4f}]':>20} {len(arr):>8} {np.mean(ncrit):>7.1f}")

    print("\n=== channel contributions (paired on prompts, within provenance) ===")
    print(f"{'provenance':11s} {'channel':34s} {'delta':>9} {'95% CI':>20}")
    channels = {}
    steps = [("polarity  (equal -> sign)", "equal", "sign"),
             ("magnitude (sign -> signed_magnitude)", "sign", "signed_magnitude"),
             ("visibility(signed_mag -> x n_raters)", "signed_magnitude",
              "signed_mag_x_visibility")]
    for prov in PROVENANCE:
        for name, lo_m, hi_m in steps:
            A_, B_ = per_prompt_store.get((prov, lo_m)), per_prompt_store.get((prov, hi_m))
            if A_ is None or B_ is None or len(A_) != len(B_):
                continue
            d = B_ - A_
            bs = np.array([d[rng.integers(0, len(d), len(d))].mean()
                           for _ in range(a.boot)])
            lo, hi = np.percentile(bs, [2.5, 97.5])
            channels.setdefault(prov, {})[name] = {
                "delta": float(d.mean()), "ci": [float(lo), float(hi)],
                "excludes_zero": bool(lo > 0 or hi < 0)}
            flag = "" if (lo > 0 or hi < 0) else "   (spans zero)"
            print(f"{prov:11s} {name:34s} {d.mean():>+9.4f} "
                  f"{f'[{lo:+.4f}, {hi:+.4f}]':>20}{flag}")

    pol = channels.get("all", {}).get("polarity  (equal -> sign)", {})
    verdict = (
        f"POST-CHOICE POLARITY IS A CHANNEL: moving from an unweighted mean to the "
        f"human-rated SIGN moves accuracy by {pol.get('delta', float('nan')):+.4f} "
        f"{pol.get('ci')}. That sign was supplied after the rater had already ranked the "
        "candidates, so a rubric score built on it is not response-blind however early "
        "the sentence was written. It is also a channel r04 and r13 dropped entirely: an "
        "unweighted mean rewards a response for satisfying a criterion the raters marked "
        "NEGATIVE."
        if pol.get("excludes_zero") else
        "POLARITY IS NOT A CHANNEL HERE: weighting by the human-rated sign does not move "
        "accuracy beyond sampling error, so on this axis the local signal is carried by "
        "criterion TEXT rather than by post-choice ratings. That is the one channel this "
        "round can close; viewpoint-scaffold and manifold dependence remain open.")
    print(f"\n  -> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(
        {"prompts": len(pairs), "grid": grid, "channels": channels, "verdict": verdict,
         "scope": "Evaluation pairs come from the ORIGINAL rankings on the same four "
                  "candidates these criteria were rated against. Internal concordance on "
                  "the elicitation manifold, not out-of-sample validation (entry 36). "
                  "Differences BETWEEN arms are the object; every arm shares the "
                  "limitation equally."},
        indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
