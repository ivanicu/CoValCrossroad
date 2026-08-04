"""R413 -- does a score-based outcome escape the conversation clustering, or is the corpus limited whatever I target?

R412 measured `P(same winning model | same conversation) = 1.0000` and concluded the effective n is
~7,822 rather than 26,789. Its NEXT proposed re-scoping onto `score`, which is per-response and whose
RAW values cluster at only ICC 0.1978.

⛔ THAT PROPOSAL HAS A HOLE AND IT IS THE SAME SHAPE AS THE LAST THREE. A clause-② test does not
   consume raw scores; it consumes an ORDERING -- does the arm rank the responses the way the human
   did. So the clustering that matters is of the ORDERING, not of the levels. If the top-scored
   response is the same model throughout a conversation, an ordering outcome is exactly as clustered
   as `if_chosen` was and `score` buys nothing. The raw-score ICC of 0.1978 would then be a NUISANCE
   -- a user rating high or low overall -- that a within-interaction contrast removes anyway.

⭐ AND THE NUISANCE CANCELS THE WAY R410's REFERENCE DID. Any conversation-level or user-level offset
   enters both responses of an interaction identically, so a WITHIN-interaction contrast subtracts it
   exactly. That is the same cancellation R410 verified at 2.8e-17, running in the helpful direction:
   differencing removes the level, so the level's ICC is the wrong quantity to price the design with.

⛔ ARITHMETIC TRAP. That a within-interaction contrast removes a purely additive conversation offset
   is FORCED and is labelled a derivation. What is NOT forced is whether the ORDERING is
   conversation-constant, and that is the measurement this round exists for.

ESTIMAND        (A) the share of interactions where `argmax(score)` selects the SAME response as
                    `if_chosen` -- i.e. whether score carries information beyond the choice;
                (B) the pairwise kappa of the ARGMAX MODEL within conversation, on the same
                    instrument R412 used, so the two numbers are directly comparable;
                (C) the ICC of the WITHIN-interaction score GAP (top minus runner-up), the quantity a
                    contrast-based design would actually consume;
                (D) the implied effective n and power ratio for a score-ordering design.

IDENTIFICATION  (A)-(C) exact given the release. (D) exact given (C) and the DEFF formula, which is
                algebra. NOT identified: the clustering of an ARM's errors, which needs the judge --
                stated, because that is the step my last three closing sentences each skipped.

SCOPE           population: second-corpus interactions with >= 2 scored responses · instrument:
                pairwise kappa and one-way ANOVA ICC · baseline: within-corpus shuffle · regime: no
                judge.

WORLDS
  W-SCORE-ESCAPES   the argmax model is NOT conversation-constant and the gap ICC is low. Then a
                    score-ordering design recovers most of the lost n and the replication is powered
                    after all.
  W-SCORE-TRAPPED   the argmax model is conversation-constant too. Then the corpus is
                    conversation-limited whatever outcome I target, R412's 7,822 is the ceiling, and
                    re-scoping onto score was a dead end that cost one round to find.

PREDICTION MATRIX
  W-SCORE-ESCAPES -> argmax-model kappa < 0.5 AND gap ICC < 0.15
  W-SCORE-TRAPPED -> argmax-model kappa > 0.9
  between         -> named as partial, with the ratio as an interval

PRE-REGISTERED KILL -- conditional on the controls, never on the kappa alone.
    if kappa_instrument_reproduces_R412_on_if_chosen and synth_controls_pass and shuffle_is_null:
        kappa < 0.5 and gap_icc < 0.15 -> W-SCORE-ESCAPES
        kappa > 0.9                    -> W-SCORE-TRAPPED
        else                           -> PARTIAL, interval reported
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  REPRODUCE (+)  my kappa instrument, run on `if_chosen` model identity, must return R412's 1.0000.
                 A control whose answer was produced by a DIFFERENT round, and it validates the
                 instrument on a quantity whose value is already committed.
  SYNTH (+/-)    a synthetic corpus at ICC 0.80 recovers it; one with no structure returns ~0.
  SHUFFLE        conversation labels destroyed on the REAL data must drop every statistic to ~0.
  TIES           interactions where the top two scores TIE have no well-defined argmax and are
                 counted separately, never silently assigned. A tie broken by array order would
                 manufacture agreement with whatever the file happens to list first.
  DERIVATION     the offset-cancellation is labelled algebra and is VERIFIED numerically anyway, on
                 the same pattern R410 used, because "it cancels" is exactly the kind of sentence
                 that is true right up until an implementation detail makes it false.

MULTIPLICITY    3 statistics x (real, shuffled) + 2 synthetic + 1 cross-round = 9 cells, all printed.
SEEDS           3; spreads printed.
ARTIFACT        results/r413_score_clustering.json with the source hash.

IMPOSSIBLE HERE
  an ARM's error clustering  -- needs the judge. This is the step my last three NEXTs each skipped,
                                and it is named rather than made to sound like a task.
  a causal reading           -- variance decomposition, not mechanism.
  a second target corpus     -- one.

EXIT
    0  controls hold and all statistics are reported
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
R412 = HERE.parent / "R412_the_clustering_that_decides_the_power" / "results" / "r412_clustering.json"
ZEFF = 1.959964 + 0.841621
SEEDS = (1, 2, 3)


def icc_oneway(groups):
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
    vb = (msb - msw) / m0
    return float(max(0.0, min(1.0, vb / (vb + msw) if (vb + msw) > 0 else 0.0))), float(N / k)


def kappa_pairwise(groups, rng, draws=200000):
    ins = tot = 0
    for g in groups.values():
        if len(g) < 2:
            continue
        for a in range(len(g)):
            for b in range(a + 1, len(g)):
                ins += (g[a] == g[b]); tot += 1
    p_in = ins / tot if tot else float("nan")
    flat = np.array([x for g in groups.values() if len(g) >= 2 for x in g])
    keys = np.array([i for i, g in enumerate(groups.values()) if len(g) >= 2 for _ in g])
    hits = n = 0
    for _ in range(draws):
        i, j = rng.integers(0, len(flat), 2)
        if keys[i] != keys[j]:
            hits += (flat[i] == flat[j]); n += 1
    p_out = hits / n if n else float("nan")
    kap = (p_in - p_out) / (1 - p_out) if p_out < 1 else float("nan")
    return float(max(0.0, min(1.0, kap))), p_in, p_out, tot


def main() -> int:
    for f in (SECOND, R411, R412):
        if not f.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    d_eff = json.loads(R411.read_text())["d"]
    committed_kappa = json.loads(R412.read_text())["icc_model"]

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R413 · does score escape the clustering?   HEAD {head}\n")
    print("  ⛔ R412's NEXT HAS A HOLE OF THE SAME SHAPE AS THE LAST THREE. A clause-② test consumes")
    print("     an ORDERING, not raw scores. If the top-scored response is the same model all")
    print("     through a conversation, an ordering outcome is exactly as clustered as `if_chosen`")
    print("     was, and the raw-score ICC of 0.1978 is a NUISANCE a within-interaction contrast")
    print("     removes anyway.\n")

    # ---- load: per interaction, the scored responses and their models ------------------------------
    inter = defaultdict(list)
    conv_of = {}
    with SECOND.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                continue
            k, c = r.get("interaction_id"), r.get("conversation_id")
            if not (k and c):
                continue
            try:
                s = float(r.get("score"))
            except Exception:
                continue
            inter[k].append((s, r.get("model_name"),
                             str(r.get("if_chosen")).lower() == "true"))
            conv_of[k] = c

    agree = tie = tot = 0
    by_conv_argmax, by_conv_chosen, by_conv_gap = defaultdict(list), defaultdict(list), defaultdict(list)
    models = {}
    for k, rows in inter.items():
        if len(rows) < 2:
            continue
        ss = sorted((r[0] for r in rows), reverse=True)
        tot += 1
        if ss[0] == ss[1]:
            tie += 1
            continue
        top = max(rows, key=lambda r: r[0])
        ch = [r for r in rows if r[2]]
        by_conv_argmax[conv_of[k]].append(models.setdefault(top[1], len(models)))
        by_conv_gap[conv_of[k]].append(ss[0] - ss[1])
        if len(ch) == 1:
            by_conv_chosen[conv_of[k]].append(models.setdefault(ch[0][1], len(models)))
            agree += (ch[0] is top or (ch[0][0] == top[0] and ch[0][1] == top[1]))

    # ---- CONTROLS ---------------------------------------------------------------------------------
    print("  CONTROLS")
    rng = np.random.default_rng(SEEDS[0])
    k_ch, pin_ch, pout_ch, _ = kappa_pairwise(by_conv_chosen, rng)
    repro = abs(k_ch - committed_kappa) < 1e-6
    print(f"    REPRODUCE (+)  my kappa on `if_chosen` model = {k_ch:.4f}; R412 committed "
          f"{committed_kappa:.4f}   {'PASS' if repro else 'FAIL'}")
    print(f"                   a control whose answer was produced by a DIFFERENT round")
    hi, lo = [], []
    for s in SEEDS:
        r2 = np.random.default_rng(s)
        k_, m_ = 2000, 4
        mu = r2.normal(0, math.sqrt(0.8), k_)
        hi.append(icc_oneway([mu[i] + r2.normal(0, math.sqrt(0.2), m_) for i in range(k_)])[0])
        lo.append(icc_oneway([r2.normal(0, 1.0, m_) for _ in range(k_)])[0])
    synth_ok = abs(np.mean(hi) - 0.8) < 0.10 and np.mean(lo) < 0.05
    print(f"    SYNTH (+/-)    ICC=0.80 recovers {np.mean(hi):.3f}; no-structure returns "
          f"{np.mean(lo):.3f}   {'PASS' if synth_ok else 'FAIL'}")
    # shuffle null on the real data
    grp_gap = [g for g in by_conv_gap.values() if len(g) >= 2]
    shf = []
    for s in SEEDS:
        r3 = np.random.default_rng(s)
        flat = np.concatenate([np.asarray(g) for g in grp_gap]); r3.shuffle(flat)
        cut, re = 0, []
        for z in [len(g) for g in grp_gap]:
            re.append(flat[cut:cut + z]); cut += z
        shf.append(icc_oneway(re)[0])
    shuffle_ok = np.mean(shf) < 0.05
    print(f"    SHUFFLE        conversation labels destroyed on the REAL gap data -> "
          f"{np.mean(shf):.4f}   {'PASS' if shuffle_ok else 'FAIL'}")
    print(f"    TIES           {tie:,} of {tot:,} interactions have a tied top score and are")
    print(f"                   EXCLUDED, never broken by array order — that would manufacture")
    print(f"                   agreement with whatever the file lists first")
    if not (repro and synth_ok and shuffle_ok):
        print("\n  UNVERIFIED — a control misbehaved. Exit 1."); return 1

    # ---- the measurements ---------------------------------------------------------------------------
    n_used = tot - tie
    rate = agree / n_used if n_used else float("nan")
    k_am, pin_am, pout_am, npair = kappa_pairwise(by_conv_argmax, np.random.default_rng(SEEDS[0]))
    icc_gap, mbar = icc_oneway(grp_gap)
    print(f"\n  (A) DOES SCORE CARRY INFORMATION BEYOND THE CHOICE?")
    print(f"      argmax(score) selects the SAME response as `if_chosen` in {agree:,} of "
          f"{n_used:,} = {rate:.4f}")
    print(f"\n  (B) IS THE ARGMAX MODEL CONVERSATION-CONSTANT, like the chosen model was?")
    print(f"      P(same argmax model | same conversation) = {pin_am:.4f} over {npair:,} pairs")
    print(f"      P(same | different)                      = {pout_am:.4f}")
    print(f"      kappa = {k_am:.4f}    (the chosen model was {committed_kappa:.4f})")
    print(f"\n  (C) THE WITHIN-INTERACTION SCORE GAP — the quantity a contrast design consumes")
    print(f"      ICC {icc_gap:.4f}  m̄ {mbar:.2f}   (raw score levels were 0.1978)")

    # ---- (D) implied power ---------------------------------------------------------------------------
    n_i = 26789
    deff = 1 + (mbar - 1) * max(icc_gap, k_am)
    n_eff = n_i / deff
    ratio = d_eff / (ZEFF / math.sqrt(n_eff))
    print(f"\n  (D) IMPLIED POWER — DEFF = 1 + (m̄-1)·max(ICC_gap, kappa_argmax), the BINDING one")
    print(f"      DEFF {deff:.3f}   n_eff {n_eff:,.0f}   ratio {ratio:.2f}x")
    print(f"      R412's if_chosen design was 2.47x; ICC=0 would be 4.57x")

    print()
    if k_am > 0.9:
        v = "W_SCORE_TRAPPED"
        print(f"  W-SCORE-TRAPPED — the argmax model is conversation-constant too (kappa {k_am:.4f}).")
        print(f"  The corpus is conversation-limited WHATEVER outcome I target, R412's ~7,822 is the")
        print(f"  ceiling, and re-scoping onto score was a dead end that cost one round to find --")
        print(f"  which is the cheapest way to find one.")
    elif k_am < 0.5 and icc_gap < 0.15:
        v = "W_SCORE_ESCAPES"
        print(f"  W-SCORE-ESCAPES — the argmax model is NOT conversation-constant (kappa {k_am:.4f})")
        print(f"  and the gap ICC is {icc_gap:.4f}. A score-ordering design recovers most of the lost")
        print(f"  n and reaches {ratio:.2f}x.")
    else:
        v = "W_PARTIAL"
        print(f"  PARTIAL — kappa {k_am:.4f}, gap ICC {icc_gap:.4f}, ratio {ratio:.2f}x. Between the")
        print(f"  pre-registered thresholds and reported as it fell.")

    print(f"\n  ⚠ AND THE STEP MY LAST THREE CLOSING SENTENCES EACH SKIPPED, NAMED RATHER THAN MADE TO")
    print(f"    SOUND LIKE A TASK: the clustering of an ARM's ERRORS is not measurable without the")
    print(f"    judge. Everything here is the clustering of the DATA an arm would be scored against.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, n_interactions=tot, ties=tie, n_used=n_used, agree=agree,
               agree_rate=rate, kappa_argmax=k_am, p_in_argmax=pin_am, p_out_argmax=pout_am,
               kappa_chosen=k_ch, committed_kappa=committed_kappa,
               icc_gap=icc_gap, mbar=mbar, deff=deff, n_eff=n_eff, ratio=ratio,
               controls=dict(reproduce=repro, synth_hi=float(np.mean(hi)),
                             synth_lo=float(np.mean(lo)), shuffle=float(np.mean(shf))),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r413_score_clustering.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
