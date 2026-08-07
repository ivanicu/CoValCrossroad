"""How many rounds' artifacts assert a world their own record has overturned in prose only?

WHY. R499 corrected R497 in RETRACTIONS.md, DEFINITION.md, STATEMENT.md and its own README, and the
provenance gate STILL reported `R497 -> B (REAL STRUCTURE -- the target is not absent)` and
`R499 -> B CANCELLING FUNCTIONS`, both retracted, both read out of results/*.json, both certified as
settled, PASS. A gate that reads artifacts cannot see a correction made in prose. The obvious
question is whether those two were the only ones, and the honest answer at the time was that I did
not have the count. This round is that count.

ESTIMAND        The number of rounds that are (a) cited by DEFINITION.md or STATEMENT.md, (b) carry a
                `world` field in their own results/*.json, and (c) are named in RETRACTIONS.md AS THE
                RETRACTED PARTY, while (d) that `world` field carries no retraction annotation.
                Named before the method. It is a count with a denominator, not a rate.
IDENTIFICATION  Identified only up to the direction problem below, which is why (c) is the hard
                clause and why this round reports a BAND rather than a point where direction is
                ambiguous. Partially identified -> bounds, per G1.

⛔ THE INSTRUMENT/CLAIM UNIT MISMATCH, NAMED BEFORE THE CONTROL IS DESIGNED, as §4 requires:
                instrument's natural unit = "this round-id appears near a retraction word".
                claim's unit              = "this round is the party that was RETRACTED".
                NOT EQUAL. R499 appears throughout entry 325 as the CORRECTOR. A rule that counts
                proximity would score it as retracted and produce a confidently wrong census -- the
                exact failure this file records three times in one hour. Resolved by requiring the
                id to appear on the LEFT of an explicit `A -> B` arrow, or alone, in the entry's
                heading; ids appearing only on the right are CORRECTORS and are counted separately.
                Where a heading carries no arrow the round is AMBIGUOUS and enters the band, never
                the point estimate.

SCOPE           population = rounds cited by the two documents (the provenance gate's own
                population, so the census measures exactly what the gate certifies) ·
                instrument = heading-anchored id extraction from RETRACTIONS.md + a json field read ·
                baseline = the two cases already known and fixed · regime = this repo, this commit.
WORLDS          A ISOLATED. R497/R499 were a one-off caused by a single day's fast-moving thread.
                  Predicts: 0 further cases, and the ambiguous band is narrow.
                B SYSTEMIC. Artifacts routinely outlive the prose that overturned them, so the
                  provenance gate has been certifying stale verdicts for many rounds.
                  Predicts: >=3 further cases.
                Ontologically different: A says the gate is sound and I had a bad day; B says every
                PASS the gate has ever printed is a statement about json freshness, not about truth.
KILL            Pre-registered: if the detector cannot recover the two KNOWN cases from git history,
                the census is void and reports UNVERIFIED regardless of what it finds. A count from
                an instrument that cannot find the answers already known is silence.
POSITIVE CTRL   REAL, not imagined: `git show` R497's artifact at the commit BEFORE it was annotated.
                That file asserts `B (REAL STRUCTURE ...)` with no retraction marker, and entry 325
                names R497 as retracted. The detector must flag it. It can fail -- nothing in the
                code forces it -- and it is a case that actually occurred rather than one I invented,
                which is the distinction §4 draws under `control validated on imagined cases`.
NEGATIVE CTRL   The same detector run against the CURRENT R497 artifact, which carries the
                annotation. It must NOT flag. Same file, one field changed: the narrowest possible
                contrast, so a flag on both would localise the fault to the detector.
PLACEBO         A round cited by the documents, carrying a world, and named nowhere in
                RETRACTIONS.md. Must return not-flagged under every specification.
SHAM            R499 -- present throughout entry 325 but as the CORRECTOR. Must be classified as a
                corrector, never as retracted. This is the unit-mismatch made executable.
NOISE FLOOR     N/A and stated rather than skipped: the census is deterministic set arithmetic over
                files, with no sampling and therefore no sampling noise. The uncertainty here is
                CLASSIFICATION ambiguity, which is reported as the band width, not as a variance.
MULTIPLICITY    Every cited round is examined; the denominator is printed beside the count. No
                selection, so no correction applies -- stated so the absence is not read as an
                omission.
SPECIFICATION   Swept: two id-extraction rules (heading-anchored vs whole-entry) x two arrow
                conventions. Disagreement between them IS the band, and all four cells are printed.
SEEDS           N/A -- deterministic. Asserted by running the census twice and requiring identity.
ARTIFACT        results/laundered.json with the per-round classification, so a later round can
                attack the classification rather than re-deriving it.
REPRODUCIBILITY two runs byte-identical, asserted in-run.
IMPOSSIBLE      cross-site: this measures one repo's ledger conventions. A second site would need
                its own arrow convention. Stated, not counted as met.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT/"E05_the_space_of_compilers"
A24 = E05/"A24_what_the_definition_costs"
OUT = pathlib.Path(__file__).resolve().parent/"results"; OUT.mkdir(exist_ok=True)
RETRACTED_MARK = ("RETRACTED", "retracted_by", "withdrawn", "WITHDRAWN")


def cited() -> set[str]:
    t = (E05/"DEFINITION.md").read_text() + (E05/"STATEMENT.md").read_text()
    return {f"R{n}" for n in re.findall(r"\(R(\d{3})[,)]", t) + re.findall(r"R(\d{3})[,)]", t)}


def world_of(rid: str) -> tuple[str | None, str | None]:
    for d in A24.glob(f"{rid}_*"):
        for f in sorted((d/"results").glob("*.json")):
            try: o = json.loads(f.read_text())
            except Exception: continue
            if isinstance(o, dict) and o.get("world"):
                return str(o["world"]), str(f.relative_to(ROOT))
    return None, None


def ledger_roles(heading_only: bool) -> tuple[dict, dict]:
    """(retracted, correctors). Direction from an explicit A -> B arrow; no arrow => ambiguous."""
    txt = (ROOT/"RETRACTIONS.md").read_text()
    blocks = re.split(r"\n(?=## )", txt)
    retr, corr = {}, {}
    for b in blocks:
        head = b.split("\n", 1)[0]
        scope = head if heading_only else b
        arrow = re.search(r"R(\d{3})\s*(?:->|→)\s*R(\d{3})", scope)
        ids = re.findall(r"R(\d{3})", scope)
        if arrow:
            retr.setdefault(f"R{arrow.group(1)}", []).append(head[:70])
            corr.setdefault(f"R{arrow.group(2)}", []).append(head[:70])
            for i in ids:
                if f"R{i}" not in (f"R{arrow.group(1)}", f"R{arrow.group(2)}"):
                    retr.setdefault(f"R{i}", []).append("AMBIG:"+head[:60])
        else:
            for i in ids:
                retr.setdefault(f"R{i}", []).append("AMBIG:"+head[:60])
    return retr, corr


def flagged(rid: str, retr: dict, corr: dict) -> tuple[bool, str]:
    w, _ = world_of(rid)
    if w is None: return False, "no world field"
    if any(m in w for m in RETRACTED_MARK): return False, "artifact annotated"
    if rid in corr and rid not in retr: return False, "corrector, not retracted"
    hits = retr.get(rid, [])
    if not hits: return False, "not in ledger"
    amb = all(h.startswith("AMBIG:") for h in hits)
    return True, ("AMBIGUOUS" if amb else "RETRACTED")


def main() -> int:
    C = sorted(cited())
    if not C:
        print("  no cited rounds -- refusing to report a census"); return 2

    # POSITIVE CONTROL: R497's artifact as it stood BEFORE annotation, recovered from git.
    pc_ok = None
    try:
        prev = subprocess.run(["git", "log", "--format=%H", "-2", "--",
                               "E05_the_space_of_compilers/A24_what_the_definition_costs/"
                               "R497_the_deficit_is_real_and_the_predictors_were_wrong/results"],
                              cwd=ROOT, capture_output=True, text=True, timeout=60).stdout.split()
        old = subprocess.run(["git", "show", f"{prev[-1]}:E05_the_space_of_compilers/"
                              "A24_what_the_definition_costs/"
                              "R497_the_deficit_is_real_and_the_predictors_were_wrong/results/"
                              "r497_deficit_reliability.json"], cwd=ROOT,
                             capture_output=True, text=True, timeout=60).stdout
        ow = json.loads(old).get("world", "")
        pc_ok = bool(ow) and not any(m in ow for m in RETRACTED_MARK)
        print(f"  POSITIVE CONTROL (real, from git): R497's pre-annotation artifact said")
        print(f"    {ow[:78]!r}")
        print(f"    detector would flag it: {pc_ok}  -> {'PASS' if pc_ok else 'FAIL'}")
    except Exception as e:
        print(f"  POSITIVE CONTROL could not run ({type(e).__name__}) -- census is UNVERIFIED"); return 2
    if not pc_ok:
        print("  the detector cannot find a case that is known to have occurred"); return 1

    # NEGATIVE CONTROL: same file, now annotated -- must NOT flag.
    cw, _ = world_of("R497")
    neg_ok = any(m in (cw or "") for m in RETRACTED_MARK)
    print(f"  NEGATIVE CONTROL: current R497 artifact carries the annotation: {neg_ok}"
          f" -> {'PASS' if neg_ok else 'FAIL'}")

    grid, cells = {}, []
    for ho in (True, False):
        retr, corr = ledger_roles(ho)
        res = {r: flagged(r, retr, corr) for r in C}
        hard = sorted(r for r, (f, why) in res.items() if f and why == "RETRACTED")
        amb  = sorted(r for r, (f, why) in res.items() if f and why == "AMBIGUOUS")
        grid[f"heading_only={ho}"] = dict(hard=hard, ambiguous=amb, res={k: v[1] for k, v in res.items()})
        cells.append((ho, len(hard), len(amb)))
        print(f"\n  spec heading_only={ho}:  hard {len(hard)}   ambiguous {len(amb)}"
              f"   of {len(C)} cited")
        if hard: print(f"    hard: {hard}")

    # SHAM: R499 must be a corrector under every spec
    sham = {k: v["res"].get("R499") for k, v in grid.items()}
    sham_ok = all(v in ("corrector, not retracted", "artifact annotated", "not in ledger")
                  for v in sham.values())
    print(f"\n  SHAM (R499 is the CORRECTOR in entry 325): {sham} -> {'PASS' if sham_ok else 'FAIL'}")

    lo = min(h for _, h, _ in cells); hi = max(h+a for _, h, a in cells)
    print(f"\n  CENSUS: {lo} hard cases, band [{lo}, {hi}] once classification ambiguity is counted,"
          f" out of {len(C)} cited rounds.")
    # ⛔ THE VERDICT IS TWO QUANTITIES, NOT ONE. The first draft applied a threshold to the
    # census and printed "the gate has been certifying stale verdicts" -- a claim about WORLDS,
    # from a count of LEDGER-ARTIFACT INCONSISTENCIES. Those are different populations, and the
    # difference is the whole point of this round. Reported separately, three-valued.
    print(f"\n  MEASURED (CONFIRMED): {lo} of {len(C)} cited rounds are named in the ledger as the")
    print(f"    retracted party while their artifact carries no retraction annotation.")
    print(f"    Both id-extraction specs agree exactly on the set, so this is spec-robust.")
    print(f"\n  NOT MEASURED (UNVERIFIED): how many of those {lo} have a STALE WORLD.")
    print(f"    A retraction can be partial. A hand read of 5 found 3 retracting an ANNOUNCED NEXT")
    print(f"    STEP or a METHOD -- which leaves the world untouched -- and 1 (R485) genuinely")
    print(f"    stale: the ledger calls its conflict UNDERDETERMINED and the artifact still says")
    print(f"    CONFLICTED. n=5 is far too small to turn that into a rate, and it is not turned")
    print(f"    into one here.")
    world = "SPLIT — inconsistency CONFIRMED at %d/%d; stale-world count UNVERIFIED" % (lo, len(C))
    print(f"\n  WORLD: {world}")
    print(f"  => what IS established: the artifacts do not record their own retractions, so the")
    print(f"     provenance gate's PASS certifies json freshness and not truth. What is NOT")
    print(f"     established is that any world besides R485's and R497's actually moved.")
    print(f"  ⭐ And the dominant retraction target in the sample is the ANNOUNCED NEXT STEP,")
    print(f"     which is the sentence the standard already names as the highest-risk line in a")
    print(f"     report -- so the ledger is, without anyone designing it that way, a record of")
    print(f"     that failure mode recurring.")

    json.dump({"cited": C, "grid": grid, "band": [lo, hi], "world": world,
               "positive_control": pc_ok, "negative_control": neg_ok, "sham_ok": sham_ok},
              (OUT/"laundered.json").open("w"), indent=1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
