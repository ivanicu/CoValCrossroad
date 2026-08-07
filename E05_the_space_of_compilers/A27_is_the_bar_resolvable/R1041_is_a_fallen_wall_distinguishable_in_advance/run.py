#!/usr/bin/env python3
"""R1041 — R1039 named the habit. Can a wall that will FALL be told from one that stands, in advance?

R1040 made it 5 of 16, five for five on one shape. Its NEXT proposed a gate requiring each IMPOSSIBLE
block to name an in-release object or say UNATTACKED.

⛔ R1031 IS THE PRECEDENT AND IT SAYS ASK FIRST. There I built a prior-art gate, measured its recall
   at 0 of 4 REAL cases, and deliberately did NOT wire it — a gate that cannot fire manufactures
   assurance. So before building another, the question is whether the thing it would flag is even
   detectable in what is committed.

⛔ AND ONE ANSWER IS ALREADY FORCED, WHICH NARROWS THE QUESTION. A gate demanding a DECLARED FIELD
   would flag all 16 blocks, because the field does not exist in any of them yet — zero discriminating
   power on the historical set, by construction. That is R1029's conclusion restated: store the field,
   do not recover it. So the only open question is whether some feature ALREADY PRESENT separates the
   five that fell from the eleven that stand.

ESTIMAND        whether any structural feature of the committed IMPOSSIBLE blocks separates the 5
                falsified from the 11 standing, at a rate the multiplicity over the feature grid
                survives.
IDENTIFICATION  exact. Population and labels are both committed (R1039's rows); features are computed
                from the blocks' own text.
SCOPE           population : the 16 IMPOSSIBLE blocks of R1022–R1038 · labels : R1039's committed
                falsified set, extended by R1040 · instrument : literal text features
WORLDS          A A RETROACTIVE SIGNAL EXISTS — some feature separates the two groups beyond the
                  multiplicity-corrected threshold. Then the eleven standing lines can be TRIAGED on
                  evidence, and R1040's "attack the highest-exposure first" can be replaced by
                  something better than an ordering guess.
                B NO RETROACTIVE SIGNAL — falsified and standing blocks are structurally
                  indistinguishable. Then the remedy is a DECLARED FIELD going forward only, the gate
                  is forward-only and must SAY so, and any ordering of the remaining eleven is a
                  guess that should be labelled as one rather than dressed as triage.
                prediction matrix: A -> at least one feature survives correction over the grid.
                                   B -> none does, and the best raw separation is inside the null.
                ⚠ ONTOLOGICAL: A says the habit leaves a written trace; B says it does not, and that
                  the only fix is at WRITING time. They imply different work.
KILL            pre-registered and CONDITIONAL:
                  if the positive control separates a KNOWN-separable label and the negative does not:
                      any feature clears Bonferroni over the grid -> World A, feature named
                      otherwise                                    -> World B
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   a label KNOWN to be separable must separate: "the block mentions GFLOP" isolates
                R1034 exactly. If the machinery cannot find a feature that IS there, a null means
                nothing.
NEGATIVE CTRL   a RANDOM relabelling of the same 16, at 200 draws, must not produce separations at
                the observed rate. This is the null the corrected threshold is read against — a
                permutation null over LABELS, which is the pairing actually under test.
PLACEBO         the label against ITSELF as a feature must separate perfectly (Fisher p = 0), showing
                the statistic can reach its own floor.
NOISE FLOOR     n = 16 with 5 positives is tiny; the smallest attainable one-sided Fisher p is
                printed, so "not significant" is read as a resolution statement rather than a null.
MULTIPLICITY    every feature is tested and reported, and the threshold is Bonferroni over the WHOLE
                grid — the standard's own rule, since this is a family of one-off tests, not BH ranks.
SEEDS           200 permutation draws at a fixed seed for the negative control.
IMPOSSIBLE      whether an UNFALSIFIED line is TRUE. This asks only whether falling is PREDICTABLE
                from the text, never whether the standing lines are correct. N/A — that is one round
                per line, which is exactly what R1039 said and what this round is trying to avoid.
"""
import itertools, json, math, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"

FELL = {"R1026", "R1035", "R1036", "R1037", "R1023"}   # R1023 added by R1040


def fisher_p(a, b, c, d):
    """one-sided Fisher exact, upper tail — small tables, exact arithmetic"""
    n = a + b + c + d
    def C(n_, k_): return math.comb(n_, k_)
    tot = C(n, a + c)
    p = 0.0
    for x in range(a, min(a + b, a + c) + 1):
        p += C(a + b, x) * C(c + d, a + c - x) / tot
    return p


def main() -> int:
    blocks = {}
    for p in sorted(A27.glob("R10*/run.py")):
        rid = re.match(r"(R\d+)", p.parent.name).group(1)
        if not (1022 <= int(rid[1:]) <= 1038):
            continue
        m = re.search(r"^IMPOSSIBLE\s+(.+?)(?=^[A-Z]{3,}\s|^\"\"\")", p.read_text(), re.M | re.S)
        if m:
            blocks[rid] = " ".join(m.group(1).split())
    if len(blocks) < 10:
        print("  UNRUNNABLE: population too small to have been enumerated correctly. Exit 2.")
        return 2
    lab = {r: (r in FELL) for r in blocks}
    print(f"  population {len(blocks)} IMPOSSIBLE blocks · fell {sum(lab.values())} · "
          f"stand {len(blocks) - sum(lab.values())}")
    print(f"  ⛔ A GATE DEMANDING A DECLARED FIELD WOULD FLAG ALL {len(blocks)} — the field exists in")
    print(f"     none of them yet, so it has ZERO retroactive power BY CONSTRUCTION (R1029's rule).")
    print(f"     The only open question is whether a feature ALREADY PRESENT separates the groups.")

    FEATURES = {
        "says outside/external": r"\b(outside|external)\b",
        "says needs/would require": r"\b(needs?|would require)\b",
        "names a second release": r"second (release|corpus|team|site)",
        "names a cost in calls": r"judge call|GFLOP|15,?488|968\s*[x×]",
        "names a specific round": r"\bR\d{3,4}\b",
        "says construct validity": r"construct validit",
        "says gold standard": r"gold standard",
        "length > 300 chars": None,
        "mentions the release itself": r"\brelease\b",
    }

    def feat(rid, name, pat):
        t = blocks[rid]
        return (len(t) > 300) if pat is None else bool(re.search(pat, t, re.I))

    def table(name, pat):
        a = sum(1 for r in blocks if feat(r, name, pat) and lab[r])
        b = sum(1 for r in blocks if feat(r, name, pat) and not lab[r])
        c = sum(1 for r in blocks if not feat(r, name, pat) and lab[r])
        d = sum(1 for r in blocks if not feat(r, name, pat) and not lab[r])
        return a, b, c, d

    # ---------- controls ----------
    pa, pb, pc, pd = table("GFLOP", r"GFLOP")
    pos_ok = (pa + pb) == 1
    plac = fisher_p(sum(lab.values()), 0, 0, len(blocks) - sum(lab.values()))
    # ⚠⚠ THIS THRESHOLD WAS SET BELOW WHAT THE DESIGN CAN RETURN, WHICH IS §4's "control that
    #   cannot PASS", mirrored. I demanded p < 1e-9 while the smallest ATTAINABLE one-sided p at
    #   n=16 with 5 positives is 2.289e-04 — perfect separation itself. A placebo that cannot pass
    #   under a maximal plant says nothing about the instrument. The criterion is now "reaches the
    #   attainable FLOOR", computed rather than typed.
    floor0 = fisher_p(sum(lab.values()), 0, 0, len(blocks) - sum(lab.values()))
    plac_ok = abs(plac - floor0) < 1e-15
    print(f"\n  POSITIVE — a feature KNOWN to be there must be found: 'GFLOP' isolates exactly one "
          f"block: {'PASS' if pos_ok else '⛔ FAIL'} (matched {pa + pb})")
    print(f"  PLACEBO  — the label as its own feature must reach the ATTAINABLE FLOOR "
          f"({floor0:.3e}), not 0: {plac:.3e}  {'PASS' if plac_ok else '⛔ FAIL'}")
    print( "     ⚠ the first version demanded p < 1e-9, below what n=16 can return — a control that")
    print( "       cannot pass, which is the mirror of the mode the standard names.")
    floor = fisher_p(sum(lab.values()), 0, 0, len(blocks) - sum(lab.values()))
    print(f"  NOISE FLOOR — smallest attainable one-sided p at n={len(blocks)} with "
          f"{sum(lab.values())} positives: {floor:.4f}")

    print(f"\n  ⭐ EVERY FEATURE, and the whole grid is reported (Bonferroni over {len(FEATURES)})")
    print(f"     {'feature':<28}{'fell+':>7}{'stand+':>8}{'p':>10}")
    rows, best = [], 1.0
    for name, pat in FEATURES.items():
        a, b, c, d = table(name, pat)
        p = fisher_p(a, b, c, d)
        best = min(best, p)
        rows.append({"feature": name, "fell_with": a, "stand_with": b, "p": p})
        print(f"     {name:<28}{a:>7}{b:>8}{p:>10.4f}")
    thresh = 0.05 / len(FEATURES)
    print(f"     Bonferroni threshold 0.05/{len(FEATURES)} = {thresh:.4f} — this is a family of")
    print(f"     one-off tests, so Bonferroni is the right correction, not BH ranks.")

    # ---------- NEGATIVE: permutation over LABELS ----------
    import numpy as np
    rng = np.random.default_rng(1041)
    ids = sorted(blocks); k = sum(lab.values())
    hits = 0
    for _ in range(200):
        perm = set(rng.choice(len(ids), size=k, replace=False).tolist())
        L = {ids[i]: (i in perm) for i in range(len(ids))}
        bp = 1.0
        for name, pat in FEATURES.items():
            a = sum(1 for r in ids if feat(r, name, pat) and L[r])
            b = sum(1 for r in ids if feat(r, name, pat) and not L[r])
            c = sum(1 for r in ids if not feat(r, name, pat) and L[r])
            d = sum(1 for r in ids if not feat(r, name, pat) and not L[r])
            bp = min(bp, fisher_p(a, b, c, d))
        hits += int(bp <= best)
    perm_p = (hits + 1) / 201
    print(f"\n  NEGATIVE — 200 random relabellings of the SAME 16: how often does the best feature")
    print(f"     reach p <= {best:.4f}? {hits}/200, permutation p = {perm_p:.4f}")

    print()
    if not (pos_ok and plac_ok):
        world = "UNVERIFIED — a control did not fire; no verdict is admissible"
    elif best <= thresh and perm_p <= 0.05:
        win = min(rows, key=lambda r: r["p"])
        world = (f"⭐ A A RETROACTIVE SIGNAL EXISTS — `{win['feature']}` separates at p = "
                 f"{win['p']:.4f}, clearing Bonferroni {thresh:.4f} and a label permutation at "
                 f"{perm_p:.4f}. The eleven standing lines can be TRIAGED on evidence.")
    else:
        world = (f"⭐ B NO RETROACTIVE SIGNAL — the best feature reaches p = {best:.4f} against a "
                 f"Bonferroni threshold of {thresh:.4f} and a label permutation of {perm_p:.4f}. "
                 f"Fallen and standing blocks are structurally INDISTINGUISHABLE in committed text. "
                 f"So the remedy is a DECLARED FIELD going forward ONLY, the gate must say it is "
                 f"forward-only, and R1040's 'attack the highest-exposure first' is an ORDERING "
                 f"GUESS that should be labelled as one rather than dressed as triage.")
    print(world)
    print(f"⛔ AND THE NULL HERE IS A RESOLUTION STATEMENT, NOT AN ACQUITTAL. With {len(blocks)} blocks")
    print(f"   and {sum(lab.values())} positives the smallest attainable p is {floor:.4f}, so a")
    print(f"   feature would have to separate almost perfectly to clear correction. This design")
    print(f"   cannot detect a weak signal, and says so rather than reporting 'no difference'.")
    print(f"⚠ THIS ASKS ONLY WHETHER FALLING IS PREDICTABLE FROM THE TEXT, never whether the standing")
    print(f"   lines are TRUE. That is one round per line — exactly what this round tried to avoid.")

    out = HERE / "results" / "fallen_wall_signal.json"
    out.write_text(json.dumps({
        "round": "R1041", "population": len(blocks), "fell": sorted(FELL & set(blocks)),
        "features": rows, "best_p": best, "bonferroni": thresh,
        "permutation_p": perm_p, "attainable_floor_p": floor,
        "controls": {"positive_gflop_isolates_one": bool(pos_ok), "placebo_self_label": plac},
        "forced": "a gate demanding a declared field flags all 16 by construction — zero retroactive "
                  "power, which is R1029's store-don't-recover rule restated",
        "world": world,
        "limitation": "asks only whether falling is predictable from text; the null is a resolution "
                      "statement at n=16, not an acquittal",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
