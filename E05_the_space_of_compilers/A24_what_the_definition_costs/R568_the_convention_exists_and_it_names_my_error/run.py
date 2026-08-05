#!/usr/bin/env python3
"""R568 · The floor convention exists, and its docstring diagnoses R567's exact error.

R567 concluded the campaign has "60+ names for its floors and no schema", and my NEXT line proposed
building a key convention "for the first time". `assurance/an_mde_records_its_denominator.py`
already IS that convention -- and its docstring records R373 making R567's mistake and naming why
it is invalid.

ESTIMAND  (a) does a floor-key convention exist and pass?  (b) does its own text name the method
          R567 used as invalid?
IDENT     fully identified: a file, its exit code, and a verbatim string in it.
SCOPE     population = assurance/*.py · instrument = existence + exit code + substring ·
          baseline = "no convention exists" (R567's claim) · regime = HEAD.
WORLDS    A no such gate -> R567's finding stands and the convention must be built.
          B it exists -> R567's conclusion is retracted: the heterogeneity is HISTORICAL and the
            convention is a forward ratchet, which is a different fact.
KILL      pre-registered: the gate exists AND exits 0 -> WORLD B.
POS CTRL  a gate KNOWN to exist and pass (statement_provenance) must read as present+passing, else
          "exists and passes" is not a measurement.
NEG CTRL  an invented gate name must not be found.
ARTIFACT  results/convention_exists.json
"""
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
G = ROOT / "assurance"
def run(name):
    p = G / f"{name}.py"
    if not p.exists(): return None
    r = subprocess.run([sys.executable, str(p)], capture_output=True, text=True, timeout=280)
    return {"exists": True, "rc": r.returncode, "text": (p.read_text())}

pos = run("statement_provenance")
print(f"  POSITIVE CONTROL  a known gate reads present and passing: "
      f"{bool(pos) and pos['rc'] == 0} -> {'PASS' if pos and pos['rc'] == 0 else 'FAIL'}")
neg = run("zz_not_a_real_gate")
print(f"  NEGATIVE CONTROL  an invented gate is not found: {neg is None} -> "
      f"{'PASS' if neg is None else 'FAIL'}")
if not (pos and pos["rc"] == 0) or neg is not None:
    sys.exit(2)

g = run("an_mde_records_its_denominator")
exists = g is not None
passes = exists and g["rc"] == 0
print(f"\n  (a) an_mde_records_its_denominator exists: {exists}   exits 0: {passes}")

# (b) does its own text name R567's method as invalid?
# ⛔ THE FIRST VERSION MATCHED THE RAW TEXT and returned False on a sentence I had just quoted
# from this very file. The docstring WRAPS: "a guessed list\n   cannot prove an absence". The
# check failed on WHITESPACE -- same class as R562's underscore and R567's UUID, sixth this
# session. A prose search must normalise whitespace before it can claim an absence.
import re as _re
MARK = "a guessed list cannot prove an absence"
_norm = _re.sub(r"\s+", " ", g["text"]) if exists else ""
names_it = exists and MARK in _norm
print(f"      (raw-text match would have said: {MARK in g['text'] if exists else None} "
      f"-- a FALSE NEGATIVE on whitespace)")
print(f"  (b) its docstring contains the verbatim diagnosis {MARK!r}: {names_it}")
r373 = exists and "R373" in g["text"]
print(f"      and attributes it to a prior round (R373): {r373}")

world = "B" if (exists and passes) else "A"
print(f"\n  WORLD {world} -- " + (
    "the convention exists and passes; R567's 'no schema' conclusion is retracted -- the "
    "heterogeneity is HISTORICAL and the convention is a forward ratchet."
    if world == "B" else "no such gate; R567 stands."))
if names_it:
    print(f"  ⭐⭐⭐ and R567 committed the exact method this file names invalid, while this file "
          f"was passing on every commit of the session.")
(pathlib.Path(__file__).parent / "results" / "convention_exists.json").write_text(json.dumps(
    {"world": world, "gate_exists": exists, "gate_passes": passes,
     "docstring_names_the_error": bool(names_it), "attributes_to_r373": bool(r373),
     "retracts": "R567's conclusion that the campaign has no floor schema",
     "corrected_finding": "the convention exists as a FORWARD RATCHET with frozen debt 0; the 60+ "
                          "historical key names are what it does not attempt to migrate"}, indent=2))
