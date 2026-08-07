"""R439 -- is candidate ④ a NEW clause, or a weaker setting of clause ②'s own knob?

⛔ THE ANNOUNCED STEP WAS FORCED. R438 closed with "run a joint census: for every arm on both
   releases, which of ②/③/④ admits it". Both cells are arithmetic:
     HOME    R436 measured ④ excluding 0 of 56 at J, so ④ admits ALL -> the conjunction is ② ∩ ③.
     SECOND  R434 measured ② admitting 0 of 7, so the conjunction is EMPTY whatever ③ and ④ do.
   Nothing could have come out otherwise. **Eighth announced step checked, SIXTH killed.**

⭐ WHAT IS NOT FORCED, AND THE LEDGER HAS A ROW FOR IT. *"A reparameterisation is not a measurement
   -- regress the candidate on what is PUBLISHED; no residual = an identity, however meaningful it
   sounds."* Clause ②'s reference is a size-matched criterion set drawn from a 16-item generic pool;
   the published choice is `POOL[0:k]`, picked by FILE ORDER, and R331 measured it at the **93.7th
   percentile of all 1,820 size-4 subsets**. Candidate ④'s bar is the best criterion-FREE rule.
   **If ④'s bar sits inside the distribution ②'s reference is drawn from, then ④ is not a new axis
   -- it is a weaker setting of ②'s existing knob, and the definition has one clause with a dial
   rather than two clauses.**

ESTIMAND (named before the method)
    PCT = the percentile of ④'s bar (the best criterion-free rule's A2) within the distribution of
          A2 over ALL C(16,4) = 1,820 size-4 subsets of the generic pool -- clause ②'s own
          reference class.
    This is a CENSUS of the reference class, not a sample of it: every subset is evaluated.

IDENTIFICATION
    Fully identified: the pool's satisfaction matrix is committed, A2 is computable for every
    subset, and ④'s bar is committed by R436. What is NOT identified: whether "the same statistic"
    makes two objects "the same axis" -- a criterion set and a text statistic can produce equal A2
    without being the same kind of thing, and that is precisely the ambiguity this round exists to
    price rather than to settle by assertion.

SCOPE  population : the home release's prompts carrying a ranking, k=4
       instrument : the committed judge for the pool subsets; NONE for ④'s bar
       baseline   : the 1,820-subset distribution itself, reported whole
       regime     : A2 over 6 pairs, one annotator drawn per prompt per seed

WORLDS
    W-REPARAM        PCT lands inside the bulk (5th-95th) -> ④'s bar is a choice ②'s knob can
                     already make. The two clauses are one clause with a dial, and adopting ④ as a
                     fourth conjunct would be double-counting a single axis.
    W-DIFFERENT-KIND PCT lands below essentially every subset -> no admissible setting of ②'s
                     reference is as weak as ④'s bar, so ④ is not reachable by turning ②'s knob and
                     the two are genuinely different objects.
    W-STRONGER       PCT lands above most subsets -> ④ would be a STRENGTHENING of ②, which would
                     invert R437's reading of which clause binds at home and needs its own round.

PREDICTION MATRIX
                       PCT in the bulk   PCT at the bottom   PCT at the top
    W-REPARAM               0.9                0.05               0.05
    W-DIFFERENT-KIND        0.05               0.9                0.02
    W-STRONGER              0.05               0.02               0.9

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    5 <= PCT <= 95   -> W-REPARAM. ④ must NOT be adopted as a fourth conjunct; the honest change is
                        to say clause ②'s reference level is under-specified, which R331 already
                        measured and which this would make unavoidable.
    PCT < 5          -> W-DIFFERENT-KIND. ④ survives as a distinct clause.
    PCT > 95         -> W-STRONGER. Reported as a separate finding requiring its own round, NOT
                        folded into "④ is a good clause".
    a control fails  -> UNVERIFIED

CONTROLS
    POSITIVE   the human's own ranking, scored through the same path, must land at PCT = 100. A
               percentile scale that cannot put a perfect ordering at the top is not a scale.
    g=0        a pool subset's OWN A2 must land at its own empirical percentile, exactly. If a
               member of the distribution does not sit where the distribution says it does, the
               percentile function is broken and every PCT below is noise.
    NEGATIVE   a random-scoring rule must land near the bottom AND the distribution must have
               non-zero spread -- a degenerate distribution admits no percentile at all, and R331's
               "93.7th percentile" would be equally meaningless if it were degenerate.
    PLACEBO    the published reference `POOL[0:4]` must reproduce R331's 93.7th percentile. This is
               the one control that ties this round's scale to the published record; if it misses,
               the scale is not the one the definition's own numbers were computed on.
    SEEDS      >=3 annotator draws; the spread across seeds is reported beside PCT.

MULTIPLICITY  one estimand, reported with its whole distribution; no selection.
ARTIFACT      results/r439_reparam.json -- including the full 1,820-value distribution, so a later
              round can re-percentile anything against it without recomputing 1,820 subsets.
IMPOSSIBLE HERE, NAMED
    * settling whether equal A2 makes two objects "the same axis" -- a construct question. Requires
      a criterion for sameness that neither release provides.
    * the supremum over criterion-free rules -- R435's 30-member family, restated.
    * generalising past k=4 -- the pool sweep is size-4 by construction.

EXIT 0 W-DIFFERENT-KIND · 1 W-REPARAM · 2 W-STRONGER or UNVERIFIED
"""
from __future__ import annotations
import hashlib
import itertools
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
L = "ABCD"


def stable(pid: str) -> int:
    """R436's lesson: `hash(str)` is randomised per process, so a round seeded with it is not
    reproducible even when its verdict looks stable."""
    return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC

    print("R439 · is ④ a NEW clause, or a weaker setting of clause ②'s own knob?\n")
    print("  ⛔ the announced joint census was FORCED: ④ admits all 56 at home (R436) so the")
    print("     conjunction is ② ∩ ③, and ② admits 0 of 7 on the second release (R434) so it is")
    print("     empty there. Eighth announced step checked, SIXTH killed.\n")

    pool = SC.load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    targets, _ = SC.load_targets()
    pids = sorted(set(pool) & set(targets))
    if len(pids) < 200:
        print("  UNRUNNABLE: too few prompts with both a pool score and a ranking. Exit 2."); return 2

    SEEDS = (0, 1, 2)
    hy = {}
    for p in pids:
        v = targets[p]
        hy[p] = [np.array(v[int(np.random.default_rng(1000 * s + stable(p))
                                 .integers(len(v)))][0], float) for s in SEEDS]

    def a2_of_y(y, p):
        c = SC.cls(y)
        return float(np.mean([np.mean([a == b for a, b in zip(c, SC.cls(h))]) for h in hy[p]]))

    # per-prompt, per-criterion satisfaction as a 16x4 matrix -> subset A2 is a sum over rows
    M = {}
    for p in pids:
        m = np.zeros((16, 4))
        for (i, ltr), v in pool[p].items():
            m[i, L.index(ltr)] = v
        M[p] = m

    subsets = list(itertools.combinations(range(16), 4))
    print(f"  prompts {len(pids)} · subsets C(16,4) = {len(subsets)} — a CENSUS of the reference")
    print(f"  class, not a sample of it")
    dist = np.array([float(np.mean([a2_of_y(M[p][list(sub)].sum(axis=0), p) for p in pids]))
                     for sub in subsets])

    # ------------------------------------------------------------------------------- controls
    ok = True
    pos = float(np.mean([a2_of_y(hy[p][0], p) for p in pids]))
    pos_pct = float((dist < pos).mean() * 100)
    ok &= (pos_pct >= 99.9)
    print(f"\n  POSITIVE  the human's own ranking -> A2 {pos:.4f}, percentile {pos_pct:.1f}, "
          f"must be 100   {'PASS' if pos_pct >= 99.9 else '⛔ FAIL — the scale cannot top out'}")

    j = 7
    own = dist[j]
    own_pct = float((dist < own).mean() * 100)
    recomputed = float(np.mean([a2_of_y(M[p][list(subsets[j])].sum(axis=0), p) for p in pids]))
    g0 = abs(recomputed - own) < 1e-12
    ok &= g0
    print(f"  g=0       a pool subset against its own distribution -> {recomputed:.6f} vs "
          f"{own:.6f}, must be EXACT   {'PASS' if g0 else '⛔ FAIL — the percentile fn is broken'}")

    rng = np.random.default_rng(3)
    rnd = float(np.mean([a2_of_y(rng.random(4), p) for p in pids]))
    rnd_pct = float((dist < rnd).mean() * 100)
    spread_ok = float(dist.std()) > 1e-6
    ok &= spread_ok
    print(f"  NEGATIVE  a random-scoring rule -> A2 {rnd:.4f}, percentile {rnd_pct:.1f}")
    print(f"            distribution spread sd {dist.std():.5f}, must be > 0   "
          f"{'PASS' if spread_ok else '⛔ FAIL — a degenerate distribution admits no percentile'}")

    pub = float(np.mean([a2_of_y(M[p][[0, 1, 2, 3]].sum(axis=0), p) for p in pids]))
    pub_pct = float((dist < pub).mean() * 100)
    plac = abs(pub_pct - 93.7) < 8.0
    ok &= plac
    print(f"  PLACEBO   the PUBLISHED reference POOL[0:4] -> A2 {pub:.4f}, percentile "
          f"{pub_pct:.1f}; R331 published 93.7   "
          f"{'PASS' if plac else '⛔ FAIL — this is not the scale the record was computed on'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r439_reparam.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ---------------------------------------------------------------------------- the estimand
    a436 = json.loads((A24 / "R436_does_clause_four_exclude_anything_at_home" /
                       "results" / "r439_reparam.json").read_text()) \
        if False else json.loads((A24 / "R436_does_clause_four_exclude_anything_at_home" /
                                  "results" / "r436_clause4_at_home.json").read_text())
    bar4 = a436["bar"]
    PCT = float((dist < bar4).mean() * 100)
    print(f"\n  the 1,820-subset distribution: min {dist.min():.4f} · 5th "
          f"{np.percentile(dist, 5):.4f} · median {np.percentile(dist, 50):.4f} · 95th "
          f"{np.percentile(dist, 95):.4f} · max {dist.max():.4f}")
    print(f"  ④'s bar (`{a436['best_rule']}`) A2 {bar4:.4f}  ->  PERCENTILE {PCT:.2f}")

    world = ("W-REPARAM" if 5 <= PCT <= 95 else
             "W-DIFFERENT-KIND" if PCT < 5 else "W-STRONGER")
    print(f"\n  WORLD: {world}")
    if world == "W-DIFFERENT-KIND":
        print(f"    ⭐ ④'s bar sits BELOW {100 - PCT:.2f}% of every size-4 subset of clause ②'s own")
        print(f"    reference pool. No admissible setting of ②'s knob is as weak as ④'s bar, so ④")
        print(f"    is NOT reachable by turning that knob: the two clauses are different objects,")
        print(f"    and adopting ④ is not double-counting one axis.")
        print(f"    ⚠ What this does NOT settle: whether equal A2 would make two objects the same")
        print(f"    axis. It settles the weaker and sufficient thing — ②'s knob cannot reach here.")
    elif world == "W-REPARAM":
        print(f"    ⛔ ④'s bar sits at the {PCT:.1f}th percentile of ②'s own reference class, well")
        print(f"    inside its bulk. ④ is a SETTING of ②'s knob, not a new axis, and adopting it as")
        print(f"    a fourth conjunct would double-count a single dimension. The honest change is")
        print(f"    that clause ②'s reference level is under-specified — which R331 measured and")
        print(f"    this makes unavoidable.")
    else:
        print(f"    ④'s bar sits ABOVE {PCT:.1f}% of the reference class — it would STRENGTHEN ②,")
        print(f"    which inverts R437's reading of which clause binds at home. Reported as a")
        print(f"    separate finding needing its own round, not folded into '④ is a good clause'.")

    (RES / "r439_reparam.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "pct": PCT, "bar4": bar4, "bar4_rule": a436["best_rule"],
         "published_ref_a2": pub, "published_ref_pct": pub_pct,
         "oracle_a2": pos, "oracle_pct": pos_pct, "random_a2": rnd, "random_pct": rnd_pct,
         "dist_min": float(dist.min()), "dist_max": float(dist.max()),
         "dist_median": float(np.percentile(dist, 50)), "dist_sd": float(dist.std()),
         "n_subsets": len(subsets), "n_prompts": len(pids), "seeds": list(SEEDS),
         "distribution": [float(x) for x in dist]}, indent=1))
    print(f"\n  artifact -> {(RES / 'r439_reparam.json').relative_to(ROOT)}")
    return 0 if world == "W-DIFFERENT-KIND" else (1 if world == "W-REPARAM" else 2)


if __name__ == "__main__":
    sys.exit(main())
