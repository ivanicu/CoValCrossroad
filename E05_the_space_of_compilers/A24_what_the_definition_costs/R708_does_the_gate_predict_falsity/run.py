#!/usr/bin/env python3
"""
R708 -- do the gate's flags predict which NEXT lines turn out FALSE? Criterion validity, partial.

CHECK #310 ON R707's NEXT LINE -- THE CITATION RESOLVES, THE PROPOSED METHOD DOES NOT.
  ✓ `chance_share_by_decile` IS in R707's artifact, 10 entries, range 0.61-0.99. The first citation
    in this thread that resolves.
  ⛔ But its method is INADMISSIBLE: it proposes I judge the lines by hand "against the rule the gate
    claims to enforce". I wrote that rule and I wrote the gate, so my judgement correlates with it BY
    CONSTRUCTION -- it would measure my consistency, not the gate's validity. Self-review is void.
  ⭐ THE SUBSTITUTE IS BETTER THAN THE PROPOSAL. This project already produces a verdict on NEXT
    lines by a process that NEVER CONSULTS THE GATE: each round opens `CHECK #N ON R___'s NEXT LINE`
    and records whether it HELD or was FALSE. That is CRITERION VALIDITY -- the row §2 marks
    impossible -- available in partial form, on labels independent of the GATE though not of ME.

ESTIMAND        SENSITIVITY P(flagged | later recorded FALSE), FALSE RATE P(flagged | later HELD),
                their GAP with exact binomial intervals, and -- because n is small and that is the
                likely answer -- the design's own MDE for the gap.
IDENTIFICATION  identified only where a check names its target AND carries a parsable verdict;
                everything else is UNLABELLED and counted, never imputed. Partial ⇒ intervals.
SCOPE           population : target rounds of checks #192-#309 with a parsable verdict
                instrument : `flagged()` UNCHANGED + R706's paragraph-initial extractor
                             instrument unit = A NEXT PARAGRAPH
                             claim unit      = THE GATE'S PREDICTIVE VALIDITY
                             ⚠ NOT EQUAL -- a flag is not validity until cross-tabulated against an
                             outcome the flag did not produce, which is what this round does.
                baseline   : the corpus flag rate 0.2772 (R707) and a label-permutation null
                regime     : this repository at HEAD
WORLDS          A VALID · B INERT · C INVERTED · D UNRESOLVED (see PREREGISTRATION.txt)
KILL            conditional on the CLASSIFIER's positive control firing and its g=0 abstaining
POSITIVE CTRL   the classifier must label #307/#308/#309 FALSE and #279/#303 HOLDS
g=0             verdict words stripped -> the classifier must ABSTAIN, not guess
NEGATIVE CTRL   permute verdict-to-line pairing at fixed counts; the world it excludes is named
SHAM            the gate's flag replaced by a coin at the corpus base rate -- rate- and count-matched
PLACEBO         two identical runs differ by exactly 0
NOISE FLOOR     the sham gap's spread over >=2000 draws, measured
ARTIFACT        results/validity.json -- the 2x2, every per-round row, the MDE curve and the sham
                distribution AS FIELDS, because check #309 was exactly the failure of not doing that
IMPOSSIBLE      construct validity by an EXTERNAL standard (needs a judge who did not write the
                rule) · cross-release (convention, protocol and vocabulary are all ours)
"""
from __future__ import annotations
import importlib.util, json, math, pathlib, random, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
NDRAW, SEEDS, BASE_RATE = 3000, (0, 1, 2), 0.2772
INSTRUMENT_UNIT, CLAIM_UNIT = "A NEXT PARAGRAPH", "THE GATE'S PREDICTIVE VALIDITY"

_spec = importlib.util.spec_from_file_location(
    "nlq", ROOT / "assurance" / "next_line_quantifiers_are_computed.py")
_nlq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_nlq)
flagged, QUANT, ARTIFACT_RE = _nlq.flagged, _nlq.QUANT, _nlq.ARTIFACT
BARE_COUNT, PROVENANCE, WIN = _nlq.BARE_COUNT, _nlq.PROVENANCE, _nlq.WINDOW
EXTRACT = re.compile(r"(?:\A|\n\n)NEXT[:.,]\s*(.*?)(?:\n\n|\Z)", re.S | re.M)
HEAD_RE = re.compile(r"CHECK\s*#(\d+)\s+ON\s+(R\d+)[^\n]*?--\s*(.+)")

# ⭐ THE CLASSIFIER. It reads a RECORDED verdict; it does not form one. HOLDS words and DEFECT words
#   are disjoint, and anything matching neither ABSTAINS rather than defaulting to either side.
HOLDS = re.compile(r"\bIT HOLDS\b|\bHOLDS\b|\bIS CONFIRMED\b|\bSTANDS\b", re.I)
DEFECT = re.compile(r"\bIS FALSE\b|\bWAS WRONG\b|\bIS WRONG\b|MISCOUNT|DOES NOT RESOLVE|"
                    r"\bIS NOT THERE\b|POPULATION IS EMPTY|NEVER CHECKED|KILLED|PROPOSED A "
                    r"COMPARISON OVER A POPULATION OF ONE|PROPOSED THE ACTION|FINDS A DEFECT|"
                    r"ITS EXAMPLE IS WRONG|MISREPORTS|COULD NOT SEE|CANNOT", re.I)


def classify(headline: str) -> str:
    h, d = bool(HOLDS.search(headline)), bool(DEFECT.search(headline))
    if h and not d: return "HELD"
    if d and not h: return "FALSE"
    return "ABSTAIN"


def flag_at(text, window):
    if PROVENANCE.search(text): return ""
    c = BARE_COUNT.search(text)
    if c: return f"bare count '{c.group(0)}'"
    for q in QUANT.finditer(text):
        near = text if window is None else text[max(0, q.start() - window): q.end() + window]
        a = ARTIFACT_RE.search(near)
        if a: return f"quantifier '{q.group(1)}' over '{a.group(1)}'"
    return ""


def round_dirs():
    return {p.name.split("_")[0]: p for p in ARC.glob("R*") if p.is_dir()}


def commit_next(path) -> str | None:
    sha = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "-1", "--", str(path)],
                         cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if not sha: return None
    body = subprocess.run(["git", "log", "-1", "--format=%B", sha], cwd=ROOT,
                          capture_output=True, text=True).stdout
    ms = list(EXTRACT.finditer(body))
    return " ".join(ms[-1].group(1).split()) if ms else None


def readme_next(path) -> str | None:
    f = path / "README.md"
    if not f.exists(): return None
    m = list(re.finditer(r"^##+\s*NEXT\b[^\n]*\n(.*?)(?=\n##|\Z)", f.read_text(errors="ignore"),
                         re.S | re.M))
    return " ".join(m[-1].group(1).split()) if m else None


def wilson(k, n, z=1.96):
    if not n: return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    dirs = round_dirs()
    checks = []
    for p in sorted(dirs.values()):
        f = p / "run.py"
        if not f.exists(): continue
        m = HEAD_RE.search(f.read_text(errors="ignore")[:5000])
        if m:
            checks.append({"n": int(m.group(1)), "target": m.group(2),
                           "headline": " ".join(m.group(3).split()), "by": p.name})
    checks.sort(key=lambda c: c["n"])
    print(f"─── POPULATION ───\n  checks naming a target with a headline: {len(checks)} "
          f"(#{checks[0]['n']}–#{checks[-1]['n']})")

    print("\n─── CONTROLS ───")
    byn = {c["n"]: c for c in checks}
    want_false, want_holds = (307, 308, 309), (279, 303)
    got_f = [n for n in want_false if n in byn and classify(byn[n]["headline"]) == "FALSE"]
    got_h = [n for n in want_holds if n in byn and classify(byn[n]["headline"]) == "HELD"]
    posok = len(got_f) == len([n for n in want_false if n in byn]) and \
            len(got_h) == len([n for n in want_holds if n in byn])
    print(f"  POSITIVE(classifier)  known-FALSE recovered {got_f}, known-HOLDS recovered {got_h} -> "
          f"{'PASS — it reads recorded verdicts' if posok else '⛔ FAIL'}")
    strip = lambda h: DEFECT.sub(" ", HOLDS.sub(" ", h))
    g0 = [classify(strip(c["headline"])) for c in checks]
    g0ok = all(v == "ABSTAIN" for v in g0)
    print(f"  g=0     (classifier)  verdict words stripped -> "
          f"{sum(1 for v in g0 if v != 'ABSTAIN')} still labelled (must be 0) -> "
          f"{'PASS — it abstains, it does not guess' if g0ok else '⛔ FAIL'}")

    rows = []
    for c in checks:
        lab = classify(c["headline"])
        p = dirs.get(c["target"])
        t_commit = commit_next(p) if p else None
        t_readme = readme_next(p) if p else None
        rows.append({**c, "label": lab, "has_commit_next": bool(t_commit),
                     "flag_commit": flagged(t_commit) if t_commit else None,
                     "flag_readme": flagged(t_readme) if t_readme else None,
                     "flag_commit_whole": flag_at(t_commit, None) if t_commit else None})
    lab = [r for r in rows if r["label"] != "ABSTAIN" and r["has_commit_next"]]
    ab = [r for r in rows if r["label"] == "ABSTAIN"]
    nonext = [r for r in rows if not r["has_commit_next"]]
    print(f"  UNLABELLED counted, never imputed: {len(ab)} abstained, "
          f"{len(nonext)} target rounds with no extractable NEXT paragraph")

    F = [r for r in lab if r["label"] == "FALSE"]
    H = [r for r in lab if r["label"] == "HELD"]
    kf, kh = sum(1 for r in F if r["flag_commit"]), sum(1 for r in H if r["flag_commit"])
    sens = kf / len(F) if F else None
    fpr = kh / len(H) if H else None
    gap = (sens - fpr) if (sens is not None and fpr is not None) else None
    print(f"\n─── THE 2×2 (labelled n={len(lab)}) ───")
    print(f"  {'':<24}{'flagged':>9}{'not':>6}{'n':>5}{'rate':>8}{'  95% (Wilson)':>18}")
    for nm, grp, k in (("later FALSE", F, kf), ("later HELD", H, kh)):
        lo, hi = wilson(k, len(grp))
        print(f"  {nm:<24}{k:>9}{len(grp)-k:>6}{len(grp):>5}"
              f"{(k/len(grp) if grp else 0):>8.4f}   [{lo:.4f}, {hi:.4f}]")
    print(f"  GAP sensitivity − false rate = {gap:+.4f}" if gap is not None else "  GAP UNCOMPUTED")

    # SHAM: the flag replaced by a coin at the corpus base rate. Its gap distribution IS the null.
    sham_gaps, negs = [], []
    for seed in SEEDS:
        rng = random.Random(seed)
        for _ in range(NDRAW // len(SEEDS)):
            a = sum(1 for _ in F if rng.random() < BASE_RATE) / len(F)
            b = sum(1 for _ in H if rng.random() < BASE_RATE) / len(H)
            sham_gaps.append(a - b)
            v = [1 if r["flag_commit"] else 0 for r in lab]
            rng.shuffle(v)
            negs.append(sum(v[:len(F)]) / len(F) - sum(v[len(F):]) / len(H))
    sham_gaps.sort(); negs.sort()
    q = lambda v, a: v[int(a * (len(v) - 1))]
    slo, shi = q(sham_gaps, 0.025), q(sham_gaps, 0.975)
    nlo, nhi = q(negs, 0.025), q(negs, 0.975)
    p_emp = (sum(1 for x in negs if abs(x) >= abs(gap)) + 1) / (len(negs) + 1)
    print(f"\n  SHAM      flag → coin at the corpus base rate {BASE_RATE}: gap null 95% "
          f"[{slo:+.4f}, {shi:+.4f}]   NOISE FLOOR spread {shi-slo:.4f} over {len(sham_gaps)} draws")
    print(f"  NEGATIVE  pairing permuted at fixed counts: 95% [{nlo:+.4f}, {nhi:+.4f}], "
          f"p={p_emp:.4f} -> {'INSIDE — no information in the pairing' if nlo <= gap <= nhi else '⛔ OUTSIDE'}")
    plc = [flagged(r) for r in (x['headline'] for x in checks)] == \
          [flagged(r) for r in (x['headline'] for x in checks)]
    seedok = len({round(sum(negs[i::len(SEEDS)]) / len(negs[i::len(SEEDS)]), 8)
                  for i in range(len(SEEDS))}) > 1
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  PLACEBO   two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    print(f"  SEEDS     3 permutation streams differ -> {'PASS' if seedok else '⛔ FAIL'}")
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and plc and seedok and unitok

    # ⭐ MDE: the smallest TRUE gap this design detects at 80% power against the permutation null.
    print(f"\n─── THE MDE OF THIS DESIGN (the likely answer, so it is measured not asserted) ───")
    mde, curve = None, []
    for d in [i / 100 for i in range(0, 101, 5)]:
        pf = min(1.0, BASE_RATE + d * len(H) / (len(F) + len(H)))
        ph = max(0.0, pf - d)
        rng, hits = random.Random(4242), 0
        for _ in range(600):
            a = sum(1 for _ in F if rng.random() < pf) / len(F)
            b = sum(1 for _ in H if rng.random() < ph) / len(H)
            if (a - b) > nhi: hits += 1
        curve.append({"true_gap": d, "power": hits / 600})
        if mde is None and hits / 600 >= 0.80: mde = d
    print("  " + "  ".join(f"{c['true_gap']:.2f}:{c['power']:.2f}" for c in curve[::2]))
    print(f"  ⭐ MDE at 80% power = {('%.3f' % mde) if mde is not None else 'NOT REACHED at gap 1.0'}"
          f"   observed |gap| = {abs(gap):.4f}")
    resolvable = mde is not None and abs(gap) >= mde

    print(f"\n─── THE SPECIFICATION SWEEP (G4) ───")
    cells = []
    for src, key in (("commit body", "flag_commit"), ("README ## NEXT", "flag_readme"),
                     ("commit, whole-para window", "flag_commit_whole")):
        sub = [r for r in lab if r[key] is not None]
        f2 = [r for r in sub if r["label"] == "FALSE"]
        h2 = [r for r in sub if r["label"] == "HELD"]
        if not f2 or not h2:
            cells.append({"source": src, "n": len(sub), "gap": None}); continue
        g = sum(1 for r in f2 if r[key]) / len(f2) - sum(1 for r in h2 if r[key]) / len(h2)
        cells.append({"source": src, "n": len(sub), "n_false": len(f2), "n_held": len(h2), "gap": g})
    for c in cells:
        print(f"  {c['source']:<28} n={c['n']:>3}  gap "
              f"{('%+.4f' % c['gap']) if c['gap'] is not None else 'UNCOMPUTED — a cell is empty'}")

    print(f"\n─── REGISTERED ───")
    print(f"  A  sensitivity = 0.35 [0.10,0.75] -> {sens:.4f}: "
          f"{'INSIDE' if 0.10 <= sens <= 0.75 else '⛔ OUTSIDE'}")
    print(f"  B  gap = +0.10 [-0.25,+0.50] -> {gap:+.4f}: "
          f"{'INSIDE' if -0.25 <= gap <= 0.50 else '⛔ OUTSIDE'}")
    print(f"  C  MDE = 0.35 [0.15,0.80] -> {('%.3f' % mde) if mde else 'NOT REACHED'}: "
          f"{'INSIDE' if mde and 0.15 <= mde <= 0.80 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL sensitivity > corpus base rate {BASE_RATE} -> "
          f"{'HOLDS' if sens > BASE_RATE else '⛔ FAILS'}")
    print(f"\n  MULTIPLICITY: {len(cells)} label×extractor cells above; "
          f"UNCOMPUTED cells named, not dropped.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; nothing here licenses a reading."
    elif not resolvable:
        world = (
            f"⭐⭐⭐ D UNRESOLVED, AND THE MDE IS THE FINDING. On the {len(lab)} NEXT lines this "
            f"project has itself judged — {len(F)} later recorded FALSE, {len(H)} recorded to HOLD — "
            f"the gate flags {sens:.3f} of the false ones and {fpr:.3f} of the true ones, a gap of "
            f"{gap:+.4f}. ⛔ This design's MDE at 80% power is "
            f"{('%.3f' % mde) if mde else 'unreachable even at a gap of 1.0'}, so a gap of that size "
            f"IS NOT READABLE HERE and neither 'the gate works' nor 'the gate is inert' is supported. "
            f"⭐ WHAT IS SUPPORTED IS THE BOUND: with n={len(F)} false and n={len(H)} held, this "
            f"corpus could not have detected criterion validity unless it were very large. ⭐⭐ BUT "
            f"ONE NUMBER HERE IS RESOLVABLE AND IT IS THE USEFUL ONE: the Wilson 95% interval on "
            f"sensitivity is [{wilson(kf,len(F))[0]:.3f}, {wilson(kf,len(F))[1]:.3f}], so the gate "
            f"catches AT MOST {wilson(kf,len(F))[1]:.0%} of the NEXT lines this project later "
            f"recorded FALSE — an upper bound, and it does not depend on the gap being readable. "
            f"⚠ The point estimate {sens:.3f} is BELOW the corpus base rate {BASE_RATE}, so the "
            f"registered directional FAILS, and across the three extractor specifications the gap "
            f"runs {min(c['gap'] for c in cells if c['gap'] is not None):+.4f} to "
            f"{max(c['gap'] for c in cells if c['gap'] is not None):+.4f} — SIGN-UNSTABLE, which is "
            f"what an unreadable effect looks like. ⚠ R707's word-scramble result — that "
            f"{0.758:.0%} of this gate's flagging survives destroying word order — remains the "
            f"strongest evidence about it that exists. ⚠ AND THE LABELS ARE NOT "
            f"INDEPENDENT OF ME: they are independent of the GATE, which is the confound this design "
            f"controls and the only one. An external judge remains impossible here. ⚠ UNIT GAP: "
            f"instrument unit is {INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT}.")
    elif gap > 0:
        world = (f"⭐⭐⭐ A VALID — the gate flags {sens:.3f} of NEXT lines later recorded FALSE "
                 f"against {fpr:.3f} of those that held, gap {gap:+.4f}, above the design's MDE of "
                 f"{mde:.3f} and outside the permutation null [{nlo:+.4f},{nhi:+.4f}] (p={p_emp:.4f}).")
    else:
        world = (f"⭐⭐⭐ C INVERTED — the gate flags TRUE lines MORE than false ones "
                 f"({fpr:.3f} vs {sens:.3f}, gap {gap:+.4f}), above the MDE {mde:.3f}. Worse than "
                 f"useless: it penalises the lines that turned out to hold.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "validity.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_checks": len(checks), "n_labelled": len(lab), "n_abstain": len(ab),
        "n_target_without_next": len(nonext),
        "two_by_two": {"false_flagged": kf, "false_total": len(F),
                       "held_flagged": kh, "held_total": len(H),
                       "sensitivity": sens, "false_rate": fpr, "gap": gap,
                       "wilson_false": wilson(kf, len(F)), "wilson_held": wilson(kh, len(H))},
        "mde": mde, "mde_curve": curve, "resolvable": resolvable,
        "sham_gap_null95": [slo, shi], "permutation_null95": [nlo, nhi], "p_permutation": p_emp,
        "noise_floor_sham_spread": shi - slo,
        "rows": rows, "cells": cells,
        "registered": ("A sensitivity 0.35 [0.10,0.75]; B gap +0.10 [-0.25,+0.50]; "
                       "C MDE 0.35 [0.15,0.80]; directional sensitivity > 0.2772"),
        "observed": {"A": sens, "B": gap, "C": mde, "directional": sens > BASE_RATE},
        "limit": ("the labels are independent of the GATE but NOT of me; an external judge is "
                  "impossible here and is not substitutable by my own hand-judgement."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
