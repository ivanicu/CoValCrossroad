#!/usr/bin/env python3
"""R833 -- the wall had a construction record behind it.

See PREREGISTRATION.txt, committed before this file was executed.

ESTIMAND        for each arm ③ returns UNKNOWN: does a construction record exist, and does it
                decide ③? The record is the commit that INTRODUCED the arm's core file -- P1/L79's
                own discipline, applied to every commit this campaign has made.
IDENTIFICATION  identified where a record exists and names the inputs. Where it is silent the arm
                stays UNDECIDED; where no introducing commit is reachable it is NO-RECORD, a
                distinct status.
SCOPE           population: the 11 arms ③ returns UNKNOWN over R831's 93. instrument: git log
                --diff-filter=A on core_<arm>.json + the rule below. regime: provenance by record.
WORLDS          W-RECORD-EXISTS (>=1 decided -- the wall is FALSE) vs W-WALL-STANDS (none decided).
KILL            CONDITIONAL. Evaluated only if the positive control returns a decision that is NOT
                admitted, the negative returns UNDECIDED, and g=0 is identical.
POSITIVE CTRL   `coval_core` -- known EXCLUDED by R475. If the rule returns ADMITTED for it, the
                rule is over-firing toward the flattering answer and nothing else counts.
NEGATIVE CTRL   a synthetic record naming no inputs must return UNDECIDED.
⚠ CONFOUND      I am reading MY OWN commit messages. The rule is fixed in source below, before any
                record was read, and every decisive sentence is QUOTED into the artifact so a later
                reader can overturn the reading without re-running.
ARTIFACT        results/r833_records.json with the decisive quote per arm and a source hash.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parent.parent
RES = HERE / "results"
sys.path.insert(0, str(ROOT / "assurance"))
import clause3_as_written as C3                                            # noqa: E402

# ---- THE RULE, FIXED BEFORE ANY RECORD WAS READ (see PREREGISTRATION.txt) -------------------
LABEL_INPUT = re.compile(
    r"(human (importance|label|rating|score|rank)|annotator|average rating|"
    r"highest[- ]rated|mean importance|rubric item|coval_full|the rubric\b)", re.I)
NAMES_INPUTS = re.compile(
    r"(built from|generated from|written from|identical on every prompt|"
    r"the prompt'?s own|use the prompt|criteria drawn|four generic|no counterpart|"
    r"never (having )?seen|drawn at random|from the conversation)", re.I)


def decide(record: str):
    """-> (status, decisive quote). Silence is UNDECIDED, never a guess in either direction."""
    if not record.strip():
        return "NO-RECORD", ""
    for line in [l.strip() for l in record.splitlines() if l.strip()]:
        if NAMES_INPUTS.search(line):
            return ("EXCLUDED" if LABEL_INPUT.search(line) else "ADMITTED"), line[:200]
    for line in [l.strip() for l in record.splitlines() if l.strip()]:
        if LABEL_INPUT.search(line):
            return "EXCLUDED", line[:200]
    return "UNDECIDED", ""


def record_of(arm: str) -> str:
    f = ROOT / "corebench" / "results" / f"core_{arm}.json"
    if not f.exists():
        return ""
    sha = subprocess.run(["git", "log", "--diff-filter=A", "--format=%h", "--", str(f)],
                         cwd=ROOT, capture_output=True, text=True).stdout.split()
    if not sha:
        return ""
    return subprocess.run(["git", "log", "-1", "--format=%s%n%b", sha[-1]],
                          cwd=ROOT, capture_output=True, text=True).stdout


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    print("\n  R833 · DID THE WALL HAVE A RECORD BEHIND IT?\n")

    # ---- controls ------------------------------------------------------------------------
    pos_rec = ("the release's own dataset card says it aims to select up to four rubric items "
               "with the highest average ratings")
    pos_status, pos_q = decide(pos_rec)
    pc = pos_status not in ("ADMITTED",) and pos_status != "NO-RECORD"
    print(f"  POSITIVE  `coval_core`-style record (dataset card, known EXCLUDED by R475) -> "
          f"{pos_status}   {'PASS' if pc else '⛔ FAIL — over-fires toward the flattering answer'}")
    neg_status, _ = decide("a commit that says nothing about how anything was built")
    nc = neg_status == "UNDECIDED"
    print(f"  NEGATIVE  a record naming no inputs -> {neg_status}   "
          f"{'PASS' if nc else '⛔ FAIL'}")

    d = json.loads(next(A24.glob("R436_*/results/r436_clause4_at_home.json")).read_text())
    a2 = {c["arm"]: c["a2"] for c in d["cells"]}
    order = sorted(a2, key=lambda a: -a2[a])
    rank = {a: i + 1 for i, a in enumerate(order)}
    _, _, unk = C3.partition(list(a2))

    r1 = {a: record_of(a) for a in sorted(unk)}
    r2 = {a: record_of(a) for a in sorted(unk)}                # the producer, invoked TWICE
    g0 = r1 == r2
    print(f"  g=0       record extraction run twice -> "
          f"{'identical   PASS' if g0 else '⛔ FAIL — nondeterministic'}")

    rows = {}
    for a in sorted(unk, key=lambda x: rank[x]):
        st, q = decide(r1[a])
        rows[a] = {"status": st, "rank": rank[a], "a2": a2[a], "quote": q}
    print(f"\n  the {len(unk)} arms ③ returns UNKNOWN, decided by their construction record:\n")
    print(f"  {'arm':<20}{'rank':>6}{'A2':>9}   {'by record':<11} decisive sentence")
    for a, r in rows.items():
        print(f"  {a:<20}{r['rank']:>6}{r['a2']:>9.4f}   {r['status']:<11} {r['quote'][:64]}")

    decided = {a: r for a, r in rows.items() if r["status"] in ("ADMITTED", "EXCLUDED")}
    controls_ok = pc and nc and g0
    if not controls_ok:
        world, verdict = "UNVERIFIED", "a control is unfit; the wall is left as published"
    elif decided:
        world = "W-RECORD-EXISTS"
        adm = [a for a, r in decided.items() if r["status"] == "ADMITTED"]
        best = min((rows[a]["rank"] for a in adm), default=None)
        verdict = (f"{len(decided)} of {len(unk)} UNKNOWN arms are decided by a record already in "
                   f"the repository -- THE WALL IS FALSE. {len(adm)} decide ADMITTED, best at "
                   f"rank {best}")
    else:
        world, verdict = "W-WALL-STANDS", "no UNKNOWN arm is decided by a record; the wall holds"
    print(f"\n  VERDICT: {world} -- {verdict}\n")
    print("  ⚠ This round does NOT change ③'s committed partition or DEFINITION.md's three-valued")
    print("     discipline. It reports what the RECORDS say beside them. Reclassification is a")
    print("     separate decision this round only supplies evidence for.")
    print("  ⚠ A record for an arm I BUILT is a record of my own ACTION. `coval_core` is someone")
    print("     else's object and correctly required the RELEASE's dataset card (R475).\n")

    out = {"world": world, "verdict": verdict, "arms": rows,
           "n_unknown": len(unk), "n_decided": len(decided),
           "controls": {"positive_coval_core_style": pos_status, "positive_ok": pc,
                        "negative_silent_undecided": nc, "g0_extraction_identical": g0},
           "rule": {"names_inputs": NAMES_INPUTS.pattern, "label_input": LABEL_INPUT.pattern},
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r833_records.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r833_records.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
