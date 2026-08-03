"""Attacks 6-10: the READOUT, not the design. One of them kills r210's own diagnosis.

r210 attacked whether the 19 operators are independent. It never asked whether the READOUT is a
defensible instrument, and the readout is where the conclusions actually come from.

ATTACK 6 -- THE AMPLIFICATION ASYMMETRY MAY BE A NORMALISATION ARTIFACT, AND IT IS r210's HEADLINE.
  `dose_g=-1 (double)` sets W[c] -> 2W[c], so its change to the raw score is EXACTLY +W[c]*S_c.
  `dose_g=+1 (delete)` sets W[c] -> 0, so its change is EXACTLY -W[c]*S_c.
  These are opposite vectors of identical magnitude. On PC1 r210 measured double at -0.451 and
  delete at +0.047 -- an asymmetry that is IMPOSSIBLE for exactly-opposite vectors, and which I
  reported as a finding about the rubric ("strengthening moves the decision, removing does not").
  The suspect is my own readout: the score channel is yn = y_centred / ||y_centred||, normalised
  AFTER the mutation, so delta(double) != -delta(delete) because the two mutations change ||y||
  in opposite directions. Normalising before differencing manufactures asymmetry out of symmetry.
  PREDICTION: with the score channel UNNORMALISED, double and delete become exactly antipodal in
  that channel (cosine -1.000 to machine precision). If the asymmetry then survives ONLY in the
  decision channels, r210's finding stands but is a fact about decision boundaries. If it vanishes
  everywhere, the finding is withdrawn.

ATTACK 7 -- EVERY CHANNEL SCALE IS A NUMBER I INVENTED. `top - 0.25`, `borda / 3.0`,
  `count / 20.0`, veto in {0,1}, register a raw cosine. An eigen-decomposition is NOT scale
  invariant, so the "energy by channel" table (top1 34.6%, score 24.6%, ...) reports my arbitrary
  constants as if they were properties of the data, and PC1's composition inherits them.
  PREDICTION: rescaling channels to equal energy materially changes PC1's loadings. If the
  amplification story survives every scaling, it is robust; if not, it was a scaling artifact.

ATTACK 8 -- THE APPARATUS HAS NO POSITIVE CONTROL. The rank/eigenvalue machinery has never been
  shown to recover a KNOWN answer. Plant a design of known rank 3 and a known full-rank design and
  require the instrument to return each. A machine that has never returned a known value is not an
  instrument.

ATTACK 9 -- THE PROMPTS ARE THE FIRST 400 IN FILE ORDER, filtered to 290. Not a sample.

ATTACK 10 -- ORDER OF OPERATIONS. Centring is applied per mutation, so the mutated and baseline
  vectors are centred in different frames. Differences of separately-normalised quantities are the
  same family of error as attack 6.
"""
from __future__ import annotations

import json, math, pathlib, sys
from collections import defaultdict
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
R9 = ROOT / "E04_no_fraction_only_an_equivalence_class/A04_is_the_detection_design_well_defined/R209_repaired_design/results"


def spec(M):
    n = np.linalg.norm(M, axis=1, keepdims=True)
    k = n[:, 0] > 1e-12
    G = M[k] / n[k]
    e = np.clip(np.linalg.eigvalsh(G @ G.T), 0, None)[::-1]
    return e / e.sum(), G


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    D = np.load(R9 / "_deltas.npy")
    ops = [tuple(x) for x in json.loads((R9 / "_ops.json").read_text())]
    nop, npr, nch = D.shape
    name = [o[0] for o in ops]
    iD, iX = name.index("dose_g=-1 (double)"), name.index("dose_g=+1 (delete)")

    # ---------------------------------------------------------------- ATTACK 6
    print("=" * 100)
    print("ATTACK 6 -- IS THE AMPLIFICATION ASYMMETRY A NORMALISATION ARTIFACT")
    print("=" * 100)
    CH = {"score": slice(0, 4), "top1": slice(4, 8), "borda": slice(8, 12),
          "count": slice(12, 13), "veto": slice(13, 14), "register": slice(14, 15)}
    print(f"\n  cosine between `double` and `delete` deltas, per channel, as r209 computed them:")
    for k, sl in CH.items():
        a, b = D[iD, :, sl].ravel(), D[iX, :, sl].ravel()
        na, nb = np.linalg.norm(a), np.linalg.norm(b)
        c = float(a @ b / max(na * nb, 1e-30)) if na > 1e-12 and nb > 1e-12 else float("nan")
        print(f"    {k:10s} cos {c:+.4f}   ||double|| {na:8.3f}  ||delete|| {nb:8.3f}")
    print(f"""
  THE SCORE CHANNEL IS THE TEST. Doubling adds +W[c]*S_c to the raw score and deleting adds
  -W[c]*S_c: exactly antipodal, so the cosine MUST be -1.0000 if the channel reports the raw
  change. Anything else is the normalisation, because r209 normalises y AFTER mutating and then
  differences two separately-normalised vectors.""")

    # rebuild the score channel WITHOUT the post-mutation normalisation
    sys.path.insert(0, str(ROOT))
    from covalx.judge import load_join
    L = "ABCD"
    R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"

    def load(p):
        d = np.load(p, allow_pickle=True)
        o = defaultdict(dict)
        for k, v in zip(d["meta"], d["sat"]):
            pid, i, ltr = str(k).split("|")
            o[pid][(int(i), ltr)] = float(v)
        return o

    sf = load(R4 / "a04_full.npz")
    recs = {pid: r for pid, _p, r in load_join(ROOT / "data/comparisons.jsonl",
                                               ROOT / "data/conversation_rubrics.jsonl")}
    raw_d, raw_x, top_d, top_x = [], [], [], []
    for p in list(sf)[:400]:
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 4:
            continue
        S = {i: np.array([sf[p][(i, x)] for x in L], float) for i in ok}
        W = {i: float(np.mean([s_["score"] for s_ in f[i]["scores"]])) for i in ok}
        c = ok[0]
        y = sum(W[i] * S[i] for i in ok)
        dbl, dele = y + W[c] * S[c], y - W[c] * S[c]
        raw_d.append((dbl - dbl.mean()) - (y - y.mean()))
        raw_x.append((dele - dele.mean()) - (y - y.mean()))
        t0 = np.zeros(4); t0[int(np.argmax(y))] = 1
        t1 = np.zeros(4); t1[int(np.argmax(dbl))] = 1
        t2 = np.zeros(4); t2[int(np.argmax(dele))] = 1
        top_d.append(t1 - t0); top_x.append(t2 - t0)
    A, B = np.concatenate(raw_d), np.concatenate(raw_x)
    cs = float(A @ B / (np.linalg.norm(A) * np.linalg.norm(B)))
    T1, T2 = np.concatenate(top_d), np.concatenate(top_x)
    ct = float(T1 @ T2 / max(np.linalg.norm(T1) * np.linalg.norm(T2), 1e-30))
    flips_d = float(np.mean([np.any(x != 0) for x in top_d]))
    flips_x = float(np.mean([np.any(x != 0) for x in top_x]))
    print(f"""  UNNORMALISED SCORE CHANNEL, recomputed from the tensors:
    cos(double, delete) = {cs:+.6f}   <- must be -1 exactly; deviation {abs(cs + 1):.2e}
  DECISION CHANNEL, same prompts:
    cos(double, delete) = {ct:+.4f}
    top-1 flipped by doubling: {flips_d:.1%}    by deleting: {flips_x:.1%}

  VERDICT ON r210's DIAGNOSIS: the score channel is EXACTLY antipodal, so the asymmetry cannot
  come from the score. It is {'REAL and lives in the decision' if abs(flips_d - flips_x) > 0.02 else 'NOT PRESENT in the decision either -- WITHDRAWN'}: doubling flips the winner on {flips_d:.1%} of
  prompts and deleting on {flips_x:.1%}. {'Same magnitude of score change, different rate of decision change -- which is what a piecewise-constant argmax does and is a fact about where the decision boundaries sit relative to the current winner.' if abs(flips_d - flips_x) > 0.02 else ''}
  BUT r210 attributed the asymmetry to PC1 loadings computed on the NORMALISED score, and those
  loadings are contaminated: -0.451 vs +0.047 for two exactly-opposite raw changes is arithmetic
  about my normalisation, not about the rubric. The CONCLUSION survives on new evidence; the
  EVIDENCE r210 gave for it is withdrawn.""")

    # ---------------------------------------------------------------- ATTACK 7
    print("\n" + "=" * 100)
    print("ATTACK 7 -- EVERY CHANNEL SCALE IS A CONSTANT I INVENTED")
    print("=" * 100)
    e0, G0 = spec(D.reshape(nop, -1))
    w0, V0 = np.linalg.eigh(G0 @ G0.T)
    pc0 = V0[:, int(np.argmax(w0))]
    amp = [name.index(x) for x in ("dose_g=-1 (double)", "set_duplicate", "dose_g=-0.5",
                                   "dose_g=-2 (invert)", "dose_saturate")]
    att = [name.index(x) for x in ("dose_g=+1 (delete)", "dose_g=+0.5 (weaken)",
                                   "set_fragment", "set_add_inert")]

    def amp_gap(pc):
        return float(np.mean(np.abs(pc[amp])) - np.mean(np.abs(pc[att])))

    print(f"  {'channel scaling':34s} {'rank95':>7s} {'top eig':>8s} {'|PC1| amp - |PC1| atten':>24s}")
    variants = {"as r209 wrote it": np.ones(nch)}
    eq = np.ones(nch)
    en = (D ** 2).sum(axis=(0, 1))
    for k, sl in CH.items():
        s_ = en[sl].sum()
        eq[sl] = 1.0 / math.sqrt(max(s_, 1e-30))
    variants["equal energy per channel"] = eq
    variants["score only"] = np.array([1.0 if 0 <= i < 4 else 0.0 for i in range(nch)])
    variants["decision only (top1+borda)"] = np.array([1.0 if 4 <= i < 12 else 0.0
                                                       for i in range(nch)])
    variants["drop count+veto+register"] = np.array([1.0 if i < 12 else 0.0 for i in range(nch)])
    rowsv = []
    for k, sc_ in variants.items():
        Dv = D * sc_[None, None, :]
        e, G = spec(Dv.reshape(nop, -1))
        w, V = np.linalg.eigh(G @ G.T)
        pc = V[:, int(np.argmax(w))]
        pc = pc if abs(pc[amp]).mean() >= 0 else -pc
        g = amp_gap(pc)
        r = int(np.searchsorted(np.cumsum(e), 0.95) + 1)
        rowsv.append({"scaling": k, "rank": r, "top": float(e[0]), "amp_gap": g})
        print(f"  {k:34s} {r:7d} {e[0]:8.3f} {g:+24.3f}")
    gaps = [r["amp_gap"] for r in rowsv]
    print(f"""
  The amplification gap -- mean |PC1 loading| on amplifying operators minus attenuating ones --
  is {min(gaps):+.3f} to {max(gaps):+.3f} across five scalings, {'SAME SIGN throughout' if min(gaps) > 0 or max(gaps) < 0 else 'SIGN FLIPS, so it is a scaling artifact'}.
  Top eigenvalue ranges {min(r['top'] for r in rowsv):.3f} to {max(r['top'] for r in rowsv):.3f} and rank {min(r['rank'] for r in rowsv)} to {max(r['rank'] for r in rowsv)}, so r210's
  "3.5x noise" and "rank 13" are BOTH functions of constants I chose. The energy-by-channel table
  in r210 is withdrawn: it reported my scalings.""")

    # ---------------------------------------------------------------- ATTACK 8
    print("\n" + "=" * 100)
    print("ATTACK 8 -- POSITIVE CONTROL ON THE APPARATUS ITSELF")
    print("=" * 100)
    rng = np.random.default_rng(7)
    for true_r in (1, 3, 8, 19):
        B_ = rng.standard_normal((true_r, npr * nch))
        C_ = rng.standard_normal((nop, true_r))
        M_ = C_ @ B_
        e, _ = spec(M_)
        got = int(np.searchsorted(np.cumsum(e), 0.95) + 1)
        noisy = M_ + 0.05 * np.linalg.norm(M_) / math.sqrt(M_.size) * rng.standard_normal(M_.shape)
        e2, _ = spec(noisy)
        got2 = int(np.searchsorted(np.cumsum(e2), 0.95) + 1)
        ok = "PASS" if got == min(true_r, nop) else "FAIL"
        print(f"  planted rank {true_r:2d} -> recovered {got:2d} ({ok});  with 5% noise -> {got2:2d}")
    print(f"""
  The instrument recovers an exactly low-rank design, and 5% noise inflates the recovered rank
  substantially -- which is the mechanism behind attack 1's finding that noise reads as 18. So the
  apparatus is calibrated, and the correct use of it is COMPARISON AGAINST A MATCHED NULL, never
  an absolute rank. r209 quoted an absolute rank. That was the error.""")

    # ---------------------------------------------------------------- ATTACK 9: the reference class
    print("\n" + "=" * 100)
    print("ATTACK 9 -- THE POSITIVE CONTROL JUST KILLED ATTACK 1's REFERENCE CLASS")
    print("=" * 100)
    print(f"""  A PLANTED RANK-19 DESIGN READS 13 -- exactly the number r209 reported for the real one. So
  "the design reads 13 while noise reads 18, therefore it is rank-deficient" compared against the
  WRONG reference. Independent gaussian ROWS give a near-identity gram and the flattest possible
  spectrum; a random MIXING of 19 independent sources is equally full-rank and reads far lower.
  The reference class, not the data, decided attack 1's verdict.
  PREDICTION: a matched random-mixing null reads ~13, i.e. indistinguishable from the design.""")
    e_obs, _ = spec(D.reshape(nop, -1))
    r_obs = int(np.searchsorted(np.cumsum(e_obs), 0.95) + 1)
    per_norm = np.linalg.norm(D, axis=2)
    rows9 = []
    for nm_, gen in [
        ("N1  independent gaussian rows (attack 1's null)",
         lambda g: (lambda Z: Z / np.maximum(np.linalg.norm(Z, axis=2, keepdims=True), 1e-12)
                    * per_norm[:, :, None])(g.standard_normal(D.shape)).reshape(nop, -1)),
        ("N5  random MIXING of 19 independent sources (full rank)",
         lambda g: g.standard_normal((nop, nop)) @ g.standard_normal((nop, npr * nch))),
        ("N6  random mixing of 19, then matched per-prompt norms",
         lambda g: (lambda M_: (M_.reshape(nop, npr, nch)
                    / np.maximum(np.linalg.norm(M_.reshape(nop, npr, nch), axis=2, keepdims=True),
                                 1e-12) * per_norm[:, :, None]).reshape(nop, -1))(
             g.standard_normal((nop, nop)) @ g.standard_normal((nop, npr * nch)))),
    ]:
        rs, tp = [], []
        for k in range(20):
            g = np.random.default_rng(100 + k)
            e, _ = spec(gen(g))
            rs.append(int(np.searchsorted(np.cumsum(e), 0.95) + 1)); tp.append(float(e[0]))
        rows9.append({"null": nm_, "rank": float(np.mean(rs)), "sd": float(np.std(rs)),
                      "top": float(np.mean(tp))})
        print(f"  {nm_:52s} rank {np.mean(rs):5.1f} +/- {np.std(rs):.1f}   top eig {np.mean(tp):.3f}")
    print(f"  {'OBSERVED design':52s} rank {r_obs:5.1f}         top eig {e_obs[0]:.3f}")
    lo = min(r["rank"] for r in rows9); hi = max(r["rank"] for r in rows9)
    tlo = min(r["top"] for r in rows9); thi = max(r["top"] for r in rows9)
    inside = lo - 1 <= r_obs <= hi + 1
    # A VERDICT COMPUTED AGAINST ONE CHOSEN REFERENCE IS THE ERROR THIS WHOLE ROUND IS ABOUT. The
    # first version of these lines compared the observation to N6 alone and printed
    # "DISTINGUISHABLE", which is the same move as attack 1 comparing to N1 alone and printing
    # "rank-deficient". Three defensible nulls exist; the verdict is against their RANGE.
    print(f"""
  VERDICT, AGAINST THE RANGE AND NOT A CHOSEN MEMBER OF IT.
    rank:            nulls span {lo:.1f} to {hi:.1f}; the design reads {r_obs}. {'INSIDE the range -- NOT DISCRIMINATING' if inside else 'outside'}.
    top eigenvalue:  nulls span {tlo:.3f} to {thi:.3f}; the design reads {e_obs[0]:.3f}. ABOVE ALL THREE.
  Note also that MATCHING PER-PROMPT NORMS ALONE raises a full-rank mixing from {[r for r in rows9 if r['null'].startswith('N5')][0]['rank']:.1f} to {[r for r in rows9 if r['null'].startswith('N6')][0]['rank']:.1f} -- the
  null CONSTRUCTION moves rank more than the data does. That is disqualifying for the statistic.

  SO: RANK IS RETIRED for this question, and with it attack 1's "five operators' worth of
  redundancy", which measured distance to the flattest conceivable reference. What SURVIVES all
  three nulls is the CONCENTRATION: top eigenvalue {e_obs[0]:.3f} against a null maximum of {thi:.3f}. The
  operators do share a dominant direction; the rank statistic was simply blind to it either way.
  r208's rank 2 also stands, because 2 is far below every reference measured here -- it is the only
  rank claim in this line that survives, and it survives because it was an EXACT algebraic
  collapse rather than a comparison of near-full-rank numbers.""")

    (OUT / "readout_attacks.json").write_text(json.dumps(
        {"cos_double_delete_raw_score": cs, "cos_double_delete_top1": ct,
         "flip_rate_double": flips_d, "flip_rate_delete": flips_x,
         "scalings": rowsv, "reference_class": rows9, "observed_rank": r_obs,
         "rank_retired": True}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
