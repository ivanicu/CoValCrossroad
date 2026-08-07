"""
R732 · the third cell varied two things

ESTIMAND        how many factors differ between oracle_k4 and oracle_k4_08bR, and does any object on
                disk permit separating the emitter effect from the selection effect?
IDENTIFICATION  ⚠ PARTIAL BY DESIGN. Their margin gap confounds which criteria were selected with
                which emitter scored them. The decomposition is reported ONLY if the 2x2 exists;
                otherwise the gap is UNIDENTIFIED with the missing cell named.
SCOPE           population today's 93 tags · instrument core_*.json criteria identity + sat cell
                agreement · baseline the default-emitter arms · regime this tree_sha
WORLDS          W-CONFOUNDED no 2x2 -> R731's third cell withdrawn to UNVERIFIED ·
                W-SEPARABLE a 2x2 exists -> the judge effect is estimable
KILL            conditional on POSITIVE and NEGATIVE. See PREREGISTRATION.txt.
POSITIVE CTRL   topw_k4 vs topw_k4_detA, proven the same object, must return 1.0000 on both
                measures; band floor (a known-different pair) < t 1.0 <= ceiling 1.0.
g=0             an arm against itself -> 1.0; the known-different pair must NOT return 1.0.
NEGATIVE CTRL   permute criteria across prompts; identity must collapse. excluded world: "the
                comparison is insensitive to WHICH criteria, only to how many".
SHAM            compare on PROMPT SETS alone, criteria removed -- absent, not inverted.
PLACEBO         an alias pair against itself -> exactly 1.0.
NOISE FLOOR     criteria identity across all same-object tag pairs from R730's partition.
MULTIPLICITY    93 tags x 2 measures + all same-object pairs, all reported.
SPECIFICATION   unit (criteria set, criteria multiset, sat cell) x reference (oracle_k4, 08b family,
                default family)
SEEDS           deterministic; 3 seeds for the permutation; two hash seeds byte-identical
ARTIFACT        results/r732_confounded_cell.json with tree_sha
IMPOSSIBLE      the judge effect alone -> needs a scoring run of one arm's criteria under the other
                emitter, a NEW MEASUREMENT not derivable from artifacts ·
                independently replicated -> a second implementer
"""
import hashlib, json, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
ROOT = HERE.parents[2]
RES  = ROOT / "corebench" / "results"
PART = ARC / "R730_seven_tags_are_not_seven_objects" / "results" / "r730_object_partition.json"
TARGET, REF = "oracle_k4_08bR", "oracle_k4"


def core(tag):
    p = RES / f"core_{tag}.json"
    return json.loads(p.read_text()) if p.exists() else None


def cells(tag):
    p = RES / f"sat_{tag}.npz"
    if not p.exists():
        return None
    z = np.load(p, allow_pickle=True)
    return dict(zip([str(m) for m in z["meta"]], z["sat"].tolist()))


def crit_identity(a, b):
    ca, cb = core(a), core(b)
    if not ca or not cb:
        return None, 0
    sh = sorted(set(ca) & set(cb))
    if not sh:
        return None, 0
    return sum(1 for p in sh if ca[p] == cb[p]) / len(sh), len(sh)


def cell_agreement(a, b):
    A, B = cells(a), cells(b)
    if not A or not B:
        return None, 0
    sk = sorted(set(A) & set(B))
    if not sk:
        return None, 0
    return sum(1 for k in sk if A[k] == B[k]) / len(sk), len(sk)


def main() -> int:
    print("=" * 100); print("R732 · THE THIRD CELL VARIED TWO THINGS"); print("=" * 100)
    if not PART.exists():
        print("  UNRUNNABLE: R730's partition absent. Exit 2, never 0."); return 2
    part = json.loads(PART.read_text())
    tags = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and p.stem != "sat_genericpool16")
    if not tags:
        print("  ⛔ EMPTY POPULATION — exit 2, never 0"); return 2
    print(f"  tags {len(tags)}   target {TARGET}   reference {REF}")

    ctl = {}
    print("\n─── CONTROLS ───")
    pc_ci, n1 = crit_identity("topw_k4", "topw_k4_detA")
    pc_ca, n2 = cell_agreement("topw_k4", "topw_k4_detA")
    diff_ci, _ = crit_identity("oracle_k4", "topw_k4")
    ctl["POSITIVE"] = (pc_ci == 1.0 and pc_ca == 1.0 and diff_ci is not None and diff_ci < 1.0)
    print(f"  POSITIVE   topw_k4 vs topw_k4_detA (same object, R730): criteria {pc_ci:.4f} on {n1} "
          f"prompts, cells {pc_ca:.4f} on {n2}")
    print(f"             band: known-different pair oracle_k4 vs topw_k4 = {diff_ci:.4f} < t 1.0 "
          f"<= ceiling 1.0 -> {'PASS' if ctl['POSITIVE'] else 'FAIL'}")

    self_ci, _ = crit_identity(TARGET, TARGET)
    ctl["G0"] = (self_ci == 1.0 and diff_ci < 1.0)
    print(f"  g=0        {TARGET} against itself: criteria {self_ci:.4f}; the known-different pair "
          f"does NOT return 1.0 -> {'PASS' if ctl['G0'] else 'FAIL'}")

    ca = core(TARGET)
    perm_scores = []
    for s in (1, 2, 3):
        rng = np.random.default_rng(500 + s)
        ks = sorted(ca)
        shuffled = dict(zip(ks, [ca[k] for k in rng.permutation(np.array(ks, dtype=object))]))
        cb = core(REF)
        sh = sorted(set(shuffled) & set(cb))
        perm_scores.append(sum(1 for p in sh if shuffled[p] == cb[p]) / len(sh))
    real_ci, n_sh = crit_identity(REF, TARGET)
    ctl["NEGATIVE"] = float(np.mean(perm_scores)) < real_ci
    print(f"  NEGATIVE   criteria permuted across prompts -> identity "
          f"{[round(x,4) for x in perm_scores]} vs real {real_ci:.4f} -> "
          f"{'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             excluded world: 'the comparison sees only HOW MANY criteria, not WHICH'")

    pa, pb = set(core(REF)), set(core(TARGET))
    sham = len(pa & pb) / len(pa | pb)
    ctl["SHAM"] = abs(sham - 1.0) < 1e-12
    print(f"  SHAM       prompt sets alone, criteria removed: {sham:.4f} -> "
          f"{'PASS' if ctl['SHAM'] else 'FAIL'}  (identical, so they carry none of the signal)")
    ctl["PLACEBO"] = (self_ci == 1.0)
    print(f"  PLACEBO    an alias pair against itself -> 1.0 -> "
          f"{'PASS' if ctl['PLACEBO'] else 'FAIL'}")

    same_obj = [c for c in part["multi_tag_classes"] if len(c) > 1]
    floors = []
    for cl in same_obj:
        for i in range(len(cl)):
            for j in range(i + 1, len(cl)):
                v, _ = crit_identity(cl[i], cl[j])
                if v is not None:
                    floors.append(v)
    print(f"  NOISE FLR  criteria identity across {len(floors)} same-object tag pairs: "
          f"min {min(floors):.4f} max {max(floors):.4f}")
    print(f"             anything below {min(floors):.4f} is a real difference, not rounding.")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── the two factors ─────────────────────────────────────────────────────────────────────
    ci, nsh = crit_identity(REF, TARGET)
    cg, nck = cell_agreement(REF, TARGET)
    print(f"\n─── HOW MANY FACTORS DIFFER between {REF} and {TARGET} ───")
    print(f"  ① SELECTION : identical criteria on {ci:.4f} of {nsh} shared prompts")
    print(f"  ② EMITTER   : per-cell satisfaction agreement {cg:.4f} on {nck} shared cell keys")
    print(f"                R424 established the _08b family is foreign to the default emitter")
    factors = int(ci < min(floors)) + 1     # selection differs (below the same-object floor) + emitter
    print(f"  => {factors} factors differ, so their margin gap is a SUM and neither term is")
    print(f"     identified from the gap alone.")

    # ── does the 2x2 exist? ─────────────────────────────────────────────────────────────────
    print(f"\n─── IS THERE AN ARM CARRYING {TARGET}'s CRITERIA UNDER A DEFAULT-EMITTER SCORE? ───")
    cand = []
    for t in tags:
        if t == TARGET or "08b" in t:
            continue
        v, n = crit_identity(TARGET, t)
        if v is not None and v >= min(floors):
            cand.append((t, v, n))
    print(f"  arms whose criteria match {TARGET} at or above the same-object floor: {len(cand)}")
    for t, v, n in sorted(cand, key=lambda x: -x[1])[:6]:
        print(f"     {t:<28} {v:.4f} on {n} prompts")
    top = sorted([(v, t) for t, v, _ in cand], reverse=True)[:3]
    print(f"  best non-08b criteria matches: {[(t, round(v,4)) for v, t in top] if top else 'none'}")
    C = len(cand)

    A_pt, B_pt = round(ci, 4), factors
    directional = (C == 0)

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A criteria identity", A_pt, 0.0, 1.0, 0.09),
                                   ("B factors differing", B_pt, 0, 3, 2),
                                   ("C default-emitter twins", C, 0, 93, 0)]:
        print(f"  {nm:<28} registered {reg:<6} -> {val:<8} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL R731's third cell is UNVERIFIED rather than evidence -> {directional}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["NEGATIVE"]):
        world = "UNVERIFIED — a gating control did not fire; no claim about the confound is admissible."
    elif C > 0:
        world = (f"⭐⭐⭐ W-SEPARABLE. {C} arm(s) carry {TARGET}'s criteria under a non-08b score, so the "
                 f"emitter effect is estimable and R731's third cell can be repaired rather than "
                 f"withdrawn: {[t for _, t in top]}")
    else:
        world = (f"⭐⭐⭐ W-CONFOUNDED — R731's THIRD CELL IS WITHDRAWN TO UNVERIFIED. {REF} and {TARGET} "
                 f"differ in TWO factors at once: they select identical criteria on only {ci:.4f} of "
                 f"{nsh} shared prompts, far below the {min(floors):.4f} floor that same-object tag "
                 f"pairs return, and R424 established the _08b family is scored by an emitter foreign "
                 f"to the default. Their margin gap is a sum of a selection effect and an emitter "
                 f"effect, and no arm on disk carries {TARGET}'s criteria under a default-emitter "
                 f"score, so the 2x2 that would separate them does not exist here. "
                 f"⛔ THEREFORE R731's READING -- that construction and behaviour come apart, which I "
                 f"used to retract my own earlier remedy -- IS NOT SUPPORTED BY THAT CELL. It is not "
                 f"refuted either; the cell simply cannot carry it, and UNVERIFIED is not an "
                 f"acquittal in either direction. ⭐ WHAT SURVIVES R731 UNTOUCHED: the greedy and "
                 f"independent objects both sit with the excluded object on both clauses, and both "
                 f"are default-emitter arms, so that comparison mixes no instruments. "
                 f"⚠ AND ONE THING R731 GOT RIGHT FOR THE WRONG REASON: the rule NAME is a poor proxy "
                 f"for construction — these two share the oracle rule and agree on {ci:.1%} of "
                 f"selections. That is now measured rather than inferred from a margin. "
                 f"⚠ The experiment that would settle it: score {TARGET}'s criteria with the default "
                 f"emitter, which is a new measurement and not derivable from any artifact here.")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": all(ctl.values()), "controls": ctl, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "target": TARGET, "reference": REF,
           "A_criteria_identity": A_pt, "n_shared_prompts": nsh,
           "cell_agreement": round(cg, 6), "n_shared_cells": nck,
           "B_factors_differing": B_pt, "C_default_emitter_twins": C,
           "same_object_floor": min(floors), "same_object_pairs": len(floors),
           "permutation_null": [round(x, 6) for x in perm_scores],
           "candidates": [{"tag": t, "identity": v, "n": n} for t, v, n in cand],
           "directional_r731_third_cell_unverified": directional,
           "prior_art": ["R423", "R424", "R426", "R730", "R731"],
           "registered": "A 0.09 [0,1]; B 2 [0,3]; C 0 [0,93]; directional third cell UNVERIFIED",
           "residue": "the emitter effect alone needs a scoring run of the target's criteria under "
                      "the default emitter -- a new measurement, not derivable from artifacts"}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r732_confounded_cell.json").write_text(json.dumps(out, indent=2, sort_keys=True))
    print(f"\n  artifact: results/r732_confounded_cell.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
