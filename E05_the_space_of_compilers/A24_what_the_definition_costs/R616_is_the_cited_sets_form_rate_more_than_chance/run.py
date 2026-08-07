#!/usr/bin/env python3
"""
R616 -- is the cited set's 17-of-17 first-token rate more than chance?

CHECK #215 CAUGHT ME NAMING THE PROPERTY WRONG. R615's closing line called classifiability
"writing a verdict in the corpus's shared vocabulary" and proposed that the selection tracks
LEGIBILITY. The instrument measures something narrower: whether the FIRST TOKEN of `world` is
one of six letters {A,B,C,D,E,UNVERIFIED}. R591's own world value is "MIXED — 0.5404=A
truncated citation ..." -- a perfectly legible verdict that this rule calls unclassifiable.
Instrument unit and claim unit are not equal, so the property under test is renamed to what is
actually measured: SIX-TOKEN FORM.

⚠ AND 17 OF 17 IS A BOUNDARY VALUE, which is exactly where a rate needs a null rather than a
comparison. At an underlying rate of 0.85, seventeen successes has probability 0.85^17 ~ 0.06 --
uncommon but not rare. The question is whether 17/17 departs from what drawing 17 rounds from
this era would give.

ESTIMAND        Delta = P(six-token form | cited) - P(six-token form | uncited), over era
                431-606, against the distribution of that difference when 17 rounds are drawn
                at random from the same era.
IDENTIFICATION  Exact as counts. ⚠ The estimand is about FORM, not about quality, legibility or
                correctness -- a round writing "MIXED" or "W-LOSES" is a well-formed verdict
                that this measure calls absent. Every claim is worded in those terms.
SCOPE           population : rounds 431-606 with artifacts (171), split cited (17) / uncited
                instrument : first token of `world`, case-folded, punctuation-stripped
                             instrument unit = A FIRST TOKEN IN A SIX-MEMBER SET
                             claim unit      = THE SAME -- equal by construction, after the
                             renaming check #215 forced
                baseline   : 17-round draws from the same era
                regime     : as committed at this sha
WORLDS          A SELECTED FOR FORM: 17/17 sits above the null -> the page cites rounds whose
                  verdicts take the six-token form more often than chance, and that is a
                  property of the citation, not of the era.
                B CHANCE: 17/17 sits inside the null -> at this rate and this n, seventeen
                  successes is unremarkable and nothing about form is being selected for.
                C REVERSED: below the null -> the page prefers rounds that do NOT use the form.
KILL            pre-registered: if the era's own rate is above 0.95, the ceiling is too close
                for 17/17 to be informative and the verdict is UNRESOLVABLE whatever the null
                says -- a rate that nearly everything meets cannot separate a selection.
POSITIVE CTRL   a synthetic cited set drawn only from six-token rounds must be detected. Fails
                at g=0: a set drawn at random from the era must not be.
NEGATIVE CTRL   2000 random 17-subsets of the era -> the null for the difference.
PLACEBO         a property every round has must give Delta exactly 0 and a degenerate null.
SEEDS           0, 1, 2.
MULTIPLICITY    one contrast, one null; the rates themselves are DERIVATIONS.
ARTIFACT        results/form_selection.json
IMPOSSIBLE      construct validity for "legible": form is not legibility and neither is
                quality. A round writing MIXED or W-LOSES is excluded by this measure and by
                nothing else, and no claim here reaches those rounds.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
CITE = r"\(R(\d{3})[,)]|R(\d{3})[,)]"
B, TOP = 431, 606
SIX = {"A", "B", "C", "D", "E", "UNVERIFIED"}


def walk(o, out):
    if isinstance(o, dict):
        for k, v in o.items():
            if str(k).lower() == "world" and isinstance(v, str):
                out.append(v)
            walk(v, out)
    elif isinstance(o, list):
        for v in o:
            walk(v, out)


def survey():
    out = {}
    for d in sorted(E05.glob("A*/R[0-9]*")):
        if not d.is_dir() or d.name.startswith("R616_"):
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
        if not ws:
            out[rid] = False
            continue
        tok = re.split(r"[\s,;:.—–-]+", ws[0].strip(), maxsplit=1)[0].strip("`*_'\"").upper()
        out[rid] = tok in SIX
    return out


def delta(sel, S, ids):
    a = [S[i] for i in ids if i in sel]
    b = [S[i] for i in ids if i not in sel]
    return (sum(a)/len(a) - sum(b)/len(b)) if a and b else 0.0


def main():
    text = (E05 / "STATEMENT.md").read_text()
    m = re.search(r"\n\| # \| claim \| scope it holds over \|\n(.*?)\n\n", text, re.S)
    cited = {int(a or b) for a, b in re.findall(CITE, m.group(1) if m else "")}
    S = survey()
    ids = sorted(S)
    if not ids:
        print("UNRUNNABLE: no era rounds. Exit 2, never 0."); return 2
    cid = sorted(i for i in ids if i in cited)
    era_rate = sum(S.values())/len(ids)
    pc = sum(S[i] for i in cid)/len(cid)
    pu = sum(S[i] for i in ids if i not in cited)/(len(ids)-len(cid))
    obs = pc - pu
    print(f"POPULATION  era {B}-{TOP}: {len(ids)} rounds, cited {len(cid)}")
    print(f"  ⚠ the property is SIX-TOKEN FORM — first token of `world` in "
          f"{{A,B,C,D,E,UNVERIFIED}} — NOT legibility. R591's own world value is "
          f"'MIXED — …', a well-formed verdict this rule excludes.")
    print(f"\n─── RATES (DERIVATIONS — counts over a complete enumeration) ───")
    print(f"  era overall    : {sum(S.values())}/{len(ids)} = {era_rate:.4f}")
    print(f"  cited          : {sum(S[i] for i in cid)}/{len(cid)} = {pc:.4f}")
    print(f"  uncited        : {pu:.4f}")
    print(f"  Delta          : {obs:+.4f}")

    print(f"\n─── KILL, EVALUATED BEFORE THE NULL ───")
    ceiling = era_rate > 0.95
    print(f"  era rate {era_rate:.4f} > 0.95 ? {ceiling} -> "
          f"{'UNRESOLVABLE — the ceiling is too close for 17/17 to separate anything' if ceiling else 'informative; proceed'}")

    print(f"\n─── CONTROLS ───")
    rng = random.Random(0)
    nulls = []
    for s in (0, 1, 2):
        r = random.Random(s)
        for _ in range(700):
            sel = set(r.sample(ids, len(cid)))
            nulls.append(delta(sel, S, ids))
    nulls.sort()
    lo, hi = nulls[int(0.025*len(nulls))], nulls[int(0.975*len(nulls))]
    pool_true = [i for i in ids if S[i]]
    pos_sel = set(rng.sample(pool_true, min(len(cid), len(pool_true))))
    d_pos = delta(pos_sel, S, ids)
    pos_ok = d_pos > hi
    print(f"  POSITIVE  a cited set drawn only from six-token rounds: Delta={d_pos:+.4f} vs "
          f"null 97.5% {hi:+.4f} -> {'PASS' if pos_ok else 'FAIL'}")
    rng2 = random.Random(11)
    d_g0 = delta(set(rng2.sample(ids, len(cid))), S, ids)
    g0_ok = lo <= d_g0 <= hi
    print(f"  POSITIVE @ g=0  a random 17-subset: Delta={d_g0:+.4f} in [{lo:+.4f}, {hi:+.4f}] "
          f"-> {'PASS (can fail)' if g0_ok else 'FAIL'}")
    Sall = {i: True for i in ids}
    d_plc = delta(set(cid), Sall, ids)
    plc_ok = abs(d_plc) < 1e-12
    print(f"  PLACEBO   a property every round has: Delta={d_plc:+.4f} -> "
          f"{'PASS — exactly zero' if plc_ok else 'FAIL'}")
    controls_ok = pos_ok and g0_ok and plc_ok

    print(f"\n─── NULL ───")
    print(f"  2100 random 17-subsets of the era: 2.5% {lo:+.4f}  median "
          f"{nulls[len(nulls)//2]:+.4f}  97.5% {hi:+.4f}")
    print(f"  observed {obs:+.4f} -> "
          f"{'ABOVE the null' if obs > hi else ('BELOW' if obs < lo else 'INSIDE the null')}")

    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif ceiling:
        world = (f"UNRESOLVABLE — the era's own six-token rate is {era_rate:.4f}, above the "
                 f"pre-registered 0.95 ceiling; 17/17 cannot separate a selection from a rate "
                 f"nearly everything meets")
    elif obs > hi:
        world = (f"A SELECTED FOR FORM — Delta={obs:+.4f} above the null's 97.5% of {hi:+.4f}: "
                 f"the page cites rounds whose verdicts take the six-token form more often than "
                 f"drawing 17 at random would give. ⚠ FORM, not legibility or quality.")
    elif obs < lo:
        world = f"C REVERSED — Delta={obs:+.4f} below the null's 2.5% of {lo:+.4f}"
    else:
        world = (f"B CHANCE — Delta={obs:+.4f} inside [{lo:+.4f}, {hi:+.4f}]: at this era rate "
                 f"and n=17, seventeen successes is unremarkable and nothing about form is "
                 f"being selected for")
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "form_selection.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "era_rate": era_rate,
        "n_era": len(ids), "n_cited": len(cid), "p_cited": pc, "p_uncited": pu,
        "delta": obs, "null_lo": lo, "null_hi": hi, "null_median": nulls[len(nulls)//2],
        "ceiling_kill": ceiling,
        "check215": ("R615's closing line called this property LEGIBILITY — writing a verdict "
                     "in the corpus's shared vocabulary. The instrument measures first token in "
                     "a six-member set; R591's own world value 'MIXED — …' is a well-formed "
                     "verdict the rule excludes. Renamed to SIX-TOKEN FORM."),
        "impossible": ("form is not legibility and neither is quality; rounds writing MIXED or "
                       "W-LOSES are excluded by this measure and by nothing else"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'form_selection.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
