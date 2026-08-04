"""R425 -- how far does the unknown instrument reach? The search is the instrument, so control it first.

R424 measured that no committed table emitted the `_08b` SATISFACTION arms, and I closed on "74
artifacts, 30 rounds citing them". Thirty is what `grep -rl 08b` returned. That is the INSTRUMENT's
unit -- a file containing four characters -- and the claim's unit is "a round whose published number
derives from an arm whose emitter is not on disk". The ledger's own entry says those two strings must
be written down and required EQUAL before the control is even designed.

⛔ AND ONE `grep -n` ALREADY SHOWED THEY ARE NOT. `R12_response_set` reads
   `a08_gold_08b.npz` -- a GOLD file, not a satisfaction table -- and R424 tested that file and
   found it carries no `meta`/`sat` at all. It is a DIFFERENT KIND OF OBJECT wearing the same four
   characters, it IS committed, and a round using it is not instrument-unknown in any sense.
   `R361` by contrast reads `sat_{arm}_08b.npz`, which is exposure. Lumping them would have inflated
   the reach with cases that carry no risk -- a label read as a description.

⭐ SO THE POPULATION IS NOT "MENTIONS 08b". It is "reads a SATISFACTION arm (`sat_*_08b*` or
   `core_*_08b*`) whose emitting table R424 could not find". Everything else -- gold files, prose,
   print strings -- is a different question and is counted separately rather than dropped.

⛔ ARITHMETIC TRAP. That a round reading `sat_X_08b.npz` reads a file whose emitter R424 did not
   locate is FORCED once R424's result is granted; this round is not re-testing that. What is NOT
   forced is HOW MANY rounds do it, nor whether reading is the same as PUBLISHING FROM -- and it is
   not: R422-R424 read those arms precisely to AUDIT them, so their numbers are ABOUT the arms rather
   than FROM them. The count is therefore an UPPER BOUND on exposure, and it is labelled as one.

ESTIMAND        (A) the number of rounds whose `run.py` reads a SATISFACTION `_08b` artifact;
                (B) the number that read only the GOLD `_08b` file, whose instrument IS committed;
                (C) the number where `08b` occurs only in prose (docstring or print) and no artifact
                    is read at all;
                (D) (A) minus the audit arc, which is the upper bound on DOWNSTREAM exposure.

IDENTIFICATION  (A)(B)(C) exact for `run.py` files. NOT identified: whether a round in (A) publishes
                a number DERIVED from the arm or merely touches it -- separating those needs reading,
                so (A) is an upper bound and is reported as one. Also not identified: exposure
                through a helper module rather than the round's own source; the scan is over
                `run.py`, and a round loading via `lib/` would be missed. Named, and the scan is
                extended to `lib/` for the count so the miss is bounded rather than assumed absent.

SCOPE           population: every `E0*/A*/R*/run.py` in the repo · instrument: AST string-constant
                classification, docstrings excluded from the artifact classes · baseline: three
                rounds whose class is KNOWN by hand · regime: committed sources, zero compute.

WORLDS
  W-NARROW    the satisfaction-arm readers are few and mostly this audit arc. Then R424's finding is
              a fact about a corner of the repo and the campaign's published numbers are largely
              untouched.
  W-WIDE      many rounds outside the arc read satisfaction `_08b` arms. Then the unknown instrument
              is load-bearing across the campaign and every one of those numbers needs its scope
              rewritten from "0.8B" to "unknown".
  W-BLIND     the classifier cannot reproduce the three hand-established answers. Then the count is
              silence and nothing here is reportable.

PREDICTION MATRIX
  W-NARROW -> (D) small, and the named rounds are inspectable by hand
  W-WIDE   -> (D) large, and the list is the work item
  W-BLIND  -> a known-answer case is misclassified

PRE-REGISTERED KILL -- conditional on the hand-established answers, never on the count alone.
    if R422/R423/R424 classify SAT and R12_response_set classifies GOLD-only and a prose-only
       plant classifies PROSE:
        report (A)(B)(C)(D) as measured, (A) labelled an UPPER bound
    else: W-BLIND -- UNVERIFIED, exit 1. A miscount here would rewrite scopes on the wrong rounds.

CONTROLS
  KNOWN (+)   R422, R423, R424 read `core_*_08b.json` and MUST classify SAT. These are real corpus
              cases whose answer I established by reading the source, not by imagining one.
  KNOWN (-)   `R12_response_set` reads `a08_gold_08b.npz` and MUST classify GOLD-ONLY, never SAT.
              This is the case that separates the instrument's unit from the claim's, and without it
              the count inflates with rounds that carry no exposure.
  PLANT       a synthetic source with `08b` only in a docstring must classify PROSE; one with
              `sat_x_08b.npz` in a code string must classify SAT. Both directions, synthetic, in
              ADDITION to the real cases -- a classifier validated only on cases I invented is
              validated against my imagination.
  UNIT        the two units are printed side by side and their INEQUALITY is stated: the instrument
              sees `reads an artifact`, the claim wants `publishes a number derived from it`. They
              are not equal, so (A) is an upper bound. Printing this is the control.
  NON-EMPTY   zero rounds scanned is exit 2, never a clean count.

MULTIPLICITY    3 classes x every round; all counts printed, and the SAT list printed in full so the
                claim can be attacked round by round rather than trusted as a total.
SEEDS           none.
ARTIFACT        results/r425_reach_of_the_unknown_instrument.json with the source hash.

IMPOSSIBLE HERE
  reads vs publishes-from -- needs reading; (A) is an upper bound and (D) subtracts only the audit
                             arc, which is the one subset established by construction.
  exposure through data files rather than source -- a round consuming a downstream artifact that was
                             itself built from an `_08b` arm is invisible to a source scan. Named;
                             it would need a provenance graph, which is exactly what the artifacts
                             do not carry.
  cross-release           -- one release.

EXIT
    0  the known-answer cases reproduce and the counts are reported
    1  a known-answer case is misclassified -- W-BLIND, UNVERIFIED
    2  nothing was scanned -- never a clean count
"""
from __future__ import annotations
import ast
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
# a SATISFACTION arm: the objects R424 could not find an emitter for.
SAT = re.compile(r"(?:sat|core)_[A-Za-z0-9_{}]*08b")
# the GOLD file: a DIFFERENT KIND OF OBJECT with the same four characters, and it IS committed.
GOLD = re.compile(r"a08_gold_08b")
ARC = ("R422", "R423", "R424", "R425")


def classify(src: str):
    """-> ('SAT'|'GOLD'|'PROSE'|'NONE', evidence)

    Docstrings are DESIGN PROSE and are excluded from the artifact classes; a filename in a docstring
    is a discussion of a file, not a read of one. Every other string constant is code."""
    if "08b" not in src:
        return "NONE", None
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return "UNPARSEABLE", f"{type(e).__name__}: {e}"
    docs = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            d = ast.get_docstring(node, clean=False)
            if d:
                docs.add(d)
    code = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value not in docs and "08b" in node.value:
                code.append(node.value)
        elif isinstance(node, ast.JoinedStr):          # f-strings: keep the literal parts
            lit = "".join(v.value for v in node.values
                          if isinstance(v, ast.Constant) and isinstance(v.value, str))
            if "08b" in lit:
                code.append(lit)
    sats = [c for c in code if SAT.search(c)]
    golds = [c for c in code if GOLD.search(c)]
    if sats:
        return "SAT", sats[0][:70]
    if golds:
        return "GOLD", golds[0][:70]
    return "PROSE", (code[0][:70] if code else "docstring only")


def main() -> int:
    # ---- CONTROLS ---------------------------------------------------------------------------------
    plant_prose = classify('"""a docstring naming sat_x_08b.npz"""\nimport os\n')[0]
    plant_sat = classify('"""d"""\nimport numpy as np\nnp.load("sat_x_08b.npz")\n')[0]
    p_ok = (plant_prose == "PROSE" and plant_sat == "SAT")

    known = {}
    for pat, want in ((f"E0*/A*/{r}_*/run.py", "SAT") for r in ("R422", "R423", "R424")):
        for p in ROOT.glob(pat):
            known[str(p.relative_to(ROOT))] = (classify(p.read_text())[0], want)
    for p in ROOT.glob("E0*/A*/R12_response_set/run.py"):
        known[str(p.relative_to(ROOT))] = (classify(p.read_text())[0], "GOLD")
    k_ok = bool(known) and all(g == w for g, w in known.values())

    print("R425 · how far does the unknown instrument reach?\n")
    print("  ⛔ `30 ROUNDS` WAS THE INSTRUMENT'S UNIT, NOT THE CLAIM'S. `grep -rl 08b` counts files")
    print("     containing four characters. The claim is about rounds reading a SATISFACTION arm")
    print("     whose emitter R424 could not find — and R12_response_set reads `a08_gold_08b.npz`,")
    print("     a GOLD file that IS committed. Same four characters, different kind of object.\n")

    print("  CONTROLS")
    print(f"    PLANT      docstring-only -> {plant_prose} · code `sat_x_08b.npz` -> {plant_sat}   "
          f"{'PASS' if p_ok else 'FAIL'}")
    print(f"    KNOWN      real cases whose class I established BY READING THE SOURCE, not by")
    print(f"               imagining one:")
    for f, (got, want) in sorted(known.items()):
        print(f"      {f[-64:]:<64} want {want:<5} got {got:<5} "
              f"{'ok' if got == want else '⛔ MISCLASSIFIED'}")
    print(f"    UNIT       instrument sees : `run.py reads an _08b satisfaction artifact`")
    print(f"               claim wants     : `a published number DERIVES from that arm`")
    print(f"               ⚠ THESE ARE NOT EQUAL. R422–R424 read those arms to AUDIT them, so their")
    print(f"                 numbers are ABOUT the arms, not FROM them. (A) is an UPPER BOUND.")
    if not (p_ok and k_ok):
        print("\n  W-BLIND — a known-answer case is misclassified. A miscount here would rewrite")
        print("  scopes on the wrong rounds. UNVERIFIED, exit 1."); return 1

    # ---- the census --------------------------------------------------------------------------------
    cls = {"SAT": [], "GOLD": [], "PROSE": [], "UNPARSEABLE": []}
    scanned = 0
    for p in sorted(ROOT.glob("E0*/A*/R*/run.py")) + sorted(ROOT.glob("lib/*.py")):
        scanned += 1
        c, ev = classify(p.read_text())
        if c != "NONE":
            cls[c].append((str(p.relative_to(ROOT)), ev))
    if not scanned:
        print("\n  UNRUNNABLE: nothing scanned. Exit 2, never a clean count."); return 2

    print(f"\n  THE CENSUS — {scanned} sources scanned")
    print(f"    (A) reads a SATISFACTION _08b arm (emitter NOT on disk) : {len(cls['SAT']):>3}")
    print(f"    (B) reads only the GOLD _08b file (IS committed)        : {len(cls['GOLD']):>3}")
    print(f"    (C) `08b` in prose only, no artifact read               : {len(cls['PROSE']):>3}")
    print(f"    (-) unparseable                                          : "
          f"{len(cls['UNPARSEABLE']):>3}")

    arc = [f for f, _ in cls["SAT"] if any(a in f for a in ARC)]
    downstream = [(f, e) for f, e in cls["SAT"] if not any(a in f for a in ARC)]
    print(f"\n    (D) SAT readers OUTSIDE this audit arc — the upper bound on DOWNSTREAM exposure:"
          f" {len(downstream)}")
    print(f"        (the arc itself contributes {len(arc)}, by construction)")
    for f, e in downstream:
        print(f"      {f[-62:]:<62} {str(e)[:34]}")

    print()
    if not downstream:
        v = "W_NARROW"
        print(f"  W-NARROW — every satisfaction-arm reader is this audit arc. R424's finding is a fact")
        print(f"  about a corner of the repo and no published number outside it derives from the")
        print(f"  unknown instrument through a source path.")
    elif len(downstream) <= 8:
        v = "W_NARROW"
        print(f"  W-NARROW — {len(downstream)} rounds outside the arc read a satisfaction `_08b` arm.")
        print(f"  That is small enough to inspect BY HAND, and the list above is the work item rather")
        print(f"  than a number to quote. Each still needs the reads-vs-publishes-from question asked")
        print(f"  of it individually; this count does not answer that and does not claim to.")
    else:
        v = "W_WIDE"
        print(f"  W-WIDE — {len(downstream)} rounds outside the arc read a satisfaction `_08b` arm.")
        print(f"  The unknown instrument is load-bearing across the campaign, and every number those")
        print(f"  rounds published needs its scope rewritten from `0.8B` to `unknown`.")

    print(f"\n  ⚠ (A) IS AN UPPER BOUND ON EXPOSURE, NOT A COUNT OF IT. Reading an arm is not")
    print(f"    publishing a number derived from it.")
    print(f"  ⚠ AND A SOURCE SCAN CANNOT SEE EXPOSURE THROUGH DATA: a round consuming a downstream")
    print(f"    artifact itself built from an `_08b` arm is invisible here. That needs a provenance")
    print(f"    graph, which is exactly what these artifacts do not carry.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               scanned=scanned, sat=cls["SAT"], gold=cls["GOLD"], prose=cls["PROSE"],
               unparseable=cls["UNPARSEABLE"], arc=arc, downstream=downstream,
               n_sat=len(cls["SAT"]), n_gold=len(cls["GOLD"]), n_prose=len(cls["PROSE"]),
               n_downstream=len(downstream), verdict=v,
               controls=dict(plant_prose=plant_prose, plant_sat=plant_sat,
                             known={k: list(v2) for k, v2 in known.items()}))
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r425_reach_of_the_unknown_instrument.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
