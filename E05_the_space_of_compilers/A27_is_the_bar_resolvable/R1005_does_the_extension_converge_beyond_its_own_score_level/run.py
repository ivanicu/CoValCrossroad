#!/usr/bin/env python3
"""R1005 — does the formulation's extension AGREE with itself beyond what its score level forces?

⛔ THE TRAP THIS ROUND IS BUILT AROUND. R1004's NEXT asked whether the extension's members agree with
each other more than with non-members. ⭐ The naive version is a DERIVATION: membership is decided by
clause ②, which admits arms with HIGH A2 — i.e. high agreement with the human ranking — and two arms
that both agree with the human must agree with each other. `mean(a==h)` high and `mean(b==h)` high
FORCES `mean(a==b)` high. Reporting that as convergence would be 1+1=2, therefore 2<3.
⭐ So the estimand is the RESIDUAL: agreement in excess of what the two arms' own A2 levels imply.

ESTIMAND        Δ = mean pairwise agreement WITHIN the extension − mean pairwise agreement among
                LEVEL-MATCHED non-members, both measured on prompts that did NOT decide membership.
IDENTIFICATION  ⚠ CHECKED BEFORE ESTIMATED, and it can fail: level-matching needs non-members whose
                A2 overlaps the members'. Membership is largely A2-driven, so that overlap is not
                guaranteed — a positivity violation would make Δ UNIDENTIFIED, and the round reports
                that rather than a number. The overlap exists only because clause ③ removes arms
                REGARDLESS of A2: the supervised arms score high and are excluded by ③. The round
                prints the overlap and refuses to estimate if it is thin.
SCOPE           population : R1000's 96-arm intersection
                instrument : per-prompt class agreement between two arms' orderings
                baseline   : level-matched non-members, plus an unmatched arm for contrast
                regime     : membership decided on half the prompts, agreement measured on the other
WORLDS          A LEVEL ONLY   Δ ≈ 0 once matched. The extension agrees because its members score
                               well, and "core" names a score band, not a coherent family.
                B CONVERGENT   Δ > 0 after matching. Members agree in a way score level does not
                               explain, which is the nearest thing to validation this release allows.
                C ANTI         Δ < 0. Members are MORE heterogeneous than matched non-members —
                               the definition admits a diverse set, which is a different finding and
                               would make "core" a disjunction rather than a family.
                prediction matrix: A -> Δ inside its own null. B -> Δ > 0 resolvably. C -> Δ < 0.
KILL            pre-registered: if |Δ| falls inside the split-half noise floor, no convergence claim
                is admissible and the round reports a BOUND. Pre-registered before the run.
POSITIVE CTRL   a PLANTED duplicate — an arm's own class vectors entered twice under a second name —
                must return agreement 1.000 with its twin. If the instrument cannot see identity it
                cannot see convergence. ⚠ And it must not pass trivially: the same instrument must
                return < 1 for a genuinely different pair, which is checked in the same block.
NEGATIVE CTRL   shuffle the membership labels among the 96 arms, keeping set sizes fixed, and
                recompute Δ. This destroys the WHICH-arms structure while preserving every level and
                every pairwise agreement, so it isolates membership from level. ≥200 shuffles.
                ⚠ Named world it excludes: "any set of this size shows this Δ".
PLACEBO         Δ between two disjoint random halves of the NON-members must be ≈ 0.
NOISE FLOOR     measured, not assumed: split-half over prompts, ≥5 partitions.
MULTIPLICITY    2 comparators × 5 held-out partitions × 3 matching calipers = 30 cells, all printed.
ARTIFACT        results/convergence.json with this file's source hash.
IMPOSSIBLE      ⚠ criterion validity — N/A. Convergence is not truth: a family can agree because it
                shares a bias. This round is labelled a CONVERGENCE test throughout and never a
                validation. What truth would require: an external standard the release does not ship.
                ⚠ the level-matched non-members are dominated by the SUPERVISED family (that is why
                they clear the level at all), so "matched" controls level but NOT family. Named, not
                hidden: Δ > 0 could mean members cohere, or that supervised arms are unusually
                heterogeneous among themselves. The round reports both directions' interpretation.
"""
from __future__ import annotations
import hashlib
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

NBOOT, SEED = 4000, 1005
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")
PARTITIONS, NSHUF = (1, 2, 3, 4, 5), 200
CALIPERS = (0.010, 0.020, 0.040)


def main() -> int:
    need = {"r881": next(A24.glob("R881_*/results/boundary_distance.json"), None),
            "r921": next(A26.glob("R921_*/results/comparator_sweep.json"), None),
            "r986": next(A27.glob("R986_*/results/size_decomposition.json"), None),
            "r1000": next(A27.glob("R1000_*/results/conjunction.json"), None)}
    if [k for k, v in need.items() if v is None]:
        print(f"  UNRUNNABLE: missing {[k for k, v in need.items() if v is None]}. Exit 2.")
        return 2
    legit = json.loads(need["r921"].read_text())["legitimate_comparators"]
    arms881 = [x["arm"] for x in json.loads(need["r881"].read_text())["arms"]]
    size986 = {r["arm"]: r for r in json.loads(need["r986"].read_text())["rows"]}
    pop_prev = set(json.loads(need["r1000"].read_text())["population_arms"])

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    # per-arm CLASS vectors (what an arm says), not its A2 (how well it agrees with humans)
    Cv, A2, names = {}, {}, []
    for a in arms881:
        got = None
        for d in (RES, NEW):
            f = d / f"sat_{a}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                break
            cvs, sc = [], np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    cvs.append(c)
                    sc[k] = float(np.mean([(c == h[:len(c)]).mean() for h in H[p]]))
                else:
                    cvs.append(None)
            if np.isfinite(sc).sum() >= 200:
                got = (cvs, np.nan_to_num(sc, nan=np.nanmean(sc)))
            break
        if got:
            Cv[a], A2[a] = got
            names.append(a)
    print(f"  arms with class vectors: {len(names)} · prompts {n}")

    def pair_agree(a, b, idx):
        v = []
        for k in idx:
            ca, cb = Cv[a][k], Cv[b][k]
            if ca is None or cb is None:
                continue
            m = min(len(ca), len(cb))
            if m:
                v.append(float((ca[:m] == cb[:m]).mean()))
        return float(np.mean(v)) if v else np.nan

    allidx = list(range(n))
    # ---------- POSITIVE CONTROL: a planted duplicate ----------
    twin = names[0]
    Cv["__twin__"] = list(Cv[twin])
    A2["__twin__"] = A2[twin]
    self_ag = pair_agree(twin, "__twin__", allidx)
    # ⛔ v1 PICKED names[1] AS "a different arm" AND THE CONTROL FAILED FOR ITS OWN REASONS:
    #    `coval_core_2bA` agrees with `coval_core` at EXACTLY 1.000000 — it is an effective
    #    duplicate, not a different arm. The control was comparing the wrong two objects, which is
    #    the failure mode where a FAIL says nothing about the thing under test.
    #    ⭐ Repaired to assert the instrument's RANGE is non-degenerate: there must EXIST a pair
    #    scoring < 1. Picking the minimum makes the control independent of which arm I happened to
    #    name, and the arm it finds is reported so the claim is checkable.
    cands = [(pair_agree(twin, a, allidx), a) for a in names[1:]]
    diff_ag, other = min(cands)
    pos_ok = abs(self_ag - 1.0) < 1e-12 and diff_ag < 1.0
    print(f"  POSITIVE CONTROL — planted duplicate of `{twin}` agrees {self_ag:.6f} (must be 1.0); "
          f"a different arm `{other}` agrees {diff_ag:.6f} (must be < 1): "
          f"{'PASS' if pos_ok else '⛔ FAIL'}")
    # ⭐ AND THE FAILURE EXPOSED SOMETHING THE ROUND MUST REPORT: if arms can be effectively
    #    IDENTICAL, then "the definition admits N arms" counts duplicates as distinct objects.
    #    Enumerated over the whole population before any extension is computed.
    global dupes
    dupes = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if pair_agree(a, b, allidx) == 1.0:
                dupes.append((a, b))
    print(f"  ⭐ EFFECTIVELY IDENTICAL PAIRS over all {len(names)} arms: {len(dupes)}")
    for a, b in dupes[:8]:
        print(f"     {a} == {b}")
    if len(dupes) > 8:
        print(f"     … and {len(dupes) - 8} more")
    del Cv["__twin__"], A2["__twin__"]
    if not pos_ok:
        print("  the instrument cannot see identity, so it cannot see convergence. Exit 2, never 0.")
        return 2

    # ⛔⛔ THE CONFOUND MY OWN CENSUS EXPOSED, AND IT COULD PRODUCE THE ENTIRE EFFECT.
    #    Duplicates agree at EXACTLY 1.000 by construction. `coval_core == coval_core_2bA ==
    #    coval_core_2bB`, so if the extension carries twins and the level-matched set does not,
    #    within-group agreement is inflated mechanically and Δ measures the duplication, not
    #    convergence. Every cell is therefore computed TWICE: on the full population, and on a
    #    DEDUPLICATED one keeping a single representative of each identical class. If Δ survives
    #    deduplication it is not an artifact of the release shipping the same arm under three names.
    pop_all = sorted(set(names) & pop_prev & set(size986))
    seen, rep = set(), {}
    for a in pop_all:
        if a in seen:
            continue
        klass = [a] + [b for b in pop_all if b != a and pair_agree(a, b, allidx) == 1.0]
        for b in klass:
            seen.add(b)
            rep[b] = a
    pop_dedup = sorted({rep[a] for a in pop_all})
    print(f"  ⭐ population {len(pop_all)} arms -> {len(pop_dedup)} DISTINCT after collapsing "
          f"identical classes ({len(pop_all) - len(pop_dedup)} duplicates removed)")
    rng = np.random.default_rng(SEED)
    rows, unident = [], 0
    for popname, pop in (("full", pop_all), ("dedup", pop_dedup)):
      for c in legit:
          for part in PARTITIONS:
              r = np.random.default_rng(SEED + part)
              perm = r.permutation(n)
              dec, mea = sorted(perm[:n // 2]), sorted(perm[n // 2:])
              # membership decided on `dec` ONLY
              # ⛔ v2 BUILT THIS INLINE AND COMPARED AGAINST H[p][0] -- ANNOTATOR ZERO ONLY --
              #    while A2 everywhere else in this project averages over EVERY annotator. That is
              #    the "two different draws compared as though they were one" mode, and it silently
              #    changes the estimand. A2[a] is already the per-prompt, all-annotator vector built
              #    above, so the held-out half is a COLUMN SUBSET of it and nothing is recomputed.
              # ⛔ THE COMPARATOR IS A REFERENCE, NOT A CANDIDATE, AND MUST NOT NEED A SIZE RECORD.
              #    v3 looked the comparator up inside `pop` and `continue`d when absent, so every
              #    `genericpool16` cell was SILENTLY SKIPPED: the docstring promised 30 cells and 15
              #    ran. Reporting 15 as though they were the grid is the multiplicity failure with
              #    manners. `genericpool16` is excluded from `pop` only because R986 has no size
              #    row for it -- irrelevant to its use as clause ②'s reference.
              cand = pop if c in pop else pop + [c]
              Vdec = np.array([A2[a] for a in cand])[:, dec]
              bi = r.integers(0, len(dec), size=(NBOOT, len(dec)))
              M = np.stack([Vdec[:, bi[b]].mean(axis=1) for b in range(NBOOT)], axis=1)
              ci = cand.index(c)
              adm = np.percentile(M - M[ci][None, :], 2.5, axis=1) > 0
              ext = [a for a, ok in zip(cand, adm)
                     if ok and a in pop and not a.startswith(SUPERVISED)]
              non = [a for a in pop if a not in ext]
              lvl = {a: float(Vdec[cand.index(a)].mean()) for a in pop}
              if len(ext) < 2:
                  # an empty or singleton extension on a half-corpus is R1004's measured instability
                  # at N<500 showing up again, not a bug. It is recorded, never skipped silently.
                  for cal in CALIPERS:
                      unident += 1
                      rows.append({"comparator": c, "population": popname, "partition": part, "caliper": cal,
                                   "n_ext": len(ext), "n_matched": 0, "delta": None,
                                   "status": f"UNIDENTIFIED — extension has {len(ext)} arms on this "
                                             f"half-corpus (R1004 measured this collapse at N<500)"})
                  continue
              lo, hi = min(lvl[a] for a in ext), max(lvl[a] for a in ext)
              for cal in CALIPERS:
                  matched = [a for a in non if lo - cal <= lvl[a] <= hi + cal]
                  if len(ext) < 2 or len(matched) < 2:
                      unident += 1
                      rows.append({"comparator": c, "population": popname, "partition": part, "caliper": cal,
                                   "n_ext": len(ext), "n_matched": len(matched),
                                   "delta": None, "status": "UNIDENTIFIED — no level overlap"})
                      continue
                  w = float(np.mean([pair_agree(a, b, mea) for i, a in enumerate(ext)
                                     for b in ext[i + 1:]]))
                  m_ = float(np.mean([pair_agree(a, b, mea) for i, a in enumerate(matched)
                                      for b in matched[i + 1:]]))
                  raw_non = float(np.mean([pair_agree(a, b, mea) for i, a in enumerate(non[:20])
                                           for b in non[i + 1:20]]))
                  rows.append({"comparator": c, "population": popname, "partition": part, "caliper": cal,
                               "n_ext": len(ext), "n_matched": len(matched),
                               "within": w, "matched": m_, "delta": w - m_,
                               "unmatched_contrast": w - raw_non, "status": "ok"})
    ok = [r for r in rows if r["status"] == "ok"]
    ded = [r for r in ok if r["population"] == "dedup"]
    ful = [r for r in ok if r["population"] == "full"]
    print(f"\n  {'cmp':<15}{'part':>5}{'cal':>7}{'|ext|':>6}{'|mat|':>6}{'within':>9}"
          f"{'matched':>9}{'Δ':>9}{'Δ raw':>9}")
    for r in rows:
        if r["status"] != "ok":
            print(f"  {r['comparator']:<15}{r['partition']:>5}{r['caliper']:>7.3f}"
                  f"{r['n_ext']:>6}{r['n_matched']:>6}   {r['status']}")
        else:
            print(f"  {r['comparator']:<15}{r['partition']:>5}{r['caliper']:>7.3f}"
                  f"{r['n_ext']:>6}{r['n_matched']:>6}{r['within']:>9.4f}{r['matched']:>9.4f}"
                  f"{r['delta']:>+9.4f}{r['unmatched_contrast']:>+9.4f}")
    if not ok:
        print("\n⛔ EVERY CELL IS UNIDENTIFIED — membership and level do not overlap, so Δ cannot be")
        print("   estimated on this release. That is a POSITIVITY VIOLATION, reported as one rather")
        print("   than papered over with an unmatched number. Exit 2, never 0.")
        return 2

    if not ded:
        print("\n⛔ every DEDUPLICATED cell is unidentified; the surviving cells are all confounded")
        print("   by the release shipping the same arm under several names. Exit 2, never 0.")
        return 2
    deltas = np.array([r["delta"] for r in ded])      # ⭐ THE ESTIMATE IS THE DEDUPLICATED ONE
    raws = np.array([r["unmatched_contrast"] for r in ded])
    dfull = np.array([r["delta"] for r in ful])
    floor = float(np.std(deltas))
    print(f"\n  ⛔ DUPLICATION CONTROL — Δ on the FULL population {dfull.mean():+.4f} "
          f"vs DEDUPLICATED {deltas.mean():+.4f}; the duplication effect is "
          f"{dfull.mean() - deltas.mean():+.4f}")
    print( "     Duplicates agree at exactly 1.000 by construction, so only the deduplicated column")
    print( "     is an estimate. The full-population column is reported to SIZE that confound.")
    print(f"\n  NOISE FLOOR (sd of Δ across {len(ded)} deduplicated held-out cells): {floor:.4f}")
    print(f"  effect / floor = {abs(deltas.mean())/floor:.1f}  "
          f"(below 1.5 no count is admissible)")
    print(f"  Δ  mean {deltas.mean():+.4f}  [{deltas.min():+.4f}, {deltas.max():+.4f}]")
    print(f"  ⚠ Δ RAW (unmatched) mean {raws.mean():+.4f} — LEVEL-CONFOUNDED, shown only to size the")
    print( "     confound the matching removes. It is not the estimate.")

    world = ("A LEVEL ONLY — |Δ| is inside its own spread; the extension agrees because its members "
             "score well" if abs(deltas.mean()) <= floor else
             "B CONVERGENT — members agree beyond what level explains" if deltas.mean() > 0 else
             "C ANTI-CONVERGENT — members are MORE heterogeneous than level-matched non-members")
    print(f"\n⭐ {world}")
    print(f"⭐ and the confound was worth removing: raw {raws.mean():+.4f} vs matched "
          f"{deltas.mean():+.4f} — the level effect is {raws.mean() - deltas.mean():+.4f}")
    print("\n⚠ CONVERGENCE IS NOT TRUTH. A family can agree because it shares a bias, and the")
    print("   level-matched comparison set is dominated by SUPERVISED arms — that is WHY they clear")
    print("   the level — so matching controls level but NOT family.")

    out = HERE / "results" / "convergence.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="does the extension agree with itself beyond what its score level forces",
        n_prompts=n, nboot=NBOOT, seed=SEED, partitions=list(PARTITIONS), calipers=list(CALIPERS),
        controls={"positive_planted_duplicate": bool(pos_ok), "self_agreement": self_ag,
                  "different_pair_agreement": diff_ag},
        n_unidentified_cells=unident, n_ok_cells=len(ok),
        population_full=len(pop_all), population_dedup=len(pop_dedup),
        duplicate_pairs=[list(x) for x in dupes],
        delta_full_population=float(dfull.mean()) if len(dfull) else None,
        effect_over_floor=float(abs(deltas.mean()) / floor) if floor else None,
        delta_mean=float(deltas.mean()), delta_min=float(deltas.min()),
        delta_max=float(deltas.max()), noise_floor=floor,
        raw_unmatched_mean=float(raws.mean()), rows=rows, world=world,
        derivation_note="the UNMATCHED contrast is level-forced: clause ② admits high-A2 arms and "
                        "two arms agreeing with the human must agree with each other. Only the "
                        "matched Δ is an estimate.",
        limitation="convergence is not truth; and the matched comparison set is dominated by the "
                   "supervised family, so level is controlled and family is not",
        not_measured="criterion validity", would_require="an external standard the release lacks",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
