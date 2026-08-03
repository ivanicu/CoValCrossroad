"""r82 -- the midpoint was used ONCE in 102,147 ratings. Where does the displaced mass go?

CLAIM CARD
----------
Claim      queue item 1's rescoping: "not a forced-choice artifact" holds only as
           "ROBUST TO POST-HOC CRITERION ABSTENTION". r35 dropped low-consensus
           criteria after the fact; it could not simulate what a participant would
           do given a real neutral option AT ELICITATION TIME.
Estimand   the shape of the released weight distribution, split by PROVENANCE --
           pre-seeded criteria a rater was shown versus write-ins the rater chose
           to author -- with the midpoint rate and the low-magnitude mass as the
           quantities of interest.
Target
observed?  PARTLY, and the part that is observable is the one nobody has read out.
           No participant was offered "no general direction" at elicitation, so
           what they WOULD have done is unobservable and stays that way. What IS
           observable is where the mass went given that the midpoint was
           effectively unavailable, and whether that differs between criteria a
           rater chose and criteria a rater was handed.
Alternative
worlds     B BINDS HARDEST ON SEEDS  a rater has an opinion about a criterion they
                                     wrote, and may have none about one they were
                                     shown. If the missing neutral binds, seeds
                                     should carry more mass at |w| = 1-2 -- the
                                     smallest available way to say "barely" --
                                     than write-ins do.
           U UNIFORM                 the two classes use the scale the same way.
                                     Then the absent midpoint is a property of the
                                     scale rather than a pressure that varies with
                                     whether the rater chose the item, and the
                                     forced-choice worry gets no support here.
           I INVERTED                write-ins carry MORE low-magnitude mass, which
                                     would mean people hedge most about the things
                                     they chose to raise -- a different finding and
                                     one I would not have predicted.
Intervention
           none. Reading the released ratings.
Null       permute the provenance label across criteria within a prompt and
           recompute; the class difference must collapse.

WHAT THIS CANNOT DO, STATED FIRST
---------------------------------
It cannot establish that forced choice CREATED anything. Nobody was offered a
neutral option, so there is no counterfactual arm in this release -- that is
exactly why S_pre and the neutral-option arm are preregistered. What it can do is
say whether the scale was used differently where the pressure should differ, and
a null here is evidence about the pressure's uniformity, not its absence.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

RUBRICS = _ROOT / "data/conversation_rubrics.jsonl"
SEED_MIN_RATERS = 6          # r48's structural gap: 1 rater vs many, nothing between
LOW = (1, 2)                 # the smallest available way to say "barely"
N_PERM = 400


def load():
    rows = []
    for line in open(RUBRICS, encoding="utf-8"):
        d = json.loads(line)
        pid = (d.get("conversation") or {}).get("id")
        for c in d.get("coval_full") or []:
            sc = [s["score"] for s in c["scores"]]
            if not sc:
                continue
            rows.append({"pid": pid, "scores": sc,
                         "seed": len(sc) >= SEED_MIN_RATERS,
                         "writein": len(sc) == 1})
    return rows


def profile(scores):
    a = np.array(scores, float)
    n = a.size
    return {
        "n_ratings": int(n),
        "midpoint_rate": float((a == 0).mean()),
        "low_magnitude_rate": float(np.isin(np.abs(a), LOW).mean()),
        "extreme_rate": float((np.abs(a) == 10).mean()),
        "positive_share": float((a > 0).mean()),
        "mean_abs": float(np.abs(a).mean()),
        "round_number_rate": float(np.isin(np.abs(a), (5, 10)).mean()),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r82_scale_use_by_provenance.json")
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
    allsc = [s for r in rows for s in r["scores"]]
    hist = Counter(allsc)
    total = len(allsc)
    if total < 10000:
        raise SystemExit(f"REFUSING: only {total} ratings.")

    seed_sc = [s for r in rows if r["seed"] for s in r["scores"]]
    wi_sc = [s for r in rows if r["writein"] for s in r["scores"]]
    prof = {"all": profile(allsc), "seed": profile(seed_sc), "write_in": profile(wi_sc)}
    print(f"ratings {total:,}   seed {len(seed_sc):,}   write-in {len(wi_sc):,}")
    print(f"\n{'quantity':22s} {'all':>10} {'seed':>10} {'write-in':>10}")
    for k in ("midpoint_rate", "low_magnitude_rate", "extreme_rate",
              "positive_share", "mean_abs", "round_number_rate"):
        print(f"  {k:20s} {prof['all'][k]:>10.4f} {prof['seed'][k]:>10.4f} "
              f"{prof['write_in'][k]:>10.4f}")

    # The class contrast, with a provenance-permutation null. Permuting WITHIN a
    # prompt keeps each prompt's own mix of criteria and only scrambles which
    # class a criterion belongs to, so a prompt-level difference in scale use
    # cannot masquerade as a provenance effect.
    obs = prof["seed"]["low_magnitude_rate"] - prof["write_in"]["low_magnitude_rate"]
    by_pid = {}
    for r in rows:
        by_pid.setdefault(r["pid"], []).append(r)
    rng = np.random.default_rng(20260903)
    null = []
    for _ in range(N_PERM):
        s_lo = s_n = w_lo = w_n = 0
        for _pid, group in by_pid.items():
            labels = np.array([r["seed"] for r in group])
            rng.shuffle(labels)
            for r, lab in zip(group, labels):
                arr = np.abs(np.array(r["scores"], float))
                lo = int(np.isin(arr, LOW).sum())
                if lab:
                    s_lo += lo; s_n += arr.size
                else:
                    w_lo += lo; w_n += arr.size
        if s_n and w_n:
            null.append(s_lo / s_n - w_lo / w_n)
    null = np.array(null)
    lo_q, hi_q = float(np.percentile(null, 2.5)), float(np.percentile(null, 97.5))
    outside = bool(obs < lo_q or obs > hi_q)
    print(f"\n  low-magnitude rate, seed minus write-in: {obs:+.4f}")
    print(f"  provenance-permutation null (within prompt): "
          f"[{lo_q:+.4f},{hi_q:+.4f}] over {len(null)} draws")
    print(f"  -> {'OUTSIDE the null' if outside else 'inside the null'}")

    # ⚠ A FOURTH WORLD I FAILED TO WRITE BEFORE THE RUN, and it predicts the same
    # direction as B: SELECTION. A rater authors a write-in because they already
    # care about it, so of course they rate it strongly; being handed a criterion
    # says nothing about caring. That produces more low-magnitude mass on seeds
    # with no forced-choice pressure anywhere. The permutation null rules out
    # prompt-level artifacts -- it does NOT rule this out, because it scrambles
    # which class a criterion is in, not why the class exists.
    #
    # Both stories are alive on this evidence and the label says so rather than
    # claiming the one I predicted. Writing the confound after seeing the result
    # is worse than writing it before; not writing it at all would be worse still.
    if not outside:
        world = "U UNIFORM"
    elif obs > 0:
        world = ("B/S UNSEPARATED -- displacement and selection both predict this, "
                 "and this design cannot tell them apart")
    else:
        world = "I INVERTED -- write-ins hedge more"

    verdict = (
        f"{world}. The midpoint of a 21-point scale was used once in {total:,} ratings "
        f"({prof['all']['midpoint_rate']:.6f}). ⚠ THAT FACT WAS ALREADY IN THE PACKAGE -- r35's "
        f"`scale_note` states it verbatim, and an earlier draft of this verdict claimed no round had "
        f"read it out, because the prior-art search used the words 'magnitude' and 'histogram' rather "
        f"than the claim being made. What IS new here is the shape: the full histogram, "
        f"{prof['all']['round_number_rate']:.4f} of all mass on 5 or 10, and the provenance split "
        f"below. Queue item 1 rescoped 'not a forced-choice artifact' to 'robust to "
        f"POST-HOC criterion abstention' precisely because r35 could not simulate an "
        f"elicitation-time neutral option; this round cannot simulate one either, and does not try. "
        f"What it asks instead is whether the scale is used DIFFERENTLY where the pressure should "
        f"differ -- a rater has an opinion about a criterion they wrote and may have none about one "
        f"they were shown. Low-magnitude ratings (|w| in {LOW}) are "
        f"{prof['seed']['low_magnitude_rate']:.4f} of seed ratings against "
        f"{prof['write_in']['low_magnitude_rate']:.4f} of write-in ratings, a difference of "
        f"{obs:+.4f} against a within-prompt provenance-permutation null of "
        f"[{lo_q:+.4f},{hi_q:+.4f}]. "
        f"SCALE-USE FACTS WORTH HAVING SEPARATELY FROM THE CONTRAST: {prof['all']['positive_share']:.4f} "
        f"of ratings are positive, {prof['all']['extreme_rate']:.4f} sit at the extreme |w|=10, and "
        f"{prof['all']['round_number_rate']:.4f} fall on 5 or 10 -- so more than a third of all "
        f"weight mass lands on two of the twenty-one available values, which is coarse mental "
        f"rounding and bears on how much resolution any weighted aggregation can actually carry. "
        f"⚠ THE RIVAL I DID NOT WRITE BEFORE THE RUN, and it predicts the same direction: "
        f"SELECTION. A rater authors a write-in because they already care about it, so it gets a "
        f"strong weight; a rater is HANDED a seed regardless of whether they care. That yields more "
        f"low-magnitude mass on seeds with no forced-choice pressure involved at all. The "
        f"permutation null does not touch it -- it scrambles which class a criterion is in, not why "
        f"the class exists -- so displacement and selection are UNSEPARATED here and the world label "
        f"says so instead of naming the one I predicted. "
        f"WHAT THIS CANNOT DO, unchanged from before the run: nobody in this release was offered a "
        f"neutral option, so what they WOULD have done is unobservable. A null here would say the "
        f"pressure is uniform across provenance, not that there is no pressure. "
        f"WHAT WOULD SEPARATE THEM: the preregistered neutral-option arm. If the missing midpoint is "
        f"doing the work, offering 'no general direction' should absorb most of the seed "
        f"low-magnitude mass and little of the write-in mass -- a directional prediction this round "
        f"contributes to Experiment 1 and cannot itself test."
    )

    doc = {
        "total_ratings": total,
        "histogram": {str(k): int(v) for k, v in sorted(hist.items())},
        "profiles": prof,
        "low_magnitude_values": list(LOW),
        "seed_minus_writein_low_rate": obs,
        "permutation_null_ci": [lo_q, hi_q], "n_perm": len(null),
        "outside_null": outside, "world": world,
        "outcome_variable_scope": (
            "Released human weights only. No judge, no model, no ranking enters this round."),
        "scope": (
            "Provenance is r48's identification by rating count -- criteria rated by at least "
            f"{SEED_MIN_RATERS} raters are the pre-seeded set shown to everyone, singly-rated ones "
            "are participant write-ins. The permutation is WITHIN prompt, so a prompt whose "
            "criteria are all rated softly cannot create a provenance effect. This measures scale "
            "USE, not what a neutral option would have produced -- that arm does not exist in this "
            "release and is preregistered."),
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
