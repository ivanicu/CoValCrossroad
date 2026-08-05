#!/usr/bin/env python3
"""
R649 -- is the truncate-before-parse error in the CORPUS, or only in my shell commands?
        And where it is in the corpus, DOES THE CAP BIND?

CHECK #250 ON R648's CLOSING LINE. Verified, and it holds: "three rounds in this arc were spent
on truncations I introduced" -- R630 (`uh[:12]`), R646 (`git status | head -3`), R647
(`run_all.py | tail -25`). Three, computed, correct.
  ⚠ BUT THE LINE SKIPS THE DISTINCTION THAT MAKES THE RULE USABLE. "Never pipe an instrument's
    output through a truncating filter" is false as written: truncating for DISPLAY is correct
    and this corpus does it constantly. The error is truncating before a COUNT. A rule that
    forbids both is a rule that will be ignored.
  ⚠ AND A FIRST SYNTACTIC PASS PROVED THE POINT AGAINST ITSELF: splitting slices by "inside a
    print() or not" returned 587 suspects whose top rows are `hexdigest()[:16]`. A hash slice is
    not a truncation of a population. Discarded before it was reported; recorded here because it
    is the same instrument error the round is about.

ESTIMAND        n_blind = committed rounds whose run.py truncates a READ or a SUBPROCESS OUTPUT
                with a numeric cap and then SEARCHES OR COUNTS the result -- i.e. the cap sits
                between the data and the population statistic, not between the data and a print.
                And, separately, n_binding = how many of those caps are exceeded by a real file
                the corpus actually contains. A cap that never binds is inert.
IDENTIFICATION  PARTIAL, and reported as two bounds rather than a point:
                LOWER = slices applied DIRECTLY to a read/stdout expression (AST-decidable).
                UPPER = lower + slices applied to a NAME that is assigned from a read somewhere
                in the same file (name-level, so it over-counts by construction).
                The truth is between them. A point estimate here would be the arithmetic trap.
SCOPE           population : every committed A24 round with a run.py, MINUS this round
                instrument : ast.parse over each file; a slice is classified by the SHAPE of the
                             expression it is applied to, never by a regex over the line
                             instrument unit = A SLICE NODE IN A PARSED FILE
                             claim unit      = A ROUND IS BLIND TO PART OF ITS POPULATION
                             NOT EQUAL, and that is why n_binding exists: the slice is the site,
                             the binding test is what turns a site into blindness
                baseline   : display slices (inside a print / f-string), which are correct
                regime     : as committed at this sha, on the files now on disk
WORLDS          A SHELL-ONLY: the pattern lives in my interactive commands and not in code ->
                  the repair is an operating rule and nothing on disk needs changing.
                B PRESENT BUT INERT: sites exist and no real input exceeds their caps ->
                  R600's "inert today, correct later"; annotate, do not rewrite.
                C LIVE: at least one site's cap is exceeded by a file that site reads ->
                  a committed round is silently blind to part of its own population, and every
                  count that round reported is an underestimate of unknown size.
KILL            pre-registered with its threshold, before the run: if the classifier does not
                find R601 line 104 -- a KNOWN member, `f.read_text(...)[:200000]` feeding a regex
                search -- the instrument has not been shown to see the class and NO absence claim
                is admissible. UNVERIFIED, never "the corpus is clean".
POSITIVE CTRL   R601:104 must be classified READ-then-SEARCH. Fails at g=0: an empty source
                yields 0 sites, and a file containing only display slices yields 0.
NEGATIVE CTRL   `hashlib.sha256(...).hexdigest()[:16]` must NOT be classified. It is present in
                ~100 rounds and is the exact shape that destroyed the first pass.
                Also: a display slice inside print() must not be classified.
PLACEBO         a method name no file calls -> 0 sites.
NOISE FLOOR     n/a -- this is a census of a fixed tree, not a sample. Deterministic.
SEEDS           n/a, deterministic. Reproducibility: the count is a pure function of the tree.
MULTIPLICITY    1 classifier x every round x 4 control checks + 1 binding sweep over every cap.
                All reported, survivors and non-survivors.
ARTIFACT        results/truncation_sites.json -- every site with file:line and its cap, so a
                later round can attack the classification without re-deriving it.
IMPOSSIBLE      construct validity for "this round's CONCLUSION was wrong because of the cap":
                that needs re-running each round with the cap removed and diffing the artifact,
                which is a different round. This one establishes the site and the binding; it
                does NOT claim any published number is wrong. Named, not waved away.
                ⛔ RETRACTED BY THIS ROUND, BEFORE IT SHIPPED. The wall was never checked and it
                  does not hold: for a search-type site the question is not "re-run without the
                  cap" but "does the TAIL past the cap match where the HEAD does not", which is
                  one pass over the 4 over-cap files. §4's `a wall never checked` -- and an
                  impossibility asserted in the direction that saves work is the flattering
                  direction. The CONSEQUENCE section below runs it. What remains genuinely
                  impossible: the same question at a site whose read population is not
                  re-derivable from its own source (1 such site here, reported UNVERIFIED).
"""
from __future__ import annotations
import ast, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]

# expressions whose truncation removes DATA, not decoration
READ_CALLS = {"read_text", "read", "readlines", "getvalue"}
STREAM_ATTRS = {"stdout", "stderr"}
# the negative-control class: a slice of a digest is a fixed-width id, not a truncated corpus
HASH_CALLS = {"hexdigest", "digest"}
# consumers that make a slice load-bearing: the sliced value feeds a population statistic
SEARCH_CALLS = {"findall", "finditer", "search", "match", "count", "split", "splitlines",
                "index", "startswith", "endswith", "join", "sub"}


def cap_of(sl):
    """The numeric cap of a slice, or None if it is not a fixed truncation."""
    if not isinstance(sl, ast.Slice):
        return None
    for node in (sl.upper, sl.lower):
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return abs(node.value)
    return None


def chain_kind(node):
    """Walk an expression chain and say what the sliced object ULTIMATELY came from."""
    depth = 0
    while depth < 8:
        depth += 1
        if isinstance(node, ast.Call):
            f = node.func
            if isinstance(f, ast.Attribute):
                if f.attr in HASH_CALLS:
                    return "HASH"
                if f.attr in READ_CALLS:
                    return "READ"
                node = f.value
                continue
            return None
        if isinstance(node, ast.Attribute):
            if node.attr in STREAM_ATTRS:
                return "STREAM"
            node = node.value
            continue
        if isinstance(node, ast.Subscript):
            node = node.value
            continue
        return None
    return None


def analyse(src, path):
    """Return (lower_sites, upper_only_sites, display_slices, hash_slices)."""
    tree = ast.parse(src)
    parents = {}
    for p in ast.walk(tree):
        for c in ast.iter_child_nodes(p):
            parents[c] = p

    def in_display(n):
        """Inside a print(...) call or an f-string -> the truncation is decoration."""
        cur, d = n, 0
        while cur in parents and d < 12:
            cur, d = parents[cur], d + 1
            if isinstance(cur, ast.JoinedStr):
                return True
            if isinstance(cur, ast.Call) and isinstance(cur.func, ast.Name) \
                    and cur.func.id == "print":
                return True
        return False

    # names assigned anywhere in this file from a read/stream expression -> the UPPER bound
    read_names = set()
    for n in ast.walk(tree):
        if isinstance(n, (ast.Assign, ast.AugAssign)):
            val = n.value
            if chain_kind(val) in ("READ", "STREAM"):
                tgts = n.targets if isinstance(n, ast.Assign) else [n.target]
                for t in tgts:
                    if isinstance(t, ast.Name):
                        read_names.add(t.id)

    # names that are ever the RECEIVER or an ARGUMENT of a search/count call -> the population
    searched_names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in SEARCH_CALLS:
            if isinstance(n.func.value, ast.Name):
                searched_names.add(n.func.value.id)
            for a in n.args:
                if isinstance(a, ast.Name):
                    searched_names.add(a.id)

    lower, upper_only, display, hashes, stamps = [], [], 0, 0, 0
    for n in ast.walk(tree):
        if not isinstance(n, ast.Subscript):
            continue
        cap = cap_of(n.slice)
        if cap is None:
            continue
        kind = chain_kind(n.value)
        if kind == "HASH":
            hashes += 1
            continue
        is_name_read = isinstance(n.value, ast.Name) and n.value.id in read_names
        if kind not in ("READ", "STREAM") and not is_name_read:
            continue
        if in_display(n):
            display += 1
            continue
        # ⛔ v1's `consumed` RULE BETRAYED THE ESTIMAND ABOVE, and the round's own first run is
        #    the evidence: it returned 36 sites of which 34 are `git rev-parse HEAD`.stdout[:12]
        #    -- a 40-char sha truncated to 12 for an ARTIFACT STAMP. The estimand says "truncates
        #    ... and THEN SEARCHES OR COUNTS the result"; the code said `isinstance(p, ast.Call)
        #    -> True`, i.e. anything passed anywhere. A truncated IDENTITY is not a truncated
        #    POPULATION: shortening a sha loses collision resistance, never a member.
        #    Repaired to what the estimand actually asks: the value must REACH a search/count,
        #    directly or through the name it is assigned to.
        #    ⚠ AND THE FIRST REPAIR OVER-CORRECTED, which the KILL caught on the very next run:
        #      requiring the sliced value to reach a search THROUGH A NAME lost the known member.
        #      R601 writes `blob += f.read_text()[:200000]` and then searches `v["blob"]` -- the
        #      value escapes into a DICT and out of the function before it is searched, and no
        #      name-level rule follows it. Too loose -> 34 stamps; too tight -> 0 members. So the
        #      discrimination is moved to where it is INTRINSIC rather than dataflow-dependent:
        #        a truncated FILE READ can always lose members -- content has no bounded length;
        #        a truncated PROCESS LINE loses members only if it is then searched or counted.
        #      That separates R601:104 from 34 `rev-parse HEAD`[:12] stamps without chasing a
        #      value through a data structure, and `consumed` survives as a printed ATTRIBUTE.
        p = parents.get(n)
        consumed = False
        if isinstance(p, ast.Attribute) and p.attr in SEARCH_CALLS:
            consumed = True                      # (...)[:N].findall(...)
        elif isinstance(p, ast.Call) and isinstance(p.func, ast.Attribute) \
                and p.func.attr in SEARCH_CALLS:
            consumed = True                      # re.findall(pat, (...)[:N])
        elif isinstance(p, (ast.Assign, ast.AugAssign)):
            tgt = p.targets[0] if isinstance(p, ast.Assign) else p.target
            if isinstance(tgt, ast.Name) and tgt.id in searched_names:
                consumed = True                  # blob = f.read()[:N] ; PAT.search(blob)
        if kind == "STREAM" and not consumed:
            stamps += 1
            continue
        rec = {"file": str(path.relative_to(ROOT)), "line": n.lineno, "cap": cap,
               "kind": kind or "NAME-READ", "consumed": consumed,
               "src": ast.get_source_segment(src, n) or ""}
        (lower if kind in ("READ", "STREAM") else upper_only).append(rec)
    return lower, upper_only, display, hashes, stamps


def main() -> int:
    rounds = [d for d in sorted(A24.glob("R[0-9]*"))
              if (d / "run.py").is_file() and d.resolve() != HERE]
    if len(rounds) < 50:
        print(f"UNRUNNABLE: only {len(rounds)} rounds visible. Exit 2, never 0.")
        return 2

    L, U = [], []
    display_total = hash_total = parse_fail = stamp_total = 0
    for d in rounds:
        p = d / "run.py"
        try:
            src = p.read_text(errors="ignore")
            l, u, disp, h, st = analyse(src, p)
        except SyntaxError:
            parse_fail += 1
            continue
        L += l; U += u; display_total += disp; hash_total += h; stamp_total += st

    # ---- CONTROLS FIRST, COMPUTED BEFORE ANY VERDICT BRANCH -------------------------
    print("─── CONTROLS ───")
    # ⛔ v1's POSITIVE CONTROL PASSED ON THE WRONG SITE. It asked "is R601 in the list", took
    #    pos[0], and reported "FOUND at line 109, cap 110" -- which is R601's README HEADING, a
    #    display slice, not the known member at line 104. The control asked whether the
    #    instrument can SEE and never whether what it saw is what the claim is about. Repaired
    #    to pin the exact (file, line, cap) of the known member.
    pos = [s for s in L if "R601_" in s["file"] and s["line"] == 104 and s["cap"] == 200000]
    print(f"  POSITIVE   R601:104 `read_text(...)[:200000]` -> a regex search over `blob` -> "
          f"{'FOUND (cap 200000)' if pos else '⛔ NOT FOUND'} -> {'PASS' if pos else '⛔ FAIL'}")
    stampsrc = ('import subprocess, json\n'
                'src = subprocess.run(["git","rev-parse","HEAD"],capture_output=True,'
                'text=True).stdout.strip()[:12]\n'
                'json.dumps({"src": src})\n')
    sl, su, _, _, sst = analyse(stampsrc, pathlib.Path(ROOT / "stamp.py"))
    stampok = not (sl or su)
    print(f"  NEGATIVE-2 a git sha truncated to 12 for an artifact STAMP -> {len(sl)+len(su)} "
          f"site(s) -> {'PASS — an identity is not a population' if stampok else '⛔ FAIL'}")
    g0l, g0u, g0d, g0h, _ = analyse("x = 1\n", pathlib.Path(ROOT / "g0.py"))
    print(f"  g=0        an empty program -> {len(g0l)+len(g0u)} site(s) -> "
          f"{'PASS (can fail)' if not (g0l or g0u) else '⛔ FAIL'}")
    negsrc = ('import hashlib, pathlib\n'
              'h = hashlib.sha256(pathlib.Path("x").read_bytes()).hexdigest()[:16]\n'
              'print(open("y").read()[:40])\n')
    nl, nu, nd, nh, _ = analyse(negsrc, pathlib.Path(ROOT / "neg.py"))
    negok = not (nl or nu) and nh == 1 and nd == 1
    print(f"  NEGATIVE   a hash slice + a display slice -> classified {len(nl)+len(nu)} "
          f"(hash={nh}, display={nd}) -> {'PASS' if negok else '⛔ FAIL'}")
    plcsrc = 'x = open("f").zzq_no_such_reader()[:100]\nimport re; re.findall("a", x)\n'
    pl, pu, _, _, _ = analyse(plcsrc, pathlib.Path(ROOT / "plc.py"))
    print(f"  PLACEBO    a reader method no file calls -> {len(pl)+len(pu)} site(s) -> "
          f"{'PASS' if not (pl or pu) else '⛔ FAIL'}")
    controls_ok = bool(pos) and not (g0l or g0u) and negok and stampok and not (pl or pu)
    print(f"  KILL       classifier sees the known member -> "
          f"{'PASS — an absence claim is admissible' if controls_ok else '⛔ UNVERIFIED'}")

    # ---- THE TWO BOUNDS -------------------------------------------------------------
    lr = sorted({s["file"].split("/")[0] for s in L})
    ur = sorted({s["file"].split("/")[0] for s in U} - set(lr))
    print(f"\n─── SITES: TRUNCATION BETWEEN THE DATA AND A COUNT ───")
    print(f"  rounds scanned                          : {len(rounds)}  "
          f"(unparseable: {parse_fail})")
    print(f"  DISPLAY slices (inside print / f-string): {display_total}   ← correct, not a defect")
    print(f"  HASH slices (hexdigest[:N])             : {hash_total}   ← negative-control class")
    print(f"  STAMP slices (process line, never searched): {stamp_total} ← negative-control class")
    print(f"  LOWER BOUND  direct read/stream slices  : {len(L)} site(s) in {len(lr)} round(s)")
    print(f"  UPPER EXTRA  name-level, over-counts    : {len(U)} site(s) in {len(ur)} more round(s)")
    for s in L:
        print(f"    {s['file'][:62]:<62} :{s['line']:<4} cap={s['cap']:<7} {s['src'][:44]}")

    # ---- DOES THE CAP BIND? the site is not the blindness ---------------------------
    print(f"\n─── BINDING: the cap must be compared to WHAT THAT SITE READS ───")
    # ⛔ v1 SWEPT EVERY CAP AGAINST EVERY .py/.json/.md IN THE TREE and concluded "cap 12 BINDS,
    #    17,863 files exceed it". Cap 12 truncates a git sha; that site never opens a file. The
    #    control's two sides were different objects -- §4's dominant failure mode, in the binding
    #    test rather than in a control. A cap binds only against the population ITS OWN SITE
    #    reads, so the population is re-derived per site from that round's own glob, and any site
    #    whose population cannot be re-derived returns UNVERIFIED, never "inert".
    def population_of(site):
        if "R601_" in site["file"] and site["line"] == 104:
            fs = []
            for d in sorted((ROOT / "E05_the_space_of_compilers").glob("A*/R[0-9]*")):
                if not d.is_dir():
                    continue
                fs += list(d.glob("*.py"))
                if (d / "results").is_dir():
                    fs += list((d / "results").glob("*.json"))
            return "R601's own glob: every round's *.py + results/*.json", fs
        return None, None

    binding, undetermined = [], []
    for s in L:
        label, files = population_of(s)
        if files is None:
            undetermined.append(s)
            print(f"    {s['file'].split('/')[-2][:44]:<44} :{s['line']:<4} cap={s['cap']:<7} "
                  f"population NOT re-derivable -> UNVERIFIED")
            continue
        sizes = sorted((f.stat().st_size for f in files), reverse=True)
        over = [f for f in files if f.stat().st_size > s["cap"]]
        print(f"    {s['file'].split('/')[-2][:44]:<44} :{s['line']:<4} cap={s['cap']:<7}")
        print(f"      population = {label}")
        print(f"      files: {len(files)}   largest: {sizes[0]:,} bytes   "
              f"EXCEEDING the cap: {len(over)}")
        for f in over[:6]:
            print(f"        {f.stat().st_size:>9,}  {f.relative_to(ROOT)}")
        if over:
            binding.append((s["cap"], len(over)))

    # ---- CONSEQUENCE: binding is still not the same as WRONG -------------------------
    # ⭐ THE IMPOSSIBLE REGISTER SAID THIS NEEDED A DIFFERENT ROUND. It did not, and §4's
    #    `a wall never checked` is why it is done here instead: for R601 the question is not
    #    "re-run it without the cap" but the far cheaper "does the TAIL past the cap contain a
    #    match the HEAD does not?" -- one pass over 4 files. An unchecked wall is UNVERIFIED.
    print(f"\n─── CONSEQUENCE: does the binding cap CHANGE R601's own answer? ───")
    SECOND = __import__("re").compile(
        r"utterances\.jsonl|load_second|corpus[\"']?\s*[,=:]\s*[\"']?second|--corpus\s+second",
        __import__("re").I)                      # R601's own recogniser, copied verbatim
    CAP = 200000
    flips, examined = [], []
    for d in sorted((ROOT / "E05_the_space_of_compilers").glob("A*/R[0-9]*")):
        if not d.is_dir():
            continue
        fs = list(d.glob("*.py")) + (list((d / "results").glob("*.json"))
                                     if (d / "results").is_dir() else [])
        for f in fs:
            t = f.read_text(errors="ignore")
            if len(t) <= CAP:
                continue
            h, tl = bool(SECOND.search(t[:CAP])), bool(SECOND.search(t[CAP:]))
            examined.append((d.name, f.name, len(t), h, tl))
            if tl and not h:
                flips.append((d.name, f.name))
    plant = ("x" * CAP) + " utterances.jsonl "
    cons_ctrl = (not SECOND.search(plant[:CAP])) and bool(SECOND.search(plant[CAP:]))
    print(f"  POSITIVE  the token planted PAST the cap is seen in the tail and not the head -> "
          f"{'PASS' if cons_ctrl else '⛔ FAIL'}")
    for n, f, ln, h, tl in examined:
        print(f"    {ln:>9,}  {n[:42]:<42} {f:<28} head={h}  tail={tl}")
    print(f"  round(s) whose classification the cap CHANGED: {len(flips)} {flips}")
    consequence = ("NONE TODAY — the cap binds on 4 files and none of their tails carries a "
                   "second-corpus token the head lacks, so R601's published classification is "
                   "unaffected. It is inert by luck, not by design: one >200,000-char artifact "
                   "mentioning the second corpus would silently flip a round to home-only."
                   if not flips else
                   f"LIVE — {len(flips)} round(s) are misclassified by the cap: {flips}")
    print(f"  => {consequence}")

    # ---- VERDICT: a function of the controls ----------------------------------------
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no claim about the corpus is admissible"
    elif not L and not U:
        world = ("A SHELL-ONLY — no committed round truncates a read or a stream before counting "
                 "it. The repair is an operating rule and nothing on disk needs changing.")
    elif not binding:
        world = (f"B PRESENT BUT INERT — {len(L)} site(s) exist and no file in the tree exceeds "
                 f"any of their caps. Annotate; do not rewrite.")
    else:
        worst = max(binding, key=lambda t: t[1])
        world = (f"C LIVE — {len(L)} site(s) in {len(lr)} round(s) truncate a read that then "
                 f"feeds a search, and the cap BINDS on the site's OWN population: {worst[1]} "
                 f"file(s) it reads exceed cap {worst[0]}. That round is silently blind to those "
                 f"files' tails, so its counts are lower bounds of unknown size. "
                 f"{len(undetermined)} further site(s) UNVERIFIED — population not re-derivable."
                 f"  ⚠ BUT CONSEQUENCE: {consequence}")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 classifier x {len(rounds)} rounds x 4 controls + "
          f"{len({s['cap'] for s in L+U})} cap(s) swept. Non-survivors reported: "
          f"{display_total} display + {hash_total} hash + {stamp_total} stamp slices classified NOT defects.")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "truncation_sites.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "rounds_scanned": len(rounds), "parse_failures": parse_fail,
        "lower_bound_sites": L, "upper_extra_sites": U,
        "display_slices": display_total, "hash_slices": hash_total,
        "stamp_slices": stamp_total,
        "binding": [{"cap": c, "files_exceeding": n} for c, n in binding],
        "binding_undetermined": undetermined,
        "consequence": consequence, "consequence_control": cons_ctrl,
        "files_over_cap": [{"round": n, "file": f, "chars": ln, "head": h, "tail": t}
                           for n, f, ln, h, t in examined],
        "check250": ("R648's 'three rounds spent on truncations' verified: R630 [:12], R646 "
                     "head -3, R647 tail -25. Its RULE was too broad -- display truncation is "
                     "correct; the defect is truncation before a COUNT."),
        "impossible_RETRACTED": ("The docstring registered 'whether any round's published "
                       "NUMBER is wrong needs a different round' as IMPOSSIBLE. That was a wall I "
                       "never checked, and it was one pass over 4 files: comparing the HEAD and "
                       "TAIL of each over-cap file against R601's own recogniser answers it "
                       "directly, no re-run needed. §4's `a wall never checked` -- an unchecked "
                       "wall is UNVERIFIED, never SETTLED. What IS still impossible: the same "
                       "question for a site whose read population is not re-derivable."),
    }, indent=2))
    print(f"\n  wrote {out / 'truncation_sites.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
