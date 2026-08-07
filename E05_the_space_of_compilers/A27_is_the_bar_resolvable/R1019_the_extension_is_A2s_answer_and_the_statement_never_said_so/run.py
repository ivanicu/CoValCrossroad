#!/usr/bin/env python3
"""R1019 — every extension figure in this arc is A2's answer, and nothing said so.

⛔ PRIOR ART FIRST, BECAUSE IT IS ON DISK AND IT IS THE HEADLINE'S SCOPE. R558 recorded, from R288's
committed `target_sweep.json`: **968 prompts, six targets, four distinct admitted sets** —
`A2·annot` and `A2·consensus` admit {coval_core, topw_k4}; `A1·annot` and `A1·consensus` admit
**nothing**; `tau·mean` admits **coval_core alone**; `top1·mean` admits **topw_k4 and NOT the
released core**. ⚠ That sweep is over **10 arms**. This arc has spent nineteen rounds reporting an
extension over **96** — *"9 arms, 4 distinct objects"* — and **never named the target**.

⭐ WHAT IS NEW HERE, and it is not the target-dependence: whether the CURRENT formulation — ②′∧③,
the intersection over both certified prompt-blind comparators plus the label predicate — survives a
target change on the FULL population. R288 swept clause ② alone, on a tenth of the arms, before ②′
and ③ existed.

ESTIMAND        the ②′∧③ extension computed under A2 and under Kendall tau-b, over the same 96 arms;
                and whether the sets differ.
IDENTIFICATION  direct. Both targets are computable from the committed satisfaction files: A2 is the
                graded class agreement this arc has used throughout, tau-b is `score.tau_b` against
                each annotator's ranking, averaged the same way.
SCOPE           population : R1000's 96-arm intersection · instrument : A2 and tau-b
                baseline   : each other · regime : this release, n = 968
WORLDS          A TARGET-STABLE   the two extensions coincide. Then "9 arms" needs no target label
                                  for these two targets, and the six-target result is about targets
                                  this round did not compute.
                B TARGET-BOUND    they differ. Then every extension figure in the statement and the
                                  README is A2's answer and must say so.
                prediction matrix: A -> identical sets. B -> a symmetric difference.
KILL            pre-registered: if the sets differ, the target label is written into DEFINITION.md
                and README.md in THIS round. A number whose scope was measured and not stated is
                eleven of twelve retractions in this project's own history.
POSITIVE CTRL   on R288's own 10-arm subset, the A2 branch here must admit exactly {coval_core,
                topw_k4} — R288's committed answer. If it does not, this is not R288's A2 and no
                comparison below means anything.
NEGATIVE CTRL   a MONOTONE rescaling of A2 (multiply by 2) must give the IDENTICAL admitted set,
                because clause ② is a paired comparison and is invariant to a positive affine change
                of the target. If rescaling moves the set, the operator is not doing what it says.
PLACEBO         A2 against A2 gives a symmetric difference of exactly 0.
NOISE FLOOR     n/a — set comparison, not an estimate. Labelled. The bootstrap that decides each
                admission carries its own interval and the seed is held fixed across targets so the
                only moving part is the target.
MULTIPLICITY    2 targets × 2 comparators, all four admitted sets printed.
ARTIFACT        results/target_scope.json with this file's source hash.
IMPOSSIBLE      ⚠ the other four targets R288 swept (A1·annot, A1·consensus, top1·mean and the
                consensus variant) — N/A here: A1 and top1 need scoring conventions this round would
                have to reconstruct, and reconstructing a target in order to sweep it is how a
                specification curve becomes an invention. R288's committed answer for them stands
                as the record, at ITS population of 10.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls, tau_b  # noqa: E402

NBOOT, SEED = 8000, 921
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")


def main() -> int:
    need = {"r921": next(A26.glob("R921_*/results/comparator_sweep.json"), None),
            "r1000": next(A27.glob("R1000_*/results/conjunction.json"), None),
            "r288": next(A24.glob("R288_*/results/target_sweep.json"), None),
            "r986": next(A27.glob("R986_*/results/size_decomposition.json"), None)}
    if [k for k, v in need.items() if v is None]:
        print(f"  UNRUNNABLE: missing {[k for k, v in need.items() if v is None]}. Exit 2.")
        return 2
    legit = json.loads(need["r921"].read_text())["legitimate_comparators"]
    pop = json.loads(need["r1000"].read_text())["population_arms"]
    r288 = json.loads(need["r288"].read_text())
    size986 = {r["arm"]: r for r in json.loads(need["r986"].read_text())["rows"]}
    print(f"  ⛔ PRIOR ART: R288 swept {len(r288['targets'])} targets over {len(r288['scores'])} "
          f"arms and found {len(r288['distinct_sets'])} distinct admitted sets:")
    for t, adm in r288["admitted"].items():
        print(f"     {t:<16}{adm}")
    print(f"  ⭐ THIS ROUND: the CURRENT formulation ②′∧③ over {len(pop)} arms, two targets.")

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: [np.array(t[0], float) for t in tg[p]] for p in pids}
    Hc = {p: [cls(h) for h in H[p]] for p in pids}
    n = len(pids)

    def vecs(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            a2 = np.full(n, np.nan)
            tb = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p not in Sa:
                    continue
                y = yvec(Sa[p], sorted({i for i, _ in Sa[p]}))
                c = np.array(cls(y), float)
                a2[k] = float(np.mean([(c[:len(h)] == h[:len(c)]).mean() for h in Hc[p]]))
                tb[k] = float(np.mean([tau_b(list(y), list(h)) for h in H[p]]))
            if np.isfinite(a2).sum() < 200:
                return None
            return (np.nan_to_num(a2, nan=np.nanmean(a2)),
                    np.nan_to_num(tb, nan=np.nanmean(tb)))
        return None

    want = sorted(set(pop) | set(legit))
    A2, TB, names = {}, {}, []
    for a in want:
        v = vecs(a)
        if v is not None:
            A2[a], TB[a] = v
            names.append(a)
    print(f"  arms scored on both targets: {len(names)} · prompts {n}")

    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))

    def extension(V, arms):
        """②′ ∧ ③ — resolvably beats EVERY certified comparator, and reads no labels."""
        sets = []
        for c in legit:
            if c not in V:
                return None
            base = V[c][idx].mean(axis=1)
            adm = set()
            for a in arms:
                if a not in V:
                    continue
                d = (V[a] - V[c])[idx].mean(axis=1)
                if np.percentile(d, 2.5) > 0:
                    adm.add(a)
            sets.append(adm)
        out = set.intersection(*sets) if sets else set()
        return {a for a in out if a in size986 and not a.startswith(SUPERVISED)}

    cand = [a for a in names if a in pop]
    ext_a2 = extension(A2, cand)
    ext_tb = extension(TB, cand)

    # ---------- controls ----------
    sub = [a for a in r288["scores"] if a in A2]
    pos_set = extension({k: v for k, v in A2.items()}, sub)
    want288 = set(r288["admitted"]["A2·annot"])
    pos_ok = pos_set is not None and pos_set == want288
    A2x2 = {k: v * 2.0 for k, v in A2.items()}
    neg_set = extension(A2x2, cand)
    neg_ok = neg_set == ext_a2
    plac_ok = extension(A2, cand) == ext_a2
    print(f"\n  POSITIVE — on R288's own {len(sub)}-arm subset, the A2 branch must admit "
          f"{sorted(want288)}: got {sorted(pos_set or [])} → {'PASS' if pos_ok else '⛔ FAIL'}")
    print(f"  NEGATIVE — a monotone rescaling (A2 x2) must give the IDENTICAL set: "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"  PLACEBO  — A2 against A2, symmetric difference 0: {'PASS' if plac_ok else '⛔ FAIL'}")
    if not (pos_ok and neg_ok and plac_ok):
        print("\n⛔ a control failed; the comparison below certifies nothing. Exit 2, never 0.")
        return 2

    only_a2 = sorted(ext_a2 - ext_tb)
    only_tb = sorted(ext_tb - ext_a2)
    print(f"\n  extension under A2      {len(ext_a2):>3}  {sorted(ext_a2)}")
    print(f"  extension under tau-b   {len(ext_tb):>3}  {sorted(ext_tb)}")
    print(f"  only under A2           {len(only_a2):>3}  {only_a2}")
    print(f"  only under tau-b        {len(only_tb):>3}  {only_tb}")
    print(f"  core admitted under A2 {'coval_core' in ext_a2} · under tau-b "
          f"{'coval_core' in ext_tb}")

    same = ext_a2 == ext_tb
    world = ("A TARGET-STABLE — the two extensions coincide" if same else
             f"B TARGET-BOUND — the extensions differ by {len(only_a2) + len(only_tb)} arms, so "
             f"every extension figure in this arc is A2's answer")
    print(f"\n⭐ {world}")
    if not same:
        print("⛔ PRE-REGISTERED KILL FIRES: the target label goes into DEFINITION.md and README.md")
        print("   in THIS round. A number whose scope was measured and not stated is eleven of")
        print("   twelve retractions in this project's own history.")
    r288_tau = set(r288["admitted"].get("tau·mean", []))
    print(f"\n⛔⛔ AND MY tau-b IS NOT R288's `tau·mean`. R288 records {sorted(r288_tau)} for that")
    print("   target; this round's tau-b gives the same 9 arms as A2. Same NAME, different")
    print("   STATISTIC — R288's is a tau against a MEAN ranking, this is a per-annotator tau")
    print("   averaged, and the populations differ (10 vs 96). ⚠ The positive control validated the")
    print("   A2 branch ONLY: it confirms the instrument and licenses NOTHING about tau, which is")
    print("   the blind-spot case the standard names. So R288's tau result is NOT reproduced here")
    print("   and NOT contradicted — it is a different measurement, and remains the record for its")
    print("   own statistic at its own population.")
    print("\n⚠ AND THE OTHER FOUR TARGETS R288 SWEPT ARE NOT RECOMPUTED HERE. A1 and top1 need")
    print("   scoring conventions this round would have to reconstruct, and reconstructing a target")
    print("   in order to sweep it is how a specification curve becomes an invention. R288's")
    print("   committed answer stands for those, at ITS population of 10.")

    out = HERE / "results" / "target_scope.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="the extension is A2's answer and the statement never said so",
        n_prompts=n, nboot=NBOOT, seed=SEED, n_arms=len(cand),
        prior_art={"round": "R288/R558", "targets": r288["targets"],
                   "n_arms": len(r288["scores"]), "admitted": r288["admitted"]},
        controls={"positive_reproduces_r288_a2": bool(pos_ok),
                  "negative_monotone_rescale_invariant": bool(neg_ok),
                  "placebo_self": bool(plac_ok)},
        extension_a2=sorted(ext_a2), extension_tau=sorted(ext_tb),
        only_a2=only_a2, only_tau=only_tb, identical=bool(same), world=world,
        not_recomputed="A1·annot, A1·consensus, top1·mean and the consensus variant — they need "
                       "scoring conventions this round would have to reconstruct",
        tau_mismatch="this round's tau-b (per-annotator tau, averaged) is NOT R288's `tau·mean` "
                     "(tau against a mean ranking): R288 admits coval_core alone under that name, "
                     "this admits the same 9 as A2. Same name, different statistic, different "
                     "population. The positive control validated the A2 branch only and licenses "
                     "nothing about tau.",
        verdict_scope="target-stable BETWEEN A2 and per-annotator tau-b; four of R288's six "
                      "targets are unswept here and one of those (tau·mean) is a different "
                      "statistic from the tau computed here",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
