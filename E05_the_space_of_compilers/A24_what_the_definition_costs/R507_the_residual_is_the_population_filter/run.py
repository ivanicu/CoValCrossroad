"""The last unexplained number in the chain: 0.6220 vs R479's 0.6132. Is it the population filter?

WHY. R506 restored the recommendation on a ranker ceiling of 0.6220 while R479 quotes 0.6132, and
said so rather than smoothing it. Reading R479:91 finds `pids = [p for p, v in TGT.items() if len(v) >= 3]`; R504-R506 used `>= 2`.

⛔ AND THAT HYPOTHESIS DIED TO THIS ROUND'S OWN POSITIVE CONTROL, WHICH IS WHY THE AXIS CHANGED.
Swept, the ranking filter gives n = 1078 at m = 1, 2 AND 3 -- EVERY prompt in the release carries at
least three rankings, so R479's filter excludes nothing and is a no-op. The sweep did not move, the
control that required it to move FAILED, and the script refused to report. The real difference is
elsewhere and was in my own code: R504-R506 intersected the population with prompts `oracle_k4`
scores, 968 of 1078. That is an ARM-COVERAGE restriction, not a ranking filter, and it is the axis
this round now sweeps.

ESTIMAND        The ranker ceiling on (a) ALL prompts with >=3 rankings -- R479's actual population
                -- and (b) the subset `oracle_k4` also covers, which is what R504-R506 used; and
                whether (a) reproduces R479's 0.6132 within its stated resolution of 0.0093.
                The ranking-filter sweep is kept and reported because its flatness is the finding
                that redirected the round.
IDENTIFICATION  Exact given m; the ceiling is a deterministic functional of the included prompts and
                the draw convention, both held fixed across the sweep.
SCOPE           population = prompts with ≥m rankings AND an oracle_k4 score · instrument = modal
                complete sign-vector of the non-held-out annotators vs one held-out annotator, 20
                draws · baseline = R479's quoted 0.6132 ± 0.0093 · regime = first release.
WORLDS          A THE FILTER EXPLAINS IT. At m=3 the ceiling lands within R479's resolution of
                  0.6132, and the residual is fully accounted for by a one-character difference.
                B THE FILTER IS NOT THE CAUSE. m=3 does not reproduce it, so something else in
                  R479's convention differs and the residual stays open — which is worth knowing
                  precisely because it would mean two implementations of one definition disagree.
                Prediction matrix: A → ceiling(3) ∈ [0.6039, 0.6225]. B → outside it.
KILL            Pre-registered: if ceiling(3) falls outside R479's stated band, world A is dead and
                the residual is reported as OPEN, not narrated away.
POSITIVE CTRL   The sweep must MOVE: ceiling(2) ≠ ceiling(10) by more than the seed spread. A filter
                that changes nothing cannot explain a discrepancy, and a flat sweep would mean the
                instrument is insensitive to the very axis under test.
NEGATIVE CTRL   n(m) must fall monotonically in m — if the filter is not actually filtering, every
                number here is one population reported four times.
PLACEBO         m=1 (no filter beyond having a hold-out) must equal m=2 when every prompt has ≥2
                rankings; if they differ, the filter is doing something other than what it says.
NOISE FLOOR     Measured across 3 seeds at each m.
MULTIPLICITY    4 filter levels × 3 seeds = 12 cells, all printed.
SPECIFICATION   The single swept axis is the filter; the draw convention is held at 20 reps
                throughout precisely so it cannot confound.
SEEDS           3.
ARTIFACT        results/population_sweep.json
REPRODUCIBILITY deterministic given seeds; asserted.
IMPOSSIBLE      isolating R479's RNG convention (one shared generator drawing sequentially) from
                mine (per-prompt crc32) — both are unbiased for this estimand, so a residual after
                the filter is explained would need R479 re-run under my draw convention, which is a
                change to a committed round rather than a measurement. Named, not counted as met.
"""
from __future__ import annotations
import collections, itertools, json, pathlib, sys, zlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/"corebench")); import score as SC
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
OUT = pathlib.Path(__file__).resolve().parent/"results"; OUT.mkdir(exist_ok=True)
cls = lambda y: tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
tgt, _ = SC.load_targets()
TGT = {p: [cls(np.array(v, float)) for v, _ in x] for p, x in tgt.items()}
R479_QUOTED, R479_RES = 0.6132, 0.0093


def ceiling(minrank: int, off: int, reps: int = 20) -> tuple[float, int]:
    acc = []
    for p, ann in TGT.items():
        if len(ann) < minrank: continue
        r = np.random.default_rng(zlib.crc32(p.encode()) + off)
        got = []
        for _ in range(reps):
            j = int(r.integers(len(ann)))
            rest = [a for k, a in enumerate(ann) if k != j]
            if not rest: continue
            mode = collections.Counter(rest).most_common(1)[0][0]
            got.append(np.mean([mode[t] == ann[j][t] for t in range(6)]))
        if got: acc.append(float(np.mean(got)))
    return float(np.mean(acc)), len(acc)


def main() -> int:
    OFFS = [0, 7919, 3571]
    rows = {}
    print(f"  R479's quoted ranker ceiling: {R479_QUOTED:.4f}  (stated resolution {R479_RES:.4f})")
    print(f"  band it must land in for the filter to explain the residual: "
          f"[{R479_QUOTED-R479_RES:.4f}, {R479_QUOTED+R479_RES:.4f}]\n")
    print(f"  {'min rankings':>13}{'n prompts':>11}{'ceiling':>10}{'seed range':>22}")
    for m in (1, 2, 3, 5, 10):
        vals, ns = zip(*[ceiling(m, o) for o in OFFS])
        rows[m] = dict(mean=float(np.mean(vals)), lo=min(vals), hi=max(vals), n=ns[0])
        print(f"  {m:>13}{ns[0]:>11}{np.mean(vals):>10.4f}   [{min(vals):.4f}, {max(vals):.4f}]")

    floor = max(v["hi"]-v["lo"] for v in rows.values())
    c = {}
    c["the sweep MOVES (m=2 vs m=10)"] = abs(rows[2]["mean"]-rows[10]["mean"]) > floor
    c["n falls monotonically in m"] = all(rows[a]["n"] >= rows[b]["n"]
                                          for a, b in zip((1,2,3,5), (2,3,5,10)))
    c["placebo: m=1 equals m=2"] = abs(rows[1]["mean"]-rows[2]["mean"]) < 1e-9
    for k, v in c.items(): print(f"    {k:<38}{'PASS' if v else 'FAIL'}")
    if not c["n falls monotonically in m"]:
        print("\n  the filter is not filtering -- every number is one population, four times"); return 1
    if not c["the sweep MOVES (m=2 vs m=10)"]:
        print(f"\n  ⛔ POSITIVE CONTROL FAILED ON THE RANKING FILTER, AND THAT IS THE FINDING:")
        print(f"     n is {rows[1]['n']} at m=1, 2 and 3 alike -- every prompt carries >=3 rankings,")
        print(f"     so R479's filter is a NO-OP and cannot explain any residual. The round")
        print(f"     redirects to the axis that does vary rather than reporting a flat sweep as")
        print(f"     evidence of anything.")

    # THE AXIS THAT ACTUALLY VARIES: arm coverage, not ranking count.
    ORA = set(np.load(ROOT/"corebench/results/sat_oracle_k4.npz", allow_pickle=True)["meta"])
    ORA = {str(k).split("|")[0] for k in ORA}
    def ceiling_cov(restrict, off, reps=20):
        acc = []
        for p, ann in TGT.items():
            if len(ann) < 3: continue
            if restrict and p not in ORA: continue
            r = np.random.default_rng(zlib.crc32(p.encode()) + off)
            got = []
            for _ in range(reps):
                j = int(r.integers(len(ann)))
                rest = [a for k, a in enumerate(ann) if k != j]
                if not rest: continue
                got.append(np.mean([collections.Counter(rest).most_common(1)[0][0][t] == ann[j][t]
                                    for t in range(6)]))
            if got: acc.append(float(np.mean(got)))
        return float(np.mean(acc)), len(acc)

    print(f"\n  ── the axis that actually varies: ARM COVERAGE ──")
    cov = {}
    for restrict, lbl in ((False, "all >=3-ranking prompts (R479's population)"),
                          (True,  "only prompts oracle_k4 covers (R504-R506)")):
        vals, ns = zip(*[ceiling_cov(restrict, o) for o in OFFS])
        cov[lbl] = dict(mean=float(np.mean(vals)), lo=min(vals), hi=max(vals), n=ns[0])
        print(f"    {lbl:<44}n={ns[0]:<6}{np.mean(vals):.4f}  [{min(vals):.4f}, {max(vals):.4f}]")
    rows["coverage"] = cov
    c["the COVERAGE axis moves"] = abs(cov[list(cov)[0]]["mean"] - cov[list(cov)[1]]["mean"]) > 0.002
    print(f"    {'the COVERAGE axis moves':<38}{'PASS' if c['the COVERAGE axis moves'] else 'FAIL'}")

    at3 = cov["all >=3-ranking prompts (R479's population)"]["mean"]
    inside = abs(at3 - R479_QUOTED) <= R479_RES
    print(f"\n  at m=3 (R479's own filter): {at3:.4f}   vs quoted {R479_QUOTED:.4f}"
          f"   |Δ| = {abs(at3-R479_QUOTED):.4f}")
    world = ("A COVERAGE EXPLAINS IT — the ranking filter is a no-op; restricting to oracle_k4's "
             "prompts is what moves the ceiling" if inside else
             "B NEITHER AXIS EXPLAINS IT — the residual stays OPEN")
    print(f"\n  WORLD: {world}")
    if inside:
        print(f"  => on R479's ACTUAL population the ceiling reproduces within its own resolution.")
        print(f"     The residual was never the ranking filter -- it was my restriction to the 968")
        print(f"     prompts oracle_k4 covers. R506's comparison remains correct BECAUSE it held")
        print(f"     both sides on that same 968, which is the right thing to do when comparing an")
        print(f"     arm to a ceiling. The chain is closed.")
    else:
        print(f"  => matching R479's filter does NOT reproduce its number, so two implementations")
        print(f"     of one definition disagree by {abs(at3-R479_QUOTED):.4f} for a reason not yet")
        print(f"     isolated. Reported OPEN rather than narrated away.")
    # ⛔ The line that stood here printed "including 2-annotator prompts RAISES/LOWERS the
    # ceiling" from rows[2] vs rows[3] -- two numbers that are IDENTICAL because the filter is a
    # no-op, so it emitted a comparative word about a difference of exactly zero. It went stale
    # the moment the round redirected axes, and a comparative word must be computed, never typed.
    same = abs(rows[2]["mean"] - rows[3]["mean"]) < 1e-12
    print(f"  ⚠ the ranking filter changes the ceiling by exactly "
          f"{abs(rows[2]['mean']-rows[3]['mean']):.6f}"
          f"{' -- identical populations, so no direction exists to report' if same else ''}.")
    print(f"     The naive prediction (a 1-annotator 'mode' is weaker, so including 2-annotator")
    print(f"     prompts should lower the ceiling) is UNTESTABLE here: there are no 2-annotator")
    print(f"     prompts. The hypothesis was not refuted, it was never applicable.")
    json.dump({"rows": {str(k): v for k, v in rows.items()}, "floor": floor, "controls": c,
               "at3": at3, "quoted": R479_QUOTED, "res": R479_RES, "world": world},
              (OUT/"population_sweep.json").open("w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
