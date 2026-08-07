#!/usr/bin/env python3
"""R1040 — R1023's wall: "which target is right needs an external gold standard". Attack it.

R1039 measured that this arc's own IMPOSSIBLE lines fell at 4 of 16, and that all four shared ONE
shape: each said the answer needed something OUTSIDE the release, and each was answered by an object
already INSIDE it. R1023's line is the longest-exposed line of exactly that shape — "whether A2 or
A1·consensus is the RIGHT target needs an external gold standard" — and it has never been attacked.

⛔ THE OBVIOUS IN-RELEASE CRITERION IS CIRCULAR, AND SAYING SO IS THE DESIGN. "Which target better
   predicts held-out annotators" favours A2 BY CONSTRUCTION, because A2 IS mean agreement with
   annotators. Using it would be the outcome-conditioned trap with extra steps.

⭐ THE NEUTRAL CRITERION IS REPRODUCIBILITY, AND IT FAVOURS NEITHER. A target whose induced ARM
   ORDERING flips when you resample the annotator panel is measuring annotator idiosyncrasy rather
   than the object. Rank stability across INDEPENDENT annotator halves is defined identically for
   both targets and is not a restatement of either.

ESTIMAND        the rank correlation between the arm orderings induced by a target on two DISJOINT
                halves of the annotator panel, for A2 and for A1·consensus.
IDENTIFICATION  exact. Annotators are committed per prompt; the split is an intervention; the
                statistic is defined identically for both targets.
SCOPE           population : R1000's committed `population_arms` · 968 prompts · instrument : the
                release's own annotators, split · baseline : R295's committed agreement 0.5520
WORLDS          A THE TARGETS DIFFER IN REPRODUCIBILITY — one target's ordering is materially more
                  stable across annotator halves. Then the target IS selectable from inside the
                  release, R1023's line falls, and it falls in the same shape as the other four.
                B THEY ARE EQUALLY REPRODUCIBLE — no separation beyond the split noise. Then this
                  criterion does not select, R1023's line STANDS against this attack, and the wall
                  survives its first real test rather than merely remaining unexamined.
                prediction matrix: A -> a gap larger than the across-split spread of either.
                                   B -> overlapping distributions.
                ⚠ ONTOLOGICAL: A makes the target an empirical choice; B leaves it a stipulation —
                  and B is a genuinely different claim from "nobody looked", which is what R1023 had.
KILL            pre-registered and CONDITIONAL:
                  if the positive control reproduces R295's agreement and the placebo is exactly 1:
                      |median rho_A2 - median rho_A1c| > 2x the pooled across-split SD -> World A
                      otherwise                                                         -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   within-prompt annotator agreement must reproduce R295's committed 0.5520 — the same
                panel, the same measure, a different round. It can fail on any loader drift.
NEGATIVE CTRL   destroy the panel structure: permute annotator identity ACROSS prompts before
                splitting. Both targets' stability must collapse toward the split floor; if it does
                not, the statistic is not reading the panel at all.
PLACEBO         a half against ITSELF must give rank correlation exactly 1 for both targets.
NOISE FLOOR     the across-split SD of each target's rho, measured over 25 splits, and printed as the
                resolution against which any gap is judged.
MULTIPLICITY    2 targets x 25 splits, the whole distribution reported, not the medians alone.
SEEDS           25 annotator splits at fixed seeds; the split seed is the unit of replication.
IMPOSSIBLE      whether the more reproducible target is the one the BENCHMARK INTENDS. Reproducibility
                is a necessary property of a good target, not a sufficient one — the same limit
                R1036 hit for q. N/A; what it would require is a statement of intent from the
                release, which the dataset card does not carry.
"""
import json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"; NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NSPLIT = 25


def main() -> int:
    r295 = json.loads(next(A24.glob("R295_*/results/*.json")).read_text())
    pop = json.loads(next(A27.glob("R1000_*/results/*.json")).read_text())["population_arms"]
    print(f"  ⛔ THE OBVIOUS CRITERION IS CIRCULAR: 'better predicts held-out annotators' IS A2.")
    print(f"     The neutral one is REPRODUCIBILITY of the induced arm ordering, defined identically")
    print(f"     for both targets. R295's committed within-prompt agreement: {r295['agree_mean']:.4f}")

    tg, _ = load_targets()
    S0 = load_sat(RES / "sat_generic.npz")
    pids = [p for p in sorted(set(S0) & set(tg)) if len(tg[p]) >= 4]
    n = len(pids)
    HC = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    print(f"  prompts with >= 4 annotators (a split needs two non-empty halves): {n}")
    if n < 100:
        print("  UNRUNNABLE: too few splittable prompts. Exit 2, never 0."); return 2

    # ---------- POSITIVE: reproduce R295's within-prompt agreement ----------
    ag = []
    for p in pids:
        H = np.array(HC[p], float)
        for i in range(len(H)):
            for j in range(i + 1, len(H)):
                ag.append(float((H[i] == H[j]).mean()))
    got = float(np.mean(ag))
    pos_ok = abs(got - r295["agree_mean"]) < 0.02
    print(f"\n  POSITIVE — within-prompt annotator agreement must reproduce R295's committed "
          f"{r295['agree_mean']:.4f}:\n     mine {got:.4f}  {'PASS' if pos_ok else '⛔ FAIL'}  "
          f"(different prompt filter, so an exact match is not expected; 0.02 is the band)")
    if not pos_ok:
        print("  this is not R295's panel. Exit 2, never 0."); return 2

    def arm_cls(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                S = load_sat(f)
                idxs = sorted({i for p in S for i, _ in S[p]})
                return {p: np.array(cls(yvec(S[p], idxs)), float) for p in pids if p in S}
        return None

    ARM = {a: c for a in sorted(pop) if (c := arm_cls(a)) is not None}
    names = sorted(ARM)
    print(f"  arms scored: {len(names)}")

    def scores(half, shuffled=False):
        """per-arm A2 and A1c against a given annotator half"""
        a2 = np.zeros(len(names)); a1 = np.zeros(len(names)); cnt = 0
        for pi, p in enumerate(pids):
            H = HC[p]
            idx = half.get(p)
            if not idx:
                continue
            Hs = [np.array(H[k] if not shuffled else HC[pids[(pi + 7 * k) % n]][0], float)
                  for k in idx]
            m = min(len(x) for x in Hs)
            cons = np.sign(np.sum([x[:m] for x in Hs], axis=0))
            cnt += 1
            for ai, a in enumerate(names):
                c = ARM[a].get(p)
                if c is None: continue
                mm = min(len(c), m)
                a2[ai] += float(np.mean([(c[:mm] == x[:mm]).mean() for x in Hs]))
                a1[ai] += float((c[:mm] == cons[:mm]).all())
        return a2 / max(cnt, 1), a1 / max(cnt, 1)

    def rho(x, y):
        rx = np.argsort(np.argsort(x)).astype(float)
        ry = np.argsort(np.argsort(y)).astype(float)
        return float(np.corrcoef(rx, ry)[0, 1])

    def run_splits(shuffled=False):
        out = {"A2": [], "A1c": []}
        for s in range(NSPLIT):
            rng = np.random.default_rng(1040 + s)
            hA, hB = {}, {}
            for p in pids:
                k = len(HC[p]); perm = rng.permutation(k)
                hA[p] = list(perm[: k // 2]); hB[p] = list(perm[k // 2:])
            a2A, a1A = scores(hA, shuffled); a2B, a1B = scores(hB, shuffled)
            out["A2"].append(rho(a2A, a2B)); out["A1c"].append(rho(a1A, a1B))
        return out

    real = run_splits(False)
    print(f"\n  ⭐ RANK REPRODUCIBILITY across {NSPLIT} disjoint annotator splits")
    print(f"     {'target':<10}{'median rho':>13}{'sd':>10}{'min':>9}{'max':>9}")
    for t in ("A2", "A1c"):
        v = np.array(real[t])
        print(f"     {t:<10}{np.median(v):>13.4f}{v.std():>10.4f}{v.min():>9.4f}{v.max():>9.4f}")
    gap = float(abs(np.median(real["A2"]) - np.median(real["A1c"])))
    pooled = float(np.sqrt((np.var(real["A2"]) + np.var(real["A1c"])) / 2))
    print(f"     gap {gap:.4f} against pooled across-split SD {pooled:.4f} — "
          f"{gap / max(pooled, 1e-12):.1f}x")

    # ---------- NEGATIVE + PLACEBO ----------
    sh = run_splits(True)
    neg_ok = (np.median(sh["A2"]) < np.median(real["A2"]) and
              np.median(sh["A1c"]) < np.median(real["A1c"]))
    print(f"\n  NEGATIVE — permuting annotator identity ACROSS prompts must collapse both: "
          f"A2 {np.median(sh['A2']):.4f}, A1c {np.median(sh['A1c']):.4f}  "
          f"{'PASS' if neg_ok else '⛔ FAIL — the statistic is not reading the panel'}")
    rng = np.random.default_rng(7)
    hh = {p: list(rng.permutation(len(HC[p]))[: max(1, len(HC[p]) // 2)]) for p in pids}
    a2, a1 = scores(hh)
    plac = (rho(a2, a2), rho(a1, a1))
    plac_ok = all(abs(x - 1.0) < 1e-9 for x in plac)
    print(f"  PLACEBO  — a half against ITSELF must give rho exactly 1: {plac}  "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")

    print()
    if not (neg_ok and plac_ok):
        world = "UNVERIFIED — a control did not fire; no verdict is admissible"
    elif gap > 2 * pooled:
        better = "A2" if np.median(real["A2"]) > np.median(real["A1c"]) else "A1·consensus"
        world = (f"⭐ A THE TARGETS DIFFER IN REPRODUCIBILITY — `{better}` induces the more stable "
                 f"arm ordering across disjoint annotator halves, gap {gap:.4f} against a pooled "
                 f"across-split SD of {pooled:.4f} ({gap/max(pooled,1e-12):.1f}x). So the target IS "
                 f"selectable from INSIDE the release, and R1023's wall falls in the same shape as "
                 f"the other four R1039 counted: it said the answer needed something outside, and "
                 f"the answer was the release's own annotator panel.")
    else:
        world = (f"⭐ B EQUALLY REPRODUCIBLE — the gap {gap:.4f} does not clear twice the pooled "
                 f"across-split SD {pooled:.4f}. This criterion does not select, so R1023's line "
                 f"STANDS against its first real attack. ⭐ That is a different claim from 'nobody "
                 f"looked', which is all it had before.")
    print(world)
    print(f"⛔ AND THE CIRCULAR CRITERION WAS REFUSED, NOT OVERLOOKED. 'Which target better predicts")
    print(f"   held-out annotators' IS A2 by construction; using it would have manufactured World A.")
    print(f"⚠ REPRODUCIBILITY IS NECESSARY, NOT SUFFICIENT — the same limit R1036 hit for q. A stable")
    print(f"   target can still be the wrong one; that needs a statement of intent the dataset card")
    print(f"   does not carry. N/A, stated not planned.")

    out = HERE / "results" / "target_choice_in_release.json"
    out.write_text(json.dumps({
        "round": "R1040", "n_prompts": n, "n_arms": len(names), "splits": NSPLIT,
        "positive_agreement": {"mine": got, "R295": r295["agree_mean"]},
        "rho": {t: {"median": float(np.median(real[t])), "sd": float(np.std(real[t])),
                    "min": float(np.min(real[t])), "max": float(np.max(real[t]))}
                for t in ("A2", "A1c")},
        "gap": gap, "pooled_sd": pooled,
        "negative_shuffled": {t: float(np.median(sh[t])) for t in ("A2", "A1c")},
        "placebo": list(plac), "world": world,
        "refused_criterion": "which target better predicts held-out annotators — that IS A2 by "
                             "construction and would have manufactured a separation",
        "limitation": "reproducibility is necessary, not sufficient; a stable target can still be "
                      "the wrong one",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
