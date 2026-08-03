"""R224 -- which definitions of "core" this release can identify at all.

realstat G1: ESTIMAND BEFORE METHOD, and IDENTIFICATION BEFORE POWER. Asking for power on an
unidentified quantity is how a well-powered-looking round gets built. So before proposing any
definition of `core`, compute whether the data carries enough information to pick one out.

THE DERIVATION (this is a DERIVATION, not a measurement -- it could not have come out otherwise,
and it is labelled so)

    A definition of the form "the k-subset of the n criteria that best preserves the decision"
    ranges over a hypothesis space of size C(n,k). Identifying one member needs

        H_need = log2 C(n, k)   bits.

    What the release offers per prompt is the induced ordering over m candidate responses. The
    number of WEAK orderings of m items is the ordered Bell (Fubini) number a(m), so a single
    ranking carries at most

        H_have = log2 a(m)      bits.        a = 1, 1, 3, 13, 75, 541, 4683, ...

    ⚠ AND ADDING RATERS DOES NOT RAISE H_have. Every rater ranks THE SAME m responses against the
    same criteria set. Their disagreement is information about RATERS, not about which criteria are
    right; the quantity a core is being fitted to is the consensus ordering, and there is exactly
    one of those per prompt. R raters buy precision on a 6-bit object, never a 60-bit one.

    Identifiable  <=>  H_need <= H_have.

    At the release's own numbers -- median n = 15, k = 4, m = 4:
        H_need = log2 C(15,4) = log2 1365 = 10.41
        H_have = log2 a(4)    = log2 75   =  6.23
    10.41 > 6.23, so the estimand is NOT IDENTIFIED, by a factor of 2^4.2 = 18 in hypothesis count.

    This predicts R221 exactly and independently: R221 MEASURED that 100% of prompts admit a single
    criterion reproducing the whole ranking, median 3 tied. The bound says that had to happen.

WHAT IT BUYS
    The same inequality, solved for m, is a design specification: the smallest candidate-set size at
    which a k-of-n core is identifiable at all. That is the missing field R220 and R223 both ended
    on, expressed as a number a next elicitation can be built to.
"""
from __future__ import annotations

import json, math, pathlib, sys, collections
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
K = 4


def fubini(m):
    """Ordered Bell number: weak orderings of m items (ties allowed)."""
    a = [1]
    for i in range(1, m + 1):
        a.append(sum(math.comb(i, j) * a[i - j] for j in range(1, i + 1)))
    return a[m]


def bits_needed(n, k):
    return math.log2(math.comb(n, min(k, n))) if n > k else 0.0


def min_m(n, k, ties=True):
    """Smallest candidate-set size whose ordering space covers C(n,k)."""
    need = bits_needed(n, k)
    m = 2
    while m < 60:
        have = math.log2(fubini(m) if ties else math.factorial(m))
        if have >= need:
            return m
        m += 1
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ns = []
    for line in (DATA / "conversation_rubrics.jsonl").open():
        d = json.loads(line)
        rated = [it for it in d["coval_full"] if it.get("scores")]
        if rated:
            ns.append(len(rated))
    ns = np.array(ns)

    print("=== the release's own numbers ===")
    print(" prompts %d | criteria per prompt: median %d  mean %.1f  p10 %d  p90 %d  max %d"
          % (len(ns), np.median(ns), ns.mean(), np.percentile(ns, 10), np.percentile(ns, 90),
             ns.max()))
    print(" candidate responses per prompt: 4 (fixed by the release)")

    print("\n=== the bound, as a DERIVATION ===")
    print(" %-4s %10s %10s %10s   %s" % ("m", "a(m)", "log2 a(m)", "orderings", "note"))
    for m in range(2, 9):
        print(" %-4d %10d %10.2f %10s   %s"
              % (m, fubini(m), math.log2(fubini(m)), math.factorial(m),
                 "<- the release" if m == 4 else ""))

    med = int(np.median(ns))
    need_med = bits_needed(med, K)
    have4 = math.log2(fubini(4))
    print("\n at the median prompt (n=%d, k=%d):" % (med, K))
    print("   H_need = log2 C(%d,%d) = log2 %d = %.2f bits" % (med, K, math.comb(med, K), need_med))
    print("   H_have = log2 a(4)     = log2 75 = %.2f bits" % have4)
    print("   deficit %.2f bits  =>  %.0fx more hypotheses than the observable can separate"
          % (need_med - have4, 2 ** (need_med - have4)))

    # per-prompt identifiability, and the m each prompt would need
    need = np.array([bits_needed(int(n), K) for n in ns])
    ident = need <= have4
    req_m = np.array([min_m(int(n), K) for n in ns], float)
    print("\n=== per prompt ===")
    print(" identifiable at m=4 with ties : %d / %d  (%.1f%%)"
          % (ident.sum(), len(ns), 100 * ident.mean()))
    print(" identifiable at m=4, strict orderings only (log2 4! = %.2f) : %d  (%.1f%%)"
          % (math.log2(24), (need <= math.log2(24)).sum(), 100 * (need <= math.log2(24)).mean()))
    print(" candidate-set size required   : median %.0f  p90 %.0f  max %.0f"
          % (np.median(req_m), np.percentile(req_m, 90), np.nanmax(req_m)))
    for m in range(4, 9):
        print("   at m=%d : %5.1f%% of prompts identifiable" % (m, 100 * np.mean(req_m <= m)))

    print("\n=== which definitions of 'core' survive this ===")
    DEFS = [
        ("minimal k-subset preserving the source's DECISION", need_med, have4,
         "the definition E05 was built on"),
        ("the k highest-RATED criteria", 0.0, have4,
         "a function of the ratings; no inference, so nothing to identify"),
        ("the k-subset maximising HUMAN agreement", need_med, have4,
         "same hypothesis space, same observable, same deficit"),
        ("a TYPED policy + certificate naming its query family", 0.0, have4,
         "the estimand is the certificate's contents, which are observed, not inferred"),
    ]
    print(" %-52s %8s %8s  %s" % ("definition", "H_need", "H_have", "verdict"))
    for nm, nd, hv, why in DEFS:
        print(" %-52s %8.2f %8.2f  %s" % (nm, nd, hv,
                                          "IDENTIFIED" if nd <= hv else "NOT IDENTIFIED"))
        print("   %s" % why)

    res = {"prompts": len(ns), "n_median": int(np.median(ns)), "k": K, "m_release": 4,
           "fubini": {str(m): fubini(m) for m in range(2, 9)},
           "H_need_median": need_med, "H_have_m4": have4,
           "deficit_bits": need_med - have4,
           "share_identifiable_at_m4_ties": float(ident.mean()),
           "share_identifiable_at_m4_strict": float((need <= math.log2(24)).mean()),
           "required_m": {"median": float(np.median(req_m)),
                          "p90": float(np.percentile(req_m, 90)),
                          "max": float(np.nanmax(req_m))},
           "share_identifiable_by_m": {str(m): float(np.mean(req_m <= m)) for m in range(4, 12)}}
    (OUT / "identifiability.json").write_text(json.dumps(res, indent=1))

    print("\n" + "=" * 78)
    print("THE FORMULATION THAT SURVIVES")
    print("=" * 78)
    print("""
 A core is NOT a compression of the rubric. It is a pair

     (policy, certificate)

 where the certificate names a query family Q, and the policy is ADMISSIBLE only if

     log2 |H(Q)|  <=  log2 a(m)

 -- the hypothesis space the sufficiency question ranges over is no larger than the
 candidate orderings the source data can distinguish.

 The inequality is what makes the definition FAILABLE, which is the whole point:
 a definition of `core` that cannot be shown unidentifiable on some dataset is not a
 definition, it is a name. On THIS release the decision-preserving definition fails it
 at every prompt, and that is a fact about the RELEASE's design, not about any compiler.
""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
