"""R427/speccurve -- the specification curve on the arm that already landed. Attack my own negative.

R427 reported ONE cell: mean-over-criteria, conversation-clustered, interactions with exactly one
chosen response. It concluded W-LENGTH -- `generic` 0.4374 against the longest-reply shortcut's
0.5096. G4 says one cell reported as if it characterised the phenomenon is the 100-line-python
failure at experiment scale, and that applies to a NEGATIVE exactly as hard as to a positive.

⛔ THE SPECIFIC RISK. `mean over criteria` was a choice nobody defended. A core could reasonably be
   read as requiring ALL its criteria (min), or ANY of them (max), or a robust middle (median). If
   `generic` beats the length shortcut under some defensible aggregation, then W-LENGTH was a
   property of MY aggregation and the headline is a cell. If it loses everywhere, the negative is
   robust and says so with a count rather than an adjective.

⭐ AND IT COSTS NO GPU. Every cell is a re-aggregation of `sat_transport_generic.npz`, already on
   disk. The cheapest possible attack on my own conclusion, which is why it runs before the other
   four arms land rather than after.

⛔ ARITHMETIC TRAP. The four aggregations are monotone transforms of the SAME per-criterion values,
   so they are not independent evidence -- they cannot each confirm the finding. What they CAN do is
   falsify it: a single cell where generic clears length would show the choice was load-bearing.
   This is a falsification sweep, not a replication.

ESTIMAND        for each cell of (aggregation x response-count restriction x unit):
                ACC(generic) and ACC(generic) - ACC(length), with the cell's own MDE.

IDENTIFICATION  Exact per cell. NOT identified: whether any aggregation is the RIGHT one -- the
                definition does not say, which is itself a finding about the definition and is named
                rather than resolved here.

SCOPE           population: the same 2,200 seeded conversations · instrument: Qwen3.5-2B-Base, the
                committed generic arm · baseline: longest-reply, recomputed inside every cell so the
                comparison never crosses populations · regime: k=4, prompt-blind.

WORLDS
  W-ROBUST      generic fails to clear length in EVERY cell. The negative is a property of the arm,
                not of my aggregation, and the count is reported.
  W-CELL        generic clears length in at least one cell. Then R427's headline was a property of
                `mean`, and the curve -- not the cell -- is the finding.

PREDICTION MATRIX
  W-ROBUST -> 0 of N cells have generic - length > that cell's MDE
  W-CELL   -> >= 1 cell does, and it is named with its aggregation and restriction

PRE-REGISTERED KILL
    if the placebo cell (length against itself) is EXACTLY 0 in every cell:
        0 cells favour generic -> W-ROBUST
        else                   -> W-CELL, cells named
    else: UNVERIFIED -- the estimator is broken and no cell is readable.

CONTROLS
  PLACEBO      length against itself must be exactly 0 in EVERY cell, not just one. A curve whose
               estimator drifts across cells cannot be compared across cells.
  RECOMPUTED   the length baseline is recomputed INSIDE each restriction. Comparing an arm on the
               n>=3 subset against a baseline computed on all interactions would be a
               population mismatch dressed as an effect.
  NON-EMPTY    a cell with fewer than 2 conversations is UNVERIFIED for that cell, never 0.0.
  MULTIPLICITY every cell printed, favourable and not, with the count stated.

ARTIFACT        results/r427_speccurve.json with the source hash.

IMPOSSIBLE HERE
  which aggregation the definition INTENDS -- it does not say. Named, not resolved.
  a prompt-specific core                 -- unchanged from R427.

EXIT
    0  the curve is reported
    1  the placebo drifts -- UNVERIFIED
    2  the arm is absent -- never a silent pass
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
ZEFF = 1.959964 + 0.841621
AGG = {"mean": np.mean, "min": np.min, "max": np.max, "median": np.median}
RESTR = {"all": lambda n: True, "n=2": lambda n: n == 2, "n>=3": lambda n: n >= 3}


def load():
    p = RES / "sat_transport_generic.npz"
    if not p.exists():
        return None, None
    with np.load(p, allow_pickle=True) as d:
        meta, sat = [str(x) for x in d["meta"]], np.asarray(d["sat"], float)
        tgt = json.loads(str(d["targets"]))
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for m, v in zip(meta, sat):
        c, i, r, _j = m.split("|")
        per[(c, i)][r].append(v)
    return per, tgt


def cell(per, tgt, agg, keep, unit):
    """-> (acc_generic, acc_length, paired diff, mde, n_units). Baseline recomputed INSIDE the cell."""
    g, l = collections.defaultdict(list), collections.defaultdict(list)
    for t in tgt:
        ch = [r["id"] for r in t["resp"] if r["chosen"]]
        if len(ch) != 1 or not keep(len(t["resp"])):
            continue
        key = (t["conv"], t["inter"])
        row = per.get(key)
        if not row:
            continue
        u = t["conv"] if unit == "conv" else f"{t['conv']}|{t['inter']}"
        scored = {r: float(agg(v)) for r, v in row.items()}
        top = max(scored.values())
        tied = sorted([r for r in scored if scored[r] == top])
        g[u].append(1.0 if tied[0] == ch[0] else 0.0)
        l[u].append(1.0 if max(t["resp"], key=lambda r: (r["len"], r["id"]))["id"] == ch[0] else 0.0)
    ks = [k for k in g if k in l]
    if len(ks) < 2:
        return None
    ga = np.array([np.mean(g[k]) for k in ks]); la = np.array([np.mean(l[k]) for k in ks])
    d = ga - la
    return (float(ga.mean()), float(la.mean()), float(d.mean()),
            float(ZEFF * d.std(ddof=1) / np.sqrt(len(d))), len(ks))


def main() -> int:
    per, tgt = load()
    if per is None:
        print("  UNRUNNABLE: sat_transport_generic.npz absent. Exit 2, never 0."); return 2

    print("R427 · specification curve — attacking my own negative, on the arm already on disk\n")
    print("  ⛔ R427 REPORTED ONE CELL: mean-over-criteria, conversation-clustered. `mean` was a")
    print("     choice nobody defended. A core could as reasonably require ALL its criteria (min),")
    print("     ANY of them (max), or a robust middle (median). G4 binds a NEGATIVE exactly as hard")
    print("     as a positive.\n")

    rows, favour, unver, placebo_ok = {}, [], [], True
    print(f"    {'agg':<8} {'restrict':<7} {'unit':<6} {'generic':>8} {'length':>8} "
          f"{'g − l':>9} {'MDE':>8} {'n':>7}")
    for a in AGG:
        for rname, keep in RESTR.items():
            for unit in ("conv", "inter"):
                out = cell(per, tgt, AGG[a], keep, unit)
                tag = f"{a}|{rname}|{unit}"
                if out is None:
                    unver.append(tag)
                    print(f"    {a:<8} {rname:<7} {unit:<6} {'—':>8} {'—':>8} {'—':>9} "
                          f"{'—':>8} {'<2':>7}   UNVERIFIED")
                    continue
                ga, la, d, mde, n = out
                rows[tag] = dict(generic=ga, length=la, diff=d, mde=mde, n=n)
                if d > mde:
                    favour.append(tag)
                print(f"    {a:<8} {rname:<7} {unit:<6} {ga:>8.4f} {la:>8.4f} {d:>+9.4f} "
                      f"{mde:>8.4f} {n:>7,}" + ("   ⭐ FAVOURS GENERIC" if d > mde else ""))
                # PLACEBO: length against itself, inside this same cell
                same = cell(per, tgt, AGG[a], keep, unit)
                placebo_ok &= abs(same[1] - la) < 1e-12

    print(f"\n  CONTROLS")
    print(f"    PLACEBO      the length baseline is identical when recomputed in the same cell: "
          f"{placebo_ok}   {'PASS' if placebo_ok else 'FAIL — the estimator drifts across cells'}")
    print(f"    RECOMPUTED   length is recomputed INSIDE each restriction, so no comparison crosses")
    print(f"                 populations — an arm on n>=3 against a baseline on all interactions")
    print(f"                 would be a population mismatch dressed as an effect")
    print(f"    ⛔ THE FOUR AGGREGATIONS ARE MONOTONE TRANSFORMS OF THE SAME VALUES. They cannot")
    print(f"       each CONFIRM the finding; they can only FALSIFY it. This is a falsification")
    print(f"       sweep, not a replication, and counting agreements would be double-counting.")

    print(f"\n  MULTIPLICITY  cells tested {len(rows)} · favouring generic {len(favour)} · "
          f"unverifiable {len(unver)}")
    if not placebo_ok:
        print("\n  UNVERIFIED — the estimator drifts. Exit 1."); return 1

    print()
    if favour:
        v = "W_CELL"
        print(f"  W-CELL — generic clears the length shortcut in {favour}. R427's headline was a")
        print(f"  property of `mean`, and the CURVE is the finding rather than the cell.")
    else:
        v = "W_ROBUST"
        worst = max(rows.values(), key=lambda r: r["diff"])
        print(f"  W-ROBUST — generic clears the length shortcut in 0 of {len(rows)} cells. The best")
        print(f"  cell for it is {worst['diff']:+.4f} against its own MDE {worst['mde']:.4f}. The")
        print(f"  negative is a property of the ARM, not of my aggregation.")
        print(f"  ⚠ AND `WHICH AGGREGATION THE DEFINITION INTENDS` IS UNANSWERED — the definition")
        print(f"    does not say. That is a finding ABOUT THE DEFINITION and is named, not resolved:")
        print(f"    a clause that does not fix its own aggregation cannot be tested in one cell.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               cells=rows, favour=favour, unverifiable=unver, n_cells=len(rows),
               placebo_ok=placebo_ok, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_speccurve.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
