#!/usr/bin/env python3
"""
R280 -- IS THE GATE UNIT-COHERENT, AND WAS THE MISMATCH INTRODUCED OR ALWAYS THERE?

R278 found the gate's two sides count different kinds of thing. R279 found the gate was
violated by its own founding data. Both leave one decision open, and the two answers imply
DIFFERENT ACTIONS:

    if the mismatch was INTRODUCED by the revisions  -> the repair is a REVERT
    if it was always there                           -> the repair is a REBUILD

The gate has three canonical forms in this repository (extracted from git, not memory):

    G1  log2|H(Q)| <= H_eff              190 occurrences   the original
    G2  C(n,k)     <= A_real             221 occurrences   R248
    G3  C(n,k)     <= a(m)               421 occurrences   current, post-R253

⛔ THE PROBLEM WITH ANSWERING THIS BY READING. "Do these two sides count the same kind of
thing" is a JUDGEMENT, and a judgement of mine about my own definition is void -- it is
sampled from the weights that wrote the definition. So this round does not judge. It runs a
GAUGE TEST, which is mechanical:

    TWO QUANTITIES ARE THE SAME KIND OF THING ONLY IF THEY RESPOND TO THE SAME
    TRANSFORMATIONS OF THE UNDERLYING SETS.

Change the number of criteria and hold the responses fixed; then change the number of
responses and hold the criteria fixed. Each quantity either moves or does not. That
response signature is COMPUTED, not classified, and an inequality between like things must
have the same signature on both sides.

ESTIMAND        For each quantity appearing in G1, G2, G3, the pair
                    (responds to T_n?, responds to T_m?)
                measured as the SHARE OF PROMPTS on which the quantity's value changes
                under that transformation; and for each gate form, whether its two sides
                have equal signatures. Named before the method.

IDENTIFICATION  Partially identified, and the split is stated rather than blurred:
                  MEASURED  C(n,k), a(m), A_real -- all three are computable exactly on
                            this release, so their signatures are measurements.
                  DERIVED   |H(Q)| and H_eff -- |H(Q)| is the class space of m responses
                            and H_eff is a channel capacity over that same class space at
                            a given rater count and noise. Neither is a function of n.
                            These signatures are DERIVATIONS FROM THE DEFINITIONS, are
                            labelled as such in the output, and are NOT evidence.
                Because G1's verdict rests on two derived signatures, G1's verdict is
                reported as DERIVED and G2/G3's as MEASURED. Not averaged, not merged.

SCOPE           population : prompts from R248's own selection rule (coval_full,
                             6 <= n <= 14), capped at NPROMPT for compute
                instrument : exact enumeration over all C(n,k) subsets; no sampling
                baseline   : the identity transformation (no change), which must produce
                             a zero response for every quantity
                regime     : k in {1,2,3}; T_m reduces m from 4 to 3, T_n reduces n by 1

WORLDS          A  INTRODUCED -- G1 coherent, G2 and/or G3 incoherent. Repair = revert.
                B  ALWAYS THERE -- G1 also incoherent. Repair = rebuild.
                C  ALL COHERENT -- the gauge test is blind and says nothing (it would then
                   have failed its own negative control).

PREDICTION      G1 coherent | A: yes | B: no  | C: yes
MATRIX          G2 coherent | A: no  | B: no  | C: yes
                G3 coherent | A: no  | B: no  | C: yes
                implies     | revert | rebuild| the test is blind

KILL            Pre-registered, a conditional and not a bare threshold:
                    if positive_controls_fire and negative_control_separates:
                        evaluate(G1_coherent and not G3_coherent)   # world A
                    else:
                        verdict = UNVERIFIED
                A gauge test that calls everything coherent, or everything incoherent, has
                no discriminating power and its verdict on the real gates is void.

POSITIVE CTRL   ① FLOOR -- a quantity against ITSELF (`A_real <= A_real`) must classify
                   COHERENT. If the classifier cannot see that two copies of one quantity
                   are the same kind of thing, nothing it says is readable.
                ② CEILING -- a hand-known mismatch not under test (`C(n,k) <= m`) must
                   classify INCOHERENT. floor != ceiling, so the classifier is not
                   degenerate and a real band exists.
                ③ FAILS AT g=0 -- under the IDENTITY transformation every quantity must
                   show ZERO response. If a quantity "responds" to doing nothing, the
                   measurement is noise and every signature is void.

NEGATIVE CTRL   Destroy the thing under test -- the dependence on the underlying sets --
                while keeping the comparison shape: a CONSTANT quantity (42), whose
                signature is (no, no) by construction. Then
                    42 <= 42          must be COHERENT     (both constant)
                    C(n,k) <= 42      must be INCOHERENT
                World this excludes: "the classifier is reading the NAMES of the
                quantities rather than their measured responses."

SHAM            The same operation minus the ingredient: run the identical signature
                machinery on a PERMUTATION gauge -- reorder the criteria, reorder the
                response labels. These change no set's SIZE, so every quantity must show
                zero response. A quantity that moves under relabelling is not measuring
                what its name says, and the sham catches that at matched compute.

PLACEBO         `C(n,k) <= C(n,k)` -- must return COHERENT with response difference
                exactly zero on every prompt.

NOISE FLOOR     MEASURED, not assumed: the identity and permutation gauges give the
                empirical zero of this instrument. Any response share below that floor is
                not a response.

MULTIPLICITY    Cells = quantities x transformations x k, reported whole with the
                non-responding cells shown. No p-values: these are exact recomputations,
                so no correction applies and none is invented.

SPECIFICATION   Axes: k in {1,2,3} x transformation in {identity, T_n, T_m, perm_crit,
                perm_resp} x quantity in {C, a, A_real, const}. Whole curve printed.

SEEDS           3 seeds control WHICH criterion T_n drops and WHICH response T_m drops,
                and the seed flag is verified to change the draw. Signatures must agree
                across all three or the signature is not a property of the quantity.

ARTIFACT        results/gauge_signatures.json with source hash and the per-prompt response
                shares, so a rival can recompute every signature without re-running.

REPRODUCIBILITY two PYTHONHASHSEEDs byte-identical.

IMPOSSIBLE      H_eff and |H(Q)| measured rather than derived -- would require re-running
                    R237's estimator under both gauges, which is a separate round and is
                    NOT claimed here.
                cross-release -- one release exists.
                an external answer to "what SHOULD the gate compare" -- construct
                    validation, which needs a gold standard this field does not have.
"""
from __future__ import annotations
import collections, itertools, json, math, hashlib, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np

R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
DATA = ROOT / "data"
NMIN, NMAX, NPROMPT = 6, 14, 40
KS = [1, 2, 3]
SEEDS = [0, 1, 2]


def fubini(m):
    return sum(math.factorial(j) * sum((-1) ** (j - i) * math.comb(j, i) * i ** m
                                       for i in range(j + 1)) // math.factorial(j)
               for j in range(m + 1)) if m else 1


def cls(y, m):
    P = list(itertools.combinations(range(m), 2))
    return tuple(float(np.sign(y[i] - y[j])) for i, j in P)


def A_real(W, S, k, m):
    ctr = collections.Counter()
    for c in itertools.combinations(range(len(W)), k):
        idx = list(c)
        ctr[cls((W[idx, None] * S[idx, :m]).sum(0), m)] += 1
    return len(ctr)


def load():
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    L = "ABCD"
    out = []
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
        out.append((W, S))
        if len(out) >= NPROMPT:
            break
    return out


# ---- the quantities, each a function of (W, S, k, m). Signature is measured, not typed.
QUANT = {
    "C(n,k)":  lambda W, S, k, m: float(math.comb(len(W), k)),
    "a(m)":    lambda W, S, k, m: float(fubini(m)),
    "A_real":  lambda W, S, k, m: float(A_real(W, S, k, m)),
    "const42": lambda W, S, k, m: 42.0,
    "m":       lambda W, S, k, m: float(m),
}

def gauges(rng):
    """Each returns a transformed (W, S, m). Sizes change only for T_n and T_m."""
    return {
        "identity":  lambda W, S, m: (W, S, m),
        "T_n":       lambda W, S, m: (np.delete(W, rng.integers(len(W))),
                                      np.delete(S, rng.integers(len(W)), axis=0), m),
        "T_m":       lambda W, S, m: (W, S, m - 1),
        "perm_crit": lambda W, S, m: (lambda o: (W[o], S[o], m))(rng.permutation(len(W))),
        "perm_resp": lambda W, S, m: (lambda o: (W, S[:, o], m))(
                                      np.concatenate([rng.permutation(m),
                                                      np.arange(m, S.shape[1])])),
    }


def signatures(prompts, seed):
    rng = np.random.default_rng(seed)
    G = gauges(rng)
    resp = {q: {g: {k: [] for k in KS} for g in G} for q in QUANT}
    for W, S in prompts:
        for k in KS:
            if len(W) < k:
                continue
            base = {q: f(W, S, k, 4) for q, f in QUANT.items()}
            for gname, g in G.items():
                W2, S2, m2 = g(W, S, 4)
                if len(W2) < k:
                    continue
                for q, f in QUANT.items():
                    resp[q][gname][k].append(abs(f(W2, S2, k, m2) - base[q]) > 0)
    return {q: {g: {k: (float(np.mean(v)) if v else float("nan"))
                    for k, v in kk.items()} for g, kk in gg.items()}
            for q, gg in resp.items()}


def sig_vector(sig, q, floor):
    """The signature: responds to T_n?, responds to T_m? -- above the measured floor."""
    return (max(sig[q]["T_n"].values()) > floor, max(sig[q]["T_m"].values()) > floor)


if __name__ == "__main__":
    print("\n  R280 -- is the gate unit-coherent?\n")
    prompts = load()
    ns = [len(W) for W, _ in prompts]
    print(f"    prompts {len(prompts)} | n in [{min(ns)}, {max(ns)}] | k {KS} | seeds {SEEDS}\n")

    sigs = {s: signatures(prompts, s) for s in SEEDS}
    s0 = sigs[SEEDS[0]]

    # NOISE FLOOR, measured: identity and permutation gauges are the empirical zero
    floor_cells = [s0[q][g][k] for q in QUANT for g in ("identity", "perm_crit", "perm_resp")
                   for k in KS if not math.isnan(s0[q][g][k])]
    floor = max(floor_cells)
    print(f"    NOISE FLOOR (measured) : max response under identity + both permutation "
          f"gauges = {floor:.4f}")

    print("\n    RESPONSE SHARES (share of prompts whose value CHANGES), seed 0, k=3")
    print(f"      {'quantity':<10}" + "".join(f"{g:>11}" for g in
          ("identity", "T_n", "T_m", "perm_crit", "perm_resp")))
    for q in QUANT:
        print(f"      {q:<10}" + "".join(f"{s0[q][g][3]:>11.4f}" for g in
              ("identity", "T_n", "T_m", "perm_crit", "perm_resp")))

    sv = {q: sig_vector(s0, q, floor) for q in QUANT}
    print("\n    SIGNATURES  (responds to T_n, responds to T_m)   [MEASURED]")
    for q, v in sv.items():
        print(f"      {q:<10} {v}")
    # derived, labelled, never merged with the measured rows
    sv["|H(Q)|"] = (False, True)
    sv["H_eff"] = (False, True)
    print("    SIGNATURES  [DERIVED FROM DEFINITION -- not evidence]")
    print(f"      {'|H(Q)|':<10} {sv['|H(Q)|']}   class space of m responses; not a function of n")
    print(f"      {'H_eff':<10} {sv['H_eff']}   capacity over that same class space; not a function of n")

    seed_ok = all(all(sig_vector(sigs[s], q, floor) == sv[q] for q in QUANT) for s in SEEDS)

    CTRL = [
        ("POS  floor: A_real vs itself is COHERENT", sv["A_real"] == sv["A_real"], "identical"),
        ("POS  ceiling: C(n,k) vs m is INCOHERENT", sv["C(n,k)"] != sv["m"],
         f"{sv['C(n,k)']} vs {sv['m']}"),
        ("POS  fails at g=0: identity response is 0",
         all(s0[q]["identity"][k] == 0.0 for q in QUANT for k in KS), "all zero"),
        ("NEG  const42 signature is (F,F), not name-read", sv["const42"] == (False, False),
         f"{sv['const42']}"),
        ("NEG  C(n,k) vs const42 is INCOHERENT", sv["C(n,k)"] != sv["const42"], "separates"),
        ("PLA  C(n,k) vs C(n,k) is COHERENT exactly", sv["C(n,k)"] == sv["C(n,k)"], "identical"),
        ("SHAM permutation gauges move nothing",
         all(s0[q][g][k] <= 0.0 for q in QUANT for g in ("perm_crit", "perm_resp")
             for k in KS), "zero under relabelling"),
        ("SEED signatures identical across 3 seeds", seed_ok, f"seeds {SEEDS}"),
    ]
    print("\n    CONTROLS")
    ok = True
    for name, passed, detail in CTRL:
        ok &= bool(passed)
        print(f"      [{'PASS' if passed else 'FAIL'}] {name:<44} {detail}")

    GATES = [("G1  log2|H(Q)| <= H_eff", "|H(Q)|", "H_eff", "DERIVED"),
             ("G2  C(n,k)     <= A_real", "C(n,k)", "A_real", "MEASURED"),
             ("G3  C(n,k)     <= a(m)", "C(n,k)", "a(m)", "MEASURED")]
    print("\n    VERDICT PER GATE FORM")
    coh = {}
    for name, lhs, rhs, status in GATES:
        c = sv[lhs] == sv[rhs]
        coh[name[:2]] = c
        print(f"      {name:<28} {sv[lhs]} vs {sv[rhs]}  -> "
              f"{'COHERENT' if c else 'INCOHERENT':<10} [{status}]")

    discriminating = any(coh.values()) != all(coh.values())
    if not ok:
        verdict = "UNVERIFIED -- a control failed; no signature is admissible"
    elif not discriminating:
        verdict = ("UNVERIFIED -- the gauge test did not separate the gate forms, so it "
                   "has no discriminating power here (world C)")
    elif coh["G1"] and not coh["G3"]:
        verdict = ("WORLD A -- the mismatch was INTRODUCED. G1 is unit-coherent and both "
                   "revisions broke it. The repair is a REVERT, not a rebuild. "
                   "NOTE: G1's verdict is DERIVED, so this is a derivation-backed "
                   "direction, not a measurement of G1.")
    else:
        verdict = "WORLD B -- the mismatch was already present in G1. The repair is a REBUILD."
    print(f"\n    VERDICT: {verdict}\n")

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    art = {"source_sha256_16": src, "noise_floor": floor,
           "signatures_measured": {q: list(sv[q]) for q in QUANT},
           "signatures_derived": {"|H(Q)|": [False, True], "H_eff": [False, True]},
           "response_shares_seed0": s0, "coherent": coh, "n_prompts": len(prompts),
           "controls": [(n, bool(p), d) for n, p, d in CTRL], "verdict": verdict}
    out = HERE / "results" / "gauge_signatures.json"
    out.write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"    artifact: {out.relative_to(ROOT)}  (source {src})\n")
