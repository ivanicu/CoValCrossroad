"""R317 — R315 measured `run.py` and said "rounds". What does the real population say?

R315 reported "25 of 278 probed rounds (9.0%) cannot resolve their inputs". Its glob is
`E*/A*/R*/run.py`. There are **341** `.py` files directly in round directories, of which 302 are
`run.py` — so **39 files, 11.4% of the population, were never asked**, and R316 found 14 stale
paths in 8 of them. `realstat §4 · a positive control asks whether the instrument can SEE, never
whether what it sees is the thing the sentence is about`: the instrument's unit was `file named
run.py`, the claim's unit was `round`, and those were never required to be equal.

The 39 are not incidental. Seven are `independent_A.py` and seven are `independent_B.py` — the
TRIPLE-BLIND implementations that `realstat §2.5` calls the only evidence surviving a framing
error, and the strongest form this site can produce. The layer the campaign leans on hardest for
independence is the layer its own runnability audit excluded by construction.

ESTIMAND      the share of executable python in round directories that cannot resolve its inputs,
              reported at BOTH units and with the unit named on every number: per FILE, and per
              ROUND (a round counts as broken if ANY of its files is). R315's headline conflated
              these; this round refuses to print either without its label.
IDENTIFICATION exact for BROKEN (a read-open inside the repo, outside library/cache territory,
              resolving to a nonexistent path). NOT identified for "works" — REACHED-WRITE means
              inputs resolved, not that the file would finish or finish correctly. TIMEOUT and
              SKIPPED-GPU are UNVERIFIED and are never folded into `intact`.
SCOPE         population every `E*/A*/R*/*.py` at HEAD · instrument R315's probe (`sys.
              addaudithook` on `open`) in a detached git worktree · 60 s wall clock · no GPU,
              no network.
WORLDS        W-SUBSET     the extra 39 files break at about the same rate as run.py -> R315's
                           RATE was right and only its noun was wrong.
              W-WORSE      the extra files break at a higher rate -> non-run.py is systematically
                           less maintained, which is what a file nothing ever executes looks
                           like, and R315 understated the problem as well as mislabelling it.
              W-BETTER     they break less -> the extra population is mostly inert libraries and
                           the scope error cost nothing but a word.
KILL          conditional on the controls:
                extra-file broken rate within [0.5x, 2x] of the run.py rate  -> W-SUBSET
                above 2x                                                     -> W-WORSE
                below 0.5x                                                   -> W-BETTER
              The bracket is pre-registered and wide on purpose: with 39 files a rate is coarse,
              and a tighter band would be a precision this design does not have.
POSITIVE CTRL THE EXACT-SUBSET CONTROL, and it is what makes the comparison readable. Filtering
              this sweep's results to `run.py` must reproduce the concurrent run.py-only sweep
              (E) round for round. If it does not, the two sweeps are not measuring the same
              thing and the extra files cannot be compared against them. Plus R315's synthetic
              controls: a planted missing read must be flagged, a present read must not.
              Fails at g=0: a synthetic file reading a file that EXISTS must come back not-broken.
NEGATIVE CTRL the probe writes NOTHING in the repo; `git status` byte-identical before and after,
              checked and reported. The sweep runs in a worktree because the audit hook does not
              reach subprocesses — measured the hard way in R315, which modified seven committed
              artifacts before that was fixed.
MULTIPLICITY  every file classified, every class counted, both units reported.
SEEDS         n/a; the churn floor measured in R316 (2 of 300, all TIMEOUT<->REACHED-WRITE,
              0 BROKEN) is the replicate and is quoted rather than re-measured.
ARTIFACT      results/population.json with source hash and the full per-file table.
IMPOSSIBLE    proving any file CORRECT by running it, and probing the 22 GPU-touching files,
              which are excluded by the pueue rule and counted separately as UNVERIFIED.
"""
import hashlib, json, os, pathlib, subprocess, sys, tempfile  # noqa: E401
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

LIVE = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(LIVE / "assurance"))
from _isolated import ensure_worktree                                        # noqa: E402

# ⚠ THE REVISION IS A PARAMETER, and it has to be. The first run of this round swept HEAD and
# reported "0 of 37 non-run.py files broken" against "6 of 279 run.py" -- and read it as the extra
# population being healthier. It is not evidence of that at all: the previous commit repaired 14
# stale sites in 8 of those very files, so the sweep measured a population I had ALREADY FIXED.
# The pre-registered worlds (W-SUBSET / W-WORSE / W-BETTER) are all about the PRE-repair rate, and
# HEAD cannot answer any of them. That is `the estimand was defined on a population the analyst
# had already changed`, and the tell is that the flattering number arrived immediately after the
# work that would produce it. git still holds the pre-repair tree, so the comparison is
# recoverable rather than lost: sweep 9f33bf2 (the last commit before the resolver) for the
# world-separating number, and HEAD for the repair's effect.
REV = os.environ.get("R317_REV", "HEAD")
ROOT = ensure_worktree(REV)
# ensure_worktree() returns an EXISTING worktree untouched, so it does not honour `rev` when the
# worktree is already there -- and a worktree left at an earlier HEAD measures the past, which
# cost R315 a whole sweep. Forced here rather than in the shared harness, because R315 and R316
# depend on that harness and this is not the round to change what they run on.
_sha = subprocess.run(["git", "rev-parse", REV], cwd=str(LIVE),
                      capture_output=True, text=True).stdout.strip()
subprocess.run(["git", "checkout", "--detach", "-f", _sha], cwd=str(ROOT), capture_output=True)
_at = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT),
                     capture_output=True, text=True).stdout.strip()
assert _at == _sha, f"worktree is at {_at[:8]}, asked for {REV} = {_sha[:8]}"
sys.path.insert(0, str(LIVE / "assurance"))
from _isolated import _link_untracked_inputs                                 # noqa: E402
_link_untracked_inputs()
PROBE = (LIVE / "E05_the_space_of_compilers/A24_what_the_definition_costs"
         / "R315_how_many_rounds_can_still_run" / "probe.py")
PY = LIVE / ".venv" / "bin" / "python"
SCRATCH = pathlib.Path("/tmp/claude-1000/-home-ivan/"
                       "7d277876-c2fd-4a27-9b05-652b391121ff/scratchpad")
TIMEOUT = 60
CLASS = {0: "COMPLETED", 3: "BROKEN-INPUT", 4: "REACHED-WRITE", 1: "OTHER-ERROR",
         124: "TIMEOUT"}
GPUMARK = ("import torch", "device_map", "cuda", "AutoModelForCausalLM", "vllm")


def probe(script, timeout=TIMEOUT):
    try:
        p = subprocess.run([str(PY), str(PROBE), str(ROOT), str(script)],
                           capture_output=True, timeout=timeout, cwd=str(script.parent))
        miss = None
        for ln in p.stderr.decode("utf8", "replace").splitlines():
            if ln.startswith("__PROBE__"):
                m = ln.split("missing=", 1)[1].split(" wrote=")[0]
                miss = None if m == "None" else m
        return p.returncode, miss
    except subprocess.TimeoutExpired:
        return 124, None


def main():
    if not PROBE.exists():
        print("  UNRUNNABLE: R315's probe absent."); return 2
    before = subprocess.run(["git", "status", "--porcelain"], cwd=str(LIVE),
                            capture_output=True).stdout

    files = sorted(p for p in ROOT.glob("E*/A*/R*/*.py"))
    if not files:
        print("  REFUSING: examined 0 files."); return 2
    runpy_n = sum(1 for f in files if f.name == "run.py")
    print(f"  population {len(files)} .py files in round directories "
          f"({runpy_n} run.py + {len(files) - runpy_n} others)")
    print(f"  worktree {ROOT}\n")

    print("  POSITIVE CONTROLS (synthetic, before anything is believed)")
    with tempfile.TemporaryDirectory() as tmp:
        def syn(missing):
            tgt = (ROOT / "no_such_input_9f3a.npz") if missing else (ROOT / "README.md")
            f = pathlib.Path(tmp) / (f"syn_{missing}.py")
            f.write_text(f"import pathlib\nprint(open(pathlib.Path({str(tgt)!r}),'rb').read(8))\n")
            return f
        rc_m, _ = probe(syn(True), 30)
        rc_p, _ = probe(syn(False), 30)
    ok_syn = (rc_m == 3) and (rc_p == 0)
    print(f"    planted MISSING read -> {CLASS.get(rc_m, rc_m):<14} want BROKEN-INPUT")
    print(f"    g=0 PRESENT read     -> {CLASS.get(rc_p, rc_p):<14} want COMPLETED")
    print(f"    -> synthetic controls {'PASS' if ok_syn else 'FAIL'}")

    gpu = {f for f in files if any(m in f.read_text(errors="replace") for m in GPUMARK)}
    probed = [f for f in files if f not in gpu]
    print(f"\n  SWEEP  {len(probed)} files probed, {len(gpu)} excluded as GPU-touching\n")
    with ThreadPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(lambda f: probe(f), probed))

    table = []
    for f in gpu:
        rel = f.relative_to(ROOT)
        table.append(dict(file=str(rel), name=f.name, round=rel.parts[2].split("_")[0],
                          cls="SKIPPED-GPU", missing=None))
    for f, (rc, miss) in zip(probed, res):
        rel = f.relative_to(ROOT)
        table.append(dict(file=str(rel), name=f.name, round=rel.parts[2].split("_")[0],
                          cls=CLASS.get(rc, str(rc)),
                          missing=(str(pathlib.Path(miss).relative_to(ROOT)) if miss else None)))

    # ---- EXACT-SUBSET CONTROL against the concurrent run.py-only sweep -------------------------
    # ⚠ THE PARTNER MUST MATCH THE REVISION *AND* THE HARNESS. The first pre-repair run compared
    # against sweep E -- a POST-repair sweep -- and the control failed, correctly, for a reason it
    # could not name. And sweep A is not the partner either: A ran before `.venv` was added to the
    # isolation harness, so it reports 25 broken where this sweep reports 19, and the 6 are
    # exactly the .venv cohort. Neither differs from this sweep by noise; each differs by a
    # deliberate change. A subset control is only a control against a sweep that shares BOTH the
    # tree and the instrument, so the partner is selected by revision and the matched pre-repair
    # sweep (F) had to be run rather than substituted.
    PARTNER = {"HEAD": "sweep_E.json"}.get(REV, "sweep_F.json")
    e_path = SCRATCH / PARTNER
    subset_ok, subset_note = None, ("the matched run.py-only sweep is absent -- subset control "
                                    "NOT RUN, so the run.py-vs-rest comparison is UNVERIFIED")
    if e_path.exists():
        E = {t["path"] + "/run.py": t["cls"] for t in json.loads(e_path.read_text())["table"]}
        mine = {t["file"]: t["cls"] for t in table if t["name"] == "run.py"}
        common = set(E) & set(mine)
        disagree = [(k, E[k], mine[k]) for k in common if E[k] != mine[k]]
        # ⚠ A DISAGREEMENT INVOLVING `TIMEOUT` IS NOT A CONTRADICTION. TIMEOUT means the file was
        # cut off at 60 s -- the sweep did not find out what it would have been -- so it cannot
        # disagree with anything. The first criterion counted any difference as failure and
        # returned FAIL on 3 of 302, all three involving TIMEOUT, i.e. exactly the churn class
        # R316 measured at 2/300. `the control fails for its own reasons`: its expectation
        # ignored the noise floor its own campaign had already measured. What must hold is that
        # no disagreement has a DECIDED class on both sides.
        decided = [(k, a_, b_) for k, a_, b_ in disagree
                   if a_ != "TIMEOUT" and b_ != "TIMEOUT"]
        subset_ok = not decided
        subset_note = (f"{len(common)} run.py files in both sweeps, {len(disagree)} disagree "
                       f"({len(decided)} with a DECIDED class on both sides)")
        print(f"  POSITIVE  exact-subset vs {PARTNER} (matched revision + harness): {subset_note}")
        for k, a, b in disagree[:6]:
            print(f"    {pathlib.Path(k).parent.name:<44}{a} vs {b}")
        if disagree and not decided:
            print("    -> every disagreement involves TIMEOUT, which is `did not find out` and")
            print("       cannot contradict anything. Subset control PASSES.")
        elif decided:
            print("    ⚠ a disagreement with a decided class on both sides means the two sweeps")
            print("      are not the same measurement.")
    else:
        print(f"  POSITIVE  {subset_note}")

    # ---- the two units, never printed without their label --------------------------------------
    by_name = defaultdict(Counter)
    for t in table:
        by_name["run.py" if t["name"] == "run.py" else "other"][t["cls"]] += 1
    counts = Counter(t["cls"] for t in table)
    print(f"\n  {'class':<16}{'all':>6}{'run.py':>9}{'other':>8}")
    for c in ("BROKEN-INPUT", "REACHED-WRITE", "COMPLETED", "OTHER-ERROR", "TIMEOUT",
              "SKIPPED-GPU"):
        print(f"    {c:<14}{counts[c]:>6}{by_name['run.py'][c]:>9}{by_name['other'][c]:>8}")

    def rate(bucket):
        n = sum(bucket.values()) - bucket["SKIPPED-GPU"]
        return (bucket["BROKEN-INPUT"] / n, n) if n else (float("nan"), 0)
    r_run, n_run = rate(by_name["run.py"])
    r_oth, n_oth = rate(by_name["other"])
    ratio = (r_oth / r_run) if r_run > 0 else float("inf")
    print(f"\n  BROKEN RATE, and the UNIT is named on every one of them:")
    print(f"    per FILE, run.py only   {r_run:.1%}  ({by_name['run.py']['BROKEN-INPUT']} of {n_run})")
    print(f"    per FILE, everything else {r_oth:.1%}  ({by_name['other']['BROKEN-INPUT']} of {n_oth})")
    br_rounds = {t["round"] for t in table if t["cls"] == "BROKEN-INPUT"}
    all_rounds = {t["round"] for t in table}
    print(f"    per ROUND (any file broken) {len(br_rounds)/len(all_rounds):.1%}  "
          f"({len(br_rounds)} of {len(all_rounds)})")
    print(f"    ratio other/run.py       {ratio:.2f}x   at revision {REV}")
    if REV == "HEAD":
        print("    ⚠ AT HEAD THIS RATIO ANSWERS NOTHING THE ROUND ASKED. The 14 stale sites in")
        print("      8 non-run.py files were repaired one commit ago, so a 0% rate here is the")
        print("      repair, not the population. Re-run with R317_REV=9f33bf2 for the number the")
        print("      worlds are about.")

    tb = [t for t in table if t["name"].startswith("independent_")]
    tb_bro = [t for t in tb if t["cls"] == "BROKEN-INPUT"]
    print(f"\n  THE TRIPLE-BLIND LAYER specifically: {len(tb)} files, "
          f"{len(tb_bro)} BROKEN-INPUT, {Counter(t['cls'] for t in tb).most_common()}")

    after = subprocess.run(["git", "status", "--porcelain"], cwd=str(LIVE),
                           capture_output=True).stdout
    untouched = before == after
    print(f"\n  NEGATIVE  git status byte-identical before and after: {untouched}")

    # The world call needs the PRE-repair tree; at HEAD the estimand is not identified.
    identified = REV != "HEAD"
    ctrl = ok_syn and untouched and (subset_ok is True) and identified
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  synthetic={ok_syn}  wrote-nothing={untouched}  "
          f"exact-subset={subset_ok}  -> {'evaluate' if ctrl else 'UNVERIFIED'}")
    if not identified and ok_syn and untouched and subset_ok:
        world = "W-UNIDENTIFIED"
        print("  -> W-UNIDENTIFIED, and it is a design defect rather than a data limit. Every")
        print("     control passed and the counts are sound, but this sweep ran at HEAD, AFTER")
        print("     the commit that repaired 14 stale sites in 8 of the very files under test.")
        print("     The estimand was defined on a population I had already changed. The counts")
        print("     stand; the RATIO and the three worlds do not. Re-run at 9f33bf2.")
    elif not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the run.py-vs-rest comparison is not")
        print("     readable. The per-file counts above stand on their own, the RATIO does not.")
    elif ratio > 2.0:
        world = "W-WORSE"
        print(f"  -> W-WORSE. Non-run.py files break at {ratio:.2f}x the run.py rate. A file")
        print("     nothing ever executes is a file nothing ever checks, and R315 both")
        print("     mislabelled its unit and understated the problem.")
    elif ratio < 0.5:
        world = "W-BETTER"
        print(f"  -> W-BETTER. Non-run.py files break at {ratio:.2f}x the run.py rate; the extra")
        print("     population is mostly inert. The scope error cost a word, not a number.")
    else:
        world = "W-SUBSET"
        print(f"  -> W-SUBSET. Non-run.py breaks at {ratio:.2f}x the run.py rate, inside the")
        print("     pre-registered [0.5x, 2x] band. R315's RATE was about right and its NOUN")
        print("     was wrong -- which is still a correction, because every number it reported")
        print("     was per-file and every sentence said per-round.")
    print("  " + "=" * 78)

    # One artifact per REVISION. The first two runs of this round overwrote each other, so the
    # HEAD numbers survived only in a scratch log -- and a round whose two arms cannot both be
    # read from disk cannot be attacked on the comparison that is its whole point.
    o = SELF.parent / "results" / f"population_{REV.replace('/', '_')}.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_files=len(files), n_runpy=runpy_n, n_other=len(files) - runpy_n,
        counts=dict(counts), by_name={k: dict(v) for k, v in by_name.items()},
        broken_rate_runpy=r_run, broken_rate_other=r_oth, ratio=ratio,
        broken_rounds=sorted(br_rounds), n_rounds=len(all_rounds),
        triple_blind=dict(n=len(tb), broken=[t["file"] for t in tb_bro]),
        revision=REV, identified=bool(identified),
        synthetic_ok=bool(ok_syn), wrote_nothing=bool(untouched), subset_ok=subset_ok,
        subset_note=subset_note, table=table), indent=1))
    print(f"\n  artifact {o.relative_to(LIVE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
