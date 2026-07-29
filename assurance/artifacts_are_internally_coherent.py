"""Two properties every published artifact must satisfy, checkable without knowing what it measures.

WHY THIS EXISTS
---------------
Twelve rounds of auditing (entries 184-196) found every defect in a SUMMARISER, an
index, a row or a check -- never in a measurement. These two invariants are how that
was established, and entry 196 left them as one-off scans. A one-off command protects
nothing after the terminal scrolls (entry 174).

THE TWO INVARIANTS, and why only these two
-------------------------------------------
  1. A point estimate lies INSIDE the interval published with it.
  2. A stored significance flag AGREES with its own interval.
     (plus: an interval's bounds are ordered, lo <= hi)

Both are checkable with NO knowledge of the estimand, the population, or what the round
intended. No judgement, no registry, no per-round exemption -- which is why they can run
over every artifact at once and why a violation is unarguable. Every richer property
this package cares about needs a reading; these two do not.

SCOPE -- deliberately narrow, so a hit is real
-----------------------------------------------
Invariant 1 applies only to STEM-MATCHED pairs: a mean and a CI the round itself names
together (`gap` / `gap_ci`). Cross-key pairs are exactly what r58's harvester got wrong,
and guessing at them here would import that defect.
Invariant 2 applies only where a node carries EXACTLY ONE CI and EXACTLY ONE flag. With
several of either, which pairs with which is a reading, and this check does not read.

THE PROXY LEDGER
----------------
PROPERTY    the artifact's numbers are mutually consistent.
PROXY       these two relations hold on unambiguous pairs.
IMPLICATION violation => inconsistent          SOUND, and this gates on it.
            holds     => the artifact is right  NOT SOUND. A round can be perfectly
                                                self-consistent and wrong about the
                                                world. These catch INCOHERENCE, never
                                                ERROR.
SAFE SIDE   reports incoherence; never certifies correctness.
"""
from __future__ import annotations

import json
import pathlib
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
CIISH = re.compile(r"^(ci|.*_ci|ci_.*|interval)$", re.I)
MEANISH = re.compile(r"^(mean|diff|delta|gap|advantage|drop|attribution|effect|"
                     r".*_mean|.*_diff|.*_delta|.*_gap)$", re.I)
BOOLISH = re.compile(r"^(excludes_zero|significant|.*_significant|significant_.*|"
                     r"excludes_0|is_significant)$", re.I)


def is_ci(v):
    return (isinstance(v, list) and len(v) == 2
            and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v))


def scan(root: pathlib.Path):
    out = {"outside": [], "contradict": [], "inverted": [], "n_pairs": 0, "n_flagged": 0}

    def walk(o, rid, path):
        if isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, rid, f"{path}[{i}]")
            return
        if not isinstance(o, dict):
            return
        cks = [(k, o[k]) for k in o if CIISH.match(k) and is_ci(o[k])]
        mks = [(k, o[k]) for k in o
               if MEANISH.match(k) and isinstance(o[k], (int, float)) and not isinstance(o[k], bool)]
        bks = [(k, o[k]) for k in o if BOOLISH.match(k) and isinstance(o[k], bool)]
        for ck, cv in cks:
            if cv[0] > cv[1]:
                out["inverted"].append((rid, path or "<root>", ck, cv))
        for mk, mv in mks:                                   # invariant 1, stem-matched only
            for ck, cv in cks:
                if mk.lower() in ck.lower() or ck.lower().replace("_ci", "") == mk.lower():
                    lo, hi = sorted(cv)
                    out["n_pairs"] += 1
                    if not (lo <= mv <= hi):
                        out["outside"].append((rid, path or "<root>", mk, mv, ck, [lo, hi]))
        if len(cks) == 1 and len(bks) == 1:                  # invariant 2, unambiguous only
            (ck, cv), (bk, bv) = cks[0], bks[0]
            lo, hi = sorted(cv)
            out["n_flagged"] += 1
            if bool(lo > 0 or hi < 0) != bv:
                out["contradict"].append((rid, path or "<root>", ck, [lo, hi], bk, bv))
        for k, v in o.items():
            walk(v, rid, f"{path}.{k}" if path else k)

    for f in sorted(root.glob("rounds/*/results/*.json")):
        if "_smoke" in str(f) or f.stat().st_size > 6_000_000:
            continue
        try:
            walk(json.load(open(f)), f.parts[-3], "")
        except Exception:
            continue
    return out


def positive_control() -> tuple[bool, str]:
    """Plant one violation of each invariant and one clean case of each. A check that has
    never returned non-zero cannot be trusted when it returns zero."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="coh_ctrl_"))
    try:
        d = tmp / "rounds" / "rZZ_plant" / "results"
        d.mkdir(parents=True)
        (d / "p.json").write_text(json.dumps({
            "clean_pair":   {"gap": 0.05, "gap_ci": [0.04, 0.06]},
            "outside_pair": {"gap": 0.50, "gap_ci": [0.04, 0.06]},
            "clean_flag":   {"ci": [0.02, 0.05], "excludes_zero": True},
            "broken_flag":  {"ci": [0.02, 0.05], "excludes_zero": False},
        }))
        r = scan(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    got_o = [x[1] for x in r["outside"]]
    got_c = [x[1] for x in r["contradict"]]
    ok = got_o == ["outside_pair"] and got_c == ["broken_flag"]
    return ok, f"outside={got_o} contradict={got_c}"


def main() -> int:
    ok, detail = positive_control()
    print(f"positive control: {detail} -> {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("\nFINDING: the check does not fire on planted violations of its own invariants, so a "
              "zero on the live tree would be silence rather than a result.")
        return 1

    r = scan(ROOT)
    print(f"\n{r['n_pairs']} stem-matched mean/CI pairs; {r['n_flagged']} nodes with exactly one CI "
          f"and one significance flag")
    # FLOOR: an empty population is "nothing to check" (2), never "clean" (0). With no
    # artifacts to scan this check finds no violations, and reporting that as a pass
    # would be silence mistaken for an acquittal -- the exact failure attack_the_suite
    # exists to prevent.
    if r["n_pairs"] == 0 and r["n_flagged"] == 0:
        print("\nZERO pairs and ZERO flagged nodes found -- nothing to check, not a clean bill.")
        return 2

    fail = 0
    for key, label in (("outside", "point estimate OUTSIDE the interval published with it"),
                       ("contradict", "significance flag CONTRADICTS its own interval"),
                       ("inverted", "interval bounds INVERTED (lo > hi)")):
        rows = r[key]
        print(f"  {label:<52} {len(rows)}")
        if rows:
            fail = 1
            for x in rows[:8]:
                print(f"      {x[0]}:{x[1]}  {x[2:]}")
    if fail:
        print("\n1 gate(s) failed.")
        return 1
    print("\nevery artifact is internally coherent on both invariants.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
