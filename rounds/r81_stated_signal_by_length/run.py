"""r81 -- r03's equivalence averages two strata differing by ten times the effect. Test the strata.

CLAIM CARD
----------
Claim      r03, as recomputed in entry 139: a rater's own stated ideals predict
           their own choice 0.5033 against a permuted null of 0.5016, difference
           +0.0017 [-0.0061,+0.0097] -- EQUIVALENT to chance at delta=0.01.
Estimand   the same difference computed SEPARATELY for judgements where the
           rater's top pick is the longer response and where it is the shorter,
           each against its own within-stratum permuted null, plus the gap
           between them with an interval.
Target
observed?  YES, and it is the same computation r03 already runs -- r03 prints the
           two hit rates and stores them, but never gives either a null, an
           interval, or a test. The numbers exist; the inference does not.
Alternative
worlds     L LENGTH-CONDITIONAL  the longer-stratum difference clears zero while
                                 the shorter does not, and the gap has an
                                 interval excluding zero. Then r03's aggregate
                                 equivalence HIDES a real signal, stated ideals
                                 do predict choices in one stratum, and what they
                                 predict is plausibly length -- the same channel
                                 r47 found in the gold head.
           A AVERAGE-IS-HONEST   both strata sit at their own nulls and the gap's
                                 interval covers zero. Then r03's aggregate is a
                                 fair summary and the +0.0235 split is noise.
           S SPLIT-BUT-NULL      the gap excludes zero but NEITHER stratum clears
                                 its own null -- the strata differ from each other
                                 while both remain at chance, which would make the
                                 gap a fact about the nulls rather than about
                                 prediction.
Intervention
           none. Recomputation, stratified.
Null       r03's own C1 control, applied WITHIN each stratum: the same prompt,
           the same response pair, a DIFFERENT person's stated text. Computing the
           null per stratum is the point -- a pooled null would import the other
           stratum's baseline and could manufacture a difference where the strata
           merely have different chance levels.

WHY THIS EXISTS
---------------
Entry 139 recomputed r03's verdict and surfaced this: the top pick is the longer
response in 55.5% of judgements, and the hit rate splits 0.5138 against 0.4903 --
a gap of +0.0235, more than TEN TIMES the aggregate difference of +0.0017. I
wrote that into the verdict, the README row and the retraction entry, and tested
it in none of them. An equivalence claim that averages over two strata differing
by ten times the effect is not yet an equivalence claim.

SCOPE, BEFORE THE RUN
---------------------
Bootstrap is CLUSTERED ON ANNOTATOR: 1,007 annotators supply 11,327 judgements.
⚠ An earlier draft of this note said r03's own interval is judgement-level and
therefore not comparable. **That was wrong** -- r03 builds `by_ann` and resamples
raters, so it already clusters. The intervals here ARE comparable to r03's, and
the claim that they were not was written about another round's code without
reading it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

from covalx import parse_ranking  # noqa: E402

COMPARISONS = _ROOT / "data/comparisons.jsonl"
ANNOTATORS = _ROOT / "data/annotators.jsonl"
DELTA = 0.01
N_BOOT = 3000


def sim(u, v) -> float:
    num = (u.multiply(v)).sum()
    den = np.sqrt(u.multiply(u).sum()) * np.sqrt(v.multiply(v).sum())
    return float(num / den) if den > 0 else 0.0


def clustered(vals, aids, rng, reps=N_BOOT):
    """Bootstrap over ANNOTATORS, resampling whole raters."""
    uniq = np.unique(aids)
    idx = {a: np.flatnonzero(aids == a) for a in uniq}
    out = []
    for _ in range(reps):
        take = np.concatenate([idx[a] for a in rng.choice(uniq, len(uniq), replace=True)])
        out.append(vals[take].mean())
    return float(np.percentile(out, 2.5)), float(np.percentile(out, 97.5))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r81_stated_signal_by_length.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)

    stated = {}
    for line in open(ANNOTATORS, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        txt = str((rec.get("demographics") or {}).get("ideal-model-behavior") or "").strip()
        if len(txt) >= 20:
            stated[rec["annotator_id"]] = txt

    responses, judgements = {}, []
    for line in open(COMPARISONS, encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        pid = rec["prompt_id"]
        responses[pid] = {r["response_index"]: r["messages"][0]["content"]
                          for r in rec["responses"]}
        for asm in rec["metadata"]["assessments"]:
            aid = asm["annotator_id"]
            if aid not in stated:
                continue
            w = (asm.get("ranking_blocks") or {}).get("world") or []
            if not w:
                continue
            r = parse_ranking(w[0].get("ranking", ""))
            if len(r) < 2:
                continue
            top, bot = r[0], r[-1]
            if len(top) != 1 or len(bot) != 1 or top[0] == bot[0]:
                continue
            judgements.append((aid, pid, top[0], bot[0]))
    print(f"annotators {len(stated):,}   judgements {len(judgements):,}")

    corpus = list(stated.values()) + [t for d in responses.values() for t in d.values()]
    vec = TfidfVectorizer(stop_words="english", max_features=60000, sublinear_tf=True,
                          ngram_range=(1, 2), min_df=2).fit(corpus)
    S = {k: vec.transform([v]) for k, v in stated.items()}
    R = {pid: {lab: vec.transform([t]) for lab, t in d.items()} for pid, d in responses.items()}

    rng = np.random.default_rng(20260727)     # r03's seed, so C1 pairs match
    ann_list = list(stated)
    hit, perm, longer, aids = [], [], [], []
    for aid, pid, top, bot in judgements:
        st = S[aid]
        # TIES COUNT 0.5, exactly as r03 does. My first version used a bare `>`,
        # which scores every zero-overlap pair as a MISS and returned an aggregate
        # hit rate of 0.1943 against r03's stored 0.5033. The reimplementation was
        # measuring a different quantity and the stratified numbers built on it
        # were about nothing. Caught by the rebuild control below -- which this
        # round did not have until it failed.
        st_t, st_b = sim(st, R[pid][top]), sim(st, R[pid][bot])
        h = 1.0 if st_t > st_b else 0.0 if st_t < st_b else 0.5
        other = aid
        while other == aid:
            other = ann_list[rng.integers(0, len(ann_list))]
        o_t, o_b = sim(S[other], R[pid][top]), sim(S[other], R[pid][bot])
        p_ = 1.0 if o_t > o_b else 0.0 if o_t < o_b else 0.5
        hit.append(h)
        perm.append(p_)
        longer.append(len(responses[pid][top]) > len(responses[pid][bot]))
        aids.append(aid)
    hit = np.array(hit, float)
    perm = np.array(perm, float)
    longer = np.array(longer, bool)
    aids = np.array(aids)

    # REBUILD CONTROL, before anything is read. If the ALL stratum does not
    # reproduce r03's stored hit rate and difference, this round is measuring a
    # different quantity and its strata mean nothing.
    r03 = json.loads((_ROOT / "rounds/r03_stated_vs_revealed/results/"
                      "a03_stated_vs_revealed.json").read_text())
    gap_hit = abs(float(hit.mean()) - r03["hit_rate"])
    gap_dif = abs(float((hit - perm).mean()) - r03["difference"])
    print(f"rebuild control: hit {hit.mean():.4f} vs r03 {r03['hit_rate']:.4f} (|d|={gap_hit:.1e}); "
          f"difference {(hit-perm).mean():+.4f} vs {r03['difference']:+.4f} (|d|={gap_dif:.1e})")
    if gap_hit > 5e-3 or gap_dif > 5e-3:
        raise SystemExit("REFUSING: this round does not reproduce r03's aggregate, so its "
                         "strata are not strata of r03's quantity.")

    bs = np.random.default_rng(20260901)
    rows = {}
    print(f"\n{'stratum':22s} {'n':>7} {'hit':>8} {'null':>8} {'diff':>9}  95% CI (annotator-clustered)")
    for name, m in (("ALL", np.ones(len(hit), bool)),
                    ("top pick LONGER", longer),
                    ("top pick SHORTER", ~longer)):
        d = hit[m] - perm[m]
        lo, hi = clustered(d, aids[m], bs)
        equiv = bool(lo > -DELTA and hi < DELTA)
        sig = bool(lo > 0 or hi < 0)
        rows[name] = {"n": int(m.sum()), "hit": float(hit[m].mean()),
                      "null": float(perm[m].mean()), "difference": float(d.mean()),
                      "ci": [lo, hi], "significant": sig, "equivalent_at_delta": equiv}
        print(f"  {name:20s} {int(m.sum()):>7,} {hit[m].mean():>8.4f} {perm[m].mean():>8.4f} "
              f"{d.mean():>+9.4f}  [{lo:+.4f},{hi:+.4f}]  "
              f"{'SIG' if sig else 'ns'} {'EQUIV' if equiv else 'not-equiv'}")

    # THE GAP, with its own clustered interval. Resampling annotators once and
    # recomputing BOTH strata inside each draw keeps the two arms paired: a rater
    # contributes to both, so independent intervals would overstate the gap's
    # precision.
    uniq = np.unique(aids)
    idx = {x: np.flatnonzero(aids == x) for x in uniq}
    gb = []
    gr = np.random.default_rng(20260902)
    for _ in range(N_BOOT):
        take = np.concatenate([idx[x] for x in gr.choice(uniq, len(uniq), replace=True)])
        L, Sh = longer[take], ~longer[take]
        if L.sum() > 30 and Sh.sum() > 30:
            gb.append((hit[take][L] - perm[take][L]).mean()
                      - (hit[take][Sh] - perm[take][Sh]).mean())
    g = rows["top pick LONGER"]["difference"] - rows["top pick SHORTER"]["difference"]
    glo, ghi = float(np.percentile(gb, 2.5)), float(np.percentile(gb, 97.5))
    gap = {"difference_of_differences": float(g), "ci": [glo, ghi],
           "excludes_zero": bool(glo > 0 or ghi < 0), "n_boot": len(gb)}
    print(f"\n  GAP (longer minus shorter, difference of differences): {g:+.4f} "
          f"[{glo:+.4f},{ghi:+.4f}]  {'EXCLUDES ZERO' if gap['excludes_zero'] else 'covers zero'}")
    print(f"  raw hit-rate split (what entry 139 quoted): "
          f"{hit[longer].mean():.4f} vs {hit[~longer].mean():.4f} = "
          f"{hit[longer].mean() - hit[~longer].mean():+.4f}")

    L, Sh = rows["top pick LONGER"], rows["top pick SHORTER"]
    if L["significant"] and not Sh["significant"] and gap["excludes_zero"]:
        world = "L LENGTH-CONDITIONAL"
    elif not gap["excludes_zero"]:
        world = "A AVERAGE-IS-HONEST"
    else:
        world = "S SPLIT-BUT-NULL"

    # Built outside the f-string. An earlier round dodged nested quotes with
    # chr() arithmetic inside the template; it worked and was unreadable, which
    # for a conclusion string is the wrong trade twice over.
    strata_line = "; ".join(
        f"{k} n={v['n']:,} diff {v['difference']:+.4f} [{v['ci'][0]:+.4f},{v['ci'][1]:+.4f}]"
        for k, v in rows.items())
    verdict = (
        f"{world}. Entry 139 recomputed r03's verdict and surfaced a split it had never tested: the "
        f"top pick is the longer response in {longer.mean():.1%} of judgements, and the raw hit rate "
        f"splits {hit[longer].mean():.4f} against {hit[~longer].mean():.4f}, a gap of "
        f"{hit[longer].mean() - hit[~longer].mean():+.4f} -- more than ten times r03's aggregate "
        f"difference. I wrote that into three documents and tested it in none. THE STRATIFIED TEST, "
        f"each stratum against ITS OWN within-stratum permuted null so that a difference in chance "
        f"levels cannot masquerade as a difference in prediction: "
        f"{strata_line}. "
        f"The difference of differences is {g:+.4f} [{glo:+.4f},{ghi:+.4f}], which "
        f"{'EXCLUDES' if gap['excludes_zero'] else 'covers'} zero. "
        f"WHY THE RAW SPLIT AND THE TESTED GAP DIFFER: the raw split compares HIT RATES, which absorb "
        f"any difference in how easy the two strata are; the tested quantity compares each stratum's "
        f"hit rate to its OWN permuted null, which is the only version that isolates prediction. "
        f"BOOTSTRAP IS CLUSTERED ON ANNOTATOR ({len(np.unique(aids)):,} raters, "
        f"{len(hit):,} judgements) and both strata are recomputed inside each draw so the arms stay "
        f"paired. This round reproduces r03's aggregate to {gap_dif:.0e} on the difference before "
        f"any stratum is read -- a control it did not have until its first version returned an "
        f"aggregate hit rate of 0.1943 against r03's 0.5033, because it scored ties as misses where "
        f"r03 scores them 0.5."
    )

    doc = {
        "n_annotators": int(len(np.unique(aids))), "n_judgements": int(len(hit)),
        "top_longer_share": float(longer.mean()),
        "strata": rows, "gap": gap, "delta": DELTA,
        "raw_hit_split": float(hit[longer].mean() - hit[~longer].mean()),
        "world": world,
        "outcome_variable_scope": (
            "Human judgements only: a rater's own stated ideal-model-behavior text against their own "
            "top/bottom ranking. No judge, no model gold head, no generated response."),
        "scope": (
            "Length is measured in characters of the response text, and 'longer' means the rater's "
            "TOP pick is longer than their BOTTOM pick -- not longer than all four. The null is "
            "r03's C1 control (same prompt, same pair, a different person's stated text) computed "
            "within each stratum. Bootstrap clusters on annotator, as r03's own does -- r03 "
            "builds `by_ann` and resamples raters, so these intervals ARE comparable to its "
            "published one. An earlier draft of this field claimed r03 was judgement-level and "
            "therefore incomparable; that was written about code I had not read, and it survived "
            "in the artifact after being corrected in the docstring, which is the propagation "
            "failure this repository logs most often."),
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
