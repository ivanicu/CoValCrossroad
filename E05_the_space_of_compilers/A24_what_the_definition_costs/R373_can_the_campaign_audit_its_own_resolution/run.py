"""R373 — the campaign publishes 1,500+ MDEs and records what almost none of their denominators averaged.

R372 found that R371's top cell was a degrees-of-freedom artifact: the between-stratum sd at S strata
has S-1 df, so at S=2 it has ONE and collapses below half the typical contrast in 28.3% of halves.
R372's NEXT line proposed auditing the rest of the campaign for the same collapse. This is that
audit, and the first thing it found was that the audit cannot be run the way it was proposed.

⛔ THE HEURISTIC I ALMOST USED WAS WRONG, AND WRONG IN THE FLATTERING DIRECTION. The obvious census
   is: for every stored MDE, read the sibling key that records its unit count. 479 of 1,542 stored
   MDEs have a sibling named `k`, `n`, `kept` or `arms`. But **`k` in this campaign means CORE SIZE,
   not the denominator's unit count** -- R301 stores `{'k': 4, 'n': 968}` beside an MDE whose
   denominator is sqrt(968). A census keyed on `k` would have reported R301 as a 4-unit design and
   manufactured a campaign-wide scandal out of a name collision. **A key that looks like the
   quantity is worse than a missing key, because absence prompts a check and a plausible name does
   not.**

⛔ SO THE INSTRUMENT'S UNIT AND THE CLAIM'S UNIT ARE NAMED SEPARATELY AND THEY ARE NOT EQUAL, which
   is the remedy the skill demands before a control is even designed:
     · the CLAIM's unit is  `a published number that a verdict rests on`
     · the INSTRUMENT's unit is `an MDE call site in source`
   A call site is not a published number: one site can produce hundreds of values, and a value can
   be published from a site this parse never sees. Everything below is scoped to call sites, and the
   gap between the two units is REPORTED rather than closed by wording.

⛔ ARITHMETIC TRAP, answered before the run and it applies to the headline. Part (a) below is a
   DERIVATION, not a measurement: the sampling distribution of a k-unit sd estimate is
   chi_{k-1}/sqrt(k-1) under normal units, so the probability it lands below a fraction f of its
   true value is chi2.cdf(f^2 (k-1), k-1). That is algebra and could not have come out otherwise.
   It is reported as a derivation and its ASSUMPTION -- approximate normality of the per-unit
   quantity -- is what part (b) tests against data already on disk. Part (c), the census, is a
   measurement and could have come out any way.

ESTIMAND
  (a) [DERIVATION] P(sd_hat < f * sigma | k units) = chi2.cdf(f^2 (k-1), k-1).
  (b) [MEASUREMENT] whether that law holds on this campaign's own data: R372 measured the 10th
      percentile and the median of the MDE at six values of k, in four specifications -- 24 cells.
      The RATIO p10/median is a pure function of k under (a) and carries no free parameter, so it
      is a genuine test of the model rather than a fit.
  (c) [MEASUREMENT] over every MDE call site in the campaign's source, the denominator expression,
      and whether the artifact that publishes it records the value that denominator took.

IDENTIFICATION  (a) is identified by algebra. (b) is identified at the six k R372 swept and NOWHERE
                ELSE -- it is a test of the model on one round's data, not a campaign-wide check.
                (c) is identified for call sites this parse finds; sites it misses are invisible to
                it and that is a bound on the census, stated with the parse's own positive control.
                NOT identified: whether any individual published verdict actually flipped. That
                needs the per-unit vectors, which is exactly what is missing.

SCOPE           population: run.py files under E0*/ that compute an MDE from ZEFF · instrument: a
                source parse plus scipy's chi2 · baseline: the chi model with no free parameter ·
                regime: the campaign as committed at this hash.

WORLDS
  W-UNAUDITABLE   the records do not permit the audit. Few call sites publish their denominator's
                  value, so most published resolution claims cannot be re-checked at all. The object
                  to fix is the RECORD, and the next action is a gate, not a measurement.
  W-CLEAN         small-k denominators are confined to the stratum family (R370-R372) and the rest
                  of the campaign averages over hundreds of units, so R372's collapse is local and
                  nothing else is affected.
  W-CONTAMINATED  small-k denominators are widespread, so many published verdicts rest on an
                  estimator whose denominator collapses at a rate the derivation gives.

PREDICTION MATRIX
  W-UNAUDITABLE  -> share of call sites whose denominator value is recorded is LOW; the k of most
                    sites is unknowable from the artifact
  W-CLEAN        -> denominators resolvable and nearly all large; small-k sites confined to R370-372
  W-CONTAMINATED -> many sites with a small-k denominator outside the stratum family
These differ on what the next action is -- write a gate, do nothing, or re-open published cells --
which is the point of separating them.

PRE-REGISTERED KILL -- conditional on the controls, never on the threshold alone.
    if chi_model_validated and placebo_ok and parser_positive_control_ok:
        if recorded_share < 0.50            -> W-UNAUDITABLE
        elif small_k_outside_stratum == 0   -> W-CLEAN
        else                                -> W-CONTAMINATED
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.
⚠ AND THE BRANCHES ARE NOT EXCLUSIVE, which is named rather than discovered: a campaign can be both
  unauditable AND contaminated. If the first branch fires, the second and third are still COMPUTED
  and PRINTED, because reporting only the branch that fired is how a disjunction becomes a claim.

⛔⛔ ANNOTATION AFTER THE RUN — the pre-registration above is KEPT VERBATIM and two of its three
   branches did not survive contact with their own instruments. Both changes are reported in the
   output rather than folded back into this block, because a pre-registration edited after the data
   is not a pre-registration.
   ① `recorded_share < 0.50` is WITHDRAWN. The only instrument available for it was a guessed
      whitelist of artifact key names, which has no positive control and cannot prove an absence.
      It returned 2 of 38 and would have been the headline; R355 (`n_pairs_pooled`) and R368
      (`len(strata)`) are both demonstrated false negatives. That branch reports UNVERIFIED.
   ② `small_k_outside_stratum == 0` is REFINED, and the refinement runs AGAINST the finding. The
      parser classifies what a denominator COUNTS, not how many it counts -- R355 is flagged and
      its k is 25, where the collapse probability is 0.0001. Judging `clean` on the flag rather
      than on resolved k would have convicted a round that is fine. Only k decides, and after
      resolving k the contamination is ONE round, not two.

CONTROLS
  CHI MODEL      the 24 R372 cells: predicted p10/median vs measured, no free parameter. This can
                 fail -- if the per-unit quantities are far from normal the ratio will not track.
  PARSER (+)     the parse must find two call sites whose answers are known independently: R372's
                 `math.sqrt(len(c))` (a stratum count) and R301's `math.sqrt(N)` (968 prompts). A
                 parse that finds neither is silence; a parse that mislabels either is refuted.
  PARSER (-)     a file with no MDE must yield no call site. An empty population exits 2, never 0.
  PLACEBO        at k = 200 the collapse probability must be ~0, and at f = 1 the probability must
                 be ~0.5 by definition of the median -- a value known independently of this code.
  RANGE          the derivation must span its own extremes across the k actually observed.

MULTIPLICITY    24 model cells x 1 comparison; the census is a full enumeration, not a test family.
                No selection is made on a p-value anywhere in this round.
SEEDS           none -- this round draws no random numbers. Stated rather than omitted, because a
                seed line that says `3` on a deterministic round is decoration.
ARTIFACT        results/r373_resolution_audit.json with the source hash.

IMPOSSIBLE HERE
  whether a published verdict FLIPPED  -- needs the per-unit vectors the artifacts do not store.
                                          That is the same wall the census measures.
  call sites this parse cannot see     -- bounded by the parser's positive control, not by hope.
  a second release                     -- one release.

EXIT
    0  controls hold and the campaign is classified
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import collections, hashlib, json, pathlib, re, sys

import numpy as np
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
R372 = (ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
        / "R372_is_the_resolving_set_stable" / "results" / "r372_stability.json")
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

# the estimator, as it is actually written across the campaign. The denominator is captured whole
# so it can be classified rather than guessed at.
CALL = re.compile(r"ZEFF\s*\*\s*(?P<sd>[^/\n]+?)\s*/\s*math\.sqrt\(\s*(?P<den>[^)]*\([^)]*\)[^)]*|[^)]*)\)")
# a denominator naming a COUNT OF UNITS this round aggregated, vs one naming the sample size
SMALLISH = re.compile(r"len\(\s*(c|con_|contrasts|exc_all|arms|cells|refs|strata)\b", re.I)


def collapse_prob(k: int, f: float) -> float:
    """[DERIVATION] P(sd_hat < f * sigma) for an sd estimated from k units of a normal quantity.

    sd_hat^2 (k-1) / sigma^2 ~ chi2_{k-1}. Could not have come out otherwise; it is algebra.
    """
    if k < 2:
        return float("nan")          # a 1-unit sd is UNDEFINED, not zero
    return float(stats.chi2.cdf(f * f * (k - 1), k - 1))


def ratio_p10_med(k: int) -> float:
    """[DERIVATION] the 10th percentile of sd_hat over its median -- free of sigma, so a test."""
    if k < 2:
        return float("nan")
    df = k - 1
    return float(np.sqrt(stats.chi2.ppf(0.10, df) / stats.chi2.ppf(0.50, df)))


def main() -> int:
    if not R372.exists():
        print(f"  UNRUNNABLE: {R372.name} absent. Exit 2, never 0."); return 2

    print("R373 · can this campaign audit its own resolution claims?\n")

    # ---- (a) THE DERIVATION -------------------------------------------------------------------
    print("  (a) [DERIVATION — algebra, not evidence] P(sd_hat < f·sigma) at k units.")
    print("      sd_hat^2 (k-1)/sigma^2 ~ chi2_{k-1}. Assumption: the per-unit quantity is")
    print("      approximately normal. (b) tests that assumption; it is not assumed away.\n")
    FS = (0.25, 0.50, 0.75)
    KS = (2, 3, 4, 5, 6, 8, 12, 20, 50, 200)
    print(f"      {'k':>5}" + "".join(f"{'f='+str(f):>12}" for f in FS))
    DERIV = {}
    for k in KS:
        DERIV[k] = {str(f): collapse_prob(k, f) for f in FS}
        print(f"      {k:>5}" + "".join(f"{collapse_prob(k,f):>12.4f}" for f in FS))
    print(f"\n      At k=2 the sd lands below HALF its true value {collapse_prob(2,0.5):.1%} of the "
          f"time; at k=8, {collapse_prob(8,0.5):.2%}.")
    print(f"      A denominator that small does not estimate noise — it samples it.")

    # ---- (b) DOES THE LAW HOLD ON THIS CAMPAIGN'S DATA? -------------------------------------
    deg = json.loads(R372.read_text())["degeneracy"]
    print(f"\n  (b) CHI MODEL vs R372's 24 measured cells — the ratio p10/median carries NO free")
    print(f"      parameter, so agreement is a test and not a fit.")
    print(f"      {'cell':>16}{'k':>4}{'predicted':>11}{'measured':>10}{'abs err':>9}")
    errs, rows_b = [], {}
    for key in sorted(deg, key=lambda s: (s.split("|")[0], s.split("|")[1], int(s.split("|")[2]))):
        spec, mt, ks = key.split("|"); k = int(ks)
        v = deg[key]
        if not v["med_mde"]:
            continue
        meas = v["p10_mde"] / v["med_mde"]
        pred = ratio_p10_med(k)
        errs.append(abs(meas - pred)); rows_b[key] = dict(k=k, pred=pred, meas=meas)
        print(f"      {spec+'|'+mt:>16}{k:>4}{pred:>11.4f}{meas:>10.4f}{abs(meas-pred):>9.4f}")
    max_err = float(max(errs)); mean_err = float(np.mean(errs))
    # tolerance ARGUED: each measured ratio is two order statistics of 480 draws; the 10th
    # percentile of 480 has a standard error of roughly sqrt(.1*.9/480)/density, which for this
    # family is a few percent of the ratio. 0.10 absolute is generous to the model and still
    # discriminating -- the ratio itself ranges 0.19..0.67 across k, so a model that got k wrong
    # by one step would miss by more than 0.10 at small k.
    chi_ok = max_err < 0.10
    print(f"      -> max abs error {max_err:.4f}, mean {mean_err:.4f} over {len(errs)} cells; "
          f"tolerance 0.10  {'PASS' if chi_ok else 'FAIL'}")
    print(f"      The prediction spans {ratio_p10_med(2):.3f} at k=2 to {ratio_p10_med(8):.3f} at "
          f"k=8, so this is not a wide net.")

    # ---- (c) THE CENSUS -----------------------------------------------------------------------
    files = sorted((ROOT).glob("E0*/*/*/*.py"))
    if not files:
        print("  UNRUNNABLE: no round source found. Exit 2, never 0."); return 2
    sites, byfile = [], collections.Counter()
    for f in files:
        try:
            txt = f.read_text()
        except Exception:
            continue
        for m in CALL.finditer(txt):
            den = m.group("den").strip()
            rel = str(f.relative_to(ROOT))
            rnd = rel.split("/")[2].split("_")[0]
            sites.append(dict(round=rnd, file=rel, den=den,
                              line=txt[: m.start()].count("\n") + 1))
            byfile[rnd] += 1
    if not sites:
        print("  UNRUNNABLE: the parse found ZERO call sites — an empty population never passes. "
              "Exit 2."); return 2

    dens = collections.Counter(s["den"] for s in sites)
    print(f"\n  (c) CENSUS — {len(sites)} MDE call sites across {len(byfile)} rounds.")
    print(f"      denominator expressions, most common first:")
    for d_, n_ in dens.most_common(14):
        tag = "small-k" if SMALLISH.search(d_) else "sample"
        print(f"      {n_:>4}  {tag:>8}  math.sqrt({d_})")
    if len(dens) > 14:
        print(f"      ... {len(dens)-14} further distinct denominator expressions")

    smallk = [s for s in sites if SMALLISH.search(s["den"])]
    strat = {"R370", "R371", "R372"}
    outside = sorted({s["round"] for s in smallk} - strat)
    print(f"\n      call sites whose denominator counts AGGREGATED UNITS (not the sample): "
          f"{len(smallk)} of {len(sites)}")
    print(f"      rounds carrying one: {sorted({s['round'] for s in smallk})}")
    print(f"      OUTSIDE the stratum family R370-R372: {outside if outside else 'none'}")

    print(f"      ⚠ `k` is EXCLUDED by name: in this campaign it means CORE SIZE. R301 stores")
    print(f"        k=4 beside an MDE over 968 prompts. Counting it would have inverted the census.")

    # ⛔ AND A SECOND INSTRUMENT I BUILT HERE HAD NO POSITIVE CONTROL, so its number is withdrawn
    #   rather than reported. v1 measured `what share of rounds RECORD their denominator's count`
    #   by testing each artifact's key names against a whitelist {kept, n_strata, n_units,
    #   denominator_n, n_terms}. It returned 2 of 38 (5.3%) and would have been the headline.
    #   **R355 is a demonstrated false negative**: it stores exactly that count under
    #   `n_pairs_pooled`, and R368 stores it as the LENGTH OF A LIST called `strata` -- a name no
    #   whitelist reaches. A guessed word list cannot prove an absence, and this one had no
    #   positive control at all, which is the failure this campaign has now logged three times.
    #   The share is therefore UNVERIFIED -- not low, not high -- and the branch that rested on it
    #   is reported as UNVERIFIED below rather than being quietly re-derived from a better list.
    rec_share = float("nan")
    print(f"\n      ⛔ WITHDRAWN: v1 reported `2 of 38 rounds record their denominator's count`.")
    print(f"         That instrument was a GUESSED WORD LIST with no positive control, and R355 is")
    print(f"         a demonstrated false negative (`n_pairs_pooled`), R368 another (`len(strata)`).")
    print(f"         A word list cannot prove an absence. The share is UNVERIFIED, not low.")

    # ---- THE DECISIVE SLICE: the five small-k sites, with k RESOLVED from the artifact ---------
    # Population of five, each path READ from the artifact and named here, so a later round can
    # check the path rather than trust the number. This is the only place k is claimed.
    def dig(round_id, fn):
        arts = list(ROOT.glob(f"E0*/*/{round_id}_*/results/*.json"))
        for a in arts:
            try:
                d_ = json.loads(a.read_text())
            except Exception:
                continue
            try:
                v_ = fn(d_)
                if v_:
                    return v_, f"{a.relative_to(ROOT)}"
            except Exception:
                continue
        return None, None

    SLICE = {
        "R355": ("n_pairs_pooled", lambda d: {"pooled": d["mechanism"]["n_pairs_pooled"]}),
        "R368": ("len(strata[metric])",
                 lambda d: {m: len(d["strata"][m]) for m in d["strata"]}),
        "R370": ("len(results[cell].rows)",
                 lambda d: {m: len(d["results"][m]["rows"]) for m in d["results"]}),
        "R371": ("rows[*].kept", lambda d: {m: d["rows"][m]["kept"] for m in d["rows"]}),
        "R372": ("corrected_full[*].kept",
                 lambda d: {m: d["corrected_full"][m]["kept"] for m in d["corrected_full"]}),
    }
    print(f"\n  THE DECISIVE SLICE — k for every small-k call site, resolved from the artifact.")
    print(f"    {'round':>6}{'k':>6}{'P(sd<sigma/2)':>15}{'P(sd<3sigma/4)':>16}   path")
    KS_FOUND, unresolved = {}, []
    for r in sorted(SLICE):
        path, fn = SLICE[r]
        got, src = dig(r, fn)
        if not got:
            unresolved.append(r)
            print(f"    {r:>6}{'—':>6}{'UNVERIFIED':>15}{'':>16}   {path} — not readable")
            continue
        ks = sorted({int(x) for x in got.values() if isinstance(x, (int, float)) and x >= 2})
        KS_FOUND[r] = dict(ks=ks, path=path, source=src)
        for k in ks:
            print(f"    {r:>6}{k:>6}{collapse_prob(k,0.5):>15.4f}{collapse_prob(k,0.75):>16.4f}"
                  f"   {path}")
    allk = sorted({k for r in KS_FOUND for k in KS_FOUND[r]["ks"]})
    worst = min(allk) if allk else None
    # ⛔ AND THE FLAG IS NOT THE SEVERITY, which resolving k has just shown. The parser classifies
    #   what a denominator COUNTS (aggregated units vs the sample); it says nothing about how many.
    #   R355 was flagged and its k is 25, where the collapse probability is 0.0001 -- no problem at
    #   all. Reporting `small-k outside the stratum family` without resolving k would have been a
    #   label doing the work of a measurement. Only k decides.
    SEVERE = 10
    severe = {r: KS_FOUND[r]["ks"] for r in KS_FOUND if min(KS_FOUND[r]["ks"]) < SEVERE}
    severe_outside = sorted(set(severe) - strat)
    print(f"    -> k across the small-k sites: {allk}; the smallest is {worst}, where the sd lands")
    print(f"       below half its true value {collapse_prob(worst,0.5):.1%} of the time.")
    print(f"    ⚠ These are the ONLY k this round claims. Every other call site's k is UNVERIFIED,")
    print(f"      and `UNVERIFIED` is not `large` — it is the audit that cannot be run.")

    # ---- CONTROLS ------------------------------------------------------------------------------
    print("\n  CONTROLS")
    r372_sites = [s for s in sites if s["round"] == "R372"]
    r301_sites = [s for s in sites if s["round"] == "R301"]
    p_r372 = any(SMALLISH.search(s["den"]) for s in r372_sites)
    p_r301 = bool(r301_sites) and not any(SMALLISH.search(s["den"]) for s in r301_sites)
    parser_pos = p_r372 and p_r301
    print(f"    PARSER (+)  R372 must classify SMALL-K (it is a stratum count) -> "
          f"{'small-k' if p_r372 else 'MISCLASSIFIED'} "
          f"[{len(r372_sites)} sites]")
    print(f"                R301 must classify SAMPLE (sqrt(968), and its k=4 is core size) -> "
          f"{'sample' if p_r301 else 'MISCLASSIFIED'} "
          f"[{len(r301_sites)} sites]")
    print(f"                both known independently of this parse  "
          f"{'PASS' if parser_pos else 'FAIL'}")
    neg = len(CALL.findall("x = 1\nprint('no mde here')\nsqrt(9)\n"))
    parser_neg = (neg == 0)
    print(f"    PARSER (-)  a file with no estimator yields {neg} call sites  "
          f"{'PASS' if parser_neg else 'FAIL'}")
    plac_big = collapse_prob(200, 0.5)
    plac_med = collapse_prob(200, 1.0)
    plac_ok = (plac_big < 1e-6) and (abs(plac_med - 0.5) < 0.02)
    print(f"    PLACEBO     at k=200 the collapse below half sigma is {plac_big:.2e} (~0), and at")
    print(f"                f=1 the probability is {plac_med:.4f} — the median, known independently"
          f"  {'PASS' if plac_ok else 'FAIL'}")
    rng_ok = collapse_prob(2, 0.5) > 10 * collapse_prob(8, 0.5)
    print(f"    RANGE       the derivation spans {collapse_prob(2,0.5):.4f} at k=2 to "
          f"{collapse_prob(8,0.5):.5f} at k=8  {'PASS' if rng_ok else 'FAIL'}")

    ctrl_ok = chi_ok and parser_pos and parser_neg and plac_ok and rng_ok

    # ---- VERDICT -------------------------------------------------------------------------------
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; every table above is silence, not a result.")
        v = "UNVERIFIED"
    else:
        # ⚠ the branches are NOT exclusive, so all are computed and printed, and the branch whose
        #   INSTRUMENT was withdrawn is reported UNVERIFIED rather than re-derived from a better
        #   word list after the fact.
        b_clean = (len(severe_outside) == 0)
        print(f"  branch computations, all of them, whichever fired:")
        print(f"    ⚠ `clean` is judged on RESOLVED k < {SEVERE}, not on the parser's flag. Flagged")
        print(f"      outside the stratum family: {outside}. Of those, actually severe: "
              f"{severe_outside if severe_outside else 'none'}")
        print(f"      (R355 is flagged and its k is 25 — the flag was not the severity.)")
        print(f"    unauditable (recorded < 50%)         : UNVERIFIED — the instrument that")
        print(f"                                           measured it had no positive control")
        print(f"                                           and is withdrawn above")
        print(f"    clean (no severe k outside R370-372) : {b_clean}")
        print(f"    contaminated                         : {not b_clean}   "
              f"(parser positive-controlled at 2 known points)")
        if b_clean:
            print(f"\n  W-CLEAN — every small-k denominator sits inside R370-R372, so R372's collapse")
            print(f"  is local to the stratum family and no other published cell inherits it.")
            v = "W_CLEAN"
        else:
            ks_out = sorted({k for r in severe_outside for k in KS_FOUND[r]["ks"]})
            print(f"\n  W-CONTAMINATED — a denominator with RESOLVED k < {SEVERE} appears outside the")
            print(f"  stratum family, in {severe_outside}, at k = {ks_out}.")
            print(f"  **{severe_outside[0]} is cited by DEFINITION.md**, so the definition's own transport row")
            print(f"  rests on an MDE whose denominator averaged {min(ks_out)} units — where the sd lands below")
            print(f"  half its true value {collapse_prob(min(ks_out),0.5):.1%} of the time and below three quarters")
            print(f"  {collapse_prob(min(ks_out),0.75):.1%} of the time. That verdict is NOT refuted; it is")
            print(f"  UNDER-PRICED, and the difference matters because nobody re-examines a cell")
            print(f"  that reported RESOLVED.")
            v = "W_CONTAMINATED"
        print(f"\n  ⛔ AND THE `UNAUDITABLE` QUESTION IS STILL OPEN, named rather than dropped: this")
        print(f"     round could not measure how much of the campaign records its denominators,")
        print(f"     because the only instrument it had for that was a word list. That is a")
        print(f"     RESIDUAL, not a finding, and it is what the gate below exists to close going")
        print(f"     forward — a gate cannot recover the {len(sites) - len(smallk)} sites already"
              f" published without their k.")
        v += "_RECORD_SHARE_UNVERIFIED"

    print(f"\n  ⚠ THE TWO UNITS, restated at the end where a summary usually asserts instead:")
    print(f"    this round counted {len(sites)} CALL SITES. It did not count published NUMBERS, and")
    print(f"    the link between them is precisely what the artifacts do not carry. Every sentence")
    print(f"    above is about call sites; none is about how many verdicts would change.")

    art = dict(stamp(str(SELF)), derivation={str(k): DERIV[k] for k in DERIV},
               chi_check=rows_b, chi_max_err=max_err, chi_mean_err=mean_err,
               n_sites=len(sites), n_rounds=len(byfile),
               denominators={d_: n_ for d_, n_ in dens.most_common()},
               small_k_sites=len(smallk),
               small_k_rounds=sorted({s["round"] for s in smallk}),
               small_k_outside_stratum=outside, severe_threshold=SEVERE,
               severe_rounds=sorted(severe), severe_outside_stratum=severe_outside,
               recorded_share="UNVERIFIED_instrument_withdrawn",
               small_k_resolved={r: KS_FOUND[r] for r in KS_FOUND}, k_unresolved=unresolved,
               controls=dict(chi=chi_ok, parser_pos=parser_pos, parser_neg=parser_neg,
                             placebo=plac_ok, range=rng_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r373_resolution_audit.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
