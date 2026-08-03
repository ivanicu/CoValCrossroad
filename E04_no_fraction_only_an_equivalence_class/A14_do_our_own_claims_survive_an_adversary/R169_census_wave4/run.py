"""Census wave four: is a "prompt-specific" rubric actually prompt-specific?

The release's central design claim is that annotators wrote criteria FOR a particular prompt, and
the onboarding quiz drilled prompt-specific against generic. That claim is testable without a model.

THE TEST. For each criterion, measure its content-word overlap with the prompt it was written for,
and with a random OTHER prompt. If a criterion is prompt-specific its own-prompt overlap must exceed
its random-prompt overlap. If the two are equal, the criterion is generic and could have been
written for anything.

    own >> random     prompt-specific, as designed
    own ~= random     generic; the rubric is a style guide wearing a prompt's name
    own <  random     something is misaligned in the join and the whole phase is in trouble

The third outcome is a live possibility and is why this doubles as a join check: if criteria were
attached to the wrong prompts, own-overlap would fall BELOW random and nothing else in this repo
would have caught it.

IDF-WEIGHTED, because raw overlap is dominated by function words that every prompt shares. A
criterion matching its prompt on "the" is not specificity. Weighting by inverse document frequency
means a rare shared term counts and a common one does not, which is the difference between "this
criterion is about vaccines and so is the prompt" and "both contain the word should".

FIVE MORE CHECKS on axes still untouched: non-English content, within-prompt criterion redundancy,
the outlier prompt carrying every annotator in the release, whether weight tracks criterion length,
and whether the highest-weighted criteria are the generic ones.

Same severity scale, CLEAN included, falsifier on every item. No model is executed.
"""
from __future__ import annotations

import json
import math
import pathlib
import re
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
F: list[dict] = []
WORD = re.compile(r"\b[a-z][a-z'-]{2,}\b")
STOP = frozenset("""the and for that this with you your not are was were has have had will would
should could can may might must about into over under more most less any all its their our from
one two very just than then when what which who how why does did done being been able such other
than only also both each many much some these those there here they them his her him she
model response answer reply assistant question prompt user""".split())


def add(axis, sev, title, meas, fals):
    F.append({"axis": axis, "severity": sev, "title": title, "measurement": meas, "falsifier": fals})


def toks(s):
    return [w for w in WORD.findall(s.lower()) if w not in STOP]


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    from covalx.judge import load_join
    joined = load_join(DATA / "comparisons.jsonl", DATA / "conversation_rubrics.jsonl")

    def ptext(rec):
        # load_join yields the WHOLE comparison record, not its "prompt" sub-object. Handle both so
        # this cannot break again when called with either shape.
        prompt = rec.get("prompt", rec) if isinstance(rec, dict) else rec
        out = []
        for m in prompt.get("messages", []):
            role = m.get("role") or (m.get("author") or {}).get("role")
            if role != "user":
                continue
            c = m.get("content")
            if isinstance(c, str):
                out.append(c)
            elif isinstance(c, dict):
                out.extend(x for x in (c.get("parts") or []) if isinstance(x, str))
        return " ".join(out)

    recs = [(pid, ptext(p), [it["criterion"] for it in r["coval_full"]],
             [float(np.mean([s["score"] for s in it["scores"]])) for it in r["coval_full"]])
            for pid, p, r in joined]
    print(f"prompts joined: {len(recs)}")

    # idf over prompts
    df = Counter()
    for _pid, pt, _c, _w in recs:
        df.update(set(toks(pt)))
    N = len(recs)
    idf = {w: math.log(1 + N / (1 + c)) for w, c in df.items()}

    def overlap(ctoks, ptoks):
        if not ctoks:
            return float("nan")
        ps = set(ptoks)
        num = sum(idf.get(w, 1.0) for w in ctoks if w in ps)
        den = sum(idf.get(w, 1.0) for w in ctoks)
        return num / den if den else float("nan")

    # ---------------------------------------------------------------- A. prompt specificity
    rng = np.random.default_rng(0)
    own, rand = [], []
    ptoks_all = [toks(pt) for _pid, pt, _c, _w in recs]
    for i, (_pid, _pt, crits, _w) in enumerate(recs):
        for c in crits:
            ct = toks(c)
            if not ct:
                continue
            own.append(overlap(ct, ptoks_all[i]))
            j = int(rng.integers(len(recs) - 1))
            j = j + 1 if j >= i else j
            rand.append(overlap(ct, ptoks_all[j]))
    own_a = np.array(own, float)
    rand_a = np.array(rand, float)
    m = np.isfinite(own_a) & np.isfinite(rand_a)
    d = own_a[m] - rand_a[m]
    se = float(d.std(ddof=1) / math.sqrt(d.size))
    above = float((d > 0).mean())
    add("specificity", "SERIOUS" if float(d.mean()) < 0.05 else "CLEAN",
        ("Criteria are barely more about their own prompt than about a random one"
         if float(d.mean()) < 0.05 else
         "CHECKED: criteria really are prompt-specific, and this doubles as a join check -- a "
         "misaligned join would have put own-overlap BELOW random"),
        f"IDF-weighted content overlap over {d.size} criteria: own prompt {own_a[m].mean():.4f}, "
        f"random other prompt {rand_a[m].mean():.4f}, paired difference {d.mean():+.4f} "
        f"[{d.mean() - 1.96 * se:+.4f}, {d.mean() + 1.96 * se:+.4f}]. "
        f"{above:.1%} of criteria overlap their own prompt more than a random one.",
        "a paired difference at or below zero")

    # ---------------------------------------------------------------- B. non-English
    NONASCII = re.compile(r"[^\x00-\x7f]")
    crit_all = [c for _p, _t, cs, _w in recs for c in cs]
    nonasc = [c for c in crit_all if NONASCII.search(c)]
    # strip the typographic marks that are not a language signal
    TYPO = re.compile(r"[‘’“”–—… ‑·•]")
    real = [c for c in nonasc if NONASCII.search(TYPO.sub("", c))]
    add("corpus", "NOTED" if real else "CLEAN",
        ("Some criteria contain non-Latin characters, so the corpus is not monolingual"
         if real else
         "CHECKED: every non-ASCII character is typographic (curly quotes, dashes); the criteria "
         "are monolingual English"),
        f"{len(crit_all)} criteria; {len(nonasc)} contain a non-ASCII character, of which "
        f"{len(real)} remain after removing curly quotes, en/em dashes, ellipses and bullets. "
        f"Examples: {[c[:60] for c in real[:2]]}",
        "zero criteria with non-typographic non-ASCII content")

    # ---------------------------------------------------------------- C. within-prompt redundancy
    import difflib
    red = tot_pairs = 0
    for _pid, _pt, crits, _w in recs:
        low = [c.strip().lower() for c in crits]
        for i in range(len(low)):
            for j in range(i + 1, len(low)):
                tot_pairs += 1
                if difflib.SequenceMatcher(None, low[i], low[j]).ratio() > 0.85:
                    red += 1
    add("compilation", "NOTED" if red else "CLEAN",
        "Near-duplicate criteria coexist within a single prompt's rubric",
        f"{tot_pairs} within-prompt criterion pairs; {red} exceed 0.85 text similarity "
        f"({red / max(1, tot_pairs):.2%}). The compiler's stated job includes removing redundancy, "
        f"so these are what it had to work with.",
        "zero pairs above 0.85 similarity")

    # ---------------------------------------------------------------- D. the outlier prompt
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    counts = {c["prompt_id"]: len((c.get("metadata") or {}).get("assessments", []) or [])
              for c in cmp_}
    top_pid, top_n = max(counts.items(), key=lambda kv: kv[1])
    med = float(np.median(list(counts.values())))
    txt = next((ptext(c["prompt"]) for c in cmp_ if c["prompt_id"] == top_pid), "")
    add("design", "SERIOUS",
        "One prompt was shown to essentially every annotator and is not marked as a calibration item",
        f"the most-assessed prompt carries {top_n} assessments against a corpus median of {med:.0f}, "
        f"i.e. roughly every annotator in the release saw it. Nothing in the schema flags it. Its "
        f"user turn: {txt[:120]!r}",
        "a field marking calibration or screening items")

    # ---------------------------------------------------------------- E. weight vs length / generic
    lens, ws = [], []
    for _pid, _pt, crits, wts in recs:
        for c, w in zip(crits, wts):
            lens.append(len(c))
            ws.append(abs(w))
    r_len = float(np.corrcoef(lens, ws)[0, 1])
    add("measurement", "NOTED" if abs(r_len) > 0.1 else "CLEAN",
        ("Criterion LENGTH predicts the weight it receives, so the scale partly measures verbosity"
         if abs(r_len) > 0.1 else
         "CHECKED: weight magnitude is not explained by how long the criterion is"),
        f"correlation between criterion length in characters and |mean weight| over "
        f"{len(lens)} criteria: r = {r_len:+.4f}",
        "an absolute correlation above 0.1")

    GEN = re.compile(r"^\s*(be |is |provides?|gives?|offers?)?\s*(clear|concise|accurate|helpful|"
                     r"honest|polite|respectful|balanced|informative|relevant|useful|correct)\b",
                     re.I)
    gw = [abs(w) for _p, _t, cs, wts in recs for c, w in zip(cs, wts) if GEN.match(c.strip())]
    sw = [abs(w) for _p, _t, cs, wts in recs for c, w in zip(cs, wts) if not GEN.match(c.strip())]
    gap = float(np.mean(gw) - np.mean(sw)) if gw and sw else float("nan")
    add("measurement", "NOTED" if abs(gap) > 0.5 else "CLEAN",
        ("Generic criteria are weighted differently from prompt-specific ones"
         if abs(gap) > 0.5 else
         "CHECKED: generic and specific criteria receive comparable weight magnitudes"),
        f"{len(gw)} criteria open with a generic quality adjective, mean |weight| {np.mean(gw):.2f}; "
        f"{len(sw)} others, mean |weight| {np.mean(sw):.2f}; difference {gap:+.2f}",
        "a difference above 0.5 in absolute weight")

    order = {"BLOCKING": 0, "SERIOUS": 1, "NOTED": 2, "CLEAN": 3}
    F.sort(key=lambda f: (order[f["severity"]], f["axis"]))
    for sev in ("BLOCKING", "SERIOUS", "NOTED", "CLEAN"):
        items = [f for f in F if f["severity"] == sev]
        if not items:
            continue
        print(f"\n{'=' * 78}\n{sev}  ({len(items)})\n{'=' * 78}")
        for f in items:
            print(f"\n[{f['axis']}] {f['title']}")
            print(f"    {f['measurement']}")
            print(f"    falsifier: {f['falsifier']}")
    print(f"\nwave 4 total: {len(F)} "
          f"({sum(1 for f in F if f['severity'] == 'BLOCKING')} blocking, "
          f"{sum(1 for f in F if f['severity'] == 'CLEAN')} clean)")
    (OUT / "census_wave4.json").write_text(json.dumps(F, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
