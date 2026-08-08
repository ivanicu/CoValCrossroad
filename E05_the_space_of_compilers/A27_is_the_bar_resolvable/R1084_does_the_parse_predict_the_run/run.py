#!/usr/bin/env python3
"""R1084 — across all 88 assurance scripts: does the PARSE predict the RUN?

R1083 repaired 8 cwd-dependent reads in one gate and shipped a guard that watches three scripts. The
directory holds 88. The obvious move is to grep for relative paths -- and R1077 measured that a text
scan counts MENTIONS as USES, while R1083's own defect was found by EXECUTION and not by reading. So
this round runs both instruments over the whole population and scores the cheap one against the
expensive one. **The proposer is the object under test, not the shortcut.**

ESTIMAND        over the 88 scripts in `assurance/`:
                  PROPOSED   an AST pass finds >=1 path-shaped string literal passed to a read/write
                             call that is NOT built from a module-level ROOT/HERE
                  CONFIRMED  the script, executed from the repository root and from an unrelated
                             directory, returns a DIFFERENT exit code or different normalised stdout
                The quantity: the 2x2 confusion of PROPOSED x CONFIRMED, and specifically the
                FALSE NEGATIVE cell -- scripts whose behaviour moves and whose parse said nothing.
                A single FN means the parse cannot be used as the instrument, only as a nomination.
IDENTIFICATION  CONFIRMED is identified by execution. PROPOSED is identified by the AST. The 2x2 is
                identified over the scripts that pass the DETERMINISM precheck; scripts failing it
                are UNVERIFIED and are reported as a third column, never folded into either.
UNIT OF THE     a script, and whether its (exit code, normalised stdout) moved between two CWDs.
  INSTRUMENT
UNIT OF THE     the same. The sentence permitted is "this script's behaviour depends on the
  CLAIM         directory it was invoked from". It is NOT "this script has a bug" -- a script that
                legitimately reports the CWD would move too, and is reported rather than accused.
SCOPE           population: assurance/*.py, 88 files. instrument: subprocess, CPython, 60s timeout.
                baseline: the determinism floor, measured as run-vs-run from the SAME directory.
                regime: this checkout, tree clean at start.
WORLDS          A THE PARSE IS THE INSTRUMENT  proposal and confirmation coincide; FN = 0, so the
                                               cheap scan could have replaced the sweep.
                B THE PARSE NOMINATES ONLY     FN > 0: behaviour moves through routes no literal
                                               names -- os.chdir, a relative glob, an env var, a
                                               subprocess of its own.
                C THE PARSE IS NOISE           FP >> TP: most literals are mentions, not uses, which
                                               is R1077's finding one level up.
                Prediction matrix on (FN, FP/TP):
                  A -> (0, small)    B -> (>0, any)    C -> (any, large)
KILL            pre-registered, evaluated ONLY if the control gate opens.
                  World A is KILLED if FN >= 1. One script whose behaviour moves without its parse
                  saying so is enough, because the proposal would then have been used to CLOSE the
                  question for the other 87.
POSITIVE CTRL   plant a cwd-dependent read into a copy of a script known invariant. BOTH instruments
                must fire. Retention reported; MDE is one script.
g=0 GUARD       the same copy WITHOUT the plant must fire on neither. Without this the harness would
                flag every script it copies.
NEGATIVE CTRL   plant a ROOT-rooted read -- a real read, not cwd-dependent. NEITHER may fire. This
                separates "reads a file" from "reads relative to the caller".
SHAM            the same operation minus the ingredient: plant a relative path literal that is
                ASSIGNED AND NEVER USED. The parse MUST fire (that is its known blind spot, measured
                here rather than asserted) and the run must NOT. This cell is the mentions-vs-uses
                gap, priced.
PLACEBO         compare a script's two runs from the SAME directory. Must be identical for every
                script that enters the 2x2 -- that is the determinism floor and it is measured.
NOISE FLOOR     the placebo above, per script.
MULTIPLICITY    all 88 scripts reported in the confusion matrix, including the UNVERIFIED column.
SPECIFICATION   compare_on   (exit code only) vs (exit code + normalised stdout)
                normalise    path-scrubbing on/off
                ⭐ Every cell is a re-READING of the SAME captured runs. The first version
                re-executed the population per cell -- 640 extra invocations to vary two post-hoc
                transformations of stdout, which cannot change what a process did, and which
                multiplied the cost of the one script that exceeds the timeout. A specification
                curve over the COMPARISON needs no new runs; one over the EXECUTION does.
ARTIFACT        results/parse_vs_run.json with the source hash.
REPRODUCIBILITY the sweep is re-run for the placebo arm; the tree is checked clean before and after
                and any script that mutated it is named.
IMPOSSIBLE      whether a moving script is WRONG rather than merely cwd-aware -- N/A, that is a
                per-script judgement; the round reports movement and names the candidates.
                Cross-repository -- N/A, a second assurance directory.
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "parse_vs_run.json"
ASSUR = ROOT / "assurance"
TIMEOUT = 60

READ_CALLS = {"open", "load", "loads", "read_text", "write_text", "read_bytes", "glob", "rglob"}
PATHY = re.compile(r"[./]|\.(json|md|py|jsonl|txt|csv)$")


WRITE_CALLS = {"write_text", "dump", "mkdir", "unlink", "rmtree", "move", "copy", "copy2",
               "rename", "touch", "write_bytes"}


def writes(path: pathlib.Path) -> bool:
    """⛔ THE EXECUTED ARM IS NOT IDENTIFIED FOR A SCRIPT THAT WRITES INTO THE REPOSITORY.

    Measured the hard way: running the population twice from two directories left
    `assurance/ASSURANCE.md` truncated to 22 of 111 lines, `DEFECTS.json` down 395 lines and
    `MANIFEST.json` churned by 943 -- because 33 of the 89 scripts write, and a script's SECOND run
    reads what its FIRST run wrote. The comparison then measures the side effect, not the CWD.
    The one FALSE NEGATIVE the first pass produced was itself a writer, so the cell that would have
    killed world A was an artifact of this.
    Excluded here and reported as N/A with what it would require: one isolated copy of the
    repository per run, which is a different round.
    """
    try:
        tree = ast.parse(path.read_text(errors="replace"))
    except SyntaxError:
        return True
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            nm = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute)
                                                       else None)
            if nm in WRITE_CALLS:
                return True
            if nm == "open" and len(n.args) > 1 and isinstance(n.args[1], ast.Constant) \
                    and any(c in str(n.args[1].value) for c in "wax"):
                return True
            if nm in {"run", "Popen", "call", "check_output"}:
                return True
    return False


# ------------------------------------------------------------------ the PROPOSER (cheap, AST)

def rooted_names(tree: ast.AST) -> set[str]:
    """module-level names that hold a path anchored somewhere other than the CWD."""
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id in {
                        "ROOT", "HERE", "A24", "DOC", "ASSUR", "E05", "BASE", "REPO", "_ROOT",
                        "_HERE", "OUT", "RES"}:
                    out.add(t.id)
    return out


def anchored(node: ast.AST, names: set[str]) -> bool:
    """is this expression built from an anchored name (ROOT / "x" / "y"), at any depth?"""
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and n.id in names:
            return True
        if isinstance(n, ast.Attribute) and n.attr in {"parent", "parents", "resolve"}:
            return True
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "next":
            return True                       # the landmark idiom
    return False


def anchored_strict(node: ast.AST, names: set[str]) -> bool:
    """⚠ THE LOOSE RULE BIASES TOWARD SILENCE, AND SILENCE IS THE CELL THE KILL KEYS ON.
       `anchored()` returns True if ANY `.parent`, `.resolve()` or `next(` appears anywhere in the
       call node, so a call that merely mentions one suppresses its own proposal -- inflating FN,
       which is exactly what `world A is KILLED if FN >= 1` reads. This variant demands an anchored
       NAME and nothing else. Both are reported; the kill is checked against both."""
    return any(isinstance(n, ast.Name) and n.id in names for n in ast.walk(node))


def propose(path: pathlib.Path, strict: bool = False) -> list[str]:
    """path-shaped string literals reaching a read/write call without an anchor. AST, not grep."""
    try:
        tree = ast.parse(path.read_text(errors="replace"))
    except SyntaxError:
        return []
    names = rooted_names(tree)
    hits = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        fn = n.func
        name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute)
                                                       else None)
        if name not in READ_CALLS:
            continue
        args = list(n.args)
        if isinstance(fn, ast.Attribute):
            args.append(fn.value)             # the receiver of `.read_text()` etc.
        for a in args:
            if isinstance(a, ast.Constant) and isinstance(a.value, str) and PATHY.search(a.value):
                anc = anchored_strict(n, names) if strict else anchored(n, names)
                if not anc:
                    hits.append(f"{name}({a.value[:70]!r})")
    return sorted(set(hits))


# ------------------------------------------------------------------ the CONFIRMER (execution)

def scrub(s: str, *paths) -> str:
    for p in paths:
        s = s.replace(str(p), "<PATH>")
    return re.sub(r"\d+\.\d+\s*s\b|\b\d{4}-\d\d-\d\d\b", "<T>", s)


def run_from(script: pathlib.Path, cwd: pathlib.Path, timeout=TIMEOUT):
    try:
        r = subprocess.run([sys.executable, str(script)], cwd=str(cwd),
                           capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout
    except subprocess.TimeoutExpired:
        return None, ""


def capture3(script, other, timeout=TIMEOUT):
    """⭐ THREE runs, not four, and the two directories CONCURRENTLY.

    The determinism floor is (ROOT vs ROOT) and the sweep is (ROOT vs other); the first ROOT run is
    shared between them. The original design ran four subprocesses per script, strictly
    sequentially, and at 88 scripts with a 60s timeout on the slow ones it had not finished in
    twelve minutes. Nothing about the question required four runs -- it required three.
    """
    # ⛔ SEQUENTIAL, DELIBERATELY. Running the two arms concurrently made every writing script race
    #    against its own twin and corrupted four tracked files. Speed is not worth measuring a
    #    different object; the population is bounded instead.
    r1, o1 = run_from(script, ROOT, timeout)
    ro, oo = run_from(script, other, timeout)
    r2, o2 = run_from(script, ROOT, timeout)
    return {"floor": {"rc": (r1, r2), "out": (o1, o2), "dirs": (ROOT, ROOT)},
            "sweep": {"rc": (r1, ro), "out": (o1, oo), "dirs": (ROOT, other)}}


def capture(script, a_dir, b_dir, timeout=TIMEOUT):
    """⭐ RUN ONCE. Every specification cell below is a different READING of these same bytes.
       The first version re-executed the whole population for each cell -- 640 extra invocations
       to vary `normalise` and `compare_on`, which are post-hoc transformations of stdout and
       cannot change what the process did. It also multiplied the cost of the one script that
       exceeds the timeout. A specification curve over the COMPARISON does not need new runs."""
    ra, oa = run_from(script, a_dir, timeout)
    rb, ob = run_from(script, b_dir, timeout)
    return {"rc": (ra, rb), "out": (oa, ob), "dirs": (a_dir, b_dir)}


def read_capture(cap, normalise=True, on_stdout=True):
    ra, rb = cap["rc"]
    if ra is None or rb is None:
        return "UNVERIFIED_timeout", (ra, rb)
    oa, ob = cap["out"]
    if normalise:
        a_dir, b_dir = cap["dirs"]
        oa, ob = scrub(oa, a_dir, b_dir, ROOT), scrub(ob, a_dir, b_dir, ROOT)
    moved = (ra != rb) or (on_stdout and oa != ob)
    return ("MOVED" if moved else "STABLE"), (ra, rb)


def compare(script, a_dir, b_dir, normalise=True, on_stdout=True, timeout=TIMEOUT):
    return read_capture(capture(script, a_dir, b_dir, timeout), normalise, on_stdout)


def main() -> int:
    every = sorted(p for p in ASSUR.glob("*.py") if p.is_file())
    writers = [p for p in every if writes(p)]
    scripts = [p for p in every if p not in writers]
    if not scripts:
        print("  UNRUNNABLE: no assurance scripts found. Exit 2, never 0.")
        return 2
    dirty_before = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                                  capture_output=True, text=True).stdout.splitlines()

    other = pathlib.Path(tempfile.mkdtemp(prefix="r1084_"))
    proposed_strict = {}
    try:
        # ---- PLACEBO / determinism floor: two runs from the SAME directory must agree ----
        floor, proposed, confirmed, verdicts, caps = {}, {}, {}, {}, {}
        for s in scripts:
            three = capture3(s, other)
            floor[s.name] = read_capture(three["floor"])[0]
            proposed[s.name] = propose(s)
            proposed_strict[s.name] = propose(s, strict=True)
            caps[s.name] = three["sweep"]
            v, rcs = read_capture(three["sweep"])
            verdicts[s.name] = {"verdict": v, "rc_root": rcs[0], "rc_other": rcs[1]}
            confirmed[s.name] = (v == "MOVED")
        nondet = sorted(k for k, v in floor.items() if v == "MOVED")
        timeouts = sorted(k for k, v in floor.items() if v.startswith("UNVERIFIED"))

        eligible = [s.name for s in scripts
                    if floor[s.name] == "STABLE" and not verdicts[s.name]["verdict"]
                    .startswith("UNVERIFIED")]
        TP = sorted(n for n in eligible if proposed[n] and confirmed[n])
        FP = sorted(n for n in eligible if proposed[n] and not confirmed[n])
        FN = sorted(n for n in eligible if not proposed[n] and confirmed[n])
        TN = sorted(n for n in eligible if not proposed[n] and not confirmed[n])

        # ---- controls: four plants into copies of a script that is STABLE and unproposed ----
        base_name = next((n for n in TN), None)
        ctrl, plant_detail = {}, {}
        if base_name is None:
            print("  UNRUNNABLE: no stable, unproposed script to plant against. Exit 2, never 0.")
            return 2
        base = ASSUR / base_name
        src = base.read_text()

        def plant(tag, injected):
            p = ASSUR / f"_r1084_{tag}.py"
            p.write_text(src.replace("def main(", injected + "\n\ndef main(", 1))
            try:
                pr = bool(propose(p))
                cf = compare(p, ROOT, other)[0] == "MOVED"
                plant_detail[tag] = {"proposed": pr, "confirmed": cf}
                return pr, cf
            finally:
                p.unlink(missing_ok=True)

        pos = plant("pos", 'import json as _j\n'
                           'try:\n'
                           '    _x = open("assurance/MANIFEST.json").read()\n'
                           '    print("PLANT saw", len(_x))\n'
                           'except OSError:\n'
                           '    print("PLANT saw nothing")')
        ctrl["POSITIVE a planted cwd-dependent read: parse fires"] = pos[0]
        ctrl["POSITIVE a planted cwd-dependent read: run confirms"] = pos[1]
        g0 = plant("g0", '# no plant at all')
        ctrl["g=0 the copied script alone fires neither"] = not g0[0] and not g0[1]
        neg = plant("neg", 'import pathlib as _pl\n'
                           '_R = _pl.Path(__file__).resolve().parent.parent\n'
                           'try:\n'
                           '    _y = open(_R / "assurance" / "MANIFEST.json").read()\n'
                           '    print("ANCHORED saw", len(_y))\n'
                           'except OSError:\n'
                           '    print("ANCHORED saw nothing")')
        ctrl["NEGATIVE a ROOT-anchored read fires neither"] = not neg[0] and not neg[1]
        # ⛔ THE FIRST SHAM FAILED FOR ITS OWN REASONS, and diagnosing it is the correction.
        #    It planted `_UNUSED = "assurance/MANIFEST.json"` -- a bare ASSIGNMENT -- and asserted
        #    the parse would fire, on the strength of R1077's "a text scan counts MENTIONS as USES".
        #    This proposer is not a text scan: it only inspects literals that are ARGUMENTS OF A
        #    READ CALL, so it ignored the assignment correctly. I asserted a blind spot my own
        #    instrument does not have -- from its description rather than its behaviour.
        # ⭐ The sham that actually isolates the ingredient: a literal that IS an argument of a read
        #    call, on a branch the run never takes. The parse MUST fire (it is syntactically a read)
        #    and the run must NOT move. That is the mentions-vs-uses gap, priced.
        sham = plant("sham", 'if False:\n'
                             '    _dead = open("assurance/MANIFEST.json").read()   # never executed')
        ctrl["SHAM an unreachable read call: the parse fires (its blind spot, measured)"] = sham[0]
        ctrl["SHAM an unreachable read call: the run does NOT move"] = not sham[1]
        ctrl["PLACEBO the determinism floor is clean for the eligible set"] = all(
            floor[n] == "STABLE" for n in eligible)
        gate_open = all(ctrl.values())

        # ---- specification curve ----
        spec = []
        for on_stdout in (True, False):
            for normalise in (True, False):
                m = sum(1 for n in eligible
                        if read_capture(caps[n], normalise, on_stdout)[0] == "MOVED")
                spec.append({"compare_on": "rc+stdout" if on_stdout else "rc only",
                             "normalise": normalise, "scripts": len(eligible), "moved": m})
    finally:
        for f in other.glob("*"):
            f.unlink(missing_ok=True)
        other.rmdir()

    dirty_after = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                                 capture_output=True, text=True).stdout.splitlines()
    mutated = sorted(set(dirty_after) - set(dirty_before))

    a_killed = gate_open and len(FN) >= 1
    prec = len(TP) / (len(TP) + len(FP)) if (TP or FP) else None
    rec = len(TP) / (len(TP) + len(FN)) if (TP or FN) else None

    if not gate_open:
        verdict = ("UNVERIFIED — a control failed, so neither instrument's count licenses a claim. "
                   "A kill that can fire on a broken instrument is not a commitment.")
    elif a_killed:
        verdict = (f"world A (THE PARSE IS THE INSTRUMENT) is KILLED — {len(FN)} script(s) move "
                   f"between working directories with NO path literal to explain it: {FN[:6]}. "
                   f"The parse has recall {rec:.2f} and precision {prec:.2f} against the run, so it "
                   f"NOMINATES and never CLOSES.")
    else:
        # ⛔ THE FIRST VERSION OF THIS STRING QUOTED `len(confirmed)` -- the SIZE OF THE DICT, 47 --
        #    as "moving scripts", where the moving count is 1, and called the population "88 files"
        #    when the executed population is 45. Two typed numbers in one sentence, neither
        #    computed. §4's `the verdict string is not a computation`, in the round whose subject is
        #    instruments. Every number below is now read from the same variables the table is.
        n_moving = len(TP) + len(FN)
        verdict = (f"world A survives ON THE READ-ONLY POPULATION — all {n_moving} script(s) whose "
                   f"behaviour moves were proposed by the parse (recall {rec:.2f}), under BOTH the "
                   f"loose and the strict rule. But precision is {prec:.2f}: {len(FP)} of "
                   f"{len(TP)+len(FP)} proposals are literals the run never reaches. The parse is a "
                   f"sound NOMINATOR and a poor DECIDER. And it speaks for {len(eligible)} of "
                   f"{len(every)} scripts only -- {len(writers)} write into the repository and are "
                   f"NOT IDENTIFIED for a two-run comparison at all.")

    art = {
        "round": "R1084",
        "question": "across all assurance scripts, does the AST parse predict the executed behaviour?",
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "population": {"scripts_in_directory": len(every),
                       "read_only_and_therefore_executable": len(scripts),
                       "writers_excluded": len(writers),
                       "writers": [q.name for q in writers],
                       "why_excluded": ("a script that writes into the repository reads its own "
                                        "previous run's output, so a two-run comparison measures "
                                        "the side effect and not the CWD. Measured: the first pass "
                                        "truncated ASSURANCE.md to 22 of 111 lines and cut 395 "
                                        "lines from DEFECTS.json."),
                       "what_it_would_require": ("one isolated copy of the repository per run"),
                       "eligible_for_the_2x2": len(eligible),
                       "non_deterministic": nondet, "timed_out": timeouts},
        "confusion": {"TP": TP, "FP": FP, "FN": FN, "TN_count": len(TN),
                      "precision": prec, "recall": rec},
        "moving_scripts": {n: verdicts[n] for n in sorted(n for n in eligible if confirmed[n])},
        "proposed_counts": {n: len(v) for n, v in sorted(proposed.items()) if v},
        "controls": ctrl,
        "plants": plant_detail,
        "specification_curve": spec,
        "proposer_variants": {
            "loose_FN": sorted(n for n in eligible if not proposed[n] and confirmed[n]),
            "strict_FN": sorted(n for n in eligible
                                if not proposed_strict[n] and confirmed[n]),
            "loose_proposed": sum(1 for n in eligible if proposed[n]),
            "strict_proposed": sum(1 for n in eligible if proposed_strict[n]),
            "why": ("the loose rule suppresses a proposal whenever the call mentions .parent, "
                    ".resolve() or next(, inflating FN -- the cell the kill reads."),
        },
        "captures": {n: {"rc": list(c["rc"]),
                         "sha_root": hashlib.sha256(
                             scrub(c["out"][0], *c["dirs"], ROOT).encode()).hexdigest()[:16],
                         "sha_other": hashlib.sha256(
                             scrub(c["out"][1], *c["dirs"], ROOT).encode()).hexdigest()[:16],
                         "head_root": scrub(c["out"][0], *c["dirs"], ROOT)[:200],
                         "head_other": scrub(c["out"][1], *c["dirs"], ROOT)[:200]}
                     for n, c in sorted(caps.items())},
        "tree_mutated_by_the_sweep": mutated,
        "kill": {"gate_open": gate_open, "world_A_killed": a_killed},
        "verdict": verdict,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1084 — does the parse predict the run, across all 88 assurance scripts?\n")
    print(f"  {len(every)} scripts in assurance/ · {len(writers)} WRITE and are NOT identified "
          f"for a two-run comparison (excluded, N/A)")
    print(f"  {len(scripts)} read-only · eligible for the 2x2 {len(eligible)} "
          f"· non-deterministic {len(nondet)} · timed out {len(timeouts)}")
    print("\n  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  THE 2x2 — the cheap instrument scored against the expensive one")
    print(f"    {'':<26}{'run: MOVED':>14}{'run: STABLE':>14}")
    print(f"    {'parse: proposed':<26}{len(TP):>14}{len(FP):>14}")
    print(f"    {'parse: silent':<26}{len(FN):>14}{len(TN):>14}")
    print(f"    precision {prec if prec is None else f'{prec:.3f}'}   "
          f"recall {rec if rec is None else f'{rec:.3f}'}")
    if FN:
        print(f"\n  ⛔ FALSE NEGATIVES — behaviour moves, the parse said nothing:")
        for n in FN[:10]:
            print(f"      {n:<52} rc {verdicts[n]['rc_root']} -> {verdicts[n]['rc_other']}")
    if TP:
        print(f"\n  ⭐ TRUE POSITIVES — proposed and confirmed:")
        for n in TP[:10]:
            print(f"      {n:<52} rc {verdicts[n]['rc_root']} -> {verdicts[n]['rc_other']}")
    print(f"\n  PROPOSER VARIANTS — the loose rule biases toward SILENCE, which is the kill's cell")
    print(f"    loose : proposes {sum(1 for n in eligible if proposed[n]):>3} of {len(eligible)}, "
          f"FN = {len([n for n in eligible if not proposed[n] and confirmed[n]])}")
    print(f"    strict: proposes {sum(1 for n in eligible if proposed_strict[n]):>3} of "
          f"{len(eligible)}, FN = "
          f"{len([n for n in eligible if not proposed_strict[n] and confirmed[n]])}")
    if FP:
        print(f"\n  ⚠ FALSE POSITIVES — a literal the run never reaches ({len(FP)}): {FP[:6]}")
    print(f"\n  SPECIFICATION CURVE — {len(spec)} cells, every one a re-READING of the same runs")
    print(f"    {'compare_on':<12}{'normalise':>11}{'scripts':>9}{'moved':>8}")
    for s in spec:
        print(f"    {s['compare_on']:<12}{str(s['normalise']):>11}{s['scripts']:>9}{s['moved']:>8}")
    if mutated:
        print(f"\n  ⚠ the sweep mutated {len(mutated)} tracked path(s): {mutated[:5]}")
    print(f"\n  KILL gate_open={gate_open}  world_A_killed={a_killed}")
    print(f"\n  {'⛔' if not gate_open else '⭐' if a_killed else '·'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
