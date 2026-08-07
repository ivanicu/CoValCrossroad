#!/usr/bin/env python3
"""R831 -- why is the definition's extension empty?

See PREREGISTRATION.txt, committed before this file was executed.

ESTIMAND        the rank distribution of ③-ADMITTED arms within the A2 ordering, against the same
                for ③-EXCLUDED arms. Named before the method.
IDENTIFICATION  identified on the 93 arms carrying both a committed A2 and a satisfaction file.
                Whether a LARGER pool would populate the extension is NOT answerable here.
SCOPE           population: 93 arms from R436's committed cells. instrument:
                clause3_as_written.partition + R436's A2. baseline: permutation of ③-labels.
WORLDS          W-SELF-DEFEATING (③-admitted sit systematically low -> the conjunction is empty BY
                CONSTRUCTION, a fact about the DEFINITION) vs W-NEAR-MISS (spread -> a small-pool
                accident, a fact about the RELEASE).
KILL            CONDITIONAL. Evaluated only if both positive controls behave, the g=0 arm is null,
                and the SUBSTANTIVE ③-admitted subset is non-empty. Otherwise UNVERIFIED.
⚠ CONFOUND      ③ may admit mostly random/sham arms, which rank low because they are weak baselines
                I chose to build -- a SELECTION fact about my inventory, not about the definition.
                Control in the same iteration: the substantive subset is reported separately, and
                if it is EMPTY neither world is decidable and the round says so.
POSITIVE CTRL   two, both required: ③-labels assigned INDEPENDENTLY of rank must show NO separation
                (bounds over-firing); assigned to the bottom half must show separation (bounds
                blindness).
NEGATIVE CTRL   ③'s partition recomputed from source TWICE and compared. ⚠ Deliberately NOT `x - x`:
                the producer is invoked on both sides, which is the idiom R828/R829 established.
MULTIPLICITY    every reported cell, survivors and non-survivors alike.
ARTIFACT        results/r831_why_empty.json with source hash.
"""
from __future__ import annotations
import hashlib, json, pathlib, re, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parent.parent
RES = HERE / "results"
sys.path.insert(0, str(ROOT / "assurance"))
import clause3_as_written as C3                                            # noqa: E402

# pre-registered in PREREGISTRATION.txt, before any rank was computed
BASELINE = re.compile(r"(^random_|sham|^const|shuffle|^full)", re.I)
R436 = next(A24.glob("R436_*/results/r436_clause4_at_home.json"))


def mean_rank_gap(labels, ranks):
    """mean rank of the True group minus mean rank of the False group. Low = admitted sit low."""
    a = np.array([r for l, r in zip(labels, ranks) if l], float)
    b = np.array([r for l, r in zip(labels, ranks) if not l], float)
    if len(a) == 0 or len(b) == 0:
        return None
    return float(a.mean() - b.mean())


def perm_p(labels, ranks, rng, B=20000):
    obs = mean_rank_gap(labels, ranks)
    if obs is None:
        return None, None
    lab = np.array(labels)
    sim = np.array([mean_rank_gap(rng.permutation(lab), ranks) for _ in range(B)])
    p = max(2 * min((sim <= obs).mean(), (sim >= obs).mean()), 1.0 / (B + 1))
    return obs, float(p)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(831)
    print("\n  R831 · WHY IS THE DEFINITION'S EXTENSION EMPTY?\n")

    # ---- controls first ------------------------------------------------------------------
    n = 60
    ranks_s = list(range(1, n + 1))
    indep = [bool(v) for v in rng.integers(0, 2, n)]
    bottom = [r <= n // 2 for r in ranks_s]                # admitted == the low-rank half
    _, p_indep = perm_p(indep, ranks_s, np.random.default_rng(1))
    g_bot, p_bot = perm_p(bottom, ranks_s, np.random.default_rng(2))
    pc1 = p_indep is not None and p_indep > 0.05
    pc2 = p_bot is not None and p_bot < 0.01
    print(f"  POSITIVE  labels independent of rank -> p={p_indep:.4f}   "
          f"{'no separation   PASS' if pc1 else '⛔ FAIL — over-fires'}")
    print(f"  POSITIVE  labels ON the bottom half  -> p={p_bot:.5f}   "
          f"{'separation detected   PASS' if pc2 else '⛔ FAIL — blind'}")

    d = json.loads(R436.read_text())
    arms = [c["arm"] for c in d["cells"]]
    a2 = {c["arm"]: c["a2"] for c in d["cells"]}
    exc1, adm1, unk1 = C3.partition(arms)
    exc2, adm2, unk2 = C3.partition(arms)                  # the producer, invoked TWICE
    g0 = (exc1, adm1, unk1) == (exc2, adm2, unk2)
    print(f"  g=0       ③'s partition recomputed from source twice -> "
          f"{'identical   PASS' if g0 else '⛔ FAIL — nondeterministic'}")

    # ---- the estimand --------------------------------------------------------------------
    order = sorted(arms, key=lambda a: -a2[a])             # rank 1 = best A2
    rank = {a: i + 1 for i, a in enumerate(order)}
    adm = set(adm1)
    lab = [a in adm for a in order if a not in unk1]
    rk = [rank[a] for a in order if a not in unk1]
    gap, p = perm_p(lab, rk, rng)

    subst = sorted(a for a in adm if not BASELINE.search(a))
    print(f"\n  arms with A2 and a satisfaction file: {len(arms)}   "
          f"③ EXCLUDED {len(exc1)} · ADMITTED {len(adm1)} · UNKNOWN {len(unk1)}")
    print(f"  mean rank of ③-ADMITTED minus ③-EXCLUDED: {gap:+.2f} "
          f"(positive = admitted sit LOWER, i.e. worse)   permutation p = {p:.5f}")
    print(f"\n  ⚠ CONFOUND CONTROL -- substantive ③-admitted arms "
          f"(not random_/sham/const/shuffle/full): {len(subst)}")
    for a in subst[:12]:
        print(f"     {a:<28} A2 {a2[a]:.4f}   rank {rank[a]}/{len(order)}")
    if not subst:
        print("     (none — every ③-admitted arm is a baseline I chose to build)")

    controls_ok = pc1 and pc2 and g0
    if not controls_ok:
        world, verdict = "UNVERIFIED", "a control is unfit; no world is chosen"
    elif not subst:
        world = "UNVERIFIED"
        verdict = ("the substantive ③-admitted subset is EMPTY, so the rank shift is a SELECTION "
                   "fact about which arms were built and cannot separate the two worlds")
    elif p < 0.01 and gap > 0:
        world = "W-SELF-DEFEATING"
        verdict = ("③-admitted arms sit systematically lower in the A2 ordering -- the conjunction "
                   "is near-empty by construction, and that is a fact about the DEFINITION")
    else:
        world = "W-NEAR-MISS"
        verdict = ("③-admitted arms are spread across the ordering -- the emptiness is a small-pool "
                   "accident, a fact about the RELEASE")
    print(f"\n  VERDICT: {world} -- {verdict}\n")

    out = {"world": world, "verdict": verdict, "n_arms": len(arms),
           "clause3": {"excluded": len(exc1), "admitted": len(adm1), "unknown": len(unk1)},
           "mean_rank_gap_admitted_minus_excluded": gap, "perm_p": p,
           "substantive_admitted": subst,
           "substantive_admitted_ranks": {a: rank[a] for a in subst},
           "unknown_arms": sorted(unk1),
           "controls": {"pos_independent_null": pc1, "pos_bottom_half_fires": pc2,
                        "g0_partition_deterministic": g0},
           "source_r436": d.get("source_sha"),
           "source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]}
    (RES / "r831_why_empty.json").write_text(json.dumps(out, indent=1) + "\n")
    print(f"  artifact -> {RES/'r831_why_empty.json'}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
