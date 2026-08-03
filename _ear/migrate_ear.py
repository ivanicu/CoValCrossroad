#!/usr/bin/env python3
"""_ear/migrate_ear.py -- make the E/A/R layout obey its own rules.

WHY, AND ALL FOUR DEFECTS ARE MEASURED, NOT ASSERTED.
Ivan, 2026-08-03: "A should be CONTINUOUS numbering, not reset for each E; and an A should be
made of MULTIPLE R's."  Auditing against that found four things, in increasing severity:

  1. A RESTARTS AT A01 IN ALL FIVE EPOCHS.  `A01` names five different decisions, so an arc id
     is not a key. 30 arc directories, 5 collisions of the name `A01` alone.

  2. SEVEN ARCS HOLD EXACTLY ONE ROUND.  P16 says an arc closes when a DECISION becomes safe and
     is composed of several belief updates. A one-round arc is a round wearing an arc's clothes.

  3. E05 SKIPS A14 AND A15.  It runs A01..A13 then A16. The gap is not a record of anything.

  4. ⛔ SIX ROUND IDS NAME TWO DIFFERENT ROUNDS EACH.  R277..R282 exist under BOTH
     `A13_is_the_admissibility_gate_the_right_gate` AND `A16_what_the_definition_costs`, and they
     are NOT copies -- different questions, different run.py, different results files:
         R277  is_necessity_tolerance_free          | the_mde_of_the_design_that_priced_it
         R278  can_the_admissibility_gate_ever_fire | is_the_boundary_resolvable
         R279  was_the_gate_violated_by_its_own_...| what_would_resolve_the_boundary
         R280  is_the_gate_unit_coherent            | the_table_at_every_annotator
         R281  does_the_coherent_gate_admit_this... | a_size_matched_neutral_arm
         R282  is_the_saturation_forced_by_sample...| neutral_clause_at_matched_k4
     89 round directories in E05, 83 distinct ids. **A round id is the key for one belief update
     and twelve updates were sharing six keys.** Every citation of `R281` in this repo -- and I
     made several this session, including one in a published file -- was ambiguous and nobody
     could have known from the id alone.

  WHO KEEPS THE ID: first claim wins, by git. A13's set was first committed 07:16-07:51; A16's
  duplicates at 10:34-10:47, about three hours later. So A16's six are the invalid claim and get
  fresh ids R303..R308. The rule does not depend on which arc I happen to be working in today.
  Checked before choosing: 0 citations of these ids exist outside this repo, so the renumber is
  contained.

WHAT THIS SCRIPT DOES NOT DO: it does not delete anything (L81 -- mv, never rm) and it does not
rewrite git history. Commit messages that cite an old id stay wrong; REMAP.tsv is what makes them
resolvable, and that is the honest repair for an immutable record.
"""
from __future__ import annotations
import pathlib, subprocess, sys, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ── the new global arc table ────────────────────────────────────────────────────────────────
# (new_arc_id, epoch_dir_prefix, arc_slug, [round ids])  -- rounds listed = the arc's whole
# membership, so a round in two arcs is impossible by construction and the check below proves it.
def rr(a, b):
    return [f"R{i:02d}" for i in range(a, b + 1)]

ARCS = [
    # E01
    ("A01", "E01", "can_this_release_be_analysed_at_all",            rr(1, 5)),
    ("A02", "E01", "which_aggregation_rule",                         rr(6, 9)),
    ("A03", "E01", "is_the_attribution_real_and_against_what_floor",  rr(10, 22)),
    # E02
    ("A04", "E02", "structured_plurality_or_reliability",            rr(23, 32)),
    ("A05", "E02", "what_coval_core_mechanically_is",                rr(33, 37)),
    ("A06", "E02", "does_the_protocol_have_the_power_it_needs",      rr(38, 45)),
    # E03
    ("A07", "E03", "can_a_local_judge_be_an_instrument",             rr(46, 59)),
    ("A08", "E03", "what_floor_each_counterfactual_requires",        rr(60, 72)),
    ("A09", "E03", "can_direction_be_read_from_text_alone",          rr(73, 84)),
    ("A10", "E03", "what_the_resampling_unit_is",                    rr(85, 99)),
    ("A11", "E03", "how_wide_every_interval_really_is",              rr(100, 109)),
    # E04
    ("A12", "E04", "who_pays_for_compilation",                       rr(110, 141)),
    ("A13", "E04", "the_chain_from_a_person_to_the_standard",        rr(142, 165)),
    ("A14", "E04", "do_our_own_claims_survive_an_adversary",         rr(166, 205)),
    # MERGE: old E04/A04 (R206-218, is the detection design well defined) + old E04/A05 (R219,
    # can a stranger check it, ONE round). Same decision -- is the design well posed and
    # checkable by someone who was not here -- and the second had no business being its own arc.
    ("A15", "E04", "is_the_detection_design_well_defined_and_checkable", rr(206, 219)),
    # E05 -- regrouped from FOURTEEN arcs (seven of them singletons) into NINE, by decision.
    # MERGE: old A01+A02+A03. One decision: what a compiler is and what its operations cost.
    ("A16", "E05", "what_a_compiler_is_and_what_its_operations_cost", rr(220, 223)),
    ("A17", "E05", "which_definitions_of_core_are_identifiable",
     ["R224", "R225", "R226", "R227", "R228", "R230", "R231", "R237", "R239"]),
    ("A18", "E05", "the_candidate_set_wall_was_wrong",               ["R233", "R238", "R241"]),
    ("A19", "E05", "triple_blind",                                   ["R234", "R235", "R243"]),
    ("A20", "E05", "is_a_global_core_real",                          ["R240", "R246", "R247"]),
    ("A21", "E05", "missing_weight_semantics",                       ["R244", "R245"]),
    # MERGE: old A05 (how i build controls, R229) + A06 (the walls this arc asserted, R232)
    # + A09 (the certificate, R236) + A11 (does E05 meet its own standard, R242).
    # Four singleton/near-singleton arcs that were all the same decision: does this arc's own
    # METHOD hold up? Grouping them is what makes the object arcs above orthogonal to method.
    ("A22", "E05", "does_this_epochs_own_method_hold_up",            ["R229", "R232", "R236", "R242"]),
    ("A23", "E05", "is_the_admissibility_gate_the_right_gate",
     rr(248, 275) + ["R277", "R278", "R279", "R280", "R281", "R282", "R283"]),
    ("A24", "E05", "what_the_definition_costs",
     ["R276"] + rr(284, 302) + ["R303", "R304", "R305", "R306", "R307", "R308"]),
]

# the six invalid claims: old id (under the OLD A16 dir) -> new id
COLLISION = {"R277": "R303", "R278": "R304", "R279": "R305",
             "R280": "R306", "R281": "R307", "R282": "R308"}
COLLIDED_ARC = "A16_what_the_definition_costs"     # the LATER claimant, by git


def sh(*a):
    return subprocess.run(a, cwd=ROOT, capture_output=True, text=True)


def main():
    apply = "--apply" in sys.argv
    epochs = {p.name[:3]: p.name for p in ROOT.glob("E0*") if p.is_dir()}

    # ── locate every existing round directory, keyed by (arc_dir, round_id) ──────────────────
    existing = {}                       # (epoch, arcdir, rid) -> Path
    for rd in sorted(ROOT.glob("E0*/A*/R*")):
        if not rd.is_dir():
            continue
        rid = rd.name.split("_")[0]
        existing[(rd.parts[-3][:3], rd.parts[-2], rid)] = rd
    print(f"  {len(existing)} round directories on disk")

    # ── build the move list ─────────────────────────────────────────────────────────────────
    moves, unclaimed = [], dict(existing)
    for new_a, ep, slug, rids in ARCS:
        for rid in rids:
            src_rid = {v: k for k, v in COLLISION.items()}.get(rid, rid)
            cands = [(k, v) for k, v in unclaimed.items() if k[0] == ep and k[2] == src_rid]
            if rid in COLLISION.values():
                cands = [c for c in cands if c[0][1] == COLLIDED_ARC]
            elif src_rid in COLLISION:
                cands = [c for c in cands if c[0][1] != COLLIDED_ARC]
            if not cands:
                print(f"  ⚠ {new_a} wants {ep}/{rid} and it is not on disk — MISSING, not skipped")
                continue
            if len(cands) > 1:
                print(f"  ⚠ {ep}/{rid} still ambiguous after the collision rule: "
                      f"{[c[0][1] for c in cands]}")
                return 2
            key, src = cands[0]
            del unclaimed[key]
            tail = src.name.split("_", 1)[1] if "_" in src.name else ""
            dst = ROOT / epochs[ep] / f"{new_a}_{slug}" / f"{rid}_{tail}"
            if src != dst:
                moves.append((src, dst))

    # ── the orthogonality proof, BEFORE anything is moved ───────────────────────────────────
    dsts = [d for _, d in moves]
    dup = [k for k, v in collections.Counter(d.name.split("_")[0] + "|" + d.parts[-3]
                                             for d in dsts).items() if v > 1]
    print(f"\n  planned moves            : {len(moves)}")
    print(f"  round dirs left UNCLAIMED: {len(unclaimed)}  "
          f"{[f'{k[1]}/{k[2]}' for k in list(unclaimed)[:6]]}")
    print(f"  duplicate (epoch,id) in the NEW layout: {len(dup)} {dup}")
    arcs_n = collections.Counter(d.parts[-2] for d in dsts)
    singles = [a for a, n in arcs_n.items() if n < 2]
    print(f"  arcs in the new layout   : {len(set(d.parts[-2] for d in dsts))}")
    print(f"  arcs with <2 rounds      : {len(singles)} {singles}")
    ok = not dup and not unclaimed and not singles
    print(f"\n  PRECONDITIONS: {'PASS — orthogonal, complete, no singleton arc' if ok else 'FAIL'}")
    if not ok:
        return 1
    if not apply:
        print("\n  dry run. re-run with --apply to move.")
        return 0

    # ── apply, and write the remap so an old citation stays resolvable ──────────────────────
    remap = ROOT / "_ear" / "REMAP.tsv"
    remap.parent.mkdir(exist_ok=True)
    lines = ["old_path\tnew_path\tnote"]
    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        r = sh("git", "mv", str(src.relative_to(ROOT)), str(dst.relative_to(ROOT)))
        if r.returncode:
            print(f"  git mv FAILED {src.name}: {r.stderr.strip()[:120]}"); return 1
        note = ("ID REASSIGNED — this round shared its id with a different round in "
                "A23; first claim by git kept the id"
                if src.name.split("_")[0] != dst.name.split("_")[0] else "arc renumbered")
        lines.append(f"{src.relative_to(ROOT)}\t{dst.relative_to(ROOT)}\t{note}")
    remap.write_text("\n".join(lines) + "\n")
    for d in sorted(ROOT.glob("E0*/A*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
    print(f"  moved {len(moves)}; remap written to {remap.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
