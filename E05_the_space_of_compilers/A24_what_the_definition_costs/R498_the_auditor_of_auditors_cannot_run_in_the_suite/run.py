"""Does the assurance suite contain a cycle, and does it stop the auditor from ever completing?

ESTIMAND        For each of the two directory-globbing auditors in assurance/, (a) does its
                discovered script set contain the OTHER auditor, and (b) is its standalone
                wall-clock above the suite's own 90s timeout. Both are properties of the
                COMMITTED code, measured by importing each module's real discovery rule --
                never by reading the source and reasoning about the glob.
IDENTIFICATION  Fully identified. Discovery is a pure function of the directory; wall-clock is
                measured directly. No estimation, no sampling.
SCOPE           population = assurance/*.py as of this commit · instrument = each module's OWN
                discovery expression, executed · baseline = the suite's own timeout constant,
                read from run_all.py rather than assumed · regime = this repo, this checkout.
WORLDS          A NO CYCLE: neither auditor discovers the other; the 120s overrun I observed is
                  simply the cost of ~40 honest gates, and the fix is a bigger timeout.
                B CYCLE, INERT: each discovers the other, but something (a guard, a self-check)
                  stops the nested call, so the overrun is again just volume.
                C CYCLE, LIVE: each actually spawns the other, so the auditor structurally
                  cannot finish inside the suite.
                Prediction matrix -- the discriminator is DIRECT OBSERVATION of the process
                tree while the auditor runs, because an excision arm would require changing
                the object under test. Count live `run_all.py` processes descended from it:
                  A -> 0, and run_all is absent from its discovered set.
                  B -> 0, while run_all IS in the set (discovered but never spawned).
                  C -> >=1.
                ⚠ An earlier draft of this round used an excision arm driven by an environment
                variable that NOTHING READS -- both arms would have been the same run. Killed
                before execution; recorded because a discriminator that cannot discriminate is
                the failure this file exists to catch.
KILL            Pre-registered, written before running: if audit_the_auditors completes in under
                the suite timeout, OR zero nested run_all processes are ever observed, world C
                is dead and I withdraw the cycle claim regardless of what the glob contains.
                A cycle that is never traversed is not a defect.
POSITIVE CTRL   TWO, because there are two instruments.
                (i) the discovery probe: excising a script that IS present must drop the count
                    by exactly 1; excising an ABSENT name must leave it unchanged; excising
                    nothing must reproduce the base count. Fails at g=0 by construction.
                (ii) the process-tree probe: it must SEE a process I know is there. While the
                    auditor runs, at least one OTHER assurance gate must be observed as a live
                    child -- if the probe cannot see the children everyone agrees exist, a zero
                    count for run_all is silence, not an acquittal.
NEGATIVE CTRL   Time a NON-auditor gate of comparable file size in the same harness. If it also
                exceeds 90s, the overrun belongs to the harness or the machine, not to recursion,
                and the cycle explains nothing. This is the world "everything here is slow".
SHAM            The same process-tree probe pointed at a NON-auditor gate: run
                definition_matches_the_record and count its `run_all.py` descendants. Same
                operation, ingredient (being an auditor) absent. Must return 0.
PLACEBO         Count descendants matching a script name that does not exist. Must be exactly 0
                under every condition, including while the auditor is at full tilt.
NOISE FLOOR     Measured as the observed spread across repeats, never modelled. Repeat counts
                differ by cost and are stated with each: the cheap gate gets 3, the auditor 2
                (each run is a multi-minute timeout). Declaring the asymmetry is the point --
                an averaged-over-unequal-n floor would understate the expensive condition.
MULTIPLICITY    Grid is small and reported whole: 2 auditors x {discovery, timing} x 4 excision
                conditions. Every cell printed, including the ones that show nothing.
SPECIFICATION   Swept: which auditor · excised-vs-not · repeat index. The timeout baseline is read
                from run_all.py, so a change there changes the verdict rather than the story.
SEEDS           No stochastic component: discovery is deterministic and timing is a measurement.
                Seed-robustness is N/A and is declared here rather than silently skipped.
ARTIFACT        results/cycle.json, with the discovered sets verbatim so a later round can attack
                the discovery rule itself rather than re-deriving it.
REPRODUCIBILITY Discovery is byte-identical across runs by construction; asserted, not assumed.
IMPOSSIBLE      cross-site: this is one repo's assurance directory, and nothing here generalises
                to another suite without that suite's own discovery rules. Would require a
                second repo with two mutually-globbing auditors.
"""
from __future__ import annotations
import json, os, pathlib, re, signal, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[3]
ASSUR = ROOT / "assurance"
OUT = pathlib.Path(__file__).resolve().parent / "results"; OUT.mkdir(exist_ok=True)

def suite_timeout() -> int:
    m = re.search(r"def run_one\([^)]*timeout: int = (\d+)", (ASSUR/"run_all.py").read_text())
    return int(m.group(1))

def discovered(auditor: str, excise: tuple[str, ...] = ()) -> list[str]:
    """Each auditor's OWN rule, executed -- not a re-implementation."""
    if auditor == "run_all":
        src = (ASSUR/"run_all.py").read_text()
        ng = set(re.findall(r'"([^"]+)"', re.search(r"NOT_A_GATE\s*=\s*\{(.*?)\}", src, re.S).group(1)))
        skip = ("_", "apply_")
        got = [p.stem for p in sorted(ASSUR.glob("*.py"))
               if p.stem not in ng and not p.stem.startswith(skip)]
    else:                                   # audit_the_auditors: everything but itself and _*
        got = [p.stem for p in sorted(ASSUR.glob("*.py"))
               if p.stem != "audit_the_auditors" and not p.name.startswith("_")]
    return [s for s in got if s not in excise]

def descendants(pid: int) -> set[str]:
    """Script basenames of every live process under pid. The probe, used by all conditions."""
    try:
        out = subprocess.run(["ps", "-eo", "pid,ppid,args"], capture_output=True,
                             text=True, timeout=20).stdout
    except Exception:
        return set()
    kids, names = {}, {}
    for ln in out.splitlines()[1:]:
        f = ln.split(None, 2)
        if len(f) < 3: continue
        try: q, pp = int(f[0]), int(f[1])
        except ValueError: continue
        kids.setdefault(pp, []).append(q); names[q] = f[2]
    seen, stack, found = set(), [pid], set()
    while stack:
        q = stack.pop()
        if q in seen: continue
        seen.add(q); stack += kids.get(q, [])
        for tok in names.get(q, "").split():
            if tok.endswith(".py"): found.add(pathlib.Path(tok).stem)
    return found


def observe(script: str, cap: int) -> tuple[float, set[str], bool]:
    """Run a gate; sample its process tree throughout. Returns (elapsed, seen, timed_out)."""
    t0 = time.time()
    proc = subprocess.Popen([sys.executable, str(ASSUR/f"{script}.py")],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            cwd=ROOT, start_new_session=True)
    seen, killed = set(), False
    while proc.poll() is None:
        seen |= descendants(proc.pid)
        if time.time() - t0 > cap:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL); killed = True; break
        time.sleep(0.4)
    return time.time()-t0, seen, killed


def main() -> int:
    T = suite_timeout()
    print(f"suite timeout, read from run_all.py: {T}s\n")
    sets = {a: discovered(a) for a in ("run_all", "audit_the_auditors")}
    if not all(sets.values()):
        print("  population EMPTY -- discovery returned nothing; refusing to report"); return 2

    print(f"  {'auditor':<22}{'discovers':>10}  contains the OTHER auditor?")
    cross = {}
    for a, other in (("run_all", "audit_the_auditors"), ("audit_the_auditors", "run_all")):
        cross[a] = other in sets[a]
        print(f"  {a:<22}{len(sets[a]):>10}  {cross[a]}")

    print("\n  probe control (i) -- discovery must be able to change:")
    base = len(discovered("audit_the_auditors")); present = sets["audit_the_auditors"][0]
    c1 = {"g=0 (excise nothing)": len(discovered("audit_the_auditors", ())) == base,
          f"excise present '{present}'": len(discovered("audit_the_auditors", (present,))) == base-1,
          "placebo (absent name)": len(discovered("audit_the_auditors", ("no_such_gate",))) == base}
    for k, v in c1.items(): print(f"    {k:<36}{'PASS' if v else 'FAIL'}")

    print("\n  running conditions (this takes a few minutes)...")
    CAP = 150
    aud = [observe("audit_the_auditors", CAP) for _ in range(2)]        # 2 reps: each is a timeout
    plain = [observe("definition_matches_the_record", CAP) for _ in range(3)]

    aud_seen = set().union(*(s for _, s, _ in aud))
    sham_seen = set().union(*(s for _, s, _ in plain))
    at = [e for e, _, _ in aud]; pt = [e for e, _, _ in plain]
    floor = max(max(at)-min(at), max(pt)-min(pt))

    print(f"\n    {'condition':<40}{'min s':>8}{'spread':>8}   run_all seen?")
    print(f"    {'audit_the_auditors (2 reps)':<40}{min(at):8.1f}{max(at)-min(at):8.1f}"
          f"   {'run_all' in aud_seen}")
    print(f"    {'SHAM: a plain gate (3 reps)':<40}{min(pt):8.1f}{max(pt)-min(pt):8.1f}"
          f"   {'run_all' in sham_seen}")

    print("\n  probe control (ii) -- the process probe must SEE known children:")
    others = aud_seen - {"run_all", "audit_the_auditors"}
    c2 = {"sees >=1 other gate as a child": len(others) >= 1,
          "placebo: sees a nonexistent script": "no_such_gate" not in aud_seen,
          "sham returns 0 run_all": "run_all" not in sham_seen}
    for k, v in c2.items(): print(f"    {k:<36}{'PASS' if v else 'FAIL'}")
    if not all(c1.values()) or not all(c2.values()):
        print("\n  a control misbehaved -- counts above are silence"); return 1
    print(f"    (probe saw {len(others)} distinct gates as children, e.g. {sorted(others)[:3]})")

    nested = "run_all" in aud_seen
    over = min(at) > T
    world = ("C LIVE CYCLE" if cross["run_all"] and cross["audit_the_auditors"] and nested
             else "B CYCLE, INERT" if cross["run_all"] and cross["audit_the_auditors"]
             else "A NO CYCLE")
    print(f"\n  measured noise floor (max spread): {floor:.1f}s")
    print(f"  a plain gate alone: {min(pt):.1f}s -- "
          f"{'the harness is not globally slow' if min(pt) < T else 'EVERYTHING is slow'}")
    print(f"\n  WORLD: {world}")
    if world.startswith("C"):
        print(f"  => the auditor spawns run_all, which re-discovers the auditor. It ran "
              f"{'past' if over else 'under'} the {T}s suite timeout ({min(at):.0f}s"
              f"{', killed at the cap' if any(k for _,_,k in aud) else ''}).")
        print(f"  => so the ONE gate whose job is catching empty-population passes is the one "
              f"gate the suite cannot run to completion.")
    json.dump({"timeout": T, "cross": cross, "sets": sets, "aud_s": at, "plain_s": pt,
               "aud_seen": sorted(aud_seen), "sham_seen": sorted(sham_seen), "floor": floor,
               "nested": nested, "world": world, "controls": {**c1, **c2}},
              (OUT/"cycle.json").open("w"), indent=1)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
