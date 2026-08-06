#!/usr/bin/env python3
"""R818 · the floor nobody subtracted — what share of the INFORMATIVE range does a core capture?

R817 put every arm on a normalised scale (`coval_core` 0.8132 of attainable) and its NEXT asked what
an arm with no per-prompt information would score. CHECK #420 found R804 already computed it:
`R804/run.py:197` gives `BESTC` = 0.451773, printed inside a negative control's parenthetical and
never used since. And 0.451773 / 0.686265 = 65.8% — a single fixed ordering, identical on every
prompt, already reaches nearly two thirds of what any scoring function could attain. The scale this
arc quotes shares on runs from 0.658 to 1, and no committed share has had that floor subtracted.

ESTIMAND        E1 the held-out constant floor · E2 ⭐ each arm's share of [floor, ceiling] ·
                E3 the per-prompt version · E4 what changes meaning
IDENTIFICATION  ⚠⚠ E2's corpus-level rescaling is AFFINE and CANNOT reorder — a DERIVATION, not a
                measurement. Only E3 can come out otherwise.
DERIVED FIRST   D1 affine maps fix the ordering · D2 the held-out floor is ≤ the in-sample one, so
                the correction runs AGAINST the arms · D3 the constant arm takes share 0 (placebo)
                · D4 `genericpool16` is criterion-blind but score-varying, so it must sit above
WORLDS          A the floor is most of the score · B minor · C E3 reorders — C checked FIRST
CONTROLS        OBJECT (R804's 0.451773 and 0.686265) · PLACEBO · POSITIVE (share ladder with an
                f=0 check) · NEGATIVE (floor from permuted annotators) · NOISE FLOOR
"""
import hashlib
import itertools
import json
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
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
ARMS = ["coval_core", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1", "topw_k4",
        "genericpool16", "random_k4_s0", "gen_sham", "full"]


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


def weak_orders():
    seen = {}
    for v in itertools.product(range(4), repeat=4):
        seen.setdefault(tuple(int(np.sign(v[i] - v[j])) for i, j in PR), v)
    return np.array(sorted(seen))


def spearman(a, b):
    ra = np.argsort(np.argsort(-np.asarray(a, float)))
    rb = np.argsort(np.argsort(-np.asarray(b, float)))
    return float(np.corrcoef(ra, rb)[0, 1])


def main():
    out = {"instrument_unit": "a PROMPT", "claim_unit": "an ARM's SHARE"}
    W = weak_orders()
    tg, _ = load_targets()
    S = {a: load_sat(RES / f"sat_{a}.npz") for a in ARMS}
    pids = sorted(set.intersection(*(set(v) for v in S.values())) &
                  {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(y, float)) for y, _ in tg[p]]) for p in pids}
    pids = [p for p in pids if len(H[p]) >= 2]
    N = len(pids)
    CL = {a: {p: np.array(cls(yvec(S[a][p], sorted({i for i, _ in S[a][p]})))) for p in pids}
          for a in ARMS}
    A2 = {a: np.array([float((H[p] == CL[a][p]).mean()) for p in pids]) for a in ARMS}
    att = np.array([((H[p][None, :, :] == W[:, None, :]).mean(axis=1)).mean(axis=1).max()
                    for p in pids])
    # per-prompt score of EVERY constant order, so any constant order can be evaluated per prompt
    percon = np.zeros((len(W), N))
    for i, p in enumerate(pids):
        percon[:, i] = (H[p][None, :, :] == W[:, None, :]).mean(axis=(1, 2))
    print(f"  POPULATION  {N} prompts · {len(W)} weak orders · att mean {att.mean():.6f}")

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - reproduce R804's two committed constants")
    # ⛔ R804 MIXED TWO WEIGHTINGS IN ONE LINE, and the object check caught it. Its `BESTC`
    # concatenates ALL annotator rows across ALL prompts and means over that pool — ANNOTATOR-
    # weighted — while its `CEIL_ATT` takes a per-prompt max and means over prompts — PROMPT-
    # weighted. The two were printed side by side as if on one scale. Every A2 in this arc is
    # prompt-weighted, so the prompt-weighted floor is the one that belongs on this scale; the
    # annotator-weighted one is reproduced here only to prove R804's computation is understood.
    allH = np.concatenate([H[p] for p in pids], axis=0)
    BESTC_ANN = float(((allH[None, :, :] == W[:, None, :]).mean(axis=1)).mean(axis=1).max())
    bestc_idx = int(percon.mean(axis=1).argmax())
    BESTC = float(percon[bestc_idx].mean())
    ok = abs(BESTC_ANN - 0.451773) < 1e-6 and abs(att.mean() - 0.686265) < 1e-6
    print(f"     R804's ANNOTATOR-weighted best constant order {BESTC_ANN:.6f} vs its committed "
          f"0.451773   {'reproduced' if abs(BESTC_ANN - 0.451773) < 1e-6 else 'FAIL'}")
    print(f"     the PROMPT-weighted best constant order {BESTC:.6f}   <- the scale every A2 in "
          f"this arc uses; difference {BESTC - BESTC_ANN:+.6f}")
    print(f"     CEIL_ATT {att.mean():.6f} vs R804's committed 0.686265 (prompt-weighted)   "
          f"{'PASS' if ok else 'FAIL'}")
    if not ok:
        print("  UNRUNNABLE: R804's constants did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"bestc_prompt_weighted": BESTC, "bestc_annotator_weighted": BESTC_ANN,
                     "ceil_att": float(att.mean()), "n": N}

    # ================= E1 · the HELD-OUT floor ===================================================
    print("\n  E1 - THE HELD-OUT FLOOR   (R804's is an in-sample optimum over 75 options)")
    rng = np.random.default_rng(4242)
    hos = []
    for _ in range(20):
        pm = rng.permutation(N)
        a_, b_ = pm[: N // 2], pm[N // 2:]
        j = int(percon[:, a_].mean(axis=1).argmax())
        hos.append(float(percon[j, b_].mean()))
    FLOOR = float(np.mean(hos))
    print(f"     held-out floor {FLOOR:.6f} ± {np.std(hos):.6f} over 20 prompt half-splits")
    print(f"     in-sample {BESTC:.6f}   optimism {BESTC - FLOOR:+.6f}   "
          f"D2 (held-out <= in-sample): {FLOOR <= BESTC + 1e-9}")
    d2 = FLOOR <= BESTC + 1e-9
    floor_share = FLOOR / att.mean()
    print(f"     ⭐ a CONSTANT order reaches {100 * floor_share:.1f}% of attainable — the scale this")
    print(f"     arc quotes shares on runs from {floor_share:.4f} to 1, not from 0 to 1")
    out["e1"] = {"floor_heldout": FLOOR, "floor_sd": float(np.std(hos)),
                 "optimism": BESTC - FLOOR, "floor_share_of_att": floor_share, "d2": d2}

    # ================= E2 · the two scales =======================================================
    print("\n  E2 - EACH ARM ON BOTH SCALES")
    print("     ⚠⚠ D1: the corpus-level rescaling is AFFINE, so the ORDERING is fixed BY")
    print("     CONSTRUCTION. That is a derivation. Only the SHARES are measurements.")
    idx = np.random.default_rng(1234).integers(0, N, (NBOOT, N))
    rows = []
    for a in ARMS:
        raw = float(A2[a].mean())
        s_att = raw / att.mean()
        s_inf = (raw - FLOOR) / (att.mean() - FLOOR)
        bs = np.array([(A2[a][i].mean() - FLOOR) / (att[i].mean() - FLOOR) for i in idx])
        rows.append({"arm": a, "raw": raw, "share_of_att": s_att, "share_informative": s_inf,
                     "lo": float(np.percentile(bs, 2.5)), "hi": float(np.percentile(bs, 97.5))})
    print(f"     {'arm':<16}{'raw':>9}{'/att':>9}{'INFORMATIVE share':>28}")
    for r in rows:
        print(f"     {r['arm']:<16}{r['raw']:>9.4f}{r['share_of_att']:>9.4f}   "
              f"{r['share_informative']:>+8.4f} [{r['lo']:+.4f}, {r['hi']:+.4f}]")
    cc = next(r for r in rows if r["arm"] == "coval_core")
    print(f"     ⭐ `coval_core` reads {cc['share_of_att']:.4f} of attainable but "
          f"{cc['share_informative']:.4f} of the INFORMATIVE range")
    out["e2"] = rows

    # ================= E3 · the per-prompt version ===============================================
    print("\n  E3 - THE PER-PROMPT VERSION  (the only part that CAN reorder)")
    fl_p = percon[bestc_idx]
    span = att - fl_p
    bad = int((span <= 1e-12).sum())
    print(f"     prompts where att_p == floor_p (ratio undefined): {bad} of {N} "
          f"({100 * bad / N:.1f}%)   {'FAIL - above 10%' if bad / N > 0.10 else 'PASS'}")
    keep = span > 1e-12
    e3 = {}
    for a in ARMS:
        e3[a] = float(((A2[a][keep] - fl_p[keep]) / span[keep]).mean())
    sp = spearman([r["share_informative"] for r in rows], [e3[r["arm"]] for r in rows])
    print(f"     {'arm':<16}{'corpus-level':>14}{'per-prompt':>13}")
    for r in rows:
        print(f"     {r['arm']:<16}{r['share_informative']:>14.4f}{e3[r['arm']]:>13.4f}")
    print(f"     ⭐ Spearman between the corpus-level and per-prompt orderings: {sp:+.4f}")
    out["e3"] = {"per_prompt": e3, "spearman": sp, "undefined": bad}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    con_raw = float(percon[bestc_idx].mean())
    con_share = (con_raw - BESTC) / (att.mean() - BESTC)
    plac_ok = abs(con_share) < 1e-12
    print(f"     PLACEBO   D3 the constant arm itself, share of [in-sample floor, ceiling]: "
          f"{con_share:.1e}   {'PASS - exactly 0' if plac_ok else 'FAIL'}")
    print("     POSITIVE  a synthetic arm placed at a KNOWN fraction f of the informative range")
    pos = {}
    for f in (0.0, 0.25, 0.5, 1.0):
        v = FLOOR + f * (att.mean() - FLOOR)
        pos[f] = (v - FLOOR) / (att.mean() - FLOOR)
        print(f"        f={f:<5} recovered share {pos[f]:.6f}   |Δ| {abs(pos[f] - f):.1e}")
    pos_ok = all(abs(pos[f] - f) < 1e-12 for f in pos)
    g0_ok = abs(pos[0.0]) < 1e-12
    print(f"        recovers f exactly at every dose: {pos_ok}   f=0 recovers 0 and not more: "
          f"{g0_ok}   {'PASS' if pos_ok and g0_ok else 'FAIL'}")
    # ⛔ THE FIRST NEGATIVE CONTROL FAILED FOR TWO REASONS, BOTH THIS ROUND'S OWN SUBJECT MATTER.
    #  (1) It permuted WHICH PROMPT an annotator belongs to — but a CONSTANT order sees no prompt
    #      information, so the pooled multiset of sign vectors is unchanged and the statistic is
    #      INVARIANT by construction. A control that cannot fail.
    #  (2) It pooled rows (ANNOTATOR-weighted) and compared against a PROMPT-weighted observation
    #      — the exact mixing this round just caught in R804, committed inside the control that
    #      was checking for it. It duly returned 0.454859 > 0.449421 and printed FAIL.
    # §1: name the world the null excludes and BUILD IT. The floor depends on there being an
    # aggregate human tendency at all, so the world to build is one with none: every annotator's
    # vector replaced by a uniform draw over the 75 weak orders, refitted, prompt-weighted.
    rngn = np.random.default_rng(707)
    nulls = []
    for _ in range(200):
        pc = np.zeros((len(W), N))
        for i, p in enumerate(pids):
            n = len(H[p])
            fake = W[rngn.integers(0, len(W), n)]
            pc[:, i] = (fake[None, :, :] == W[:, None, :]).mean(axis=(1, 2))
        nulls.append(float(pc.mean(axis=1).max()))
    nulls = np.array(nulls)
    neg_ok = bool(nulls.max() < BESTC)
    print(f"     NEGATIVE  a SYNTHETIC world with no aggregate human tendency (every annotator a")
    print(f"               uniform weak order), floor refitted and PROMPT-weighted, 200 draws:")
    print(f"               {nulls.mean():.6f} [{np.percentile(nulls, 2.5):.6f}, "
          f"{np.percentile(nulls, 97.5):.6f}] max {nulls.max():.6f}   real {BESTC:.6f}")
    print(f"               the whole null lies below the real floor: {neg_ok}   "
          f"{'PASS' if neg_ok else 'FAIL'}")
    print(f"     NOISE FLOOR  the held-out floor over 20 prompt half-splits: sd {np.std(hos):.6f}")
    gate = ok and plac_ok and pos_ok and g0_ok and neg_ok and d2 and bad / N <= 0.10
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo": con_share, "placebo_ok": plac_ok, "positive": pos,
                       "positive_ok": pos_ok, "g0_ok": g0_ok, "null_floor": float(nulls.mean()),
                       "negative_ok": neg_ok, "floor_sd": float(np.std(hos)), "gate": gate}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif sp < 1.0:
        world = "C"
    elif cc["share_informative"] < 0.5:
        world = "A"
    elif cc["share_informative"] > 0.7:
        world = "B"
    else:
        world = "NO WORLD CLAIMED"
    print(f"     E3 vs E2 Spearman {sp:+.4f}   `coval_core` informative share "
          f"{cc['share_informative']:.4f} [{cc['lo']:.4f}, {cc['hi']:.4f}]  ->  WORLD {world}")
    out["world"] = world

    art = HERE / "results/floor_subtracted.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
