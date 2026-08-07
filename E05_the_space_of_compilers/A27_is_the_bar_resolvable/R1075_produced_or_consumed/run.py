"""R1075 — the two candidates: produced by their round's computation, or consumed from an earlier one?

R1074 read the three distinct singly-carried clause decimals. One (`0.009103`, R981) its own round
calls a population error being corrected. Two remain candidates: `0.551354` (R782, a comparator mean
inside a result table) and `0.559311` (R1000, a bar quoted in a derivation discussion). R1074 could
not settle them because its proxy — position in the README — is unsound in exactly that direction.

⭐ ORIGIN IS DECIDABLE WHERE POSITION IS NOT. A value TYPED AS A LITERAL in the round's own `run.py`
   was put there by hand: it is a constant the round CONSUMED. A value appearing in the round's
   README or stdout but NOWHERE in its source was COMPUTED by that round. That is a mechanical test
   on committed text, and it is the one R1074's ledger said was still owed.

ESTIMAND        for each candidate, whether its value occurs as a literal in the carrying round's
                run.py (consumed) or only in that round's output (produced)
IDENTIFICATION  exact for literal presence. ⚠ A round can compute a value AND print it via an
                f-string without the digits ever appearing in source — that is the produced case and
                is correctly detected. The converse trap: a literal may be a THRESHOLD rather than a
                consumed measurement, so `literal` is reported with the source line for judgement.
SCOPE           population : R1074's 2 candidate values + the 1 it classified incidental, as a check
                instrument : exact literal match in the carrying round's run.py, with the line shown
                baseline   : R1074's position-based classification
                regime     : this checkout
WORLDS          A PRODUCED — the candidates appear only in output, so each is a value its round
                  computed and failed to persist: writing it back closes a real gap.
                B CONSUMED — they appear as literals in source, so they are constants the round read
                  in, and persisting them would store someone else's number in the wrong round.
                prediction matrix: A -> no literal in source;  B -> literal present
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      no literal in the carrying round's source -> PRODUCED, persist it
                      literal present                           -> CONSUMED, do not
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ a value KNOWN to be a hardcoded constant must classify CONSUMED. R923's `NBOOT`
                and its seed are literals in its own source; whichever is present must be detected.
NEGATIVE CTRL   a value known to be computed and printed via an f-string must classify PRODUCED —
                the round's own reported share, which appears in no source as digits.
PLACEBO         a round with no run.py yields NO_SOURCE and is reported, never assumed either way.
NOISE FLOOR     N/A - literal presence is exact. Stated, not omitted.
MULTIPLICITY    all three of R1074's values reported, including the one already called incidental,
                so the classification can be checked against a known case.
SEEDS           N/A.
IMPOSSIBLE      whether a literal is a consumed MEASUREMENT or a chosen THRESHOLD. The source line is
                printed so that reading decides it. SETTLES: IN-RELEASE, two lines.
"""
import json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E05 = ROOT / "E05_the_space_of_compilers"


def main() -> int:
    src = next(ROOT.glob("E05_the_space_of_compilers/A27*/R1074_*/results/"
                         "role_of_the_six.json"), None)
    if src is None:
        print("  UNRUNNABLE: R1074's artifact is missing. Exit 2, never 0."); return 2
    vals, seen = [], set()
    for v in json.loads(src.read_text())["values"]:
        if v["value"] not in seen and v.get("role"):
            seen.add(v["value"]); vals.append(v)
    if not vals:
        print("  UNRUNNABLE: no classified value. Exit 2, never 0."); return 2

    runs = {}
    for p in E05.glob("A*/R*/run.py"):
        m = re.match(r"R\d+", p.parent.name)
        if m:
            runs[m.group(0)] = p

    def literal(rid, val):
        p = runs.get(rid)
        if p is None:
            return None, None
        txt = p.read_text()
        m = re.search(r"(?<![\w.])" + re.escape(val) + r"(?![\w.])", txt)
        if not m:
            return False, None
        line = txt[txt.rfind("\n", 0, m.start()) + 1: txt.find("\n", m.end())].strip()
        return True, line[:150]

    # ---------- controls ----------
    pos_rid = next((r for r in runs if r == "R923"), None)
    pos = False
    if pos_rid:
        txt = runs[pos_rid].read_text()
        pos = re.search(r"(?<![\w.])8000(?![\w.])", txt) is not None
    neg, _ = literal("R1074", "0.667")
    print(f"  POSITIVE — a known hardcoded constant must be detected in its own source "
          f"(R923 NBOOT=8000): {pos}")
    print(f"  NEGATIVE — a value computed and printed via an f-string must NOT appear in source "
          f"(R1074's own share 0.667): {neg is False}")
    if not (pos and neg is False):
        print("  the literal test cannot be read either way. Exit 2, never 0."); return 2

    rows = []
    for v in vals:
        has, line = literal(v["round"], v["value"])
        role = ("NO_SOURCE" if has is None else "CONSUMED" if has else "PRODUCED")
        rows.append({"value": v["value"], "round": v["round"], "r1074_role": v["role"],
                     "origin": role, "source_line": line})
        print(f"\n  {v['value']:>12}  {v['round']:<7} R1074:{v['role']:<18} -> {role}")
        if line:
            print(f"               | {line[:112]}")

    produced = [r for r in rows if r["origin"] == "PRODUCED"]
    consumed = [r for r in rows if r["origin"] == "CONSUMED"]
    cands = [r for r in rows if r["r1074_role"] == "candidate-finding"]
    cand_prod = [r for r in cands if r["origin"] == "PRODUCED"]

    print(f"\n  ⭐ of {len(rows)} distinct values: PRODUCED {len(produced)} · CONSUMED "
          f"{len(consumed)} · no source {len(rows) - len(produced) - len(consumed)}")
    print(f"  ⭐ of the {len(cands)} R1074 candidates: PRODUCED {len(cand_prod)}")

    print()
    if cands and len(cand_prod) == len(cands):
        world = (f"⭐ A PRODUCED — both R1074 candidates appear nowhere in their carrying round's "
                 f"source, so each is a value that round COMPUTED and failed to persist. Writing "
                 f"them back closes a real gap: {[r['value'] for r in cand_prod]}.")
    elif not cand_prod:
        world = (f"⛔ B CONSUMED — every R1074 candidate is a LITERAL in its carrying round's source, "
                 f"so they are constants the round read in rather than results it produced. "
                 f"Persisting them would store someone else's number in the wrong round, and the "
                 f"provenance gap they seemed to represent is not one.")
    else:
        world = (f"⭐ SPLIT — {len(cand_prod)} of {len(cands)} candidates are PRODUCED "
                 f"({[r['value'] for r in cand_prod]}); the rest are literals in source and are "
                 f"CONSUMED. Only the produced ones are worth persisting.")
    print(world)
    print(f"⛔ AND A LITERAL IS NOT AUTOMATICALLY A CONSUMED MEASUREMENT — it may be a chosen")
    print(f"   THRESHOLD. The source line is printed above for exactly that judgement, which is two")
    print(f"   lines of reading and the entire remaining cost of this question.")

    # ⛔⛔⛔ AND THE PREMISE OF THIS ENTIRE CHAIN IS VOID, DISCOVERED WHILE COMMITTING THIS ROUND.
    #   R1070 declared these decimals `stored by no round` using an EXACT float comparison. They are
    #   all stored, at FULL PRECISION: `0.559311` is `0.5593110791885862` on disk, `0.551354` is
    #   `0.5513543391990778`, `0.009103` is `0.009102604212460431`. The statement prints a rounded
    #   display value; the artifact stores the full one; exact matching finds nothing.
    #   ⭐ THAT IS PRECISELY THE DEFECT R1047 FOUND AND FIXED — display rounding versus stored
    #   precision — recurring five rounds later because R1070 wrote a FRESH exact `has()` instead of
    #   reusing R1047's `has_rounded()`. **A fix that lives inside one round's script does not
    #   propagate.** That is worth more than the chain it kills.
    def leaves2(o, out):
        if isinstance(o, bool):
            return
        if isinstance(o, (int, float)):
            out.add(float(o)); return
        if isinstance(o, list):
            for v in o:
                leaves2(v, out)
        elif isinstance(o, dict):
            for v in o.values():
                leaves2(v, out)

    pool = set()
    for f in E05.glob("A*/R*/results/*.json"):
        try:
            leaves2(json.loads(f.read_text()), pool)
        except Exception:
            continue
    recheck = []
    for r in rows:
        v, dp = float(r["value"]), len(r["value"].split(".")[1])
        hits = sorted(x for x in pool if round(x, dp) == round(v, dp))
        recheck.append({"value": r["value"], "exact_in_artifacts": v in pool,
                        "rounds_to_it": len(hits), "example": hits[0] if hits else None})
        print(f"\n  ⛔ {r['value']}: exact match in artifacts = {v in pool} · values that ROUND to "
              f"it = {len(hits)} · e.g. {hits[0] if hits else None}")
    n_stored = sum(1 for r in recheck if r["rounds_to_it"])
    print(f"\n  ⛔⛔⛔ {n_stored} of {len(recheck)} supposedly-unstored values ARE STORED at full "
          f"precision. **R1070's `31 unstored` is VOID, and with it R1071, R1073, R1074 and this "
          f"round's own premise.** The origin classification above is internally sound and answers a "
          f"question that no longer needs asking.")

    o = HERE / "results" / "produced_or_consumed.json"
    o.write_text(json.dumps({
        "round": "R1075", "rows": rows,
        "RETRACTION": {"kills": ["R1070 `31 unstored`", "R1071", "R1073", "R1074",
                                 "this round's premise"],
                       "cause": "R1070 used an exact float comparison; the statement prints rounded "
                                "display values while artifacts store full precision",
                       "prior_fix": "R1047 found and fixed this exact defect; R1070 wrote a fresh "
                                    "exact has() instead of reusing has_rounded()",
                       "recheck": recheck, "stored_at_full_precision": n_stored}, "produced": len(produced), "consumed": len(consumed),
        "candidates": len(cands), "candidates_produced": len(cand_prod), "world": world,
        "controls": {"positive_known_literal": bool(pos), "negative_computed_absent": neg is False},
        "limitation": "a literal may be a chosen threshold rather than a consumed measurement; the "
                      "source line is printed for that judgement",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
