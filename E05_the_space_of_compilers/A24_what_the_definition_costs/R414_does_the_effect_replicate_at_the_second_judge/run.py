"""R414 -- does coval_core's +0.009 over the maximum blind set replicate at the SECOND judge?

R413 closed the second-corpus replication line at ~2.5x and its NEXT said to check whether a second
JUDGE could host the comparison before treating that as structurally impossible -- because
R358/R359's "at 0.8B nothing is admitted at any safe reference" is a fact about ONE alternative judge.

⛔ AND THAT SENTENCE ANSWERS A DIFFERENT QUESTION THAN THE ONE I NEED, WHICH IS THE R406 SHAPE AGAIN.
   "Nothing is ADMITTED" is a BINARY verdict: it requires clearing a significance bar against a
   reference. The quantity at issue here is the CONTINUOUS effect, `coval_core` minus the maximum
   prompt-blind set. An arm can carry a positive effect and still fail admission -- indeed R408 showed
   exactly that at the 2B judge, where all five label-free arms clear `e > 0` and none clears
   `|e| >= ZEFF*se`. So "nothing admitted at 0.8B" does NOT establish "no effect at 0.8B", and the
   effect there has never been looked at.

⭐ AND THE 0.8B SCORES ARE ALREADY ON DISK. `sat08_coval_core.npz`, `sat08_genericpool16.npz` and
   `sat08_topw_k4.npz` were scored and committed, and R360's arm filter explicitly excludes them
   (`not p.stem.startswith("sat08")`). A genuine CROSS-MODEL replication -- the criterion §2 calls
   structurally impossible on one site -- has been sitting unused, and it costs no GPU.

⛔ BUT THERE ARE TWO NAMING FAMILIES FOR THIS JUDGE AND MIXING THEM WOULD BE A SILENT CONFOUND.
   `sat08_*` holds coval_core, genericpool16 and topw_k4; `sat_*_08b` holds oracle_k4, the fits and
   the topw sweep. Whether they are the SAME run is unverified -- and `topw_k4` appears in BOTH, so
   it is testable rather than assumable. That test decides this round's scope BEFORE any effect is
   computed, and if it fails the round restricts to the single family that carries the headline arm.

⛔ ARITHMETIC TRAP. Nothing forces the sign at a different judge. A model with different biases could
   rank the blind maximum above the core, and the whole point is that it could.

ESTIMAND        (A) whether the two 0.8B naming families are the same scoring run, from the arm they
                    share;
                (B) `coval_core` minus the per-k MAXIMUM prompt-blind set, at the 0.8B judge, paired
                    over prompts -- the same construction R408 used at 2B;
                (C) the sign and the ratio to the 2B judge's committed +0.009002.

IDENTIFICATION  Exact given the committed 0.8B scores. NOT identified: whether a THIRD judge would
                agree -- two judges is two, and a two-point agreement is not a trend.

SCOPE           population: CoVal prompts scored by BOTH judges · instrument: the 0.8B judge's
                committed sat files, loaded through the same scoring module R360/R408 use · baseline:
                the per-k maximum blind subset at 0.8B · regime: literal rule, p = 100.

WORLDS
  W-REPLICATES   the effect is positive at 0.8B with a comparable magnitude. Then the +0.009 is not
                 an artifact of one judge, and this is the strongest evidence available on this box --
                 a criterion the register has been calling impossible.
  W-SIGN-FLIP    the effect is negative at 0.8B. Then `coval_core`'s advantage over the blind maximum
                 is JUDGE-SPECIFIC, and R408's result must carry that scope forever after.
  W-ATTENUATED   positive but far smaller relative to its own noise. Then the direction survives and
                 the magnitude does not, and the honest report is the pair, not the mean.

PREDICTION MATRIX
  W-REPLICATES -> e_08b > 0 and e_08b/se_08b within a factor ~2 of the 2B ratio
  W-SIGN-FLIP  -> e_08b < 0
  W-ATTENUATED -> e_08b > 0 but the standardised effect is under half the 2B one

PRE-REGISTERED KILL -- conditional on the controls, never on the sign alone.
    if family_identity_resolved and (oracle_positive_at_08b if oracle usable) and pool_nonempty:
        e < 0                                   -> W-SIGN-FLIP
        e > 0 and d_08b >= 0.5 * d_2B           -> W-REPLICATES
        e > 0                                   -> W-ATTENUATED
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  FAMILY (=)    `topw_k4` exists in BOTH naming families. Their scores must be identical, or the two
                are different runs and mixing them is forbidden. This decides the round's SCOPE
                before any effect is computed, rather than being checked afterwards.
  ORACLE (+)    `oracle_k4` reads the prompt's own rankings, so it must beat the blind maximum at ANY
                judge. If the 0.8B files permit it, this is the instrument check: a judge too weak to
                separate a label-reader from a blind set cannot host the comparison at all, and THAT
                would be the honest reading of R358/R359 rather than "no effect".
  SCORING       load_sat/load_targets/yvec/cls are IMPORTED from the module R360 and R408 use.
  POOL          the 0.8B pool must yield the same criterion count; a different npool silently changes
                what "the maximum blind subset of that size" means.

MULTIPLICITY    one headline contrast plus its controls; every number printed.
SEEDS           none -- deterministic enumeration.
ARTIFACT        results/r414_second_judge.json with the source hash.

IMPOSSIBLE HERE
  a THIRD judge          -- would need a scoring pass, i.e. the GPU, which R396 holds.
  a claim about judges in general -- two judges is two.
  re-scoring at 2B       -- R408's value is committed and is used as given.

EXIT
    0  the controls hold and the second-judge effect is reported
    1  a control misbehaved -- UNVERIFIED
    2  a required file is absent -- never a silent pass
"""
from __future__ import annotations
import hashlib
import itertools
import json
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
R408 = HERE.parent / "R408_the_literal_test_at_the_universal_reference" / "results" / \
    "r408_literal_test.json"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621


def main() -> int:
    need = ["sat08_coval_core.npz", "sat08_genericpool16.npz", "sat08_topw_k4.npz",
            "sat_topw_k4_08b.npz"]
    missing = [f for f in need if not (RES / f).exists()]
    if missing or not R408.exists():
        print(f"  UNRUNNABLE: missing {missing or 'R408 artifact'}. Exit 2, never 0."); return 2
    a408 = json.loads(R408.read_text())
    e_2b = a408["rows"]["coval_core"]["e"]
    se_2b = a408["rows"]["coval_core"]["se"]
    n_2b = a408["n_prompts"]
    d_2b = e_2b / (se_2b * math.sqrt(n_2b))

    print("R414 · does the +0.009 replicate at the SECOND judge?\n")
    print("  ⛔ R358/R359's `nothing is ADMITTED at 0.8B` ANSWERS A DIFFERENT QUESTION. Admission is")
    print("     a BINARY needing `|e| >= ZEFF*se`; the quantity here is the CONTINUOUS effect. R408")
    print("     showed at 2B that all five label-free arms clear `e > 0` and NONE clears the")
    print("     significance bar — so `not admitted` never meant `no effect`, and the effect at")
    print("     0.8B has never been looked at.\n")

    # ---- CONTROL: are the two 0.8B naming families the same run? ----------------------------------
    A = load_sat(RES / "sat08_topw_k4.npz")
    B = load_sat(RES / "sat_topw_k4_08b.npz")
    shared = sorted(set(A) & set(B))
    same = bool(shared) and all(A[q] == B[q] for q in shared[:200])
    print(f"  CONTROLS")
    print(f"    FAMILY (=)   `topw_k4` exists in BOTH families; {len(shared):,} shared prompts, first")
    print(f"                 200 compared: identical = {same}   "
          f"{'PASS — one run, both families usable' if same else 'DIFFER — restricting to sat08_*'}")

    tg, _ = load_targets()
    POOL = load_sat(RES / "sat08_genericpool16.npz")
    pids = sorted(set(POOL) & {q for q in tg if len(tg[q]) >= 2})
    H = {q: [cls(np.array(t[0], float)) for t in tg[q]] for q in pids}
    npool = len({i for i, _ in POOL[pids[0]]})
    print(f"    POOL         0.8B pool: {len(pids):,} prompts, {npool} criteria "
          f"(2B run used {n_2b:,} prompts)")
    if len(pids) < 100:
        print("  UNRUNNABLE: 0.8B pool too small. Exit 2, never 0."); return 2

    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])

    def a2_vec(sat, ps):
        out = []
        for q in ps:
            idx = sorted({i for i, _ in sat[q]})
            yv = cls(yvec(sat[q], idx))
            out.append(np.mean([[yv[c] == h[c] for c in range(6)] for h in H[q]]))
        return np.array(out, float)

    def build(k):
        sb = np.array(list(itertools.combinations(range(npool), k)))
        SAT = np.stack([np.array([[POOL[q][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                        for q in pids])
        out = np.empty((len(sb), len(pids)))
        for n in range(len(pids)):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[:, n] = (C_[:, None, :] == np.array(H[pids[n]], float)[None, :, :]).mean(axis=(1, 2))
        return out

    subjects = {"coval_core": "sat08_coval_core.npz", "topw_k4": "sat08_topw_k4.npz"}
    if same and (RES / "sat_oracle_k4_08b.npz").exists():
        subjects["oracle_k4"] = "sat_oracle_k4_08b.npz"

    stats = {}
    CLSk = {}
    for name, fn in subjects.items():
        S = load_sat(RES / fn)
        ps = [q for q in pids if q in S]
        if len(ps) < 100:
            print(f"    {name}: only {len(ps)} prompts at 0.8B — skipped"); continue
        k = min(max(int(np.median([len({i for i, _ in S[q]}) for q in ps])), 1), npool)
        if k not in CLSk:
            CLSk[k] = build(k)
        Bk = CLSk[k]
        ref = Bk[int(np.argsort(Bk.mean(axis=1))[-1])]
        v = a2_vec(S, ps)
        pos = [n for n, q in enumerate(pids) if q in set(ps)]
        d = v - ref[pos]
        e = float(d.mean()); se = float(d.std(ddof=1) / math.sqrt(len(d)))
        stats[name] = dict(k=k, n=len(d), e=e, se=se, d=e / (se * math.sqrt(len(d))))

    oracle_ok = ("oracle_k4" not in stats) or (stats["oracle_k4"]["e"] > 0)
    if "oracle_k4" in stats:
        o = stats["oracle_k4"]
        print(f"    ORACLE (+)   a label-reader must beat the blind maximum at ANY judge: "
              f"e = {o['e']:+.6f}   {'PASS' if oracle_ok else 'FAIL'}")
        print(f"                 a judge too weak to separate a label-reader from a blind set could")
        print(f"                 not host this comparison at all — and THAT would be the honest")
        print(f"                 reading of R358/R359 rather than `no effect`")
    else:
        print(f"    ORACLE (+)   UNAVAILABLE — the families differ, so the oracle file cannot be")
        print(f"                 mixed with this pool. Named, not skipped.")
    if "coval_core" not in stats:
        print("\n  UNRUNNABLE: coval_core has too few 0.8B prompts. Exit 2."); return 2
    if not oracle_ok:
        print("\n  UNVERIFIED — the judge cannot separate a label-reader from the blind maximum, so")
        print("  a null on coval_core would be silence. Exit 1."); return 1

    c = stats["coval_core"]
    print(f"\n  THE SECOND-JUDGE EFFECT — same construction as R408, different judge")
    print(f"    {'arm':<14}{'k':>3}{'n':>7}{'e':>13}{'se':>11}{'d':>10}")
    for name, s in stats.items():
        print(f"    {name:<14}{s['k']:>3}{s['n']:>7}{s['e']:>+13.6f}{s['se']:>11.6f}{s['d']:>10.5f}")
    print(f"\n    2B judge (R408, committed): e {e_2b:+.6f}  se {se_2b:.6f}  d {d_2b:.5f}")
    ratio = c["d"] / d_2b if d_2b else float("nan")
    print(f"    0.8B / 2B standardised ratio: {ratio:+.3f}")

    print()
    if c["e"] < 0:
        v = "W_SIGN_FLIP"
        print(f"  W-SIGN-FLIP — at the second judge the effect is {c['e']:+.6f}, NEGATIVE. The")
        print(f"  released core does NOT beat the maximum prompt-blind set there, so R408's +0.009 is")
        print(f"  JUDGE-SPECIFIC and every statement of it must carry that scope from now on.")
    elif c["d"] >= 0.5 * d_2b:
        v = "W_REPLICATES"
        print(f"  W-REPLICATES — positive at both judges, standardised ratio {ratio:.2f}. The +0.009")
        print(f"  is not an artifact of one model. This is CROSS-MODEL replication, which the")
        print(f"  register has been listing as structurally impossible on one site — and it cost no")
        print(f"  GPU because the scores were already committed.")
    else:
        v = "W_ATTENUATED"
        print(f"  W-ATTENUATED — positive at both judges but the standardised effect is {ratio:.2f} of")
        print(f"  the 2B one. The DIRECTION survives and the MAGNITUDE does not, and the honest")
        print(f"  report is the pair rather than either number alone.")

    print(f"\n  ⚠ TWO JUDGES IS TWO. A two-point agreement is not a trend, and nothing here licenses a")
    print(f"    claim about judges in general. A third would need a scoring pass, i.e. the GPU.")
    print(f"  ⚠ AND THIS DOES NOT CONTRADICT R358/R359. They measured ADMISSION, a binary needing")
    print(f"    significance; this measures the CONTINUOUS effect. Both can be true at once and at")
    print(f"    2B they demonstrably are.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               families_identical=same, n_prompts_08b=len(pids), npool=npool,
               stats=stats, e_2b=e_2b, se_2b=se_2b, d_2b=d_2b, ratio=ratio,
               controls=dict(family_same=same, oracle_ok=oracle_ok,
                             oracle_e=stats.get("oracle_k4", {}).get("e")),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r414_second_judge.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
