"""R427/response_effect -- WHY the two arms agree: is satisfaction a response effect, not a criterion one?

R427/arm_agreement measured the two prompt-blind arms picking the SAME response 69.8% of the time
against a 50.7% shuffled null. That says the criteria are close to inert as an INPUT to the RANKING.
It does not say why.

⭐ THE MECHANISM CANDIDATE IS ONE LEVEL DOWN. If the judge assigns a response nearly the same
   satisfaction whatever criterion it is handed, then the criterion text is being largely ignored at
   the SCORING level -- and identical rankings follow for free. That is a claim about the instrument,
   measurable from the two committed npz files, and it is sharper than the ranking agreement because
   it identifies where the inertness lives.

⛔ ARITHMETIC TRAP, AND IT IS THE WHOLE DESIGN HERE. Two arms scored by the SAME judge on the SAME
   responses will correlate somewhat no matter what, because both inherit whatever the responses are
   like. So a positive correlation is not by itself evidence. The informative quantity is the
   VARIANCE DECOMPOSITION inside a single arm: how much of satisfaction is a response main effect
   versus a criterion main effect versus their interaction. A criterion effect near zero cannot be
   explained by shared responses -- it is the criteria failing to differentiate anything.

ESTIMAND        within the `generic` arm, over all (response, criterion) cells:
                (A) the share of satisfaction variance attributable to the RESPONSE main effect;
                (B) the share attributable to the CRITERION main effect;
                (C) the residual (interaction + noise);
                and across arms, (D) corr(mean satisfaction per response under generic, under
                randblind).

IDENTIFICATION  (A)-(C) exact: the design is a complete response x criterion grid within each
                interaction, so the decomposition is balanced. (D) exact on shared responses.
                NOT identified: whether a criterion effect near zero is the JUDGE ignoring text or
                these particular criteria being undiscriminating. Named, and (D) bears on it.

SCOPE           population: every response in the 2,200 seeded conversations · instrument:
                Qwen3.5-2B-Base, k=4 prompt-blind criteria · baseline: shuffled-response null for
                (D) · regime: mean over nothing -- the raw cells are used.

WORLDS
  W-RESPONSE-EFFECT   the response main effect dominates and the criterion main effect is near zero.
                      Then satisfaction is mostly `how this judge feels about this reply`, the
                      criterion is nearly decorative at the scoring level, and the ranking agreement
                      is explained rather than merely described.
  W-CRITERION-EFFECT  the criterion main effect is comparable to or larger than the response effect.
                      Then the criteria DO move scores, and the ranking agreement must be explained
                      some other way -- the arms would be agreeing despite discriminating criteria.

PREDICTION MATRIX
  W-RESPONSE-EFFECT  -> response share >> criterion share; (D) high
  W-CRITERION-EFFECT -> criterion share comparable; (D) lower

PRE-REGISTERED KILL -- conditional on both controls.
    if the identity control returns corr = 1.0 and the shuffled-response null returns ~0:
        criterion share < half the response share -> W-RESPONSE-EFFECT
        else                                      -> W-CRITERION-EFFECT
    else: UNVERIFIED -- the estimator is unfit.

CONTROLS
  IDENTITY (+)  corr(generic mean, generic mean) must be exactly 1.0.
  SHUFFLE (-)   corr(generic mean, randblind mean with responses SHUFFLED) must be ~0. This is the
                floor for (D), and without it a high correlation says nothing.
                ⚠ It answers `did the pairing matter`, never why -- the world it excludes is exactly
                `the two arms' per-response means are unrelated`.
  BALANCE       the decomposition is only valid on a complete grid; the count of cells per response
                is checked and any ragged response is dropped and COUNTED.
  NO-TARGET     nothing here reads `if_chosen`.

MULTIPLICITY    4 quantities + 3 controls; all printed.
ARTIFACT        results/r427_response_effect.json with the source hash.

IMPOSSIBLE HERE
  whether the judge IGNORES criterion text in general -- this is k=4 prompt-blind criteria on one
                                                          corpus; a stronger claim needs varied k
                                                          and prompt-specific criteria.
  a mechanistic account of the judge -- needs access this design does not have.

EXIT
    0  the controls hold and a branch is reached
    1  a control misbehaved -- UNVERIFIED
    2  an arm is absent -- never a silent pass
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


def cells(tag):
    p = RES / f"sat_transport_{tag}.npz"
    if not p.exists():
        return None
    with np.load(p, allow_pickle=True) as d:
        meta, sat = [str(x) for x in d["meta"]], np.asarray(d["sat"], float)
    out = collections.defaultdict(dict)
    for m, v in zip(meta, sat):
        c, i, r, j = m.split("|")
        out[(c, i, r)][int(j)] = float(v)
    return dict(out)


def main() -> int:
    g = cells("generic")
    r = cells("randblind_s0")
    if g is None or r is None:
        print("  UNRUNNABLE: an arm is absent. Exit 2, never 0."); return 2

    print("R427 · response_effect — WHY do the arms agree? Is satisfaction a RESPONSE effect?\n")
    print("  ⛔ TWO ARMS SCORED BY THE SAME JUDGE ON THE SAME RESPONSES WILL CORRELATE SOMEWHAT NO")
    print("     MATTER WHAT — both inherit whatever the responses are like. So a positive")
    print("     correlation is not by itself evidence. The informative quantity is the VARIANCE")
    print("     DECOMPOSITION inside ONE arm, where a near-zero criterion effect cannot be")
    print("     explained by shared responses.\n")

    ks = sorted(set(g) & set(r))
    kfull = sorted({len(v) for v in g.values()})
    kmode = max(kfull, key=lambda x: sum(1 for v in g.values() if len(v) == x))
    ragged = sum(1 for v in g.values() if len(v) != kmode)
    grid = [k for k in ks if len(g[k]) == kmode and len(r[k]) == kmode]
    print("  CONTROLS")
    print(f"    BALANCE     complete grid requires {kmode} criteria per response; ragged responses "
          f"dropped: {ragged:,} of {len(g):,}   usable {len(grid):,}")
    if len(grid) < 8:
        print("  UNRUNNABLE: too few complete cells. Exit 2."); return 2

    # ---- (A)-(C) two-way decomposition WITHIN generic -----------------------------------------------
    M = np.array([[g[k][j] for j in range(kmode)] for k in grid], float)   # responses x criteria
    gm = M.mean()
    row = M.mean(axis=1) - gm            # response main effect
    col = M.mean(axis=0) - gm            # criterion main effect
    resid = M - gm - row[:, None] - col[None, :]
    ss_row = float(kmode * np.sum(row ** 2))
    ss_col = float(len(grid) * np.sum(col ** 2))
    ss_res = float(np.sum(resid ** 2))
    ss_tot = ss_row + ss_col + ss_res

    # ---- (D) cross-arm per-response correlation ------------------------------------------------------
    gv = np.array([np.mean(list(g[k].values())) for k in grid])
    rv = np.array([np.mean(list(r[k].values())) for k in grid])
    ident = float(np.corrcoef(gv, gv)[0, 1])
    rng = np.random.default_rng(0)
    shuf = float(np.corrcoef(gv, rng.permutation(rv))[0, 1])
    cross = float(np.corrcoef(gv, rv)[0, 1])
    id_ok = abs(ident - 1.0) < 1e-9
    sh_ok = abs(shuf) < 0.05
    print(f"    IDENTITY (+) corr(generic, generic) = {ident:.4f}   {'PASS' if id_ok else 'FAIL'}")
    print(f"    SHUFFLE (-)  corr(generic, randblind with responses SHUFFLED) = {shuf:+.4f}   "
          f"{'PASS' if sh_ok else 'FAIL'}")
    print(f"                 ⚠ answers `did the pairing matter`, never why. The world it excludes is")
    print(f"                   exactly `the two arms' per-response means are unrelated`.")
    print(f"    NO-TARGET    nothing here reads `if_chosen`.")
    if not (id_ok and sh_ok):
        print("\n  UNVERIFIED — the estimator is unfit. Exit 1."); return 1

    print(f"\n  VARIANCE OF SATISFACTION INSIDE `generic` — {len(grid):,} responses x {kmode} criteria")
    print(f"    RESPONSE main effect  {ss_row/ss_tot:>8.2%}   (how this judge feels about this reply)")
    print(f"    CRITERION main effect {ss_col/ss_tot:>8.2%}   (which of the four it was asked)")
    print(f"    residual + interaction{ss_res/ss_tot:>8.2%}")
    print(f"\n  CROSS-ARM, per response: corr(generic mean, randblind mean) = {cross:+.4f}")
    print(f"    against a shuffled-response floor of {shuf:+.4f}")

    print()
    if ss_col < 0.5 * ss_row:
        v = "W_RESPONSE_EFFECT"
        print(f"  W-RESPONSE-EFFECT — the RESPONSE main effect is {ss_row/ss_tot:.1%} of satisfaction")
        print(f"  variance and the CRITERION main effect is {ss_col/ss_tot:.1%}. Satisfaction is")
        print(f"  mostly `how this judge feels about this reply`; which of the four criteria it was")
        print(f"  asked moves it far less.")
        print(f"  ⛔ THAT EXPLAINS THE 69.8% RANKING AGREEMENT RATHER THAN MERELY RESTATING IT: if the")
        print(f"     criterion barely moves the score, two arms with different criteria must rank")
        print(f"     alike, and `generic − randblind ≈ 0` follows for free.")
    else:
        v = "W_CRITERION_EFFECT"
        print(f"  W-CRITERION-EFFECT — the criterion main effect is {ss_col/ss_tot:.1%} against the")
        print(f"  response effect's {ss_row/ss_tot:.1%}: comparable. The criteria DO move scores, so")
        print(f"  the ranking agreement needs a different explanation — the arms agree DESPITE")
        print(f"  discriminating criteria, which is the more surprising world.")

    print(f"\n  ⚠ WHETHER THE JUDGE IGNORES CRITERION TEXT IN GENERAL IS NOT IDENTIFIED. This is k=4")
    print(f"    PROMPT-BLIND criteria on one corpus; a stronger claim needs varied k and")
    print(f"    prompt-specific criteria. And a near-zero criterion effect could be these particular")
    print(f"    criteria failing to discriminate rather than the judge failing to read them.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               n_responses=len(grid), k=kmode, ragged=ragged,
               ss_response=ss_row/ss_tot, ss_criterion=ss_col/ss_tot, ss_residual=ss_res/ss_tot,
               cross_corr=cross, controls=dict(identity=ident, shuffle=shuf), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_response_effect.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
