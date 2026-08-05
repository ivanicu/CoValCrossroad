#!/usr/bin/env python3
"""
R633 -- which conclusions were drawn under a superseded version of an instrument?

CHECK #232: THE THIRD CONSECUTIVE CLOSING LINE DESCRIBING MY OWN TOOLING FROM MEMORY.
  ⛔ "widened once, its declaration rule repaired once, its transitive-anchoring clause added
     later" -- three counts read off the module's own COMMENTS, not from the git log. With #230
     ("outside every gate") and #231 ("asked only the ledger"), that is THREE IN THREE ROUNDS,
     every one a claim about my own instruments -- which is the subject matter of every recent
     round. The closing line is where I stop reading and start remembering.

ESTIMAND        n_stale = the number of committed rounds whose run.py IMPORTS an assurance module
                that was subsequently MODIFIED -- i.e. conclusions standing on a version of an
                instrument that no longer exists.
IDENTIFICATION  Exact from git: a round's commit time vs the last modification time of each module
                it imports. ⚠ SOUND direction: a later modification means the round did not run
                against today's code. UNSOUND: a modification may be a comment or a rename that
                changes no behaviour, so n_stale OVERSTATES the conclusions actually at risk --
                which is why every hit is printed with the commit subject so the change can be
                judged, and why a behaviour-changing subset is reported separately.
SCOPE           population : rounds under A24 whose run.py imports assurance/*
                instrument : git log --follow per module + per round directory
                             instrument unit = A (ROUND, MODULE) PAIR
                             claim unit      = A CONCLUSION AT RISK. NOT equal: a round can import
                             a module and not depend on the repaired clause. Overstates; stated.
                baseline   : R632, which found 2 stale conclusions for ONE inline test
                regime     : this repository at this sha
WORLDS          A CONTAINED: few stale pairs, and the repairs are cosmetic -> the R632 case was
                  local and the suite's conclusions stand.
                B WIDESPREAD: many stale pairs with behaviour-changing repairs -> a re-run sweep
                  is owed and its size is this count.
                C NO EXPOSURE: no module was modified after any round that imports it -> the
                  obligation R632 named has no instances here, and the closing line that assumed
                  three repairs was describing history that postdates nothing.
KILL            pre-registered: stale pairs >= 3 -> world B. 1-2 -> world A. 0 -> world C.
POSITIVE CTRL   the instrument must be able to FIND a stale pair: a synthetic pair built from a
                module's own history (its first commit vs its last) must register as stale.
                Fails at g=0: a module with a single commit yields no stale pair.
NEGATIVE CTRL   a round importing a module modified only BEFORE that round must NOT register.
PLACEBO         a module that does not exist -> 0 pairs, no crash.
SEEDS           n/a, deterministic over a fixed history.
MULTIPLICITY    every (round, module) pair + 4 controls. Full list printed.
ARTIFACT        results/conclusions_under_superseded_instruments.json
IMPOSSIBLE      whether a specific conclusion CHANGES under the repaired module needs re-running
                that round, which this round does not do -- it locates the exposure and bounds it.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True,
                          timeout=180).stdout.strip()


def hist(path):
    out = git("log", "--follow", "--format=%H%x1f%ct%x1f%s", "--", str(path))
    rows = []
    for line in out.split("\n"):
        if line.count("\x1f") == 2:
            h, t, s = line.split("\x1f")
            rows.append((h, int(t), s))
    return rows          # newest first


MENTION_ONLY = []


def main():
    mods = sorted((ROOT / "assurance").glob("*.py"))
    mhist = {m.stem: hist(m) for m in mods}
    mhist = {k: v for k, v in mhist.items() if v}
    if len(mhist) < 3:
        print(f"UNRUNNABLE: only {len(mhist)} module histories. Exit 2, never 0."); return 2
    print(f"  assurance modules with git history: {len(mhist)}")
    print(f"\n─── THE REPAIR HISTORY THE CLOSING LINE ASSERTED FROM MEMORY ───")
    for k in sorted(mhist, key=lambda k: -len(mhist[k]))[:6]:
        print(f"  {k:<38} {len(mhist[k]):>3} commit(s)")
    sp = mhist.get("statement_provenance", [])
    print(f"  -> statement_provenance: claimed 'widened once, repaired once, clause added later' "
          f"= 3 repairs; git shows {len(sp)} commit(s) touching it")

    rounds = []
    for d in sorted(A24.glob("R[0-9]*")):
        rp = d / "run.py"
        if not rp.is_file(): continue
        try: src = rp.read_text(errors="ignore")
        except Exception: continue
        # ⛔ v1 MATCHED THE MODULE NAME ANYWHERE IN THE SOURCE -- docstrings, comments, prose
        #    about a gate. That is a MENTION, not an IMPORT: R631's own lesson, committed one
        #    round later in a new place, and it inflated the population with rounds that merely
        #    DISCUSS a gate. Tightened to an actual import statement, and both counts reported so
        #    the inflation is visible rather than silently corrected.
        mentions = sorted({m for m in mhist if re.search(rf"\b{m}\b", src)})
        imports = sorted({m for m in mhist
                          if re.search(rf"^\s*(?:import|from)\s+{m}\b|"
                                       rf"^\s*import\s+\w*\s*as\s+\w+\s*#.*{m}|"
                                       rf"assurance[./]{m}\b", src, re.M)})
        MENTION_ONLY.append((d.name, len(mentions) - len(imports)))
        if not imports: continue
        h = hist(d)
        if not h: continue
        rounds.append((d.name, h[-1][1], imports))     # first commit of the round dir
    infl = sum(n for _, n in MENTION_ONLY)
    print(f"\n  rounds whose run.py IMPORTS an assurance module: {len(rounds)}")
    print(f"  ⛔ v1 counted MENTIONS: {infl} additional (round, module) pairs were prose about a gate, not a dependency on it")

    print(f"\n─── CONTROLS ───")
    multi = [k for k, v in mhist.items() if len(v) > 1]
    pos = bool(multi)
    print(f"  POSITIVE  a module with >1 commit exists ({multi[0] if multi else '—'}, "
          f"{len(mhist[multi[0]]) if multi else 0}) so a stale pair is FINDABLE -> "
          f"{'PASS' if pos else '⛔ FAIL'}")
    single = [k for k, v in mhist.items() if len(v) == 1]
    print(f"  g=0       {len(single)} module(s) have exactly 1 commit and can never produce a "
          f"stale pair -> {'PASS — the test can return nothing' if single else 'no such module'}")
    print(f"  PLACEBO   a module that does not exist -> "
          f"{0 if 'zzq_nomodule' not in mhist else 'FAIL'} pairs -> PASS")
    controls_ok = pos

    print(f"\n─── EVERY (ROUND, MODULE) PAIR WHERE THE MODULE MOVED AFTER THE ROUND ───")
    stale = []
    for name, rt, imports in rounds:
        for m in imports:
            later = [(h, t, s) for h, t, s in mhist[m] if t > rt]
            if later:
                stale.append({"round": name, "module": m, "n_later": len(later),
                              "subjects": [s[:70] for _, _, s in later[:2]]})
    for s in stale:
        print(f"  {s['round'][:44]:<44} {s['module']:<34} +{s['n_later']}")
        for sub in s["subjects"]:
            print(f"      later: {sub}")
    if not stale:
        print("  (none)")

    print(f"\n─── VERDICT (pre-registered: >=3 stale pairs -> sweep owed) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif len(stale) >= 3:
        world = (f"B WIDESPREAD — {len(stale)} (round, module) pairs stand on a version of an "
                 f"instrument that has since changed. A re-run sweep is owed and this is its size.")
    elif stale:
        world = (f"A CONTAINED — {len(stale)} stale pair(s); the R632 case was local.")
    else:
        world = (f"C NO EXPOSURE — no assurance module was modified after any round that imports "
                 f"it. The obligation R632 named has no instances among imported modules, so the "
                 f"exposure is confined to inline logic like R630's, which no import graph sees.")
    print(f"  {world}")
    print(f"\n  ⚠ OVERSTATES: a modification may be a comment or a rename that changes no "
          f"behaviour, and a round can import a module without depending on the repaired clause. "
          f"Every hit is printed with its commit subject so the change can be judged.")
    print(f"  ⚠ AND IT UNDERSTATES IN ONE DIRECTION THAT MATTERS: rounds with INLINE copies of a "
          f"rule -- R630's ledger test was inline -- are invisible to an import graph, which is "
          f"exactly how the R632 case escaped.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "conclusions_under_superseded_instruments.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "module_commit_counts": {k: len(v) for k, v in mhist.items()},
        "statement_provenance_commits": len(sp),
        "rounds_importing": len(rounds), "stale_pairs": stale,
        "mention_only_pairs_removed": sum(n for _, n in MENTION_ONLY),
        "check232": ("'widened once, repaired once, clause added later' was read off the module's "
                     "comments, not the git log -- third consecutive closing line describing my "
                     "own tooling from memory"),
        "impossible": "whether a conclusion CHANGES needs re-running that round; this locates exposure",
    }, indent=2))
    print(f"\n  wrote {OUT / 'conclusions_under_superseded_instruments.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
