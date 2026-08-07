#!/usr/bin/env python3
"""R828 -- run the controls that were registered and never executed.

See PREREGISTRATION.txt, committed before this file was executed.

ESTIMAND        per recoverable round: the value its registered control NAMES, computed through
                that round's own SECOND PRODUCER, at full precision.
IDENTIFICATION  identified for 3 of 5 (a second producer exists). R361 has none and its registered
                property is unrecoverable as written; R746 is partial. Both reported as such.
SCOPE           population: the 5 rounds flagged by assurance/a_control_that_cannot_fail.py under
                E05/A24, excluding R436 (adjudicated last round). instrument: each round's own
                producer, imported or extracted from its committed source. baseline: the ORIGINAL
                `x - x` expression, run side by side. regime: unperturbed (g=0) and perturbed.
WORLDS          W-EMPTY-ASSURANCE (3/3 recovered checks pass -- the numbers stand, the assurance
                was absent) vs W-MASKED-DEFECT (>=1 fails -- a real defect was hidden).
KILL            CONDITIONAL. Evaluated only if every positive control fires AND every g=0 arm is
                null. Otherwise UNVERIFIED -- never OVERTURNED, never CONFIRMED.
POSITIVE CTRL   per producer, a perturbation the registered property forbids. Requires BOTH:
                (a) the recovered check FAILS on it, and (b) the ORIGINAL x-x check still PASSES.
                (b) is what measures the collapse instead of asserting it.
NEGATIVE CTRL   g=0: the unperturbed producer. The recovered check must pass.
SEEDS           R731's cell() swept over 3 seeds; R332/R672 are deterministic by construction and
                that determinism is the property under test.
MULTIPLICITY    5 cells, all reported -- survivors and non-survivors alike.
ARTIFACT        results/r828_recovered_controls.json, with the source hash of every module read.
"""
from __future__ import annotations
import ast, hashlib, json, math, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parent.parent
RES = HERE / "results"
ZEFF = 1.959963984540054


def _src(rnd: str) -> tuple[str, str]:
    p = next(A24.glob(f"{rnd}_*/run.py"))
    t = p.read_text()
    return t, hashlib.sha256(t.encode()).hexdigest()[:16]


def _extract(src: str, name: str):
    """pull a nested FunctionDef out of committed source and bind it standalone."""
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name)
    ns: dict = {"np": np, "math": math, "ZEFF": ZEFF, "json": json,
                "subprocess": subprocess, "pathlib": pathlib}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "<extract>", "exec"), ns)
    return ns[name]


# ---------------------------------------------------------------- R332 · rate() against itself
def r332(rng):
    """registered: 'the closure reference against itself: exactly 0'.
    rate(Bk, ref) is the fraction of rows in Bk that CLEAR clause 2 against ref. Restricted to the
    reference's OWN row, that fraction must be exactly 0 -- a row cannot significantly beat itself.
    The committed check computed `|v - v|.max() == 0` on the extracted vector instead."""
    src, sha = _src("R332")
    rate = _extract(src, "rate")
    Bk = rng.normal(0.5, 0.05, (40, 300))          # a class of 40 candidates over 300 prompts
    i = 7
    recovered = float(rate(Bk[i:i + 1], Bk[i]))     # the row against itself
    original = float(np.abs(Bk[i] - Bk[i]).max())   # what the round actually ran

    def rate_broken(X, r, cols=None):               # perturbation: `>=` admits a tie
        d = X - r
        e = d.mean(axis=1)
        mde = ZEFF * d.std(axis=1, ddof=1) / math.sqrt(d.shape[1])
        return float(((e >= 0) & (np.abs(e) >= mde)).mean())

    pert = float(rate_broken(Bk[i:i + 1], Bk[i]))
    return dict(sha=sha, recovered=recovered, recovered_ok=recovered == 0.0,
                original=original, original_ok=original == 0.0,
                perturbed=pert, pos_fires=pert != 0.0, pos_original_still_passes=original == 0.0)


# ------------------------------------------------------------- R672 · versions() against itself
def r672(rng):
    """registered: 'a version compared against itself must show 0 added and 0 retired'.
    The transition builder computes added/retired as set differences between two INDEPENDENTLY
    constructed version sets. Constructing the SAME version twice must give byte-identical sets.
    The committed check computed `len(s0 - s0)` on one already-built set."""
    src, sha = _src("R672")
    ns: dict = {"__name__": "_r672", "__file__": str(next(A24.glob("R672_*/run.py")))}
    exec(compile(src, "<r672>", "exec"), ns)
    a, b = ns["versions"](), ns["versions"]()        # two independent constructions
    ok = len(a) == len(b) and len(a) > 0 and all(
        sa == sb and ka == kb for (ka, sa), (kb, sb) in zip(a, b))
    added = sum(len(sb - sa) for (_, sa), (_, sb) in zip(a, b))
    retired = sum(len(sa - sb) for (_, sa), (_, sb) in zip(a, b))
    s0 = a[0][1] if a else set()
    original = len(s0 - s0)

    pert = list(a)                                   # perturbation: one nondeterministic element
    if pert:
        k0, s = pert[0]
        pert[0] = (k0, set(s) | {f"__nondet_{rng.integers(1 << 30)}"})
    p_added = sum(len(sb - sa) for (_, sa), (_, sb) in zip(a, pert))
    return dict(sha=sha, n_versions=len(a), recovered_added=added, recovered_retired=retired,
                recovered_ok=bool(ok and added == 0 and retired == 0),
                original=original, original_ok=original == 0,
                perturbed_added=p_added, pos_fires=p_added != 0,
                pos_original_still_passes=len(s0 - s0) == 0)


# ------------------------------------------------------------------ R731 · cell() against itself
def r731(rng, seeds=(31337, 1, 2)):
    """registered: 'an object against itself -> gap exactly 0'.
    cell() carries a 1200-draw bootstrap, so its determinism at a fixed seed is a real property
    that can fail. Two calls on the same data must agree in EVERY field, not only in `eff`.
    The committed check subtracted the STORED eff from itself."""
    src, sha = _src("R731")
    ns: dict = {"__name__": "_r731", "__file__": str(next(A24.glob("R731_*/run.py")))}
    exec(compile(src, "<r731>", "exec"), ns)
    cell = ns["cell"]
    d = rng.normal(0.01, 0.2, 400)
    per_seed = {}
    for s in seeds:
        x, y = cell(d, seed=s), cell(d, seed=s)
        per_seed[str(s)] = {k: (x[k] == y[k]) for k in x}
    ok = all(all(v.values()) for v in per_seed.values())
    original = abs(cell(d)["eff"] - cell(d)["eff"])

    def cell_broken(dd, seed=None, B=1200):          # perturbation: a fresh seed per call
        n = len(dd)
        idx = np.random.default_rng().integers(0, n, (B, n))
        bs = dd[idx].mean(axis=1)
        return {"eff": float(dd.mean()), "lo": float(np.percentile(bs, 2.5)),
                "hi": float(np.percentile(bs, 97.5))}

    p1, p2 = cell_broken(d), cell_broken(d)
    pert_same = all(p1[k] == p2[k] for k in p1)
    return dict(sha=sha, per_seed=per_seed, recovered_ok=bool(ok),
                original=float(original), original_ok=original == 0.0,
                perturbed_identical=bool(pert_same), pos_fires=not pert_same,
                pos_original_still_passes=p1["eff"] == p2["eff"])


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(828)
    print("\n  R828 · THE CONTROLS THAT WERE REGISTERED AND NEVER RUN\n")
    cells = {}
    for name, fn in (("R332", r332), ("R672", r672), ("R731", r731)):
        try:
            cells[name] = fn(rng)
        except Exception as e:                       # a producer that will not run is UNRUNNABLE,
            cells[name] = {"error": f"{type(e).__name__}: {e}"}   # never a PASS and never a FAIL
    if any("error" in c for c in cells.values()):
        for k, c in cells.items():
            if "error" in c:
                print(f"  ⛔ UNRUNNABLE {k}: {c['error']}")
        (RES / "r828_recovered_controls.json").write_text(
            json.dumps({"world": "UNRUNNABLE", "cells": cells}, indent=1))
        return 2

    print(f"  {'round':<8}{'recovered':>12}{'g=0':>7}{'pos fires':>11}"
          f"{'orig still passes':>20}")
    for k, c in cells.items():
        print(f"  {k:<8}{('PASS' if c['recovered_ok'] else '⛔ FAIL'):>12}"
              f"{('null' if c['recovered_ok'] else 'FAIL'):>7}"
              f"{('YES' if c['pos_fires'] else '⛔ no'):>11}"
              f"{('YES — it was blind' if c['pos_original_still_passes'] else 'no'):>20}")

    pos_all = all(c["pos_fires"] for c in cells.values())
    blind_all = all(c["pos_original_still_passes"] for c in cells.values())
    g0_all = all(c["recovered_ok"] for c in cells.values())

    print(f"\n  POSITIVE  every perturbed producer fails its recovered check   "
          f"{'PASS' if pos_all else '⛔ FAIL'}")
    print(f"  POWER     every ORIGINAL x-x check still passes on the SAME perturbation   "
          f"{'PASS — the originals had no power' if blind_all else '⛔ FAIL'}")

    # ---- the kill is a CONDITIONAL. A kill that can fire on a broken instrument is an automated
    #      way to publish an artifact (R826). Controls first, threshold only inside them.
    if pos_all and blind_all:
        world = "W-EMPTY-ASSURANCE" if g0_all else "W-MASKED-DEFECT"
        verdict = ("all three recovered checks PASS -- the rounds' numbers stand and what was "
                   "absent was the assurance" if g0_all else
                   "at least one recovered check FAILS -- a real defect was masked by a constant")
    else:
        world, verdict = "UNVERIFIED", "a control is unfit; the kill is NOT evaluated"
    print(f"\n  VERDICT: {world} -- {verdict}\n")

    print("  NOT RECOVERABLE, reported and not scored:")
    print("    R361  rank[j] is a dict comprehension with no second producer, and a DUPLICATED arm")
    print("          receives an ADJACENT rank, not an equal one. Its registered property is")
    print("          unrecoverable as written -- UNVERIFIED, never a pass and never a fail.")
    print("    R746  the constant difference is conjoined with `and len(cov) > 0`, a real")
    print("          empty-population guard. PARTIAL: half the control is live.\n")

    out = {"world": world, "verdict": verdict, "cells": cells,
           "positive_all_fire": pos_all, "originals_all_blind": blind_all, "g0_all_null": g0_all,
           "not_recovered": {"R361": "no second producer; a duplicate ranks ADJACENT, not equal",
                             "R746": "partial -- conjoined with a real empty-population guard"},
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r828_recovered_controls.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r828_recovered_controls.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
