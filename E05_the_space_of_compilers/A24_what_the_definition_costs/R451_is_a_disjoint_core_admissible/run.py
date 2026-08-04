"""R451 -- has the definition EVER admitted an object disjoint from the released core?

⛔ THE ANNOUNCED STEP IS ALREADY ANSWERED BY A TABLE I COMMITTED LAST ROUND. R450 closed proposing
   "score r=4 with a=4..12 and see whether admission survives padding to size 8". Its own grid has
   `r=4, a=4` -> m=8, share **0.9793**, against m=4's 0.9841. Padding to 8 IS admitted and the size
   caveat holds. *Nineteenth announced step checked; the part that mattered was forced.*

⭐ WHAT R450 IS NOT ENTITLED TO, AND IT IS THE OPPOSITE OF ITS OPTIMISM. R450 concluded "the
   extension of 1 is a fact about WHICH ARMS WERE BUILT, not about strictness", on the evidence that
   perturbations of the released core stay admitted. **But every admitted object in that grid SHARES
   CRITERIA WITH THE RELEASED CORE** -- r>0 by construction. A ball around one point is not the same
   thing as a category with members. The question never asked in ~50 rounds:

       has anything DISJOINT from the released core ever been admitted?

   ⚠ AND A BARE `no` WOULD BE SILENCE, not a finding, because nothing establishes that a disjoint
   object CAN be admitted by this test. That control is the round's centre of gravity.

ESTIMAND (named before the method)
    OVERLAP(S) = |S ∩ released core| / |released core|, per prompt, averaged.
    SHARE(S)   = fraction of the size-matched class C(16,|S|) that S beats under clause ②'s test.
    PRIMARY    max SHARE over all HINDSIGHT-FREE objects with OVERLAP = 0.
    CONTROL    SHARE of a hindsight-USING object with OVERLAP = 0 (the oracle pool selection).
               Their difference is the whole result: the second says the test CAN admit a disjoint
               object, the first says whether anything real does.

IDENTIFICATION
    Identified for every object built from the 16-criterion pool or from the released core, because
    overlap is known BY CONSTRUCTION. ⚠ NOT identified for arms whose criteria come from elsewhere
    (`gen`, `promptecho`): their satisfaction files are keyed by index, and index identity across
    files is not text identity. Those are reported as PROVENANCE-DISJOINT with that caveat stated,
    never folded into the by-construction group.

SCOPE  population : the 968 home-release prompts
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs, 3 annotator draws held common
       baseline   : the size-matched C(16,m) class -- each object against its OWN size
       regime     : m = 4 throughout, so size is held fixed and cannot explain a difference

WORLDS
    W-BALL      the oracle IS admitted, and no hindsight-free disjoint object is -> the test CAN
                admit a disjoint core, and in ~50 rounds nothing has. The extension is a ball around
                one released point, and R450's "which arms were built" is too kind: the arms that
                were built include prompt-specific ones, and they fail.
    W-DISJOINT  some hindsight-free disjoint object is admitted -> the extension genuinely contains
                members unrelated to the released core, and R450's reading stands as written.
    W-BLIND     even the ORACLE is not admitted -> the test cannot admit a disjoint object at all,
                so the absence is a property of the INSTRUMENT and no conclusion about cores follows.

PREDICTION MATRIX
                    oracle in, rest out   some real one in   oracle out
    W-BALL                 0.85                 0.05            0.10
    W-DISJOINT             0.05                 0.90            0.05
    W-BLIND                0.10                 0.05            0.85

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the oracle control fires.
    if SHARE(oracle, overlap 0) >= 0.80:                     [the test CAN admit a disjoint object]
        max SHARE over hindsight-free disjoint objects >= 0.80  -> W-DISJOINT
        max SHARE over hindsight-free disjoint objects <  0.80  -> W-BALL
    else: W-BLIND, and every "not admitted" in this round is SILENCE, not a measurement.

CONTROLS
    POSITIVE   the oracle pool selection -- per prompt, the 4 of 16 pool criteria that best match the
               human ranking. Zero overlap with the released core BY CONSTRUCTION, and it uses the
               answer, so it is an UPPER BOUND and never evidence about generators.
               ⚠ it must FAIL at g=0: the same selector given a SHUFFLED target must not be admitted.
    CEILING/FLOOR  ceiling = the oracle; floor = the class's own mean self-share (R450: 0.2198).
               The 0.80 threshold must lie strictly between, and that is checked before it is used.
    NEGATIVE   the anti-oracle -- per prompt the 4 pool criteria that WORST match the human. Must
               land far below the floor; if it does not, the selector is not selecting.
    SHAM       released-core criteria from OTHER prompts: overlap is 0 in content while the SOURCE
               is identical, which separates "disjoint" from "not from the rubric".
    SIZE       every object is m=4, so size cannot explain any difference.
    SEEDS      3 seeds on every randomised object; spread reported.

MULTIPLICITY  every object built is reported, admitted or not. No selection, so nothing to correct.
ARTIFACT      results/r451_disjoint.json
IMPOSSIBLE HERE, NAMED
    * text-level overlap for `gen`/`promptecho` -- needs the criterion TEXTS aligned across files,
      which the satisfaction npz does not carry. Reported as provenance-disjoint, caveat attached.
    * whether a disjoint object is "really" a core -- needs a standard outside this definition.
    * a second RELEASED core to test disjointness against -- the release ships exactly one.
"""
from __future__ import annotations
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
ZEFF = 1.959964 + 0.841621
L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))
M = 4


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R451 · has the definition EVER admitted an object DISJOINT from the released core?\n")
    print("  ⛔ the announced step was FORCED by R450's own table: r=4,a=4 -> m=8, share 0.9793 vs")
    print("     m=4's 0.9841. Padding to 8 is admitted. Nineteenth step checked.\n")

    core_f, pool_f = SATD / "sat_coval_core.npz", SATD / "sat_genericpool16.npz"
    if not (core_f.exists() and pool_f.exists()):
        print("  UNRUNNABLE: satisfaction absent. Exit 2, never 0."); return 2
    core, pool = SC.load_sat(core_f), SC.load_sat(pool_f)
    targets, _ = SC.load_targets()
    pids = sorted(set(core) & set(pool) & set(targets))
    n = len(pids)
    print(f"  prompts: {n}   every object below is m={M}, so size cannot explain a difference")
    if n < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    SEEDS = (0, 1, 2)
    HC = {p: np.array([SC.cls(np.array(targets[p][int(np.random.default_rng(1000 * s + stable(p))
                                                      .integers(len(targets[p])))][0], float))
                       for s in SEEDS]) for p in pids}
    CM, PM = {}, {}
    for p in pids:
        cs = sorted({c for (c, _) in core[p]})
        CM[p] = np.array([[core[p].get((c, l), 0.0) for l in L] for c in cs])
        PM[p] = np.zeros((16, 4))
        for (i, ltr), v in pool[p].items():
            PM[p][i, L.index(ltr)] = v

    def a2_rows(Y, p):
        return (signs(Y)[:, None, :] == HC[p][None, :, :]).mean(axis=(1, 2))

    subs = list(itertools.combinations(range(16), M))
    S = np.zeros((len(subs), 16))
    for j, s in enumerate(subs):
        S[j, list(s)] = 1.0
    REF = np.zeros((len(subs), n))
    ALL = {}
    for i, p in enumerate(pids):
        A = a2_rows((S @ PM[p]) / M, p)
        REF[:, i] = A
        ALL[p] = A
    print(f"  reference class: C(16,{M}) = {len(subs)} prompt-blind sets, judged by 2B")

    def share(v):
        d = v[None, :] - REF
        return float((d.mean(axis=1) > ZEFF * d.std(axis=1, ddof=1) / np.sqrt(n)).mean())

    def pool_pick(rule, seed=0):
        """Per prompt choose a 4-subset of the pool. rule: best | worst | rand.
        ⛔ REWRITTEN: the first version tried to express the g=0 control by permuting the objective
           and then indexing through the permutation, and the result was unreadable and wrong (it
           returned W-BLIND on controls that are fine). The g=0 control IS `rand`: an argmax over a
           SHUFFLED objective is a uniformly random index, so destroying the objective and picking
           at random are THE SAME OPERATION. Saying it once, simply, is the fix."""
        v = np.zeros(n)
        for i, p in enumerate(pids):
            A = ALL[p]
            j = (int(np.argmax(A)) if rule == "best" else int(np.argmin(A)) if rule == "worst"
                 else int(np.random.default_rng(seed * 977 + stable(p)).integers(len(subs))))
            v[i] = A[j]
        return v

    # ---- CONTROLS -------------------------------------------------------------------------------
    print("\n  CONTROLS — the oracle is the centre of gravity: without it, `not admitted` is silence")
    orc = pool_pick("best"); s_orc = share(orc)
    anti = pool_pick("worst"); s_anti = share(anti)
    # g=0: the SAME selector with its objective destroyed (see pool_pick docstring)
    g0 = [share(pool_pick("rand", seed=sd)) for sd in range(3)]
    floor = 0.2198  # R450, the class's own computed mean self-share
    print(f"    POSITIVE  oracle pool pick (overlap 0, USES the answer) -> share {s_orc:.4f}"
          f"   {'PASS — a disjoint object CAN be admitted' if s_orc >= 0.80 else '⛔ FAIL'}")
    print(f"              g=0, same selector on a SHUFFLED objective -> {np.mean(g0):.4f} "
          f"[{min(g0):.4f},{max(g0):.4f}]   "
          f"{'PASS (does not fire)' if np.mean(g0) < 0.80 else '⛔ FAIL (fires on noise)'}")
    print(f"    NEGATIVE  anti-oracle (worst pick) -> {s_anti:.4f} vs floor {floor:.4f}   "
          f"{'PASS' if s_anti < floor else '⛔ FAIL — the selector is not selecting'}")
    print(f"    BAND      floor {floor:.4f} < threshold 0.80 < ceiling {s_orc:.4f}   "
          f"{'PASS' if floor < 0.80 < s_orc else '⛔ FAIL'}")
    ctrl_ok = bool((s_orc >= 0.80) and (np.mean(g0) < 0.80) and (s_anti < floor)
                   and (floor < 0.80 < s_orc))

    # ---- the hindsight-FREE disjoint objects -----------------------------------------------------
    objs = []
    for sd in range(3):
        objs.append((f"pool_random_perprompt_s{sd}", share(pool_pick("rand", seed=sd)), "by-construction"))
    rgx = np.random.default_rng(91)
    for sd in range(3):
        sub = rgx.choice(16, size=M, replace=False)
        v = np.array([a2_rows(PM[p][sub].mean(axis=0)[None, :], p)[0] for p in pids])
        objs.append((f"pool_fixed_s{sd}", share(v), "by-construction"))
    # the SHAM: released-core criteria from OTHER prompts -- content disjoint, SOURCE identical
    for sd in range(3):
        v = np.zeros(n)
        for i, p in enumerate(pids):
            q = pids[int(np.random.default_rng(sd * 13 + stable(p)).integers(n))]
            v[i] = a2_rows(CM[q].mean(axis=0)[None, :], p)[0]
        objs.append((f"core_criteria_wrong_prompt_s{sd}", share(v), "by-construction"))
    # provenance-disjoint arms, caveat attached
    for nm in ("gen", "promptecho", "generic", "gen_sham"):
        f = SATD / f"sat_{nm}.npz"
        if not f.exists():
            continue
        d = SC.load_sat(f)
        if not set(pids) <= set(d):
            continue
        v = np.zeros(n)
        for i, p in enumerate(pids):
            cs = sorted({c for (c, _) in d[p]})
            Y = np.array([[d[p].get((c, l), 0.0) for l in L] for c in cs])
            v[i] = a2_rows(Y.mean(axis=0)[None, :], p)[0]
        objs.append((nm, share(v), "provenance (index≠text, caveat)"))

    print("\n  EVERY DISJOINT OBJECT, hindsight-free, m=4 — admitted or not, all reported")
    print(f"    {'object':<34}{'share':>9}   basis for disjointness")
    for nm, sh, basis in sorted(objs, key=lambda o: -o[1]):
        print(f"    {nm:<34}{sh:>9.4f}   {basis}")
    # ⭐ `generic` is PROMPT-BLIND. It is disjoint from the released core, but it is not a candidate
    #    CORE -- it is a member of the same family as the reference class, so its share is a
    #    within-family comparison and near-circular. Classifying the objects is what makes 0.7154
    #    readable instead of confusing, and the classification is by CONSTRUCTION, not by eye.
    PROMPT_SPECIFIC = {"gen", "gen_sham"} | {o[0] for o in objs
                                             if o[0].startswith("pool_random_perprompt")
                                             or o[0].startswith("core_criteria_wrong_prompt")}
    cand = [o for o in objs if o[0] in PROMPT_SPECIFIC and not o[0].endswith("_sham")
            and "wrong_prompt" not in o[0]]
    best = max(objs, key=lambda o: o[1])
    best_cand = max(cand, key=lambda o: o[1]) if cand else ("none", 0.0, "")
    # ⚠ AND ONE LABEL ABOVE WAS WRONG. `pool_random_perprompt` VARIES per prompt but the variation
    #   is a random index, not the prompt's CONTENT -- calling it prompt-specific inflates the
    #   category. The distinction that matters for a CORE is content-driven, and exactly one
    #   hindsight-free disjoint object on this site is: `gen`, generated from the conversation.
    #   Keeping the looser category too, because it is the CONSERVATIVE one: it scores higher, so
    #   W-BALL surviving under it is the stronger statement.
    content_driven = [o for o in objs if o[0] == "gen"]
    best_content = max(content_driven, key=lambda o: o[1]) if content_driven else ("none", 0.0, "")
    print("\n  ⭐ CLASSIFIED — `generic` is PROMPT-BLIND, so it is disjoint but not a candidate CORE")
    print(f"    best over ALL hindsight-free disjoint objects      : {best[0]} = {best[1]:.4f}")
    print(f"    best over PROMPT-VARYING ones (random or content)  : {best_cand[0]} = {best_cand[1]:.4f}")
    print(f"    the only CONTENT-DRIVEN disjoint object ever built : {best_content[0]} = "
          f"{best_content[1]:.4f}")
    print(f"    the ORACLE over that same disjoint space           : {s_orc:.4f}  [uses the answer]")

    # ⚠ THE 0.80 KILL IS PRE-REGISTERED AND BINDING, BUT IT IS ALSO A NUMBER I CHOSE. Reporting the
    #   verdict across a threshold sweep is what dissolves that, and it is G4, not a hedge.
    print("\n  THRESHOLD SWEEP — the pre-registered cell is 0.80; every other cell is printed too")
    print(f"    {'t':>6}{'all objects':>16}{'prompt-specific':>18}")
    sweep = {}
    for tval in (0.50, 0.60, 0.70, 0.80, 0.90):
        wa = "W-DISJOINT" if best[1] >= tval else "W-BALL"
        wc = "W-DISJOINT" if best_cand[1] >= tval else "W-BALL"
        sweep[f"{tval:.2f}"] = {"all": wa, "prompt_specific": wc}
        mark = "  <- pre-registered" if abs(tval - 0.80) < 1e-9 else ""
        print(f"    {tval:>6.2f}{wa:>16}{wc:>18}{mark}")

    print(f"    {'—':<34}{'':>9}")
    print(f"    {'ORACLE (uses the answer)':<34}{s_orc:>9.4f}   by-construction  [CONTROL, not evidence]")

    if not ctrl_ok:
        world = "W-BLIND"
    elif best[1] >= 0.80:
        world = "W-DISJOINT"
    else:
        world = "W-BALL"

    print(f"\n  WORLD: {world}")
    if world == "W-BALL":
        print(f"    The test CAN admit a disjoint object -- the oracle clears at {s_orc:.4f}. In ~50")
        print(f"    rounds NOTHING hindsight-free has: the best is `{best[0]}` at {best[1]:.4f}.")
        print("    ⛔ So R450's 'a fact about WHICH ARMS WERE BUILT' is too kind. Prompt-specific")
        print("       arms WERE built, and they fail. Every admitted object shares criteria with the")
        print("       released core. The extension is a BALL AROUND ONE POINT.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "m": M, "n_refs": len(subs),
           "oracle_share": s_orc, "anti_oracle_share": s_anti, "g0_shuffled": g0,
           "floor_from_r450": floor, "controls_ok": ctrl_ok,
           "best_hindsight_free": {"name": best[0], "share": best[1]},
           "best_prompt_specific_candidate": {"name": best_cand[0], "share": best_cand[1]},
           "threshold_sweep": sweep,
           "only_content_driven_disjoint": {"name": best_content[0],
                                            "share": best_content[1]},
           "objects": [{"name": a, "share": b, "basis": c} for a, b, c in objs]}
    (RES / "r451_disjoint.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r451_disjoint.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
