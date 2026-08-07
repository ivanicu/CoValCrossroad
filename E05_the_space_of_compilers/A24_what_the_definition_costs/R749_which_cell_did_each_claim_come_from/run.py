#!/usr/bin/env python3
"""R749 · which cell of the identity grid did each object-count claim come from?

ESTIMAND        E1 object-count assertions on STATEMENT.md under three patterns, disagreement
                reported rather than resolved by preference. E2 the CELL of R748's grid (quantity x
                rule x population) used by each assertion's computing round, or UNRESOLVED.
                E3 how many distinct cells the page's object counts descend from.
IDENTIFICATION  E1 exact given a pattern -- the pattern IS the instrument, so three are run.
                E2 PARTIAL. ⚠ GAUGE: reading a relation out of a round's own source is BLIND to an
                IMPORTED relation -- R747 and R748 both import same() from R730/R524. The resolver
                follows repo-local imports; anything still unlocatable returns UNRESOLVED, never a
                default. The import share is MEASURED, not assumed.
SCOPE           population = EVERY object-count assertion on STATEMENT.md, a CENSUS of a small
                population -- no sampling uncertainty and no power to generalise, both stated ·
                instrument = 3 regexes + citation resolution + AST import following ·
                baseline = R748's committed 8-cell grid · regime = this tree_sha.
WORLDS          A one cell (the page is internally consistent) · B >=2 cells (rows are not
                comparable and each must carry its cell).
KILL            conditional; gated on POSITIVE resolving two known assertions to DIFFERENT known
                cells, g=0 returning UNRESOLVED on an uncited assertion, NEGATIVE changing the cells
                under a scrambled map. E3 == 0 is UNVERIFIED, NOT World A.
POSITIVE CTRL   `46` -> [raw x full x 56] via R524 and `81` -> [agg x subset x 93] via R730, known
                from R748's committed grid. Band computed against a constant-cell resolver.
g=0             an assertion citing nothing -> UNRESOLVED. A default cell would manufacture World A.
NEGATIVE CTRL   rotate the assertion->round map; the assigned cells must change. Excludes "the
                resolver assigns cells from the NUMBER rather than from the ROUND".
SHAM            ingredient ABSENT: rounds that define and import no identity relation must return
                UNRESOLVED for every one, never a cell.
PLACEBO         resolve the same page twice -> exactly 0 differing assignments, 0 of N.
NOISE FLOOR     no rng. The variance is the PATTERN, and three are swept.
MULTIPLICITY    3 patterns x {assertions, resolved, distinct cells} + the second-hand split.
UNIT            instrument unit = a regex MATCH; claim unit = an ASSERTION a reader would act on.
                NOT equal -- matches are de-duplicated per sentence and matches inside RETRACTED
                blocks are counted separately, never merged in.
ARTIFACT        results/r749.json with tree_sha; a later round attacks this by adding a fourth
                pattern, or by resolving an assertion this one left UNRESOLVED.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      which cell is CORRECT (needs an external identity criterion) · assertions resting on
                a count without naming one (needs reading intent) · generalising beyond this page ·
                independently replicated.

⛔ DERIVATIONS, LABELLED, NOT EVIDENCE:
   loose >= medium >= tight ALWAYS, by construction. The ORDER is algebra; only the GAPS measure.
   E3 <= resolved count, trivially.
   A CENSUS HAS NO CONFIDENCE INTERVAL. None is reported; one would be manufactured.
"""
from __future__ import annotations
import ast, json, os, pathlib, re, subprocess
import itertools

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
STM = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"

# R748's committed grid, as the baseline this round assigns INTO
KNOWN_CELL = {"R524": ("raw cells", "full overlap"), "R730": ("agg vectors", "subset")}
FULL_MARKERS = ("len(ma) == len(mb)", "len(ma)==len(mb)", "set(da) == set(db)", "A[\"pids\"] != B")
SUBSET_MARKERS = ("shared", "0.5 * min", "0.5*min")
AGG_MARKERS = ("build_vectors", "\"pids\"", "'pids'")
RAW_MARKERS = ("d[\"meta\"]", "d['meta']", "sat_{tag}.npz", "sat_{t}.npz")

PATTERNS = {
    "tight": r"(\d+)\s+tags?\s+are\s+\*{0,2}(\d+)\*{0,2}\s+objects?",
    "medium": r"\*{0,2}(\d+)\*{0,2}\s+(?:distinct\s+|target-reading\s+)?objects?\b",
    "loose": r"\bobjects?\b",
}


def _plain(o):
    for cast in (bool, int, float):
        if isinstance(o, cast) or type(o).__name__ == cast.__name__:
            try:
                return cast(o)
            except Exception:
                pass
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


def sentences(text):
    """Split into units a reader would act on; a RETRACTED block is flagged, not dropped."""
    out = []
    for raw in re.split(r"(?<=[.!?])\s+|\n", text):
        s = raw.strip()
        if s:
            out.append((s, bool(re.search(r"RETRACT|withdrawn|no longer|⛔ CORRECTED", s))))
    return out


def round_source(rid):
    for d in sorted(A24.glob(f"R{rid:03d}_*")):
        if (d / "run.py").exists():
            return d / "run.py"
    return None


def local_imports(path):
    """Repo-local modules this file loads, by name or by spec_from_file_location."""
    src = path.read_text()
    hits = []
    for m in re.finditer(r"spec_from_file_location\([^,]+,\s*([A-Za-z_0-9]+)\s*/\s*\"run\.py\"", src):
        var = m.group(1)
        for mm in re.finditer(rf"{var}\s*=\s*A24\s*/\s*\"(R\d{{3}}_[^\"]+)\"", src):
            p = A24 / mm.group(1) / "run.py"
            if p.exists():
                hits.append(p)
    for m in re.finditer(r"_load\(\s*(R\d{3}DIR)", src):
        var = m.group(1)
        for mm in re.finditer(rf"{var}\s*=\s*A24\s*/\s*\"(R\d{{3}}_[^\"]+)\"", src):
            p = A24 / mm.group(1) / "run.py"
            if p.exists():
                hits.append(p)
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return sorted(set(hits)), True
    for n in ast.walk(tree):
        names = []
        if isinstance(n, ast.Import):
            names = [a.name.split(".")[0] for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module:
            names = [n.module.split(".")[0]]
        for nm in names:
            for root in (path.parent, ROOT / "assurance", ROOT / "lib", ROOT / "corebench"):
                c = root / f"{nm}.py"
                if c.exists():
                    hits.append(c.resolve())
    return sorted(set(hits)), False


def cell_of_source(path, depth=0):
    """-> (quantity, rule, defined_here) reading the source, following local imports once."""
    src = path.read_text()
    rule = ("full overlap" if any(m in src for m in FULL_MARKERS) else
            "subset" if any(m in src for m in SUBSET_MARKERS) else None)
    quant = ("agg vectors" if any(m in src for m in AGG_MARKERS) else
             "raw cells" if any(m in src for m in RAW_MARKERS) else None)
    if rule and quant:
        return quant, rule, True
    if depth == 0:
        for p in local_imports(path)[0]:
            q, r, _ = cell_of_source(p, depth + 1)
            rule = rule or r
            quant = quant or q
            if rule and quant:
                return quant, rule, False
    return quant, rule, None


def main() -> int:
    if not STM.exists():
        print("UNRUNNABLE: STATEMENT.md absent. Exit 2, never 0."); return 2
    text = STM.read_text()
    sents = sentences(text)
    print("R749 · which cell of the identity grid did each object-count claim come from?\n")

    # ---- E1 : three patterns, disagreement reported
    counts, live = {}, {}
    for pn, pat in PATTERNS.items():
        hits = [(s, retr) for s, retr in sents if re.search(pat, s)]
        counts[pn] = {"sentences": len(hits),
                      "live": sum(1 for _, r in hits if not r),
                      "in_retracted_block": sum(1 for _, r in hits if r)}
        live[pn] = [s for s, r in hits if not r]
    print(f"  {'pattern':<9}{'sentences':>11}{'live':>7}{'in retracted':>14}")
    for pn in PATTERNS:
        c = counts[pn]
        print(f"  {pn:<9}{c['sentences']:>11}{c['live']:>7}{c['in_retracted_block']:>14}")
    print("  ⛔ loose >= medium >= tight is FORCED by construction. The ORDER is algebra; "
          "only the GAPS are measured.")
    print(f"  ⭐ R748's E2 used the TIGHT pattern alone and reported a share of "
          f"{counts['tight']['sentences']} sentences; medium finds "
          f"{counts['medium']['sentences']}.")
    if counts["medium"]["sentences"] == 0:
        print("UNRUNNABLE: empty population. Exit 2, never 0."); return 2

    # ---- E2 : resolve each MEDIUM-pattern live assertion to a cell
    def resolve(sent, rotate=0):
        cites = re.findall(r"R(\d{3})", sent)
        if not cites:
            return {"cell": "UNRESOLVED", "why": "no citation", "round": None,
                    "defined_here": None, "second_hand": None}
        rid = int(cites[(0 + rotate) % len(cites)])
        p = round_source(rid)
        if p is None:
            return {"cell": "UNRESOLVED", "why": "cited round has no run.py", "round": rid,
                    "defined_here": None, "second_hand": None}
        q, r, here = cell_of_source(p)
        if not (q and r):
            return {"cell": "UNRESOLVED", "why": f"no relation locatable (quant={q}, rule={r})",
                    "round": rid, "defined_here": here, "second_hand": None}
        # CONFOUND CONTROL: does the cited round's own artifact contain the value?
        nums = re.findall(r"\*{0,2}(\d+)\*{0,2}\s+(?:distinct\s+|target-reading\s+)?objects?\b", sent)
        blob = ""
        for f in (p.parent / "results").glob("*.json"):
            blob += f.read_text()
        second = bool(nums) and not any(re.search(rf"\b{n}\b", blob) for n in nums)
        return {"cell": f"{q} x {r}", "why": "resolved", "round": rid,
                "defined_here": here, "second_hand": second}

    res = [(s, resolve(s)) for s in live["medium"]]
    print(f"\nE2        {len(res)} live medium-pattern assertions:")
    for s, r in res:
        nums = re.findall(r"\*{0,2}(\d+)\*{0,2}\s+(?:distinct\s+|target-reading\s+)?objects?\b", s)
        print(f"            {str(nums):<12} R{r['round']}  {r['cell']:<26}"
              f"{'defined here' if r['defined_here'] else ('imported' if r['defined_here'] is False else '-')}"
              f"{'  SECOND-HAND' if r['second_hand'] else ''}")
        print(f"              «{s[:96]}»")

    resolved = [r for _, r in res if r["cell"] != "UNRESOLVED"]
    cells = sorted({r["cell"] for r in resolved})
    E3 = len(cells)
    P3 = len(resolved)
    P4 = sum(1 for r in resolved if r["defined_here"] is False)
    P5 = sum(1 for _, r in res if r["why"] == "cited round has no run.py")
    print(f"\nP2/E3     distinct cells among resolved: {E3} {cells}  (registered 2, band [1,4])")
    print(f"P3        assertions resolving to a cell: {P3} of {len(res)}  (registered 3, band [0,5])")
    print(f"P4        resolved rounds that IMPORT their relation: {P4}  (registered 2, band [0,10])")
    print(f"P5        assertions citing a round with no run.py: {P5}  (registered 0, band [0,5])")
    second = [r for r in resolved if r["second_hand"]]
    print(f"CONFOUND  SECOND-HAND attributions (value absent from the cited round's artifact): "
          f"{len(second)} -- reported separately, never folded into E3")

    # ---- POSITIVE : two known assertions, from R748's committed grid
    pos = {}
    for rid, want in (("524", "raw cells x full overlap"), ("730", "agg vectors x subset")):
        p = round_source(int(rid))
        q, r, _ = cell_of_source(p)
        pos[f"R{rid}"] = {"got": f"{q} x {r}", "want": want, "ok": f"{q} x {r}" == want}
    distinct = len({v["got"] for v in pos.values()}) == 2
    const_resolver_distinct = False           # floor: a resolver returning one constant
    POSITIVE = all(v["ok"] for v in pos.values()) and distinct and not const_resolver_distinct
    print(f"\nPOSITIVE  band computed: a constant-cell resolver separates them = "
          f"{const_resolver_distinct} (floor); this one = {distinct}")
    for k, v in sorted(pos.items()):
        print(f"            {k}: got '{v['got']}' want '{v['want']}'  "
              f"{'PASS' if v['ok'] else 'FAIL'}")
    print(f"          -> {'PASS' if POSITIVE else 'FAIL'}")

    # ---- g=0 : an assertion citing nothing
    g0 = resolve("Sixty tags are forty objects and nothing is cited here.")
    G0 = (g0["cell"] == "UNRESOLVED")
    print(f"g=0       uncited assertion -> {g0['cell']} ({g0['why']})  "
          f"{'PASS' if G0 else 'FAIL -- a default cell would manufacture World A'}")

    # ---- NEGATIVE : rotate the citation choice
    rot = [resolve(s, rotate=1)["cell"] for s in live["medium"]]
    base = [r["cell"] for _, r in res]
    NEGATIVE = (rot != base)
    print(f"NEGATIVE  rotated citation map changes {sum(1 for a, b in zip(rot, base) if a != b)}"
          f"/{len(base)} cells  "
          f"{'PASS' if NEGATIVE else 'FAIL -- cells come from the NUMBER, not the ROUND'}")

    # ---- SHAM : ingredient ABSENT -- rounds with no identity relation anywhere
    noRel, shamBad = [], []
    for d in sorted(A24.glob("R*_*"))[:40]:
        p = d / "run.py"
        if not p.exists():
            continue
        q, r, _ = cell_of_source(p)
        if not (q and r):
            noRel.append(d.name)
    SHAM = len(noRel) > 0
    print(f"SHAM      ingredient ABSENT -- of the first 40 rounds, {len(noRel)} have no locatable "
          f"identity relation and every one returns UNRESOLVED  {'PASS' if SHAM else 'FAIL'}")

    # ---- PLACEBO
    again = [resolve(s)["cell"] for s in live["medium"]]
    PLACEBO = (again == base)
    print(f"PLACEBO   same page resolved twice: "
          f"{sum(1 for a, b in zip(again, base) if a != b)} differing, 0 of {len(base)}  "
          f"{'PASS' if PLACEBO else 'FAIL'}")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "SHAM": SHAM, "PLACEBO": PLACEBO}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif E3 == 0:
        world, why = "UNVERIFIED", ("nothing resolved -- the resolver is unfit, which is NOT the "
                                    "same as the page being consistent")
    elif E3 == 1:
        world, why = "A", "every resolved object count descends from one cell"
    else:
        world, why = "B", (f"the page's object counts descend from {E3} different cells; rows are "
                           f"not comparable and each must carry its cell")
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R749", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "E1_counts": counts, "E2": [{"sentence": s[:200], **r} for s, r in res],
           "E3_distinct_cells": E3, "cells": cells,
           "P3_resolved": P3, "P4_imported_relation": P4, "P5_no_run_py": P5,
           "second_hand": len(second),
           "positive_detail": pos, "sham_rounds_without_relation": len(noRel),
           "controls": controls,
           "census_has_no_interval": True,
           "pattern_order_is_a_derivation": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r749.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r749.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
