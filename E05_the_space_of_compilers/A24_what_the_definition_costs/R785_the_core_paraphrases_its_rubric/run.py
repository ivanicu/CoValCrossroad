#!/usr/bin/env python3
"""R785 · the released core is a PARAPHRASE of its rubric, not a subset — and whether `gen` is too.

CHECK #387 declined R784's proposed gate on arithmetic (every scope line in 780+ READMEs says "968",
so the only implementable form is a freeze and the frozen ones stay wrong) and found the object
question instead: `coval_core` clears clause ② at q_res 0.9978 while `gen` — also conversation-only,
also k=4 — sits at 0.0396. What separates them?

ESTIMAND        E1 coval_core vs its own rubric, TWO instruments + the cross-conversation null ·
                E2 the same for `gen` — the discriminating cell · E3 does rubric affinity predict
                clause-② standing · E4 what the definition must then say
IDENTIFICATION  E1 exact for verbatim; the token measure is a CHOICE, swept over {3,4,5} ·
                E2 via R468's join, rebuilt exactly in R783 · E3 only over arms whose criterion TEXTS
                exist, counted, never over "the arms"
DERIVED FIRST   D1 a similarity without its cross-pair null is uninterpretable · D2 the
                cross-conversation pairing IS a valid permutation, unlike ledger 1125/1129 ·
                D3 the sham and the null are the same object here, so no sham is built ·
                D4 an exact-match instrument measures string identity, not content (§4)
WORLDS          A affinity separates them · B both track it · C the measure is not detecting content
CONTROLS        OBJECT · PLACEBO · NULL · NULL-TOPIC (the confound) · POSITIVE (dose, band computed) ·
                SWEEP over tokenisation
"""
import collections
import itertools
import json
import math
import pathlib
import re
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets                      # noqa: E402

RES = ROOT / "corebench/results"
REL = ROOT / "data/conversation_rubrics.jsonl"
ZEFF = 1.959964 + 0.841621
SEED = 31337
LENS = (3, 4, 5)

INSTRUMENT_UNIT = "a criterion-to-criterion comparison"
CLAIM_UNIT = "a conversation"


def _plain(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def toks(s, n):
    return set(re.findall(r"[a-z]{%d,}" % n, s.lower()))


def jac(a, b):
    """⚠ Jaccard is UNDEFINED on two empty sets and the first draft returned 0, because the guard
    `max(len(a|b), 1)` turned 0/0 into 0/1. The PLACEBO caught it: a rubric against ITSELF returned
    0.999848 rather than 1.0. Two empty sets are IDENTICAL, so the value is 1.0. This is a degenerate
    being defined, not a threshold being loosened -- 3 of 19,147 release criteria tokenise to nothing
    and all three are junk: 'Lwa', a bare UUID, and an empty string."""
    if not a and not b:
        return 1.0
    u = len(a | b)
    return len(a & b) / u if u else 1.0


def affinity(C, F, n):
    """mean over core criteria of the best Jaccard against any rubric criterion"""
    if not C or not F:
        return float("nan")
    Ft = [toks(f, n) for f in F]
    o = []
    for c in C:
        ct = toks(c, n)
        o.append(max((jac(ct, ft) for ft in Ft), default=0.0))
    return float(np.mean(o))


def cell(d):
    d = d[~np.isnan(d)]
    n = len(d)
    ib = np.random.default_rng(SEED).integers(0, n, (1200, n))
    bs = d[ib].mean(axis=1)
    eff = float(d.mean())
    mde = ZEFF * float(d.std(ddof=1)) / math.sqrt(n)
    return {"n": n, "eff": eff, "lo": float(np.percentile(bs, 2.5)),
            "hi": float(np.percentile(bs, 97.5)), "mde": mde,
            "resolves": bool(abs(eff) >= mde and not (np.percentile(bs, 2.5) <= 0
                                                      <= np.percentile(bs, 97.5)))}


def main():
    out = {"instrument_unit": INSTRUMENT_UNIT, "claim_unit": CLAIM_UNIT}
    rng = np.random.default_rng(SEED)

    # ================= OBJECT CHECK -- exit 2, never 0 ============================================
    print("  OBJECT CHECK")
    recs = []
    for line in open(REL, encoding="utf-8"):
        if not line.strip():
            continue
        r = json.loads(line)
        C = [(it.get("criterion") or "").strip() for it in (r.get("coval_core") or [])]
        F = [(it.get("criterion") or "").strip() for it in (r.get("coval_full") or [])]
        if C and F:
            recs.append((r["conversation"]["id"], C, F))
    gen = json.loads((RES / "core_gen.json").read_text())
    full_rank = json.loads((RES / "core_full.json").read_text())
    # R468's join, rebuilt: rubric criterion texts key both spaces
    relkey = collections.defaultdict(list)
    for cid, _, F in recs:
        relkey[tuple(sorted(F))].append(cid)
    rel_by_id = {cid: (C, F) for cid, C, F in recs}
    join, unmatched, ambiguous = {}, 0, 0
    for p in full_rank:
        cand = relkey.get(tuple(sorted(str(x).strip() for x in full_rank[p])), [])
        if len(cand) == 1:
            join[p] = cand[0]
        elif not cand:
            unmatched += 1
        else:
            ambiguous += 1
    print(f"     release records with both fields {len(recs)}   `core_gen.json` prompts {len(gen)}")
    print(f"     JOIN ranking->release: exact {len(join)}   unmatched {unmatched}   "
          f"ambiguous {ambiguous}   (R468, rebuilt in R783)")
    if not recs or not join or unmatched or ambiguous:
        print("  UNRUNNABLE: the join is not exact and total. Exit 2, never 0.")
        return 2
    out["object"] = {"records": len(recs), "gen_prompts": len(gen), "join": len(join),
                     "unmatched": unmatched, "ambiguous": ambiguous}

    # ================= CONTROLS ===================================================================
    print("\n  CONTROLS")
    plac = np.array([affinity(F, F, 4) for _, _, F in recs])
    print(f"     PLACEBO    a rubric against itself: {plac.mean():.6f}  "
          f"{'PASS' if abs(plac.mean() - 1.0) < 1e-12 else 'FAIL'}")
    # NULL: cross-conversation pairing (D2's valid permutation)
    perm = rng.permutation(len(recs))
    own4 = np.array([affinity(C, F, 4) for _, C, F in recs])
    oth4 = np.array([affinity(recs[i][1], recs[perm[i]][2], 4) for i in range(len(recs))])
    nul = cell(own4 - oth4)
    print(f"     NULL       own rubric {own4.mean():.4f}  vs ANOTHER's {oth4.mean():.4f}   "
          f"difference {nul['eff']:+.4f} [{nul['lo']:+.4f}, {nul['hi']:+.4f}]  MDE {nul['mde']:.4f}  "
          f"{'RESOLVES' if nul['resolves'] else 'inside null'}")
    print(f"                records with own > other: "
          f"{int((own4 > oth4).sum())} of {len(recs)}")
    # NULL-TOPIC: the confound -- nearest OTHER conversation by rubric-token overlap
    sample = rng.choice(len(recs), 150, replace=False)
    sig = [toks(" ".join(recs[i][2]), 4) for i in range(len(recs))]
    topic = []
    for i in sample:
        best, bj = None, -1.0
        for j in rng.choice(len(recs), 60, replace=False):
            if j == i:
                continue
            jj = jac(sig[i], sig[j])
            if jj > bj:
                bj, best = jj, j
        topic.append(affinity(recs[i][1], recs[best][2], 4))
    topic = np.array(topic)
    tcell = cell(own4[sample] - topic)
    print(f"     NULL-TOPIC nearest-topic other rubric {topic.mean():.4f}   own {own4[sample].mean():.4f}"
          f"   difference {tcell['eff']:+.4f}  MDE {tcell['mde']:.4f}  "
          f"{'RESOLVES' if tcell['resolves'] else 'inside null'}   (n={len(sample)})")
    # POSITIVE: degrade a paraphrase by deleting tokens
    dose, okp = {}, True
    for frac in (0.0, 0.25, 0.5, 0.75):
        vals = []
        for _, _, F in recs[:300]:
            deg = []
            for f in F:
                w = f.split()
                keep = [x for x in w if rng.random() >= frac]
                deg.append(" ".join(keep) if keep else "")
            vals.append(affinity(deg, F, 4))
        dose[str(frac)] = float(np.mean(vals))
        print(f"     POSITIVE   delete {frac:>4.0%} of tokens -> affinity {dose[str(frac)]:.4f}")
    okp = (abs(dose["0.0"] - 1.0) < 1e-9 and dose["0.0"] > dose["0.25"] > dose["0.5"] > dose["0.75"])
    print(f"                band COMPUTED: floor delete-0% must be 1.0000, and the curve must be "
          f"monotone down   POSITIVE {'PASS' if okp else 'FAIL'}")
    print(f"     SHAM       ⛔ NOT BUILT -- D3: the ingredient is *being the same conversation*, and "
          f"removing it IS the NULL")
    gate = abs(plac.mean() - 1.0) < 1e-12 and nul["resolves"] and okp
    out["controls"] = {"placebo": float(plac.mean()), "null": nul, "null_topic": tcell,
                       "dose": dose, "positive": okp, "gate": gate}

    # ================= E1/E2 · the two objects, two instruments, swept ============================
    print("\n  E1/E2 - `coval_core` AND `gen` AGAINST THE RUBRIC")
    rows = {}
    genr = {join[p]: [str(x).strip() for x in gen[p]] for p in gen if p in join}
    print(f"     `gen` joined to a release record: {len(genr)} of {len(gen)}")
    print(f"     {'object':<12}{'tok':>5}{'verbatim':>11}{'affinity':>11}{'null':>9}"
          f"{'own-null':>10}{'MDE':>9}   verdict")
    cells = []
    for n in LENS:
        oc = np.array([affinity(C, F, n) for _, C, F in recs])
        on = np.array([affinity(recs[i][1], recs[perm[i]][2], n) for i in range(len(recs))])
        vb = np.array([len(set(C) & set(F)) / len(C) for _, C, F in recs])
        if n == LENS[0]:
            junk = sum(1 for _, C, F in recs for t in C + F if not toks(t, 4))
            print(f"     ⚠ release criteria tokenising to NOTHING: {junk} "
                  f"(all junk: 'Lwa', a bare UUID, an empty string) -- the PLACEBO's catch")
        c = cell(oc - on)
        rows[f"coval_core|{n}"] = {"verbatim": float(vb.mean()), "affinity": float(oc.mean()),
                                   "null": float(on.mean()), **c}
        print(f"     {'coval_core':<12}{n:>5}{vb.mean():>11.4f}{oc.mean():>11.4f}{on.mean():>9.4f}"
              f"{c['eff']:>+10.4f}{c['mde']:>9.4f}   "
              f"{'RESOLVES' if c['resolves'] else 'inside null'}")
        ids = sorted(genr)
        gc = np.array([affinity(genr[i], rel_by_id[i][1], n) for i in ids])
        gn = np.array([affinity(genr[ids[k]], rel_by_id[ids[(k + 7) % len(ids)]][1], n)
                       for k in range(len(ids))])
        gv = np.array([len(set(genr[i]) & set(rel_by_id[i][1])) / max(len(genr[i]), 1) for i in ids])
        g = cell(gc - gn)
        rows[f"gen|{n}"] = {"verbatim": float(gv.mean()), "affinity": float(gc.mean()),
                            "null": float(gn.mean()), **g}
        print(f"     {'gen':<12}{n:>5}{gv.mean():>11.4f}{gc.mean():>11.4f}{gn.mean():>9.4f}"
              f"{g['eff']:>+10.4f}{g['mde']:>9.4f}   "
              f"{'RESOLVES' if g['resolves'] else 'inside null'}")
        # the discriminating comparison, on the conversations both cover
        common = [i for i in ids]
        idx = {cid: k for k, (cid, _, _) in enumerate(recs)}
        d = np.array([affinity(rel_by_id[i][0], rel_by_id[i][1], n)
                      - affinity(genr[i], rel_by_id[i][1], n) for i in common])
        cmpc = cell(d)
        rows[f"core_minus_gen|{n}"] = cmpc
        cells.append((n, cmpc["resolves"], cmpc["eff"]))
        print(f"     {'core - gen':<12}{n:>5}{'':>11}{'':>11}{'':>9}{cmpc['eff']:>+10.4f}"
              f"{cmpc['mde']:>9.4f}   "
              f"{'RESOLVES' if cmpc['resolves'] else 'inside null'}   <- the discriminating cell")
    out["rows"] = rows

    # ================= E3 · does affinity predict clause-② standing? ==============================
    print("\n  E3 - DOES RUBRIC AFFINITY PREDICT CLAUSE-② STANDING?")
    q782 = {"coval_core": 0.9978, "gen": 0.0396}
    aff = {"coval_core": rows["coval_core|4"]["affinity"], "gen": rows["gen|4"]["affinity"]}
    print(f"     arms with criterion TEXT available: {len(aff)} "
          f"(`coval_core` from the release, `gen` from `core_gen.json`)")
    for k in aff:
        print(f"     {k:<12} affinity {aff[k]:.4f}   q_resolved (R782) {q782[k]:.4f}")
    print(f"     ⚠ n = 2 arms. A correlation is UNDEFINED at n=2 and is NOT computed; the pair is "
          f"reported as a pair.")
    out["e3"] = {"affinity": aff, "q_resolved_R782": q782, "n_arms": len(aff),
                 "correlation": None, "why": "undefined at n=2"}

    # ================= WORLD =======================================================================
    surv = sum(1 for _, r, _ in cells if r)
    signs = {np.sign(e) for _, r, e in cells if r}
    if not gate:
        world = "UNVERIFIED - a control did not fire. Never OVERTURNED, never CONFIRMED."
    elif not all(rows[f"{o}|{n}"]["resolves"] for o in ("coval_core",) for n in LENS):
        world = ("C - THE MEASURE IS NOT DETECTING CONTENT: own-vs-cross fails to resolve at some "
                 "tokenisation")
    elif surv == len(cells) and signs == {1.0}:
        world = (f"A - RUBRIC AFFINITY SEPARATES THEM: `coval_core` exceeds `gen` at all "
                 f"{len(cells)} tokenisations, effects "
                 f"{[round(e, 4) for _, _, e in cells]}")
    elif surv == 0:
        world = (f"B - BOTH TRACK IT: the core-minus-gen difference is inside its MDE at all "
                 f"{len(cells)} tokenisations, so affinity does not explain the ② gap")
    else:
        world = (f"NO WORLD CLAIMED: the discriminating cell resolves at {surv} of {len(cells)} "
                 f"tokenisations, so the answer is specification-dependent and is reported as a curve")
    print(f"\n  WORLD {world}")
    out["world"] = world
    out["tree_sha"] = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                     capture_output=True, text=True).stdout.strip()
    d = pathlib.Path(__file__).resolve().parent / "results"
    d.mkdir(exist_ok=True)
    (d / "rubric_affinity.json").write_text(json.dumps(out, indent=2, default=_plain))
    print("  artifact -> rubric_affinity.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
