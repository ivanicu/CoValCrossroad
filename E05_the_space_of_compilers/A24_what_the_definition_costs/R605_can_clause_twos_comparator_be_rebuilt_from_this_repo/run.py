#!/usr/bin/env python3
"""
R605 -- can clause ②'s comparator be rebuilt from this repository?

CHECK #204 CAUGHT TWO UNVERIFIED CLAIMS in R604's closing line. It said `genericpool16[:4]` is
*"assembled in corebench"* -- a LOCATION never checked, and wrong: nothing in the tree
assembles it. And it said *"the scorer can settle what a search cannot"* -- reading
construction code settles the CONSTRUCTION, never that the committed numbers came from it,
which is §4's `determinism read as currency` distinction and was elided.

What the search found instead is sharper than a rename. R454's own docstring separates the two
objects: *"`genericpool16` k=16 on all 968 prompts; **`full` is the RUBRIC (prompt-SPECIFIC)**"*.
So the scored comparator is a GENERIC 16-criterion pool, while `STATEMENT.md` describes ②'s
baseline as *"the released pool's first four by file order"*. And `sat_genericpool16.npz` sits
in `corebench/results/` with NO script in the repository writing it.

ESTIMAND        For every scored artifact `corebench/results/sat_*.npz`: does any .py or .sh in
                the repository WRITE it? n_unbuildable is the count whose construction is not
                recoverable here, and whether ②'s comparator is among them is the decision.
IDENTIFICATION  Exact for "a script names this file in a writing context". ⚠ A builder could
                name the path indirectly (an f-string, a loop over stems), so the count is an
                UPPER BOUND on unbuildability -- a file may have a builder the search cannot
                see. Every miss is therefore checked a second way, by stem, before it counts.
SCOPE           population : corebench/results/sat_*.npz
                instrument : filename and stem occurrence in a write-context line
                             instrument unit = A PATH NAMED NEAR A WRITE CALL
                             claim unit      = A SCRIPT THAT PRODUCES THE FILE
                             NOT equal -- indirect construction is invisible, so the result is
                             an upper bound and says so
                baseline   : artifacts whose builders ARE in the tree, if any exist
                regime     : as committed at this sha
WORLDS          A REBUILDABLE: ②'s comparator has a builder here -> the construction can be
                  compared to the page's wording and R604's open question closes.
                B UNBUILDABLE, TYPICAL: it has none AND most artifacts have none -> the corpus
                  imports its scored matrices wholesale, which is a property of the SITE and
                  not a defect specific to ②.
                C UNBUILDABLE, EXCEPTIONAL: it has none while most others do -> ②'s comparator
                  specifically cannot be reconstructed, and the page's description of it is
                  unverifiable from this repository.
KILL            pre-registered: if NO artifact in the population has a discoverable builder,
                the detector has never returned positive and every `unbuildable` is silence,
                not absence -- verdict UNVERIFIED regardless of what ② does.
POSITIVE CTRL   the detector must find a builder for at least one artifact. Its identity is
                not chosen in advance -- whichever it finds is reported.
NEGATIVE CTRL   an invented artifact name must have no builder, proving absence is detectable
                rather than universal.
PLACEBO         a file that certainly HAS a producer in-tree -- a round's own results/*.json,
                written by its own run.py -- must be detected as built.
SEEDS           n/a, deterministic.
MULTIPLICITY    every artifact x every script + 3 control checks, all reported.
ARTIFACT        results/rebuildable.json
IMPOSSIBLE      construct validity for "the committed matrix came from that builder": even a
                found builder proves the construction, not the provenance of the bytes. That
                needs a hash recorded at write time, which these artifacts do not carry.
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
WRITE = re.compile(r"savez|np\.save|\.write|open\([^)]*[\"']w|to_csv|dump", re.I)


def scripts():
    out = []
    for p in ROOT.rglob("*.py"):
        if ".venv" in p.parts or "R605_" in str(p):
            continue
        try:
            out.append((p, p.read_text(errors="ignore")))
        except Exception:
            pass
    for p in ROOT.rglob("*.sh"):
        if ".venv" in p.parts:
            continue
        try:
            out.append((p, p.read_text(errors="ignore")))
        except Exception:
            pass
    return out


def builder_for(name, stem, S):
    """A script that names the file (or its stem) on a line that also writes."""
    hits = []
    for p, t in S:
        for line in t.split("\n"):
            if (name in line or stem in line) and WRITE.search(line):
                hits.append((str(p.relative_to(ROOT)), line.strip()[:100]))
                break
    return hits


def main():
    RES = ROOT / "corebench" / "results"
    if not RES.is_dir():
        print("UNRUNNABLE: corebench/results absent. Exit 2, never 0."); return 2
    arts = sorted(RES.glob("sat_*.npz"))
    if not arts:
        print("UNRUNNABLE: no sat_*.npz. Exit 2."); return 2
    S = scripts()
    print(f"POPULATION  {len(arts)} scored artifacts in corebench/results, "
          f"{len(S)} scripts searched")

    built, unbuilt = {}, []
    for a in arts:
        h = builder_for(a.name, a.stem, S)
        if h:
            built[a.name] = h
        else:
            unbuilt.append(a.name)

    print(f"\n─── CONTROLS ───")
    pos_ok = len(built) > 0
    print(f"  POSITIVE  the detector finds a builder for at least one artifact: "
          f"{len(built)} of {len(arts)} -> {'PASS' if pos_ok else '⛔ FAIL — every zero below is silence'}")
    if built:
        k = sorted(built)[0]
        print(f"            e.g. {k} <- {built[k][0][0]}")
    neg = builder_for("sat_zzq_invented.npz", "sat_zzq_invented", S)
    neg_ok = not neg
    print(f"  NEGATIVE  an invented artifact name: {len(neg)} builder(s) -> "
          f"{'PASS — absence is detectable' if neg_ok else '⛔ FAIL'}")
    own = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs/R604_does_clause_twos_baseline_name_exist_in_any_artifact/results/baseline_name.json"
    plc = builder_for(own.name, own.stem, S) if own.is_file() else []
    plc_ok = bool(plc)
    print(f"  PLACEBO   a file certainly written in-tree ({own.name}): {len(plc)} builder(s) -> "
          f"{'PASS' if plc_ok else '⛔ FAIL — the detector cannot see a producer it should'}")
    controls_ok = pos_ok and neg_ok and plc_ok

    print(f"\n─── REBUILDABILITY ───")
    print(f"  artifacts WITH a builder in-tree : {len(built)}")
    print(f"  artifacts WITHOUT               : {len(unbuilt)}")
    target = "sat_genericpool16.npz"
    t_built = target in built
    print(f"\n  ②'s comparator `{target}`: "
          f"{'HAS a builder — ' + built[target][0][0] if t_built else '⛔ NO builder in the repository'}")
    for n in unbuilt[:10]:
        print(f"      unbuildable: {n}")
    if len(unbuilt) > 10:
        print(f"      … and {len(unbuilt)-10} more")

    print(f"\n─── VERDICT ───")
    frac = len(unbuilt) / len(arts)
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; an absent builder is silence, not absence"
    elif t_built:
        world = f"A REBUILDABLE — ②'s comparator has a builder in-tree"
    elif frac >= 0.5:
        world = (f"B UNBUILDABLE, TYPICAL — {len(unbuilt)} of {len(arts)} scored artifacts "
                 f"({frac:.1%}) have no builder here, ②'s among them. The site IMPORTS its "
                 f"scored matrices; that is a property of the corpus, not a defect specific to "
                 f"②. ⚠ But it means the page's description of ②'s baseline cannot be checked "
                 f"against a construction that is not present.")
    else:
        world = (f"C UNBUILDABLE, EXCEPTIONAL — ②'s comparator has no builder while "
                 f"{len(built)} of {len(arts)} others do")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: {len(arts)} artifacts x {len(S)} scripts + 3 control checks. "
          f"UPPER BOUND: indirect construction is invisible to this detector.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "rebuildable.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "n_artifacts": len(arts), "n_scripts": len(S),
        "built": {k: v[:2] for k, v in built.items()}, "unbuilt": unbuilt,
        "target": target, "target_built": t_built, "frac_unbuilt": frac,
        "check204": ("R604's closing line placed the construction 'in corebench' without "
                     "checking, and said 'the scorer can settle what a search cannot' — reading "
                     "construction code settles the CONSTRUCTION, never the provenance of the "
                     "committed bytes"),
        "r454_says": ("`genericpool16` k=16 on all 968 prompts; `full` is the RUBRIC "
                      "(prompt-SPECIFIC) — the two objects are distinguished in a round's own "
                      "docstring"),
        "impossible": ("even a found builder proves the construction, not that the committed "
                       "matrix came from it; that needs a write-time hash these artifacts lack"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'rebuildable.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
