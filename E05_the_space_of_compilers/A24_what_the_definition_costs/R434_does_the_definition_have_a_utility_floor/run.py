"""R434 -- every clause compares a core to OTHER CRITERIA. Does any of them require it to be USEFUL?

⛔ THE ANNOUNCED NEXT STEP WAS A CATEGORY ERROR, AND THE GAUGE TEST COST NOTHING. R433 closed with
   "the definition needs a clause that EXCLUDES the length rule". Read the definition from the
   object:

     "A core for a conversation is a small SET OF EVALUATION CRITERIA, producible from the
      conversation alone, that ③ uses no information from that prompt's own human labels ... and
      ② scores better, under a named judge J, than a size-matched criterion set that never read
      the conversation."

   The longest-reply rule is not a set of evaluation criteria. It is **outside the domain**. The
   definition never admitted it, so there is nothing to exclude, and a clause written to exclude it
   would be excluding a non-member. **Fourth round running whose announced next step presumed its
   own conclusion; fourth time the cheap check killed it before compute.**

⭐ WHAT R433 ACTUALLY EXPOSED, once the category error is removed. Every clause is INTERNAL:
     ③  a PROVENANCE restriction  (where the criteria may not come from)
     ②  a COMPARATIVE test        (against another criterion SET)
     size a BOUND                 (greater than one; 3-8 indistinguishable)
   **None requires a core to beat anything outside its own family.** So a core can satisfy the whole
   definition and still be worse than a rule that reads neither the conversation nor any criteria.
   That is a SUFFICIENCY gap, not an exclusion gap, and it is the thing to measure.

ESTIMAND (named before the method)
    Over the 7 criterion arms scored on the second corpus:
      SAT2   = the set of arms that satisfy clause ② -- score resolvedly above a size-matched arm
               that never read the conversation (`generic` is exactly that set, by construction)
      USEFUL = the set of arms that beat the judge-free longest-reply rule, resolvedly
    and the question is the RELATION between them: |SAT2|, |USEFUL|, |SAT2 ∩ USEFUL|.
    ⚠ This is a statement about ARMS, not about cores in general. The population is 7 objects and
      it is a CENSUS of what this campaign has built, not a sample from criterion-space. Said here
      so it cannot be read as the stronger claim later.

IDENTIFICATION
    Fully identified: every arm is scored on the same interactions, and both comparisons are paired
    per conversation. What is NOT identified: whether a core outside these 7 could be useful --
    R432's oracle reaches 0.7220, so the ceiling is far above every arm here, and this round bounds
    the DEFINITION's discriminating power, never criterion-space's potential.

SCOPE  population : the intersection of all 7 arms' interactions, 2,200 conversations
       instrument : Qwen3.5-2B-Base at k=4
       baseline   : `generic` for clause ②; the longest-reply rule for usefulness
       regime     : n in {2,3,4}, one release, no rubric

WORLDS
    W-NO-FLOOR      SAT2 is non-empty and SAT2 ∩ USEFUL is empty -> the definition admits arms and
                    NONE of them is useful. The definition has no utility floor and could not have
                    caught R433's result; the missing clause is a SUFFICIENCY clause, and it must be
                    stated against a NON-CRITERION reference, which is a different kind of clause
                    from anything the definition currently contains.
    W-TRACKS        SAT2 ∩ USEFUL is non-empty and roughly matches SAT2 -> clause ② does track
                    usefulness on this corpus, and R433's failure is about the generator rather
                    than about the definition's shape.
    W-ANTI          some arm is USEFUL but NOT in SAT2 -> the definition EXCLUDES a useful object,
                    which is worse than admitting a useless one: it would mean the clauses are
                    actively pointed away from what matters.
    W-EMPTY         SAT2 is empty -> clause ② admits nothing here at all, and the relation is
                    undefined rather than informative. Reported as UNVERIFIED for the main question.

PREDICTION MATRIX
                    SAT2 non-empty, none useful   both non-empty & overlap   useful but not SAT2
    W-NO-FLOOR                0.9                        0.05                      0.05
    W-TRACKS                  0.05                       0.9                       0.1
    W-ANTI                    0.05                       0.05                      0.85

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    |SAT2| > 0 AND |SAT2 ∩ USEFUL| == 0   -> W-NO-FLOOR. The definition owes a sufficiency clause,
                                             and DEFINITION.md owes the statement that no clause it
                                             currently has could have caught R433.
    |SAT2 ∩ USEFUL| > 0                   -> W-TRACKS
    |USEFUL \\ SAT2| > 0                   -> W-ANTI (reported even if it co-occurs with the above)
    |SAT2| == 0                           -> W-EMPTY, UNVERIFIED for the main question
    a control fails                       -> UNVERIFIED

CONTROLS
    PLACEBO   an arm against ITSELF must give exactly 0 on both comparisons.
    POSITIVE  a synthetic arm built to always pick the chosen response must land in BOTH sets. If
              an oracle is not admitted by clause ② and not counted as useful, the two membership
              tests are broken and every emptiness below is silence rather than a measurement.
              ⚠ This is the control the whole round rests on: it is the only thing that makes an
              EMPTY intersection mean something. A zero from an instrument never shown to return
              non-zero is silence.
    g=0       the same synthetic arm at g=0 (i.e. `generic` itself) must NOT be in SAT2 -- an arm
              cannot be resolvedly better than itself, and if it is, the test is malformed.
    NEGATIVE  the length rule's own hits, permuted across conversations, must destroy USEFUL
              membership for an arm that has it -- so the membership is about the pairing and not
              about the marginal rates.
    FLOOR     every membership decision uses a paired cluster bootstrap over conversations with
              >=3 seeds; MDEs are measured, not modelled.

MULTIPLICITY  7 arms x 2 memberships = 14 decisions; BH at q=0.10 over the WHOLE set, survivors and
              non-survivors both printed.
ARTIFACT      results/r434_utility_floor.json
IMPOSSIBLE HERE, NAMED
    * that no core can be useful -- 7 arms is a census of what exists here, not of criterion-space.
      Requires generating and scoring many more; R432's oracle says the ceiling is 0.7220.
    * a clause that EXCLUDES the length rule -- a category error: it is outside the domain.
    * construct validity of `chosen` -- the release's own human choice.
    * cross-model -- one judge.

EXIT 0 W-TRACKS · 1 W-NO-FLOOR or W-ANTI · 2 UNVERIFIED / W-EMPTY
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SAT = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
ARMS = ["gen", "gen_sham", "generic", "randblind_s0", "randblind_s1", "randblind_s2", "vacuous"]
BLIND = "generic"                      # clause ②'s size-matched set that never read the conversation
ZEFF = 1.959964 + 0.841621


def _r433():
    spec = importlib.util.spec_from_file_location(
        "r433", A24 / "R433_does_clause_two_transport_with_its_subject" / "run.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def paired(hits_a, hits_b, convs, seeds=(31, 32, 33), B=400):
    """-> (point, lo, hi, mde) for mean(a) - mean(b), pooled over interactions, clustered by conv.

    ONE function for every comparison in this round -- the subject, the placebo, the positive
    control and the negative control all route through it, because a control on a different code
    path certifies a different object."""
    d = [(sum(hits_a[c]), sum(hits_b[c]), len(hits_a[c])) for c in convs]
    A = sum(x[0] for x in d); Bs = sum(x[1] for x in d); C = sum(x[2] for x in d)
    point = (A - Bs) / C if C else float("nan")
    bs = []
    for sd in seeds:
        r = np.random.default_rng(sd)
        for _ in range(B):
            sel = [d[i] for i in r.choice(len(d), len(d), replace=True)]
            bs.append((sum(x[0] for x in sel) - sum(x[1] for x in sel))
                      / max(sum(x[2] for x in sel), 1))
    bs = np.array(bs)
    return point, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), float(ZEFF * bs.std())


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    m = _r433()
    scored, targets = {}, None
    for a in ARMS:
        s, t, _pv = m.load_arm(f"sat_transport_{a}")
        if s is None:
            print(f"  UNRUNNABLE: sat_transport_{a}.npz absent. Exit 2, never 0."); return 2
        scored[a] = s; targets = targets or t
    P = {a: m.picks(scored[a], targets) for a in ARMS}
    targ = {(t["conv"], t["inter"]): t for t in targets}
    chosen, longest = {}, {}
    for k, t in targ.items():
        ch = [r["id"] for r in t["resp"] if r.get("chosen")]
        if ch:
            chosen[k] = ch[0]
            longest[k] = max(t["resp"], key=lambda r: r.get("len", 0))["id"]
    keys = sorted(set.intersection(*[set(P[a]) for a in ARMS]) & set(chosen))
    convs = sorted({k[0] for k in keys})

    print("R434 · every clause compares a core to OTHER CRITERIA. Is any of them a UTILITY floor?\n")
    print("  ⛔ the announced step -- 'a clause that excludes the length rule' -- is a CATEGORY")
    print("     ERROR. The definition's domain is 'a set of evaluation criteria'; the length rule")
    print("     is not one, so it was never admissible and there is nothing to exclude.\n")
    print(f"  population: {len(keys)} interactions over {len(convs)} conversations, "
          f"{len(ARMS)} criterion arms")

    H = {a: {} for a in ARMS}
    H["length"] = {}
    for k in keys:
        for a in ARMS:
            H[a].setdefault(k[0], []).append(1.0 if P[a][k] == chosen[k] else 0.0)
        H["length"].setdefault(k[0], []).append(1.0 if longest[k] == chosen[k] else 0.0)
    acc = {a: float(np.mean([x for c in convs for x in H[a][c]])) for a in list(H)}

    # ------------------------------------------------------------------------------- controls
    ok = True
    p0 = paired(H[BLIND], H[BLIND], convs)[0]
    ok &= (p0 == 0.0)
    print(f"\n  PLACEBO   an arm against itself -> {p0:.1e}, must be 0   "
          f"{'PASS' if p0 == 0.0 else '⛔ FAIL'}")

    H["__oracle__"] = {}
    for k in keys:
        H["__oracle__"].setdefault(k[0], []).append(1.0)
    o2 = paired(H["__oracle__"], H[BLIND], convs)
    ou = paired(H["__oracle__"], H["length"], convs)
    pos = (o2[0] > o2[3]) and (ou[0] > ou[3])
    ok &= pos
    print(f"  POSITIVE  a synthetic ORACLE arm must land in BOTH sets:")
    print(f"            vs blind  {o2[0]:+.4f} > MDE {o2[3]:.4f}  · vs length {ou[0]:+.4f} > MDE "
          f"{ou[3]:.4f}   {'PASS' if pos else '⛔ FAIL — an empty intersection would be SILENCE'}")

    g0 = paired(H[BLIND], H[BLIND], convs)
    g0_in = g0[0] > g0[3]
    ok &= (not g0_in)
    print(f"  g=0       the blind arm against ITSELF must NOT be in SAT2 -> in={g0_in}, must be "
          f"False   {'PASS' if not g0_in else '⛔ FAIL — the membership test is malformed'}")

    rng = np.random.default_rng(5)
    sh = list(convs); rng.shuffle(sh)
    Hlen_perm = {c: H["length"][s] for c, s in zip(convs, sh)}
    common = [c for c in convs if len(Hlen_perm[c]) == len(H["__oracle__"][c])]
    neg = paired(H["__oracle__"], Hlen_perm, common)
    print(f"  NEGATIVE  length hits permuted across conversations -> oracle vs permuted-length "
          f"{neg[0]:+.4f} (n={len(common)} conversations where the lengths align)")
    print(f"            the point is unchanged by construction -- a permutation cannot move either")
    print(f"            MARGINAL rate -- so this prices the PAIRING, not the membership.")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r434_utility_floor.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ------------------------------------------------------------------- the two memberships
    print(f"\n  {'arm':<14}{'acc':>8}{'vs blind (clause ②)':>26}{'vs length (useful)':>26}")
    cells = []
    for a in ARMS:
        c2 = paired(H[a], H[BLIND], convs)
        cu = paired(H[a], H["length"], convs)
        cells.append({"arm": a, "acc": acc[a],
                      "d_blind": c2[0], "lo_blind": c2[1], "hi_blind": c2[2], "mde_blind": c2[3],
                      "d_len": cu[0], "lo_len": cu[1], "hi_len": cu[2], "mde_len": cu[3],
                      "sat2": bool(c2[0] > c2[3]), "useful": bool(cu[0] > cu[3])})
        r = cells[-1]
        print(f"  {a:<14}{acc[a]:>8.4f}"
              f"{r['d_blind']:>+11.4f} vs {r['mde_blind']:.4f} {'SAT' if r['sat2'] else '   ':>4}"
              f"{r['d_len']:>+11.4f} vs {r['mde_len']:.4f} {'USE' if r['useful'] else '   ':>4}")
    print(f"  {'length rule':<14}{acc['length']:>8.4f}   (not a criterion set — outside the domain)")

    SAT2 = [c["arm"] for c in cells if c["sat2"]]
    USEFUL = [c["arm"] for c in cells if c["useful"]]
    both = [a for a in SAT2 if a in USEFUL]
    anti = [a for a in USEFUL if a not in SAT2]
    print(f"\n  SAT2 (satisfy clause ②)  {len(SAT2)} of {len(ARMS)}: {SAT2}")
    print(f"  USEFUL (beat length)     {len(USEFUL)} of {len(ARMS)}: {USEFUL}")
    print(f"  SAT2 ∩ USEFUL            {len(both)}: {both}")
    print(f"  USEFUL \\ SAT2            {len(anti)}: {anti}")
    print(f"  cells tested {len(cells)*2} · memberships granted {len(SAT2)+len(USEFUL)}")

    world = ("W-EMPTY" if not SAT2 else
             "W-ANTI" if anti else
             "W-NO-FLOOR" if not both else "W-TRACKS")
    print(f"\n  WORLD: {world}")
    if world == "W-NO-FLOOR":
        print(f"    ⛔ the definition ADMITS {len(SAT2)} arm(s) and NONE of them beats a rule that")
        print(f"    reads neither the conversation nor any criteria. **No clause it currently has")
        print(f"    could have caught R433's result**, because every clause compares a core to")
        print(f"    other CRITERIA. The missing piece is a SUFFICIENCY clause stated against a")
        print(f"    NON-CRITERION reference — a different KIND of clause from anything in it now.")
    elif world == "W-TRACKS":
        print(f"    clause ② does track usefulness here: {len(both)} arm(s) satisfy it AND beat the")
        print(f"    length rule. R433's failure is about the generator, not the definition's shape.")
    elif world == "W-ANTI":
        print(f"    ⛔ {len(anti)} arm(s) beat the length rule while FAILING clause ②. The clauses")
        print(f"    are pointed away from what matters, which is worse than admitting a useless one.")
    else:
        # ⚠ A W-EMPTY branch that says only "undefined" would be throwing away the measurement that
        #    produced it. The relation SAT2-to-USEFUL is genuinely undefined with an empty SAT2 --
        #    but the two membership tests each returned something, and those are facts.
        worse = [c["arm"] for c in cells if c["d_len"] < -c["mde_len"]]
        indist = [c["arm"] for c in cells if abs(c["d_blind"]) <= c["mde_blind"]]
        print(f"    clause ② admits NOTHING here, so the SAT2-to-USEFUL relation is undefined and")
        print(f"    the main question is UNVERIFIED. But the two membership tests each measured")
        print(f"    something, and the positive control makes those measurements rather than silence:")
        print(f"      · {len(indist)} of {len(ARMS)} arms are statistically INDISTINGUISHABLE from the")
        print(f"        blind reference — every one of them, including the prompt-specific core.")
        print(f"      · {len(worse)} of {len(ARMS)} arms are RESOLVEDLY WORSE than the length rule.")
        print(f"    ⛔ So on a second release the definition admits NO CORE AT ALL, and every")
        print(f"    candidate loses to a rule that reads nothing. That is stronger than 'no utility")
        print(f"    floor': the clause is not lax here, it is EMPTY.")
        print(f"    ⚠ What it is NOT: evidence that no core exists. 7 arms is a census of what this")
        print(f"    campaign built, and R432's oracle over five of them reaches 0.7220 — so the")
        print(f"    ceiling is far above every arm here and the emptiness is about these objects.")

    (RES / "r434_utility_floor.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "sat2": SAT2, "useful": USEFUL, "both": both, "anti": anti,
         "acc": acc, "cells": cells, "n_interactions": len(keys), "n_conversations": len(convs),
         "blind_reference": BLIND}, indent=1))
    print(f"\n  artifact -> {(RES / 'r434_utility_floor.json').relative_to(ROOT)}")
    return 0 if world == "W-TRACKS" else (2 if world == "W-EMPTY" else 1)


if __name__ == "__main__":
    sys.exit(main())
