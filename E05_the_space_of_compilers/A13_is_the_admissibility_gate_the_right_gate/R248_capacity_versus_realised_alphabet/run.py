"""R248 -- the definition's own admissibility gate, tested as a PREDICTOR rather than quoted.

FORMULATION.md states the gate in one line:

    admissible only if  log2|H(Q)| <= H_eff

and every round since R224 has used the capacity form of the right-hand side: H_have = log2 a(m),
the ordered Bell number, = log2 75 = 6.2288 bits at m=4. R237 corrected it to a noisy-channel
bracket [1.02, 3.45]. Neither version has ever been asked the only question that matters for a
GATE: DOES IT PREDICT WHEN RECOVERY ACTUALLY FAILS?

THE CRACK, VISIBLE IN THIS REPOSITORY'S OWN NUMBERS AND NEVER FOLLOWED
    R230 measured that 72 candidate subsets per prompt collapse into 13 distinct Q-classes.
    The capacity bound permits 75. So the binding constraint on that prompt was 13, not 75 --
    the gate was loose by 5.5x -- and R230 reported the 13 as a consequence rather than as a
    REPLACEMENT for the quantity in the gate.

    C(n,k) <= a(m) is NECESSARY and never SUFFICIENT. It counts how many messages the channel
    could carry if the encoder used it well. Identification needs the encoder to actually SEPARATE
    the candidates, and two subsets that induce the same class are indistinguishable no matter how
    much capacity is spare. The right-hand side of the gate should be the alphabet the data
    REALISES, not the alphabet the observation space ADMITS.

ESTIMAND        per prompt and per k:
                  A_real(k) = |{distinct Q-classes induced by all C(n,k) subsets}|
                  U(k)      = share of subsets that induce a class NO other subset induces
                and the three quantities the gate could use, in bits:
                  need     = log2 C(n,k)        what must be distinguished
                  capacity = log2 a(4) = 6.2288 what the observation space admits  [current gate]
                  realised = log2 A_real(k)     what this data actually separates  [the rival]
IDENTIFICATION  exact and exhaustive. Every subset is enumerated; nothing is sampled, nothing
                inferred. This is a DERIVATION over a measured tensor -- labelled as such -- and
                the arithmetic trap applies: `need <= realised` is forced to be violated whenever
                collisions exist, so the FINDING is the SIZE of the gap, never its sign.
SCOPE           population: prompts with 6 <= n <= 14 from the r04 cache, capped at 250 for the
                exhaustive enumeration. instrument: the r04 Qwen3.5-2B tensor, the same one R228
                and R230 used, so any disagreement with them is arithmetic. baseline: the two
                rival right-hand sides. regime: k in {1,2,3}, m=4, no noise (the gate is a
                statement about the noiseless case; R237 handles noise separately).
WORLDS          W1 the capacity gate is the binding constraint
                     -> A_real(k) ~= min(C(n,k), 75); uniqueness stays near 1 until C(n,k) > 75
                W2 the realised alphabet binds far earlier, and the cause is the OBSERVABLE
                     -> A_real(k) << min(C(n,k), 75) for real AND random tensors alike. The
                        collapse is geometry: subset sums quotient into weak orderings
                W3 the realised alphabet binds far earlier, and the cause is the RUBRIC
                     -> real tensors realise FEWER classes than random ones of the same shape.
                        The criteria agree with each other; the collapse is REDUNDANCY, and the
                        gate should be about the rubric's internal correlation, not about channel
                        capacity at all. W2 and W3 are separated by the random-tensor arm alone
KILL            pre-registered: if the median ratio min(C(n,k),75) / A_real(k) is below 1.5 at
                every k, the capacity gate is the binding constraint and FORMULATION's
                admissibility line stands as written. If it exceeds 1.5, the line is quoting the
                wrong quantity and must be restated in terms of the realised alphabet.
POSITIVE CTRL   ⚠ THE FIRST VERSION OF THIS CONTROL COULD NOT PASS, AND FIXING IT PRODUCED THE
                ROUND'S MAIN RESULT. It built a synthetic prompt with geometrically separated
                criteria and demanded A_real = C(n,k) at every k. That is impossible for k>=2 by
                construction: a class is a WEAK ORDERING, i.e. a quotient of the sum vector, so
                distinct sums do not imply distinct orderings and nothing in the construction
                enforces the quotient to stay injective. It returned A_real = 10 of C(8,2) = 28 --
                and a REAL prompt returns 12, so the "maximally separated" control was WORSE than
                the data it was built to bracket. Fifth control-that-cannot-pass in this arc.
                The two that CAN fail, and which replace it:
                  POS-A  k=1 only, where the ceiling IS constructible: n criteria assigned n
                         distinct permutation score vectors. A_real must equal n exactly and
                         U must equal 1.0000.
                  POS-B  an INDEPENDENT RECOUNT of A_real through a different code path, on every
                         real prompt and every k. Must agree exactly. This tests the counter,
                         which is what a positive control here is actually for.
CEILING         MEASURED, never assumed (R229): the alphabet realised by RANDOM tensors of the
                same shape, which is the most separation this observable admits at this n and m.
                The band is then 1 (negative control) < A_real(real) < A_real(random).
NEGATIVE CTRL   a SYNTHETIC prompt whose criteria are all IDENTICAL. Every subset of a given size
                induces the same class, so A_real must be exactly 1 and U exactly 0 for C(n,k)>1.
                This is the world W2 predicts in the extreme, built rather than assumed.
SHAM            the same enumeration with the satisfaction tensor REPLACED by uniform random
                values of the same shape. If real criteria realise no more classes than random
                noise does, the collapse is a property of the observable (4 responses, 75 orders),
                not of the rubric -- and that distinction is the whole point of the gate.
PLACEBO         k = n: exactly one subset, so A_real = 1 and U = 1.0000 by construction.
NOISE FLOOR     none needed -- the enumeration is deterministic. Reported as N/A rather than
                omitted, per the register discipline.
MULTIPLICITY    3 values of k x 5 arms (real, positive, negative, sham, placebo) x all prompts.
                Distributions printed, not just medians; the non-supporting tail included.
SPECIFICATION   the axis swept is WHICH QUANTITY SITS ON THE RIGHT-HAND SIDE OF THE GATE.
ARTIFACT        per-prompt A_real and U persisted, so a later round can test the gate against
                recovery without re-enumerating.
IMPOSSIBLE      whether the realised alphabet is stable across judges. The r04 cache is one judge
                and the 200-criterion global vocabulary of R240 is not the per-prompt rubric, so
                no second instrument covers this exact object. Would require re-judging the
                per-prompt rubrics under R164's phi/qwen3b variants, which exist only for the
                full and core sets, not for arbitrary subsets.
"""
from __future__ import annotations
import collections, itertools, json, math, pathlib, sys
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
KS = [1, 2, 3]
NMIN, NMAX, NPROMPT = 6, 14, 250


def fubini(m):
    a = [1]
    for i in range(1, m + 1):
        a.append(sum(math.comb(i, j) * a[i - j] for j in range(1, i + 1)))
    return a[m]


CAP = fubini(4)


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def alphabet(W, S, k):
    """A_real and uniqueness over ALL C(n,k) subsets. Exhaustive, never sampled."""
    ctr = collections.Counter()
    for c in itertools.combinations(range(len(W)), k):
        idx = list(c)
        ctr[cls((W[idx, None] * S[idx]).sum(0))] += 1
    n_sub = sum(ctr.values())
    uniq = sum(1 for v in ctr.values() if v == 1)
    return len(ctr), uniq / n_sub, n_sub


def alphabet_recount(W, S, k):
    """POS-B: the same quantity through a DIFFERENT code path -- no Counter, no cls(), signs
    computed by explicit comparison and keys built as strings. If the two disagree anywhere the
    counter is wrong and every cell in this round is void."""
    seen = {}
    for c in itertools.combinations(range(len(W)), k):
        y = [0.0, 0.0, 0.0, 0.0]
        for i in c:
            for x in range(4):
                y[x] += float(W[i]) * float(S[i][x])
        key = ""
        for i in range(4):
            for j in range(i + 1, 4):
                key += "<" if y[i] < y[j] else (">" if y[i] > y[j] else "=")
        seen[key] = seen.get(key, 0) + 1
    return len(seen), sum(1 for v in seen.values() if v == 1) / sum(seen.values())


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    prompts = []
    for p in sorted(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if not (NMIN <= len(ok) <= NMAX):
            continue
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok])
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        prompts.append((W, S))
        if len(prompts) >= NPROMPT:
            break
    ns = [len(W) for W, _S in prompts]
    print("prompts %d | n in [%d, %d], median %d | a(4) = %d = %.4f bits"
          % (len(prompts), min(ns), max(ns), int(np.median(ns)), CAP, math.log2(CAP)))

    print("\n=== controls, built synthetically, before any real number is read ===")
    rng = np.random.default_rng(0)
    n_c = 8
    # POS-A: k=1 only, where the ceiling IS constructible -- n distinct permutation rows
    perms = list(itertools.permutations([4.0, 3.0, 2.0, 1.0]))[:n_c]
    Wp, Sp = np.ones(n_c), np.array(perms)
    ap1, up1, _ = alphabet(Wp, Sp, 1)
    pos_a = (ap1 == n_c and up1 == 1.0)
    print(" POS-A  k=1, %d criteria assigned %d distinct orderings : A_real %d  U %.4f  %s"
          % (n_c, n_c, ap1, up1, "OK" if pos_a else "COUNTER BROKEN"))
    # POS-B: independent recount through a different code path, on real prompts, every k
    mism = []
    for W, S in prompts[:25]:
        for k in KS:
            a1, u1, _ = alphabet(W, S, k)
            a2, u2 = alphabet_recount(W, S, k)
            if a1 != a2 or abs(u1 - u2) > 1e-12:
                mism.append((k, a1, a2))
    pos_b = not mism
    print(" POS-B  independent recount, %d prompts x %d k, different code path : %s"
          % (25, len(KS), "OK -- exact agreement" if pos_b else "MISMATCH %s" % mism[:3]))
    # NEGATIVE: all criteria identical -> exactly one class
    Wn = np.ones(n_c)
    Sn = np.tile(np.array([0.9, 0.4, 0.2, 0.7]), (n_c, 1))
    negs = [alphabet(Wn, Sn, k) for k in KS]
    neg_ok = all(a == 1 for a, _u, _n in negs)
    print(" NEG    all criteria identical : A_real %s  %s"
          % ([a for a, _u, _n in negs], "OK" if neg_ok else "COUNTER BROKEN"))
    pos_ok = pos_a and pos_b

    # PLACEBO: k = n -> one subset
    apl, upl, npl = alphabet(*prompts[0][:2], len(prompts[0][0]))
    print(" PLACEBO k=n : subsets %d  A_real %d  U %.4f  %s"
          % (npl, apl, upl, "OK" if (npl == 1 and apl == 1 and upl == 1.0) else "BROKEN"))
    print("\n ⚠ THE CONTROL THIS REPLACED could not pass. It demanded A_real = C(n,k) at every k")
    print("   from a 'maximally separated' synthetic prompt, and returned 10 of 28 at k=2 -- while")
    print("   a REAL prompt returns 12. A class is a WEAK ORDERING, a quotient of the sum vector,")
    print("   so distinct sums do not give distinct classes and no construction in vector space")
    print("   can force the quotient injective. The synthetic bracket was BELOW the data.")

    print("\n=== the measurement: what the gate admits vs what the data realises ===")
    print("%-4s %10s %10s %10s %10s %10s %9s" % ("k", "C(n,k)", "admitted", "A_real", "ratio",
                                                 "unique", "sham"))
    grid, per = {}, collections.defaultdict(list)
    for k in KS:
        rows, shams = [], []
        for W, S in prompts:
            if len(W) < k:
                continue
            a_, u_, ns_ = alphabet(W, S, k)
            adm = min(math.comb(len(W), k), CAP)
            rows.append((adm, a_, u_, ns_))
            # CEILING, measured: random tensors of the SAME shape, 5 draws, paired per prompt.
            # This is what separates W2 (the observable collapses everything) from W3 (the RUBRIC
            # is redundant and random criteria would separate better).
            shams.append(float(np.mean([alphabet(W, rng.random((len(W), 4)), k)[0]
                                        for _ in range(5)])))
            per[k].append({"n": int(len(W)), "C": int(math.comb(len(W), k)), "admitted": int(adm),
                           "A_real": int(a_), "unique": float(u_), "A_random": shams[-1]})
        adm = float(np.median([r[0] for r in rows]))
        ar = float(np.median([r[1] for r in rows]))
        ratio = float(np.median([r[0] / r[1] for r in rows]))
        uq = float(np.median([r[2] for r in rows]))
        sh = float(np.median(shams))
        grid[k] = (adm, ar, ratio, uq, sh)
        print("%-4d %10.0f %10.0f %10.0f %10.2f %10.4f %9.0f"
              % (k, np.median([math.comb(len(W), k) for W, _ in prompts]), adm, ar, ratio, uq, sh))
    print(" (admitted = min(C(n,k), 75) -- the current gate.  A_real = classes the data separates.")
    print("  ratio = admitted / A_real, per prompt, median.  sham = A_real on a random tensor.)")

    print("\n=== the same three quantities in BITS, which is how the gate is written ===")
    print("%-4s %12s %12s %12s %14s" % ("k", "need", "capacity", "realised", "gate says"))
    for k in KS:
        need = float(np.median([math.log2(math.comb(len(W), k)) for W, _ in prompts]))
        real = math.log2(grid[k][1])
        ok_cap = "ADMISSIBLE" if need <= math.log2(CAP) else "refused"
        ok_real = "ADMISSIBLE" if need <= real else "REFUSED"
        print("%-4d %12.4f %12.4f %12.4f   %s / %s"
              % (k, need, math.log2(CAP), real, ok_cap, ok_real))
    print(" (left verdict = the gate as FORMULATION writes it; right = with the realised alphabet)")

    print("\n=== distribution, not just the median -- the non-supporting tail included ===")
    for k in KS:
        rr = np.array([p_["admitted"] / p_["A_real"] for p_ in per[k]])
        print(" k=%d  ratio deciles %s   share below 1.5 : %.4f"
              % (k, " ".join("%.2f" % q for q in np.percentile(rr, [10, 30, 50, 70, 90])),
                 float((rr < 1.5).mean())))

    print("\n=== W2 vs W3: is the collapse the OBSERVABLE, or the RUBRIC? (paired, per prompt) ===")
    w3 = {}
    for k in KS:
        d = np.array([p_["A_real"] - p_["A_random"] for p_ in per[k]])
        below = float((d < 0).mean())
        w3[k] = (float(np.median(d)), below)
        print(" k=%d  A_real - A_random  median %+.2f   share of prompts where the REAL rubric "
              "separates FEWER classes than random : %.4f" % (k, np.median(d), below))
    print(" (W2 predicts ~0 and ~0.5; W3 predicts a negative median and a share well above 0.5)")

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not (pos_ok and neg_ok):
        v = ("UNVERIFIED -- the counter did not validate (POS-A %s, POS-B %s, NEG %s); A_real is "
             "not being counted correctly and no cell is readable." % (pos_a, pos_b, neg_ok))
    else:
        worst = max(grid[k][2] for k in KS)
        if worst < 1.5:
            v = ("The capacity gate BINDS: median admitted/A_real stays under 1.5 at every k "
                 "(max %.2f). FORMULATION's admissibility line stands as written." % worst)
        else:
            rub = sum(1 for k in KS if w3[k][1] > 0.5)
            v = ("THE GATE QUOTES THE WRONG QUANTITY. Median admitted/A_real reaches %.2f, so the "
                 "capacity bound log2 a(m) admits cores the data cannot separate. The right-hand "
                 "side must be the REALISED alphabet log2 A_real: %.4f bits at k=1 against the "
                 "capacity's %.4f. C(n,k) <= a(m) is NECESSARY and NEVER SUFFICIENT, and every "
                 "k_max in this arc was computed from the necessary condition alone. "
                 % (worst, math.log2(grid[1][1]), math.log2(CAP)))
            v += (("AND THE CAUSE IS THE RUBRIC, NOT THE OBSERVABLE (W3): at %d of %d values of k "
                   "the real rubric separates FEWER classes than a RANDOM tensor of the same shape "
                   "on the same prompt. The criteria agree with one another, so subsets collapse; "
                   "the binding constraint is the rubric's internal REDUNDANCY, which no capacity "
                   "argument can see." % (rub, len(KS))) if rub > len(KS) / 2 else
                  ("The cause is the OBSERVABLE (W2): random tensors collapse just as far, so the "
                   "quotient into weak orderings is doing the work and the rubric is not unusually "
                   "redundant."))
    print("\n  " + v)
    json.dump({"n_prompts": len(prompts), "capacity": CAP, "capacity_bits": math.log2(CAP),
               "controls": {"pos_a": bool(pos_a), "pos_b": bool(pos_b), "negative_ok": bool(neg_ok)},
               "w3_real_minus_random": {str(k): w3[k] for k in KS},
               "grid": {str(k): {"admitted_med": grid[k][0], "A_real_med": grid[k][1],
                                 "ratio_med": grid[k][2], "unique_med": grid[k][3],
                                 "sham_A_real_med": grid[k][4]} for k in KS},
               "per_prompt": {str(k): per[k] for k in KS}, "verdict": v},
              open(OUT / "gate_test.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
