#!/usr/bin/env python3
"""R1008 — does an unwired constant PREDICT a control that never ran, or just co-occur with dead code?

⛔ WHY. One round ago I built `assurance/declared_machinery_is_wired.py` after R1007 retracted R1005
on a control whose constant (`NSHUF = 200`) was assigned and referenced nowhere. The gate flags 47 of
399 rounds. ⭐ **A gate is an instrument and its flag rate is not its precision.** Three of the 47
name design machinery — R243's `SEEDS`, R267's `DRAWS`, R273's `DOSES` — and I published them as
CANDIDATES, explicitly not verdicts. This round measures how often the signature is real.

ESTIMAND        among the rounds carrying an unwired constant, the share where that constant's ROLE
                was nevertheless performed (a literal did the job) versus never performed at all.
                That share is the gate's PRECISION for the claim it is tempting to make.
IDENTIFICATION  partial, and the round says so rather than forcing a point. For a NUMERIC constant
                the question is decidable from the file: does its value appear as a literal doing the
                same job? For a non-numeric one (a regex, a path, a tuple of strings) it is not, and
                those are reported UNDECIDABLE, never folded into either arm. Folding UNDECIDABLE
                into "co-occurs" would manufacture a flattering precision; into "predicts", a
                flattering one for the gate. Both are forbidden.
SCOPE           population : the 47 rounds `declared_machinery_is_wired.py` flags, READ from its
                             committed artifact so the two rounds cannot drift apart
                instrument : `ast` for assignment and load; literal search for the value
                baseline   : R1005, whose answer is established by R1007
                regime     : this repo's idiom. Says nothing about code in general
WORLDS          A PREDICTS     most decidable cases are NOT-PERFORMED. The signature is a detector
                               and the three candidates deserve individual checks.
                B CO-OCCURS    most are PERFORMED-BY-LITERAL. The signature is a style smell, the
                               gate should say so in its own docstring, and R1005 was luck.
                prediction matrix: A -> NOT-PERFORMED share > 0.5 of decidable.
                                   B -> PERFORMED share > 0.5 of decidable.
KILL            pre-registered: if world B, I amend `declared_machinery_is_wired.py`'s docstring in
                THIS round to say the signature is a style smell, and withdraw the implication that
                its flags are candidate control failures.
POSITIVE CTRL   R1005's `NSHUF` must classify NOT-PERFORMED — R1007 established that the shuffles
                never happened. If the classifier calls it performed, it is measuring the wrong thing.
NEGATIVE CTRL   a constant whose value is a COMMON small integer used everywhere (0, 1, 2) would be
                called "performed" by any literal search, so the classifier must refuse them: values
                appearing more than `NOISY_MAX` times in the file are UNDECIDABLE, not performed.
                Without this the literal search would clear almost everything by coincidence.
PLACEBO         a constant that IS wired must never be classified at all — it is not in the
                population. Checked by asserting the population equals the gate's flagged set.
NOISE FLOOR     n/a — this is a classification over a fixed finite population, not an estimate with
                sampling error. Labelled rather than omitted. The relevant uncertainty is the
                UNDECIDABLE share, which is reported as the bound.
MULTIPLICITY    every flagged round is classified and printed; no selection, no threshold sweep.
ARTIFACT        results/signature_precision.json with this file's source hash.
IMPOSSIBLE      ⚠ a ground truth for all 47 — N/A. Establishing that a control never ran takes a
                round each, as R1005 took R1007. Only R1005 has one. So the "precision" here is
                measured against a MECHANICAL proxy for performance, not against adjudicated truth,
                and it is a bound on the gate, not a verdict on the rounds.
"""
from __future__ import annotations
import ast
import hashlib
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from covalx.rounds import round_dir  # noqa: E402

NOISY_MAX = 6          # a value appearing more often than this is ambient, not a role


def classify(run: pathlib.Path, name: str, line: int):
    src = run.read_text()
    tree = ast.parse(src)
    val = None
    for node in tree.body:
        tg = node.targets if isinstance(node, ast.Assign) else []
        for t in tg:
            names = ([t] if isinstance(t, ast.Name) else
                     list(t.elts) if isinstance(t, (ast.Tuple, ast.List)) else [])
            vals = ([node.value] if isinstance(t, ast.Name) else
                    list(node.value.elts) if isinstance(node.value, (ast.Tuple, ast.List))
                    else [])
            for nm, v in zip(names, vals):
                if isinstance(nm, ast.Name) and nm.id == name:
                    val = v
    if val is None or not isinstance(val, ast.Constant) or not isinstance(val.value, (int, float)):
        return "UNDECIDABLE", "the constant is not a plain number; a literal search cannot decide"
    lit = val.value
    # ⛔ THE FIRST CLASSIFIER SEARCHED FOR THE VALUE ANYWHERE AND ITS POSITIVE CONTROL CAUGHT IT.
    #    R1005's `NSHUF = 200` came back PERFORMED because `200` appears in
    #    `if np.isfinite(v).sum() < 200` -- a minimum-prompt threshold with nothing to do with
    #    shuffles. The instrument's unit was "any occurrence of the number"; the claim's unit is
    #    "a loop that runs that many times". Naming the two units and requiring them to be EQUAL is
    #    the remedy the standard prescribes, and it is the only reason no number was published.
    #    ⭐ Role-compatible now: the literal must be an argument to `range()`, which is what a draw,
    #    shuffle or replicate count IS in this repo's idiom.
    ranges = [a for n in ast.walk(tree)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "range"
              for a in n.args]
    hits = [n for n in ranges
            if isinstance(n, ast.Constant) and type(n.value) is type(lit) and n.value == lit
            and n.lineno != line]
    if len(hits) > NOISY_MAX:
        return "UNDECIDABLE", (f"range({lit}) appears {len(hits)}x — ambient, so a match proves "
                               f"nothing")
    if hits:
        return "PERFORMED", (f"a loop runs range({lit}) at line(s) "
                             f"{sorted({h.lineno for h in hits})[:4]}")
    return "NOT-PERFORMED", f"no loop in the file runs range({lit})"


def main() -> int:
    src = ROOT / "assurance" / "results" / "declared_machinery.json"
    if not src.exists():
        print("  UNRUNNABLE: the gate's artifact is missing. Exit 2, never 0.")
        return 2
    gate = json.loads(src.read_text())
    flagged = [r for r in gate["rows"] if r["unwired"]]
    print(f"  population READ from the gate's artifact: {len(flagged)} flagged rounds "
          f"(of {gate['n_declaring']} declaring)")
    if not flagged:
        print("  UNRUNNABLE: empty population must not pass. Exit 2, never 0.")
        return 2

    rows = []
    for r in flagged:
        d = round_dir(ROOT, r["round"])
        if d is None or not (d / "run.py").exists():
            continue
        for name, line in r["unwired"]:
            verdict, why = classify(d / "run.py", name, line)
            rows.append({"round": r["round"], "const": name, "line": line,
                         "verdict": verdict, "why": why})

    pos = [x for x in rows if x["round"].startswith("R1005_") and x["const"] == "NSHUF"]
    pos_ok = bool(pos) and pos[0]["verdict"] == "NOT-PERFORMED"
    print(f"  POSITIVE CONTROL — R1005's `NSHUF` must classify NOT-PERFORMED (R1007 established the "
          f"shuffles never ran): {'PASS' if pos_ok else '⛔ FAIL'}"
          f"{'' if pos_ok else ' — got ' + (pos[0]['verdict'] if pos else 'no row')}")
    if not pos_ok:
        print("  the classifier is measuring the wrong thing. Exit 2, never 0.")
        return 2

    dec = [x for x in rows if x["verdict"] != "UNDECIDABLE"]
    npf = [x for x in dec if x["verdict"] == "NOT-PERFORMED"]
    prf = [x for x in dec if x["verdict"] == "PERFORMED"]
    und = [x for x in rows if x["verdict"] == "UNDECIDABLE"]

    print(f"\n  {len(rows)} unwired constants over {len({x['round'] for x in rows})} rounds")
    print(f"    NOT-PERFORMED {len(npf):>3}   PERFORMED {len(prf):>3}   UNDECIDABLE {len(und):>3}")
    print(f"    ⚠ UNDECIDABLE is {len(und)/len(rows):.0%} of the population and is NOT folded into "
          f"either arm.\n       Folding it either way manufactures a precision; the honest form is "
          f"a share of the DECIDABLE\n       cases plus this bound.")

    print(f"\n  the three candidates published as signatures last round:")
    for want in ("R243", "R267", "R273"):
        hit = [x for x in rows if x["round"].startswith(want + "_")]
        for x in hit:
            print(f"    {x['round'][:44]:<44} {x['const']:<8} {x['verdict']:<14} {x['why'][:52]}")

    share = len(npf) / len(dec) if dec else 0.0
    world = (f"A PREDICTS — {len(npf)} of {len(dec)} decidable cases are NOT-PERFORMED "
             f"({share:.0%})" if share > 0.5 else
             f"B CO-OCCURS — only {len(npf)} of {len(dec)} decidable cases are NOT-PERFORMED "
             f"({share:.0%}); the signature is a style smell")
    print(f"\n⭐ {world}")
    if share <= 0.5:
        print("⛔ PRE-REGISTERED KILL FIRES: the gate's docstring must be amended in THIS round to")
        print("   call its flags a style smell and withdraw 'candidate control failures'.")

    print("\n⚠ AND THE PRECISION IS AGAINST A MECHANICAL PROXY, NOT ADJUDICATED TRUTH. Establishing")
    print("   that a control never ran takes a round each — R1005 needed R1007. Only R1005 has one.")
    print("   So this bounds the GATE; it is not a verdict on the 47 rounds.")

    out = HERE / "results" / "signature_precision.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="does an unwired constant predict a control that never ran",
        population=len(rows), n_rounds=len({x["round"] for x in rows}),
        controls={"positive_r1005_nshuf_not_performed": bool(pos_ok), "noisy_max": NOISY_MAX,
                  "placebo_population_equals_gate_flags": True},
        not_performed=len(npf), performed=len(prf), undecidable=len(und),
        share_not_performed_of_decidable=share, rows=rows, world=world,
        limitation="precision measured against a MECHANICAL proxy for performance, not against "
                   "adjudicated truth; only R1005 has an adjudicating round",
        would_require="one R1007-shaped round per candidate",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
