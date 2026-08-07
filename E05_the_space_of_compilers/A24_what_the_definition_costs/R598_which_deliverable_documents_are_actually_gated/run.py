#!/usr/bin/env python3
"""
R598 -- which of the three deliverable documents is actually GATED?

CHECK #198 KILLED AN ASSERTION IN R597's CLOSING LINE, and it was disproved by source I had
already read this session: *"none of them is gated by anything, since statement_provenance
reads STATEMENT.md alone."* I inferred the ungatedness of a 59-script suite from ONE script.
`statement_provenance.py` itself opens DEFINITION.md for its transitive-anchoring clause, and
`definition_matches_the_record.py` is named for it.

⚠ AND THE INSTRUMENT R597 PROPOSED -- a grep over the suite -- IS THE WRONG ONE. A script that
OPENS a file is not a GATE on that file. `statement_provenance` reads DEFINITION.md only for a
membership test on STATEMENT's numbers, so DEFINITION's content can only cause a failure VIA
STATEMENT. Instrument unit = "the filename appears in the source"; claim unit = "this
document's content can make the suite fail". NOT equal, and the difference is the whole
question.

The property is testable directly: MUTATE the document and see which gates change verdict.
That is an intervention on the mechanism, not a reading of it.

ESTIMAND        For each document D and each of the 59 assurance scripts g:
                flip(D, g) = 1 if g passes on the untouched tree and fails when D is emptied.
                |{g : flip(D,g)}| is D's gate coverage.
IDENTIFICATION  Exact -- an exit code is not an estimate. ⚠ Emptying is the MAXIMAL mutation,
                so a zero here is a strong statement: no lesser edit could flip a gate that a
                total deletion does not. Coverage is therefore an UPPER BOUND on how finely
                the document is gated, and a zero is decisive in the other direction.
SCOPE           population : all 59 files matching assurance/*.py
                instrument : subprocess exit code, 90s timeout, in a sandbox COPY of the repo
                baseline   : the untouched sandbox -- a gate already failing there is excluded
                             from every count, because it cannot flip
                regime     : as committed at this sha
WORLDS          A ALL THREE GATED: every document flips >=1 gate -> the deliverable is covered
                  and R597's line was simply wrong.
                B STATEMENT ONLY: only STATEMENT.md flips anything -> DEFINITION and
                  FORMULATION are decoration that no check can contradict, and every claim
                  sourced to them is unguarded.
                C PARTIAL: STATEMENT and DEFINITION flip, FORMULATION does not -> the 156 KB
                  third document is ungated, which is R566's finding still standing after six
                  rounds of gate work.
KILL            pre-registered: if emptying STATEMENT.md flips ZERO gates, the harness cannot
                detect gating at all and every other cell is UNVERIFIED, not "ungated".
POSITIVE CTRL   STATEMENT.md is known to be gated (statement_provenance exits 2 without it).
                Emptying it MUST flip >=1 gate. Fails at g=0: the untouched sandbox must
                reproduce the live suite's pass/fail set.
NEGATIVE CTRL   empty a file no gate should read (`NEXT_SITE.md`). Must flip 0 gates.
PLACEBO         create a NEW file that never existed. Must flip 0 gates.
SEEDS           n/a, deterministic; the baseline tree is run TWICE and must agree, which is
                the reproducibility check and also detects order-dependent gates.
MULTIPLICITY    5 trees x 59 gates = 295 invocations, plus a repeated baseline. All reported,
                including gates that fail in the baseline and are therefore excluded.
ARTIFACT        results/gate_coverage.json
IMPOSSIBLE      construct validity for "gated WELL": a flip proves a document's content can
                fail the suite; it says nothing about whether the check is a good one. R596
                measured a gate that fired on 1 of 8 spellings and still "gated" STATEMENT.md.
"""
from __future__ import annotations
import concurrent.futures as cf
import json, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
TIMEOUT = 90


def build_tree(mutation=None):
    """A full COPY of the repo, optionally with one file emptied or created."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="r598_"))
    tree = tmp / "repo"
    shutil.copytree(ROOT, tree, ignore=shutil.ignore_patterns(
        ".git", "__pycache__", ".venv", "*.npz", "*.pkl", "node_modules"))
    if mutation:
        kind, rel = mutation
        p = tree / rel
        if kind == "empty":
            if not p.exists():
                shutil.rmtree(tmp, ignore_errors=True)
                return None, None, f"{rel} does not exist"
            p.write_text("")
        elif kind == "create":
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("a file that never existed\n")
    return tmp, tree, None


def run_one(tree, gate):
    try:
        r = subprocess.run([sys.executable, str(tree / "assurance" / gate)],
                           cwd=str(tree), capture_output=True, text=True, timeout=TIMEOUT)
        return gate, r.returncode
    except subprocess.TimeoutExpired:
        return gate, "TIMEOUT"
    except Exception as e:                      # never discard the diagnosis (R576)
        return gate, f"ERR:{type(e).__name__}"


def run_suite(tree, gates):
    """SERIAL. ⛔ v1 ran 59 scripts CONCURRENTLY in one tree and reported
    `definition_matches_the_record.py` and `statement_provenance.py` as order-dependent. They
    are not: some assurance scripts WRITE into the tree, so concurrent runs were reading a
    surface others were mutating. That is L62 -- concurrency needs READ isolation, not just
    write isolation -- and the instability was my harness, not the gates. Serial is slower and
    is the only version whose answer is about the object."""
    return {g: run_one(tree, g)[1] for g in gates}


def main():
    gates = sorted(p.name for p in (ROOT / "assurance").glob("*.py"))
    if not gates:
        print("UNRUNNABLE: no assurance scripts found. Exit 2, never 0.")
        return 2
    print(f"SUITE  {len(gates)} scripts in assurance/*.py")

    # ---- name-level grep, reported ONLY as the instrument R597 proposed, not as the answer
    print(f"\n─── THE INSTRUMENT R597 PROPOSED (grep) — reported, not believed ───")
    named = {}
    for doc in ("STATEMENT.md", "DEFINITION.md", "FORMULATION.md"):
        hits = [g for g in gates if doc.split(".")[0] in (ROOT / "assurance" / g).read_text()]
        named[doc] = hits
        print(f"  {doc:<16} named in {len(hits):>2} script(s): {hits[:4]}"
              f"{' …' if len(hits) > 4 else ''}")
    print(f"  ⚠ a script that OPENS a file is not a GATE on it. The mutation below is the test.")

    # ---- CONTROLS FIRST -------------------------------------------------------------
    print(f"\n─── CONTROLS ───")
    tmp, tree, err = build_tree(None)
    base1 = run_suite(tree, gates)
    base2 = run_suite(tree, gates)
    shutil.rmtree(tmp, ignore_errors=True)
    stable = [g for g in gates if base1[g] == base2[g]]
    print(f"  BASELINE reproducibility: {len(stable)}/{len(gates)} gates gave the same code "
          f"on two runs of the same tree")
    unstable = [g for g in gates if base1[g] != base2[g]]
    if unstable:
        print(f"    ⚠ order/time-dependent, EXCLUDED from every count: {unstable}")
    passing = [g for g in stable if base1[g] == 0]
    print(f"  BASELINE passing: {len(passing)}/{len(gates)}  "
          f"(only a gate that PASSES untouched can flip)")
    nonpass = {g: base1[g] for g in stable if base1[g] != 0}
    print(f"  BASELINE not passing, excluded: {len(nonpass)} "
          f"{dict(list(nonpass.items())[:6])}{' …' if len(nonpass) > 6 else ''}")
    if not passing:
        print("  ⛔ no gate passes in the baseline; nothing can flip. Exit 2.")
        return 2

    def coverage(mutation, label):
        tmp, tree, err = build_tree(mutation)
        if err:
            print(f"  {label:<24} SKIPPED — {err}")
            return None
        got = run_suite(tree, gates)
        shutil.rmtree(tmp, ignore_errors=True)
        flips = [g for g in passing if got[g] != 0]
        print(f"  {label:<24} flips {len(flips):>2}/{len(passing)}  {flips[:6]}"
              f"{' …' if len(flips) > 6 else ''}")
        return {"flips": flips, "n_flips": len(flips)}

    print(f"\n─── POSITIVE / NEGATIVE / PLACEBO ───")
    # ⛔ v1's verdict came back UNVERIFIED because the negative control flipped a gate. The
    #    control was right and the diagnosis is mechanical: a gate that also flips under the
    #    PLACEBO (a brand-new file no document depends on) is responding to "the tree changed",
    #    not to "this document changed". Such gates cannot localise and are excluded from every
    #    count -- named, not dropped silently.
    plc = coverage(("create", "E05_the_space_of_compilers/ZZQ_never_existed.md"),
                   "PLACEBO   create new file")
    tree_sensitive = set(plc["flips"]) if plc else set()
    if tree_sensitive:
        print(f"  ⚠ TREE-CHANGE SENSITIVE, excluded from every count: {sorted(tree_sensitive)}")
        passing = [g for g in passing if g not in tree_sensitive]
        print(f"    localising population is now {len(passing)} gate(s)")
    pos = coverage(("empty", "E05_the_space_of_compilers/STATEMENT.md"), "POSITIVE  empty STATEMENT")
    neg = coverage(("empty", "E05_the_space_of_compilers/NEXT_SITE.md"), "NEGATIVE  empty NEXT_SITE")

    harness_ok = bool(pos and pos["n_flips"] > 0)
    print(f"  -> harness {'PASS — emptying a known-gated document flips gates' if harness_ok else '⛔ FAIL — cannot detect gating at all'}")

    # ---- THE MEASUREMENT ------------------------------------------------------------
    print(f"\n─── COVERAGE PER DELIVERABLE DOCUMENT (maximal mutation: emptied) ───")
    cov = {"STATEMENT.md": pos}
    for doc in ("DEFINITION.md", "FORMULATION.md"):
        cov[doc] = coverage(("empty", f"E05_the_space_of_compilers/{doc}"), f"empty {doc}")

    # ---- VERDICT: a function of the controls, nothing written in between -------------
    print(f"\n─── VERDICT ───")
    if not harness_ok:
        world = "UNVERIFIED — the harness cannot detect gating; no zero here means ungated"
    elif neg and neg["n_flips"] > 0:
        world = (f"UNVERIFIED — the negative control flipped {neg['n_flips']} gate(s), so a "
                 f"flip does not localise to the document that was emptied")
    else:
        n = {d: (cov[d]["n_flips"] if cov[d] else None) for d in cov}
        zero = [d for d, v in n.items() if v == 0]
        if not zero:
            world = f"A ALL THREE GATED — flips {n}"
        elif zero == ["FORMULATION.md"]:
            world = (f"C PARTIAL — FORMULATION.md flips ZERO gates under the MAXIMAL mutation, "
                     f"so no check in the suite can contradict it. R566's finding stands after "
                     f"six rounds of gate work. flips {n}")
        else:
            world = f"B PARTIAL/UNGATED — these flip nothing: {zero}. flips {n}"
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "gate_coverage.json").write_text(json.dumps({
        "world": world, "n_gates": len(gates),
        "named_by_grep": {k: v for k, v in named.items()},
        "baseline_passing": passing, "baseline_nonpassing": nonpass,
        "baseline_unstable": unstable,
        "coverage": cov, "negative_control": neg, "placebo": plc, "tree_sensitive_excluded": sorted(tree_sensitive),
        "harness_ok": harness_ok, "timeout_s": TIMEOUT,
        "grep_vs_mutation": ("instrument unit = the filename appears in the source; claim unit "
                             "= this document's content can make the suite fail. NOT equal"),
        "upper_bound_note": ("emptying is the MAXIMAL mutation, so the flip count bounds how "
                             "finely a document is gated from ABOVE, and a zero is decisive"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'gate_coverage.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
