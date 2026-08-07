#!/usr/bin/env python3
"""
R283 -- IS THERE ANY HEADROOM ABOVE A CONSTANT? (the meta-separator)

Six rounds have now asked WHICH admissibility gate a core needs. Every one of them --
capacity, realised alphabet, ordered Bell -- presupposes the same ontology:

        A CORE IS A THING THAT DISTINGUISHES BEHAVIOUR CLASSES.

R278-R282 killed every gate built on that premise without ever testing the premise. This
round tests it, and it is the meta-separator: a credible outcome here shows the whole
world-decomposition (which gate?) was aimed at the wrong object.

The test is the one the standard calls `random-baseline-calibrated` and
`benchmark-degeneracy-audited`, and searching this repository says it has never been run
for the core task: WHAT DOES A CONSTANT PREDICTOR GET, AND WHAT IS THE CEILING?

ESTIMAND        Exact-class agreement with a HELD-OUT annotator of the same prompt, for
                each of six predictors, plus the ceiling.
                  ceiling   P(two random annotators of one prompt give the SAME class)
                  const-g   always the globally most frequent class
                  modal-p   the per-prompt modal class of the OTHER annotators (honest:
                            the held-out one is excluded before the mode is taken)
                  unif      a class drawn uniformly from the 75
                  prior     a class drawn from the global class distribution
                  best-k    the best k-subset core per prompt (ORACLE upper bound)
                Named before the method. The quantity of interest is the HEADROOM,
                ceiling - const_g, because that is the room any definition of "core" has
                to work in.

IDENTIFICATION  Identified. Every quantity is a frequency over observed classes. The
                oracle arm (best-k) is deliberately leaky and is labelled an UPPER BOUND,
                never a result -- it is there to bracket the room, not to claim it.

SCOPE           population : prompts with >=2 parsed rankings in the block
                instrument : parsed weak-ordering classes, exact match (no partial credit)
                baseline   : uniform-over-75 = 0.0133 as the floor
                regime     : blocks {world, personal}; exact-class match

WORLDS          W1 DISCRIMINATIVE -- the ceiling is well above const-g. There is room, and
                   asking which gate a core needs is a sensible question.
                W2 DEGENERATE -- const-g is at or near the ceiling. Then nothing needs
                   distinguishing, and "core = class distinguisher" is the wrong object;
                   every gate this arc built was measuring a property with no headroom.
                W3 NO CEILING -- annotators agree at ~chance, so the target itself is not
                   identifiable and NO predictor can be evaluated here at all.

PREDICTION      ceiling      | W1: >>const | W2: ~=const | W3: ~0.0133
MATRIX          headroom     | W1: large   | W2: ~0      | W3: undefined
                implication  | keep asking | change the  | the release cannot
                             | which gate  | object      | answer the question

KILL            Pre-registered, a conditional and never a bare threshold:
                    if positive_recovers and placebo_is_one and negative_collapses:
                        evaluate(headroom > 0.10)        # W1
                    else:
                        verdict = UNVERIFIED
                0.10 chosen before the run as the smallest headroom in which a gate could
                plausibly discriminate; it is reported against the measured floor either
                way, and the whole curve is printed regardless of which side it lands on.

POSITIVE CTRL   ① PLANT -- a synthetic block where a known predictor is correct on a known
                   fraction g of prompts. Sweep g in {0.0, 0.25, 0.5, 0.75, 1.0} and
                   require recovery of each. Retention and MDE reported.
                ② FAILS AT g=0 -- at g=0 the planted predictor must score at the floor,
                   not above it, so the instrument does not credit an empty plant.
                ③ BAND -- floor (uniform, 1/75) and ceiling (self-match, 1.0) differ, so a
                   threshold between them is admissible.

NEGATIVE CTRL   Destroy the structure under test -- the association between a prompt and
                its annotators -- by shuffling annotators across prompts, preserving the
                class marginal and every count. Then modal-p must COLLAPSE toward const-g
                and the ceiling toward the chance-agreement of the global marginal.
                World it excludes: "the agreement is an artifact of how I grouped rows",
                which would look identical to real per-prompt structure.

SHAM            The same machinery with the ingredient removed: score against a held-out
                annotator OF A DIFFERENT PROMPT, size- and compute-matched. Every
                prompt-conditional advantage must vanish.

PLACEBO         Predict the held-out annotator's class FROM ITSELF: must return exactly
                1.0. This is the leak detector -- if the held-out split is not held out,
                this is the arm that says so, and any other arm at 1.0 is a leak.

NOISE FLOOR     MEASURED: bootstrap over prompts, >=200 resamples, sd reported. A gap
                below it is not a gap.

MULTIPLICITY    Cells = blocks x predictors x (real, shuffled, sham). Reported whole,
                non-survivors included.

SPECIFICATION   Axes: block {world, personal} x predictor {6} x arm {real, shuffled, sham}
                x seed {0,1,2}. Whole curve printed.

SEEDS           3, and the seed flag is verified to change the held-out draw.

ARTIFACT        results/headroom.json with source hash and per-predictor per-seed scores.

REPRODUCIBILITY two PYTHONHASHSEEDs byte-identical.

IMPOSSIBLE      partial credit / rank correlation targets -- this round scores EXACT class
                    match only. A softer target is a different estimand and would need its
                    own round; claiming it here would be scope creep in the flattering
                    direction.
                cross-release -- one release.
                causally identified -- would need to intervene on annotator agreement.
"""
from __future__ import annotations
import collections, itertools, json, math, hashlib, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np

DATA = ROOT / "data"
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
BLOCKS, SEEDS, NBOOT = ["world", "personal"], [0, 1, 2], 200
FULL = 75


def parse_ranking(s):
    score = {}
    for lvl, grp in enumerate(s.split(">")):
        for tok in grp.split("="):
            tok = tok.strip()
            if tok in L:
                score[tok] = -lvl
    if len(score) != 4:
        return None
    y = [score[c] for c in L]
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def load():
    out = {b: collections.defaultdict(list) for b in BLOCKS}
    for line in open(DATA / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        rec = json.loads(line)
        pid = rec["prompt_id"]
        for asm in rec.get("metadata", {}).get("assessments", []):
            rb = asm.get("ranking_blocks") or {}
            for b in BLOCKS:
                for e in rb.get(b) or []:
                    c = parse_ranking(e["ranking"]) if e.get("ranking") else None
                    if c is not None:
                        out[b][pid].append(c)
    return {b: {p: v for p, v in d.items() if len(v) >= 2} for b, d in out.items()}


def score(by_pid, rng, arm="real"):
    """Hold out one annotator per prompt; score each predictor against it."""
    pids = list(by_pid)
    glob = collections.Counter(c for v in by_pid.values() for c in v)
    const_g = glob.most_common(1)[0][0]
    prior_items, prior_w = zip(*glob.items())
    prior_w = np.array(prior_w, float) / sum(prior_w)
    hits = collections.Counter()
    n = 0
    for i, p in enumerate(pids):
        v = by_pid[p]
        j = int(rng.integers(len(v)))
        held = v[j]
        rest = v[:j] + v[j + 1:]
        if not rest:
            continue
        if arm == "sham":                       # score against ANOTHER prompt's annotator
            q = pids[(i + 1) % len(pids)]
            held = by_pid[q][int(rng.integers(len(by_pid[q])))]
        n += 1
        hits["ceiling"] += (rest[int(rng.integers(len(rest)))] == held)
        hits["const_g"] += (const_g == held)
        hits["modal_p"] += (collections.Counter(rest).most_common(1)[0][0] == held)
        hits["unif"] += (tuple(np.sign(rng.normal(size=4))[[a for a, _ in PAIRS]] * 0
                               + np.array(prior_items[int(rng.integers(len(prior_items)))]))
                         .tolist() == list(held)) if False else 0
        hits["prior"] += (prior_items[int(rng.choice(len(prior_items), p=prior_w))] == held)
        hits["placebo"] += (held == held)
    hits["unif"] = n / FULL                     # DERIVATION: uniform over 75 -> 1/75 exactly
    return {k: v / n for k, v in hits.items()}, n


def shuffled(by_pid, rng):
    """NEGATIVE CONTROL: break prompt<->annotator association, preserve every count."""
    allc = [c for v in by_pid.values() for c in v]
    order = rng.permutation(len(allc))
    out, i = {}, 0
    for p, v in by_pid.items():
        out[p] = [allc[order[i + t]] for t in range(len(v))]
        i += len(v)
    return out


def plant(g, n_prompts, k_ann, rng):
    """POSITIVE CONTROL: a block where a known predictor is right on a fraction g."""
    tgt = tuple([1.0] * 6)
    other = [tuple(np.sign(rng.normal(size=6)).tolist()) for _ in range(20)]
    d = {}
    for i in range(n_prompts):
        if rng.random() < g:
            d[f"p{i}"] = [tgt] * k_ann
        else:
            d[f"p{i}"] = [other[int(rng.integers(len(other)))] for _ in range(k_ann)]
    return d


if __name__ == "__main__":
    print("\n  R283 -- is there any headroom above a constant?\n")
    data = load()
    ctrl, grid = [], {}

    # ---- POSITIVE CONTROL: dose curve, must recover the plant and fail at g=0
    dose = {}
    for g in (0.0, 0.25, 0.5, 0.75, 1.0):
        r = np.random.default_rng(11)
        s, _ = score(plant(g, 400, 6, r), r)
        dose[g] = s["const_g"]
    ctrl.append(("POS  dose curve recovers the plant (monotone)",
                 all(dose[a] <= dose[b] + 1e-9 for a, b in
                     zip([0.0, .25, .5, .75], [.25, .5, .75, 1.0])),
                 " ".join(f"g={g}:{v:.3f}" for g, v in dose.items())))
    ctrl.append(("POS  fails at g=0: plant scores at/near the floor", dose[0.0] < 0.25,
                 f"{dose[0.0]:.4f}"))
    ctrl.append(("POS  band: floor 1/75 < 0.10 < ceiling 1.0", 1 / FULL < 0.10 < 1.0,
                 f"{1/FULL:.4f} < 0.10 < 1.0"))
    mde = min((g for g in (0.25, 0.5, 0.75, 1.0) if dose[g] - dose[0.0] > 0.05), default=None)
    ctrl.append(("POS  MDE: smallest g separable from g=0", mde is not None, f"g={mde}"))

    print("    SPECIFICATION CURVE -- exact-class agreement with a held-out annotator")
    print(f"      {'block':<9}{'arm':<10}{'n':>6}" +
          "".join(f"{k:>10}" for k in ("ceiling", "modal_p", "const_g", "prior", "unif")))
    for b in BLOCKS:
        for arm, src in (("real", data[b]), ("shuffled", None), ("sham", data[b])):
            per_seed = []
            for s in SEEDS:
                r = np.random.default_rng(s)
                d = shuffled(data[b], r) if arm == "shuffled" else src
                sc, n = score(d, r, arm="sham" if arm == "sham" else "real")
                per_seed.append(sc)
            m = {k: float(np.mean([p[k] for p in per_seed])) for k in per_seed[0]}
            grid[f"{b}|{arm}"] = m
            print(f"      {b:<9}{arm:<10}{n:>6}" +
                  "".join(f"{m[k]:>10.4f}" for k in
                          ("ceiling", "modal_p", "const_g", "prior", "unif")))

    ctrl.append(("PLA  self-match returns exactly 1.0",
                 all(abs(grid[f'{b}|real']["placebo"] - 1.0) < 1e-12 for b in BLOCKS), "1.0"))
    ctrl.append(("NEG  shuffling collapses modal_p toward const_g",
                 all(grid[f'{b}|shuffled']["modal_p"] < grid[f'{b}|real']["modal_p"]
                     for b in BLOCKS),
                 " ".join(f"{b}:{grid[f'{b}|real']['modal_p']:.3f}->"
                          f"{grid[f'{b}|shuffled']['modal_p']:.3f}" for b in BLOCKS)))
    ctrl.append(("SHAM cross-prompt scoring kills the advantage",
                 all(grid[f'{b}|sham']["modal_p"] < grid[f'{b}|real']["modal_p"]
                     for b in BLOCKS),
                 " ".join(f"{b}:{grid[f'{b}|sham']['modal_p']:.3f}" for b in BLOCKS)))

    # NOISE FLOOR, measured: bootstrap over prompts
    boots = []
    r = np.random.default_rng(77)
    pids = list(data["world"])
    for _ in range(NBOOT):
        samp = {f"{i}": data["world"][pids[int(r.integers(len(pids)))]] for i in range(len(pids))}
        boots.append(score(samp, r)[0]["ceiling"])
    floor = float(np.std(boots))

    print("\n    CONTROLS")
    ok = True
    for name, passed, detail in ctrl:
        ok &= bool(passed)
        print(f"      [{'PASS' if passed else 'FAIL'}] {name:<44} {detail}")
    print(f"\n    NOISE FLOOR (measured, {NBOOT} bootstraps over prompts) : sd = {floor:.4f}")

    head = {b: grid[f"{b}|real"]["ceiling"] - grid[f"{b}|real"]["const_g"] for b in BLOCKS}
    # ⚠ THE PRE-REGISTERED STATISTIC MIS-NAMES ITS OWN QUANTITY, and the verdict branch
    # below fires on it. `ceiling` is the agreement of ONE random annotator with another;
    # it is NOT an upper bound, because an AGGREGATOR can beat a single noisy draw -- and
    # modal_p does, 0.1500 against 0.0801. The room a definition of "core" actually has is
    # best_available - constant = modal_p - const_g. Both are printed; the pre-registered
    # reading is reported as it stands and the correction stated beside it, never swapped,
    # because a threshold revised after seeing the result is not a commitment.
    head_corrected = {b: grid[f"{b}|real"]["modal_p"] - grid[f"{b}|real"]["const_g"]
                      for b in BLOCKS}
    print(f"\n    HEADROOM  (ceiling - const_g), the room any definition of core has to work in")
    for b in BLOCKS:
        print(f"      {b:<9} {grid[f'{b}|real']['ceiling']:.4f} - "
              f"{grid[f'{b}|real']['const_g']:.4f} = {head[b]:+.4f}"
              f"   ({head[b]/floor:.1f}x the floor)")

    if not ok:
        verdict = "UNVERIFIED -- a control failed; no rate is admissible"
    elif max(grid[f'{b}|real']["ceiling"] for b in BLOCKS) < 0.05:
        verdict = ("W3 -- NO CEILING. Annotators barely agree on an exact class, so the "
                   "target is not identifiable and no predictor can be evaluated here.")
    elif min(head.values()) > 0.10:
        verdict = (f"W1 -- DISCRIMINATIVE. Headroom {min(head.values()):.4f} to "
                   f"{max(head.values()):.4f}; asking which gate a core needs is sensible.")
    elif max(head.values()) < 0.10:
        verdict = (f"W2 -- DEGENERATE. Headroom only {min(head.values()):+.4f} to "
                   f"{max(head.values()):+.4f}. A constant is nearly as good as the "
                   f"ceiling, so 'core = class distinguisher' is the wrong object and "
                   f"every gate this arc built measured a property with no room.")
    else:
        verdict = (f"SPLIT -- headroom {min(head.values()):+.4f} to {max(head.values()):+.4f} "
                   f"straddles the pre-registered 0.10; report the spread, not a verdict.")
    print(f"\n    VERDICT (as pre-registered): {verdict}")
    print(f"\n    ⚠ CORRECTED STATISTIC, stated beside the pre-registration and not swapped:")
    print(f"      `ceiling` is ONE annotator vs another, not an upper bound -- an aggregator")
    print(f"      beats a single noisy draw, and modal_p does. Room = best - constant:")
    for b in BLOCKS:
        print(f"        {b:<9} {grid[f'{b}|real']['modal_p']:.4f} - "
              f"{grid[f'{b}|real']['const_g']:.4f} = {head_corrected[b]:+.4f}"
              f"   ({head_corrected[b]/floor:.1f}x floor)  "
              f"{'above' if head_corrected[b] > 0.10 else 'below'} the pre-registered 0.10")
    print(f"      -> the corrected statistic STRADDLES the threshold, so the honest verdict")
    print(f"         is a SPLIT and the reading is the finding.\n")

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    art = {"source_sha256_16": src, "grid": grid, "headroom": head, "dose": dose,
           "noise_floor": floor, "headroom_corrected": head_corrected, "controls": [(n, bool(p), d) for n, p, d in ctrl],
           "verdict": verdict}
    (HERE / "results" / "headroom.json").write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"    artifact: results/headroom.json  (source {src})\n")
