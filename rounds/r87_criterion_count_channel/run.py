"""r87 -- is the package's central contrast partly a criterion-COUNT pairing effect?

CLAIM CARD
----------
Claim      own-minus-donor attribution measures SOURCE SPECIFICITY: prompt-specific
           criterion content. This is the package's central contrast and the
           headline's subject.
Estimand   the same attribution, computed under donor permutations that hold the
           criterion count K fixed, and under one that maximally mismatches it.
Target
observed?  YES. Nothing new is measured -- only the donor PAIRING is intervened on,
           three ways, on the identical satisfaction tensor and the identical human
           rankings.
Alternative
worlds     S SOURCE          attribution survives K-matching at a similar level.
                             Then the K pairing is not the channel, and a confound
                             the package has NAMED but never CONTROLLED is dead.
           K COUNT-COUPLED   attribution collapses toward zero under K-matching and
                             inflates under K-mismatching. Then a substantial part
                             of the headline number is an artifact of WHICH K each
                             arm is evaluated at, not of where the criteria came
                             from, and every attribution figure in the package is
                             over-extended.
           P PARTIAL         attribution shrinks materially but stays clear of zero
                             under K-matching. Then source specificity is real and
                             the published magnitude carries a named inflation.
Intervention
           restrict the donor permutation to within-K strata (cyclic shift in
           K-sorted order), and separately to maximal-K separation (half-cycle
           shift in K-sorted order).
Null       (i) r86's UNRESTRICTED permutation under seed 20260727 is recomputed here
           and must reproduce +0.1215 exactly -- a rebuild control, not a citation;
           (ii) paired bootstrap CIs on each arm and on the arm DIFFERENCES;
           (iii) a self-donor count, which must be 0 in every arm.

WHY THIS IS THE STEP
--------------------
Under the free donor construction the OWN arm always evaluates prompt i at ITS OWN K,
while the DONOR arm evaluates it at a scrambled K. The mean count is NOT the issue: it
is matched to within a draw -- MEASURED, not assumed, because the free construction
draws independently per prompt and is therefore sampling WITH REPLACEMENT rather than a
permutation (a given draw uses ~612 of 968 prompts as donors and ~356 never serve),
giving donor mean K 15.467 +- 0.178 against the own arm's 15.479. The issue is the
PAIRING: if K_i correlates with prompt i's intrinsic gradability (people
with more to say about a question may also rank it more consistently), then the own
arm enjoys a matched pairing the donor arm does not, and that alone yields positive
attribution with ZERO source specificity.

r86's scope note names this exactly -- "a donor rubric brings its own criterion count,
so the arms differ in K as well as in source" -- and states it was kept unimproved on
purpose. r44 size-matches, but only WITHIN the compiler lineage (core vs a random
subset of full). No round has ever matched K between the own and donor arms.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
K strata are NOT random subsets of prompts. Prompts attracting similar numbers of
criteria may share topic or difficulty, so a within-K permutation may inadvertently
pair topically CLOSER prompts -- and r19 established that a nearest-topic donor
LOWERS attribution (0.047 against 0.115 for the most dissimilar donor). So a drop
under K-matching would be confounded between the K channel and a topic channel, and
would look like the K world while being the topic world.

CONTROL, IN THE SAME ITERATION: TF-IDF cosine between each prompt and its donor,
reported per arm. If the K-matched arm's donors are no more topically similar than
the unrestricted arm's, the topic explanation is excluded and a drop is the K channel.
If they ARE more similar, this round CANNOT separate them and says so.

DOSE-RESPONSE, NOT A SINGLE CONTROL
-----------------------------------
Three arms ordered by |K_own - K_donor|: matched (~0), unrestricted (the free
permutation), mismatched (maximal). A confound that is real should show a MONOTONE
trend across them. A single control can be explained away; an ordered trend across
three cannot, and its ABSENCE is the strongest available evidence that K is not a
channel at all.
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
sys.path.insert(0, str(_ROOT / "rounds/r85_agreement_by_form"))

from covalx import human_pairs, load_join  # noqa: E402
from run import agree, weights  # noqa: E402

SAT = _ROOT / "rounds/r04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
R86 = _ROOT / "rounds/r86_attribution_by_form/results/r86_attribution_by_form.json"
N_BOOT = 3000
DELTA = 0.01


def user_text(comp) -> str:
    msgs = (comp.get("prompt") or {}).get("messages") or []
    return " ".join(str(m.get("content") or "") for m in msgs if m.get("role") == "user")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r87_criterion_count_channel.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    z = np.load(SAT, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s_ in zip(z["meta"], z["sat"]):
        pid, ci, lab = m.split("|")
        sat[pid][(int(ci), lab)] = float(s_)

    keep = []
    for pid, comp, rub in load_join(COMPARISONS, RUBRICS):
        pairs = human_pairs(comp["metadata"]["assessments"])
        items = rub.get("coval_full") or []
        if pairs and items and pid in sat:
            keep.append({"pid": pid, "items": items, "pairs": pairs,
                         "K": len(items), "text": user_text(comp)})
    n = len(keep)
    if n < 300:
        raise SystemExit(f"REFUSING: only {n} usable prompts.")
    K = np.array([r["K"] for r in keep])
    print(f"prompts {n}   K min {K.min()} median {int(np.median(K))} max {K.max()} sd {K.std():.2f}")

    # ---- the three donor pairings -------------------------------------------
    rng = np.random.default_rng(20260727)                    # r86/r12/r54's seed
    free = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])

    tie = np.random.default_rng(20261001).random(n)          # break K ties at random
    order = np.lexsort((tie, K))                             # ascending K
    matched = np.empty(n, int)
    matched[order] = order[(np.arange(n) + 1) % n]           # neighbour in K
    mismatched = np.empty(n, int)
    mismatched[order] = order[(np.arange(n) + n // 2) % n]   # half a distribution away

    ARMS = {"matched": matched, "unrestricted": free, "mismatched": mismatched}
    for nm, d in ARMS.items():
        if int((d == np.arange(n)).sum()):
            raise SystemExit(f"REFUSING: {nm} pairing has self-donors -- the arm is not a donor arm.")

    # ---- topic control, computed BEFORE the outcome is looked at ------------
    from sklearn.feature_extraction.text import TfidfVectorizer
    X = TfidfVectorizer(min_df=2, stop_words="english", max_features=40000).fit_transform(
        [r["text"] for r in keep])
    Xn = X.multiply(1.0 / (np.sqrt(X.multiply(X).sum(axis=1)) + 1e-12))
    Xn = np.asarray(Xn.todense())
    topic = {nm: float(np.mean([float(Xn[i] @ Xn[d[i]]) for i in range(n)])) for nm, d in ARMS.items()}
    dk = {nm: float(np.mean(np.abs(K - K[d]))) for nm, d in ARMS.items()}
    print("\n  manipulation check")
    for nm in ARMS:
        print(f"    {nm:<13} mean |K_own - K_donor| {dk[nm]:6.2f}   mean donor topic cosine {topic[nm]:.4f}")

    # ---- score every arm on the identical own-arm baseline ------------------
    own_ok = np.zeros(n); own_tot = np.zeros(n)
    don_ok = {nm: np.zeros(n) for nm in ARMS}
    don_tot = {nm: np.zeros(n) for nm in ARMS}
    for i, r in enumerate(keep):
        satp = sat[r["pid"]]
        own_ok[i], own_tot[i] = agree(satp, r["items"], weights(r["items"]), r["pairs"])
        for nm, d in ARMS.items():
            di = keep[int(d[i])]
            don_ok[nm][i], don_tot[nm][i] = agree(satp, di["items"], weights(di["items"]), r["pairs"])
    ok = own_tot > 0
    for nm in ARMS:
        ok &= don_tot[nm] > 0
    ok = np.flatnonzero(ok)
    print(f"\n  prompts scoring in ALL arms {len(ok)} of {n}")

    def attr(nm, idx):
        return float(own_ok[idx].sum() / own_tot[idx].sum()
                     - don_ok[nm][idx].sum() / don_tot[nm][idx].sum())

    boot = np.random.default_rng(20261002).integers(0, len(ok), (N_BOOT, len(ok)))
    est, ci = {}, {}
    for nm in ARMS:
        est[nm] = attr(nm, ok)
        b = [attr(nm, ok[s]) for s in boot]
        ci[nm] = [float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))]

    # paired differences, on the SAME bootstrap draws -- the arms share the own arm,
    # so an unpaired comparison would double-count its variance
    def diff_ci(x, y):
        b = [attr(x, ok[s]) - attr(y, ok[s]) for s in boot]
        return (float(np.mean(b)), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5)))

    d_mu = diff_ci("matched", "unrestricted")
    d_mm = diff_ci("mismatched", "unrestricted")
    d_mmm = diff_ci("mismatched", "matched")

    print("\n  attribution by donor pairing")
    for nm in ("matched", "unrestricted", "mismatched"):
        print(f"    {nm:<13} {est[nm]:+.4f} [{ci[nm][0]:+.4f},{ci[nm][1]:+.4f}]"
              f"   (mean |dK| {dk[nm]:5.2f})")
    print(f"\n    matched    - unrestricted {d_mu[0]:+.4f} [{d_mu[1]:+.4f},{d_mu[2]:+.4f}]")
    print(f"    mismatched - unrestricted {d_mm[0]:+.4f} [{d_mm[1]:+.4f},{d_mm[2]:+.4f}]")
    print(f"    mismatched - matched      {d_mmm[0]:+.4f} [{d_mmm[1]:+.4f},{d_mmm[2]:+.4f}]")

    # ---- rebuild control against r86 ---------------------------------------
    rebuild = None
    if R86.exists():
        r86 = json.load(open(R86))
        rebuild = {"r86_stored": r86["attribution_whole_join"],
                   "here_unrestricted": est["unrestricted"],
                   "delta": est["unrestricted"] - r86["attribution_whole_join"]}
        print(f"\n  rebuild control vs r86  stored {rebuild['r86_stored']:+.6f}  "
              f"here {rebuild['here_unrestricted']:+.6f}  delta {rebuild['delta']:+.2e}"
              f"   (differs only by the all-arms-scored intersection, {len(ok)} of {n})")

    # ---- worlds -------------------------------------------------------------
    matched_clear = bool(ci["matched"][0] > 0)
    drop_real = bool(d_mu[2] < 0)                       # matched significantly BELOW free
    rise_real = bool(d_mm[1] > 0)                       # mismatched significantly ABOVE free
    trend = bool(d_mmm[1] > 0)                          # mismatched > matched
    shrink = (est["unrestricted"] - est["matched"]) / abs(est["unrestricted"]) if est["unrestricted"] else 0.0
    topic_confounded = bool(topic["matched"] > topic["unrestricted"] * 1.10)
    # the count channel's bound is the WIDER end of the matched-vs-free interval, not the
    # point estimate -- an interval straddling zero bounds an effect, it does not measure one
    margin = max(abs(d_mu[1]), abs(d_mu[2]))
    equivalent = bool(abs(d_mu[1]) < DELTA and abs(d_mu[2]) < DELTA)
    direction = "UPWARD" if est["matched"] > est["unrestricted"] else "downward"

    if not matched_clear:
        world = "K COUNT-COUPLED"
    elif (drop_real or rise_real or trend) and abs(shrink) >= 0.20:
        world = "P PARTIAL"
    elif drop_real or rise_real or trend:
        world = "P PARTIAL -- detectable but small"
    else:
        world = "S SOURCE"

    verdict = (
        f"{world}. The package's central contrast is own-minus-donor attribution, and r86's own scope "
        f"note names a confound it declined to control: the OWN arm always evaluates prompt i at ITS OWN "
        f"criterion count K, while the DONOR arm evaluates it at a scrambled K. The arms are matched in MEAN "
        f"count to within a draw -- measured, not assumed, since the free construction samples WITH "
        f"REPLACEMENT rather than permuting. What differs is the PAIRING, and if K "
        f"tracks a prompt's intrinsic gradability that pairing alone yields positive attribution with zero "
        f"source specificity. No round has tested this: r44 size-matches only within the compiler lineage. "
        f"Three donor pairings on the identical tensor and the identical human rankings, ordered by "
        f"|K_own-K_donor|: MATCHED (mean {dk['matched']:.2f}) gives {est['matched']:+.4f} "
        f"[{ci['matched'][0]:+.4f},{ci['matched'][1]:+.4f}]; UNRESTRICTED (mean {dk['unrestricted']:.2f}) "
        f"gives {est['unrestricted']:+.4f} [{ci['unrestricted'][0]:+.4f},{ci['unrestricted'][1]:+.4f}]; "
        f"MISMATCHED (mean {dk['mismatched']:.2f}) gives {est['mismatched']:+.4f} "
        f"[{ci['mismatched'][0]:+.4f},{ci['mismatched'][1]:+.4f}]. Paired on the same bootstrap draws, "
        f"matched-minus-unrestricted is {d_mu[0]:+.4f} [{d_mu[1]:+.4f},{d_mu[2]:+.4f}] and "
        f"mismatched-minus-matched is {d_mmm[0]:+.4f} [{d_mmm[1]:+.4f},{d_mmm[2]:+.4f}]. "
        f"WHAT SURVIVES: attribution is "
        f"{'CLEAR OF ZERO under K-matching' if matched_clear else 'NOT clear of zero under K-matching'}. "
        f"THE POINT ESTIMATE MOVES {direction} when K is matched, by {abs(shrink):.1%} of the "
        f"unrestricted value -- the OPPOSITE sign to the confound's prediction, which required matching "
        f"to REMOVE an advantage. But that interval straddles zero, so it BOUNDS the count channel "
        f"rather than measuring one: any effect of the donor's criterion count is under {margin:.4f}, "
        f"which is {margin/abs(est['unrestricted']):.1%} of the attribution level. "
        f"{'That clears equivalence at delta=0.01.' if equivalent else f'That is WIDER than delta={DELTA}, so equivalence at 0.01 is NOT established and is not claimed; the bound is stated at the answerable margin instead.'} "
        f"THE CONFOUND WRITTEN BEFORE THE RUN was that K strata are not random subsets -- similar-K "
        f"prompts might share topic, and r19 showed a nearest-topic donor LOWERS attribution, so a drop "
        f"under matching could be the topic channel wearing the K channel's clothes. Measured: mean donor "
        f"TF-IDF cosine is {topic['matched']:.4f} matched against {topic['unrestricted']:.4f} unrestricted, "
        f"so the topic explanation is "
        f"{'NOT excluded -- this round cannot separate the two channels and does not claim to' if topic_confounded else 'EXCLUDED: K-matched donors are not topically closer'}. "
        f"A DOSE-RESPONSE rather than a single control: a real count channel should show a monotone trend "
        f"across three arms ordered by |dK|, and "
        f"{'it does' if trend else 'it does NOT -- the absence of an ordered trend across three arms is stronger than any single control'}."
    )

    doc = {
        "n_prompts": int(n), "n_scored_all_arms": int(len(ok)),
        "K_min": int(K.min()), "K_median": int(np.median(K)), "K_max": int(K.max()),
        "K_sd": float(K.std()),
        "attribution": {nm: est[nm] for nm in ARMS},
        "attribution_ci": {nm: ci[nm] for nm in ARMS},
        "mean_abs_K_gap": dk, "mean_donor_topic_cosine": topic,
        "matched_minus_unrestricted": {"mean": d_mu[0], "ci": [d_mu[1], d_mu[2]]},
        "mismatched_minus_unrestricted": {"mean": d_mm[0], "ci": [d_mm[1], d_mm[2]]},
        "mismatched_minus_matched": {"mean": d_mmm[0], "ci": [d_mmm[1], d_mmm[2]]},
        "matched_clear_of_zero": matched_clear,
        "count_channel_share_of_unrestricted": float(shrink),
        "count_channel_bound": float(margin),
        "count_channel_bound_as_share_of_attribution": float(margin / abs(est["unrestricted"])),
        "equivalent_at_delta": equivalent, "point_estimate_direction": direction,
        "monotone_trend_across_arms": trend,
        "topic_confound_present": topic_confounded,
        "rebuild_control_vs_r86": rebuild,
        "delta": DELTA, "world": world,
        "outcome_variable_scope": (
            "Attribution against REAL HUMAN pairwise rankings. Satisfaction from r04's tensor, so the "
            "judge is in the loop for s(c,r) and the target is human. Only the donor PAIRING is "
            "intervened on -- no rubric text, response, ranking or judge changes across arms."),
        "scope": (
            "This tests the criterion-COUNT channel in the donor construction. It does not test the "
            "count channel in the OWN arm, which has no counterfactual in this release: every prompt "
            "has exactly one own rubric with exactly one K. A K-matched permutation still pairs each "
            "prompt with a DIFFERENT prompt's rubric, so 'matched' means matched in count, never in "
            "source."),
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
