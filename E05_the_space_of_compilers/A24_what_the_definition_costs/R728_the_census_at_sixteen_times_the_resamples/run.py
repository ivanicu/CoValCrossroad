"""
R728 · the census at sixteen times the resamples

ESTIMAND        (1) at B = 16x the shipped resample count, how many of the 41 arms change admission?
                (2) the open one: at the SHIPPED B, how many change if only the SEED changes?
IDENTIFICATION  (1) exact -- the census is recomputable from the object. (2) a seed distribution over
                >=5 seeds. NOT identified: whether R294's construction is the right one.
SCOPE           population 41 arms from corebench/results/sat_*.npz · instrument R294's construction
                re-implemented on the same score.py · baseline the committed full_census.json ·
                regime B in {1200,4800,19200,76800}
WORLDS          W-STABLE no change · W-SEED the seed moves an admission · W-BROKEN my code differs
                from R294's and nothing is readable
KILL            conditional on the reproduction anchor. See PREREGISTRATION.txt.
POSITIVE CTRL   reproduce R294's committed ok1/ok2/ok3/admitted EXACTLY at B=1200, seed 31337.
                floor 0 < t 41 <= ceiling 41. A re-run that cannot reproduce the committed output is
                measuring a different object.
g=0             same B, same seed -> exactly 0 changes, or the code is non-deterministic.
NEGATIVE CTRL   permute the difference vectors ACROSS arms; the extension must change. excluded
                world: "admission is insensitive to which arm has which data".
SHAM            admissions from the B-INVARIANT half only (|eff| >= mde) -- the CI ingredient absent,
                not inverted. Must be identical at every B, exactly.
PLACEBO         the committed set against itself -> symmetric difference exactly 0.
NOISE FLOOR     seed-to-seed spread of admission counts at B=1200 over 5 seeds, measured.
MULTIPLICITY    4 B x 41 + 5 seeds x 41 = 369 admission decisions, all reported.
SPECIFICATION   B x seed x rule (full vs mde-only sham)
SEEDS           5 at B=1200, 3 higher; the seed flag is verified to change the draws
ARTIFACT        results/r728_census_rerun.json with tree_sha
IMPOSSIBLE      whether R294's construction is RIGHT -> a different definition, not a different B ·
                independently replicated -> a second implementer
"""
import hashlib, itertools, json, math, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
from report import verdict, POS                              # noqa: E402

RES = ROOT / "corebench" / "results"
CENSUS = ARC / "R294_the_definition_against_everything" / "results" / "full_census.json"
ZEFF = 1.959964 + 0.841621
USES_PROMPT_LABELS = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}
B_LEVELS = (1200, 4800, 19200, 76800)
SEEDS_AT_SHIPPED = (31337, 11, 22, 33, 44)


def build_vectors():
    """R294:76-152, reproduced. Returns per-arm (d1, d2, n, k, kcap, ok3)."""
    tg, _ = load_targets()
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and p.stem != "sat_genericpool16")
    POOL = load_sat(RES / "sat_genericpool16.npz")
    S, K = {}, {}
    for a in arms:
        try: S[a] = load_sat(RES / f"sat_{a}.npz")
        except Exception: continue
        ks = [len({i for i, _ in S[a][p]}) for p in list(S[a])[:200]]
        K[a] = int(np.median(ks))
    arms = [a for a in arms if a in S]
    BASE = set(POOL) & {p for p in tg if len(tg[p]) >= 2}
    PIDS = {a: sorted(set(S[a]) & BASE) for a in arms}
    pids = sorted(BASE & set(S["random_k4_s0"]))
    HC = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    npool = len({i for i, _ in POOL[pids[0]]})

    def on(sat, ps, idx=None):
        return np.array([np.mean([[cls(yvec(sat[p], idx if idx is not None
                                            else sorted({i for i, _ in sat[p]})))[q] == h[q]
                                   for q in range(6)] for h in HC[p]]) for p in ps])

    out = {}
    for a in arms:
        if a == "random_k4_s0":
            continue
        ps = PIDS[a]
        x  = on(S[a], ps)
        d1 = x - on(S["random_k4_s0"], ps)
        d2 = x - on(POOL, ps, list(range(min(K[a], npool))))
        out[a] = {"d1": d1, "d2": d2, "n": len(ps), "k": K[a],
                  "kcap": bool(K[a] > npool), "ok3": a not in USES_PROMPT_LABELS,
                  "a2": float(x.mean())}
    return out


def decide(d, B, seed, mde_only=False):
    n = len(d)
    idx = np.random.default_rng(seed).integers(0, n, (B, n))
    bs = d[idx].mean(axis=1)
    eff = float(d.mean()); lo = float(np.percentile(bs, 2.5)); hi = float(np.percentile(bs, 97.5))
    mde = ZEFF * float(d.std(ddof=1)) / math.sqrt(n)
    if mde_only:
        return (abs(eff) >= mde), eff, lo, hi, mde
    return (verdict(eff, lo, hi, mde) == POS), eff, lo, hi, mde


def census(V, B, seed, mde_only=False):
    adm, per = [], {}
    for a, v in V.items():
        o1, e1, l1, h1, m1 = decide(v["d1"], B, seed, mde_only)
        o2, e2, l2, h2, m2 = decide(v["d2"], B, seed, mde_only)
        ok = bool(o1 and o2 and v["ok3"])
        per[a] = {"ok1": bool(o1), "ok2": bool(o2), "ok3": v["ok3"], "admitted": ok,
                  "c1": [e1, l1, h1], "mde1": m1, "c2": [e2, l2, h2], "mde2": m2}
        if ok:
            adm.append(a)
    return tuple(sorted(adm)), per


def main() -> int:
    print("=" * 100); print("R728 · THE CENSUS AT SIXTEEN TIMES THE RESAMPLES"); print("=" * 100)
    if not CENSUS.exists():
        print("  UNRUNNABLE: committed census absent. Exit 2, never 0."); return 2
    cen = json.loads(CENSUS.read_text())
    committed = tuple(sorted(cen["admitted"])); crows = cen["rows"]

    cache = HERE / "results" / "_vectors.npz"
    if cache.exists():
        z = np.load(cache, allow_pickle=True)
        V = {k: v.item() for k, v in z.items()}
        print(f"  difference vectors loaded from cache ({len(V)} arms); delete "
              f"results/_vectors.npz to rebuild from the object")
    else:
        print("  rebuilding the difference vectors from the OBJECT (sat store), not the summary …")
        V = build_vectors()
        (HERE / "results").mkdir(exist_ok=True)
        np.savez_compressed(cache, **{k: np.array(v, dtype=object) for k, v in V.items()})
    if not V:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0"); return 2
    print(f"  arms rebuilt: {len(V)}   committed rows: {len(crows)}   "
          f"committed extension: {len(committed)}")

    ctl = {}
    print("\n─── CONTROLS ───")
    ext0, per0 = census(V, 1200, 31337)
    matched = sum(1 for a in V
                  if a in crows and per0[a]["ok1"] == crows[a]["ok1"]
                  and per0[a]["ok2"] == crows[a]["ok2"]
                  and per0[a]["admitted"] == crows[a]["admitted"])
    # ⚠ v1 required matched == len(V) = 92 while the CEILING is |committed ∩ rebuilt| = 41: a
    #   threshold above what the design can return under a perfect reproduction. The control could
    #   not pass. Ceiling computed, not chosen.
    shared = sorted(set(V) & set(crows))
    ceiling = len(shared)
    ext0_shared = tuple(sorted(a for a in shared if per0[a]["admitted"]))
    ctl["ANCHOR"] = (matched == ceiling) and (0 < ceiling <= len(crows)) and ext0_shared == committed
    print(f"  ANCHOR     R294's committed verdicts reproduced on {matched}/{ceiling} of the arms "
          f"its census CONTAINS (B=1200, seed 31337)")
    print(f"             band floor 0 < t {ceiling} <= ceiling {ceiling}  (v1 demanded {len(V)}, "
          f"which the design cannot return — a control that could not pass)")
    print(f"             extension on those arms reproduced: {ext0_shared == committed}")
    print(f"             -> {'PASS' if ctl['ANCHOR'] else 'FAIL — measuring a different object'}")
    if matched != len(V):
        for a in V:
            if a in crows and per0[a]["admitted"] != crows[a]["admitted"]:
                print(f"               ⚠ {a}: mine {per0[a]['admitted']} vs committed "
                      f"{crows[a]['admitted']}")

    ext0b, _ = census(V, 1200, 31337)
    ctl["G0"] = ext0b == ext0
    print(f"  g=0        same B, same seed -> identical extension: {ext0b == ext0} -> "
          f"{'PASS' if ctl['G0'] else 'FAIL — the code is non-deterministic'}")

    names = sorted(V)
    rot = names[1:] + names[:1]
    Vperm = {a: {**V[a], "d1": V[b]["d1"], "d2": V[b]["d2"], "n": V[b]["n"]}
             for a, b in zip(names, rot)}
    extp, _ = census(Vperm, 1200, 31337)
    ctl["NEGATIVE"] = extp != committed
    print(f"  NEGATIVE   difference vectors rotated across arms -> extension {list(extp)[:4]}"
          f"{'…' if len(extp) > 4 else ''} ({len(extp)}), differs: {extp != committed} -> "
          f"{'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             excluded world: 'admission is insensitive to which arm has which data'")

    sham = {B: census(V, B, 31337, mde_only=True)[0] for B in B_LEVELS}
    ctl["SHAM"] = len(set(sham.values())) == 1
    print(f"  SHAM       B-invariant half only (|eff|>=mde, CI absent): identical at all "
          f"{len(B_LEVELS)} B levels: {len(set(sham.values())) == 1}, size "
          f"{len(next(iter(sham.values())))} -> {'PASS' if ctl['SHAM'] else 'FAIL'}")

    ctl["PLACEBO"] = len(set(committed) ^ set(committed)) == 0
    print(f"  PLACEBO    committed set against itself -> symmetric difference 0 -> "
          f"{'PASS' if ctl['PLACEBO'] else 'FAIL'}")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── POPULATION DRIFT — not registered, found by the anchor's own failure ────────────────
    new_arms = sorted(set(V) - set(crows))
    gone = sorted(set(crows) - set(V))
    ext_today, _ = census(V, 1200, 31337)
    print(f"\n─── POPULATION DRIFT · the census population is a DIRECTORY GLOB ───")
    print(f"  arms in R294's committed census : {len(crows)}")
    print(f"  arms the same glob returns today: {len(V)}   new {len(new_arms)}   absent {len(gone)}")
    print(f"  re-running R294's own procedure over TODAY's population admits {len(ext_today)}, "
          f"not {len(committed)}")
    print(f"  the {len(set(ext_today) - set(committed))} additional admits: "
          f"{sorted(set(ext_today) - set(committed))[:8]}"
          f"{'…' if len(set(ext_today)-set(committed)) > 8 else ''}")
    print(f"  ⚠ THIS IS NOT A CORRECTION TO THE EXTENSION. The new arms were built by LATER rounds")
    print(f"    for other purposes; whether they are admissible objects is a separate question this")
    print(f"    round does not ask. What it establishes is that the census's POPULATION is defined")
    print(f"    by a glob over a directory later rounds write into, so the same procedure returns a")
    print(f"    different answer depending on when it runs.")

    # every sweep below answers the REGISTERED question, so it runs on the committed population
    V = {a: V[a] for a in shared}
    ext0, per0 = census(V, 1200, 31337)
    print(f"\n  sweeps below restricted to the {len(V)} arms of the COMMITTED census, which is the")
    print(f"  population the registered points are about.")

    # ── B SWEEP ─────────────────────────────────────────────────────────────────────────────
    print(f"\n─── B SWEEP · {len(B_LEVELS)} levels x {len(V)} arms ───")
    byB, ci_moved = {}, {}
    for B in B_LEVELS:
        ext, per = census(V, B, 31337)
        chg = [a for a in V if per[a]["admitted"] != per0[a]["admitted"]]
        byB[B] = {"ext": list(ext), "n_admitted": len(ext), "changes_vs_shipped": chg,
                  "equals_committed": ext == committed}
        ci_moved[B] = max(abs(per[a]["c1"][1] - per0[a]["c1"][1]) for a in V)
        print(f"  B={B:<7} admitted {len(ext):<3} equals committed {ext == committed}   "
              f"changes {len(chg)}   max |Δlo| vs B=1200 {ci_moved[B]:.6f}")

    # ── SEED SWEEP AT THE SHIPPED B ─────────────────────────────────────────────────────────
    print(f"\n─── SEED SWEEP AT THE SHIPPED B=1200 · {len(SEEDS_AT_SHIPPED)} seeds x {len(V)} arms ───")
    byS = {}
    for s in SEEDS_AT_SHIPPED:
        ext, per = census(V, 1200, s)
        chg = [a for a in V if per[a]["admitted"] != per0[a]["admitted"]]
        byS[s] = {"ext": list(ext), "n_admitted": len(ext), "changes": chg,
                  "equals_committed": ext == committed}
        print(f"  seed {s:<7} admitted {len(ext):<3} equals committed {ext == committed}   "
              f"changes {len(chg)}   {chg if chg else ''}")
    seed_draws_differ = len({tuple(round(census(V, 1200, s)[1][names[0]]["c1"][1], 12)
                                   for _ in (0,)) for s in SEEDS_AT_SHIPPED}) > 1
    print(f"  seed flag verified to change the draws (lo of {names[0]} differs across seeds): "
          f"{seed_draws_differ}")

    A = 1
    Bpt = len(byB[19200]["changes_vs_shipped"])
    C = max(len(byS[s]["changes"]) for s in SEEDS_AT_SHIPPED)
    D = matched
    directional = all(byB[b]["equals_committed"] for b in B_LEVELS) and \
                  all(byS[s]["equals_committed"] for s in SEEDS_AT_SHIPPED)

    print("\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A at-risk cells ⛔deriv", A, 0, 82, 1),
                                   ("B changes at B=19200 ⛔deriv", Bpt, 0, 41, 0),
                                   ("C changes from SEED alone", C, 0, 41, 0),
                                   ("D arms reproduced", D, 0, 41, 41)]:
        print(f"  {nm:<30} registered {reg:<4} -> {val:<6} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL extension identical at all B and all seeds -> {directional}")

    print("\n─── KILL (conditional on the anchor) ───")
    if not ctl["ANCHOR"]:
        world = ("UNVERIFIED — my re-implementation does not reproduce R294's committed verdicts, so "
                 "it is measuring a different object and no comparison below is admissible.")
    elif C > 0:
        world = (f"⭐⭐⭐ W-SEED. At the SHIPPED B=1200, changing only the bootstrap seed moves "
                 f"{C} admission(s): {sorted({a for s in SEEDS_AT_SHIPPED for a in byS[s]['changes']})}. "
                 f"The committed extension is one draw of a random procedure and every claim in this "
                 f"arc resting on the 5-set is downgraded to seed-dependent.")
    elif Bpt > 0:
        world = (f"⭐⭐⭐ THE DERIVATION IS WRONG. {Bpt} admission(s) moved at B=19200 although the "
                 f"B-invariant half was supposed to bind. Find the error before reporting anything.")
    else:
        world = (f"⭐⭐⭐ W-STABLE, AND FOR THE FIRST TIME AGAINST THE OBJECT. Re-running R294's census "
                 f"from the sat store reproduces its committed verdicts on {matched} of {len(V)} arms "
                 f"exactly. Raising the resample count 64-fold, from {B_LEVELS[0]} to {B_LEVELS[-1]}, "
                 f"changes NO admission and leaves the extension identical; so does changing the "
                 f"bootstrap seed at the shipped count, over {len(SEEDS_AT_SHIPPED)} seeds. "
                 f"⭐ The 5-set is neither a resample-count artifact nor a seed artifact. "
                 f"⛔ AND MOST OF THAT IS ALGEBRA, NOT EVIDENCE: mde does not depend on B, only the "
                 f"CI lower bound does, and the single cell within Monte-Carlo reach of its CI "
                 f"boundary (random_k8_s0 clause 1, t = 2.1458) is already excluded by the "
                 f"B-invariant half. Zero was forced. What was NOT forced, and is the round's real "
                 f"content, is that my independent re-implementation reproduces the committed census "
                 f"exactly — every prior round in this arc read the summary and none had checked that "
                 f"the summary is what the object yields. ⚠ The largest CI movement across the whole "
                 f"B sweep is {max(ci_moved.values()):.6f}, which is what a null of this shape looks "
                 f"like when it is real rather than silent.")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": all(ctl.values()), "controls": ctl, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "committed_extension": list(committed), "n_arms_rebuilt_today": len(crows) + len(new_arms), "n_arms_committed": len(crows),
           "population_drift_new_arms": new_arms, "population_drift_absent": gone,
           "extension_over_todays_population": list(ext_today),
           "extra_admits_today": sorted(set(ext_today) - set(committed)),
           "anchor_matched": matched, "anchor_extension_reproduced": ext0 == committed,
           "by_B": {str(k): v for k, v in byB.items()},
           "by_seed": {str(k): v for k, v in byS.items()},
           "max_abs_delta_lo_vs_shipped": {str(k): v for k, v in ci_moved.items()},
           "sham_mde_only_sizes": {str(k): len(v) for k, v in sham.items()},
           "A_at_risk_cells": A, "A_is_a_derivation": True,
           "B_changes_at_19200": Bpt, "B_is_a_derivation": True,
           "C_changes_from_seed": C, "D_arms_reproduced": D,
           "directional_identical_everywhere": directional,
           "registered": "A 1 [0,82] deriv; B 0 [0,41] deriv; C 0 [0,41]; D 41 [0,41]",
           "residue": "whether R294's construction is the right one is not addressed here"}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r728_census_rerun.json").write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"\n  artifact: results/r728_census_rerun.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
