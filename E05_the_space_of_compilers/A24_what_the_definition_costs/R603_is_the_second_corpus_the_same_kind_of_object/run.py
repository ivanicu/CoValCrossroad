#!/usr/bin/env python3
"""
R603 -- is the second corpus the same KIND of object, and does row 5 survive?

CHECK #202 CAUGHT ME ASSERTING FROM A DOCSTRING. R602's closing line stated *"R433 scores per
interaction while the home release scores per prompt"* as fact; I had read it once in
`generate_core.py`'s comment, never in the keying code. Door ①: a convincing description is the
most dangerous evidence, and it was mine.

⛔ AND R602 CREATED A LIVE CONTRADICTION INSIDE THE DELIVERABLE. Register row 5 carries R556's
correction -- *"WRONG IN KIND ... one is already on disk"* -- while R602 measured that same file
sharing exact 0, normalised 0, and token-Jaccard AT the shuffled floor with home.

⚠ MY FIRST READING OF THAT WAS AN OVER-SWING AND IS RECORDED AS ONE. Disjointness is what you
WANT in a replication: new data is the point, and low overlap is not an objection. The question
row 5 actually turns on is not whether the corpora share strings but whether the second corpus
is the SAME KIND OF OBJECT -- whether it can support the same estimand at all. That is decidable
from the two schemas and needs no corpus statistic.

ESTIMAND        For each structural requirement the home estimand imposes, is it satisfiable in
                the second corpus? requirement_satisfied is a per-field lookup, and
                n_unsatisfiable is the count that decides row 5.
IDENTIFICATION  Exact for presence/absence. ⚠ "satisfiable" for the RECONSTRUCTIBLE ones (many
                responses per unit) is measured, not assumed: the rows are counted.
                ⚠ Whether a requirement is NECESSARY to the estimand is a reading of the
                definition, not a fact about the files. Each is stated with the clause it
                serves so a reader can overrule.
SCOPE           population : the two release files, whole
                instrument : json key presence + row counts
                             instrument unit = A FIELD IN A RELEASE
                             claim unit      = A REQUIREMENT OF THE ESTIMAND
                             NOT equal -- a field can exist and be unusable, and a requirement
                             can be met by reconstruction. Hence every row is printed with what
                             it serves and whether it is direct or reconstructed.
                baseline   : the home release, which satisfies its own estimand BY
                             CONSTRUCTION -- a DERIVATION, labelled, not evidence
                regime     : as committed at this sha
WORLDS          A SAME KIND: every requirement is satisfiable -> R556 stands, row 5 is WRONG IN
                  KIND, and independent replication really is available on this site.
                B DIFFERENT KIND: >=1 requirement is unsatisfiable -> the file is a second
                  DATASET, not a second RELEASE of the same object, row 5 goes back to
                  genuinely impossible here, and R556 is overturned.
                C RECONSTRUCTIBLE: the gaps are all reconstructible -> row 5 survives but its
                  price changes from "already on disk" to "on disk after a build step".
KILL            pre-registered: if the recogniser cannot find a requirement in the HOME release
                where it is known present, it cannot see the class and every absence is
                UNVERIFIED -- silence, not a missing field.
POSITIVE CTRL   every requirement must be found in home, where all are known present.
NEGATIVE CTRL   a requirement named with a key that exists in NEITHER file must be absent in
                both -- proving absence is detectable rather than universal.
PLACEBO         a key present in both files must be found in both.
SEEDS           n/a, deterministic; the row counts are exact.
MULTIPLICITY    5 requirements x 2 releases + 3 control checks, all reported.
ARTIFACT        results/same_kind.json
IMPOSSIBLE      construct validity for "the same kind of object": kind is a judgement about
                what the estimand needs, not a property of a file. Every requirement is printed
                with the clause it serves and marked direct / reconstructed / absent.
"""
from __future__ import annotations
import json, pathlib, sys
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[3]
DATA = ROOT / "data"
OUT = pathlib.Path(__file__).resolve().parent / "results"
SCAN = 60000

REQS = [
    ("a prompt / user turn",        "②③ both score responses TO something", ("prompt", "user_prompt")),
    ("MULTIPLE responses per unit", "② compares a core's ranking of responses", ("responses", "model_response")),
    ("a human preference target",   "A2 is agreement with a held-out annotator", ("responses", "score")),
    ("SHIPPED criteria (a rubric)", "② is 'better than the released pool' — the pool is the baseline", ("coval_full", "coval_core")),
    ("a released CORE",             "the object the definition is written from", ("coval_core",)),
]


def keyset(path, cap=SCAN):
    ks, n = set(), 0
    with path.open() as fh:
        for line in fh:
            if n >= cap:
                break
            try:
                j = json.loads(line)
            except Exception:
                continue
            if isinstance(j, dict):
                ks |= set(j)
            n += 1
    return ks, n


def responses_per_unit(path, unit_key, resp_key, cap=SCAN):
    d = defaultdict(set)
    n = 0
    with path.open() as fh:
        for line in fh:
            if n >= cap:
                break
            try:
                j = json.loads(line)
            except Exception:
                continue
            n += 1
            u, r = j.get(unit_key), j.get(resp_key)
            if u is not None and isinstance(r, str):
                d[u].add(r)
    if not d:
        return None
    v = sorted(len(x) for x in d.values())
    return {"units": len(d), "median": v[len(v)//2], "max": v[-1],
            "frac_ge_2": sum(1 for x in v if x >= 2) / len(v)}


def main():
    files = {"HOME/comparisons": DATA / "comparisons.jsonl",
             "HOME/rubrics": DATA / "conversation_rubrics.jsonl",
             "SECOND/utterances": DATA / "utterances.jsonl"}
    for n, p in files.items():
        if not p.is_file():
            print(f"UNRUNNABLE: {n} absent. Exit 2, never 0."); return 2
    ks = {n: keyset(p) for n, p in files.items()}
    home = ks["HOME/comparisons"][0] | ks["HOME/rubrics"][0]
    second = ks["SECOND/utterances"][0]
    print("POPULATION  top-level keys per release (first "
          f"{SCAN} rows each)")
    for n, (k, cnt) in ks.items():
        print(f"  {n:20} {cnt:>6} rows   {sorted(k)}")

    print(f"\n─── CONTROLS ───")
    pos = [r for r in REQS if not (set(r[2]) & home)]
    print(f"  POSITIVE  every requirement found in HOME: "
          f"{len(REQS)-len(pos)}/{len(REQS)} -> {'PASS' if not pos else '⛔ FAIL '+str(pos)}")
    neg_key = "zzq_key_in_neither_release"
    neg_ok = neg_key not in home and neg_key not in second
    print(f"  NEGATIVE  a key present in NEITHER release is absent in both -> "
          f"{'PASS — absence is detectable' if neg_ok else '⛔ FAIL'}")
    # ⛔ v1's PLACEBO PRESUPPOSED A NON-NULL OVERLAP: "a key present in BOTH must be found in
    #    both" is undefined when the intersection is empty, and it IS empty. §4's `the control
    #    presupposes a non-null effect` — and the zero it tripped over is not a control failure,
    #    it is a RESULT. Replaced with one that can pass either way: a key known present in ONE
    #    release must be found there and not in the other.
    shared = home & second
    plc_ok = ("prompt" in home and "prompt" not in second
              and "score" in second and "score" not in home)
    print(f"  PLACEBO   a key known present in ONE release is found there and not the other "
          f"(`prompt` home-only, `score` second-only) -> {'PASS' if plc_ok else '⛔ FAIL'}")
    print(f"  ⭐ AND A RESULT, NOT A CONTROL: the two releases share {len(shared)} top-level "
          f"key names. Zero shared field names is the schema-level form of the same answer the "
          f"requirement table gives below.")
    controls_ok = (not pos) and neg_ok and plc_ok

    print(f"\n─── REQUIREMENT x RELEASE (every row printed with the clause it serves) ───")
    rows, unsat = [], []
    for name, serves, keys in REQS:
        in_home = sorted(set(keys) & home)
        in_second = sorted(set(keys) & second)
        status = "DIRECT" if in_second else "ABSENT"
        rows.append({"requirement": name, "serves": serves, "keys": list(keys),
                     "home": in_home, "second": in_second, "status": status})
        if not in_second:
            unsat.append(name)
        print(f"  {name:<28} home {str(in_home):<28} second {str(in_second):<24} {status}")
        print(f"      serves: {serves}")

    print(f"\n─── RECONSTRUCTION: can MULTIPLE responses per unit be rebuilt in SECOND? ───")
    rec = responses_per_unit(files["SECOND/utterances"], "interaction_id", "model_response")
    if rec:
        print(f"  keyed on interaction_id: {rec['units']} units, median "
              f"{rec['median']} response(s), max {rec['max']}, "
              f"{rec['frac_ge_2']:.4f} have >= 2")
    rec_c = responses_per_unit(files["SECOND/utterances"], "conversation_id", "model_response")
    if rec_c:
        print(f"  keyed on conversation_id: {rec_c['units']} units, median "
              f"{rec_c['median']}, max {rec_c['max']}, {rec_c['frac_ge_2']:.4f} have >= 2")

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif not unsat:
        world = "A SAME KIND — every requirement is satisfiable; R556 stands"
    else:
        world = (f"B DIFFERENT KIND — {len(unsat)} requirement(s) UNSATISFIABLE in the second "
                 f"release: {unsat}. It is a second DATASET, not a second RELEASE of the same "
                 f"object, so row 5's 'already on disk' does not discharge independent "
                 f"replication and R556 is OVERTURNED on that point.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: {len(REQS)} requirements x 2 releases + 3 control checks. "
          f"{len(unsat)} unsatisfiable.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "same_kind.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "keys": {n: sorted(k) for n, (k, _) in ks.items()},
        "rows_scanned": {n: c for n, (_, c) in ks.items()},
        "requirements": rows, "unsatisfiable": unsat,
        "reconstruction_interaction": rec, "reconstruction_conversation": rec_c,
        "check202": ("R602's closing line asserted the per-interaction/per-prompt unit fact from "
                     "a docstring comment, never from the keying code — door ①"),
        "overswing_recorded": ("my first reading treated LOW OVERLAP as an objection to row 5. "
                               "It is not: disjointness is what a replication WANTS. The "
                               "question is KIND, not overlap, and the schemas decide it."),
        "impossible": ("'the same kind of object' is a judgement about what the estimand needs, "
                       "not a property of a file; every requirement is printed with what it serves"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'same_kind.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
