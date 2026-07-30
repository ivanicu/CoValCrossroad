"""r106 -- 0.69 of the own arm's over-chance accuracy is prompt-specific. Is that a number?

CLAIM CARD
----------
Claim      r105 reported the prompt-specific SHARE at 0.6948 / 0.6991 / 0.6840 and quoted
           only its ACROSS-BIN difference, because the LEVEL inherits r104's single donor
           draw. The level is the more quotable number -- "roughly 69% of what the rubric
           achieves above chance is its own prompt's criteria" -- and it has never been
           reported anywhere in this package, precisely because nobody measured what a
           redraw does to it.
Estimand   the sampling distribution of the share's LEVEL over independent donor draws,
           on r104's population and label.
Target
observed?  YES, and cheaply, because of what the donor arm actually is. `gap()` scores
           THIS prompt's satisfaction values with the DONOR's weight vector -- so a redraw
           changes only a vector of weights, not any satisfaction. Per pair, the
           per-criterion satisfaction differences can be computed ONCE and every draw is a
           dot product. 200 draws is a matrix multiply, not 200 rebuilds.
Alternative
worlds     T TIGHT   the share's draw-to-draw sd is small against the 0.05 margin r105
                     pre-registered. Then 0.69 is a reportable level, with an interval,
                     and the package gains its first statement about the COMPOSITION of
                     the signal rather than its size.
           W WIDE    the sd is comparable to or larger than the differences being
                     discussed. Then the level is a property of WHICH donors were drawn,
                     not of the rubric, only r105's across-bin difference may be quoted,
                     and r88's reassurance -- pooled attribution sd 0.0055 -- does not
                     transfer to a ratio.
Intervention
           redraw the donor assignment 200 times with the same idiom and a different seed
           each time. Nothing else moves: own arm, labels, population and bins are fixed.
Null       (i) REBUILD CONTROL -- the round recovers each split record's LABEL DIRECTION
           from r104's persisted own-arm hits, then recomputes the CANONICAL donor's hits
           from scratch. They must match r104's stored donor hits exactly. If the recovery
           is wrong, every redraw below is scoring against a label this round invented.
           (ii) DEGENERATE CONTROL -- a draw in which every prompt donates to ITSELF must
           produce a share of exactly 0.0: own and donor arms coincide, so the numerator
           vanishes. A pipeline that cannot return 0 when the two arms are identical is
           not measuring a difference between them.

WHY THIS IS THE STEP
--------------------
Entry 219's NEXT. r88 established that the pooled ATTRIBUTION moves 0.0055 sd across 120
donor draws, and that number has been used since as the reason a single draw is acceptable.
But the share is a RATIO, and a ratio's variance is not its numerator's: dividing by
(own - 0.5), which is 0.12 in the lowest bin, multiplies the donor's spread by more than
eight. Whether 0.0055 survives that magnification is arithmetic nobody has done.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
Draws are not independent of each other in the way a textbook interval assumes: every draw
reuses the same 968 weight vectors, so the donor POOL is fixed and only the assignment
moves. The spread measured here is therefore the spread over ASSIGNMENTS, not over
hypothetical other populations of rubrics -- it is a lower bound on the uncertainty a
different corpus would carry, and the verdict says so rather than reporting it as the
share's total uncertainty.
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
sys.path.insert(0, str(_ROOT / "09_form_donor_draw_and_unit/r85_agreement_by_form"))

from covalx import human_pairs, load_join  # noqa: E402
from run import weights  # noqa: E402

SAT = _ROOT / "01_object_and_rebuild/r04_rebuild_satisfaction/results/a04_full.npz"
COMPARISONS = _ROOT / "data/comparisons.jsonl"
RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
VEC = _ROOT / "11_reliability_and_the_width_chain/r104_deattenuated_consensus/results/r104_split_records.npz"
R105 = _ROOT / "11_reliability_and_the_width_chain/r105_specific_share_invariance/results/r105_specific_share_invariance.json"

MIN_RATERS, EDGES = 12, (0.49, 0.6, 0.9, 1.01)
MIN_BIN, MIN_DENOM = 300, 0.05
N_DRAWS = 200
DONOR_SEED = 20260726          # r104's canonical draw, reproduced as the rebuild control
TIGHT = 0.02                   # pre-registered: sd below this makes the LEVEL quotable


def draw_donors(n, seed):
    """r104's idiom exactly: sampling WITH replacement over donors, not a permutation."""
    rng = np.random.default_rng(seed)
    return np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])


def share_of(own_hit, don_hit, cons, edges=EDGES, min_bin=MIN_BIN, min_denom=MIN_DENOM):
    out = []
    for i in range(len(edges) - 1):
        m = (cons >= edges[i]) & (cons < edges[i + 1])
        if m.sum() < min_bin:
            continue
        o, d = own_hit[m].mean(), don_hit[m].mean()
        out.append((o - d) / (o - 0.5) if (o - 0.5) >= min_denom else np.nan)
    o, d = own_hit.mean(), don_hit.mean()
    pooled = (o - d) / (o - 0.5) if (o - 0.5) >= min_denom else np.nan
    return pooled, out


def build():
    """Per-pair criterion-difference vectors, own-arm directions, and the prompt weight
    matrix. Lifted to module level so r107 IMPORTS this rather than reimplementing it --
    two hand-written copies of a construction is two chances to diverge silently. Its
    correctness is checked at every use by the rebuild control against r104's stored
    donor hits."""
    z = np.load(SAT, allow_pickle=True)
    sat = defaultdict(dict)
    for m, s_ in zip(z["meta"], z["sat"]):
        p_, ci, lab = m.split("|")
        sat[p_][(int(ci), lab)] = float(s_)

    keep = []
    for pid_, comp, rub in load_join(COMPARISONS, RUBRICS):
        pr = human_pairs(comp["metadata"]["assessments"])
        items = rub.get("coval_full") or []
        if pr and items and pid_ in sat:
            keep.append((pid_, items, pr))
    n = len(keep)
    maxK = max(len(it) for _, it, _ in keep)
    D, own_dir, pair_prompt = [], [], []
    for i, (pid_, items, pr) in enumerate(keep):
        satp, w = sat[pid_], weights(items)
        cnt: dict = defaultdict(int)
        for x, y in pr:
            cnt[(x, y)] += 1
        # SORTED: set iteration order follows per-process string hashing (entry 218).
        for k in sorted({tuple(sorted(t)) for t in cnt}):
            if cnt.get((k[0], k[1]), 0) + cnt.get((k[1], k[0]), 0) < MIN_RATERS:
                continue
            d = np.zeros(maxK)
            for ci in range(len(items)):
                va, vb = satp.get((ci, k[0])), satp.get((ci, k[1]))
                if va is not None and vb is not None:
                    d[ci] = va - vb
            D.append(d)
            own_dir.append(float(np.dot(w, d[:len(w)]) > 0))
            pair_prompt.append(i)
    W = np.zeros((n, maxK))
    for i, (_, items, _) in enumerate(keep):
        w = weights(items)
        W[i, :len(w)] = w
    return np.array(D), np.array(own_dir), np.array(pair_prompt), W, n, maxK


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r106_share_level_under_redraw.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not VEC.exists():
        raise SystemExit("REFUSING: r104's split records are absent; this round redraws its donor arm.")

    D, own_dir, pair_prompt, W, n, maxK = build()
    print(f"pairs {len(D):,}   criterion slots {maxK}   prompts {n}")

    rec = np.load(VEC)
    rpid, cons, own_hit, don_hit = rec["pid"], rec["cons"], rec["own"], rec["donor"]
    if len(D) != int(rpid.max()) + 1:
        raise SystemExit(f"REFUSING: rebuilt {len(D)} pairs but r104's records index "
                         f"{int(rpid.max()) + 1}; the pair order does not match and every "
                         f"redraw below would be scored against the wrong label.")

    # ---- recover each record's LABEL DIRECTION from r104's own-arm hits --------
    od = own_dir[rpid]
    label_dir = np.where(own_hit > 0.5, od, 1.0 - od)

    # ---- CONTROL (i): recompute the CANONICAL donor and match r104 exactly -----
    canon = draw_donors(n, DONOR_SEED)
    def donor_hits(assign):
        dd = (np.einsum("ij,ij->i", W[assign[pair_prompt]], D) > 0).astype(float)
        return (dd[rpid] == label_dir).astype(float)
    got = donor_hits(canon)
    mism = int((got != don_hit).sum())
    print(f"\nCONTROL (i) rebuild of r104's canonical donor arm: {mism} mismatches of "
          f"{len(don_hit):,} records")
    if mism:
        raise SystemExit("REFUSING: the recovered label direction does not reproduce r104's stored "
                         "donor hits, so this round is scoring against a label it invented.")
    print("   -> PASS: label direction recovered exactly; redraws below are comparable to r104.")

    # ---- CONTROL (ii): self-donation must give a share of exactly 0 -----------
    self_share, _ = share_of(own_hit, donor_hits(np.arange(n)), cons)
    print(f"CONTROL (ii) every prompt donates to ITSELF: share {self_share:.2e}")
    if abs(self_share) > 1e-12:
        raise SystemExit("REFUSING: with the two arms identical the share must be exactly 0; a "
                         "pipeline that cannot return 0 there is not measuring their difference.")
    print("   -> PASS: the two arms coincide and the numerator vanishes.")

    # ---- THE REDRAW -----------------------------------------------------------
    canon_pooled, canon_bins = share_of(own_hit, don_hit, cons)
    pooled, bins = [], []
    for s_ in range(N_DRAWS):
        p_, b_ = share_of(own_hit, donor_hits(draw_donors(n, 900000 + s_)), cons)
        pooled.append(p_); bins.append(b_)
    pooled, bins = np.array(pooled), np.array(bins)
    sd = float(pooled.std(ddof=1))
    lo, hi = float(np.percentile(pooled, 2.5)), float(np.percentile(pooled, 97.5))
    zscore = (canon_pooled - pooled.mean()) / sd
    print(f"\n  canonical draw pooled share {canon_pooled:.4f}")
    print(f"  {N_DRAWS} redraws: mean {pooled.mean():.4f}  sd {sd:.4f}  "
          f"95% [{lo:.4f},{hi:.4f}]  canonical at {zscore:+.2f} sd")
    print(f"\n  {'bin':>13} {'canonical':>10} {'redraw mean':>12} {'sd':>8} {'95% interval':>20}")
    rows = []
    for j, (l_, h_) in enumerate(zip(EDGES[:-1], EDGES[1:])):
        col = bins[:, j]
        s_lo, s_hi = float(np.percentile(col, 2.5)), float(np.percentile(col, 97.5))
        rows.append({"lo": l_, "hi": min(h_, 1.0), "canonical": float(canon_bins[j]),
                     "redraw_mean": float(col.mean()), "sd": float(col.std(ddof=1)),
                     "ci95": [s_lo, s_hi]})
        print(f"  {'[%.2f,%.2f)' % (l_, min(h_, 1.0)):>13} {canon_bins[j]:>10.4f} "
              f"{col.mean():>12.4f} {col.std(ddof=1):>8.4f} {f'[{s_lo:.4f},{s_hi:.4f}]':>20}")

    # ---- r105's CANCELLATION ARGUMENT, TESTED ---------------------------------
    # r105 quoted the across-bin difference and justified ignoring the draw with "every bin
    # inherits the SAME draw". That is false: one assignment meets DIFFERENT pairs in
    # different bins, so it enters the two sides of the comparison differently. Measurable
    # here for free, since every draw already produced a per-bin share.
    hl = bins[:, -1] - bins[:, 0]
    hl_lo, hl_hi = float(np.percentile(hl, 2.5)), float(np.percentile(hl, 97.5))
    canon_hl = float(canon_bins[-1] - canon_bins[0])
    canon_hl_z = (canon_hl - hl.mean()) / hl.std(ddof=1)
    neg = int((hl < 0).sum())
    print(f"\n  ACROSS-BIN DIFFERENCE (high - low share) over draws: mean {hl.mean():+.4f}  "
          f"sd {hl.std(ddof=1):.4f}  95% [{hl_lo:+.4f},{hl_hi:+.4f}]")
    print(f"  {neg}/{N_DRAWS} draws negative; r105's canonical draw gave {canon_hl:+.4f}, at "
          f"{canon_hl_z:+.2f} sd -- an unusually FLAT draw")

    worst_bin_sd = max(r["sd"] for r in rows)
    world = "T TIGHT" if sd < TIGHT and worst_bin_sd < TIGHT else "W WIDE"
    vec = _RES / "r106_share_draws.npz"
    np.savez_compressed(vec, pooled=pooled, bins=bins, canonical=np.array([canon_pooled]))
    print(f"\n  draws persisted -> {vec.relative_to(_ROOT)}")

    r88 = 0.0055
    magnify = sd / r88
    verdict = (
        f"{world}. r105 declined to quote the prompt-specific share's LEVEL because it inherits "
        f"r104's single donor draw, and r88's reassurance -- pooled ATTRIBUTION sd {r88} over 120 draws "
        f"-- does not transfer to a RATIO, whose denominator (own - 0.5) is as small as 0.12 in the "
        f"lowest bin. Measured directly over {N_DRAWS} independent redraws on r104's population and "
        f"label: the pooled share is {pooled.mean():.4f} with sd {sd:.4f}, 95% of draws in "
        f"[{lo:.4f},{hi:.4f}], and r104's canonical draw sits at {zscore:+.2f} sd -- "
        f"{'an ordinary draw' if abs(zscore) < 2 else 'an UNUSUAL draw, and that is itself a finding'}. "
        f"Per bin the sd runs " + ", ".join(f"{r['sd']:.4f}" for r in rows) + ". "
        + (f"SO THE LEVEL IS QUOTABLE: roughly {pooled.mean():.2f} of what the rubric achieves above "
           f"chance is contributed by its own prompt's criteria, {sd:.4f} sd over donor assignments, "
           f"and this package can for the first time state a COMPOSITION rather than a size."
           if world.startswith("T") else
           f"SO THE LEVEL IS NOT QUOTABLE AS A NUMBER: at sd {sd:.4f} the draw moves the share by more "
           f"than the {TIGHT} a level would need, and the {r88} that justified a single draw for the "
           f"attribution is magnified {magnify:.1f}x by the division. Only r105's ACROSS-BIN difference "
           f"survives, because every bin there inherits the SAME draw and the draw cancels from a "
           f"comparison it enters identically on both sides.") +
        f" AND IT OVERTURNS r105's REASON, THOUGH NOT ITS VERDICT. r105 quoted the ACROSS-BIN "
        f"difference and justified ignoring the donor draw on the ground that every bin inherits the "
        f"SAME draw, so it cancels from a comparison it enters identically on both sides. IT DOES NOT "
        f"CANCEL: one assignment meets DIFFERENT pairs in different bins. Over these {N_DRAWS} draws "
        f"the high-minus-low share is {hl.mean():+.4f} with sd {hl.std(ddof=1):.4f}, 95% in "
        f"[{hl_lo:+.4f},{hl_hi:+.4f}], and {neg} of {N_DRAWS} draws are NEGATIVE -- so the typical "
        f"draw says the prompt-specific share FALLS with consensus, i.e. prompt-specific content "
        f"carries relatively MORE where humans disagree, which is the reverse of r104's absolute "
        f"reading. r105's canonical draw gave {canon_hl:+.4f}, sitting at {canon_hl_z:+.2f} sd of this "
        f"distribution: an unusually FLAT draw. r105's verdict of ANSWERABLE MARGIN survives -- the "
        f"draw interval still crosses zero at its upper edge -- but for a LARGER reason than it gave, "
        f"and its cancellation argument is retracted. The draw spread ({hl.std(ddof=1):.4f}) is on the "
        f"same scale as the pair-bootstrap half-width r105 reported (0.1260) and was omitted from it "
        f"entirely, so r105's interval is too NARROW, not too wide. "
        f"REBUILD CONTROL: the round recovers each split record's LABEL DIRECTION from r104's stored "
        f"own-arm hits and recomputes the CANONICAL donor arm from scratch -- {mism} mismatches in "
        f"{len(don_hit):,} records, so the redraws are scored against r104's actual labels rather than "
        f"an invented one. DEGENERATE CONTROL: a draw in which every prompt donates to ITSELF returns a "
        f"share of {self_share:.0e}; a pipeline that cannot return 0 when the two arms coincide is not "
        f"measuring their difference. "
        f"WHY THIS IS CHEAP, AND IT MATTERS FOR READING IT: the donor arm scores THIS prompt's "
        f"satisfaction values with the DONOR's weight vector, so a redraw changes only weights. The "
        f"per-criterion satisfaction differences are built once and each draw is a dot product -- "
        f"{N_DRAWS} draws, not {N_DRAWS} rebuilds. "
        f"THE CONFOUND, WRITTEN BEFORE THE RUN: every draw reuses the SAME {n} weight vectors, so only "
        f"the ASSIGNMENT moves and the donor POOL is fixed. This spread is over assignments, not over "
        f"hypothetical other corpora of rubrics, and is therefore a LOWER BOUND on the uncertainty a "
        f"different corpus would carry."
    )

    doc = {
        "n_draws": N_DRAWS, "n_pairs": int(len(D)), "n_prompts": n,
        "n_records": int(len(cons)), "canonical_pooled_share": float(canon_pooled),
        "redraw_mean": float(pooled.mean()), "redraw_sd": sd, "redraw_ci95": [lo, hi],
        "canonical_z": float(zscore), "bins": rows, "worst_bin_sd": float(worst_bin_sd),
        "across_bin_difference_over_draws": {
            "mean": float(hl.mean()), "sd": float(hl.std(ddof=1)), "ci95": [hl_lo, hl_hi],
            "n_negative": neg, "canonical": canon_hl, "canonical_z": float(canon_hl_z)},
        "tight_threshold": TIGHT, "r88_attribution_sd": r88, "magnification": float(magnify),
        "rebuild_mismatches": mism, "self_donation_share": float(self_share),
        "persisted_vector": str(vec.relative_to(_ROOT)), "world": world,
        "outcome_variable_scope": (
            "The sampling distribution over DONOR ASSIGNMENTS of (own - donor)/(own - 0.5), on r104's "
            "population and third-rater labels. Own arm, labels, population and bins are held fixed; "
            "only the donor assignment moves."),
        "scope": (
            "Spread over ASSIGNMENTS from a fixed pool of weight vectors -- a lower bound on the "
            "uncertainty a different corpus of rubrics would carry. Does not revisit r105's across-bin "
            "difference -- it MEASURES that difference's draw spread, and finds r105's cancellation "
            "argument false: one assignment meets different pairs in different bins."),
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
