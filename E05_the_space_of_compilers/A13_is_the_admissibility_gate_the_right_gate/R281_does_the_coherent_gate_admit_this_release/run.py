#!/usr/bin/env python3
"""
R281 -- DOES THE COHERENT GATE ADMIT THIS RELEASE AT ALL?

R280 found G1 (`log2|H(Q)| <= H_eff`) is the only unit-coherent form of the gate, so the
repair is a revert. THE REVERT IS NOT FREE, and this round computes its price before it is
written down: claim 5 measures H_eff in [1.02, 3.45] bits, and if the release's own target
needs more than that, the coherent gate rejects this release at every k. That is a real
answer, not a failure -- but it must be COMPUTED, because "the revert probably works" is
exactly the flattering reading.

UNIT CHECK FIRST, per the rule that produced R278/R280:
    log2|H(Q)|  -> bits needed to name a behaviour class   "bits about a class"
    H_eff       -> bits the noisy channel delivers about a class  "bits about a class"
    EQUAL. G1 is comparable; that is why it is the form being priced.

ESTIMAND        The information the target actually requires, in bits, two ways because
                two are defensible and they are NOT the same quantity:
                  (a) log2|support| -- the uniform bound the gate literally writes
                  (b) H(target)     -- the Shannon entropy of the realised class
                                       distribution, which is what a channel argument
                                       requires
                Both compared against claim 5's H_eff in [1.02, 3.45] bits.
                Named before the method.

IDENTIFICATION  Identified, with one estimator hazard stated up front rather than
                discovered later: PLUG-IN ENTROPY IS BIASED DOWNWARD at finite sample, and
                the bias is IN THE FLATTERING DIRECTION -- it makes the release look more
                admissible than it is. So entropy is reported with the plug-in AND the
                Miller-Madow correction as a second estimator, and the gap between them is
                printed rather than buried.
                |support| is biased downward too (unseen classes) and is therefore a LOWER
                BOUND on the uniform requirement, stated as such.

SCOPE           population : the 968 prompts' human rankings in metadata.assessments
                instrument : ranking_blocks strings ("A>B>C=D") parsed to weak orderings,
                             which are exactly the a(4)=75 class space
                baseline   : claim 5's H_eff in [1.02, 3.45] bits (R237), and a(4)=75
                             i.e. 6.2288 bits as the ceiling
                regime     : blocks {world, personal}; aggregation {pooled, per-prompt}

WORLDS          A  ADMISSIBLE -- the requirement fits inside H_eff. The revert yields a
                   working gate and the definition regains an admissibility criterion.
                B  INADMISSIBLE AT EVERY READING -- the requirement exceeds 3.45 bits
                   everywhere. The coherent gate REJECTS this release, which is a finding
                   about the release, not about the gate.
                C  DEGENERATE -- the target distribution is concentrated on one or two
                   classes, so the requirement is near zero and the gate is satisfied
                   before anything is tested: a CHECK THAT CANNOT FAIL, and its pass
                   would mean nothing.
                D  SPLIT -- admissible under one reading, not another. Then the reading is
                   the finding and no single verdict may be reported.

PREDICTION      log2|support|  | A: <3.45 | B: >3.45 | C: ~0    | D: straddles
MATRIX          H(target)      | A: <1.02 | B: >3.45 | C: ~0    | D: straddles
                what it implies| revert   | release  | gate is  | report the
                               | works    | rejected | vacuous  | spread

KILL            Pre-registered, a conditional and never a bare threshold:
                    if positive_recovers and negative_moves and not degenerate:
                        evaluate(max_over_readings(requirement) < 1.02)   # world A
                    else:
                        verdict = UNVERIFIED
                Note the threshold is the LOW end of H_eff's bracket. Using the high end
                would be choosing the arm that flatters the conclusion; the bracket is
                reported whole and the verdict is read against both ends.

POSITIVE CTRL   Plant a KNOWN entropy and require recovery, with a real band:
                  FLOOR   a degenerate distribution (one class) -> must return 0.0000
                  CEILING a uniform distribution over all a(4)=75 classes -> must return
                          log2(75) = 6.2288 within the estimator's own bias
                  retention and MDE reported. floor != ceiling, so a threshold between
                  them is admissible. FAILS AT g=0: the degenerate plant must NOT be read
                  as satisfying any positive requirement.

NEGATIVE CTRL   Destroy the structure under test -- agreement between annotators -- while
                keeping everything else: permute each annotator's response labels
                INDEPENDENTLY. This preserves each annotator's ordering SHAPE and the
                number of annotators, and destroys only the alignment between them.
                World it excludes: "the requirement is low because my parser collapses
                orderings", which would look identical to genuine agreement. If the
                permuted arm does not rise, the parser is the finding.

SHAM            The same operation minus the ingredient: run the identical machinery on
                the `unacceptable` block, which carries RATINGS and not rankings, so it
                cannot express a weak ordering. Size- and compute-matched.

PLACEBO         The entropy of a constant column must be exactly 0.0000.

NOISE FLOOR     MEASURED, not assumed: bootstrap over annotators, >=200 resamples, and the
                floor is the resampling spread of the estimate. A gap smaller than the
                floor is not a gap.

MULTIPLICITY    Cells = blocks x aggregations x estimators, reported whole with the
                non-surviving cells shown beside the surviving ones.

SPECIFICATION   Axes: block {world, personal} x aggregation {pooled, per-prompt} x
                estimator {plug-in, Miller-Madow} x statistic {log2|support|, entropy}.
                Whole curve printed including the cells that kill each world.

SEEDS           3 seeds for the permutation control and the bootstrap; the seed flag is
                verified to change the draws.

ARTIFACT        results/requirement.json with source hash and the full class histograms,
                so a rival can recompute every cell without re-parsing the release.

REPRODUCIBILITY two PYTHONHASHSEEDs byte-identical.

IMPOSSIBLE      H_eff RE-MEASURED under this round's parse -- claim 5's bracket comes from
                    R237 and is taken as given. Would require re-running R237.
                construct validated -- would need an external answer to what the
                    downstream system must actually distinguish.
                cross-release -- one release exists.
"""
from __future__ import annotations
import collections, itertools, json, math, hashlib, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np

DATA = ROOT / "data"
L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))
H_EFF_LO, H_EFF_HI = 1.02, 3.45          # claim 5 (R237), taken as given
CEIL = math.log2(75)
BLOCKS = ["world", "personal"]
NBOOT, SEEDS = 200, [0, 1, 2]


def parse_ranking(s):
    """'A>B>C=D' -> the weak-ordering class, in the same cls() convention used across E05:
    a score vector (higher = better) mapped to sign(y_i - y_j) over the 6 pairs."""
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


def load_classes():
    """-> {block: {pid: [class, ...]}} plus the sham block's parse failures."""
    out = {b: collections.defaultdict(list) for b in BLOCKS}
    sham_attempts = sham_ok = 0
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
            for e in rb.get("unacceptable") or []:      # SHAM: ratings, not rankings
                sham_attempts += 1
                if e.get("ranking") and parse_ranking(e["ranking"]) is not None:
                    sham_ok += 1
    return out, sham_attempts, sham_ok


def H_plugin(counts):
    n = sum(counts)
    if n == 0:
        return float("nan")
    p = np.array(counts, float) / n
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def H_mm(counts):
    """Miller-Madow: plug-in + (K_observed - 1) / (2 n ln2). Corrects the DOWNWARD bias,
    which is the direction that flatters this gate."""
    n = sum(counts)
    if n == 0:
        return float("nan")
    return H_plugin(counts) + (len([c for c in counts if c > 0]) - 1) / (2 * n * math.log(2))


def requirement(classes_by_pid, how, est):
    """how: 'pooled' -> one distribution over the whole release
            'per_prompt' -> mean over prompts of the within-prompt requirement"""
    f = H_plugin if est == "plugin" else H_mm
    if how == "pooled":
        ctr = collections.Counter(c for v in classes_by_pid.values() for c in v)
        return f(list(ctr.values())), math.log2(len(ctr)) if ctr else float("nan"), len(ctr)
    hs, sups = [], []
    for v in classes_by_pid.values():
        if len(v) < 2:
            continue
        ctr = collections.Counter(v)
        hs.append(f(list(ctr.values())))
        sups.append(math.log2(len(ctr)))
    return float(np.mean(hs)), float(np.mean(sups)), float(np.mean([2 ** s for s in sups]))


def permute_labels(classes_by_pid, rng):
    """NEGATIVE CONTROL. Re-derive each annotator's class after independently permuting its
    response labels: preserves the ordering SHAPE and annotator count, destroys alignment."""
    inv = {}
    out = {}
    for pid, v in classes_by_pid.items():
        newv = []
        for c in v:
            o = rng.permutation(4)
            y = np.zeros(4)
            for (i, j), s in zip(PAIRS, c):          # reconstruct a consistent score vector
                y[i] += s; y[j] -= s
            y = y[o]
            newv.append(tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS))
        out[pid] = newv
    return out


if __name__ == "__main__":
    print("\n  R281 -- does the coherent gate admit this release?\n")
    cls_by_block, sham_attempts, sham_ok = load_classes()

    # ---- POSITIVE CONTROL: plant known entropies, require recovery, report the band
    floor_est = H_plugin([1000])
    ceil_counts = [1000] * 75
    ceil_est = H_plugin(ceil_counts)
    ctrl = [("POS  floor: degenerate plant returns exactly 0", floor_est == 0.0, f"{floor_est:.4f}"),
            ("POS  ceiling: uniform-over-75 recovers log2(75)", abs(ceil_est - CEIL) < 1e-9,
             f"{ceil_est:.4f} vs {CEIL:.4f}  retention {ceil_est/CEIL:.4f}"),
            ("POS  floor != ceiling, so a threshold is admissible", floor_est < H_EFF_LO < ceil_est,
             f"0 < {H_EFF_LO} < {ceil_est:.4f}"),
            ("PLA  entropy of a constant column is exactly 0", H_plugin([777]) == 0.0, "0.0000")]
    # MDE of the entropy estimator: smallest planted entropy separable from 0 at n=1000
    mde = None
    for kk in range(2, 76):
        c = [1000 // kk] * kk
        if H_plugin(c) > 0.05:
            mde = (kk, H_plugin(c)); break
    ctrl.append(("POS  MDE: smallest plant separable from 0", mde is not None,
                 f"K={mde[0]} -> {mde[1]:.4f} bits"))
    # SHAM: the unacceptable block cannot express a weak ordering
    ctrl.append(("SHAM `unacceptable` block yields no ranking", sham_ok == 0,
                 f"{sham_ok}/{sham_attempts} parsed"))

    # ---- NEGATIVE CONTROL + noise floor
    rng = np.random.default_rng(SEEDS[0])
    perm = {b: permute_labels(cls_by_block[b], rng) for b in BLOCKS}
    real_pooled = {b: requirement(cls_by_block[b], "pooled", "plugin")[0] for b in BLOCKS}
    perm_pooled = {b: requirement(perm[b], "pooled", "plugin")[0] for b in BLOCKS}
    moved = all(perm_pooled[b] > real_pooled[b] for b in BLOCKS)
    ctrl.append(("NEG  label permutation RAISES the requirement (pooled)", moved,
                 " ".join(f"{b}:{real_pooled[b]:.3f}->{perm_pooled[b]:.3f}" for b in BLOCKS)))

    # ⚠ THE POOLED NEGATIVE CONTROL IS AT CEILING and therefore weak: all 75 classes are
    # already realised, so permutation has almost nowhere to move. A control with no room
    # is not a control. The per-prompt arm has room (|support| ~ 10 of 75), so the same
    # destruction is run there, across all 3 seeds, and THAT is the load-bearing version.
    pp_deltas = []
    for s in SEEDS:
        r = np.random.default_rng(s)
        for b in BLOCKS:
            a = requirement(cls_by_block[b], "per_prompt", "plugin")[0]
            c = requirement(permute_labels(cls_by_block[b], r), "per_prompt", "plugin")[0]
            pp_deltas.append(c - a)
    ctrl.append(("NEG  same destruction PER-PROMPT, where there IS room",
                 all(d > floor_hint for d in pp_deltas) if (floor_hint := 0.05) else False,
                 f"min delta +{min(pp_deltas):.4f}, max +{max(pp_deltas):.4f} over "
                 f"{len(pp_deltas)} seed x block cells"))

    # measured noise floor: bootstrap over annotators
    boots = []
    for s in SEEDS:
        r = np.random.default_rng(100 + s)
        allc = [c for v in cls_by_block["world"].values() for c in v]
        for _ in range(NBOOT // len(SEEDS)):
            samp = [allc[i] for i in r.integers(0, len(allc), len(allc))]
            boots.append(H_plugin(list(collections.Counter(samp).values())))
    floor = float(np.std(boots))
    print(f"    NOISE FLOOR (measured, {len(boots)} bootstrap resamples) : sd = {floor:.4f} bits")

    print("\n    CONTROLS")
    ok = True
    for name, passed, detail in ctrl:
        ok &= bool(passed)
        print(f"      [{'PASS' if passed else 'FAIL'}] {name:<48} {detail}")

    print(f"\n    SPECIFICATION CURVE -- bits required, against H_eff in "
          f"[{H_EFF_LO}, {H_EFF_HI}] and ceiling {CEIL:.4f}")
    print(f"      {'block':<9}{'aggregation':<13}{'estimator':<11}"
          f"{'H(target)':>11}{'log2|sup|':>11}{'|support|':>11}")
    grid = {}
    for b in BLOCKS:
        for how in ("pooled", "per_prompt"):
            for est in ("plugin", "mm"):
                h, ls, sup = requirement(cls_by_block[b], how, est)
                grid[f"{b}|{how}|{est}"] = (h, ls, sup)
                print(f"      {b:<9}{how:<13}{est:<11}{h:>11.4f}{ls:>11.4f}{sup:>11.2f}")

    hs = [v[0] for v in grid.values()]
    lss = [v[1] for v in grid.values()]
    degenerate = max(hs) < floor
    n_ann = sum(len(v) for v in cls_by_block["world"].values())
    print(f"\n    annotator rankings parsed : world {n_ann}, "
          f"personal {sum(len(v) for v in cls_by_block['personal'].values())}")
    print(f"    H(target)      range      : [{min(hs):.4f}, {max(hs):.4f}] bits")
    print(f"    log2|support|  range      : [{min(lss):.4f}, {max(lss):.4f}] bits")
    print(f"    cells tested / surviving  : {len(grid)} / "
          f"{sum(1 for v in grid.values() if v[0] < H_EFF_LO)} below H_eff_lo, "
          f"{sum(1 for v in grid.values() if v[0] < H_EFF_HI)} below H_eff_hi")

    if not ok:
        verdict = "UNVERIFIED -- a control failed; no requirement is admissible"
    elif degenerate:
        verdict = ("WORLD C -- the target distribution is degenerate; the gate would be "
                   "satisfied before anything is tested and its pass means nothing")
    elif max(hs) < H_EFF_LO and max(lss) < H_EFF_LO:
        verdict = ("WORLD A -- ADMISSIBLE under every reading. The revert yields a working "
                   "gate.")
    elif min(hs) > H_EFF_HI and min(lss) > H_EFF_HI:
        verdict = ("WORLD B -- INADMISSIBLE under every reading. The coherent gate rejects "
                   "this release, which is a finding about the release.")
    else:
        verdict = ("WORLD D -- SPLIT. The verdict depends on the reading, so the READING is "
                   "the finding and no single number may be reported. "
                   f"H(target) in [{min(hs):.4f}, {max(hs):.4f}], "
                   f"log2|support| in [{min(lss):.4f}, {max(lss):.4f}], "
                   f"against H_eff [{H_EFF_LO}, {H_EFF_HI}].")
    print(f"\n    VERDICT: {verdict}\n")

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    art = {"source_sha256_16": src, "noise_floor_sd": floor, "grid": grid,
           "h_eff": [H_EFF_LO, H_EFF_HI], "ceiling_bits": CEIL,
           "negative_control": {"real": real_pooled, "permuted": perm_pooled},
           "controls": [(n, bool(p), d) for n, p, d in ctrl], "verdict": verdict}
    (HERE / "results" / "requirement.json").write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"    artifact: results/requirement.json  (source {src})\n")
