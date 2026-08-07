"""R285 — how many resolution units wide is the space the definition partitions?

WHY. Every clause, arm and verdict on this page lives between two references: `chance` at the
bottom (A2 = 0.5 by construction of a sign comparison) and the HUMAN CEILING at the top. R306
measured the arms at all 15,593 annotations. **The ceiling was never recomputed** — it is quoted
from a 3-draw era as 0.5451/0.5528 — and it is the reference that says how much room the definition
has to work in at all. If the band is only a few MDEs wide, then "4 admitted, 6 excluded" is a
partition of a space barely larger than the instrument's own resolution, and that is the single most
important scope sentence the artifact can carry.

⚠ AND `THE` CEILING IS NOT ONE NUMBER — that is the trap this round exists to avoid rather than
discover. Three defensible ceilings, and they answer different questions:
  (a) HUMAN vs HUMAN, one annotator predicting another. This is the ceiling for an arm scored
      against a SINGLE drawn annotator, which is what every A2 on this page is.
  (b) HUMAN vs the CONSENSUS of the others. Higher, because a consensus is denoised — and NOT the
      right ceiling for our arms, since our arms are scored against individuals.
  (c) the ORACLE: the best achievable class per prompt against the drawn annotator. Higher still.
Quoting (b) or (c) beside arms measured against (a) would inflate every "fraction of ceiling" on
the page. All three are computed and the one that matches the arms' estimand is named.

ESTIMAND        (a) the inter-annotator A2 ceiling, all pairs, all prompts;
                (b) the consensus ceiling and (c) the per-prompt oracle, for contrast;
                (d) the admissible band width (ceiling − chance) expressed in MDE units;
                (e) each arm's position in that band.
IDENTIFICATION  exact for (a)-(c) — all are averages over the release's own annotations, with no
                model in the loop. (d) and (e) are DERIVATIONS and are labelled so.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument NONE for the ceiling
                (it is human-vs-human) and Qwen3.5-2B-Base for the arms · baseline chance = 0.5 ·
                regime pairwise accuracy over 6 pairs, all annotators.
WORLDS          W-ROOMY   the band is wide relative to the MDE (say >6 units) -> the definition
                          partitions a space the instrument can see structure in, and the
                          admitted/excluded distinction is about cores.
                W-CRAMPED the band is a few MDEs -> the partition is mostly about the instrument,
                          and the honest headline for the whole artifact changes from "what a core
                          is" to "what this release can distinguish".
KILL            pre-registered: if (ceiling − 0.5) / MDE_median < 6, FORMULATION.md must carry the
                band width in MDE units in its opening block, beside the definition, permanently.
POSITIVE CTRL   an annotator against THEMSELVES must give A2 = 1.0 exactly. Catches any class-
                function or pairing error, which would silently deflate the ceiling and inflate
                every fraction computed from it.
NEGATIVE CTRL   an annotator against a RANDOMLY DRAWN annotator OF A DIFFERENT PROMPT. Humans
                agreeing at chance across prompts is what makes the within-prompt number a measure
                of shared judgement rather than of a shared response-ordering habit. It must land
                at ~0.5; if it lands high, the ceiling is measuring position bias, not agreement.
PLACEBO         included in the positive control.
NOISE FLOOR     the per-prompt MDE distribution from R306's 45 cells, carried in and cited, not
                re-derived.
MULTIPLICITY    3 ceilings + 1 negative control; the claim is a scope statement, not a test family.
SEEDS           the cross-prompt negative control uses 5 seeds and all are reported.
ARTIFACT        results/band.json with source hash.
IMPOSSIBLE      construct validity — whether pairwise agreement with one annotator is the right
                target at all is not answerable here and is not claimed either way.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
CHANCE = 0.5
ARMS = ["coval_core", "topw_k4", "generic", "gen", "full", "topwvar_k4",
        "random_k4_s0", "topabs_k4", "topvar_k4", "gen_sham"]
R306 = json.loads((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                   / "R306_the_table_at_every_annotator/results/all_annotators.json").read_text())


def a2(c, h):
    return float(np.mean([c[q] == h[q] for q in range(len(PAIRS))]))


def main():
    tg, _ = load_targets()
    sat = {}
    for a in ARMS:
        S = load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz")
        sat[a] = {p: cls(yvec(S[p], sorted({i for i, _ in S[p]}))) for p in S if p in tg and len(tg[p]) >= 2}
    pids = sorted(set.intersection(*(set(v) for v in sat.values())))
    HS = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    N = len(pids)
    m = np.array([len(HS[p]) for p in pids])
    print(f"  {N} prompts · {int(m.sum())} annotations · median {int(np.median(m))} per prompt\n")

    # ---- positive control -----------------------------------------------------------------
    self_a2 = np.mean([a2(HS[p][0], HS[p][0]) for p in pids])
    pos_ok = self_a2 == 1.0
    print(f"  POSITIVE CONTROL  an annotator against THEMSELVES  A2 = {self_a2:.12f}  "
          f"{'PASS' if pos_ok else 'FAIL'}")

    # ---- chance is MEASURED, per comparison type, and it is NOT 0.5 -----------------------
    # ⚠ FIRST RUN FAILED HERE AND THE CONTROL WAS RIGHT. I pre-registered "annotators of different
    # prompts must land at ~0.5" and it returned 0.3869 with sd 0.0037 across five seeds. 0.5 is
    # wrong: A2 counts matches on a THREE-valued sign vector (-1, 0, +1), so random agreement is
    # sum(p_i^2) over the sign marginal, not 1/2. With ties common among humans that is ~0.39; with
    # ties RARE in a model's continuous satisfaction scores it is higher. So the arms and the
    # ceiling are DIFFERENT COMPARISON TYPES WITH DIFFERENT CHANCE LEVELS, and dividing an arm's
    # (A2 - 0.5) by a human-vs-human band would have been a category error printed as a fraction.
    # Both floors are now measured; nothing is assumed.
    def cross(kind, seeds=5):
        out = []
        for s in range(seeds):
            rng = np.random.default_rng(7000 + s)
            v = []
            for p in pids:
                q = pids[int(rng.integers(N))]
                if q == p:
                    continue
                h = HS[q][int(rng.integers(len(HS[q])))]          # a human of ANOTHER prompt
                if kind == "hh":
                    v.append(a2(HS[p][int(rng.integers(len(HS[p])))], h))
                else:
                    v.append(a2(sat[kind][p], h))                  # this prompt's ARM vs that human
            out.append(float(np.mean(v)))
        return float(np.mean(out)), float(np.std(out))

    CH = {}
    CH["human vs human"] = cross("hh")
    for a in ("coval_core", "topw_k4", "generic", "random_k4_s0"):
        CH[f"arm `{a}` vs human"] = cross(a)
    print("\n  MEASURED CHANCE, per comparison type (partner drawn from a DIFFERENT prompt)\n")
    for k_, (mu, sd) in CH.items():
        print(f"    {k_:<28}{mu:.4f}  (5 seeds, sd {sd:.4f})")
    spread = max(v[0] for v in CH.values()) - min(v[0] for v in CH.values())
    print(f"\n    spread across comparison types {spread:.4f}   "
          f"— 0.5 is not any of them, and they are not each other")
    neg_ok = all(sd < 0.02 for _, sd in CH.values())
    print(f"    NEGATIVE CTRL: are the floors stable across seeds ?  "
          f"{'PASS' if neg_ok else 'FAIL — the floor itself is noisy'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — controls did not behave; no band is admissible.")
        return 1
    CHANCE_HH = CH["human vs human"][0]

    # ---- the three ceilings ------------------------------------------------------------------
    pair_c, cons_c, orac_c = [], [], []
    for p in pids:
        H = HS[p]
        k = len(H)
        pv = [a2(H[i], H[j]) for i, j in itertools.combinations(range(k), 2)]
        pair_c.append(np.mean(pv))
        # consensus of the OTHERS, leave-one-out, majority sign per pair
        cv = []
        for i in range(k):
            rest = [H[j] for j in range(k) if j != i]
            cons = tuple(float(np.sign(sum(r[q] for r in rest))) for q in range(6))
            cv.append(a2(cons, H[i]))
        cons_c.append(np.mean(cv))
        # oracle: the single class maximising mean agreement with THIS prompt's annotators
        best = max((np.mean([a2(c, h) for h in H])
                    for c in {tuple(float(np.sign(sum(r[q] for r in H))) for q in range(6))}
                    | {tuple(x) for x in H}), default=0.0)
        orac_c.append(best)
    CEIL = {"(a) human vs human — MATCHES the arms": float(np.mean(pair_c)),
            "(b) human vs consensus of others": float(np.mean(cons_c)),
            "(c) per-prompt oracle class": float(np.mean(orac_c))}
    print("\n  THE THREE CEILINGS\n")
    for k_, v in CEIL.items():
        print(f"    {k_:<42}{v:.4f}")
    ceil_a = CEIL["(a) human vs human — MATCHES the arms"]

    # ---- the band, in MDE units -- a DERIVATION -------------------------------------------
    mdes = sorted(c["mde"] for c in R306["cells"].values())
    mde_med = float(np.median(mdes))
    band = ceil_a - CHANCE_HH
    units = band / mde_med
    print(f"\n  THE ADMISSIBLE BAND — a DERIVATION (measured band ÷ measured MDE)\n")
    print(f"    MEASURED chance(human vs human) {CHANCE_HH:.4f}  →  ceiling(a) {ceil_a:.4f}"
          f"      band = {band:.4f}")
    print(f"    (the discarded 0.5 would have given a band of {ceil_a - 0.5:+.4f} — "
          f"{abs((ceil_a-0.5)/band):.2f}x the real one, and of the wrong sign if negative)")
    print(f"    R306 per-cell MDE: median {mde_med:.4f}, range {mdes[0]:.4f}–{mdes[-1]:.4f}")
    print(f"    band width = {units:.2f} MDE units")

    print(f"\n  WHERE THE ARMS SIT IN IT\n")
    print(f"    {'arm':<14}{'A2':>9}{'its OWN chance':>16}{'MDE units above it':>25}")
    rows = {}
    for a in ARMS:
        v = float(np.mean([np.mean([a2(sat[a][p], h) for h in HS[p]]) for p in pids]))
        fl = CH.get(f"arm `{a}` vs human", (None,))[0]
        base = fl if fl is not None else float("nan")
        rows[a] = dict(a2=v, own_chance=base, above_own=(v - base) if fl else None,
                       units=((v - base) / mde_med) if fl else None)
        s1 = f"{base:.4f}" if fl else "  n/a "
        s2 = f"{(v-base)/mde_med:>8.2f}" if fl else "     n/a"
        print(f"    {a:<14}{v:>9.4f}{s1:>16}{s2:>25}")
    print(f"    {'HUMAN (a)':<14}{ceil_a:>9.4f}{CHANCE_HH:>16.4f}{units:>25.2f}")

    killed = units < 6
    print("\n  " + "=" * 74)
    print(f"  PRE-REGISTERED KILL: band < 6 MDE units ?   {killed}   ({units:.2f})")
    if killed:
        print("  -> W-CRAMPED. The definition partitions a space only a few resolution units wide.")
        print("     The band width belongs beside the definition permanently, because 'admitted vs")
        print("     excluded' is then a statement about this instrument as much as about cores.")
    else:
        print("  -> W-ROOMY. There is structure in the band the instrument can see.")
    print("  " + "=" * 74)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    o = pathlib.Path(__file__).parent / "results" / "band.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(source_sha=src, n_prompts=N, ceilings=CEIL, chance=CHANCE,
                                 band=band, mde_median=mde_med, band_in_mde_units=units,
                                 arms=rows, measured_chance={k_: v for k_, v in CH.items()},
                                 cramped=bool(killed)), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
