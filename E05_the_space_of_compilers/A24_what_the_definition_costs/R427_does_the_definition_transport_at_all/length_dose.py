"""R427/length_dose -- where length cannot help, does the core still carry anything?

The target is length-loaded at tau +0.2113 (R427/target_length). That reframes every accuracy in this
round, but it does not answer the question it raises: **does the judged core carry ANY signal that is
not length?**

⛔ THE OBVIOUS TEST IS THE FORBIDDEN ONE. "Accuracy among interactions where the longest response was
   NOT chosen" conditions on the OUTCOME -- Oldham's error, a named row in this campaign's ledger,
   and it manufactures opposite gradients from the same data. It is not run here.

⭐ THE ADMISSIBLE VERSION STRATIFIES ON A PRE-OUTCOME COVARIATE: how DISPERSED the response lengths
   are within an interaction. Where every candidate is about the same length, the length heuristic has
   no purchase by construction -- and any accuracy the core retains there cannot be a length effect.
   Dispersion is a property of the responses, computable before any target is consulted, so nothing
   is conditioned on what the human picked.

⛔ ARITHMETIC TRAP. That the length rule loses its edge as dispersion falls is FORCED as dispersion
   goes to zero -- at exactly equal lengths the rule becomes an arbitrary tiebreak. That forcing is
   what makes it a usable POSITIVE CONTROL on the stratifier and a worthless finding. What is NOT
   forced is whether GENERIC's edge survives where length's does not.

ESTIMAND        within quartiles of within-interaction length dispersion:
                (A) ACC(generic) - chance and (B) ACC(length) - chance, each against the stratum's
                own chance, with the conversation as the unit;
                (C) whether generic retains an edge in the bin where length's has collapsed.

IDENTIFICATION  Exact per bin. NOT identified: a causal effect of length -- no intervention on
                response length exists. This is a nuisance-matched comparison, not an ablation.

SCOPE           population: the same 2,200 seeded conversations · instrument: the committed generic
                arm · baseline: 1/n within each bin · regime: k=4, prompt-blind, mean aggregation ·
                stratifier: log(max length / min length) within an interaction, quartiles.

WORLDS
  W-BEYOND-LENGTH   in the lowest-dispersion bin, LENGTH is at chance and GENERIC is above it. Then
                    the core carries signal that is not a length effect, however small.
  W-ONLY-LENGTH     generic and length collapse together as dispersion falls. Then what the core
                    tracks on this corpus IS length, and clause ②'s comparator has no independent
                    content here.
  W-BLIND           length does NOT decline with dispersion. Then the stratifier does not do what it
                    claims, and no bin is readable.

PREDICTION MATRIX
  W-BEYOND-LENGTH -> length's edge falls to within MDE in bin 1; generic's does not
  W-ONLY-LENGTH   -> both fall to within MDE in bin 1
  W-BLIND         -> length's edge does not decline monotonically across bins

PRE-REGISTERED KILL -- conditional on the stratifier being shown to work.
    if length's edge in bin 1 < length's edge in bin 4 (the stratifier bites):
        generic's edge in bin 1 > its MDE  -> W-BEYOND-LENGTH
        else                               -> W-ONLY-LENGTH
    else: W-BLIND -- UNVERIFIED, exit 1.

CONTROLS
  STRATIFIER (+)  LENGTH's edge must DECLINE from the highest-dispersion bin to the lowest. That is
                  the positive control on the stratifier itself: if the binning does not weaken the
                  rule it is built to weaken, it is not measuring dispersion.
  CHANCE          computed WITHIN each bin as mean(1/n), because the bins need not be balanced on
                  response count -- and comparing a bin's arm to a POOLED chance is the error the
                  strata round already caught once in this same round.
  NOT-OUTCOME     the stratifier is a function of the RESPONSES only. Stated explicitly because the
                  tempting version of this test conditions on whether the longest was chosen, which
                  is Oldham's error.
  NON-EMPTY       a bin with < 2 conversations is UNVERIFIED for that bin, never 0.0.

MULTIPLICITY    4 bins x 2 arms; every bin printed with its n and its own chance.
ARTIFACT        results/r427_length_dose.json with the source hash.

IMPOSSIBLE HERE
  a causal effect of length -- no intervention on response length is available.
  a prompt-specific core    -- unchanged.

EXIT
    0  the stratifier bites and the bins are reported
    1  the stratifier does not bite -- UNVERIFIED
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

    print("R427 · length_dose — where length cannot help, does the core still carry anything?\n")
    print("  ⛔ THE OBVIOUS TEST IS THE FORBIDDEN ONE. `accuracy where the longest was NOT chosen`")
    print("     conditions on the OUTCOME — Oldham's error, a named row in this ledger. Not run.")
    print("  ⭐ THE ADMISSIBLE VERSION stratifies on log(max len / min len) WITHIN an interaction:")
    print("     a property of the RESPONSES, computable before the target is consulted.\n")

    recs = []
    for t in tgt:
        ch = [r["id"] for r in t["resp"] if r["chosen"]]
        row = per.get((t["conv"], t["inter"]))
        if len(ch) != 1 or not row:
            continue
        lens = [max(1, r["len"]) for r in t["resp"]]
        disp = float(np.log(max(lens) / min(lens)))
        scored = {r: float(np.mean(v)) for r, v in row.items()}
        top = max(scored.values())
        g = 1.0 if sorted([r for r in scored if scored[r] == top])[0] == ch[0] else 0.0
        l = 1.0 if max(t["resp"], key=lambda r: (r["len"], r["id"]))["id"] == ch[0] else 0.0
        recs.append((t["conv"], disp, g, l, 1.0 / len(t["resp"])))
    if len(recs) < 8:
        print("  UNRUNNABLE: too few interactions. Exit 2."); return 2

    qs = np.quantile([r[1] for r in recs], [0.25, 0.50, 0.75])
    bins = collections.defaultdict(lambda: collections.defaultdict(lambda: ([], [], [])))
    for conv, disp, g, l, c in recs:
        b = int(np.searchsorted(qs, disp, side="right"))
        a_, b_, c_ = bins[b][conv]
        a_.append(g); b_.append(l); c_.append(c)

    def edge(byconv, idx):
        ks = list(byconv)
        d = np.array([np.mean(byconv[k][idx]) - np.mean(byconv[k][2]) for k in ks], float)
        if len(d) < 2:
            return None
        return float(d.mean()), float(ZEFF * d.std(ddof=1) / np.sqrt(len(d))), len(d)

    print(f"    {'bin':<5} {'log(max/min) range':<22} {'chance':>7} {'g−chance':>9} {'MDE':>8} "
          f"{'l−chance':>9} {'MDE':>8} {'convs':>7}")
    lo = ["min"] + [f"{q:.3f}" for q in qs]
    hi = [f"{q:.3f}" for q in qs] + ["max"]
    rows, unver = {}, []
    for b in sorted(bins):
        ge, le = edge(bins[b], 0), edge(bins[b], 1)
        ch = float(np.mean([np.mean(v[2]) for v in bins[b].values()]))
        if ge is None or le is None:
            unver.append(b)
            print(f"    {b:<5} {lo[b] + ' … ' + hi[b]:<22} {ch:>7.4f} {'—':>9} {'—':>8} "
                  f"{'—':>9} {'—':>8} {len(bins[b]):>7}   UNVERIFIED")
            continue
        rows[b] = dict(chance=ch, g=ge[0], g_mde=ge[1], l=le[0], l_mde=le[1], convs=ge[2],
                       range=[lo[b], hi[b]])
        print(f"    {b:<5} {lo[b] + ' … ' + hi[b]:<22} {ch:>7.4f} {ge[0]:>+9.4f} {ge[1]:>8.4f} "
              f"{le[0]:>+9.4f} {le[1]:>8.4f} {ge[2]:>7,}")

    if 0 not in rows or max(rows) not in rows:
        print("\n  UNVERIFIED — the extreme bins are not both estimable. Exit 1."); return 1
    b_lo, b_hi = rows[0], rows[max(rows)]
    bites = b_lo["l"] < b_hi["l"]
    print(f"\n  CONTROLS")
    print(f"    STRATIFIER (+)  LENGTH's edge falls from {b_hi['l']:+.4f} (most dispersed) to "
          f"{b_lo['l']:+.4f} (least): {bites}   {'PASS' if bites else 'FAIL'}")
    print(f"                    if the binning does not weaken the rule it is built to weaken, it is")
    print(f"                    not measuring dispersion and no bin is readable")
    print(f"    NOT-OUTCOME     the stratifier is a function of the RESPONSES only — never of which")
    print(f"                    one the human chose. The tempting version of this test is Oldham's")
    print(f"                    error and is not run.")
    print(f"    ⛔ THAT LENGTH WEAKENS AS DISPERSION -> 0 IS FORCED (at equal lengths the rule is an")
    print(f"       arbitrary tiebreak). That is what makes it a control and a worthless finding.")
    if not bites:
        print(f"\n  W-BLIND — the stratifier does not bite. UNVERIFIED. Exit 1."); return 1

    print()
    g_survives = b_lo["g"] > b_lo["g_mde"]
    l_dead = b_lo["l"] <= b_lo["l_mde"]
    if g_survives:
        v = "W_BEYOND_LENGTH"
        print(f"  W-BEYOND-LENGTH — in the LEAST dispersed bin, where the length rule has "
              f"{'collapsed to chance' if l_dead else 'weakened'} ({b_lo['l']:+.4f} vs MDE "
              f"{b_lo['l_mde']:.4f}), generic still holds {b_lo['g']:+.4f} against its own MDE "
              f"{b_lo['g_mde']:.4f}.")
        print(f"  The core carries signal that is NOT a length effect, however small.")
    else:
        v = "W_ONLY_LENGTH"
        print(f"  W-ONLY-LENGTH — in the LEAST dispersed bin generic sits at {b_lo['g']:+.4f} "
              f"against its MDE {b_lo['g_mde']:.4f}: within it.")
        print(f"  Where length cannot help, the core does not either. On this corpus what the")
        print(f"  prompt-blind apparatus tracks is not separable from length.")
    print(f"\n  ⚠ NO CAUSAL CLAIM. This is nuisance-matching on a covariate, not an ablation — no")
    print(f"    intervention on response length exists here.")

    # ---- THE CONFOUND THE FIRST PANEL CANNOT ESCAPE, AND THE PANEL THAT CAN ------------------------
    # Bin chance runs 0.4997 -> 0.2854, so dispersion is ENTANGLED with response count: the most
    # dispersed bin is mostly n=4, and the strata round already found generic clears at n>=3. So a
    # rising edge across bins could be the n effect wearing dispersion's clothes. Holding n FIXED at
    # 2 makes chance constant at 0.5 by construction and leaves dispersion as the only mover.
    print(f"\n  ⛔ THE FIRST PANEL IS CONFOUNDED WITH RESPONSE COUNT — chance runs {rows[0]['chance']:.4f}")
    print(f"     to {rows[max(rows)]['chance']:.4f} across bins, so the most dispersed bin is mostly")
    print(f"     n=4, and generic was already shown to clear at n>=3. Holding n FIXED at 2:")
    r2 = [r for r in recs if abs(r[4] - 0.5) < 1e-9]
    fixed = {}
    if len(r2) >= 8:
        q2 = np.quantile([r[1] for r in r2], [0.25, 0.50, 0.75])
        b2 = collections.defaultdict(lambda: collections.defaultdict(lambda: ([], [], [])))
        for conv, disp, g, l, c in r2:
            k = int(np.searchsorted(q2, disp, side="right"))
            x, y, z = b2[k][conv]
            x.append(g); y.append(l); z.append(c)
        print(f"    {'bin':<5} {'log(max/min) range':<22} {'chance':>7} {'g−chance':>9} {'MDE':>8} "
              f"{'l−chance':>9} {'MDE':>8} {'convs':>7}")
        lo2 = ["min"] + [f"{q:.3f}" for q in q2]; hi2 = [f"{q:.3f}" for q in q2] + ["max"]
        for k in sorted(b2):
            ge, le = edge(b2[k], 0), edge(b2[k], 1)
            if ge is None or le is None:
                print(f"    {k:<5} {lo2[k] + ' … ' + hi2[k]:<22} {'0.5000':>7} {'—':>9} {'—':>8} "
                      f"{'—':>9} {'—':>8} {len(b2[k]):>7}   UNVERIFIED"); continue
            fixed[k] = dict(g=ge[0], g_mde=ge[1], l=le[0], l_mde=le[1], convs=ge[2],
                            range=[lo2[k], hi2[k]])
            print(f"    {k:<5} {lo2[k] + ' … ' + hi2[k]:<22} {'0.5000':>7} {ge[0]:>+9.4f} "
                  f"{ge[1]:>8.4f} {le[0]:>+9.4f} {le[1]:>8.4f} {ge[2]:>7,}")
        if fixed:
            k_lo, k_hi = min(fixed), max(fixed)
            bites2 = fixed[k_lo]["l"] < fixed[k_hi]["l"]
            surv2 = fixed[k_lo]["g"] > fixed[k_lo]["g_mde"]
            print(f"\n    STRATIFIER (+) at fixed n=2: length falls {fixed[k_hi]['l']:+.4f} -> "
                  f"{fixed[k_lo]['l']:+.4f}: {bites2}   {'PASS' if bites2 else 'FAIL'}")
            print(f"    generic in the least-dispersed n=2 bin: {fixed[k_lo]['g']:+.4f} vs MDE "
                  f"{fixed[k_lo]['g_mde']:.4f} -> {'CLEARS' if surv2 else 'within noise'}")
            print(f"    ⭐ THIS PANEL IS THE ONE THAT LICENSES THE VERDICT. chance is 0.5 in every")
            print(f"       cell by construction, so nothing here can be the response-count effect.")
            v = "W_BEYOND_LENGTH_AT_FIXED_N" if surv2 else "W_ONLY_LENGTH_AT_FIXED_N"
    else:
        print(f"    too few n=2 interactions to stratify — UNVERIFIED at fixed n")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               bins={str(k): v2 for k, v2 in rows.items()}, quantiles=[float(q) for q in qs],
               stratifier_bites=bites, generic_survives=g_survives, length_dead_lowbin=l_dead,
               unverifiable=unver, fixed_n2=fixed, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_length_dose.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
