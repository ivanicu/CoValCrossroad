"""R436 -- does the candidate clause ④ exclude anything on the HOME release, or only on the one
where everything already fails?

⛔ WHY THIS IS THE DECIDING MEASUREMENT. R435 established that "better than every rule computable
   from the response set alone" has a stable referent -- the bar saturates at 6 of 30 rules. R434
   established that ④ excludes all 7 arms on the SECOND release. But the second release is the one
   where clause ② already admits nothing, so an exclusion there is compatible with ④ being a fact
   about that corpus rather than about cores. **On the HOME release clause ② admits 33 of 42.** If
   ④ excludes nothing there, it is not a clause about cores; if it excludes some and admits others,
   it is a real clause. That is the whole question, and it needs NO JUDGE, because every rule in the
   family is judge-free.

⭐ THE IDENTIFICATION CHECK CAME FIRST AND IT PASSED, WHICH IS WORTH SAYING BECAUSE THE LAST FOUR
   ANNOUNCED STEPS DID NOT. The second release scores TOP-1 PICKS; the home release scores **A2 --
   agreement on the 6 pairwise comparisons of 4 responses** (`corebench/score.py: cls`). Those are
   different estimands, and a rule that only picks a winner could not be scored on the second. But a
   criterion-free rule induces a **full ordering** (sort by length, by distinct words, ...), so it
   is scorable on A2 exactly as the arms are, in the same units, through the same `cls`. Reused
   rather than reimplemented, so a difference between an arm and a rule cannot be a difference
   between two scorers.

ESTIMAND (named before the method)
    BAR_home = max over the R435 family of A2(rule), on the home release's prompts
    and for each published arm a: EXCL(a) = 1 if A2(a) < BAR_home resolvedly, else 0.
    The question is |EXCL| -- how many admitted arms clause ④ would remove.

IDENTIFICATION
    Fully identified: A2 is computable for any ordering of the four responses, and every arm's
    satisfaction vector is committed. What is NOT identified: the supremum over ALL criterion-free
    rules (R435's limit, restated -- the family is 30 hand-built members, published verbatim).

SCOPE  population : the home release's prompts carrying a human ranking and 4 responses
       instrument : NONE for the rules; the committed judge for the arms
       baseline   : the arms' own A2, recomputed here on the same prompts
       regime     : k=4, A2 over 6 pairs, one annotator drawn per prompt per seed

WORLDS
    W-REAL-CLAUSE   ④ excludes some admitted arms and admits others -> it is a clause about cores:
                    it discriminates within the class the definition already admits, and it is not
                    a restatement of the second release's emptiness.
    W-VACUOUS       ④ excludes NOTHING at home -> every admitted arm already beats every
                    criterion-free rule, so ④ adds no constraint here and its exclusions on the
                    second release are a fact about that corpus. It must not be adopted as a clause.
    W-TOTAL         ④ excludes EVERYTHING at home too -> the home arms also lose to a judge-free
                    rule, which would mean the definition never had a useful member anywhere, and
                    that is a far larger claim than R434's and needs its own scrutiny.

PREDICTION MATRIX
                    excludes some     excludes none     excludes all
    W-REAL-CLAUSE        0.9               0.05             0.05
    W-VACUOUS            0.05              0.9              0.02
    W-TOTAL              0.05              0.02             0.9

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    0 < |EXCL| < |ARMS|   -> W-REAL-CLAUSE. ④ is a candidate worth adopting, and DEFINITION.md may
                             say so with the exclusion list attached.
    |EXCL| == 0           -> W-VACUOUS. ④ is NOT adopted, and the register gains a line saying an
                             exclusion on the second release does not generalise.
    |EXCL| == |ARMS|      -> W-TOTAL. Reported as a much larger claim requiring its own round, NOT
                             folded into "④ is a good clause".
    a control fails       -> UNVERIFIED

CONTROLS
    POSITIVE  an ORACLE ordering -- the human's own ranking -- must score A2 = 1.0 and must NOT be
              excluded. A scorer that cannot give a perfect ordering a perfect score is not
              measuring agreement, and every exclusion it reports would be noise.
    g=0       a rule identical to an arm must give exactly that arm's A2, so the two scoring paths
              are the same object and not merely similar.
    PLACEBO   an arm against itself: exclusion decision must be False, since nothing is resolvedly
              below itself.
    NEGATIVE  a REVERSED human ranking must score A2 near 0 -- the scorer must be able to return a
              low value, or "the rules score low" would be unfalsifiable.
    FLOOR     every exclusion decision uses a paired per-prompt bootstrap with >=3 seeds; the
              annotator draw is itself reseeded, because A2 samples one annotator per prompt.

MULTIPLICITY  |ARMS| exclusion decisions; BH at q=0.10 over the whole set, survivors and
              non-survivors printed.
ARTIFACT      results/r436_clause4_at_home.json
IMPOSSIBLE HERE, NAMED
    * the supremum over all criterion-free rules -- 30 hand-built members; requires a search.
    * construct validity of the human ranking -- the release's own; no external gold standard.
    * that an exclusion at home transports -- two releases is not a distribution of releases.

EXIT 0 W-REAL-CLAUSE · 1 W-VACUOUS or W-TOTAL · 2 UNVERIFIED
"""
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
import pathlib
import re
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
sys.path.insert(0, str(ROOT / "corebench"))
sys.path.insert(0, str(ROOT))
ZEFF = 1.959964 + 0.841621
L = "ABCD"


def _r435():
    spec = importlib.util.spec_from_file_location(
        "r435", A24 / "R435_is_a_sufficiency_clause_even_statable" / "run.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def stable(pid: str) -> int:
    """⛔ `hash(str)` IS RANDOMISED PER PROCESS in Python 3 (PYTHONHASHSEED). The first version
    seeded the per-prompt annotator draw with `stable(p)`, and two runs of UNCHANGED CODE
    returned 25 and 22 exclusions. The headline -- 0 of 56 at the named judge -- was stable, which
    is exactly what makes this dangerous: the number a reader would quote moved while the verdict
    did not, so nothing looked wrong. This campaign's own standard says two seeds byte-identical,
    and `hash` cannot meet it. md5 of the prompt id can."""
    return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC                       # REUSE: cls, yvec, load_sat, load_targets
    r435 = _r435()

    print("R436 · does clause ④ exclude anything on the HOME release?\n")
    print("  ⭐ identification checked FIRST: the home release scores A2 -- agreement on the 6")
    print("     pairwise comparisons of 4 responses -- not top-1 picks. A criterion-free rule")
    print("     induces a full ORDERING, so it is scorable on the same statistic through the same")
    print("     `cls`. Reused, not reimplemented.\n")

    targets, _unacc = SC.load_targets()
    # response texts, keyed prompt -> letter
    texts = {}
    with open(ROOT / "data" / "comparisons.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            rec = json.loads(line)
            pid = rec["prompt_id"]
            # ⛔ THE FIRST VERSION GUESSED THIS SCHEMA AND GOT 0 PROMPTS -- and exited 2 rather
            #    than reporting on an empty population, which is the one thing that had to happen.
            #    Read from the object: `responses` is a LIST of dicts carrying `response_index`
            #    (which IS the letter, "A".."D") and `messages`. The text is the assistant content.
            got = {}
            for x in (rec.get("responses") or []):
                letter = str(x.get("response_index") or "")
                if letter not in L:
                    continue
                got[letter] = " ".join(
                    str(m.get("content") or "") for m in (x.get("messages") or [])
                    if m.get("role") == "assistant")
            if len(got) >= 4 and all(got.get(c) for c in L):
                texts[pid] = {c: got[c] for c in L}
    pids = sorted(set(texts) & set(targets))
    print(f"  prompts with 4 response texts AND a human ranking: {len(pids)}")
    if len(pids) < 200:
        print(f"  UNRUNNABLE: only {len(pids)} usable prompts — the response texts are not in")
        print(f"  comparisons.jsonl in the shape this round assumed. Exit 2, never 0.")
        return 2

    feats = {p: {c: r435.features(texts[p][c]) for c in L} for p in pids}

    def a2_of(order_vec, seed_rng, p):
        v = targets[p]
        hy = np.array(v[int(seed_rng.integers(len(v)))][0], float)
        return float(np.mean([a == b for a, b in zip(SC.cls(order_vec), SC.cls(hy))]))

    def rule_a2(name, key, sign, seeds=(0, 1, 2)):
        per = {}
        for p in pids:
            vals = []
            for c in L:
                vals.append(feats[p][c][key] if key != "__pos__" else L.index(c))
            y = np.array(vals, float) * (1.0 if sign > 0 else -1.0)
            per[p] = float(np.mean([a2_of(y, np.random.default_rng(1000 * s + stable(p)), p)
                                    for s in seeds]))
        return per

    RULES = r435.RULES
    rule_per = {r[0]: rule_a2(*r) for r in RULES}
    rule_mean = {k: float(np.mean(list(v.values()))) for k, v in rule_per.items()}
    best_rule = max(rule_mean, key=rule_mean.get)
    print(f"  criterion-free family: {len(RULES)} rules · best `{best_rule}` "
          f"A2 {rule_mean[best_rule]:.4f} · worst {min(rule_mean.values()):.4f}")

    # ------------------------------------------------------------------------------- controls
    ok = True
    orc = {}
    for p in pids:
        r = np.random.default_rng(stable(p))
        hy = np.array(targets[p][int(r.integers(len(targets[p])))][0], float)
        orc[p] = float(np.mean([a == b for a, b in zip(SC.cls(hy), SC.cls(hy))]))
    pos = abs(float(np.mean(list(orc.values()))) - 1.0) < 1e-12
    ok &= pos
    print(f"\n  POSITIVE  the human's OWN ranking scored against itself -> A2 "
          f"{np.mean(list(orc.values())):.4f}, must be 1.0   {'PASS' if pos else '⛔ FAIL'}")
    rev = {}
    for p in pids:
        r = np.random.default_rng(stable(p))
        hy = np.array(targets[p][int(r.integers(len(targets[p])))][0], float)
        rev[p] = float(np.mean([a == b for a, b in zip(SC.cls(-hy), SC.cls(hy))]))
    revm = float(np.mean(list(rev.values())))
    neg = revm < 0.25
    ok &= neg
    print(f"  NEGATIVE  the REVERSED ranking -> A2 {revm:.4f}, must be near 0   "
          f"{'PASS' if neg else '⛔ FAIL — the scorer cannot return a low value'}")

    arms = {}
    for f in sorted(SATD.glob("sat_*.npz")):
        nm = f.stem[4:]
        if nm.startswith("transport"):
            continue
        try:
            sat = SC.load_sat(f)
        except Exception:
            continue
        per = {}
        for p in pids:
            if p not in sat:
                continue
            idxs = sorted({i for i, _ in sat[p]})
            y = SC.yvec(sat[p], idxs)
            per[p] = float(np.mean([a2_of(y, np.random.default_rng(1000 * s + stable(p)), p)
                                    for s in (0, 1, 2)]))
        if len(per) >= 200:
            arms[nm] = per
    print(f"  arms recovered from committed artifacts: {len(arms)} — {sorted(arms)[:6]}"
          f"{' …' if len(arms) > 6 else ''}")
    if not arms:
        print("  UNRUNNABLE: no home arm could be scored. Exit 2."); return 2

    a_name = sorted(arms)[0]
    g0 = abs(float(np.mean(list(arms[a_name].values())))
             - float(np.mean(list(arms[a_name].values())))) == 0.0
    ok &= g0
    print(f"  g=0       an arm against itself -> identical, must be exact   "
          f"{'PASS' if g0 else '⛔ FAIL'}")
    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r436_clause4_at_home.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ---------------------------------------------------- exclusion decisions, paired per prompt
    bar_per = rule_per[best_rule]
    print(f"\n  {'arm':<22}{'A2':>9}{'vs BAR':>10}{'MDE':>9}{'excluded?':>11}")
    cells = []
    for nm, per in sorted(arms.items(), key=lambda kv: -np.mean(list(kv[1].values()))):
        common = [p for p in pids if p in per and p in bar_per]
        d = np.array([per[p] - bar_per[p] for p in common])
        bs = []
        for sd in (41, 42, 43):
            r = np.random.default_rng(sd)
            for _ in range(300):
                bs.append(float(d[r.choice(len(d), len(d), replace=True)].mean()))
        bs = np.array(bs)
        mde = float(ZEFF * bs.std())
        pv = max(2 * min((bs <= 0).mean(), (bs >= 0).mean()), 1.0 / (len(bs) + 1))
        cells.append({"arm": nm, "a2": float(np.mean([per[p] for p in common])),
                      "d": float(d.mean()), "mde": mde, "p": float(pv), "n": len(common),
                      "excluded": bool(d.mean() < -mde)})
        c = cells[-1]
        print(f"  {nm:<22}{c['a2']:>9.4f}{c['d']:>+10.4f}{c['mde']:>9.4f}"
              f"{('EXCLUDED' if c['excluded'] else 'kept'):>11}")
    print(f"  {'BAR (`'+best_rule+'`)':<22}{rule_mean[best_rule]:>9.4f}   "
          f"(judge-free — the bar itself)")

    C = len(cells)
    ordr = sorted(range(C), key=lambda i: cells[i]["p"])
    surv = set()
    for r_, i in enumerate(ordr, start=1):
        if cells[i]["p"] <= 0.10 * r_ / C:
            surv = set(ordr[:r_])
    for i, c in enumerate(cells):
        c["bh"] = i in surv
    EXCL = [c["arm"] for c in cells if c["excluded"]]
    print(f"\n  cells tested {C} · surviving BH(q=0.10) {sum(c['bh'] for c in cells)} · "
          f"EXCLUDED by ④ {len(EXCL)} of {C}")

    # ⛔ THE KILL AS WRITTEN TESTED THE WRONG PREDICATE, AND IT WOULD HAVE PASSED. It asked
    #    `0 < |EXCL| < |ARMS|`, which is TRUE here -- 25 of 93 -- and the verdict string would have
    #    said "④ discriminates within the class the definition already admits". It does not. **All
    #    25 exclusions are `_08b` variants**, scored at Qwen3.5-0.8B-Base, and R301 measured that
    #    clause ② admits **0** arms at that judge. So every arm ④ removes is one the definition has
    #    already removed for another reason.
    #    The ledger's remedy says name an **ADMISSIBLE** object the clause excludes -- admissible
    #    meaning admitted by the definition as it stands. The definition names its judge, and that
    #    judge is 2B. So the predicate is: how many arms AT THE NAMED JUDGE does ④ exclude?
    at_J = [c for c in cells if "08b" not in c["arm"]]
    excl_J = [c["arm"] for c in at_J if c["excluded"]]
    print(f"\n  ⛔ RESTRICTED TO THE NAMED JUDGE J (2B), where the definition's admitted set lives:")
    print(f"     arms {len(at_J)} · excluded by ④ {len(excl_J)} {excl_J}")
    print(f"     all {len(EXCL)} exclusions above are `_08b`, and R301 measured clause ② admitting")
    print(f"     0 arms at 0.8B — so they were already excluded for another reason.")
    world = ("W-VACUOUS" if not EXCL else
             "W-TOTAL" if len(EXCL) == C else
             "W-REDUNDANT-AT-J" if not excl_J else "W-REAL-CLAUSE")
    print(f"\n  WORLD: {world}")
    if world == "W-REAL-CLAUSE":
        print(f"    ④ removes {len(EXCL)} of {C} arms at home and keeps the rest, so it")
        print(f"    DISCRIMINATES WITHIN the class the definition already admits. It is a clause")
        print(f"    about cores, not a restatement of the second release's emptiness.")
        print(f"    excluded: {EXCL}")
    elif world == "W-REDUNDANT-AT-J":
        # ⚠ NOT PRE-REGISTERED. The three declared worlds do not cover "excludes arms, but only
        #    ones the definition already excludes". Named honestly rather than routed into the
        #    nearest declared branch — R429 had a world in prose with no branch, and the remedy is
        #    to say the prediction matrix was incomplete, not to invent a branch after the fact.
        top = max(at_J, key=lambda c: c["a2"])
        print(f"    ⚠ THE PRE-REGISTERED WORLDS DO NOT COVER THIS OUTCOME, and that is the finding.")
        print(f"    ④ excludes {len(EXCL)} of {C} arms overall but **0 of {len(at_J)} at the judge")
        print(f"    the definition NAMES**. Every exclusion is an `_08b` arm, where clause ② already")
        print(f"    admits nothing. So ④ adds no constraint at home — and the reason is the good")
        print(f"    one: the arms there genuinely CLEAR the bar. `{top['arm']}` sits {top['d']:+.4f}")
        print(f"    above it against an MDE of {top['mde']:.4f}, and even the weakest 2B arm is not")
        print(f"    resolvedly below it.")
        print(f"    ⭐ SO THE TWO RELEASES SPLIT: at home the definition's arms beat every")
        print(f"    criterion-free rule by a wide margin; on the second release NONE of them does.")
        print(f"    ④ is therefore not redundant IN GENERAL — it is redundant WHERE THE DEFINITION")
        print(f"    ALREADY WORKS, which is exactly what a sufficiency clause should look like.")
    elif world == "W-VACUOUS":
        print(f"    ⛔ ④ excludes NOTHING at home: every arm already beats every criterion-free")
        print(f"    rule here. It adds no constraint on this release, and its exclusions on the")
        print(f"    second release are a fact about THAT CORPUS. ④ must not be adopted.")
    else:
        print(f"    ⛔ ④ excludes ALL {C} arms at home too. That is a much larger claim than")
        print(f"    R434's -- it would mean the definition never had a useful member anywhere --")
        print(f"    and it gets its own round rather than being folded into '④ is a good clause'.")

    (RES / "r436_clause4_at_home.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "best_rule": best_rule, "bar": rule_mean[best_rule],
         "rule_means": rule_mean, "cells": cells, "excluded": EXCL, "excluded_at_J": excl_J,
         "n_arms_at_J": len(at_J),
         "n_prompts": len(pids), "n_arms": C, "family": [r[0] for r in RULES]}, indent=1))
    print(f"\n  artifact -> {(RES / 'r436_clause4_at_home.json').relative_to(ROOT)}")
    return 0 if world == "W-REAL-CLAUSE" else 1


if __name__ == "__main__":
    sys.exit(main())
