"""R226 -- pricing the observable. R224's OTHER assumption, and it is the expensive one.

R224 bounded identifiability by log2 a(m), the number of weak orderings of m candidates. R225
attacked the rater half of that and it survived. This attacks the other half:

    "the observable is the ORDERING."

It need not be. A richer per-prompt observable raises H_have without adding a single candidate, and
the release chose which one to ship. So: price every candidate observable in bits, and ask which
ones close the 10.41-bit gap at m=4.

TWO NUMBERS PER OBSERVABLE, AND THEY ARE NOT THE SAME NUMBER
    CAPACITY   log2 |possible values|            -- a DERIVATION, an upper bound, assumes uniform use
    ACHIEVED   the empirical entropy in the release -- a MEASUREMENT, and it can only be lower
    R224 used CAPACITY. If achieved << capacity, R224 was OPTIMISTIC and the situation is worse
    than it published. That is the way this round can embarrass me, which is why it is worth running.

ESTIMAND        for each observable O: H_cap(O) and H_ach(O), and the sign of H(O) - log2 C(n,k).
IDENTIFICATION  H_cap is exact arithmetic. H_ach is a plug-in entropy over a finite sample and is
                BIASED DOWNWARD; Miller-Madow correction reported beside the raw value, and the
                bias is largest exactly where the alphabet is largest, i.e. where it matters most.
SCOPE           population: the 18,384 released assessments. instrument: none for the ordering and
                veto (released fields); the satisfaction observable is NOT in the release at all.
                baseline: log2 C(15,4) = 10.41 bits. regime: m=4, n=15 median, k=4.
WORLDS          W1 the release's observable is near its capacity -> R224's bound is tight
                W2 it is far below capacity                      -> R224 was optimistic
POSITIVE CTRL   a synthetic corpus drawn UNIFORMLY over weak orderings must return H_ach = log2 75
                = 6.23. If the estimator cannot recover a known entropy it cannot measure this one.
                Fails at g=0: a degenerate corpus (one ordering repeated) must return 0.000.
NEGATIVE CTRL   the degenerate corpus above.
NOISE FLOOR     5 bootstrap resamples of the assessment set.
MULTIPLICITY    6 observables x 2 estimators (plug-in, Miller-Madow); whole grid printed.
IMPOSSIBLE      the ACHIEVED entropy of per-criterion satisfaction, because the release does not
                ship it -- only its capacity can be priced. That absence IS the finding.
"""
from __future__ import annotations

import json, math, pathlib, sys, collections, re
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
L = "ABCD"
M = 4
N_MED, K = 15, 4
SEEDS = [0, 1, 2, 3, 4]


def fubini(m):
    a = [1]
    for i in range(1, m + 1):
        a.append(sum(math.comb(i, j) * a[i - j] for j in range(1, i + 1)))
    return a[m]


def canon(rank):
    """⚠ THE FIRST VERSION COUNTED RAW STRINGS and returned 6.3868 bits against a capacity of
    6.2288 -- 102.5%, which is arithmetically IMPOSSIBLE: an empirical entropy cannot exceed the
    log of its own alphabet. That impossibility is the only reason the bug surfaced.
    The cause: "A=B>D=C" and "A=B>C=D" are the SAME weak ordering written two ways. The string
    encodes an order WITHIN a tie group, which is not information about the ranking. I was
    measuring the entropy of the ENCODING, not of the observable.
    Canonicalising sorts inside every tie group, so one weak ordering has exactly one key."""
    tiers = [sorted(t.split("=")) for t in str(rank).replace(" ", "").split(">")]
    return ">".join("=".join(t) for t in tiers)


def entropy(counts):
    c = np.array([v for v in counts.values() if v > 0], float)
    if not len(c):
        return 0.0, 0.0
    p = c / c.sum()
    H = float(-(p * np.log2(p)).sum())
    mm = H + (len(c) - 1) / (2 * c.sum() * math.log(2))     # Miller-Madow
    return H, float(mm)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(l) for l in (DATA / "merged_comparisons_annotators.jsonl").open()]

    obs = {"world_ordering": collections.Counter(),
           "personal_ordering": collections.Counter(),
           "veto_set": collections.Counter(),
           "ordering_plus_veto": collections.Counter()}
    for r in rows:
        rb = r.get("ranking_blocks") or {}
        w = (rb.get("world") or [{}])[0].get("ranking")
        if w:
            obs["world_ordering"][canon(w)] += 1
        p_ = (rb.get("personal") or [{}])
        pr = p_[0].get("ranking") if p_ and isinstance(p_[0], dict) else None
        if pr:
            obs["personal_ordering"][canon(pr)] += 1
        vs = set()
        for u in (rb.get("unacceptable") or []):
            for t in (u.get("rating") or []):
                mm_ = re.match(r"\s*([A-Z])\b", str(t))
                if mm_:
                    vs.add(mm_.group(1))
        if rb.get("personal"):                       # veto only exists in the long form
            obs["veto_set"][frozenset(vs)] += 1
            if w:
                obs["ordering_plus_veto"][(canon(w), frozenset(vs))] += 1

    CAP = {"world_ordering": math.log2(fubini(M)),
           "personal_ordering": math.log2(fubini(M)),
           "veto_set": M,                                    # any subset of the m shown
           "ordering_plus_veto": math.log2(fubini(M) * 2 ** M),
           "graded_5pt_per_response": M * math.log2(5),
           "graded_10pt_per_response": M * math.log2(10),
           "pairwise_confidence_5pt": math.comb(M, 2) * math.log2(5),
           "per_criterion_satisfaction": N_MED * M * 1.0}    # n x m binary -- NOT in the release
    need = math.log2(math.comb(N_MED, K))

    print("=== controls, before any number is read ===")
    rng = np.random.default_rng(0)
    uni = collections.Counter(rng.integers(0, fubini(M), size=200000).tolist())
    hu, mu = entropy(uni)
    deg = collections.Counter({"A>B>C>D": 200000})
    hd, md = entropy(deg)
    print(" POSITIVE  uniform over the %d weak orderings -> H %.4f (MM %.4f), target %.4f  %s"
          % (fubini(M), hu, mu, math.log2(fubini(M)),
             "OK" if abs(hu - math.log2(fubini(M))) < 0.02 else "ESTIMATOR BROKEN"))
    print(" NEGATIVE  one ordering repeated             -> H %.4f (MM %.4f), target 0.0000  %s"
          % (hd, md, "OK" if hd < 1e-9 else "FIRES AT ZERO"))

    print("\n=== the price list.  H_need = log2 C(%d,%d) = %.2f bits ===" % (N_MED, K, need))
    print("%-30s %9s %9s %9s %7s   %s"
          % ("observable", "capacity", "achieved", "MillerMad", "n", "closes the gap?"))
    res = {"H_need": need, "m": M, "n_median": N_MED, "k": K, "observables": {}}
    for name, cap in CAP.items():
        if name in obs and obs[name]:
            h, mm_ = entropy(obs[name])
            n_ = sum(obs[name].values())
            ach, mmv = "%9.4f" % h, "%9.4f" % mm_
            use = mm_
        else:
            h = mm_ = None
            ach, mmv, n_ = "  NOT SHIPPED", "         -", 0
            use = cap
        gap = "YES" if use >= need else "no"
        print("%-30s %9.4f %9s %9s %7d   %s (on %s)"
              % (name, cap, ach, mmv, n_, gap, "achieved" if h is not None else "capacity only"))
        res["observables"][name] = {"capacity": cap, "achieved": h, "miller_madow": mm_,
                                    "n": n_, "closes_gap": bool(use >= need)}

    # noise floor on the achieved entropies
    print("\n=== noise floor: 5 bootstrap resamples of the assessments ===")
    for name in ("world_ordering", "ordering_plus_veto"):
        if not obs[name]:
            continue
        keys = list(obs[name]); w_ = np.array([obs[name][k_] for k_ in keys], float)
        p = w_ / w_.sum(); hs = []
        for s in SEEDS:
            r2 = np.random.default_rng(s)
            draw = r2.multinomial(int(w_.sum()), p)
            hs.append(entropy({k_: int(v) for k_, v in zip(keys, draw)})[0])
        print("  %-24s %s   spread %.4f" % (name, " ".join("%.4f" % x for x in hs),
                                            max(hs) - min(hs)))
        res["observables"][name]["bootstrap_spread"] = float(max(hs) - min(hs))

    wo = res["observables"]["world_ordering"]
    for nm in ("world_ordering", "personal_ordering"):
        if res["observables"][nm]["achieved"] is not None:
            assert res["observables"][nm]["achieved"] <= CAP[nm] + 1e-9, (
                "achieved entropy %.4f exceeds capacity %.4f for %s -- impossible, so it is a "
                "coding error, not a measurement" % (res["observables"][nm]["achieved"],
                                                     CAP[nm], nm))
    print("\n  [checked] no achieved entropy exceeds its own capacity")
    print("\n" + "=" * 78)
    print("VERDICT")
    print("=" * 78)
    ratio = wo["miller_madow"] / CAP["world_ordering"]
    print(" the release's own observable uses %.1f%% of its capacity (%.4f of %.4f bits)"
          % (100 * ratio, wo["miller_madow"], CAP["world_ordering"]))
    if ratio < 0.9:
        print(" => R224 was OPTIMISTIC. It bounded with capacity; the achieved figure is lower,")
        print("    so the deficit is %.2f bits, not %.2f."
              % (need - wo["miller_madow"], need - CAP["world_ordering"]))
    closes = [k_ for k_, v in res["observables"].items() if v["closes_gap"]]
    print("\n observables that close the gap at m=4: %s" % (", ".join(closes) or "NONE"))
    print(" and the largest of them by far is the one field the release does NOT ship:")
    print("   per-criterion satisfaction, %d x %d = %.0f bits against the ordering's %.2f"
          % (N_MED, M, CAP["per_criterion_satisfaction"], wo["miller_madow"]))
    res["capacity_used_fraction"] = float(ratio)
    (OUT / "observable_price_list.json").write_text(json.dumps(res, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
