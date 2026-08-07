"""The published admitted set is one draw. What is the distribution over pool orderings?

`R294/run.py:140` builds the clause-② reference as `POOL[0:k]` -- the FIRST k rows of
`sat_genericpool16.npz`. Not a random draw, not a best-of: the order the file happens to be in. That
subset sits at the 93.7th percentile of all 1,820 size-4 subsets, a rank this campaign had already
recorded for `generic` and which I verified. And the admitted set is steeply sensitive to the
reference level -- 7 arms at ~0.538, 0 by ~0.557.

So the published five is ONE DRAW from a distribution nobody has measured, and the draw was made by
a file's row order. This round measures the distribution.

ESTIMAND, named before the method
---------------------------------
Over random PERMUTATIONS of the 16-criterion pool, the distribution of the admitted set when the
clause-② reference is `POOL_perm[0:k]` -- i.e. the same rule the census uses, applied to a pool that
could have been written down in any order.

    P(admitted | arm)   fraction of orderings admitting that arm
    |admitted|          distribution of the SET SIZE
    rank of published   where the identity permutation's set sits

A PERMUTATION, not an independent subset per k, because the census's rule is `prefix of the file` and
prefixes at different k are NESTED. Sampling independent subsets per k would measure a policy the
census does not use.

IDENTIFICATION. Exact: every quantity is recomputed from the same satisfaction matrices and the same
statistic the census uses. What is NOT identified is the clause-③ provenance flag, which is declared
per arm from `select_core.py`'s rules rather than computed -- it is carried over from R294 unchanged
and is invariant to pool order, so it cannot bias this comparison.

SCOPE
  population  the arms R294 judged, at their own k, against a size-matched prefix of a permuted pool
  instrument  A2 against every annotator, effect vs its own per-cell MDE, exactly as R294
  baseline    the identity permutation -- the published choice
  regime      n = the census's own per-arm prompt population; all annotators

WORLDS
  W1 ORDER IS NOISE     the admitted set barely moves; the published five is typical and the file
                        order is a harmless implementation detail.
  W2 ORDER IS THE ANSWER  the set moves a lot; `which five` is substantially a fact about a file's
                        row order, and the definition must name its reference explicitly or accept
                        that its output is not reproducible from its own words.

PREDICTION MATRIX
  W1 -> P(published set) high, |admitted| tightly concentrated
  W2 -> P(published set) low, |admitted| spread wide, and P(arm) far from 0/1 for several arms
⚠ Recorded before the run: I expect W2, because the reference level's own spread (min 0.5144,
  max 0.5575) straddles the whole 7->0 sensitivity band. If W1 comes back, the prediction was wrong
  and the reason will be that the ARMS move with the reference rather than against it -- a
  possibility the level-only analysis could not see, since it held the arms fixed.

PRE-REGISTERED KILL
    if the reproduction control fires (identity permutation reproduces R294's published set):
        P(published set) >= 0.50 -> W1. The order is noise; say so with the interval.
        P(published set) <  0.50 -> W2. The published five is one draw among many; report the
                                    distribution and P(arm) per arm, never the modal set alone.
    else: UNVERIFIED -- a reimplementation that cannot reproduce the census cannot vary it either.

CONTROLS
  REPRODUCTION, positive  the identity permutation must reproduce R294's committed admitted set
                          EXACTLY. This is the whole instrument validated where the answer is known.
  DETERMINISM, g=0        the identity permutation evaluated twice gives the same set.
  MOVEMENT, negative      at least one permutation must give a DIFFERENT set, or the sweep is
                          measuring nothing and `the order is noise` would be unfalsifiable.
  SEEDS                   two independent seeds; the distributions are reported separately, never
                          averaged.

EXIT
    0  controls hold and the distribution is reported
    1  a control misbehaved -- the distribution is silence
    2  inputs missing: an empty population, never a silent pass
"""
from __future__ import annotations
import hashlib, json, math, pathlib, sys, time
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls, yvec          # noqa: E402

RES = ROOT / "corebench" / "results"
CENSUS = ROOT / ("E05_the_space_of_compilers/A17_which_definitions_of_core_are_identifiable/"
                 "../A18_the_candidate_set_wall_was_wrong/x")   # resolved by glob below
ZEFF = 1.959964 + 0.841621
NPERM = int(__import__("os").environ.get("R353_NPERM", "400"))
SEEDS = [3531, 3532]


def census():
    import glob
    hits = sorted(glob.glob(str(ROOT / "E0*/A*/R294_the_definition_against_everything/results/*.json")))
    return json.loads(pathlib.Path(hits[0]).read_text()) if hits else None


def main() -> int:
    cen = census()
    if not cen:
        print("  UNRUNNABLE: R294's census is missing. Exit 2, never 0.")
        return 2
    rows = cen["rows"]
    POOL = load_sat(RES / "sat_genericpool16.npz")
    tg, _ = load_targets()
    base = sorted(set(POOL) & {p for p in tg if len(tg[p]) >= 2})
    HCA = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in base}
    npool = len({i for i, _ in POOL[base[0]]})
    print(f"R353 · the admitted set under every pool order   pool={npool}, {NPERM} permutations "
          f"x {len(SEEDS)} seeds\n")

    S, ps = {}, {}
    for a in rows:
        try:
            S[a] = load_sat(RES / f"sat_{a}.npz")
        except Exception:
            continue
        ps[a] = [p for p in base if p in S[a]]
    arms = [a for a in rows if a in S and ps[a]]

    def vec(sat, pids, idx=None):
        return np.array([(HCA[p] == np.array(cls(yvec(sat[p], idx if idx is not None
                          else sorted({i for i, _ in sat[p]}))), float)).mean() for p in pids])

    A = {a: vec(S[a], ps[a]) for a in arms}
    K = {a: rows[a]["k"] for a in arms}
    OK1 = {a: bool(rows[a]["ok1"]) for a in arms}
    OK3 = {a: bool(rows[a]["ok3"]) for a in arms}

    refcache: dict[tuple, np.ndarray] = {}

    def admitted(perm):
        out = []
        for a in arms:
            idx = tuple(sorted(perm[:min(K[a], npool)]))
            key = (a, idx)
            r = refcache.get(key)
            if r is None:
                r = vec(POOL, ps[a], list(idx))
                refcache[key] = r
            d = A[a] - r
            mde = ZEFF * d.std(ddof=1) / math.sqrt(len(d))
            if OK1[a] and OK3[a] and d.mean() > mde:
                out.append(a)
        return tuple(sorted(out))

    ident = admitted(list(range(npool)))
    published = tuple(sorted(a for a in rows if rows[a].get("admitted")))
    repro_ok = (ident == published)
    print(f"  REPRODUCTION control: identity permutation -> {len(ident)} arms")
    print(f"      mine      {list(ident)}")
    print(f"      published {list(published)}")
    print(f"      {'PASS' if repro_ok else 'FAIL — a reimplementation that cannot reproduce the census cannot vary it'}")
    g0_ok = (admitted(list(range(npool))) == ident)
    print(f"  DETERMINISM g=0: identity twice -> {'same' if g0_ok else 'DIFFERENT'}  "
          f"{'PASS' if g0_ok else 'FAIL'}")

    t0 = time.time()
    per_seed = {}
    for sd in SEEDS:
        rng = np.random.default_rng(sd)
        counts, sizes, armhits = {}, [], {a: 0 for a in arms}
        for _ in range(NPERM):
            perm = list(rng.permutation(npool))
            s = admitted(perm)
            counts[s] = counts.get(s, 0) + 1
            sizes.append(len(s))
            for a in s:
                armhits[a] += 1
        per_seed[sd] = {"counts": counts, "sizes": sizes, "armhits": armhits}
    el = time.time() - t0

    move_ok = any(s != ident for sd in SEEDS for s in per_seed[sd]["counts"])
    print(f"  MOVEMENT control: at least one ordering gives a different set  "
          f"{'PASS' if move_ok else 'FAIL — the sweep moves nothing'}")

    print(f"\n  {NPERM} permutations x {len(SEEDS)} seeds in {el:.0f}s\n")
    print(f"    {'seed':>6}{'P(published set)':>18}{'distinct sets':>15}{'|admitted| mean':>17}"
          f"{'min':>5}{'max':>5}")
    for sd in SEEDS:
        d = per_seed[sd]
        p = d["counts"].get(ident, 0) / NPERM
        print(f"    {sd:>6}{p:>18.3f}{len(d['counts']):>15}{np.mean(d['sizes']):>17.2f}"
              f"{min(d['sizes']):>5}{max(d['sizes']):>5}")

    print(f"\n    {'arm':<16}" + "".join(f"{'P(seed '+str(s)+')':>14}" for s in SEEDS))
    order = sorted(arms, key=lambda a: -per_seed[SEEDS[0]]["armhits"][a])
    for a in order:
        ps_ = [per_seed[s]["armhits"][a] / NPERM for s in SEEDS]
        if max(ps_) > 0.001:
            print(f"    {a:<16}" + "".join(f"{x:>14.3f}" for x in ps_))

    p0 = per_seed[SEEDS[0]]["counts"].get(ident, 0) / NPERM
    controls_ok = repro_ok and g0_ok and move_ok
    print()
    if not controls_ok:
        print("  UNVERIFIED: a control misbehaved, so the distribution above is silence.")
        v = "UNVERIFIED"
    elif p0 >= 0.50:
        print(f"  W1 — ORDER IS NOISE. The published set recurs in {p0:.1%} of orderings.")
        v = "W1_ORDER_IS_NOISE"
    else:
        print(f"  W2 — ORDER IS PART OF THE ANSWER. The published set recurs in only {p0:.1%} of")
        print("  orderings. `Which five` is substantially a fact about a file's row order, and the")
        print("  page must carry P(arm) rather than the modal set alone.")
        v = "W2_ORDER_IS_THE_ANSWER"

    art = {"npool": npool, "nperm": NPERM, "seeds": SEEDS, "identity_set": list(ident),
           "published_set": list(published), "elapsed_s": el,
           "per_seed": {str(s): {"p_published": per_seed[s]["counts"].get(ident, 0) / NPERM,
                                 "distinct_sets": len(per_seed[s]["counts"]),
                                 "size_mean": float(np.mean(per_seed[s]["sizes"])),
                                 "size_min": int(min(per_seed[s]["sizes"])),
                                 "size_max": int(max(per_seed[s]["sizes"])),
                                 "P_arm": {a: per_seed[s]["armhits"][a] / NPERM for a in arms}}
                        for s in SEEDS},
           "controls": {"reproduction": repro_ok, "g0": g0_ok, "movement": move_ok},
           "verdict": v}
    outp = HERE / "results" / "r353_pool_order.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    print("\n  ⚠ SCOPE. Clause ③ is DECLARED per arm from select_core.py's rules, not computed, so")
    print("    it is carried from R294 unchanged -- it is invariant to pool order and cannot bias")
    print("    this comparison, but it is not re-derived here either. And permutations are SAMPLED:")
    print(f"    {NPERM} of 16! , so P(arm) carries a binomial se of about {0.5/math.sqrt(NPERM):.3f}")
    print("    at p=0.5 -- enough to separate `almost always` from `almost never`, not enough to")
    print("    rank two arms three points apart.")
    return 0 if controls_ok else 1


if __name__ == "__main__":
    sys.exit(main())
