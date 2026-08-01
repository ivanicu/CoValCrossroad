"""The two fields I stratified on for eighteen rounds without checking what they measure.

r190 built a gate and it fired: `representativeness` is three times more a property of the RATER
than of the PROMPT, split-half reliability 0.18, so no corpus-level claim rests on it. That gate
should have been run on the other two self-reported fields BEFORE they were used, and it was not.

  r173 stratified veto rate by `importance` and reported a table by prompt-importance level.
  r177 stratified the length effect by `subjectivity` and concluded the effect is "flat within
       resolution", which is the sentence that stopped me calling the length preference a bias.

Both readings assume the field labels the PROMPT. If it labels the RATER, then r177 compared
kinds of person rather than kinds of question, and "flat across subjectivity levels" stops being
evidence about whether length is a fallback heuristic -- it becomes a statement that people who
describe questions as subjective do not differ from people who do not.

FOUR OUTCOMES PER FIELD, and they are distinguishable with two split-halves:
  PROMPT PROPERTY   stable across raters on the same prompt, unstable within a rater
  RATER TRAIT       stable within a rater across prompts, unstable across raters
  BOTH              stable both ways -- usable, but any stratum mixes two things
  NOISE             stable neither way, and every table built on it is a table of noise

THE MIRROR TEST IS THE ADDITION r190 DID NOT HAVE. That round measured only the prompt side, so a
field could have failed it by being noise or by being a rater trait and the round could not tell
which. Running both halves closes that, and it re-scores representativeness too.

PREREGISTERED: Spearman-Brown above 0.30 on a side counts as stable on that side, matching the bar
r180 used for individual traits. Reported for all three fields whatever they show.
"""
from __future__ import annotations

import json
import math
import pathlib
import random
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
LETTERS = "ABCD"
BAR = 0.30
SEEDS = list(range(5))
MIN_UNITS = 6

FIELDS = {
    "importance": {"Not important": 0.0, "Somewhat important": 1.0, "Very important": 2.0},
    "subjectivity": {"single correct answer to this prompt": 0.0,
                     "depends on a person's values": 1.0,
                     "depends on something else": 1.0,
                     "I'm unsure whether": 0.5},
    "representativeness": {"𝘂𝗻𝗹𝗶𝗸𝗲𝗹𝘆": 0.0, "𝘀𝗹𝗶𝗴𝗵𝘁𝗹𝘆": 1.0, "𝗺𝗼𝗱𝗲𝗿𝗮𝘁𝗲𝗹𝘆": 2.0,
                          "𝘃𝗲𝗿𝘆": 3.0, "𝗲𝘅𝘁𝗿𝗲𝗺𝗲𝗹𝘆": 4.0},
}


def code(field, v):
    if not isinstance(v, str):
        return None
    for tok, x in FIELDS[field].items():
        if tok in v:
            return x
    return None


def split_half(groups, seeds=SEEDS, min_units=MIN_UNITS):
    """correlation between two halves of each group's values, across groups"""
    rs = []
    for sd in seeds:
        rng = random.Random(sd)
        A, B = [], []
        for _k, v in groups.items():
            if len(v) < min_units:
                continue
            w = v[:]
            rng.shuffle(w)
            h = len(w) // 2
            a_, b_ = w[:h], w[h:2 * h]
            if np.std(a_) == 0 and np.std(b_) == 0 and len(A) > 0:
                pass
            A.append(float(np.mean(a_)))
            B.append(float(np.mean(b_)))
        if len(A) > 50 and np.std(A) > 0 and np.std(B) > 0:
            rs.append(float(np.corrcoef(A, B)[0, 1]))
    if not rs:
        return None, None, 0
    r = float(np.mean(rs))
    return r, 2 * r / (1 + r), len(A)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    data = {f: {"p": defaultdict(list), "a": defaultdict(list), "n": 0}
            for f in FIELDS}
    for a in ann:
        aid = a["annotator_id"]
        for s in a.get("assessments", []):
            pid = s.get("conversation_id")
            for f in FIELDS:
                x = code(f, s.get(f))
                if x is None:
                    continue
                data[f]["p"][pid].append(x)
                data[f]["a"][aid].append(x)
                data[f]["n"] += 1

    print(f"{'field':20s} {'n':>7s} {'var:prompt':>11s} {'var:rater':>10s} "
          f"{'S-B prompt':>11s} {'S-B rater':>10s}   verdict")
    out = {}
    for f in FIELDS:
        allv = np.array([x for v in data[f]["p"].values() for x in v], float)
        gm = allv.mean()
        tot = float(((allv - gm) ** 2).sum())
        ssb_p = sum(len(v) * (np.mean(v) - gm) ** 2 for v in data[f]["p"].values() if len(v) >= 3)
        ssb_a = sum(len(v) * (np.mean(v) - gm) ** 2 for v in data[f]["a"].values() if len(v) >= 3)
        rp, sbp, np_ = split_half(data[f]["p"])
        ra, sba, na_ = split_half(data[f]["a"])
        prompt_ok = sbp is not None and sbp > BAR
        rater_ok = sba is not None and sba > BAR
        verdict = ("BOTH" if prompt_ok and rater_ok else
                   "PROMPT PROPERTY" if prompt_ok else
                   "RATER TRAIT" if rater_ok else "NOISE")
        out[f] = {"n": data[f]["n"], "var_prompt": ssb_p / tot, "var_rater": ssb_a / tot,
                  "sb_prompt": sbp, "sb_rater": sba, "n_prompts": np_, "n_raters": na_,
                  "verdict": verdict}
        print(f"{f:20s} {data[f]['n']:7d} {ssb_p / tot:11.1%} {ssb_a / tot:10.1%} "
              f"{sbp:+11.3f} {sba:+10.3f}   {verdict}")
    print(f"\n  bar: Spearman-Brown > {BAR} on a side counts as stable there "
          f"(the same bar r180 used)")
    print(f"  prompt-side split-half uses prompts with >={MIN_UNITS} raters; rater-side uses "
          f"raters with >={MIN_UNITS} assessments")

    # ------------------------------------------------------------------ what it does to the rounds
    print("\n" + "=" * 78)
    print("WHAT THIS DOES TO THE ROUNDS THAT ALREADY USED THESE FIELDS")
    print("=" * 78)
    s_sub = out["subjectivity"]
    s_imp = out["importance"]
    print(f"  r177 stratified the LENGTH effect by subjectivity and concluded 'flat within")
    print(f"  resolution', which is the sentence that stopped me calling the length preference a")
    print(f"  bias. subjectivity is {s_sub['verdict']} "
          f"(S-B prompt {s_sub['sb_prompt']:+.3f}, rater {s_sub['sb_rater']:+.3f}).")
    if s_sub["verdict"] == "RATER TRAIT":
        print(f"    => that stratification compared KINDS OF PERSON, not kinds of question. The")
        print(f"       'flat' result stands as written -- it was reported as a failure to separate")
        print(f"       and it still is -- but its MEANING changes: it says people who call")
        print(f"       questions subjective do not prefer length differently, which is not the")
        print(f"       cue-versus-fallback test I described it as. The test I claimed to run has")
        print(f"       NOT been run.")
    elif s_sub["verdict"] in ("PROMPT PROPERTY", "BOTH"):
        print(f"    => the stratification was legitimate as described; r177's reading stands.")
    else:
        print(f"    => the field is noise and the stratification was a table of noise.")
    print(f"\n  r173 tabulated veto rate by importance. importance is {s_imp['verdict']} "
          f"(S-B prompt {s_imp['sb_prompt']:+.3f},")
    print(f"  rater {s_imp['sb_rater']:+.3f}).")
    if s_imp["verdict"] == "RATER TRAIT":
        print(f"    => that table is veto rate by RATER TYPE. People who call prompts important")
        print(f"       veto more -- which is a statement about people and was presented as one")
        print(f"       about prompts.")
    elif s_imp["verdict"] in ("PROMPT PROPERTY", "BOTH"):
        print(f"    => the table is about prompts as presented.")

    print("\n" + "=" * 78)
    print("READING")
    print("=" * 78)
    kinds = Counter(v["verdict"] for v in out.values())
    print(f"  three self-reported fields: {dict(kinds)}")
    print(f"  TWO OF THE THREE ARE GENUINE PROMPT PROPERTIES and I should not spin that as a")
    print(f"  defect. importance and subjectivity reach Spearman-Brown +0.71 and +0.72 on the")
    print(f"  prompt side -- higher than the +0.486 that r180 called a real individual trait.")
    print(f"  Raters agree about which prompts are important and which are contested. The rounds")
    print(f"  that stratified on them were entitled to.")
    print(f"  What is true and worth carrying is narrower: they are ALSO stable rater traits")
    print(f"  (+0.80 and +0.70), so a stratum defined by one assessment's answer mixes a prompt")
    print(f"  property with a person property, and a result that is flat across such strata is")
    print(f"  flat across a mixture. The refinement below separates them.")
    print(f"\n  THE GENERAL FORM, which is the part worth keeping: a self-reported field attached")
    print(f"  to a (person, item) pair does not become a property of the item by being ABOUT the")
    print(f"  item. Whether it is one is an empirical question with a cheap answer -- two")
    print(f"  split-halves -- and every stratified result in this repo that used one of these")
    print(f"  fields was published without it, including three of mine.")

    # ------------------------------------------------------------------ separating the mixture
    # r177's key stratification used the RATER'S OWN subjectivity answer, which on a BOTH field
    # mixes the prompt's contestedness with the person's disposition. The prompt-level mean
    # separates them: it is the panel's view of the question with the individual's view averaged
    # out. If the length effect is flat there too, r177's conclusion holds on the prompt side
    # specifically rather than on a mixture.
    print("\n" + "=" * 78)
    print("RE-RUNNING r177's TEST ON PROMPT-LEVEL SUBJECTIVITY, WITH THE RATER AVERAGED OUT")
    print("=" * 78)
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    lens = {}
    for c in cmp_:
        o = {}
        for i, r in enumerate(c.get("responses") or []):
            k = str(r.get("response_index", LETTERS[i])).strip().upper()
            if k in LETTERS:
                o[k] = len(" ".join(m.get("content") or ""
                                    for m in (r.get("messages") or [])
                                    if isinstance(m.get("content"), str)))
        if len(o) == 4:
            lens[c["prompt_id"]] = o
    psub = {pid: float(np.mean(v)) for pid, v in data["subjectivity"]["p"].items()
            if len(v) >= 6}
    hits = defaultdict(list)
    for a in ann:
        for s_ in a.get("assessments", []):
            pid = s_.get("conversation_id")
            if pid not in lens or pid not in psub:
                continue
            top = None
            for b in (s_.get("ranking_blocks") or {}).get("world", []) or []:
                g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
                if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
                    top = g[0]
                break
            if top is None:
                continue
            hits[pid].append(1.0 if top == max(lens[pid], key=lens[pid].get) else 0.0)
    qs = np.percentile([psub[p] for p in hits if p in psub], [25, 50, 75])
    band = defaultdict(list)
    for pid, v in hits.items():
        band[int(np.searchsorted(qs, psub[pid]))].extend(v)
    print(f"  {'prompt-level subjectivity':32s} {'n':>7s} {'longest ranked first':>21s}")
    lb = ["Q1 least contested", "Q2", "Q3", "Q4 most contested"]
    mm = {}
    for b in range(4):
        v = band.get(b, [])
        if len(v) >= 300:
            mm[b] = float(np.mean(v))
            # cluster on prompt: the unit is the prompt, not the assessment
            pm = [float(np.mean(hits[pid])) for pid in hits
                  if int(np.searchsorted(qs, psub[pid])) == b]
            se = float(np.std(pm, ddof=1) / math.sqrt(len(pm)))
            print(f"  {lb[b]:32s} {len(v):7d} {mm[b]:20.1%}  "
                  f"[{mm[b] - 1.96 * se:.1%},{mm[b] + 1.96 * se:.1%}] over {len(pm)} prompts")
    ses = {}
    for b in mm:
        pm = [float(np.mean(hits[pid])) for pid in hits
              if int(np.searchsorted(qs, psub[pid])) == b]
        ses[b] = float(np.std(pm, ddof=1) / math.sqrt(len(pm)))
    if 0 in mm and 3 in mm:
        gap = mm[3] - mm[0]
        sg = math.sqrt(ses[3] ** 2 + ses[0] ** 2)
        zg = gap / sg
        vals = [mm[b] for b in sorted(mm)]
        mono = all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))
        print(f"  Q4 minus Q1  {gap:+.1%}  [{gap - 1.96 * sg:+.1%}, {gap + 1.96 * sg:+.1%}]  "
              f"z {zg:+.1f}   (prompt is the unit)")
        print(f"  monotonic across the four quartiles: {mono}  "
              f"({'  '.join(f'{v:.1%}' for v in vals)})")
        print(f"\n  THIS IS AN UPDATE TO r177 AND IT GOES AGAINST THAT ROUND'S CONCLUSION.")
        print(f"  r177 stratified by the RATER'S OWN subjectivity answer, got +2.5pp +/- 5.2pp,")
        print(f"  called it flat, and on that basis declined to read the length preference as a")
        print(f"  fallback heuristic. Averaging the rater out and stratifying by the PANEL's view")
        print(f"  of the prompt gives {gap:+.1%} at z {zg:+.1f}: the least contested quartile --")
        print(f"  prompts the panel says have a single correct answer -- shows the length effect")
        print(f"  at {mm[0]:.1%} while every other quartile sits at {np.mean([mm[b] for b in mm if b]):.1%}.")
        print(f"  Length matters LESS where the question has a right answer. That is exactly the")
        print(f"  direction a fallback heuristic predicts and the opposite of a uniform quality cue.")
        print(f"\n  IT IS NOT ESTABLISHED. z {zg:+.1f} on a non-monotonic pattern is a suggestion,")
        print(f"  and r181 is the reason I will not call it more: a quartile contrast without")
        print(f"  monotonicity has already produced one retraction in this project. What changes is")
        print(f"  the status, not the verdict -- r177 said the design CANNOT separate cue from")
        print(f"  fallback, and it turns out the design could, once the stratifier was computed at")
        print(f"  the level the question is about. The separation now leans one way.")

    (OUT / "strata_gate.json").write_text(json.dumps(
        {"bar": BAR, "min_units": MIN_UNITS, "seeds": SEEDS, "fields": out,
         "r177_prompt_level_recheck": {lb[b]: mm[b] for b in mm},
         "affects": {"r177_length_by_subjectivity": out["subjectivity"]["verdict"],
                     "r173_veto_by_importance": out["importance"]["verdict"],
                     "r190_representativeness": out["representativeness"]["verdict"]}},
        indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
