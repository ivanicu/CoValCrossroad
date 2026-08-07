"""R1051 — execute the 16 flagged rounds. Does the committed artifact come from the committed code?

R1050 downgraded the clause to unverified-provenance: the currency gate cannot show the statement
carries the 16 facts R1049 flagged. R1050's NEXT named the repair — re-run each round and compare.

⛔⛔ AND A NAIVE VERSION OF THAT REPAIR IS §4's `determinism read as currency` RUN BACKWARDS. A first
   probe showed R978's artifact changing on re-run and R1012's not. `differs from committed` has TWO
   causes and they demand opposite conclusions:
       the round is NON-DETERMINISTIC          -> the comparison is meaningless, UNVERIFIED
       the round is deterministic and DRIFTED  -> the committed artifact did NOT come from the
                                                  committed code, which is the real defect
   So every round is run TWICE. run1 vs run2 separates them, and no verdict is read off a single run.

ESTIMAND        for each flagged round, the joint outcome (committed == run1, run1 == run2), and the
                count of rounds in each of the four cells
IDENTIFICATION  exact for the comparisons. ⚠ Byte-equality is strict: a path, an ordering or a float
                repr can differ while every value agrees, so BOTH byte and numeric-value comparison
                are computed and reported (G4 - the comparison rule is a specification axis).
SCOPE           population : R1050's 16 flagged rounds
                instrument : the rounds' own run.py, executed in place, artifact restored after
                baseline   : the committed artifact bytes, read from git, never from the worktree
                regime     : this checkout, this interpreter
WORLDS          A THE PROVENANCE HOLDS - deterministic rounds re-derive their committed artifact, so
                  the numbers under the clause are re-derivable and the downgrade is about the GATE,
                  not about the values.
                B THE ARTIFACTS HAVE DRIFTED - deterministic rounds produce something else, so a
                  committed artifact does not come from its committed code and the clause rests on
                  numbers no longer reproducible.
                prediction matrix: A -> drifted count 0    B -> drifted count > 0
KILL            pre-registered and CONDITIONAL:
                  if the controls fire:
                      any DETERMINISTIC round differing from committed -> World B
                      none                                             -> World A
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the differ must detect a KNOWN difference: the committed bytes with one digit changed
                must compare unequal. A comparison never shown to return unequal is silence.
NEGATIVE CTRL   the committed bytes compared to THEMSELVES must compare equal.
PLACEBO         a round that errors or times out is UNVERIFIED - never counted as agreeing, and never
                counted as drifted.
NOISE FLOOR     run1 vs run2 IS the noise floor, measured per round rather than assumed.
MULTIPLICITY    all 16 reported in all four cells, plus errors, not only the drifted ones.
SEEDS           2 executions per round; the design is the two-run comparison itself.
IMPOSSIBLE      whether a DRIFTED artifact's committed value was ever correct. Drift shows the code
                and the artifact disagree NOW; it cannot say which was right when committed.
                SETTLES: IN-RELEASE - the round's git history holds both, at one log read per round.
"""
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PY = str(ROOT / ".venv/bin/python")


def git_show(rel):
    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT,
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def restore(rel):
    subprocess.run(["git", "checkout", "--", rel], cwd=ROOT, capture_output=True)


def values(b):
    """numeric leaves only — the value comparison, blind to key order and formatting"""
    out = []

    def walk(o):
        if isinstance(o, bool):
            return
        if isinstance(o, (int, float)):
            out.append(round(float(o), 9))
        elif isinstance(o, dict):
            for k in sorted(o):
                walk(o[k])
        elif isinstance(o, list):
            for v in o:
                walk(v)
    try:
        walk(json.loads(b))
    except Exception:
        return None
    return out


def main() -> int:
    fl = json.loads(next(ROOT.glob(
        "E05_the_space_of_compilers/A27*/R1050_*/results/audit_reached_the_object.json")
    ).read_text())["flagged"]
    if not fl:
        print("  UNRUNNABLE: empty flagged set. Exit 2, never 0."); return 2

    jobs = []
    for r in fl:
        ds = [p for p in ROOT.glob(f"E05_the_space_of_compilers/A*/{r}_*") if p.is_dir()]
        if not ds or not (ds[0] / "run.py").exists():
            jobs.append((r, None, None)); continue
        arts = sorted((ds[0] / "results").glob("*.json"))
        jobs.append((r, ds[0] / "run.py", arts[0] if arts else None))

    runnable = [j for j in jobs if j[1] and j[2]]
    if not runnable:
        print("  UNRUNNABLE: no flagged round has both a script and an artifact. Exit 2, never 0.")
        return 2

    # ---------- controls, on the real committed bytes ----------
    rel0 = str(runnable[0][2].relative_to(ROOT))
    b0 = git_show(rel0)
    if b0 is None:
        print("  UNRUNNABLE: cannot read committed bytes. Exit 2, never 0."); return 2
    # ⛔ THE FIRST MUTATION WAS A BYTE MUTATION AND THE CONTROL CAUGHT IT. Replacing the first "0"
    #   hit a digit inside a STRING ("R1000" -> "R9000"): bytes changed, no numeric value did, so
    #   the value comparison correctly reported EQUAL and the control correctly reported FAIL. The
    #   mutation has to target the unit the comparison is about — a numeric LEAF, not a character.
    def mutate_a_number(b):
        o = json.loads(b)
        done = []

        def walk(x):
            if isinstance(x, dict):
                for k in sorted(x):
                    if isinstance(x[k], (int, float)) and not isinstance(x[k], bool) and not done:
                        x[k] = float(x[k]) + 1.5
                        done.append(k)
                    else:
                        walk(x[k])
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(o)
        return (json.dumps(o).encode(), bool(done))

    mutated, planted = mutate_a_number(b0)
    pos = planted and (b0 != mutated) and (values(b0) != values(mutated))
    if not planted:
        print("  ⛔ no numeric leaf to plant in — the control cannot be run, so it cannot pass.")
    neg = (b0 == b0) and (values(b0) == values(b0))
    print(f"  POSITIVE — the differ must call a one-digit mutation UNEQUAL, on bytes AND on values: "
          f"{pos}")
    print(f"  NEGATIVE — identical bytes must compare EQUAL: {neg}")
    if not (pos and neg):
        print("  the comparison does not discriminate. Exit 2, never 0."); return 2

    rows = []
    for rid, script, art in jobs:
        if not (script and art):
            rows.append({"round": rid, "status": "NO_ARTIFACT"}); continue
        rel = str(art.relative_to(ROOT))
        committed = git_show(rel)
        rec = {"round": rid}
        try:
            outs = []
            for _ in range(2):
                p = subprocess.run([PY, str(script)], cwd=ROOT, capture_output=True, timeout=200)
                if p.returncode != 0:
                    rec["status"] = f"EXIT_{p.returncode}"
                    break
                outs.append(art.read_bytes())
            else:
                rec.update(
                    status="RAN",
                    deterministic_bytes=outs[0] == outs[1],
                    deterministic_values=values(outs[0]) == values(outs[1]),
                    matches_committed_bytes=committed == outs[0],
                    matches_committed_values=values(committed) == values(outs[0]),
                )
        except subprocess.TimeoutExpired:
            rec["status"] = "TIMEOUT"
        finally:
            restore(rel)
        rows.append(rec)
        print(f"     {rid:>6} {rec.get('status'):<9} "
              f"det(b/v)={rec.get('deterministic_bytes')}/{rec.get('deterministic_values')} "
              f"match(b/v)={rec.get('matches_committed_bytes')}/{rec.get('matches_committed_values')}")

    ran = [r for r in rows if r.get("status") == "RAN"]
    unver = [r for r in rows if r.get("status") != "RAN"]
    # ⛔ ONLY A DETERMINISTIC ROUND CAN DRIFT. A non-deterministic one is UNVERIFIED, never drifted.
    det = [r for r in ran if r["deterministic_values"]]
    drifted = [r["round"] for r in det if not r["matches_committed_values"]]
    nondet = [r["round"] for r in ran if not r["deterministic_values"]]

    print(f"\n  ⭐ flagged {len(rows)} · ran {len(ran)} · unverified (error/timeout/missing) "
          f"{len(unver)} · deterministic on values {len(det)} · NON-deterministic {len(nondet)}")
    print(f"  ⭐ DRIFTED (deterministic AND != committed): {len(drifted)} {drifted}")
    print(f"  non-deterministic (comparison meaningless, UNVERIFIED): {nondet}")

    print()
    if not ran:
        world = "⛔ UNVERIFIED — nothing executed."
    elif drifted:
        world = (f"⭐ B THE ARTIFACTS HAVE DRIFTED — {len(drifted)} deterministic round(s) produce "
                 f"something other than what is committed: {drifted}. For those, the committed "
                 f"artifact did not come from the committed code, so the clause rests on numbers "
                 f"that no longer reproduce. This is a stronger defect than R1050's downgrade: not "
                 f"'the gate cannot attribute it' but 'the code disagrees with the file'.")
    else:
        world = (f"⭐ A THE PROVENANCE HOLDS ON THE VALUES — all {len(det)} deterministic flagged "
                 f"rounds re-derive their committed artifact exactly. The clause's downgrade is "
                 f"therefore about the GATE and not about the numbers: they are re-derivable on "
                 f"demand, which is what R1050 said the repair would need to show.")
    print(world)
    print(f"⛔ AND {len(nondet)} NON-DETERMINISTIC ROUND(S) ARE UNVERIFIED, NOT CLEARED. A round whose")
    print(f"   own two runs disagree cannot be compared to its committed file at all, and folding")
    print(f"   that into 'agrees' would be a false acquittal — permanent, because nobody re-examines")
    print(f"   a cleared claim.")

    # ⭐⭐ WHY 9 ROUNDS MATCH ON VALUES BUT NOT ON BYTES — measured, not inferred from one case.
    #   Every byte-mismatching round differs by exactly one field, and that field is a PROVENANCE
    #   STAMP: `commit` in some rounds, `head` in others. The artifact records the HEAD hash at run
    #   time, so re-running at a later commit changes it BY CONSTRUCTION.
    #   ⛔ THEREFORE THE BYTE CELL OF THIS SPECIFICATION CURVE IS DEGENERATE FOR STAMPED ROUNDS:
    #   floor == ceiling, it can only ever return `differs`, and §4 says no threshold is admissible
    #   on a degenerate statistic. The VALUE cell is the only admissible one.
    #   ⚠ And the mirror defect: the rounds that DO match on bytes are the ones carrying NO stamp
    #   at all, so they cannot be traced to the commit that produced them by any means.
    STAMPS = ("commit", "head")
    stamped, unstamped = [], []
    for rid, script, art in jobs:
        if not art:
            continue
        b = git_show(str(art.relative_to(ROOT)))
        if b is None:
            continue
        try:
            top = json.loads(b)
        except Exception:
            continue
        (stamped if any(k in top for k in STAMPS) else unstamped).append(rid)
    print(f"\n  ⭐ PROVENANCE STAMP CENSUS — artifacts carrying a `commit`/`head` field: "
          f"{len(stamped)} {stamped}")
    print(f"     artifacts carrying NO stamp, hence untraceable to a producing commit: "
          f"{len(unstamped)} {unstamped}")
    byte_mismatch = [r["round"] for r in ran if not r["matches_committed_bytes"]]
    covered = set(byte_mismatch) <= set(stamped)
    print(f"     every byte-mismatch is a stamped round: {covered}  "
          f"(byte-mismatch {len(byte_mismatch)} of {len(ran)})")

    out = HERE / "results" / "reran_the_flagged.json"
    out.write_text(json.dumps({
        "round": "R1051", "flagged": len(rows), "ran": len(ran), "unverified": len(unver),
        "deterministic": len(det), "nondeterministic": nondet, "drifted": drifted,
        "controls": {"positive_mutation_detected": bool(pos), "negative_identity_equal": bool(neg)},
        "stamp_census": {"stamped": stamped, "unstamped": unstamped,
                         "byte_mismatch": byte_mismatch,
                         "every_byte_mismatch_is_stamped": bool(covered)},
        "detail": rows, "world": world,
        "limitation": "drift shows code and artifact disagree NOW; it cannot say which was right "
                      "when committed",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
