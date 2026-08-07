#!/usr/bin/env python3
"""R821 · which definition is the deliverable — ②∧③∧④, or ②∧③?

CHECK #423 read the head of DEFINITION.md, which eighteen rounds of this session appended to without
opening. The file states TWO definitions and says so about itself: the head conjoins ②∧③∧④, while
line 1820 carries "the definition is ② ∧ ③" (R519, R599) annotated with "the retirement reached the
claim table and not this sentence, which is why the deliverable stated two different definitions for
80 rounds." And R803 built exactly the rule family ④ names — six judge-free predictors, best 0.4557 —
measuring 27 of 27 arms beating it, an independent replication of ④'s committed 0 of 42.

ESTIMAND        E1 ④'s exclusion count on the current arm set · E2 ⭐ can ④ exclude ANYTHING at home
                · E3 the contradiction counted mechanically · E4 the decision and the repair
IDENTIFICATION  E3 is a SEARCH and therefore an instrument: run where the answer is known first
DERIVED FIRST   D1 a constant order reads nothing, so ④'s bar is at least R803's 0.4557 · D2 an arm
                below the floor MUST be removed if ④ is implemented as written · D3 ④'s zero was
                defended as a SCOPE claim · D4 this round settles what the file says and what the
                evidence supports, not what the definition SHOULD be
WORLDS          A free-but-real · B binds at home · C unfalsifiable — C checked FIRST
CONTROLS        OBJECT · PLACEBO (the floor against itself) · POSITIVE (planted below-floor arms
                with a delta=0 check) · NEGATIVE (floor permuted) · NOISE FLOOR (margin CIs)
"""
import hashlib
import itertools
import json
import pathlib
import re
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                    # noqa: E402
from assurance.null_is_informative import assert_null_is_informative   # noqa: E402

RES = ROOT / "corebench/results"
HERE = pathlib.Path(__file__).resolve().parent
ARC = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
DEFN = ROOT / "E05_the_space_of_compilers/DEFINITION.md"
R803J = ARC / "R803_the_judge_free_floor_on_release_one/results/judge_free_floor.json"
PR = list(itertools.combinations(range(4), 2))
NBOOT = 1200
L = "ABCD"


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    raise TypeError(type(o))


def main():
    out = {"instrument_unit": "an ARM", "claim_unit": "a CLAUSE"}
    tg, _ = load_targets()
    r803 = json.loads(R803J.read_text())
    FLOOR_COMMITTED = 0.4557

    # ---- rebuild R803's judge-free floor from the raw release ----------------------------------
    text = {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        rs = r.get("responses") or []
        if len(rs) != 4:
            continue
        text[r["prompt_id"]] = [" ".join(str(m.get("content", "")) for m in (it.get("messages")
                               or []) if isinstance(m, dict)) for it in rs]
    base = load_sat(RES / "sat_random_k4_s0.npz")
    pids = sorted(p for p in base if p in tg and p in text and len(tg[p]) >= 2)
    H = {p: np.array([cls(np.array(y, float)) for y, _ in tg[p]]) for p in pids}
    N = len(pids)
    CH = np.array([[len(t) for t in text[p]] for p in pids], float)

    def score_from(Smat):
        v = np.zeros(N)
        for i, p in enumerate(pids):
            s = np.sign(Smat[i][[u for u, _ in PR]] - Smat[i][[w for _, w in PR]])
            v[i] = float((H[p] == s).mean())
        return v

    floor_v = score_from(CH)
    FLOOR = float(floor_v.mean())
    print(f"  POPULATION  {N} prompts · judge-free floor (characters, longer-is-better) "
          f"{FLOOR:.6f}")

    # ================= OBJECT ====================================================================
    print("\n  OBJECT CHECK - reproduce R803's floor and its 27-of-27 count")
    arms = sorted(p.stem[4:] for p in RES.glob("sat_*.npz")
                  if not p.stem.startswith("sat08") and "_08b" not in p.stem)
    S, A2 = {}, {}
    for a in arms:
        try:
            sat = load_sat(RES / f"sat_{a}.npz")
        except Exception:
            continue
        if not all(p in sat for p in pids):
            continue
        S[a] = sat
        A2[a] = np.array([float((H[p] == np.array(cls(yvec(sat[p],
                          sorted({i for i, _ in sat[p]}))))).mean()) for p in pids])
    ok = abs(FLOOR - FLOOR_COMMITTED) < 5e-5
    print(f"     floor {FLOOR:.6f} vs R803's committed {FLOOR_COMMITTED}   "
          f"{'PASS' if ok else 'FAIL'}")
    print(f"     arms scoreable on this population: {len(A2)}")
    if not ok:
        print("  UNRUNNABLE: R803's floor did not reproduce. Exit 2, never 0.")
        return 2
    out["object"] = {"floor": FLOOR, "n_arms": len(A2), "n_prompts": N}

    # ================= E1 · ④'s exclusion count ==================================================
    print("\n  E1 - CLAUSE ④ ON THE CURRENT ARM SET")
    print("     ⚠ D1: a constant order reads NOTHING, so it belongs to 'rules computable from the")
    print("     response set alone'; ④'s bar is at least max(0.4557, 0.449421) = R803's floor.")
    rng = np.random.default_rng(1234)
    idx = rng.integers(0, N, (NBOOT, N))
    rows = []
    for a in sorted(A2, key=lambda a: -A2[a].mean()):
        d = A2[a] - floor_v
        bs = d[idx].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        verdict = "PASSES ④" if lo > 0 else ("EXCLUDED by ④" if hi < 0 else "UNVERIFIED")
        rows.append({"arm": a, "a2": float(A2[a].mean()), "margin": float(d.mean()),
                     "lo": lo, "hi": hi, "verdict": verdict})
    excl = [r for r in rows if r["verdict"] == "EXCLUDED by ④"]
    unv = [r for r in rows if r["verdict"] == "UNVERIFIED"]
    print(f"     {'arm':<26}{'A2':>9}{'margin vs floor':>28}  verdict")
    for r in rows[:3] + rows[-4:]:
        print(f"     {r['arm']:<26}{r['a2']:>9.4f}   {r['margin']:+.4f} "
              f"[{r['lo']:+.4f}, {r['hi']:+.4f}]  {r['verdict']}")
    print(f"     ⭐ ④ EXCLUDES {len(excl)} of {len(rows)} arms   UNVERIFIED (CI straddles 0): "
          f"{len(unv)} {[r['arm'] for r in unv] if unv else ''}")
    out["e1"] = {"rows": rows, "excluded": len(excl), "unverified": len(unv)}

    # ================= E2 · can ④ exclude anything? ==============================================
    print("\n  E2 - CAN ④ EXCLUDE ANYTHING AT HOME?  (the test no round has run)")
    print("     A clause measured at 0 of 42 and 0 of 27 is either free-but-binding-elsewhere or")
    print("     UNFALSIFIABLE. The difference is testable: plant an arm below the floor.")
    planted = {}
    for delta in (0.10, 0.05, 0.01, 0.0):
        # an arm that agrees with the floor's ordering but is degraded on a random subset
        v = floor_v.copy()
        if delta > 0:
            k = int(N * delta / max(floor_v.mean(), 1e-9))
            hurt = rng.permutation(N)[:min(k, N)]
            v[hurt] = 0.0
        d = v - floor_v
        bs = d[idx].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        removed = hi < 0
        planted[delta] = {"a2": float(v.mean()), "margin": float(d.mean()), "lo": lo, "hi": hi,
                          "removed": bool(removed)}
        print(f"        delta={delta:<5} arm A2 {v.mean():.4f}   margin {d.mean():+.4f} "
              f"[{lo:+.4f}, {hi:+.4f}]   ④ removes it: {removed}")
    pos_ok = all(planted[d]["removed"] for d in (0.10, 0.05, 0.01)) and not planted[0.0]["removed"]
    print(f"     ⭐ ④ removes every planted below-floor arm and NOT the one at delta=0: {pos_ok}")
    out["e2"] = {str(k): v for k, v in planted.items()}

    # ================= E3 · the contradiction ====================================================
    print("\n  E3 - THE CONTRADICTION, COUNTED   (a search is an instrument: calibrated first)")
    txt = DEFN.read_text()
    pat_full = re.compile(r"②\s*[∧和and]*\s*③\s*[∧和and]*\s*④|②③④")
    pat_pair = re.compile(r"definition is\s*\*{0,2}②\s*∧\s*③\s*\*{0,2}(?!\s*∧\s*④)")
    head = txt[:2000]
    cal_head = bool(re.search(r"\*\*③\*\*", head) and re.search(r"\*\*④\*\*", head))
    # ⛔ the calibration literal carried asterisks INSIDE the phrase; the file has them OUTSIDE
    # ("**SUPERSEDED — the definition is ② ∧ ③**"). The instrument could not see a known answer.
    cal_1820 = "the definition is ② ∧ ③" in txt
    print(f"     CALIBRATION on the two known answers: the head states ③ and ④ as clauses: "
          f"{cal_head}   the '② ∧ ③' sentence exists: {cal_1820}")
    if not (cal_head and cal_1820):
        # ⛔ AND THE FIRST RUN PRINTED THE COUNTS ANYWAY after saying the instrument was
        # uncalibrated — §4's "the verdict string is not a computation", committed one line below
        # the sentence that declared the instrument unfit. The counts are now withheld.
        n_full = n_pair = None
        print("     ⛔ the pattern cannot see a known answer. The counts are WITHHELD, not printed "
              "with a caveat.")
    else:
        n_full = len(pat_full.findall(txt))
        n_pair = len(pat_pair.findall(txt))
        print(f"     statements conjoining ②∧③∧④: {n_full}   statements saying the definition is "
              f"②∧③: {n_pair}")
    out["e3"] = {"calibrated": bool(cal_head and cal_1820), "n_full": n_full, "n_pair": n_pair}

    # ================= CONTROLS ==================================================================
    print("\n  CONTROLS")
    dz = floor_v - floor_v
    plac_ok = float(dz.mean()) == 0.0
    print(f"     PLACEBO   the floor arm against ITSELF: margin {dz.mean():.1e} — it does not beat")
    print(f"               itself, so ④ cannot admit it   "
          f"{'PASS - exactly 0' if plac_ok else 'FAIL'}")
    print(f"     POSITIVE  the planted ladder above   {'PASS' if pos_ok else 'FAIL'}")
    rngn = np.random.default_rng(707)
    # ⛔ TWO DEGENERATE NULLS IN ONE ROUND, both caught by R820's assertion on its first live use.
    #    v1 counted exclusions under a permuted floor: 0 in every draw by construction.
    #    v2 used the mean arm margin — and `(A2[a] - fp).mean() == A2[a].mean() - fp.mean()`, while
    #    `fp` is a permutation of `floor_v` so `fp.mean() == floor_v.mean()` EXACTLY. I replaced one
    #    permutation-invariant statistic with another.
    # ⭐ THE DERIVATION I SHOULD HAVE RUN BEFORE EITHER (the arithmetic trap, §0): ④'s statistic is a
    #    DIFFERENCE OF CORPUS MEANS, and a difference of means is invariant to permuting either side.
    #    So a PERMUTATION null is STRUCTURALLY UNAVAILABLE for clause ④ — not a coding defect, a fact
    #    about the clause: ④ cannot see which prompt the floor came from. Verified numerically below.
    deriv_perm = []
    for _ in range(20):
        fp = floor_v[rngn.permutation(N)]
        deriv_perm.append(float(np.mean([(A2[a] - fp).mean() for a in A2])))
    real_margin = float(np.mean([(A2[a] - floor_v).mean() for a in A2]))
    perm_invariant = float(np.max(np.abs(np.array(deriv_perm) - real_margin))) < 1e-12
    print(f"     ⛔ DERIVATION (not evidence): ④'s statistic is a difference of corpus means, so it is")
    print(f"        permutation-invariant BY ALGEBRA. checked over 20 permutations: max |Δ| "
          f"{np.max(np.abs(np.array(deriv_perm) - real_margin)):.3e}  invariant: {perm_invariant}")
    print(f"        => a permutation null is STRUCTURALLY UNAVAILABLE here. The negative control must")
    print(f"        destroy the ARM's advantage, not the floor's pairing. It resamples instead.")
    # the admissible negative control: replace each arm by a synthetic arm drawn WITH REPLACEMENT
    # from the floor's own per-prompt distribution. That destroys 'this arm beats the floor' while
    # preserving the population, the floor, and the comparison. Under it the margin must sit on 0.
    nulls = []
    for _ in range(200):
        synth = floor_v[rngn.integers(0, N, size=N)]
        nulls.append(float(synth.mean() - floor_v.mean()))
    nulls = np.array(nulls, float)
    real_margin = float(np.mean([(A2[a] - floor_v).mean() for a in A2]))
    try:
        info = assert_null_is_informative(nulls, real_margin, name="R821 negative control")
        # it must sit ON zero (a synthetic arm has no advantage) AND the real margin must lie
        # outside its whole range. Both, or it is not a control.
        on_zero = abs(nulls.mean()) < 2 * nulls.std()
        outside = real_margin > nulls.max()
        neg_ok = bool(on_zero and outside)
        print(f"     NEGATIVE  each arm REPLACED by a synthetic arm resampled from the floor's own")
        print(f"               per-prompt distribution, 200 draws: {nulls.mean():+.5f} ± "
              f"{nulls.std():.5f}   real {real_margin:+.5f}")
        print(f"               spread {info['spread']:.5f}   sits on zero: {on_zero}   real outside "
              f"the null's whole range: {outside}   PASS: {neg_ok}")
    except AssertionError as e:
        neg_ok = False
        print(f"     NEGATIVE  ⛔ {e}")
    hs = []
    rngh = np.random.default_rng(55)
    for _ in range(20):
        s_ = rngh.permutation(N)[: N // 2]
        hs.append(float((A2["coval_core"][s_] - floor_v[s_]).mean()))
    print(f"     NOISE FLOOR  20 half-splits of `coval_core`'s margin: sd {np.std(hs):.4f}")
    gate = ok and plac_ok and pos_ok and neg_ok and out["e3"]["calibrated"]
    print(f"     GATE      {'PASS - the kill may evaluate' if gate else 'FAIL - UNVERIFIED'}")
    out["controls"] = {"placebo_ok": plac_ok, "positive_ok": pos_ok, "negative_ok": neg_ok,
                       "null_mean": float(nulls.mean()), "null_sd": float(nulls.std()),
                       "halfsplit_sd": float(np.std(hs)), "gate": gate}

    # ================= THE KILL ==================================================================
    print("\n  THE KILL -- conditional, gated on the controls")
    if not gate:
        world = "UNVERIFIED"
    elif len(excl) >= 1:
        world = "B"
    elif not pos_ok:
        world = "C"
    else:
        world = "A"
    print(f"     ④ excludes {len(excl)} of {len(rows)} at home · removes every planted below-floor "
          f"arm: {pos_ok} · the file states ②∧③∧④ in {n_full} place(s) and ②∧③ in {n_pair}")
    print(f"     -> WORLD {world}")
    out["world"] = world

    art = HERE / "results/which_definition.json"
    art.parent.mkdir(exist_ok=True)
    art.write_text(json.dumps(out, indent=1, sort_keys=True, default=_plain))
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"\n  ARTIFACT {art.relative_to(ROOT)}  md5 "
          f"{hashlib.md5(art.read_bytes()).hexdigest()}  source_sha {sha[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
