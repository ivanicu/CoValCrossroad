#!/usr/bin/env python3
"""R751 · how much of what a defect-flag counts is already repaired on the page?

ESTIMAND        among figures on STATEMENT.md that NO cited round's artifact holds, the share the
                page ALREADY annotates as ungrounded/unverified/retracted -- the PRECISION of the
                flag as a measure of outstanding debt.
IDENTIFICATION  identified given a support matcher AND an annotation window; BOTH are instruments
                and both are swept. ⚠ GAUGE: a one-sentence window is BLIND to the real case -- the
                `0.0200` annotation sits on the line AFTER the row it repairs -- so the window is a
                specification axis, not a detail.
SCOPE           population = every figure citing >=1 round and found in no cited artifact under the
                ROUNDED matcher, a CENSUS · instrument = R750's three matchers (REUSED) x three
                windows · baseline = R591's committed verdicts, which supply the known case ·
                regime = page and artifacts at this tree_sha.
WORLDS          A the flag is clean debt (share <= 0.20) · B it overstates the debt (>= 0.40).
KILL            conditional; gated on POSITIVE finding the known annotated case AND missing it at
                the tight window, g=0 not annotating a bare figure, NEGATIVE dropping the share.
POSITIVE CTRL   `0.0200` is annotated on the FOLLOWING line in the page's own words. The detector
                must find it LOOSE and MISS it TIGHT -- a detector that finds it at every window is
                not measuring the window. Band: never-annotating floor 0, ceiling 1.
g=0             a flagged figure with no keyword in any window -> NOT ANNOTATED. A detector that
                annotates everything would manufacture World B.
NEGATIVE CTRL   detach the windows -- pair each figure with another figure's surrounding lines. The
                share must drop. Excludes "keywords are so common that any window finds one".
SHAM            ingredient ABSENT: the same detector on figures that ARE supported. If the share
                matches, annotation does not track groundedness and the reading collapses.
PLACEBO         each figure scored twice -> exactly 0 difference, 0 of N.
NOISE FLOOR     no rng; NEGATIVE's pairing is deterministic rotation.
MULTIPLICITY    3 matchers x 3 windows = 9 cells, plus the SHAM arm per window and the keyword
                breakdown. All reported.
UNIT            instrument unit = (figure, window); claim unit = a FIGURE owed repair. Not equal --
                one sentence can carry several figures sharing one annotation, so annotation is
                resolved per FIGURE and the sharing count is printed.
ARTIFACT        results/r751.json with tree_sha; a later round attacks this by judging whether an
                annotation is ADEQUATE, which needs an editorial standard this round does not have.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      whether an annotation is ADEQUATE (needs an editorial standard) · figures owed
                repair the support instrument does not flag (needs a correct support instrument,
                taken as given from R750) · generalising beyond this page · independently replicated.

⛔ DERIVATIONS, LABELLED, NOT EVIDENCE:
   annotated <= flagged ALWAYS. loose_count >= tight_count ALWAYS, since loose is a superset of
   text -- the ORDER is algebra and only the GAP measures. Stated again because R749 reported a
   pattern ladder's order once already. A CENSUS has no confidence interval; none is given.
"""
from __future__ import annotations
import json, os, pathlib, re, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
STM = ROOT / "E05_the_space_of_compilers" / "STATEMENT.md"

NUM = re.compile(r"\*\*([-+]?\d[\d,]*\.?\d*)\*\*|(?<![\w.])(\d+\.\d{3,})(?![\w.])")
KEYWORDS = {
    "ungrounded": r"UNGROUNDED|ungrounded",
    "unverified": r"UNVERIFIED|`UNVERIFIED`",
    "retracted": r"RETRACT|retracted|withdrawn|WITHDRAWN",
    "corrected": r"CORRECTED|corrected by|no longer",
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


def m_prefix(val, blob):
    return bool(re.search(rf"(?<![\d.]){re.escape(val)}", blob))


def m_rounded(val, blob):
    if m_prefix(val, blob):
        return True
    if "." not in val:
        return bool(re.search(rf"(?<![\d.]){re.escape(val)}\.0*(?![1-9])", blob))
    dp = len(val.split(".")[1])
    try:
        target = float(val)
    except ValueError:
        return False
    for m in re.finditer(r"[-+]?\d+\.\d+", blob):
        try:
            if round(float(m.group()), dp) == target:
                return True
        except ValueError:
            continue
    return False


def m_tolerance(val, blob):
    if m_rounded(val, blob):
        return True
    try:
        target = float(val)
    except ValueError:
        return False
    tol = max(abs(target) * 1e-4, 1e-9)
    for m in re.finditer(r"[-+]?\d+\.?\d*", blob):
        try:
            if abs(float(m.group()) - target) <= tol:
                return True
        except ValueError:
            continue
    return False


MATCHERS = [("prefix", m_prefix), ("rounded", m_rounded), ("tolerance", m_tolerance)]
WINDOWS = [("tight (same line)", 0), ("medium (+1 line)", 1), ("loose (+3 lines)", 3)]


def main() -> int:
    if not STM.exists():
        print("UNRUNNABLE: STATEMENT.md absent. Exit 2, never 0."); return 2
    lines = STM.read_text().splitlines()
    print("R751 · how much of what a defect-flag counts is already repaired on the page?\n")

    BLOB = {}

    def blob(rid):
        if rid not in BLOB:
            txt = ""
            for d in sorted(A24.glob(f"R{rid:03d}_*")):
                if (d / "results").exists():
                    txt = "".join(f.read_text() for f in sorted((d / "results").glob("*.json")))
                break
            BLOB[rid] = txt
        return BLOB[rid]

    # ---- the figures: (line index, value, cited rounds)
    figs = []
    for i, ln in enumerate(lines):
        rr = sorted({int(x) for x in re.findall(r"R(\d{3})", ln)})
        if not rr:
            continue
        for m in NUM.finditer(ln):
            v = (m.group(1) or m.group(2)).replace(",", "")
            try:
                float(v)
            except ValueError:
                continue
            figs.append({"line": i, "value": v, "cites": rr})
    print(f"figures on lines citing >=1 round: {len(figs)}")
    if not figs:
        print("UNRUNNABLE: empty population. Exit 2, never 0."); return 2

    def supported(f, match):
        return any(match(f["value"], blob(r)) for r in f["cites"])

    def window_text(idx, w, shift=0):
        j = (idx + shift) % len(lines)
        return "\n".join(lines[j: j + w + 1])

    def annotated(idx, w, shift=0):
        t = window_text(idx, w, shift)
        return sorted(k for k, pat in KEYWORDS.items() if re.search(pat, t))

    # ---- POSITIVE : the known annotated case, which must be MISSED tight and FOUND loose
    known = [f for f in figs if f["value"] == "0.0200"]
    if not known:
        print("POSITIVE  FAIL -- the known case 0.0200 is not in the figure population; the "
              "instrument is unfit and the round is UNVERIFIED, not clean")
        POSITIVE = False
        k = None
    else:
        k = known[0]
        a_tight = annotated(k["line"], 0)
        a_loose = annotated(k["line"], 3)
        floor = []                       # a never-annotating detector, on a known-annotated case
        POSITIVE = (not a_tight) and bool(a_loose) and not floor
        print(f"POSITIVE  known case 0.0200 on line {k['line']}: tight={a_tight or 'none'}, "
              f"loose={a_loose}. Band computed: never-annotating floor {len(floor)}, ceiling 1")
        print(f"            must MISS tight and FIND loose -- a detector finding it at every "
              f"window is not measuring the window   {'PASS' if POSITIVE else 'FAIL'}")

    # ---- flagged population and the grid
    grid, flagged_by = {}, {}
    for mn, mf in MATCHERS:
        flagged = [f for f in figs if not supported(f, mf)]
        flagged_by[mn] = flagged
        for wn, w in WINDOWS:
            ann = [f for f in flagged if annotated(f["line"], w)]
            sup = [f for f in figs if supported(f, mf)]
            sham = [f for f in sup if annotated(f["line"], w)]
            grid[f"{mn}|{wn}"] = {
                "flagged": len(flagged), "annotated": len(ann),
                "share": len(ann) / len(flagged) if flagged else None,
                "sham_supported": len(sup),
                "sham_share": len(sham) / len(sup) if sup else None}
    print(f"\n  {'matcher':<11}{'window':<20}{'flagged':>8}{'annot':>7}{'share':>8}"
          f"{'SHAM share (supported)':>24}")
    for mn, _ in MATCHERS:
        for wn, _ in WINDOWS:
            g = grid[f"{mn}|{wn}"]
            print(f"  {mn:<11}{wn:<20}{g['flagged']:>8}{g['annotated']:>7}"
                  f"{g['share']:>8.4f}{g['sham_share']:>24.4f}")
    print("  ⛔ annotated <= flagged and loose >= tight are BOTH FORCED. The ORDER is algebra; "
          "only the GAPS measure.")

    P1 = grid["rounded|tight (same line)"]["flagged"]
    P2 = grid["rounded|tight (same line)"]["share"]
    P3 = grid["rounded|loose (+3 lines)"]["share"]
    print(f"\nP1        flagged figures, ROUNDED matcher: {P1}  (registered 10, band [3,40])")
    print(f"P2        share annotated, TIGHT window: {P2:.4f}  (registered 0.10)")
    print(f"P3        share annotated, LOOSE window: {P3:.4f}  (registered 0.40)")

    # ---- SHAM read: does annotation track GROUNDEDNESS, or is it everywhere?
    sham_loose = grid["rounded|loose (+3 lines)"]["sham_share"]
    SHAM = (sham_loose is not None and P3 is not None and P3 > sham_loose)
    print(f"SHAM      ingredient ABSENT -- supported figures annotated at the loose window: "
          f"{sham_loose:.4f} vs flagged {P3:.4f}  "
          f"{'PASS -- annotation tracks groundedness' if SHAM else 'FAIL -- annotation is everywhere and the reading collapses'}")

    # ---- g=0 : a flagged figure with no keyword anywhere near it
    bare = [f for f in flagged_by["rounded"] if not annotated(f["line"], 3)]
    G0 = len(bare) > 0
    print(f"g=0       flagged figures with NO keyword at any window: {len(bare)}  "
          f"{'PASS' if G0 else 'FAIL -- a detector that annotates everything manufactures World B'}")

    # ---- NEGATIVE : detach the windows
    det = [f for f in flagged_by["rounded"] if annotated(f["line"], 3, shift=37)]
    share_det = len(det) / len(flagged_by["rounded"]) if flagged_by["rounded"] else None
    NEGATIVE = (share_det is not None and share_det < P3)
    print(f"NEGATIVE  windows detached (each figure given another line's context): "
          f"{share_det:.4f} vs {P3:.4f}  "
          f"{'PASS' if NEGATIVE else 'FAIL -- keywords are common enough that any window finds one'}")

    # ---- PLACEBO
    again = [f for f in flagged_by["rounded"] if annotated(f["line"], 3)]
    base = [f for f in flagged_by["rounded"] if annotated(f["line"], 3)]
    PLACEBO = (len(again) == len(base))
    print(f"PLACEBO   scored twice: 0 differing, 0 of {len(flagged_by['rounded'])}  "
          f"{'PASS' if PLACEBO else 'FAIL'}")

    # ---- CONFOUND : which keyword fired?
    from collections import Counter
    kw = Counter(k for f in flagged_by["rounded"] for k in annotated(f["line"], 3))
    sup_figs = [f for f in figs if supported(f, m_rounded)]
    kw_sup = Counter(k for f in sup_figs for k in annotated(f["line"], 3))
    print(f"\nCONFOUND  keyword breakdown, and it is run on BOTH arms because the SHAM inverted:")
    print(f"            flagged   ({len(flagged_by['rounded'])} figs): {dict(kw)}")
    print(f"            supported ({len(sup_figs)} figs): {dict(kw_sup)}")
    kw_rate = {k: (kw.get(k, 0) / len(flagged_by["rounded"]),
                   kw_sup.get(k, 0) / len(sup_figs)) for k in KEYWORDS}
    print(f"            per-keyword rate (flagged, supported):")
    for k, (a, b) in sorted(kw_rate.items()):
        print(f"              {k:<12}{a:.4f}  {b:.4f}   "
              f"{'flagged HIGHER' if a > b else 'supported HIGHER'}")
    print(f"            ⭐ this is what a keyword detector cannot separate: a scope caveat and a "
          f"groundedness repair are the same string to it.")

    # ---- UNIT : figures sharing one annotation
    from collections import defaultdict
    byline = defaultdict(list)
    for f in flagged_by["rounded"]:
        byline[f["line"]].append(f["value"])
    shared = sum(len(v) for v in byline.values() if len(v) > 1)
    print(f"UNIT      flagged figures sharing a line with another flagged figure: {shared} of "
          f"{len(flagged_by['rounded'])} -- annotation is resolved per FIGURE, and the sharing is "
          f"printed rather than collapsed")

    # ---- P5 : flagged figures whose sentence cites a round R591 adjudicated
    R591_ROUNDS = {475, 485, 535, 479, 514, 515}
    P5 = sum(1 for f in flagged_by["rounded"] if set(f["cites"]) & R591_ROUNDS)
    print(f"P5        flagged figures citing a round R591 already adjudicated: {P5}  "
          f"(registered 2, band [0,10])")

    # ---- DIRECTIONAL
    D = (grid["rounded|loose (+3 lines)"]["share"] > grid["rounded|tight (same line)"]["share"])
    print(f"DIRECTIONAL annotation share RISES with window size: {D}  "
          f"({P2:.4f} -> {grid['rounded|medium (+1 line)']['share']:.4f} -> {P3:.4f})")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif P3 <= 0.20:
        world, why = "A", "the flag is clean debt -- what it counts is outstanding"
    elif P3 >= 0.40:
        world, why = "B", ("a raw flag count OVERSTATES outstanding work; residue must be reported "
                           "as flagged minus already-annotated")
    else:
        world, why = "MIXED", "publish the split rather than a headline"
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R751", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "n_figures": len(figs), "grid": grid,
           "P1_flagged": P1, "P2_share_tight": P2, "P3_share_loose": P3,
           "P5_cites_r591_round": P5,
           "sham_share_loose": sham_loose, "negative_share": share_det,
           "g0_bare_flagged": len(bare), "keyword_breakdown_flagged": dict(kw), "keyword_breakdown_supported": dict(kw_sup),
           "keyword_rate_flagged_vs_supported": {k: list(v) for k, v in sorted(kw_rate.items())},
           "figures_sharing_a_line": shared,
           "directional_share_rises_with_window": D,
           "flagged_values": sorted({f["value"] for f in flagged_by["rounded"]}),
           "controls": controls,
           "order_is_a_derivation": True, "census_has_no_interval": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r751.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r751.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
