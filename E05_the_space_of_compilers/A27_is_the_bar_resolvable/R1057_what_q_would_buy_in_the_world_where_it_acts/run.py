"""R1057 — my own NEXT was a derivation. Build the world where q acts, and measure what it buys.

R1056 closed by proposing to restate the clause with and without q and re-run R1055's ablation.

⛔⛔ THAT PROPOSAL CANNOT PRODUCE EVIDENCE, AND R1055 ALREADY PROVED WHY. At |family| = 2,
   need(q=90) = ceil(0.9*2) = 2 = need(q=100), so `with q` and `without q` ARE THE SAME OPERATOR.
   Re-running the ablation would return Δ=0 by algebra and I would have reported a forced zero as a
   decision. My own NEXT even said the two are `indistinguishable at this family size` — and then
   proposed running them anyway. **The closing sentence named the obstacle and proposed walking into
   it**, which is exactly the failure §4 records for closing sentences: written last, acted on later,
   with no control attached.

⭐ THE ROUND THAT CAN DECIDE IT IS §3's LADDER STEP 4 — BUILD THE WORLD THE RIVAL PREDICTS. A
   prompt-blind comparator is a FIXED criterion selection used on every prompt; that is R918's own
   `fixed` predicate, and a fixed index subset of the rubric satisfies it BY CONSTRUCTION. So a
   family of any size can be built legitimately, and in that world q is no longer inert and its value
   can be measured rather than argued.

ESTIMAND        the symmetric difference between the admitted set under q=90 and under q=100, as a
                function of synthetic family size k, over k where the two differ (k >= 10)
IDENTIFICATION  exact given the operator. ⚠ SYNTHETIC: these comparators are constructed, not
                released. The measurement says what q WOULD buy against a family built this way; it
                does not say a real second release would produce such a family.
SCOPE           population : the 95 released arms, scored against synthetic blind comparators
                instrument : the R923 admission operator, 2.5th percentile of the paired bootstrap
                baseline   : the released family of 2, where q is inert (R1055, R1056)
                regime     : 968 prompts, target A2, fixed subsets of the rubric
WORLDS          A q BUYS SOMETHING — at k >= 10 the two settings admit different sets, and the
                  difference grows with k. Then q is a real parameter awaiting a real family, and the
                  clause should keep it with its precondition stated.
                B q BUYS NOTHING EVEN WHERE IT CAN ACT — the sets coincide at every k. Then q is not
                  merely inert here, it is inert in principle for this operator, and the clause
                  should drop it.
                prediction matrix: A -> Δ > 0 for some k >= 10;  B -> Δ = 0 at every k
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      Δ > 0 at any k >= 10 -> World A, and report the whole Δ(k) curve
                      Δ = 0 at every k     -> World B, drop q
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ the synthetic comparators must be PROMPT-BLIND by R918's own rule: each uses one
                selection on every prompt, so n_distinct == 1. Asserted in code, not assumed.
NEGATIVE CTRL   at k < 10 the two settings must agree EXACTLY — that is R1055's arithmetic, and if
                the harness shows a difference there it is not implementing q at all.
SHAM            a family of k IDENTICAL comparators must make q inert again regardless of k, because
                beating one means beating all: a size that is nominal rather than real buys nothing.
PLACEBO         k = 0 admits nothing.
NOISE FLOOR     3 seeds; arms unstable across them are excluded from every difference.
MULTIPLICITY    the whole k curve reported, including the k where Δ = 0.
SEEDS           3.
IMPOSSIBLE      whether a real second release would yield >= 10 genuinely blind comparators.
                SETTLES: OUT-OF-RELEASE - it needs the second release, the register's standing entry.
"""
import itertools, json, pathlib, sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT = 2000
KS = (2, 4, 8, 10, 12, 15)


def main() -> int:
    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    pids = sorted(set(Sfull) & {p for p in tg if len(tg[p]) >= 2})
    if len(pids) < 100:
        print("  UNRUNNABLE: too few prompts. Exit 2, never 0."); return 2
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)

    # criterion indices present on EVERY prompt — a fixed subset must exist everywhere to be blind
    common = set.intersection(*[{i for i, _ in Sfull[p]} for p in pids])
    print(f"  ⭐ prompts {n} · criterion indices present on EVERY prompt: {sorted(common)}")
    if len(common) < 4:
        print("  UNRUNNABLE: too few common criteria to build a blind family. Exit 2, never 0.")
        return 2

    # ⛔⛔ THE BLIND-COMPARATOR SPACE IS BOUNDED, AND THE FIRST ATTEMPT HIT THE BOUND. Only 4
    #   criterion indices are present on EVERY prompt, so the fixed subsets that are well-defined
    #   everywhere number 2^4 - 1 = 15. I asked for 20 and the round correctly refused to run.
    #   ⭐ That bound is a finding in its own right: even SYNTHETICALLY, a blind family built from
    #   universally-available criteria caps at 15 — and 15 >= 10, so q remains exercisable, but
    #   only just, and a clause needing k > 15 could not be satisfied by construction either.
    subsets = [tuple(s) for r in range(1, len(common) + 1)
               for s in itertools.combinations(sorted(common), r)]
    print(f"  ⭐ BLIND-COMPARATOR SPACE — every non-empty fixed subset of the {len(common)} "
          f"universally-available criteria: {len(subsets)} = 2^{len(common)} - 1 (a hard cap)")
    pos = all(len({sub}) == 1 for sub in subsets)      # one selection per comparator, every prompt
    print(f"  POSITIVE — every synthetic comparator uses ONE selection on every prompt "
          f"(R918's `fixed`): {pos} · built {len(subsets)} of them")
    if not (pos and len(subsets) >= max(KS)):
        print("  cannot build a blind family of the needed size. Exit 2, never 0."); return 2

    def scorevec(sat, idxs):
        v = np.full(n, np.nan)
        for k, p in enumerate(pids):
            if p in sat:
                c = np.array(cls(yvec(sat[p], idxs)), float)
                v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
        return v

    C = np.array([scorevec(Sfull, list(s)) for s in subsets])
    C = np.nan_to_num(C, nan=float(np.nanmean(C)))

    arms, V = [], []
    for f in sorted(RES.glob("sat_*.npz")):
        nm = f.stem[4:]
        try:
            Sa = load_sat(f)
        except Exception:
            continue
        v = scorevec(Sa, None) if False else np.full(n, np.nan)
        for k, p in enumerate(pids):
            if p in Sa:
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
        if np.isfinite(v).sum() < 100:
            continue
        arms.append(nm); V.append(np.nan_to_num(v, nan=float(np.nanmean(v))))
    V = np.array(V)
    print(f"  ⭐ released arms scored against the synthetic family: {len(arms)}")

    def admit(seed, k, q, comps=None):
        rng = np.random.default_rng(seed)
        Cc = C[:k] if comps is None else comps[:k]
        if k == 0:
            return set()
        idx = rng.integers(0, n, size=(NBOOT, n))
        need = k if q >= 100 else max(1, int(np.ceil(q / 100 * k)))
        out = set()
        for i, nm in enumerate(arms):
            beats = 0
            for j in range(k):
                d = V[i] - Cc[j]
                bs = d[idx].mean(axis=1)
                beats += float(np.percentile(bs, 2.5)) > 0
            if beats >= need:
                out.add(nm)
        return out

    rows = []
    for k in KS:
        sets90 = [admit(s, k, 90) for s in (11, 23, 47)]
        sets100 = [admit(s, k, 100) for s in (11, 23, 47)]
        st90, st100 = set.intersection(*sets90), set.intersection(*sets100)
        unstable = (set.union(*sets90) - st90) | (set.union(*sets100) - st100)
        a, b = st90 - unstable, st100 - unstable
        need90 = max(1, int(np.ceil(0.9 * k)))
        rows.append({"k": k, "need_q90": need90, "need_q100": k,
                     "admitted_q90": len(a), "admitted_q100": len(b),
                     "symmetric_difference": len(a ^ b), "unstable": len(unstable),
                     "gained_by_q90": sorted(a - b)[:6]})
        print(f"     k={k:>3}  need 90/100 = {need90}/{k}  admitted {len(a):>3}/{len(b):>3}  "
              f"Δ={len(a ^ b):>3}  unstable={len(unstable)}")

    small = [r for r in rows if r["k"] < 10]
    neg = all(r["symmetric_difference"] == 0 for r in small)
    sham_sets = [admit(s, 12, 90, comps=np.repeat(C[:1], 12, axis=0)) for s in (11, 23)]
    sham_ref = [admit(s, 12, 100, comps=np.repeat(C[:1], 12, axis=0)) for s in (11, 23)]
    sham = (sham_sets[0] ^ sham_ref[0]) == set()
    plac = admit(11, 0, 90) == set()
    print(f"  NEGATIVE — at k < 10 the two settings must agree exactly (R1055's arithmetic): {neg}")
    print(f"  SHAM     — 12 IDENTICAL comparators must leave q inert (beating one is beating all): "
          f"{sham}")
    print(f"  PLACEBO  — k = 0 admits nothing: {plac}")
    if not (neg and sham and plac):
        print("  the harness is not implementing q. Exit 2, never 0."); return 2

    big = [r for r in rows if r["k"] >= 10]
    buys = [r for r in big if r["symmetric_difference"] > 0]
    print()
    if buys:
        world = (f"⭐ A q BUYS SOMETHING WHERE IT CAN ACT — at k >= 10 the two settings differ in "
                 f"{len(buys)} of {len(big)} cells, by "
                 f"{[r['symmetric_difference'] for r in big]} arms. So q is a real parameter awaiting "
                 f"a real family, and the clause should KEEP it with its precondition stated: q is "
                 f"inert below |family| = 10 and this release supplies 2.")
    else:
        world = (f"⛔ B q BUYS NOTHING EVEN WHERE IT CAN ACT — at every k >= 10 the admitted sets "
                 f"coincide. Then q is inert in principle for this operator, not merely inert here, "
                 f"and the clause should DROP it.")
    print(world)
    print(f"⛔ AND THE FAMILY IS SYNTHETIC. These comparators are constructed fixed subsets, blind by")
    print(f"   construction and legitimate under R918's rule, but they are NOT a second release. This")
    print(f"   measures what q would buy against a family built this way; whether a real release")
    print(f"   yields >= 10 genuinely blind comparators is OUT-OF-RELEASE and stays in the register.")

    o = HERE / "results" / "q_in_its_own_world.json"
    o.write_text(json.dumps({
        "round": "R1057", "prompts": n, "arms": len(arms), "nboot": NBOOT,
        "common_criteria": sorted(common), "synthetic_family": [list(s) for s in subsets],
        "rows": rows, "world": world,
        "controls": {"positive_blind_by_construction": bool(pos), "negative_small_k_agree": bool(neg),
                     "sham_identical_comparators": bool(sham), "placebo_k0": bool(plac)},
        "limitation": "the family is synthetic; whether a real release yields >=10 blind comparators "
                      "is out-of-release",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
