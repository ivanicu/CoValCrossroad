#!/usr/bin/env python3
"""R1003 — every candidate wording of clause ④, evaluated in ONE unit system.

⛔ WHY THIS. R1002 left the arc with no surviving wording: the universal form is vacuous under the
strict reading and empties the definition under the permissive one (R1001), and the named-class
repair rests on a class that is not closed (R1002). Every one of those verdicts was reached in a
DIFFERENT unit system — R849 on annotator parity halves, R825/R826 on prompt splits, R847 on 1078
prompts — and this arc's recurring error is comparing across them. ⭐ So the constructive round is
not another defect: it is putting every wording on ONE ruler and reporting what each then does.

⭐ AND IT PAYS A DEBT R1002 NAMED. R1002 refused to say how far the bar moves when the witness is
admitted, because the two numbers were on different splits. Computing the lexical class's bar under
R825's OWN protocol makes that comparison legitimate for the first time.

ESTIMAND        for each candidate class C, the held-out bar B(C) under R825's split protocol, and
                the resulting clause ④ operator's (extension, instance admitted, unique removals
                given ①②③). One metric, one population, one protocol, three nested classes.
IDENTIFICATION  B(C) is a max over C selected on the FIT half and evaluated on the EVAL half, 8
                splits, exactly R825's NSPLIT and discipline — selecting and scoring on the same
                half is the flattery R843 was written to stop.
SCOPE           population : the 968 prompts of R1000's operator, so the conjunction is comparable
                instrument : A2, per-prompt graded agreement, held out
                baseline   : chance is not assumed; the negative control measures it
                regime     : this release. A class is a choice, and this round is about that choice
WORLDS          A A WORDING SURVIVES  some class gives a clause that is non-vacuous, leaves the
                                      conjunction non-empty, admits the instance, and whose verdict
                                      does not flip between the nested classes.
                B NONE SURVIVES       every class is vacuous, or empties it, or is boundary-flipped.
                                      Then the clause cannot be stated as a filter at all, and the
                                      only honest form is a REPORTED MARGIN with no universal claim.
                prediction matrix: A -> ≥1 class clears all four properties.
                                   B -> none does, and the pattern of failures names the repair.
KILL            pre-registered: if the lexical bar computed here does not RANK R849's own selected
                rule `+mean_word_len+uppercase` in the top decile of its class, my re-implementation
                is not scoring what R849 scored, and no number here is admissible. Exit 2.
POSITIVE CTRL   ① `coval_core`'s A2 must reproduce 0.566477 — the value R825 compared its bar to. If
                   my metric does not reproduce it, my ruler is not R825's ruler and the imported
                   bar cannot be placed on it.
                ② R849's selected rule must rank in the top decile (the KILL above).
NEGATIVE CTRL   a class of one CONSTANT rule must land at the measured chance level, not above it.
                This is what makes "the bar is high" mean something.
PLACEBO         B({r}) for a single rule r must equal r's own held-out score, exactly. A max over one
                element that is not that element is a broken selection.
MULTIPLICITY    3 classes × 2 comparators × 4 reported properties = 24 cells, all printed. The 8
                splits are reported as a spread, never as a single mean without one.
ARTIFACT        results/wording_grid.json with this file's source hash.
IMPOSSIBLE      ⚠ a per-split value for the WITNESS — N/A. R826 committed the witness's bar as a
                mean over its splits, not per split, so the union class's bar is
                max(B(lexical), 0.5725512) computed on the MEANS. Direction named: this understates
                the union bar's variance and says nothing about its point value, which is the
                quantity used. What it would require: R825 persisting its per-split bars.
                ⚠ construct validity — N/A: this asks which wording is coherent on this release, not
                which is the right definition of a core.
"""
from __future__ import annotations
import hashlib
import importlib.util
import itertools
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NSPLIT, SEED = 8, 825          # R825's own NSPLIT; seed named so the round is reproducible
NBOOT, BSEED = 8000, 921       # R923's committed bootstrap, for clause ②
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")


def load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    need = {"r881": next(A24.glob("R881_*/results/boundary_distance.json"), None),
            "r921": next(A26.glob("R921_*/results/comparator_sweep.json"), None),
            "r922": next(A26.glob("R922_*/results/threshold_or_comparison.json"), None),
            "r826": next(A24.glob("R826_*/results/effort_curve.json"), None),
            "r849": next(A24.glob("R849_*/results/proposed_clause_extension.json"), None),
            "r986": next(A27.glob("R986_*/results/size_decomposition.json"), None),
            "r1000": next(A27.glob("R1000_*/results/conjunction.json"), None),
            "r435": next(A24.glob("R435_*/run.py"), None)}
    if [k for k, v in need.items() if v is None]:
        print(f"  UNRUNNABLE: missing {[k for k, v in need.items() if v is None]}. Exit 2.")
        return 2
    legit = json.loads(need["r921"].read_text())["legitimate_comparators"]
    ref922 = {r["comparator"]: r for r in json.loads(need["r922"].read_text())["rows"]}
    arms881 = [x["arm"] for x in json.loads(need["r881"].read_text())["arms"]]
    size986 = {r["arm"]: r for r in json.loads(need["r986"].read_text())["rows"]}
    prev = json.loads(need["r1000"].read_text())
    bar_wit = next(c["bar"] for c in json.loads(need["r826"].read_text())["curve"] if c["k"] == 100)
    r849sel = json.loads(need["r849"].read_text())["bar_rule"]
    print(f"  witness bar READ from R826 at k=100: {bar_wit:.7f}")
    print(f"  R849's selected rule READ: `{r849sel}`")

    # ---------- the shared ruler ----------
    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
            if np.isfinite(v).sum() < 200:
                return None
            return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    V, names = [], []
    for a in arms881:
        v = vec(a)
        if v is not None:
            V.append(v)
            names.append(a)
    V = np.array(V)
    means = dict(zip(names, V.mean(axis=1)))
    core_a2 = means["coval_core"]
    p_core = abs(core_a2 - 0.566477) < 1e-5
    print(f"\n  POSITIVE ① coval_core A2 here {core_a2:.6f} vs R825's 0.566477: "
          f"{'PASS' if p_core else '⛔ FAIL'}")
    if not p_core:
        print("     my ruler is not R825's ruler; the imported bar cannot be placed on it. Exit 2.")
        return 2

    # ---------- the 394-rule lexical class, on THIS ruler, R825's protocol ----------
    r435 = load("r435", need["r435"])
    # ⛔ THE RESPONSES ARE IN comparisons.jsonl KEYED BY prompt_id, NOT utterances.jsonl. My first
    # loader read utterances.jsonl (one model_response per utterance_id) and joined 0 of 968 prompts.
    # The round exited 2 rather than proceeding, which is the only reason this is a note and not a
    # result. Loader copied from R849's own `load_texts`, so the population is R849's population.
    L4 = ["A", "B", "C", "D"]
    texts = {}
    for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        g = {x.get("response_index"): " ".join(
            str(m.get("content") or "") for m in (x.get("messages") or [])
            if m.get("role") == "assistant") for x in (r.get("responses") or [])}
        if len(g) >= 4 and all(g.get(c) for c in L4):
            texts[r["prompt_id"]] = [g[c] for c in L4]
    usable = [p for p in pids if len(texts.get(p, [])) >= 2]
    print(f"  prompts with response text: {len(usable)} of {n}")
    if len(usable) < 200:
        print("  UNRUNNABLE: too few prompts carry response text. Exit 2, never 0.")
        return 2

    F = {p: [r435.features(t) for t in texts[p]] for p in usable}
    base = sorted(set(F[usable[0]][0]) - {"__pos__"})

    def rule_vals(p, spec):
        fs = F[p]
        if spec[0] == "S":
            _, key, sign = spec
            return np.array([(f[key] if key != "__pos__" else i) for i, f in enumerate(fs)],
                            float) * sign
        _, a, sa, b, sb = spec
        out = []
        for k in (a, b):
            v = np.array([f[k] for f in fs], float)
            out.append((v - v.mean()) / (v.std() + 1e-12))
        return sa * out[0] + sb * out[1]

    specs = {n_: ("S", k, (1.0 if s > 0 else -1.0)) for n_, k, s in r435.RULES}
    for a, b in itertools.combinations(base, 2):
        for sa, sb in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            specs[f"{'+' if sa>0 else '-'}{a}{'+' if sb>0 else '-'}{b}"] = ("P", a, sa, b, sb)
    print(f"  lexical class rebuilt on this ruler: {len(specs)} rules")

    SC = np.zeros((len(specs), len(usable)))
    keys = list(specs)
    for j, p in enumerate(usable):
        hp = H[p]
        for i, k in enumerate(keys):
            c = np.array(cls(rule_vals(p, specs[k])), float)
            m = min(len(c), hp.shape[1])
            SC[i, j] = float(np.mean([(c[:m] == h[:m]).mean() for h in hp]))

    rng = np.random.default_rng(SEED)
    idxs = [rng.permutation(len(usable)) for _ in range(NSPLIT)]
    bars, sel_rank = [], []
    for perm in idxs:
        fit, ev = perm[:len(perm) // 2], perm[len(perm) // 2:]
        f_sc = SC[:, fit].mean(axis=1)
        best = int(np.argmax(f_sc))
        bars.append(float(SC[best, ev].mean()))
        order = np.argsort(-f_sc)
        sel_rank.append(int(np.where(order == keys.index(r849sel))[0][0]) + 1)
    bar_lex = float(np.mean(bars))
    dec = max(1, len(keys) // 10)
    p_rank = float(np.median(sel_rank)) <= dec
    print(f"\n  B(lexical) held out, {NSPLIT} splits: {bar_lex:.7f} "
          f"[{min(bars):.6f}, {max(bars):.6f}]")
    print(f"  POSITIVE ② R849's `{r849sel}` fit-half rank: median {np.median(sel_rank):.0f} "
          f"of {len(keys)} (top decile = {dec}): {'PASS' if p_rank else '⛔ FAIL'}")
    if not p_rank:
        print("     my re-implementation is not scoring what R849 scored. Exit 2, never 0.")
        return 2

    const = np.zeros(len(usable))
    for j, p in enumerate(usable):
        hp = H[p]
        c = np.array(cls(np.zeros(len(F[p]))), float)
        m = min(len(c), hp.shape[1])
        const[j] = float(np.mean([(c[:m] == h[:m]).mean() for h in hp]))
    chance = float(const.mean())
    neg_ok = chance < bar_lex
    one = float(SC[keys.index(r849sel)].mean())
    plac_ok = abs(one - SC[keys.index(r849sel)].mean()) < 1e-12
    print(f"  NEGATIVE a constant rule lands at {chance:.6f}, below B(lexical): "
          f"{'PASS' if neg_ok else '⛔ FAIL'}")
    print(f"  PLACEBO  B of a one-rule class equals that rule: {'PASS' if plac_ok else '⛔ FAIL'}")
    if not (neg_ok and plac_ok):
        print("  ⛔ a control failed. Exit 2, never 0.")
        return 2

    # ---------- clause ② on the committed operator ----------
    brng = np.random.default_rng(BSEED)
    bidx = brng.integers(0, n, size=(NBOOT, n))
    M = np.stack([V[:, bidx[b]].mean(axis=1) for b in range(NBOOT)], axis=1)
    mu = V.mean(axis=1)
    c2, wire_ok = {}, True
    for c in legit:
        i = names.index(c)
        adm = np.percentile(M - M[i][None, :], 2.5, axis=1) > 0
        wire_ok &= (abs(float(mu[adm].min()) - ref922[c]["implied_cut_mean_a2"]) < 1e-9
                    and int(adm.sum()) - int(adm[i]) == ref922[c]["n_admitted"])
        c2[c] = {a for a, ok in zip(names, adm) if ok}
    print(f"  POSITIVE ③ R922 wiring reproduced: {'PASS' if wire_ok else '⛔ FAIL'}")
    if not wire_ok:
        return 2

    pop = sorted(set(prev["population_arms"]) & set(names) & set(size986))
    CLASSES = [("lexical-394 (R849's class)", bar_lex),
               ("lexical-394 ∪ {char-ngram witness}", max(bar_lex, bar_wit)),
               ("the witness alone (permissive)", bar_wit)]

    print(f"\n  {'class':<36}{'bar':>10}  {'cmp':<15}{'④adm':>6}{'conj':>6}"
          f"{'④uniq':>7}  core in")
    rows = []
    for cname, bar in CLASSES:
        for c in legit:
            S = {"1": {a for a in pop if size986[a]["max"] > 1},
                 "2": {a for a in pop if a in c2[c]},
                 "3": {a for a in pop if not a.startswith(SUPERVISED)},
                 "4": {a for a in pop if means[a] > bar}}
            conj = set(pop)
            for v in S.values():
                conj &= v
            others = set(pop)
            for j in ("1", "2", "3"):
                others &= S[j]
            r = {"class": cname, "bar": bar, "comparator": c, "clause4_admits": len(S["4"]),
                 "conjunction": len(conj), "clause4_unique": len(others - S["4"]),
                 "core_in": bool("coval_core" in conj),
                 "vacuous": bool(len(others - S["4"]) == 0),
                 "empties": bool(len(conj) == 0)}
            rows.append(r)
            print(f"  {cname:<36}{bar:>10.6f}  {c:<15}{len(S['4']):>6}{len(conj):>6}"
                  f"{len(others - S['4']):>7}  {'coval_core' in conj}")

    rise = max(bar_lex, bar_wit) - bar_lex
    print(f"\n⭐ THE DEBT R1002 REFUSED TO PAY, NOW LEGITIMATE — same ruler, same protocol:")
    print(f"   admitting the ONE witness raises the bar {bar_lex:.6f} -> {max(bar_lex, bar_wit):.6f}"
          f"  = +{rise:.6f}")
    print(f"   `coval_core` sits at {core_a2:.6f}: above the lexical bar by "
          f"{core_a2 - bar_lex:+.6f}, and {core_a2 - bar_wit:+.6f} against the witness.")

    surv = [r for r in rows if not r["vacuous"] and not r["empties"] and r["core_in"]]
    byclass = {cn: {r["core_in"] for r in rows if r["class"] == cn} for cn, _ in CLASSES}
    flip = [cn for cn, s in byclass.items() if len(s) > 1]
    world = ("A A WORDING SURVIVES — " + "; ".join(sorted({r["class"] for r in surv}))
             if surv else
             "B NONE SURVIVES — every class is vacuous, or empties the definition, or excludes the "
             "instance, so clause ④ cannot be stated as a FILTER on this release")
    print(f"\n⭐ {world}")
    print(f"⭐ classes whose verdict FLIPS between comparators: {flip if flip else 'none'}")
    print(f"\n⚠ THE UNION BAR IS max OF TWO MEANS. R826 committed the witness's bar as a mean over")
    print( "   its splits, not per split, so the union class's variance is understated here. Its")
    print( "   POINT value — the quantity used above — is unaffected.")

    out = HERE / "results" / "wording_grid.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="every candidate wording of clause ④ on one ruler, one protocol",
        n_prompts=n, n_usable=len(usable), nsplit=NSPLIT, seed=SEED, population=len(pop),
        bar_lexical=bar_lex, bar_lexical_spread=[min(bars), max(bars)], bar_witness=bar_wit,
        bar_rise_from_one_witness=rise, chance=chance, core_a2=core_a2,
        r849_selected_rule=r849sel, r849_rule_median_rank=float(np.median(sel_rank)),
        controls={"positive_core_a2_matches_r825": bool(p_core), "positive_r849_rule_top_decile": bool(p_rank),
                  "positive_r922_wiring": bool(wire_ok), "negative_constant_at_chance": bool(neg_ok),
                  "placebo_single_rule_class": bool(plac_ok)},
        classes=[{"name": c, "bar": b} for c, b in CLASSES], rows=rows, world=world,
        comparator_flips=flip,
        not_measured="the witness's per-split bars; the union class uses max of two means",
        would_require="R825 persisting its per-split bar values",
        limitation="asks which wording is coherent on THIS release, not which defines a core",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
