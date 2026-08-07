#!/usr/bin/env python3
"""R482 — the assurance suite has ~46 gates. This session ran four, every round, and called it green.

⚠ ACTION CLASS: **CLOSURE + PRODUCTION, not Frontier** (CLAUDE.md §0). It resolves no ontological
fork and separates no worlds. It (a) protects existing conclusions by actually running the checks
that exist, and (b) produces an instrument — `assurance/run_all.py` — so the failure cannot recur.
Labelling it a discovery would be exactly the "closure disguised as discovery" failure mode.

⛔ WHAT HAPPENED. `assurance/` holds 52 files. Every round this session ended with four of them —
`definition_matches_the_record`, `comparator_scope`, `statement_provenance`, `register_requirements` —
and the sentence "all four gates PASS". Each did pass. But there is **no Makefile, no runner and no
manifest**, so nothing anywhere contradicted the reading that the assurance layer was green.

⭐ IT IS R476's DEFECT ONE LEVEL UP. R476 found `definition_matches_the_record` reporting "302 of 302
assertions" — a numerator with no denominator — which let a corrupted number pass. **A pass count
quoted without the population it was drawn from will be read as a proportion.** I found that at the
assertion level and then committed it at the suite level in the same session.

⚠ AND THE UNRUN SUBSET WAS NOT RANDOM. `seed_filter_is_disclosed.py` is precisely retraction 304's
defect (an undeclared seed axis). `next_gradient_is_new.py` targets the sentence type behind
retractions 300 and 302. **The gates aimed at the errors I was actually making are the ones I was
not running.**

ESTIMAND
    (a) |gates that exist| vs |gates run per round this session|  -- a census, not an inference.
    (b) of the gates never run, how many FAIL when finally run -- the debt, measured.
    ⚠ (b) is NOT "how broken is the campaign": a gate may fail because it encodes a superseded
    framing, because its input moved, or because it found a real defect. Those are distinguished by
    reading each failure, and this round reports the COUNT and the CLASSIFICATION separately.

IDENTIFICATION
    Direct census; nothing is estimated. The only judgement is which files are gates rather than
    helpers, and that rule is written in `run_all.py:NOT_A_GATE`/`PREFIX_SKIP` rather than applied
    by hand, so it is auditable and was positive-controlled (`run_all.py --selftest`).

SCOPE
    population  assurance/*.py at HEAD.
    instrument  `run_all.py`, self-tested: it must classify a deliberately-failing gate as FAIL, a
                deliberately-empty gate as UNRUNNABLE, and must exit 2 on an empty gate population.
    baseline    the four gates run per round this session.
    regime      one repository, one session; says nothing about earlier sessions' discipline.

WORLDS
    A  DEBT SMALL   most unrun gates pass -> the four were a lucky subset and the cost was the
                    reporting language, not the state of the repo.
    B  DEBT LARGE   many unrun gates fail -> claims committed this session rest on unchecked ground
                    and the failures must be triaged before anything else proceeds.
    C  GATES STALE  the failures are gates encoding superseded framings rather than live defects ->
                    the debt is in the assurance layer itself, and unrun gates rot.

PREDICTION MATRIX
                    unrun failures    what they are        what it licenses
    A  small              few           n/a                fix the reporting sentence
    B  large             many        live defects          stop and triage
    C  stale             many      superseded framings     the gates need retiring, not the claims

PRE-REGISTERED KILL
    if runner_selftest_passes:
        A if fail_count <= 2 ; B if fail_count > 2 and any failure names a CURRENT artifact ;
        C if fail_count > 2 and all failures name retired framings
    else:
        UNVERIFIED -- an instrument that cannot detect a failing gate cannot census failures.

CONTROLS
    POSITIVE   `run_all.py --selftest` plants a gate that exits 1 and one that exits 2 and requires
               correct classification plus a non-zero overall status. RETURNED: PASS.
    g=0        an empty gate directory must discover nothing and the runner must EXIT 2, never 0 --
               the rule this suite's own `attack_the_suite.py` exists to enforce, applied to the
               runner itself. RETURNED: PASS.
    NEGATIVE   `_helper.py`-style files must be excluded by discovery, so the denominator counts
               gates rather than every file in the directory. RETURNED: PASS.

MULTIPLICITY  every gate reported, PASS and FAIL alike; no gate is dropped for being slow or noisy.

ARTIFACT  results/r482_suite_census.json

IMPOSSIBLE HERE, NAMED
    "were these gates green before this session?" -- would require running each at its own commit,
        which git can supply but which measures the repo's history rather than its state; not run.
    a severity ordering of the failures -- would need each gate's own claim card, and several do not
        carry one.
"""
import json, pathlib, subprocess, sys, time
ROOT = pathlib.Path(".")
OUT = ROOT/"E05_the_space_of_compilers/A24_what_the_definition_costs/R482_the_suite_has_fifty_two_gates_and_i_ran_four/results"
sys.path.insert(0, str(ROOT/"assurance"))
import run_all

RUN_THIS_SESSION = ["definition_matches_the_record", "comparator_scope",
                    "statement_provenance", "register_requirements"]

gates = run_all.discover()
print(f"  gates that EXIST      : {len(gates)}", flush=True)
print(f"  gates run per round   : {len(RUN_THIS_SESSION)}   {RUN_THIS_SESSION}")
print(f"  never run this session: {len(gates) - len(RUN_THIS_SESSION)}")
print(f"  ⭐ coverage {len(RUN_THIS_SESSION)}/{len(gates)} = {len(RUN_THIS_SESSION)/len(gates):.1%}"
      f" — the number every 'all gates PASS' this session actually meant")

print(f"\n  POSITIVE CONTROL — can the runner detect a failing gate?")
sel = subprocess.run([sys.executable, "assurance/run_all.py", "--selftest"],
                     capture_output=True, text=True)
print("\n".join("    " + l for l in sel.stdout.strip().splitlines()))
if sel.returncode != 0:
    print("\n  ⛔ UNVERIFIED — the instrument cannot detect a failing gate."); sys.exit(2)

rows = []
for p in gates:
    name, rc, el, msg = run_all.run_one(p, timeout=45)
    rows.append({"gate": name, "rc": rc, "sec": round(el, 1), "msg": msg,
                 "run_this_session": name in RUN_THIS_SESSION})
    print(f"    {'PASS' if rc==0 else 'FAIL' if rc==1 else 'UNRUN' if rc==2 else 'ERR':<5} "
          f"{name:<48} {el:5.1f}s {msg[:60]}", flush=True)

f = [r for r in rows if r["rc"] == 1]
u = [r for r in rows if r["rc"] == 2]
e = [r for r in rows if r["rc"] not in (0, 1, 2)]
print(f"\n  PASS {sum(1 for r in rows if r['rc']==0)} of {len(rows)}   FAIL {len(f)}   "
      f"UNRUNNABLE {len(u)}   ERROR/TIMEOUT {len(e)}")
print(f"  of the {len(f)} failures, {sum(1 for r in f if r['run_this_session'])} were in the four "
      f"I was running and {sum(1 for r in f if not r['run_this_session'])} were not.")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"n_gates": len(gates), "run_this_session": RUN_THIS_SESSION,
           "coverage": len(RUN_THIS_SESSION)/len(gates), "rows": rows,
           "n_fail": len(f), "n_unrunnable": len(u), "n_error": len(e),
           "selftest_passed": sel.returncode == 0},
          open(OUT/"r482_suite_census.json", "w"), indent=2)
sys.exit(0)
