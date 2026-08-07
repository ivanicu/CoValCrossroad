#!/usr/bin/env python3
"""R988 — the card caps size, and names two properties the definition has no clause for.

⛔ FIRST, A PRIOR-ART FAILURE OF MY OWN, TWO ROUNDS OLD. R986's headline was *"coval_core's
per-prompt size runs 2 to 4"*. `data/DATASET_CARD.md`, the release's own documentation, says it:

    "Most prompts end up with four core rubric items (about 95%), with the remainder having
     two or three."

**So R986's claim about `coval_core` is a VERIFICATION that the object does what it says, not a
finding.** The standard's own rule — prior_art non-empty ⇒ verification, never a finding — applies,
and this round records the downgrade rather than leaving R986's framing standing. What survives from
R986 is the part the card does NOT contain: the decomposition across 96 arms into pool capping (a
prompt property, 28 arms) versus arm selection (6 arms), and the measurement that every k12/k8/k6
family shares a byte-identical per-prompt profile.

⭐ AND READING THE CARD ANSWERS R987's NEXT, WHICH ASKED WHETHER SIZE IS THE RIGHT PROPERTY.

    "we keep only a small set of highly rated, NON-REDUNDANT, and NON-CONFLICTING rubric items …
     it aims to select UP TO FOUR rubric items with the highest average ratings that remain
     compatible with each other and do not repeat the same idea."

Three things the definition does not have:
  ① the card's size criterion is an **UPPER bound** — *up to four*. The definition's clause ① is a
     **LOWER** bound — *greater than one*. They constrain opposite ends.
  ② **non-redundant** — no clause.
  ③ **non-conflicting** — no clause.

ESTIMAND        how many arms clause ② admits whose nominal size EXCEEDS the card's cap of four —
                objects the release's own construction could not produce, which the definition
                nonetheless calls cores.
IDENTIFICATION  exact: nominal size is R987's adopted reading (max realised, artifact-recoverable,
                40 of 40 against the ledger) and clause-② admission is the committed operator.
                ⚠ NOT identified here: non-redundancy and non-conflict. Both need criterion TEXT and
                a similarity or compatibility judgement, which is a different instrument and a
                different round. Their absence from the definition is established by READING; their
                consequence is not measured, and that is stated rather than implied.
SCOPE           population : the 96 prompt-pool arms R986 classified
                instrument : mean A2 vs human targets, 8000-draw paired bootstrap, `lo > 0`
                baseline   : the card's own construction — "up to four"
                regime     : comparator `generic`; release one
WORLDS          A THE CAP IS REDUNDANT   clause ② already excludes every oversized arm, so the
                              definition's silence about an upper bound costs nothing.
                B THE DEFINITION ADMITS WHAT THE CARD WOULD NOT   at least one admitted arm exceeds
                              four, and it must be NAMED.
                prediction matrix: A -> 0 admitted arms above four. B -> a named set.
KILL            pre-registered, CONDITIONAL on the controls: 0 admitted arms above the cap ⇒ world B
                dead and the missing upper bound is harmless on this inventory.
POSITIVE CTRL   the operator must admit arms at or below the cap too — if it admitted ONLY oversized
                arms, or none at all, the comparison would be measuring the operator rather than the
                cap. Reported as the admitted count at size <= 4 beside the count above it.
NEGATIVE CTRL   an arm known to fail clause ② — `random_k4_s0`, whose margin is −0.0587 — must not
                appear in the admitted set at any size.
PLACEBO         `generic` against itself: margin exactly 0, never admitted.
NOISE FLOOR     admission is a bootstrap CI verdict at 3 seeds; a cell counts only if all agree.
MULTIPLICITY    every arm above the cap is tested and all are reported, admitted or not.
SEEDS           3; a verdict counts only under unanimity.
ARTIFACT        results/cap_and_missing_clauses.json with this file's source hash.
IMPOSSIBLE      construct validity — N/A: this shows the definition and the card disagree about
                size's direction, never which of them is right. The card calls core "a proof of
                concept … an invitation for others to develop better synthesis methods", so a
                definition departing from it is not automatically wrong — but the departure has to
                be deliberate, and it currently is not stated anywhere.
                non-redundancy / non-conflict — N/A here: needs criterion text and a compatibility
                instrument. Named, with what it would require.
"""
from __future__ import annotations
import hashlib
import itertools
import json
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
CARD = ROOT / "data/DATASET_CARD.md"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                          # noqa: E402

PR = list(itertools.combinations(range(4), 2))
NBOOT, SEEDS, COMP, CAP = 8000, (11, 22, 33), "generic", 4


def main() -> int:
    r986 = next(A27.glob("R986_*/results/size_decomposition.json"), None)
    if not (r986 and CARD.exists()):
        print("  UNRUNNABLE: R986's artifact or the dataset card is missing. Exit 2, never 0.")
        return 2
    card = CARD.read_text()
    # ⭐ the card's own words, quoted from the object rather than paraphrased
    quotes = {
        "cap": "up to four rubric items with the highest average ratings",
        "properties": "highly rated, non-redundant, and non-conflicting rubric items",
        "size_distribution": "Most prompts end up with four core rubric items (about 95%)",
        "purpose": "Core is a proof of concept",
    }
    found = {k: (v in card) for k, v in quotes.items()}
    print("THE CARD, quoted from the object:")
    for k, v in quotes.items():
        print(f"  {k:<18} present in DATASET_CARD.md: {found[k]}   {v!r}")
    if not all(found.values()):
        print("  UNRUNNABLE: a quote did not verify against the card. Exit 2, never 0.")
        return 2

    rows = {r["arm"]: r for r in json.loads(r986.read_text())["rows"]}
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

    def admits(nm):
        v = vec(nm)
        if v is None:
            return None
        d = v - comp
        return all(float(np.percentile(c @ d / n, 2.5)) > 0 for c in CNT)

    over = sorted(a for a, r in rows.items() if r["max"] > CAP)
    under = sorted(a for a, r in rows.items() if r["max"] <= CAP)
    adm_over = [(a, rows[a]["max"]) for a in over if admits(a)]
    adm_under = [a for a in under if admits(a)]
    print(f"\nPOPULATION  {len(rows)} prompt-pool arms · {len(over)} above the card's cap of "
          f"{CAP} · {len(under)} at or below")
    print(f"\n⭐ ADMITTED by clause ② with nominal size > {CAP} — objects the card's own "
          f"construction could not produce:")
    for a, k in adm_over:
        print(f"     {a:<24} nominal size {k}")
    print(f"   {len(adm_over)} of {len(over)}")

    # ── CONTROLS
    print(f"\n  POSITIVE  the operator also admits arms AT or BELOW the cap: {len(adm_under)} "
          f"of {len(under)} — so the comparison measures the cap, not the operator")
    neg_ok = admits("random_k4_s0") is False
    plac = np.percentile(CNT[0] @ (comp - comp) / n, 2.5)
    plac_ok = float(plac) == 0.0
    print(f"  NEGATIVE  random_k4_s0 (margin −0.0587) is not admitted: {neg_ok}")
    print(f"  PLACEBO   generic against itself: lo = {float(plac):.1e}, never admitted: {plac_ok}")
    ctrl_ok = neg_ok and plac_ok and len(adm_under) > 0 and len(over) > 0

    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; the comparison certifies nothing"
    elif not adm_over:
        world = (f"A THE CAP IS REDUNDANT — clause ② already excludes every arm above {CAP}, so the "
                 f"definition's silence about an upper bound costs nothing on this inventory")
    else:
        world = (f"B THE DEFINITION ADMITS WHAT THE CARD WOULD NOT — {len(adm_over)} admitted arms "
                 f"exceed the card's cap of {CAP}: "
                 + ", ".join(f"{a} (size {k})" for a, k in adm_over))
    print(f"\n⭐ {world}")
    print("\n⚠ AND TWO PROPERTIES THE CARD CALLS CONSTITUTIVE HAVE NO CLAUSE AT ALL:")
    print("   non-redundant · non-conflicting — established by READING the card; their consequence")
    print("   is NOT measured here, because it needs criterion text and a compatibility instrument.")

    out = HERE / "results" / "cap_and_missing_clauses.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        card_quotes=quotes, card_quotes_verified=found, cap=CAP,
        n_arms=len(rows), n_over_cap=len(over), n_admitted_over_cap=len(adm_over),
        admitted_over_cap=[{"arm": a, "nominal_size": k} for a, k in adm_over],
        n_admitted_at_or_below=len(adm_under),
        controls={"positive_admits_below_cap": len(adm_under), "negative_random_k4_rejected": neg_ok,
                  "placebo_self_zero": plac_ok, "all_ok": ctrl_ok},
        world=world,
        r986_downgrade="R986's claim that coval_core's per-prompt size runs 2 to 4 is a "
                       "VERIFICATION of the dataset card, which states 'about 95%' have four and "
                       "'the remainder two or three'. Its decomposition across 96 arms stands.",
        not_measured=["non-redundancy", "non-conflict"],
        would_require="criterion text plus a semantic-similarity and weight-compatibility "
                      "instrument, neither of which this round builds",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
