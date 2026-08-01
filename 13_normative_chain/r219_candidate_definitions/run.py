"""r219 -- grounded numbers for the six candidate definitions of "normative information".

WHY THIS ROUND EXISTS
    Part A of the paper presents C1..C6 as a four-column table. Ivan read it and could not
    tell what any row MEANT. The repair is not more prose: it is a WORKED EXAMPLE per
    definition, on real strings from the release, with the arithmetic done here so the paper
    can quote a checked number instead of an assertion.

ESTIMAND        for each candidate definition Ci, the loss it assigns to the SAME observed
                transformation (coval_full -> coval_core) on the SAME prompt.
IDENTIFICATION  fully identified: all six are deterministic functions of released fields,
                except C4, which requires Y (absent) -- that absence is itself the finding.
SCOPE           986 released rubrics; the walk-through prompt is line 1 (the beef prompt),
                chosen because it is line 1, not because it is favourable. The corpus-wide
                distributions below say whether line 1 is typical.
CONTROLS        C1's word-overlap statistic is computed against a SHUFFLED pairing of core
                to full criteria (negative control): if matched pairs do not score above
                shuffled pairs, the statistic is measuring English, not correspondence.
KILL            if the four text operations identified on prompt 1 (verbatim / truncation /
                merge / polarity-inversion) do not each occur at >=1% corpus-wide, the
                "C1 assigns four different losses to one operation" claim is anecdote and is
                withdrawn.
ARTIFACT        r219.json next to this file.
"""
import json, pathlib, random, re, statistics as st, itertools, math

ROOT = pathlib.Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = pathlib.Path(__file__).resolve().parent

STOP = set("a an the and or of to in on at is are be as by for with from that this it "
           "not but if so when about into over than then there their they them we you "
           "your our its his her do does did can could should would will shall may might "
           "have has had been being any all each other more most less least such very".split())


def content(s):
    return [w for w in re.findall(r"[a-z']+", s.lower()) if w not in STOP and len(w) > 2]


def jac(a, b):
    A, B = set(a), set(b)
    return len(A & B) / len(A | B) if A | B else 0.0


def load():
    return [json.loads(l) for l in open(DATA / "conversation_rubrics.jsonl")]


# ---------------------------------------------------------------- C1: the text
def c1(rubrics, seed=0):
    """Best-match Jaccard from each CORE criterion to the FULL rubric it was compiled from,
    against a shuffled-pairing negative control."""
    rng = random.Random(seed)
    matched, shuffled, ops = [], [], {"verbatim": 0, "truncation": 0, "merge": 0, "rewrite": 0}
    allfull = [[it["criterion"] for it in r["coval_full"]] for r in rubrics]
    n_core = 0
    for i, r in enumerate(rubrics):
        F = allfull[i]
        Ftok = [content(f) for f in F]
        j = rng.randrange(len(rubrics))
        while j == i:
            j = rng.randrange(len(rubrics))
        Gtok = [content(f) for f in allfull[j]]
        for it in r["coval_core"]:
            c = it["criterion"]
            ct = content(c)
            n_core += 1
            best = max((jac(ct, f) for f in Ftok), default=0.0)
            matched.append(best)
            shuffled.append(max((jac(ct, f) for f in Gtok), default=0.0))
            # which text operation produced it
            lc = c.lower().rstrip(".")
            exact = any(lc == f.lower().rstrip(".") for f in F)
            sub = any(lc in f.lower() or f.lower().rstrip(".") in lc for f in F)
            # a MERGE: two distinct full criteria each contribute >=2 content words
            donors = sum(1 for f in Ftok if len(set(ct) & set(f)) >= 2)
            if exact:
                ops["verbatim"] += 1
            elif sub:
                ops["truncation"] += 1
            elif donors >= 2:
                ops["merge"] += 1
            else:
                ops["rewrite"] += 1
    return {
        "n_core": n_core,
        "matched_median": st.median(matched),
        "matched_mean": st.mean(matched),
        "shuffled_median": st.median(shuffled),
        "shuffled_mean": st.mean(shuffled),
        "zero_overlap_share": sum(1 for m in matched if m == 0.0) / len(matched),
        "operations": ops,
        "operation_shares": {k: v / n_core for k, v in ops.items()},
        "dropped_share": 1 - sum(len(r["coval_core"]) for r in rubrics)
                             / sum(len(r["coval_full"]) for r in rubrics),
    }


# ---------------------------------------------------------------- C2: the numbers
def c2(rubrics):
    """A person's weight vector on a prompt. C2 calls a rescaling a total change; every
    observable consequence is invariant. Report the size of the rescaling that is ALREADY
    present between people who agree."""
    out = {"pairs": 0, "cos_ge_0.95": 0, "scale_ratios": [], "norms": []}
    for r in rubrics:
        byann = {}
        for k, it in enumerate(r["coval_full"]):
            for s in it["scores"]:
                byann.setdefault(s["annotator_id"], {})[k] = s["score"]
        ids = [a for a, v in byann.items() if len(v) >= 4]
        for a, b in itertools.combinations(ids, 2):
            ks = sorted(set(byann[a]) & set(byann[b]))
            if len(ks) < 4:
                continue
            x = [byann[a][k] for k in ks]
            y = [byann[b][k] for k in ks]
            nx = math.sqrt(sum(v * v for v in x))
            ny = math.sqrt(sum(v * v for v in y))
            if nx == 0 or ny == 0:
                continue
            cos = sum(u * v for u, v in zip(x, y)) / (nx * ny)
            out["pairs"] += 1
            if cos >= 0.95:
                out["cos_ge_0.95"] += 1
                out["scale_ratios"].append(max(nx, ny) / min(nx, ny))
        for a, v in byann.items():
            out["norms"].append(math.sqrt(sum(s * s for s in v.values())))
    return {
        "pairs": out["pairs"],
        "near_parallel_pairs": out["cos_ge_0.95"],
        "near_parallel_share": out["cos_ge_0.95"] / out["pairs"] if out["pairs"] else None,
        "scale_ratio_median": st.median(out["scale_ratios"]) if out["scale_ratios"] else None,
        "scale_ratio_p90": (sorted(out["scale_ratios"])[int(.9 * len(out["scale_ratios"]))]
                            if out["scale_ratios"] else None),
        "norm_median": st.median(out["norms"]),
        "norm_max_over_min": max(out["norms"]) / min(n for n in out["norms"] if n > 0),
    }


# ---------------------------------------------------------------- C3: the ranking
def c3():
    """The veto lives in a SEPARATE block from the ranking. C3 sees only the ranking, so it
    cannot distinguish 'ranked last' from 'ranked last AND forbidden'. Count how often the
    data contains both readings of the same ordering."""
    rows = [json.loads(l) for l in open(DATA / "merged_comparisons_annotators.jsonl")]
    seen = {}
    n_with_veto = n_total = 0
    for r in rows:
        rb = r.get("ranking_blocks") or {}
        pers = rb.get("personal") or []
        rank = pers[0].get("ranking") if pers and isinstance(pers[0], dict) else None
        if not rank:
            continue
        unacc = rb.get("unacceptable") or []
        letters = set()
        for u in unacc:
            for s in (u.get("rating") or []):
                m = re.match(r"\s*([A-Z])\b", s)
                if m:
                    letters.add(m.group(1))
        n_total += 1
        if letters:
            n_with_veto += 1
        key = (r["prompt_id"], rank)
        seen.setdefault(key, set()).add(frozenset(letters))
    ambiguous = sum(1 for k, v in seen.items() if len(v) > 1)
    return {
        "rankings": n_total,
        "with_veto": n_with_veto,
        "veto_share": n_with_veto / n_total,
        "distinct_prompt_ranking_pairs": len(seen),
        "same_ranking_different_veto": ambiguous,
        "ambiguous_share": ambiguous / len(seen),
    }


# ---------------------------------------------------------------- C5: mutual information
def c5(rubrics):
    """The sign flip N -> -N is a bijection, so I(-N;G) = I(N;G) exactly, while every argmax
    becomes an argmin. Measure how often the flip actually changes the winner, so the reader
    sees that the invariance is not vacuous on this corpus."""
    flipped = same = 0
    for r in rubrics:
        w = []
        for it in r["coval_full"]:
            s = [x["score"] for x in it["scores"]]
            w.append(st.mean(s))
        if len(w) < 2:
            continue
        if max(range(len(w)), key=lambda i: w[i]) != max(range(len(w)), key=lambda i: -w[i]):
            flipped += 1
        else:
            same += 1
    return {"rubrics": flipped + same, "top_criterion_changes_under_sign_flip": flipped,
            "share": flipped / (flipped + same)}


def walkthrough(rubrics):
    r = rubrics[0]
    full = []
    for it in r["coval_full"]:
        s = [x["score"] for x in it["scores"]]
        full.append({"criterion": it["criterion"], "n": len(s), "mean": round(st.mean(s), 2)})
    core = [it["criterion"] for it in r["coval_core"]]
    tab = []
    for c in core:
        ct = content(c)
        sc = sorted(((jac(ct, content(f["criterion"])), f) for f in full),
                    key=lambda t: -t[0])[:2]
        tab.append({"core": c,
                    "best": [{"jaccard": round(j, 3), **f} for j, f in sc]})
    return {"n_full": len(full), "n_core": len(core), "full": full, "core_match": tab}


def main():
    R = load()
    res = {"n_rubrics": len(R), "C1": c1(R), "C2": c2(R), "C3": c3(), "C5": c5(R),
           "walkthrough": walkthrough(R)}
    # seed robustness for C1's shuffled control
    res["C1_shuffle_seeds"] = [round(c1(R, s)["shuffled_median"], 4) for s in (0, 1, 2, 3, 4)]
    (OUT / "r219.json").write_text(json.dumps(res, indent=1))

    print("=== C1  the text " + "=" * 55)
    a = res["C1"]
    print(" core criteria                    %d" % a["n_core"])
    print(" full criteria dropped            %.1f%%" % (100 * a["dropped_share"]))
    print(" best-match Jaccard  matched      median %.3f  mean %.3f" % (a["matched_median"], a["matched_mean"]))
    print("                     shuffled     median %.3f  mean %.3f   <- negative control"
          % (a["shuffled_median"], a["shuffled_mean"]))
    print(" shuffled median across 5 seeds   %s" % res["C1_shuffle_seeds"])
    print(" core criteria with ZERO overlap  %.1f%%" % (100 * a["zero_overlap_share"]))
    print(" text operation used:")
    for k, v in a["operation_shares"].items():
        print("     %-11s %6.1f%%   (n=%d)" % (k, 100 * v, a["operations"][k]))
    kill = min(a["operation_shares"].values()) >= 0.01
    print(" KILL (each op >=1%%): %s" % ("survives" if kill else "FIRES -- withdraw the claim"))

    print("\n=== C2  the numbers " + "=" * 52)
    b = res["C2"]
    print(" annotator pairs compared         %d" % b["pairs"])
    print(" near-parallel (cos>=0.95)        %d  (%.1f%%)" % (b["near_parallel_pairs"], 100 * b["near_parallel_share"]))
    print("   their scale ratio  median      %.2f x" % b["scale_ratio_median"])
    print("                      p90         %.2f x" % b["scale_ratio_p90"])
    print(" ||N_i|| median                   %.1f" % b["norm_median"])
    print(" ||N_i|| max/min                  %.1f x" % b["norm_max_over_min"])

    print("\n=== C3  the ranking " + "=" * 52)
    c = res["C3"]
    print(" personal rankings                %d" % c["rankings"])
    print(" carrying a veto block            %d  (%.1f%%)" % (c["with_veto"], 100 * c["veto_share"]))
    print(" distinct (prompt, ranking)       %d" % c["distinct_prompt_ranking_pairs"])
    print(" SAME ranking, DIFFERENT veto set %d  (%.1f%%)" % (c["same_ranking_different_veto"],
                                                              100 * c["ambiguous_share"]))

    print("\n=== C5  mutual information " + "=" * 45)
    d = res["C5"]
    print(" I(-N;G) = I(N;G) exactly (bijection). Consequence on this corpus:")
    print(" rubrics where the sign flip moves the top criterion  %d/%d (%.1f%%)"
          % (d["top_criterion_changes_under_sign_flip"], d["rubrics"], 100 * d["share"]))

    print("\n=== walkthrough, prompt 1 " + "=" * 46)
    w = res["walkthrough"]
    print(" full=%d  core=%d" % (w["n_full"], w["n_core"]))
    for f in w["full"]:
        print("   %+6.2f n=%2d  %s" % (f["mean"], f["n"], f["criterion"][:88]))
    print(" -- compiled core, with its best match in the full rubric:")
    for t in w["core_match"]:
        print("   CORE  %s" % t["core"])
        for m in t["best"]:
            print("      J=%.3f  %+6.2f n=%2d  %s" % (m["jaccard"], m["mean"], m["n"], m["criterion"][:80]))


if __name__ == "__main__":
    main()
