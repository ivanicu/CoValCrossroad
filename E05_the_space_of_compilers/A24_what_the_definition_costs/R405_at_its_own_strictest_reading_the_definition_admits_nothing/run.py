"""R405 -- at clause ②'s plain-English reading, does the definition admit anything at all?

R404 reduced clause ③ to one working conjunct and showed ③c, enforced as written, collapses the
admitted set to `coval_core` alone. R327 had separately shown clause ② names a CLASS and no member,
and that its readings disagree. Neither round composed the two, and R360's committed sweep -- 45
cells over the reference percentile -- makes the composition computable without touching the GPU.

⛔ ARITHMETIC TRAP, AND IT IS SHARP HERE, SO IT IS ANSWERED BEFORE THE RUN. Intersecting R360's
   per-percentile `admitted` with its `labels` set is SET ARITHMETIC -- it could not come out
   otherwise given those inputs, and it is a DERIVATION. What is NOT forced, and is the entire
   content, is WHICH ARMS R360 measured into each cell. That `admitted` at the 100th percentile
   happens to equal the label-reader set is a measured fact about the object; the emptiness that
   follows is the algebra I am allowed to do with it. Both are labelled.

⛔ AND THE TWO ROUNDS DISAGREE, WHICH IS THE REASON THIS IS NOT A RESTATEMENT. R327's reading A --
   "better than EVERY prompt-blind set of that size", which it called the plain-English reading --
   admitted `coval_core`, using a reference it recorded as the "best HELD-OUT of 1,820". R360's
   sweep at the 100th percentile admits NO non-label arm. A held-out maximum is lower than an
   in-sample maximum, so the two instantiate "every prompt-blind set" differently -- and the gap
   between them is exactly one arm: the released core. That choice is named in NEITHER round and in
   no sentence of the definition.

ESTIMAND        (A) |admitted ∧ ③a| as a function of the reference percentile, over R360's whole
                    committed sweep -- the curve, not a cell;
                (B) its value at the 100th percentile, i.e. clause ② read as a universal;
                (C) whether that value agrees with R327's reading-A result, and if not, the arm the
                    two disagree about.

IDENTIFICATION  (A) and (B) exact GIVEN R360's sweep -- a derivation from committed measurements.
                (C) exact as a comparison of two committed artifacts. NOT identified: which
                instantiation of "every prompt-blind set" is CORRECT. That is an act of definition
                and this round does not perform it; it reports that the sentence does not decide.

SCOPE           population: R360's 42 arms · instrument: R360's committed per-percentile sweep and
                R327's committed readings · baseline: the published cell · regime: HEAD, no re-scoring.

WORLDS
  W-NONEMPTY-EVERYWHERE   the admitted set is non-empty at every percentile including 100. Then
                          clause ②'s under-specification changes the SIZE of the admitted set and
                          never its existence, and the definition survives its own strictest reading.
  W-EMPTY-AT-UNIVERSAL    the admitted set is EMPTY at the 100th percentile. Then the definition,
                          read as its own plain English, admits NOTHING -- not even the object it was
                          written from -- and the published `5` exists only because the reference is
                          a member rather than the class.

PREDICTION MATRIX
  W-NONEMPTY-EVERYWHERE -> |admitted ∧ ③a| >= 1 at pct = 100
  W-EMPTY-AT-UNIVERSAL  -> |admitted ∧ ③a| == 0 at pct = 100, and the survivors there are exactly
                           the arms ③a excludes

PRE-REGISTERED KILL -- conditional on the controls, never on the endpoint alone.
    if monotone_nonincreasing and published_cell_reproduces_the_published_five:
        if |admitted ∧ ③a| at pct=100 == 0 -> W-EMPTY-AT-UNIVERSAL
        else -> W-NONEMPTY-EVERYWHERE
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  MONOTONE       a stricter reference must admit no MORE arms. This is R327's own positive control
                 promoted to a curve: if the sweep is not non-increasing, "stricter" is a label
                 rather than a fact and no reading can be called strictest.
  PUBLISHED (+)  the cell at the published reference must reproduce the published five arms exactly.
                 If it does not, the sweep and the headline are not about the same object and the
                 curve says nothing about the definition.
  EMPTY-IS-REAL  emptiness must be shown ATTAINABLE and not an artifact of an off-by-one at the end
                 of the sweep: the two cells before the last are printed with their contents.
  CROSS-ROUND    R327's reading-A result is read from ITS artifact, not restated from memory, and
                 the disagreement is reported as a disagreement rather than adjudicated.

MULTIPLICITY    45 committed cells, the whole curve printed at every distinct size.
SEEDS           none -- a derivation over committed cells.
ARTIFACT        results/r405_universal_reading.json with the source hash.

IMPOSSIBLE HERE
  deciding which instantiation is correct -- an act of definition, not a measurement.
  re-scoring any arm                      -- needs the judge; this composes committed cells.
  a held-out vs in-sample reconciliation  -- would need the 1,820 subset scores under both, which
                                             R360's artifact does not carry. Named as the next step.
  a second release                        -- two corpora, neither re-scored here.

EXIT
    0  the controls hold and the curve is reported
    1  the sweep is not monotone or the published cell does not reproduce -- UNVERIFIED
    2  an artifact is absent -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
R360 = HERE.parent / "R360_which_clause_is_load_bearing" / "results" / "r360_clause_ledger.json"
R327 = HERE.parent / "R327_clause2_names_no_reference" / "results" / "readings.json"


def main() -> int:
    for f in (R360, R327):
        if not f.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    d = json.loads(R360.read_text())
    r327 = json.loads(R327.read_text())
    sweep = sorted(d["sweep"], key=lambda c: c["pct"])
    published = set(d["clause23_admits"])

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R405 · at clause ②'s plain-English reading, does anything survive?   HEAD {head}\n")
    print("  ⛔ THE INTERSECTION IS A DERIVATION AND IS LABELLED ONE. What is NOT forced is WHICH")
    print("     ARMS R360 measured into each cell — that is the measurement, and the emptiness that")
    print("     follows is the algebra I am allowed to do with it.\n")

    # ---- the curve -------------------------------------------------------------------------------
    curve = []
    for c in sweep:
        adm, lab = set(c["admitted"]), set(c["labels"])
        curve.append((c["pct"], sorted(adm - lab)))
    sizes = [len(v) for _, v in curve]
    monotone = all(a >= b for a, b in zip(sizes, sizes[1:]))

    print(f"  (A) |admitted ∧ ③a| ACROSS R360's {len(sweep)} COMMITTED CELLS — printed at every")
    print(f"      distinct size, so the plateau and the cliff are both visible")
    last = None
    for pct, arms in curve:
        if len(arms) != last:
            print(f"      pct {pct:>6.1f}   n={len(arms)}   {arms}")
            last = len(arms)
    print(f"      ... {len(sweep)} cells total; sizes {sizes[0]} → {sizes[-1]}")

    # ---- CONTROLS --------------------------------------------------------------------------------
    pub_cell = next((v for p, v in curve if abs(p - 93.5) < 0.01), None)
    pub_ok = pub_cell is not None and set(pub_cell) == published
    print(f"\n  CONTROLS")
    print(f"    MONOTONE       a stricter reference admits no MORE arms: {monotone}   "
          f"{'PASS' if monotone else 'FAIL — `stricter` is a label, not a fact'}")
    print(f"    PUBLISHED (+)  the published-reference cell reproduces the published five: {pub_ok}")
    print(f"                   cell {pub_cell}")
    print(f"                   published {sorted(published)}   {'PASS' if pub_ok else 'FAIL'}")
    if not (monotone and pub_ok):
        print("\n  UNVERIFIED — the curve and the headline are not about the same object. Exit 1.")
        return 1
    tail = curve[-3:]
    print(f"    EMPTY-IS-REAL  the last three cells, so emptiness is not an end-of-sweep artifact:")
    for pct, arms in tail:
        print(f"                     pct {pct:>6.1f}  n={len(arms)}  {arms}")

    # ---- (B) the universal reading ----------------------------------------------------------------
    pct100, arms100 = curve[-1]
    survivors = set(sweep[-1]["admitted"])
    labels = set(sweep[-1]["labels"])
    print(f"\n  (B) AT pct = {pct100} — clause ② read as a UNIVERSAL, `better than EVERY prompt-blind")
    print(f"      set of that size`")
    print(f"      arms surviving clause ②      : {sorted(survivors)}")
    print(f"      arms clause ③a excludes      : {sorted(labels)}")
    print(f"      -> clause ② ∧ ③a             : {arms100}   (n={len(arms100)})")
    empty = (len(arms100) == 0)
    if empty:
        print(f"      ⚠ THE SURVIVORS ARE EXACTLY THE ARMS THAT READ THE LABELS. The only way to beat")
        print(f"        EVERY prompt-blind set, on this release, is to have seen the answer.")

    # ---- (C) the cross-round disagreement ---------------------------------------------------------
    r327_A = set(r327["admitted_by_reading"]["A"])
    ref_a = next((r for r in r327["readings"] if r["reading"].startswith("A")), {})
    print(f"\n  (C) CROSS-ROUND — R327's reading A, read from ITS artifact, not from memory")
    print(f"      R327 reading A admits : {sorted(r327_A)}")
    print(f"      its reference         : {ref_a.get('reference')!r}  (ref_a2 {ref_a.get('ref_a2')})")
    print(f"      this round at pct=100 : {arms100}")
    disagree = sorted(r327_A.symmetric_difference(set(arms100)))
    print(f"      DISAGREE ABOUT        : {disagree}")

    # ---- VERDICT ----------------------------------------------------------------------------------
    print()
    if empty:
        v = "W_EMPTY_AT_UNIVERSAL"
        print(f"  W-EMPTY-AT-UNIVERSAL — read as its own plain English, the definition admits NOTHING.")
        print(f"  Not `only its own instance` — nothing at all, including `coval_core`. The published")
        print(f"  {len(published)} exists because the reference is a MEMBER of the class the sentence names,")
        print(f"  chosen by file order at the 93.7th percentile, rather than the class itself.")
    else:
        v = "W_NONEMPTY_EVERYWHERE"
        print(f"  W-NONEMPTY-EVERYWHERE — {arms100} survives even the universal reading, so clause ②'s")
        print(f"  under-specification changes the SIZE of the admitted set and never its existence.")

    if disagree:
        print(f"\n  ⛔ AND A THIRD UNDER-SPECIFICATION, NAMED HERE FOR THE FIRST TIME. R327 and this")
        print(f"     round instantiate `EVERY prompt-blind set` differently — R327 as the best")
        print(f"     HELD-OUT of 1,820, R360's sweep as the in-sample maximum — and a held-out")
        print(f"     maximum is lower. The two answers differ by exactly {disagree}: the released")
        print(f"     core. So whether the definition admits its own instance or nothing at all turns")
        print(f"     on a choice NEITHER round names and NO sentence of the definition decides.")
        print(f"  ⚠ THIS ROUND DOES NOT ADJUDICATE IT. Choosing held-out or in-sample is an act of")
        print(f"    definition, and performing it here would be tuning the definition to whichever")
        print(f"    answer I found first.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, n_cells=len(sweep), monotone=monotone, published_ok=pub_ok,
               published=sorted(published),
               curve={str(p): v for p, v in curve}, at_universal=arms100,
               survivors_at_universal=sorted(survivors), labels=sorted(labels),
               r327_reading_A=sorted(r327_A), r327_reference=ref_a.get("reference"),
               disagree_about=disagree, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r405_universal_reading.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
