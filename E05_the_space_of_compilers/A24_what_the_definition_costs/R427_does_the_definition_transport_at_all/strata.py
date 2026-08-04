"""R427/strata -- is `generic` above chance AT ALL, or is +0.0179 a pooling artifact?

R427 reported `generic - chance = +0.0179` against an MDE of 0.0171 -- 1.05x, the thinnest possible
"clears chance". The specification curve then printed something I did not stop on:

    n = 2 interactions   generic ~0.507    (chance there is 0.500)
    n >= 3 interactions  generic ~0.308    (chance there is ~0.29)
    pooled `all`         generic  0.4374   (pooled chance 0.4194)

⛔ CHANCE IS NOT ONE NUMBER HERE. It is 1/n_responses, and n varies: 2, 3 or 4. Pooling strata with
   DIFFERENT chance levels can make an arm that sits exactly at chance in EVERY stratum appear above
   chance overall, purely from how the strata are weighted. That is a composition artifact, and the
   pooled +0.0179 is exactly the size where it would matter.

⭐ AND THE SAME ARITHMETIC MAKES THE ATTACK FREE. Every number here re-reads the arm already on disk.
   No GPU, no new judging, and it can only be run this cheaply because the estimand is stratifiable.

⛔ ARITHMETIC TRAP. `chance = 1/n` within a stratum is FORCED -- a derivation, not a measurement.
   What is NOT forced is whether `generic` sits on it in each stratum, nor whether the pooled effect
   survives once the strata are separated.

ESTIMAND        (A) ACC(generic) - chance WITHIN each response-count stratum, each against ITS OWN
                    chance level;
                (B) the same for LENGTH, which is the positive control: if the within-stratum test
                    cannot detect the length effect, a null for generic is silence rather than a
                    result;
                (C) whether the pooled +0.0179 survives stratification.

IDENTIFICATION  Exact per stratum. NOT identified: any stratum with < 2 conversations, reported
                UNVERIFIED rather than folded in.

SCOPE           population: the same 2,200 seeded conversations, split by response count · instrument:
                the committed `generic` arm, Qwen3.5-2B-Base · baseline: 1/n within each stratum ·
                regime: k=4, prompt-blind, mean aggregation (the curve showed all four agree).

WORLDS
  W-COMPOSITION   generic is within MDE of chance in EVERY stratum while LENGTH clears it in at least
                  one. Then the pooled +0.0179 is a weighting artifact, and `generic` does not beat
                  chance at all -- a strictly stronger negative than W-LENGTH.
  W-REAL          generic clears chance in at least one stratum. Then the pooled effect is real,
                  small, and located, and the stratum is named.
  W-BLIND         LENGTH does not clear chance in any stratum either. Then the within-stratum test
                  has no power and NOTHING here is readable -- a null from an instrument never shown
                  to return non-zero.

PREDICTION MATRIX
  W-COMPOSITION -> generic within MDE everywhere; length outside MDE somewhere
  W-REAL        -> generic outside MDE in >= 1 stratum, named
  W-BLIND       -> length within MDE everywhere

PRE-REGISTERED KILL -- conditional on the positive control, never on generic's numbers alone.
    if length clears chance in >= 1 stratum:      # the test is shown able to detect an effect
        generic clears in 0 strata -> W-COMPOSITION
        else                       -> W-REAL, strata named
    else: W-BLIND -- UNVERIFIED, exit 1.

CONTROLS
  LENGTH (+)   the positive control, and it is the whole reason a null here is admissible. It is a
               REAL arm on the REAL corpus, not a synthetic plant, so it cannot share an imagined
               blind spot with the thing under test.
  CHANCE       computed WITHIN each stratum as 1/n. Comparing a stratum's arm to the POOLED chance
               is the exact error this round exists to test for, so it is never done here.
  PAIRED       every contrast is paired per conversation before averaging, so the arm and its
               baseline are measured on the same units in the same stratum.
  NON-EMPTY    a stratum with < 2 conversations is UNVERIFIED for that stratum, never 0.0.

MULTIPLICITY    strata x 2 arms; every stratum printed with its n, including ones that answer nothing.
ARTIFACT        results/r427_strata.json with the source hash.

IMPOSSIBLE HERE
  why n varies across interactions -- a property of the release's collection, not measurable here.
  a prompt-specific core           -- unchanged.

EXIT
    0  the positive control fires and the strata are reported
    1  the positive control is blind -- UNVERIFIED
    2  the arm is absent -- never a silent pass
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
ZEFF = 1.959964 + 0.841621


def main() -> int:
    p = RES / "sat_transport_generic.npz"
    if not p.exists():
        print("  UNRUNNABLE: sat_transport_generic.npz absent. Exit 2, never 0."); return 2
    with np.load(p, allow_pickle=True) as d:
        meta, sat = [str(x) for x in d["meta"]], np.asarray(d["sat"], float)
        tgt = json.loads(str(d["targets"]))
    per = collections.defaultdict(lambda: collections.defaultdict(list))
    for m, v in zip(meta, sat):
        c, i, r, _j = m.split("|")
        per[(c, i)][r].append(v)

    print("R427 · strata — is `generic` above chance AT ALL, or is +0.0179 a pooling artifact?\n")
    print("  ⛔ CHANCE IS NOT ONE NUMBER HERE. It is 1/n_responses and n varies: 2, 3 or 4. Pooling")
    print("     strata with different chance levels can make an arm sitting exactly ON chance in")
    print("     every stratum look ABOVE chance overall, purely from how the strata are weighted.")
    print("     The pooled +0.0179 at 1.05x its MDE is exactly the size where that matters.\n")

    S = collections.defaultdict(lambda: collections.defaultdict(lambda: ([], [], [])))
    for t in tgt:
        ch = [r["id"] for r in t["resp"] if r["chosen"]]
        if len(ch) != 1:
            continue
        row = per.get((t["conv"], t["inter"]))
        if not row:
            continue
        n = len(t["resp"])
        scored = {r: float(np.mean(v)) for r, v in row.items()}
        top = max(scored.values())
        g = 1.0 if sorted([r for r in scored if scored[r] == top])[0] == ch[0] else 0.0
        l = 1.0 if max(t["resp"], key=lambda r: (r["len"], r["id"]))["id"] == ch[0] else 0.0
        a, b, c_ = S[n][t["conv"]]
        a.append(g); b.append(l); c_.append(1.0 / n)

    def contrast(byconv, idx):
        ks = list(byconv)
        d = np.array([np.mean(byconv[k][idx]) - np.mean(byconv[k][2]) for k in ks], float)
        if len(d) < 2:
            return None
        return float(d.mean()), float(ZEFF * d.std(ddof=1) / np.sqrt(len(d))), len(d)

    print(f"    {'n_resp':<8} {'chance':>7} {'generic':>8} {'g−chance':>9} {'MDE':>8} "
          f"{'length':>8} {'l−chance':>9} {'MDE':>8} {'convs':>7}")
    rows, g_hits, l_hits, unver = {}, [], [], []
    for n in sorted(S):
        byconv = S[n]
        gm = float(np.mean([np.mean(v[0]) for v in byconv.values()]))
        lm = float(np.mean([np.mean(v[1]) for v in byconv.values()]))
        gc, lc = contrast(byconv, 0), contrast(byconv, 1)
        if gc is None or lc is None:
            unver.append(n)
            print(f"    {n:<8} {1/n:>7.4f} {'—':>8} {'—':>9} {'—':>8} {'—':>8} {'—':>9} "
                  f"{'—':>8} {len(byconv):>7}   UNVERIFIED (<2 convs)")
            continue
        rows[n] = dict(chance=1/n, generic=gm, g_diff=gc[0], g_mde=gc[1],
                       length=lm, l_diff=lc[0], l_mde=lc[1], convs=gc[2])
        if gc[0] > gc[1]:
            g_hits.append(n)
        if lc[0] > lc[1]:
            l_hits.append(n)
        print(f"    {n:<8} {1/n:>7.4f} {gm:>8.4f} {gc[0]:>+9.4f} {gc[1]:>8.4f} "
              f"{lm:>8.4f} {lc[0]:>+9.4f} {lc[1]:>8.4f} {gc[2]:>7,}"
              + ("   ⭐ generic clears" if gc[0] > gc[1] else ""))

    print(f"\n  CONTROLS")
    print(f"    LENGTH (+)  clears chance within strata: {l_hits or 'NONE'}   "
          f"{'PASS' if l_hits else 'FAIL — the within-stratum test has no power'}")
    print(f"                a REAL arm on the REAL corpus, not a synthetic plant, so it cannot share")
    print(f"                an imagined blind spot with the thing under test")
    print(f"    CHANCE      computed WITHIN each stratum as 1/n. Comparing a stratum's arm to the")
    print(f"                POOLED chance is the exact error this round exists to test for.")
    print(f"    ⛔ `chance = 1/n` IS A DERIVATION, forced by the design. What is not forced is")
    print(f"       whether generic sits on it.")
    print(f"\n  MULTIPLICITY  strata tested {len(rows)} · generic clears in {len(g_hits)} · "
          f"length clears in {len(l_hits)} · unverifiable {len(unver)}")

    print()
    if not l_hits:
        v = "W_BLIND"
        print(f"  W-BLIND — LENGTH does not clear chance in any stratum either, so the within-stratum")
        print(f"  test has no power and nothing here is readable. A null from an instrument never")
        print(f"  shown to return non-zero is silence. UNVERIFIED. Exit 1.")
    elif not g_hits:
        v = "W_COMPOSITION"
        print(f"  W-COMPOSITION — generic is within its MDE of chance in ALL {len(rows)} strata, while")
        print(f"  LENGTH clears chance in {l_hits}. So the pooled `+0.0179 clears chance` is a")
        print(f"  WEIGHTING ARTIFACT: an arm sitting on chance in every stratum looked above chance")
        print(f"  once the strata were mixed.")
        print(f"  ⛔ THAT IS STRICTLY STRONGER THAN W-LENGTH. R427 said generic beats chance and loses")
        print(f"     to the shortcut. This says it does not beat chance AT ALL, and the one positive")
        print(f"     number in the whole round dissolves.")
    else:
        v = "W_REAL"
        print(f"  W-REAL — generic clears chance in strata {g_hits}. The pooled effect is real, small,")
        print(f"  and LOCATED rather than an artifact of mixing.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               strata={str(k): v2 for k, v2 in rows.items()}, generic_clears=g_hits,
               length_clears=l_hits, unverifiable=unver, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_strata.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if l_hits else 1


if __name__ == "__main__":
    sys.exit(main())
