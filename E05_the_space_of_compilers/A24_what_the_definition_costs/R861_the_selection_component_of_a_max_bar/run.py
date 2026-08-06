#!/usr/bin/env python3
"""
R861 · how much MDE does a MAX bar hide? — re-select the argmax inside the bootstrap.

⛔ WHY. R860 measured that a bar which is a MAXIMUM carries selection variability an MDE cannot see
if the argmax is fixed before resampling: there, over 1,820 subsets, the true MDE was **1.56×** the
fixed-bar proxy, moving a ratio from 1.358 to 0.870. R1387 then read R436's source and found the
same shape at a smaller scale: `bar_per = rule_per[best_rule]` is resampled WITH the arm (good), but
`best_rule = max(rule_mean, ...)` is chosen ONCE, OUTSIDE the bootstrap (the omission).

**R436's family is 30 rules, not 1,820, so the effect should be much smaller — but nobody has
measured it, and entry 1386 already overstated it once by importing R860's factor across a
60×-larger family.** This measures it instead.

⛔⛔ THE ARITHMETIC TRAP FIRED ON ME, IN THE ROUND WHOSE DOCSTRING INVOKED IT. The first version of
this file said: *"re-selecting the max inside each resample can only INCREASE the bar's bootstrap
variance, so `MDE_selective >= MDE_fixed` is a DERIVATION."* **The measurement returned 0.966.** A
quantity I labelled DERIVED — which by the standard's own definition means it could not have come
out otherwise — came out otherwise.

**The error, exactly.** A max has TWO consequences; I derived one and assumed the other:
  ⭐ the LEVEL rises — `max_k mean_b(R_k) >= mean_b(R_star)` for every resample. **This IS forced,
     and the run confirms it at 100.0% of 4,000 resamples.**
  ⛔ the VARIANCE does NOT follow. When the rank-1 rule dips on a resample, a DIFFERENT rule wins
     instead — so the max **CLIPS THE DOWNSIDE** and is LESS variable, not more. Measured:
     bar sd 0.004968 fixed -> 0.004606 selective, **ratio 0.927**.
  ⭐ Why this regime: rank1 `min_ttr` 0.4560 vs rank2 `max_len_chars` 0.4515 — **a gap of 0.0045
     against a bar sd of 0.0050.** The top rules are TIED relative to bootstrap noise, which is
     exactly when switching is frequent and clipping is strong.

**So the finding is the RATIO and its SIGN**, and the sign is the opposite of what three entries
assumed. The pre-registered question is unchanged: does the ratio exceed **1.23**, the factor that
would push the tightest published margin (1.84×, `topw_k8`) below this project's 1.5 floor.

ESTIMAND        `MDE_selective / MDE_fixed` for arm-versus-④'s-bar, where the bar is the max over
                R435's 30-rule criterion-free family.
IDENTIFICATION  exact; both MDEs are computable from released matrices and the same rule family.
SCOPE           population: prompts with 4 response texts and a human ranking
                instrument: A2 vs EVERY annotator (no draw, no seed)
                ⚠ R436 used 3 stable-seeded draws, so the ABSOLUTE MDEs here will differ from its
                  published ones. **The RATIO is instrument-internal and is what transfers** — that
                  is stated, not glossed.
                baseline:   the fixed-argmax MDE, i.e. R436's construction
WORLDS          A · ratio < 1.23 -> the omission is real but cannot move any published verdict
                B · ratio >= 1.23 -> it can move the tightest cell below the 1.5 floor
                ⭐ C · ratio < 1.00 -> the omission has the OPPOSITE sign: the fixed-argmax MDE is
                    CONSERVATIVE, and every published margin computed against it is UNDERSTATED.
                    ⚠ This world was NOT in the first draft, because I had "derived" it away.
KILL            CONDITIONAL, and BOTH arms must fire before the ratio is readable:
                  ① the fixed-argmax bar must reproduce R436's `best_rule` identity (`min_ttr`).
                     If the family does not reproduce the published winner, the two constructions
                     are not comparable.
                  ⭐ ② POSITIVE CONTROL: the argmax must ACTUALLY SWITCH across resamples. If it
                     never moves, the two constructions are IDENTICAL, the ratio is 1.000 by
                     construction, and a 0.966 would be a bug rather than a finding. **This arm was
                     added after the first run returned a number my derivation forbade** — the
                     cheapest way to tell "my algebra was wrong" from "my code is wrong", and it
                     had to be run before either could be reported. Exit 2 otherwise.
SEEDS           3 bootstrap seeds; the spread across them is reported, not hidden.
ARTIFACT        results/selection_component.json
IMPOSSIBLE      construct validity · cross-release.
"""
import itertools, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
import score as SC                                              # noqa: E402
R435 = next(ROOT.glob("E0*/A*/R435_*"), None)
import importlib.util                                            # noqa: E402
_s = importlib.util.spec_from_file_location("r435", R435 / "run.py")
r435 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r435)

L = ["A", "B", "C", "D"]
NBOOT, ZEFF = 4000, 2.802
ARMS = ["topw_k8", "coval_core", "topw_k4", "greedy_k4_fit1"]


def load_texts():
    t = {}
    for line in open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        g = {x.get("response_index"): " ".join(
            str(m.get("content") or "") for m in (x.get("messages") or [])
            if m.get("role") == "assistant") for x in (r.get("responses") or [])}
        if len(g) >= 4 and all(g.get(c) for c in L):
            t[r["prompt_id"]] = {c: g[c] for c in L}
    return t


def main() -> int:
    tg, _ = SC.load_targets()
    texts = load_texts()
    pids = sorted(set(texts) & set(tg) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([SC.cls(np.array(y, float)) for y, _ in tg[p]]) for p in pids}
    n = len(pids)
    print(f"  prompts {n} · rules {len(r435.RULES)} (R435's criterion-free family)")

    feats = {p: {c: r435.features(texts[p][c]) for c in L} for p in pids}
    R = np.array([[np.mean(SC.cls(np.array([(feats[p][c][key] if key != "__pos__" else L.index(c))
                                            for c in L], float) * (1.0 if sign > 0 else -1.0))
                           == H[p])
                   for p in pids] for _, key, sign in r435.RULES])
    names = [nm for nm, _, _ in r435.RULES]
    star = int(R.mean(1).argmax())
    rm = R.mean(1); order = np.argsort(-rm)
    print("  rule means, top 3: " + " · ".join(f"{names[i]} {rm[i]:.4f}" for i in order[:3])
          + f"   gap rank1-rank2 = {rm[order[0]]-rm[order[1]]:.4f}")
    print(f"  KILL CHECK  fixed-argmax best_rule = `{names[star]}` "
          f"(R436 published `min_ttr`)  {'PASS' if names[star]=='min_ttr' else 'FAIL'}")
    if names[star] != "min_ttr":
        print("\n  UNVERIFIED: the family does not reproduce the published winner, so the two")
        print("  constructions are not comparable. Exit 2, never 0.")
        return 2

    # ---- POSITIVE CONTROL: the two constructions must actually DIFFER --------------------------
    _rng = np.random.default_rng(11)
    _idx = _rng.integers(0, n, size=(NBOOT, n))
    _Rb = R[:, _idx]
    _ks = _Rb.mean(2).argmax(0)
    switch = float((_ks != star).mean())
    nwin = int(len(np.unique(_ks)))
    sw_ok = switch > 0.01
    print(f"  POSITIVE CONTROL  the argmax SWITCHES across resamples: {switch*100:.1f}% "
          f"({nwin} distinct winners)  {'PASS' if sw_ok else 'FAIL'}")
    print("    Without this the two constructions are the same object and the ratio is 1.000 by")
    print("    construction — a bug and a finding would print identically.")
    bf = _Rb[star].mean(1); bsel = _Rb[_ks, np.arange(NBOOT)].mean(1)
    hi_frac = float((bsel >= bf).mean())
    bar_sd_ratio = float(bsel.std() / bf.std())
    print(f"  MECHANISM  selective bar is HIGHER in {hi_frac*100:.1f}% of resamples (forced: max>=any)")
    print(f"             selective bar sd / fixed bar sd = {bar_sd_ratio:.3f}  "
          f"-> the max CLIPS THE DOWNSIDE, so it is LESS variable, not more")
    if not sw_ok:
        print("\n  UNVERIFIED: the argmax never moves; the two MDEs are one quantity. Exit 2.")
        return 2

    rows = []
    for a in ARMS:
        f = ROOT / "corebench" / "results" / f"sat_{a}.npz"
        if not f.exists():
            continue
        S = SC.load_sat(f)
        ks = [i for i, p in enumerate(pids) if p in S]
        A = np.full(n, np.nan)
        for i in ks:
            p = pids[i]
            A[i] = np.mean(SC.cls(SC.yvec(S[p], sorted({j for j, _ in S[p]}))) == H[p])
        m = np.isfinite(A)
        fixed, sel = [], []
        for sd in (11, 22, 33):
            rng = np.random.default_rng(sd)
            idx = rng.integers(0, n, size=(NBOOT, n))
            Ab = np.where(m[idx], np.nan_to_num(A)[idx], np.nan)
            Rb = R[:, idx]                                    # rules x NBOOT x n
            d_fix = np.nanmean(Ab - Rb[star], axis=1)         # bar FIXED outside
            k_sel = Rb.mean(2).argmax(0)                      # argmax RE-SELECTED per resample
            d_sel = np.nanmean(Ab - Rb[k_sel, np.arange(NBOOT)], axis=1)
            fixed.append(ZEFF * d_fix.std()); sel.append(ZEFF * d_sel.std())
        mf, ms = float(np.mean(fixed)), float(np.mean(sel))
        rows.append({"arm": a, "mde_fixed": mf, "mde_selective": ms, "ratio": ms / mf,
                     "fixed_seeds": fixed, "sel_seeds": sel})
        print(f"  {a:<16} MDE fixed {mf:.6f}  selective {ms:.6f}  ratio {ms/mf:.3f}"
              f"   (seed spread fixed {np.std(fixed):.2e}, sel {np.std(sel):.2e})")

    r = float(np.mean([x["ratio"] for x in rows]))
    world = "B" if r >= 1.23 else ("A" if r >= 1.0 else "C")
    print(f"\n  ⭐ mean ratio across {len(rows)} arms: {r:.3f}")
    print(f"  ⭐ WORLD {world}: " + {
        "B": "it CAN push the tightest published margin (1.84×) below the 1.5 floor",
        "A": "the omission is REAL but cannot move any published verdict — 1.84 / %.3f = %.2f, "
             "still above 1.5" % (r, 1.84 / r),
        "C": "the omission has the OPPOSITE SIGN — the fixed-argmax MDE is CONSERVATIVE, so every "
             "margin computed against it is UNDERSTATED: 1.84 / %.3f = %.2f, FURTHER above 1.5"
             % (r, 1.84 / r)}[world])
    print("     ⛔ I called this direction FORCED. It was not: a max raises the LEVEL (forced) and")
    print("        CLIPS the downside (not forced, and it dominates here). The derivation was a")
    print("        guess wearing a derivation's label, caught only because the number contradicted it.")
    print("     ⛔ AND R860's `1.56×` WAS NEVER A SELECTION COMPONENT. Its own artifact records")
    print("        replaces_proxy = {entry: 1383, proxy_mde: 0.0066309665} — 1.56 = 0.0103435 /")
    print("        0.0066310, the ratio between the RIGHT subset's MDE and a DIFFERENT subset's.")
    print("        A borrowed-denominator correction. Entry 1386 imported it as a selection factor;")
    print("        entry 1387 corrected its MAGNITUDE and accepted the MISLABELLING. This is the")
    print("        first round that measured the thing all three entries were talking about.")
    print("     ⚠ SCOPE, and it is the same trap: 0.966 is the 30-RULE family. R860's own MDE has")
    print("        the identical omission over 1,820 subsets, and whether the sign holds there is")
    print("        UNMEASURED. It is not transferred here.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "n_prompts": n, "n_rules": len(r435.RULES),
               "best_rule": names[star], "arms": rows, "mean_ratio": r, "world": world,
               "threshold_that_would_matter": 1.23,
               "controls": {"best_rule_reproduced": names[star] == "min_ttr",
                            "argmax_switch_rate": switch, "distinct_winners": nwin,
                            "selective_bar_higher_frac": hi_frac,
                            "bar_sd_ratio_sel_over_fixed": bar_sd_ratio},
               "derivation_that_was_refuted":
                   "MDE_selective >= MDE_fixed; a max raises the LEVEL (forced) but CLIPS the "
                   "downside, so it is LESS variable, not more",
               "r860_156_was_not_a_selection_component":
                   "R860/results/exact_mde.json records replaces_proxy.proxy_mde=0.0066309665; "
                   "1.56 = 0.0103435/0.0066310, a borrowed-denominator correction",
               "not_transferred": "the 1,820-subset family's own sign is UNMEASURED"},
              open(OUT / "selection_component.json", "w"), indent=2)
    print(f"\n  artifact: results/selection_component.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
