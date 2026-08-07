"""R319 — six rounds read the tensor R257 produced with a hand-retyped prompt, and one is the site MDE.

R318 said the two tensors differ by "an unrecorded change" and concluded the site MDE is bounded by
something nobody wrote down. **That was a wall I never checked.** The change is recorded, in the
place this project's own constitution says the WHY lives: the commit body.

    4498585, 2026-08-03 06:02:28
    "[fix] The judge is not bit-deterministic within a single process, and my own positive
     control caught me retyping the prompt instead of importing it"
    "POSITIVE, a real failure: r 0.9407 / MAD 0.0632 against the r04 cache, where R234's
     faithful re-implementation gets 0.998 / 0.008. I HAND-RETYPED the few-shot block instead
     of importing covalx.judge.build_prompt."

My independent measurement of the same pair was r = 0.9508. Their contemporaneous measurement
against the cache was 0.9407. Same phenomenon, two vantage points.

⛔ AND THE PROVENANCE IS PROVEN BY HASH, not by filename and not by inference:
    4135f31  06:00:32  R257/results/instruments.npz  sha f29c6e028c98aea6  <- PRE-fix
    _archive/r257_first_pass/instruments_retyped_prompt.npz  sha f29c6e028c98aea6  <- IDENTICAL
    f6e3bbd  06:12:56  R257/results/instruments.npz  sha 42a84f65224ae0f7  <- POST-fix, and is
                                                                             what is committed now
So draw A IS the output of the hand-retyped prompt and draw B IS the output of the canonical
imported builder. D8, from git object hashes.

⛔ AND "NEITHER INSTRUMENT IS PRIVILEGED" DOES NOT APPLY. R257 wrote that line about DEFAULT vs
FLIPPED label order — a gauge, where both readings are legitimate and disagreement is the finding.
It is not about canonical-builder vs my typo. **A typo is not a gauge.** I quoted it one round ago
to argue neither bracket may be preferred, and that was the line doing work it was never about.

WHY IT HAPPENED, because the mechanism is more useful than the blame: the corrected tensor did not
exist when the readers were written. The fix landed 06:02:28, a reader first pointed at the archived
first pass 06:06:13, and the re-run with the imported prompt only arrived 06:12:56. For those ten
minutes the defective tensor was the ONLY tensor. Nobody re-pointed the readers afterwards, and the
artifacts have been read as current ever since.

ESTIMAND      for each of the six rounds reading the archived tensor, the change in every published
              quantity when the input is repointed to the canonical one — and whether each round's
              VERDICT survives, separately from whether its numbers do.
IDENTIFICATION exact for the numbers. NOT identified for "which is true in the world": this
              establishes that the canonical builder is the one the round intended, not that its
              output is correct. A round whose verdict flips is UNVERIFIED, not corrected.
SCOPE         population the 6 rounds under A23 that read `_archive/r257_first_pass/` · instrument
              Qwen3.5-2B-Base under R234's canonical builder vs a hand-retyped approximation of it ·
              regime R257's 250-prompt grid.
WORLDS        W-NUMBERS-ONLY  every verdict survives; only magnitudes move -> the arc's conclusions
                              stand and six numbers are corrected.
              W-VERDICT-MOVES some verdict changes -> that round is UNVERIFIED and everything
                              downstream of it re-opens.
              W-INERT         nothing moves -> the retyping did not reach these statistics and the
                              whole line is a filing error rather than a measurement error.
KILL          conditional on the provenance control:
                all 6 verdicts identical, >=1 number moves   -> W-NUMBERS-ONLY
                any verdict differs                          -> W-VERDICT-MOVES
                no number moves anywhere                     -> W-INERT
POSITIVE CTRL the provenance chain itself, and it is checkable rather than argued: the archived
              file's sha256 must equal the git blob at 4135f31, and must NOT equal the blob at
              f6e3bbd. If either fails, the story is wrong and nothing below is licensed.
PLACEBO       re-running a round with its input UNCHANGED must reproduce its committed artifact key
              for key — established for R274 at 16/16 in R318, and required here for each round
              before its repointed run is compared to anything.
NEGATIVE CTRL none available: destroying the structure means a third prompt typing, which needs the
              GPU. Named, not improvised.
MULTIPLICITY  6 rounds x every key in each artifact; movers and non-movers both printed.
ARTIFACT      results/repoint.json with per-round before/after and the provenance hashes.
IMPOSSIBLE    establishing that the canonical builder's output is CORRECT rather than merely
              intended — that needs an external criterion the release does not carry.
"""
import hashlib, json, pathlib, shutil, subprocess, sys, tempfile

LIVE = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
PY = LIVE / ".venv" / "bin" / "python"
A23 = LIVE / "E05_the_space_of_compilers/A23_is_the_admissibility_gate_the_right_gate"
A_NPZ = LIVE / "_archive/r257_first_pass/instruments_retyped_prompt.npz"
B_NPZ = A23 / "R257_label_order_gauge_propagation" / "results" / "instruments.npz"
OLD_REF = 'ROOT / "_archive/r257_first_pass/instruments_retyped_prompt.npz"'
ROUNDS = ["R260", "R267", "R268", "R269", "R274", "R275"]
PRE_BLOB, POST_BLOB = "4135f31", "f6e3bbd"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def blob_sha(commit):
    out = subprocess.run(["git", "ls-tree", "-r", "--name-only", commit], cwd=str(LIVE),
                         capture_output=True, text=True).stdout
    path = next((l for l in out.splitlines()
                 if "R257" in l and l.endswith("results/instruments.npz")), None)
    if not path:
        return None
    raw = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=str(LIVE),
                         capture_output=True).stdout
    return hashlib.sha256(raw).hexdigest()[:16]


def main():
    print("  PROVENANCE CONTROL — proven by git object hash, not by filename\n")
    pre, post, arch, comm = blob_sha(PRE_BLOB), blob_sha(POST_BLOB), sha(A_NPZ), sha(B_NPZ)
    print(f"    {PRE_BLOB} (06:00, PRE-fix)   R257/results/instruments.npz  {pre}")
    print(f"    archived first-pass tensor                                 {arch}"
          f"   {'IDENTICAL' if arch == pre else 'MISMATCH'}")
    print(f"    {POST_BLOB} (06:12, POST-fix)  R257/results/instruments.npz  {post}")
    print(f"    committed tensor now                                       {comm}"
          f"   {'IDENTICAL' if comm == post else 'MISMATCH'}")
    prov_ok = (arch == pre) and (comm == post) and (arch != comm)
    print(f"\n    -> provenance {'ESTABLISHED' if prov_ok else 'NOT established'}: draw A is the "
          f"hand-retyped output, draw B the canonical one")
    if not prov_ok:
        print("  REFUSING: the provenance story is wrong; nothing below is licensed.")
        return 2

    rows = []
    for rid in ROUNDS:
        d = next((p for p in A23.glob(f"{rid}_*") if p.is_dir()), None)
        if d is None:
            print(f"  {rid}: directory absent"); continue
        art = sorted(d.glob("results/*.json"))
        src = (d / "run.py").read_text()
        if not art or OLD_REF not in src:
            rows.append(dict(round=rid, status="SKIPPED",
                             note="no artifact or no archived-tensor reference"))
            continue
        committed = json.loads(art[0].read_text())

        with tempfile.TemporaryDirectory() as tmp:
            work = pathlib.Path(tmp) / d.name
            shutil.copytree(d, work)
            # ROOT is resolved from the round's own depth; pin it to LIVE so the copy still reads
            # the real inputs, and repoint ONLY the tensor.
            s = work.joinpath("run.py").read_text()
            # ⚠ A PATH, NOT A STRING. The first version substituted `repr(str(LIVE))`, which is a
            # str literal, so `ROOT / "data"` raised TypeError and BOTH runs died at import. And
            # because copytree had already copied the committed artifact into results/, the dead
            # runs left it in place -- so the placebo compared the committed artifact to ITSELF
            # and passed, the repointed run compared it to itself and "moved 0 keys", and the
            # round printed W-INERT with every control green having executed nothing.
            # `a fallback hides the primary's death`, and the fallback here was doing nothing.
            pin = f"__import__('pathlib').Path({str(LIVE)!r})"
            # ⚠ AND THE PIN MUST NOT ASSUME ONE IDIOM. The first version rewrote only
            # `parents[3]`; R260 computes its root as
            # `next(p for p in ...parents if (p / "covalx").is_dir())`, which finds nothing under
            # /tmp, so it died with StopIteration and was reported RUN-FAILED -- correctly, but the
            # failure was MINE. Rewriting the whole `ROOT = ...` / `_ROOT = ...` assignment covers
            # every idiom, because what varies is how the root is DERIVED and what matters is only
            # what it ends up being.
            import re as _re
            s = _re.sub(r"^(_?ROOT)\s*=\s*.*$", lambda m: f"{m.group(1)} = {pin}", s,
                        flags=_re.M)
            s = s.replace("str(" + pin + ")", repr(str(LIVE)))
            base = s

            def execute(source):
                """Run a variant from a CLEARED results dir and refuse to read a stale artifact."""
                for old in work.glob("results/*.json"):
                    old.unlink()
                work.joinpath("run.py").write_text(source)
                pr = subprocess.run([str(PY), "run.py"], cwd=str(work),
                                    capture_output=True, timeout=1800)
                got = sorted(work.glob("results/*.json"))
                if pr.returncode != 0 or not got:
                    tail = pr.stderr.decode("utf8", "replace").strip().splitlines()[-1:] or [""]
                    return None, f"rc={pr.returncode} {tail[0][:90]}"
                return json.loads(got[0].read_text()), None

            placebo, pl_err = execute(base)
            repointed, rp_err = execute(base.replace(OLD_REF, f"__import__('pathlib')."
                                                              f"Path({str(B_NPZ)!r})"))
            if placebo is None or repointed is None:
                rows.append(dict(round=rid, status="RUN-FAILED",
                                 note=f"placebo: {pl_err} | repointed: {rp_err}"))
                print(f"\n  {rid}  RUN-FAILED  placebo:{pl_err}  repointed:{rp_err}")
                continue
            pl_diff = [k for k in set(committed) | set(placebo)
                       if committed.get(k) != placebo.get(k)]

        moved = sorted(k for k in set(committed) | set(repointed)
                       if committed.get(k) != repointed.get(k))
        # ⚠ COMPARE THE VERDICT LABEL, NOT THE VERDICT STRING. These rounds interpolate their own
        # numbers into the verdict sentence, so a string comparison reports a verdict change
        # whenever ANY number moves -- which is precisely what this round is measuring, so it
        # returned "5 of 5 verdicts moved" when the truth was 1 of 5. Same defect as R318's
        # admitted-set extractor, third time this session that a string shortcut manufactured a
        # verdict. The label is the token before the em-dash separator.
        def label(v):
            return (v or "").split(" -- ")[0].strip()
        vkeys = [k for k in committed if "verdict" in k.lower() or "world" in k.lower()]
        vmoved = [k for k in vkeys if label(committed.get(k)) != label(repointed.get(k))]
        vlabels = {k: [label(committed.get(k)), label(repointed.get(k))] for k in vkeys}
        rows.append(dict(round=rid, status="OK" if not pl_diff else "PLACEBO-FAILED",
                         placebo_diff=pl_diff, n_keys=len(set(committed) | set(repointed)),
                         moved=moved, verdict_keys=vkeys, verdict_moved=vmoved,
                         verdict_labels=vlabels,
                         before={k: committed.get(k) for k in moved if not isinstance(committed.get(k), (dict, list))},
                         after={k: repointed.get(k) for k in moved if not isinstance(repointed.get(k), (dict, list))}))
        lab = "  ".join(f"{k}: {a_}->{b_}" for k, (a_, b_) in vlabels.items())
        print(f"\n  {rid}  placebo={'PASS' if not pl_diff else 'FAIL ' + str(pl_diff)}  "
              f"keys={len(set(committed) | set(repointed))}  moved={len(moved)}  "
              f"LABEL {lab or '(none)'}")
        for k in moved[:8]:
            a_, b_ = committed.get(k), repointed.get(k)
            if not isinstance(a_, (dict, list)):
                print(f"      {k:<22}{str(a_)[:26]:>28} -> {str(b_)[:26]}")

    ok = [r for r in rows if r.get("status") == "OK"]
    failed = [r["round"] for r in rows if r.get("status") == "RUN-FAILED"]
    if failed:
        print(f"\n  ⚠ {len(failed)} rounds could not be executed: {failed}")
    plc_ok = bool(ok) and all(not r["placebo_diff"] for r in ok) and len(ok) == len(ROUNDS)
    any_moved = any(r["moved"] for r in ok)
    verdict_moved = [r["round"] for r in ok if r["verdict_moved"]]

    print("\n  " + "=" * 78)
    print(f"  CONTROLS  provenance={prov_ok}  placebo={plc_ok} ({len(ok)} rounds)  -> "
          f"{'evaluate' if prov_ok and plc_ok else 'UNVERIFIED'}")
    if not (prov_ok and plc_ok):
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A round's committed artifact does not reproduce from its own")
        print("     code and input, so a repointed run cannot be compared to it.")
    elif verdict_moved:
        world = "W-VERDICT-MOVES"
        print(f"  -> W-VERDICT-MOVES. {verdict_moved} change their verdict under the canonical")
        print("     tensor. Those rounds are UNVERIFIED and everything downstream re-opens.")
    elif not any_moved:
        world = "W-INERT"
        print("  -> W-INERT. Nothing moves. The retyping did not reach these statistics, and")
        print("     six rounds pointing at an archived file is a filing error, not a measurement")
        print("     error.")
    else:
        world = "W-NUMBERS-ONLY"
        n_mv = sum(len(r["moved"]) for r in ok)
        print(f"  -> W-NUMBERS-ONLY. {n_mv} published quantities across {len(ok)} rounds move")
        print("     under the canonical tensor, and NOT ONE VERDICT does. The arc's conclusions")
        print("     stand; its magnitudes were computed on the output of a hand-retyped prompt.")
    print("  " + "=" * 78)

    o = SELF.parent / "results" / "repoint.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        provenance=dict(pre_blob=pre, archived=arch, post_blob=post, committed=comm,
                        established=bool(prov_ok)),
        rounds=rows, placebo_ok=bool(plc_ok), verdict_moved=verdict_moved,
        n_executed=len(ok), n_failed=len(rows) - len(ok)), indent=1))
    print(f"\n  artifact {o.relative_to(LIVE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
