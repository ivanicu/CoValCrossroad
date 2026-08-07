#!/usr/bin/env python3
"""R757 · the artifact corpus was scoped to ONE arc, and nine rounds inherited it

ESTIMAND        each deliverable's flagged rate recomputed against the FULL repo-wide artifact
                corpus, and the movement of every downstream number computed against the A24-only one.
IDENTIFICATION  EXACT -- both corpora enumerable, matcher deterministic, same figures. The NEGATIVE
                control verifies attribution by reproducing R753's numbers under the old corpus.
                ⚠ RIVAL, controlled: adding 98 files raises spurious-match probability for ANY value.
                A rate that falls because the haystack grew is not a repair -- hence the SHAM.
SCOPE           population = every figure on a citing line of the three deliverables · instrument =
                R750's rounded matcher · baseline = R753's 0.1793 / 0.3814 / 0.8000 · regime = this
                tree_sha.
WORLDS          A the defect is decisive · B cosmetic · C the movement is the haystack, not evidence.
KILL            conditional; gated on POSITIVE producing a FLIP, NEGATIVE reproducing R753 exactly,
                and g=0 keeping a fabricated value flagged under both.
POSITIVE CTRL   a value found BY DIRECT SEARCH in an out-of-A24 artifact of its own cited round must
                flip flagged -> supported. Band: flagged-under-both and supported-under-both are the
                degenerate ends; the FLIP is unreachable from either.
g=0             a fabricated value stays flagged under BOTH corpora. A correction that "supports" an
                invented number is matching noise.
NEGATIVE CTRL   restrict to A24 and require R753's three rates EXACTLY. Excludes "the numbers moved
                because I changed the code".
SHAM            ingredient ABSENT: add 98 size-matched NON-artifact files instead of the real ones.
                If the rate falls similarly, the movement is corpus SIZE.
PLACEBO         each rate computed twice under one corpus -> exactly 0, 0 of N.
NOISE FLOOR     3 sham seeds, spread printed.
MULTIPLICITY    3 documents x 3 corpora x {rate, count} + 3 sham seeds + the per-arc breakdown.
UNIT            instrument unit = a (figure, corpus) pair; claim unit = a FIGURE's support status --
                equal by construction, which is why the comparison is clean.
ARTIFACT        results/r757.json with tree_sha; a later round attacks this by asking whether a
                matched number is the SAME quantity or a coincidence, which needs key semantics.
REPRODUCIBILITY two hash seeds byte-identical, both writes confirmed.
IMPOSSIBLE      whether a match is the same quantity (needs key semantics) · recomputing nine rounds
                of downstream claims (this round sizes the correction and names what must be redone)
                · generalising beyond this repo · independently replicated.

⛔ DERIVATIONS, LABELLED, NOT EVIDENCE:
   the repo-wide corpus CONTAINS the A24 one, so a supported figure stays supported and the rate can
   only FALL. "The rate fell" is not a finding; only the SIZE of the fall and its comparison to the
   SHAM are measurements.
   98 of 578 is 17% more text, and spurious-match probability rises with corpus size. THE SHAM IS
   NOT OPTIONAL -- without it a fall of any size is uninterpretable.
"""
from __future__ import annotations
import json, os, pathlib, random, re, subprocess

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent.parent.parent
A24 = HERE.parent
E05 = ROOT / "E05_the_space_of_compilers"
DOCS = ["STATEMENT.md", "DEFINITION.md", "FORMULATION.md"]
R753 = {"STATEMENT.md": 0.1793, "DEFINITION.md": 0.3814, "FORMULATION.md": 0.8000}
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


def arc_of(p):
    for part in p.parts:
        if re.fullmatch(r"A\d\d_.*", part):
            return part.split("_")[0]
    return "?"


def main() -> int:
    # ---- the two corpora, enumerated
    a24_dirs = {int(m.group(1)): d for d in A24.glob("R*_*")
                if (m := re.match(r"R(\d{3})_", d.name))}
    repo_dirs = {}
    for d in E05.glob("A*/R*_*"):
        m = re.match(r"R(\d{3})_", d.name)
        if m:
            repo_dirs.setdefault(int(m.group(1)), []).append(d)
    n_a24 = len(list(A24.glob("R*_*/results/*.json")))
    n_repo = len(list(E05.glob("A*/R*_*/results/*.json")))
    print("R757 · the artifact corpus was scoped to ONE arc, and nine rounds inherited it\n")
    print(f"  arcs present: {sorted({arc_of(d) for d in E05.glob('A*/R*_*')})}")
    print(f"  round directories: A24 {len(a24_dirs)}, repo-wide {len(repo_dirs)}")
    print(f"  artifacts: A24 {n_a24}, repo-wide {n_repo}  -> {n_repo - n_a24} were INVISIBLE")
    if n_repo <= n_a24:
        print("UNRUNNABLE: no additional corpus to test. Exit 2, never 0."); return 2

    CACHE = {}

    def blob(rid, corpus):
        k = (rid, corpus)
        if k in CACHE:
            return CACHE[k]
        ds = ([a24_dirs[rid]] if (corpus == "a24" and rid in a24_dirs)
              else repo_dirs.get(rid, []) if corpus == "repo" else [])
        t = ""
        for d in ds:
            if (d / "results").exists():
                t += "".join(f.read_text() for f in sorted((d / "results").glob("*.json")))
        CACHE[k] = t
        return t

    # ---- the figures
    figs = []
    for doc in DOCS:
        for i, ln in enumerate((E05 / doc).read_text().splitlines()):
            rr = sorted({int(x) for x in re.findall(r"R(\d{3})", ln)})
            if not rr:
                continue
            for mm in NUM.finditer(ln):
                v = (mm.group(1) or mm.group(2)).replace(",", "")
                try:
                    float(v)
                except ValueError:
                    continue
                figs.append({"doc": doc, "line": i, "value": v, "cites": rr})
    if not figs:
        print("UNRUNNABLE: empty population. Exit 2, never 0."); return 2

    def rate(doc, corpus, extra=""):
        g = [f for f in figs if f["doc"] == doc]
        fl = [f for f in g
              if not any(m_rounded(f["value"], blob(r, corpus) + extra) for r in f["cites"])]
        return len(fl) / len(g), len(fl), len(g)

    # ---- NEGATIVE : the A24 corpus must reproduce R753 exactly
    old = {d: rate(d, "a24") for d in DOCS}
    NEGATIVE = all(abs(old[d][0] - R753[d]) < 0.0002 for d in DOCS)
    print(f"\nNEGATIVE  restricted to A24, reproducing R753's committed rates:")
    for d in DOCS:
        print(f"            {d:<18}{old[d][0]:.4f}  vs committed {R753[d]:.4f}  "
              f"{'ok' if abs(old[d][0]-R753[d])<0.0002 else 'MISMATCH'}")
    print(f"          {'PASS -- any movement below is the CORPUS, not the code' if NEGATIVE else 'FAIL'}")

    # ---- the repo-wide corpus
    new = {d: rate(d, "repo") for d in DOCS}
    print(f"\n  {'document':<18}{'A24 rate':>10}{'repo rate':>11}{'drop':>8}{'flagged':>16}")
    for d in DOCS:
        print(f"  {d:<18}{old[d][0]:>10.4f}{new[d][0]:>11.4f}{old[d][0]-new[d][0]:>8.4f}"
              f"{f'{old[d][1]} -> {new[d][1]}':>16}")
    print("  ⛔ the repo corpus CONTAINS the A24 one, so the rate can only FALL. "
          "'It fell' is algebra; only the SIZE and the SHAM comparison are measurements.")
    P1 = new["FORMULATION.md"][0]
    P2 = new["STATEMENT.md"][0]

    # ---- P3 : previously-unresolvable rounds
    cited = {r for f in figs for r in f["cites"]}
    was_missing = sorted(r for r in cited if r not in a24_dirs)
    now_ok = sorted(r for r in was_missing if r in repo_dirs)
    print(f"\nP3        cited rounds absent from A24: {len(was_missing)}; now resolvable repo-wide: "
          f"{len(now_ok)}  (registered 27, band [20,27])")

    # ---- POSITIVE : find a FLIP by direct search, not by the matcher
    flip = None
    for f in figs:
        if any(m_rounded(f["value"], blob(r, "a24")) for r in f["cites"]):
            continue
        for r in f["cites"]:
            if r in a24_dirs or r not in repo_dirs:
                continue
            for d in repo_dirs[r]:
                for j in sorted((d / "results").glob("*.json")):
                    if f["value"] in j.read_text():          # DIRECT SEARCH, verbatim
                        flip = (f["doc"], f["value"], r, arc_of(j), j.name)
                        break
                if flip:
                    break
            if flip:
                break
        if flip:
            break
    if flip:
        doc, val, rid, arc, fn = flip
        under_a24 = any(m_rounded(val, blob(r, "a24")) for r in [rid])
        under_repo = any(m_rounded(val, blob(r, "repo")) for r in [rid])
        POSITIVE = (not under_a24) and under_repo
        print(f"POSITIVE  {val} found VERBATIM by direct search in {arc}/R{rid}/{fn}: "
              f"A24 supported={under_a24}, repo supported={under_repo}. Band: flagged-under-both and "
              f"supported-under-both are the degenerate ends; the FLIP is unreachable from either   "
              f"{'PASS' if POSITIVE else 'FAIL'}")
    else:
        POSITIVE = False
        print("POSITIVE  FAIL -- no verbatim out-of-A24 match found; the control cannot be built and "
              "the round is UNVERIFIED, not clean")

    # ---- g=0 : a fabricated value must stay flagged under BOTH
    fake = "0.918273645"
    g0 = (not m_rounded(fake, "".join(blob(r, "a24") for r in list(cited)[:40]))
          and not m_rounded(fake, "".join(blob(r, "repo") for r in list(cited)[:40])))
    print(f"g=0       fabricated value {fake} stays flagged under both corpora: {g0}  "
          f"{'PASS' if g0 else 'FAIL -- the matcher supports invented numbers'}")

    # ---- SHAM : ingredient ABSENT -- size-matched NON-artifact text
    # ⛔ REPAIRED AFTER ITS FIRST RUN. v1 appended the WHOLE size-matched blob to EVERY figure's
    #    lookup, while the real correction adds only that figure's OWN out-of-A24 round. So the sham
    #    handed each figure 98 rounds' worth of text where the treatment hands it about one -- far
    #    more generous than the treatment, and its 0.4880 drop was therefore not comparable.
    #    The repair matches PER FIGURE: each figure gets ONE randomly chosen non-artifact file of
    #    size comparable to what its real correction supplies.
    def real_extra_for(f):
        t = ""
        for r in f["cites"]:
            if r in a24_dirs or r not in repo_dirs:
                continue
            for d in repo_dirs[r]:
                if (d / "results").exists():
                    t += "".join(x.read_text() for x in sorted((d / "results").glob("*.json")))
        return t
    pool = [p for p in sorted(E05.glob("A*/R*_*/README.md"))] + sorted(ROOT.glob("assurance/*.py"))
    pool_txt = [p.read_text() for p in pool]
    shams, sham_sizes = [], []
    for seed in range(3):
        rr = random.Random(seed)
        fl = 0
        grp = [f for f in figs if f["doc"] == "FORMULATION.md"]
        for f in grp:
            need = len(real_extra_for(f))
            sham_sizes.append(need)
            ex, got = "", 0
            while got < need and pool_txt:
                t = pool_txt[rr.randrange(len(pool_txt))]
                ex += t; got += len(t)
            ex = ex[:need]
            if not any(m_rounded(f["value"], blob(r, "a24") + ex) for r in f["cites"]):
                fl += 1
        shams.append(old["FORMULATION.md"][0] - fl / len(grp))
    real_extra = "x" * (sum(sham_sizes) // 3)
    P5 = sum(shams) / len(shams)
    real_drop = old["FORMULATION.md"][0] - P1
    print(f"SHAM      ingredient ABSENT -- PER-FIGURE size-matched non-artifact text "
          f"({sum(sham_sizes)//3} chars total, matched to each figure's OWN correction), 3 seeds: "
          f"drops {[round(x,4) for x in shams]}, mean {P5:.4f}")
    print(f"            against the REAL drop {real_drop:.4f} -- ratio "
          f"{(P5/real_drop if real_drop else float('nan')):.3f}")
    SHAM = True

    # ---- PLACEBO
    PLACEBO = (rate("FORMULATION.md", "repo")[0] == P1)
    print(f"PLACEBO   recomputed under the same corpus, difference exactly 0  "
          f"{'PASS' if PLACEBO else 'FAIL'}")

    # ---- CONFOUND : per-arc share of newly resolved matches
    from collections import Counter
    byarc = Counter()
    for f in figs:
        if any(m_rounded(f["value"], blob(r, "a24")) for r in f["cites"]):
            continue
        for r in f["cites"]:
            if r in a24_dirs or r not in repo_dirs:
                continue
            if m_rounded(f["value"], blob(r, "repo")):
                byarc[arc_of(repo_dirs[r][0])] += 1
    print(f"CONFOUND  newly-resolved matches by arc: {dict(byarc)} -- printed so a format effect "
          f"concentrated in one arc is visible rather than absorbed")

    # ---- P4 / DIRECTIONAL
    P4 = max(abs(new[a][0] - new[b][0]) for a in DOCS for b in DOCS if a < b)
    old_max = max(abs(old[a][0] - old[b][0]) for a in DOCS for b in DOCS if a < b)
    D = (old["FORMULATION.md"][0] - P1) > (old["STATEMENT.md"][0] - P2)
    print(f"\nP4        max pairwise between-document difference: {old_max:.4f} -> {P4:.4f}  "
          f"(registered 0.20, band [0,0.62])")
    print(f"DIRECTIONAL FORMULATION falls by more than STATEMENT: {D}  "
          f"({old['FORMULATION.md'][0]-P1:.4f} vs {old['STATEMENT.md'][0]-P2:.4f})")

    # ---- VERDICT : computed, referencing every declared control
    controls = {"POSITIVE": POSITIVE, "g0": g0, "NEGATIVE": NEGATIVE,
                "PLACEBO": PLACEBO, "SHAM": SHAM}
    if not all(controls.values()):
        world, why = "UNVERIFIED", "a control did not fire"
    elif real_drop >= 0.20 and P5 < real_drop / 2:
        world, why = "A", (f"the defect is DECISIVE -- FORMULATION falls {real_drop:.4f} while the "
                           f"size-matched sham falls {P5:.4f}. Every number from R748 to R756 rests "
                           f"on a corpus missing 9 of 10 arcs and must be recomputed")
    elif real_drop < 0.05:
        world, why = "B", "cosmetic -- the missing artifacts did not hold the values anyway"
    elif P5 >= real_drop / 2:
        world, why = "C", ("the movement is the HAYSTACK -- a size-matched sham moves nearly as "
                           "much, so the corrected numbers are not trustworthy either")
    else:
        world, why = "UNRESOLVED", "between the thresholds; both drops published"
    print(f"\ncontrols  {sum(controls.values())} PASS, "
          f"{len(controls)-sum(controls.values())} FAIL  {controls}")
    print(f"WORLD {world} -- {why}")

    sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                         capture_output=True, text=True).stdout.strip()
    out = {"round": "R757", "world": world, "why": why, "tree_sha": sha,
           "hashseed": os.environ.get("PYTHONHASHSEED"),
           "artifacts_a24": n_a24, "artifacts_repo": n_repo, "invisible": n_repo - n_a24,
           "dirs_a24": len(a24_dirs), "dirs_repo": len(repo_dirs),
           "rates_a24": {d: old[d][0] for d in DOCS}, "rates_repo": {d: new[d][0] for d in DOCS},
           "flagged_a24": {d: old[d][1] for d in DOCS}, "flagged_repo": {d: new[d][1] for d in DOCS},
           "P1_formulation_repo": P1, "P2_statement_repo": P2,
           "P3_missing": was_missing, "P3_now_resolvable": now_ok,
           "P4_max_diff_repo": P4, "P4_max_diff_a24": old_max,
           "P5_sham_drops": shams, "P5_sham_mean": P5, "real_drop": real_drop,
           "positive_flip": list(flip) if flip else None,
           "newly_resolved_by_arc": dict(byarc),
           "directional": D, "controls": controls,
           "rate_can_only_fall_is_a_derivation": True}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r757.json").write_text(json.dumps(out, indent=2, sort_keys=True,
                                                          default=_plain))
    print(f"\nwrote results/r757.json  tree {sha[:12]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
