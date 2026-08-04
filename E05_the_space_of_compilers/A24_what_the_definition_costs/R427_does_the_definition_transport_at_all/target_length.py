"""R427/target_length -- is the TARGET itself length-loaded? The confound under every number so far.

Every result in R427 is measured against one target: which response a human chose. `length` reaches
0.5096 on it while the judged core reaches 0.4374, and I have been calling `length` a SHORTCUT
BASELINE -- the thing an arm must beat.

⛔ BUT A BASELINE THAT STRONG IS ALSO A HYPOTHESIS ABOUT THE TARGET, AND I NEVER TESTED IT. If the
   human `score` largely tracks response LENGTH within an interaction, then "pick what people picked"
   is substantially "pick the longest", and `length` is not a shortcut to beat -- it is close to what
   the target IS. Every number in this round would then be read differently: not "the core fails to
   beat a heuristic" but "the core fails to reproduce a length preference", which is a claim about
   the CORPUS as much as about the core.

⭐ AND IT COSTS NOTHING. `score` and response length are both in the corpus. No judge, no arm, no
   GPU. This is the cheapest question in the round and it sits UNDER every number in it, which is
   exactly the order the attack ladder says to work in -- and I ran three analyses before asking it.

⛔ ARITHMETIC TRAP. That the longest response is chosen at SOME rate above 1/n is not by itself
   evidence of a length preference -- with n=2 any rule that is not exactly balanced deviates from
   0.5. The permutation null below is what makes the rate readable, and the CORRELATION is the
   quantity that could have come out at zero.

ESTIMAND        (A) the within-interaction rank correlation between `score` and response length
                    (Kendall tau-b, averaged over interactions, clustered by conversation);
                (B) P(the longest response is also the highest-scoring one), per stratum;
                (C) what (A) implies for how every accuracy in R427 should be read.

IDENTIFICATION  Exact. Both quantities are deterministic functions of committed fields. NOT
                identified: WHY the association exists -- verbosity bias in raters, longer answers
                being genuinely better, or a collection artifact. Named, not guessed.

SCOPE           population: the same 2,200 seeded conversations · instrument: none, this reads the
                corpus · baseline: a within-interaction permutation of lengths · regime: interactions
                with >= 2 distinct responses and a human score.

WORLDS
  W-TARGET-IS-LENGTH   tau is well above its permutation null and P(longest = top) is far above 1/n.
                       Then `length` is not a shortcut but a near-restatement of the target, and
                       R427's numbers measure how well a criterion-based core reproduces a length
                       preference. The finding stands and its WORDING must change.
  W-INDEPENDENT        tau sits on its permutation null. Then length and the human target are
                       unrelated within an interaction, `length` really is an external shortcut, and
                       the fact that it beats the core is a fact about the core alone.
  W-PARTIAL            tau is resolvably above null but modest. Then both readings hold in part and
                       the number is reported as a bound rather than a story.

PREDICTION MATRIX
  W-TARGET-IS-LENGTH -> tau >> null, P(longest=top) >> 1/n
  W-INDEPENDENT      -> tau within MDE of null
  W-PARTIAL          -> tau above null, magnitude modest, reported as such

PRE-REGISTERED KILL -- conditional on both controls.
    if the identity control returns tau = 1 and the permutation null is within MDE of 0:
        tau within MDE of null            -> W-INDEPENDENT
        tau > null and |tau| >= 0.30      -> W-TARGET-IS-LENGTH
        else                              -> W-PARTIAL
    else: UNVERIFIED -- the correlation estimator is unfit.

CONTROLS
  IDENTITY (+)  tau between `score` and ITSELF must be exactly 1.0. An estimator that cannot return
                1 on a perfect association cannot be trusted to report a weak one.
  PERM (-)      lengths permuted WITHIN each interaction destroys the pairing and preserves both
                marginal distributions. It must return tau ~ 0. ⚠ A permutation null answers `did the
                pairing matter`, never WHY -- so the world it excludes is named explicitly: "length
                and score are unrelated within an interaction", and nothing more.
  STRATIFIED    reported per response-count stratum, because P(longest = top) has a different
                arithmetic floor (1/n) in each and pooling them is the error the strata round caught.
  NON-EMPTY     a stratum with < 2 conversations is UNVERIFIED, never 0.0.

MULTIPLICITY    strata x 2 statistics + 2 controls; every cell printed.
ARTIFACT        results/r427_target_length.json with the source hash.

IMPOSSIBLE HERE
  WHY the association exists -- rater verbosity bias vs longer answers genuinely being better vs a
                               collection artifact are not separable from these fields.
  a causal claim             -- no intervention on length is available.

EXIT
    0  the controls hold and a branch is reached
    1  a control misbehaved -- UNVERIFIED
    2  the corpus is absent -- never a silent pass
"""
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
ZEFF = 1.959964 + 0.841621


def tau_b(x, y):
    """Kendall tau-b.

    ⛔ MY FIRST DENOMINATOR WAS WRONG AND THE IDENTITY CONTROL CAUGHT IT: tau(score, score) came
    back 0.9453 instead of 1.0. I had used sqrt((c+d+tx)(c+d+ty)), which is not tau-b. The
    definition is sqrt((n0-n1)(n0-n2)) with n0 = ALL pairs, n1 = pairs tied in x, n2 = pairs tied
    in y. For x == y that gives (n0-T)/(n0-T) = 1 exactly, which is the whole point of running the
    control -- an estimator that cannot return 1 on a perfect association cannot be trusted with a
    weak one. This is the ledger's `control fails for its own reasons` row, and here it failed for
    MY reasons, which is the version that is worth catching."""
    n = len(x)
    n0 = n * (n - 1) // 2
    c = d = n1 = n2 = 0
    for i in range(n):
        for j in range(i + 1, n):
            a, b = x[i] - x[j], y[i] - y[j]
            if a == 0:
                n1 += 1
            if b == 0:
                n2 += 1
            if a != 0 and b != 0:
                if (a > 0) == (b > 0):
                    c += 1
                else:
                    d += 1
    den = np.sqrt((n0 - n1) * (n0 - n2))
    # ⛔ AND THE IDENTITY CONTROL FAILED A SECOND TIME, AT 0.9880, FOR A DEFECT IN THE MEASUREMENT
    #    RATHER THAN THE CONTROL. When every score in an interaction is tied, n0 - n1 = 0 and tau is
    #    UNDEFINED. Returning 0.0 folds `undefined` into `no association` and biases EVERY average
    #    toward zero -- including the real tau I was about to report. That is the ledger's
    #    `floor == ceiling` sub-kind: the statistic is degenerate there and no value is admissible.
    #    Return None; the caller drops them and COUNTS them.
    return (c - d) / den if den > 0 else None


def clus(by):
    """Degenerate (None) interactions are DROPPED, never counted as zero."""
    a = np.array([np.mean([x for x in v if x is not None])
                  for v in by.values() if any(x is not None for x in v)], float)
    if len(a) < 2:
        return None
    return float(a.mean()), float(ZEFF * a.std(ddof=1) / np.sqrt(len(a))), len(a)


def main() -> int:
    prod = ROOT / "corebench" / "judge_transport.py"
    corpus = ROOT / "data" / "utterances.jsonl"
    if not (prod.exists() and corpus.exists()):
        print("  UNRUNNABLE: producer or corpus absent. Exit 2, never 0."); return 2
    spec = importlib.util.spec_from_file_location("jt", prod)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    data = m.load_second(corpus, 2200, 0)

    print("R427 · target_length — is the TARGET itself length-loaded?\n")
    print("  ⛔ I HAVE BEEN CALLING `length` A SHORTCUT BASELINE FOR THREE ANALYSES WITHOUT TESTING")
    print("     WHAT IT IMPLIES ABOUT THE TARGET. If the human `score` tracks length within an")
    print("     interaction, `length` is not a shortcut to beat — it is close to what the target IS,")
    print("     and every accuracy in this round is a length-reproduction score.\n")

    rng = np.random.default_rng(0)
    degenerate = [0]
    real, perm, ident, top = (collections.defaultdict(lambda: collections.defaultdict(list))
                              for _ in range(4))
    for cid, _iid, _pr, cands in data:
        sc = [c[2] for c in cands]
        ln = [float(len(c[1])) for c in cands]
        n = len(cands)
        t_real = tau_b(sc, ln)
        if t_real is None:
            degenerate[0] += 1
        real[n][cid].append(t_real)
        perm[n][cid].append(tau_b(sc, list(rng.permutation(ln))))
        ident[n][cid].append(tau_b(sc, sc))
        top[n][cid].append(1.0 if int(np.argmax(ln)) == int(np.argmax(sc)) else 0.0)

    ia = clus({k: v for n in ident for k, v in ident[n].items()})
    pa = clus({k: v for n in perm for k, v in perm[n].items()})
    id_ok = ia is not None and abs(ia[0] - 1.0) < 1e-9
    perm_ok = pa is not None and abs(pa[0]) <= max(pa[1], 1e-9)
    n_tot = sum(len(v) for n in real for v in real[n].values())
    print("  CONTROLS")
    print(f"    DEGENERATE    interactions where every score ties, so tau is UNDEFINED: "
          f"{degenerate[0]:,} of {n_tot:,} ({degenerate[0]/n_tot:.1%}) — DROPPED, never counted as 0")
    print(f"    IDENTITY (+)  tau(score, score) = {ia[0]:.4f}   "
          f"{'PASS' if id_ok else 'FAIL — the estimator cannot return 1 on a perfect association'}")
    print(f"    PERM (-)      lengths permuted WITHIN each interaction: tau = {pa[0]:+.4f} "
          f"vs its MDE {pa[1]:.4f}   {'PASS' if perm_ok else 'FAIL'}")
    print(f"                  ⚠ this answers `did the pairing matter`, never WHY. The world it")
    print(f"                    excludes is exactly: `length and score are unrelated within an")
    print(f"                    interaction`, and nothing more.")
    if not (id_ok and perm_ok):
        print("\n  UNVERIFIED — the correlation estimator is unfit. Exit 1."); return 1

    print(f"\n  {'n_resp':<8} {'tau(score,len)':>15} {'MDE':>8} {'perm null':>10} "
          f"{'P(longest=top)':>15} {'1/n':>7} {'convs':>7}")
    rows, taus = {}, []
    for n in sorted(real):
        r, p_, t_ = clus(real[n]), clus(perm[n]), clus(top[n])
        if r is None or t_ is None:
            print(f"    {n:<8} {'—':>15} {'—':>8} {'—':>10} {'—':>15} {1/n:>7.4f} "
                  f"{len(real[n]):>7}   UNVERIFIED")
            continue
        rows[n] = dict(tau=r[0], mde=r[1], perm=p_[0] if p_ else None, top=t_[0], chance=1/n,
                       convs=r[2])
        taus.append(r[0])
        print(f"    {n:<8} {r[0]:>+15.4f} {r[1]:>8.4f} {(p_[0] if p_ else 0):>+10.4f} "
              f"{t_[0]:>15.4f} {1/n:>7.4f} {r[2]:>7,}")

    pooled = clus({k: v for n in real for k, v in real[n].items()})
    print(f"\n    pooled tau {pooled[0]:+.4f} vs MDE {pooled[1]:.4f} · permutation null "
          f"{pa[0]:+.4f}")

    print()
    if abs(pooled[0]) <= pooled[1]:
        v = "W_INDEPENDENT"
        print(f"  W-INDEPENDENT — tau sits on its permutation null. Length and the human target are")
        print(f"  unrelated within an interaction, so `length` really is an EXTERNAL shortcut and the")
        print(f"  fact that it beats the core is a fact about the core alone.")
    elif abs(pooled[0]) >= 0.30:
        v = "W_TARGET_IS_LENGTH"
        print(f"  W-TARGET-IS-LENGTH — tau {pooled[0]:+.4f} is far above its null. `length` is not a")
        print(f"  shortcut to beat; it is close to a restatement of the target.")
        print(f"  ⛔ SO R427's NUMBERS MEASURE HOW WELL A CRITERION-BASED CORE REPRODUCES A LENGTH")
        print(f"     PREFERENCE. The finding stands and its WORDING must change: `the core loses to a")
        print(f"     heuristic` becomes `the core does not reproduce this corpus's length preference`,")
        print(f"     which is a claim about the CORPUS as much as about the core.")
    else:
        v = "W_PARTIAL"
        print(f"  W-PARTIAL — tau {pooled[0]:+.4f} is resolvably above its null ({pa[0]:+.4f}) but")
        print(f"  modest. Both readings hold in part, so this is reported as a BOUND: the target is")
        print(f"  length-loaded to a degree that matters and does not reduce to length.")
    print(f"  ⚠ WHY the association exists is NOT identified — rater verbosity bias, longer answers")
    print(f"    being genuinely better, and a collection artifact are not separable from these")
    print(f"    fields. No intervention on length is available, so no causal claim is made.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               strata={str(k): v2 for k, v2 in rows.items()}, pooled_tau=pooled[0],
               pooled_mde=pooled[1], perm_null=pa[0], perm_mde=pa[1], identity=ia[0], verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_target_length.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
