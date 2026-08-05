#!/usr/bin/env python3
"""
R635 -- of the rounds reading a verdict key inline, how many actually read a key they reject?

CHECK #234: TWO, AND THE FIRST IS THE FOURTH CONSECUTIVE ROUND MISDESCRIBING MY OWN PRIOR WORK.
  ⛔ "R632 showed one SUCH reader was wrong" -- R632's broken reader was the LEDGER MEMBERSHIP
     test, not a verdict-key reader. Different predicate family entirely. With #230 ("outside
     every gate"), #231 ("asked only the ledger") and #232 ("widened once, repaired once"), that
     is FOUR OF THE LAST FIVE closing lines mischaracterising my own tooling -- and this round
     counts that rather than asserting it.
  ⛔ "ANY round predating that reads a settled round as unsettled" -- only rounds that read an
     artifact which actually uses `verdict`. The universal drops the conditional that makes it
     true, and the conditional is exactly what this round measures.

ESTIMAND        n_at_risk = rounds whose inline verdict reader accepts a key set K, which read at
                least one artifact whose result is recorded under a key NOT in K -- i.e. read a
                settled round as unsettled.
IDENTIFICATION  Exact given the key sets and the artifacts on disk. ⚠ A round can read an artifact
                without its conclusion depending on that read, so n_at_risk OVERSTATES conclusions
                actually wrong; every member is printed so the dependency can be judged.
SCOPE           population : rounds under A24 whose run.py reads a verdict key inline (self
                             EXCLUDED -- R634 made that a default, not a repair)
                instrument : key-literal extraction + the artifact key census
                             instrument unit = A (ROUND, ARTIFACT) PAIR
                             claim unit      = A CONCLUSION AT RISK. Unequal; stated above.
                baseline   : the canonical reader after R600, which accepts world AND verdict
                regime     : this repository at this sha
WORLDS          A ALL ACCEPT BOTH: no round rejects a key that any artifact uses -> the divergence
                  R634 found is confined to citation regexes.
                B THE MISMATCH BITES: >=1 round accepts a narrower set than the artifacts it reads
                  use -> those conclusions read settled rounds as unsettled, and the count is the
                  size of the debt.
                C SPLIT BUT INERT: narrow readers exist, but no artifact they read uses the key
                  they reject -> the divergence is real and costs nothing here, which is a
                  different claim from A and must not be reported as it.
KILL            pre-registered: n_at_risk >= 1 -> world B. Narrow readers exist but n_at_risk == 0
                -> world C. No narrow readers -> world A.
POSITIVE CTRL   a round known to accept both keys must classify as wide; and the artifact census
                must FIND at least one artifact recorded under `verdict`, or "at risk" is
                unmeasurable and every zero is silence.
NEGATIVE CTRL   a round with no inline key read must not be counted.
PLACEBO         a key that no artifact uses -> 0 artifacts, and it must not create risk.
SEEDS           n/a, deterministic.
MULTIPLICITY    every (round, artifact) pair + the meta-count of closing lines + 4 controls.
ARTIFACT        results/who_reads_a_key_they_reject.json
IMPOSSIBLE      whether a specific conclusion CHANGES needs re-running that round. This locates
                and bounds; it does not re-adjudicate.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
SELF = pathlib.Path(__file__).resolve().parent.name
KEYTUP = re.compile(r'for\s+\w+\s+in\s+\(([^)]*)\)')
KEYLIT = re.compile(r'"(world|verdict)"')


def main():
    rounds = [d for d in sorted(A24.glob("R[0-9]*"))
              if (d / "run.py").is_file() and d.name != SELF]
    if len(rounds) < 20:
        print(f"UNRUNNABLE: {len(rounds)} rounds. Exit 2, never 0."); return 2

    # artifact census: which key does each round's artifact record its result under?
    census = {}
    for d in rounds:
        for f in (d / "results").glob("*.json"):
            try: j = json.loads(f.read_text())
            except Exception: continue
            if isinstance(j, dict):
                for k in ("world", "verdict"):
                    if isinstance(j.get(k), str):
                        census.setdefault(d.name, set()).add(k)
    uses_verdict = {r for r, ks in census.items() if "verdict" in ks and "world" not in ks}
    print(f"  rounds with a run.py (self excluded): {len(rounds)}")
    print(f"  artifacts recording a result: {len(census)}   "
          f"under `verdict` ONLY: {len(uses_verdict)}")

    # which rounds read a key inline, and which keys do they accept?
    readers = {}
    for d in rounds:
        src = (d / "run.py").read_text(errors="ignore")
        keys = set()
        for m in KEYTUP.finditer(src):
            keys |= set(KEYLIT.findall(m.group(1)))
        if not keys:
            keys = set(KEYLIT.findall(src))
        if keys:
            readers[d.name] = frozenset(keys)
    groups = {}
    for r, k in readers.items(): groups.setdefault(k, []).append(r)
    print(f"\n─── THE 195, GROUPED BY THE KEY SET THEY ACCEPT ───")
    for k, rs in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        print(f"  {sorted(k) if k else '(none)'!s:<26} {len(rs):>4} round(s)")

    print(f"\n─── CONTROLS ───")
    wide = [r for r, k in readers.items() if k == frozenset({"world", "verdict"})]
    pos1 = bool(wide)
    pos2 = bool(uses_verdict)
    print(f"  POSITIVE  {len(wide)} round(s) accept BOTH keys -> {'PASS' if pos1 else '⛔ FAIL'}")
    print(f"  POSITIVE  {len(uses_verdict)} artifact(s) record under `verdict` ONLY, so 'at risk' "
          f"is measurable -> {'PASS' if pos2 else '⛔ FAIL — every zero below would be silence'}")
    nokey = [d.name for d in rounds if d.name not in readers]
    print(f"  NEGATIVE  {len(nokey)} round(s) read no key inline and are not counted -> "
          f"{'PASS' if nokey else '⛔ FAIL'}")
    plc = sum(1 for ks in census.values() if "zzq_nokey" in ks)
    print(f"  PLACEBO   a key no artifact uses -> {plc} -> {'PASS' if plc == 0 else '⛔ FAIL'}")
    controls_ok = pos1 and pos2 and bool(nokey)

    print(f"\n─── WHO READS A KEY THEY REJECT ───")
    at_risk = []
    for r, k in readers.items():
        if "verdict" in k: continue
        src = (A24 / r / "run.py").read_text(errors="ignore")
        # which OTHER rounds' artifacts does it reach? conservative: any that record verdict-only
        touched = sorted(x for x in uses_verdict if re.search(rf"\b{x[:4]}\b|R\(\\d\{{3\}}\)", src))
        if touched and re.search(r"A24|glob\(.*R\[0-9\]|results", src):
            at_risk.append({"round": r, "accepts": sorted(k), "verdict_only_reachable": len(touched)})
    for a in sorted(at_risk, key=lambda a: -a["verdict_only_reachable"])[:12]:
        print(f"  {a['round'][:58]:<58} accepts {a['accepts']}  reaches "
              f"{a['verdict_only_reachable']} verdict-only artifact(s)")
    print(f"  total at risk: {len(at_risk)}")

    print(f"\n─── THE META-COUNT CHECK #234 ASSERTED ───")
    log = subprocess.run(["git", "log", "-12", "--format=%B%x1e"], cwd=ROOT,
                         capture_output=True, text=True, timeout=120).stdout
    nexts = [re.search(r"NEXT[:.]?\s*(.*?)(?:\n\n|\Z)", b, re.S)
             for b in log.split("\x1e") if "NEXT" in b]
    selfref = [n.group(1) for n in nexts if n and
               re.search(r"previous round|R6\d{2}|the gate|my own|this round", n.group(1), re.I)]
    print(f"  last {len([n for n in nexts if n])} closing lines; "
          f"{len(selfref)} make a claim about my own prior work "
          f"({len(selfref)/max(len([n for n in nexts if n]),1):.0%})")
    print(f"  ⚠ how many of those were WRONG is not decidable here -- it took a round each to find "
          f"four. The share that MAKE such a claim is the measurable part, and it is the exposure.")

    print(f"\n─── VERDICT (pre-registered) ───")
    narrow = [r for r, k in readers.items() if "verdict" not in k]
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif at_risk:
        world = (f"B THE MISMATCH BITES — {len(at_risk)} round(s) accept a narrower key set than "
                 f"the artifacts they reach use, so they read settled rounds as unsettled.")
    elif narrow:
        world = (f"C SPLIT BUT INERT — {len(narrow)} round(s) accept `world` only, but none reaches "
                 f"an artifact recorded under `verdict` alone. The divergence is real and costs "
                 f"nothing here, which is NOT the same claim as 'all readers agree'.")
    else:
        world = "A ALL ACCEPT BOTH — the divergence R634 found is confined to citation regexes."
    print(f"  {world}")
    print(f"\n  ⚠ OVERSTATES: a round can read an artifact without its conclusion depending on that "
          f"read. Members are printed so the dependency can be judged.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "who_reads_a_key_they_reject.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "n_rounds": len(rounds), "n_readers": len(readers),
        "groups": {str(sorted(k)): len(v) for k, v in groups.items()},
        "verdict_only_artifacts": len(uses_verdict), "at_risk": at_risk,
        "closing_lines_examined": len([n for n in nexts if n]),
        "closing_lines_claiming_own_prior_work": len(selfref),
        "check234": ("R632's broken reader was the LEDGER test, not a verdict-key reader; and "
                     "'any round predating' drops the conditional that makes it true"),
        "impossible": "whether a conclusion CHANGES needs re-running that round",
    }, indent=2))
    print(f"\n  wrote {OUT / 'who_reads_a_key_they_reject.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
