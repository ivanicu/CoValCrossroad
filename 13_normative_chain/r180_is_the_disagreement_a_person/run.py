"""The 38% that no aggregation removes: is it people differing, or is it noise?

r179 established the ceiling. A predictor that always names the crowd's modal choice reaches
62.5%, so 37.5% of assessments disagree with their own prompt's majority and no aggregation
recovers them. I refused to call that "genuine disagreement" because the flattering reading of an
unmeasured quantity is exactly the error this sweep keeps catching. This round measures it.

The two worlds make opposite predictions and they are cheap to separate:

  STRUCTURED   people differ systematically. A rater who prefers long answers on Monday prefers
               them on Tuesday; a rater who breaks from the majority does so repeatedly. Then a
               trait measured on half of someone's assessments PREDICTS the other half, and the
               residual is normative content that a prompt-level aggregate is throwing away.
  NOISE        the same person is inconsistent. A trait measured on half their work predicts
               nothing about the other half, the disagreement is unattributable, and collecting
               1,012 people rather than 100 buys precision but no additional structure.

THE INSTRUMENT IS SPLIT-HALF RELIABILITY, WHICH IS THE RIGHT TOOL AND HAS AN EXACT NULL. For each
rater with enough assessments, split them at random, compute the trait on each half, and correlate
across raters. A real trait gives a positive correlation. Sampling noise alone gives zero -- not
approximately zero, exactly zero in expectation -- so the null needs no simulation to be trusted,
though it is simulated anyway by permuting which rater each assessment belongs to.

Spearman-Brown is applied because a half-length measurement is noisier than the full one, and the
quantity anyone would want to quote is the reliability of the full instrument.

THREE TRAITS, chosen because each would mean something different if it were real:
  length preference   how often this person's top choice is the longest response. A stylistic
                      disposition, and the one r177 showed has population-level force.
  nonconformity       how often this person's top choice differs from the prompt's majority.
                      If stable, some people systematically dissent -- which is the single most
                      consequential thing a collective-alignment dataset could contain, because
                      it is exactly what majority aggregation deletes.
  veto propensity     how often this person flags anything as unacceptable at all. Capped at five
                      per rater by the census's ceiling finding, so it is the weakest of the three
                      and is reported with that limit attached.

PREREGISTERED: a Spearman-Brown reliability above 0.30 counts as a real individual difference;
below 0.10 counts as absent; between them is UNVERIFIED and will be reported as such rather than
rounded toward whichever story is running.
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
LETTERS = "ABCD"
SEEDS = list(range(5))
MIN_ASSESSMENTS = 6
HI, LO = 0.30, 0.10


def top_of(s):
    for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
        g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
        if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
            return g[0]
        break
    return None


def spearman_brown(r):
    return 2 * r / (1 + r) if r > -1 else float("nan")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    lens = {}
    for c in cmp_:
        o = {}
        for i, r in enumerate(c.get("responses") or []):
            key = str(r.get("response_index", LETTERS[i])).strip().upper()
            if key in LETTERS:
                o[key] = len(" ".join(m.get("content") or ""
                                      for m in (r.get("messages") or [])
                                      if isinstance(m.get("content"), str)))
        if len(o) == 4:
            lens[c["prompt_id"]] = o

    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    # prompt-level majority, over everyone
    tops = defaultdict(list)
    for a in ann:
        for s in a.get("assessments", []):
            t = top_of(s)
            if t:
                tops[s.get("conversation_id")].append((a["annotator_id"], t))

    # per-rater event lists: one row per assessment, carrying each trait's 0/1 outcome
    per = defaultdict(list)
    for a in ann:
        aid = a["annotator_id"]
        for s in a.get("assessments", []):
            pid = s.get("conversation_id")
            t = top_of(s)
            b = s.get("ranking_blocks") or {}
            asked = bool(b.get("unacceptable") or b.get("personal"))
            vetoed = any((blk.get("rating") or []) for blk in (b.get("unacceptable") or []))
            rat = []
            for kk in ("world", "personal", "unacceptable"):
                for blk in (b.get(kk) or []):
                    if blk.get("rationale"):
                        rat.append(len(blk["rationale"]))
            row = {"pid": pid, "veto_asked": asked, "veto": 1.0 if vetoed else 0.0,
                   "effort": float(np.mean(rat)) if rat else None}
            if t and pid in lens:
                row["long"] = 1.0 if t == max(lens[pid], key=lens[pid].get) else 0.0
                others = [x for who, x in tops.get(pid, []) if who != aid]
                if others:
                    c = Counter(others)
                    mx = max(c.values())
                    row["nonconf"] = 0.0 if t in [k for k, v in c.items() if v == mx] else 1.0
                    # THE CONFOUND THAT DECIDES THIS ROUND, and it is not optional. Raters see
                    # DIFFERENT prompts. On a contested prompt almost everyone departs from the
                    # majority, so a rater who happened to draw contested prompts scores high on
                    # BOTH halves and the reliability is a property of their ASSIGNMENT, not of
                    # them. The expected nonconformity of a random rater on this prompt is
                    # 1 - (majority share among the others), and the residual is what is left once
                    # that is removed. A trait that survives residualization is a person.
                    row["nonconf_exp"] = 1.0 - mx / len(others)
                    row["nonconf_res"] = row["nonconf"] - row["nonconf_exp"]
            per[aid].append(row)

    print(f"raters {len(per)};  with >= {MIN_ASSESSMENTS} assessments: "
          f"{sum(1 for v in per.values() if len(v) >= MIN_ASSESSMENTS)}")

    def reliability(field, gate=None, permute=False, seed=0):
        rng = random.Random(seed)
        pool = []
        if permute:
            # NULL: keep every event, destroy which rater it belongs to, preserve rater sizes
            allrows = [r for v in per.values() for r in v]
            rng.shuffle(allrows)
            k, rebuilt = 0, {}
            for aid, v in per.items():
                rebuilt[aid] = allrows[k:k + len(v)]
                k += len(v)
            src = rebuilt
        else:
            src = per
        for _aid, v in src.items():
            ev = [r[field] for r in v
                  if field in r and (gate is None or r.get(gate))]
            if len(ev) < MIN_ASSESSMENTS:
                continue
            rng.shuffle(ev)
            h = len(ev) // 2
            a_, b_ = ev[:h], ev[h:2 * h]
            pool.append((float(np.mean(a_)), float(np.mean(b_))))
        if len(pool) < 30:
            return None, len(pool)
        A = np.array([x for x, _ in pool])
        B = np.array([y for _, y in pool])
        if A.std() == 0 or B.std() == 0:
            return 0.0, len(pool)
        return float(np.corrcoef(A, B)[0, 1]), len(pool)

    TRAITS = [("long", None, "length preference (top choice is the longest)"),
              ("nonconf", None, "nonconformity (top choice differs from the majority)"),
              ("nonconf_exp", None, "  ...prompt difficulty alone (assignment, not person)"),
              ("nonconf_res", None, "  ...nonconformity RESIDUALIZED on prompt difficulty"),
              ("veto", "veto_asked", "veto propensity (flags anything unacceptable)")]

    print("\n" + "=" * 78)
    print("SPLIT-HALF RELIABILITY -- does a trait measured on half a rater's work predict the "
          "other half")
    print("=" * 78)
    print(f"  {'trait':52s} {'r':>7s} {'S-B':>7s} {'null':>7s}  n     verdict")
    out = []
    for field, gate, label in TRAITS:
        rs, ns = [], 0
        for sd in SEEDS:
            r, n = reliability(field, gate, seed=sd)
            if r is not None:
                rs.append(r)
                ns = n
        nulls = []
        for sd in SEEDS:
            r, _ = reliability(field, gate, permute=True, seed=100 + sd)
            if r is not None:
                nulls.append(r)
        if not rs:
            print(f"  {label:52s} {'--':>7s} {'--':>7s} {'--':>7s}  too few raters")
            continue
        r = float(np.mean(rs))
        sb = spearman_brown(r)
        nl = float(np.mean(nulls)) if nulls else float("nan")
        v = ("REAL" if sb > HI else "ABSENT" if sb < LO else "UNVERIFIED")
        print(f"  {label:52s} {r:+7.3f} {sb:+7.3f} {nl:+7.3f}  {ns:<5d} {v}")
        out.append({"trait": label, "field": field, "r_halves": r, "spearman_brown": sb,
                    "permutation_null": nl, "raters": ns, "verdict": v,
                    "seed_spread": float(np.std(rs))})

    print(f"\n  preregistered bands: S-B > {HI} REAL, < {LO} ABSENT, between UNVERIFIED.")
    print(f"  the permutation null destroys rater identity while preserving every event and every")
    print(f"  rater's workload, so a non-zero null would mean the estimator invents structure.")

    # ---------------------------------------------------------------- what it means for the ceiling
    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    res = next((o for o in out if o["field"] == "nonconf_res"), None)
    exp = next((o for o in out if o["field"] == "nonconf_exp"), None)
    raw = next((o for o in out if o["field"] == "nonconf"), None)
    if res and exp and raw:
        print(f"  THE DECOMPOSITION OF NONCONFORMITY:")
        print(f"    raw                       S-B {raw['spearman_brown']:+.3f}")
        print(f"    prompt difficulty alone   S-B {exp['spearman_brown']:+.3f}   "
              f"<- pure assignment; this much would appear for a rater with no disposition at all")
        print(f"    residualized on it        S-B {res['spearman_brown']:+.3f}   <- the PERSON")
        if res["spearman_brown"] > HI:
            print(f"    The trait survives removing which prompts the rater drew. It is a person.")
        elif res["spearman_brown"] < LO:
            print(f"    NOTHING SURVIVES. The apparent trait was the prompt assignment, and the raw")
            print(f"    reliability of {raw['spearman_brown']:+.3f} is a statement about the sampler.")
        else:
            print(f"    Between the bands: UNVERIFIED after the control, and the raw number must")
            print(f"    not be quoted without it.")
    real = [o for o in out if o["verdict"] == "REAL" and o["field"] == "nonconf_res"]
    if real:
        print(f"  Nonconformity survives its own confound control:")
        for o in real:
            print(f"    {o['trait']}  S-B {o['spearman_brown']:+.3f}")
        print(f"  So part of r179's unreachable 37.5% is a PERSON, not noise. A rater who departs")
        print(f"  from the majority on one prompt departs on the next, which is precisely the")
        print(f"  signal that majority aggregation deletes -- and the release's stated purpose is")
        print(f"  collective alignment, which is aggregation.")
    else:
        print(f"  No trait clears the preregistered bar. On this evidence the disagreement above")
        print(f"  the ceiling is not attributable to stable individual dispositions, and a")
        print(f"  prompt-level aggregate is not discarding recoverable structure.")
    # THE LAST ALTERNATIVE, and it survives everything above: a rater who answers CARELESSLY also
    # departs from the majority at a stable rate. Stable dissent and stable inattention are the same
    # split-half signature. They differ in effort, and the rationales are a free effort proxy -- an
    # inattentive rater writes less. If nonconformity were low effort, the two would be strongly
    # negatively correlated across raters.
    xs, ys = [], []
    for _aid, v in per.items():
        nnc = [r["nonconf"] for r in v if "nonconf" in r]
        eff = [r["effort"] for r in v if r.get("effort") is not None]
        if len(nnc) >= MIN_ASSESSMENTS and len(eff) >= MIN_ASSESSMENTS:
            xs.append(float(np.mean(nnc)))
            ys.append(float(np.mean(eff)))
    reff = float(np.corrcoef(xs, ys)[0, 1]) if len(xs) > 30 else float("nan")
    print(f"\n  IS IT JUST INATTENTION? correlation across {len(xs)} raters between nonconformity")
    print(f"  and mean rationale length (an effort proxy): r = {reff:+.3f}")
    if abs(reff) < 0.15:
        print(f"    Effectively none. Whatever makes a rater dissent consistently, it is not that")
        print(f"    they are writing less -- the low-effort reading is not supported. It is NOT")
        print(f"    ruled out either: rationale length is a proxy for effort, not a measure of it,")
        print(f"    and the release ships no timing data, which is what would settle it.")
    else:
        print(f"    Substantial. Part of the nonconformity trait may be low effort rather than")
        print(f"    dissent, and the finding must be reported with that alternative live.")

    nc = res
    if nc:
        print(f"\n  The load-bearing one is nonconformity at S-B {nc['spearman_brown']:+.3f}: it is")
        print(f"  the only trait whose reality changes what an aggregation pipeline SHOULD do,")
        print(f"  rather than merely describing a stylistic quirk of the panel.")

    (OUT / "person_or_noise.json").write_text(json.dumps(
        {"raters": len(per), "min_assessments": MIN_ASSESSMENTS, "seeds": SEEDS,
         "bands": {"real_above": HI, "absent_below": LO}, "traits": out,
         "nonconformity_vs_effort_r": reff,
         "effort_proxy_limit": "rationale length proxies effort; no timing data ships, so the "
                               "low-effort alternative is unsupported rather than excluded"},
        indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
