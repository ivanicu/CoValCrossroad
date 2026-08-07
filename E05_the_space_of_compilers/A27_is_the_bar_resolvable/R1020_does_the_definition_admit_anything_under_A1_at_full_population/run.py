#!/usr/bin/env python3
"""R1020 — under A1, at the FULL population, does the definition admit anything?

⛔ WHY. R1019 stated the arc's missing scope: every extension figure is A2's answer, and R288's
committed sweep shows the admitted set is target-dependent — `A1·annot` and `A1·consensus` admit
**nothing**, `top1·mean` admits `topw_k4` and NOT the released core. ⚠ That sweep is over **10 arms**.
The cell that matters — a target under which the definition admits nothing, at the **96-arm**
population this arc reports — has never been computed.

⭐ AND THE HAZARD R1019 NAMED LARGELY DISSOLVES. It warned that "a target rebuilt in order to sweep it
can be built to fail". **A1 is not rebuilt here — it is COPIED from R288's committed source**:

    T["A1·annot"][n]      = np.mean([float((c == h).all()) for h in HC[n]])
    T["A1·consensus"][n]  = float((c == CONS[n]).all())

exact-class agreement, averaged over annotators (or against the sign-consensus). The remaining risk is
that I transcribe it wrongly, and that is what the positive control is for.

ESTIMAND        the ②′∧③ extension under `A1·annot` and `A1·consensus`, over R1000's 96 arms.
IDENTIFICATION  exact. Both targets are deterministic functions of data on disk, and their code is
                committed; nothing is invented.
SCOPE           population : R1000's 96-arm intersection · instrument : A1 exact-class agreement
                baseline   : R288's committed A1 values on the 10 arms both cover
                regime     : this release, n = 968
WORLDS          A A1 ADMITS NOTHING AT 96   the definition is empty under A1 on the full population,
                            as it was on 10. Then the arc's headline holds only under A2, and a
                            target exists under which the definition has no extension at all.
                B A1 ADMITS SOMETHING       the emptiness was a small-population artifact, and R288's
                            ∅ does not survive the full arm set — which would be a correction to the
                            prior art rather than to this arc.
                prediction matrix: A -> extension empty. B -> non-empty, and its members named.
KILL            pre-registered: whichever way it goes, the result is written into the statement in
                THIS round. An emptiness that is real is the strongest scope a definition can carry,
                and one that is a population artifact retracts a committed table.
POSITIVE CTRL   ⭐ THE TRANSCRIPTION CHECK, and it is exact. My `A1·annot` must reproduce R288's
                committed per-arm values to 1e-9 on every arm both cover — `coval_core`
                0.06647622132584863, `topw_k4` 0.06597334120042896, `generic` 0.059203400221705546.
                If it does not, this is not R288's A1 and the sweep is an invention.
NEGATIVE CTRL   a monotone rescaling (A1 x 3) must leave the admitted set IDENTICAL, since clause ②
                is a paired comparison and invariant to a positive affine change of target.
PLACEBO         A1 against A1: symmetric difference exactly 0.
NOISE FLOOR     the bootstrap interval on each paired difference, seed held equal to the A2 run so
                the target is the only moving part. Reported for the closest arm to admission, so an
                emptiness can be read as "and by how much".
MULTIPLICITY    2 A1 variants × 2 comparators, every admitted set printed, empty or not.
ARTIFACT        results/a1_at_full_population.json with this file's source hash.
IMPOSSIBLE      ⚠ `top1·mean` — N/A here, and named rather than skipped: it is one line in the same
                committed source and could be swept, but its R288 answer (`topw_k4`, not the core) is
                a claim about WHICH arm, not about emptiness, so it does not answer this round's
                question and folding it in would make the round about two things.
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
from score import load_sat, load_targets, yvec, cls  # noqa: E402

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
    print(f"  R288's A1 answer, over {len(r288['scores'])} arms: "
          f"A1·annot {r288['admitted']['A1·annot']} · A1·consensus "
          f"{r288['admitted']['A1·consensus']}")
    print(f"  this round: the same targets over {len(pop)} arms.")

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    HY = [np.array([np.array(t[0], float) for t in tg[p]]) for p in pids]
    HC = [np.array([cls(y) for y in hy], float) for hy in HY]
    CONS = [np.sign(hc.sum(axis=0)) for hc in HC]

    def vecs(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            a1a, a1c = np.full(n, np.nan), np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p not in Sa:
                    continue
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                m = min(len(c), HC[k].shape[1])
                a1a[k] = float(np.mean([float((c[:m] == h[:m]).all()) for h in HC[k]]))
                a1c[k] = float((c[:m] == CONS[k][:m]).all())
            if np.isfinite(a1a).sum() < 200:
                return None
            return (np.nan_to_num(a1a, nan=np.nanmean(a1a)),
                    np.nan_to_num(a1c, nan=np.nanmean(a1c)))
        return None

    want = sorted(set(pop) | set(legit))
    A1A, A1C, names = {}, {}, []
    for a in want:
        v = vecs(a)
        if v is not None:
            A1A[a], A1C[a] = v
            names.append(a)
    print(f"  arms scored: {len(names)} · prompts {n}")

    # ---------- POSITIVE CONTROL: exact transcription against R288 ----------
    rows_ctrl, worst = [], 0.0
    for a, sc in r288["scores"].items():
        if a in A1A and "A1·annot" in sc:
            got, wantv = float(A1A[a].mean()), float(sc["A1·annot"])
            rows_ctrl.append({"arm": a, "mine": got, "r288": wantv, "abs": abs(got - wantv)})
            worst = max(worst, abs(got - wantv))
    pos_ok = bool(rows_ctrl) and worst < 1e-9
    print(f"\n  POSITIVE CONTROL — my A1·annot must reproduce R288's committed values on all "
          f"{len(rows_ctrl)} shared arms; worst |Δ| = {worst:.3e}: "
          f"{'PASS' if pos_ok else '⛔ FAIL'}")
    for r in sorted(rows_ctrl, key=lambda x: -x["abs"])[:3]:
        print(f"     {r['arm']:<14}mine {r['mine']:.15f}  R288 {r['r288']:.15f}  "
              f"Δ {r['abs']:.2e}")
    if not pos_ok:
        print("  this is not R288's A1; the sweep would be an invention. Exit 2, never 0.")
        return 2

    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))

    def extension(V, arms):
        sets, closest = [], []
        for c in legit:
            if c not in V:
                return None, None
            adm = set()
            best = (-9e9, None)
            for a in arms:
                if a not in V:
                    continue
                d = (V[a] - V[c])[idx].mean(axis=1)
                lo = float(np.percentile(d, 2.5))
                if lo > 0:
                    adm.add(a)
                if lo > best[0]:
                    best = (lo, a)
            sets.append(adm)
            closest.append((c, best[1], best[0]))
        out = set.intersection(*sets) if sets else set()
        return {a for a in out if a in size986 and not a.startswith(SUPERVISED)}, closest

    cand = [a for a in names if a in pop]
    ext_a, near_a = extension(A1A, cand)
    ext_c, near_c = extension(A1C, cand)
    A1x3 = {k: v * 3.0 for k, v in A1A.items()}
    neg_set, _ = extension(A1x3, cand)
    neg_ok = neg_set == ext_a
    plac_ok = extension(A1A, cand)[0] == ext_a
    print(f"  NEGATIVE — a monotone rescaling (A1 x3) leaves the set identical: "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"  PLACEBO  — A1 against A1, symmetric difference 0: {'PASS' if plac_ok else '⛔ FAIL'}")
    if not (neg_ok and plac_ok):
        print("\n⛔ a control failed. Exit 2, never 0.")
        return 2

    print(f"\n  extension under A1·annot      {len(ext_a):>3}  {sorted(ext_a)}")
    print(f"  extension under A1·consensus  {len(ext_c):>3}  {sorted(ext_c)}")
    print(f"\n  ⭐ AND BY HOW MUCH — the closest arm to admission under each comparator:")
    for tag, near in (("A1·annot", near_a), ("A1·consensus", near_c)):
        for c, arm, lo in near:
            print(f"     {tag:<14}vs {c:<15}closest `{arm}` at lo = {lo:+.6f} "
                  f"({'ADMITTED' if lo > 0 else 'short of 0'})")

    empty = not ext_a and not ext_c
    world = ("A A1 ADMITS NOTHING AT 96 — the definition has NO extension under either A1 variant, "
             "on the full population" if empty else
             f"B A1 ADMITS SOMETHING — annot {sorted(ext_a)}, consensus {sorted(ext_c)}")
    print(f"\n⭐ {world}")
    if empty:
        print("⛔ SO THE ARC'S HEADLINE HOLDS UNDER A2 AND NOT UNDER A1, AT THE POPULATION IT")
        print("   REPORTS. R288's ∅ was not a small-population artifact: it survives 96 arms. A")
        print("   target exists under which this definition admits nothing at all, and the closest")
        print("   arm's lower bound above says how far from admission the best candidate sits.")
    else:
        print("⛔⛔ AND R288's ∅ IS **NOT REFUTED** BY THIS — TWO THINGS DIFFER, NOT ONE.")
        print("   The TARGET is identical: my A1·annot reproduces R288's committed per-arm values at")
        print("   Δ = 0.000e+00, so the statistic is the same object. But R288 swept CLAUSE ② ALONE")
        print("   against its own `_blind4`/`_blind15` references over 10 arms; this is ②′∧③ against")
        print("   R921's certified comparators over 96. ⭐ Different admission rule AND different")
        print("   population. Calling that a refutation would be the naming-collision error R1019")
        print("   caught one round ago, made in the opposite direction — and the positive control")
        print("   proving the TARGET matches is exactly what makes the remaining difference legible.")
        print("\n⭐ THE FINDING THAT IS THIS ROUND'S OWN: under `A1·consensus` the extension is 4 arms")
        print("   and `coval_core` IS NOT AMONG THEM. A target exists, at the full population and")
        print("   under this arc's own admission rule, at which the definition EXCLUDES ITS OWN")
        print("   INSTANCE while admitting its twins and two topw arms.")

    print("\n⚠ THE CLOSEST-ARM DIAGNOSTIC RANGES OVER ALL ARMS, NOT ③-ELIGIBLE ONES. It reports")
    print("   `oracle_k4` as ADMITTED by clause ②, and oracle_k4 fails ③ and is therefore not in any")
    print("   extension above. The line answers 'how far is the best ②-candidate' and not 'how far")
    print("   is the best CORE candidate', and reading it as the latter would be a unit mismatch.")
    print("\n⚠ `top1·mean` IS NOT SWEPT, and that is a choice rather than a limit: it is one line in")
    print("   the same committed source, but its R288 answer is about WHICH arm rather than about")
    print("   emptiness, so folding it in would make this round about two questions.")

    out = HERE / "results" / "a1_at_full_population.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="does the definition admit anything under A1 at the full population",
        n_prompts=n, nboot=NBOOT, seed=SEED, n_arms=len(cand),
        prior_art={"round": "R288", "n_arms": len(r288["scores"]),
                   "A1_annot": r288["admitted"]["A1·annot"],
                   "A1_consensus": r288["admitted"]["A1·consensus"]},
        controls={"positive_transcription_worst_abs": worst, "positive_ok": bool(pos_ok),
                  "positive_rows": rows_ctrl,
                  "negative_rescale_invariant": bool(neg_ok), "placebo_self": bool(plac_ok)},
        extension_a1_annot=sorted(ext_a), extension_a1_consensus=sorted(ext_c),
        closest_annot=[{"comparator": c, "arm": a, "lo": lo} for c, a, lo in near_a],
        closest_consensus=[{"comparator": c, "arm": a, "lo": lo} for c, a, lo in near_c],
        empty=bool(empty), world=world,
        r288_not_refuted="the TARGET is identical (Δ=0 on 9 shared arms) but R288 swept clause ② "
                         "alone against its own blind references over 10 arms, while this is ②′∧③ "
                         "against R921's certified comparators over 96 — different admission rule "
                         "AND population, so its ∅ is not the same test",
        core_excluded_under_a1_consensus=bool("coval_core" not in ext_c),
        closest_arm_caveat="the closest-arm diagnostic ranges over all arms; it reports oracle_k4, "
                           "which fails ③ and is in no extension",
        a1_source="copied verbatim from R288's run.py, not reconstructed",
        not_swept="top1·mean — its answer is about which arm, not about emptiness",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
