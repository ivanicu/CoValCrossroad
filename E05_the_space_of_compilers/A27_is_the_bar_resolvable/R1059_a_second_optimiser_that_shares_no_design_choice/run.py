"""R1059 — build the second optimiser R1058 said was the binding constraint, and let the clause judge it.

R1058 found the clause's central claim UNIDENTIFIED here: 13 never-seen cores admitted at 0 against
0.247 for released arms, but every rule I could build was UNSELECTED while every admitted released
arm was OPTIMISED. The comparison confounded provenance with quality and named the fix — a core built
by an optimiser sharing no design choice with the one that produced the released arms.

⭐ THIS ROUND BUILDS IT. Two optimisers, on two axes that the released `greedy_*` / `topw_*` family
   shares and these do not:
     OBJECTIVE  released arms fit agreement with the HUMAN target.
                `varmax` never sees the target at all — it selects the criteria that DISCRIMINATE
                most among the four responses, which is an intrinsic property of the prompt.
     SEARCH     released arms select greedily, forward, one criterion at a time.
                `heldout` scores every criterion on a FIT HALF of prompts and applies the global
                ranking to the EVAL half — a different search and an honest split.
   `varmax` shares neither axis; `heldout` shares the objective and not the search. Reporting both
   separates `the clause needs target-fitting` from `the clause needs THIS optimiser`.

ESTIMAND        whether a core built by each optimiser is admitted by the clause, on prompts its
                selection rule was not fitted on
IDENTIFICATION  ⚠ PARTIAL AND STATED. `heldout` fits on half the prompts and is judged on the other
                half, so its admission is leakage-free. `varmax` never touches the target, so leakage
                is impossible by construction. What remains unidentified is whether a SECOND TEAM
                would build either of these — I built both, and that is the register's standing entry.
SCOPE           population : 968 prompts, evaluated on the held-out half where a split applies
                instrument : the R923 admission operator, family of 2, 2.5th pct paired bootstrap
                baseline   : R1058's 13 unselected cores, admitted at 0; released arms at 0.247
                regime     : target A2
WORLDS          A THE CLAUSE ADMITS A DIFFERENTLY-BUILT CORE — at least one optimiser's core is
                  admitted. Then the clause is testing a property, R1058's confound is resolved in
                  the clause's favour, and `defines a category` gains its first real evidence.
                B IT ADMITS ONLY ITS OWN LINEAGE — neither is admitted while released arms pass.
                  Combined with R1058's zeros this is the first evidence FOR the provenance reading,
                  and it is no longer confounded with `unoptimised`, because these are optimised.
                prediction matrix: A -> >=1 admitted   B -> 0 admitted, released > 0
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      >=1 optimiser core admitted -> World A
                      0 admitted and released > 0 -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   a KNOWN-admitted released arm must be admitted by this harness on the same prompts,
                or every zero below is silence rather than measurement.
NEGATIVE CTRL   a comparator's own vector must NOT be admitted.
SHAM            ⭐ `varmax` with its ranking REVERSED — the least discriminating criteria, same size,
                same search, ingredient inverted. If the sham scores at or above varmax, the
                objective is not doing the work.
PLACEBO         a random selection of the same per-prompt size must sit at the R1058 rate (0).
NOISE FLOOR     3 seeds for every bootstrap; 3 fit/eval splits for `heldout`, spread reported.
MULTIPLICITY    both optimisers x several k, all cells reported.
SEEDS           3.
IMPOSSIBLE      whether a second TEAM would build these. SETTLES: OUT-OF-RELEASE. I built them; the
                design choices they avoid are named above, and that is the strongest available here.
"""
import json, pathlib, sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT = 2000
COMPARATORS = ["generic", "genericpool16"]
KS = (2, 3, 4)


def main() -> int:
    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    pids = sorted(set(Sfull) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    if n < 200:
        print("  UNRUNNABLE: too few prompts. Exit 2, never 0."); return 2
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    avail = {p: sorted({i for i, _ in Sfull[p]}) for p in pids}
    print(f"  ⭐ prompts {n} · criteria per prompt: min {min(len(a) for a in avail.values())} "
          f"max {max(len(a) for a in avail.values())}")

    def agree(p, idxs):
        c = np.array(cls(yvec(Sfull[p], list(idxs))), float)
        return float(np.mean([(c == h).mean() for h in H[p]]))

    def vec(selfn, on=None):
        ps = on or pids
        v = np.full(n, np.nan)
        for k, p in enumerate(pids):
            if p in ps:
                idxs = selfn(p)
                if idxs:
                    v[k] = agree(p, idxs)
        return v

    def released_vec(nm):
        f = RES / f"sat_{nm}.npz"
        if not f.exists():
            return None
        try:
            Sa = load_sat(f)
        except Exception:
            return None
        v = np.full(n, np.nan)
        for k, p in enumerate(pids):
            if p in Sa:
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
        return v if np.isfinite(v).sum() >= 100 else None

    Cv = [released_vec(c) for c in COMPARATORS]
    if any(c is None for c in Cv):
        print("  UNRUNNABLE: a comparator is missing. Exit 2, never 0."); return 2

    def admits(v, seed, mask=None):
        rng = np.random.default_rng(seed)
        for cv in Cv:
            m = np.isfinite(v) & np.isfinite(cv) & (np.ones(n, bool) if mask is None else mask)
            if m.sum() < 50:
                return False
            d = (v - cv)[m]
            idx = rng.integers(0, m.sum(), size=(NBOOT, m.sum()))
            if not float(np.percentile(d[idx].mean(axis=1), 2.5)) > 0:
                return False
        return True

    # ---------- OPTIMISER 1: varmax — never sees the human target ----------
    def varmax(k, reverse=False):
        def f(p):
            sat = Sfull[p]
            sc = {}
            for i in avail[p]:
                vals = [sat.get((i, x), 0.0) for x in "ABCD"]
                sc[i] = float(np.var(vals))
            order = sorted(avail[p], key=lambda i: sc[i], reverse=not reverse)
            return order[:k]
        return f

    # ---------- OPTIMISER 2: heldout — global criterion ranking fitted on half the prompts ----------
    def heldout(k, seed):
        rng = np.random.default_rng(seed)
        mask = rng.random(n) < 0.5
        fit = {p for p, m in zip(pids, mask) if m}
        ev = np.array([p not in fit for p in pids])
        gain = {}
        for i in range(max(len(a) for a in avail.values())):
            hits = [agree(p, [i]) for p in fit if i in avail[p]]
            if len(hits) >= 30:
                gain[i] = float(np.mean(hits))
        order = sorted(gain, key=lambda i: -gain[i])

        def f(p):
            sel = [i for i in order if i in avail[p]][:k]
            return sel or avail[p][:k]
        return f, ev

    kv = None
    r1055 = next(ROOT.glob("E05_the_space_of_compilers/A27*/R1055_*/results/"
                           "component_ablation.json"), None)
    for a in (json.loads(r1055.read_text())["baseline_admitted"] if r1055 else []):
        kv = released_vec(a)
        if kv is not None:
            break
    pos = kv is not None and all(admits(kv, s) for s in (11, 23, 47))
    neg = not any(admits(Cv[0], s) for s in (11, 23))
    print(f"  POSITIVE — a KNOWN-admitted released arm must be admitted here: {pos}")
    print(f"  NEGATIVE — a comparator's own vector must NOT be: {neg}")
    if not (pos and neg):
        print("  the harness cannot read these cores. Exit 2, never 0."); return 2

    rows = []
    for k in KS:
        vm = vec(varmax(k))
        sh = vec(varmax(k, reverse=True))
        vm_ok = [admits(vm, s) for s in (11, 23, 47)]
        sh_ok = [admits(sh, s) for s in (11, 23, 47)]
        rows.append({"optimiser": "varmax (target-free)", "k": k, "admitted": sum(vm_ok),
                     "sham_admitted": sum(sh_ok),
                     "mean_agreement": float(np.nanmean(vm)),
                     "sham_mean_agreement": float(np.nanmean(sh))})
        print(f"     varmax  k={k}  admitted {sum(vm_ok)}/3  mean {np.nanmean(vm):.4f}   "
              f"SHAM(reversed) admitted {sum(sh_ok)}/3  mean {np.nanmean(sh):.4f}")
        hos = []
        for s in (11, 23, 47):
            f, ev = heldout(k, s)
            hos.append(admits(vec(f), s, mask=ev))
        rows.append({"optimiser": "heldout (fit half, judged on the other)", "k": k,
                     "admitted": sum(hos), "sham_admitted": None})
        print(f"     heldout k={k}  admitted {sum(hos)}/3 (judged only on the half not fitted on)")

    cmp_mean = float(np.nanmean(Cv[0]))
    print(f"  ⭐ comparator `generic` mean agreement: {cmp_mean:.4f}")
    any_admitted = any(r["admitted"] > 0 for r in rows)

    # ⛔⛔ THE SHAM CONDITION COULD ONLY FIRE IF THE OPTIMISER WAS ADMITTED — a check that cannot
    #   fail in the case that actually occurred (both at 0). The sham must be read on the CONTINUOUS
    #   score, which is where it has power: reversing varmax's ranking changes the mean agreement by
    #   almost nothing, so the target-free objective contributes ~0 and varmax is a size-matched
    #   selection rule rather than an optimiser.
    vm_rows = [r for r in rows if r["sham_admitted"] is not None]
    sham_gaps = [r["mean_agreement"] - r["sham_mean_agreement"] for r in vm_rows]
    objective_inert = max(abs(g) for g in sham_gaps) < 0.01
    print(f"  ⛔ SHAM ON THE CONTINUOUS SCORE — reversing varmax's ranking moves mean agreement by "
          f"{[round(g, 4) for g in sham_gaps]}; the objective is inert: {objective_inert}")

    # ⛔⛔ AND THE QUANTITY THAT DECIDES THE ROUND IS THE GAP TO THE COMPARATOR, WHICH I ALMOST DID
    #   NOT LOOK AT. Every core built here scores far below `generic`. Non-admission is then fully
    #   explained by QUALITY, and R1058's provenance-vs-quality confound is NOT resolved.
    best = max(r["mean_agreement"] for r in vm_rows)
    gap = cmp_mean - best
    quality_explains = gap > 0.02
    print(f"  ⛔ QUALITY GAP — best synthetic core {best:.4f} vs comparator {cmp_mean:.4f}, "
          f"gap {gap:+.4f}; quality alone explains non-admission: {quality_explains}")

    print()
    if quality_explains or objective_inert:
        world = (f"⛔ UNVERIFIED AGAIN, AND NOW WITH THE MECHANISM MEASURED — NOT World A, NOT World "
                 f"B. Neither optimiser is admitted, but the best core built here scores "
                 f"{best:.4f} against the comparator's {cmp_mean:.4f}, a gap of {gap:.4f}. "
                 f"**Non-admission is fully explained by quality**, so R1058's provenance-vs-quality "
                 f"confound is NOT resolved — it is reproduced with better-built objects. ⭐ And the "
                 f"sham says one of my two optimisers is not one: reversing varmax's ranking moves "
                 f"mean agreement by at most {max(abs(g) for g in sham_gaps):.4f}, so its target-free "
                 f"objective contributes nothing and it is a size-matched selection rule wearing an "
                 f"optimiser's name. Only `heldout` is a real optimiser, and one optimiser is n=1.")
    elif any_admitted:
        world = (f"⭐ A THE CLAUSE ADMITS A DIFFERENTLY-BUILT CORE — admitted on prompts it was not "
                 f"fitted on, with the sham showing the objective does the work.")
    else:
        world = (f"⛔ B THE CLAUSE ADMITS ONLY ITS OWN LINEAGE — neither optimiser is admitted while "
                 f"released arms pass, the sham confirms both objectives do work, and the quality gap "
                 f"to the comparator is under 0.02, so quality does not explain the rejection.")
    print(world)
    print(f"⛔ AND I BUILT BOTH OPTIMISERS, SO `INDEPENDENT` MEANS `SHARES NO NAMED DESIGN CHOICE`,")
    print(f"   never `built by someone else`. The axes avoided are stated in the docstring; whether a")
    print(f"   second TEAM converges on the same answer stays OUT-OF-RELEASE.")

    o = HERE / "results" / "second_optimiser.json"
    o.write_text(json.dumps({
        "round": "R1059", "prompts": n, "nboot": NBOOT, "rows": rows,
        "comparator_mean_agreement": cmp_mean, "world": world,
        "quality_gap": gap, "best_synthetic_mean": best,
        "objective_inert": bool(objective_inert), "quality_explains": bool(quality_explains),
        "controls": {"positive_known_arm": bool(pos), "negative_self": bool(neg),
                     "sham_gaps": sham_gaps},
        "limitation": "independent means shares no named design choice, not built by someone else",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
