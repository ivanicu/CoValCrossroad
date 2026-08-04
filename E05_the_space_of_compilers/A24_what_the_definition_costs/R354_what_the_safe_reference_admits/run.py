"""The campaign derived a rule for a safe clause-② reference. What does the definition admit under it?

R331 answered how to choose a clause-② reference, and answered it with a number:

    "a clause-② reference is SAFE because of its PERCENTILE -- put it high in the blind
     distribution -- the rule is a number, and it is p99, not p94."

Its own table shows why. Every one of the 1,820 k=4 subsets of the generic pool never reads the
conversation, so every one is a MEMBER OF CLAUSE ②'s OWN REFERENCE CLASS, and a reference that
admits any of them is refuted by clause ②'s own words. The published reference sits at p93.7 and
admits **3**. At p99 the blind admission rate is **0**.

⛔ AND NOBODY EVER REPORTED WHAT THE DEFINITION ADMITS AT p99. The rule has been on the page since
R331; the admitted set has only ever been published at the p93.7 reference the census happens to
use. R353 then showed that reference is a prefix of a file and that the published five recurs in
7.7% of pool orderings. So the one reference the campaign has ARGUED FOR has never been evaluated.

ESTIMAND, named before the method
---------------------------------
The admitted set when the clause-② reference is, at each arm's own k, the subset at the **p99** of
that k's blind distribution -- R331's rule, applied.

    level_p(k)   the p-th percentile of A2 over ALL C(16,k) size-k subsets of the pool
    reference    the subset achieving that level (nearest at or below p)
    admitted     clause ① and ③ as the census declares them, clause ② against that reference

Reported as a CURVE over p, not at one cell: p50, p75, p90, p93.7 (the published level), p95, p99.
One cell would be the same error the published set makes.

IDENTIFICATION. Exact and exhaustive where C(16,k) is enumerable, which it is for every k an
admitted arm has ever had. Arms with k > 8 are never admitted even at the weakest reference, so the
sweep is restricted to k <= 8 and that restriction is stated rather than silently applied.

WORLDS
  W1 THE RULE IS CHEAP     the admitted set at p99 is close to the published five. The reference
                           choice was lucky rather than load-bearing.
  W2 THE RULE IS EXPENSIVE the set collapses. Applying the campaign's own safety rule leaves
                           almost nothing admitted -- and if `coval_core` is among the excluded,
                           the rule excludes the object the benchmark ships.

PREDICTION MATRIX, recorded before the run
  W1 -> |admitted at p99| >= 4, coval_core in
  W2 -> |admitted at p99| <= 2, and coval_core plausibly OUT, because an earlier uniform-shift
        screen put its exclusion at a reference level of about 0.5516 while p99 is about 0.5547.
⚠ I expect W2. If W1 comes back, the screen's uniform-shift assumption was doing the work, which is
  exactly the approximation it declared and could not test.

⚠⚠ PREDICTION UPDATED WHILE THE RUN WAS IN FLIGHT, from data I ALREADY HAD and had not consulted.
R353 measured P(coval_core admitted) over random pool orderings at 1.000 and 0.998 across 400 draws
per seed. A random permutation's k=4 prefix is a UNIFORM random 4-subset, so ~1% of those draws sit
at or above p99 -- about four orderings. coval_core missed in 0 and 1 of 400, i.e. roughly the top
0.25%, which lies INSIDE the top 1% rather than covering it. So the p99 subset is probably NOT strong
enough to exclude it, and the exclusion sits nearer p99.75.

That REVERSES the coval_core half of the prediction: I now expect it to SURVIVE at p99, while the
set still collapses around it. The original guess came from the uniform-shift screen; this one comes
from a measurement, and the two disagree. Recording both, before the result, because a prediction
revised after seeing the answer is not a prediction -- and because the disagreement between a screen
and a measurement is itself the thing to watch.

PRE-REGISTERED KILL
    if the reproduction control fires and R331's p99 blind-admission rate is reproduced:
        |admitted at p99| <= 2 -> W2. Report the whole curve and say plainly which arms survive.
        otherwise              -> W1.
    else: UNVERIFIED.

CONTROLS
  REPRODUCTION      the census's own reference (POOL[0:k]) must reproduce R294's committed five.
  R331 CROSS-CHECK  the p99 level at k=4 must match R331's committed 0.5547, and the blind
                    admission rate at that level must be 0 -- a REAL positive control against a
                    number computed by a different round with different code.
  MONOTONICITY      the admitted set must SHRINK as p rises; a stricter reference admitting MORE
                    arms would mean the sweep is not measuring what it claims.
  ⚠ no permutation null: the question is the value of a computed reference, not whether a pairing
    matters.

EXIT
    0  controls hold and the curve is reported
    1  a control misbehaved -- the curve is silence
    2  inputs missing: an empty population, never a silent pass
"""
from __future__ import annotations
import glob, hashlib, itertools, json, math, pathlib, sys, time
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls, yvec          # noqa: E402

RES = ROOT / "corebench" / "results"
ZEFF = 1.959964 + 0.841621
PCTS = [50, 75, 90, 93.7, 95, 99]
KMAX = 8


def main() -> int:
    hits = sorted(glob.glob(str(ROOT / "E0*/A*/R294_the_definition_against_everything/results/*.json")))
    if not hits:
        print("  UNRUNNABLE: R294's census is missing. Exit 2, never 0.")
        return 2
    rows = json.loads(pathlib.Path(hits[0]).read_text())["rows"]
    POOL = load_sat(RES / "sat_genericpool16.npz")
    tg, _ = load_targets()
    base = sorted(set(POOL) & {p for p in tg if len(tg[p]) >= 2})
    HCA = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in base}
    npool = len({i for i, _ in POOL[base[0]]})
    print(f"R354 · what does R331's SAFE reference admit?   pool={npool}, k<= {KMAX}\n")

    S, ps = {}, {}
    for a in rows:
        try:
            S[a] = load_sat(RES / f"sat_{a}.npz")
        except Exception:
            continue
        ps[a] = [p for p in base if p in S[a]]
    arms = [a for a in rows if a in S and ps[a] and rows[a]["k"] <= KMAX]
    print(f"  {len(arms)} arms with k <= {KMAX}; arms with larger k are not admitted even at the")
    print("  weakest reference, so the restriction is stated rather than silently applied.\n")

    def vec(sat, pids, idx=None):
        return np.array([(HCA[p] == np.array(cls(yvec(sat[p], idx if idx is not None
                          else sorted({i for i, _ in sat[p]}))), float)).mean() for p in pids])

    A = {a: vec(S[a], ps[a]) for a in arms}
    ks = sorted({rows[a]["k"] for a in arms})
    t0 = time.time()
    # blind distribution per k, on a FIXED population so percentiles are comparable across k
    fixed = ps[max(arms, key=lambda a: len(ps[a]))]
    dist, subs_by_k, VEC4 = {}, {}, None
    for k in ks:
        subs = list(itertools.combinations(range(npool), k))
        V = np.array([vec(POOL, fixed, list(s)) for s in subs])   # (nsub, nprompt)
        lv = V.mean(axis=1)
        if k == 4:
            VEC4 = V          # kept for the R331 cross-check, which needs PAIRED differences
        dist[k], subs_by_k[k] = lv, subs
        print(f"    k={k:<3} C(16,k)={len(subs):>6}  min {lv.min():.4f}  med {np.median(lv):.4f}  "
              f"max {lv.max():.4f}")
    print(f"  blind distributions in {time.time()-t0:.0f}s\n")

    def ref_at(k, p):
        lv, subs = dist[k], subs_by_k[k]
        thr = np.percentile(lv, p)
        i = int(np.argmin(np.where(lv <= thr, thr - lv, np.inf)))
        return list(subs[i]), float(lv[i])

    def admitted(getidx):
        out = []
        for a in arms:
            idx = getidx(rows[a]["k"])
            d = A[a] - vec(POOL, ps[a], idx)
            mde = ZEFF * d.std(ddof=1) / math.sqrt(len(d))
            if rows[a]["ok1"] and rows[a]["ok3"] and d.mean() > mde:
                out.append(a)
        return sorted(out)

    published = sorted(a for a in rows if rows[a].get("admitted"))
    ident = admitted(lambda k: list(range(min(k, npool))))
    repro_ok = (ident == published)
    print(f"  REPRODUCTION: census reference -> {ident}")
    print(f"      published                  -> {published}   {'PASS' if repro_ok else 'FAIL'}")

    # ⚠ R331 CROSS-CHECK, CORRECTED. v1 counted blind subsets scoring numerically ABOVE the
    # reference and got 19 where R331 committed 0 -- and 19 is ARITHMETICALLY FORCED, because the
    # 99th percentile of 1,820 values has ~18 above it BY DEFINITION. The control was computing a
    # tautology and comparing it to a measurement. R331's `admitted` means what clause ② means:
    # RESOLVABLY better, effect > its own MDE. So the count is now a paired computation per subset,
    # the same statistic the definition uses -- the unit-equality rule, applied to a control that
    # had quietly used `>` where the claim said `admitted`.
    idx99, lv99 = ref_at(4, 99)
    ref99 = vec(POOL, fixed, idx99)
    dd = VEC4 - ref99                                   # (nsub, nprompt) paired differences
    eff = dd.mean(axis=1)
    mdes = ZEFF * dd.std(axis=1, ddof=1) / math.sqrt(dd.shape[1])
    blind_admit = int((eff > mdes).sum())
    r331_ok = abs(lv99 - 0.5547) < 0.0015 and blind_admit == 0
    print(f"  R331 CROSS-CHECK: p99 level at k=4 = {lv99:.4f} (R331 committed 0.5547); blind subsets")
    print(f"      RESOLVABLY better = {blind_admit} (R331 committed 0)   {'PASS' if r331_ok else 'FAIL'}")
    print(f"      (numerically above, which is forced at ~1% by definition: {int((dist[4] > lv99).sum())})")

    print(f"\n    {'percentile':>11}{'ref level (k=4)':>17}{'|admitted|':>12}   set")
    curve, prev = {}, None
    mono_ok = True
    for p in PCTS:
        s = admitted(lambda k, _p=p: ref_at(k, _p)[0])
        curve[str(p)] = {"level_k4": ref_at(4, p)[1], "admitted": s}
        if prev is not None and not set(s) <= set(prev):
            mono_ok = False
        prev = s
        mark = "   <- the published reference" if abs(p - 93.7) < 0.05 else ""
        print(f"    {p:>11}{ref_at(4, p)[1]:>17.4f}{len(s):>12}   {', '.join(s) or '(none)'}{mark}")
    print(f"\n  MONOTONICITY: the set shrinks as the reference strengthens  "
          f"{'PASS' if mono_ok else 'FAIL'}")

    at99 = curve["99"]["admitted"]
    ok = repro_ok and r331_ok and mono_ok
    print()
    if not ok:
        print("  UNVERIFIED: a control misbehaved, so the curve above is silence.")
        v = "UNVERIFIED"
    elif len(at99) <= 2:
        print(f"  W2 — THE RULE IS EXPENSIVE. At R331's own safe reference the definition admits")
        print(f"  {len(at99)} arm(s): {at99 or '(none)'}.")
        if "coval_core" not in at99:
            print("  ⛔ `coval_core` — the core the benchmark ships — is NOT among them.")
        v = "W2_RULE_IS_EXPENSIVE"
    else:
        print(f"  W1 — THE RULE IS CHEAP. At p99 the definition still admits {len(at99)}: {at99}")
        v = "W1_RULE_IS_CHEAP"

    art = {"npool": npool, "kmax": KMAX, "arms": arms, "published": published,
           "identity": ident, "curve": curve, "p99_level_k4": lv99,
           "blind_admit_at_p99_k4": blind_admit,
           "controls": {"reproduction": repro_ok, "r331_crosscheck": r331_ok,
                        "monotonicity": mono_ok}, "verdict": v}
    outp = HERE / "results" / "r354_safe_reference.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    print("\n  ⚠ SCOPE. Percentiles are computed on ONE fixed prompt population so that levels are")
    print("    comparable across k; each arm's own contrast still uses its own population, which is")
    print("    what the census does. Clause ① and ③ are taken from the census unchanged -- they do")
    print("    not depend on the clause-② reference, so they cannot bias this curve, but they are")
    print("    not re-derived here either.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
