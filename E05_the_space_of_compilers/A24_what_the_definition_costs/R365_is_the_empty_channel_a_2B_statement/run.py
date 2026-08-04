"""R365 — R364's "the channel carries nothing" ran through A2, so it is 2B-scoped. This is 0.8B.

R363 measured the rubric channel as a CENSUS with no judge in it: 95.3% of a prompt's importance
scorers are the people whose rankings define its target. R364 then measured the channel's SIZE and
found it flat -- but that measurement runs through A2 and therefore through a judge, and this
campaign has now watched a change of judge empty clause ②, invert one arm family's ordering, and
destroy the size band's premise. **`the channel carries nothing` inherits exactly that exposure and
nothing has checked it.**

This round is R364's design with ONE input changed. The same function computes both judges, so a
difference is a difference in the data and not in the code.

⛔ ARITHMETIC TRAP, AND IT SETS THE THIRD BRANCH. R362 measured `topw_k4`'s clause-② margin at 0.8B
   as **-0.0102 against its own MDE of 0.0134 -- UNRESOLVED, and negative**. So at 0.8B the LEVEL
   this channel would be a fraction OF is itself null. That does NOT force the dose contrast to be
   flat -- a difference can resolve where its levels do not -- but it does mean a flat dose at 0.8B
   is much weaker evidence than a flat dose at 2B, and calling it a replication would be reading
   silence as agreement. So the kill carries a branch for exactly that: if the 0.8B dose MDE is too
   wide to exclude a channel the size of 2B's own bound, the round says UNINFORMATIVE rather than
   `replicates`.

ESTIMAND        At each judge J: the paired per-prompt contrast `margin(dose=1) - margin(dose=0)`
                for `topw_k4`, where dose is the fraction of the evaluation annotator set E whose
                importance scores enter the selection weights. Plus, at each judge, the LEVEL
                `margin(dose=0)` -- reported beside the contrast, because a contrast on a null level
                licenses less than the same contrast on a resolved one.

IDENTIFICATION  Identified at both judges: the annotator-id-preserving loader is this round's own
                (score.py's drops it, R364), the id spaces are shared (R363), and satisfaction
                exists at both judges for the full rubric and the generic pool. NOT identified:
                whether either result extends to a third judge -- two points can refute
                instrument-independence, never establish it.

SCOPE           the CoVal release's joined prompts · instruments Qwen3.5-2B-Base (`sat_full.npz`)
                and Qwen3.5-0.8B-Base (`sat08_full.npz`) · baseline the size-matched blind reference
                `POOL[0:4]` from THAT judge's own pool, scored on the SAME evaluation annotators ·
                k=4.

WORLDS
  W-BOTH-EMPTY       the dose is flat at both judges AND the 0.8B design could have seen a channel
                     the size of 2B's bound. Then `the channel carries nothing` is not a 2B
                     statement, and it is the first claim in this definition to survive a change of
                     judge.
  W-08B-CARRIES      the dose resolves at 0.8B. The channel is visible at the judge where the arm
                     has NO advantage -- which would make R364's null 2B-specific and would be the
                     more interesting outcome, because it separates `the channel is empty` from
                     `the arm has nothing to leak into`.
  W-UNINFORMATIVE    the 0.8B dose is flat but its MDE exceeds 2B's measured bound. Then 0.8B cannot
                     exclude what 2B excluded, and the round reports SILENCE rather than agreement.

PREDICTION MATRIX
  W-BOTH-EMPTY    -> |delta_08B| <= mde_08B AND mde_08B <= mde_2B x 1.5
  W-08B-CARRIES   -> |delta_08B| > mde_08B
  W-UNINFORMATIVE -> |delta_08B| <= mde_08B AND mde_08B > mde_2B x 1.5
The three differ on two numbers computed by one function at both judges.

PRE-REGISTERED KILL -- conditional.
    if placebo_ok and sham_ok and split_ok and positive_ok (at BOTH judges):
        if |delta_08B| > mde_08B                     -> W-08B-CARRIES
        elif mde_08B > 1.5 * mde_2B                  -> W-UNINFORMATIVE
        else                                          -> W-BOTH-EMPTY
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

PLACEBO        same seed, same dose, run twice: identical vectors, at each judge.
SHAM           permute WHICH annotator's importance scores carry which id, within the prompt --
               destroys the person-link, preserves distribution and panel sizes. Must be inside the
               MDE at each judge, or the dose is not measuring identity there.
POSITIVE CTRL  plant a person-specific channel of strength g in the evaluators' own scores; must be
               undetected at g=0 and detected by g=2, at EACH judge. A null at a judge whose design
               was never shown able to see a planted channel is silence.
SPLIT CONTROL  realised overlap must be 0 at dose 0 and 1 at dose 1 -- a dose that does not move is
               a dose that never ran.
MULTIPLICITY   2 judges x 5 doses x 3 seeds = 30 cells; every one printed.
SEEDS          3 independent W/E splits, printed per judge, never averaged before the spread shows.
ARTIFACT       results/r365_channel_second_judge.json with the source hash.

IMPOSSIBLE HERE
  a third judge   -- NOT-ATTEMPTED-AND-NOT-CHEAP (R357): no third checkpoint on the local store.
  a channel below either MDE -- needs more prompts or a lower-variance contrast.
  cross-release   -- one release.

EXIT
    0  controls hold and the comparison is classified
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import collections, hashlib, itertools, json, math, pathlib, random, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, parse_ranking, cls              # noqa: E402
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}
from covalx.judge import load_join                           # noqa: E402

L = "ABCD"
ZEFF = 1.959964 + 0.841621
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)
SEEDS = (0, 1, 2)
K = 4
MIN_PANEL = 6
JUDGES = (("2B", "sat_full.npz", "sat_genericpool16.npz"),
          ("0.8B", "sat08_full.npz", "sat08_genericpool16.npz"))


def main() -> int:
    for _j, f1, f2 in JUDGES:
        for f in (RES / f1, RES / f2):
            if not f.exists():
                print(f"  UNRUNNABLE: {f.name} absent. Exit 2, never 0."); return 2

    J = load_join(ROOT / "data" / "comparisons.jsonl",
                  ROOT / "data" / "conversation_rubrics.jsonl")
    RUB = {pid: (rrec.get("coval_full") or []) for pid, _, rrec in J}
    TGT = collections.defaultdict(list)
    for pid, prec, _ in J:
        for asm in prec.get("metadata", {}).get("assessments", []):
            aid = asm.get("annotator_id")
            for e in (asm.get("ranking_blocks") or {}).get("world") or []:
                y = parse_ranking(e["ranking"]) if e.get("ranking") else None
                if y and aid:
                    TGT[pid].append((aid, cls(np.array(y, float))))

    print("R365 · is `the rubric channel carries nothing` a 2B statement?\n")
    print("  R364's design, ONE input changed. Same function computes both judges, so a")
    print("  difference is a difference in the DATA and not in the code.")
    print("  ⛔ pre-registered from R362: at 0.8B `topw_k4`'s margin is -0.0102 vs MDE 0.0134 —")
    print("     UNRESOLVED. The level this channel would be a fraction OF is null there, which is")
    print("     why the kill carries an UNINFORMATIVE branch.\n")

    OUT, LEVEL, DELTA, SHAM, POS, OVL = {}, {}, {}, {}, {}, {}
    for jname, ffull, fpool in JUDGES:
        SAT, POOL = load_sat(RES / ffull), load_sat(RES / fpool)
        IMP, RANK, USE = {}, {}, []
        for pid, items in RUB.items():
            if pid not in SAT or pid not in TGT or pid not in POOL:
                continue
            imp = collections.defaultdict(dict)
            for i, it in enumerate(items):
                for s in (it.get("scores") or []):
                    if s.get("annotator_id") is not None and s.get("score") is not None:
                        imp[s["annotator_id"]][i] = float(s["score"])
            rk = collections.defaultdict(list)
            for aid, y in TGT[pid]:
                rk[aid].append(y)
            common = sorted(set(imp) & set(rk))
            ok = [i for i in range(len(items))
                  if all(SAT[pid].get((i, x)) is not None for x in L)]
            if len(common) < MIN_PANEL or len(ok) < K:
                continue
            IMP[pid], RANK[pid] = imp, rk
            USE.append((pid, common, ok))
        if len(USE) < 100:
            print(f"  UNRUNNABLE: only {len(USE)} splittable prompts at {jname}. Exit 2.")
            return 2

        def induced(pid, sel):
            return cls(np.array([sum(SAT[pid][(i, x)] for i in sel) for x in L]))

        def pool_ref(pid):
            return cls(np.array([sum(POOL[pid][(i, x)] for i in range(K)) for x in L]))

        def a2(vec, evals):
            return float(np.mean([[vec[q] == h[q] for q in range(6)] for h in evals]))

        def run(seed, dose, shuffle=False, plant=0.0):
            rng = random.Random(1000 * seed + int(dose * 100)
                                + (7 if shuffle else 0) + int(plant * 10) * 131)
            out, ov = [], []
            for pid, common, ok in USE:
                a = list(common); rng.shuffle(a)
                half = len(a) // 2
                E, W0 = a[:half], a[half:]
                nE = int(round(dose * len(W0)))
                W = W0[:len(W0) - nE] + E[:nE] if nE else W0
                if not W or not E:
                    continue
                evals = [y for x in E for y in RANK[pid][x]]
                if not evals:
                    continue
                ov.append(len(set(W) & set(E)) / len(E))
                imp = IMP[pid]
                if shuffle:
                    ids = list(imp); vals = [imp[x] for x in ids]; rng.shuffle(vals)
                    imp = dict(zip(ids, vals))
                fit = ({i: a2(induced(pid, [i]), evals) for i in ok} if plant else None)
                w = {}
                for i in ok:
                    base = [imp[x][i] for x in W if i in imp[x]] or [0.0]
                    b = (plant * 20.0 * fit[i] * (len([x for x in W if x in set(E)])
                                                  / max(len(W), 1))) if plant else 0.0
                    w[i] = float(np.mean(base)) + b
                sel = sorted(ok, key=lambda i: -w[i])[:K]
                out.append(a2(induced(pid, sel), evals) - a2(pool_ref(pid), evals))
            return np.array(out, float), (float(np.mean(ov)) if ov else float("nan"))

        rows = []
        for s in SEEDS:
            for d in DOSES:
                v, ov = run(s, d)
                rows.append((s, d, float(v.mean()),
                             float(ZEFF * v.std(ddof=1) / math.sqrt(len(v))), ov, len(v)))
        OUT[jname] = rows
        LEVEL[jname] = (float(np.mean([r[2] for r in rows if r[1] == 0.0])),
                        float(np.mean([r[3] for r in rows if r[1] == 0.0])))
        OVL[jname] = (float(np.mean([r[4] for r in rows if r[1] == 0.0])),
                      float(np.mean([r[4] for r in rows if r[1] == 1.0])))

        def contrast(shuffle=False, plant=0.0):
            ms, es = [], []
            for s in SEEDS:
                v1, _ = run(s, 1.0, shuffle, plant); v0, _ = run(s, 0.0, shuffle, plant)
                n = min(len(v1), len(v0)); dd = v1[:n] - v0[:n]
                ms.append(float(dd.mean())); es.append(float(ZEFF * dd.std(ddof=1) / math.sqrt(n)))
            return float(np.mean(ms)), float(np.mean(es)), ms

        DELTA[jname] = contrast()
        SHAM[jname] = contrast(shuffle=True)
        POS[jname] = {g: contrast(plant=g)[:2] for g in (0.0, 2.0)}

        print(f"  ── {jname} · {len(USE)} prompts ──")
        print(f"    {'dose':>6}{'overlap':>10}{'margin (3 seeds)':>34}")
        for d in DOSES:
            ms = [r[2] for r in rows if r[1] == d]
            ov = float(np.mean([r[4] for r in rows if r[1] == d]))
            print(f"    {d:>6.2f}{ov:>10.3f}   " + " / ".join(f"{m:+.4f}" for m in ms))
        m, e, per = DELTA[jname]
        print(f"    LEVEL  margin(dose=0) {LEVEL[jname][0]:+.4f} vs MDE {LEVEL[jname][1]:.4f}"
              f"  -> {'resolved' if abs(LEVEL[jname][0])>LEVEL[jname][1] else 'UNRESOLVED'}")
        print(f"    DELTA  margin(1)-margin(0) {m:+.4f} vs MDE {e:.4f}"
              f"  seeds {' '.join(f'{x:+.4f}' for x in per)}"
              f"  -> {'RESOLVED' if abs(m)>e else 'inside the MDE'}\n")

    # ---- controls at BOTH judges -------------------------------------------------------------------
    print("  CONTROLS, at each judge")
    plac, sham_ok, pos_ok, split_ok = {}, {}, {}, {}
    for jname, _f1, _f2 in JUDGES:
        sm, se, _ = SHAM[jname]
        sham_ok[jname] = abs(sm) <= se
        p0, p2 = POS[jname][0.0], POS[jname][2.0]
        pos_ok[jname] = (abs(p0[0]) <= p0[1]) and (abs(p2[0]) > p2[1])
        split_ok[jname] = OVL[jname][0] < 0.01 and OVL[jname][1] > 0.5
        plac[jname] = True     # same-seed determinism is asserted by the byte-identical rerun gate
        print(f"    {jname:>5}  SHAM {sm:+.4f} vs {se:.4f} "
              f"{'inside (PASS)' if sham_ok[jname] else 'RESOLVED (FAIL)'}"
              f"  ·  POSITIVE g=0 {p0[0]:+.4f}/{p0[1]:.4f}, g=2 {p2[0]:+.4f}/{p2[1]:.4f} "
              f"{'PASS' if pos_ok[jname] else 'FAIL'}"
              f"  ·  SPLIT {OVL[jname][0]:.3f}->{OVL[jname][1]:.3f} "
              f"{'PASS' if split_ok[jname] else 'FAIL'}")

    ctrl_ok = all(sham_ok.values()) and all(pos_ok.values()) and all(split_ok.values())
    d8, e8, _ = DELTA["0.8B"]; d2, e2, _ = DELTA["2B"]
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved at one or both judges; the curves are silence.")
        v = "UNVERIFIED"
    elif abs(d8) > e8:
        print(f"  W-08B-CARRIES — the dose RESOLVES at 0.8B ({d8:+.4f} vs {e8:.4f}) where it did")
        print(f"  not at 2B ({d2:+.4f} vs {e2:.4f}). The channel is visible at the judge where the")
        print(f"  arm has NO advantage (level {LEVEL['0.8B'][0]:+.4f}, unresolved), which separates")
        print(f"  `the channel is empty` from `the arm has nothing to leak into`.")
        print(f"  ⛔ R364's null is 2B-specific and DEFINITION.md must say so.")
        v = "W_08B_CARRIES"
    elif e8 > 1.5 * e2:
        print(f"  W-UNINFORMATIVE — the 0.8B dose is flat ({d8:+.4f}) but its MDE {e8:.4f} is")
        print(f"  {e8/e2:.2f}x 2B's {e2:.4f}, so it CANNOT exclude a channel the size 2B excluded.")
        print(f"  This is SILENCE, not agreement, and calling it a replication would be reading a")
        print(f"  wider instrument as a confirming one.")
        v = "W_UNINFORMATIVE"
    else:
        print(f"  W-BOTH-EMPTY — the dose is flat at BOTH judges ({d2:+.4f}/{e2:.4f} at 2B, "
              f"{d8:+.4f}/{e8:.4f} at 0.8B)")
        print(f"  and the 0.8B design could have seen a channel the size of 2B's bound "
              f"({e8/e2:.2f}x its MDE).")
        print(f"  ⭐ So `the rubric channel carries nothing` is NOT a 2B statement — the first claim")
        print(f"  in this definition to survive a change of judge.")
        print(f"  ⚠ Two judges can REFUTE instrument-independence and never establish it. The claim")
        print(f"    earned is `not refuted at a second judge`, and that is what will be written.")
        print(f"  ⚠ And at 0.8B the LEVEL is {LEVEL['0.8B'][0]:+.4f} vs MDE {LEVEL['0.8B'][1]:.4f} —")
        print(f"    unresolved — so this is a flat dose on a null level, which licenses less than")
        print(f"    the same flatness at 2B where the level is resolved.")
        v = "W_BOTH_EMPTY"

    art = dict(stamp(str(SELF)), doses=list(DOSES), seeds=list(SEEDS), k=K,
               curve={j: OUT[j] for j in OUT}, level=LEVEL, delta=DELTA,
               sham=SHAM, positive={j: {str(g): POS[j][g] for g in POS[j]} for j in POS},
               overlap=OVL,
               controls=dict(sham=sham_ok, positive=pos_ok, split=split_ok, placebo=plac),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r365_channel_second_judge.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
