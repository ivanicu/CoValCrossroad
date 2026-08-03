"""r42 -- equivalence tests at a declared margin, over every persisted contrast.

CLAIM_CARD.md is the contract.  In one line: this package reads "no effect" off
several non-significant results, and non-significance is not equivalence.  A
p > 0.05 on a contrast whose CI is four times wider than the margin says the
study could not see the effect, not that the effect is absent -- and those two
readings support opposite sentences.

TOST at alpha = 0.05, equivalently: the 90% bootstrap CI inside (-delta, delta).
The published intervals are 95%, which is the interval for the significance
question; reusing them here would be conservative in a way that is not
principled, so the interval is recomputed at the level the test actually needs
from the paired vectors r34/r35/r36/r37 now persist.

The cross-tab is the output, not a single verdict:

                    | equivalent at delta | not equivalent
    ----------------+---------------------+----------------------------
    significant     | real but negligible | real and material
    not significant | no material effect  | INCONCLUSIVE  <- a null read
                    |                     | off silence

delta is a STIPULATION (0.01, from external review), not a derived quantity, so
the round sweeps it and reports the sweep instead of inheriting one number.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"

DELTA = 0.01
SWEEP = [0.0025, 0.005, 0.01, 0.02, 0.05]

# Where the paired vectors live, and the scope each contrast carries with it.
SOURCES = [
    ("r34", "E02_the_plural_public_dissolved/A02_what_coval_core_mechanically_is/R34_global_rater_crossfit/results/r34_global_rater_crossfit.json",
     ["estimands"], "cross-fitted concordance vs individual rater rankings, original menu"),
    ("r35", "E02_the_plural_public_dissolved/A02_what_coval_core_mechanically_is/R35_polarity_abstention/results/r35_polarity_abstention.json",
     ["regimes", "*", "comparisons"], "post-hoc abstention only; not elicitation-time neutrality"),
    ("r36", "E02_the_plural_public_dissolved/A02_what_coval_core_mechanically_is/R36_channel_shapley/results/r36_channel_shapley.json",
     ["shapley"], "Shapley over 16 coalitions; predictive, not causal"),
    ("r37", "E02_the_plural_public_dissolved/A02_what_coval_core_mechanically_is/R37_leakage_topology/results/r37_leakage_topology.json",
     ["levels"], "isolation rungs A0->A3; L(4) response-blind is undefined, not zero"),
]


def collect(doc, path):
    """Walk a declared path, '*' meaning every key at that level."""
    cur = [([], doc)]
    for step in path:
        nxt = []
        for pre, node in cur:
            if not isinstance(node, dict):
                continue
            keys = list(node) if step == "*" else ([step] if step in node else [])
            for k in keys:
                nxt.append((pre + [k], node[k]))
        cur = nxt
    out = []
    for pre, node in cur:
        if not isinstance(node, dict):
            continue
        for k, v in node.items():
            if isinstance(v, dict) and "paired_differences" in v:
                out.append((".".join(pre + [k]), v))
    return out


def tost(d: np.ndarray, delta: float, boot: int, rng):
    """Bootstrap TOST.  Returns the 90% CI, the two one-sided p-values and the verdict.

    Equivalence at alpha = 0.05 <=> the 90% CI of the mean lies inside
    (-delta, +delta).  The one-sided p-values are the bootstrap tail masses
    beyond each margin, reported so a reader can apply a different alpha.
    """
    n = len(d)
    bs = np.array([d[rng.integers(0, n, n)].mean() for _ in range(boot)])
    lo90, hi90 = np.percentile(bs, [5, 95])
    lo95, hi95 = np.percentile(bs, [2.5, 97.5])
    p_lower = float(np.mean(bs <= -delta))     # evidence against H0: mean <= -delta
    p_upper = float(np.mean(bs >= delta))
    return {
        "delta_hat": float(d.mean()), "n": n,
        "ci90": [float(lo90), float(hi90)], "ci95": [float(lo95), float(hi95)],
        "p_tost": float(max(p_lower, p_upper)),
        "equivalent": bool(lo90 > -delta and hi90 < delta),
        "significant": bool(lo95 > 0 or hi95 < 0),
        "ci95_width_over_delta": float((hi95 - lo95) / delta),
    }


def cell(sig, eq):
    if sig and eq:
        return "real but negligible"
    if sig and not eq:
        return "real and material"
    if not sig and eq:
        return "no material effect"
    return "INCONCLUSIVE"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--delta", type=float, default=DELTA)
    ap.add_argument("--boot", type=int, default=20000)
    ap.add_argument("--out", type=Path, default=_RES / "r42_equivalence.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        a.boot = 200
        a.out = a.out.with_name(a.out.stem + "_SMOKE.json")
        print("*** SMOKE -- must never reach the README ***")

    rng = np.random.default_rng(20260728)

    # ---- CONTROLS FIRST -----------------------------------------------
    # An equivalence test that cannot say NOT EQUIVALENT would report every
    # claim as tightly bounded, which is silence dressed as precision.
    controls = {}
    big = None
    rows = []
    for tag, rel, path, scope in SOURCES:
        p = _ROOT / rel
        if not p.exists():
            print(f"  ! {rel} missing -- {tag} contributes nothing")
            continue
        doc = json.loads(p.read_text())
        found = collect(doc, path)
        # A wrong walk path drops contrasts SILENTLY -- the first run of this
        # round reported 17 contrasts and never mentioned that r36 contributed
        # zero, because its key was "shapley" and the path said "channels".
        # A check is only as good as the population it iterates over, so the
        # population is verified against the file rather than assumed.
        present = json.dumps(doc).count('"paired_differences"')
        if len(found) != present:
            raise SystemExit(
                f"REFUSING: {rel} contains {present} paired vectors but the walk "
                f"path {path} reached {len(found)}. Fix the path -- a silently "
                f"truncated population would report a clean table over a subset.")
        print(f"  {tag}: {len(found)} contrasts")
        for name, node in found:
            d = np.array(node["paired_differences"], dtype=float)
            key = node.get("delta", node.get("L", node.get("gap")))
            if key is not None and abs(float(np.mean(d)) - float(key)) > 1e-9:
                raise SystemExit(f"REFUSING: {tag}.{name} paired vector mean "
                                 f"{np.mean(d)} != published {key}")
            rows.append({"round": tag, "contrast": name, "scope": scope, "d": d})
            if "D_population" in name:
                big = d

    if big is None:
        raise SystemExit("REFUSING: positive control contrast D_population not found")
    pc = tost(big, a.delta, a.boot, rng)
    controls["positive"] = {"contrast": "D_population", **pc,
                            "must_be": "not equivalent", "passed": not pc["equivalent"]}
    nc = tost(np.zeros(500), a.delta, a.boot, rng)
    controls["negative"] = {"contrast": "exact zeros", **nc,
                            "must_be": "equivalent", "passed": nc["equivalent"]}
    print(f"positive control  D_population = {pc['delta_hat']:+.4f}  "
          f"({pc['delta_hat']/a.delta:.1f}x the margin) -> "
          f"{'NOT EQUIVALENT (pass)' if not pc['equivalent'] else 'EQUIVALENT (FAIL)'}")
    print(f"negative control  exact zeros -> "
          f"{'EQUIVALENT (pass)' if nc['equivalent'] else 'NOT EQUIVALENT (FAIL)'}")
    if not (controls["positive"]["passed"] and controls["negative"]["passed"]):
        raise SystemExit("REFUSING TO REPORT: the equivalence instrument failed its "
                         "own controls; every row below would be uninterpretable")

    # ---- the cross-tab -------------------------------------------------
    print(f"\n=== TOST at delta = {a.delta} ({len(rows)} persisted contrasts) ===")
    print(f"{'contrast':52s} {'delta':>9s} {'90% CI':>20s} {'sig':>4s} {'equiv':>6s}  cell")
    out = []
    for r in rows:
        t = tost(r["d"], a.delta, a.boot, rng)
        c = cell(t["significant"], t["equivalent"])
        ci = f"[{t['ci90'][0]:+.4f},{t['ci90'][1]:+.4f}]"
        print(f"{r['round'] + '.' + r['contrast']:52s} {t['delta_hat']:>+9.4f} {ci:>20s} "
              f"{'Y' if t['significant'] else 'n':>4s} {'Y' if t['equivalent'] else 'n':>6s}  {c}")
        out.append({"round": r["round"], "contrast": r["contrast"],
                    "scope": r["scope"], "cell": c, **t})

    # ---- delta sweep: which verdicts are stipulation-dependent? --------
    print(f"\n=== delta sweep -- how many contrasts are EQUIVALENT at each margin ===")
    sweep = {}
    for dl in SWEEP:
        eq = [tost(r["d"], dl, max(2000, a.boot // 5), rng)["equivalent"] for r in rows]
        sweep[str(dl)] = {"n_equivalent": int(sum(eq)), "n_total": len(eq)}
        print(f"  delta = {dl:<7} {sum(eq):2d}/{len(eq)} equivalent")

    incon = [o for o in out if o["cell"] == "INCONCLUSIVE"]
    negl = [o for o in out if o["cell"] == "real but negligible"]
    print(f"\n  INCONCLUSIVE (a null cannot be read off these): {len(incon)}")
    for o in incon:
        print(f"    {o['round']}.{o['contrast']}: {o['delta_hat']:+.4f}, "
              f"95% CI is {o['ci95_width_over_delta']:.1f}x the margin wide")
    print(f"  real but negligible (significant AND bounded below the margin): {len(negl)}")
    for o in negl:
        print(f"    {o['round']}.{o['contrast']}: {o['delta_hat']:+.4f}")

    verdict = (
        f"{len(incon)} of {len(out)} persisted contrasts are INCONCLUSIVE at delta="
        f"{a.delta}: non-significant with an interval too wide to exclude an effect "
        f"of practical size. A null claim is not supported by those. "
        f"{len(negl)} are significant AND bounded below the margin, which is the "
        f"cell where an effect is real and does not matter -- reported separately "
        f"because significance and practical equivalence are different questions."
        if incon else
        f"No contrast is INCONCLUSIVE at delta={a.delta}: every non-significant "
        f"result is also bounded inside the margin, so the null readings in this "
        f"package are supported at this stipulated margin and at no other.")
    print(f"\n-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "delta": a.delta, "boot": a.boot, "alpha": 0.05,
        "delta_is_a_stipulation": True,
        "margin_source": "external methodological review, 2026-07-28; not derived "
                         "from any decision this project specifies",
        "controls": controls, "contrasts": out, "delta_sweep": sweep,
        "n_inconclusive": len(incon), "n_negligible": len(negl),
        "verdict": verdict,
        "scope": ("Aggregate equivalence only. A contrast can be equivalent in "
                  "aggregate and heterogeneous underneath -- criterion-level sign "
                  "reversals and minority-only criteria are NOT tested here and are "
                  "queue item 5. An equivalence result here is not a "
                  "population-invariance result."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
