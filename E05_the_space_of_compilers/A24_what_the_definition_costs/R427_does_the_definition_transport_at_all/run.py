"""R427 -- the first number on the second corpus. Does a prompt-blind core pick what people picked?

DEFINITION.md's `What this definition cannot claim` table has carried `transfer to another release`
as RETRACTED since R398: `data/utterances.jsonl` holds 68,371 human-scored rows over 8,011
conversations and had been referenced by zero rounds. Since then SEVEN rounds have READ that corpus
-- R398 existence, R399 estimand, R400 depth, R402 harness, R403 statability, R412 clustering, R413
score-clustering -- and NOT ONE calls `select_core` or `judge_core` on it.

⛔ SIX ROUNDS OF `CAN WE?` AND NONE OF `HERE IS THE NUMBER`. That is preparing rather than producing,
   and it is the campaign's largest open structural gap: the definition's own table says clause ②
   and the human-agreement target CAN transport, and nobody has made them.

⭐ AND THE CHEAP VERSION IS THE HONEST ONE. The second corpus has no rubric, so a prompt-SPECIFIC
   core would need generating first. `core_generic.json` is PROMPT-BLIND -- fixed criteria that never
   see the prompt -- so it transports unchanged, and it is the arm the sham-vs-neutral lesson found
   carries five-sixths of what the instrument achieves. This round measures the FLOOR of transport
   and says plainly that it speaks to no prompt-specific core.

⛔ ARITHMETIC TRAP, TWICE.
   (1) CHANCE is `mean(1/n_responses)` -- forced by the design, a DERIVATION, and it is the baseline
       rather than a finding.
   (2) The MDE below is `ZEFF * sd / sqrt(n_conv)` with ZEFF = 2.801585. That is algebra, not
       evidence. What is NOT forced is any arm's accuracy, nor whether it clears its own MDE.

ESTIMAND        (A) ACC = P(the response the core ranks first is the one a human chose), estimated
                    with the CONVERSATION as the independent unit;
                (B) ACC(generic) - ACC(randblind), the value of THESE criteria over ANY criteria;
                (C) ACC(generic) - ACC(length), the value over the shortcut a length-preferring
                    judge would produce for free.

IDENTIFICATION  (A)(B)(C) exact on the sampled conversations. NOT identified: anything about a
                prompt-SPECIFIC core -- none exists for this corpus and generating one is a separate
                job with separate assumptions. NOT identified: transport of clauses defined against
                `full`, which needs a rubric this corpus does not have (R403).

SCOPE           population: 2,200 conversations sampled seeded from `utterances.jsonl`, restricted to
                interactions with >= 2 distinct responses carrying a human `score` · instrument:
                Qwen3.5-2B-Base at batch 32, the campaign's default judge · baseline: CHANCE and
                LENGTH, both computed here · regime: k = 4, prompt-blind criteria only.

WORLDS
  W-TRANSPORTS      generic beats BOTH chance and length by more than its own MDE. Then the scoring
                    apparatus carries human-preference signal onto a corpus it was never built for,
                    and the definition gains its first cross-release evidence.
  W-LENGTH          generic beats chance but NOT length. Then what transports is a length preference,
                    the criteria are decorative on this corpus, and the honest report is a shortcut.
  W-DOES-NOT        generic does not clear chance. Then the apparatus does not transport at all, and
                    every clause stated against `full` is release-local in the strongest sense.
  W-ANY-CRITERIA    generic beats chance and length, but randblind matches it. Then what transports
                    is `having criteria`, not having THESE criteria -- and clause ②'s content is not
                    what carries.

PREDICTION MATRIX
  W-TRANSPORTS   -> generic - chance > MDE, generic - length > MDE, generic - randblind > MDE
  W-LENGTH       -> generic - chance > MDE, generic - length <= MDE
  W-DOES-NOT     -> generic - chance <= MDE
  W-ANY-CRITERIA -> generic - randblind <= MDE while both clear chance and length

PRE-REGISTERED KILL -- conditional on the controls, never on an accuracy alone.
    if placebo == 0 exactly and shuffle lands within MDE of chance and plant reaches the ceiling:
        generic - chance <= MDE                      -> W-DOES-NOT
        elif generic - length <= MDE                 -> W-LENGTH
        elif generic - randblind <= MDE              -> W-ANY-CRITERIA
        else                                         -> W-TRANSPORTS
    else: UNVERIFIED -- never CONFIRMED, never OVERTURNED.

CONTROLS
  PLACEBO      an arm against ITSELF must differ by EXACTLY 0. A contrast where no effect can exist
               that returns anything but zero means the estimator is broken.
  SHUFFLE (-)  satisfaction permuted WITHIN each interaction destroys the core's ordering while
               preserving every margin. It must land at CHANCE. This is the world where the criteria
               carry nothing, built rather than assumed.
  PLANT (+)    satisfaction overwritten so the chosen response wins must reach accuracy 1.0 -- the
               CEILING. And the threshold must sit strictly between the shuffle floor and this
               ceiling, or the control cannot fail in one direction.
  LENGTH       the longest response, the shortcut a length-preferring judge produces for free. It is
               a BASELINE, not a nuisance: an arm that cannot beat it has not shown criteria matter.
  CLUSTER      n_eff is CONVERSATIONS. R413 measured kappa_chosen = 1.0 and p_in_argmax = 1.0 within
               a conversation, so rows are not independent and using them would shrink every
               interval by sqrt(3.317).
  PROVENANCE   the artifact's own `provenance` block is printed, so the configuration that produced
               the numbers is visible in the same output as the numbers.

MULTIPLICITY    4 arms (generic, randblind, chance, length) x 3 contrasts; every cell printed,
                including the ones that kill the finding.
SEEDS           the sample is seeded; randblind exists at s0/s1/s2 and this round reports whichever
                are on disk, naming the ones that are not rather than implying three.
ARTIFACT        results/r427_transport.json with the source hash.

IMPOSSIBLE HERE
  a prompt-specific core       -- no rubric on this corpus; generating one is a separate job.
  clauses defined against `full` -- R403 measured them NOT-STATABLE off the home release.
  a second team                -- one operator.
  construct validity of `score` -- it is this release's own human rating; no external gold standard.

EXIT
    0  the controls hold and a branch is reached
    1  a control misbehaved -- UNVERIFIED
    2  the scored artifacts are absent -- never a silent pass
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
ZEFF = 1.959964 + 0.841621          # two-sided alpha .05 + power .80
ARMS = {"generic": "sat_transport_generic.npz",
        "randblind_s0": "sat_transport_randblind_s0.npz",
        "randblind_s1": "sat_transport_randblind_s1.npz",
        "randblind_s2": "sat_transport_randblind_s2.npz"}


def load(p):
    with np.load(p, allow_pickle=True) as d:
        meta, sat = [str(x) for x in d["meta"]], np.asarray(d["sat"], float)
        tgt = json.loads(str(d["targets"])) if "targets" in d.files else None
        prov = json.loads(str(d["provenance"])) if "provenance" in d.files else None
    per = collections.defaultdict(dict)          # (conv, inter) -> {resp: [values]}
    for m, v in zip(meta, sat):
        c, i, r, _j = m.split("|")
        per[(c, i)].setdefault(r, []).append(v)
    return {k: {r: float(np.mean(vs)) for r, vs in d.items()} for k, d in per.items()}, tgt, prov


def acc_by_conv(scored, tgt, pick=None):
    """-> {conv: [0/1 per interaction]} using `pick(resp_dicts, scored_row)` or the arm's own argmax."""
    out = collections.defaultdict(list)
    for t in tgt:
        key = (t["conv"], t["inter"])
        chosen = [r["id"] for r in t["resp"] if r["chosen"]]
        if len(chosen) != 1:
            continue                              # no unique human pick -> not an admissible unit
        row = scored.get(key)
        if pick is None:
            if not row:
                continue
            best = max(row, key=lambda r: (row[r], r))
        else:
            best = pick(t["resp"], row)
            if best is None:
                continue
        out[t["conv"]].append(1.0 if best == chosen[0] else 0.0)
    return out


def cluster_mean(by_conv):
    """Conversation is the unit: mean within, then across. Returns (mean, sd_across, n_conv)."""
    m = np.array([np.mean(v) for v in by_conv.values() if v], float)
    return (float(m.mean()), float(m.std(ddof=1)), len(m)) if len(m) > 1 else (float("nan"), 0.0, len(m))


def paired(a_by, b_by):
    ks = [k for k in a_by if k in b_by and a_by[k] and b_by[k]]
    d = np.array([np.mean(a_by[k]) - np.mean(b_by[k]) for k in ks], float)
    if len(d) < 2:
        return float("nan"), float("nan"), len(d)
    return float(d.mean()), float(ZEFF * d.std(ddof=1) / np.sqrt(len(d))), len(d)


def main() -> int:
    have = {k: RES / v for k, v in ARMS.items() if (RES / v).exists()}
    if "generic" not in have:
        print(f"  UNRUNNABLE: {ARMS['generic']} absent — the judge job has not landed yet.")
        print(f"  Exit 2, never 0. An absent artifact is not a null result.")
        return 2
    missing = [k for k in ARMS if k not in have]

    print("R427 · the first number on the second corpus\n")
    print("  ⛔ SEVEN ROUNDS READ THIS CORPUS AND NONE SCORED ANYTHING ON IT. Six rounds of `can we?`")
    print("     and none of `here is the number` — preparing rather than producing.\n")

    scored, tgt, prov = load(have["generic"])
    if prov:
        print("  PROVENANCE (the producer's own record, printed beside the numbers it made)")
        for k in ("corpus", "model", "n_convs", "n_interactions", "n_calls", "n_criteria", "seed"):
            if k in prov:
                print(f"    {k:<16} {prov[k]}")

    # ---- CONTROLS ---------------------------------------------------------------------------------
    gen = acc_by_conv(scored, tgt)
    g_mean, g_sd, g_n = cluster_mean(gen)

    placebo_d, _, _ = paired(gen, gen)
    placebo_ok = placebo_d == 0.0

    rng = np.random.default_rng(0)
    shuf = {k: dict(zip(list(v), rng.permutation(list(v.values())))) for k, v in scored.items()}
    s_mean, _, _ = cluster_mean(acc_by_conv(shuf, tgt))

    plant = {}
    for t in tgt:
        ch = [r["id"] for r in t["resp"] if r["chosen"]]
        key = (t["conv"], t["inter"])
        if key in scored and len(ch) == 1:
            plant[key] = {r: (1.0 if r == ch[0] else 0.0) for r in scored[key]}
    p_mean, _, _ = cluster_mean(acc_by_conv(plant, tgt))

    ch_by = collections.defaultdict(list)
    for t in tgt:
        ch = [r["id"] for r in t["resp"] if r["chosen"]]
        if len(ch) == 1:
            ch_by[t["conv"]].append(1.0 / len(t["resp"]))
    c_mean, _, _ = cluster_mean(ch_by)

    len_by = acc_by_conv(scored, tgt,
                         pick=lambda resp, row: max(resp, key=lambda r: (r["len"], r["id"]))["id"])
    l_mean, _, _ = cluster_mean(len_by)

    mde = ZEFF * g_sd / np.sqrt(g_n) if g_n > 1 else float("nan")
    print(f"\n  CONTROLS")
    print(f"    PLACEBO     an arm against ITSELF differs by exactly 0: {placebo_ok}   "
          f"{'PASS' if placebo_ok else 'FAIL — the estimator is broken'}")
    print(f"    SHUFFLE (-) satisfaction permuted WITHIN each interaction: {s_mean:.4f} "
          f"vs chance {c_mean:.4f}")
    print(f"    PLANT (+)   satisfaction overwritten so the chosen response wins: {p_mean:.4f} "
          f"(ceiling)")
    floor_ok = abs(s_mean - c_mean) <= max(mde, 1e-9)
    ceil_ok = p_mean >= 0.999
    print(f"    BAND        floor {s_mean:.4f} < any threshold < ceiling {p_mean:.4f}: "
          f"{'PASS' if (floor_ok and ceil_ok) else 'FAIL'}")
    print(f"    CLUSTER     n_eff = CONVERSATIONS = {g_n:,} (R413: kappa_chosen 1.0 within a")
    print(f"                conversation, deff 3.317 — rows would shrink every interval by 1.82x)")
    print(f"    ⛔ CHANCE {c_mean:.4f} IS A DERIVATION — mean(1/n_responses), forced by the design.")
    print(f"       So is MDE {mde:.4f} = {ZEFF:.6f} * sd/sqrt(n). Neither is evidence.")
    if not (placebo_ok and floor_ok and ceil_ok):
        print("\n  UNVERIFIED — a control misbehaved. Exit 1."); return 1

    # ---- the measurement ---------------------------------------------------------------------------
    print(f"\n  ACCURACY AT PICKING THE HUMAN-CHOSEN RESPONSE — conversation is the unit")
    print(f"    {'arm':<16} {'ACC':>8} {'vs chance':>11} {'vs length':>11} {'MDE':>8}")
    rows = {"generic": dict(acc=g_mean, n=g_n)}
    dc, mc, _ = paired(gen, ch_by)
    dl, ml, _ = paired(gen, len_by)
    print(f"    {'generic':<16} {g_mean:>8.4f} {dc:>+11.4f} {dl:>+11.4f} {mde:>8.4f}")
    print(f"    {'chance (deriv)':<16} {c_mean:>8.4f} {'—':>11} {'—':>11} {'—':>8}")
    print(f"    {'length':<16} {l_mean:>8.4f} {'—':>11} {'—':>11} {'—':>8}")

    rb, dr, mr = {}, float("nan"), float("nan")
    for k in [a for a in have if a.startswith("randblind")]:
        s2, t2, _ = load(have[k])
        by = acc_by_conv(s2, t2)
        m2, _, n2 = cluster_mean(by)
        d2, mm2, _ = paired(gen, by)
        rb[k] = dict(acc=m2, n=n2, gen_minus=d2, mde=mm2)
        print(f"    {k:<16} {m2:>8.4f} {'—':>11} {'—':>11} {'—':>8}   generic − it: "
              f"{d2:+.4f} vs MDE {mm2:.4f}")
        if np.isnan(dr):
            dr, mr = d2, mm2
    if missing:
        print(f"\n    ⚠ ABSENT, named rather than implied: {missing}")

    print()
    if dc <= mc:
        v = "W_DOES_NOT"
        print(f"  W-DOES-NOT — generic does not clear CHANCE ({dc:+.4f} vs MDE {mc:.4f}). The")
        print(f"  apparatus does not transport, and every clause stated against `full` is")
        print(f"  release-local in the strongest sense available here.")
    elif dl <= ml:
        v = "W_LENGTH"
        print(f"  W-LENGTH — generic clears chance but NOT length ({dl:+.4f} vs MDE {ml:.4f}). What")
        print(f"  transports is a LENGTH PREFERENCE; the criteria are decorative on this corpus.")
    elif not rb:
        v = "W_UNVERIFIED_NO_BASELINE"
        print(f"  UNVERIFIED — generic clears chance and length, but no randblind arm is on disk, so")
        print(f"  `THESE criteria` cannot be separated from `ANY criteria`. That is the one contrast")
        print(f"  that decides whether clause ②'s CONTENT is what carries. Not a finding yet.")
    elif dr <= mr:
        v = "W_ANY_CRITERIA"
        print(f"  W-ANY-CRITERIA — generic beats chance and length, but a RANDOM prompt-blind core")
        print(f"  matches it ({dr:+.4f} vs MDE {mr:.4f}). What transports is HAVING criteria, not")
        print(f"  having THESE criteria — and clause ②'s content is not what carries.")
    else:
        v = "W_TRANSPORTS"
        print(f"  W-TRANSPORTS — generic clears chance ({dc:+.4f} > {mc:.4f}), length ({dl:+.4f} >")
        print(f"  {ml:.4f}) and a random prompt-blind core ({dr:+.4f} > {mr:.4f}). The apparatus")
        print(f"  carries human-preference signal onto a corpus it was never built for, and the")
        print(f"  definition has its first cross-release evidence.")

    print(f"\n  ⚠ THIS SPEAKS TO NO PROMPT-SPECIFIC CORE. `generic` is prompt-BLIND by construction;")
    print(f"    the corpus has no rubric and generating one is a separate job with its own")
    print(f"    assumptions. The floor of transport is what was measured.")
    print(f"  ⚠ AND `score` IS THIS RELEASE'S OWN HUMAN RATING. There is no external gold standard,")
    print(f"    so construct validity is not claimed.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               generic=rows["generic"], chance=c_mean, length=l_mean, randblind=rb,
               d_chance=dc, mde_chance=mc, d_length=dl, mde_length=ml, mde=mde,
               controls=dict(placebo=placebo_d, shuffle=s_mean, plant=p_mean,
                             floor_ok=floor_ok, ceil_ok=ceil_ok, n_conv=g_n),
               missing=missing, provenance=prov, verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r427_transport.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
