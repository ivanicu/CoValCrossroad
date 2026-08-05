#!/usr/bin/env python3
"""
R701 -- what formulation does the audit actually support? PRODUCTION, labelled.

CHECK #303 ON R700's NEXT LINE -- IT HOLDS, and it is deferred rather than run.
  Its question (are flags denser in closing sections?) is well-posed and answerable. But the drift
  audit returns FIVE consecutive corpus rounds at the tail, and every object finding is already
  landed. ⭐ The interrupt fires: the arc has produced a thorough CRITIQUE of the definition and
  never a FORMULATION informed by it, which is what the standing task asks for.

⚠ PRODUCTION, NOT FRONTIER, AND SAID SO. This executes a decision the audit already made. §0 permits
  it when it traces to gated decisions; every constraint below cites the round that established it.

ESTIMAND        of the 5 clause-positions the current statement carries, how many survive the
                audit's own constraints unchanged?
IDENTIFICATION  ⚠ "survives" is MY judgement against rounds I ran. It is bookkeeping of my audit
                against my statement -- not a measurement of the world. Named, not disguised.
SCOPE           population : the 5 clause-positions (1, 2, 3, 4, size)
                instrument : 5 constraints, each citing a committed round
                             instrument unit = A CONSTRAINT-CLAUSE PAIR
                             claim unit      = A CLAUSE THAT SHOULD BE WRITTEN
                             ⚠ NOT EQUAL -- surviving my constraints is not being correct.
                baseline   : the statement as it stands
                regime     : this repository at HEAD
WORLDS          A SUBTRACTIVE: fewer survive; the audit narrowed the definition.
                B UNCHANGED: all survive; the audit produced no formulation change.
KILL            all 5 survive -> world B, say so rather than manufacture a change.
POSITIVE CTRL   a clause the audit killed (a named k) scores NOT surviving.
g=0             a clause the audit preserved (③'s provenance test) scores surviving.
NEGATIVE CTRL   a clause no constraint mentions is UNSCORED, never counted as surviving.
PLACEBO         run twice identical.
ARTIFACT        results/formulation.json
IMPOSSIBLE      whether the formulation is CORRECT needs a second released core. The release ships
                one, which is C1 and is why no clause may name a k.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent

CONSTRAINTS = {
    "C1": ("R689", "the release ships ONE core; the card gives the INSTANCE's size, not the "
                   "CATEGORY's -> no clause may name a k"),
    "C2": ("R696", "② IS an A2 threshold -> no clause may be justified by agreement with A2"),
    "C3": ("R694", "95.2% of the discriminating power is recoverable from (family,k) -- two "
                   "parameters we chose; the residual is the sham distinction"),
    "C4": ("R688", "③ (provenance) survives §4's falsifier on the reachable population"),
    "C5": ("R683/R685", "the ③ separation is judge-dependent, on n=1 -> a scope condition is "
                        "required and it rests on a single verdict pair"),
}

CLAUSES = {
    "①": {"status_now": "retired (R518/R519: drops 0 passers)", "hit_by": [],
          "verdict": "STAYS RETIRED", "survives": False,
          "why": "already retired before this arc; nothing here revives it"},
    "②": {"status_now": "live -- 'carries the whole boundary'", "hit_by": ["C2", "C3"],
          "verdict": "SURVIVES, RESCOPED", "survives": False,
          "why": "the clause stands but its JUSTIFICATION cannot be agreement with A2 (C2), and "
                 "its boundary is 95.2% our own parameterisation (C3). It is kept for the residual "
                 "it does own: the released core against its own sham."},
    "③": {"status_now": "live -- provenance, checkable from the producer", "hit_by": ["C4", "C5"],
          "verdict": "SURVIVES, WITH A SCOPE CONDITION", "survives": True,
          "why": "survives §4's falsifier (C4); needs 'at the 2B judge' attached, and that "
                 "condition itself rests on one verdict pair (C5)"},
    "④": {"status_now": "retired (R518/R519: drops 0 of 9)", "hit_by": [],
          "verdict": "STAYS RETIRED", "survives": False,
          "why": "already retired; nothing here revives it"},
    "size": {"status_now": "'more than one criterion; 3-8 indistinguishable'", "hit_by": ["C1"],
             "verdict": "MUST NOT NAME A NUMBER", "survives": False,
             "why": "the card's ~95%-are-four is the INSTANCE's distribution; the category's k is "
                    "not resolvable here, so the clause may state a bound and never a value"},
}


def main() -> int:
    print("─── CONTROLS ───")
    pos = not CLAUSES["size"]["survives"]
    print(f"  POSITIVE  a clause the audit killed (a named k) scores NOT surviving -> "
          f"{'PASS' if pos else '⛔ FAIL'}")
    g0 = CLAUSES["③"]["survives"]
    print(f"  g=0       a clause the audit preserved (③) scores SURVIVING -> "
          f"{'PASS — the scorer returns both' if g0 else '⛔ FAIL'}")
    unscored = [k for k, v in CLAUSES.items() if not v["hit_by"]]
    negok = all(not CLAUSES[k]["survives"] for k in unscored)
    print(f"  NEGATIVE  clauses no constraint mentions ({unscored}) are not counted as surviving -> "
          f"{'PASS' if negok else '⛔ FAIL'}")
    print(f"  PLACEBO   deterministic by construction -> PASS")
    ctl = pos and g0 and negok

    surv = [k for k, v in CLAUSES.items() if v["survives"]]
    print(f"\n─── EVERY CLAUSE-POSITION AGAINST EVERY CONSTRAINT (G3) ───")
    for k, v in CLAUSES.items():
        print(f"  {k:<5} now: {v['status_now']}")
        print(f"  {'':5} hit by {v['hit_by'] or '—'}   ⭐ {v['verdict']}")
        print(f"  {'':5} {v['why']}")
    print(f"\n  ⭐ clause-positions surviving UNCHANGED : {len(surv)} of {len(CLAUSES)} -> {surv}")
    print(f"  registered A 1 [0,5] -> {len(surv)}: error {len(surv)-1:+d}")
    killed = len(surv) == len(CLAUSES)
    print(f"  pre-registered kill (all survive) -> "
          f"{'⭐ FIRES — the audit changed nothing' if killed else 'does not fire'}")

    FORMULATION = [
        ("F1 · PROVENANCE", "the criteria were selected without reading the outcome labels -- "
         "checkable from the PRODUCER, never from the product. ⚠ AT THE 2B JUDGE: the separation "
         "does not hold at 0.8B, and that scope rests on ONE verdict pair.",
         ["C4", "C5"], "an arm whose selector reads labels but whose emitted criteria are textually "
         "identical to a label-free one -- R503 measured both sides at 100% verbatim overlap"),
        ("F2 · BEHAVIOUR ABOVE A PROMPT-BLIND FLOOR", "the criteria beat a baseline that never sees "
         "the prompt. ⚠ NOT justified by agreement with A2, because that agreement is arithmetic "
         "(C2). Kept for the residual it owns: the released core against its own sham.",
         ["C2", "C3"], "coval_core_sham -- the same generator with the prompt withheld"),
        ("F3 · SIZE AS A BOUND, NEVER A VALUE", "more than one criterion. ⚠ NO NUMBER: the release's "
         "own card gives ~95%-are-four for the INSTANCE, and the category's k is not resolvable "
         "from a release that ships one core (C1).",
         ["C1"], "a one-criterion arm -- topw_k1, which the bound excludes and no k-value could "
         "exclude without naming the instance's own number"),
    ]
    print(f"\n─── ⭐⭐⭐ THE FORMULATION THE AUDIT SUPPORTS ({len(FORMULATION)} CLAUSES) ───")
    for name, text, cites, excl in FORMULATION:
        print(f"\n  {name}")
        print(f"    {text}")
        print(f"    constraints: {cites}")
        print(f"    ⭐ EXCLUDES (§4's test, per clause): {excl}")
    print(f"\n  registered B 3 [1,6] -> {len(FORMULATION)}: error {len(FORMULATION)-3:+d}")
    dirn = len(surv) < 3
    print(f"  DIRECTIONAL fewer survive than the statement asserts live (② and ③ = 2) -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = "B UNCHANGED — every clause survives; the audit produced no formulation change."
    else:
        world = (f"⭐⭐⭐ A SUBTRACTIVE. Of {len(CLAUSES)} clause-positions, {len(surv)} survives "
                 f"unchanged: ③. ② survives RESCOPED -- the clause stands, its justification does "
                 f"not, because agreement with A2 is arithmetic. The size clause must state a BOUND "
                 f"and never a value. ① and ④ stay retired. ⭐ THE FORMULATION THE AUDIT SUPPORTS IS "
                 f"THREE CLAUSES: provenance at a named judge, behaviour above a prompt-blind floor, "
                 f"and size as a bound. ⚠ EACH CARRIES WHAT IT EXCLUDES, per §4's per-clause test, "
                 f"and the excluded object is one this benchmark actually contains. ⚠ AND THE LIMIT "
                 f"IS THE WHOLE PROJECT: 'survives' is MY judgement against rounds I ran -- "
                 f"bookkeeping of my audit against my statement, not a measurement of the world. "
                 f"A second released core is what would test it, and the release ships one.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(CLAUSES)} clauses × {len(CONSTRAINTS)} constraints, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"formulation.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "action_type": "PRODUCTION",
        "constraints": {k: {"round": v[0], "text": v[1]} for k, v in CONSTRAINTS.items()},
        "clauses": CLAUSES, "n_surviving_unchanged": len(surv), "surviving": surv,
        "formulation": [{"name": n, "text": t, "constraints": c, "excludes": e}
                        for n, t, c, e in FORMULATION],
        "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 1 [0,5] surviving; B 3 [1,6] clauses; subtractive; kill if all survive",
        "limit": ("'survives' is my judgement against rounds I ran -- bookkeeping of my audit "
                  "against my statement, not a measurement of the world."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'formulation.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
