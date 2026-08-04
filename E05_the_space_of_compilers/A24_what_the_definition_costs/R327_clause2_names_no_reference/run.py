"""R327 — clause 2 names a CLASS, not a reference, and R326 shows the under-specification is load-bearing.

    (1) better than the same number DRAWN AT RANDOM from that conversation's own rubric
    (2) better than the same number that NEVER READ THE CONVERSATION AT ALL

Clause 1 names a PROCEDURE -- draw at random from a stated pool -- so the comparison it licenses is
unambiguous. Clause 2 names a CLASS and no member and no procedure. English reads it most naturally
as a UNIVERSAL: better than any such set. The campaign has instead tested it against five different
members, and R326 measured that they disagree about the admitted set.

⛔ THIS IS THE SAME DEFECT R293 ALREADY CAUGHT ONCE IN THIS DEFINITION. `held out from the core's own
construction` was an adjective nothing computed until a round asked `held out from WHAT`, and
applied to `oracle_k4` the definition ADMITTED an arm its own author called leaky. `never read the
conversation at all` is the same shape: a phrase that sounds like a criterion and does not name what
it is measured against.

ESTIMAND      the admitted set under each defensible READING of clause 2 -- a specification curve
              over the READING, not over the data. G4 applied to the definition itself.
IDENTIFICATION exact. Every reading maps to references R326 already priced; this round selects
              among committed cells and adds no estimate.
SCOPE         the two arms clause 2 currently admits · 968 prompts · A2·annotator · references as
              published.
WORLDS        W-SAME     every reading admits the same set -> the wording is loose and harmless.
              W-DIVERGES readings disagree -> the clause is UNDER-SPECIFIED in a load-bearing way
                         and the page's headline depends on an unstated choice.
KILL          all readings give the same admitted set   -> W-SAME
              any two differ                            -> W-DIVERGES
POSITIVE CTRL the strictest reading must admit FEWER arms than the loosest, or the readings are not
              ordered by strictness and calling one strict is a label rather than a fact.
NEGATIVE CTRL a reading nobody would defend -- the DISQUALIFIED in-sample argmax -- is carried to
              show what an illegitimate choice does. It is not offered as an option.
PLACEBO       n/a and stated: there is no contrast here that must return zero. This round selects
              among measured cells; inventing a placebo would be decoration.
MULTIPLICITY  3 defensible readings x 2 arms, plus the disqualified one; all printed.
ARTIFACT      results/readings.json with source hash.
IMPOSSIBLE    deciding WHICH reading the definition should take. That is a choice about what the
              word `better` quantifies over, and no measurement settles it -- the round's job is to
              price each option, not to pick.
"""
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
CURVE = (SELF.parent.parent / "R326_the_clause2_baseline_curve" / "results"
         / "baseline_curve.json")

READINGS = [
    ("A · UNIVERSAL — better than EVERY prompt-blind set of that size",
     "best held-out of 1,820", "strictest; the plain-English reading of `never read the "
     "conversation at all`"),
    ("B · NAMED — better than a stated held-out reference",
     "generic at matched k=4", "names one member, as clause 1 names its pool"),
    ("C · PROCEDURAL — better than one DRAWN AT RANDOM from the prompt-blind pool",
     "budget 0 · random draw", "symmetric with clause 1's own wording"),
]
DISQUALIFIED = "budget 1820 · IN-SAMPLE (ceiling, unattainable)"


def main():
    if not CURVE.exists():
        print(f"  UNRUNNABLE: {CURVE.name} absent."); return 2
    d = json.loads(CURVE.read_text())
    pts = {p["ref"]: p for p in d["points"]}
    # R326 merged duplicate references; rebuild a lookup tolerant of both labels
    by_a2 = {}
    for p in d["points"]:
        by_a2.setdefault(round(p["ref_a2"], 6), {}).update(p["cells"])

    def cells_for(label):
        p = pts.get(label)
        if p is None:
            return None, None
        return by_a2.get(round(p["ref_a2"], 6), p["cells"]), p["ref_a2"]

    print("  Clause ① names a PROCEDURE. Clause ② names a CLASS, no member, no procedure.")
    print("  Three defensible readings, each mapping to a reference R326 already priced.\n")
    print(f"    {'reading':<58}{'coval_core':>14}{'topw_k4':>14}   admitted")
    rows = []
    for name, ref, why in READINGS:
        cells, a2 = cells_for(ref)
        if cells is None:
            print(f"    {name:<58}  reference {ref!r} absent"); return 2
        # ⚠ UNMEASURED IS NOT NOT-ADMITTED. R287 ran only coval_core at budget 0, so reading C
        # has NO CELL for topw_k4 -- and the first version of this round reported C's admitted
        # set as ['coval_core'], which reads as an exclusion and is an absence of data. Sixth
        # population error this session and the same fix: make the three-valued split explicit.
        ARMS = ("coval_core", "topw_k4")
        adm = sorted(a for a in ARMS
                     if a in cells and cells[a]["resolved"] and cells[a]["gap"] > 0)
        notadm = sorted(a for a in ARMS
                        if a in cells and not (cells[a]["resolved"] and cells[a]["gap"] > 0))
        unmeas = sorted(a for a in ARMS if a not in cells)
        def fmt(a):
            c = cells.get(a)
            return f"{c['ratio']:>13.2f}x" if c else f"{'unmeasured':>14}"
        rows.append(dict(reading=name, reference=ref, ref_a2=a2, why=why,
                         cells=cells, admitted=adm, not_admitted=notadm, unmeasured=unmeas))
        tag = f"{adm}" + (f" · NOT {notadm}" if notadm else "") + \
              (f" · UNMEASURED {unmeas}" if unmeas else "")
        print(f"    {name:<58}{fmt('coval_core')}{fmt('topw_k4')}   {tag}")

    cells, a2 = cells_for(DISQUALIFIED)
    if cells:
        adm = sorted(a for a, c in cells.items() if c["resolved"] and c["gap"] > 0)
        print(f"\n    {'✗ DISQUALIFIED · in-sample argmax (negative control, not an option)':<58}"
              f"{cells.get('coval_core', {}).get('ratio', float('nan')):>13.2f}x"
              f"{'--':>14}   {adm}")

    # Divergence must be read off MEASURED cells only; a reading that did not run an arm cannot
    # disagree with one that did.
    comparable = [r for r in rows if not r["unmeasured"]]
    sets = [tuple(r["admitted"]) for r in comparable]
    diverges = len(set(sets)) > 1
    print(f"\n  {len(comparable)} of {len(rows)} readings measured BOTH arms; divergence is read")
    print(f"  off those only -- a reading that did not run an arm cannot disagree with one that did.")
    strictest, loosest = rows[0], rows[-1]
    pos_ok = len(strictest["admitted"]) <= len(loosest["admitted"])
    print(f"\n  POSITIVE  the strictest reading admits no more than the loosest: {pos_ok}  "
          f"({len(strictest['admitted'])} vs {len(loosest['admitted'])})")
    print(f"  NEGATIVE  the disqualified reading is carried, not offered: {cells is not None}")

    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  negative={cells is not None}  -> "
          f"{'evaluate' if pos_ok else 'UNVERIFIED'}")
    if not pos_ok:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. The readings are not ordered by strictness, so calling one strict")
        print("     is a label rather than a fact and nothing below is licensed.")
    elif not diverges:
        world = "W-SAME"
        print("  -> W-SAME. Every reading admits the same set; the wording is loose and harmless.")
    else:
        world = "W-DIVERGES"
        print(f"  -> W-DIVERGES. Among readings that measured BOTH arms: "
              f"{ {r['reading'][:1]: r['admitted'] for r in comparable} }")
        for r in rows:
            if r["unmeasured"]:
                print(f"     ({r['reading'][:1]} did not run {r['unmeasured']} — reported as "
                      f"UNMEASURED, never as excluded.)")
        print("     Clause ② is UNDER-SPECIFIED in a load-bearing way. `Two arms admitted of")
        print("     nine` is true under reading B, FALSE under reading A, and UNDETERMINED under C")
        print("     because C never ran the second arm. The definition does not say which it means.")
        print("     (An earlier draft of this line said `true under B and C` — C is unmeasured,")
        print("      and a verdict string must not fill in a cell the round did not compute.)")
        print("     ⚠ SAME SHAPE AS R293: `held out from the core's own construction` was an")
        print("       adjective nothing computed until a round asked `held out from WHAT`. Here")
        print("       `never read the conversation at all` names a CLASS and never says which")
        print("       member the comparison runs against.")
        print("     ⚠ AND THE TENSION IS REAL, NOT A DRAFTING SLIP: reading C is the one SYMMETRIC")
        print("       with clause ①'s own `drawn at random`, and R287 already established that a")
        print("       random draw is too weak a baseline to test anything against. So the")
        print("       symmetric reading is the weakest test and the strongest test breaks an")
        print("       admission. That is a choice about what `better` quantifies over, and no")
        print("       measurement settles it — which is why this round prices the options and")
        print("       does not pick.")
    print("  " + "=" * 78)

    o = SELF.parent / "results" / "readings.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        readings=rows, diverges=bool(diverges), positive_ok=bool(pos_ok),
        disqualified_carried=bool(cells is not None),
        admitted_by_reading={r["reading"][:1]: r["admitted"] for r in rows},
        unmeasured_by_reading={r["reading"][:1]: r["unmeasured"] for r in rows},
        comparable_readings=[r["reading"][:1] for r in comparable]), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
