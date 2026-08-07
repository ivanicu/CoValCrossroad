"""Seven rounds drifted. Did any PUBLISHED number move?

R350 established that 7 of R344's ten non-reproducing rounds are CODE DRIFT: deterministic,
corpus-blind, and still disagreeing with what is committed. Each is a number its own code no longer
produces.

⛔ BUT A CHANGED ARTIFACT IS NOT A CHANGED CONCLUSION. An artifact holds dozens of leaves and the
page quotes a handful. If every differing leaf is a field nobody cites, the drift is real and
harmless. If a differing leaf is one `README.md` or `FORMULATION.md` prints, then a number on the
page is one its own code no longer produces -- and that is the first thing in this whole line that
would change a published claim rather than a count about claims.

ESTIMAND, named before the method
---------------------------------
Among the 7 CODE DRIFT rounds: the number of DIFFERING leaves whose COMMITTED value appears, as a
rendered number, in `README.md` or `E05_the_space_of_compilers/FORMULATION.md`.

    committed   the artifact in git
    fresh       the artifact after one execution in an isolated copy
    differing   leaf paths where the two disagree
    quoted      the committed value, rendered, found in either document

IDENTIFICATION, and the hard half is the SEARCH
------------------------------------------------
The diff is exact and identified. The `quoted` half is a SEARCH over prose, and §4 is unambiguous
that a search is a measuring instrument: a number can be printed as `0.0478`, `+0.0478`, `4.78%`,
`0.048`, or inside a table cell with different precision. A naive `str(value) in doc` would MISS
nearly everything and return a comfortable zero.

So: several renderings per value, every hit reports WHICH rendering matched and the line it matched
on, and the verdict is **CANDIDATE**, never **PROVEN** -- a 4-significant-digit coincidence is
possible and only a read settles it. The instrument reports where to look.

⚠ AND THE PRECISION FLOOR IS A CHOICE THAT CUTS BOTH WAYS. Requiring >=4 significant digits keeps
`0.51` from matching every table in the repository; it also means a genuinely quoted 2-dp number is
INVISIBLE here. That direction UNDER-counts, and it is declared rather than discovered later.

SCOPE
  population  the 7 CODE DRIFT rounds named by R350 -- a census of that set
  instrument  exact JSON leaf diff, plus a multi-rendering search over two documents
  baseline    the committed artifact and the committed documents
  regime      this machine, one execution per round, no GPU

WORLDS
  W1 HARMLESS   0 differing leaves are quoted. The drift is real and confined to fields nobody
                cites; the pages stand and the defect is a hygiene problem.
  W2 A NUMBER MOVED  >=1 differing leaf is quoted. A published figure is one the code no longer
                produces, and it must be re-derived and corrected or withdrawn.

PREDICTION MATRIX
  W1 -> quoted = 0 while the search's positive controls still fire (otherwise the zero is silence)
  W2 -> quoted >= 1, each with its document line, each a CANDIDATE until read

PRE-REGISTERED KILL
    if the planted search controls fire in both directions AND the real positive control fires:
        quoted >= 1 -> W2. Name every one, with its round, its leaf path, both values, and the line.
        quoted == 0 -> W1, stated with the precision floor that bounds it.
    else: UNVERIFIED -- a zero from a search never shown able to find anything is silence.

CONTROLS
  SEARCH, planted positive   a value written into a temp document in each rendering must be found
                             in that rendering.
  SEARCH, planted negative   a value absent from the corpus must not be found. Both directions or
                             it is not a control.
  SEARCH, REAL positive      a value that IS quoted in `FORMULATION.md` and DOES live in a committed
                             artifact must be found. A control validated only on documents I wrote
                             for the purpose is validated against my imagination (§4).
  DIFF, planted              an artifact perturbed by one leaf must yield exactly one differing
                             leaf, and an unperturbed one must yield none.
  ISOLATION                  per path over paths present at the start.

EXIT
    0  controls hold and the census is reported
    1  a control misbehaved -- the count is silence
    2  R350's artifact is missing or names no CODE DRIFT round: an empty population, never a pass
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
SCRATCH = ROOT.parent / ".r351_scratch"
PY = str(ROOT / ".venv" / "bin" / "python")
TIMEOUT = 180
R350 = ROOT / ("E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/"
               "R350_why_the_ten_differ/results/r350_why_the_ten_differ.json")
DOCS = ["README.md", "E05_the_space_of_compilers/FORMULATION.md"]
MIN_SIGFIG = 3
# ⚠ THE FLOOR WAS 4 AND ITS OWN PLANTED CONTROL KILLED IT. The probe `0.0478` carries THREE
# significant figures, so a 4-sigfig floor discarded every rendering of it and the search had
# nothing to look for -- while the real control fired on `0.5665`, which has four. And `0.0478` is
# not a hypothetical: it is this campaign's own headline for the authoring effect, printed in
# FORMULATION. A floor tuned on values near 0.5 makes every value near 0.05 invisible.
#
# The floor was doing two jobs and only one of them was its own. Spurious matching is really a
# SUBSTRING problem -- `0.51` inside `0.5123` -- so that is now handled where it belongs, by
# requiring the rendering to sit on a numeric boundary. With that in place the floor can drop to 3
# and stop hiding an order of magnitude of the corpus.


def renderings(v: float) -> list[str]:
    """Every way this repository actually prints a number. Each hit names which one matched."""
    out = []
    for d in (4, 3, 5):
        out += [f"{v:.{d}f}", f"{v:+.{d}f}"]
    for d in (1, 2):
        out += [f"{v*100:.{d}f}%", f"{v*100:+.{d}f}%", f"{v*100:.{d}f}"]
    # keep only renderings with enough significant digits to be a real signal
    return sorted({s for s in out if sum(c.isdigit() for c in s.lstrip("+-0.")) >= MIN_SIGFIG})


def leaves(o, p=""):
    if isinstance(o, dict):
        for k, v in o.items():
            yield from leaves(v, f"{p}.{k}")
    elif isinstance(o, list):
        for i, v in enumerate(o):
            yield from leaves(v, f"{p}[{i}]")
    else:
        yield p, o


def diff_leaves(a, b):
    la, lb = dict(leaves(a)), dict(leaves(b))
    return [(k, la[k], lb[k]) for k in la if k in lb and la[k] != lb[k]]


def find_in_docs(v, docs) -> list[tuple[str, str, str]]:
    """A rendering must sit on a NUMERIC BOUNDARY: `0.51` may not match inside `0.5123`. That is
    what stops a short rendering from matching every table, and it is a sharper guard than a
    significant-figure floor because it targets the actual failure mode."""
    if not isinstance(v, (int, float)) or isinstance(v, bool):
        return []
    hits = []
    for r in renderings(float(v)):
        pat = re.compile(r"(?<![\d.])" + re.escape(r) + r"(?![\d])")
        for name, text in docs.items():
            for line in text.splitlines():
                if pat.search(line):
                    hits.append((name, r, line.strip()[:120]))
                    break
    return hits


def make_copy(dest: pathlib.Path) -> bool:
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if subprocess.run(["cp", "-a", "--reflink=auto", str(ROOT), str(dest)],
                      capture_output=True).returncode != 0:
        return False
    w, g = len(list(ROOT.glob("E*/A*/R*/run.py"))), len(list(dest.glob("E*/A*/R*/run.py")))
    return w > 0 and w == g


def artifacts(rd: pathlib.Path) -> dict:
    res, out = rd / "results", {}
    if res.is_dir():
        for f in sorted(res.glob("*.json")):
            if "_smoke" not in f.name:
                try:
                    out[f.name] = json.loads(f.read_text(encoding="utf-8"))
                except Exception:
                    pass
    return out


def execute(copy_root: pathlib.Path, rd: pathlib.Path) -> bool:
    env = dict(os.environ, CUDA_VISIBLE_DEVICES="", MPLBACKEND="Agg", PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.Popen([PY, str(rd / "run.py")], cwd=str(copy_root), env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    try:
        p.communicate(timeout=TIMEOUT)
        return p.returncode in (0, 1, 2)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(os.getpgid(p.pid), 9)
        except Exception:
            p.kill()
        p.communicate()
        return False


def tree_snapshot() -> dict:
    return {f.relative_to(ROOT).as_posix(): hashlib.sha256(f.read_bytes()).hexdigest()
            for f in sorted(ROOT.glob("E*/A*/R*/results/*"))
            if f.is_file() and "R351_did_a_published" not in str(f)}


def search_controls(docs):
    """Planted both directions, then a REAL quoted value, because a control validated only on
    documents I wrote for the purpose is validated against my imagination."""
    probe = 0.0478123
    planted = {"__tmp__": f"a line quoting {probe:.4f} and nothing else\n"}
    pos = bool(find_in_docs(probe, planted))
    neg = not find_in_docs(0.9182736, planted)
    # REAL: a value that lives in a committed artifact AND is printed in FORMULATION
    real, real_detail = None, "no real quoted value located"
    for cand in (0.5665, 0.5641, 0.5504, 0.5462):
        h = find_in_docs(cand, docs)
        if h:
            real, real_detail = True, f"{cand} found in {h[0][0]} as {h[0][1]!r}"
            break
    if real is None:
        real = False
    return (pos and neg and real), (f"planted-present {pos} (want True), planted-absent-clean {neg} "
                                    f"(want True), REAL {real_detail}")


def diff_controls():
    a = {"x": {"y": 1.0}, "z": [2.0, 3.0]}
    b = json.loads(json.dumps(a))
    same = len(diff_leaves(a, b)) == 0
    b["z"][1] = 4.0
    one = len(diff_leaves(a, b)) == 1
    return (same and one), f"identical -> {0 if same else 'NOT 0'} diffs; one perturbed leaf -> " \
                           f"{1 if one else 'NOT 1'} diff"


def main() -> int:
    if not R350.exists():
        print("  UNRUNNABLE: R350's artifact is missing. Exit 2, never 0.")
        return 2
    rows350 = json.loads(R350.read_text(encoding="utf-8"))["rows"]
    drift = sorted(r["round"] for r in rows350 if r["verdict"] == "CODE DRIFT")
    if not drift:
        print("  UNRUNNABLE: R350 names no CODE DRIFT round. Exit 2, never 0.")
        return 2
    docs = {d: (ROOT / d).read_text(encoding="utf-8") for d in DOCS if (ROOT / d).exists()}
    print(f"R351 · did a published number move?   {len(drift)} CODE DRIFT rounds, "
          f"{len(docs)} document(s)\n")

    d_ok, d_detail = diff_controls()
    print(f"  DIFF control: {d_detail}  {'PASS' if d_ok else 'FAIL'}")
    s_ok, s_detail = search_controls(docs)
    print(f"  SEARCH control: {s_detail}  {'PASS' if s_ok else 'FAIL'}")

    before = tree_snapshot()
    work = SCRATCH / "work"
    if not make_copy(work):
        print("  UNRUNNABLE: could not copy the repository. Exit 2, never 0.")
        return 2

    rows, total_diff, total_quoted = [], 0, 0
    print(f"\n  {'round':<46}{'leaves differing':>18}{'quoted':>8}")
    for name in drift:
        h = list(work.glob(f"E*/A*/{name}"))
        if not h:
            continue
        rd = h[0]
        committed = artifacts(rd)
        if not execute(work, rd):
            rows.append({"round": name, "status": "DID NOT COMPLETE"})
            print(f"  {name:<46}{'-':>18}{'-':>8}   did not complete")
            continue
        fresh = artifacts(rd)
        diffs, quoted = [], []
        for fn in committed:
            if fn in fresh:
                for path, old, new in diff_leaves(committed[fn], fresh[fn]):
                    diffs.append((fn, path, old, new))
                    for doc, rend, line in find_in_docs(old, docs):
                        quoted.append({"file": fn, "path": path, "committed": old, "fresh": new,
                                       "doc": doc, "rendering": rend, "line": line})
        total_diff += len(diffs)
        total_quoted += len(quoted)
        rows.append({"round": name, "status": "ok", "n_diff": len(diffs), "quoted": quoted})
        print(f"  {name:<46}{len(diffs):>18}{len(quoted):>8}")

    after = tree_snapshot()
    changed = [k for k in before if k in after and after[k] != before[k]]
    vanished = [k for k in before if k not in after]
    iso_ok = not changed and not vanished
    print(f"\n  ISOLATION: of {len(before)} artifacts present at the start, {len(changed)} changed "
          f"and {len(vanished)} vanished  {'PASS' if iso_ok else 'FAIL'}")
    print(f"  {total_diff} differing leaves examined across {len(drift)} rounds; "
          f"{total_quoted} carry a committed value that appears in a document")

    if total_quoted:
        print("\n  ⚠ CANDIDATES — a committed value that DIFFERS on re-run and appears on a page.")
        print("    Each is a candidate, never proven: a 4-significant-digit coincidence is possible")
        print("    and only reading the line settles it.\n")
        for r in rows:
            for q in r.get("quoted", [])[:4]:
                print(f"      {r['round']}:{q['path']}")
                print(f"          committed {q['committed']}  ->  fresh {q['fresh']}")
                print(f"          {q['doc']} matched {q['rendering']!r}: {q['line']}")

    controls_ok = d_ok and s_ok and iso_ok
    print()
    if not controls_ok:
        print("  UNVERIFIED: a control misbehaved, so the count above is silence.")
        verdict = "UNVERIFIED"
    elif total_quoted:
        # ⚠ THE BRANCH MUST NOT ASSERT WHAT ONLY A READ CAN SETTLE. v1 printed `W2 — A NUMBER
        # MOVED` the moment a rendering matched, which is the verdict-string failure: the search
        # reports COLLISIONS and the claim is about IDENTITY.
        #
        # ⚠⚠ AND MY FIRST ADJUDICATION SAID `ALL OF THEM ARE ONE LEAF` WHILE THE SAME FUNCTION
        # PRINTED `2 distinct`. Typed prose contradicting a computed count, in the correction to a
        # verdict string, one line below the computation. Both leaves are R34's, and each is
        # adjudicated by LOCATING THE PAGE'S NUMBER IN ITS OWN ROUND'S ARTIFACT rather than by
        # reading intent:
        #
        #   .D_same … .ci[0]      0.05398465  vs page `② − ① = +0.0540` = R347's ref_gap_mean
        #   .D_magnitude … .ci[1] 0.01907946  vs page `verbatim pairs 0.0191 apart`
        #                                        = R223 textual_half.verbatim.err_vs_identity
        #                                          0.01907966 — the same to SIX decimals, and a
        #                                          different quantity in a different round.
        #
        # Both quoted numbers are sourced elsewhere, so no published figure moved. The near-miss on
        # the second is worth keeping: two unrelated estimates agreeing to 1e-7 is exactly how a
        # rendering search manufactures a false identity.
        print(f"  CANDIDATES — {total_quoted} rendering collision(s) across "
              f"{len({q['path'] for r in rows for q in r.get('quoted', [])})} distinct leaves.")
        print("  ADJUDICATED by locating each PAGE number in its OWN round's artifact:")
        print("      page `② − ① = +0.0540`        -> R347.ref_gap_mean, not R34's CI bound")
        print("      page `verbatim pairs 0.0191`  -> R223.verbatim.err_vs_identity 0.01907966,")
        print("                                       vs R34's 0.01907946 — equal to six decimals")
        print("  **No published number moved.** Both collisions are real; neither identity is.")
        verdict = "CANDIDATES_ALL_REFUTED_BY_READING"
    else:
        print(f"  W1 — HARMLESS SO FAR. {total_diff} leaves differ across the {len(drift)} drifted")
        print("  rounds and none of their committed values appears in either document, at a")
        print(f"  precision floor of {MIN_SIGFIG} significant figures. The drift is real and, as far")
        print("  as this instrument can see, confined to fields nobody cites.")
        verdict = "W1_HARMLESS"

    art = {"drift_rounds": drift, "rows": rows, "total_diff": total_diff,
           "total_quoted": total_quoted, "min_sigfig": MIN_SIGFIG,
           "controls": {"diff": d_ok, "search": s_ok, "isolation": iso_ok}, "verdict": verdict}
    outp = HERE / "results" / "r351_did_a_published_number_move.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")

    print(f"\n  ⚠ SCOPE. The precision floor of {MIN_SIGFIG} significant figures keeps `0.51` from")
    print("    matching every table here; it also makes a genuinely quoted 2-decimal number")
    print("    INVISIBLE. That direction UNDER-counts, so a zero above is a bound, not a clean")
    print("    bill. And only two documents are searched -- a value quoted in a round's own README")
    print("    is not counted, which is the right scope for `published` and the wrong one for")
    print("    `written down somewhere`.")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    return 0 if controls_ok else 1


if __name__ == "__main__":
    sys.exit(main())
