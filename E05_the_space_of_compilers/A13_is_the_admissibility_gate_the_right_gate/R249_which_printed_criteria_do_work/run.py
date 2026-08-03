"""R249 -- the `representative` field has been FAILED since R236. This measures what goes in it.

WHAT R236's CERTIFICATE SAYS AND WHY IT IS STUCK
    representative FAILED -- "4 printed, at most 2 identifiable (R228). The artifact does not
    distinguish identified items from chosen ones. Naming the split would pass the field without
    changing a single criterion."

    Eight rounds have repeated that sentence. None has produced the split, because R228's k_max is
    a statement about the SPACE of candidate subsets, and the certificate needs a statement about
    THE FOUR CRITERIA THAT WERE PRINTED. Those are different objects and the arc kept substituting
    one for the other.

WHAT IS DIRECTLY MEASURABLE AND NEVER WAS
    The core is scored unweighted -- R231 sums the core's satisfaction rows -- so "does criterion j
    do any work" is a leave-one-out on the printed set, exact and exhaustive:

        necessary(j)  <=>  class(core \\ {j}) != class(core)
        minimal(core) =  size of the smallest subset of the printed core inducing the same class

    And the question that makes this a finding rather than a description: IS THE OFFICIAL CORE MORE
    OR LESS REDUNDANT THAN FOUR CRITERIA PICKED AT RANDOM? A compiler that selects mutually
    redundant criteria is spending its budget badly, and R248 just showed this rubric's criteria
    agree with one another far more than random ones do -- so redundancy is the live failure mode.

⚠ PROXY LEDGER, because necessity and identifiability are NOT the same property (P6)
    PROPERTY    the printed criterion is identified by the data
    PROXY       removing it changes the induced class
    IMPLICATION necessary => it does work WITHIN the printed set.  It does NOT imply the set is
                distinguishable from the other C(n,4) subsets -- R231 measured that separately and
                the answer there was 0.3864 against a floor of 0.3836.
    SAFE SIDE   redundant(j) is sound: if the class does not move, j contributed nothing to THIS
                observable, full stop. necessary(j) is reported as NECESSARY-WITHIN-SET and never
                promoted to "identified".

ESTIMAND        per prompt: (a) the number of printed core criteria whose removal changes the
                class; (b) the size of the minimal subset of the printed core inducing the same
                class; (c) the same two quantities for a size-matched random subset of the FULL
                rubric, paired on the same prompt.
IDENTIFICATION  exact and exhaustive over the printed set's power set. No sampling for (a) and (b);
                (c) uses 20 draws per prompt with its own spread reported.
SCOPE           population: prompts where the cached core tensor covers every printed criterion on
                all four responses. instrument: r04 Qwen3.5-2B cache, the same tensor R231 and R248
                used. baseline: random subsets of the full rubric of the same size, paired.
                regime: m=4, Q = the weak ordering over A-D, unweighted core as CoVal ships it.
WORLDS          W1 the compiler selects complementary criteria
                     -> the printed core is LESS redundant than a random subset of the same size
                W2 the compiler selects on individual salience, so its picks agree with each other
                     -> the printed core is MORE redundant than random. R248 predicts this world:
                        high-agreement criteria are exactly the ones a per-criterion score ranks up
                W3 redundancy is a property of the rubric, not of the selection
                     -> the two are indistinguishable, and the certificate's split is the same for
                        any four criteria one might have printed
KILL            pre-registered: if the paired difference (core minimal size - random minimal size)
                is inside the random arm's own draw spread, W3 holds and the `representative` field
                can be issued but carries NO information about the compiler. If the core is
                strictly MORE redundant, W2 holds and that is a defect of the compilation, not of
                the release.

                ⚠ THAT KILL WAS MIS-SCALED AND IS RECORDED AS UNVERIFIED, NOT AS ITS ANSWER. It
                compares a PAIRED MEAN over ~1000 prompts against a PER-PROMPT RANGE over 20 draws
                (2.2306). Those are not the same scale, and the range is an extreme order
                statistic -- the identical error this repository committed in R240 and added to
                realstat §4 as "min/max of N draws quoted as an interval" three commits ago. The
                threshold fired W3 while the paired CI is [-0.2479, -0.1626], excluding zero.
                Neither reading is admissible: the first is mis-scaled, the second is a threshold
                chosen after seeing the number. The W2/W3 question therefore stands OPEN and is
                settled by the arm registered below, whose reading rule is fixed before it runs.

W4 AND THE ARM THAT SEPARATES IT -- pre-registered, reading rule fixed before execution
                The confound I did not write down first time: the core's criteria are NOT the full
                rubric's criteria. They are compiled, rewritten text, and R248 showed criteria that
                AGREE with one another collapse the class. A rewrite into a more generic register
                would produce mutual agreement with no selection effect at all.
                  W4  the redundancy comes from GENERIC TEXT, not from which criteria were chosen.
                THE SEPARATOR: random 4-subsets of R240's 200-criterion GENERIC vocabulary -- real
                full-rubric criteria, selected only for token genericness, never for outcome.
                  if generic-random minimal size ~= the CORE's  -> W4: genericness explains it
                  if generic-random minimal size ~= full-random -> genericness does not; selection
                                                                   or rewriting does
                "~=" means: within the standard error of the paired difference between those two
                arms, computed on the prompts where all three arms exist. Stated before the run.
POSITIVE CTRL   a synthetic core of 4: one DISCRIMINATING criterion (satisfaction [1,0,0,0]) and
                three CONSTANT ones ([.5,.5,.5,.5]). Minimal size must be exactly 1 and exactly one
                criterion must be flagged necessary. This fails if the leave-one-out is wrong, and
                its target is an exact integer, not a range -- and it is reachable, which is the
                thing five controls in this arc were not.
NEGATIVE CTRL   four IDENTICAL criteria: every single one redundant, minimal size 1, necessary
                count 0. The extreme of W2, built rather than assumed.
SHAM            leave-one-out on random subsets of the FULL rubric -- the same operation, minus the
                ingredient under study, which is the compiler's selection.
PLACEBO         class(core) == class(core) exactly, and the minimal subset must induce exactly the
                core's class by construction. Both must be exact or the class function is broken.
NOISE FLOOR     the random arm's draw spread, per prompt, reported beside every paired difference.
MULTIPLICITY    2 statistics x 2 arms x all prompts, plus 20 draws in the random arm. The paired
                difference is one test per statistic; both reported, survivor or not.
SPECIFICATION   swept: subset size (the core's own size, which varies), and whether the comparand
                is drawn from the full rubric or from the core's own size class.
ARTIFACT        per-prompt necessity vectors persisted, so the certificate can be issued for any
                individual prompt without re-running.
IMPOSSIBLE      whether a criterion a HUMAN would call load-bearing is flagged necessary here. No
                labels of that kind exist in the release, and manufacturing them from my own
                reading is exactly the imagination-validated control realstat §4 forbids.
"""
from __future__ import annotations
import collections, itertools, json, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
DRAWS = 20


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def analyse(M):
    """M: (k, 4) unweighted satisfaction rows. Returns (n_necessary, minimal_size, flags)."""
    k = len(M)
    base = cls(M.sum(0))
    flags = []
    for j in range(k):
        keep = [i for i in range(k) if i != j]
        flags.append(cls(M[keep].sum(0)) != base if keep else True)
    minimal = k
    for s in range(1, k + 1):
        if any(cls(M[list(c)].sum(0)) == base for c in itertools.combinations(range(k), s)):
            minimal = s
            break
    return sum(flags), minimal, flags


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    sc = r220.load_sat(R4 / "a04_core.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}

    print("=== controls, synthetic, before any real core is read ===")
    Mpos = np.array([[1.0, 0.0, 0.0, 0.0], [.5, .5, .5, .5], [.5, .5, .5, .5], [.5, .5, .5, .5]])
    np_, mp_, fp_ = analyse(Mpos)
    pos_ok = (np_ == 1 and mp_ == 1 and fp_[0] is True or fp_[0] == True) and np_ == 1 and mp_ == 1
    print(" POSITIVE 1 discriminating + 3 constant : necessary %d (target 1)  minimal %d (target 1)"
          "  flags %s  %s" % (np_, mp_, ["N" if f else "-" for f in fp_],
                              "OK" if (np_ == 1 and mp_ == 1 and fp_[0]) else "LEAVE-ONE-OUT BROKEN"))
    Mneg = np.tile(np.array([0.9, 0.4, 0.2, 0.7]), (4, 1))
    nn_, mn_, fn_ = analyse(Mneg)
    neg_ok = (nn_ == 0 and mn_ == 1)
    print(" NEGATIVE 4 identical criteria          : necessary %d (target 0)  minimal %d (target 1)"
          "  %s" % (nn_, mn_, "OK" if neg_ok else "BROKEN"))

    # W4 arm: R240's 200 GENERIC full-rubric criteria, per prompt, outcome-blind selection
    GT = ROOT / ("E05_the_space_of_compilers/A10_is_a_global_core_real/R240_fit_a_global_core"
                 "/results/sat_global.npz")
    GEN = {}
    if GT.exists():
        gd = np.load(GT, allow_pickle=True)
        tmp = collections.defaultdict(lambda: np.zeros((200, 4), dtype=np.float32))
        for m, v in zip(gd["meta"], gd["sat"]):
            pp, vi, r_ = str(m).split("|")
            tmp[pp][int(vi), int(r_)] = v
        GEN = dict(tmp)
    print(" W4 ARM   generic-vocabulary tensor available on %d prompts" % len(GEN))

    rows, rand_rows, sizes, gen_rows = [], [], [], []
    rng = np.random.default_rng(0)
    placebo_ok = True
    for p in sorted(sc):
        if p not in recs or p not in sf:
            continue
        cj = sorted({k[0] for k in sc[p]})
        if not cj or not all((j, x) in sc[p] for j in cj for x in L):
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < len(cj) + 1:
            continue
        M = np.array([[sc[p][(j, x)] for x in L] for j in cj], float)
        nec, mini, flags = analyse(M)
        base = cls(M.sum(0))
        # PLACEBO: the minimal subset must induce EXACTLY the core's class
        found = False
        for c in itertools.combinations(range(len(cj)), mini):
            if cls(M[list(c)].sum(0)) == base:
                found = True
                break
        placebo_ok &= found
        rows.append((len(cj), nec, mini))
        sizes.append(len(cj))
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        rr = []
        for d in range(DRAWS):
            idx = list(rng.choice(len(ok), size=len(cj), replace=False))
            rn, rm, _fl = analyse(S[idx])
            rr.append((rn, rm))
        rand_rows.append((float(np.mean([a for a, _b in rr])),
                          float(np.mean([b for _a, b in rr])),
                          float(np.ptp([b for _a, b in rr]))))
        if p in GEN:
            G = GEN[p].astype(float)
            gm = [analyse(G[list(rng.choice(len(G), size=len(cj), replace=False))])[1]
                  for _ in range(DRAWS)]
            gen_rows.append((len(rows) - 1, float(np.mean(gm))))

    n = len(rows)
    print(" PLACEBO  minimal subset induces the core's own class on all %d prompts : %s"
          % (n, "OK" if placebo_ok else "CLASS FUNCTION BROKEN -- all cells void"))
    print("\nprompts %d | printed core size: %s" % (n, dict(collections.Counter(sizes))))

    nec = np.array([r[1] for r in rows], float)
    mini = np.array([r[2] for r in rows], float)
    ksz = np.array([r[0] for r in rows], float)
    rnec = np.array([r[0] for r in rand_rows])
    rmin = np.array([r[1] for r in rand_rows])
    rsp = np.array([r[2] for r in rand_rows])

    print("\n=== how much of the printed core does work ===")
    print(" criteria printed, mean                       : %.4f" % ksz.mean())
    print(" of those, NECESSARY-WITHIN-SET, mean         : %.4f  (%.1f%% of what is printed)"
          % (nec.mean(), 100 * nec.mean() / ksz.mean()))
    print(" MINIMAL subset reproducing the class, mean   : %.4f" % mini.mean())
    print(" prompts where ZERO printed criteria are necessary : %.4f" % float((nec == 0).mean()))
    print(" prompts where ALL printed criteria are necessary  : %.4f" % float((nec == ksz).mean()))
    print(" distribution of minimal size : %s"
          % dict(sorted(collections.Counter(mini.astype(int)).items())))

    print("\n=== the comparison that makes it a finding: core vs random, paired per prompt ===")
    dn, dm = nec - rnec, mini - rmin
    print(" %-34s %10s %10s %12s" % ("", "core", "random", "paired diff"))
    print(" %-34s %10.4f %10.4f %12s"
          % ("necessary criteria", nec.mean(), rnec.mean(), "%+.4f" % dn.mean()))
    print(" %-34s %10.4f %10.4f %12s"
          % ("minimal sufficient size", mini.mean(), rmin.mean(), "%+.4f" % dm.mean()))
    print(" random arm's own draw spread on minimal size, mean : %.4f" % rsp.mean())
    se = float(np.std(dm, ddof=1) / np.sqrt(len(dm)))
    print(" paired diff on minimal size : %+.4f  se %.4f  [%.4f, %.4f]"
          % (dm.mean(), se, dm.mean() - 1.96 * se, dm.mean() + 1.96 * se))
    print(" share of prompts where the core is STRICTLY more redundant than the random median : "
          "%.4f" % float((dm < 0).mean()))

    print("\n=== W4 arm: does GENERIC TEXT explain the redundancy? (registered before the run) ===")
    w4 = None
    if len(gen_rows) >= 30:
        gi = [i for i, _g in gen_rows]
        gv = np.array([g for _i, g in gen_rows])
        c_sub, r_sub = mini[gi], rmin[gi]
        d_cg = c_sub - gv                      # core  - generic
        d_rg = r_sub - gv                      # full-random - generic
        se_cg = float(np.std(d_cg, ddof=1) / np.sqrt(len(d_cg)))
        se_rg = float(np.std(d_rg, ddof=1) / np.sqrt(len(d_rg)))
        print(" prompts with all three arms : %d" % len(gv))
        print(" %-26s %10s" % ("minimal sufficient size", "mean"))
        print(" %-26s %10.4f" % ("  CORE (printed)", c_sub.mean()))
        print(" %-26s %10.4f" % ("  GENERIC vocabulary", gv.mean()))
        print(" %-26s %10.4f" % ("  FULL-rubric random", r_sub.mean()))
        print(" paired core - generic      : %+.4f  se %.4f  [%.4f, %.4f]"
              % (d_cg.mean(), se_cg, d_cg.mean() - 1.96 * se_cg, d_cg.mean() + 1.96 * se_cg))
        print(" paired full-random - generic: %+.4f  se %.4f  [%.4f, %.4f]"
              % (d_rg.mean(), se_rg, d_rg.mean() - 1.96 * se_rg, d_rg.mean() + 1.96 * se_rg))
        near_core = abs(d_cg.mean()) <= 1.96 * se_cg
        near_rand = abs(d_rg.mean()) <= 1.96 * se_rg
        w4 = ("W4 CONFIRMED -- generic text explains it: the generic vocabulary is as redundant as "
              "the printed core (%+.4f, CI contains 0) while full-rubric random is not (%+.4f). "
              "The compiler's redundancy is inherited from WRITING GENERIC CRITERIA, not from "
              "which criteria it chose." % (d_cg.mean(), d_rg.mean())) if (near_core and not near_rand) \
            else ("W4 REFUTED -- the generic vocabulary is as redundant as FULL-RUBRIC RANDOM "
                  "(%+.4f, CI contains 0) and the core differs from it by %+.4f. Genericness does "
                  "not explain the core's redundancy." % (d_rg.mean(), d_cg.mean())) \
            if (near_rand and not near_core) else \
            ("W4 UNRESOLVED -- core-generic %+.4f and random-generic %+.4f; the three arms do not "
             "separate at this n. Reported as UNRESOLVED, never as either answer."
             % (d_cg.mean(), d_rg.mean()))
        print("\n  " + w4)
    else:
        print(" NOT RUN -- fewer than 30 prompts carry the generic tensor. Reported ABSENT.")

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not ((np_ == 1 and mp_ == 1 and fp_[0]) and neg_ok and placebo_ok):
        v = "UNVERIFIED -- a control did not behave; the leave-one-out or the class function is wrong."
    else:
        v = ("THE ORIGINAL KILL IS UNVERIFIED, BY ITS OWN SCALE ERROR. It compares a paired mean "
             "over %d prompts (%+.4f) against a per-prompt range over %d draws (%.4f) and fired W3; "
             "the paired CI is [%.4f, %.4f] and excludes zero, which reads W2. A mean and an extreme "
             "order statistic are not comparable -- the same defect this repository added to "
             "realstat as 'min/max of N draws quoted as an interval' three commits ago. Neither "
             "reading is admissible and the W2/W3 question is settled by the W4 arm instead.\n\n  "
             "WHAT IS ESTABLISHED REGARDLESS, and it is what the certificate needed: of %.2f "
             "criteria printed per core, %.2f are NECESSARY-WITHIN-SET (%.1f%%) and the smallest "
             "subset reproducing the printed core's own class is %.2f. On %.1f%% of prompts ZERO "
             "printed criteria are necessary; on %.1f%% all are. The `representative` field can be "
             "issued from these numbers today.\n\n  W4: %s"
             % (len(dm), dm.mean(), DRAWS, rsp.mean(),
                dm.mean() - 1.96 * se, dm.mean() + 1.96 * se,
                ksz.mean(), nec.mean(), 100 * nec.mean() / ksz.mean(), mini.mean(),
                100 * float((nec == 0).mean()), 100 * float((nec == ksz).mean()),
                w4 or "ABSENT"))
    print("\n  " + v)
    print("\n  ⚠ PROXY: `necessary` means necessary WITHIN THE PRINTED SET. It is not identifiability")
    print("    among the C(n,k) alternatives -- R231 measured that separately at 0.3864 against a")
    print("    floor of 0.3836. Only `redundant` is sound in both directions.")
    json.dump({"prompts": n, "core_size_mean": float(ksz.mean()),
               "necessary_mean": float(nec.mean()), "minimal_mean": float(mini.mean()),
               "zero_necessary_share": float((nec == 0).mean()),
               "all_necessary_share": float((nec == ksz).mean()),
               "random_necessary_mean": float(rnec.mean()), "random_minimal_mean": float(rmin.mean()),
               "paired_diff_minimal": float(dm.mean()), "paired_se": se,
               "random_draw_spread": float(rsp.mean()),
               "minimal_distribution": {str(k): int(v_) for k, v_ in
                                        sorted(collections.Counter(mini.astype(int)).items())},
               "controls": {"positive": bool(np_ == 1 and mp_ == 1 and fp_[0]),
                            "negative": bool(neg_ok), "placebo": bool(placebo_ok)},
               "w4": w4, "verdict": v}, open(OUT / "representative_field.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
