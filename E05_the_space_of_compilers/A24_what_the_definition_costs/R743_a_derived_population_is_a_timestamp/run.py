#!/usr/bin/env python3
"""R743 · a derived population is a timestamp

ESTIMAND        among rounds cited by STATEMENT.md's TEN CLAIM ROWS -- the rows inheriting the one
                population constant "R294's 41 arms" -- the fraction whose run.py obtains its arm
                population by a LIVE GLOB rather than by explicit enumeration.
IDENTIFICATION  identified from SOURCE (ast). NOT identified from artifact fields: a population
                size is recorded under 19 key spellings across 465 artifacts, commonest covering
                35. That estimand was killed by the gauge test before this file was written.
SCOPE           population = distinct R### inside the ten claim rows · instrument = ast, classifier
                REUSED from assurance/arm_population_is_derived.py · baseline = the complement
                population (A24 rounds not cited by the claim rows) · regime = this tree_sha.
WORLDS          A the constant is a SCOPE (f<=0.25) · B the constant is a TIMESTAMP (f>=0.60) ·
                C mixed, and one column cannot carry both (0.25<f<0.60).
KILL            conditional; gated on POSITIVE firing and NEGATIVE being null. See PREREGISTRATION.
POSITIVE CTRL   R728 -> DERIVED, R477 -> TYPED/DECLARED; band computed (0 < 2 <= n_parseable).
                (R719 was the first choice and was WRONG -- see the note at the control itself.)
NEGATIVE CTRL   delete every glob call from a known-DERIVED source, keep the rest -> class flips.
                Excludes the world "the classifier fires on any file".
SHAM            same operation, ingredient ABSENT (not inverted): the complement population.
PLACEBO         classify files with no Python (README.md) -> must report 0 of 0, distinguished
                from 0 of N.
NOISE FLOOR     the classifier is deterministic on source; the variance is the DETECTOR choice --
                three variants swept, all reported.
MULTIPLICITY    3 detectors x 2 populations = 6 cells; survivors and non-survivors both printed.
SPECIFICATION   the three detectors ARE the curve, not a footnote.
SEEDS           no rng in this design. Determinism verified by two PYTHONHASHSEED runs, both
                writes confirmed.
ARTIFACT        results/r743.json with tree_sha; a later round attacks this by re-running the
                detectors with a fourth variant, or by dating the glob's growth.
IMPOSSIBLE      independently replicated (a second team) · cross-site (one repository) ·
                temporally resolved (git records the tree, not each round's run-day listing).
"""
from __future__ import annotations
import ast, json, os, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
STM = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"
sys.path.insert(0, str(ROOT / "assurance"))
import arm_population_is_derived as APD  # P4: REUSE. Its ARM_NAMES come from the arm store on disk.

GLOBFN = ("glob", "iglob", "iterdir", "listdir", "discover")


def _plain(o):
    """numpy-2's np.bool_ has __class__.__name__ == 'bool', so json's own check misses it."""
    for cast in (bool, int, float):
        if isinstance(o, cast) or type(o).__name__ == cast.__name__:
            try:
                return cast(o)
            except Exception:
                pass
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


# ---------------------------------------------------------------- the three detectors
def _glob_calls(tree):
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            name = getattr(n.func, "attr", getattr(n.func, "id", ""))
            if name in GLOBFN:
                pats = [a.value for a in n.args if isinstance(a, ast.Constant)
                        and isinstance(a.value, str)]
                yield name, pats


def det_loose(tree):
    """The EXISTING gate's rule: any glob-family call anywhere in the file."""
    return any(True for _ in _glob_calls(tree))


def det_medium(tree):
    """A glob whose pattern literal names the arm store's file type."""
    return any(any(("sat_" in p) or (".npz" in p) for p in pats) for _, pats in _glob_calls(tree))


def det_tight(tree):
    """A glob whose pattern literal IS the arm store's own pattern."""
    return any(any(p.startswith("sat_") for p in pats) for _, pats in _glob_calls(tree))


DETECTORS = [("loose", det_loose), ("medium", det_medium), ("tight", det_tight)]


def classify(src: str, det) -> str:
    """-> NO_ARMS / DECLARED / UNPARSEABLE / DERIVED / TYPED / NONE, under one detector."""
    if not APD.LOADS.search(src):
        return "NO_ARMS"
    if APD.DECL.search(src):
        return "DECLARED"
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return "UNPARSEABLE"
    if det(tree):
        return "DERIVED"
    if any(APD._literal_arm_seq(n) for n in ast.walk(tree)):
        return "TYPED"
    return "NONE"


HAS_POP = ("DERIVED", "TYPED", "DECLARED")


def frac(counts: dict) -> float | None:
    d = sum(counts.get(k, 0) for k in HAS_POP)
    return None if d == 0 else counts.get("DERIVED", 0) / d


# ---------------------------------------------------------------- the claim rows
def claim_row_citations(text: str):
    """The ten rows of the claim table. Returns (n_rows, sorted round ids, the raw rows)."""
    lines = text.splitlines()
    hdr = [i for i, l in enumerate(lines) if l.startswith("| # | claim |")]
    if not hdr:
        return 0, [], []
    rows = []
    for l in lines[hdr[0] + 2:]:
        if not l.startswith("|"):
            break
        rows.append(l)
    cites = sorted({int(x) for r in rows for x in re.findall(r"\bR(\d{3})\b", r)})
    return len(rows), cites, rows


def run_dir(rid: int):
    ds = sorted(A24.glob(f"R{rid:03d}_*"))
    return [d for d in ds if (d / "run.py").exists()]


def main() -> int:
    if not STM.exists():
        print("UNRUNNABLE: STATEMENT.md absent. Exit 2, never 0."); return 2
    text = STM.read_text()
    n_rows, cited, rows = claim_row_citations(text)
    print("R743 · a derived population is a timestamp\n")
    print(f"claim table: {n_rows} rows, {len(cited)} distinct rounds cited")
    if n_rows == 0 or not cited:
        print("UNRUNNABLE: the claim table did not parse. Empty population must exit 2."); return 2

    # ---- UNIT control: the INSTRUMENT unit must not be coarser than the CLAIM unit.
    #
    # ⛔ REPAIRED AFTER ITS FIRST RUN, AND THE REPAIR IS THE POINT. v1 demanded EXACTLY one run.py
    #    per cited round and FAILED on R580 and R581 -- which have a README and results and no
    #    run.py at all. That is a KNOWN category here (R592 studied the codeless rounds) and it has
    #    nothing to do with whether a population is a timestamp. §4's dominant mode: the control
    #    failed for its OWN reasons. The property is "one round never maps to two sources"; a round
    #    mapping to ZERO sources is a separate, named fact and is excluded from the denominator BY
    #    CONSTRUCTION rather than by silence.
    unit_bad, no_code, resolved = [], [], {}
    for r in cited:
        ds = run_dir(r)
        if len(ds) > 1:
            unit_bad.append((r, len(ds)))
        elif not ds:
            no_code.append(r)
        else:
            resolved[r] = ds[0]
    print(f"UNIT      cited rounds mapping to >1 run.py: {len(unit_bad)} (property: never >1)")
    print(f"            codeless cited rounds, NAMED and excluded from every denominator: "
          f"{no_code or 'none'}")

    # ---- the complement population (the SHAM: ingredient absent, not inverted)
    all_rounds = sorted({int(m.group(1)) for d in A24.glob("R*_*")
                         if (m := re.match(r"R(\d{3})_", d.name)) and (d / "run.py").exists()})
    complement = [r for r in all_rounds if r not in set(cited)]
    print(f"complement population (ingredient ABSENT): {len(complement)} rounds\n")

    srcs = {r: (resolved[r] / "run.py").read_text() for r in sorted(resolved)}
    comp_srcs = {}
    for r in complement:
        ds = run_dir(r)
        if ds:
            comp_srcs[r] = (ds[0] / "run.py").read_text()

    # ---- POSITIVE CONTROL, with a COMPUTED band
    n_parseable = 0
    for s in srcs.values():
        try:
            ast.parse(s); n_parseable += 1
        except SyntaxError:
            pass
    # ⛔ THE SECOND POSITIVE CASE WAS REPLACED, AND WHY MATTERS. v1 used R719, expecting TYPED
    #    because it runs on the literal set PUBLISHED_FIVE. It returned NO_ARMS -- correctly:
    #    R719 works on PUBLISHED ARM NAMES from a card and never loads a `sat_*.npz`, so the
    #    classifier's gate (does this file load an arm artifact?) is not even reached. My
    #    EXPECTATION was wrong, not the instrument -- §4 form ③, a control aimed at a different
    #    statistic than the one reported.
    #    The replacement's expectation is grounded OUTSIDE this instrument, in the record:
    #    assurance/arm_population_is_derived.py's own docstring states "R477 bounded the
    #    ③-admissible class by the nine arms that happened to carry a `.npz`" -- a hand-typed
    #    population, documented by the round that CORRECTED it (R478), not by this classifier.
    pos = {}
    for rid, want in ((728, "DERIVED"), (477, ("TYPED", "DECLARED"))):
        ds = run_dir(rid)
        got = classify((ds[0] / "run.py").read_text(), det_medium) if ds else "MISSING"
        pos[f"R{rid}"] = {"got": got, "want": want,
                          "ok": got == want if isinstance(want, str) else got in want}
    n_pos = sum(1 for v in pos.values() if v["ok"])
    band_ok = 0 < 2 <= n_parseable          # floor < threshold <= ceiling, COMPUTED not chosen
    print("POSITIVE  band computed, not chosen: floor 0 DERIVED, ceiling "
          f"{n_parseable} (every parseable cited round), threshold 2 -> admissible={band_ok}")
    for k, v in sorted(pos.items()):
        print(f"            {k}: got {v['got']!r}, want {v['want']!r}  {'PASS' if v['ok'] else 'FAIL'}")
    POSITIVE = (n_pos == 2) and band_ok

    # ---- g=0 : a source with no arm code must return NO_ARMS, never a silent class
    g0 = classify("import os\nx = 1\nprint(x)\n", det_medium)
    G0 = (g0 == "NO_ARMS")
    print(f"g=0       source with no arm code -> {g0!r}  {'PASS' if G0 else 'FAIL'}")

    # ---- NEGATIVE : strip globs from a known-DERIVED source, keep everything else
    donor = (run_dir(728)[0] / "run.py").read_text()
    stripped = re.sub(r"\.(?:%s)\(" % "|".join(GLOBFN), ".__nothing__(", donor)
    before, after = classify(donor, det_medium), classify(stripped, det_medium)
    NEGATIVE = (before == "DERIVED" and after != "DERIVED")
    print(f"NEGATIVE  R728 {before!r} -> glob calls removed -> {after!r}  "
          f"{'PASS' if NEGATIVE else 'FAIL'}  (excludes: the classifier fires on any file)")

    # ---- PLACEBO : files with no Python at all
    readmes = [d / "README.md" for d in sorted(A24.glob("R*_*")) if (d / "README.md").exists()]
    pl_arm = sum(1 for p in readmes if APD.LOADS.search(p.read_text()))
    pl_der = 0
    for p in readmes:
        s = p.read_text()
        try:
            if det_medium(ast.parse(s)):
                pl_der += 1
        except SyntaxError:
            pass
    PLACEBO = (pl_der == 0) and (len(readmes) > 0)
    print(f"PLACEBO   {len(readmes)} README.md: {pl_der} DERIVED -- '0 of {len(readmes)}', "
          f"not '0 of 0'  {'PASS' if PLACEBO else 'FAIL'}")
    print(f"            (of those, {pl_arm} MENTION an arm artifact in prose -- the detector is "
          f"looking at a real population, not an empty one)\n")

    # ---- THE GRID : 3 detectors x 2 populations, all six cells
    grid, per_round = {}, {}
    for dname, det in DETECTORS:
        for pname, S in (("cited", srcs), ("complement", comp_srcs)):
            c = {}
            for r, s in sorted(S.items()):
                k = classify(s, det)
                c[k] = c.get(k, 0) + 1
                if pname == "cited":
                    per_round.setdefault(r, {})[dname] = k
            grid[f"{dname}|{pname}"] = {"counts": c, "f": frac(c),
                                        "n_with_population": sum(c.get(x, 0) for x in HAS_POP),
                                        "n_total": len(S)}
    print(f"  {'detector':<9}{'population':<13}{'DERIVED':>8}{'TYPED':>7}{'DECL':>6}"
          f"{'NO_ARMS':>9}{'NONE':>6}{'n_pop':>7}{'f':>9}")
    for dname, _ in DETECTORS:
        for pname in ("cited", "complement"):
            g = grid[f"{dname}|{pname}"]; c = g["counts"]
            f = g["f"]
            print(f"  {dname:<9}{pname:<13}{c.get('DERIVED',0):>8}{c.get('TYPED',0):>7}"
                  f"{c.get('DECLARED',0):>6}{c.get('NO_ARMS',0):>9}{c.get('NONE',0):>6}"
                  f"{g['n_with_population']:>7}" + (f"{f:>9.4f}" if f is not None else f"{'n/a':>9}"))

    # ---- P4 : cross-detector agreement, per round
    agree = [r for r, d in per_round.items() if len({d[n] for n, _ in DETECTORS}) == 1]
    p4 = len(agree) / len(per_round) if per_round else None
    print(f"\nP4        detectors agree on {len(agree)}/{len(per_round)} cited rounds"
          + (f" = {p4:.4f}" if p4 is not None else ""))

    # ---- P3 : what does each cited DERIVED round's glob return TODAY?
    stated = 41  # the page's line-84 constant; a literal here so the comparison is stateable
    today = []
    for r, d in sorted(per_round.items()):
        if d["medium"] != "DERIVED":
            continue
        s = srcs[r]
        pats = sorted({p for _, ps in _glob_calls(ast.parse(s)) for p in ps
                       if "sat_" in p or ".npz" in p})
        for p in pats:
            n = len(list((ROOT / "corebench" / "results").glob(p)))
            today.append({"round": r, "pattern": p, "returns_today": n,
                          "differs_from_stated_41": n != stated})
    n_diff = sum(1 for t in today if t["differs_from_stated_41"])
    print(f"P3        cited DERIVED rounds' arm-store globs, evaluated TODAY: "
          f"{len(today)} patterns, {n_diff} return a count != the page's stated {stated}")
    for t in today[:12]:
        print(f"            R{t['round']:03d}  {t['pattern']:<18}-> {t['returns_today']:>4}"
              f"{'   != 41' if t['differs_from_stated_41'] else '   == 41'}")
    # ⚠ P6, SAFE SIDE. This is the RAW file count the pattern returns. R728 reports the census
    #   population at 92 today. Whether 101 and 92 differ because R294 filters after globbing is
    #   NOT established by this instrument -- it needs the construction step, not a search. The
    #   relation is UNVERIFIED and is reported as such rather than reconciled in prose.
    print(f"            ⚠ raw glob count; R728's census figure is a different quantity "
          f"(post-filter). Their relation is UNVERIFIED from this instrument.")

    # ---- CONFOUND written before the run: is class a pure function of era?
    der = sorted(r for r, d in per_round.items() if d["medium"] == "DERIVED")
    typ = sorted(r for r, d in per_round.items() if d["medium"] in ("TYPED", "DECLARED"))
    # ⛔ THE ARITHMETIC TRAP, CAUGHT IN MY OWN VERDICT STRING. Separability of two sets of round
    #    numbers is FORCED when either has one member -- a single point is separable from every
    #    set. So `era_pure` is only a measurement when BOTH sides have >= 2 members; below that it
    #    is 1+1=2, therefore 2<3, and printing True would be reporting the algebra as evidence.
    era_informative = len(der) >= 2 and len(typ) >= 2
    era_pure = (bool(der and typ and (min(der) > max(typ) or min(typ) > max(der)))
                if era_informative else None)
    print(f"\nCONFOUND  class vs era. DERIVED rounds {der}\n                        "
          f"TYPED/DECLARED rounds {typ}")
    if not era_informative:
        print(f"            UNINFORMATIVE: separability is FORCED at |DERIVED|={len(der)}, "
              f"|TYPED|={len(typ)}. Not a measurement -- a derivation. The confound is UNCONTROLLED.")
    else:
        print(f"            class is a pure function of era: {era_pure} -- "
              + ("so the finding is a DERIVATION about the calendar and is labelled one"
                 if era_pure else "the ranges interleave, so class is not the calendar"))

    # ---- DIRECTIONAL
    directional = bool(der) and (min(cited) in der or max(cited) in der) and len(set(der)) > 1
    print(f"DIRECTIONAL glob-derived rounds not confined to one era: {directional}")

    # ---- VERDICT : computed, never typed. Every control referenced in the branch.
    f_med = grid["medium|cited"]["f"]
    UNIT_OK = not unit_bad          # >1 source per round is the defect; 0 is a named category
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "UNIT": UNIT_OK}
    if not all(controls.values()) or f_med is None:
        world = "UNVERIFIED"
        why = "a control did not fire, or the population with an arm population is empty"
    elif f_med <= 0.25:
        world, why = "A", "the constant is a SCOPE; World B killed"
    elif f_med >= 0.60:
        world, why = "B", "the constant is a TIMESTAMP; World A killed"
    else:
        world, why = "C", "mixed -- one column cannot carry both"
    # ---- the shape none of the three worlds named. COMPUTED, so the sentence cannot be typed.
    src_derived = per_round.get(294, {}).get("medium") == "DERIVED"
    inheritors = sorted(r for r, d in per_round.items()
                        if r != 294 and d["medium"] in HAS_POP)
    n_no_pop = len(per_round) - len([r for r, d in per_round.items() if d["medium"] in HAS_POP])
    print(f"\nSHAPE     the constant's SOURCE round (R294) is DERIVED: {src_derived}")
    print(f"            cited rounds other than R294 with an arm population of their own: "
          f"{len(inheritors)} {inheritors}")
    print(f"            cited rounds with NO identifiable arm population at all: "
          f"{n_no_pop} of {len(per_round)} -- they inherit the constant without establishing it")

    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}   (f_medium = "
          + (f"{f_med:.4f})" if f_med is not None else "n/a)"))

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R743", "world": world, "why": why,
           "tree_sha": sha, "hashseed": os.environ.get("PYTHONHASHSEED"),
           "n_claim_rows": n_rows, "cited": cited, "n_cited": len(cited),
           "n_complement": len(complement), "unit_bad": unit_bad, "codeless_cited": no_code,
           "grid": grid, "per_round": {str(k): v for k, v in sorted(per_round.items())},
           "P1_n_cited": len(cited), "P2_f_medium_cited": f_med,
           "P3_globs_today": today, "P3_n_differing": n_diff,
           "P4_detector_agreement": p4,
           "directional": directional, "era_pure": era_pure, "era_informative": era_informative,
           "shape": {"source_R294_derived": src_derived, "inheritors_with_own_population": inheritors,
                     "cited_with_no_arm_population": n_no_pop, "n_cited_with_code": len(per_round)},
           "controls": controls, "positive_detail": pos,
           "placebo": {"n_readmes": len(readmes), "derived": pl_der, "mention_arms": pl_arm},
           "negative_detail": {"before": before, "after": after}}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r743.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r743.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
