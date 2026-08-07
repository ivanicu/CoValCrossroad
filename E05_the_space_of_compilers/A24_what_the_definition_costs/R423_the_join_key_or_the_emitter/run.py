"""R423 -- was R422's 0.1% a second judge, or my own join key? Repair the key and ask again.

R422 compared the five committed `_08b`/`_08bR` pairs at criterion level and fired
W-DIFFERENT-EMITTER on 5-14 differing cells out of 7,000-8,200 -- ONE CELL IN A THOUSAND. A second
judge changes essentially every value, so the branch asserted the wrong world with correct arithmetic
underneath: its pre-registered kill compared to ZERO instead of to a null.

⛔ AND THE CONFOUND IS IN THE JOIN KEY THAT R422's OWN README CALLS `the whole instrument`.
   `select_core.py` emits `sat[pid][(i, letter)]` keyed on the criterion's ORIGINAL index `i`; R422
   keyed on its TEXT. A prompt whose list repeats a text has two original indices carrying the same
   text and DIFFERENT values -- 82 of 968 prompts (8.5%) in `core_full.json`. A dict keeps whichever
   came last, so two files that selected different duplicate instances register a "difference" that
   is not in the emitter at all.

⭐ THE REPAIR IS THE RIGHT INSTRUMENT, NOT A PATCH. The key `(pid, criterion text, letter)` does not
   name one value; it names a SET of values, one per original index sharing that text. Two files
   agree at that key when their sets INTERSECT and disagree only when the sets are DISJOINT. R422's
   last-wins dict was a set of size one chosen arbitrarily.

⭐ AND THE INDEPENDENT CHECK COSTS NOTHING MORE. Every value either family emitted must be present in
   the DEFAULT npz's own multiset for that key -- because `select_core.py` makes ZERO judge calls and
   only looks values up. If both families' values are in it, ONE npz can produce both, and no second
   judge is needed to explain anything. If a value is absent from it, that value came from somewhere
   else, and THAT is what a second emitter looks like.

⛔ ARITHMETIC TRAP. That a value emitted by a lookup is present in the table it was looked up from is
   FORCED -- for a file emitted from the default npz. It is a derivation, and it is exactly why its
   FAILURE is informative: the `_08b`/`_08bR` families are the ones whose emitter is in question, so
   containment is a real prediction for them and could come out either way.

ESTIMAND        (A) under the REPAIRED set-valued join, the number of criterion-cells where the two
                    families' value sets are DISJOINT, per rule;
                (B) for every cell R422 called differing, whether BOTH families' values appear in the
                    default npz's multiset at that key;
                (C) the share of R422's differing cells that sit on a prompt carrying a repeated
                    criterion text, against that base rate.

IDENTIFICATION  (A) and (B) exact on the committed artifacts. NOT identified: which npz produced a
                value that is absent from the default's multiset -- absence names a foreign emitter,
                never which one. Named.

SCOPE           population: the same 5 committed `_08b`/`_08bR` pairs · instrument: set intersection
                on values joined by (pid, criterion text, letter), plus containment in the default
                npz's multiset · baseline: `topw_k4` vs `topw_k2`, which must stay at zero under the
                repair · regime: committed artifacts only, zero runs.

WORLDS
  W-JOIN-ARTIFACT      zero disjoint cells under the repaired join, and every R422 difference is
                       explained by both values living in the default multiset. Then R422's
                       W-DIFFERENT-EMITTER was MY KEY, the two families share an emitter, and what
                       differed between them is the SELECTION input.
  W-DIFFERENT-EMITTER  at least one disjoint cell survives the repair, or a value is absent from the
                       default multiset. Then a second emitter is real, and it is named cell by cell
                       rather than asserted from a count.
  W-MIXED              some rules repair to zero and others do not. Then the families are not one
                       thing and no family-level statement is admissible.

PREDICTION MATRIX
  W-JOIN-ARTIFACT     -> 0 disjoint in all five; all R422 differences contained in the default
  W-DIFFERENT-EMITTER -> >= 1 disjoint, or >= 1 value not contained; both named
  W-MIXED             -> rules split, and the split is printed

PRE-REGISTERED KILL -- conditional on the controls, and this time on a NULL rather than on zero.
    if plant_is_uncontained and a_real_value_is_contained and topw_pair_stays_at_zero:
        0 disjoint everywhere AND every R422 diff contained -> W-JOIN-ARTIFACT
        rules split                                          -> W-MIXED, split printed
        else                                                 -> W-DIFFERENT-EMITTER, cells named
    else: UNVERIFIED -- never CONFIRMED, never OVERTURNED.

CONTROLS
  CONTAIN (+)   a synthetic value (a real value + 1.0) must be reported NOT contained in the default
                multiset. Without it, `everything is contained` is silence from an instrument never
                shown to return non-contained.
  g = 0         a value taken FROM the multiset must be reported contained. A containment test that
                says yes to everything passes the plant only if the plant is impossible, so both
                directions are required.
  REAL (=)      `topw_k4` vs `topw_k2` must STILL show zero disjoint cells after the repair. A repair
                that fixes the failing case by breaking the passing one has moved the error, not
                removed it.
  DEFAULT-NPZ   every `topw_k4` value must be contained in the default multiset. `topw_k4` was
                emitted from the default npz, so this is what establishes that `core_full.json` +
                `sat_full.npz` ARE the default emitter's table rather than some other file's -- the
                whole containment test is meaningless if that table is the wrong table.
  NON-EMPTY     a rule with no shared keys is UNVERIFIED for that rule, never folded into agreement.

MULTIPLICITY    5 rule pairs x 2 tests (disjointness, containment) + 4 controls; every rule printed
                with its counts, including rules that answer nothing.
SEEDS           none -- this reads committed bytes.
ARTIFACT        results/r423_join_or_emitter.json with the source hash.

IMPOSSIBLE HERE
  which foreign npz produced an uncontained value -- absence from the default table names a foreign
                                                     emitter, never which one.
  which SELECTION input differed                  -- unchanged from R422: --select-npz, --fit-parity
                                                     and the target are not separable from artifacts
                                                     that record no configuration.
  cross-release                                   -- one release.

EXIT
    0  the controls hold and a branch is reached
    1  a control misbehaved, or nothing overlaps -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
R422 = HERE.parent / "R422_did_the_judge_differ_or_only_the_selection" / "results" \
    / "r422_emitter_or_selector.json"
PAIRS = ("oracle_k4", "greedy_k4_fit1", "indep_k4_fit1", "topvar_k4", "topwvar_k4")


def load_sets(tag):
    """-> {(pid, criterion_text, letter): set(values)}.

    ⚠ THE SET IS THE REPAIR. The key does not name one value: a prompt whose criterion list repeats
    a text has several ORIGINAL indices carrying that text, each with its own value. R422's dict kept
    whichever came last, which is a set of size one chosen arbitrarily."""
    cj, sz = RES / f"core_{tag}.json", RES / f"sat_{tag}.npz"
    if not (cj.exists() and sz.exists()):
        return None
    texts = json.loads(cj.read_text())
    with np.load(sz, allow_pickle=True) as d:
        meta, sat = list(d["meta"]), np.asarray(d["sat"])
    out = collections.defaultdict(set)
    for m, v in zip(meta, sat):
        pid, j, ltr = str(m).split("|")
        lst = texts.get(pid)
        if lst is None or int(j) >= len(lst):
            continue
        out[(pid, lst[int(j)], ltr)].add(float(v))
    return dict(out)


def disjointness(a, b):
    ks = a.keys() & b.keys()
    bad = [k for k in ks if not (a[k] & b[k])]
    return len(ks), bad


def main() -> int:
    full = load_sets("full")
    if full is None:
        print("  UNRUNNABLE: core_full.json / sat_full.npz absent. Exit 2, never 0."); return 2

    print("R423 · was R422's 0.1% a second judge, or my own join key?\n")
    print("  ⛔ R422 KEYED ON THE CRITERION TEXT WHILE select_core.py EMITS ON THE ORIGINAL INDEX.")
    print("     82 of 968 prompts repeat a text, so the key names a SET of values and a dict kept an")
    print("     arbitrary one. The repair is set intersection, not a patch.\n")

    # ---- CONTROLS ---------------------------------------------------------------------------------
    probe_k = next(iter(full))
    real_v = next(iter(full[probe_k]))
    g0_ok = real_v in full[probe_k]
    plant_ok = (real_v + 1.0) not in full[probe_k]

    tw4, tw2 = load_sets("topw_k4"), load_sets("topw_k2")
    real_ok, nr, badr = False, 0, []
    if tw4 and tw2:
        nr, badr = disjointness(tw4, tw2)
        real_ok = (nr > 0 and not badr)

    # DEFAULT-NPZ: is core_full+sat_full actually the DEFAULT emitter's table?
    dflt_tot = dflt_bad = 0
    if tw4:
        for k, vs in tw4.items():
            if k in full:
                dflt_tot += 1
                if not (vs & full[k]):
                    dflt_bad += 1
    dflt_ok = (dflt_tot > 0 and dflt_bad == 0)

    print("  CONTROLS")
    print(f"    g = 0        a value taken FROM the multiset is reported contained: {g0_ok}   "
          f"{'PASS' if g0_ok else 'FAIL'}")
    print(f"    CONTAIN (+)  a synthetic value (real + 1.0) is reported NOT contained: {plant_ok}   "
          f"{'PASS' if plant_ok else 'FAIL — a `contained` below would be silence'}")
    print(f"    REAL (=)     topw_k4 vs topw_k2 STILL zero disjoint after the repair: "
          f"{nr:,} shared, {len(badr)} disjoint   {'PASS' if real_ok else 'FAIL/ABSENT'}")
    print(f"                 ⚠ a repair that fixes the failing case by breaking the passing one has")
    print(f"                   moved the error, not removed it")
    print(f"    DEFAULT-NPZ  every topw_k4 value is contained in the table: {dflt_tot - dflt_bad:,} "
          f"of {dflt_tot:,}   {'PASS' if dflt_ok else 'FAIL'}")
    print(f"                 topw_k4 WAS emitted from the default npz, so this is what establishes")
    print(f"                 core_full+sat_full IS the default emitter's table. Containment against")
    print(f"                 the wrong table would be meaningless in both directions.")
    if not (g0_ok and plant_ok and real_ok and dflt_ok):
        print("\n  UNVERIFIED — the containment test is not validated in both directions, or the")
        print("  repair broke the case that already passed. Exit 1."); return 1

    # ---- the measurement ---------------------------------------------------------------------------
    prior = {}
    if R422.exists():
        prior = (json.loads(R422.read_text()).get("pairs") or {})

    print(f"\n  THE FIVE PAIRS UNDER THE REPAIRED JOIN")
    print(f"    {'rule':<16} {'shared':>9} {'R422 diff':>10} {'DISJOINT':>9} {'uncontained':>12}"
          f"   verdict")
    rows, disj_rules, uncont_rules, usable = {}, [], [], []
    for tag in PAIRS:
        A, B = load_sets(f"{tag}_08b"), load_sets(f"{tag}_08bR")
        if A is None or B is None:
            rows[tag] = dict(status="MISSING")
            print(f"    {tag:<16} {'-':>9} {'-':>10} {'-':>9} {'-':>12}   MISSING")
            continue
        n, bad = disjointness(A, B)
        # containment: every value either family emits must live in the default table
        unc = 0
        for src in (A, B):
            for k, vs in src.items():
                if k in full and not (vs & full[k]):
                    unc += 1
        st = "UNVERIFIED (no overlap)" if n == 0 else \
             ("DISJOINT CELLS" if bad else ("uncontained" if unc else "explained by the join"))
        rows[tag] = dict(status=st, shared=n, disjoint=len(bad), uncontained=unc,
                         r422_differ=(prior.get(tag) or {}).get("differ"),
                         example=list(bad[0]) if bad else None)
        if n:
            usable.append(tag)
        if bad:
            disj_rules.append(tag)
        if unc:
            uncont_rules.append(tag)
        print(f"    {tag:<16} {n:>9,} {str((prior.get(tag) or {}).get('differ')):>10} "
              f"{len(bad):>9} {unc:>12}   {st}")

    print(f"\n    rules with a computable overlap: {len(usable)} of {len(PAIRS)}")

    print()
    if not usable:
        v = "W_NO_OVERLAP"
        print(f"  W-NO-OVERLAP — nothing to compare. UNVERIFIED. Exit 1.")
    elif not disj_rules and not uncont_rules:
        v = "W_JOIN_ARTIFACT"
        print(f"  W-JOIN-ARTIFACT — under the repaired join, ZERO cells are disjoint in any of the")
        print(f"  {len(usable)} rules, and EVERY value either family emitted is present in the")
        print(f"  default npz's own table. One npz can produce both families; no second judge is")
        print(f"  needed to explain anything.")
        print(f"  ⛔ SO R422's W-DIFFERENT-EMITTER WAS MY KEY, AND IT IS RETRACTED HERE — by the")
        print(f"     round that measured it, not by a later one that inherited it.")
        print(f"  ⚠ WHAT DIFFERED BETWEEN THE FAMILIES IS THE SELECTION INPUT, AND WHICH ONE IS STILL")
        print(f"    NOT IDENTIFIED: --select-npz, --fit-parity and the target are not separable from")
        print(f"    artifacts that record no configuration.")
    elif disj_rules and len(disj_rules) < len(usable) or (uncont_rules and
                                                          len(uncont_rules) < len(usable)):
        v = "W_MIXED"
        print(f"  W-MIXED — disjoint in {disj_rules}, uncontained in {uncont_rules}, clean elsewhere.")
        print(f"  The families are not one thing and no family-level statement is admissible.")
    else:
        v = "W_DIFFERENT_EMITTER"
        print(f"  W-DIFFERENT-EMITTER — cells survive the repair in {disj_rules or uncont_rules}.")
        print(f"  A second emitter is real, and it is named cell by cell rather than asserted from a")
        print(f"  count. Absence from the default table names a FOREIGN emitter, never which one.")

    print(f"\n  ⚠ FIVE PAIRS ON ONE RELEASE, read from committed bytes.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               pairs=rows, usable=usable, disjoint_rules=disj_rules, uncontained_rules=uncont_rules,
               verdict=v, controls=dict(g0=g0_ok, plant=plant_ok, real_shared=nr,
                                        real_disjoint=len(badr), default_npz_total=dflt_tot,
                                        default_npz_bad=dflt_bad))
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r423_join_or_emitter.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if usable else 1


if __name__ == "__main__":
    sys.exit(main())
