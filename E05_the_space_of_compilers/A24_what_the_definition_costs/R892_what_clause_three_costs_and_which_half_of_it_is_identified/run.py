#!/usr/bin/env python3
"""
R892 · what does clause ③ COST — and which half of that cost is even identified?

⛔ WHY. R888/R891 established that clause ③ excludes 16 of clause ②'s 28 arms and contributes
**nothing** to the admitted set's concentration (+0.1079 on PR, i.e. it mildly diversifies). So the
clause's whole justification is on principle: *do not consume the answer key.* **Its PRICE has never
been measured.** The excluded arms' median margin is +0.0565 to +0.0804 against the kept arms'
+0.0219 — a gap several times R860's MDE of 0.0103, sitting unpriced under a headline.

⭐ **AND THE RELEASE CONTAINS A BUILT-IN DOSE AXIS THAT MAKES HALF OF IT IDENTIFIED.**
`select_core.py:203-206` appends `_fit{parity}` to the tag only when `fit_parity >= 0`, and
`compare.py:35` states the design in its own words: *"oracle fitted on the OTHER parity has never
seen the annotator it is scored against. Without this the oracle arm is leaky and its value is an
inflated upper bound."* So the 16 split **8 / 8**:
  · **LEAKY** (no `_fit`): fitted on ALL annotators, scored against annotators it saw.
  · **HELD-OUT** (`_fit1`): fitted on parity 1, scored on parity 0 — labels consumed, but honestly.

⭐⭐ **THIS SPLITS THE COST INTO ONE IDENTIFIED CONTRAST AND ONE THAT IS NOT, AND CONFLATING THEM IS
THE ERROR THIS ROUND EXISTS TO AVOID.**
  · `leaky − held-out` — ⛔⛔ **I CLAIMED "same rules, same families, same k" AND THAT WAS FALSE.
    The permutation placebo caught it.** The leaky stratum is entirely `k=4`; the held-out stratum
    spans `k = 2, 4, 8, 12`. **So `k` varies between strata alongside `fit_parity`, and the 8-vs-8
    contrast is confounded.** A stratum-label shuffle put the observed +0.0190 INSIDE its null
    [-0.0289, +0.0250] — because between-arm variance across rules and k swamps the effect. The
    identified comparison is only the **PAIRED, WITHIN-(rule, k=4)** one, which is what this round
    now computes. ⚠ And note what nearly happened: a prompt-bootstrap CI of [+0.0155, +0.0224]
    looked decisive while holding the very labelling in question FIXED. **A tight interval around
    a confounded contrast is the most confident way to be wrong.**
  · `held-out − label-free` — **NOT IDENTIFIED.** The label-consuming rules are exactly
    `oracle_k`, `indep_k`, `greedy_k`, and **every one of them consumes labels by construction**;
    the release contains no label-free version of any of them. So rule and label-access change
    TOGETHER, and the gap is an upper bound on what labels buy, confounded with whatever
    greedy/independent search buys over top-weight selection. **Reported as a bound, never a point.**

⚠ This is §1's rule that identification comes before power. The second contrast is well-powered and
unidentified, which is exactly the shape that produces a confident wrong number.

ESTIMAND        (a) mean margin(LEAKY) − mean margin(HELD-OUT)  [identified: pure leakage]
                (b) mean margin(HELD-OUT) − mean margin(LABEL-FREE)  [partially identified: an
                    upper bound on the value of consuming labels, confounded with search rule]
IDENTIFICATION  (a) exact — the arms differ only in `fit_parity`, a flag in the generator.
                (b) PARTIAL — bounds only. Stated in the output, not buried here.
SCOPE           population: the 28 clause-②-admitted arms, split 12 / 8 / 8 by the generator's own
                            rule set and tag convention — DERIVED, never globbed
                instrument: per-prompt A2 margin vs comparator genericpool16
                baseline:   zero gap between strata
                regime:     home release, judge J, 968 prompts
WORLDS          A · leaky > held-out > label-free, with (a) resolved -> the leak is real AND clause
                    ③ additionally excludes honest held-out learning, so its price is more than
                    cheating-prevention and the definition has never said so
                B · leaky ≈ held-out -> the "leak" does not leak, and clause ③'s stated premise is
                    wrong about the objects it excludes
                C · held-out ≈ label-free -> consuming labels buys nothing here and clause ③ is
                    free, which would make it the cheapest clause in the definition
KILL            CONDITIONAL, and the positive control is the round's own premise:
                  ⭐ ① POSITIVE: `leaky − held-out` must be > 0 with a bootstrap CI excluding zero.
                     **If leakage is not detectable, this instrument cannot see the thing the whole
                     round is about**, and (b) is unreadable regardless of what it returns.
                  ⭐ ② PLACEBO: **a LABEL-SHUFFLE permutation.** Reassign the 28 arms to strata of
                     the same sizes at random and recompute contrast (a); the observed must sit
                     outside that null.
                     ⛔⛔ POST-RUN CORRECTION — MY FIRST PLACEBO COULD NOT FAIL, WHICH IS THE §4
                     `check that cannot fail` MODE IN THE CONTROL SLOT. It compared the `_kA`/`_kB`
                     replica pairs and returned `+0.0000 [+0.0000, +0.0000]` — ZERO WIDTH — because
                     R890 had already measured those replicas at **r = 1.000000**. Their difference
                     is forced by the algebra: **a DERIVATION wearing a control's name**, and it
                     offered no assurance whatever. The tell was in its own output, and it is the
                     one this session keeps re-learning: *a control that returns a zero-width
                     interval has not measured anything.* Replaced by the permutation above, which
                     can land either side.
                  ⭐ ③ the three strata must partition the 28 exactly: 12 + 8 + 8 = 28.
                  ④ the LEAKY/HELD-OUT split must be READ from the tag convention in the generator,
                     not assigned by hand.
MULTIPLICITY    2 contrasts, 1 placebo; all reported with CIs, survivors and non-survivors alike.
ARTIFACT        results/clause3_price.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · cross-model. ⚠ AND, newly named: **`held-out − label-free` is NOT
                identified on this release** and would require a label-free arm using one of
                `oracle_k`/`indep_k`/`greedy_k` — an object the release does not contain and which
                the generator cannot produce, since that branch opens the label file
                unconditionally.
"""
import json, pathlib, re, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

BLIND, CORE = "genericpool16", "coval_core"
NBOOT, SEED = 4000, 892
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
GEN = ROOT / "corebench" / "select_core.py"


def art(g, n):
    p = next(A24.glob(f"{g}/results/{n}"), None)
    return json.loads(p.read_text()) if p else None


def fit_tag_convention():
    """READ the tag rule: `_fit{parity}` is appended only when fit_parity >= 0."""
    m = re.search(r'f"_fit\{a\.fit_parity\}"\s*if a\.rule in \(([^)]*)\)\s*\n\s*and '
                  r'a\.fit_parity >= 0', GEN.read_text())
    return None if not m else "_fit"


def main() -> int:
    r889, r881 = art("R889_*", "two_admitted_sets.json"), art("R881_*", "boundary_distance.json")
    marker = fit_tag_convention()
    if r889 is None or r881 is None or marker is None:
        print("  UNRUNNABLE: an artifact or the tag convention could not be read. Exit 2.")
        return 2
    print(f"  ④ tag convention READ from {GEN.name}: held-out arms carry {marker!r}")

    keep = set(r889["r888_corrected"]["surviving"])
    adm = [x["arm"] for x in r881["arms"] if x["admitted"]]
    free = [a for a in adm if a in keep]
    excl = [a for a in adm if a not in keep]
    ho = [a for a in excl if marker in a]
    lk = [a for a in excl if marker not in a]
    c3 = len(free) + len(ho) + len(lk) == len(adm)
    print(f"  ③ partition {len(free)} label-free + {len(ho)} held-out + {len(lk)} leaky = "
          f"{len(adm)}: {c3}  {'PASS' if c3 else 'FAIL'}")
    if not c3:
        print("  UNVERIFIED: the strata do not partition the admitted set. Exit 2, never 0.")
        return 2

    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / f"sat_{BLIND}.npz")
    A = load_sat(ROOT / "corebench" / "results" / f"sat_{CORE}.npz")
    pids = sorted(set(S) & set(A) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]

    def vec(nm):
        f = ROOT / "corebench" / "results" / f"sat_{nm}.npz"
        if not f.exists():
            return None
        try:
            Sa = load_sat(f)
        except Exception:
            return None
        v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                      for k, p in enumerate(pids)])
        return v if np.isfinite(v).sum() >= 200 else None

    base = vec(BLIND)
    V = {}
    for a in adm:
        v = vec(a)
        if v is not None:
            V[a] = np.nan_to_num(v, nan=np.nanmean(v)) - np.nan_to_num(base, nan=np.nanmean(base))
    free = [a for a in free if a in V]; ho = [a for a in ho if a in V]; lk = [a for a in lk if a in V]
    n = len(pids)
    print(f"  prompts {n} · strata with vectors: free {len(free)} · held-out {len(ho)} · "
          f"leaky {len(lk)}")

    rng = np.random.default_rng(SEED)
    idxb = [rng.integers(0, n, n) for _ in range(NBOOT)]

    def stratum(g):
        return np.mean([V[a] for a in g], axis=0)          # per-prompt mean margin of the stratum

    def boot(gap_fn):
        pt = gap_fn(np.arange(n))
        d = np.array([gap_fn(b) for b in idxb])
        return pt, float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))

    m_free, m_ho, m_lk = stratum(free), stratum(ho), stratum(lk)
    # PAIRED within (rule, k): the ONLY place fit_parity varies with everything else held fixed
    import collections
    def cell(a):
        m = re.match(r"(oracle|indep|greedy)_k(\d+)", a)
        return (m.group(1), m.group(2)) if m else None
    lk_by, ho_by = collections.defaultdict(list), collections.defaultdict(list)
    for a in lk:
        if cell(a): lk_by[cell(a)].append(a)
    for a in ho:
        if cell(a): ho_by[cell(a)].append(a)
    pairs_cells = sorted(set(lk_by) & set(ho_by))
    print(f"  ⚠ MATCHED CELLS (rule,k) with BOTH leaky and held-out present: {pairs_cells}")
    print(f"    held-out-only cells (no leaky twin, EXCLUDED from the identified contrast): "
          f"{sorted(set(ho_by) - set(lk_by))}")
    if not pairs_cells:
        print("  UNRUNNABLE: no matched cell. Exit 2, never 0.")
        return 2
    def paired_gap(b):
        return float(np.mean([np.mean([V[x][b] for x in lk_by[c]], axis=0).mean()
                              - np.mean([V[y][b] for y in ho_by[c]], axis=0).mean()
                              for c in pairs_cells]))
    a_pt, a_lo, a_hi = boot(paired_gap)
    b_pt, b_lo, b_hi = boot(lambda b: float(m_ho[b].mean() - m_free[b].mean()))

    # ---- CONTROLS -----------------------------------------------------------------------------
    c1 = a_lo > 0
    # PLACEBO: shuffle the stratum assignment, keep the sizes. CAN land either side of 0.
    pool = free + ho + lk
    rngp = np.random.default_rng(SEED + 1)
    perm = []
    for _ in range(1000):
        q = list(pool); rngp.shuffle(q)
        f2, h2, l2 = q[:len(free)], q[len(free):len(free) + len(ho)], q[len(free) + len(ho):]
        perm.append(float(np.mean([V[a] for a in l2], axis=0).mean()
                          - np.mean([V[a] for a in h2], axis=0).mean()))
    perm = np.array(perm)
    r_pt = float(np.median(perm))
    r_lo, r_hi = float(np.percentile(perm, 2.5)), float(np.percentile(perm, 97.5))
    # the null must be PAIRED too: flip leaky/held-out WITHIN each matched cell
    permp = []
    for _ in range(1000):
        g = []
        for c in pairs_cells:
            L = np.mean([V[x] for x in lk_by[c]], axis=0)
            Hh = np.mean([V[y] for y in ho_by[c]], axis=0)
            g.append(float((L - Hh).mean()) * (1 if rngp.random() < 0.5 else -1))
        permp.append(float(np.mean(g)))
    permp = np.array(permp)
    r_pt = float(np.median(permp))
    r_lo, r_hi = float(np.percentile(permp, 2.5)), float(np.percentile(permp, 97.5))
    c2 = bool(r_lo < r_hi) and (a_pt > r_hi or a_pt < r_lo)
    print(f"\n  ① POSITIVE leaky − held-out = {a_pt:+.4f} [{a_lo:+.4f}, {a_hi:+.4f}], CI excludes "
          f"0: {c1}  {'PASS' if c1 else 'FAIL'}")
    print(f"     if leakage is undetectable, this instrument cannot see what the round is about")
    print(f"  ② PLACEBO  PAIRED sign-flip within each matched (rule,k) cell, 1000 draws: "
          f"median {r_pt:+.4f} [{r_lo:+.4f}, {r_hi:+.4f}]")
    print(f"     ⚠ n = {len(pairs_cells)} cells, so this null is coarse BY CONSTRUCTION — "
          f"2^{len(pairs_cells)} = {2**len(pairs_cells)} distinct sign patterns, floor "
          f"{1/2**len(pairs_cells):.4f}")
    print(f"     observed {a_pt:+.4f} lies OUTSIDE that null: {c2}  {'PASS' if c2 else 'FAIL'}")
    print(f"     ⛔ replaces a first placebo that returned +0.0000 [0,0] — zero width, forced by")
    print(f"        the algebra, because the _kA/_kB replicas are identical at r = 1.000000")
    if not (c1 and c2):
        floor = 1 / 2 ** len(pairs_cells)
        print(f"\n  ⛔⛔ UNVERIFIED — AND THE REASON IS THE RELEASE, NOT THE EFFECT.")
        print(f"     The paired null has {2**len(pairs_cells)} distinct sign patterns over "
              f"{len(pairs_cells)} matched cells,")
        print(f"     so its resolution FLOOR is {floor:.4f}. **It cannot reject at 0.05 no matter")
        print(f"     what the data say.** A FAIL here is silence, not an acquittal — UNVERIFIED,")
        print(f"     never OVERTURNED.")
        print(f"\n  ⭐ WHAT IS NEVERTHELESS MEASURED, and it is the round's finding:")
        print(f"     unmatched 8-vs-8 leaky − held-out : +0.0190")
        print(f"     PAIRED within (rule, k=4)          : {a_pt:+.4f}")
        print(f"     **the k-confound accounted for ~{1 - a_pt/0.0190:.0%} of the apparent effect.**")
        print(f"     The leaky stratum is entirely k=4; the held-out stratum spans k=2,4,8,12.")
        print(f"     My 'IDENTIFIED' label on the 8-vs-8 contrast was FALSE and the permutation")
        print(f"     placebo is what caught it — after a prompt-bootstrap CI of [+0.0155,+0.0224]")
        print(f"     had already made it look decisive. A tight interval around a confounded")
        print(f"     contrast is the most confident way to be wrong.")
        print(f"\n  ⚠ SO CLAUSE ③'s PRICE IS UNRESOLVED IN BOTH HALVES on this release:")
        print(f"     (a) leakage        — matched at only {len(pairs_cells)} cells; null floor "
              f"{floor:.4f}")
        print(f"     (b) held-out−free  — never identified; no label-free twin of the three rules")
        json.dump({"verdict": "UNVERIFIED", "reason": "the paired null's resolution floor is "
                   f"{floor}, so it cannot reject at 0.05 regardless of the data",
                   "controls": {"positive_prompt_bootstrap": bool(c1),
                                "placebo_paired_signflip": bool(c2)},
                   "matched_cells": [list(c) for c in pairs_cells],
                   "heldout_only_cells": [list(c) for c in sorted(set(ho_by) - set(lk_by))],
                   "gap_unmatched_8v8": 0.0190,
                   "gap_paired_within_rule_k4": a_pt,
                   "gap_paired_ci95_prompt_bootstrap": [a_lo, a_hi],
                   "share_of_effect_from_k_confound": 1 - a_pt / 0.0190,
                   "paired_null": {"median": r_pt, "ci95": [r_lo, r_hi],
                                   "n_sign_patterns": 2 ** len(pairs_cells), "floor": floor},
                   "retracted_in_this_round": "the docstring's claim that leaky-vs-held-out is "
                                              "IDENTIFIED because the arms share rule, family and "
                                              "k. They do not share k: leaky is all k=4, held-out "
                                              "spans k=2,4,8,12.",
                   "withdrawn_placebo": "the _kA/_kB replica placebo returned +0.0000 [0,0] — zero "
                                        "width, forced by the algebra (r = 1.000000). A derivation "
                                        "wearing a control's name.",
                   "what_would_resolve_it": "leaky arms at k=2, 8 and 12 — the generator can "
                                            "produce them (drop --fit-parity), so this is a "
                                            "MISSING RUN, not a structural impossibility",
                   "stratum_mean_margin": {"label_free": float(m_free.mean()),
                                           "held_out": float(m_ho.mean()),
                                           "leaky": float(m_lk.mean())}},
                  open(OUT / "clause3_price.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐ STRATUM MEANS (per-prompt margin vs {BLIND}):")
    for nm, m, g in (("label-free", m_free, free), ("held-out", m_ho, ho), ("leaky", m_lk, lk)):
        print(f"     {nm:<12} n={len(g):<3} mean margin {m.mean():+.4f}")
    print(f"\n  ⭐⭐ (a) leaky − held-out  = {a_pt:+.4f} [{a_lo:+.4f}, {a_hi:+.4f}]   IDENTIFIED")
    print(f"      same rules, same families, same k — only `fit_parity` changes. This is leakage.")
    print(f"  ⭐⭐ (b) held-out − free   = {b_pt:+.4f} [{b_lo:+.4f}, {b_hi:+.4f}]   NOT IDENTIFIED")
    print(f"      ⚠ AN UPPER BOUND, NOT A VALUE. `oracle_k`/`indep_k`/`greedy_k` consume labels")
    print(f"      BY CONSTRUCTION and have no label-free twin on this release, so rule and")
    print(f"      label-access change together. The gap bounds `what labels buy` PLUS `what")
    print(f"      greedy/independent search buys over top-weight selection`, and nothing here")
    print(f"      separates them.")

    world = ("B" if not c1 else
             "C" if (b_lo <= 0 <= b_hi) else "A")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": "leaky > held-out > label-free — the leak is real AND clause ③ additionally excludes "
             "HONEST held-out learning. Its price is more than cheating-prevention, and the "
             "definition has never said so",
        "B": "the leak does not leak — clause ③'s premise is wrong about the objects it excludes",
        "C": "held-out ≈ label-free — consuming labels buys nothing measurable here, and clause ③ "
             "is the cheapest clause in the definition"}[world])
    if world == "A":
        print(f"      ⚠ AND THE PRICE IS A BOUND: clause ③ costs AT MOST {b_pt:+.4f} in margin,")
        print(f"        because that gap is confounded with the search rule. The honest statement")
        print(f"        is an inequality, not a number.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "nboot": NBOOT, "n_prompts": n,
               "strata": {"label_free": free, "held_out": ho, "leaky": lk},
               "stratum_mean_margin": {"label_free": float(m_free.mean()),
                                       "held_out": float(m_ho.mean()),
                                       "leaky": float(m_lk.mean())},
               "contrast_a_leaky_minus_heldout": {"point": a_pt, "ci95": [a_lo, a_hi],
                                                  "identified": True,
                                                  "why": "only fit_parity changes"},
               "contrast_b_heldout_minus_free": {"point": b_pt, "ci95": [b_lo, b_hi],
                                                 "identified": False,
                                                 "why": "rule and label-access change together; "
                                                        "no label-free twin of oracle_k/indep_k/"
                                                        "greedy_k exists on this release",
                                                 "read_as": "UPPER BOUND, not a value"},
               "placebo_label_shuffle": {"median": r_pt, "ci95": [r_lo, r_hi], "n_draws": 1000,
                                         "observed_outside_null": bool(c2)},
               "withdrawn_placebo": "the _kA/_kB replica-pair placebo returned +0.0000 [0,0] — "
                                    "zero width, forced by the algebra (R890 measured those "
                                    "replicas at r = 1.000000). A derivation wearing a control's "
                                    "name; it offered no assurance and is withdrawn.",
               "controls": {"positive_leak_detectable": bool(c1), "placebo_replicas_null": bool(c2),
                            "partition_sums": c3},
               "newly_named_impossibility": "held-out minus label-free is NOT identified here; it "
                                            "would require a label-free arm using one of the three "
                                            "label-consuming rules, which the generator cannot "
                                            "produce because that branch opens the label file "
                                            "unconditionally",
               "unit_note": "margins are A2 units vs genericpool16; counts are ARMS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "clause3_price.json", "w"), indent=2)
    print(f"\n  artifact: results/clause3_price.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
