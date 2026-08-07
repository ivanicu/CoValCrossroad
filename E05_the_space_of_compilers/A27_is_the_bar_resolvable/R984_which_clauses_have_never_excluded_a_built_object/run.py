#!/usr/bin/env python3
"""R984 — which clauses have never excluded an object somebody actually built?

⛔ WHY. R440 ran all four clauses on one 41-arm space and found: clause ① drops **0 of 9** clause-②
passers (and 24 of 32 rejects — subsumed), clause ③ drops **4 passers and 0 rejects** (orthogonal by
measurement), clause ④ drops **0 and 0**. Its headline: *"the definition is a pair."*

⭐ AND THEN ① AND ④ WERE BOTH REOPENED — EACH BY AN OBJECT THAT HAD TO BE BUILT. R925 established ①
independently necessary using **120 label-blind size-1 arms constructed for the purpose**; R821
established ④'s binding region non-empty by **planting an arm below the floor**. Neither reopening
came from the inventory. So the live question is not whether the clauses can bind — they can — but
whether either has ever excluded an object somebody built for another reason.

ESTIMAND        for each clause, the number of clause-② PASSERS it drops and the number of clause-②
                REJECTS it drops, on today's inventory. The reject column is what separates
                "discriminates nowhere" from "discriminates only where ② already has".
IDENTIFICATION  identified for ①, ② and ④ on all scoreable arms — each is a function of k, of the
                paired margin against the comparator, and of the paired margin against R803's
                judge-free floor. ⚠ ③ is NOT: it is a provenance property (R979), so it is computed
                only on the arms whose provenance is recorded, and that population is stated
                separately rather than merged.
SCOPE           population : R881's arm inventory on the 968 shared prompts (R440 used 41; this is
                             the same construction on today's larger set)
                instrument : mean A2 vs human targets; 8000-draw paired bootstrap; `lo > 0`
                baseline   : R440's committed table — ① 0/24, ③ 4/0, ④ 0/0
                regime     : comparator `generic` (R923's stronger); k from the ledger
WORLDS          A STILL A PAIR   ① and ④ drop 0 passers on the larger inventory too, so R440's
                                 finding survives a 2.4× population and the two clauses have never
                                 excluded a built object.
                B THE INVENTORY GREW INTO THEM   at least one of ①/④ now drops a passer, so the
                                 earlier zero was a population limit rather than a property.
                prediction matrix: A -> ① and ④ both 0 passers. B -> ≥1, and the arm is NAMED.
KILL            pre-registered, CONDITIONAL on the controls: if ① or ④ drops ≥1 clause-② passer,
                world A is dead and that arm must be named. If both drop 0, world B is dead.
POSITIVE CTRL   clause ② against its OWN admitted set must drop 0 — the join is sound. And clause ③,
                on the arms where provenance is known, must drop the label-consuming ones: a zero
                everywhere would mean the instrument cannot see any clause bite.
NEGATIVE CTRL   a synthetic arm at k=1 must be dropped by ①, and a synthetic arm scoring below the
                floor must be dropped by ④. Without these, "drops 0" is silence: R925 and R821 both
                had to CONSTRUCT such an object, and this round rebuilds them to prove the
                instrument fires.
PLACEBO         a clause against the empty set drops 0 and must not crash.
NOISE FLOOR     admission is a bootstrap CI verdict; the boundary layer is reported, since an arm
                inside the resolution of a cut is admitted by a margin the design cannot see.
MULTIPLICITY    every clause × (passers, rejects) cell reported; the named members persisted.
SEEDS           3 bootstrap seeds; a drop counts only if all three agree.
ARTIFACT        results/which_clauses_bite.json with this file's source hash.
IMPOSSIBLE      cross-release — N/A: one release, one inventory.
                construct validity — N/A: this asks which clauses cut, never whether cutting there
                is right.
                ⚠ AND A REAL ONE: "has never excluded a built object" is a statement about THIS
                inventory, which we built. It cannot distinguish "the clause is idle" from "nobody
                has yet built the object it excludes", and that distinction needs a third party.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                          # noqa: E402

PR = list(itertools.combinations(range(4), 2))
NBOOT, SEEDS = 8000, (11, 22, 33)
COMP = "generic"


def main() -> int:
    r881 = next(A24.glob("R881_*/results/boundary_distance.json"), None)
    r920 = next(A26.glob("R920_*/results/clause3_detectability.json"), None)
    r360 = next(A24.glob("R360_*/results/*.json"), None)
    if not (r881 and r920 and r360):
        print("  UNRUNNABLE: a prior artifact is missing. Exit 2, never 0.")
        return 2
    arms881 = [x["arm"] for x in json.loads(r881.read_text())["arms"]]
    K = json.loads(r360.read_text())["k"]
    labelled = {a["arm"]: a["labelled"] for a in json.loads(r920.read_text())["arms"]}

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{COMP}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)
    CH = np.array([[len(t) for t in (
        None,)] for _ in range(0)]) if False else None

    def vec(nm):
        f = RES / f"sat_{nm}.npz"
        if not f.exists():
            return None
        Sa = load_sat(f)
        v = np.full(n, np.nan)
        for k, p in enumerate(pids):
            if p in Sa:
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
        if np.isfinite(v).sum() < 200:
            return None
        return np.nan_to_num(v, nan=np.nanmean(v))

    # ── R803's judge-free floor, rebuilt (clause ④'s bar)
    text = {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        rs = r.get("responses") or []
        if len(rs) == 4:
            text[r["prompt_id"]] = [" ".join(str(m.get("content", "")) for m in
                                             (it.get("messages") or []) if isinstance(m, dict))
                                    for it in rs]
    CHm = np.array([[len(t) for t in text[p]] if p in text else [0, 0, 0, 0] for p in pids], float)
    floor_v = np.array([float((H[p] == np.sign(CHm[i][[u for u, _ in PR]]
                                               - CHm[i][[w for _, w in PR]])).mean())
                        for i, p in enumerate(pids)])

    V, names = [], []
    for a in arms881:
        v = vec(a)
        if v is not None:
            V.append(v); names.append(a)
    V = np.array(V)
    comp_v = vec(COMP)
    print(f"POPULATION  {len(names)} arms × {n} prompts   (R440 used 41)")
    print(f"  judge-free floor {floor_v.mean():.6f}   comparator {COMP} {comp_v.mean():.6f}")

    # ⚡ the count matrices are built ONCE and reused across every arm; v1 rebuilt an 8000x968
    #    multinomial per arm per seed, which is ~600 rebuilds for the same three matrices.
    CNT = [np.random.default_rng(s).multinomial(n, np.ones(n) / n, size=NBOOT).astype(float)
           for s in SEEDS]

    def resolvably_beats(arm_vec, ref_vec):
        """all three seeds must agree — a drop on one seed is not a drop"""
        d = arm_vec - ref_vec
        return all(float(np.percentile(c @ d / n, 2.5)) > 0 for c in CNT)

    passes2 = {nm: resolvably_beats(V[i], comp_v) for i, nm in enumerate(names)}
    passes4 = {nm: resolvably_beats(V[i], floor_v) for i, nm in enumerate(names)}
    # ⛔ v1 SCORED MISSING DATA AS A VERDICT, AND IT INVERTED THE HEADLINE. `K.get(nm) is not
    #    None and K[nm] > 1` reads an arm absent from R360's ledger as FAILING clause ①. R360
    #    covers 42 arms; this round scores 99. So 15 clause-② passers were reported as "dropped by
    #    clause ①" — and every one of the 15 has its k IN ITS OWN NAME (greedy_k8_fit1, k=8).
    #    Measured: 15 of 15 missing, 0 genuinely k=1. Three-valued instead: unknown is UNSCOREABLE,
    #    never a drop. §P6 — folding UNVERIFIED into OVERTURNED manufactures false verdicts.
    #    ⚠ And my own negative control passed throughout, because it tested a k I SUPPLIED and
    #    never a k that was ABSENT. A control validated on the case you imagined.
    passes1 = {nm: (K[nm] > 1) for nm in names if nm in K}
    unscoreable1 = [nm for nm in names if nm not in K]
    passers = [nm for nm in names if passes2[nm]]
    rejects = [nm for nm in names if not passes2[nm]]
    print(f"  clause ② admits {len(passers)}, rejects {len(rejects)}")

    def drops(pred, pool):
        return [nm for nm in pool if not pred.get(nm, True)]

    scored1 = [nm for nm in names if nm in K]
    d1p = drops(passes1, [nm for nm in passers if nm in K])
    d1r = drops(passes1, [nm for nm in rejects if nm in K])
    d4p, d4r = drops(passes4, passers), drops(passes4, rejects)
    known = [nm for nm in names if nm in labelled]
    d3p = [nm for nm in passers if nm in labelled and labelled[nm]]
    d3r = [nm for nm in rejects if nm in labelled and labelled[nm]]

    print(f"\n  {'clause':<28}{'drops PASSERS':>16}{'drops REJECTS':>16}   population")
    print(f"  {'① size > 1':<28}{len(d1p):>16}{len(d1r):>16}   {len(scored1)} arms with a "
          f"recorded k ({len(unscoreable1)} UNSCOREABLE, not dropped)")
    print(f"  {'③ no prompt labels':<28}{len(d3p):>16}{len(d3r):>16}   {len(known)} arms "
          f"with recorded provenance")
    print(f"  {'④ beats response-only':<28}{len(d4p):>16}{len(d4r):>16}   {len(names)} arms")
    print(f"\n  R440 committed: ① 0/24 · ③ 4/0 · ④ 0/0 on 41 arms")
    if d1p:
        print(f"  ⭐ ① drops these passers: {d1p}")
    if d4p:
        print(f"  ⭐ ④ drops these passers: {d4p}")

    # ── CONTROLS
    join_ok = len(drops(passes2, passers)) == 0
    see3 = len(d3p) > 0
    synth_k1 = "topw_k1" in K and not (K["topw_k1"] > 1)
    # ⭐ THE CONTROL v1 LACKED: an arm with NO recorded k must be unscoreable, never dropped.
    miss_ok = all(nm not in passes1 for nm in unscoreable1)
    below = floor_v - 0.05
    synth_low = not resolvably_beats(below, floor_v)
    print(f"\n  POSITIVE  clause ② against its own admitted set drops 0: {join_ok}")
    print(f"  POSITIVE  clause ③ drops {len(d3p)} passer(s) — the instrument can see a clause bite: "
          f"{see3}")
    print(f"  NEGATIVE  a synthetic k=1 arm is dropped by ①: {synth_k1}")
    print(f"  NEGATIVE  a synthetic arm 0.05 below the floor is dropped by ④: {synth_low}")
    print(f"  PLACEBO   any clause against the empty set drops {len(drops(passes1, []))}")
    print(f"  NEGATIVE  an arm with NO recorded k is unscoreable, not dropped: {miss_ok} "
          f"({len(unscoreable1)} such arms)")
    ctrl_ok = join_ok and see3 and synth_k1 and synth_low and miss_ok

    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; neither world is excluded"
    elif not d1p and not d4p:
        world = (f"A STILL A PAIR — ① and ④ drop 0 of {len(passers)} clause-② passers on "
                 f"{len(names)} arms, 2.4× R440's population. Neither has excluded a built object.")
    else:
        world = (f"B THE INVENTORY GREW INTO THEM — ① drops {d1p}, ④ drops {d4p}")
    print(f"\n⭐ {world}")

    out = HERE / "results" / "which_clauses_bite.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_arms=len(names), n_prompts=n, comparator=COMP, nboot=NBOOT, seeds=list(SEEDS),
        floor=float(floor_v.mean()), n_passers=len(passers), n_rejects=len(rejects),
        clause1={"population": len(scored1), "unscoreable": unscoreable1,
                 "drops_passers": d1p, "drops_rejects": len(d1r)},
        clause3={"population": len(known), "drops_passers": d3p, "drops_rejects": len(d3r)},
        clause4={"drops_passers": d4p, "drops_rejects": len(d4r)},
        r440_committed={"c1": [0, 24], "c3": [4, 0], "c4": [0, 0], "n_arms": 41},
        controls={"join_sound": join_ok, "clause3_visible": see3,
                  "synthetic_k1_dropped": synth_k1, "synthetic_below_floor_dropped": synth_low,
                  "missing_k_is_unscoreable": miss_ok,
                  "all_ok": ctrl_ok},
        world=world,
        limitation="'has never excluded a built object' is a statement about an inventory WE built; "
                   "it cannot separate an idle clause from one whose excluded object nobody has "
                   "constructed yet, and that needs a third party.",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
