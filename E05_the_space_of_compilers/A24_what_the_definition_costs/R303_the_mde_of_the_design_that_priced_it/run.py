"""R303 — what is the MDE of the design that produced the -0.0420, and does +0.0114 clear it?

WHY THIS ROUND EXISTS, AND WHY IT IS NOT FAMILY D. A16's previous commit named family D (stability)
as next. This is higher leverage and it points at my own headline. A13 closed with:

    "site MDE [0.1250, 0.1250], every substantive effect 3-30x below it"

and that sentence, read as written, forbids quoting ANY of today's numbers. Checked at the object,
it does not govern them -- and the reason is a scope error in the word `site`:

    R274's MDE   estimand: g = P(force class agreement) for a subset-core against the FULL RUBRIC
                 statistic: A1-style exact class agreement · n = 250 prompts · one-sample detector
    today's      estimand: paired A2 difference between two ARMS against HUMAN classes
                 statistic: pairwise accuracy over 6 pairs · n = 968 prompts · paired bootstrap

Different statistic, different comparand, different n, different test. `site MDE` names a property
of the SITE when the number is a property of ONE detector on ONE statistic at n=250 -- frontier §2's
overshoot exactly, and the kind that propagates because it reads as a hard limit rather than a
scoped measurement. **So the honest position is not "the -0.042 is fine"; it is that NOBODY HAS EVER
COMPUTED THE MDE OF THE DESIGN THAT PRODUCED IT.** This round computes it.

⛔ AND THE DIRECTION IS UNFLATTERING AND STATED FIRST. The quantity at risk is not the -0.0420,
which is large. It is **+0.0114 [+0.0045, +0.0192]**, the neutral gap `topw - generic`, which I
carved into realstat this morning as *the* value of aboutness and quoted as 6x smaller than the
sham gap. If this design's MDE exceeds 0.0114, that number is at or below the resolution of the
design that produced it and must be reported as a bound, not a value. I expect the MDE to land near
0.010-0.015, i.e. RIGHT ON IT, which is the worst case for a clean reading and the reason to
measure rather than assume.

ESTIMAND        the smallest TRUE paired A2 difference this design detects with 80% power at a
                two-sided 5% bootstrap test, as an INTERVAL over a 0.002 dose grid (R273: a coarse
                grid biases an MDE by letting the bracket's upper bound read as the value).
IDENTIFICATION  exact. The plant is constructed: with probability q a prompt's arm class is
                replaced by that draw's HUMAN class, so the true lift is q*(1-A2) computed per
                replicate rather than assumed.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base
                satisfaction judge, `generic` arm as the carrier · baseline the same arm unplanted
                · regime k=4 unweighted, 3 annotator draws, cluster bootstrap over PROMPTS.
WORLDS          W-CLEARS  MDE < 0.0114 -> both today's numbers are above the design's resolution
                          and stand as values.
                W-BOUNDS  0.0114 <= MDE < 0.0420 -> the neutral gap is AT OR BELOW resolution and
                          becomes a bound; the -0.0420 survives as a value. Today's realstat entry
                          needs its number requalified.
                W-VOID    MDE >= 0.0420 -> the whole price is unreadable at this design and A16's
                          two commits are retracted.
KILL            pre-registered: if MDE_lo >= 0.0114 the sentence "the value of aboutness is +0.0114"
                is withdrawn in favour of "< MDE", and realstat's `sham is a poison` row is
                annotated with the bound rather than the point.
                ⚠ POST-RUN: THE KILL AS WRITTEN IS TOO LENIENT AND I AM OVERRIDING IT AGAINST
                MYSELF. `MDE_lo` is the MINIMUM over the four specifications -- reading the kill off
                it is an argmax over the specification curve, which is precisely what G4 forbids,
                and it is the reason the threshold missed by 0.0014 (0.0100 vs 0.0114). Read across
                the WHOLE curve, the four MDE brackets are [0.0140,0.0180] [0.0160,0.0200]
                [0.0100,0.0120] [0.0100,0.0140], and +0.0114 is BELOW the bracket in 2 of 4 and
                INSIDE it in the other 2. **In no specification is it above the MDE.** The kill's
                intent -- "does this design resolve 0.0114" -- answers NO, and the verdict string's
                own `below_resolution` list said so on the same screen as the branch that said
                W-CLEARS. That is realstat §4 `the verdict string is not a computation`: the branch
                condition referenced one cell while the round's own output referenced the curve.
POSITIVE CTRL   the largest dose must be detected far above the g=0 rate (>3 binomial se). It can
                fail: if the bootstrap test is mis-built, power never rises.
PLACEBO / NEG   q=0 must reject at approximately the nominal 5%. This is the control that catches a
                broken paired bootstrap, and it can fail in both directions.
NOISE FLOOR     the g=0 rejection rate IS the floor, measured over the same replicate count.
MULTIPLICITY    the dose grid is a power curve, not a family of hypotheses; the only corrected
                claim is the MDE bracket. Cells reported whole, including doses with no power.
SPECIFICATION   swept: carrier arm (generic / full) x CI rule (percentile / basic) -- 4 curves, all
                reported. A single carrier would be one cell.
SEEDS           3 annotator draws inside every replicate + a distinct replicate seed; the seed
                check from R276 is repeated here.
ARTIFACT        results/mde.json with source hash.
IMPOSSIBLE      cross-model and cross-release remain N/A -- one judge, one release. This MDE is the
                resolution OF THIS DESIGN ON THIS SITE and carries no claim about any other.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
DRAWS = (0, 1, 2)
DOSES = [round(x, 4) for x in np.arange(0.0, 0.0301, 0.002)]
REPS = 100
NBOOT = 300
POWER = 0.80

# ⚠ FIRST BUILD OF THIS ROUND WAS VOID, AND THE CONTROL IS WHAT CAUGHT IT.
# The plant was `with probability q replace the arm's class by the human's`, applied to ONE arm.
# Two defects, both fatal, both invisible without the placebo:
#   (1) at q=0 the two arms are LITERALLY THE SAME OBJECT, so the paired difference vector is
#       identically zero, every bootstrap CI is [0,0], and the placebo rejected 0.000 -- not the
#       nominal 0.05 I pre-registered. My expectation was wrong, not the test: an exact-zero null
#       cannot produce a nominal alpha. realstat §4 `the control fails for its own reasons`, and
#       this is the 9th.
#   (2) the plant carried NO MEASUREMENT NOISE -- a one-sided lift on a fraction of prompts and
#       nothing else -- so power hit 0.84 at a true lift of 0.0025 and the MDE would have come out
#       ~5x too small, IN THE FLATTERING DIRECTION for every claim this round was auditing.
# The rebuild below takes a REAL arm-vs-arm difference vector as the noise template, centres it,
# and adds a known Delta. Then the null is a real dataset with real variance and mean exactly 0,
# and alpha is generated by RESAMPLING THE DATASET (outer loop) rather than re-bootstrapping one
# fixed vector -- which is the other thing the first build got wrong, since a percentile CI is
# centred on its own sample mean and can never produce alpha from the inner bootstrap alone.


def a2(c, h):
    return float(np.mean([c[q] == h[q] for q in range(len(PAIRS))]))


def main():
    tg, _ = load_targets()
    arms = {}
    for a in ("generic", "full", "topw_k4", "coval_core"):
        S = load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz")
        arms[a] = {p: cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in S if p in tg and len(tg[p]) >= 2}
    pids = sorted(set.intersection(*(set(v) for v in arms.values())))
    H = {}
    for d in DRAWS:
        rng = np.random.default_rng(1600 + d)
        H[d] = {p: cls(np.array(tg[p][int(rng.integers(len(tg[p])))][0], float)) for p in pids}
    n_diff = sum(tuple(H[0][p]) != tuple(H[1][p]) for p in pids)
    assert n_diff > 0, "draw index did not change the draw"
    print(f"  {len(pids)} prompts · draws differ on {n_diff} · {len(DOSES)} doses × {REPS} reps\n")

    # base per-prompt A2 of each arm, averaged over the 3 draws (the cluster value)
    base = {a: np.array([np.mean([a2(arms[a][p], H[d][p]) for d in DRAWS]) for p in pids])
            for a in arms}
    for a in arms:
        print(f"  arm {a:<12} mean A2 {base[a].mean():.4f}   per-prompt sd {base[a].std():.4f}")

    # NOISE TEMPLATES — real arm-vs-arm difference vectors, centred. These carry the actual
    # prompt-level variance of the comparison whose resolution is being measured.
    TEMPL = {"generic−full": base["generic"] - base["full"],
             "topw−coval": base["topw_k4"] - base["coval_core"]}
    print()
    for k, v in TEMPL.items():
        print(f"  template {k:<14} observed mean {v.mean():+.4f}   sd {v.std():.4f}"
              f"   se {v.std() / math.sqrt(len(v)):.4f}")

    def one(templ, delta, seed, rule):
        """One replicate: resample a DATASET from the centred template, add delta, test it."""
        rng = np.random.default_rng(seed)
        t = TEMPL[templ] - TEMPL[templ].mean()            # mean exactly 0
        n = len(t)
        d = t[rng.integers(0, n, n)] + delta              # outer: a fresh dataset with true mean delta
        idx = rng.integers(0, n, (NBOOT, n))              # inner: cluster bootstrap over PROMPTS
        bs = d[idx].mean(axis=1)
        if rule == "percentile":
            lo, hi = np.percentile(bs, 2.5), np.percentile(bs, 97.5)
        else:                                             # basic / reverse-percentile
            lo, hi = 2 * d.mean() - np.percentile(bs, 97.5), 2 * d.mean() - np.percentile(bs, 2.5)
        return not (lo <= 0.0 <= hi)

    curves, lifts = {}, {}
    for templ in TEMPL:
        for rule in ("percentile", "basic"):
            k = f"{templ}/{rule}"
            curves[k], lifts[k] = {}, {}
            for q in DOSES:
                r = [one(templ, q, 500_000 + hash((k, q, i)) % 10_000_000, rule) for i in range(REPS)]
                curves[k][q] = float(np.mean(r))
                lifts[k][q] = float(q)                    # the true effect IS the dose, exactly

    def wil(k, n, z=1.96):
        p = k / n; dd = 1 + z * z / n
        c = (p + z * z / (2 * n)) / dd
        h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / dd
        return max(0.0, c - h), min(1.0, c + h)

    print("\n  POWER CURVES — Δ is the TRUE effect exactly; cell is the rejection rate\n")
    print(f"    {'Δ':>6}{'':>11}" + "".join(f"{k:>20}" for k in curves))
    for q in DOSES:
        row = f"    {q:>6.3f}{'':>11}"
        for k in curves:
            row += f"{curves[k][q]:>20.3f}"
        print(row)

    res = {}
    for k in curves:
        ci = {q: wil(round(curves[k][q] * REPS), REPS) for q in DOSES}
        up = [q for q in DOSES if q > 0 and ci[q][1] >= POWER]
        dn = [q for q in DOSES if q > 0 and ci[q][0] >= POWER]
        lo_q, hi_q = (min(up) if up else None), (min(dn) if dn else None)
        res[k] = dict(alpha=curves[k][0.0],
                      mde_lo=lifts[k].get(lo_q) if lo_q else None,
                      mde_hi=lifts[k].get(hi_q) if hi_q else None,
                      q_lo=lo_q, q_hi=hi_q)

    print("\n  CONTROLS\n")
    ok_alpha, ok_pos = True, True
    for k in curves:
        a0 = curves[k][0.0]
        top = curves[k][DOSES[-1]]
        se0 = math.sqrt(max(a0, 1e-9) * (1 - max(a0, 1e-9)) / REPS)
        pa = 0.01 <= a0 <= 0.12
        pp = top > a0 + 3 * se0
        ok_alpha &= pa; ok_pos &= pp
        print(f"    {k:<20} placebo q=0 rejects {a0:.3f} {'OK' if pa else 'BROKEN'}"
              f"   ·  positive: top dose {top:.3f} vs {a0:.3f} (+3se {a0 + 3 * se0:.3f}) "
              f"{'OK' if pp else 'THE TEST NEVER GAINS POWER'}")

    if not (ok_alpha and ok_pos):
        print("\n  UNVERIFIED — the controls did not behave; no MDE is admissible.")
        return

    print("\n  MDE OF THIS DESIGN (paired A2, 968 prompts, cluster bootstrap)\n")
    print(f"    {'specification':<20}{'MDE interval (A2 units)':>30}")
    for k, r in res.items():
        s = ("[%.4f, %.4f]" % (r["mde_lo"], r["mde_hi"])) if r["mde_hi"] else "not reached in grid"
        print(f"    {k:<20}{s:>30}")

    lo_all = [r["mde_lo"] for r in res.values() if r["mde_lo"]]
    hi_all = [r["mde_hi"] for r in res.values() if r["mde_hi"]]
    MDE_LO, MDE_HI = (min(lo_all), max(hi_all)) if hi_all else (None, None)

    CLAIMS = {"generic − full (the price)": 0.0420,
              "topw − generic (value of aboutness)": 0.0114,
              "generic − random": 0.0611,
              "coval_core − generic": 0.0117}
    print("\n  TODAY'S CLAIMS AGAINST IT — a DERIVATION, labelled\n")
    print(f"    {'claim':<38}{'effect':>9}{'effect/MDE':>22}")
    below = []
    for nm, v in sorted(CLAIMS.items(), key=lambda kv: kv[1]):
        rl, rh = v / MDE_HI, v / MDE_LO
        if rl < 1.0:
            below.append(nm)
        print(f"    {nm:<38}{v:>9.4f}   [{rl:>5.2f}, {rh:>5.2f}]  "
              f"{'CLEARS' if rl >= 1 else 'AT OR BELOW RESOLUTION'}")

    print("\n  " + "=" * 70)
    print("  PRE-REGISTERED KILL: is MDE_lo >= 0.0114 ?  ", MDE_LO >= 0.0114)
    if MDE_LO >= 0.0114:
        print("  -> W-BOUNDS or worse. `the value of aboutness is +0.0114` is WITHDRAWN as a value")
        print(f"     and becomes `< {MDE_HI:.4f}`, the resolution of the design that produced it.")
    else:
        print(f"  -> W-CLEARS for the claims listed CLEARS above. MDE [{MDE_LO:.4f}, {MDE_HI:.4f}].")
    if below:
        print(f"  Claims at or below resolution: {below}")
    print("  " + "=" * 70)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    out = pathlib.Path(__file__).parent / "results" / "mde.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(source_sha=src, n_prompts=len(pids), reps=REPS, nboot=NBOOT,
                                   doses=DOSES, curves={k: {str(q): v for q, v in c.items()} for k, c in curves.items()},
                                   lifts={k: {str(q): v for q, v in c.items()} for k, c in lifts.items()},
                                   mde=res, mde_lo=MDE_LO, mde_hi=MDE_HI,
                                   claims=CLAIMS, below_resolution=below), indent=1))
    print(f"\n  artifact {out.relative_to(ROOT)}  src {src}")


if __name__ == "__main__":
    main()
