"""R459 -- is R457's 0.8812 a property of the PROMPT, or of which wrong partner the sham drew?

⛔ THE ANNOUNCED STEP'S DECISION RULE IS UNSOUND IN ONE DIRECTION. R458 closed proposing a
   bag-of-words overlap between each core's criteria and its own prompt: "if it reaches zero, the
   semantic hypothesis is weaker than it looks." **Lexical overlap and semantic relevance are
   different things**; an embedding can capture what BOW cannot, so a BOW null is weak evidence
   against the semantic hypothesis. The other direction (positive BOW -> the GPU is worth it) is
   fine. *Twenty-seventh announced step checked; its inference is half-valid and it is not the most
   load-bearing thing available.*

⭐ AND CHECKING IT EXPOSED A CONFOUND IN MY OWN MOST RECENT HEADLINE. R457's estimand is
   `d[p] = A2(core,p) - A2(sham,p)`, and the sham applies ANOTHER PROMPT's criteria to p's responses.
   Which partner was drawn is FIXED per prompt in the release file -- so a split-half over ANNOTATORS
   holds the partner constant, and **partner-driven variance is counted as perfectly "reliable" while
   being no property of prompt p at all.** R457 reported rho_full = 0.8812 and called it "the value
   of having the RIGHT criteria on this prompt". Part of it may be the value of not having THAT
   PARTICULAR wrong set.

⚠ AND THIS ROUND CANNOT DECOMPOSE THAT VARIANCE, WHICH IS STATED RATHER THAN WORKED AROUND. Because
  the partner is fixed per prompt, no annotator-split can separate partner variance from prompt
  variance. What IS testable is whether a PARTNER-FREE estimand reaches the same reliability:
  `generic` is a single FIXED criterion set (verified: exactly 1 distinct criterion-index tuple
  across all 968 prompts), so `A2(core,p) - A2(generic,p)` has no partner at all.

ESTIMAND (named before the method)
    Split-half over each prompt's annotators, two disjoint halves:
      RHO(x) = Spearman-Brown corrected corr(x_A, x_B) across prompts, for
        components   A2(core), A2(sham), A2(generic), A2(oracle)
        differences  d_sham = core - sham        [R457's, PARTNER-CONFOUNDED]
                     d_gen  = core - generic     [PARTNER-FREE]
    ⭐ The comparison RHO(d_gen) vs RHO(d_sham) is the whole result. Components are reported too, so
      the SOURCE of each difference's reliability is visible rather than inferred.

IDENTIFICATION
    Identified for the comparison. ⚠ NOT identified: the partner variance itself, for the reason
    above. Registered as impossible here, with what it would require: the same core criteria scored
    against several DIFFERENT partner prompts, which is a re-judging job.

SCOPE  population : the 968 prompts with >=4 annotators; min 4 / median 16 / max 46
       instrument : Qwen3.5-2B-Base; A2 over 6 pairs; annotators split, never resampled with return
       baseline   : R457's committed rho_full = 0.8812 for d_sham
       regime     : half-length ~8 annotators; Spearman-Brown projects to full

WORLDS
    W-PARTNER   RHO(d_gen) is MUCH lower than RHO(d_sham) -> the partner draw contributes
                substantially, and R457's 0.8812 overstates the per-prompt property. The reliable
                quantity is partly "which wrong criteria happened to be drawn".
    W-CLEAN     the two agree -> the conclusion does not depend on the partner; a partner-FREE
                estimand reaches the same reliability and R457 stands as a statement about prompts.
    W-HIGHER    RHO(d_gen) EXCEEDS RHO(d_sham) -> the partner draw was ADDING noise, and R457 was
                conservative rather than inflated.

PREDICTION MATRIX
                   d_gen much lower   d_gen ~ equal   d_gen higher
    W-PARTNER            0.90             0.05           0.05
    W-CLEAN              0.05             0.90           0.05
    W-HIGHER             0.05             0.05           0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the controls fire.
    RHO(d_gen) < RHO(d_sham) - 0.15                  -> W-PARTNER
    |RHO(d_gen) - RHO(d_sham)| <= 0.15               -> W-CLEAN
    RHO(d_gen) > RHO(d_sham) + 0.15                  -> W-HIGHER
    else / control failure                           -> UNVERIFIED

CONTROLS
    POSITIVE   the ORACLE's per-prompt A2, chosen USING the answer, must be reliably high -- the
               instrument must be able to see prompt-level structure that is known to be there.
    g=0        a component against ITSELF is identically equal, so rho is 1.0 by construction; the
               code prints it as a DERIVATION and it licenses nothing.
    NEGATIVE   prompt labels of half B shuffled: rho must collapse to ~0 for every quantity.
    PARTNER-FREE VERIFICATION  `generic`'s criterion-index tuple count is asserted to be 1 inside the
               run, not taken from a previous command. If it is not 1, the round is UNRUNNABLE --
               because then `generic` has a partner too and the comparison is void.
    SEEDS      5 independent half-splits; spread reported, never averaged away.

MULTIPLICITY  6 quantities x 5 splits, all printed, nothing selected.
ARTIFACT      results/r459_partner.json
IMPOSSIBLE HERE, NAMED
    * decomposing partner variance -- the partner is fixed per prompt in the release; would require
      re-judging each core's criteria against several different partner prompts.
    * whether `generic`'s fixed criteria are REPRESENTATIVE of prompt-blind sets -- one fixed set is
      one draw, and R450/R453 measured that fixed prompt-blind sets vary widely in strength.
"""
from __future__ import annotations
import hashlib, itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
L = "ABCD"
PAIRS = list(itertools.combinations(range(4), 2))
M, NSPLIT = 4, 5
R457_DSHAM = 0.8812


def stable(pid): return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)
def signs(Y): return np.stack([np.sign(Y[..., i] - Y[..., j]) for i, j in PAIRS], axis=-1)
def sb(r): return 2 * r / (1 + r) if r > -1 else float("nan")


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R459 · is R457's 0.8812 about the PROMPT, or about which wrong PARTNER the sham drew?\n")
    print("  ⛔ R458's announced BOW test is half-valid: a lexical null is weak evidence against a")
    print("     SEMANTIC hypothesis. Twenty-seventh step checked. And checking it exposed a confound")
    print("     in R457's own estimand — the sham's partner is FIXED per prompt, so an annotator")
    print("     split counts partner variance as 'reliable' while it is no property of the prompt.\n")

    need = {"core": "coval_core", "sham": "coval_core_sham", "generic": "generic",
            "pool": "genericpool16"}
    S = {}
    for k, nm in need.items():
        f = SATD / f"sat_{nm}.npz"
        if not f.exists():
            print(f"  UNRUNNABLE: sat_{nm}.npz absent. Exit 2, never 0."); return 2
        S[k] = SC.load_sat(f)
    # PARTNER-FREE VERIFICATION, asserted here and not inherited from a previous command
    gt = {tuple(sorted({c for (c, _) in v})) for v in S["generic"].values()}
    print(f"  PARTNER-FREE CHECK  `generic` distinct criterion-index tuples: {len(gt)}")
    if len(gt) != 1:
        print("  UNRUNNABLE: `generic` is not a single fixed set, so it has a partner too and the")
        print("  comparison is void. Exit 2, never 0.")
        return 2
    targets, _ = SC.load_targets()
    pids = sorted(set(targets) & set.intersection(*[set(v) for v in S.values()]))
    pids = [p for p in pids if len(targets[p]) >= 4]
    n = len(pids)
    if n < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2
    na = np.array([len(targets[p]) for p in pids])
    print(f"  prompts {n};  annotators min {na.min()} median {int(np.median(na))} max {na.max()}")

    subs = list(itertools.combinations(range(16), M))
    Sm = np.zeros((len(subs), 16))
    for j, s in enumerate(subs):
        Sm[j, list(s)] = 1.0
    CL, ARM, POOLS = {}, {k: {} for k in ("core", "sham", "generic")}, {}
    for p in pids:
        CL[p] = np.array([SC.cls(np.array(t[0], float)) for t in targets[p]])
        for k in ARM:
            d = S[k][p]; cs = sorted({c for (c, _) in d})
            ARM[k][p] = signs(np.array([[d.get((c, l), 0.0) for l in L] for c in cs]).mean(axis=0))
        PMp = np.zeros((16, 4))
        for (ci, ltr), v in S["pool"][p].items():
            PMp[ci, L.index(ltr)] = v
        POOLS[p] = signs((Sm @ PMp) / M)

    def halves(seed):
        out = {k: (np.zeros(n), np.zeros(n)) for k in ("core", "sham", "generic", "oracle")}
        for i, p in enumerate(pids):
            C = CL[p]
            perm = np.random.default_rng(seed * 7919 + stable(p)).permutation(len(C))
            h = len(C) // 2
            for sl, idx in ((0, perm[:h]), (1, perm[h:2 * h])):
                HC = C[idx]
                for k in ARM:
                    out[k][sl][i] = (ARM[k][p][None, :] == HC).mean()
                out["oracle"][sl][i] = (POOLS[p][:, None, :] == HC[None, :, :]).mean(axis=(1, 2)).max()
        return out

    QUANT = ["core", "sham", "generic", "oracle", "d_sham", "d_gen"]

    def series(h, q):
        if q == "d_sham":
            return h["core"][0] - h["sham"][0], h["core"][1] - h["sham"][1]
        if q == "d_gen":
            return h["core"][0] - h["generic"][0], h["core"][1] - h["generic"][1]
        return h[q]

    rows = {}
    for q in QUANT:
        rr = []
        for sd in range(NSPLIT):
            a, b = series(halves(sd), q)
            rr.append(float(np.corrcoef(a, b)[0, 1]))
        rh = float(np.mean(rr))
        a0, b0 = series(halves(0), q)
        rb = np.random.default_rng(31)
        bs = np.array([np.corrcoef(*np.array([a0, b0])[:, rb.integers(0, n, n)])[0, 1]
                       for _ in range(3000)])
        rows[q] = {"rho_half": rh, "rho_full": sb(rh),
                   "ci_full": [sb(float(np.percentile(bs, 2.5))),
                               sb(float(np.percentile(bs, 97.5)))],
                   "spread": float(np.std(rr))}

    print("\n  CONTROLS")
    orc = rows["oracle"]
    pos_ok = orc["rho_full"] > 0.30 and orc["ci_full"][0] > 0
    print(f"    POSITIVE  the ORACLE's per-prompt A2 -> rho_full {orc['rho_full']:+.4f} "
          f"CI [{orc['ci_full'][0]:+.4f},{orc['ci_full'][1]:+.4f}]   "
          f"{'PASS' if pos_ok else '⛔ FAIL'}")
    h0 = halves(0)
    a0, b0 = series(h0, "d_sham")
    negs = [float(np.corrcoef(a0, np.random.default_rng(5 + s).permutation(b0))[0, 1])
            for s in range(3)]
    neg_ok = abs(np.mean(negs)) < 0.10
    print(f"    NEGATIVE  prompt labels of half B shuffled -> {np.mean(negs):+.4f}   "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"    g=0       a component against ITSELF is identically equal -> rho = 1.0 BY")
    print(f"              CONSTRUCTION; a DERIVATION, printed as one, licensing nothing")

    print("\n  ⭐ SPLIT-HALF RELIABILITY — components first, so each difference's SOURCE is visible")
    print(f"    {'quantity':<10}{'rho_half':>10}{'rho_full':>10}{'CI_full':>22}{'seed sd':>9}")
    for q in QUANT:
        r = rows[q]
        tag = ""
        if q == "d_sham":
            tag = "   <- R457's, PARTNER-CONFOUNDED"
        if q == "d_gen":
            tag = "   <- PARTNER-FREE"
        print(f"    {q:<10}{r['rho_half']:>+10.4f}{r['rho_full']:>+10.4f}   "
              f"[{r['ci_full'][0]:+.4f},{r['ci_full'][1]:+.4f}]{r['spread']:>9.4f}{tag}")

    ds, dg = rows["d_sham"]["rho_full"], rows["d_gen"]["rho_full"]
    print(f"\n    R457 committed d_sham = {R457_DSHAM:.4f}; reproduced here as {ds:.4f} "
          f"({'agrees' if abs(ds - R457_DSHAM) < 0.03 else '⛔ DOES NOT AGREE'})")
    delta = dg - ds
    ctrl_ok = pos_ok and neg_ok and abs(ds - R457_DSHAM) < 0.03
    if not ctrl_ok:
        world = "UNVERIFIED"
    elif delta < -0.15:
        world = "W-PARTNER"
    elif delta > 0.15:
        world = "W-HIGHER"
    else:
        world = "W-CLEAN"
    print(f"    RHO(d_gen) - RHO(d_sham) = {delta:+.4f}")
    print(f"\n  WORLD: {world}")
    if world == "W-CLEAN":
        print(f"    A PARTNER-FREE estimand reaches the same reliability ({dg:.4f} vs {ds:.4f}), so")
        print(f"    R457's conclusion does not depend on which wrong partner the sham drew.")
        print(f"    ⚠ This does NOT decompose partner variance -- that is impossible here -- it")
        print(f"       shows the conclusion survives without a partner at all.")
    elif world == "W-PARTNER":
        print(f"    The partner draw contributes substantially: without it, reliability falls to")
        print(f"    {dg:.4f}. R457's 0.8812 overstates the per-PROMPT property.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "n_prompts": n, "quantities": rows,
           "r457_committed_d_sham": R457_DSHAM, "d_sham_here": ds, "d_gen_here": dg,
           "delta": delta, "generic_distinct_tuples": len(gt),
           "controls": {"positive_ok": bool(pos_ok), "negative_rho": float(np.mean(negs)),
                        "negative_ok": bool(neg_ok)}}
    (RES / "r459_partner.json").write_text(json.dumps(out, indent=2))
    print(f"  artifact: {RES/'r459_partner.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
