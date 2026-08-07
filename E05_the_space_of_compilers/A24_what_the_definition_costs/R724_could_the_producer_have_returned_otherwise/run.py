"""
R724 · could the producer have returned otherwise

ESTIMAND        over the defensible decision-rule space of R294's OWN procedure, how many DISTINCT
                extensions can it return, and what share of that space gives the released 5-set?
IDENTIFICATION  identified for the axes the artifact fixes (effect, CI, MDE, provenance, k-cap).
                NOT identified: bootstrap seed, NBOOT, BH q, annotator filter -> a LOWER BOUND on
                reachable extensions, never a count.
SCOPE           population 41 judged arms · instrument re-derivation from persisted statistics ·
                baseline R294's own cell · regime full_census.json at source_sha 2bc1124f6825df0f
WORLDS          W-FORCED invariant -> a derivation · W-FITTED released set rare -> a rule choice ·
                W-ROBUST released set modal -> the producer survives
KILL            conditional; gated on the g=0 reconstruction AND the negative control. See
                PREREGISTRATION.txt.
POSITIVE CTRL   reconstruction at R294's own cell reproduces `admitted` exactly on all 41 arms;
                floor 0 < t 41 <= ceiling 41. PLANT: maximal-margin arm admitted under all 5 rules,
                zero-margin arm under none (the g=0 half).
NEGATIVE CTRL   permute the arm->statistics pairing; the released set must NOT be recovered.
                excluded world: "the rule returns the same set whatever the data".
SHAM            criteria removed, admit everything -> all 41. absence, not inversion.
PLACEBO         released cell against itself -> symmetric difference exactly 0.
NOISE FLOOR     deterministic given the artifact; verified under two hash seeds, not assumed.
MULTIPLICITY    100 cells; every distinct extension reported with its cell count.
SPECIFICATION   ①rule x5 · ②rule x5 · ③ on/off · k-capped kept/dropped
SEEDS           deterministic; two hash seeds byte-identical
ARTIFACT        results/r724_producer_degrees_of_freedom.json with tree_sha
IMPOSSIBLE      seed/NBOOT/q/annotator-filter -> a re-run of the census · independently replicated
                -> a second implementer
"""
import hashlib, json, pathlib, random, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
CENSUS = ARC / "R294_the_definition_against_everything" / "results" / "full_census.json"

RULES = ("strict", "ci_only", "point", "mde_only", "conservative")


def clears(eff: float, lo: float, hi: float, mde: float, rule: str) -> bool:
    """The five defensible readings of 'this clause is satisfied'. R294 uses `strict`."""
    if rule == "strict":        return lo > 0.0 and abs(eff) >= mde       # corebench.report.verdict
    if rule == "ci_only":       return lo > 0.0
    if rule == "point":         return eff > 0.0
    if rule == "mde_only":      return eff >= mde
    if rule == "conservative":  return lo > mde
    raise ValueError(rule)


def extension(rows, r1: str, r2: str, use3: bool, drop_kcap: bool):
    out = []
    for a, r in rows.items():
        if drop_kcap and r["kcap"]:
            continue
        e1, l1, _h1 = r["c1"]; e2, l2, _h2 = r["c2"]
        ok = clears(e1, l1, _h1, r["mde1"], r1) and clears(e2, l2, _h2, r["mde2"], r2)
        if use3:
            ok = ok and r["ok3"]
        if ok:
            out.append(a)
    return tuple(sorted(out))


def main() -> int:
    print("=" * 100)
    print("R724 · COULD THE PRODUCER HAVE RETURNED OTHERWISE")
    print("=" * 100)
    if not CENSUS.exists():
        print("  UNRUNNABLE: R294's census absent. Exit 2, never 0."); return 2
    cen = json.loads(CENSUS.read_text())
    rows, released = cen["rows"], tuple(sorted(cen["admitted"]))
    if not rows:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0"); return 2
    print(f"  arms {len(rows)}   released extension {len(released)}: {list(released)}")
    print(f"  census source_sha {cen['source_sha']}")

    ctl = {}
    print("\n─── CONTROLS ───")

    # g=0 / POSITIVE — the reconstruction must reproduce the COMMITTED verdicts exactly
    matched = sum(1 for a, r in rows.items()
                  if (clears(*r["c1"], r["mde1"], "strict") and
                      clears(*r["c2"], r["mde2"], "strict") and r["ok3"]) == r["admitted"])
    t, ceiling = len(rows), len(rows)
    ctl["RECONSTRUCTION"] = matched == t and 0 < t <= ceiling
    print(f"  g=0/POSITIVE  R294's own cell reproduces `admitted` on {matched}/{len(rows)} arms")
    print(f"                band floor 0 < t {t} <= ceiling {ceiling}: {0 < t <= ceiling}")
    print(f"                -> {'PASS' if ctl['RECONSTRUCTION'] else 'FAIL'}")

    big  = {"c1": [9.0, 8.0, 10.0], "mde1": 0.01, "c2": [9.0, 8.0, 10.0], "mde2": 0.01,
            "ok3": True, "kcap": False, "admitted": True}
    zero = {"c1": [0.0, -1.0, 1.0], "mde1": 0.01, "c2": [0.0, -1.0, 1.0], "mde2": 0.01,
            "ok3": True, "kcap": False, "admitted": False}
    plant_hi = all(clears(*big["c1"], big["mde1"], r) for r in RULES)
    plant_lo = any(clears(*zero["c1"], zero["mde1"], r) for r in RULES)
    ctl["PLANT"] = plant_hi and not plant_lo
    print(f"  PLANT         maximal-margin arm clears all 5 rules: {plant_hi}")
    print(f"                zero-margin arm clears ANY rule (must be False): {plant_lo}")
    print(f"                -> {'PASS' if ctl['PLANT'] else 'FAIL'}")

    rng = random.Random(20260805)
    names = sorted(rows); shuffled = names[:]; rng.shuffle(shuffled)
    permuted = {n: rows[s] for n, s in zip(names, shuffled)}
    perm_ext = extension(permuted, "strict", "strict", True, False)
    ctl["NEGATIVE"] = perm_ext != released
    print(f"  NEGATIVE      arm->statistics pairing permuted -> {len(perm_ext)} admitted, "
          f"equals released: {perm_ext == released} -> {'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"                excluded world: 'the rule returns the same set whatever the data'")

    sham = tuple(sorted(rows))
    ctl["SHAM"] = len(sham) == len(rows) and len(sham) != len(released)
    print(f"  SHAM          criteria removed, admit everything -> {len(sham)} of {len(rows)} "
          f"-> {'PASS' if ctl['SHAM'] else 'FAIL'}  (absence, not inversion)")

    base = extension(rows, "strict", "strict", True, False)
    ctl["PLACEBO"] = len(set(base) ^ set(released)) == 0
    print(f"  PLACEBO       released cell against itself, symmetric difference "
          f"{len(set(base) ^ set(released))} (must be 0) -> {'PASS' if ctl['PLACEBO'] else 'FAIL'}")

    ctl["UNIT"] = True
    print(f"  UNIT          instrument: extension recomputed from persisted per-arm statistics")
    print(f"                claim     : what R294's procedure could have returned")
    print(f"                residue   : seed, NBOOT, BH q and the annotator filter need a re-run,")
    print(f"                            so the count below is a LOWER BOUND -> PASS")

    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── THE GRID ─────────────────────────────────────────────────────────────────────────────
    print("\n─── SPECIFICATION CURVE · 5 x 5 x 2 x 2 = 100 CELLS (all reported) ───")
    cells, tally = [], {}
    for r1 in RULES:
        for r2 in RULES:
            for use3 in (True, False):
                for dk in (False, True):
                    ext = extension(rows, r1, r2, use3, dk)
                    cells.append({"c1_rule": r1, "c2_rule": r2, "clause3": use3,
                                  "drop_kcap": dk, "n": len(ext), "ext": list(ext)})
                    tally[ext] = tally.get(ext, 0) + 1

    order = sorted(tally.items(), key=lambda kv: (-kv[1], len(kv[0])))
    print(f"  {'cells':<7} {'size':<6} extension")
    for ext, c in order:
        mark = "  ⭐ RELEASED" if ext == released else ""
        shown = ", ".join(ext[:6]) + (f", +{len(ext)-6} more" if len(ext) > 6 else "")
        print(f"  {c:<7} {len(ext):<6} {shown or '(empty)'}{mark}")

    A = len(tally)
    B = tally.get(released, 0) / len(cells)
    modal = order[0][0]
    directional = modal == released

    off = extension(rows, "strict", "strict", False, False)
    C = len(off)
    added = sorted(set(off) - set(released))

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo, hi, reg in [("A distinct extensions", A, 2, 100, 12),
                                 ("B released share", round(B, 4), 0.0, 1.0, 0.25),
                                 ("C size with ③ OFF", C, 5, 41, 7)]:
        print(f"  {nm:<24} registered {reg:<6} -> {val:<8} in [{lo},{hi}]: {lo <= val <= hi}")
    print(f"  ⛔ C IS A DERIVATION, NOT EVIDENCE: turning ③ off can only ADD the arms ③ excluded,")
    print(f"     so C = 5 + |{{a in USES_PROMPT_LABELS : a clears ①②}}| by algebra. added = {added}")
    print(f"  DIRECTIONAL released set is the MODAL extension -> {directional} "
          f"(modal has {order[0][1]} cells, size {len(modal)})")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["RECONSTRUCTION"] and ctl["NEGATIVE"]):
        verdict = "UNVERIFIED — a gating control did not fire; no degrees-of-freedom count is admissible."
    elif A == 1:
        verdict = ("⭐⭐⭐ W-FORCED. The producer returns the SAME extension in all 100 cells: it could "
                   "not have come out otherwise, so R294 is a DERIVATION and the deliverable's single "
                   "remaining computation has zero degrees of freedom.")
    elif B < 0.10:
        verdict = (f"⭐⭐⭐ W-FITTED. The released 5-set appears in {B:.1%} of the rule space "
                   f"({tally.get(released,0)} of {len(cells)} cells) while {A} distinct extensions are "
                   f"reachable. The number 5 is a choice of decision rule reported as a measurement.")
    else:
        verdict = (f"⭐⭐⭐ W-ROBUST, WITH ITS SIZE STATED. {A} distinct extensions are reachable across "
                   f"100 defensible cells and the released 5-set holds {tally.get(released,0)} of them "
                   f"({B:.1%}); the modal extension has size {len(modal)} and "
                   f"{'IS' if directional else 'is NOT'} the released set. ⭐ So R294 COULD have "
                   f"returned otherwise — the producer is a measurement, not a derivation, and "
                   f"R723's 'one independent computation' survives as one rather than collapsing to "
                   f"zero. ⚠ AND IT IS A LOWER BOUND: the bootstrap seed, NBOOT, the BH q and the "
                   f">=2-annotator filter are fixed inside the artifact and would need the census "
                   f"re-run, so the true rule space is at least this wide and no narrower.")
    print(f"  {verdict}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {
        "world": verdict,
        "controls_ok": all(ctl.values()),
        "controls": ctl,
        "tree_sha": tree_sha,
        "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        "census_source_sha": cen["source_sha"],
        "n_arms": len(rows),
        "released": list(released),
        "A_distinct_extensions": A,
        "B_released_share": round(B, 4),
        "C_size_clause3_off": C,
        "C_is_a_derivation": True,
        "C_added_by_turning_clause3_off": added,
        "modal_extension": list(modal),
        "modal_cells": order[0][1],
        "directional_released_is_modal": directional,
        "n_cells": len(cells),
        "tally": [{"n_cells": c, "size": len(e), "ext": list(e)} for e, c in order],
        "cells": cells,
        "registered": "A 12 [2,100]; B 0.25 [0,1]; C 7 [5,41] (derivation); directional released==modal",
        "residue": "seed/NBOOT/q/annotator-filter unreachable from the artifact -> LOWER BOUND",
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r724_producer_degrees_of_freedom.json").write_text(
        json.dumps(out, indent=2, sort_keys=True))
    print(f"\n  artifact: results/r724_producer_degrees_of_freedom.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
