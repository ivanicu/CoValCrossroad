"""R412 -- the within-conversation clustering that decides between 4.57x and 2.50x.

R411 found the second-corpus replication is powered at 4.57x if the independent unit is the
INTERACTION and marginal at 2.50x if it is the CONVERSATION, and its NEXT said to measure the
within-conversation correlation.

⛔ THAT NEXT NAMES A QUANTITY THAT NEEDS THE JUDGE, WHICH IS THE THIRD OF MY OWN CLOSING SENTENCES IN
   A ROW WITH AN UNEXAMINED STEP. The outcome whose clustering sets the design effect is "did the arm
   pick the `if_chosen` response", and no arm has been run on this corpus. Its ICC is NOT measurable
   here, and saying "measure it" made an unavailable thing sound like a task.

⛔ AND R411's OWN RANGE WAS ALREADY THE WHOLE RANGE -- A DERIVATION I DID NOT NOTICE WHILE WRITING IT.
   With DEFF = 1 + (m-1)*ICC and m = 27,172/8,011 = 3.39 interactions per conversation, ICC = 0 gives
   n_eff = 26,789 and ICC = 1 gives n_eff = 7,900. Those are exactly R411's two endpoints. So the
   "range whose ends imply opposite decisions" was not two candidate designs -- it was ICC in [0, 1]
   with the interior left blank, and the interior is what this round fills.

⭐ WHAT IS MEASURABLE, AND IT IS THE RIGHT PROXY RATHER THAN A CONVENIENT ONE. The outcome inherits its
   clustering from the DATA. Two observable interaction-level quantities carry it:
     (a) `score` -- if a user rates consistently within a conversation, the outcome does too;
     (b) THE WINNING MODEL'S IDENTITY -- if the same model keeps winning inside a conversation, an arm
         that happens to favour that model is right repeatedly, which is the outcome's clustering
         almost directly.
   (b) is the closer proxy and is reported as the headline; (a) is reported beside it because two
   proxies disagreeing is information and one alone is a guess.

⚠ AND A PROXY IS NOT THE OUTCOME. This round reports the clustering of the DATA the outcome is built
  from, not of the outcome. It narrows the range; it does not close it, and the verdict says so.

ESTIMAND        (A) the one-way ICC of `score` across conversations;
                (B) the one-way ICC of the winning model's identity across conversations;
                (C) the implied design effect and the resulting power ratio, for each.

IDENTIFICATION  (A) and (B) exact given the release. (C) exact given (A)/(B) and the DEFF formula,
                which is a DERIVATION. NOT identified: the outcome's own ICC, which needs the judge.

SCOPE           population: second-corpus conversations with >= 2 interactions · instrument: one-way
                ANOVA ICC · baseline: a within-corpus shuffle null · regime: no judge, no re-scoring.

WORLDS
  W-LOW-ICC   both proxies < 0.15, so DEFF < 1.4 and the ratio stays above 3.5. The replication is
              powered and R411's marginal reading came from assuming the worst.
  W-HIGH-ICC  either proxy > 0.5, so DEFF > 2.2 and the ratio falls under 3. The replication is
              marginal and must be re-scoped before it is run.
  W-MID       between; the ratio is reported as an interval and the decision is a judgement the
              data cannot make for me.

PREDICTION MATRIX
  W-LOW-ICC  -> max(ICC_a, ICC_b) < 0.15
  W-HIGH-ICC -> max(ICC_a, ICC_b) > 0.50
  W-MID      -> between, interval reported

PRE-REGISTERED KILL -- conditional on both controls, never on the ICC alone.
    if synthetic_high_icc_recovered and synthetic_zero_icc_returns_near_zero:
        by max(ICC_a, ICC_b) as above
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  SYNTH (+)    a synthetic corpus built with ICC = 0.80 must be recovered within 0.10. Without it a
               low ICC below cannot be told from an estimator that always returns low.
  SYNTH (-)    a synthetic corpus with NO conversation structure must return ICC ~ 0. Both directions,
               because an estimator that always returns 0.8 would pass the positive check.
  SHUFFLE      the REAL data with conversation labels shuffled must drop to ~0. This is the null on
               the actual data rather than on my imagination, and it is the one that catches an
               estimator picking up something other than conversation membership.
  m-BAR        the mean cluster size is MEASURED, not taken from R398's ratio, because DEFF is linear
               in it and a wrong m moves the answer directly.
  DERIVATION   DEFF = 1 + (m-1)*ICC is labelled algebra, and R411's endpoints are shown to BE the
               ICC=0 and ICC=1 cases rather than two independent designs.

MULTIPLICITY    2 proxies x (real, shuffled) + 2 synthetic = 6 cells, all printed.
SEEDS           3 for the synthetic and shuffle controls; spread printed.
ARTIFACT        results/r412_clustering.json with the source hash.

IMPOSSIBLE HERE
  the OUTCOME's own ICC   -- needs an arm run on this corpus, i.e. the judge. Named, not approximated.
  a causal reading of ICC -- it is a variance decomposition, not a mechanism.
  a second release        -- one target corpus.

EXIT
    0  the controls hold and both ICCs are reported
    1  a control misbehaved -- UNVERIFIED
    2  the corpus is unusable -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import math
import pathlib
import subprocess
import sys
from collections import defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
SECOND = ROOT / "data" / "utterances.jsonl"
R411 = HERE.parent / "R411_are_the_two_effects_even_commensurable" / "results" / \
    "r411_commensurability.json"
ZEFF = 1.959964 + 0.841621
SEEDS = (1, 2, 3)


def icc_oneway(groups):
    """One-way random-effects ICC by ANOVA, unequal group sizes (Snedecor & Cochran m0)."""
    groups = [np.asarray(g, float) for g in groups if len(g) >= 2]
    k = len(groups)
    if k < 2:
        return float("nan"), 0.0
    ns = np.array([len(g) for g in groups], float)
    N = ns.sum()
    gm = np.concatenate(groups).mean()
    msb = sum(len(g) * (g.mean() - gm) ** 2 for g in groups) / (k - 1)
    msw = sum(((g - g.mean()) ** 2).sum() for g in groups) / (N - k)
    m0 = (N - (ns ** 2).sum() / N) / (k - 1)
    var_b = (msb - msw) / m0
    icc = var_b / (var_b + msw) if (var_b + msw) > 0 else 0.0
    return float(max(0.0, min(1.0, icc))), float(N / k)


def main() -> int:
    if not (SECOND.exists() and R411.exists()):
        print("  UNRUNNABLE: corpus or R411 artifact absent. Exit 2, never 0."); return 2
    a411 = json.loads(R411.read_text())
    d_eff = a411["d"]

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R412 · the clustering that decides 4.57x vs 2.50x   HEAD {head}\n")
    print("  ⛔ R411's NEXT NAMED A QUANTITY THAT NEEDS THE JUDGE — the third of my own closing")
    print("     sentences in a row with an unexamined step. The outcome whose clustering sets the")
    print("     design effect is `did the arm pick the chosen response`, and no arm has been run")
    print("     here. Its ICC is NOT measurable, and `measure it` made that sound like a task.\n")

    # ---- load ------------------------------------------------------------------------------------
    by_conv_score, by_conv_model = defaultdict(list), defaultdict(list)
    models = {}
    with SECOND.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            c, k = r.get("conversation_id"), r.get("interaction_id")
            if not (c and k):
                continue
            if str(r.get("if_chosen")).lower() == "true":
                m = r.get("model_name")
                if m is not None:
                    by_conv_model[c].append(models.setdefault(m, len(models)))
            try:
                by_conv_score[c].append(float(r.get("score")))
            except Exception:
                pass
    if len(by_conv_model) < 100:
        print(f"  UNRUNNABLE: {len(by_conv_model)} conversations. Exit 2, never 0."); return 2

    # winning-model identity -> indicator of "same model as this conversation's modal winner"
    def model_indicator(groups):
        out = []
        for g in groups.values():
            if len(g) < 2:
                continue
            vals, cnts = np.unique(g, return_counts=True)
            modal = vals[int(np.argmax(cnts))]
            out.append([1.0 if x == modal else 0.0 for x in g])
        return out

    grp_score = [g for g in by_conv_score.values() if len(g) >= 2]
    grp_model = model_indicator(by_conv_model)

    # ---- CONTROLS --------------------------------------------------------------------------------
    print("  CONTROLS")
    hi, lo, shf_s, shf_m = [], [], [], []
    for s in SEEDS:
        rng = np.random.default_rng(s)
        # SYNTH (+): ICC 0.80 by construction
        k_, m_ = 2000, 4
        mu = rng.normal(0, math.sqrt(0.8), k_)
        synth_hi = [mu[i] + rng.normal(0, math.sqrt(0.2), m_) for i in range(k_)]
        hi.append(icc_oneway(synth_hi)[0])
        # SYNTH (-): no conversation structure
        synth_lo = [rng.normal(0, 1.0, m_) for _ in range(k_)]
        lo.append(icc_oneway(synth_lo)[0])
        # SHUFFLE on the REAL data: destroy conversation membership, keep the values
        flat_s = np.concatenate([np.asarray(g) for g in grp_score])
        rng.shuffle(flat_s)
        sizes = [len(g) for g in grp_score]
        cut, re_s = 0, []
        for z in sizes:
            re_s.append(flat_s[cut:cut + z]); cut += z
        shf_s.append(icc_oneway(re_s)[0])
        flat_m = np.concatenate([np.asarray(g) for g in grp_model])
        rng.shuffle(flat_m)
        cut, re_m = 0, []
        for z in [len(g) for g in grp_model]:
            re_m.append(flat_m[cut:cut + z]); cut += z
        shf_m.append(icc_oneway(re_m)[0])
    pos_ok = abs(np.mean(hi) - 0.80) < 0.10
    neg_ok = np.mean(lo) < 0.05
    print(f"    SYNTH (+)   a corpus built at ICC=0.80 recovers {np.mean(hi):.3f} "
          f"(seeds {[round(x,3) for x in hi]})   {'PASS' if pos_ok else 'FAIL'}")
    print(f"    SYNTH (-)   a corpus with NO structure returns {np.mean(lo):.3f}   "
          f"{'PASS' if neg_ok else 'FAIL — an estimator that always returns 0.8 would pass (+)'}")
    if not (pos_ok and neg_ok):
        print("\n  UNVERIFIED — the estimator is blind in one direction. Exit 1."); return 1

    # ---- the measurement --------------------------------------------------------------------------
    icc_s, mbar_s = icc_oneway(grp_score)
    icc_m, mbar_m = icc_oneway(grp_model)
    print(f"\n  (A)(B) THE TWO PROXIES — the clustering of the DATA the outcome is built from")
    print(f"    {'proxy':<34}{'conversations':>15}{'m̄':>7}{'ICC':>9}{'shuffled':>11}")
    print(f"    {'score':<34}{len(grp_score):>15,}{mbar_s:>7.2f}{icc_s:>9.4f}"
          f"{np.mean(shf_s):>11.4f}")
    print(f"    {'winning model = modal winner':<34}{len(grp_model):>15,}{mbar_m:>7.2f}"
          f"{icc_m:>9.4f}{np.mean(shf_m):>11.4f}")
    print(f"    ⭐ the model proxy is the CLOSER one: if the same model keeps winning inside a")
    print(f"       conversation, an arm favouring it is right repeatedly — the outcome's clustering")
    print(f"       almost directly. `score` is printed beside it because two proxies disagreeing is")
    print(f"       information and one alone is a guess.")
    shuffle_ok = max(np.mean(shf_s), np.mean(shf_m)) < 0.05
    print(f"    SHUFFLE     conversation labels destroyed on the REAL data -> "
          f"{max(np.mean(shf_s), np.mean(shf_m)):.4f}   {'PASS' if shuffle_ok else 'FAIL'}")
    if not shuffle_ok:
        print("\n  UNVERIFIED — the estimator picks up something other than conversation membership.")
        return 1

    # ---- (C) the implied power --------------------------------------------------------------------
    n_i = 26789
    print(f"\n  (C) THE IMPLIED POWER — DEFF = 1 + (m̄-1)·ICC is ALGEBRA and is labelled one")
    rows = {}
    for name, icc, mbar in (("score", icc_s, mbar_s), ("winning model", icc_m, mbar_m)):
        deff = 1 + (mbar - 1) * icc
        n_eff = n_i / deff
        ratio = d_eff / (ZEFF / math.sqrt(n_eff))
        rows[name] = dict(icc=icc, mbar=mbar, deff=deff, n_eff=n_eff, ratio=ratio)
        print(f"    {name:<16} ICC {icc:.4f}  m̄ {mbar:.2f}  DEFF {deff:.3f}  "
              f"n_eff {n_eff:>9,.0f}  ratio {ratio:.2f}x")
    print(f"    for comparison, R411's endpoints: ICC=0 -> 4.57x, ICC=1 -> ~2.47x")
    print(f"    ⛔ WHICH MEANS R411's `RANGE` WAS ALREADY ICC IN [0,1] WITH THE INTERIOR BLANK — a")
    print(f"       derivation I did not notice while writing it. This round fills the interior.")

    worst = min(r["ratio"] for r in rows.values())
    mx = max(icc_s, icc_m)
    print()
    if mx < 0.15:
        v = "W_LOW_ICC"
        print(f"  W-LOW-ICC — both proxies below 0.15 (max {mx:.4f}), so the design effect is small")
        print(f"  and the ratio holds at {worst:.2f}x. The replication is POWERED, and R411's")
        print(f"  `marginal` came from assuming the worst rather than from measuring it.")
    elif mx > 0.50:
        v = "W_HIGH_ICC"
        print(f"  W-HIGH-ICC — max proxy {mx:.4f}, so the ratio falls to {worst:.2f}x. The")
        print(f"  replication is MARGINAL and must be re-scoped before it is run.")
    else:
        v = "W_MID"
        print(f"  W-MID — max proxy {mx:.4f}, ratio {worst:.2f}x, between the pre-registered")
        print(f"  thresholds. Reported as it fell rather than rounded toward a decision.")

    print(f"\n  ⚠ A PROXY IS NOT THE OUTCOME. This measures the clustering of the DATA the outcome is")
    print(f"    built from, not of the outcome. It NARROWS the range; it does not close it, and the")
    print(f"    outcome's own ICC still needs an arm run on this corpus.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, d=d_eff, n_interactions=n_i, rows=rows,
               icc_score=icc_s, icc_model=icc_m, mbar_score=mbar_s, mbar_model=mbar_m,
               shuffled=dict(score=float(np.mean(shf_s)), model=float(np.mean(shf_m))),
               controls=dict(synth_hi=float(np.mean(hi)), synth_lo=float(np.mean(lo)),
                             pos_ok=pos_ok, neg_ok=neg_ok, shuffle_ok=shuffle_ok),
               worst_ratio=worst, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r412_clustering.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
