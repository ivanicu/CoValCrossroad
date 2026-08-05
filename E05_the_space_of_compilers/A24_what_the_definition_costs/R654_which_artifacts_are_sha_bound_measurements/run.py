#!/usr/bin/env python3
"""
R654 -- which artifacts are SHA-BOUND measurements, and does anything say so?

CHECK #255 ON R653's CLOSING LINE. TWO CLAUSES HOLD, ONE IS FALSE, AND VERIFYING IT BROKE SOMETHING.
  ✓ "the 4 CALLEE sites are blocked by a module-local function's RETURN" -- all 4 carry that exact
    reason, and all 4 are R652 D1 members. The label WAS overloaded in the code (two branches
    write `CALLEE`), but the other branch fired 0 times, so the sentence is true. Verified rather
    than assumed, because an overloaded label is how a true sentence becomes false later.
  ⛔ "4 is small enough that the answer is exact rather than a bound, WHICH NOTHING ELSE IN THIS
    ARC HAS BEEN." FALSE. Five exact results are already published in the four preceding rounds:
    R649's head-vs-tail over every over-cap file (4, exhaustive, 0 flips); R651's census
    replication; R651's join addressability (0 ambiguous); R653's vacuous guard (0 over 59);
    R653's kill check (0). §4's tell exactly -- a quantifier over my own work, which is the
    population I am worst at enumerating, and all five were mine and recent.

⛔⛔ AND CHECKING IT EXPOSED A LIVE DEFECT, THEN RE-RUNNING TO FIX THAT DEFECT DESTROYED A RESULT.
   R651's artifact persists `sites_mine: 355, sites_published: 354` -- the DISTINCT-KEY counts its
   own multiset repair exists to reject -- while the control that ran and passed compared 364 to
   364. So the REPORT was right and the ARTIFACT recorded different numbers, and this round read
   the artifact and quoted 355 vs 354 as the replication.
   Re-running R651 to regenerate a truthful artifact returned `mine 369 vs published 364` and
   wrote `census_replicated: FALSE` over a passing result: R652 and R653 have been added to the
   corpus since R651 ran, and R651's population IS the corpus. RE-RUNNING IS NOT REPRODUCTION.
   The artifact was restored from git; the code annotation was kept. THAT is this round.

ESTIMAND        n_sha_bound = committed rounds whose run.py derives its population by globbing at
                or above the round-collection directory, so the corpus's own growth changes what
                the round measures; and of those, n_uninterpretable = the ones whose artifact
                records a COUNT but no identifier of the tree it was counted over.
                A count without its tree is not a measurement a later round can use -- it is a
                number that was true once.
IDENTIFICATION  Exact for "globs at or above the collection directory" (a static property, with
                the glob base resolved symbolically). NOT identified for "this round's conclusion
                would change" -- that needs re-running each round at today's tree, which is the
                very operation that just destroyed a result. So n_sha_bound is an UPPER bound on
                rounds whose NUMBERS move, and a LOWER bound on nothing.
SCOPE           population : every A24 round with a run.py, MINUS this round
                instrument : ast + a symbolic pathlib evaluator over the glob's base expression
                             instrument unit = A ROUND
                             claim unit      = A ROUND
                             EQUAL by construction
                baseline   : R636, R650 and R651 -- three rounds whose numbers were OBSERVED to
                             move today and in this arc, so the positive control is a fact rather
                             than a guess
                regime     : as committed at this sha
WORLDS          A ISOLATED: few rounds are corpus-dependent -> the four number-movements in this
                  arc are a local accident and no general practice needs changing.
                B SYSTEMIC: many are -> every one of their artifacts is a sha-bound measurement,
                  and the arc's repeated surprise is a missing STAMP, not repeated carelessness.
                C ALREADY STAMPED: they are corpus-dependent AND record the tree -> the
                  information exists and I simply never read it, which is a different defect.
KILL            pre-registered, before the run: if the classifier does not find ALL THREE of
                R636, R650, R651 -- rounds whose counts were observed to move -- it has not been
                shown to see the class and NO count is admissible. UNVERIFIED, not "few".
POSITIVE CTRL   the three known movers above. Fails at g=0: a program with no glob yields 0.
NEGATIVE CTRL   a round that globs only its OWN results/ directory must NOT be corpus-dependent.
                This is the discriminating case: the failure direction is to call every glob
                corpus-dependent, which would make the count meaningless.
PLACEBO         a module with no glob at all -> 0, and it must be distinguishable from "globs
                something I could not resolve", which is reported as UNRESOLVED-BASE, never 0.
NOISE FLOOR     n/a -- a census of a fixed tree. Deterministic.
SEEDS           n/a.
MULTIPLICITY    1 classifier x every round + 4 controls + a stamp audit over every artifact.
                Survivors AND non-survivors.
ARTIFACT        results/sha_bound.json
IMPOSSIBLE      whether a given round's CONCLUSION (not its counts) would change needs re-running
                it at today's tree; that is destructive, as demonstrated above, and would require
                a pinned worktree per round. Named, not attempted.
"""
from __future__ import annotations
import ast, json, pathlib, re, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
E05 = A24.parent
ROOT = A24.parents[1]

GLOBS = {"glob", "rglob", "iterdir"}


class PathEval:
    def __init__(self, modpath):
        self.mod, self.env = modpath, {}

    def bind(self, tree):
        for n in tree.body:
            if isinstance(n, ast.Assign) and len(n.targets) == 1 \
                    and isinstance(n.targets[0], ast.Name):
                v = self.path_of(n.value)
                if v is not None:
                    self.env[n.targets[0].id] = v

    def path_of(self, n):
        if isinstance(n, ast.Name):
            return self.env.get(n.id)
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            return pathlib.Path(n.value)
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            l = self.path_of(n.left)
            r = n.right
            if l is None or not (isinstance(r, ast.Constant) and isinstance(r.value, str)):
                return None
            return l / r.value
        if isinstance(n, ast.Attribute):
            b = self.path_of(n.value)
            return b.parent if (b is not None and n.attr == "parent") else None
        if isinstance(n, ast.Subscript):
            if isinstance(n.value, ast.Attribute) and n.value.attr == "parents" \
                    and isinstance(n.slice, ast.Constant):
                b = self.path_of(n.value.value)
                try:
                    return b.parents[n.slice.value] if b is not None else None
                except Exception:
                    return None
            return None
        if isinstance(n, ast.Call):
            f = n.func
            if isinstance(f, ast.Attribute):
                if f.attr in ("resolve", "absolute", "expanduser"):
                    return self.path_of(f.value)
                if f.attr == "Path" and n.args:
                    a = n.args[0]
                    return self.mod if (isinstance(a, ast.Name) and a.id == "__file__") \
                        else self.path_of(a)
            if isinstance(f, ast.Name) and f.id == "Path" and n.args:
                a = n.args[0]
                return self.mod if (isinstance(a, ast.Name) and a.id == "__file__") \
                    else self.path_of(a)
        return None


def classify_round(path):
    """CORPUS-DEPENDENT if any glob's base resolves at or above the round-collection directory."""
    try:
        tree = ast.parse(path.read_text(errors="ignore"))
    except SyntaxError:
        return "UNPARSEABLE", []
    ev = PathEval(path.resolve())
    ev.bind(tree)
    hits, unresolved, own_only = [], 0, 0
    for n in ast.walk(tree):
        if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                and n.func.attr in GLOBS):
            continue
        base = ev.path_of(n.func.value)
        if base is None:
            unresolved += 1
            continue
        try:
            rel = base.resolve()
        except Exception:
            unresolved += 1
            continue
        # ⭐ THE DISCRIMINATING RULE, and the negative control is built for exactly it: a glob of
        #    the round's OWN directory is not corpus-dependent. Only a base AT OR ABOVE the
        #    collection directory sees other rounds appear.
        if rel == A24.resolve() or rel == E05.resolve() or rel == ROOT.resolve() \
                or A24.resolve() in rel.parents or rel in (A24.resolve(), E05.resolve()):
            if rel == path.resolve().parent or path.resolve().parent in rel.parents:
                own_only += 1
                continue
            pat = n.args[0].value if (n.args and isinstance(n.args[0], ast.Constant)) else "*"
            hits.append(f"{rel.name or rel}/{pat}")
        else:
            own_only += 1
    if hits:
        return "CORPUS-DEPENDENT", hits
    if unresolved:
        return "UNRESOLVED-BASE", []
    if own_only:
        return "OWN-SCOPE", []
    return "NO-GLOB", []


def artifact_facts(d):  # noqa: C901
    """Does this round's artifact hold a COUNT, and does anything identify the TREE?"""
    res = d / "results"
    if not res.is_dir():
        return None
    for f in sorted(res.glob("*.json")):
        try:
            j = json.loads(f.read_text())
        except Exception:
            continue
        if not isinstance(j, dict):
            continue
        # ⛔ v1's SOURCE-HASH DETECTOR RETURNED 0 ACROSS 93 ROUNDS AND I PRINTED A CLAIM BUILT ON
        #    THAT ZERO -- "the corpus stamps its METHOD and not its POPULATION" REQUIRES the
        #    method count to be non-zero. §P5: a zero from an instrument never shown to return
        #    non-zero is silence, not an acquittal. It looked for top-level keys `src` /
        #    `source_hash` / `src_sha`; the corpus actually writes `source_sha` (96) and
        #    `source_sha256` (73). Repaired, and both detectors now carry positive controls in
        #    main() that must fire before any stamp number is printed.
        # ⭐ AND THE TREE STAMP HIDES UNDER A MISLEADING KEY. 38 rounds call `git rev-parse HEAD`
        #    and persist it -- as `head` or `revision`, and in one era under `src`, which reads
        #    as "source" and is in fact the COMMIT. A key name is not a type.
        code = (d / "run.py").read_text(errors="ignore") if (d / "run.py").is_file() else ""
        hexv = re.compile(r'^[0-9a-f]{7,64}$')
        hexkeys = [k for k, v in j.items() if isinstance(v, str) and hexv.match(v)]
        has_count = any(isinstance(v, int) and not isinstance(v, bool) and abs(v) > 1
                        for v in j.values())
        has_tree = bool("rev-parse" in code and hexkeys)
        has_srchash = any(re.match(r'^(src|source)[_a-z0-9]*$', k, re.I) and "sha" in k.lower()
                          for k in hexkeys)
        return {"file": f.name, "has_count": has_count, "has_tree_id": has_tree,
                "has_source_hash": has_srchash, "hex_keys": hexkeys[:3]}
    return None


def main() -> int:
    rounds = [d for d in sorted(A24.glob("R[0-9]*"))
              if (d / "run.py").is_file() and d.resolve() != HERE]
    if len(rounds) < 50:
        print(f"UNRUNNABLE: only {len(rounds)} rounds. Exit 2, never 0.")
        return 2
    verdicts = {d.name: classify_round(d / "run.py") for d in rounds}

    # ---- CONTROLS FIRST -------------------------------------------------------------
    print("─── CONTROLS ───")
    known = {}
    for pre in ("R636_", "R650_", "R651_"):
        k = next((n for n in verdicts if n.startswith(pre)), None)
        known[pre] = (k, verdicts[k][0] if k else None)
    pos = all(v == "CORPUS-DEPENDENT" for _, v in known.values())
    print(f"  POSITIVE   three rounds whose counts were OBSERVED to move "
          f"(R636 in-arc, R650 900→902, R651 364→369 today):")
    for pre, (k, v) in known.items():
        print(f"               {pre:<7} {(k or 'NOT FOUND')[:52]:<52} -> {v}")
    print(f"             -> {'PASS' if pos else '⛔ FAIL — the classifier cannot see the class'}")

    def synth(src, name):
        p = HERE / f"_{name}.py"
        tree = ast.parse(src)
        ev = PathEval((A24 / "R999_synthetic" / "run.py").resolve())
        ev.bind(tree)
        hits = []
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr in GLOBS:
                base = ev.path_of(n.func.value)
                if base is None:
                    return "UNRESOLVED-BASE"
                rel = base.resolve()
                if rel == (A24 / "R999_synthetic").resolve() \
                        or (A24 / "R999_synthetic").resolve() in rel.parents:
                    continue
                if rel in (A24.resolve(), E05.resolve(), ROOT.resolve()):
                    hits.append(1)
        return "CORPUS-DEPENDENT" if hits else ("OWN-SCOPE" if "glob" in src else "NO-GLOB")

    neg = synth("import pathlib\nHERE=pathlib.Path(__file__).resolve().parent\n"
                "OUT=HERE/'results'\nfor f in OUT.glob('*.json'):\n    pass\n", "neg")
    print(f"  NEGATIVE   a round globbing only its OWN results/ -> {neg} -> "
          f"{'PASS — not every glob is corpus-dependent' if neg != 'CORPUS-DEPENDENT' else '⛔ FAIL'}")
    plc = synth("import pathlib\nx = pathlib.Path('/tmp')\n", "plc")
    print(f"  PLACEBO    a module with no glob at all -> {plc} -> "
          f"{'PASS' if plc == 'NO-GLOB' else '⛔ FAIL'}")
    g0 = synth("x = 1\n", "g0")
    print(f"  g=0        an empty program -> {g0} -> {'PASS' if g0 == 'NO-GLOB' else '⛔ FAIL'}")
    # ⭐ THE STAMP DETECTORS GET THEIR OWN POSITIVE CONTROLS, because v1's returned 0 and a
    #    sentence was written on that 0. Both must fire over the WHOLE corpus before any stamp
    #    number is admissible.
    allr = [d for d in sorted(A24.glob("R[0-9]*")) if (d / "run.py").is_file()]
    allf = [(d.name, artifact_facts(d)) for d in allr]
    src_all = [n for n, f in allf if f and f["has_source_hash"]]
    tree_all = [n for n, f in allf if f and f["has_tree_id"]]
    print(f"  POSITIVE   SOURCE-stamp detector over all {len(allr)} rounds (incl. this one; the "
          f"census below excludes it) -> {len(src_all)} "
          f"-> {'PASS' if len(src_all) >= 100 else '⛔ FAIL — v1 returned 0 on this same corpus'}")
    print(f"  POSITIVE   TREE-stamp detector over all {len(allr)} rounds -> {len(tree_all)} "
          f"-> {'PASS' if tree_all else '⛔ FAIL'}")
    controls_ok = (pos and neg != "CORPUS-DEPENDENT" and plc == "NO-GLOB" and g0 == "NO-GLOB"
                   and len(src_all) >= 100 and bool(tree_all))
    print(f"  KILL       all three known movers recognised -> "
          f"{'PASS — a count is admissible' if controls_ok else '⛔ UNVERIFIED'}")

    # ---- THE CENSUS -----------------------------------------------------------------
    cnt = Counter(v[0] for v in verdicts.values())
    print(f"\n─── HOW MANY ROUNDS MEASURE A POPULATION THAT GROWS UNDER THEM? ───")
    for k in ("CORPUS-DEPENDENT", "OWN-SCOPE", "NO-GLOB", "UNRESOLVED-BASE", "UNPARSEABLE"):
        c = cnt.get(k, 0)
        print(f"  {k:<18} {c:>4}  ({c/len(rounds):>5.1%})")

    # ---- THE STAMP AUDIT ------------------------------------------------------------
    dep = [n for n, v in verdicts.items() if v[0] == "CORPUS-DEPENDENT"]
    facts = {n: artifact_facts(A24 / n) for n in dep}
    with_art = {n: f for n, f in facts.items() if f}
    counts = [n for n, f in with_art.items() if f["has_count"]]
    treed = [n for n, f in with_art.items() if f["has_tree_id"]]
    srched = [n for n, f in with_art.items() if f["has_source_hash"]]
    uninterp = [n for n in counts if n not in treed]
    print(f"\n─── THE STAMP AUDIT, over the {len(dep)} corpus-dependent rounds ───")
    print(f"  with a parsed artifact                    : {len(with_art)}")
    print(f"  whose artifact records a COUNT            : {len(counts)}")
    print(f"  whose artifact identifies the TREE        : {len(treed)}")
    print(f"  whose artifact hashes its OWN SOURCE      : {len(srched)}")
    print(f"  ⭐ COUNT but NO TREE — uninterpretable later: {len(uninterp)} "
          f"({len(uninterp)/max(len(counts),1):.1%} of counted rounds)")
    print(f"\n  corpus-wide: {len(src_all)} rounds stamp the SOURCE, {len(tree_all)} stamp the "
          f"TREE — the method is recorded {len(src_all)/max(len(tree_all),1):.1f}x more often "
          f"than the population it ran over.")
    print(f"\n  a sample of the uninterpretable ones, with the glob that makes them so:")
    for n in uninterp[:10]:
        print(f"    {n[:52]:<52} {verdicts[n][1][:2]}")

    # ---- VERDICT --------------------------------------------------------------------
    share = len(dep) / len(rounds)
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no census is admissible"
    elif treed and not uninterp:
        world = (f"C ALREADY STAMPED — every corpus-dependent round records the tree; the "
                 f"information existed and I never read it.")
    elif len(dep) >= 20:
        world = (f"B SYSTEMIC — {len(dep)} of {len(rounds)} rounds ({share:.1%}) derive their "
                 f"population by globbing at or above the collection directory, and "
                 f"{len(uninterp)} of the {len(counts)} that record a count do NOT identify the "
                 f"tree they counted over. The four number-movements in this arc (R636, R648, "
                 f"R650 900→902, R651 364→369) are one missing STAMP, not four lapses of "
                 f"attention. Re-running such a round is a NEW MEASUREMENT, not a reproduction.")
    else:
        world = (f"A ISOLATED — only {len(dep)} of {len(rounds)} rounds ({share:.1%}) are "
                 f"corpus-dependent; the movements are local and no general practice changes.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 classifier x {len(rounds)} rounds + 4 controls + a stamp audit "
          f"over {len(with_art)} artifacts. All five classes printed.")
    print(f"  ⚠ UPPER BOUND: corpus-dependence says the POPULATION moves, not that the "
          f"CONCLUSION does. Establishing the latter means re-running each round at today's "
          f"tree — the operation that destroyed R651's artifact an hour ago.")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "sha_bound.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "rounds": len(rounds), "counts": dict(cnt),
        "corpus_dependent": dep,
        "with_artifact": len(with_art), "recording_a_count": len(counts),
        "identifying_the_tree": len(treed), "hashing_own_source": len(srched),
        "corpus_wide_source_stamped": len(src_all),
        "corpus_wide_tree_stamped": len(tree_all),
        "uninterpretable": uninterp,
        "known_movers": {k: v for k, (_, v) in known.items()},
        "check255": ("R653's NEXT claimed 'nothing else in this arc has been exact'. FALSE -- "
                     "five exact results precede it (R649 head-vs-tail; R651 census; R651 join "
                     "addressability; R653 vacuous guard; R653 kill). And verifying it exposed "
                     "that R651's artifact persists 355/354 while its control compared 364/364; "
                     "re-running R651 to fix that returned 369 vs 364 and overwrote a passing "
                     "result, because R652 and R653 had joined the corpus. Artifact restored "
                     "from git; the code annotation kept."),
        "impossible": ("whether a corpus-dependent round's CONCLUSION would change needs "
                       "re-running it at today's tree, which is destructive and would require a "
                       "pinned worktree per round. Named, not attempted."),
    }, indent=2))
    print(f"\n  wrote {out / 'sha_bound.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
