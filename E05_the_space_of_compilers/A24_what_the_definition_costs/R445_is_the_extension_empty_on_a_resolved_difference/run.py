"""R445 -- the extension is ONE arm because `gen` fails ②. Is that failure RESOLVED?

⛔ THE ANNOUNCED STEP'S PREMISE WAS FALSE, AND THE COUNT TOOK ONE COMMAND. R444 closed with "the
   generated core R433 built is the only object in this whole campaign that was not built by
   select_core.py from one rubric" -- a quantifier over my own work, which this standard names as
   the exact tell. **`gen` and `gen_sham` are home-release cores generated from the conversation
   alone, and both have been in R360's 42-arm space the whole time.** Thirteenth announced step
   checked; its premise was wrong, not merely its necessity.

⭐ AND THE CHECK FOUND SOMETHING SHARPER THAN THE STEP IT KILLED. ③-corrected does NOT exclude
   `gen` -- `select_core.py` never built it, so its selector is UNKNOWN and R444's clause returns it
   unexcluded. **② excludes it.** So the definition's extension is one arm NOT because no
   third-source object exists, but because **the one that exists fails clause ②** -- and ② is the
   clause whose whole purpose is to admit things producible from the conversation alone.

   The raw gap is `gen 0.5374` against ②'s published reference `POOL[0:4] 0.5537` = **-0.0162**.
   R436's MDE for `gen` was **0.0232**, but against a DIFFERENT baseline. **If -0.0162 sits inside
   its own paired floor, the definition's extension is one arm on a difference it cannot resolve.**

ESTIMAND (named before the method)
    DELTA = A2(gen) - A2(POOL[0:4]), paired per prompt over the home release, where POOL[0:4] is
            clause ②'s published reference -- the size-matched set that never read the conversation.
    and the question is whether |DELTA| exceeds its own MDE.

IDENTIFICATION
    Fully identified: both arms are scored on the same prompts by the same judge, and the comparison
    is paired per prompt with the annotator draw held common. What is NOT identified: whether ②'s
    reference SHOULD be `POOL[0:4]` -- R331 measured it at the 93.7th percentile of 1,820 subsets,
    chosen by FILE ORDER, and that is a separate defect this round does not re-open.

SCOPE  population : home-release prompts with a ranking and a score for both arms
       instrument : the committed judge J = Qwen3.5-2B-Base, k=4
       baseline   : `POOL[0:4]`, clause ②'s own published reference
       regime     : A2 over 6 pairs, 3 annotator draws per prompt

WORLDS
    W-RESOLVED    |DELTA| > MDE -> `gen` genuinely fails ②, the extension of one arm rests on a
                  difference the design can see, and the definition's emptiness is a finding about
                  generated cores rather than about the threshold.
    W-UNRESOLVED  |DELTA| <= MDE -> the definition excludes the ONE third-source object it has on a
                  difference it cannot resolve. The extension's size is then an artifact of where a
                  boundary was drawn, not of what was measured, and "the extension is one arm" must
                  be restated as "one arm, and the exclusion of the second is unresolved".
    W-BEATS       DELTA > +MDE -> `gen` actually SATISFIES ② and the committed admit list is wrong,
                  which would be a defect in R360 rather than in the definition.

PREDICTION MATRIX
                    |DELTA| > MDE, negative   inside the floor   positive and resolved
    W-RESOLVED               0.9                    0.05                 0.02
    W-UNRESOLVED             0.05                   0.9                  0.02
    W-BEATS                  0.02                   0.05                 0.95

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    DELTA < -MDE   -> W-RESOLVED
    |DELTA| <= MDE -> W-UNRESOLVED; DEFINITION.md owes the restatement
    DELTA > +MDE   -> W-BEATS; R360's admit list is wrong and that is its own round
    a control fails -> UNVERIFIED

CONTROLS
    POSITIVE   an ORACLE ordering against `POOL[0:4]` must be resolvedly ABOVE it. A paired test
               that cannot separate a perfect arm from the reference cannot make any null mean
               anything.
    g=0        `POOL[0:4]` against ITSELF must give exactly 0 with a non-degenerate MDE -- if the
               MDE collapses to 0 the statistic is degenerate and no threshold is admissible.
    NEGATIVE   `gen_sham` -- the same generator on the wrong prompt -- must fail ② by MORE than
               `gen` does. If the sham is not worse, the comparison is not measuring the arm.
    PLACEBO    the annotator draw is held COMMON across the two arms; drawing independently would
               add a difference that is not the arms'.
    SEEDS      3 annotator draws; the across-draw spread is reported beside DELTA.

MULTIPLICITY  3 arms x 1 comparison = 3 cells, all reported; no selection.
ARTIFACT      results/r445_gen_vs_clause2.json
IMPOSSIBLE HERE, NAMED
    * whether `POOL[0:4]` is the RIGHT reference -- R331's defect, not re-opened here.
    * construct validity of A2 -- the release's own human rankings.
    * generalising to generated cores this campaign did not build -- one generator, one decode.

EXIT 0 W-RESOLVED · 1 W-UNRESOLVED · 2 W-BEATS or UNVERIFIED
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
ZEFF = 1.959964 + 0.841621
L = "ABCD"


def stable(pid: str) -> int:
    return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R445 · the extension is ONE arm because `gen` fails ②. Is that failure RESOLVED?\n")
    print("  ⛔ R444's closing line said the R433 core was 'the only object not built by")
    print("     select_core.py'. `gen` and `gen_sham` are home-release generated cores and have")
    print("     been in the 42-arm space the whole time. Thirteenth announced step checked; its")
    print("     PREMISE was false, not merely its necessity.\n")

    targets, _ = SC.load_targets()
    pool = SC.load_sat(SATD / "sat_genericpool16.npz")
    arms = {}
    for nm in ("gen", "gen_sham", "coval_core"):
        p = SATD / f"sat_{nm}.npz"
        if p.exists():
            arms[nm] = SC.load_sat(p)
    if "gen" not in arms:
        print("  UNRUNNABLE: sat_gen.npz absent. Exit 2, never 0."); return 2

    pids = sorted(set(pool) & set(targets) & set(arms["gen"]))
    print(f"  prompts with a ranking, a pool score and a `gen` score: {len(pids)}")
    if len(pids) < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    SEEDS = (0, 1, 2)

    def hy_of(p):
        v = targets[p]
        return [np.array(v[int(np.random.default_rng(1000 * s + stable(p)).integers(len(v)))][0],
                         float) for s in SEEDS]

    HY = {p: hy_of(p) for p in pids}

    def a2(y, p):
        c = SC.cls(y)
        return float(np.mean([np.mean([x == z for x, z in zip(c, SC.cls(h))]) for h in HY[p]]))

    def ref_y(p):
        m = np.zeros((16, 4))
        for (i, ltr), v in pool[p].items():
            m[i, L.index(ltr)] = v
        return m[[0, 1, 2, 3]].sum(axis=0)

    def arm_y(nm, p):
        s = arms[nm].get(p)
        if not s:
            return None
        idxs = sorted({i for i, _ in s})
        return SC.yvec(s, idxs)

    def paired(nm):
        ks = [p for p in pids if arm_y(nm, p) is not None]
        d = np.array([a2(arm_y(nm, p), p) - a2(ref_y(p), p) for p in ks])
        bs = []
        for sd in (71, 72, 73):
            r = np.random.default_rng(sd)
            for _ in range(400):
                bs.append(float(d[r.choice(len(d), len(d), replace=True)].mean()))
        bs = np.array(bs)
        return float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), \
            float(ZEFF * bs.std()), len(ks)

    # ------------------------------------------------------------------------------- controls
    ok = True
    d_or = np.array([a2(HY[p][0], p) - a2(ref_y(p), p) for p in pids])
    bs = []
    for sd in (71, 72, 73):
        r = np.random.default_rng(sd)
        for _ in range(400):
            bs.append(float(d_or[r.choice(len(d_or), len(d_or), replace=True)].mean()))
    or_mde = float(ZEFF * np.std(bs))
    pos = d_or.mean() > or_mde
    ok &= pos
    print(f"\n  POSITIVE  an ORACLE ordering vs POOL[0:4] -> {d_or.mean():+.4f} vs MDE {or_mde:.4f}"
          f"   {'PASS' if pos else '⛔ FAIL — the test cannot separate a perfect arm'}")

    d_self = np.array([a2(ref_y(p), p) - a2(ref_y(p), p) for p in pids])
    bs2 = []
    for sd in (71, 72, 73):
        r = np.random.default_rng(sd)
        for _ in range(200):
            bs2.append(float(d_self[r.choice(len(d_self), len(d_self), replace=True)].mean()))
    g0 = (d_self.mean() == 0.0)
    ok &= g0
    print(f"  g=0       POOL[0:4] against itself -> {d_self.mean():.1e}, must be exactly 0   "
          f"{'PASS' if g0 else '⛔ FAIL'}")

    print(f"  PLACEBO   the annotator draw is held COMMON across both arms of every comparison")
    print(f"            (same {len(SEEDS)} seeds, same prompt-keyed rng) — drawing independently")
    print(f"            would add a difference that is not the arms'.")

    cells = {}
    for nm in [n for n in ("gen", "gen_sham", "coval_core") if n in arms]:
        cells[nm] = paired(nm)
    if "gen_sham" in cells:
        neg = cells["gen_sham"][0] < cells["gen"][0]
        ok &= neg
        print(f"  NEGATIVE  `gen_sham` must fail ② by MORE than `gen`: "
              f"{cells['gen_sham'][0]:+.4f} < {cells['gen'][0]:+.4f}   "
              f"{'PASS' if neg else '⛔ FAIL — the comparison is not measuring the arm'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r445_gen_vs_clause2.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ------------------------------------------------------------------------------ the estimand
    print(f"\n  {'arm':<12}{'DELTA vs ②ref':>15}{'95% CI':>22}{'MDE':>9}{'':>12}")
    for nm, (pt, lo, hi, mde, n) in cells.items():
        verdict = ("RESOLVED below" if pt < -mde else
                   "RESOLVED above" if pt > mde else "INSIDE THE FLOOR")
        print(f"  {nm:<12}{pt:>+15.4f}  [{lo:+.4f},{hi:+.4f}]{mde:>9.4f}   {verdict}")

    DELTA, _lo, _hi, MDE, N = cells["gen"]
    world = ("W-BEATS" if DELTA > MDE else
             "W-RESOLVED" if DELTA < -MDE else "W-UNRESOLVED")
    print(f"\n  WORLD: {world}")
    if world == "W-UNRESOLVED":
        print(f"    ⛔ the definition excludes the ONE third-source object it has on a difference")
        print(f"    it CANNOT RESOLVE: {DELTA:+.4f} against an MDE of {MDE:.4f}. The extension's")
        print(f"    size is then an artifact of where a boundary was drawn, not of what was")
        print(f"    measured, and 'the extension is one arm' must be restated as **one arm, and")
        print(f"    the exclusion of the second is unresolved**.")
        print(f"    ⚠ This does NOT say `gen` is a core. It says the definition cannot currently")
        print(f"    tell, and a definition that cannot tell should say so rather than exclude.")
    elif world == "W-RESOLVED":
        print(f"    `gen` genuinely fails ② at {DELTA:+.4f} vs MDE {MDE:.4f}. The extension of one")
        print(f"    arm rests on a difference the design can see, and the emptiness is a finding")
        print(f"    about generated cores rather than about the threshold.")
    else:
        print(f"    `gen` SATISFIES ② at {DELTA:+.4f} vs MDE {MDE:.4f} — R360's committed admit")
        print(f"    list is wrong, which is a defect in that round and gets its own.")

    (RES / "r445_gen_vs_clause2.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "n_prompts": N, "seeds": list(SEEDS),
         "oracle_delta": float(d_or.mean()), "oracle_mde": or_mde,
         "cells": {k: {"delta": v[0], "lo": v[1], "hi": v[2], "mde": v[3], "n": v[4]}
                   for k, v in cells.items()}}, indent=1))
    print(f"\n  artifact -> {(RES / 'r445_gen_vs_clause2.json').relative_to(ROOT)}")
    return 0 if world == "W-RESOLVED" else (1 if world == "W-UNRESOLVED" else 2)


if __name__ == "__main__":
    sys.exit(main())
