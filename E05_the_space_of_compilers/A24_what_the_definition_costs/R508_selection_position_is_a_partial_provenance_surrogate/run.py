"""R503 said both sides of ③ draw from the same pool. Then the signature must be in the SELECTION.

WHY THIS IS NEW AND R501 COULD NOT HAVE TRIED IT. R501 asked whether a behavioural statistic can
replace clause ③ and failed its own positive control: per-prompt A2 dispersion could not place
`oracle_k4` outside the middle of the pack. R503 then measured that every ③-excluded arm draws
**100.0%** of its criteria VERBATIM from the prompt's own rubric — and so do the ③-admissible
`random_k*` arms. If the pool is shared and the text is identical, the only thing that can differ is
WHICH ITEMS ARE PICKED. That reframes the surrogate search from the criteria to the selection, and it
was not available before R503.

ESTIMAND        Per arm: the mean NORMALISED POSITION of its selected criteria within the prompt's
                own rubric list, and whether that separates ③-excluded arms from ③-admissible ones.
                Named before the method.
IDENTIFICATION  Identified as a SEPARATION question only. A positive answer says a surrogate exists
                on this arm population, never that it would catch an unseen selector — and the
                round reports which known readers it MISSES, because a surrogate with a blind spot
                is a surrogate whose nulls are silence for whatever lives in the blind spot.
SCOPE           population = arms with criterion text on the first release · instrument = index of
                each selected criterion within `core_full.json`'s list for that prompt, normalised
                to [0,1] · baseline = the random arms, which must land at 0.5 · regime = first
                release.

⛔ THE ARITHMETIC TRAP, NAMED FIRST. Some ③-excluded arms are DEFINED by a selection rule over the
                rubric's own ordering — `topw_k4` picks top-weighted items. For those, any relation
                between selection and position is FORCED, and finding one is a derivation. That does
                NOT make the surrogate useless: the question is whether a third party can DETECT
                provenance, not whether the detection is surprising. But it does mean a positive
                result on `topw`-family arms is worth nothing on its own, and the round is judged on
                the arms whose rule is not stated in terms of position.
WORLDS          A COMPLETE SURROGATE. Every ③-excluded arm separates from the admissible ones. Then
                  ③ is replaceable by a checkable clause and the formulation fork dissolves.
                B PARTIAL SURROGATE. Some separate and some do not. Then ③ is not replaceable, but
                  the failure is localised: we learn WHICH provenance is detectable and which hides.
                C NO SURROGATE. Nothing separates once the position-defined arms are set aside.
KILL            Pre-registered: if any ③-excluded arm lands inside the random arms' band, world A is
                dead. No amount of separation elsewhere rescues it — a surrogate that misses one
                known reader cannot certify an unknown one.
POSITIVE CTRL   `oracle_k4` — the maximal label-reader — must separate. If the most extreme case
                does not, the statistic is blind and every other number is silence.
NEGATIVE CTRL   The `random_k*` arms must land at 0.5 within noise. They select uniformly from the
                pool by construction, so any departure means the position index is malformed.
PLACEBO         `generic` and `gen` draw 0% from the pool (R503), so they have NO positions at all;
                the round must report them as N/A rather than as a number.
NOISE FLOOR     Measured as the spread across the three `random_k4` seeds.
MULTIPLICITY    Every arm with text is reported; none is selected after the fact.
SPECIFICATION   Swept: normalised mean position · median position · fraction in the first quartile.
                Disagreement between them is reported rather than resolved by preference.
SEEDS           N/A for the statistic (deterministic); the random ARMS supply three independent
                draws of the null.
ARTIFACT        results/selection_position.json
IMPOSSIBLE      whether `core_full.json`'s list order encodes quality is not established here — the
                round uses position as an OPAQUE index and reports separation, not meaning. If the
                order is arbitrary, the random arms would still sit at 0.5 and the readers would
                not separate, so the design degrades to a null rather than to a false positive.
"""
from __future__ import annotations
import json, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
R = ROOT/"corebench"/"results"
OUT = pathlib.Path(__file__).resolve().parent/"results"; OUT.mkdir(exist_ok=True)
FULL = json.loads((R/"core_full.json").read_text())
READER = ["oracle_k4","oracle_k4_fit1","greedy_k4_fit1","indep_k4_fit1","topw_k4","topw_k2",
          "topw_k8","topabs_k4","topvar_k4","topwvar_k4"]
FREE = ["gen","generic","genericpool16","random_k4_s0","random_k4_s1","random_k4_s2",
        "random_k3_s0","random_k8_s0","promptecho"]
# Arms whose selection rule is STATED in terms of the rubric's own ordering. A position effect here
# is forced by the algebra and is a derivation, not evidence.
POSITION_DEFINED = {"topw_k4","topw_k2","topw_k8","topabs_k4","topvar_k4","topwvar_k4"}


def stats(arm):
    f = R/f"core_{arm}.json"
    if not f.exists(): return None
    o = json.loads(f.read_text()); pos = []
    for p, cs in o.items():
        pool = FULL.get(p) or []
        if len(pool) < 2: continue
        idx = {c: i for i, c in enumerate(pool)}
        for c in (cs if isinstance(cs, list) else []):
            if c in idx: pos.append(idx[c]/(len(pool)-1))
    if not pos: return dict(n=0)
    v = np.array(pos)
    return dict(n=len(v), mean=float(v.mean()), median=float(np.median(v)),
                q1frac=float((v <= 0.25).mean()))


def main() -> int:
    rows = {a: s for a in READER+FREE if (s := stats(a))}
    rnd = [rows[a]["mean"] for a in ("random_k4_s0","random_k4_s1","random_k4_s2") if rows.get(a, {}).get("n")]
    if len(rnd) < 3:
        print("  the random arms are missing -- no null, refusing to report"); return 2
    lo, hi, floor = min(rnd), max(rnd), max(rnd)-min(rnd)
    print(f"  NEGATIVE CONTROL: random_k4 arms must sit at 0.5 -> {rnd[0]:.4f}, {rnd[1]:.4f}, "
          f"{rnd[2]:.4f}  spread {floor:.4f}"
          f"  -> {'PASS' if all(abs(x-0.5) < 0.02 for x in rnd) else 'FAIL'}")
    if not all(abs(x-0.5) < 0.02 for x in rnd):
        print("  uniform selectors do not land at 0.5 -- the position index is malformed"); return 1

    band = (lo-2*floor, hi+2*floor)
    print(f"  null band from the random arms: [{band[0]:.4f}, {band[1]:.4f}]\n")
    print(f"  {'arm':<18}{'family':>8}{'n':>7}{'mean pos':>10}{'median':>9}{'<=q1':>8}   verdict")
    sep, missed, na = [], [], []
    for a, s in sorted(rows.items(), key=lambda kv: (kv[1].get("mean", 9))):
        if not s["n"]:
            na.append(a); print(f"  {a:<18}{'free' if a in FREE else 'reader':>8}{0:>7}"
                                f"{'N/A':>10}{'N/A':>9}{'N/A':>8}   no rubric overlap (R503: 0%)")
            continue
        fam = "reader" if a in READER else "free"
        # ⚠ n is criteria, not prompts. `promptecho` contributes TWO, which is not a measurement;
        # a separation verdict on it would be an order statistic of a 2-sample. Reported as
        # underpowered rather than silently counted, which is the min/max-of-N-draws row.
        if s["n"] < 100:
            print(f"  {a:<18}{fam:>8}{s['n']:>7}{s['mean']:>10.4f}{s['median']:>9.4f}"
                  f"{s['q1frac']:>8.3f}   UNDERPOWERED (n={s['n']} criteria) -- not counted")
            continue
        out = not (band[0] <= s["mean"] <= band[1])
        tag = ("SEPARATES" + (" (position-defined: derivation)" if a in POSITION_DEFINED else "")) if out else "inside the null band"
        if fam == "reader":
            (sep if out else missed).append(a)
        print(f"  {a:<18}{fam:>8}{s['n']:>7}{s['mean']:>10.4f}{s['median']:>9.4f}"
              f"{s['q1frac']:>8.3f}   {tag}")

    pc = "oracle_k4" in sep
    print(f"\n  POSITIVE CONTROL: oracle_k4 separates -> {'PASS' if pc else 'FAIL'}")
    if not pc:
        print("  the maximal label-reader is invisible to this statistic -- the rest is silence"); return 1

    honest = [a for a in sep if a not in POSITION_DEFINED]
    world = ("A COMPLETE SURROGATE" if not missed else
             "B PARTIAL SURROGATE" if sep else "C NO SURROGATE")
    print(f"\n  ③-excluded arms that SEPARATE: {len(sep)}  of which not position-defined: {len(honest)} {honest}")
    print(f"  ③-excluded arms INSIDE the null band (missed): {len(missed)} {missed}")
    print(f"  arms with no rubric overlap, reported N/A rather than as a number: {na}")
    print(f"\n  WORLD: {world}")
    if world.startswith("B"):
        print(f"  => selection position detects some label-reading and not all. ③ is NOT replaceable")
        print(f"     by this clause: a surrogate that misses a KNOWN reader cannot certify an")
        print(f"     unknown one, which is the pre-registered kill and it fired.")
        print(f"  => but the failure is LOCALISED, which R501's could not be: {honest} are caught by")
        print(f"     a rule not stated in terms of position, so label-reading DOES leave a trace")
        print(f"     the artifact carries. The fork survives; its ②-side is now narrower.")
    json.dump({"rows": rows, "null_band": band, "separates": sep, "missed": missed,
               "na": na, "honest": honest, "world": world}, (OUT/"selection_position.json").open("w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
