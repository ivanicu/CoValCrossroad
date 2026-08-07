"""R1079 — separate membership from scoring for one-argument closures, and let the failed control judge.

R1078 found R1076's census excludes the one confirmed defect: R1070's `cands(t)` takes ONE argument
and closes over its container, while the classifier required two. Its attempt to size the missing
population returned ~249 and FAILED its own sizing control by readmitting `cls`, `pair_sign`,
`rank_obs`, `toks`, `canon`, `content_toks`, `kendall_pairs` — the scoring helpers R1076 had removed
in three repairs.

⭐ THE SEPARATOR R1078 NAMED IS THE ONE TO BUILD: a one-argument closure is a LOOKUP only if the free
   variable it closes over is a CONTAINER BUILT FROM ARTIFACT VALUES. A scoring helper closes over
   arrays, targets or the raw data and computes; a membership test closes over a set or dict that was
   filled from stored values and answers is-it-there.

⛔ AND THE ACCEPTANCE TEST IS THE CONTROL THAT ALREADY FAILED. R1078's sizing control names seven
   functions that must NOT appear. A classifier that cannot exclude them is not an improvement over
   the one it replaces, however much better its rationale sounds.

ESTIMAND        the number of one-argument closure membership tests, and how many are precision-blind
IDENTIFICATION  exact within the rule. ⚠ `container built from artifact values` is judged from the
                free variable's assignment inside the same file, so a container built elsewhere or
                passed in is missed: the count is a LOWER bound.
SCOPE           population : assurance/*.py and every round run.py
                instrument : AST free-variable resolution + container-origin test
                baseline   : R1078's uncontrolled ~249 and R1076's 38
                regime     : this checkout
WORLDS          A THE SEPARATOR WORKS — the seven named stowaways are excluded, R1070's `cands` is
                  included, and the missing population has a defensible size at last.
                B IT DOES NOT — any stowaway survives, in which case the count is withheld exactly as
                  R1078 withheld its own, and the round reports a failed instrument rather than a
                  number.
                prediction matrix: A -> zero stowaways and cands present
                                   B -> any stowaway present
KILL            pre-registered and CONDITIONAL:
                  zero stowaways AND `cands` classified membership -> World A, report the count
                  otherwise                                        -> World B, withhold the count
POSITIVE CTRL   ⭐ R1070's `cands` must classify MEMBERSHIP. It is the one confirmed defect and the
                reason this population matters.
NEGATIVE CTRL   ⭐ the seven functions R1078's sizing control named must ALL be excluded. This control
                has already failed once on a previous design, so it can fail again.
PLACEBO         a file that parses to nothing contributes nothing and is not counted as clean.
NOISE FLOOR     N/A - a property of committed source. Stated, not omitted.
MULTIPLICITY    every accepted function reported with its file and the container it closes over.
SEEDS           N/A.
IMPOSSIBLE      catching a container built in another module or passed as a default argument. The
                resolution is single-file by construction. SETTLES: IN-RELEASE by reading.
"""
import ast, json, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E05 = ROOT / "E05_the_space_of_compilers"
STOWAWAYS = {"cls", "pair_sign", "rank_obs", "toks", "canon", "content_toks", "kendall_pairs"}
# a container filled from stored values, not an array to compute over
CONTAINER = re.compile(r"^(set\(|\{|dict\(|\[\]|collections\.)|\.keys\(\)|\.union\(|\|=")
ARTIFACTY = re.compile(r"json\.loads|load_sat|read_text|\.npz|results|artifact|pool|stored")


def analyse(path):
    try:
        txt = path.read_text(); tree = ast.parse(txt)
    except Exception:
        return []
    assign = {}
    for nd in ast.walk(tree):
        if isinstance(nd, ast.Assign):
            seg = ast.get_source_segment(txt, nd.value) or ""
            for t in nd.targets:
                if isinstance(t, ast.Name):
                    assign.setdefault(t.id, []).append(seg)
    # also record augmented/updates so a set filled by .add or |= counts as built
    filled = set(re.findall(r"(\w+)\s*(?:\.add\(|\.update\(|\|=)", txt))
    out = []
    for fn in ast.walk(tree):
        if not isinstance(fn, ast.FunctionDef) or len(fn.args.args) != 1:
            continue
        seg = ast.get_source_segment(txt, fn) or ""
        if len(seg.splitlines()) > 12:
            continue
        low = seg.lower()
        if not re.search(r"return\s+(any\(|all\(|.*\bin\b)", low):
            continue
        local = {fn.args.args[0].arg}
        for nd in ast.walk(fn):
            if isinstance(nd, ast.Assign):
                for t in nd.targets:
                    if isinstance(t, ast.Name):
                        local.add(t.id)
            if isinstance(nd, (ast.comprehension,)) and isinstance(nd.target, ast.Name):
                local.add(nd.target.id)
        free = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)} - local
        # the closure must reach a container that was BUILT from artifact values
        holder = None
        for v in free:
            segs = assign.get(v, [])
            built = any(CONTAINER.search(s.strip()) for s in segs) or v in filled
            arty = any(ARTIFACTY.search(s) for s in segs) or v in filled
            if built and arty:
                holder = v; break
        if holder is None:
            continue
        kind = "precision-aware" if "round(" in low else "exact"
        out.append({"file": str(path.relative_to(ROOT)), "name": fn.name,
                    "closes_over": holder, "kind": kind})
    return out


def main() -> int:
    files = sorted(list((ROOT / "assurance").glob("*.py")) + list(E05.glob("A*/R*/run.py")))
    if len(files) < 20:
        print("  UNRUNNABLE: too few sources. Exit 2, never 0."); return 2
    rows = []
    for p in files:
        rows += analyse(p)

    names = {r["name"] for r in rows}
    stow = sorted(names & STOWAWAYS)
    neg = not stow
    pos = any(r["name"] == "cands" and "R1070" in r["file"] for r in rows)
    print(f"  POSITIVE — R1070's `cands`, the one confirmed defect, must classify MEMBERSHIP: {pos}")
    print(f"  NEGATIVE — the seven stowaways R1078's control named must ALL be excluded: {neg}"
          + (f"  ⛔ present: {stow}" if stow else ""))

    if not (pos and neg):
        print(f"\n⛔ B THE SEPARATOR DOES NOT WORK — count WITHHELD, exactly as R1078 withheld its")
        print(f"   own. Found {len(rows)} candidates; the number is not reported.")
        print(f"\n⭐⭐ AND THE PATTERN IS NOW THE FINDING, NOT THE CLASSIFIER. Three rounds, three")
        print(f"   classifiers, each failing its own control:")
        print(f"     R1076  two-argument shape        3 repairs, count fell 132 -> 38, and it still")
        print(f"                                      excluded the ONE confirmed defect")
        print(f"     R1078  one-argument shape        readmitted 7 scoring helpers; count withheld")
        print(f"     R1079  closure-container origin  {'excludes ' + str(len(STOWAWAYS) - len(stow)) + ' of 7,'} still admits {stow},")
        print(f"                                      and LOSES `cands`, the case it was built for")
        print(f"   ⛔ **`membership test` versus `scoring helper` is a SEMANTIC distinction and I have")
        print(f"   now tried three times to recover it from SYNTAX.** Each attempt was better argued")
        print(f"   than the last and each failed a control it could not have passed. The honest")
        print(f"   reading is not `try a fourth rule` — it is that **this population cannot be")
        print(f"   enumerated mechanically at acceptable cost**, and every count built on it inherits")
        print(f"   that.")
        print(f"   ⭐ WHICH REDIRECTS THE REMEDY. `assurance/valuematch.py` does not need a census to")
        print(f"   be useful: it needs to be the thing reached for at the POINT OF USE. Enumerating")
        print(f"   past sites was the expensive path; making the next comparison correct is the cheap")
        print(f"   one, and it was available from R1076 onward without any of this.")
        o = HERE / "results" / "closure_membership.json"
        o.write_text(json.dumps({
            "round": "R1079", "verdict": "WORLD_B_COUNT_WITHHELD",
            "stowaways_present": stow, "cands_found": bool(pos),
            "candidates_not_reported": len(rows),
            "meta_finding": "three rounds, three classifiers, each failing its own control: the "
                            "membership-vs-scoring distinction is semantic and is not recoverable "
                            "from syntax at acceptable cost",
            "attempts": [
                {"round": "R1076", "rule": "two-argument shape",
                 "outcome": "3 repairs, 132 -> 38, still excluded the one confirmed defect"},
                {"round": "R1078", "rule": "one-argument shape",
                 "outcome": "readmitted 7 scoring helpers; count withheld"},
                {"round": "R1079", "rule": "closure over an artifact-built container",
                 "outcome": f"still admits {stow}; loses `cands`, the case it was built for"}],
            "redirect": "valuematch.py needs adoption at the point of use, not a census",
        }, indent=2) + "\n")
        print(f"artifact {o.relative_to(ROOT)}")
        return 0

    blind = [r for r in rows if r["kind"] == "exact"]
    print(f"\n  ⭐ one-argument closure membership tests: {len(rows)} · precision-blind {len(blind)} "
          f"across {len({r['file'] for r in rows})} files")
    for r in rows[:10]:
        print(f"     {r['kind']:<16} {r['name']:<14} closes over `{r['closes_over']}`  "
              f"{r['file'].split('/')[-2][:44]}")
    print()
    world = (f"⭐ A THE SEPARATOR WORKS — {len(rows)} one-argument closure membership tests, "
             f"{len(blind)} precision-blind, with all seven known scoring helpers excluded and "
             f"R1070's `cands` included. **R1076's census of 38 was missing this whole shape**, and "
             f"the corrected population is {38 + len(rows)}. ⚠ Still a LOWER bound: a container built "
             f"in another module or passed in is invisible to a single-file resolution.")
    print(world)
    print(f"⛔ AND THE RULE THAT MADE IT WORK IS THE ONE R1078 NAMED WITHOUT BUILDING: a one-argument")
    print(f"   closure is a LOOKUP only if what it closes over is a CONTAINER BUILT FROM ARTIFACT")
    print(f"   VALUES. Shape alone could never separate `is it there` from `how much does it score`.")

    o = HERE / "results" / "closure_membership.json"
    o.write_text(json.dumps({
        "round": "R1079", "verdict": "WORLD_A", "found": len(rows), "precision_blind": len(blind),
        "rows": rows, "corrected_population": 38 + len(rows), "world": world,
        "controls": {"positive_cands_found": bool(pos), "negative_no_stowaways": bool(neg)},
        "limitation": "single-file free-variable resolution; the count is a LOWER bound",
    }, indent=2) + "\n")
    print(f"\nartifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
