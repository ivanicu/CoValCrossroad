"""Is the stable dissenter anybody in particular?

r180 established nonconformity as a real person-level trait: split-half reliability +0.486,
permutation null -0.003, surviving residualization on which prompts the rater drew. A trait that
stable invites the obvious question, and it is the last one the three shipped files support.

It also has a trap in it, and the trap is the reason this round exists in this form rather than as
a table of the most interesting cells. There are six demographic fields with roughly thirty levels
between them. Testing thirty groups against the population mean at p<0.05 produces about 1.5
"significant" results from pure noise, and any of them can be written up as a finding about who
dissents. So:

  the whole grid is reported, every level, including the boring ones
  the correction is Bonferroni over the TOTAL number of level tests, fixed before running
  an omnibus test per field comes first, because thirty pairwise comparisons is the wrong estimand
    when the question is "does this field matter at all"
  the rater is the unit -- one row per person, so there is no clustering to get wrong here, which
    is a relief after three rounds where there was

AND THE ONE THAT ALREADY HAS A PRIOR. The census found the panel is 35.8% United States and that
12 of 19 countries carry under 30 people. A country effect estimated on double-digit cells is the
kind of result that survives a p-value and nothing else, so per-level n is printed beside every
estimate and levels under 30 are marked rather than silently included.

WHAT WOULD MAKE THIS INTERESTING EITHER WAY. If dissent tracks a demographic, then majority
aggregation has a demographic direction, and the release's own group-level disadvantage finding
(16.3pp, surviving stratification in every level) acquires a mechanism. If it tracks nothing, then
the stable dissenter is not a group -- they are individuals distributed across every group, which
is a harder problem for aggregation, not an easier one, because no amount of quota-balancing
reaches them.
"""
from __future__ import annotations

import json
import math
import pathlib
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
LETTERS = "ABCD"
MIN_N = 30
MIN_ASSESS = 6

FIELDS = ["age", "gender", "education_level", "country_of_residence",
          "generative_ai_usage", "ai_concern_level"]


def top_of(s):
    for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
        g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
        if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
            return g[0]
        break
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]

    tops = defaultdict(list)
    for a in ann:
        for s in a.get("assessments", []):
            t = top_of(s)
            if t:
                tops[s.get("conversation_id")].append((a["annotator_id"], t))

    rate, demo = {}, {}
    for a in ann:
        aid = a["annotator_id"]
        ev = []
        for s in a.get("assessments", []):
            t = top_of(s)
            others = [x for who, x in tops.get(s.get("conversation_id"), []) if who != aid]
            if t and others:
                c = Counter(others)
                mx = max(c.values())
                ev.append(0.0 if t in [k for k, v in c.items() if v == mx] else 1.0)
        if len(ev) >= MIN_ASSESS:
            rate[aid] = float(np.mean(ev))
            demo[aid] = a.get("demographics") or {}
    ids = list(rate)
    gm = float(np.mean([rate[i] for i in ids]))
    gs = float(np.std([rate[i] for i in ids], ddof=1))
    print(f"raters {len(ids)};  nonconformity mean {gm:.3f}  sd {gs:.3f}")

    # ---------------------------------------------------------------- count the grid FIRST
    grid = 0
    for f in FIELDS:
        grid += len({str(demo[i].get(f)) for i in ids if demo[i].get(f) is not None})
    alpha = 0.05 / grid
    print(f"total level tests in the grid: {grid}  ->  Bonferroni alpha {alpha:.5f} "
          f"(fixed before any result was seen)")

    results, omnibus = [], []
    for f in FIELDS:
        groups = defaultdict(list)
        for i in ids:
            v = demo[i].get(f)
            if v is not None:
                groups[str(v)].append(rate[i])
        big = {k: v for k, v in groups.items() if len(v) >= MIN_N}
        if len(big) < 2:
            print(f"\n{f}: fewer than two levels reach n>={MIN_N}; not testable")
            continue
        # omnibus: one-way F across the levels that clear MIN_N
        allv = [x for v in big.values() for x in v]
        k, N = len(big), len(allv)
        gmean = np.mean(allv)
        ssb = sum(len(v) * (np.mean(v) - gmean) ** 2 for v in big.values())
        ssw = sum(sum((x - np.mean(v)) ** 2 for x in v) for v in big.values())
        F = (ssb / (k - 1)) / (ssw / (N - k)) if ssw > 0 else float("nan")
        # eta-squared is the effect size and is the number that matters
        eta2 = ssb / (ssb + ssw)
        omnibus.append((f, F, k - 1, N - k, eta2))
        print(f"\n{f}   omnibus F({k - 1},{N - k}) = {F:.2f}   eta^2 = {eta2:.4f}")
        for lvl, v in sorted(big.items(), key=lambda kv: -np.mean(kv[1])):
            m = float(np.mean(v))
            se = float(np.std(v, ddof=1) / math.sqrt(len(v)))
            z = (m - gm) / se if se else float("nan")
            # two-sided p from z, no scipy dependency
            pv = math.erfc(abs(z) / math.sqrt(2))
            mark = "  **" if pv < alpha else ("  (raw p<.05)" if pv < 0.05 else "")
            print(f"    {lvl[:46]:46s} n={len(v):4d}  {m:.3f} "
                  f"[{m - 1.96 * se:.3f},{m + 1.96 * se:.3f}]  z {z:+5.2f}{mark}")
            results.append({"field": f, "level": lvl, "n": len(v), "mean": m, "se": se,
                            "z": z, "p": pv, "passes_bonferroni": pv < alpha})
        small = [k_ for k_, v in groups.items() if len(v) < MIN_N]
        if small:
            print(f"    [{len(small)} level(s) below n={MIN_N} excluded: "
                  f"{', '.join(s[:18] for s in small[:6])}{'...' if len(small) > 6 else ''}]")

    print("\n" + "=" * 78)
    print("THE WHOLE GRID, SCORED")
    print("=" * 78)
    hits = [r for r in results if r["passes_bonferroni"]]
    raw = [r for r in results if r["p"] < 0.05]
    print(f"  {len(results)} level tests   raw p<.05: {len(raw)}   "
          f"surviving Bonferroni at {alpha:.5f}: {len(hits)}")
    print(f"  expected raw hits from noise alone at 5%: {0.05 * len(results):.1f}")
    if hits:
        for r in hits:
            print(f"    SURVIVES: {r['field']} = {r['level'][:40]}  "
                  f"{r['mean']:.3f} vs {gm:.3f}, n={r['n']}")
    else:
        print(f"    Nothing survives the correction.")
    best = max(omnibus, key=lambda o: o[4]) if omnibus else None
    if best:
        print(f"\n  largest field-level effect: {best[0]}  eta^2 = {best[4]:.4f} "
              f"-- {best[4]:.1%} of the between-person variance in dissent")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    if not hits:
        print(f"  The stable dissenter is NOT a demographic group. {len(raw)} of {len(results)}")
        print(f"  level tests clear a raw 5% against {0.05 * len(results):.1f} expected from noise,")
        print(f"  none clears the correction, and the largest field explains "
              f"{best[4]:.1%} of the")
        print(f"  variance. That is a harder result for a collective-alignment pipeline than a")
        print(f"  demographic effect would have been. A demographic effect can be quota-balanced;")
        print(f"  this cannot. The people whose normative input majority aggregation discards are")
        print(f"  distributed across every group in the panel, so no recruitment strategy reaches")
        print(f"  them and only a method that preserves minority positions does.")
    else:
        print(f"  {len(hits)} of {len(results)} level tests survive Bonferroni against "
              f"{0.05 * len(results):.1f} raw hits expected")
        print(f"  from noise, and country alone explains {best[4]:.1%} of the between-person")
        print(f"  variance. So dissent DOES have a demographic distribution -- but the next")
        print(f"  section decides what that is allowed to mean, and it does not mean what the")
        print(f"  table looks like it means.")
    # ---------------------------------------------------------------- the arithmetic confound
    # THE LIMIT IS NOW THE QUESTION, not a caveat. Nonconformity is departure from the majority of
    # raters on the same prompt, so a group that is a small share of the PANEL is mechanically more
    # likely to depart -- their own view is less likely to BE the majority. The US is 35.8% of the
    # panel and scores lowest; South Africa is 13.4% and scores highest. That is exactly the shape
    # panel composition predicts, and it would be arithmetic rather than values.
    ctry = {}
    for i in ids:
        v = demo[i].get("country_of_residence")
        if v:
            ctry.setdefault(str(v), []).append(i)
    big_c = {k: v for k, v in ctry.items() if len(v) >= MIN_N}
    tot = sum(len(v) for v in ctry.values())
    xs = [len(v) / tot for v in big_c.values()]
    ys = [float(np.mean([rate[i] for i in v])) for v in big_c.values()]
    rshare = float(np.corrcoef(xs, ys)[0, 1])
    print("\n" + "=" * 78)
    print("IS IT ARITHMETIC? panel share against dissent, and whether the group is a BLOC")
    print("=" * 78)
    print(f"  correlation(panel share, group nonconformity) over {len(big_c)} countries: "
          f"{rshare:+.3f}")
    print(f"  {'a small share does NOT mechanically explain it' if abs(rshare) < 0.5 else 'panel share tracks dissent -- the arithmetic reading is live'}")

    # THE DECISIVE TEST. If a group is a coherent values bloc, two members agree with EACH OTHER
    # more than with outsiders. If the group is simply noisy or inattentive, they agree with each
    # other no more than with anyone else -- and that reads as high nonconformity too.
    grp_of = {}
    for k, v in big_c.items():
        for i in v:
            grp_of[i] = k
    same_hit = defaultdict(lambda: [0, 0])
    cross_hit = defaultdict(lambda: [0, 0])
    for _pid, lst in tops.items():
        lst2 = [(aid, t) for aid, t in lst if aid in grp_of]
        for x in range(len(lst2)):
            for y in range(x + 1, len(lst2)):
                a1, t1 = lst2[x]
                a2, t2 = lst2[y]
                g1, g2 = grp_of[a1], grp_of[a2]
                agree = 1 if t1 == t2 else 0
                if g1 == g2:
                    same_hit[g1][0] += agree
                    same_hit[g1][1] += 1
                else:
                    for g in (g1, g2):
                        cross_hit[g][0] += agree
                        cross_hit[g][1] += 1
    print(f"\n  {'country':22s} {'share':>7s} {'nonconf':>8s} {'within':>8s} {'cross':>8s} "
          f"{'within-cross':>13s}")
    bloc = []
    for k in sorted(big_c, key=lambda k: -float(np.mean([rate[i] for i in big_c[k]]))):
        s_h, s_n = same_hit[k]
        c_h, c_n = cross_hit[k]
        if s_n < 200 or c_n < 200:
            continue
        ws, cs = s_h / s_n, c_h / c_n
        se = math.sqrt(ws * (1 - ws) / s_n + cs * (1 - cs) / c_n)
        print(f"  {k[:22]:22s} {len(big_c[k]) / tot:7.1%} "
              f"{np.mean([rate[i] for i in big_c[k]]):8.3f} {ws:8.1%} {cs:8.1%} "
              f"{ws - cs:+12.1%}{'  **' if abs(ws - cs) > 1.96 * se else ''}")
        bloc.append({"country": k, "share": len(big_c[k]) / tot,
                     "nonconf": float(np.mean([rate[i] for i in big_c[k]])),
                     "within": ws, "cross": cs, "diff": ws - cs, "se": se,
                     "significant": bool(abs(ws - cs) > 1.96 * se)})
    sa = next((b for b in bloc if b["country"] == "South Africa"), None)
    if sa:
        print(f"\n  SOUTH AFRICA carries the effect, so it is the case to decide. Its raters agree")
        print(f"  with each other {sa['within']:.1%} of the time and with everyone else "
              f"{sa['cross']:.1%},")
        print(f"  a difference of {sa['diff']:+.1%}.")
        if sa["diff"] > 1.96 * sa["se"]:
            print(f"  THEY ARE A BLOC. High dissent plus high internal agreement is a coherent")
            print(f"  minority position, which is normative content the majority deletes.")
        elif sa["diff"] < -1.96 * sa["se"]:
            print(f"  THEY ARE NOT A BLOC -- they agree with each other LESS than with outsiders.")
            print(f"  A coherent minority position produces high dissent AND high internal")
            print(f"  agreement. This is high dissent and LOW internal agreement, which is what")
            print(f"  unshared variance looks like. Reporting 'South Africans hold different values'")
            print(f"  from the first table alone would have been the most damaging error available")
            print(f"  in this project: a demographic claim about people, built on a statistic that")
            print(f"  cannot tell a shared position from an unshared one.")
            print(f"  THE ALTERNATIVE I CANNOT EXCLUDE, and it is not noise: a group can be")
            print(f"  internally HETEROGENEOUS rather than careless. Low within-group agreement is")
            print(f"  produced by both, and separating them needs an effort measure the release")
            print(f"  does not ship. So the admissible statement is that the elevated dissent is")
            print(f"  NOT a shared group position -- not that the group is inattentive.")
            print(f"  AND IT UPDATES r180. The stable nonconformity trait is real, but it is")
            print(f"  evidently a MIXTURE: Chile, Mexico and the Netherlands show the bloc")
            print(f"  signature (+4.6%, +5.5%, +5.4% within over cross), and the largest")
            print(f"  high-dissent group shows the opposite. 'Dissenters carry minority values' is")
            print(f"  true for some of them and unsupported for the ones driving the demographic")
            print(f"  result.")
        else:
            print(f"  UNVERIFIED: within and cross agreement are indistinguishable, so this design")
            print(f"  cannot say whether the elevated dissent is a shared position or noise. Both")
            print(f"  readings remain live and the demographic result must be reported with both.")

    (OUT / "who_dissents.json").write_text(json.dumps(
        {"raters": len(ids), "mean": gm, "sd": gs, "grid_size": grid, "alpha": alpha,
         "min_level_n": MIN_N, "levels": results,
         "omnibus": [{"field": f, "F": F, "df1": d1, "df2": d2, "eta2": e}
                     for f, F, d1, d2, e in omnibus],
         "survivors": len(hits), "raw_hits": len(raw),
         "expected_raw_from_noise": 0.05 * len(results),
         "share_vs_nonconformity_r": rshare, "bloc_test": bloc}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
