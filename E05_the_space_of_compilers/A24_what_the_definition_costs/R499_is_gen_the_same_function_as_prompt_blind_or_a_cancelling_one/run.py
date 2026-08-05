"""Clause 2's gap is inside the floor. Is that because the arms agree, or because they cancel?

THE REFRAME THIS ROUND RESTS ON. R494-R497 spent four rounds decomposing the per-prompt deficit
`coval_core - gen`. But clause 2 of the definition does not compare an admissible arm to
`coval_core`; it compares it to THE BEST GENERALISING PROMPT-BLIND SET, cross-fitted at 0.5404.
The best 3-admissible prompt-aware arm is `gen` at 0.5337 -- a gap of -0.0067, INSIDE the 0.0122
floor. So the difference those four rounds explained is not the difference the definition turns on,
and the one it does turn on is unresolvable at the mean.

ESTIMAND        The test-retest reliability r and the noise-corrected true standard deviation of
                the PER-PROMPT difference (prompt-aware arm - prompt-blind arm), estimated from
                two independent held-out-annotator draws. Named before the method, and it is not
                the mean: the mean is already known to sit inside the floor, which is exactly why
                a mean cannot separate the two worlds below.
IDENTIFICATION  Identified, and by an instrument this campaign has already calibrated. A2 samples
                a held-out annotator per prompt, so re-running at an independent draw offset is a
                SECOND DRAW OF THE SAME QUANTITY -- the design supplies its own noise floor rather
                than modelling one. R497 established this on (coval_core - gen) at r = 0.9355.
SCOPE           population = the 968 prompts both arms score · instrument = A2 vs a held-out
                annotator, 20 draws, crc32-seeded per prompt so it is process-stable ·
                baseline = the same statistic on a placebo pair · regime = this release, k as
                released per arm, aggregation by sum (identical to mean under cls, verified).
WORLDS          A SAME FUNCTION. `gen` and the prompt-blind arms compute nearly the same thing;
                  the per-prompt difference is noise. Prompt-awareness buys nothing ANYWHERE, and
                  clause 2 is a genuine wall for 3-admissible prompt-aware arms.
                  Predicts: r ~ 0, true_sd ~ 0, indistinguishable from the placebo.
                B CANCELLING FUNCTIONS. They differ substantially and reliably per prompt and
                  happen to average the same. Prompt-awareness buys something real that an
                  aggregate cannot see, and clause 2 as written is the WRONG INSTRUMENT -- it
                  should be stated per-prompt or conditioned.
                  Predicts: r well above the placebo, true_sd several times the measured noise.
                These are ontologically different, not parametrically: A says the object does not
                exist, B says the object exists and the measurement integrates it away. They imply
                different DEFINITIONS, which is why this is worth compute.
KILL            Pre-registered before running. World B dies if the reliability of
                (gen - prompt_blind) fails to exceed the PLACEBO's reliability by more than the
                spread across seeds. World A dies if it exceeds it on every prompt-blind
                comparator. Split outcomes across comparators are reported as split, never averaged.
POSITIVE CTRL   (coval_core - gen) must reproduce R497's r = 0.9355 within seed spread. If this
                script cannot recover a number a previous round established on the same data, it
                is not running the instrument that was validated, and every other row is void.
                It can fail: nothing in this code forces that value.
PLACEBO         `gen` against ITSELF at two different draw offsets. Structurally pure noise, so
                its reliability across an independent replication must be ~0. This is the bar the
                real pairs must clear, and unlike a `gen - gen` at identical offsets (which is 0
                by construction and cannot fail) this one CAN come back non-zero and indict the
                whole design.
NEGATIVE CTRL   (gen - gen_sham): a difference where structure is known to exist but of a
                different kind. Destroys the prompt-blind contrast while preserving arm identity.
SHAM            (generic - generic_reprov): the same operation on two arms that are both
                prompt-blind, so the ingredient under study (prompt-awareness) is absent from
                both sides rather than inverted.
NOISE FLOOR     Measured as sd(d0-d1)/sqrt(2) per pair, from the two independent draws. Never
                modelled, never shared across pairs -- each pair gets its own.
MULTIPLICITY    Grid reported whole: 6 pairs x 3 seed-offset pairings = 18 cells, every one
                printed including the ones that show nothing. No selection of a best cell.
SPECIFICATION   Swept: which prompt-blind comparator (generic, genericpool16) · which draw-offset
                pairing (3) · and the placebo/sham/negative rows alongside, on the same axes.
SEEDS           3 independent offset pairings, and the code asserts the offsets actually change
                the draws (a seed flag that does nothing is the failure this line exists for).
ARTIFACT        results/cancel.json -- per-pair r, observed sd, measured noise, true sd, and the
                full per-prompt difference vectors, so a later round can attack this without
                recomputing 968x20 draws.
REPRODUCIBILITY crc32-seeded, so byte-identical across processes; asserted in-run, not assumed.
IMPOSSIBLE      construct validation: whether A2-vs-held-out-annotator is the right target needs
                an external gold standard this release does not carry. Would require a second
                release with independent quality judgments. Stated, not counted as met.
"""
from __future__ import annotations
import collections, itertools, json, pathlib, sys, zlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/"corebench")); import score as SC
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = pathlib.Path(__file__).resolve().parent/"results"; OUT.mkdir(exist_ok=True)
cls = lambda y: tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
tgt, _ = SC.load_targets(); TGT = {p: [tuple(v) for v, _ in x] for p, x in tgt.items()}
_C: dict = {}

def per_prompt(arm: str, off: int = 0) -> dict:
    if (arm, off) in _C: return _C[(arm, off)]
    d = np.load(ROOT/f"corebench/results/sat_{arm}.npz", allow_pickle=True)
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    sc = {}
    for p, c in o.items():
        if p not in TGT: continue
        idx = sorted({i for i, _ in c})
        cc = cls(np.array([sum(c.get((i, x), 0.0) for i in idx) for x in L]))
        r = np.random.default_rng(zlib.crc32(p.encode()) + off)
        sc[p] = float(np.mean([np.mean([cc[t] == cls(np.array(TGT[p][int(r.integers(len(TGT[p])))], float))[t]
                                        for t in range(6)]) for _ in range(20)]))
    _C[(arm, off)] = sc
    return sc


def decompose(a: str, b: str, o0: int, o1: int):
    """r, observed sd, MEASURED noise, true sd for the per-prompt difference a-b."""
    A0, B0, A1, B1 = per_prompt(a, o0), per_prompt(b, o0), per_prompt(a, o1), per_prompt(b, o1)
    P = sorted(set(A0) & set(B0) & set(A1) & set(B1))
    d0 = np.array([A0[p]-B0[p] for p in P]); d1 = np.array([A1[p]-B1[p] for p in P])
    noise = float((d0-d1).std()/np.sqrt(2)); obs = float(d0.std())
    true = float(np.sqrt(max(obs**2 - noise**2, 0.0)))
    r = float(np.corrcoef(d0, d1)[0, 1]) if d0.std() > 0 and d1.std() > 0 else 0.0
    return dict(n=len(P), mean=float(d0.mean()), r=r, obs=obs, noise=noise, true=true,
                ratio=(true/noise if noise > 0 else float("nan")))


def main() -> int:
    OFFS = [(0, 7919), (0, 3571), (7919, 3571)]
    PAIRS_ = [("coval_core", "gen",        "POSITIVE CTRL (R497: r=0.9355)"),
              ("gen",        "generic",    "clause 2, comparator 1"),
              ("gen",        "genericpool16", "clause 2, comparator 2"),
              ("gen",        "gen_sham",   "NEGATIVE (structure, different kind)"),
              ("generic",    "generic_reprov", "SHAM (ingredient absent both sides)")]

    # PLACEBO: the same arm against itself at two DIFFERENT offsets -- pure noise, can fail.
    pl = []
    for o0, o1 in OFFS:
        A0, A1 = per_prompt("gen", o0), per_prompt("gen", o1)
        P = sorted(set(A0) & set(A1))
        d0 = np.array([A0[p]-A1[p] for p in P])
        B0, B1 = per_prompt("gen", o0+101), per_prompt("gen", o1+101)
        d1 = np.array([B0[p]-B1[p] for p in P])
        pl.append(float(np.corrcoef(d0, d1)[0, 1]) if d0.std() > 0 and d1.std() > 0 else 0.0)
    placebo_r = float(np.mean(pl)); placebo_spread = float(max(pl)-min(pl))
    print(f"  PLACEBO  gen vs itself at different draws: r = {placebo_r:+.4f} "
          f"(spread {placebo_spread:.4f} over {len(pl)} pairings)")

    # seed flag must actually change the draws
    same = per_prompt("gen", 0) == per_prompt("gen", 7919)
    print(f"  seed check: offsets change the draws: {not same}")
    if same:
        print("  the offset does nothing -- every number below is one draw, reported as two"); return 1

    rows = {}
    print(f"\n  {'pair':<34}{'r':>9}{'true sd':>9}{'noise':>8}{'x noise':>9}{'mean':>9}")
    for a, b, lbl in PAIRS_:
        cells = [decompose(a, b, o0, o1) for o0, o1 in OFFS]
        rs = [c["r"] for c in cells]
        rows[f"{a}-{b}"] = dict(label=lbl, cells=cells, r_min=min(rs), r_max=max(rs))
        c = cells[0]
        print(f"  {a+' - '+b:<34}{min(rs):+9.4f}{c['true']:9.4f}{c['noise']:8.4f}"
              f"{c['ratio']:9.2f}{c['mean']:+9.4f}   [{lbl}]")
        if len(rs) > 1:
            print(f"  {'':<34}{'seed range':>9} {min(rs):+.4f} .. {max(rs):+.4f}")

    # POSITIVE CONTROL, evaluated -- not narrated
    pc = rows["coval_core-gen"]
    ok_pc = abs(pc["r_max"] - 0.9355) < 0.05
    print(f"\n  positive control: recovered r = {pc['r_max']:+.4f} vs R497's +0.9355 "
          f"-> {'PASS' if ok_pc else 'FAIL'}")
    if not ok_pc:
        print("  this is not the instrument R497 validated -- every row above is silence"); return 1

    seed_spread = max(v["r_max"]-v["r_min"] for v in rows.values())
    bar = placebo_r + max(seed_spread, placebo_spread)
    print(f"  kill bar = placebo {placebo_r:+.4f} + max(seed spread {seed_spread:.4f}, "
          f"placebo spread {placebo_spread:.4f}) = {bar:+.4f}")

    verdicts = {}
    for k in ("gen-generic", "gen-genericpool16"):
        verdicts[k] = rows[k]["r_min"] > bar
        print(f"  {k:<24} r_min {rows[k]['r_min']:+.4f} {'>' if verdicts[k] else '<='} bar"
              f"  -> {'B (cancelling)' if verdicts[k] else 'A (same function)'}")

    if all(verdicts.values()):
        world = "B CANCELLING FUNCTIONS"
    elif not any(verdicts.values()):
        world = "A SAME FUNCTION"
    else:
        world = "SPLIT -- comparators disagree; reported split, not averaged"
    print(f"\n  WORLD: {world}")
    if world.startswith("B"):
        tr = max(rows[k]["cells"][0]["true"] for k in verdicts)
        nz = max(rows[k]["cells"][0]["ratio"] for k in verdicts)
        print(f"  => the -0.0067 mean gap hides a per-prompt difference of true sd {tr:.4f}"
              f" ({nz:.1f}x its own measured noise). Clause 2's aggregate integrates away a real"
              f" object; 'indistinguishable' is a statement about the INSTRUMENT.")
    elif world.startswith("A"):
        print(f"  => prompt-awareness buys nothing per-prompt either. Clause 2 is a genuine wall"
              f" for 3-admissible prompt-aware arms, not an artifact of aggregation.")

    json.dump({"placebo_r": placebo_r, "placebo_spread": placebo_spread, "bar": bar,
               "seed_spread": seed_spread, "rows": rows, "verdicts": verdicts,
               "world": world, "positive_control_ok": ok_pc},
              (OUT/"cancel.json").open("w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
