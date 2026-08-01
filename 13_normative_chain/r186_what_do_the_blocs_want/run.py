"""Five rounds on who agrees with whom, and none on what they agree ABOUT.

r183 found two coherent groups in the release, Netherlands and Mexico. r184 nearly dissolved them
into a consistency gradient; r185 showed the clustering survives holding consistency fixed, with
100% of the effect retained. So there are two real blocs, each about +4.5%, and nobody has asked
what they want.

The question is answerable because a bloc that clusters must cluster somewhere: there are prompts
where the bloc's modal choice differs from the panel's modal choice, and on those prompts two
different responses were preferred. Both responses are shipped text. Whatever the bloc wants is a
property of the response it picked and the panel did not.

SEVEN AXES, all computable from the response text, all chosen before looking:
  length            the one cue r177 measured at population level
  hedging           "it depends", "however", "some people" -- acknowledging the question is open
  directness        imperatives and second person -- telling the reader what to do
  structure         markdown lists and numbered steps
  caveat            warnings, risks, "consult a professional"
  warmth            "I understand", "that sounds", second-person empathy
  concreteness      digits, units, named specifics

THE NULL IS THE ENTIRE POINT AND IT IS NOT OPTIONAL. Take any 117 raters, find the prompts where
their modal choice differs from the panel's, and the responses they preferred WILL differ on some
axis -- that is what seven axes and a few hundred prompts buys you for free. So every axis is
scored against groups of the SAME SIZE drawn at random, 200 of them, and the reported quantity is
where the real bloc sits in that distribution. An axis that is not extreme against random groups
of matched size is not a finding about the bloc, however interpretable it sounds.

AND THE SECOND CONTROL, which catches something the first cannot: the two blocs are tested
SEPARATELY. If Netherlands and Mexico -- two groups with no obvious shared context -- independently
depart on the same axis in the same direction, that is a replication. If they depart on different
axes, then whatever each bloc is, it is not the same thing, and r184's "one pole" reading loses
its last support.
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

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
LETTERS = "ABCD"
BLOCS = ["Netherlands", "Mexico"]
MIN_BLOC = 4
MIN_OTHER = 6
N_NULL = 200

AXES = {
    "hedging": r"\b(it depends|depends on|however|although|on the other hand|some people|"
               r"many people|in some cases|generally|often|typically|may vary|not always)\b",
    "directness": r"\b(you should|you can|you need to|make sure|be sure|try to|start by|"
                  r"first,|next,|remember to)\b",
    "structure": r"(\n\s*[-*•]\s|\n\s*\d+[.)]\s)",
    "caveat": r"\b(consult|professional|doctor|lawyer|risk|danger|caution|be careful|"
              r"seek help|emergency|important to note)\b",
    "warmth": r"\b(I understand|that sounds|I'm sorry|it's okay|you're not alone|"
              r"completely normal|valid)\b",
    "concreteness": r"(\b\d+(\.\d+)?\s*(%|mg|ml|km|kg|hours?|minutes?|days?|years?|dollars?|\$)|\$\d)",
}


def top_of(s):
    for b in (s.get("ranking_blocks") or {}).get("world", []) or []:
        g = [x for x in (b.get("ranking") or "").replace(" ", "").split(">") if x]
        if g and len(g[0].split("=")) == 1 and g[0] in LETTERS:
            return g[0]
        break
    return None


def features(text):
    f = {"length": float(len(text))}
    for k, pat in AXES.items():
        f[k] = float(len(re.findall(pat, text, re.I)))
    return f


def departures(prompt_rows, members, feats, panel_mode):
    """axis deltas PER ASSESSMENT, not per prompt.

    THE FIRST VERSION OF THIS FUNCTION WAS UNDERPOWERED AND THE RUN SAID SO. It required 4+ bloc
    members on a prompt before that prompt counted, but 142 Mexican raters doing ~14 assessments
    each spread over 1078 prompts is 1.9 members per prompt -- so only 185 prompts qualified, 22
    of them departed, and every axis came back at |z| < 0.6. The Netherlands did not clear the
    filter at all. That is not a null about the blocs; it is a null about the filter.
    A per-assessment estimand uses every choice a member made: for each of their assessments,
    compare the features of the response THEY picked against the response the rest of the panel
    picked. Same question, roughly 15x the data."""
    acc = defaultdict(list)
    n_dep = n_tot = 0
    for pid, rows in prompt_rows.items():
        pm = panel_mode.get(pid)
        if pm is None:
            continue
        for aid, t in rows:
            if aid not in members:
                continue
            n_tot += 1
            if t == pm:
                continue
            n_dep += 1
            fb, fo = feats[pid].get(t), feats[pid].get(pm)
            if not fb or not fo:
                continue
            for k in fb:
                acc[k].append(fb[k] - fo[k])
    return {k: float(np.mean(v)) for k, v in acc.items() if len(v) >= 100}, n_dep, n_tot


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    feats = {}
    for c in cmp_:
        o = {}
        for i, r in enumerate(c.get("responses") or []):
            key = str(r.get("response_index", LETTERS[i])).strip().upper()
            if key in LETTERS:
                o[key] = features(" ".join(m.get("content") or ""
                                           for m in (r.get("messages") or [])
                                           if isinstance(m.get("content"), str)))
        if len(o) == 4:
            feats[c["prompt_id"]] = o

    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    prompt_rows = defaultdict(list)
    country = {}
    for a in ann:
        v = (a.get("demographics") or {}).get("country_of_residence")
        if v:
            country[a["annotator_id"]] = str(v)
        for s in a.get("assessments", []):
            t = top_of(s)
            pid = s.get("conversation_id")
            if t and pid in feats:
                prompt_rows[pid].append((a["annotator_id"], t))
    ids = list(country)
    # the panel's modal choice per prompt, computed once over everyone
    panel_mode = {}
    for pid, rows in prompt_rows.items():
        c = Counter(t for _a, t in rows)
        if len(rows) >= MIN_OTHER:
            m = [k for k, v in c.items() if v == max(c.values())]
            if len(m) == 1:
                panel_mode[pid] = m[0]
    print(f"prompts usable {len(prompt_rows)};  with a unique panel mode {len(panel_mode)};  "
          f"raters with a country {len(ids)}")

    out = {}
    for bloc in BLOCS:
        members = {i for i in ids if country[i] == bloc}
        obs, nd, ne = departures(prompt_rows, members, feats, panel_mode)
        if not obs:
            print(f"\n{bloc}: too few departure prompts")
            continue
        # NULL: random groups of the SAME SIZE
        null = defaultdict(list)
        nds = []
        for k in range(N_NULL):
            r = random.Random(4000 + k)
            fake = set(r.sample(ids, len(members)))
            o2, nd2, _ = departures(prompt_rows, fake, feats, panel_mode)
            nds.append(nd2)
            for kk, v in o2.items():
                null[kk].append(v)
        print(f"\n{'=' * 78}\n{bloc}  ({len(members)} raters)\n{'=' * 78}")
        print(f"  assessments {ne};  departures from the panel mode {nd} "
              f"({nd / max(1, ne):.1%});  random same-size groups depart {np.mean(nds):.0f} "
              f"({np.std(nds):.0f} sd)")
        print(f"  {'axis':16s} {'bloc-panel':>12s} {'null mean':>11s} {'null sd':>9s} {'z':>7s}")
        rows = []
        for k in ["length"] + list(AXES):
            if k not in obs or len(null.get(k, [])) < 30:
                continue
            mu, sd = float(np.mean(null[k])), float(np.std(null[k]))
            z = (obs[k] - mu) / sd if sd else float("nan")
            rows.append({"axis": k, "obs": obs[k], "null_mean": mu, "null_sd": sd, "z": z})
            print(f"  {k:16s} {obs[k]:+12.2f} {mu:+11.2f} {sd:9.2f} {z:+7.1f}")
        out[bloc] = {"n_members": len(members), "departures": nd, "eligible": ne, "axes": rows}

    print("\n" + "=" * 78)
    print("DO THE TWO BLOCS WANT THE SAME THING?")
    print("=" * 78)
    if len(out) == 2:
        a, b = out[BLOCS[0]]["axes"], out[BLOCS[1]]["axes"]
        za = {r["axis"]: r["z"] for r in a}
        zb = {r["axis"]: r["z"] for r in b}
        common = [k for k in za if k in zb]
        print(f"  {'axis':16s} {BLOCS[0][:12]:>12s} {BLOCS[1][:12]:>12s}   agreement")
        agree = 0
        for k in common:
            same = (za[k] > 0) == (zb[k] > 0)
            both_strong = abs(za[k]) > 2 and abs(zb[k]) > 2
            agree += 1 if (same and both_strong) else 0
            tag = "SAME direction, both strong" if same and both_strong else (
                "same sign" if same else "OPPOSITE")
            print(f"  {k:16s} {za[k]:+12.1f} {zb[k]:+12.1f}   {tag}")
        r_ = float(np.corrcoef([za[k] for k in common], [zb[k] for k in common])[0, 1])
        print(f"\n  correlation of the two z-profiles across {len(common)} axes: {r_:+.2f}")
        print(f"  axes where both blocs are strong and agree: {agree}")
        # MULTIPLICITY OVER THE WHOLE GRID, and it governs everything printed above.
        ntest = len(za) + len(zb)
        bar = 2.9                                  # ~Bonferroni for 14 tests at 5%
        survivors = [(k, za[k]) for k in za if abs(za[k]) > bar] + \
                    [(k, zb[k]) for k in zb if abs(zb[k]) > bar]
        mx = max(max(abs(v) for v in za.values()), max(abs(v) for v in zb.values()))
        print(f"\n  {ntest} axis tests across two blocs; Bonferroni-scale bar |z| > {bar}.")
        print(f"  largest |z| anywhere in the table: {mx:.1f}.  Survivors: {len(survivors)}.")
        if not survivors:
            print(f"  -> NO CONTENT SIGNATURE. Not one of seven measurable axes distinguishes what")
            print(f"     either bloc prefers from what a random group of the same size prefers.")
            print(f"     THEREFORE THE COMPARISON ABOVE IS UNINFORMATIVE and the 'same or")
            print(f"     different' question cannot be answered: comparing two profiles that are")
            print(f"     each indistinguishable from noise says nothing about whether they agree.")
            print(f"     The first draft of this section read the sign pattern anyway and")
            print(f"     concluded 'two islands'. That is reading a table whose every cell is")
            print(f"     inside its own null -- the fifth time this project has been caught doing")
            print(f"     exactly this, and the first time the catch was a multiplicity bar rather")
            print(f"     than a fresh control.")
            print(f"\n     WHAT SURVIVES: the blocs are real and their content is not these seven")
            print(f"     axes. Netherlands and Mexico raters cluster with their compatriots at")
            print(f"     +4.5% and neither length, hedging, directness, structure, caveats,")
            print(f"     warmth nor concreteness is where the clustering lives.")
        elif agree >= 2 and r_ > 0.5:
            print(f"  -> THE SAME THING. Two groups with no shared context depart from the panel")
            print(f"     on the same axes in the same direction. That is a replication, and it")
            print(f"     gives r184's 'one pole' the content it was missing.")
        elif r_ < -0.3:
            print(f"  -> OPPOSITE THINGS. The blocs pull apart, so the panel has two poles rather")
            print(f"     than one, and no single aggregate sits at either.")
        else:
            print(f"  -> NOT THE SAME THING, and not opposite either. Each bloc is internally")
            print(f"     coherent and they cohere around DIFFERENT axes. r184's 'one pole' reading")
            print(f"     loses its last support: these are two islands that happened to agree at")
            print(f"     the rate two consistent groups agree, and the content says they are not")
            print(f"     the same population.")

    print(f"\n  LIMIT: these seven axes are lexical counts, not meanings. An axis that fails here")
    print(f"  is not shown absent from the blocs' preferences -- it is shown absent from these")
    print(f"  regexes. The null protects against reading noise as structure; it cannot supply a")
    print(f"  vocabulary the axes do not have.")

    (OUT / "what_blocs_want.json").write_text(json.dumps(
        {"min_bloc": MIN_BLOC, "min_other": MIN_OTHER, "nulls": N_NULL,
         "blocs": out}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
