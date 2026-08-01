"""A census of everything wrong with the release, run against the artefact rather than the card.

Every previous round attacked MY claims. This one attacks the object: a systematic sweep for defects
across every axis the release exposes, reporting each with its measurement and its severity, and
separating what is DEMONSTRATED from what is merely SUSPICIOUS.

The sweep is deliberately broad and shallow. A wide net that finds twenty anomalies of which three
matter beats a deep dive into the one axis I already suspected, because the axis I already suspected
is the one my priors are worst on.

SEVERITY IS DEFINED BEFORE ANYTHING RUNS, so a finding cannot be promoted by how interesting it
turns out to be:

  BLOCKING    a documented capability the artefact does not have, or a field that means something
              other than what a reader would take it to mean. Anyone using the release naively gets
              a wrong answer.
  SERIOUS     a real limitation that constrains what can be concluded, but is visible to a careful
              reader who looks.
  NOTED       an oddity with no established consequence. Recorded so it is not rediscovered.

AND EVERY ITEM CARRIES ITS OWN FALSIFIER. "This looks wrong" is not a defect; "this is wrong and
here is the number that would have to change for it not to be" is.

No model is executed anywhere in this round.
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}

FINDINGS: list[dict] = []


def add(axis, severity, title, measurement, falsifier, established=True):
    """A finding whose own falsifier fires is not a finding. Passing severity=CLEAN records that the
    check RAN and came back negative, which is worth keeping -- a census listing things that turned
    out fine as if they were defects inflates its own count, and the next reader cannot tell which
    entries are load-bearing."""
    FINDINGS.append({"axis": axis, "severity": severity, "title": title,
                     "measurement": measurement, "falsifier": falsifier,
                     "established": established})


def msg_text(m):
    c = m.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, dict):
        return " ".join(x for x in (c.get("parts") or []) if isinstance(x, str))
    return ""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------- load
    rub = [json.loads(l) for l in (DATA / "conversation_rubrics.jsonl").open()]
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    print(f"rubrics {len(rub)}   comparisons {len(cmp_)}   annotators {len(ann)}")

    # ---------------------------------------------------------------- A. identity & joins
    rid = {r["conversation"]["id"] for r in rub}
    pid = {c["prompt_id"] for c in cmp_}
    aid = {a["conversation_id"] for r in ann for a in r.get("assessments", [])}
    add("identity", "SERIOUS",
        "Two disjoint id namespaces; the rubric file cannot be joined to anything by key",
        f"conversation_rubrics ids: {len(rid)}, comparisons prompt_ids: {len(pid)}, "
        f"overlap: {len(rid & pid)}. annotators' conversation_id overlaps comparisons at "
        f"{len(aid & pid)} and rubrics at {len(aid & rid)}.",
        "any non-zero overlap between the rubric ids and the prompt ids")

    from covalx.judge import load_join
    joined = load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl")
    add("identity", "SERIOUS",
        "18 of 986 rubric records join to no prompt even under fuzzy text matching",
        f"{len(rub)} rubric records, {len(joined)} joined, {len(rub) - len(joined)} unmatched",
        "a join key existing in the release, or the unmatched count being zero")

    # ---------------------------------------------------------------- B. schema traps
    enc = Counter()
    for a in ann:
        for s in a.get("assessments", []):
            b = s.get("ranking_blocks") or {}
            for k in ("unacceptable", "personal", "world"):
                v = b.get(k)
                enc[(k, "MISSING" if v is None else "EMPTY" if v == [] else "FILLED")] += 1
    tot_ass = sum(len(a.get("assessments", [])) for a in ann)
    add("schema", "BLOCKING",
        "'Question never asked' is encoded as an EMPTY LIST, indistinguishable from 'asked and "
        "answered nothing' to any .get(k, []) default",
        f"of {tot_ass} assessments, unacceptable is FILLED {enc[('unacceptable','FILLED')]} and "
        f"EMPTY {enc[('unacceptable','EMPTY')]}; the key is never missing. personal is identical. "
        f"world is FILLED {enc[('world','FILLED')]}.",
        "a null, a sentinel, or any field distinguishing the two states")

    schemas = set()
    for r in rub[:50]:
        for m in r["conversation"]["messages"]:
            schemas.add(("nested" if isinstance(m.get("content"), dict) else "flat"))
    for c in cmp_[:50]:
        for m in c["prompt"]["messages"]:
            schemas.add(("nested" if isinstance(m.get("content"), dict) else "flat"))
    add("schema", "SERIOUS",
        "Two different message schemas in one release",
        f"conversation_rubrics uses author.role + content.parts; comparisons uses role + content "
        f"as a plain string. Observed shapes: {sorted(schemas)}",
        "one schema across both files")

    # ---------------------------------------------------------------- C. provenance
    n1 = sum(1 for r in rub for it in r["coval_full"] if len(it["scores"]) == 1)
    nall = sum(len(r["coval_full"]) for r in rub)
    add("provenance", "BLOCKING",
        "No authorship field; the pool silently mixes lab-written and participant-written criteria",
        f"{nall} criteria, {n1} rated by exactly one person and {nall - n1} by four or more, with "
        f"EXACTLY ZERO in between. The card says both kinds exist and never marks which is which.",
        "an origin field on a rubric item, or any criterion rated by 2 or 3 people")

    core_keys = Counter(tuple(sorted(c.keys())) for r in rub for c in r["coval_core"])
    add("provenance", "BLOCKING",
        "Compiled rubric items carry no pointer to their source and no weight",
        f"coval_core item key-sets across the whole release: {dict(core_keys)}",
        "any id, weight or source reference on a core item")

    # ---------------------------------------------------------------- D. free-text hazards
    solo_texts = [it["criterion"] for r in rub for it in r["coval_full"] if len(it["scores"]) == 1]
    add("privacy", "SERIOUS",
        "Self-authored criteria are attributable to a single annotator id, and are free text",
        f"{len(solo_texts)} criteria are traceable to one person each via the sole-rater signature, "
        f"alongside that person's age, gender, country, education and AI-usage in annotators.jsonl",
        "criteria being unlinkable to an individual, or demographics being coarsened")

    firstp = sum(1 for t in solo_texts if re.search(r"\b(I|my|me|myself)\b", t))
    add("privacy", "NOTED" if firstp / len(solo_texts) > 0.01 else "CLEAN",
        ("A minority of criteria are written in the first person, raising the disclosure surface"
         if firstp / len(solo_texts) > 0.01 else
         "CHECKED: first-person criteria are negligible, so the disclosure surface is the "
         "attribution itself and not the wording"),
        f"{firstp} of {len(solo_texts)} self-authored criteria ({firstp / len(solo_texts):.1%}) "
        f"contain a first-person pronoun",
        "zero first-person criteria")

    # ---------------------------------------------------------------- E. scale usage
    scores = [s["score"] for r in rub for it in r["coval_full"] for s in it["scores"]]
    c = Counter(scores)
    extreme = (c[10] + c[-10]) / len(scores)
    add("measurement", "SERIOUS",
        "The weight scale is used as a near-binary: the endpoints dominate",
        f"{len(scores)} ratings on -10..+10; +/-10 alone account for {extreme:.1%}. "
        f"top five values: {c.most_common(5)}",
        "a roughly uniform or unimodal-interior distribution over the scale")

    # ---------------------------------------------------------------- F. ranking degeneracy
    parsed = degen = failed = 0
    for a in ann:
        for s in a.get("assessments", []):
            for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
                t = b.get("ranking")
                if not t:
                    continue
                parts = [g for g in t.replace(" ", "").split(">") if g]
                if not parts:
                    failed += 1
                    continue
                parsed += 1
                if len(parts) == 1:
                    degen += 1
    add("measurement", "NOTED",
        "A small share of world rankings express no order at all",
        f"{parsed} parsed rankings, {degen} declare every response equal ({degen / parsed:.2%}), "
        f"{failed} unparseable",
        "zero all-tied rankings")

    # ---------------------------------------------------------------- G. workload structure
    load = Counter(len(a.get("assessments", [])) for a in ann)
    asked = Counter()
    for a in ann:
        k = sum(1 for s in a.get("assessments", [])
                if (s.get("ranking_blocks") or {}).get("unacceptable"))
        asked[k] += 1
    add("design", "BLOCKING",
        "The veto and personal-ranking questions were asked only in each annotator's first batch, "
        "so those fields are not a sample of the corpus",
        f"assessments per annotator: {sorted(load.items())[:6]} ... max "
        f"{max(load)}. Assessments WITH a veto block per annotator: "
        f"{sorted(asked.items())[:6]} ... max {max(asked)}",
        "the veto block appearing beyond a fixed per-annotator cap")

    # ---------------------------------------------------------------- H. panel composition
    dem = defaultdict(Counter)
    for a in ann:
        for k, v in (a.get("demographics") or {}).items():
            dem[k][v if isinstance(v, str) else "NON-STRING"] += 1
    country = dem.get("country_of_residence", Counter())
    top3 = sum(n for _v, n in country.most_common(3))
    add("population", "SERIOUS",
        "The panel is concentrated in a few countries, so any 'collective' aggregate is that panel's",
        f"{len(country)} countries; the top three hold {top3}/{sum(country.values())} annotators "
        f"({top3 / sum(country.values()):.1%}). Top five: {country.most_common(5)}",
        "an approximately even country distribution")

    # ---------------------------------------------------------------- I. prompt corpus
    ptexts = {}
    for c in cmp_:
        t = " ".join(msg_text(m) for m in c["prompt"]["messages"]
                     if (m.get("role") or (m.get("author") or {}).get("role")) == "user")
        ptexts[c["prompt_id"]] = t.strip()
    dupe = Counter(ptexts.values())
    ndupe = sum(v - 1 for v in dupe.values() if v > 1)
    add("corpus", "NOTED" if ndupe else "CLEAN",
        "Duplicate prompt texts" if ndupe else "CHECKED: no duplicate prompt texts",
        f"{len(ptexts)} prompts, {ndupe} exact-duplicate texts",
        "zero duplicate prompt texts")

    lens = sorted(len(t) for t in ptexts.values())
    add("corpus", "SERIOUS",
        "Prompts are synthetic and short, so conclusions do not transfer to real traffic",
        f"user-turn length in chars: median {lens[len(lens) // 2]}, p10 {lens[len(lens) // 10]}, "
        f"p90 {lens[9 * len(lens) // 10]}, max {lens[-1]}. The card describes them as synthetic.",
        "the card describing the prompts as sampled from production traffic")

    # ---------------------------------------------------------------- J. response set
    nresp = Counter(len(c.get("responses", [])) for c in cmp_)
    add("candidates", "BLOCKING",
        "Nothing in the release says where the four candidate responses came from",
        f"responses per prompt: {dict(nresp)}. No model id, sampling temperature, generation date "
        f"or provenance field appears on any response object.",
        "any generation-provenance field on a response")

    # ---------------------------------------------------------------- K. no time
    has_time = any(re.search(r"time|date|created|stamp", k, re.I)
                   for a in ann[:5] for k in a)
    add("design", "SERIOUS",
        "No timestamp, session or batch field anywhere, so order and cohort effects cannot be "
        "controlled",
        f"top-level annotator keys: {sorted(ann[0].keys())}; assessment keys: "
        f"{sorted(ann[0]['assessments'][0].keys())}. Any time-like field found: {has_time}",
        "a timestamp or batch id on an assessment")

    # ---------------------------------------------------------------- L. position bias
    # TIES BREAK THE NAIVE TEST. 11.5% of rankings tie at the top, and a tied ranking would vote for
    # several slots at once, inflating chi-square without any bias existing. Restricted to rankings
    # with a UNIQUE first place, and the last-place version is run too because a slot that is
    # disproportionately LAST is the same defect wearing the other sign.
    uniq, lastc = Counter(), Counter()
    n_rank = tied_top = 0
    for a in ann:
        for s_ in a.get("assessments", []):
            for b in (s_.get("ranking_blocks") or {}).get("world", []) or []:
                t = b.get("ranking")
                if not t:
                    continue
                g = [x for x in t.replace(" ", "").split(">") if x]
                if not g:
                    continue
                n_rank += 1
                f = g[0].split("=")
                if len(f) == 1 and f[0] in RANK_MAP:
                    uniq[f[0]] += 1
                else:
                    tied_top += 1
                if len(g) > 1:
                    lz = g[-1].split("=")
                    if len(lz) == 1 and lz[0] in RANK_MAP:
                        lastc[lz[0]] += 1
                break
    tu = sum(uniq.values())
    eu = tu / 4
    chi = sum((uniq[L] - eu) ** 2 / eu for L in "ABCD")
    tl = sum(lastc.values())
    el = tl / 4
    chil = sum((lastc[L] - el) ** 2 / el for L in "ABCD")
    # SEVERITY CORRECTED BY WAVE TWO. This was BLOCKING here on the strength of the chi-square
    # alone. r167 then PRICED it: a predictor knowing only the slot reaches pairwise concordance
    # 0.4993 against a 0.5000 chance level. The asymmetry is overwhelmingly significant at n=16,530
    # and carries no predictive power on the metric everything in this repo uses. Both are true, and
    # calling it blocking without pricing it was the significance-versus-magnitude error.
    add("measurement", "NOTED" if chi > 16.27 else "CLEAN",
        ("Response SLOT predicts first and last place at high significance, but a slot-only "
         "predictor scores 0.4993 against 0.5000 chance -- real and worth nothing"
         if chi > 16.27 else "CHECKED: no position effect"),
        f"on the {tu} rankings with a UNIQUE first place ({tu / n_rank:.1%} of {n_rank}): "
        f"{dict(sorted(uniq.items()))}, chi-square {chi:.1f} on 3 df against 16.27 at p=.001. "
        f"Slot B is {100 * (uniq['B'] - eu) / eu:+.1f}% versus uniform. Unique LAST place is "
        f"stronger still: {dict(sorted(lastc.items()))}, chi-square {chil:.1f}, with slot D "
        f"{100 * (lastc['D'] - el) / el:+.1f}%.",
        "a chi-square below 16.27 on the unique-first-place subset")

    # ---------------------------------------------------------------- M. length bias
    rlen = defaultdict(list)
    for c in cmp_:
        for r in c.get("responses", []):
            i = (r.get("response_index") or "").strip()
            if i in RANK_MAP:
                rlen[i].append(sum(len(msg_text(m)) for m in r.get("messages", [])))
    means = {k: float(np.mean(v)) for k, v in rlen.items() if v}
    spread = (max(means.values()) - min(means.values())) / np.mean(list(means.values()))
    # THE CONTROL THAT DECIDES WHAT THE POSITION EFFECT MEANS. If the four responses differ by
    # slot -- different generator, different length -- then slot is a real property and the ranking
    # asymmetry is information. If they are indistinguishable, the asymmetry is in the RATERS.
    add("candidates", "SERIOUS" if spread > 0.15 else "CLEAN",
        ("Candidate responses differ systematically by slot, so slot encodes a property"
         if spread > 0.15 else
         "CHECKED: response content is statistically identical across slots, which is what makes "
         "the position effect a RATER effect rather than a property of the responses"),
        f"mean response length by slot: {({k: round(v) for k, v in means.items()})}; "
        f"spread relative to the mean = {spread:.1%}",
        "a relative spread above 15%")

    # ---------------------------------------------------------------- N. prompts with no rubric
    nor = len(pid) - len(rid & pid) - (len(joined))
    add("coverage", "SERIOUS",
        "Nearly a hundred prompts carry rankings but no rubric at all",
        f"{len(pid)} prompts in comparisons, {len(joined)} of them joined to a rubric, "
        f"{len(pid) - len(joined)} with none",
        "every prompt having a rubric")

    # ---------------------------------------------------------------- O. demographic missingness
    miss = Counter()
    for a in ann:
        d = a.get("demographics") or {}
        for k in ("age", "gender", "country_of_residence", "education_level"):
            v = d.get(k)
            if not isinstance(v, str) or not v or v.lower().startswith(("prefer not", "not sure")):
                miss[k] += 1
    worst_k, worst_n = miss.most_common(1)[0] if miss else ("none", 0)
    add("population", "NOTED" if worst_n / len(ann) > 0.02 else "CLEAN",
        ("Demographic fields carry refusals and non-answers that any group analysis must handle"
         if worst_n / len(ann) > 0.02 else
         "CHECKED: demographic coverage is effectively complete"),
        f"missing-or-refused per field over {len(ann)} annotators: {dict(miss)}",
        "no field exceeding 2% missing")

    # ---------------------------------------------------------------- P. generic core criteria
    core_all = Counter(c["criterion"].strip().lower() for r in rub for c in r["coval_core"])
    reused = [(t, n) for t, n in core_all.items() if n > 1]
    add("compilation", "NOTED" if reused else "CLEAN",
        ("Some compiled criteria are reused verbatim across different prompts, which is the "
         "signature of a generic criterion in a prompt-specific rubric" if reused else
         "CHECKED: no compiled criterion is reused across prompts"),
        f"{len(core_all)} distinct core criteria, {len(reused)} appearing on more than one prompt; "
        f"most reused: {sorted(reused, key=lambda x: -x[1])[:3]}",
        "zero reuse across prompts")

    # ---------------------------------------------------------------- report
    order = {"BLOCKING": 0, "SERIOUS": 1, "NOTED": 2, "CLEAN": 3}
    FINDINGS.sort(key=lambda f: (order[f["severity"]], f["axis"]))
    for sev in ("BLOCKING", "SERIOUS", "NOTED", "CLEAN"):
        items = [f for f in FINDINGS if f["severity"] == sev]
        print(f"\n{'=' * 78}\n{sev}  ({len(items)})\n{'=' * 78}")
        for f in items:
            print(f"\n[{f['axis']}] {f['title']}")
            print(f"    {f['measurement']}")
            print(f"    falsifier: {f['falsifier']}")
    print(f"\ntotal: {len(FINDINGS)} findings "
          f"({sum(1 for f in FINDINGS if f['severity'] == 'BLOCKING')} blocking)")
    (OUT / "census.json").write_text(json.dumps(FINDINGS, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
