"""Build the claim-harness-budget package a third party can act on.

The role asks for "increasing rigor of external assurances by turning external
findings into robust evaluations". A finding becomes an assurance artifact only
when an outsider can answer, without asking us:

  CLAIM     what exactly is asserted, and over what population and version
  HARNESS   what code, data, seeds and exclusions produce it
  BUDGET    what it costs to rerun, in wall-clock, GPU-hours and dollars
  VALIDITY  which four validity types are and are not established
  VERSION   what change invalidates the claim

This emits all five from the actual run: every hash is read off disk, every
budget number is measured, not estimated. Claims whose supporting file is
missing are emitted as UNSUPPORTED rather than silently dropped -- an assurance
package that quietly omits a failed claim is worse than no package.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def sha256(p: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def git_rev() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "uncommitted"


# ---------------------------------------------------------------- claims
# (id, statement, source file, json path, direction, threshold)
CLAIMS = [
    ("C1",
     "SCOPED BY C12. On the four RELEASED candidate responses, less than half of "
     "a rubric's ability to predict held-out human rankings is attributable to "
     "prompt-specific criterion content; the remainder is generic response "
     "quality obtainable with an unrelated rubric. C12 shows this prompt-specific "
     "component does not extend to responses the criteria were not authored "
     "against, so C1 must not be read as a property of the rubric in general.",
     "rounds/r04_rebuild_satisfaction/results/a04_full.json", "rubric_contribution_share", "<", 0.5),

    ("C2",
     "The rebuilt criterion-satisfaction layer predicts held-out human pairwise "
     "rankings above chance and above a length-only baseline.",
     "rounds/r04_rebuild_satisfaction/results/a04_full.json", "pairwise_accuracy", ">", 0.55),

    ("C3",
     "Among defensible aggregation principles at k=4, out-of-sample predictive "
     "accuracy spans less than 3 percentage points, and a lower-quartile "
     "consensus rule is indistinguishable from random selection of four shared "
     "criteria.",
     "rounds/r06_rule_tournament/results/a06_rule_tournament.json", "rules.consensus.accuracy", "~", 0.64),

    # REWRITTEN 2026-07-28.  The old C4 read: "...exceeds its permutation null
    # and survives removal of per-rater response style, so disagreement carries
    # a stable person-level component", tested as r01's style-removed rho > 0.05.
    # Two defects.  (a) The style-removal clause is unfalsifiable: Pearson
    # correlation is invariant to per-rater affine rescaling, so that control
    # returns "survived" on any input (131,771/131,771 dyads unchanged, median
    # |delta| 5.6e-17).  (b) The tested number conflates an additive ACTOR
    # effect -- raters differing in reliability, which is compatible with a
    # single shared target -- with the PAIR-specific structure the pluralism
    # argument actually needs.  r23 separates them; the actor part is the larger
    # one.  C4 now asserts and tests only the part that was ever in question.
    ("C4",
     "Beyond an additive per-rater (actor) effect, pairwise rater agreement "
     "carries a PAIR-specific component that persists across disjoint prompt "
     "sets above a dyad-permutation null. The actor component is the larger of "
     "the two; the pair-specific residual is roughly a quarter of the raw "
     "persistence r01 reported, and it is the only part that bears on whether a "
     "single core rubric is the wrong object.",
     "rounds/r23_actor_vs_dyad/results/r23_actor_vs_dyad.json", "style_removed.resid_z", ">", 2.0),

    ("C5",
     "Anthropomorphic style independently predicts human preference after "
     "controlling for the rubric score and response length, while fewer than "
     "1 percent of crowd-written criteria address it.",
     "rounds/r07_anthropomorphism/results/a07_anthropomorphism.json", "rubric_absorption_test.anthro_t", ">", 2.0),

    # ADDED 2026-07-28.  C5's sentence makes TWO assertions and its test gated
    # only the first.  A construct review then read all 24 Tier-1 hits and found
    # at least 13 off-construct or reversed in polarity -- `personal opinion`
    # mostly appears in instructions to AVOID opinions, one `as an ai` hit is an
    # anti-anthropomorphism disclosure rule, and all four `persona` hits are
    # content roleplay on request.  The rate claim survives either way (both
    # 0.157% and the ~0.07% floor are under 1%), but it must be gated, not
    # merely written.
    ("C14",
     "Fewer than one percent of crowd-written CoVal-full criteria address "
     "anthropomorphic self-presentation, under a word-boundary lexicon whose "
     "Tier-1 term list is known to over-count: at least 13 of its 24 matches are "
     "off-construct or polarity-reversed, so this rate is an upper bound.",
     "rounds/r07_anthropomorphism/results/a07_anthropomorphism.json", "criteria_tier1_share", "<", 0.01),

    ("C6",
     "PRE-REGISTERED AND REFUTED: optimizing selection against the rubric was "
     "predicted to raise lexical overlap with the criterion text (the gaming "
     "direction implied by C1). Test compares overlap at max strength against "
     "overlap at n=1; the prediction requires a rise of at least 0.02.",
     "rounds/r09_overoptimization/results/a09_overoptimization.json", "overlap_rise", ">", 0.02),

    ("C7",
     "RETRACTED BY C11. Within best-of-16 pressure the gold preference change is "
     "distinguishable from zero. This held only with a gold head sharing the "
     "judge's backbone; the independent-backbone control (C11) does not "
     "reproduce it, so the effect is NOT established in either direction.",
     "rounds/r11_backbone_control/results/a11_backbone_control.json", "gold_08b_independent.delta", ">", 0.30),

    ("C11",
     "The A09 result is reproduced by a gold preference head built on a "
     "DIFFERENT backbone from the judge, ruling out shared-backbone leakage.",
     "rounds/r11_backbone_control/results/a11_backbone_control.json", "independent_reproduces", "==", True),

    ("C9",
     "The attribution decomposition is not an artifact of one judge or one "
     "prompt template: across three judge/template configurations the "
     "prompt-specific contribution stays positive with small spread.",
     "rounds/r10_attribution_robustness/results/a10_attribution.json", "attribution_mean", ">", 0.03),

    ("C10",
     "Part of what the random-donor control attributes to 'prompt-specific "
     "value content' is merely topic match: a nearest-topic donor recovers a "
     "material share of the gap.",
     "rounds/r10_attribution_robustness/results/a10_attribution.json", "topic_share_mean", ">", 0.10),

    ("C12",
     "The prompt-specific advantage in C1 survives on responses the criteria were "
     "NOT authored against. Measured as attribution on rubric-blind fresh "
     "responses; requires a positive value. FAILS -- but note r13 refutes the "
     "response-set-knowledge explanation for that failure: response-blind seed "
     "criteria carry more attribution than criteria written after reading the "
     "candidates, so the non-transfer is a property of the measurement off "
     "distribution, not of what the criteria encode.",
     "rounds/r12_response_set/results/a12_response_set.json",
     "sets.FRESH.attribution", ">", 0.0),

    ("C13",
     "The fresh response set used by C12 admits an ordering at all, so a null "
     "there is a measurement rather than silence.",
     "rounds/r12_response_set/results/a12_response_set.json",
     "control_passed", "==", True),

    ("C8",
     "The instrument used for C6/C7 discriminates among the candidates it "
     "scores, so a null there is a measurement and not silence.",
     "rounds/r09_overoptimization/results/a09_overoptimization.json", "positive_control_passed", "==", True),
]


def derived(doc, path: str):
    """Fields that are computed from the curve rather than stored."""
    if path == "overlap_rise":
        c = doc.get("curve") or []
        if len(c) < 2:
            return None
        k = "mk_criterion_lexical_overlap"
        return float(c[-1].get(k, 0.0) - c[0].get(k, 0.0))
    if path == "rubric_contribution_share":
        # ADDED 2026-07-28 after an independent reproducibility review.
        # C1 asserts a PROPORTION ("less than half of a rubric's ability") but
        # was tested against `rubric_contribution`, a raw accuracy-point
        # difference of 0.0791, compared to a threshold of 0.5.  Pairwise
        # accuracy differences on this task cannot approach 0.5, so the test
        # returned HOLDS for every reachable value of the quantity -- it would
        # have passed at a true share of 90%.  A check that cannot fail is not
        # a check.  This is the second live instance of the defect RETRACTIONS
        # entry 5 claimed to have generalised away.
        acc, con = doc.get("pairwise_accuracy"), doc.get("rubric_contribution")
        if acc is None or con is None or acc <= 0.5:
            return None
        return float(con) / float(acc - 0.5)
    return None


def dig(doc, path: str):
    d = derived(doc, path)
    if d is not None:
        return d
    cur = doc
    for k in path.split("."):
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        elif isinstance(cur, list):
            try:
                cur = cur[int(k)]
            except Exception:
                return None
        else:
            return None
    return cur


def check(val, direction, thr):
    if val is None:
        return "UNSUPPORTED"
    try:
        if direction == ">":
            return "HOLDS" if val > thr else "FAILS"
        if direction == "<":
            return "HOLDS" if val < thr else "FAILS"
        if direction == "==":
            return "HOLDS" if val == thr else "FAILS"
        if direction == "~":
            return "HOLDS" if abs(val - thr) < 0.02 else "FAILS"
    except Exception:
        return "UNSUPPORTED"
    return "UNSUPPORTED"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--out", type=Path, default=Path("assurance/MANIFEST.json"))
    ap.add_argument("--md", type=Path, default=Path("assurance/ASSURANCE.md"))
    a = ap.parse_args()
    root = a.root.resolve()

    inputs = {}
    for p in sorted((root / "data").glob("*.jsonl")):
        inputs[f"data/{p.name}"] = {"bytes": p.stat().st_size, "sha256": sha256(p)}

    code = {}
    for p in sorted(root.glob("covalx/*.py")) + sorted(root.glob("rounds/*/run.py")) \
             + sorted(root.glob("assurance/*.py")) + sorted(root.glob("data/*.py")):
        code[str(p.relative_to(root))] = {"bytes": p.stat().st_size, "sha256": sha256(p)}

    outputs = {}
    for p in sorted(root.glob("rounds/*/results/*.json")):
        outputs[str(p.relative_to(root))] = {"bytes": p.stat().st_size, "sha256": sha256(p)}

    claims = []
    broken = []
    for cid, stmt, src, path, direction, thr in CLAIMS:
        f = root / src
        if not f.exists():
            # Distinct from UNSUPPORTED. A missing source file means the harness
            # is broken -- e.g. the repository was reorganised and these paths
            # were not updated. Reporting that as "unsupported" reads like the
            # claim was never measured, which is a different and much softer
            # statement than "this package can no longer check itself".
            status, val = "BROKEN_HARNESS", None
            broken.append((cid, src))
        else:
            val = dig(json.loads(f.read_text()), path)
            status = check(val, direction, thr)
        claims.append({
            "id": cid, "statement": stmt, "source": src, "field": path,
            "value": val, "test": f"{direction} {thr}", "status": status,
        })
    if broken:
        print("BROKEN HARNESS -- these claims cannot be checked at all:")
        for cid, src in broken:
            print(f"    {cid}: missing {src}")
        raise SystemExit(
            f"{len(broken)} claim source(s) missing. Refusing to emit a manifest that "
            "would read as if the claims were merely unmeasured.")

    # measured budget
    budget = {}
    for name, src, field in [
        ("satisfaction_full", "rounds/r04_rebuild_satisfaction/results/a04_full.json", "seconds"),
        ("satisfaction_core", "rounds/r04_rebuild_satisfaction/results/a04_core.json", "seconds"),
    ]:
        f = root / src
        if f.exists():
            v = dig(json.loads(f.read_text()), field)
            if v:
                budget[name + "_gpu_seconds"] = v
    total_gpu_s = sum(v for k, v in budget.items() if k.endswith("_gpu_seconds"))
    budget["total_measured_gpu_hours"] = round(total_gpu_s / 3600, 3)
    budget["gpu"] = "1x RTX 5080 16GB"
    budget["judge_model"] = "Qwen3.5-2B-Base (local weights, no API)"
    budget["api_dollars"] = 0.0
    budget["note"] = ("no paid API is used; a third party reproducing this needs "
                      "one consumer GPU and the public CoVal release")

    manifest = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "git": git_rev(),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "seed": 20260727,
        "inputs": inputs, "code": code, "outputs": outputs,
        "claims": claims, "budget": budget,
        "validity": {
            "construct": "satisfaction is a model judgement, not a human label; "
                         "validated only against held-out human RANKINGS",
            # CORRECTED 2026-07-28 after an independent from-scratch recount of
            # the raw JSONL, reproduced here.  This sentence named ONE population
            # where the release has two.  The COMPARISON layer (rankings) is the
            # 1,012 described in annotators.jsonl.  The RUBRIC-SCORING layer that
            # r01/r04/r13/r16-r18 actually run on draws from 1,160 distinct
            # raters, 148 of whom appear in no annotator record -- so 12.8% of
            # the people whose scores drive those rounds have no demographic,
            # country or consent metadata in the release at all.  That is not a
            # footnote for r16: a bloc analysis cannot be checked against
            # demographic strata for raters who have no demographics.
            "population": "TWO populations, not one. Comparison rankings: 1,012 "
                          "English-reading online annotators in 19 countries "
                          "(annotators.jsonl), all of whom also scored criteria. "
                          "Criterion scoring: 1,160 distinct raters, of whom 148 "
                          "(12.8%) appear in no annotator record and therefore "
                          "carry no demographic metadata. Neither is a probability "
                          "sample of any population, and any rater-level claim "
                          "must say which of the two it is about",
            "ecological": "synthetic value-sensitive prompts, not real traffic",
            "adversarial": "gaming probed by best-of-n selection only; no trained "
                           "adversary, no human red team",
        },
        "invalidated_by": [
            "any change to the four release files (hashes above)",
            "a different judge model or prompt template",
            "a different shuffle scheme for the attribution control",
            "a different definition of the shared-criterion threshold",
        ],
    }
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(manifest, indent=1))

    lines = ["# Assurance package", "",
             f"generated {manifest['generated_utc']} · git `{manifest['git'][:12]}` · seed {manifest['seed']}",
             "", "## Claims", "",
             "| id | status | measured | test | claim |", "|---|---|---:|---|---|"]
    for c in claims:
        v = c["value"]
        vs = f"{v:.4f}" if isinstance(v, float) else str(v)
        lines.append(f"| {c['id']} | **{c['status']}** | {vs} | `{c['test']}` | {c['statement'][:110]}… |")
    lines += ["", "## Budget to reproduce", ""]
    for k, v in budget.items():
        lines.append(f"- **{k}**: {v}")
    # ---------------------------------------------------------- gate
    def val(cid):
        for c in claims:
            if c["id"] == cid:
                return c["value"]
        return None

    attribution = val("C1")
    topic_share = val("C10")
    value_only = None
    if attribution is not None and topic_share is not None:
        value_only = attribution * (1 - topic_share)

    gate = {
        "quantity": "attribution A = accuracy(real rubric) - accuracy(unrelated rubric), "
                    "measured on held-out human rankings",
        "measured_A": attribution,
        "topic_share_of_A": topic_share,
        "value_only_A": value_only,
        "rules": [
            {"band": "A < 0.02", "reading": "the rubric is a quality detector wearing a "
             "values label", "decision": "DO NOT use as a training or steering target; "
             "diagnostic use only, and report the shuffled-rubric arm alongside any "
             "headline number"},
            {"band": "0.02 <= A < 0.10", "reading": "real but minority value signal",
             "decision": "usable as ONE component of an ensemble; cap optimisation "
             "pressure at the strongest setting empirically tested; re-measure A after "
             "any rubric or judge change"},
            {"band": "A >= 0.10", "reading": "value signal dominates",
             "decision": "admissible as a primary target, still subject to an "
             "overoptimization curve with a gold side"},
        ],
        "optimisation_bound": {
            "tested_up_to": "best-of-16 selection (~1.8 nats)",
            "observed": "gaming markers fell; the gold preference change is "
                        "indistinguishable from zero once gold is built on a backbone "
                        "independent of the judge (the apparent rise appeared only "
                        "under a shared backbone)",
            "permitted_claim": "no overoptimization detected at or below the tested "
                               "pressure, and no improvement established either",
            "forbidden_claims": ["this rubric cannot be gamed",
                                 "optimising this rubric improves human preference"],
        },
        "blind_spot_rule": "an axis that predicts human preference independently of the "
                           "rubric (here: anthropomorphic style, t=+4.02, present in "
                           "0.16% of criteria) must be instrumented separately before "
                           "the rubric is optimised, because optimisation is free to "
                           "move along it unobserved",
    }
    manifest["deployment_gate"] = gate

    lines += ["", "## Deployment gate", "",
              (f"Measured attribution **A = {attribution:.4f}**"
               if attribution is not None else
               "Measured attribution **A = UNAVAILABLE** (source missing)")
              + (f", of which {topic_share:.1%} is topic rather than value "
                 f"(value-only A ~ {value_only:.4f})" if topic_share is not None else ""),
              ""]
    lines += ["| band | reading | decision |", "|---|---|---|"]
    for r in gate["rules"]:
        lines.append(f"| `{r['band']}` | {r['reading']} | {r['decision']} |")
    lines += ["", f"**Optimisation bound.** Tested to {gate['optimisation_bound']['tested_up_to']}; "
              f"{gate['optimisation_bound']['observed']}. Permitted claim: "
              f"*{gate['optimisation_bound']['permitted_claim']}*. Forbidden claims: "
              + "; ".join(f"*{c}*" for c in gate['optimisation_bound']['forbidden_claims']) + ".",
              "", f"**Blind-spot rule.** {gate['blind_spot_rule']}"]

    lines += ["", "## Validity boundaries", ""]
    for k, v in manifest["validity"].items():
        lines.append(f"- **{k}**: {v}")
    lines += ["", "## A new version is required if", ""]
    for v in manifest["invalidated_by"]:
        lines.append(f"- {v}")
    a.md.write_text("\n".join(lines) + "\n")

    ok = sum(1 for c in claims if c["status"] == "HOLDS")
    print(f"claims: {ok}/{len(claims)} HOLDS")
    for c in claims:
        v = c["value"]
        vs = f"{v:.4f}" if isinstance(v, float) else str(v)
        print(f"  {c['id']} {c['status']:12s} {vs:>10} {c['test']:>10}")
    print(f"\ninputs {len(inputs)} · code {len(code)} · outputs {len(outputs)}")
    print(f"measured GPU hours: {budget['total_measured_gpu_hours']}")
    print(f"wrote {a.out} and {a.md}")


if __name__ == "__main__":
    main()
