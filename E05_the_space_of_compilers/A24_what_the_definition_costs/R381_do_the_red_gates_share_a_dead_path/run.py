"""R381 — do the red gates share one dead path, or does each have its own?

R380 repaired one gate whose glob matched 0 files while the tree held 363, and closed with:
"[HYPOTHESIS] I expect `rounds/` to be a dead directory that several gates still point at ... checkable
for free by grepping every assurance script for the literal `rounds/` prefix."

⛔ THE PROPOSED INSTRUMENT PRESUPPOSES ITS OWN ANSWER. Grepping for `rounds/` can only find gates
   that are dead in the ONE way I already found. A gate pointing at `campaigns/`, or at a path that
   was renamed for an unrelated reason, is invisible to it -- so a zero would read as "no others"
   when it means "none of the kind I looked for". The instrument's unit would be `the string I
   guessed`, and the claim's unit is `a path expression that resolves to nothing`. Not equal.

   So the extraction is done with `ast` instead: EVERY string literal in every assurance module is
   parsed out, the path-shaped ones are handed to the filesystem, and the ones matching nothing are
   reported. That asks the tree rather than my memory, and it can find a dead path I have never seen.

⭐ AND THE POSITIVE CONTROL HAS AN ANSWER ESTABLISHED BY AN EARLIER ROUND, not by this one. R380
   measured that `donor_numbers_carry_their_draw_scope` contained `rounds/E*/A*/R*/run.py` matching
   0 of 363. That file is now repaired, so the control reads the PRE-REPAIR version out of git and
   requires the extractor to flag exactly that literal. A extractor that cannot re-find a known dead
   path is blind, and every "no dead paths here" it prints would be silence.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES on both counts.
   The number of gates carrying a dead path is free to be zero, one, or all ten. And a literal
   matching zero files is NOT automatically a defect -- a script may build paths dynamically, or
   hold a fragment that is joined later. So a raw count of zero-matching literals would be an
   inflated numerator by construction. It is therefore JOINED to an independent fact: R379 measured,
   by audit hook, how many round artifacts each gate actually OPENS. A gate that both carries a
   dead round-path literal AND opens zero round artifacts is the strong signal; either alone is not.

ESTIMAND        (a) per assurance module, the set of path-shaped string literals that match ZERO
                    files in the tree;
                (b) the join of (a) with R379's measured read-sets: which red gates carry a dead
                    round-path literal AND open zero round artifacts;
                (c) whether the ten red gates share ONE dead path or carry distinct ones.

IDENTIFICATION  (a) is exact for literals reachable by `ast` -- an f-string or a path assembled at
                runtime is invisible, and that is a bound, not a caveat to wave at. (b) is exact.
                NOT identified: whether a dead literal is the CAUSE of a gate's failure. R380 needed
                a whole round to establish that for ONE gate; this locates candidates.

SCOPE           population: every *.py in assurance/ · instrument: `ast` literal extraction plus
                `Path.glob` · baseline: R379's committed read-sets · regime: HEAD.

WORLDS
  W-ONE-DEAD-PATH   several red gates carry the SAME dead path prefix. They are one fix, and the
                    repair order R378 ruled out on gate-coupling grounds returns on path grounds.
  W-EACH-ITS-OWN    the dead paths are distinct or absent. R380's repair generalises to nothing and
                    each remaining gate is its own round.
  W-NOT-A-PATH-PROBLEM  no red gate besides the one already repaired carries a dead path at all.
                    Then paths are not the shared mechanism and the search moves elsewhere.

PREDICTION MATRIX
  W-ONE-DEAD-PATH      -> >=2 red gates share a dead prefix
  W-EACH-ITS-OWN       -> >=2 red gates have dead literals, no shared prefix
  W-NOT-A-PATH-PROBLEM -> 0 red gates (post-R380) carry a dead round-path literal

PRE-REGISTERED KILL -- conditional on the controls, never on a count alone.
    if extractor_positive_control_ok and extractor_negative_control_ok:
        s = number of red gates carrying a dead ROUND-path literal
        if s == 0                          -> W-NOT-A-PATH-PROBLEM
        elif a prefix is shared by >= 2     -> W-ONE-DEAD-PATH, and the prefix is named
        else                                -> W-EACH-ITS-OWN
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  EXTRACTOR (+)  the PRE-REPAIR `donor_numbers_carry_their_draw_scope.py`, read out of git, must be
                 flagged carrying `rounds/E*/A*/R*/run.py`. The answer comes from R380, not here.
  EXTRACTOR (-)  a live glob (`E0*/A*/R*/run.py`) must NOT be flagged, and the post-repair version
                 of the same file must come back clean. Both directions, because an extractor that
                 flagged every literal would pass the positive control.
  JOIN           a dead literal alone is not a defect. Every claim is joined to R379's independently
                 measured read-set, and the two counts are reported separately so the join is
                 visible rather than assumed.
  BOUND          literals built at runtime are invisible to `ast`. The count of f-strings and
                 concatenations in each module is reported beside the result, so the blind spot has
                 a size instead of a disclaimer.

MULTIPLICITY    no test family. Every module and every flagged literal is printed.
SEEDS           none -- ast and glob are deterministic.
ARTIFACT        results/r381_dead_paths.json with the source hash.

IMPOSSIBLE HERE
  runtime-assembled paths  -- invisible to `ast`; counted and reported, not waved away.
  whether a dead literal CAUSES a failure -- R380 spent a round proving that for one gate.
  a second release         -- one release.

EXIT
    0  controls hold and the ten are classified
    1  a control misbehaved -- UNVERIFIED
    2  the tree or the prior artifact is unreadable -- never a silent pass
"""
from __future__ import annotations
import ast
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
ASSUR = ROOT / "assurance"
R379 = (ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
        / "R379_the_exit_code_is_not_the_population" / "results" / "r379_read_sets.json")
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

GATE = "donor_numbers_carry_their_draw_scope.py"
KNOWN_DEAD = "rounds/E*/A*/R*/run.py"
KNOWN_LIVE = "E0*/A*/R*/run.py"


REGEX_META = ("\\", "[", "(?", "]", "+)", ".*", "|")


def looks_like_regex(s: str) -> bool:
    """⛔ ADDED AFTER THE FIRST RUN, because `glob` is the WRONG TEST for a regex and the verdict
    was about to rest on two items that are not paths. `donor_numbers...` was flagged for
    `rounds/r8[89]_[a-z_]+\)` -- a PATTERN matched against README text, never globbed -- and
    asking the filesystem whether it exists answers a question nobody posed. A regex encoding a
    stale link format IS a real candidate class, but it needs its own instrument (does it match
    anything in the documents it is applied to?), so it is separated here and NOT counted."""
    return any(m in s for m in REGEX_META)


def path_shaped(s: str) -> bool:
    """A literal worth asking the filesystem about. Deliberately narrow: a path expression has a
    separator, no whitespace, and is not a URL or a format template."""
    return ("/" in s and len(s) > 3 and not any(c.isspace() for c in s)
            and "://" not in s and "{" not in s and "%" not in s
            and not s.startswith(("http", "git@")))


def _chain(node):
    """Reconstruct `ROOT / "a" / "b"` into `a/b`. Returns None if any part is not a literal."""
    if isinstance(node, ast.Name):
        return "" if node.id in ("ROOT", "_ROOT", "HERE", "ASSUR") else None
    if isinstance(node, ast.Attribute):
        return "" if node.attr in ("parent", "resolve") else None
    if isinstance(node, ast.Call):
        return _chain(node.func.value) if isinstance(node.func, ast.Attribute) else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _chain(node.left)
        if left is None or not isinstance(node.right, ast.Constant) \
                or not isinstance(node.right.value, str):
            return None
        return (left + "/" + node.right.value).lstrip("/")
    return None


def literals(src: str):
    """-> (path EXPRESSIONS, count of runtime-assembled ones)

    ⛔ v1 EXTRACTED LITERALS AND ITS POSITIVE CONTROL CAUGHT IT. R380's dead path is written
      `(ROOT / "rounds").glob("E*/A*/R*/run.py")` -- TWO literals, and neither is dead alone:
      `"rounds"` has no separator, and `"E*/A*/R*/run.py"` matches 363 files relative to ROOT.
      So the dead path is not a literal at all, it is a COMPOSITION, and an extractor whose unit
      is `a string literal` cannot see it while the claim's unit is `a path expression that
      resolves to nothing`. That is the same unit mismatch this round's docstring was written to
      avoid, committed one level down. The control had its answer from a PRIOR round, which is the
      only reason it could fail here rather than after publication.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return set(), -1
    exprs, dynamic = set(), 0
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            if path_shaped(n.value):
                exprs.add(n.value)
        elif isinstance(n, ast.JoinedStr):
            dynamic += 1
        elif isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in ("glob", "rglob") and n.args:
            base = _chain(n.func.value)
            arg = n.args[0]
            if base is not None and isinstance(arg, ast.Constant) \
                    and isinstance(arg.value, str):
                exprs.add((base + "/" + arg.value).lstrip("/"))
            else:
                dynamic += 1
        elif isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div):
            c = _chain(n)
            if c and path_shaped(c):
                exprs.add(c)
    # ⛔ A LITERAL WRITTEN *INTO* TEXT IS NOT A PATH READ FROM DISK, and `glob` is the wrong test
    #   for it too. `attack_every_check` contains `text.replace(<real round>, "rounds/_no_such_round")`
    #   -- the replacement is a path DESIGNED not to exist, planted to make a check fire. It was
    #   the last surviving candidate and it is a false positive by construction. The exclusion is
    #   STRUCTURAL (the second argument of a `.replace` call) rather than a word list, so it does
    #   not depend on the fixture being named `_no_such_anything`.
    written = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr == "replace" and len(n.args) >= 2:
            a = n.args[1]
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                written.add(a.value)
    return exprs - written, dynamic


def dead(lits):
    """literals that match NOTHING under ROOT. `glob` on a non-pattern still tests existence."""
    out = []
    for s in sorted(lits):
        try:
            if list(ROOT.glob(s.lstrip("/"))):
                continue
            if (ROOT / s.lstrip("/")).exists():
                continue
        except (ValueError, OSError):
            continue
        out.append(s)
    return out


def main() -> int:
    if not ASSUR.exists():
        print("  UNRUNNABLE: assurance/ absent. Exit 2, never 0."); return 2
    if not R379.exists():
        print("  UNRUNNABLE: R379's read-sets absent — the join has no second side. Exit 2.")
        return 2
    reads = json.loads(R379.read_text())["rows"]
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R381 · do the red gates share a dead path?   HEAD {head}\n")
    print(f"  ⛔ R380's NEXT proposed grepping for `rounds/`. That instrument can only find gates")
    print(f"     dead in the ONE way already known, so a zero would read as `no others` while")
    print(f"     meaning `none of the kind I looked for`. Every path-shaped LITERAL is extracted")
    print(f"     with `ast` instead, and handed to the filesystem.\n")

    # ---- CONTROLS -----------------------------------------------------------------------------
    pre = subprocess.run(["git", "show", f"efb2f2f~1:assurance/{GATE}"], cwd=str(ROOT),
                         capture_output=True, text=True)
    if pre.returncode != 0:
        pre = subprocess.run(["git", "show", f"HEAD~1:assurance/{GATE}"], cwd=str(ROOT),
                             capture_output=True, text=True)
    pre_lits, _ = literals(pre.stdout) if pre.returncode == 0 else (set(), 0)
    pre_dead = dead(pre_lits)
    pos_ok = KNOWN_DEAD in pre_dead
    post_lits, _ = literals((ASSUR / GATE).read_text())
    post_dead = dead(post_lits)
    neg_live_ok = KNOWN_LIVE not in dead({KNOWN_LIVE})
    neg_clean_ok = KNOWN_DEAD not in post_dead
    print("  CONTROLS on the extractor, against answers R380 established")
    print(f"    EXTRACTOR (+)  the PRE-REPAIR gate is flagged carrying `{KNOWN_DEAD}`: {pos_ok}  "
          f"{'PASS' if pos_ok else 'FAIL — blind to a dead path a prior round proved'}")
    print(f"    EXTRACTOR (-)  a live glob `{KNOWN_LIVE}` is NOT flagged: {neg_live_ok}")
    print(f"                   the POST-repair gate no longer carries it: {neg_clean_ok}  "
          f"{'PASS' if neg_live_ok and neg_clean_ok else 'FAIL'}")
    if not (pos_ok and neg_live_ok and neg_clean_ok):
        print("\n  UNVERIFIED — the extractor is blind in one direction. Exit 1."); return 1

    # ---- the sweep ----------------------------------------------------------------------------
    RED = sorted(reads)
    ROWS, dyn_total = {}, 0
    for p in sorted(ASSUR.glob("*.py")):
        lits, dyn = literals(p.read_text())
        d = dead(lits)
        dyn_total += max(dyn, 0)
        ROWS[p.name] = dict(n_literals=len(lits), dead=d, dynamic=dyn,
                            is_red=(p.stem in reads),
                            round_files=reads.get(p.stem, {}).get("round_files"))
    for k, v in ROWS.items():
        v["regexes"] = [x for x in v["dead"] if looks_like_regex(x)]
        v["dead"] = [x for x in v["dead"] if not looks_like_regex(x)]
    withdead = {k: v for k, v in ROWS.items() if v["dead"]}
    n_regex = sum(len(v["regexes"]) for v in ROWS.values())
    print(f"\n  SWEEP — {len(ROWS)} assurance modules, {sum(r['n_literals'] for r in ROWS.values())}"
          f" path-shaped literals")
    print(f"    modules carrying at least one literal that matches NOTHING: {len(withdead)}")
    print(f"    {'module':<46}{'red?':>6}{'opens':>7}   dead literals")
    for k in sorted(withdead):
        v = withdead[k]
        print(f"    {k:<46}{('RED' if v['is_red'] else '-'):>6}"
              f"{str(v['round_files']) if v['round_files'] is not None else '-':>7}   {v['dead']}")

    # ---- the join, which is what makes any of it a signal -------------------------------------
    ROUNDISH = ("rounds/", "E0", "R0", "R1", "R2", "R3")
    def roundpath(s):
        return any(t in s for t in ("rounds/", "/A", "/R")) or s.startswith(ROUNDISH)

    strong = {k: [s for s in v["dead"] if roundpath(s)]
              for k, v in withdead.items() if v["is_red"]}
    strong = {k: v for k, v in strong.items() if v}
    joined = {k: v for k, v in strong.items() if ROWS[k]["round_files"] == 0}
    print(f"\n  THE JOIN — a dead literal alone is not a defect")
    print(f"    RED gates carrying a dead ROUND-path literal          : {len(strong)}")
    print(f"    of those, gates R379 measured opening ZERO artifacts  : {len(joined)}")
    for k in sorted(joined):
        print(f"      {k}  opens {ROWS[k]['round_files']}  {joined[k]}")
    if strong and not joined:
        print(f"    ⚠ every candidate DOES open artifacts, so a dead literal here is not the")
        print(f"      mechanism — which is exactly what the join is for.")

    prefixes = {}
    for k, ss in strong.items():
        for s in ss:
            prefixes.setdefault(s.split("/")[0] + "/", set()).add(k)
    shared = {p: sorted(g) for p, g in prefixes.items() if len(g) >= 2}

    print(f"\n  SEPARATED, NOT COUNTED — {n_regex} flagged items are REGEXES, and `glob` is the")
    print(f"    wrong test for a pattern matched against text. Several encode a stale LINK format")
    print(f"    (e.g. `rounds/r8[89]_...`), which is a real candidate class needing its own")
    print(f"    instrument: does the pattern match anything in the documents it is applied to?")
    for k, v in sorted(ROWS.items()):
        if v["regexes"] and v["is_red"]:
            print(f"      RED {k}: {v['regexes']}")

    print(f"\n  BOUND — literals assembled at runtime are invisible to `ast`:")
    print(f"    {dyn_total} f-string expressions across {len(ROWS)} modules. The blind spot has a")
    print(f"    size rather than a disclaimer, and a path built from an f-string is not counted.")

    # ---- verdict ------------------------------------------------------------------------------
    print()
    if not strong:
        print(f"  W-NOT-A-PATH-PROBLEM — no red gate besides the one R380 already repaired carries")
        print(f"  a dead round-path literal. Paths are not the shared mechanism, R380's repair")
        print(f"  generalises to nothing, and the search for what the nine share moves elsewhere.")
        v = "W_NOT_A_PATH_PROBLEM"
    elif shared:
        p0 = sorted(shared, key=lambda p: -len(shared[p]))[0]
        print(f"  W-ONE-DEAD-PATH — {len(shared[p0])} red gates share the dead prefix `{p0}`:")
        for k in shared[p0]:
            print(f"    · {k}")
        print(f"  They are ONE fix. R378 ruled out a repair ORDER on gate-coupling grounds; this")
        print(f"  returns it on path grounds, which is a different mechanism reaching the same")
        print(f"  practical conclusion.")
        v = "W_ONE_DEAD_PATH"
    else:
        print(f"  W-EACH-ITS-OWN — {len(strong)} red gate(s) carry a dead round-path literal and no")
        print(f"  prefix is shared by two of them. R380's repair does not generalise: each")
        print(f"  remaining gate is its own round, and the rate measured there — one round per")
        print(f"  gate — is the rate to plan with.")
        v = "W_EACH_ITS_OWN"

    print(f"\n  ⚠ SCOPE: this LOCATES candidates. It does not establish that a dead literal CAUSES")
    print(f"    any gate's failure — R380 needed a whole round to prove that for one gate, with a")
    print(f"    disarm proof at the end. Nothing here substitutes for that.")

    art = dict(stamp(str(SELF)), head=head, modules=ROWS, with_dead=sorted(withdead),
               strong=strong, joined=sorted(joined), shared_prefixes={k: v for k, v in shared.items()},
               n_regex_separated=n_regex,
               regexes_in_red={k: v["regexes"] for k, v in ROWS.items() if v["regexes"] and v["is_red"]},
               dynamic_total=dyn_total,
               controls=dict(extractor_pos=pos_ok, extractor_neg_live=neg_live_ok,
                             extractor_neg_clean=neg_clean_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r381_dead_paths.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
