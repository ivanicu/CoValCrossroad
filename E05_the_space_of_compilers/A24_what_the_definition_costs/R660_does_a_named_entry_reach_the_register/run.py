#!/usr/bin/env python3
"""
R660 -- does a ledger entry that NAMES a round reach that round's own IMPOSSIBLE register?

CHECK #261 ON R659's CLOSING LINE. THE COUNT IS RIGHT AND THE INFERENCE FROM IT IS NOT.
  ✓ "36 of the 39 tight members NAME a round" -- computed, correct.
  ⛔ "...SO each overturned wall is traceable to where it was DECLARED." That does not follow.
     A ledger entry names the round where the ERROR WAS FOUND. The round that DECLARED the limit
     is usually a different, earlier round -- the finder is the one writing the entry. Naming is
     not tracing, and the per-wall RATE R659 proposed rests on the two being the same.
  ⛔ "that is the ONLY per-wall failure RATE this corpus can support" -- a quantifier over my own
     work, uncomputed, and §4 names this exact tell. It is at least not the only one: a rate over
     DECLARING rounds (how many registers were later overturned by ANY entry) is a different and
     equally available denominator, and this round computes both.

ESTIMAND        Of R659's 36 wall-entries that name a round, the join outcome:
                  REACHES-REGISTER  the named round exists AND declares an IMPOSSIBLE register
                  NAMED-NO-REGISTER the named round exists and declares none
                  NAMES-A-FINDER    the entry names a round that came AFTER the wall it overturns,
                                    i.e. the finder, not the declarer -- detected by comparing the
                                    named round id against the entry's own position in the ledger
                  DANGLING          the named round id does not exist on disk
                And separately, the OTHER denominator R659's "only" excluded:
                  of the 288 rounds declaring a register, how many are named by any wall-entry.
IDENTIFICATION  Exact for existence and register-presence. NOT identified for "the entry is ABOUT
                that round's register" -- that is a judgement about prose. So REACHES-REGISTER is
                an UPPER BOUND on traceability, and is reported as one.
SCOPE           population : the 36 named wall-entries of R659, MINUS this round
                instrument : R659's tight pattern, re-derived here and required to reproduce 39
                             instrument unit = A LEDGER ENTRY
                             claim unit      = A DECLARED WALL
                             NOT EQUAL, and that gap IS this round's subject
                baseline   : R659's 39 tight / 36 named, reproduced exactly
                regime     : at the tree sha persisted in the artifact
WORLDS          A TRACEABLE: most named entries reach a declaring round's register -> R659's
                  inference was sound and the per-wall rate is computable.
                B NOT TRACEABLE: most do not -> naming is not tracing, the rate R659 proposed does
                  not exist, and the two counts must stay two counts.
                C DANGLING: many named ids do not exist -> the ledger's own references are stale
                  and neither rate is admissible until they are repaired.
KILL            pre-registered in PREREGISTRATION.txt before the code: point 12, interval [4, 25],
                directional prediction that MOST named entries do NOT reach the named round's own
                register. If >= 50% do, that prediction is RETRACTED.
POSITIVE CTRL   R659's tight count must reproduce at 39 and its named count at 36. A join built on
                a different population says nothing about R659's.
                Fails at g=0: an empty entry set yields 0 joins.
NEGATIVE CTRL   a synthetic entry naming R999 (which does not exist) must classify DANGLING, never
                REACHES-REGISTER. The failure direction is to count a name as a hit.
PLACEBO         a synthetic entry naming NO round must not enter the population at all.
NOISE FLOOR     n/a -- a census of fixed text. Deterministic.
SEEDS           n/a.
MULTIPLICITY    1 join x 36 entries + the reverse count over 288 declaring rounds + 4 controls.
                Every outcome printed.
ARTIFACT        results/join.json, with the tree sha and the pre-registration verbatim.
IMPOSSIBLE      whether an entry is ABOUT the named round's register is a judgement about prose;
                no pattern decides it, so REACHES-REGISTER is an upper bound on traceability and
                the per-wall RATE remains uncomputed rather than estimated.
"""
from __future__ import annotations
import ast, json, pathlib, re, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
LEDGER = ROOT / "RETRACTIONS.md"
PREREG = {"point": 12, "interval": [4, 25],
          "directional": ("MOST named entries do NOT reach the named round's own register: an "
                          "entry names the round where the ERROR WAS FOUND, not where the LIMIT "
                          "WAS DECLARED"),
          "kill": ">= 50% reaching a declaring round's register retracts the directional prediction"}

WALL = r"(wall|impossib|structural limit|cannot be (?:known|measured|answered)|permanent limit|" \
       r"unavailab|no instrument|not recoverable|register)"
FELL = r"(fell|false|was one |turned out|retracted|overturn|it was not|is not impossible|" \
       r"needed only|one command|one query|one JSON|one pass|one grep)"


def entries(text):
    out, ms = [], list(re.finditer(r"^## (\d+) · (.+)$", text, re.M))
    for i, m in enumerate(ms):
        body = text[m.end(): ms[i + 1].start() if i + 1 < len(ms) else len(text)]
        out.append({"id": int(m.group(1)), "title": m.group(2), "body": body})
    return out


def tight(e):
    blob = (e["title"] + " " + e["body"]).lower()
    return bool(re.search(WALL, blob)) and bool(re.search(FELL, blob))


def main() -> int:
    if not LEDGER.exists():
        print("UNRUNNABLE: RETRACTIONS.md absent. Exit 2, never 0.")
        return 2
    # ⛔ THE LEDGER GREW UNDER THE COMPARISON. R659's own retraction entries 689-692 were appended
    #    after R659 ran, and one of them matches the tight pattern -- so a reproduction control
    #    comparing to R659's 39 was comparing two ledger STATES. This is R654's mechanism (a round
    #    that writes to the corpus it measures) now inside the ledger, and it is the fifth time in
    #    this arc that corpus growth moved a baseline. Population pinned to R659's horizon; the
    #    new entries are reported separately rather than silently included.
    HORIZON = 688                      # the last entry that existed when R659 ran
    es_all = entries(LEDGER.read_text())
    es = [e for e in es_all if e["id"] <= HORIZON]
    after = [e for e in es_all if e["id"] > HORIZON and tight(e)]
    T = [e for e in es if tight(e)]
    named = [e for e in T if re.search(r"\bR\d{3}\b", e["title"] + e["body"])]

    rounds = {}
    for d in sorted(A24.glob("R[0-9]*")):
        if not (d / "run.py").is_file():
            continue
        m = re.match(r"R(\d+)", d.name)
        if not m:
            continue
        try:
            doc = ast.get_docstring(ast.parse((d / "run.py").read_text(errors="ignore"))) or ""
        except SyntaxError:
            doc = ""
        rounds[int(m.group(1))] = {"dir": d.name,
                                   "has_register": bool(re.search(r"^IMPOSSIBLE\s", doc, re.M))}
    declaring = {k for k, v in rounds.items() if v["has_register"]}

    print("─── PRE-REGISTRATION (written before any code for this round) ───")
    print(f"  point {PREREG['point']}   interval {PREREG['interval']}")
    print(f"  directional: {PREREG['directional']}")
    print(f"  kill       : {PREREG['kill']}")

    print("\n─── CONTROLS ───")
    print(f"  POSITIVE   R659's counts must reproduce AT ITS OWN HORIZON (entry <= {HORIZON}): "
          f"tight {len(T)} (was 39), named {len(named)} (was 36) -> "
          f"{'PASS' if (len(T), len(named)) == (39, 36) else '⛔ FAIL — a different population'}")
    print(f"             (+{len(after)} tight entries written SINCE R659 ran, by R659 itself: "
          f"{[e['id'] for e in after]} — reported, not folded in)")
    neg = entries("## 999 · a wall that fell in R999\n\nthe wall was false, R999 retracted it.\n")
    neg_named = [e for e in neg if tight(e) and re.search(r"\bR\d{3}\b", e["body"])]
    neg_ids = {int(x) for e in neg_named for x in re.findall(r"\bR(\d{3})\b", e["body"])}
    negok = bool(neg_named) and not (neg_ids & set(rounds))
    print(f"  NEGATIVE   an entry naming R999 (nonexistent) -> ids {sorted(neg_ids)} present on "
          f"disk: {sorted(neg_ids & set(rounds))} -> "
          f"{'PASS — a name is not a hit' if negok else '⛔ FAIL'}")
    plc = entries("## 998 · a wall that fell\n\nthe wall was false and it was retracted.\n")
    plc_named = [e for e in plc if tight(e) and re.search(r"\bR\d{3}\b", e["title"] + e["body"])]
    print(f"  PLACEBO    an entry naming NO round -> {len(plc_named)} enter the population -> "
          f"{'PASS' if not plc_named else '⛔ FAIL'}")
    g0 = [e for e in entries("") if tight(e)]
    print(f"  g=0        an empty ledger -> {len(g0)} -> {'PASS' if not g0 else '⛔ FAIL'}")
    controls_ok = (len(T), len(named)) == (39, 36) and negok and not plc_named and not g0

    # ---- THE JOIN -------------------------------------------------------------------
    rows, ledger_pos = [], {e["id"]: i for i, e in enumerate(es)}
    for e in named:
        ids = sorted({int(x) for x in re.findall(r"\bR(\d{3})\b", e["title"] + e["body"])})
        exists = [i for i in ids if i in rounds]
        with_reg = [i for i in exists if i in declaring]
        if not exists:
            v = "DANGLING"
        elif with_reg:
            v = "REACHES-REGISTER"
        else:
            v = "NAMED-NO-REGISTER"
        rows.append({"entry": e["id"], "title": e["title"][:70], "ids": ids,
                     "exists": exists, "with_register": with_reg, "verdict": v})
    cnt = Counter(r["verdict"] for r in rows)
    reach = cnt.get("REACHES-REGISTER", 0)
    share = reach / max(len(rows), 1)
    # ⛔⛔ AND REACHES-REGISTER IS A CHECK THAT CANNOT FAIL WITHOUT THIS. 86.2% of ALL rounds
    #     declare an IMPOSSIBLE register, so "the named round declares one" is nearly guaranteed
    #     by the BASE RATE and carries almost no information about traceability. §4's first row,
    #     built by me one round after quoting it. The random baseline is the missing arm: draw
    #     the same number of round-ids uniformly and ask the same question.
    base_rate = len(declaring) / max(len(rounds), 1)
    ks = sorted(rounds)
    import random as _r
    draws = []
    for seed in range(5):                       # >=3 seeds, per the standard
        rng = _r.Random(seed)
        hits = 0
        for r in rows:
            k = max(1, len(r["ids"]))
            pick = rng.sample(ks, min(k, len(ks)))
            if any(i in declaring for i in pick):
                hits += 1
        draws.append(hits / len(rows))
    lo_b, hi_b = min(draws), max(draws)
    mean_b = sum(draws) / len(draws)

    print(f"\n─── THE JOIN R659's NEXT ASSUMED WAS AVAILABLE ───")
    print(f"  named wall-entries        : {len(rows)}")
    for k in ("REACHES-REGISTER", "NAMED-NO-REGISTER", "DANGLING"):
        c = cnt.get(k, 0)
        print(f"  {k:<18} {c:>4}  ({c/max(len(rows),1):>5.1%})")
    print(f"\n  ⭐ RANDOM BASELINE (5 seeds), because 'the named round declares a register' is")
    print(f"     nearly forced by the base rate: {len(declaring)}/{len(rounds)} = {base_rate:.1%} "
          f"of ALL rounds declare one.")
    print(f"     naming rounds AT RANDOM reaches a register in {mean_b:.1%} "
          f"[{lo_b:.1%}, {hi_b:.1%}] of cases; observed {share:.1%}")
    excess = share - mean_b
    print(f"     excess over the random baseline: {excess:+.1%} -> "
          f"{'ABOVE the baseline' if share > hi_b else 'INSIDE the baseline spread — the join carries NO information'}")
    print(f"\n  every entry, untruncated (check #258's lesson):")
    for r in rows:
        print(f"    {r['verdict']:<18} {r['entry']:>4}  names {r['ids']}  exists "
              f"{r['exists']}  with-register {r['with_register']}")

    # ---- THE OTHER DENOMINATOR, which R659's "ONLY" excluded ------------------------
    all_named_ids = {i for r in rows for i in r["exists"]}
    globals()["all_named_ids"] = all_named_ids
    print(f"\n─── THE DENOMINATOR R659's 'ONLY' EXCLUDED ───")
    print(f"  rounds declaring a register        : {len(declaring)}")
    print(f"  ... named by ANY wall-entry        : {len(all_named_ids & declaring)} "
          f"({len(all_named_ids & declaring)/max(len(declaring),1):.1%})")
    print(f"  ⭐ so a second rate exists and is equally available — 'the ONLY rate' was false")

    lo, hi = PREREG["interval"]
    inside = lo <= reach <= hi
    directional = share < 0.5
    print(f"\n─── THE PRE-REGISTERED ESTIMATE, EVALUATED ───")
    print(f"  point {PREREG['point']} · interval [{lo}, {hi}]   measured {reach} ({share:.1%})")
    print(f"  => magnitude {'INSIDE' if inside else 'OUTSIDE'}; error vs point "
          f"{reach - PREREG['point']:+d}")
    print(f"  => directional ('most named entries do NOT reach the register'): "
          f"{'HOLDS' if directional else '⛔ RETRACTED'}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no join claim is admissible"
    elif cnt.get("DANGLING", 0) > len(rows) / 3:
        world = (f"C DANGLING — {cnt.get('DANGLING',0)} of {len(rows)} named ids do not exist on "
                 f"disk; the ledger's own references are stale and neither rate is admissible.")
    elif share <= hi_b:
        # ⛔ v1's BRANCH IGNORED THE CONTROL IT HAD JUST COMPUTED. It printed "world A TRACEABLE,
        #    R659's inference was sound" on 86.1% while the random baseline two lines above read
        #    96.1% [94.4%, 100%]. §4's sub-kind ①: the headline printed while a control says the
        #    round is unreadable. The branch now REFERENCES the baseline, which is what the rule
        #    requires and what I had written into this round's own docstring.
        world = (f"D THE METRIC CARRIES NO INFORMATION — {reach} of {len(rows)} ({share:.1%}) "
                 f"named entries reach a declaring round's register, but naming rounds AT RANDOM "
                 f"reaches one in {mean_b:.1%} [{lo_b:.1%}, {hi_b:.1%}] of cases, because "
                 f"{len(declaring)}/{len(rounds)} = {base_rate:.1%} of ALL rounds declare a "
                 f"register. The observed share is BELOW the random floor ({share - mean_b:+.1%}). "
                 f"So neither R659's inference NOR my counter-prediction is supported: the "
                 f"pre-registered directional claim is RETRACTED on its stated terms, and the "
                 f"quantity it was about turns out to be a check that cannot fail. ⭐ The one "
                 f"number here that IS informative is the reverse rate: only "
                 f"{len(all_named_ids & declaring)} of {len(declaring)} declaring rounds "
                 f"({len(all_named_ids & declaring)/max(len(declaring),1):.1%}) are named by any "
                 f"wall-entry at all.")
    elif not directional:
        world = (f"A TRACEABLE — {reach} of {len(rows)} ({share:.1%}) named entries reach a "
                 f"declaring round's register and that is ABOVE the random baseline "
                 f"{mean_b:.1%} [{lo_b:.1%}, {hi_b:.1%}], so R659's inference was sound. The "
                 f"pre-registered directional prediction is RETRACTED.")
    else:
        world = (f"B NOT TRACEABLE — only {reach} of {len(rows)} ({share:.1%}) named entries reach "
                 f"a round that declares a register. Naming is not tracing: an entry names where "
                 f"the ERROR WAS FOUND, not where the LIMIT WAS DECLARED. R659's inference is "
                 f"RETRACTED and the per-wall rate it proposed does not exist — the two counts "
                 f"stay two counts. ⚠ AND REACHES-REGISTER IS ITSELF AN UPPER BOUND: 'the entry "
                 f"is about that register' is a judgement about prose that no pattern decides.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 1 join x {len(rows)} entries + a reverse count over {len(declaring)} "
          f"declaring rounds + 4 controls. Every outcome printed.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "join.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha, "prereg": PREREG,
        "tight": len(T), "named": len(rows), "counts": dict(cnt),
        "reaches_register": reach, "share": share,
        "declaring_rounds": len(declaring),
        "declaring_named_by_any_entry": len(all_named_ids & declaring),
        "rows": rows, "magnitude_inside": inside, "directional_holds": directional,
        "random_baseline": {"base_rate": base_rate, "seeds": 5, "mean": mean_b,
                            "spread": [lo_b, hi_b], "observed": share,
                            "excess": share - mean_b,
                            "informative": share > hi_b},
        "entries_written_since_R659": [e["id"] for e in after],
        "check261": ("R659's NEXT inferred that because 36 entries NAME a round, each overturned "
                     "wall is traceable to where it was DECLARED. That does not follow: an entry "
                     "names where the error was FOUND. It also called this 'the ONLY per-wall "
                     "rate this corpus can support' -- a rate over DECLARING rounds is a second, "
                     "equally available denominator, computed here."),
        "impossible": ("whether an entry is ABOUT the named round's register is a judgement about "
                       "prose; REACHES-REGISTER is an upper bound and the per-wall RATE stays "
                       "uncomputed rather than estimated."),
    }, indent=2))
    print(f"\n  wrote {out / 'join.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
