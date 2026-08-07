"""R366 — my explanation for R365's survival is refuted by an artifact I committed two rounds ago.

R365's commit closed with a mechanism, offered as the honest reading of why one claim survived a
change of judge when every other clause in the definition did not:

    "it survived because it is a claim about a DIFFERENCE rather than about a level, and differences
     are what shrink transformations preserve. ... the definition should be restated in differences
     wherever possible."

That is a claim about my own record, it names a next ACTION (restate the definition), and it was
never checked. **R362's adjacent-k steps are differences of differences -- the same algebraic form as
R365's dose contrast -- and of the three that resolve at 2B, only ONE survives at 0.8B, while a
FOURTH appears there that 2B does not have.** The hypothesis is refuted by evidence I had already
committed.

This round does the check properly rather than acting on the sentence, and asks the sharper
question the refutation leaves: does ANYTHING in the committed record predict which claims survive
the judge axis?

⛔ ARITHMETIC TRAP, and it is the rival explanation. Under ANY scaling `x -> beta*x`, a TRUE ZERO
   maps to zero exactly, while a true nonzero maps to `beta*nonzero` and may fall below its MDE. So
   **a NULL claim is the easiest possible thing to have survive a shrink** -- its survival is forced
   by algebra and is not evidence of robustness at all. R365's dose contrast is a null. If the
   null/positive split sorts the record, R365's survival is much weaker than its commit message
   said, and that sentence needs correcting too.

ESTIMAND        Over every claim in the committed record that has been evaluated at BOTH judges:
                whether it SURVIVED, cross-classified by (a) LEVEL vs DIFFERENCE and (b) NULL vs
                POSITIVE. Then, for each classification, Fisher's exact test on the 2x2, with the
                design's own detectable odds ratio reported beside it.

IDENTIFICATION  ⚠ THIS IS THE BINDING CONSTRAINT AND IT IS STATED FIRST. The population is the
                claims this campaign has actually run at both judges. That is a SMALL, ENUMERATED
                set -- not a sample of anything -- so the question may simply be unidentified, and
                the round is built to report that rather than to manufacture a rule. Every claim is
                read from a committed artifact with the round that produced it named; nothing is
                classified from memory.

SCOPE           the CoVal campaign's own judge-tested claims · instruments Qwen3.5-2B-Base and
                Qwen3.5-0.8B-Base · this is an audit OF THE RECORD, not of the release.

WORLDS
  W-DIFFERENCE-SORTS  difference claims survive at a resolvably higher rate than level claims. My
                      R365 sentence stands and `restate the definition in differences` is supported.
  W-NULL-SORTS        null claims survive at a resolvably higher rate. Then survival is largely the
                      arithmetic of scaling a zero, R365's survival is nearly forced, and its commit
                      message overstated what the round earned.
  W-NEITHER-SORTS     neither reaches resolution on this population. Then I have no supported
                      explanation for which claims survive, the proposed restatement rests on
                      nothing, and the honest output is the enumerated table plus the power.

PREDICTION MATRIX
  W-DIFFERENCE-SORTS -> Fisher p < 0.05 on (form x survived), difference side higher
  W-NULL-SORTS       -> Fisher p < 0.05 on (nullness x survived), null side higher
  W-NEITHER-SORTS    -> both p >= 0.05
The three differ on two exact tests over one enumerated table.

PRE-REGISTERED KILL -- conditional, and the population check comes FIRST because a rule fitted to
seven points is the failure this round exists to avoid.
    if enumeration_ok and both_judges_ok:
        if p_form < 0.05 and p_null >= 0.05     -> W-DIFFERENCE-SORTS
        elif p_null < 0.05 and p_form >= 0.05   -> W-NULL-SORTS
        elif both < 0.05                         -> NAMED EXPLICITLY (confounded: report both)
        else                                     -> W-NEITHER-SORTS
    else: UNVERIFIED.

POSITIVE CTRL  a PLANTED table of the same size in which the split is perfect (every difference
               survives, every level dies) must reach p < 0.05. If a perfect separation at n=7
               cannot reach significance, the design cannot detect ANY rule and every p below is
               silence rather than a null. **This is the control that decides whether this round
               can say anything at all.**
g=0 CTRL       a planted table with the SAME marginals and no association must NOT reach p < 0.05.
PLACEBO        classifying every claim identically returns an undefined/1.0 test, never a pass.
NOISE FLOOR    the exact hypergeometric distribution underlying Fisher -- combinatorial, no draws.
MULTIPLICITY   2 classifications tested on 1 table; both reported whichever way they come out.
SEEDS          none needed; Fisher is exact and the enumeration is deterministic.
ARTIFACT       results/r366_what_survives.json with the source hash.

IMPOSSIBLE HERE
  a larger population -- would need more claims run at both judges. The 7 below are ALL of them.
  a third judge       -- NOT-ATTEMPTED-AND-NOT-CHEAP (R357).

EXIT
    0  controls hold and the classification is reported
    1  a control misbehaved -- UNVERIFIED
    2  the enumeration is empty -- never a silent pass
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}


def art(pat):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def fisher(a, b, c, d):
    """Exact two-sided Fisher on [[a,b],[c,d]]. Combinatorial; no sampling."""
    def C(n, k):
        return math.comb(n, k) if 0 <= k <= n else 0
    n = a + b + c + d
    r1, c1 = a + b, a + c
    denom = C(n, c1)
    if denom == 0:
        return float("nan")
    p_obs = C(r1, a) * C(n - r1, c1 - a) / denom
    tot = 0.0
    for x in range(0, min(r1, c1) + 1):
        p = C(r1, x) * C(n - r1, c1 - x) / denom
        if p <= p_obs + 1e-12:
            tot += p
    return min(1.0, tot)


def main() -> int:
    # ---- the enumeration: every claim run at BOTH judges, read from its artifact ----------------
    CLAIMS = []

    a = art("R301_*")
    if a:
        CLAIMS.append(dict(round="R301", claim="the definition admits a non-empty set",
                           form="level", null=False,
                           survived=len(a["admitted_08b"]) > 0,
                           evidence=f"2B {len(a['admitted_2b'])} arms, 0.8B {len(a['admitted_08b'])}"))
    a2_, a8_ = art("R355_*"), art("R358_*")
    if a2_ and a8_:
        ov = a8_["k_overlap"]["45"]
        CLAIMS.append(dict(round="R355/R358", claim="the closed region is not upward-closed",
                           form="level", null=False,
                           survived=bool(a8_["totals_08b"]["45"] > 0 and ov),
                           evidence=f"2B {a2_['totals']['45']} violations, 0.8B "
                                    f"{a8_['totals_08b']['45']}, k overlap {ov}"))
    a = art("R362_*")
    if a:
        r2, r8 = set(a["resolved"]["2B"]), set(a["resolved"]["0.8B"])
        for s in sorted(r2):
            CLAIMS.append(dict(round="R362", claim=f"the size-band step {s} resolves",
                               form="difference", null=False, survived=s in r8,
                               evidence=f"2B resolved; 0.8B {'resolved' if s in r8 else 'not'}"))
    a = art("R361_*")
    if a:
        CLAIMS.append(dict(round="R361", claim="no reference purges a label-user",
                           form="level", null=False,
                           survived=a["min_labels"]["0.8B"] == 4,
                           evidence=f"min label-users 2B {a['min_labels']['2B']}, "
                                    f"0.8B {a['min_labels']['0.8B']}"))
    a = art("R365_*")
    if a:
        d2, e2, _ = a["delta"]["2B"]; d8, e8, _ = a["delta"]["0.8B"]
        CLAIMS.append(dict(round="R364/R365", claim="the rubric channel carries nothing",
                           form="difference", null=True,
                           survived=abs(d8) <= e8,
                           evidence=f"2B {d2:+.4f}/{e2:.4f}, 0.8B {d8:+.4f}/{e8:.4f}"))
    if not CLAIMS:
        print("  UNRUNNABLE: no claim could be read from an artifact. Exit 2, never 0.")
        return 2

    print("R366 · does anything in the record predict which claims survive the judge axis?\n")
    print("  ⛔ MY R365 COMMIT SAID: `it survived because it is a claim about a DIFFERENCE ...")
    print("     the definition should be restated in differences wherever possible.` That names")
    print("     an ACTION and was never checked. It is checked here.\n")
    print(f"    {'round':>10}{'form':>12}{'null':>6}{'survived':>10}   claim / evidence")
    for c in CLAIMS:
        print(f"    {c['round']:>10}{c['form']:>12}{str(c['null']):>6}"
              f"{('YES' if c['survived'] else 'no'):>10}   {c['claim']}")
        print(f"    {'':>38}   {c['evidence']}")
    n = len(CLAIMS)
    print(f"\n  population: {n} claims — this is the WHOLE set the campaign has run at both judges,")
    print(f"  enumerated from artifacts, not sampled.\n")

    def table(key, val):
        a_ = sum(1 for c in CLAIMS if c[key] == val and c["survived"])
        b_ = sum(1 for c in CLAIMS if c[key] == val and not c["survived"])
        c_ = sum(1 for c in CLAIMS if c[key] != val and c["survived"])
        d_ = sum(1 for c in CLAIMS if c[key] != val and not c["survived"])
        return a_, b_, c_, d_

    fa, fb, fc, fd = table("form", "difference")
    na, nb, nc, nd = table("null", True)
    p_form, p_null = fisher(fa, fb, fc, fd), fisher(na, nb, nc, nd)
    print(f"    {'classification':>16}{'survived':>10}{'died':>7}{'  |  ':>5}"
          f"{'other survived':>16}{'other died':>12}{'Fisher p':>11}")
    print(f"    {'DIFFERENCE':>16}{fa:>10}{fb:>7}{'  |  ':>5}{fc:>16}{fd:>12}{p_form:>11.4f}")
    print(f"    {'NULL':>16}{na:>10}{nb:>7}{'  |  ':>5}{nc:>16}{nd:>12}{p_null:>11.4f}")

    # ---- controls -----------------------------------------------------------------------------
    half = n // 2
    p_perfect = fisher(half, 0, 0, n - half)
    p_g0 = fisher(max(half // 2, 1), half - max(half // 2, 1),
                  max((n - half) // 2, 1), (n - half) - max((n - half) // 2, 1))
    pos_ok = p_perfect < 0.05
    g0_ok = p_g0 >= 0.05
    print(f"\n  POSITIVE  a PERFECT split at this n ({half}/0 vs 0/{n-half}) reaches p = "
          f"{p_perfect:.4f}  {'PASS' if pos_ok else 'FAIL'}")
    print(f"            ⚠ if a perfect separation cannot reach 0.05, this design can detect NO")
    print(f"            rule and every p above is SILENCE, not a null.")
    print(f"  g=0       a table with the same marginals and no association: p = {p_g0:.4f}  "
          f"{'PASS' if g0_ok else 'FAIL'}")
    plac = math.isnan(fisher(n, 0, 0, 0)) or fisher(n, 0, 0, 0) >= 0.999
    print(f"  PLACEBO   every claim classified identically -> degenerate/1.0, never a pass  "
          f"{'PASS' if plac else 'FAIL'}")

    ctrl_ok = g0_ok and plac
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the table is silence.")
        v = "UNVERIFIED"
    elif not pos_ok:
        print(f"  W-UNDERPOWERED — a PERFECT separation at n={n} reaches only p={p_perfect:.4f}, so")
        print(f"  this population cannot resolve ANY sorting rule. Both p-values above are")
        print(f"  SILENCE rather than nulls, and no rule may be read from them in either direction.")
        print(f"  ⛔ MY R365 SENTENCE IS THEREFORE UNSUPPORTED — not refuted by this round, but")
        print(f"     resting on a population that cannot test it. `Restate the definition in")
        print(f"     differences` is withdrawn as an action until there is something to test it on.")
        v = "W_UNDERPOWERED"
    elif p_form < 0.05 and p_null >= 0.05:
        print(f"  W-DIFFERENCE-SORTS — difference claims survive at a resolvable rate "
              f"(p={p_form:.4f}) and nullness does not (p={p_null:.4f}). My R365 sentence stands.")
        v = "W_DIFFERENCE_SORTS"
    elif p_null < 0.05 and p_form >= 0.05:
        print(f"  W-NULL-SORTS — NULL claims survive (p={p_null:.4f}), form does not "
              f"(p={p_form:.4f}). Survival is largely the arithmetic of scaling a zero, so R365's")
        print(f"  survival was nearly FORCED and its commit message overstated the round.")
        v = "W_NULL_SORTS"
    elif p_form < 0.05 and p_null < 0.05:
        print(f"  CONFOUNDED — both classifications reach significance (form {p_form:.4f}, null")
        print(f"  {p_null:.4f}) on {n} claims where the two labels nearly coincide. Named rather")
        print(f"  than resolved: this population cannot separate them.")
        v = "W_CONFOUNDED"
    else:
        print(f"  W-NEITHER-SORTS — neither classification resolves (form {p_form:.4f}, null")
        print(f"  {p_null:.4f}) on a population a perfect split COULD have resolved ({p_perfect:.4f}).")
        print(f"  ⛔ So I have no supported explanation for which claims survive the judge axis,")
        print(f"     and `restate the definition in differences` rests on nothing. Withdrawn.")
        v = "W_NEITHER_SORTS"

    # the refutation that started the round, stated as its own fact
    r362 = [c for c in CLAIMS if c["round"] == "R362"]
    if r362:
        s = sum(1 for c in r362 if c["survived"])
        print(f"\n  ⚠ AND THE OBSERVATION THAT PROMPTED THIS, INDEPENDENT OF ANY TEST: R362's")
        print(f"    adjacent-k steps are differences of differences — the SAME algebraic form as")
        print(f"    R365's dose contrast — and {s} of {len(r362)} survive. Whatever explains R365,")
        print(f"    `it is a difference` does not, because differences do both here.")

    a_ = art("R365_*")
    if a_:
        print(f"\n  ⚠ AND THE RIVAL EXPLANATION IS A DERIVATION, not a finding: under ANY scaling")
        print(f"    x -> beta*x, a TRUE ZERO maps to zero exactly while a true nonzero maps to")
        print(f"    beta*nonzero and may fall below its MDE. So a NULL claim surviving a shrink is")
        print(f"    the cheapest possible survival. R365 IS a null. Its survival is therefore worth")
        print(f"    less than `the first claim to survive a change of judge` implies, whatever this")
        print(f"    round's test can or cannot resolve.")

    out = dict(stamp(str(SELF)), n_claims=n, claims=CLAIMS,
               table_form=dict(a=fa, b=fb, c=fc, d=fd, p=p_form),
               table_null=dict(a=na, b=nb, c=nc, d=nd, p=p_null),
               controls=dict(positive_p=p_perfect, positive_ok=pos_ok,
                             g0_p=p_g0, g0_ok=g0_ok, placebo=plac),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r366_what_survives.json"
    outp.write_text(json.dumps(out, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
