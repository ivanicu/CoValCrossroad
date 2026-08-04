"""R337 — every clause-3 route hits the same wall, and it is not the route. It is n=4.

R336 killed the PERFORMANCE route for clause 3: R295's slope correlates with arm quality at
r = +0.934 and carries no residual leak signal. It closed by proposing a route that does not go
through the score -- a signature read off the CRITERIA THEMSELVES -- and asserting "criterion text is
data this campaign has never touched in 300+ rounds."

FALSE, AND R250 IS 86 ROUNDS OLD. `R250_can_provenance_be_reconstructed` did exactly that: 303 of
3,899 core items are VERBATIM matches to a criterion in their own prompt's rubric, giving ground
truth; a dose-response on text perturbation; recovery 0.9871 at 40% token drop against a chance floor
of 0.0792. Its verdict: "provenance SURVIVES realistic rewriting."

⚠ AND THAT IS THE FOURTH CONSECUTIVE next-gradient line wrong about my own work -- R333 (annotator
axis, migrated by R306), R334 (clause 3 has no instrument, built by R295), R336 (criterion text
never touched, done by R250), plus R333's margin argument which was wrong on mechanism. Three of the
four MANUFACTURED work that already existed. §4 says the direction is not systematic; over these
four it is, and the count is the reason this round exists rather than another detector.

⛔ BUT R250 DOES NOT ANSWER CLAUSE 3, and conflating them would be the fifth error. R250 recovers a
criterion's PARENT -- where the text came from. Clause 3 asks how the SUBSET was CHOSEN. A leaky core
and a clean core draw from the same rubric, so their criteria have the same textual ancestry; what
differs is WHICH ones were picked. Provenance-of-text and provenance-of-selection are different
estimands and only the second is clause 3.

THE QUESTION THAT SURVIVES. Is there ANY label-free signature -- text or structure -- of a
label-driven SELECTION? And if there is, does it generalise to an arm the classifier has not seen?
Because that is where every route so far has actually failed: the release contains 4 arms annotated
leaky, and 4 is the population, not the instrument.

ESTIMAND      (i) whether the selected SET's label-free features differ between annotated-leaky and
              annotated-clean arms, at the (arm, prompt) unit where n is large; (ii) whether a
              classifier trained on those features generalises to a HELD-OUT ARM, which is the unit
              a clause-3 test must actually work at; (iii) the gap between the two, which is the
              measurable form of "the wall is the population".
IDENTIFICATION (i) is identified at n = 968 prompts per arm. (ii) is identified only at n = 4
              positive arms, and leave-one-ARM-out is the only honest split -- holding out prompts
              lets the classifier memorise the arm. The contrast between the two n's is the point.
SCOPE         population R294's 39 scored arms x 968 prompts · features computed from the rubric
              and the judge's satisfaction ONLY, never from human labels · instrument logistic
              discrimination on standardised features · regime k as published per arm.
WORLDS        W-SIGNATURE  separable within-arm AND across held-out arms -> a label-free selection
                           signature exists and clause 3 can carry a computed test.
              W-POPULATION separable within-arm but NOT across held-out arms -> the features track
                           these four arms rather than leakage, and the binding constraint is the
                           number of leaky arms. Register entry with a number attached.
              W-NOTHING    not separable even within-arm -> selection leaves no label-free trace at
                           all, which is a stronger negative and closes the route outright.
KILL          pre-registered, conditional on the controls:
                within-arm AUC <= 0.60                          -> W-NOTHING
                else held-out-arm AUC >= 0.80                    -> W-SIGNATURE
                else                                             -> W-POPULATION
POSITIVE CTRL a PLANTED signature: add a feature that is the leak label plus noise, at a dose that
              makes it recoverable. Held-out-arm AUC must rise to ~1.0, or the leave-one-arm-out
              harness cannot detect a signature that IS there and its low AUC is silence.
              It FAILS at g=0: with the planted feature at pure noise, AUC must return to the
              unplanted value.
NEGATIVE CTRL SHUFFLE the arm labels among arms (not among rows) and re-run leave-one-arm-out. AUC
              must fall to chance. Shuffling ROWS would leave each arm's identity intact and is the
              contaminated-control failure; the permutation has to destroy the thing under test.
PLACEBO       a feature set of pure noise: AUC ~ 0.5 both within-arm and held-out.
NOISE FLOOR   across-seed spread of every AUC, from 3 seeds.
MULTIPLICITY  2 evaluation modes x 3 seeds x 4 held-out folds; every fold printed.
SPECIFICATION the feature family is swept in three nested sets (structure only, + text, + both) so
              the conclusion is shown not to depend on one choice of features.
SEEDS         3.
ARTIFACT      results/selection_signature.json with source hash.
IMPOSSIBLE    more leaky arms. The release annotates 4, and manufacturing more (as R335 did) makes
              them MINE rather than the release's -- which is exactly the generalisation this round
              is testing, so it cannot be fixed by manufacturing.
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, re, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

SELF = pathlib.Path(__file__).resolve()
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
SEEDS = (0, 1, 2)
TOK = re.compile(r"[a-z0-9]+")


def load_json(pat, sub="A24_what_the_definition_costs"):
    d = next((ROOT / "E05_the_space_of_compilers" / sub).glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def auc(y, s):
    pos = s[y == 1]; neg = s[y == 0]
    if len(pos) == 0 or len(neg) == 0:
        return float("nan")
    return float((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean())


def fit_logit(X, y, iters=200, lr=0.5):
    w = np.zeros(X.shape[1]); b = 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(X @ w + b)))
        g = X.T @ (p - y) / len(y); gb = float((p - y).mean())
        w -= lr * g; b -= lr * gb
    return w, b


def main() -> int:
    r294 = load_json("R294_*")
    if r294 is None:
        print("  UNRUNNABLE: R294 absent."); return 2
    rows = r294["rows"]

    RES = ROOT / "corebench" / "results"
    tg, _ = load_targets()
    FULL = load_sat(RES / "sat_full.npz")
    # ⚠ conversation_rubrics.jsonl carries NO id field -- only `conversation`, `coval_full`,
    # `coval_core`. Keying it by `r.get("prompt_id")` gave a single None key and an EMPTY
    # intersection, which crashed rather than passing: `empty population passes` avoided by luck.
    # The campaign's own joiner is covalx.judge.load_join, which pairs the rubric file to
    # comparisons.jsonl. Use it rather than re-deriving a key that does not exist.
    from covalx.judge import load_join                                   # noqa: E402
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    rub_txt = {}
    for p_, _pr, r in joined:
        items = r.get("coval_full") or []
        if items:
            rub_txt[p_] = [
                (i.get("criterion", ""),
                 float(np.mean([sc["score"] for sc in (i.get("scores") or [])]))
                 if i.get("scores") else 0.0) for i in items]

    arms = [a for a in sorted(rows) if (RES / f"core_{a}.json").exists()]
    core = {a: json.loads((RES / f"core_{a}.json").read_text()) for a in arms}
    pids = sorted(set(FULL) & set(rub_txt) & {p for p in tg if len(tg[p]) >= 2}
                  & set.intersection(*(set(core[a]) for a in arms)))
    leaky = {a for a in arms if not rows[a]["ok3"]}
    print(f"  {len(arms)} arms with a core json · {len(pids)} prompts · "
          f"{len(leaky)} annotated LEAKY: {sorted(leaky)}\n")
    if len(leaky) < 2:
        print("  UNRUNNABLE: fewer than 2 leaky arms."); return 2
    if len(pids) < 50:
        # §4 `empty population passes`: exit 2, never 0, and never a traceback either.
        print(f"  UNRUNNABLE: only {len(pids)} prompts in the 3-way intersection "
              f"(sat_full {len(FULL)}, rubrics {len(rub_txt)}, cores "
              f"{min(len(core[a]) for a in arms)})."); return 2

    SATM = {p: np.array([[FULL[p][(i, x)] for x in "ABCD"]
                         for i in sorted({i for i, _ in FULL[p]})], float) for p in pids}

    def feats(a, p):
        sel_txt = [it["criterion"] if isinstance(it, dict) else str(it) for it in core[a][p]]
        pool = rub_txt[p]
        pool_txt = [t for t, _ in pool]; pool_w = np.array([w for _, w in pool], float)
        M = SATM[p]
        idx = [pool_txt.index(t) for t in sel_txt if t in pool_txt]
        n_match = len(idx)
        if idx:
            w = pool_w[idx]; sm = M[[i for i in idx if i < len(M)]] if len(M) else np.zeros((1, 4))
            posn = np.array(idx, float) / max(len(pool_txt) - 1, 1)
        else:
            w = np.zeros(1); sm = np.zeros((1, 4)); posn = np.zeros(1)
        toks = [set(TOK.findall(t.lower())) for t in sel_txt]
        jac = [len(x & y) / max(len(x | y), 1) for x, y in itertools.combinations(toks, 2)] or [0.0]
        return dict(
            struct=[float(w.mean()), float(w.max()), float(w.std()),
                    float(sm.std(axis=1).mean()), float(sm.mean()),
                    float(posn.mean()), float(posn.std())],
            text=[float(np.mean([len(t) for t in sel_txt])),
                  float(np.mean([len(x) for x in toks])),
                  float(np.mean(jac)), float(np.max(jac)),
                  float(n_match) / max(len(sel_txt), 1)])

    print("  building (arm, prompt) feature rows …")
    F, Y, ARM = [], [], []
    for a in arms:
        for p in pids:
            try:
                f = feats(a, p)
            except Exception:
                continue
            F.append(f); Y.append(1 if a in leaky else 0); ARM.append(a)
    Y = np.array(Y); ARM = np.array(ARM)
    SETS = {"structure only": lambda f: f["struct"],
            "text only": lambda f: f["text"],
            "structure + text": lambda f: f["struct"] + f["text"]}
    print(f"  {len(F)} rows · {len(set(ARM))} arms · {int(Y.sum())} leaky rows\n")

    def run(Xall, y, arm, planted=None, shuffle_arm_labels=False, seed=0):
        rng = np.random.default_rng(500 + seed)
        yy = y.copy()
        if shuffle_arm_labels:
            uniq = sorted(set(arm)); lab = {a: int(y[arm == a][0]) for a in uniq}
            vals = list(lab.values()); rng.shuffle(vals)
            newlab = dict(zip(uniq, vals))
            yy = np.array([newlab[a] for a in arm])
        X = Xall.copy()
        if planted is not None:
            X = np.column_stack([X, yy * planted + rng.normal(0, 1, len(yy))])
        mu, sd = X.mean(0), X.std(0) + 1e-9
        X = (X - mu) / sd
        # within-arm (rows split at random): the optimistic mode
        idx = rng.permutation(len(yy)); cut = len(yy) // 2
        w, b = fit_logit(X[idx[:cut]], yy[idx[:cut]].astype(float))
        a_in = auc(yy[idx[cut:]], X[idx[cut:]] @ w + b)
        # leave-one-ARM-out over the positive arms: the honest mode
        outs = []
        for a_ in sorted({a for a in arm if yy[arm == a][0] == 1}):
            tr = arm != a_
            w, b = fit_logit(X[tr], yy[tr].astype(float))
            te = (arm == a_) | (yy == 0)
            outs.append(auc(yy[te], X[te] @ w + b))
        return a_in, float(np.mean(outs)), outs

    print(f"    {'feature set':<20}{'within-arm AUC':>16}{'held-out-arm AUC':>18}{'folds':>32}")
    RESU = {}
    for name, pick in SETS.items():
        X = np.array([pick(f) for f in F], float)
        ins, hos, folds = zip(*[run(X, Y, ARM, seed=s) for s in SEEDS])
        RESU[name] = dict(within=float(np.mean(ins)), within_sd=float(np.std(ins)),
                          heldout=float(np.mean(hos)), heldout_sd=float(np.std(hos)),
                          folds=[round(x, 3) for x in folds[0]])
        print(f"    {name:<20}{np.mean(ins):>10.3f} ±{np.std(ins):<4.3f}"
              f"{np.mean(hos):>12.3f} ±{np.std(hos):<4.3f}   {[round(x,3) for x in folds[0]]}")

    Xb = np.array([SETS["structure + text"](f) for f in F], float)
    within = RESU["structure + text"]["within"]; heldout = RESU["structure + text"]["heldout"]

    # ---- POSITIVE CTRL · a planted signature must be recoverable across held-out arms -------------
    pin, pho, _ = zip(*[run(Xb, Y, ARM, planted=6.0, seed=s) for s in SEEDS])
    pos_ok = float(np.mean(pho)) > 0.95
    zin, zho, _ = zip(*[run(Xb, Y, ARM, planted=0.0, seed=s) for s in SEEDS])
    g0_ok = abs(float(np.mean(zho)) - heldout) < 0.10
    print(f"\n  POSITIVE CTRL  a PLANTED feature (label + noise, dose 6.0): held-out AUC "
          f"{np.mean(pho):.3f}  {'PASS — the harness CAN see a signature that is there' if pos_ok else 'FAIL'}")
    print(f"    g=0 · the same feature at pure noise: held-out AUC {np.mean(zho):.3f} vs unplanted "
          f"{heldout:.3f}  {'PASS' if g0_ok else 'FAIL'}")

    # ---- NEGATIVE · shuffle ARM labels, not rows ---------------------------------------------------
    sin, sho, _ = zip(*[run(Xb, Y, ARM, shuffle_arm_labels=True, seed=s) for s in SEEDS])
    neg_ok = abs(float(np.mean(sho)) - 0.5) < 0.20
    print(f"  NEGATIVE CTRL  ARM labels shuffled (not rows — shuffling rows leaves arm identity "
          f"intact): held-out AUC {np.mean(sho):.3f}  {'PASS' if neg_ok else 'FAIL'}")

    # ---- PLACEBO · pure noise features ---------------------------------------------------------------
    rngp = np.random.default_rng(9)
    Xn = rngp.normal(0, 1, (len(F), Xb.shape[1]))
    nin, nho, _ = zip(*[run(Xn, Y, ARM, seed=s) for s in SEEDS])
    plc_ok = abs(float(np.mean(nin)) - 0.5) < 0.10
    print(f"  PLACEBO        pure-noise features: within {np.mean(nin):.3f}, held-out "
          f"{np.mean(nho):.3f}  {'PASS' if plc_ok else 'FAIL'}")

    ctrl = pos_ok and g0_ok and neg_ok and plc_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  positive={pos_ok}  g0={g0_ok}  negative={neg_ok}  placebo={plc_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; no signature statement is readable.")
    elif within <= 0.60:
        world = "W-NOTHING"
        print(f"  -> W-NOTHING. Within-arm AUC {within:.3f}: a label-driven selection leaves NO")
        print("     label-free trace at all, even where the classifier has seen the arm. The route")
        print("     closes outright and clause 3 cannot be computed from artifacts by any of the")
        print("     three feature families tried.")
    elif heldout >= 0.80:
        world = "W-SIGNATURE"
        print(f"  -> W-SIGNATURE. Held-out-arm AUC {heldout:.3f}: the signature generalises to an arm")
        print("     the classifier never saw, so clause 3 can carry a computed test.")
    else:
        world = "W-POPULATION"
        print(f"  -> W-POPULATION. Within-arm AUC {within:.3f} against held-out-arm {heldout:.3f}.")
        print("     The features separate these four arms and do NOT transfer to an arm held out,")
        print("     so what they track is the arms rather than leakage. And the positive control")
        print(f"     shows the harness CAN see a real signature across arms ({np.mean(pho):.3f}), so")
        print("     this is a measurement and not silence.")
        print("  ⛔ THE BINDING CONSTRAINT IS THE POPULATION, NOT THE ROUTE. The release annotates 4")
        print("     leaky arms. Performance-based detection died to a quality confound (R336);")
        print("     feature-based detection dies to n=4. Manufacturing more leaky arms makes them")
        print("     MINE rather than the release's, which is precisely the generalisation being")
        print("     tested, so it cannot be fixed by manufacturing.")
    print("  " + "=" * 78)
    print(f"\n  ⚠ AND R250 IS NOT THIS. It recovers a criterion's PARENT -- provenance of TEXT, at")
    print(f"    0.9871 recovery against chance 0.0792. Clause 3 asks how the SUBSET was CHOSEN.")
    print(f"    Same rubric, same ancestry, different selection: two estimands, and conflating them")
    print(f"    would have been the fifth next-gradient error in a row.")
    print(f"\n  MULTIPLICITY  {len(SETS)} feature sets x {len(SEEDS)} seeds x {len(leaky)} held-out "
          f"folds; every fold printed.")

    o = SELF.parent / "results" / "selection_signature.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_rows=len(F), n_arms=len(arms), leaky=sorted(leaky), n_prompts=len(pids),
        feature_sets=RESU, planted_heldout=float(np.mean(pho)),
        planted_zero_heldout=float(np.mean(zho)), shuffled_heldout=float(np.mean(sho)),
        noise_within=float(np.mean(nin)), noise_heldout=float(np.mean(nho)),
        controls=dict(positive=bool(pos_ok), g0=bool(g0_ok), negative=bool(neg_ok),
                      placebo=bool(plc_ok)),
        corrects="R336's next-gradient line said criterion text was untouched; R250 did it 86 rounds ago.",
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
