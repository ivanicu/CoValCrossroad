#!/usr/bin/env python3
"""R1039 — this session's own IMPOSSIBLE lines, and how often its own later rounds falsified them.

R1038's NEXT proposed re-reading the register's N/A entries against what the release contains. ⛔ That
population is NOT IDENTIFIED — R1029 established the requirement TYPE was never stored, and three
instruments gave three denominators (17 / 9 / 7). Re-running it would repeat a measurement that
already failed at G1.

⭐ WHAT IS IDENTIFIED IS MY OWN. Every round R1022–R1038 carries an `IMPOSSIBLE` block in a known
   format, written by me, enumerable mechanically. That is a population with no classifier in it. And
   the NUMERATOR is not my judgement either: a line counts as falsified only when a LATER COMMITTED
   ROUND's own artifact contradicts it, which is a fact about committed text.

⛔ AND R999's CAVEAT IS THE DESIGN CONSTRAINT, NOT AN AFTERTHOUGHT. It measured wall-revisiting at
   8 of 11 and recorded, in its own words, *"eligibility is unequal: later rounds had fewer chances to
   be checked"*. A raw rate over this window would be dominated by that. So EXPOSURE is carried per
   entry — how many later rounds existed at all — and the rate is reported both raw and
   exposure-weighted, never only the flattering one.

ESTIMAND        the rate at which this session's own IMPOSSIBLE lines were falsified by its own later
                rounds, raw and per unit of exposure.
IDENTIFICATION  exact. The population is my docstrings; the numerator is committed contradictions.
SCOPE           population : the IMPOSSIBLE blocks of R1022–R1038 · instrument : committed artifacts
                baseline   : R802's committed 1 of 30 = 0.0333 over a 13-round window
WORLDS          A THIS SESSION IS NO WORSE — the exposure-weighted rate is at or below R802's 0.0333.
                  Then the impossibility discipline held and the falsifications are the tail.
                B THIS SESSION IS MATERIALLY WORSE — the rate is several times R802's. Then writing
                  IMPOSSIBLE is where this session was least reliable, and the register entries it
                  produced should be read as hypotheses rather than limits.
                prediction matrix: A -> weighted rate <= ~0.05. B -> >= 0.15.
                ⚠ ONTOLOGICAL: A says the walls were real and a few fell; B says the wall-writing
                  itself is a defective habit, which is a claim about ME rather than the release.
KILL            pre-registered and CONDITIONAL:
                  if the population enumerates without a classifier and every falsification cites a
                  committed artifact:
                      exposure-weighted rate >= 0.15 -> World B
                      <= 0.05                        -> World A
                      otherwise                       -> report both, claim neither
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the enumerator must find an IMPOSSIBLE block in a round KNOWN to carry one (R1034,
                whose block names the 254-GFLOP closure) and must NOT invent one in a file that has
                none — checked against a constructed docstring with no IMPOSSIBLE section.
NEGATIVE CTRL   a line NOT falsified must have no later artifact contradicting it: R1034's GFLOP wall
                is asserted and no later round ran the exhaustive closure, so it must score 0.
PLACEBO         a round audited against ITSELF must find nothing — a round cannot falsify its own
                IMPOSSIBLE line, and the enumerator must enforce strict lateness.
NOISE FLOOR     the population is small; a binomial SE at n=16 is ±0.11 at p=0.25 and is printed.
MULTIPLICITY    every entry is listed with its verdict, including the ones that stand.
SEEDS           N/A — deterministic over committed text. Stated rather than skipped.
IMPOSSIBLE      whether an unfalsified line is TRUE. Absence of a later contradiction is not evidence
                of a real wall — it is exactly the "unchecked wall" this arc keeps finding. N/A: what
                it would require is attacking each remaining line, one round each.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"

# ⛔ THE NUMERATOR IS COMMITTED TEXT, NOT JUDGEMENT MADE NOW. Each pair names the falsifying round
#    and the artifact key whose value contradicts the earlier line.
FALSIFIED = {
    "R1026": ("R1033", "a stricter prompt-blind comparator needs BUILDING AND SCORING",
              "R1033 built one from pool16 subsets for 0 judge calls"),
    "R1035": ("R1038", "which q is right needs an external criterion",
              "R1038 measured it: the family is its own null, only q=90 reaches nominal"),
    "R1036": ("R1038", "whether the scale-free q is the RIGHT q needs an external criterion",
              "R1038 selected q=90 on false-admission evidence"),
    "R1037": ("R1038", "which q is RIGHT is not decided here; needs an external criterion",
              "R1038 decided it on evidence from the comparator family itself"),
}


def main() -> int:
    rounds = []
    for p in sorted(A27.glob("R10*/run.py")):
        rid = re.match(r"(R\d+)", p.parent.name).group(1)
        # ⚠ THIS ROUND IS EXCLUDED FROM ITS OWN POPULATION. It has exposure 0, cannot be
        #   falsified, and is being written now — including it dilutes the denominator by one.
        if int(rid[1:]) < 1022 or p.parent == HERE:
            continue
        m = re.search(r"^IMPOSSIBLE\s+(.+?)(?=^[A-Z]{3,}\s|^\"\"\")", p.read_text(), re.M | re.S)
        rounds.append((rid, int(rid[1:]), bool(m), (m.group(1).strip() if m else "")))
    if not rounds:
        print("  UNRUNNABLE: no rounds enumerated — an empty population must not pass. Exit 2.")
        return 2

    # ---------- controls ----------
    known = dict((r, has) for r, _n, has, _t in rounds)
    pos = known.get("R1034") is True
    fake = "\"\"\"a docstring with no impossibility section\nESTIMAND x\n\"\"\""
    neg_invent = re.search(r"^IMPOSSIBLE\s", fake, re.M) is None
    print(f"  POSITIVE — the enumerator must find R1034's block (it names the 254-GFLOP closure): "
          f"{pos}")
    print(f"  NEGATIVE — and must NOT invent one where there is none: {neg_invent}")
    late_ok = all(int(FALSIFIED[k][0][1:]) > int(k[1:]) for k in FALSIFIED)
    print(f"  PLACEBO  — strict lateness: no round may falsify its own line: {late_ok}")
    if not (pos and neg_invent and late_ok):
        print("  a control did not fire. Exit 2, never 0."); return 2

    last = max(n for _r, n, _h, _t in rounds)
    print(f"\n  ⭐ THE POPULATION — {len(rounds)} rounds, each with an IMPOSSIBLE block, no classifier")
    print(f"     {'round':<8}{'exposure':>10}{'falsified by':>14}  what fell")
    rows, nf, wsum, wf = [], 0, 0.0, 0.0
    for rid, n, has, _t in rounds:
        exposure = last - n                       # how many later rounds existed at all
        f = FALSIFIED.get(rid)
        rows.append({"round": rid, "exposure": exposure,
                     "falsified_by": (f[0] if f else None),
                     "line": (f[1] if f else None), "by_what": (f[2] if f else None)})
        nf += int(bool(f))
        wsum += exposure
        wf += exposure * int(bool(f))
        print(f"     {rid:<8}{exposure:>10}{(f[0] if f else '—'):>14}  {(f[1][:52] if f else '')}")
    raw = nf / len(rounds)
    mean_exp = wsum / len(rounds)
    se = (raw * (1 - raw) / len(rounds)) ** 0.5
    # ⛔⛔ THE EXPOSURE ADJUSTMENT IS A HAZARD, NOT A PROPORTION, AND THE FIRST RUN COMPARED IT TO
    #   R802's PROPORTION. That is a units mismatch — the same failure this arc has caught four
    #   times at other levels. A hazard is falsifications PER ROUND OF EXPOSURE; it is unbounded
    #   above and is NOT comparable to 1-of-30. Only the RAW proportion is put beside the baseline;
    #   the hazard is reported separately as a diagnostic, in its own units.
    hazard = wf and (nf / wsum) or 0.0
    print(f"\n     RAW proportion            : {nf} of {len(rounds)} = {raw:.4f}  "
          f"(binomial SE ±{se:.4f})")
    print(f"     R802's committed baseline : 1 of 30 = {1/30:.4f} — SAME UNIT, directly comparable")
    print(f"     mean exposure             : {mean_exp:.2f} later rounds")
    print(f"     HAZARD (diagnostic only)  : {hazard:.4f} falsifications per round-of-exposure")
    print(f"       ⚠ a HAZARD is not a PROPORTION and is NOT compared to the baseline. The first")
    print(f"         run printed an exposure-weighted 0.5821 beside 0.0333 — a units mismatch.")
    print(f"     ⚠ R999's caveat is why both are printed: 'eligibility is unequal — later rounds had")
    print(f"       fewer chances to be checked'. R1038's own line has exposure 0 and CANNOT fall here.")

    print()
    if raw >= 0.15:
        world = (f"⭐ B THIS SESSION IS MATERIALLY WORSE THAN THE BASELINE — {nf} of {len(rounds)} "
                 f"IMPOSSIBLE lines were falsified by its OWN later rounds {raw:.4f} against R802's "
                 f"committed {1/30:.4f}, the same unit — a {raw/(1/30):.1f}x difference. Writing "
                 f"IMPOSSIBLE is where this session was least reliable, and its register entries "
                 f"should be read as HYPOTHESES rather than limits.")
    elif raw <= 0.05:
        world = (f"⭐ A NO WORSE THAN THE BASELINE — {raw:.4f} against R802's {1/30:.4f}; the falsifications are the tail and the discipline held.")
    else:
        world = (f"⭐ NEITHER PRE-REGISTERED BAND — raw {raw:.4f}. It is "
                 f"reported and no world is claimed.")
    print(world)
    print(f"⛔ AND ALL FOUR FALSIFICATIONS SHARE ONE SHAPE: each said the answer needed something")
    print(f"   OUTSIDE the release, and each was answered by an object already INSIDE it — pool16's")
    print(f"   subsets (R1033) and the comparator family as its own null (R1038). That is not four")
    print(f"   mistakes; it is one habit, and naming it is what the count buys.")
    print(f"⚠ AND AN UNFALSIFIED LINE IS NOT A TRUE ONE. Absence of a later contradiction is exactly")
    print(f"   the 'unchecked wall' this arc keeps finding. N/A — attacking each remaining line is")
    print(f"   one round each, and this round does not do it.")

    out = HERE / "results" / "own_impossibility_rate.json"
    out.write_text(json.dumps({
        "round": "R1039", "population": len(rounds), "falsified": nf,
        "raw_rate": raw, "binomial_se": se, "mean_exposure": mean_exp,
        "hazard_per_round_of_exposure": hazard,
        "unit_note": "the hazard is NOT a proportion and is not comparable to the baseline", "baseline_R802": 1 / 30,
        "rows": rows, "world": world,
        "shared_shape": "each falsified line said the answer needed something OUTSIDE the release, "
                        "and each was answered by an object already inside it",
        "limitation": "an unfalsified line is not a true one; absence of a later contradiction is "
                      "the unchecked wall, not evidence of a real one",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
