#!/usr/bin/env python3
"""R786 · the rubric-affinity axis has ten points, not two — R785's n=2 was typed, not counted.

R785 reported "arms with criterion TEXT available: 2" from a hard-coded dict
`q782 = {"coval_core": 0.9978, "gen": 0.0396}`. A literal cannot return a different value, so that
population claim had no severity (D4). Enumerated from the object, 9 arms with a `core_*.json` carry
criteria that are NOT the rubric's, and `coval_core` makes 10.

ESTIMAND        E1 the ENUMERATED population and its rubric-derived partition · E2 affinity per
                non-rubric-derived arm with its own null · E3 the affinity-to-q_resolved relation,
                WITH and WITHOUT shams · E4 what survives for the definition
IDENTIFICATION  E3 only over arms carrying BOTH quantities; the intersection is COUNTED IN CODE and
                every arm missing either is listed, never silently dropped
DERIVED FIRST   D1 a rubric-derived arm has affinity 1.0 by construction -- used as the POSITIVE
                control, not reported as a result · D2 a sham sits at q_res 0.0000 by construction so
                including shams could manufacture the relation · D3 a correlation at single-digit n
                has an MDE near 0.9, printed BEFORE the number · D4 R785's n=2 was a literal
WORLDS          A tracks beyond the pair · B the pair was coincidence · C underpowered
CONTROLS        OBJECT · PLACEBO · POSITIVE (D1) · NULL · SHAM-SPLIT · A2-CHECK · SWEEP · MDE-first
"""
import collections
import itertools
import json
import math
import pathlib
import re
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls                 # noqa: E402

RES = ROOT / "corebench/results"
REL = ROOT / "data/conversation_rubrics.jsonl"
R782 = (ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
        / "R782_the_released_core_does_not_have_four_criteria/results/size_and_comparator.json")
ZEFF = 1.959964 + 0.841621
SEED = 31337
LENS = (3, 4, 5)
DERIVED_AT = 0.5          # verbatim overlap above this = rubric-derived, by construction

INSTRUMENT_UNIT = "a criterion-to-criterion comparison"
CLAIM_UNIT = "an arm"


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def toks(s, n):
    return set(re.findall(r"[a-z]{%d,}" % n, s.lower()))


def jac(a, b):
    if not a and not b:
        return 1.0
    u = len(a | b)
    return len(a & b) / u if u else 1.0


def affinity(C, F, n):
    if not C or not F:
        return float("nan")
    Ft = [toks(f, n) for f in F]
    return float(np.mean([max((jac(toks(c, n), ft) for ft in Ft), default=0.0) for c in C]))


def corr_mde(n):
    """D3: the MDE on Pearson r at z_eff, via Fisher z. Printed BEFORE any r."""
    return float(np.tanh(ZEFF / math.sqrt(n - 3))) if n > 3 else float("nan")


def main():
    out = {"instrument_unit": INSTRUMENT_UNIT, "claim_unit": CLAIM_UNIT}
    rng = np.random.default_rng(SEED)

    # ================= OBJECT CHECK -- exit 2, never 0 ============================================
    print("  OBJECT CHECK")
    if not R782.is_file():
        print("  UNRUNNABLE: R782's artifact is absent. Exit 2, never 0.")
        return 2
    q_res = {k: v["q_res"] for k, v in json.loads(R782.read_text())["e4"]["q"].items()}
    a2_of = {k: v["a2"] for k, v in json.loads(R782.read_text())["e4"]["q"].items()}
    full = json.loads((RES / "core_full.json").read_text())
    rub = {p: [str(x).strip() for x in v] for p, v in full.items()}
    rel = {}
    for line in open(REL, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        rel[tuple(sorted((it.get("criterion") or "").strip()
                         for it in (r.get("coval_full") or [])))] = \
            [(it.get("criterion") or "").strip() for it in (r.get("coval_core") or [])]
    print(f"     R782 artifact: q_resolved for {len(q_res)} arms   rubric prompts {len(rub)}   "
          f"release rubric keys {len(rel)}")
    if not q_res or not rub:
        print("  UNRUNNABLE: q_resolved or the rubric is empty. Exit 2, never 0.")
        return 2

    # ================= E1 · the ENUMERATED population (computed, never typed) ======================
    print("\n  E1 - ARMS WITH CRITERION TEXT, ENUMERATED FROM THE OBJECT")
    texts = {}
    for p in sorted(RES.glob("core_*.json")):
        t = p.stem[5:]
        if t == "full":
            continue
        try:
            d = json.loads(p.read_text())
        except Exception:
            continue
        if isinstance(d, dict) and len(set(d) & set(rub)) >= 100:
            texts[t] = {q: [str(x).strip() for x in d[q]] for q in d if q in rub}
    # `coval_core` has no core file (R782); its texts live in the release, keyed by rubric tuple
    cc = {}
    for p, F in rub.items():
        C = rel.get(tuple(sorted(F)))
        if C:
            cc[p] = C
    if cc:
        texts["coval_core"] = cc
    vb = {t: float(np.mean([len(set(v[q]) & set(rub[q])) / max(len(v[q]), 1) for q in v]))
          for t, v in texts.items()}
    derived = sorted(t for t in vb if vb[t] >= DERIVED_AT)
    notderived = sorted(t for t in vb if vb[t] < DERIVED_AT)
    print(f"     arms with criterion text: {len(texts)} (COUNTED in code)")
    print(f"     rubric-DERIVED (verbatim >= {DERIVED_AT}): {len(derived)}")
    print(f"     NOT rubric-derived: {len(notderived)} -> {notderived}")
    print(f"     ⛔ R785 reported this population as 2, from a hard-coded dict (D4)")
    out["e1"] = {"n_text": len(texts), "derived": derived, "not_derived": notderived,
                 "verbatim": vb}

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    ps = sorted(set(rub) & set(texts["gen"]))
    plac = float(np.mean([affinity(rub[p], rub[p], 4) for p in ps]))
    print(f"     PLACEBO    a rubric against itself: {plac:.6f}  "
          f"{'PASS' if abs(plac - 1.0) < 1e-12 else 'FAIL'}")
    posv = {}
    for t in derived[:6]:
        v = texts[t]
        q = sorted(set(v) & set(rub))
        posv[t] = float(np.mean([affinity(v[x], rub[x], 4) for x in q]))
    posok = all(abs(x - 1.0) < 1e-9 for x in posv.values())
    print(f"     POSITIVE   rubric-derived arms must return 1.0 (D1): "
          f"{ {k: round(x, 6) for k, x in posv.items()} }  {'PASS' if posok else 'FAIL'}")
    # NULL: cross-conversation, per arm
    print(f"     NULL       cross-conversation affinity, per arm, printed in E2")
    print(f"     MDE FIRST  (D3) correlation MDE by n: " +
          "  ".join(f"n={n}:{corr_mde(n):.3f}" for n in (5, 6, 7, 8, 10)))
    gate = abs(plac - 1.0) < 1e-12 and posok
    out["controls"] = {"placebo": plac, "positive": posv, "positive_ok": posok, "gate": gate,
                       "corr_mde": {str(n): corr_mde(n) for n in (5, 6, 7, 8, 10)}}

    # ================= E2 · affinity per non-derived arm ==========================================
    print("\n  E2 - RUBRIC AFFINITY FOR THE NON-RUBRIC-DERIVED ARMS")
    aff = {}
    print(f"     {'arm':<20}{'verbatim':>10}" + "".join(f"{'aff@'+str(n):>10}" for n in LENS) +
          f"{'null@4':>9}{'A2':>9}{'q_res':>9}")
    for t in notderived:
        v = texts[t]
        q = sorted(set(v) & set(rub))
        row = {}
        for n in LENS:
            row[n] = float(np.mean([affinity(v[x], rub[x], n) for x in q]))
        sh = list(q)
        rng.shuffle(sh)
        row["null"] = float(np.mean([affinity(v[q[i]], rub[sh[i]], 4) for i in range(len(q))]))
        aff[t] = row
        print(f"     {t:<20}{vb[t]:>10.4f}" + "".join(f"{row[n]:>10.4f}" for n in LENS) +
              f"{row['null']:>9.4f}"
              f"{a2_of.get(t, float('nan')):>9.4f}{q_res.get(t, float('nan')):>9.4f}")
    out["e2"] = aff

    # ================= E3 · the relation, WITH and WITHOUT shams ==================================
    print("\n  E3 - AFFINITY vs CLAUSE-② STANDING")
    both = [t for t in notderived if t in q_res]
    missing = [t for t in notderived if t not in q_res]
    shams = [t for t in both if t.endswith("_sham")]
    clean = [t for t in both if not t.endswith("_sham")]
    print(f"     arms with BOTH affinity and q_resolved: {len(both)} -> {both}")
    print(f"     arms with text but NO q_resolved (listed, not dropped silently): "
          f"{len(missing)} -> {missing}")
    print(f"     of those, SHAM arms: {len(shams)} -> {shams}")
    print(f"     sham-free population: {len(clean)} -> {clean}")
    rows = {}
    for label, pop in (("with shams", both), ("sham-free", clean)):
        for n in LENS:
            if len(pop) < 3:
                rows[f"{label}|{n}"] = {"n": len(pop), "r": None,
                                        "mde": corr_mde(len(pop)), "note": "n<3, undefined"}
                continue
            x = np.array([aff[t][n] for t in pop])
            y = np.array([q_res[t] for t in pop])
            r = float(np.corrcoef(x, y)[0, 1]) if x.std() > 0 and y.std() > 0 else float("nan")
            rows[f"{label}|{n}"] = {"n": len(pop), "r": r, "mde": corr_mde(len(pop))}
            print(f"     {label:<12} tok {n}   n {len(pop):>2}   r {r:+.4f}   "
                  f"MDE(D3) {corr_mde(len(pop)):.3f}   "
                  f"{'RESOLVES' if abs(r) >= corr_mde(len(pop)) else 'INSIDE the MDE'}")
    # A2-CHECK: is the ordering anything but the A2 ordering?
    for label, pop in (("with shams", both), ("sham-free", clean)):
        if len(pop) >= 3:
            x = np.array([aff[t][4] for t in pop])
            a = np.array([a2_of[t] for t in pop])
            y = np.array([q_res[t] for t in pop])
            print(f"     A2-CHECK {label:<12} corr(affinity, A2) "
                  f"{float(np.corrcoef(x, a)[0, 1]):+.4f}   corr(A2, q_res) "
                  f"{float(np.corrcoef(a, y)[0, 1]):+.4f}")
            rows[f"{label}|a2"] = {"aff_a2": float(np.corrcoef(x, a)[0, 1]),
                                   "a2_q": float(np.corrcoef(a, y)[0, 1])}
    out["e3"] = {"both": both, "missing_q": missing, "shams": shams, "clean": clean, "rows": rows}

    # ================= WORLD =======================================================================
    nclean = len(clean)
    rs = [rows[f"sham-free|{n}"]["r"] for n in LENS if rows[f"sham-free|{n}"]["r"] is not None]
    res = [abs(r) >= corr_mde(nclean) for r in rs] if rs and nclean > 3 else []
    if not gate:
        world = "UNVERIFIED - a control did not fire. Never OVERTURNED, never CONFIRMED."
    elif nclean < 5:
        world = (f"C - UNDERPOWERED, AS D3 PREDICTED: the sham-free population is {nclean}, where the "
                 f"correlation MDE is {corr_mde(nclean) if nclean > 3 else float('nan'):.3f}. **The "
                 f"round's product is the ENUMERATION** — {len(notderived)} non-rubric-derived arms "
                 f"with text where R785 typed 2 — and the hypothesis stays untestable here")
    elif res and all(res) and all(r > 0 for r in rs):
        world = (f"A - AFFINITY TRACKS CLAUSE ② BEYOND THE PAIR: sham-free n={nclean}, r="
                 f"{[round(r, 3) for r in rs]} against MDE {corr_mde(nclean):.3f}")
    else:
        world = (f"B - THE PAIR WAS COINCIDENCE: sham-free n={nclean}, r={[round(r, 3) for r in rs]} "
                 f"inside its MDE of {corr_mde(nclean):.3f}")
    print(f"\n  WORLD {world}")
    out["world"] = world
    out["tree_sha"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip()
    d = pathlib.Path(__file__).resolve().parent / "results"
    d.mkdir(exist_ok=True)
    (d / "affinity_axis.json").write_text(json.dumps(out, indent=2, default=_plain))
    print("  artifact -> affinity_axis.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
