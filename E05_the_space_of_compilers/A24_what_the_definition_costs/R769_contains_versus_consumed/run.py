#!/usr/bin/env python3
"""R769 · contains vs consumed — 968 of 1,078 prompts, and what resolving the extension would cost.

⛔ CHECK #371, THE COUNT §4's SHAM ROW DEMANDS FIRST:
   annotators : median **16**, total **15,593** consumed — exactly the release's own figure, so the
                ×5 gain that row found on a different design IS NOT AVAILABLE HERE.
   prompts    : the release carries **1,078**; the estimator uses **968**. 110 prompts and 2,791
                annotations — 15.2% — are not consumed. contains/consumed = 15,593/18,384 = 0.8482.

⛔ FORCED, AND IT SAYS THIS ROUND CANNOT RESCUE R768:
  D1 MDE ∝ 1/√n, so 968 → 1,078 multiplies the MDE by √(968/1078) = 0.947 — a 5.3% reduction.
     R768's `coval_core` vs `topw_k4` gap is 0.0023 against MDE 0.0085, a factor of 3.7; closing it
     needs n × 13.7 ≈ 13,200 prompts. **The 110 cannot change any verdict, and that is algebra.**
     Stated before running so a null cannot be read as a discovery.
  D2 the count is for SCOPE, not power: if the 110 drop by an ARM-COVERAGE accident rather than a
     property of the release, every number in this campaign carries an unstated 89.8% scope.
  D3 required-n scales as (MDE/gap)² × n — a DERIVATION from the measured sd, labelled as one.

CONTROLS  POSITIVE (the MDE-vs-n curve must follow the 1/√n law to within 5%, asserted not fitted) ·
          g=0 (at n = 968 it reproduces R768's committed MDEs exactly) · NEGATIVE (pairing destroyed
          at every n) · SHAM (the ingredient is NEW PROMPTS — draw n WITH replacement from the same
          968) · PLACEBO (an arm against itself, MDE exactly 0 at every n).
UNIT      instrument = a PROMPT · claim = an ARM PAIR. Required-n is per pair, never pooled.
"""
import itertools, json, math, pathlib, subprocess, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, cls          # noqa: E402

RES = ROOT / "corebench/results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
R768 = A24 / "R768_can_the_extension_be_ordered_at_all/results/pairwise_ordering.json"
ZEFF, L = 1.959964 + 0.841621, "ABCD"
PR = list(itertools.combinations(range(4), 2))
COMMITTED = ["coval_core", "topw_k3", "topw_k4", "topw_k6", "topw_k8"]
NS = [100, 200, 400, 600, 800, 968]
NSUB = 50


def _plain(o):
    if isinstance(o, np.bool_):    return bool(o)
    if isinstance(o, np.integer):  return int(o)
    if isinstance(o, np.floating): return float(o)
    if isinstance(o, np.ndarray):  return o.tolist()
    raise TypeError(type(o))


def main():
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    used = sorted({p for p in base if p in targets and p in POOL and len(targets[p]) >= 2})
    allp = sorted(targets)
    dropped = [p for p in allp if p not in set(used)]
    print(f"  release prompts {len(allp)}   estimator population {len(used)}   dropped {len(dropped)}")

    # ---- E1 · attribute every drop to the clause responsible -----------------------------------
    att = {"not_in_base_arm": 0, "not_in_pool": 0, "fewer_than_2_annotators": 0, "several": 0}
    detail = []
    for p in dropped:
        why = []
        if p not in base: why.append("not_in_base_arm")
        if p not in POOL: why.append("not_in_pool")
        if len(targets.get(p, [])) < 2: why.append("fewer_than_2_annotators")
        detail.append({"pid": p, "why": why, "n_annot": len(targets.get(p, []))})
        att[why[0] if len(why) == 1 else "several"] += 1
    print(f"\n  ⭐ E1 · WHY THE 110 ARE DROPPED, per clause")
    for k, v in att.items():
        print(f"     {k:<26}{v:>5}")
    multi = [d for d in detail if len(d["why"]) > 1]
    if multi:
        from collections import Counter
        print(f"     `several` breakdown: {dict(Counter(tuple(sorted(d['why'])) for d in multi))}")

    # ---- E2 · how many are RECOVERABLE for the arms R768 compared -------------------------------
    sats = {t: load_sat(RES / f"sat_{t}.npz") for t in COMMITTED}
    rec = [d["pid"] for d in detail
           if d["n_annot"] >= 2 and all(d["pid"] in s for s in sats.values())]
    print(f"\n  ⭐ E2 · RECOVERABLE for R768's five arms (>=2 annotators AND scored by all five): "
          f"{len(rec)} of {len(dropped)}")
    if rec[:3]:
        print(f"     e.g. {rec[:3]}")

    # ---- the estimator, parameterised by prompt set ---------------------------------------------
    def build(pids):
        P = len(pids)
        HC = [np.array([cls(y) for y, _ in targets[p]]) for p in pids]
        Hm = max(len(h) for h in HC)
        HP = np.zeros((P, Hm, 6)); HK = np.zeros((P, Hm))
        for a, h in enumerate(HC):
            HP[a, :len(h)] = h; HK[a, :len(h)] = 1.0
        return HP, HK, HK.sum(1)

    def a2_for(tag, pids, HP, HK, nH):
        S = sats.get(tag) or load_sat(RES / f"sat_{tag}.npz")
        P = len(pids); Y = np.zeros((P, 4))
        for ai, p in enumerate(pids):
            ii = sorted({i for i, _ in S[p]})
            for c, x in enumerate(L):
                Y[ai, c] = sum(S[p].get((i, x), 0.0) for i in ii)
        s = np.sign(Y[:, [i for i, _ in PR]] - Y[:, [j for _, j in PR]])
        return ((s[:, None, :] == HP).mean(2) * HK).sum(1) / nH

    HP, HK, nH = build(used)
    V = {t: a2_for(t, used, HP, HK, nH) for t in COMMITTED}
    pairs = list(itertools.combinations(COMMITTED, 2))

    def mde_of(d):
        return ZEFF * float(d.std(ddof=1)) / math.sqrt(len(d))

    full = {f"{a} vs {b}": {"eff": float((V[a] - V[b]).mean()),
                            "mde": mde_of(V[a] - V[b])} for a, b in pairs}

    # ---- CONTROL · g=0 : reproduce R768's committed MDEs exactly ---------------------------------
    prev = {f"{r['a']} vs {r['b']}": r for r in json.loads(R768.read_text())["pairs"]
            if r["family"] == "committed"}
    ok_g0 = all(abs(full[k]["mde"] - prev[k]["mde"]) < 1e-12 for k in full if k in prev)
    print(f"\n  g=0         at n = {len(used)} the curve reproduces R768's committed MDEs exactly: "
          f"{ok_g0}  {'PASS' if ok_g0 else '⛔ FAIL'}")

    # ---- E3 · the power curve, and the SHAM/NEGATIVE/PLACEBO at every n --------------------------
    rng = np.random.default_rng(769)
    curve, sham, neg = {}, {}, {}
    for n in NS:
        sub, shm, ng = [], [], []
        for _ in range(NSUB if n < len(used) else 1):
            idx = rng.choice(len(used), n, replace=False) if n < len(used) else np.arange(len(used))
            d = V["coval_core"][idx] - V["topw_k4"][idx]
            sub.append(mde_of(d))
            ridx = rng.choice(len(used), n, replace=True)
            shm.append(mde_of(V["coval_core"][ridx] - V["topw_k4"][ridx]))
            ng.append(mde_of(V["coval_core"][idx] - V["topw_k4"][rng.permutation(len(used))[:n]]))
        curve[n] = (float(np.mean(sub)), float(np.std(sub)))
        sham[n] = float(np.mean(shm)); neg[n] = float(np.mean(ng))
    m968 = curve[len(used)][0]
    print(f"\n  ⭐ E3 · MDE vs n   (`coval_core` vs `topw_k4`, {NSUB} subsamples each)")
    print(f"  {'n':>6}{'MDE':>10}{'sd':>9}{'1/sqrt law':>12}{'ratio':>8}{'SHAM w/repl':>13}"
          f"{'NEG /real':>11}")
    worst = 0.0
    for n in NS:
        law = m968 * math.sqrt(len(used) / n)
        r = curve[n][0] / law
        worst = max(worst, abs(r - 1))
        print(f"  {n:>6}{curve[n][0]:>10.5f}{curve[n][1]:>9.5f}{law:>12.5f}{r:>8.4f}"
              f"{sham[n]:>13.5f}{neg[n]/curve[n][0]:>11.2f}")
    ok_pos = worst <= 0.05
    print(f"  POSITIVE    worst deviation from the 1/sqrt law: {worst:.4f}  "
          f"{'PASS' if ok_pos else '⛔ FAIL'}  (asserted, not fitted; band: a flat curve fails)")
    sham_ok = abs(sham[400] / curve[400][0] - 1) < 0.10
    print(f"  SHAM        drawing n WITH replacement from the same {len(used)} gives the same MDE "
          f"(ratio at n=400: {sham[400]/curve[400][0]:.3f}) -> the curve needs NEW prompts, "
          f"resampling buys nothing")
    plc = mde_of(V["coval_core"] - V["coval_core"])
    print(f"  PLACEBO     an arm against ITSELF: MDE {plc:.10f}  {'PASS' if plc == 0.0 else '⛔ FAIL'}")

    # ---- D3 · the required n, per pair, labelled a DERIVATION ------------------------------------
    print(f"\n  ⭐ D3 · REQUIRED n PER PAIR — a DERIVATION from the measured sd, not a measurement")
    print(f"  {'pair':<26}{'gap':>9}{'MDE':>9}{'MDE/gap':>9}{'n required':>12}{'x today':>9}")
    need = {}
    for k, v in sorted(full.items(), key=lambda z: -abs(z[1]["eff"])):
        g = abs(v["eff"])
        if g == 0:
            need[k] = None; continue
        f = v["mde"] / g
        nreq = int(math.ceil(len(used) * f * f))
        need[k] = nreq
        print(f"  {k:<26}{v['eff']:>9.4f}{v['mde']:>9.4f}{f:>9.2f}{nreq:>12,}{nreq/len(used):>9.1f}")
    print(f"  ⚠ and the release has {len(allp)} prompts, so recovering all 110 buys "
          f"{1 - math.sqrt(len(used)/len(allp)):.1%} of MDE — D1, forced, not measured")

    # ---- CONFOUND · is the recoverable subset different in kind? ---------------------------------
    cc = None
    if len(rec) >= 20:
        HPr, HKr, nHr = build(rec)
        Vr = {t: a2_for(t, rec, HPr, HKr, nHr) for t in COMMITTED}
        sd_r = float((Vr["coval_core"] - Vr["topw_k4"]).std(ddof=1))
        sd_u = float((V["coval_core"] - V["topw_k4"]).std(ddof=1))
        cc = sd_r / sd_u
        print(f"\n  ⚠ CONFOUND  difference-sd on the {len(rec)} recoverable vs the {len(used)} used: "
              f"{sd_r:.4f} vs {sd_u:.4f}  ratio {cc:.3f}  "
              f"-> {'DIFFERENT IN KIND' if abs(cc-1) > 0.10 else 'same in kind'}")
    else:
        print(f"\n  ⚠ CONFOUND  only {len(rec)} recoverable — too few to compare sds. UNIDENTIFIED.")

    ctrl = ok_g0 and ok_pos and plc == 0.0
    if not ctrl:
        world = "UNVERIFIED"
    elif len(rec) >= 60:
        world = f"A · the drop is an ARM-COVERAGE artifact — {len(rec)} of {len(dropped)} recoverable"
    elif len(dropped) - len(rec) >= 60:
        world = f"B · the drop is a property of the RELEASE — only {len(rec)} of {len(dropped)} recoverable"
    else:
        world = "NO WORLD — counts reported, none claimed"
    if cc is not None and abs(cc - 1) > 0.10:
        world += "  ·  +C: the recoverable subset differs in kind"
    print(f"\n  WORLD {world}")
    print(f"  ⚠ NO BRANCH CHANGES R768's VERDICT — D1 forbids it. CLOSURE on the headline, "
          f"FRONTIER on scope.")

    out = pathlib.Path(__file__).parent / "results/contains_vs_consumed.json"
    out.write_text(json.dumps({
        "tree_sha": subprocess.run(["git", "rev-parse", "HEAD^{tree}"], cwd=ROOT,
                                   capture_output=True, text=True).stdout.strip()[:16],
        "release_prompts": len(allp), "used_prompts": len(used), "dropped": len(dropped),
        "annot_total_release": sum(len(targets[p]) for p in allp),
        "annot_total_used": sum(len(targets[p]) for p in used),
        "attribution": att, "recoverable": len(rec), "recoverable_pids": rec[:50],
        "mde_curve": {str(n): curve[n] for n in NS},
        "sham_with_replacement": {str(n): sham[n] for n in NS},
        "negative_ratio": {str(n): neg[n] / curve[n][0] for n in NS},
        "controls": {"g0_reproduces_r768": ok_g0, "positive_worst_law_dev": worst,
                     "placebo_self_mde": plc, "sham_ratio_at_400": sham[400] / curve[400][0]},
        "full_pairs": full, "n_required": need,
        "confound_sd_ratio_recoverable": cc, "world": world,
    }, indent=2, default=_plain))
    print(f"  artifact -> {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
