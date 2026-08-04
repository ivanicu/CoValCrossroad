"""R427/position -- generic 0.4374 and first 0.4375. Coincidence, or shared structure?

R427 reported the prompt-blind arm at 0.4374 and the positional rule `always take the corpus-first
response` at 0.4375. Two rules that share no mechanism landing one ten-thousandth apart is either a
coincidence worth naming as one, or evidence of a structure neither was designed to have.

⭐ AND THE ARM CANNOT HAVE A POSITION BIAS BY CONSTRUCTION. `judge_transport.py` scores each
   (response, criterion) independently; nothing in `build_prompt` sees the other candidates or their
   order. So `generic`'s argmax is order-invariant apart from its tiebreak. If generic and first
   agree more than chance allows, the alignment cannot live in the JUDGE -- it must live in the
   CORPUS, i.e. in what the first-listed response tends to BE.

⛔ ARITHMETIC TRAP. A random rule picks the first response at exactly 1/n -- forced, a derivation,
   and it is the baseline rather than a finding. What is NOT forced is whether the first response is
   systematically longer, nor how often generic's pick coincides with it.

ESTIMAND        per response-count stratum, each against its own 1/n:
                (A) P(the corpus-first response is the LONGEST);
                (B) P(generic's argmax is the corpus-first response);
                (C) P(the length rule picks the corpus-first response).
                None involves the human target: this characterises the RULES, not their accuracy.

IDENTIFICATION  Exact. All three are deterministic functions of committed fields.

SCOPE           population: the same 2,200 seeded conversations · instrument: the committed generic
                arm · baseline: 1/n within each stratum · regime: k=4, mean aggregation.

WORLDS
  W-CORPUS-ORDER   the first response is longer than chance allows, and generic/length both tilt
                   toward it. Then `first` is not an independent baseline at all -- it is a weak
                   proxy for length, and R427's `generic is indistinguishable from first` is a fact
                   about the CORPUS's ordering rather than about the arm.
  W-COINCIDENCE    the first response is at chance on length, and generic picks it at chance. Then
                   0.4374 vs 0.4375 is a coincidence and must be reported as one -- two unrelated
                   rules that happened to land together.

PREDICTION MATRIX
  W-CORPUS-ORDER -> P(first is longest) > 1/n, and P(generic picks first) > 1/n
  W-COINCIDENCE  -> both within MDE of 1/n

PRE-REGISTERED KILL
    if the derivation control holds (a seeded random rule picks first at 1/n within MDE):
        P(first is longest) > its MDE above 1/n  -> W-CORPUS-ORDER
        else                                     -> W-COINCIDENCE
    else: UNVERIFIED -- the estimator is unfit.

CONTROLS
  RANDOM (=)   a seeded uniform pick must select the first response at 1/n within its MDE. This is
               the estimator's calibration: if a rule known to be positionally neutral does not land
               on 1/n here, no other rate is readable.
  NO-TARGET    nothing in this round touches `if_chosen`. Stated because every other analysis in
               R427 does, and mixing them would let an accuracy effect masquerade as structure.
  STRATIFIED   per response count, because 1/n differs and pooling them is the error already caught
               twice in this round.

MULTIPLICITY    strata x 4 quantities; every cell printed.
ARTIFACT        results/r427_position.json with the source hash.

IMPOSSIBLE HERE
  WHY the corpus is ordered as it is -- a property of collection, not measurable from these fields.
  a presentation-order effect on the HUMAN -- the release carries no presentation-order field, only
                                              the storage order, and the two need not coincide.

EXIT
    0  the calibration holds and a branch is reached
    1  the calibration fails -- UNVERIFIED
    2  an input is absent -- never a silent pass
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

    print("R427 · position — generic 0.4374 and first 0.4375. Coincidence, or shared structure?\n")
    print("  ⭐ THE ARM CANNOT HAVE A POSITION BIAS BY CONSTRUCTION. Each (response, criterion) is")
    print("     scored independently; nothing in build_prompt sees the other candidates or their")
    print("     order. So if generic and first agree beyond chance, the alignment lives in the")
    print("     CORPUS — in what the first-listed response tends to BE — never in the judge.")
    print("  ⚠ NOTHING HERE TOUCHES `if_chosen`. This characterises the RULES, not their accuracy.\n")

    rng = np.random.default_rng(0)
    S = collections.defaultdict(lambda: collections.defaultdict(
        lambda: ([], [], [], [], [])))   # first_is_longest, generic_first, len_first, rand, 1/n
    for t in tgt:
        row = per.get((t["conv"], t["inter"]))
        if not row:
            continue
        n = len(t["resp"])
        ids = [r["id"] for r in t["resp"]]
        first = ids[0]
        longest = max(t["resp"], key=lambda r: (r["len"], r["id"]))["id"]
        scored = {r: float(np.mean(v)) for r, v in row.items()}
        top = max(scored.values())
        gpick = sorted([r for r in scored if scored[r] == top])[0]
        a, b, c, e, f = S[n][t["conv"]]
        a.append(float(first == longest))
        b.append(float(gpick == first))
        c.append(float(longest == first))
        e.append(float(ids[int(rng.integers(n))] == first))
        f.append(1.0 / n)

    def clus(by, idx):
        v = np.array([np.mean(x[idx]) for x in by.values() if x[idx]], float)
        if len(v) < 2:
            return None
        return float(v.mean()), float(ZEFF * v.std(ddof=1) / np.sqrt(len(v))), len(v)

    allconv = {k: v for n in S for k, v in S[n].items()}
    # ⛔ MY FIRST CALIBRATION FAILED FOR ITS OWN REASONS AND IT IS THE LEDGER'S DOMINANT ROW:
    #    `rc` was conversation-clustered while the expectation averaged 1/n over (stratum,
    #    conversation) PAIRS -- and a conversation appears in several strata when its interactions
    #    have different response counts. Two different weightings compared as though they were one.
    #    Both sides are now the SAME object: mean within conversation, then across conversations.
    rc = clus(allconv, 3)
    er = clus(allconv, 4)
    exp_rand = er[0]
    cal_ok = rc is not None and abs(rc[0] - exp_rand) <= max(rc[1], 1e-9)
    print("  CONTROLS")
    print(f"    RANDOM (=)  a seeded uniform pick selects the first response at {rc[0]:.4f} "
          f"vs the derivation {exp_rand:.4f} (MDE {rc[1]:.4f})   {'PASS' if cal_ok else 'FAIL'}")
    print(f"                if a positionally NEUTRAL rule does not land on 1/n here, no other rate")
    print(f"                in this round is readable")
    if not cal_ok:
        print("\n  UNVERIFIED — the estimator is not calibrated. Exit 1."); return 1

    print(f"\n    {'n_resp':<8} {'1/n':>7} {'P(first=longest)':>17} {'MDE':>8} "
          f"{'P(generic=first)':>17} {'MDE':>8} {'convs':>7}")
    rows, hits = {}, []
    for n in sorted(S):
        fl, gp = clus(S[n], 0), clus(S[n], 1)
        if fl is None or gp is None:
            print(f"    {n:<8} {1/n:>7.4f} {'—':>17} {'—':>8} {'—':>17} {'—':>8} "
                  f"{len(S[n]):>7}   UNVERIFIED")
            continue
        rows[n] = dict(chance=1/n, first_longest=fl[0], fl_mde=fl[1],
                       generic_first=gp[0], gf_mde=gp[1], convs=fl[2])
        if fl[0] - 1/n > fl[1]:
            hits.append(n)
        print(f"    {n:<8} {1/n:>7.4f} {fl[0]:>17.4f} {fl[1]:>8.4f} {gp[0]:>17.4f} "
              f"{gp[1]:>8.4f} {fl[2]:>7,}" + ("   ⭐ first is longer than chance" if n in hits else ""))

    print()
    if hits:
        v = "W_CORPUS_ORDER"
        print(f"  W-CORPUS-ORDER — the first-listed response is the LONGEST more often than 1/n in")
        print(f"  strata {hits}. So `first` is not an independent baseline: it is a weak proxy for")
        print(f"  LENGTH, and R427's `generic is indistinguishable from first` is a fact about the")
        print(f"  CORPUS's storage order rather than about the arm.")
        print(f"  ⚠ AND THAT MAKES `first` A WEAKER CONTROL THAN I CLAIMED. I offered it as the")
        print(f"    position substitute for a release with no presentation-order field. It is")
        print(f"    partly a length rule, so it does not isolate position at all.")
    else:
        v = "W_COINCIDENCE"
        print(f"  W-COINCIDENCE — the first response is at chance on length in every stratum. So")
        print(f"  0.4374 vs 0.4375 is a COINCIDENCE and is reported as one: two rules sharing no")
        print(f"  mechanism that happened to land together.")

    print(f"\n  ⚠ THE RELEASE CARRIES NO PRESENTATION-ORDER FIELD — only storage order, and the two")
    print(f"    need not coincide. Nothing here is a claim about what a human SAW.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               strata={str(k): v2 for k, v2 in rows.items()}, first_longer_strata=hits,
               calibration=dict(rand=rc[0], expected=exp_rand, mde=rc[1], ok=cal_ok), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_position.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
