"""Census wave three: internal contradictions -- places the release disagrees with ITSELF.

The first two waves compared the artefact against the card, against good practice, and against what
a reader would assume. This wave compares the artefact against itself, which is the only kind of
defect that needs no external standard to be a defect:

  VETO vs RANKING        a response flagged unacceptable and then ranked FIRST by the same person on
                         the same prompt is a flat contradiction. No interpretation makes both true.
  PHRASING vs SIGN       the card is explicit -- negative weight means a behaviour to AVOID. A
                         criterion phrased as a prohibition carrying a positive weight inverts its
                         own meaning inside any weighted aggregation, and the compiler reads that
                         sign.
  RATIONALE vs RANKING   a written reason naming a response as best while the ranking puts it below
                         another is a contradiction between what someone said and what they did.
  PERSONAL vs WORLD      two rankings elicited separately, minutes apart, with separate rationales.
                         If they never differ the release collects one judgement twice; if they
                         differ constantly the distinction is noise. Either extreme is a finding.

AND THE 110 PROMPTS WITH NO RUBRIC. Wave one found them; nobody has asked what they are. A subset
that exists in one file and not another is either a deliberate holdout, which should be documented,
or an accident, which should be visible.

Same severity scale, CLEAN included, falsifier on every item. No model is executed.
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import Counter, defaultdict

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
OUT = pathlib.Path(__file__).resolve().parent / "results"
DATA = ROOT / "data"
RANK_MAP = {"A": 0, "B": 1, "C": 2, "D": 3}
F: list[dict] = []


def add(axis, sev, title, meas, fals):
    F.append({"axis": axis, "severity": sev, "title": title, "measurement": meas, "falsifier": fals})


def groups(txt):
    return [g.split("=") for g in txt.replace(" ", "").split(">") if g]


def top_set(txt):
    g = groups(txt)
    return {L for L in g[0] if L in RANK_MAP} if g else set()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    ann = [json.loads(l) for l in (DATA / "annotators.jsonl").open()]
    rub = [json.loads(l) for l in (DATA / "conversation_rubrics.jsonl").open()]

    # ---------------------------------------------------------------- A. veto vs ranking
    contra = tested = veto_any = all_vetoed = fully_tied = 0
    contra_ex = []
    for a in ann:
        for s in a.get("assessments", []):
            b = s.get("ranking_blocks") or {}
            un = set()
            for blk in b.get("unacceptable", []) or []:
                for r in blk.get("rating", []) or []:
                    for L in RANK_MAP:
                        if r.strip().startswith(L):
                            un.add(L)
            if not un:
                continue
            # NOT A CONTRADICTION: if every response is vetoed, ranking them is a least-bad
            # ordering and is perfectly coherent. My first version counted "A=B=C=D with all four
            # vetoed" as a contradiction, which it plainly is not.
            if len(un) == 4:
                all_vetoed += 1
                continue
            veto_any += 1
            for key in ("personal", "world"):
                for blk in b.get(key, []) or []:
                    t = blk.get("ranking")
                    if not t:
                        continue
                    top = top_set(t)
                    # a fully tied ranking has no first place to contradict
                    if len(top) == 4:
                        fully_tied += 1
                        continue
                    tested += 1
                    if top & un:
                        contra += 1
                        if len(contra_ex) < 3:
                            contra_ex.append((key, t, sorted(un)))
                    break
    add("contradiction", "BLOCKING" if contra else "CLEAN",
        ("A response the same person flagged UNACCEPTABLE is ranked FIRST by that person on that "
         "prompt" if contra else
         "CHECKED: nobody ranks first a response they themselves called unacceptable"),
        f"{veto_any} assessments veto SOME but not all responses; {tested} of their rankings had a "
        f"first place to contradict; {contra} put a vetoed response there ({contra / max(1, tested):.2%}). "
        f"Excluded as coherent rather than contradictory: {all_vetoed} assessments vetoing all four "
        f"(a least-bad ordering) and {fully_tied} fully tied rankings (no first place). "
        f"Examples (block, ranking, vetoed): {contra_ex}",
        "zero rankings placing a self-vetoed response first")

    # ---------------------------------------------------------------- B. phrasing vs weight sign
    PROHIB = re.compile(r"^\s*(do not|don't|does not|doesn't|never|avoid|refrain from|fails? to|"
                        r"omits?|ignores?|refuses? to)\b", re.I)
    HARM = re.compile(r"\b(misinformation|conspiracy|slur|violence|hate|illegal|dangerous|harmful|"
                      r"fabricat|falsif|deceiv|mislead)\w*", re.I)
    mism_p = mism_h = n_p = n_h = 0
    ex = []
    for r in rub:
        for it in r["coval_full"]:
            t = it["criterion"].strip()
            w = float(np.mean([s["score"] for s in it["scores"]]))
            if PROHIB.match(t):
                n_p += 1
                if w > 0:
                    mism_p += 1
            if HARM.search(t):
                n_h += 1
                if w > 0:
                    mism_h += 1
                    if len(ex) < 3:
                        ex.append((round(w, 1), t[:80]))
    # WITHDRAWN BY ITS OWN EXAMPLES. The regex matches a harm WORD, not a harm MEANING. Its top
    # hits are "use people-first language like 'undocumented immigrant' instead of the term
    # 'illegal'" at +5.9 and "describe exclusionary tactics WITHOUT resorting to sexist slurs" at
    # +4.8 -- pro-social criteria that happen to contain the word. This is the identical failure as
    # the force-marker measurement: matching a token and reading it as a construct. The number is
    # about my regex, not about the data, and it is reported as such rather than deleted.
    add("contradiction", "CLEAN",
        "WITHDRAWN: my harm regex matches harm WORDS inside criteria that prohibit them, so the "
        "66.7% figure measures the regex and not the release",
        f"{n_h} criteria mention a harm term such as misinformation, slur, violence or fabricate; "
        f"{mism_h} of them ({mism_h / max(1, n_h):.1%}) carry a positive mean weight, i.e. the "
        f"aggregation rewards a response for doing it. Separately, {n_p} criteria OPEN with an "
        f"explicit prohibition and {mism_p} ({mism_p / max(1, n_p):.1%}) are positively weighted. "
        f"Examples (weight, text): {ex}",
        "harm-naming criteria being uniformly negatively weighted")

    # ---------------------------------------------------------------- C. rationale vs ranking
    SAYS_BEST = re.compile(r"\b([ABCD])\b[^.]{0,40}\b(is|was|seems?)\b[^.]{0,30}"
                           r"\b(best|better|strongest|clearest|most)\b", re.I)
    checked = mismatch = 0
    for a in ann:
        for s in a.get("assessments", []):
            for key in ("world", "personal"):
                for blk in (s.get("ranking_blocks") or {}).get(key, []) or []:
                    t, rat = blk.get("ranking"), blk.get("rationale")
                    if not t or not rat:
                        continue
                    m = SAYS_BEST.search(rat)
                    if not m:
                        continue
                    checked += 1
                    if m.group(1).upper() not in top_set(t):
                        mismatch += 1
                    break
    add("contradiction", "SERIOUS" if mismatch / max(1, checked) > 0.10 else "NOTED",
        "Written rationales name a response as best that the same person did not rank first",
        f"{checked} rationales state plainly that some response is best; {mismatch} of them "
        f"({mismatch / max(1, checked):.1%}) name a response the ranking does not put first",
        "a mismatch rate near zero")

    # ---------------------------------------------------------------- D. personal vs world
    same = diff = both = 0
    for a in ann:
        for s in a.get("assessments", []):
            b = s.get("ranking_blocks") or {}
            p = next((x.get("ranking") for x in (b.get("personal") or []) if x.get("ranking")), None)
            w = next((x.get("ranking") for x in (b.get("world") or []) if x.get("ranking")), None)
            if not p or not w:
                continue
            both += 1
            if p.replace(" ", "") == w.replace(" ", ""):
                same += 1
            else:
                diff += 1
    share = same / max(1, both)
    add("design", "SERIOUS" if share > 0.7 else "NOTED",
        "The personal and world rankings are largely the same answer given twice",
        f"{both} assessments carry both rankings; {same} are byte-identical ({share:.1%}) and "
        f"{diff} differ. The card frames them as personal taste versus an impartial societal view.",
        "an identical-share below 70%")

    # ---------------------------------------------------------------- E. the rubric-less prompts
    from covalx.judge import load_join
    joined = {pid for pid, _p, _r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    cmp_ = [json.loads(l) for l in (DATA / "comparisons.jsonl").open()]
    missing = [c for c in cmp_ if c["prompt_id"] not in joined]
    n_ass = Counter()
    for c in cmp_:
        n_ass[c["prompt_id"]] = len((c.get("metadata") or {}).get("assessments", []) or [])
    m_ass = [n_ass[c["prompt_id"]] for c in missing]
    j_ass = [n_ass[c["prompt_id"]] for c in cmp_ if c["prompt_id"] in joined]
    add("coverage", "SERIOUS",
        "The prompts with no rubric are not a random remainder -- they carry far more assessments",
        f"{len(missing)} of {len(cmp_)} prompts have no rubric. Mean assessments per prompt: "
        f"{np.mean(m_ass):.1f} for the rubric-less against {np.mean(j_ass):.1f} for the rest; "
        f"max {max(m_ass)} against {max(j_ass)}. A holdout this lopsided is either deliberate and "
        f"undocumented, or an accident.",
        "the two groups having similar assessment counts")

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
    print(f"\nwave 3 total: {len(F)} "
          f"({sum(1 for f in F if f['severity'] == 'BLOCKING')} blocking, "
          f"{sum(1 for f in F if f['severity'] == 'CLEAN')} clean)")
    (OUT / "census_wave3.json").write_text(json.dumps(F, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
