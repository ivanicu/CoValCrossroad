"""R368 — R233 declined its own verdict and named the fix. The data is cached. This runs the fix.

R233 ran the candidate-set transport test -- does a compiled core still reproduce the full rubric's
ordering on RESPONSES IT WAS NOT BUILT AGAINST -- and then refused its own result, for a reason it
stated precisely:

    "the arms differ in difficulty, and the floors say so. The random-4 floor is HIGHER on fresh
     (0.4166) than on original (0.4044). Random selection also does better on the fresh responses.
     ... The design conflated `unseen` with `equally hard`. They are different, and the floors
     caught it."

    "What would settle it: match the arms on difficulty rather than assuming it."

**The 33,320 judgements are cached in `sat_fresh_and_orig.npz`, so the fix is a RE-ANALYSIS and
needs no GPU.** That is the whole reason to run it now rather than to have run it then.

⚠ AND WHY IT MATTERS FOR THE DEFINITION, which is the standing question. `DEFINITION.md` mentions
  transport ZERO times. It certifies a core against the four responses it was scored on and says
  nothing about new ones -- so `core` currently names an object that may work only where it was
  measured. Whatever this returns is either a candidate clause or a stated limit, and either is
  worth more than the silence there now.

⛔ ARITHMETIC TRAP, and it is why matching is the whole design. A core's raw agreement is HIGHER on
   the fresh set (0.468 vs 0.352) and so is the RANDOM floor (0.4166 vs 0.4044). The fresh
   responses come from one model at one temperature with one length cap, so they are more
   homogeneous and fewer criteria suffice. Comparing raw agreements across arms is therefore
   measuring the population, not the transport, and the difference-in-differences R233 fell back on
   is clean only if the population effect is ADDITIVE -- which R233 explicitly said nothing here
   establishes. Matching removes the assumption instead of making it.

ESTIMAND        `core − floor` on each arm, computed WITHIN strata of per-prompt difficulty, and the
                transport contrast `(core−floor)_fresh − (core−floor)_orig` pooled over strata with
                the ORIGINAL arm's difficulty distribution as the common weighting. Difficulty is
                the per-prompt spread of the FULL rubric's response scores -- the quantity R233
                identified as the confound, computed from the same cached labels.

IDENTIFICATION  Identified only where the two arms OVERLAP in difficulty; strata occupied by one arm
                alone carry no transport information and are EXCLUDED BY A STATED RULE and counted.
                ⚠ NOT identified, and R233's register entry does not move: the fresh responses carry
                NO HUMAN RANKINGS. This measures transport of the COMPILATION -- agreement with the
                full rubric -- and never agreement with people.

SCOPE           250 prompts · Qwen3.5-2B-Base · `sat_fresh_and_orig.npz`, 33,320 cached judgements ·
                baseline the same-size random draw from the full rubric, recomputed WITHIN each
                stratum so the floor is matched too.

WORLDS
  W-TRANSPORTS    the matched contrast is positive beyond its own MDE: the core reproduces the full
                  rubric's ordering on unseen responses better than a size-matched random draw does,
                  after difficulty is held fixed. Then the definition is MISSING a clause it could
                  carry.
  W-NO-TRANSPORT  the matched contrast is negative beyond its MDE: the core is worse on unseen
                  responses than random is. Then `core` names something that works only where it was
                  measured, and the definition must say so.
  W-UNRESOLVED    the contrast sits inside its MDE. R233's verdict stands as UNVERIFIED for a
                  DIFFERENT and better reason -- not `the arms are incomparable` but `matched, and
                  this release cannot resolve it` -- and the MDE is the number to report.

PREDICTION MATRIX
  W-TRANSPORTS   -> matched contrast > MDE
  W-NO-TRANSPORT -> matched contrast < -MDE
  W-UNRESOLVED   -> |contrast| <= MDE
The three differ on the sign and resolvability of one stratified contrast.

PRE-REGISTERED KILL -- conditional.
    if placebo_ok and floor_ok and overlap_ok:
        if contrast > mde   -> W-TRANSPORTS
        elif contrast < -mde -> W-NO-TRANSPORT
        else                 -> W-UNRESOLVED
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

PLACEBO        `full` against itself on each arm: exactly 1.0. R233 reported this and it is kept.
FLOOR          the size-matched random draw, recomputed INSIDE each stratum over >=3 seeds, so the
               baseline carries the same difficulty as the arm it judges. R233's floors were
               computed on the whole arm, which is what let the population leak in.
OVERLAP CTRL   the two arms must actually share difficulty strata; if they do not, the matched
               estimand is empty and the round says so rather than pooling anyway.
POSITIVE CTRL  a planted core -- the full rubric's own top-k by weight, which reproduces `full` far
               better than random -- must come out resolvably positive on BOTH arms. Without it a
               null here is silence.
MULTIPLICITY   strata x arms; every stratum's n and contrast printed, occupied and excluded alike.
SEEDS          3 on the within-stratum random floor; reported separately.
ARTIFACT       results/r368_matched_transport.json with the source hash.

IMPOSSIBLE HERE
  agreement with PEOPLE on fresh responses -- they carry no human rankings. R233's register entry
                                              stands unmoved and is restated rather than quietly
                                              dropped.
  a second judge                            -- the cache was judged by 2B only.
  cross-release                             -- one release.

EXIT
    0  controls hold and the matched contrast is reported
    1  a control misbehaved -- UNVERIFIED
    2  the cache is missing or the arms share no difficulty stratum -- never a silent pass
"""
from __future__ import annotations
import collections, hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
CACHE = (ROOT / "E05_the_space_of_compilers" / "A18_the_candidate_set_wall_was_wrong"
         / "R233_fresh_candidate_transport" / "results" / "sat_fresh_and_orig.npz")
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
SEEDS = (0, 1, 2)
NSTRATA = 4
METRICS = ("exact", "pair")   # exact is R233's; pair is the finer secondary


def cls_of(y):
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    return np.sign(y[ii] - y[jj])


# ⛔ TWO METRICS, BECAUSE v1 SILENTLY USED A DIFFERENT ONE FROM R233 AND THE FLOORS SAID SO.
#   v1 scored agreement as the FRACTION of the 6 pairs matching and got random floors of
#   0.83/0.82, against R233's reported 0.4044/0.4166 -- a 2x discrepancy that is not noise. R233's
#   "preserves Full's class" is an EXACT class match: all six pairs identical, or nothing. Running
#   a different statistic and calling it a fix of R233 is §4's "targets a different statistic than
#   the one being reported", and the floor mismatch is what caught it. BOTH are computed now:
#   EXACT is primary because it is R233's, PAIR is a finer secondary reported beside it.
def agree(a, b, metric):
    m = (cls_of(a) == cls_of(b))
    return float(m.all()) if metric == "exact" else float(m.mean())


def main() -> int:
    if not CACHE.exists():
        print(f"  UNRUNNABLE: {CACHE.name} absent. Exit 2, never 0."); return 2
    d = np.load(CACHE, allow_pickle=True)
    meta = [str(x).split("|") for x in d["meta"]]
    W, S = d["weight"], d["sat"]

    # (pid, arm, set) -> {crit: [sat per response]}, and the criterion's weight
    T = collections.defaultdict(lambda: collections.defaultdict(lambda: [None] * 4))
    WT = collections.defaultdict(dict)
    for k, (pid, arm, st, ci, ri) in enumerate(meta):
        T[(pid, arm, st)][int(ci)][int(ri)] = float(S[k])
        WT[(pid, arm, st)][int(ci)] = float(W[k])

    pids = sorted({m[0] for m in meta})
    ARMS = ("orig", "fresh")

    def score(pid, arm, st, crits=None):
        tab = T[(pid, arm, st)]
        w = WT[(pid, arm, st)]
        cs = sorted(tab) if crits is None else [c for c in crits if c in tab]
        if not cs:
            return None
        y = np.zeros(4)
        for c in cs:
            v = tab[c]
            if any(x is None for x in v):
                continue
            y += w[c] * np.array(v, float)
        return y

    print("R368 · R233 declined its verdict and named the fix. The cache makes it a re-analysis.\n")
    print(f"  {len(pids)} prompts · {len(meta)} cached judgements · no GPU\n")

    # ---- per-prompt agreement and difficulty ------------------------------------------------------
    AG, DIFF, NC = {}, {}, {}
    for arm in ARMS:
        for pid in pids:
            yf = score(pid, arm, "full")
            yc = score(pid, arm, "core")
            if yf is None or yc is None:
                continue
            for mt in METRICS:
                AG[(mt, pid, arm)] = agree(yc, yf, mt)
            # difficulty = how SEPARATED the four responses are under the full rubric.
            # R233 named exactly this as the confound: a homogeneous set is easier for anything.
            DIFF[(pid, arm)] = float(np.std(yf))
            NC[(pid, arm)] = len(T[(pid, arm, "core")])
    usable = [p for p in pids if ("exact", p, "orig") in AG and ("exact", p, "fresh") in AG]
    if not usable:
        print("  UNRUNNABLE: no prompt scored on both arms. Exit 2, never 0."); return 2

    # ---- strata on the ORIGINAL arm's difficulty, applied to both --------------------------------
    dorig = np.array([DIFF[(p, "orig")] for p in usable])
    edges = np.quantile(dorig, np.linspace(0, 1, NSTRATA + 1))
    edges[0], edges[-1] = -np.inf, np.inf

    def stratum(v):
        return int(np.searchsorted(edges, v, side="right") - 1)

    def floor_in(idx_prompts, arm, seed, metric):
        """size-matched random draw, drawn WITHIN the stratum -- R233's floors were whole-arm."""
        rng = np.random.default_rng(seed)
        vals = []
        for pid in idx_prompts:
            tab = T[(pid, arm, "full")]
            k = max(1, NC[(pid, arm)])
            cs = sorted(tab)
            if len(cs) <= k:
                continue
            sel = list(rng.choice(cs, k, replace=False))
            yr, yf = score(pid, arm, "full", sel), score(pid, arm, "full")
            if yr is None or yf is None:
                continue
            vals.append(agree(yr, yf, metric))
        return np.array(vals, float)

    RES, CON, MDEV = {}, {}, {}
    for mt in METRICS:
        print(f"\n  ── metric: {mt}{'  (R233 s own)' if mt=='exact' else '  (finer secondary)'} ──")
        print(f"    {'stratum':>8}{'n orig':>8}{'n fresh':>9}"
              f"{'core-floor orig':>17}{'core-floor fresh':>18}{'contrast':>11}")
        rows, contrasts, weights = [], [], []
        for s in range(NSTRATA):
            po = [p for p in usable if stratum(DIFF[(p, "orig")]) == s]
            pf = [p for p in usable if stratum(DIFF[(p, "fresh")]) == s]
            if len(po) < 5 or len(pf) < 5:
                rows.append(dict(stratum=s, n_orig=len(po), n_fresh=len(pf), excluded=True))
                print(f"    {s:>8}{len(po):>8}{len(pf):>9}{'excluded (n<5 on an arm)':>46}")
                continue
            co = np.array([AG[(mt, p, "orig")] for p in po])
            cf = np.array([AG[(mt, p, "fresh")] for p in pf])
            fo = np.mean([floor_in(po, "orig", sd, mt).mean() for sd in SEEDS])
            ff = np.mean([floor_in(pf, "fresh", sd, mt).mean() for sd in SEEDS])
            do_, df_ = float(co.mean() - fo), float(cf.mean() - ff)
            rows.append(dict(stratum=s, n_orig=len(po), n_fresh=len(pf), excluded=False,
                             core_orig=float(co.mean()), floor_orig=float(fo),
                             core_fresh=float(cf.mean()), floor_fresh=float(ff),
                             d_orig=do_, d_fresh=df_, contrast=df_ - do_))
            contrasts.append(df_ - do_); weights.append(len(po))
            print(f"    {s:>8}{len(po):>8}{len(pf):>9}{do_:>+17.4f}{df_:>+18.4f}{df_-do_:>+11.4f}")
        if not contrasts:
            print("\n  UNRUNNABLE: no usable stratum. Exit 2, never 0."); return 2
        wgt = np.array(weights, float) / sum(weights)
        con = float(np.dot(wgt, contrasts))
        sd = float(np.sqrt(np.dot(wgt, (np.array(contrasts) - con) ** 2)))
        mde = float(ZEFF * sd / math.sqrt(len(contrasts))) if len(contrasts) > 1 else float("nan")
        raw = (float(np.mean([AG[(mt, p, "fresh")] for p in usable]))
               - float(np.mean([AG[(mt, p, "orig")] for p in usable])))
        RES[mt], CON[mt], MDEV[mt] = rows, con, mde
        print(f"    MATCHED CONTRAST {con:+.4f} vs own MDE {mde:.4f} over {len(contrasts)} strata"
              f"   ·  UNMATCHED raw {raw:+.4f}")
    ROWS = RES["exact"]
    con, mde = CON["exact"], MDEV["exact"]
    occ = [r for r in ROWS if not r["excluded"]]

    # ---- controls ---------------------------------------------------------------------------------
    plac = []
    for arm in ARMS:
        for p in usable[:50]:
            yf = score(p, arm, "full")
            plac.append(agree(yf, yf, "exact"))
    plac_ok = all(abs(x - 1.0) < 1e-12 for x in plac)
    print(f"\n  PLACEBO   `full` against itself: {sorted(set(round(x,6) for x in plac))}  "
          f"{'PASS' if plac_ok else 'FAIL'}")

    fl = {arm: float(np.mean([floor_in(usable, arm, sd, "exact").mean() for sd in SEEDS]))
          for arm in ARMS}
    floor_ok = all(0.0 < fl[a] < 1.0 for a in ARMS)
    print(f"  FLOOR     within-arm random draw: orig {fl['orig']:.4f}, fresh {fl['fresh']:.4f} "
          f"— R233's whole-arm floors were 0.4044 / 0.4166  {'PASS' if floor_ok else 'FAIL'}")

    overlap_ok = len(occ) >= 2
    print(f"  OVERLAP   {len(occ)} of {NSTRATA} strata occupied on both arms  "
          f"{'PASS' if overlap_ok else 'FAIL'}")

    # positive: the full rubric's own top-k by weight must beat random on BOTH arms
    pos = {}
    for arm in ARMS:
        vals = []
        for pid in usable:
            tab, w = T[(pid, arm, "full")], WT[(pid, arm, "full")]
            k = max(1, NC[(pid, arm)])
            top = sorted(tab, key=lambda c: -w[c])[:k]
            yt, yf = score(pid, arm, "full", top), score(pid, arm, "full")
            if yt is None or yf is None:
                continue
            vals.append(agree(yt, yf, "exact"))
        pos[arm] = float(np.mean(vals)) - fl[arm]
    pos_ok = all(pos[a] > 0 for a in ARMS)
    print(f"  POSITIVE  the full rubric's own top-k by weight, vs the same random floor: "
          f"orig {pos['orig']:+.4f}, fresh {pos['fresh']:+.4f}  {'PASS' if pos_ok else 'FAIL'}")
    print(f"            without it a null here is silence, not `the core does not transport`")

    ctrl_ok = plac_ok and floor_ok and overlap_ok and pos_ok
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the table above is silence.")
        v = "UNVERIFIED"
    elif con > mde:
        print(f"  W-TRANSPORTS — matched on difficulty, the core reproduces the full rubric's")
        print(f"  ordering on UNSEEN responses better than a size-matched random draw, by "
              f"{con:+.4f}")
        print(f"  against its own MDE {mde:.4f}. ⭐ The definition is missing a clause it could carry.")
        v = "W_TRANSPORTS"
    elif con < -mde:
        print(f"  W-NO-TRANSPORT — matched, the core is WORSE than random on unseen responses "
              f"({con:+.4f} vs MDE {mde:.4f}).")
        print(f"  ⛔ `Core` then names something that works only where it was measured, and")
        print(f"  DEFINITION.md must say so rather than stay silent about transport.")
        v = "W_NO_TRANSPORT"
    else:
        print(f"  W-UNRESOLVED — matched, the contrast is {con:+.4f} against its own MDE {mde:.4f}.")
        print(f"  R233's UNVERIFIED stands, but for a BETTER reason: not `the arms are")
        print(f"  incomparable` — they have now been matched — but `matched, and this release")
        print(f"  cannot resolve it at {len(contrasts)} strata`. The MDE is the number to report,")
        print(f"  and DEFINITION.md must record transport as UNMEASURED rather than unmentioned.")
        v = "W_UNRESOLVED"

    print(f"\n  ⚠ R233's register entry does NOT move and is restated rather than dropped: the")
    print(f"    fresh responses carry NO HUMAN RANKINGS. This measures transport of the")
    print(f"    COMPILATION — agreement with the full rubric — and never agreement with people.")

    # R373: the MDE above divides by sqrt(len(contrasts)) -- a count of STRATA, not of prompts.
    # At k=4 the sd lands below half its true value 13.9% of the time, so the count is part of
    # the number and is recorded here rather than left to be hand-traced out of `strata`.
    art = dict(stamp(str(SELF)), n_prompts=len(usable), n_judgements=len(meta),
               n_units={m: len(RES[m]) for m in METRICS},
               strata={m: RES[m] for m in METRICS},
               matched_contrast={m: CON[m] for m in METRICS},
               mde={m: MDEV[m] for m in METRICS},
               floors=fl, positive=pos,
               controls=dict(placebo=plac_ok, floor=floor_ok, overlap=overlap_ok,
                             positive=pos_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r368_matched_transport.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
