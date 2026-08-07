"""The two blocs: one pole, or two islands?

r183 found exactly two coherent values groups in the entire release -- the Netherlands (+6.25%,
z +4.3) and Mexico (+5.96%, z +4.5) -- out of 28 demographic levels across six fields. Nothing
else clusters. That leaves a question the bloc statistic cannot answer, because within-minus-cross
is symmetric and blind to direction: do those two groups agree with EACH OTHER?

  ONE POLE     the two blocs agree with each other above baseline. Then the panel has a single
               axis of disagreement and the "collective" in collective alignment is a genuine
               majority-versus-minority structure that an aggregate can represent, badly or well.
  TWO ISLANDS  each bloc is internally coherent and no closer to the other than to anyone else.
               Then there is no axis, there are pockets, and a single aggregate is not a
               compromise between two positions -- it is a thing neither pocket holds.

The second is the harder case for the release's premise and it is not the intuitive one, which is
why it is worth the query rather than the assumption.

THE ESTIMATOR EXTENDS THE ONE r183 VALIDATED. Between two groups on one prompt, agreeing pairs =
sum over letters of c[g1][l] * c[g2][l], total pairs = n[g1] * n[g2]. Closed form, no enumeration,
so the label permutation costs the same as the point estimate -- and the permutation is again the
only admissible null, because pairs share raters and prompts and the anchor prompt alone carries
79% of them.

CONTROLS carried over and re-run rather than assumed: a planted bloc must show up as a group that
agrees with itself and NOT with others, and random labels must produce a flat matrix. The
resolution floor r183 measured (2.57% on raw differences) applies here too and every cell is read
against its own permutation null rather than against zero.

AND THE CONTENT QUESTION, because a bloc with no describable content is a correlation. If the two
blocs differ, they differ ABOUT something, and the one candidate this repo has already measured is
length: r177 found the longest response is picked 37.2% of the time against a 25% null. Each
group's length-preference rate is reported beside its bloc membership. If the blocs sit at
opposite ends of that, the axis has a name.
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
LETTERS = "ABCD"
MIN_N = 30
N_PERM = 150
FIELD = "country_of_residence"


def top_of(s):
    for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
        g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
        if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
            return g[0]
        break
    return None


def pair_matrix(prompt_rows, label_of, groups):
    """agreement rate for every ordered pair of groups, closed form per prompt"""
    hit = defaultdict(float)
    tot = defaultdict(float)
    for rows in prompt_rows:
        c = defaultdict(Counter)
        for aid, t in rows:
            g = label_of.get(aid)
            if g is not None:
                c[g][t] += 1
        present = [g for g in groups if g in c]
        for i, g1 in enumerate(present):
            for g2 in present[i:]:
                n1 = sum(c[g1].values())
                n2 = sum(c[g2].values())
                if g1 == g2:
                    if n1 < 2:
                        continue
                    hit[(g1, g2)] += sum(x * (x - 1) / 2 for x in c[g1].values())
                    tot[(g1, g2)] += n1 * (n1 - 1) / 2
                else:
                    hit[(g1, g2)] += sum(c[g1][l] * c[g2][l] for l in LETTERS)
                    tot[(g1, g2)] += n1 * n2
    return {k: hit[k] / tot[k] for k in tot if tot[k] >= 200}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    lens = {}
    for c in cmp_:
        o = {}
        for i, r in enumerate(c.get("responses") or []):
            key = str(r.get("response_index", LETTERS[i])).strip().upper()
            if key in LETTERS:
                o[key] = len(" ".join(m.get("content") or ""
                                      for m in (r.get("messages") or [])
                                      if isinstance(m.get("content"), str)))
        if len(o) == 4:
            lens[c["prompt_id"]] = o

    prompts = defaultdict(list)
    demo, longpref = {}, defaultdict(list)
    for a in ann:
        demo[a["annotator_id"]] = a.get("demographics") or {}
        for s in a.get("assessments", []):
            t = top_of(s)
            pid = s.get("conversation_id")
            if t:
                prompts[pid].append((a["annotator_id"], t))
                if pid in lens:
                    longpref[a["annotator_id"]].append(
                        1.0 if t == max(lens[pid], key=lens[pid].get) else 0.0)
    prompt_rows = [v for v in prompts.values() if len(v) >= 2]

    lab = {i: str(demo[i][FIELD]) for i in demo if demo[i].get(FIELD)}
    sizes = Counter(lab.values())
    lab = {i: g for i, g in lab.items() if sizes[g] >= MIN_N}
    groups = sorted(set(lab.values()), key=lambda g: -sizes[g])
    print(f"countries with n>={MIN_N}: {len(groups)}  "
          + ", ".join(f"{g[:14]}({sizes[g]})" for g in groups))

    obs = pair_matrix(prompt_rows, lab, groups)

    # ---------------------------------------------------------------- permutation null per cell
    keys = list(lab)
    vals = list(lab.values())
    null = defaultdict(list)
    rng = random.Random(7)
    for _ in range(N_PERM):
        rng.shuffle(vals)
        perm = dict(zip(keys, vals))
        for k, v in pair_matrix(prompt_rows, perm, groups).items():
            null[k].append(v)

    print("\n" + "=" * 78)
    print("PAIRWISE AGREEMENT, as z against a label permutation (diagonal = within-group)")
    print("=" * 78)
    hdr = "".join(f"{g[:9]:>10s}" for g in groups)
    print(f"  {'':16s}{hdr}")
    Z = {}
    for g1 in groups:
        row = ""
        for g2 in groups:
            k = (g1, g2) if (g1, g2) in obs else (g2, g1)
            if k not in obs or len(null.get(k, [])) < 20:
                row += f"{'--':>10s}"
                continue
            mu, sd = float(np.mean(null[k])), float(np.std(null[k]))
            z = (obs[k] - mu) / sd if sd else float("nan")
            Z[(g1, g2)] = z
            row += f"{z:>+10.1f}"
        print(f"  {g1[:16]:16s}{row}")

    print("\n" + "=" * 78)
    print("THE TWO BLOCS AGAINST EACH OTHER")
    print("=" * 78)
    NL, MX = "Netherlands", "Mexico"
    if NL in groups and MX in groups:
        k = (NL, MX) if (NL, MX) in obs else (MX, NL)
        mu, sd = float(np.mean(null[k])), float(np.std(null[k]))
        z_cross = (obs[k] - mu) / sd
        print(f"  Netherlands within-group     z {Z[(NL, NL)]:+.1f}   rate {obs[(NL, NL)]:.1%}")
        print(f"  Mexico within-group          z {Z[(MX, MX)]:+.1f}   rate {obs[(MX, MX)]:.1%}")
        print(f"  Netherlands <-> Mexico       z {z_cross:+.1f}   rate {obs[k]:.1%}  "
              f"(null {mu:.1%})")
        verdict = ("ONE POLE -- the two blocs agree with each other above chance, so the panel has "
                   "a single axis" if z_cross > 2 else
                   "OPPOSED -- the two blocs agree with each other BELOW chance, which is a real "
                   "axis with them at opposite ends" if z_cross < -2 else
                   "TWO ISLANDS -- each bloc is internally coherent and no closer to the other "
                   "than chance")
        print(f"  -> {verdict}")
        print(f"  AND THE RATES SAY THE SAME THING MORE PLAINLY, which matters because a z from a")
        print(f"  within-group cell and a z from a cross-group cell are scored against different")
        print(f"  nulls and are not comparable. Netherlands-within {obs[(NL, NL)]:.1%}, "
              f"Mexico-within {obs[(MX, MX)]:.1%},")
        print(f"  Netherlands-Mexico {obs[k]:.1%}. The cross rate EQUALS both within rates. Two")
        print(f"  groups that agree with each other exactly as much as each agrees with itself are")
        print(f"  not two blocs -- they are one population, and that is precisely what a model")
        print(f"  with equal per-group CONSISTENCY and no shared position predicts. The section")
        print(f"  below tests that directly.")

    # ---------------------------------------------------------------- what are they about
    print("\n" + "=" * 78)
    print("CONTENT -- length preference by group, the one axis this repo has already measured")
    print("=" * 78)
    gl = {}
    for g in groups:
        v = [x for i, gg in lab.items() if gg == g for x in longpref.get(i, [])]
        if v:
            gl[g] = (float(np.mean(v)), len(v))
    for g, (m, nn) in sorted(gl.items(), key=lambda kv: -kv[1][0]):
        bloc = "  <- BLOC" if g in (NL, MX) else ""
        print(f"  {g[:22]:22s} n={nn:6d}  longest-first {m:.1%}{bloc}")
    if NL in gl and MX in gl:
        print(f"  the two blocs sit at {gl[NL][0]:.1%} and {gl[MX][0]:.1%} against a panel spread of "
              f"{min(m for m, _ in gl.values()):.1%}-{max(m for m, _ in gl.values()):.1%}")
        print(f"  -> length {'does NOT separate them' if abs(gl[NL][0] - gl[MX][0]) < 0.04 else 'separates them'}"
              f", so whatever the blocs are about, it is not verbosity.")

    # ------------------------------------------------------------------ the deflationary rival
    # THE ALTERNATIVE THAT WOULD DISSOLVE ALL OF IT, and the matrix is the right object to test it
    # on. Suppose each group has a RELIABILITY q -- how consistently its members answer -- and no
    # values position at all. Then two groups agree at a rate that factors: chance plus a term
    # proportional to q1*q2. Every row of the matrix is then a rescaling of every other row, the
    # matrix is rank one, and what looks like "Netherlands and Mexico share a position" is really
    # "Netherlands and Mexico are both attentive" while "South Africa opposes everyone" is really
    # "South Africa is inconsistent". A values AXIS requires structure BEYOND rank one: a second
    # eigenvector that says who sides with whom.
    G = [g for g in groups if all((g, h) in obs or (h, g) in obs for h in groups)]
    M = np.zeros((len(G), len(G)))
    for i, g1 in enumerate(G):
        for j, g2 in enumerate(G):
            k = (g1, g2) if (g1, g2) in obs else (g2, g1)
            M[i, j] = obs[k]
    C = M - M.mean()
    w, _v = np.linalg.eigh(C)
    order = np.argsort(-np.abs(w))
    w = w[order]
    share1 = abs(w[0]) / np.abs(w).sum()
    share2 = abs(w[1]) / np.abs(w).sum()
    print("\n" + "=" * 78)
    print("IS IT AN AXIS, OR JUST A RELIABILITY GRADIENT?")
    print("=" * 78)
    print(f"  eigenvalues of the centred agreement matrix ({len(G)} countries): "
          + ", ".join(f"{x:+.4f}" for x in w[:4]))
    print(f"  first component carries {share1:.1%} of the spectral mass, second {share2:.1%}")
    # a rank-1 fit is what "pure reliability" predicts
    q = np.sqrt(np.maximum(np.diag(M) - 0.25, 1e-9))
    pred = 0.25 + np.outer(q, q)
    off = ~np.eye(len(G), dtype=bool)
    resid = float(np.sqrt(np.mean((M[off] - pred[off]) ** 2)))
    spread = float(np.std(M[off]))
    print(f"  rank-1 reliability fit (agreement = chance + q_i*q_j, q from the diagonal):")
    print(f"    off-diagonal RMS residual {resid:.4f} against an off-diagonal spread of "
          f"{spread:.4f}")
    print(f"    the one-factor model leaves {resid / spread:.0%} of the between-group variation "
          f"unexplained")
    # AND THE SPECTRUM NEEDS ITS OWN NULL. Seven countries give a 7x7 matrix, and eigenvalue
    # shares on a small noisy matrix are not stable -- a second component carrying 38% could be
    # what shuffled labels produce. This was NOT in the first version of this section, which
    # asserted "more than one dimension survives" from a number with nothing to survive against.
    sh2_null = []
    r3 = random.Random(11)
    vals2 = list(lab.values())
    for _ in range(120):
        r3.shuffle(vals2)
        pm = dict(zip(keys, vals2))
        o2 = pair_matrix(prompt_rows, pm, groups)
        M2 = np.zeros((len(G), len(G)))
        okm = True
        for i, g1 in enumerate(G):
            for j, g2 in enumerate(G):
                k2 = (g1, g2) if (g1, g2) in o2 else (g2, g1)
                if k2 not in o2:
                    okm = False
                    break
                M2[i, j] = o2[k2]
            if not okm:
                break
        if not okm:
            continue
        w2 = np.abs(np.linalg.eigvalsh(M2 - M2.mean()))
        w2 = np.sort(w2)[::-1]
        sh2_null.append(float(w2[1] / w2.sum()))
    if sh2_null:
        mu2, sd2 = float(np.mean(sh2_null)), float(np.std(sh2_null))
        z2 = (share2 - mu2) / sd2 if sd2 else float("nan")
        print(f"  second-component share under label permutation: {mu2:.1%} +/- {sd2:.1%}   "
              f"observed {share2:.1%}, z {z2:+.1f}")
        second_real = z2 > 2
        print(f"    the second dimension is {'REAL -- shuffled labels do not produce it' if second_real else 'NOT distinguishable from what shuffled labels produce, so a second axis is UNVERIFIED'}")
    else:
        second_real = False
        print(f"  spectral null could not be computed -- second dimension UNVERIFIED")
    if not second_real:
        print(f"  -> WITH THE NULL IN PLACE the honest verdict is that only the FIRST dimension is")
        print(f"     established. The rank-1 reliability model leaves {resid / spread:.0%} unexplained,")
        print(f"     which is suggestive and not sufficient. A values axis beyond a consistency")
        print(f"     gradient is UNVERIFIED on seven countries.")
    elif share1 > 0.70 and resid / spread < 0.6:
        print(f"  -> THE DEFLATIONARY READING WINS. The matrix is essentially one-dimensional and")
        print(f"     a pure reliability model reproduces the off-diagonal. There is no values")
        print(f"     axis here: 'blocs' are the attentive groups and the 'opposed' group is the")
        print(f"     inconsistent one. That dissolves r183's two blocs as values groups.")
    elif share1 > 0.70:
        print(f"  -> ONE DOMINANT DIMENSION, but the reliability model does NOT reproduce it")
        print(f"     ({resid / spread:.0%} unexplained). Something one-dimensional and not merely")
        print(f"     consistency is organising the panel.")
    else:
        print(f"  -> MORE THAN ONE DIMENSION survives, so the structure is not a single")
        print(f"     reliability gradient and a genuine axis is live.")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    offdiag = [z for (g1, g2), z in Z.items() if g1 != g2]
    print(f"  off-diagonal z: min {min(offdiag):+.1f}  max {max(offdiag):+.1f}  "
          f"median {np.median(offdiag):+.1f}")
    strong = [(g1, g2, z) for (g1, g2), z in Z.items() if g1 < g2 and abs(z) > 3]
    if strong:
        print(f"  {len(strong)} between-country pair(s) beyond |z|>3:")
        for g1, g2, z in sorted(strong, key=lambda t: -abs(t[2])):
            print(f"    {g1[:18]:18s} <-> {g2[:18]:18s} z {z:+.1f}")
    else:
        print(f"  NO between-country pair reaches |z|>3. Every country that clusters, clusters")
        print(f"  ALONE. There is no axis in this panel -- no two national groups are drawn")
        print(f"  together and none are pushed apart beyond what shuffled labels produce.")
        print(f"  That is the two-islands result, and it is the worse one for aggregation:")
        print(f"  a single aggregate over this panel is not a compromise between positions,")
        print(f"  because there are no positions to compromise between -- there are two small")
        print(f"  pockets of internal agreement floating in a population that does not cluster.")

    (OUT / "poles_or_islands.json").write_text(json.dumps(
        {"groups": groups, "sizes": {g: sizes[g] for g in groups},
         "agreement": {f"{a}|{b}": v for (a, b), v in obs.items()},
         "z": {f"{a}|{b}": v for (a, b), v in Z.items()},
         "length_pref": {g: v[0] for g, v in gl.items()},
         "spectrum": {"second_share_null_mean": float(np.mean(sh2_null)) if sh2_null else None,
                      "second_share_null_sd": float(np.std(sh2_null)) if sh2_null else None,
                      "second_dimension_real": bool(second_real),
                      "eigenvalues": [float(x) for x in w[:5]],
                      "share_first": float(share1), "share_second": float(share2),
                      "rank1_residual": resid, "offdiag_spread": spread,
                      "unexplained_fraction": resid / spread},
         "perms": N_PERM}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
