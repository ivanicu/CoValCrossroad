#!/usr/bin/env python3
"""R992 — what would the two closable departures actually exclude?

⛔ WHY. R991 stated three departures from the release's card and closed none, saying each closure is
an authorial decision of the kind R987 made for the size reading. R987's discipline was to split the
decision: decide the measurable half on evidence, and name what stays authorial. **For a PROPOSED
clause the measurable half is the standard's own remedy — name an admissible object this clause
EXCLUDES — and then ask whether another clause already excludes it.** A proposed clause whose
exclusions are all already excluded is decoration, and adding it would cost nothing and change
nothing. One whose exclusions are unique is load-bearing, and adding it has a price that should be
paid deliberately.

Two of the three departures are closable this way. The third — non-conflict — is not, because R989
measured that core weights are unpublished and only 7.8% of core items match a full item verbatim.

ESTIMAND        for each proposed clause, ① the clause-② passers it would exclude, and ② how many of
                those are ALREADY excluded by clause ③ (provenance) or clause ④ (response-only bar).
                The difference is the clause's unique cost.
IDENTIFICATION  identified for the cap, which is a function of nominal size (R987's adopted reading,
                artifact-recoverable on 40 of 40).
                ⚠ PARTIALLY for non-redundancy: its threshold is a CHOICE, so the round reports the
                whole curve of thresholds rather than picking one — a specification curve, not a
                cell. And the measure is R990's lexical proxy, sound in one direction only.
SCOPE           population : the 96 prompt-pool arms; clause ② admission recomputed and PERSISTED
                             this time, because R985 and R988 both hit the missing passer list
                instrument : mean A2 vs human targets, 8000-draw paired bootstrap, `lo > 0`;
                             Jaccard over content words for redundancy
                baseline   : the released core's own within-arm redundancy — a clause that excluded
                             the instance would be self-refuting, and that is checked
                regime     : comparator `generic`; release one
WORLDS          A BOTH ARE DECORATION   every arm each proposed clause would exclude is already
                              excluded by ③ or ④, so closing the departures is free.
                B AT LEAST ONE IS LOAD-BEARING   a proposed clause uniquely excludes an admitted
                              arm, so closing that departure changes the extension and costs
                              something nameable.
                prediction matrix: A -> unique cost 0 for both. B -> a named set.
KILL            pre-registered, CONDITIONAL on the controls: unique cost 0 for both ⇒ world B dead.
POSITIVE CTRL   the released core must PASS both proposed clauses. A cap at four that excluded
                `coval_core`, or a redundancy threshold that did, would be self-refuting and the
                round would report UNVERIFIED rather than a cost.
NEGATIVE CTRL   an arm known to fail clause ② must not appear among the passers at all.
PLACEBO         a cap at the maximum observed size must exclude nobody — a clause set outside the
                data's range has zero cost by construction, and seeing that confirms the accounting.
NOISE FLOOR     admission is a bootstrap verdict at 3 seeds, unanimity required.
MULTIPLICITY    the redundancy threshold is swept over the whole range and every cell reported.
SEEDS           3 for admission.
ARTIFACT        results/departure_costs.json with this file's source hash, INCLUDING the passer list.
IMPOSSIBLE      non-conflict — N/A: R989 measured the wall (no core weights, 7.8% verbatim match).
                whether the departures SHOULD be closed — N/A and deliberately so: this prices the
                decision, it does not make it.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import pathlib
import re
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                          # noqa: E402

PR = list(itertools.combinations(range(4), 2))
NBOOT, SEEDS, COMP, CAP = 8000, (11, 22, 33), "generic", 4
STOP = set("the a an and or of to in for on with that this it is are be as at by from not you your "
           "model response should does do any all more most if when than then but so its their "
           "there they them he she we our us can could would will may might have has had".split())


def toks(s):
    return {w for w in re.findall(r"[a-z]{3,}", s.lower()) if w not in STOP}


def jac(a, b):
    u = a | b
    return len(a & b) / len(u) if u else 0.0


def main() -> int:
    r986 = next(A27.glob("R986_*/results/size_decomposition.json"), None)
    r920 = next(A26.glob("R920_*/results/clause3_detectability.json"), None)
    if not (r986 and r920):
        print("  UNRUNNABLE: a prior artifact is missing. Exit 2, never 0.")
        return 2
    sizes = {r["arm"]: r["max"] for r in json.loads(r986.read_text())["rows"]}
    labelled = {a["arm"]: a["labelled"] for a in json.loads(r920.read_text())["arms"]}

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{COMP}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        f = RES / f"sat_{nm}.npz"
        if not f.exists():
            return None
        Sa = load_sat(f)
        v = np.full(n, np.nan)
        for i, p in enumerate(pids):
            if p in Sa:
                c = np.array(cls(yvec(Sa[p], sorted({j for j, _ in Sa[p]}))), float)
                v[i] = float(np.mean([(c == h).mean() for h in H[p]]))
        return np.nan_to_num(v, nan=np.nanmean(v))

    comp = vec(COMP)
    CNT = [np.random.default_rng(s).multinomial(n, np.ones(n) / n, size=NBOOT).astype(float)
           for s in SEEDS]

    def admits(v):
        d = v - comp
        return all(float(np.percentile(c @ d / n, 2.5)) > 0 for c in CNT)

    # ── clause ② passers, RECOMPUTED AND PERSISTED (R985 and R988 both hit the missing list)
    passers = []
    for a in sorted(sizes):
        v = vec(a)
        if v is not None and admits(v):
            passers.append(a)
    print(f"POPULATION  {len(sizes)} prompt-pool arms · clause ② admits {len(passers)}")

    # ── clause ④: beats the judge-free floor
    text = {}
    for line in open(ROOT / "data/comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        rs = r.get("responses") or []
        if len(rs) == 4:
            text[r["prompt_id"]] = [" ".join(str(m.get("content", "")) for m in
                                             (it.get("messages") or []) if isinstance(m, dict))
                                    for it in rs]
    CHm = np.array([[len(t) for t in text[p]] if p in text else [0, 0, 0, 0] for p in pids], float)
    floor_v = np.array([float((H[p] == np.sign(CHm[i][[u for u, _ in PR]]
                                               - CHm[i][[w for _, w in PR]])).mean())
                        for i, p in enumerate(pids)])

    def beats_floor(nm):
        v = vec(nm)
        if v is None:
            return None
        d = v - floor_v
        return all(float(np.percentile(c @ d / n, 2.5)) > 0 for c in CNT)

    # ── within-arm redundancy, R990's measure applied per arm
    def redundancy(nm):
        f = RES / f"sat_{nm}.npz"
        if not f.exists():
            return None
        Sa = load_sat(f)
        vals = []
        for p in list(Sa)[:400]:                     # 400 prompts is ample and keeps this cheap
            idx = sorted({i for i, _ in Sa[p]})
            if len(idx) < 2:
                continue
            vals.append(0.0)                          # placeholder replaced below
        return None

    # criterion TEXT per arm is not in the sat files; redundancy is only computable for the
    # RELEASED core and full rubrics, which is what R990 used.
    print("\n⚠ REDUNDANCY IS NOT COMPUTABLE PER ARM, and the round says so rather than faking it.")
    print("   The sat_*.npz files carry criterion INDICES and satisfaction, never criterion TEXT.")
    print("   R990 measured redundancy on the RELEASE's own core and full rubrics, where text is")
    print("   published. An arm's selected criteria cannot be resolved back to text from these")
    print("   artifacts, so the redundancy departure is NOT closable on this inventory either.")

    # ── the cap, which IS computable
    would_exclude = [a for a in passers if sizes[a] > CAP]
    already = {}
    for a in would_exclude:
        by3 = labelled.get(a)                        # None where provenance is unrecorded
        by4 = beats_floor(a)
        already[a] = {"clause3_labelled": by3, "clause4_beats_floor": by4,
                      "already_excluded": bool(by3 is True or by4 is False)}
    unique = [a for a, d in already.items() if not d["already_excluded"]]
    print(f"\nTHE CAP AT {CAP}  would exclude {len(would_exclude)} of the {len(passers)} passers:")
    print(f"  {'arm':<24}{'size':>5}{'③ labelled':>13}{'④ beats floor':>15}   already excluded?")
    for a in would_exclude:
        d = already[a]
        print(f"  {a:<24}{sizes[a]:>5}{str(d['clause3_labelled']):>13}"
              f"{str(d['clause4_beats_floor']):>15}   {d['already_excluded']}")
    print(f"\n  ⭐ UNIQUE COST of the cap: {len(unique)} arm(s) {unique}")

    # ── CONTROLS
    core_ok = "coval_core" in passers and sizes.get("coval_core", 99) <= CAP
    neg_ok = "random_k4_s0" not in passers
    maxsz = max(sizes.values())
    plac = [a for a in passers if sizes[a] > maxsz]
    print(f"\n  POSITIVE  the released core passes clause ② and the proposed cap: {core_ok}")
    print(f"  NEGATIVE  random_k4_s0 is not among the passers: {neg_ok}")
    print(f"  PLACEBO   a cap at the maximum observed size ({maxsz}) excludes {len(plac)} arms")
    ctrl_ok = core_ok and neg_ok and not plac

    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; the costs certify nothing"
    elif not unique:
        world = (f"A THE CAP IS DECORATION — every arm it would exclude is already excluded by "
                 f"clause ③ or ④, so closing that departure is free")
    else:
        world = (f"B THE CAP IS LOAD-BEARING — it uniquely excludes {len(unique)} admitted arm(s): "
                 f"{unique}. Closing that departure changes the extension and the cost is nameable.")
    print(f"\n⭐ {world}")
    print(f"\n⚠ AND ONLY ONE OF THE THREE DEPARTURES TURNED OUT TO BE CLOSABLE HERE. Non-conflict")
    print(f"   was already unreachable (R989). Non-redundancy is unreachable per-arm for a reason")
    print(f"   this round measured: the artifacts carry indices, not text.")

    out = HERE / "results" / "departure_costs.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_arms=len(sizes), comparator=COMP, cap=CAP, nboot=NBOOT, seeds=list(SEEDS),
        clause2_passers=passers,                    # ⭐ PERSISTED — R985 and R988 both needed this
        cap_would_exclude=would_exclude, already_excluded=already, unique_cost=unique,
        controls={"positive_core_passes": core_ok, "negative_random_not_passer": neg_ok,
                  "placebo_cap_at_max_excludes": len(plac), "all_ok": ctrl_ok},
        world=world,
        redundancy_not_closable="sat_*.npz carry criterion INDICES and satisfaction, never TEXT; "
                                "R990's measure needs the published rubric text, which exists only "
                                "for the release's own core and full sets",
        not_decided="whether the departures SHOULD be closed — this prices the decision only",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
