#!/usr/bin/env python3
"""
R696 -- do the corpus's a2 SCORES and its ② VERDICTS agree? Three sources, three exact tests.

CHECK #298 ON R695's NEXT LINE -- IT PROPOSED A COMPARISON OVER A POPULATION OF ONE.
  It asked "which arm of a PAIR scores higher"; R695 had just measured the assemblable-pair count at
  1. ⭐ THIRD CLOSING LINE IN A ROW to propose a comparison whose population the same round had
  measured as ~1 (R685 proposed a derivation, R694 proposed data that does not exist, this proposed
  a pairwise test with one pair). Reframed over ARMS it is runnable, and that reframing is the round.

⚠ AND NOT OVER A UNION. The 12-arm coverage is a union of four artifacts; comparing a2 across
  artifacts assumes they are the same quantity from the same run, which is the assumption under test.
  Three sources are independently runnable, so this is a SPECIFICATION CURVE, not a pooled sample.

ESTIMAND        per source: do ②-admitted arms rank above ②-rejected ones by that source's own a2?
                Statistic: admitted arms' mean rank vs the EXACT null over all C(n, n_adm) labellings.
IDENTIFICATION  ⚠ agreement across three sources is convergence across three ARTIFACTS, not
                independent replication -- they may share an upstream scoring run, which this corpus
                does not record.
SCOPE           population : arms carrying an a2-named value within a single artifact
                instrument : rank statistic + exact enumeration of labellings
                             instrument unit = AN ARM'S RANK WITHIN ONE ARTIFACT
                             claim unit      = AGREEMENT BETWEEN SCORES AND VERDICTS
                             ⚠ NOT EQUAL -- a rank agreement can arise from a shared upstream run.
                baseline   : the exact null; and the resolution floor 1/C(n, n_adm)
                regime     : this repository at HEAD
WORLDS          A AGREE: admitted rank above rejected in every source -> the ledger's verdicts and
                  the corpus's scores are consistent.
                B DISAGREE IN SIGN: the framing is the finding; no pooled claim admissible.
KILL            the three disagree in sign -> world B, report the disagreement, never the average.
POSITIVE CTRL   labelling the top scorers as admitted -> percentile 100.
g=0             a random labelling -> ~50th percentile on average.
NEGATIVE CTRL   labelling the bottom scorers as admitted -> percentile ~0.
RESOLUTION      the minimum achievable p is 1/C(n, n_adm), reported per source.
PLACEBO         run twice identical.
ARTIFACT        results/scores_vs_verdicts.json
IMPOSSIBLE      whether two artifacts share an upstream scoring run is not recorded anywhere in this
                corpus; that is what would turn convergence into replication.
"""
from __future__ import annotations
import itertools, json, math, pathlib, random, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
SEED = 20260805


def sources(arms):
    out = {}
    for j in ROOT.rglob("results/*.json"):
        if "/.git/" in str(j): continue
        try: d = json.loads(j.read_text())
        except Exception: continue
        def walk(o, path=""):
            if isinstance(o, dict):
                for k, v in o.items():
                    p = f"{path}.{k}" if path else k
                    if isinstance(v, dict) and "a2" in k.lower():
                        vals = {a: x for a, x in v.items()
                                if a in arms and isinstance(x, (int, float))}
                        if len(vals) >= 4:
                            out[f"{j.parent.parent.name.split('_')[0]}:{p}"] = vals
                    if isinstance(v, (dict, list)): walk(v, p)
            elif isinstance(o, list):
                for v in o[:20]:
                    if isinstance(v, (dict, list)): walk(v, path)
        walk(d)
    return out


def pct_and_p(vals, admitted):
    """mean rank of `admitted`, against the EXACT null over all labellings of that size."""
    names = sorted(vals, key=lambda a: vals[a])          # ascending: rank 1 = lowest a2
    rank = {a: i + 1 for i, a in enumerate(names)}
    n, m = len(names), len(admitted)
    obs = sum(rank[a] for a in admitted) / m
    null = [sum(rank[a] for a in c) / m for c in itertools.combinations(names, m)]
    pct = sum(x <= obs for x in null) / len(null)
    p = min(1.0, 2 * min(sum(x <= obs for x in null), sum(x >= obs for x in null)) / len(null))
    return obs, pct, p, len(null), 1 / math.comb(n, m)


def main() -> int:
    led = json.loads(next(ARC.glob("R360_*/results/*.json")).read_text())
    arms, pass2 = set(led["arms"]), set(led["clause2_admits"])
    srcs = {s: v for s, v in sources(arms).items()
            if 2 <= len(set(v) & pass2) <= len(v) - 2}
    if len(srcs) < 2:
        print(f"UNRUNNABLE: {len(srcs)} runnable sources. Exit 2, never 0."); return 2

    print("─── CONTROLS (per source; a rank test is an instrument) ───")
    s0, v0 = next(iter(srcs.items()))
    order = sorted(v0, key=lambda a: v0[a])
    m = len(set(v0) & pass2)
    _, pct_top, _, _, floor0 = pct_and_p(v0, order[-m:])
    _, pct_bot, _, _, _ = pct_and_p(v0, order[:m])
    rng = random.Random(SEED)
    rnd = [pct_and_p(v0, rng.sample(order, m))[1] for _ in range(200)]
    print(f"  POSITIVE  top scorers labelled admitted -> percentile {pct_top*100:.0f} -> "
          f"{'PASS' if pct_top > 0.95 else '⛔ FAIL'}")
    print(f"  NEGATIVE  bottom scorers labelled admitted -> percentile {pct_bot*100:.0f} -> "
          f"{'PASS' if pct_bot < 0.05 else '⛔ FAIL'}")
    g0 = sum(rnd) / len(rnd)
    print(f"  g=0       random labellings average percentile {g0*100:.0f} -> "
          f"{'PASS — the statistic returns both ends' if 0.35 < g0 < 0.65 else '⛔ FAIL'}")
    plc = pct_and_p(v0, order[-m:])[1] == pct_top
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = pct_top > 0.95 and pct_bot < 0.05 and 0.35 < g0 < 0.65 and plc

    print(f"\n─── THE SPECIFICATION CURVE (G3/G4 — every source, none pooled) ───")
    rows = []
    for s, vals in sorted(srcs.items()):
        adm = sorted(set(vals) & pass2)
        obs, pct, p, ncells, floor = pct_and_p(vals, adm)
        res = p < 0.05
        rows.append({"source": s, "n": len(vals), "n_adm": len(adm), "admitted": adm,
                     "mean_rank": obs, "percentile": pct, "p": p, "null_cells": ncells,
                     "resolution_floor": floor, "resolved": res, "above_half": pct > 0.5})
        print(f"  {s[:44]:<46} n={len(vals):<3} adm={len(adm)}  "
              f"mean rank {obs:.2f}  percentile {pct*100:5.1f}%  p={p:.4f}  "
              f"{'RESOLVED' if res else 'not resolved'}")
        print(f"  {'':46} exact null {ncells} cells; resolution floor p={floor:.4f} "
              f"{'(cannot reach 0.05 — a non-resolution here is meaningless)' if floor > 0.05 else ''}")
    mean_pct = sum(r["percentile"] for r in rows) / len(rows)
    n_res = sum(r["resolved"] for r in rows)
    signs = {r["above_half"] for r in rows}
    killed = len(signs) > 1

    print(f"\n  mean percentile across sources : {mean_pct*100:.1f}")
    print(f"  registered A 85 [40,100] -> {mean_pct*100:.1f}: "
          f"{'INSIDE' if 40 <= mean_pct*100 <= 100 else '⛔ OUTSIDE'}, error {mean_pct*100-85:+.1f}")
    print(f"  registered B 1 of 3 resolve -> {n_res} of {len(rows)}: error {n_res-1:+d}")
    print(f"  DIRECTIONAL all sources agree in sign -> {'HOLDS' if not killed else '⛔ FAILS'}")
    print(f"  pre-registered kill (sources disagree in sign) -> "
          f"{'⭐ FIRES — the framing is the finding, no pooled claim' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = (f"⭐⭐⭐ B DISAGREE IN SIGN — the sources do not agree on whether ②-admitted arms "
                 f"score higher. Per §2.5 the FRAMING is the finding and no pooled claim is "
                 f"admissible; the disagreement is reported, never the average.")
    else:
        saturated = all(r["percentile"] >= 0.999 for r in rows)
        world = (f"⛔⛔⛔ THE AGREEMENT IS FORCED, AND THE SATURATED STATISTIC IS THE TELL. "
                 f"R360's `run.py` computes `clause2_admits` FROM `a2_vec` -- ② IS AN A2 THRESHOLD. "
                 f"So ②-admitted arms scoring above ②-rejected ones is an ARITHMETIC CONSEQUENCE "
                 f"wherever the a2 values come from the same scoring run, and this corpus records "
                 f"nothing about which run any artifact's a2 came from. "
                 f"{'⭐ ALL THREE SOURCES RETURNED PERCENTILE 100.0 -- the CEILING of the statistic, ' if saturated else ''}"
                 f"which is exactly what a threshold predicts and is why the result should have been "
                 f"suspected before it was interpreted. ⚠ SO THIS IS A DERIVATION IF THE RUNS ARE "
                 f"SHARED AND A CONSISTENCY CHECK IF THEY ARE NOT, AND THE CORPUS CANNOT SAY WHICH. "
                 f"The numbers below stand as computed and are NOT evidence that the ledger was "
                 f"independently confirmed. ⚠ What WOULD separate them: an a2 produced by a scoring "
                 f"run recorded as distinct from R360's -- and R684 measured that 90 of this arc's "
                 f"rounds vary a judge while 9 record which. "
                 f"⚠ ORIGINAL (RETRACTED) READING: in all {len(rows)} sources the ②-admitted arms "
                 f"rank ABOVE the rejected, mean percentile {mean_pct*100:.1f}, with {n_res} of "
                 f"{len(rows)} resolving at p<0.05 against their own exact nulls. ⭐ So the corpus's "
                 f"a2 SCORES and R360's ② VERDICTS are consistent, which is a precondition for every "
                 f"claim this arc has built on that ledger and had never been checked. ⚠ AND IT IS "
                 f"CONVERGENCE, NOT REPLICATION: three artifacts may share an upstream scoring run, "
                 f"and this corpus records nothing about which. ⚠ Resolution floors are reported per "
                 f"source, because a source whose minimum p exceeds 0.05 cannot fail to 'not "
                 f"resolve'.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(rows)} sources × exact enumeration, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}   seed: {SEED}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"scores_vs_verdicts.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "seed": SEED,
        "rows": rows, "mean_percentile": mean_pct, "n_resolved": n_res,
        "kill_fired": killed, "directional_holds": not killed,
        "FORCED": ("R360 computes clause2_admits from a2_vec -- clause 2 IS an A2 threshold. The "
                   "agreement is an arithmetic consequence if the a2 values share R360's scoring "
                   "run; the corpus does not record which run any a2 came from. Percentile 100.0 "
                   "in every source is the ceiling of the statistic and the tell."),
        "registered": "A 85 [40,100]; B 1 of 3 resolve; all agree in sign; kill on sign disagreement",
        "limit": ("convergence across three artifacts is not independent replication; a shared "
                  "upstream scoring run is not recorded anywhere in this corpus."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'scores_vs_verdicts.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
