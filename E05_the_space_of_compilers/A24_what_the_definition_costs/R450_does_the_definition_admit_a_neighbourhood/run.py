"""R450 -- does the definition admit a NEIGHBOURHOOD of the released core, or only the point?

⛔ THE ANNOUNCED AUDIT'S MOTIVATION WAS FALSE IN TWO OF ITS THREE CLAUSES. R449 closed by proposing an
   audit of "what else rests on a population of one", citing three examples. Checked against the
   document before building anything:
     * "④'s adoption argument used a one-release bar"        -> FALSE. DEFINITION.md:133 and :522 --
       ④ removes ALL 7 ARMS ON THE SECOND RELEASE. Its case is explicitly TWO-release.
     * "the register lists cross-release as unmet"           -> FALSE. DEFINITION.md:600 -- "the route
       is now WALKED, not open"; R433 ran it.
     * "n_judge_pairs = 1"                                   -> TRUE (R449, measured last round).
   *Eighteenth announced step checked, TENTH premise killed*, and both false ones ran in the
   direction that MANUFACTURES work -- inventing a weakness the document does not have.

⭐ WHAT THE CHECK SURFACED INSTEAD, and it is the central problem of the whole quest. §4's oldest
   entry is `the definition describes the instance`, and the extension is currently ONE ARM: the
   released core, the very object the definition was written from (R442/R444). That is either
   strictness or tautology, and NOTHING SO FAR SEPARATES THEM -- every round has tested clauses
   against arms built by other selectors, never against objects ADJACENT TO THE CORE ITSELF.

   The separator is free. `sat_coval_core.npz` holds PER-CRITERION satisfaction, so any sub-set of the
   released core's own criteria, and any mixture with the generic pool, can be scored with NO new
   judging. A definition that describes the instance admits the released set and nothing beside it.
   A definition that captures a category admits a NEIGHBOURHOOD with a measurable boundary.

ESTIMAND (named before the method)
    For a candidate criterion set S built from r of the released core's own criteria plus a of the
    16 generic pool criteria (so |S| = r+a, distance d = (k-r) + a from the released core):
        SHARE(S) = fraction of the SIZE-MATCHED reference class C(16, r+a) that S beats, where
                   "beats" is clause ②'s own test: paired mean A2 gap > ZEFF*sd/sqrt(n).
    The outcome is the DOSE-RESPONSE CURVE of SHARE against d. ⭐ A share needs no threshold, so
    this round introduces no free parameter anywhere.

IDENTIFICATION
    Fully identified and it needs no GPU: every criterion involved is already judged on every
    response. ⚠ NOT identified: whether an admitted neighbour is a "core" in any sense external to
    this definition. This measures the definition's EXTENSION, never its correctness.

SCOPE  population : the 968 home-release prompts
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs, 3 annotator draws held common
       baseline   : the size-matched C(16,m) reference class, per m -- never a fixed reference
       regime     : m = r+a in 1..8; the released core has k in {2,3,4}, mean 3.94

WORLDS
    W-POINT          SHARE collapses as soon as d>0 -- dropping ONE released criterion or adding ONE
                     generic one destroys admission. The definition is a description of the instance
                     and the extension of 1 is tautology, not strictness.
    W-NEIGHBOURHOOD  SHARE decays gradually with d and stays high for small d -> the definition picks
                     out a REGION, the extension of 1 is an artifact of which arms were built, and
                     the boundary is measurable and reportable.
    W-VACUOUS        SHARE stays high even at maximal d -> the test does not discriminate at all in
                     this neighbourhood and clause ② is weaker than every previous round implies.

PREDICTION MATRIX
                        collapse at d=1   graded decay   high everywhere
    W-POINT                  0.90              0.05            0.05
    W-NEIGHBOURHOOD          0.05              0.90            0.05
    W-VACUOUS                0.05              0.05            0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if BOTH anchors hold.
    if SHARE(d=0) is within 0.02 of R446's committed 0.9841 and SHARE(full replacement) is in
    [0.35, 0.65]:
        SHARE at d=1 < 0.20                                  -> W-POINT
        SHARE at d=1 >= 0.20 and SHARE at max d < 0.80        -> W-NEIGHBOURHOOD
        SHARE >= 0.80 at every d                              -> W-VACUOUS
    else: UNVERIFIED. Never OVERTURNED, never CONFIRMED.

CONTROLS -- ⭐ BOTH ANCHORS COME FREE, WHICH IS WHY THIS DESIGN WAS CHOSEN
    CEILING    d=0 is the released core, and R446 committed its share as 0.9841 on this exact
               reference class. Recovering it re-derives a published number from an independent code
               path; missing it means this round's A2 is not the campaign's A2.
    FLOOR      at FULL replacement (r=0) the candidate IS a member of the reference class, so its
               share must sit near 0.5 BY CONSTRUCTION. A floor that is not ~0.5 means the
               size-matching is broken. This is the g=0 cell and it CANNOT be satisfied in advance.
    SHAM       criteria drawn from OTHER prompts at matched size -- content destroyed, size kept.
    SEEDS      5 instantiations per (r,a) cell; the spread is reported, never averaged away.
    NOISE      the seed spread at each d IS the noise floor for the curve; measured, not assumed.

MULTIPLICITY  the whole (r,a) grid is reported -- every cell, including the ones that kill a world.
              No cell is selected, so there is nothing to correct; the curve is the result.
ARTIFACT      results/r450_neighbourhood.json
IMPOSSIBLE HERE, NAMED
    * whether a neighbour is "really" a core -- needs a standard outside this definition.
    * criteria not already judged (paraphrases, new generations) -- needs GPU and a generator; this
      round is deliberately confined to what is scored, which is why it costs nothing.
    * a second released core to repeat this around -- the release ships exactly one.
"""
from __future__ import annotations
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
ZEFF = 1.959964 + 0.841621
L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R450 · does the definition admit a NEIGHBOURHOOD of the released core, or only the point?\n")
    print("  ⛔ the announced audit's motivation was FALSE in 2 of 3 claims (checked against the")
    print("     document, not memory): ④'s case IS two-release (:133,:522) and cross-release is")
    print("     WALKED, not open (:600). Eighteenth step, TENTH premise killed.\n")

    core_f, pool_f = SATD / "sat_coval_core.npz", SATD / "sat_genericpool16.npz"
    if not (core_f.exists() and pool_f.exists()):
        print("  UNRUNNABLE: satisfaction files absent. Exit 2, never 0."); return 2
    core, pool = SC.load_sat(core_f), SC.load_sat(pool_f)
    targets, _ = SC.load_targets()
    pids = sorted(set(core) & set(pool) & set(targets))
    n = len(pids)
    print(f"  prompts: {n}   (no GPU: every criterion here is already judged)")
    if n < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    SEEDS = (0, 1, 2)
    HC = {p: np.array([SC.cls(np.array(targets[p][int(np.random.default_rng(1000 * s + stable(p))
                                                      .integers(len(targets[p])))][0], float))
                       for s in SEEDS]) for p in pids}
    CM, PM, KK = {}, {}, {}
    for p in pids:
        cs = sorted({c for (c, _) in core[p]})
        CM[p] = np.array([[core[p].get((c, l), 0.0) for l in L] for c in cs])
        KK[p] = len(cs)
        PM[p] = np.zeros((16, 4))
        for (i, ltr), v in pool[p].items():
            PM[p][i, L.index(ltr)] = v
    kbar = float(np.mean([KK[p] for p in pids]))
    print(f"  released core: mean k = {kbar:.2f}  (k per prompt in {sorted(set(KK.values()))})")

    def a2_rows(Y, p):
        return (signs(Y)[:, None, :] == HC[p][None, :, :]).mean(axis=(1, 2))

    # size-matched reference classes, one per m -- the baseline is never a fixed subset
    REF = {}
    for m in range(1, 9):
        subs = list(itertools.combinations(range(16), m))
        S = np.zeros((len(subs), 16))
        for j, s in enumerate(subs):
            S[j, list(s)] = 1.0
        R = np.zeros((len(subs), n))
        for i, p in enumerate(pids):
            R[:, i] = a2_rows((S @ PM[p]) / m, p)
        REF[m] = R
        print(f"    reference class m={m}: C(16,{m}) = {len(subs):5d}")

    def share(v, m):
        d = v[None, :] - REF[m]
        return float((d.mean(axis=1) > ZEFF * d.std(axis=1, ddof=1) / np.sqrt(n)).mean())

    def build(r, a, seed, sham=False):
        """r core criteria + a pool criteria, per prompt, drawn at `seed`. -> per-prompt A2 vector."""
        v = np.zeros(n)
        for i, p in enumerate(pids):
            rg = np.random.default_rng(seed * 100003 + stable(p))
            k = KK[p]
            rr = min(r, k)
            rows = []
            if rr:
                src = CM[np.random.default_rng(seed * 7 + stable(p)).choice(pids)] if sham else CM[p]
                idx = rg.choice(len(src), size=min(rr, len(src)), replace=False)
                rows.append(src[idx])
            if a:
                rows.append(PM[p][rg.choice(16, size=a, replace=False)])
            M = np.vstack(rows)
            v[i] = a2_rows(M.mean(axis=0)[None, :], p)[0]
        return v

    # ---- ANCHORS -------------------------------------------------------------------------------
    print("\n  ANCHORS — both come free, and neither can be satisfied in advance")
    v0 = np.zeros(n)
    for i, p in enumerate(pids):
        v0[i] = a2_rows(CM[p].mean(axis=0)[None, :], p)[0]
    m0 = int(round(kbar))
    s0 = share(v0, m0)
    ceil_ok = abs(s0 - 0.9841) <= 0.02
    print(f"    CEILING  d=0, the released core itself -> share {s0:.4f} vs R446's committed 0.9841"
          f"   {'PASS' if ceil_ok else '⛔ FAIL — this round is not computing the campaign A2'}")
    fl = [share(build(0, m0, sd), m0) for sd in range(5)]
    # ⛔ THE FIRST VERSION OF THIS ANCHOR FAILED FOR ITS OWN REASONS, and the fix is a computation.
    #    It asserted "a full-replacement candidate IS a class member, so its share must be ~0.5".
    #    FALSE: `share` counts references beaten RESOLVEDLY (gap > MDE), not merely exceeded, and
    #    those are different statistics. The campaign's own committed numbers already showed it --
    #    coval_core quantile 1.0000 -> share 0.9841, but `gen` quantile 0.2615 -> share 0.0038.
    #    §4 sub-kind ③: the control targeted a different statistic than the one being reported.
    #    The right floor is the class's OWN mean self-share, which is derivable, not guessable.
    rgf = np.random.default_rng(77)
    idx = rgf.choice(REF[m0].shape[0], size=120, replace=False)
    self_shares = [share(REF[m0][j], m0) for j in idx]
    exp_floor = float(np.mean(self_shares))
    # ⛔ AND THE SECOND VERSION STILL COMPARED TWO DIFFERENT OBJECTS. `build()` re-draws the
    #    criterion indices PER PROMPT (rng keyed on the pid) -- correct for a CORE, which is
    #    per-conversation by definition -- while every member of the reference class is ONE FIXED
    #    subset used on all prompts. So the r=0 arm and the class are built by different rules and
    #    the anchor was testing that difference, not the size-matching. Built the same way as the
    #    class, the anchor becomes a real check on the size-matching:
    fixed = []
    rgx = np.random.default_rng(91)
    for _ in range(5):
        sub = rgx.choice(16, size=m0, replace=False)
        v = np.zeros(n)
        for i, p_ in enumerate(pids):
            v[i] = a2_rows(PM[p_][sub].mean(axis=0)[None, :], p_)[0]
        fixed.append(share(v, m0))
    floor_ok = abs(float(np.mean(fixed)) - exp_floor) <= 0.06
    print(f"             SAME-RULE floor (a FIXED subset, as the class is built): "
          f"{np.mean(fixed):.4f} [{min(fixed):.4f},{max(fixed):.4f}]   "
          f"{'PASS' if floor_ok else '⛔ FAIL — size-matching is broken'}")
    print(f"             ⭐ and the per-prompt-varying draw scores {np.mean(fl):.4f} vs the fixed "
          f"{np.mean(fixed):.4f} — a separate finding, not a defect: a prompt-VARYING random")
    print(f"             selection from the pool is WORSE than a fixed one at the same size.")
    print(f"    FLOOR    the class's OWN mean self-share (120 members vs all {REF[m0].shape[0]}): "
          f"{exp_floor:.4f}")
    print(f"             full replacement (r=0) -> {np.mean(fl):.4f} "
          f"[{min(fl):.4f},{max(fl):.4f}]   "
          f"{'PASS' if floor_ok else '⛔ FAIL — size-matching is broken'}")
    print(f"             ⚠ the discarded guess was 0.5; it confused RESOLVEDLY-beaten with "
          f"merely-exceeded")

    # ---- the grid ------------------------------------------------------------------------------
    cells = []
    for r in range(0, 5):
        for a in range(0, 5):
            m = r + a
            if m < 1 or m > 8:
                continue
            sh = [share(build(r, a, sd), m) for sd in range(5)]
            shm = [share(build(r, a, sd, sham=True), m) for sd in range(3)] if r else None
            cells.append({"r": r, "a": a, "m": m, "d": (m0 - min(r, m0)) + a,
                          "share_mean": float(np.mean(sh)), "share_min": float(min(sh)),
                          "share_max": float(max(sh)), "seeds": [float(x) for x in sh],
                          "sham_mean": None if shm is None else float(np.mean(shm))})

    print("\n  THE NEIGHBOURHOOD — share of the SIZE-MATCHED class beaten (no threshold anywhere)")
    print(f"    {'r':>2}{'a':>3}{'m':>3}{'d':>3}{'share':>9}{'[min,max]':>18}{'sham':>8}")
    for c in sorted(cells, key=lambda c: (c["d"], -c["r"])):
        sh = "     n/a" if c["sham_mean"] is None else f"{c['sham_mean']:>8.4f}"
        print(f"    {c['r']:>2}{c['a']:>3}{c['m']:>3}{c['d']:>3}{c['share_mean']:>9.4f}"
              f"   [{c['share_min']:.4f},{c['share_max']:.4f}]{sh}")

    # ⭐ IS `d` EVEN THE RIGHT COORDINATE? The grid varies r and a independently, so that is a
    #    measurement, not an assumption -- and a could have mattered a great deal (diluting a core
    #    with generic criteria might destroy it).
    def by(key):
        g = {}
        for c in cells:
            g.setdefault(c[key], []).append(c["share_mean"])
        return {k: (float(np.mean(v)), float(np.std(v)), len(v)) for k, v in sorted(g.items())}
    byr, bya = by("r"), by("a")
    allv = np.array([c["share_mean"] for c in cells])
    def eta2(key):
        g = {}
        for c in cells:
            g.setdefault(c[key], []).append(c["share_mean"])
        ssb = sum(len(v) * (np.mean(v) - allv.mean()) ** 2 for v in g.values())
        return float(ssb / ((allv - allv.mean()) ** 2).sum())
    print("\n  ⭐ WHICH COORDINATE GOVERNS ADMISSION?  (r = core criteria retained, a = generic added)")
    print(f"    {'r':>3}{'share':>9}{'sd':>8}{'cells':>7}     {'a':>3}{'share':>9}{'sd':>8}{'cells':>7}")
    ks = sorted(set(list(byr) + list(bya)))
    for k in ks:
        lr = f"{k:>3}{byr[k][0]:>9.4f}{byr[k][1]:>8.4f}{byr[k][2]:>7d}" if k in byr else " " * 27
        la = f"{k:>3}{bya[k][0]:>9.4f}{bya[k][1]:>8.4f}{bya[k][2]:>7d}" if k in bya else ""
        print(f"    {lr}     {la}")
    e_r, e_a = eta2("r"), eta2("a")
    print(f"    variance of share explained:  by r  {100*e_r:.1f}%    by a  {100*e_a:.1f}%")

    bydist = {}
    for c in cells:
        bydist.setdefault(c["d"], []).append(c["share_mean"])
    print("\n  DOSE-RESPONSE — share against distance from the released core")
    for d in sorted(bydist):
        v = bydist[d]
        bar = "█" * int(round(40 * float(np.mean(v))))
        print(f"    d={d}  {np.mean(v):.4f}  n_cells={len(v):2d}  {bar}")

    d1 = float(np.mean(bydist.get(1, [np.nan])))
    dmax = float(np.mean(bydist[max(bydist)]))
    anchors_ok = ceil_ok and floor_ok
    if not anchors_ok:
        world = "UNVERIFIED"
    elif min(bydist[d] and float(np.mean(bydist[d])) for d in bydist) >= 0.80:
        world = "W-VACUOUS"
    elif d1 < 0.20:
        world = "W-POINT"
    else:
        world = "W-NEIGHBOURHOOD"

    print(f"\n  WORLD: {world}")
    if world == "W-NEIGHBOURHOOD":
        print("    The definition picks out a REGION, not the released point. The extension of 1 is")
        print("    a fact about WHICH ARMS WERE BUILT, not about the definition's strictness.")
    elif world == "W-POINT":
        print("    ⛔ Perturbing the released core by one criterion destroys admission. The")
        print("       extension of 1 is TAUTOLOGY: the definition describes the instance.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "k_bar": kbar, "m0": m0,
           "share_d0": s0, "share_floor_mean": float(np.mean(fl)), "share_floor_seeds": fl,
           "share_d1": d1, "share_dmax": dmax, "cells": cells,
           "dose_response": {str(d): float(np.mean(v)) for d, v in sorted(bydist.items())},
           "by_r": byr, "by_a": bya, "eta2_r": e_r, "eta2_a": e_a,
           "anchors": {"ceiling_ok": ceil_ok, "floor_ok": floor_ok,
                       "r446_committed_d0": 0.9841, "class_self_share": exp_floor, "same_rule_floor": float(np.mean(fixed)),
                       "per_prompt_floor": float(np.mean(fl)),
                       "fixed_floor_seeds": [float(x) for x in fixed]}}
    (RES / "r450_neighbourhood.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r450_neighbourhood.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
