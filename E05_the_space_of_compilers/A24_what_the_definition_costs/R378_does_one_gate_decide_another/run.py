"""R378 — an INTERVENTION: does one gate's verdict decide another gate's verdict?

R377 established that `attack_every_check` is deterministic at a fixed commit (8/8 identical) and
that its 1->2->1 movement is therefore TREE-STATE dependence. It labelled the state variable as
[HYPOTHESIS]: whether `every_round_reaches_the_readme` -- one of the six checks the subject plants
into -- is itself passing. That was explicitly untested, and an inline observation in its own
direction was reported as suggestive rather than as evidence.

This is the controlled version, and it is an INTERVENTION rather than an observation. That matters
beyond this one check: `interventionally validated` is a line this campaign's register has marked
N/A in almost every round, because the objects were fixed releases. Here the object is the
repository, which I can actually set.

⛔ WHY THE ANSWER CHANGES WHAT HAPPENS NEXT, not just what is believed. Ten gates are red. If a
   gate's verdict depends on ANOTHER gate's verdict, they are not ten independent problems, the
   repair order matters, and fixing them in the wrong order will make some flip back. If they are
   independent, the ten can be worked in any order by anyone.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. The subject's exit
   is free to be identical across all three cells. And the PLACEBO is what makes a positive result
   mean anything: without it, "the exit changed after I edited README.md" is equally explained by
   `any edit moves it`, which would be a fact about the file rather than about the coupling.

⛔ AND THE PLACEBO ITSELF MUST BE SHOWN TO HAVE HAPPENED. `attack_every_check`'s own output taught
   this the hard way -- it prints `PLANT INVALID -- the mutation changed nothing` for two of its six
   subjects. A placebo edit that silently no-ops proves exactly nothing while looking like a clean
   negative. So the placebo asserts BOTH that the file's bytes changed AND that the gate's verdict
   did not.

ESTIMAND        the exit code of `attack_every_check` under three states of README.md, each
                measured R times:
                  A  BASE     the file as committed
                  B  KNOCKOUT the newest round's link line removed, which flips
                              `every_round_reaches_the_readme` from 0 to nonzero
                  C  PLACEBO  a byte-level edit that leaves every gate's verdict unchanged
                Contrast of interest: exit(B) - exit(A), with exit(C) - exit(A) as the null.

IDENTIFICATION  Identified at this commit, for this pair of checks. NOT identified: whether other
                pairs are coupled -- that is a 10x10 question and this is one cell of it. NOT
                identified: the mechanism inside the subject, only that the coupling exists or does
                not.

SCOPE           population: 3 README states x R runs · instrument: process exit codes and the
                subject's own verdict rows · baseline: cell A · regime: HEAD, live tree.

WORLDS
  W-GATE-COUPLED  exit(B) != exit(A) and exit(C) == exit(A). The subject's verdict depends on
                  ANOTHER GATE'S VERDICT. The ten reds are a dependency graph, not a list, and
                  repair order matters.
  W-ANY-EDIT      exit(C) != exit(A) as well. Then the dependence is on the FILE, not on the gate's
                  status, and R377's hypothesis is refuted while the flicker is still explained.
  W-UNCOUPLED     exit(B) == exit(A). The knockout does not move the subject at all, R377's
                  hypothesis is dead, and the state variable is something neither round has named.

PREDICTION MATRIX
  W-GATE-COUPLED -> A==C, B differs
  W-ANY-EDIT     -> A differs from BOTH B and C
  W-UNCOUPLED    -> A==B (whatever C does)

PRE-REGISTERED KILL -- conditional on the controls, never on a difference alone.
    if knockout_took_effect and placebo_really_edited and placebo_left_gates_alone
       and tree_restored_every_time:
        if exit(B) != exit(A) and exit(C) == exit(A)  -> W-GATE-COUPLED
        elif exit(C) != exit(A)                       -> W-ANY-EDIT
        else                                          -> W-UNCOUPLED
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  KNOCKOUT (+)   `every_round_reaches_the_readme` must read 0 in A and NONZERO in B. If it does not,
                 the intervention never happened and the whole round is an examined-nothing.
  PLACEBO EDIT   the file's sha256 in C must DIFFER from A -- otherwise the placebo is a no-op, and
                 a no-op that "changes nothing" is the plant-invalid failure wearing a control's
                 clothes.
  PLACEBO NULL   `every_round_reaches_the_readme` must read the SAME in C as in A. A placebo that
                 moves the gate is a second knockout, not a null.
  RESTORE        README.md is restored from git after every cell and verified byte-identical to the
                 committed version. A round that leaves the repository edited is not a measurement.
  REPEAT         R runs per cell. R377 measured this subject deterministic, but a design that
                 assumes what a previous round measured, without re-measuring, inherits its scope.

MULTIPLICITY    3 cells x R runs, all printed. No selection, no threshold on a p-value.
SEEDS           none -- every cell is a deterministic file state.
ARTIFACT        results/r378_intervention.json with the source hash.

IMPOSSIBLE HERE
  the other 45 pairs      -- 10 red gates is a 10x10 dependency question; this measures ONE cell,
                             chosen because R377 named it. A claim about the graph needs the graph.
  the mechanism inside    -- this establishes coupling, not how.
  a second release        -- one release.

EXIT
    0  controls hold and the pair is classified
    1  a control misbehaved, or the tree could not be restored -- UNVERIFIED
    2  the tree was dirty at the start, or an input is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
PY = ROOT / ".venv" / "bin" / "python"
README = ROOT / "README.md"
SUBJECT = "attack_every_check"
COUPLED = "every_round_reaches_the_readme"
R = 3
OWN = "E05_the_space_of_compilers/A24_what_the_definition_costs/R378_"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def git(*a):
    return subprocess.run(["git", *a], cwd=str(ROOT), capture_output=True, text=True, timeout=300)


def dirty():
    return [l for l in git("status", "--porcelain").stdout.split("\n")
            if l.strip() and not l[3:].strip().strip('"').startswith(OWN)]


def run_check(name):
    p = subprocess.run([str(PY), str(ROOT / "assurance" / f"{name}.py")], cwd=str(ROOT),
                       capture_output=True, text=True, timeout=400)
    return p.returncode, p.stdout


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def restore_readme(orig_sha):
    git("checkout", "--", "README.md")
    return sha(README) == orig_sha


def main() -> int:
    if not PY.exists() or not README.exists():
        print("  UNRUNNABLE: interpreter or README missing. Exit 2, never 0."); return 2
    d0 = dirty()
    if d0:
        print(f"  UNRUNNABLE: the live tree is dirty ({len(d0)} path(s)). This round EDITS")
        print(f"  README.md and must start clean so the restore is verifiable. Exit 2, never 0.")
        for l in d0[:6]:
            print(f"    {l}")
        return 2

    head = git("rev-parse", "HEAD").stdout.strip()[:12]
    base_sha = sha(README)
    base_text = README.read_text()
    print(f"R378 · does one gate's verdict decide another's?   HEAD {head}, R={R}\n")
    print(f"  ⚠ THIS ROUND EDITS THE LIVE README. It is restored from git after every cell and")
    print(f"    verified byte-identical to the committed version (sha {base_sha}).\n")

    # the newest round mentioned in README, whose link line is the knockout target
    ids = sorted({m.group(1) for m in re.finditer(r"/(R\d+)_", base_text)},
                 key=lambda s: int(s[1:]))
    if not ids:
        print("  UNRUNNABLE: no round link found in README. Exit 2, never 0."); return 2
    target = ids[-1]
    lines = [l for l in base_text.split("\n") if target + "_" in l]
    if not lines:
        print(f"  UNRUNNABLE: no line mentions {target}. Exit 2, never 0."); return 2
    knock_text = "\n".join(l for l in base_text.split("\n") if target + "_" not in l)
    # PLACEBO: append a trailing blank line. Byte-different, semantically inert -- and both of
    # those are ASSERTED below rather than assumed.
    plac_text = base_text + "\n"
    print(f"  knockout target: {target}  ({len(lines)} line(s) mention it)")

    CELLS = {"A_base": base_text, "B_knockout": knock_text, "C_placebo": plac_text}
    OUT, ok_restore = {}, True
    print(f"\n    {'cell':>12}{'README sha':>14}{COUPLED[:26]:>28}{'  subject exits':>18}")
    try:
        for cell, text in CELLS.items():
            README.write_text(text)
            s = sha(README)
            crc, _ = run_check(COUPLED)
            exits = []
            for _ in range(R):
                rc, out = run_check(SUBJECT)
                exits.append(rc)
                d = dirty()
                if d:
                    git("checkout", "--", ".")
                    README.write_text(text)     # the CELL's state, not the committed one
            OUT[cell] = dict(readme_sha=s, coupled_exit=crc, subject_exits=exits)
            print(f"    {cell:>12}{s:>14}{('exit ' + str(crc)):>28}{str(exits):>18}")
    finally:
        ok_restore = restore_readme(base_sha)
        for _ in range(3):
            if not dirty():
                break
            git("checkout", "--", ".")
    print(f"\n    README restored byte-identical: {ok_restore}   tree clean: {not dirty()}")

    a, b, c = OUT["A_base"], OUT["B_knockout"], OUT["C_placebo"]
    knock_ok = (a["coupled_exit"] == 0 and b["coupled_exit"] != 0)
    plac_edit_ok = (c["readme_sha"] != a["readme_sha"])
    plac_null_ok = (c["coupled_exit"] == a["coupled_exit"])
    print(f"\n  CONTROLS")
    print(f"    KNOCKOUT (+)   `{COUPLED}` {a['coupled_exit']} in A -> {b['coupled_exit']} in B  "
          f"{'PASS' if knock_ok else 'FAIL — the intervention never happened'}")
    print(f"    PLACEBO EDIT   README sha {a['readme_sha']} -> {c['readme_sha']}  "
          f"{'PASS — really edited' if plac_edit_ok else 'FAIL — a no-op proves nothing'}")
    print(f"    PLACEBO NULL   `{COUPLED}` {a['coupled_exit']} in A -> {c['coupled_exit']} in C  "
          f"{'PASS' if plac_null_ok else 'FAIL — the placebo is a second knockout'}")
    print(f"    RESTORE        README byte-identical and tree clean  "
          f"{'PASS' if ok_restore and not dirty() else 'FAIL'}")

    ctrl_ok = knock_ok and plac_edit_ok and plac_null_ok and ok_restore and not dirty()
    ea = set(a["subject_exits"]); eb = set(b["subject_exits"]); ec = set(c["subject_exits"])

    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the cells above are silence, not a result.")
        v = "UNVERIFIED"
    elif eb != ea and ec == ea:
        print(f"  W-GATE-COUPLED — knocking out `{COUPLED}` moves `{SUBJECT}` from {sorted(ea)} to")
        print(f"  {sorted(eb)}, while a real but inert README edit leaves it at {sorted(ec)}.")
        print(f"  ⛔ So one gate's verdict DECIDES another's. The ten red gates are a DEPENDENCY")
        print(f"     GRAPH, not a list: repair order matters, and fixing them in the wrong order")
        print(f"     will make some flip back. R377's [HYPOTHESIS] is confirmed by intervention.")
        v = "W_GATE_COUPLED"
    elif ec != ea:
        print(f"  W-ANY-EDIT — the placebo moved it too ({sorted(ea)} -> {sorted(ec)}), so the")
        print(f"  dependence is on the FILE and not on the other gate's verdict. R377's")
        print(f"  [HYPOTHESIS] is REFUTED, and the flicker is still explained — by something")
        print(f"  cruder than a dependency between checks.")
        v = "W_ANY_EDIT"
    else:
        print(f"  W-UNCOUPLED — the knockout did NOT move the subject ({sorted(ea)} vs "
              f"{sorted(eb)}).")
        print(f"  R377's [HYPOTHESIS] is dead. The state variable that produced 1->2->1 is")
        print(f"  something neither round has named, and naming it is the open question.")
        v = "W_UNCOUPLED"

    print(f"\n  ⚠ SCOPE: this is ONE cell of a 10x10 question. Ten red gates admit 45 unordered")
    print(f"    pairs; this measured the pair R377 named. Nothing here says the others are coupled,")
    print(f"    and nothing here says they are not.")
    print(f"  ⚠ AND `interventionally validated` is met for this claim and this claim only — the")
    print(f"    repository is settable, which almost nothing else in this campaign has been.")

    art = dict(stamp(str(SELF)), head=head, target=target, repeats=R, cells=OUT,
               controls=dict(knockout=knock_ok, placebo_edit=plac_edit_ok,
                             placebo_null=plac_null_ok, restore=ok_restore),
               exits=dict(A=sorted(ea), B=sorted(eb), C=sorted(ec)), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r378_intervention.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
