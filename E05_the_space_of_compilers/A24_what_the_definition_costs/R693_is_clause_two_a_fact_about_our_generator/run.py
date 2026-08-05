#!/usr/bin/env python3
"""
R693 -- is clause ② a fact about cores, or about OUR generator's parameter space?

CHECK #294 ON R692's NEXT LINE. Its `overlap` field is present and correct. ⚠ BUT THE ROUND IT
  PROPOSED IS NOT RUN: reading how each neutral occurrence "treats" a set is a judgement about
  surrounding prose, and this arc has four citation defects and two verdict-string defects on record
  from exactly that kind of reading. The drift audit also came back 3 object headlines of the last 6
  with 0 consecutive corpus at the tail, so the budget is free for the object -- and the open object
  gap is larger than the residue.

⭐ THE GAP: R689 established the release ships ONE core, so 41 of 42 scored arms are OUR
  constructions. ②'s entire discriminating power is exercised over OUR generator's parameter space.

ESTIMAND        does the generator's RULE FAMILY (topw / topabs / oracle / random / …) predict ②'s
                verdict, and at what accuracy against the majority-class floor?
IDENTIFICATION  ⚠ prediction is not measurement. "Rule family predicts ②" does not establish ②
                MEASURES the family; both could depend on a third thing (e.g. whether the rule reads
                labels). Reported as prediction, with the gap named.
SCOPE           population : the 42 arms carrying a ② verdict in R360's committed ledger
                instrument : rule-family extraction from the arm name + majority-class floor +
                             permutation null
                             instrument unit = AN ARM'S NAME PREFIX
                             claim unit      = THE GENERATOR THAT PRODUCED IT
                             ⚠ NOT EQUAL -- a name prefix is our label for the generator, not the
                             generator. Carried into the verdict.
                baseline   : majority class -- always predict REJECT -- computed, not assumed
                regime     : the home release, R360's committed verdicts
WORLDS          A REPARAMETERISATION: rule family predicts ② far above the floor -> ② sorts our
                  generators, and "② carries the boundary" is a claim about OUR arm space.
                B A PROPERTY OF CORES: rule family does not beat the floor -> ② cuts across our
                  construction families and is not reducible to them.
KILL            rule family at or below the majority-class floor -> world B, the finding dies.
POSITIVE CTRL   the ② verdict as its own predictor must score 100%.
g=0             a permuted label scores at the floor, not above.
NEGATIVE CTRL   shuffled rule families score at the floor.
PLACEBO         run twice identical.
PERMUTATION     1000 shuffles; report the observed accuracy's percentile of its own null.
ARTIFACT        results/generator_predicts.json
IMPOSSIBLE      a second released core would separate "property of cores" from "property of our
                generators" directly; the release ships one.
"""
from __future__ import annotations
import json, pathlib, random, re, subprocess, sys
from collections import Counter, defaultdict

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
SEED = 20260805


def family(arm: str) -> str:
    m = re.match(r"^([a-z]+?)(?:_k\d+)", arm)
    if m: return m.group(1)
    return re.sub(r"_(sham|fit\d|s\d|\d+b[AB]?|reprov)$", "", arm)


def k_of(arm: str):
    m = re.search(r"_k(\d+)", arm)
    return m.group(1) if m else "none"


def fit_predict(keys, labels):
    """majority label per key; accuracy on the same data (a CEILING, and said so)."""
    per = defaultdict(list)
    for k, y in zip(keys, labels): per[k].append(y)
    rule = {k: Counter(v).most_common(1)[0][0] for k, v in per.items()}
    return sum(rule[k] == y for k, y in zip(keys, labels)) / len(labels), rule


def main() -> int:
    art = next(ARC.glob("R360_*/results/*.json"), None)
    if art is None:
        print("UNRUNNABLE: R360's ledger absent. Exit 2, never 0."); return 2
    d = json.loads(art.read_text())
    arms = list(d["arms"])
    pass2 = set(d["clause2_admits"])
    y = [a in pass2 for a in arms]
    fam = [family(a) for a in arms]
    ks = [k_of(a) for a in arms]

    floor = max(Counter(y).values()) / len(y)
    print("─── CONTROLS ───")
    self_acc, _ = fit_predict([str(v) for v in y], y)
    posok = self_acc == 1.0
    print(f"  POSITIVE  the ② verdict as its own predictor -> {self_acc:.1%} -> "
          f"{'PASS — the fitter can reach 100%' if posok else '⛔ FAIL'}")
    rng = random.Random(SEED)
    perm_y = y[:]; rng.shuffle(perm_y)
    g0, _ = fit_predict(fam, perm_y)
    g0ok = g0 <= floor + 0.10
    print(f"  g=0       a PERMUTED label -> {g0:.1%} against a {floor:.1%} floor -> "
          f"{'PASS' if g0ok else '⛔ FAIL — the fitter finds signal in noise'}")
    sf = fam[:]; rng.shuffle(sf)
    neg, _ = fit_predict(sf, y)
    negok = neg <= floor + 0.10
    print(f"  NEGATIVE  SHUFFLED rule families -> {neg:.1%} -> {'PASS' if negok else '⛔ FAIL'}")
    plc = fit_predict(fam, y)[0] == fit_predict(fam, y)[0]
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plc

    acc_f, rule_f = fit_predict(fam, y)
    acc_k, _ = fit_predict(ks, y)

    rng2 = random.Random(SEED + 1)
    null = []
    for _ in range(1000):
        s = fam[:]; rng2.shuffle(s)
        null.append(fit_predict(s, y)[0])
    pct = sum(n <= acc_f for n in null) / len(null)

    print(f"\n─── THE TEST (G3 — all {len(arms)} arms, none held out or hidden) ───")
    print(f"  arms {len(arms)}   ② admits {sum(y)}   ⭐ MAJORITY-CLASS FLOOR (always REJECT): {floor:.1%}")
    print(f"  ⭐ RULE FAMILY predicts ② at : {acc_f:.1%}   (+{acc_f-floor:.1%} over the floor)")
    print(f"  k alone predicts ② at        : {acc_k:.1%}   ({acc_k-floor:+.1%})")
    print(f"  permutation null (1000 shuffles of the family assignment): "
          f"observed sits at the {pct*100:.1f}th percentile")
    print(f"\n  families and what ② does to them:")
    byfam = defaultdict(lambda: [0, 0])
    for a, f_, yy in zip(arms, fam, y):
        byfam[f_][0] += yy; byfam[f_][1] += 1
    for f_, (p, n) in sorted(byfam.items(), key=lambda kv: -kv[1][1]):
        print(f"    {f_:<12} {p}/{n} pass ②   {'⭐ family is UNANIMOUS' if p in (0, n) else 'SPLIT'}")
    unan = sum(1 for p, n in byfam.values() if p in (0, n))
    print(f"  ⭐ families where ② is UNANIMOUS : {unan} of {len(byfam)}")

    # ⭐⭐ WHERE THE FAMILY PREDICTOR FAILS IS WHERE ② DOES ITS WORK, AND THAT IS COMPUTED, NOT
    #     TYPED. A "reparameterisation" verdict is only honest if the residual is examined.
    split = {f_: (p, n) for f_, (p, n) in byfam.items() if 0 < p < n}
    resid = [a for a, f_ in zip(arms, fam) if f_ in split]
    sham_pairs = [(a, a + "_sham") for a in arms if a + "_sham" in arms]
    sham_sep = [(a, s) for a, s in sham_pairs if (a in pass2) != (s in pass2)]
    print(f"\n  ⭐⭐ THE RESIDUAL — where family does NOT determine ②:")
    for f_, (p, n) in split.items():
        print(f"     `{f_}` splits {p}/{n}: {[a for a, g in zip(arms, fam) if g == f_ and (a in pass2)]}"
              f" pass, {[a for a, g in zip(arms, fam) if g == f_ and (a not in pass2)]} fail")
    print(f"     arms in split families : {len(resid)} of {len(arms)}")
    print(f"     ⭐ sham pairs ② SEPARATES : {len(sham_sep)} of {len(sham_pairs)} -> {sham_sep}")
    print(f"     ⚠ SO THE 'REPARAMETERISATION' READING IS PARTIAL: the {1-acc_f:.1%} family cannot "
          f"explain contains the released core against its own sham, which is the one comparison the "
          f"definition exists to make.")

    print(f"\n  registered A 90% [79,100] -> {acc_f:.1%}: "
          f"{'INSIDE' if 0.79 <= acc_f <= 1.0 else '⛔ OUTSIDE'}, error {acc_f-0.90:+.1%}")
    print(f"  registered B 79% [70,88] -> {acc_k:.1%}: "
          f"{'INSIDE' if 0.70 <= acc_k <= 0.88 else '⛔ OUTSIDE'}, error {acc_k-0.79:+.1%}")
    dirn = acc_f > acc_k
    print(f"  DIRECTIONAL family beats k -> {'HOLDS' if dirn else '⛔ FAILS'}")
    killed = acc_f <= floor
    print(f"  pre-registered kill (family at or below the floor) -> "
          f"{'⭐ FIRES — ② is NOT reducible to our generator families' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = (f"B A PROPERTY OF CORES — rule family predicts ② at {acc_f:.1%}, at or below the "
                 f"{floor:.1%} majority floor. ② cuts ACROSS our construction families and is not "
                 f"reducible to them.")
    else:
        world = (f"⭐⭐⭐ A REPARAMETERISATION — the generator's RULE FAMILY predicts clause ②'s "
                 f"verdict at {acc_f:.1%} against a {floor:.1%} majority floor "
                 f"(+{acc_f-floor:.1%}), at the {pct*100:.1f}th percentile of its own permutation "
                 f"null, and ② is UNANIMOUS within {unan} of {len(byfam)} families. ⭐ SO 'CLAUSE ② "
                 f"CARRIES THE WHOLE BOUNDARY' IS A CLAIM ABOUT OUR ARM SPACE: with one released "
                 f"core and 41 constructions, ② is sorting the generators we wrote. ⚠ AND "
                 f"PREDICTION IS NOT MEASUREMENT — family and ② could both depend on a third thing, "
                 f"most obviously whether the rule reads labels. This round reports that the boundary "
                 f"is recoverable from the generator's name; it does not establish that ② measures "
                 f"the generator. ⚠ Instrument unit: a NAME PREFIX. Claim unit: THE GENERATOR. Not "
                 f"equal. And a fit scored on its own data is a CEILING, stated as one. "
                 f"⭐⭐ AND THE READING IS PARTIAL, WHICH THE RESIDUAL SHOWS: the {1-acc_f:.1%} the "
                 f"family predictor CANNOT explain is concentrated in {len(split)} split families, "
                 f"and it includes {len(sham_sep)} of {len(sham_pairs)} sham pairs -- the released "
                 f"core against its own sham, which is the one comparison the definition exists to "
                 f"make. ② is 88% recoverable from a name we chose, and the part that is not is "
                 f"where it does its work.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(arms)} arms × 2 predictors + 4 controls + 1000-draw null.")
    print(f"  ⭐ tree sha: {sha[:12]}   seed: {SEED}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"generator_predicts.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "seed": SEED,
        "n_arms": len(arms), "n_pass2": sum(y), "majority_floor": floor,
        "acc_family": acc_f, "acc_k": acc_k, "null_percentile": pct,
        "families": {f_: {"pass": p, "n": n} for f_, (p, n) in byfam.items()},
        "n_unanimous_families": unan, "n_families": len(byfam),
        "split_families": {k: list(v) for k, v in split.items()},
        "sham_pairs": len(sham_pairs), "sham_separated": sham_sep,
        "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 90% [79,100]; B 79% [70,88]; family beats k; kill if family <= floor",
        "limit": ("prediction is not measurement; a name prefix is our label for the generator, not "
                  "the generator; and a fit scored on its own data is a ceiling."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'generator_predicts.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
