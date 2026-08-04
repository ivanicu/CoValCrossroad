"""R338 — does R337's selection signature detect LEAKAGE, or the four rules the page happens to label?

R337 got held-out-ARM AUC 0.866 from label-free features of the selected criterion set. But every
positive it trained on is one of the four arms R294 annotates leaky, and those four share a family:
`oracle_k4`, `oracle_k4_fit1`, `greedy_k4_fit1`, `indep_k4_fit1` -- all built by select_core.py's
fitted rules. Holding out one ARM still leaves three arms of the SAME MECHANISM in the training set,
so a high AUC is equally consistent with:

    W-LEAKAGE   the features detect label-driven selection as such
    W-RULE      the features detect THOSE RULES, and would miss a leak produced any other way

A held-out arm cannot separate those. A held-out MECHANISM can, and R335 already manufactured one:
an oracle over a 300-subset search fitted on a controlled fraction of the parity-1 annotators. It is
label-driven selection by a rule the classifier has never seen.

⚠ AND THE CONTROL THAT DECIDES WHETHER A FAILURE IS READABLE. If the features cannot separate the
manufactured mechanism EVEN WHEN TRAINED ON IT, then a failure to transfer says nothing about
transfer -- it says the mechanism has no signature in these features. So the round trains on
manufactured arms and tests on held-out manufactured SEEDS first. Without that number, W-RULE would
be silence wearing a verdict's clothes.

⛔ ARITHMETIC DECLARED. Nothing here is forced: the classifier's weights come from one population and
are applied to another, and either outcome is available. But note one asymmetry that is NOT evidence:
the manufactured arms are k=4 by construction while the page's arms span k=1..15, so any feature
that tracks k would transfer trivially. k is therefore EXCLUDED from the feature set, and the round
reports the AUC with and without that exclusion so the exclusion can be checked rather than trusted.

ESTIMAND      (i) AUC of an R337-trained classifier on R335's manufactured arms, clean (dose 0) vs
              leaky (dose >= 0.10); (ii) the classifier's score as a function of dose; (iii) the
              same AUC when trained ON manufactured arms and tested on held-out manufactured seeds,
              which bounds what any transfer result can mean.
IDENTIFICATION Exact for (iii). For (i) the training population is 4 leaky arms of one family, so a
              LOW transfer AUC is identified as `these features do not transfer to this mechanism`
              and NOT as `no selection signature exists` -- one mechanism cannot refute a class.
SCOPE         population R294's arms with a committed core json, plus 18 manufactured arms · 968
              CoVal prompts with >=1 annotator in each parity · features from the rubric and the
              judge's satisfaction only · regime k=4 for manufactured arms.
WORLDS        W-LEAKAGE  transfer AUC >= 0.75 and the score rises with dose -> the signature is
                         about label-driven selection, not about four particular rules, and clause
                         3 can carry a computed test that generalises.
              W-RULE     transfer AUC ~ 0.5 while the trained-on-manufactured control is high ->
                         R337's 0.866 was detecting the rule family. Clause 3's test would only
                         catch leaks built the way select_core.py builds them.
              W-BLIND    the trained-on-manufactured control is ALSO low -> these features cannot
                         see this mechanism at all, and the transfer number is unreadable.
KILL          pre-registered, conditional on the controls:
                trained-on-manufactured AUC < 0.70              -> W-BLIND
                else transfer AUC >= 0.75                        -> W-LEAKAGE
                else                                             -> W-RULE
POSITIVE CTRL train on manufactured, test on HELD-OUT manufactured seeds. Must be high, or nothing
              about transfer is readable. It FAILS at g=0: dose-0 manufactured arms held out against
              each other must give AUC ~ 0.5.
NEGATIVE CTRL shuffle the DOSE labels among manufactured arms and re-run the transfer evaluation;
              AUC must fall to chance. Shuffling rows would leave arm identity intact.
SHAM          the k feature, excluded from the main set and reported separately: manufactured arms
              are all k=4 while the page's arms span k=1..15, so a k-tracking feature transfers for
              a reason that has nothing to do with leakage. Both AUCs are printed.
PLACEBO       manufactured dose-0 arms scored against each other: AUC ~ 0.5.
NOISE FLOOR   across-seed spread of every AUC, 3 seeds.
MULTIPLICITY  2 training populations x 2 feature sets x 3 seeds; every cell printed.
SPECIFICATION the dose axis is published whole, including doses where the score does not separate.
SEEDS         3.
ARTIFACT      results/rule_transfer.json with source hash.
IMPOSSIBLE    a second LEAK MECHANISM from the release itself. The release annotates one family; the
              second mechanism here is manufactured, so `generalises to any leak` remains out of
              reach and only `generalises beyond one family` is testable.
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, re, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402

SELF = pathlib.Path(__file__).resolve()
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
PAIRS = list(itertools.combinations(range(4), 2))
IIP = np.array([i for i, _ in PAIRS]); JJP = np.array([j for _, j in PAIRS])
SEEDS = (0, 1, 2)
TOK = re.compile(r"[a-z0-9]+")
K, NSUB = 4, 300
DOSES = (0.0, 0.10, 0.25, 0.50, 0.75, 1.00)


def load_json(pat):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def auc(y, s):
    pos, neg = s[y == 1], s[y == 0]
    if not len(pos) or not len(neg):
        return float("nan")
    return float((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean())


def fit_logit(X, y, iters=300, lr=0.5):
    w = np.zeros(X.shape[1]); b = 0.0
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(X @ w + b)))
        w -= lr * (X.T @ (p - y) / len(y)); b -= lr * float((p - y).mean())
    return w, b


def main() -> int:
    r294 = load_json("R294_*")
    if r294 is None:
        print("  UNRUNNABLE: R294 absent."); return 2
    rows = r294["rows"]
    RES = ROOT / "corebench" / "results"
    tg, _ = load_targets()
    FULL = load_sat(RES / "sat_full.npz")
    from covalx.judge import load_join                                   # noqa: E402
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    rub = {}
    for p_, _pr, r in joined:
        items = r.get("coval_full") or []
        if items:
            rub[p_] = [(i.get("criterion", ""),
                        float(np.mean([sc["score"] for sc in (i.get("scores") or [])]))
                        if i.get("scores") else 0.0) for i in items]

    arms = [a for a in sorted(rows) if (RES / f"core_{a}.json").exists()]
    core = {a: json.loads((RES / f"core_{a}.json").read_text()) for a in arms}
    pids = sorted(set(FULL) & set(rub) & {p for p in tg if len(tg[p]) >= 2
                                          and len(tg[p][1::2]) >= 1}
                  & set.intersection(*(set(core[a]) for a in arms)))
    if len(pids) < 50:
        print(f"  UNRUNNABLE: only {len(pids)} prompts."); return 2
    N = len(pids)
    H1 = [np.array([cls(np.array(t[0], float)) for t in tg[p][1::2]], float) for p in pids]
    SATM = {p: np.array([[FULL[p][(i, x)] for x in "ABCD"]
                         for i in sorted({i for i, _ in FULL[p]})], float) for p in pids}
    nrub = np.array([len(rub[p]) for p in pids])
    leaky = {a for a in arms if not rows[a]["ok3"]}
    print(f"  {len(arms)} page arms ({len(leaky)} annotated leaky) · {N} prompts · "
          f"{len(DOSES)}x{len(SEEDS)} manufactured arms\n")

    def featvec(sel_txt, p, n, with_k=False):
        pool = rub[p]; pool_txt = [t for t, _ in pool]
        pw = np.array([w for _, w in pool], float); M = SATM[p]
        idx = [pool_txt.index(t) for t in sel_txt if t in pool_txt]
        if idx:
            w = pw[idx]; sm = M[[i for i in idx if i < len(M)]] if len(M) else np.zeros((1, 4))
            posn = np.array(idx, float) / max(len(pool_txt) - 1, 1)
        else:
            w = np.zeros(1); sm = np.zeros((1, 4)); posn = np.zeros(1)
        toks = [set(TOK.findall(t.lower())) for t in sel_txt]
        jac = [len(x & y) / max(len(x | y), 1) for x, y in itertools.combinations(toks, 2)] or [0.0]
        v = [float(w.mean()), float(w.max()), float(w.std()), float(sm.std(axis=1).mean()),
             float(sm.mean()), float(posn.mean()), float(posn.std()),
             float(np.mean([len(t) for t in sel_txt])), float(np.mean([len(x) for x in toks])),
             float(np.mean(jac)), float(np.max(jac)),
             float(len(idx)) / max(len(sel_txt), 1)]
        return v + ([float(len(sel_txt))] if with_k else [])

    # ---- the page's arms ---------------------------------------------------------------------------
    def page_rows(with_k):
        X, Y = [], []
        for a in arms:
            for n, p in enumerate(pids):
                st = [it["criterion"] if isinstance(it, dict) else str(it) for it in core[a][p]]
                X.append(featvec(st, p, n, with_k)); Y.append(1 if a in leaky else 0)
        return np.array(X, float), np.array(Y)

    # ---- R335's manufactured mechanism, selections rebuilt ------------------------------------------
    def manufactured(with_k):
        X, Y, D, S = [], [], [], []
        for f_ in DOSES:
            for s_ in SEEDS:
                rng = np.random.default_rng(120_000 + 7919 * s_ + int(f_ * 1000))
                for n, p in enumerate(pids):
                    sels = np.stack([rng.choice(nrub[n], K, replace=False) for _ in range(NSUB)])
                    Ymat = SATM[p][sels].sum(axis=1)
                    C = np.sign(Ymat[:, IIP] - Ymat[:, JJP])
                    if f_ <= 0.0:
                        pick = int(rng.integers(NSUB))
                    else:
                        take = max(1, int(round(f_ * len(H1[n]))))
                        fit = H1[n][rng.choice(len(H1[n]), take, replace=False)]
                        pick = int(np.argmax((C[:, None, :] == fit[None, :, :]).mean(axis=(1, 2))))
                    st = [rub[p][i][0] for i in sels[pick]]
                    X.append(featvec(st, p, n, with_k)); Y.append(0 if f_ <= 0 else 1)
                    D.append(f_); S.append(s_)
        return np.array(X, float), np.array(Y), np.array(D), np.array(S)

    print("  building feature rows (page + manufactured) …")
    OUT = {}
    for with_k, tag in ((False, "no k"), (True, "with k (SHAM)")):
        Xp, Yp = page_rows(with_k)
        Xm, Ym, Dm, Sm = manufactured(with_k)
        mu, sd = Xp.mean(0), Xp.std(0) + 1e-9
        w, b = fit_logit((Xp - mu) / sd, Yp.astype(float))
        sm_score = ((Xm - mu) / sd) @ w + b
        transfer = auc(Ym, sm_score)
        # control: train ON manufactured, test on held-out SEEDS
        ho = []
        for s_ in SEEDS:
            tr, te = Sm != s_, Sm == s_
            m2, d2 = Xm[tr].mean(0), Xm[tr].std(0) + 1e-9
            w2, b2 = fit_logit((Xm[tr] - m2) / d2, Ym[tr].astype(float))
            ho.append(auc(Ym[te], ((Xm[te] - m2) / d2) @ w2 + b2))
        OUT[tag] = dict(transfer=transfer, trained_on_manufactured=float(np.mean(ho)),
                        ho_folds=[round(x, 3) for x in ho],
                        dose_score={str(f_): float(sm_score[Dm == f_].mean()) for f_ in DOSES})
        print(f"\n  {tag}:  transfer AUC {transfer:.3f}   trained-on-manufactured "
              f"{np.mean(ho):.3f} {[round(x,3) for x in ho]}")
        print(f"    score by dose: " + "  ".join(
            f"{f_:.2f}→{sm_score[Dm == f_].mean():+.2f}" for f_ in DOSES))

    Xm, Ym, Dm, Sm = manufactured(False)
    Xp, Yp = page_rows(False)
    mu, sd = Xp.mean(0), Xp.std(0) + 1e-9
    w, b = fit_logit((Xp - mu) / sd, Yp.astype(float))
    score = ((Xm - mu) / sd) @ w + b
    transfer = OUT["no k"]["transfer"]; on_man = OUT["no k"]["trained_on_manufactured"]

    # ---- NEGATIVE · shuffle DOSE labels among manufactured arms ------------------------------------
    rng = np.random.default_rng(31)
    keys = sorted({(f_, s_) for f_, s_ in zip(Dm, Sm)})
    lab = {k_: (0 if k_[0] <= 0 else 1) for k_ in keys}
    vals = list(lab.values()); rng.shuffle(vals)
    newlab = dict(zip(keys, vals))
    Ysh = np.array([newlab[(f_, s_)] for f_, s_ in zip(Dm, Sm)])
    neg = auc(Ysh, score)
    neg_ok = abs(neg - 0.5) < 0.20
    print(f"\n  NEGATIVE CTRL  DOSE labels shuffled among manufactured arms: AUC {neg:.3f}  "
          f"{'PASS' if neg_ok else 'FAIL'}")

    # ---- PLACEBO · dose-0 arms against each other ----------------------------------------------------
    z = Dm <= 0
    plc = auc((Sm[z] == SEEDS[0]).astype(int), score[z])
    plc_ok = abs(plc - 0.5) < 0.15
    print(f"  PLACEBO        manufactured dose-0 arms scored against each other: AUC {plc:.3f}  "
          f"{'PASS' if plc_ok else 'FAIL'}")

    # ---- g=0 for the positive control --------------------------------------------------------------
    # ⚠ v1 held out ONE SEED's dose-0 rows and asked the classifier to predict `seed == SEEDS[0]`.
    # Every row in a held-out fold shares that seed, so the test label is CONSTANT and AUC is nan.
    # The control compared a label that could not vary -- malformed, and it returned neither pass
    # nor fail. Correct form: two dose-0 arms differing ONLY by draw, split by PROMPT so both
    # classes appear in the test set. They should be indistinguishable, i.e. AUC ~ 0.5.
    z0 = (Dm <= 0) & np.isin(Sm, SEEDS[:2])
    y0 = (Sm[z0] == SEEDS[0]).astype(int)
    X0 = Xm[z0]
    rng0 = np.random.default_rng(77)
    perm0 = rng0.permutation(len(y0)); cut0 = len(y0) // 2
    m0, d0 = X0[perm0[:cut0]].mean(0), X0[perm0[:cut0]].std(0) + 1e-9
    w0, b0 = fit_logit((X0[perm0[:cut0]] - m0) / d0, y0[perm0[:cut0]].astype(float))
    g0v = auc(y0[perm0[cut0:]], ((X0[perm0[cut0:]] - m0) / d0) @ w0 + b0)
    g0 = [g0v]
    g0_ok = np.isfinite(g0v) and abs(g0v - 0.5) < 0.15
    print(f"  POSITIVE @ g=0 two dose-0 arms differing only by DRAW, split by prompt: "
          f"AUC {g0v:.3f}  {'PASS — indistinguishable, as they must be' if g0_ok else 'FAIL'}")

    ctrl = neg_ok and plc_ok and g0_ok
    print("\n  " + "=" * 78)
    print(f"  CONTROLS  negative={neg_ok}  placebo={plc_ok}  g0={g0_ok}  -> "
          f"{'evaluate' if ctrl else 'UNVERIFIED'}")
    if not ctrl:
        world = "UNVERIFIED"
        print("  -> UNVERIFIED. A control misbehaved; the transfer number is not readable.")
    elif on_man < 0.70:
        world = "W-BLIND"
        print(f"  -> W-BLIND. Trained ON the manufactured mechanism the AUC is only {on_man:.3f}, so")
        print("     these features cannot see this mechanism at all and the transfer number says")
        print("     nothing about transfer. A low transfer AUC here would have been silence.")
    elif transfer >= 0.75:
        world = "W-LEAKAGE"
        print(f"  -> W-LEAKAGE. Transfer AUC {transfer:.3f} onto a leak mechanism the classifier")
        print(f"     never saw, with the trained-on-manufactured control at {on_man:.3f}. The")
        print("     signature is about label-driven SELECTION, not about four particular rules.")
    else:
        world = "W-RULE"
        print(f"  -> W-RULE. Transfer AUC {transfer:.3f} while the same features trained ON the")
        print(f"     manufactured mechanism reach {on_man:.3f}. So the mechanism IS visible to these")
        print("     features and R337's 0.866 did not carry to it: what transferred across held-out")
        print("     ARMS was the rule FAMILY, because holding out one of four arms leaves three of")
        print("     the same mechanism in training. Clause 3's test would catch leaks built the way")
        print("     select_core.py builds them and is unproven against any other route.")
    print("  " + "=" * 78)
    print(f"\n  ⚠ SHAM (the k feature): manufactured arms are all k=4 while the page's span k=1..15,")
    print(f"    so a k-tracking feature transfers for a reason unrelated to leakage. Excluded from")
    print(f"    the main set; with it, transfer AUC is {OUT['with k (SHAM)']['transfer']:.3f} against")
    print(f"    {transfer:.3f} without. The exclusion is checkable rather than trusted.")
    print(f"\n  MULTIPLICITY  2 training populations x 2 feature sets x {len(SEEDS)} seeds, all printed.")

    o = SELF.parent / "results" / "rule_transfer.json"
    o.parent.mkdir(parents=True, exist_ok=True)
    o.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(SELF.read_bytes()).hexdigest()[:16], world=world,
        n_prompts=N, n_page_arms=len(arms), leaky=sorted(leaky), doses=list(DOSES),
        results=OUT, transfer=transfer, trained_on_manufactured=on_man,
        negative_shuffled=neg, placebo=plc, g0=float(np.mean(g0)),
        controls=dict(negative=bool(neg_ok), placebo=bool(plc_ok), g0=bool(g0_ok)),
    ), indent=1))
    print(f"\n  artifact {o.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
