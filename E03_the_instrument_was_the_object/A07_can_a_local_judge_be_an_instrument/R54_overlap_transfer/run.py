"""r54 -- does the judge's overlap channel explain r12's transfer failure?

r52 established the judge is CAUSALLY overlap-sensitive: six tokens copied from
response A move the A-vs-B satisfaction gap by +0.2507.  That makes a specific
mechanism available for the project's most-chased result.

Own criteria were written by people looking at the ORIGINAL four responses, so
they share vocabulary with those responses above chance.  Donor criteria come
from a different prompt and share vocabulary with neither.  On FRESH responses
the own-rubric overlap advantage should evaporate while the donor never had one
-- which is the shape of r12: an own-rubric advantage on originals that shrinks
or inverts on generated text.

CLAIM CARD, inline:
  Claim       the collapse of the own-vs-donor overlap advantage explains r12
  Estimand    (a) mean containment for own/donor criteria on original/fresh;
              (b) corr(per-prompt collapse, per-prompt attribution drop)
  Target      overlap observed exactly; the ATTRIBUTION is model-proxy scored
              (r47/entry 50) and that scope travels
  Worlds      A mechanism explains r12 -> collapse tracks the drop across
              prompts;  B mechanism is real but orthogonal -> collapse is
              significant and the correlation is ~0;  C no mechanism -> no
              collapse
  Null        the donor arm IS the null: criteria from another prompt should
              show no advantage on either response set
  WATCH       a zero correlation does NOT rule out a UNIFORM contribution. If
              the collapse were near-constant across prompts it could shift
              every attribution equally and correlate with nothing. Variance of
              the collapse is reported so that reading stays available.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = next(p for p in _HERE.parents if (p / "covalx").is_dir())
_RES = _HERE / "results"
sys.path.insert(0, str(_ROOT))
from covalx import load_join  # noqa: E402

OUTCOME_SCOPE = (
    "The overlap quantities are exact text statistics. The ATTRIBUTION they are "
    "correlated against is scored by the r08 model gold head, not by humans -- see "
    "entry 50 and r47 -- so that half of every correlation here is proxy-world."
)
STOP = set("the a an and or of to in for on with is are be that this it as at by from "
           "not no should must does do response answer model user its their they was "
           "have has had can will would could may might also more most other such".split())


def toks(s):
    return {w for w in re.findall(r"[a-z']{4,}", str(s).lower()) if w not in STOP}


def containment(crits, texts):
    rt = [toks(t) for t in texts]
    out = []
    for c in crits:
        ct = toks(c)
        if ct:
            out.append(float(np.mean([len(ct & r) / len(ct) for r in rt])))
    return float(np.mean(out)) if out else np.nan


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--comparisons", type=Path, default=_ROOT / "data/comparisons.jsonl")
    p.add_argument("--rubrics", type=Path, default=_ROOT / "data/conversation_rubrics.jsonl")
    p.add_argument("--gen", type=Path,
                   default=_ROOT / "E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor/R12_response_set/results/a12_fresh_generations.json")
    p.add_argument("--r12", type=Path,
                   default=_ROOT / "E01_the_rubric_was_the_object/A03_is_the_attribution_real_and_against_what_floor/R12_response_set/results/a12_response_set.json")
    p.add_argument("--out", type=Path, default=_RES / "r54_overlap_transfer.json")
    p.add_argument("--boot", type=int, default=4000)
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
    # r12's donor permutation, from r12's seed, so the donor arm here is the
    # same pairing r12's attribution was computed against.
    rng = np.random.default_rng(20260727)
    donor = np.array([(i + 1 + rng.integers(0, n - 1)) % n for i in range(n)])

    own_o, own_f, don_o, don_f = [], [], [], []
    for k, it in enumerate(items):
        o, f = gen["original"][it["i"]], gen["fresh"][it["i"]]
        dcr = items[int(donor[k])]["crits"]
        own_o.append(containment(it["crits"], o))
        own_f.append(containment(it["crits"], f))
        don_o.append(containment(dcr, o))
        don_f.append(containment(dcr, f))
    own_o, own_f, don_o, don_f = (np.array(x, float) for x in (own_o, own_f, don_o, don_f))

    def ci(x):
        x = x[np.isfinite(x)]
        bs = np.array([x[rng.integers(0, len(x), len(x))].mean() for _ in range(a.boot)])
        lo, hi = np.percentile(bs, [2.5, 97.5])
        return float(x.mean()), float(lo), float(hi)

    print(f"prompts {n}   mean criterion->response lexical containment\n")
    cells = {}
    for tag, x in (("own_x_original", own_o), ("own_x_fresh", own_f),
                   ("donor_x_original", don_o), ("donor_x_fresh", don_f)):
        m, lo, hi = ci(x)
        cells[tag] = [m, lo, hi]
        print(f"  {tag:20s} {m:.4f} [{lo:.4f},{hi:.4f}]")

    adv_o, adv_f = own_o - don_o, own_f - don_f
    collapse = adv_o - adv_f
    ao, alo, ahi = ci(adv_o)
    af, flo, fhi = ci(adv_f)
    cm, clo, chi = ci(collapse)
    print(f"\n  overlap advantage ORIGINAL {ao:+.4f} [{alo:+.4f},{ahi:+.4f}]")
    print(f"  overlap advantage FRESH    {af:+.4f} [{flo:+.4f},{fhi:+.4f}]")
    print(f"  COLLAPSE                   {cm:+.4f} [{clo:+.4f},{chi:+.4f}]"
          f"   sd across prompts {np.nanstd(collapse):.4f}")

    r12 = json.loads(a.r12.read_text())
    pid2i = {p_: i for i, p_ in enumerate(r12["sets"]["ORIGINAL"]["per_prompt"]["pids"])}
    drop = (np.array(r12["sets"]["ORIGINAL"]["per_prompt"]["attribution"], float)
            - np.array(r12["sets"]["FRESH"]["per_prompt"]["attribution"], float))
    idx = [pid2i[it["pid"]] for it in items if it["pid"] in pid2i]
    dd = drop[idx]
    keep = np.isfinite(collapse) & np.isfinite(dd)
    r = float(np.corrcoef(collapse[keep], dd[keep])[0, 1])
    bs = np.array([float(np.corrcoef(collapse[keep][i], dd[keep][i])[0, 1])
                   for i in (rng.integers(0, keep.sum(), keep.sum()) for _ in range(a.boot))])
    rlo, rhi = np.percentile(bs[np.isfinite(bs)], [2.5, 97.5])
    print(f"\n  corr(collapse, attribution drop) {r:+.4f} [{rlo:+.4f},{rhi:+.4f}]  "
          f"n={int(keep.sum())}")

    real = bool(clo > 0)
    explains = bool(rlo > 0)
    if real and not explains:
        verdict = (
            f"THE MECHANISM IS REAL AND DOES NOT EXPLAIN r12. Own criteria contain "
            f"{cells['own_x_original'][0]:.4f} of their words in the original responses and "
            f"{cells['own_x_fresh'][0]:.4f} in fresh ones, while donor criteria sit near "
            f"{cells['donor_x_original'][0]:.4f} on both -- so the own-rubric overlap "
            f"advantage really does collapse, by {cm:+.4f} [{clo:+.4f},{chi:+.4f}]. Given "
            f"r52's causal +0.2507, that collapse must depress own-rubric satisfaction on "
            f"fresh responses. But it does NOT predict WHICH prompts show the attribution "
            f"drop: corr = {r:+.4f} [{rlo:+.4f},{rhi:+.4f}]. "
            f"WHAT THIS DOES NOT RULE OUT: a UNIFORM contribution. The collapse varies "
            f"across prompts with sd {np.nanstd(collapse):.4f}; a component that shifts "
            f"every prompt equally would correlate with nothing while still moving the "
            f"aggregate, and this design cannot see it")
    elif real and explains:
        verdict = (
            f"THE OVERLAP COLLAPSE TRACKS THE DROP: corr {r:+.4f} [{rlo:+.4f},{rhi:+.4f}], "
            f"with the advantage falling {cm:+.4f}. Combined with r52's causal result this "
            f"is a mechanism for r12 rather than a correlate")
    else:
        verdict = (
            f"NO OVERLAP COLLAPSE: the own-vs-donor advantage moves {cm:+.4f} "
            f"[{clo:+.4f},{chi:+.4f}] between response sets, so the mechanism r52 makes "
            f"available does not arise here")
    print(f"\n-> {verdict}")

    _RES.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({
        "prompts": n, "containment": cells,
        "advantage_original": [ao, alo, ahi], "advantage_fresh": [af, flo, fhi],
        "collapse": [cm, clo, chi], "collapse_sd": float(np.nanstd(collapse)),
        "corr_collapse_with_drop": [r, rlo, rhi], "n_corr": int(keep.sum()),
        "mechanism_real": real, "mechanism_explains_r12": explains,
        "verdict": verdict, "outcome_variable_scope": OUTCOME_SCOPE,
        "scope": ("A zero per-prompt correlation does not exclude a UNIFORM contribution: "
                  "a component shifting every prompt's attribution equally correlates with "
                  "nothing while still moving the aggregate. Separating that needs an "
                  "intervention on overlap in the transfer setting, not an observation of "
                  "it. Half of every correlation here is proxy-world (entry 50)."),
    }, indent=1))
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
