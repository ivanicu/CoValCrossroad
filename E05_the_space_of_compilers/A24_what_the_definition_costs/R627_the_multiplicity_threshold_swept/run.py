#!/usr/bin/env python3
"""
R627 -- the multiplicity threshold, swept, against TWO positive classes because one is circular

CHECK #226 CAUGHT AN ERROR IN THE SELF-CRITICAL DIRECTION, AND A DESIGN FLAW IT WALKED PAST.
  ⛔ "the previous four rounds each picked one cell and three were reporting laxity" -- FALSE.
     R624 reported an explicit three-cell specification curve, R625 a three-band null over three
     seeds, R622 three tiers, R623 three causes. Tenth uncomputed quantifier in seventeen closing
     lines -- and the first to manufacture a fault rather than excuse one, which is the direction
     §4 says is not systematic. It now has a measured instance on each side.
  ⛔ AND THE REAL PROBLEM: "the gate-verified arm as the positive class" is CIRCULAR. T1 values are
     exactly the ones `definition_matches_the_record` re-derives -- they were selected BY the
     instrument whose coverage this rule would extend. A threshold tuned on them measures the
     gate's own taste. So the sweep runs against a SECOND positive class the gate never saw.

ESTIMAND        for each threshold m0 in 1..20, precision and recall of the rule "a decimal is
                anchored iff it is carried by >= m0 distinct rounds", against:
                  P1 GATE-VERIFIED  values derive() returns          -- CIRCULAR, reported as such
                  P2 HEADLINE       values appearing in a round's own README table, which the gate
                                    has never read                    -- independent of the gate
                  N  matched random draws, 3 seeds                    -- measured, non-circular
IDENTIFICATION  Exact per threshold. ⚠ P2 is not a gold standard either: a README table can carry
                a number the round did not measure. It is INDEPENDENT of the gate, which is the
                only property being claimed for it, and the agreement between P1 and P2 is what
                licenses reading either.
SCOPE           population : decimals on the two documents that match the corpus at 4 dp
                instrument : value -> set of rounds persisting it
                             instrument unit = A DECIMAL
                             claim unit      = A NUMERIC ASSERTION. Unchanged, still unequal.
                baseline   : R626 -- doc median 3, random 1, T1 14.5
                regime     : this repository at this sha
WORLDS          A THE CLASSES AGREE: P1 and P2 peak within a few of each other, so the threshold is
                  a property of the corpus rather than of the gate's taste, and it is usable.
                B CIRCULARITY DROVE IT: the two disagree materially. Then the T1 curve was
                  measuring which values the gate already knows, and no threshold is licensed.
KILL            pre-registered: |argmax_F1(P1) - argmax_F1(P2)| > 4 -> world B, no threshold is
                reported. Written before the run.
POSITIVE CTRL   at m0 = 1 recall must be 1.0 for both classes by construction -- if it is not, the
                positive sets are not subsets of the matched population and the sweep is void.
NEGATIVE CTRL   R621's fabricated value must fall BELOW whichever threshold is chosen; if a
                fabrication clears the bar the rule admits exactly what it exists to exclude.
PLACEBO         a threshold above the corpus maximum must give recall 0 and undefined precision,
                handled rather than crashed.
SEEDS           3 for the negative arm; the seed flag is verified to change the draws.
MULTIPLICITY    20 thresholds x 2 positive classes x 3 seeds. The WHOLE curve is reported.
ARTIFACT        results/multiplicity_threshold_curve.json
IMPOSSIBLE      neither positive class is a gold standard. P1 is the gate's own selection; P2 is a
                README's, which can name a number the round never measured. Their AGREEMENT is the
                evidence, not either curve alone -- and agreement between two proxies that share
                the corpus cannot rule out a bias in the corpus itself.
"""
from __future__ import annotations
import json, pathlib, random, re, statistics as st, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
A24 = E05 / "A24_what_the_definition_costs"
DEC = re.compile(r"(?<![\w.])(\d+\.\d{3,4})(?![\w])")


def build_map():
    m: dict[float, set] = {}
    for d in sorted(A24.glob("R[0-9]*")):
        mm = re.match(r"R(\d+)", d.name)
        if not mm: continue
        vals = []
        def walk(o):
            if isinstance(o, dict):
                for v in o.values(): walk(v)
            elif isinstance(o, (list, tuple)):
                for v in o: walk(v)
            elif isinstance(o, bool) or o is None: return
            elif isinstance(o, (int, float)): vals.append(float(o))
            elif isinstance(o, str):
                s = o.strip().lstrip("+-")
                if DEC.fullmatch(s):
                    try: vals.append(float(s))
                    except ValueError: pass
        for f in (d / "results").glob("*.json"):
            try: walk(json.loads(f.read_text(errors="ignore")))
            except Exception: pass
        for v in vals:
            for k in (round(v, 4), round(abs(v), 4)):
                m.setdefault(k, set()).add(mm.group(1))
    return m


def main():
    M = build_map()
    if len(M) < 1000:
        print(f"UNRUNNABLE: map has {len(M)} values. Exit 2, never 0."); return 2
    mult = lambda v: len(M.get(round(v, 4), ()))

    # P1 -- the gate's own selection. Circular, and labelled.
    sys.path.insert(0, str(ROOT / "assurance"))
    import definition_matches_the_record as DM
    P1 = sorted({round(float(v), 4) for _l, p in DM.derive().items()
                 if isinstance((v := p[0] if isinstance(p, tuple) else p), (int, float))
                 and not isinstance(v, bool) and round(float(v), 4) in M})
    # P2 -- decimals inside a round README's own tables. The gate has never read these files.
    p2 = set()
    for f in sorted(A24.glob("R*/README.md")):
        try: txt = f.read_text(errors="ignore")
        except Exception: continue
        for line in txt.split("\n"):
            if line.lstrip().startswith("|"):
                for d in DEC.findall(line):
                    if round(float(d), 4) in M: p2.add(round(float(d), 4))
    P2 = sorted(p2)
    print(f"  corpus values {len(M)}   P1 gate-verified {len(P1)}   P2 README-table {len(P2)}   "
          f"overlap {len(set(P1) & set(P2))}")
    if len(P2) < 50:
        print("UNRUNNABLE: P2 too small to sweep. Exit 2, never 0."); return 2

    NEG = []
    for seed in (0, 1, 2):
        rng = random.Random(seed)
        NEG.append([d for d in (round(rng.random(), 4) for _ in range(4000)) if d in M])
    seeds_differ = len({tuple(x[:20]) for x in NEG}) == 3

    def pr(P, m0):
        tp = sum(1 for v in P if mult(v) >= m0)
        fp = st.mean([sum(1 for v in N if mult(v) >= m0) for N in NEG])
        prec = tp / (tp + fp) if (tp + fp) else float("nan")
        rec = tp / len(P)
        f1 = 2 * prec * rec / (prec + rec) if prec == prec and (prec + rec) else 0.0
        return prec, rec, f1

    print(f"\n─── CONTROLS ───")
    r1 = all(abs(pr(P, 1)[1] - 1.0) < 1e-9 for P in (P1, P2))
    print(f"  POSITIVE  at m0=1 recall is 1.0 for both classes -> "
          f"{'PASS — the positive sets are subsets of the matched population' if r1 else '⛔ FAIL'}")
    print(f"  SEEDS     the seed flag changes the draws -> {'PASS' if seeds_differ else '⛔ FAIL'}")
    fake_m = mult(0.9187)
    print(f"  NEGATIVE  R621's fabricated 0.9187 has multiplicity {fake_m}")
    hi = max(mult(v) for v in P1) + 5
    p_hi, r_hi, _ = pr(P1, hi)
    print(f"  PLACEBO   a threshold above the corpus maximum (m0={hi}) -> recall {r_hi:.2f}, "
          f"precision {'undefined, handled' if p_hi != p_hi else f'{p_hi:.2f}'} -> "
          f"{'PASS' if r_hi == 0 else '⛔ FAIL'}")
    controls_ok = r1 and seeds_differ and r_hi == 0

    print(f"\n─── THE WHOLE CURVE ───")
    print(f"  {'m0':>3}   {'P1 prec':>8} {'P1 rec':>7} {'P1 F1':>6}   "
          f"{'P2 prec':>8} {'P2 rec':>7} {'P2 F1':>6}")
    curve = []
    for m0 in range(1, 21):
        a, b = pr(P1, m0), pr(P2, m0)
        curve.append({"m0": m0, "P1": [round(x, 4) for x in a], "P2": [round(x, 4) for x in b]})
        print(f"  {m0:>3}   {a[0]:>8.3f} {a[1]:>7.3f} {a[2]:>6.3f}   "
              f"{b[0]:>8.3f} {b[1]:>7.3f} {b[2]:>6.3f}")
    b1 = max(curve, key=lambda c: c["P1"][2])["m0"]
    b2 = max(curve, key=lambda c: c["P2"][2])["m0"]

    print(f"\n─── VERDICT (pre-registered: |argmaxF1(P1) - argmaxF1(P2)| > 4 -> world B) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif abs(b1 - b2) > 4:
        world = (f"B CIRCULARITY DROVE IT — the gate's own values peak at m0={b1} and the "
                 f"gate-blind README values at m0={b2}. The T1 curve was measuring which values "
                 f"the gate already knows; no threshold is licensed.")
    else:
        world = (f"A THE CLASSES AGREE — gate-verified peaks at m0={b1}, gate-blind README values "
                 f"at m0={b2}, |Δ|={abs(b1-b2)}. The threshold is a property of the corpus rather "
                 f"than of the gate's taste, and R621's fabricated value sits at multiplicity "
                 f"{fake_m}, {'BELOW' if fake_m < min(b1,b2) else 'NOT below'} it.")
    print(f"  {world}")
    print(f"\n  ⚠ NEITHER CLASS IS A GOLD STANDARD. P1 is the gate's own selection; P2 is a "
          f"README's, which can name a number its round never measured. Their AGREEMENT is the "
          f"evidence, and two proxies sharing one corpus cannot rule out a bias in the corpus.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "multiplicity_threshold_curve.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "n_P1": len(P1), "n_P2": len(P2),
        "overlap_P1_P2": len(set(P1) & set(P2)), "best_m0_P1": b1, "best_m0_P2": b2,
        "fabricated_value_multiplicity": fake_m, "curve": curve,
        "check226": ("'the previous four rounds each picked one cell' is false -- R624 reported a "
                     "three-cell curve and R625 a three-band null; and the line's positive class "
                     "was circular"),
        "impossible": "neither positive class is a gold standard; agreement is the evidence",
    }, indent=2))
    print(f"\n  wrote {OUT / 'multiplicity_threshold_curve.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
