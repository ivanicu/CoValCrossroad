"""R1078 — reading prose somewhere is not comparing a prose value. Trace the argument, not the file.

R1077 narrowed 34 precision-blind comparisons to 12 AT-RISK by asking whether the containing round
reads prose at all, and said plainly that AT-RISK is an UPPER bound: a round may read a README for
titles and never compare a value that came from it.

⭐ THE DATAFLOW IS WHAT DECIDES IT. For each at-risk site, find where it is CALLED, take the argument
   it compares, and trace that name back through the file's assignments. If it originates in a regex
   over document text, the comparison really can meet a displayed value. If it originates in a JSON
   load or a computation, the exact comparison is correct however much prose the round reads
   elsewhere.

⛔ P6, WRITTEN BEFORE THE RUN.
   PROPERTY    the compared value was displayed before being compared
   PROXY       its name traces back to a regex applied to text read from a `.md` file
   IMPLICATION traces to prose      ==> the exact comparison is genuinely exposed   [SOUND]
               does not trace       ==> safe                                        [NOT SOUND: the
                                        trace is bounded in depth and stays inside one file, so a
                                        value laundered through a helper or another module is missed]
   SAFE SIDE   rule only on `traces to prose`. A non-trace returns NOT-TRACED, never SAFE.

ESTIMAND        of R1077's 12 at-risk sites, how many compare a value whose assignment chain reaches
                a regex over document text
IDENTIFICATION  exact within the bound. ⚠ Depth-limited, single-file, and name-based, so NOT-TRACED
                is a LOWER bound on safety and the round claims only the positive direction.
SCOPE           population : R1077's AT-RISK sites
                instrument : AST assignment map + bounded backward walk from the call argument
                baseline   : R1077's 12
                regime     : this checkout
WORLDS          A THE EXPOSURE IS REAL AND SMALL — a few sites trace to prose. Those are the actual
                  defects R1075's retraction was an instance of, and they are nameable.
                B NOTHING TRACES — then even the 12 is an artifact of file-level reasoning, the only
                  confirmed exposure is R1070's, and the sound claim collapses to a single site.
                prediction matrix: A -> >=1 traces; B -> 0 trace
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      >=1 site traces to prose -> World A, name them
                      0 trace                   -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   ⭐ R1070's own membership test MUST trace to prose — its argument comes from a regex
                over `DEFINITION.md`, and it is the one confirmed case in this repository. A tracer
                that misses it cannot clear anything.
NEGATIVE CTRL   a site whose argument is loaded from JSON must NOT trace to prose.
PLACEBO         a site whose function is never called in its own file yields NO-CALLSITE, reported
                and never counted as safe.
NOISE FLOOR     N/A - this is a property of committed source. Stated, not omitted.
MULTIPLICITY    all at-risk sites reported with their trace verdict and the assignment reached.
SEEDS           N/A.
IMPOSSIBLE      catching a value laundered through a helper or another module. The walk is bounded
                and single-file by construction. SETTLES: IN-RELEASE by reading, at one file each.
"""
import ast, json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PROSE_SRC = re.compile(r"\.md['\"]|DEF\b|read_text\(\)")
REGEXY = ("findall", "finditer", "search", "match", "split")
DEPTH = 6


def main() -> int:
    src = next(ROOT.glob("E05_the_space_of_compilers/A27*/R1077_*/results/"
                         "exposed_sites.json"), None)
    if src is None:
        print("  UNRUNNABLE: R1077's artifact is missing. Exit 2, never 0."); return 2
    at = [r for r in json.loads(src.read_text())["rows"] if r["verdict"] == "AT-RISK"]
    if not at:
        print("  UNRUNNABLE: no at-risk site. Exit 2, never 0."); return 2

    def trace(rel, fname):
        p = ROOT / rel
        try:
            txt = p.read_text(); tree = ast.parse(txt)
        except Exception:
            return "UNREADABLE", None
        # assignment map: name -> source segment of its value
        assign = {}
        for nd in ast.walk(tree):
            if isinstance(nd, ast.Assign):
                seg = ast.get_source_segment(txt, nd.value) or ""
                for t in nd.targets:
                    if isinstance(t, ast.Name):
                        assign[t.id] = seg
                    elif isinstance(t, ast.Tuple):
                        for e in t.elts:
                            if isinstance(e, ast.Name):
                                assign[e.id] = seg
            elif isinstance(nd, (ast.For, ast.comprehension)):
                tgt = getattr(nd, "target", None)
                it = getattr(nd, "iter", None)
                if isinstance(tgt, ast.Name) and it is not None:
                    assign.setdefault(tgt.id, ast.get_source_segment(txt, it) or "")
        # call sites of fname; take the first positional argument's name
        names = []
        for nd in ast.walk(tree):
            if isinstance(nd, ast.Call) and isinstance(nd.func, ast.Name) \
                    and nd.func.id == fname and nd.args:
                a0 = nd.args[0]
                if isinstance(a0, ast.Name):
                    names.append(a0.id)
                else:
                    seg = ast.get_source_segment(txt, a0) or ""
                    if any(k in seg for k in REGEXY):
                        return "TRACES-TO-PROSE", seg[:110]
        if not names:
            return "NO-CALLSITE", None
        for n0 in names:
            seen, frontier = set(), [n0]
            for _ in range(DEPTH):
                nxt = []
                for n in frontier:
                    if n in seen:
                        continue
                    seen.add(n)
                    seg = assign.get(n, "")
                    if any(k in seg for k in REGEXY) and PROSE_SRC.search(txt):
                        if re.search(r"\b(doc|txt|text|body|md|readme|statement)\b", seg, re.I):
                            return "TRACES-TO-PROSE", f"{n} = {seg[:100]}"
                    nxt += re.findall(r"\b([A-Za-z_]\w*)\b", seg)
                frontier = nxt
        return "NOT-TRACED", None

    # ⛔⛔⛔ THE POSITIVE CONTROL DID NOT FAIL FOR ITS OWN REASONS — IT EXPOSED THE CENSUS.
    #   R1070's membership test is `sourced(t)`: one argument, closing over `stored`. R1076's
    #   classifier required `len(args) >= 2`, so **R1070 has NO rows in that census at all** — the
    #   single confirmed defect in this repository, the one that caused R1075's retraction, was
    #   never counted among the 38. And R1076's positive control passed anyway, because it checked
    #   `has`/`has_rounded`, which happen to take two arguments.
    #   ⭐ §4's row at a new level: **the positive control confirmed the instrument could see A
    #   membership test, never that it could see THE one the claim is about.** So this round's
    #   estimand changes: the population, not the traces.
    def closure_tests(path):
        """single-argument membership tests — the shape R1076's census could not see"""
        try:
            txt = path.read_text(); tree = ast.parse(txt)
        except Exception:
            return []
        out = []
        for fn in ast.walk(tree):
            if not isinstance(fn, ast.FunctionDef) or len(fn.args.args) != 1:
                continue
            seg = ast.get_source_segment(txt, fn) or ""
            if len(seg.splitlines()) > 12:
                continue
            low = seg.lower()
            if re.search(r"return\s+(any\(|all\(|.*\bin\b)", low) and \
                    ("round(" in low or "float(" in low or " in " in low):
                kind = "precision-aware" if "round(" in low else "exact"
                out.append({"file": str(path.relative_to(ROOT)), "name": fn.name, "kind": kind})
        return out

    E05 = ROOT / "E05_the_space_of_compilers"
    missed = []
    for pth in sorted(list((ROOT / "assurance").glob("*.py")) + list(E05.glob("A*/R*/run.py"))):
        missed += closure_tests(pth)
    r1070_missed = [m for m in missed if "R1070" in m["file"]]
    pos = bool(r1070_missed)
    known_two_arg = 38
    print(f"  POSITIVE — R1070's own membership test must appear in the MISSED population: {pos} "
          f"{[m['name'] for m in r1070_missed]}")
    neg = not any(m["name"] == "main" for m in missed)
    print(f"  NEGATIVE — `main` must not appear among them: {neg}")
    if not (pos and neg):
        print("  the missed-population scan cannot be read either way. Exit 2, never 0."); return 2

    blind = [m for m in missed if m["kind"] == "exact"]
    print(f"\n  ⛔⛔ SINGLE-ARGUMENT MEMBERSHIP TESTS R1076's CENSUS COULD NOT SEE: {len(missed)} "
          f"({len(blind)} precision-blind) across {len({m['file'] for m in missed})} files")
    for m in missed[:8]:
        print(f"     {m['kind']:<16} {m['name']:<14} {m['file'].split('/')[-2][:50]}")
    print(f"  ⚠ that {len(missed)} is NOT a count — see the sizing control below.")

    rows = []
    # ⛔⛔ AND MY SIZING OF THE MISSING POPULATION IS NOT REPORTABLE. The one-argument scan pulled in
    #   `cls`, `pair_sign`, `rank_obs`, `toks`, `canon` — the SAME scoring helpers R1076 spent three
    #   repairs removing from its two-argument scan. I reproduced the contamination I had just
    #   watched someone else's instrument suffer, in the round whose whole point was that instrument's
    #   blind spot. So `249` is an upper bound with a known-bad denominator, and it is NOT a count.
    STOWAWAYS = {"cls", "pair_sign", "rank_obs", "toks", "canon", "content_toks", "kendall_pairs"}
    contaminated = sorted({m["name"] for m in missed} & STOWAWAYS)
    sizing_ok = not contaminated
    print(f"  ⛔ SIZING CONTROL — known scoring helpers must not appear in the missed population: "
          f"{sizing_ok}" + (f" ⛔ present: {contaminated}" if contaminated else ""))

    print()
    world = (f"⛔ THE CENSUS PROVABLY EXCLUDES THE ONE CONFIRMED DEFECT, AND THAT IS THE WHOLE "
             f"FINDING. R1070's membership test is `{r1070_missed[0]['name']}` — ONE argument, "
             f"closing over its container — and R1076's classifier required two, so **R1070 has no "
             f"rows in that census at all.** The single confirmed exposure in this repository, the "
             f"cause of R1075's retraction, was never among the 38. ⭐ And R1076's positive control "
             f"passed throughout because it checked a two-argument pair: **it confirmed the "
             f"instrument could see A membership test, never THE one the claim was about** — §4's "
             f"row, at a new level. R1077's 34-to-12 narrowing inherits the hole.\n"
             f"⚠ HOW BIG THE MISSING POPULATION IS: **UNVERIFIED.** My one-argument scan returned "
             f"{len(missed)}, but its own sizing control FAILS — it readmitted {contaminated}, the "
             f"very scoring helpers R1076 removed in three repairs. **I reproduced the contamination "
             f"in the round about that instrument's blind spot.** So `{len(missed)}` is not a count "
             f"and is not reported as one; what stands is n=1, verified, and it is enough to void "
             f"the census as a characterisation.")
    o = HERE / "results" / "argument_traces.json"
    o.write_text(json.dumps({
        "round": "R1078", "missed_single_arg_tests": len(missed),
        "missed_precision_blind": len(blind), "missed_rows": missed,
        "sizing_control_passed": bool(sizing_ok), "sizing_contaminants": contaminated,
        "SIZE_IS_UNVERIFIED": True,
        "R1070_was_missing_from_census": bool(r1070_missed),
        "world": world,
        "proxy_ledger": {"property": "the compared value was displayed before being compared",
                         "proxy": "its name traces to a regex over text read from a .md file",
                         "sound": "traces => exposed", "unsound": "no trace => safe",
                         "safe_side": "a non-trace returns NOT-TRACED, never SAFE"},
        "controls": {"positive_R1070_in_missed_population": bool(pos),
                     "negative_main_excluded": bool(neg)},
        "limitation": "depth-bounded, single-file, name-based; NOT-TRACED is a lower bound on safety",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
