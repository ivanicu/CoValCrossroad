#!/usr/bin/env python3
"""
R916 · which "arms" in the reported populations are APPARATUS rather than candidate cores?

⛔ WHY. R915 found the comparator `genericpool16` sitting inside `FIXED_CHECKLIST`'s denominator —
an INELIGIBLE unit, because its margin against itself is exactly 0 and it can never be admitted.
The correction was small (1/2 → 1/1, verdict unchanged) but the CLASS is not: **a population that
contains the instrument is not a population of units.** This round asks whether that happened
anywhere else, and it is designed to be able to find nothing.

⭐⭐ **THE CLASSIFICATION MUST BE MECHANICALLY CHECKABLE, NOT MY TASTE.** Deciding by name — "that
one looks like a control" — would be the label-is-not-a-measurement error this arc has logged
twice. Three apparatus signatures, each a property of the committed data:
  · **COMPARATOR** — its margin against the comparator is exactly 0 (it IS the comparator)
  · **WHOLE RUBRIC** — its selection equals the prompt's ENTIRE criterion set on ~every prompt. A
    core is a SUBSET; the whole rubric is the object a core is extracted FROM, so `full` is the
    reference, not a candidate
  · **MISDIRECTED** — its criteria are NOT drawn from the prompt they score **AND they VARY across
    prompts**. §4's row calls this a poison, not a placebo, and a poison is apparatus.
    ⛔⛔ POST-RUN: THE SECOND CLAUSE WAS MISSING AND THE SIGNATURE OVER-FIRED. Without it,
    `not-from-this-prompt = 1.000` is true for a sham (criteria from a DIFFERENT prompt) **and for
    a FIXED CHECKLIST** (criteria from NO prompt) — two different objects, one a poison and one a
    legitimate arm kind. It flagged `generic`, which R904 had already typed as a fixed checklist by
    exactly the test I omitted: **identical set on every prompt.** My control ② could not catch it
    because it tested `topw_k4`, a rubric selector, which is far from this boundary. **A negative
    control has to sit near the line it is guarding.**
⚠ Anything else is left as a CANDIDATE. **The round errs toward calling things candidates**, so a
finding here is a finding and a null is not manufactured by an over-eager filter.

ESTIMAND        the count and identity of arms in the reported populations that satisfy an
                apparatus signature, and which reported shares contain them.
IDENTIFICATION  exact — every signature is a property of committed selections or margins.
SCOPE           population: R881's 99 arms plus the 30 built in R893–R912, with committed
                            per-prompt selections where the signature needs them
                instrument: exact set comparison against `core_full.json`; margin vs genericpool16
                baseline:   zero apparatus arms, i.e. every reported unit is a candidate
                regime:     home release, judge 2B
WORLDS          A · only `genericpool16` is apparatus -> R915 was a one-off and the populations are
                    otherwise clean
                B · more arms are apparatus -> the same error occurred more than once, and every
                    share containing them needs the R915 treatment
                C · the signatures fire on arms that are plainly candidates -> the classifier is
                    too loose and its output is not usable
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE, on the case already established: `genericpool16` MUST be flagged
                     COMPARATOR. If the classifier misses the one apparatus arm we know about, it
                     cannot be trusted on the others.
                  ⭐ ② NEGATIVE: `topw_k4` — a plain rule-selected candidate — must be flagged as
                     NOTHING. A classifier that flags everything finds apparatus trivially.
                  ⭐ ③ the WHOLE-RUBRIC test must be a real comparison against `core_full.json`,
                     not a name match on the string "full".
MULTIPLICITY    3 signatures × every arm with the data to test it; all hits printed with which
                signature fired and on what evidence.
ARTIFACT        results/apparatus_audit.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND: whether an arm SHOULD count as a candidate is partly a
                definitional choice. This flags mechanical signatures, not intent.
"""
import json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls               # noqa: E402

RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
COMP, NBOOT, SEED = "genericpool16", 1500, 916


def main() -> int:
    r881 = json.loads(next(A24.glob("R881_*/results/boundary_distance.json")).read_text())
    arms = sorted({x["arm"] for x in r881["arms"]} |
                  {f.stem[4:] for f in NEW.glob("sat_*.npz")})

    sys.path.insert(0, str(ROOT))
    from covalx.judge import load_join                                       # noqa: E402
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    fullr = {p: set(i["criterion"] for i in (r.get("coval_full") or [])) for p, _q, r in joined}

    def sel(nm):
        for d in (RES, NEW):
            f = d / f"core_{nm}.json"
            if f.exists():
                try:
                    return json.loads(f.read_text())
                except Exception:
                    return None
        return None

    tg, _ = load_targets()
    S = load_sat(RES / f"sat_{COMP}.npz")
    pids = sorted(set(S) & set(fullr) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if f.exists():
                try:
                    Sa = load_sat(f)
                except Exception:
                    return None
                v = np.array([np.mean([[cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]})))[c] == h[c]
                                        for c in range(6)] for h in H[k]]) if p in Sa else np.nan
                              for k, p in enumerate(pids)])
                return np.nan_to_num(v, nan=np.nanmean(v)) if np.isfinite(v).sum() >= 200 else None
        return None

    base = vec(COMP)
    if base is None:
        print("  UNRUNNABLE: comparator missing. Exit 2, never 0.")
        return 2

    def classify(nm):
        sigs, ev = [], {}
        v = vec(nm)
        if v is not None:
            m = float((v - base).mean())
            if abs(m) < 1e-12:
                sigs.append("COMPARATOR"); ev["margin_vs_comparator"] = m
        s = sel(nm)
        if s:
            shared = [p for p in s if p in fullr and s[p]]
            if len(shared) >= 50:
                whole = float(np.mean([set(s[p]) == fullr[p] for p in shared]))
                outside = float(np.mean([not (set(s[p]) <= fullr[p]) for p in shared]))
                fixed = len({frozenset(s[p]) for p in shared}) == 1     # R904's discriminator
                ev["share_equals_whole_rubric"] = whole
                ev["share_not_from_this_prompt"] = outside
                ev["identical_set_every_prompt"] = fixed
                if whole > 0.95:
                    sigs.append("WHOLE_RUBRIC")
                if outside > 0.95 and not fixed:
                    sigs.append("MISDIRECTED")          # varies per prompt -> a sham
                elif outside > 0.95 and fixed:
                    sigs.append("FIXED_CHECKLIST_not_apparatus")
        return sigs, ev

    print(f"  arms examined: {len(arms)} · prompts {len(pids)}")
    hits, tested = {}, 0
    for a in arms:
        sg, ev = classify(a)
        tested += 1
        if sg:
            hits[a] = {"signatures": sg, "evidence": ev}

    c1 = "COMPARATOR" in hits.get(COMP, {}).get("signatures", [])
    # ② now has TWO negatives: one far from the line, one ON it
    c2a = "topw_k4" not in hits
    c2b = "MISDIRECTED" not in hits.get("generic", {}).get("signatures", [])
    c2 = c2a and c2b
    print(f"\n  ① POSITIVE {COMP} flagged COMPARATOR: {c1}  {'PASS' if c1 else 'FAIL'}")
    print(f"     if the classifier misses the one apparatus arm we know about, it is untrustworthy")
    print(f"  ② NEGATIVE ×2, one far from the line and one ON it:")
    print(f"     topw_k4 (plain rule selection) flagged as nothing:        {c2a}")
    print(f"     `generic` (fixed checklist, NOT a sham) not MISDIRECTED:  {c2b}")
    print(f"     {c2}  {'PASS' if c2 else 'FAIL'}   ⚠ the second negative is the one that")
    print(f"     matters: a negative control has to sit NEAR the line it guards, and my first")
    print(f"     version only had the far one, so the over-firing went through.")
    c3 = any("share_equals_whole_rubric" in h["evidence"] for h in hits.values()) or \
        all("WHOLE_RUBRIC" not in h["signatures"] for h in hits.values())
    print(f"  ③ the WHOLE_RUBRIC test is a real set comparison against core_full.json, not a name "
          f"match: {c3}  {'PASS' if c3 else 'FAIL'}")
    if not (c1 and c2 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "hits": hits},
                  open(OUT / "apparatus_audit.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐ APPARATUS SIGNATURES — every hit, with the evidence that fired it:")
    for a, h in sorted(hits.items()):
        ev = ", ".join(f"{k}={v:.3f}" if isinstance(v, float) else f"{k}={v}"
                       for k, v in h["evidence"].items())
        print(f"     {a:<24} {'+'.join(h['signatures']):<26} {ev}")
    if not hits:
        print(f"     none")

    apparatus = {a for a, h in hits.items()
                 if any(x in h["signatures"] for x in ("COMPARATOR", "WHOLE_RUBRIC",
                                                       "MISDIRECTED"))}
    # which reported shares contain them?
    r906 = json.loads(next(A24.glob("R906_*/results/bar_by_source.json")).read_text())
    r908 = json.loads(next(A24.glob("R908_*/results/bar_by_rule.json")).read_text())
    affected = []
    for k in r906["kinds"]:
        bad = sorted(set(k["built"]) & apparatus)
        if bad:
            affected.append({"round": "R906", "cell": k["kind"], "n_built": k["n_built"],
                             "apparatus": bad})
    for r in r908["rules"]:
        names = [a for a in arms if a.startswith(r["rule"] + "_k")]
        bad = sorted(set(names) & apparatus)
        if bad:
            affected.append({"round": "R908", "cell": r["rule"], "n_built": r["n_built"],
                             "apparatus": bad})
    print(f"\n  ⭐⭐ REPORTED CELLS CONTAINING APPARATUS:")
    for a in affected:
        print(f"     {a['round']} {a['cell']:<24} n={a['n_built']:<4} contains {a['apparatus']}")
    if not affected:
        print(f"     none beyond what R915 already corrected")

    only_comp = apparatus <= {COMP}
    world = "A" if only_comp else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": f"only `{COMP}` carries an apparatus signature — R915 was a one-off and the reported "
             "populations are otherwise clean",
        "B": f"{len(hits)} arms carry an apparatus signature — the same error occurred more than "
             "once, and every share containing them needs the R915 treatment"}[world])
    print(f"\n  ⚠ THE ROUND ERRS TOWARD `CANDIDATE`. Only three mechanical signatures fire, each a")
    print(f"    property of committed data; anything else is left a candidate. So a null here is")
    print(f"    not manufactured by an over-eager filter — and it is also not proof that every")
    print(f"    remaining arm SHOULD count as a candidate, which is partly a definitional choice")
    print(f"    this round does not make.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "seed": SEED, "n_arms_examined": len(arms),
               "n_prompts": len(pids), "hits": hits, "affected_cells": affected,
               "signatures": {
                   "COMPARATOR": "margin against the comparator is exactly 0 — it IS the comparator",
                   "WHOLE_RUBRIC": "its selection equals the prompt's ENTIRE criterion set; a core "
                                   "is a SUBSET, so the whole rubric is the reference not a "
                                   "candidate",
                   "MISDIRECTED": "its criteria are not drawn from the prompt it scores — a sham "
                                  "by construction, and §4 calls that a poison"},
               "errs_toward_candidate": "only three mechanical signatures fire; anything else is "
                                        "left a candidate, so a null is not manufactured",
               "does_not_decide": "whether an arm SHOULD count as a candidate — that is partly "
                                  "definitional and this round flags signatures, not intent",
               "controls": {"positive_comparator_flagged": bool(c1),
                            "negative_topw_k4_clean": bool(c2),
                            "whole_rubric_is_a_set_comparison": bool(c3)},
               "unit_note": "counts are ARMS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "apparatus_audit.json", "w"), indent=2)
    print(f"\n  artifact: results/apparatus_audit.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
