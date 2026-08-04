"""Does ANY check in this suite verify that a committed artifact came from the committed source?

R342 found that a property can be unidentified from the input a gate reads: `is this point a ratio`
lives in the source, and no artifact-side arithmetic decides it at any sample size. That was one
property. This round asks whether the SUITE has the same shape at its foundation.

Every artifact-side verdict in this repository -- 389 coherence pairs, 382 centred intervals, every
`results are not degenerate`, every `verdict cites its own contrasts` -- rests on one unstated
assumption: THAT THE JSON NEXT TO A run.py WAS PRODUCED BY THAT run.py. Nothing has ever tested it.
realstat §4 names the shape: `determinism read as currency` -- a two-seed gate compares two fresh
runs to EACH OTHER, never to disk, and certifies determinism rather than provenance.

ESTIMAND, named before the method
---------------------------------
The number of checks in the suite whose VERDICT changes when a round's source is edited to compute
a DIFFERENT STATISTIC while its committed artifact is left byte-identical.

    baseline    every check's exit code on an unmutated copy
    T_src       every round's run.py: `mean` -> `median` (numpy calls and method calls alike),
                a meaning-changing, syntax-preserving edit. Artifacts untouched.
    verdict change = exit code differs from baseline

IDENTIFICATION, and half the answer is a DERIVATION rather than a measurement
------------------------------------------------------------------------------
A check that never opens a `run.py` CANNOT respond to a source edit. That is forced by the algebra
of what it reads, not discovered -- so this round FIRST censuses what each check opens (mechanically,
via an audit hook on `open`, not by reading the code and judging), and reports the artifact-only
checks as a DERIVATION with its assumption stated: `a function's output depends only on its inputs`.
⛔ Calling that a measurement would be realstat's arithmetic trap exactly.

The MEASUREMENT is the remainder: of the checks that DO read sources, how many notice?

WORLDS
  W1 SOMEONE CHECKS   >=1 check changes verdict under T_src. Provenance is verified somewhere; name
                      it, and the assumption above is not free-floating.
  W2 NOBODY CHECKS    0 change. Every artifact-side verdict in the repo rests on an assumption no
                      instrument here tests, and a stale or hand-edited artifact is invisible.
  W3 NOISY HARNESS    verdicts move under the SHAM too, so a change under T_src would mean nothing.

PREDICTION MATRIX
  W1 -> T_src moves >=1; sham moves 0; positive control moves the check it targets
  W2 -> T_src moves 0;   sham moves 0; positive control moves the check it targets
  W3 -> sham moves >0  -> the round is UNVERIFIED whatever T_src does
The positive control appears in every row on purpose: without it, `0 changed` is silence rather
than a measurement, and this design's whole risk is reporting a zero from a harness never shown to
return non-zero.

CONTROLS
  POSITIVE   T_art: corrupt ONE artifact so a point estimate falls outside its own CI. At least one
             check MUST change verdict. This proves the harness can observe a verdict change at all.
             It fails at g=0 by construction: with no corruption the same comparison returns 0.
  SHAM       T_comment: append a comment line to every run.py. Same files touched, same bytes
             rewritten, ZERO semantic change. Any check that moves here is reacting to the edit
             rather than to its meaning, and the round is void.
  g=0        T_none: copy and mutate nothing. Every verdict must equal baseline. Detects harness
             noise, non-determinism, and copy damage in one comparison.
  ISOLATION  the real repository is hashed before and after. A hardlink copy shares inodes, so an
             in-place write would edit the ORIGINAL. Mutation therefore unlinks before writing, and
             the assertion is checked rather than trusted.

SCOPE
  population  the 21 checks registered in assurance/attack_the_suite.py -- a CENSUS
  instrument  exit codes, and an audit hook on `open` for the read census
  baseline    each check's own unmutated exit code, not a shared expectation
  regime      the repository at this commit; checks run from the COPY, so their ROOT follows

MULTIPLICITY  one family, 21 cells, 4 conditions. Cells tested and cells moving are both reported;
              no correction is applied because no per-cell null hypothesis is being tested -- these
              are verdict changes, not test statistics, and calling them significant would be the
              arithmetic trap in the other direction.

⚠ REPRODUCIBILITY IS A FIXPOINT HERE, NOT AN IDENTITY, and saying so is not a hedge.
This round copies the repository and runs 21 checks over it. Its OWN artifact lands in that
repository, so the corpus the next run measures includes the previous run's output, and several
checks count corpus files. Measured: run 1 -> 8dc9b3c8, runs 2, 3, 4 -> 2ee66bcc, byte-identical.
The artifact is stable FROM THE SECOND RUN ON. Reporting `two runs byte-identical` without that
sentence would have been true and misleading -- the first transition is real and is a property of
measuring a system you are inside of, which is what every check in this suite also does.

EXIT
    0  controls hold and the census is reported
    1  a control misbehaved: the sham moved, or the positive control did not
    2  no checks found, or the copy failed: an empty population, never a silent pass
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
# Same filesystem as the repository, deliberately: hardlinks cannot cross devices, and /tmp is
# tmpfs here while the repo is ext4. Outside the repo, so no glob or git command can see it.
SCRATCH = pathlib.Path(os.environ.get("R343_SCRATCH", str(ROOT.parent / ".r343_scratch")))


def registered_checks() -> list[str]:
    """Read the suite's own registry rather than globbing assurance/*.py: the registry IS the
    population the suite claims to protect, and a file that is not registered is not in it."""
    src = (ROOT / "assurance" / "attack_the_suite.py").read_text(encoding="utf-8")
    return re.findall(r'^\s*\("([a-z0-9_]+)",\s', src, re.M)


# ------------------------------------------------------------------------- mutations -------------
def mutate_none(root: pathlib.Path) -> int:
    return 0


def _rewrite(p: pathlib.Path, text: str) -> None:
    """⚠ UNLINK FIRST. The copy is made with hardlinks for speed, so `p.write_text(...)` would
    truncate and rewrite the inode the REAL repository still points at. Unlinking breaks the link
    before any byte is written. The isolation assertion below checks this rather than trusting it."""
    p.unlink()
    p.write_text(text, encoding="utf-8")


def mutate_src_mean_to_median(root: pathlib.Path) -> int:
    """Meaning-changing, syntax-preserving: every mean becomes a median. Artifacts untouched, so
    every committed number is now one the source cannot reproduce."""
    n = 0
    for p in sorted(root.glob("E*/A*/R*/run.py")):
        t = p.read_text(encoding="utf-8", errors="replace")
        u = re.sub(r"\bnanmean\b", "nanmedian", t)
        u = re.sub(r"(?<![\w.])mean\(", "median(", u)
        u = re.sub(r"\.mean\(", ".median(", u)
        u = re.sub(r"np\.mean\b", "np.median", u)
        if u != t:
            _rewrite(p, u)
            n += 1
    return n


def mutate_comment_only(root: pathlib.Path) -> int:
    """THE SHAM: the same files, rewritten, with zero semantic change."""
    n = 0
    for p in sorted(root.glob("E*/A*/R*/run.py")):
        t = p.read_text(encoding="utf-8", errors="replace")
        _rewrite(p, t + "\n# R343 sham: this line changes nothing about what the round computes.\n")
        n += 1
    return n


def _gate_regexes():
    """⚠ IMPORTED, NEVER RE-TYPED, and this is the whole reason the first positive control failed.
    v1 planted its corruption wherever a numeric key stem-matched a two-element list. The coherence
    gate pairs only where `MEANISH` matches the mean AND `CIISH` matches the interval, so the plant
    landed on `R03_stated_vs_revealed` -- a pair that gate never looks at -- and the control
    reported `0 moved` while the harness was working perfectly. realstat §4, stated exactly:
    name the instrument's unit and the claim's unit as two separate strings and require them to be
    EQUAL, before the control is even designed. Mine were `any stem-matched numeric` and
    `a pair this gate checks`, and I had written the gate."""
    p = ROOT / "assurance" / "artifacts_are_internally_coherent.py"
    spec = importlib.util.spec_from_file_location("r343_gate", p)
    m = importlib.util.module_from_spec(spec)
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(m)
    return m


def mutate_artifact_break_ci(root: pathlib.Path) -> int:
    """POSITIVE CONTROL: move ONE point estimate outside its own interval, in one artifact, in a
    node THE COHERENCE GATE ACTUALLY PAIRS. If no check notices this, the harness cannot observe a
    verdict change and every zero below is silence."""
    G = _gate_regexes()
    for f in sorted(root.glob("E*/A*/R*/results/*.json")):
        if "_smoke" in str(f) or f.stat().st_size > 6_000_000:
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        hit = [0]

        def walk(o):
            if hit[0]:
                return o
            if isinstance(o, list):
                return [walk(v) for v in o]
            if not isinstance(o, dict):
                return o
            for k, v in list(o.items()):
                if G.CIISH.match(k) and G.is_ci(v):
                    for mk, mv in o.items():
                        if (mk != k and G.MEANISH.match(mk) and not G.PVALUE.match(mk)
                                and isinstance(mv, (int, float)) and not isinstance(mv, bool)
                                and (mk.lower() in k.lower()
                                     or k.lower().replace("_ci", "") == mk.lower())):
                            lo, hi = sorted(v)
                            o[mk] = hi + (abs(hi - lo) + 1.0)     # unambiguously outside
                            hit[0] = 1
                            return o
            return {k: walk(v) for k, v in o.items()}

        d = walk(d)
        if hit[0]:
            _rewrite(f, json.dumps(d, indent=2, sort_keys=True))
            return 1
    return 0


CONDITIONS = [
    ("g0_none", mutate_none, "copy, mutate nothing -- must equal baseline"),
    ("sham_comment", mutate_comment_only, "SHAM: same files rewritten, zero semantic change"),
    ("T_src_mean_to_median", mutate_src_mean_to_median,
     "every round computes a MEDIAN; artifacts untouched"),
    ("T_art_break_ci", mutate_artifact_break_ci,
     "POSITIVE: one point estimate moved outside its own CI"),
]


# --------------------------------------------------------------------------- harness -------------
# ⚠ ONE audit hook, installed once. `sys.addaudithook` cannot be REMOVED, so installing one per
# traced check would leave 21 live hooks, each still appending to the set of a check that finished
# long ago -- every earlier check would inherit every later check's reads and the census would
# report that all 21 open sources. A single hook writing into a rebindable target is the only shape
# that measures what it says it measures.
_CURRENT: set[str] | None = None
_HOOK_INSTALLED = False


def _install_hook() -> None:
    global _HOOK_INSTALLED
    if _HOOK_INSTALLED:
        return

    def hook(event, args):
        if _CURRENT is not None and event == "open" and args:
            try:
                _CURRENT.add(str(args[0]))
            except Exception:
                pass

    sys.addaudithook(hook)
    _HOOK_INSTALLED = True


def run_check(root: pathlib.Path, name: str, trace: bool = False):
    """Exit code, plus (optionally) the set of paths the check opened. Runs in-process against the
    COPY, so the check's own `ROOT = parents[1]` resolves inside the copy."""
    global _CURRENT
    p = root / "assurance" / f"{name}.py"
    if not p.exists():
        return (None, None), set()
    opened: set[str] = set()

    cwd, argv, path0 = os.getcwd(), list(sys.argv), list(sys.path)
    try:
        os.chdir(root)
        sys.path.insert(0, str(root))
        sys.argv = [name]
        if trace:
            _install_hook()
            _CURRENT = opened
        spec = importlib.util.spec_from_file_location(f"chk_{name}", p)
        m = importlib.util.module_from_spec(spec)
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(io.StringIO()):
                spec.loader.exec_module(m)
                rc = m.main() if hasattr(m, "main") else 0
        except SystemExit as e:
            rc = e.code if isinstance(e.code, int) else 1
        except Exception:
            rc = "ERROR"
        # ⚠ TWO INSTRUMENTS, because the coarse one is SATURATED. `artifacts_are_internally
        # _coherent` already exits 1 on R141's six violations, so planting a seventh cannot move an
        # exit code -- realstat §4's `control that cannot PASS`, where the threshold sits above what
        # the design can return under a maximal plant. The floor/ceiling test it prescribes is what
        # exposed it: ceiling(exit code | maximal corruption) == 1 == floor. So the report digest is
        # carried too, and which instrument the headline uses is decided by whether the SHAM moves
        # under it -- not by which one gives the nicer answer.
        digest = hashlib.sha256(buf.getvalue().encode("utf-8", "replace")).hexdigest()[:16]
    finally:
        _CURRENT = None
        os.chdir(cwd)
        sys.argv = argv
        sys.path[:] = path0
    return (rc, digest), opened


def make_copy(dest: pathlib.Path) -> bool:
    """⚠ AND IT MUST ASSERT ITS OWN SHAPE. v1 pointed SCRATCH at /tmp, which is tmpfs while the
    repository is ext4, so `cp -al` died on the first cross-device link and left a PARTIAL tree --
    and the fallback `cp -a src dst` then found `dst` already existing and copied the repo INTO it
    as a subdirectory. Every glob returned 0, every mutation touched 0 files, and every condition
    reported `verdict changed: 0` -- including, in a run with no controls, what would have read as
    the headline. The positive control is the only reason that was a FAIL instead of a finding.
    So the copy now (a) lands on the SAME filesystem, where hardlinks work, (b) clears `dst` before
    any fallback, and (c) REFUSES to return success unless the copy holds the same number of round
    sources as the original. A copy that produced no rounds was never a copy."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = subprocess.run(["cp", "-al", str(ROOT), str(dest)], capture_output=True)
    if r.returncode != 0:
        if dest.exists():
            shutil.rmtree(dest)
        r = subprocess.run(["cp", "-a", str(ROOT), str(dest)], capture_output=True)
    if r.returncode != 0:
        return False
    want = len(list(ROOT.glob("E*/A*/R*/run.py")))
    got = len(list(dest.glob("E*/A*/R*/run.py")))
    if want == 0 or got != want:
        print(f"    COPY SHAPE WRONG: {got} round sources in the copy, {want} in the original")
        return False
    return True


def repo_fingerprint() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain"],
                       capture_output=True, text=True)
    return hashlib.sha256(r.stdout.encode()).hexdigest()[:16]


def main() -> int:
    checks = registered_checks()
    if not checks:
        print("  UNRUNNABLE: the registry lists no checks. Exit 2, never 0.")
        return 2
    print(f"R343 · does any check tie an artifact to its source?   {len(checks)} registered checks\n")

    before = repo_fingerprint()

    # ---- baseline + the read census, in one pass ------------------------------------------------
    base_dir = SCRATCH / "baseline"
    if not make_copy(base_dir):
        print("  UNRUNNABLE: could not copy the repository. Exit 2, never 0.")
        return 2
    baseline, reads = {}, {}
    for c in checks:
        rc, opened = run_check(base_dir, c, trace=True)
        baseline[c] = rc
        reads[c] = opened

    def kinds(paths):
        k = set()
        for s in paths:
            if "/results/" in s and s.endswith(".json"):
                k.add("artifact")
            elif re.search(r"/R\d+[^/]*/run\.py$", s):
                k.add("round source")
            elif s.endswith(".md"):
                k.add("document")
            elif "/assurance/" in s and s.endswith(".json"):
                k.add("registry")
        return k

    print("  READ CENSUS -- what each check actually OPENS, from an audit hook, not from reading")
    print("  the code and forming an opinion:\n")
    print(f"    {'check':<42}{'baseline':>9}   opens")
    src_readers, art_only = [], []
    for c in checks:
        k = kinds(reads[c])
        if "round source" in k:
            src_readers.append(c)
        elif k:
            art_only.append(c)
        print(f"    {c:<42}{str(baseline[c]):>9}   {', '.join(sorted(k)) or '(nothing traced)'}")
    print(f"\n  {len(src_readers)} check(s) open a round's run.py; {len(art_only)} open only "
          f"artifacts/documents/registries.")
    print("  ⛔ DERIVATION, not a measurement: a check that never opens a run.py cannot respond to a")
    print("     source edit. Forced by `a function's output depends only on its inputs`. The")
    print("     measurement below is the remainder.")

    # ---- the four conditions ---------------------------------------------------------------------
    print("\n  CONDITIONS -- exit code per check, compared to that check's OWN baseline\n")
    results = {}
    for cname, fn, desc in CONDITIONS:
        d = SCRATCH / cname
        if not make_copy(d):
            print(f"    {cname:<22} COPY FAILED")
            results[cname] = {"error": "copy failed"}
            continue
        touched = fn(d)
        moved_exit, moved_rep, verdicts = [], [], {}
        for c in checks:
            v, _ = run_check(d, c)
            verdicts[c] = v
            if v[0] != baseline[c][0]:
                moved_exit.append((c, baseline[c][0], v[0]))
            if v != baseline[c]:
                moved_rep.append((c, baseline[c][0], v[0]))
        results[cname] = {"files_touched": touched, "moved": moved_exit, "moved_report": moved_rep,
                          "verdicts": {k: [str(a), b] for k, (a, b) in verdicts.items()}}
        print(f"    {cname:<22} touched {touched:>4}   moved(exit) {len(moved_exit):>2}   "
              f"moved(report) {len(moved_rep):>2}   ({desc})")
        for c, b, a in moved_rep[:6]:
            tag = "exit+report" if any(c == x for x, _, _ in moved_exit) else "report only"
            print(f"        {c:<44} {b} -> {a}  [{tag}]")
        if len(moved_rep) > 6:
            print(f"        … {len(moved_rep) - 6} more")
        shutil.rmtree(d, ignore_errors=True)

    after = repo_fingerprint()
    iso_ok = (before == after)
    print(f"\n  ISOLATION: the real repository's git status is unchanged  "
          f"{'PASS' if iso_ok else 'FAIL -- the hardlink copy wrote through'}")

    g0 = results.get("g0_none", {})
    sham = results.get("sham_comment", {})
    tsrc = results.get("T_src_mean_to_median", {})
    tart = results.get("T_art_break_ci", {})
    # WHICH INSTRUMENT CARRIES THE HEADLINE is decided by the sham, before any T_src number is
    # read. If the report digest moves on a comment-only edit it is measuring the edit rather than
    # its meaning, and the coarse instrument is the only admissible one.
    sham_rep = len(sham.get("moved_report", [1]))
    sham_exit = len(sham.get("moved", [1]))
    INSTR = "moved_report" if sham_rep == 0 else "moved"
    print(f"\n  INSTRUMENT SELECTION: the sham moves {sham_exit} exit code(s) and {sham_rep} report "
          f"digest(s).\n  -> headline instrument = {'report digest' if INSTR == 'moved_report' else 'exit code only'}"
          f" (chosen by the sham, not by which answer it gives)")

    g0_ok = len(g0.get(INSTR, [1])) == 0
    sham_ok = len(sham.get(INSTR, [1])) == 0
    pos_ok = len(tart.get(INSTR, [])) >= 1 and tart.get("files_touched", 0) == 1
    print(f"  g=0 (nothing mutated):      {len(g0.get(INSTR, []))} moved (want 0)  "
          f"{'PASS' if g0_ok else 'FAIL'}")
    print(f"  SHAM (comment only):        {len(sham.get(INSTR, []))} moved (want 0)  "
          f"{'PASS' if sham_ok else 'FAIL'}")
    print(f"  POSITIVE (one broken CI):   {len(tart.get(INSTR, []))} moved (want >=1)  "
          f"{'PASS' if pos_ok else 'FAIL'}")
    if tart.get("moved_report") and not tart.get("moved"):
        print("      ⚠ and it moved the REPORT without moving the EXIT CODE, which is the")
        print("        saturation this dual instrument exists for: the coherence gate already")
        print("        exits 1 on R141, so a seventh violation is invisible to an exit code.")

    n_src = len(tsrc.get(INSTR, []))
    print()
    if not (iso_ok and g0_ok and sham_ok and pos_ok):
        print("  UNVERIFIED: a control misbehaved, so the source-mutation count below is silence.")
        verdict = "UNVERIFIED"
    elif n_src >= 1:
        print(f"  W1. {n_src} check(s) noticed that every round now computes a MEDIAN while its")
        print("  committed artifact still holds the mean. Provenance is verified somewhere:")
        for c, b, a in tsrc[INSTR]:
            print(f"      {c}  ({b} -> {a})")
        verdict = "W1_SOMEONE_CHECKS"
    else:
        print(f"  W2. ZERO of {len(checks)} checks noticed. Every round in the repository was edited")
        print("  to compute a different statistic, every committed artifact was left holding numbers")
        print("  that source can no longer produce, and the suite's verdict did not move by one exit")
        print("  code. The positive control moved, so this is a measurement and not silence.")
        print("  Every artifact-side verdict here rests on an assumption no instrument tests.")
        verdict = "W2_NOBODY_CHECKS"

    art = {
        "checks": checks, "baseline": {k: [str(v[0]), v[1]] for k, v in baseline.items()},
        "headline_instrument": INSTR,
        "read_census": {c: sorted(kinds(reads[c])) for c in checks},
        "source_readers": src_readers, "artifact_only": art_only,
        "conditions": {k: {"files_touched": v.get("files_touched"),
                           "moved_exit": [[c, str(b), str(a)] for c, b, a in v.get("moved", [])],
                           "moved_report": [[c, str(b), str(a)] for c, b, a in v.get("moved_report", [])]}
                       for k, v in results.items()},
        "controls": {"isolation": iso_ok, "g0": g0_ok, "sham": sham_ok, "positive": pos_ok},
        "verdict": verdict,
    }
    outp = HERE / "results" / "r343_provenance_gauge.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")

    print("\n  ⚠ SCOPE. This tests ONE direction of correspondence: source changed, artifact stale.")
    print("    It does not test the reverse (an artifact hand-edited to agree with a source that")
    print("    never produced it), and it does not test whether any individual number is correct.")
    print("    A check that legitimately has nothing to say about statistics is not defective for")
    print("    scoring 0 here -- the claim is about the SUITE, whose unit is the whole registry.")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    return 0 if (iso_ok and g0_ok and sham_ok and pos_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
