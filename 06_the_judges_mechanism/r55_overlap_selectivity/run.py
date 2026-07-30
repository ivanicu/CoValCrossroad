"""r55 -- the overlap channel's ORDERING component, which is the only part that could explain r12.

r54 measured MEAN criterion->response overlap and found the own-vs-donor
advantage collapses on fresh responses (+0.1294 -> +0.0945) while failing to
predict which prompts drop (corr -0.0736).  That left a live possibility the
round itself flagged: a UNIFORM contribution, invisible to a per-prompt
correlation.

This closes it by measuring the right quantity instead of the same one again.
Attribution is an ORDERING statistic -- agreement between the rubric's ranking
of four responses and gold's.  A mean shift that raises or lowers all four
equally cannot move an ordering.  What can is SELECTIVITY:

    selectivity(c) = sd over the four responses of containment(c, r)

A criterion written about response B's specific flaw overlaps B and not the
others, and THAT is what carries ranking information.  So the mechanism r51/r52
established can only explain r12 if selectivity collapses between response sets.

CLAIM CARD, inline:
  Claim       the overlap channel's ordering-relevant component collapses on
              fresh responses and thereby explains r12
  Estimand    own-minus-donor selectivity on each response set, and its change
  Target      observed exactly (text statistics); the attribution it is
              correlated against is model-proxy scored (entry 50)
  Worlds      A collapse -> overlap explains r12 by the only available route;
              B no collapse -> the mechanism is real, uniform, and CANNOT move
              an ordering, so the uniform-contribution escape closes too
  Null        the donor arm: criteria from another prompt have no reason to be
              selective about these responses on either set
  Kill        a collapse near zero with a tight interval kills the hypothesis
              rather than leaving it underpowered
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import load_join  # noqa: E402

OUTCOME_SCOPE = (
    "Selectivity is an exact text statistic. The attribution it is correlated against "
    "is scored by the r08 model gold head, not by humans (entry 50)."
)
STOP = set("the a an and or of to in for on with is are be that this it as at by from "
           "not no should must does do response answer model user its their they was "
           "have has had can will would could may might also more most other such".split())


def toks(s):
    return {w for w in re.findall(r"[a-z']{4,}", str(s).lower()) if w not in STOP}


def selectivity(crits, texts):
    """Mean over criteria of the SD of containment across the four responses."""
    rt = [toks(t) for t in texts]
    out = []
    for c in crits:
        ct = toks(c)
        if ct:
            out.append(float(np.std([len(ct & r) / len(ct) for r in rt])))
    return float(np.mean(out)) if out else np.nan


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--gen", type=Path,
                   default=_ROOT / "02_attribution_under_attack/r12_response_set/results/a12_fresh_generations.json")
    p.add_argument("--r12", type=Path,
                   default=_ROOT / "02_attribution_under_attack/r12_response_set/results/a12_response_set.json")
    p.add_argument("--out", type=Path, default=_RES / "r55_overlap_selectivity.json")
    p.add_argument("--boot", type=int, default=4000)
    p.add_argument("--delta", type=float, default=0.01,
                   help="equivalence margin, r42's declared value")
    a = p.parse_args()

    gen = json.loads(a.gen.read_text())
    gp = {p_: i for i, p_ in enumerate(gen["prompt_ids"])}
    items = []
    for pid, comp, rub in load_join(a.comparisons, a.rubrics):
        if pid not in gp:
            continue
        cr = [c["criterion"] for c in (rub.get("coval_core") or [])]
        if cr:
            items.append({"pid": pid, "crits": cr, "i": gp[pid]})
    n = len(items)
    rng = np.random.default_rng(20260727)
    donor = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])

    own_o, own_f, don_o, don_f = [], [], [], []
    for k, it in enumerate(items):
        o, f = gen["original"][it["i"]], gen["fresh"][it["i"]]
        d = items[int(donor[k])]["crits"]
        own_o.append(selectivity(it["crits"], o))
        own_f.append(selectivity(it["crits"], f))
        don_o.append(selectivity(d, o))
        don_f.append(selectivity(d, f))
    own_o, own_f, don_o, don_f = (np.array(x, float) for x in (own_o, own_f, don_o, don_f))

    def ci(x):
        x = x[np.isfinite(x)]
        bs = np.array([x[rng.integers(0, len(x), len(x))].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return float(x.mean()), float(lo), float(hi)

    cells = {}
    print(f"prompts {n}\nSELECTIVITY = sd of containment across the four responses\n")
    for tag, x in (("own_x_original", own_o), ("own_x_fresh", own_f),
                   ("donor_x_original", don_o), ("donor_x_fresh", don_f)):
        m, lo, hi = ci(x)
        cells[tag] = [m, lo, hi]
        print(f"  {tag:18s} {m:.4f} [{lo:.4f},{hi:.4f}]")

    adv_o, adv_f = own_o - don_o, own_f - don_f
    coll = adv_o - adv_f
    ao, alo, ahi = ci(adv_o)
    af, flo, fhi = ci(adv_f)
    cm, clo, chi = ci(coll)
    print(f"\n  selectivity advantage ORIGINAL {ao:+.4f} [{alo:+.4f},{ahi:+.4f}]")
    print(f"  selectivity advantage FRESH    {af:+.4f} [{flo:+.4f},{fhi:+.4f}]")
    print(f"  COLLAPSE                       {cm:+.4f} [{clo:+.4f},{chi:+.4f}]")

    r12 = json.loads(a.r12.read_text())
    p2i = {p_: i for i, p_ in enumerate(r12["sets"]["ORIGINAL"]["per_prompt"]["pids"])}
    drop = (np.array(r12["sets"]["ORIGINAL"]["per_prompt"]["attribution"], float)
            - np.array(r12["sets"]["FRESH"]["per_prompt"]["attribution"], float))
    dd = drop[[p2i[it["pid"]] for it in items if it["pid"] in p2i]]
    keep = np.isfinite(coll) & np.isfinite(dd)
    r = float(np.corrcoef(coll[keep], dd[keep])[0, 1])
    bs = np.array([float(np.corrcoef(coll[keep][i], dd[keep][i])[0, 1])
                   for i in (rng.integers(0, keep.sum(), keep.sum()) for _ in range(a.boot))])
    rlo, rhi = np.percentile(bs[np.isfinite(bs)], [2.5, 97.5])
    print(f"\n  corr(selectivity collapse, attribution drop) {r:+.4f} [{rlo:+.4f},{rhi:+.4f}]")

    # EQUIVALENCE, not just non-significance -- r42's discipline, r42's margin.
    bs90 = np.array([coll[np.isfinite(coll)][rng.integers(0, np.isfinite(coll).sum(),
                                                          np.isfinite(coll).sum())].mean()
                     for _ in range(a.boot)])
    e_lo, e_hi = np.percentile(bs90, [5, 95])
    equivalent = bool(e_lo > -a.delta and e_hi < a.delta)
    print(f"  equivalence at delta={a.delta}: 90% CI [{e_lo:+.4f},{e_hi:+.4f}] -> "
          f"{'EQUIVALENT to zero' if equivalent else 'not equivalent'}")

    collapsed = bool(clo > 0)
    if collapsed:
        verdict = (
            f"THE ORDERING COMPONENT COLLAPSES ({cm:+.4f} [{clo:+.4f},{chi:+.4f}]), so the "
            f"judge's overlap sensitivity can move r12's ordering statistic and the "
            f"mechanism is live")
    elif equivalent:
        verdict = (
            f"THE ORDERING COMPONENT DOES NOT COLLAPSE, AND IS EQUIVALENT TO ZERO AT "
            f"delta={a.delta}. Own criteria are as SELECTIVE about fresh responses "
            f"({cells['own_x_fresh'][0]:.4f}) as about the originals they were written for "
            f"({cells['own_x_original'][0]:.4f}); the own-minus-donor advantage is "
            f"{ao:+.4f} then {af:+.4f}, a change of {cm:+.4f} [{clo:+.4f},{chi:+.4f}]. "
            f"r54 found the MEAN overlap advantage really does fall, but attribution is an "
            f"ORDERING statistic and a shift that moves all four responses equally cannot "
            f"move an ordering. So the uniform-contribution escape r54 left open is now "
            f"CLOSED: the component that could have acted uniformly is the one that does "
            f"not vary, and the component that would have to vary does not change. The "
            f"judge's overlap channel is real (r51, r52) and cannot explain r12")
    else:
        verdict = (
            f"NO DETECTED COLLAPSE, BUT NOT EQUIVALENT EITHER: {cm:+.4f} "
            f"[{clo:+.4f},{chi:+.4f}], 90% CI [{e_lo:+.4f},{e_hi:+.4f}] against "
            f"delta={a.delta}. Underpowered rather than informative")
    print(f"\n-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "prompts": n, "selectivity": cells,
        "advantage_original": [ao, alo, ahi], "advantage_fresh": [af, flo, fhi],
        "collapse": [cm, clo, chi], "collapse_ci90": [float(e_lo), float(e_hi)],
        "equivalence_delta": a.delta, "equivalent_to_zero": equivalent,
        "corr_with_attribution_drop": [r, rlo, rhi],
        "verdict": verdict, "outcome_variable_scope": OUTCOME_SCOPE,
        "scope": ("Lexical containment only -- a criterion can be selectively ABOUT one "
                  "response while sharing few of its words, and this measure is blind to "
                  "that. What it establishes is that the SURFACE-FORM channel r51 and r52 "
                  "demonstrated has no ordering-relevant change between response sets; it "
                  "does not establish that no semantic selectivity changed."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
