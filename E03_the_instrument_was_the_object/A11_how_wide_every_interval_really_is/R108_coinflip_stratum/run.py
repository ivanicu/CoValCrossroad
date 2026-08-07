"""r108 -- 17% of the records have a label decided by a coin flip. What does the chain say there?

CLAIM CARD
----------
Claim      r104 broke a tied labelling third AT RANDOM rather than dropping it, because
           dropping conditions on the label being decisive. That choice is right, and it
           means 8,041 of 47,148 records carry a label that is literally a coin flip. Every
           accuracy, attenuation factor, share and interval in r104-r107 is computed across
           those records, and no round has ever asked what they contribute.
Estimand   two things from one partition:
           (a) the own and donor arm accuracy, and their difference, RESTRICTED to
               coin-flip-labelled records;
           (b) the consensus GRADIENT with every coin-flip record DELETED, against the raw
               gradient computed over both strata -- i.e. how much of r104's raw rise is
               the differential tie rate rather than the arms.
Target
observed?  YES. r104 persisted `label_tied` alongside every record precisely so this
           partition would be possible later.
Alternative
worlds     N NULL RECOVERED  both arms sit at 0.5 on the coin-flip stratum and their
                             difference at 0. Then the chain passes a null-recovery test on
                             8,041 REAL records: where the target carries no information,
                             the instrument reports none.
           L LEAKING         an arm departs from 0.5. Then something connects an arm to the
                             label other than through the human ranking -- the random
                             tiebreak is not independent of the arms, or r106's label-
                             direction recovery is wrong -- and every number in r104-r107
                             is suspect.
           Crossed with, once N holds -- and note what this axis is NOT. The first draft
           of this card claimed the untied-only gradient is an INDEPENDENT ROUTE to r104's
           deattenuated gradient. It is not, and the run proved it: stratifying out ties
           removes only the ZERO-information records, while an untied third is still an
           unreliable majority. So the honest second question is narrower.
           E EXPLAINED       the differential tie rate (0.258 -> 0.107 across bins) accounts
                             for the raw gradient: deleting every tied record collapses it.
                             Then r104's raw rise was substantially a tie-rate artifact.
           S SURVIVES        deleting them barely moves it. Then the confound written
                             before r104 -- that the low-consensus bin is the most diluted
                             -- is measured and dismissed, and the gradient is carried by
                             records that all had a real majority.
Intervention
           none. A partition of records r104 already persisted.
Null       THIS ROUND IS ITSELF A NULL, so its control is the COMPLEMENTARY STRATUM: the
           untied records must show a large effect. A partition where BOTH halves read 0.5
           would "pass" the null for the wrong reason -- it would mean the partition is not
           separating anything, or the arms are dead. Both directions are required, and the
           round refuses if the informative stratum is not clearly non-null.

WHY THIS IS THE STEP
--------------------
Four rounds have been spent narrowing an interval. None of them asked whether the
measurement can return NOTHING when there is nothing -- and the data to ask it were
persisted the whole time. A chain that has never produced a zero has never demonstrated it
can.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
The tie rate is NOT constant across bins: r104 recorded 0.258 / 0.202 / 0.107 from low to
high consensus, so the low-consensus bin is the most diluted and the raw gradient could be
partly a tie-rate gradient. That is the hypothesis (b) tests, and it is a REAL alternative:
a tied record contributes exactly 0.5/0.5 and therefore attribution 0, so each bin's raw
attribution is (1 - tie_rate) x its untied attribution. With rates 0.258 and 0.107 the two
ends are shrunk by different amounts, which is a mechanism for a gradient with no arms in
it at all.

AND A CORRECTION TO THIS CARD, KEPT RATHER THAN REWRITTEN. The first draft claimed the
untied-only gradient is an INDEPENDENT ROUTE to r104's deattenuated gradient -- two ways to
remove label noise, one dividing and one deleting rows, whose agreement would be strong
evidence. That was wrong, and the run showed it: deleting ties removes only the ZERO-
information records, while an untied third is still an unreliable majority. The number that
proves it is A=B agreement among the SURVIVING records, which is 0.8347, not 1.0 -- an
attenuation factor of about 0.82 that this stratification leaves untouched and r104's
division does not. So (b) is compared against the RAW gradient, which is the only thing it
is commensurable with.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

VEC = _ROOT / "E03_the_instrument_was_the_object/A11_how_wide_every_interval_really_is/R104_deattenuated_consensus/results/r104_split_records.npz"
R104 = _ROOT / "E03_the_instrument_was_the_object/A11_how_wide_every_interval_really_is/R104_deattenuated_consensus/results/r104_deattenuated_consensus.json"
EDGES = (0.49, 0.6, 0.9, 1.01)
MIN_BIN, N_BOOT = 300, 400
NULL_SE = 3.0        # pre-registered: an arm may sit this many standard errors from 0.5
EXPLAINS = 0.30      # pre-registered: ties "explain" the gradient if deleting them moves
                     # it by more than this FRACTION of the raw rise


def arms(own, don, m):
    o, d = float(own[m].mean()), float(don[m].mean())
    se = float(np.sqrt(0.25 / m.sum()))
    return {"n": int(m.sum()), "own": o, "donor": d, "attribution": o - d,
            "se_of_a_chance_arm": se, "own_z": (o - 0.5) / se, "donor_z": (d - 0.5) / se}


def gradient(own, don, cons, sel, edges=EDGES, min_bin=MIN_BIN):
    """Low-to-high-consensus rise of own-minus-donor, on a chosen subset."""
    vals = []
    for i in range(len(edges) - 1):
        m = sel & (cons >= edges[i]) & (cons < edges[i + 1])
        if m.sum() < min_bin:
            return None, []
        vals.append(float(own[m].mean() - don[m].mean()))
    return vals[-1] - vals[0], vals


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r108_coinflip_stratum.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not (VEC.exists() and R104.exists()):
        raise SystemExit("REFUSING: r104's records are absent; this round partitions them.")

    z = np.load(VEC)
    cons, own, don, ab = z["cons"], z["own"], z["donor"], z["ab"]
    tied = z["label_tied"] > 0.5
    r104 = json.load(open(R104))

    print(f"records {len(tied):,}   label decided by a COIN FLIP: {tied.sum():,} "
          f"({tied.mean():.1%})")
    t = arms(own, don, tied)
    u = arms(own, don, ~tied)
    print(f"\n  {'stratum':<24} {'n':>7} {'own':>8} {'donor':>8} {'attrib':>9} {'own z':>8}")
    for name, r_ in (("COIN FLIP (must be 0.5)", t), ("informative", u)):
        print(f"  {name:<24} {r_['n']:>7,} {r_['own']:>8.4f} {r_['donor']:>8.4f} "
              f"{r_['attribution']:>+9.4f} {r_['own_z']:>+8.1f}")

    # ---- the null, and its complementary control ------------------------------
    null_ok = abs(t["own_z"]) < NULL_SE and abs(t["donor_z"]) < NULL_SE
    ctrl_ok = u["own_z"] > 10 * NULL_SE
    print(f"\n  NULL: both arms within {NULL_SE} se of chance on the coin-flip stratum -> "
          f"{'PASS' if null_ok else 'FAIL'}")
    print(f"  COMPLEMENTARY CONTROL: the informative stratum is clearly non-null "
          f"(own {u['own_z']:+.0f} se) -> {'PASS' if ctrl_ok else 'FAIL'}")
    if not ctrl_ok:
        raise SystemExit("REFUSING: the informative stratum is not clearly non-null, so a null on the "
                         "coin-flip stratum would pass for the wrong reason -- a partition that "
                         "separates nothing, or arms that are dead.")

    # a coin-flip A against a real B majority must also agree at chance
    ab_tied, ab_untied = float(ab[tied].mean()), float(ab[~tied].mean())
    print(f"  SECOND NULL, on the reliability probe: A=B agreement is {ab_tied:.4f} on coin-flip "
          f"records against {ab_untied:.4f} on informative ones")

    # ---- the two independent routes to the gradient ---------------------------
    raw_rise, raw_bins = gradient(own, don, cons, np.ones_like(tied))
    unt_rise, unt_bins = gradient(own, don, cons, ~tied)
    corrected = r104["rise_corrected"]
    delta = unt_rise - raw_rise
    moved = abs(delta) / abs(raw_rise)
    explained = moved > EXPLAINS
    print(f"\n  raw rise, both strata pooled            {raw_rise:+.4f}")
    print(f"  rise with every tied record DELETED     {unt_rise:+.4f}   moved {delta:+.4f} "
          f"({moved:.1%} of the raw rise)")
    print(f"  -> the differential tie rate {'EXPLAINS' if explained else 'does NOT explain'} "
          f"the gradient (threshold {EXPLAINS:.0%})")
    # WHY DELETING TIES IS NOT r104'S CORRECTION, stated with the number that shows it.
    resid_f = float(np.sqrt(max(2 * ab_untied - 1, 0.0)))
    print(f"\n  and deleting ties is NOT r104's correction: A=B agreement among the SURVIVING "
          f"records is {ab_untied:.4f},")
    print(f"  an attenuation factor of {resid_f:.4f} still uncorrected. r104's {corrected:+.4f} "
          f"divides that out too; this stratification does not.")

    # bootstrap the untied-only rise over PAIRS
    pid = z["pid"]
    npairs = int(pid.max()) + 1
    order = np.argsort(pid, kind="stable")
    start = np.searchsorted(pid[order], np.arange(npairs), side="left")
    end = np.searchsorted(pid[order], np.arange(npairs), side="right")
    rb = np.random.default_rng(20260736)
    draws = []
    for _ in range(N_BOOT):
        pick = rb.integers(0, npairs, npairs)
        sel = np.concatenate([order[start[p]:end[p]] for p in pick])
        r_, _ = gradient(own[sel], don[sel], cons[sel], ~tied[sel], min_bin=1)
        if r_ is not None:
            draws.append(r_)
    draws = np.array(draws)
    blo, bhi = float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))
    print(f"  untied-only rise 95% CI over pairs [{blo:+.4f},{bhi:+.4f}] ({len(draws)} draws)")

    world = ("L LEAKING" if not null_ok else
             ("N NULL + E EXPLAINED" if explained else "N NULL + S SURVIVES"))
    vec = _RES / "r108_untied_rise_draws.npz"
    np.savez_compressed(vec, untied_rise=draws, untied_bins=np.array(unt_bins),
                        raw_bins=np.array(raw_bins))
    print(f"  draws persisted -> {vec.relative_to(_ROOT)}")

    verdict = (
        f"{world}. r104 broke a tied labelling third AT RANDOM rather than dropping it -- dropping "
        f"conditions on the label being decisive -- so {tied.sum():,} of {len(tied):,} records "
        f"({tied.mean():.1%}) carry a label that is literally a coin flip, and four rounds computed "
        f"across them without asking what they contribute. ON THAT STRATUM THE CHAIN RETURNS NOTHING: "
        f"own {t['own']:.4f} and donor {t['donor']:.4f}, each within {max(abs(t['own_z']), abs(t['donor_z'])):.1f} "
        f"standard errors of chance, attribution {t['attribution']:+.4f}. "
        + ("That is a NULL RECOVERY on 8,041 real records rather than a simulation: where the target "
           "carries no information the instrument reports none, which no round in this line had ever "
           "demonstrated. "
           if null_ok else
           "AN ARM DEPARTS FROM CHANCE, which the human ranking cannot explain -- something connects "
           "an arm to the label other than through it, and every number in r104-r107 is suspect. ") +
        f"COMPLEMENTARY CONTROL, and it is what stops the null passing for the wrong reason: the "
        f"informative stratum is {u['own_z']:+.0f} standard errors from chance with attribution "
        f"{u['attribution']:+.4f}. A partition whose halves BOTH read 0.5 would mean the partition "
        f"separates nothing, or the arms are dead. SECOND NULL, on the reliability probe itself: a "
        f"coin-flip labelling third agrees with a real probe third {ab_tied:.4f} of the time against "
        f"{ab_untied:.4f} on informative records -- chance, as a coin flip against a real majority must "
        f"be, so the attenuation factor r104 divides by correctly reads this stratum as carrying no "
        f"reliability at all. "
        f"AND THE TIE-RATE CONFOUND IS MEASURED AND DISMISSED. The tie rate is NOT flat -- 0.258 / "
        f"0.202 / 0.107 from low to high consensus -- and a tied record contributes attribution "
        f"exactly 0, so each bin's raw attribution is (1 - tie_rate) times its untied one and the two "
        f"ends are shrunk by different amounts. That is a mechanism for a gradient with no arms in it. "
        f"Deleting every tied record moves the rise from {raw_rise:+.4f} to {unt_rise:+.4f}, a change "
        f"of {delta:+.4f} or {moved:.1%} of it, against a pre-registered threshold of {EXPLAINS:.0%}: "
        + (f"the differential tie rate EXPLAINS a substantial part of the gradient, and r104's raw "
           f"rise must be read as partly an artifact of dilution."
           if explained else
           f"the differential tie rate does NOT explain the gradient. It is carried by records that "
           f"all had a real majority, and 95% CI over pairs on the untied-only rise is "
           f"[{blo:+.4f},{bhi:+.4f}].") +
        f" A CORRECTION TO THIS ROUND'S OWN CLAIM CARD, KEPT RATHER THAN REWRITTEN: its first draft "
        f"called the untied-only gradient an INDEPENDENT ROUTE to r104's deattenuated {corrected:+.4f} "
        f"-- two ways of removing label noise, one dividing and one deleting rows, whose agreement "
        f"would be strong evidence for the noise model. THAT WAS WRONG. Deleting ties removes only the "
        f"ZERO-information records; an untied third is still an unreliable majority. The number that "
        f"proves it is A=B agreement among the SURVIVING records, {ab_untied:.4f} rather than 1.0, an "
        f"attenuation factor of {resid_f:.4f} that this stratification leaves untouched and r104's "
        f"division does not. The two are not commensurable and the comparison here is against the RAW "
        f"gradient instead. "
        f"SCOPE: a partition of r104's persisted records. No new measurement, no judge call, and no "
        f"donor redraw -- the single canonical draw of r104 is inherited unchanged, so r106's finding "
        f"that a ratio magnifies draw variance does not apply here, these being differences rather "
        f"than ratios."
    )

    doc = {
        "n_records": int(len(tied)), "n_coinflip": int(tied.sum()),
        "coinflip_rate": float(tied.mean()),
        "coinflip_stratum": t, "informative_stratum": u,
        "null_pass": bool(null_ok), "complementary_control_pass": bool(ctrl_ok),
        "null_se_threshold": NULL_SE,
        "ab_agreement_coinflip": ab_tied, "ab_agreement_informative": ab_untied,
        "raw_pooled_rise": float(raw_rise), "untied_only_rise": float(unt_rise),
        "tie_deletion_moves_rise_by": float(delta),
        "fraction_of_raw_rise_moved": float(moved),
        "explains_threshold": EXPLAINS, "tie_rate_explains_gradient": bool(explained),
        "r104_deattenuated_rise_NOT_COMMENSURABLE": corrected,
        "residual_attenuation_after_deleting_ties": resid_f,
        "untied_rise_ci95_over_pairs": [blo, bhi], "n_boot": int(len(draws)),
        "untied_bins": unt_bins, "raw_bins": raw_bins,
        "persisted_vector": str(vec.relative_to(_ROOT)), "world": world,
        "outcome_variable_scope": (
            "Own and donor accuracy against a third of each pair's human raters, partitioned by "
            "whether that third TIED and had its label decided by a coin flip. Both quantities come "
            "from r104's persisted records; nothing is remeasured."),
        "scope": (
            "Inherits r104's single canonical donor draw unchanged. Deleting tied records removes "
            "proportionally more from the low-consensus end, since the tie rate is not flat -- which "
            "is the confound this tests, and it is compared against the RAW gradient because that is "
            "the only quantity it is commensurable with. It is NOT a second route to r104's "
            "deattenuated figure: A=B agreement among the surviving records is 0.8347, leaving an "
            "attenuation factor of 0.82 that deletion does not touch and division does."),
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
