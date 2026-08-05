#!/usr/bin/env python3
"""R536 — weights beat spread under the 2B judge. Does it hold under a second judge?

R535 found topw_k4 (0.5642) beats topvar_k4 (0.4863), refuting select_core.py's own rationale
that spread-selection is "the direct fix". My closing line then said settling whether that is a
fact about selection or about the judge needs an install. ⛔ SIXTH false wall of that shape:
rebuild_selection_08b.sh already re-ran every selection arm under the 0.8B judge, and 32 _08b
artifacts are on disk. This is a reanalysis.

⭐ WHICH ARMS, from the source rather than by convenience:
  frozen (_08b)  = selection fixed at 2B, SCORED at 0.8B
  rerun  (_08bR) = the RULE re-run under 0.8B
  select_core.py: topw_k is satisfaction-blind, so "the two specifications coincide for them
  exactly" -- which is why no topw_k4_08bR exists. So topw_k4_08b IS the 0.8B-judge topw arm,
  and topvar_k4_08bR is the 0.8B-judge topvar arm.

ESTIMAND (before method): the sign and size of A2(topw) - A2(topvar) under the 0.8B judge, on
  that judge's own population, compared to +0.0779 under the 2B judge.
IDENTIFICATION: fully identified; both artifacts exist.
SCOPE  population: the prompts the _08b arms cover · instrument: A2 over all annotators ·
  baseline: the other selector · regime: SECOND release, 0.8B judge.
  ⚠ the two judges are measured on DIFFERENT populations. The ORDERING transfers; the SIZE is
  not comparable across them, and is reported as sign+magnitude within each judge separately.
WORLDS  A · weights still beat spread. The ordering is a fact about SELECTION, and R535's
              refutation of the source's rationale survives a judge change.
        B · the ordering flips or vanishes. R535's finding is a fact about the 2B judge.
KILL (pre-registered): a non-positive topw-minus-topvar under 0.8B kills world A.
POSITIVE CONTROL: topw_k4_08b must DIFFER from topw_k4 -- if the judge swap changed nothing the
  _08b family is a mislabelled copy and nothing here is admissible. (R526 established this for
  five other arms; it is re-run here for the arms actually used.)
NEGATIVE CONTROL: topvar_k4_08b (frozen) must differ from topvar_k4_08bR (rerun) -- the rule is
  satisfaction-consuming, so re-running it under a new judge must change identity. If they were
  identical the "0.8B-judge topvar arm" would not exist as a distinct object.
NOISE FLOOR: cluster bootstrap over prompts, 1200 draws; CI reported.
MULTIPLICITY: 2 judges x 1 contrast; both printed.
IMPOSSIBLE HERE: a third judge, and coval_core under 0.8B (sat_coval_core_08b is absent).
"""
import itertools, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls

RES = ROOT / "corebench/results"
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
NBOOT = 1200

def main():
    src = " ".join((ROOT / "corebench/select_core.py").read_text().split())
    # ⚠ THIRD premise-check exit-2 this session, third distinct markup mechanism:
    #   R529 whitespace wrapping · R534 comment markers · here STRING CONCATENATION, where
    #   the sentence is split as "...and the two " "specifications coincide...".
    #   The robust fix is not a wider normaliser but a SHORTER fragment that cannot span a
    #   boundary -- widening the normaliser three times is chasing the markup, not the quote.
    ok_src = "specifications coincide for them exactly" in src and "satisfaction-blind" in src
    print(f"  SOURCE READ  topw_k is satisfaction-blind so frozen==rerun: "
          f"{'PASS' if ok_src else 'FAIL'}")
    no_rerun = not (RES / "sat_topw_k4_08bR.npz").exists()
    print(f"               and no topw_k4_08bR exists, as that implies: "
          f"{'PASS' if no_rerun else 'FAIL'}")
    if not (ok_src and no_rerun): return 2

    targets, _ = load_targets()
    def a2(tag):
        S = load_sat(RES / f"sat_{tag}.npz")
        ps = sorted({p for p in S if p in targets and len(targets[p]) >= 2})
        out = []
        for p in ps:
            ii = sorted({i for i, _ in S[p]})
            y = np.array([sum(S[p].get((i, x), 0.0) for i in ii) for x in L])
            s = np.sign(y[[i for i, _ in PAIRS]] - y[[j for _, j in PAIRS]])
            H = [cls(yy) for yy, _ in targets[p]]
            out.append(np.mean([(s == np.array(h)).mean() for h in H]))
        return ps, np.array(out)

    def same_npz(a, b):
        da, db = np.load(RES/f"sat_{a}.npz", allow_pickle=True), np.load(RES/f"sat_{b}.npz", allow_pickle=True)
        ma = np.array([str(k) for k in da["meta"]]); mb = np.array([str(k) for k in db["meta"]])
        oa, ob = np.argsort(ma, kind="stable"), np.argsort(mb, kind="stable")
        return (len(ma) == len(mb) and (ma[oa] == mb[ob]).all()
                and np.array_equal(np.asarray(da["sat"])[oa], np.asarray(db["sat"])[ob]))

    pc = not same_npz("topw_k4", "topw_k4_08b")
    print(f"  POSITIVE CONTROL  topw_k4_08b differs from topw_k4 (the judge swap bit): "
          f"{pc} -> {'PASS' if pc else 'FAIL'}")
    nc = not same_npz("topvar_k4_08b", "topvar_k4_08bR")
    print(f"  NEGATIVE CONTROL  topvar_k4_08b (frozen) differs from _08bR (rerun): "
          f"{nc} -> {'PASS' if nc else 'FAIL'}")
    if not (pc and nc):
        print("  -> UNVERIFIED."); return 0

    rows = {}
    for label, w_tag, v_tag in (("2B  (home)", "topw_k4", "topvar_k4"),
                                ("0.8B (second)", "topw_k4_08b", "topvar_k4_08bR")):
        pw, aw = a2(w_tag); pv, av = a2(v_tag)
        common = sorted(set(pw) & set(pv))
        iw = {p: i for i, p in enumerate(pw)}; iv = {p: i for i, p in enumerate(pv)}
        x = np.array([aw[iw[p]] for p in common]); y = np.array([av[iv[p]] for p in common])
        d = x - y
        ib = np.random.default_rng(31337).integers(0, len(common), (NBOOT, len(common)))
        bs = d[ib].mean(axis=1)
        rows[label] = {"n": len(common), "topw": float(x.mean()), "topvar": float(y.mean()),
                       "diff": float(d.mean()), "lo": float(np.percentile(bs, 2.5)),
                       "hi": float(np.percentile(bs, 97.5)), "arms": [w_tag, v_tag]}
        r = rows[label]
        print(f"\n  {label:<15}n={r['n']}  topw {r['topw']:.4f}  topvar {r['topvar']:.4f}  "
              f"diff {r['diff']:+.4f} [{r['lo']:+.4f}, {r['hi']:+.4f}]")

    d8 = rows["0.8B (second)"]
    world = "A" if d8["lo"] > 0 else "B"
    print(f"\n  WORLD {world} -- " +
          ("weights still beat spread under a second judge: the ordering is a fact about "
           "SELECTION, and R535's refutation survives a judge change"
           if world == "A" else "the ordering does not survive; R535's finding is judge-specific"))
    print(f"  ⚠ the two judges use DIFFERENT populations, so the SIGN transfers and the SIZE "
          f"does not compare across them.")

    out = pathlib.Path(__file__).parent / "results/cross_judge.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"rows": rows, "world": world}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
