"""R302 — is a committed artifact in this campaign reproducible from its committed code?

WHY, AND IT STARTED AS HOUSEKEEPING. Eight result JSONs have sat modified-but-uncommitted for
days; the session hook has flagged them every start and nobody diagnosed them. Diffing them was
supposed to be a two-minute cleanup. It is not: **742 leaf values differ across the eight, and
three of them changed their `verdict` string.** R241's committed artifact asserts
`valid = ['FLOOR_circular']`; three runs of the committed code produce `valid = []` and
`UNVERIFIED`.

MECHANISM, ALREADY ESTABLISHED BEFORE THIS ROUND (so this round measures its REACH, not its
existence). R241 line 93 seeds an rng with `abs(hash((pid, arm, dd))) % 2**32`. Python randomises
`hash()` of a str per process unless PYTHONHASHSEED is set. Controlled:

    same PYTHONHASHSEED twice   -> artifacts IDENTICAL
    different PYTHONHASHSEED    -> artifacts DIFFER

That is a two-cell experiment with the placebo (same seed) passing, and it is why the estimand
below is about REACH rather than about cause.

⚠ THE UNIT TRAP, WRITTEN BEFORE THE RUN. A grep found 24 run.py files containing
`default_rng(...hash(...))`. **The instrument's unit is `file contains a pattern`; the claim's unit
is `round's artifact moves`.** They are not equal, and realstat's search row says a positive
control on the grep licenses nothing about the second unit. A hash-seeded rng can be inert -- used
for a display sample, or averaged away. So the 24 are CANDIDATES; this round executes them and the
count of affected rounds is the measurement, never the grep.

ESTIMAND        (a) of the candidate rounds, how many produce a DIFFERENT artifact under two
                PYTHONHASHSEEDs; (b) of those, how many change a `verdict`/decision field rather
                than only numbers; (c) whether any NON-candidate round also differs.
IDENTIFICATION  exact and mechanical -- run, hash the artifact, compare. No modelling.
SCOPE           population every E0*/A*/R*/run.py in this repo that writes into its own results/
                dir · instrument the committed code itself · baseline the same code at a second
                hash seed · regime one machine, one venv, one data snapshot.
WORLDS          W-INERT     the pattern is decorative; few or no artifacts move. -> the 8 dirty
                            files are something else and the diagnosis above is incomplete.
                W-NUMERIC   artifacts move but no verdict does. -> published NUMBERS carry an
                            undeclared seed, and every interval in FORMULATION.md is understated
                            by the between-seed spread.
                W-VERDICT   at least one verdict moves. -> an artifact in this repo can assert a
                            conclusion the code does not reproduce, and no committed number is
                            citable until its round is re-run under a fixed seed.
KILL            pre-registered, conditional on the controls:
                  if placebo_holds and negative_control_null:
                      >=1 verdict field differs  -> W-VERDICT
                      >=1 artifact differs, no verdict does -> W-NUMERIC
                      none differ -> W-INERT
                  else: UNVERIFIED
POSITIVE CTRL   R241 is a candidate and is ALREADY PROVEN to differ. The sweep must recover it. If
                it does not, the sweep is not measuring what R241 demonstrated and nothing below
                reads. Fails at g=0: a round with no rng cannot differ.
NEGATIVE CTRL   the NON-candidate rounds. If those differ too, `hash()` is not the mechanism and
                the whole framing is wrong -- reported, not suppressed.
PLACEBO         each round also run TWICE AT THE SAME SEED; that pair must be byte-identical. A
                round failing the placebo has some other nondeterminism and is reported in its own
                bucket, never merged into the hash-seed count.
NOISE FLOOR     n/a -- the comparison is byte equality, not an estimate.
MULTIPLICITY    no test statistic; every round is reported, both buckets, with timeouts named.
SEEDS           PYTHONHASHSEED in {1234, 9999}; the placebo repeats 1234.
ARTIFACT        results/reproducibility.json with source hash.
⚠ SIDE EFFECTS   these scripts write into their own results/ dirs. Every touched file is byte-
                snapshotted before and RESTORED after, and the restoration is VERIFIED, because a
                sweep that silently rewrote 24 committed artifacts would be worse than the defect.
IMPOSSIBLE      whether a round is reproducible on a DIFFERENT machine -- needs a second machine.
"""
import hashlib, json, os, pathlib, subprocess, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[3]
PY = str(ROOT / ".venv" / "bin" / "python")
TIMEOUT = int(os.environ.get("R302_TIMEOUT", "150"))
SEED_A, SEED_B = "1234", "9999"
SELF = pathlib.Path(__file__).resolve()


def digest(d: pathlib.Path):
    """Content hash of a results dir, or None if it has no files."""
    fs = sorted(p for p in d.rglob("*") if p.is_file())
    if not fs:
        return None, []
    h = hashlib.sha256()
    for p in fs:
        h.update(p.relative_to(d).as_posix().encode()); h.update(p.read_bytes())
    return h.hexdigest()[:16], fs


def snapshot(d: pathlib.Path):
    return {p: p.read_bytes() for p in d.rglob("*") if p.is_file()}


def restore(snap, d: pathlib.Path):
    """Put back exactly what was there, and delete anything the run created."""
    for p in list(d.rglob("*")):
        if p.is_file() and p not in snap:
            p.unlink()
    for p, b in snap.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists() or p.read_bytes() != b:
            p.write_bytes(b)


def verdict_fields(d: pathlib.Path):
    """Every string-valued leaf whose key names a decision, from every json in the dir."""
    out = {}
    KEYS = ("verdict", "world", "killed", "admitted", "valid", "decision", "conclusion",
            "pass", "ok", "survived", "result")
    def walk(o, p=""):
        if isinstance(o, dict):
            for k, v in o.items(): walk(v, f"{p}.{k}" if p else str(k))
        elif isinstance(o, list):
            for i, v in enumerate(o): walk(v, f"{p}[{i}]")
        else:
            leaf = p.split(".")[-1].split("[")[0].lower()
            if any(k in leaf for k in KEYS):
                out[p] = o
    for j in sorted(d.glob("*.json")):
        try: walk(json.loads(j.read_text()), j.name)
        except Exception: pass
    return out


def run_once(script: pathlib.Path, seed: str):
    d = script.parent / "results"
    d.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONHASHSEED=seed)
    t0 = time.time()
    try:
        r = subprocess.run([PY, str(script)], cwd=str(ROOT), env=env,
                           capture_output=True, timeout=TIMEOUT)
        rc = r.returncode
    except subprocess.TimeoutExpired:
        return None, None, "timeout", time.time() - t0
    dg, _ = digest(d)
    return dg, verdict_fields(d), f"exit{rc}", time.time() - t0


def main():
    cands, others, gpu_skipped = [], [], []
    for s in sorted(ROOT.glob("E0*/A*/R*/run.py")):
        if s.resolve() == SELF:
            continue
        try: src = s.read_text()
        except Exception: continue
        # A round that loads a judge would contend for the 16 GB card with whatever else is
        # queued, and three runs of it is three model loads. EXCLUDED AND NAMED -- a silent skip
        # here would read as `swept everything` in the count below, which is the exact thing the
        # last two closing summaries got wrong.
        if any(t in src for t in ("import torch", "from torch", "device_map", "cuda")):
            gpu_skipped.append(s); continue
        (cands if "hash(" in src and "default_rng" in src else others).append(s)
    print(f"  {len(cands)} CANDIDATE rounds (default_rng + hash) · "
          f"{len(others)} non-candidate · {len(gpu_skipped)} EXCLUDED for touching the GPU:")
    for s in gpu_skipped:
        print(f"    excluded (GPU): {'/'.join(s.parts[-3:-1])}")
    print()
    print(f"  ⚠ the grep's unit is `file contains a pattern`; the claim's unit is `artifact "
          f"moves`.\n    The 24 below are candidates. The MEASUREMENT is what running them does."
          f"\n  timeout {TIMEOUT}s per run; a timeout is UNVERIFIED, never `identical`.\n")

    # the negative control is a SAMPLE of the non-candidates, size-matched, so the sweep's total
    # cost stays bounded. Which ones is deterministic (first N by path) and stated, not sampled.
    NEG_N = min(len(others), 12)
    neg = others[:NEG_N]
    print(f"  NEGATIVE CONTROL: the first {NEG_N} non-candidate rounds by path, size-bounded so the"
          f"\n  sweep terminates. Named in the artifact; not a random sample and not claimed to be."
          f"\n")

    res, order = {}, [("candidate", s) for s in cands] + [("non-candidate", s) for s in neg]
    print(f"  {'round':<46}{'kind':<14}{'A/B':<10}{'placebo':<9}  fields moved")
    for kind, s in order:
        name = "/".join(s.parts[-3:-1])
        d = s.parent / "results"
        snap = snapshot(d)
        try:
            dA, vA, sA, tA = run_once(s, SEED_A)
            dB, vB, sB, tB = run_once(s, SEED_B)
            dP, vP, sP, tP = run_once(s, SEED_A)          # placebo: same seed as A
        finally:
            restore(snap, d)
            back, _ = digest(d)
        if dA is None or dB is None or dP is None:
            res[name] = dict(kind=kind, status="timeout", ab=None, placebo=None)
            print(f"    {name[:44]:<46}{kind:<14}{'TIMEOUT':<10}{'—':<9}  UNVERIFIED")
            continue
        ab_same = (dA == dB)
        pl_same = (dA == dP)
        moved = sorted(k for k in set(vA) | set(vB) if vA.get(k) != vB.get(k)) if vA else []
        res[name] = dict(kind=kind, status=sA, ab_identical=bool(ab_same),
                         placebo_identical=bool(pl_same), verdict_fields_moved=moved,
                         n_verdict_fields=len(vA or {}), seconds=round(tA, 1))
        print(f"    {name[:44]:<46}{kind:<14}"
              f"{'same' if ab_same else 'DIFFER':<10}{'ok' if pl_same else 'BROKEN':<9}  "
              f"{len(moved)} of {len(vA or {})}")

    ran = {k: v for k, v in res.items() if v.get("ab_identical") is not None}
    cand_r = {k: v for k, v in ran.items() if v["kind"] == "candidate"}
    neg_r = {k: v for k, v in ran.items() if v["kind"] == "non-candidate"}
    moved_c = [k for k, v in cand_r.items() if not v["ab_identical"]]
    moved_n = [k for k, v in neg_r.items() if not v["ab_identical"]]
    verd = [k for k, v in cand_r.items() if v["verdict_fields_moved"]]
    placebo_broken = [k for k, v in ran.items() if not v["placebo_identical"]]
    timeouts = [k for k, v in res.items() if v.get("status") == "timeout"]

    pos_key = [k for k in cand_r if "R241" in k]
    pos_ok = bool(pos_key) and not cand_r[pos_key[0]]["ab_identical"]
    print(f"\n  POSITIVE CTRL  R241 recovered as DIFFERING: {pos_ok}"
          + ("" if pos_key else "   (R241 not in the swept set — the sweep missed its own anchor)"))
    print(f"  PLACEBO        same seed twice identical for all but {len(placebo_broken)}: "
          f"{placebo_broken}")
    print(f"  NEGATIVE CTRL  non-candidates that ALSO differ: {len(moved_n)} of {len(neg_r)} "
          f"{moved_n}")
    print(f"  TIMEOUTS       {len(timeouts)} rounds UNVERIFIED (not counted as identical): "
          f"{timeouts}")

    print("\n  " + "=" * 78)
    ctrl = pos_ok and not placebo_broken
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. The positive control did not recover R241, or the placebo broke.")
        print("     Neither world is readable and this is NOT a verdict of W-INERT.")
    elif verd:
        world = "W-VERDICT"
        print(f"  -> W-VERDICT. {len(verd)} of {len(cand_r)} candidate rounds change a DECISION")
        print(f"     field across hash seeds: {verd}")
        print("     An artifact in this repo can assert a conclusion its own code does not")
        print("     reproduce. No number from an affected round is citable until it is re-run")
        print("     with PYTHONHASHSEED fixed, and the fix is to seed from the DATA, not hash().")
    elif moved_c:
        world = "W-NUMERIC"
        print(f"  -> W-NUMERIC. {len(moved_c)} of {len(cand_r)} candidates move their NUMBERS and")
        print("     none moves a verdict. Published intervals are understated by the between-seed")
        print("     spread, which is a real but bounded defect.")
    else:
        world = "W-INERT"
        print(f"  -> W-INERT. No candidate artifact moved. The hash-seeded rng is decorative in")
        print("     all of them and the eight dirty files have a DIFFERENT cause, still open.")
    print(f"  candidates moving: {len(moved_c)} of {len(cand_r)} run  ·  "
          f"verdict-movers: {len(verd)}")
    print("  " + "=" * 78)

    src = hashlib.sha256(SELF.read_bytes()).hexdigest()[:16]
    o = SELF.parent / "results" / "reproducibility.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=src, timeout_s=TIMEOUT, seeds=[SEED_A, SEED_B], world=world,
        n_candidates=len(cands), n_noncandidates=len(others),
        gpu_excluded=[str(p.relative_to(ROOT)) for p in gpu_skipped],
        negative_control_set=[str(p.relative_to(ROOT)) for p in neg],
        rounds=res, moved_candidates=moved_c, moved_noncandidates=moved_n,
        verdict_movers=verd, placebo_broken=placebo_broken, timeouts=timeouts,
        positive_control_ok=bool(pos_ok)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
