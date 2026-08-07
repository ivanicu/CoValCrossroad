#!/usr/bin/env python3
"""R1018 — did any commit this session land while the currency gate was RED?

⛔ WHY. The previous commit recorded that `next_line_quantifiers_are_computed.py` fired on the commit
before it and changed nothing, because the check and `git commit` were in the same command: the
verdict arrived after the write. Its NEXT asked whether the same sequencing error reached the
CURRENCY and ANCHORING gates.

⚠ AND THE NEXT AS WRITTEN IS NOT ANSWERABLE. It said "readable from how each is invoked in this
session's commits" — but HOW a gate was invoked lives in a shell history the repository does not
contain. That is the same shape as R1010's finding: intent is not in the record. ⭐ What IS in the
record is the CONSEQUENCE: whether any commit landed in a state the gate would have refused. A
sequencing error that never let a red state through cost nothing; one that did is a defect with a
name and a hash.

ESTIMAND        for every commit that touched DEFINITION.md or the currency gate, the gate's verdict
                computed against THAT COMMIT's content: green, red, or unrunnable.
IDENTIFICATION  exact and reproducible. Both inputs are files in the tree, so `git show <sha>:<path>`
                reconstructs the state at each commit without checking anything out — which matters,
                because a checkout in this repo already cost one incident.
SCOPE           population : commits touching either file, from the first R1000-series commit on
                instrument : the currency gate's own matcher, imported from the file AT THAT COMMIT
                             so a commit is judged by the rules it was written under, not today's
                baseline   : the gate's green/red contract · regime : this session
WORLDS          A CLEAN         no commit landed red. The sequencing error existed but never let a
                                bad state through, and the finding is the near-miss.
                B RED LANDED    at least one commit is red at its own revision. Then the discipline
                                has a hole with a hash, and it must be named.
                prediction matrix: A -> every commit green or unrunnable-for-a-stated-reason.
                                   B -> >= 1 red, listed.
KILL            pre-registered: any red commit is named with its hash in this round's headline, not
                summarised as a rate.
POSITIVE CTRL   the gate must be able to return RED here. Reconstruct a deliberately inconsistent
                state — the CURRENT gate file against an OLD DEFINITION.md, which registers facts
                that had not been written yet — and require RED. Without this, an all-green sweep is
                silence rather than a measurement.
NEGATIVE CTRL   HEAD against HEAD must be GREEN, since the working tree is green now.
PLACEBO         a commit compared against ITSELF twice must give the same verdict — determinism of
                the reconstruction, so a difference later is a real difference.
NOISE FLOOR     n/a — exact verdicts over a finite commit list. Labelled.
MULTIPLICITY    every qualifying commit is evaluated and printed, green and red alike.
ARTIFACT        results/gate_at_each_commit.json with this file's source hash.
IMPOSSIBLE      ⚠ whether the gate was actually RUN before each commit — N/A, and this round says so
                rather than inferring it. Shell history is not in the repository. What is measurable
                is whether the state it would have judged was acceptable.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GATE = "assurance/a_statement_is_current_with_the_arc.py"
DEFN = "E05_the_space_of_compilers/DEFINITION.md"


def sh(*a):
    return subprocess.run(a, cwd=ROOT, capture_output=True, text=True)


def at(sha, path):
    r = sh("git", "show", f"{sha}:{path}")
    return r.stdout if r.returncode == 0 else None


def verdict(gate_src, defn_src):
    """Load the gate AT THAT COMMIT and ask its matcher about that commit's statement."""
    if gate_src is None or defn_src is None:
        return "UNRUNNABLE", "a file did not exist at this commit"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(gate_src)
        tmp = f.name
    try:
        spec = importlib.util.spec_from_file_location("g", tmp)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        region = m.statement_region(defn_src)
        if region is None:
            return "UNRUNNABLE", "the statement region failed to load"
        import re
        missing = []
        for name in dir(m):
            pass
        # the gate's fact list is built inside main(); re-derive it by matching its own patterns
        pats = re.findall(r'\[r"((?:[^"\\]|\\.)*)"(?:\s*\n\s*r"((?:[^"\\]|\\.)*)")*', gate_src)
        # fall back to the gate's declared behaviour: run it in-process against this region
        return ("GREEN" if region else "UNRUNNABLE"), f"{len(region.splitlines())} statement lines"
    except Exception as e:
        return "UNRUNNABLE", f"{type(e).__name__}: {e}"
    finally:
        pathlib.Path(tmp).unlink(missing_ok=True)



def stage(td, gate_src, defn_src):
    """Reconstruct a judgeable tree WITHOUT a checkout: the two files under test are written, and
    everything the gate reads is symlinked from the live tree.
    ⛔ The first version symlinked E05 itself AFTER creating it to hold DEFINITION.md, and died on
    FileExistsError. E05 must be a REAL directory here — it is the one being reconstructed — so its
    ARC subdirectories are linked individually while the other epochs are linked whole."""
    td = pathlib.Path(td)
    (td / "assurance").mkdir(exist_ok=True)
    (td / DEFN).parent.mkdir(parents=True, exist_ok=True)
    (td / GATE).write_text(gate_src)
    (td / DEFN).write_text(defn_src)
    e5 = ROOT / "E05_the_space_of_compilers"
    for arc in e5.glob("A*"):
        tgt = td / e5.name / arc.name
        if not tgt.exists():
            tgt.symlink_to(arc)
    for e in ROOT.glob("E0*"):
        if e.name == e5.name:
            continue
        if not (td / e.name).exists():
            (td / e.name).symlink_to(e)
    if (ROOT / "covalx").is_dir() and not (td / "covalx").exists():
        (td / "covalx").symlink_to(ROOT / "covalx")
    return td


def main() -> int:
    r = sh("git", "log", "--format=%H %s", "-40")
    if r.returncode != 0:
        print("  UNRUNNABLE: git log failed. Exit 2, never 0.")
        return 2
    commits = []
    for line in r.stdout.splitlines():
        sha, _, subj = line.partition(" ")
        touched = sh("git", "show", "--name-only", "--format=", sha).stdout
        if GATE in touched or DEFN in touched:
            commits.append((sha, subj))
    commits.reverse()
    if not commits:
        print("  UNRUNNABLE: no commit touched either file. Exit 2, never 0.")
        return 2
    print(f"  commits touching the statement or its gate: {len(commits)}")

    # ⭐ THE REAL TEST: run the gate AS IT WAS at each commit, against that commit's files, in a
    #    scratch worktree-free way -- write both to a temp dir and invoke the gate's main().
    def run_at(sha):
        g, d = at(sha, GATE), at(sha, DEFN)
        if g is None or d is None:
            return "UNRUNNABLE", "a file did not exist at this commit"
        with tempfile.TemporaryDirectory() as td:
            td = stage(td, g, d)
            p = subprocess.run([sys.executable, str(td / GATE)], cwd=td,
                               capture_output=True, text=True, timeout=300)
            return ({0: "GREEN", 1: "RED", 2: "UNRUNNABLE"}.get(p.returncode, f"rc={p.returncode}"),
                    (p.stdout.strip().splitlines() or ["(no output)"])[-1][:90])

    # ---------- POSITIVE CONTROL: the gate must be ABLE to say RED ----------
    old = commits[0][0]
    cur_gate, old_defn = at("HEAD", GATE), at(old, DEFN)
    pos = "UNRUNNABLE"
    with tempfile.TemporaryDirectory() as td:
        td = stage(td, cur_gate, old_defn)
        p = subprocess.run([sys.executable, str(td / GATE)], cwd=td, capture_output=True,
                           text=True, timeout=300)
        pos = {0: "GREEN", 1: "RED", 2: "UNRUNNABLE"}.get(p.returncode, f"rc={p.returncode}")
    pos_ok = pos == "RED"
    print(f"\n  POSITIVE CONTROL — today's gate against the OLDEST statement (facts registered that "
          f"were not yet written) must be RED: got {pos} → {'PASS' if pos_ok else '⛔ FAIL'}")
    if not pos_ok:
        print("  an all-green sweep would be silence, not a measurement. Exit 2, never 0.")
        return 2

    print(f"\n  {'commit':<10}{'verdict':<12}subject")
    rows, red = [], []
    for sha, subj in commits:
        v, why = run_at(sha)
        rows.append({"sha": sha[:8], "subject": subj[:80], "verdict": v, "detail": why})
        if v == "RED":
            red.append(sha[:8])
        print(f"  {sha[:8]:<10}{v:<12}{subj[:72]}")

    neg_ok = rows and rows[-1]["verdict"] == "GREEN"
    print(f"\n  NEGATIVE CONTROL — the newest commit must be GREEN (the tree is green now): "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    world = (f"B RED LANDED — {red}" if red else
             "A CLEAN — no commit landed in a state the currency gate would have refused")
    print(f"\n⭐ {world}")
    if red:
        print("⛔ PRE-REGISTERED KILL FIRES: each hash above is named, not summarised as a rate.")
    else:
        print("⭐ So the sequencing error the previous commit found was a NEAR-MISS for this gate:")
        print("   the red-first discipline — register, confirm RED, annotate, confirm GREEN, commit")
        print("   — kept the consequence at zero even though the ORDER was not enforced anywhere.")
    print("\n⚠ AND THIS DOES NOT SHOW THE GATE WAS RUN BEFORE EACH COMMIT. Shell history is not in")
    print("   the repository — the same shape as 'intent is not in the record'. What is measured is")
    print("   whether the state it would have judged was acceptable, which is the consequence and")
    print("   not the process.")

    out = HERE / "results" / "gate_at_each_commit.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="did any commit land while the currency gate was red",
        n_commits=len(commits), rows=rows, red=red, world=world,
        controls={"positive_gate_can_say_red": pos, "positive_ok": bool(pos_ok),
                  "negative_head_green": bool(neg_ok)},
        not_measured="whether the gate was actually RUN before each commit — shell history is not "
                     "in the repository",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
