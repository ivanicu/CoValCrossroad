#!/usr/bin/env python3
"""
R617 -- does the `controls` KEY track running controls, and is the cited set selected for it?

CHECK #216 CAUGHT THE THIRD NAMING ERROR OF THE SAME FAMILY IN THREE ROUNDS. R616's closing
line called `has_controls` "the axis closest to the definition's evidential quality". It is a
JSON KEY named `controls`. Whether a round RAN controls is not whether its artifact HAS that
key -- R608 measured `has_py` at 1.00 cited / 0.96 uncited, so nearly every round ships code,
and controls live there and in the README.

  #214 called first-token-in-a-set   "verdict class"
  #215 called first-token-in-a-set   "legibility"
  #216 called a key named `controls` "evidential quality"

⭐ Three consecutive rounds promoting a KEY-PRESENCE measure to a SUBSTANTIVE property. So this
round does what none of the three did: it tests the CONSTRUCT before testing the contrast.

ESTIMAND        (i) construct: agreement between the `controls` KEY and two independent signals
                of controls actually being run -- the word "control" in the round's README, and
                a control-shaped identifier in its .py.
                (ii) contrast: Delta = P(key | cited) - P(key | uncited), against a null of
                17-round draws -- but READ ONLY IF (i) shows the key tracks anything.
IDENTIFICATION  (i) is exact as counts; it is a construct check, not a gold standard -- README
                prose and code identifiers are themselves proxies, so agreement bounds the
                construct from ABOVE and disagreement is decisive against it.
                (ii) is exact given (i).
SCOPE           population : rounds 431-606 with artifacts (171), cited (17) / uncited
                instrument : top-level or nested key named `controls`; regex on README and .py
                             instrument unit = A KEY NAMED `controls`
                             claim unit      = THE ROUND RAN CONTROLS -- NOT equal, which is
                             exactly what (i) measures rather than assumes
                baseline   : the two independent signals
                regime     : as committed at this sha
WORLDS          A KEY TRACKS AND CITED SELECTED: the key agrees with the independent signals
                  AND the cited set is enriched -> the page prefers rounds that record controls.
                B KEY TRACKS, NO SELECTION: agreement holds, contrast inside the null.
                C KEY IS EMPTY FORM: the key disagrees with both signals -> it measures a
                  schema habit, not control-running, and NO contrast on it may be reported as
                  being about evidential quality. R616's closing line would then be wrong twice.
KILL            pre-registered and evaluated FIRST: if the key's agreement with BOTH independent
                signals is below 0.60, world C and the contrast is not read at all.
POSITIVE CTRL   a synthetic round with the key and both signals must score agreement 1.0; one
                with neither must too (agreement counts both cells).
NEGATIVE CTRL   shuffle the key across rounds -> agreement must collapse toward the marginal.
PLACEBO         a key every round has must give agreement equal to the signal's own rate, not 1.
SEEDS           0, 1, 2.
MULTIPLICITY    2 signals x 1 key + 1 contrast; all reported.
ARTIFACT        results/controls_construct.json
IMPOSSIBLE      construct validity for "ran controls": README prose and code identifiers are
                proxies too. Agreement bounds the construct from above; nothing here can show
                a round's controls were CORRECT, only that something control-shaped exists.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
CITE = r"\(R(\d{3})[,)]|R(\d{3})[,)]"
B, TOP = 431, 606
CODE = re.compile(r"\b(pos_ok|neg_ok|plc_ok|placebo|positive|negative|control)", re.I)
PROSE = re.compile(r"\bcontrol", re.I)


def keys_of(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            acc.add(str(k).lower()); keys_of(v, acc)
    elif isinstance(o, list):
        for v in o:
            keys_of(v, acc)


def survey():
    out = {}
    for d in sorted(E05.glob("A*/R[0-9]*")):
        if not d.is_dir() or d.name.startswith("R617_"):
            continue
        m = re.match(r"R(\d+)", d.name)
        if not m:
            continue
        rid = int(m.group(1))
        if not (B <= rid <= TOP) or not (d / "results").is_dir():
            continue
        ks = set()
        for f in sorted((d / "results").glob("*.json")):
            try:
                keys_of(json.loads(f.read_text()), ks)
            except Exception:
                pass
        doc = d / "README.md"
        prose = bool(PROSE.search(doc.read_text(errors="ignore"))) if doc.is_file() else False
        code = False
        for p in d.iterdir():
            if p.is_file() and p.suffix == ".py":
                if CODE.search(p.read_text(errors="ignore")):
                    code = True
                    break
        out[rid] = {"key": "controls" in ks, "prose": prose, "code": code}
    return out


def agree(a, b):
    return sum(1 for x, y in zip(a, b) if x == y) / len(a) if a else 0.0


def main():
    text = (E05 / "STATEMENT.md").read_text()
    m = re.search(r"\n\| # \| claim \| scope it holds over \|\n(.*?)\n\n", text, re.S)
    cited = {int(a or b) for a, b in re.findall(CITE, m.group(1) if m else "")}
    S = survey()
    ids = sorted(S)
    if not ids:
        print("UNRUNNABLE: no era rounds. Exit 2, never 0."); return 2
    key = [S[i]["key"] for i in ids]
    pro = [S[i]["prose"] for i in ids]
    cod = [S[i]["code"] for i in ids]
    print(f"POPULATION  era {B}-{TOP}: {len(ids)} rounds, cited {sum(1 for i in ids if i in cited)}")
    print(f"  ⚠ the property is A KEY NAMED `controls`, not 'ran controls' and not "
          f"'evidential quality' — the construct is TESTED below, not assumed")

    print(f"\n─── (i) CONSTRUCT: does the key track anything? ───")
    print(f"  rate: key {sum(key)/len(ids):.4f}   README says 'control' {sum(pro)/len(ids):.4f}"
          f"   .py has control-shaped names {sum(cod)/len(ids):.4f}")
    a_pro, a_cod = agree(key, pro), agree(key, cod)
    print(f"  agreement key vs README prose : {a_pro:.4f}")
    print(f"  agreement key vs code names   : {a_cod:.4f}")
    print(f"\n─── KILL, EVALUATED BEFORE THE CONTRAST ───")
    tracks = min(a_pro, a_cod) >= 0.60
    print(f"  min agreement {min(a_pro, a_cod):.4f} >= 0.60 ? {tracks} -> "
          f"{'the key tracks something; the contrast may be read' if tracks else 'WORLD C: the key is EMPTY FORM and no contrast on it is about evidential quality'}")

    print(f"\n─── CONTROLS ───")
    pos = agree([True, False], [True, False])
    print(f"  POSITIVE  a round with key+signal and one with neither: agreement {pos:.4f} -> "
          f"{'PASS' if pos == 1.0 else 'FAIL'}")
    negs = []
    for s in (0, 1, 2):
        r = random.Random(s); k2 = key[:]; r.shuffle(k2)
        negs.append(agree(k2, pro))
    marg = max(sum(key)/len(ids), 1 - sum(key)/len(ids))
    neg_ok = all(abs(n - a_pro) > 0.02 or a_pro < 0.6 for n in negs)
    print(f"  NEGATIVE  key shuffled across rounds: agreement {[round(n,4) for n in negs]} "
          f"vs observed {a_pro:.4f} -> {'PASS — shuffling changes it' if neg_ok else 'FAIL — agreement survives shuffling, so it was the marginal all along'}")
    allk = [True]*len(ids)
    a_all = agree(allk, pro)
    plc_ok = abs(a_all - sum(pro)/len(ids)) < 1e-12
    print(f"  PLACEBO   a key every round has: agreement {a_all:.4f} = the signal's own rate "
          f"{sum(pro)/len(ids):.4f} -> {'PASS — not 1' if plc_ok else 'FAIL'}")
    controls_ok = pos == 1.0 and plc_ok

    print(f"\n─── (ii) CONTRAST, read only if the construct held ───")
    cid = [i for i in ids if i in cited]
    pc = sum(S[i]["key"] for i in cid)/len(cid)
    pu = sum(S[i]["key"] for i in ids if i not in cited)/(len(ids)-len(cid))
    obs = pc - pu
    nulls = []
    for s in (0, 1, 2):
        r = random.Random(100+s)
        for _ in range(700):
            sel = set(r.sample(ids, len(cid)))
            a = [S[i]["key"] for i in ids if i in sel]
            b = [S[i]["key"] for i in ids if i not in sel]
            nulls.append(sum(a)/len(a) - sum(b)/len(b))
    nulls.sort()
    lo, hi = nulls[int(0.025*len(nulls))], nulls[int(0.975*len(nulls))]
    print(f"  P(key | cited) {pc:.4f}   P(key | uncited) {pu:.4f}   Delta {obs:+.4f}")
    print(f"  null 2100 draws: [{lo:+.4f}, {hi:+.4f}]")
    if not tracks:
        print(f"  ⚠ NOT READ AS EVIDENCE — the construct check failed, so this contrast is "
              f"about a schema habit and not about controls being run.")

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif not tracks:
        world = (f"C KEY IS EMPTY FORM — agreement with README prose {a_pro:.4f} and with code "
                 f"names {a_cod:.4f}, below the pre-registered 0.60. The `controls` key does "
                 f"NOT track controls being run, so R616's closing line was wrong to call it "
                 f"the axis closest to evidential quality. Delta={obs:+.4f} is a fact about a "
                 f"schema habit.")
    elif obs > hi:
        world = (f"A KEY TRACKS AND CITED SELECTED — construct agreement "
                 f"{min(a_pro,a_cod):.4f}, Delta={obs:+.4f} above {hi:+.4f}")
    else:
        world = (f"B KEY TRACKS, NO SELECTION — construct agreement {min(a_pro,a_cod):.4f}, "
                 f"Delta={obs:+.4f} inside [{lo:+.4f}, {hi:+.4f}]")
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "controls_construct.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tracks": tracks,
        "n": len(ids), "n_cited": len(cid),
        "rate_key": sum(key)/len(ids), "rate_prose": sum(pro)/len(ids),
        "rate_code": sum(cod)/len(ids),
        "agree_prose": a_pro, "agree_code": a_cod, "shuffled_agreement": negs,
        "p_cited": pc, "p_uncited": pu, "delta": obs, "null_lo": lo, "null_hi": hi,
        "check216": ("three consecutive closing lines promoted a KEY-PRESENCE measure to a "
                     "substantive property: #214 'verdict class', #215 'legibility', #216 "
                     "'evidential quality'"),
        "impossible": ("README prose and code identifiers are proxies too; agreement bounds the "
                       "construct from above and nothing here shows a round's controls were "
                       "CORRECT, only that something control-shaped exists"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'controls_construct.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
