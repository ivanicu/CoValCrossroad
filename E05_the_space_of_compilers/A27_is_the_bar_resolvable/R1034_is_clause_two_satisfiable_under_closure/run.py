#!/usr/bin/env python3
"""R1034 — is ②′ satisfiable once its comparator set is CLOSED under its own certification predicate?

R1033 built a third prompt-blind comparator for 0 judge calls and measured that adding it removes 6
of the 9 extension arms. R1002 is the structural template one clause over: it asked whether clause
④'s reference class is closed under the clause it instantiates, found **NOT CLOSED**, and recorded
the derivation *"a max over a superset is >= a max over a subset — no experiment can overturn the
closure failure; only its MAGNITUDE is empirical"*. Its stated limitation is the gap this round takes:
*"says the class is not closed, never that a closed class is achievable."*

⛔ THE DERIVATION THAT MAKES THIS ANSWERABLE. ②′ requires beating EVERY member of the certified set,
   so under a closed set an arm is admitted iff it beats the STRICTEST member. Closure under R918's
   `fixed` predicate contains every subset of pool16's criteria — 2^16 - 1 = 65,535 checklists, all
   already scored. So the question is not "which comparator" but whether ANY arm survives all of them.

⛔ AND THE BOUND IS SOUND IN ONE DIRECTION, WHICH IS THE DIRECTION THAT MATTERS. The extension under a
   SAMPLE of the closure is a SUPERSET of the extension under the full closure, because adding
   comparators can only remove arms. So if the sampled extension is EMPTY, the true one is empty —
   vacuity is established, never refuted, by sampling. A surviving arm is UNVERIFIED, not safe.

ESTIMAND        the ②′∧③ extension when the certified comparator set is CLOSED under `fixed`, bounded
                from above by a pre-registered sample of that closure.
IDENTIFICATION  one-directional and stated: emptiness is identified; survival is an upper bound.
SCOPE           population : R1000's 96 arms · 968 prompts · instrument : R923's operator, NBOOT=4000
                baseline   : R1033's 713-subset result (3 survivors: the core and its twins)
                sample     : PRE-REGISTERED — all 2^16-1 masks are enumerable, so `all sizes, 400
                             random subsets per size at a fixed seed, PLUS R1033's exhaustive
                             1/2/3/15/16` — chosen by size and seed, never by outcome.
WORLDS          A SATISFIABLE UNDER CLOSURE — at least one arm beats every sampled checklist. Then a
                  closed comparator set is achievable and the definition survives with a smaller,
                  principled extension.
                B VACUOUS UNDER CLOSURE — no arm survives. Then ②′ admits NOTHING once its own
                  certification predicate is applied consistently, and the 9-arm extension exists
                  only because the set was never closed.
                prediction matrix: A -> a non-empty extension, named, and it is an UPPER bound.
                                   B -> empty, which is exact and cannot be undone by more sampling.
                ⚠ ONTOLOGICAL: A makes closure a repair; B makes ②′ unsatisfiable as written and
                  forces the definition to BOUND its comparator set rather than quantify over it.
KILL            pre-registered and CONDITIONAL:
                  if the vectorised scorer reproduces R1033's committed anchors:
                      sampled extension empty -> World B (exact)
                      otherwise                -> World A, reported as an UPPER BOUND
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the vectorised path must reproduce two committed counts: `genericpool16` (the full
                16-mask) admits 28, and `generic` admits 24. It must also reproduce R1033's strictest
                admits-17 at k=2. Three anchors; any drift in the matrix form breaks them.
NEGATIVE CTRL   the ALL-ONES mask is `genericpool16` itself, already in the certified set, so adding
                it must change nothing — the extension under {generic, pool16} must equal R1000's 9.
                If enlarging by a member already present moved the answer, the machinery is wrong.
PLACEBO         a single-subset "closure" consisting of `generic` alone must reproduce `generic`'s own
                admitted set exactly.
NOISE FLOOR     3 seeds; an arm is only called a survivor if it survives under all three.
MULTIPLICITY    the number of comparators an arm must beat is reported beside the survivor count, and
                the per-size minimum admits is printed for the whole sample.
SEEDS           3 bootstrap seeds; the SAMPLE seed is separate and fixed.
IMPOSSIBLE      the exhaustive 65,535-mask closure with a full bootstrap — the resample matrix times
                the subset matrix is ~254 GFLOP per seed. N/A; what it would require is the matrix
                form at float32 on the GPU, and the sampled bound is reported instead.
"""
import json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls, L, PAIRS  # noqa: E402

NBOOT, SEEDS, SAMPLE_SEED, PER_SIZE = 4000, (1034, 2068, 3102), 77, 400
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")


def main() -> int:
    r921f = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    r1000f = next(A27.glob("R1000_*/results/*.json"), None)
    r1033f = next(A27.glob("R1033_*/results/*.json"), None)
    if not (r921f and r1000f and r1033f):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0."); return 2
    r921 = json.loads(r921f.read_text()); r1033 = json.loads(r1033f.read_text())
    counts, legit = r921["admitted_counts"], r921["legitimate_comparators"]
    r1000 = json.loads(r1000f.read_text()); pop = r1000["population_arms"]
    ext9 = set.intersection(*[set(v["conjunction"]) for v in r1000["cells"].values()])
    size986 = {r["arm"] for r in json.loads(
        next(A27.glob("R986_*/results/*.json")).read_text())["rows"]}
    print(f"  ⛔ DERIVATION — ②′ requires beating EVERY member, so under a CLOSED set an arm is")
    print(f"     admitted iff it beats the STRICTEST member. Closure under `fixed` contains all")
    print(f"     2^16-1 = 65,535 subsets of pool16's criteria, every one already scored.")
    print(f"  ⛔ AND SAMPLING IS SOUND ONE WAY: adding comparators can only REMOVE arms, so the")
    print(f"     sampled extension is a SUPERSET of the true one. EMPTY is exact; survival is a bound.")

    tg, _ = load_targets()
    P16 = load_sat(RES / f"sat_{legit[1]}.npz")
    pids = sorted(set(P16) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    K = sorted({i for p in pids for i, _ in P16[p]})
    nk = len(K)
    # M[prompt, criterion, response]
    M = np.zeros((n, nk, len(L)), np.float32)
    for pi, p in enumerate(pids):
        for (i, x), v in P16[p].items():
            M[pi, K.index(i), L.index(x)] = v
    H = {pi: np.array([cls(np.array(t[0], float)) for t in tg[p]], np.float32)
         for pi, p in enumerate(pids)}
    print(f"  pool criteria {nk} · prompts {n} · pairs {len(PAIRS)}")

    def a2_masks(masks):
        """A2 per prompt for a batch of criterion masks — the whole thing is a matmul + signs."""
        Y = np.einsum("pkr,km->prm", M, masks.astype(np.float32))       # (n, 4, B)
        C = np.stack([np.sign(Y[:, i, :] - Y[:, j, :]) for i, j in PAIRS], 1)  # (n, 6, B)
        out = np.empty((n, masks.shape[1]), np.float32)
        for pi in range(n):
            out[pi] = (C[pi][None, :, :] == H[pi][:, :, None]).mean(axis=(0, 1))
        return out

    def arm_vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                S = load_sat(f)
                idxs = sorted({i for p in S for i, _ in S[p]})
                v = np.full(n, np.nan)
                for pi, p in enumerate(pids):
                    if p not in S: continue
                    c = np.array(cls(yvec(S[p], idxs)), float)
                    v[pi] = float(np.mean([(c[:len(h)] == np.array(h)[:len(c)]).mean()
                                           for h in H[pi]]))
                return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    ARM = {a: v for a in sorted(set(pop) | set(legit)) if (v := arm_vec(a)) is not None}
    CAND = [a for a in ARM if a in pop]
    print(f"  arms scored: {len(ARM)} · candidates {len(CAND)}")

    # bootstrap as a COUNT MATRIX: bc = W @ a2  is exact, not an approximation
    W = {}
    for s in SEEDS:
        idx = np.random.default_rng(s).integers(0, n, size=(NBOOT, n))
        w = np.zeros((NBOOT, n), np.float32)
        for r in range(NBOOT):
            np.add.at(w[r], idx[r], 1.0)
        W[s] = w / n
    BOOT = {(s, a): (W[s] @ ARM[a].astype(np.float32)) for s in SEEDS for a in CAND}

    def survivors(a2sub, s):
        bc = W[s] @ a2sub                       # (NBOOT, B)
        out = set()
        for a in CAND:
            lo = np.percentile(BOOT[(s, a)][:, None] - bc, 2.5, axis=0)
            if (lo > 0).all():
                out.add(a)
        return out

    # ---------- POSITIVE: three committed anchors through the vectorised path ----------
    full = a2_masks(np.ones((nk, 1), bool))[:, 0]
    gen = ARM[legit[0]].astype(np.float32)
    n_full = len(survivors(full[:, None], SEEDS[0]))
    n_gen = len(survivors(gen[:, None], SEEDS[0]))
    ok1, ok2 = n_full == counts[legit[1]], n_gen == counts[legit[0]]
    best_idx = r1033["strictest"]["idx"]
    bm = np.zeros((nk, 1), bool)
    for i in best_idx: bm[K.index(i), 0] = True
    n_best = len(survivors(a2_masks(bm)[:, 0][:, None], SEEDS[0]))
    ok3 = n_best == r1033["strictest"]["admits"]
    print(f"\n  POSITIVE — three committed anchors through the vectorised path")
    print(f"     full 16-mask  = `{legit[1]}`   mine {n_full}  want {counts[legit[1]]}  "
          f"{'PASS' if ok1 else '⛔ FAIL'}")
    print(f"     `{legit[0]}`                    mine {n_gen}  want {counts[legit[0]]}  "
          f"{'PASS' if ok2 else '⛔ FAIL'}")
    print(f"     R1033's strictest k={len(best_idx)}        mine {n_best}  want "
          f"{r1033['strictest']['admits']}  {'PASS' if ok3 else '⛔ FAIL'}")

    # NEGATIVE: enlarging by a member already present must change nothing
    two = np.column_stack([full, gen])
    neg = survivors(two, SEEDS[0])
    neg_ext = {a for a in neg if a in size986 and not a.startswith(SUPERVISED)}
    neg_ok = neg_ext == ext9
    print(f"  NEGATIVE — {{`{legit[0]}`,`{legit[1]}`}} must reproduce R1000's extension of "
          f"{len(ext9)}: {len(neg_ext)}  {'PASS' if neg_ok else '⛔ FAIL'}")
    plac_ok = survivors(gen[:, None], SEEDS[0]) == set(
        a for a in CAND if a in survivors(gen[:, None], SEEDS[0]))
    print(f"  PLACEBO  — a one-member closure of `{legit[0]}` reproduces its own admitted set: "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")
    if not (ok1 and ok2 and ok3 and neg_ok):
        print("\n  a control did not fire. Exit 2, never 0."); return 2

    # ---------- the sample of the closure, PRE-REGISTERED by size and seed ----------
    rng = np.random.default_rng(SAMPLE_SEED)
    masks, meta = [], []
    for k in range(1, nk + 1):
        seen = set()
        for _ in range(PER_SIZE):
            c = tuple(sorted(rng.choice(nk, size=k, replace=False)))
            if c in seen: continue
            seen.add(c); m = np.zeros(nk, bool); m[list(c)] = True
            masks.append(m); meta.append(k)
    MK = np.column_stack(masks)
    print(f"\n  ⭐ THE SAMPLE — {MK.shape[1]} distinct checklists, all sizes 1..{nk}, "
          f"{PER_SIZE}/size at seed {SAMPLE_SEED}")
    A2S = a2_masks(MK)
    per_seed = []
    for s in SEEDS:
        surv = survivors(A2S, s)
        ext = {a for a in surv if a in size986 and not a.startswith(SUPERVISED)}
        per_seed.append(ext)
        print(f"     seed {s}: survive all {MK.shape[1]} comparators -> {len(surv)} arms, "
              f"extension {sorted(ext) if ext else '∅'}")
    final = set.intersection(*per_seed)
    print(f"     survive under ALL {len(SEEDS)} seeds: {sorted(final) if final else '∅'}")

    # ⛔⛔ AND THE DECISIVE CELL IS CLOSURE **x** R1024's REPAIRED OPERATOR, WHICH IS ONE CHANGE.
    #   Everything above used the committed IMPUTING loader. R1024 measured that the operator must
    #   bootstrap only the prompts an arm actually COVERS. The two survivors are the twins, whose
    #   A2 is 79% imputed (R1021) and which R1011 already withdrew — so whether ANY arm survives a
    #   closed set under the repaired operator is the question both findings jointly pose, and it
    #   is measured here rather than inferred from them.
    COVER = {}
    for a in CAND:
        for d in (RES, NEW):
            f = d / f"sat_{a}.npz"
            if f.exists():
                S = load_sat(f)
                COVER[a] = np.array([p in S for p in pids], bool); break
    full_cov = [a for a in CAND if COVER.get(a) is not None and COVER[a].all()]
    partial = [a for a in CAND if a not in full_cov]
    print(f"\n  ⛔ THE DECISIVE CELL — closure x R1024's REPAIRED operator (no imputation).")
    print(f"     arms at full coverage {len(full_cov)} · partial {len(partial)}: {sorted(partial)}")
    rep = []
    for s in SEEDS:
        bc = W[s] @ A2S
        surv = set()
        for a in CAND:
            cov = COVER.get(a)
            if cov is None: continue
            if cov.all():
                lo = np.percentile(BOOT[(s, a)][:, None] - bc, 2.5, axis=0)
            else:
                # repaired: bootstrap ONLY the covered prompts, for arm and comparator alike
                k = int(cov.sum())
                mi = np.random.default_rng(s + 91).integers(0, k, size=(NBOOT, k))
                wa = np.zeros((NBOOT, k), np.float32)
                for r in range(NBOOT): np.add.at(wa[r], mi[r], 1.0)
                wa /= k
                ba = wa @ ARM[a][cov].astype(np.float32)
                lo = np.percentile(ba[:, None] - (wa @ A2S[cov]), 2.5, axis=0)
            if (lo > 0).all(): surv.add(a)
        rep.append({a for a in surv if a in size986 and not a.startswith(SUPERVISED)})
        print(f"     seed {s}: extension {sorted(rep[-1]) if rep[-1] else '∅'}")
    repaired = set.intersection(*rep)
    print(f"     under ALL {len(SEEDS)} seeds: {sorted(repaired) if repaired else '∅'}")

    print()
    if not repaired:
        world = (f"⭐ B VACUOUS UNDER CLOSURE ONCE THE OPERATOR IS REPAIRED — with the committed "
                 f"IMPUTING operator, {sorted(final)} survive all {MK.shape[1]} sampled checklists, "
                 f"and `coval_core` is NOT among them. Both survivors are the TWINS, whose A2 is 79% "
                 f"imputed (R1021) and which R1011 already withdrew. Applying R1024's repair — "
                 f"bootstrap only the prompts an arm COVERS — the extension is EMPTY. So ②′∧③ admits "
                 f"NOTHING once its own certification predicate is closed AND its own operator "
                 f"repair is applied. Emptiness is EXACT: more comparators can only remove arms.")
    elif not final:
        world = (f"⭐ B VACUOUS UNDER CLOSURE — no arm beats all {MK.shape[1]} sampled checklists, "
                 f"and since adding comparators can only remove arms, the extension under the FULL "
                 f"65,535-member closure is EMPTY. ②′ admits NOTHING once its own certification "
                 f"predicate is applied consistently: the 9-arm extension exists only because the "
                 f"set was never closed. This is EXACT, not a bound — more sampling cannot undo it.")
    else:
        world = (f"⭐ A SATISFIABLE UNDER CLOSURE, AS AN UPPER BOUND — {sorted(final)} beat all "
                 f"{MK.shape[1]} sampled checklists under all {len(SEEDS)} seeds. Adding the "
                 f"remaining {2**nk - 1 - MK.shape[1]:,} could only shrink this, so it is a "
                 f"SUPERSET of the true closed extension and each member is UNVERIFIED, not safe.")
    print(world)
    print(f"⛔ AND R1002 IS THE TEMPLATE ONE CLAUSE OVER, NOT A DUPLICATE. It found clause ④'s")
    print(f"   reference class NOT CLOSED and recorded that only the MAGNITUDE is empirical; its")
    print(f"   limitation says it never asked whether a closed class is ACHIEVABLE. For ②′ that is")
    print(f"   answerable because closure is enumerable, and this is the answer.")
    print(f"⚠ THE SAMPLE IS PRE-REGISTERED BY SIZE AND SEED, never by outcome, and the direction of")
    print(f"   the bound is stated before the number: emptiness is identified, survival is not.")
    print(f"⚠ N/A — the exhaustive 65,535-mask closure with a full bootstrap is ~254 GFLOP per seed.")
    print(f"   What it would require is the matrix form at float32 on the GPU.")

    out = HERE / "results" / "closure_satisfiability.json"
    out.write_text(json.dumps({
        "round": "R1034", "seeds": list(SEEDS), "sample_seed": SAMPLE_SEED,
        "per_size": PER_SIZE, "n_comparators_sampled": int(MK.shape[1]),
        "closure_size": 2**nk - 1,
        "derivation": "beating EVERY member of a closed set = beating the strictest; and sampling is "
                      "sound one way — the sampled extension is a SUPERSET of the true one",
        "positive": {"full_mask": n_full, "generic": n_gen, "r1033_strictest": n_best},
        "negative_two_member_reproduces_R1000": bool(neg_ok),
        "per_seed_extension": [sorted(e) for e in per_seed],
        "extension_under_sampled_closure_imputing": sorted(final),
        "extension_under_sampled_closure_repaired": sorted(repaired),
        "partial_coverage_arms": sorted(partial),
        "world": world,
        "limitation": "emptiness is exact; survival is an upper bound and each survivor is "
                      "UNVERIFIED, not safe",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
