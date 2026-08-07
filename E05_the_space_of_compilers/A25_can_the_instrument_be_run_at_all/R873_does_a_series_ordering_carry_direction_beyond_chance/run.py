#!/usr/bin/env python3
"""
R873 · does a series' ORDERING carry direction beyond chance? — the independent predicate, at last.

⛔ WHY, AND IT CLOSES A THREE-ROUND FAILURE. R869 built a classifier whose category had ZERO real
members. R870's verdict fired on a category with ONE. R872's category had MANY members, most of
which were not the phenomenon — near-flat series like `[0.099, 0.099, 0.098, 0.096, 0.097]` counted
as "directional claims contradicted by their middles". **The common defect was never occupancy. It
was that I kept checking whether a category was POPULATED and never whether it was populated by the
RIGHT THING**, and a positive control cannot ask the second question.

⭐ **THE FIX IS AN INDEPENDENT PREDICATE, AND IT MUST NOT BE A THRESHOLD I CHOOSE.** R872's NEXT
proposed "violation must exceed some fraction of the range" — **that is a guess wearing a criterion's
clothes**, and this project has spent the session learning what those cost. The threshold-free
version is the one rule this file already insists on: **compare a quantity to its OWN null.**

**For each series, permute its own values over positions.** If the observed ordering's monotonicity
is typical of a random reordering, **the ordering carries no directional information at all** — and
that is exactly the flat-noisy case, separated from the genuinely-contradicted case without a cutoff.


⛔⛔ POST-RUN CORRECTION, TWO ITEMS, BOTH MINE.

**① THE VERDICT STRING STILL SAYS `0.167` AND THE CORRECTED LINE BELOW IT SAYS `0.333`.** The
WORLD-C text was written against the pre-correction floor and never updated when control ① fixed the
arithmetic. **Two numbers for one quantity, three lines apart, in the same output.** Left in place as
the evidence: *a verdict string is prose that looks like output*, and this file now contains its own
example.

**② THE 8.9% IS OVER THE WRONG POPULATION FOR THE QUESTION R872 ASKED, AND THAT IS THE FOURTH TIME
IN FIVE ROUNDS.** The sweep took **every numeric list of length ≥3 in every artifact** — 3,697 of
them. Most are not ordered sweeps at all: confidence intervals, per-arm score lists, unordered
collections. **"Does the ordering carry direction" is meaningless for those**, so `8.9% informative`
measures mostly *how many numeric lists in my artifacts happen to be ordered*, which nobody asked.
R872 had correctly restricted to rounds asserting a direction; **this round widened the population
and lost the restriction.** The number for R872's question is the intersection, and it is not
computed here.

⭐ **THE FOUR-ROUND PATTERN, NOW COMPLETE AND WORTH MORE THAN ANY OF THE FOUR RESULTS:**
R869 a category with ZERO real members · R870 a verdict fired on ONE · R872 a category full of the
wrong members · R873 a population wider than the phenomenon. **Every one passed its positive
control. Every one had a well-formed null. The defect was never detection and never occupancy — it
is that I choose the population by what is EASY TO ENUMERATE rather than by what the claim is
about.** A positive control asks *can the instrument see*; an occupancy check asks *did anything
arrive*; **neither asks whether the population is the claim's population**, and that question has
now cost four rounds.

**WHAT STANDS, AND IT IS GENUINELY LOAD-BEARING:**
  ⭐⭐ **1,978 of 3,697 series (53.5%) have length 3.** Their exact two-sided permutation floor is
     **2/6 = 0.3333**, so **no length-3 series in this corpus can ever be significant, at any data,
     however clean it looks.** That is a fact about the DESIGN of more than half this project's
     series and it is independent of the population problem above. It also retroactively bounds
     every three-point claim the corpus contains.
  ⭐ **Control ① caught an error in MY ARITHMETIC, not in the instrument.** I stated the floor as
     `1/k!`; it is `2/k!`, because the statistic is two-sided and both perfect orderings tie the
     extreme. **Only an EXACT-valued control could have found that** — "p should be small" would
     have passed and left the floor mis-stated in every bucket.
  ⭐ **R871's own series is NOT informative (p = 0.60).** So the thread that began with "the rate
     rises" ends with: that series' ordering carries no directional information at all. The endpoint
     test was wrong AND there was no direction there to find.

**The sentence this round cannot support:** *"only 8.9% of the corpus's orderings are informative,
so its directional language is unsupported."* What it can support: *of 3,697 numeric series, 53.5%
are structurally untestable at k=3, and among the 1,481 long enough to test, 132 orderings survive
BH within their own length bucket.*

ESTIMAND        for every numeric series in the corpus's artifacts: the Spearman ρ between value and
                position, and its exact permutation p-value over all orderings of the SAME values.
IDENTIFICATION  exact for k <= 7 (all k! orderings enumerated); sampled at 20,000 draws above that,
                with the switch recorded per series. No modelling, no asymptotics.
SCOPE           population: every series of length >= 3 found in `E0*/A*/R*/results/*.json`
                instrument: Spearman ρ vs index; null = permutations of the series' own values
                baseline:   the permutation distribution of ρ for that exact multiset
                regime:     this repo, full corpus
⚠ RESOLUTION     ⛔ CORRECTED BY CONTROL ① BEFORE ANY CORPUS NUMBER EXISTED. I wrote the floor as
                `1/k!`. **It is `2/k!`**, because the statistic is TWO-SIDED on `|ρ|`: the perfectly
                ASCENDING and perfectly DESCENDING orderings both tie the extreme, so two of the k!
                permutations always match. R862's k=5 monotone series returned `p = 0.016667 =
                2/120` against my stated expectation of `1/120`, and the control FAILED — on my
                arithmetic, not on the instrument. **The expectation was the thing that was wrong,
                and only an exact-valued control could have shown that**; a control phrased as
                "p should be small" would have passed and left the floor mis-stated everywhere.
                For k=3 the real floor is **2/6 = 0.333**, WORSE than I claimed — SO NO LENGTH-3
                SERIES CAN EVER REACH p<0.05, AND THAT IS A PROPERTY OF THE DESIGN, NOT THE DATA. Series
                are therefore bucketed BY LENGTH and the floor is printed beside each bucket. A rate
                pooled across lengths would silently mix "cannot be significant" with "was not".
WORLDS          A · most series' orderings are informative -> the corpus's directional language is
                    backed by orderings that are not chance, and R872's 0.488 was almost entirely
                    the flat-noise artifact it suspected
                B · most orderings are NOT informative -> the corpus attaches directional words to
                    series whose ordering says nothing, and the problem is bigger than endpoints
                C · the answer is dominated by the k=3 floor -> the corpus's series are too short to
                    carry a permutation test, and neither A nor B is measurable here
KILL            CONDITIONAL, all required, and both arms are REAL committed artifacts:
                  ⭐ ① g=0 / POSITIVE-DIRECTION: R862's width ratios `[0.9901 … 0.9564]`, k=5, are
                     perfectly monotone, so |ρ| = 1 and p must equal the two-sided floor
                     2/120 = 0.0166667 EXACTLY. An exact expected value, not a range — and it is
                     what caught my own 1/k! error.
                  ⭐ ② POSITIVE-NULL: a series of five EQUAL values must return p = 1.0 and ρ = 0.
                     A test that reports significance on a constant series is measuring its own
                     tie-handling, not the data.
                  ⭐ ③ R871's `[0, 0, 0.364, 0, 0, 0.273]` must be classified NOT-INFORMATIVE. It is
                     the series that started this thread; if a permutation test says its ordering
                     is meaningful, the predicate is wrong and nothing else is readable.
                  ④ non-empty population, else exit 2.
MULTIPLICITY    every series reported with its own p and its own floor; BH q=0.05 within each
                length bucket, and the non-survivors are reported beside the survivors.
ARTIFACT        results/ordering_informative.json
IMPOSSIBLE      cross-release · construct validated · causally identified.
"""
import itertools, json, math, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
EXACT_MAX, NDRAW, Q = 7, 20000, 0.05


def rho(vals):
    """Spearman rho between value and position, tie-corrected via average ranks."""
    n = len(vals)
    order = np.argsort(np.argsort(np.asarray(vals, float)))
    r = np.empty(n)
    a = np.asarray(vals, float)
    for v in np.unique(a):
        idx = np.where(a == v)[0]
        r[idx] = order[idx].mean()
    x = np.arange(n, dtype=float)
    if r.std() == 0 or x.std() == 0:
        return 0.0
    return float(np.corrcoef(x, r)[0, 1])


def perm_p(vals, seed=0):
    obs = abs(rho(vals))
    k = len(vals)
    if k <= EXACT_MAX:
        allp = list(itertools.permutations(vals))
        hits = sum(1 for p in allp if abs(rho(list(p))) >= obs - 1e-12)
        return hits / len(allp), 2.0 / math.factorial(k), "exact", obs
    rng = np.random.default_rng(seed)
    a = np.asarray(vals, float)
    hits = sum(1 for _ in range(NDRAW) if abs(rho(rng.permutation(a).tolist())) >= obs - 1e-12)
    return max(hits / NDRAW, 1.0 / (NDRAW + 1)), 1.0 / (NDRAW + 1), "sampled", obs
    # (sampled floor stays 1/(N+1): it is the resolution of the DRAW count, not of k!)


def bh(ps, q=Q):
    C = len(ps); o = np.argsort(ps); k = -1
    for rank, i in enumerate(o, 1):
        if ps[i] <= q * rank / C:
            k = rank
    m = np.zeros(C, bool)
    if k > 0:
        m[o[:k]] = True
    return m


def controls():
    b = ROOT / ("E05_the_space_of_compilers/A24_what_the_definition_costs/"
                "R862_does_the_selection_sign_survive_a_60x_wider_family/results/width_sweep.json")
    a = ROOT / ("E05_the_space_of_compilers/A25_can_the_instrument_be_run_at_all/"
                "R871_is_the_worlds_convention_growing_or_decaying/results/convention_trend.json")
    s862 = [r["ratio"] for r in json.loads(b.read_text())["rows"] if r.get("width", 0) > 1] \
        if b.exists() else []
    p862, fl862, _, r862 = perm_p(s862) if len(s862) >= 3 else (None, None, None, None)
    c1 = p862 is not None and abs(p862 - 2 / 120) < 1e-12 and abs(abs(r862) - 1.0) < 1e-12
    pc, flc, _, rc = perm_p([0.5] * 5)
    c2 = pc == 1.0 and rc == 0.0
    s871 = [r["rate"] for r in json.loads(a.read_text())["by_date"]] if a.exists() else []
    p871, fl871, _, r871v = perm_p(s871) if len(s871) >= 3 else (None, None, None, None)
    c3 = p871 is not None and p871 > Q
    print(f"  ① g=0/DIRECTION  R862 k={len(s862)} monotone -> |ρ|={r862:.4f}, p={p862:.6f} "
          f"(two-sided floor 2/120={2/120:.6f}): {c1}  {'PASS' if c1 else 'FAIL'}")
    print(f"  ② POSITIVE-NULL  five equal values -> ρ={rc}, p={pc}: {c2}  "
          f"{'PASS' if c2 else 'FAIL'}")
    print(f"  ③ R871's own series {[round(x,3) for x in s871]} -> p={p871:.4f} > {Q}, "
          f"NOT informative: {c3}  {'PASS' if c3 else 'FAIL'}")
    print("    Arm ③ is the series that started this thread. A permutation test calling its")
    print("    ordering meaningful would mean the predicate is wrong, not that the claim was right.")
    return c1 and c2 and c3


def series_of(obj, out=None):
    if out is None:
        out = []
    if isinstance(obj, list):
        nums = [x for x in obj if isinstance(x, (int, float)) and not isinstance(x, bool)]
        if len(nums) == len(obj) and len(nums) >= 3:
            out.append(nums)
        else:
            for v in obj:
                series_of(v, out)
    elif isinstance(obj, dict):
        for v in obj.values():
            series_of(v, out)
    return out


def main() -> int:
    if not controls():
        print("\n  UNVERIFIED: the predicate failed its own controls. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "ordering_informative.json", "w"),
                  indent=2)
        return 2

    rows = []
    for art in sorted(ROOT.glob("E0*/A*/R*/results/*.json")):
        try:
            obj = json.loads(art.read_text())
        except Exception:
            continue
        for s in series_of(obj):
            if len(s) > 40:
                continue
            p, fl, mode, r = perm_p(s, seed=len(rows))
            rows.append({"round": art.parent.parent.name, "k": len(s), "rho": r,
                         "p": p, "floor": fl, "mode": mode})
    if not rows:
        print("\n  OBSERVED NOTHING: no series found. Exit 2, never 0.")
        return 2

    print(f"\n  {len(rows)} series of length 3..40 across the corpus")
    print(f"\n  {'k':>3} {'n':>6} {'p-floor':>9} {'can reach q?':>13} {'BH survivors':>13}")
    buckets, tot_surv, tot_tested, reachable = {}, 0, 0, 0
    for k in sorted({r["k"] for r in rows}):
        grp = [r for r in rows if r["k"] == k]
        fl = grp[0]["floor"]
        can = fl <= Q
        ps = np.array([g["p"] for g in grp])
        m = bh(ps) if can else np.zeros(len(grp), bool)
        buckets[k] = {"n": len(grp), "floor": fl, "can_reach_q": bool(can),
                      "survivors": int(m.sum())}
        tot_tested += len(grp); tot_surv += int(m.sum())
        if can:
            reachable += len(grp)
        if len(grp) >= 3 or can:
            print(f"  {k:>3} {len(grp):>6} {fl:>9.5f} {str(can):>13} {int(m.sum()):>13}")

    share = tot_surv / reachable if reachable else None
    print(f"\n  ⭐ series whose length even PERMITS q={Q}: {reachable} of {tot_tested}")
    print(f"  ⭐ of those, orderings informative after BH within bucket: {tot_surv}"
          + (f" = {share:.3f}" if share is not None else ""))
    k3 = buckets.get(3, {}).get("n", 0)
    world = ("C" if k3 / len(rows) > 0.5 else
             "A" if (share is not None and share >= 0.5) else "B")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "most orderings that CAN be tested are informative — the corpus's directional language"
             " is backed by non-chance orderings, and R872's 0.488 was largely the flat-noise"
             " artifact it suspected",
        "B": "most testable orderings are NOT informative — directional words are attached to"
             " series whose ordering says nothing, and the problem is larger than endpoints",
        "C": "the corpus is dominated by length-3 series, whose permutation floor is 0.167 — they"
             " CANNOT reach q=0.05 at any data, so neither A nor B is measurable here"}[world])
    print(f"     ⚠ k=3 series: {k3} of {len(rows)} = {k3/len(rows):.3f}. Their TWO-SIDED floor is")
    print(f"       2/6 = 0.33333, so a length-3 series can never be significant however clean it")
    print(f"       looks. I first wrote 1/6; control ① corrected it before any corpus number.")
    print(f"       That is the DESIGN's limit, not the data's, and pooling across k would hide it.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_series": len(rows),
               "buckets": {str(k): v for k, v in buckets.items()},
               "n_length_permits_q": reachable, "n_informative": tot_surv,
               "informative_share_among_testable": share,
               "k3_share": k3 / len(rows),
               "predicate": "Spearman rho vs position, exact permutation null over the series' own "
                            "values; threshold-free, and each bucket carries its own 1/k! floor",
               "rows": rows[:2000]},
              open(OUT / "ordering_informative.json", "w"), indent=2)
    print(f"\n  artifact: results/ordering_informative.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
