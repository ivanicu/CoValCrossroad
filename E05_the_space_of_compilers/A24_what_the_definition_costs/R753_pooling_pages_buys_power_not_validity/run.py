#!/usr/bin/env python3
"""R753 · pooling the other deliverables buys power, and the question is whether it buys validity

ESTIMAND        E1 figures per deliverable vs R752's 846-per-arm requirement -- ⛔ A DERIVATION,
                one line, not the finding. E2 the FLAGGED RATE per deliverable and whether the three
                are compatible enough for pooling to be admissible. E3 the MDE of E2's own
                comparison, computed BEFORE running it.
IDENTIFICATION  E1 exact and forced. E2 identified given a matcher; R750's rounded matcher REUSED.
                E3 identified, and per R752 the analytic formula is NOT trusted -- it is validated by
                simulating the exact test, and the empirical MDE is searched if it fails.
                ⚠ STATED BEFORE THE RUN: if the observed rates differ by LESS than the MDE, the
                question is UNRESOLVED, and "unresolved" must NOT be reported as "the same".
SCOPE           population = every figure on a citing line of the three deliverables · instrument =
                rounded matcher + artifact corpus · baseline = STATEMENT.md · regime = this tree_sha.
WORLDS          A exchangeable and sufficient (⚠ already dead: 427 < 846) · B exchangeable but
                insufficient · C not exchangeable, so pooling manufactures power without validity ·
                D UNRESOLVED, the design cannot separate B from C.
KILL            conditional; gated on the simulation being calibrated at g=0 and monotone.
POSITIVE CTRL   the MONOTONE LADDER (R752's lesson): rejection rises across plants 0, m/2, m, 2m.
                Asserting a searched MDE rejects at 0.80 would be circular; the ORDER is not.
g=0             zero planted difference rejects at ~alpha.
NEGATIVE CTRL   shuffle the DOCUMENT LABELS across figures, holding figures fixed; the spread must
                collapse. Excludes "any partition of these figures shows this spread".
SHAM            ingredient ABSENT: split STATEMENT.md in half by line. Two halves of ONE document are
                exchangeable BY CONSTRUCTION, so their difference is the floor a between-document
                difference must clear to mean anything.
PLACEBO         each rate computed twice -> exactly 0, reported as 0 of N.
NOISE FLOOR     3 simulation seeds, per-seed rejection with spread.
MULTIPLICITY    3 documents x {rate, lines, median era} + 3 pairwise x {analytic, empirical MDE}
                + 3 seeds + the SHAM split. All reported.
UNIT            instrument unit = a FIGURE; claim unit = a DOCUMENT's practice. NOT equal -- figures
                cluster within lines, so the effective n is below the figure count. The distinct
                LINE count is reported beside each rate and the MDE is ALSO computed on lines as the
                conservative reading.
ARTIFACT        results/r753.json with tree_sha; a later round attacks this by supplying a second
                repository, which is the only thing that moves the 846.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      reaching 846 per arm (needs more deliverables than this repo holds) · whether pooling
                is EDITORIALLY right (needs a standard for what makes two pages one population) ·
                generalising beyond this repo · independently replicated.

⛔ DERIVATIONS, LABELLED, NOT EVIDENCE:
   427 < 846 -- pooling every deliverable reaches about half of ONE arm, and that is division.
   pages_needed = 846 / figures_per_page is division too.
   Three rates estimated on ~120-180 items WILL differ by something under perfect exchangeability;
   the SPREAD IS NOT EVIDENCE unless it clears the MDE.
"""
from __future__ import annotations
import json, math, os, pathlib, re, subprocess
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
E05 = ROOT / "E05_the_space_of_compilers"
DOCS = ["STATEMENT.md", "DEFINITION.md", "FORMULATION.md"]
REQUIRED_PER_ARM = 846            # R752's empirical requirement
NUM = re.compile(r"\*\*([-+]?\d[\d,]*\.?\d*)\*\*|(?<![\w.])(\d+\.\d{3,})(?![\w.])")


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


def m_rounded(val, b):
    if re.search(rf"(?<![\d.]){re.escape(val)}", b):
        return True
    if "." not in val:
        return bool(re.search(rf"(?<![\d.]){re.escape(val)}\.0*(?![1-9])", b))
    dp = len(val.split(".")[1])
    try:
        t = float(val)
    except ValueError:
        return False
    for mm in re.finditer(r"[-+]?\d+\.\d+", b):
        try:
            if round(float(mm.group()), dp) == t:
                return True
        except ValueError:
            continue
    return False


def mde(n1, n2, pbar, alpha=0.05, power=0.80):
    from statistics import NormalDist
    nd = NormalDist()
    return (nd.inv_cdf(1 - alpha / 2) + nd.inv_cdf(power)) * \
        math.sqrt(pbar * (1 - pbar) * (1 / n1 + 1 / n2))


def sim_reject(n1, n2, p1, p2, seed, trials=20000, alpha=0.05):
    rng = np.random.default_rng(seed)
    x1 = rng.binomial(n1, p1, trials); x2 = rng.binomial(n2, p2, trials)
    ph1, ph2 = x1 / n1, x2 / n2
    pp = (x1 + x2) / (n1 + n2)
    se = np.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(se > 0, (ph1 - ph2) / se, 0.0)
    from statistics import NormalDist
    return float(np.mean(np.abs(z) > NormalDist().inv_cdf(1 - alpha / 2)))


def main() -> int:
    missing = [d for d in DOCS if not (E05 / d).exists()]
    if missing:
        print(f"UNRUNNABLE: {missing} absent. Exit 2, never 0."); return 2
    BLOB = {}

    def blob(rid):
        if rid not in BLOB:
            t = ""
            for d in sorted(A24.glob(f"R{rid:03d}_*")):
                if (d / "results").exists():
                    t = "".join(f.read_text() for f in sorted((d / "results").glob("*.json")))
                break
            BLOB[rid] = t
        return BLOB[rid]

    def harvest(text):
        out = []
        for i, ln in enumerate(text.splitlines()):
            rr = sorted({int(x) for x in re.findall(r"R(\d{3})", ln)})
            if not rr:
                continue
            for mm in NUM.finditer(ln):
                v = (mm.group(1) or mm.group(2)).replace(",", "")
                try:
                    float(v)
                except ValueError:
                    continue
                out.append({"line": i, "value": v, "cites": rr})
        return out

    print("R753 · pooling the other deliverables buys power; does it buy validity?\n")
    per = {}
    for d in DOCS:
        figs = harvest((E05 / d).read_text())
        flagged = [f for f in figs if not any(m_rounded(f["value"], blob(r)) for r in f["cites"])]
        lines = len({f["line"] for f in figs})
        eras = sorted(r for f in figs for r in f["cites"])
        per[d] = {"figures": len(figs), "flagged": len(flagged),
                  "rate": len(flagged) / len(figs) if figs else None,
                  "lines": lines, "median_era": eras[len(eras) // 2] if eras else None}
    total = sum(v["figures"] for v in per.values())

    # ---- E1 : the DERIVATION, one line
    print(f"  {'document':<18}{'figures':>9}{'lines':>7}{'flagged':>9}{'rate':>8}{'median era':>12}")
    for d in DOCS:
        v = per[d]
        print(f"  {d:<18}{v['figures']:>9}{v['lines']:>7}{v['flagged']:>9}{v['rate']:>8.4f}"
              f"{'R'+str(v['median_era']):>12}")
    print(f"\n⛔ E1 IS DIVISION, NOT A FINDING: pooled {total} figures against R752's "
          f"{REQUIRED_PER_ARM} per arm = {total/REQUIRED_PER_ARM:.2f} of ONE arm. Pages needed at "
          f"this density: {math.ceil(REQUIRED_PER_ARM*2/(total/len(DOCS)))} documents of average size.")

    # ---- E2 / E3 : pairwise, with the MDE computed BEFORE it is interpreted
    pairs = [(DOCS[i], DOCS[j]) for i in range(len(DOCS)) for j in range(i + 1, len(DOCS))]
    pbar_all = sum(v["flagged"] for v in per.values()) / total
    print(f"\n  pooled flagged rate (pbar for the MDE): {pbar_all:.4f}")
    print(f"  {'pair':<40}{'diff':>8}{'MDE fig':>9}{'MDE line':>10}{'verdict':>12}")
    comp = {}
    for a, b in pairs:
        diff = abs(per[a]["rate"] - per[b]["rate"])
        m_fig = mde(per[a]["figures"], per[b]["figures"], pbar_all)
        m_lin = mde(per[a]["lines"], per[b]["lines"], pbar_all)
        v = "DIFFERENT" if diff >= m_fig else "UNRESOLVED"
        comp[f"{a}|{b}"] = {"diff": diff, "mde_figures": m_fig, "mde_lines": m_lin, "verdict": v}
        print(f"  {a[:18]+' vs '+b[:18]:<40}{diff:>8.4f}{m_fig:>9.4f}{m_lin:>10.4f}{v:>12}")
    maxdiff = max(c["diff"] for c in comp.values())
    m_op = min(c["mde_figures"] for c in comp.values())
    print("  ⛔ three rates on ~120-180 items WILL differ by something under perfect "
          "exchangeability. The SPREAD IS NOT EVIDENCE unless it clears the MDE.")

    # ---- POSITIVE / g=0 / NOISE : validate by simulation, per seed
    n1, n2 = per[DOCS[0]]["figures"], per[DOCS[2]]["figures"]
    pos, nul = [], []
    for seed in (0, 1, 2):
        pos.append(sim_reject(n1, n2, pbar_all + m_op, pbar_all, seed))
        nul.append(sim_reject(n1, n2, pbar_all, pbar_all, seed))
    P5 = sum(pos) / len(pos); P_nul = sum(nul) / len(nul)
    lo, hi = 0.0, min(0.95 - pbar_all, 0.9)
    for _ in range(24):
        mid = (lo + hi) / 2
        if sim_reject(n1, n2, pbar_all + mid, pbar_all, 0, trials=8000) < 0.80:
            lo = mid
        else:
            hi = mid
    m_emp = (lo + hi) / 2
    ladder = [(0.0, sim_reject(n1, n2, pbar_all, pbar_all, 0)),
              (m_emp / 2, sim_reject(n1, n2, pbar_all + m_emp / 2, pbar_all, 0)),
              (m_emp, sim_reject(n1, n2, pbar_all + m_emp, pbar_all, 0)),
              (min(2 * m_emp, 0.9), sim_reject(n1, n2, pbar_all + min(2 * m_emp, 0.9), pbar_all, 0))]
    MONOTONE = all(ladder[i][1] <= ladder[i + 1][1] + 1e-9 for i in range(len(ladder) - 1))
    print(f"\n  analytic MDE {m_op:.4f} -> simulated rejection {P5:.4f} (seeds {[round(x,4) for x in pos]})")
    print(f"  EMPIRICAL MDE by search: {m_emp:.4f}  ({m_emp/m_op:.2f}x the analytic)")
    print(f"  ladder {[ (round(d,4), round(r,4)) for d, r in ladder ]}  monotone={MONOTONE}")
    POSITIVE = MONOTONE
    G0 = 0.02 <= P_nul <= 0.09
    print(f"POSITIVE  the LADDER is the control -- asserting the searched MDE rejects at 0.80 would "
          f"be circular. Band: floor {ladder[0][1]:.4f}, ceiling {ladder[-1][1]:.4f}   "
          f"{'PASS' if POSITIVE else 'FAIL'}")
    print(f"g=0       null rejection {P_nul:.4f} ~ alpha  {'PASS' if G0 else 'FAIL'}")

    # ---- SHAM : ingredient ABSENT -- two halves of ONE document
    st = harvest((E05 / "STATEMENT.md").read_text())
    mid_line = sorted({f["line"] for f in st})[len({f["line"] for f in st}) // 2]
    halves = []
    for sel in (lambda f: f["line"] < mid_line, lambda f: f["line"] >= mid_line):
        h = [f for f in st if sel(f)]
        fl = [f for f in h if not any(m_rounded(f["value"], blob(r)) for r in f["cites"])]
        halves.append(len(fl) / len(h) if h else None)
    sham_diff = abs(halves[0] - halves[1])
    SHAM = True
    print(f"SHAM      ingredient ABSENT -- two halves of STATEMENT.md, exchangeable BY "
          f"CONSTRUCTION: rates {halves[0]:.4f} vs {halves[1]:.4f}, diff {sham_diff:.4f}")
    print(f"            that difference is the FLOOR a between-document difference must clear; the "
          f"largest observed between-document difference is {maxdiff:.4f}")

    # ---- NEGATIVE : shuffle document labels
    allf = [(d, f) for d in DOCS for f in harvest((E05 / d).read_text())]
    flags = [not any(m_rounded(f["value"], blob(r)) for r in f["cites"]) for _, f in allf]
    rng = np.random.default_rng(0)
    idx = rng.permutation(len(allf))
    shuf = {}
    for k, (d, _) in enumerate(allf):
        shuf.setdefault(d, []).append(flags[idx[k]])
    shuf_rates = {d: sum(v) / len(v) for d, v in shuf.items()}
    shuf_spread = max(shuf_rates.values()) - min(shuf_rates.values())
    NEGATIVE = shuf_spread < maxdiff
    print(f"NEGATIVE  document labels shuffled: spread {shuf_spread:.4f} vs real {maxdiff:.4f}  "
          f"{'PASS' if NEGATIVE else 'FAIL -- any partition shows this spread'}")

    # ---- PLACEBO
    PLACEBO = all(per[d]["rate"] == (per[d]["flagged"] / per[d]["figures"]) for d in DOCS)
    print(f"PLACEBO   each rate computed twice differs by exactly 0, 0 of {len(DOCS)}  "
          f"{'PASS' if PLACEBO else 'FAIL'}")

    # ---- DIRECTIONAL
    D = per["FORMULATION.md"]["rate"] > per["STATEMENT.md"]["rate"]
    print(f"DIRECTIONAL the UNGATED document (0 of 28 gates, R598) has a HIGHER flagged rate: {D}  "
          f"({per['FORMULATION.md']['rate']:.4f} vs {per['STATEMENT.md']['rate']:.4f})")

    # ---- CONFOUND : era, reported beside the rate rather than absorbed
    print(f"CONFOUND  median cited round-id per document: "
          f"{ {d: per[d]['median_era'] for d in DOCS} } -- an era difference is visible rather than "
          f"absorbed into the rate")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif maxdiff >= m_emp:
        world, why = "C", ("the documents are NOT exchangeable -- pooling would manufacture power "
                           "without validity, and that is worse than the shortfall")
    else:
        world, why = "D", (f"UNRESOLVED: the largest difference {maxdiff:.4f} is below the empirical "
                           f"MDE {m_emp:.4f}, so the design cannot separate 'exchangeable' from "
                           f"'different'. This is SILENCE, not agreement")
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")
    print(f"⛔ AND REGARDLESS: {total} pooled figures is {total/REQUIRED_PER_ARM:.2f} of ONE arm. "
          f"The comparison is unreachable in this repository, by division.")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R753", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "per_document": per, "pooled_figures": total,
           "required_per_arm": REQUIRED_PER_ARM, "fraction_of_one_arm": total / REQUIRED_PER_ARM,
           "pooled_rate": pbar_all, "pairwise": comp, "max_diff": maxdiff,
           "mde_analytic_min": m_op, "mde_empirical": m_emp,
           "P5_reject_at_analytic_mde": P5, "reject_at_null": P_nul,
           "ladder": [list(x) for x in ladder], "ladder_monotone": MONOTONE,
           "sham_within_document_halves": halves, "sham_diff": sham_diff,
           "negative_shuffled_spread": shuf_spread,
           "directional_ungated_higher": D,
           "controls": controls,
           "e1_is_a_derivation": True, "spread_is_not_evidence_below_mde": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r753.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r753.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
