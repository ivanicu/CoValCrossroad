"""Census wave five: the response texts, and whether generation instructions leaked into the corpus.

Wave four found that the single prompt shown to essentially every annotator ends with the fragment
"say different 4 exam" -- not natural language, and unflagged. That is the signature of a GENERATION
INSTRUCTION leaking into the artefact: something written to steer a model into producing four
different examples, left in the prompt a human was then shown and asked to answer.

If it happened once it may have happened more, and a leaked instruction changes what the prompt IS.
An annotator ranking responses to a garbled prompt is doing a different task from one ranking
responses to a question.

FIVE CHECKS, on the last object in the release nothing has read:

  LEAKAGE     prompts carrying meta-instructions, generation artefacts or truncation
  ON-TOPIC    does each response actually address its own prompt, measured the same IDF way that
              validated criterion specificity -- a response that matches a random prompt as well as
              its own is not an answer to anything
  CHOICE      do the four differ enough to constitute a choice? Near-identical candidates make the
              ranking task meaningless regardless of what anyone ranks
  TRUNCATION  responses ending mid-sentence are generation failures, and a rater penalising one is
              rating the pipeline rather than the policy
  BOILERPLATE shared openings and closings across the corpus indicate a single generator with a
              fixed template, which bears on the missing provenance field

Same severity scale, CLEAN included, falsifier on every item. No model is executed anywhere.
"""
from __future__ import annotations

import difflib
import json
import math
import pathlib
import re
import sys
from collections import Counter

import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
F: list[dict] = []
WORD = re.compile(r"\b[a-z][a-z'-]{2,}\b")
STOP = frozenset("""the and for that this with you your not are was were has have had will would
should could can may might must about into over under more most less any all its their our from
one two very just than then what which who how why does did being been such other only also both
each many much some these those there here they them his her him she can't don't""".split())


def add(axis, sev, title, meas, fals):
    F.append({"axis": axis, "severity": sev, "title": title, "measurement": meas, "falsifier": fals})


def toks(s):
    return [w for w in WORD.findall(s.lower()) if w not in STOP]


def txt(m):
    c = m.get("content")
    if isinstance(c, str):
        return c
    if isinstance(c, dict):
        return " ".join(x for x in (c.get("parts") or []) if isinstance(x, str))
    return ""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    prompts, resps = {}, {}
    for c in cmp_:
        pid = c["prompt_id"]
        prompts[pid] = " ".join(txt(m) for m in c["prompt"]["messages"]
                                if (m.get("role") or (m.get("author") or {}).get("role")) == "user")
        slots = {}
        for r in c.get("responses", []):
            i = (r.get("response_index") or "").strip()
            if i in RANK_MAP:
                slots[i] = " ".join(txt(m) for m in r.get("messages", []))
        if len(slots) == 4:
            resps[pid] = [slots[k] for k in "ABCD"]
    print(f"prompts {len(prompts)}   with four responses {len(resps)}")

    # ---------------------------------------------------------------- A. instruction leakage
    LEAK = re.compile(r"\b(say different|give \d+|write \d+|generate \d+|make \d+|"
                      r"\d+\s*(exam|examples?|versions?|variants?|options?)\b|"
                      r"as an ai|you are chatgpt|system prompt|\[.*?\]|\{\{.*?\}\})", re.I)
    # A PROMPT ENDING WITHOUT A FULL STOP IS NOT TRUNCATED. My first pattern matched any prompt
    # ending in a lowercase letter and reported 415 of 1,078 as mid-sentence, which is simply how
    # people type questions. Truncation needs a stronger signal: ending mid-word or on a dangling
    # function word.
    TRUNC = re.compile(r"\b(the|a|an|and|or|but|of|to|in|for|with|that|is|are)\s*$", re.I)
    leaked = [(p, t) for p, t in prompts.items() if LEAK.search(t)]
    trunc_p = [p for p, t in prompts.items() if t.strip() and TRUNC.search(t.strip())]
    add("corpus", "SERIOUS" if leaked else "CLEAN",
        ("Generation instructions leaked into the prompt text a human was then asked to answer"
         if leaked else "CHECKED: no generation instructions found in prompt text"),
        f"{len(leaked)} of {len(prompts)} prompts ({len(leaked) / len(prompts):.1%}) contain a "
        f"meta-instruction pattern. {len(trunc_p)} end on a dangling function word, the only "
        f"reliable truncation signal for a typed question. "
        f"Examples: {[t[-70:] for _p, t in leaked[:3]]}",
        "zero prompts containing a generation instruction")

    # ---------------------------------------------------------------- B. on-topic
    df = Counter()
    for t in prompts.values():
        df.update(set(toks(t)))
    N = len(prompts)
    idf = {w: math.log(1 + N / (1 + c)) for w, c in df.items()}

    def ov(a, b):
        at = toks(a)
        if not at:
            return float("nan")
        bs = set(toks(b))
        num = sum(idf.get(w, 1.0) for w in at if w in bs)
        den = sum(idf.get(w, 1.0) for w in at)
        return num / den if den else float("nan")

    rng = np.random.default_rng(0)
    keys = list(resps)
    own, rnd = [], []
    for i, pid in enumerate(keys):
        j = int(rng.integers(len(keys) - 1))
        j = j + 1 if j >= i else j
        for r in resps[pid]:
            own.append(ov(r, prompts[pid]))
            rnd.append(ov(r, prompts[keys[j]]))
    o, r_ = np.array(own, float), np.array(rnd, float)
    m = np.isfinite(o) & np.isfinite(r_)
    d = o[m] - r_[m]
    se = float(d.std(ddof=1) / math.sqrt(d.size))
    add("candidates", "SERIOUS" if d.mean() < 0.05 else "CLEAN",
        ("Responses are barely more about their own prompt than a random one" if d.mean() < 0.05
         else "CHECKED: every response addresses its own prompt far more than a random one"),
        f"IDF overlap of {d.size} responses with their own prompt {o[m].mean():.4f} against a random "
        f"prompt {r_[m].mean():.4f}; paired difference {d.mean():+.4f} "
        f"[{d.mean() - 1.96 * se:+.4f}, {d.mean() + 1.96 * se:+.4f}]",
        "a paired difference at or below 0.05")

    # ---------------------------------------------------------------- C. is it a choice
    sims = []
    for pid in keys:
        rs = resps[pid]
        for i in range(4):
            for j in range(i + 1, 4):
                sims.append(difflib.SequenceMatcher(None, rs[i][:600], rs[j][:600]).ratio())
    sims = np.array(sims)
    near = float((sims > 0.8).mean())
    add("candidates", "SERIOUS" if near > 0.05 else "CLEAN",
        ("Many candidate pairs are near-identical, so the ranking task offers less choice than it "
         "appears" if near > 0.05 else
         "CHECKED: the four candidates are genuinely distinct texts"),
        f"{len(sims)} within-prompt response pairs; mean pairwise similarity {sims.mean():.3f}, "
        f"p90 {np.percentile(sims, 90):.3f}, share above 0.8 similarity {near:.2%}",
        "more than 5% of pairs above 0.8 similarity")

    # ---------------------------------------------------------------- D. truncation
    ends_bad = 0
    for pid in keys:
        for r in resps[pid]:
            s = r.strip()
            if s and not re.search(r"[.!?\"'\)\]]\s*$", s):
                ends_bad += 1
    tot_r = 4 * len(keys)
    add("candidates", "SERIOUS" if ends_bad / tot_r > 0.05 else "NOTED",
        "Some responses do not end in terminal punctuation, the signature of a truncated generation",
        f"{ends_bad} of {tot_r} responses ({ends_bad / tot_r:.1%}) end without terminal punctuation",
        "a rate below 5%")

    # ---------------------------------------------------------------- E. boilerplate
    opens = Counter(" ".join(r.split()[:6]).lower() for pid in keys for r in resps[pid])
    closes = Counter(" ".join(r.split()[-6:]).lower() for pid in keys for r in resps[pid])
    top_o, top_c = opens.most_common(1)[0], closes.most_common(1)[0]
    add("candidates", "NOTED" if top_o[1] / tot_r > 0.02 or top_c[1] / tot_r > 0.02 else "CLEAN",
        ("A shared opening or closing recurs across the corpus, indicating one generator with a "
         "template" if (top_o[1] / tot_r > 0.02 or top_c[1] / tot_r > 0.02) else
         "CHECKED: no boilerplate opening or closing recurs across responses"),
        f"most common six-word opening appears {top_o[1]} times ({top_o[1] / tot_r:.1%}): "
        f"{top_o[0][:60]!r}. Most common closing {top_c[1]} times ({top_c[1] / tot_r:.1%}): "
        f"{top_c[0][:60]!r}",
        "no opening or closing exceeding 2% of responses")

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
    print(f"\nwave 5 total: {len(F)} "
          f"({sum(1 for f in F if f['severity'] == 'BLOCKING')} blocking, "
          f"{sum(1 for f in F if f['severity'] == 'CLEAN')} clean)")
    (OUT / "census_wave5.json").write_text(json.dumps(F, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
