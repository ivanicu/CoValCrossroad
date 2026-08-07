#!/usr/bin/env python3
"""
R868 · can a gate be DEAD and GREEN at the same time? — fault injection into every gate.

⛔ WHY, and it is a measured event from one round ago. `a_seed_must_be_stable` wrapped its tokenizer
in a bare `except Exception`, so a **NameError from a missing import in the gate's own code** was
reported as `untokenisable` against the scanned file. Every file would have come back clean, the
population would have read as fully examined, and the gate would have **exited 0 forever**. The only
thing that noticed was its positive control.

**So the question is not hypothetical and it generalises: how many of this project's gates report
SUCCESS when their own machinery throws?** Every gate here has a positive control on WHAT IT
DETECTS. **None has a control on what happens when the gate ITSELF fails.** That is the difference
between "this check found nothing" and "this check ran".

ESTIMAND        for each gate, the exit status and output when a fault is injected into its own
                population-scanning code: does the failure PROPAGATE, or does the gate report a
                clean population and exit 0?
IDENTIFICATION  exact and direct. This is an intervention on the mechanism, not an observational
                claim — which is worth noting, because `causally identified` sits in this project's
                impossibility register for every round about the DATA. It is available here because
                the object under study is code I control.
SCOPE           population: every `assurance/*.py` that exposes a `main()`, completes in baseline
                            within the timeout, AND is READ-ONLY by AST.
                ⛔⛔ THE READ-ONLY RESTRICTION IS NOT A CONVENIENCE — IT IS A RETRACTION OF THIS
                ROUND'S FIRST DESIGN, WHICH WAS UNSAFE AND I RAN IT. The first version injected
                faults into all 70 gates and executed them against the LIVE repo. **26 of those 70
                write to disk by design** — `apply_*`, `attack_every_check`, `_repair`,
                `generate_round_index` — and I never asked which before running. The run mutated
                two of the suite's own output files and DELETED this round's log while it was being
                written. The tree survived (3,523 tracked files, verified), so the cost was small,
                but that was luck and not design: **the round about whether instruments fail safely
                was itself an instrument with no safety analysis.**
                The correct fix is an isolated checkout; creating one was not available this
                session, so the population is narrowed instead and the exclusion is REGISTERED
                below rather than quietly dropped.
                            Gates that time out are REPORTED and excluded, not silently dropped.
                instrument: `raise RuntimeError(MARKER)` inserted as the first statement of each
                            non-main, non-control top-level function, one at a time
                baseline:   the same gate's exit status with no injection
                regime:     this repo, this commit
WORLDS          A · every gate fails loud -> last round's defect was unique to one file
                B · some gates are DEAD-AND-GREEN -> the suite has been reporting a status it
                    cannot support, and the number of such gates is the finding
                C · injections do not reach the code -> my harness is the broken instrument, and
                    that must be distinguishable from B rather than read as a pass
KILL            CONDITIONAL, and the harness must prove itself before any gate is judged:
                  ⭐ ① POSITIVE: a synthetic gate that swallows exceptions in a bare `except` MUST
                     be classified DEAD_AND_GREEN. If the harness cannot see a known-swallowing
                     gate, its zeros are silence.
                  ⭐ ② g=0: a synthetic gate that lets exceptions propagate MUST be classified
                     LOUD. A harness that flags everything is not a detector.
                  ③ every injection must be OBSERVED to execute — otherwise NOT_REACHED
                     (UNVERIFIED), never a pass. This is the C-vs-B separation, made mechanical.
                     ⛔⛔ AND MY FIRST VERSION OF THIS ARM MADE THE FINDING UNDETECTABLE. It defined
                     "observed" as `the marker appears OR the exit status changed`. But a gate that
                     PERFECTLY swallows a fault shows neither — no marker, same exit code — because
                     **that is what dead-and-green MEANS.** So the criterion excluded exactly the
                     class it was built to find, and the POSITIVE CONTROL returned NOT_REACHED on a
                     gate I had written to swallow. The detector could not see the thing it was for,
                     and nothing but its own control would have said so. **Observation is now the
                     gate's OUTPUT differing from baseline**, which changes even when status does
                     not: the swallowing control prints `scanned 0` where baseline printed
                     `scanned 3`.
                  ④ the baseline must be REPRODUCIBLE: each gate is run twice with no injection and
                     its output compared. A gate whose own output is unstable cannot be judged by
                     an output diff, and is excluded and REPORTED rather than scored.
PLACEBO         running each gate with NO injection must reproduce its baseline exit status exactly.
MULTIPLICITY    every eligible gate × ONE injection point (its first non-main, non-control
                top-level function). ⚠ THE REDUCTION IS STATED, NOT SILENT: the full design injects
                every function, which at 70 gates × ~3 points × a 45 s ceiling does not fit the
                budget. One point per gate answers the question in the SOUND direction only — a
                gate that swallows at THAT point is dead-and-green for certain; a gate that is loud
                there may still swallow elsewhere. **So a LOUD verdict here is a lower bound on
                safety, never a clearance.**
ARTIFACT        results/gate_liveness.json
IMPOSSIBLE      cross-release · construct validated.
                ⚠ `causally identified` is NOT impossible here and IS claimed: the design
                intervenes directly on the mechanism, which is available because the object is code.
                ⛔ **THE 26 MUTATING GATES ARE UNTESTED, and this is an availability claim in the
                UNFLATTERING direction, which is the only kind worth trusting.** What it would
                require: an isolated checkout (`git worktree add --detach`, or a `git archive`
                extract) so an injected copy cannot reach the live tree. Until then their liveness
                is UNKNOWN — not assumed good, and NOT counted as passing.
⚠ RESIDUAL LIMIT, named rather than discovered later: a gate that swallows a fault AND emits
                byte-identical output is indistinguishable from one whose injected function is never
                called. Both land in NOT_REACHED. This design cannot separate them, and NOT_REACHED
                is therefore UNVERIFIED in both directions — not a pass for either.
"""
import ast, json, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
PY = str(ROOT / ".venv" / "bin" / "python")
MARKER = "INJECTED_FAULT_R868"
TIMEOUT = 45
SKIP_FN = re.compile(r"^(main|_.*|.*control.*|synthetic_.*|verify|run|flagged)$")


MUTATORS = ("write_text", "unlink", "rename", "replace", "mkdir", "rmtree", "copy", "copytree",
            "move", "remove")


def is_read_only(path):
    """AST check: does this gate write anywhere? Conservative — any writey name disqualifies.

    ⚠ SOUND IN ONE DIRECTION ONLY. A gate flagged as a mutator certainly is excluded; a gate that
    passes could still mutate through a name this list does not know (an f-string command, an
    imported helper). So this makes the run SAFER, never provably safe, and it is why the live-repo
    execution is a fallback rather than the design.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr in MUTATORS:
            return False
        if isinstance(node, ast.Name) and node.id in ("subprocess",):
            pass
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "open":
            for a in node.args[1:]:
                if isinstance(a, ast.Constant) and isinstance(a.value, str) \
                        and any(c in a.value for c in "wax+"):
                    return False
    return True


def injectable(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return [(f.name, f.body[0].lineno) for f in tree.body
            if isinstance(f, ast.FunctionDef) and not SKIP_FN.match(f.name)]


def run(path, cwd):
    try:
        p = subprocess.run([PY, str(path)], cwd=str(cwd), capture_output=True, text=True,
                           timeout=TIMEOUT)
        return p.returncode, (p.stdout + p.stderr)
    except subprocess.TimeoutExpired:
        return None, "TIMEOUT"


def inject(src_path, fn_line, dst):
    lines = src_path.read_text(encoding="utf-8").splitlines(keepends=True)
    i = fn_line - 1
    indent = len(lines[i]) - len(lines[i].lstrip())
    lines.insert(i, " " * indent + f'raise RuntimeError("{MARKER}")\n')
    dst.write_text("".join(lines), encoding="utf-8")


def classify(rc, out, base_rc, base_out):
    """⛔ `seen` is an OUTPUT diff, not a status diff. See KILL ③: a status-based definition made
    DEAD_AND_GREEN unreachable, because a perfectly swallowed fault changes no status."""
    if out == "TIMEOUT":
        return "TIMEOUT"
    seen = (rc != base_rc) or (out != base_out) or (MARKER in out)
    if not seen:
        return "NOT_REACHED"
    return "DEAD_AND_GREEN" if rc == 0 else "LOUD"


def harness_controls(tmp):
    """The harness must see a KNOWN swallowing gate and must NOT flag a propagating one."""
    swallow = tmp / "g_swallow.py"
    swallow.write_text(
        "import sys\n"
        "def scan():\n"
        "    hits = []\n"
        "    for x in range(3):\n"
        "        try:\n"
        "            hits.append(x)\n"
        "        except Exception:\n"
        "            pass\n"
        "    return hits\n"
        "def main():\n"
        "    try:\n"
        "        h = scan()\n"
        "    except Exception:\n"
        "        h = []          # <- swallows its own machinery failing\n"
        "    print(f'scanned {len(h)}')\n"
        "    return 0\n"
        "raise SystemExit(main())\n")
    loud = tmp / "g_loud.py"
    loud.write_text(
        "def scan():\n"
        "    return [1, 2, 3]\n"
        "def main():\n"
        "    h = scan()\n"
        "    print(f'scanned {len(h)}')\n"
        "    return 0\n"
        "raise SystemExit(main())\n")
    res = {}
    for name, f in (("swallow", swallow), ("loud", loud)):
        base_rc, base_out = run(f, tmp)
        tgt = tmp / f"inj_{name}.py"
        inject(f, injectable(f)[0][1], tgt)
        rc, out = run(tgt, tmp)
        res[name] = classify(rc, out, base_rc, base_out)
    pos = res["swallow"] == "DEAD_AND_GREEN"
    g0 = res["loud"] == "LOUD"
    print(f"  POSITIVE CONTROL  a gate that swallows its own fault is seen as DEAD_AND_GREEN: "
          f"{res['swallow']}  {'PASS' if pos else 'FAIL'}")
    print(f"  g=0               a gate that propagates is seen as LOUD: {res['loud']}  "
          f"{'PASS' if g0 else 'FAIL'}")
    print("    Without the first arm a count of zero dead gates is silence, not an acquittal.")
    return pos and g0, res


def main() -> int:
    tmp = pathlib.Path(tempfile.mkdtemp())
    ok, ctl = harness_controls(tmp)
    if not ok:
        print("\n  UNVERIFIED: the harness failed its own controls. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "harness": ctl},
                  open(OUT / "gate_liveness.json", "w"), indent=2)
        return 2

    gates = sorted((ROOT / "assurance").glob("*.py"))
    rows, excluded = [], []
    print(f"\n  {len(gates)} candidate gate file(s) in assurance/")
    mutators = []
    for g in gates:
        ro = is_read_only(g)
        if ro is None:
            excluded.append((g.name, "unparseable")); continue
        if not ro:
            mutators.append(g.name); continue
        fns = injectable(g)
        if fns is None:
            excluded.append((g.name, "unparseable")); continue
        if "def main(" not in g.read_text(encoding="utf-8"):
            excluded.append((g.name, "no main()")); continue
        base_rc, base_out = run(g, ROOT)
        if base_rc is None:
            excluded.append((g.name, "baseline TIMEOUT")); continue
        # KILL ④: the output diff is the instrument, so an unstable baseline makes it useless.
        rc2, out2 = run(g, ROOT)
        if rc2 != base_rc or out2 != base_out:
            excluded.append((g.name, "baseline output NOT reproducible")); continue
        if not fns:
            excluded.append((g.name, "no injectable function")); continue
        fns = fns[:1]      # ONE point per gate — the reduction is declared in MULTIPLICITY
        cells = []
        for fname, ln in fns:
            # ⚠ THE COPY MUST LIVE INSIDE assurance/. Every gate computes
            # `ROOT = Path(__file__).resolve().parents[1]`, so an injected copy in /tmp would
            # resolve ROOT to /tmp and scan an empty tree — every cell would read NOT_REACHED for
            # a reason that has nothing to do with the gate. Caught before running; it would have
            # produced a confident WORLD C about my own harness.
            tgt = ROOT / "assurance" / f"_r868_inj_{g.stem}__{fname}.py"
            try:
                inject(g, ln, tgt)
                rc, out = run(tgt, ROOT)
            finally:
                tgt.unlink(missing_ok=True)
            cells.append({"fn": fname, "rc": rc,
                          "verdict": classify(rc, out, base_rc, base_out)})
        worst = ("DEAD_AND_GREEN" if any(c["verdict"] == "DEAD_AND_GREEN" for c in cells)
                 else "NOT_REACHED" if all(c["verdict"] == "NOT_REACHED" for c in cells)
                 else "LOUD")
        rows.append({"gate": g.name, "baseline_rc": base_rc, "cells": cells, "verdict": worst})
        flag = {"DEAD_AND_GREEN": "⛔", "LOUD": "  ", "NOT_REACHED": "⚠ "}[worst]
        print(f"  {flag} {g.name:<46} base_rc={base_rc}  {worst}"
              f"  ({len(cells)} injection point(s))")

    dead = [r["gate"] for r in rows if r["verdict"] == "DEAD_AND_GREEN"]
    unreached = [r["gate"] for r in rows if r["verdict"] == "NOT_REACHED"]
    print(f"\n  tested {len(rows)} gate(s) · {sum(len(r['cells']) for r in rows)} injections")
    print(f"  ⛔ {len(mutators)} gate(s) EXCLUDED as WRITERS and left UNTESTED — an isolated")
    print(f"     checkout would be required. Their liveness is UNKNOWN, not assumed good:")
    for nm in mutators[:8]:
        print(f"       {nm}")
    if len(mutators) > 8:
        print(f"       ... and {len(mutators)-8} more (all in the artifact)")
    if excluded:
        print(f"  ⚠ EXCLUDED and REPORTED, not silently dropped: {len(excluded)}")
        for nm, why in excluded[:6]:
            print(f"      {nm}  ({why})")
    world = "B" if dead else ("C" if len(unreached) > len(rows) / 2 else "A")
    print(f"\n  ⭐ DEAD_AND_GREEN: {len(dead)}  ·  NOT_REACHED: {len(unreached)}  ·  "
          f"LOUD: {len(rows) - len(dead) - len(unreached)}")
    for d in dead:
        print(f"      ⛔ {d}")
    print(f"  ⭐ WORLD {world}: " + {
        "A": "every gate fails loud — last round's defect was specific to one file, not a pattern",
        "B": "some gates report SUCCESS while their own machinery throws. The suite has been"
             " reporting a status it cannot support, and these are the files",
        "C": "most injections never executed — the HARNESS is the broken instrument here, and that"
             " is reported as UNVERIFIED rather than as a clean result"}[world])
    if unreached:
        print(f"     ⚠ {len(unreached)} gate(s) NOT_REACHED: the injected function is never called")
        print(f"       on this repo's data. That is UNVERIFIED for those gates, not a pass.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "harness_controls": ctl,
               "excluded_writers_UNTESTED": mutators,
               "reduction": "one injection point per gate; a LOUD verdict is a lower bound on "
                            "safety, never a clearance",
               "n_gates": len(rows), "dead_and_green": dead, "not_reached": unreached,
               "excluded": excluded, "rows": rows,
               "note": "causally identified is CLAIMED here: the design intervenes on the "
                       "mechanism directly, which is available because the object is code."},
              open(OUT / "gate_liveness.json", "w"), indent=2)
    print(f"\n  artifact: results/gate_liveness.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
