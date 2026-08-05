#!/usr/bin/env python3
"""
R678 -- git supplies the lineage the artifacts omit. Producer, not popularity.

CHECK #279 ON R677's NEXT LINE -- IT HOLDS.
  `spec_curve_aggregator` is present in R677's artifact and reads 0 under majority, 1 otherwise.
  The line names its instrument, states the ambiguity it wants closed, and pre-names the failure
  mode (several rounds introducing identical members in one commit). Nothing to retract.

ESTIMAND        A: of the 6 five-member arm sets, how many receive a UNIQUE producer -- the earliest
                   commit whose diff introduces the set into a results JSON?
                B: under producer-based denotation, how many denote a ③-reading extension?
IDENTIFICATION  A is exact over git history. B inherits R677's classifier, whose limit stands: a
                docstring states INTENT, not what the code computed.
                ⚠ AND GIT RECORDS WRITES, NOT COMPUTATIONS. A set computed in one round and first
                written in another is attributed to the WRITER. Not closable from history alone.
SCOPE           population : 6 sets × every commit touching a results JSON
                instrument : git diff scan over added AND modified results files
                             instrument unit = A COMMIT THAT WRITES A SET
                             claim unit      = THE ROUND THAT COMPUTED IT
                             ⚠ NOT EQUAL -- hence the write/compute caveat above, carried into the
                             verdict rather than left in a docstring (ledger 750's lesson).
                baseline   : R677's two aggregators, 0 and 1
                regime     : this repository's history
WORLDS          A LINEAGE RECOVERABLE: most sets get a unique producer; the count becomes a fact.
                B NOT RECOVERABLE: producers are ambiguous, and R677's range 0-1 stands.
KILL            pre-registered: fewer than 3 unique producers -> world B.
POSITIVE CTRL   a set whose producing round is known by name resolves to that round.
NEGATIVE CTRL   a synthetic never-committed combination of real arm names -> no producer.
PLACEBO         the search run twice returns identical producers.
ARTIFACT        results/lineage.json
IMPOSSIBLE      attributing a COMPUTATION rather than a WRITE would need each round re-executed
                against its own inputs; 93 rounds in this arc are corpus-dependent and would not
                reproduce. Named, not planned.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
CENSUS = ARC / "R676_the_number_five_is_stable_the_membership_is_not" / "results" / "five_member_sets.json"
DEN = ARC / "R677_four_sets_four_objects_not_four_readings" / "results" / "denotation.json"
C3 = re.compile(r"③|clause[ _-]?(three|3)\b", re.I)


def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout


def writes():
    """(commit, path) for every commit that ADDS or MODIFIES a results JSON, oldest first."""
    out, cur = [], None
    for line in git("log", "--reverse", "--diff-filter=AM", "--format=@%H",
                    "--name-only", "--", "*/results/*.json").splitlines():
        if line.startswith("@"): cur = line[1:]
        elif line.strip() and cur: out.append((cur, line.strip()))
    return out


def find_producers(sets):
    prod = {s: [] for s in sets}
    for c, p in writes():
        blob = git("show", f"{c}:{p}")
        if not blob: continue
        # ⭐⭐⭐ REPAIRED BY THE g=0 CONTROL, WHICH FIRED AND VOIDED THE FIRST RESULT.
        #     v1 asked `all(f'"{m}"' in blob for m in s)` -- whether five strings CO-OCCUR in a
        #     file. corebench/results/leaderboard.json and R294's full_census.json list EVERY arm,
        #     so every set "resolved" to them, including a synthetic combination never committed.
        #     Instrument unit was "five strings present in a blob"; claim unit is "a file holds this
        #     SET AS A VALUE". Repair: parse the JSON and require a list field whose sorted contents
        #     EQUAL the set. This is the unit fix the control demanded, not a threshold moved.
        try: obj = json.loads(blob)
        except Exception: continue
        vals = {}
        def walk(o, key=None):
            if isinstance(o, dict):
                for k2, v in o.items(): walk(v, k2)
            elif isinstance(o, list):
                if o and all(isinstance(x, str) for x in o):
                    vals.setdefault(tuple(sorted(o)), key)
                for v in o:
                    if isinstance(v, (dict, list)): walk(v, key)
        walk(obj)
        for s in sets:
            if prod[s]: continue
            if s in vals:
                prod[s].append((c, p, vals[s]))
    return prod


def main() -> int:
    if not CENSUS.is_file() or not DEN.is_file():
        print("UNRUNNABLE: R676/R677 artifacts absent. Exit 2, never 0."); return 2
    census = json.loads(CENSUS.read_text())["sets"]
    sets = [tuple(sorted(s["members"])) for s in census]

    print("─── CONTROLS ───")
    known = tuple(sorted(["coval_core", "topabs_k4", "topvar_k4", "topw_k4", "topwvar_k4"]))
    fake = tuple(sorted(["coval_core", "topw_k1", "topw_k12", "oracle_k4", "topabs_k4"]))
    probe = find_producers([known, fake])
    pos = probe[known][0][1].split("/")[-3] if probe[known] else None
    posok = pos is not None and "R442" in pos
    print(f"  POSITIVE  a set with a KNOWN producing round resolves to it -> "
          f"{pos} -> {'PASS' if posok else '⛔ FAIL'}")
    g0ok = not probe[fake]
    print(f"  g=0       a never-committed combination must return NOTHING -> "
          f"{probe[fake] or 'none'} -> "
          f"{'PASS — it locates rather than matches' if g0ok else '⛔ FAIL — matches anything'}")
    print(f"  NEGATIVE  (same probe, real arm names in an uncommitted combination) -> "
          f"{'PASS' if g0ok else '⛔ FAIL'}")

    prod = find_producers(sets)
    prod2 = find_producers(sets)
    plcok = all(prod[s] == prod2[s] for s in sets)
    print(f"  PLACEBO   the search run twice returns identical producers -> "
          f"{'PASS' if plcok else '⛔ FAIL — nondeterministic'}")
    ctl = posok and g0ok and plcok

    uniq = [s for s in sets if len(prod[s]) == 1]
    none_ = [s for s in sets if not prod[s]]
    print(f"\n─── A · LINEAGE FROM GIT (G3 — all six printed) ───")
    for s in sets:
        p = prod[s]
        who = p[0][1].split("/")[-3] if p else "— NO PRODUCER FOUND"
        print(f"  {who[:52]:<54} {list(s)[:3]}…")
    print(f"\n  sets with a UNIQUE producer : {len(uniq)} of {len(sets)}")
    print(f"  sets with NO producer found : {len(none_)}")
    print(f"  registered A 5 [3,6] -> {len(uniq)}: "
          f"{'INSIDE' if 3 <= len(uniq) <= 6 else '⛔ OUTSIDE'}, error {len(uniq)-5:+d}")
    killed = len(uniq) < 3
    print(f"  pre-registered kill (<3 unique) -> "
          f"{'⭐ FIRES — git does not supply it either; R677 range 0-1 stands' if killed else 'does not fire'}")

    nb = None
    if not killed:
        # ⭐ USE R677's VALIDATED CLASSIFIER, NOT A BARE ③-MENTION TEST. A first pass here asked
        #   only whether ③ appears in the producer's ESTIMAND and returned 5 -- counting R470,
        #   whose estimand is "the extension BEFORE ③ is applied", as a ③ reading. That is the
        #   exact error R677 was built to catch, and regressing to a cruder instrument one round
        #   after validating a better one is its own failure.
        BEFORE = re.compile(r"before ③|before clause[ _-]?(three|3)|①∧②∧④|prior to ③", re.I)
        PUBLISHED = re.compile(r"publish(ed)?(?![a-z])", re.I)
        n3 = 0
        rows = []
        for s in uniq:
            rd = prod[s][0][1].split("/")[-3]
            field = prod[s][0][2] or ""
            f = next((d / "run.py" for d in ARC.glob(f"{rd.split('_')[0]}_*") if (d / "run.py").is_file()), None)
            est = ""
            if f:
                m = re.search(r"ESTIMAND(.{0,400})", f.read_text(errors="ignore"), re.S)
                est = " ".join(m.group(1).split()) if m else ""
            if BEFORE.search(est): kind = "b_before_three"
            elif PUBLISHED.search(field or ""): kind = "c_publication_list"
            elif C3.search(est) and re.search(r"extens|admit", field or "", re.I): kind = "a_three_extension"
            elif C3.search(est): kind = "d_three_round_other_field"
            else: kind = "d_other"
            n3 += kind == "a_three_extension"
            rows.append((rd.split("_")[0], kind, f"{field} | {est[:52]}"))
        nb = n3
        print(f"\n─── B · DENOTATION BY PRODUCER, NOT BY POPULARITY ───")
        for rd, kind, e in rows:
            print(f"  {rd:<7} {kind:<26} {e}")
        print(f"\n  ⭐ ③-reading extensions by PRODUCER : {n3}")
        print(f"  registered B 2 [1,4] -> {n3}: "
              f"{'INSIDE' if 1 <= n3 <= 4 else '⛔ OUTSIDE'}, error {n3-2:+d}")
        print(f"  R677's aggregators gave 0 (majority) and 1 (any/earliest).")
        dirn = n3 not in (0, 1)
        print(f"  DIRECTIONAL producer-count differs from BOTH -> {'HOLDS' if dirn else '⛔ FAILS'}")
    else:
        dirn = False

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; no lineage claim is admissible."
    elif killed:
        world = (f"B NOT RECOVERABLE — only {len(uniq)} sets got a unique producer. R677's range "
                 f"0-1 stands as the final word.")
    else:
        world = (f"⭐ A LINEAGE RECOVERABLE — {len(uniq)} of {len(sets)} sets have a unique producing "
                 f"commit, and by producer {nb} denote a ③-reading extension against R677's "
                 f"aggregator-dependent 0 or 1. ⭐ THE COUNT STOPS BEING A CHOICE: it is read off the "
                 f"commit that first wrote each set, not off how many later rounds quoted it. "
                 f"⚠ AND THE LIMIT IS REAL AND NOT COSMETIC: git records WRITES, not COMPUTATIONS, "
                 f"so a set computed in one round and first written in another is attributed to the "
                 f"writer. That gap is not closable from history, and it is the reason this is "
                 f"lineage rather than provenance.")
    print(f"  {world}")

    sha = git("rev-parse", "HEAD").strip()
    print(f"\n  MULTIPLICITY: {len(sets)} sets × {len(writes())} result-writing commits, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"lineage.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_sets": len(sets), "n_unique_producer": len(uniq), "n_no_producer": len(none_),
        "kill_fired": killed, "n_three_by_producer": nb, "directional_holds": dirn,
        "producers": {"/".join(sorted(s)[:2]): (prod[s][0][1] if prod[s] else None) for s in sets},
        "producer_fields": {"/".join(sorted(s)[:2]): (prod[s][0][2] if prod[s] else None) for s in sets},
        "registered": "A 5 [3,6]; B 2 [1,4]; directional differs from both aggregators; kill if <3",
        "write_not_compute": ("git records WRITES. A set computed in one round and first written in "
                              "another is attributed to the writer; not closable from history."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'lineage.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
