#!/usr/bin/env python3
"""R516 — does a PER-PROMPT clause ① exclude any admitted arm?

R515 showed the ①/② comparator ordering reverses on 26.96% of prompts, so a per-prompt ① has
something to bind on. It did not show that it binds on any ARM. This closes that.

ESTIMAND (before method): for each admitted arm, the fraction of prompts on which it outscores
  the clause-① comparator (`random_k4_s0`) -- its WIN RATE -- and the threshold τ at which a
  per-prompt ① of the form "win on ≥τ of prompts" would exclude it.
IDENTIFICATION: fully identified; both sides are released saturation matrices scored by the same
  per-prompt A2 the census uses.
SCOPE  population: the 968 prompts · instrument: per-prompt A2 over ALL annotators · baseline:
  `random_k4_s0` · regime: each arm at its OWN k, as R294 scores it.
WORLDS  A · every admitted arm wins on a clear majority, so a per-prompt ① at any sane τ
              excludes nothing and ① stays inert however it is operationalised.
        B · at least one admitted arm's win rate falls near or below the null's, so a
              per-prompt ① separates arms the global one cannot.
KILL (pre-registered): if every admitted arm's win rate exceeds the null arm's upper range,
  world B dies for τ at the null; the specification curve is reported regardless.
POSITIVE CONTROL: for EACH arm, the mean per-prompt difference must reproduce that arm's stored
  c1[0] from R294 to 1e-4. Five independent exact checks, not one aggregate.
NEGATIVE CONTROL (the null): `random_k4_s1` -- a SIBLING random arm, same construction, no
  advantage over `random_k4_s0` by design. Its win rate is what "no effect" looks like on this
  statistic, which a permutation cannot tell you because the tie structure is the whole issue.
PLACEBO: `random_k4_s0` against itself -- must be exactly 0 wins, 100% ties.
SHAM: `coval_core_sham` -- the same construction with the ingredient inverted; must sit below
  `coval_core`, and its position relative to the null is itself informative.
NOISE FLOOR: per-prompt A2 has 7 levels over 6 pairs, so ties are structural; the tie rate is
  reported beside every win rate and the curve is swept over both tie conventions.
MULTIPLICITY: 7 arms x 9 τ levels = 63 cells; the whole curve is printed, survivors and not.
SPECIFICATION: τ swept 0.30-0.70; ties counted as losses AND as half-wins (both conventions).
IMPOSSIBLE HERE: whether "win on ≥τ" is the right per-prompt rule. That is a construct claim and
  needs an external standard for what a core must do. Named, not marked planned.
"""
import json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
import score as S

RES = ROOT / "corebench/results"
ADMITTED = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]
EXTRA    = ["random_k4_s1", "coval_core_sham"]     # null + sham
TAUS     = [0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70]

def per_prompt(sat, pids, HC):
    return np.array([np.mean([[S.cls(S.yvec(sat[p], sorted({i for i, _ in sat[p]})))[q] == h[q]
                               for q in range(6)] for h in HC[p]]) for p in pids])

def main():
    census = json.loads((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                         "/R294_the_definition_against_everything/results/full_census.json").read_text())
    base = S.load_sat(RES / "sat_random_k4_s0.npz")
    targets, _ = S.load_targets()
    arms = {}
    for a in ADMITTED + EXTRA:
        arms[a] = S.load_sat(RES / f"sat_{a}.npz")
    pids = sorted(set(base) & set(targets) & set.intersection(*[set(v) for v in arms.values()]))
    pids = [p for p in pids if len(targets[p]) >= 2]
    if not pids:
        print("  empty population -> UNRUNNABLE"); return 2
    HC = {p: [S.cls(y) for y, _ in targets[p]] for p in pids}
    b = per_prompt(base, pids, HC)
    print(f"  population: {len(pids)} prompts\n")

    # PLACEBO
    plac = per_prompt(base, pids, HC) - b
    print(f"  PLACEBO   base vs itself: wins={float((plac>0).mean()):.4f} "
          f"ties={float((plac==0).mean()):.4f} -> "
          f"{'PASS' if (plac==0).all() else 'FAIL'}")

    rows, pos_fail = {}, []
    print(f"\n  {'arm':<18}{'mean Δ':>10}{'c1[0]':>10}{'ctrl':>7}{'win':>8}{'tie':>8}{'loss':>8}")
    for a in ADMITTED + EXTRA:
        d = per_prompt(arms[a], pids, HC) - b
        mean_d = float(d.mean())
        stored = census["rows"].get(a, {}).get("c1", [None])[0]
        ok = stored is not None and abs(mean_d - stored) <= 1e-4
        if a in ADMITTED and not ok: pos_fail.append(a)
        w, t = float((d > 0).mean()), float((d == 0).mean())
        rows[a] = {"mean_delta": mean_d, "stored_c1": stored, "ctrl_ok": bool(ok),
                   "win": w, "tie": t, "loss": 1 - w - t}
        print(f"  {a:<18}{mean_d:>+10.6f}{(stored if stored is not None else float('nan')):>+10.6f}"
              f"{('OK' if ok else 'FAIL'):>7}{w:>8.4f}{t:>8.4f}{1-w-t:>8.4f}")

    print(f"\n  POSITIVE CONTROL  {len(ADMITTED)-len(pos_fail)}/{len(ADMITTED)} admitted arms "
          f"reproduce their stored c1[0] to 1e-4 -> {'PASS' if not pos_fail else 'FAIL '+str(pos_fail)}")
    if pos_fail:
        print("  -> reconstruction unvalidated; NO conclusion admissible. UNVERIFIED.")
        (pathlib.Path(__file__).parent / "results/per_prompt_clause1.json").write_text(
            json.dumps({"world": "UNVERIFIED", "rows": rows, "pos_fail": pos_fail}, indent=2))
        return 0

    null_w = rows["random_k4_s1"]["win"]
    print(f"  NEGATIVE CONTROL (null)  sibling random arm win rate = {null_w:.4f}\n")

    print(f"  SPECIFICATION CURVE — excluded by 'win ≥ τ'?  (ties as LOSSES | ties as HALF)")
    print(f"  {'arm':<18}" + "".join(f"{t:>7.2f}" for t in TAUS))
    curve = {}
    for a in ADMITTED + EXTRA:
        w, t = rows[a]["win"], rows[a]["tie"]
        wh = w + t / 2
        cells = ["  ✗/✗" if (w < tau and wh < tau) else ("  ✗/·" if w < tau else "  ·/·")
                 for tau in TAUS]
        curve[a] = {"win": w, "win_half": wh,
                    "excluded_at": [tau for tau in TAUS if w < tau]}
        print(f"  {a:<18}" + "".join(f"{c:>7}" for c in cells))
    print(f"  (✗ = excluded at that τ)")

    adm_w = [rows[a]["win"] for a in ADMITTED]
    world = "B" if min(adm_w) <= null_w else "A"
    print(f"\n  lowest admitted win rate {min(adm_w):.4f} vs null {null_w:.4f}")
    print(f"  WORLD {world} -- " +
          ("a per-prompt ① separates arms the global one cannot"
           if world == "B" else
           "every admitted arm beats the null; a per-prompt ① at the null's τ excludes none"))
    tau_sep = [tau for tau in TAUS if any(rows[a]["win"] < tau for a in ADMITTED)]
    print(f"  τ at which a per-prompt ① first excludes an admitted arm: "
          f"{min(tau_sep) if tau_sep else 'none in [0.30,0.70]'}")

    (pathlib.Path(__file__).parent / "results/per_prompt_clause1.json").write_text(json.dumps(
        {"n_prompts": len(pids), "rows": rows, "curve": curve, "taus": TAUS,
         "null_win": null_w, "world": world,
         "tau_first_exclusion": (min(tau_sep) if tau_sep else None)}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
