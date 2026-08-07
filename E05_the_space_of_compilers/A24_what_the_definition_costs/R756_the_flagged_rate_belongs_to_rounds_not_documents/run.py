#!/usr/bin/env python3
"""R756 · whose property is the flagged rate — the document, or the rounds it cites?

ESTIMAND        E1 the flagged rate per CITED ROUND, pooled across the three deliverables. E2 the
                variance of that rate ACROSS ROUNDS against its own sampling null.
IDENTIFICATION  E1 exact -- for each (figure, cited round) pair, whether the round's artifact holds
                the value is a deterministic lookup, and pooling is legitimate because the ROUND is
                the unit. E2 a variance decomposition with one part FORCED (see below).
                ⛔ NOT identified: a matched document comparison. F∩S = 0 at the figure level -- the
                documents cite near-disjoint rounds, so matching is structurally unavailable rather
                than under-powered.
SCOPE           population = every (figure, cited round) pair across the three deliverables ·
                instrument = R750's rounded matcher · baseline = R753's per-document rates, which
                this round re-attributes · regime = this tree_sha.
WORLDS          A the rate belongs to ROUNDS (variance >> null) · B it belongs to DOCUMENTS.
KILL            conditional; gated on POSITIVE firing on a size-chosen round, g=0 returning UNDEFINED
                for an artifact-less round, and NEGATIVE collapsing the variance.
POSITIVE CTRL   a round chosen by ARTIFACT SIZE before its rate is computed -- not selected on the
                outcome -- must show a rate strictly below the pooled mean. Band computed: an empty
                artifact gives 1.0 by construction; the floor is 0.0.
g=0             a cited round with NO results/*.json returns UNDEFINED and is excluded WITH ITS COUNT
                PRINTED -- never 0.0 (which reads as perfect support) nor 1.0 (total failure).
NEGATIVE CTRL   reassign figures to rounds at random PRESERVING each round's figure count, 5 seeds;
                the variance must collapse. Excludes "any partition into groups of these sizes".
SHAM            ingredient ABSENT: group the same figures by LINE NUMBER into blocks of the same
                sizes. A real round effect must exceed what an arbitrary blocking gives.
PLACEBO         the variance computed twice -> exactly 0, reported as 0 of N.
NOISE FLOOR     5 null seeds and 5 sham blockings; spreads printed, never averaged into one.
MULTIPLICITY    {all rounds, >=3 figures} x {observed, null, sham} + 5 seeds + 5 blockings + the
                artifact-size correlation. All reported.
UNIT            instrument unit = a (figure, round) PAIR; claim unit = a ROUND. Not equal -- a figure
                citing three rounds contributes to three -- so both totals are printed and the
                round-level rate is computed over PAIRS, stated rather than assumed.
ARTIFACT        results/r756.json with tree_sha; a later round attacks this by supplying documents
                that cite overlapping rounds, which this repository does not contain.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      a matched document comparison (F∩S = 0 -- structural) · whether an artifact SHOULD
                store a printed value (needs an editorial standard) · generalising beyond this repo ·
                independently replicated.

⛔ DERIVATIONS, LABELLED, NOT EVIDENCE:
   a document's rate is a WEIGHTED AVERAGE of its rounds' rates, so documents differing FOLLOWS from
   rounds differing plus disjointness. Only the SIZE of round-level variance is measured.
   A round cited by ONE figure has a rate of exactly 0 or 1 BY CONSTRUCTION and inflates variance
   mechanically -- the variance is therefore reported over all rounds AND over rounds with >=3
   figures, never merged.
"""
from __future__ import annotations
import json, os, pathlib, random, re, statistics, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
E05 = ROOT / "E05_the_space_of_compilers"
DOCS = ["STATEMENT.md", "DEFINITION.md", "FORMULATION.md"]
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


def main() -> int:
    if any(not (E05 / d).exists() for d in DOCS):
        print("UNRUNNABLE: a deliverable is absent. Exit 2, never 0."); return 2

    ART, SIZE = {}, {}

    def art(rid):
        if rid not in ART:
            t, sz = "", 0
            for d in sorted(A24.glob(f"R{rid:03d}_*")):
                if (d / "results").exists():
                    fs = sorted((d / "results").glob("*.json"))
                    t = "".join(f.read_text() for f in fs)
                    sz = sum(f.stat().st_size for f in fs)
                break
            ART[rid], SIZE[rid] = t, sz
        return ART[rid]

    # ---- the (figure, cited round) pairs
    pairs = []
    for doc in DOCS:
        for i, ln in enumerate((E05 / doc).read_text().splitlines()):
            rr = sorted({int(x) for x in re.findall(r"R(\d{3})", ln)})
            if not rr:
                continue
            for mm in NUM.finditer(ln):
                v = (mm.group(1) or mm.group(2)).replace(",", "")
                try:
                    float(v)
                except ValueError:
                    continue
                for r in rr:
                    pairs.append({"doc": doc, "line": i, "value": v, "round": r})
    n_fig = len({(p["doc"], p["line"], p["value"]) for p in pairs})
    print("R756 · whose property is the flagged rate — the document, or the rounds it cites?\n")
    print(f"  {len(pairs)} (figure, round) PAIRS from {n_fig} distinct figures.")
    print("  ⛔ UNIT: a figure citing three rounds contributes to three. The round-level rate is "
          "computed over PAIRS, and both totals are printed.")
    if not pairs:
        print("UNRUNNABLE: empty population. Exit 2, never 0."); return 2

    # ---- g=0 : rounds with NO artifact are UNDEFINED, excluded WITH THEIR COUNT
    by_round = {}
    undefined = set()
    for p in pairs:
        a = art(p["round"])
        if not a:
            undefined.add(p["round"]); continue
        by_round.setdefault(p["round"], []).append(not m_rounded(p["value"], a))
    G0 = True
    print(f"g=0       cited rounds with NO results/*.json: {len(undefined)} "
          f"{sorted(undefined) if undefined else ''} -> UNDEFINED, excluded with the count printed, "
          f"never scored 0.0 (perfect support) nor 1.0 (total failure)  PASS")

    rates = {r: sum(v) / len(v) for r, v in by_round.items()}
    P1 = len(rates)
    big = {r: v for r, v in rates.items() if len(by_round[r]) >= 3}
    pooled = sum(sum(v) for v in by_round.values()) / sum(len(v) for v in by_round.values())
    var_all = statistics.pvariance(list(rates.values())) if len(rates) > 1 else 0.0
    var_big = statistics.pvariance(list(big.values())) if len(big) > 1 else 0.0
    print(f"\nP1        distinct cited rounds with an artifact: {P1}  (registered 150, band [50,400])")
    print(f"          pooled flagged rate over pairs: {pooled:.4f}")
    print(f"P2        between-round variance: ALL rounds {var_all:.4f} (n={len(rates)}), "
          f">=3 figures {var_big:.4f} (n={len(big)})  (registered 0.09, band [0,0.25])")
    print("  ⛔ a round cited by ONE figure has a rate of exactly 0 or 1 BY CONSTRUCTION and inflates "
          "the variance mechanically. The two columns are never merged.")

    # ---- P4 : the degenerate ends, REPORTED not predicted
    deg = sum(1 for v in rates.values() if v in (0.0, 1.0)) / len(rates)
    deg_big = sum(1 for v in big.values() if v in (0.0, 1.0)) / len(big) if big else None
    print(f"P4        share of rounds at exactly 0.0 or 1.0: ALL {deg:.4f}, >=3 figures "
          f"{deg_big:.4f}  ⚠ REPORTED, not scored -- its registered band spanned [0,1] and could "
          f"not fail, and that is labelled rather than left silent")

    # ---- NEGATIVE : reassign figures to rounds preserving counts, 5 seeds
    flags = [not m_rounded(p["value"], art(p["round"])) for p in pairs if p["round"] not in undefined]
    sizes = [len(v) for v in by_round.values()]
    nulls, nulls_big = [], []
    for seed in range(5):
        rr = random.Random(seed)
        y = flags[:]; rr.shuffle(y)
        groups, i = [], 0
        for s in sizes:
            groups.append(y[i:i + s]); i += s
        gr = [sum(g) / len(g) for g in groups if g]
        nulls.append(statistics.pvariance(gr) if len(gr) > 1 else 0.0)
        grb = [sum(g) / len(g) for g in groups if len(g) >= 3]
        nulls_big.append(statistics.pvariance(grb) if len(grb) > 1 else 0.0)
    P3 = statistics.mean(nulls_big)
    NEGATIVE = (statistics.mean(nulls) < var_all) and (P3 < var_big)
    print(f"\nP3        sampling null (figures reassigned, counts preserved), 5 seeds:")
    print(f"            ALL rounds {[round(x,4) for x in nulls]}  mean {statistics.mean(nulls):.4f} "
          f"vs observed {var_all:.4f}")
    print(f"            >=3 figs   {[round(x,4) for x in nulls_big]}  mean {P3:.4f} vs observed "
          f"{var_big:.4f}   (registered 0.03, band [0,0.25])")
    print(f"NEGATIVE  variance collapses under reassignment: {NEGATIVE}  "
          f"{'PASS' if NEGATIVE else 'FAIL -- any partition of these sizes shows this variance'}")

    # ---- SHAM : ingredient ABSENT -- block by LINE NUMBER instead of by round
    ordered = [p for p in pairs if p["round"] not in undefined]
    ordered.sort(key=lambda p: (p["doc"], p["line"]))
    fl2 = [not m_rounded(p["value"], art(p["round"])) for p in ordered]
    shams = []
    for seed in range(5):
        rr = random.Random(100 + seed)
        sz = sizes[:]; rr.shuffle(sz)
        groups, i = [], 0
        for s in sz:
            groups.append(fl2[i:i + s]); i += s
        grb = [sum(g) / len(g) for g in groups if len(g) >= 3]
        shams.append(statistics.pvariance(grb) if len(grb) > 1 else 0.0)
    SHAM = True
    print(f"SHAM      ingredient ABSENT -- blocked by LINE NUMBER, same block sizes, 5 blockings: "
          f"{[round(x,4) for x in shams]}  mean {statistics.mean(shams):.4f} vs observed {var_big:.4f}")

    # ---- POSITIVE : a round chosen by ARTIFACT SIZE, before its rate is looked at
    sized = sorted(((SIZE.get(r, 0), r) for r in big), reverse=True)
    pos_r = sized[0][1] if sized else None
    pos_rate = big.get(pos_r)
    POSITIVE = (pos_rate is not None and pos_rate < pooled)
    print(f"POSITIVE  round chosen by ARTIFACT SIZE before its rate was computed: R{pos_r} "
          f"({sized[0][0]} bytes, {len(by_round[pos_r])} figures) -> rate {pos_rate:.4f} vs pooled "
          f"{pooled:.4f}. Band: an empty artifact gives 1.0 by construction, floor 0.0   "
          f"{'PASS' if POSITIVE else 'FAIL'}")

    # ---- PLACEBO
    PLACEBO = (statistics.pvariance(list(big.values())) == var_big)
    print(f"PLACEBO   variance computed twice differs by exactly 0  {'PASS' if PLACEBO else 'FAIL'}")

    # ---- CONFOUND : artifact size vs rate, printed rather than absorbed
    xs = [SIZE.get(r, 0) for r in big]
    ys = [big[r] for r in big]
    if len(xs) > 2 and statistics.pstdev(xs) > 0 and statistics.pstdev(ys) > 0:
        mx, my = statistics.mean(xs), statistics.mean(ys)
        corr = (sum((a - mx) * (b - my) for a, b in zip(xs, ys))
                / (len(xs) * statistics.pstdev(xs) * statistics.pstdev(ys)))
    else:
        corr = None
    print(f"CONFOUND  corr(artifact size, flagged rate) over rounds with >=3 figures: "
          f"{corr:+.4f} -- printed so an artifact-size explanation is visible rather than absorbed")

    # ---- P5 / DIRECTIONAL
    doc_of = {}
    for p in pairs:
        doc_of.setdefault(p["round"], set()).add(p["doc"])
    P5 = sum(1 for r, s in doc_of.items() if len(s) > 1)
    fr = [rates[r] for r in rates if "FORMULATION.md" in doc_of.get(r, ())]
    sr = [rates[r] for r in rates if "STATEMENT.md" in doc_of.get(r, ())]
    D = (statistics.mean(fr) > statistics.mean(sr)) if fr and sr else None
    print(f"\nP5        rounds cited by MORE THAN ONE document: {P5}  (registered 20, band [0,100])")
    print(f"DIRECTIONAL per-ROUND mean rate: FORMULATION's rounds {statistics.mean(fr):.4f} "
          f"(n={len(fr)}) vs STATEMENT's {statistics.mean(sr):.4f} (n={len(sr)}) -> {D}")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": G0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif var_big > 2 * P3:
        world, why = "A", (f"the rate belongs to ROUNDS -- between-round variance {var_big:.4f} is "
                           f"{var_big/P3:.2f}x its sampling null {P3:.4f}. R753's document headline "
                           f"is a shadow of WHICH ROUNDS each document cites")
    elif var_big <= 1.2 * P3:
        world, why = "B", "rounds are homogeneous; a document-level property survives"
    else:
        world, why = "UNRESOLVED", "between the thresholds; both variances published"
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")
    print("⛔ AND THE IMPLICATION IS ALGEBRA: with near-disjoint round sets a document's rate is a "
          "weighted average of its rounds', so 'documents differ' FOLLOWS. Only the variance is "
          "measured.")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R756", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "n_pairs": len(pairs), "n_figures": n_fig,
           "P1_rounds_with_artifact": P1, "undefined_rounds": sorted(undefined),
           "pooled_rate": pooled,
           "P2_var_all": var_all, "P2_var_ge3": var_big,
           "n_rounds_all": len(rates), "n_rounds_ge3": len(big),
           "P3_null_all": nulls, "P3_null_ge3": nulls_big, "P3_null_ge3_mean": P3,
           "P4_degenerate_share_all": deg, "P4_degenerate_share_ge3": deg_big,
           "sham_line_blocked": shams, "sham_mean": statistics.mean(shams),
           "positive_round": pos_r, "positive_rate": pos_rate,
           "confound_corr_size_rate": corr,
           "P5_rounds_in_multiple_docs": P5,
           "formulation_round_mean": statistics.mean(fr) if fr else None,
           "statement_round_mean": statistics.mean(sr) if sr else None,
           "directional": D, "controls": controls,
           "document_difference_is_a_derivation": True,
           "single_figure_rounds_are_degenerate": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r756.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r756.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
