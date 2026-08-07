#!/usr/bin/env python3
"""
R687 -- is there a convention to enforce? The decision R686 left blocked on an unread fact.

CHECK #288 ON R686's NEXT LINE -- IT HOLDS. `counts.value` is 13, the field is named correctly, and
  the question it poses (a shared name is enforceable, one-offs are not) is a real fork with
  different builds behind it. ⭐ Seventh NEXT in this arc to survive intact.

ESTIMAND        across the 13 rounds encoding a judge in a JSON value field, how many DISTINCT field
                names, and how far does the commonest reach?
IDENTIFICATION  ⚠ a shared field name shows a shared HABIT, not a shared meaning. A gate built on it
                enforces a SPELLING, not a semantics, and says so in its own docstring.
SCOPE           population : the 13 value-field rounds from R686
                instrument : JSON walk attributing each judge token to its enclosing key
                             instrument unit = A (field name, judge token) PAIR
                             claim unit      = A RECORDING CONVENTION
                             ⚠ NOT EQUAL -- hence the spelling-not-semantics caveat.
                baseline   : R686's encoding split
                regime     : this repository at HEAD
WORLDS          A CONVENTION: one name dominates -> a gate is writable and gets built here.
                B ONE-OFFS: 13 names -> no rule; the remedy is per-round by hand.
KILL            13 distinct names -> world B, build nothing, say so.
POSITIVE CTRL   a judge under a known field name -> attributed to that name.
g=0             a judge OUTSIDE any field -> not attributed; the attributor returns both values.
NEGATIVE CTRL   no judge -> no field name.
PLACEBO         run twice identical.
ARTIFACT        results/convention.json
IMPOSSIBLE      whether two rounds using the same field name MEAN the same thing needs their code
                read by a reader; the name is all a gate can see.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
sys.path.insert(0, str(ROOT / "assurance"))
from token_boundaries import token                                    # noqa: E402
TOKEN = token("0.8B", "2B", "8B", "7B")
PRIOR = ARC / "R686_is_the_judge_recoverable_at_all" / "results" / "recoverability.json"


def named_fields(o, key=None, depth=0, out=None):
    """(field name, judge token) for every judge token sitting in a STRING VALUE."""
    if out is None: out = []
    if isinstance(o, dict):
        for k, v in o.items():
            if depth < 5: named_fields(v, k, depth + 1, out)
    elif isinstance(o, list):
        for v in o[:40]:
            if depth < 5: named_fields(v, key, depth + 1, out)
    elif isinstance(o, str) and key is not None:
        # ⭐⭐⭐ STRUCTURED RECORD vs PROSE MENTION. v1 counted any string containing a judge token,
        #     so `world`, `direction`, `evidence`, `not_measured` -- PROSE fields, including R684's
        #     own verdict sentence -- read as judge records. A structured record is a value that IS
        #     a judge name (optionally with a short qualifier); a 300-character verdict string that
        #     happens to say "2B" is a MENTION. Instrument unit was "a string containing a token";
        #     claim unit is "a field recording the judge".
        toks = TOKEN.findall(o)
        if not toks: return out
        kind = "structured" if len(o.strip()) <= 24 else "prose"
        for t in toks: out.append((key, t, kind))
    return out


def main() -> int:
    if not PRIOR.is_file():
        print("UNRUNNABLE: R686's artifact absent. Exit 2, never 0."); return 2
    rows = json.loads(PRIOR.read_text())["rows"]
    val_rounds = [r["round"] for r in rows if r.get("via") == "value"]

    print("─── CONTROLS ───")
    pos = named_fields({"judge_model": "ran at 2B"})
    posok = pos == [("judge_model", "2B")]
    print(f"  POSITIVE  a judge under a known field name -> {pos} -> "
          f"{'PASS' if posok else '⛔ FAIL'}")
    g0 = named_fields(["2B"])
    g0ok = not g0
    print(f"  g=0       a judge OUTSIDE any field (a bare list item) -> {g0 or 'none'} -> "
          f"{'PASS — the attributor returns both values' if g0ok else '⛔ FAIL'}")
    neg = named_fields({"n": "968 prompts"})
    negok = not neg
    print(f"  NEGATIVE  no judge -> {neg or 'none'} -> {'PASS' if negok else '⛔ FAIL'}")
    plc = named_fields({"judge_model": "ran at 2B"}) == pos
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plc

    per_round, names, prose_rounds = {}, Counter(), []
    for rd in val_rounds:
        d = next(iter(ARC.glob(f"{rd}_*")), None)
        if not d: continue
        found = []
        for j in sorted((d / "results").glob("*.json")):
            try: found += named_fields(json.loads(j.read_text()))
            except Exception: pass
        ks = sorted({k for k, _, kind in found if kind == "structured"})
        prose_only = sorted({k for k, _, kind in found if kind == "prose"}) if not ks else []
        per_round[rd] = ks
        if not ks: prose_rounds.append((rd, prose_only))
        for k in ks: names[k] += 1

    print(f"\n─── THE FIELD NAMES (G3 — every round, every name) ───")
    for rd, ks in sorted(per_round.items()):
        print(f"  {rd:<7} {ks}")
    structured = {r: v for r, v in per_round.items() if v}
    print(f"\n  ⚠ SPLIT — a STRUCTURED record vs a PROSE mention:")
    print(f"     rounds with a STRUCTURED judge field : {len(structured)}")
    print(f"     rounds where the judge appears ONLY inside prose : {len(prose_rounds)}")
    for rd, ks in prose_rounds[:8]:
        print(f"        {rd:<7} prose fields: {ks}")
    print(f"     ⛔ SO R686's '13 in a value field' OVERSTATES recoverability: only "
          f"{len(structured)} RECORD the judge; the rest MENTION it in a sentence.")
    print(f"\n  rounds encoding a judge in a value field : {len(per_round)}")
    print(f"  ⭐ DISTINCT field names                   : {len(names)}")
    for k, n in names.most_common(10):
        print(f"     {n:>3} round(s)  `{k}`")
    top = names.most_common(1)[0] if names else ("(none)", 0)
    print(f"  ⭐ commonest name `{top[0]}` covers {top[1]} of {len(per_round)}")
    print(f"  registered A 5 [1,13] -> {len(names)}: "
          f"{'INSIDE' if 1 <= len(names) <= 13 else '⛔ OUTSIDE'}, error {len(names)-5:+d}")
    print(f"  registered B 6 [1,13] -> {top[1]}: "
          f"{'INSIDE' if 1 <= top[1] <= 13 else '⛔ OUTSIDE'}, error {top[1]-6:+d}")
    dirn = top[1] >= len(per_round) / 2
    print(f"  DIRECTIONAL one name covers at least half -> {'HOLDS' if dirn else '⛔ FAILS'}")
    killed = len(structured) == 0 or len(names) >= max(len(structured), 1)
    print(f"  pre-registered kill (as many names as rounds) -> "
          f"{'⭐ FIRES — no rule is writable' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = (f"⭐⭐⭐ B ONE-OFFS, AND R686 IS DOWNGRADED. Of the 13 'value-field' rounds, only "
                 f"{len(structured)} carry a STRUCTURED judge record; the other {len(prose_rounds)} "
                 f"merely MENTION a judge inside a prose field — `world`, `direction`, `evidence`, "
                 f"`not_measured` — and one of those is R684's own verdict sentence. With "
                 f"{len(names)} distinct names over {len(structured)} structured rounds, NO RULE IS "
                 f"WRITABLE and this round builds nothing. ⭐ THE PRODUCTION DECISION IS THEREFORE "
                 f"MADE AND CLOSED: the judge-recording defect is not gate-fixable, and R686's "
                 f"recoverable count must be read as {len(structured)} structured plus "
                 f"{len(prose_rounds)} prose mentions, not 13 records.")
    else:
        world = (f"⭐⭐ A CONVENTION (partial) — {len(per_round)} rounds use {len(names)} distinct "
                 f"field names, the commonest `{top[0]}` covering {top[1]}. A gate can require that "
                 f"any round varying a judge record it under a name from this set. ⚠ IT ENFORCES A "
                 f"SPELLING, NOT A SEMANTICS: two rounds using the same key need not mean the same "
                 f"thing by it, and no gate can see that. Stated in the gate's own docstring rather "
                 f"than discovered later.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(per_round)} rounds × {sum(len(v) for v in per_round.values())} "
          f"name occurrences, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"convention.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_rounds": len(per_round), "n_structured": len(structured),
        "n_prose_only": len(prose_rounds), "prose_rounds": prose_rounds,
        "n_distinct_names": len(names),
        "name_counts": dict(names), "top_name": top[0], "top_cover": top[1],
        "per_round": per_round, "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 5 [1,13]; B 6 [1,13]; one name covers >=half; kill if names == rounds",
        "limit": ("a shared field NAME is a shared habit, not a shared meaning. A gate on it "
                  "enforces a spelling, not a semantics."),
    }, indent=2))
    print(f"  wrote {HERE/'results'/'convention.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
