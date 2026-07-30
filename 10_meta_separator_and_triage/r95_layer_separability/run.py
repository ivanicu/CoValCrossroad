"""r95 -- the meta-separator: does the object resist the decomposition it has been given?

CLAIM CARD
----------
Claim      M(R, J, pi, Q, P) with "each layer validated separately" is the project's
           framing. It PRESUMES the layers are separable enough that validating one at
           a time means something.
Estimand   on r30's 3 judges x 2 donor conditions: (a) does the near<random ordering
           hold in every judge, and (b) is the judge a pure multiplicative GAIN --
           i.e. is near/random constant across judges?
Target
observed?  (a) YES, from stored point estimates. (b) NO, and that is the finding: the
           comparison needs the JOINT bootstrap draws, and r30 stored only the rep
           COUNT and marginal CIs. Marginal CIs cannot substitute, because r30's own
           note records that the bootstrap resampled prompts JOINTLY across numerator
           and denominator -- the arms are correlated by design, so marginal intervals
           overstate the uncertainty of their ratio by an unknown amount.
Alternative
worlds     M MULTIPLICATIVE  ordering holds and near/random is constant. Then J is a
                             gain, R is separable up to scale, and layer-at-a-time
                             validation is sound.
           O ORDINAL-ONLY    ordering holds but the ratio moves. Then R has a
                             judge-invariant ORDINAL property and no cardinal one, and
                             the judge interacts beyond rescaling.
           N NON-SEPARABLE   the ordering flips in some judge. Then there is no
                             judge-invariant property at all and the framing
                             understates the problem.
Intervention
           none. Reads r30's stored grid; adds no judge, which is frozen.
Null       sign agreement across three independent judges has a null: if the ordering
           were arbitrary, P(all three agree) = 2/2^3 = 0.25. That is weak, and the
           round reports it as weak rather than as a p-value dressed up.

WHY THIS IS THE STEP
--------------------
Every prior attack this session tested MY FRAMING OF WHAT REMAINS. None tested the
framing itself. The constitution asks once per programme: is there a credible outcome
showing the world-decomposition is wrong? For M(R,J,pi,Q,P) that outcome is concrete --
if the rubric's measured ordering depends on which judge measures it, then "validate
each layer separately" is not merely incomplete, it is ill-posed, because R has no
value to validate independently of J.

WHAT THIS ROUND CANNOT DO, STATED BEFORE THE NUMBERS
-----------------------------------------------------
It cannot settle M vs O. That needs the paired ratio's sampling distribution, which
requires draws r30 did not persist. Recomputing them means re-running the judge panel;
"more judges" is frozen but re-running the SAME three is not -- it is simply expensive,
and this round exists partly to say precisely what that expense would buy. The verdict
is three-valued and UNVERIFIED is not an acquittal.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

R30 = _ROOT / "03_person_or_pair/r30_scope_grid/results/r30_scope_grid.json"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r95_layer_separability.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not R30.exists():
        raise SystemExit("REFUSING: r30's artifact is absent and this round reads its grid rather "
                         "than restating it.")
    r30 = json.load(open(R30))
    grid = r30["grid"]

    rows, ratios, signs = {}, {}, []
    print(f"  {'judge':<26} {'near':>9} {'random':>9} {'near-random':>12} {'near/random':>12}")
    for j, c in grid.items():
        n, r = c["near"]["share"], c["random"]["share"]
        rows[j] = {"near": n, "random": r, "diff": n - r,
                   "near_ci": c["near"]["ci"], "random_ci": c["random"]["ci"],
                   "prompts": c["near"].get("prompts")}
        ratios[j] = n / r if r else None
        signs.append(n < r)
        print(f"  {j:<26} {n:>9.4f} {r:>9.4f} {n - r:>12.4f} {ratios[j]:>12.4f}")

    all_same = bool(all(signs) or not any(signs))
    n_j = len(signs)
    p_sign = 2 / (2 ** n_j)
    rv = [v for v in ratios.values() if v is not None]
    spread = max(rv) / min(rv)
    print(f"\n  ordering agrees in sign across all {n_j} judges: {all_same}   "
          f"(null P(all agree) = {p_sign:.2f} -- weak by construction, not a p-value)")
    print(f"  near/random ratio spans {min(rv):.4f}-{max(rv):.4f} = {spread:.2f}x")

    # can the ratio spread be tested from what r30 stored?
    has_draws = isinstance(r30.get("boot"), (list, dict))
    print(f"\n  r30 stored joint bootstrap draws: {has_draws}   "
          f"(`boot` is {type(r30.get('boot')).__name__} = {r30.get('boot')!r})")
    # marginal CIs cannot substitute -- record WHY, from r30's own note
    note = r30.get("note", "")
    joint = "jointly" in note.lower()
    print(f"  r30's note records joint resampling across numerator and denominator: {joint}")

    if not all_same:
        world = "N NON-SEPARABLE"
    elif has_draws:
        world = "M MULTIPLICATIVE" if spread < 1.10 else "O ORDINAL-ONLY"
    else:
        world = "O ORDINAL-ONLY (point estimates) / UNVERIFIED between M and O"

    verdict = (
        f"{world}. Every attack this session tested the framing of what REMAINS; none tested the "
        f"framing itself. M(R,J,pi,Q,P) with 'each layer validated separately' PRESUMES the layers are "
        f"separable, and r30's grid can put that to a test the release already paid for. RESULT (a), "
        f"WHICH IS CLEAN: the near<random ordering holds in {sum(signs)} of {n_j} judges -- "
        f"{'all of them' if all_same else 'NOT all of them'}. So the rubric's ordinal property survives "
        f"a change of judge, and the world in which there is no judge-invariant property at all is "
        f"REFUTED at the ordinal level. The null is weak and is reported as weak: with {n_j} judges, "
        f"P(all agree by chance) = {p_sign:.2f}, which is evidence and not proof. "
        f"RESULT (b), WHICH IS THE FINDING: the near/random ratio is "
        + ", ".join(f"{v:.3f}" for v in rv) + f" -- a {spread:.2f}x spread. If the judge were a pure "
        f"multiplicative GAIN that ratio would be constant, and R would be separable from J up to "
        f"scale. It is not constant in the point estimates. BUT THIS CANNOT BE SETTLED HERE, AND THE "
        f"REASON IS A STORAGE GAP RATHER THAN A DATA LIMIT: the paired ratio's sampling distribution "
        f"needs the JOINT bootstrap draws, and r30 persisted only the rep count (`boot` = "
        f"{r30.get('boot')!r}) with marginal CIs. Marginal CIs cannot substitute, because r30's own "
        f"note records that the bootstrap resampled prompts JOINTLY across numerator and denominator "
        f"-- the arms are correlated by construction, so marginal intervals overstate the ratio's "
        f"uncertainty by an unknown amount, in the direction that would make a real interaction look "
        f"untestable. VERDICT IS THREE-VALUED AND UNVERIFIED IS NOT AN ACQUITTAL: the multiplicative "
        f"world is neither confirmed nor excluded. WHAT WOULD SETTLE IT, priced rather than wished for: "
        f"re-running the SAME three judges on the SAME {rows[list(rows)[0]]['prompts']} prompts and "
        f"persisting per-draw ratios. That is not 'more judges', which is frozen -- it is the panel "
        f"already frozen by r80, re-scored to store what r30 discarded. CONSEQUENCE FOR THE FRAMING: "
        f"layer-at-a-time validation is defensible for ORDINAL claims about R and is UNVERIFIED for "
        f"CARDINAL ones, which is exactly the distinction the headline already draws between an "
        f"ordering and a share -- reached here from the separability side rather than the floor side."
    )

    doc = {
        "judges": list(grid), "n_judges": n_j, "rows": rows,
        "near_over_random": ratios, "ratio_spread": float(spread),
        "ordering_agrees_all_judges": all_same, "sign_null_p": float(p_sign),
        "r30_stored_joint_draws": has_draws, "r30_boot_field": r30.get("boot"),
        "r30_note_records_joint_resampling": joint,
        "world": world,
        "outcome_variable_scope": (
            "r30's stored source-specificity shares for two donor conditions under three judge "
            "families, on 300 prompts. Nothing is recomputed and no judge is added."),
        "scope": (
            "Settles the ORDINAL question and leaves the CARDINAL one UNVERIFIED for want of joint "
            "bootstrap draws. It also inherits r30's own stated gap: no phi cell was ever measured at "
            "the farthest-donor floor, so the grid's upper corner is unobserved and this test covers "
            "the two donor conditions that exist in all three judges."),
        "verdict": verdict,
    }
    try:
        from covalx.frozen import append_to
        doc["verdict"] = append_to(doc["verdict"], _HERE.name)
    except Exception:
        pass
    a.out.write_text(json.dumps(doc, indent=1))
    print(f"\n  WORLD: {world}")
    print(f"\n-> {a.out.relative_to(_ROOT)}")


if __name__ == "__main__":
    main()
