"""definition_matches_the_record — every number in DEFINITION.md is re-derived from an artifact.

WHY THIS EXISTS. `DEFINITION.md` states the definition once, in prose, with numbers in it. Prose
does not recompute. The campaign's own history says what happens next: a number stated in a document
drifts from the round that produced it, and the copy is never the one that gets corrected (R351/R352
found seven artifacts whose committed numbers no longer matched their source, and NO page quoted
them). A definition is the worst possible place for that, because it is the one document a reader
takes as settled.

So every quantitative claim in DEFINITION.md is written as a CHECKABLE ASSERTION and re-derived here
from the committed artifact of the round that measured it. If the artifact moves and the prose does
not — or the prose is edited and the artifact does not support it — this fails.

PROXY LEDGER, because this check approximates its property in one direction only:
  PROPERTY   "DEFINITION.md's claims are true of the record"
  PROXY      "the numbers this file knows how to extract match the artifacts"
  IMPLICATION  proxy fails => property fails.  proxy passes =/=> property holds: a claim written in
               prose that is NOT in the assertion table below is unchecked by construction.
  SAFE SIDE  the count of checked-vs-total assertions is PRINTED every run, so the unchecked
             remainder is visible rather than implied. This check may never be read as certifying
             the document.

EMPTY POPULATION: if DEFINITION.md is missing, or no assertion can be evaluated because artifacts
are absent, exit 2 — never 0. A gate that examined nothing has not passed.

POSITIVE CONTROL: the file mutates its own in-memory copy of each claimed value and requires the
comparison to reject it. A checker never shown able to fail is silence.
"""
from __future__ import annotations
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = ROOT / "E05_the_space_of_compilers" / "DEFINITION.md"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"


def art(pat):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def derive():
    """Each entry: label -> (value from the artifact, the round it came from).

    Returns None for a value whose artifact is absent, so the caller can count it as unevaluable
    rather than silently skipping it."""
    out = {}
    a = art("R347_*")
    out["clause1_excludes"] = (len(a["counterexamples"]) if a else None, "R347")
    out["n_arms_r347"] = (a["n_arms"] if a else None, "R347")
    a = art("R360_*")
    if a:
        out["clause2_excludes"] = (len(a["arms"]) - len(a["clause2_admits"]), "R360")
        out["clause3_excludes"] = (len(a["clause2_admits"]) - len(a["clause23_admits"]), "R360")
        out["n_arms_r360"] = (len(a["arms"]), "R360")
        out["sweep_levels"] = (len(a["sweep"]), "R360")
        out["label_users_min"] = (min(len(r["labels"]) for r in a["sweep"]), "R360")
        out["five_at_strongest"] = (len(a["sweep"][-1]["five"]), "R360")
    else:
        for k in ("clause2_excludes", "clause3_excludes", "n_arms_r360", "sweep_levels",
                  "label_users_min", "five_at_strongest"):
            out[k] = (None, "R360")
    a = art("R301_*")
    out["admitted_2B"] = (len(a["admitted_2b"]) if a else None, "R301")
    out["admitted_08B"] = (len(a["admitted_08b"]) if a else None, "R301")
    out["n_arms_r301"] = (a["n_arms"] if a else None, "R301")
    a = art("R331_*")
    out["published_ref_pctile"] = (round(a["r294_reference"]["pctile"], 1) if a else None, "R331")
    a = art("R355_*")
    out["closure_violations_2B"] = (a["totals"]["45"] if a else None, "R355")
    out["closure_k_count"] = (len(a["ks"]) if a else None, "R355")
    a = art("R358_*")
    out["closure_violations_08B"] = (a["totals_08b"]["45"] if a else None, "R358")
    a = art("R371_*")
    if a:
        out["null_ratio"] = (round(a["median_ratio"], 2), "R371")
    else:
        out["null_ratio"] = (None, "R371")
    a = art("R372_*")
    if a:
        h = a["setstat"]["half|exact"]
        out["r371_set_rate"] = (round(100 * h["p_r371"], 1), "R372")
        out["r372_empty_rate"] = (round(100 * h["p_empty"], 1), "R372")
        out["r372_distinct"] = (h["distinct"], "R372")
        out["r372_splithalf"] = (round(100 * a["split_half"]["half|exact"]["cond"], 1), "R372")
        out["r372_degen_2"] = (round(100 * a["degeneracy"]["half|exact|2"]["degenerate"], 1),
                               "R372")
        out["r372_degen_max"] = (round(100 * max(
            a["degeneracy"][f"half|exact|{S}"]["degenerate"] for S in (3, 4, 5, 6, 8)), 1), "R372")
        out["r372_halves"] = (a["n_halves"], "R372")
    else:
        for k in ("r371_set_rate", "r372_empty_rate", "r372_distinct", "r372_splithalf",
                  "r372_degen_2", "r372_degen_max", "r372_halves"):
            out[k] = (None, "R372")
    a = art("R373_*")
    if a:
        out["r373_sites"] = (a["n_sites"], "R373")
        out["r373_rounds"] = (a["n_rounds"], "R373")
        out["r373_small_k"] = (a["small_k_sites"], "R373")
        out["r373_k368"] = (a["small_k_resolved"]["R368"]["ks"][0], "R373")
        out["r373_p_half"] = (round(100 * a["derivation"]["4"]["0.5"], 1), "R373")
        out["r373_p_three_q"] = (round(100 * a["derivation"]["4"]["0.75"], 1), "R373")
        out["r373_k355"] = (a["small_k_resolved"]["R355"]["ks"][0], "R373")
    else:
        for k in ("r373_sites", "r373_rounds", "r373_small_k", "r373_k368", "r373_p_half",
                  "r373_p_three_q", "r373_k355"):
            out[k] = (None, "R373")
    # R398 -- the register's `one release` line was retracted from DEFINITION.md, and a retraction
    # that states counts must be re-derivable exactly like the claims it replaced. Otherwise the
    # correction is the one sentence in the document nobody can check.
    a = art("R398_*")
    if a:
        out["r398_rows"] = (a["rows"], "R398")
        out["r398_convs"] = (a["conversations"], "R398")
        out["r398_multi"] = (a["multi_response_prompts"], "R398")
        out["r398_models"] = (a["n_models"], "R398")
        out["r398_refs"] = (a["prior_art_references"], "R398")
    else:
        for k in ("r398_rows", "r398_convs", "r398_multi", "r398_models", "r398_refs"):
            out[k] = (None, "R398")
    a = art("R419_*")
    if a:
        out["r419_maxabs"] = (a["max_abs"], "R419")
        out["r419_n"] = (a["n_prompts"], "R419")
    else:
        for k in ("r419_maxabs", "r419_n"):
            out[k] = (None, "R419")
    # R424 -- the containment anchors. These are the numbers that turn "foreign" from a word into a
    # measurement, so they are the ones a later edit must not be able to drift silently.
    # R403 -- the statability counts the new DEFINITION.md block asserts. Re-derived so the prose
    # cannot drift. maxraters/multirater are NOT re-declared here: anchors for them already exist
    # further down, and declaring them twice is exactly the silent failure this file now guards.
    # R427 -- the first cross-release numbers. Three artifacts live in one round directory, so each
    # is located BY NAME rather than by "the first json", which would silently pick whichever sorts
    # first -- the same shape of silent wrong-target error the duplicate-key control now guards.
    d427 = next(A24.glob("R427_*"), None)

    def r427(stem):
        f = (d427 / "results" / stem) if d427 else None
        return json.loads(f.read_text()) if f and f.exists() else None
    a = r427("r427_transport.json")
    if a:
        out["r427_generic"] = (f"{a['generic']['acc']:.4f}", "R427")
        out["r427_length"] = (f"{a['length']:.4f}", "R427")
        out["r427_convs"] = (a["controls"]["n_conv"], "R427")
    else:
        for k in ("r427_generic", "r427_length", "r427_convs"):
            out[k] = (None, "R427")
    a = r427("r427_speccurve.json")
    out["r427_cells"] = ((a["n_cells"], "R427") if a else (None, "R427"))
    out["r427_favour"] = ((len(a["favour"]), "R427") if a else (None, "R427"))
    a = r427("r427_strata.json")
    if a:
        s2 = a["strata"]["2"]
        out["r427_n2_diff"] = (f"{s2['g_diff']:+.4f}", "R427")
        out["r427_n2_mde"] = (f"{s2['g_mde']:.4f}", "R427")
    else:
        for k in ("r427_n2_diff", "r427_n2_mde"):
            out[k] = (None, "R427")
    # R427's ARMS + R429. Added 2026-08-04. ⛔ WHY THIS IS NOT OPTIONAL: DEFINITION.md gained a
    # five-row arm table and a resolution paragraph, and this gate's own closing line says every
    # prose claim not in the assertion table is "unchecked BY CONSTRUCTION". Adding numbers to the
    # document without adding their anchors GROWS that unchecked remainder while the gate keeps
    # printing PASS -- the pass gets no less true and steadily less informative, which is how a
    # gate becomes decoration without anyone editing it.
    a = r427("r427_transport.json")
    if a and "randblind" in a:
        out["r427_vacuous"] = (f"{a['randblind']['vacuous']['acc']:.4f}", "R427")
        out["r427_vacuous_gap"] = (f"{a['randblind']['vacuous']['gen_minus']:+.4f}", "R427")
        out["r427_vacuous_mde"] = (f"{a['randblind']['vacuous']['mde']:.4f}", "R427")
        out["r427_rb0"] = (f"{a['randblind']['randblind_s0']['acc']:.4f}", "R427")
    else:
        for k in ("r427_vacuous", "r427_vacuous_gap", "r427_vacuous_mde", "r427_rb0"):
            out[k] = (None, "R427")
    d429 = next(A24.glob("R429_*"), None)

    def r429(stem):
        f = (d429 / "results" / stem) if d429 else None
        return json.loads(f.read_text()) if f and f.exists() else None
    a = r429("r429_pair_resolution.json")
    if a and a.get("world") != "UNVERIFIED":
        t = a["top_vs_rank2"]
        out["r429_delta"] = (f"{t['delta']:+.4f}", "R429")
        out["r429_lo"] = (f"{t['lo']:+.4f}", "R429")
        out["r429_hi"] = (f"{t['hi']:+.4f}", "R429")
        out["r429_cells"] = (a["cells_tested"], "R429")
    else:
        for k in ("r429_delta", "r429_lo", "r429_hi", "r429_cells"):
            out[k] = (None, "R429")
    a = r429("r429_null_estimator.json")
    if a and a.get("world") != "UNVERIFIED":
        out["r429_inside"] = (a["inside"], "R429")
        out["r429_meangap"] = (f"{a['mean_gap']:+.4f}", "R429")
        out["r429_half"] = (f"{a['mean_band_half']:.4f}", "R429")
    else:
        for k in ("r429_inside", "r429_meangap", "r429_half"):
            out[k] = (None, "R429")
    a = art("R403_*")
    if a:
        cl = a["clauses"]
        out["r403_statable"] = (sum(1 for v in cl.values() if v["second"] == "STATABLE"), "R403")
        out["r403_total"] = (len(cl), "R403")
    else:
        for k in ("r403_statable", "r403_total"):
            out[k] = (None, "R403")
    a = art("R424_*")
    if a:
        an = a["anchors"]
        out["r424_neg_rate"] = (f"{an['neg_rate']:.4f}", "R424")
        out["r424_neg_n"] = (an["neg_n"], "R424")
        out["r424_neg_tot"] = (an["neg_total"], "R424")
        out["r424_pos_rate"] = (f"{an['pos_rate']:.4f}", "R424")
        out["r424_pos_n"] = (an["pos_n"], "R424")
    else:
        for k in ("r424_neg_rate", "r424_neg_n", "r424_neg_tot", "r424_pos_rate", "r424_pos_n"):
            out[k] = (None, "R424")
    # R426 -- the emitter, identified. These are the numbers that RETRACT R424's wall, so they are
    # the ones a later edit must not be able to drift back.
    a = art("R426_*")
    if a:
        c = a["candidates"]["corebench/results/sat08_full.npz"]
        out["r426_pos"] = (f"{c['oracle_k4_08b']['rate']:.4f}", "R426")
        out["r426_pos_n"] = (c["oracle_k4_08b"]["ok"], "R426")
        out["r426_topw"] = (f"{c['topw_k4']['rate']:.4f}", "R426")
        out["r426_excluded"] = (a["excluded_by_r424"], "R426")
    else:
        for k in ("r426_pos", "r426_pos_n", "r426_topw", "r426_excluded"):
            out[k] = (None, "R426")
    a = art("R415_*")
    if a:
        out["r415_shift"] = (round(a["worst_mean_shift"], 6), "R415")
        out["r415_pairs"] = (a["controls"]["n_pairs"], "R415")
    else:
        for k in ("r415_shift", "r415_pairs"):
            out[k] = (None, "R415")
    a = art("R408_*")
    if a:
        out["r408_strict"] = (len(a["label_free_strict"]), "R408")
        out["r408_literal"] = (len(a["label_free_literal"]), "R408")
        out["r408_core_e"] = (round(a["rows"]["coval_core"]["e"], 6), "R408")
    else:
        for k in ("r408_strict", "r408_literal", "r408_core_e"):
            out[k] = (None, "R408")
    a = art("R407_*")
    if a:
        out["r407_free"] = (len(a["label_free_admitted"]), "R407")
        out["r407_top"] = (len(a["top_cell"]), "R407")
        out["r407_core_pct"] = (a["brackets"]["coval_core"][0], "R407")
    else:
        for k in ("r407_free", "r407_top", "r407_core_pct"):
            out[k] = (None, "R407")
    a = art("R406_*")
    if a:
        out["r406_gap"] = (round(a["gap"], 10), "R406")
        out["r406_max"] = (round(a["blind_dist"]["max"], 10), "R406")
        out["r406_ref"] = (round(a["ref_a"], 10), "R406")
    else:
        for k in ("r406_gap", "r406_max", "r406_ref"):
            out[k] = (None, "R406")
    a = art("R404_*")
    if a:
        out["r404_b_beyond_a"] = (len(a["b_beyond_a"]), "R404")
        out["r404_excl_c"] = (len(a["excl_3c"]), "R404")
        out["r404_admitted_abc"] = (len(a["admitted_2abc"]), "R404")
        out["r404_published"] = (len(a["published"]), "R404")
    else:
        for k in ("r404_b_beyond_a", "r404_excl_c", "r404_admitted_abc", "r404_published"):
            out[k] = (None, "R404")
    a = art("R403_*")
    if a:
        out["r403_notstatable"] = (len(a["not_statable_on_second"]), "R403")
        out["r403_maxraters"] = (a["max_raters"], "R403")
        out["r403_multirater"] = (a["multi_rater_interactions"], "R403")
        out["r403_interactions"] = (a["interactions"], "R403")
    else:
        for k in ("r403_notstatable", "r403_maxraters", "r403_multirater", "r403_interactions"):
            out[k] = (None, "R403")
    a = art("R370_*")
    if a:
        out["pool_contrast"] = (round(a["results"]["pool|exact"]["contrast"], 4), "R370")
        out["pool_mde"] = (round(a["results"]["pool|exact"]["mde"], 4), "R370")
    else:
        out["pool_contrast"] = (None, "R370"); out["pool_mde"] = (None, "R370")
    a = art("R369_*")
    if a:
        out["dfloor_exact"] = (round(a["decomposition"]["exact"]["d_floor"], 4), "R369")
        out["dcore_exact"] = (round(a["decomposition"]["exact"]["d_core"], 4), "R369")
    else:
        out["dfloor_exact"] = (None, "R369"); out["dcore_exact"] = (None, "R369")
    a = art("R368_*")
    if a:
        out["transport_exact"] = (round(a["matched_contrast"]["exact"], 4), "R368")
        out["transport_mde"] = (round(a["mde"]["exact"], 4), "R368")
    else:
        out["transport_exact"] = (None, "R368"); out["transport_mde"] = (None, "R368")
    a = art("R367_*")
    if a:
        out["rule_b_2B"] = (round(a["rule_b"]["mean_2B"], 4), "R367")
        out["rule_b_08B"] = (round(a["rule_b"]["mean_08B"], 4), "R367")
        out["rule_b_n"] = (a["n_external"], "R367")
    else:
        for k in ("rule_b_2B", "rule_b_08B", "rule_b_n"):
            out[k] = (None, "R367")
    a = art("R366_*")
    if a:
        out["survive_n"] = (a["n_claims"], "R366")
        out["p_form"] = (round(a["table_form"]["p"], 4), "R366")
        out["p_null"] = (round(a["table_null"]["p"], 4), "R366")
        out["p_perfect"] = (round(a["controls"]["positive_p"], 4), "R366")
    else:
        for k in ("survive_n", "p_form", "p_null", "p_perfect"):
            out[k] = (None, "R366")
    a = art("R365_*")
    if a:
        out["mde_ratio_08B"] = (round(a["delta"]["0.8B"][1] / a["delta"]["2B"][1], 2), "R365")
        out["channel_mde_08B"] = (round(a["delta"]["0.8B"][1], 4), "R365")
    else:
        out["mde_ratio_08B"] = (None, "R365"); out["channel_mde_08B"] = (None, "R365")
    a = art("R364_*")
    if a:
        out["channel_mde"] = (round(a["delta_mde"], 4), "R364")
        out["plant_detected"] = (round(a["positive"]["0.5"][0], 4), "R364")
    else:
        out["channel_mde"] = (None, "R364"); out["plant_detected"] = (None, "R364")
    a = art("R363_*")
    if a:
        out["overlap_pct"] = (round(a["same"]["mean"] * 100, 1), "R363")
        out["overlap_ratio"] = (round(a["ratio"]), "R363")
        out["n_annotators"] = (a["n_annotators"], "R363")
        out["full_overlap_prompts"] = (a["all_overlap_prompts"], "R363")
    else:
        for k in ("overlap_pct", "overlap_ratio", "n_annotators", "full_overlap_prompts"):
            out[k] = (None, "R363")
    a = art("R362_*")
    if a:
        out["neg_sizes_08B"] = (sum(1 for k in a["ks"]
                                    if a["margins"][f"0.8B|{k}"][0] < 0), "R362")
        out["sign_flips"] = (len(a["sign_flips"]), "R362")
    else:
        out["neg_sizes_08B"] = (None, "R362"); out["sign_flips"] = (None, "R362")
    a = art("R361_*")
    out["labels_min_08B"] = (a["min_labels"]["0.8B"] if a else None, "R361")
    out["rank_p_2B"] = (round(a["rank_null"]["2B"]["two_sided_p"], 4) if a else None, "R361")
    out["rank_null_n"] = (a["rank_null"]["2B"]["n"] if a else None, "R361")
    return out


# label -> the regex that must find that number in DEFINITION.md. The pattern is the CLAIM's own
# wording, so an edit that changes the sentence without changing the artifact is caught too.
ASSERTIONS = {
    "clause1_excludes":      r"\*\*(\d+) of 41\*\*",
    "clause2_excludes":      r"\*\*(\d+) of 42\*\*",
    "clause3_excludes":      r"\*\*(\d+) of 42\*\*\s*\|\s*\*\*DERIVED\*\* that it excludes",
    "admitted_2B":           r"\*\*(\d+)\*\* arms admitted at Qwen3\.5-2B-Base",
    "admitted_08B":          r"\*\*(\d+)\*\* at\s*\n?\s*Qwen3\.5-0\.8B-Base",
    "n_arms_r301":           r"on all (\d+) arms",
    "published_ref_pctile":  r"\*\*(\d+\.\d)th percentile\*\*",
    "sweep_levels":          r"Across all \*\*(\d+)\*\* reference levels",
    "label_users_min":       r"never falls below (\d+)",
    "five_at_strongest":     r"published five fall to \*\*(\d+)\*\*",
    # R361 — added when the closing claim was corrected. A claim that changes must bring its
    # check with it, or the gate silently certifies the OLD sentence's numbers.
    "labels_min_08B":        r"falls to \*\*(\d+)\*\* — references \*do\* purge them there",
    "rank_p_2B":             r"exact two-sided p = \*\*(\d\.\d+)\*\*",
    "rank_null_n":           r"C\(9,4\)=(\d+) assignments",
    # R362 — the size claim became judge-indexed; its numbers come with it.
    "neg_sizes_08B":         r"\*\*negative at (\d+) of 7 sizes\*\*",
    "sign_flips":            r"a \*sign\ninversion\* at \*\*(\d+) of 7 sizes\*\*",
    # R363 — clause ③ narrowed; its census numbers come with it.
    "overlap_pct":           r"are, at \*\*(\d+\.\d)%\*\*, the same",
    "overlap_ratio":         r"ratio \*\*(\d+)×\*\*",
    "n_annotators":          r"\*\*([\d,]+)\*\* distinct annotators",
    "full_overlap_prompts":  r"\*\*(\d+) of 968\*\* prompts have complete",
    # R364 — the channel was sized; the bound and its power come with the claim.
    "channel_mde":           r"MDE of (\d\.\d+)\*\*, with three seeds",
    "plant_detected":        r"detected from \*\*\+(\d\.\d+)\*\* upward",
    # R365 — the null survived a change of judge; its second-judge numbers come with it.
    "channel_mde_08B":       r"\*\*\+0\.0000 vs MDE (\d\.\d+) at 0\.8B\*\*",
    "mde_ratio_08B":         r"only \*\*(\d\.\d+)×\*\* 2B's",
    # R366 — the survival explanation was refuted; its counts come with the correction.
    "survive_n":             r"population of \*\*(\d+)\*\* claims run at both judges",
    "p_form":                r"neither `difference` \(Fisher\n\*\*p = (\d\.\d+)\*\*\)",
    "p_null":                r"nor `null` \(\*\*p = (\d\.\d+)\*\*\)",
    "p_perfect":             r"\*\*would\*\*\s+have reached \*\*p = (\d\.\d+)\*\*",
    # R367 — J became nameable; the external check's numbers come with the rule.
    "rule_b_2B":             r"last \*\*(\d\.\d+)\*\* of the time",
    "rule_b_08B":            r"against 0\.8B's \*\*(\d\.\d+)\*\*",
    "rule_b_n":              r"on the \*\*(\d+)\*\*\s*\n?prompts carrying such a rating",
    # R368 — transport measured; its numbers travel with the clause.
    "transport_exact":       r"by \*\*\+(\d\.\d+) against an MDE",
    "transport_mde":         r"against an MDE of (\d\.\d+)\*\*",
    # R369 — the decomposition; its two numbers travel with the caveat.
    "dfloor_exact":          r"is \*\*\+(\d\.\d+)\*\* on exact",
    "dcore_exact":           r"under both \(\*\*\+(\d\.\d+)\*\*",
    # R370 — transport demoted to a limit; the non-subset numbers travel with it.
    # ⚠ anchored on the R370 sentence: the bare `**+N vs MDE` form also matches R367's
    #   rule-A number (+0.0967) earlier in the document, and the gate caught that collision.
    "pool_contrast":         r"the contrast is \*\*\+(\d\.\d+) vs MDE",
    "pool_mde":              r"vs MDE (\d\.\d+)\*\* \(exact\)",
    # R371 — the verdict is S-dependent; the null ratio travels with that caveat.
    "null_ratio":            r"median ratio is \*\*(\d\.\d+)\*\*",
    # R372 — the S-curve itself dies. Every pattern is anchored on words unique to its row,
    # because R370's collision taught that a bare number form matches the wrong round.
    "r371_set_rate":         r"R371's set `\{2, 5\}` recurs \| \*\*(\d+\.\d)%\*\*",
    "r372_empty_rate":       r"at \*\*(\d+\.\d)%\*\* — with",
    "r372_distinct":         r"— with \*\*(\d+)\*\* distinct sets",
    "r372_splithalf":        r"agree on the set \| \*\*(\d+\.\d)%\*\*",
    "r372_degen_2":          r"in \*\*(\d+\.\d)%\*\* of halves against at most",
    "r372_degen_max":        r"against at most \*\*(\d+\.\d)%\*\* anywhere else",
    "r372_halves":           r"\*\*(\d+) random halves\*\*",
    # R373 — the transport MDE is under-priced. Anchored on words unique to each row.
    "r373_sites":            r"Of \*\*(\d+)\*\* MDE call sites",
    "r373_rounds":           r"call sites across \*\*(\d+)\*\* rounds",
    "r373_small_k":          r"rounds, \*\*(\d+)\*\* divide by a count",
    "r373_k368":             r"that count is \*\*(\d+)\*\*",
    # ⚠ the bold wraps the whole clause, not the number -- v1 anchored on `**N%**` and the gate
    #   caught it as an assertion it could no longer locate, which is the point of that branch.
    "r373_p_half":           r"below half its true value (\d+\.\d)%\*\* of the time",
    # R398's retraction of the `one release` wall. Anchored on the surrounding words, not on a bare
    # number, because R373 already cost a false failure when a regex anchored on `**N%**` while the
    # bold wrapped the whole clause.
    "r398_rows":             r"\*\*([\d,]+) rows over [\d,]+ conversations",
    "r398_convs":            r"rows over ([\d,]+) conversations",
    "r398_multi":            r"with ([\d,]+) prompts having",
    "r398_models":           r"distinct model responses across (\d+) models",
    "r398_refs":             r"and referenced by (\d+) files in this repository",
    # R403's statability split. Anchored on surrounding WORDS, never a bare number — R373 and R398
    # both cost a false failure when an anchor met a bold span instead of a digit.
    # ⚠ ADDED AFTER THE GATE PRINTED A CLEAN BILL WITHOUT IT — TWICE. `r404_b_beyond_a` was declared
    # in the extractor with no anchor here, so this round's LOAD-BEARING claim (③b excludes nothing
    # beyond ③a) was silently unchecked. A declared assertion with no anchor is not a weaker check,
    # it is NO check. And my first attempt to add it failed its own guard and applied nothing while
    # the commit message said it had — so the second failure was in the REPAIR, not the original.
    "r419_n":                r"bitwise identical on all (\d+) prompts",
    "r427_generic":          r"picks the human-chosen response at \*\*`([\d.]+)`\*\*",
    "r427_length":           r"rule reaches \*\*`([\d.]+)`\*\*",
    "r427_convs":            r"judge calls, ([\d,]+) seeded conversations",
    # R427 arms + R429. Anchored on the arm table's own row shape and the resolution sentence, so a
    # number edited in the prose without re-running the round fails here rather than drifting.
    "r427_vacuous":          r"\*\*all evaluative content\*\* \| ([\d.]+) \|",
    "r427_vacuous_gap":      r"\*\*all evaluative content\*\* \| [\d.]+ \| \*\*([+\-][\d.]+)\*\*",
    "r427_vacuous_mde":      r"\*\*all evaluative content\*\* \| [\d.]+ \| \*\*[+\-][\d.]+\*\* \| ([\d.]+)",
    "r427_rb0":              r"the criteria↔prompt assignment \| ([\d.]+) \|",
    "r429_delta":            r"\*\*Δ\(rank 1 - rank 2\) = ([+\-][\d.]+)",
    "r429_lo":               r"\*\*Δ\(rank 1 - rank 2\) = [+\-][\d.]+ \[([+\-][\d.]+),",
    "r429_hi":               r"\*\*Δ\(rank 1 - rank 2\) = [+\-][\d.]+ \[[+\-][\d.]+, ([+\-][\d.]+)\]",
    "r429_cells":            r"surviving BH\(q=0\.10\) over all (\d+)\s*\n?\s*> ordered comparisons",
    "r429_inside":           r"only (\d+) of 10 inside",
    "r429_meangap":          r"mean ([+\-][\d.]+) against a one-draw band",
    "r429_half":             r"one-draw band half-width of ([\d.]+)",
    "r427_cells":            r"clears the shortcut in 0 of (\d+) cells",
    "r427_favour":           r"clears the shortcut in (\d+) of \d+ cells",
    "r427_n2_diff":          r"\| \*\*2\*\* \(2,191 convs\) \| 0\.5000 \| \*\*([+\d.]+)\*\*",
    "r427_n2_mde":           r"\| \*\*2\*\* \(2,191 convs\) \| 0\.5000 \| \*\*[+\d.]+\*\* \| ([\d.]+)",
    "r403_statable":         r"\*\*(\d+) of \d+ are STATABLE on the",
    "r403_total":            r"\*\*\d+ of (\d+) are STATABLE on the",
    "r426_pos":              r"contains both families at\s*\n?`([\d.]+)` \(",
    "r426_pos_n":            r"contains both families at\s*\n?`[\d.]+` \(([\d,]+) of",
    "r426_topw":             r"while containing `topw_k4` at `([\d.]+)`",
    "r426_excluded":         r"skipped `corebench/results` — (\d+) files",
    "r424_neg_rate":         r"absent from the default judge's table\*\* — `([\d.]+)`",
    "r424_neg_n":            r"absent from the default judge's table\*\* — `[\d.]+`\s*\n?\(([\d,]+) of",
    "r424_neg_tot":          r"absent from the default judge's table\*\* — `[\d.]+`\s*\n?\([\d,]+ of ([\d,]+)\)",
    "r424_pos_rate":         r"against that table's `([\d.]+)`",
    "r424_pos_n":            r"against that table's `[\d.]+`\s*\n?\(([\d,]+) of",
    "r415_shift":            r"mean A2 by up to `(0\.\d+)`",
    "r415_pairs":            r"\*\*(\d+)\*\* committed re-run pairs exist",
    "r408_core_e":           r"scores \*\*`\+(0\.\d+)`\*\* against `se",
    "r408_literal":          r"\| \*\*(\d+)\*\* — `coval_core`, `topw_k3/4/6/8` \|",
    "r407_core_pct":         r"\*\*`coval_core` (\d+\.\d)\*\*",
    "r407_free":             r"Label-free admitted: (\d+)\.\*\*",
    "r406_ref":              r"instantiated at `(0\.\d+)`, the best HELD-OUT",
    "r406_max":              r"the same 1,820\s*\nis `(0\.\d+)`",
    "r406_gap":              r"The gap is \*\*`\+(0\.\d+)`\*\*",
    "r404_b_beyond_a":       r"fitted on a \*\*half\*\* of them \| 3 \| \*\*(\d+)\*\*",
    "r404_excl_c":           r"annotator-written \*\*rubric\*\* \| (\d+) \|",
    "r404_admitted_abc":     r"collapses the admitted set from \*\*5 to (\d+)",
    "r404_published":        r"collapses the admitted set from \*\*(\d+) to",
    "r403_notstatable":      r"\*\*(\d+) of 6 clause-parts are NOT-STATABLE",
    "r403_maxraters":        r"measured: \*\*max (\d+) rater\*\*",
    "r403_multirater":       r"rater\*\*, (\d+) of [\d,]+ interactions have 2",
    "r403_interactions":     r"of ([\d,]+) interactions have 2",
    "r373_p_three_q":        r"below three quarters\n\*\*(\d+\.\d)%\*\* of the time",
    "r373_k355":             r"its k is \*\*(\d+)\*\*, which is fine",
}


def same(claimed, actual):
    """THE comparison. Factored out so the positive control below exercises THIS code path.

    ⚠ v1's positive control computed `abs((tv + 1.0) - tv) >= 1e-9` inline -- arithmetic that is
    true whatever this function does. Neutering the check to `return True` would have left the
    control passing, which is a control that does not run the instrument it certifies. Caught by
    attacking the gate after building it (P7), which is also where the previous fix's hole was."""
    return abs(float(claimed) - float(actual)) < 1e-9


def read_claims(text):
    got = {}
    for label, pat in ASSERTIONS.items():
        m = re.search(pat, text)
        got[label] = float(m.group(1).replace(",", "")) if m else None
    return got


def duplicate_keys(path: pathlib.Path):
    """⛔ A CONTROL ON THIS GATE, ADDED AFTER IT FAILED SILENTLY. `r403_maxraters` was declared TWICE
    in the CLAIMS literal; Python keeps the LAST, so the newer anchor was discarded without a word
    and the gate printed `ok` for a claim it was not checking. A mutation test on that claim also
    `passed`, because the surviving anchor pointed at a different sentence entirely.

    A dict cannot report its own dropped keys, so the SOURCE is scanned instead. Planting a
    duplicate makes this fail, which is how it was verified."""
    src = path.read_text()
    keys = re.findall(r'^\s{4}"([a-z0-9_]+)":\s+r"', src, re.M)
    seen, dup = set(), []
    for k in keys:
        (dup.append(k) if k in seen else seen.add(k))
    return keys, sorted(set(dup))


def main() -> int:
    keys, dup = duplicate_keys(pathlib.Path(__file__))
    print(f"  CONTROL on this gate — duplicate anchor keys in the CLAIMS literal: {dup or 'none'}")
    print(f"    {len(keys)} anchors declared, {len(set(keys))} distinct. Python drops a duplicate")
    print(f"    SILENTLY, so an anchor can be discarded and this gate prints `ok` for a claim it is")
    print(f"    not checking. That happened once and nothing here could detect it.")
    if dup:
        print(f"\n  FAIL: {dup} declared more than once. The later wins and the earlier is unchecked.")
        return 1
    if not DOC.exists():
        print(f"  UNRUNNABLE: {DOC.relative_to(ROOT)} is absent. Exit 2, never 0.")
        return 2
    text = DOC.read_text(encoding="utf-8")
    truth = derive()
    claimed = read_claims(text)

    evaluable = [k for k in ASSERTIONS
                 if truth.get(k, (None,))[0] is not None and claimed.get(k) is not None]
    if not evaluable:
        print("  UNRUNNABLE: not one assertion could be evaluated — either DEFINITION.md carries")
        print("  none of them or every artifact is absent. Exit 2; a gate that examined nothing")
        print("  has not passed.")
        return 2

    print(f"  DEFINITION.md checked against the committed artifacts of the rounds it cites\n")
    print(f"    {'assertion':>24}{'in the doc':>12}{'in the artifact':>17}   round   verdict")
    bad, missing = [], []
    for label in ASSERTIONS:
        tv, rnd = truth.get(label, (None, "?"))
        cv = claimed.get(label)
        if cv is None:
            missing.append(label)
            print(f"    {label:>24}{'NOT FOUND':>12}{str(tv):>17}   {rnd:<7} ⚠ claim absent from doc")
            continue
        if tv is None:
            print(f"    {label:>24}{cv:>12g}{'artifact absent':>17}   {rnd:<7} ⚠ UNEVALUABLE")
            continue
        ok = same(cv, tv)
        if not ok:
            bad.append((label, cv, tv, rnd))
        print(f"    {label:>24}{cv:>12g}{tv:>17}   {rnd:<7} {'ok' if ok else '⛔ MISMATCH'}")

    # ---- positive control: the comparison must reject a wrong value ------------------------------
    probe = evaluable[0]
    tv = float(truth[probe][0])
    caught = (not same(tv + 1.0, tv)) and same(tv, tv)
    print(f"\n  POSITIVE CONTROL  `same()` -- THE comparison this gate rules with, not a restatement")
    print(f"    of it -- is handed `{probe}` = {tv + 1:g} against the artifact's {tv:g} and must")
    print(f"    REJECT, and handed {tv:g} against {tv:g} and must ACCEPT: "
          f"{'caught' if caught else 'MISSED'}  {'PASS' if caught else 'FAIL'}")

    print(f"\n  PROXY LEDGER — {len(evaluable)} of {len(ASSERTIONS)} assertions were evaluable; "
          f"{len(missing)} are not in the document.")
    print(f"    This check is sound in ONE direction: a failure means the document is wrong about")
    print(f"    the record. A pass does NOT certify the document — every prose claim not in the")
    print(f"    assertion table is unchecked BY CONSTRUCTION, and that remainder is why this line")
    print(f"    prints a count instead of a clean bill.")

    if not caught:
        print("\n  FAIL: the comparison could not reject a planted wrong value.")
        return 1
    if bad:
        print(f"\n  FAIL: {len(bad)} claim(s) in DEFINITION.md no longer match their artifact:")
        for label, cv, tv, rnd in bad:
            print(f"    {label}: document says {cv:g}, {rnd} says {tv}")
        print("  Either the document drifted or a round was re-run. Fix the one that is wrong —")
        print("  and note the artifact is the authority, because it recomputes and prose does not.")
        return 1
    if missing:
        print(f"\n  FAIL: {len(missing)} assertion(s) are declared here but absent from the")
        print(f"  document: {missing}. An assertion that cannot be located is not a pass —")
        print(f"  it means the claim was deleted or reworded and this gate went blind to it.")
        return 1
    print(f"\n  PASS: every locatable claim in DEFINITION.md is re-derived from a committed artifact.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
