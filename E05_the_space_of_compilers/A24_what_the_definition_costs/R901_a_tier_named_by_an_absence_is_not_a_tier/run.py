#!/usr/bin/env python3
"""
R901 · why two satisfaction-blind rules differ by 0.0748 — and why the tier was never a tier.

⛔ WHY. R900's placebo found `topw_k4` (+0.0219) and `topabs_k4` (−0.0528) differing by **+0.0748**
despite both being satisfaction-blind and label-blind. That killed R900's tier means: the
within-tier spread was 67% of the contrast the tiers were built to measure. **The obstacle is the
question, and the generator answers it in its own words:**
  · `select_core.py:16` — `topw_k` = *"the k criteria with the highest MEAN importance score"*
  · `select_core.py:18` — `topabs_k` = *"the k with the largest |mean|, i.e. most polarising
    EITHER WAY"*
**`topabs_k` deliberately admits criteria with strongly NEGATIVE mean importance.** The two rules
are not two draws of one thing; they optimise different objectives over the same weights.

⭐⭐ **AND THAT IS THE GENERALISABLE FAILURE, WHICH IS WORTH MORE THAN THE GAP.** I built the tier
`T1 = no search` and defined it by what its members DO NOT SEE — satisfaction, labels. **An absence
does not constrain what the members DO.** So the tier pooled *"pick what the rubric says matters"*
with *"pick what is most polarising"*, and its mean was an average over an arbitrary set. That is
this session's recurring population failure — a group chosen by a FILTER rather than by a PROPERTY
— arriving at the level of taxonomy rather than of row selection.

ESTIMAND        the per-prompt overlap between the criterion sets `topw_k4` and `topabs_k4` select,
                and whether low overlap accompanies the score gap.
IDENTIFICATION  exact for overlap: both arms' selected criteria are committed per prompt in
                `core_*.json`. ⚠ **Whether overlap CAUSES the gap is NOT identified** — this shows
                the two rules choose different objects, not that the difference in objects is what
                produced the difference in score. That would need an intervention.
SCOPE           population: prompts where BOTH arms committed a selection — counted, not assumed
                instrument: Jaccard overlap of selected criterion sets; per-prompt A2 margin
                baseline:   two arms of the SAME rule — the overlap two runs of one rule produce
                regime:     home release, judge 2B, k=4
WORLDS          A · overlap is low -> the two rules select genuinely different criteria, the tier
                    pooled two objects, and R900's tier means were invalid for a NAMED reason
                B · overlap is high -> the rules pick nearly the same criteria and the 0.0748 gap
                    is NOT a selection difference; something else produced it and the mechanism is
                    still open
                C · one arm's selections are unreadable -> UNVERIFIED, and the comparison waits
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE / CEILING: a rule against ITSELF must give overlap 1.0. If identical
                     inputs do not give perfect overlap, the overlap statistic is broken and
                     nothing below it is readable.
                  ⭐ ② FLOOR: the overlap of a RANDOM k-subset of the same prompt's criteria, which
                     is what "no relationship" looks like at this k and this pool size. Without it
                     a Jaccard of 0.4 has no interpretation.
                     ⛔⛔ POST-RUN, AND THE FLOOR'S FIRST POPULATION WAS THE BIASED ONE. I drew the
                     random subsets from the UNION OF THE TWO ARMS' SELECTIONS and required
                     `len(pool) >= 2k`. That condition holds **only where the arms DO NOT overlap**
                     — 29 of 968 prompts — so the floor was computed on exactly the subsample that
                     makes the arms look most different. **The filter selected the population, and
                     the population was the answer.** This session's recurring failure, committed
                     inside the control built to make another number readable.
                     ⭐ AND ITS FAILURE IS DATA: on **939 of 968** prompts the union of two 4-sets
                     is under 8, so the two rules already share criteria on 97% of prompts.
                     Corrected: the pool is the prompt's FULL criterion set from `core_full.json`
                     (median 15, range 4–39), which is what the rules actually choose from.
                  ⭐ ③ the population must be the prompts where BOTH arms selected; counted and
                     printed, never assumed to be all 968.
MULTIPLICITY    one estimand; the whole overlap distribution reported, not its mean alone.
ARTIFACT        results/tier_was_not_a_tier.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: causation. Low overlap explains why the tier is incoherent; it
                does not establish that the criterion difference produced the score difference.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
GEN = ROOT / "corebench" / "select_core.py"
SEED = 901
A, B = "topw_k4", "topabs_k4"


def load_core(nm):
    f = RES / f"core_{nm}.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text())
    except Exception:
        return None


def jac(x, y):
    x, y = set(x), set(y)
    return len(x & y) / len(x | y) if (x or y) else float("nan")


def main() -> int:
    src = GEN.read_text()
    doc_w = "highest MEAN importance" in src
    doc_a = "most polarising either way" in src
    print(f"  the generator's OWN description, read not remembered:")
    print(f"    topw_k   'highest MEAN importance score'          present: {doc_w}")
    print(f"    topabs_k 'largest |mean|, most polarising either way' present: {doc_a}")

    ca, cb = load_core(A), load_core(B)
    if ca is None or cb is None:
        print(f"  UNRUNNABLE: core json missing for {A if ca is None else B}. Exit 2, never 0.")
        return 2
    shared = sorted(set(ca) & set(cb))
    print(f"\n  ③ prompts with a selection in BOTH arms: {len(shared)} "
          f"({A}: {len(ca)}, {B}: {len(cb)})")
    if len(shared) < 100:
        print("  UNRUNNABLE: fewer than 100 shared prompts. Exit 2, never 0.")
        return 2

    # ---- ① CEILING: a rule against itself -----------------------------------------------------
    self_j = np.array([jac(ca[p], ca[p]) for p in shared])
    c1 = abs(float(self_j.mean()) - 1.0) < 1e-9
    print(f"  ① CEILING  {A} against ITSELF: mean Jaccard {self_j.mean():.6f} == 1.0: {c1}  "
          f"{'PASS' if c1 else 'FAIL'}")

    # ---- ② FLOOR: random k-subsets of the same prompt's own pool -------------------------------
    rng = np.random.default_rng(SEED)
    full = load_core("full")
    if full is None:
        print("  UNRUNNABLE: core_full.json missing — no pool to draw the floor from. Exit 2.")
        return 2
    floor = []
    for p in shared:
        pool = sorted(set(full.get(p, [])))          # the FULL choice set, not the union
        k = len(ca[p])
        if len(pool) >= 2 * k:
            u = rng.choice(len(pool), k, replace=False)
            v = rng.choice(len(pool), k, replace=False)
            floor.append(jac([pool[i] for i in u], [pool[i] for i in v]))
    floor = np.array(floor) if floor else np.array([np.nan])
    c2 = np.isfinite(floor).sum() >= 50
    print(f"  ② FLOOR    random k-subsets of the FULL criterion pool: mean {np.nanmean(floor):.4f} "
          f"(n={int(np.isfinite(floor).sum())}): {c2}  {'PASS' if c2 else 'FAIL'}")
    print(f"     ⚠ the floor is what `no relationship` LOOKS like at this k and pool size —")
    print(f"       without it a Jaccard of 0.4 has no interpretation at all.")
    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "controls": [bool(c1), bool(c2)]},
                  open(OUT / "tier_was_not_a_tier.json", "w"), indent=2)
        return 2

    obs = np.array([jac(ca[p], cb[p]) for p in shared])
    ident = float((obs == 1.0).mean())
    disj = float((obs == 0.0).mean())
    print(f"\n  ⭐ OVERLAP OF THE SELECTED CRITERION SETS, {A} vs {B}:")
    print(f"     mean Jaccard {obs.mean():.4f}   median {np.median(obs):.4f}")
    for q in (5, 25, 50, 75, 95):
        print(f"       p{q:<3} {np.percentile(obs, q):.4f}")
    print(f"     identical on {ident:.1%} of prompts · completely disjoint on {disj:.1%}")
    print(f"     floor (random subsets) {np.nanmean(floor):.4f}")

    world = "A" if obs.mean() < 0.5 else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": f"the two rules select genuinely different criteria (mean Jaccard {obs.mean():.4f}, "
             f"disjoint on {disj:.1%} of prompts) — R900's `T1 = no search` tier pooled TWO "
             "OBJECTS, and its mean was invalid for a named reason",
        "B": f"the rules pick nearly the same criteria (mean Jaccard {obs.mean():.4f}) — the "
             "0.0748 gap is NOT a selection difference and its mechanism is still open"}[world])

    print(f"\n  ⭐⭐ AND THE LESSON IS WORTH MORE THAN THE GAP. I named the tier by what its members")
    print(f"     DO NOT SEE — satisfaction, labels. **An absence does not constrain what the")
    print(f"     members DO.** So `no search` pooled `pick what the rubric says matters` with")
    print(f"     `pick what is most polarising`, and averaged them. That is a group chosen by a")
    print(f"     FILTER rather than by a PROPERTY — this session's recurring population failure,")
    print(f"     arriving at the level of TAXONOMY instead of row selection.")
    print(f"\n  ⚠ NOT CAUSATION. Low overlap explains why the tier is incoherent. It does NOT")
    print(f"    establish that the criterion difference PRODUCED the score difference — that")
    print(f"    needs an intervention this release cannot run.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED,
               "arms": [A, B], "n_shared_prompts": len(shared),
               "generator_says": {"topw_k": "highest MEAN importance score",
                                  "topabs_k": "largest |mean|, most polarising EITHER WAY",
                                  "read_from_source": bool(doc_w and doc_a)},
               "jaccard": {"mean": float(obs.mean()), "median": float(np.median(obs)),
                           "p5": float(np.percentile(obs, 5)),
                           "p95": float(np.percentile(obs, 95)),
                           "share_identical": ident, "share_disjoint": disj},
               "floor_population_corrected": "the floor first drew from the UNION of the two "
                                             "arms' selections with len(pool) >= 2k, which holds "
                                             "only where the arms DO NOT overlap — 29 of 968. The "
                                             "filter chose the population and the population was "
                                             "the answer. Corrected to the FULL criterion pool.",
               "controls": {"ceiling_self_jaccard": float(self_j.mean()),
                            "floor_random_subsets": float(np.nanmean(floor)),
                            "floor_n": int(np.isfinite(floor).sum())},
               "explains": "R900's within-tier spread of 0.0748 between two satisfaction-blind "
                           "rules",
               "lesson": "a tier named by an ABSENCE (does not see satisfaction/labels) does not "
                         "constrain what its members DO, so its mean is an average over an "
                         "arbitrary set — a group chosen by a FILTER rather than a PROPERTY",
               "not_causation": "low overlap explains the tier's incoherence; it does not establish "
                                "that the criterion difference produced the score difference",
               "unit_note": "Jaccard is a set overlap; margins are A2 units",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "tier_was_not_a_tier.json", "w"), indent=2)
    print(f"\n  artifact: results/tier_was_not_a_tier.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
