#!/usr/bin/env python3
"""R836 -- R835's null used a resolution bound that is conservative by construction.

See PREREGISTRATION.txt, committed with this file before it ran.

ESTIMAND        per adjacent pair in R835's ordering, the rho at which the gap becomes separable:
                    rho* = 1 - (gap / MDE_A)^2 / 2
                A SENSITIVITY CURVE, not a re-verdict. Named before the method.
⚠ DERIVATION    both arms are scored against the SAME bar, so d_AC = d_AB - d_CB and
                MDE_AC = MDE_A * sqrt(2(1-rho)). Using MDE_A directly, as R835 did, IS the
                assumption rho = 0.5, and for rho > 0.5 the true resolution is FINER.
IDENTIFICATION  rho* is identified from committed numbers. rho itself is NOT -- the per-prompt
                difference vectors were never persisted -- so no pair is re-labelled SEPARABLE.
SCOPE           population: R835's 46-arm ③-admissible ordering. instrument: R436's committed a2
                and mde plus the closed form. baseline: R835's MDE_A. regime: A2, this judge.
WORLDS          W-CONSERVATIVE (some pair's rho* is below a value measured on this site -- R835's
                null is scope-dependent) vs W-ROBUST.
KILL            CONDITIONAL on the simulation reproducing the closed form, the application positive
                giving rho* < 0, and the negative giving rho* = 1.
POSITIVE CTRL   ① the SIMULATION, on the derivation itself, at rho in {0.0, 0.5, 0.84, 0.95};
                ② `oracle_k4` vs the best ③-admissible arm must give rho* < 0.
NEGATIVE CTRL   an arm against ITSELF -- looked up TWICE -- must give rho* = 1 exactly.
⚠ BORROWED      0.8377 is R825's corr(bar, core), a DIFFERENT pairing. Used as a reference point on
                the curve, never as this site's arm-vs-arm correlation. Recorded as borrowed.
ARTIFACT        results/r836_rho_sensitivity.json with source hash.
"""
from __future__ import annotations
import hashlib, json, math, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
RES = HERE / "results"
BORROWED_RHO = 0.8377          # R825, corr(bar, core) -- a DIFFERENT pairing


def rho_star(gap: float, mde_a: float) -> float:
    """the rho at which `gap` becomes exactly detectable. Closed form; simulated below."""
    return 1.0 - (gap / mde_a) ** 2 / 2.0


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("\n  R836 · THE RESOLUTION R835 USED IS CONSERVATIVE BY CONSTRUCTION\n")

    # ---- POSITIVE CONTROL ① : the derivation itself, against simulation --------------------
    rng = np.random.default_rng(836)
    n, sd = 968, 1.0
    sim_rows, sim_ok = [], True
    for rho in (0.0, 0.5, 0.84, 0.95):
        cov = np.array([[sd ** 2, rho * sd * sd], [rho * sd * sd, sd ** 2]])
        x = rng.multivariate_normal([0, 0], cov, size=(n, 4000))     # 4000 replicates of n draws
        emp = float(np.mean(np.std(x[..., 0] - x[..., 1], axis=0, ddof=1)))
        closed = sd * math.sqrt(2 * (1 - rho))
        ok = abs(emp - closed) / closed < 0.01
        sim_ok &= ok
        sim_rows.append({"rho": rho, "empirical_sd": emp, "closed_form": closed, "ok": ok})
        print(f"  SIM  rho={rho:<5} empirical sd(d_AC) {emp:.4f}  closed form {closed:.4f}   "
              f"{'match   PASS' if ok else '⛔ FAIL — the derivation is wrong'}")

    d = json.loads(next(A24.glob("R436_*/results/r436_clause4_at_home.json")).read_text())
    cells = {c["arm"]: c for c in d["cells"]}
    r835 = json.loads(next(A24.glob("R835_*/results/r835_external_anchor.json")).read_text())
    pool = r835["pool"]

    # ---- POSITIVE CONTROL ② and NEGATIVE ---------------------------------------------------
    best = pool[0]
    g_pos = cells["oracle_k4"]["a2"] - cells[best]["a2"]
    m_pos = max(cells["oracle_k4"]["mde"], cells[best]["mde"])
    rs_pos = rho_star(g_pos, m_pos)
    pc2 = rs_pos < 0
    print(f"\n  POSITIVE  oracle_k4 vs {best}: gap {g_pos:+.4f} -> rho* {rs_pos:+.4f}   "
          f"{'separable for every admissible rho   PASS' if pc2 else '⛔ FAIL'}")
    g_neg = cells[best]["a2"] - cells[best]["a2"]                    # looked up TWICE, not `x - x`
    rs_neg = rho_star(g_neg, cells[best]["mde"])
    nc = rs_neg == 1.0
    print(f"  NEGATIVE  {best} against itself: gap {g_neg:+.4f} -> rho* {rs_neg:.4f}   "
          f"{'never separable below rho=1   PASS' if nc else '⛔ FAIL'}")

    # ---- the sensitivity curve -------------------------------------------------------------
    rows, flips = [], []
    for p in r835["pairs"]:
        rs = rho_star(p["gap"], p["mde"])
        rows.append({**p, "rho_star": rs, "flips_below_borrowed": rs < BORROWED_RHO})
        if rs < BORROWED_RHO:
            flips.append((p["upper"], p["lower"], p["gap"], rs))
    print(f"\n  pairs whose verdict FLIPS below the borrowed rho = {BORROWED_RHO}: "
          f"{len(flips)} of {len(rows)}\n")
    print(f"  {'upper':<22}{'lower':<22}{'gap':>9}{'rho*':>9}")
    for u, l, g, rs in sorted(flips, key=lambda t: t[3])[:12]:
        print(f"  {u:<22}{l:<22}{g:>+9.4f}{rs:>9.4f}")

    controls_ok = sim_ok and pc2 and nc
    if not controls_ok:
        world, verdict = "UNVERIFIED", "a control is unfit; R835 stands unannotated"
    elif flips:
        world = "W-CONSERVATIVE"
        verdict = (f"{len(flips)} of {len(rows)} adjacent pairs become separable at a rho BELOW the "
                   f"{BORROWED_RHO} measured for a comparable pairing on this site -- R835's null "
                   f"is SCOPE-DEPENDENT and its scope is rho <= its own implicit 0.5")
    else:
        world = "W-ROBUST"
        verdict = "every pair needs a rho above any measured here; R835's null stands unqualified"
    print(f"\n  VERDICT: {world} -- {verdict}\n")
    print("  ⚠ rho is NOT measured here and no pair is re-labelled SEPARABLE. R835's pre-registered")
    print("     verdict is NOT rewritten -- its kill fired as written, and a verdict is not reopened")
    print("     because a later round prefers a different resolution model. It is ANNOTATED.")
    print(f"  ⚠ {BORROWED_RHO} is R825's corr(bar, core), a DIFFERENT pairing, used as a reference")
    print("     point on the curve and recorded in the artifact as borrowed.\n")

    out = {"world": world, "verdict": verdict, "simulation": sim_rows, "simulation_ok": sim_ok,
           "positive_oracle_rho_star": rs_pos, "positive_ok": pc2,
           "negative_self_rho_star": rs_neg, "negative_ok": nc,
           "pairs": rows, "n_flip_below_borrowed": len(flips), "n_pairs": len(rows),
           "borrowed_rho": BORROWED_RHO,
           "borrowed_rho_source": "R825 corr(bar, core) -- a DIFFERENT pairing, not arm-vs-arm",
           "rho_is_not_measured_here": True,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r836_rho_sensitivity.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r836_rho_sensitivity.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
