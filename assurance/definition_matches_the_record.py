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
        # ⚠ REPOINTED 2026-08-04 (R444). This derived R360's 4 = |②admits| - |②∧③admits|, which
        #    is what the row said while ③ was a hand-written list. R444 corrected ③ to be derived
        #    from `select_core.py` and the row now carries 14. Re-anchoring to the old text would
        #    re-assert a superseded number; deleting the anchor would lose the check. So it points
        #    at R444's artifact, which is what the document now states.
        d444_ = next(A24.glob("R444_*"), None)
        f444_ = (d444_ / "results" / "r444_decision.json") if d444_ else None
        a444_ = json.loads(f444_.read_text()) if (f444_ and f444_.exists()) else None
        out["clause3_excludes"] = ((a444_["clause3_excludes_after"], "R444") if a444_
                                   else (len(a["clause2_admits"]) - len(a["clause23_admits"]), "R360"))[0], \
            ("R444" if a444_ else "R360")
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
    # R430 -- the decomposition that OVERTURNED R429's attribution. Anchored because a retraction
    # is the one paragraph a reader most needs to be able to check, and because R429's own numbers
    # (r429_inside / meangap / half) SURVIVE it unchanged: the measurement stood, the attribution
    # fell. Keeping both sets anchored in the same document is what makes that distinction legible
    # rather than a claim about my own honesty.
    d430 = next(A24.glob("R430_*"), None)

    def r430(stem):
        f = (d430 / "results" / stem) if d430 else None
        return json.loads(f.read_text()) if f and f.exists() else None
    a = r430("r430_decomposition.json")
    if a and a.get("world") != "UNVERIFIED":
        for cell, key in (("CONV/PERM", "r430_convperm"), ("CONV/ANLY", "r430_convanly"),
                          ("INTER/PERM", "r430_interperm"), ("INTER/ANLY", "r430_interanly")):
            out[key] = (a["hits"][cell], "R430")
    else:
        for k in ("r430_convperm", "r430_convanly", "r430_interperm", "r430_interanly"):
            out[k] = (None, "R430")
    a = r430("r430_headline_under_both.json")
    if a and a.get("world") != "UNVERIFIED":
        out["r430_conv_delta"] = (f"{a['cells']['CONV']['delta']:+.4f}", "R430")
        out["r430_conv_p"] = (f"{a['cells']['CONV']['p']:.4f}", "R430")
    else:
        for k in ("r430_conv_delta", "r430_conv_p"):
            out[k] = (None, "R430")
    a = r430("r430_rank_stability.json")
    if a and a.get("world") != "UNVERIFIED":
        out["r430_wmoves"] = (a["weighting_moves"], "R430")
        out["r430_nullmed"] = (int(a["null_moves_median"]), "R430")
        out["r430_pos4"] = (a["null_position_freq"].get("4"), "R430")
    else:
        for k in ("r430_wmoves", "r430_nullmed", "r430_pos4"):
            out[k] = (None, "R430")
    # R431 -- the size-confound round. Anchored because it CORRECTS a scope a reader would
    # otherwise carry from R430: the ~0.013 is the gap on the NULL, and the gap on the EXCESS is
    # 10x smaller. A correction that is not re-derivable is the one sentence nobody can check.
    d431 = next(A24.glob("R431_*"), None)

    def r431(stem):
        f = (d431 / "results" / stem) if d431 else None
        return json.loads(f.read_text()) if f and f.exists() else None
    a = r431("r431_size_confound.json")
    if a and a.get("world") != "UNVERIFIED":
        out["r431_maxgap"] = (f"{max(abs(r['gap_raw']) for r in a['gap_rows']):.4f}", "R431")
        out["r431_surv"] = (a["cells_surviving"], "R431")
        out["r431_cells"] = (a["cells_tested"], "R431")
        out["r431_stdin"] = (a["std_inside"], "R431")
    else:
        for k in ("r431_maxgap", "r431_surv", "r431_cells", "r431_stdin"):
            out[k] = (None, "R431")
    # R432 -- the GPU gate. Anchored because the register line it edits is the one a later round
    # will ACT on, and a bar stated in prose that no artifact re-derives is how an expensive round
    # gets pointed at the wrong number.
    d432 = next(A24.glob("R432_*"), None)

    def r432(stem):
        f = (d432 / "results" / stem) if d432 else None
        return json.loads(f.read_text()) if f and f.exists() else None
    a = r432("r432_headroom.json")
    if a and a.get("world") != "UNVERIFIED":
        c = a["cells"]["INTER"]
        out["r432_best"] = (f"{c['best']:.4f}", "R432")
        out["r432_oracle"] = (f"{c['oracle']:.4f}", "R432")
        out["r432_head"] = (f"{c['headroom']:+.4f}", "R432")
        out["r432_floor"] = (f"{c['floor']:.4f}", "R432")
        out["r432_over"] = (f"{c['oracle'] - a['length_rule']:+.4f}", "R432")
    else:
        for k in ("r432_best", "r432_oracle", "r432_head", "r432_floor", "r432_over"):
            out[k] = (None, "R432")
    # R433 -- clause ②'s subject, W-LOSES. Anchored because this is the row a reader will treat as
    # settling the transport question, and a settled-looking row that no artifact re-derives is the
    # exact object this gate exists to prevent.
    d433 = next(A24.glob("R433_*"), None)

    def r433(stem):
        f = (d433 / "results" / stem) if d433 else None
        return json.loads(f.read_text()) if f and f.exists() else None
    a = r433("r433_clause2_subject.json")
    if a and a.get("world") != "UNVERIFIED":
        c = a["cells"]["INTER"]
        out["r433_gen"] = (f"{c['gen']:.4f}", "R433")
        out["r433_length"] = (f"{c['length']:.4f}", "R433")
        out["r433_delta"] = (f"{c['delta_vs_length']:+.4f}", "R433")
        out["r433_mde"] = (f"{c['mde']:.4f}", "R433")
        out["r433_neutral"] = (f"{c['neutral_gap']:+.4f}", "R433")
        out["r433_nmde"] = (f"{c['neutral_mde']:.4f}", "R433")
        out["r433_n"] = (a["n_interactions"], "R433")
        out["r433_shammde"] = (f"{a['gate']['mde_sham']:.4f}", "R433")
    else:
        for k in ("r433_gen", "r433_length", "r433_delta", "r433_mde", "r433_neutral",
                  "r433_nmde", "r433_n", "r433_shammde"):
            out[k] = (None, "R433")
    # R434 -- the emptiness, and the ORACLE numbers that make it a measurement. The oracle values
    # are anchored deliberately: without them "0 of 7" is silence, and a reader has no way to tell
    # the two apart from the prose alone.
    d434 = next(A24.glob("R434_*"), None)
    f434 = (d434 / "results" / "r434_utility_floor.json") if d434 else None
    a = json.loads(f434.read_text()) if (f434 and f434.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r434_sat2"] = (len(a["sat2"]), "R434")
        out["r434_useful"] = (len(a["useful"]), "R434")
        out["r434_arms"] = (len(a["cells"]), "R434")
        out["r434_n"] = (a["n_interactions"], "R434")
        out["r434_len"] = (f"{a['acc']['length']:.4f}", "R434")
        out["r434_best"] = (f"{max(c['acc'] for c in a['cells']):.4f}", "R434")
    else:
        for k in ("r434_sat2", "r434_useful", "r434_arms", "r434_n", "r434_len", "r434_best"):
            out[k] = (None, "R434")
    # R435 -- the saturation numbers. m* is the load-bearing one: it is what makes the bar a bar
    # rather than a function of how many rules someone tried, and a prose claim of "it saturates"
    # that no artifact re-derives is exactly the shape this gate exists to catch.
    d435 = next(A24.glob("R435_*"), None)
    f435 = (d435 / "results" / "r435_bar_stability.json") if d435 else None
    a = json.loads(f435.read_text()) if (f435 and f435.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r435_mstar"] = (a["m_star"], "R435")
        out["r435_family"] = (len(a["family"]), "R435")
        out["r435_resid"] = (f"{a['residual_climb_at_m_star']:+.4f}", "R435")
        out["r435_floor"] = (f"{a['data_floor']:.4f}", "R435")
        out["r435_lift"] = (f"{a['curve'][-1]['lift']:+.4f}", "R435")
    else:
        for k in ("r435_mstar", "r435_family", "r435_resid", "r435_floor", "r435_lift"):
            out[k] = (None, "R435")
    # R436 -- the split. `excluded_at_J` is the load-bearing number: it is what turns "④ excludes
    # 22 arms" from a claim about cores into a claim about a judge the definition does not name.
    d436 = next(A24.glob("R436_*"), None)
    f436 = (d436 / "results" / "r436_clause4_at_home.json") if d436 else None
    a = json.loads(f436.read_text()) if (f436 and f436.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        top = max(a["cells"], key=lambda c: c["a2"] if "08b" not in c["arm"] else -1)
        out["r436_bar"] = (f"{a['bar']:.4f}", "R436")
        out["r436_excl"] = (len(a["excluded"]), "R436")
        out["r436_arms"] = (a["n_arms"], "R436")
        out["r436_exclJ"] = (len(a["excluded_at_J"]), "R436")
        out["r436_armsJ"] = (a["n_arms_at_J"], "R436")
        out["r436_topd"] = (f"{top['d']:+.4f}", "R436")
        out["r436_topmde"] = (f"{top['mde']:.4f}", "R436")
    else:
        for k in ("r436_bar", "r436_excl", "r436_arms", "r436_exclJ", "r436_armsJ",
                  "r436_topd", "r436_topmde"):
            out[k] = (None, "R436")
    # R437 -- the inversion. Both GAPs and both MDEs are anchored, because the CLAIM is about their
    # SIGNS and a sign that no artifact re-derives is the cheapest thing in this document to get
    # backwards.
    d437 = next(A24.glob("R437_*"), None)
    f437 = (d437 / "results" / "r437_bar_inversion.json") if d437 else None
    a = json.loads(f437.read_text()) if (f437 and f437.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r437_home_bar2"] = (f"{a['home']['bar2']:.4f}", "R437")
        out["r437_home_bar4"] = (f"{a['home']['bar4']:.4f}", "R437")
        out["r437_home_gap"] = (f"{a['home']['gap_paired']:+.4f}", "R437")
        out["r437_home_mde"] = (f"{a['home']['mde']:.4f}", "R437")
        out["r437_sec_bar2"] = (f"{a['second']['bar2']:.4f}", "R437")
        out["r437_sec_bar4"] = (f"{a['second']['bar4']:.4f}", "R437")
        out["r437_sec_gap"] = (f"{a['second']['gap']:+.4f}", "R437")
        out["r437_sec_mde"] = (f"{a['second']['mde']:.4f}", "R437")
    else:
        for k in ("r437_home_bar2", "r437_home_bar4", "r437_home_gap", "r437_home_mde",
                  "r437_sec_bar2", "r437_sec_bar4", "r437_sec_gap", "r437_sec_mde"):
            out[k] = (None, "R437")
    # R438 -- the within-release attack. The two RESOLVED gaps and the selection-inflation triple
    # are anchored: the inflation numbers are the ones that would be quietly dropped if the FIXED /
    # RESELECTED choice were ever made silently, which is what the round exists to prevent.
    d438 = next(A24.glob("R438_*"), None)
    f438 = (d438 / "results" / "r438_within_release_flip.json") if d438 else None
    a = json.loads(f438.read_text()) if (f438 and f438.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        fx = {c["n"]: c for c in a["cells"] if c["mode"] == "FIXED"}
        rs = {c["n"]: c for c in a["cells"] if c["mode"] == "RESELECTED"}
        for n in (2, 3, 4):
            out[f"r438_gap{n}"] = (f"{fx[n]['gap']:+.4f}", "R438")
            out[f"r438_mde{n}"] = (f"{fx[n]['mde']:.4f}", "R438")
            out[f"r438_infl{n}"] = (f"{rs[n]['bar4'] - fx[n]['bar4']:+.4f}", "R438")
        out["r438_n2"] = (fx[2]["n_int"], "R438")
        out["r438_n4"] = (fx[4]["n_int"], "R438")
    else:
        for n in (2, 3, 4):
            out[f"r438_gap{n}"] = (None, "R438"); out[f"r438_mde{n}"] = (None, "R438")
            out[f"r438_infl{n}"] = (None, "R438")
        out["r438_n2"] = (None, "R438"); out["r438_n4"] = (None, "R438")
    # R439 -- the reparameterisation test. The PERCENTILE and the distribution MINIMUM are anchored
    # together on purpose: "0.00th percentile" alone is compatible with a degenerate distribution,
    # and it is the gap to the MINIMUM that makes it a statement about reach rather than about ties.
    d439 = next(A24.glob("R439_*"), None)
    f439 = (d439 / "results" / "r439_reparam.json") if d439 else None
    a = json.loads(f439.read_text()) if (f439 and f439.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r439_pct"] = (f"{a['pct']:.2f}", "R439")
        out["r439_subsets"] = (a["n_subsets"], "R439")
        out["r439_below"] = (f"{a['dist_min'] - a['bar4']:.4f}", "R439")
        out["r439_pubpct"] = (f"{a['published_ref_pct']:.1f}", "R439")
    else:
        for k in ("r439_pct", "r439_subsets", "r439_below", "r439_pubpct"):
            out[k] = (None, "R439")
    # R440 -- the fourth table row. COVERAGE is anchored alongside the count, because "0 of 42" is
    # only a count if the space was fully scored; at partial coverage the same string would be a
    # bound wearing a count's clothes, and no reader could tell them apart.
    d440 = next(A24.glob("R440_*"), None)
    f440 = (d440 / "results" / "r440_one_space.json") if d440 else None
    a = json.loads(f440.read_text()) if (f440 and f440.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r440_e4"] = (a["E4"], "R440")
        out["r440_e2"] = (a["E2"], "R440")
        out["r440_arms"] = (a["n_arms"], "R440")
        out["r440_cov"] = (a["n_covered"], "R440")
    else:
        for k in ("r440_e4", "r440_e2", "r440_arms", "r440_cov"):
            out[k] = (None, "R440")
    # R441 -- the size line. `n_with_k` is anchored beside the k=1 count on purpose: "1 arm has
    # k=1" is only informative next to how many arms had a readable k at all, and a document that
    # gave the numerator without the denominator would be stating a bound as a survey.
    d441 = next(A24.glob("R441_*"), None)
    f441 = (d441 / "results" / "r441_size_clause.json") if d441 else None
    a = json.loads(f441.read_text()) if (f441 and f441.exists()) else None
    if a and a.get("world") not in (None, "UNVERIFIED"):
        out["r441_withk"] = (a["n_with_k"], "R441")
        out["r441_k1"] = (len(a.get("k1_arms", [])), "R441")
        out["r441_redundant"] = (a["redundant"], "R441")
    else:
        for k in ("r441_withk", "r441_k1", "r441_redundant"):
            out[k] = (None, "R441")
    # R442 -- the extension. BOTH readings are anchored, because the document now states two and
    # the whole point is that neither may be quoted without saying which produced it. An anchor on
    # only one would let the other drift silently, which is how a contradiction becomes a claim.
    d442 = next(A24.glob("R442_*"), None)
    f442 = (d442 / "results" / "r442_extension.json") if d442 else None
    a = json.loads(f442.read_text()) if (f442 and f442.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r442_impl"] = (len(a["ext_impl"]), "R442")
        out["r442_writ"] = (len(a["ext_writ"]), "R442")
        out["r442_overlap"] = (len(a["overlap_impl_published"]), "R442")
    else:
        for k in ("r442_impl", "r442_writ", "r442_overlap"):
            out[k] = (None, "R442")
    # R443 -- the containment number AND its sham. The sham is anchored because a containment of
    # 0.0779 reads as "low" only next to a zero cross-prompt baseline; without it the same figure
    # would be an opinion, and the round's own kill divided by it and broke.
    d443 = next(A24.glob("R443_*"), None)
    f443 = (d443 / "results" / "r443_core_provenance.json") if d443 else None
    a = json.loads(f443.read_text()) if (f443 and f443.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r443_cont"] = (f"{a['containment']:.4f}", "R443")
        out["r443_sham"] = (f"{a['sham']:.4f}", "R443")
        out["r443_n"] = (a["n_prompts"], "R443")
    else:
        for k in ("r443_cont", "r443_sham", "r443_n"):
            out[k] = (None, "R443")
    # R444 -- the reconciliation. Both the BEFORE and AFTER counts are anchored: a corrected number
    # with no record of what it replaced is how a reconciliation becomes indistinguishable from a
    # number that was always there.
    d444 = next(A24.glob("R444_*"), None)
    f444 = (d444 / "results" / "r444_decision.json") if d444 else None
    a = json.loads(f444.read_text()) if (f444 and f444.exists()) else None
    if a:
        out["r444_after"] = (a["clause3_excludes_after"], "R444")
        out["r444_before"] = (a["clause3_excludes_before"], "R444")
        out["r444_ext_after"] = (a["extension_after"], "R444")
        out["r444_unknown"] = (len(a["unknown_provenance"]), "R444")
    else:
        for k in ("r444_after", "r444_before", "r444_ext_after", "r444_unknown"):
            out[k] = (None, "R444")
    # R445 -- the margin AND its floor, anchored together. A delta without its MDE is exactly the
    # scope error this campaign has retracted most, and here the ratio is 1.07: the number is only
    # honest beside the floor it barely clears.
    d445 = next(A24.glob("R445_*"), None)
    f445 = (d445 / "results" / "r445_gen_vs_clause2.json") if d445 else None
    a = json.loads(f445.read_text()) if (f445 and f445.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        c = a["cells"]
        out["r445_gen"] = (f"{c['gen']['delta']:+.4f}", "R445")
        out["r445_genmde"] = (f"{c['gen']['mde']:.4f}", "R445")
        out["r445_core"] = (f"{c['coval_core']['delta']:+.4f}", "R445")
        out["r445_sham"] = (f"{c['gen_sham']['delta']:+.4f}", "R445")
        out["r445_oracle"] = (f"{a['oracle_delta']:+.4f}", "R445")
        out["r445_n"] = (a["n_prompts"], "R445")
    else:
        for k in ("r445_gen", "r445_genmde", "r445_core", "r445_sham", "r445_oracle", "r445_n"):
            out[k] = (None, "R445")
    # R446 -- the reference sweep. The POINT quantile is anchored beside the ADMITTED share because
    # the 25.8-point gap between them IS the finding; an anchor on only the share would let the
    # comparison that makes it meaningful drift away.
    d446 = next(A24.glob("R446_*"), None)
    f446 = (d446 / "results" / "r446_reference_sweep.json") if d446 else None
    a = json.loads(f446.read_text()) if (f446 and f446.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        c = a["cells"]
        out["r446_gen"] = (f"{100*c['gen']['admitted_share']:.1f}", "R446")
        out["r446_core"] = (f"{100*c['coval_core']['admitted_share']:.1f}", "R446")
        out["r446_genq"] = (f"{100*c['gen']['point_quantile']:.1f}", "R446")
        out["r446_refs"] = (a["n_refs"], "R446")
    else:
        for k in ("r446_gen", "r446_core", "r446_genq", "r446_refs"):
            out[k] = (None, "R446")
    # R470 -- the extension interval. BOTH endpoints are anchored, because the finding is that a
    # single integer was hiding a convention, and anchoring one endpoint would recreate exactly that.
    d470 = next(A24.glob("R470_*"), None)
    f470 = (d470 / "results" / "r470_extension_interval.json") if d470 else None
    a = json.loads(f470.read_text()) if (f470 and f470.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r470_lo"] = (a["ext_unknown_as_excluded"], "R470")
        out["r470_hi"] = (a["ext_unknown_as_admitted"], "R470")
        out["r470_unv"] = (a["ext_unverified_bucket"], "R470")
        out["r470_np"] = (len(a["P"]), "R470")
    else:
        for k in ("r470_lo", "r470_hi", "r470_unv", "r470_np"):
            out[k] = (None, "R470")

    # R469 -- containment's degeneracy. BOTH class means are anchored, because the finding is the
    # SEPARATION and either alone would read as a level rather than as the collapse of a partition.
    d469 = next(A24.glob("R469_*"), None)
    f469 = (d469 / "results" / "r469_containment_degenerate.json") if d469 else None
    a = json.loads(f469.read_text()) if (f469 and f469.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        cl = a["classes"]
        out["r469_exc"] = (f"{cl['EXCLUDED']['mean']:.4f}", "R469")
        out["r469_adm"] = (f"{cl['ADMITTED']['mean']:.4f}", "R469")
        out["r469_unk"] = (f"{cl['UNKNOWN']['mean']:.4f}", "R469")
        out["r469_sep"] = (f"{cl['EXCLUDED']['mean'] - cl['ADMITTED']['mean']:.4f}", "R469")
        out["r469_pos"] = (f"{a['positive_full']:.4f}", "R469")
    else:
        for k in ("r469_exc", "r469_adm", "r469_unk", "r469_sep", "r469_pos"):
            out[k] = (None, "R469")

    # R468 -- the exact join. The RANDOM-pair similarity is anchored with the joined-pair one,
    # because 0.8811 alone is unreadable: the validation is the CONTRAST, on a channel the join was
    # not built from.
    d468 = next(A24.glob("R468_*"), None)
    f468 = (d468 / "results" / "r468_exact_join.json") if d468 else None
    a = json.loads(f468.read_text()) if (f468 and f468.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r468_cov"] = (f"{a['coverage']:.4f}", "R468")
        out["r468_n"] = (a["mapping_size"], "R468")
        out["r468_sim"] = (f"{a['sim_joined']:.4f}", "R468")
        out["r468_rnd"] = (f"{a['sim_random']:.4f}", "R468")
        out["r468_surplus"] = (a["surplus_rubric"], "R468")
    else:
        for k in ("r468_cov", "r468_n", "r468_sim", "r468_rnd", "r468_surplus"):
            out[k] = (None, "R468")

    # R467 -- the content join. The CROSS-FILE control flag is anchored, not just the coverage,
    # because coverage 0.0000 is SILENCE unless that control passed and it did not.
    d467 = next(A24.glob("R467_*"), None)
    f467 = (d467 / "results" / "r467_id_join.json") if d467 else None
    a = json.loads(f467.read_text()) if (f467 and f467.exists()) else None
    if a:
        out["r467_cov"] = (f"{a['coverage_rubric_to_cmp']:.4f}", "R467")
        out["r467_inter"] = (a["id_intersection"], "R467")
        out["r467_self"] = (f"{a['self_unique_rubric']:.4f}", "R467")
    else:
        for k in ("r467_cov", "r467_inter", "r467_self"):
            out[k] = (None, "R467")

    # R466 -- the id-space join. The INTERSECTION is anchored with both population sizes, because
    # "0" alone reads as an absence rather than as two populations that cannot meet.
    d466 = next(A24.glob("R466_*"), None)
    f466 = (d466 / "results" / "r466_unit_equality.json") if d466 else None
    a = json.loads(f466.read_text()) if (f466 and f466.exists()) else None
    if a:
        out["r466_rub"] = (a["rubric_ids"], "R466")
        out["r466_rank"] = (a["ranking_ids"], "R466")
        out["r466_inter"] = (a["id_intersection"], "R466")
        out["r466_anchor"] = (f"{a['core_containment']:.4f}", "R466")
    else:
        for k in ("r466_rub", "r466_rank", "r466_inter", "r466_anchor"):
            out[k] = (None, "R466")

    # R465 -- clause ③'s type. The BASELINE is anchored with the collision rate, because the round
    # explicitly declines to claim a difference between them and an unanchored baseline would let a
    # later reader restore that claim by drift.
    d465 = next(A24.glob("R465_*"), None)
    f465 = (d465 / "results" / "r465_clause_three_type.json") if d465 else None
    a = json.loads(f465.read_text()) if (f465 and f465.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r465_ncol"] = (a["n_collided"], "R465")
        out["r465_nchoice"] = (a["n_choice"], "R465")
        out["r465_rate"] = (f"{a['collision_choice']:.4f}", "R465")
        out["r465_base"] = (f"{a['baseline_labelfree_pair']:.4f}", "R465")
    else:
        for k in ("r465_ncol", "r465_nchoice", "r465_rate", "r465_base"):
            out[k] = (None, "R465")

    # R464 -- clause ①'s extension. The RANDOM-draw boundary is anchored beside the worst-subset
    # exclusion, because "excluded" is only readable if a draw from the reference process itself
    # sits ON the boundary -- the two numbers are one control and must not drift apart.
    d464 = next(A24.glob("R464_*"), None)
    f464 = (d464 / "results" / "r464_clause_one.json") if d464 else None
    a = json.loads(f464.read_text()) if (f464 and f464.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r464_worst"] = (f"{a['arms']['rubric_worst']['gap']:.4f}", "R464")
        out["r464_core"] = (f"{a['arms']['coval_core']['gap']:.4f}", "R464")
        out["r464_random"] = (f"{a['arms']['rubric_random']['gap']:.4f}", "R464")
        out["r464_mde"] = (f"{a['arms']['rubric_worst']['mde']:.4f}", "R464")
    else:
        for k in ("r464_worst", "r464_core", "r464_random", "r464_mde"):
            out[k] = (None, "R464")

    # R463 -- the third block. The CLAUSE-② marker count is anchored beside the flag totals,
    # because it is a DIFFERENT statistic from the forced one and merging them is the exact error
    # the round caught in its own verdict branch.
    d463 = next(A24.glob("R463_*"), None)
    f463 = (d463 / "results" / "r463_ordering_forced.json") if d463 else None
    a = json.loads(f463.read_text()) if (f463 and f463.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r463_decl"] = (a["declared_differences"], "R463")
        out["r463_cov"] = (a["coverage"], "R463")
        out["r463_markers"] = (a["n_markers"], "R463")
        out["r463_clause2"] = (max(a["markers_per_section"].values()), "R463")
    else:
        for k in ("r463_decl", "r463_cov", "r463_markers", "r463_clause2"):
            out[k] = (None, "R463")

    # R462 -- the ordering test. BOTH block sizes are anchored, because "0 of 32 vs 0 of 18" is the
    # comparison and a bare "0 flagged" would read as a clean bill rather than as a refuted ordering.
    d462 = next(A24.glob("R462_*"), None)
    f462 = (d462 / "results" / "r462_ordering.json") if d462 else None
    a = json.loads(f462.read_text()) if (f462 and f462.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r462_old"] = (a["n_declared_old"], "R462")
        out["r462_new"] = (a["n_declared_new"], "R462")
        out["r462_cov"] = (a["coverage"], "R462")
        out["r462_total"] = (len(ASSERTIONS), "LIVE")   # same live rule as r461_anchors
    else:
        for k in ("r462_old", "r462_new", "r462_cov", "r462_total"):
            out[k] = (None, "R462")

    # R461 -- the comparator-scope gate. The FLAGGED-at-widest is anchored with the coverage, so a
    # future reader cannot read "0 flagged" as "the document is clean" -- the two numbers mean
    # different things and the round's own lesson is that separating them is the point.
    d461 = next(A24.glob("R461_*"), None)
    f461 = (d461 / "results" / "r461_comparator_scope.json") if d461 else None
    a = json.loads(f461.read_text()) if (f461 and f461.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r461_declared"] = (a["sweep"][-1]["n_declared_diff"], "R461")
        out["r461_flagged_tight"] = (a["sweep"][0]["n_flagged"], "R461")
        # ⛔ LIVE, NOT SNAPSHOT. Retraction 272 said to anchor a self-referential count
        #    "against the instrument's LIVE state rather than a snapshot taken while
        #    writing" -- and then compared artifact-snapshot to document-snapshot, which
        #    agree with each other while both go stale. It drifted again within two rounds
        #    (261 -> 264). The anchor count is now read from the LIVE table, so adding any
        #    anchor FORCES the sentence to be updated instead of silently passing.
        out["r461_coverage"] = (a["declared"], "R461")
        out["r461_anchors"] = (len(ASSERTIONS), "LIVE")
    else:
        for k in ("r461_declared", "r461_flagged_tight", "r461_coverage", "r461_anchors"):
            out[k] = (None, "R461")

    # R460 -- the comparator census. The MINIMUM is anchored with the IQR, because the finding
    # narrows a number while PRESERVING the claim, and only the minimum shows the claim survives.
    d460 = next(A24.glob("R460_*"), None)
    f460 = (d460 / "results" / "r460_comparator_census.json") if d460 else None
    a = json.loads(f460.read_text()) if (f460 and f460.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        q = a["quantiles"]
        out["r460_min"] = (f"{q['0']:.4f}" if "0" in q else f"{q[0]:.4f}", "R460")
        out["r460_med"] = (f"{q['50']:.4f}" if "50" in q else f"{q[50]:.4f}", "R460")
        out["r460_iqr"] = (f"{a['iqr']:.4f}", "R460")
        out["r460_strength"] = (f"{a['corr_rho_strength']:.4f}", "R460")
        out["r460_ncomp"] = (a["n_comparators"], "R460")
    else:
        for k in ("r460_min", "r460_med", "r460_iqr", "r460_strength", "r460_ncomp"):
            out[k] = (None, "R460")

    # R459 -- the partner check. d_gen is anchored WITH both components, because the finding is
    # that the DIFFERENCE beats its parts, and a lone rho would lose the comparison that shows it.
    d459 = next(A24.glob("R459_*"), None)
    f459 = (d459 / "results" / "r459_partner.json") if d459 else None
    a = json.loads(f459.read_text()) if (f459 and f459.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        q = a["quantities"]
        out["r459_dgen"] = (f"{q['d_gen']['rho_full']:.4f}", "R459")
        out["r459_core"] = (f"{q['core']['rho_full']:.4f}", "R459")
        out["r459_sham"] = (f"{q['sham']['rho_full']:.4f}", "R459")
        out["r459_delta"] = (f"{a['delta']:.4f}", "R459")
        out["r459_tuples"] = (a["generic_distinct_tuples"], "R459")
    else:
        for k in ("r459_dgen", "r459_core", "r459_sham", "r459_delta", "r459_tuples"):
            out[k] = (None, "R459")

    # R458 -- explainability. R2 is anchored WITH the positive control, because 0.0384 alone reads
    # as a weak model; only the 0.9170 recovery makes it a statement about the OBJECT.
    d458 = next(A24.glob("R458_*"), None)
    f458 = (d458 / "results" / "r458_explainability.json") if d458 else None
    a = json.loads(f458.read_text()) if (f458 and f458.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r458_r2"] = (f"{a['blocks']['all']['r2']:.4f}", "R458")
        out["r458_share"] = (f"{100*a['blocks']['all']['share_of_ceiling']:.1f}", "R458")
        out["r458_pos"] = (f"{a['controls']['positive_r2']:.4f}", "R458")
        out["r458_nfeat"] = (len(a["features"]), "R458")
        cr = next(b for b in a["both_arms"] if b["feature"] == "core_range")
        out["r458_corerange"] = (f"{cr['r_core']:.4f}", "R458")
    else:
        for k in ("r458_r2", "r458_share", "r458_pos", "r458_nfeat", "r458_corerange"):
            out[k] = (None, "R458")

    # R457 -- reliability. The CONTAMINATED pair is anchored beside the clean one, because the
    # finding is that the sham EXCEEDS the core on the naive statistic, and anchoring only the clean
    # rho would let the reason this round has two estimands drift away.
    d457 = next(A24.glob("R457_*"), None)
    f457 = (d457 / "results" / "r457_reliability.json") if d457 else None
    a = json.loads(f457.read_text()) if (f457 and f457.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r457_clean"] = (f"{a['arm_specific_core_minus_sham']['rho_full']:.4f}", "R457")
        out["r457_sham"] = (f"{a['arms']['sham']['rho_full']:.4f}", "R457")
        out["r457_core"] = (f"{a['arms']['core']['rho_full']:.4f}", "R457")
    else:
        for k in ("r457_clean", "r457_sham", "r457_core"):
            out[k] = (None, "R457")

    # R456 -- the annotator ladder. ALPHA is anchored with the m=16 cell, because the claim is that
    # the gap does NOT resolve and alpha alone would read as a precision note rather than a bound.
    d456 = next(A24.glob("R456_*"), None)
    f456 = (d456 / "results" / "r456_annotators.json") if d456 else None
    a = json.loads(f456.read_text()) if (f456 and f456.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        g16 = next(r for r in a["grid"] if r["m"] == 16)
        out["r456_alpha"] = (f"{a['alpha']:.3f}", "R456")
        out["r456_gap16"] = (f"{g16['gap']:.4f}", "R456")
        out["r456_ratio16"] = (f"{g16['ratio']:.2f}", "R456")
        out["r456_total"] = (a["annotators"]["total"], "R456")
        out["r456_mderatio"] = (f"{a['mde_ratio']:.2f}", "R456")
    else:
        for k in ("r456_alpha", "r456_gap16", "r456_ratio16", "r456_total", "r456_mderatio"):
            out[k] = (None, "R456")

    # R455 -- the strengthened clause. The GAP is anchored WITH the neutral arm, because the claim
    # is "the core specifically", and without `generic`'s unresolved zero the gap would only show
    # that something beats a cross-fitted pick.
    d455 = next(A24.glob("R455_*"), None)
    f455 = (d455 / "results" / "r455_strengthened.json") if d455 else None
    a = json.loads(f455.read_text()) if (f455 and f455.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        c = a["controls"]
        out["r455_gap"] = (f"{a['gap_mean']:.4f}", "R455")
        out["r455_oracle"] = (f"{c['oracle_gap']:.4f}", "R455")
        out["r455_neutral"] = (f"{c['neutral_gap']:.4f}", "R455")
        out["r455_leaky"] = (f"{c['leaky_gap']:.4f}", "R455")
    else:
        for k in ("r455_gap", "r455_oracle", "r455_neutral", "r455_leaky"):
            out[k] = (None, "R455")

    # R454 -- breadth saturation. The PLATEAU sd is anchored with the rise, because "saturates" is
    # a claim about both and either alone would let the shape drift.
    d454 = next(A24.glob("R454_*"), None)
    f454 = (d454 / "results" / "r454_breadth.json") if d454 else None
    a = json.loads(f454.read_text()) if (f454 and f454.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r454_pos8"] = (f"{a['pos_curve'][0]:.4f}", "R454")
        out["r454_pos12"] = (f"{a['pos_curve'][2]:.4f}", "R454")
        out["r454_plateau"] = (f"{a['plateau_sd_W12_16']:.4f}", "R454")
        out["r454_fams"] = (a["n_prompt_blind_families_with_breadth"], "R454")
    else:
        for k in ("r454_pos8", "r454_pos12", "r454_plateau", "r454_fams"):
            out[k] = (None, "R454")

    # R453 -- the hold-out. The held-out share is anchored WITH the core's half-sample bar, because
    # the claim is the position BETWEEN floor and core and either endpoint alone lets it drift.
    d453 = next(A24.glob("R453_*"), None)
    f453 = (d453 / "results" / "r453_holdout.json") if d453 else None
    a = json.loads(f453.read_text()) if (f453 and f453.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r453_best"] = (f"{a['held_out']['best']['mean']:.4f}", "R453")
        out["r453_corehalf"] = (f"{a['core_halfsample_share']:.4f}", "R453")
        out["r453_g0"] = (f"{a['held_out']['g0']['mean']:.4f}", "R453")
        out["r453_win"] = (f"{100*a['top_subset_win_share']['holdout']:.2f}", "R453")
    else:
        for k in ("r453_best", "r453_corehalf", "r453_g0", "r453_win"):
            out[k] = (None, "R453")

    # R452 -- the oracle's concentration. Real AND synthetic are anchored together, because the
    # claim is the RATIO and either number alone would let the comparison drift.
    d452 = next(A24.glob("R452_*"), None)
    f452 = (d452 / "results" / "r452_oracle_excess.json") if d452 else None
    a = json.loads(f452.read_text()) if (f452 and f452.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r452_eff"] = (f"{a['eff_winners_real']:.1f}", "R452")
        out["r452_syn"] = (f"{a['eff_winners_synthetic']:.1f}", "R452")
        out["r452_top1"] = (f"{100*a['top1_win_share']:.2f}", "R452")
        out["r452_fixed"] = (f"{a['best_fixed_mean']:.4f}", "R452")
    else:
        for k in ("r452_eff", "r452_syn", "r452_top1", "r452_fixed"):
            out[k] = (None, "R452")

    # R451 -- the ball. The ORACLE is anchored beside `gen`, because the pair IS the finding: a zero
    # without its ceiling is silence, and anchoring only the zero would let that ceiling drift away.
    d451 = next(A24.glob("R451_*"), None)
    f451 = (d451 / "results" / "r451_disjoint.json") if d451 else None
    a = json.loads(f451.read_text()) if (f451 and f451.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r451_gen"] = (f"{a['only_content_driven_disjoint']['share']:.4f}", "R451")
        out["r451_oracle"] = (f"{a['oracle_share']:.4f}", "R451")
        out["r451_generic"] = (f"{a['best_hindsight_free']['share']:.4f}", "R451")
    else:
        for k in ("r451_gen", "r451_oracle", "r451_generic"):
            out[k] = (None, "R451")

    # R450 -- the neighbourhood. The eta² SPLIT is anchored, not the individual shares, because the
    # finding is that one coordinate governs and the other does not; anchoring a share alone would
    # let the contrast that constitutes it drift.
    d450 = next(A24.glob("R450_*"), None)
    f450 = (d450 / "results" / "r450_neighbourhood.json") if d450 else None
    a = json.loads(f450.read_text()) if (f450 and f450.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        out["r450_eta_r"] = (f"{100*a['eta2_r']:.1f}", "R450")
        out["r450_eta_a"] = (f"{100*a['eta2_a']:.1f}", "R450")
        br = {str(k): v for k, v in a["by_r"].items()}
        out["r450_r0"] = (f"{br['0'][0]:.4f}", "R450")
        out["r450_r3"] = (f"{br['3'][0]:.4f}", "R450")
        out["r450_d0"] = (f"{a['share_d0']:.4f}", "R450")
        out["r450_selfshare"] = (f"{a['anchors']['class_self_share']:.4f}", "R450")
    else:
        for k in ("r450_eta_r", "r450_eta_a", "r450_r0", "r450_r3", "r450_d0",
                  "r450_selfshare"):
            out[k] = (None, "R450")

    # R449 -- the split verdict. The SHARED-VARIANCE bound is anchored, not the correlation, because
    # the claim is "at most ~2%" and a bound is what the round licenses.
    d449 = next(A24.glob("R449_*"), None)
    f449 = (d449 / "results" / "r449_axis_or_reparameterisation.json") if d449 else None
    a = json.loads(f449.read_text()) if (f449 and f449.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        pv = a["paired_real_vs_sham"]["all_pairs"]
        out["r449_sham_delta"] = (f"{pv['pooled_delta']:+.4f}", "R449")
        out["r449_npos"] = (pv["n_positive"], "R449")
        out["r449_rho"] = (f"{a['partial_vs_score_gap']['all_pairs']['rho']:+.4f}", "R449")
        out["r449_shared"] = (f"{100*a['partial_vs_score_gap']['all_pairs']['max_shared_var']:.1f}",
                              "R449")
        out["r449_pairs"] = (a["n_judge_pairs"], "R449")
    else:
        for k in ("r449_sham_delta", "r449_npos", "r449_rho", "r449_shared", "r449_pairs"):
            out[k] = (None, "R449")

    # R448 -- the mechanism behind the inversion. The two DELTAS-vs-pool are anchored rather than
    # the raw X values, because the finding is that one is resolved and the other is not, and an
    # anchor on the levels alone would let that contrast drift.
    d448 = next(A24.glob("R448_*"), None)
    f448 = (d448 / "results" / "r448_regression_null.json") if d448 else None
    a = json.loads(f448.read_text()) if (f448 and f448.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        x = a["X"]["all_pairs"]
        out["r448_gen_shift"] = (f"{a['observed']['gen']['shift']:+.4f}", "R448")
        out["r448_core_shift"] = (f"{a['observed']['coval_core']['shift']:.4f}", "R448")
        out["r448_gen_pool"] = (f"{x['gen_vs_pool']['delta']:+.4f}", "R448")
        out["r448_pool_x"] = (f"{x['X_pool16']:.4f}", "R448")
    else:
        for k in ("r448_gen_shift", "r448_core_shift", "r448_gen_pool", "r448_pool_x"):
            out[k] = (None, "R448")

    # R447 -- the judge sweep that corrected R301. Both judges' shares for BOTH arms are anchored,
    # because the finding is the INVERSION and an anchor on one arm at one judge would let the
    # comparison that constitutes it drift away.
    d447 = next(A24.glob("R447_*"), None)
    f447 = (d447 / "results" / "r447_judge_sweep.json") if d447 else None
    a = json.loads(f447.read_text()) if (f447 and f447.exists()) else None
    if a and a.get("world") != "UNVERIFIED":
        c = a["cells"]
        out["r447_core8"] = (f"{100*c['coval_core']['share_08b']:.1f}", "R447")
        out["r447_gen8"] = (f"{100*c['gen']['share_08b']:.1f}", "R447")
        out["r447_refs"] = (a["n_refs"], "R447")
    else:
        for k in ("r447_core8", "r447_gen8", "r447_refs"):
            out[k] = (None, "R447")
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
    "clause3_excludes":      r"no prompt labels \| \*\*(\d+) of 42\*\*",
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
    # ⛔ TIGHTENED 2026-08-04. This pattern was `against an MDE of (\d\.\d+)\*\*` -- a phrase
    #    the document now uses TWICE, because R433 reports its neutral gap the same way. The
    #    gate then read R433's 0.0140 and reported R368 as drifted: a FALSE FAILURE against a
    #    document that was correct. A loose anchor does not just miss, it MISATTRIBUTES -- and
    #    this one would have sent me to "fix" a row that was right. Every anchor must carry
    #    enough of its own sentence to be unique in a document that keeps growing.
    "transport_mde":         r"size-matched random\s+draw, by \*\*[+\-][\d.]+ against an MDE of (\d\.\d+)\*\*",
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
    "r447_core8": r"admits `coval_core` under \*\*([\d.]+)%\*\* of its own",
    "r447_gen8":  r"and `gen` under \*\*([\d.]+)%\*\*",
    "r447_refs":  r"over all \*\*([\d,]+)\*\* references judged by 0\.8B",
    "r448_gen_shift":  r"`gen` rises\s+\*\*([+\-\d.]+)\*\* in quantile",
    # MINUS is the U+2212 typographic character in prose and ASCII '-' in json floats. Written
    # once, here, because getting it wrong by hand is now a 3-time defect.
    "r448_core_shift": r"while `coval_core`'s \*\*([\u2212\-][\d.]+)\*\* survives only",
    "r448_gen_pool":   r"\(Δ \*\*([+\-\d.]+)\*\*, MDE 0\.0143, RESOLVED\)",
    "r448_pool_x":     r"the\s+reference pool's \*\*([\d.]+)\*\*",
    "r449_sham_delta": r"sham, pooled \*\*([+\u2212\-][\d.]+)\*\*",
    "r449_npos":       r"\*\*(\d+) of 5\*\*\s*\n?\s*arms beat their own wrong-prompt sham",
    "r449_rho":        r"corr\(ΔX, ΔA2\) = \*\*([+\u2212\-][\d.]+)\*\*",
    "r449_shared":     r"share \*\*at most ~([\d.]+)%\*\* of their",
    "r449_pairs":      r"`n_judge_pairs = (\d+)`",
    "r450_eta_r":      r"by `r` ([\d.]+)%, by",
    "r450_eta_a":      r"`a` ([\d.]+)%\.\*\*",
    "r450_r0":         r"beaten is \*\*([\d.]+) · ",
    "r450_r3":         r"· [\d.]+ · [\d.]+ · ([\d.]+) · [\d.]+\*\* for",
    "r450_d0":         r"reproduces R446's committed \*\*([\d.]+)\*\*",
    "r450_selfshare":  r"own computed self-share \(\*\*([\d.]+)\*\*;",
    "r451_gen":     r"is `gen`, at \*\*([\d.]+)\*\*",
    "r451_oracle":  r"disjoint space clears \*\*([\d.]+)\*\*",
    "r451_generic": r"on `generic` \(([\d.]+)\)",
    "r452_eff":   r"distinct winners is \*\*([\d.]+)\*\* of 1,820",
    "r452_syn":   r"no-structure baseline gives \*\*([\d.]+)\*\* effective",
    "r452_top1":  r"wins\s*\n?\*\*([\d.]+)%\*\* of all prompts",
    "r452_fixed": r"`best fixed ([\d.]+)`",
    "r453_best":     r"it reaches \*\*([\d.]+)\*\* \[",
    "r453_corehalf": r"own half-sample bar of \*\*([\d.]+)\*\*",
    "r453_g0":       r"destroyed-objective g=0 at\s*\n?\*\*([\d.]+)\*\*",
    "r453_win":      r"33\.47% \(train\) → \*\*([\d.]+)%\*\*",
    "r454_pos8":    r"core is \*\*([\d.]+) · [\d.]+ · [\d.]+ · [\d.]+ ·\s*\n?[\d.]+\*\* for `W = 8",
    "r454_pos12":   r"core is \*\*[\d.]+ · [\d.]+ · ([\d.]+) · [\d.]+ ·\s*\n?[\d.]+\*\* for `W = 8",
    "r454_plateau": r"sd over W=12…16 = \*\*([\d.]+)\*\*",
    "r454_fams":    r"`n_prompt_blind_families_with_breadth = (\d+)`",
    "r455_gap":     r"clears that stronger bar by \*\*\+([\d.]+)\*\*",
    "r455_oracle":  r"clears the same baseline by \*\*\+([\d.]+)\*\*",
    "r455_neutral": r"`generic` sits at \*\*([\u2212\-][\d.]+) \[",
    "r455_leaky":   r"IN-FOLD baseline gives\s*\n?\+([\d.]+)\*\*",
    "r456_alpha":    r"exponent\s*\n?is α = ([\d.]+), not the",
    "r456_gap16":    r"failing at \*\*m=16\*\* \(gap \*\*\+([\d.]+)\*\*",
    "r456_ratio16":  r"MDE 0\.0104, ratio ([\d.]+)\)",
    "r456_total":    r"max 46, \*\*([\d,]+)\*\* total",
    "r456_mderatio": r"MDE falls just \*\*([\d.]+)×\*\*",
    "r457_clean": r"replicates at\s*\n?\*\*ρ_full = ([\d.]+)\*\*",
    "r457_sham":  r"sham scores ([\d.]+) — HIGHER",
    "r457_core":  r"HIGHER than\s*\n?the core's ([\d.]+)\*\*",
    "r458_r2":        r"gives out-of-fold \*\*R² = \+([\d.]+)\*\*",
    "r458_share":     r"\*\*([\d.]+)%\*\* of the 0\.8812 ceiling",
    "r458_pos":       r"recovered at\s*\n?R² = \+([\d.]+)\*\*",
    "r458_nfeat":     r"ridge from \*\*(\d+) target-free features\*\*",
    "r458_corerange": r"`core_range` at \*\*\+([\d.]+) /",
    "r459_dgen":   r"`core − generic` replicates at \*\*([\d.]+)\*\*",
    "r459_core":   r"parts \(core ([\d.]+), sham",
    "r459_sham":   r"parts \(core [\d.]+, sham ([\d.]+)\)",
    "r459_delta":  r"\*\*Δ = ([\u2212\-][\d.]+)\*\*, inside",
    "r459_tuples": r"verified in-run at\s*\n?\*\*(\d+)\*\* distinct criterion-index tuple",
    "r460_min":      r"population: min \*\*([\d.]+)\*\*",
    "r460_med":      r"median \*\*([\d.]+)\*\*, p75",
    "r460_iqr":      r"\*\*IQR ([\d.]+)\*\*",
    "r460_strength": r"comparator strength\) = ([\u2212\-][\d.]+)\*\*",
    "r460_ncomp":    r"census of all ([\d,]+)\*\* is free",
    "r461_declared":      r"\*\*(\d+)\*\* declared difference-anchors",
    "r461_flagged_tight": r"and \*\*(\d+)\*\* at the tightest",
    # ⛔ SELF-REFERENTIAL ANCHORS. These two describe the gate that checks them, so adding any
    #    anchor invalidates them -- and it did, one commit after R461 ran. They are KEPT rather than
    #    dropped precisely because the gate then FORCES the update; an unanchored count would have
    #    drifted silently and forever. The lesson is not "avoid self-reference" but "if a document
    #    describes its own checker, that description must be checked BY the checker."
    "r461_coverage":      r"coverage is (\d+) of \d+ anchors",
    "r461_anchors":       r"coverage is \d+ of (\d+) anchors",
    "r462_old": r"flag rate of \*\*0 of (\d+)\*\* at windows",
    "r462_new": r"recent block's \*\*0 of (\d+)\*\*",
    "r462_cov":   r"declaration coverage now (\d+) of \d+",
    "r462_total": r"declaration coverage now \d+ of (\d+)",
    "r463_decl":    r"— (\d+) DECLARED DIFFERENCES",
    "r463_cov":     r"coverage (\d+) of 265",
    "r463_markers": r"max 1 over (\d+) rounds",
    "r463_clause2": r"clause ② carries (\d+) of the 21 round-markers",
    "r464_worst":  r"subset is excluded at\s*\n?\*\*([\u2212\-][\d.]+)\*\*",
    "r464_core":   r"released core sits at\s*\n?\*\*\+([\d.]+)\*\*",
    "r464_random": r"sits at \*\*\+([\d.]+)\*\* with a CI straddling zero",
    "r464_mde":    r"against an MDE of ([\d.]+), while the released core",
    "r465_ncol":    r"criterion set on (\d+) of [\d,]+\*\* prompts",
    "r465_nchoice": r"criterion set on \d+ of ([\d,]+)\*\* prompts",
    "r465_rate":    r"\(rate \*\*([\d.]+)\*\*, seed spread",
    "r465_base":    r"label-free baseline of \*\*([\d.]+)\*\*",
    "r466_rub":    r"rubric-text ids \*\*(\d+)\*\*",
    "r466_rank":   r"ranking ids \*\*(\d+)\*\*",
    "r466_inter":  r"\*\*intersection (\d+)\*\*",
    "r466_anchor": r"reproduces its anchor \(\*\*([\d.]+)\*\*",
    "r467_cov":   r"exact-text join\s*\n?\(\*\*([\d.]+)\*\* after the schema was corrected\)",
    "r467_inter": r"an id join \(intersection \*\*(\d+)\*\*\)",
    "r467_self":  r"passed at \*\*([\d.]+)\*\* both ways",
    "r468_cov":     r"\*\*coverage\s*\n?([\d.]+) \(968 of 968\)",
    "r468_n":       r"coverage\s*\n?[\d.]+ \((\d+) of 968\)",
    "r468_sim":     r"joined pairs are \*\*([\d.]+)\*\* similar",
    "r468_rnd":     r"against \*\*([\d.]+)\*\* for random pairs",
    "r468_surplus": r"⚠ (\d+) rubric-space\s*\n?records have no ranking-space partner",
    "r469_exc": r"\*\*EXCLUDED ([\d.]+)\*\*",
    "r469_adm": r"\*\*ADMITTED ([\d.]+)\*\*",
    "r469_unk": r"class sits at\s*\n?\*\*([\d.]+)\*\*",
    "r469_sep": r"separation ([\u2212\-][\d.]+)\*\*",
    "r469_pos": r"criterion — returns \*\*([\d.]+)\*\*",
    "r470_lo":  r"extension is \*\*(\d+)\*\* under unknown-as-excluded",
    "r470_hi":  r"\*\*(\d+)\*\* under unknown-as-admitted",
    "r470_unv": r"\*\*\d+ confirmed \+ (\d+) unverified\*\*",
    "r470_np":  r"Of the \*\*(\d+)\*\* arms admitted by",
    "r446_gen":  r"resolvedly\*\* better than \*\*([\d.]+)%\*\* of them",
    "r446_core": r"`coval_core` than \*\*([\d.]+)%\*\*",
    "r446_genq": r"would be \*\"better\"\* than \*\*([\d.]+)%\*\* of references",
    "r446_refs": r"Sweeping \*\*all ([\d,]+)\*\* size-4 subsets",
    "r445_gen":    r"`gen` scores\s*\n?\*\*([+\-][\d.]+) \[",
    "r445_genmde": r"against an MDE of ([\d.]+)\*\* — resolved",
    "r445_core":   r"`coval_core` scores \*\*([+\-][\d.]+) \[",
    "r445_sham":   r"fails by \*\*more\*\* \(\*\*([+\-][\d.]+)\*\*\)",
    "r445_oracle": r"clears the reference by \*\*([+\-][\d.]+)\*\*",
    "r445_n":      r"`POOL\[0:4\]` over \*\*(\d+)\*\* prompts",
    "r444_after":     r"excluding \*\*\d+\*\* to \*\*(\d+)\*\* of 42",
    "r444_before":    r"excluding \*\*(\d+)\*\* to \*\*\d+\*\* of 42",
    "r444_ext_after": r"goes from \*\*5\*\* to \*\*(\d+)\*\*",
    # ⚠ SAME BUG AS TWO ROUNDS AGO, AND I WROTE THE WORD AGAIN. The first version matched
    #    `(?:Seven|(\d+))`; "Seven" won the alternation, group(1) was None, and the gate
    #    crashed on `.replace`. A claim meant to be checked has to carry a DIGIT -- an
    #    alternation that can match without capturing is a pattern that fails silently right
    #    up until it fails loudly.
    "r444_unknown":   r"⚠ \*\*(\d+)\*\* arms have provenance the source cannot classify",
    "r443_cont": r"only \*\*([\d.]+)\*\* of its criteria appear verbatim",
    "r443_sham": r"cross-prompt sham of exactly \*\*([\d.]+)\*\*",
    "r443_n":    r"sham of exactly \*\*[\d.]+\*\*, over \*\*(\d+)\*\* prompts",
    "r442_impl":    r"hand-written 4-arm set~~ \| ~~(\d+)~~",
    "r442_writ":    r"now also as implemented\*\* \| \*\*(\d+)\*\*:",
    "r442_overlap": r"only \*\*(\d+) of 5\*\* overlap",
    "r441_withk":     r"of \*\*(\d+)\*\* arms with a k readable",
    "r441_k1":        r"exactly \*\*(\d+)\*\* has k=1",
    "r441_redundant": r"half A removes \*\*(\d+) of \d+\*\* arms",
    "r440_e4":   r"criterion-free rule \| \*\*(\d+) of \d+\*\* \| \*\*MEASURED\*\*",
    "r440_arms": r"criterion-free rule \| \*\*\d+ of (\d+)\*\* \| \*\*MEASURED\*\*",
    "r440_cov":  r"coverage of this space is (\d+)/\d+",
    "r440_e2":   r"prompt-blind set \| \*\*(\d+) of 42\*\*",
    "r439_pct":     r"bar sits at the \*\*([\d.]+)th percentile\*\*",
    "r439_subsets": r"all ([\d,]+) size-4 subsets of ②.s own reference pool",
    "r439_below":   r"\*\*([\d.]+) below the weakest of them\*\*",
    # ⚠ `[\d.]+` swallowed the sentence-ending period and float() choked on "91.7.". A
    #    character class that includes `.` cannot be greedy at the end of a sentence. Same
    #    family as the "seven" bug two rounds ago: a claim meant to be checked has to be
    #    written -- and matched -- in the units the checker reads.
    "r439_pubpct":  r"published reference sits at (\d+\.\d+)",
    "r438_gap2":  r"n=2 \| [\d,]+ \| [\d.]+ \| [\d.]+ \| [\d.]+ \| \*\*([+\-][\d.]+)\*\*",
    "r438_gap3":  r"n=3 \| [\d,]+ \| [\d.]+ \| [\d.]+ \| [\d.]+ \| ([+\-][\d.]+) \|",
    "r438_gap4":  r"n=4 \| [\d,]+ \| [\d.]+ \| [\d.]+ \| [\d.]+ \| \*\*([+\-][\d.]+)\*\*",
    "r438_mde2":  r"n=2 \| [\d,]+ \|(?: [\d.]+ \|){3} \*\*[+\-][\d.]+\*\* \| ([\d.]+)",
    "r438_mde3":  r"n=3 \| [\d,]+ \|(?: [\d.]+ \|){3} [+\-][\d.]+ \| ([\d.]+)",
    "r438_mde4":  r"n=4 \| [\d,]+ \|(?: [\d.]+ \|){3} \*\*[+\-][\d.]+\*\* \| ([\d.]+)",
    "r438_infl2": r"\*\*measured\*\*\s*\n?\(([+\-][\d.]+) / [+\-][\d.]+ / [+\-][\d.]+\)",
    "r438_infl3": r"\*\*measured\*\*\s*\n?\([+\-][\d.]+ / ([+\-][\d.]+) / [+\-][\d.]+\)",
    "r438_infl4": r"\*\*measured\*\*\s*\n?\([+\-][\d.]+ / [+\-][\d.]+ / ([+\-][\d.]+)\)",
    "r438_n2":    r"n=2 \| ([\d,]+) \|",
    "r438_n4":    r"n=4 \| ([\d,]+) \|",
    "r437_home_bar2": r"`random_k4_s0` \*\*([\d.]+)\*\*",
    "r437_home_bar4": r"`min_ttr` \*\*([\d.]+)\*\*",
    "r437_home_gap":  r"\*\*([+\-][\d.]+)\*\* vs MDE [\d.]+ · RESOLVED \| \*\*②\*\*",
    "r437_home_mde":  r"\*\*[+\-][\d.]+\*\* vs MDE ([\d.]+) · RESOLVED \| \*\*②\*\*",
    "r437_sec_bar2":  r"`generic` \*\*([\d.]+)\*\*",
    "r437_sec_bar4":  r"\| `length` \*\*([\d.]+)\*\*",
    "r437_sec_gap":   r"\*\*([+\-][\d.]+)\*\* vs MDE [\d.]+ · RESOLVED \| \*\*④\*\*",
    "r437_sec_mde":   r"\*\*[+\-][\d.]+\*\* vs MDE ([\d.]+) · RESOLVED \| \*\*④\*\*",
    "r436_bar":     r"the bar is \*\*`min_ttr` at ([\d.]+)\*\*",
    "r436_excl":    r"\*\*④ excludes (\d+) of \d+ arms overall",
    "r436_arms":    r"\*\*④ excludes \d+ of (\d+) arms overall",
    "r436_exclJ":   r"arms overall but (\d+) of \d+ at the judge",
    "r436_armsJ":   r"arms overall but \d+ of (\d+) at the judge",
    "r436_topd":    r"sits \*\*([+\-][\d.]+)\*\* above the bar",
    "r436_topmde":  r"above the bar \(MDE \*\*([\d.]+)\*\*\)",
    "r435_mstar":  r"\*\*saturates at m\\\* = (\d+)\*\*",
    "r435_family": r"family of \*\*(\d+)\*\* judge-free rules",
    "r435_resid":  r"BAR\(\|F\|\) − BAR\(6\) = `?([+\-][\d.]+)`?",
    "r435_floor":  r"inside the \*\*([\d.]+)\*\* that the",
    "r435_lift":   r"signal-free family of the same size is \*\*([+\-][\d.]+)\*\*",
    "r434_sat2":   r"\*\*Clause ② admits (\d+) of 7\.",
    "r434_useful": r"And (\d+) of 7 beat the length rule",
    # ⚠ the document said "seven" and this anchor captured the WORD, which the gate then tried
    #    to float() and crashed. A claim that is meant to be checked has to be written in the
    #    units the checker reads -- prose spelling out a number is prose, not an assertion.
    "r434_arms":   r"asked the next question of all\s+\*\*(\d+)\*\* criterion arms",
    "r434_n":      r"one shared population of\s+\*\*([\d,]+) interactions over",
    "r434_len":    r"conversation nor any criteria \(\*\*([\d.]+)\*\*",
    "r434_best":   r"against a best arm of \*\*([\d.]+)\*\*",
    "r433_gen": r"conversation alone — clause ②.s subject, absent from every previous cross-release number — scores \*\*([\d.]+)\*\*",
    "r433_length": r"longest-reply rule at \*\*([\d.]+)\*\*",
    "r433_delta": r"\*\*([+\-][\d.]+) \[[+\-][\d.]+, [+\-][\d.]+\] against its own MDE",
    "r433_mde": r"against its own MDE of ([\d.]+), resolved\*\*",
    "r433_neutral": r"that gap is \*\*([+\-][\d.]+) \[",
    "r433_nmde": r"that gap is \*\*[+\-][\d.]+ \[[+\-][\d.]+, [+\-][\d.]+\] against an MDE of ([\d.]+)\*\*",
    "r433_n": r"on the same ([\d,]+) interactions",
    "r433_shammde": r"buys \*\*less than ([\d.]+)\*\*",
    "r432_best": r"ranks the human.s choice first on \*\*([\d.]+)\*\* of interactions",
    "r432_oracle": r"while \*some\* arm does on \*\*([\d.]+)\*\*",
    "r432_head": r"headroom \*\*([+\-][\d.]+)\*\* against a floor",
    "r432_floor": r"against a floor of \*\*([\d.]+)\*\*",
    "r432_over": r"length rule \(0\.5096\) by ([+\-][\d.]+)\*\*",
    "r431_maxgap":           r"at \*\*at most ([\d.]+)\*\* across all ten pairs",
    "r431_surv":             r"\*\*(\d+) of 30\*\*\s*\n?within-stratum size-association cells",
    "r431_cells":            r"\*\*\d+ of (30)\*\*\s*\n?within-stratum size-association cells",
    "r431_stdin":            r"inside its own floor for only \*\*(\d+) of 10\*\* pairs",
    "r430_convperm":         r"\*\*CONV/PERM (\d+) of 10",
    "r430_convanly":         r"CONV/ANLY (\d+)\s*\n?of 10",
    "r430_interperm":        r"INTER/PERM (\d+) of 10",
    "r430_interanly":        r"INTER/ANLY (\d+) of 10\.\*\*",
    "r430_conv_delta":       r"\*\*CONV ([+\-][\d.]+) \[",
    "r430_conv_p":           r"\*\*CONV [+\-][\d.]+ \[[+\-][\d.]+, [+\-][\d.]+\] p=([\d.]+)\*\*",
    "r430_wmoves":           r"weighting alone moves \*\*(\d+) of 10\*\*",
    "r430_nullmed":          r"moves a \*\*median of (\d+)\*\*",
    "r430_pos4":             r"position 4 moves in (\d+) of 30",
    "r429_meangap":          r"mean ([+\-][\d.]+)\s+against a one-draw band",
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
        # ⛔ NORMALISE AT THE CONVERSION SITE, not in each pattern. Prose uses the typographic
        #    MINUS U+2212 and json floats use ASCII '-'; float() rejects the former. Fixing this
        #    per-anchor failed twice and this is the third occurrence, so it is fixed once, here,
        #    where every present and future anchor passes through.
        got[label] = float(m.group(1).replace(",", "").replace("\u2212", "-")) if m else None
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
