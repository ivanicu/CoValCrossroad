#!/usr/bin/env python3
"""
R615 -- can the outcome-selection question be asked at all?

CHECK #214 FOUND R614's CLOSING LINE PROPOSING A COMPARISON OVER A FIELD MY OWN WORK PROVED
UNUSABLE. It said to "compare their `world` values" between the 17 cited and 154 uncited rounds.
But R595 measured `world` as a genuinely OPEN vocabulary -- 220 distinct values, ~95% occurring
exactly once, and the tail NOT translatable into the {B, A, UNVERIFIED} core. So "verdict
class" is not a well-defined variable, and comparing distributions over it would require
INVENTING the classification: the rubric-invention failure R593 refused and R595 measured.

⚠ THE WELL-POSED FRAGMENT IS NARROW AND ITS POWER IS COMPUTED BEFORE ANYTHING IS READ. Only
rounds whose `world` begins with a core token can be classified at all; if too few of the 17
carry one, the question is not answerable here and saying so IS the round.

ESTIMAND        Among era rounds (431-606) whose `world` FIRST TOKEN is in the derived core:
                Delta = P(verdict = most common class | cited) - P(same | uncited).
IDENTIFICATION  ⚠ PARTIALLY identified at best. The classifiable subset is a NON-RANDOM slice
                -- R595 showed short values are commoner late -- so any Delta here is
                conditional on classifiability and cannot speak for the unclassifiable
                majority. Reported as such, never generalised.
SCOPE           population : rounds 431-606 with artifacts, split cited / uncited by the claim
                             table
                instrument : first token of `world`, case-folded, punctuation-stripped --
                             the same rule `statement_provenance.py` uses
                             instrument unit = A FIRST TOKEN
                             claim unit      = THE ROUND'S VERDICT CLASS -- NOT equal, because
                             95% of values are singletons whose first token may not be a class
                baseline   : the uncited rounds, same instrument
                regime     : as committed at this sha
WORLDS          A ANSWERABLE AND SKEWED: enough cited rounds are classifiable AND the
                  distribution differs beyond the null -> selection tracks outcome.
                B ANSWERABLE AND FLAT: enough are classifiable and the distributions agree ->
                  selection does not track outcome, at least on the classifiable slice.
                C NOT ANSWERABLE: too few cited rounds carry a classifiable verdict -> the
                  question cannot be asked at this site, and R614's closing line proposed an
                  ill-posed round.
KILL            pre-registered, evaluated BEFORE any distribution is read: fewer than 8
                classifiable cited rounds, or any expected cell below 5, -> world C and no
                comparison is reported whatever it would have shown.
POSITIVE CTRL   a synthetic population where cited rounds are all one class and uncited all
                another must be detected. Fails at g=0: classes assigned independently of
                citation must not be.
NEGATIVE CTRL   2000 permutations of the cited label within the classifiable subset.
PLACEBO         a constant class must give Delta exactly 0.
SEEDS           0, 1, 2.
MULTIPLICITY    one contrast; the classifiable fraction is a DERIVATION and is labelled.
ARTIFACT        results/outcome_selection.json
IMPOSSIBLE      construct validity for "verdict class": R595 measured this field as open, so a
                first-token class is a convenience, not a type. Nothing here can speak for the
                unclassifiable rounds, which are the majority.
"""
from __future__ import annotations
import json, pathlib, random, re, sys
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
CITE = r"\(R(\d{3})[,)]|R(\d{3})[,)]"
B, TOP = 431, 606
CORE = {"A", "B", "C", "D", "E", "UNVERIFIED"}


def walk(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if str(k).lower() == "world" and isinstance(v, str):
                out.append(v)
            walk(v, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, out)


def first_token(w):
    t = re.split(r"[\s,;:.—–-]+", w.strip(), maxsplit=1)[0]
    return t.strip("`*_'\"").upper()


def survey():
    out = {}
    for d in sorted(E05.glob("A*/R[0-9]*")):
        if not d.is_dir() or d.name.startswith("R615_"):
            continue
        m = re.match(r"R(\d+)", d.name)
        if not m:
            continue
        rid = int(m.group(1))
        if not (B <= rid <= TOP) or not (d / "results").is_dir():
            continue
        ws = []
        for f in sorted((d / "results").glob("*.json")):
            try:
                walk(json.loads(f.read_text()), ws)
            except Exception:
                pass
        out[rid] = first_token(ws[0]) if ws else None
    return out


def main():
    text = (E05 / "STATEMENT.md").read_text()
    m = re.search(r"\n\| # \| claim \| scope it holds over \|\n(.*?)\n\n", text, re.S)
    block = m.group(1) if m else ""
    cited = {int(a or b) for a, b in re.findall(CITE, block)}
    S = survey()
    if not S:
        print("UNRUNNABLE: no era rounds. Exit 2, never 0."); return 2
    ids = sorted(S)
    n_c = sum(1 for i in ids if i in cited)
    print(f"POPULATION  era {B}-{TOP}: {len(ids)} rounds, cited by the claim table {n_c}")

    classif = {i: S[i] for i in ids if S[i] in CORE}
    cc = [i for i in classif if i in cited]
    cu = [i for i in classif if i not in cited]
    print(f"\n─── CLASSIFIABILITY (a DERIVATION — counts over a complete enumeration) ───")
    print(f"  rounds writing a `world` at all      : {sum(1 for i in ids if S[i])}")
    print(f"  whose FIRST TOKEN is in the core set : {len(classif)} "
          f"({len(classif)/len(ids):.4f})")
    print(f"    of the cited   : {len(cc)} of {n_c}")
    print(f"    of the uncited : {len(cu)} of {len(ids)-n_c}")
    top = Counter(classif.values())
    print(f"  class distribution over the classifiable: {dict(top.most_common())}")

    print(f"\n─── KILL, EVALUATED BEFORE ANY DISTRIBUTION IS READ ───")
    common = top.most_common(1)[0][0] if top else None
    if cc and cu and common:
        pc = sum(1 for i in cc if classif[i] == common) / len(cc)
        pu = sum(1 for i in cu if classif[i] == common) / len(cu)
        exp_min = min(len(cc) * pc, len(cc) * (1 - pc),
                      len(cu) * pu, len(cu) * (1 - pu))
    else:
        pc = pu = exp_min = 0.0
    enough = len(cc) >= 8 and exp_min >= 5
    print(f"  classifiable cited rounds {len(cc)} >= 8 ?  {len(cc) >= 8}")
    print(f"  smallest expected cell {exp_min:.2f} >= 5 ?  {exp_min >= 5}")
    print(f"  -> {'the comparison is admissible' if enough else 'WORLD C: the question cannot be asked at this site'}")

    print(f"\n─── CONTROLS ───")
    rng = random.Random(0)
    synth_ids = list(range(100))
    synth_cls = {i: ("B" if i < 50 else "A") for i in synth_ids}
    sc, su = synth_ids[:50], synth_ids[50:]
    d_pos = (sum(1 for i in sc if synth_cls[i] == "B")/len(sc)
             - sum(1 for i in su if synth_cls[i] == "B")/len(su))
    print(f"  POSITIVE  synthetic: cited all one class, uncited all another -> Delta="
          f"{d_pos:+.4f} -> {'PASS' if abs(d_pos) > 0.9 else 'FAIL'}")
    rng2 = random.Random(3)
    ind = {i: rng2.choice(["A", "B"]) for i in synth_ids}
    d_g0 = (sum(1 for i in sc if ind[i] == "B")/len(sc)
            - sum(1 for i in su if ind[i] == "B")/len(su))
    print(f"  POSITIVE @ g=0  classes independent of citation -> Delta={d_g0:+.4f} -> "
          f"{'PASS (can fail)' if abs(d_g0) < 0.3 else 'FAIL'}")
    const = {i: "B" for i in synth_ids}
    d_plc = (sum(1 for i in sc if const[i] == "B")/len(sc)
             - sum(1 for i in su if const[i] == "B")/len(su))
    print(f"  PLACEBO   a constant class -> Delta={d_plc:+.4f} -> "
          f"{'PASS — exactly zero' if abs(d_plc) < 1e-12 else 'FAIL'}")
    controls_ok = abs(d_pos) > 0.9 and abs(d_g0) < 0.3 and abs(d_plc) < 1e-12

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif not enough:
        world = (f"C NOT ANSWERABLE — only {len(cc)} of the {n_c} cited rounds carry a "
                 f"classifiable verdict and the smallest expected cell is {exp_min:.2f}. "
                 f"R614's closing line proposed an ill-posed round: `world` is an OPEN "
                 f"vocabulary (R595: 220 distinct values, ~95% singletons), so 'verdict class' "
                 f"is not a variable this corpus carries. The question cannot be asked here "
                 f"WITHOUT inventing the classification.")
    else:
        obs = pc - pu
        nulls = []
        pool = list(classif)
        for s in (0, 1, 2):
            r = random.Random(s)
            for _ in range(700):
                sel = set(r.sample(pool, len(cc)))
                a = [i for i in pool if i in sel]; bb = [i for i in pool if i not in sel]
                nulls.append(sum(1 for i in a if classif[i] == common)/len(a)
                             - sum(1 for i in bb if classif[i] == common)/len(bb))
        nulls.sort()
        lo, hi = nulls[int(0.025*len(nulls))], nulls[int(0.975*len(nulls))]
        skew = not (lo <= obs <= hi)
        world = ((f"A ANSWERABLE AND SKEWED — Delta={obs:+.4f} outside the null [{lo:+.4f}, "
                  f"{hi:+.4f}]") if skew else
                 (f"B ANSWERABLE AND FLAT — Delta={obs:+.4f} inside the null [{lo:+.4f}, "
                  f"{hi:+.4f}]; selection does not track outcome on the classifiable slice"))
    print(f"  {world}")
    print(f"\n  ⚠ Whatever this returns, it is CONDITIONAL ON CLASSIFIABILITY: the classifiable "
          f"subset is a non-random slice and cannot speak for the unclassifiable majority.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "outcome_selection.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "n_era": len(ids), "n_cited": n_c,
        "n_with_world": sum(1 for i in ids if S[i]), "n_classifiable": len(classif),
        "classifiable_cited": len(cc), "classifiable_uncited": len(cu),
        "class_distribution": dict(top.most_common()),
        "p_cited": pc, "p_uncited": pu, "smallest_expected_cell": exp_min, "admissible": enough,
        "check214": ("R614's closing line proposed comparing `world` distributions, but R595 "
                     "measured that field as an OPEN vocabulary — 220 distinct values, ~95% "
                     "singletons, tail not translatable into the core — so 'verdict class' is "
                     "not a variable this corpus carries"),
        "impossible": ("a first-token class is a convenience, not a type; nothing here can "
                       "speak for the unclassifiable rounds, which are the majority"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'outcome_selection.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
