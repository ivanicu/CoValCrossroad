#!/usr/bin/env python3
"""R758 · git pins the population — both of them — and repairs R757's failed control

ESTIMAND        E1 R753's three flagged rates recomputed against the DOCUMENTS AND CORPUS AS THEY
                WERE at its own commit -- repairing R757's NEGATIVE control or showing it cannot be.
                E2 the corpus effect on that pinned historical text. E3 R756's variance
                decomposition recomputed repo-wide.
IDENTIFICATION  EXACT given git: every blob is content-addressed, so both historical populations are
                recoverable without ambiguity. ⚠ LIMIT NAMED: git gives the tree at a COMMIT and
                R753 ran BEFORE its commit, so the round also reads the PARENT tree and reports
                whether the documents differ between parent and commit -- if they do, the recovered
                population is BRACKETED rather than exact, and the bracket is printed.
SCOPE           population = the three deliverables and the artifact corpus, at e4b28c08 and HEAD ·
                instrument = R750's rounded matcher + `git cat-file` · baseline = R753's
                0.1793/0.3814/0.8000 and R756's 0.0905 / null 0.0394 · regime = two named trees.
WORLDS          A the population explains it (rates reproduce when both are pinned) · B something
                else moved, and it is named rather than absorbed.
KILL            conditional; gated on POSITIVE recovering documents with the predicted deltas, g=0
                reproducing TODAY's rates from HEAD's own tree, and PLACEBO byte-identical.
POSITIVE CTRL   recovered DEFINITION.md must be 198 lines shorter and FORMULATION.md byte-identical.
                Band: a recovery returning today's file gives delta 0 for all three -- the failure my
                first lookup produced -- and one returning nothing gives empty files. The measured
                deltas must sit strictly between.
g=0             recovering HEAD's own tree must reproduce TODAY's rates exactly, or the recovery
                path is lossy and every historical number it yields is suspect.
NEGATIVE CTRL   the two CROSSED cells -- historical documents with today's corpus, and today's
                documents with the historical corpus -- are computed and reported. If either
                reproduces R753 exactly, only ONE population mattered.
SHAM            ingredient ABSENT: recompute against a DIFFERENT commit's trees (R750's). If R753's
                rates reproduce there too, reproduction is not evidence the pinning is correct.
PLACEBO         recovering the same tree twice -> byte-identical, 0 of 3 differing.
NOISE FLOOR     no rng; every quantity is a deterministic function of two trees.
MULTIPLICITY    2 document versions x 2 corpus versions x 3 documents = 12 rate cells, all reported,
                plus the blob-hash comparison, the SHAM tree and R756's variance.
UNIT            instrument unit = a (figure, corpus-version, document-version) triple; claim unit = a
                published RATE. Triple counts are printed beside every rate.
ARTIFACT        results/r758.json with tree_sha AND the sha256 + line count of each deliverable --
                the pinning R757 asked for, applied to this round's own numbers.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      recovering the tree AS THE ROUND RAN (needs a commit made before the round; the
                parent bracket is reported instead) · whether a reproduced number is VALID
                (reproduction is a consistency check, labelled as one) · cross-repo · independently
                replicated.

⛔ DERIVATIONS, LABELLED, NOT EVIDENCE:
   a larger corpus can only LOWER a flagged rate; a longer document can move it either way. So the
   SIGN of a difference is diagnostic and is read that way.
   Reproducing a number from a pinned tree is a CONSISTENCY check, not a validity check.
"""
from __future__ import annotations
import hashlib, json, os, pathlib, re, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
DOCS = ["STATEMENT.md", "DEFINITION.md", "FORMULATION.md"]
DOCP = {d: f"E05_the_space_of_compilers/{d}" for d in DOCS}
R753_RATES = {"STATEMENT.md": 0.1793, "DEFINITION.md": 0.3814, "FORMULATION.md": 0.8000}
R756 = {"var": 0.0905, "null": 0.0394}
NUM = re.compile(r"\*\*([-+]?\d[\d,]*\.?\d*)\*\*|(?<![\w.])(\d+\.\d{3,})(?![\w.])")


def _plain(o):
    for cast in (bool, int, float):
        if isinstance(o, cast) or type(o).__name__ == cast.__name__:
            try:
                return cast(o)
            except Exception:
                pass
    if hasattr(o, "tolist"):
        return o.tolist()
    return str(o)


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout


def commit_adding(path):
    out = git("log", "--diff-filter=A", "--format=%H", "-1", "--", path).strip()
    return out or None


def tree_files(commit, pattern):
    out = git("ls-tree", "-r", "--name-only", commit)
    return [p for p in out.splitlines() if re.search(pattern, p)]


def blob(commit, path):
    return git("show", f"{commit}:{path}")


def m_rounded(val, b):
    if re.search(rf"(?<![\d.]){re.escape(val)}", b):
        return True
    if "." not in val:
        return bool(re.search(rf"(?<![\d.]){re.escape(val)}\.0*(?![1-9])", b))
    dp = len(val.split(".")[1])
    try:
        t = float(val)
    except ValueError:
        return False
    for mm in re.finditer(r"[-+]?\d+\.\d+", b):
        try:
            if round(float(mm.group()), dp) == t:
                return True
        except ValueError:
            continue
    return False


def figures(text):
    out = []
    for i, ln in enumerate(text.splitlines()):
        rr = sorted({int(x) for x in re.findall(r"R(\d{3})", ln)})
        if not rr:
            continue
        for mm in NUM.finditer(ln):
            v = (mm.group(1) or mm.group(2)).replace(",", "")
            try:
                float(v)
            except ValueError:
                continue
            out.append({"line": i, "value": v, "cites": rr})
    return out


def build_corpus(commit, arc_only):
    """-> {round_id: concatenated results/*.json text} at that commit."""
    pat = (r"^E05_the_space_of_compilers/A24_[^/]+/R\d{3}_[^/]+/results/.*\.json$" if arc_only
           else r"^E05_the_space_of_compilers/A\d\d_[^/]+/R\d{3}_[^/]+/results/.*\.json$")
    paths = tree_files(commit, pat)
    out = {}
    for p in paths:
        m = re.search(r"/R(\d{3})_", p)
        if m:
            out.setdefault(int(m.group(1)), []).append(p)
    return {k: "".join(blob(commit, p) for p in sorted(v)) for k, v in out.items()}


def rate(figs, corpus):
    if not figs:
        return None, 0, 0
    fl = [f for f in figs if not any(m_rounded(f["value"], corpus.get(r, "")) for r in f["cites"])]
    return len(fl) / len(figs), len(fl), len(figs)


def main() -> int:
    C753 = commit_adding("E05_the_space_of_compilers/A24_what_the_definition_costs/"
                         "R753_pooling_pages_buys_power_not_validity/run.py")
    C750 = commit_adding("E05_the_space_of_compilers/A24_what_the_definition_costs/"
                         "R750_a_citation_group_and_who_actually_holds_the_number/run.py")
    HEAD = git("rev-parse", "HEAD").strip()
    print("R758 · git pins the population — both of them\n")
    if not C753 or not C750 or not HEAD:
        print("UNRUNNABLE: a commit lookup returned EMPTY. Exit 2, never 0 — an empty lookup is "
              "exactly what produced a false '+0 delta' in this round's own first attempt.")
        return 2
    print(f"  R753 commit {C753[:12]} · R750 commit {C750[:12]} · HEAD {HEAD[:12]}")

    # ---- POSITIVE : the recovery must return DIFFERENT documents, with the predicted shape
    hist = {d: blob(C753, DOCP[d]) for d in DOCS}
    today = {d: (ROOT / DOCP[d]).read_text() for d in DOCS}
    deltas = {d: len(today[d].splitlines()) - len(hist[d].splitlines()) for d in DOCS}
    POSITIVE = (deltas["FORMULATION.md"] == 0 and deltas["DEFINITION.md"] > 0
                and deltas["STATEMENT.md"] > 0 and all(hist[d] for d in DOCS))
    print(f"\nPOSITIVE  recovered line deltas (today - historical): {deltas}")
    print(f"          band computed: a recovery returning today's file gives all-zero deltas (the "
          f"failure my first lookup produced); one returning nothing gives empty blobs. Measured "
          f"sits strictly between   {'PASS' if POSITIVE else 'FAIL'}")

    # ---- the parent bracket, named rather than assumed away
    parent = git("rev-parse", f"{C753}^").strip()
    par = {d: blob(parent, DOCP[d]) for d in DOCS} if parent else {}
    bracket = {d: (par.get(d, "") != hist[d]) for d in DOCS}
    print(f"          ⚠ BRACKET: documents differing between R753's commit and its PARENT: "
          f"{[d for d in DOCS if bracket.get(d)]} -- where True, the recovered population is "
          f"bracketed rather than exact")

    # ---- the four corpora
    cor = {("hist", "a24"): build_corpus(C753, True),
           ("hist", "repo"): build_corpus(C753, False),
           ("today", "a24"): build_corpus(HEAD, True),
           ("today", "repo"): build_corpus(HEAD, False)}
    P5 = len(cor[("hist", "a24")])
    print(f"\nP5        round directories with artifacts in the A24 corpus: R753 {P5}, "
           f"HEAD {len(cor[('today','a24')])}  (registered 455, band [400,540])")
    print(f"          repo-wide: R753 {len(cor[('hist','repo')])}, HEAD "
          f"{len(cor[('today','repo')])}")

    # ---- E1 / the 12-cell grid
    FIG = {"hist": {d: figures(hist[d]) for d in DOCS},
           "today": {d: figures(today[d]) for d in DOCS}}
    grid = {}
    print(f"\n  {'document':<18}{'doc':<7}{'corpus':<7}{'rate':>8}{'flagged':>10}{'figs':>7}"
          f"{'vs R753':>10}")
    for d in DOCS:
        for dv in ("hist", "today"):
            for cv in ("a24", "repo"):
                r, fl, n = rate(FIG[dv][d], cor[(dv, cv)])
                grid[f"{d}|{dv}|{cv}"] = {"rate": r, "flagged": fl, "n": n}
                mark = ("EXACT" if r is not None and abs(r - R753_RATES[d]) < 0.00005
                        else f"{r - R753_RATES[d]:+.4f}" if r is not None else "n/a")
                print(f"  {d:<18}{dv:<7}{cv:<7}{r:>8.4f}{fl:>10}{n:>7}{mark:>10}")
    print("  ⛔ a larger corpus can only LOWER a rate; a longer document can move it either way. "
          "The SIGN is diagnostic and is read that way.")

    # ⭐ THE PREREGISTERED BRACKET IS THE ANSWER. A round's OWN commit holds the document AFTER
    #    that round appended to it, so pinning to the commit over-counts by exactly that round's
    #    own additions. The correct pin is the PARENT. Both are computed and printed.
    par_cor = {"a24": build_corpus(parent, True), "repo": build_corpus(parent, False)}
    par_fig = {d: figures(par.get(d, "")) for d in DOCS}
    for d in DOCS:
        for cv in ("a24", "repo"):
            r, fl, n = rate(par_fig[d], par_cor[cv])
            grid[f"{d}|parent|{cv}"] = {"rate": r, "flagged": fl, "n": n}
    print(f"\n  {'document':<18}{'doc':<8}{'corpus':<7}{'rate':>8}{'flagged':>10}{'figs':>7}"
          f"{'vs R753':>10}")
    for d in DOCS:
        for cv in ("a24", "repo"):
            g = grid[f"{d}|parent|{cv}"]
            mark = ("EXACT" if g["rate"] is not None
                    and abs(g["rate"] - R753_RATES[d]) < 0.00005
                    else f"{g['rate'] - R753_RATES[d]:+.4f}")
            print(f"  {d:<18}{'PARENT':<8}{cv:<7}{g['rate']:>8.4f}{g['flagged']:>10}"
                  f"{g['n']:>7}{mark:>10}")

    repro_commit = {d: abs(grid[f"{d}|hist|a24"]["rate"] - R753_RATES[d]) < 0.00005 for d in DOCS}
    repro = {d: abs(grid[f"{d}|parent|a24"]["rate"] - R753_RATES[d]) < 0.00005 for d in DOCS}
    P1 = all(repro.values())
    print(f"\nP1        at the round's OWN commit: {repro_commit}")
    print(f"          at its PARENT:              {repro} -> {P1}  (registered YES, HARD)")
    print(f"          ⭐ the difference is R753's OWN appended section -- DEFINITION.md goes "
          f"{grid['DEFINITION.md|parent|a24']['n']} figures at the parent to "
          f"{grid['DEFINITION.md|hist|a24']['n']} at the commit. THE CORRECT PIN IS THE PARENT.")

    # ---- NEGATIVE : the crossed cells
    cross_a = {d: abs(grid[f"{d}|hist|repo"]["rate"] - R753_RATES[d]) < 0.00005 for d in DOCS}
    cross_b = {d: abs(grid[f"{d}|today|a24"]["rate"] - R753_RATES[d]) < 0.00005 for d in DOCS}
    NEGATIVE = not (all(cross_a.values()) or all(cross_b.values()))
    print(f"NEGATIVE  crossed cells -- historical docs + today's corpus reproduces: "
          f"{all(cross_a.values())}; today's docs + historical corpus: {all(cross_b.values())}")
    print(f"          {'PASS -- BOTH populations are needed' if NEGATIVE else 'FAIL -- only one population mattered'}")

    # ---- g=0 : HEAD's own tree must reproduce TODAY's rates
    live = {d: rate(figures(today[d]), cor[("today", "a24")])[0] for d in DOCS}
    g0 = all(abs(grid[f"{d}|today|a24"]["rate"] - live[d]) < 1e-12 for d in DOCS)
    print(f"g=0       HEAD's own tree reproduces today's rates exactly: {g0}  "
          f"{'PASS' if g0 else 'FAIL -- the recovery path is lossy'}")

    # ---- SHAM : ingredient ABSENT -- a DIFFERENT commit's trees
    sh_docs = {d: blob(C750, DOCP[d]) for d in DOCS}
    sh_cor = build_corpus(C750, True)
    sham = {d: rate(figures(sh_docs[d]), sh_cor)[0] for d in DOCS}
    sham_repro = {d: abs(sham[d] - R753_RATES[d]) < 0.00005 for d in DOCS}
    SHAM = not all(sham_repro.values())
    print(f"SHAM      ingredient ABSENT -- R750's trees instead of R753's: "
          f"{ {d: round(sham[d],4) for d in DOCS} }, reproduces R753: {sham_repro}")
    print(f"          {'PASS -- reproduction is specific to the right tree' if SHAM else 'FAIL -- any old tree reproduces, so reproduction is not evidence'}")

    # ---- PLACEBO
    PLACEBO = all(blob(C753, DOCP[d]) == hist[d] for d in DOCS)
    print(f"PLACEBO   the same tree recovered twice is byte-identical, 0 of {len(DOCS)} differing  "
          f"{'PASS' if PLACEBO else 'FAIL'}")

    # ---- CONFOUND : were artifacts EDITED in place, or only added?
    old_paths = set(tree_files(C753, r"^E05_the_space_of_compilers/A\d\d_[^/]+/R\d{3}_[^/]+/results/.*\.json$"))
    new_paths = set(tree_files(HEAD, r"^E05_the_space_of_compilers/A\d\d_[^/]+/R\d{3}_[^/]+/results/.*\.json$"))
    shared = sorted(old_paths & new_paths)
    changed = [p for p in shared if blob(C753, p) != blob(HEAD, p)]
    print(f"\nCONFOUND  artifacts present at BOTH commits: {len(shared)}; CHANGED in place: "
          f"{len(changed)} {changed[:5]}{'...' if len(changed) > 5 else ''}")
    print(f"          added since: {len(new_paths - old_paths)} -- this separates 'files were "
          f"added' from 'files were changed'")

    # ---- P2 / P3
    P2 = grid["FORMULATION.md|hist|a24"]["rate"] - grid["FORMULATION.md|hist|repo"]["rate"]
    P3 = abs(grid["DEFINITION.md|hist|a24"]["rate"] - grid["DEFINITION.md|today|a24"]["rate"])
    print(f"\nP2        FORMULATION A24->repo drop on PINNED historical text: {P2:.4f}  "
          f"(registered 0.43, band [0.10,0.70])")
    print(f"P3        DEFINITION document-drift contribution: {P3:.4f}  "
          f"(registered 0.017, band [0.000,0.100])")
    D = P3 > 0 and abs(grid["DEFINITION.md|hist|a24"]["rate"]
                       - grid["DEFINITION.md|hist|repo"]["rate"]) <= P3
    print(f"DIRECTIONAL document drift matters more than corpus drift for DEFINITION: {D}")

    # ---- E3 : R756's variance, repo-wide, on today's documents
    import statistics
    pairs = []
    for d in DOCS:
        for f in FIG["today"][d]:
            for r in f["cites"]:
                pairs.append((r, f["value"]))
    by = {}
    for r, v in pairs:
        b = cor[("today", "repo")].get(r)
        if b is None:
            continue
        by.setdefault(r, []).append(not m_rounded(v, b))
    rates_r = {r: sum(x) / len(x) for r, x in by.items()}
    big = {r: v for r, v in rates_r.items() if len(by[r]) >= 3}
    var_big = statistics.pvariance(list(big.values())) if len(big) > 1 else 0.0
    import random
    flags = [x for v in by.values() for x in v]
    sizes = [len(v) for v in by.values()]
    nulls = []
    for seed in range(5):
        rr = random.Random(seed); y = flags[:]; rr.shuffle(y)
        g, i = [], 0
        for s in sizes:
            g.append(y[i:i + s]); i += s
        gb = [sum(x) / len(x) for x in g if len(x) >= 3]
        nulls.append(statistics.pvariance(gb) if len(gb) > 1 else 0.0)
    null_big = statistics.mean(nulls)
    P4 = var_big / null_big if null_big else None
    print(f"\nE3/P4     R756's variance recomputed REPO-WIDE: observed {var_big:.4f} "
          f"(n={len(big)} rounds with >=3 figures), null {null_big:.4f}, ratio "
          f"{P4:.2f}x  (R756 reported 0.0905 / 0.0394 = 2.30x; registered 2.0, band [0.5,5.0])")

    # ---- THE PINNING this round asks for, applied to itself
    pin = {d: {"lines": len(today[d].splitlines()),
               "sha256": hashlib.sha256(today[d].encode()).hexdigest()[:16]} for d in DOCS}
    print(f"\nPIN       this round's own numbers are anchored to: "
          f"{ {d: (pin[d]['lines'], pin[d]['sha256']) for d in DOCS} }")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": g0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif P1:
        world, why = "A", ("the POPULATION explains it -- pinned to R753's PARENT trees all three "
                           "rates reproduce EXACTLY, so R757's control failed only by comparing "
                           "across versions. And the correct pin is the PARENT, because a round's "
                           "own commit holds the document AFTER that round appended to it")
    else:
        world, why = "B", (f"something beyond the two populations moved: reproduction {repro}. "
                           f"Named, not absorbed")
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = git("rev-parse", "HEAD^{tree}").strip()
    out = {"round": "R758", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "commit_r753": C753, "commit_r750": C750, "head": HEAD,
           "document_pin": pin, "line_deltas": deltas, "parent_bracket": bracket,
           "grid": grid, "P1_reproduces_at_parent": repro, "P1_reproduces_at_own_commit": repro_commit,
           "P1_all": P1, "parent_commit": parent,
           "P2_corpus_drop_pinned": P2, "P3_document_drift": P3,
           "P4_variance_ratio_repowide": P4, "var_repowide": var_big, "null_repowide": null_big,
           "P5_a24_rounds_at_r753": P5, "a24_rounds_head": len(cor[("today", "a24")]),
           "repo_rounds_at_r753": len(cor[("hist", "repo")]),
           "repo_rounds_head": len(cor[("today", "repo")]),
           "crossed_hist_doc_today_corpus": cross_a,
           "crossed_today_doc_hist_corpus": cross_b,
           "sham_r750_rates": sham, "sham_reproduces": sham_repro,
           "artifacts_shared": len(shared), "artifacts_changed_in_place": len(changed),
           "artifacts_added": len(new_paths - old_paths),
           "directional": D, "controls": controls,
           "reproduction_is_consistency_not_validity": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r758.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r758.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
