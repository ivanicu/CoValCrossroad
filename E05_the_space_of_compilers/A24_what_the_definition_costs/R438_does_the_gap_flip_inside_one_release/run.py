"""R438 -- if the GAP flips sign INSIDE one release, "the bars invert between releases" is the wrong
ontology and the real variable is whatever the strata differ on.

⛔ WHY THIS ATTACKS THE ONTOLOGY AND NOT THE NUMBER. R437's claim is structural -- clause ② and
   candidate ④ are two bars whose order flips -- and it rests on **n = 2 releases**. There is no
   third. So the cheapest attack is not more releases but a WITHIN-release split: if the sign of
   `GAP = BAR4 - BAR2` flips across strata of ONE release, then "release" is not the variable, and
   R437 named the wrong object.

⭐ AND THE STRATIFIER HAD TO BE CHECKED BEFORE THE DESIGN. R437's next-step line proposed splitting
   on "response count, prompt length, turn depth". **Response count is not a stratifier at home** --
   every prompt there carries exactly four responses by construction (`score.py: L = "ABCD"`). The
   two releases share no such axis, so a cross-release stratified sweep is not available at all.
   What IS available is decisive on its own: the second release has n in {2,3,4} with 5,204 / 456 /
   1,684 interactions, and a sign flip THERE falsifies the release-level ontology using one release,
   one statistic, and no cross-scale comparison. Seventh announced step checked; it survived, in a
   smaller form than announced.

ESTIMAND (named before the method)
    Within the second release, per stratum s of n_responses:
        BAR2(s) = accuracy of `generic` -- clause ②'s prompt-blind reference
        BAR4(s) = accuracy of the best criterion-free rule
        GAP(s)  = BAR4(s) - BAR2(s)
    The question is the SIGN of GAP(s) across s, and whether any flip is resolved.

⛔ THE DESIGN DECISION THAT DECIDES THE ANSWER, MADE EXPLICIT. BAR4 is a MAXIMUM over a family, and
   R435 measured that a maximum over a growing family climbs by construction. Re-selecting the best
   rule WITHIN each stratum is a max over 30 in a smaller sample -- it inflates BAR4 and biases the
   result toward "④ binds". Holding the globally-best rule fixed does not, but is then not "the best
   criterion-free rule in that stratum". **Both are computed and both are reported**; the KILL rests
   on the FIXED-rule version, and the re-selected version is reported as an UPPER BOUND on ④'s bar.
   Choosing only one of these would have been the whole finding, silently.

IDENTIFICATION
    Fully identified within the release. What is NOT identified: whether a stratum-level flip and a
    release-level flip are the same phenomenon -- that needs a stratifier both releases share, and
    there is none.

SCOPE  population : the second release, 7,342 interactions / 2,200 conversations, split by
                    n_responses in {2,3,4}
       instrument : Qwen3.5-2B-Base at k=4 for BAR2; none for BAR4
       baseline   : each stratum's own chance rate, 1/n, printed beside both bars
       regime     : top-1 accuracy, one release

WORLDS
    W-STABLE-SIGN   GAP has the same sign in every stratum where it resolves -> the release-level
                    ontology survives this attack. R437 stands, with one more thing it is not.
    W-FLIPS-INSIDE  GAP resolves with opposite signs in two strata -> "the bars invert between
                    releases" is the WRONG OBJECT. The real variable is whatever the strata differ
                    on -- here, the number of responses -- and R437's framing must be retracted in
                    favour of it.
    W-UNRESOLVED    GAP is inside its floor in every stratum but one -> the split has no power and
                    the attack fails to be an attack, which is a fact about this design and not an
                    acquittal of R437.

PREDICTION MATRIX
                     same sign everywhere   opposite signs resolved   nothing resolves
    W-STABLE-SIGN            0.9                    0.02                   0.1
    W-FLIPS-INSIDE           0.05                   0.9                    0.1
    W-UNRESOLVED             0.05                   0.08                   0.8

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    >=2 strata resolve AND their signs differ  -> W-FLIPS-INSIDE; R437's framing is RETRACTED
    >=2 strata resolve AND signs agree         -> W-STABLE-SIGN
    <2 strata resolve                          -> W-UNRESOLVED, and no claim either way
    a control fails                            -> UNVERIFIED

CONTROLS
    POSITIVE  a synthetic ORACLE arm must beat BOTH bars in EVERY stratum. If a perfect arm is not
              above the bars somewhere, the per-stratum comparison is broken there and any sign it
              reports in that stratum is noise.
    g=0       `generic` against ITSELF in each stratum must be exactly 0 -- BAR2 is that arm, so
              this is the placebo for the left-hand side of every GAP.
    NEGATIVE  each stratum's chance rate 1/n printed beside both bars: at n=2 chance is 0.5, so a
              GAP between two bars that both sit at 0.5 would be an ordering of two nulls, and the
              n=2 stratum is 71% of the corpus.
    SELECTION the fixed-rule and re-selected-rule versions are both reported; their difference IS
              the selection inflation, measured rather than argued.
    FLOOR     every GAP carries a paired cluster bootstrap over CONVERSATIONS (R413) within the
              stratum, >=3 seeds.

MULTIPLICITY  3 strata x 2 rule-selection modes = 6 cells, all reported; BH at q=0.10 over the whole
              grid, survivors and non-survivors both printed.
ARTIFACT      results/r438_within_release_flip.json
IMPOSSIBLE HERE, NAMED
    * a stratified CROSS-release sweep -- home has 4 responses by construction; no shared axis.
    * deciding whether a stratum flip and a release flip are the same phenomenon -- needs that
      shared axis.
    * the supremum over criterion-free rules -- R435's 30-member family, restated.

EXIT 0 W-STABLE-SIGN · 1 W-FLIPS-INSIDE · 2 W-UNRESOLVED or UNVERIFIED
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
ZEFF = 1.959964 + 0.841621


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, A24 / rel / "run.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def paired(a, b, convs, seeds=(61, 62, 63), B=300):
    d = [(sum(a[c]), sum(b[c]), len(a[c])) for c in convs if c in a and c in b]
    if not d:
        return None
    A = sum(x[0] for x in d); Bb = sum(x[1] for x in d); C = sum(x[2] for x in d)
    pt = (A - Bb) / C if C else float("nan")
    bs = []
    for sd in seeds:
        r = np.random.default_rng(sd)
        for _ in range(B):
            sel = [d[i] for i in r.choice(len(d), len(d), replace=True)]
            bs.append((sum(x[0] for x in sel) - sum(x[1] for x in sel))
                      / max(sum(x[2] for x in sel), 1))
    bs = np.array(bs)
    p = max(2 * min((bs <= 0).mean(), (bs >= 0).mean()), 1.0 / (len(bs) + 1))
    return pt, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)), \
        float(ZEFF * bs.std()), float(p), len(d)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    r433 = _load("r433", "R433_does_clause_two_transport_with_its_subject")
    r435 = _load("r435", "R435_is_a_sufficiency_clause_even_statable")

    s_gen, targets, _pv = r433.load_arm("sat_transport_generic")
    if s_gen is None:
        print("  UNRUNNABLE: the second release's generic arm is absent. Exit 2, never 0."); return 2
    P = r433.picks(s_gen, targets)

    texts = {}
    with open(ROOT / "data" / "utterances.jsonl") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            u = str(r.get("utterance_id"))
            if u:
                texts[u] = r.get("model_response") or ""

    items, dropped = [], 0
    for t in targets:
        k = (t["conv"], t["inter"])
        ch = [r["id"] for r in t["resp"] if r.get("chosen")]
        ids = [r["id"] for r in t["resp"]]
        if not ch or k not in P:
            continue
        if any(i not in texts for i in ids):
            dropped += 1; continue
        items.append((k, ids, ch[0], [r435.features(texts[i]) for i in ids]))

    print("R438 · does the GAP flip sign INSIDE one release?\n")
    print("  ⭐ the announced stratifiers were checked first: response count is NOT a stratifier at")
    print("     home (every prompt has 4 by construction), so no CROSS-release stratified sweep")
    print("     exists. The second release alone is decisive and needs no cross-scale comparison.\n")
    print(f"  usable interactions {len(items)} · dropped for missing text {dropped}")
    if len(items) < 500:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    RULES = r435.RULES

    def rule_hits(name, key, sign, subset):
        h = {}
        for (c, _i), ids, chosen, feats in subset:
            if key == "__pos__":
                pick = ids[-1] if sign > 0 else ids[0]
            else:
                vals = [f[key] for f in feats]
                pick = ids[int(np.argmax(vals)) if sign > 0 else int(np.argmin(vals))]
            h.setdefault(c, []).append(1.0 if pick == chosen else 0.0)
        return h

    def gen_hits(subset):
        h = {}
        for (c, i), _ids, chosen, _f in subset:
            h.setdefault(c, []).append(1.0 if P[(c, i)] == chosen else 0.0)
        return h

    strata = {}
    for it in items:
        strata.setdefault(len(it[1]), []).append(it)

    # global best rule, for the FIXED-rule mode
    allh = {r[0]: rule_hits(*r, items) for r in RULES}
    allacc = {k: float(np.mean([x for v in h.values() for x in v])) for k, h in allh.items()}
    fixed = max(allacc, key=allacc.get)
    print(f"  globally best criterion-free rule (FIXED mode): `{fixed}` {allacc[fixed]:.4f}")

    # ------------------------------------------------------------------------------- controls
    ok = True
    print()
    for n in sorted(strata):
        sub = strata[n]
        convs = sorted({k[0] for k, _, _, _ in sub})
        g2 = gen_hits(sub)
        b4 = rule_hits(*[r for r in RULES if r[0] == fixed][0], sub)
        orc = {c: [1.0] * len(v) for c, v in g2.items()}
        o2 = paired(orc, g2, convs); o4 = paired(orc, b4, convs)
        good = o2 and o4 and o2[0] > o2[3] and o4[0] > o4[3]
        ok &= bool(good)
        print(f"  POSITIVE  n={n}: an oracle beats BAR2 by {o2[0]:+.4f} (MDE {o2[3]:.4f}) and BAR4 "
              f"by {o4[0]:+.4f} (MDE {o4[3]:.4f})   {'PASS' if good else '⛔ FAIL'}")
        pl = paired(g2, g2, convs)
        ok &= (pl is not None and pl[0] == 0.0)
        print(f"  g=0       n={n}: `generic` against itself -> {pl[0]:.1e}, must be 0   "
              f"{'PASS' if pl and pl[0] == 0.0 else '⛔ FAIL'}")
    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r438_within_release_flip.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ---------------------------------------------------------------------------- the sweep
    print(f"\n  {'stratum':<10}{'n_int':>7}{'chance':>8}{'BAR2':>8}{'BAR4':>8}{'GAP':>9}"
          f"{'MDE':>8}{'mode':>10}")
    cells = []
    for mode in ("FIXED", "RESELECTED"):
        for n in sorted(strata):
            sub = strata[n]
            convs = sorted({k[0] for k, _, _, _ in sub})
            g2 = gen_hits(sub)
            if mode == "FIXED":
                rule = [r for r in RULES if r[0] == fixed][0]
            else:
                accs = {}
                for r in RULES:
                    h = rule_hits(*r, sub)
                    accs[r[0]] = float(np.mean([x for v in h.values() for x in v]))
                rule = [r for r in RULES if r[0] == max(accs, key=accs.get)][0]
            b4 = rule_hits(*rule, sub)
            g = paired(b4, g2, convs)
            bar2 = float(np.mean([x for v in g2.values() for x in v]))
            bar4 = float(np.mean([x for v in b4.values() for x in v]))
            cells.append({"mode": mode, "n": n, "n_int": len(sub), "n_conv": len(convs),
                          "chance": 1.0 / n, "bar2": bar2, "bar4": bar4, "rule": rule[0],
                          "gap": g[0], "lo": g[1], "hi": g[2], "mde": g[3], "p": g[4],
                          "resolved": bool(abs(g[0]) > g[3])})
            c = cells[-1]
            print(f"  n={n:<8}{len(sub):>7}{1.0/n:>8.4f}{bar2:>8.4f}{bar4:>8.4f}{g[0]:>+9.4f}"
                  f"{g[3]:>8.4f}{mode:>10}  `{rule[0]}`"
                  f"{'  RESOLVED' if abs(g[0]) > g[3] else ''}")

    C = len(cells)
    ordr = sorted(range(C), key=lambda i: cells[i]["p"])
    surv = set()
    for r_, i in enumerate(ordr, start=1):
        if cells[i]["p"] <= 0.10 * r_ / C:
            surv = set(ordr[:r_])
    for i, c in enumerate(cells):
        c["bh"] = i in surv
    print(f"\n  cells tested {C} · surviving BH(q=0.10) {sum(c['bh'] for c in cells)}")

    infl = [c for c in cells if c["mode"] == "RESELECTED"]
    fixc = {c["n"]: c for c in cells if c["mode"] == "FIXED"}
    print(f"  SELECTION inflation (RESELECTED − FIXED on BAR4): " + " · ".join(
        f"n={c['n']} {c['bar4'] - fixc[c['n']]['bar4']:+.4f}" for c in infl))
    print(f"    measured, not argued — this is what re-choosing the max inside a smaller sample buys.")

    fixed_cells = [c for c in cells if c["mode"] == "FIXED"]
    res = [c for c in fixed_cells if c["resolved"]]
    signs = {int(np.sign(c["gap"])) for c in res}
    world = ("W-UNRESOLVED" if len(res) < 2 else
             "W-FLIPS-INSIDE" if len(signs) > 1 else "W-STABLE-SIGN")
    print(f"\n  FIXED-rule strata that resolve: {len(res)} of {len(fixed_cells)} · signs {sorted(signs)}")
    print(f"\n  WORLD: {world}")
    if world == "W-STABLE-SIGN":
        print(f"    the GAP has the SAME sign in every stratum that resolves, so the number of")
        print(f"    responses does not reorder the two bars. R437's release-level framing survives")
        print(f"    this attack — and survives it on the axis that was most likely to break it,")
        print(f"    since chance itself moves from {1/max(strata):.4f} to {1/min(strata):.4f} across")
        print(f"    these strata and both bars had every opportunity to cross.")
    elif world == "W-FLIPS-INSIDE":
        print(f"    ⛔ the GAP resolves with OPPOSITE SIGNS inside one release. 'The bars invert")
        print(f"    between releases' is the WRONG OBJECT — the real variable is the number of")
        print(f"    responses, and R437's framing is retracted in favour of it.")
    else:
        print(f"    fewer than two strata resolve, so the split has no power here. That is a fact")
        print(f"    about THIS design and NOT an acquittal of R437: the attack failed to be an")
        print(f"    attack, which is different from the claim surviving one.")

    (RES / "r438_within_release_flip.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "fixed_rule": fixed, "cells": cells, "n_items": len(items),
         "dropped_missing_text": dropped,
         "strata_sizes": {str(k): len(v) for k, v in strata.items()}}, indent=1))
    print(f"\n  artifact -> {(RES / 'r438_within_release_flip.json').relative_to(ROOT)}")
    return 0 if world == "W-STABLE-SIGN" else (1 if world == "W-FLIPS-INSIDE" else 2)


if __name__ == "__main__":
    sys.exit(main())
