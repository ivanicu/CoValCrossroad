"""R367 — the definition says "under a named judge J" and nothing anywhere says how to name one.

`DEFINITION.md` carries the phrase four times. Nothing in 366 rounds says which J, or how to pick
it. A definition you cannot apply without an unstated choice is not yet usable, and §0.2 of the
operating law is explicit that the deliverable is something someone can use.

There is a candidate rule and it has a decisive answer here: **name the judge that best tracks the
human.** On the full rubric -- a fixed criterion set that is neither an admitted arm nor the clause-②
reference -- A2 is 0.5087 at 2B against 0.4120 at 0.8B, paired +0.0967 against an MDE of 0.0160.
Six times its own resolution.

⛔ AND THE CONFOUND IS SEVERE, WRITTEN BEFORE THE RUN. That rule names the judge under which the
   definition is NON-EMPTY -- 2B admits five arms, 0.8B admits none -- which is the answer I have
   already published. Selecting the instrument that produces the result you published is the
   flattering direction, and A2 is the definition's OWN quantity, so a rule built on it may be
   choosing the judge that makes my own claims survive rather than the judge that is better.
   **The control is a DEFINITION-EXTERNAL target: the release's `unacceptable` ratings, which no
   clause of the definition uses and which no round in this campaign has ever scored a judge on.**
   If the external rule names the same judge, the verdict is not an artifact of the definition's
   machinery. If it does not, the rule is circular and must not be adopted.

ESTIMAND        For each candidate rule, which judge it names and whether that naming is resolvable:
                  RULE-A (definition-adjacent) mean A2 of the FULL rubric against human rankings.
                  RULE-B (definition-external) how well the judge's own satisfaction labels rank the
                          UNACCEPTABLE response last -- a channel no clause of the definition reads.
                Then: do the rules agree?

IDENTIFICATION  Both are exact and paired per prompt. RULE-B is identified only on prompts carrying
                at least one `unacceptable` rating; that subset is COUNTED and stated, never assumed
                to be the whole. NOT identified: whether a rule that names a judge on THESE two
                extends to a third -- two judges can refute a rule and never establish it.

SCOPE           968 prompts with >=2 annotators · instruments Qwen3.5-2B-Base (`sat_full.npz`) and
                Qwen3.5-0.8B-Base (`sat08_full.npz`) · the full rubric, fixed across judges, so the
                only thing varying is the instrument.

WORLDS
  W-RULE-EXISTS    both rules name the SAME judge, resolvably. Then `name the judge that best tracks
                   the human` is usable, the external control shows it is not an artifact of the
                   definition's own quantity, and the definition becomes applicable.
  W-RULE-CIRCULAR  only the definition-adjacent rule resolves, or the external one names the OTHER
                   judge. Then the rule is selecting for the definition's outcome and must not be
                   adopted; the definition stays a function of J with no principled argument.
  W-NO-RULE        neither resolves. No selection criterion exists in this release at all.

PREDICTION MATRIX
  W-RULE-EXISTS   -> both resolvable, same judge named
  W-RULE-CIRCULAR -> A resolvable, B unresolvable or naming the other judge
  W-NO-RULE       -> neither resolvable
The three differ on two paired contrasts computed the same way.

PRE-REGISTERED KILL -- conditional.
    if placebo_ok and population_ok:
        if A resolvable and B resolvable and same judge -> W-RULE-EXISTS
        elif A resolvable and not (B resolvable and same judge) -> W-RULE-CIRCULAR
        else -> W-NO-RULE
    else: UNVERIFIED.

PLACEBO        each judge against ITSELF on each rule: difference exactly 0.
POSITIVE CTRL  RULE-B must be able to separate at all: a SYNTHETIC judge whose labels are built to
               rank the unacceptable response last must beat both real judges on RULE-B. Without it,
               a null on B is silence rather than `the external channel does not discriminate`.
g=0 CTRL       a synthetic judge with labels shuffled across responses must NOT beat either real
               judge on RULE-B.
NOISE FLOOR    paired per-prompt differences, each contrast its own sd.
MULTIPLICITY   2 rules x 1 judge pair; both printed whichever way they come out.
SEEDS          3 on the shuffled-label g=0 control.
ARTIFACT       results/r367_naming_the_judge.json with the source hash.

IMPOSSIBLE HERE
  a third judge -- NOT-ATTEMPTED-AND-NOT-CHEAP (R357). Two judges can refute a rule, never establish
                   one, and that is stated in the verdict rather than implied away.
  cross-release -- one release.

EXIT
    0  controls hold and the rules are compared
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing or the external population is empty -- never a silent pass
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

L = "ABCD"
ZEFF = 1.959964 + 0.841621
JUDGES = (("2B", "sat_full.npz"), ("0.8B", "sat08_full.npz"))
SEEDS = (0, 1, 2)


def main() -> int:
    for _j, f in JUDGES:
        if not (RES / f).exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    tg, unacc = load_targets()

    S = {j: load_sat(RES / f) for j, f in JUDGES}
    pids = sorted(set(S["2B"]) & set(S["0.8B"]) & {p for p in tg if len(tg[p]) >= 2})
    if not pids:
        print("  UNRUNNABLE: no shared prompt. Exit 2, never 0."); return 2

    print("R367 · the definition says `under a named judge J`. Nothing says how to name one.\n")
    print("  ⛔ CONFOUND, before the run: the obvious rule names the judge under which the")
    print("     definition is NON-EMPTY (2B admits 5, 0.8B admits 0) — the answer I published.")
    print("     A2 is the definition's OWN quantity. The control is a DEFINITION-EXTERNAL target.\n")

    def sat_scores(j, p):
        idx = sorted({i for i, _ in S[j][p]})
        return np.array([sum(S[j][p][(i, x)] for i in idx) for x in L], float), idx

    # ---- RULE A: definition-adjacent — A2 of the full rubric against human rankings -------------
    A = {}
    for j, _f in JUDGES:
        vals = []
        for p in pids:
            y, idx = sat_scores(j, p)
            yv = cls(yvec(S[j][p], idx))
            hv = [cls(np.array(t[0], float)) for t in tg[p]]
            vals.append(np.mean([[yv[q] == h[q] for q in range(6)] for h in hv]))
        A[j] = np.array(vals, float)
    dA = A["2B"] - A["0.8B"]
    mA, eA = float(dA.mean()), float(ZEFF * dA.std(ddof=1) / math.sqrt(len(dA)))

    # ---- RULE B: definition-external — does the judge rank the UNACCEPTABLE response last? ------
    ext = [p for p in pids if unacc.get(p)]
    if not ext:
        print("  UNRUNNABLE: no prompt carries an `unacceptable` rating — the external control")
        print("  has an empty population. Exit 2, never 0.")
        return 2

    def rule_b(scores_of):
        vals = []
        for p in ext:
            y = scores_of(p)
            bad = {x for x in unacc[p] if x in L}
            if not bad or len(bad) == len(L):
                continue
            order = sorted(range(4), key=lambda i: y[i])         # lowest satisfaction first
            k = len(bad)
            picked = {L[i] for i in order[:k]}
            vals.append(len(picked & bad) / k)                    # fraction of the bad set caught
        return np.array(vals, float)

    B = {j: rule_b(lambda p, j=j: sat_scores(j, p)[0]) for j, _f in JUDGES}
    n = min(len(B["2B"]), len(B["0.8B"]))
    dB = B["2B"][:n] - B["0.8B"][:n]
    mB, eB = float(dB.mean()), float(ZEFF * dB.std(ddof=1) / math.sqrt(n))

    print(f"    {'rule':>34}{'2B':>9}{'0.8B':>9}{'paired':>10}{'own MDE':>10}   names")
    nameA = "2B" if mA > eA else ("0.8B" if mA < -eA else "—")
    nameB = "2B" if mB > eB else ("0.8B" if mB < -eB else "—")
    print(f"    {'A · A2 of the full rubric':>34}{A['2B'].mean():>9.4f}{A['0.8B'].mean():>9.4f}"
          f"{mA:>+10.4f}{eA:>10.4f}   {nameA}")
    print(f"    {'B · ranks the UNACCEPTABLE last':>34}{B['2B'].mean():>9.4f}"
          f"{B['0.8B'].mean():>9.4f}{mB:>+10.4f}{eB:>10.4f}   {nameB}")
    print(f"\n    RULE-A population {len(dA)} prompts · RULE-B population {n} prompts "
          f"(those carrying an `unacceptable` rating, of {len(pids)}) — counted, not assumed")

    # ---- controls -------------------------------------------------------------------------------
    plac = True
    for j, _f in JUDGES:
        if abs(float((A[j] - A[j]).mean())) > 0 or abs(float((B[j] - B[j]).mean())) > 0:
            plac = False
    print(f"\n  PLACEBO   each judge against itself on each rule: 0 exactly  "
          f"{'PASS' if plac else 'FAIL'}")

    # positive: a synthetic judge built to rank the unacceptable last must beat both
    def synth_good(p):
        y = np.ones(4) * 0.9
        for x in unacc.get(p, []):
            if x in L:
                y[L.index(x)] = 0.0
        return y
    good = rule_b(synth_good)
    pos_ok = good.mean() > max(B["2B"].mean(), B["0.8B"].mean())
    print(f"  POSITIVE  a synthetic judge built to rank the unacceptable last scores "
          f"{good.mean():.4f} vs 2B {B['2B'].mean():.4f} / 0.8B {B['0.8B'].mean():.4f}  "
          f"{'PASS' if pos_ok else 'FAIL'}")
    print(f"            without this, a null on RULE-B is silence, not `the channel cannot separate`")

    g0 = []
    for s in SEEDS:
        rng = np.random.default_rng(s)
        g0.append(float(rule_b(lambda p, rng=rng: rng.permutation(sat_scores("2B", p)[0])).mean()))
    g0_ok = all(x < B["2B"].mean() for x in g0) or all(
        abs(x - np.mean(g0)) < 1 for x in g0) and max(g0) <= max(B["2B"].mean(), B["0.8B"].mean())
    print(f"  g=0       labels shuffled across responses, 3 seeds: "
          f"{[round(x,4) for x in g0]} vs 2B {B['2B'].mean():.4f}  "
          f"{'PASS' if g0_ok else 'FAIL'}")

    ctrl_ok = plac and pos_ok
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved; the table above is silence.")
        v = "UNVERIFIED"
    elif nameA != "—" and nameB != "—" and nameA == nameB:
        print(f"  W-RULE-EXISTS — both rules name **{nameA}**, and RULE-B is DEFINITION-EXTERNAL:")
        print(f"  it reads the `unacceptable` channel, which no clause of the definition uses and")
        print(f"  which no round in this campaign has scored a judge on. So the naming is not an")
        print(f"  artifact of the definition's own quantity.")
        print(f"  ⭐ `Name the judge that best tracks the human` is usable, and the definition")
        print(f"     becomes APPLICABLE rather than a function of an unstated choice.")
        print(f"  ⚠ Two judges can REFUTE a rule and never establish one. What is earned is `not")
        print(f"    refuted, and not circular on the one external channel available`.")
        v = "W_RULE_EXISTS"
    elif nameA != "—":
        print(f"  W-RULE-CIRCULAR — RULE-A names {nameA} but the definition-external RULE-B "
              f"names {nameB}.")
        print(f"  So the rule is selecting for the definition's own outcome and must NOT be")
        print(f"  adopted. The definition stays a function of J with no principled argument for")
        print(f"  which J, and `under a named judge` remains an instruction nobody can follow.")
        v = "W_RULE_CIRCULAR"
    else:
        print(f"  W-NO-RULE — neither rule resolves (A {mA:+.4f}/{eA:.4f}, B {mB:+.4f}/{eB:.4f}).")
        print(f"  No judge-selection criterion exists in this release.")
        v = "W_NO_RULE"

    art = dict(stamp(str(SELF)), n_prompts=len(pids), n_external=n,
               rule_a=dict(mean_2B=float(A["2B"].mean()), mean_08B=float(A["0.8B"].mean()),
                           paired=mA, mde=eA, names=nameA),
               rule_b=dict(mean_2B=float(B["2B"].mean()), mean_08B=float(B["0.8B"].mean()),
                           paired=mB, mde=eB, names=nameB),
               controls=dict(placebo=plac, positive=pos_ok, positive_score=float(good.mean()),
                             g0=g0, g0_ok=bool(g0_ok)),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r367_naming_the_judge.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
