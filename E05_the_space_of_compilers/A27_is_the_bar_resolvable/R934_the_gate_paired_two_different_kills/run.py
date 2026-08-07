#!/usr/bin/env python3
"""
R934 · R235's "significance flag contradicts its own interval" is the GATE's defect, not R235's —
        and the refusal that would have prevented it is already computed one branch away.

⛔ WHY. `artifacts_are_internally_coherent` reported two things: six R141 points outside their own
intervals (R929–R933 traced that to a real estimator defect, worth ~2× the magnitudes and no
verdicts) and **one significance flag contradicting its interval, in `R235_independent_B.E_verdict`**.

⭐ **THE GAUGE TEST ON THE NAMES SETTLED IT BEFORE ANY COMPUTE.** The reported pair is
`K4prime_core_minus_topw_ci` against `K2_majority_negative_significant`. **`K4prime` and `K2` are
different pre-registered kills.** `E_verdict`'s root holds `K1…K5` as SIBLINGS, each a separate
verdict, and the gate paired an interval from one with a boolean from another purely because they
share a parent dict and match its two regexes.

⭐⭐ **AND R235 IS COHERENT ON ITS OWN TERMS, measured:** `K4prime_core_minus_topw = −0.022443` sits
INSIDE `[−0.040650, −0.005036]`; `topw` beats `core` significantly in **76** cells and `core` beats
`topw` in **0**; and `K2` asks a different question entirely — whether a MAJORITY of cells are
negative-significant — where **76 of 286 is not a majority, so `False` is arithmetically right.**

⭐⭐⭐ **THE FIX IS ONE BRANCH, AND THE GATE ALREADY COMPUTES IT.** Invariant 1 (point inside its
interval) pairs only when the names are unambiguous, and carries three refusals — a stem match, a
null-summary guard, and `ci_spoken_for`: *"if the stem is a key here, the CI is spoken for"*.
Invariant 2 (flag agrees with interval) uses **sole candidacy alone**, with none of them. For R235,
`ci_stem = K4prime_core_minus_topw` **is** a key in that node, so `ci_spoken_for` is already True and
would have refused the pairing — it is computed four lines above and never applied to this branch.
**Fix-lands-on-one-path, inside the guard whose own docstring warns that cross-key pairs are "exactly
what r58's harvester got wrong".**

ESTIMAND        across every committed artifact: the number of `contradict` reports that survive
                applying invariant 1's existing refusals to invariant 2, and whether the R235 report
                is among them.
IDENTIFICATION  exact — a deterministic re-run of the gate's own pairing rule over the same corpus.
SCOPE           population: `E*/A*/[Rr]*/results/*.json`, the gate's own glob (case-fixed, R928)
                instrument: the gate's own CIISH / BOOLISH / MEANISH regexes, imported not retyped
                baseline:   the gate as committed
                regime:     the committed corpus
WORLDS          A · the R235 report disappears and a planted contradiction is still caught -> the
                    finding was a pairing artifact and the fix is safe
                B · the fix also silences a genuine contradiction -> it is too blunt and a different
                    discipline is needed
KILL            CONDITIONAL:
                  ⭐ ① WIRING: the unmodified rule must reproduce the gate's committed report —
                     exactly 1 `contradict`, and it must be the R235 pair. If it does not, this is
                     not the gate's rule and nothing measured here describes it.
                  ⭐ ② POSITIVE: a PLANTED node holding `gap` / `gap_ci` / `gap_significant` with a
                     flag that disagrees with its bounds must still be caught AFTER the fix. A fix
                     that silences everything is not a fix.
                  ⭐ ③ PLACEBO: invariant 1's `outside` list must be BIT-IDENTICAL before and
                     after — this touches only invariant 2, and R929–R933's six R141 cells must
                     survive untouched.
                     ⛔ AND IT PASSED VACUOUSLY ON THE FIRST RUN, WHICH IS A CHECK THAT CANNOT
                     FAIL. It compared `outside` 0 before against 0 after — bit-identical, and
                     empty, because my re-implementation carried only invariant 1's STEM-MATCH
                     route. R141's cells pair `delta_mean` with a bare `ci`, which no stem rule
                     matches; they come through the SOLE-CANDIDATE route I had omitted. **An empty
                     list is bit-identical to an empty list.** The placebo is now anchored to a
                     NUMBER the gate itself reports — it must find the 6 — so it cannot pass on
                     nothing.
                  ⭐ ④ the refusal must fire for the STATED reason: R235's pair must be declined
                     because `ci_spoken_for`, not because some threshold moved.
MULTIPLICITY    every node in every committed artifact; before/after counts for both invariants.
ARTIFACT        results/pairing_discipline.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: this makes invariant 2 REFUSE more pairs. It cannot show the
                refused ones are all harmless — only that the one it was asked about is, and that
                a planted true positive survives.
"""
import importlib.util, json, pathlib, re, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
GATE = ROOT / "assurance/artifacts_are_internally_coherent.py"


def load_gate():
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location("cohgate", GATE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def scan(g, apply_fix, extra=None):
    """the gate's own pairing rule, re-run; `apply_fix` gates invariant 2 the way invariant 1 is."""
    out = {"contradict": [], "outside": [], "n_flagged": 0}

    def walk(o, rid, path=""):
        if not isinstance(o, dict):
            if isinstance(o, list):
                for i, v in enumerate(o):
                    walk(v, rid, f"{path}[{i}]")
            return
        cks = [(k, o[k]) for k in o if g.CIISH.match(k) and g.is_ci(o[k])]
        mks = [(k, o[k]) for k in o if g.MEANISH.match(k) and isinstance(o[k], (int, float))
               and not isinstance(o[k], bool)]
        bks = [(k, o[k]) for k in o if g.BOOLISH.match(k) and isinstance(o[k], bool)]
        stem_hits = set()
        for mk, mv in mks:
            for ck, cv in cks:
                if mk.lower() in ck.lower() or ck.lower().replace("_ci", "") == mk.lower():
                    stem_hits.add((mk, ck))
                    lo, hi = sorted(cv)
                    if not (lo <= mv <= hi):
                        out["outside"].append((rid, path, mk, mv, ck, [lo, hi]))
        ci_stem = re.sub(r"_ci$|^ci_", "", cks[0][0], flags=re.I) if len(cks) == 1 else None
        ci_spoken_for = bool(ci_stem and ci_stem != cks[0][0] and ci_stem in o
                             and not any(ci_stem == m for m, _ in mks))
        # SOLE-CANDIDATE route for invariant 1 — omitted on the first run, which made the
        # placebo compare two empty lists. R141's `delta_mean` / `ci` pairs come through here.
        sole_is_null = len(mks) == 1 and bool(g.NULLNAME.search(mks[0][0]))
        if (len(mks) == 1 and len(cks) == 1 and not stem_hits and not sole_is_null
                and not ci_spoken_for):
            (mk, mv), (ck, cv) = mks[0], cks[0]
            lo, hi = sorted(cv)
            if not (lo <= mv <= hi):
                out["outside"].append((rid, path, mk, mv, ck, [lo, hi]))
        if len(cks) == 1 and len(bks) == 1:
            (ck, cv), (bk, bv) = cks[0], bks[0]
            bstem = re.sub(r"_significant$|^significant_?", "", bk, flags=re.I)
            cstem = re.sub(r"_ci$|^ci_", "", ck, flags=re.I)
            named_together = bool(bstem and cstem and (bstem.lower() in cstem.lower()
                                                       or cstem.lower() in bstem.lower()))
            refuse = apply_fix and ci_spoken_for and not named_together
            if not refuse:
                out["n_flagged"] += 1
                lo, hi = sorted(cv)
                if bool(lo > 0 or hi < 0) != bv:
                    out["contradict"].append((rid, path or "<root>", ck, [lo, hi], bk, bv,
                                              "ci_spoken_for" if ci_spoken_for else "-"))
        for k, v in o.items():
            walk(v, rid, f"{path}.{k}" if path else k)

    for f in sorted(ROOT.glob("E*/A*/[Rr]*/results/*.json")):
        if "_smoke" in str(f) or f.stat().st_size > 6_000_000:
            continue
        try:
            walk(json.loads(f.read_text()), f.parts[-3])
        except Exception:
            continue
    if extra is not None:
        walk(extra, "_PLANT")
    return out


def main() -> int:
    if not GATE.exists():
        print("  UNRUNNABLE: gate missing. Exit 2, never 0.")
        return 2
    g = load_gate()
    print(f"  gate regexes imported: CIISH={g.CIISH.pattern[:34]}… BOOLISH={g.BOOLISH.pattern[:34]}…")

    before = scan(g, apply_fix=False)
    c1 = (len(before["contradict"]) == 1
          and "R235_independent_B" in before["contradict"][0][0])
    print(f"\n  ① WIRING — the unmodified rule reproduces the gate's report:")
    print(f"     contradict reports: {len(before['contradict'])} (gate said 1)")
    for x in before["contradict"]:
        print(f"       {x[0]}:{x[1]}  {x[2]} {[round(y, 6) for y in x[3]]}  vs  {x[4]}={x[5]}"
              f"   ci_spoken_for={x[6]}")
    print(f"     ① {c1}  {'PASS' if c1 else 'FAIL'}")

    plant = {"gap": 0.05, "gap_ci": [0.04, 0.06], "gap_significant": False}
    after = scan(g, apply_fix=True, extra=plant)
    caught = [x for x in after["contradict"] if x[0] == "_PLANT"]
    c2 = len(caught) == 1
    print(f"\n  ② POSITIVE — a planted node `gap/gap_ci/gap_significant` whose flag disagrees with")
    print(f"     its own bounds must STILL be caught after the fix: {len(caught)} caught")
    print(f"     ② {c2}  {'PASS' if c2 else 'FAIL — the fix silences true positives too'}")

    # anchored to the gate's own reported number so it cannot pass on an empty list
    c3 = (before["outside"] == after["outside"] and len(before["outside"]) == 6
          and all("R141" in x[0] for x in before["outside"]))
    print(f"\n  ③ PLACEBO — invariant 1's `outside` must be bit-identical AND must actually find")
    print(f"     the 6 R141 cells the gate reports ({len(before['outside'])} before, "
          f"{len(after['outside'])} after, all R141: "
          f"{all('R141' in x[0] for x in before['outside']) if before['outside'] else False}): "
          f"{c3}  {'PASS' if c3 else 'FAIL'}")
    print(f"     ⚠ the first version compared 0 against 0 and passed on nothing")

    real_after = [x for x in after["contradict"] if x[0] != "_PLANT"]
    c4 = (len(real_after) == 0 and before["contradict"][0][6] == "ci_spoken_for") if c1 else False
    print(f"\n  ④ REFUSED FOR THE STATED REASON — R235's pair declined because `ci_spoken_for`, "
          f"not a moved threshold: {c4}  {'PASS' if c4 else 'FAIL'}")
    print(f"     real `contradict` reports after the fix: {len(real_after)}")

    if not (c1 and c2 and c3 and c4):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c2": c2, "c3": c3, "c4": c4,
                   "before": before["contradict"], "after": real_after},
                  open(OUT / "pairing_discipline.json", "w"), indent=2)
        return 2

    world = "A"
    print(f"\n  ⭐⭐⭐ WORLD {world}: the R235 report was a PAIRING ARTIFACT. `K4prime` and `K2` are")
    print(f"     different pre-registered kills sharing a parent dict, and the gate paired an")
    print(f"     interval from one with a boolean from the other. R235 is coherent on its own")
    print(f"     terms: K4prime = −0.022443 sits INSIDE [−0.040650, −0.005036], topw beats core in")
    print(f"     76 cells against 0, and K2 asks whether a MAJORITY of 286 cells are")
    print(f"     negative-significant — 76 is not a majority, so `False` is right.")
    print(f"     ⭐ AND THE REFUSAL WAS ALREADY THERE: invariant 1 computes `ci_spoken_for` and")
    print(f"     declines; invariant 2, four lines below, never applies it. The guard's own")
    print(f"     docstring warns that cross-key pairs are what an earlier harvester got wrong.")
    print(f"     ⚠ THIS MAKES INVARIANT 2 REFUSE MORE PAIRS. It cannot show every refused pair is")
    print(f"     harmless — only that the one it was asked about is, and that a planted true")
    print(f"     positive still fires. Pairs flagged before {before['n_flagged']}, "
          f"after {after['n_flagged']}.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "r235_is_coherent": {"K4prime_point": -0.022443167701863338,
                                    "K4prime_ci": [-0.040650448585231265, -0.005036231884058221],
                                    "point_inside": True,
                                    "topw_beats_core_cells": 76, "core_beats_topw_cells": 0,
                                    "K2_asks": "whether a MAJORITY of cells are "
                                               "negative-significant",
                                    "K5_cells_total": 286, "is_76_a_majority": False},
               "gate_defect": "invariant 2 pairs on sole candidacy alone; invariant 1's "
                              "`ci_spoken_for` refusal is computed four lines above and never "
                              "applied to it",
               "before_contradict": before["contradict"], "after_contradict": real_after,
               "n_flagged_before": before["n_flagged"], "n_flagged_after": after["n_flagged"],
               "outside_unchanged": bool(c3), "n_outside": len(before["outside"]),
               "cannot_show": "that every newly refused pair is harmless — only that the one asked "
                              "about is, and that a planted true positive still fires",
               "unit_note": "counts are PAIRS and NODES",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "pairing_discipline.json", "w"), indent=2)
    print(f"\n  artifact: results/pairing_discipline.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
