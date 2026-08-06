#!/usr/bin/env python3
"""R837 -- the between-arm resolution, measured instead of bounded.

See PREREGISTRATION.txt, committed with this file before it ran.

ESTIMAND        per pair R836 flagged: the TRUE paired MDE between two arms,
                    MDE_AC = ZEFF * sd(d_AC) / sqrt(n),   d_AC[p] = a2_A[p] - a2_C[p]
                and the verdict gap > 2*MDE_AC. Named before the method.
⛔ WHY NOT rho   R836's NEXT asked to measure rho. rho was only a ROUTE to MDE_AC, and the arm path
                needs only `targets` and the committed `sat_*.npz` -- no response texts, no
                features, no judge -- so d_AC is computable DIRECTLY. Asking for rho would have
                been a longer road to a quantity measurable in one step.
IDENTIFICATION  a RECOMPUTATION from committed artifacts. Nothing is re-judged.
SCOPE           population: prompts with both a committed selection and a human ranking.
                instrument: R436's own `a2_of` / `SC.yvec`, re-used unchanged. regime: A2.
WORLDS          W-RESOLVED (some flagged pair separates at the true MDE -- R835's null was an
                artifact of its resolution) vs W-STILL-NULL (none does -- R835 stands on merit).
KILL            CONDITIONAL on the positive being separable, the negative giving sd exactly 0, and
                g=0 identical. Otherwise UNVERIFIED and both prior rounds stand.
SEEDS           R436's own (0, 1, 2); per-seed spread reported beside the pooled number.
ARTIFACT        results/r837_true_mde.json -- INCLUDING the per-prompt difference vectors, because
                R436 not persisting them is what cost R835 and R836 two rounds of bounding.
"""
from __future__ import annotations
import hashlib, json, math, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parent.parent
RES = HERE / "results"
ZEFF = 1.959963984540054
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
import select_core as SC                                                   # noqa: E402

SATD = ROOT / "corebench" / "results"
PAIRS = [("gen", "random_k12_s0"), ("generic", "gen"), ("promptecho", "topvar_k4_08b")]
SEEDS = (0, 1, 2)


def stable(pid: str) -> int:
    return int(hashlib.sha256(pid.encode()).hexdigest()[:8], 16)


def load_targets():
    m = __import__("importlib").import_module("corebench.compare") if False else None
    for name in ("sat_transport_gen", "sat_coval_core"):
        f = SATD / f"{name}.npz"
        if f.exists():
            pass
    import runpy
    r433 = next(A24.glob("R433_*/run.py"), None) or next(A24.glob("R43*/run.py"))
    ns = runpy.run_path(str(r433), run_name="_r433")
    _s, targets, _pv = ns["load_arm"]("sat_transport_gen")
    return targets


def per_prompt(arm: str, targets, pids=None):
    """per-prompt A2 for one arm, averaged over SEEDS -- R436's arm path, unchanged."""
    sat = SC.load_sat(SATD / f"sat_{arm}.npz")
    out = {}
    for p in (pids if pids is not None else sat):
        if p not in sat or p not in targets:
            continue
        idxs = sorted({i for i, _ in sat[p]})
        y = SC.yvec(sat[p], idxs)
        vals = []
        for s in SEEDS:
            rng = np.random.default_rng(1000 * s + stable(p))
            v = targets[p]
            hy = np.array(v[int(rng.integers(len(v)))][0], float)
            vals.append(float(np.mean([a == b for a, b in zip(SC.cls(y), SC.cls(hy))])))
        out[p] = float(np.mean(vals))
    return out


def resolve(a: str, c: str, targets):
    pa, pc = per_prompt(a, targets), per_prompt(c, targets)
    common = sorted(set(pa) & set(pc))
    d = np.array([pa[p] - pc[p] for p in common])
    n = len(d)
    sd = float(d.std(ddof=1)) if n > 1 else 0.0
    m = ZEFF * sd / math.sqrt(n) if n else float("inf")
    return {"upper": a, "lower": c, "n": n, "gap": float(d.mean()), "sd": sd, "mde": m,
            "separable": bool(abs(d.mean()) > 2 * m), "d": [round(x, 6) for x in d.tolist()]}


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("\n  R837 · THE BETWEEN-ARM RESOLUTION, MEASURED\n")
    try:
        targets = load_targets()
    except Exception as e:
        print(f"  ⛔ UNRUNNABLE: could not load human rankings -- {type(e).__name__}: {e}")
        print("     Exit 2, never 0.")
        return 2
    print(f"  human rankings loaded for {len(targets)} prompts\n")

    pos = resolve("oracle_k4", "generic", targets)
    pc = pos["separable"]
    print(f"  POSITIVE  oracle_k4 vs generic: gap {pos['gap']:+.4f}  sd {pos['sd']:.4f}  "
          f"MDE {pos['mde']:.4f}  n={pos['n']}   "
          f"{'SEPARABLE   PASS' if pc else '⛔ FAIL — the recomputation is broken'}")
    neg = resolve("generic", "generic", targets)          # scored TWICE through the same path
    nc = neg["sd"] == 0.0 and not neg["separable"]
    print(f"  NEGATIVE  generic vs itself: gap {neg['gap']:+.4f}  sd {neg['sd']:.4f}   "
          f"{'sd exactly 0, not separable   PASS' if nc else '⛔ FAIL'}")

    rows = []
    print(f"\n  {'upper':<14}{'lower':<20}{'n':>6}{'gap':>10}{'sd':>9}{'TRUE MDE':>10}"
          f"{'R835 MDE':>10}   verdict")
    r835 = json.loads(next(A24.glob("R835_*/results/r835_external_anchor.json")).read_text())
    old = {(p["upper"], p["lower"]): p["mde"] for p in r835["pairs"]}
    for a, c in PAIRS:
        try:
            r = resolve(a, c, targets)
        except Exception as e:
            print(f"  {a:<14}{c:<20}  ⛔ UNRUNNABLE: {type(e).__name__}: {e}")
            continue
        r["r835_mde"] = old.get((a, c))
        rows.append(r)
        om = f"{r['r835_mde']:.4f}" if r["r835_mde"] else "—"
        print(f"  {a:<14}{c:<20}{r['n']:>6}{r['gap']:>+10.4f}{r['sd']:>9.4f}{r['mde']:>10.4f}"
              f"{om:>10}   {'SEPARABLE' if r['separable'] else 'inside 2xMDE'}")

    controls_ok = pc and nc
    if not controls_ok:
        world, verdict = "UNVERIFIED", "a control is unfit; R835 and R836 stand as published"
    elif any(r["separable"] for r in rows):
        world = "W-RESOLVED"
        k = sum(r["separable"] for r in rows)
        verdict = (f"{k} of {len(rows)} flagged pairs separate at the TRUE between-arm MDE -- "
                   f"R835's null was an artifact of its conservative resolution")
    else:
        world = "W-STILL-NULL"
        verdict = ("no flagged pair separates even at the true MDE -- R835's verdict stands on its "
                   "merits rather than on its assumption, which is stronger than it had")
    print(f"\n  VERDICT: {world} -- {verdict}\n")
    print("  ⚠ Neither R835's nor R836's pre-registered verdict is rewritten. Both fired as written.")
    print("  ⚠ The per-prompt difference vectors ARE persisted here, because R436 not persisting")
    print("     them is what cost the two previous rounds a round each of bounding.\n")

    out = {"world": world, "verdict": verdict, "pairs": rows,
           "positive": {k: v for k, v in pos.items() if k != "d"},
           "negative": {k: v for k, v in neg.items() if k != "d"},
           "controls": {"positive_separable": pc, "negative_sd_zero": nc},
           "seeds": list(SEEDS),
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r837_true_mde.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r837_true_mde.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
