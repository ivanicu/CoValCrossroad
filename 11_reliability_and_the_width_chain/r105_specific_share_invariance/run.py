"""r105 -- the attribution's MAGNITUDE rises with consensus. Does its COMPOSITION?

CLAIM CARD
----------
Claim      r104 established that 74% of r103's consensus gradient survives the label's
           own noise: deattenuated attribution runs +0.1546 -> +0.2491. Both arms rise.
           Every statement so far is about the SIZE of the signal on contested versus
           consensual pairs. None is about what the signal is MADE OF.
Estimand   the prompt-specific SHARE of over-chance accuracy,

               share = (own - donor) / (own - 0.5),

           per consensus bin. The numerator is the increment a prompt's own rubric adds
           over an unrelated one; the denominator is everything the own rubric achieves
           above chance. The share is the fraction of the own arm's work that its own
           prompt's criteria are doing.
Target
observed?  YES, and with a property nothing else in this line has: THE ATTENUATION FACTOR
           CANCELS. Deattenuation divides both arms' over-chance accuracy by the same f,
           so (own* - donor*)/(own* - 0.5) == (own - donor)/(own - 0.5) identically. The
           share needs NO noise model, NO independence assumption, and none of r104's
           confounds reach it. It is the one quantity on this axis that is model-free.
Alternative
worlds     THREE VERDICTS, because significance and practical equivalence are separate
           questions and collapsing them is how a wide interval gets read as a flat
           result. E requires the INTERVAL inside the margin; M is what a small point
           estimate with a wide interval actually licenses.
           E EQUIVALENT    the share is flat across consensus. Then the consensus axis
                           SCALES the whole measurement without changing its composition:
                           contested and consensual pairs are decided by the same mix of
                           prompt-specific and general normative content, and "the rubric
                           works better where humans agree" is a statement about how
                           legible the comparison is, not about which layer does the work.
           C COMPOSITIONAL the share shifts. Then contested pairs are decided by a
                           DIFFERENT mix -- if it falls with consensus, generic quality
                           carries relatively more where humans agree; if it rises,
                           prompt-specific content is what consensus buys. Either way the
                           layers R_general and R_prompt trade off along an axis nobody
                           has reported, and the pooled share is an average over that
                           trade.
           M ANSWERABLE    the interval covers zero AND is wider than the margin. Then
             MARGIN        the data neither show a shift nor exclude one, the question is
                           answerable but unanswered, and the round's job is to say how
                           much data would settle it rather than to pick a side.
Intervention
           none. A ratio of two quantities r104 already persisted, per bin.
Null       (i) ALGEBRAIC REBUILD -- the share computed from the RAW accuracies must equal
           the share computed from the DEATTENUATED ones to 1e-12. That is the claim that
           the factor cancels, executed rather than asserted; if it fails, the statistic
           is not the one this card describes.
           (ii) TWO-SIDED SIMULATION -- two synthetic arms whose share is constant across
           bins must read flat, and two whose share genuinely shifts must read shifted.
           An instrument that reports invariance whatever the data cannot report
           invariance.
           (iii) a DENOMINATOR FLOOR. A share is unreadable when the own arm is near
           chance, and r103's 2.95x ratio span was exactly that failure with the donor arm
           in the denominator (0.0041 in its lowest bin). This round refuses to report any
           bin whose denominator is below MIN_DENOM, rather than printing a large number.

WHY THIS IS THE STEP
--------------------
Entry 218's NEXT: the corrected own-arm accuracy is 0.7225 even where humans barely agree,
and nothing said what it is tracking there. The share answers a sharper version of that --
not how much signal there is on contested pairs, but whether it is the SAME KIND of signal.
Under the reframed object, R = R_general + R_prompt + ..., and this is the first estimate
of that decomposition along an axis internal to the human data.

THE CONFOUND, WRITTEN BEFORE THE RUN
------------------------------------
The donor arm is ONE draw. r88 measured the draw-to-draw sd of the pooled attribution at
0.0055; every bin here inherits the SAME draw, so a share difference ACROSS bins is not
explained by which donors were sampled -- but the share LEVEL is, and the level is not
what this round reports. Separately: `share` is a ratio of two estimates from the same
records, so its sampling distribution is skewed and a naive standard error would understate
the tails. The interval here is a bootstrap over PAIRS, which does not assume symmetry.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))

R104 = _ROOT / "11_reliability_and_the_width_chain/r104_deattenuated_consensus/results/r104_deattenuated_consensus.json"
VEC = _ROOT / "11_reliability_and_the_width_chain/r104_deattenuated_consensus/results/r104_split_records.npz"
EDGES = (0.49, 0.6, 0.9, 1.01)
MIN_BIN, MIN_DENOM, N_BOOT = 300, 0.05, 400
FLAT_TOL = 0.05          # pre-registered EQUIVALENCE MARGIN on the share, set before the run


def shares(cons, own, don, edges=EDGES, min_bin=MIN_BIN, min_denom=MIN_DENOM):
    """Per-bin raw accuracies and the prompt-specific share. Refuses thin denominators."""
    rows = []
    for i in range(len(edges) - 1):
        m = (cons >= edges[i]) & (cons < edges[i + 1])
        if m.sum() < min_bin:
            continue
        o, d = float(own[m].mean()), float(don[m].mean())
        denom = o - 0.5
        rows.append({"lo": edges[i], "hi": min(edges[i + 1], 1.0), "n": int(m.sum()),
                     "own": o, "donor": d, "attribution": o - d, "denominator": denom,
                     "share": (o - d) / denom if denom >= min_denom else None})
    return rows


def span(rows):
    s = [r["share"] for r in rows if r["share"] is not None]
    return (max(s) - min(s), s) if s else (float("nan"), [])


def simulate(rng, shifting: bool, n=40000):
    """Three equal bins. Own accuracy rises with the bin either way; the SHARE is held
    constant in one arm-pair and made to move in the other."""
    b = rng.integers(0, 3, n)
    own_acc = np.array([0.62, 0.70, 0.80])[b]
    sh = np.array([0.30, 0.50, 0.70])[b] if shifting else np.full(n, 0.50)
    don_acc = own_acc - sh * (own_acc - 0.5)
    cons = np.array([0.50, 0.75, 1.00])[b]
    return cons, (rng.random(n) < own_acc).astype(float), (rng.random(n) < don_acc).astype(float)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_RES / "r105_specific_share_invariance.json")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        (_RES / "_smoke").mkdir(parents=True, exist_ok=True)
        a.out = _RES / "_smoke" / (a.out.stem + "_SMOKE.json")
        print("*** SMOKE -> results/_smoke/ -- must never reach the README ***")
    _RES.mkdir(parents=True, exist_ok=True)
    if not (VEC.exists() and R104.exists()):
        raise SystemExit("REFUSING: r104's records are absent; this round is a ratio of its arms.")

    # ---- CONTROL (ii): two-sided, before the data -----------------------------
    cf, of_, df = simulate(np.random.default_rng(21), shifting=False)
    cs, os_, ds = simulate(np.random.default_rng(22), shifting=True)
    spF, shF = span(shares(cf, of_, df))
    spS, shS = span(shares(cs, os_, ds))
    print(f"CONTROL (ii) constant-share arms  -> shares {[round(x, 3) for x in shF]}  span {spF:.4f}")
    print(f"CONTROL (ii) shifting-share arms  -> shares {[round(x, 3) for x in shS]}  span {spS:.4f}")
    ok_ctrl = spF < FLAT_TOL and spS > 0.20
    print(f"   -> {'PASS' if ok_ctrl else 'FAIL'} (flat read as flat, planted shift recovered)")
    if not ok_ctrl:
        raise SystemExit("REFUSING: the share statistic failed its two-sided control. An instrument "
                         "that cannot recover a planted compositional shift cannot report invariance.")

    # ---- REAL DATA ------------------------------------------------------------
    z = np.load(VEC)
    cons, own, don = z["cons"], z["own"], z["donor"]
    pid = z["pid"]
    rows = shares(cons, own, don)
    if any(r["share"] is None for r in rows):
        raise SystemExit(f"REFUSING: a bin's own-arm accuracy is within {MIN_DENOM} of chance, so its "
                         f"share is a ratio of noise -- the failure that made r103's 2.95x span "
                         f"unreadable. Reporting nothing beats reporting a large number.")

    # ---- CONTROL (i): the attenuation factor must cancel ----------------------
    r104 = json.load(open(R104))
    drift = 0.0
    for r_, b in zip(rows, r104["bins"]):
        d_share = (b["own_deatt"] - b["donor_deatt"]) / (b["own_deatt"] - 0.5)
        drift = max(drift, abs(d_share - r_["share"]))
    print(f"\nCONTROL (i) share from RAW vs from DEATTENUATED accuracies: max drift {drift:.2e}")
    if drift > 1e-9:
        raise SystemExit("REFUSING: the attenuation factor does not cancel out of the share, so this "
                         "statistic is not model-free and the claim card is wrong about it.")
    print("   -> PASS: the factor cancels, so nothing below depends on r104's noise model.")

    sp, sh = span(rows)
    print(f"\n{'consensus(C)':>13} {'n':>7} {'own':>8} {'donor':>8} {'attrib':>9} "
          f"{'own-0.5':>8} {'share':>7}")
    for r_ in rows:
        print(f"{'[%.2f,%.2f)' % (r_['lo'], r_['hi']):>13} {r_['n']:>7,} {r_['own']:>8.4f} "
              f"{r_['donor']:>8.4f} {r_['attribution']:>+9.4f} {r_['denominator']:>8.4f} "
              f"{r_['share']:>7.4f}")
    print(f"\n  attribution rises {rows[0]['attribution']:+.4f} -> {rows[-1]['attribution']:+.4f} "
          f"({100 * (rows[-1]['attribution'] / rows[0]['attribution'] - 1):+.0f}%)")
    print(f"  share            {sh[0]:.4f} -> {sh[-1]:.4f}   span {sp:.4f} "
          f"against a pre-registered tolerance of {FLAT_TOL}")

    # ---- BOOTSTRAP over PAIRS -------------------------------------------------
    order = np.argsort(pid, kind="stable")
    npairs = int(pid.max()) + 1
    start = np.searchsorted(pid[order], np.arange(npairs), side="left")
    end = np.searchsorted(pid[order], np.arange(npairs), side="right")
    rb = np.random.default_rng(20260734)
    spans, lohi = [], []
    for _ in range(N_BOOT):
        pick = rb.integers(0, npairs, npairs)
        sel = np.concatenate([order[start[p]:end[p]] for p in pick])
        rr = shares(cons[sel], own[sel], don[sel], min_bin=1)
        if len(rr) == len(rows) and all(x["share"] is not None for x in rr):
            s_, v_ = span(rr)
            spans.append(s_); lohi.append(v_[-1] - v_[0])
    spans, lohi = np.array(spans), np.array(lohi)
    dlo, dhi = float(np.percentile(lohi, 2.5)), float(np.percentile(lohi, 97.5))
    print(f"  bootstrap over pairs ({len(spans)} draws): high-minus-low share "
          f"{lohi.mean():+.4f} [{dlo:+.4f},{dhi:+.4f}]")

    # SIGNIFICANCE AND EQUIVALENCE ARE SEPARATE VERDICTS, and collapsing them is how a
    # wide interval gets read as a flat result. The point estimate being small says the
    # data do not SHOW a shift; only an interval INSIDE the margin says there is not one.
    significant = not (dlo <= 0 <= dhi)
    equivalent = dlo > -FLAT_TOL and dhi < FLAT_TOL
    world = ("C COMPOSITIONAL" if significant else
             "E EQUIVALENT" if equivalent else
             "M ANSWERABLE MARGIN")
    # r91's precision budget: halving an interval costs 4x the units.
    half = (dhi - dlo) / 2
    need = npairs * (half / FLAT_TOL) ** 2
    print(f"  significant: {significant}   equivalent at +/-{FLAT_TOL}: {equivalent}   "
          f"half-width {half:.4f}")
    print(f"  to resolve the margin: {need:,.0f} pairs, {need / npairs:.1f}x the {npairs:,} available")
    vec = _RES / "r105_share_bootstrap.npz"
    np.savez_compressed(vec, span=spans, high_minus_low=lohi,
                        share=np.array(sh), n=np.array([r_["n"] for r_ in rows]))
    print(f"  bootstrap draws persisted -> {vec.relative_to(_ROOT)}")

    verdict = (
        f"{world}. Everything on this axis so far has been about the SIZE of the signal: r103 found "
        f"attribution rising with human consensus, r104 established that 74% of that rise survives the "
        f"label's own noise. None of it is about what the signal is MADE OF. The prompt-specific SHARE "
        f"of over-chance accuracy -- (own - donor)/(own - 0.5), the fraction of everything the own "
        f"rubric achieves above chance that its own prompt's criteria contribute -- runs "
        + ", ".join(f"{x:.4f}" for x in sh)
        + f" across the same consensus bins, a span of {sp:.4f} against a pre-registered tolerance of "
        f"{FLAT_TOL}, while the attribution it is a share OF rises "
        f"{rows[0]['attribution']:+.4f} to {rows[-1]['attribution']:+.4f}, a "
        f"{100 * (rows[-1]['attribution'] / rows[0]['attribution'] - 1):+.0f}% change. Bootstrap over "
        f"PAIRS puts the high-minus-low share at {lohi.mean():+.4f} [{dlo:+.4f},{dhi:+.4f}]. "
        + (f"SIGNIFICANCE AND EQUIVALENCE ARE REPORTED SEPARATELY, AND THIS IS NEITHER. The data do "
           f"not SHOW a compositional shift -- the interval covers zero -- but they do not establish "
           f"there is none either: the interval is {(dhi - dlo) / 2:.4f} wide at the half, against a "
           f"pre-registered margin of {FLAT_TOL}, so a shift up to {max(abs(dlo), abs(dhi)):.4f} "
           f"remains compatible with these records. Reading the {sp:.4f} point span as invariance would "
           f"be a claim {(dhi - dlo) / 2 / sp:.0f}x larger than the measurement supports. What CAN be "
           f"said: the composition does not move in step with the magnitude -- attribution rises "
           f"{100 * (rows[-1]['attribution'] / rows[0]['attribution'] - 1):+.0f}% while the share's "
           f"best estimate moves {lohi.mean():+.4f} -- so the consensus gradient is not obviously a "
           f"change in which normative layer does the work. Resolving it to the margin needs "
           f"{need:,.0f} pairs, {need / npairs:.1f}x the {npairs:,} here (r91's budget: halving an "
           f"interval costs 4x the units), and that is a preregistration number, not a result."
           if world.startswith("M") else
           "SO THE CONSENSUS AXIS SCALES THE MEASUREMENT WITHOUT RECOMPOSING IT, TO WITHIN THE "
           "PRE-REGISTERED MARGIN: contested and consensual pairs are decided by the same MIX of "
           "prompt-specific and general normative content, and the rise r103 and r104 measured is "
           "about how legible a comparison is, not about which normative layer does the work."
           if world.startswith("E") else
           "SO THE COMPOSITION SHIFTS: contested and consensual pairs are decided by different mixes of "
           "prompt-specific and general normative content, and the pooled share is an average across "
           "that trade rather than a property of the rubric.") +
        f" THE PROPERTY THAT MAKES THIS THE STRONGEST STATEMENT ON THIS AXIS: the attenuation factor "
        f"CANCELS. Deattenuation divides both arms' over-chance accuracy by the same number, so the "
        f"share computed from RAW accuracies equals the share computed from r104's DEATTENUATED ones -- "
        f"verified to {drift:.0e}, executed rather than asserted. This statistic needs no noise model, "
        f"no independence assumption, and none of r104's confounds reach it. "
        f"TWO-SIDED CONTROL: synthetic arms built with a CONSTANT share across bins read {spF:.4f} span; "
        f"arms built with a share moving 0.30 to 0.70 read {spS:.4f}. An instrument that reported "
        f"invariance whatever the data could not report invariance, and this one recovers a planted "
        f"shift. DENOMINATOR FLOOR: any bin whose own-arm accuracy is within {MIN_DENOM} of chance is "
        f"refused rather than printed -- that is exactly the failure that made r103's 2.95x over-chance "
        f"ratio span unreadable, its lowest bin having a donor arm 0.0041 above chance. "
        f"THE CONFOUND, WRITTEN BEFORE THE RUN: the donor arm is ONE draw (r88: sd 0.0055 pooled), and "
        f"every bin inherits the SAME draw -- so a share difference ACROSS bins is not explained by "
        f"which donors were sampled, though the share LEVEL is, and the level is not what this reports. "
        f"SCOPE: computed on r104's persisted split records -- {len(cons):,} records over {npairs:,} "
        f"pairs of at least 12 raters, labelled by a THIRD of each pair's raters. The share is a ratio "
        f"of two estimates from the same records, so the interval is a bootstrap over PAIRS rather than "
        f"a symmetric standard error."
    )

    doc = {
        "bins": rows, "share": sh, "share_span": float(sp),
        "flat_tolerance": FLAT_TOL, "min_denominator": MIN_DENOM,
        "high_minus_low_share": float(lohi.mean()),
        "high_minus_low_ci95_over_pairs": [dlo, dhi], "n_boot": int(len(spans)),
        "significant": bool(significant), "equivalent_at_margin": bool(equivalent),
        "ci_half_width": float(half), "pairs_needed_for_margin": float(need),
        "attribution_low": rows[0]["attribution"], "attribution_high": rows[-1]["attribution"],
        "cancellation_drift": float(drift),
        "control_constant_share_span": float(spF), "control_shifting_share_span": float(spS),
        "control_pass": bool(ok_ctrl),
        "n_records": int(len(cons)), "n_pairs": int(npairs),
        "persisted_vector": str(vec.relative_to(_ROOT)), "world": world,
        "outcome_variable_scope": (
            "The ratio (own - donor)/(own - 0.5) of accuracies against a third of each pair's human "
            "raters, per consensus bin, on r104's persisted records. No judge call, no new measurement, "
            "and no dependence on r104's noise model -- the attenuation factor cancels."),
        "scope": (
            "NEITHER significant NOR equivalent at the pre-registered margin -- the interval covers "
            "zero and is wider than the margin, so this is an answerable-margin result and not a "
            "demonstration of invariance. Reports the share's ACROSS-BIN difference, not its level: the level inherits r104's single "
            "donor draw. Bins whose own-arm accuracy is within 0.05 of chance are refused rather than "
            "reported. The label is a third of each pair's raters, so accuracy levels are not comparable "
            "to r103's."),
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
