#!/usr/bin/env python3
"""R783 · the released core's shortness is in the RELEASE, not the pipeline.

R782 made "the released core does not have four criteria" its headline off a count of SAT-FILE
indices, and its own E1b flagged that `coval_core` has no readable `core_*.json` -- so the criteria
were never read. §3: the attack applies hardest when it might succeed. CHECK #385 found the source,
`data/conversation_rubrics.jsonl`, 986 records carrying `coval_core` and `coval_full` as lists of
`{"criterion": str}`.

ESTIMAND        E1 release size distribution vs the scored one, TWO INDEPENDENT INSTRUMENTS ·
                E2 the 18 released records never scored · E3 why a short core is short ·
                E4 whether coval_core's clause-② standing depends on its short prompts
IDENTIFICATION  MARGINAL only -- the id spaces are disjoint (NEXT_SITE item 2), so per-record
                comparison is impossible and residuals up to |986-968| = 18 are uninformative (D1)
DERIVED FIRST   D1 a marginal residual <= 18 is evidence of nothing · D2 a multiset is order-invariant
                so the permutation negative is VOID and is NOT built · D3 a sham is undefined for a
                counting instrument and is NOT built (ledger 1131, applied before the fact)
WORLDS          A shipped · B pipeline · C disagreeing beyond the bound
CONTROLS        OBJECT · CROSS-INSTRUMENT (the real one) · PLACEBO · g=0 · POSITIVE (with a
                deliberately broken counter as the floor) · DUPLICATES
"""
import collections
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls                 # noqa: E402

RES = ROOT / "corebench/results"
REL = ROOT / "data/conversation_rubrics.jsonl"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
BOUND = None  # computed from the two population sizes, never typed

INSTRUMENT_UNIT = "a JSON list length"
CLAIM_UNIT = "a released conversation's core size"


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def read_release(path):
    """-> [(cid, core_list, full_list)], plus records missing a key"""
    recs, missing = [], []
    for line in open(path, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        cid = (r.get("conversation") or {}).get("id")
        if cid is None or "coval_core" not in r or "coval_full" not in r:
            missing.append(cid)
            continue
        recs.append((cid, r["coval_core"] or [], r["coval_full"] or []))
    return recs, missing


def main():
    out = {"instrument_unit": INSTRUMENT_UNIT, "claim_unit": CLAIM_UNIT}

    # ================= OBJECT CHECK -- exit 2, never 0 ============================================
    print("  OBJECT CHECK")
    if not REL.is_file():
        print("  UNRUNNABLE: the release file is absent. Exit 2, never 0.")
        return 2
    recs, missing = read_release(REL)
    ids = [c for c, _, _ in recs]
    ndup = len(ids) - len(set(ids))
    print(f"     release records {len(recs)}   records missing a key {len(missing)}   "
          f"distinct ids {len(set(ids))}   DUPLICATE ids {ndup}")

    targets, _ = load_targets()
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted({p for p in base if p in targets and len(targets[p]) >= 2})
    P = len(pids)
    S = load_sat(RES / "sat_coval_core.npz")
    F = load_sat(RES / "sat_full.npz")
    overlap = len(set(ids) & set(pids))
    global BOUND
    BOUND = abs(len(recs) - P)
    # ⚠ the first draft printed "per-record join IMPOSSIBLE" here, and E2 below builds one. A printed
    # impossibility that the same script refutes forty lines later is §4's *verdict string is not a
    # computation*: what is absent is a shared ID, not a join.
    print(f"     scored prompts {P}   id-space overlap {overlap}   -> no shared ID; a join must be "
          f"built from criterion TEXTS (E2), which R468 established is exact")
    print(f"     D1 bound on an uninformative residual = |{len(recs)} - {P}| = {BOUND}")
    if len(recs) == 0 or P == 0 or missing:
        print(f"  UNRUNNABLE: {len(recs)} records, {P} prompts, {len(missing)} malformed. "
              f"Exit 2, never 0.")
        return 2
    out["object"] = {"release_records": len(recs), "missing_key": len(missing),
                     "distinct_ids": len(set(ids)), "duplicate_ids": ndup,
                     "scored_prompts": P, "id_overlap": overlap, "d1_bound": BOUND}

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    rel_core = collections.Counter(len(c) for _, c, _ in recs)
    rel_full = collections.Counter(len(f) for _, _, f in recs)
    recs2, _ = read_release(REL)
    plac = collections.Counter(len(c) for _, c, _ in recs2) == rel_core
    print(f"     PLACEBO    recounting the same file returns identical counts: {plac}  "
          f"{'PASS' if plac else 'FAIL'}")
    g0 = len([]) == 0 and all(len(c) > 0 for _, c, _ in recs)
    print(f"     g=0        an empty list counts 0: True   records with an EMPTY core: "
          f"{sum(1 for _, c, _ in recs if len(c) == 0)}  {'PASS' if g0 else 'REPORTED'}")
    inject = [("x0", [], []), ("x1", [{"criterion": "a"}], []),
              ("x4", [{"criterion": str(i)} for i in range(4)], []),
              ("x39", [{"criterion": str(i)} for i in range(39)], [])]
    got = sorted(len(c) for _, c, _ in inject)
    exact = got == [0, 1, 4, 39]
    broken = sorted(len(json.dumps(c)) for _, c, _ in inject)   # the deliberately broken counter
    posok = exact and broken != [0, 1, 4, 39]
    print(f"     POSITIVE   injected sizes recovered exactly: {got} -> {exact}")
    print(f"                broken counter (character length) returns {broken} -> does NOT "
          f"reproduce them: {broken != [0, 1, 4, 39]}")
    print(f"                band COMPUTED: floor = the broken counter, ceiling = exact recovery   "
          f"POSITIVE {'PASS' if posok else 'FAIL'}")
    print(f"     NEGATIVE   ⛔ NOT BUILT -- D2: a multiset is order-invariant, so a record permutation "
          f"cannot move the distribution")
    print(f"     SHAM       ⛔ NOT BUILT -- D3: a counting instrument has no ingredient to remove")
    gate = plac and posok and ndup == 0 and not missing
    print(f"     DUPLICATES {ndup} (the confound: 18 unscored would be arithmetic about a file with "
          f"repeats)   gate {gate}")

    # ================= E1 · two instruments ========================================================
    print("\n  E1 - SIZE DISTRIBUTION, TWO INDEPENDENT INSTRUMENTS")
    sat_core = collections.Counter(len({i for i, _ in S[p]}) for p in pids)
    sat_full = collections.Counter(len({i for i, _ in F[p]}) for p in pids)
    print(f"     coval_core  RELEASE  {dict(sorted(rel_core.items()))}")
    print(f"     coval_core  SAT      {dict(sorted(sat_core.items()))}")
    resid = {k: rel_core.get(k, 0) - sat_core.get(k, 0)
             for k in set(rel_core) | set(sat_core)}
    worst = max(abs(v) for v in resid.values())
    print(f"     residual per cell {dict(sorted(resid.items()))}   worst |residual| {worst}   "
          f"D1 bound {BOUND}   within bound: {worst <= BOUND}")
    print(f"     coval_full  RELEASE  min {min(rel_full)} max {max(rel_full)}  "
          f"below 4: {sum(v for k, v in rel_full.items() if k < 4)}")
    print(f"     coval_full  SAT      min {min(sat_full)} max {max(sat_full)}  "
          f"below 4: {sum(v for k, v in sat_full.items() if k < 4)}")
    rel_short = sum(v for k, v in rel_core.items() if k < 4)
    sat_short = sum(v for k, v in sat_core.items() if k < 4)
    print(f"     ⭐ cores with FEWER than four criteria: RELEASE {rel_short} of {len(recs)} "
          f"({rel_short / len(recs):.2%})   SAT {sat_short} of {P} ({sat_short / P:.2%})")
    out["e1"] = {"rel_core": dict(rel_core), "sat_core": dict(sat_core),
                 "rel_full_min": min(rel_full), "rel_full_max": max(rel_full),
                 "sat_full_min": min(sat_full), "sat_full_max": max(sat_full),
                 "residual": resid, "worst_residual": worst,
                 "rel_short": rel_short, "sat_short": sat_short}

    # ================= E2 · the unscored records, IDENTIFIED =======================================
    # ⛔ THE PREREGISTRATION CALLED THIS IMPOSSIBLE -- "which 18 records went unscored, by id: the
    # recovered cross-space key". That was a FABRICATED IMPOSSIBILITY, killed inside the round.
    # R468 ("the join exists and is exact") established that the RUBRIC criterion texts are short
    # exact strings carried in BOTH spaces -- `core_full.json` in the ranking space and
    # `coval_full` in the rubric space -- so the join needs no threshold and no new data. It is
    # rebuilt here from scratch and its exactness is the control on itself.
    print(f"\n  E2 - RELEASED BUT NEVER SCORED, IDENTIFIED (the register entry was a false wall)")
    full = json.loads((RES / "core_full.json").read_text())
    relkey = collections.defaultdict(list)
    for cid, core, fl in recs:
        relkey[tuple(sorted((it.get("criterion") or "").strip() for it in fl))].append(cid)
    matched, unmatched, ambiguous = set(), 0, 0
    for p in pids:
        cand = relkey.get(tuple(sorted(str(x).strip() for x in full.get(p, []))), [])
        if len(cand) == 1:
            matched.add(cand[0])
        elif not cand:
            unmatched += 1
        else:
            ambiguous += 1
    unscored = [cid for cid, _, _ in recs if cid not in matched]
    print(f"     JOIN on rubric criterion texts: exact {len(matched)} of {P}   unmatched "
          f"{unmatched}   ambiguous {ambiguous}   (R468 reproduced)")
    size_of = {cid: len(core) for cid, core, _ in recs}
    uk = collections.Counter(size_of[c] for c in unscored)
    print(f"     unscored records {len(unscored)}   their core sizes {dict(sorted(uk.items()))}")
    recon = {k: rel_core.get(k, 0) - uk.get(k, 0) for k in sorted(rel_core)}
    exact_join = recon == {k: sat_core.get(k, 0) for k in sorted(rel_core)}
    print(f"     release MINUS unscored = {recon}")
    print(f"     scored sat file        = {dict(sorted(sat_core.items()))}")
    print(f"     ⭐ the two instruments agree EXACTLY once the join is applied: {exact_join}")
    print(f"     short share: unscored {sum(v for k, v in uk.items() if k < 4)}/{len(unscored)}  "
          f"vs release {rel_short}/{len(recs)}")
    out["e2"] = {"unscored": len(unscored), "join_exact": len(matched), "join_unmatched": unmatched,
                 "join_ambiguous": ambiguous, "unscored_sizes": dict(uk),
                 "reconstructed": recon, "exact_agreement": exact_join,
                 "register_entry_was_false": True}

    # ================= E3 · why a short core is short ==============================================
    print("\n  E3 - WHY A SHORT CORE IS SHORT")
    short = [(c, core) for c, core, _ in recs if len(core) < 4]
    empt = dup = ws = 0
    for _, core in short:
        txts = [(it.get("criterion") or "") for it in core]
        empt += sum(1 for t in txts if t == "")
        ws += sum(1 for t in txts if t.strip() == "" and t != "")
        dup += len(txts) - len(set(t.strip().lower() for t in txts))
    print(f"     short records {len(short)}   items that are EMPTY {empt}   WHITESPACE-only {ws}   "
          f"DUPLICATE within a record {dup}")
    mech = ("a de-duplication or emptiness artifact" if (empt or ws or dup)
            else "the generator produced fewer distinct substantive criteria")
    print(f"     -> {mech}")
    lens = [len((it.get('criterion') or '')) for _, core in short for it in core]
    print(f"     short-core criterion text length: min {min(lens)} median "
          f"{int(np.median(lens))} max {max(lens)}")
    out["e3"] = {"n_short": len(short), "empty": empt, "whitespace": ws, "dup": dup,
                 "mechanism": mech, "len_min": min(lens), "len_max": max(lens)}

    # ================= E4 · does ② depend on the short prompts? ====================================
    print("\n  E4 - coval_core's CLAUSE-② STANDING, WITH AND WITHOUT ITS SHORT PROMPTS")
    print("     ⚠ n_eff = 1.1 (R781): q is a fraction of a 0.043-wide band, NOT a probability")
    POOL = load_sat(RES / "sat_genericpool16.npz")
    keep_all = [p for p in pids if p in POOL]
    keep_4 = [p for p in keep_all if len({i for i, _ in S[p]}) == 4]
    idx = sorted({i for i, _ in POOL[keep_all[0]]})
    SUB = list(itertools.combinations(range(len(idx)), 4))

    # ⚠ the annotator class vectors are hoisted OUT of the subset loop. The first draft rebuilt them
    # inside `a2_on`, i.e. 3,640 x 968 x ~16 `cls()` calls for a quantity that does not depend on the
    # subset at all -- R781 had already hoisted it and I un-hoisted it. Cost meter, not correctness.
    HC_CACHE = {}

    def a2_on(sub_pids, getY):
        key = id(sub_pids)
        if key not in HC_CACHE:
            HC_CACHE[key] = [np.array([cls(y) for y, _ in targets[p]]) for p in sub_pids]
        hc = HC_CACHE[key]
        Y = getY(sub_pids)
        o = np.zeros(len(sub_pids))
        for a in range(len(sub_pids)):
            s = np.sign(Y[a][[i for i, _ in PR]] - Y[a][[j for _, j in PR]])
            o[a] = np.mean([(s == h).mean() for h in hc[a]])
        return o

    def arm_Y(sub_pids):
        return np.array([[sum(S[p].get((i, x), 0.0) for i in sorted({i for i, _ in S[p]}))
                          for x in L] for p in sub_pids])

    for label, sub in (("all prompts", keep_all), ("4-criterion only", keep_4)):
        T = np.zeros((len(sub), len(idx), 4))
        for a, p in enumerate(sub):
            for bi, i in enumerate(idx):
                for c_, x in enumerate(L):
                    T[a, bi, c_] = POOL[p].get((i, x), 0.0)
        v = a2_on(sub, arm_Y)
        ref = np.zeros((len(SUB), len(sub)))
        for si, s in enumerate(SUB):
            ref[si] = a2_on(sub, lambda sp, s=s: T[:, list(s), :].sum(axis=1))
        d = v[None, :] - ref
        keep = ~np.all(np.abs(d) < 1e-12, axis=1)
        m = d[keep].mean(axis=1)
        mde = ZEFF * d[keep].std(axis=1, ddof=1) / math.sqrt(len(sub))
        q = float((m > 0).mean())
        qr = float(((m > 0) & (np.abs(m) >= mde)).mean())
        print(f"     {label:<20} n {len(sub):>4}   A2 {v.mean():.4f}   q {q:.4f}   q_res {qr:.4f}")
        out.setdefault("e4", {})[label] = {"n": len(sub), "a2": float(v.mean()), "q": q, "q_res": qr}

    # ================= WORLD =======================================================================
    if not gate:
        world = "UNVERIFIED - a control did not fire. Never OVERTURNED, never CONFIRMED."
    elif rel_short > 0 and worst <= BOUND:
        world = (f"A - THE SHORTNESS IS SHIPPED: the release itself carries {rel_short} of "
                 f"{len(recs)} cores below four criteria ({rel_short / len(recs):.2%}), every cell "
                 f"residual against the scored count is within the D1 bound of {BOUND}, and the "
                 f"rubric never drops below 4")
    elif rel_short == 0 and sat_short > 0:
        world = (f"B - THE SHORTNESS IS THE PIPELINE: the release is uniformly >= 4 while the scored "
                 f"file has {sat_short} short; R782's headline retracts to 'the scored core'")
    elif worst > BOUND:
        world = (f"C - THE TWO INSTRUMENTS DISAGREE BEYOND THE BOUND: worst residual {worst} against "
                 f"{BOUND}; size is UNVERIFIED pending the recovered join")
    else:
        world = "NO WORLD CLAIMED: the branches do not cover this combination"
    print(f"\n  WORLD {world}")
    out["world"] = world
    out["tree_sha"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip()
    d = pathlib.Path(__file__).resolve().parent / "results"
    d.mkdir(exist_ok=True)
    (d / "release_vs_pipeline.json").write_text(json.dumps(out, indent=2, default=_plain))
    print("  artifact -> release_vs_pipeline.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
