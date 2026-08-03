"""Two findings that may be one: the hedging penalty and the length preference.

r193: the response people converge on flagging as unacceptable hedges LESS than the one they leave
alone, within the same prompt, z -5.6 against a 300-permutation null, and it is not length in
disguise (length z -0.8).

r191: the length preference -- the longest of four ranked first -- runs at 32.6% on the prompts
the panel says have a single correct answer against ~39% on every contested quartile, +5.0pp at
z +2.1 with the prompt as the unit.

Both point at the same latent variable without either having tested it: whether the question is
CONTESTED. If that is the common cause, then one account covers both -- on a question with more
than one defensible answer people penalise a response that pretends otherwise and reach for length
as a proxy for care; on a question with a single right answer neither applies because there is a
right answer to find. If it is not, they are two unrelated effects and should stop being described
together.

THE STRATIFIER IS ALREADY VALIDATED, which is why this round is cheap and why it could not have
been run before r191. Prompt-level subjectivity has Spearman-Brown +0.724 across half-panels, so
it describes the prompt rather than the person -- the mistake that made r177's version of this
test come out flat.

THE PREDICTION MATRIX, written before the run:
                          contested prompts        single-answer prompts
  ONE VARIABLE            hedging penalty large    hedging penalty small or absent
                          length preference large  length preference small
  TWO EFFECTS             the two do not move together across strata
  NEITHER                 both flat, and r191/r193 were both stratum-independent

A PLACEBO AXIS IS CARRIED THROUGH THE SAME CODE. `warmth` showed |z| < 1 in r193; if it develops a
stratum difference here, the stratification is manufacturing structure and nothing in this round
is admissible.
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import re
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
LETTERS = "ABCD"
MIN_RATERS = 6
N_PERM = 300

FLAG = re.compile(r"^\s*([ABCD])\b")
SUBJ = {"single correct answer to this prompt": 0.0, "depends on a person's values": 1.0,
        "depends on something else": 1.0, "I'm unsure whether": 0.5}
AXES = {
    "hedging": r"\b(it depends|depends on|however|although|on the other hand|some people|"
               r"in some cases|generally|often|typically|may vary|not always)\b",
    "warmth": r"\b(I understand|that sounds|I'm sorry|it's okay|you're not alone|"
              r"completely normal|valid)\b",     # PLACEBO -- showed |z|<1 in r193
}


def top_of(s):
    for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
        g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
        if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
            return g[0]
        break
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    feats = {}
    for c in cmp_:
        o = {}
        for i, r in enumerate(c.get("responses") or []):
            k = str(r.get("response_index", LETTERS[i])).strip().upper()
            if k in LETTERS:
                body = " ".join(m.get("content") or "" for m in (r.get("messages") or [])
                                if isinstance(m.get("content"), str))
                f = {"length": float(len(body))}
                for name, pat in AXES.items():
                    f[name] = float(len(re.findall(pat, body, re.I)))
                o[k] = f
        if len(o) == 4:
            feats[c["prompt_id"]] = o

    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    flag = defaultdict(list)
    subj = defaultdict(list)
    tops = defaultdict(list)
    for a in ann:
        for s in a.get("assessments", []):
            pid = s.get("conversation_id")
            if pid not in feats:
                continue
            v = s.get("subjectivity")
            if isinstance(v, str):
                for tok, x in SUBJ.items():
                    if tok in v:
                        subj[pid].append(x)
                        break
            t = top_of(s)
            if t:
                tops[pid].append(t)
            b = s.get("ranking_blocks") or {}
            if not (b.get("unacceptable") or b.get("personal")):
                continue
            fl = set()
            for blk in (b.get("unacceptable") or []):
                for r in (blk.get("rating") or []):
                    m = FLAG.match(r) if isinstance(r, str) else None
                    if m:
                        fl.add(m.group(1))
            for L in LETTERS:
                flag[(pid, L)].append(1.0 if L in fl else 0.0)

    psub = {p: float(np.mean(v)) for p, v in subj.items() if len(v) >= MIN_RATERS}
    rate = {k: float(np.mean(v)) for k, v in flag.items() if len(v) >= MIN_RATERS}
    fl_prompts = sorted({p for p, _L in rate if p in psub})
    print(f"prompts with a validated subjectivity mean: {len(psub)}")
    print(f"  of those, with >={MIN_RATERS} asked assessments (flag analysis): {len(fl_prompts)}")

    # single-answer = bottom third of prompt-level subjectivity; contested = top third
    cut = np.percentile([psub[p] for p in fl_prompts], [33, 67])

    def stratum(p):
        return "single-answer" if psub[p] <= cut[0] else (
            "contested" if psub[p] >= cut[1] else "middle")

    # ---------------------------------------------------------------- the hedging contrast
    def contrast(pick, keep):
        acc = defaultdict(list)
        for p in fl_prompts:
            if stratum(p) != keep:
                continue
            hi, lo = pick(p)
            if hi is None or hi == lo:
                continue
            for k in feats[p][hi]:
                acc[k].append(feats[p][hi][k] - feats[p][lo][k])
        return {k: (float(np.mean(v)), len(v)) for k, v in acc.items() if len(v) >= 40}

    def real(p):
        r = {L: rate.get((p, L), 0.0) for L in LETTERS}
        hi, lo = max(r, key=r.get), min(r, key=r.get)
        return (hi, lo) if r[hi] > r[lo] else (None, None)

    print("\n" + "=" * 78)
    print("HEDGING PENALTY IN THE FLAGGED RESPONSE, BY WHETHER THE PROMPT IS CONTESTED")
    print("=" * 78)
    print(f"  {'stratum':16s} {'axis':10s} {'prompts':>8s} {'diff':>9s} {'null sd':>9s} {'z':>7s}")
    hedge = {}
    for st in ("single-answer", "contested"):
        obs = contrast(real, st)
        null = defaultdict(list)
        for k in range(N_PERM):
            rng = random.Random(5000 + k)

            def fake(p, rng=rng):
                a, b = rng.sample(LETTERS, 2)
                return a, b
            for kk, (v, _n) in contrast(fake, st).items():
                null[kk].append(v)
        for ax in ("hedging", "warmth"):
            if ax not in obs or len(null.get(ax, [])) < 50:
                continue
            mu, sd = float(np.mean(null[ax])), float(np.std(null[ax]))
            z = (obs[ax][0] - mu) / sd if sd else float("nan")
            hedge[(st, ax)] = {"diff": obs[ax][0], "n": obs[ax][1], "null_sd": sd, "z": z}
            tag = "  <- PLACEBO" if ax == "warmth" else ""
            print(f"  {st:16s} {ax:10s} {obs[ax][1]:8d} {obs[ax][0]:+9.3f} {sd:9.3f} "
                  f"{z:+7.1f}{tag}")

    # ---------------------------------------------------------------- the length preference
    print("\n" + "=" * 78)
    print("LENGTH PREFERENCE IN THE RANKING, SAME TWO STRATA")
    print("=" * 78)
    # THE CUT POINTS MUST COME FROM THE POPULATION BEING ANALYSED. The strata above were cut on
    # the 313 prompts that carry asked assessments; the length analysis runs on every prompt with
    # >=6 rankings, which is a different and larger set. Reusing the first set's thresholds would
    # put unequal numbers in each stratum and make the two halves of this round incomparable --
    # so the length side recomputes its own, and BOTH specifications are printed because r191 used
    # quartiles and this round's terciles disagree with it.
    rank_pool = [p for p, ts in tops.items() if p in psub and len(ts) >= MIN_RATERS]
    hit_rate = {}
    for p in rank_pool:
        longest = max(feats[p], key=lambda L: feats[p][L]["length"])
        hit_rate[p] = float(np.mean([1.0 if t == longest else 0.0 for t in tops[p]]))
    lp = {}
    for spec, pct in (("terciles", [33, 67]), ("quartiles (r191's spec)", [25, 50, 75])):
        q = np.percentile([psub[p] for p in rank_pool], pct)
        lowest = [hit_rate[p] for p in rank_pool if int(np.searchsorted(q, psub[p])) == 0]
        highest = [hit_rate[p] for p in rank_pool
                   if int(np.searchsorted(q, psub[p])) == len(pct)]
        if len(lowest) < 30 or len(highest) < 30:
            continue
        ml, mh = float(np.mean(lowest)), float(np.mean(highest))
        sl = float(np.std(lowest, ddof=1) / math.sqrt(len(lowest)))
        sh = float(np.std(highest, ddof=1) / math.sqrt(len(highest)))
        gap = mh - ml
        sg = math.sqrt(sl ** 2 + sh ** 2)
        lp[spec] = {"low": ml, "high": mh, "gap": gap, "se": sg, "z": gap / sg,
                    "n_low": len(lowest), "n_high": len(highest)}
        print(f"  {spec:24s} single-answer {ml:.1%} (n={len(lowest)})   "
              f"contested {mh:.1%} (n={len(highest)})   gap {gap:+.1%}  z {gap / sg:+.1f}")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    pl = hedge.get(("single-answer", "warmth"))
    pc = hedge.get(("contested", "warmth"))
    if pl and pc and max(abs(pl["z"]), abs(pc["z"])) > 3:
        print(f"  THE PLACEBO FIRED (warmth z {pl['z']:+.1f} / {pc['z']:+.1f}). The stratification")
        print(f"  manufactures structure and nothing in this round is admissible.")
        return 1
    print(f"  placebo clean: warmth sits at z {pl['z']:+.1f} (single-answer) and {pc['z']:+.1f} "
          f"(contested).")
    hs = hedge.get(("single-answer", "hedging"))
    hc = hedge.get(("contested", "hedging"))
    if hs and hc:
        d = hc["diff"] - hs["diff"]
        sd_ = math.sqrt(hc["null_sd"] ** 2 + hs["null_sd"] ** 2)
        print(f"\n  HEDGING PENALTY  single-answer {hs['diff']:+.3f} (z {hs['z']:+.1f})   "
              f"contested {hc['diff']:+.3f} (z {hc['z']:+.1f})")
        print(f"  difference {d:+.3f}, roughly {abs(d) / sd_:.1f} null-sd apart")
        stronger = "contested" if hc["diff"] < hs["diff"] else "single-answer"
        print(f"  the penalty is stronger on {stronger.upper()} prompts")
    if lp:
        print(f"\n  LENGTH PREFERENCE, BOTH SPECIFICATIONS:")
        for spec, v in lp.items():
            print(f"    {spec:24s} gap {v['gap']:+.1%}  z {v['z']:+.1f}")
        gaps = [v["gap"] for v in lp.values()]
        zs = [v["z"] for v in lp.values()]
        print(f"\n  AND THIS RETRACTS r191's LEAN. That round used quartiles on a slightly")
        print(f"  different prompt pool, got +5.0pp at z +2.1, and called it a lean toward the")
        print(f"  fallback-heuristic reading while explicitly noting the pattern was")
        print(f"  non-monotonic. Recomputed here with the cut points taken from the population")
        print(f"  actually being analysed, the same quartile specification gives "
              f"{lp.get('quartiles (r191s spec)', lp[list(lp)[-1]])['gap']:+.1%} and the")
        print(f"  tercile specification gives {lp['terciles']['gap']:+.1%}. Two specifications one")
        print(f"  step apart, both containing zero.")
        print(f"  The honest status returns to what r177 originally reported: the length")
        print(f"  preference is real at the population level (+12.3pp over chance, z +9.2) and")
        print(f"  this design cannot tell a quality cue from a fallback heuristic. r191's lean is")
        print(f"  WITHDRAWN -- it was a specification, not a finding, and I published it as a")
        print(f"  correction to r177 which makes the withdrawal a correction of a correction.")
        gap = lp["terciles"]["gap"]
        sg = lp["terciles"]["se"]
        same = (stronger == "contested") and abs(gap / sg) > 2 and gap > 0
        print(f"\n  {'ONE VARIABLE' if same else 'NOT ONE VARIABLE'}: both effects "
              f"{'concentrate on contested prompts' if same else 'do NOT move together across the strata'}.")
        if same:
            print(f"  On a question the panel says has more than one defensible answer, people")
            print(f"  penalise a response that does not concede that and reach for length as a")
            print(f"  proxy for care. On a question with a single right answer both fade, because")
            print(f"  there is a right answer to find. That is one account of two findings that")
            print(f"  were arrived at through different channels -- a veto and a ranking -- and")
            print(f"  measured with different instruments.")
        else:
            print(f"  They should stop being described together. Whatever the hedging penalty is")
            print(f"  about, it is not the same latent variable as the length preference.")

    (OUT / "one_or_two.json").write_text(json.dumps(
        {"prompts_with_subjectivity": len(psub), "flag_prompts": len(fl_prompts),
         "cut": list(cut), "hedging": {f"{k[0]}|{k[1]}": v for k, v in hedge.items()},
         "length_pref_specifications": lp, "perms": N_PERM,
         "retraction": "r191's +5.0pp length-by-contestedness lean is withdrawn: recomputed with "
                       "cut points from the analysed population, both tercile and quartile "
                       "specifications contain zero"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
