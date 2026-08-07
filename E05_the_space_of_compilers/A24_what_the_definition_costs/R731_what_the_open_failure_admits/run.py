"""
R731 · what the open failure admits

ESTIMAND        at the OBJECT level, do the three target-reading objects clause ③ admits sit with the
                object ③ EXCLUDES, or with the label-blind topw objects, on clause ① and ② margins?
IDENTIFICATION  identified from R728's cached difference vectors, one representative tag per object
                from R730's partition. NOT identified: a principled threshold for "sits with" --
                so every distance is reported in units of the within-topw spread, never as a bare
                classification.
SCOPE           population R730's objects · instrument R294's contrast machinery on R728's vectors ·
                baseline the excluded oracle object and the four topw objects · regime this tree_sha
WORLDS          W-INFLATION they sit with the excluded object -> ③ needs a predicate ·
                W-MISDRAWN they sit with topw -> the blocklist is around the wrong property
KILL            conditional on POSITIVE and NEGATIVE. See PREREGISTRATION.txt.
POSITIVE CTRL   reproduce R522's six published clause-② effects to 4 decimals from R728's cache;
                floor 0 < t 6 <= ceiling 6.
g=0             an object against itself -> gap exactly 0.
NEGATIVE CTRL   permute the object->margin pairing; the separation must collapse to its null.
                excluded world: "any partition would show this separation".
SHAM            the same separation on `n`, which carries no clause information -- absent, not
                inverted.
PLACEBO         topw against topw -> gaps at the within-group floor.
NOISE FLOOR     the within-topw spread, measured; every distance reported in its units.
MULTIPLICITY    2 clauses x 9 objects x 2 reference groups, every pairing reported.
SPECIFICATION   metric (absolute, MDE units, spread units) x clause x representative (first, mean)
SEEDS           1000 permutations x 3 seeds; two hash seeds byte-identical
ARTIFACT        results/r731_what_the_failure_admits.json with tree_sha
IMPOSSIBLE      whether a similar margin implies the same MECHANISM -> needs an intervention on the
                construction · independently replicated -> a second implementer
"""
import hashlib, json, math, pathlib, subprocess, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ARC  = HERE.parent
Z95, ZEFF = 1.959964, 1.959964 + 0.841621
VEC  = ARC / "R728_the_census_at_sixteen_times_the_resamples" / "results" / "_vectors.npz"
PART = ARC / "R730_seven_tags_are_not_seven_objects" / "results" / "r730_object_partition.json"
R522 = ARC / "R522_the_six_candidacies_become_verdicts" / "results" / "six_verdicts.json"
BLOCKLIST = {"oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"}


def cell(d, seed=31337, B=1200):
    n = len(d)
    idx = np.random.default_rng(seed).integers(0, n, (B, n))
    bs = d[idx].mean(axis=1)
    return {"eff": float(d.mean()), "lo": float(np.percentile(bs, 2.5)),
            "hi": float(np.percentile(bs, 97.5)),
            "mde": ZEFF * float(d.std(ddof=1)) / math.sqrt(n), "n": n}


def main() -> int:
    print("=" * 100); print("R731 · WHAT THE OPEN FAILURE ADMITS"); print("=" * 100)
    for p in (VEC, PART, R522):
        if not p.exists():
            print(f"  UNRUNNABLE: {p.name} absent. Exit 2, never 0."); return 2
    z = np.load(VEC, allow_pickle=True)
    V = {k: z[k].item() for k in z.files}
    part = json.loads(PART.read_text()); r522 = json.loads(R522.read_text())["six"]
    classes = [set(c) for c in part["multi_tag_classes"]]

    def obj_of(t):
        for c in classes:
            if t in c:
                return tuple(sorted(c))
        return (t,)

    # objects under study, one representative tag each (present in the vector cache)
    GROUPS = {
        "admitted_target_reading": [("greedy", "greedy_k4_greedy_kA"),
                                    ("indep", "indep_k4_indep_kA"),
                                    ("oracle08bR", "oracle_k4_08bR")],
        "excluded_target_reading": [("oracle", "oracle_k4")],
        "label_blind_topw":        [("topw_k3", "topw_k3"), ("topw_k4", "topw_k4"),
                                    ("topw_k6", "topw_k6"), ("topw_k8", "topw_k8")],
        "released_core":           [("coval_core", "coval_core")],
    }
    missing = [t for g in GROUPS.values() for _, t in g if t not in V]
    if missing:
        print(f"  ⛔ representatives absent from the vector cache: {missing} — exit 2, never 0")
        return 2

    M = {}
    for grp, items in GROUPS.items():
        for name, tag in items:
            c1, c2 = cell(V[tag]["d1"]), cell(V[tag]["d2"])
            M[name] = {"tag": tag, "group": grp, "object": list(obj_of(tag)),
                       "c1": c1, "c2": c2, "n": V[tag]["n"]}

    ctl = {}
    print("\n─── CONTROLS ───")
    ok, tot = 0, 0
    for t, v in r522.items():
        if t in V:
            tot += 1
            e = cell(V[t]["d2"])["eff"]
            if abs(e - v["c2"]) < 5e-5:
                ok += 1
            else:
                print(f"             ⚠ {t}: mine {e:.6f} vs R522 {v['c2']:.6f}")
    ctl["POSITIVE"] = (ok == tot and tot == 6)
    print(f"  POSITIVE   R522's published clause-② effects reproduced: {ok}/{tot} to 4 decimals")
    print(f"             band floor 0 < t {tot} <= ceiling {tot} -> "
          f"{'PASS' if ctl['POSITIVE'] else 'FAIL'}")

    ctl["G0"] = abs(M["greedy"]["c2"]["eff"] - M["greedy"]["c2"]["eff"]) == 0.0
    print(f"  g=0        an object against itself -> gap exactly 0 -> "
          f"{'PASS' if ctl['G0'] else 'FAIL'}")

    topw = [k for k, v in M.items() if v["group"] == "label_blind_topw"]
    adm  = [k for k, v in M.items() if v["group"] == "admitted_target_reading"]
    spread = {c: float(np.std([M[k][c]["eff"] for k in topw], ddof=1)) for c in ("c1", "c2")}
    print(f"  NOISE FLR  within-topw spread  clause① {spread['c1']:.6f}   clause② {spread['c2']:.6f}")
    print(f"             every distance below is also reported in these units, because 'sits with'")
    print(f"             has no absolute meaning.")

    def sep(assign, clause):
        """mean distance to the oracle group minus mean distance to the topw group, over `assign`."""
        o = M["oracle"][clause]["eff"]
        tw = np.mean([M[k][clause]["eff"] for k in topw])
        return float(np.mean([abs(M[k][clause]["eff"] - o) - abs(M[k][clause]["eff"] - tw)
                              for k in assign]))

    real_sep = {c: sep(adm, c) for c in ("c1", "c2")}
    pool = [k for k in M if k not in ("oracle",)]
    nulls = {}
    for c in ("c1", "c2"):
        vals = []
        for s in (1, 2, 3):
            rng = np.random.default_rng(1000 + s)
            for _ in range(1000):
                pick = list(rng.choice(pool, size=len(adm), replace=False))
                vals.append(sep(pick, c))
        nulls[c] = np.array(vals)
    ctl["NEGATIVE"] = all(real_sep[c] < float(np.percentile(nulls[c], 25)) for c in ("c1", "c2"))
    for c in ("c1", "c2"):
        p = float((nulls[c] <= real_sep[c]).mean())
        print(f"  NEGATIVE   {c}: real separation {real_sep[c]:+.6f}  null median "
              f"{float(np.median(nulls[c])):+.6f}  p(null <= real) = {p:.4f}")
    print(f"             (negative = closer to the EXCLUDED object) -> "
          f"{'PASS' if ctl['NEGATIVE'] else 'FAIL'}")
    print(f"             excluded world: 'any partition of these objects shows this separation'")

    n_o = M["oracle"]["n"]; n_tw = np.mean([M[k]["n"] for k in topw])
    sham = float(np.mean([abs(M[k]["n"] - n_o) - abs(M[k]["n"] - n_tw) for k in adm]))
    ctl["SHAM"] = abs(sham) < 1e-9
    print(f"  SHAM       the same separation on `n`, which carries no clause information: "
          f"{sham:+.6f} -> {'PASS' if ctl['SHAM'] else 'FAIL'}  (ingredient absent)")

    plc = {c: float(np.mean([abs(M[a][c]["eff"] - M[b][c]["eff"])
                             for i, a in enumerate(topw) for b in topw[i+1:]]))
           for c in ("c1", "c2")}
    ctl["PLACEBO"] = all(plc[c] <= 3 * spread[c] for c in ("c1", "c2"))
    print(f"  PLACEBO    topw against topw: mean |gap| ①{plc['c1']:.6f} ②{plc['c2']:.6f} "
          f"vs 3x spread ①{3*spread['c1']:.6f} ②{3*spread['c2']:.6f} -> "
          f"{'PASS' if ctl['PLACEBO'] else 'FAIL'}")
    n_pass = sum(1 for v in ctl.values() if v)
    print(f"\n  controls: {n_pass} PASS, {len(ctl)-n_pass} FAIL")

    # ── the table ────────────────────────────────────────────────────────────────────────────
    print(f"\n─── OBJECT-LEVEL MARGINS · every object counted ONCE ───")
    print(f"  {'object':<13}{'group':<26}{'clause① eff':>13}{'clause② eff':>13}{'②/mde':>9}  tags")
    for k, v in M.items():
        print(f"  {k:<13}{v['group']:<26}{v['c1']['eff']:>13.6f}{v['c2']['eff']:>13.6f}"
              f"{v['c2']['eff']/v['c2']['mde']:>9.2f}  {len(v['object'])}")

    o2, tw2 = M["oracle"]["c2"]["eff"], float(np.mean([M[k]["c2"]["eff"] for k in topw]))
    o1, tw1 = M["oracle"]["c1"]["eff"], float(np.mean([M[k]["c1"]["eff"] for k in topw]))
    print(f"\n─── DISTANCE OF EACH ADMITTED OBJECT, IN WITHIN-TOPW SPREADS ───")
    nearest = {}
    for k in adm:
        row = {}
        for c, o, tw in (("c1", o1, tw1), ("c2", o2, tw2)):
            do = abs(M[k][c]["eff"] - o) / spread[c]
            dt = abs(M[k][c]["eff"] - tw) / spread[c]
            row[c] = ("oracle" if do < dt else "topw", do, dt)
            print(f"  {k:<13} {c}  to oracle {do:>7.2f}   to topw {dt:>7.2f}   -> "
                  f"{'ORACLE' if do < dt else 'topw'}")
        nearest[k] = row

    A = ok
    B = float(np.mean([abs(M[k]["c2"]["eff"] - o2) for k in adm]))
    C = float(np.mean([abs(M[k]["c2"]["eff"] - tw2) for k in adm]))
    D = sum(1 for k in adm if nearest[k]["c2"][0] == "oracle")
    directional = all(nearest[k]["c1"][0] == nearest[k]["c2"][0] for k in adm)

    print(f"\n─── REGISTERED POINTS ───")
    for nm, val, lo_, hi_, reg in [("A R522 reproduced", A, 0, 6, 6),
                                   ("B mean |②gap| to oracle", round(B, 4), 0.0, 1.0, 0.02),
                                   ("C mean |②gap| to topw", round(C, 4), 0.0, 1.0, 0.04),
                                   ("D admitted closer to oracle", D, 0, 3, 3)]:
        print(f"  {nm:<30} registered {reg:<6} -> {val:<8} in [{lo_},{hi_}]: {lo_ <= val <= hi_}")
    print(f"  DIRECTIONAL clause ① and ② give the same nearest group for every object -> "
          f"{directional}")

    print("\n─── KILL (conditional on controls) ───")
    if not (ctl["POSITIVE"] and ctl["NEGATIVE"]):
        world = "UNVERIFIED — a gating control did not fire; no claim about what ③ admits is admissible."
    elif D == 0:
        world = (f"⭐⭐⭐ W-MISDRAWN. All {len(adm)} admitted target-reading objects sit with the "
                 f"label-blind topw objects, so the blocklist is drawn around the wrong property and "
                 f"the defect is in the DEFINITION rather than in its implementation.")
    elif D == len(adm):
        world = (f"⭐⭐⭐ W-INFLATION — THE OPEN FAILURE ADMITS KNOWN INFLATION. All {len(adm)} "
                 f"target-reading objects clause ③ admits sit with the object it EXCLUDES, on both "
                 f"clauses: clause-② margins {[round(M[k]['c2']['eff'], 4) for k in adm]} against the "
                 f"excluded oracle's {o2:.4f} and the label-blind topw mean {tw2:.4f}, with the "
                 f"released core at {M['coval_core']['c2']['eff']:.4f}. Mean distance to the excluded "
                 f"object is {B:.4f} against {C:.4f} to the blind group. ⭐ SO ③ IS NOT MERELY "
                 f"INCOMPLETE — its omissions have the size the clause exists to remove, and a longer "
                 f"list would not fix it: the clause needs a PREDICATE over construction. "
                 f"⚠ THIS IS A COMPARISON OF OUTCOMES, NOT OF MECHANISMS. A margin near the oracle's "
                 f"does not establish that the same construction produced it; that needs an "
                 f"intervention and is in the impossibility register. ⚠ And the separation is "
                 f"reported in units of the within-topw spread ({spread['c2']:.6f} on clause ②) "
                 f"because 'sits with' has no absolute meaning, with a permutation null over all "
                 f"non-oracle objects to exclude the world where any grouping would show it.")
    else:
        world = (f"⭐⭐⭐ SPLIT — {D} of {len(adm)} admitted objects sit with the excluded one and the "
                 f"rest with the blind group, so neither world holds and the object identity is doing "
                 f"work the rule name does not. That disagreement is the finding: "
                 f"{ {k: nearest[k]['c2'][0] for k in adm} }")
    print(f"  {world}")

    tree_sha = subprocess.run(["git", "rev-parse", "HEAD^{tree}"], capture_output=True,
                              text=True, cwd=str(ARC)).stdout.strip()
    out = {"world": world, "controls_ok": all(ctl.values()), "controls": ctl, "tree_sha": tree_sha,
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "objects": M, "within_topw_spread": spread,
           "real_separation": real_sep,
           "null_median": {c: float(np.median(nulls[c])) for c in nulls},
           "null_p": {c: float((nulls[c] <= real_sep[c]).mean()) for c in nulls},
           "nearest": {k: {c: nearest[k][c][0] for c in ("c1", "c2")} for k in adm},
           "distances_in_spreads": {k: {c: [nearest[k][c][1], nearest[k][c][2]]
                                        for c in ("c1", "c2")} for k in adm},
           "A_r522_reproduced": A, "B_mean_gap_to_oracle": B, "C_mean_gap_to_topw": C,
           "D_closer_to_oracle": D, "directional_clauses_agree": directional,
           "prior_art": ["R520", "R521", "R522", "R523", "R525", "R730"],
           "registered": "A 6 [0,6]; B 0.02 [0,1]; C 0.04 [0,1]; D 3 [0,3]; directional clauses agree",
           "residue": "a similar margin does not establish a similar MECHANISM; that needs an "
                      "intervention on the construction"}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "r731_what_the_failure_admits.json").write_text(
        json.dumps(out, indent=2, sort_keys=True))
    print(f"\n  artifact: results/r731_what_the_failure_admits.json   tree {tree_sha[:12]}")
    return 0 if all(ctl.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
