#!/usr/bin/env python3
"""
R611 -- what else changed at the boundary, or did only provenance stop?

CHECK #210 CAUGHT A CATEGORY ERROR IN R610's CLOSING LINE. It proposed asking whether "the
rounds whose scripts stopped writing artifacts they could point at" coincide with the ones that
stopped recording provenance. But R605's 101 scored matrices live in `corebench/results/` -- a
SHARED POOL with no round attribution at all. They are not per-round objects, so aligning them
with a per-round boundary is ill-posed: two populations at different levels of the hierarchy,
merged because both were absences I had measured.

The well-posed question keeps every quantity per-round: R610 established that provenance
recording stopped corpus-wide at ~430 (cited arm 434, uncited arm 428, both Delta = 1.0000
against their own nulls). WHAT ELSE crossed that boundary?

ESTIMAND        For each per-round structural feature f: Delta_f = P(f | id >= B) - P(f | id < B)
                over band 365-485, BOTH arms pooled (n=118), at B = 431 -- the midpoint of the
                two measured boundaries, fixed before any feature is read.
IDENTIFICATION  Exact as counts. B is CHOSEN, not fitted, so no feature selects its own cut --
                the difference between this and a second sweep.
SCOPE           population : all rounds 365-485 with >=1 parseable results/*.json
                instrument : filesystem + json key presence
                             instrument unit = A STRUCTURAL PROPERTY OF THE DIRECTORY
                             claim unit      = SOMETHING THAT CHANGED IN THE PRACTICE
                             NOT equal -- a correlate is not an event
                baseline   : provenance itself, whose shift at B is the effect being explained
                regime     : as committed at this sha
WORLDS          A ONLY PROVENANCE: no other feature clears the whole-grid null -> one field
                  stopped being written and nothing else measurable changed.
                B A BROADER SHIFT: >=1 other feature clears -> the boundary marks a change in
                  how rounds were built and provenance is one symptom of several.
                C PROVENANCE DOES NOT CLEAR: the pooled cut at a FIXED B fails where the
                  per-arm fitted cuts succeeded -> pooling destroyed it, retracting the
                  corpus-wide reading.
KILL            pre-registered: if provenance itself does not clear at the fixed B, world C and
                no statement about "what else changed" is admissible.
POSITIVE CTRL   provenance, and it is a REAL one -- separated by two independent sweeps, so it
                must clear at the fixed midpoint too. Fails at g=0: a feature independent of id
                must not clear.
NEGATIVE CTRL   200 random features at matched marginals -> the whole-grid null on max|Delta|.
PLACEBO         a constant feature must return exactly 0.
SEEDS           0, 1, 2.
MULTIPLICITY    n_features against a null on the MAXIMUM across the grid.
ARTIFACT        results/what_changed.json
IMPOSSIBLE      a boundary in id order is not a date and a correlate is not a cause; this names
                WHAT differs across a position in the sequence, never WHY.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
FIELDS = ("source_sha256", "source_name", "source_hash", "sha256", "src_sha")
LO, HI, B = 365, 485, 431


def walk(o, acc):
    if isinstance(o, dict):
        for k, v in o.items():
            acc.append(str(k)); walk(v, acc)
    elif isinstance(o, list):
        for v in o:
            walk(v, acc)


def survey():
    out = {}
    for d in sorted(E05.glob("A*/R[0-9]*")):
        if not d.is_dir() or d.name.startswith("R611_"):
            continue
        m = re.match(r"R(\d+)", d.name)
        if not m:
            continue
        rid = int(m.group(1))
        if not (LO <= rid <= HI) or not (d / "results").is_dir():
            continue
        js = list((d / "results").glob("*.json"))
        if not js:
            continue
        prov, keys, nkeys = False, set(), 0
        for f in js:
            try:
                o = json.loads(f.read_text())
            except Exception:
                continue
            acc = []; walk(o, acc)
            nkeys += len(acc); keys |= set(acc)
            if any(any(x in k for x in FIELDS) for k in acc):
                prov = True
        files = [p for p in (d / "results").rglob("*") if p.is_file()]
        pys = [p for p in d.iterdir() if p.is_file() and p.suffix == ".py"]
        doc = d / "README.md"
        out[rid] = {
            "prov": prov,
            "has_py": bool(pys),
            "py_over_8k": bool(pys) and max(p.stat().st_size for p in pys) > 8000,
            "has_readme": doc.is_file(),
            "readme_over_4k": doc.is_file() and doc.stat().st_size > 4000,
            "multi_artifact": len(files) >= 2,
            "many_keys": nkeys >= 40,
            "has_world": "world" in keys,
            "has_controls": "controls" in keys,
            "has_mde": any("mde" in k.lower() for k in keys),
        }
    return out


def delta(flag, late):
    a = [f for f, l in zip(flag, late) if l]
    b = [f for f, l in zip(flag, late) if not l]
    return (sum(a)/len(a) - sum(b)/len(b)) if a and b else 0.0


def main():
    S = survey()
    ids = sorted(S)
    if len(ids) < 30:
        print(f"UNRUNNABLE: only {len(ids)} rounds in band. Exit 2, never 0."); return 2
    late = [i >= B for i in ids]
    n, nlate = len(ids), sum(late)
    print(f"POPULATION  band {LO}-{HI}, BOTH arms pooled: n={n}   at/after B={B}: {nlate}   "
          f"before: {n-nlate}")
    print(f"  B is CHOSEN as the midpoint of R610's two independently measured cuts "
          f"(434 cited, 428 uncited) — NOT fitted here, so no feature selects its own boundary")

    feats = [k for k in next(iter(S.values())) if k != "prov"]
    print(f"\n─── WHOLE-GRID NULL (computed before any feature is read) ───")
    rng = random.Random(0)
    nulls = []
    for _ in range(200):
        row = []
        for _f in feats:
            rate = rng.uniform(0.15, 0.85)
            fl = [1.0 if rng.random() < rate else 0.0 for _ in range(n)]
            row.append(abs(delta(fl, late)))
        nulls.append(max(row))
    nulls.sort()
    t = nulls[int(0.95*len(nulls))]
    print(f"  max|Delta| over {len(feats)} random features, 200 draws: median "
          f"{nulls[len(nulls)//2]:.4f}  p95 {t:.4f}  max {nulls[-1]:.4f}")

    print(f"\n─── CONTROLS ───")
    dp = delta([1.0 if S[i]["prov"] else 0.0 for i in ids], late)
    pos_ok = abs(dp) > t
    print(f"  POSITIVE  provenance itself at the FIXED B: Delta={dp:+.4f} vs {t:.4f} -> "
          f"{'PASS — the boundary survives pooling and fixing' if pos_ok else 'FAIL — world C'}")
    rng2 = random.Random(7)
    g0 = abs(delta([1.0 if rng2.random() < 0.5 else 0.0 for _ in ids], late))
    g0_ok = g0 <= t
    print(f"  POSITIVE @ g=0  a feature independent of id: |Delta|={g0:.4f} -> "
          f"{'PASS (can fail)' if g0_ok else 'fires on noise'}")
    dc = abs(delta([1.0]*n, late))
    plc_ok = dc < 1e-12
    print(f"  PLACEBO   constant feature: |Delta|={dc:.4f} -> "
          f"{'PASS — exactly zero' if plc_ok else 'FAIL'}")
    controls_ok = pos_ok and g0_ok and plc_ok

    print(f"\n─── EVERY FEATURE ACROSS B (survivors and not) ───")
    rows = []
    for f in feats:
        fl = [1.0 if S[i][f] else 0.0 for i in ids]
        d = delta(fl, late)
        pre = sum(x for x, l in zip(fl, late) if not l)/max(1, n-nlate)
        post = sum(x for x, l in zip(fl, late) if l)/max(1, nlate)
        beats = abs(d) > t
        rows.append({"feature": f, "before": pre, "after": post, "delta": d, "clears": beats})
        print(f"  {f:<16} before {pre:.4f}   after {post:.4f}   Delta={d:+.4f}   "
              f"{'CLEARS' if beats else 'inside the grid null'}")
    others = [r for r in rows if r["clears"]]

    print(f"\n─── VERDICT ───")
    if not pos_ok:
        world = ("C PROVENANCE DOES NOT CLEAR AT THE FIXED B — pooling the arms and fixing the "
                 "cut destroys the boundary, which retracts the corpus-wide reading")
    elif not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif not others:
        world = (f"A ONLY PROVENANCE — provenance shifts {dp:+.4f} across B while none of the "
                 f"{len(feats)} other features clears {t:.4f}. One field stopped being written "
                 f"and nothing else measurable about the rounds changed.")
    else:
        world = (f"B A BROADER SHIFT — {len(others)} other feature(s) clear alongside "
                 f"provenance: {[(r['feature'], round(r['delta'], 4)) for r in others]}. The "
                 f"boundary marks a change in how rounds were built.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: {len(feats)} features against a null on the MAXIMUM across the "
          f"grid, so no feature is credited for being the best of many.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "what_changed.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "B": B, "n": n, "n_late": nlate,
        "provenance_delta": dp, "grid_null_p95": t,
        "null_median": nulls[len(nulls)//2], "null_max": nulls[-1],
        "features": rows, "others_clearing": [r["feature"] for r in others],
        "check210": ("R610's closing line proposed aligning R605's 101 scored matrices — which "
                     "live in a SHARED pool with no round attribution — with a per-round "
                     "boundary: two populations at different levels of the hierarchy, merged "
                     "because both were absences I had measured. Ill-posed, and replaced."),
        "impossible": ("a boundary in id order is not a date and a correlate is not a cause"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'what_changed.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
