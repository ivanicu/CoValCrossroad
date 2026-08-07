#!/usr/bin/env python3
"""R994 — the cap is refused, and the reason is measured rather than tasteful.

⛔ WHY. R993 priced the size cap at exactly 2 arms and said what remained was the authorial choice
R987 modelled: decide it, or record why it stays open — and that deciding is not a measurement and
should not be dressed as one. This round decides it. **The decision is authorial; the reason for it
is not.**

⭐ THE REASON. The statement's own parenthetical says *"sizes 3 to 8 are not distinguishable by this
release."* If that holds, a cap at four asserts a boundary the design cannot see — which is
precisely §4's record of how the number "four" got into this definition the first time. So the
decision turns on a measurable question: **are the arms the cap would separate resolvably different
from the instance?**

ESTIMAND        for each arm the cap would uniquely exclude, the paired A2 margin against
                `coval_core` and whether its interval excludes zero.
IDENTIFICATION  identified: a paired difference over the same 968 prompts with a cluster bootstrap.
SCOPE           population : 968 shared prompts · instrument : mean A2 vs human targets, 8000-draw
                paired bootstrap · baseline : `coval_core`, the instance the cap would keep ·
                regime : release one
WORLDS          A THE BOUNDARY IS VISIBLE   every arm the cap excludes is resolvably worse than the
                              instance, so the cap tracks something the design can see and adding it
                              costs nothing epistemically.
                B THE BOUNDARY IS BELOW RESOLUTION   at least one excluded arm is indistinguishable
                              from the instance, so the cap asserts a distinction the release cannot
                              support — the error §4 records.
                prediction matrix: A -> all intervals exclude 0. B -> at least one covers it, named.
KILL            pre-registered, CONDITIONAL on the controls: all intervals excluding 0 ⇒ world B
                dead and the cap is adopted. Any covering 0 ⇒ world A dead and the cap is refused,
                with the arm NAMED.
POSITIVE CTRL   the size-sweep claim itself must reproduce: `topw_k3` vs `topw_k8` must be
                unresolvable, since the statement asserts 3–8 are indistinguishable. If that pair
                RESOLVES, the parenthetical is wrong and this round's premise with it.
NEGATIVE CTRL   an arm known resolvably below the instance must show an interval excluding 0 —
                otherwise the instrument cannot resolve anything and every null is silence.
PLACEBO         `coval_core` against itself: margin exactly 0, interval degenerate.
NOISE FLOOR     the bootstrap interval is the floor; 3 seeds, unanimity required for "resolvable".
MULTIPLICITY    every arm the cap would exclude is tested and reported, resolvable or not.
SEEDS           3.
ARTIFACT        results/cap_refused.json with this file's source hash.
IMPOSSIBLE      whether a cap is the RIGHT clause in principle — N/A: this establishes that THIS
                cap, on THIS release, would draw a line the design cannot see. A release that
                resolves 3 from 8 would reopen it, and that is stated as the condition.
"""
from __future__ import annotations
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls
NBOOT, SEEDS = 8000, (11, 22, 33)


def main() -> int:
    r993 = next(A27.glob("R993_*/results/cap_cost_value.json"), None)
    if not r993:
        print("  UNRUNNABLE: R993's artifact is missing. Exit 2, never 0.")
        return 2
    members = json.loads(r993.read_text())["cap_unique_cost_members"]
    tg, _ = load_targets()
    S0 = load_sat(RES / "sat_generic.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        f = RES / f"sat_{nm}.npz"
        if not f.exists():
            return None
        Sa = load_sat(f); v = np.full(n, np.nan)
        for k, p in enumerate(pids):
            if p in Sa:
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
        return np.nan_to_num(v, nan=np.nanmean(v))

    CNT = [np.random.default_rng(s).multinomial(n, np.ones(n) / n, size=NBOOT).astype(float)
           for s in SEEDS]
    core = vec("coval_core")

    def contrast(nm, ref=None):
        v = vec(nm)
        if v is None:
            return None
        d = v - (core if ref is None else ref)
        los = [float(np.percentile(c @ d / n, 2.5)) for c in CNT]
        his = [float(np.percentile(c @ d / n, 97.5)) for c in CNT]
        return {"arm": nm, "mean_a2": float(v.mean()), "margin": float(d.mean()),
                "lo": min(los), "hi": max(his),
                "resolvable": bool(all(l > 0 for l in los) or all(h < 0 for h in his))}

    print(f"THE {len(members)} ARMS THE CAP WOULD UNIQUELY EXCLUDE, against coval_core:")
    print(f"  {'arm':<16}{'mean A2':>10}{'margin':>11}{'95% CI':>24}  resolvable")
    rows = []
    for a in members:
        r = contrast(a)
        rows.append(r)
        print(f"  {r['arm']:<16}{r['mean_a2']:>10.6f}{r['margin']:>+11.6f}"
              f"   [{r['lo']:+.5f}, {r['hi']:+.5f}]   {r['resolvable']}")

    # ── CONTROLS
    k3k8 = contrast("topw_k8", vec("topw_k3"))
    pos_ok = k3k8 is not None and not k3k8["resolvable"]
    print(f"\n  POSITIVE  the statement's own claim reproduces — topw_k3 vs topw_k8 unresolvable: "
          f"{pos_ok}  (margin {k3k8['margin']:+.6f}, CI [{k3k8['lo']:+.5f}, {k3k8['hi']:+.5f}])")
    neg = contrast("random_k4_s0")
    neg_ok = neg["resolvable"] and neg["margin"] < 0
    print(f"  NEGATIVE  random_k4_s0 is resolvably below the instance: {neg_ok} "
          f"(margin {neg['margin']:+.6f})")
    zero = contrast("coval_core")
    plac_ok = abs(zero["margin"]) < 1e-12 and not zero["resolvable"]
    print(f"  PLACEBO   coval_core against itself: margin {zero['margin']:+.1e}, "
          f"resolvable {zero['resolvable']}  -> {plac_ok}")
    ctrl_ok = pos_ok and neg_ok and plac_ok

    unres = [r["arm"] for r in rows if not r["resolvable"]]
    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; the decision has no evidenced reason"
        decision = "DEFERRED"
    elif not unres:
        world = ("A THE BOUNDARY IS VISIBLE — every arm the cap excludes is resolvably different "
                 "from the instance")
        decision = "ADOPT the cap"
    else:
        world = (f"B THE BOUNDARY IS BELOW RESOLUTION — {unres} is indistinguishable from "
                 f"coval_core, so the cap would assert a distinction this release cannot support")
        decision = "REFUSE the cap"
    print(f"\n⭐ {world}")
    print(f"⭐ DECISION: {decision}")
    print("\n⚠ AND THE DECISION IS AUTHORIAL; ONLY ITS REASON IS MEASURED. A release that resolves")
    print("   3 from 8 reopens it, and that condition is the thing to watch rather than the verdict.")

    out = HERE / "results" / "cap_refused.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git","rev-parse","HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_prompts=n, nboot=NBOOT, seeds=list(SEEDS), members=members, rows=rows,
        controls={"positive_k3_k8_unresolvable": pos_ok, "positive_detail": k3k8,
                  "negative_random_resolvably_below": neg_ok, "placebo_self_zero": plac_ok,
                  "all_ok": ctrl_ok},
        world=world, decision=decision, unresolvable=unres,
        reopens_if="a release whose design resolves sizes 3 from 8",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
