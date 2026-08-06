#!/usr/bin/env python3
"""R803 · the judge-free floor on release ONE — what does a word count score against the same humans?

CHECK #405 killed R802's NEXT (scoring an arm on release two needs a judge pass that does not exist —
every `sat_*.npz` is keyed to release one) and found a better question in the same place: R433
measured a core "losing to a judge-free length heuristic by −0.0545" on release TWO, and the FIRST
release — where every committed A2 in this campaign lives — has never been checked against one.

ESTIMAND        E1 ⭐ the judge-free predictors' A2 · E2 ⭐ the 27 arms against the floor · E3 ⭐ the
                decisive pair · E4 D4's partialling — "beats length" vs "IS length"
IDENTIFICATION  exact; ⚠ E4's residual is a LOWER bound, since partialling removes shared prompt
                difficulty along with length
DERIVED FIRST   D1 a judge-free predictor is a FLOOR, not a rival · D2 the sign is not forced, so this
                is a measurement · D3 the comparison is paired and needs no new instrument ·
                D4 if length predicts criterion satisfaction the arms inherit its power
WORLDS          A the arms beat it · B the floor sits at their level · C the floor is above them —
                C checked FIRST
CONTROLS        OBJECT (reproduce a committed A2 from raw text) · PLACEBO (a constant predictor gives
                exactly the human tie rate, computed) · POSITIVE (`oracle_k4` must beat the floor) ·
                NEGATIVE (lengths shuffled within prompt) · CONFOUND (D4) · NOISE FLOOR
"""
import hashlib
import itertools
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                    # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R789 = ARC / "R789_how_many_levels_the_a2_axis_resolves/results/ladder.json"
L = "ABCD"
PR = list(itertools.combinations(range(4), 2))
ZEFF = 2.801585
NBOOT = 1200
SEEDS = [31337, 31338, 31339]


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def bh(pv, q=0.05):
    pv = np.asarray(pv, float)
    m = len(pv)
    order = np.argsort(pv)
    kmax = 0
    for r, i in enumerate(order, start=1):
        if pv[i] <= q * r / m:
            kmax = r
    keep = np.zeros(m, bool)
    keep[order[:kmax]] = True
    return keep


def main():
    out = {"instrument_unit": "a (prompt, annotator) judgement", "claim_unit": "an ARM",
           "e1_unit": "a PREDICTOR"}

    print("  OBJECT CHECK")
    lad = json.loads(R789.read_text())
    targets, _ = load_targets()
    SC = load_sat(RES / "sat_coval_core.npz")
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")

    # response TEXT from the raw release
    text = {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        rs = r.get("responses") or []
        if len(rs) != 4:
            continue
        got = []
        for it in rs:
            msgs = it.get("messages") or []
            got.append(" ".join(str(m.get("content", "")) for m in msgs
                                if isinstance(m, dict)))
        text[r["prompt_id"]] = got
    pids = sorted(p for p in base if p in targets and p in POOL and p in text
                  and len(targets[p]) >= 2)
    P = len(pids)
    HC = [np.array([cls(np.array(y, float)) for y, _ in targets[p]]) for p in pids]
    print(f"     prompts with 4 responses AND annotators: {P}")

    def a2_from_scores(S):
        """S (P,4) any per-response score -> per-prompt A2 against all annotators."""
        v = np.zeros(P)
        for a in range(P):
            s = np.sign(S[a][[u for u, _ in PR]] - S[a][[w for _, w in PR]])
            v[a] = (HC[a] == s).mean()
        return v

    core = np.array([cls(yvec(SC[p], sorted({i for i, _ in SC[p]}))) for p in pids], float)
    a2_core = np.array([(HC[a] == core[a]).mean() for a in range(P)])
    ref = lad["e2"]["a2"]["coval_core"]
    okobj = abs(float(a2_core.mean()) - ref) < 1e-9
    print(f"     `coval_core` recomputed from raw text+annotators {a2_core.mean():.10f} vs R789's "
          f"committed {ref:.10f}   {'PASS' if okobj else 'FAIL'}")
    if not okobj or P < 900:
        print("  UNRUNNABLE: a committed arm did not reproduce, or the population is short. Exit 2.")
        return 2
    out["object"] = {"prompts": P, "coval_core": float(a2_core.mean()), "committed": ref}

    # ================= E1 · the judge-free predictors ============================================
    print("\n  E1 - THE JUDGE-FREE PREDICTORS  (no judge, no rubric, no criteria)")
    CH = np.array([[len(t) for t in text[p]] for p in pids], float)
    TK = np.array([[len(t.split()) for t in text[p]] for p in pids], float)
    POS = np.tile(np.arange(4, dtype=float), (P, 1))
    preds = {}
    for lab, S in (("characters", CH), ("tokens", TK), ("position", POS)):
        for sgn, dl in ((+1.0, "longer-is-better"), (-1.0, "shorter-is-better")):
            v = a2_from_scores(sgn * S)
            preds[f"{lab} ({dl})"] = v
            print(f"     {lab:<12} {dl:<20} A2 {v.mean():.4f}")
    floor_lab = max(preds, key=lambda k: preds[k].mean())
    floor = preds[floor_lab]
    print(f"     ⭐ the FLOOR is `{floor_lab}` at {floor.mean():.4f}   ⚠ a MAX over "
          f"{len(preds)} predictors is a selection, and all {len(preds)} are printed above")
    out["e1"] = {k: float(v.mean()) for k, v in preds.items()}
    out["e1_floor"] = {"label": floor_lab, "a2": float(floor.mean())}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    tie = a2_from_scores(np.zeros((P, 4)))
    human_tie = float(np.mean([(HC[a] == 0).mean() for a in range(P)]))
    plac_ok = abs(float(tie.mean()) - human_tie) < 1e-12
    print(f"     PLACEBO   a CONSTANT predictor: A2 {tie.mean():.10f}   the human tie rate "
          f"{human_tie:.10f}   {'PASS -- identical, as derived' if plac_ok else 'FAIL'}")

    rng = np.random.default_rng(SEEDS[0])
    BI = rng.integers(0, P, size=(NBOOT, P))

    def ci(d):
        b = d[BI].mean(axis=1)
        lo, hi = float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))
        p = 2.0 * min(float((b <= 0).mean()), float((b >= 0).mean()))
        mde = ZEFF * float(d.std(ddof=1)) / math.sqrt(P)
        return (float(d.mean()), lo, hi, max(min(p, 1.0), 1.0 / (NBOOT + 1)), mde,
                bool((lo > 0 or hi < 0) and abs(d.mean()) >= mde))

    SO = load_sat(RES / "sat_oracle_k4.npz")
    orc = np.array([cls(yvec(SO[p], sorted({i for i, _ in SO[p]}))) for p in pids], float)
    a2_orc = np.array([(HC[a] == orc[a]).mean() for a in range(P)])
    e, lo, hi, _, _, res = ci(a2_orc - floor)
    posok = res and e > 0
    print(f"     POSITIVE  `oracle_k4` (reads the target) − floor {e:+.4f} [{lo:+.4f}, {hi:+.4f}]   "
          f"{'PASS -- the comparison can detect a real difference' if posok else 'FAIL'}")
    print(f"               band COMPUTED at both ends: placebo {tie.mean():.4f} → oracle "
          f"{a2_orc.mean():.4f}")

    nrng = np.random.default_rng(SEEDS[0] + 13)
    SH = np.array([CH[a][nrng.permutation(4)] for a in range(P)])
    v_sh = a2_from_scores(SH)
    negok = v_sh.mean() < floor.mean() - 0.01
    print(f"     NEGATIVE  lengths shuffled WITHIN each prompt: floor {floor.mean():.4f} → "
          f"{v_sh.mean():.4f}   {'PASS' if negok else 'FAIL'}")
    print(f"               world it excludes: 'the predictor scores well because of how the class is "
          f"built rather than because length tracks the humans'")

    frng = np.random.default_rng(SEEDS[0] + 17)
    halves = []
    for _ in range(20):
        h1 = np.zeros(P)
        h2 = np.zeros(P)
        sgn = np.sign(np.array([1.0]))
        for a in range(P):
            k = HC[a].shape[0]
            pm = frng.permutation(k)
            i1, i2 = pm[:k // 2], pm[k // 2:2 * (k // 2)]
            S = (1.0 if "longer" in floor_lab else -1.0) * (CH if "char" in floor_lab
                                                            else TK if "token" in floor_lab else POS)
            s = np.sign(S[a][[u for u, _ in PR]] - S[a][[w for _, w in PR]])
            h1[a] = (HC[a][i1] == s).mean()
            h2[a] = (HC[a][i2] == s).mean()
        halves.append(abs(h1.mean() - h2.mean()))
    print(f"     NOISE FLOOR  annotator split-half on the floor, 20 draws: {np.mean(halves):.6f}")

    gate = okobj and plac_ok and posok and negok
    out["controls"] = {"placebo": float(tie.mean()), "human_tie": human_tie, "placebo_ok": plac_ok,
                       "oracle_minus_floor": e, "positive_ok": posok,
                       "neg_shuffled": float(v_sh.mean()), "negative_ok": negok,
                       "split_half": float(np.mean(halves)), "gate": gate}
    print(f"     GATE      {'PASS -- the kill may evaluate' if gate else 'FAIL -- UNVERIFIED'}")

    # ================= E2/E3/E4 · the arms against the floor =====================================
    print("\n  E2/E3 - THE 27 COMMITTED ARMS AGAINST THE FLOOR")
    rows, pv = [], []
    for t in sorted(lad["e2"]["a2"]):
        f = RES / f"sat_{t}.npz"
        if not f.is_file():
            continue
        S = load_sat(f)
        if not set(pids) <= set(S):
            continue
        cm = np.array([cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in pids], float)
        v = np.array([(HC[a] == cm[a]).mean() for a in range(P)])
        e_, l_, h_, p_, m_, r_ = ci(v - floor)
        # D4: partial the floor out of the arm's per-prompt A2
        A = np.vstack([floor, np.ones_like(floor)]).T
        co, *_ = np.linalg.lstsq(A, v, rcond=None)
        rows.append({"arm": t, "a2": float(v.mean()), "eff": e_, "lo": l_, "hi": h_, "p": p_,
                     "mde": m_, "resolved": r_, "slope_on_floor": float(co[0]),
                     "resid_mean": float(np.mean(v - A @ co))})
        pv.append(p_)
    keep = bh(np.array(pv))
    rows.sort(key=lambda r: -r["a2"])
    nbeat = sum(1 for i, r in enumerate(rows) if r["resolved"] and r["eff"] > 0)
    nbeat_bh = sum(1 for r, k in zip(sorted(rows, key=lambda x: x["p"]), sorted(keep, reverse=True))
                   if k and r["resolved"] and r["eff"] > 0)
    for r in rows[:4] + [x for x in rows if x["arm"] in ("coval_core", "full")] + rows[-3:]:
        print(f"     {r['arm']:<24} A2 {r['a2']:.4f}   − floor {r['eff']:+.4f} "
              f"[{r['lo']:+.4f}, {r['hi']:+.4f}]  {'RESOLVED' if r['resolved'] else 'unresolved'}")
    med = float(np.median([r["a2"] for r in rows]))
    print(f"     ⭐ the floor {floor.mean():.4f} vs the arms: min {min(r['a2'] for r in rows):.4f}  "
          f"median {med:.4f}  max {max(r['a2'] for r in rows):.4f}")
    print(f"     ⭐ arms beating the floor resolvedly: {nbeat} of {len(rows)}   after BH "
          f"{int(keep.sum())} of {len(rows)} survive the correction")
    out["e2"] = {"rows": rows, "n_beat": nbeat, "bh_surviving": int(keep.sum()),
                 "arms": len(rows), "median_arm": med}

    print("\n  E4 - D4's PARTIALLING: 'BEATS LENGTH' VERSUS 'IS LENGTH'")
    sl = np.array([r["slope_on_floor"] for r in rows])
    print(f"     slope of an arm's per-prompt A2 on the floor's: mean {sl.mean():+.4f}  range "
          f"[{sl.min():+.4f}, {sl.max():+.4f}]")
    cc = [r for r in rows if r["arm"] == "coval_core"][0]
    print(f"     `coval_core` slope on the floor {cc['slope_on_floor']:+.4f}   residual mean "
          f"{cc['resid_mean']:+.6f}")
    print(f"     ⚠ the residual is a LOWER bound — partialling removes shared PROMPT difficulty "
          f"along with length")
    out["e4"] = {"slope_mean": float(sl.mean()), "slope_min": float(sl.min()),
                 "slope_max": float(sl.max())}

    print("\n  THE KILL -- conditional, gated on the controls")
    inrange = min(r["a2"] for r in rows) <= floor.mean() <= max(r["a2"] for r in rows)
    if not gate:
        world = "UNVERIFIED"
    elif floor.mean() > med:
        world = "C"
    elif nbeat >= 20:
        world = "A"
    elif nbeat < 14 and inrange:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     gate {gate}   floor {floor.mean():.4f}   median arm {med:.4f}   arms beating it "
          f"{nbeat} of {len(rows)}  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/judge_free_floor.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True).stdout.strip()
    except Exception:
        sha = "unknown"
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
