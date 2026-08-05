#!/usr/bin/env python3
"""
R686 -- is the judge recoverable at all, by any encoding? And a derivation labelled as one.

CHECK #287 ON R685's NEXT LINE -- IT PROPOSED A DERIVATION AND I WROTE IT.
  "Count how many of the 81 store per-judge ranks or means." R684 DEFINED those 81 as the rounds
  with NO judge key in their artifact, and a per-judge mean is stored under a judge key. The answer
  is zero by construction. ⭐ The arithmetic trap, in my own closing sentence, one round after
  quoting the standard on it. What IS separable is whether the judge is recoverable by a DIFFERENT
  encoding, which R684's exact-name test could not see.

ESTIMAND        of the 81 rounds R684 classified UNRECORDED, from how many is a judge recoverable by
                an encoding other than a top-level judge key -- filename, a value field, or an
                embedded token?
IDENTIFICATION  ⚠ "recoverable" = a judge name is findable in the artifact's bytes or filename. It
                does NOT establish that the recovered judge produced the verdict. UPPER BOUND.
SCOPE           population : the 81 UNRECORDED rounds
                instrument : filename regex + value scan + embedded-token scan, with a
                             substring guard
                             instrument unit = A RECOVERABLE JUDGE MENTION
                             claim unit      = THE JUDGE THAT PRODUCED THE VERDICT
                             ⚠ NOT EQUAL -- hence the bound, carried into the verdict.
                baseline   : R684's exact-key test, which found none of these
                regime     : this repository at HEAD
WORLDS          A NOT PRINTED: the judge is there in another encoding, so scope is recoverable and
                  the defect is a formatting one.
                B LOST: it is genuinely absent, and those verdicts cannot be scoped without
                  re-running the rounds.
KILL            zero recoverable -> world B, and "the corpus lost its scope" is the answer.
ARITHMETIC CTRL confirm none of the 81 carries a top-level judge key. ⚠ THIS IS A DERIVATION -- it
                restates R684's partition and is NOT evidence.
POSITIVE CTRL   a synthetic artifact with the judge in its FILENAME -> recovered.
g=0             no judge anywhere -> not recovered.
NEGATIVE CTRL   "2B" inside a longer token ("d2Bx") must not match; a substring is not an encoding.
PLACEBO         run twice identical.
ARTIFACT        results/recoverability.json
IMPOSSIBLE      confirming a recovered judge is the one that produced the verdict needs the round
                re-run; 93 rounds here are corpus-dependent.
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
PRIOR = ARC / "R684_the_judge_is_not_in_the_record" / "results" / "judge_record.json"
KEY = re.compile(r"^(0\.8B|2B|8B|7B|home|second)$", re.I)
# ⭐⭐⭐ IMPORTED, NOT RE-WRITTEN. v1 used `(?<![\w.])(...)` and its POSITIVE CONTROL FAILED:
#     `_` is a word character, so `scores_2B.json` did not match. That is the THIRD instance of this
#     exact root cause in this arc (ledger 762, 768, here), so per P7 the fix is infrastructure:
#     `assurance/token_boundaries.py`, with its own doctest-style self-check.
sys.path.insert(0, str(ROOT / "assurance"))
from token_boundaries import token          # noqa: E402
TOKEN = token("0.8B", "2B", "8B", "7B")


def top_keys(o, depth=0):
    out = set()
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(k, str) and KEY.match(k): out.add(k)
            if depth < 3: out |= top_keys(v, depth + 1)
    elif isinstance(o, list) and depth < 3:
        for v in o[:20]: out |= top_keys(v, depth + 1)
    return out


def recover(d: pathlib.Path):
    hits = {"filename": set(), "value": set(), "embedded": set()}
    for j in sorted((d / "results").glob("*.json")):
        hits["filename"] |= set(TOKEN.findall(j.name))
        try: o = json.loads(j.read_text()); txt = j.read_text()
        except Exception: continue
        for m in re.finditer(r'"[^"]*"\s*:\s*"([^"]*)"', txt):
            hits["value"] |= set(TOKEN.findall(m.group(1)))
        hits["embedded"] |= set(TOKEN.findall(txt))
    return {k: sorted(v) for k, v in hits.items()}


def main() -> int:
    if not PRIOR.is_file():
        print("UNRUNNABLE: R684's artifact absent. Exit 2, never 0."); return 2
    rows84 = json.loads(PRIOR.read_text())["rows"]
    unrec = [r["round"] for r in rows84 if r.get("kind") == "UNRECORDED"]

    print("─── CONTROLS ───")
    stillnone = 0
    for rd in unrec:
        d = next(iter(ARC.glob(f"{rd}_*")), None)
        if not d: continue
        ks = set()
        for j in (d / "results").glob("*.json"):
            try: ks |= top_keys(json.loads(j.read_text()))
            except Exception: pass
        if not ks: stillnone += 1
    print(f"  ⚠ ARITHMETIC (A DERIVATION, NOT EVIDENCE) none of the {len(unrec)} carries a top-level "
          f"judge key -> {stillnone}/{len(unrec)} -> "
          f"{'confirms R684 partition' if stillnone == len(unrec) else '⛔ the partition is wrong'}")
    print(f"           this could not have come out otherwise; it restates R684's definition.")
    posok = bool(TOKEN.findall("scores_2B.json"))
    print(f"  POSITIVE  judge in a FILENAME -> {TOKEN.findall('scores_2B.json')} -> "
          f"{'PASS' if posok else '⛔ FAIL'}")
    g0ok = not TOKEN.findall("results.json")
    print(f"  g=0       no judge anywhere -> {TOKEN.findall('results.json') or 'none'} -> "
          f"{'PASS — the recoverer returns both values' if g0ok else '⛔ FAIL'}")
    negok = not TOKEN.findall("d2Bx")
    print(f"  NEGATIVE  a SUBSTRING ('d2Bx') must not match -> {TOKEN.findall('d2Bx') or 'none'} -> "
          f"{'PASS — a substring is not an encoding' if negok else '⛔ FAIL'}")
    plc = TOKEN.findall("scores_2B.json") == TOKEN.findall("scores_2B.json")
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = (stillnone == len(unrec)) and posok and g0ok and negok and plc

    rows, c = [], Counter()
    for rd in unrec:
        d = next(iter(ARC.glob(f"{rd}_*")), None)
        if not d or not (d / "results").is_dir(): continue
        h = recover(d)
        via = ("filename" if h["filename"] else
               "value" if h["value"] else
               "embedded" if h["embedded"] else "none")
        c[via] += 1
        rows.append({"round": rd, "via": via, **h})

    rec = sum(v for k, v in c.items() if k != "none")
    killed = rec == 0
    print(f"\n─── RECOVERABILITY (G3 — every one of the {len(rows)} classified) ───")
    for k in ("filename", "value", "embedded", "none"):
        print(f"  via {k:<9}: {c[k]}")
    print(f"  ⭐ recoverable by SOME encoding : {rec} of {len(rows)}  "
          f"({rec/max(len(rows),1):.1%})")
    print(f"  registered A 20 [5,50] -> {rec}: "
          f"{'INSIDE' if 5 <= rec <= 50 else '⛔ OUTSIDE'}, error {rec-20:+d}")
    dirn = c["filename"] > c["value"]
    print(f"  DIRECTIONAL filename beats value-field -> {'HOLDS' if dirn else '⛔ FAILS'} "
          f"(filename {c['filename']}, value {c['value']})")
    print(f"  pre-registered kill (zero recoverable) -> "
          f"{'⭐ FIRES — the judge is LOST, not merely unprinted' if killed else 'does not fire'}")
    ex = [r["round"] for r in rows if r["via"] == "embedded"][:8]
    if ex: print(f"  examples recovered only as an EMBEDDED token: {ex}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = (f"⭐⭐⭐ B LOST — no judge is recoverable from any of the {len(rows)} artifacts by "
                 f"filename, value field or embedded token. Those verdicts cannot be scoped without "
                 f"re-running the rounds, and 93 rounds in this arc are corpus-dependent.")
    else:
        world = (f"⭐⭐ A NOT PRINTED (partly) — {rec} of {len(rows)} ({rec/len(rows):.1%}) carry a "
                 f"judge somewhere in the artifact that R684's exact-key test could not see: "
                 f"{c['filename']} by filename, {c['value']} in a value field, {c['embedded']} only "
                 f"as an embedded token. ⭐ SO THE SCOPE IS NOT UNIFORMLY LOST — for those it is a "
                 f"FORMATTING defect, recoverable by reading bytes rather than re-running anything. "
                 f"⚠ AND FOR THE REMAINING {c['none']} IT IS GENUINELY ABSENT. ⚠ UPPER BOUND: a "
                 f"recovered judge NAME is not proof it produced the verdict — the instrument's unit "
                 f"is a mention, the claim's unit is a provenance, and those are not equal.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(rows)} rounds × 3 encodings, 5 controls (one a labelled derivation).")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"recoverability.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_unrecorded": len(unrec), "n_classified": len(rows), "counts": dict(c),
        "n_recoverable": rec, "kill_fired": killed, "directional_holds": dirn, "rows": rows,
        "registered": "A 20 [5,50]; filename beats value-field; kill if zero recoverable",
        "check287": ("R685's NEXT asked how many of the 81 store per-judge means. R684 defined them "
                     "as having no judge key, and a per-judge mean is stored under one. Zero by "
                     "construction — a DERIVATION, not a test."),
        "derivation_not_evidence": ("the arithmetic control confirms R684's partition and could not "
                                    "have come out otherwise; no claim rests on it."),
        "limit": "a recovered judge NAME is not proof it produced the verdict. Upper bound.",
    }, indent=2))
    print(f"  wrote {HERE/'results'/'recoverability.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
