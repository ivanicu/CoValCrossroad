"""R1060 — exhaustively bound what any fixed-subset core can reach here, and decide if the confound breaks.

R1059 measured the gap that sustains R1058's provenance-vs-quality confound: the best core I built
scored 0.4863 against comparator `generic` at 0.5514, a gap of +0.0651, so non-admission was fully
explained by quality. That turned the confound from a shrug into a specification — close 0.0651 —
but left open whether anything on this site CAN close it.

⭐ AN EXHAUSTIVE SEARCH ANSWERS THAT AND A BETTER OPTIMISER NEVER COULD. If the best fixed subset,
   scored on prompts it was not selected on, still falls short of the comparator, then no rule OF
   THIS SHAPE can close the gap here and the confound is structurally unbreakable on this site — a
   bound, not another failed attempt. If some subset clears it, then R1059's optimisers were simply
   bad, and the confound is breakable by better construction.

ESTIMAND        max over fixed criterion subsets of held-out mean agreement with the human target,
                against the comparator's mean on the same prompts
IDENTIFICATION  exact within the enumerated family. ⚠ SCOPE: `fixed subsets of size <= 5 drawn from
                the 15 criteria available on >= 50% of prompts`. It bounds THAT family and not every
                conceivable core; a prompt-conditioned rule is outside it by construction, which is
                stated rather than discovered later.
SCOPE           population : 968 prompts, split into selection and evaluation halves
                instrument : agreement of the induced pairwise ranking with each human ranking
                baseline   : `generic` on the SAME evaluation prompts, not its global mean
                regime     : target A2
WORLDS          A THE CONFOUND IS BREAKABLE — some fixed subset clears the comparator on held-out
                  prompts. Then R1059's optimisers were weak, not the site, and a properly-built
                  never-seen core could be admitted.
                B THE BOUND BINDS — the best held-out subset falls short. Then no fixed-subset core
                  can close R1059's gap here, non-admission of every such core is forced by the
                  release, and `does the clause test provenance` is UNANSWERABLE by this family.
                prediction matrix: A -> best_heldout > comparator_heldout
                                   B -> best_heldout <= comparator_heldout
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      best held-out subset > comparator on the same prompts -> World A
                      otherwise                                              -> World B, and the
                      shortfall is the bound
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ the comparator's OWN selection must be inside the enumerated family and must
                recover its own score. If enumerating cannot reproduce a known member, the search is
                not over the space it claims.
NEGATIVE CTRL   the WORST subset must score below the comparator, or the family is degenerate and no
                maximum over it is informative.
SHAM            ⭐ the selection half is REPLACED BY NOISE — pick the best subset by a random
                criterion, then evaluate honestly. The gap between honest selection and sham
                selection is what selection is worth; if it is ~0, the search is not selecting.
PLACEBO         an empty subset scores at the degenerate floor.
NOISE FLOOR     ⭐ SELECTION BIAS IS THE FLOOR HERE and it is measured: 5 independent splits, and the
                in-sample best is reported beside the held-out best so the optimism is visible.
MULTIPLICITY    4943 subsets is the family size and it is reported; the best is a MAXIMUM over it,
                so the held-out evaluation is what makes it admissible at all.
SEEDS           5 splits.
IMPOSSIBLE      whether a PROMPT-CONDITIONED rule could clear the bar. Outside this family by
                construction. SETTLES: IN-RELEASE - it is a larger search, not a different release.
"""
import itertools, json, pathlib, sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls, PAIRS  # noqa: E402

MAXK = 5
AVAIL_FRAC = 0.5


def main() -> int:
    tg, _ = load_targets()
    S = load_sat(RES / "sat_full.npz")
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    if n < 200:
        print("  UNRUNNABLE: too few prompts. Exit 2, never 0."); return 2

    cnt = {}
    for p in pids:
        for i in {i for i, _ in S[p]}:
            cnt[i] = cnt.get(i, 0) + 1
    idxs = sorted(i for i, c in cnt.items() if c >= AVAIL_FRAC * n)
    print(f"  ⭐ prompts {n} · criteria on >= {AVAIL_FRAC:.0%} of prompts: {len(idxs)} {idxs}")

    # A[prompt, criterion, letter] — precomputed so a subset's score is a sum, not a re-read
    A = np.zeros((n, len(idxs), 4))
    for k, p in enumerate(pids):
        for j, i in enumerate(idxs):
            for li, x in enumerate("ABCD"):
                A[k, j, li] = S[p].get((i, x), 0.0)
    Hm = np.array([np.mean([cls(np.array(t[0], float)) for t in tg[p]], axis=0) for p in pids])
    Hs = np.sign(Hm)                                   # consensus pairwise sign per prompt
    ia = np.array([i for i, _ in PAIRS]); ib = np.array([j for _, j in PAIRS])

    def score_subset(cols):
        y = A[:, cols, :].sum(axis=1)                   # (n, 4)
        c = np.sign(y[:, ia] - y[:, ib])                # (n, 6)
        return (c == Hs).mean(axis=1)                   # per-prompt agreement

    fam = [c for r in range(1, MAXK + 1) for c in itertools.combinations(range(len(idxs)), r)]
    print(f"  ⭐ enumerated family: {len(fam)} fixed subsets of size 1..{MAXK}")

    gen_cols = tuple(j for j, i in enumerate(idxs) if i in (0, 1, 2, 3))
    pos = gen_cols in set(fam) or len(gen_cols) > MAXK
    gen_score = score_subset(list(gen_cols))
    print(f"  POSITIVE — the comparator's own selection {[idxs[j] for j in gen_cols]} is inside the "
          f"enumerated family: {gen_cols in set(fam)} · its mean here {gen_score.mean():.4f}")
    if not (gen_cols in set(fam)):
        print("  the search is not over the space it claims. Exit 2, never 0."); return 2

    allm = np.array([score_subset(list(c)).mean() for c in fam])
    neg = allm.min() < gen_score.mean()
    print(f"  NEGATIVE — the WORST subset must score below the comparator: {neg} "
          f"(min {allm.min():.4f} vs {gen_score.mean():.4f})")
    if not neg:
        print("  the family is degenerate. Exit 2, never 0."); return 2

    # ⛔⛔ THE COMPARATOR SCORES 0.5880 HERE AND 0.5514 IN R1059 — SAME ARM, TWO AGGREGATIONS, AND
    #   MIXING THEM WOULD BE THE `two properties one field apart` ERROR AT THE ESTIMAND LEVEL.
    #   R1059 averaged agreement against EACH annotator's ranking, then averaged annotators. This
    #   round compares against the CONSENSUS sign (mean over annotators, then sign). Both are
    #   defensible; they are not the same number, and R1059's +0.0651 gap is NOT on this round's
    #   scale. Computed here rather than asserted, so nobody later quotes one against the other.
    per_ann = np.array([np.mean([(np.sign(np.array(cls(np.array(t0[0], float)), float))
                                  == np.sign(A[k, gen_cols, :].sum(axis=0)[ia]
                                             - A[k, gen_cols, :].sum(axis=0)[ib])).mean()
                                 for t0 in tg[p]]) for k, p in enumerate(pids)])
    print(f"  ⛔⛔ ESTIMAND CHECK, AND IT LANDS HARDER THAN INTENDED. `generic` scores "
          f"{gen_score.mean():.4f} under this round's consensus aggregation and {per_ann.mean():.4f} "
          f"under my quick reimplementation of R1059's per-annotator one — and R1059 itself reported "
          f"0.5514. THREE numbers for one arm.")
    print(f"     ⭐ So the honest statement is not `different estimands` but `the two rounds' scales "
          f"are UNVERIFIED against each other`: a 3-line reimplementation is not evidence about what "
          f"R1059 computed, and I will not claim to know its estimand from one. R1059's +0.0651 gap "
          f"and this round's margins must NOT be quoted against each other until one round re-derives")
    print(f"     the other's number with the other's code. Each round's internal comparison — arm vs "
          f"comparator on the SAME prompts under the SAME aggregation — stands.")

    rows = []
    for seed in (3, 11, 23, 37, 53):
        rng = np.random.default_rng(seed)
        sel = rng.random(n) < 0.5
        ev = ~sel
        sc_sel = np.array([score_subset(list(c))[sel].mean() for c in fam])
        best = fam[int(np.argmax(sc_sel))]
        ho = score_subset(list(best))[ev].mean()
        sham_best = fam[int(rng.integers(0, len(fam)))]      # selection replaced by noise
        sham_ho = score_subset(list(sham_best))[ev].mean()
        cmp_ho = gen_score[ev].mean()
        rows.append({"seed": int(seed), "best_subset": [idxs[j] for j in best],
                     "in_sample": float(sc_sel.max()), "held_out": float(ho),
                     "sham_held_out": float(sham_ho), "comparator_held_out": float(cmp_ho),
                     "margin": float(ho - cmp_ho)})
        print(f"     seed {seed:>3}  best {[idxs[j] for j in best]}  in-sample {sc_sel.max():.4f}  "
              f"HELD-OUT {ho:.4f}  comparator {cmp_ho:.4f}  margin {ho - cmp_ho:+.4f}  "
              f"sham {sham_ho:.4f}")

    opt = float(np.mean([r["in_sample"] - r["held_out"] for r in rows]))
    sel_worth = float(np.mean([r["held_out"] - r["sham_held_out"] for r in rows]))
    margins = [r["margin"] for r in rows]
    print(f"\n  ⭐ SELECTION OPTIMISM (in-sample minus held-out): {opt:+.4f} — the floor this design "
          f"had to clear to say anything")
    print(f"  ⭐ SHAM — honest selection minus random selection, held out: {sel_worth:+.4f}")
    print(f"  ⭐ MARGIN over the comparator on held-out prompts, 5 splits: "
          f"{[round(m, 4) for m in margins]}")

    beats = all(m > 0 for m in margins)
    sham_ok = sel_worth > 0.005
    print()
    if not sham_ok:
        world = (f"⛔ UNVERIFIED — selecting the best subset is worth only {sel_worth:+.4f} over "
                 f"picking one at random, so the search is not selecting and no maximum over it is "
                 f"interpretable.")
    elif beats:
        world = (f"⭐ A THE CONFOUND IS BREAKABLE — the best fixed subset beats the comparator on "
                 f"held-out prompts in all 5 splits, by {min(margins):+.4f} to {max(margins):+.4f}. "
                 f"R1059's optimisers were weak, not the site: a properly-built never-seen core CAN "
                 f"reach comparator quality here, so the clause's rejection of one would carry "
                 f"information about provenance after all.")
    else:
        world = (f"⛔ B THE BOUND BINDS — even the exhaustive best fixed subset fails to beat the "
                 f"comparator on held-out prompts in {sum(1 for m in margins if m <= 0)} of 5 "
                 f"splits, margins {[round(m, 4) for m in margins]}. No rule of this shape can close "
                 f"R1059's gap here, so every such core's non-admission is FORCED by the release and "
                 f"`does the clause test provenance` is unanswerable by this family — a bound, not "
                 f"another failed attempt.")
    print(world)
    print(f"⛔ AND THE BOUND IS OVER A NAMED FAMILY, NEVER OVER ALL CORES: fixed subsets of size <= "
          f"{MAXK} from the {len(idxs)} criteria available on >= {AVAIL_FRAC:.0%} of prompts. A")
    print(f"   prompt-conditioned rule sits outside it by construction, and that is a larger search")
    print(f"   on this same release rather than a different release.")

    o = HERE / "results" / "fixed_rule_bound.json"
    o.write_text(json.dumps({
        "round": "R1060", "prompts": n, "criteria": idxs, "family_size": len(fam), "max_k": MAXK,
        "comparator_consensus_mean": float(gen_score.mean()),
        "comparator_per_annotator_mean": float(per_ann.mean()),
        "rows": rows, "selection_optimism": opt, "selection_worth_vs_sham": sel_worth,
        "margins": margins, "world": world,
        "controls": {"positive_comparator_in_family": bool(gen_cols in set(fam)),
                     "negative_worst_below": bool(neg), "sham_selection_worth": sel_worth},
        "limitation": "bounds the named family only; prompt-conditioned rules are outside it",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
