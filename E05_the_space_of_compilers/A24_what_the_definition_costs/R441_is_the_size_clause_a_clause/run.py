"""R441 -- the size line has never had the test that adopted ④ pointed at it. Is it a clause at all?

⛔ WHY. The definition's last line reads *"Its size, under that same judge J, is greater than one;
   sizes 3 to 8 are not distinguishable by this release."* It has **no row in the cost table** and
   **no round since R373**. The remedy that adopted ④ -- *name an admissible object this clause
   EXCLUDES* -- has never been pointed at it, and this document's own ledger says a clause that
   excludes nothing is untested decoration.

⭐ AND THE LINE IS TWO DIFFERENT THINGS, WHICH IS WHY IT SURVIVED UNEXAMINED.
     HALF B  "sizes 3 to 8 are not distinguishable" is a statement about RESOLUTION. It excludes
             nothing BY CONSTRUCTION -- a non-result cannot remove a member. **This is a DERIVATION,
             labelled as one, and it needs no round: half B is a CAVEAT, not a clause.**
     HALF A  "greater than one" does exclude a k=1 core. Whether that exclusion is REDUNDANT --
             whether ②∧③∧④ already removes every k=1 arm -- is a measurement, and it is the round.

ESTIMAND (named before the method)
    REDUNDANT = |{ arms with k == 1 that ②∧③∧④ ADMIT }|
    i.e. the set half A removes and nothing else in the definition does. If it is empty over every
    arm whose k is recoverable, half A costs nothing on this evidence.

IDENTIFICATION
    **k is read from the committed core JSON, never parsed from the arm's NAME.** A name-parse is a
    grep and a grep is an instrument: `random_k12_s0` and `topw_k1` differ by one character, and
    this campaign's ledger has three separate entries for loose patterns returning confident wrong
    answers. Arms with no committed core file have **UNKNOWN k**, are counted as such, and are
    never defaulted to anything.
    ⚠ What is NOT identified: whether a k=1 core could exist that ②∧③∧④ admits. The population is
    the arms this campaign built; absence here is a bound on THEM, not a proof about k=1 cores.

SCOPE  population : arms at judge J with a committed core file and an A2 score
       instrument : the committed judge for ② and ④; file inspection for ③ and for k
       baseline   : ②'s published admit list (R360); ④'s criterion-free bar (R436)
       regime     : home release, judge J = Qwen3.5-2B-Base

WORLDS
    W-DECORATION  REDUNDANT == 0 -> half A removes nothing the other clauses leave. On this evidence
                  it is decoration, and the honest statement is that the size line is a REPORTED
                  PROPERTY of admitted cores, not a criterion they must meet.
    W-REAL        REDUNDANT > 0 -> there is a k=1 arm the other three clauses admit and half A
                  removes. It is a working clause and the table gains a fifth row.
    W-UNTESTABLE  no arm with k == 1 has both a core file and a score -> the question cannot be
                  asked of this evidence at all, which is a fact about the arm space and must be
                  reported as UNVERIFIED rather than as "it excludes nothing".

PREDICTION MATRIX
                   REDUNDANT = 0   REDUNDANT > 0   no k=1 arm scorable
    W-DECORATION        0.9             0.03              0.05
    W-REAL              0.05            0.95              0.02
    W-UNTESTABLE        0.05            0.02              0.93

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    at least one k==1 arm is scorable AND REDUNDANT == 0  -> W-DECORATION
    REDUNDANT > 0                                          -> W-REAL
    no k==1 arm is scorable                                -> W-UNTESTABLE, UNVERIFIED
    a control fails                                        -> UNVERIFIED

CONTROLS
    POSITIVE   k read from the core files must RECOVER the k encoded in names where both exist --
               `oracle_k4` must read k=4, `random_k12_s0` must read k=12. If file-k and name-k
               disagree anywhere, the disagreement is PRINTED and the round stops, because one of
               the two is wrong and I do not get to choose which.
    g=0        an arm with no core file must be reported UNKNOWN, never 0 and never dropped -- a
               missing k silently treated as k=1 would manufacture the very exclusion under test.
    NEGATIVE   the k distribution must have spread. If every arm has the same k, "greater than one"
               is untestable here and the round must say so rather than return a comfortable zero.
    PLACEBO    the count of arms excluded by "k > 0" -- a condition every core meets -- must be 0.

MULTIPLICITY  one count over one population; no selection, no correction owed, stated.
ARTIFACT      results/r441_size_clause.json
IMPOSSIBLE HERE, NAMED
    * whether a k=1 core could exist that the other clauses admit -- requires constructing one,
      which is a generation job with its own assumptions.
    * half B's status as anything but a caveat -- it is a derivation and no measurement changes it.
    * the 3-to-8 bound itself -- R373's job; not re-derived here.

EXIT 0 W-REAL · 1 W-DECORATION · 2 W-UNTESTABLE or UNVERIFIED
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
CLAUSE3_EXCLUDES = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}


def k_from_file(arm: str):
    """k read from the OBJECT. -> int, or None if there is no committed core file."""
    p = SATD / f"core_{arm}.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text())
    except Exception:
        return None
    if isinstance(d, dict):
        vals = list(d.values())
        if not vals:
            return 0
        ks = {len(v) for v in vals if isinstance(v, list)}
        return max(ks) if ks else None
    if isinstance(d, list):
        return len(d)
    return None


def k_from_name(arm: str):
    m = re.search(r"_k(\d+)", arm)
    return int(m.group(1)) if m else None


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    f360 = A24 / "R360_which_clause_is_load_bearing" / "results" / "r360_clause_ledger.json"
    f436 = (A24 / "R436_does_clause_four_exclude_anything_at_home" /
            "results" / "r436_clause4_at_home.json")
    if not (f360.exists() and f436.exists()):
        print("  UNRUNNABLE: R360 or R436 artifact absent. Exit 2, never 0."); return 2
    a360 = json.loads(f360.read_text()); a436 = json.loads(f436.read_text())
    admits2 = set(a360["clause2_admits"])
    scored = {c["arm"]: c for c in a436["cells"] if "08b" not in c["arm"]}

    print("R441 · the size line has never had the test that adopted ④. Is it a clause at all?\n")
    print("  ⭐ THE LINE IS TWO THINGS, which is why it survived unexamined:")
    print("     HALF B  'sizes 3 to 8 are not distinguishable' is a statement about RESOLUTION.")
    print("             A non-result cannot remove a member, so it excludes nothing BY")
    print("             CONSTRUCTION. That is a DERIVATION and it needs no round: half B is a")
    print("             CAVEAT, not a clause.")
    print("     HALF A  'greater than one' does exclude a k=1 core. Whether that is REDUNDANT is")
    print("             a measurement, and it is this round.\n")

    ks, unknown, disagree = {}, [], []
    for arm in sorted(scored):
        kf, kn = k_from_file(arm), k_from_name(arm)
        if kf is None:
            unknown.append(arm); continue
        ks[arm] = kf
        if kn is not None and kn != kf:
            disagree.append((arm, kn, kf))

    # ------------------------------------------------------------------------------- controls
    ok = True
    print(f"  POSITIVE  k read from the OBJECT must recover k encoded in NAMES where both exist:")
    if disagree:
        print(f"            ⛔ {len(disagree)} disagreements: {disagree[:6]}")
        print(f"            one of the two is wrong and I do not get to choose which. Exit 2.")
        ok = False
    else:
        n_both = sum(1 for a in ks if k_from_name(a) is not None)
        print(f"            {n_both} arms carry k in both; 0 disagreements   PASS")

    print(f"  g=0       arms with no committed core file -> UNKNOWN, never 0, never dropped: "
          f"{len(unknown)}")
    if unknown:
        print(f"            {unknown[:8]}{' …' if len(unknown) > 8 else ''}")

    spread = sorted(set(ks.values()))
    neg = len(spread) > 1
    ok &= neg
    print(f"  NEGATIVE  the k distribution must have spread -> k values present {spread}   "
          f"{'PASS' if neg else '⛔ FAIL — half A is untestable if every arm shares a k'}")

    plac = sum(1 for a in ks if ks[a] <= 0)
    ok &= (plac == 0)
    print(f"  PLACEBO   arms excluded by 'k > 0', which every core meets: {plac}, must be 0   "
          f"{'PASS' if plac == 0 else '⛔ FAIL'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r441_size_clause.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ------------------------------------------------------------------------------ the count
    k1 = [a for a in ks if ks[a] == 1]
    print(f"\n  arms with a readable k: {len(ks)} · with k == 1: {len(k1)} {k1}")
    if not k1:
        print(f"\n  WORLD: W-UNTESTABLE")
        print(f"    no arm with k == 1 has both a core file and a score, so the question cannot be")
        print(f"    asked of this evidence. That is a fact about the ARM SPACE and is reported as")
        print(f"    UNVERIFIED — NOT as 'half A excludes nothing', which would be silence dressed")
        print(f"    as a measurement.")
        (RES / "r441_size_clause.json").write_text(json.dumps(
            {"world": "W-UNTESTABLE", "n_with_k": len(ks), "unknown": unknown,
             "k_spread": spread}, indent=1))
        return 2

    rows = []
    for a in k1:
        adm2 = a in admits2
        adm3 = a not in CLAUSE3_EXCLUDES
        adm4 = (a in scored) and (not scored[a]["excluded"])
        rows.append({"arm": a, "k": ks[a], "admits2": adm2, "admits3": adm3, "admits4": adm4,
                     "admitted_by_234": bool(adm2 and adm3 and adm4)})
        r = rows[-1]
        print(f"    {a:<22} k={ks[a]}  ②{'✓' if adm2 else '✗'}  ③{'✓' if adm3 else '✗'}  "
              f"④{'✓' if adm4 else '✗'}  -> {'ADMITTED by ②∧③∧④' if r['admitted_by_234'] else 'already excluded'}")

    REDUNDANT = sum(1 for r in rows if r["admitted_by_234"])
    world = "W-REAL" if REDUNDANT > 0 else "W-DECORATION"
    print(f"\n  arms half A removes that ②∧③∧④ would ADMIT: {REDUNDANT} of {len(k1)}")
    print(f"\n  WORLD: {world}")
    if world == "W-DECORATION":
        print(f"    half A removes nothing the other three clauses leave standing. On this evidence")
        print(f"    it is DECORATION, and the honest restatement is that the size line is a")
        print(f"    REPORTED PROPERTY of admitted cores, not a criterion they must meet.")
        print(f"    ⚠ Bound, not proof: the population is the arms this campaign BUILT. A k=1 core")
        print(f"    that ②∧③∧④ admits may exist and would make half A a clause — constructing one")
        print(f"    is a generation job, and its absence here is a statement about these arms.")
    else:
        print(f"    half A removes {REDUNDANT} arm(s) the other three admit. It is a working clause")
        print(f"    and the cost table gains a fifth row.")

    (RES / "r441_size_clause.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "redundant": REDUNDANT, "k1_arms": k1, "rows": rows,
         "n_with_k": len(ks), "unknown": unknown, "k_spread": spread,
         "half_b": "DERIVATION — a resolution statement excludes nothing by construction"},
        indent=1))
    print(f"\n  artifact -> {(RES / 'r441_size_clause.json').relative_to(ROOT)}")
    return 0 if world == "W-REAL" else 1


if __name__ == "__main__":
    sys.exit(main())
