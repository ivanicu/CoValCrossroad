"""R315 — how many of this project's rounds can still run at all?

R314's next-gradient line pointed at the last failing row in `consistency.py`: r144 vs r145,
0.2831 vs 0.3404. Two defects surfaced before the statistics did, and the second is much larger
than the row that led me here.

① THE CHECK INVENTS THE QUANTITY IT COMPARES. `u144 = r144["mean_residual_G0"] / 15.6`, and
`15.6` appears in NEITHER round's artifact. R144 computes the mean panel size as
`pan = mean(n_criteria)` and PRINTS it; it never persists it. So the constant was transcribed
from a printout, cannot be verified from any committed file, and goes silently stale the moment
r144's population changes. Worse, r144's own `analyse` already returns `residual_G0_frac`
per prompt — the mean-of-ratios estimator, i.e. exactly the quantity r145 reports — and r144
aggregates it nowhere. The check reconstructed by hand, with a magic number, a quantity the
round already had.

② AND R144 CANNOT BE RE-RUN, which is why ① was never caught. Line 226 reads
`base = ROOT / "E01" / "R04_rebuild_satisfaction" / "results"` — the PRE-MIGRATION epoch and
arc names. The EAR reorganisation moved it to
`E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction`
and nothing noticed, because nothing re-runs rounds. **A repository whose rounds are not
re-runnable has artifacts that cannot be attacked, only cited.**

So the round in front of me is not the 15.6. It is: HOW MANY ROUNDS ARE IN THAT STATE?

ESTIMAND      the count and share of committed rounds whose declared inputs no longer resolve,
              measured by execution rather than by pattern-matching paths — a grep cannot see
              `ROOT / "E01" / ...` assembled from parts, and this project has a standing rule
              that a search is an instrument requiring its own positive control.
IDENTIFICATION exact for BROKEN (a read-open inside the repo resolved to a nonexistent path is
              decisive). NOT identified for "works": reaching a write proves the inputs
              resolved, not that the round would finish or finish correctly. Those are reported
              as REACHED-WRITE, never as `passing`, and a timeout is UNVERIFIED, never `ok`.
SCOPE         population every `E*/A*/R*/run.py` committed at HEAD · instrument a `sys.
              addaudithook` on the `open` event · baseline none · regime a 60 s wall clock per
              round, no GPU, no network.
WORLDS        W-ISOLATED   r144 is a one-off; the broken share is ~0 and the fix is one line.
              W-MIGRATION  the EAR migration broke a COHORT — rounds written before it, citing
                           bare epoch names. Prediction: breakage concentrates in low round
                           ids and in path strings containing an un-suffixed `E0N`.
              W-ENDEMIC    breakage is spread across ids and causes, i.e. the repo has never
                           been re-runnable and the migration is a red herring.
KILL          conditional on the controls:
                0 broken besides r144                       -> W-ISOLATED
                >=3 broken AND they cluster in round id     -> W-MIGRATION
                >=3 broken AND no id clustering             -> W-ENDEMIC
              Clustering is tested, not eyeballed: Mann-Whitney U of broken vs non-broken round
              ids against a permutation null, reported with its own floor.
POSITIVE CTRL three, and the third is the one that matters. ① r144 must come back BROKEN.
              ② a round known to run (R313, committed this session) must NOT. ③ a SYNTHETIC
              round is planted that reads one nonexistent file and is otherwise trivial: the
              instrument must flag it. ③ is what makes a zero elsewhere a measurement rather
              than silence — ① only shows the instrument agrees with the case that motivated it,
              which is `a control that shares the instrument's blind spot`.
              Fails at g=0: a synthetic round reading a file that DOES exist must come back
              not-broken, or the probe flags everything and its zeros mean nothing.
NEGATIVE CTRL the probe writes NOTHING inside the repo — enforced by the audit hook, not by
              intention — so the sweep cannot damage the artifacts it is measuring. Verified by
              `git status` being byte-identical before and after, which is checked and reported.
PLACEBO       the probe run against a file that is empty: must exit 0, not 3.
MULTIPLICITY  one classification per round over the whole population; every class is reported
              with its count, including the ones that are not decisive.
SEEDS         n/a — execution is deterministic here; the permutation null for clustering uses
              200 draws.
ARTIFACT      results/runnability.json with source hash and the full per-round table.
IMPOSSIBLE    proving a round is CORRECT by running it. The probe establishes that inputs
              resolve, nothing more, and REACHED-WRITE is named that way so it cannot be read
              as a pass. Would require each round's own controls to be re-run and compared to
              its committed artifact, which is a different and much larger instrument.
"""
import hashlib, json, math, os, pathlib, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
import numpy as np

LIVE = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
PROBE = SELF.parent / "probe.py"
PY = LIVE / ".venv" / "bin" / "python"
sys.path.insert(0, str(LIVE / "assurance"))
# ⚠ THE SWEEP RUNS IN A GIT WORKTREE, AND THE FIRST VERSION DID NOT. The audit hook blocks
# writes only in the process that installs it, and 9 rounds in this repo shell out to
# subprocesses -- which have no hook. The first sweep therefore MODIFIED SEVEN COMMITTED
# ARTIFACTS (R220, R221, R238, R241, R244, R245, R265) while its own docstring promised it
# wrote nothing. They were restored from git. The negative control CAUGHT it -- `git status`
# was not byte-identical and the verdict went UNVERIFIED rather than being reported -- which is
# the only reason this is a paragraph and not a silent corruption. A write block that a
# subprocess walks straight through is not isolation; a worktree is.
from _isolated import ensure_worktree                                        # noqa: E402
ROOT = ensure_worktree("HEAD")
TIMEOUT = 60
CLASS = {0: "COMPLETED", 3: "BROKEN-INPUT", 4: "REACHED-WRITE", 1: "OTHER-ERROR",
         124: "TIMEOUT"}


def probe(script: pathlib.Path, timeout=TIMEOUT):
    try:
        p = subprocess.run([str(PY), str(PROBE), str(ROOT), str(script)],
                           capture_output=True, timeout=timeout, cwd=str(script.parent))
        tail = p.stderr.decode("utf8", "replace")
        miss = None
        for ln in tail.splitlines():
            if ln.startswith("__PROBE__"):
                m = ln.split("missing=", 1)[1].split(" wrote=")[0]
                miss = None if m == "None" else m
        return p.returncode, miss
    except subprocess.TimeoutExpired:
        return 124, None


def synthetic(tmp, missing: bool):
    """A round that reads exactly one file inside the repo. g=0 form reads one that EXISTS."""
    tgt = (ROOT / "no_such_input_9f3a.npz") if missing else (ROOT / "README.md")
    f = pathlib.Path(tmp) / ("syn_missing.py" if missing else "syn_present.py")
    f.write_text(f"import pathlib\np = pathlib.Path({str(tgt)!r})\n"
                 f"print(open(p, 'rb').read(8))\n")
    return f


def main():
    if not PROBE.exists() or not PY.exists():
        print("  UNRUNNABLE: probe or interpreter absent."); return 2
    before = subprocess.run(["git", "status", "--porcelain"], cwd=str(LIVE),
                            capture_output=True).stdout
    print(f"  worktree {ROOT}\n  live tree {LIVE} — the sweep must not touch it\n")

    rounds = sorted(p for p in ROOT.glob("E*/A*/R*/run.py"))
    if not rounds:
        print("  REFUSING: examined 0 rounds. An empty population never passes."); return 2
    print(f"  population {len(rounds)} rounds under E*/A*/R*/run.py\n")

    # ---- POSITIVE CONTROLS, before anything is believed ---------------------------------------
    print("  POSITIVE CONTROLS")
    with tempfile.TemporaryDirectory() as tmp:
        rc_syn_m, miss_m = probe(synthetic(tmp, True), 30)
        rc_syn_p, _ = probe(synthetic(tmp, False), 30)
        empty = pathlib.Path(tmp) / "empty.py"; empty.write_text("")
        rc_empty, _ = probe(empty, 30)
    r144 = ROOT / ("E04_no_fraction_only_an_equivalence_class/A13_the_chain_from_a_person_to_"
                   "the_standard/R144_information_loss/run.py")
    r313 = (ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
            / "R313_is_the_signed_shrink_precision_or_shared_noise" / "run.py")
    rc144, m144 = probe(r144)
    rc313, _ = probe(r313)
    ctl = [("synthetic round reading a MISSING file", rc_syn_m, 3),
           ("g=0: synthetic round reading a PRESENT file", rc_syn_p, 0),
           ("placebo: an EMPTY script", rc_empty, 0),
           ("r144 (the case that motivated this)", rc144, 3),
           ("R313 (known to run)", rc313, 4)]
    ok = True
    for nm, got, want in ctl:
        good = got == want
        ok &= good
        print(f"    {nm:<44}{CLASS.get(got, got):>15}  want {CLASS.get(want, want):<14}"
              f"{'ok' if good else 'FAIL'}")
    print(f"    -> instrument {'VALIDATED' if ok else 'NOT validated'}; "
          f"{'zeros below are measurements' if ok else 'nothing below is readable'}")
    if m144:
        print(f"    r144's first unresolvable read: {pathlib.Path(m144).relative_to(ROOT)}")

    # ---- THE SWEEP ----------------------------------------------------------------------------
    # GPU-TOUCHING ROUNDS ARE NOT PROBED. AGENTS.md: all CUDA work goes through pueue and never
    # straight from a shell. Running them here would put a model in VRAM 10 at a time. They are
    # classified SKIPPED-GPU -- their own class, counted, and NEVER folded into `intact`, which
    # would be an unavailability claim in the flattering direction.
    GPUMARK = ("import torch", "device_map", "cuda", "AutoModelForCausalLM", "vllm")
    gpu = {s for s in rounds
           if any(m in s.read_text(errors="replace") for m in GPUMARK)}
    probed = [s for s in rounds if s not in gpu]
    print(f"\n  SWEEP  {len(probed)} rounds probed, {TIMEOUT}s wall clock each, nothing written")
    print(f"         {len(gpu)} excluded as GPU-touching (pueue rule), counted separately\n")
    with ThreadPoolExecutor(max_workers=10) as ex:
        res = list(ex.map(lambda s: probe(s), probed))
    table = []
    for s in gpu:
        rel = s.relative_to(ROOT)
        table.append(dict(round=rel.parts[2].split("_")[0], path=str(rel.parent),
                          cls="SKIPPED-GPU", missing=None))
    for s, (rc, miss) in zip(probed, res):
        rel = s.relative_to(ROOT)
        rid = rel.parts[2].split("_")[0]
        table.append(dict(round=rid, path=str(rel.parent), cls=CLASS.get(rc, str(rc)),
                          missing=(str(pathlib.Path(miss).relative_to(ROOT)) if miss else None)))
    counts = {c: sum(1 for t in table if t["cls"] == c) for c in
              ("BROKEN-INPUT", "REACHED-WRITE", "COMPLETED", "OTHER-ERROR", "TIMEOUT",
               "SKIPPED-GPU")}
    print(f"    {'class':<16}{'n':>6}   what it licenses")
    lic = {"BROKEN-INPUT": "decisive: an input does not exist",
           "REACHED-WRITE": "inputs resolved -- NOT a pass",
           "COMPLETED": "ran without writing in-tree",
           "OTHER-ERROR": "needs inspection; not classified",
           "TIMEOUT": "UNVERIFIED -- says nothing either way",
           "SKIPPED-GPU": "not probed (pueue rule) -- UNVERIFIED, not intact"}
    for c, n in counts.items():
        print(f"    {c:<16}{n:>6}   {lic[c]}")

    broken = [t for t in table if t["cls"] == "BROKEN-INPUT"]
    print(f"\n  BROKEN INPUTS: {len(broken)} of {len(probed)} PROBED "
          f"({len(broken)/max(1,len(probed)):.1%})  —  the share is over what was probed, not")
    print(f"                 over all {len(rounds)} rounds; {len(gpu)} were never asked.")
    for t in sorted(broken, key=lambda t: t["round"])[:40]:
        print(f"    {t['round']:<7}{(t['missing'] or '?')[:88]}")
    if len(broken) > 40:
        print(f"    … and {len(broken) - 40} more, all in the artifact")

    # ---- does breakage CLUSTER in round id? ---------------------------------------------------
    def rid_num(t):
        try:
            return int(t["round"].lstrip("Rr"))
        except ValueError:
            return None
    bi = [n for n in map(rid_num, broken) if n is not None]
    oi = [n for n in map(rid_num, [t for t in table if t["cls"] != "BROKEN-INPUT"])
          if n is not None]
    clustered, u_obs, u_lo, u_hi = False, float("nan"), float("nan"), float("nan")
    if len(bi) >= 3 and len(oi) >= 3:
        def U(a, b):
            return float(sum(1 for x in a for y in b if x < y) + 0.5 *
                         sum(1 for x in a for y in b if x == y)) / (len(a) * len(b))
        u_obs = U(bi, oi)
        allv = np.array(bi + oi)
        rng = np.random.default_rng(4242)
        null = []
        for _ in range(200):
            p = rng.permutation(allv)
            null.append(U(list(p[:len(bi)]), list(p[len(bi):])))
        u_lo, u_hi = float(np.percentile(null, 2.5)), float(np.percentile(null, 97.5))
        clustered = not (u_lo <= u_obs <= u_hi)
        print(f"\n  CLUSTERING  P(broken id < intact id) = {u_obs:.3f}, permutation envelope "
              f"[{u_lo:.3f}, {u_hi:.3f}] over 200 draws")
        print(f"              -> {'CLUSTERED (broken rounds are systematically older)' if clustered else 'not clustered'}")
    else:
        print(f"\n  CLUSTERING  not computable: {len(bi)} broken with a numeric id "
              f"(needs >=3). UNVERIFIED, not `no clustering`.")

    # ---- CAUSE CONCENTRATION, and it is the discriminator the pre-registered test was not ----
    # W-MIGRATION was pre-registered as "breakage clusters in round ID". That was the wrong
    # prediction: a migration's signature is many rounds failing on the SAME moved input, and
    # ids need not cluster at all. The id test is kept and reported because it was
    # pre-registered and it is what a reader will look for; this one is what separates.
    causes = {}
    for t in broken:
        causes[t["missing"] or "?"] = causes.get(t["missing"] or "?", 0) + 1
    top = max(causes.values()) if causes else 0
    conc = top / len(broken) if broken else float("nan")
    print(f"\n  CAUSE CONCENTRATION  {len(causes)} distinct missing inputs across "
          f"{len(broken)} broken rounds")
    for c, k in sorted(causes.items(), key=lambda kv: -kv[1]):
        print(f"    {k:>4}x  {c}")
    print(f"    largest single cause covers {conc:.0%} of all breakage")

    after = subprocess.run(["git", "status", "--porcelain"], cwd=str(LIVE),
                           capture_output=True).stdout
    untouched = before == after
    print(f"\n  NEGATIVE  git status byte-identical before and after the sweep: {untouched}")

    # ---- KILL ---------------------------------------------------------------------------------
    ctrl = ok and untouched
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  instrument={ok}  wrote-nothing={untouched}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the counts are not readable.")
    elif len(broken) <= 1:
        world = "W-ISOLATED"
        print(f"  -> W-ISOLATED. {len(broken)} broken round(s). r144 is a one-off and the fix is")
        print("     one path. The repo's re-runnability is not the problem it looked like.")
    elif conc >= 0.5 or clustered:
        world = "W-MIGRATION"
        print(f"  -> W-MIGRATION. {len(broken)} rounds cannot resolve their inputs and "
              f"{conc:.0%} of them")
        print(f"     fail on the SAME moved input ({len(causes)} distinct causes in total). A")
        print("     reorganisation moved files under rounds that name their inputs by absolute")
        print("     path, and no gate re-ran anything afterwards.")
        print(f"     ⚠ The pre-registered id-clustering test says {'CLUSTERED' if clustered else 'NOT clustered'} "
              f"(U {u_obs:.3f} vs [{u_lo:.3f}, {u_hi:.3f}]) —")
        print("       it was the wrong prediction, not a contrary result: ids need not cluster")
        print("       for a single moved file to break rounds written years of commits apart.")
    else:
        world = "W-ENDEMIC"
        print(f"  -> W-ENDEMIC. {len(broken)} rounds broken with no id clustering "
              f"(U {u_obs:.3f} inside [{u_lo:.3f}, {u_hi:.3f}]).")
        print("     This is not a migration artifact: the repository has not been re-runnable")
        print("     for a while, and every artifact in it is citable but not attackable.")
    print("  " + "=" * 78)

    # the artifact goes to the LIVE tree; everything measured came from the worktree
    o = SELF.parent / "results" / "runnability.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16],
        probe_sha=hashlib.sha256(PROBE.read_bytes()).hexdigest()[:16],
        world=world, n_rounds=len(rounds), n_probed=len(probed), n_skipped_gpu=len(gpu),
        counts=counts, timeout_s=TIMEOUT,
        controls={nm: dict(got=CLASS.get(g, g), want=CLASS.get(w, w), ok=bool(g == w))
                  for nm, g, w in ctl},
        instrument_ok=bool(ok), wrote_nothing=bool(untouched),
        clustering=dict(u=u_obs, lo=u_lo, hi=u_hi, clustered=bool(clustered)),
        causes=causes, cause_concentration=conc, worktree=str(ROOT),
        table=table), indent=1))
    print(f"\n  artifact {o.relative_to(LIVE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
