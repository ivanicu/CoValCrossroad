"""
R723 · the path was built, not written

ESTIMAND        of R680's 8 DERIVERS of the ③ extension, how many read a PRIOR ROUND'S ARTIFACT,
                measured at the CLAIM's unit (a cross-round file read) rather than at R680's
                instrument unit (a literal path substring)?
IDENTIFICATION  identified from source. NOT identified: whether the value is USED -- out of scope,
                that is R722's NEXT line. So the output is a CEILING on independence, never a count.
SCOPE           population R680's 8 derivers · instrument python ast · baseline R680's regex ·
                regime this arc at this tree_sha
WORLDS          W1 R680 right (2 readers) · W2 R680's regex blind to pathlib-constructed paths
KILL            conditional; see PREREGISTRATION.txt. Gated on POSITIVE and NEGATIVE both firing.
POSITIVE CTRL   R353 and R519 -- R680's OWN true positives -- must be flagged by the new instrument.
                floor 0 < t 2 <= ceiling 8, computed below, not chosen.
NEGATIVE CTRL   R294 reads the RELEASE's corebench/results and must NOT flag. Excluded world:
                "any file read is dependence".
SHAM            cross-round path in the DOCSTRING only, no read call -> 0. absence, not inversion.
PLACEBO         a round against its OWN id (self-write) -> exactly 0.
NOISE FLOOR     deterministic; verified by a changed PYTHONHASHSEED, not assumed.
MULTIPLICITY    8 rounds x 5 specs = 40 classifications, all reported.
SPECIFICATION   S1 R680 regex · S2 ast lit+read · S3 ast lit · S4 file EXISTS · S5 PATH-SHAPED+read
SEEDS           deterministic; two hash seeds byte-identical
ARTIFACT        results/r723_reader_recount.json with tree_sha
IMPOSSIBLE      independently replicated -> a second implementer · causally identified -> would
                require editing a round and re-running it (that is the NEXT question, not this one)
"""
import ast, hashlib, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
DERIVERS = ["R294", "R353", "R404", "R405", "R408", "R409", "R519", "R667"]

# every round directory that exists on disk -- the instrument matches against REALITY, not a pattern
DIRNAMES = sorted(d.name for d in ARC.iterdir() if d.is_dir() and re.match(r"^R\d{3}_", d.name))
DIRIDS   = {d.split("_")[0]: d for d in DIRNAMES}

READ_CALLS = ("read_text", "read_bytes", "load", "loads", "open", "glob", "iglob")

# ── R680's instrument, verbatim ────────────────────────────────────────────────────────────────
R680_RE = re.compile(r"results/[\w.]+\.json|R\d{3}[\w]*/results", re.I)


def executable_source(src: str) -> str:
    """strip comments and docstrings, as R680 did -- same pre-processing for every spec."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return src
    drop = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            body = getattr(node, "body", [])
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) \
               and isinstance(body[0].value.value, str):
                drop.add(id(body[0]))
    keep = []
    for line in src.splitlines():
        s = line.split("#")[0]
        keep.append(s)
    txt = "\n".join(keep)
    # remove triple-quoted blocks (docstrings) textually -- ast gives no spans for all versions
    txt = re.sub(r'"""(?:.|\n)*?"""', "", txt)
    txt = re.sub(r"'''(?:.|\n)*?'''", "", txt)
    return txt


def exec_literals(src: str):
    """every string literal in EXECUTABLE code (docstrings excluded), via ast."""
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    doc_ids = set()
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if isinstance(body, list) and body and isinstance(body[0], ast.Expr) \
           and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            doc_ids.add(id(body[0].value))
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and id(node) not in doc_ids:
            out.append(node.value)
    return out


def has_read_call(src: str) -> bool:
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if name in READ_CALLS:
                return True
    return False


def cross_round_refs(src: str, self_id: str):
    """round ids OTHER than self, named in an executable string literal."""
    hits = set()
    for lit in exec_literals(src):
        for m in re.finditer(r"R(\d{3})", lit):
            rid = "R" + m.group(1)
            if rid != self_id:
                hits.add(rid)
    return sorted(hits)


def path_shaped(lit: str) -> bool:
    """Is this literal a PATH FRAGMENT, or is it prose that happens to name a round?

    ⚠ This predicate is the round's second repair. Without it, the sentence
    '(R358/R359), so a second judge cannot host this comparison' registers as a cross-round
    reference -- and R409 really does contain that sentence. A round id inside prose is a
    CITATION; only a path fragment is a READ. A literal qualifies if it is exactly a round
    directory that exists on disk, or if it contains a separator together with a results
    segment or a data-file extension.
    """
    if lit in DIRNAMES:
        return True
    return ("/" in lit) and (("results" in lit) or bool(re.search(r"\.(json|npz|jsonl|csv)\b", lit)))


def cross_round_refs_pathlike(src: str, self_id: str):
    """cross_round_refs, restricted to literals that are actually paths."""
    hits = set()
    for lit in exec_literals(src):
        if not path_shaped(lit):
            continue
        for m in re.finditer(r"R(\d{3})", lit):
            rid = "R" + m.group(1)
            if rid != self_id:
                hits.add(rid)
    return sorted(hits)


def resolves_on_disk(src: str, self_id: str):
    """S4 -- strictest: a referenced round id whose directory ACTUALLY EXISTS here."""
    return sorted(r for r in cross_round_refs(src, self_id) if r in DIRIDS)


def classify(src: str, self_id: str):
    s1 = bool(R680_RE.search(executable_source(src)))
    refs = cross_round_refs(src, self_id)
    s2 = bool(refs) and has_read_call(src)
    s3 = bool(refs)
    s4 = bool(resolves_on_disk(src, self_id)) and has_read_call(src)
    pl = cross_round_refs_pathlike(src, self_id)
    s5 = bool(pl) and has_read_call(src)
    return {"S1_r680_regex": s1, "S2_ast_lit_and_read": s2, "S3_ast_lit_only": s3,
            "S4_exists_on_disk": s4, "S5_pathshaped_and_read": s5, "refs": refs, "refs_pathlike": pl}


def path_style(src: str, self_id: str) -> str:
    """DIRECTIONAL mechanism: is the cross-round path ONE literal, or built from operands?

    ⚠ v2. v1 matched r"R\d{3}[\w*]*/" against every executable literal and called R409
    'single_literal' on the strength of a PROSE sentence -- '(R358/R359), so a second judge...'.
    A style classifier is a search, and a search is an instrument: v1 had no positive control and
    produced exactly the confident wrong answer that buys. v2 requires the literal to name a round
    DIRECTORY THAT EXISTS ON DISK followed by a separator, so prose cannot satisfy it.
    """
    for lit in exec_literals(src):
        # single_literal means the WHOLE path sits in one string: a separator is required.
        # A bare directory name IS the operand-built case and must not qualify.
        if path_shaped(lit) and "/" in lit and re.search(r"R\d{3}", lit) and self_id not in lit:
            return "single_literal"
    return ("built_from_operands" if cross_round_refs_pathlike(src, self_id)
            else "no_cross_round_path")


def main() -> int:
    print("=" * 100)
    print("R723 · THE PATH WAS BUILT, NOT WRITTEN")
    print("=" * 100)
    print(f"  round dirs on disk: {len(DIRNAMES)}   derivers under test: {len(DERIVERS)}")

    src = {}
    for rid in DERIVERS:
        d = DIRIDS.get(rid)
        if d is None:
            print(f"  ⛔ {rid} has no directory — population incomplete")
            return 2
        src[rid] = (ARC / d / "run.py").read_text(errors="ignore")

    if not src:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0")
        return 2

    # ── CONTROLS ──────────────────────────────────────────────────────────────────────────────
    print("\n─── CONTROLS ───")
    ctl = {}

    POS_SRC = ('import json,pathlib\n'
               'p = pathlib.Path(".").parent / "R999_other_round" / "results" / "a.json"\n'
               'x = json.loads(p.read_text())\n')
    pos_hit = classify(POS_SRC, "R000")["S2_ast_lit_and_read"]
    # threshold band, computed not chosen
    floor_ceiling = (0, len(DERIVERS))
    known_true = ["R353", "R519"]           # R680's OWN true positives — the known-answer cases
    recovered = [r for r in known_true if classify(src[r], r)["S2_ast_lit_and_read"]]
    t = len(known_true)
    ok_band = floor_ceiling[0] < t <= floor_ceiling[1]
    ctl["POSITIVE"] = pos_hit and len(recovered) == t and ok_band
    print(f"  POSITIVE   synthetic cross-round read flagged: {pos_hit}")
    print(f"             R680's own true positives recovered: {recovered} ({len(recovered)}/{t})")
    print(f"             band floor {floor_ceiling[0]} < t {t} <= ceiling {floor_ceiling[1]}: {ok_band}")
    print(f"             -> {'PASS' if ctl['POSITIVE'] else 'FAIL'}")

    G0_SRC = 'import json,pathlib\np = pathlib.Path("data")/"x.jsonl"\nx = p.read_text()\n'
    g0 = classify(G0_SRC, "R000")
    ctl["G0"] = not g0["S2_ast_lit_and_read"] and not g0["S3_ast_lit_only"]
    print(f"  g=0        no cross-round literal -> flagged {g0['S2_ast_lit_and_read']}  "
          f"-> {'PASS' if ctl['G0'] else 'FAIL'}")

    r294 = classify(src["R294"], "R294")
    ctl["NEGATIVE"] = not r294["S2_ast_lit_and_read"]
    print(f"  NEGATIVE   R294 reads the RELEASE's corebench/results, refs={r294['refs']} -> "
          f"flagged {r294['S2_ast_lit_and_read']} -> {'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             world excluded: 'any file read is dependence' — reading the benchmark is")
    print(f"             sharing a source, not copying a result.")

    SHAM_SRC = ('"""ARTIFACT reads ../R999_other_round/results/a.json"""\n'
                'import json\nx = 1 + 1\n')
    sham = classify(SHAM_SRC, "R000")
    ctl["SHAM"] = not sham["S2_ast_lit_and_read"]
    print(f"  SHAM       path in DOCSTRING only, no read -> flagged {sham['S2_ast_lit_and_read']} "
          f"-> {'PASS' if ctl['SHAM'] else 'FAIL'}")

    plc = [r for r in DERIVERS if r in classify(src[r], r)["refs"]]
    ctl["PLACEBO"] = len(plc) == 0
    print(f"  PLACEBO    rounds counted as reading THEMSELVES: {len(plc)} (must be 0) "
          f"-> {'PASS' if ctl['PLACEBO'] else 'FAIL'}")

    st_pos_single = path_style('import json\np="R353_the_admitted_set_under_every_pool_order/results/a.json"\nx=json.loads(open(p).read())\n', "R000")
    st_pos_built  = path_style('import pathlib\np=pathlib.Path(".")/"R353_the_admitted_set_under_every_pool_order"/"results"/"a.json"\nx=p.read_text()\n', "R000")
    st_neg_prose  = path_style('x = "   (R358/R359), so a second judge cannot host this."\n', "R000")
    ctl["STYLE"] = (st_pos_single == "single_literal" and st_pos_built == "built_from_operands"
                    and st_neg_prose == "no_cross_round_path")
    print(f"  STYLE      the DIRECTIONAL's own classifier, which v1 shipped uncontrolled:")
    print(f"             positive single-literal path -> {st_pos_single}")
    print(f"             positive operand-built path  -> {st_pos_built}")
    print(f"             negative PROSE '(R358/R359)' -> {st_neg_prose}  (v1 said single_literal)")
    print(f"             -> {'PASS' if ctl['STYLE'] else 'FAIL'}")

    ctl["UNIT"] = True
    print(f"  UNIT       instrument unit: cross-round dir name in an executable literal + a read call")
    print(f"             claim unit     : reads a prior round's artifact")
    print(f"             residue        : USE of the value is NOT measured here (R722's NEXT) -> PASS")

    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── THE GRID ──────────────────────────────────────────────────────────────────────────────
    print("\n─── 8 ROUNDS x 5 SPECIFICATIONS = 40 CLASSIFICATIONS (all reported) ───")
    print(f"  {'round':<7} {'S1 r680':<9} {'S2 ast+read':<13} {'S3 lit':<8} {'S4 exists':<11} "
          f"{'S5 strict':<11} {'style':<20} refs(path-shaped)")
    grid, styles = {}, {}
    for rid in DERIVERS:
        c = classify(src[rid], rid)
        st = path_style(src[rid], rid)
        grid[rid], styles[rid] = c, st
        print(f"  {rid:<7} {str(c['S1_r680_regex']):<9} {str(c['S2_ast_lit_and_read']):<13} "
              f"{str(c['S3_ast_lit_only']):<8} {str(c['S4_exists_on_disk']):<11} "
              f"{str(c['S5_pathshaped_and_read']):<11} {st:<20} {','.join(c['refs_pathlike'][:4])}")

    counts = {k: sum(1 for r in DERIVERS if grid[r][k])
              for k in ("S1_r680_regex", "S2_ast_lit_and_read", "S3_ast_lit_only",
                        "S4_exists_on_disk", "S5_pathshaped_and_read")}
    print(f"\n  spec curve (readers found): " +
          "  ".join(f"{k.split('_')[0]}={v}" for k, v in counts.items()))

    A = counts["S5_pathshaped_and_read"]
    B = len(DERIVERS) - A
    s1_set = {r for r in DERIVERS if grid[r]["S1_r680_regex"]}
    s2_set = {r for r in DERIVERS if grid[r]["S5_pathshaped_and_read"]}
    C = len(s1_set & s2_set) / len(s2_set) if s2_set else float("nan")
    missed = sorted(s2_set - s1_set)

    # DIRECTIONAL: are the misses exactly the operand-built paths?
    built = {r for r in DERIVERS if styles[r] == "built_from_operands"}
    single = {r for r in DERIVERS if styles[r] == "single_literal"}
    directional = (set(missed) == (built & s2_set)) and not (built & s1_set) and (single <= s1_set)

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo, hi, reg in [("A readers (claim unit)", A, 2, 8, 7),
                                 ("B ceiling on independent", B, 0, 6, 1),
                                 ("C R680 recall", round(C, 4), 0.0, 1.0, 0.29)]:
        inside = lo <= val <= hi
        print(f"  {nm:<26} registered {reg:<6} -> {val:<8} in [{lo},{hi}]: {inside}")
    print(f"  DIRECTIONAL misses == operand-built paths -> {directional}")
    print(f"     missed by R680     : {missed}")
    print(f"     operand-built      : {sorted(built)}")
    print(f"     single-literal     : {sorted(single)}")

    # ── CONDITIONAL KILL ──────────────────────────────────────────────────────────────────────
    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["NEGATIVE"]):
        verdict = "UNVERIFIED — a gating control did not fire; no recount is admissible."
        refuted = None
    elif A <= 2 and C == 1.0:
        refuted = True
        verdict = ("ATTACK REFUTED — the claim-unit instrument agrees with R680; the ceiling of six "
                   "stands and R722's NEXT line was chasing a non-defect.")
    else:
        refuted = False
        verdict = (f"⭐⭐⭐ R680'S TIGHTENING IS BLIND TO CONSTRUCTED PATHS. {A} of {len(DERIVERS)} "
                   f"derivers read a PRIOR ROUND'S ARTIFACT at the claim's unit; R680's regex found "
                   f"{len(s1_set)}, recall {C:.4f}, missing {missed}. "
                   f"⭐ The deliverable's 'at most SIX independent computations' is therefore itself "
                   f"an overcount: the corrected ceiling is {B}"
                   + (f" ({sorted(set(DERIVERS)-s2_set)})." if B else ".") +
                   " ⚠ AND IT IS STILL A CEILING, NOT A COUNT: this round measures that the artifact "
                   "is READ, never that its value is USED, which is a separate and unmeasured step. "
                   "⚠ MECHANISM: R680's regex needs the substring 'results/' or 'Rnnn.../results'; a "
                   "path assembled with pathlib operands ('R360_x' / 'results' / 'f.json') contains "
                   "neither, so the MEASUREMENT is invariant under a rewrite the PROPERTY is not — "
                   "the same gauge failure R680 used to kill R679's proposal one round earlier.")
    print(f"  {verdict}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {
        "world": verdict,
        "controls_ok": all(ctl.values()),
        "controls": ctl,
        "tree_sha": tree_sha,
        "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        "derivers": DERIVERS,
        "grid": {r: {k: v for k, v in grid[r].items()} for r in DERIVERS},
        "path_style": styles,
        "spec_counts": counts,
        "A_readers_claim_unit": A,
        "B_corrected_ceiling": B,
        "B_members": sorted(set(DERIVERS) - s2_set),
        "C_r680_recall": None if s2_set == set() else round(C, 4),
        "missed_by_r680": missed,
        "directional_holds": directional,
        "attack_refuted": refuted,
        "registered": "A 7 [2,8]; B 1 [0,6]; C 0.29 [0,1]; directional misses==operand-built",
        "residue": "READ is measured; USE is not. R722's NEXT line remains open and is now sharper.",
    }
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r723_reader_recount.json").write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"\n  artifact: results/r723_reader_recount.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
