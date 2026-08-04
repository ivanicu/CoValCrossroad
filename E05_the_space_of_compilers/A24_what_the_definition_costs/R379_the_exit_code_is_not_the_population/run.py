"""R379 — I planned to group ten red gates by exit code. The exit code is not the population.

R378's NEXT said: read what each of the ten red gates says and group by the population it claims to
have lost, with the hypothesis that several are one defect reported ten ways -- "because four of the
ten exit 2 (empty population) and an empty population usually means one moved path rather than ten."

⛔ THAT PLAN HAS A SEARCH INSTRUMENT AT ITS CENTRE AND NO POSITIVE CONTROL. Grouping ten free-text
   failure messages "by the population they say they lost" measures MY VOCABULARY, not the gates'
   populations -- the exact failure this campaign has now logged four times. The remedy the ledger
   demands is to name the instrument's unit and the claim's unit and require them to be equal:
     · the CLAIM's unit is  `the set of files a gate actually examined`
     · a keyword scan's unit is `words I chose to look for`
   Those are not equal, so the keyword plan is abandoned before it is written.

⭐ AND THE OBJECTIVE INSTRUMENT ONLY BECAME ADMISSIBLE TWO ROUNDS AGO. `_isolated.run_isolated`
   records every file a subject opens via a CPython audit hook -- it cannot be fooled by a check that
   computes from an empty list without saying so. It printed "do not use this harness" until R376
   measured that its failing criterion was counting its own probe file, repaired it, and proved the
   repair still fires on a destructive subject (0 tracked vs 95 tracked). This round is the first
   use of that repair for a question it was not repaired for.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES, and the plan
   presumed one answer. `exit 2` is the convention for `empty population`, so IF the convention held,
   every exit-2 gate would read ~0 round artifacts and the partition by exit code and the partition
   by read-set would be the same partition. Nothing forces that: a gate is free to read five hundred
   artifacts and still exit 2 for a reason of its own. Which happens is the measurement.

ESTIMAND        for each of the ten gates red at HEAD: the number of DISTINCT repository files it
                opens, split into round artifacts / assurance files / other, measured by audit hook;
                and whether the partition induced by `exit code` equals the partition induced by
                `reads the corpus or not`.

IDENTIFICATION  Exact per gate -- an audit hook is an enumeration, not a sample. NOT identified:
                whether the files a gate opened are the RIGHT files. That is aiming, and it is a
                different round; this measures that it opened some.
                NOT identified: WHY any gate is red. R374 measured when, R375 which commit, this
                measures what each one reads. None of the three is a diagnosis.

SCOPE           population: the 10 gates whose exit is non-zero at HEAD · instrument: the repaired
                `_isolated` audit-hook harness · baseline: the committed
                `what_each_check_read.json`, produced independently before this question was asked ·
                regime: this tree, this commit.

WORLDS
  W-EXIT-PROXIES-POPULATION  every exit-2 gate reads ~0 round artifacts and every exit-1 gate reads
                             many. The exit code IS a proxy for the population, R378's grouping plan
                             would have worked, and the ten reduce to two causes.
  W-ORTHOGONAL               exit code and read-set cut the ten differently. The exit code carries
                             no information about the population, the grouping plan was wrong at its
                             root, and the useful partition is one no exit code shows.
  W-ALL-READ-EVERYTHING      every gate reads the corpus. Then no gate is failing for want of a
                             population and `empty population` is not among the ten defects at all.

PREDICTION MATRIX
  W-EXIT-PROXIES  -> exit2 gates have ~0 round files; exit1 gates have many; the two partitions agree
  W-ORTHOGONAL    -> at least one exit-2 gate reads the corpus AND at least one exit-1 gate does not
  W-ALL-READ      -> min round-file count across all ten is large

PRE-REGISTERED KILL -- conditional on the controls, never on a count alone.
    if instrument_positive_control_ok and instrument_negative_control_ok and reproduction_ok:
        if min(round_files) > 100                        -> W-ALL-READ-EVERYTHING
        elif every exit2 has ~0 and every exit1 has many -> W-EXIT-PROXIES-POPULATION
        else                                             -> W-ORTHOGONAL, and the crossing gates
                                                            are NAMED, because a partition claim
                                                            without its counterexamples is a story
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.
    `~0` is fixed at ZERO round artifacts before the run, not at a threshold chosen after seeing the
    counts. A gate that opens one round file has not lost its corpus.

CONTROLS
  INSTRUMENT (+)  a gate known to read the corpus (`every_round_reaches_the_readme`, green, iterates
                  every round directory) must show MANY round files. If the harness reports zero
                  there, every zero below is silence.
                  ⛔⛔ ANNOTATION AFTER THE RUN, kept rather than rewritten: THIS CONTROL COULD NOT
                  PASS, and it is the fifth of its kind in this campaign's ledger. It demanded >100
                  round artifacts from a gate that ITERATES round directories and only OPENS each
                  arc's README -- a design ceiling of about 24. The threshold sat above the ceiling,
                  so its failure said nothing about the harness, which is exactly
                  `realstat §4 · control that cannot PASS`. Replaced by a PLANT whose answer is
                  known EXACTLY rather than argued: a probe opening a fixed list of 50 real round
                  artifacts, where the harness must report 50. It does. The old gate is still run
                  and printed as a REFERENCE, never as a criterion, because its number is
                  informative about the gate and uninformative about the instrument.
  INSTRUMENT (-)  a subject that opens nothing (`print('noop')`) must show ZERO. Both directions,
                  because a harness that reported hundreds for everything would pass the positive
                  control and mean nothing.
  REPRODUCTION    the committed `what_each_check_read.json` was produced BEFORE this question was
                  asked, by a different script, for a different purpose. Fresh counts must agree
                  with it in ORDER OF MAGNITUDE per gate -- exact equality is not required and
                  demanding it would be a control that cannot pass, because the corpus has grown by
                  several rounds since it was written.
  EMPTY           if fewer than 8 of the 10 gates are measurable, exit 2. A partition drawn over a
                  population that was lost is the failure this round is about.

MULTIPLICITY    10 gates x 1 measurement, all printed, no threshold on any p-value.
SEEDS           none -- an audit hook is deterministic given the tree.
ARTIFACT        results/r379_read_sets.json with the source hash.

IMPOSSIBLE HERE
  whether the files opened are the RIGHT files  -- aiming, not population. A separate round.
  WHY any gate is red                           -- three rounds have now measured when, which
                                                   commit, and what it reads. None is a diagnosis.
  a second release                              -- one release.

EXIT
    0  controls hold and the partition is classified
    1  a control misbehaved -- UNVERIFIED
    2  too few gates measurable, or the harness is unusable -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
PY = ROOT / ".venv" / "bin" / "python"
PRIOR = ROOT / "assurance" / "results" / "what_each_check_read.json"
sys.path.insert(0, str(ROOT / "assurance"))
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

RED = ["artifacts_are_internally_coherent", "attack_every_check", "attack_no_withdrawn_framings",
       "attack_outcome_variable_declared", "donor_numbers_carry_their_draw_scope", "pueue_wait",
       "readme_row_carries_the_verdict", "seed_filter_is_disclosed", "synthesis_cites_recent_work",
       "verdict_cites_its_own_contrasts"]
POS_CONTROL = "every_round_reaches_the_readme"     # green, iterates every round directory


def main() -> int:
    try:
        from _isolated import ensure_worktree, restore, run_isolated   # noqa: E402
    except Exception as e:
        print(f"  UNRUNNABLE: cannot import the repaired harness ({e}). Exit 2, never 0."); return 2
    if not PY.exists():
        print(f"  UNRUNNABLE: {PY} absent. Exit 2, never 0."); return 2

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R379 · the exit code is not the population   HEAD {head}\n")
    print(f"  ⛔ R378's NEXT planned to group these ten by keyword over their failure text. That is")
    print(f"     a search instrument measuring MY vocabulary, not their populations, so the plan is")
    print(f"     abandoned. The unit measured here is `files the process actually opened`.\n")

    wt = ensure_worktree()
    restore(wt)

    def counts(name):
        rel = f"assurance/{name}.py"
        if not (wt / rel).exists():
            return None
        rc, files, _ = run_isolated(rel)
        rf = [f for f in files if f.startswith("E0") and "/R" in f]
        af = [f for f in files if f.startswith("assurance/") and f != rel]
        of = [f for f in files if not f.startswith("E0") and not f.startswith("assurance/")
              and not f.startswith(".venv")]
        return dict(exit=rc, round_files=len(rf), assurance_files=len(af), other_files=len(of))

    # ---- INSTRUMENT CONTROLS, both directions, before any subject ---------------------------
    # ⛔ v1's POSITIVE CONTROL COULD NOT PASS, and it is the fifth of its kind in this campaign's
    #   ledger. It required `every_round_reaches_the_readme` to show >100 round artifacts. That
    #   gate ITERATES round directories and only OPENS each arc's README, so the design can return
    #   about 24 -- the threshold sat above the ceiling and its failure said nothing about the
    #   harness. `realstat §4 · control that cannot PASS`: compute the ceiling before the threshold.
    #   Replaced with a PLANT whose answer is known exactly rather than argued: a probe that opens
    #   a fixed list of N real round artifacts, where the harness must report N.
    real = sorted(str(q.relative_to(wt)) for q in wt.glob("E0*/*/*/results/*.json"))[:50]
    if len(real) < 20:
        print(f"  UNRUNNABLE: only {len(real)} round artifacts to plant with. Exit 2."); return 2
    probe = "assurance/_r379_probe.py"
    body = ("import pathlib\nR = pathlib.Path(__file__).resolve().parents[1]\n"
            "for rel in %r:\n    (R / rel).read_bytes()\nprint('opened', len(%r))\n"
            % (real, real))
    (wt / probe).write_text(body)
    prc, pfiles, _ = run_isolated(probe, restore_first=False)
    (wt / probe).unlink(missing_ok=True)
    pos_round = len([f for f in pfiles if f.startswith("E0") and "/R" in f])
    pos_ok = (pos_round == len(real))
    # NEGATIVE: the same harness, a subject that opens nothing.
    (wt / probe).write_text("print('noop')\n")
    nrc, nfiles, _ = run_isolated(probe, restore_first=False)
    (wt / probe).unlink(missing_ok=True)
    neg_round = len([f for f in nfiles if f.startswith("E0") and "/R" in f])
    neg_ok = (neg_round == 0)
    pc = counts(POS_CONTROL)
    print("  CONTROLS on the audit-hook harness, before any red gate is measured")
    print(f"    INSTRUMENT (+)  a probe planted to open EXACTLY {len(real)} round artifacts is")
    print(f"                    reported as {pos_round}  {'PASS' if pos_ok else 'FAIL'}")
    print(f"    INSTRUMENT (-)  a `print('noop')` subject opens {neg_round}  "
          f"{'PASS' if neg_ok else 'FAIL'}")
    print(f"    reference       `{POS_CONTROL}` opens "
          f"{pc['round_files'] if pc else 'n/a'} — reported, NOT a criterion: it iterates round")
    print(f"                    directories and only OPENS each arc README, so its ceiling is low")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the harness is blind in one direction. Exit 1."); return 1

    # ---- the ten ------------------------------------------------------------------------------
    print(f"\n  THE TEN RED GATES — measured, not read")
    print(f"    {'gate':<40}{'exit':>6}{'round':>8}{'assur':>7}{'other':>7}   reads the corpus?")
    ROWS = {}
    for g in RED:
        c = counts(g)
        if c is None:
            print(f"    {g:<40}{'—':>6}   ABSENT"); continue
        ROWS[g] = c
        print(f"    {g:<40}{str(c['exit']):>6}{c['round_files']:>8}"
              f"{c['assurance_files']:>7}{c['other_files']:>7}   "
              f"{'YES' if c['round_files'] else 'no — zero round artifacts'}")
    if len(ROWS) < 8:
        print(f"\n  UNRUNNABLE: only {len(ROWS)} of {len(RED)} gates measurable. Exit 2, never 0.")
        return 2

    # ---- REPRODUCTION against an artifact written before this question existed ---------------
    repro, rep_rows = True, {}
    if PRIOR.exists():
        prior = json.loads(PRIOR.read_text()).get("rows", {})
        print(f"\n  REPRODUCTION vs `what_each_check_read.json` — written earlier, by another")
        print(f"  script, for another purpose. Order of magnitude, not equality: the corpus grew.")
        print(f"    {'gate':<40}{'then':>8}{'now':>8}   same order?")
        for g in ROWS:
            was = prior.get(g + ".py", {}).get("round_files")
            if was is None:
                continue
            now = ROWS[g]["round_files"]
            same = (was == 0 and now == 0) or (was > 0 and now > 0 and
                                               0.5 <= (now + 1) / (was + 1) <= 2.0)
            rep_rows[g] = dict(then=was, now=now, same=same)
            repro &= same
            print(f"    {g:<40}{was:>8}{now:>8}   {'yes' if same else 'NO'}")
        print(f"    -> {'PASS' if repro else 'FAIL'}")
    else:
        repro = False
        print(f"\n  REPRODUCTION: prior artifact absent — UNVERIFIED, not a pass.")

    if not repro:
        print("\n  UNVERIFIED — the fresh read-sets do not reproduce the independent prior. Exit 1.")
        return 1

    # ---- the two partitions -------------------------------------------------------------------
    e2 = [g for g in ROWS if ROWS[g]["exit"] == 2]
    e1 = [g for g in ROWS if ROWS[g]["exit"] == 1]
    reads = [g for g in ROWS if ROWS[g]["round_files"] > 0]
    blind = [g for g in ROWS if ROWS[g]["round_files"] == 0]
    e2_reading = sorted(set(e2) & set(reads))
    e1_blind = sorted(set(e1) & set(blind))
    print(f"\n  THE TWO PARTITIONS")
    print(f"    by EXIT CODE : exit1 = {len(e1)}, exit2 = {len(e2)}")
    print(f"    by READ-SET  : reads the corpus = {len(reads)}, opens zero round artifacts "
          f"= {len(blind)}")
    print(f"    exit-2 gates that DO read the corpus : {e2_reading if e2_reading else 'none'}")
    print(f"    exit-1 gates that read NOTHING       : {e1_blind if e1_blind else 'none'}")

    minrf = min(ROWS[g]["round_files"] for g in ROWS)
    print()
    if minrf > 100:
        print(f"  W-ALL-READ-EVERYTHING — the smallest read-set is {minrf} round artifacts, so no")
        print(f"  gate is failing for want of a population and `empty population` is not among the")
        print(f"  ten defects at all.")
        v = "W_ALL_READ_EVERYTHING"
    elif not e2_reading and not e1_blind:
        print(f"  W-EXIT-PROXIES-POPULATION — every exit-2 gate opens zero round artifacts and")
        print(f"  every exit-1 gate reads the corpus. The exit code IS a proxy for the population")
        print(f"  and R378's grouping plan would have worked.")
        v = "W_EXIT_PROXIES_POPULATION"
    else:
        print(f"  W-ORTHOGONAL — the two partitions cut the ten DIFFERENTLY, and the crossing gates")
        print(f"  are named rather than summarised:")
        for g in e2_reading:
            print(f"    · {g} exits 2 and opens {ROWS[g]['round_files']} round artifacts")
        for g in e1_blind:
            print(f"    · {g} exits 1 and opens ZERO")
        print(f"  ⛔ So `exit 2 means it lost its population` is FALSE here, and R378's NEXT rested")
        print(f"     on it. A gate can read five hundred artifacts and still exit 2 for a reason of")
        print(f"     its own, and a gate can read nothing and still exit 1.")
        v = "W_ORTHOGONAL"

    print(f"\n  ⚠ THIS IS NOT A DIAGNOSIS, and three rounds have now stopped short of one on")
    print(f"    purpose: R374 measured WHEN each gate went red, R375 WHICH COMMIT, R379 WHAT EACH")
    print(f"    READS. None of the three says WHY, and stacking them does not either.")
    print(f"  ⚠ AND A ZERO HERE IS NOT A DEFECT. A gate scoped to documents legitimately opens no")
    print(f"    round artifact; whether its read-set matches its intended population is AIMING, a")
    print(f"    different question this round does not touch.")

    art = dict(stamp(str(SELF)), head=head, rows=ROWS, reproduction=rep_rows,
               partitions=dict(exit1=sorted(e1), exit2=sorted(e2), reads=sorted(reads),
                               blind=sorted(blind), exit2_reading=e2_reading,
                               exit1_blind=e1_blind),
               controls=dict(instrument_pos=pos_ok, instrument_neg=neg_ok, reproduction=repro,
                             pos_round_files=pc["round_files"]),
               min_round_files=minrf, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r379_read_sets.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
