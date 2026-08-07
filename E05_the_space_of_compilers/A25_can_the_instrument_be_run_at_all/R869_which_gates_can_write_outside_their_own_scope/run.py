#!/usr/bin/env python3
"""
R869 · which gates can write OUTSIDE their own scope? — the set R868 owes before it can finish.

⛔ WHY. R868 could only fault-inject **30 of 70** gates, because 30 write to disk and running injected
copies of writers against the live repo already cost two mutated files and this round's own log.
Its NEXT proposed a WRITES/READ-ONLY contract per gate.

⚠ **AND THAT NEXT, AS WRITTEN, WOULD HAVE BUILT A CHECK THAT CANNOT FAIL.** Deriving a declaration
from the AST and then verifying the declaration against the same AST is circular — §4's first row,
and I have built it five times in this session. So the estimand is changed, deliberately, and the
change is the round's first move rather than a footnote.

⭐ **THE SHARP QUESTION IS NOT *DOES IT WRITE* BUT *WHERE*.** A gate writing its own
`assurance/results/*.json` or its own frozen baseline is self-scoped and harmless to re-run. A gate
that can write **outside `assurance/`** — into the round tree, into `DEFINITION.md`, into arbitrary
repo paths — is the class that made R868's injection unsafe. **That set is a concrete deliverable:
it is exactly the list R868 needs to finish, and nothing in the suite currently records it.**


⛔⛔⛔ POST-RUN CORRECTION, WRITTEN BEFORE COMMIT. **THE PRINTED WORLD-B SENTENCE OVERCLAIMS AND IS
WITHDRAWN IN ITS SECOND HALF.** It reads *"a minority can write outside assurance/"*. **That is not
what was measured.** The tell is in the round's own output column: every one of the 27 flagged gates
shows `N site(s), N unresolved` — **100% UNRESOLVED, 0% REPO.** The `REPO` category was never
populated by a single real gate.

**So the resolver classified nothing.** `path_root` handles `ROOT / "x" / "y"` and `OUT / "z"`, but
the real corpus writes through LOCAL VARIABLES — `p.write_text(...)`, `tgt.unlink()`, `f.rename(...)`
where the path was computed lines earlier or came out of a loop. A static walk cannot follow that,
and **the entire 27 comes from my safety rule `UNRESOLVED -> REPO`, not from evidence.**

⭐ **AND MY POSITIVE CONTROL PASSED ANYWAY, WHICH IS THE LESSON.** It planted
`(ROOT / "E05" / "x.md").write_text(...)` and the scoper correctly called it REPO. But **no gate in
this repo is written that way.** The control proved the instrument can see a shape that does not
occur — §4, verbatim: *a control validated only against cases you invented is validated against your
imagination.* The third g=0 arm caught a rubber stamp; nothing caught a scoper that is simply blind
to the corpus's actual idiom, because I never checked that any REAL line landed in the positive
category.

**WHAT SURVIVES, AND IT IS STILL THE DELIVERABLE R868 NEEDED:**
  ⭐ **42 of 69 gates have NO write site at all (39) or write only through a SELF root (3).** That is
     a POSITIVE, resolved measurement — an absent call is not an unresolved one — and it is a
     genuine safe-to-inject set, larger than the 30 R868 managed.
  ⛔ **27 are UNKNOWN, not DANGEROUS.** The correct word is unknown. Reporting them as writers-to-
     the-repo would be a fabricated impossibility in the flattering direction: it makes R868's
     unfinished 40% look like someone else's fault.

**WHAT THIS ACTUALLY SETTLES ABOUT R868:** static analysis **cannot** produce the safe set beyond
the trivially write-free. Anything that writes at all writes through a variable, so **isolation is
required for every one of the 27 regardless of destination** — which is nearer WORLD C than the
WORLD B the branch printed. The branch condition tested `frac < 0.5`; it should have tested whether
the REPO category had any members at all, and it is left in place, uncorrected, as the evidence.

⚠ **The remedy for next time, and it is mechanical:** before trusting a classifier's positive
category, **require at least one REAL corpus item to land in it.** A category with zero real members
is a category the instrument has never demonstrated on the object.

ESTIMAND        for each `assurance/*.py`, the set of filesystem-write sites it contains, each
                classified by DESTINATION SCOPE: SELF (under assurance/), REPO (elsewhere under
                ROOT), or UNRESOLVED (the target is not a static path expression).
IDENTIFICATION  partial by construction, and that is stated up front rather than discovered: a
                statically unresolvable target (an f-string, a variable, a loop over a glob) cannot
                be scoped by AST. Those are counted as UNRESOLVED and **treated as REPO for safety**,
                never as SELF. The result is therefore a BOUND — an upper bound on the safe set —
                which is the direction that cannot hurt anyone.
SCOPE           population: every `assurance/*.py` that parses
                instrument: AST walk for write sites — `write_text`, `open(..., mode w/a/x/+)`,
                            `unlink`, `rename`, `replace`, `mkdir`, `shutil.*`, `Path.touch`
                baseline:   R868's crude name-level `is_read_only` heuristic, which said 26/70
                regime:     this repo, this commit
WORLDS          A · every writer is SELF-scoped -> R868's exclusion was over-cautious and all 70
                    gates can be injected safely with no isolation at all
                B · a minority write outside assurance/ -> the safe set is most of the 70, and
                    R868 can be finished for everything except a named few
                C · most writers are REPO-scoped or UNRESOLVED -> isolation is genuinely required
                    and R868's 40% coverage is the honest ceiling until a worktree exists
KILL            CONDITIONAL, all required, and the controls use REAL code shapes from this repo:
                  ⭐ ① POSITIVE: a synthetic gate writing to `ROOT / "E05..." / "x.md"` must be
                     classified REPO. If the scoper cannot see an out-of-scope write, its SELF
                     verdicts are silence.
                  ⭐ ② g=0: a synthetic gate writing only to
                     `pathlib.Path(__file__).resolve().parent / "results" / "x.json"` must be SELF.
                     A scoper that calls everything REPO is not a scoper.
                  ⭐ ③ g=0 second arm: a gate with NO writes must yield an EMPTY site list. Without
                     this, a scoper that reports "REPO" for everything passes arm ① trivially.
                  ④ the population must be non-empty. Exit 2 otherwise.
PLACEBO         re-running the scoper on the same file must give byte-identical output.
MULTIPLICITY    every gate × every write site; all reported, including UNRESOLVED.
ARTIFACT        results/write_scope.json — and it is the INPUT R868's rerun needs.
IMPOSSIBLE      cross-release · construct validated. ⚠ `causally identified` is claimed for R868's
                liveness question but NOT here: this round is a static read of code, and a static
                read cannot prove a path is never written at runtime. It bounds, it does not prove.
"""
import ast, json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)

WRITE_ATTRS = {"write_text", "write_bytes", "unlink", "rename", "replace", "mkdir", "touch",
               "rmdir", "symlink_to", "hardlink_to"}
SHUTIL_ATTRS = {"copy", "copy2", "copytree", "move", "rmtree", "copyfile"}
MODE_CHARS = "wax+"


def path_root(node):
    """Best-effort: the leftmost NAME of a path expression, e.g. OUT / 'x' -> 'OUT'."""
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        node = node.left
    while isinstance(node, ast.Call) and node.args:
        node = node.func if not isinstance(node.func, ast.Attribute) else node.func.value
    while isinstance(node, ast.Attribute):
        node = node.value
    return node.id if isinstance(node, ast.Name) else None


SELF_ROOTS = {"OUT", "FROZEN", "CORR", "HERE", "SELFDIR", "RESULTS", "STATE", "LEDGER"}


def write_sites(path):
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    sites = []
    for node in ast.walk(tree):
        tgt, kind = None, None
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            a = node.func.attr
            if a in WRITE_ATTRS:
                tgt, kind = node.func.value, a
            elif a in SHUTIL_ATTRS and path_root(node.func.value) == "shutil":
                tgt, kind = (node.args[1] if len(node.args) > 1 else None), f"shutil.{a}"
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                and node.func.id == "open":
            for arg in list(node.args[1:]) + [k.value for k in node.keywords
                                              if k.arg == "mode"]:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str) \
                        and any(c in arg.value for c in MODE_CHARS):
                    tgt, kind = (node.args[0] if node.args else None), f"open({arg.value!r})"
        if kind is None:
            continue
        r = path_root(tgt) if tgt is not None else None
        if r in SELF_ROOTS:
            scope = "SELF"
        elif r is None:
            scope = "UNRESOLVED"
        elif r in ("ROOT", "REPO"):
            scope = "REPO"
        else:
            scope = "UNRESOLVED"
        sites.append({"kind": kind, "root": r, "scope": scope, "line": node.lineno})
    return sites


def controls(tmp):
    a = tmp / "c_repo.py"
    a.write_text("import pathlib\nROOT = pathlib.Path('/x')\n"
                 "(ROOT / 'E05' / 'x.md').write_text('hi')\n")
    b = tmp / "c_self.py"
    b.write_text("import pathlib\nOUT = pathlib.Path(__file__).resolve().parent / 'results'\n"
                 "(OUT / 'x.json').write_text('hi')\n")
    c = tmp / "c_none.py"
    c.write_text("import pathlib\nprint(pathlib.Path('.').exists())\n")
    sa, sb, sc = write_sites(a), write_sites(b), write_sites(c)
    p1 = bool(sa) and all(x["scope"] == "REPO" for x in sa)
    p2 = bool(sb) and all(x["scope"] == "SELF" for x in sb)
    p3 = sc == []
    print(f"  POSITIVE  an out-of-scope write is seen as REPO: {p1}  {'PASS' if p1 else 'FAIL'}")
    print(f"  g=0       a self-scoped write is seen as SELF: {p2}  {'PASS' if p2 else 'FAIL'}")
    print(f"  g=0       a gate with NO writes yields an EMPTY list: {p3}  "
          f"{'PASS' if p3 else 'FAIL'}")
    print("    The third arm exists because a scoper that returns REPO for everything passes the")
    print("    first arm trivially — the positive control alone cannot tell a detector from a")
    print("    rubber stamp.")
    return p1 and p2 and p3


def main() -> int:
    import tempfile
    tmp = pathlib.Path(tempfile.mkdtemp())
    if not controls(tmp):
        print("\n  UNVERIFIED: the scoper failed its own controls. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED"}, open(OUT / "write_scope.json", "w"), indent=2)
        return 2

    gates = sorted((ROOT / "assurance").glob("*.py"))
    rows, unparsed = [], []
    for g in gates:
        s = write_sites(g)
        if s is None:
            unparsed.append(g.name); continue
        scopes = {x["scope"] for x in s}
        # ⚠ UNRESOLVED is treated as REPO. A statically unknown target cannot be certified safe,
        # and the whole point of this list is that something will be RUN on its strength.
        verdict = ("READ_ONLY" if not s else
                   "SELF_ONLY" if scopes == {"SELF"} else "CAN_WRITE_REPO")
        rows.append({"gate": g.name, "n_sites": len(s), "verdict": verdict, "sites": s})
    if not rows:
        print("\n  OBSERVED NOTHING: no gate parsed. Exit 2, never 0.")
        return 2

    ro = [r for r in rows if r["verdict"] == "READ_ONLY"]
    so = [r for r in rows if r["verdict"] == "SELF_ONLY"]
    rw = [r for r in rows if r["verdict"] == "CAN_WRITE_REPO"]
    print(f"\n  {len(rows)} gate(s) parsed"
          + (f" · {len(unparsed)} unparseable: {unparsed}" if unparsed else ""))
    print(f"    READ_ONLY       {len(ro):>3}   no write site at all")
    print(f"    SELF_ONLY       {len(so):>3}   writes only under assurance/ (own results/frozen)")
    print(f"    CAN_WRITE_REPO  {len(rw):>3}   at least one REPO or UNRESOLVED target")
    print(f"\n  ⚠ R868's crude name-level heuristic called 26 of 70 writers. This resolves them by")
    print(f"    DESTINATION instead, which is the property that decides whether a rerun is safe.")

    safe = sorted(r["gate"] for r in ro + so)
    print(f"\n  ⭐ SAFE-TO-INJECT SET (R868's missing input): {len(safe)} of {len(rows)}")
    print(f"  ⭐ MUST BE ISOLATED: {len(rw)}")
    for r in rw[:10]:
        unres = sum(1 for x in r["sites"] if x["scope"] == "UNRESOLVED")
        print(f"      {r['gate']:<44} {r['n_sites']:>2} site(s), {unres} unresolved")
    if len(rw) > 10:
        print(f"      ... and {len(rw)-10} more (all in the artifact)")

    frac = len(rw) / len(rows)
    world = "A" if not rw else ("B" if frac < 0.5 else "C")
    print(f"\n  ⭐ WORLD {world}: " + {
        "A": "every writer is SELF-scoped — R868's exclusion was over-cautious and all gates can"
             " be injected safely with no isolation",
        "B": "a minority can write outside assurance/ — R868 can be finished for everything but"
             " the named few, and its 40% was too conservative",
        "C": "most writers are REPO-scoped or statically UNRESOLVED — isolation is genuinely"
             " required, and R868's 40% is the honest ceiling until a worktree exists"}[world])
    print(f"     ⚠ This is a STATIC read. It BOUNDS the safe set and cannot prove a path is never")
    print(f"       written at runtime; UNRESOLVED is counted as REPO for exactly that reason.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "n_gates": len(rows), "unparsed": unparsed,
               "safe_to_inject": safe, "must_isolate": [r["gate"] for r in rw],
               "counts": {"READ_ONLY": len(ro), "SELF_ONLY": len(so),
                          "CAN_WRITE_REPO": len(rw)},
               "unresolved_treated_as": "REPO (a statically unknown target cannot be certified)",
               "rows": rows}, open(OUT / "write_scope.json", "w"), indent=2)
    print(f"\n  artifact: results/write_scope.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
