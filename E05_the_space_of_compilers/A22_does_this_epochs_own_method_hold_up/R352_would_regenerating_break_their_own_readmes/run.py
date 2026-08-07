"""If I regenerate the seven drifted rounds, does each round's OWN README go stale?

R351 asked whether the seven CODE DRIFT rounds touch a number on `README.md` or `FORMULATION.md`.
They do not: 27 differing leaves, 6 rendering collisions across 2 leaves, both traced to a different
round's artifact. Its scope note named the population it had deliberately left out --

    "only two documents are searched -- a value quoted in a round's own README is not counted,
     which is the right scope for `published` and the wrong one for `written down somewhere`."

That is the population here, and the ORDER matters: R351's remedy is to regenerate the seven, and
regenerating rewrites the artifact a round's own README quotes. **Checking after regenerating would
destroy the evidence needed to check.**

ESTIMAND, named before the method
---------------------------------
For each of the 7 CODE DRIFT rounds: the number of DIFFERING leaves whose COMMITTED value appears in
**that round's own README.md**. Its own, not every round's -- 345 documents would make a 3-significant
-figure collision routine, and the question that decides whether regenerating is safe is whether the
round's own writeup would go stale.

IDENTIFICATION. Same as R351 and its limits are inherited rather than restated as new: the diff is
exact; the quoted half is a SEARCH, so every hit is a CANDIDATE that only a read settles, the
precision floor is 3 significant figures, and a match must sit on a numeric boundary. The instrument
is IMPORTED from R351 rather than re-typed, so it cannot drift away from the one whose controls were
validated.

WORLDS
  W1 SAFE TO REGENERATE   0 differing leaves are quoted in their own READMEs. Regenerating the seven
                          is pure hygiene and no prose needs touching.
  W2 PROSE GOES STALE     >=1 is quoted. Regenerating would silently make a round's own writeup
                          disagree with its own artifact -- trading one inconsistency for another.

PREDICTION MATRIX
  W1 -> quoted 0 with the search's controls still firing
  W2 -> quoted >=1, each named with its line, each a CANDIDATE until read
⚠ I expect W2 for R34 and R36, which carry 13 and 9 of the 27 differing leaves, and W1 for the five
  that differ in a single leaf. Writing that down first, because a prediction I record only after
  seeing the table is not a prediction.

PRE-REGISTERED KILL
    if the imported controls fire and the REAL positive fires on this document population:
        quoted >= 1 -> W2. Name them; regeneration must update the prose in the same commit.
        quoted == 0 -> W1. Regeneration is safe, at the stated floor.
    else: UNVERIFIED.

CONTROLS
  IMPORTED    R351's diff control and planted search controls, run again here rather than assumed.
  REAL, this population   a value that IS in a round's own README and DOES live in its artifact must
              be found. R351's real control used FORMULATION; a control validated on a different
              document population than the claim's is the unit mismatch this session keeps repeating.
  ISOLATION   per path over paths present at the start.

EXIT
    0  controls hold and the census is reported
    1  a control misbehaved -- the count is silence
    2  R350 names no CODE DRIFT round, or no README exists for them: empty population, never a pass
"""
from __future__ import annotations
import hashlib, importlib.util, json, pathlib, shutil, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
SCRATCH = ROOT.parent / ".r352_scratch"


def load_r351():
    p = ROOT / ("E05_the_space_of_compilers/A22_does_this_epochs_own_method_hold_up/"
                "R351_did_a_published_number_move/run.py")
    spec = importlib.util.spec_from_file_location("r351", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, hashlib.sha256(p.read_bytes()).hexdigest()[:12]


R, R351_SHA = load_r351()


def main() -> int:
    if not R.R350.exists():
        print("  UNRUNNABLE: R350's artifact is missing. Exit 2, never 0.")
        return 2
    drift = sorted(r["round"] for r in json.loads(R.R350.read_text())["rows"]
                   if r["verdict"] == "CODE DRIFT")
    if not drift:
        print("  UNRUNNABLE: no CODE DRIFT round. Exit 2, never 0.")
        return 2
    print(f"R352 · would regenerating break their own READMEs?   {len(drift)} rounds   "
          f"(instrument imported from R351, sha {R351_SHA})\n")

    d_ok, d_detail = R.diff_controls()
    print(f"  DIFF control (imported): {d_detail}  {'PASS' if d_ok else 'FAIL'}")
    probe = 0.0478123
    planted = {"__tmp__": f"quoting {probe:.4f}\n"}
    s_ok = bool(R.find_in_docs(probe, planted)) and not R.find_in_docs(0.9182736, planted)
    print(f"  SEARCH control (imported, planted both ways): {'PASS' if s_ok else 'FAIL'}")

    before = R.tree_snapshot()
    work = SCRATCH / "work"
    if not R.make_copy(work):
        print("  UNRUNNABLE: could not copy. Exit 2, never 0.")
        return 2

    # REAL positive on THIS population: a value in a round's own README and in its own artifact
    real_ok, real_detail = False, "none located"
    for name in drift:
        h = list(work.glob(f"E*/A*/{name}"))
        if not h or not (h[0] / "README.md").exists():
            continue
        doc = {f"{name}/README.md": (h[0] / "README.md").read_text(encoding="utf-8")}
        for fn, obj in R.artifacts(h[0]).items():
            for path, v in R.leaves(obj):
                if isinstance(v, float) and R.find_in_docs(v, doc):
                    real_ok, real_detail = True, f"{name}{path} = {v} appears in its own README"
                    break
            if real_ok:
                break
        if real_ok:
            break
    print(f"  REAL positive on THIS population: {real_detail}  {'PASS' if real_ok else 'FAIL'}")

    rows, tot_d, tot_q = [], 0, 0
    print(f"\n  {'round':<46}{'leaves differing':>18}{'quoted in own README':>22}")
    for name in drift:
        h = list(work.glob(f"E*/A*/{name}"))
        if not h:
            continue
        rd = h[0]
        rme = rd / "README.md"
        doc = {f"{name}/README.md": rme.read_text(encoding="utf-8")} if rme.exists() else {}
        committed = R.artifacts(rd)
        if not R.execute(work, rd):
            print(f"  {name:<46}{'-':>18}{'did not complete':>22}")
            rows.append({"round": name, "status": "DID NOT COMPLETE"})
            continue
        fresh = R.artifacts(rd)
        nd, q = 0, []
        for fn in committed:
            if fn in fresh:
                for path, old, new in R.diff_leaves(committed[fn], fresh[fn]):
                    nd += 1
                    for d_, rend, line in R.find_in_docs(old, doc):
                        q.append({"path": path, "committed": old, "fresh": new,
                                  "rendering": rend, "line": line})
        tot_d += nd
        tot_q += len(q)
        rows.append({"round": name, "status": "ok", "n_diff": nd, "has_readme": bool(doc),
                     "quoted": q})
        print(f"  {name:<46}{nd:>18}{len(q):>22}")

    after = R.tree_snapshot()
    changed = [k for k in before if k in after and after[k] != before[k]]
    iso_ok = not changed and not [k for k in before if k not in after]
    print(f"\n  ISOLATION: {len(changed)} of {len(before)} artifacts changed  "
          f"{'PASS' if iso_ok else 'FAIL'}")
    print(f"  {tot_d} differing leaves; {tot_q} quoted in the round's own README")

    for r in rows:
        for q in r.get("quoted", [])[:6]:
            print(f"\n      {r['round']}:{q['path']}")
            print(f"          committed {q['committed']}  ->  fresh {q['fresh']}")
            print(f"          own README matched {q['rendering']!r}: {q['line']}")

    ok = d_ok and s_ok and real_ok and iso_ok
    print()
    if not ok:
        print("  UNVERIFIED: a control misbehaved, so the count is silence.")
        v = "UNVERIFIED"
    elif tot_q:
        print(f"  W2 — PROSE WOULD GO STALE. {tot_q} value(s) a round's own README prints would")
        print("  change on regeneration. Each is a CANDIDATE until the line is read; where it holds,")
        print("  the prose must be updated in the SAME commit as the artifact, or regenerating just")
        print("  trades an artifact-vs-code inconsistency for a prose-vs-artifact one.")
        v = "W2_PROSE_GOES_STALE"
    else:
        print(f"  W1 — SAFE TO REGENERATE. None of the {tot_d} differing leaves is quoted in its own")
        print("  round's README, at 3 significant figures. Regeneration is pure hygiene.")
        v = "W1_SAFE"

    art = {"drift_rounds": drift, "rows": rows, "total_diff": tot_d, "total_quoted": tot_q,
           "r351_sha": R351_SHA, "min_sigfig": R.MIN_SIGFIG,
           "controls": {"diff": d_ok, "search_planted": s_ok, "real_this_population": real_ok,
                        "isolation": iso_ok}, "verdict": v}
    outp = HERE / "results" / "r352_own_readmes.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    print("\n  ⚠ SCOPE. Each round's OWN README only. A value one round quotes from ANOTHER round is")
    print("    not counted here -- and that is a real gap, because cross-citation is exactly how a")
    print("    regenerated number would travel. 345 READMEs at 3 significant figures would collide")
    print("    constantly, so the wider population needs a tighter instrument, not this one.")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
