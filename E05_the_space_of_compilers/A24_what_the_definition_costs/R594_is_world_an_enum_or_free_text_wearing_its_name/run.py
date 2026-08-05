#!/usr/bin/env python3
"""
R594 -- is `world` an enum, or free text wearing an enum's name?

CHECK #194 FOUND TWO ERRORS IN R593'S CLOSING SENTENCE, both quantifiers over my own work:
  ⛔ "verdict and world are the ONLY keys with meaningful prevalence" -- FOUR keys cleared the
     20% floor (verdict 0.49, world 0.44, controls 0.26, n_prompts 0.22). "Only two" is true
     solely under a >=40% threshold I never stated. All four are tested here.
  ⛔ "the 239 rounds that write one" -- 239 is the CODE-BEARING count quoted as a corpus count.
     The corpus has 569 rounds with artifacts. Recomputed over the whole population below.

⚠ AND "free text vs enum" IS NOT MEASURABLE BY LOOKING AT VALUES AND JUDGING THEM. That is
the rubric-invention failure R593 already refused once. The non-invented operational
definition: an ENUM's distinct-value count SATURATES as more rounds are sampled; FREE TEXT
grows about linearly. That is a growth exponent, and it is computable without any opinion
about what a value means.

ESTIMAND        beta_key = the exponent in  distinct_values(n) ~ n^beta , estimated by
                subsampling n rounds that write `key`, over a log-spaced sweep of n.
                beta ~ 0 => a closed vocabulary (enum). beta ~ 1 => a fresh value per round
                (free text). Anything between is a partially-conventionalised field.
IDENTIFICATION  Identified: every value is on disk and n sweeps the full range. ⚠ beta is
                estimated by OLS on log-log points, so it is a SUMMARY of a curve, not a
                parameter of a generative model -- reported with the curve beside it, never
                alone, because a saturating curve and a linear one can share a fitted slope
                over a narrow range.
SCOPE           population : every round in E01..E05 whose artifacts contain the key at any
                             depth (recomputed per key, never assumed from R593)
                instrument : json value -> a normalised string. Lists/dicts are serialised,
                             so a structural difference counts as a different value -- stated
                             because it BIASES beta UPWARD and therefore against the enum
                             hypothesis, which is the conservative direction for HB8.
                baseline   : two synthetic keys built on the SAME population -- a 3-value enum
                             (floor) and a unique-per-round field (ceiling)
                regime     : as committed at this sha
WORLDS          A ENUM: beta sits at the synthetic-enum floor -> the key is a real closed
                  vocabulary and HB8 is satisfied. Nothing to fix.
                B FREE TEXT: beta sits at the unique-per-round ceiling -> the key is a
                  text_free field wearing an enum's name, which HB8 calls a schema bug, and
                  every GROUP BY over the corpus's own verdicts is already broken.
                C PARTIAL: beta strictly between the two -> a core vocabulary plus a tail of
                  one-offs. Then the actionable quantity is the SIZE OF THE TAIL, not beta.
KILL            pre-registered, evaluated ONLY if floor and ceiling separate:
                  if beta_key is within the floor's seed spread -> world A for that key and no
                  free-text claim is admissible about it. If floor and ceiling do NOT
                  separate, the instrument is degenerate and every key is UNVERIFIED.
POSITIVE CTRL   the synthetic unique-per-round key must return beta near 1 (the instrument can
                see free text). FLOOR/CEILING pair, per §4: require floor < observed < ceiling
                to be a MEANINGFUL placement, and report when it is not.
NEGATIVE CTRL   the synthetic 3-value enum on the same population must return beta near 0.
                If it does not, the estimator is broken and nothing here is admissible.
PLACEBO         shuffling which round holds which value must leave beta UNCHANGED -- beta is a
                property of the value MULTISET, not of the pairing. A placebo that moved would
                mean the estimator is reading the wrong structure.
SEEDS           0, 1, 2 on every subsample; the seed spread is reported as the resolution.
MULTIPLICITY    4 real keys x 8 sweep points x 3 seeds, plus 2 synthetic keys. All reported.
ARTIFACT        results/vocabulary.json
IMPOSSIBLE      construct validity for "is this vocabulary MEANINGFUL": beta measures whether
                a vocabulary is closed, never whether its members are the right ones. A key
                could take exactly 3 values and all of them nonsense. Establishing that needs
                an external reader, which this site does not have.
"""
from __future__ import annotations
import json, math, pathlib, random, re, sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
# ⚠ `n_prompts` IS A SCALAR, NOT A VOCABULARY. v1 classified it B FREE TEXT off beta=+1.0677,
# which is my instrument committing a category error: HB8 types a count as scalar_with_range,
# and "does its vocabulary saturate" is not a question about a count. It is kept in the sweep
# and reported, but under its own type, because DROPPING it silently would hide the defect.
KEYS = ("verdict", "world", "controls")
SCALARS = ("n_prompts",)


def walk(o, key):
    """Every value stored under `key` at any depth, normalised to a string."""
    if isinstance(o, dict):
        for k, v in o.items():
            if str(k).lower() == key:
                yield json.dumps(v, sort_keys=True) if isinstance(v, (dict, list)) else str(v)
            yield from walk(v, key)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v, key)


def corpus():
    """round-id -> parsed json objects."""
    out = {}
    for ep in sorted(ROOT.glob("E0*")):
        for d in sorted(ep.glob("A*/R[0-9]*")):
            if not d.is_dir():
                continue
            m = re.match(r"R(\d+)", d.name)
            if not m or not (d / "results").is_dir():
                continue
            objs = []
            for f in sorted((d / "results").rglob("*.json")):
                try:
                    objs.append(json.loads(f.read_text()))
                except Exception:
                    pass
            if objs:
                out[int(m.group(1))] = objs
    return out


def values_for(C, key):
    """round-id -> the SET of values that round writes under key (rounds writing none are out)."""
    out = {}
    for rid, objs in C.items():
        vs = set()
        for o in objs:
            vs |= set(walk(o, key))
        if vs:
            out[rid] = vs
    return out


def beta(per_round, seeds=(0, 1, 2)):
    """Exponent of distinct(n) ~ n^beta over a log-spaced sweep, plus the raw curve."""
    ids = sorted(per_round)
    N = len(ids)
    if N < 8:
        return None, [], None
    ns, x = [], 1
    while x < N:
        ns.append(x)
        x = max(x + 1, int(x * 2))
    ns.append(N)
    ns = sorted(set(ns))[-8:] if len(ns) > 8 else ns
    curve, per_seed = [], {s: [] for s in seeds}
    for n in ns:
        cnts = []
        for s in seeds:
            rng = random.Random(1000 * s + n)
            samp = rng.sample(ids, n)
            d = len({v for i in samp for v in per_round[i]})
            cnts.append(d)
            per_seed[s].append((n, d))
        curve.append((n, sum(cnts) / len(cnts), min(cnts), max(cnts)))

    def ols(pts):
        pts = [(math.log(n), math.log(d)) for n, d in pts if n > 1 and d > 0]
        if len(pts) < 3:
            return None
        mx = sum(p[0] for p in pts) / len(pts)
        my = sum(p[1] for p in pts) / len(pts)
        den = sum((p[0] - mx) ** 2 for p in pts)
        return (sum((p[0] - mx) * (p[1] - my) for p in pts) / den) if den else None

    bs = [b for b in (ols(per_seed[s]) for s in seeds) if b is not None]
    if not bs:
        return None, curve, None
    return sum(bs) / len(bs), curve, (min(bs), max(bs))


def main():
    C = corpus()
    if not C:
        print("UNRUNNABLE: no round shipped a readable JSON artifact. Exit 2, never 0.")
        return 2
    print(f"CORPUS  rounds with >=1 readable JSON artifact = {len(C)}")

    # ---- CONTROLS FIRST: build the floor and the ceiling on the SAME population ------
    print(f"\n─── CONTROLS (floor and ceiling, built on the real population) ───")
    ids = sorted(C)
    rng = random.Random(0)
    synth_enum = {i: {rng.choice(["A", "B", "C"])} for i in ids}
    synth_free = {i: {f"free-{i}-{rng.random()}"} for i in ids}
    b_enum, c_enum, s_enum = beta(synth_enum)
    b_free, c_free, s_free = beta(synth_free)
    print(f"  NEGATIVE  synthetic 3-value enum      : beta = {b_enum:+.4f}  "
          f"seed spread [{s_enum[0]:+.4f},{s_enum[1]:+.4f}]  distinct at n={len(ids)}: "
          f"{c_enum[-1][1]:.0f}")
    print(f"  POSITIVE  synthetic unique-per-round  : beta = {b_free:+.4f}  "
          f"seed spread [{s_free[0]:+.4f},{s_free[1]:+.4f}]  distinct at n={len(ids)}: "
          f"{c_free[-1][1]:.0f}")
    separated = (b_free - b_enum) > 0.5
    print(f"  -> floor/ceiling separation = {b_free - b_enum:+.4f}  "
          f"{'PASS' if separated else '⛔ FAIL -- the estimator is degenerate, everything below is UNVERIFIED'}")

    # PLACEBO: beta is a property of the value multiset, not of the pairing
    shuffled = list(synth_free.values())
    rng.shuffle(shuffled)
    b_plc, _, _ = beta(dict(zip(ids, shuffled)))
    plc_ok = abs(b_plc - b_free) < 0.05
    print(f"  PLACEBO   pairing shuffled (must NOT move): beta = {b_plc:+.4f} vs "
          f"{b_free:+.4f}  -> {'PASS' if plc_ok else '⛔ FAIL -- the estimator reads the pairing'}")

    controls_fired = separated and plc_ok

    # ---- THE MEASUREMENT ------------------------------------------------------------
    def matched_ceiling(pr, seed=7):
        """A unique-per-round ceiling MATCHED to this key's values-per-round distribution.

        ⛔ v1 used a single-valued ceiling (exactly one value per round), so beta was pinned at
        1.0000 and a real key writing SETS could exceed it -- n_prompts returned +1.0677. A
        ceiling the object under test can jump over is not a ceiling (§4, floor/ceiling row).
        """
        r2 = random.Random(seed)
        return {i: {f"u-{i}-{j}-{r2.random()}" for j in range(len(vs))}
                for i, vs in pr.items()}

    print(f"\n─── THE THREE VOCABULARY KEYS + 1 SCALAR (all four -- R593's closing line said 'only two') ───")
    rows, tested, surviving = {}, 0, 0
    for key in KEYS + SCALARS:
        pr = values_for(C, key)
        b, curve, spread = beta(pr)
        allv = Counter(v for vs in pr.values() for v in vs)
        tested += 1
        if b is None:
            print(f"  {key:<10} n={len(pr):<4} UNRUNNABLE (fewer than 8 rounds write it)")
            rows[key] = {"n_rounds": len(pr), "beta": None, "world": "UNRUNNABLE"}
            continue
        # the ceiling is rebuilt PER KEY, matched to its values-per-round distribution
        b_ceil, _, s_ceil = beta(matched_ceiling(pr))
        vpr = sum(len(v) for v in pr.values()) / len(pr)
        if key in SCALARS:
            w = ("SCALAR -- beta is the WRONG INSTRUMENT for a count; HB8 types this "
                 "scalar_with_range, and its vocabulary is unbounded BY DEFINITION")
        elif not controls_fired:
            w = "UNVERIFIED"
        elif b_ceil is None or (b_ceil - s_enum[1]) < 0.5:
            w = "UNVERIFIED -- the matched ceiling does not separate from the floor"
        elif b <= s_enum[1] + 0.05:
            w = "A ENUM"
        elif b >= b_ceil - 0.05:
            w = "B FREE TEXT"
        else:
            w = "C PARTIAL"
            surviving += 1
        top = allv.most_common(3)
        print(f"  {key:<10} n={len(pr):<4} distinct={len(allv):<5} beta={b:+.4f} "
              f"[{spread[0]:+.4f},{spread[1]:+.4f}]  vs MATCHED ceiling "
              f"{b_ceil:+.4f} (vals/round {vpr:.2f})")
        print(f"             -> {w}")
        print(f"             top-3: " + " · ".join(f"{v[:34]!r}×{c}" for v, c in top))
        singl = sum(1 for v, c in allv.items() if c == 1)
        print(f"             tail: {singl}/{len(allv)} values occur ONCE = "
              f"{singl/len(allv):.1%} of the vocabulary")
        rows[key] = {"n_rounds": len(pr), "distinct": len(allv), "beta": b,
                     "matched_ceiling_beta": b_ceil, "values_per_round": vpr,
                     "seed_spread": spread, "world": w, "curve": curve,
                     "singleton_frac": singl / len(allv),
                     "top3": [[v[:120], c] for v, c in top]}

    # ---- STRONGEST CONFOUND, written before the run: AM I THE CAUSE? ----------------
    # R592 measured a 13.6x late-half decay in code persistence. If the singleton tail is
    # also concentrated late, the "corpus has no enum" finding is really "I stopped using
    # one", which is a different object and a different fix.
    print(f"\n─── CONFOUND: is the tail RECENT (i.e. mine)? ───")
    med = sorted(C)[len(C) // 2]
    conf = {}
    for key in KEYS:
        pr = values_for(C, key)
        if not pr:
            continue
        early = [v for i, vs in pr.items() if i <= med for v in vs]
        late = [v for i, vs in pr.items() if i > med for v in vs]
        def short(vs):
            return (sum(1 for v in vs if len(v) <= 12) / len(vs)) if vs else float("nan")
        ce, cl = Counter(early), Counter(late)
        se = (sum(1 for v, c in ce.items() if c == 1) / len(ce)) if ce else float("nan")
        sl = (sum(1 for v, c in cl.items() if c == 1) / len(cl)) if cl else float("nan")
        conf[key] = {"median_round": med, "n_early": len(early), "n_late": len(late),
                     "short_frac_early": short(early), "short_frac_late": short(late),
                     "singleton_frac_early": se, "singleton_frac_late": sl}
        print(f"  {key:<10} short(<=12 chars): early {short(early):.3f} -> late "
              f"{short(late):.3f}   singletons: early {se:.3f} -> late {sl:.3f}   "
              f"(n {len(early)}/{len(late)})")

    print(f"\n  MULTIPLICITY: {tested} keys x 8 sweep points x 3 seeds, plus 2 synthetic "
          f"controls. All reported; {surviving} landed strictly between floor and ceiling.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "vocabulary.json").write_text(json.dumps({
        "world": ("UNVERIFIED" if not controls_fired
                  else "+".join(f"{k}={v['world']}" for k, v in rows.items())),
        "n_rounds_with_artifacts": len(C),
        "floor_beta_synthetic_enum": b_enum, "floor_seed_spread": s_enum,
        "ceiling_beta_synthetic_free": b_free, "ceiling_seed_spread": s_free,
        "separation": b_free - b_enum, "placebo_beta": b_plc,
        "controls_fired": controls_fired, "keys": rows, "confound_recency": conf,
        "beta_is": ("an OLS summary of a log-log curve, reported WITH the curve; a saturating "
                    "and a linear curve can share a slope over a narrow range"),
        "known_bias": ("lists/dicts are serialised, so a structural difference counts as a "
                       "different value -- this biases beta UPWARD, i.e. AGAINST the enum "
                       "hypothesis, which is the conservative direction for HB8"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'vocabulary.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
