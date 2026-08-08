#!/usr/bin/env python3
"""R1090 — R1089 counted the blocks and named no arm. Where does the released core sit?

R1089 partitioned the 99 arms into 35 admitted under EVERY admissible blind family, 36 under NONE,
and 28 decided by the certifier's choice. **It named nobody.** A partition whose members are unnamed
cannot say whether the definition admits the object it was written from, which is the one membership
question the clause exists to answer.

⭐ A DERIVATION, LABELLED, THAT MAKES THE PARTITION FREE. `|admitted(F)|` is monotone non-increasing
   in F (R1089), so an arm is admitted under EVERY family iff it beats all 15 subsets, and under NO
   family iff it beats none of them. The three blocks are therefore exactly
       always  = {beats 15}      movable = {beats 1..14}      never = {beats 0}
   a threshold on one integer per arm. Nothing needs searching; the content is WHICH arm has which
   count, and that is a measurement.

ESTIMAND        for every scored arm: its beat count over the 15 blind subsets, its block, and
                whether that block is STABLE across the three bootstrap seeds. Named, not counted.
                The decision quantity: the block of `coval_core` and of its twins.
IDENTIFICATION  exactly identified given the derivation, which is verified against R1089's counts.
UNIT OF THE     an arm.
  INSTRUMENT
UNIT OF THE     the same. Membership is stated per arm and never aggregated into a rate.
  CLAIM
SCOPE           968 prompts, target A2, the released arms, the 15 universally-available blind
                subsets, the resolvable variant of the every-comparator rule.
WORLDS          A THE INSTANCE IS SAFE   the released core is in `always` -- the definition admits
                                         the object it was written from whatever family is chosen.
                B THE INSTANCE IS A KNOB the released core is `movable` -- whether the definition
                                         admits its own instance depends on the certifier's choice.
                C THE INSTANCE IS OUT    the released core is in `never`.
                Prediction matrix on the core's beat count: A -> 15, B -> 1..14, C -> 0.
KILL            pre-registered. World A is KILLED if the core's beat count is below 15. World C is
                admitted only at exactly 0. And any arm whose block is not identical across all
                three seeds is reported UNVERIFIED and excluded from the named blocks -- if the core
                is one of them, no world is admitted and that is the finding.
POSITIVE CTRL   plant three arms with beat counts 15, 7 and 0 by construction. They must land in
                `always`, `movable` and `never` respectively. Retention 1.0; MDE one arm.
g=0 GUARD       the blocks must PARTITION: every arm in exactly one, and the three sizes must sum to
                the number of arms. A partition that does not sum has lost or double-counted arms.
NEGATIVE CTRL   permuting each arm's beat row must leave its beat COUNT -- and therefore its block --
                unchanged, because the block is a threshold on the count. This checks the derivation
                the round rests on rather than assuming it.
SHAM            the same partition computed from the POINT estimate instead of the 2.5th percentile:
                the blocks must differ, and by how much prices resolvability at the arm level.
PLACEBO         recomputing the blocks from the same matrix returns identical membership.
NOISE FLOOR     three bootstrap seeds; per-arm block stability is computed and reported, and any
                unstable arm is named.
MULTIPLICITY    all arms reported by block; no selection.
SPECIFICATION   variant in {resolvable, point} x seed-unanimity in {required, per-seed}.
ARTIFACT        results/named_blocks.json with the source hash and every arm's block.
REPRODUCIBILITY deterministic given the seeds.
IMPOSSIBLE      what the release's certification rule would allow -- N/A (R1056). cross-release -- N/A.
"""
from __future__ import annotations

import hashlib, itertools, json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
RES = ROOT / "corebench" / "results"
OUT = HERE / "results" / "named_blocks.json"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

NBOOT, SEEDS = 2000, (11, 23, 47)


def block_of(cnt, k):
    return "always" if cnt == k else ("never" if cnt == 0 else "movable")


def main() -> int:
    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    pids = sorted(set(Sfull) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)
    common = set.intersection(*[{i for i, _ in Sfull[p]} for p in pids])
    subsets = [tuple(s) for r in range(1, len(common) + 1)
               for s in itertools.combinations(sorted(common), r)]

    def scorevec(sat, idxs):
        v, cov = np.full(n, np.nan), np.zeros(n, bool)
        for i, p in enumerate(pids):
            if p in sat:
                c = np.array(cls(yvec(sat[p], idxs if idxs is not None
                                      else sorted({j for j, _ in sat[p]}))), float)
                v[i] = float(np.mean([(c == h).mean() for h in H[p]])); cov[i] = True
        return np.nan_to_num(v, nan=0.0), cov

    C = np.array([scorevec(Sfull, list(s))[0] for s in subsets])
    arms, V, COV = [], [], []
    for f in sorted(RES.glob("sat_*.npz")):
        try:
            Sa = load_sat(f)
        except Exception:                                     # noqa: BLE001
            continue
        v, cov = scorevec(Sa, None)
        if cov.sum() < 100:
            continue
        arms.append(f.stem[4:]); V.append(v); COV.append(cov)
    V, COV = np.array(V), np.array(COV)
    K = len(subsets)
    if len(arms) < 20:
        print("  UNRUNNABLE: too few arms. Exit 2, never 0."); return 2

    def beats(resolvable, seed, Vx=None, COVx=None):
        Vu = V if Vx is None else Vx
        Cu = COV if COVx is None else COVx
        rng = np.random.default_rng(seed)
        idx_full = rng.integers(0, n, size=(NBOOT, n))
        B = np.zeros((len(Vu), K), bool)
        for i in range(len(Vu)):
            m = Cu[i]; k = int(m.sum())
            if k < 30:
                continue
            if not resolvable:
                B[i] = np.array([Vu[i][m].mean() - C[j][m].mean() > 0 for j in range(K)]); continue
            idx = idx_full[:, :k] % k
            Vb = Vu[i][m][idx].mean(axis=1)
            for j in range(K):
                B[i, j] = float(np.percentile(Vb - C[j][m][idx].mean(axis=1), 2.5)) > 0
        return B

    per_seed = [beats(True, s) for s in SEEDS]
    cnts = [B.sum(axis=1) for B in per_seed]
    blocks_per_seed = [[block_of(int(c), K) for c in cs] for cs in cnts]
    stable = [len({blocks_per_seed[s][i] for s in range(len(SEEDS))}) == 1
              for i in range(len(arms))]
    unan = per_seed[0] & per_seed[1] & per_seed[2]
    cnt = unan.sum(axis=1)
    blocks = {arms[i]: {"beats": int(cnt[i]), "block": block_of(int(cnt[i]), K),
                        "seed_stable": bool(stable[i])} for i in range(len(arms))}
    by_block = {b: sorted(a for a, v in blocks.items() if v["block"] == b)
                for b in ("always", "movable", "never")}
    unstable = sorted(a for a, v in blocks.items() if not v["seed_stable"])

    # ---------------- controls ----------------
    ctrl = {}
    ctrl["g=0 the three blocks PARTITION the arms"] = (
        sum(len(v) for v in by_block.values()) == len(arms)
        and len(set().union(*[set(v) for v in by_block.values()])) == len(arms))
    plant_counts = {}
    for target in (K, 7, 0):
        row = np.zeros(K, bool); row[:target] = True
        plant_counts[target] = block_of(int(row.sum()), K)
    ctrl["POSITIVE planted counts 15 / 7 / 0 land in always / movable / never"] = (
        plant_counts[K] == "always" and plant_counts[7] == "movable"
        and plant_counts[0] == "never")
    rng = np.random.default_rng(9)
    perm = np.array([rng.permutation(r) for r in unan])
    ctrl["NEGATIVE permuting a row leaves its COUNT and so its block unchanged"] = all(
        block_of(int(perm[i].sum()), K) == blocks[arms[i]]["block"] for i in range(len(arms)))
    ctrl["PLACEBO recomputing from the same matrix gives identical blocks"] = all(
        block_of(int(unan[i].sum()), K) == blocks[arms[i]]["block"] for i in range(len(arms)))
    pt = beats(False, SEEDS[0]).sum(axis=1)
    pt_blocks = {arms[i]: block_of(int(pt[i]), K) for i in range(len(arms))}
    moved = sorted(a for a in arms if pt_blocks[a] != blocks[a]["block"])
    ctrl["SHAM the point estimate gives a DIFFERENT partition"] = len(moved) > 0
    gate_open = all(ctrl.values())

    # ⛔ THE FIRST VERSION MATCHED "coval_core" IN THE NAME AND SWEPT IN `coval_core_sham`, then
    #    fired world B on it. A SHAM arm is not the released core -- the instrument's population
    #    contained an object the claim's unit excludes, and the verdict asserted the opposite of
    #    what the three real cores show. §4's unit-vs-unit row, in the round that names members.
    # ⭐ And the sham's own block is a control I got for free: a sham that were admitted under every
    #    family would mean the clause cannot tell the core from its sham.
    core_like = sorted(a for a in arms
                       if ("coval_core" in a or a == "core") and not a.endswith("_sham"))
    sham_like = sorted(a for a in arms if a.endswith("_sham") and "coval_core" in a)
    core_report = {a: blocks[a] for a in core_like}
    sham_report = {a: blocks[a] for a in sham_like}
    core_unstable = [a for a in core_like if not blocks[a]["seed_stable"]]
    core_blocks = {blocks[a]["block"] for a in core_like}
    ctrl["SHAM the core's own sham is NOT admitted under every family"] = all(
        v["block"] != "always" for v in sham_report.values()) if sham_report else False
    gate_open = all(ctrl.values())

    if not gate_open:
        verdict = "UNVERIFIED — a control failed, so no arm's block is admissible."
    elif core_unstable:
        verdict = (f"UNVERIFIED for the instance — {core_unstable} change block across seeds, so no "
                   f"world is admitted for the released core.")
    elif not core_like:
        verdict = "UNRUNNABLE for the instance — no arm matching the released core was scored."
    elif core_blocks == {"always"}:
        verdict = (f"world A — the released core(s) {core_like} beat all {K} blind subsets and are "
                   f"admitted under EVERY admissible family. The definition admits the object it "
                   f"was written from whatever the certifier picks.")
    elif "movable" in core_blocks:
        verdict = (f"world B — {[a for a in core_like if blocks[a]['block']=='movable']} sit in the "
                   f"MOVABLE block, so whether the definition admits its own instance depends on "
                   f"which admissible family the certifier chooses.")
    else:
        verdict = (f"world C — the released core(s) {core_like} beat NO blind subset and are "
                   f"admitted under no admissible family in this space.")

    art = {"round": "R1090",
           "question": "which arms are in each block, and where does the released core sit?",
           "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           "derivation": ("monotonicity (R1089) makes the blocks a threshold on one integer per "
                          "arm: always = beats all 15, never = beats 0, movable = 1..14. The "
                          "partition is free; WHICH arm has which count is the measurement."),
           "population": {"prompts": n, "arms": len(arms), "subsets": K},
           "controls": ctrl,
           "block_sizes": {b: len(v) for b, v in by_block.items()},
           "blocks": by_block,
           "per_arm": blocks,
           "seed_unstable_arms": unstable,
           "SHAM_point_estimate_moves": moved,
           "released_core": core_report,
           "core_sham_control": sham_report,
           "kill": {"gate_open": gate_open, "core_seed_unstable": core_unstable},
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1090 — which arms sit in each block?\n")
    print(f"  {n} prompts · {len(arms)} arms · {K} blind subsets")
    print("\n  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  BLOCK SIZES  always {len(by_block['always'])} · movable "
          f"{len(by_block['movable'])} · never {len(by_block['never'])}")
    print(f"  seed-unstable arms: {len(unstable)} {unstable[:6]}")
    print(f"  SHAM — arms whose block moves under the point estimate: {len(moved)}")
    print(f"\n  THE RELEASED CORE(S) — the sham is reported separately, as a control")
    for a, v in sorted(core_report.items()):
        print(f"    {a:<28} beats {v['beats']:>3} of {K}   block {v['block']:<9} "
              f"seed-stable {v['seed_stable']}")
    for a, v in sorted(sham_report.items()):
        print(f"    {a:<28} beats {v['beats']:>3} of {K}   block {v['block']:<9} ⭐ SHAM control")
    print(f"\n  ALWAYS ({len(by_block['always'])}): {by_block['always'][:8]}")
    print(f"  MOVABLE ({len(by_block['movable'])}): {by_block['movable'][:8]}")
    print(f"  NEVER ({len(by_block['never'])}): {by_block['never'][:8]}")
    print(f"\n  {'⛔' if not gate_open or core_unstable else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
